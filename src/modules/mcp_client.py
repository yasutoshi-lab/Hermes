"""
MCP Web Search client wrapper.

This module provides a typed Python interface for interacting with the
web-search-mcp server described in 基本設計書.md Section 2.2. It encapsulates
connection handling, retries, and response normalization so nodes can depend on
a consistent API without worrying about transport details.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, TypedDict
from urllib.parse import urljoin

from config import settings

try:
    import requests
except ImportError:  # pragma: no cover - requests should be available via requirements
    requests = None

logger = logging.getLogger(__name__)


class MCPClientError(RuntimeError):
    """Base exception for MCP client failures."""


class RateLimitError(MCPClientError):
    """Raised when the MCP server rate limits requests."""


class TransportNotAvailableError(MCPClientError):
    """Raised when HTTP client dependencies are missing."""


class SearchResult(TypedDict, total=False):
    """Normalized structure for search results."""

    title: str
    url: str
    description: str
    content: str
    language: str
    retrieved_at: str
    score: float


@dataclass
class MCPResponse:
    """Internal helper to carry HTTP response metadata."""

    status_code: int
    payload: Dict[str, Any]


class WebSearchClient:
    """
    High-level client for the web-search-mcp server.

    The client exposes synchronous helper methods that map to the tools listed
    in the design doc. It performs retry/backoff and basic language-aware query
    shaping before issuing requests. The implementation is sync-first but is
    structured so an async drop-in replacement can be added later.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        *,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        backoff_factor: float = 0.5,
        api_key: Optional[str] = None,
        session: Optional[Any] = None,
        default_language: Optional[str] = None,
        default_limit: Optional[int] = None
    ) -> None:
        self.base_url = (base_url or settings.web_search_mcp_endpoint).rstrip("/")
        self.timeout = timeout or float(settings.timeout_seconds)
        self.max_retries = max_retries or settings.max_retries
        self.backoff_factor = backoff_factor
        self.default_language = (default_language or settings.default_language).lower()
        self.default_limit = default_limit or settings.default_search_limit
        self.api_key = api_key
        self.session = session or self._build_session()

    def full_search(
        self,
        query: str,
        *,
        language: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[SearchResult]:
        """Call the `full-web-search` tool."""
        return self._execute_search(
            tool_name="full-web-search",
            query=query,
            language=language,
            limit=limit
        )

    def summary_search(
        self,
        query: str,
        *,
        language: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[SearchResult]:
        """Call the `get-web-search-summaries` tool."""
        return self._execute_search(
            tool_name="get-web-search-summaries",
            query=query,
            language=language,
            limit=limit
        )

    def fetch_page_content(
        self,
        url: str,
        *,
        language: Optional[str] = None
    ) -> SearchResult:
        """Fetch a single page's content via `get-single-web-page-content`."""
        payload = {
            "url": url,
            "language": (language or self.default_language).lower()
        }
        response = self._call_tool_with_retries("get-single-web-page-content", payload)
        content = response.payload.get("content") or response.payload.get("data") or ""
        title = response.payload.get("title") or url
        description = response.payload.get("description", "")
        return self._normalize_result(
            {
                "title": title,
                "url": url,
                "description": description,
                "content": content,
                "score": response.payload.get("score")
            },
            language or self.default_language
        )

    def multi_search(
        self,
        queries: Sequence[str],
        *,
        language: Optional[str] = None,
        per_query_limit: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Execute several searches and deduplicate by URL.

        Args:
            queries: Search queries to run sequentially
            language: Preferred language (defaults to client default)
            per_query_limit: Result cap per query (defaults to `default_limit`)
        """
        aggregated: List[SearchResult] = []
        seen_urls: set[str] = set()
        lang = (language or self.default_language).lower()
        limit = per_query_limit or self.default_limit

        for query in queries:
            results = self.full_search(query, language=lang, limit=limit)
            for result in results:
                url = result.get("url", "")
                if url and url in seen_urls:
                    continue
                if url:
                    seen_urls.add(url)
                aggregated.append(result)
        return aggregated

    def _execute_search(
        self,
        *,
        tool_name: str,
        query: str,
        language: Optional[str],
        limit: Optional[int]
    ) -> List[SearchResult]:
        shaped_query = self._prepare_query(query, language)
        payload: Dict[str, Any] = {
            "query": shaped_query,
            "language": (language or self.default_language).lower(),
            "limit": limit or self.default_limit
        }
        response = self._call_tool_with_retries(tool_name, payload)
        raw_results = self._extract_results(response.payload)
        return [
            self._normalize_result(raw, payload["language"])
            for raw in raw_results
        ]

    def _prepare_query(self, query: str, language: Optional[str]) -> str:
        """Add lightweight language-aware hints to the query."""
        cleaned = (query or "").strip()
        lang = (language or self.default_language).lower()
        if not cleaned:
            raise MCPClientError("Query must be a non-empty string")

        if lang == "ja" and "最新" not in cleaned:
            cleaned = f"{cleaned} 最新情報"
        elif lang == "en" and "latest" not in cleaned.lower():
            cleaned = f"{cleaned} latest insights"
        return cleaned

    def _call_tool_with_retries(self, tool_name: str, payload: Dict[str, Any]) -> MCPResponse:
        """Issue HTTP POST with retry/backoff."""
        last_error: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._post(tool_name, payload)
                if response.status_code == 429:
                    raise RateLimitError("web-search-mcp rate limited the request")
                if response.status_code >= 500:
                    raise MCPClientError(f"MCP server error: {response.status_code}")
                return response
            except RateLimitError as exc:
                last_error = exc
                self._sleep_with_backoff(attempt)
            except MCPClientError as exc:
                last_error = exc
                if attempt == self.max_retries:
                    break
                self._sleep_with_backoff(attempt)
            except Exception as exc:  # pragma: no cover - defensive logging
                last_error = exc
                logger.exception("Unexpected MCP client error: %s", exc)
                if attempt == self.max_retries:
                    break
                self._sleep_with_backoff(attempt)
        if last_error:
            raise last_error
        raise MCPClientError("MCP request failed without specific error")

    def _post(self, tool_name: str, payload: Dict[str, Any]) -> MCPResponse:
        """Low-level POST helper."""
        if self.session is None:
            raise TransportNotAvailableError("HTTP session is not available")

        url = urljoin(f"{self.base_url}/", f"tools/{tool_name}")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = self.session.post(url, json=payload, headers=headers, timeout=self.timeout)

        try:
            parsed = response.json()
        except ValueError as exc:
            raise MCPClientError(f"Invalid JSON response for {tool_name}") from exc

        return MCPResponse(status_code=response.status_code, payload=parsed)

    def _build_session(self) -> Any:
        """Create a default requests session."""
        if requests is None:
            raise TransportNotAvailableError(
                "The 'requests' package is required for WebSearchClient. "
                "Install it via `pip install requests`."
            )
        session = requests.Session()
        session.headers.update({"User-Agent": "Hermes-Research-Agent/1.0"})
        return session

    @staticmethod
    def _extract_results(payload: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        """
        Normalize MCP responses that may use different envelope keys.

        Supported formats:
        - {"results": [...]}
        - {"data": {"results": [...]}}
        - direct list/dict payload
        """
        if not payload:
            return []
        if isinstance(payload, list):
            return payload
        if "results" in payload and isinstance(payload["results"], list):
            return payload["results"]
        if "data" in payload:
            data = payload["data"]
            if isinstance(data, dict) and isinstance(data.get("results"), list):
                return data["results"]
        return [payload]

    def _normalize_result(self, raw: Dict[str, Any], language: str) -> SearchResult:
        """Map raw MCP payloads into SearchResult dictionaries."""
        now = datetime.now(timezone.utc).isoformat()
        title = (raw.get("title") or raw.get("name") or "Untitled").strip()
        url = (raw.get("url") or raw.get("link") or "").strip()
        description = raw.get("description") or raw.get("summary") or ""
        content = raw.get("content") or raw.get("body") or ""
        score = raw.get("score")

        result: SearchResult = {
            "title": title,
            "url": url,
            "description": description.strip(),
            "content": content,
            "language": language,
            "retrieved_at": now
        }
        if isinstance(score, (int, float)):
            result["score"] = float(score)
        return result

    def _sleep_with_backoff(self, attempt: int) -> None:
        """Sleep helper extracted for easier testing/mocking."""
        delay = self.backoff_factor * (2 ** (attempt - 1))
        logger.debug("MCP client retry #%s sleeping for %.2fs", attempt, delay)
        time.sleep(delay)

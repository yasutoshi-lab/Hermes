"""
Browser automation client for web research.

Provides automatic fallback to DuckDuckGo search when the optional browser-use
package is unavailable. Results include lightweight content extraction so that
downstream nodes receive usable text even without full browser automation.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from html import unescape
from urllib import robotparser
from urllib.parse import urljoin, urlparse
import re

import httpx
from duckduckgo_search import DDGS

try:  # pragma: no cover - optional dependency
    from browser_use import BrowserAgent  # type: ignore
except ImportError:  # pragma: no cover - executed in fallback mode
    BrowserAgent = None  # type: ignore


@dataclass
class BrowserSearchResult:
    """Result from browser search."""

    url: str
    title: str
    snippet: str
    content: str
    timestamp: str


class BrowserUseClient:
    """Client for web research using browser-use or DuckDuckGo fallback."""

    USER_AGENT = "HermesBrowserClient/1.0"
    MAX_PARAGRAPHS = 3
    MAX_CHARS = 2000
    _SCRIPT_STYLE_RE = re.compile(r"<(script|style|noscript)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
    _BLOCK_TAG_RE = re.compile(r"</?(p|div|br|li|section|article|h[1-6]|blockquote)[^>]*>", re.IGNORECASE)
    _TAG_RE = re.compile(r"<[^>]+>")
    _WHITESPACE_RE = re.compile(r"\s+")

    def __init__(self, max_sources: int = 8, http_timeout: float = 10.0) -> None:
        """
        Initialize browser client.

        Args:
            max_sources: Maximum number of sources to collect per query.
            http_timeout: Timeout for HTTP requests when fetching page content.
        """
        self.max_sources = max_sources
        self.http_timeout = http_timeout
        self.logger = logging.getLogger(__name__)
        self._duck_client = DDGS()
        self._http_client = httpx.Client(
            timeout=http_timeout,
            headers={"User-Agent": self.USER_AGENT},
            follow_redirects=True,
        )
        self._robots_cache: Dict[str, Optional[robotparser.RobotFileParser]] = {}

        self.browser_agent = None
        if BrowserAgent is not None:
            try:
                self.browser_agent = BrowserAgent()
                self.logger.info("browser-use detected; BrowserAgent initialized.")
            except Exception as exc:  # pragma: no cover - depends on external lib
                self.logger.warning(
                    "browser-use import succeeded but initialization failed (%s). Falling back to DuckDuckGo.",
                    exc,
                )

        self.logger.info("Initialized BrowserUseClient with max_sources=%s", max_sources)

    def search(self, query: str, max_sources: Optional[int] = None) -> List[BrowserSearchResult]:
        """
        Perform web search and extract information.

        Args:
            query: Search query string.
            max_sources: Override default max sources for this query.

        Returns:
            List of search results with extracted content.
        """
        sources_limit = max_sources if max_sources is not None else self.max_sources
        self.logger.info(
            "Starting web search for query='%s' with max_sources=%s", query, sources_limit
        )

        if self.browser_agent is not None:
            try:
                return self._search_with_browser_use(query, sources_limit)
            except Exception as exc:  # pragma: no cover - external dep runtime
                self.logger.warning(
                    "browser-use search failed (%s). Switching to DuckDuckGo fallback.",
                    exc,
                )

        return self._search_with_duckduckgo(query, sources_limit)

    def _search_with_browser_use(self, query: str, sources_limit: int) -> List[BrowserSearchResult]:
        """Attempt to use browser-use if it is available."""
        results: List[BrowserSearchResult] = []
        raw_results = list(self.browser_agent.search(query, max_results=sources_limit))  # type: ignore[attr-defined]
        for entry in raw_results[:sources_limit]:
            url = self._read_entry_field(entry, "url") or self._read_entry_field(entry, "href")
            if not url:
                continue
            title = self._read_entry_field(entry, "title") or url
            snippet = self._read_entry_field(entry, "snippet") or ""
            content = self._read_entry_field(entry, "content") or self.extract_content(url) or snippet
            results.append(
                BrowserSearchResult(
                    url=url,
                    title=title,
                    snippet=snippet,
                    content=content,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
            )
        return results

    def _search_with_duckduckgo(self, query: str, sources_limit: int) -> List[BrowserSearchResult]:
        """Search using DuckDuckGo and fetch content for each hit."""
        try:
            raw_hits = list(self._duck_client.text(query, max_results=sources_limit))
        except Exception as exc:
            self.logger.error("DuckDuckGo search failed: %s", exc)
            raise BrowserUseError(f"DuckDuckGo search failed: {exc}") from exc

        results: List[BrowserSearchResult] = []
        for hit in raw_hits:
            url = hit.get("href") or hit.get("url")
            if not url:
                continue
            title = hit.get("title") or url
            snippet = hit.get("body") or hit.get("snippet") or ""
            content = self.extract_content(url) or snippet
            results.append(
                BrowserSearchResult(
                    url=url,
                    title=title,
                    snippet=snippet,
                    content=content,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                )
            )
        self.logger.info("DuckDuckGo fallback returned %s sources.", len(results))
        return results[:sources_limit]

    @staticmethod
    def _read_entry_field(entry: Any, key: str) -> Optional[str]:
        """Helper to read from dict-like or attribute-based entries."""
        if isinstance(entry, dict):
            value = entry.get(key)
        else:
            value = getattr(entry, key, None)
        if value is None:
            return None
        return str(value)

    def extract_content(self, url: str) -> Optional[str]:
        """
        Extract trimmed textual content from a URL.

        Args:
            url: Target URL.

        Returns:
            Cleaned text limited to a few paragraphs, or None if extraction fails.
        """
        if not url:
            return None

        if not self._allowed_by_robots(url):
            self.logger.debug("Robots.txt disallows fetching %s", url)
            return None

        try:
            response = self._http_client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            self.logger.debug("HTTP fetch failed for %s: %s", url, exc)
            return None

        return self._shrink_content(response.text)

    def _allowed_by_robots(self, url: str) -> bool:
        """Check robots.txt once per host and cache the result."""
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self._robots_cache:
            robots_url = urljoin(origin, "/robots.txt")
            parser = robotparser.RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
            except Exception:
                self._robots_cache[origin] = None
            else:
                self._robots_cache[origin] = parser

        rp = self._robots_cache[origin]
        if rp is None:
            return True

        return rp.can_fetch(self.USER_AGENT, url)

    def _shrink_content(self, html: str) -> str:
        """Convert HTML to a compact text block."""
        without_scripts = self._SCRIPT_STYLE_RE.sub(" ", html)
        with_breaks = self._BLOCK_TAG_RE.sub("\n", without_scripts)
        stripped_tags = self._TAG_RE.sub(" ", with_breaks)
        text = self._WHITESPACE_RE.sub(" ", unescape(stripped_tags))
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        trimmed = "\n\n".join(paragraphs[: self.MAX_PARAGRAPHS])
        return trimmed[: self.MAX_CHARS].strip()

    def close(self) -> None:
        """Clean up browser resources."""
        self.logger.debug("Closing BrowserUseClient")
        try:
            self._http_client.close()
        except Exception:
            pass
        try:
            self._duck_client.close()
        except Exception:
            pass
        if self.browser_agent and hasattr(self.browser_agent, "close"):
            try:
                self.browser_agent.close()
            except Exception:  # pragma: no cover - depends on external lib
                self.logger.debug("browser-use close() raised but was ignored.")

    def __enter__(self) -> "BrowserUseClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()


class BrowserUseError(Exception):
    """Raised when browser automation fails."""

    pass

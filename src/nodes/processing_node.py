"""Processing node for data cleaning and preparation in isolated containers."""

from __future__ import annotations

import logging
import re
import textwrap
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from config import settings
from modules.history_manager import HistoryManager, HistoryManagerError
from state.agent_state import AgentState, add_error

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    from markdownify import markdownify as html_to_markdown  # type: ignore
except ImportError:  # pragma: no cover
    html_to_markdown = None

try:  # pragma: no cover - optional dependency
    from pdfminer.high_level import extract_text as pdf_extract_text  # type: ignore
except ImportError:  # pragma: no cover
    pdf_extract_text = None

try:  # pragma: no cover - optional dependency
    import requests
except ImportError:  # pragma: no cover
    requests = None


class ContainerProcessorError(RuntimeError):
    """Raised when container processing fails."""


class _HTMLStripper(HTMLParser):
    """Basic HTML to text converter used when markdownify is unavailable."""

    def __init__(self) -> None:
        super().__init__()
        self._parts: List[str] = []

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def get_text(self) -> str:
        return " ".join(part.strip() for part in self._parts if part.strip())


class ContainerProcessor:
    """
    Processing interface that can talk to container-use or fall back to local parsing.

    The default implementation keeps everything local (safer for unit tests) but the
    class exposes hooks (`enable_remote=True`) so we can route heavy parsing to the
    container-use MCP endpoint once it is wired up.
    """

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        enable_remote: bool = False,
        session: Optional[Any] = None,
    ) -> None:
        self.base_url = (base_url or settings.container_use_mcp_endpoint).rstrip("/")
        self.timeout = timeout or settings.timeout_seconds
        self.max_retries = max_retries or settings.max_retries
        self.enable_remote = enable_remote
        self.session = session or (requests.Session() if enable_remote and requests else None)

    def process_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single document into normalized snippets and metadata."""
        if self.enable_remote and self.session is not None:
            try:
                return self._process_remote(document)
            except ContainerProcessorError as exc:
                logger.warning("ContainerProcessor: remote call failed (%s); falling back to local mode", exc)
        return self._process_local(document)

    def _process_remote(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder remote processing via container-use MCP."""
        if self.session is None:
            raise ContainerProcessorError("Remote session not configured")

        endpoint = urljoin(f"{self.base_url}/", "process")
        payload = {
            "document": document,
            "operations": ["normalize", "extract_facts", "extract_tables"],
        }
        response = self.session.post(endpoint, json=payload, timeout=self.timeout)
        if response.status_code != 200:
            raise ContainerProcessorError(f"Container returned HTTP {response.status_code}")
        try:
            data = response.json()
        except ValueError as exc:  # pragma: no cover - defensive
            raise ContainerProcessorError("Invalid JSON from container") from exc

        processed = data.get("processed")
        if not processed:
            raise ContainerProcessorError("Container response missing 'processed' payload")
        processed.setdefault("provenance", {})["processor"] = "container-use"
        return processed

    def _process_local(self, document: Dict[str, Any]) -> Dict[str, Any]:
        content = document.get("content", "")
        language = (document.get("language") or settings.default_language).lower()
        content_type = self._detect_content_type(document, content)
        normalized = self._normalize_content(content, content_type)

        snippets = self._build_snippets(normalized)
        key_facts = self._extract_key_facts(normalized, language)
        tables = self._extract_tables(normalized)

        return {
            "source": {
                "title": document.get("title", "Untitled"),
                "url": document.get("url", ""),
                "language": language,
                "content_type": content_type,
                "retrieved_at": document.get("retrieved_at"),
            },
            "summary": document.get("summary", ""),
            "normalized_content": normalized,
            "snippets": snippets,
            "key_facts": key_facts,
            "tables": tables,
            "provenance": {
                "processor": "local",
                "notes": document.get("notes", []),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _detect_content_type(document: Dict[str, Any], content: str) -> str:
        if "content_type" in document:
            return document["content_type"]
        url = document.get("url", "")
        if isinstance(url, str) and url.lower().endswith(".pdf"):
            return "application/pdf"
        snippet = content[:200].lower()
        if "<html" in snippet or "</" in snippet:
            return "text/html"
        return "text/plain"

    def _normalize_content(self, content: str, content_type: str) -> str:
        if not content:
            return ""
        if content_type == "application/pdf":
            return self._convert_pdf_to_text(content)
        if content_type == "text/html":
            return self._convert_html_to_markdown(content)
        return self._cleanup_text(content)

    def _convert_html_to_markdown(self, html: str) -> str:
        if html_to_markdown:
            return self._cleanup_text(html_to_markdown(html))
        stripper = _HTMLStripper()
        stripper.feed(html)
        return self._cleanup_text(stripper.get_text())

    def _convert_pdf_to_text(self, data: str) -> str:
        if pdf_extract_text:
            try:
                return self._cleanup_text(pdf_extract_text(data))  # type: ignore[arg-type]
            except Exception as exc:  # pragma: no cover - best effort
                logger.warning("ContainerProcessor: pdfminer failed (%s); falling back to raw data", exc)
        return self._cleanup_text(data)

    def _cleanup_text(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line)

    def _build_snippets(self, text: str) -> List[Dict[str, Any]]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        snippets: List[Dict[str, Any]] = []
        for idx, paragraph in enumerate(paragraphs[:5]):
            snippets.append({"order": idx + 1, "text": textwrap.shorten(paragraph, width=400)})
        return snippets

    def _extract_key_facts(self, text: str, language: str) -> List[str]:
        sentences = re.split(r"[。．\.!?]\s*", text)
        key_phrases: List[str] = []
        for sentence in sentences:
            cleaned = sentence.strip()
            if not cleaned:
                continue
            if re.search(r"\d", cleaned) or ":" in cleaned or "・" in cleaned:
                key_phrases.append(cleaned)
            if len(key_phrases) >= 8:
                break
        if not key_phrases and sentences:
            key_phrases.append(sentences[0].strip())
        return key_phrases

    def _extract_tables(self, text: str) -> List[str]:
        tables: List[str] = []
        for block in text.split("\n\n"):
            if "|" in block or "\t" in block:
                tables.append(block.strip())
        return tables


def processing_node(
    state: AgentState,
    processor: ContainerProcessor | None = None,
    history_manager: HistoryManager | None = None
) -> Dict[str, Any]:
    """
    Process search results in isolated container environment.

    Parses HTML/PDF content, extracts text, removes noise,
    and prepares data for LLM analysis.
    """
    search_results = state.get("search_results") or []
    if not search_results:
        error_msg = "ProcessingNode: No search results available for processing."
        logger.error(error_msg)
        return add_error(state, error_msg)

    processor = processor or ContainerProcessor()
    processed_entries: List[Dict[str, Any]] = []
    errors: List[str] = []
    seen_urls: set[str] = set()

    for result in search_results:
        url = result.get("url", "")
        if url and url in seen_urls:
            logger.debug("ProcessingNode: Skipping duplicate URL %s", url)
            continue
        if url:
            seen_urls.add(url)

        document = {
            "title": result.get("title", "Untitled"),
            "url": url,
            "content": result.get("content") or result.get("summary", ""),
            "summary": result.get("summary", ""),
            "language": result.get("language") or state.get("language", settings.default_language),
            "retrieved_at": result.get("retrieved_at"),
        }

        try:
            processed_entries.append(processor.process_document(document))
        except ContainerProcessorError as exc:
            msg = f"ProcessingNode: Failed to process {url or document['title']}: {exc}"
            logger.error(msg)
            errors.append(msg)

    if not processed_entries:
        error_msg = "ProcessingNode: Failed to process any documents."
        logger.error(error_msg)
        return add_error(state, error_msg)

    _persist_processed_history(state, processed_entries, history_manager)

    result_state: Dict[str, Any] = {"processed_data": processed_entries}
    if errors:
        result_state["errors"] = state.get("errors", []) + errors
    return result_state


def _persist_processed_history(
    state: AgentState,
    processed_entries: List[Dict[str, Any]],
    history_manager: HistoryManager | None = None
) -> None:
    history_path = state.get("history_path", "").strip()
    if not history_path:
        return

    session_path = Path(history_path)
    if not session_path.exists():
        return

    session_id = session_path.name
    base_path = session_path.parent
    hm = history_manager or HistoryManager(base_path=base_path)

    payload = []
    for entry in processed_entries:
        source = entry.get("source", {})
        payload.append(
            {
                "step": source.get("title") or source.get("url") or "Processed Document",
                "timestamp": entry.get("timestamp"),
                "input": source.get("url", ""),
                "output": "\n".join(entry.get("key_facts", [])) or entry.get("normalized_content", "")[:500],
                "logs": f"Snippets: {len(entry.get('snippets', []))}",
            }
        )

    try:
        hm.save_processed_data(session_id, payload)
    except HistoryManagerError as exc:
        logger.warning("ProcessingNode: Failed to persist processed data: %s", exc)

"""Search node for web information retrieval via web-search-mcp."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from config import settings
from modules.history_manager import HistoryManager, HistoryManagerError
from modules.mcp_client import (
    MCPClientError,
    RateLimitError,
    SearchResult,
    WebSearchClient,
)
from state.agent_state import AgentState, add_error

logger = logging.getLogger(__name__)


def search_node(
    state: AgentState,
    client: WebSearchClient | None = None,
    history_manager: HistoryManager | None = None
) -> Dict[str, Any]:
    """
    Perform resilient multi-strategy web search via web-search-mcp.

    Strategy:
        1. Run `full-web-search` with the requested language
        2. If we have fewer than the configured limit, fall back to
           `get-web-search-summaries`
        3. Generate follow-up queries (per 基本設計書 Section 5 step 2) and run
           them through `multi_search`
        4. Fetch full page content for the top hits that lack bodies

    Results are normalized and written to both state and HistoryManager. Errors
    are propagated through state["errors"] without aborting successful partial
    fetches.
    """
    query = (state.get("query") or "").strip()
    if not query:
        logger.error("SearchNode: Missing query in state")
        return add_error(state, "SearchNode: query is required.")

    language = (state.get("language") or settings.default_language).lower()
    search_limit = max(1, settings.default_search_limit)
    client = client or WebSearchClient()
    aggregated: List[SearchResult] = []
    encountered_errors: List[str] = []

    logger.info("SearchNode: Running full-web-search for '%s' (%s)", query, language)
    try:
        aggregated.extend(
            client.full_search(query, language=language, limit=search_limit)
        )
    except RateLimitError as exc:
        msg = f"SearchNode: full-web-search rate limited: {exc}"
        logger.warning(msg)
        encountered_errors.append(msg)
    except MCPClientError as exc:
        msg = f"SearchNode: full-web-search failed: {exc}"
        logger.error(msg)
        encountered_errors.append(msg)

    if len(aggregated) < search_limit:
        logger.info(
            "SearchNode: Falling back to get-web-search-summaries (have %s, need %s)",
            len(aggregated),
            search_limit,
        )
        try:
            summaries = client.summary_search(
                query,
                language=language,
                limit=search_limit,
            )
            aggregated.extend(summaries)
        except MCPClientError as exc:
            msg = f"SearchNode: summary fallback failed: {exc}"
            logger.error(msg)
            encountered_errors.append(msg)

    if len(aggregated) < search_limit:
        follow_up_queries = _generate_follow_up_queries(query, language)
        if follow_up_queries:
            logger.info(
                "SearchNode: Running follow-up queries %s",
                follow_up_queries,
            )
            try:
                aggregated.extend(
                    client.multi_search(
                        follow_up_queries,
                        language=language,
                        per_query_limit=max(2, search_limit // 2),
                    )
                )
            except MCPClientError as exc:
                msg = f"SearchNode: multi-search failed: {exc}"
                logger.error(msg)
                encountered_errors.append(msg)

    aggregated = _deduplicate_results(aggregated)
    _enrich_results_with_content(
        aggregated,
        client=client,
        language=language,
        error_collector=encountered_errors,
    )

    normalized_results = [_to_state_result(result) for result in aggregated]

    if not normalized_results:
        error_msg = "SearchNode: No search results available after retries."
        logger.error(error_msg)
        return add_error(state, error_msg)

    _persist_search_history(state, normalized_results, history_manager)

    result_state: Dict[str, Any] = {"search_results": normalized_results}
    if encountered_errors:
        result_state["errors"] = state.get("errors", []) + encountered_errors
    return result_state


def _generate_follow_up_queries(query: str, language: str) -> List[str]:
    """Heuristic-based query expansion for broader coverage."""
    extras: List[str] = []
    if language == "ja":
        extras = [f"{query} 根拠", f"{query} 事例", f"{query} 最新ニュース"]
    else:
        extras = [
            f"{query} supporting data",
            f"{query} case study",
            f"{query} regulatory context",
        ]
    return extras


def _deduplicate_results(results: List[SearchResult]) -> List[SearchResult]:
    """Remove duplicate URLs while keeping the earliest occurrence."""
    unique: List[SearchResult] = []
    seen_urls: set[str] = set()
    for item in results:
        url = (item.get("url") or "").strip()
        if url and url in seen_urls:
            continue
        if url:
            seen_urls.add(url)
        unique.append(item)
    return unique


def _enrich_results_with_content(
    results: List[SearchResult],
    *,
    client: WebSearchClient,
    language: str,
    error_collector: List[str],
) -> None:
    """Fetch missing page content for high-priority hits."""
    max_fetches = 3
    fetch_count = 0
    for result in results:
        if fetch_count >= max_fetches:
            break
        if result.get("content"):
            continue
        url = result.get("url")
        if not url:
            continue
        try:
            logger.debug("SearchNode: Fetching page content for %s", url)
            fetched = client.fetch_page_content(url, language=language)
            if fetched.get("content"):
                result["content"] = fetched["content"]
            fetch_count += 1
        except MCPClientError as exc:
            msg = f"SearchNode: Failed to fetch content for {url}: {exc}"
            logger.warning(msg)
            error_collector.append(msg)


def _to_state_result(result: SearchResult) -> Dict[str, Any]:
    """Convert SearchResult to the shape expected in AgentState."""
    summary = result.get("description") or result.get("content", "")[:280]
    return {
        "title": result.get("title", "Untitled"),
        "url": result.get("url", ""),
        "summary": summary.strip() if isinstance(summary, str) else "",
        "content": result.get("content", ""),
        "language": result.get("language"),
        "retrieved_at": result.get("retrieved_at")
        or datetime.now(timezone.utc).isoformat(),
    }


def _persist_search_history(
    state: AgentState,
    results: List[Dict[str, Any]],
    history_manager: HistoryManager | None = None
) -> None:
    """Write search results to HistoryManager if history_path is available."""
    history_path = state.get("history_path", "").strip()
    if not history_path:
        return

    session_path = Path(history_path)
    if not session_path.exists():
        return

    session_id = session_path.name
    base_path = session_path.parent
    hm = history_manager or HistoryManager(base_path=base_path)

    payload = [
        {
            "title": item.get("title", "Untitled"),
            "url": item.get("url", ""),
            "description": item.get("summary", ""),
            "content": item.get("content", ""),
        }
        for item in results
    ]

    try:
        hm.save_search_results(session_id, payload)
    except HistoryManagerError as exc:
        logger.warning("SearchNode: Failed to persist search results: %s", exc)

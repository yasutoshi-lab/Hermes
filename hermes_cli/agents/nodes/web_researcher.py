"""Web research node for Hermes workflow.

This node performs web research for each generated query using browser automation,
collecting sources and content for analysis.
"""

from hermes_cli.agents.state import HermesState
from hermes_cli.tools import BrowserUseClient
import logging

logger = logging.getLogger(__name__)


def web_researcher(state: HermesState) -> HermesState:
    """Perform web research for each generated query.

    Uses browser automation to search and collect information from
    multiple sources for each query.

    Args:
        state: Current workflow state

    Returns:
        Updated state with search results
    """
    queries_to_run = state.follow_up_queries or state.queries
    if not queries_to_run:
        logger.warning("No queries available for web research")
        state.error_log.append("Web research skipped: no queries available")
        return state

    loop_label = f"loop {state.loop_count}" if state.loop_count else "initial pass"
    logger.info(
        "Starting web research for %s queries (%s)",
        len(queries_to_run),
        loop_label,
    )

    try:
        with BrowserUseClient(max_sources=state.max_sources) as browser:
            for idx, query in enumerate(queries_to_run):
                logger.info(
                    "Researching query %s/%s (%s): %s",
                    idx + 1,
                    len(queries_to_run),
                    loop_label,
                    query,
                )

                try:
                    results = browser.search(query, max_sources=state.max_sources)
                    formatted_results = [
                        {
                            "url": r.url,
                            "title": r.title,
                            "snippet": r.snippet,
                            "content": r.content,
                            "timestamp": r.timestamp,
                            "loop": state.loop_count,
                        }
                        for r in results
                    ]

                    existing = state.query_results.get(query, [])
                    state.query_results[query] = existing + formatted_results
                    state.executed_queries.append(query)
                    logger.info(
                        "Collected %s sources for query '%s'",
                        len(results),
                        query,
                    )
                    if not results:
                        logger.warning("No sources returned for query '%s'", query)

                except Exception as e:
                    logger.error(f"Failed to research query '{query}': {e}")
                    state.error_log.append(f"Research error for '{query}': {str(e)}")
                    state.query_results[query] = []

    except Exception as e:
        logger.error(f"Browser initialization failed: {e}")
        state.error_log.append(f"Browser error: {str(e)}")

    # Follow-up queries have been consumed
    state.follow_up_queries = []
    logger.info("Web research complete")
    return state

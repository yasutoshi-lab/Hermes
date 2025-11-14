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
    logger.info(f"Starting web research for {len(state.queries)} queries")

    try:
        with BrowserUseClient(max_sources=state.max_sources) as browser:
            for idx, query in enumerate(state.queries):
                logger.info(f"Researching query {idx + 1}/{len(state.queries)}: {query}")

                try:
                    results = browser.search(query, max_sources=state.max_sources)
                    state.query_results[query] = [
                        {
                            "url": r.url,
                            "title": r.title,
                            "content": r.content,
                            "timestamp": r.timestamp,
                        }
                        for r in results
                    ]
                    logger.info(f"Found {len(results)} sources for query: {query}")

                except Exception as e:
                    logger.error(f"Failed to research query '{query}': {e}")
                    state.error_log.append(f"Research error for '{query}': {str(e)}")
                    state.query_results[query] = []

    except Exception as e:
        logger.error(f"Browser initialization failed: {e}")
        state.error_log.append(f"Browser error: {str(e)}")

    logger.info("Web research complete")
    return state

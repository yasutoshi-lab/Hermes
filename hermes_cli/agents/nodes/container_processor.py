"""Container processing node for Hermes workflow.

This node processes and normalizes collected content in a containerized environment,
ensuring consistent text formatting and extraction.
"""

from hermes_cli.agents.state import HermesState
from hermes_cli.tools import ContainerUseClient
import logging

logger = logging.getLogger(__name__)


def container_processor(state: HermesState) -> HermesState:
    """Process and normalize collected content in container environment.

    Uses containerized text processing to normalize and extract
    meaningful content from research results.

    Args:
        state: Current workflow state

    Returns:
        Updated state with processed notes
    """
    logger.info("Processing content in container")

    try:
        with ContainerUseClient() as container:
            for query, results in state.query_results.items():
                if not results:
                    continue

                logger.info(f"Processing {len(results)} results for query: {query}")

                # Extract content from results
                texts = [r["content"] for r in results if r.get("content")]

                try:
                    # Normalize texts in container
                    normalized = container.normalize_texts(texts)

                    # Combine into single note
                    combined = "\n\n".join(normalized)
                    state.processed_notes[query] = combined

                    logger.info(f"Processed content for query: {query}")

                except Exception as e:
                    logger.error(f"Failed to process query '{query}': {e}")
                    state.error_log.append(f"Processing error for '{query}': {str(e)}")

    except Exception as e:
        logger.error(f"Container initialization failed: {e}")
        state.error_log.append(f"Container error: {str(e)}")

    logger.info("Container processing complete")
    return state

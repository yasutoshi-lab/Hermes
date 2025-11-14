"""Draft aggregation node for Hermes workflow.

This node aggregates processed research notes into a draft report using LLM,
creating a comprehensive initial report.
"""

from hermes_cli.agents.state import HermesState
from hermes_cli.tools import OllamaClient
import logging

logger = logging.getLogger(__name__)


def draft_aggregator(state: HermesState) -> HermesState:
    """Aggregate processed notes into draft report using LLM.

    Combines all processed research notes and generates a comprehensive
    draft report answering the original question.

    Args:
        state: Current workflow state

    Returns:
        Updated state with draft report
    """
    logger.info("Aggregating draft report")

    # Combine all processed notes
    all_notes = "\n\n---\n\n".join(
        f"## Query: {query}\n\n{notes}"
        for query, notes in state.processed_notes.items()
    )

    prompt = f"""Based on the following research notes, create a comprehensive report
answering the original question.

Original Question: {state.user_prompt}

Research Notes:
{all_notes}

Create a well-structured markdown report in {state.language}."""

    try:
        # TODO: Implement actual LLM call
        # Example:
        # client = OllamaClient(config)
        # response = client.chat([{"role": "user", "content": prompt}])
        # state.draft_report = response

        # For now, create placeholder
        state.draft_report = f"# Draft Report\n\n{all_notes}"
        logger.info("Draft report created")

    except Exception as e:
        logger.error(f"Draft aggregation failed: {e}")
        state.error_log.append(f"Draft error: {str(e)}")

    return state

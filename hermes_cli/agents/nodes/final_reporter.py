"""Final reporter node for Hermes workflow.

This node finalizes the report with metadata and formatting,
producing the final validated output.
"""

from hermes_cli.agents.state import HermesState
import logging

logger = logging.getLogger(__name__)


def final_reporter(state: HermesState) -> HermesState:
    """Finalize report with metadata and formatting.

    Adds metadata header and performs final formatting to produce
    the complete validated report.

    Args:
        state: Current workflow state

    Returns:
        Updated state with final validated report
    """
    logger.info("Creating final report")

    if not state.draft_report:
        logger.error("No draft report available")
        state.validated_report = "# Error\n\nNo report could be generated."
        return state

    # Add metadata header
    metadata = f"""---
query: {state.user_prompt}
language: {state.language}
queries_generated: {len(state.queries)}
sources_collected: {sum(len(r) for r in state.query_results.values())}
validation_loops: {state.loop_count}
---

"""

    state.validated_report = metadata + state.draft_report
    logger.info("Final report complete")

    return state

"""Draft aggregation node for Hermes workflow.

This node aggregates processed research notes into a draft report using LLM,
creating a comprehensive initial report.
"""

import logging

from hermes_cli.agents.state import HermesState

logger = logging.getLogger(__name__)


def draft_aggregator(state: HermesState) -> HermesState:
    """Aggregate processed notes into draft report using LLM."""
    logger.info("Aggregating draft report")

    if not state.processed_notes:
        logger.warning("No processed notes available; draft quality may be degraded")

    all_notes = "\n\n---\n\n".join(
        f"## Query: {query}\n\n{notes}"
        for query, notes in state.processed_notes.items()
    ).strip()

    system_prompt = (
        "You are an expert research analyst. Create a concise, well-structured "
        "markdown report citing the provided notes."
    )
    user_prompt = (
        f"Original question:\n{state.user_prompt}\n\n"
        f"Language: {state.language}\n\n"
        "Research notes:\n"
        f"{all_notes or 'No structured notes were provided; summarize based on the question.'}\n\n"
        "Write a markdown report with:\n"
        "- Executive summary\n"
        "- Key findings\n"
        "- Supporting details referencing the queries\n"
        "- Recommended next steps\n"
    )

    try:
        response = state.call_ollama(system_prompt, user_prompt)
        state.draft_report = response.strip()
        logger.info("Draft report created using Ollama")

    except Exception as exc:  # pragma: no cover - covered in integration
        logger.error("Draft aggregation failed: %s", exc, exc_info=True)
        state.error_log.append(f"Draft aggregation error: {exc}")

    return state

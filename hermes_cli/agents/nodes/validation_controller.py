"""Validation controller node for Hermes workflow.

This node controls the validation loop, deciding whether to continue
validation or proceed to final report generation.
"""

from hermes_cli.agents.state import HermesState
import logging

logger = logging.getLogger(__name__)


def validation_controller(state: HermesState) -> HermesState:
    """Control validation loop - decide whether to continue or finish.

    Checks validation loop count against min/max thresholds and
    quality criteria to determine next action.

    Args:
        state: Current workflow state

    Returns:
        Updated state with validation completion flag
    """
    logger.info(
        "Validation controller: loop %s/%s (quality=%.2f threshold=%.2f)",
        state.loop_count,
        state.max_validation,
        state.quality_score,
        state.quality_threshold,
    )

    # Check if we've done minimum loops
    if state.loop_count < state.min_validation:
        logger.info("Continuing validation (below minimum)")
        state.validation_complete = False
        return state

    # Check if we've hit maximum loops
    if state.loop_count >= state.max_validation:
        logger.info("Validation complete (maximum reached)")
        state.validation_complete = True
        return state

    # Evaluate draft quality heuristically
    quality_score = _evaluate_quality(state)
    state.quality_score = quality_score

    if quality_score >= state.quality_threshold:
        logger.info("Validation complete (quality threshold met: %.2f)", quality_score)
        state.validation_complete = True
    else:
        logger.info("Continuing validation (quality %.2f below threshold %.2f)", quality_score, state.quality_threshold)
        state.validation_complete = False

    return state


def _evaluate_quality(state: HermesState) -> float:
    """Compute a heuristic quality score for the current draft."""
    draft = state.draft_report or ""
    draft_score = min(len(draft) / 1200.0, 1.0)

    if state.queries:
        processed = len([v for v in state.processed_notes.values() if v.strip()])
        coverage_score = min(processed / len(state.queries), 1.0)
    else:
        coverage_score = 0.0

    total_sources = sum(len(results) for results in state.query_results.values())
    max_possible_sources = max(1, len(state.executed_queries or state.queries) * state.max_sources)
    source_score = min(total_sources / max_possible_sources, 1.0)

    loop_bonus = min(state.loop_count / max(1, state.max_validation), 1.0)

    return round(
        0.35 * draft_score +
        0.25 * coverage_score +
        0.25 * source_score +
        0.15 * loop_bonus,
        3,
    )

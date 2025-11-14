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
    logger.info(f"Validation controller: loop {state.loop_count}/{state.max_validation}")

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

    # TODO: Add quality check logic here
    # Could analyze draft for:
    # - Completeness
    # - Citation quality
    # - Answer accuracy
    # - Structure quality

    # For now, just complete after min loops
    logger.info("Validation complete (minimum satisfied)")
    state.validation_complete = True

    return state

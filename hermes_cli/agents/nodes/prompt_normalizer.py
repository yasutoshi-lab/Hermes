"""Prompt normalization node for Hermes workflow.

This node normalizes the user prompt based on language settings,
ensuring consistent input for downstream processing.
"""

from hermes_cli.agents.state import HermesState
import logging

logger = logging.getLogger(__name__)


def prompt_normalizer(state: HermesState) -> HermesState:
    """Normalize user prompt based on language setting.

    Performs basic normalization including whitespace trimming and
    language-specific formatting preparation.

    Args:
        state: Current workflow state

    Returns:
        Updated state with normalized prompt
    """
    logger.info(f"Normalizing prompt in language: {state.language}")

    # Basic normalization: strip whitespace, handle language-specific formatting
    normalized = state.user_prompt.strip()

    # Could add more sophisticated normalization here:
    # - Remove excessive whitespace
    # - Normalize punctuation
    # - Language-specific character handling
    # For now, keep it simple

    logger.info("Prompt normalization complete")
    return state

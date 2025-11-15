"""Prompt normalization node"""

from loguru import logger
from hermes_cli.agents.state import WorkflowState


def normalize_prompt(state: WorkflowState) -> WorkflowState:
    """プロンプト正規化"""
    logger.info("Normalizing prompt", extra={"category": "RUN"})

    state["current_node"] = "normalize_prompt"

    prompt = state["original_prompt"]

    # 空白の正規化
    normalized = " ".join(prompt.split())

    # 前後の空白削除
    normalized = normalized.strip()

    state["normalized_prompt"] = normalized

    logger.info(
        f"Prompt normalized: {len(prompt)} -> {len(normalized)} chars",
        extra={"category": "RUN"},
    )

    return state

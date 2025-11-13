"""LLM node for generating analysis using Ollama."""

from typing import Dict, Any
from ..state.agent_state import AgentState


def llm_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate analysis and provisional answer using Ollama LLM.

    Calls Ollama with the configured model (default: gpt-oss:20b)
    to analyze processed data and generate insights.

    Args:
        state: Current agent state with processed data

    Returns:
        Updated state with provisional answer
    """
    # TODO: Implement Ollama integration
    # TODO: Add model selection logic
    # TODO: Handle tool calling if needed
    return {}

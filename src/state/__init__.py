"""State management module for research analyst agent."""

from .agent_state import (
    AgentState,
    create_initial_state,
    add_error,
    increment_verification_count,
    NodeFunction
)

__all__ = [
    "AgentState",
    "create_initial_state",
    "add_error",
    "increment_verification_count",
    "NodeFunction"
]

"""Search node for web information retrieval via web-search-mcp."""

from typing import Dict, Any
from ..state.agent_state import AgentState


def search_node(state: AgentState) -> Dict[str, Any]:
    """
    Perform web search using web-search-mcp.

    Uses full-web-search or get-web-search-summaries to retrieve
    relevant information based on the query.

    Args:
        state: Current agent state with query

    Returns:
        Updated state with search results
    """
    # TODO: Implement web-search-mcp integration
    # TODO: Handle search errors and retries
    return {}

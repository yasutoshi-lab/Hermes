"""Query generation node for Hermes workflow.

This node generates multiple search queries from the user prompt using LLM,
creating diverse queries to gather comprehensive information.
"""

from hermes_cli.agents.state import HermesState
from hermes_cli.tools import OllamaClient, OllamaConfig
import logging

logger = logging.getLogger(__name__)


def query_generator(state: HermesState) -> HermesState:
    """Generate multiple search queries from user prompt using LLM.

    Creates 3-5 diverse search queries that will help gather
    comprehensive information for the research question.

    Args:
        state: Current workflow state

    Returns:
        Updated state with generated queries
    """
    logger.info("Generating search queries from prompt")

    # TODO: Get Ollama config from somewhere (will be provided by run_service)
    # For now, use placeholder

    prompt = f"""Based on the following research question, generate 3-5 diverse search queries
that would help gather comprehensive information.

Research Question: {state.user_prompt}

Language: {state.language}

Generate queries in {state.language}. Return only the queries, one per line."""

    try:
        # TODO: Implement actual LLM call
        # Example:
        # client = OllamaClient(config)
        # response = client.chat([{"role": "user", "content": prompt}])
        # queries = response.strip().split('\n')

        # For now, create placeholder queries
        queries = [
            f"Query 1 for: {state.user_prompt}",
            f"Query 2 for: {state.user_prompt}",
            f"Query 3 for: {state.user_prompt}",
        ]

        state.queries = queries
        logger.info(f"Generated {len(queries)} queries")

    except Exception as e:
        logger.error(f"Query generation failed: {e}")
        state.error_log.append(f"Query generation error: {str(e)}")

    return state

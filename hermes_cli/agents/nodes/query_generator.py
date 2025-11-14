"""Query generation node for Hermes workflow.

This node generates multiple search queries from the user prompt using LLM,
creating diverse queries to gather comprehensive information.
"""

from __future__ import annotations

import logging
import re
from typing import List

from hermes_cli.agents.state import HermesState

logger = logging.getLogger(__name__)


def query_generator(state: HermesState) -> HermesState:
    """Generate multiple search queries from user prompt using LLM."""
    logger.info("Generating search queries from prompt")

    desired_count = max(1, state.query_count or 3)

    system_prompt = (
        "You are a research assistant that proposes diverse, high-quality search "
        "queries to investigate a topic."
    )
    user_prompt = (
        "Research question:\n"
        f"{state.user_prompt}\n\n"
        f"Language: {state.language}\n"
        f"Provide {desired_count} distinct web search queries. "
        "Return them as a simple list, one per line. "
        "Avoid explanations or markdown."
    )

    try:
        response = state.call_ollama(system_prompt, user_prompt)
        parsed = _parse_queries(response, desired_count)

        if not parsed:
            raise ValueError("LLM response did not contain any queries")

        state.queries = parsed
        logger.info("Generated %s queries via Ollama", len(parsed))

    except Exception as exc:  # pragma: no cover - exercised via tests for error handling
        logger.error("Query generation failed: %s", exc, exc_info=True)
        state.error_log.append(f"Query generation error: {exc}")
        if not state.queries:
            # Fallback to at least one query using the original prompt
            state.queries = [state.user_prompt]

    return state


def _parse_queries(raw_text: str, desired_count: int) -> List[str]:
    """Normalize LLM output into a clean list of queries."""
    queries: List[str] = []

    for line in raw_text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue
        # Remove numbering such as "1. " or "- "
        cleaned = re.sub(r"^\s*[\-\*\d\.\)\:]+\s*", "", cleaned).strip()
        if cleaned:
            queries.append(cleaned)

    return queries[:desired_count]

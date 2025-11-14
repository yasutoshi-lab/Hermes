"""Validator node for Hermes workflow.

This node validates and improves the draft report using LLM-based review,
checking for accuracy, completeness, and clarity.
"""

import logging
import re
from typing import List

from hermes_cli.agents.state import HermesState

logger = logging.getLogger(__name__)


def validator(state: HermesState) -> HermesState:
    """Validate and improve draft report."""
    logger.info("Validating report (loop %s)", state.loop_count)

    if not state.draft_report:
        logger.warning("No draft to validate")
        return state

    system_prompt = (
        "You are a meticulous technical editor. Improve the report while preserving facts."
    )
    user_prompt = (
        "Review the following markdown report and revise it to improve accuracy, "
        "coverage, and clarity. Keep the language consistent with the requested language.\n\n"
        f"{state.draft_report}\n\n"
        "Ensure the final output is markdown and highlight improvements subtly without "
        "adding commentary outside the report.\n\n"
        "Identify up to three missing evidence gaps and propose short follow-up search "
        "queries for each gap. Append them at the end of the report under a heading "
        "titled 'Follow-up Queries' as bullet points."
    )

    try:
        response = state.call_ollama(system_prompt, user_prompt)
        state.draft_report = response.strip()
        state.loop_count += 1

        llm_follow_ups = _extract_follow_up_queries(state.draft_report)
        if llm_follow_ups:
            state.follow_up_queries = llm_follow_ups
        else:
            state.follow_up_queries = _generate_follow_up_queries(state)

        if state.follow_up_queries:
            logger.info(
                "Validation identified %s follow-up queries",
                len(state.follow_up_queries),
            )
        logger.info("Validation loop %s completed", state.loop_count)

    except Exception as exc:  # pragma: no cover
        logger.error("Validation failed: %s", exc, exc_info=True)
        state.error_log.append(f"Validation error: {exc}")

    return state


def _extract_follow_up_queries(report: str, max_items: int = 3) -> List[str]:
    """Extract follow-up queries section from validator output, if present."""
    if not report:
        return []

    queries: List[str] = []
    capture = False

    bullet_re = re.compile(r"^[\-\*\+•]\s*")
    ordinal_re = re.compile(r"^\d+[\.\)]\s*")

    for raw_line in report.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        normalized = line.lower()
        if not capture and "follow-up queries" in normalized:
            capture = True
            continue

        if capture and line.startswith("#"):
            break

        if capture:
            entry = bullet_re.sub("", line)
            entry = ordinal_re.sub("", entry).strip()
            if entry:
                queries.append(entry)
            if len(queries) >= max_items:
                break

    return queries


def _generate_follow_up_queries(state: HermesState, max_items: int = 3) -> List[str]:
    """Generate deterministic follow-up queries based on coverage gaps."""
    deficit_queries: List[str] = []
    min_required = max(1, state.min_sources)

    for query, results in state.query_results.items():
        if len(results) < min_required:
            deficit_queries.append(
                f"{query} primary sources and statistics"
            )

    if not deficit_queries:
        suffixes = ["recent developments", "case studies", "expert interviews"]
        base_prompt = state.user_prompt
        deficit_queries = [
            f"{base_prompt} {suffix}"
            for suffix in suffixes
        ]

    # Deduplicate while preserving order
    seen = set()
    unique_queries: List[str] = []
    for query in deficit_queries:
        if query not in seen:
            seen.add(query)
            unique_queries.append(query)

    return unique_queries[:max_items]

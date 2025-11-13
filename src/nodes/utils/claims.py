"""Helpers for extracting lightweight claims from provisional answers."""

from __future__ import annotations

import re
from typing import List, Dict

_SENTENCE_BOUNDARY_PATTERN = re.compile(r"(?<=[。．\.\?!！？])\s+")
_BULLET_PATTERN = re.compile(r"^\s*[-*•●]\s+")
_NUMBER_PATTERN = re.compile(r"\d+(?:[\.,]\d+)?")


def _score_candidate(text: str) -> float:
    """Assign a heuristic priority score to a candidate claim."""
    score = 1.0
    if _NUMBER_PATTERN.search(text):
        score += 0.4
    if len(text) >= 80:
        score += 0.2
    if any(marker in text for marker in (":", "：", "によれば", "according")):
        score += 0.1
    return score


def _split_sentences(paragraph: str) -> List[str]:
    """Split a paragraph into lightweight sentences."""
    if not paragraph:
        return []
    parts = _SENTENCE_BOUNDARY_PATTERN.split(paragraph)
    sentences: List[str] = []
    for part in parts:
        chunk = part.strip().strip("・-•●")
        if chunk:
            sentences.append(chunk)
    return sentences


def extract_claims(text: str, max_claims: int = 5) -> List[Dict[str, object]]:
    """Extract high-priority claims from free-form text.

    Args:
        text: Provisional answer text.
        max_claims: Maximum number of claims to return.

    Returns:
        List of claim dictionaries with fields:
            - text: Claim sentence
            - priority: Heuristic score used for ordering
            - paragraph: Paragraph index (0-based)
            - line: Line index within the paragraph

    Example:
        >>> extract_claims("LangGraphは2023年に公開され、2つの主要モジュールを持ちます。\n\n" \
        ...               "It supports multi-actor graphs.")
        [{'text': 'LangGraphは2023年に公開され、2つの主要モジュールを持ちます。', ...}, ...]
    """
    if not text or not text.strip():
        return []

    raw_claims: List[Dict[str, object]] = []
    paragraphs = [para.strip() for para in text.split("\n\n") if para.strip()]
    order = 0
    for paragraph_index, paragraph in enumerate(paragraphs):
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        for line_index, line in enumerate(lines):
            candidate_line = _BULLET_PATTERN.sub("", line).strip()
            for sentence in _split_sentences(candidate_line or line):
                normalized_sentence = sentence.strip()
                if len(normalized_sentence) < 8:
                    continue
                score = _score_candidate(normalized_sentence)
                raw_claims.append({
                    "text": normalized_sentence,
                    "priority": score,
                    "paragraph": paragraph_index,
                    "line": line_index,
                    "order": order,
                })
                order += 1

    raw_claims.sort(key=lambda item: (-float(item["priority"]), item["order"]))
    top_claims = raw_claims[:max(0, max_claims)]
    for claim in top_claims:
        claim.pop("order", None)
    return top_claims


__all__ = ["extract_claims"]

"""Verification node for validating and fact-checking results."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Sequence

from config import settings
from state.agent_state import AgentState, add_error, increment_verification_count
from .utils.claims import extract_claims

logger = logging.getLogger(__name__)

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9一-龠ぁ-んァ-ヶー]+")
NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?")


class SearchClient(Protocol):
    """Protocol describing the minimal search interface used for verification."""

    def search(self, query: str, *, language: str, limit: int = 3) -> list[dict]:
        """Execute a search for the given query and return MCP-style results."""


class NullSearchClient:
    """Fallback search client used when no implementation is injected."""

    def search(self, query: str, *, language: str, limit: int = 3) -> list[dict]:
        logger.debug(
            "VerificationNode: NullSearchClient invoked (query=%s, language=%s, limit=%s)",
            query,
            language,
            limit
        )
        return []


def _normalize_language(value: Optional[str]) -> str:
    return "ja" if value == "ja" else "en"


def _build_corpus(results: Sequence[dict]) -> List[str]:
    corpus: List[str] = []
    for result in results:
        for key in ("snippet", "content", "description", "extracted_info"):
            snippet = result.get(key)
            if snippet:
                corpus.append(str(snippet))
                break
    return corpus


def _score_claim_support(claim_text: str, corpus: Sequence[str]) -> float:
    if not corpus or not claim_text:
        return 0.0

    tokens = [token.lower() for token in TOKEN_PATTERN.findall(claim_text) if len(token) > 1]
    numbers = NUMBER_PATTERN.findall(claim_text)
    best_score = 0.0

    for snippet in corpus:
        normalized_snippet = snippet.lower()
        if not normalized_snippet:
            continue

        token_hits = sum(1 for token in tokens if token in normalized_snippet)
        token_score = (token_hits / len(tokens)) if tokens else 0.0

        number_hits = sum(1 for number in numbers if number in snippet)
        number_score = (number_hits / len(numbers)) if numbers else 0.0

        snippet_score = min(1.0, (token_score * 0.7) + (number_score * 0.3))
        best_score = max(best_score, snippet_score)

    return best_score


def _classify_claim(score: float) -> str:
    if score >= settings.verification_claim_pass_threshold:
        return "pass"
    if score >= settings.verification_claim_review_threshold:
        return "review"
    return "fail"


def _format_summary(language: str, summary: Dict[str, Any]) -> str:
    template_ja = (
        "検証結果: {passed}/{total} 件の主張を確認 (信頼度 {confidence:.2f}). "
        "{action}"
    )
    template_en = (
        "Verification results: {passed}/{total} claims validated (avg confidence {confidence:.2f}). "
        "{action}"
    )
    action_ja = "追加検索が必要です。" if summary["needs_additional_search"] else "レポート生成に進みます。"
    action_en = "Additional search required." if summary["needs_additional_search"] else "Proceeding to report."

    template = template_ja if language == "ja" else template_en
    action = action_ja if language == "ja" else action_en
    return template.format(
        passed=summary["passed"],
        total=summary["total_claims"],
        confidence=summary["average_confidence"],
        action=action
    )


def _format_claim_detail(language: str, claim_result: Dict[str, Any]) -> str:
    status_labels = {
        "pass": ("確認済み", "PASS"),
        "review": ("再確認推奨", "REVIEW"),
        "fail": ("要再調査", "FAIL")
    }
    ja_label, en_label = status_labels[claim_result["status"]]
    label = ja_label if language == "ja" else en_label
    prefix = "検証" if language == "ja" else "Verification"
    return (
        f"{prefix} [{label}]: {claim_result['text']} "
        f"(score={claim_result['support_score']})"
    )


def _persist_findings(history_path: str, summary: Dict[str, Any], claims: List[Dict[str, Any]]) -> None:
    if not history_path:
        return

    try:
        verified_dir = Path(history_path)
        verified_dir.mkdir(parents=True, exist_ok=True)
        verified_file = verified_dir / "verified.md"
        timestamp = datetime.now().isoformat()

        lines = [
            f"## Verification Run - {timestamp}",
            "",
            f"- Total claims: {summary['total_claims']}",
            f"- Passed: {summary['passed']}",
            f"- Failed: {summary['failed']}",
            f"- Needs review: {summary['needs_review']}",
            f"- Average confidence: {summary['average_confidence']:.2f}",
            f"- Next action: {'Re-run search' if summary['needs_additional_search'] else 'Proceed to report'}",
            "",
            "### Claims",
            "",
        ]

        for idx, claim in enumerate(claims, start=1):
            lines.extend([
                f"#### Claim {idx}",
                f"- Text: {claim['text']}",
                f"- Status: {claim['status']}",
                f"- Score: {claim['support_score']}",
                f"- Sources checked: {claim['sources_checked']}",
                ""
            ])

        with verified_file.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
    except OSError as exc:
        logger.warning("VerificationNode: Failed to persist verification log: %s", exc)


def _resolve_search_client(state: AgentState) -> SearchClient:
    candidate = state.get("search_client")
    if candidate and callable(getattr(candidate, "search", None)):
        return candidate  # type: ignore[return-value]
    return NullSearchClient()


def verification_node(state: AgentState) -> Dict[str, Any]:
    """
    Verify provisional answer and check for inconsistencies.

    Args:
        state: Current agent state with provisional answer

    Returns:
        Updated state with verification results and loop decision
    """
    provisional_answer = state.get("provisional_answer", "")
    if not provisional_answer or not provisional_answer.strip():
        return add_error(state, "VerificationNode: provisional_answer is empty")

    language = _normalize_language(state.get("language"))
    claims = extract_claims(provisional_answer, max_claims=settings.verification_max_claims)

    search_client = _resolve_search_client(state)
    existing_results_raw = state.get("search_results") or []
    existing_results = list(existing_results_raw)
    existing_corpus = _build_corpus(existing_results)
    aggregated_new_results: List[dict] = []
    claim_results: List[Dict[str, Any]] = []

    if not claims:
        summary = {
            "total_claims": 0,
            "passed": 0,
            "failed": 0,
            "needs_review": 0,
            "average_confidence": 1.0,
            "pass_ratio": 1.0,
            "needs_additional_search": False,
        }
        updates = increment_verification_count(state)
        updates.update({
            "verification_summary": summary,
            "messages": [{"role": "system", "content": _format_summary(language, summary)}],
        })
        _persist_findings(state.get("history_path", ""), summary, [])
        return updates

    for claim in claims:
        try:
            fetched_results = search_client.search(
                claim["text"],
                language=language,
                limit=settings.verification_search_limit
            ) or []
        except Exception as exc:  # pragma: no cover - dependent on external MCP
            logger.warning("VerificationNode: Search client error for claim '%s': %s", claim["text"], exc)
            fetched_results = []

        aggregated_new_results.extend(fetched_results)
        fetched_corpus = _build_corpus(fetched_results)
        combined_corpus = existing_corpus + fetched_corpus
        score = _score_claim_support(claim["text"], combined_corpus)
        existing_corpus.extend(fetched_corpus)

        status = _classify_claim(score)
        claim_results.append({
            "text": claim["text"],
            "status": status,
            "support_score": round(score, 3),
            "sources_checked": len(fetched_results),
        })

    total = len(claim_results)
    passed = sum(1 for c in claim_results if c["status"] == "pass")
    failed = sum(1 for c in claim_results if c["status"] == "fail")
    needs_review = sum(1 for c in claim_results if c["status"] == "review")

    avg_confidence = sum(c["support_score"] for c in claim_results) / total if total else 1.0
    pass_ratio = passed / total if total else 1.0
    needs_additional_search = (
        failed > 0
        or pass_ratio < settings.verification_pass_ratio
        or avg_confidence < settings.verification_min_confidence
        or (needs_review > 0 and pass_ratio < 1.0)
    )

    summary = {
        "total_claims": total,
        "passed": passed,
        "failed": failed,
        "needs_review": needs_review,
        "average_confidence": round(avg_confidence, 3),
        "pass_ratio": round(pass_ratio, 3),
        "needs_additional_search": needs_additional_search,
    }

    errors = [
        f"Claim verification failed: {claim['text']} (score={claim['support_score']})"
        for claim in claim_results
        if claim["status"] == "fail"
    ]

    messages = [{"role": "system", "content": _format_summary(language, summary)}]
    for claim in claim_results:
        if claim["status"] != "pass":
            messages.append({"role": "system", "content": _format_claim_detail(language, claim)})

    updates = increment_verification_count(state)
    updates.update({
        "verification_summary": summary,
        "messages": messages,
    })

    if aggregated_new_results:
        updates["search_results"] = existing_results + aggregated_new_results

    if errors:
        updates["errors"] = state.get("errors", []) + errors

    _persist_findings(state.get("history_path", ""), summary, claim_results)

    return updates

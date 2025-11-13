"""Tests for VerificationNode behavior."""

import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from state import create_initial_state  # type: ignore  # noqa: E402

verification_module = importlib.import_module("nodes.verification_node")  # type: ignore


class SupportiveSearchClient:
    def search(self, query: str, *, language: str, limit: int = 3):  # noqa: D401
        return [{"snippet": f"{query} was confirmed in 2023 according to docs."}]


class EmptySearchClient:
    def search(self, query: str, *, language: str, limit: int = 3):  # noqa: D401
        return []


class ErrorSearchClient:
    def search(self, query: str, *, language: str, limit: int = 3):  # noqa: D401
        raise RuntimeError("search failed")


class MismatchSearchClient:
    def search(self, query: str, *, language: str, limit: int = 3):  # noqa: D401
        return [{"snippet": "Unrelated snippet"}]


def _state_with_answer(tmp_path, provisional_answer: str, language: str = "en") -> dict:
    state = create_initial_state()
    state["messages"] = [{"role": "user", "content": "Verify"}]
    state["query"] = "Test"
    state["search_results"] = []
    state["processed_data"] = []
    state["provisional_answer"] = provisional_answer
    state["language"] = language
    state["history_path"] = str(tmp_path)
    state["verification_summary"] = {}
    return state


def test_verification_node_marks_claim_as_pass_and_persists(tmp_path):
    state = _state_with_answer(tmp_path, "LangGraph launched in 2023 and supports loops.")
    state["search_client"] = SupportiveSearchClient()

    result = verification_module.verification_node(state)

    summary = result["verification_summary"]
    assert summary["needs_additional_search"] is False
    assert Path(tmp_path / "verified.md").exists()
    assert "Verification results" in result["messages"][0]["content"]
    assert "errors" not in result


def test_verification_node_flags_failed_claims(tmp_path):
    answer = "LangGraph released in 2020 and handles 100 sources per minute."
    state = _state_with_answer(tmp_path, answer, language="ja")
    state["search_client"] = EmptySearchClient()

    result = verification_module.verification_node(state)

    summary = result["verification_summary"]
    assert summary["needs_additional_search"] is True
    assert any("要再調査" in message["content"] for message in result["messages"] if message["role"] == "system")
    assert any("Claim verification failed" in err for err in result["errors"])


def test_verification_node_appends_new_search_results(tmp_path):
    state = _state_with_answer(tmp_path, "LangGraph has two core modules.")
    state["search_client"] = MismatchSearchClient()

    result = verification_module.verification_node(state)

    assert len(result.get("search_results", [])) == 1
    assert result["verification_summary"]["needs_additional_search"] is True


def test_verification_node_handles_search_client_errors(tmp_path):
    state = _state_with_answer(tmp_path, "LangGraph powers research automation.")
    state["search_client"] = ErrorSearchClient()

    result = verification_module.verification_node(state)

    assert result["verification_summary"]["needs_additional_search"] is True


def test_verification_node_handles_text_without_claims(tmp_path):
    state = _state_with_answer(tmp_path, "N/A", language="en")
    state["search_client"] = EmptySearchClient()

    result = verification_module.verification_node(state)

    assert result["verification_summary"]["total_claims"] == 0
    assert result["verification_summary"]["needs_additional_search"] is False

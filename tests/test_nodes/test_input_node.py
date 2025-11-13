"""Tests for InputNode and helper utilities."""

import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from config import settings as app_settings  # type: ignore  # noqa: E402
from state import create_initial_state  # type: ignore  # noqa: E402
from modules.history_manager import HistoryManagerError  # type: ignore  # noqa: E402

input_node_module = importlib.import_module("nodes.input_node")  # type: ignore


@pytest.fixture
def session_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(input_node_module.settings, "session_storage_path", tmp_path)
    return tmp_path


def _base_state(message: str) -> dict:
    state = create_initial_state()
    state["messages"] = [{"role": "user", "content": message}]
    state["language"] = ""
    state["model_name"] = ""
    state["history_path"] = ""
    return state


def test_input_node_detects_japanese_message(session_dir) -> None:
    state = _base_state("LangGraphとは何ですか？ 最新情報も合わせて説明してください。")

    result = input_node_module.input_node(state)

    assert result["language"] == "ja"
    assert result["query"] == "LangGraphとは何ですか？ 最新情報も合わせて説明してください。"
    assert Path(result["history_path"]).exists()
    assert result["messages"][0]["role"] == "system"


def test_input_node_detects_english_even_with_japanese_code(session_dir) -> None:
    message = """Please summarize the API.\n```python\nprint('こんにちは')\n```"""
    state = _base_state(message)

    result = input_node_module.input_node(state)

    assert result["language"] == "en"


def test_input_node_respects_user_configuration(session_dir, tmp_path) -> None:
    state = _base_state("Custom config test")
    state["language"] = "en"
    state["model_name"] = "custom-model"
    custom_path = tmp_path / "session_existing"
    custom_path.mkdir()
    state["history_path"] = str(custom_path)

    result = input_node_module.input_node(state)

    assert result["language"] == "en"
    assert result["model_name"] == "custom-model"
    assert result["history_path"] == str(custom_path)


def test_input_node_handles_empty_input(session_dir) -> None:
    state = _base_state("   ")

    result = input_node_module.input_node(state)

    assert "errors" in result
    assert any("Failed to prepare input" in err for err in result["errors"])


def test_input_node_falls_back_to_default_model(session_dir) -> None:
    state = _base_state("Need default model")
    state["model_name"] = "   "

    result = input_node_module.input_node(state)

    assert result["model_name"] == app_settings.default_model


def test_input_node_warns_when_history_manager_fails(monkeypatch, session_dir) -> None:
    class BrokenHistoryManager:
        def __init__(self, *_, **__):
            pass

        def create_session(self) -> str:  # pragma: no cover - simple stub
            raise HistoryManagerError("disk full")

    monkeypatch.setattr(input_node_module, "HistoryManager", BrokenHistoryManager)

    state = _base_state("History failure should warn")
    state["language"] = "en"

    result = input_node_module.input_node(state)

    assert result["history_path"] == ""
    assert any("Warning" in msg["content"] for msg in result["messages"])


def test_prepare_initial_context_preserves_unicode(session_dir) -> None:
    messages = [{"role": "user", "content": "LangGraph🙂の最新情報"}]
    context = input_node_module.prepare_initial_context(messages)

    assert "🙂" in context["query"]


def test_prepare_initial_context_requires_messages() -> None:
    with pytest.raises(input_node_module.InputPreparationError):
        input_node_module.prepare_initial_context([])

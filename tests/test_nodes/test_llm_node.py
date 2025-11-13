"""Tests for the LLM node implementation."""

import importlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

llm_node_module = importlib.import_module("nodes.llm_node")  # noqa: E402
from nodes.llm_node import llm_node  # noqa: E402
from modules.model_manager import OllamaConnectionError  # noqa: E402
from state.agent_state import create_initial_state  # noqa: E402


class MockModelManager:
    """Simple mock that records prompts and returns canned responses."""

    def __init__(self, response: str = "Mock response"):
        self.response = response
        self.prompts: list[str] = []

    @staticmethod
    def get_system_prompt(language: str, task_type: str = "general") -> str:
        return f"system:{language}:{task_type}"

    def generate(self, model_name: str, prompt: str, **kwargs) -> str:  # pragma: no cover - invoked in tests
        self.prompts.append(prompt)
        return self.response

    def generate_streaming(self, *args, **kwargs):  # pragma: no cover - streaming tests patch custom class
        raise NotImplementedError("Streaming not used in this mock")


class FlakyStreamManager(MockModelManager):
    """Mock manager that fails once when streaming then succeeds."""

    def __init__(self):
        super().__init__()
        self._fail_once = True

    def generate_streaming(self, *args, **kwargs):
        if self._fail_once:
            self._fail_once = False
            raise OllamaConnectionError("stream failure")
        yield "partial "
        yield "answer"


class TestLLMNode(unittest.TestCase):
    """Unit tests for llm_node behavior."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.session_dir = Path(self.temp_dir.name) / "session_test"
        self.session_dir.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _build_state(self, **overrides):
        state = create_initial_state(
            query="LangGraph overview",
            language="en",
            model_name="test-model",
            history_path=str(self.session_dir),
        )
        state["processed_data"] = [
            {
                "source": {"title": "Doc1", "url": "https://example.com/doc1"},
                "summary": "LangGraph enables stateful agents.",
                "key_facts": ["LangGraph is stateful.", "Supports multi-actor graphs."],
            }
        ]
        state.update(overrides)
        return state

    def test_llm_node_generates_answer_and_writes_summary(self):
        mock_manager = MockModelManager(response="Sample answer with [S1]")
        state = self._build_state(model_manager=mock_manager)

        updates = llm_node(state)

        self.assertIn("provisional_answer", updates)
        self.assertIn("Sample answer", updates["provisional_answer"])
        metadata = updates.get("llm_metadata", {})
        self.assertEqual(metadata.get("model"), "test-model")
        self.assertEqual(metadata.get("context_items"), 1)
        summary_file = self.session_dir / "llm_summary.md"
        self.assertTrue(summary_file.exists())
        self.assertIn("[S1]", summary_file.read_text(encoding="utf-8"))

    def test_llm_node_streaming_retries_and_reports_error(self):
        events: list[str] = []

        def stream_collector(chunk: str):
            events.append(chunk)

        state = self._build_state(model_manager=FlakyStreamManager(), llm_stream_callback=stream_collector)
        state["processed_data"].append(
            {
                "source": {"title": "Doc2", "url": "https://example.com/doc2"},
                "summary": "Second document to keep multiple context entries.",
            }
        )

        updates = llm_node(state)

        self.assertIn("provisional_answer", updates)
        self.assertEqual("partial answer", updates["provisional_answer"])
        self.assertIn("errors", updates)  # first streaming failure should be reported
        self.assertTrue(any("generation failed" in err for err in updates["errors"]))
        self.assertEqual("partial answer", "".join(events))

    def test_llm_node_returns_error_without_context(self):
        state = create_initial_state(query="Needs data", language="en")
        updates = llm_node(state)
        self.assertIn("errors", updates)
        self.assertTrue(any("No processed data" in err for err in updates["errors"]))


if __name__ == "__main__":
    unittest.main()

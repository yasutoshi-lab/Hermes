"""Tests for the report node implementation."""

import importlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

report_node_module = importlib.import_module("nodes.report_node")  # noqa: E402
from nodes.report_node import report_node  # noqa: E402
from state.agent_state import create_initial_state  # noqa: E402


class TestReportNode(unittest.TestCase):
    """Unit tests for report node behavior."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.session_dir = Path(self.temp_dir.name) / "session_test"
        self.session_dir.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _state_with_content(self, **overrides):
        state = create_initial_state(
            query="LangGraph roadmap",
            language="en",
            history_path=str(self.session_dir),
        )
        state["provisional_answer"] = "LangGraph enables multi-actor graphs with local state. [S1]"
        state["processed_data"] = [
            {
                "source": {"title": "LangGraph Docs", "url": "https://example.com/langgraph"},
                "summary": "Documentation covering stateful graphs.",
            },
            {
                "source": {"title": "LangChain Blog", "url": "https://example.com/blog"},
                "summary": "Blog post describing practical adoption.",
            },
        ]
        state["search_results"] = [
            {
                "title": "LangGraph Docs",
                "url": "https://example.com/langgraph",
                "summary": "Duplicate entry that should be deduped.",
            },
            {
                "title": "Community Showcase",
                "url": "https://example.com/showcase",
                "summary": "Examples of productions uses.",
            },
        ]
        state["verification_summary"] = {
            "average_confidence": 0.76,
            "needs_additional_search": False,
            "passed": 3,
            "total_claims": 3,
        }
        state["verification_count"] = 1
        state.update(overrides)
        return state

    def test_report_node_generates_markdown_and_pdf_placeholder(self):
        state = self._state_with_content(report_format="both")
        updates = report_node(state)

        self.assertIn("final_report", updates)
        report_text = updates["final_report"]
        self.assertIn("## Sources", report_text)
        self.assertTrue(report_text.startswith("# Research Report"))

        report_path = Path(updates["report_path"])
        self.assertTrue(report_path.exists())
        self.assertIn("LangGraph roadmap", report_path.read_text(encoding="utf-8"))

        metadata = updates.get("report_metadata", {})
        self.assertGreaterEqual(len(metadata.get("sources", [])), 2)
        pdf_path = metadata.get("pdf_path")
        self.assertTrue(pdf_path)
        self.assertTrue(Path(pdf_path).exists())

    def test_report_node_handles_missing_history_path(self):
        state = self._state_with_content(history_path="", report_format="markdown")
        updates = report_node(state)
        self.assertEqual(updates["report_path"], "")
        self.assertNotIn("errors", updates)

    def test_report_node_requires_provisional_answer(self):
        state = create_initial_state(query="No answer", language="en")
        updates = report_node(state)
        self.assertIn("errors", updates)
        self.assertTrue(any("provisional_answer is empty" in err for err in updates["errors"]))


if __name__ == "__main__":
    unittest.main()

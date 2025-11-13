"""Tests for the ProcessingNode implementation."""

import importlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

processing_node_module = importlib.import_module("nodes.processing_node")  # noqa: E402
from nodes.processing_node import processing_node  # noqa: E402
from nodes.processing_node import ContainerProcessorError  # noqa: E402
from state.agent_state import create_initial_state  # noqa: E402


class FakeProcessor:
    """Processor that simply echoes normalized results."""

    def __init__(self):
        self.calls = []

    def process_document(self, document):
        self.calls.append(document)
        return {
            "source": {
                "title": document.get("title", ""),
                "url": document.get("url", ""),
                "language": document.get("language", "en"),
                "content_type": "text/html",
                "retrieved_at": document.get("retrieved_at"),
            },
            "summary": document.get("summary", ""),
            "normalized_content": document.get("content", ""),
            "snippets": [{"order": 1, "text": "snippet"}],
            "key_facts": ["fact"],
            "tables": [],
            "provenance": {"processor": "test", "notes": []},
            "timestamp": "2024-01-01T00:00:00Z",
        }


class FlakyProcessor(FakeProcessor):
    """Processor that raises for the first document then succeeds."""

    def __init__(self):
        super().__init__()
        self.fail_next = True

    def process_document(self, document):
        if self.fail_next:
            self.fail_next = False
            raise ContainerProcessorError("failure")
        return super().process_document(document)


class TestProcessingNode(unittest.TestCase):
    """Test cases for processing_node."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.session_dir = Path(self.temp_dir.name) / "session_test"
        self.session_dir.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_processing_node_generates_processed_data_and_history(self):
        state = create_initial_state(
            query="test",
            language="en",
            history_path=str(self.session_dir),
        )
        state["search_results"] = [
            {
                "title": "Doc 1",
                "url": "https://example.com/doc1",
                "summary": "Summary 1",
                "content": "<html>Doc1</html>",
                "language": "en",
                "retrieved_at": "2024-01-01T00:00:00Z",
            },
            {
                "title": "Doc 1 duplicate",
                "url": "https://example.com/doc1",
                "summary": "Summary 1 dup",
                "content": "Duplicate content",
                "language": "en",
                "retrieved_at": "2024-01-01T00:00:05Z",
            },
        ]

        fake_processor = FakeProcessor()
        with patch.object(processing_node_module, "ContainerProcessor", return_value=fake_processor):
            updates = processing_node(state)

        self.assertIn("processed_data", updates)
        processed = updates["processed_data"]
        self.assertEqual(len(processed), 1)
        self.assertEqual(processed[0]["source"]["url"], "https://example.com/doc1")

        history_file = self.session_dir / "processed_data.md"
        self.assertTrue(history_file.exists())
        self.assertIn("Doc 1", history_file.read_text(encoding="utf-8"))

    def test_processing_node_continues_after_processor_failure(self):
        state = create_initial_state(
            query="test",
            language="en",
            history_path=str(self.session_dir),
        )
        state["search_results"] = [
            {
                "title": "Doc A",
                "url": "https://example.com/a",
                "summary": "Summary A",
                "content": "A content",
                "language": "en",
                "retrieved_at": "2024-01-01T00:00:00Z",
            },
            {
                "title": "Doc B",
                "url": "https://example.com/b",
                "summary": "Summary B",
                "content": "B content",
                "language": "en",
                "retrieved_at": "2024-01-01T00:00:01Z",
            },
        ]

        fake_processor = FlakyProcessor()
        with patch.object(processing_node_module, "ContainerProcessor", return_value=fake_processor):
            updates = processing_node(state)

        self.assertEqual(len(updates["processed_data"]), 1)
        self.assertIn("errors", updates)
        self.assertTrue(any("Failed to process" in err for err in updates["errors"]))

    def test_processing_node_requires_search_results(self):
        state = create_initial_state(history_path=str(self.session_dir))

        updates = processing_node(state)

        self.assertIn("errors", updates)
        self.assertTrue(any("No search results" in err for err in updates["errors"]))


if __name__ == "__main__":
    unittest.main()

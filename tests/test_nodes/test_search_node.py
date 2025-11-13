"""Tests for the SearchNode implementation."""

import importlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

search_node_module = importlib.import_module("nodes.search_node")  # noqa: E402
from nodes.search_node import search_node  # noqa: E402
from modules.mcp_client import MCPClientError  # noqa: E402
from state.agent_state import create_initial_state  # noqa: E402


class FakeSearchClient:
    """Fake MCP client for testing search node logic."""

    def __init__(self):
        self.fetch_calls = []

    def full_search(self, query, language=None, limit=None):
        return [
            {
                "title": "Primary",
                "url": "https://example.com/primary",
                "description": "Primary desc",
                "content": "",
                "language": language or "en",
                "retrieved_at": "2024-01-01T00:00:00Z",
            }
        ]

    def summary_search(self, query, language=None, limit=None):
        return [
            {
                "title": "Summary",
                "url": "https://example.com/summary",
                "description": "Summary desc",
                "content": "Summary content",
                "language": language or "en",
                "retrieved_at": "2024-01-01T00:00:01Z",
            }
        ]

    def multi_search(self, queries, language=None, per_query_limit=None):
        return []

    def fetch_page_content(self, url, language=None):
        self.fetch_calls.append(url)
        return {
            "title": "Fetched",
            "url": url,
            "description": "",
            "content": "Fetched content body",
            "language": language or "en",
            "retrieved_at": "2024-01-01T00:00:02Z",
        }


class TestSearchNode(unittest.TestCase):
    """Test cases for search_node."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.session_dir = Path(self.temp_dir.name) / "session_test"
        self.session_dir.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_search_node_populates_results_and_history(self):
        state = create_initial_state(
            query="LangGraph 事例",
            language="ja",
            history_path=str(self.session_dir),
        )
        fake_client = FakeSearchClient()

        with patch.object(search_node_module, "WebSearchClient", return_value=fake_client):
            updates = search_node(state)

        self.assertIn("search_results", updates)
        results = updates["search_results"]
        self.assertEqual(len(results), 2)
        self.assertTrue(any(result["url"] == "https://example.com/primary" for result in results))
        self.assertIn("Fetched content body", results[0]["content"])

        history_file = self.session_dir / "search_results.md"
        self.assertTrue(history_file.exists())
        self.assertIn("Primary", history_file.read_text(encoding="utf-8"))

    def test_search_node_handles_client_failure(self):
        state = create_initial_state(query="fail query", history_path=str(self.session_dir))

        class FailingClient:
            def full_search(self, *args, **kwargs):
                raise MCPClientError("boom")

            def summary_search(self, *args, **kwargs):
                raise MCPClientError("boom")

            def multi_search(self, *args, **kwargs):
                return []

            def fetch_page_content(self, *args, **kwargs):
                return {}

        with patch.object(search_node_module, "WebSearchClient", return_value=FailingClient()):
            updates = search_node(state)

        self.assertIn("errors", updates)
        self.assertTrue(any("No search results" in err for err in updates["errors"]))


if __name__ == "__main__":
    unittest.main()

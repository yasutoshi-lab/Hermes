"""Unit tests for the WebSearchClient MCP wrapper."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from modules.mcp_client import WebSearchClient  # noqa: E402


class FakeResponse:
    """Simple stand-in for requests.Response."""

    def __init__(self, status_code: int, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakeSession:
    """Captures POST requests for assertions."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.requests = []

    def post(self, url, json, headers=None, timeout=None):
        self.requests.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
        response = self._responses.pop(0)
        return response


class TestWebSearchClient(unittest.TestCase):
    """Test suite for WebSearchClient."""

    def test_full_search_normalizes_results(self):
        responses = [
            FakeResponse(
                200,
                {
                    "results": [
                        {"title": "Result 1", "url": "https://example.com/1", "description": "Desc 1"},
                        {"title": "Result 2", "url": "https://example.com/2", "content": "<html>Body</html>"},
                    ]
                },
            )
        ]
        session = FakeSession(responses)
        client = WebSearchClient(base_url="http://fake-mcp", session=session, timeout=1, max_retries=1)

        results = client.full_search("テスト クエリ", language="ja", limit=2)

        self.assertEqual(len(results), 2)
        shaped_query = session.requests[0]["json"]["query"]
        self.assertIn("最新情報", shaped_query)
        self.assertEqual(results[0]["url"], "https://example.com/1")
        self.assertEqual(results[0]["language"], "ja")
        self.assertIn("retrieved_at", results[0])

    def test_full_search_retries_on_rate_limit(self):
        responses = [
            FakeResponse(429, {"error": "rate limited"}),
            FakeResponse(200, {"results": [{"title": "Recovered", "url": "https://example.com"}]}),
        ]
        session = FakeSession(responses)
        client = WebSearchClient(base_url="http://fake-mcp", session=session, timeout=1, max_retries=2)

        with patch("modules.mcp_client.time.sleep", return_value=None):
            results = client.full_search("test query", language="en", limit=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(len(session.requests), 2)

    def test_multi_search_deduplicates_urls(self):
        responses = [
            FakeResponse(200, {"results": [{"title": "A", "url": "https://example.com/a"}]}),
            FakeResponse(
                200,
                {
                    "results": [
                        {"title": "A (duplicate)", "url": "https://example.com/a"},
                        {"title": "B", "url": "https://example.com/b"},
                    ]
                },
            ),
        ]
        session = FakeSession(responses)
        client = WebSearchClient(base_url="http://fake-mcp", session=session, timeout=1, max_retries=1)

        results = client.multi_search(["first query", "second query"], language="en", per_query_limit=2)

        self.assertEqual(len(results), 2)
        urls = [result["url"] for result in results]
        self.assertListEqual(urls, ["https://example.com/a", "https://example.com/b"])


if __name__ == "__main__":
    unittest.main()

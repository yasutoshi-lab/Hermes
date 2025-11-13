"""
Unit tests for HistoryManager module.
"""

import json
import tempfile
import unittest
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from modules.history_manager import (
    HistoryManager,
    HistoryManagerError,
    SessionNotFoundError
)


class TestHistoryManager(unittest.TestCase):
    """Test cases for HistoryManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test sessions
        self.temp_dir = tempfile.mkdtemp()
        self.history_manager = HistoryManager(base_path=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization_default_path(self):
        """Test HistoryManager initialization with default path."""
        hm = HistoryManager()
        self.assertEqual(hm.base_path, Path.cwd() / "sessions")

    def test_initialization_custom_path(self):
        """Test HistoryManager initialization with custom path."""
        custom_path = Path(self.temp_dir) / "custom_sessions"
        hm = HistoryManager(base_path=custom_path)
        self.assertEqual(hm.base_path, custom_path)
        self.assertTrue(hm.base_path.exists())

    def test_create_session(self):
        """Test session creation."""
        session_id = self.history_manager.create_session()

        # Check session ID format
        self.assertTrue(session_id.startswith("session_"))

        # Check directory was created
        session_path = Path(self.temp_dir) / session_id
        self.assertTrue(session_path.exists())
        self.assertTrue(session_path.is_dir())

    def test_create_multiple_sessions(self):
        """Test creating multiple sessions."""
        session_ids = [self.history_manager.create_session() for _ in range(3)]

        # All should be unique
        self.assertEqual(len(session_ids), len(set(session_ids)))

        # All should exist
        for session_id in session_ids:
            session_path = Path(self.temp_dir) / session_id
            self.assertTrue(session_path.exists())

    def test_save_input(self):
        """Test saving user input."""
        session_id = self.history_manager.create_session()
        prompt = "What is the capital of France?"
        config = {
            "language": "en",
            "model_name": "gpt-oss:20b"
        }

        self.history_manager.save_input(session_id, prompt, config)

        # Check file was created
        input_file = Path(self.temp_dir) / session_id / "input.md"
        self.assertTrue(input_file.exists())

        # Check content
        content = input_file.read_text(encoding='utf-8')
        self.assertIn(prompt, content)
        self.assertIn("gpt-oss:20b", content)
        self.assertIn("en", content)

    def test_save_input_with_japanese(self):
        """Test saving input with Japanese characters."""
        session_id = self.history_manager.create_session()
        prompt = "日本の首都は何ですか?"
        config = {
            "language": "ja",
            "model_name": "gpt-oss:20b"
        }

        self.history_manager.save_input(session_id, prompt, config)

        # Check file was created and content is correct
        input_file = Path(self.temp_dir) / session_id / "input.md"
        content = input_file.read_text(encoding='utf-8')
        self.assertIn(prompt, content)
        self.assertIn("ja", content)

    def test_save_input_invalid_session(self):
        """Test saving input to non-existent session."""
        with self.assertRaises(SessionNotFoundError):
            self.history_manager.save_input("invalid_session", "test", {})

    def test_save_search_results(self):
        """Test saving search results."""
        session_id = self.history_manager.create_session()
        results = [
            {
                "title": "Paris - Wikipedia",
                "url": "https://en.wikipedia.org/wiki/Paris",
                "description": "Paris is the capital of France",
                "content": "Paris is the capital and most populous city..."
            },
            {
                "title": "France Capital",
                "url": "https://example.com/france",
                "description": "Information about France's capital"
            }
        ]

        self.history_manager.save_search_results(session_id, results)

        # Check file was created
        search_file = Path(self.temp_dir) / session_id / "search_results.md"
        self.assertTrue(search_file.exists())

        # Check content
        content = search_file.read_text(encoding='utf-8')
        self.assertIn("Paris - Wikipedia", content)
        self.assertIn("https://en.wikipedia.org/wiki/Paris", content)
        self.assertIn("**Total Results**: 2", content)

    def test_save_search_results_empty_list(self):
        """Test saving empty search results."""
        session_id = self.history_manager.create_session()
        results = []

        self.history_manager.save_search_results(session_id, results)

        search_file = Path(self.temp_dir) / session_id / "search_results.md"
        self.assertTrue(search_file.exists())
        content = search_file.read_text(encoding='utf-8')
        self.assertIn("**Total Results**: 0", content)

    def test_save_processed_data(self):
        """Test saving processed data."""
        session_id = self.history_manager.create_session()
        data = [
            {
                "step": "Parse HTML",
                "timestamp": "2024-01-01T12:00:00",
                "input": "<html>...</html>",
                "output": "Parsed text content",
                "logs": "Processing completed successfully"
            },
            {
                "step": "Extract Entities",
                "timestamp": "2024-01-01T12:01:00",
                "input": "Parsed text content",
                "output": "Entity list: [...]"
            }
        ]

        self.history_manager.save_processed_data(session_id, data)

        # Check file was created
        processed_file = Path(self.temp_dir) / session_id / "processed_data.md"
        self.assertTrue(processed_file.exists())

        # Check content
        content = processed_file.read_text(encoding='utf-8')
        self.assertIn("Parse HTML", content)
        self.assertIn("Extract Entities", content)
        self.assertIn("**Total Processing Steps**: 2", content)

    def test_save_report(self):
        """Test saving final report."""
        session_id = self.history_manager.create_session()
        report = """# Research Report

## Introduction
This is a test report.

## Findings
- Finding 1
- Finding 2

## Conclusion
Test conclusion.
"""

        self.history_manager.save_report(session_id, report)

        # Check file was created
        report_file = Path(self.temp_dir) / session_id / "report.md"
        self.assertTrue(report_file.exists())

        # Check content
        content = report_file.read_text(encoding='utf-8')
        self.assertIn("Research Report", content)
        self.assertIn("Finding 1", content)

    def test_save_report_with_pdf(self):
        """Test saving report with PDF generation flag."""
        session_id = self.history_manager.create_session()
        report = "# Test Report"

        self.history_manager.save_report(session_id, report, generate_pdf=True)

        # Check markdown file
        report_file = Path(self.temp_dir) / session_id / "report.md"
        self.assertTrue(report_file.exists())

        # Check PDF placeholder was created
        pdf_file = Path(self.temp_dir) / session_id / "report.pdf"
        self.assertTrue(pdf_file.exists())

    def test_save_state(self):
        """Test saving session state."""
        session_id = self.history_manager.create_session()
        state = {
            "messages": [{"role": "user", "content": "Hello"}],
            "query": "test query",
            "language": "en",
            "model_name": "gpt-oss:20b"
        }

        self.history_manager.save_state(session_id, state)

        # Check file was created
        state_file = Path(self.temp_dir) / session_id / "state.json"
        self.assertTrue(state_file.exists())

        # Check content
        content = state_file.read_text(encoding='utf-8')
        state_data = json.loads(content)
        self.assertIn("state", state_data)
        self.assertEqual(state_data["state"]["query"], "test query")
        self.assertIn("saved_at", state_data)

    def test_load_session(self):
        """Test loading a complete session."""
        # Create session and save all data types
        session_id = self.history_manager.create_session()

        prompt = "Test prompt"
        config = {"language": "en"}
        self.history_manager.save_input(session_id, prompt, config)

        results = [{"title": "Test", "url": "http://test.com"}]
        self.history_manager.save_search_results(session_id, results)

        data = [{"step": "Test step", "input": "input", "output": "output"}]
        self.history_manager.save_processed_data(session_id, data)

        report = "# Test Report"
        self.history_manager.save_report(session_id, report)

        state = {"test": "state"}
        self.history_manager.save_state(session_id, state)

        # Load session
        loaded = self.history_manager.load_session(session_id)

        # Verify all data was loaded
        self.assertIn("input", loaded)
        self.assertIn("search_results", loaded)
        self.assertIn("processed_data", loaded)
        self.assertIn("report", loaded)
        self.assertIn("state", loaded)

        self.assertIn(prompt, loaded["input"])
        self.assertIn("Test", loaded["search_results"])
        self.assertIn("Test step", loaded["processed_data"])
        self.assertIn("Test Report", loaded["report"])
        self.assertEqual(loaded["state"]["state"]["test"], "state")

    def test_load_session_partial_data(self):
        """Test loading session with only some files present."""
        session_id = self.history_manager.create_session()
        self.history_manager.save_input(session_id, "test", {})

        loaded = self.history_manager.load_session(session_id)

        self.assertIn("input", loaded)
        self.assertNotIn("search_results", loaded)
        self.assertNotIn("report", loaded)

    def test_load_session_not_found(self):
        """Test loading non-existent session."""
        with self.assertRaises(SessionNotFoundError):
            self.history_manager.load_session("invalid_session")

    def test_list_sessions(self):
        """Test listing all sessions."""
        # Create multiple sessions
        session_ids = [self.history_manager.create_session() for _ in range(3)]

        # List sessions
        listed = self.history_manager.list_sessions()

        # All created sessions should be listed
        self.assertEqual(len(listed), 3)
        for session_id in session_ids:
            self.assertIn(session_id, listed)

    def test_list_sessions_empty(self):
        """Test listing sessions when none exist."""
        sessions = self.history_manager.list_sessions()
        self.assertEqual(len(sessions), 0)

    def test_list_sessions_sorted(self):
        """Test that sessions are listed newest first."""
        import time

        session_ids = []
        for _ in range(3):
            sid = self.history_manager.create_session()
            session_ids.append(sid)
            time.sleep(0.01)  # Small delay to ensure different timestamps

        listed = self.history_manager.list_sessions()

        # Should be in reverse order (newest first)
        self.assertEqual(listed[0], session_ids[2])
        self.assertEqual(listed[2], session_ids[0])

    def test_cleanup_old_sessions(self):
        """Test cleaning up old sessions."""
        import time

        # Create 5 sessions with small delays to ensure different timestamps
        session_ids = []
        for _ in range(5):
            sid = self.history_manager.create_session()
            session_ids.append(sid)
            time.sleep(0.01)

        # Keep only last 2
        deleted = self.history_manager.cleanup_old_sessions(keep_last_n=2)

        self.assertEqual(deleted, 3)

        # Check remaining sessions
        remaining = self.history_manager.list_sessions()
        self.assertEqual(len(remaining), 2)

        # Most recent 2 should remain
        self.assertIn(session_ids[3], remaining)
        self.assertIn(session_ids[4], remaining)

    def test_cleanup_old_sessions_invalid_param(self):
        """Test cleanup with invalid parameter."""
        with self.assertRaises(ValueError):
            self.history_manager.cleanup_old_sessions(keep_last_n=0)

    def test_cleanup_when_fewer_sessions_than_keep_n(self):
        """Test cleanup when there are fewer sessions than keep_last_n."""
        # Create 2 sessions
        self.history_manager.create_session()
        self.history_manager.create_session()

        # Try to keep 5
        deleted = self.history_manager.cleanup_old_sessions(keep_last_n=5)

        self.assertEqual(deleted, 0)
        self.assertEqual(len(self.history_manager.list_sessions()), 2)

    def test_delete_session(self):
        """Test deleting a specific session."""
        session_id = self.history_manager.create_session()
        self.history_manager.save_input(session_id, "test", {})

        # Delete session
        self.history_manager.delete_session(session_id)

        # Session should not exist
        with self.assertRaises(SessionNotFoundError):
            self.history_manager.load_session(session_id)

        # Should not be in list
        sessions = self.history_manager.list_sessions()
        self.assertNotIn(session_id, sessions)

    def test_delete_session_not_found(self):
        """Test deleting non-existent session."""
        with self.assertRaises(SessionNotFoundError):
            self.history_manager.delete_session("invalid_session")


class TestHistoryManagerEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.history_manager = HistoryManager(base_path=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_very_long_content(self):
        """Test handling very long content."""
        session_id = self.history_manager.create_session()
        long_content = "x" * 10000
        results = [{"title": "Test", "url": "http://test.com", "content": long_content}]

        # Should not raise exception
        self.history_manager.save_search_results(session_id, results)

        search_file = Path(self.temp_dir) / session_id / "search_results.md"
        self.assertTrue(search_file.exists())

    def test_special_characters_in_content(self):
        """Test handling special characters."""
        session_id = self.history_manager.create_session()
        prompt = "Test with special chars: <>&\"'"
        config = {"test": "value"}

        self.history_manager.save_input(session_id, prompt, config)

        input_file = Path(self.temp_dir) / session_id / "input.md"
        content = input_file.read_text(encoding='utf-8')
        self.assertIn(prompt, content)

    def test_unicode_characters(self):
        """Test handling various unicode characters."""
        session_id = self.history_manager.create_session()
        prompt = "日本語 中文 한글 Emoji: 🚀🌟"
        config = {"language": "multi"}

        self.history_manager.save_input(session_id, prompt, config)

        input_file = Path(self.temp_dir) / session_id / "input.md"
        content = input_file.read_text(encoding='utf-8')
        self.assertIn("日本語", content)
        self.assertIn("🚀", content)


if __name__ == '__main__':
    unittest.main()

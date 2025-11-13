"""
History Manager Module

This module provides functionality to save and retrieve session data including
prompts, search results, processing logs, and final reports.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class HistoryManagerError(Exception):
    """Base exception for HistoryManager errors."""
    pass


class SessionNotFoundError(HistoryManagerError):
    """Raised when a session ID is not found."""
    pass


class HistoryManager:
    """
    Manages session history for the research assistant agent.

    Each session is stored in a timestamped directory with the following structure:
    sessions/session_<timestamp>/
    ├── input.md           # User prompt and settings
    ├── search_results.md  # Web search results
    ├── processed_data.md  # Container processing results
    ├── report.md          # Final report
    ├── report.pdf         # PDF version (if generated)
    └── state.json         # Complete session state
    """

    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize the HistoryManager.

        Args:
            base_path: Base directory for storing sessions. Defaults to './sessions'
        """
        if base_path is None:
            self.base_path = Path.cwd() / "sessions"
        else:
            self.base_path = Path(base_path)

        # Ensure base directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_session(self) -> str:
        """
        Create a new session directory with a unique timestamp-based ID.

        Returns:
            str: Session ID in format 'session_YYYYMMDD_HHMMSS'

        Raises:
            HistoryManagerError: If session directory cannot be created
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"session_{timestamp}"
        session_path = self.base_path / session_id

        try:
            session_path.mkdir(parents=True, exist_ok=False)
            return session_id
        except FileExistsError:
            # In case of collision, add microseconds
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            session_id = f"session_{timestamp}"
            session_path = self.base_path / session_id
            session_path.mkdir(parents=True, exist_ok=False)
            return session_id
        except Exception as e:
            raise HistoryManagerError(f"Failed to create session directory: {e}")

    def _get_session_path(self, session_id: str) -> Path:
        """
        Get the path to a session directory.

        Args:
            session_id: The session ID

        Returns:
            Path: Path to the session directory

        Raises:
            SessionNotFoundError: If session does not exist
        """
        session_path = self.base_path / session_id
        if not session_path.exists():
            raise SessionNotFoundError(f"Session '{session_id}' not found")
        return session_path

    def save_input(self, session_id: str, prompt: str, config: Dict[str, Any]) -> None:
        """
        Save user input and configuration to input.md.

        Args:
            session_id: The session ID
            prompt: User's input prompt
            config: Configuration dictionary (language, model, etc.)

        Raises:
            SessionNotFoundError: If session does not exist
            HistoryManagerError: If file cannot be written
        """
        session_path = self._get_session_path(session_id)
        input_file = session_path / "input.md"

        try:
            timestamp = datetime.now().isoformat()
            content = f"""# Session Input

**Session ID**: {session_id}
**Timestamp**: {timestamp}
**Language**: {config.get('language', 'N/A')}
**Model**: {config.get('model_name', 'N/A')}

## Configuration

```json
{json.dumps(config, indent=2, ensure_ascii=False)}
```

## User Prompt

{prompt}
"""
            input_file.write_text(content, encoding='utf-8')
        except Exception as e:
            raise HistoryManagerError(f"Failed to save input: {e}")

    def save_search_results(self, session_id: str, results: List[Dict[str, Any]]) -> None:
        """
        Save web search results to search_results.md.

        Args:
            session_id: The session ID
            results: List of search result dictionaries with keys:
                    - title: Page title
                    - url: Page URL
                    - description: Brief description
                    - content: Full page content (optional)

        Raises:
            SessionNotFoundError: If session does not exist
            HistoryManagerError: If file cannot be written
        """
        session_path = self._get_session_path(session_id)
        search_file = session_path / "search_results.md"

        try:
            timestamp = datetime.now().isoformat()
            content = f"""# Search Results

**Session ID**: {session_id}
**Timestamp**: {timestamp}
**Total Results**: {len(results)}

---

"""
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                url = result.get('url', 'No URL')
                description = result.get('description', 'No description')
                page_content = result.get('content', '')

                content += f"""## Result {i}: {title}

**URL**: {url}

**Description**: {description}

"""
                if page_content:
                    # Truncate very long content for readability
                    if len(page_content) > 5000:
                        page_content = page_content[:5000] + "\n\n...(truncated)"
                    content += f"""**Content Preview**:

```
{page_content}
```

"""
                content += "---\n\n"

            search_file.write_text(content, encoding='utf-8')
        except Exception as e:
            raise HistoryManagerError(f"Failed to save search results: {e}")

    def save_processed_data(self, session_id: str, data: List[Dict[str, Any]]) -> None:
        """
        Save processed data and logs to processed_data.md.

        Args:
            session_id: The session ID
            data: List of processed data dictionaries with keys:
                 - step: Processing step name
                 - input: Input data
                 - output: Output data
                 - logs: Processing logs (optional)
                 - timestamp: Processing timestamp (optional)

        Raises:
            SessionNotFoundError: If session does not exist
            HistoryManagerError: If file cannot be written
        """
        session_path = self._get_session_path(session_id)
        processed_file = session_path / "processed_data.md"

        try:
            timestamp = datetime.now().isoformat()
            content = f"""# Processed Data

**Session ID**: {session_id}
**Timestamp**: {timestamp}
**Total Processing Steps**: {len(data)}

---

"""
            for i, item in enumerate(data, 1):
                step_name = item.get('step', f'Step {i}')
                step_timestamp = item.get('timestamp', 'N/A')
                input_data = item.get('input', 'N/A')
                output_data = item.get('output', 'N/A')
                logs = item.get('logs', '')

                content += f"""## {step_name}

**Timestamp**: {step_timestamp}

### Input

```
{input_data}
```

### Output

```
{output_data}
```

"""
                if logs:
                    content += f"""### Logs

```
{logs}
```

"""
                content += "---\n\n"

            processed_file.write_text(content, encoding='utf-8')
        except Exception as e:
            raise HistoryManagerError(f"Failed to save processed data: {e}")

    def save_report(self, session_id: str, report: str, generate_pdf: bool = False) -> None:
        """
        Save final report to report.md and optionally generate PDF.

        Args:
            session_id: The session ID
            report: Final report content in Markdown format
            generate_pdf: Whether to generate PDF version (default: False)

        Raises:
            SessionNotFoundError: If session does not exist
            HistoryManagerError: If file cannot be written

        Note:
            PDF generation requires additional dependencies (e.g., markdown2, pdfkit)
            and is not implemented in this version.
        """
        session_path = self._get_session_path(session_id)
        report_file = session_path / "report.md"

        try:
            timestamp = datetime.now().isoformat()
            content = f"""# Final Report

**Session ID**: {session_id}
**Generated**: {timestamp}

---

{report}
"""
            report_file.write_text(content, encoding='utf-8')

            if generate_pdf:
                # PDF generation would be implemented here
                # For now, we just create a placeholder
                pdf_file = session_path / "report.pdf"
                pdf_file.write_text(
                    "PDF generation not yet implemented. Please use report.md",
                    encoding='utf-8'
                )
        except Exception as e:
            raise HistoryManagerError(f"Failed to save report: {e}")

    def save_state(self, session_id: str, state: Dict[str, Any]) -> None:
        """
        Save complete session state to state.json.

        Args:
            session_id: The session ID
            state: Complete state dictionary

        Raises:
            SessionNotFoundError: If session does not exist
            HistoryManagerError: If file cannot be written
        """
        session_path = self._get_session_path(session_id)
        state_file = session_path / "state.json"

        try:
            # Add metadata
            state_with_metadata = {
                "session_id": session_id,
                "saved_at": datetime.now().isoformat(),
                "state": state
            }

            state_file.write_text(
                json.dumps(state_with_metadata, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            raise HistoryManagerError(f"Failed to save state: {e}")

    def load_session(self, session_id: str) -> Dict[str, Any]:
        """
        Load a previous session's data.

        Args:
            session_id: The session ID to load

        Returns:
            Dict containing:
                - input: Content of input.md if exists
                - search_results: Content of search_results.md if exists
                - processed_data: Content of processed_data.md if exists
                - report: Content of report.md if exists
                - state: Parsed state.json if exists

        Raises:
            SessionNotFoundError: If session does not exist
            HistoryManagerError: If files cannot be read
        """
        session_path = self._get_session_path(session_id)

        try:
            session_data = {
                "session_id": session_id,
                "session_path": str(session_path)
            }

            # Load input.md
            input_file = session_path / "input.md"
            if input_file.exists():
                session_data["input"] = input_file.read_text(encoding='utf-8')

            # Load search_results.md
            search_file = session_path / "search_results.md"
            if search_file.exists():
                session_data["search_results"] = search_file.read_text(encoding='utf-8')

            # Load processed_data.md
            processed_file = session_path / "processed_data.md"
            if processed_file.exists():
                session_data["processed_data"] = processed_file.read_text(encoding='utf-8')

            # Load report.md
            report_file = session_path / "report.md"
            if report_file.exists():
                session_data["report"] = report_file.read_text(encoding='utf-8')

            # Load state.json
            state_file = session_path / "state.json"
            if state_file.exists():
                state_content = state_file.read_text(encoding='utf-8')
                session_data["state"] = json.loads(state_content)

            return session_data
        except json.JSONDecodeError as e:
            raise HistoryManagerError(f"Failed to parse state.json: {e}")
        except Exception as e:
            raise HistoryManagerError(f"Failed to load session: {e}")

    def list_sessions(self) -> List[str]:
        """
        List all session IDs in chronological order (newest first).

        Returns:
            List of session IDs
        """
        try:
            sessions = [
                d.name for d in self.base_path.iterdir()
                if d.is_dir() and d.name.startswith('session_')
            ]
            # Sort by modification time, newest first
            sessions.sort(key=lambda s: (self.base_path / s).stat().st_mtime, reverse=True)
            return sessions
        except Exception as e:
            raise HistoryManagerError(f"Failed to list sessions: {e}")

    def cleanup_old_sessions(self, keep_last_n: int = 10) -> int:
        """
        Delete old sessions, keeping only the last N sessions.

        Args:
            keep_last_n: Number of recent sessions to keep (default: 10)

        Returns:
            int: Number of sessions deleted

        Raises:
            HistoryManagerError: If cleanup fails
        """
        if keep_last_n < 1:
            raise ValueError("keep_last_n must be at least 1")

        try:
            sessions = self.list_sessions()
            sessions_to_delete = sessions[keep_last_n:]

            deleted_count = 0
            for session_id in sessions_to_delete:
                session_path = self.base_path / session_id
                shutil.rmtree(session_path)
                deleted_count += 1

            return deleted_count
        except Exception as e:
            raise HistoryManagerError(f"Failed to cleanup sessions: {e}")

    def delete_session(self, session_id: str) -> None:
        """
        Delete a specific session.

        Args:
            session_id: The session ID to delete

        Raises:
            SessionNotFoundError: If session does not exist
            HistoryManagerError: If deletion fails
        """
        session_path = self._get_session_path(session_id)

        try:
            shutil.rmtree(session_path)
        except Exception as e:
            raise HistoryManagerError(f"Failed to delete session: {e}")

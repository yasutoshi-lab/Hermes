"""Log file operations for Hermes.

This module handles log file operations including writing formatted log entries,
tailing log files, and streaming logs in real-time.
"""

from pathlib import Path
from datetime import datetime
from typing import Iterator, Optional, List, Any
import time

from .file_paths import FilePaths


class LogRepository:
    """Handles log file operations.

    Provides methods for writing formatted log entries, reading recent logs,
    and streaming log files in real-time.
    """

    def __init__(self, file_paths: FilePaths):
        """Initialize log repository.

        Args:
            file_paths: FilePaths instance for path management
        """
        self.file_paths = file_paths

    def get_log_file(self, date: Optional[datetime] = None, debug: bool = False) -> Path:
        """Get log file path for specific date.

        Args:
            date: Date for log file. If None, uses current date.
            debug: If True, returns debug log path instead of regular log

        Returns:
            Path to log file (format: hermes-YYYYMMDD.log)
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y%m%d")
        filename = f"hermes-{date_str}.log"

        if debug:
            log_dir = self.file_paths.debug_log_dir
        else:
            log_dir = self.file_paths.log_dir

        return log_dir / filename

    def write_log(
        self,
        level: str,
        component: str,
        message: str,
        task_id: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Write formatted log entry.

        Format: ISO8601時刻 [レベル] [コンポーネント] メッセージ key=value...

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            component: Component name (RUN, BROWSER, OLLAMA, etc.)
            message: Log message
            task_id: Optional task identifier
            **kwargs: Additional key-value pairs to log

        Example:
            write_log("INFO", "RUN", "Starting task", task_id="2025-0001", phase="query_generation")
            # Output: 2025-11-14T10:31:02+09:00 [INFO] [RUN] Starting task task_id=2025-0001 phase=query_generation
        """
        log_file = self.get_log_file()
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Build timestamp in ISO8601 format with timezone
        timestamp = datetime.now().astimezone().isoformat()

        # Build key=value pairs
        kv_pairs = []
        if task_id:
            kv_pairs.append(f"task_id={task_id}")

        for key, value in kwargs.items():
            kv_pairs.append(f"{key}={value}")

        # Build complete log line
        kv_str = " ".join(kv_pairs)
        if kv_str:
            log_line = f"{timestamp} [{level}] [{component}] {message} {kv_str}\n"
        else:
            log_line = f"{timestamp} [{level}] [{component}] {message}\n"

        # Append to log file
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)

    def tail(self, lines: int = 10, debug: bool = False) -> List[str]:
        """Get last N lines from log file.

        Args:
            lines: Number of lines to return (default: 10)
            debug: If True, reads from debug log instead of regular log

        Returns:
            List of log lines (may be fewer than requested if file is smaller)
        """
        log_file = self.get_log_file(debug=debug)

        if not log_file.exists():
            return []

        # Read all lines and return last N
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()

        return all_lines[-lines:]

    def stream(self, debug: bool = False) -> Iterator[str]:
        """Stream log file in real-time.

        This is a generator that yields new log lines as they are written.
        It follows the file similar to 'tail -f' behavior.

        Args:
            debug: If True, streams debug log instead of regular log

        Yields:
            New log lines as they appear

        Example:
            for line in log_repo.stream():
                print(line, end='')
        """
        log_file = self.get_log_file(debug=debug)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not log_file.exists():
            log_file.touch()

        with open(log_file, 'r', encoding='utf-8') as f:
            # First, yield existing content
            for line in f:
                yield line

            # Then, follow the file for new content
            while True:
                line = f.readline()
                if line:
                    yield line
                else:
                    # No new content, wait a bit
                    time.sleep(0.1)

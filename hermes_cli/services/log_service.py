"""Log service for Hermes.

This module provides log viewing and streaming operations,
including tail and real-time streaming functionality.
"""

from typing import Iterator, Optional, List
from datetime import datetime
from pathlib import Path
import logging

from hermes_cli.persistence.file_paths import FilePaths
from hermes_cli.persistence.log_repository import LogRepository


class LogService:
    """Service for viewing and streaming logs."""

    def __init__(self, file_paths: Optional[FilePaths] = None):
        """
        Initialize log service.

        Args:
            file_paths: File path manager (uses default if not provided)
        """
        self.file_paths = file_paths or FilePaths()
        self.repository = LogRepository(self.file_paths)
        self.logger = logging.getLogger(__name__)

    def tail(self, lines: int = 50, debug: bool = False) -> List[str]:
        """
        Get last N lines from log file.

        Args:
            lines: Number of lines to retrieve
            debug: Use debug log instead of regular log

        Returns:
            List of log lines
        """
        log_lines = self.repository.tail(lines=lines, debug=debug)
        self.logger.info(f"Retrieved {len(log_lines)} log lines")
        return log_lines

    def stream(self, debug: bool = False) -> Iterator[str]:
        """
        Stream log file in real-time (like tail -f).

        Args:
            debug: Use debug log instead of regular log

        Yields:
            Log lines as they are written
        """
        self.logger.info(f"Starting log stream (debug={debug})")
        return self.repository.stream(debug=debug)

    def get_log_file_path(self, date: Optional[datetime] = None, debug: bool = False) -> Path:
        """
        Get path to log file for specific date.

        Args:
            date: Date for log file (uses today if not specified)
            debug: Return debug log path instead

        Returns:
            Path to log file
        """
        return self.repository.get_log_file(date=date, debug=debug)

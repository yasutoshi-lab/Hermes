"""Debug service for Hermes.

This module provides debug log viewing and filtering operations,
allowing users to view logs with level filtering.
"""

from typing import Iterator, List, Optional, Literal
import logging

from hermes_cli.services.log_service import LogService


LogLevel = Literal["info", "warning", "error", "all"]


class DebugService:
    """Service for viewing debug and system logs with filtering."""

    def __init__(self, log_service: Optional[LogService] = None):
        """
        Initialize debug service.

        Args:
            log_service: Log service instance (creates new if not provided)
        """
        self.log_service = log_service or LogService()
        self.logger = logging.getLogger(__name__)

    def tail(
        self,
        lines: int = 50,
        level: LogLevel = "all",
        include_debug: bool = True
    ) -> List[str]:
        """
        Get last N lines from logs with level filtering.

        Args:
            lines: Number of lines to retrieve
            level: Filter by log level (info, warning, error, all)
            include_debug: Include debug logs in addition to regular logs

        Returns:
            Filtered log lines
        """
        # Get regular logs
        regular_logs = self.log_service.tail(lines=lines, debug=False)

        # Get debug logs if requested
        if include_debug:
            debug_logs = self.log_service.tail(lines=lines, debug=True)
            # Merge and sort by timestamp
            all_logs = self._merge_logs(regular_logs, debug_logs)
        else:
            all_logs = regular_logs

        # Filter by level
        if level != "all":
            all_logs = self._filter_by_level(all_logs, level)

        self.logger.info(f"Retrieved {len(all_logs)} filtered log lines")
        return all_logs[-lines:]  # Return last N after filtering

    def stream(
        self,
        level: LogLevel = "all",
        include_debug: bool = True
    ) -> Iterator[str]:
        """
        Stream logs in real-time with level filtering.

        Args:
            level: Filter by log level
            include_debug: Include debug logs

        Yields:
            Filtered log lines as they are written
        """
        # For simplicity, just stream regular logs
        # In production, would need to monitor both files
        for line in self.log_service.stream(debug=include_debug):
            if level == "all" or self._matches_level(line, level):
                yield line

    def _merge_logs(self, logs1: List[str], logs2: List[str]) -> List[str]:
        """Merge and sort two log lists by timestamp."""
        all_logs = logs1 + logs2
        # Sort by timestamp (first part of each line)
        return sorted(all_logs)

    def _filter_by_level(self, logs: List[str], level: LogLevel) -> List[str]:
        """Filter logs by level."""
        level_upper = level.upper()
        return [line for line in logs if self._matches_level(line, level)]

    def _matches_level(self, log_line: str, level: LogLevel) -> bool:
        """Check if log line matches the specified level."""
        if level == "all":
            return True

        level_upper = level.upper()
        return f"[{level_upper}]" in log_line

"""History service for Hermes.

This module provides history management operations, including listing,
retrieving, exporting, and deleting execution history and reports.
"""

from typing import List, Optional
from pathlib import Path
import logging

from hermes_cli.persistence.file_paths import FilePaths
from hermes_cli.persistence.history_repository import HistoryMeta, HistoryRepository


class HistoryService:
    """Service for managing execution history."""

    def __init__(self, file_paths: Optional[FilePaths] = None):
        """
        Initialize history service.

        Args:
            file_paths: File path manager (uses default if not provided)
        """
        self.file_paths = file_paths or FilePaths()
        self.repository = HistoryRepository(self.file_paths)
        self.logger = logging.getLogger(__name__)

    def list_history(self, limit: Optional[int] = None) -> List[HistoryMeta]:
        """
        List execution history, optionally limited.

        Args:
            limit: Maximum number of entries to return (newest first)

        Returns:
            List of history metadata entries
        """
        histories = self.repository.list_all(limit=limit)
        self.logger.info(f"Listed {len(histories)} history entries")
        return histories

    def get_history(self, task_id: str) -> Optional[HistoryMeta]:
        """
        Get specific history entry.

        Args:
            task_id: Task/run ID

        Returns:
            History metadata if found, None otherwise
        """
        return self.repository.load_meta(task_id)

    def get_report(self, task_id: str) -> Optional[str]:
        """
        Get report content for a specific run.

        Args:
            task_id: Task/run ID

        Returns:
            Report content if found, None otherwise
        """
        return self.repository.load_report(task_id)

    def export_report(self, task_id: str, dest_path: Path) -> bool:
        """
        Export report to specified path.

        Args:
            task_id: Task/run ID
            dest_path: Destination file path

        Returns:
            True if exported, False if history not found

        Raises:
            IOError: On file operation failure
        """
        meta = self.repository.load_meta(task_id)
        if not meta:
            self.logger.warning(f"History not found: {task_id}")
            return False

        if meta.status != "success" or not meta.report_file:
            self.logger.warning(f"History {task_id} has no successful report to export (status={meta.status})")
            return False

        self.repository.export_report(task_id, dest_path)
        self.logger.info(f"Exported report {task_id} to {dest_path}")
        return True

    def delete_history(self, task_id: str) -> bool:
        """
        Delete history entry and report.

        Args:
            task_id: Task/run ID to delete

        Returns:
            True if deleted, False if not found
        """
        meta = self.repository.load_meta(task_id)
        if not meta:
            self.logger.warning(f"History not found: {task_id}")
            return False

        self.repository.delete(task_id)
        self.logger.info(f"Deleted history: {task_id}")
        return True

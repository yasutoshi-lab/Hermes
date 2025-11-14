"""Task service for Hermes.

This module provides high-level task lifecycle management operations,
including creation, listing, updating, and deletion of tasks.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from hermes_cli.persistence.file_paths import FilePaths
from hermes_cli.persistence.task_repository import Task, TaskRepository, Status


class TaskService:
    """Service for managing task lifecycle."""

    def __init__(self, file_paths: Optional[FilePaths] = None):
        """
        Initialize task service.

        Args:
            file_paths: File path manager (uses default if not provided)
        """
        self.file_paths = file_paths or FilePaths()
        self.repository = TaskRepository(self.file_paths)
        self.logger = logging.getLogger(__name__)

    def create_task(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Task:
        """
        Create a new scheduled task.

        Args:
            prompt: Task prompt/query
            options: Optional configuration overrides

        Returns:
            Created task
        """
        options = options or {}
        task = self.repository.create(prompt, options)
        self.logger.info(f"Task created: {task.id}")
        return task

    def list_tasks(self, status_filter: Optional[Status] = None) -> List[Task]:
        """
        List all tasks, optionally filtered by status.

        Args:
            status_filter: Optional status to filter by

        Returns:
            List of tasks
        """
        tasks = self.repository.list_all()

        if status_filter:
            tasks = [t for t in tasks if t.status == status_filter]

        # Sort by created_at descending (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        self.logger.info(f"Listed {len(tasks)} tasks")
        return tasks

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get specific task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task if found, None otherwise
        """
        return self.repository.load(task_id)

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task ID to delete

        Returns:
            True if deleted, False if not found
        """
        task = self.repository.load(task_id)
        if not task:
            self.logger.warning(f"Task not found: {task_id}")
            return False

        self.repository.delete(task_id)
        self.logger.info(f"Task deleted: {task_id}")
        return True

    def update_status(self, task_id: str, status: Status) -> bool:
        """
        Update task status.

        Args:
            task_id: Task ID
            status: New status

        Returns:
            True if updated, False if task not found
        """
        task = self.repository.load(task_id)
        if not task:
            self.logger.warning(f"Task not found: {task_id}")
            return False

        self.repository.update_status(task_id, status)
        self.logger.info(f"Task {task_id} status updated to {status}")
        return True

    def get_latest_running_task(self) -> Optional[Task]:
        """
        Get the most recent task with 'running' status.

        Returns:
            Latest running task if any, None otherwise
        """
        tasks = self.list_tasks(status_filter="running")
        return tasks[0] if tasks else None

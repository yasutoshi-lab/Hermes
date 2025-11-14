"""Task queue execution service for Hermes.

Provides sequential execution of scheduled tasks so contributors can process
their backlog without manually invoking each task ID.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Literal
import logging

from hermes_cli.services.task_service import TaskService
from hermes_cli.services.run_service import RunService
from hermes_cli.persistence.history_repository import HistoryMeta


QueueStatus = Literal["success", "failed"]


@dataclass
class QueueResult:
    """Result of executing a single queued task."""

    task_id: str
    status: QueueStatus
    history_meta: Optional[HistoryMeta] = None
    error_message: Optional[str] = None


class QueueService:
    """Service that processes scheduled tasks sequentially."""

    def __init__(
        self,
        task_service: Optional[TaskService] = None,
        run_service: Optional[RunService] = None,
    ) -> None:
        self.task_service = task_service or TaskService()
        self.run_service = run_service or RunService()
        self.logger = logging.getLogger(__name__)

    def list_scheduled_tasks(self) -> List:
        """Return scheduled tasks ordered from oldest to newest."""
        tasks = [
            task for task in self.task_service.list_tasks()
            if task.status == "scheduled"
        ]
        tasks.sort(key=lambda t: t.created_at)
        return tasks

    def process_queue(self, limit: Optional[int] = None) -> List[QueueResult]:
        """
        Execute scheduled tasks sequentially.

        Args:
            limit: Maximum number of tasks to process. If None or <= 0, run all.

        Returns:
            List of QueueResult objects describing each execution outcome.
        """
        scheduled = self.list_scheduled_tasks()
        if not scheduled:
            return []

        if limit is not None and limit > 0:
            scheduled = scheduled[:limit]

        results: List[QueueResult] = []
        for task in scheduled:
            try:
                history_meta = self.run_service.run_task(task.id)
                results.append(QueueResult(
                    task_id=task.id,
                    status="success",
                    history_meta=history_meta,
                ))
            except Exception as exc:  # pragma: no cover - exercised via tests
                error_message = str(exc)
                self.logger.error(
                    "Queued task %s failed: %s",
                    task.id,
                    error_message,
                    exc_info=True,
                )
                results.append(QueueResult(
                    task_id=task.id,
                    status="failed",
                    error_message=error_message,
                ))

        return results

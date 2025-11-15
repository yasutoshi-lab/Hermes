"""Task service for Hermes"""

from pathlib import Path
from typing import Optional, List
from loguru import logger

from hermes_cli.models.task import Task, TaskOptions
from hermes_cli.persistence.task_repository import TaskRepository


class TaskService:
    """タスク管理サービス"""

    def __init__(self, work_dir: Optional[Path] = None):
        self.repository = TaskRepository(work_dir)

    def create_task(
        self, prompt: str, options: Optional[TaskOptions] = None
    ) -> Task:
        """タスク作成"""
        task_id = self.repository.generate_task_id()
        task = Task(id=task_id, prompt=prompt, status="scheduled", options=options)
        self.repository.save(task)
        logger.info(f"Task created: {task_id}", extra={"category": "CONFIG"})
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """タスク取得"""
        return self.repository.load(task_id)

    def list_tasks(self, status: Optional[str] = None) -> List[Task]:
        """タスク一覧"""
        tasks = self.repository.list_all()
        if status:
            tasks = [t for t in tasks if t.status == status]
        return tasks

    def update_task_status(self, task_id: str, status: str) -> bool:
        """タスクステータス更新"""
        task = self.repository.load(task_id)
        if not task:
            return False

        from datetime import datetime

        task.status = status
        task.updated_at = datetime.now()
        self.repository.save(task)
        logger.info(
            f"Task status updated: {task_id} -> {status}",
            extra={"category": "CONFIG"},
        )
        return True

    def delete_task(self, task_id: str) -> bool:
        """タスク削除"""
        return self.repository.delete(task_id)

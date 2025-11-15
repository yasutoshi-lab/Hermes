"""Task repository for Hermes"""

from pathlib import Path
from typing import List, Optional
from loguru import logger

from hermes_cli.models.task import Task
from hermes_cli.persistence.file_paths import FilePaths


class TaskRepository:
    """タスクリポジトリ"""

    def __init__(self, work_dir: Optional[Path] = None):
        self.file_paths = FilePaths(work_dir)

    def save(self, task: Task) -> None:
        """タスク保存"""
        self.file_paths.ensure_directories()
        task.save(self.file_paths.task_dir)
        logger.info(f"Task saved: {task.id}", extra={"category": "CONFIG"})

    def load(self, task_id: str) -> Optional[Task]:
        """タスク読み込み"""
        task_file = self.file_paths.task_dir / f"{task_id}.yaml"
        if not task_file.exists():
            return None

        try:
            with open(task_file, "r", encoding="utf-8") as f:
                return Task.from_yaml(f.read())
        except Exception as e:
            logger.error(
                f"Failed to load task {task_id}: {e}", extra={"category": "CONFIG"}
            )
            return None

    def list_all(self) -> List[Task]:
        """全タスク一覧"""
        tasks = []
        if not self.file_paths.task_dir.exists():
            return tasks

        for task_file in self.file_paths.task_dir.glob("*.yaml"):
            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    task = Task.from_yaml(f.read())
                    tasks.append(task)
            except Exception as e:
                logger.warning(
                    f"Failed to load task {task_file}: {e}",
                    extra={"category": "CONFIG"},
                )

        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    def delete(self, task_id: str) -> bool:
        """タスク削除"""
        task_file = self.file_paths.task_dir / f"{task_id}.yaml"
        if task_file.exists():
            task_file.unlink()
            logger.info(f"Task deleted: {task_id}", extra={"category": "CONFIG"})
            return True
        return False

    def generate_task_id(self) -> str:
        """タスクID生成 (YYYY-NNNN形式)"""
        from datetime import datetime

        year = datetime.now().year
        tasks = self.list_all()
        year_tasks = [t for t in tasks if t.id.startswith(str(year))]

        if year_tasks:
            max_num = max(int(t.id.split("-")[1]) for t in year_tasks)
            new_num = max_num + 1
        else:
            new_num = 1

        return f"{year}-{new_num:04d}"

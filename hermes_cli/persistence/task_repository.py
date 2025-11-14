"""Task file persistence for Hermes.

This module handles task YAML files, providing CRUD operations
for task creation, retrieval, update, and deletion.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Literal, Optional, Dict, Any, List
from pathlib import Path
import yaml

from .file_paths import FilePaths


Status = Literal["scheduled", "running", "done", "failed"]


@dataclass
class Task:
    """Task model.

    Attributes:
        id: Unique task identifier (format: YYYY-NNNN)
        prompt: User's task prompt/description
        created_at: Task creation timestamp
        status: Current task status
        options: Additional task options (language, validation settings, etc.)
    """
    id: str
    prompt: str
    created_at: datetime
    status: Status
    options: Dict[str, Any]


class TaskRepository:
    """Handles task file persistence.

    Provides methods for creating, loading, listing, updating, and deleting
    task files in YAML format.
    """

    def __init__(self, file_paths: FilePaths):
        """Initialize task repository.

        Args:
            file_paths: FilePaths instance for path management
        """
        self.file_paths = file_paths

    def create(self, prompt: str, options: Dict[str, Any]) -> Task:
        """Create new task with auto-generated ID.

        Generates a unique task ID in format YYYY-NNNN (e.g., 2025-0001)
        and saves the task to a YAML file.

        Args:
            prompt: User's task prompt
            options: Task options dictionary

        Returns:
            Created Task object
        """
        # Generate ID format: YYYY-NNNN (e.g., 2025-0001)
        task_id = self._generate_next_id()

        task = Task(
            id=task_id,
            prompt=prompt,
            created_at=datetime.now(),
            status="scheduled",
            options=options,
        )

        self.save(task)
        return task

    def save(self, task: Task) -> None:
        """Save task to YAML file.

        Args:
            task: Task object to save
        """
        task_path = self.file_paths.task_file(task.id)
        task_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert task to dict, handling datetime serialization
        task_dict = asdict(task)
        task_dict['created_at'] = task.created_at.isoformat()

        with open(task_path, 'w', encoding='utf-8') as f:
            yaml.dump(task_dict, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def load(self, task_id: str) -> Optional[Task]:
        """Load task from file.

        Args:
            task_id: Task identifier

        Returns:
            Task object if found, None otherwise
        """
        task_path = self.file_paths.task_file(task_id)

        if not task_path.exists():
            return None

        with open(task_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Parse datetime from ISO format
        created_at = datetime.fromisoformat(data['created_at'])

        return Task(
            id=data['id'],
            prompt=data['prompt'],
            created_at=created_at,
            status=data['status'],
            options=data['options'],
        )

    def list_all(self) -> List[Task]:
        """List all tasks.

        Returns:
            List of all Task objects, sorted by creation time (newest first)
        """
        task_dir = self.file_paths.task_dir

        if not task_dir.exists():
            return []

        tasks = []
        for task_file in task_dir.glob("task-*.yaml"):
            task_id = task_file.stem.replace("task-", "")
            task = self.load(task_id)
            if task:
                tasks.append(task)

        # Sort by creation time, newest first
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks

    def delete(self, task_id: str) -> None:
        """Delete task file.

        Args:
            task_id: Task identifier

        Raises:
            FileNotFoundError: If task file doesn't exist
        """
        task_path = self.file_paths.task_file(task_id)

        if not task_path.exists():
            raise FileNotFoundError(f"Task file not found: {task_id}")

        task_path.unlink()

    def update_status(self, task_id: str, status: Status) -> None:
        """Update task status.

        Args:
            task_id: Task identifier
            status: New status value

        Raises:
            FileNotFoundError: If task doesn't exist
        """
        task = self.load(task_id)

        if task is None:
            raise FileNotFoundError(f"Task not found: {task_id}")

        task.status = status
        self.save(task)

    def _generate_next_id(self) -> str:
        """Generate next available task ID.

        Returns:
            Task ID in format YYYY-NNNN
        """
        current_year = datetime.now().year
        existing_tasks = self.list_all()

        # Find highest number for current year
        max_num = 0
        for task in existing_tasks:
            if task.id.startswith(f"{current_year}-"):
                try:
                    num = int(task.id.split("-")[1])
                    max_num = max(max_num, num)
                except (IndexError, ValueError):
                    continue

        next_num = max_num + 1
        return f"{current_year}-{next_num:04d}"

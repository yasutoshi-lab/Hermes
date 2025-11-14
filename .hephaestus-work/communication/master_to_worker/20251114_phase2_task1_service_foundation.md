# Task: Service Layer Foundation

**Task ID**: phase2_task1_service_foundation
**Priority**: high
**Assigned to**: worker-1
**Dependencies**: phase1_task1_project_setup, phase1_task2_persistence_layer

## Objective
Implement the foundational service layer components: ConfigService and TaskService. These services provide high-level business logic on top of the persistence layer.

## Context
Services act as the business logic layer between CLI commands and the persistence layer. They handle configuration management, task lifecycle, and provide clean APIs for the CLI layer.

Reference design document: `/home/ubuntu/python_project/Hermes/詳細設計書.md` (section 8.1, 8.2)

## Requirements

### 1. Implement `services/config_service.py`

```python
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from hermes_cli.persistence.file_paths import FilePaths
from hermes_cli.persistence.config_repository import (
    Config,
    ConfigRepository,
    OllamaConfig,
    ValidationConfig,
    SearchConfig,
    LoggingConfig,
)


class ConfigService:
    """Service for managing application configuration."""

    def __init__(self, file_paths: Optional[FilePaths] = None):
        """
        Initialize config service.

        Args:
            file_paths: File path manager (uses default if not provided)
        """
        self.file_paths = file_paths or FilePaths()
        self.repository = ConfigRepository()
        self.logger = logging.getLogger(__name__)

    def load(self) -> Config:
        """
        Load configuration from file.

        Returns:
            Loaded configuration

        Notes:
            - Creates default config if file doesn't exist
            - Returns default config if file is corrupted
        """
        config_path = self.file_paths.config_file

        if not config_path.exists():
            self.logger.info("Config file not found, creating default")
            config = self.repository.create_default()
            self.save(config)
            return config

        try:
            config = self.repository.load(config_path)
            self.logger.info("Configuration loaded successfully")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}, using default")
            return self.repository.create_default()

    def save(self, config: Config) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration to save
        """
        self.file_paths.ensure_directories()
        config_path = self.file_paths.config_file
        self.repository.save(config, config_path)
        self.logger.info("Configuration saved")

    def reset_to_default(self) -> Config:
        """
        Reset configuration to default values.

        Returns:
            Default configuration
        """
        config = self.repository.create_default()
        self.save(config)
        self.logger.info("Configuration reset to default")
        return config

    def apply_overrides(self, config: Config, overrides: Dict[str, Any]) -> Config:
        """
        Apply CLI option overrides to configuration.

        Args:
            config: Base configuration
            overrides: Dictionary of override values
                      Keys: 'api', 'model', 'retry', 'timeout', 'language',
                           'min_validation', 'max_validation', 'query_count',
                           'min_sources', 'max_sources'

        Returns:
            Configuration with overrides applied (does not modify original)

        Example:
            overrides = {
                'api': 'http://localhost:11434/api/chat',
                'model': 'gpt-oss:20b',
                'language': 'ja',
                'query_count': 5,
            }
        """
        # Create a copy and apply overrides
        # Handle nested structure (ollama.api_base, validation.min_loops, etc.)
        pass

    def get_ollama_config(self, config: Config) -> 'OllamaConfig':
        """
        Extract Ollama-specific configuration.

        Args:
            config: Full configuration

        Returns:
            Ollama configuration object
        """
        return config.ollama
```

### 2. Implement `services/task_service.py`

```python
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
```

### 3. Update `services/__init__.py`

```python
"""
Services package for Hermes.

Business logic layer providing high-level operations for:
- Configuration management
- Task lifecycle management
- Execution orchestration
- History management
- Log management
"""

from .config_service import ConfigService
from .task_service import TaskService

__all__ = [
    "ConfigService",
    "TaskService",
]
```

## Implementation Notes

### Error Handling
- Services should handle repository-level errors gracefully
- Log errors at appropriate levels
- Return None or False for expected failures (e.g., task not found)
- Raise exceptions only for unexpected failures

### Logging
- Log all significant operations (create, update, delete)
- Include relevant context (task IDs, file paths)
- Use appropriate log levels (INFO for normal ops, WARNING for issues, ERROR for failures)

### Configuration Overrides
The `apply_overrides` method should handle CLI option mappings:
- `api` → `ollama.api_base`
- `model` → `ollama.model`
- `retry` → `ollama.retry`
- `timeout` → `ollama.timeout_sec`
- `language` → `language`
- `min_validation` → `validation.min_loops`
- `max_validation` → `validation.max_loops`
- `query_count` → (custom option, stored in task options)
- `min_sources` → `search.min_sources`
- `max_sources` → `search.max_sources`

### Type Hints
- Use proper type hints throughout
- Import types from persistence layer
- Use Optional[] for nullable returns
- Use List[], Dict[] for collections

## Expected Output

All files in `/home/ubuntu/python_project/Hermes/hermes_cli/services/`:
1. `config_service.py` - Complete ConfigService implementation
2. `task_service.py` - Complete TaskService implementation
3. `__init__.py` - Package exports

## Resources

- Design document section: 8.1, 8.2
- Persistence layer modules (already implemented in Phase 1)
- Python logging documentation

## Success Criteria

- Both service classes fully implemented with all methods
- Proper error handling and logging
- Type hints and docstrings complete
- Integration with persistence layer working
- Can be imported: `from hermes_cli.services import ConfigService, TaskService`
- Services can be instantiated and used without errors

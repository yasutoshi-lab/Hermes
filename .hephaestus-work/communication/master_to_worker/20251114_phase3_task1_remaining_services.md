# Task: Remaining Services Implementation

**Task ID**: phase3_task1_remaining_services
**Priority**: high
**Assigned to**: worker-1
**Dependencies**: phase2_task1_service_foundation, phase2_task2_langgraph_workflow, phase1_task2_persistence_layer

## Objective
Implement the remaining service layer components: RunService, HistoryService, LogService, and DebugService. These services complete the business logic layer.

## Context
These services build on the foundation services (ConfigService, TaskService) and provide high-level operations for execution, history management, and log viewing.

Reference design document: `/home/ubuntu/python_project/Hermes/詳細設計書.md` (section 8.3, 8.4, 8.5)

## Requirements

### 1. Implement `services/run_service.py`

```python
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from hermes_cli.persistence.file_paths import FilePaths
from hermes_cli.persistence.task_repository import Task, TaskRepository
from hermes_cli.persistence.history_repository import HistoryMeta, HistoryRepository
from hermes_cli.persistence.log_repository import LogRepository
from hermes_cli.services.config_service import ConfigService
from hermes_cli.agents import create_hermes_workflow, HermesState


class RunService:
    """Service for executing Hermes tasks and workflows."""

    def __init__(self, file_paths: Optional[FilePaths] = None):
        """
        Initialize run service.

        Args:
            file_paths: File path manager (uses default if not provided)
        """
        self.file_paths = file_paths or FilePaths()
        self.config_service = ConfigService(self.file_paths)
        self.task_repository = TaskRepository(self.file_paths)
        self.history_repository = HistoryRepository(self.file_paths)
        self.log_repository = LogRepository(self.file_paths)
        self.logger = logging.getLogger(__name__)

    def run_prompt(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> HistoryMeta:
        """
        Execute a single-shot research task from a prompt.

        Args:
            prompt: User query/prompt
            options: Optional configuration overrides
                    Keys: api, model, retry, timeout, language,
                         min_validation, max_validation, query_count,
                         min_sources, max_sources

        Returns:
            History metadata for the completed run

        Raises:
            RuntimeError: On execution failure
        """
        options = options or {}

        # Load config and apply overrides
        config = self.config_service.load()
        if options:
            config = self.config_service.apply_overrides(config, options)

        # Generate task ID for this run
        task_id = self._generate_run_id()

        # Initialize logging
        self.log_repository.write_log(
            "INFO", "RUN", f"Starting task execution",
            task_id=task_id, prompt=prompt[:50]
        )

        try:
            # Create initial state
            state = HermesState(
                user_prompt=prompt,
                language=options.get('language', config.language),
                min_validation=options.get('min_validation', config.validation.min_loops),
                max_validation=options.get('max_validation', config.validation.max_loops),
                min_sources=options.get('min_sources', config.search.min_sources),
                max_sources=options.get('max_sources', config.search.max_sources),
            )

            # Execute workflow
            self.log_repository.write_log(
                "INFO", "RUN", "Initializing LangGraph workflow", task_id=task_id
            )

            workflow = create_hermes_workflow()
            result_state = workflow.invoke(state)

            # Extract final report
            if not result_state.validated_report:
                raise RuntimeError("Workflow did not produce a report")

            # Save to history
            created_at = datetime.now()
            finished_at = datetime.now()

            history_meta = HistoryMeta(
                id=task_id,
                prompt=prompt,
                created_at=created_at,
                finished_at=finished_at,
                model=config.ollama.model,
                language=state.language,
                validation_loops=state.loop_count,
                source_count=sum(len(r) for r in result_state.query_results.values()),
                report_file=f"report-{task_id}.md",
            )

            self.history_repository.save_report(task_id, result_state.validated_report)
            self.history_repository.save_meta(history_meta)

            self.log_repository.write_log(
                "INFO", "RUN", "Task execution completed",
                task_id=task_id, sources=history_meta.source_count
            )

            return history_meta

        except Exception as e:
            self.log_repository.write_log(
                "ERROR", "RUN", f"Task execution failed: {str(e)}",
                task_id=task_id
            )
            raise RuntimeError(f"Execution failed: {str(e)}") from e

    def run_task(self, task_id: str) -> HistoryMeta:
        """
        Execute a pre-scheduled task.

        Args:
            task_id: Task ID to execute

        Returns:
            History metadata for the completed run

        Raises:
            ValueError: If task not found
            RuntimeError: On execution failure
        """
        task = self.task_repository.load(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")

        # Update task status to running
        self.task_repository.update_status(task_id, "running")

        try:
            # Execute using task prompt and options
            history_meta = self.run_prompt(task.prompt, task.options)

            # Update task status to done
            self.task_repository.update_status(task_id, "done")

            return history_meta

        except Exception as e:
            # Update task status to failed
            self.task_repository.update_status(task_id, "failed")
            raise

    def _generate_run_id(self) -> str:
        """
        Generate unique run ID.

        Returns:
            Run ID in format: YYYY-NNNN
        """
        # Use same format as task IDs
        now = datetime.now()
        year = now.year

        # Find next available number
        # This is simplified - could collide if multiple runs at same time
        # In production, use better ID generation
        import random
        num = random.randint(1, 9999)

        return f"{year}-{num:04d}"
```

### 2. Implement `services/history_service.py`

```python
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
```

### 3. Implement `services/log_service.py`

```python
from typing import Iterator, Optional
from datetime import datetime
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
```

### 4. Implement `services/debug_service.py`

```python
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
```

### 5. Update `services/__init__.py`

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
from .run_service import RunService
from .history_service import HistoryService
from .log_service import LogService
from .debug_service import DebugService, LogLevel

__all__ = [
    "ConfigService",
    "TaskService",
    "RunService",
    "HistoryService",
    "LogService",
    "DebugService",
    "LogLevel",
]
```

## Implementation Notes

### Error Handling
- Services should handle repository-level errors gracefully
- Log errors at appropriate levels
- Return None or False for expected failures
- Raise specific exceptions for unexpected failures

### Logging Integration
- Use LogRepository for structured logging throughout
- Include task IDs in log messages where applicable
- Log at appropriate levels (INFO for operations, ERROR for failures)

### RunService Integration
- RunService ties together config, tasks, agents, and persistence
- It's the core execution engine for Hermes
- Handles full lifecycle: initialization → execution → persistence

### ID Generation
- Use consistent ID format (YYYY-NNNN) across tasks and runs
- In production, consider using UUID or more robust ID generation
- Current implementation uses simple counter/random for prototyping

## Expected Output

All files in `/home/ubuntu/python_project/Hermes/hermes_cli/services/`:
1. `run_service.py` - Complete RunService implementation
2. `history_service.py` - Complete HistoryService implementation
3. `log_service.py` - Complete LogService implementation
4. `debug_service.py` - Complete DebugService implementation
5. Updated `__init__.py` with all exports

## Resources

- Design document sections: 8.3, 8.4, 8.5
- Phase 2 implementations: config_service, task_service, agents
- Phase 1 implementations: persistence layer

## Success Criteria

- All four service classes fully implemented
- Proper integration with persistence layer
- RunService successfully orchestrates workflow execution
- HistoryService manages report exports and deletions
- LogService provides tail and stream functionality
- DebugService filters logs by level
- Type hints and docstrings complete
- Can be imported: `from hermes_cli.services import RunService, HistoryService, LogService, DebugService`

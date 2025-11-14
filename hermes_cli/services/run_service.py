"""Run service for Hermes.

This module provides workflow execution and orchestration operations,
including running tasks and managing the execution lifecycle.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging
import random

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
        num = random.randint(1, 9999)

        return f"{year}-{num:04d}"

"""Run service for Hermes.

This module provides workflow execution and orchestration operations,
including running tasks and managing the execution lifecycle.
"""

from __future__ import annotations

from typing import Callable, Optional, Dict, Any
from datetime import datetime
import logging
import random

from hermes_cli.persistence.file_paths import FilePaths
from hermes_cli.persistence.task_repository import Task, TaskRepository
from hermes_cli.persistence.history_repository import HistoryMeta, HistoryRepository
from hermes_cli.persistence.log_repository import LogRepository
from hermes_cli.services.config_service import ConfigService
from hermes_cli.agents import create_hermes_workflow, HermesState
from hermes_cli.tools.ollama_client import OllamaClient, OllamaConfig as OllamaClientConfig


class RunService:
    """Service for executing Hermes tasks and workflows."""

    def __init__(
        self,
        file_paths: Optional[FilePaths] = None,
        ollama_client_factory: Optional[Callable[[OllamaClientConfig], OllamaClient]] = None,
    ):
        """
        Initialize run service.

        Args:
            file_paths: File path manager (uses default if not provided)
            ollama_client_factory: Optional factory for creating Ollama clients
                                   (enables dependency injection in tests)
        """
        self.file_paths = file_paths or FilePaths()
        self.config_service = ConfigService(self.file_paths)
        self.task_repository = TaskRepository(self.file_paths)
        self.history_repository = HistoryRepository(self.file_paths)
        self.log_repository = LogRepository(self.file_paths)
        self.logger = logging.getLogger(__name__)
        self.ollama_client_factory = ollama_client_factory or (lambda cfg: OllamaClient(cfg))

    def run_prompt(
        self,
        prompt: str,
        options: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
    ) -> HistoryMeta:
        """
        Execute a single-shot research task from a prompt.

        Args:
            prompt: User query/prompt
            options: Optional configuration overrides
                    Keys: api, model, retry, timeout, language,
                         min_validation, max_validation, query_count,
                         min_sources, max_sources

        Args:
            prompt: User query/prompt
            options: Optional configuration overrides
            task_id: Optional externally provided task ID (used for scheduled tasks)

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
        run_id = task_id or self._generate_run_id()
        state: Optional[HermesState] = None

        # Initialize logging
        self.log_repository.write_log(
            "INFO", "RUN", f"Starting task execution",
            task_id=run_id, prompt=prompt[:50]
        )

        try:
            # Create initial state
            ollama_config = OllamaClientConfig(
                api_base=config.ollama.api_base,
                model=config.ollama.model,
                retry=config.ollama.retry,
                timeout_sec=config.ollama.timeout_sec,
            )

            state = HermesState(
                user_prompt=prompt,
                language=options.get('language', config.language),
                min_validation=options.get('min_validation', config.validation.min_loops),
                max_validation=options.get('max_validation', config.validation.max_loops),
                min_sources=options.get('min_sources', config.search.min_sources),
                max_sources=options.get('max_sources', config.search.max_sources),
                query_count=options.get('query_count') or 3,
                ollama_config=ollama_config,
                ollama_client_factory=self.ollama_client_factory,
            )

            # Execute workflow
            self.log_repository.write_log(
                "INFO", "RUN", "Initializing LangGraph workflow", task_id=task_id
            )

            workflow = create_hermes_workflow()
            result_state = workflow.invoke(state)

            # Extract final report (LangGraph returns dict)
            validated_report = result_state.get("validated_report", "")
            if not validated_report:
                raise RuntimeError("Workflow did not produce a report")

            # Save to history
            created_at = datetime.now()
            finished_at = datetime.now()

            history_meta = HistoryMeta(
                id=run_id,
                prompt=prompt,
                created_at=created_at,
                finished_at=finished_at,
                model=config.ollama.model,
                language=result_state.get("language", state.language),
                validation_loops=result_state.get("loop_count", 0),
                source_count=sum(len(r) for r in result_state.get("query_results", {}).values()),
                report_file=f"report-{run_id}.md",
                status="success",
            )

            self.history_repository.save_report(run_id, validated_report)
            self.history_repository.save_meta(history_meta)

            self.log_repository.write_log(
                "INFO", "RUN", "Task execution completed",
                task_id=run_id, sources=history_meta.source_count
            )

            return history_meta

        except Exception as e:
            self.log_repository.write_log(
                "ERROR", "RUN", f"Task execution failed: {str(e)}",
                task_id=run_id
            )
            self._record_failure_meta(run_id, prompt, config, state, str(e))
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
            history_meta = self.run_prompt(task.prompt, task.options, task_id=task_id)

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

    def _record_failure_meta(
        self,
        run_id: str,
        prompt: str,
        config,
        state: Optional[HermesState],
        error_message: str,
    ) -> None:
        """Persist failure metadata so history reflects unsuccessful runs."""
        now = datetime.now()
        language = state.language if state else config.language
        validation_loops = state.loop_count if state else 0
        source_count = 0

        if state:
            try:
                source_count = sum(len(r) for r in state.query_results.values())
            except Exception:
                source_count = 0

        failure_meta = HistoryMeta(
            id=run_id,
            prompt=prompt,
            created_at=now,
            finished_at=now,
            model=config.ollama.model,
            language=language,
            validation_loops=validation_loops,
            source_count=source_count,
            report_file="",
            status="failed",
            error_message=error_message[:500],
        )

        try:
            self.history_repository.save_meta(failure_meta)
            self.logger.warning("Recorded failure metadata for %s", run_id)
        except Exception as exc:
            self.logger.error("Failed to store failure metadata for %s: %s", run_id, exc)

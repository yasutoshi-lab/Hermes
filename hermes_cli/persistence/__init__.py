"""Persistence layer for Hermes.

This package provides file-based persistence for tasks, history, logs, and configuration.
All data is stored under ~/.hermes/ directory with OS-specific path handling.
"""

from .file_paths import FilePaths
from .config_repository import (
    Config,
    OllamaConfig,
    ValidationConfig,
    SearchConfig,
    LoggingConfig,
    ConfigRepository,
)
from .task_repository import Task, Status, TaskRepository
from .history_repository import HistoryMeta, HistoryRepository
from .log_repository import LogRepository

__all__ = [
    # Path management
    "FilePaths",
    # Configuration
    "Config",
    "OllamaConfig",
    "ValidationConfig",
    "SearchConfig",
    "LoggingConfig",
    "ConfigRepository",
    # Tasks
    "Task",
    "Status",
    "TaskRepository",
    # History
    "HistoryMeta",
    "HistoryRepository",
    # Logging
    "LogRepository",
]

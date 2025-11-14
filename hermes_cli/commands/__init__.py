"""
CLI commands for Hermes.

Each module implements a specific command group:
- init: Initialize Hermes environment
- task: Task scheduling and management
- run: Execute research tasks
- log: View execution logs
- history: Manage execution history
- debug: View debug logs
"""

from .init_cmd import init_command
from .task_cmd import task_command
from .run_cmd import run_command
from .log_cmd import log_command
from .history_cmd import history_command
from .debug_cmd import debug_command
from .queue_cmd import queue_command

__all__ = [
    "init_command",
    "task_command",
    "run_command",
    "log_command",
    "history_command",
    "debug_command",
    "queue_command",
]

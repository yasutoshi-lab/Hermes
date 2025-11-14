"""File path management for Hermes data storage.

This module provides centralized path management for all Hermes data files,
with support for both Linux/Mac and Windows operating systems.
"""

from pathlib import Path
from typing import Optional
import platform


class FilePaths:
    """Manages all file paths for Hermes data storage.

    Provides centralized access to all file and directory paths used by Hermes,
    with automatic OS-specific path resolution.

    Attributes:
        _base_path: Base directory for all Hermes data (~/.hermes/)
    """

    def __init__(self, base_path: Optional[Path] = None):
        """Initialize file paths.

        Args:
            base_path: Override default ~/.hermes/ path (useful for testing).
                      If None, uses OS-appropriate default path.
        """
        if base_path is not None:
            self._base_path = Path(base_path)
        else:
            # Detect OS and set appropriate base path
            home = Path.home()
            self._base_path = home / ".hermes"

    @property
    def base(self) -> Path:
        """Base directory (~/.hermes/)."""
        return self._base_path

    @property
    def cache(self) -> Path:
        """Cache directory."""
        return self._base_path / "cache"

    @property
    def config_file(self) -> Path:
        """Config file path (config.yaml)."""
        return self._base_path / "config.yaml"

    @property
    def task_dir(self) -> Path:
        """Task directory."""
        return self._base_path / "task"

    @property
    def log_dir(self) -> Path:
        """Log directory."""
        return self._base_path / "log"

    @property
    def debug_log_dir(self) -> Path:
        """Debug log directory."""
        return self._base_path / "debug_log"

    @property
    def history_dir(self) -> Path:
        """History directory."""
        return self._base_path / "history"

    def ensure_directories(self) -> None:
        """Create all directories if they don't exist.

        Creates the base directory and all subdirectories required by Hermes.
        This method is idempotent and safe to call multiple times.
        """
        directories = [
            self.base,
            self.cache,
            self.task_dir,
            self.log_dir,
            self.debug_log_dir,
            self.history_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def task_file(self, task_id: str) -> Path:
        """Get path for specific task file.

        Args:
            task_id: Task identifier (e.g., "2025-0001")

        Returns:
            Path to task YAML file
        """
        return self.task_dir / f"task-{task_id}.yaml"

    def history_meta_file(self, task_id: str) -> Path:
        """Get path for history metadata file.

        Args:
            task_id: Task identifier (e.g., "2025-0001")

        Returns:
            Path to history metadata YAML file
        """
        return self.history_dir / f"report-{task_id}.meta.yaml"

    def history_report_file(self, task_id: str) -> Path:
        """Get path for history report file.

        Args:
            task_id: Task identifier (e.g., "2025-0001")

        Returns:
            Path to history report markdown file
        """
        return self.history_dir / f"report-{task_id}.md"

"""History metadata and report file persistence for Hermes.

This module handles history metadata YAML files and markdown report files,
providing operations for saving, loading, listing, and managing historical task results.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import yaml
import shutil

from .file_paths import FilePaths


@dataclass
class HistoryMeta:
    """History metadata model.

    Attributes:
        id: Task identifier
        prompt: Original task prompt
        created_at: Task creation timestamp
        finished_at: Task completion timestamp
        model: LLM model used
        language: Output language used
        validation_loops: Number of validation loops executed
        source_count: Total number of sources collected
        report_file: Filename of the report markdown file
    """
    id: str
    prompt: str
    created_at: datetime
    finished_at: datetime
    model: str
    language: str
    validation_loops: int
    source_count: int
    report_file: str


class HistoryRepository:
    """Handles history metadata and report files.

    Provides methods for saving, loading, listing, and managing
    task execution history and generated reports.
    """

    def __init__(self, file_paths: FilePaths):
        """Initialize history repository.

        Args:
            file_paths: FilePaths instance for path management
        """
        self.file_paths = file_paths

    def save_meta(self, meta: HistoryMeta) -> None:
        """Save history metadata.

        Args:
            meta: HistoryMeta object to save
        """
        meta_path = self.file_paths.history_meta_file(meta.id)
        meta_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict, handling datetime serialization
        meta_dict = asdict(meta)
        meta_dict['created_at'] = meta.created_at.isoformat()
        meta_dict['finished_at'] = meta.finished_at.isoformat()

        with open(meta_path, 'w', encoding='utf-8') as f:
            yaml.dump(meta_dict, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def save_report(self, task_id: str, report_content: str) -> None:
        """Save report markdown file.

        Args:
            task_id: Task identifier
            report_content: Markdown content of the report
        """
        report_path = self.file_paths.history_report_file(task_id)
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

    def load_meta(self, task_id: str) -> Optional[HistoryMeta]:
        """Load history metadata.

        Args:
            task_id: Task identifier

        Returns:
            HistoryMeta object if found, None otherwise
        """
        meta_path = self.file_paths.history_meta_file(task_id)

        if not meta_path.exists():
            return None

        with open(meta_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Parse datetime from ISO format
        created_at = datetime.fromisoformat(data['created_at'])
        finished_at = datetime.fromisoformat(data['finished_at'])

        return HistoryMeta(
            id=data['id'],
            prompt=data['prompt'],
            created_at=created_at,
            finished_at=finished_at,
            model=data['model'],
            language=data['language'],
            validation_loops=data['validation_loops'],
            source_count=data['source_count'],
            report_file=data['report_file'],
        )

    def load_report(self, task_id: str) -> Optional[str]:
        """Load report content.

        Args:
            task_id: Task identifier

        Returns:
            Report content as string if found, None otherwise
        """
        report_path = self.file_paths.history_report_file(task_id)

        if not report_path.exists():
            return None

        with open(report_path, 'r', encoding='utf-8') as f:
            return f.read()

    def list_all(self, limit: Optional[int] = None) -> List[HistoryMeta]:
        """List all history entries, optionally limited.

        Args:
            limit: Maximum number of entries to return (most recent first).
                  If None, returns all entries.

        Returns:
            List of HistoryMeta objects, sorted by finished_at (newest first)
        """
        history_dir = self.file_paths.history_dir

        if not history_dir.exists():
            return []

        histories = []
        for meta_file in history_dir.glob("report-*.meta.yaml"):
            # Extract task_id from filename: report-{task_id}.meta.yaml
            task_id = meta_file.stem.replace(".meta", "").replace("report-", "")
            meta = self.load_meta(task_id)
            if meta:
                histories.append(meta)

        # Sort by finished_at, newest first
        histories.sort(key=lambda h: h.finished_at, reverse=True)

        # Apply limit if specified
        if limit is not None:
            histories = histories[:limit]

        return histories

    def delete(self, task_id: str) -> None:
        """Delete history metadata and report.

        Args:
            task_id: Task identifier

        Raises:
            FileNotFoundError: If history files don't exist
        """
        meta_path = self.file_paths.history_meta_file(task_id)
        report_path = self.file_paths.history_report_file(task_id)

        if not meta_path.exists() and not report_path.exists():
            raise FileNotFoundError(f"History not found: {task_id}")

        # Delete both files if they exist
        if meta_path.exists():
            meta_path.unlink()
        if report_path.exists():
            report_path.unlink()

    def export_report(self, task_id: str, dest_path: Path) -> None:
        """Copy report to destination path.

        Args:
            task_id: Task identifier
            dest_path: Destination file path

        Raises:
            FileNotFoundError: If report doesn't exist
        """
        report_path = self.file_paths.history_report_file(task_id)

        if not report_path.exists():
            raise FileNotFoundError(f"Report not found: {task_id}")

        # Ensure destination directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy report file to destination
        shutil.copy2(report_path, dest_path)

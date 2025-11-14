#!/usr/bin/env python3
"""
Persistence layer smoke test.

Exercises TaskService CRUD paths and HistoryService read/export/delete
operations using temporary objects under ~/.hermes.
"""

from datetime import datetime
from pathlib import Path

from hermes_cli.services import TaskService, HistoryService
from hermes_cli.persistence.file_paths import FilePaths
from hermes_cli.persistence.history_repository import HistoryMeta


def main() -> None:
    file_paths = FilePaths()
    task_service = TaskService(file_paths)
    history_service = HistoryService(file_paths)

    print("=== TaskService CRUD ===")
    task = task_service.create_task(
        "Integration test prompt",
        options={"language": "en", "min_validation": 1, "max_validation": 2},
    )
    print(f"Created task: {task.id} ({task.status})")

    tasks = task_service.list_tasks()
    print(f"Total tasks after create: {len(tasks)}")

    task_service.update_status(task.id, "running")
    updated = task_service.get_task(task.id)
    print(f"Status after update: {updated.status}")

    task_service.delete_task(task.id)
    print(f"Deleted task: {task.id}")

    print("\n=== HistoryService persistence ===")
    history_id = "integration-test-0001"
    meta = HistoryMeta(
        id=history_id,
        prompt="Integration history prompt",
        created_at=datetime.now(),
        finished_at=datetime.now(),
        model="gpt-oss:20b",
        language="ja",
        validation_loops=2,
        source_count=4,
        report_file=f"{history_id}.md",
    )

    history_service.repository.save_meta(meta)
    history_service.repository.save_report(history_id, "# Test Report\n\nAll good.")
    print(f"Saved history metadata and report for {history_id}")

    histories = history_service.list_history()
    print(f"History entries available: {len(histories)}")
    fetched = history_service.get_history(history_id)
    print(f"Fetched history language: {fetched.language if fetched else 'missing'}")

    export_path = Path(file_paths.history_dir) / f"{history_id}-export.md"
    history_service.export_report(history_id, export_path)
    print(f"Exported report exists: {export_path.exists()}")

    history_service.delete_history(history_id)
    if export_path.exists():
        export_path.unlink()
    print(f"Cleaned up history entry {history_id}")


if __name__ == "__main__":
    main()

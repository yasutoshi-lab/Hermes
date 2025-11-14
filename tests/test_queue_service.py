from datetime import datetime
from typing import List

from hermes_cli.services.queue_service import QueueService
from hermes_cli.services.task_service import TaskService
from hermes_cli.persistence.file_paths import FilePaths
from hermes_cli.persistence.history_repository import HistoryMeta


class StubRunService:
    def __init__(self, task_service: TaskService):
        self.task_service = task_service
        self.executed: List[str] = []

    def run_task(self, task_id: str) -> HistoryMeta:
        self.executed.append(task_id)
        # Simulate successful completion
        return HistoryMeta(
            id=task_id,
            prompt="prompt",
            created_at=datetime.now(),
            finished_at=datetime.now(),
            model="model",
            language="ja",
            validation_loops=1,
            source_count=1,
            report_file=f"report-{task_id}.md",
        )


class FailingRunService(StubRunService):
    def run_task(self, task_id: str) -> HistoryMeta:
        raise RuntimeError(f"boom-{task_id}")


def _task_service(tmp_path):
    file_paths = FilePaths(base_path=tmp_path / ".hermes")
    return TaskService(file_paths)


def test_queue_service_runs_tasks_in_creation_order(tmp_path):
    task_service = _task_service(tmp_path)
    first = task_service.create_task("First")
    second = task_service.create_task("Second")
    run_service = StubRunService(task_service)
    queue_service = QueueService(task_service=task_service, run_service=run_service)

    results = queue_service.process_queue()

    assert [r.task_id for r in results] == [first.id, second.id]
    assert run_service.executed == [first.id, second.id]
    assert all(r.status == "success" for r in results)


def test_queue_service_respects_limit_and_handles_failures(tmp_path):
    task_service = _task_service(tmp_path)
    task_service.create_task("First")
    task_service.create_task("Second")
    run_service = FailingRunService(task_service)
    queue_service = QueueService(task_service=task_service, run_service=run_service)

    # Limit to one task so only the first failure is recorded
    results = queue_service.process_queue(limit=1)

    assert len(results) == 1
    assert results[0].status == "failed"
    assert "boom" in (results[0].error_message or "")

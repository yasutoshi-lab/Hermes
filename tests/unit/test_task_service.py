"""Unit tests for TaskService"""

import pytest
from datetime import datetime

from hermes_cli.services.task_service import TaskService
from hermes_cli.models.task import Task


class TestTaskService:
    """TaskServiceのテスト"""

    @pytest.fixture
    def task_service(self, temp_work_dir):
        """TaskServiceインスタンス"""
        return TaskService(temp_work_dir)

    def test_create_task(self, task_service):
        """タスク作成テスト"""
        prompt = "Test prompt for task creation"
        task = task_service.create_task(prompt)

        assert task is not None
        assert task.prompt == prompt
        assert task.status == "scheduled"
        assert task.id is not None

    def test_get_task(self, task_service):
        """タスク取得テスト"""
        # タスク作成
        prompt = "Test prompt"
        created_task = task_service.create_task(prompt)

        # タスク取得
        retrieved_task = task_service.get_task(created_task.id)

        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.prompt == created_task.prompt

    def test_get_nonexistent_task(self, task_service):
        """存在しないタスクの取得テスト"""
        task = task_service.get_task("nonexistent-id")
        assert task is None

    def test_list_tasks(self, task_service):
        """タスク一覧取得テスト"""
        # 複数タスク作成
        task_service.create_task("Task 1")
        task_service.create_task("Task 2")
        task_service.create_task("Task 3")

        # 一覧取得
        tasks = task_service.list_tasks()

        assert len(tasks) == 3

    def test_list_tasks_by_status(self, task_service):
        """ステータス別タスク一覧取得テスト"""
        # タスク作成とステータス更新
        task1 = task_service.create_task("Scheduled task")
        task2 = task_service.create_task("Running task")
        task3 = task_service.create_task("Completed task")

        task_service.update_task_status(task2.id, "running")
        task_service.update_task_status(task3.id, "completed")

        # ステータスフィルタで取得
        scheduled = task_service.list_tasks(status="scheduled")
        running = task_service.list_tasks(status="running")
        completed = task_service.list_tasks(status="completed")

        assert len(scheduled) == 1
        assert len(running) == 1
        assert len(completed) == 1

    def test_update_task_status(self, task_service):
        """タスクステータス更新テスト"""
        task = task_service.create_task("Test task")
        assert task.status == "scheduled"

        # ステータス更新
        task_service.update_task_status(task.id, "running")

        # 確認
        updated_task = task_service.get_task(task.id)
        assert updated_task.status == "running"

    def test_delete_task(self, task_service):
        """タスク削除テスト"""
        task = task_service.create_task("Task to delete")
        assert task_service.get_task(task.id) is not None

        # 削除
        task_service.delete_task(task.id)

        # 確認
        assert task_service.get_task(task.id) is None

    def test_update_nonexistent_task_status(self, task_service):
        """存在しないタスクのステータス更新テスト"""
        # エラーなく実行完了することを確認
        task_service.update_task_status("nonexistent-id", "running")

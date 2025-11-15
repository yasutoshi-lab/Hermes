"""Integration tests for full workflow

これらのテストは実際の依存サービス(Redis, Ollama, SearxNG)を必要とします。
"""

import pytest
from pathlib import Path

from hermes_cli.models.config import HermesConfig
from hermes_cli.services.run_service import RunService
from hermes_cli.services.task_service import TaskService
from hermes_cli.persistence.config_repository import ConfigRepository


# 統合テストは実際のサービスが必要なため、マーカーを付ける
pytestmark = pytest.mark.integration


class TestFullWorkflow:
    """完全なワークフロー統合テスト"""

    @pytest.fixture
    def config(self) -> HermesConfig:
        """実際の設定を読み込み"""
        config_repo = ConfigRepository()
        return config_repo.load()

    @pytest.fixture
    def run_service(self, config: HermesConfig) -> RunService:
        """RunServiceインスタンス"""
        return RunService(config)

    @pytest.fixture
    def task_service(self, config: HermesConfig) -> TaskService:
        """TaskServiceインスタンス"""
        return TaskService(config.work_dir)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_simple_prompt_execution(self, run_service: RunService):
        """シンプルなプロンプトの実行テスト"""
        # シンプルなプロンプトで実行
        prompt = "Pythonの基本的な特徴を3つ挙げてください"

        result = await run_service.execute(
            prompt=prompt,
        )

        # 結果検証
        assert result is not None
        assert result["status"] == "success"
        assert "task_id" in result
        assert "report_path" in result
        assert Path(result["report_path"]).exists()

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_task_based_execution(
        self,
        run_service: RunService,
        task_service: TaskService,
    ):
        """タスクベースの実行テスト"""
        # タスク作成
        prompt = "機械学習の主な種類について説明してください"
        task = task_service.create_task(prompt)

        # タスクID指定で実行
        result = await run_service.execute(task_id=task.id)

        # 結果検証
        assert result is not None
        assert result["status"] == "success"
        assert result["task_id"] == task.id

        # タスクステータス確認
        updated_task = task_service.get_task(task.id)
        assert updated_task.status == "completed"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_workflow_with_validation(self, run_service: RunService):
        """検証ループを含むワークフローテスト"""
        # より複雑なプロンプトで検証ループを発生させる
        prompt = "量子コンピューティングの基本原理と応用分野について詳しく説明してください"

        result = await run_service.execute(prompt=prompt)

        # 結果検証
        assert result is not None
        assert result["status"] == "success"

        # レポートファイルの内容確認
        report_path = Path(result["report_path"])
        assert report_path.exists()

        report_content = report_path.read_text(encoding="utf-8")
        assert len(report_content) > 0
        assert "参考文献" in report_content or "Citations" in report_content

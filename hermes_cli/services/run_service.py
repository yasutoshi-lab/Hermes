"""Run service for Hermes"""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from loguru import logger

from hermes_cli.models.config import HermesConfig
from hermes_cli.models.report import Report, ReportMetadata, ReportSection, Citation
from hermes_cli.services.task_service import TaskService
from hermes_cli.services.history_service import HistoryService
from hermes_cli.agents.graph import create_workflow


class RunService:
    """実行サービス"""

    def __init__(self, config: HermesConfig):
        self.config = config
        self.task_service = TaskService(config.work_dir)
        self.history_service = HistoryService(config.work_dir)

    async def execute(
        self,
        prompt: Optional[str] = None,
        task_id: Optional[str] = None,
        task_all: bool = False,
    ) -> Dict[str, Any]:
        """タスク実行"""
        if task_all:
            # 全タスク実行
            tasks = self.task_service.list_tasks(status="scheduled")
            results = []
            for task in tasks:
                result = await self._execute_single(task.prompt, task.id)
                results.append(result)
            return {"results": results}

        elif task_id:
            # タスクID指定実行
            task = self.task_service.get_task(task_id)
            if not task:
                raise ValueError(f"Task not found: {task_id}")
            return await self._execute_single(task.prompt, task_id)

        elif prompt:
            # 即時実行
            return await self._execute_single(prompt, None)

        else:
            raise ValueError("prompt, task_id, or task_all must be specified")

    async def _execute_single(
        self, prompt: str, task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """単一タスク実行"""
        start_time = datetime.now()

        # タスクID生成
        if not task_id:
            task_id = self.task_service.repository.generate_task_id()

        logger.info(f"Starting task: {task_id}", extra={"category": "RUN"})

        # タスクステータス更新
        if self.task_service.get_task(task_id):
            self.task_service.update_task_status(task_id, "running")

        try:
            # ワークフロー実行
            workflow = create_workflow()

            initial_state = {
                "original_prompt": prompt,
                "config": {
                    "ollama": self.config.ollama.model_dump(),
                    "search": self.config.search.model_dump(),
                    "validation": self.config.validation.model_dump(),
                },
                "start_time": start_time.isoformat(),
            }

            result_state = await workflow.ainvoke(initial_state)

            # レポート作成
            final_report_data = result_state.get("final_report", {})
            report = Report(
                title=final_report_data.get("title", "調査レポート"),
                sections=[
                    ReportSection(**section)
                    for section in final_report_data.get("sections", [])
                ],
                citations=[
                    Citation(**citation)
                    for citation in final_report_data.get("citations", [])
                ],
            )

            # メタデータ作成
            finish_time = datetime.now()
            metadata = ReportMetadata(
                task_id=task_id,
                status="success",
                start_at=start_time,
                finish_at=finish_time,
                duration=(finish_time - start_time).total_seconds(),
                model=self.config.ollama.model,
                loops=result_state.get("validation_loop", 0),
                sources=sum(
                    len(r.get("results", []))
                    for r in result_state.get("search_responses", [])
                ),
            )

            # レポート保存
            self.history_service.save_report(task_id, report, metadata)

            # タスクステータス更新
            if self.task_service.get_task(task_id):
                self.task_service.update_task_status(task_id, "completed")

            logger.info(
                f"Task completed: {task_id}",
                extra={"category": "RUN", "duration": metadata.duration},
            )

            return {
                "task_id": task_id,
                "status": "success",
                "report_path": (
                    self.config.work_dir / "history" / f"report-{task_id}.md"
                ),
                "duration": metadata.duration,
            }

        except Exception as e:
            # エラー処理
            finish_time = datetime.now()
            metadata = ReportMetadata(
                task_id=task_id,
                status="failed",
                start_at=start_time,
                finish_at=finish_time,
                duration=(finish_time - start_time).total_seconds(),
                model=self.config.ollama.model,
                loops=0,
                sources=0,
                error=str(e),
            )

            # タスクステータス更新
            if self.task_service.get_task(task_id):
                self.task_service.update_task_status(task_id, "failed")

            logger.error(
                f"Task failed: {task_id} - {e}", extra={"category": "RUN"}
            )

            raise

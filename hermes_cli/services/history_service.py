"""History service for Hermes"""

from pathlib import Path
from typing import Optional, List, Tuple
import shutil

from hermes_cli.models.report import Report, ReportMetadata
from hermes_cli.persistence.history_repository import HistoryRepository


class HistoryService:
    """履歴管理サービス"""

    def __init__(self, work_dir: Optional[Path] = None):
        self.repository = HistoryRepository(work_dir)

    def save_report(
        self, task_id: str, report: Report, metadata: ReportMetadata
    ) -> None:
        """レポート保存"""
        self.repository.save_report(task_id, report, metadata)

    def get_report(self, task_id: str) -> Optional[Tuple[str, ReportMetadata]]:
        """レポート取得"""
        return self.repository.load_report(task_id)

    def list_histories(self, limit: Optional[int] = None) -> List[ReportMetadata]:
        """履歴一覧"""
        histories = self.repository.list_all()
        if limit:
            return histories[:limit]
        return histories

    def export_report(self, task_id: str, destination: Path) -> bool:
        """レポートエクスポート"""
        result = self.repository.load_report(task_id)
        if not result:
            return False

        markdown, metadata = result

        # ディレクトリ作成
        destination.parent.mkdir(parents=True, exist_ok=True)

        # ファイル書き込み
        with open(destination, "w", encoding="utf-8") as f:
            f.write(markdown)

        return True

    def delete_history(self, task_id: str) -> bool:
        """履歴削除"""
        return self.repository.delete(task_id)

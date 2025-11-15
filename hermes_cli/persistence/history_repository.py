"""History repository for Hermes"""

from pathlib import Path
from typing import List, Optional, Tuple
from loguru import logger

from hermes_cli.models.report import Report, ReportMetadata
from hermes_cli.persistence.file_paths import FilePaths


class HistoryRepository:
    """履歴リポジトリ"""

    def __init__(self, work_dir: Optional[Path] = None):
        self.file_paths = FilePaths(work_dir)

    def save_report(self, task_id: str, report: Report, metadata: ReportMetadata) -> None:
        """レポート保存"""
        self.file_paths.ensure_directories()

        # Markdownファイル
        md_file = self.file_paths.history_dir / f"report-{task_id}.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(report.to_markdown())

        # メタデータファイル
        meta_file = self.file_paths.history_dir / f"report-{task_id}.meta.yaml"
        with open(meta_file, "w", encoding="utf-8") as f:
            f.write(metadata.to_yaml())

        logger.info(
            f"Report saved: {task_id}", extra={"category": "RUN"}
        )

    def load_report(self, task_id: str) -> Optional[Tuple[str, ReportMetadata]]:
        """レポート読み込み"""
        md_file = self.file_paths.history_dir / f"report-{task_id}.md"
        meta_file = self.file_paths.history_dir / f"report-{task_id}.meta.yaml"

        if not md_file.exists() or not meta_file.exists():
            return None

        try:
            with open(md_file, "r", encoding="utf-8") as f:
                markdown = f.read()

            with open(meta_file, "r", encoding="utf-8") as f:
                import yaml
                metadata = ReportMetadata(**yaml.safe_load(f))

            return markdown, metadata
        except Exception as e:
            logger.error(
                f"Failed to load report {task_id}: {e}",
                extra={"category": "RUN"},
            )
            return None

    def list_all(self) -> List[ReportMetadata]:
        """全履歴一覧"""
        histories = []
        if not self.file_paths.history_dir.exists():
            return histories

        for meta_file in self.file_paths.history_dir.glob("*.meta.yaml"):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    import yaml
                    metadata = ReportMetadata(**yaml.safe_load(f))
                    histories.append(metadata)
            except Exception as e:
                logger.warning(
                    f"Failed to load metadata {meta_file}: {e}",
                    extra={"category": "RUN"},
                )

        return sorted(histories, key=lambda h: h.start_at, reverse=True)

    def delete(self, task_id: str) -> bool:
        """履歴削除"""
        md_file = self.file_paths.history_dir / f"report-{task_id}.md"
        meta_file = self.file_paths.history_dir / f"report-{task_id}.meta.yaml"

        deleted = False
        if md_file.exists():
            md_file.unlink()
            deleted = True
        if meta_file.exists():
            meta_file.unlink()
            deleted = True

        if deleted:
            logger.info(f"History deleted: {task_id}", extra={"category": "RUN"})

        return deleted

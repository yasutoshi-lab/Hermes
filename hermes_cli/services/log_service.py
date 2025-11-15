"""Log service for Hermes"""

from pathlib import Path
from typing import Optional, List, Iterator
from loguru import logger

from hermes_cli.persistence.log_repository import LogRepository


class LogService:
    """ログ管理サービス"""

    def __init__(self, work_dir: Optional[Path] = None):
        self.repository = LogRepository(work_dir)

    def read_logs(
        self,
        lines: int = 50,
        debug: bool = False,
        follow: bool = False,
        task_id: Optional[str] = None,
    ) -> Iterator[str]:
        """ログ読み込み"""
        if task_id:
            # タスクIDでフィルタ
            filtered_lines = self.repository.filter_by_task_id(task_id, debug)
            for line in filtered_lines[-lines:]:
                yield line
        else:
            # 通常読み込み
            yield from self.repository.read_log_lines(lines, debug, follow)

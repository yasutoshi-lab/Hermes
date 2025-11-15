"""Log repository for Hermes"""

from pathlib import Path
from typing import Optional, List, Iterator
from loguru import logger as loguru_logger

from hermes_cli.persistence.file_paths import FilePaths


class LogRepository:
    """ログリポジトリ"""

    def __init__(self, work_dir: Optional[Path] = None):
        self.file_paths = FilePaths(work_dir)

    def get_latest_log_file(self, debug: bool = False) -> Optional[Path]:
        """最新のログファイル取得"""
        log_dir = self.file_paths.debug_log_dir if debug else self.file_paths.log_dir

        if not log_dir.exists():
            return None

        log_files = sorted(log_dir.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
        return log_files[0] if log_files else None

    def read_log_lines(
        self, lines: int = 50, debug: bool = False, follow: bool = False
    ) -> Iterator[str]:
        """ログ行読み込み"""
        log_file = self.get_latest_log_file(debug)
        if not log_file:
            return

        if follow:
            # tail -f 相当
            import time
            with open(log_file, "r", encoding="utf-8") as f:
                # 既存行をスキップ
                f.seek(0, 2)  # ファイル末尾へ
                while True:
                    line = f.readline()
                    if line:
                        yield line.rstrip()
                    else:
                        time.sleep(0.1)
        else:
            # 最後のN行を読む
            with open(log_file, "r", encoding="utf-8") as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    yield line.rstrip()

    def filter_by_task_id(self, task_id: str, debug: bool = False) -> List[str]:
        """タスクIDでフィルタ"""
        log_file = self.get_latest_log_file(debug)
        if not log_file:
            return []

        filtered = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if task_id in line:
                    filtered.append(line.rstrip())

        return filtered

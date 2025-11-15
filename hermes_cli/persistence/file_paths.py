"""File path definitions for Hermes"""

from pathlib import Path
from typing import Optional


class FilePaths:
    """ファイルパス管理"""

    def __init__(self, work_dir: Optional[Path] = None):
        self.work_dir = work_dir or Path.home() / ".hermes"

    @property
    def config_file(self) -> Path:
        """設定ファイルパス"""
        return self.work_dir / "config.yaml"

    @property
    def docker_compose_file(self) -> Path:
        """docker-compose.yamlパス"""
        return self.work_dir / "docker-compose.yaml"

    @property
    def cache_dir(self) -> Path:
        """キャッシュディレクトリ"""
        return self.work_dir / "cache"

    @property
    def task_dir(self) -> Path:
        """タスクディレクトリ"""
        return self.work_dir / "task"

    @property
    def log_dir(self) -> Path:
        """ログディレクトリ"""
        return self.work_dir / "log"

    @property
    def debug_log_dir(self) -> Path:
        """デバッグログディレクトリ"""
        return self.work_dir / "debug_log"

    @property
    def history_dir(self) -> Path:
        """履歴ディレクトリ"""
        return self.work_dir / "history"

    @property
    def searxng_dir(self) -> Path:
        """SearxNG設定ディレクトリ"""
        return self.work_dir / "searxng"

    def ensure_directories(self) -> None:
        """ディレクトリ作成"""
        directories = [
            self.work_dir,
            self.cache_dir,
            self.task_dir,
            self.log_dir,
            self.debug_log_dir,
            self.history_dir,
            self.searxng_dir,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

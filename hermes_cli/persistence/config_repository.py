"""Configuration repository for Hermes"""

from pathlib import Path
from typing import Optional
from loguru import logger

from hermes_cli.models.config import HermesConfig
from hermes_cli.persistence.file_paths import FilePaths


class ConfigRepository:
    """設定リポジトリ"""

    def __init__(self, work_dir: Optional[Path] = None):
        self.file_paths = FilePaths(work_dir)

    def load(self) -> HermesConfig:
        """設定読み込み"""
        config_path = self.file_paths.config_file

        if not config_path.exists():
            logger.warning(
                f"Config not found, using defaults: {config_path}",
                extra={"category": "CONFIG"},
            )
            return HermesConfig(work_dir=self.file_paths.work_dir)

        try:
            config = HermesConfig.load_from_yaml(config_path)
            logger.info(
                f"Config loaded: {config_path}", extra={"category": "CONFIG"}
            )
            return config
        except Exception as e:
            logger.error(
                f"Failed to load config: {e}", extra={"category": "CONFIG"}
            )
            raise

    def save(self, config: HermesConfig) -> None:
        """設定保存"""
        config_path = self.file_paths.config_file
        self.file_paths.ensure_directories()

        try:
            config.save_to_yaml(config_path)
            logger.info(
                f"Config saved: {config_path}", extra={"category": "CONFIG"}
            )
        except Exception as e:
            logger.error(
                f"Failed to save config: {e}", extra={"category": "CONFIG"}
            )
            raise

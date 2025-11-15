"""Configuration service for Hermes"""

from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from hermes_cli.models.config import HermesConfig
from hermes_cli.persistence.config_repository import ConfigRepository


class ConfigService:
    """設定管理サービス"""

    def __init__(self, work_dir: Optional[Path] = None):
        self.repository = ConfigRepository(work_dir)

    def load(self) -> HermesConfig:
        """設定読み込み"""
        return self.repository.load()

    def save(self, config: HermesConfig) -> None:
        """設定保存"""
        self.repository.save(config)

    @staticmethod
    def merge_with_cli_args(config: HermesConfig, cli_args: Dict[str, Any]) -> HermesConfig:
        """CLIオプションとマージ"""
        # CLIオプションが指定されている場合は上書き
        if cli_args.get("model"):
            config.ollama.model = cli_args["model"]
        if cli_args.get("api"):
            config.ollama.api_url = cli_args["api"]
        if cli_args.get("language"):
            config.language = cli_args["language"]
        if cli_args.get("min_validation") is not None:
            config.validation.min_validation = cli_args["min_validation"]
        if cli_args.get("max_validation") is not None:
            config.validation.max_validation = cli_args["max_validation"]
        if cli_args.get("min_search") is not None:
            config.search.min_search = cli_args["min_search"]
        if cli_args.get("max_search") is not None:
            config.search.max_search = cli_args["max_search"]
        if cli_args.get("query") is not None:
            config.search.query_count = cli_args["query"]
        if cli_args.get("retry") is not None:
            config.ollama.retry = cli_args["retry"]

        return config

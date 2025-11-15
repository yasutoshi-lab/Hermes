"""Logging setup for Hermes"""

from loguru import logger
from pathlib import Path
import sys

from hermes_cli.models.config import HermesConfig


def setup_logging(config: HermesConfig):
    """ロギング設定"""

    # デフォルトハンドラー削除
    logger.remove()

    # コンソール出力
    logger.add(
        sys.stderr,
        format=config.logging.format,
        level=config.logging.level,
        colorize=True,
    )

    # 通常ログファイル
    log_file = config.work_dir / "log" / "hermes.{time:YYYY-MM-DD}.log"
    logger.add(
        log_file,
        format=config.logging.format,
        level="INFO",
        rotation=config.logging.rotation,
        retention=config.logging.retention,
        encoding="utf-8",
    )

    # デバッグログファイル
    debug_file = config.work_dir / "debug_log" / "debug.{time:YYYY-MM-DD}.log"
    logger.add(
        debug_file,
        format="{time:YYYY-MM-DDTHH:mm:ss.SSSSSSZ} [{level}] [{name}:{function}:{line}] {message}",
        level="DEBUG",
        rotation=config.logging.rotation,
        retention=config.logging.retention,
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
    )

    # カテゴリをコンテキストに追加
    logger.configure(extra={"category": "SYSTEM"})

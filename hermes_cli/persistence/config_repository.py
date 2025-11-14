"""Configuration file persistence for Hermes.

This module handles reading and writing the config.yaml file,
with type-safe dataclasses for all configuration sections.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict
import yaml


@dataclass
class OllamaConfig:
    """Ollama API configuration.

    Attributes:
        api_base: Base URL for Ollama API
        model: Model name to use
        retry: Number of retry attempts for failed requests
        timeout_sec: Request timeout in seconds
    """
    api_base: str
    model: str
    retry: int
    timeout_sec: int


@dataclass
class ValidationConfig:
    """Validation loop configuration.

    Attributes:
        min_loops: Minimum number of validation loops
        max_loops: Maximum number of validation loops
    """
    min_loops: int
    max_loops: int


@dataclass
class SearchConfig:
    """Web search configuration.

    Attributes:
        min_sources: Minimum number of sources to collect
        max_sources: Maximum number of sources to collect
    """
    min_sources: int
    max_sources: int


@dataclass
class LoggingConfig:
    """Logging configuration.

    Attributes:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for regular logs
        debug_log_dir: Directory for debug logs
    """
    level: str
    log_dir: str
    debug_log_dir: str


@dataclass
class Config:
    """Complete Hermes configuration.

    Attributes:
        ollama: Ollama API settings
        language: Default output language ("ja" or "en")
        validation: Validation loop settings
        search: Web search settings
        logging: Logging settings
        cli: CLI-specific settings (history_limit, etc.)
    """
    ollama: OllamaConfig
    language: str
    validation: ValidationConfig
    search: SearchConfig
    logging: LoggingConfig
    cli: Dict[str, Any]


class ConfigRepository:
    """Handles configuration file persistence.

    Provides methods to load, save, and create default configurations
    for the Hermes system.
    """

    def load(self, config_path: Path) -> Config:
        """Load config from YAML file.

        Args:
            config_path: Path to config.yaml file

        Returns:
            Config object with loaded settings

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is malformed
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return Config(
            ollama=OllamaConfig(**data['ollama']),
            language=data['language'],
            validation=ValidationConfig(**data['validation']),
            search=SearchConfig(**data['search']),
            logging=LoggingConfig(**data['logging']),
            cli=data.get('cli', {}),
        )

    def save(self, config: Config, config_path: Path) -> None:
        """Save config to YAML file.

        Args:
            config: Config object to save
            config_path: Path where config.yaml should be written
        """
        data = {
            'ollama': asdict(config.ollama),
            'language': config.language,
            'validation': asdict(config.validation),
            'search': asdict(config.search),
            'logging': asdict(config.logging),
            'cli': config.cli,
        }

        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    def create_default(self) -> Config:
        """Create default configuration.

        Returns:
            Config object with default values from design specification
        """
        return Config(
            ollama=OllamaConfig(
                api_base="http://localhost:11434/api/chat",
                model="gpt-oss:20b",
                retry=3,
                timeout_sec=60,
            ),
            language="ja",
            validation=ValidationConfig(
                min_loops=1,
                max_loops=3,
            ),
            search=SearchConfig(
                min_sources=3,
                max_sources=8,
            ),
            logging=LoggingConfig(
                level="INFO",
                log_dir="~/.hermes/log",
                debug_log_dir="~/.hermes/debug_log",
            ),
            cli={
                "history_limit": 100,
            },
        )

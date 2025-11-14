"""Configuration service for Hermes.

This module provides high-level configuration management operations,
including loading, saving, resetting, and applying CLI overrides.
"""

from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import replace
import logging

from hermes_cli.persistence.file_paths import FilePaths
from hermes_cli.persistence.config_repository import (
    Config,
    ConfigRepository,
    OllamaConfig,
    ValidationConfig,
    SearchConfig,
    LoggingConfig,
)


class ConfigService:
    """Service for managing application configuration."""

    def __init__(self, file_paths: Optional[FilePaths] = None):
        """
        Initialize config service.

        Args:
            file_paths: File path manager (uses default if not provided)
        """
        self.file_paths = file_paths or FilePaths()
        self.repository = ConfigRepository()
        self.logger = logging.getLogger(__name__)

    def load(self) -> Config:
        """
        Load configuration from file.

        Returns:
            Loaded configuration

        Notes:
            - Creates default config if file doesn't exist
            - Returns default config if file is corrupted
        """
        config_path = self.file_paths.config_file

        if not config_path.exists():
            self.logger.info("Config file not found, creating default")
            config = self.repository.create_default()
            self.save(config)
            return config

        try:
            config = self.repository.load(config_path)
            self.logger.info("Configuration loaded successfully")
            return config
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}, using default")
            return self.repository.create_default()

    def save(self, config: Config) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration to save
        """
        self.file_paths.ensure_directories()
        config_path = self.file_paths.config_file
        self.repository.save(config, config_path)
        self.logger.info("Configuration saved")

    def reset_to_default(self) -> Config:
        """
        Reset configuration to default values.

        Returns:
            Default configuration
        """
        config = self.repository.create_default()
        self.save(config)
        self.logger.info("Configuration reset to default")
        return config

    def apply_overrides(self, config: Config, overrides: Dict[str, Any]) -> Config:
        """
        Apply CLI option overrides to configuration.

        Args:
            config: Base configuration
            overrides: Dictionary of override values
                      Keys: 'api', 'model', 'retry', 'timeout', 'language',
                           'min_validation', 'max_validation', 'query_count',
                           'min_sources', 'max_sources'

        Returns:
            Configuration with overrides applied (does not modify original)

        Example:
            overrides = {
                'api': 'http://localhost:11434/api/chat',
                'model': 'gpt-oss:20b',
                'language': 'ja',
                'query_count': 5,
            }
        """
        # Start with copies of nested configs
        ollama_config = replace(config.ollama)
        validation_config = replace(config.validation)
        search_config = replace(config.search)

        # Apply overrides to nested configs
        if 'api' in overrides and overrides['api'] is not None:
            ollama_config = replace(ollama_config, api_base=overrides['api'])

        if 'model' in overrides and overrides['model'] is not None:
            ollama_config = replace(ollama_config, model=overrides['model'])

        if 'retry' in overrides and overrides['retry'] is not None:
            ollama_config = replace(ollama_config, retry=overrides['retry'])

        if 'timeout' in overrides and overrides['timeout'] is not None:
            ollama_config = replace(ollama_config, timeout_sec=overrides['timeout'])

        if 'min_validation' in overrides and overrides['min_validation'] is not None:
            validation_config = replace(validation_config, min_loops=overrides['min_validation'])

        if 'max_validation' in overrides and overrides['max_validation'] is not None:
            validation_config = replace(validation_config, max_loops=overrides['max_validation'])

        if 'min_sources' in overrides and overrides['min_sources'] is not None:
            search_config = replace(search_config, min_sources=overrides['min_sources'])

        if 'max_sources' in overrides and overrides['max_sources'] is not None:
            search_config = replace(search_config, max_sources=overrides['max_sources'])

        # Apply language override
        language = config.language
        if 'language' in overrides and overrides['language'] is not None:
            language = overrides['language']

        # Create new config with overridden values
        new_config = Config(
            ollama=ollama_config,
            language=language,
            validation=validation_config,
            search=search_config,
            logging=config.logging,  # Logging config not overridable via CLI
            cli=config.cli,
        )

        return new_config

    def get_ollama_config(self, config: Config) -> OllamaConfig:
        """
        Extract Ollama-specific configuration.

        Args:
            config: Full configuration

        Returns:
            Ollama configuration object
        """
        return config.ollama

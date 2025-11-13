"""
Configuration settings for Hermes Research Agent.

This module defines default configuration values for the research analyst agent system.
All settings can be overridden via environment variables or CLI arguments.
"""

import os
from pathlib import Path
from typing import Literal
try:
    from pydantic import BaseSettings, Field
except Exception:  # pragma: no cover - fallback for pydantic>=2
    from pydantic import Field
    from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Model Configuration
    default_model: str = Field(
        default="gpt-oss:20b",
        description="Default Ollama model to use for LLM operations"
    )

    ollama_api_endpoint: str = Field(
        default="http://localhost:11434",
        description="Ollama API endpoint URL"
    )

    # Language Configuration
    default_language: Literal["ja", "en"] = Field(
        default="ja",
        description="Default language for input/output (ja=Japanese, en=English)"
    )

    # Session Storage
    session_storage_path: Path = Field(
        default_factory=lambda: Path.cwd() / "sessions",
        description="Directory path for storing session history"
    )

    # MCP Server Endpoints
    web_search_mcp_endpoint: str = Field(
        default="http://localhost:3000",
        description="Web Search MCP server endpoint"
    )

    container_use_mcp_endpoint: str = Field(
        default="http://localhost:3001",
        description="Container Use MCP server endpoint"
    )

    # Search Configuration
    default_search_limit: int = Field(
        default=5,
        description="Default number of search results to retrieve"
    )

    # Processing Configuration
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed operations"
    )

    timeout_seconds: int = Field(
        default=300,
        description="Default timeout for long-running operations (in seconds)"
    )

    # Verification Configuration
    verification_max_loops: int = Field(
        default=2,
        description="Maximum number of verification iterations before forcing report"
    )

    verification_pass_ratio: float = Field(
        default=0.8,
        description="Minimum ratio of passing claims required to skip re-search"
    )

    verification_min_confidence: float = Field(
        default=0.5,
        description="Minimum average confidence required to skip re-search"
    )

    verification_claim_pass_threshold: float = Field(
        default=0.65,
        description="Per-claim support score threshold to mark as PASS"
    )

    verification_claim_review_threshold: float = Field(
        default=0.4,
        description="Per-claim support score threshold to request review instead of fail"
    )

    verification_search_limit: int = Field(
        default=3,
        description="Number of snippets fetched per claim during verification search"
    )

    verification_max_claims: int = Field(
        default=5,
        description="Maximum number of claims to evaluate per verification loop"
    )

    # Report Generation
    report_format: Literal["markdown", "pdf", "both"] = Field(
        default="markdown",
        description="Default format for generated reports"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    log_file_path: Path = Field(
        default_factory=lambda: Path.cwd() / "logs" / "hermes.log",
        description="Path to log file"
    )

    class Config:
        env_prefix = "HERMES_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the current application settings."""
    return settings


def update_settings(**kwargs) -> None:
    """Update settings dynamically."""
    global settings
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)


# Ensure session storage and log directories exist
settings.session_storage_path.mkdir(parents=True, exist_ok=True)
settings.log_file_path.parent.mkdir(parents=True, exist_ok=True)

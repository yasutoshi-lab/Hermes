"""
Configuration management for Hermes backend API.
Uses pydantic-settings for environment variable management.
"""
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application settings
    APP_NAME: str = "Hermes API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False

    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Database settings
    POSTGRES_USER: str = Field(default="hermes", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(default="hermes_password", description="PostgreSQL password")
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")
    POSTGRES_DB: str = Field(default="hermes_db", description="PostgreSQL database name")

    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # JWT Authentication settings
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token generation"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Ollama settings
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL"
    )
    OLLAMA_DEFAULT_MODEL: str = Field(
        default="gpt-oss:20b",
        description="Default Ollama model for summarization"
    )
    OLLAMA_TIMEOUT: int = Field(default=300, description="Ollama request timeout in seconds")

    # Web Search MCP settings
    WEB_SEARCH_MCP_URL: str = Field(
        default="http://localhost:8001",
        description="Web Search MCP server URL"
    )

    # Container Use settings
    CONTAINER_USE_ENABLED: bool = Field(
        default=True,
        description="Enable Container Use for isolated task execution"
    )
    CONTAINER_BASE_IMAGE: str = "ubuntu:24.04"

    # File storage settings
    UPLOAD_DIR: str = Field(default="./uploads", description="Directory for uploaded files")
    MAX_UPLOAD_SIZE: int = Field(default=50 * 1024 * 1024, description="Max upload size in bytes (50MB)")
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt"]

    # Task scheduler settings
    SCHEDULER_ENABLED: bool = True
    MAX_CONCURRENT_TASKS: int = Field(default=3, description="Maximum concurrent task executions")
    TASK_RETRY_ATTEMPTS: int = Field(default=3, description="Number of retry attempts for failed tasks")

    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR")
    LOG_FORMAT: str = "json"  # "json" or "text"
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path (None for stdout only)")

    # WebSocket settings
    WEBSOCKET_HEARTBEAT_INTERVAL: int = Field(
        default=30,
        description="WebSocket heartbeat interval in seconds"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency for FastAPI to get settings."""
    return settings

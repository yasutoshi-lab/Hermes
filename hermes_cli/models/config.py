"""Configuration models for Hermes"""

from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, Literal
from pathlib import Path


class OllamaConfig(BaseModel):
    """Ollama API設定"""

    api_url: str = Field(
        default="http://localhost:11434/api/chat", description="Ollama APIエンドポイント"
    )
    model: str = Field(default="gpt-oss:20b", description="使用するLLMモデル")
    timeout: int = Field(default=120, ge=10, le=600, description="タイムアウト秒")
    retry: int = Field(default=3, ge=0, le=10, description="リトライ回数")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=128, le=32768)


class SearchConfig(BaseModel):
    """検索設定"""

    searxng_base_url: str = Field(
        default="http://localhost:8080", description="SearxNGベースURL"
    )
    redis_url: str = Field(default="redis://localhost:6379/0", description="RedisベースURL")
    min_search: int = Field(default=3, ge=1, le=20, description="最小ソース数")
    max_search: int = Field(default=8, ge=1, le=50, description="最大ソース数")
    query_count: int = Field(default=3, ge=1, le=10, description="クエリ生成数")
    cache_ttl: int = Field(default=3600, description="キャッシュTTL(秒)")


class ValidationConfig(BaseModel):
    """検証設定"""

    min_validation: int = Field(default=1, ge=0, le=10)
    max_validation: int = Field(default=3, ge=0, le=10)

    @field_validator("max_validation")
    @classmethod
    def validate_max(cls, v: int, info) -> int:
        if "min_validation" in info.data and v < info.data["min_validation"]:
            raise ValueError("max_validation must be >= min_validation")
        return v


class BrowserConfig(BaseModel):
    """ブラウザ設定"""

    headless: bool = Field(default=True, description="ヘッドレスモード")
    stealth_mode: bool = Field(default=True, description="ステルスモード")
    timeout: int = Field(default=30, ge=5, le=180)
    user_agent: Optional[str] = None


class LoggingConfig(BaseModel):
    """ロギング設定"""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    format: str = "{time:YYYY-MM-DDTHH:mm:ss.SSSSSSZ} [{level}] [{extra[category]}] {message}"
    rotation: str = "1 day"
    retention: str = "30 days"


class LangfuseConfig(BaseModel):
    """Langfuse設定 (オプション)"""

    enabled: bool = False
    base_url: Optional[str] = "https://cloud.langfuse.com"
    public_key: Optional[str] = None
    secret_key: Optional[str] = None


class HermesConfig(BaseModel):
    """Hermes全体設定"""

    work_dir: Path = Field(default=Path.home() / ".hermes")
    language: Literal["ja", "en"] = "ja"

    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    langfuse: LangfuseConfig = Field(default_factory=LangfuseConfig)

    class Config:
        use_enum_values = True

    def save_to_yaml(self, path: Path) -> None:
        """YAMLファイルに保存"""
        import yaml

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                self.model_dump(mode="json", exclude_none=True),
                f,
                allow_unicode=True,
                default_flow_style=False,
            )

    @classmethod
    def load_from_yaml(cls, path: Path) -> "HermesConfig":
        """YAMLファイルから読み込み"""
        import yaml

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**data)

"""Pytest configuration and fixtures"""

import pytest
import asyncio
from pathlib import Path
from typing import Generator
import tempfile
import shutil

from hermes_cli.models.config import (
    HermesConfig,
    OllamaConfig,
    SearchConfig,
    ValidationConfig,
    LangfuseConfig,
    LoggingConfig,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """セッションスコープのイベントループ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_work_dir() -> Generator[Path, None, None]:
    """一時作業ディレクトリ"""
    temp_dir = Path(tempfile.mkdtemp(prefix="hermes_test_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_config(temp_work_dir: Path) -> HermesConfig:
    """テスト用設定"""
    return HermesConfig(
        work_dir=temp_work_dir,
        language="ja",
        ollama=OllamaConfig(
            api_url="http://localhost:11434/api/chat",
            model="gpt-oss:20b",
            temperature=0.7,
            max_tokens=4096,
            timeout=120,
            retry=3,
        ),
        search=SearchConfig(
            searxng_base_url="http://localhost:8080",
            redis_url="redis://localhost:6379/0",
            cache_ttl=3600,
            query_count=3,
            min_search=3,
            max_search=8,
        ),
        validation=ValidationConfig(
            min_validation=1,
            max_validation=3,
        ),
        langfuse=LangfuseConfig(
            enabled=False,
            host="http://localhost:3000",
            public_key=None,
            secret_key=None,
        ),
        logging=LoggingConfig(
            level="INFO",
            format="{time:YYYY-MM-DDTHH:mm:ss.SSSSSSZ} [{level}] [{extra[category]}] {message}",
            rotation="1 day",
            retention="30 days",
        ),
    )


@pytest.fixture
def mock_ollama_response():
    """モックOllamaレスポンス"""
    return {
        "model": "gpt-oss:20b",
        "created_at": "2024-01-01T00:00:00Z",
        "message": {
            "role": "assistant",
            "content": "Test response from Ollama",
        },
        "done": True,
    }


@pytest.fixture
def mock_search_response():
    """モック検索レスポンス"""
    return {
        "query": "test query",
        "results": [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "content": "Test content 1",
                "engine": "google",
            },
            {
                "title": "Test Result 2",
                "url": "https://example.com/2",
                "content": "Test content 2",
                "engine": "bing",
            },
        ],
    }


@pytest.fixture
def sample_task_data():
    """サンプルタスクデータ"""
    return {
        "id": "2024-0001",
        "prompt": "Test prompt",
        "status": "scheduled",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
    }


@pytest.fixture
def sample_report_data():
    """サンプルレポートデータ"""
    return {
        "title": "Test Report",
        "sections": [
            {
                "heading": "Section 1",
                "content": "Content 1",
            }
        ],
        "citations": [
            {
                "number": 1,
                "title": "Source 1",
                "url": "https://example.com/1",
            }
        ],
    }

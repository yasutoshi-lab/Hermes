"""Unit tests for SearxNGClient"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from hermes_cli.tools.container_use_client import SearxNGClient


class TestSearxNGClient:
    """SearxNGClientのテスト"""

    @pytest.fixture
    def searxng_client(self, test_config):
        """SearxNGClientインスタンス"""
        return SearxNGClient(
            searxng_url=test_config.search.searxng_base_url,
            redis_url=test_config.search.redis_url,
            cache_ttl=test_config.search.cache_ttl,
        )

    @pytest.mark.asyncio
    async def test_init(self, searxng_client, test_config):
        """初期化テスト"""
        assert searxng_client.searxng_url == test_config.search.searxng_base_url
        assert searxng_client.cache_ttl == test_config.search.cache_ttl

    @pytest.mark.asyncio
    async def test_search_success(self, searxng_client, mock_search_response):
        """正常な検索テスト"""
        with patch("httpx.AsyncClient.get") as mock_get:
            # モックレスポンス設定
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = AsyncMock(return_value=mock_search_response)
            mock_get.return_value = mock_response

            # Redisキャッシュをモック
            with patch("redis.Redis.get", return_value=None):
                with patch("redis.Redis.set"):
                    # テスト実行
                    results = await searxng_client.search("test query")

                    # 検証
                    assert results is not None
                    assert len(results) == 2
                    assert results[0]["title"] == "Test Result 1"
                    assert results[1]["title"] == "Test Result 2"
                    mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_with_cache(self, searxng_client, mock_search_response):
        """キャッシュヒット時の検索テスト"""
        cached_data = json.dumps(mock_search_response)

        with patch("redis.Redis.get", return_value=cached_data):
            with patch("httpx.AsyncClient.get") as mock_get:
                # テスト実行
                results = await searxng_client.search("test query")

                # 検証
                assert results is not None
                assert len(results) == 2
                # キャッシュヒットしたのでHTTPリクエストは呼ばれない
                mock_get.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_failure(self, searxng_client):
        """検索失敗テスト"""
        with patch("httpx.AsyncClient.get") as mock_get:
            # エラーレスポンス設定
            mock_get.side_effect = Exception("Connection error")

            # Redisキャッシュをモック
            with patch("redis.Redis.get", return_value=None):
                # テスト実行
                results = await searxng_client.search("test query")

                # 検証
                assert results == []
                mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_empty_results(self, searxng_client):
        """空の検索結果テスト"""
        with patch("httpx.AsyncClient.get") as mock_get:
            # 空の結果
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json = AsyncMock(return_value={"query": "test", "results": []})
            mock_get.return_value = mock_response

            # Redisキャッシュをモック
            with patch("redis.Redis.get", return_value=None):
                with patch("redis.Redis.set"):
                    # テスト実行
                    results = await searxng_client.search("test query")

                    # 検証
                    assert results == []
                    mock_get.assert_called_once()

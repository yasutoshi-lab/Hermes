"""Unit tests for Agent Nodes"""

import pytest
from unittest.mock import AsyncMock, patch

from hermes_cli.agents.state import WorkflowState
from hermes_cli.agents.nodes.prompt_normalizer import normalize_prompt
from hermes_cli.agents.nodes.query_generator import generate_queries


class TestPromptNormalizer:
    """PromptNormalizerノードのテスト"""

    @pytest.mark.asyncio
    async def test_normalize_prompt_basic(self, test_config):
        """基本的なプロンプト正規化テスト"""
        state: WorkflowState = {
            "original_prompt": "  Test prompt with extra spaces  ",
            "config": test_config.model_dump(),
        }

        result = await normalize_prompt(state)

        assert "normalized_prompt" in result
        assert result["normalized_prompt"] == "Test prompt with extra spaces"
        assert result["original_prompt"] == state["original_prompt"]

    @pytest.mark.asyncio
    async def test_normalize_prompt_empty(self, test_config):
        """空プロンプトの正規化テスト"""
        state: WorkflowState = {
            "original_prompt": "",
            "config": test_config.model_dump(),
        }

        result = await normalize_prompt(state)

        assert "normalized_prompt" in result
        assert result["normalized_prompt"] == ""

    @pytest.mark.asyncio
    async def test_normalize_prompt_with_newlines(self, test_config):
        """改行を含むプロンプトの正規化テスト"""
        state: WorkflowState = {
            "original_prompt": "Line 1\n\nLine 2\n\n\nLine 3",
            "config": test_config.model_dump(),
        }

        result = await normalize_prompt(state)

        assert "normalized_prompt" in result
        # 改行が適切に処理されているか確認
        assert "\n" in result["normalized_prompt"]


class TestQueryGenerator:
    """QueryGeneratorノードのテスト"""

    @pytest.mark.asyncio
    async def test_generate_queries_success(self, test_config, mock_ollama_response):
        """正常なクエリ生成テスト"""
        state: WorkflowState = {
            "normalized_prompt": "Test prompt for query generation",
            "config": {
                "ollama": test_config.ollama.model_dump(),
                "search": test_config.search.model_dump(),
            },
        }

        # Ollamaクライアントをモック
        with patch("hermes_cli.tools.ollama_client.OllamaClient.generate") as mock_generate:
            mock_generate.return_value = {
                "content": "query1\nquery2\nquery3",
                "done": True,
            }

            result = await generate_queries(state)

            assert "queries" in result
            assert isinstance(result["queries"], list)
            assert len(result["queries"]) > 0

    @pytest.mark.asyncio
    async def test_generate_queries_empty_prompt(self, test_config):
        """空プロンプトでのクエリ生成テスト"""
        state: WorkflowState = {
            "normalized_prompt": "",
            "config": {
                "ollama": test_config.ollama.model_dump(),
                "search": test_config.search.model_dump(),
            },
        }

        with patch("hermes_cli.tools.ollama_client.OllamaClient.generate") as mock_generate:
            mock_generate.return_value = None

            result = await generate_queries(state)

            # エラーハンドリングされているか確認
            assert "queries" in result or "errors" in result

    @pytest.mark.asyncio
    async def test_generate_queries_with_limit(self, test_config):
        """クエリ数制限テスト"""
        state: WorkflowState = {
            "normalized_prompt": "Generate multiple queries",
            "config": {
                "ollama": test_config.ollama.model_dump(),
                "search": {
                    **test_config.search.model_dump(),
                    "query_count": 2,  # 最大2クエリ
                },
            },
        }

        with patch("hermes_cli.tools.ollama_client.OllamaClient.generate") as mock_generate:
            # 5つのクエリを生成するレスポンス
            mock_generate.return_value = {
                "content": "query1\nquery2\nquery3\nquery4\nquery5",
                "done": True,
            }

            result = await generate_queries(state)

            assert "queries" in result
            # query_countで制限されているか確認
            assert len(result["queries"]) <= state["config"]["search"]["query_count"]

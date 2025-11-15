"""Unit tests for LangfuseClient"""

import pytest
from unittest.mock import MagicMock, patch

from hermes_cli.tools.langfuse_client import LangfuseClient


class TestLangfuseClient:
    """LangfuseClientのテスト"""

    @pytest.fixture
    def langfuse_client_disabled(self):
        """無効化されたLangfuseClient"""
        return LangfuseClient(
            enabled=False,
            host="http://localhost:3000",
            public_key=None,
            secret_key=None,
        )

    @pytest.fixture
    def langfuse_client_enabled(self):
        """有効化されたLangfuseClient"""
        with patch("langfuse.Langfuse") as mock_langfuse:
            mock_instance = MagicMock()
            mock_langfuse.return_value = mock_instance

            client = LangfuseClient(
                enabled=True,
                host="http://localhost:3000",
                public_key="test_public_key",
                secret_key="test_secret_key",
            )
            client.client = mock_instance
            return client

    def test_init_disabled(self, langfuse_client_disabled):
        """無効化時の初期化テスト"""
        assert langfuse_client_disabled.enabled is False
        assert langfuse_client_disabled.client is None

    def test_init_enabled(self, langfuse_client_enabled):
        """有効化時の初期化テスト"""
        assert langfuse_client_enabled.enabled is True
        assert langfuse_client_enabled.client is not None

    def test_create_trace_disabled(self, langfuse_client_disabled):
        """無効化時のトレース作成テスト"""
        result = langfuse_client_disabled.create_trace(
            name="test-trace",
            metadata={"test": "data"},
        )
        assert result is None

    def test_create_trace_enabled(self, langfuse_client_enabled):
        """有効化時のトレース作成テスト"""
        mock_trace = MagicMock()
        langfuse_client_enabled.client.trace.return_value = mock_trace

        result = langfuse_client_enabled.create_trace(
            name="test-trace",
            metadata={"test": "data"},
            input_data={"prompt": "test"},
        )

        assert result is not None
        assert langfuse_client_enabled.current_trace == mock_trace
        langfuse_client_enabled.client.trace.assert_called_once()

    def test_update_trace_disabled(self, langfuse_client_disabled):
        """無効化時のトレース更新テスト"""
        # エラーなく実行完了することを確認
        langfuse_client_disabled.update_trace(
            output_data={"result": "test"},
        )

    def test_update_trace_enabled(self, langfuse_client_enabled):
        """有効化時のトレース更新テスト"""
        mock_trace = MagicMock()
        langfuse_client_enabled.current_trace = mock_trace

        langfuse_client_enabled.update_trace(
            output_data={"result": "test"},
            metadata={"status": "success"},
        )

        mock_trace.update.assert_called_once()

    def test_flush_disabled(self, langfuse_client_disabled):
        """無効化時のフラッシュテスト"""
        # エラーなく実行完了することを確認
        langfuse_client_disabled.flush()

    def test_flush_enabled(self, langfuse_client_enabled):
        """有効化時のフラッシュテスト"""
        langfuse_client_enabled.flush()
        langfuse_client_enabled.client.flush.assert_called_once()

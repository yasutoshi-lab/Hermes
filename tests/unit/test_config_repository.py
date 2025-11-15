"""Unit tests for ConfigRepository"""

import pytest
from pathlib import Path
import yaml

from hermes_cli.persistence.config_repository import ConfigRepository
from hermes_cli.models.config import HermesConfig


class TestConfigRepository:
    """ConfigRepositoryのテスト"""

    @pytest.fixture
    def config_repo(self, temp_work_dir):
        """ConfigRepositoryインスタンス"""
        return ConfigRepository(work_dir=temp_work_dir)

    def test_init(self, config_repo):
        """初期化テスト"""
        assert config_repo is not None

    def test_save_and_load_config(self, config_repo, test_config):
        """設定保存・読み込みテスト"""
        # 保存
        config_repo.save(test_config)

        # 読み込み
        loaded_config = config_repo.load()

        # 検証
        assert loaded_config is not None
        assert loaded_config.language == test_config.language
        assert loaded_config.ollama.model == test_config.ollama.model
        assert loaded_config.search.searxng_base_url == test_config.search.searxng_base_url

    def test_load_default_config(self, config_repo):
        """デフォルト設定読み込みテスト"""
        # 設定ファイルが存在しない場合
        config = config_repo.load()

        # デフォルト値が使用される
        assert config is not None
        assert isinstance(config, HermesConfig)

    def test_config_file_path(self, config_repo, temp_work_dir):
        """設定ファイルパステスト"""
        expected_path = temp_work_dir / "config.yaml"

        # 設定を保存
        config_repo.save(config_repo.load())

        # ファイルが存在することを確認
        assert expected_path.exists()

    def test_config_yaml_format(self, config_repo, test_config, temp_work_dir):
        """YAML形式テスト"""
        # 保存
        config_repo.save(test_config)

        # YAMLファイルを直接読み込み
        config_path = temp_work_dir / "config.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)

        # 検証
        assert "ollama" in yaml_data
        assert "search" in yaml_data
        assert yaml_data["ollama"]["model"] == test_config.ollama.model

# Hermes Test Suite

Hermesプロジェクトのテストスイートです。

## ディレクトリ構造

```
tests/
├── README.md                      # このファイル
├── __init__.py
├── conftest.py                    # Pytest fixtures
├── test_dependencies.py           # 依存サービス疎通テスト
├── unit/                          # ユニットテスト
│   ├── test_ollama_client.py
│   ├── test_searxng_client.py
│   ├── test_langfuse_client.py
│   ├── test_task_repository.py
│   ├── test_config_repository.py
│   ├── test_agent_nodes.py
│   └── test_task_service.py
├── integration/                   # 統合テスト
│   ├── test_workflow.py
│   └── test_services_integration.py
└── e2e/                          # E2Eテスト（将来用）
```

## テストカテゴリ

### 1. 依存サービス疎通テスト

依存する外部サービスの接続性を確認します。

**対象サービス:**
- Redis
- Ollama
- SearxNG
- Langfuse

**実行方法:**
```bash
python tests/test_dependencies.py
```

**期待される出力:**
```
Checking Hermes Dependencies...

┏━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Service  ┃ Status  ┃ Version/Info  ┃ Details                ┃
┡━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Redis    │ ✓ OK    │ 7.0.15        │ Connected clients: 1   │
│ Ollama   │ ✓ OK    │ 5 models...   │ Configured: gpt-oss... │
│ SearxNG  │ ✓ OK    │ SearxNG       │ Test search returned...│
│ Langfuse │ ✓ OK    │ 3.104.0       │ Status: OK             │
└──────────┴─────────┴───────────────┴────────────────────────┘

✓ All services are healthy
```

### 2. ユニットテスト

個々のコンポーネントを単独でテストします。モックを使用し、外部依存なしで実行できます。

**実行方法:**
```bash
# 全ユニットテストを実行
pytest tests/unit -v

# 特定のモジュールをテスト
pytest tests/unit/test_ollama_client.py -v

# カバレッジ付きで実行
pytest tests/unit --cov=hermes_cli --cov-report=html
```

**テスト対象:**
- ツール/クライアント (Ollama, SearxNG, Langfuse)
- リポジトリ (Task, Config, History)
- エージェントノード (Normalizer, QueryGenerator)
- サービス (Task, Run, History)

### 3. 統合テスト

複数のコンポーネントを組み合わせた動作を確認します。実際の外部サービスを使用します。

**前提条件:**
- Redis が起動している
- Ollama が起動している
- SearxNG が起動している
- Langfuse が起動している（オプション）

**実行方法:**
```bash
# 全統合テストを実行
pytest tests/integration -v -m integration

# 時間がかかるテストを除外
pytest tests/integration -v -m "integration and not slow"

# 特定のテストのみ実行
pytest tests/integration/test_workflow.py::TestFullWorkflow::test_simple_prompt_execution -v
```

**注意:**
- 統合テストは実際のLLMを使用するため、実行に数分かかる場合があります
- `@pytest.mark.slow` マーカーがついているテストは特に時間がかかります

### 4. E2Eテスト（将来実装予定）

エンドユーザーの視点から、システム全体の動作を確認します。

## テストマーカー

Pytestマーカーを使用してテストをフィルタリングできます:

```bash
# ユニットテストのみ実行
pytest -m unit

# 統合テストのみ実行
pytest -m integration

# 遅いテストを除外
pytest -m "not slow"

# 依存サービステストのみ
pytest -m dependency
```

## 利用可能なマーカー:
- `unit`: ユニットテスト（高速、外部依存なし）
- `integration`: 統合テスト（外部サービス必要）
- `slow`: 実行に時間がかかるテスト
- `dependency`: 依存サービスチェックテスト

## カバレッジレポート

テストカバレッジを確認するには:

```bash
# カバレッジ付きでテスト実行
pytest tests/unit --cov=hermes_cli --cov-report=html --cov-report=term

# HTMLレポートを開く
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## CI/CDでの使用

GitHub ActionsやGitLab CIでテストを実行する場合:

```yaml
# .github/workflows/test.yml の例
- name: Run unit tests
  run: pytest tests/unit -v

- name: Run dependency checks
  run: python tests/test_dependencies.py

- name: Run integration tests
  run: pytest tests/integration -v -m "integration and not slow"
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

## トラブルシューティング

### テストが失敗する場合

1. **依存サービスチェック**
   ```bash
   python tests/test_dependencies.py
   ```
   すべてのサービスが正常に動作していることを確認

2. **詳細ログ出力**
   ```bash
   pytest -vv --log-cli-level=DEBUG
   ```

3. **特定のテストのみ実行**
   ```bash
   pytest tests/unit/test_ollama_client.py::TestOllamaClient::test_generate_success -vv
   ```

### よくある問題

**Redis接続エラー:**
```bash
docker start hermes-redis
# または
redis-server --daemonize yes
```

**Ollama接続エラー:**
```bash
ollama serve  # 別ターミナルで実行
```

**SearxNG接続エラー:**
```bash
docker start searxng-container
```

## テストの追加

新しいテストを追加する場合:

1. 適切なディレクトリに配置 (`unit/`, `integration/`, `e2e/`)
2. ファイル名は `test_*.py` の形式
3. テストクラスは `Test*` の形式
4. テスト関数は `test_*` の形式
5. 適切なマーカーを付与

```python
import pytest

@pytest.mark.unit
def test_my_function():
    assert my_function() == expected_value

@pytest.mark.integration
@pytest.mark.slow
async def test_full_workflow():
    result = await run_workflow()
    assert result.status == "success"
```

## ベストプラクティス

1. **テストの独立性**: 各テストは他のテストに依存しないこと
2. **クリーンアップ**: フィクスチャを使用して、テスト後のクリーンアップを確実に実行
3. **モックの使用**: 外部依存を避けるため、ユニットテストではモックを使用
4. **明確なアサーション**: テストの意図が明確になるようなアサーションを書く
5. **ドキュメント**: 複雑なテストにはコメントを追加

## 参考リンク

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Python Mock](https://docs.python.org/3/library/unittest.mock.html)

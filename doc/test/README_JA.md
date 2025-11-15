# Hermes テストドキュメント

このディレクトリには、Hermesテストスイートのドキュメントが含まれています。

## テスト概要

Hermesプロジェクトには、以下の種類のテストが含まれています:

| テストタイプ | 目的 | 場所 |
|-----------|---------|----------|
| **スモークテスト** | モックを使用せずに基本機能を検証 | `tests/test_*.py` |
| **統合テスト** | コンポーネント間の相互作用をテスト | `tests/test_*.py` |
| **ワークフローテスト** | LangGraphのコンパイルを検証 | `test_workflow.py` (ルート) |

## テストの実行

### すべてのテストを実行

```bash
# 仮想環境をアクティブ化
source .venv/bin/activate

# pytestを実行
pytest

# カバレッジを含む
pytest --cov=hermes_cli

# 詳細出力
pytest -v
```

### 特定のテストファイルを実行

```bash
pytest tests/test_config.py
pytest tests/test_browser_client.py
```

### ワークフロースモークテストを実行

```bash
python test_workflow.py
```

## テスト要件

### 環境

- Python 3.10以降
- 仮想環境がアクティブ化されている
- 依存関係がインストール済み (`pip install -e .[dev]`)
- Hermesが初期化済み (`hermes init`)

### 外部サービス（統合テスト用）

- **Ollamaサーバー**: `test_nodes_ollama.py`、`test_run_service.py`で必要
  ```bash
  ollama serve
  ollama pull gpt-oss:20b
  ```

- **インターネット接続**: `test_browser_client.py`で必要（DuckDuckGo）

- **Docker**: コンテナテスト用（オプション、利用不可の場合は自動フォールバック）

## テストファイル

### test_browser_client.py

**目的**: BrowserUseClientのDuckDuckGoフォールバック機能を検証

**テスト内容**:
- DuckDuckGo検索が結果を返すこと
- 結果構造（タイトル、URL、スニペット、コンテンツ）
- コンテキストマネージャーの使用
- ネットワーク接続の処理

**要件**:
- インターネット接続
- 外部モック不要

**実行方法**:
```bash
python tests/test_browser_client.py
# または
pytest tests/test_browser_client.py
```

**期待される出力**:
```
Sample result: Example Title -> https://example.com
Snippet: Brief description of result...
Content preview: Full content preview...
Fetched 2 total sources.
```

**よくある失敗原因**:
- ネットワーク接続の問題
- DuckDuckGoのレート制限
- DNS解決の問題

---

### test_config.py

**目的**: ConfigServiceの読み込みとオーバーライドロジックをテスト

**テスト内容**:
- `~/.hermes/config.yaml`からのデフォルト設定の読み込み
- CLIオーバーライドの適用
- オーバーライド後の元の設定の不変性
- 設定データクラス構造

**要件**:
- Hermesが初期化済み (`hermes init`)
- 有効な`~/.hermes/config.yaml`

**実行方法**:
```bash
python tests/test_config.py
# または
pytest tests/test_config.py
```

**期待される出力**:
```
=== Default Configuration ===
Ollama API: http://localhost:11434/api/chat
Model: gpt-oss:20b
Language: ja
Validation loops: 1-3
Search sources: 3-8

=== After Overrides ===
Ollama API: http://localhost:11434/api/chat
Model: gpt-oss:8b
Language: en
Validation loops: 2-4
Search sources: 2-6

=== Original Config Still Intact ===
Language: ja
Validation loops: 1-3
```

**よくある失敗原因**:
- `~/.hermes/config.yaml`が見つからない
- YAMLシンタックスの破損
- データクラス構造の不正

---

### test_persistence.py

**目的**: TaskServiceとHistoryServiceのCRUD操作をテスト

**テスト内容**:
- タスクの作成、更新、削除
- タスクのリスト表示とフィルタリング
- 履歴メタデータの保存/読み込み
- レポートファイルのエクスポート
- クリーンアップ操作

**要件**:
- Hermesが初期化済み
- `~/.hermes/`への書き込み権限

**実行方法**:
```bash
python tests/test_persistence.py
# または
pytest tests/test_persistence.py
```

**期待される出力**:
```
=== TaskService CRUD ===
Created task: 2025-XXXX (scheduled)
Total tasks after create: X
Status after update: running
Deleted task: 2025-XXXX

=== HistoryService persistence ===
Saved history metadata and report for integration-test-0001
History entries available: X
Fetched history language: ja
Exported report exists: True
Cleaned up history entry integration-test-0001
```

**よくある失敗原因**:
- `~/.hermes/`への書き込み権限拒否
- ディスク容量の問題
- 同時アクセスの競合

---

### test_run_service.py

**目的**: RunServiceワークフロー実行のエンドツーエンド統合テスト

**テスト内容**:
- 完全なワークフロー実行
- Ollamaクライアントとの相互作用
- 履歴メタデータの作成
- レポート生成
- エラーハンドリング

**要件**:
- **Ollamaサーバーが実行中** (`ollama serve`)
- **モデルが利用可能** (`ollama pull gpt-oss:20b`)
- インターネット接続（Web調査用）
- Hermesが初期化済み

**実行方法**:
```bash
# Ollamaが実行中であることを確認
ollama serve &

# テストを実行
python tests/test_run_service.py
# または
pytest tests/test_run_service.py
```

**期待される動作**:
- 完全な調査ワークフローを実行
- `~/.hermes/history/`にレポートを作成
- モデルとクエリの複雑さに応じて30〜180秒かかる
- Ollamaが遅い場合はタイムアウトの可能性あり

**よくある失敗原因**:
- Ollamaサーバーが起動していない
- モデルが見つからない
- タイムアウト（設定で`timeout_sec`を増やす）
- Web検索のレート制限

---

### test_nodes_ollama.py

**目的**: Ollama統合を使用した個別のLangGraphノードをテスト

**テスト内容**:
- クエリジェネレーターノード
- ドラフトアグリゲーターノード
- バリデーターノード
- Ollamaクライアントのリトライロジック
- エラーハンドリング

**要件**:
- **Ollamaサーバーが実行中**
- **モデルが利用可能**

**実行方法**:
```bash
pytest tests/test_nodes_ollama.py -v
```

**期待される動作**:
- 個別のノードを分離してテスト
- Ollamaレスポンスのパースを検証
- エラーハンドリングとリトライをチェック

**よくある失敗原因**:
- Ollama接続が拒否される
- モデルタイムアウト
- プロンプトの形式不正

---

### test_queue_service.py

**目的**: キュー処理ロジックをテスト

**テスト内容**:
- キューの順序（FIFO）
- タスクステータスの更新
- 制限の適用
- 失敗したタスクのエラーハンドリング
- 順次実行

**要件**:
- Hermesが初期化済み
- モックタスクが作成済み

**実行方法**:
```bash
pytest tests/test_queue_service.py
```

**期待される動作**:
- 作成順にタスクを処理
- タスクステータスを正しく更新
- limitパラメータを尊重
- 個別のタスク失敗時も継続

---

### test_logging.py

**目的**: LogServiceとLogRepositoryをテスト

**テスト内容**:
- ログファイルの書き込み
- ログローテーション（日次）
- tail機能
- stream機能
- タスクIDフィルタリング

**要件**:
- Hermesが初期化済み
- `~/.hermes/log/`への書き込み権限

**実行方法**:
```bash
pytest tests/test_logging.py
```

**期待される動作**:
- 構造化されたログ行を書き込む
- 日付変更時に新しいファイルを作成
- tailが正しい行数を返す
- streamがリアルタイムで新しい行を返す

---

### test_workflow.py（ルート）

**目的**: LangGraphグラフコンパイルのスモークテスト

**テスト内容**:
- `create_hermes_workflow()`がインポート可能
- `HermesState`がインスタンス化可能
- ワークフローグラフがエラーなくコンパイルされる
- ノード/エッジ設定エラーがない

**要件**:
- 基本的なPython環境
- LangGraphがインストール済み

**実行方法**:
```bash
python test_workflow.py
```

**期待される出力**:
```
✓ Successfully imported create_hermes_workflow and HermesState
✓ Successfully created HermesState: Test research question
✓ Successfully created workflow graph

=== All tests passed! ===
```

**よくある失敗原因**:
- 依存関係の欠落
- インポートエラー
- グラフ構造エラー
- ノード登録の問題

## テストカバレッジ

テストカバレッジを確認するには:

```bash
pytest --cov=hermes_cli --cov-report=html
open htmlcov/index.html  # カバレッジレポートを表示
```

モジュール別の目標カバレッジ:

| モジュール | 目標カバレッジ |
|--------|----------------|
| `commands/` | 80%以上 |
| `services/` | 90%以上 |
| `persistence/` | 95%以上 |
| `agents/` | 70%以上 |
| `tools/` | 60%以上 |

## 新しいテストの作成

### スモークテストテンプレート

```python
#!/usr/bin/env python3
"""Brief description of what this test verifies."""

from hermes_cli.services import YourService

def main() -> None:
    service = YourService()
    result = service.do_something()

    if not result:
        raise SystemExit("Test failed: no result returned")

    print(f"✓ Test passed: {result}")

if __name__ == "__main__":
    main()
```

### Pytestテストテンプレート

```python
"""Unit tests for YourModule."""

import pytest
from hermes_cli.your_module import YourClass

def test_basic_functionality():
    """Test basic functionality."""
    instance = YourClass()
    result = instance.method()
    assert result is not None

def test_error_handling():
    """Test error handling."""
    instance = YourClass()
    with pytest.raises(ValueError):
        instance.method_that_fails()
```

## 継続的インテグレーション

テストは、以下を含むCI/CDパイプラインで実行する必要があります:

1. **ユニットテスト**: 高速、外部依存関係なし
2. **統合テスト**: Ollama、Docker、インターネット接続が必要
3. **スモークテスト**: 迅速なエンドツーエンドチェック

### CI設定例

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e .[dev]
      - name: Run unit tests
        run: pytest tests/ -m "not integration"
      - name: Install Ollama
        run: |
          curl -sSL https://ollama.ai/install.sh | sh
          ollama serve &
          ollama pull gpt-oss:20b
      - name: Run integration tests
        run: pytest tests/ -m integration
```

## テストのトラブルシューティング

### すべてのテストが失敗する場合

1. 仮想環境を確認:
   ```bash
   which python
   pip list | grep hermes
   ```

2. 依存関係を再インストール:
   ```bash
   pip install -e .[dev]
   ```

3. Hermesを再初期化:
   ```bash
   hermes init
   ```

### Ollamaテストが失敗する場合

1. サーバーを確認:
   ```bash
   curl http://localhost:11434/api/version
   ```

2. モデルを確認:
   ```bash
   ollama list | grep gpt-oss
   ```

3. タイムアウトを増やす:
   ```yaml
   # ~/.hermes/config.yaml
   ollama:
     timeout_sec: 300
   ```

### ネットワークテストが失敗する場合

1. 接続を確認:
   ```bash
   ping 8.8.8.8
   curl https://duckduckgo.com
   ```

2. レート制限を確認（1〜2分待つ）

3. 地理的にブロックされている場合はVPNを使用

## テストメンテナンス

- **新機能にはテストを追加**
- **動作が変更されたらテストを更新**
- **機能が削除されたら古いテストを削除**
- **テストを高速に保つ**（ユニットテストは30秒未満）
- **要件をドキュメント化**（テストのdocstringに記載）
- **可能な限り外部サービスをモック化**

## 関連ドキュメント

- [DEVELOPMENT.md](../../DEVELOPMENT.md) - 開発環境のセットアップ
- [ARCHITECTURE.md](../../ARCHITECTURE.md) - システムアーキテクチャ
- [doc/command/](../command/)のコマンドドキュメント

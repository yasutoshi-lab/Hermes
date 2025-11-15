# Hermesコマンドドキュメント

このディレクトリには、すべてのHermes CLIコマンドの詳細なドキュメントが含まれています。

## 利用可能なコマンド

| コマンド | 説明 | ドキュメント |
|---------|-------------|---------------|
| `hermes init` | Hermesワークスペースと設定を初期化 | [init.md](./init.md) |
| `hermes run` | LangGraphワークフローでリサーチタスクを実行 | [run.md](./run.md) |
| `hermes task` | スケジュール済みタスクを管理 | [task.md](./task.md) |
| `hermes queue` | スケジュール済みタスクを順次処理 | [queue.md](./queue.md) |
| `hermes history` | 実行履歴を表示およびエクスポート | [history.md](./history.md) |
| `hermes log` | 構造化された実行ログを表示 | [log.md](./log.md) |
| `hermes debug` | 詳細なデバッグログを表示 | [debug.md](./debug.md) |

## クイックリファレンス

### 初回セットアップ

```bash
# 1. ワークスペースを初期化
hermes init

# 2. Ollamaサーバーを起動（別のターミナル）
ollama serve

# 3. 最初のタスクを実行
hermes run --prompt "リサーチ質問"
```

### 一般的なワークフロー

#### 単一タスク実行

```bash
hermes run --prompt "リサーチトピック" --language ja
hermes history --limit 1
hermes history --export 2025-0001:./report.md
```

#### バッチ処理

```bash
# 複数のタスクをスケジュール
hermes task --prompt "トピックA"
hermes task --prompt "トピックB"
hermes task --prompt "トピックC"

# キューを確認
hermes task --list

# すべてを処理
hermes queue --all

# 結果を確認
hermes history --limit 10
```

#### モニタリングとトラブルシューティング

```bash
# アクティブなタスクをモニター
hermes log --follow

# エラーを確認
hermes debug --error -n 100

# 特定のタスクログを表示
hermes log --task-id 2025-0005 -n 200
```

## コマンドの関係

```
init → run → history
       ↓      ↓
      task → queue
       ↓
      log / debug
```

1. **init**: ワークスペースを作成（1回限りのセットアップ）
2. **run**: 単一タスクを即座に実行
3. **task**: 後で実行するタスクをスケジュール
4. **queue**: スケジュール済みタスクを処理
5. **history**: 完了したレポートを表示
6. **log**: 実行の進捗をモニター
7. **debug**: 失敗のトラブルシューティング

## グローバルオプション

すべてのコマンドがサポート:

- 標準出力への出力
- 他のコマンドへのパイプ
- スクリプト用の終了コード
- リッチフォーマット（色、テーブル）

## 終了コード

| コード | 意味 |
|------|---------|
| 0 | 成功 |
| 1 | 一般的なエラー |
| 2 | 無効な引数 |
| 3 | 検証失敗 |

## 環境変数

現在サポートされていません。設定は`~/.hermes/config.yaml`経由で行います。

## ファイルの場所

| ディレクトリ | 目的 | ファイル |
|-----------|---------|-------|
| `~/.hermes/` | ベースディレクトリ | `config.yaml` |
| `~/.hermes/history/` | レポート | `report-*.md`, `report-*.meta.yaml` |
| `~/.hermes/task/` | スケジュール済みタスク | `task-*.yaml` |
| `~/.hermes/log/` | 実行ログ | `hermes-YYYYMMDD.log` |
| `~/.hermes/debug_log/` | デバッグログ | `hermes-YYYYMMDD.log` |
| `~/.hermes/cache/` | 一時ファイル | （各種） |

## ヘルプの取得

コマンド固有のヘルプの場合:

```bash
hermes COMMAND --help
```

詳細なドキュメントの場合:

- このディレクトリの個別コマンドの`.md`ファイルを参照
- タスク指向のワークフローについては[USAGE_GUIDE.md](../../USAGE_GUIDE.md)を参照
- システム内部については[ARCHITECTURE.md](../../ARCHITECTURE.md)を確認

## 一般的な問題

コマンド固有のトラブルシューティングについては、各コマンドのドキュメントを参照してください。

### 一般的な問題

1. **Ollamaが実行されていない**: `ollama serve`がアクティブである必要があります
2. **モデルが見つからない**: `ollama pull gpt-oss:20b`
3. **権限拒否**: `~/.hermes/`の権限を確認
4. **タイムアウトエラー**: 設定で`ollama.timeout_sec`を増やす

## シェル補完

HermesはTyperを使用しており、シェル補完をサポートしています:

```bash
# Bash
hermes --install-completion bash

# Zsh
hermes --install-completion zsh

# Fish
hermes --install-completion fish
```

## API/プログラマティックアクセス

コマンドはサービスクラスの薄いラッパーです。プログラマティックな使用の場合:

```python
from hermes_cli.services import RunService, TaskService

# タスクをプログラマティックに実行
run_service = RunService()
history_meta = run_service.run_prompt("プロンプト", options={})
```

詳細は[DEVELOPMENT.md](../../DEVELOPMENT.md)を参照してください。

## 変更履歴

コマンドインターフェースは安定しています。破壊的な変更はリリースノートに記載されます。

## 貢献

新しいコマンドを追加するには:

1. `hermes_cli/commands/new_cmd.py`を作成
2. Typerデコレータを使用してコマンド関数を実装
3. `hermes_cli/commands/__init__.py`でエクスポート
4. `hermes_cli/main.py`で登録
5. `doc/command/new.md`にドキュメントを追加
6. `tests/test_new_cmd.py`にテストを追加

貢献ガイドラインについては[DEVELOPMENT.md](../../DEVELOPMENT.md)を参照してください。

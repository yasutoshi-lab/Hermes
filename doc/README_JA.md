# Hermes ドキュメント

このディレクトリには、Hermes CLI研究エージェントの詳細なドキュメントが含まれています。

## ドキュメント構造

```
doc/
├── command/           # コマンドラインインターフェースドキュメント
│   ├── README.md     # コマンド概要とクイックリファレンス
│   ├── init.md       # hermes init コマンド
│   ├── run.md        # hermes run コマンド
│   ├── task.md       # hermes task コマンド
│   ├── queue.md      # hermes queue コマンド
│   ├── history.md    # hermes history コマンド
│   ├── log.md        # hermes log コマンド
│   └── debug.md      # hermes debug コマンド
│
├── dependencies/      # 外部依存関係ドキュメント
│   ├── README.md     # 依存関係の概要とセットアップガイド
│   ├── ollama.md     # Ollama LLMサーバーセットアップ
│   ├── browser-use.md # ブラウザ自動化セットアップ
│   └── container-use.md # Docker統合セットアップ
│
└── test/             # テストスイートドキュメント
    └── README.md     # テスト概要、要件、ガイド
```

## クイックナビゲーション

### ユーザー向け

- **はじめに**: プロジェクトルートの [README.md](../README.md) を参照
- **インストール**: [README.md](../README.md#installation)
- **クイックスタート**: [README.md](../README.md#quick-start)
- **コマンド**: [command/README.md](./command/README.md)
- **依存関係セットアップ**: [dependencies/README.md](./dependencies/README.md)
- **使用例**: [USAGE_GUIDE.md](../USAGE_GUIDE.md)
- **統合セットアップ**: [README.md](../README.md#integration-setup)

### 開発者向け

- **アーキテクチャ**: [ARCHITECTURE.md](../ARCHITECTURE.md)
- **開発ガイド**: [DEVELOPMENT.md](../DEVELOPMENT.md)
- **テストドキュメント**: [test/README.md](./test/README.md)
- **Claude Codeガイド**: [CLAUDE.md](../CLAUDE.md)

## タスク別ドキュメント

### 初回セットアップ

1. [インストール](../README.md#installation) - Hermesと依存関係をインストール
2. [依存関係セットアップ](./dependencies/README.md) - Ollama、Docker、browser-useを設定
   - [Ollamaセットアップ](./dependencies/ollama.md) - 必須のLLMサーバー
   - [Dockerセットアップ](./dependencies/container-use.md) - オプションのコンテナ分離
   - [browser-useセットアップ](./dependencies/browser-use.md) - オプションの拡張Web検索
3. [hermes init](./command/init.md) - ワークスペースを初期化
4. [クイックスタート](../README.md#quick-start) - 最初のタスクを実行

### 調査タスクの実行

- [hermes run](./command/run.md) - 単一タスクを実行
- [hermes task](./command/task.md) - 後で実行するタスクをスケジュール
- [hermes queue](./command/queue.md) - スケジュールされたタスクをバッチ処理
- [hermes history](./command/history.md) - 結果の表示とエクスポート

### 監視とデバッグ

- [hermes log](./command/log.md) - 実行の進行状況を監視
- [hermes debug](./command/debug.md) - 失敗のトラブルシューティング
- [トラブルシューティング](../README.md#troubleshooting-highlights) - よくある問題

### 開発とテスト

- [開発ガイド](../DEVELOPMENT.md) - 開発環境をセットアップ
- [テストドキュメント](./test/README.md) - テストの実行と作成
- [アーキテクチャ概要](../ARCHITECTURE.md) - システム設計を理解

## コマンドリファレンス

すべてのコマンドは `--help` でインラインドキュメントをサポートしています：

```bash
hermes --help
hermes run --help
hermes task --help
```

| コマンド | 目的 | ドキュメント |
|---------|---------|---------------|
| `hermes init` | ワークスペースを初期化 | [init.md](./command/init.md) |
| `hermes run` | 調査タスクを実行 | [run.md](./command/run.md) |
| `hermes task` | スケジュールされたタスクを管理 | [task.md](./command/task.md) |
| `hermes queue` | タスクキューを処理 | [queue.md](./command/queue.md) |
| `hermes history` | 実行履歴を表示 | [history.md](./command/history.md) |
| `hermes log` | 実行ログを表示 | [log.md](./command/log.md) |
| `hermes debug` | デバッグログを表示 | [debug.md](./command/debug.md) |

## 主要な概念

### タスクのライフサイクル

```
作成 → スケジュール → 実行 → 検証 → 完了
  ↓                    ↓      ↓      ↓
task.yaml         running  looping  history/
```

1. **作成**: `hermes task --prompt "..."`
2. **スケジュール**: タスクは `task-YYYY-NNNN.yaml` として保存
3. **実行**: `hermes queue` または `hermes run --task-id`
4. **検証**: 設定可能な検証ループ (1-N)
5. **完了**: レポートは `history/` に保存

### データフロー

```
プロンプト → クエリ生成 → Web調査 → 処理 → ドラフト → 検証 → レポート
           (Ollama)    (DuckDuckGo)  (Docker)  (Ollama)  (Loop)  (Output)
```

詳細なフローについては [ARCHITECTURE.md](../ARCHITECTURE.md) を参照してください。

### ファイル構成

```
~/.hermes/
├── config.yaml          # 設定
├── history/             # 生成されたレポート
│   ├── report-*.md
│   └── report-*.meta.yaml
├── task/                # スケジュールされたタスク
│   └── task-*.yaml
├── log/                 # 実行ログ
│   └── hermes-YYYYMMDD.log
└── debug_log/           # デバッグログ
    └── hermes-YYYYMMDD.log
```

## 設定

### メイン設定ファイル

場所: `~/.hermes/config.yaml`

主要な設定:

```yaml
ollama:
  api_base: http://localhost:11434/api/chat
  model: gpt-oss:20b
  retry: 3
  timeout_sec: 180

language: ja  # または "en"

validation:
  min_loops: 1
  max_loops: 3

search:
  min_sources: 3
  max_sources: 8
```

### ランタイムオーバーライド

すべての設定値はCLIフラグで上書きできます：

```bash
hermes run --prompt "..." \
  --model llama2:70b \
  --language en \
  --max-validation 5 \
  --max-search 12
```

すべてのオプションについては [hermes run](./command/run.md#options) を参照してください。

## 一般的なワークフロー

### 単一タスクの調査

```bash
hermes run --prompt "Your research question"
hermes history --limit 1
hermes history --export 2025-0001:./report.md
```

### バッチ処理

```bash
# タスクをスケジュール
hermes task --prompt "Topic A"
hermes task --prompt "Topic B"
hermes task --prompt "Topic C"

# キューを処理
hermes queue --all

# 結果を確認
hermes history --limit 10
```

### 長時間タスクの監視

```bash
# ターミナル1: タスクを実行
hermes run --prompt "Complex research" --max-validation 5

# ターミナル2: ログを追跡
hermes log --follow

# ターミナル3: エラーを監視
hermes debug --follow --error
```

### 失敗したタスクのトラブルシューティング

```bash
# 失敗したタスクを検索
hermes history | grep failed

# エラーログを確認
hermes debug --error -n 200 | grep task_id=2025-0003

# 完全なログを表示
hermes log --task-id 2025-0003 -n 500
```

## 外部依存関係

### 必須

- **Python 3.10+**: ランタイム環境
- **Ollama**: LLM推論 (`ollama serve`)
- **モデル**: `gpt-oss:20b` または類似 (`ollama pull gpt-oss:20b`)

### オプション

- **Docker 20.10+**: テキスト処理のためのコンテナ分離
- **browser-use**: 高度なWeb自動化（ソースからインストール）

セットアップ手順については [README.md](../README.md#integration-setup) を参照してください。

## サポートとリソース

### ドキュメントファイル

- **README.md**: プロジェクト概要とインストール
- **USAGE_GUIDE.md**: タスク指向のウォークスルー
- **DEVELOPMENT.md**: 開発環境のセットアップ
- **ARCHITECTURE.md**: システム設計とデータフロー
- **CLAUDE.md**: Claude Code（AIアシスタント）のガイド
- **doc/command/**: 詳細なコマンドドキュメント
- **doc/test/**: テストスイートドキュメント

### ヘルプの入手

1. **コマンドヘルプ**: `hermes COMMAND --help`
2. **トラブルシューティング**: [README.md](../README.md#troubleshooting-highlights)
3. **Issues**: [GitHub Issues](https://github.com/your-org/Hermes/issues)
4. **ログ**: `hermes log` および `hermes debug`

### 貢献

以下については [DEVELOPMENT.md](../DEVELOPMENT.md) を参照してください：

- 開発環境のセットアップ
- テストの実行
- コードスタイルガイドライン
- プルリクエストの提出

## バージョン履歴

ドキュメントはHermes CLIバージョン1.0.0に対応しています。

変更履歴とバージョン履歴については、プロジェクトルートを参照してください。

## ライセンス

MITライセンス - 詳細はプロジェクトルートを参照してください。

---

**ナビゲーション**: [↑ ドキュメントルート](#hermes-ドキュメント) | [→ コマンド](./command/README.md) | [→ テスト](./test/README.md)

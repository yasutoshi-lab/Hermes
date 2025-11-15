# hermes init

## 概要

データディレクトリ構造とデフォルト設定ファイルを作成して、Hermesワークスペースを初期化します。

## シノプシス

```bash
hermes init
```

## 説明

`init`コマンドは以下の操作により、Hermesを初回使用のためにセットアップします:

1. `~/.hermes/`ディレクトリ構造を作成
2. OllamaとValidation設定を含むデフォルトの`config.yaml`を生成
3. history、logs、tasks、cacheのサブディレクトリをセットアップ

このコマンドは**冪等性**を持っており、複数回実行しても安全で、既存の設定を上書きしません。

## 作成されるディレクトリ構造

```
~/.hermes/
├── cache/              # 一時キャッシュファイル
├── config.yaml         # メイン設定ファイル
├── history/            # レポートMarkdownファイルとメタデータ
├── task/               # スケジュール済みタスク定義
├── log/                # 構造化ログファイル（日次ローテーション）
└── debug_log/          # デバッグレベルログ（日次ローテーション）
```

## デフォルト設定

生成される`config.yaml`には以下が含まれます:

- **Ollama設定**: APIエンドポイント(`http://localhost:11434/api/chat`)、モデル(`gpt-oss:20b`)、タイムアウト(180秒)
- **Validationループ**: 最小=1、最大=3
- **検索ソース**: 最小=3、最大=8
- **言語**: デフォルトで日本語(`ja`)
- **ロギング**: INFOレベル、ログディレクトリ

## 例

### 初回の初期化

```bash
hermes init
```

**出力:**
```
╭─────── Initialization Complete ───────╮
│ ✓ Hermes initialized successfully!   │
│                                       │
│ Data directory: /home/user/.hermes   │
│ Config file: /home/user/.hermes/...  │
│                                       │
│ You can now use:                      │
│ hermes run --prompt "your query"      │
╰───────────────────────────────────────╯
```

### すでに初期化済みの場合

```bash
hermes init
```

**出力:**
```
Hermes is already initialized.
Location: /home/user/.hermes
```

## 終了コード

- **0**: 成功
- **1**: 初期化失敗（権限、ディスク容量など）

## 注意事項

- このコマンドは、ファイルを作成する前に既存の設定を確認します
- `config.yaml`が存在する場合、上書きされません
- ディレクトリ作成は`mkdir -p`のセマンティクスを使用します（存在する場合はエラーなし）
- すべてのファイルはUnixシステムでユーザー専用の権限で作成されます

## 関連コマンド

- [`hermes run --clear`](./run.md#reset-configuration) - 設定をデフォルトにリセット
- [`hermes history`](./history.md) - 実行履歴を表示
- [`hermes log`](./log.md) - ログを表示

## 設定ファイルの場所

- **Linux/macOS**: `~/.hermes/config.yaml`
- **Windows**: `%USERPROFILE%\.hermes\config.yaml`

## トラブルシューティング

### 権限拒否

ホームディレクトリへの書き込みアクセスがあることを確認してください:

```bash
ls -ld ~
mkdir -p ~/.hermes
```

### ディスク容量の問題

利用可能な容量を確認してください:

```bash
df -h ~
```

初期化には最小限の容量(<1 MB)が必要です。

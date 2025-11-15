# hermes log

## 概要

オプションのタスクフィルタリングとリアルタイムストリーミングを使用して、構造化された実行ログを表示します。

## シノプシス

```bash
hermes log
hermes log -n COUNT
hermes log --follow
hermes log --task-id TASK_ID
```

## 説明

`log`コマンドは、`~/.hermes/log/`に保存されているHermes実行ログへのアクセスを提供します。ログは:

- **構造化**: 各行にタイムスタンプ、レベル、カテゴリ、メッセージがあります
- **日次ローテーション**: 1日ごとに新しいファイル（`hermes-YYYYMMDD.log`）
- **ユーザー向け**: タスクの進捗に焦点を当て、内部デバッグではありません

詳細な開発者ログには`hermes debug`を使用してください。

## オプション

| オプション | 型 | デフォルト | 説明 |
|--------|------|---------|-------------|
| `-n, --lines INT` | 整数 | `50` | 表示するログ行数 |
| `-f, --follow` | フラグ | `false` | リアルタイムでログをストリーム（`tail -f`のように） |
| `--task-id TEXT` | 文字列 | 最新の実行中 | 特定のタスクIDでログをフィルター |

## ログ形式

各ログ行は以下の構造に従います:

```
YYYY-MM-DDTHH:MM:SS.mmmmmm+TZ [LEVEL] [CATEGORY] Message key=value ...
```

### 例

```
2025-11-14T14:28:30.123456+09:00 [INFO] [RUN] Starting task execution task_id=2025-0005 prompt=Quantum computing
2025-11-14T14:28:30.234567+09:00 [INFO] [RUN] Initializing LangGraph workflow
2025-11-14T14:28:45.345678+09:00 [INFO] [WEB] Collected 8 sources for query="quantum error correction"
2025-11-14T14:30:52.456789+09:00 [INFO] [RUN] Task execution completed task_id=2025-0005 sources=24
```

## ログレベル

| レベル | 説明 |
|-------|-------------|
| **INFO** | 通常の操作イベント（タスク開始、完了、ソース収集） |
| **WARNING** | 潜在的な問題（フォールバック使用、再試行実施） |
| **ERROR** | 実行失敗（タイムアウト、接続拒否、検証失敗） |

## ログカテゴリ

| カテゴリ | 説明 |
|----------|-------------|
| **RUN** | タスク実行ライフサイクル |
| **WEB** | Webリサーチ操作 |
| **OLLAMA** | LLM API対話 |
| **DOCKER** | コンテナ操作 |
| **CONFIG** | 設定変更 |

## 例

### 最新50行を表示（デフォルト）

```bash
hermes log
```

**出力:**
```
2025-11-14T14:28:30+09:00 [INFO] [RUN] Starting task execution task_id=2025-0005
2025-11-14T14:28:30+09:00 [INFO] [RUN] Initializing LangGraph workflow
2025-11-14T14:28:45+09:00 [INFO] [WEB] Collected 8 sources
2025-11-14T14:30:52+09:00 [INFO] [RUN] Task execution completed sources=24
...
```

### 最新100行を表示

```bash
hermes log -n 100
```

### ログをリアルタイムでフォロー

```bash
hermes log --follow
```

**出力:**
```
Following log (Ctrl+C to exit)...

2025-11-14T14:35:00+09:00 [INFO] [RUN] Starting task execution task_id=2025-0006
2025-11-14T14:35:00+09:00 [INFO] [RUN] Initializing LangGraph workflow
... (Ctrl+Cまで続く)
```

### タスクIDでフィルター

```bash
hermes log --task-id 2025-0005 -n 200
```

**出力:**
```
2025-11-14T14:28:30+09:00 [INFO] [RUN] Starting task execution task_id=2025-0005
2025-11-14T14:28:30+09:00 [INFO] [RUN] Initializing LangGraph workflow
2025-11-14T14:30:52+09:00 [INFO] [RUN] Task execution completed task_id=2025-0005
```

`task_id=2025-0005`を含まないすべての行はフィルタリングされます。

### アクティブなタスクをモニター

```bash
# 最新の実行中タスクを自動選択
hermes log --follow
```

**出力:**
```
Defaulting to latest running task 2025-0006
Following log (Ctrl+C to exit)...
```

## ログファイルの場所

ログは日次ローテーションで`~/.hermes/log/`に保存されます:

```
~/.hermes/log/
├── hermes-20251114.log  # 今日
├── hermes-20251113.log  # 昨日
├── hermes-20251112.log
└── ...
```

## 日次ローテーション

- 新しいログファイルは深夜（ローカル時間）に作成されます
- 前日のログは無期限に保持されます
- 自動クリーンアップはありません（必要に応じて手動で管理）

## フィルタリング動作

### タスクIDフィルタリング

`--task-id`が指定された場合:
1. コマンドは指定された行数を読み取ります
2. `task_id=TASK_ID`を含む行にフィルター
3. フィルター結果を表示

一致する行が見つからない場合:
```
No log lines found for task 2025-9999
```

### タスクIDなし

最新の実行中タスクにデフォルト:
```bash
# 以下と同等:
hermes log  # 最新の実行中タスクを自動選択
```

実行中のタスクがない場合、すべてのログを表示（フィルタリングなし）。

## リアルタイムストリーミング

### フォローモード

```bash
hermes log --follow
```

- 書き込まれた新しいログ行をストリーミング
- `Ctrl+C`で終了
- タスクフィルタリングと併用可能:
  ```bash
  hermes log --follow --task-id 2025-0005
  ```

### ユースケース

長時間実行タスクをモニター:
```bash
hermes run --prompt "複雑なクエリ" --max-validation 10 &
hermes log --follow
```

複数のターミナルウィンドウ:
```
ターミナル1: hermes queue --all
ターミナル2: hermes log --follow
```

## 標準ツールとの組み合わせ

### エラーをgrepで検索

```bash
hermes log -n 500 | grep ERROR
```

### Webソースをカウント

```bash
hermes log -n 200 | grep "Collected.*sources" | wc -l
```

### タスクIDを抽出

```bash
hermes log -n 100 | grep -oE 'task_id=[0-9]{4}-[0-9]{4}' | sort -u
```

### ファイルに保存

```bash
hermes log -n 1000 > analysis.log
```

## パフォーマンスノート

- ログの読み取りは高速（1000行で<100ms）
- フォローモードは最小限のオーバーヘッド
- タスクIDフィルタリングはすべての指定行をスキャン
- 大きな行数（>10000）は遅い場合があります

## 終了コード

- **0**: 成功
- **1**: ログサービスエラー

## 複数日にまたがるタスク

深夜をまたいで実行されるタスクは複数のログファイルにまたがります:

```bash
# タスクが11月13日23:50に開始し、11月14日00:10に終了

# 両日を確認
hermes log --task-id 2025-0005 -n 1000  # 11月14日部分のみ表示される可能性

# 手動アプローチ
cat ~/.hermes/log/hermes-20251113.log | grep task_id=2025-0005
cat ~/.hermes/log/hermes-20251114.log | grep task_id=2025-0005
```

## ログのクリーンアップ

ログは自動的に削除されません。ディスク容量を管理するには:

### 古いログを削除

```bash
# 30日より古いログを削除
find ~/.hermes/log -name "hermes-*.log" -mtime +30 -delete
```

### 古いログをアーカイブ

```bash
# 7日より古いログを圧縮
find ~/.hermes/log -name "hermes-*.log" -mtime +7 -exec gzip {} \;
```

### ディスク使用量を確認

```bash
du -sh ~/.hermes/log
ls -lh ~/.hermes/log/*.log
```

## トラブルシューティング

### ログが表示されない

ログディレクトリを確認:
```bash
ls -la ~/.hermes/log/
hermes init  # 欠落している場合は再作成
```

### フォローモードが更新されない

タスクが実際に実行されていることを確認:
```bash
ps aux | grep hermes
hermes task --list
```

### タスクIDフィルタが何も返さない

タスクID形式を確認:
```bash
hermes history  # 正しいタスクIDを確認
hermes log --task-id 2025-0005  # 正しい形式を使用
```

### ログファイルが大きすぎる

手動でローテーション:
```bash
mv ~/.hermes/log/hermes-$(date +%Y%m%d).log{,.bak}
```

## デバッグログとの比較

| 機能 | `hermes log` | `hermes debug` |
|---------|--------------|----------------|
| **目的** | ユーザー向けタスク進捗 | 開発者デバッグ |
| **詳細度** | 低（INFO+） | 高（DEBUG+） |
| **場所** | `~/.hermes/log/` | `~/.hermes/debug_log/` |
| **フィルタリング** | タスクID別 | ログレベル別 |
| **典型的な用途** | 実行のモニター | 失敗のトラブルシューティング |

通常のモニタリングには`hermes log`を、調査には`hermes debug`を使用してください。

## 関連コマンド

- [`hermes debug`](./debug.md) - 詳細なデバッグログを表示
- [`hermes history`](./history.md) - 実行結果を表示
- [`hermes run`](./run.md) - タスクを実行

## 注意事項

- ログエントリは即座に書き込まれます（バッファリングなし）
- 構造化された形式により簡単な解析が可能
- タイムスタンプにはタイムゾーンオフセットが含まれます
- タスクID形式は常に`YYYY-NNNN`
- フォローモードはパイプと併用可能: `hermes log -f | grep ERROR`

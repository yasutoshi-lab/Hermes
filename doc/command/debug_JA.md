# hermes debug

## 概要

トラブルシューティングと開発のためにログレベルでフィルタリングされた詳細なデバッグログを表示します。

## シノプシス

```bash
hermes debug
hermes debug --error
hermes debug --warning
hermes debug --info
hermes debug --all
hermes debug -n COUNT
hermes debug --follow
```

## 説明

`debug`コマンドは、`~/.hermes/debug_log/`に保存された詳細なデバッグログへのアクセスを提供します。これらのログには以下が含まれます:

- 内部状態遷移
- スタックトレース付きの詳細なエラートレース
- APIリクエスト/レスポンスの詳細
- パフォーマンスメトリクス
- ノードレベルのワークフローイベント

デバッグログは通常のログよりも詳細であり、以下を目的としています:
- 実行失敗のトラブルシューティング
- パフォーマンス分析
- 開発とデバッグ
- ワークフロー内部の理解

## オプション

| オプション | 型 | デフォルト | 説明 |
|--------|------|---------|-------------|
| `-n, --lines INT` | 整数 | `50` | 表示するログ行数 |
| `--error` | フラグ | `false` | ERRORレベルのログのみを表示 |
| `--warning` | フラグ | `false` | WARNINGレベルのログのみを表示 |
| `--info` | フラグ | `false` | INFOレベルのログのみを表示 |
| `--all` | フラグ | `false` | すべてのログレベルを表示（明示的） |
| `-f, --follow` | フラグ | `false` | ログをリアルタイムでストリーミング |

## ログレベルの優先順位

複数のレベルフラグが指定された場合、最も具体的なものが優先されます:

1. `--error` (最も具体的)
2. `--warning`
3. `--info`
4. `--all`またはなし（デフォルト、すべてのレベルを表示）

## ログ形式

デバッグログは通常のログと同じ形式に従いますが、追加の詳細があります:

```
YYYY-MM-DDTHH:MM:SS.mmmmmm+TZ [LEVEL] [MODULE] Detailed message
```

### 例

```
2025-11-14T14:28:30.123456+09:00 [DEBUG] [nodes.query_generator] Generating queries for prompt="quantum computing"
2025-11-14T14:28:31.234567+09:00 [DEBUG] [tools.ollama_client] Sending request to http://localhost:11434/api/chat
2025-11-14T14:28:35.345678+09:00 [DEBUG] [tools.ollama_client] Received response: 347 tokens in 3.2s
2025-11-14T14:28:36.456789+09:00 [ERROR] [tools.browser_use_client] DuckDuckGo rate limit exceeded, retrying after 2s
```

## デバッグログのログレベル

| レベル | 説明 |
|-------|-------------|
| **DEBUG** | 詳細な内部操作、状態変更、API呼び出し |
| **INFO** | 主要なマイルストーンとワークフローの進行 |
| **WARNING** | 潜在的な問題、フォールバック、再試行、パフォーマンス低下 |
| **ERROR** | スタックトレース付きの失敗、タイムアウト、接続エラー |

## 例

### すべてのデバッグログを表示（デフォルト50行）

```bash
hermes debug
```

### 最新100行を表示

```bash
hermes debug -n 100
```

### エラーのみを表示

```bash
hermes debug --error -n 200
```

**出力:**
```
2025-11-14T14:28:36+09:00 [ERROR] [tools.browser_use_client] DuckDuckGo rate limit
2025-11-14T14:32:15+09:00 [ERROR] [tools.ollama_client] Request timeout after 180s
2025-11-14T14:35:22+09:00 [ERROR] [services.run_service] Execution failed: 'dict' object has no attribute 'validated_report'
Traceback (most recent call last):
  File "hermes_cli/services/run_service.py", line 121
  ...
```

### 警告とエラーを表示

```bash
hermes debug --warning -n 150
```

### INFOレベルのみを表示

```bash
hermes debug --info -n 75
```

### デバッグログをリアルタイムでフォロー

```bash
hermes debug --follow
```

**出力:**
```
Following debug logs [level=all] (Ctrl+C to exit)...

2025-11-14T14:40:00+09:00 [DEBUG] [nodes.prompt_normalizer] Normalizing prompt
2025-11-14T14:40:01+09:00 [DEBUG] [nodes.query_generator] Calling Ollama for queries
... (Ctrl+Cまで続く)
```

### エラーのみをフォロー

```bash
hermes debug --follow --error
```

**出力:**
```
Following debug logs [level=error] (Ctrl+C to exit)...

(エラーが発生するまで待機)
```

## デバッグログファイルの場所

デバッグログは日次ローテーションで`~/.hermes/debug_log/`に保存されます:

```
~/.hermes/debug_log/
├── hermes-20251114.log  # 今日
├── hermes-20251113.log  # 昨日
├── hermes-20251112.log
└── ...
```

## ユースケース

### Ollamaタイムアウトを調査

```bash
hermes debug --error -n 500 | grep -i timeout
```

### Webリサーチの失敗を確認

```bash
hermes debug --warning -n 200 | grep -i duckduckgo
```

### 検証ループの動作を分析

```bash
hermes debug -n 1000 | grep -i validator
```

### ノード実行順序をモニター

```bash
hermes debug --follow | grep -E "nodes\.(prompt|query|web|container|draft|validator|final)"
```

### 設定の問題をデバッグ

```bash
hermes debug -n 100 | grep -i config
```

### エラースタックトレースを抽出

```bash
hermes debug --error -n 500 > errors.log
```

## レベルフィルタリング動作

### --errorフラグ

`[ERROR]`レベルの行のみを表示:

```bash
hermes debug --error -n 100
```

エラー行に続くスタックトレースを含みます。

### --warningフラグ

`[WARNING]`レベルの行のみを表示:

```bash
hermes debug --warning -n 100
```

### --infoフラグ

`[INFO]`レベルの行のみを表示:

```bash
hermes debug --info -n 100
```

### --allまたはフラグなし

すべてのレベル（DEBUG, INFO, WARNING, ERROR）を表示:

```bash
hermes debug -n 100
# 以下と同等:
hermes debug --all -n 100
```

## 標準ツールとの組み合わせ

### モジュールごとのエラー数をカウント

```bash
hermes debug --error -n 1000 | grep -oE '\[.*?\]' | sort | uniq -c | sort -nr
```

### Ollamaレスポンス時間を抽出

```bash
hermes debug -n 500 | grep "Received response" | grep -oE '[0-9.]+s'
```

### 最も遅い操作を検索

```bash
hermes debug -n 1000 | grep -i "took" | sort -t ' ' -k 10 -nr | head -20
```

### フィルタリングされたエラーを保存

```bash
hermes debug --error -n 1000 > errors-$(date +%Y%m%d).log
```

## パフォーマンスノート

- デバッグログは通常のログよりも大幅に大きい（10〜50倍）
- レベルフィルタリングは行を読み取った後に発生（ファイルレベルではない）
- 大きな行数（>5000）は遅い場合があります
- フォローモードは最小限のオーバーヘッド

## デバッグログ管理

### ディスク使用量を確認

```bash
du -sh ~/.hermes/debug_log
```

デバッグログは大きくなる可能性があります（頻繁に使用すると1日あたり100MB以上）。

### 古いデバッグログをクリーン

```bash
# 7日より古いデバッグログを削除
find ~/.hermes/debug_log -name "hermes-*.log" -mtime +7 -delete
```

### 古いログを圧縮

```bash
# 3日より古いログを圧縮
find ~/.hermes/debug_log -name "hermes-*.log" -mtime +3 -exec gzip {} \;
```

### デバッグログを無効化

`~/.hermes/config.yaml`を編集:

```yaml
logging:
  level: INFO  # DEBUGから変更
  debug_log_dir: ~/.hermes/debug_log
```

これによりデバッグログの詳細度が減りますが、debug_logディレクトリへの書き込みは続けられます。

## 一般的なデバッグワークフロー

### 失敗したタスクを調査

```bash
# 1. タスクIDを検索
hermes history --limit 10 | grep failed

# 2. エラーを確認
hermes debug --error -n 500 | grep task_id=2025-0003

# 3. 警告を確認
hermes debug --warning -n 500 | grep task_id=2025-0003

# 4. 完全なコンテキスト
hermes debug -n 2000 | grep task_id=2025-0003 > task-2025-0003-debug.log
```

### ライブ実行をモニター

```bash
# ターミナル1: タスクを実行
hermes run --prompt "複雑なクエリ"

# ターミナル2: エラーを監視
hermes debug --follow --error

# ターミナル3: すべてのアクティビティを監視
hermes debug --follow
```

### パフォーマンスを分析

```bash
# タイミング情報を抽出
hermes debug -n 2000 | grep -E "(took|duration|elapsed|seconds)" | less
```

## 終了コード

- **0**: 成功
- **1**: デバッグサービスエラー

## 通常のログとの比較

| 機能 | `hermes log` | `hermes debug` |
|---------|--------------|----------------|
| **詳細度** | 低 | 非常に高 |
| **対象者** | エンドユーザー | 開発者 |
| **場所** | `~/.hermes/log/` | `~/.hermes/debug_log/` |
| **ファイルサイズ** | 小（1〜10 MB/日） | 大（50〜500 MB/日） |
| **スタックトレース** | なし | あり |
| **パフォーマンスデータ** | なし | あり |
| **フィルタリング** | タスクID別 | ログレベル別 |

## トラブルシューティング

### デバッグログがない

デバッグログが有効になっていることを確認:
```bash
cat ~/.hermes/config.yaml | grep -A 3 logging
```

デバッグログディレクトリが存在することを確認:
```bash
ls -la ~/.hermes/debug_log/
hermes init  # 欠落している場合は再作成
```

### 出力が多すぎる

レベルフィルタリングを使用:
```bash
hermes debug --error -n 50  # エラーのみ
hermes debug --warning -n 100  # 警告以上
```

### フォローモードが動作しない

タスクが実行中であることを確認:
```bash
ps aux | grep hermes
```

### ログファイルが見つからない

デバッグログは最初の書き込み時に作成されます。タスクを実行:
```bash
hermes run --prompt "テストクエリ"
hermes debug -n 20
```

## 関連コマンド

- [`hermes log`](./log.md) - ユーザー向けログを表示
- [`hermes history`](./history.md) - 実行結果を表示
- [`hermes run`](./run.md) - タスクを実行

## 注意事項

- デバッグログは無期限に保持されます（手動クリーンアップが必要）
- スタックトレースは複数行にまたがります（レベルでフィルタリングされません）
- タイムスタンプにはパフォーマンス分析用のマイクロ秒が含まれます
- フォローモードはレベルフィルタリングと併用可能
- デバッグログには機密データ（プロンプト内容、APIレスポンス）が含まれる場合があります
- パフォーマンスとディスク容量のため、本番環境ではデバッグログを無効化してください

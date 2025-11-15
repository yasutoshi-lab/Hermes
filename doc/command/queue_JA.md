# hermes queue

## 概要

タスクキューからスケジュール済みタスクを空になるかまたは制限に達するまで順次処理します。

## シノプシス

```bash
hermes queue
hermes queue --all
hermes queue -n COUNT
hermes queue --limit COUNT
```

## 説明

`queue`コマンドは、スケジュール済みタスクをFIFO（先入れ先出し）順で実行します。以下を実行します:

1. `status: scheduled`のすべてのタスクを取得
2. 作成タイムスタンプで並べ替え（古いものから）
3. `RunService`を使用して各タスクを実行
4. タスクステータスを更新（`running` → `completed`）
5. 実行サマリーテーブルを生成

このコマンドは、手動介入なしで複数のリサーチタスクをバッチ処理するのに最適です。

## オプション

| オプション | 型 | デフォルト | 説明 |
|--------|------|---------|-------------|
| `-n, --limit INT` | 整数 | `1` | 実行するタスクの最大数 |
| `--all` | フラグ | `false` | キュー全体を処理（`--limit`をオーバーライド） |

### 制限の動作

- **デフォルト** (`hermes queue`): 1つのタスクを処理
- **特定の数** (`-n 5`): 最大5つのタスクを処理
- **無制限** (`--all`または`-n 0`): すべてのスケジュール済みタスクを処理

## 例

### 1つのタスクを処理（デフォルト）

```bash
hermes queue
```

**出力:**
```
Queue Execution Summary
┏━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Task ID  ┃ Status  ┃ Report               ┃ Error  ┃
┡━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ 2025-001 │ success │ report-2025-001.md   │        │
└──────────┴─────────┴──────────────────────┴────────┘

✓ Completed queue run: 1 succeeded, 0 failed.
```

### 最初の3つのタスクを処理

```bash
hermes queue -n 3
```

### キュー全体を空にする

```bash
hermes queue --all
```

**出力:**
```
Queue Execution Summary
┏━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Task ID  ┃ Status  ┃ Report               ┃ Error            ┃
┡━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ 2025-001 │ success │ report-2025-001.md   │                  │
│ 2025-002 │ success │ report-2025-002.md   │                  │
│ 2025-003 │ failed  │                      │ Ollama timeout   │
│ 2025-004 │ success │ report-2025-004.md   │                  │
└──────────┴─────────┴──────────────────────┴──────────────────┘

✓ Completed queue run: 3 succeeded, 1 failed.
```

### 短い構文ですべてを処理

```bash
hermes queue -n 0
```

## 実行フロー

キュー内の各タスクについて:

1. **タスクをロード**: `~/.hermes/task/task-YYYY-NNNN.yaml`からYAMLを読み込み
2. **ステータスを更新**: `status: running`に設定
3. **ワークフローを実行**: `RunService.run_task(task_id)`を呼び出し
4. **レポートを保存**: `~/.hermes/history/`に書き込み
5. **メタデータを更新**: 結果で`HistoryMeta`を作成
6. **完了を処理**: タスクはタスクディレクトリに残りますが、完了としてマーク

実行が失敗した場合、タスクは失敗としてマークされ、キューは次のタスクに続きます。

## 出力サマリー

実行サマリーテーブルには以下が表示されます:

- **Task ID**: 一意の識別子（YYYY-NNNN形式）
- **Status**: `success`（緑）または`failed`（赤）
- **Report**: レポートファイル名（成功したタスクのみ）
- **Error**: エラーメッセージ（失敗したタスクのみ）

最終サマリー行には、成功と失敗の合計数が表示されます。

## 順次処理

タスクは**順次**（並列ではなく）処理されます:

- 各タスクは次のタスクが開始される前に完了
- 合計実行時間 = 個別タスク時間の合計
- 失敗したタスクはキュー処理を停止しない
- Ollamaサーバーは一度に1つのリクエストを処理

## 終了コード

- **0**: 成功（すべての処理済みタスクが完了、一部が失敗した場合も含む）
- **1**: キューサービスエラー（インフラストラクチャー障害）

注意: 個別のタスク失敗は終了コード0になります。タスクごとのステータスはサマリーテーブルを確認してください。

## 空のキュー処理

```bash
hermes queue --all
```

**出力:**
```
No scheduled tasks to process
```

これはエラーではありません。終了コードは0です。

## ユースケース

### 夜間バッチ処理

```bash
# 日中にタスクをスケジュール
hermes task --prompt "トピック1の分析"
hermes task --prompt "トピック2のリサーチ"
hermes task --prompt "トピック3のまとめ"
# ... （さらにタスクを追加）

# cron経由で夜間に実行
0 2 * * * cd /path/to/project && hermes queue --all >> queue.log 2>&1
```

### レート制限された処理

```bash
# レート制限を回避するため、1時間ごとに3つのタスクを処理
hermes queue -n 3
```

### バッチ間の手動レビュー

```bash
# 一度に1つずつ処理し、結果をレビュー
hermes queue
hermes history --limit 1
# ... レポートをレビュー ...
hermes queue
# ... 繰り返し ...
```

## Cron/Systemdとの統合

### Cronの例

```cron
# 毎日午前2時にキューを処理
0 2 * * * /home/user/.venv/bin/hermes queue --all

# 6時間ごとに5つのタスクを処理
0 */6 * * * /home/user/.venv/bin/hermes queue -n 5
```

### Systemdタイマーの例

```ini
# /etc/systemd/system/hermes-queue.service
[Unit]
Description=Hermes Queue Processor
After=network.target

[Service]
Type=oneshot
User=hermes-user
WorkingDirectory=/home/hermes-user
ExecStart=/home/hermes-user/.venv/bin/hermes queue --all
```

```ini
# /etc/systemd/system/hermes-queue.timer
[Unit]
Description=Run Hermes queue daily

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

## パフォーマンスに関する考慮事項

### 実行時間の見積もり

各タスクが平均約3分かかる場合:

- 1タスク: 約3分
- 10タスク: 約30分
- 50タスク: 約2.5時間

大きなキューで`--all`を使用する場合は、それに応じて計画してください。

### Ollamaリソース使用量

- Ollamaは一度に1つのタスクを処理（並列実行なし）
- キュー処理中はGPU/CPUの使用率が高くなります
- 無人実行には十分なシステムリソースを確保してください

## トラブルシューティング

### スケジュール済みタスクが見つからない

タスクディレクトリを確認:
```bash
hermes task --list
ls ~/.hermes/task/
```

最初にタスクを作成:
```bash
hermes task --prompt "リサーチトピック"
```

### すべてのタスクが失敗

Ollamaサーバーを確認:
```bash
curl http://localhost:11434/api/version
ollama list
```

ログをレビュー:
```bash
hermes log -n 100
hermes debug --error -n 50
```

### キュー処理が中断された

キューコマンドを再実行して再開:
```bash
hermes queue --all
```

中断時に`running`としてマークされたタスクはスキップされます。必要に応じてYAMLファイルを編集してステータスを手動でリセットしてください。

### タスクが'running'状態でスタック

タスクが実行途中で中断された場合:

```bash
# タスクファイルを見つける
ls ~/.hermes/task/task-YYYY-NNNN.yaml

# ステータスを手動で'scheduled'に戻す
# 次に再実行
hermes queue
```

## 関連コマンド

- [`hermes task`](./task.md) - スケジュール済みタスクを作成および管理
- [`hermes run --task-id`](./run.md) - IDで単一タスクを実行
- [`hermes history`](./history.md) - 完了したタスクの結果を表示
- [`hermes log`](./log.md) - 実行ログをモニター

## 注意事項

- タスクファイルは完了後も`~/.hermes/task/`に残ります
- 完了したタスクを削除するには`hermes task --delete`を使用
- 失敗したタスクはステータスを`scheduled`に戻すことで再実行可能
- キュー処理はタスク定義からのすべての設定オーバーライドを尊重します

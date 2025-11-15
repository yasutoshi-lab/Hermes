# hermes task

## 概要

`hermes run`または`hermes queue`で後で実行できるスケジュール済みタスクを管理します。

## シノプシス

```bash
hermes task --prompt "リサーチ質問"
hermes task --list
hermes task --delete TASK_ID
```

## 説明

`task`コマンドは、プロンプトとメタデータをYAMLファイルとして`~/.hermes/task/`に保存することで、タスクスケジューリング機能を提供します。タスクはすぐには実行されません。処理するには`hermes run --task-id`または`hermes queue`を使用してください。

これは以下のような場合に便利です:
- 複数のリサーチトピックをバッチ処理
- オフピーク時に実行するタスクをスケジュール
- 後で調査するための興味深いプロンプトを保存
- リサーチ質問のバックログを構築

## オプション

| オプション | 型 | 説明 |
|--------|------|-------------|
| `--prompt TEXT` | 文字列 | 指定されたプロンプトで新しいタスクを作成 |
| `--list` | フラグ | すべてのスケジュール済みタスクを表示 |
| `--delete TEXT` | 文字列 | IDでタスクを削除 |
| `--deleate TEXT` | 文字列 | IDでタスクを削除（後方互換性のためのタイプミスエイリアス） |

## タスクのライフサイクル

タスクには3つの状態があります:

1. **scheduled** - 作成済みだが未実行
2. **running** - 現在処理中（`RunService`により設定）
3. **completed** - 実行完了（履歴にアーカイブ）

`task`コマンドは**scheduled**状態のタスクのみを管理します。

## 例

### 新しいタスクを作成

```bash
hermes task --prompt "量子コンピューティングが暗号化に与える影響を分析する"
```

**出力:**
```
✓ Task created: 2025-0010
Prompt: 量子コンピューティングが暗号化に与える影響を分析する
Status: scheduled

Execute with: hermes run --task-id 2025-0010
```

### すべてのスケジュール済みタスクをリスト表示

```bash
hermes task --list
```

**出力:**
```
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Task ID  ┃ Created         ┃ Status    ┃ Prompt                      ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2025-001 │ 2025-11-14 1... │ scheduled │ 量子コンピューティング分析    │
│ 2025-002 │ 2025-11-14 1... │ scheduled │ AI安全性リサーチまとめ       │
│ 2025-003 │ 2025-11-14 1... │ running   │ 気候変動ソリューション        │
└──────────┴─────────────────┴───────────┴─────────────────────────────┘
```

### タスクを削除

```bash
hermes task --delete 2025-0001
```

**出力:**
```
✓ Task 2025-0001 deleted
```

### タイプミスエイリアスを使用して削除

```bash
hermes task --deleate 2025-0002
```

**出力:**
```
✓ Task 2025-0002 deleted
```

## タスクファイル形式

タスクは`~/.hermes/task/`にYAMLファイルとして保存されます:

```yaml
# task-2025-0001.yaml
id: 2025-0001
prompt: "量子誤り訂正方法を説明する"
created_at: "2025-11-14T10:30:00+09:00"
status: scheduled
language: ja
config_overrides: {}
```

## スケジュール済みタスクの実行

### 単一タスクを実行

```bash
hermes run --task-id 2025-0001
```

### すべてのスケジュール済みタスクを実行

```bash
hermes queue --all
```

### 最初のN個のタスクを実行

```bash
hermes queue -n 5
```

## 終了コード

- **0**: 成功
- **1**: タスクが見つからない（削除操作の場合）
- **2**: 無効な引数

## 注意事項

- タスクIDは`YYYY-NNNN`形式で自動生成されます（例: `2025-0042`）
- タスクはHermesの再起動後も保持されます
- タスクを削除しても、すでに実行されている場合は実行履歴には影響しません
- `--deleate`オプションは一般的なタイプミスに対応するために存在します（両方のスペルが機能します）
- 実行中のタスクはリストに「running」と表示されますが、完了するまでタスクディレクトリに残ります

## ワークフロー統合

### 典型的なワークフロー

```bash
# 1. 複数のタスクを作成
hermes task --prompt "トピックAのリサーチ"
hermes task --prompt "トピックBの分析"
hermes task --prompt "トピックCのまとめ"

# 2. キューを確認
hermes task --list

# 3. すべてを一度に実行
hermes queue --all

# 4. 結果を確認
hermes history --limit 10
```

## 関連コマンド

- [`hermes run --task-id`](./run.md) - 単一のスケジュール済みタスクを実行
- [`hermes queue`](./queue.md) - 複数のタスクを順次処理
- [`hermes history`](./history.md) - 完了したタスクの結果を表示

## ファイルの場所

- **タスクファイル**: `~/.hermes/task/task-YYYY-NNNN.yaml`
- **設定**: `~/.hermes/config.yaml` (新しいタスクのデフォルト設定)

## トラブルシューティング

### リスト表示時にタスクが見つからない

Hermesが初期化されていることを確認してください:
```bash
hermes init
ls ~/.hermes/task/
```

### タスクを削除できない

タスクIDが存在するか確認してください:
```bash
hermes task --list
# リストから正確なIDを使用
```

### タスク作成が失敗する

ディスク容量と権限を確認してください:
```bash
df -h ~/.hermes
ls -ld ~/.hermes/task
```

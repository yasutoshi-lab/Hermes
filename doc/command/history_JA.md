# hermes history

## 概要

実行履歴と生成されたレポートをリスト、エクスポート、および管理します。

## シノプシス

```bash
hermes history
hermes history --limit COUNT
hermes history --export TASK_ID:PATH
hermes history --delete TASK_ID
```

## 説明

`history`コマンドは、完了したリサーチタスクの結果へのアクセスを提供します。各実行は以下を生成します:

- **レポートファイル**: リサーチ結果を含むMarkdownドキュメント（`report-YYYY-NNNN.md`）
- **メタデータファイル**: 実行詳細を含むYAML（`report-YYYY-NNNN.meta.yaml`）

履歴エントリは明示的に削除されるまで無期限に保持されます。

## オプション

| オプション | 型 | デフォルト | 説明 |
|--------|------|---------|-------------|
| `--limit INT` | 整数 | `100` | 表示する履歴エントリの最大数 |
| `--export TEXT` | 文字列 | なし | `TASK_ID:PATH`形式でレポートをエクスポート |
| `--delete TEXT` | 文字列 | なし | タスクIDで履歴エントリを削除 |
| `--deleate TEXT` | 文字列 | なし | IDで履歴を削除（タイプミスエイリアス） |

## 例

### 最近の履歴をリスト表示（デフォルト100エントリ）

```bash
hermes history
```

**出力:**
```
Execution History (last 5)
┏━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━┓
┃ Task ID ┃ Status  ┃ Created        ┃ Finished     ┃ Model    ┃ Loops ┃ Sources ┃ Error ┃
┡━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━┩
│ 2025-05 │ success │ 2025-11-14 ... │ 14:30 (142s) │ gpt-o... │     2 │      24 │       │
│ 2025-04 │ success │ 2025-11-14 ... │ 14:15 (98s)  │ gpt-o... │     1 │      18 │       │
│ 2025-03 │ failed  │ 2025-11-14 ... │ 13:50 (5s)   │ gpt-o... │     0 │       0 │ Time… │
│ 2025-02 │ success │ 2025-11-14 ... │ 13:30 (215s) │ gpt-o... │     3 │      36 │       │
│ 2025-01 │ success │ 2025-11-14 ... │ 10:15 (87s)  │ gpt-o... │     1 │      12 │       │
└─────────┴─────────┴────────────────┴──────────────┴──────────┴───────┴─────────┴───────┘
```

### 最新10エントリをリスト表示

```bash
hermes history --limit 10
```

### 特定のレポートをエクスポート

```bash
hermes history --export 2025-0005:./quantum-report.md
```

**出力:**
```
✓ Report exported to ./quantum-report.md
```

### 相対パスでエクスポート

```bash
hermes history --export 2025-0003:../reports/ai-safety.md
```

### 履歴エントリを削除

```bash
hermes history --delete 2025-0001
```

**出力:**
```
✓ History 2025-0001 deleted
```

これにより、レポートとメタデータファイルの両方が削除されます。

## 履歴テーブルの列

| 列 | 説明 |
|--------|-------------|
| **Task ID** | 一意の識別子（YYYY-NNNN形式） |
| **Status** | `success`（緑）または`failed`（赤） |
| **Created** | 実行開始タイムスタンプ |
| **Finished** | 完了時刻と期間 |
| **Model** | 使用されたOllamaモデル（切り捨て） |
| **Loops** | 実行された検証ループ数 |
| **Sources** | 収集されたWebソースの合計 |
| **Error** | エラーメッセージ（切り捨て、失敗時のみ） |

## メタデータファイル形式

各履歴エントリにはメタデータファイルがあります:

```yaml
# ~/.hermes/history/report-2025-0005.meta.yaml
id: 2025-0005
prompt: "量子コンピューティングのエラー訂正を説明する"
created_at: "2025-11-14T14:28:30+09:00"
finished_at: "2025-11-14T14:30:52+09:00"
model: gpt-oss:20b
language: ja
validation_loops: 2
source_count: 24
report_file: report-2025-0005.md
status: success
error_message: null
```

## レポートファイル形式

レポートは構造化されたMarkdownです:

```markdown
---
query: <元のプロンプト>
language: ja
queries_generated: 3
queries_executed: 6
sources_collected: 24
validation_loops: 2
quality_score: 0.85
---

# <レポートタイトル>

## エグゼクティブサマリー
...

## 主要な発見
...

## 詳細なサポート
...

## 推奨される次のステップ
...
```

## エクスポートの動作

### 成功ケース

```bash
hermes history --export 2025-0001:./report.md
```

- レポートファイルが指定されたパスにコピーされます
- 宛先の既存ファイルは上書きされます
- 必要に応じて親ディレクトリが作成されます

### 失敗ケース

```bash
# タスクが見つからない
hermes history --export 2025-9999:./report.md
# 出力: ✗ History 2025-9999 not found

# タスクが失敗（レポート未生成）
hermes history --export 2025-0003:./report.md
# 出力: ✗ History 2025-0003 failed; no report to export
# 理由: Ollama timeout
```

### 無効な形式

```bash
# コロン区切りがない
hermes history --export 2025-0001 ./report.md
# 出力: ✗ Export format must be TASK_ID:PATH (e.g., 2025-0001:./report.md)
```

## ファイルの場所

履歴ファイルは`~/.hermes/history/`に保存されます:

```
~/.hermes/history/
├── report-2025-0001.md         # レポートMarkdown
├── report-2025-0001.meta.yaml  # メタデータ
├── report-2025-0002.md
├── report-2025-0002.meta.yaml
└── ...
```

## フィルタリングとソート

### ステータス別

失敗したタスクは赤でエラーメッセージとともに表示されます:

```bash
hermes history | grep -E "failed|✗"
```

### 日付別

履歴は作成時刻でソートされます（新しいものから）:

```bash
# 最も古いエントリ
hermes history --limit 1000 | tail -20
```

### モデル別

```bash
hermes history | grep "llama"
```

## 終了コード

- **0**: 成功
- **1**: 操作失敗（エクスポート/削除）
- **2**: 無効な引数

## ユースケース

### サマリーレポートを生成

```bash
# すべての最近のレポートをエクスポート
for id in $(hermes history --limit 10 | grep -oE '2025-[0-9]{4}'); do
  hermes history --export "$id:reports/$id.md"
done
```

### 古い履歴をクリーンアップ

```bash
# すべての失敗したタスクを削除
for id in $(hermes history | grep failed | grep -oE '2025-[0-9]{4}'); do
  hermes history --delete "$id"
done
```

### 成功したレポートをアーカイブ

```bash
# レポートをアーカイブディレクトリにコピー
mkdir -p archive/$(date +%Y-%m)
for id in $(hermes history --limit 30 | grep success | grep -oE '2025-[0-9]{4}'); do
  cp ~/.hermes/history/report-$id.md archive/$(date +%Y-%m)/
done
```

## パフォーマンスノート

- 履歴のリスト表示は`~/.hermes/history/`内のすべてのメタデータファイルをスキャンします
- 数千のエントリがある場合、読み込み時間を短縮するため`--limit`の使用を検討してください
- エクスポートは単純なファイルコピー操作です（高速）
- 削除は`.md`と`.meta.yaml`ファイルの両方をアトミックに削除します

## トラブルシューティング

### 履歴が見つからない

タスクが実行されたことを確認:
```bash
hermes run --prompt "テストクエリ"
hermes history
```

### エクスポートパスエラー

親ディレクトリが存在することを確認:
```bash
mkdir -p reports/
hermes history --export 2025-0001:reports/test.md
```

### メタデータが破損

メタデータが破損している場合、手動で検査:
```bash
cat ~/.hermes/history/report-2025-0001.meta.yaml
```

回復が不可能な場合はタスクを再実行してください。

### エクスポート時に権限拒否

書き込み権限があることを確認:
```bash
touch ./test.md
hermes history --export 2025-0001:./test.md
```

## 関連コマンド

- [`hermes run`](./run.md) - 新しいレポートを生成
- [`hermes task`](./task.md) - 実行のためにタスクをスケジュール
- [`hermes queue`](./queue.md) - 複数のタスクを処理
- [`hermes log`](./log.md) - 実行ログを表示

## 注意事項

- 履歴はHermesの再インストール後も保持されます（`~/.hermes/`に保存）
- 履歴を削除してもタスク定義には影響しません
- 失敗したタスクでもメタデータファイルは作成されます（監査のため）
- `--deleate`タイプミスエイリアスは後方互換性のために提供されています
- エクスポートは元のレポートファイルを変更しません

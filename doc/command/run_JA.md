# hermes run

## 概要

Ollama LLMとWeb検索機能を使用したLangGraphワークフローでリサーチタスクを実行します。

## シノプシス

```bash
hermes run --prompt "リサーチ質問" [OPTIONS]
hermes run --task-id TASK_ID [OPTIONS]
hermes run --export PATH
hermes run --clear
```

## 説明

`run`コマンドは、リサーチタスクを実行するための主要なインターフェースです。以下を実行します:

1. 入力プロンプトを正規化
2. Ollamaを使用して検索クエリを生成
3. DuckDuckGo（または利用可能な場合はbrowser-use）経由でソースを収集
4. コンテンツを処理および正規化
5. ドラフトレポートを生成
6. 設定されたループ反復を通じて検証および改善
7. 最終レポートを`~/.hermes/history/`に保存

## オプション

### コアオプション

| オプション | 型 | 説明 |
|--------|------|-------------|
| `--prompt TEXT` | 文字列 | 調査するリサーチ質問またはプロンプト |
| `--task-id TEXT` | 文字列 | IDで事前スケジュール済みタスクを実行 |
| `--export PATH` | パス | 最新のレポートを指定パスにエクスポート |
| `--clear` | フラグ | 設定をデフォルトにリセットして終了 |

### LLM設定

| オプション | 型 | デフォルト | 説明 |
|--------|------|---------|-------------|
| `--api TEXT` | 文字列 | `http://localhost:11434/api/chat` | Ollama APIエンドポイント |
| `--model TEXT` | 文字列 | `gpt-oss:20b` | 使用するモデル名 |
| `--retry INT` | 整数 | `3` | 失敗したリクエストの再試行回数 |

### Validation制御

| オプション | 型 | デフォルト | 説明 |
|--------|------|---------|-------------|
| `--min-validation INT` | 整数 | `1` | 最小検証ループ（常に適用） |
| `--max-validation INT` | 整数 | `3` | 最大検証ループ（ハードリミット） |

### 検索設定

| オプション | 型 | デフォルト | 説明 |
|--------|------|---------|-------------|
| `--min-search INT` | 整数 | `3` | クエリごとに収集する最小ソース数 |
| `--max-search INT` | 整数 | `8` | クエリごとに収集する最大ソース数 |
| `--query INT` | 整数 | `3` | 生成する検索クエリ数 |

### 出力設定

| オプション | 型 | デフォルト | 説明 |
|--------|------|---------|-------------|
| `--language TEXT` | 文字列 | `ja` | 出力言語コード（`ja`または`en`） |

## 例

### 基本的なリサーチタスク

```bash
hermes run --prompt "量子コンピューティングのエラー訂正について説明する"
```

**出力:**
```
⠙ Executing research task...
╭───────── Execution Complete ─────────╮
│ ✓ Task completed successfully!      │
│                                      │
│ Task ID: 2025-0001                   │
│ Model: gpt-oss:20b                   │
│ Sources: 24                          │
│ Validation loops: 2                  │
│ Duration: 142s                       │
│                                      │
│ Report: ~/.hermes/history/...        │
╰──────────────────────────────────────╯
```

### カスタム検証を使用した英語出力

```bash
hermes run \
  --prompt "Latest developments in AI safety research" \
  --language en \
  --min-validation 2 \
  --max-validation 5
```

### 異なるモデルを使用

```bash
hermes run \
  --prompt "量子コンピュータの現状" \
  --model llama2:70b \
  --language ja
```

### スケジュール済みタスクを実行

```bash
# まず、タスクを作成
hermes task --prompt "週刊AIニュースまとめ"

# 次に実行
hermes run --task-id 2025-0042
```

### 最近のレポートをエクスポート

```bash
hermes run --export ./my-report.md
```

### 設定をリセット

```bash
hermes run --clear
```

## ワークフローステージ

リサーチワークフローは以下のステージを進行します:

1. **プロンプト正規化** - 入力をクリーンアップおよび検証
2. **クエリ生成** - 多様な検索クエリを作成（Ollama）
3. **Web リサーチ** - ソースを収集（DuckDuckGo/browser-use）
4. **コンテナ処理** - テキストを正規化（Docker/ローカルフォールバック）
5. **ドラフト集約** - 初期レポートを合成（Ollama）
6. **Validationコントローラー** - 品質とループ制限を確認
7. **Validator** - 批評してフォローアップクエリを生成（Ollama）
8. **最終レポーター** - メタデータを追加してレポートを完成

ワークフローは検証設定に基づいてステージ3-7間でループします。

## 出力ファイル

各実行は以下を作成します:

- **レポートファイル**: `~/.hermes/history/report-YYYY-NNNN.md`
- **メタデータファイル**: `~/.hermes/history/report-YYYY-NNNN.meta.yaml`
- **ログエントリ**: `~/.hermes/log/hermes-YYYYMMDD.log`

## 終了コード

- **0**: 成功 - レポート生成
- **1**: 実行失敗（ログを参照）
- **2**: 無効な引数
- **3**: 検証失敗（レポート未生成）

## 環境要件

### 必須サービス

- **Ollamaサーバー**: 実行中である必要があります（`ollama serve`）
  ```bash
  # ステータスを確認
  curl http://localhost:11434/api/version
  ```

- **モデル**: ローカルにプル済みである必要があります
  ```bash
  ollama pull gpt-oss:20b
  ```

### オプションサービス

- **Docker**: コンテナベースの処理用（利用不可の場合はローカルにフォールバック）
- **browser-use**: 高度なWeb自動化用（デフォルトでDuckDuckGoフォールバックを使用）

## 設定オーバーライド優先順位

設定は以下の順序で適用されます（後のものが優先）:

1. ハードコードされたデフォルト
2. `~/.hermes/config.yaml`
3. コマンドラインフラグ

例:
```yaml
# config.yamlでタイムアウトを180秒に設定
ollama:
  timeout_sec: 180
```

```bash
# この実行は180秒のタイムアウトを使用
hermes run --prompt "test"

# この実行は300秒のタイムアウトを使用（オーバーライド）
hermes run --prompt "test" --timeout 300
```

## パフォーマンスチューニング

### 高速実行（少ないソース、検証なし）

```bash
hermes run \
  --prompt "トピックの簡単なまとめ" \
  --min-validation 1 \
  --max-validation 1 \
  --max-search 3 \
  --query 2
```

### 包括的なリサーチ（多くのソース、徹底的な検証）

```bash
hermes run \
  --prompt "トピックの詳細分析" \
  --min-validation 3 \
  --max-validation 5 \
  --max-search 12 \
  --query 5
```

## トラブルシューティング

### タイムアウトエラー

`~/.hermes/config.yaml`でタイムアウトを増やす:

```yaml
ollama:
  timeout_sec: 300  # デフォルト: 180
```

### ソースが返されない

- インターネット接続を確認
- DuckDuckGoがレート制限していないか確認
- `--max-sources`を減らしてみる
- 実行間で1〜2分待つ

### モデルが見つからない

```bash
# 利用可能なモデルをリスト
ollama list

# 必要なモデルをプル
ollama pull gpt-oss:20b
```

### ワークフローがレポートを生成しなかった

エラーのログを確認:
```bash
hermes log -n 50
hermes debug --error -n 100
```

一般的な原因:
- Ollamaサーバーが実行されていない
- 複雑なクエリでのモデルタイムアウト
- すべてのWeb検索が失敗（レート制限）

## 関連コマンド

- [`hermes init`](./init.md) - ワークスペースを初期化
- [`hermes task`](./task.md) - 後で実行するタスクをスケジュール
- [`hermes queue`](./queue.md) - 複数のスケジュール済みタスクを実行
- [`hermes history`](./history.md) - レポートを表示およびエクスポート
- [`hermes log`](./log.md) - 実行ログを表示

## 注意事項

- `--clear`フラグは設定をリセットしますが、履歴とログは保持します
- 検証ループは実行時間を大幅に増加させる可能性があります
- DuckDuckGoは積極的なクエリをレート制限する場合があります
- 検証が失敗してもレポートは保存されます
- タスクIDは`YYYY-NNNN`形式に従います（例: `2025-0001`）

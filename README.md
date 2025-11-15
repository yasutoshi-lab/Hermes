# Hermes

**Hermes** は、研究者や技術者向けのローカル実行可能な CLI 情報収集エージェントです。

## 特徴

- 🔒 **完全ローカル実行**: 外部API課金なし、プライバシー保護
- 🔍 **メタ検索**: SearxNG経由で複数検索エンジンを統合
- 🤖 **検証ループ**: 情報の矛盾や不足を自動検出・修正
- 📝 **レポート生成**: Markdown形式で引用付きレポートを自動生成
- 🎯 **CLI特化**: シェルスクリプトとの統合が容易

## アーキテクチャ

```
User Input → CLI → Workflow Engine (LangGraph)
                      ↓
              ┌───────┴───────┐
              ↓               ↓
         Ollama (LLM)    SearxNG (Search)
              ↓               ↓
         gpt-oss:20b      Redis Cache
              ↓               ↓
         Report Generator ←───┘
              ↓
         Markdown Report
```

## 前提条件

- **OS**: Ubuntu 22.04 以上
- **Python**: 3.10 以上
- **Docker**: docker および docker-compose
- **GPU**: VRAM 16GB 推奨（Ollama用）

## インストール

### 1. リポジトリクローン

```bash
git clone https://github.com/yasutoshi-lab/Hermes.git
cd Hermes
```

### 2. 依存関係インストール

```bash
# uvインストール（未インストールの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係インストール
uv sync

# CLIインストール
uv pip install -e .
```

### 3. Ollama セットアップ

```bash
# Ollamaインストール
curl -fsSL https://ollama.com/install.sh | sh

# モデルダウンロード
ollama pull gpt-oss:20b

# サービス起動
ollama serve
```

### 4. Hermes 初期化

```bash
# ワークスペース初期化
hermes init

# Docker サービス起動
cd ~/.hermes
docker compose up -d
```

## 使い方

### 基本的な使用例

```bash
# 即時実行
hermes run --prompt "量子コンピュータの暗号化への影響を調査"

# タスク登録
hermes task --add "AI倫理の最新動向"

# タスク一覧表示
hermes task --list

# タスク実行
hermes run --task-id 2025-0001

# 履歴表示
hermes history

# ログ表示
hermes log --lines 100
```

### 詳細オプション

```bash
# 検証ループ数を調整
hermes run --prompt "..." --min-validation 2 --max-validation 5

# 検索クエリ数を指定
hermes run --prompt "..." --query 5

# レポートをエクスポート
hermes run --prompt "..." --export ./report.md

# デバッグモード
hermes log --debug --follow
```

## コマンドリファレンス

### `hermes init`

ワークスペースを初期化します。

```bash
hermes init [--work-dir PATH] [--clear]
```

### `hermes task`

タスクを管理します。

```bash
# タスク追加
hermes task --add "調査内容"

# タスク一覧
hermes task --list

# タスク削除
hermes task --remove 2025-0001
```

### `hermes run`

リサーチタスクを実行します。

```bash
hermes run [OPTIONS]

Options:
  --prompt TEXT              即時実行プロンプト
  --task-id TEXT            実行するタスクID
  --task-all                全タスク実行
  --export PATH             レポート出力パス
  --model TEXT              LLMモデル名
  --min-validation INT      最小検証ループ数
  --max-validation INT      最大検証ループ数
  --query INT               クエリ生成数
  --language [ja|en]        出力言語
```

### `hermes log`

ログを表示します。

```bash
hermes log [--lines N] [--follow] [--debug] [--task-id ID]
```

### `hermes history`

実行履歴を管理します。

```bash
# 履歴一覧
hermes history [--limit N]

# レポートエクスポート
hermes history --export 2025-0001:./report.md

# 履歴削除
hermes history --delete 2025-0001
```

## ディレクトリ構造

```
~/.hermes/
├── config.yaml              # 設定ファイル
├── docker-compose.yaml      # Docker設定
├── cache/                   # キャッシュ
├── task/                    # タスク定義
├── log/                     # 通常ログ
├── debug_log/               # デバッグログ
├── history/                 # 実行履歴とレポート
└── searxng/                 # SearxNG設定
```

## 設定

`~/.hermes/config.yaml` で設定をカスタマイズできます：

```yaml
# Ollama設定
ollama:
  api_url: http://localhost:11434/api/chat
  model: gpt-oss:20b
  timeout: 120
  temperature: 0.7

# 検索設定
search:
  query_count: 3
  min_search: 3
  max_search: 8

# 検証設定
validation:
  min_validation: 1
  max_validation: 3
```

## トラブルシューティング

### Ollama に接続できない

```bash
# Ollamaの状態確認
curl http://localhost:11434/api/tags

# サービス再起動
sudo systemctl restart ollama
```

### SearxNG に接続できない

```bash
# コンテナ状態確認
cd ~/.hermes
docker compose ps

# ログ確認
docker compose logs searxng

# サービス再起動
docker compose restart
```

### 検索結果が取得できない

- SearxNGの設定を確認: `~/.hermes/searxng/settings.yml`
- Redisの接続を確認
- ファイアウォール設定を確認

## 開発

### テスト実行

```bash
# 全テスト実行
pytest

# カバレッジ付き
pytest --cov=hermes_cli

# 特定テスト
pytest tests/unit/test_ollama_client.py
```

### コードフォーマット

```bash
# フォーマット
black hermes_cli/

# リント
ruff check hermes_cli/

# 型チェック
mypy hermes_cli/
```

## ライセンス

MIT License

## 参考

- [agenticSeek](https://github.com/Fosowl/agenticSeek) - 設計の参考
- [LangGraph](https://github.com/langchain-ai/langgraph) - ワークフローエンジン
- [SearxNG](https://github.com/searxng/searxng) - メタ検索エンジン
- [Ollama](https://ollama.com/) - ローカルLLM実行環境

## 貢献

Issue や Pull Request を歓迎します！

## 作者

Hermes Team

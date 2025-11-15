# Hermes CLI

Hermesは、LangGraphワークフロー、Ollama でホストされたLLM、および（将来的な）ブラウザ/コンテナ統合を組み合わせて、情報収集、検証ループの反復、ローカルでのレポート保存を行う、CLI ファーストのリサーチエージェントです。

## 機能

- 🤖 **LLM駆動のワークフロー** – Typer CLI がプロンプトを LangGraph グラフ
  (`hermes_cli/agents/graph.py`) に送り込み、入力を正規化し、クエリを生成し、
  構造化されたマークダウンレポートを作成します。
- 🔁 **設定可能な検証ループ** – `~/.hermes/config.yaml` が `validation_controller` によって
  実行される最小/最大検証サイクルを制御します。各ループは制限に達するまでドラフトステージに
  再度入ります。
- 🗂️ **ファイルベースの永続化** – タスク、ログ、履歴は `hermes_cli/persistence/` の
  リポジトリを介して `~/.hermes/` 配下に YAML とマークダウンとして永続化されます。
- 🛠️ **サービスレイヤーの抽象化** – コマンドはサービス（config、run、task、history、log、debug）
  に処理を委譲し、他のエントリポイントでも再利用可能です。
- 📜 **完全な監査証跡** – `hermes history`、`hermes log`、`hermes debug` が
  レポートのエクスポート、構造化ログ、フィルタリングされたデバッグストリームを提供します。
- 🌐 **Web リサーチ機能** – DuckDuckGo 統合により即座に Web 検索機能を提供。
  高度な自動化のための browser-use アップグレードもオプションで利用可能です。
- 🐳 **コンテナ分離** – dagger-io を介した Docker ベースの処理。コンテナが
  利用できない場合は自動的にローカル処理にフォールバックします。

## 前提条件

- Python 3.10+ (CPython 3.10-3.12 でテスト済み。仮想環境の使用を推奨)
- 依存関係管理のための `uv` または `pip`
- `gpt-oss:20b` モデルがローカルにプルされた [Ollama](https://ollama.ai/)
  ```bash
  # https://ollama.ai/download から Ollama をインストール
  # 必要なモデルをプル
  ollama pull gpt-oss:20b

  # Ollama サーバーを起動（別のターミナルで実行し続ける）
  ollama serve
  ```
- **Docker** (container-use 統合に必要)
  - Docker 20.10+ を推奨
  - 詳細な手順については[統合のセットアップ](#統合のセットアップ)セクションを参照
- **オプション: browser-use** 高度な Web 自動化のため
  - これがなくても DuckDuckGo フォールバックが機能します
  - インストール方法は[統合のセットアップ](#統合のセットアップ)セクションを参照

> ℹ️ Hermes は LLM 操作のために `ollama serve` の実行が必要です。Web リサーチは
> DuckDuckGo で箱から出してすぐに動作します。browser-use をインストールすると
> 拡張機能が利用可能になります。container-use は Docker が利用可能な場合に分離処理を
> 提供し、それ以外の場合はローカル処理にフォールバックします。

## インストール

```bash
git clone https://example.com/Hermes.git
cd Hermes

# 仮想環境を作成してアクティベート（パス/シェルは適宜調整）
python -m venv .venv
source .venv/bin/activate

# pip を使用した編集可能インストール
pip install -e .

# または uv を使用してインストール（より高速なリゾルバ）
uv pip install -e .

# 注意: DuckDuckGo Web 検索はすぐに動作します。
# 高度なブラウザ自動化については、以下の統合のセットアップセクションを参照してください。
```

開発者ツール（pytest、ruff、mypy、black）を含める場合:

```bash
pip install -e .[dev]
# または
uv pip install -e '.[dev]'
```

## 統合のセットアップ

### Container-use (dagger-io)

Hermes は分離されたテキスト正規化と処理のために container-use（dagger-io 経由）を使用します。`dagger-io` パッケージは自動的にインストールされますが、完全な機能を利用するには Docker が実行されている必要があります。

**セットアップ手順:**

1. **Docker のインストール**（まだインストールされていない場合）:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install docker.io
   sudo systemctl start docker
   sudo systemctl enable docker

   # macOS (Docker Desktop を使用)
   # https://www.docker.com/products/docker-desktop からダウンロード

   # インストールの確認
   docker --version
   ```

2. **ユーザーを docker グループに追加**（Linux のみ、sudo を避けるため）:
   ```bash
   sudo usermod -aG docker $USER
   # 変更を有効にするためログアウトして再度ログイン
   ```

3. **コンテナアクセスのテスト**:
   ```bash
   docker ps
   # 実行中のコンテナを表示（実行中のものがない場合は空のリスト）
   ```

**フォールバック動作:**
Docker が利用できない場合、Hermes は自動的にローカルのテキスト正規化にフォールバックし、警告をログに記録します。ワークフローはコンテナ分離なしで続行されます。

### Browser-use

Hermes は Web リサーチに 2 つのモードをサポートしています:

1. **DuckDuckGo フォールバック（デフォルト）** - `duckduckgo-search` で箱から出してすぐに動作
2. **browser-use（オプション）** - 高度なブラウザ自動化機能を提供

**オプション A: DuckDuckGo フォールバックを使用（入門に推奨）**

追加のセットアップは不要です。`duckduckgo-search` パッケージは自動的にインストールされ、信頼性の高い Web 検索機能を提供します。

**オプション B: 高度な機能のために browser-use をインストール**

現在、`browser-use` は PyPI でまだ利用できないため、ソースからインストールする必要があります。

1. **browser-use をクローンしてインストール**:
   ```bash
   # 別のディレクトリで
   cd /tmp
   git clone https://github.com/browser-use/browser-use.git
   cd browser-use
   pip install -e .
   ```

2. **browser extra 付きで Hermes をインストール**:
   ```bash
   cd /path/to/Hermes
   pip install -e .[browser]
   ```

3. **ブラウザの依存関係をインストール**:
   ```bash
   # Playwright ブラウザをインストール
   playwright install chromium

   # Linux では、追加のシステム依存関係が必要な場合があります
   playwright install-deps chromium
   ```

4. **browser-use が検出されることを確認**:
   ```bash
   # テストクエリを実行 - ログで "browser-use detected" を確認
   hermes run --prompt "test query" --max-validation 1
   hermes log -n 10 | grep browser
   ```

**モード間の切り替え:**

Hermes は `browser-use` がインストールされているかどうかを自動的に検出して使用します。browser-use が利用可能でも DuckDuckGo フォールバックを強制するには、アンインストールしてください:

```bash
pip uninstall browser-use
```

**トラブルシューティング:**

- **DuckDuckGo のレート制限**: レート制限に関するエラーが表示される場合は、実行間に遅延を追加するか、より小さい `--max-sources` 値を使用してください。
- **browser-use の初期化失敗**: `playwright --version` で Playwright のインストールを確認し、chromium がインストールされていることを確認してください。
- **Robots.txt によるブロック**: 一部のサイトは自動アクセスをブロックします。Hermes は robots.txt を尊重し、それらの URL をスキップします。

## クイックスタート

1. **Ollama デーモンを起動**
   ```bash
   ollama serve
   ```
   Hermes が API に到達できるよう、別のターミナルでこれを実行し続けてください。

2. **ワークスペースの初期化**
   ```bash
   hermes init
   ```
   `config.yaml`、`history/`、`log/`、および関連ディレクトリを含む `~/.hermes/` を作成します。
   すべてが既に存在する場合、再実行するとリマインダーが表示されます。

3. **最初のリサーチタスクを実行**
   ```bash
   hermes run --prompt "量子コンピューティングのエラー訂正手法を説明してください"
   ```
   `RunService` が設定をロードし、LangGraph ステートを構築し、構造化ログを書き込み、
   `~/.hermes/history/` に `report-<ID>.md` とメタデータを保存します。

4. **結果を確認**
   ```bash
   hermes history --limit 5
   hermes run --export ./latest-report.md    # 最新のレポートをエクスポート
   hermes history --export 2025-0001 ./report.md
   ```

5. **ログを追跡**
   ```bash
   hermes log --follow       # tail ~/.hermes/log/hermes-YYYYMMDD.log
   hermes debug --error -n 100
   ```

6. **準備ができたらスケジュール済みタスクを実行**
   ```bash
   hermes task --prompt "週次 AI まとめ"
   hermes queue --all        # スケジュール済みタスクをすべて順番に実行
   ```
   `QueueService` が最も古い `scheduled` エントリを選択し、順次実行するため、
   各タスクを手動でトリガーする必要はありません。

7. **必要に応じて設定をリセット**
   ```bash
   hermes run --clear
   ```
   `ConfigService` が Ollama と検証設定を含むデフォルトの YAML を再作成します。

タスク指向のウォークスルーについては [USAGE_GUIDE.md](USAGE_GUIDE.md) を参照してください。

## コアコマンド

| コマンド | 説明 |
| --- | --- |
| `hermes init` | `~/.hermes/` ディレクトリとデフォルトの `config.yaml` を作成します。 |
| `hermes run --prompt ...` | 単発のリサーチタスクを実行します。オプションには `--language`、`--api`、`--model`、`--min-validation`、`--max-validation`、`--min-search`、`--max-search`、`--retry`、`--query`、`--export`（最新の実行）、およびスケジュール済みタスクを実行するための `--task-id` があります。 |
| `hermes task --prompt ...` | `task-<ID>.yaml` を介して後で使用するためにプロンプトを保存します。`--list` でリスト表示、`--delete TASK_ID` で削除します。 |
| `hermes queue` | スケジュール済みタスクを順次実行します。`-n/--limit` で実行数を制限、`--all` でキューを空にします。 |
| `hermes history` | 保存された実行をリスト表示し、`--export TASK_ID PATH` でレポートをエクスポート、`--delete` でエントリを削除します。 |
| `hermes log` | `~/.hermes/log/` 内の構造化ログを表示または追跡します。`--task-id` で特定の実行にフィルタ（デフォルトは最新の実行中タスク）、`--follow` でストリーム、`-n` で行数を制御します。 |
| `hermes debug` | 標準とデバッグの両方のログファイルからレベルフィルタ（`--error`、`--warning`、`--info`、`--all`）で読み取ります。 |

コマンドの実装は `hermes_cli/commands/` にあり、テスト容易性のために `hermes_cli/services/` の
サービスに処理を委譲します。

## 設定の概要

`hermes init`（または `ConfigService`）は以下のレイアウトを確保します:

```
~/.hermes/
├── cache/
├── config.yaml
├── history/
│   ├── report-<ID>.md
│   └── report-<ID>.meta.yaml
├── task/
│   └── task-<ID>.yaml
├── log/
│   └── hermes-YYYYMMDD.log
└── debug_log/
    └── hermes-YYYYMMDD.log
```

主要な設定フィールド（`~/.hermes/config.yaml`）:

- `ollama.api_base`、`ollama.model`、`ollama.retry`、`ollama.timeout_sec`
- `language`: デフォルトの出力ロケール（デフォルトは `ja`）
- `validation.min_loops`、`validation.max_loops`: Hermès がバリデーターのループを
  停止するタイミングを決定します。品質チェックに合格しても最小ループは常に実行されます。
- `search.min_sources`、`search.max_sources`: ソースを収集する際にノード/ツールに
  渡されるヒント。現在のプレースホルダーは提供された範囲を尊重します。
- `logging.log_dir`、`logging.debug_log_dir`
- `cli.history_limit`: `hermes history` のデフォルト上限

すべてのランタイムオーバーライドは CLI フラグに直接マップされます（例: `--model llama2:70b` は
その呼び出しに対してのみ Ollama 設定を更新します）。

## 現在の制限と注意事項

- **ブラウザリサーチ**: DuckDuckGo 統合は即座の Web 検索機能のために箱から出してすぐに動作します。
  高度な自動化機能については、[統合のセットアップ](#統合のセットアップ)の手順に従って
  ソースから `browser-use` をインストールしてください。Hermes は利用可能な場合、
  browser-use を自動的に検出して使用します。
- **コンテナ処理**: 分離されたテキスト正規化には Docker 20.10+ が必要です。
  Docker が利用できない場合、Hermes は自動的にローカル処理にフォールバックし、
  警告をログに記録します。Docker のインストール手順については
  [統合のセットアップ](#統合のセットアップ)を参照してください。
- **検証ループ**: 品質スコアリングとフォローアップクエリの生成は進化する
  ヒューリスティックしきい値を使用します。使用データが増えるにつれて評価メトリクスが
  改善されるため、ループ数にはある程度のばらつきが予想されます。
- **タスクスケジューリング**: タスクは YAML ファイルとして保存されますが、
  `hermes queue` または `hermes run --task-id` を介した手動実行が必要です。
  バックグラウンドデーモンはありません。必要に応じてシステムの cron/systemd で
  キュー実行をスケジュールしてください。
- **ログフィルタリング**: `hermes log --task-id` はエントリをフィルタしますが、
  ログファイルは日ごとにセグメント化されます（`hermes-YYYYMMDD.log`）。
  深夜をまたぐ長時間実行タスクの場合、複数のログファイルを確認する必要がある場合があります。
- **モデルタイムアウト**: デフォルトの Ollama タイムアウトは 180 秒です
  （`~/.hermes/config.yaml: ollama.timeout_sec` で設定可能）。大規模なモデルや
  複雑なクエリでは、より高い値が必要になる場合があります。

実装の詳細と拡張ポイントについては、`hermes_cli/tools/` と `hermes_cli/agents/nodes/` の
統合ノートを参照してください。

## トラブルシューティングのハイライト

- **Ollama 接続エラー** – `ollama serve` がローカルで実行されており、
  `~/.hermes/config.yaml` の `ollama.api_base` が正しいホストを指していることを確認してください。
  `curl http://localhost:11434/api/version` で接続を確認してください。
- **モデルが見つからない** – `ollama pull gpt-oss:20b`（または CLI で設定したモデル）を実行してください。
  Hermes は HTTP 404/500 エラーを `hermes log` に表示します。
- **タイムアウトエラー** – `~/.hermes/config.yaml` の `ollama.timeout_sec` を
  デフォルトの 180 秒から増やしてください。大規模なモデルは複雑なクエリに 300 秒以上必要な場合があります。
- **Docker 接続拒否** – container-use には Docker の実行が必要です。`docker ps` で確認してください。
  利用できない場合、Hermes は警告とともにローカル処理にフォールバックします。
- **DuckDuckGo のレート制限** – リクエスト間隔を空けるか、`--max-sources` を減らしてください。
  サービスは急速なクエリを一時的にブロックする場合があります。1〜2 分待ってから再試行してください。
- **browser-use が検出されない** – ソースからインストールした後、
  `python -c "import browser_use; print('OK')"` で確認してください。
  必要に応じて playwright ブラウザを再インストールしてください。
- **古い設定** – `hermes run --clear` でデフォルト設定を再生成します。
- **履歴/ログファイルの欠落** – `hermes init` は安全に再実行できます。ログは
  日ごとにローテーションされます（`hermes-YYYYMMDD.log`）。
- **LangGraph インポートの問題** – `python test_workflow.py` を使用して
  `create_hermes_workflow()` がコンパイルされることを確認してください。
  これが失敗する場合は依存関係を再インストールしてください。

## ドキュメント一覧

- [ARCHITECTURE.md](ARCHITECTURE.md) – レイヤーの詳細、データフロー、ノードマップ
- [DEVELOPMENT.md](DEVELOPMENT.md) – 環境セットアップ、ツール、テストのヒント
- [USAGE_GUIDE.md](USAGE_GUIDE.md) – タスクベースのウォークスルーと CLI フラグ

これらのドキュメントはリポジトリルートのこの README と同じ場所にあります。
新しいサービスや統合が追加されたら更新してください。

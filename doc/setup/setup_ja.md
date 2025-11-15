# セットアップガイド

このガイドでは、Hermesアプリケーションを実行するために必要なすべてのコンポーネントのセットアップ手順を説明します。

## 1. 前提条件

-   **OS**: Ubuntu 22.04 以上
-   **Python**: 3.10 以上
-   **Docker**: `docker` および `docker-compose`
-   **GPU**: VRAM 16GB 推奨（Ollama用）
-   **Git**: ソースコードのクローンに必要
-   **uv**: Pythonパッケージのインストールに推奨 (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

## 2. Hermes CLI のインストール

### a. リポジトリのクローン

まず、HermesのソースコードをGitHubからクローンします。

```bash
git clone https://github.com/yasutoshi-lab/Hermes.git
cd Hermes
```

### b. 依存関係のインストール

`uv` を使って、プロジェクトの依存関係をインストールし、CLIを編集可能モードでインストールします。

```bash
# 依存関係をインストール
uv sync

# CLIをインストール
uv pip install -e .
```

## 3. Ollama のセットアップ

Hermesは、LLM（大規模言語モデル）をローカルで実行するために [Ollama](https://ollama.com/) を利用します。

### a. Ollama のインストール

公式のインストールスクリプトを実行します。

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### b. LLMモデルのダウンロード

Hermesがデフォルトで使用するモデルをダウンロードします。他のモデルを使用する場合は、適宜モデル名を変更してください。

```bash
ollama pull gpt-oss:20b
```

### c. Ollama サービスの起動

Ollamaがバックグラウンドで常に実行されるように、サービスを起動（または有効化）します。

```bash
# サービスを起動
ollama serve
```

システム起動時に自動で開始させたい場合は、以下のコマンドを実行します。

```bash
sudo systemctl enable ollama
```

## 4. Hermes ワークスペースの初期化

最後に、Hermesのワークスペースをセットアップします。これには設定ファイルや外部サービス（SearxNG, Redis）のDocker設定が含まれます。

### a. ワークスペースの初期化

`hermes init` コマンドを実行して、`~/.hermes` ディレクトリに必要なファイルを作成します。

```bash
hermes init
```

### b. 外部サービスの起動

作成されたワークスペースに移動し、`docker compose` を使ってSearxNG（メタ検索エンジン）とRedis（キャッシュ）をバックグラウンドで起動します。

```bash
cd ~/.hermes
docker compose up -d
```

## 5. セットアップの確認

すべてが正しくセットアップされたかを確認するために、簡単なリサーチタスクを実行してみましょう。

```bash
hermes run --prompt "日本の首都はどこですか？"
```

"Execution completed!" というメッセージとレポートのパスが表示されれば、セットアップは成功です。

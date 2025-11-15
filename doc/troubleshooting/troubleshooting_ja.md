# トラブルシューティング

このガイドは、Hermesの利用中に発生する可能性のある一般的な問題とその解決策をまとめたものです。

## 1. Ollama に接続できない

`hermes run` を実行した際に、Ollamaに関するエラー（例: `Connection refused`）が表示される場合。

### 原因

-   Ollamaサービスが起動していない。
-   `config.yaml` の `api_url` が間違っている。
-   ファイアウォールによって接続がブロックされている。

### 解決策

1.  **Ollamaの状態確認**:
    まず、Ollamaサーバーが正常に動作しているかを確認します。ターミナルで以下のコマンドを実行し、インストールされているモデルの一覧が返ってくるか確認してください。

    ```bash
    curl http://localhost:11434/api/tags
    ```

    エラーが返ってくる場合は、Ollamaが起動していない可能性があります。

2.  **Ollamaサービスの再起動**:
    以下のコマンドでOllamaサービスを再起動します。

    ```bash
    # systemd を使用している場合
    sudo systemctl restart ollama

    # または、単にターミナルで直接起動
    ollama serve
    ```

3.  **設定ファイルの確認**:
    `~/.hermes/config.yaml` を開き、`ollama.api_url` が正しいか確認してください。デフォルトは `http://localhost:11434/api/chat` です。

## 2. SearxNG に接続できない / 検索結果が取得できない

Web検索のステップでエラーが発生する場合。

### 原因

-   SearxNGのDockerコンテナが起動していない。
-   RedisのDockerコンテナが起動していない。
-   ネットワークの問題やファイアウォール。
-   SearxNG自体の設定に問題がある。

### 解決策

1.  **Dockerコンテナの状態確認**:
    Hermesのワークスペースディレクトリに移動し、`docker compose ps` を実行して、`searxng` と `redis` の両方のコンテナが `Up` (または `running`) 状態であることを確認します。

    ```bash
    cd ~/.hermes
    docker compose ps
    ```

2.  **コンテナのログ確認**:
    いずれかのコンテナが `Up` でない場合、または問題が解決しない場合は、ログを確認して詳細なエラーメッセージを探します。

    ```bash
    # SearxNGのログを確認
    docker compose logs searxng

    # Redisのログを確認
    docker compose logs redis
    ```

3.  **サービスの再起動**:
    コンテナを再起動することで問題が解決する場合があります。

    ```bash
    docker compose restart
    ```

4.  **SearxNGの設定確認**:
    `~/.hermes/searxng/settings.yml` ファイルを確認し、検索エンジンの設定が有効になっているかを確認してください。特定の検索エンジンがブロックされている可能性があります。

5.  **ファイアウォール設定の確認**:
    Dockerコンテナが外部ネットワークにアクセスすることをファイアウォールが妨げていないか確認してください。

## 3. ログの確認方法

より詳細な問題解決のためには、Hermes自体のログを確認することが有効です。

-   **通常ログ**:
    `hermes log` コマンドで主要なログを確認できます。

    ```bash
    hermes log --lines 200
    ```

-   **デバッグログ**:
    `--debug` フラグを付けると、エージェントの各ステップの思考プロセスやAPIの応答など、より詳細なログを確認できます。問題の切り分けに非常に役立ちます。

    ```bash
    hermes log --debug --lines 500
    ```

-   **リアルタイムログ**:
    `--follow` フラグを付けると、現在実行中のタスクのログをリアルタイムで追跡できます。

    ```bash
    hermes log --follow --debug
    ```

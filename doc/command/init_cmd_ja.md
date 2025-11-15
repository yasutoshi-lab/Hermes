# `hermes init` コマンド

`hermes init` コマンドは、Hermesアプリケーションのワークスペースを初期化するために使用されます。

## 機能

このコマンドは、Hermesが動作するために必要なディレクトリ構造と設定ファイルを `~/.hermes` （または指定されたワークディレクトリ）に作成します。

具体的には、以下の処理を実行します。

-   キャッシュ、タスク、ログ、履歴などを保存するためのサブディレクトリを作成します。
-   デフォルト設定を含む `config.yaml` ファイルを生成します。
-   SearxNGやRedisなどの外部サービスを起動するための `docker-compose.yaml` ファイルを配置します。

## オプション

| オプション | 説明 | デフォルト値 |
| :--- | :--- | :--- |
| `--work-dir PATH` | ワークスペースとして使用するディレクトリのパスを指定します。 | `~/.hermes` |
| `--clear` | このフラグを指定すると、既存のワークスペースと設定がすべて削除され、完全に新しい状態で再初期化されます。 | N/A |

## 実装詳細

-   **CLIフレームワーク**: `click`
-   **メインロジック**:
    1.  指定されたワークディレクトリが存在し、`--clear` フラグが指定されていない場合、すでに初期化済みであると判断し、処理を中断します。
    2.  `--clear` フラグが指定されている場合、既存のワークスペースディレクトリを削除します。
    3.  `hermes_cli.persistence.file_paths.FilePaths` を使用して、必要なすべてのサブディレクトリ（`cache`, `task`, `log`, `debug_log`, `history`, `searxng`）を作成します。
    4.  `hermes_cli.models.config.HermesConfig` を使用してデフォルトの設定オブジェクトを生成し、`hermes_cli.persistence.config_repository.ConfigRepository` を介して `config.yaml` として保存します。
    5.  `.hermes_template` ディレクトリから `docker-compose.yaml` をワークスペースにコピーします。
    6.  初期化完了後、次のステップ（Dockerコンテナの起動方法など）をユーザーに案内します。

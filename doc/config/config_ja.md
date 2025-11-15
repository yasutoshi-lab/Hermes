# 設定ファイル (`config.yaml`)

Hermesの動作は、ワークスペースのルートにある `config.yaml` ファイルを通じてカスタマイズできます。このファイルは `hermes init` コマンドによってデフォルト値で生成されます。

`hermes run` コマンドのオプションで指定された値は、このファイルの値を一時的に上書きします。

## デフォルト設定の例

```yaml
work_dir: /home/user/.hermes
ollama:
  api_url: http://localhost:11434/api/chat
  model: gpt-oss:20b
  timeout: 120
  temperature: 0.7
  max_retries: 3
search:
  query_count: 3
  min_search: 3
  max_search: 8
  max_results: 5
validation:
  min_validation: 1
  max_validation: 3
langfuse:
  enabled: false
  host: http://localhost:3000
  public_key:
  secret_key:
log:
  level: INFO
  retention: 7 days
```

## パラメータ詳細

### `work_dir`

-   **説明**: Hermesが使用するワークスペースの絶対パス。
-   **デフォルト**: `~/.hermes`

### `ollama`

Ollama（ローカルLLM実行環境）に関する設定です。

-   `api_url`: OllamaのAPIエンドポイント。
-   `model`: 使用するデフォルトのLLMモデル名。
-   `timeout`: APIコールのタイムアウト時間（秒）。
-   `temperature`: モデルの応答の多様性を制御するパラメータ。値が低いほど決定的になり、高いほど多様な応答が生成されます。
-   `max_retries`: APIコールが失敗した際の最大リトライ回数。

### `search`

Web検索に関する設定です。

-   `query_count`: 最初のステップでLLMに生成させる検索クエリの数。
-   `min_search`: 収集する情報ソースの最小数。これを下回る場合、追加の検索が試みられます。
-   `max_search`: 収集する情報ソースの最大数。
-   `max_results`: 1つの検索クエリあたりでSearxNGから取得する最大検索結果数。

### `validation`

生成されたレポートの品質を検証するためのループに関する設定です。

-   `min_validation`: レポートを最終化するための最小検証ループ回数。
-   `max_validation`: 最大検証ループ回数。これを超えると、たとえ改善点が見つかってもループは終了します。

### `langfuse`

[Langfuse](https://langfuse.com/) を使用した実行トレースの記録に関する設定です。

-   `enabled`: Langfuseへのトレース記録を有効にするかどうか。
-   `host`: LangfuseサーバーのホストURL。
-   `public_key`: Langfuseプロジェクトの公開鍵。
-   `secret_key`: Langfuseプロジェクトの秘密鍵。

### `log`

ログに関する設定です。

-   `level`: ログレベル（`DEBUG`, `INFO`, `WARNING`, `ERROR`）。
-   `retention`: ログファイルを保持する期間。

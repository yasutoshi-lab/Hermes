# Browser-use統合

## 概要

Browser-useは、HermesのWeb研究機能を強化するオプションのWeb自動化ライブラリです。HermesはDuckDuckGoフォールバックですぐに動作し、利用可能な場合はbrowser-useに自動的にアップグレードします。

## 動作モード

Hermesは2つのWeb研究モードをサポート：

### モード1：DuckDuckGoフォールバック（デフォルト）

- **有効化**：すぐに使用可能、セットアップ不要
- **技術**：`duckduckgo-search` + `httpx`
- **機能**：
  - DuckDuckGo経由のテキスト検索
  - HTTPコンテンツ取得
  - 基本的なHTML解析
  - robots.txt遵守
- **制限事項**：
  - JavaScriptレンダリングなし
  - インタラクティブ要素なし
  - レート制限の対象
  - 基本的なコンテンツ抽出

### モード2：browser-use（拡張）

- **有効化**：`browser-use`パッケージがインストールされている場合
- **技術**：Playwright + ブラウザ自動化
- **機能**：
  - 完全なJavaScriptレンダリング
  - インタラクティブ要素の処理
  - 高度なページスクレイピング
  - 動的コンテンツサポート
- **要件**：
  - ソースからのインストール（PyPIにはまだ未公開）
  - Playwrightブラウザバイナリ
  - 追加のディスク容量（約300 MB）

## 各モードを使用するタイミング

### DuckDuckGoモード（デフォルト）を使用する場合：

- Hermesを始めるとき
- テキスト中心のトピックを研究するとき
- ネットワーク帯域幅が限られているとき
- ディスク容量が制約されているとき
- 簡単なコンテンツ抽出で十分な場合
- レート制限が問題でない場合

### browser-useモードを使用する場合：

- JavaScriptでレンダリングされたコンテンツが必要な場合
- シングルページアプリケーション（SPA）をスクレイピングする場合
- 動的Webページとやり取りする場合
- 正確な要素選択が必要な場合
- スクリーンショット機能が必要な場合
- 高度な自動化機能が必要な場合

## インストール

### 前提条件

- Python 3.10以上
- Hermesが既にインストール済み
- インターネット接続
- 500 MB以上の空きディスク容量

### ソースからbrowser-useをインストール

現在、browser-useはPyPIで利用できません。GitHubからインストール：

```bash
# 一時ディレクトリに移動
cd /tmp

# リポジトリをクローン
git clone https://github.com/browser-use/browser-use.git
cd browser-use

# パッケージをインストール
pip install -e .

# インストールを確認
python -c "import browser_use; print('browser-use installed')"
```

### Playwrightブラウザをインストール

browser-useはブラウザ自動化にPlaywrightを使用：

```bash
# Chromiumブラウザをインストール
playwright install chromium

# システム依存関係をインストール（Linuxのみ）
playwright install-deps chromium

# インストールを確認
playwright --version
```

### Hermesブラウザ拡張をインストール

browser-useをインストール後：

```bash
cd /path/to/Hermes
pip install -e .[browser]
```

これにより、すべてのブラウザ関連依存関係が存在することを保証します。

## 設定

### 自動検出

Hermesは自動的にbrowser-useを検出：

```python
# 起動時にHermesがチェック
try:
    from browser_use import BrowserAgent
    # 利用可能な場合はbrowser-useを使用
except ImportError:
    # DuckDuckGoにフォールバック
    pass
```

設定変更は不要です！

### 検出を確認

```bash
# テストタスクを実行
hermes run --prompt "test browser" --max-validation 1

# ログで検出メッセージをチェック
hermes log -n 50 | grep browser

# 期待される出力："browser-use detected; BrowserAgent initialized"
# またはフォールバック時："Using DuckDuckGo fallback"
```

### DuckDuckGoモードを強制

browser-useを一時的に無効化するには：

```bash
# browser-useをアンインストール
pip uninstall browser-use

# またはインポートの名前を変更（一時的）
python -c "import sys; sys.modules['browser_use'] = None"
```

## 検証

### DuckDuckGoモードをテスト

```bash
# browser-useがインストールされていないことを確認
pip list | grep browser-use

# テストを実行
python tests/test_browser_client.py
```

**期待される出力**：
```
Sample result: Example Title -> https://example.com
Snippet: Brief description...
Content preview: Full text...
Fetched 2 total sources.
```

### browser-useモードをテスト

```bash
# browser-useがインストールされていることを確認
python -c "import browser_use; print('OK')"

# テストタスクを実行
hermes run --prompt "JavaScript framework comparison" --max-validation 1

# ログをチェック
hermes log -n 20 | grep -i browser
```

期待されるログ行：
```
[INFO] [WEB] browser-use detected; BrowserAgent initialized.
```

## トラブルシューティング

### browser-useが検出されない

**症状**：インストール後もログに「Using DuckDuckGo fallback」と表示される

**解決策**：

1. **インストールを確認**
   ```bash
   python -c "import browser_use; print(browser_use.__version__)"
   ```

2. **仮想環境をチェック**
   ```bash
   which python
   pip list | grep browser-use
   ```

3. **再インストール**
   ```bash
   pip uninstall browser-use
   cd /tmp/browser-use
   pip install -e .
   ```

4. **インポートエラーをチェック**
   ```bash
   python -c "from browser_use import BrowserAgent; print('OK')"
   ```

### Playwrightインストール失敗

**症状**：`playwright install`がエラーで失敗

**Linuxの解決策**：

```bash
# システムパッケージを更新
sudo apt-get update
sudo apt-get upgrade

# 欠落している依存関係をインストール
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2

# Playwrightインストールを再試行
playwright install chromium
playwright install-deps chromium
```

**macOSの解決策**：

```bash
# Xcode Command Line Toolsがインストールされていることを確認
xcode-select --install

# インストールを再試行
playwright install chromium
```

**権限の問題**：

```bash
# sudoで実行（推奨されません）
sudo playwright install chromium

# または権限を修正
sudo chown -R $USER:$USER ~/.cache/ms-playwright
playwright install chromium
```

### ブラウザ起動失敗

**症状**：「Failed to launch browser」エラー

**原因と解決策**：

1. **実行ファイルの欠落**
   ```bash
   # Playwrightブラウザをチェック
   ls ~/.cache/ms-playwright/

   # 欠落している場合は再インストール
   playwright install chromium
   ```

2. **ディスプレイサーバーの問題（Linux）**
   ```bash
   # ヘッドレスモードを設定（Hermesでは既にデフォルト）
   export PLAYWRIGHT_BROWSERS_PATH=0

   # またはXvfbを使用
   sudo apt-get install xvfb
   xvfb-run hermes run --prompt "test"
   ```

3. **メモリ不足**
   ```bash
   # 利用可能なRAMをチェック
   free -h

   # 他のアプリケーションを閉じる
   # またはスワップ領域を増やす
   ```

### パフォーマンスの遅さ

**症状**：browser-useを使用するとタスクに大幅に時間がかかる

**原因**：

- ブラウザ起動のオーバーヘッド（クエリごとに約2-5秒）
- JavaScriptレンダリング時間
- ネットワークレイテンシ

**最適化**：

1. **ソース数を減らす**
   ```bash
   hermes run --prompt "..." --max-search 5
   ```

2. **簡単なクエリにはDuckDuckGoを使用**
   ```bash
   pip uninstall browser-use  # 一時的
   hermes run --prompt "..."
   pip install -e /tmp/browser-use  # 復元
   ```

3. **クエリをバッチ処理**
   ```bash
   # 複数のタスクをスケジュール
   hermes task --prompt "Topic 1"
   hermes task --prompt "Topic 2"

   # 夜間に実行
   hermes queue --all
   ```

### レート制限

**症状**：DuckDuckGoが429エラーまたは空の結果を返す

**適用対象**：両方のモード（browser-useも検索エンジンを使用）

**解決策**：

1. **実行間に遅延を追加**
   ```bash
   hermes run --prompt "Query 1"
   sleep 60
   hermes run --prompt "Query 2"
   ```

2. **ソースを減らす**
   ```bash
   hermes run --prompt "..." --max-search 3
   ```

3. **異なる検索エンジンを使用**（コード変更が必要）

4. **待ってから再試行**
   ```bash
   # 2-5分待つ
   sleep 120
   hermes run --prompt "..."
   ```

### robots.txtのブロック

**症状**：ログに「Robots.txt disallows fetching」

**動作**：Hermesはデフォルトでrobots.txtを尊重

**解決策**：

1. **スニペット/要約に依存**（変更不要）

2. **手動介入**（重要な場合）
   ```bash
   # ログからURLを抽出
   hermes debug -n 100 | grep "disallows fetching"

   # 手動で訪問してコンテンツを保存
   curl https://example.com > content.txt
   ```

3. **スクレイピングを許可するソースに焦点を当てる**
   - 学術サイト（arxiv.org、scholar.google.com）
   - ニュースサイト（通常許可）
   - オープンデータプラットフォーム

### メモリリーク

**症状**：時間とともにRAM使用量が増加

**原因**：ブラウザインスタンスが適切にクリーンアップされない

**解決策**：

```bash
# 孤児Chromeプロセスを終了
pkill -f chrome
pkill -f chromium

# Hermesタスクを再起動
hermes run --prompt "..."
```

**予防**（Hermesで既に実装済み）：

- コンテキストマネージャーの使用（`with BrowserUseClient()`）
- エラーハンドラーでの明示的クリーンアップ

## 高度な設定

### Browser-use設定

現在、browser-useの設定は`BrowserUseClient`にハードコードされています。将来のバージョンでは以下をサポートする可能性：

```yaml
# 将来の ~/.hermes/config.yaml
browser:
  headless: true
  timeout: 30
  user_agent: "Mozilla/5.0 ..."
  viewport_width: 1920
  viewport_height: 1080
```

### カスタムユーザーエージェント

`hermes_cli/tools/browser_use_client.py`を編集：

```python
USER_AGENT = "Mozilla/5.0 (compatible; HermesBot/1.0)"
```

### プロキシ設定

ネットワーク制限の場合：

```bash
# 環境変数を設定
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Hermesを実行
hermes run --prompt "..."
```

## パフォーマンス比較

### ベンチマーク：簡単なテキストクエリ

| モード | ソース数 | 時間 | 品質 |
|------|-------------|------|---------|
| DuckDuckGo | 8 | 15秒 | 良好 |
| browser-use | 8 | 45秒 | 優秀 |

### ベンチマーク：JavaScriptヘビーサイト

| モード | ソース数 | 時間 | 品質 |
|------|-------------|------|---------|
| DuckDuckGo | 8 | 20秒 | 不良（コンテンツ欠落） |
| browser-use | 8 | 60秒 | 優秀 |

### 推奨

- **デフォルト**：DuckDuckGoを使用（高速、ほとんどのケースで十分）
- **必要時**：特殊なタスクのためbrowser-useをインストール
- **本番**：特定のユースケースで両方のモードをテスト

## モード間の切り替え

### 一時的な切り替え

```bash
# 1回の実行でbrowser-useを無効化
pip uninstall browser-use -y
hermes run --prompt "..."

# 再有効化
cd /tmp/browser-use && pip install -e .
```

### 永続的な切り替え

**DuckDuckGoのみに**：
```bash
pip uninstall browser-use
```

**browser-useに**：
```bash
# インストール済みであることを確認
cd /tmp/browser-use && pip install -e .
```

## テスト

### 単体テスト

```bash
# DuckDuckGoモードをテスト
pytest tests/test_browser_client.py

# browser-useでテスト（インストール済みの場合）
# 同じテストが自動的にbrowser-useを検出
python -c "import browser_use" && pytest tests/test_browser_client.py
```

### 統合テスト

```bash
# 完全なワークフローテスト
hermes run --prompt "Compare Python web frameworks" \
  --max-validation 1 \
  --max-search 5

# どのモードが使用されたかチェック
hermes log -n 50 | grep -i browser
```

## ディスク容量管理

### 使用状況をチェック

```bash
# Playwrightブラウザ
du -sh ~/.cache/ms-playwright/

# browser-useパッケージ
du -sh /tmp/browser-use/
```

### クリーンアップ

```bash
# Playwrightブラウザを削除
playwright uninstall

# browser-useを削除
pip uninstall browser-use
rm -rf /tmp/browser-use
```

### 最小セットアップ

制約のある環境の場合：

```bash
# DuckDuckGoのみを使用（browser-use無し）
pip install -e .  # Hermesベースインストールのみ
```

## セキュリティに関する考慮事項

### ヘッドレスモード

Hermesはセキュリティのためデフォルトでヘッドレスモード（GUI無し）でブラウザを実行します。

### サンドボックス化

Playwrightブラウザはサンドボックスモードで実行されます。無効化する場合（推奨されません）：

```bash
export PLAYWRIGHT_CHROMIUM_ARGS="--no-sandbox"
hermes run --prompt "..."
```

### データプライバシー

- Browser-useは`~/.cache/ms-playwright/`にデータをキャッシュする可能性があります
- 定期的にキャッシュをクリア：
  ```bash
  rm -rf ~/.cache/ms-playwright/
  playwright install chromium
  ```

## 将来の機能強化

browser-use統合の計画機能：

- `config.yaml`での設定可能なブラウザ設定
- ビジュアル分析用のスクリーンショットキャプチャ
- Cookie/セッション管理
- マルチブラウザサポート（Firefox、Safari）
- 分散ブラウザプール

## 関連ドキュメント

- [Container-use統合](./container-use.md)
- [Ollama統合](./ollama.md)
- [Hermesアーキテクチャ](../../ARCHITECTURE.md)
- [トラブルシューティング](../../README.md#troubleshooting-highlights)

## 外部リソース

- [browser-use GitHub](https://github.com/browser-use/browser-use)
- [Playwrightドキュメント](https://playwright.dev/)
- [DuckDuckGo Search API](https://duckduckgo.com/api)

## サポート

browser-use固有の問題について：
- エラートレースについて`hermes debug --error`をチェック
- Playwrightインストールを確認：`playwright --version`
- ブラウザ起動をテスト：`playwright open chromium`
- `hermes debug -n 200`からのログとともに問題を報告

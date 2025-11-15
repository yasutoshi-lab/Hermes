# Hermes 外部依存関係

このディレクトリには、Hermesの外部依存関係と統合に関する詳細なドキュメントが含まれています。

## 概要

Hermesは、研究機能のために3つの外部システムに依存しています。

| 依存関係 | ステータス | 目的 | ドキュメント |
|------------|--------|---------|---------------|
| **Ollama** | 必須 | テキスト生成のためのLLM推論 | [ollama.md](./ollama.md) |
| **Docker** | オプション | 処理のためのコンテナ分離 | [container-use.md](./container-use.md) |
| **browser-use** | オプション | 拡張Web自動化 | [browser-use.md](./browser-use.md) |

## クイックセットアップガイド

### 最小セットアップ（必須のみ）

基本的なHermes機能のため：

```bash
# 1. Ollamaをインストール
curl -fsSL https://ollama.ai/install.sh | sh

# 2. モデルをプル
ollama serve &
ollama pull gpt-oss:20b

# 3. Hermesをインストール
pip install -e .

# 4. 初期化
hermes init

# 5. テスト
hermes run --prompt "test query" --max-validation 1
```

**有効な機能**:
- ✅ LLM駆動のテキスト生成
- ✅ DuckDuckGo Web検索
- ✅ ローカルテキスト処理
- ❌ コンテナ分離
- ❌ 高度なブラウザ自動化

### フルセットアップ（全機能）

完全な機能のため：

```bash
# 1. Ollamaをインストール（上記参照）

# 2. Dockerをインストール
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER

# 3. browser-useをインストール
cd /tmp
git clone https://github.com/browser-use/browser-use.git
cd browser-use
pip install -e .
playwright install chromium

# 4. Hermesを拡張機能付きでインストール
cd /path/to/Hermes
pip install -e .[browser,dev]

# 5. 初期化とテスト
hermes init
hermes run --prompt "comprehensive test" --max-validation 2
```

**有効な機能**:
- ✅ LLM駆動のテキスト生成
- ✅ browser-useによる拡張Web検索
- ✅ コンテナベースの処理
- ✅ 完全な自動化機能

## 依存関係マトリックス

### オペレーティングシステム別

| OS | Ollama | Docker | browser-use |
|----|--------|--------|-------------|
| Ubuntu 20.04+ | ✅ ネイティブ | ✅ ネイティブ | ✅ サポート |
| Ubuntu 18.04 | ✅ ネイティブ | ✅ ネイティブ | ⚠️ 手動セットアップ |
| Debian 11+ | ✅ ネイティブ | ✅ ネイティブ | ✅ サポート |
| CentOS 8+ | ✅ ネイティブ | ✅ ネイティブ | ✅ サポート |
| macOS 11+ | ✅ ネイティブ | ✅ Docker Desktop | ✅ サポート |
| macOS 10.15 | ✅ ネイティブ | ⚠️ Docker Desktop | ⚠️ 制限あり |
| Windows 11 (WSL2) | ✅ WSL2経由 | ✅ Docker Desktop | ✅ WSL2経由 |
| Windows 10 (WSL2) | ✅ WSL2経由 | ✅ Docker Desktop | ✅ WSL2経由 |

✅ 完全サポート | ⚠️ 追加セットアップが必要 | ❌ 非サポート

### ハードウェア別

| ハードウェア | Ollama | Docker | browser-use | 推奨設定 |
|----------|--------|--------|-------------|--------------------|
| 8 GB RAM、GPU無し | ⚠️ 小型モデル | ✅ 制限あり | ✅ はい | llama2:7b、2ループ |
| 16 GB RAM、GPU無し | ✅ 中型モデル | ✅ 良好 | ✅ はい | llama2:13b、3ループ |
| 32 GB RAM、GPU 8 GB | ✅ 大型モデル | ✅ 優秀 | ✅ はい | gpt-oss:20b、5ループ |
| 64+ GB RAM、GPU 16+ GB | ✅ 任意のモデル | ✅ 優秀 | ✅ はい | llama2:70b、無制限 |

## 依存関係決定ツリー

### Dockerをインストールするべきか？

```
再現可能な結果が必要？ ───はい─→ Dockerをインストール
         │
         いいえ
         │
単一ユーザー開発？ ───はい─→ Dockerをスキップ（ローカルモード使用）
         │
         いいえ
         │
CI/CD環境？ ───はい─→ Dockerをインストール
         │
         いいえ
         │
本番デプロイ？ ───はい─→ Dockerをインストール
         │
         いいえ
         │
         └─→ Dockerをスキップ（ローカルモード使用）
```

### browser-useをインストールするべきか？

```
JavaScript レンダリングが必要？ ───はい─→ browser-useをインストール
         │
         いいえ
         │
動的サイトのスクレイピング？ ───はい─→ browser-useをインストール
         │
         いいえ
         │
DuckDuckGoで十分？ ───はい─→ browser-useをスキップ
         │
         いいえ
         │
         └─→ まずDuckDuckGoを試し、必要に応じてbrowser-useをインストール
```

## インストール順序

推奨インストール順序：

1. **Ollama**（必須、最初にインストール）
2. **Hermesベース**（必須）
3. **Docker**（オプション、コンテナモード用）
4. **browser-use**（オプション、拡張検索用）

この順序により、必要な時に依存関係が利用可能になります。

## 検証チェックリスト

インストール後、各コンポーネントを検証：

### ✅ Ollama

```bash
# サーバーをチェック
curl http://localhost:11434/api/version

# モデルをチェック
ollama list | grep gpt-oss

# 生成をテスト
ollama run gpt-oss:20b "Hello"
```

### ✅ Docker

```bash
# デーモンをチェック
docker info

# 権限をチェック
docker ps

# コンテナをテスト
docker run hello-world
```

### ✅ browser-use

```bash
# インストールをチェック
python -c "import browser_use; print('OK')"

# Playwrightをチェック
playwright --version

# ブラウザをテスト
playwright open chromium
```

### ✅ Hermes統合

```bash
# 完全テスト
hermes run --prompt "integration test" --max-validation 1

# ログをチェック
hermes log -n 50 | grep -E "(ollama|docker|browser)"
```

## 一般的なセットアップシナリオ

### シナリオ1：開発用ラップトップ（8 GB RAM）

**目標**：最小限のオーバーヘッドで高速開発

```bash
# Ollama + 小型モデルをインストール
ollama pull mistral:7b

# Hermesのみインストール
pip install -e .

# 速度のための設定
# ~/.hermes/config.yaml
ollama:
  model: mistral:7b
  timeout_sec: 120
validation:
  max_loops: 2
search:
  max_sources: 5
```

**スキップ**：Docker、browser-use

### シナリオ2：研究用ワークステーション（32 GB RAM + GPU）

**目標**：最大品質と機能

```bash
# すべてをインストール
ollama pull gpt-oss:20b
sudo apt-get install docker.io
cd /tmp && git clone https://github.com/browser-use/browser-use.git
cd browser-use && pip install -e .
playwright install chromium
pip install -e .[browser,dev]

# 品質のための設定
# ~/.hermes/config.yaml
ollama:
  model: gpt-oss:20b
  timeout_sec: 300
validation:
  max_loops: 5
search:
  max_sources: 12
```

### シナリオ3：CI/CDパイプライン

**目標**：再現可能な自動テスト

```bash
# DockerfileまたはCIスクリプト内
RUN curl -fsSL https://ollama.ai/install.sh | sh
RUN ollama serve & sleep 5 && ollama pull llama2:7b

# Docker-in-Dockerをインストール
RUN apt-get install -y docker.io

# browser-useはスキップ（ほとんどのテストには不要）

# CI用の設定
ENV HERMES_MAX_VALIDATION=1
ENV HERMES_MAX_SOURCES=3
```

### シナリオ4：本番サーバー（バッチ処理）

**目標**：夜間バッチ実行の安定性

```bash
# すべてのコンポーネントをインストール
# 自動再起動のためsystemdサービスを使用

# Ollamaサービス
sudo systemctl enable ollama

# Dockerサービス
sudo systemctl enable docker

# 信頼性のための設定
# ~/.hermes/config.yaml
ollama:
  model: llama2:13b  # 速度/品質のバランス
  timeout_sec: 240
  retry: 5  # より多い再試行
validation:
  max_loops: 3
search:
  max_sources: 8
```

## トラブルシューティングクイックリファレンス

### Ollamaの問題

| 症状 | クイックフィックス | ドキュメント |
|---------|-----------|---------------|
| 接続拒否 | `ollama serve &` | [ollama.md](./ollama.md#connection-refused) |
| モデルが見つからない | `ollama pull gpt-oss:20b` | [ollama.md](./ollama.md#model-not-found-404-error) |
| タイムアウト | `timeout_sec`を増やす | [ollama.md](./ollama.md#timeout-errors) |
| パフォーマンスの遅さ | より小型のモデルを使用 | [ollama.md](./ollama.md#slow-performance) |

### Dockerの問題

| 症状 | クイックフィックス | ドキュメント |
|---------|-----------|---------------|
| デーモンが実行されていない | `sudo systemctl start docker` | [container-use.md](./container-use.md#docker-daemon-not-running) |
| 権限が拒否された | `sudo usermod -aG docker $USER` | [container-use.md](./container-use.md#permission-denied) |
| ディスク容量 | `docker system prune -a` | [container-use.md](./container-use.md#disk-space-issues) |
| ネットワークの問題 | DNS設定をチェック | [container-use.md](./container-use.md#network-issues) |

### browser-useの問題

| 症状 | クイックフィックス | ドキュメント |
|---------|-----------|---------------|
| 検出されない | ソースから再インストール | [browser-use.md](./browser-use.md#browser-use-not-detected) |
| Playwrightエラー | `playwright install chromium` | [browser-use.md](./browser-use.md#playwright-installation-failed) |
| ブラウザ起動失敗 | システム依存関係をインストール | [browser-use.md](./browser-use.md#browser-launch-failures) |
| レート制限 | 2分待って再試行 | [browser-use.md](./browser-use.md#rate-limiting) |

## パフォーマンス最適化ガイド

### ユースケース別

#### クイックテスト（開発）

```yaml
# すべてを最小化
ollama:
  model: mistral:7b
  timeout_sec: 60
validation:
  min_loops: 1
  max_loops: 1
search:
  max_sources: 3
```

**無効化**：Docker、browser-use

**予想時間**：タスクあたり30-60秒

#### バランスのとれた品質（デフォルト）

```yaml
# 現在のデフォルト
ollama:
  model: gpt-oss:20b
  timeout_sec: 180
validation:
  min_loops: 1
  max_loops: 3
search:
  max_sources: 8
```

**有効化**：Docker（オプション）、DuckDuckGoのみ

**予想時間**：タスクあたり2-4分

#### 最大品質（研究）

```yaml
# すべての機能、最高品質
ollama:
  model: llama2:70b
  timeout_sec: 300
validation:
  min_loops: 3
  max_loops: 7
search:
  max_sources: 15
```

**有効化**：Docker、browser-use

**予想時間**：タスクあたり10-20分

## アップグレードパス

### 最小セットアップからフルセットアップへ

```bash
# 1. 既にある：Ollama + Hermes

# 2. Dockerを追加
sudo apt-get install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER
# ログアウト/ログイン

# 3. browser-useを追加
cd /tmp && git clone https://github.com/browser-use/browser-use.git
cd browser-use && pip install -e .
playwright install chromium

# 4. 段階的な改善をテスト
hermes run --prompt "upgrade test" --max-validation 2
```

### ダウングレード（オプションコンポーネントの削除）

```bash
# browser-useを削除
pip uninstall browser-use

# Dockerを停止/無効化
sudo systemctl stop docker
sudo systemctl disable docker

# Hermesは自動的にフォールバック
# 設定変更は不要
```

## メンテナンススケジュール

### 日次（自動）

- Ollamaサービスのステータスをチェック
- ディスク容量を監視

### 週次（手動）

```bash
# Dockerリソースをクリーン
docker system prune -a

# ログをチェック
hermes debug --error -n 500 | grep -E "(ollama|docker|browser)"

# すべてのコンポーネントをテスト
hermes run --prompt "weekly health check" --max-validation 1
```

### 月次（手動）

```bash
# Ollamaを更新
curl -fsSL https://ollama.ai/install.sh | sh

# Dockerを更新
sudo apt-get update && sudo apt-get upgrade docker-ce

# browser-useを更新
cd /tmp/browser-use && git pull && pip install -e .

# Playwrightを更新
playwright install chromium

# 完全統合テスト
hermes run --prompt "monthly verification" --max-validation 3
```

## リソース計画

### ディスク容量要件

| コンポーネント | 初期 | 増加率 | 備考 |
|-----------|---------|-------------|-------|
| Ollama | 10 GB | モデルあたり+5 GB | モデルは`~/.ollama/`にあります |
| Docker | 2 GB | +1 GB/月 | イメージとコンテナ |
| browser-use | 300 MB | 最小 | Playwrightブラウザ |
| Hermesデータ | 100 MB | +10 MB/日 | `~/.hermes/`のレポートとログ |

**合計**：初期12-15 GB、継続的に+10-50 MB/日

### メモリ要件

| ワークロード | Ollama | Docker | browser-use | 合計 |
|----------|--------|--------|-------------|-------|
| アイドル | 500 MB | 200 MB | 0 MB | 700 MB |
| 単一タスク | 4-8 GB | 500 MB | 200 MB | 5-9 GB |
| キュー処理 | 4-8 GB | 500 MB | 200 MB | 5-9 GB |

**推奨**：快適な動作のため16 GB RAM

## 関連ドキュメント

- [メインREADME](../../README.md) - プロジェクト概要
- [インストールガイド](../../README.md#installation)
- [統合セットアップ](../../README.md#integration-setup)
- [コマンドリファレンス](../command/README.md)
- [トラブルシューティング](../../README.md#troubleshooting-highlights)

## 外部リソース

- [Ollamaドキュメント](https://github.com/ollama/ollama)
- [Dockerドキュメント](https://docs.docker.com/)
- [browser-use GitHub](https://github.com/browser-use/browser-use)
- [Playwrightドキュメント](https://playwright.dev/)

## サポート

依存関係固有の問題について：

1. **ログをチェック**：`hermes debug --error -n 200`
2. **コンポーネントを個別にテスト**（検証チェックリストのコマンドを使用）
3. **特定の依存関係の詳細ドキュメントを確認**
4. **既知の問題については外部プロジェクトのイシュートラッカーをチェック**

Hermes統合の問題について：

- [トラブルシューティングガイド](../../README.md#troubleshooting-highlights)を確認
- [アーキテクチャドキュメント](../../ARCHITECTURE.md)をチェック
- 完全なログとともに報告：`hermes debug -n 500 > debug.log`

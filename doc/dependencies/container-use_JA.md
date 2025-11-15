# Container-use（Docker）統合

## 概要

Container-use（dagger-io経由）は、Hermesに分離されたテキスト処理を提供します。一貫性とセキュリティのために、正規化と処理タスクを使い捨てDockerコンテナで実行します。

HermesはDockerが利用できない場合、自動的にローカル処理にフォールバックし、ワークフローが常に完了することを保証します。

## 動作モード

### モード1：コンテナ処理（推奨）

- **有効化**：Dockerが実行中の場合
- **技術**：dagger-io + Docker
- **利点**：
  - 分離された実行環境
  - システム間で一貫した処理
  - ローカル依存関係の競合なし
  - 再現可能な結果
- **要件**：
  - Docker 20.10以上がインストール済み
  - Dockerデーモンが実行中
  - ユーザーがdockerグループに所属（Linux）

### モード2：ローカルフォールバック（自動）

- **有効化**：Dockerが利用できない場合
- **技術**：ネイティブPython処理
- **利点**：
  - Docker依存なし
  - より高速な実行（コンテナオーバーヘッドなし）
  - 制限された環境で動作
- **制限事項**：
  - システム間で結果が異なる可能性
  - 実行の分離なし

## コンテナモードが重要な場合

### コンテナモードを使用する場合：

- 本番デプロイ
- マルチユーザー環境
- CI/CDパイプライン
- 再現性が重要
- セキュリティ分離が必要

### ローカルモードが許容される場合：

- 個人的な開発
- 迅速なプロトタイピング
- Docker利用不可（一時的）
- 簡単なテキスト処理
- 単一ユーザーワークステーション

## Dockerインストール

### Ubuntu/Debian

```bash
# パッケージインデックスを更新
sudo apt-get update

# 依存関係をインストール
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# DockerのオフィシャルGPGキーを追加
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 安定版リポジトリをセットアップ
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker Engineをインストール
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# インストールを確認
sudo docker run hello-world
```

### CentOS/RHEL

```bash
# 必要なパッケージをインストール
sudo yum install -y yum-utils

# Dockerリポジトリを追加
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Dockerをインストール
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Dockerを起動
sudo systemctl start docker
sudo systemctl enable docker

# 確認
sudo docker run hello-world
```

### macOS

```bash
# オプション1：Homebrew
brew install --cask docker

# オプション2：Docker Desktopをダウンロード
# https://www.docker.com/products/docker-desktop にアクセス

# Docker Desktopアプリケーションを起動

# ターミナルから確認
docker run hello-world
```

### Windows（WSL2）

1. **WSL2をインストール**
   ```powershell
   wsl --install
   ```

2. **Docker Desktopをインストール**
   - https://www.docker.com/products/docker-desktop からダウンロード
   - 設定でWSL2バックエンドを有効化

3. **WSL2で確認**
   ```bash
   docker run hello-world
   ```

## インストール後のセットアップ

### Linux：ユーザーをDockerグループに追加

`sudo`なしでDockerを実行：

```bash
# 現在のユーザーをdockerグループに追加
sudo usermod -aG docker $USER

# 変更を有効にするためログアウト/ログイン
# またはnewgrpを使用
newgrp docker

# 確認（sudo不要）
docker ps
```

### Dockerサービスを有効化

```bash
# Dockerデーモンを起動
sudo systemctl start docker

# 起動時に有効化
sudo systemctl enable docker

# ステータスをチェック
sudo systemctl status docker
```

### インストールを確認

```bash
# Dockerバージョンをチェック
docker --version

# デーモンステータスをチェック
docker info

# テストコンテナを実行
docker run hello-world

# 実行中のコンテナをリスト
docker ps

# すべてのコンテナをリスト
docker ps -a
```

## Hermes統合

### 自動検出

Hermesは自動的にDockerの可用性を検出：

```python
# 各実行時にチェック
try:
    result = subprocess.run(["docker", "ps"], capture_output=True)
    if result.returncode == 0:
        # コンテナモードを使用
    else:
        # ローカルにフォールバック
except Exception:
    # ローカルにフォールバック
```

### コンテナモードを確認

```bash
# タスクを実行
hermes run --prompt "test container" --max-validation 1

# ログでコンテナ使用をチェック
hermes log -n 50 | grep -i docker

# 期待される：警告メッセージなし
# フォールバック時："Docker is unavailable, using local processing"
```

### ローカルモードを強制

テストまたはデバッグのため：

```bash
# Dockerを一時的に停止
sudo systemctl stop docker

# Hermesを実行（フォールバックを使用）
hermes run --prompt "..."

# Dockerを再起動
sudo systemctl start docker
```

## コンテナのライフサイクル

### 実行中に何が起こるか

1. **コンテナ作成**
   - Hermesがdagger-io経由でコンテナを要求
   - Dockerが必要なイメージをプル（初回のみ）
   - マウントされたボリュームでコンテナが起動

2. **処理**
   - テキスト正規化が分離環境で実行
   - 結果がHermesに返される

3. **クリーンアップ**
   - コンテナが自動的に停止
   - 一時データが削除
   - リソースが解放

### コンテナを監視

```bash
# Hermes実行中のコンテナアクティビティを監視
watch -n 1 docker ps

# コンテナログを表示
docker logs <container_id>

# リソース使用状況をチェック
docker stats
```

## トラブルシューティング

### Dockerデーモンが実行されていない

**症状**：「Cannot connect to the Docker daemon」

**解決策**：

```bash
# デーモンステータスをチェック
sudo systemctl status docker

# デーモンを起動
sudo systemctl start docker

# 起動時に有効化
sudo systemctl enable docker

# 確認
docker ps
```

### 権限が拒否された

**症状**：「permission denied while trying to connect to the Docker daemon socket」

**原因**：ユーザーがdockerグループにいない

**解決策**：

```bash
# ユーザーをdockerグループに追加
sudo usermod -aG docker $USER

# 変更を適用（ログアウト/ログインまたはnewgrpを使用）
newgrp docker

# 確認
docker ps  # sudoなしで動作するはず
```

### ポート競合

**症状**：「port is already allocated」

**解決策**：

```bash
# ポートを使用しているプロセスを見つける
sudo lsof -i :PORT
sudo netstat -tulpn | grep PORT

# プロセスを終了するかHermes設定を変更
sudo kill <PID>
```

### ディスク容量の問題

**症状**：「no space left on device」

**ディスク使用状況をチェック**：

```bash
# Dockerディスク使用状況をチェック
docker system df

# 利用可能なスペースをチェック
df -h /var/lib/docker
```

**クリーンアップ**：

```bash
# 未使用のコンテナを削除
docker container prune

# 未使用のイメージを削除
docker image prune

# 未使用のボリュームを削除
docker volume prune

# 未使用のものすべてを削除
docker system prune -a

# または解放する量を指定
docker system prune -a --volumes --filter "until=24h"
```

### イメージプル失敗

**症状**：「Error response from daemon: pull access denied」

**解決策**：

1. **インターネット接続をチェック**
   ```bash
   ping registry-1.docker.io
   ```

2. **異なるレジストリミラーを使用**
   ```bash
   # /etc/docker/daemon.jsonを編集
   sudo tee /etc/docker/daemon.json > /dev/null <<EOF
   {
     "registry-mirrors": ["https://mirror.example.com"]
   }
   EOF

   sudo systemctl restart docker
   ```

3. **手動でプル**
   ```bash
   docker pull python:3.10-slim
   ```

### コンテナ起動失敗

**症状**：「Error starting userland proxy」

**解決策**：

1. **Dockerを再起動**
   ```bash
   sudo systemctl restart docker
   ```

2. **ファイアウォールをチェック**
   ```bash
   # UFW（Ubuntu）
   sudo ufw status
   sudo ufw allow docker

   # iptables
   sudo iptables -L -n
   ```

3. **SELinuxをチェック（RHEL/CentOS）**
   ```bash
   getenforce
   # 'Enforcing'の場合、テスト用に一時的にPermissiveに設定
   sudo setenforce 0
   ```

### ネットワークの問題

**症状**：コンテナがインターネットに到達できない

**解決策**：

1. **Dockerネットワークをチェック**
   ```bash
   docker network ls
   docker network inspect bridge
   ```

2. **コンテナから接続性をテスト**
   ```bash
   docker run --rm alpine ping -c 3 8.8.8.8
   docker run --rm alpine ping -c 3 google.com
   ```

3. **Dockerネットワークをリセット**
   ```bash
   sudo systemctl stop docker
   sudo ip link delete docker0
   sudo systemctl start docker
   ```

4. **DNS設定をチェック**
   ```bash
   # /etc/docker/daemon.jsonを編集
   sudo tee -a /etc/docker/daemon.json > /dev/null <<EOF
   {
     "dns": ["8.8.8.8", "8.8.4.4"]
   }
   EOF

   sudo systemctl restart docker
   ```

### メモリ制限

**症状**：コンテナログに「OOMKilled」

**解決策**：

```bash
# Dockerメモリ制限をチェック
docker info | grep Memory

# メモリ制限を増やす（Docker Desktop）
# 設定 → リソース → メモリ → スライダーを増やす

# またはコンテナごとにメモリ制限を設定（コード変更が必要）
docker run --memory="2g" ...
```

### パフォーマンスの遅さ

**症状**：コンテナ操作に時間がかかりすぎる

**最適化**：

1. **Dockerボリュームマウントを使用**
   ```bash
   # 現在のマウントタイプをチェック
   docker inspect <container_id> | grep -A 10 Mounts
   ```

2. **未使用のリソースをプルーン**
   ```bash
   docker system prune
   ```

3. **Dockerリソースを増やす**（macOS/Windows）
   - Docker Desktop → 設定 → リソース
   - CPUとメモリを増やす

4. **ディスクパフォーマンスをチェック**
   ```bash
   sudo iotop  # I/Oを監視
   ```

## パフォーマンスチューニング

### リソース割り当て

#### 開発用（8 GB RAMシステム）

```bash
# Docker Desktop設定
CPUs: 2
Memory: 2 GB
Swap: 1 GB
```

#### 本番用（16 GB以上のRAMシステム）

```bash
# Docker Desktop設定
CPUs: 4
Memory: 4 GB
Swap: 2 GB
```

### イメージ最適化

現在、Hermesはデフォルトのdaggerイメージを使用しています。将来の最適化：

- 必要なイメージを事前にプル
- より軽量なベースイメージを使用
- 実行間でレイヤーをキャッシュ

### バッチ処理

`hermes queue`の場合：

```bash
# 同じセッション内のタスク間でコンテナを再利用
# 個別のタスク実行を最適化する必要なし
hermes queue --all
```

## 監視とログ記録

### リアルタイム監視

```bash
# コンテナの作成/削除を監視
watch -n 1 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"'

# リソース使用状況を監視
docker stats

# ログを表示
docker logs -f <container_id>
```

### Hermes統合ログ

```bash
# コンテナ警告をチェック
hermes debug -n 100 | grep -i docker

# フォールバック有効化をチェック
hermes log -n 50 | grep -i "using local"
```

### システムログ

```bash
# Dockerデーモンログ（systemd）
journalctl -u docker -f

# Dockerデーモンログ（ファイル）
sudo tail -f /var/log/docker.log
```

## セキュリティに関する考慮事項

### コンテナ分離

Hermesコンテナはデフォルトのdockerセキュリティで実行：

- 名前空間化されたプロセス
- 限定されたファイルシステムアクセス
- ネットワーク分離（デフォルトブリッジ）
- 読み取り専用ルートファイルシステム（可能な場合）

### ベストプラクティス

1. **Dockerを最新に保つ**
   ```bash
   sudo apt-get update && sudo apt-get upgrade docker-ce
   ```

2. **Dockerをrootとして実行しない**（dockerグループを使用）

3. **コンテナリソースを制限**
   ```bash
   # 将来のHermes設定
   container:
     memory_limit: 2g
     cpu_limit: 2
   ```

4. **定期的なクリーンアップ**
   ```bash
   # 週次Cronジョブ
   0 2 * * 0 /usr/bin/docker system prune -af
   ```

### ネットワークセキュリティ

```bash
# Docker APIアクセスを制限
sudo chmod 660 /var/run/docker.sock

# リモートDocker用にTLSを使用（該当する場合）
# /etc/docker/daemon.jsonで設定
```

## 高度な設定

### Dockerデーモン設定

`/etc/docker/daemon.json`を編集：

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "dns": ["8.8.8.8", "8.8.4.4"],
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5
}
```

変更を適用：

```bash
sudo systemctl restart docker
```

### ストレージドライバーの最適化

```bash
# 現在のドライバーをチェック
docker info | grep "Storage Driver"

# 推奨：overlay2（最新システムではデフォルト）

# ドライバーを変更（データ移行が必要）
# /etc/docker/daemon.jsonを編集
{
  "storage-driver": "overlay2"
}

# Dockerを再起動
sudo systemctl restart docker
```

## CI/CD統合

### GitHub Actionsの例

```yaml
name: Hermes Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      docker:
        image: docker:dind
        options: --privileged

    steps:
      - uses: actions/checkout@v2

      - name: Set up Docker
        run: |
          sudo systemctl start docker
          docker info

      - name: Install Hermes
        run: |
          pip install -e .

      - name: Test with containers
        run: |
          hermes run --prompt "CI test" --max-validation 1
```

### Docker-in-Docker（DinD）

コンテナ化されたCI環境の場合：

```bash
# Dockerを持つコンテナ内でHermesを実行
docker run --privileged -v /var/run/docker.sock:/var/run/docker.sock \
  your-hermes-image hermes run --prompt "test"
```

## メンテナンス

### 定期的なタスク

#### 週次

```bash
# 未使用のリソースをクリーンアップ
docker system prune -a --volumes

# ディスク使用状況をチェック
docker system df
```

#### 月次

```bash
# Dockerを更新
sudo apt-get update && sudo apt-get upgrade docker-ce

# ヘルスを確認
docker info
docker run hello-world
```

#### 必要に応じて

```bash
# すべてのDockerデータをクリア（核オプション）
docker system prune -a --volumes -f
sudo systemctl stop docker
sudo rm -rf /var/lib/docker
sudo systemctl start docker
```

## アンインストール

### Docker Engineを削除（Linux）

```bash
# Dockerを停止
sudo systemctl stop docker

# パッケージを削除
sudo apt-get purge docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Dockerデータを削除
sudo rm -rf /var/lib/docker
sudo rm -rf /var/lib/containerd

# Dockerグループを削除
sudo groupdel docker
```

### Docker Desktopを削除（macOS/Windows）

- macOS：Docker.appをゴミ箱にドラッグ
- Windows：コントロールパネル経由でアンインストール

### Hermesは動作し続けます

Docker削除後、Hermesは自動的にローカル処理モードを使用します。設定変更は不要です。

## 比較：コンテナ vs ローカルモード

| 側面 | コンテナモード | ローカルモード |
|--------|----------------|------------|
| **セットアップ** | Docker必須 | なし |
| **速度** | 遅い（オーバーヘッド） | 高速 |
| **分離** | はい | いいえ |
| **再現性** | 高い | 中程度 |
| **ディスク使用** | +1-2 GB | なし |
| **セキュリティ** | より良い | 良好 |
| **メンテナンス** | 定期的なクリーンアップ | なし |

## 関連ドキュメント

- [Ollama統合](./ollama.md)
- [browser-use統合](./browser-use.md)
- [Hermesアーキテクチャ](../../ARCHITECTURE.md)
- [インストールガイド](../../README.md#installation)

## 外部リソース

- [Dockerドキュメント](https://docs.docker.com/)
- [Dagger.io](https://dagger.io/)
- [Dockerベストプラクティス](https://docs.docker.com/develop/dev-best-practices/)

## サポート

Docker固有の問題について：
- 設定のため`docker info`をチェック
- デーモンエラーのため`journalctl -u docker`を確認
- `docker run hello-world`でテスト
- Hermesログをチェック：`hermes debug --error -n 100 | grep -i docker`

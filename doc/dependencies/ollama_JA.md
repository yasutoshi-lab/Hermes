# Ollama統合

## 概要

Ollamaは、Hermesのテキスト生成機能を支えるローカルLLM推論サーバーです。以下を処理します：

- 検索クエリ生成
- レポートの下書きと統合
- コンテンツの検証と批評
- フォローアップクエリの生成

OllamaはHermesの動作に**必須**です。

## システム要件

### 最小要件

- **CPU**：4コア（8以上推奨）
- **RAM**：8 GB（16 GB以上推奨）
- **ディスク**：モデル用に10 GB以上の空き容量
- **OS**：Linux、macOS、またはWindows（WSL2）

### gpt-oss:20b用の推奨要件

- **CPU**：8コア以上
- **RAM**：32 GB
- **GPU**：16 GB以上のVRAMを持つNVIDIA GPU（オプションだが大幅に高速）
- **ディスク**：20 GB以上の空き容量

### GPUサポート

- **NVIDIA**：CUDA 11.7以上のドライバーが必要
- **AMD**：Linux上でROCmサポート
- **Apple Silicon**：ネイティブMetalアクセラレーション

## インストール

### Linux（Ubuntu/Debian）

```bash
# ダウンロードとインストール
curl -fsSL https://ollama.ai/install.sh | sh

# インストールを確認
ollama --version
```

### macOS

```bash
# オプション1：Homebrew
brew install ollama

# オプション2：直接ダウンロード
# https://ollama.ai/download からダウンロード
# .dmgファイルをインストール

# インストールを確認
ollama --version
```

### Windows（WSL2）

```bash
# WSL2 Ubuntu内で
curl -fsSL https://ollama.ai/install.sh | sh

# 確認
ollama --version
```

### Docker（代替方法）

```bash
# Ollamaイメージをプル
docker pull ollama/ollama

# サーバーを実行
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# 確認
curl http://localhost:11434/api/version
```

## モデルのセットアップ

### 必要なモデルをプル

Hermesはデフォルトで`gpt-oss:20b`を使用します：

```bash
# まずOllamaサーバーを起動
ollama serve &

# モデルをプル（13 GBダウンロード）
ollama pull gpt-oss:20b
```

これは`~/.ollama/models/`にダウンロードされます。

### 代替モデル

`gpt-oss:20b`が利用できない場合、以下の代替を使用：

```bash
# より小型で高速なモデル
ollama pull llama2:7b      # 3.8 GB - 高速だが品質は低い
ollama pull llama2:13b     # 7.3 GB - 良好なバランス
ollama pull mistral:7b     # 4.1 GB - 高速、良好な品質

# より大型で高品質なモデル
ollama pull llama2:70b     # 39 GB - 最高品質、遅い
ollama pull mixtral:8x7b   # 26 GB - 高品質
```

`~/.hermes/config.yaml`で設定：

```yaml
ollama:
  model: llama2:13b  # ここで変更
```

または実行ごとにオーバーライド：

```bash
hermes run --prompt "..." --model llama2:13b
```

### インストール済みモデルのリスト

```bash
ollama list
```

### モデルの削除

```bash
ollama rm gpt-oss:20b
```

## サーバーの起動

### バックグラウンドサービス（推奨）

```bash
# バックグラウンドでサーバーを起動
ollama serve &

# ステータスをチェック
curl http://localhost:11434/api/version

# 期待される出力：
# {"version":"0.x.x"}
```

### Systemdサービス（Linux）

```bash
# サービスファイルを作成
sudo tee /etc/systemd/system/ollama.service > /dev/null <<EOF
[Unit]
Description=Ollama LLM Server
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 有効化して起動
sudo systemctl enable ollama
sudo systemctl start ollama

# ステータスをチェック
sudo systemctl status ollama
```

### Dockerコンテナ

```bash
# コンテナを起動
docker start ollama

# ログを表示
docker logs -f ollama

# コンテナを停止
docker stop ollama
```

## 設定

### デフォルト設定

Ollamaはデフォルトで`http://localhost:11434`をリッスンします。

### カスタムホスト/ポート

```bash
# 環境変数を設定
export OLLAMA_HOST=0.0.0.0:11434

# サーバーを起動
ollama serve
```

### GPU設定

```bash
# CPUのみモードを強制（GPUに問題がある場合）
export CUDA_VISIBLE_DEVICES=""
ollama serve

# 特定のGPUを使用
export CUDA_VISIBLE_DEVICES=0
ollama serve

# 複数のGPUを使用
export CUDA_VISIBLE_DEVICES=0,1
ollama serve
```

### メモリ制限

```bash
# GPUメモリ使用量を制限（MB単位）
export OLLAMA_GPU_MEMORY_FRACTION=0.8
ollama serve
```

## Hermes統合

### 設定ファイル

`~/.hermes/config.yaml`を編集：

```yaml
ollama:
  api_base: http://localhost:11434/api/chat  # APIエンドポイント
  model: gpt-oss:20b                         # 使用するモデル
  retry: 3                                    # 再試行回数
  timeout_sec: 180                            # リクエストタイムアウト（秒）
```

### 実行時オーバーライド

```bash
# 異なるモデルを使用
hermes run --prompt "..." --model llama2:13b

# 遅いモデル用にタイムアウトを増やす
hermes run --prompt "..." --timeout 300

# 異なるAPIエンドポイント
hermes run --prompt "..." --api http://remote-host:11434/api/chat
```

## 検証

### サーバーステータスをチェック

```bash
# 方法1：curl
curl http://localhost:11434/api/version

# 方法2：生成をテスト
ollama run gpt-oss:20b "Hello, world!"
```

### Hermesでテスト

```bash
# 簡単なテストタスク
hermes run --prompt "テスト" --min-validation 1 --max-validation 1
```

成功すれば、レポートが`~/.hermes/history/`に生成されます。

## トラブルシューティング

### サーバーが起動しない

**症状**：`ollama serve`が失敗するか、すぐに終了する

**原因と解決策**：

1. **ポートが既に使用中**
   ```bash
   # ポート11434を使用しているものをチェック
   lsof -i :11434
   sudo netstat -tulpn | grep 11434

   # 既存のプロセスを終了
   kill <PID>

   # または異なるポートを使用
   export OLLAMA_HOST=localhost:11435
   ollama serve
   ```

2. **権限の問題**
   ```bash
   # Ollamaインストールをチェック
   which ollama
   ls -la $(which ollama)

   # 必要に応じて再インストール
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. **依存関係の欠落（Linux）**
   ```bash
   # 必要なライブラリをインストール
   sudo apt-get update
   sudo apt-get install -y libgomp1
   ```

### 接続拒否

**症状**：`hermes run`が「Ollama connection error」を報告

**解決策**：

```bash
# 1. サーバーが実行中か確認
ps aux | grep ollama
curl http://localhost:11434/api/version

# 2. 実行されていない場合はサーバーを起動
ollama serve &

# 3. ファイアウォールをチェック（Linux）
sudo ufw status
sudo ufw allow 11434/tcp

# 4. 設定を確認
cat ~/.hermes/config.yaml | grep -A 4 ollama
```

### タイムアウトエラー

**症状**：「Request timed out after 180s」

**原因**：

- 利用可能なリソースに対してモデルが大きすぎる
- 長い推論時間を要する複雑なクエリ
- GPUメモリが枯渇

**解決策**：

1. **タイムアウトを増やす**
   ```yaml
   # ~/.hermes/config.yaml
   ollama:
     timeout_sec: 300  # 5分
   ```

2. **より小型のモデルを使用**
   ```bash
   hermes run --prompt "..." --model llama2:7b
   ```

3. **クエリの複雑さを減らす**
   ```bash
   # ソースと検証ループを減らす
   hermes run --prompt "..." \
     --max-search 5 \
     --min-validation 1 \
     --max-validation 2
   ```

4. **GPUメモリを解放**
   ```bash
   # 他のGPUプロセスを終了
   nvidia-smi
   kill <PID>

   # Ollamaを再起動
   pkill ollama
   ollama serve &
   ```

### モデルが見つからない（404エラー）

**症状**：「Model 'gpt-oss:20b' not found」

**解決策**：

```bash
# 利用可能なモデルをリスト
ollama list

# モデルをプル
ollama pull gpt-oss:20b

# 確認
ollama list | grep gpt-oss
```

### パフォーマンスの遅さ

**症状**：タスクに5分以上かかる

**最適化**：

1. **利用可能な場合はGPUを使用**
   ```bash
   # GPU検出をチェック
   nvidia-smi

   # OllamaがGPUを認識しているか確認
   ollama run gpt-oss:20b "test"
   # nvidia-smiでGPU使用量が表示されるはず
   ```

2. **モデルサイズを削減**
   ```bash
   # より小型のモデルは高速
   hermes run --prompt "..." --model mistral:7b
   ```

3. **量子化モデル**
   ```bash
   # 量子化バージョンをプル（利用可能な場合）
   ollama pull gpt-oss:20b-q4_0  # 4ビット量子化
   ```

4. **システムリソースを増やす**
   - 他のアプリケーションを閉じる
   - スワップ領域を増やす
   - RAMを追加

### GPUメモリ不足

**症状**：ログにCUDA out of memoryエラー

**解決策**：

1. **CPUモードを使用**
   ```bash
   export CUDA_VISIBLE_DEVICES=""
   pkill ollama
   ollama serve &
   ```

2. **より小型のモデルを使用**
   ```bash
   ollama pull llama2:7b
   hermes run --prompt "..." --model llama2:7b
   ```

3. **バッチサイズを削減**（将来のOllamaバージョンで利用可能な場合）

4. **他のGPUアプリケーションを閉じる**
   ```bash
   # GPU使用状況をチェック
   nvidia-smi

   # GPUプロセスを終了
   kill <PID>
   ```

### 誤った応答

**症状**：生成されたテキストが意味不明または反復的

**原因**：

- モデルダウンロードが破損
- システムリソース不足
- Ollamaバージョンとモデルの互換性がない

**解決策**：

1. **モデルを再ダウンロード**
   ```bash
   ollama rm gpt-oss:20b
   ollama pull gpt-oss:20b
   ```

2. **Ollamaを更新**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. **異なるモデルを試す**
   ```bash
   ollama pull llama2:13b
   hermes run --prompt "..." --model llama2:13b
   ```

## パフォーマンスチューニング

### 一般的なハードウェア用の最適設定

#### 8 GB RAM、GPU無し

```yaml
ollama:
  model: mistral:7b
  timeout_sec: 300

validation:
  max_loops: 2

search:
  max_sources: 5
```

#### 16 GB RAM、GPU無し

```yaml
ollama:
  model: llama2:13b
  timeout_sec: 240

validation:
  max_loops: 3

search:
  max_sources: 8
```

#### 32 GB以上のRAM、GPU 8 GB以上

```yaml
ollama:
  model: gpt-oss:20b
  timeout_sec: 180

validation:
  max_loops: 3

search:
  max_sources: 12
```

### バッチ処理の最適化

`hermes queue --all`の場合：

1. **検証ループを減らす**
   ```yaml
   validation:
     min_loops: 1
     max_loops: 2
   ```

2. **ソースを制限**
   ```yaml
   search:
     max_sources: 6
   ```

3. **夜間に実行**
   ```bash
   # 午前2時のCronジョブ
   0 2 * * * /path/to/venv/bin/hermes queue --all
   ```

## 監視

### リソース使用状況をチェック

```bash
# CPU/メモリ
top -p $(pgrep ollama)
htop -p $(pgrep ollama)

# GPU
watch -n 1 nvidia-smi

# ディスクI/O
iotop -p $(pgrep ollama)
```

### ログ監視

```bash
# Ollamaログ（systemdの場合）
journalctl -u ollama -f

# Hermesログ
hermes log --follow
hermes debug --follow
```

### パフォーマンスメトリクス

Hermesログで追跡：

```bash
# 平均応答時間
hermes debug -n 1000 | grep "Received response" | grep -oE '[0-9.]+s' | awk '{sum+=$1; count++} END {print sum/count "s avg"}'

# タイムアウト回数
hermes debug --error -n 1000 | grep -i timeout | wc -l
```

## 高度な設定

### モデル選択戦略

| ユースケース | 推奨モデル | 必要RAM | 速度 |
|----------|------------------|--------------|-------|
| クイックテスト | mistral:7b | 8 GB | 高速 |
| バランスのとれた品質 | llama2:13b | 16 GB | 中程度 |
| 高品質 | gpt-oss:20b | 32 GB | 遅い |
| 最高品質 | llama2:70b | 64 GB | 非常に遅い |

### マルチモデルセットアップ

異なるタスクに異なるモデルを使用：

```bash
# クエリに高速モデル
hermes run --prompt "..." --query-model mistral:7b

# ドラフトに大型モデル
hermes run --prompt "..." --draft-model gpt-oss:20b
```

（注：マルチモデルサポートにはコード変更が必要）

## セキュリティに関する考慮事項

### ネットワーク公開

デフォルトでは、Ollamaはlocalhostのみにバインドします。ネットワークに公開するには：

```bash
# ⚠️ セキュリティリスク - ファイアウォールを使用
export OLLAMA_HOST=0.0.0.0:11434
ollama serve
```

**推奨**：認証付きリバースプロキシを使用：

```nginx
# nginx設定
location /ollama/ {
    auth_basic "Ollama API";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:11434/;
}
```

### モデルの整合性

ダウンロード後にモデルのチェックサムを確認：

```bash
# 詳細付きモデルをリスト
ollama list

# 疑わしい場合は再ダウンロード
ollama rm gpt-oss:20b
ollama pull gpt-oss:20b
```

## Ollamaの更新

```bash
# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew upgrade ollama

# サーバーを再起動
pkill ollama
ollama serve &

# Hermesで再テスト
hermes run --prompt "test" --max-validation 1
```

## アンインストール

### Ollamaを削除

```bash
# Linux
sudo rm /usr/local/bin/ollama
sudo rm -rf /usr/share/ollama

# macOS
brew uninstall ollama

# モデルとデータを削除
rm -rf ~/.ollama
```

### Hermes設定を削除

```bash
# 履歴を保持するがOllama設定をリセット
hermes run --clear
```

## 関連ドキュメント

- [Hermes設定](../../README.md#configuration-overview)
- [hermes runコマンド](../command/run.md)
- [トラブルシューティングガイド](../../README.md#troubleshooting-highlights)
- [公式Ollamaドキュメント](https://github.com/ollama/ollama)

## サポート

- **Ollamaの問題**：https://github.com/ollama/ollama/issues
- **Hermesの問題**：診断のため`hermes debug --error`をチェック

# Hermes - Literature Summarization & Analysis Agent

Hermesは、開発者や研究者が論文や技術文書を手元の環境で要約・分析するための研究支援エージェントです。

## 特徴

- **ローカル処理**: すべての処理をローカル環境で実行し、プライバシーを保護
- **高度な要約**: Ollama + gpt-oss:20bによる文献の要約と分析
- **Web検索統合**: Web-Search-MCPによる関連情報の自動収集
- **安全な環境**: Container Useによる隔離された実行環境
- **タスクスケジューリング**: 指定時刻での自動処理
- **多言語対応**: 日本語・英語のサポート

## アーキテクチャ

```
Frontend (React + TypeScript)
    ↓
Backend API (FastAPI)
    ↓
PostgreSQL + Ollama + Web-Search-MCP + Container Use
```

## 技術スタック

### バックエンド
- FastAPI 0.115.0
- SQLAlchemy 2.0 + PostgreSQL
- APScheduler (タスクスケジューリング)
- Ollama (LLM)

### フロントエンド
- React + TypeScript
- Tailwind CSS
- React Router
- i18next (多言語対応)

### インフラ
- Docker + Docker Compose
- PostgreSQL 16

## セットアップ

### 前提条件
- Docker & Docker Compose
- Ollama (ローカルインストール)
- Python 3.11+
- Node.js 18+

### インストール

1. リポジトリのクローン
```bash
git clone <repository-url>
cd Hermes
```

2. Ollamaモデルのダウンロード
```bash
ollama pull gpt-oss:20b
```

3. Dockerサービスの起動
```bash
cd docker
docker-compose up -d
```

4. バックエンドの起動
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

5. フロントエンドの起動
```bash
cd frontend
npm install
npm run dev
```

## 開発状況

現在、以下の機能を開発中です：

- [x] プロジェクト構造の初期化
- [ ] データベーススキーマの設計
- [ ] バックエンドAPI基盤
- [ ] フロントエンド基盤
- [ ] ユーザー認証
- [ ] ファイルアップロード
- [ ] タスクスケジューラー
- [ ] Ollama統合
- [ ] Web-Search-MCP統合
- [ ] Container Use統合

## ライセンス

TBD

## 貢献

貢献を歓迎します！詳細はCONTRIBUTING.mdを参照してください。

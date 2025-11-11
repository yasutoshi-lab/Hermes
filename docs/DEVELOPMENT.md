# Development Guide

## 開発環境のセットアップ

### 前提条件

- Python 3.11以上
- Node.js 18以上
- Docker & Docker Compose
- Ollama (ローカルインストール)

### 初回セットアップ

1. **リポジトリのクローン**
```bash
git clone <repository-url>
cd Hermes
```

2. **環境変数の設定**
```bash
cp .env.example .env
# .envファイルを編集して適切な値を設定
```

3. **Ollamaモデルのダウンロード**
```bash
ollama pull gpt-oss:20b
```

4. **データベースの起動**
```bash
cd docker
docker-compose up -d postgres
```

5. **バックエンドのセットアップ**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# データベースマイグレーション
alembic upgrade head

# 開発サーバーの起動
uvicorn app.main:app --reload
```

6. **フロントエンドのセットアップ**
```bash
cd frontend
npm install
npm run dev
```

## プロジェクト構造

```
Hermes/
├── backend/              # FastAPIバックエンド
│   ├── app/
│   │   ├── api/         # APIエンドポイント
│   │   ├── core/        # コア設定（config, security等）
│   │   ├── db/          # データベース接続
│   │   ├── models/      # SQLAlchemyモデル
│   │   ├── schemas/     # Pydanticスキーマ
│   │   ├── services/    # ビジネスロジック
│   │   └── main.py      # アプリケーションエントリーポイント
│   ├── tests/           # テストコード
│   └── alembic/         # データベースマイグレーション
├── frontend/            # Reactフロントエンド
│   ├── src/
│   │   ├── api/         # API通信レイヤー
│   │   ├── components/  # Reactコンポーネント
│   │   ├── layouts/     # レイアウトコンポーネント
│   │   ├── pages/       # ページコンポーネント
│   │   ├── hooks/       # カスタムフック
│   │   ├── stores/      # 状態管理
│   │   └── i18n/        # 多言語対応
│   └── public/          # 静的ファイル
├── docker/              # Docker設定
│   └── docker-compose.yml
└── docs/                # ドキュメント
```

## 開発ワークフロー

### ブランチ戦略

- `main`: 本番環境用ブランチ
- `develop`: 開発用ブランチ
- `feature/*`: 機能開発用ブランチ
- `fix/*`: バグ修正用ブランチ

### コミットメッセージ規約

```
<type>: <subject>

<body>

<footer>
```

**Type:**
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメントのみの変更
- `style`: コードの意味に影響を与えない変更（空白、フォーマット等）
- `refactor`: バグ修正や機能追加を行わないコード変更
- `test`: テストの追加や修正
- `chore`: ビルドプロセスやツールの変更

### テスト実行

**バックエンド:**
```bash
cd backend
pytest
pytest --cov=app tests/  # カバレッジ付き
```

**フロントエンド:**
```bash
cd frontend
npm test
npm run test:coverage
```

### コードフォーマット

**バックエンド:**
```bash
cd backend
black app tests
ruff check app tests
mypy app
```

**フロントエンド:**
```bash
cd frontend
npm run lint
npm run format
```

## デバッグ

### バックエンド

Visual Studio Codeの`launch.json`設定例：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false
    }
  ]
}
```

### フロントエンド

ブラウザのDevToolsを使用：
- React Developer Tools
- Redux DevTools (状態管理に応じて)

## トラブルシューティング

### データベース接続エラー

```bash
# PostgreSQLコンテナの状態確認
docker ps | grep hermes-db

# ログ確認
docker logs hermes-db

# コンテナの再起動
docker-compose restart postgres
```

### Ollamaモデルが見つからない

```bash
# インストール済みモデルの確認
ollama list

# モデルの再ダウンロード
ollama pull gpt-oss:20b
```

### ポート競合

デフォルトポート：
- フロントエンド: 3000 (Vite: 5173)
- バックエンド: 8000
- PostgreSQL: 5432
- Ollama: 11434

ポートを変更する場合は`.env`ファイルを編集してください。

## 追加リソース

- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [React公式ドキュメント](https://react.dev/)
- [Ollama公式ドキュメント](https://ollama.ai/docs)
- [SQLAlchemy 2.0ドキュメント](https://docs.sqlalchemy.org/)

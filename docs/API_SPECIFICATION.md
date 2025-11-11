# Hermes API Specification

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

すべての保護されたエンドポイントはJWT Bearer Tokenを必要とします。

```
Authorization: Bearer <token>
```

## Endpoints

### Authentication

#### POST /api/v1/auth/register
新規ユーザー登録

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "created_at": "2025-11-11T12:00:00Z"
}
```

#### POST /api/v1/auth/login
ユーザーログイン

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST /api/v1/auth/refresh
トークンのリフレッシュ

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response (200):**
```json
{
  "access_token": "new_token_here",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Files

#### POST /api/v1/files/upload
PDFファイルのアップロード

**Request:**
- Content-Type: multipart/form-data
- Max file size: 50MB
- Allowed extensions: .pdf

**Form Data:**
```
file: <binary>
```

**Response (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "file_name": "research_paper.pdf",
  "storage_path": "/uploads/user_1/research_paper_20251111.pdf",
  "file_size": 2048576,
  "uploaded_at": "2025-11-11T12:00:00Z"
}
```

#### GET /api/v1/files
ユーザーのアップロードファイル一覧

**Query Parameters:**
- `page`: int (default: 1)
- `limit`: int (default: 20, max: 100)

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "file_name": "research_paper.pdf",
      "file_size": 2048576,
      "uploaded_at": "2025-11-11T12:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "pages": 1
}
```

#### GET /api/v1/files/{file_id}
ファイル詳細情報

**Response (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "file_name": "research_paper.pdf",
  "storage_path": "/uploads/user_1/research_paper_20251111.pdf",
  "file_size": 2048576,
  "uploaded_at": "2025-11-11T12:00:00Z",
  "tasks": [
    {
      "id": 1,
      "task_type": "summary",
      "status": "success"
    }
  ]
}
```

#### DELETE /api/v1/files/{file_id}
ファイル削除

**Response (204):** No Content

### Tasks

#### POST /api/v1/tasks/summary
要約タスクの作成

**Request Body:**
```json
{
  "file_id": 1,
  "model_name": "gpt-oss:20b",
  "schedule_time": null,
  "options": {
    "language": "ja",
    "include_analysis": true,
    "web_search": true
  }
}
```

**Response (201):**
```json
{
  "id": 1,
  "user_id": 1,
  "file_id": 1,
  "task_type": "summary",
  "model_name": "gpt-oss:20b",
  "status": "pending",
  "created_at": "2025-11-11T12:00:00Z"
}
```

#### POST /api/v1/tasks/schedule
タスクのスケジュール予約

**Request Body:**
```json
{
  "file_id": 1,
  "task_type": "summary",
  "model_name": "gpt-oss:20b",
  "schedule_time": "2025-11-12T09:00:00Z",
  "options": {
    "language": "ja",
    "include_analysis": true
  }
}
```

**Response (201):**
```json
{
  "id": 2,
  "user_id": 1,
  "file_id": 1,
  "task_type": "summary",
  "model_name": "gpt-oss:20b",
  "schedule_time": "2025-11-12T09:00:00Z",
  "status": "scheduled",
  "created_at": "2025-11-11T12:00:00Z"
}
```

#### GET /api/v1/tasks
ユーザーのタスク一覧

**Query Parameters:**
- `page`: int (default: 1)
- `limit`: int (default: 20)
- `status`: string (pending/running/success/fail)
- `task_type`: string (summary/search)

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "file_name": "research_paper.pdf",
      "task_type": "summary",
      "model_name": "gpt-oss:20b",
      "status": "success",
      "created_at": "2025-11-11T12:00:00Z",
      "completed_at": "2025-11-11T12:05:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "pages": 1
}
```

#### GET /api/v1/tasks/{task_id}
タスク詳細と結果

**Response (200):**
```json
{
  "id": 1,
  "user_id": 1,
  "file_id": 1,
  "task_type": "summary",
  "model_name": "gpt-oss:20b",
  "status": "success",
  "created_at": "2025-11-11T12:00:00Z",
  "completed_at": "2025-11-11T12:05:00Z",
  "result": {
    "summary_text": "This paper discusses...",
    "analysis_text": "Key findings include...",
    "key_points": [
      "Point 1",
      "Point 2"
    ]
  }
}
```

#### DELETE /api/v1/tasks/{task_id}
タスクのキャンセル（実行中の場合は停止）

**Response (204):** No Content

### Models

#### GET /api/v1/models
利用可能なLLMモデル一覧

**Response (200):**
```json
{
  "models": [
    {
      "name": "gpt-oss:20b",
      "size": "20B",
      "capabilities": ["tool_calling", "reasoning"],
      "available": true
    },
    {
      "name": "qwen3:8b",
      "size": "8B",
      "capabilities": ["tool_calling"],
      "available": true
    }
  ]
}
```

### Messages (WebSocket)

#### WS /api/v1/ws/chat
リアルタイムチャット接続

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/chat?token=<jwt_token>');
```

**Send Message:**
```json
{
  "type": "message",
  "content": "この論文を要約してください",
  "task_id": 1
}
```

**Receive Message:**
```json
{
  "type": "message",
  "sender": "system",
  "content": "要約を開始しました...",
  "task_id": 1,
  "timestamp": "2025-11-11T12:00:00Z"
}
```

**Task Notification:**
```json
{
  "type": "task_update",
  "task_id": 1,
  "status": "success",
  "message": "要約が完了しました"
}
```

### Health Check

#### GET /api/v1/health
サービスのヘルスチェック

**Response (200):**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "components": {
    "database": "healthy",
    "ollama": "healthy",
    "web_search": "healthy",
    "container_use": "healthy"
  }
}
```

## Error Responses

すべてのエラーは以下の形式で返されます：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {}
  }
}
```

### Status Codes

- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

### Error Codes

- `INVALID_CREDENTIALS`: ログイン情報が無効
- `TOKEN_EXPIRED`: トークンの有効期限切れ
- `FILE_TOO_LARGE`: ファイルサイズが上限を超過
- `INVALID_FILE_TYPE`: 許可されていないファイル形式
- `TASK_NOT_FOUND`: タスクが見つからない
- `MODEL_NOT_AVAILABLE`: 指定されたモデルが利用不可
- `RATE_LIMIT_EXCEEDED`: レート制限を超過

## Rate Limiting

- 認証エンドポイント: 10 requests / minute
- ファイルアップロード: 5 uploads / hour
- タスク作成: 20 tasks / hour
- その他: 100 requests / minute

## Pagination

リスト取得エンドポイントは以下のページネーション形式を使用：

```json
{
  "items": [],
  "total": 100,
  "page": 1,
  "pages": 5,
  "has_next": true,
  "has_prev": false
}
```

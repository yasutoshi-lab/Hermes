# Hermes Backend API

FastAPI-based backend for the Hermes document summarization and analysis system.

## Features

- **FastAPI** with async support
- **RESTful API** with versioning (v1)
- **WebSocket** support for real-time communication
- **JWT Authentication** for secure access
- **CORS** configuration for frontend integration
- **Structured logging** (JSON and text formats)
- **Error handling** with standardized responses
- **Health check** endpoints
- **Docker** support

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── core/                # Core application components
│   │   ├── config.py        # Configuration management
│   │   ├── logging.py       # Logging setup
│   │   └── exceptions.py    # Error handlers
│   ├── api/                 # API routes
│   │   └── v1/              # API version 1
│   │       ├── __init__.py  # Router configuration
│   │       └── endpoints/   # Endpoint modules
│   │           └── health.py
│   ├── schemas/             # Pydantic models
│   │   └── base.py          # Base schemas
│   ├── models/              # SQLAlchemy models
│   ├── services/            # Business logic
│   └── db/                  # Database setup
├── tests/                   # Test suite
├── Dockerfile               # Docker configuration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Ollama (for LLM)

### Installation

1. Clone the repository:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run the application:
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the main module
python -m app.main
```

## Docker

Build and run with Docker:

```bash
# Build image
docker build -t hermes-backend .

# Run container
docker run -p 8000:8000 --env-file .env hermes-backend
```

## API Documentation

When running in debug mode, access:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## Endpoints

### Root
- `GET /` - API information

### Health
- `GET /api/v1/health` - Detailed health check
- `GET /api/v1/health/ping` - Simple ping

### Future Endpoints
- `/api/v1/auth` - Authentication
- `/api/v1/users` - User management
- `/api/v1/files` - File upload/management
- `/api/v1/tasks` - Task management
- `/api/v1/ws` - WebSocket connections

## Configuration

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `ENVIRONMENT` | Environment name | `development` |
| `DATABASE_URL` | PostgreSQL connection | Generated from components |
| `SECRET_KEY` | JWT secret key | Change in production! |
| `OLLAMA_BASE_URL` | Ollama API URL | `http://localhost:11434` |
| `LOG_LEVEL` | Logging level | `INFO` |

See `.env.example` for full configuration options.

## Development

### Code Style

Follow PEP 8 guidelines. Use type hints where possible.

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

### Logging

Logs are output to stdout in JSON format (production) or colored text (development).

```python
from app.core.logging import get_logger

logger = get_logger(__name__)
logger.info("Message", extra={"key": "value"})
```

## License

[Your License Here]

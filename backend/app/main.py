"""
Hermes FastAPI Application
Main application entry point for the document summarization & analysis agent.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import register_exception_handlers
from app.api.v1 import api_router

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # TODO: Initialize database connection pool
    # await init_db()

    # TODO: Initialize task scheduler
    # if settings.SCHEDULER_ENABLED:
    #     await start_scheduler()

    # TODO: Verify external service connections
    # await check_ollama_connection()
    # await check_mcp_connection()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")

    # TODO: Close database connections
    # await close_db()

    # TODO: Stop task scheduler
    # if settings.SCHEDULER_ENABLED:
    #     await stop_scheduler()

    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Hermes is a document summarization and analysis agent system. "
        "It provides REST and WebSocket APIs for processing academic papers, "
        "technical documents, and research materials using local LLM models."
    ),
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add GZip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add trusted host middleware in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1"]  # TODO: Configure from settings
    )

# Register exception handlers
register_exception_handlers(app)

# Include API routers
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs" if settings.DEBUG else "disabled",
        "health": "/api/v1/health"
    }


# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all HTTP requests."""
    import time
    from app.core.logging import RequestLogger

    start_time = time.time()

    response = await call_next(request)

    duration_ms = (time.time() - start_time) * 1000

    RequestLogger.log_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms
    )

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )

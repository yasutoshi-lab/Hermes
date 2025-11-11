"""
Health check endpoints.
Provides system health status and component availability checks.
"""
from typing import Dict
from fastapi import APIRouter, status
from datetime import datetime
import httpx
import logging

from app.core.config import settings
from app.schemas.base import HealthCheckResponse

router = APIRouter()
logger = logging.getLogger(__name__)


async def check_database() -> bool:
    """Check database connectivity."""
    try:
        # TODO: Add actual database connection check when DB is set up
        # from app.db.session import engine
        # async with engine.connect() as conn:
        #     await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def check_ollama() -> bool:
    """Check Ollama service availability."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            return response.status_code == 200
    except Exception as e:
        logger.warning(f"Ollama health check failed: {e}")
        return False


async def check_web_search_mcp() -> bool:
    """Check Web Search MCP service availability."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Attempt to connect to Web Search MCP
            response = await client.get(f"{settings.WEB_SEARCH_MCP_URL}/health", timeout=5.0)
            return response.status_code == 200
    except Exception as e:
        logger.warning(f"Web Search MCP health check failed: {e}")
        return False


@router.get(
    "",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health status of the API and its dependencies"
)
async def health_check() -> HealthCheckResponse:
    """
    Perform health check on the API and its components.

    Returns:
        HealthCheckResponse with status of all components
    """
    components: Dict[str, bool] = {
        "api": True,  # If we reach here, API is running
    }

    # Check optional components (don't fail if they're down)
    components["database"] = await check_database()
    components["ollama"] = await check_ollama()
    components["web_search_mcp"] = await check_web_search_mcp()

    # Overall status is healthy if API is running (other components are optional)
    overall_status = "healthy"

    # Log warnings for failed components
    for component, is_healthy in components.items():
        if not is_healthy and component != "api":
            logger.warning(f"Component '{component}' is not healthy")

    return HealthCheckResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        components=components
    )


@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Simple Ping",
    description="Simple ping endpoint for quick availability check"
)
async def ping() -> Dict[str, str]:
    """
    Simple ping endpoint.

    Returns:
        Dict with pong message
    """
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}

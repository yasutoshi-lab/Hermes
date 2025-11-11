"""API v1 router."""
from fastapi import APIRouter
from .endpoints import health

# Create v1 router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Future routers will be added here:
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(files.router, prefix="/files", tags=["files"])
# api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])

__all__ = ["api_router"]

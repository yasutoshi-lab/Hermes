"""
Base Pydantic schemas for common patterns.
Provides reusable schema classes for API responses and requests.
"""
from typing import Any, Dict, Generic, List, Optional, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# Base configuration for all schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLAlchemy models
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
    )


# Response schemas
class SuccessResponse(BaseSchema):
    """Standard success response."""

    success: bool = Field(default=True, description="Indicates successful operation")
    message: Optional[str] = Field(default=None, description="Optional success message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")


class ErrorDetail(BaseSchema):
    """Error detail structure."""

    message: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")
    code: int = Field(..., description="HTTP status code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")


class ErrorResponse(BaseSchema):
    """Standard error response."""

    success: bool = Field(default=False, description="Indicates failed operation")
    error: ErrorDetail = Field(..., description="Error details")


# Pagination schemas
class PaginationParams(BaseSchema):
    """Query parameters for pagination."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database query."""
        return self.page_size


T = TypeVar("T")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response wrapper."""

    success: bool = Field(default=True, description="Indicates successful operation")
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ) -> "PaginatedResponse[T]":
        """Create paginated response."""
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


# Timestamp mixin
class TimestampMixin(BaseSchema):
    """Mixin for models with timestamps."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")


# Health check schema
class HealthCheckResponse(BaseSchema):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    components: Dict[str, bool] = Field(
        default_factory=dict,
        description="Health status of components"
    )


# WebSocket message schemas
class WebSocketMessage(BaseSchema):
    """Base WebSocket message."""

    type: str = Field(..., description="Message type")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")


class WebSocketHeartbeat(BaseSchema):
    """WebSocket heartbeat message."""

    type: str = Field(default="heartbeat", description="Message type")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Heartbeat timestamp")


# Task status schemas
class TaskStatus(BaseSchema):
    """Task status information."""

    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Task status: pending, running, success, failed")
    progress: Optional[float] = Field(default=None, ge=0, le=100, description="Progress percentage")
    message: Optional[str] = Field(default=None, description="Status message")
    created_at: datetime = Field(..., description="Task creation time")
    started_at: Optional[datetime] = Field(default=None, description="Task start time")
    completed_at: Optional[datetime] = Field(default=None, description="Task completion time")

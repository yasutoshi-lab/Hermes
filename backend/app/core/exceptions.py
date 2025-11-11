"""
Custom exceptions and error handlers for Hermes API.
Provides structured error responses and exception handling.
"""
from typing import Any, Optional, Dict
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


# Custom Exception Classes
class HermesException(Exception):
    """Base exception for Hermes application."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(HermesException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class AuthorizationError(HermesException):
    """Authorization failed - user lacks permission."""

    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class NotFoundError(HermesException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class ValidationError(HermesException):
    """Data validation error."""

    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class DatabaseError(HermesException):
    """Database operation failed."""

    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)


class FileUploadError(HermesException):
    """File upload failed."""

    def __init__(self, message: str = "File upload failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


class TaskExecutionError(HermesException):
    """Task execution failed."""

    def __init__(self, message: str = "Task execution failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)


class OllamaError(HermesException):
    """Ollama API error."""

    def __init__(self, message: str = "LLM service unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, details)


class ExternalServiceError(HermesException):
    """External service (MCP, Container Use) error."""

    def __init__(self, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, details)


# Error Response Formatters
def create_error_response(
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
    error_type: Optional[str] = None
) -> Dict[str, Any]:
    """Create standardized error response."""
    response = {
        "success": False,
        "error": {
            "message": message,
            "type": error_type or "error",
            "code": status_code
        }
    }
    if details:
        response["error"]["details"] = details
    return response


# Exception Handlers
async def hermes_exception_handler(request: Request, exc: HermesException) -> JSONResponse:
    """Handle custom Hermes exceptions."""
    logger.error(
        f"HermesException: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            error_type=exc.__class__.__name__
        )
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.warning(
        f"HTTPException: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            message=str(exc.detail),
            status_code=exc.status_code,
            error_type="HTTPException"
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors."""
    logger.warning(
        f"ValidationError: {exc.errors()}",
        extra={"path": request.url.path}
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            message="Request validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"validation_errors": exc.errors()},
            error_type="ValidationError"
        )
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={"path": request.url.path},
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_type="InternalServerError"
        )
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with FastAPI app."""
    app.add_exception_handler(HermesException, hermes_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

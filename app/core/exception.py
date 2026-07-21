from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from typing import Union
import traceback

# Custom Exception Classes
class AppException(Exception):
    """Base exception for application-specific errors"""
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code or "APP_ERROR"
        super().__init__(self.detail)

class ValidationException(AppException):
    """Exception for validation errors"""
    def __init__(self, detail: str, field: str = None):
        self.field = field
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )

class AuthenticationException(AppException):
    """Exception for authentication errors"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTH_ERROR"
        )

class AuthorizationException(AppException):
    """Exception for authorization errors"""
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="ACCESS_DENIED"
        )

class NotFoundException(AppException):
    """Exception for resource not found"""
    def __init__(self, detail: str = "Resource not found", resource: str = None):
        self.resource = resource
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND"
        )

class ConflictException(AppException):
    """Exception for conflicts (e.g., duplicate entries)"""
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="CONFLICT"
        )

class DatabaseException(AppException):
    """Exception for database errors"""
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR"
        )

# Standardized Error Response Format
def error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    details: Union[dict, list] = None,
    path: str = None
):
    """Generate standardized error response"""
    response = {
        "success": False,
        "status_code": status_code,
        "error": {
            "code": error_code or "ERROR",
            "message": message,
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    if path:
        response["error"]["path"] = path
    
    return response

# Exception Handlers
async def app_exception_handler(request: Request, exc: AppException):
    """Handler for custom application exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            status_code=exc.status_code,
            message=exc.detail,
            error_code=exc.error_code,
            path=request.url.path
        )
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler for FastAPI HTTPException"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            status_code=exc.status_code,
            message=exc.detail,
            error_code="HTTP_ERROR",
            path=request.url.path
        )
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for request validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation error",
            error_code="VALIDATION_ERROR",
            details=errors,
            path=request.url.path
        )
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Handler for unhandled exceptions"""
    # Log the full traceback for debugging
    print("=" * 50)
    print("UNHANDLED EXCEPTION:")
    print(traceback.format_exc())
    print("=" * 50)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details={"error": str(exc)} if __debug__ else None,
            path=request.url.path
        )
    )
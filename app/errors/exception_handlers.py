"""
Exception handlers for the application.

This module provides centralized exception handling for all API endpoints.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette import status
import logging
from typing import Union

from app.core.exceptions import BaseAPIException

logger = logging.getLogger(__name__)


async def base_api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """
    Handle custom API exceptions.
    
    Args:
        request: FastAPI request object
        exc: Custom API exception
        
    Returns:
        JSONResponse: Formatted error response
    """
    logger.error(
        f"API Exception: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.message,
                "details": exc.details,
                "type": exc.__class__.__name__
            }
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTP exceptions.
    
    Args:
        request: FastAPI request object
        exc: HTTP exception
        
    Returns:
        JSONResponse: Formatted error response
    """
    logger.warning(
        f"HTTP Exception: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "type": "HTTPException"
            }
        }
    )


async def not_found_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle 404 Not Found errors.
    
    Args:
        request: FastAPI request object
        exc: Exception object
        
    Returns:
        JSONResponse: 404 error response
    """
    logger.warning(
        f"Resource not found: {request.url.path}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "message": "Resource not found",
                "path": request.url.path,
                "type": "NotFoundError"
            }
        }
    )


async def server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle 500 Internal Server errors.
    
    Args:
        request: FastAPI request object
        exc: Exception object
        
    Returns:
        JSONResponse: 500 error response
    """
    logger.error(
        f"Internal server error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "Internal server error",
                "type": "InternalServerError"
            }
        }
    )


async def validation_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle validation errors.
    
    Args:
        request: FastAPI request object
        exc: Validation exception
        
    Returns:
        JSONResponse: 422 error response
    """
    logger.warning(
        f"Validation error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation error",
                "details": str(exc),
                "type": "ValidationError"
            }
        }
    )

"""
Custom exceptions for the application.

This module defines all custom exceptions used throughout the application
for better error handling and debugging.
"""

from typing import Any, Dict, Optional


class BaseAPIException(Exception):
    """Base exception class for all API-related errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 422, details)


class NotFoundError(BaseAPIException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 404, details)


class ConflictError(BaseAPIException):
    """Raised when there's a conflict with the current state."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 409, details)


class UnauthorizedError(BaseAPIException):
    """Raised when authentication is required or fails."""
    
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 401, details)


class ForbiddenError(BaseAPIException):
    """Raised when access is forbidden."""
    
    def __init__(self, message: str = "Access forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 403, details)


class DatabaseError(BaseAPIException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, details)


class ExternalServiceError(BaseAPIException):
    """Raised when external service calls fail."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 502, details)


class RateLimitError(BaseAPIException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, 429, details)


# Specific business logic exceptions
class EmployeeNotFoundError(NotFoundError):
    """Raised when an employee is not found."""
    
    def __init__(self, employee_id: str):
        super().__init__(
            f"Employee with ID '{employee_id}' not found",
            {"employee_id": employee_id}
        )


class EmployeeAlreadyExistsError(ConflictError):
    """Raised when trying to create an employee that already exists."""
    
    def __init__(self, employee_id: str):
        super().__init__(
            f"Employee with ID '{employee_id}' already exists",
            {"employee_id": employee_id}
        )


class UserNotFoundError(NotFoundError):
    """Raised when a user is not found."""
    
    def __init__(self, username: str):
        super().__init__(
            f"User '{username}' not found",
            {"username": username}
        )


class UserAlreadyExistsError(ConflictError):
    """Raised when trying to create a user that already exists."""
    
    def __init__(self, username: str):
        super().__init__(
            f"User '{username}' already exists",
            {"username": username}
        )


class InvalidCredentialsError(UnauthorizedError):
    """Raised when authentication credentials are invalid."""
    
    def __init__(self):
        super().__init__("Invalid username or password")


class TokenExpiredError(UnauthorizedError):
    """Raised when JWT token has expired."""
    
    def __init__(self):
        super().__init__("Token has expired")


class InvalidTokenError(UnauthorizedError):
    """Raised when JWT token is invalid."""
    
    def __init__(self):
        super().__init__("Invalid token")

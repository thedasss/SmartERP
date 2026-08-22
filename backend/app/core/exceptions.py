"""
Custom exception classes for SmartERP.
These are converted to standard JSON responses in main.py exception handlers.
"""
from typing import Any, Dict, Optional


class SmartERPException(Exception):
    """Base exception for all SmartERP errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(SmartERPException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            status_code=401,
        )


class AuthorizationError(SmartERPException):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED",
            status_code=403,
        )


class NotFoundError(SmartERPException):
    def __init__(self, resource: str, resource_id: Any = None):
        msg = f"{resource} not found"
        if resource_id:
            msg = f"{resource} with ID '{resource_id}' not found"
        super().__init__(
            message=msg,
            error_code=f"{resource.upper().replace(' ', '_')}_NOT_FOUND",
            status_code=404,
        )


class ConflictError(SmartERPException):
    def __init__(self, message: str, error_code: str = "CONFLICT"):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=409,
        )


class ValidationError(SmartERPException):
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=422,
        )


class BusinessRuleError(SmartERPException):
    def __init__(self, message: str, error_code: str = "BUSINESS_RULE_VIOLATION"):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=400,
        )


class RateLimitError(SmartERPException):
    def __init__(self, message: str = "Too many requests"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
        )


class StorageError(SmartERPException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="STORAGE_ERROR",
            status_code=500,
        )

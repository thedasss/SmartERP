"""
Shared Pydantic schema utilities.
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with ORM mode enabled."""
    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20
    search: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: str = "asc"  # "asc" | "desc"


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "OK"
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None

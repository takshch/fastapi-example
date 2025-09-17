from pydantic import BaseModel, Field
from typing import List, TypeVar, Generic, Optional

T = TypeVar('T')

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number", example=1)
    page_size: int = Field(..., description="Number of items per page", example=10)
    total_items: int = Field(..., description="Total number of items", example=25)
    total_pages: int = Field(..., description="Total number of pages", example=3)
    has_next: bool = Field(..., description="Whether there is a next page", example=True)
    has_previous: bool = Field(..., description="Whether there is a previous page", example=False)

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T] = Field(..., description="List of items for current page")
    meta: PaginationMeta = Field(..., description="Pagination metadata")

class PaginationParams(BaseModel):
    """Pagination query parameters"""
    page: int = Field(1, ge=1, description="Page number (starts from 1)", example=1)
    page_size: int = Field(10, ge=1, le=100, description="Number of items per page (max 100)", example=10)

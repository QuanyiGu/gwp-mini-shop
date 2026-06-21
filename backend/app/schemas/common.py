"""通用Schema - TDD GREEN阶段"""
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Any


T = TypeVar('T')


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int = 0


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    details: dict[str, Any] | None = None

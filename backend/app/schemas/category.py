"""商品分类Schema - TDD GREEN阶段"""
from pydantic import BaseModel
from datetime import datetime


class CategoryResponse(BaseModel):
    """分类响应Schema"""
    id: int
    name: str
    icon: str = ''
    sort: int = 0
    created_at: datetime | None = None

    class Config:
        from_attributes = True

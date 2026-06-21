"""Banner配置Schema - TDD GREEN阶段"""
from pydantic import BaseModel
from datetime import datetime


class BannerResponse(BaseModel):
    """Banner响应Schema"""
    id: int
    type: str
    title: str
    content: str
    status: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

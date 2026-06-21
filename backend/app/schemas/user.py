"""用户Schema - TDD GREEN阶段"""
from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    """用户创建Schema"""
    uid: str
    openid: str | None = None
    nickname: str | None = None


class UserUpdate(BaseModel):
    """用户更新Schema"""
    nickname: str | None = None
    avatar_url: str | None = None
    phone: str | None = None


class UserResponse(BaseModel):
    """用户响应Schema"""
    id: int
    uid: str
    openid: str | None = None
    unionid: str | None = None
    nickname: str | None = None
    avatar_url: str = ''
    phone: str = ''
    created_at: datetime

    class Config:
        from_attributes = True

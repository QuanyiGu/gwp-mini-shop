"""商家后台用户Schema - TDD GREEN阶段"""
from pydantic import BaseModel


class AdminLogin(BaseModel):
    """管理员登录Schema"""
    username: str
    password: str


class AdminTokenResponse(BaseModel):
    """管理员Token响应Schema"""
    access_token: str
    refresh_token: str | None = None
    token_type: str = 'bearer'

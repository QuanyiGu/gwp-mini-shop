"""认证相关 Pydantic Schema"""
from typing import Optional

from pydantic import BaseModel, Field


class WxLoginRequest(BaseModel):
    """微信小程序登录请求"""
    code: str = Field(..., description="wx.login 返回的临时登录凭证")
    nickname: Optional[str] = Field(default="", description="昵称（首次登录可携带）")
    avatar_url: Optional[str] = Field(default="", description="头像 URL（首次登录可携带）")


class UserInfoBrief(BaseModel):
    """登录后返回的用户简要信息"""
    uid: str
    nickname: str = ""
    avatar_url: str = ""
    phone: str = ""

    class Config:
        from_attributes = True


class WxLoginData(BaseModel):
    """微信登录成功响应 data"""
    access_token: str
    refresh_token: str
    user_info: UserInfoBrief


class TokenRefreshRequest(BaseModel):
    """刷新 access_token 请求"""
    refresh_token: str = Field(..., description="登录时返回的 refresh_token")


class TokenRefreshData(BaseModel):
    """刷新成功响应 data"""
    access_token: str

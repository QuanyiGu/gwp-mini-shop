"""认证路由 - 微信登录 / Token 刷新"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import (
    TokenRefreshRequest,
    WxLoginRequest,
)
from app.services import auth_service

router = APIRouter()


@router.post("/auth/wxlogin", response_model=dict)
def wx_login(payload: WxLoginRequest, db: Session = Depends(get_db)) -> dict:
    """微信小程序登录

    流程：前端 wx.login 获取 code → 调用本接口 → 后端 code2session 换 openid
    → 查找/创建用户 → 签发 JWT。
    """
    return auth_service.wx_login(
        db=db,
        code=payload.code,
        nickname=payload.nickname or "",
        avatar_url=payload.avatar_url or "",
    )


@router.post("/auth/refresh", response_model=dict)
def refresh_token(payload: TokenRefreshRequest, db: Session = Depends(get_db)) -> dict:
    """刷新 access_token"""
    return auth_service.refresh_access_token(db=db, refresh_token=payload.refresh_token)

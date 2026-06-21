"""微信登录与 Token 管理服务"""
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.user import User
from app.services.user_service import get_or_create_user_by_openid
from app.utils.error_codes import ErrorCode, error_response


class WxLoginError(Exception):
    """微信 code2session 接口返回业务错误"""
    def __init__(self, errcode: int, errmsg: str):
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"[{errcode}] {errmsg}")


def code2session(code: str) -> dict:
    """调用微信 code2session 接口换取 openid/session_key

    Args:
        code: 微信临时登录凭证

    Returns:
        微信返回的 JSON 数据（含 openid, session_key, unionid 等）

    Raises:
        WxLoginError: 微信侧返回 errcode 时
    """
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": settings.WX_APPID,
        "secret": settings.WX_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    resp = httpx.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        raise WxLoginError(errcode=data["errcode"], errmsg=data.get("errmsg", ""))

    return data


def wx_login(
    db: Session,
    code: str,
    nickname: str = "",
    avatar_url: str = "",
) -> dict:
    """微信登录主流程

    1. 校验 code 非空
    2. 调用微信 code2session 换取 openid
    3. 根据 openid 查找或创建用户
    4. 签发 access_token / refresh_token
    5. 返回 data

    Args:
        db: 数据库会话
        code: 微信临时登录凭证
        nickname: 昵称
        avatar_url: 头像 URL

    Returns:
        统一响应格式 {code, message, data}
    """
    if not code:
        return error_response(ErrorCode.PARAM_ERROR)

    try:
        wx_data = code2session(code)
    except WxLoginError:
        return error_response(ErrorCode.SIGN_ERROR)
    except httpx.HTTPStatusError:
        return error_response(ErrorCode.SIGN_ERROR)
    except httpx.TimeoutException:
        return error_response(ErrorCode.SIGN_ERROR)

    openid = wx_data.get("openid", "")
    unionid = wx_data.get("unionid")

    user = get_or_create_user_by_openid(
        db,
        openid=openid,
        unionid=unionid,
        nickname=nickname,
        avatar_url=avatar_url,
    )

    access_token = create_access_token(subject=user.uid)
    refresh_token = create_refresh_token(subject=user.uid)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_info": {
                "uid": user.uid,
                "nickname": user.nickname or "",
                "avatar_url": user.avatar_url or "",
                "phone": user.phone or "",
            },
        },
    }


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    """使用 refresh_token 换取新的 access_token

    Args:
        db: 数据库会话
        refresh_token: 之前签发的 refresh_token

    Returns:
        统一响应格式 {code, message, data}
    """
    payload = decode_token(refresh_token)
    if payload is None:
        return error_response(ErrorCode.TOKEN_EXPIRED)

    if payload.get("type") != "refresh":
        return error_response(ErrorCode.TOKEN_EXPIRED)

    uid = payload.get("sub")
    user = db.query(User).filter(User.uid == uid).first()
    if not user:
        return error_response(ErrorCode.USER_NOT_FOUND)

    new_access = create_access_token(subject=user.uid)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "access_token": new_access,
        },
    }
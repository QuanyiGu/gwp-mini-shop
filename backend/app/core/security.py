"""安全模块 - JWT令牌和密码哈希"""
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, Header, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.utils.error_codes import ErrorCode, ERROR_MESSAGES


def create_access_token(subject: str, expires_delta: Optional[int] = None) -> str:
    """创建access token

    Args:
        subject: 令牌主题（用户标识）
        expires_delta: 过期时间增量（秒），为负数则立即过期
    """
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """创建refresh token

    Args:
        subject: 令牌主题（用户标识）
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """解码JWT令牌

    Args:
        token: JWT令牌字符串

    Returns:
        解码后的payload，失败返回None
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """使用bcrypt哈希密码"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    """FastAPI 依赖：从 Authorization Header 解析当前登录用户

    Args:
        authorization: 形如 "Bearer <access_token>"
        db: 数据库会话

    Returns:
        User 对象

    Raises:
        HTTPException(401): token 不存在/无效/类型错误/用户不存在
    """
    from app.models.user import User  # 局部导入避免循环依赖

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": ErrorCode.TOKEN_EXPIRED,
                "message": ERROR_MESSAGES[ErrorCode.TOKEN_EXPIRED],
            },
        )

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": ErrorCode.TOKEN_EXPIRED,
                "message": ERROR_MESSAGES[ErrorCode.TOKEN_EXPIRED],
            },
        )

    uid = payload.get("sub")
    user = db.query(User).filter(User.uid == uid).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": ErrorCode.USER_NOT_FOUND,
                "message": ERROR_MESSAGES[ErrorCode.USER_NOT_FOUND],
            },
        )

    return user

"""用户服务层"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.utils.error_codes import ErrorCode, error_response
from app.utils.snowflake import generate_uid


def get_user(db: Session, user_id: int) -> dict:
    """获取用户信息"""
    user = db.get(User, user_id)
    if not user:
        return error_response(ErrorCode.USER_NOT_FOUND)
    return {"code": ErrorCode.SUCCESS, "data": user}


def get_user_by_openid(db: Session, openid: str) -> Optional[User]:
    """通过openid查找用户"""
    return db.scalars(select(User).where(User.openid == openid)).first()


def get_user_by_uid(db: Session, uid: str) -> Optional[User]:
    """通过uid查找用户"""
    return db.scalars(select(User).where(User.uid == uid)).first()


def create_user(
    db: Session,
    openid: Optional[str] = None,
    unionid: Optional[str] = None,
    nickname: str = "",
    avatar_url: str = "",
    phone: str = "",
) -> User:
    """创建新用户（微信登录时）"""
    user = User(
        uid=str(generate_uid()),
        openid=openid,
        unionid=unionid,
        nickname=nickname,
        avatar_url=avatar_url,
        phone=phone,
    )
    db.add(user)
    db.flush()
    return user


def get_or_create_user_by_openid(
    db: Session,
    openid: str,
    unionid: Optional[str] = None,
    nickname: str = "",
    avatar_url: str = "",
) -> User:
    """通过openid获取或创建用户"""
    user = get_user_by_openid(db, openid)
    if user:
        return user
    return create_user(
        db=db,
        openid=openid,
        unionid=unionid,
        nickname=nickname,
        avatar_url=avatar_url,
    )


def update_user(
    db: Session,
    user_id: int,
    nickname: Optional[str] = None,
    avatar_url: Optional[str] = None,
    phone: Optional[str] = None,
) -> dict:
    """更新用户信息"""
    user = db.get(User, user_id)
    if not user:
        return error_response(ErrorCode.USER_NOT_FOUND)

    if nickname is not None:
        user.nickname = nickname
    if avatar_url is not None:
        user.avatar_url = avatar_url
    if phone is not None:
        user.phone = phone

    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": user}


def bind_phone(db: Session, user_id: int, phone: str) -> dict:
    """绑定手机号"""
    user = db.get(User, user_id)
    if not user:
        return error_response(ErrorCode.USER_NOT_FOUND)

    user.phone = phone
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": user}

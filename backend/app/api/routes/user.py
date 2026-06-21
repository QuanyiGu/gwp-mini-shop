"""用户路由 - TDD GREEN阶段"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import get_user, update_user
from app.utils.error_codes import ERROR_MESSAGES, ErrorCode

router = APIRouter()


def user_to_response(user: User) -> dict:
    """将用户模型转换为响应字典"""
    return UserResponse.model_validate(user).model_dump()


def service_error_response(result: dict) -> dict:
    """将服务层错误转换为统一响应格式"""
    code = result.get("code", ErrorCode.SERVER_ERROR)
    return {
        "code": code,
        "message": result.get("message", ERROR_MESSAGES.get(code, "未知错误")),
        "data": None,
    }


@router.get("/user/info", response_model=dict)
def get_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取当前用户信息

    Returns:
        统一响应格式，包含当前登录用户信息
    """
    result = get_user(db, current_user.id)
    if result.get("code") != ErrorCode.SUCCESS:
        return service_error_response(result)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": user_to_response(result["data"])
    }


@router.post("/user/update", response_model=dict)
def update_user_info(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """更新当前用户信息

    Args:
        user_data: 用户更新数据

    Returns:
        统一响应格式，包含更新后的用户信息
    """
    result = update_user(
        db=db,
        user_id=current_user.id,
        nickname=user_data.nickname,
        avatar_url=user_data.avatar_url,
        phone=user_data.phone,
    )
    if result.get("code") != ErrorCode.SUCCESS:
        return service_error_response(result)

    db.commit()
    db.refresh(result["data"])

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": user_to_response(result["data"])
    }

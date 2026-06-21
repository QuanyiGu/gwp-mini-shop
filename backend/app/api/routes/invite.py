"""邀请路由 - TDD GREEN阶段"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.utils.error_codes import ErrorCode

router = APIRouter()


@router.post("/invites/generate", response_model=dict)
def generate_invite_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """生成邀请码

    Returns:
        统一响应格式
    """
    from app.models.invite import Invite

    user_id = current_user.id

    # 检查是否已有邀请码
    existing = db.query(Invite).filter(
        Invite.inviter_id == user_id
    ).order_by(Invite.created_at.desc()).first()

    if existing and not existing.coupon_sent:
        # 返回已有未使用的邀请码
        return {
            "code": ErrorCode.SUCCESS,
            "message": "success",
            "data": {
                "invite_code": existing.invite_code,
                "created_at": existing.created_at.isoformat() if existing.created_at else None
            }
        }

    # 创建新的邀请码
    invite_code = f"INVITE_{uuid.uuid4().hex[:8].upper()}"
    invite = Invite(
        inviter_id=user_id,
        invite_code=invite_code
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "invite_code": invite.invite_code,
            "created_at": invite.created_at.isoformat() if invite.created_at else None
        }
    }


@router.get("/invites/history", response_model=dict)
def get_invite_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取邀请记录

    Returns:
        统一响应格式
    """
    from app.models.invite import Invite
    from app.models.user import User

    user_id = current_user.id

    invites = db.query(Invite).filter(
        Invite.inviter_id == user_id
    ).order_by(Invite.created_at.desc()).all()

    result = []
    for invite in invites:
        # 获取被邀请人信息
        invitee = None
        if invite.invitee_id:
            invitee = db.query(User).filter(User.id == invite.invitee_id).first()

        result.append({
            "id": invite.id,
            "invite_code": invite.invite_code,
            "invitee_nickname": invitee.nickname if invitee else None,
            "coupon_sent": invite.coupon_sent == 1,
            "created_at": invite.created_at.isoformat() if invite.created_at else None
        })

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": result
    }

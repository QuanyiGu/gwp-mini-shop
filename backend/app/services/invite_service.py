"""邀请服务层"""
import random
import string
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.invite import Invite
from app.models.user import User
from app.models.coupon import Coupon
from app.utils.error_codes import ErrorCode, error_response


def generate_invite_code(length: int = 8) -> str:
    """生成随机邀请码"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def create_invite_code(db: Session, user_id: int) -> dict:
    """生成邀请码"""
    invite_code = generate_invite_code()
    # 保存到用户关联的邀请记录中（invitee_id=0表示未使用）
    invite = Invite(
        inviter_id=user_id,
        invitee_id=0,
        invite_code=invite_code,
        order_id=0,
        coupon_sent=0,
    )
    db.add(invite)
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": {"invite_code": invite_code}}


def use_invite_code(db: Session, invitee_id: int, invite_code: str) -> dict:
    """使用邀请码（被邀请人下单成功后调用）"""
    # 查找邀请码
    invite = db.scalars(
        select(Invite).where(
            Invite.invite_code == invite_code,
            Invite.invitee_id == 0,  # 未被使用
        ).order_by(Invite.id.desc()).limit(1)
    ).first()

    if not invite:
        return error_response(ErrorCode.NOT_FOUND)

    # 检查不能邀请自己
    if invite.inviter_id == invitee_id:
        return error_response(ErrorCode.PARAM_ERROR)

    # 更新邀请记录
    invite.invitee_id = invitee_id
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": invite}


def link_invite_to_order(db: Session, invite_id: int, order_id: int) -> dict:
    """将邀请记录关联到订单"""
    invite = db.get(Invite, invite_id)
    if not invite:
        return error_response(ErrorCode.NOT_FOUND)

    invite.order_id = order_id
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": invite}


def send_coupon_to_inviter(db: Session, inviter_id: int) -> dict:
    """给邀请人发送优惠券"""
    # 查找最近使用的邀请记录
    invite = db.scalars(
        select(Invite).where(
            Invite.inviter_id == inviter_id,
            Invite.coupon_sent == 0,
        ).order_by(Invite.id.desc()).limit(1)
    ).first()

    if not invite:
        return error_response(ErrorCode.NOT_FOUND)

    # 创建优惠券（假设满100减10）
    from datetime import timedelta
    from app.models.coupon import Coupon
    coupon = Coupon(
        code=f"INVITE{invite.id}",
        user_id=inviter_id,
        discount=10,
        min_amount=100,
        status=0,
        expires_at=invite.created_at + timedelta(days=365),
    )
    db.add(coupon)

    # 标记已发送
    invite.coupon_sent = 1
    db.flush()

    return {"code": ErrorCode.SUCCESS, "data": coupon}


def get_invite_history(db: Session, user_id: int) -> dict:
    """获取邀请记录"""
    invites = db.scalars(
        select(Invite).where(Invite.inviter_id == user_id).order_by(Invite.created_at.desc())
    ).all()

    result = []
    for inv in invites:
        invitee = db.get(User, inv.invitee_id) if inv.invitee_id else None
        result.append({
            "id": inv.id,
            "invite_code": inv.invite_code,
            "invitee_nickname": invitee.nickname if invitee else None,
            "order_id": inv.order_id,
            "coupon_sent": inv.coupon_sent,
            "created_at": inv.created_at,
        })

    return {"code": ErrorCode.SUCCESS, "data": result}

"""优惠券服务层"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models.coupon import Coupon
from app.models.order import Order
from app.utils.error_codes import ErrorCode, error_response
from app.utils.snowflake import generate_order_no


def claim_coupon(db: Session, user_id: int, coupon_code: str) -> dict:
    """领取优惠券"""
    # 查找优惠券
    coupon = db.scalars(
        select(Coupon).where(Coupon.code == coupon_code)
    ).first()

    if not coupon:
        return error_response(ErrorCode.COUPON_NOT_FOUND)

    # 检查是否已过期
    if coupon.expires_at < datetime.utcnow():
        coupon.status = 2  # 已过期
        db.flush()
        return error_response(ErrorCode.COUPON_EXPIRED)

    # 检查是否已被领取且属于其他用户
    if coupon.user_id != 0 and coupon.user_id != user_id:
        return error_response(ErrorCode.COUPON_NOT_FOUND)

    # 已领取过
    if coupon.user_id == user_id:
        return error_response(ErrorCode.COUPON_USED)

    # 领取
    coupon.user_id = user_id
    coupon.status = 0  # 未使用
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": coupon}


def get_user_coupons(db: Session, user_id: int, status: Optional[int] = None) -> dict:
    """获取用户优惠券列表

    status: 0=未使用 1=已使用 2=已过期
    """
    query = select(Coupon).where(Coupon.user_id == user_id)
    if status is not None:
        query = query.where(Coupon.status == status)
    coupons = db.scalars(query.order_by(Coupon.created_at.desc())).all()
    return {"code": ErrorCode.SUCCESS, "data": coupons}


def get_applicable_coupons(db: Session, user_id: int, total_amount: Decimal) -> dict:
    """查询可用优惠券（订单金额满足条件的未使用优惠券）"""
    now = datetime.utcnow()
    coupons = db.scalars(
        select(Coupon).where(
            and_(
                Coupon.user_id == user_id,
                Coupon.status == 0,
                Coupon.expires_at > now,
                Coupon.min_amount <= total_amount,
            )
        ).order_by(Coupon.discount.desc())
    ).all()
    return {"code": ErrorCode.SUCCESS, "data": coupons}


def use_coupon(db: Session, coupon_id: int, user_id: int) -> dict:
    """使用优惠券（标记为已使用）"""
    coupon = db.get(Coupon, coupon_id)
    if not coupon or coupon.user_id != user_id:
        return error_response(ErrorCode.COUPON_NOT_FOUND)
    if coupon.status != 0:
        return error_response(ErrorCode.COUPON_USED)
    if coupon.expires_at < datetime.utcnow():
        coupon.status = 2
        db.flush()
        return error_response(ErrorCode.COUPON_EXPIRED)

    coupon.status = 1
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": coupon}


def return_coupon(db: Session, coupon_id: int, user_id: int) -> dict:
    """退回优惠券（订单取消时）"""
    coupon = db.get(Coupon, coupon_id)
    if not coupon or coupon.user_id != user_id:
        return error_response(ErrorCode.COUPON_NOT_FOUND)

    # 只有已使用的优惠券才能退回
    if coupon.status == 1:
        coupon.status = 0
        db.flush()
    return {"code": ErrorCode.SUCCESS, "data": coupon}


def create_coupon(
    db: Session,
    code: str,
    discount: Decimal,
    min_amount: Decimal,
    user_id: int = 0,
    expires_at=None,
) -> dict:
    """创建优惠券（后台创建）"""
    if expires_at is None:
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(days=30)

    coupon = Coupon(
        code=code,
        user_id=user_id,
        discount=discount,
        min_amount=min_amount,
        status=0,
        expires_at=expires_at,
    )
    db.add(coupon)
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": coupon}

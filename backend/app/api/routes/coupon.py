"""优惠券路由 - TDD GREEN阶段"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.coupon import CouponResponse
from app.utils.error_codes import ErrorCode

router = APIRouter()


def coupon_to_response(coupon) -> dict:
    """将优惠券模型转换为响应字典"""
    data = CouponResponse.model_validate(coupon).model_dump()
    data['discount'] = str(data['discount'])
    data['min_amount'] = str(data['min_amount'])
    return data


@router.post("/coupons/claim", response_model=dict)
def claim_coupon(
    invite_code: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """通过邀请码领取优惠券

    Args:
        invite_code: 邀请码

    Returns:
        统一响应格式
    """
    from app.models.coupon import Coupon
    from app.models.invite import Invite

    user_id = current_user.id

    # 查找邀请记录
    if invite_code:
        invite = db.query(Invite).filter(
            Invite.invite_code == invite_code
        ).first()

        if not invite:
            return {
                "code": ErrorCode.NOT_FOUND,
                "message": "邀请码无效",
                "data": None
            }

        # 检查是否已经领取过
        existing = db.query(Coupon).filter(
            Coupon.user_id == user_id,
            Coupon.code.startswith('INVITE_')
        ).first()

        if existing:
            return {
                "code": ErrorCode.COUPON_USED,
                "message": "您已经领取过邀请优惠券",
                "data": None
            }

        # 创建优惠券
        coupon = Coupon(
            code=f"INVITE_{uuid.uuid4().hex[:16]}",
            user_id=user_id,
            type=1,  # 满减券
            discount=Decimal('10.00'),
            min_amount=Decimal('39.00'),
            status=0,  # 未使用
            expires_at=datetime.utcnow().replace(year=datetime.utcnow().year + 1)
        )
        db.add(coupon)
        db.commit()
        db.refresh(coupon)

        return {
            "code": ErrorCode.SUCCESS,
            "message": "success",
            "data": coupon_to_response(coupon)
        }

    return {
        "code": ErrorCode.PARAM_ERROR,
        "message": "邀请码不能为空",
        "data": None
    }


@router.get("/coupons", response_model=dict)
def get_my_coupons(
    status: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取我的优惠券列表

    Args:
        status: 优惠券状态（0=未使用, 1=已使用, 2=已过期）

    Returns:
        统一响应格式
    """
    from app.models.coupon import Coupon

    user_id = current_user.id

    query = db.query(Coupon).filter(Coupon.user_id == user_id)

    if status is not None:
        query = query.filter(Coupon.status == status)

    coupons = query.order_by(Coupon.created_at.desc()).all()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": [coupon_to_response(c) for c in coupons]
    }


@router.get("/coupons/apply", response_model=dict)
def apply_coupons(
    order_amount: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """查询可用优惠券

    Args:
        order_amount: 订单金额

    Returns:
        统一响应格式
    """
    from app.models.coupon import Coupon

    user_id = current_user.id
    now = datetime.utcnow()

    # 查询可用的优惠券
    coupons = db.query(Coupon).filter(
        Coupon.user_id == user_id,
        Coupon.status == 0,
        Coupon.expires_at > now,
        Coupon.min_amount <= Decimal(str(order_amount))
    ).all()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": [coupon_to_response(c) for c in coupons]
    }

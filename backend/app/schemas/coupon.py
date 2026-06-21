"""优惠券Schema - TDD GREEN阶段"""
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class CouponResponse(BaseModel):
    """优惠券响应Schema"""
    id: int
    code: str
    user_id: int
    type: int
    discount: Decimal
    min_amount: Decimal
    status: int
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

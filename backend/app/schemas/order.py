"""订单Schema - TDD GREEN阶段"""
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class OrderCreate(BaseModel):
    """订单创建Schema"""
    address_id: int
    items: list[dict] = []  # [{"product_id": 1, "quantity": 2}]
    coupon_id: int | None = None


class OrderResponse(BaseModel):
    """订单响应Schema"""
    id: int
    user_id: int
    order_no: str
    total_amount: Decimal
    discount_amount: Decimal = Decimal('0')
    pay_amount: Decimal
    pay_time: datetime | None = None
    status: int
    items: list[dict] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

"""购物车Schema - TDD GREEN阶段"""
from pydantic import BaseModel
from datetime import datetime


class CartItemCreate(BaseModel):
    """购物车商品创建Schema"""
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    """购物车商品更新Schema"""
    quantity: int


class CartItemResponse(BaseModel):
    """购物车商品响应Schema"""
    id: int
    user_id: int
    product_id: int
    quantity: int
    selected: int = 1
    created_at: datetime

    class Config:
        from_attributes = True

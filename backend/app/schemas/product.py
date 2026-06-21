"""商品Schema - TDD GREEN阶段"""
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class ProductCreate(BaseModel):
    """商品创建Schema"""
    category_id: int
    name: str
    main_image: str
    price: Decimal
    original_price: Decimal
    stock: int
    images: list[str] = []
    description: str = ''
    status: int = 1


class ProductUpdate(BaseModel):
    """商品更新Schema"""
    category_id: int | None = None
    name: str | None = None
    main_image: str | None = None
    images: list[str] | None = None
    description: str | None = None
    price: Decimal | None = None
    original_price: Decimal | None = None
    stock: int | None = None
    status: int | None = None


class ProductResponse(BaseModel):
    """商品响应Schema"""
    id: int
    category_id: int
    name: str
    main_image: str
    images: list[str] = []
    description: str = ''
    price: Decimal
    original_price: Decimal
    stock: int
    sales: int
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

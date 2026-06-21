"""收货地址Schema - TDD GREEN阶段"""
from pydantic import BaseModel
from datetime import datetime


class AddressCreate(BaseModel):
    """收货地址创建Schema"""
    name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: int = 0


class AddressUpdate(BaseModel):
    """收货地址更新Schema"""
    name: str | None = None
    phone: str | None = None
    province: str | None = None
    city: str | None = None
    district: str | None = None
    detail: str | None = None
    is_default: int | None = None


class AddressResponse(BaseModel):
    """收货地址响应Schema"""
    id: int
    user_id: int
    name: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True

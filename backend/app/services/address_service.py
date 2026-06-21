"""收货地址服务层"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.address import Address
from app.utils.error_codes import ErrorCode, error_response


def get_addresses(db: Session, user_id: int) -> dict:
    """获取用户收货地址列表"""
    query = select(Address).where(Address.user_id == user_id).order_by(Address.is_default.desc(), Address.id.desc())
    addresses = db.scalars(query).all()
    return {"code": ErrorCode.SUCCESS, "data": addresses}


def get_address(db: Session, address_id: int, user_id: int) -> dict:
    """获取单个收货地址"""
    address = db.get(Address, address_id)
    if not address or address.user_id != user_id:
        return error_response(ErrorCode.NOT_FOUND)
    return {"code": ErrorCode.SUCCESS, "data": address}


def create_address(
    db: Session,
    user_id: int,
    name: str,
    phone: str,
    province: str,
    city: str,
    district: str,
    detail: str,
    is_default: int = 0,
) -> dict:
    """创建收货地址"""
    # 如果设为默认，先取消其他默认地址
    if is_default == 1:
        db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_default == 1
        ).update({"is_default": 0})

    address = Address(
        user_id=user_id,
        name=name,
        phone=phone,
        province=province,
        city=city,
        district=district,
        detail=detail,
        is_default=is_default,
    )
    db.add(address)
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": address}


def update_address(
    db: Session,
    address_id: int,
    user_id: int,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    province: Optional[str] = None,
    city: Optional[str] = None,
    district: Optional[str] = None,
    detail: Optional[str] = None,
    is_default: Optional[int] = None,
) -> dict:
    """更新收货地址"""
    address = db.get(Address, address_id)
    if not address or address.user_id != user_id:
        return error_response(ErrorCode.NOT_FOUND)

    # 如果设为默认，先取消其他默认地址
    if is_default == 1:
        db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_default == 1,
            Address.id != address_id
        ).update({"is_default": 0})

    # 更新字段
    update_data = {
        "name": name,
        "phone": phone,
        "province": province,
        "city": city,
        "district": district,
        "detail": detail,
        "is_default": is_default,
    }
    for key, value in update_data.items():
        if value is not None and hasattr(address, key):
            setattr(address, key, value)

    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": address}


def delete_address(db: Session, address_id: int, user_id: int) -> dict:
    """删除收货地址"""
    address = db.get(Address, address_id)
    if not address or address.user_id != user_id:
        return error_response(ErrorCode.NOT_FOUND)

    db.delete(address)
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": None}


def set_default_address(db: Session, address_id: int, user_id: int) -> dict:
    """设为默认收货地址"""
    address = db.get(Address, address_id)
    if not address or address.user_id != user_id:
        return error_response(ErrorCode.NOT_FOUND)

    # 取消其他默认地址
    db.query(Address).filter(
        Address.user_id == user_id,
        Address.is_default == 1
    ).update({"is_default": 0})

    address.is_default = 1
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": address}

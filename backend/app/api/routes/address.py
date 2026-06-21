"""收货地址路由 - TDD GREEN阶段"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
from app.utils.error_codes import ErrorCode

router = APIRouter()


def address_to_response(address) -> dict:
    """将地址模型转换为响应字典"""
    return AddressResponse.model_validate(address).model_dump()


@router.get("/addresses", response_model=dict)
def get_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取收货地址列表

    Returns:
        统一响应格式
    """
    from app.models.address import Address

    user_id = current_user.id
    addresses = db.query(Address).filter(Address.user_id == user_id).all()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": [address_to_response(addr) for addr in addresses]
    }


@router.get("/addresses/default", response_model=dict)
def get_default_address(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取当前用户默认地址；无默认则返回第一个地址"""
    from app.models.address import Address

    user_id = current_user.id
    address = db.query(Address).filter(
        Address.user_id == user_id,
        Address.is_default == 1
    ).first()

    if not address:
        address = db.query(Address).filter(
            Address.user_id == user_id
        ).order_by(Address.id.asc()).first()

    if not address:
        return {
            "code": ErrorCode.NOT_FOUND,
            "message": "未找到地址",
            "data": None
        }

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": address_to_response(address)
    }


@router.post("/addresses", response_model=dict)
def create_address(
    address_data: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """添加收货地址

    Args:
        address_data: 地址数据

    Returns:
        统一响应格式
    """
    from app.models.address import Address

    user_id = current_user.id

    # 如果设为默认，先取消其他默认
    if address_data.is_default == 1:
        db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_default == 1
        ).update({Address.is_default: 0})

    address = Address(
        user_id=user_id,
        name=address_data.name,
        phone=address_data.phone,
        province=address_data.province,
        city=address_data.city,
        district=address_data.district,
        detail=address_data.detail,
        is_default=address_data.is_default
    )
    db.add(address)
    db.commit()
    db.refresh(address)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": address_to_response(address)
    }


@router.put("/addresses/{address_id}", response_model=dict)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """更新收货地址

    Args:
        address_id: 地址ID
        address_data: 更新数据

    Returns:
        统一响应格式
    """
    from app.models.address import Address

    user_id = current_user.id

    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id
    ).first()

    if not address:
        return {
            "code": ErrorCode.NOT_FOUND,
            "message": "地址不存在",
            "data": None
        }

    # 如果设为默认，先取消其他默认
    if address_data.is_default == 1:
        db.query(Address).filter(
            Address.user_id == user_id,
            Address.is_default == 1,
            Address.id != address_id
        ).update({Address.is_default: 0})

    # 更新字段
    update_data = address_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(address, key, value)

    db.commit()
    db.refresh(address)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": address_to_response(address)
    }


@router.delete("/addresses/{address_id}", response_model=dict)
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """删除收货地址

    Args:
        address_id: 地址ID

    Returns:
        统一响应格式
    """
    from app.models.address import Address

    user_id = current_user.id

    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id
    ).first()

    if not address:
        return {
            "code": ErrorCode.NOT_FOUND,
            "message": "地址不存在",
            "data": None
        }

    db.delete(address)
    db.commit()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": None
    }


@router.put("/addresses/{address_id}/default", response_model=dict)
def set_default_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """设为默认地址

    Args:
        address_id: 地址ID

    Returns:
        统一响应格式
    """
    from app.models.address import Address

    user_id = current_user.id

    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id
    ).first()

    if not address:
        return {
            "code": ErrorCode.NOT_FOUND,
            "message": "地址不存在",
            "data": None
        }

    # 取消其他默认
    db.query(Address).filter(
        Address.user_id == user_id,
        Address.is_default == 1
    ).update({Address.is_default: 0})

    # 设为默认
    address.is_default = 1
    db.commit()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": address_to_response(address)
    }

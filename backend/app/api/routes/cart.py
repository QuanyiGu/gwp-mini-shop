"""购物车路由 - TDD GREEN阶段"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse
from app.utils.error_codes import ErrorCode

router = APIRouter()


def cart_item_to_response(item) -> dict:
    """将购物车项转换为响应字典"""
    data = CartItemResponse.model_validate(item).model_dump()
    # 包含商品信息
    if item.product:
        data['product'] = {
            'id': item.product.id,
            'name': item.product.name,
            'main_image': item.product.main_image,
            'price': str(item.product.price),
            'stock': item.product.stock,
            'status': item.product.status
        }
    return data


@router.post("/cart/select-all", response_model=dict)
def select_all_cart_items(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """购物车全选/取消全选

    Args:
        payload: {"selected": true/false}

    Returns:
        统一响应格式，包含更新后的购物车商品列表
    """
    from app.models.cart_item import CartItem

    selected = 1 if payload.get("selected") else 0
    user_id = current_user.id

    db.query(CartItem).filter(CartItem.user_id == user_id).update(
        {CartItem.selected: selected}
    )
    db.commit()

    items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "list": [cart_item_to_response(item) for item in items],
            "total": len(items)
        }
    }


@router.get("/cart", response_model=dict)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取购物车列表

    Returns:
        统一响应格式，包含购物车商品列表
    """
    from app.models.cart_item import CartItem

    user_id = current_user.id
    items = db.query(CartItem).filter(CartItem.user_id == user_id).all()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "list": [cart_item_to_response(item) for item in items],
            "total": len(items)
        }
    }


@router.post("/cart", response_model=dict)
def add_to_cart(
    item: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """添加商品到购物车

    Args:
        item: 购物车商品数据

    Returns:
        统一响应格式
    """
    from app.models.cart_item import CartItem
    from app.models.product import Product

    user_id = current_user.id

    # 检查商品是否存在
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        return {
            "code": ErrorCode.NOT_FOUND,
            "message": "商品不存在",
            "data": None
        }

    if product.status != 1:
        return {
            "code": ErrorCode.STOCK_NOT_ENOUGH,
            "message": "商品已下架",
            "data": None
        }

    # 检查购物车中是否已有该商品
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.product_id == item.product_id
    ).first()

    if existing_item:
        # 叠加数量
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        return {
            "code": ErrorCode.SUCCESS,
            "message": "success",
            "data": cart_item_to_response(existing_item)
        }

    # 创建新购物车项
    new_item = CartItem(
        user_id=user_id,
        product_id=item.product_id,
        quantity=item.quantity
    )
    db.add(new_item)

    try:
        db.commit()
        db.refresh(new_item)
    except IntegrityError:
        db.rollback()
        return {
            "code": ErrorCode.PARAM_ERROR,
            "message": "添加购物车失败",
            "data": None
        }

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": cart_item_to_response(new_item)
    }


@router.put("/cart/{item_id}", response_model=dict)
def update_cart_item(
    item_id: int,
    item: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """更新购物车商品数量

    Args:
        item_id: 购物车项ID
        item: 更新数据

    Returns:
        统一响应格式
    """
    from app.models.cart_item import CartItem

    user_id = current_user.id

    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == user_id
    ).first()

    if not cart_item:
        return {
            "code": ErrorCode.NOT_FOUND,
            "message": "购物车项不存在",
            "data": None
        }

    if item.quantity <= 0:
        # 数量为0时删除
        db.delete(cart_item)
        db.commit()
        return {
            "code": ErrorCode.SUCCESS,
            "message": "success",
            "data": None
        }

    cart_item.quantity = item.quantity
    db.commit()
    db.refresh(cart_item)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": cart_item_to_response(cart_item)
    }


@router.delete("/cart/{item_id}", response_model=dict)
def delete_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """删除购物车商品

    Args:
        item_id: 购物车项ID

    Returns:
        统一响应格式
    """
    from app.models.cart_item import CartItem

    user_id = current_user.id

    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.user_id == user_id
    ).first()

    if not cart_item:
        return {
            "code": ErrorCode.NOT_FOUND,
            "message": "购物车项不存在",
            "data": None
        }

    db.delete(cart_item)
    db.commit()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": None
    }

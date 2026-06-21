"""购物车服务层"""
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.models.cart_item import CartItem
from app.models.product import Product
from app.utils.error_codes import ErrorCode, error_response


def get_cart_items(db: Session, user_id: int) -> dict:
    """获取用户购物车列表"""
    query = select(CartItem).where(CartItem.user_id == user_id)
    items = db.scalars(query).all()
    return {"code": ErrorCode.SUCCESS, "data": items}


def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int = 1) -> dict:
    """添加商品到购物车

    如果商品已在购物车中，则增加数量；否则新增条目
    """
    # 校验商品是否存在且上架
    product = db.get(Product, product_id)
    if not product:
        return error_response(ErrorCode.NOT_FOUND)
    if product.status != 1:
        return error_response(ErrorCode.PARAM_ERROR)

    # 检查购物车中是否已有该商品
    query = select(CartItem).where(
        and_(CartItem.user_id == user_id, CartItem.product_id == product_id)
    )
    existing_item = db.scalars(query).first()

    if existing_item:
        # 已存在，增加数量
        new_quantity = existing_item.quantity + quantity
        if product.stock < new_quantity:
            return error_response(ErrorCode.STOCK_NOT_ENOUGH)
        existing_item.quantity = new_quantity
        db.flush()
        return {"code": ErrorCode.SUCCESS, "data": existing_item}
    else:
        # 新增
        if product.stock < quantity:
            return error_response(ErrorCode.STOCK_NOT_ENOUGH)
        new_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            selected=1,
        )
        db.add(new_item)
        db.flush()
        return {"code": ErrorCode.SUCCESS, "data": new_item}


def update_cart_item(db: Session, cart_id: int, user_id: int, quantity: int, selected: Optional[int] = None) -> dict:
    """更新购物车商品数量"""
    cart_item = db.get(CartItem, cart_id)
    if not cart_item or cart_item.user_id != user_id:
        return error_response(ErrorCode.NOT_FOUND)

    if quantity <= 0:
        # 数量为0或负数时删除
        db.delete(cart_item)
        db.flush()
        return {"code": ErrorCode.SUCCESS, "data": None}

    # 检查库存
    product = db.get(Product, cart_item.product_id)
    if not product or product.stock < quantity:
        return error_response(ErrorCode.STOCK_NOT_ENOUGH)

    cart_item.quantity = quantity
    if selected is not None:
        cart_item.selected = selected
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": cart_item}


def remove_cart_item(db: Session, cart_id: int, user_id: int) -> dict:
    """删除购物车商品"""
    cart_item = db.get(CartItem, cart_id)
    if not cart_item or cart_item.user_id != user_id:
        return error_response(ErrorCode.NOT_FOUND)

    db.delete(cart_item)
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": None}


def clear_cart(db: Session, user_id: int) -> dict:
    """清空购物车"""
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": None}


def get_selected_items(db: Session, user_id: int) -> list[CartItem]:
    """获取已选中的购物车商品（用于结算）"""
    query = select(CartItem).where(
        and_(CartItem.user_id == user_id, CartItem.selected == 1)
    )
    return db.scalars(query).all()

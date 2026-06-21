"""订单服务层"""
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.address import Address
from app.models.coupon import Coupon
from app.utils.error_codes import ErrorCode, error_response
from app.utils.snowflake import generate_order_no


def create_order(
    db: Session,
    user_id: int,
    address_id: int,
    items: list[dict],
    coupon_id: Optional[int] = None,
    gift_package: int = 0,
    greeting_card: str = "",
) -> dict:
    """创建订单

    items: [{"product_id": int, "quantity": int}, ...]
    """
    # 1. 校验收货地址
    address = db.get(Address, address_id)
    if not address or address.user_id != user_id:
        return error_response(ErrorCode.NOT_FOUND)

    # 2. 校验商品 & 计算金额
    order_items = []
    total_amount = Decimal("0")

    for item in items:
        product = db.get(Product, item["product_id"])
        if not product:
            return error_response(ErrorCode.NOT_FOUND)
        if product.stock < item["quantity"]:
            return error_response(ErrorCode.STOCK_NOT_ENOUGH)

        subtotal = product.price * item["quantity"]
        total_amount += subtotal
        order_items.append((product, item["quantity"], subtotal))

    # 3. 扣减库存（原子操作）
    for product, quantity, _ in order_items:
        product.stock -= quantity

    # 4. 优惠券
    pay_amount = total_amount
    coupon = None
    if coupon_id is not None:
        coupon = db.get(Coupon, coupon_id)
        if not coupon or coupon.user_id != user_id:
            return error_response(ErrorCode.COUPON_NOT_FOUND)
        if coupon.status != 0:
            return error_response(ErrorCode.COUPON_USED)
        if coupon.expires_at and coupon.expires_at < __import__("datetime").datetime.utcnow():
            return error_response(ErrorCode.COUPON_EXPIRED)
        if total_amount < coupon.min_amount:
            return error_response(ErrorCode.COUPON_CONDITION_NOT_MET)

        pay_amount = total_amount - coupon.discount
        if pay_amount < 0:
            pay_amount = Decimal("0")
        coupon.status = 1  # 标记已使用

    # 5. 创建订单
    order = Order(
        order_no=str(generate_order_no()),
        user_id=user_id,
        total_amount=total_amount,
        pay_amount=pay_amount,
        discount_amount=total_amount - pay_amount,
        address_name=address.name,
        address_phone=address.phone,
        address_detail=f"{address.province}{address.city}{address.district}{address.detail}",
        status=Order.STATUS_PENDING,
        gift_package=gift_package,
        greeting_card=greeting_card,
    )
    db.add(order)
    db.flush()

    # 6. 创建订单商品
    for product, quantity, subtotal in order_items:
        oi = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_image=product.main_image,
            price=product.price,
            quantity=quantity,
            total_price=subtotal,
        )
        db.add(oi)

    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": order}


def cancel_order(db: Session, order_id: int, user_id: int) -> dict:
    """取消订单（仅限待付款状态）"""
    order = db.get(Order, order_id)
    if not order or order.user_id != user_id:
        return error_response(ErrorCode.NOT_FOUND)
    if order.status != Order.STATUS_PENDING:
        return error_response(ErrorCode.ORDER_STATUS_ERROR)

    # 1. 回滚库存
    for item in order.items:
        product = db.get(Product, item.product_id)
        if product:
            product.stock += item.quantity

    # 2. 退回优惠券（查找该用户最近使用的优惠券退回）
    # NOTE: Order模型无coupon_id字段，通过用户最近已使用优惠券退回
    used_coupon = db.scalar(
        select(Coupon).where(
            Coupon.user_id == user_id,
            Coupon.status == 1,
        ).order_by(Coupon.created_at.desc()).limit(1)
    )
    if used_coupon:
        used_coupon.status = 0

    # 3. 更新订单状态
    order.status = Order.STATUS_CANCELLED
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": order}

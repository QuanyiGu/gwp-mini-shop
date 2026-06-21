"""订单路由 - TDD GREEN阶段"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from decimal import Decimal

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse
from app.utils.error_codes import ErrorCode
from app.utils.snowflake import generate_order_no as snowflake

router = APIRouter()


def order_to_response(order, include_items=False) -> dict:
    """将订单模型转换为响应字典"""
    data = {
        "id": order.id,
        "order_no": order.order_no,
        "user_id": order.user_id,
        "total_amount": str(order.total_amount),
        "pay_amount": str(order.pay_amount),
        "discount_amount": str(getattr(order, 'discount_amount', Decimal('0'))),
        "address_name": order.address_name,
        "address_phone": order.address_phone,
        "address_detail": order.address_detail,
        "status": order.status,
        "gift_package": getattr(order, 'gift_package', 0),
        "greeting_card": getattr(order, 'greeting_card', ''),
        "tracking_node": getattr(order, 'tracking_node', 0),
        "logistics_company": getattr(order, 'logistics_company', ''),
        "logistics_no": getattr(order, 'logistics_no', ''),
        "pay_time": order.pay_time.isoformat() if order.pay_time else None,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
    }

    if include_items and hasattr(order, 'items'):
        data['items'] = [{
            'id': item.id,
            'product_id': item.product_id,
            'product_name': item.product_name,
            'product_image': item.product_image,
            'price': str(item.price),
            'quantity': item.quantity,
            'total_price': str(item.total_price)
        } for item in order.items]

    return data


@router.post("/orders", response_model=dict)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """创建订单

    Args:
        order_data: 订单数据

    Returns:
        统一响应格式
    """
    from app.models.order import Order
    from app.models.order_item import OrderItem
    from app.models.product import Product
    from app.models.address import Address
    from app.models.cart_item import CartItem

    user_id = current_user.id

    # 获取收货地址
    address = db.query(Address).filter(
        Address.id == order_data.address_id,
        Address.user_id == user_id
    ).first()

    if not address:
        return {
            "code": ErrorCode.NOT_FOUND,
            "message": "收货地址不存在",
            "data": None
        }

    # 计算订单金额
    total_amount = Decimal('0')
    order_items = []

    # 从items计算
    for item_data in order_data.items:
        product = db.query(Product).filter(Product.id == item_data['product_id']).first()
        if not product:
            return {
                "code": ErrorCode.NOT_FOUND,
                "message": f"商品ID {item_data['product_id']} 不存在",
                "data": None
            }

        if product.stock < item_data['quantity']:
            return {
                "code": ErrorCode.STOCK_NOT_ENOUGH,
                "message": f"商品 {product.name} 库存不足",
                "data": None
            }

        item_total = product.price * item_data['quantity']
        total_amount += item_total

        order_items.append({
            'product': product,
            'quantity': item_data['quantity'],
            'price': product.price,
            'total': item_total
        })

    # 计算优惠
    discount_amount = Decimal('0')
    pay_amount = total_amount

    # 应用优惠券
    if order_data.coupon_id:
        from app.models.coupon import Coupon
        coupon = db.query(Coupon).filter(
            Coupon.id == order_data.coupon_id,
            Coupon.user_id == user_id,
            Coupon.status == 0  # 未使用
        ).first()

        if not coupon:
            return {
                "code": ErrorCode.COUPON_NOT_FOUND,
                "message": "优惠券不存在或不可用",
                "data": None
            }

        if coupon.expires_at < datetime.utcnow():
            return {
                "code": ErrorCode.COUPON_EXPIRED,
                "message": "优惠券已过期",
                "data": None
            }

        if total_amount < coupon.min_amount:
            return {
                "code": ErrorCode.COUPON_CONDITION_NOT_MET,
                "message": f"订单金额未达到优惠券使用条件（满{coupon.min_amount}元）",
                "data": None
            }

        discount_amount = coupon.discount
        pay_amount = total_amount - discount_amount

        # 标记优惠券已使用
        coupon.status = 1

    # 生成订单号
    order_no = str(snowflake())

    # 创建订单
    order = Order(
        order_no=order_no,
        user_id=user_id,
        total_amount=total_amount,
        discount_amount=discount_amount,
        pay_amount=pay_amount,
        address_name=address.name,
        address_phone=address.phone,
        address_detail=f"{address.province}{address.city}{address.district}{address.detail}",
        status=0  # 待付款
    )
    db.add(order)
    db.flush()

    # 创建订单项
    for item in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product'].id,
            product_name=item['product'].name,
            product_image=item['product'].main_image,
            price=item['price'],
            quantity=item['quantity'],
            total_price=item['total']
        )
        db.add(order_item)

        # 冻结库存（乐观锁）
        result = db.query(Product).filter(
            Product.id == item['product'].id,
            Product.stock >= item['quantity']
        ).update({
            Product.stock: Product.stock - item['quantity']
        })

        if result == 0:
            db.rollback()
            return {
                "code": ErrorCode.STOCK_NOT_ENOUGH,
                "message": f"商品 {item['product'].name} 库存不足",
                "data": None
            }

    # 删除已结算的购物车商品
    for item_data in order_data.items:
        db.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.product_id == item_data['product_id']
        ).delete()

    db.commit()
    db.refresh(order)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": order_to_response(order)
    }


@router.get("/orders", response_model=dict)
def get_orders(
    status: int = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取订单列表

    Args:
        status: 订单状态（可选）
        page: 页码
        page_size: 每页数量

    Returns:
        统一响应格式
    """
    from app.models.order import Order

    user_id = current_user.id

    query = db.query(Order).filter(Order.user_id == user_id)

    if status is not None:
        query = query.filter(Order.status == status)

    total = query.count()
    offset = (page - 1) * page_size
    orders = query.order_by(Order.created_at.desc()).offset(offset).limit(page_size).all()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "list": [order_to_response(order, include_items=True) for order in orders],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    }


@router.get("/orders/{order_id}", response_model=dict)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """获取订单详情

    Args:
        order_id: 订单ID

    Returns:
        统一响应格式
    """
    from app.models.order import Order

    user_id = current_user.id

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()

    if not order:
        return {
            "code": ErrorCode.ORDER_NOT_FOUND,
            "message": "订单不存在",
            "data": None
        }

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": order_to_response(order, include_items=True)
    }


@router.post("/orders/{order_id}/pay", response_model=dict)
def pay_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """发起订单支付

    Args:
        order_id: 订单ID

    Returns:
        统一响应格式，包含支付参数
    """
    from app.models.order import Order

    user_id = current_user.id

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()

    if not order:
        return {
            "code": ErrorCode.ORDER_NOT_FOUND,
            "message": "订单不存在",
            "data": None
        }

    if order.status != 0:
        return {
            "code": ErrorCode.ORDER_STATUS_ERROR,
            "message": "订单状态不允许支付",
            "data": None
        }

    # TODO: 调用微信支付API获取预支付订单
    # 这里返回模拟的支付参数
    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "order_no": order.order_no,
            "pay_amount": str(order.pay_amount),
            "pay_url": f"/pages/order/pay?order_no={order.order_no}"
        }
    }


@router.post("/orders/{order_no}/cancel", response_model=dict)
def cancel_order(
    order_no: str,
    payload: dict | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """取消待付款订单，回滚库存并退回优惠券"""
    from app.models.order import Order
    from app.models.product import Product
    from app.models.coupon import Coupon

    user_id = current_user.id
    order = db.query(Order).filter(
        Order.order_no == order_no,
        Order.user_id == user_id
    ).first()

    if not order:
        return {
            "code": ErrorCode.ORDER_NOT_FOUND,
            "message": "订单不存在",
            "data": None
        }

    if order.status != Order.STATUS_PENDING:
        return {
            "code": ErrorCode.ORDER_STATUS_ERROR,
            "message": "订单状态不允许取消",
            "data": None
        }

    for item in order.items:
        db.query(Product).filter(Product.id == item.product_id).update({
            Product.stock: Product.stock + item.quantity
        })

    returned_coupon = None
    if getattr(order, 'discount_amount', Decimal('0')) and order.discount_amount > 0:
        coupon = db.query(Coupon).filter(
            Coupon.user_id == user_id,
            Coupon.status == 1,
            Coupon.discount == order.discount_amount
        ).order_by(Coupon.created_at.desc()).first()
        if coupon:
            coupon.status = 0
            returned_coupon = {
                "id": coupon.id,
                "code": coupon.code,
                "status": coupon.status
            }

    order.status = Order.STATUS_CANCELLED
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)

    data = order_to_response(order, include_items=True)
    data["returned_coupon"] = returned_coupon
    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": data
    }


@router.post("/orders/{order_no}/confirm", response_model=dict)
def confirm_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """确认收货：已发货订单变更为已完成"""
    from app.models.order import Order

    user_id = current_user.id
    order = db.query(Order).filter(
        Order.order_no == order_no,
        Order.user_id == user_id
    ).first()

    if not order:
        return {
            "code": ErrorCode.ORDER_NOT_FOUND,
            "message": "订单不存在",
            "data": None
        }

    if order.status != Order.STATUS_SHIPPED:
        return {
            "code": ErrorCode.ORDER_STATUS_ERROR,
            "message": "订单状态不允许确认收货",
            "data": None
        }

    order.status = Order.STATUS_COMPLETED
    order.pay_time = datetime.utcnow()
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": order_to_response(order, include_items=True)
    }


@router.post("/orders/{order_no}/refund", response_model=dict)
def refund_order(
    order_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """申请退款：已付款待发货订单变更为退款中"""
    from app.models.order import Order

    user_id = current_user.id
    order = db.query(Order).filter(
        Order.order_no == order_no,
        Order.user_id == user_id
    ).first()

    if not order:
        return {
            "code": ErrorCode.ORDER_NOT_FOUND,
            "message": "订单不存在",
            "data": None
        }

    if order.status != Order.STATUS_PAID:
        return {
            "code": ErrorCode.ORDER_STATUS_ERROR,
            "message": "订单状态不允许退款",
            "data": None
        }

    order.status = Order.STATUS_REFUNDING
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": order_to_response(order, include_items=True)
    }


@router.get("/orders/{order_id}/tracking", response_model=dict)
def get_order_tracking(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """查询订单追踪节点

    Args:
        order_id: 订单ID

    Returns:
        统一响应格式
    """
    from app.models.order import Order

    user_id = current_user.id

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user_id
    ).first()

    if not order:
        return {
            "code": ErrorCode.ORDER_NOT_FOUND,
            "message": "订单不存在",
            "data": None
        }

    # 追踪节点映射
    tracking_nodes = {
        0: {"name": "已采摘", "desc": "农产品已采摘"},
        1: {"name": "已打包", "desc": "商品已打包完毕"},
        2: {"name": "已发货", "desc": "商品已发出"},
        3: {"name": "已送达", "desc": "商品已送达"}
    }

    current_node = getattr(order, 'tracking_node', 0)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "order_no": order.order_no,
            "current_node": current_node,
            "logistics_company": getattr(order, 'logistics_company', ''),
            "logistics_no": getattr(order, 'logistics_no', ''),
            "nodes": [
                {
                    "index": i,
                    "name": tracking_nodes[i]["name"],
                    "desc": tracking_nodes[i]["desc"],
                    "completed": i <= current_node
                }
                for i in range(4)
            ]
        }
    }

"""订单相关定时任务 - GWP小店 Celery Tasks"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from celery import shared_task
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.core.database import get_engine, get_session_factory
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.coupon import Coupon
from app.models.user import User

logger = logging.getLogger(__name__)

# 订单超时时间（分钟）
ORDER_TIMEOUT_MINUTES = 30


def get_db():
    """获取数据库会话（Celery任务中使用）"""
    engine = get_engine()
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def _cancel_expired_orders_logic(db: Session, cutoff_time: datetime):
    """取消超时订单核心逻辑（可单独测试）

    Args:
        db: 数据库会话
        cutoff_time: 超时截止时间

    Returns:
        取消的订单数量
    """
    # 查找超时订单
    expired_orders = db.scalars(
        select(Order).where(
            and_(
                Order.status == Order.STATUS_PENDING,
                Order.created_at < cutoff_time,
            )
        )
    ).all()

    if not expired_orders:
        logger.info("[_cancel_expired_orders_logic] 没有超时订单")
        return 0

    cancelled_count = 0
    for order in expired_orders:
        try:
            # 1. 回滚库存
            for item in order.items:
                product = db.get(Product, item.product_id)
                if product:
                    product.stock += item.quantity
                    logger.info(f"[_cancel_expired_orders_logic] 订单 {order.order_no} 退回库存: "
                               f"商品 {product.name} x{item.quantity}")

            # 2. 退回优惠券（查找该订单关联用户最近使用的优惠券）
            used_coupon = db.scalar(
                select(Coupon).where(
                    and_(
                        Coupon.user_id == order.user_id,
                        Coupon.status == 1,
                    )
                ).order_by(Coupon.created_at.desc()).limit(1)
            )
            if used_coupon:
                used_coupon.status = 0
                logger.info(f"[_cancel_expired_orders_logic] 订单 {order.order_no} 退回优惠券: {used_coupon.code}")

            # 3. 更新订单状态
            order.status = Order.STATUS_CANCELLED

            cancelled_count += 1
            logger.info(f"[_cancel_expired_orders_logic] 已取消订单: {order.order_no}")

        except Exception as e:
            logger.error(f"[_cancel_expired_orders_logic] 取消订单 {order.order_no} 失败: {e}")
            raise

    # 确保更改刷新到数据库（供测试使用）
    db.flush()
    return cancelled_count


@shared_task(bind=True, max_retries=3, default_retry_delay=60, name="order_tasks.cancel_expired_orders")
def cancel_expired_orders(self):
    """取消超时未付款订单

    查找状态为待付款(0)且创建时间超过30分钟的订单：
    1. 回滚库存
    2. 退回已用优惠券
    3. 更新订单状态为已取消(4)
    4. 发送微信通知
    """
    db = None
    try:
        db = get_db()
        cutoff_time = datetime.utcnow() - timedelta(minutes=ORDER_TIMEOUT_MINUTES)

        cancelled_count = _cancel_expired_orders_logic(db, cutoff_time)

        db.commit()
        logger.info(f"[cancel_expired_orders] 完成，共取消 {cancelled_count} 个订单")

        # 为每个取消的订单发送通知
        if cancelled_count > 0:
            cutoff_time = datetime.utcnow() - timedelta(minutes=ORDER_TIMEOUT_MINUTES)
            cancelled_orders = db.scalars(
                select(Order).where(
                    and_(
                        Order.status == Order.STATUS_CANCELLED,
                        Order.created_at < cutoff_time,
                    )
                ).order_by(Order.created_at.desc()).limit(cancelled_count)
            ).all()
            for order in cancelled_orders:
                _send_notification("notification_tasks.send_order_cancelled_notification", order.order_no)

        return {"cancelled": cancelled_count}

    except Exception as e:
        logger.error(f"[cancel_expired_orders] 执行失败: {e}")
        if db:
            db.rollback()
        raise self.retry(exc=e)
    finally:
        if db:
            db.close()


def _check_refund_orders_logic(db: Session) -> int:
    """检查退款订单核心逻辑（可单独测试）

    Args:
        db: 数据库会话

    Returns:
        检查的订单数量
    """
    # 查找退款中的订单
    refunding_orders = db.scalars(
        select(Order).where(Order.status == Order.STATUS_REFUNDING)
    ).all()

    if not refunding_orders:
        logger.info("[_check_refund_orders_logic] 没有退款中的订单")
        return 0

    checked_count = 0
    for order in refunding_orders:
        try:
            # 调用微信支付查询退款状态
            refund_status = query_wechat_refund_status(order)

            if refund_status == "SUCCESS":
                # 退款成功，更新订单状态
                order.status = Order.STATUS_REFUNDED
                logger.info(f"[_check_refund_orders_logic] 订单 {order.order_no} 退款成功")
            elif refund_status == "FAIL":
                # 退款失败，记录日志（保持退款中状态供下次重试）
                logger.warning(f"[_check_refund_orders_logic] 订单 {order.order_no} 退款失败")
            else:
                # 处理中或其他状态
                logger.info(f"[_check_refund_orders_logic] 订单 {order.order_no} 退款状态: {refund_status}")

            checked_count += 1

        except Exception as e:
            logger.error(f"[_check_refund_orders_logic] 检查订单 {order.order_no} 失败: {e}")
            raise

    # 确保更改刷新到数据库（供测试使用）
    db.flush()
    return checked_count


@shared_task(bind=True, max_retries=3, default_retry_delay=300, name="order_tasks.check_refund_orders")
def check_refund_orders(self):
    """检查退款中订单的微信支付退款状态

    查找状态为退款中(6)的订单，调用微信支付API查询退款状态：
    - 退款成功：更新订单状态为已退款(5)，触发微信退款
    - 退款失败：保持退款中状态，记录错误
    """
    db = None
    try:
        db = get_db()

        checked_count = _check_refund_orders_logic(db)

        db.commit()
        logger.info(f"[check_refund_orders] 完成，共检查 {checked_count} 个订单")

        # 发送退款成功通知
        if checked_count > 0:
            success_orders = db.scalars(
                select(Order).where(Order.status == Order.STATUS_REFUNDED).limit(checked_count)
            ).all()
            for order in success_orders:
                _send_notification("notification_tasks.send_refund_success_notification", order.order_no)

        return {"checked": checked_count}

    except Exception as e:
        logger.error(f"[check_refund_orders] 执行失败: {e}")
        if db:
            db.rollback()
        raise self.retry(exc=e)
    finally:
        if db:
            db.close()


def query_wechat_refund_status(order: Order) -> str:
    """查询微信支付退款状态
    
    Args:
        order: 订单对象
        
    Returns:
        SUCCESS: 退款成功
        FAIL: 退款失败
        PROCESSING: 退款处理中
        NOT_FOUND: 未找到退款记录
    """
    # TODO: 实现微信支付退款查询API
    # 实际实现需要调用微信支付API:
    # POST https://api.mch.weixin.qq.com/pay/refundquery
    # 参数: transaction_id 或 out_trade_no + out_refund_no
    # 
    # 这里返回 PROCESSING 作为占位，表示退款仍在处理中
    logger.info(f"[query_wechat_refund_status] 查询订单 {order.order_no} 退款状态 (mock)")
    return "PROCESSING"


def _expire_coupons_logic(db: Session, now: datetime) -> int:
    """优惠券过期核心逻辑（可单独测试）

    Args:
        db: 数据库会话
        now: 当前时间

    Returns:
        过期的优惠券数量
    """
    # 查找已过期但状态仍为未使用的优惠券
    expired_coupons = db.scalars(
        select(Coupon).where(
            and_(
                Coupon.status == 0,
                Coupon.expires_at < now,
            )
        )
    ).all()

    if not expired_coupons:
        logger.info("[_expire_coupons_logic] 没有过期优惠券")
        return 0

    expired_count = 0
    for coupon in expired_coupons:
        coupon.status = 2  # 已过期
        expired_count += 1
        logger.info(f"[_expire_coupons_logic] 优惠券已过期: {coupon.code}")

    # 确保更改刷新到数据库（供测试使用）
    db.flush()
    return expired_count


@shared_task(bind=True, max_retries=3, default_retry_delay=60, name="order_tasks.expire_coupons")
def expire_coupons(self):
    """将过期的优惠券状态更新为已过期

    查找状态为未使用(0)且已过期的优惠券，更新状态为已过期(2)
    """
    db = None
    try:
        db = get_db()
        now = datetime.utcnow()

        expired_count = _expire_coupons_logic(db, now)

        db.commit()
        logger.info(f"[expire_coupons] 完成，共 {expired_count} 张优惠券过期")
        return {"expired": expired_count}

    except Exception as e:
        logger.error(f"[expire_coupons] 执行失败: {e}")
        if db:
            db.rollback()
        raise self.retry(exc=e)
    finally:
        if db:
            db.close()


# 通知任务通过 send_task 调用避免循环导入
def _send_notification(task_name: str, *args, **kwargs):
    """通过 Celery send_task 延迟发送通知"""
    from celery_app import celery_app
    celery_app.send_task(task_name, args=args, kwargs=kwargs)

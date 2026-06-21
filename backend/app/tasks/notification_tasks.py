"""通知相关定时任务 - GWP小店 Celery Tasks"""
import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal

import httpx
from celery import shared_task
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.core.database import get_engine, get_session_factory
from app.core.config import settings
from app.models.order import Order
from app.models.user import User

logger = logging.getLogger(__name__)


def get_db():
    """获取数据库会话"""
    engine = get_engine()
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def get_wechat_access_token() -> str:
    """获取微信 access_token"""
    # TODO: 实现从缓存或微信API获取access_token
    # 实际实现:
    # url = f"https://api.weixin.qq.com/cgi-bin/token"
    # params = {"grant_type": "client_credential", "appid": settings.WX_APPID, "secret": settings.WX_SECRET}
    # response = httpx.get(url, params=params)
    # return response.json()["access_token"]
    logger.warning("[get_wechat_access_token] 使用mock token，实际需实现")
    return "mock_access_token"


def send_wechat_subscribe_message(openid: str, template_id: str, data: dict) -> bool:
    """发送微信订阅消息
    
    Args:
        openid: 用户openid
        template_id: 模板消息ID
        data: 模板数据
        
    Returns:
        是否发送成功
    """
    try:
        access_token = get_wechat_access_token()
        url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send"
        params = {"access_token": access_token}
        
        payload = {
            "touser": openid,
            "template_id": template_id,
            "data": data,
        }
        
        # 实际发送（目前mock）
        logger.info(f"[send_wechat_subscribe_message] 发送至 {openid}, 模板 {template_id}, 数据: {data}")
        # response = httpx.post(url, params=params, json=payload, timeout=10)
        # result = response.json()
        # return result.get("errcode") == 0
        return True
        
    except Exception as e:
        logger.error(f"[send_wechat_subscribe_message] 发送失败: {e}")
        return False


def _send_order_notification_logic(db: Session, order_no: str, notification_type: str) -> dict:
    """发送订单通知核心逻辑（可单独测试）

    Args:
        db: 数据库会话
        order_no: 订单号
        notification_type: 通知类型

    Returns:
        包含 success 和 reason 的字典
    """
    # 查询订单
    order = db.scalars(
        select(Order).where(Order.order_no == order_no)
    ).first()

    if not order:
        logger.warning(f"[_send_order_notification_logic] 订单 {order_no} 不存在")
        return {"success": False, "reason": "order_not_found"}

    # 查询用户获取openid
    user = db.get(User, order.user_id)
    if not user or not user.openid:
        logger.warning(f"[_send_order_notification_logic] 用户或openid不存在")
        return {"success": False, "reason": "user_or_openid_not_found"}

    # 根据通知类型构建消息
    messages = {
        "order_placed": {
            "template_id": "YOUR_TEMPLATE_ID_1",
            "data": {
                "order_no": {"value": order_no},
                "amount": {"value": str(order.pay_amount)},
            }
        },
        "order_paid": {
            "template_id": "YOUR_TEMPLATE_ID_2",
            "data": {
                "order_no": {"value": order_no},
                "amount": {"value": str(order.pay_amount)},
            }
        },
        "order_shipped": {
            "template_id": "YOUR_TEMPLATE_ID_3",
            "data": {
                "order_no": {"value": order_no},
                "logistics": {"value": order.logistics_company or "未知"},
                "tracking_no": {"value": order.logistics_no or "未知"},
            }
        },
        "order_received": {
            "template_id": "YOUR_TEMPLATE_ID_4",
            "data": {
                "order_no": {"value": order_no},
            }
        },
        "order_cancelled": {
            "template_id": "YOUR_TEMPLATE_ID_5",
            "data": {
                "order_no": {"value": order_no},
                "reason": {"value": "超时未付款"},
            }
        },
        "refund_success": {
            "template_id": "YOUR_TEMPLATE_ID_6",
            "data": {
                "order_no": {"value": order_no},
                "amount": {"value": str(order.pay_amount)},
                "reason": {"value": "退款已原路退回"},
            }
        },
    }

    msg_config = messages.get(notification_type)
    if not msg_config:
        logger.warning(f"[_send_order_notification_logic] 未知通知类型: {notification_type}")
        return {"success": False, "reason": "unknown_type"}

    success = send_wechat_subscribe_message(
        openid=user.openid,
        template_id=msg_config["template_id"],
        data=msg_config["data"],
    )

    logger.info(f"[_send_order_notification_logic] 订单 {order_no} {notification_type} 通知: {'成功' if success else '失败'}")
    return {"success": success}


@shared_task(bind=True, max_retries=3, default_retry_delay=60, name="notification_tasks.send_order_notification")
def send_order_notification(self, order_no: str, notification_type: str):
    """发送订单状态变更微信通知

    由 API 订单状态变更时触发，支持的通知类型：
    - order_placed: 下单成功
    - order_paid: 付款成功
    - order_shipped: 已发货
    - order_received: 已收货
    - order_cancelled: 订单取消
    - refund_success: 退款成功

    Args:
        order_no: 订单号
        notification_type: 通知类型
    """
    db = None
    try:
        db = get_db()
        result = _send_order_notification_logic(db, order_no, notification_type)
        return result

    except Exception as e:
        logger.error(f"[send_order_notification] 执行失败: {e}")
        raise self.retry(exc=e)
    finally:
        if db:
            db.close()


@shared_task(bind=True, max_retries=3, default_retry_delay=60, name="notification_tasks.send_order_cancelled_notification")
def send_order_cancelled_notification(self, order_no: str):
    """订单取消通知（被 order_tasks.cancel_expired_orders 调用）"""
    return send_order_notification(order_no, "order_cancelled")


@shared_task(bind=True, max_retries=3, default_retry_delay=60, name="notification_tasks.send_refund_success_notification")
def send_refund_success_notification(self, order_no: str):
    """退款成功通知（被 order_tasks.check_refund_orders 调用）"""
    return send_order_notification(order_no, "refund_success")


def _send_daily_summary_logic(db: Session, yesterday_start: datetime, yesterday_end: datetime) -> dict:
    """每日订单汇总核心逻辑（可单独测试）

    Args:
        db: 数据库会话
        yesterday_start: 昨日开始时间
        yesterday_end: 昨日结束时间

    Returns:
        汇总结果字典
    """
    # 统计各项数据
    total_new = db.scalar(
        select(func.count(Order.id)).where(
            Order.created_at >= yesterday_start,
            Order.created_at < yesterday_end,
        )
    ) or 0

    total_paid = db.scalar(
        select(func.count(Order.id)).where(
            Order.created_at >= yesterday_start,
            Order.created_at < yesterday_end,
            Order.status.in_([Order.STATUS_PAID, Order.STATUS_SHIPPED, Order.STATUS_COMPLETED]),
        )
    ) or 0

    total_cancelled = db.scalar(
        select(func.count(Order.id)).where(
            Order.created_at >= yesterday_start,
            Order.created_at < yesterday_end,
            Order.status == Order.STATUS_CANCELLED,
        )
    ) or 0

    total_refunded = db.scalar(
        select(func.count(Order.id)).where(
            Order.created_at >= yesterday_start,
            Order.created_at < yesterday_end,
            Order.status == Order.STATUS_REFUNDED,
        )
    ) or 0

    total_sales = db.scalar(
        select(func.coalesce(func.sum(Order.pay_amount), 0)).where(
            Order.created_at >= yesterday_start,
            Order.created_at < yesterday_end,
            Order.status.in_([Order.STATUS_PAID, Order.STATUS_SHIPPED, Order.STATUS_COMPLETED]),
        )
    ) or Decimal("0")

    yesterday_str = yesterday_start.strftime("%Y-%m-%d")

    # 构建汇总消息
    summary_text = (
        f"📊 GWP小店日报 [{yesterday_str}]\n\n"
        f"📦 新增订单: {total_new} 单\n"
        f"💰 已付款: {total_paid} 单\n"
        f"❌ 已取消: {total_cancelled} 单\n"
        f"💸 已退款: {total_refunded} 单\n"
        f"💵 销售总额: ¥{total_sales:.2f}"
    )

    logger.info(f"[_send_daily_summary_logic] 昨日汇总: {summary_text}")

    return {
        "date": yesterday_str,
        "total_new": total_new,
        "total_paid": total_paid,
        "total_cancelled": total_cancelled,
        "total_refunded": total_refunded,
        "total_sales": str(total_sales),
        "summary_text": summary_text,
    }


@shared_task(bind=True, max_retries=3, default_retry_delay=300, name="notification_tasks.send_daily_summary")
def send_daily_summary(self):
    """每日订单汇总通知 - 每天9:00发送给管理员

    统计昨日订单数据：
    - 新增订单数
    - 已付款订单数
    - 取消订单数
    - 退款订单数
    - 总销售额
    """
    db = None
    try:
        db = get_db()

        # 昨日时间范围
        yesterday_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        yesterday_end = yesterday_start + timedelta(days=1)

        result = _send_daily_summary_logic(db, yesterday_start, yesterday_end)

        # TODO: 发送给管理员（目前mock）
        # 可以通过微信模板消息或邮件发送
        # admin_openid = "ADMIN_OPENID"
        # send_wechat_subscribe_message(admin_openid, "ADMIN_TEMPLATE_ID", {...})

        return result

    except Exception as e:
        logger.error(f"[send_daily_summary] 执行失败: {e}")
        raise self.retry(exc=e)
    finally:
        if db:
            db.close()

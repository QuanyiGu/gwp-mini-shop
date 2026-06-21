"""Celery 应用配置 - GWP小店定时任务"""
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# 创建 Celery 应用
celery_app = Celery(
    "gwp_shop",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.order_tasks",
        "app.tasks.notification_tasks",
    ]
)

# Celery 配置
celery_app.conf.update(
    # 序列化方式
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,

    # 任务执行配置
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=300,  # 5分钟超时
    task_soft_time_limit=240,  # 4分钟软超时

    # 结果配置
    result_expires=3600,  # 结果保留1小时
    result_extended=True,

    # Worker 配置
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Beat 定时任务调度
    beat_schedule={
        # 订单超时取消 - 每5分钟检查一次
        "cancel-expired-orders": {
            "task": "app.tasks.order_tasks.cancel_expired_orders",
            "schedule": crontab(minute="*/5"),
            "options": {"queue": "order_tasks"},
        },
        # 退款状态检查 - 每10分钟检查一次
        "check-refund-orders": {
            "task": "app.tasks.order_tasks.check_refund_orders",
            "schedule": crontab(minute="*/10"),
            "options": {"queue": "order_tasks"},
        },
        # 优惠券过期检查 - 每小时检查一次
        "expire-coupons": {
            "task": "app.tasks.order_tasks.expire_coupons",
            "schedule": crontab(minute=0),
            "options": {"queue": "order_tasks"},
        },
        # 每日订单汇总通知 - 每天9:00
        "daily-summary": {
            "task": "app.tasks.notification_tasks.send_daily_summary",
            "schedule": crontab(hour=9, minute=0),
            "options": {"queue": "notifications"},
        },
    },
    # 任务路由
    task_routes={
        "app.tasks.order_tasks.*": {"queue": "order_tasks"},
        "app.tasks.notification_tasks.*": {"queue": "notifications"},
    },
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def health_check(self):
    """健康检查任务"""
    return {"status": "ok", "service": "celery"}

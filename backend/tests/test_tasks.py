"""Celery定时任务测试 - GWP小店"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.models.coupon import Coupon
from app.utils.snowflake import generate_order_no


@pytest.fixture
def category(db_session):
    cat = Category(name="水果", icon="fruit.png", sort=1)
    db_session.add(cat)
    db_session.flush()
    return cat


@pytest.fixture
def product(db_session, category):
    p = Product(
        name="红富士苹果",
        category_id=category.id,
        price=Decimal("29.90"),
        stock=100,
        main_image="/images/apple.jpg",
        images="/images/apple.jpg",
        description="新鲜红富士",
        status=1,
    )
    db_session.add(p)
    db_session.flush()
    return p


@pytest.fixture
def user(db_session):
    u = User(
        uid="test_user_001",
        nickname="测试用户",
        openid="test_openid_12345",
    )
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def pending_order(db_session, user, product):
    """创建一个待付款订单"""
    # 确保库存重置为100
    product.stock = 100
    db_session.flush()
    
    order = Order(
        order_no=str(generate_order_no()),
        user_id=user.id,
        total_amount=Decimal("59.80"),
        pay_amount=Decimal("59.80"),
        discount_amount=Decimal("0"),
        status=Order.STATUS_PENDING,
        address_name="张三",
        address_phone="13800138000",
        address_detail="广东省深圳市南山区",
        created_at=datetime.utcnow(),  # 显式设置创建时间
    )
    db_session.add(order)
    db_session.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        product_image=product.main_image,
        price=product.price,
        quantity=2,
        total_price=Decimal("59.80"),
    )
    db_session.add(order_item)
    db_session.flush()

    # 扣减库存
    product.stock -= 2
    db_session.flush()

    return order


@pytest.fixture
def expired_order(db_session, pending_order):
    """创建一个已过期的待付款订单"""
    pending_order.created_at = datetime.utcnow() - timedelta(minutes=31)
    db_session.flush()
    return pending_order


@pytest.fixture
def non_expired_order(db_session, pending_order):
    """创建一个未过期的待付款订单"""
    pending_order.created_at = datetime.utcnow() - timedelta(minutes=10)
    db_session.flush()
    return pending_order


@pytest.fixture
def refunding_order(db_session, user, product):
    """创建一个退款中的订单"""
    order = Order(
        order_no=str(generate_order_no()),
        user_id=user.id,
        total_amount=Decimal("29.90"),
        pay_amount=Decimal("29.90"),
        discount_amount=Decimal("0"),
        status=Order.STATUS_REFUNDING,
        address_name="张三",
        address_phone="13800138000",
        address_detail="广东省深圳市南山区",
    )
    db_session.add(order)
    db_session.flush()
    return order


@pytest.fixture
def coupon_to_expire(db_session, user):
    """创建一个即将过期的优惠券"""
    c = Coupon(
        user_id=user.id,
        code="EXPIRE_SOON",
        type=1,
        discount=Decimal("10.00"),
        min_amount=Decimal("50.00"),
        status=0,
        expires_at=datetime.utcnow() - timedelta(days=1),
    )
    db_session.add(c)
    db_session.flush()
    return c


@pytest.fixture
def valid_coupon(db_session, user):
    """创建一个有效的优惠券"""
    c = Coupon(
        user_id=user.id,
        code="VALID_001",
        type=1,
        discount=Decimal("10.00"),
        min_amount=Decimal("50.00"),
        status=0,
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db_session.add(c)
    db_session.flush()
    return c


@pytest.fixture
def yesterdays_orders(db_session, user, product):
    """创建昨日的测试订单"""
    orders = []
    yesterday = datetime.utcnow() - timedelta(days=1)

    # 已付款订单
    order1 = Order(
        order_no=str(generate_order_no()),
        user_id=user.id,
        total_amount=Decimal("59.80"),
        pay_amount=Decimal("59.80"),
        status=Order.STATUS_PAID,
        address_name="张三",
        address_phone="13800138000",
        address_detail="广东省深圳市南山区",
        created_at=yesterday.replace(hour=10),
    )
    db_session.add(order1)
    orders.append(order1)

    # 已取消订单
    order2 = Order(
        order_no=str(generate_order_no()),
        user_id=user.id,
        total_amount=Decimal("29.90"),
        pay_amount=Decimal("29.90"),
        status=Order.STATUS_CANCELLED,
        address_name="张三",
        address_phone="13800138000",
        address_detail="广东省深圳市南山区",
        created_at=yesterday.replace(hour=11),
    )
    db_session.add(order2)
    orders.append(order2)

    db_session.flush()
    return orders


class TestCancelExpiredOrders:
    """取消超时订单任务测试"""

    def test_cancel_expired_order(self, db_session, expired_order, product):
        """成功取消超时订单"""
        from app.tasks.order_tasks import _cancel_expired_orders_logic

        # 运行任务前检查状态
        db_session.refresh(expired_order)
        assert expired_order.status == Order.STATUS_PENDING
        assert product.stock == 98  # 已扣减

        # 将占位订单(id=0)和其他订单改为非待付款状态，确保只统计我们的测试订单
        db_session.query(Order).filter(Order.id != expired_order.id).update({Order.status: Order.STATUS_PAID})
        db_session.flush()

        # 运行核心逻辑 - 使用宽松的截止时间确保订单被认定为过期
        # 订单创建于31分钟前，截止时间设为现在-25分钟，这样订单肯定过期了
        cutoff_time = datetime.utcnow() - timedelta(minutes=25)
        
        cancelled_count = _cancel_expired_orders_logic(db_session, cutoff_time)

        assert cancelled_count == 1

        # 验证订单状态和库存
        db_session.refresh(expired_order)
        assert expired_order.status == Order.STATUS_CANCELLED
        db_session.refresh(product)
        assert product.stock == 100  # 库存已回滚

    def test_no_expired_orders(self, db_session, non_expired_order):
        """没有超时订单"""
        from app.tasks.order_tasks import _cancel_expired_orders_logic

        # 将所有其他订单改为非待付款状态，确保只有我们的目标订单是待付款
        db_session.query(Order).filter(Order.id != non_expired_order.id).update({Order.status: Order.STATUS_PAID})
        db_session.flush()

        # 确保订单创建时间是最近的，不会被误判为过期
        db_session.refresh(non_expired_order)

        # 使用严格的截止时间（现在-35分钟），确保10分钟前的订单不会被取消
        cutoff_time = datetime.utcnow() - timedelta(minutes=35)
        cancelled_count = _cancel_expired_orders_logic(db_session, cutoff_time)

        assert cancelled_count == 0

        # 订单状态保持不变
        db_session.refresh(non_expired_order)
        assert non_expired_order.status == Order.STATUS_PENDING

    def test_cancel_order_with_coupon_rollback(self, db_session, expired_order, user, product):
        """取消订单时优惠券退回"""
        from app.tasks.order_tasks import _cancel_expired_orders_logic

        # 创建一个已使用的优惠券
        used_coupon = Coupon(
            user_id=user.id,
            code="USED_001",
            type=1,
            discount=Decimal("10.00"),
            min_amount=Decimal("50.00"),
            status=1,
            expires_at=datetime.utcnow() + timedelta(days=30),
        )
        db_session.add(used_coupon)
        db_session.flush()

        # 先将其他订单改为非待付款状态，确保只取消我们的目标订单
        db_session.query(Order).filter(Order.id != expired_order.id).update({Order.status: Order.STATUS_PAID})
        db_session.flush()

        # 运行核心逻辑
        cutoff_time = datetime.utcnow() - timedelta(minutes=25)
        cancelled_count = _cancel_expired_orders_logic(db_session, cutoff_time)

        assert cancelled_count == 1

        # 验证优惠券已退回
        db_session.refresh(used_coupon)
        assert used_coupon.status == 0


class TestCheckRefundOrders:
    """检查退款订单任务测试"""

    def test_check_refunding_orders(self, db_session, refunding_order):
        """检查退款中的订单"""
        from app.tasks.order_tasks import _check_refund_orders_logic

        with patch("app.tasks.order_tasks.query_wechat_refund_status", return_value="SUCCESS"):
            checked_count = _check_refund_orders_logic(db_session)

        assert checked_count == 1

        # 验证订单状态更新
        db_session.refresh(refunding_order)
        assert refunding_order.status == Order.STATUS_REFUNDED

    def test_no_refunding_orders(self, db_session, pending_order):
        """没有退款中的订单"""
        from app.tasks.order_tasks import _check_refund_orders_logic

        checked_count = _check_refund_orders_logic(db_session)
        assert checked_count == 0


class TestExpireCoupons:
    """优惠券过期任务测试"""

    def test_expire_expired_coupons(self, db_session, coupon_to_expire):
        """将已过期的优惠券标记为过期"""
        from app.tasks.order_tasks import _expire_coupons_logic

        # 运行任务前检查
        db_session.refresh(coupon_to_expire)
        assert coupon_to_expire.status == 0  # 未使用

        now = datetime.utcnow()
        expired_count = _expire_coupons_logic(db_session, now)
        assert expired_count == 1

        # 验证优惠券状态已更新
        db_session.refresh(coupon_to_expire)
        assert coupon_to_expire.status == 2  # 已过期

    def test_no_expired_coupons(self, db_session, valid_coupon):
        """没有需要过期的优惠券"""
        from app.tasks.order_tasks import _expire_coupons_logic

        now = datetime.utcnow()
        expired_count = _expire_coupons_logic(db_session, now)
        assert expired_count == 0

        # 优惠券状态保持不变
        db_session.refresh(valid_coupon)
        assert valid_coupon.status == 0


class TestSendDailySummary:
    """每日汇总通知测试"""

    def test_send_daily_summary(self, db_session, yesterdays_orders):
        """发送每日订单汇总"""
        from app.tasks.notification_tasks import _send_daily_summary_logic

        yesterday_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        yesterday_end = yesterday_start + timedelta(days=1)

        result = _send_daily_summary_logic(db_session, yesterday_start, yesterday_end)

        assert result["total_new"] == 2
        assert result["total_paid"] == 1
        assert result["total_cancelled"] == 1
        assert result["total_refunded"] == 0
        assert result["total_sales"] == "59.80"
        assert "GWP小店日报" in result["summary_text"]


class TestSendOrderNotification:
    """订单状态通知测试"""

    def test_send_order_placed_notification(self, db_session, pending_order):
        """发送下单成功通知"""
        from app.tasks.notification_tasks import _send_order_notification_logic

        with patch("app.tasks.notification_tasks.send_wechat_subscribe_message", return_value=True):
            result = _send_order_notification_logic(db_session, pending_order.order_no, "order_placed")

        assert result["success"] is True

    def test_send_order_paid_notification(self, db_session, pending_order):
        """发送付款成功通知"""
        from app.tasks.notification_tasks import _send_order_notification_logic

        with patch("app.tasks.notification_tasks.send_wechat_subscribe_message", return_value=True):
            result = _send_order_notification_logic(db_session, pending_order.order_no, "order_paid")

        assert result["success"] is True

    def test_send_order_notification_order_not_found(self, db_session):
        """订单不存在时发送通知"""
        from app.tasks.notification_tasks import _send_order_notification_logic

        result = _send_order_notification_logic(db_session, "NONEXISTENT_ORDER", "order_paid")
        assert result["success"] is False
        assert result["reason"] == "order_not_found"

    def test_send_order_notification_unknown_type(self, db_session, pending_order):
        """未知通知类型"""
        from app.tasks.notification_tasks import _send_order_notification_logic

        result = _send_order_notification_logic(db_session, pending_order.order_no, "unknown_type")
        assert result["success"] is False
        assert result["reason"] == "unknown_type"


class TestWechatSubscribeMessage:
    """微信订阅消息发送测试"""

    def test_send_wechat_subscribe_message_success(self, db_session):
        """成功发送微信订阅消息"""
        from app.tasks.notification_tasks import send_wechat_subscribe_message

        with patch("app.tasks.notification_tasks.get_wechat_access_token", return_value="mock_token"):
            result = send_wechat_subscribe_message(
                openid="test_openid",
                template_id="test_template_id",
                data={"field1": {"value": "test"}}
            )

        assert result is True

    def test_get_wechat_access_token(self, db_session):
        """获取微信access_token"""
        from app.tasks.notification_tasks import get_wechat_access_token

        token = get_wechat_access_token()
        assert token == "mock_access_token"

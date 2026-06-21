"""订单服务层测试"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.models.address import Address
from app.models.coupon import Coupon
from app.utils.error_codes import ErrorCode


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
def product2(db_session, category):
    p = Product(
        name="蜂蜜",
        category_id=category.id,
        price=Decimal("89.00"),
        stock=50,
        main_image="/images/honey.jpg",
        images="/images/honey.jpg",
        description="天然蜂蜜",
        status=1,
    )
    db_session.add(p)
    db_session.flush()
    return p


@pytest.fixture
def user(db_session):
    u = User(uid="test_uid_001", nickname="测试用户")
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def address(db_session, user):
    addr = Address(
        user_id=user.id,
        name="张三",
        phone="13800138000",
        province="广东省",
        city="深圳市",
        district="南山区",
        detail="科技园路123号",
        is_default=True,
    )
    db_session.add(addr)
    db_session.flush()
    return addr


@pytest.fixture
def coupon(db_session, user):
    c = Coupon(
        user_id=user.id,
        code="NEW10",
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
def expired_coupon(db_session, user):
    c = Coupon(
        user_id=user.id,
        code="EXPIRED",
        type=1,
        discount=Decimal("5.00"),
        min_amount=Decimal("30.00"),
        status=0,
        expires_at=datetime.utcnow() - timedelta(days=1),
    )
    db_session.add(c)
    db_session.flush()
    return c


@pytest.fixture
def used_coupon(db_session, user):
    c = Coupon(
        user_id=user.id,
        code="USED",
        type=1,
        discount=Decimal("5.00"),
        min_amount=Decimal("30.00"),
        status=1,
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db_session.add(c)
    db_session.flush()
    return c


class TestCreateOrder:
    """创建订单测试"""

    def test_create_order_success(self, db_session, user, address, product):
        """成功创建订单"""
        from app.services.order_service import create_order

        items = [{"product_id": product.id, "quantity": 2}]
        result = create_order(db_session, user.id, address.id, items)

        assert result["code"] == ErrorCode.SUCCESS
        order = result["data"]
        assert order.user_id == user.id
        assert order.total_amount == Decimal("59.80")
        assert order.pay_amount == Decimal("59.80")
        assert order.status == 0
        assert len(order.items) == 1
        assert order.items[0].product_id == product.id
        assert order.items[0].quantity == 2
        # 库存已扣减
        db_session.refresh(product)
        assert product.stock == 98

    def test_create_order_multiple_products(self, db_session, user, address, product, product2):
        """创建订单 - 多商品"""
        from app.services.order_service import create_order

        items = [
            {"product_id": product.id, "quantity": 2},
            {"product_id": product2.id, "quantity": 1},
        ]
        result = create_order(db_session, user.id, address.id, items)

        assert result["code"] == ErrorCode.SUCCESS
        order = result["data"]
        assert len(order.items) == 2
        assert order.total_amount == Decimal("148.80")  # 29.9*2 + 89*1
        db_session.refresh(product)
        db_session.refresh(product2)
        assert product.stock == 98
        assert product2.stock == 49

    def test_create_order_address_not_found(self, db_session, user, product):
        """创建订单 - 地址不存在"""
        from app.services.order_service import create_order

        items = [{"product_id": product.id, "quantity": 1}]
        result = create_order(db_session, user.id, 99999, items)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_create_order_address_not_owner(self, db_session, user, address, product):
        """创建订单 - 地址不属于当前用户"""
        from app.services.order_service import create_order

        # 创建另一个用户的地址
        other_user = User(uid="other_user", nickname="其他用户")
        db_session.add(other_user)
        db_session.flush()
        other_address = Address(
            user_id=other_user.id,
            name="李四",
            phone="13900139000",
            province="北京市",
            city="北京市",
            district="朝阳区",
            detail="某某路456号",
            is_default=True,
        )
        db_session.add(other_address)
        db_session.flush()

        items = [{"product_id": product.id, "quantity": 1}]
        result = create_order(db_session, user.id, other_address.id, items)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_create_order_product_not_found(self, db_session, user, address):
        """创建订单 - 商品不存在"""
        from app.services.order_service import create_order

        items = [{"product_id": 99999, "quantity": 1}]
        result = create_order(db_session, user.id, address.id, items)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_create_order_stock_not_enough(self, db_session, user, address, product):
        """创建订单 - 库存不足"""
        from app.services.order_service import create_order

        items = [{"product_id": product.id, "quantity": 200}]  # 库存只有100
        result = create_order(db_session, user.id, address.id, items)
        assert result["code"] == ErrorCode.STOCK_NOT_ENOUGH
        # 库存未扣减
        db_session.refresh(product)
        assert product.stock == 100

    def test_create_order_with_coupon(self, db_session, user, address, product, coupon):
        """创建订单 - 使用优惠券"""
        from app.services.order_service import create_order

        items = [{"product_id": product.id, "quantity": 2}]  # 59.8 >= 50
        result = create_order(db_session, user.id, address.id, items, coupon_id=coupon.id)

        assert result["code"] == ErrorCode.SUCCESS
        order = result["data"]
        assert order.pay_amount == Decimal("49.80")  # 59.8 - 10
        assert order.discount_amount == Decimal("10.00")
        # 优惠券已标记为已使用
        db_session.refresh(coupon)
        assert coupon.status == 1

    def test_create_order_coupon_not_found(self, db_session, user, address, product):
        """创建订单 - 优惠券不存在"""
        from app.services.order_service import create_order

        items = [{"product_id": product.id, "quantity": 2}]
        result = create_order(db_session, user.id, address.id, items, coupon_id=99999)
        assert result["code"] == ErrorCode.COUPON_NOT_FOUND

    def test_create_order_coupon_not_owner(self, db_session, user, address, product, coupon):
        """创建订单 - 优惠券不属于当前用户"""
        from app.services.order_service import create_order

        # 创建另一个用户的优惠券
        other_user = User(uid="other2", nickname="其他用户2")
        db_session.add(other_user)
        db_session.flush()
        other_coupon = Coupon(
            user_id=other_user.id,
            code="OTHER",
            type=1,
            discount=Decimal("5.00"),
            min_amount=Decimal("30.00"),
            status=0,
            expires_at=datetime.utcnow() + timedelta(days=30),
        )
        db_session.add(other_coupon)
        db_session.flush()

        items = [{"product_id": product.id, "quantity": 2}]
        result = create_order(db_session, user.id, address.id, items, coupon_id=other_coupon.id)
        assert result["code"] == ErrorCode.COUPON_NOT_FOUND

    def test_create_order_coupon_already_used(self, db_session, user, address, product, used_coupon):
        """创建订单 - 优惠券已使用"""
        from app.services.order_service import create_order

        items = [{"product_id": product.id, "quantity": 2}]
        result = create_order(db_session, user.id, address.id, items, coupon_id=used_coupon.id)
        assert result["code"] == ErrorCode.COUPON_USED

    def test_create_order_coupon_expired(self, db_session, user, address, product, expired_coupon):
        """创建订单 - 优惠券已过期"""
        from app.services.order_service import create_order

        items = [{"product_id": product.id, "quantity": 2}]
        result = create_order(db_session, user.id, address.id, items, coupon_id=expired_coupon.id)
        assert result["code"] == ErrorCode.COUPON_EXPIRED

    def test_create_order_coupon_condition_not_met(self, db_session, user, address, product, coupon):
        """创建订单 - 不满足优惠券使用条件"""
        from app.services.order_service import create_order

        items = [{"product_id": product.id, "quantity": 1}]  # 29.9 < 50
        result = create_order(db_session, user.id, address.id, items, coupon_id=coupon.id)
        assert result["code"] == ErrorCode.COUPON_CONDITION_NOT_MET

    def test_create_order_with_gift_and_card(self, db_session, user, address, product):
        """创建订单 - 包含礼品包装和贺卡"""
        from app.services.order_service import create_order

        items = [{"product_id": product.id, "quantity": 1}]
        result = create_order(
            db_session, user.id, address.id, items,
            gift_package=1,
            greeting_card="生日快乐！"
        )

        assert result["code"] == ErrorCode.SUCCESS
        order = result["data"]
        assert order.gift_package == 1
        assert order.greeting_card == "生日快乐！"


class TestCancelOrder:
    """取消订单测试"""

    def test_cancel_order_success(self, db_session, user, address, product):
        """取消订单成功"""
        from app.services.order_service import create_order, cancel_order

        # 先创建订单
        items = [{"product_id": product.id, "quantity": 2}]
        create_result = create_order(db_session, user.id, address.id, items)
        order = create_result["data"]
        db_session.refresh(product)
        assert product.stock == 98

        # 取消订单
        cancel_result = cancel_order(db_session, order.id, user.id)
        assert cancel_result["code"] == ErrorCode.SUCCESS
        assert cancel_result["data"].status == 4  # 已取消

        # 库存已回滚
        db_session.refresh(product)
        assert product.stock == 100

    def test_cancel_order_with_coupon(self, db_session, user, address, product, coupon):
        """取消订单 - 优惠券退回"""
        from app.services.order_service import create_order, cancel_order

        # 先创建订单（使用优惠券）
        items = [{"product_id": product.id, "quantity": 2}]
        create_result = create_order(db_session, user.id, address.id, items, coupon_id=coupon.id)
        order = create_result["data"]
        db_session.refresh(coupon)
        assert coupon.status == 1  # 已使用

        # 取消订单
        cancel_result = cancel_order(db_session, order.id, user.id)
        assert cancel_result["code"] == ErrorCode.SUCCESS

        # 优惠券已退回
        db_session.refresh(coupon)
        assert coupon.status == 0  # 未使用

    def test_cancel_order_not_found(self, db_session, user):
        """取消订单 - 订单不存在"""
        from app.services.order_service import cancel_order

        result = cancel_order(db_session, 99999, user.id)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_cancel_order_not_owner(self, db_session, user, address, product):
        """取消订单 - 越权访问"""
        from app.services.order_service import create_order, cancel_order

        # 创建订单
        items = [{"product_id": product.id, "quantity": 1}]
        create_result = create_order(db_session, user.id, address.id, items)
        order = create_result["data"]

        # 另一个用户尝试取消
        other_user = User(uid="hacker", nickname="黑客")
        db_session.add(other_user)
        db_session.flush()

        result = cancel_order(db_session, order.id, other_user.id)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_cancel_order_wrong_status(self, db_session, user, address, product):
        """取消订单 - 状态不允许（非待付款状态）"""
        from app.services.order_service import create_order, cancel_order
        from app.models.order import Order

        # 创建订单
        items = [{"product_id": product.id, "quantity": 1}]
        create_result = create_order(db_session, user.id, address.id, items)
        order = create_result["data"]

        # 修改为已发货状态
        order.status = Order.STATUS_SHIPPED
        db_session.flush()

        # 尝试取消
        result = cancel_order(db_session, order.id, user.id)
        assert result["code"] == ErrorCode.ORDER_STATUS_ERROR

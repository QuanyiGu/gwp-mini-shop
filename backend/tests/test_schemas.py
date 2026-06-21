"""测试Pydantic schemas - TDD RED阶段"""
import pytest
from datetime import datetime, date
from decimal import Decimal


class TestUserSchemas:
    """测试用户相关schemas"""

    def test_user_create_schema(self):
        """UserCreate应能验证用户创建数据"""
        from app.schemas.user import UserCreate
        data = UserCreate(uid="1234567890", openid="wx_openid_123", nickname="测试用户")
        assert data.uid == "1234567890"
        assert data.openid == "wx_openid_123"
        assert data.nickname == "测试用户"

    def test_user_response_schema(self):
        """UserResponse应能序列化用户数据"""
        from app.schemas.user import UserResponse
        data = UserResponse(
            id=1, uid="1234567890", openid="wx_openid_123",
            nickname="测试用户", avatar_url="", phone="",
            created_at=datetime(2026, 1, 1)
        )
        assert data.id == 1
        assert data.uid == "1234567890"


class TestProductSchemas:
    """测试商品相关schemas"""

    def test_product_create_schema(self):
        """ProductCreate应能验证商品创建数据"""
        from app.schemas.product import ProductCreate
        data = ProductCreate(
            category_id=1, name="红富士苹果", main_image="apple.jpg",
            price=Decimal("29.90"), original_price=Decimal("39.90"),
            stock=100
        )
        assert data.name == "红富士苹果"
        assert data.price == Decimal("29.90")

    def test_product_response_schema(self):
        """ProductResponse应能序列化商品数据"""
        from app.schemas.product import ProductResponse
        data = ProductResponse(
            id=1, category_id=1, name="红富士苹果",
            main_image="apple.jpg", images=[], description="好吃的苹果",
            price=Decimal("29.90"), original_price=Decimal("39.90"),
            stock=100, sales=0, status=1,
            created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1)
        )
        assert data.name == "红富士苹果"
        assert data.status == 1

    def test_product_update_schema(self):
        """ProductUpdate应允许部分更新"""
        from app.schemas.product import ProductUpdate
        data = ProductUpdate(name="新品种苹果")
        assert data.name == "新品种苹果"


class TestOrderSchemas:
    """测试订单相关schemas"""

    def test_order_create_schema(self):
        """OrderCreate应能验证订单创建数据"""
        from app.schemas.order import OrderCreate
        data = OrderCreate(
            address_id=1,
            items=[{"product_id": 1, "quantity": 2}],
            coupon_id=None
        )
        assert data.address_id == 1
        assert len(data.items) == 1

    def test_order_response_schema(self):
        """OrderResponse应能序列化订单数据"""
        from app.schemas.order import OrderResponse
        data = OrderResponse(
            id=1, order_no="1234567890", user_id=1,
            total_amount=Decimal("59.80"), pay_amount=Decimal("59.80"),
            status=0, created_at=datetime(2026, 1, 1),
            items=[]
        )
        assert data.order_no == "1234567890"
        assert data.status == 0


class TestAddressSchemas:
    """测试收货地址相关schemas"""

    def test_address_create_schema(self):
        """AddressCreate应能验证地址创建数据"""
        from app.schemas.address import AddressCreate
        data = AddressCreate(
            name="张三", phone="13800138000",
            province="北京市", city="北京市", district="朝阳区",
            detail="某某街道123号", is_default=1
        )
        assert data.name == "张三"
        assert data.is_default == 1

    def test_address_response_schema(self):
        """AddressResponse应能序列化地址数据"""
        from app.schemas.address import AddressResponse
        data = AddressResponse(
            id=1, user_id=1, name="张三", phone="13800138000",
            province="北京市", city="北京市", district="朝阳区",
            detail="某某街道123号", is_default=1
        )
        assert data.name == "张三"


class TestCategorySchemas:
    """测试分类相关schemas"""

    def test_category_response_schema(self):
        """CategoryResponse应能序列化分类数据"""
        from app.schemas.category import CategoryResponse
        data = CategoryResponse(id=1, name="苹果", icon="apple.png", sort=1)
        assert data.name == "苹果"


class TestCartItemSchemas:
    """测试购物车相关schemas"""

    def test_cart_item_create_schema(self):
        """CartItemCreate应能验证购物车添加数据"""
        from app.schemas.cart import CartItemCreate
        data = CartItemCreate(product_id=1, quantity=2)
        assert data.product_id == 1
        assert data.quantity == 2


class TestCouponSchemas:
    """测试优惠券相关schemas"""

    def test_coupon_response_schema(self):
        """CouponResponse应能序列化优惠券数据"""
        from app.schemas.coupon import CouponResponse
        data = CouponResponse(
            id=1, code="uuid-code", user_id=1,
            type=1, discount=Decimal("5.00"),
            min_amount=Decimal("39.00"), status=0,
            expires_at=datetime(2026, 12, 31),
            created_at=datetime(2026, 1, 1)
        )
        assert data.type == 1
        assert data.discount == Decimal("5.00")


class TestBannerSchemas:
    """测试Banner相关schemas"""

    def test_banner_response_schema(self):
        """BannerResponse应能序列化Banner数据"""
        from app.schemas.banner import BannerResponse
        data = BannerResponse(
            id=1, type="growth_status", title="苹果生长中",
            content="图片URL", status=1,
            created_at=datetime(2026, 1, 1), updated_at=datetime(2026, 1, 1)
        )
        assert data.type == "growth_status"


class TestAdminUserSchemas:
    """测试商家后台用户schemas"""

    def test_admin_login_schema(self):
        """AdminLogin应能验证登录数据"""
        from app.schemas.admin import AdminLogin
        data = AdminLogin(username="admin", password="123456")
        assert data.username == "admin"

    def test_admin_token_response_schema(self):
        """AdminTokenResponse应能序列化token数据"""
        from app.schemas.admin import AdminTokenResponse
        data = AdminTokenResponse(access_token="token123", refresh_token="refresh123")
        assert data.access_token == "token123"


class TestPaginationSchema:
    """测试分页相关schemas"""

    def test_pagination_params(self):
        """PaginationParams应能验证分页参数"""
        from app.schemas.common import PaginationParams
        data = PaginationParams(page=1, page_size=10)
        assert data.page == 1
        assert data.page_size == 10

    def test_pagination_params_defaults(self):
        """PaginationParams应有默认值"""
        from app.schemas.common import PaginationParams
        data = PaginationParams()
        assert data.page == 1
        assert data.page_size == 10

    def test_paginated_response(self):
        """PaginatedResponse应能序列化分页结果"""
        from app.schemas.common import PaginatedResponse
        data = PaginatedResponse(items=[], total=0, page=1, page_size=10)
        assert data.total == 0


class TestErrorCodeSchema:
    """测试错误码schemas"""

    def test_error_response(self):
        """ErrorResponse应能序列化错误信息"""
        from app.schemas.common import ErrorResponse
        data = ErrorResponse(code=1001, message="参数错误")
        assert data.code == 1001
        assert data.message == "参数错误"

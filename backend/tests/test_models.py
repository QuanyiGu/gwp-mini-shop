"""测试13个数据模型 - TDD RED阶段"""
import pytest
from datetime import datetime, date
from decimal import Decimal


class TestUserModel:
    """测试 users 用户表模型"""

    def test_user_model_exists(self):
        """User模型应存在"""
        from app.models.user import User
        assert User is not None

    def test_user_has_required_fields(self):
        """User应有所有必需字段"""
        from app.models.user import User
        assert hasattr(User, 'id')
        assert hasattr(User, 'uid')
        assert hasattr(User, 'openid')
        assert hasattr(User, 'unionid')
        assert hasattr(User, 'nickname')
        assert hasattr(User, 'avatar_url')
        assert hasattr(User, 'phone')
        assert hasattr(User, 'created_at')

    def test_user_table_name(self):
        """User表名应为users"""
        from app.models.user import User
        assert User.__tablename__ == 'users'


class TestProductModel:
    """测试 products 商品表模型"""

    def test_product_model_exists(self):
        """Product模型应存在"""
        from app.models.product import Product
        assert Product is not None

    def test_product_has_required_fields(self):
        """Product应有所有必需字段"""
        from app.models.product import Product
        assert hasattr(Product, 'id')
        assert hasattr(Product, 'category_id')
        assert hasattr(Product, 'name')
        assert hasattr(Product, 'main_image')
        assert hasattr(Product, 'images')
        assert hasattr(Product, 'description')
        assert hasattr(Product, 'price')
        assert hasattr(Product, 'original_price')
        assert hasattr(Product, 'stock')
        assert hasattr(Product, 'sales')
        assert hasattr(Product, 'status')
        assert hasattr(Product, 'created_at')
        assert hasattr(Product, 'updated_at')

    def test_product_table_name(self):
        """Product表名应为products"""
        from app.models.product import Product
        assert Product.__tablename__ == 'products'


class TestOrderModel:
    """测试 orders 订单表模型"""

    def test_order_model_exists(self):
        """Order模型应存在"""
        from app.models.order import Order
        assert Order is not None

    def test_order_has_required_fields(self):
        """Order应有所有必需字段"""
        from app.models.order import Order
        assert hasattr(Order, 'id')
        assert hasattr(Order, 'order_no')
        assert hasattr(Order, 'user_id')
        assert hasattr(Order, 'total_amount')
        assert hasattr(Order, 'pay_amount')
        assert hasattr(Order, 'address_name')
        assert hasattr(Order, 'address_phone')
        assert hasattr(Order, 'address_detail')
        assert hasattr(Order, 'status')
        assert hasattr(Order, 'gift_package')
        assert hasattr(Order, 'greeting_card')
        assert hasattr(Order, 'tracking_node')
        assert hasattr(Order, 'logistics_company')
        assert hasattr(Order, 'logistics_no')
        assert hasattr(Order, 'created_at')

    def test_order_table_name(self):
        """Order表名应为orders"""
        from app.models.order import Order
        assert Order.__tablename__ == 'orders'

    def test_order_status_constants(self):
        """订单状态常量应与设计文档一致"""
        from app.models.order import Order
        assert Order.STATUS_PENDING == 0
        assert Order.STATUS_PAID == 1
        assert Order.STATUS_SHIPPED == 2
        assert Order.STATUS_COMPLETED == 3
        assert Order.STATUS_CANCELLED == 4
        assert Order.STATUS_REFUNDED == 5
        assert Order.STATUS_REFUNDING == 6


class TestOrderItemModel:
    """测试 order_items 订单商品表模型"""

    def test_order_item_model_exists(self):
        """OrderItem模型应存在"""
        from app.models.order_item import OrderItem
        assert OrderItem is not None

    def test_order_item_has_required_fields(self):
        """OrderItem应有所有必需字段"""
        from app.models.order_item import OrderItem
        assert hasattr(OrderItem, 'id')
        assert hasattr(OrderItem, 'order_id')
        assert hasattr(OrderItem, 'product_id')
        assert hasattr(OrderItem, 'product_name')
        assert hasattr(OrderItem, 'product_image')
        assert hasattr(OrderItem, 'price')
        assert hasattr(OrderItem, 'quantity')
        assert hasattr(OrderItem, 'total_price')

    def test_order_item_table_name(self):
        """OrderItem表名应为order_items"""
        from app.models.order_item import OrderItem
        assert OrderItem.__tablename__ == 'order_items'


class TestAddressModel:
    """测试 addresses 收货地址表模型"""

    def test_address_model_exists(self):
        """Address模型应存在"""
        from app.models.address import Address
        assert Address is not None

    def test_address_has_required_fields(self):
        """Address应有所有必需字段"""
        from app.models.address import Address
        assert hasattr(Address, 'id')
        assert hasattr(Address, 'user_id')
        assert hasattr(Address, 'name')
        assert hasattr(Address, 'phone')
        assert hasattr(Address, 'province')
        assert hasattr(Address, 'city')
        assert hasattr(Address, 'district')
        assert hasattr(Address, 'detail')
        assert hasattr(Address, 'is_default')

    def test_address_table_name(self):
        """Address表名应为addresses"""
        from app.models.address import Address
        assert Address.__tablename__ == 'addresses'


class TestCategoryModel:
    """测试 categories 商品分类表模型"""

    def test_category_model_exists(self):
        """Category模型应存在"""
        from app.models.category import Category
        assert Category is not None

    def test_category_has_required_fields(self):
        """Category应有所有必需字段"""
        from app.models.category import Category
        assert hasattr(Category, 'id')
        assert hasattr(Category, 'name')
        assert hasattr(Category, 'icon')
        assert hasattr(Category, 'sort')

    def test_category_table_name(self):
        """Category表名应为categories"""
        from app.models.category import Category
        assert Category.__tablename__ == 'categories'


class TestCartItemModel:
    """测试 cart_items 购物车表模型"""

    def test_cart_item_model_exists(self):
        """CartItem模型应存在"""
        from app.models.cart_item import CartItem
        assert CartItem is not None

    def test_cart_item_has_required_fields(self):
        """CartItem应有所有必需字段"""
        from app.models.cart_item import CartItem
        assert hasattr(CartItem, 'id')
        assert hasattr(CartItem, 'user_id')
        assert hasattr(CartItem, 'product_id')
        assert hasattr(CartItem, 'quantity')
        assert hasattr(CartItem, 'selected')

    def test_cart_item_table_name(self):
        """CartItem表名应为cart_items"""
        from app.models.cart_item import CartItem
        assert CartItem.__tablename__ == 'cart_items'


class TestAdminUserModel:
    """测试 admin_users 商家后台用户表模型"""

    def test_admin_user_model_exists(self):
        """AdminUser模型应存在"""
        from app.models.admin_user import AdminUser
        assert AdminUser is not None

    def test_admin_user_has_required_fields(self):
        """AdminUser应有所有必需字段"""
        from app.models.admin_user import AdminUser
        assert hasattr(AdminUser, 'id')
        assert hasattr(AdminUser, 'username')
        assert hasattr(AdminUser, 'password_hash')
        assert hasattr(AdminUser, 'nickname')
        assert hasattr(AdminUser, 'role')
        assert hasattr(AdminUser, 'created_at')

    def test_admin_user_table_name(self):
        """AdminUser表名应为admin_users"""
        from app.models.admin_user import AdminUser
        assert AdminUser.__tablename__ == 'admin_users'


class TestCouponModel:
    """测试 coupons 优惠券表模型"""

    def test_coupon_model_exists(self):
        """Coupon模型应存在"""
        from app.models.coupon import Coupon
        assert Coupon is not None

    def test_coupon_has_required_fields(self):
        """Coupon应有所有必需字段"""
        from app.models.coupon import Coupon
        assert hasattr(Coupon, 'id')
        assert hasattr(Coupon, 'code')
        assert hasattr(Coupon, 'user_id')
        assert hasattr(Coupon, 'type')
        assert hasattr(Coupon, 'discount')
        assert hasattr(Coupon, 'min_amount')
        assert hasattr(Coupon, 'status')
        assert hasattr(Coupon, 'expires_at')
        assert hasattr(Coupon, 'created_at')

    def test_coupon_table_name(self):
        """Coupon表名应为coupons"""
        from app.models.coupon import Coupon
        assert Coupon.__tablename__ == 'coupons'


class TestInviteModel:
    """测试 invites 邀请记录表模型"""

    def test_invite_model_exists(self):
        """Invite模型应存在"""
        from app.models.invite import Invite
        assert Invite is not None

    def test_invite_has_required_fields(self):
        """Invite应有所有必需字段"""
        from app.models.invite import Invite
        assert hasattr(Invite, 'id')
        assert hasattr(Invite, 'inviter_id')
        assert hasattr(Invite, 'invitee_id')
        assert hasattr(Invite, 'invite_code')
        assert hasattr(Invite, 'order_id')
        assert hasattr(Invite, 'coupon_sent')
        assert hasattr(Invite, 'created_at')

    def test_invite_table_name(self):
        """Invite表名应为invites"""
        from app.models.invite import Invite
        assert Invite.__tablename__ == 'invites'


class TestBannerConfigModel:
    """测试 banner_configs Banner配置表模型"""

    def test_banner_config_model_exists(self):
        """BannerConfig模型应存在"""
        from app.models.banner_config import BannerConfig
        assert BannerConfig is not None

    def test_banner_config_has_required_fields(self):
        """BannerConfig应有所有必需字段"""
        from app.models.banner_config import BannerConfig
        assert hasattr(BannerConfig, 'id')
        assert hasattr(BannerConfig, 'type')
        assert hasattr(BannerConfig, 'title')
        assert hasattr(BannerConfig, 'content')
        assert hasattr(BannerConfig, 'status')
        assert hasattr(BannerConfig, 'created_at')
        assert hasattr(BannerConfig, 'updated_at')

    def test_banner_config_table_name(self):
        """BannerConfig表名应为banner_configs"""
        from app.models.banner_config import BannerConfig
        assert BannerConfig.__tablename__ == 'banner_configs'


class TestProductExtraModel:
    """测试 product_extras 商品扩展表模型"""

    def test_product_extra_model_exists(self):
        """ProductExtra模型应存在"""
        from app.models.product_extra import ProductExtra
        assert ProductExtra is not None

    def test_product_extra_has_required_fields(self):
        """ProductExtra应有所有必需字段"""
        from app.models.product_extra import ProductExtra
        assert hasattr(ProductExtra, 'id')
        assert hasattr(ProductExtra, 'product_id')
        assert hasattr(ProductExtra, 'harvest_date')
        assert hasattr(ProductExtra, 'variety_info')
        assert hasattr(ProductExtra, 'created_at')
        assert hasattr(ProductExtra, 'updated_at')

    def test_product_extra_table_name(self):
        """ProductExtra表名应为product_extras"""
        from app.models.product_extra import ProductExtra
        assert ProductExtra.__tablename__ == 'product_extras'


class TestAdminOperateLogModel:
    """测试 admin_operate_logs 管理员操作日志表模型"""

    def test_admin_operate_log_model_exists(self):
        """AdminOperateLog模型应存在"""
        from app.models.admin_operate_log import AdminOperateLog
        assert AdminOperateLog is not None

    def test_admin_operate_log_has_required_fields(self):
        """AdminOperateLog应有所有必需字段"""
        from app.models.admin_operate_log import AdminOperateLog
        assert hasattr(AdminOperateLog, 'id')
        assert hasattr(AdminOperateLog, 'admin_id')
        assert hasattr(AdminOperateLog, 'action')
        assert hasattr(AdminOperateLog, 'target_type')
        assert hasattr(AdminOperateLog, 'target_id')
        assert hasattr(AdminOperateLog, 'detail')
        assert hasattr(AdminOperateLog, 'created_at')

    def test_admin_operate_log_table_name(self):
        """AdminOperateLog表名应为admin_operate_logs"""
        from app.models.admin_operate_log import AdminOperateLog
        assert AdminOperateLog.__tablename__ == 'admin_operate_logs'


class TestModelsCreateTables:
    """测试所有模型可以创建数据库表"""

    def test_create_all_tables_with_sqlite(self):
        """所有模型应在SQLite上创建对应的表"""
        from sqlalchemy import create_engine, inspect
        from app.core.database import Base
        # 导入所有模型以注册到Base.metadata
        from app.models import user, product, order, order_item, address
        from app.models import category, cart_item, admin_user, coupon
        from app.models import invite, banner_config, product_extra, admin_operate_log

        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        expected_tables = [
            'users', 'products', 'orders', 'order_items', 'addresses',
            'categories', 'cart_items', 'admin_users', 'coupons',
            'invites', 'banner_configs', 'product_extras', 'admin_operate_logs'
        ]

        for table in expected_tables:
            assert table in tables, f"表 {table} 未创建"

"""购物车服务层测试"""
import pytest
from decimal import Decimal

from app.models.product import Product
from app.models.category import Category
from app.models.user import User


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
        images="/images/apple.jpg,/images/apple2.jpg",
        description="新鲜红富士",
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
def product_offline(db_session, category):
    p = Product(
        name="已下架商品",
        category_id=category.id,
        price=Decimal("19.90"),
        stock=10,
        main_image="/images/offline.jpg",
        status=0,  # 下架
    )
    db_session.add(p)
    db_session.flush()
    return p


@pytest.fixture
def product_low_stock(db_session, category):
    """库存很低的商品"""
    p = Product(
        name="限量商品",
        category_id=category.id,
        price=Decimal("99.00"),
        stock=5,
        main_image="/images/limited.jpg",
        status=1,
    )
    db_session.add(p)
    db_session.flush()
    return p


class TestCartService:
    def test_add_to_cart_new(self, db_session, user, product):
        from app.services.cart_service import add_to_cart

        result = add_to_cart(db_session, user.id, product.id, quantity=2)
        assert result["code"] == 0
        assert result["data"].quantity == 2
        assert result["data"].product_id == product.id

    def test_add_to_cart_existing(self, db_session, user, product):
        from app.services.cart_service import add_to_cart

        add_to_cart(db_session, user.id, product.id, quantity=2)
        result = add_to_cart(db_session, user.id, product.id, quantity=3)
        assert result["code"] == 0
        assert result["data"].quantity == 5  # 2+3

    def test_add_to_cart_existing_stock_not_enough(self, db_session, user, product_low_stock):
        """测试已存在商品时，增加数量后库存不足"""
        from app.services.cart_service import add_to_cart
        from app.utils.error_codes import ErrorCode

        # 先加3个（库存5）
        add_to_cart(db_session, user.id, product_low_stock.id, quantity=3)
        # 再加3个，但只剩2个库存
        result = add_to_cart(db_session, user.id, product_low_stock.id, quantity=3)
        assert result["code"] == ErrorCode.STOCK_NOT_ENOUGH

    def test_add_to_cart_product_not_found(self, db_session, user):
        from app.services.cart_service import add_to_cart
        from app.utils.error_codes import ErrorCode

        result = add_to_cart(db_session, user.id, 99999)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_add_to_cart_offline_product(self, db_session, user, product_offline):
        from app.services.cart_service import add_to_cart
        from app.utils.error_codes import ErrorCode

        result = add_to_cart(db_session, user.id, product_offline.id)
        assert result["code"] == ErrorCode.PARAM_ERROR

    def test_add_to_cart_stock_not_enough(self, db_session, user, product):
        from app.services.cart_service import add_to_cart
        from app.utils.error_codes import ErrorCode

        result = add_to_cart(db_session, user.id, product.id, quantity=999)
        assert result["code"] == ErrorCode.STOCK_NOT_ENOUGH

    def test_get_cart_items(self, db_session, user, product):
        from app.services.cart_service import add_to_cart, get_cart_items

        add_to_cart(db_session, user.id, product.id, quantity=2)
        result = get_cart_items(db_session, user.id)
        assert result["code"] == 0
        assert len(result["data"]) == 1

    def test_update_cart_item(self, db_session, user, product):
        from app.services.cart_service import add_to_cart, update_cart_item

        add_result = add_to_cart(db_session, user.id, product.id)
        cart_id = add_result["data"].id

        result = update_cart_item(db_session, cart_id, user.id, quantity=5)
        assert result["code"] == 0
        assert result["data"].quantity == 5

    def test_update_cart_item_with_selected(self, db_session, user, product):
        """测试更新购物车时同时更新selected状态"""
        from app.services.cart_service import add_to_cart, update_cart_item

        add_result = add_to_cart(db_session, user.id, product.id)
        cart_id = add_result["data"].id

        result = update_cart_item(db_session, cart_id, user.id, quantity=3, selected=0)
        assert result["code"] == 0
        assert result["data"].selected == 0

    def test_update_cart_item_stock_not_enough(self, db_session, user, product_low_stock):
        """测试更新购物车数量时库存不足"""
        from app.services.cart_service import add_to_cart, update_cart_item
        from app.utils.error_codes import ErrorCode

        add_result = add_to_cart(db_session, user.id, product_low_stock.id, quantity=2)
        cart_id = add_result["data"].id

        # 尝试更新到超过库存的数量
        result = update_cart_item(db_session, cart_id, user.id, quantity=100)
        assert result["code"] == ErrorCode.STOCK_NOT_ENOUGH

    def test_update_cart_item_zero_quantity(self, db_session, user, product):
        from app.services.cart_service import add_to_cart, update_cart_item

        add_result = add_to_cart(db_session, user.id, product.id)
        cart_id = add_result["data"].id

        result = update_cart_item(db_session, cart_id, user.id, quantity=0)
        assert result["code"] == 0
        assert result["data"] is None

    def test_update_cart_item_not_found(self, db_session, user):
        from app.services.cart_service import update_cart_item
        from app.utils.error_codes import ErrorCode

        result = update_cart_item(db_session, 99999, user.id, quantity=1)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_update_cart_item_wrong_user(self, db_session, user, product):
        """测试用错误的用户ID更新购物车"""
        from app.services.cart_service import add_to_cart, update_cart_item
        from app.utils.error_codes import ErrorCode

        add_result = add_to_cart(db_session, user.id, product.id)
        cart_id = add_result["data"].id

        result = update_cart_item(db_session, cart_id, user_id=99999, quantity=5)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_remove_cart_item(self, db_session, user, product):
        from app.services.cart_service import add_to_cart, remove_cart_item

        add_result = add_to_cart(db_session, user.id, product.id)
        cart_id = add_result["data"].id

        result = remove_cart_item(db_session, cart_id, user.id)
        assert result["code"] == 0

        # 验证已删除
        from app.services.cart_service import get_cart_items
        get_result = get_cart_items(db_session, user.id)
        assert len(get_result["data"]) == 0

    def test_remove_cart_item_not_found(self, db_session, user):
        from app.services.cart_service import remove_cart_item
        from app.utils.error_codes import ErrorCode

        result = remove_cart_item(db_session, 99999, user.id)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_remove_cart_item_wrong_user(self, db_session, user, product):
        """测试用错误的用户ID删除购物车"""
        from app.services.cart_service import add_to_cart, remove_cart_item
        from app.utils.error_codes import ErrorCode

        add_result = add_to_cart(db_session, user.id, product.id)
        cart_id = add_result["data"].id

        result = remove_cart_item(db_session, cart_id, user_id=99999)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_clear_cart(self, db_session, user, product):
        from app.services.cart_service import add_to_cart, clear_cart

        add_to_cart(db_session, user.id, product.id, quantity=2)
        result = clear_cart(db_session, user.id)
        assert result["code"] == 0

        from app.services.cart_service import get_cart_items
        get_result = get_cart_items(db_session, user.id)
        assert len(get_result["data"]) == 0

    def test_get_selected_items(self, db_session, user, product):
        from app.services.cart_service import add_to_cart, get_selected_items

        add_to_cart(db_session, user.id, product.id, quantity=2)
        items = get_selected_items(db_session, user.id)
        assert len(items) == 1
        assert items[0].selected == 1

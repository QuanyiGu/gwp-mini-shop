"""商品服务层测试"""
import pytest
from decimal import Decimal

from app.models.product import Product
from app.models.category import Category
from app.utils.error_codes import ErrorCode


@pytest.fixture
def category(db_session):
    cat = Category(name="水果", icon="fruit.png", sort=1)
    db_session.add(cat)
    db_session.flush()
    return cat


@pytest.fixture
def category2(db_session):
    cat = Category(name="蜂蜜", icon="honey.png", sort=2)
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
        description="新鲜红富士苹果",
        status=1,
    )
    db_session.add(p)
    db_session.flush()
    return p


@pytest.fixture
def product2(db_session, category2):
    p = Product(
        name="天然蜂蜜",
        category_id=category2.id,
        price=Decimal("89.00"),
        stock=50,
        main_image="/images/honey.jpg",
        images="/images/honey.jpg",
        description="纯天然农家蜂蜜",
        status=1,
    )
    db_session.add(p)
    db_session.flush()
    return p


@pytest.fixture
def offline_product(db_session, category):
    p = Product(
        name="下架商品",
        category_id=category.id,
        price=Decimal("9.90"),
        stock=10,
        main_image="/images/offline.jpg",
        images="/images/offline.jpg",
        description="已下架",
        status=0,
    )
    db_session.add(p)
    db_session.flush()
    return p


@pytest.fixture
def many_products(db_session, category):
    """创建25个商品用于分页测试"""
    products = []
    for i in range(25):
        p = Product(
            name=f"测试商品{i}",
            category_id=category.id,
            price=Decimal("10.00"),
            stock=100,
            main_image=f"/images/{i}.jpg",
            images=f"/images/{i}.jpg",
            description=f"测试商品{i}",
            status=1,
        )
        db_session.add(p)
        products.append(p)
    db_session.flush()
    return products


class TestGetProducts:
    """获取商品列表测试"""

    def test_get_products_default(self, db_session, product, product2):
        """默认获取所有上架商品"""
        from app.services.product_service import get_products

        result = get_products(db_session)
        assert result["code"] == ErrorCode.SUCCESS
        assert result["data"]["total"] == 2
        assert len(result["data"]["items"]) == 2
        assert result["data"]["page"] == 1
        assert result["data"]["page_size"] == 20
        assert result["data"]["total_pages"] == 1

    def test_get_products_filter_by_category(self, db_session, product, product2, category):
        """按分类筛选商品"""
        from app.services.product_service import get_products

        result = get_products(db_session, category_id=category.id)
        assert result["code"] == ErrorCode.SUCCESS
        assert result["data"]["total"] == 1
        assert result["data"]["items"][0].id == product.id

    def test_get_products_filter_by_status(self, db_session, product, offline_product):
        """按状态筛选商品"""
        from app.services.product_service import get_products

        # 只获取上架商品（默认）
        result = get_products(db_session)
        assert result["data"]["total"] == 1

        # 获取所有状态商品
        result = get_products(db_session, status=None)
        assert result["data"]["total"] == 2

        # 只获取下架商品
        result = get_products(db_session, status=0)
        assert result["data"]["total"] == 1
        assert result["data"]["items"][0].status == 0

    def test_get_products_pagination_first_page(self, db_session, many_products):
        """分页测试 - 第一页"""
        from app.services.product_service import get_products

        result = get_products(db_session, page=1, page_size=10)
        assert result["code"] == ErrorCode.SUCCESS
        assert result["data"]["total"] == 25
        assert result["data"]["page"] == 1
        assert result["data"]["page_size"] == 10
        assert result["data"]["total_pages"] == 3
        assert len(result["data"]["items"]) == 10

    def test_get_products_pagination_second_page(self, db_session, many_products):
        """分页测试 - 第二页"""
        from app.services.product_service import get_products

        result = get_products(db_session, page=2, page_size=10)
        assert result["data"]["page"] == 2
        assert len(result["data"]["items"]) == 10

    def test_get_products_pagination_last_page(self, db_session, many_products):
        """分页测试 - 最后一页"""
        from app.services.product_service import get_products

        result = get_products(db_session, page=3, page_size=10)
        assert result["data"]["page"] == 3
        assert len(result["data"]["items"]) == 5

    def test_get_products_pagination_empty_page(self, db_session, many_products):
        """分页测试 - 超出范围的页"""
        from app.services.product_service import get_products

        result = get_products(db_session, page=10, page_size=10)
        assert result["data"]["page"] == 10
        assert len(result["data"]["items"]) == 0

    def test_get_products_order_by_created_at_desc(self, db_session, category):
        """测试按创建时间倒序排列"""
        from app.services.product_service import get_products

        # 先创建3个商品
        for i in range(3):
            p = Product(
                name=f"商品{i}",
                category_id=category.id,
                price=Decimal("10.00"),
                stock=100,
                main_image=f"/images/{i}.jpg",
                images=f"/images/{i}.jpg",
                description=f"商品{i}",
                status=1,
            )
            db_session.add(p)
        db_session.flush()

        result = get_products(db_session, page_size=10)
        names = [p.name for p in result["data"]["items"]]
        # 应该是倒序：商品2, 商品1, 商品0
        assert names == ["商品2", "商品1", "商品0"]


class TestGetProduct:
    """获取商品详情测试"""

    def test_get_product_success(self, db_session, product):
        """成功获取商品详情"""
        from app.services.product_service import get_product

        result = get_product(db_session, product.id)
        assert result["code"] == ErrorCode.SUCCESS
        assert result["data"].id == product.id
        assert result["data"].name == "红富士苹果"
        assert result["data"].price == Decimal("29.90")

    def test_get_product_not_found(self, db_session):
        """商品不存在"""
        from app.services.product_service import get_product

        result = get_product(db_session, 99999)
        assert result["code"] == ErrorCode.NOT_FOUND


class TestCreateProduct:
    """创建商品测试"""

    def test_create_product_success(self, db_session, category):
        """成功创建商品"""
        from app.services.product_service import create_product

        data = {
            "name": "新品橙子",
            "category_id": category.id,
            "price": Decimal("19.90"),
            "stock": 200,
            "main_image": "/images/orange.jpg",
            "images": "/images/orange.jpg",
            "description": "新鲜橙子",
            "status": 1,
        }
        result = create_product(db_session, data)
        assert result["code"] == ErrorCode.SUCCESS
        assert result["data"].name == "新品橙子"
        assert result["data"].price == Decimal("19.90")
        assert result["data"].stock == 200
        assert result["data"].status == 1

        # 验证数据库中存在
        from app.models.product import Product
        created = db_session.get(Product, result["data"].id)
        assert created is not None
        assert created.name == "新品橙子"


class TestUpdateProduct:
    """更新商品测试"""

    def test_update_product_success(self, db_session, product):
        """成功更新商品"""
        from app.services.product_service import update_product

        data = {
            "name": "红富士苹果（特级）",
            "price": Decimal("39.90"),
            "stock": 150,
            "description": "特级红富士苹果",
        }
        result = update_product(db_session, product.id, data)
        assert result["code"] == ErrorCode.SUCCESS
        assert result["data"].name == "红富士苹果（特级）"
        assert result["data"].price == Decimal("39.90")
        assert result["data"].stock == 150
        assert result["data"].description == "特级红富士苹果"

        # category_id 未修改，保持原值
        assert result["data"].category_id == product.category_id

    def test_update_product_not_found(self, db_session):
        """更新不存在的商品"""
        from app.services.product_service import update_product

        result = update_product(db_session, 99999, {"name": "测试"})
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_update_product_ignore_unknown_fields(self, db_session, product):
        """更新时忽略不存在的字段"""
        from app.services.product_service import update_product

        data = {
            "name": "新名称",
            "unknown_field": "应该被忽略",
        }
        result = update_product(db_session, product.id, data)
        assert result["code"] == ErrorCode.SUCCESS
        assert result["data"].name == "新名称"


class TestUpdateStock:
    """更新库存测试"""

    def test_update_stock_add(self, db_session, product):
        """增加库存"""
        from app.services.product_service import update_stock

        result = update_stock(db_session, product.id, 50)
        assert result["code"] == ErrorCode.SUCCESS
        assert result["data"].stock == 150  # 100 + 50

    def test_update_stock_subtract(self, db_session, product):
        """减少库存"""
        from app.services.product_service import update_stock

        result = update_stock(db_session, product.id, -30)
        assert result["code"] == ErrorCode.SUCCESS
        assert result["data"].stock == 70  # 100 - 30

    def test_update_stock_exact(self, db_session, product):
        """库存刚好减到0"""
        from app.services.product_service import update_stock

        result = update_stock(db_session, product.id, -100)
        assert result["code"] == ErrorCode.SUCCESS
        assert result["data"].stock == 0

    def test_update_stock_not_enough(self, db_session, product):
        """库存不足"""
        from app.services.product_service import update_stock

        result = update_stock(db_session, product.id, -200)
        assert result["code"] == ErrorCode.STOCK_NOT_ENOUGH
        # 库存未变化
        db_session.refresh(product)
        assert product.stock == 100

    def test_update_stock_not_found(self, db_session):
        """更新不存在的商品库存"""
        from app.services.product_service import update_stock

        result = update_stock(db_session, 99999, 10)
        assert result["code"] == ErrorCode.NOT_FOUND

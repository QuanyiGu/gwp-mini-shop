"""数据库初始化脚本：创建表并插入测试数据"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, get_engine
from app.models.product import Product, ProductCategory
from app.models.user import User, Address
from app.models.coupon import Coupon, UserCoupon
from app.models.order import Order, OrderItem
from app.models.cart import CartItem

from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta


def init_database():
    """初始化数据库"""
    print("🔧 开始初始化数据库...")

    # 创建引擎
    engine = get_engine()

    # 创建所有表
    print("📊 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 所有表创建完成")

    # 创建 Session
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        # 检查是否已有数据
        if db.query(Product).count() > 0:
            print("⚠️  数据库已有数据，跳过初始化")
            return

        print("📝 插入测试数据...")

        # 1. 创建商品分类
        categories = [
            ProductCategory(name="新鲜果蔬", sort=1, status=1),
            ProductCategory(name="肉禽蛋奶", sort=2, status=1),
            ProductCategory(name="粮油调味", sort=3, status=1),
            ProductCategory(name="酒水饮料", sort=4, status=1),
        ]
        db.add_all(categories)
        db.flush()

        # 2. 创建测试商品
        products = [
            Product(
                category_id=categories[0].id,
                name="GWP有机鲜牛奶 250ml*12盒",
                main_image="https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400",
                images='["https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400"]',
                description="GWP农场直供新鲜牛奶，巴氏杀菌，保留天然营养。",
                price=59.90,
                original_price=79.90,
                stock=100,
                sales=50,
                status=1,
            ),
            Product(
                category_id=categories[0].id,
                name="GWP有机蔬菜礼盒 6种鲜蔬",
                main_image="https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400",
                images='["https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400"]',
                description="精选当季6种有机蔬菜，新鲜采摘，当日配送。",
                price=88.00,
                original_price=128.00,
                stock=50,
                sales=30,
                status=1,
            ),
            Product(
                category_id=categories[1].id,
                name="GWP散养土鸡蛋 30枚",
                main_image="https://images.unsplash.com/photo-1582722872445-44dc5e720555?w=400",
                images='["https://images.unsplash.com/photo-1582722872445-44dc5e720555?w=400"]',
                description="农家散养土鸡蛋，蛋黄饱满，营养丰富。",
                price=49.90,
                original_price=69.90,
                stock=200,
                sales=120,
                status=1,
            ),
            Product(
                category_id=categories[2].id,
                name="GWP东北五常大米 5kg",
                main_image="https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400",
                images='["https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400"]',
                description="五常核心产区，一年一季，颗粒饱满。",
                price=79.00,
                original_price=99.00,
                stock=80,
                sales=65,
                status=1,
            ),
            Product(
                category_id=categories[3].id,
                name="GWP鲜榨橙汁 1L*4瓶",
                main_image="https://images.unsplash.com/photo-1621506289937-a8e4df240a05?w=400",
                images='["https://images.unsplash.com/photo-1621506289937-a8e4df240a05?w=400"]',
                description="100%鲜榨橙汁，无添加，保留天然维C。",
                price=68.00,
                original_price=88.00,
                stock=60,
                sales=40,
                status=1,
            ),
        ]
        db.add_all(products)

        # 3. 创建测试用户
        test_user = User(
            openid="test_openid_001",
            unionid="test_unionid_001",
            nickname="测试用户",
            avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=gwp",
            gender=1,
            phone="13800138000",
            status=1,
            points=1000,
            balance=500.00,
        )
        db.add(test_user)
        db.flush()

        # 4. 创建用户地址
        address = Address(
            user_id=test_user.id,
            name="张三",
            phone="13800138000",
            province="广东省",
            city="深圳市",
            district="南山区",
            detail="科技园GWP大厦1001室",
            is_default=1,
        )
        db.add(address)

        # 5. 创建优惠券
        coupons = [
            Coupon(
                name="新用户专享券",
                description="满100减20",
                type=1,
                value=20.00,
                min_amount=100.00,
                total_count=1000,
                used_count=0,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(days=30),
                status=1,
            ),
            Coupon(
                name="满减优惠券",
                description="满200减50",
                type=1,
                value=50.00,
                min_amount=200.00,
                total_count=500,
                used_count=0,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(days=30),
                status=1,
            ),
        ]
        db.add_all(coupons)
        db.flush()

        # 6. 给用户发放优惠券
        user_coupon = UserCoupon(
            user_id=test_user.id,
            coupon_id=coupons[0].id,
            status=0,
            expire_time=datetime.now() + timedelta(days=30),
        )
        db.add(user_coupon)

        db.commit()
        print("✅ 测试数据插入完成")
        print(f"   - 商品分类: {len(categories)} 个")
        print(f"   - 商品: {len(products)} 个")
        print(f"   - 测试用户: 1 个")
        print(f"   - 用户地址: 1 个")
        print(f"   - 优惠券: {len(coupons)} 个")

    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {e}")
        raise
    finally:
        db.close()

    print("🎉 数据库初始化完成！")


if __name__ == "__main__":
    init_database()

"""用户和首页 API 集成测试 - TDD RED阶段"""
from decimal import Decimal

from app.core.security import create_access_token
from app.models.banner_config import BannerConfig
from app.models.category import Category
from app.models.product import Product
from app.models.user import User


def _auth(uid: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token(uid)}"}


def _make_user(db_session, uid: str) -> User:
    user = User(
        uid=uid,
        openid=f"openid_{uid}",
        nickname="原昵称",
        avatar_url="http://avatar.old/a.png",
        phone="13800000000",
    )
    db_session.add(user)
    db_session.flush()
    return user


class TestUserInfoAPI:
    """GET /api/user/info"""

    def test_info_without_token_401(self, client):
        resp = client.get("/api/user/info")
        assert resp.status_code == 401

    def test_info_returns_current_user(self, client, db_session):
        user = _make_user(db_session, "user_info_uid")

        resp = client.get("/api/user/info", headers=_auth(user.uid))

        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["id"] == user.id
        assert body["data"]["nickname"] == "原昵称"
        assert body["data"]["avatar_url"] == "http://avatar.old/a.png"
        assert body["data"]["phone"] == "13800000000"


class TestUserUpdateAPI:
    """POST /api/user/update"""

    def test_update_without_token_401(self, client):
        resp = client.post("/api/user/update", json={"nickname": "新昵称"})
        assert resp.status_code == 401

    def test_update_current_user_partial(self, client, db_session):
        user = _make_user(db_session, "user_update_uid")

        resp = client.post(
            "/api/user/update",
            json={"nickname": "新昵称", "phone": "13900000000"},
            headers=_auth(user.uid),
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["nickname"] == "新昵称"
        assert body["data"]["phone"] == "13900000000"
        assert body["data"]["avatar_url"] == "http://avatar.old/a.png"


class TestHomeDataAPI:
    """GET /api/home/data"""

    def test_home_data_public(self, client, db_session):
        category = Category(name="苹果", icon="apple.png", sort=1)
        db_session.add(category)
        db_session.flush()
        product = Product(
            category_id=category.id,
            name="红富士",
            main_image="apple-main.png",
            images='["apple-1.png"]',
            description="甜脆",
            price=Decimal("10.00"),
            original_price=Decimal("12.00"),
            stock=100,
            sales=5,
            status=1,
        )
        banner = BannerConfig(type="home", title="首页轮播", content="banner.png", status=1)
        growth = BannerConfig(type="growth", title="生长状态", content="growth.png", status=1)
        db_session.add_all([product, banner, growth])
        db_session.flush()

        resp = client.get("/api/home/data")

        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["banners"][0]["title"] == "首页轮播"
        assert body["data"]["categories"][0]["name"] == "苹果"
        assert body["data"]["products"][0]["name"] == "红富士"
        assert body["data"]["growth_status"]["title"] == "生长状态"

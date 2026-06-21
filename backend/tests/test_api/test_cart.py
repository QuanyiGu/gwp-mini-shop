"""购物车 API 集成测试 - 验证 get_current_user 依赖接入

P1-3 任务驱动测试：
- 所有 /api/cart* 接口必须经过 Bearer Token 认证
- user_id 必须从 token 解析
"""
from decimal import Decimal

from app.core.security import create_access_token
from app.models.cart_item import CartItem
from app.models.category import Category
from app.models.product import Product
from app.models.user import User


def _auth(uid: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token(uid)}"}


def _make_user(db_session, uid: str) -> User:
    u = User(uid=uid, openid=f"cart_{uid}")
    db_session.add(u)
    db_session.flush()
    return u


def _make_product(db_session) -> Product:
    """创建一个可用商品"""
    cat = Category(name="test")
    db_session.add(cat)
    db_session.flush()
    p = Product(category_id=cat.id, name="P", price=Decimal("10"), stock=100)
    db_session.add(p)
    db_session.flush()
    return p


class TestCartGetAPI:
    """GET /api/cart"""

    def test_without_token_401(self, client):
        resp = client.get("/api/cart")
        assert resp.status_code == 401

    def test_invalid_token_401(self, client):
        resp = client.get("/api/cart", headers={"Authorization": "Bearer bad.token"})
        assert resp.status_code == 401

    def test_happy_path_empty(self, client, db_session):
        u = _make_user(db_session, "cart_get_uid")
        resp = client.get("/api/cart", headers=_auth(u.uid))
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["list"] == []


class TestCartAddAPI:
    """POST /api/cart"""

    def test_without_token_401(self, client):
        resp = client.post("/api/cart", json={"product_id": 1, "quantity": 1})
        assert resp.status_code == 401

    def test_add_and_list_isolated(self, client, db_session):
        """A 添加的商品只出现在 A 的购物车中"""
        a = _make_user(db_session, "cart_add_a")
        b = _make_user(db_session, "cart_add_b")
        p = _make_product(db_session)

        # A 添加商品
        resp_a = client.post(
            "/api/cart",
            json={"product_id": p.id, "quantity": 2},
            headers=_auth(a.uid),
        )
        assert resp_a.status_code == 200
        assert resp_a.json()["code"] == 0

        # B 的购物车为空
        resp_b = client.get("/api/cart", headers=_auth(b.uid))
        assert resp_b.status_code == 200
        assert resp_b.json()["data"]["list"] == []


class TestCartUpdateDeleteAPI:
    """PUT/DELETE /api/cart/{id}"""

    def test_update_without_token_401(self, client):
        resp = client.put("/api/cart/1", json={"quantity": 3})
        assert resp.status_code == 401

    def test_delete_without_token_401(self, client):
        resp = client.delete("/api/cart/1")
        assert resp.status_code == 401

    def test_cross_user_update_returns_not_found(self, client, db_session):
        """A 不能改 B 的购物车项"""
        a = _make_user(db_session, "cart_cu_a")
        b = _make_user(db_session, "cart_cu_b")
        p = _make_product(db_session)
        item_b = CartItem(user_id=b.id, product_id=p.id, quantity=1)
        db_session.add(item_b)
        db_session.flush()

        resp = client.put(
            f"/api/cart/{item_b.id}",
            json={"quantity": 5},
            headers=_auth(a.uid),
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == 1004  # NOT_FOUND


class TestCartSelectAllAPI:
    """POST /api/cart/select-all"""

    def test_select_all_without_token_401(self, client):
        resp = client.post("/api/cart/select-all", json={"selected": True})
        assert resp.status_code == 401

    def test_select_all_invalid_token_401(self, client):
        resp = client.post(
            "/api/cart/select-all",
            json={"selected": True},
            headers={"Authorization": "Bearer bad.token"},
        )
        assert resp.status_code == 401

    def test_select_all_success(self, client, db_session):
        u = _make_user(db_session, "cart_select_uid")
        other = _make_user(db_session, "cart_select_other")
        p1 = _make_product(db_session)
        p2 = _make_product(db_session)
        item1 = CartItem(user_id=u.id, product_id=p1.id, quantity=1, selected=0)
        item2 = CartItem(user_id=u.id, product_id=p2.id, quantity=2, selected=0)
        other_item = CartItem(user_id=other.id, product_id=p1.id, quantity=1, selected=0)
        db_session.add_all([item1, item2, other_item])
        db_session.flush()

        resp = client.post(
            "/api/cart/select-all",
            json={"selected": True},
            headers=_auth(u.uid),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 2
        assert all(item["selected"] == 1 for item in body["data"]["list"])

        db_session.refresh(other_item)
        assert other_item.selected == 0
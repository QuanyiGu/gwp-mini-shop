"""订单 API 集成测试 - 验证 get_current_user 依赖接入

P1-3 任务驱动测试：
- 所有 /api/orders* 接口必须经过 Bearer Token 认证
- user_id 必须从 token 解析
"""
from decimal import Decimal

from app.core.security import create_access_token
from app.models.address import Address
from app.models.category import Category
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User


def _auth(uid: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token(uid)}"}


def _make_user(db_session, uid: str) -> User:
    u = User(uid=uid, openid=f"order_{uid}")
    db_session.add(u)
    db_session.flush()
    return u


def _make_address(db_session, user_id: int) -> Address:
    a = Address(
        user_id=user_id, name="N", phone="P", province="P",
        city="C", district="D", detail="X", is_default=1,
    )
    db_session.add(a)
    db_session.flush()
    return a


def _make_product(db_session, stock: int = 100) -> Product:
    cat = Category(name="o-cat")
    db_session.add(cat)
    db_session.flush()
    p = Product(category_id=cat.id, name="P", price=Decimal("10"), stock=stock)
    db_session.add(p)
    db_session.flush()
    return p


def _make_order(db_session, user_id: int, order_no: str, status: int = 0) -> Order:
    o = Order(
        order_no=order_no, user_id=user_id,
        total_amount=Decimal("10"), pay_amount=Decimal("10"),
        address_name="N", address_phone="P", address_detail="D",
        status=status,
    )
    db_session.add(o)
    db_session.flush()
    return o


def _add_order_item(db_session, order: Order, product: Product, quantity: int = 1) -> OrderItem:
    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        product_name=product.name,
        product_image=product.main_image,
        price=product.price,
        quantity=quantity,
        total_price=product.price * quantity,
    )
    db_session.add(item)
    db_session.flush()
    return item


class TestOrderListAPI:
    """GET /api/orders"""

    def test_without_token_401(self, client):
        resp = client.get("/api/orders")
        assert resp.status_code == 401

    def test_invalid_token_401(self, client):
        resp = client.get("/api/orders", headers={"Authorization": "Bearer bad"})
        assert resp.status_code == 401

    def test_list_only_own_orders(self, client, db_session):
        """A 只能看到自己的订单"""
        a = _make_user(db_session, "ord_list_a")
        b = _make_user(db_session, "ord_list_b")
        db_session.add(Order(
            order_no="OA_1", user_id=a.id,
            total_amount=Decimal("10"), pay_amount=Decimal("10"),
            address_name="N", address_phone="P", address_detail="D",
            status=0,
        ))
        db_session.add(Order(
            order_no="OB_1", user_id=b.id,
            total_amount=Decimal("20"), pay_amount=Decimal("20"),
            address_name="N", address_phone="P", address_detail="D",
            status=0,
        ))
        db_session.flush()

        resp = client.get("/api/orders", headers=_auth(a.uid))
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        order_nos = [o["order_no"] for o in body["data"]["list"]]
        assert "OA_1" in order_nos
        assert "OB_1" not in order_nos


class TestOrderCreateAPI:
    """POST /api/orders"""

    def test_without_token_401(self, client):
        resp = client.post("/api/orders", json={"address_id": 1, "items": []})
        assert resp.status_code == 401

    def test_create_writes_token_user_id(self, client, db_session):
        u = _make_user(db_session, "ord_cr_uid")
        addr = _make_address(db_session, u.id)
        p = _make_product(db_session)

        resp = client.post(
            "/api/orders",
            json={
                "address_id": addr.id,
                "items": [{"product_id": p.id, "quantity": 1}],
            },
            headers=_auth(u.uid),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["user_id"] == u.id


class TestOrderDetailAPI:
    """GET /api/orders/{id}"""

    def test_without_token_401(self, client):
        resp = client.get("/api/orders/1")
        assert resp.status_code == 401

    def test_cross_user_returns_order_not_found(self, client, db_session):
        a = _make_user(db_session, "ord_det_a")
        b = _make_user(db_session, "ord_det_b")
        o_b = Order(
            order_no="ODB_1", user_id=b.id,
            total_amount=Decimal("10"), pay_amount=Decimal("10"),
            address_name="N", address_phone="P", address_detail="D",
            status=0,
        )
        db_session.add(o_b)
        db_session.flush()

        resp = client.get(f"/api/orders/{o_b.id}", headers=_auth(a.uid))
        assert resp.status_code == 200
        assert resp.json()["code"] == 2002  # ORDER_NOT_FOUND


class TestOrderPayTrackingAPI:
    """POST /api/orders/{id}/pay 与 GET /api/orders/{id}/tracking"""

    def test_pay_without_token_401(self, client):
        resp = client.post("/api/orders/1/pay")
        assert resp.status_code == 401

    def test_tracking_without_token_401(self, client):
        resp = client.get("/api/orders/1/tracking")
        assert resp.status_code == 401


class TestOrderCancelAPI:
    """POST /api/orders/{order_no}/cancel"""

    def test_cancel_without_token_401(self, client):
        resp = client.post("/api/orders/OC_1/cancel", json={"reason": "不想买了"})
        assert resp.status_code == 401

    def test_cancel_invalid_token_401(self, client):
        resp = client.post(
            "/api/orders/OC_1/cancel",
            json={"reason": "bad"},
            headers={"Authorization": "Bearer bad"},
        )
        assert resp.status_code == 401

    def test_cancel_success(self, client, db_session):
        u = _make_user(db_session, "ord_cancel_uid")
        p = _make_product(db_session, stock=8)
        order = _make_order(db_session, u.id, "OC_SUCCESS", status=0)
        _add_order_item(db_session, order, p, quantity=2)

        resp = client.post(
            f"/api/orders/{order.order_no}/cancel",
            json={"reason": "不想买了"},
            headers=_auth(u.uid),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["status"] == 4

        db_session.refresh(p)
        assert p.stock == 10

    def test_cancel_cross_user(self, client, db_session):
        a = _make_user(db_session, "ord_cancel_a")
        b = _make_user(db_session, "ord_cancel_b")
        order_b = _make_order(db_session, b.id, "OC_CROSS", status=0)

        resp = client.post(
            f"/api/orders/{order_b.order_no}/cancel",
            json={"reason": "hack"},
            headers=_auth(a.uid),
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == 2002  # ORDER_NOT_FOUND


class TestOrderConfirmAPI:
    """POST /api/orders/{order_no}/confirm"""

    def test_confirm_without_token_401(self, client):
        resp = client.post("/api/orders/OF_1/confirm")
        assert resp.status_code == 401

    def test_confirm_invalid_token_401(self, client):
        resp = client.post(
            "/api/orders/OF_1/confirm",
            headers={"Authorization": "Bearer bad"},
        )
        assert resp.status_code == 401

    def test_confirm_success(self, client, db_session):
        u = _make_user(db_session, "ord_confirm_uid")
        order = _make_order(db_session, u.id, "OF_SUCCESS", status=2)

        resp = client.post(
            f"/api/orders/{order.order_no}/confirm",
            headers=_auth(u.uid),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["status"] == 3
        assert body["data"]["pay_time"] is not None

    def test_confirm_cross_user(self, client, db_session):
        a = _make_user(db_session, "ord_confirm_a")
        b = _make_user(db_session, "ord_confirm_b")
        order_b = _make_order(db_session, b.id, "OF_CROSS", status=2)

        resp = client.post(
            f"/api/orders/{order_b.order_no}/confirm",
            headers=_auth(a.uid),
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == 2002  # ORDER_NOT_FOUND


class TestOrderRefundAPI:
    """POST /api/orders/{order_no}/refund"""

    def test_refund_without_token_401(self, client):
        resp = client.post("/api/orders/OR_1/refund")
        assert resp.status_code == 401

    def test_refund_invalid_token_401(self, client):
        resp = client.post(
            "/api/orders/OR_1/refund",
            headers={"Authorization": "Bearer bad"},
        )
        assert resp.status_code == 401

    def test_refund_success(self, client, db_session):
        u = _make_user(db_session, "ord_refund_uid")
        order = _make_order(db_session, u.id, "OR_SUCCESS", status=1)

        resp = client.post(
            f"/api/orders/{order.order_no}/refund",
            headers=_auth(u.uid),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["status"] == 6

    def test_refund_cross_user(self, client, db_session):
        a = _make_user(db_session, "ord_refund_a")
        b = _make_user(db_session, "ord_refund_b")
        order_b = _make_order(db_session, b.id, "OR_CROSS", status=1)

        resp = client.post(
            f"/api/orders/{order_b.order_no}/refund",
            headers=_auth(a.uid),
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == 2002  # ORDER_NOT_FOUND
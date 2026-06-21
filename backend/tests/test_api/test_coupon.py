"""优惠券 API 集成测试 - 验证 get_current_user 依赖接入"""
from datetime import datetime
from decimal import Decimal

from app.core.security import create_access_token
from app.models.coupon import Coupon
from app.models.user import User


def _auth(uid: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token(uid)}"}


def _make_user(db_session, uid: str) -> User:
    u = User(uid=uid, openid=f"coupon_{uid}")
    db_session.add(u)
    db_session.flush()
    return u


class TestCouponListAPI:
    """GET /api/coupons"""

    def test_without_token_401(self, client):
        resp = client.get("/api/coupons")
        assert resp.status_code == 401

    def test_invalid_token_401(self, client):
        resp = client.get("/api/coupons", headers={"Authorization": "Bearer x"})
        assert resp.status_code == 401

    def test_list_only_own_coupons(self, client, db_session):
        a = _make_user(db_session, "cp_a")
        b = _make_user(db_session, "cp_b")
        db_session.add(Coupon(
            code="A_COUP", user_id=a.id, type=1,
            discount=Decimal("5"), min_amount=Decimal("10"),
            status=0, expires_at=datetime(2099, 1, 1),
        ))
        db_session.add(Coupon(
            code="B_COUP", user_id=b.id, type=1,
            discount=Decimal("8"), min_amount=Decimal("20"),
            status=0, expires_at=datetime(2099, 1, 1),
        ))
        db_session.flush()

        resp = client.get("/api/coupons", headers=_auth(a.uid))
        assert resp.status_code == 200
        body = resp.json()
        codes = [c["code"] for c in body["data"]]
        assert "A_COUP" in codes
        assert "B_COUP" not in codes


class TestCouponApplyAPI:
    """GET /api/coupons/apply"""

    def test_without_token_401(self, client):
        resp = client.get("/api/coupons/apply", params={"order_amount": 50})
        assert resp.status_code == 401


class TestCouponClaimAPI:
    """POST /api/coupons/claim"""

    def test_without_token_401(self, client):
        resp = client.post("/api/coupons/claim", params={"invite_code": "X"})
        assert resp.status_code == 401

    def test_claim_without_code_returns_param_error(self, client, db_session):
        u = _make_user(db_session, "cp_claim_uid")
        resp = client.post("/api/coupons/claim", headers=_auth(u.uid))
        assert resp.status_code == 200
        assert resp.json()["code"] == 1001  # PARAM_ERROR
"""支付 API 集成测试"""
from decimal import Decimal
from unittest.mock import patch

from app.core.security import create_access_token
from app.models.order import Order
from app.models.user import User


class TestPrepayAPI:
    """POST /api/pay/prepare（需要 Authorization Bearer Token）"""

    API_URL = "/api/pay/prepare"

    def _auth_headers(self, uid: str) -> dict:
        return {"Authorization": f"Bearer {create_access_token(uid)}"}

    def test_prepay_success(self, client, db_session):
        """正常预下单（带 token）"""
        u = User(uid="prepay_uid", openid="prepay_openid")
        db_session.add(u)
        db_session.flush()

        o = Order(
            order_no="PREP_API_001", user_id=u.id,
            total_amount=Decimal("100"), pay_amount=Decimal("90"),
            address_name="N", address_phone="P", address_detail="D",
            status=Order.STATUS_PENDING,
        )
        db_session.add(o)
        db_session.flush()

        from app.services import pay_service

        fake_wx = {
            "return_code": "SUCCESS", "result_code": "SUCCESS",
            "prepay_id": "wx_pid", "nonce_str": "n",
        }
        with patch.object(pay_service, "wx_unified_order", return_value=fake_wx):
            resp = client.post(
                self.API_URL,
                json={"order_no": o.order_no},
                headers=self._auth_headers(u.uid),
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert "paySign" in data["data"]

    def test_prepay_order_not_found(self, client, db_session):
        u = User(uid="prepay_404_uid", openid="prepay_404_openid")
        db_session.add(u)
        db_session.flush()

        resp = client.post(
            self.API_URL,
            json={"order_no": "NON_EXIST"},
            headers=self._auth_headers(u.uid),
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == 2002

    def test_prepay_without_token(self, client):
        """不带 token → 401"""
        resp = client.post(self.API_URL, json={"order_no": "x"})
        assert resp.status_code == 401

    def test_prepay_invalid_token(self, client):
        """token 无效 → 401"""
        resp = client.post(
            self.API_URL,
            json={"order_no": "x"},
            headers={"Authorization": "Bearer not.a.real.token"},
        )
        assert resp.status_code == 401


class TestPayNotifyAPI:
    """POST /api/pay/notify"""

    API_URL = "/api/pay/notify"

    def test_notify_success(self, client, db_session):
        """正常回调 → 返回 XML <return_code>SUCCESS</return_code>"""
        u = User(uid="notify_api_uid", openid="notify_api_openid")
        db_session.add(u)
        db_session.flush()

        o = Order(
            order_no="NOTIFY_API_001", user_id=u.id,
            total_amount=Decimal("50"), pay_amount=Decimal("50"),
            address_name="N", address_phone="P", address_detail="D",
            status=Order.STATUS_PENDING,
        )
        db_session.add(o)
        db_session.flush()

        from app.utils.wxpay import build_sign, dict_to_xml

        params = {
            "return_code": "SUCCESS", "result_code": "SUCCESS",
            "out_trade_no": o.order_no, "transaction_id": "t_id",
            "total_fee": "5000", "nonce_str": "n",
        }
        params["sign"] = build_sign(params, key="test_pay_key")
        xml_body = dict_to_xml(params)

        from app.services import pay_service
        with patch.object(pay_service, "_get_pay_key", return_value="test_pay_key"):
            resp = client.post(
                self.API_URL,
                data=xml_body,
                headers={"Content-Type": "application/xml"},
            )

        assert resp.status_code == 200
        assert b"<return_code><![CDATA[SUCCESS]]></return_code>" in resp.content

    def test_notify_invalid_xml(self, client):
        """无效 XML → 返回 FAIL"""
        resp = client.post(
            self.API_URL,
            data="not xml",
            headers={"Content-Type": "text/plain"},
        )
        assert resp.status_code == 200
        assert b"<return_code><![CDATA[FAIL]]></return_code>" in resp.content
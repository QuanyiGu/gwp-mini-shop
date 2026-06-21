"""微信支付服务层测试 - 预下单 / 回调处理"""
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pytest

from app.models.order import Order
from app.models.user import User
from app.utils.error_codes import ErrorCode


# ---------- 公共 fixtures ----------

@pytest.fixture
def pay_user(db_session):
    u = User(uid="pay_uid", openid="pay_openid", nickname="支付用户")
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def pending_order(db_session, pay_user):
    """待付款订单"""
    o = Order(
        order_no="ORDER_PEND_001",
        user_id=pay_user.id,
        total_amount=Decimal("100.00"),
        pay_amount=Decimal("88.00"),
        address_name="张三",
        address_phone="13800000000",
        address_detail="北京市朝阳区某路1号",
        status=Order.STATUS_PENDING,
    )
    db_session.add(o)
    db_session.flush()
    return o


@pytest.fixture
def paid_order(db_session, pay_user):
    """已付款订单（用于幂等测试）"""
    o = Order(
        order_no="ORDER_PAID_001",
        user_id=pay_user.id,
        total_amount=Decimal("50.00"),
        pay_amount=Decimal("50.00"),
        address_name="李四",
        address_phone="13900000000",
        address_detail="上海市浦东新区某路2号",
        status=Order.STATUS_PAID,
    )
    db_session.add(o)
    db_session.flush()
    return o


# ---------- 签名工具 ----------

class TestWxpaySign:
    """微信支付签名生成与验证"""

    def test_build_sign_keys_sorted(self):
        from app.utils.wxpay import build_sign

        params = {"b": "2", "a": "1", "c": "3"}
        sign = build_sign(params, key="testkey")
        # 不同顺序生成相同签名
        sign2 = build_sign({"c": "3", "a": "1", "b": "2"}, key="testkey")
        assert sign == sign2
        assert len(sign) == 32  # MD5 hex

    def test_build_sign_excludes_sign_and_empty(self):
        from app.utils.wxpay import build_sign

        with_sign = build_sign(
            {"a": "1", "sign": "anything", "b": ""},  # b 空值，sign 字段都应排除
            key="testkey",
        )
        without = build_sign({"a": "1"}, key="testkey")
        assert with_sign == without

    def test_verify_sign_true(self):
        from app.utils.wxpay import build_sign, verify_sign

        params = {"a": "1", "b": "2"}
        params["sign"] = build_sign(params, key="testkey")
        assert verify_sign(params, key="testkey") is True

    def test_verify_sign_false(self):
        from app.utils.wxpay import verify_sign

        bad = {"a": "1", "b": "2", "sign": "ffffffffffffffffffffffffffffffff"}
        assert verify_sign(bad, key="testkey") is False


class TestWxpayXml:
    """XML 序列化/反序列化"""

    def test_dict_to_xml_roundtrip(self):
        from app.utils.wxpay import dict_to_xml, xml_to_dict

        d = {"appid": "wx123", "mch_id": "1900000000", "nonce_str": "abc"}
        xml = dict_to_xml(d)
        assert "<xml>" in xml and "</xml>" in xml
        parsed = xml_to_dict(xml)
        assert parsed == d

    def test_xml_to_dict_with_cdata(self):
        from app.utils.wxpay import xml_to_dict

        xml = "<xml><return_code><![CDATA[SUCCESS]]></return_code><openid>oId123</openid></xml>"
        d = xml_to_dict(xml)
        assert d["return_code"] == "SUCCESS"
        assert d["openid"] == "oId123"


# ---------- 预下单 ----------

class TestCreatePrepayOrder:
    """create_prepay_order(db, user_id, order_no)"""

    def test_prepay_success(self, db_session, pay_user, pending_order):
        """正常预下单：返回 wx.requestPayment 5 元素"""
        from app.services import pay_service

        fake_wx_resp = {
            "return_code": "SUCCESS",
            "result_code": "SUCCESS",
            "prepay_id": "wx_prepay_id_xxx",
            "nonce_str": "wx_nonce_xxx",
        }

        with patch.object(pay_service, "wx_unified_order", return_value=fake_wx_resp):
            result = pay_service.create_prepay_order(
                db_session, user_id=pay_user.id, order_no=pending_order.order_no
            )

        assert result["code"] == ErrorCode.SUCCESS
        data = result["data"]
        # wx.requestPayment 必须的 5 个字段
        assert "timeStamp" in data
        assert "nonceStr" in data
        assert "package" in data and data["package"].startswith("prepay_id=")
        assert data["signType"] == "MD5"
        assert "paySign" in data and len(data["paySign"]) == 32

    def test_prepay_order_not_found(self, db_session, pay_user):
        from app.services import pay_service

        result = pay_service.create_prepay_order(
            db_session, user_id=pay_user.id, order_no="NOT_EXIST"
        )
        assert result["code"] == ErrorCode.ORDER_NOT_FOUND

    def test_prepay_order_not_belong_to_user(self, db_session, pending_order):
        """订单不属于该用户"""
        from app.services import pay_service

        result = pay_service.create_prepay_order(
            db_session, user_id=99999, order_no=pending_order.order_no
        )
        assert result["code"] == ErrorCode.NO_PERMISSION

    def test_prepay_order_status_not_pending(self, db_session, pay_user, paid_order):
        """订单已付款，不能再预下单"""
        from app.services import pay_service

        result = pay_service.create_prepay_order(
            db_session, user_id=pay_user.id, order_no=paid_order.order_no
        )
        assert result["code"] == ErrorCode.ORDER_STATUS_ERROR

    def test_prepay_wechat_return_fail(self, db_session, pay_user, pending_order):
        """微信侧返回 return_code=FAIL"""
        from app.services import pay_service

        fake_resp = {
            "return_code": "FAIL",
            "return_msg": "system error",
        }
        with patch.object(pay_service, "wx_unified_order", return_value=fake_resp):
            result = pay_service.create_prepay_order(
                db_session, user_id=pay_user.id, order_no=pending_order.order_no
            )
        assert result["code"] == ErrorCode.PAY_FAILED


# ---------- 回调处理 ----------

class TestHandlePayNotify:
    """handle_pay_notify(db, xml_body)"""

    def _build_notify_xml(self, order_no: str, key: str = "test_pay_key",
                          return_code: str = "SUCCESS",
                          result_code: str = "SUCCESS") -> str:
        """构造一个签名正确的微信回调 XML"""
        from app.utils.wxpay import build_sign, dict_to_xml

        params = {
            "return_code": return_code,
            "result_code": result_code,
            "out_trade_no": order_no,
            "transaction_id": "wx_tx_id_001",
            "total_fee": "8800",
            "nonce_str": "callback_nonce",
        }
        params["sign"] = build_sign(params, key=key)
        return dict_to_xml(params)

    def test_notify_success_marks_order_paid(self, db_session, pending_order):
        """回调成功 → 订单状态 0→1"""
        from app.services import pay_service

        xml = self._build_notify_xml(pending_order.order_no)
        with patch.object(pay_service, "_get_pay_key", return_value="test_pay_key"):
            result = pay_service.handle_pay_notify(db_session, xml)

        assert result["return_code"] == "SUCCESS"
        db_session.refresh(pending_order)
        assert pending_order.status == Order.STATUS_PAID

    def test_notify_idempotent_on_paid_order(self, db_session, paid_order):
        """已付款订单二次回调 → 直接返回 SUCCESS，不再变更"""
        from app.services import pay_service

        xml = self._build_notify_xml(paid_order.order_no)
        with patch.object(pay_service, "_get_pay_key", return_value="test_pay_key"):
            result = pay_service.handle_pay_notify(db_session, xml)

        assert result["return_code"] == "SUCCESS"
        db_session.refresh(paid_order)
        assert paid_order.status == Order.STATUS_PAID  # 状态不变

    def test_notify_invalid_sign(self, db_session, pending_order):
        """签名错误 → 返回 FAIL，订单状态不变"""
        from app.services import pay_service
        from app.utils.wxpay import dict_to_xml

        bad_xml = dict_to_xml({
            "return_code": "SUCCESS",
            "result_code": "SUCCESS",
            "out_trade_no": pending_order.order_no,
            "total_fee": "8800",
            "nonce_str": "x",
            "sign": "ffffffffffffffffffffffffffffffff",
        })
        with patch.object(pay_service, "_get_pay_key", return_value="test_pay_key"):
            result = pay_service.handle_pay_notify(db_session, bad_xml)

        assert result["return_code"] == "FAIL"
        db_session.refresh(pending_order)
        assert pending_order.status == Order.STATUS_PENDING

    def test_notify_return_code_fail(self, db_session, pending_order):
        """微信回调 return_code=FAIL（业务侧不处理，但要回 SUCCESS 防止重试）"""
        from app.services import pay_service

        xml = self._build_notify_xml(pending_order.order_no, return_code="FAIL")
        with patch.object(pay_service, "_get_pay_key", return_value="test_pay_key"):
            result = pay_service.handle_pay_notify(db_session, xml)

        # 业务上失败回调订单状态不变
        db_session.refresh(pending_order)
        assert pending_order.status == Order.STATUS_PENDING

    def test_notify_order_not_found(self, db_session):
        """订单号不存在 → 返回 FAIL"""
        from app.services import pay_service

        xml = self._build_notify_xml("NOT_EXIST_ORDER")
        with patch.object(pay_service, "_get_pay_key", return_value="test_pay_key"):
            result = pay_service.handle_pay_notify(db_session, xml)

        assert result["return_code"] == "FAIL"

    def test_notify_order_cancelled_state(self, db_session, pay_user):
        """订单已取消，不应再标记为已付款"""
        from app.services import pay_service

        cancelled = Order(
            order_no="ORDER_CANCEL_001",
            user_id=pay_user.id,
            total_amount=Decimal("10"),
            pay_amount=Decimal("10"),
            address_name="A",
            address_phone="1",
            address_detail="x",
            status=Order.STATUS_CANCELLED,
        )
        db_session.add(cancelled)
        db_session.flush()

        xml = self._build_notify_xml(cancelled.order_no)
        with patch.object(pay_service, "_get_pay_key", return_value="test_pay_key"):
            result = pay_service.handle_pay_notify(db_session, xml)

        # 已取消订单不允许变更，但回 SUCCESS 防止微信重试（业务侧已有日志记录）
        # 这里要求 return_code=SUCCESS（防重试），但订单状态保持 CANCELLED
        assert result["return_code"] == "SUCCESS"
        db_session.refresh(cancelled)
        assert cancelled.status == Order.STATUS_CANCELLED

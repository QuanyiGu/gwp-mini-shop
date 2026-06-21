"""邀请服务层测试"""
import pytest

from app.models.user import User


@pytest.fixture
def user1(db_session):
    u = User(uid="inviter_uid", nickname="邀请人")
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def user2(db_session):
    u = User(uid="invitee_uid", nickname="被邀请人")
    db_session.add(u)
    db_session.flush()
    return u


class TestInviteService:
    def test_generate_invite_code(self, db_session, user1):
        from app.services.invite_service import create_invite_code

        result = create_invite_code(db_session, user1.id)
        assert result["code"] == 0
        assert len(result["data"]["invite_code"]) == 8

    def test_generate_invite_code_unique(self, db_session, user1):
        from app.services.invite_service import create_invite_code

        result1 = create_invite_code(db_session, user1.id)
        result2 = create_invite_code(db_session, user1.id)
        assert result1["data"]["invite_code"] != result2["data"]["invite_code"]

    def test_use_invite_code(self, db_session, user1, user2):
        from app.services.invite_service import create_invite_code, use_invite_code

        code_result = create_invite_code(db_session, user1.id)
        invite_code = code_result["data"]["invite_code"]

        result = use_invite_code(db_session, user2.id, invite_code)
        assert result["code"] == 0
        assert result["data"].invitee_id == user2.id

    def test_use_invite_code_not_found(self, db_session, user2):
        from app.services.invite_service import use_invite_code
        from app.utils.error_codes import ErrorCode

        result = use_invite_code(db_session, user2.id, "INVALID")
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_use_invite_code_self_invite(self, db_session, user1):
        from app.services.invite_service import create_invite_code, use_invite_code
        from app.utils.error_codes import ErrorCode

        code_result = create_invite_code(db_session, user1.id)
        invite_code = code_result["data"]["invite_code"]

        result = use_invite_code(db_session, user1.id, invite_code)
        assert result["code"] == ErrorCode.PARAM_ERROR

    def test_link_invite_to_order(self, db_session, user1, user2):
        from app.services.invite_service import create_invite_code, use_invite_code, link_invite_to_order
        from app.models.order import Order
        from datetime import datetime

        code_result = create_invite_code(db_session, user1.id)
        invite_code = code_result["data"]["invite_code"]
        use_result = use_invite_code(db_session, user2.id, invite_code)
        invite_id = use_result["data"].id

        # 创建真实订单用于测试关联
        order = Order(
            order_no="TEST_ORDER_12345",
            user_id=user1.id,
            total_amount=100,
            pay_amount=100,
            address_name="测试地址",
            address_phone="13800000000",
            address_detail="测试详细地址",
            status=1,
            created_at=datetime.now(),
        )
        db_session.add(order)
        db_session.flush()

        result = link_invite_to_order(db_session, invite_id, order.id)
        assert result["code"] == 0
        assert result["data"].order_id == order.id

    def test_link_invite_to_order_not_found(self, db_session, user1):
        """测试关联不存在的邀请记录"""
        from app.services.invite_service import link_invite_to_order
        from app.utils.error_codes import ErrorCode

        result = link_invite_to_order(db_session, 99999, 1)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_send_coupon_to_inviter(self, db_session, user1, user2):
        from app.services.invite_service import create_invite_code, use_invite_code, send_coupon_to_inviter

        code_result = create_invite_code(db_session, user1.id)
        invite_code = code_result["data"]["invite_code"]
        use_invite_code(db_session, user2.id, invite_code)

        result = send_coupon_to_inviter(db_session, user1.id)
        assert result["code"] == 0
        assert result["data"].user_id == user1.id
        assert result["data"].discount == 10  # 默认邀请优惠券金额

    def test_send_coupon_to_inviter_no_invite(self, db_session, user1):
        """测试没有可发放优惠券的邀请记录"""
        from app.services.invite_service import send_coupon_to_inviter
        from app.utils.error_codes import ErrorCode

        # user1没有任何邀请记录
        result = send_coupon_to_inviter(db_session, user1.id)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_get_invite_history(self, db_session, user1, user2):
        from app.services.invite_service import create_invite_code, use_invite_code, get_invite_history

        code_result = create_invite_code(db_session, user1.id)
        invite_code = code_result["data"]["invite_code"]
        use_invite_code(db_session, user2.id, invite_code)

        result = get_invite_history(db_session, user1.id)
        assert result["code"] == 0
        assert len(result["data"]) == 1
        assert result["data"][0]["invitee_nickname"] == "被邀请人"

    def test_get_invite_history_with_order(self, db_session, user1, user2):
        """测试获取邀请历史包含订单信息"""
        from app.services.invite_service import (
            create_invite_code, use_invite_code,
            link_invite_to_order, get_invite_history
        )
        from app.models.order import Order
        from datetime import datetime

        code_result = create_invite_code(db_session, user1.id)
        invite_code = code_result["data"]["invite_code"]
        use_result = use_invite_code(db_session, user2.id, invite_code)
        invite_id = use_result["data"].id

        order = Order(
            order_no="TEST_ORDER_67890",
            user_id=user1.id,
            total_amount=200,
            pay_amount=200,
            address_name="测试地址",
            address_phone="13800000000",
            address_detail="测试详细地址",
            status=1,
            created_at=datetime.now(),
        )
        db_session.add(order)
        db_session.flush()

        link_invite_to_order(db_session, invite_id, order.id)

        result = get_invite_history(db_session, user1.id)
        assert result["code"] == 0
        assert len(result["data"]) == 1
        assert result["data"][0]["order_id"] == order.id

"""优惠券服务层测试"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.user import User
from app.models.coupon import Coupon


@pytest.fixture
def user(db_session):
    u = User(uid="test_coupon_uid", nickname="测试用户")
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def other_user(db_session):
    """另一个用户"""
    u = User(uid="other_coupon_uid", nickname="其他用户")
    db_session.add(u)
    db_session.flush()
    return u


@pytest.fixture
def coupon(db_session, user):
    c = Coupon(
        code="TEST123",
        user_id=user.id,
        discount=Decimal("10.00"),
        min_amount=Decimal("50.00"),
        status=0,
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db_session.add(c)
    db_session.flush()
    return c


@pytest.fixture
def unclaimed_coupon(db_session):
    """未被领取的优惠券"""
    c = Coupon(
        code="UNCLAIMED456",
        user_id=0,  # 0表示未被领取
        discount=Decimal("20.00"),
        min_amount=Decimal("100.00"),
        status=0,
        expires_at=datetime.utcnow() + timedelta(days=30),
    )
    db_session.add(c)
    db_session.flush()
    return c


@pytest.fixture
def expired_coupon(db_session, user):
    c = Coupon(
        code="EXPIRED789",
        user_id=user.id,
        discount=Decimal("20.00"),
        min_amount=Decimal("100.00"),
        status=0,
        expires_at=datetime.utcnow() - timedelta(days=1),  # 已过期
    )
    db_session.add(c)
    db_session.flush()
    return c


class TestCouponService:
    def test_claim_coupon(self, db_session, user, unclaimed_coupon):
        from app.services.coupon_service import claim_coupon

        result = claim_coupon(db_session, user.id, "UNCLAIMED456")
        assert result["code"] == 0
        assert result["data"].user_id == user.id

    def test_claim_coupon_not_found(self, db_session, user):
        from app.services.coupon_service import claim_coupon
        from app.utils.error_codes import ErrorCode

        result = claim_coupon(db_session, user.id, "NOTEXIST")
        assert result["code"] == ErrorCode.COUPON_NOT_FOUND

    def test_claim_coupon_already_claimed_by_other(self, db_session, user, other_user):
        """测试优惠券已被其他用户领取"""
        from app.services.coupon_service import claim_coupon
        from app.utils.error_codes import ErrorCode

        # 创建被other_user领取的优惠券
        coupon = Coupon(
            code="OTHER_CLAIMED",
            user_id=other_user.id,
            discount=Decimal("15.00"),
            min_amount=Decimal("50.00"),
            status=0,
            expires_at=datetime.utcnow() + timedelta(days=30),
        )
        db_session.add(coupon)
        db_session.flush()

        # 当前用户尝试领取
        result = claim_coupon(db_session, user.id, "OTHER_CLAIMED")
        assert result["code"] == ErrorCode.COUPON_NOT_FOUND

    def test_claim_coupon_already_used(self, db_session, user, coupon):
        from app.services.coupon_service import claim_coupon
        from app.utils.error_codes import ErrorCode

        coupon.user_id = user.id
        coupon.status = 1  # 已使用
        db_session.flush()

        result = claim_coupon(db_session, user.id, "TEST123")
        assert result["code"] == ErrorCode.COUPON_USED

    def test_claim_expired_coupon(self, db_session, user, expired_coupon):
        from app.services.coupon_service import claim_coupon
        from app.utils.error_codes import ErrorCode

        result = claim_coupon(db_session, user.id, "EXPIRED789")
        assert result["code"] == ErrorCode.COUPON_EXPIRED

    def test_get_user_coupons(self, db_session, user, coupon):
        from app.services.coupon_service import get_user_coupons

        result = get_user_coupons(db_session, user.id)
        assert result["code"] == 0
        assert len(result["data"]) == 1

    def test_get_user_coupons_by_status(self, db_session, user, coupon):
        from app.services.coupon_service import get_user_coupons

        coupon.status = 1  # 已使用
        db_session.flush()

        result = get_user_coupons(db_session, user.id, status=1)
        assert result["code"] == 0
        assert len(result["data"]) == 1
        assert result["data"][0].status == 1

    def test_get_applicable_coupons(self, db_session, user, coupon):
        from app.services.coupon_service import get_applicable_coupons

        result = get_applicable_coupons(db_session, user.id, Decimal("100.00"))
        assert result["code"] == 0
        assert len(result["data"]) == 1

    def test_get_applicable_coupons_amount_too_low(self, db_session, user, coupon):
        from app.services.coupon_service import get_applicable_coupons

        # 订单金额低于min_amount
        result = get_applicable_coupons(db_session, user.id, Decimal("30.00"))
        assert result["code"] == 0
        assert len(result["data"]) == 0

    def test_use_coupon(self, db_session, user, coupon):
        from app.services.coupon_service import use_coupon

        result = use_coupon(db_session, coupon.id, user.id)
        assert result["code"] == 0
        assert result["data"].status == 1

    def test_use_coupon_not_found(self, db_session, user):
        """测试使用不存在的优惠券"""
        from app.services.coupon_service import use_coupon
        from app.utils.error_codes import ErrorCode

        result = use_coupon(db_session, 99999, user.id)
        assert result["code"] == ErrorCode.COUPON_NOT_FOUND

    def test_use_coupon_wrong_user(self, db_session, user, other_user, coupon):
        """测试使用别人的优惠券"""
        from app.services.coupon_service import use_coupon
        from app.utils.error_codes import ErrorCode

        # coupon属于user，但用other_user的ID去使用
        result = use_coupon(db_session, coupon.id, other_user.id)
        assert result["code"] == ErrorCode.COUPON_NOT_FOUND

    def test_use_coupon_already_used(self, db_session, user, coupon):
        from app.services.coupon_service import use_coupon
        from app.utils.error_codes import ErrorCode

        coupon.status = 1
        db_session.flush()

        result = use_coupon(db_session, coupon.id, user.id)
        assert result["code"] == ErrorCode.COUPON_USED

    def test_use_coupon_expired(self, db_session, user, expired_coupon):
        """测试使用已过期的优惠券"""
        from app.services.coupon_service import use_coupon
        from app.utils.error_codes import ErrorCode

        result = use_coupon(db_session, expired_coupon.id, user.id)
        assert result["code"] == ErrorCode.COUPON_EXPIRED
        # 验证状态被更新为已过期
        db_session.refresh(expired_coupon)
        assert expired_coupon.status == 2

    def test_return_coupon(self, db_session, user, coupon):
        from app.services.coupon_service import return_coupon

        coupon.status = 1  # 已使用
        db_session.flush()

        result = return_coupon(db_session, coupon.id, user.id)
        assert result["code"] == 0
        assert result["data"].status == 0

    def test_return_coupon_not_found(self, db_session, user):
        """测试退回不存在的优惠券"""
        from app.services.coupon_service import return_coupon
        from app.utils.error_codes import ErrorCode

        result = return_coupon(db_session, 99999, user.id)
        assert result["code"] == ErrorCode.COUPON_NOT_FOUND

    def test_return_coupon_wrong_user(self, db_session, user, other_user, coupon):
        """测试退回别人的优惠券"""
        from app.services.coupon_service import return_coupon
        from app.utils.error_codes import ErrorCode

        # coupon属于user，但用other_user的ID去退回
        result = return_coupon(db_session, coupon.id, other_user.id)
        assert result["code"] == ErrorCode.COUPON_NOT_FOUND

    def test_return_coupon_not_used(self, db_session, user, coupon):
        """测试退回未使用的优惠券（状态不变）"""
        from app.services.coupon_service import return_coupon

        coupon.status = 0  # 未使用
        db_session.flush()

        result = return_coupon(db_session, coupon.id, user.id)
        assert result["code"] == 0
        assert result["data"].status == 0  # 仍然是未使用

    def test_create_coupon(self, db_session, user):
        from app.services.coupon_service import create_coupon

        result = create_coupon(
            db_session,
            code="NEWCOUPON",
            discount=Decimal("15.00"),
            min_amount=Decimal("80.00"),
            user_id=user.id,
        )
        assert result["code"] == 0
        assert result["data"].code == "NEWCOUPON"

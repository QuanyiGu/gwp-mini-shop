"""用户服务层测试"""
import pytest

from app.models.user import User


@pytest.fixture
def user(db_session):
    u = User(uid="test_user_svc", nickname="测试用户", openid="wx_test_openid")
    db_session.add(u)
    db_session.flush()
    return u


class TestUserService:
    def test_get_user(self, db_session, user):
        from app.services.user_service import get_user

        result = get_user(db_session, user.id)
        assert result["code"] == 0
        assert result["data"].nickname == "测试用户"

    def test_get_user_not_found(self, db_session):
        from app.services.user_service import get_user
        from app.utils.error_codes import ErrorCode

        result = get_user(db_session, 99999)
        assert result["code"] == ErrorCode.USER_NOT_FOUND

    def test_get_user_by_openid(self, db_session, user):
        from app.services.user_service import get_user_by_openid

        found = get_user_by_openid(db_session, "wx_test_openid")
        assert found is not None
        assert found.nickname == "测试用户"

    def test_get_user_by_openid_not_found(self, db_session):
        from app.services.user_service import get_user_by_openid

        found = get_user_by_openid(db_session, "not_exist")
        assert found is None

    def test_get_user_by_uid(self, db_session, user):
        from app.services.user_service import get_user_by_uid

        found = get_user_by_uid(db_session, "test_user_svc")
        assert found is not None
        assert found.nickname == "测试用户"

    def test_create_user(self, db_session):
        from app.services.user_service import create_user

        user = create_user(
            db_session,
            openid="wx_new_openid",
            unionid="wx_union_123",
            nickname="新用户",
            avatar_url="http://avatar.com/1.jpg",
            phone="13900000001",
        )
        assert user.uid is not None
        assert user.nickname == "新用户"
        assert user.openid == "wx_new_openid"

    def test_get_or_create_user_by_openid_existing(self, db_session, user):
        from app.services.user_service import get_or_create_user_by_openid

        found = get_or_create_user_by_openid(db_session, "wx_test_openid")
        assert found.id == user.id

    def test_get_or_create_user_by_openid_new(self, db_session):
        from app.services.user_service import get_or_create_user_by_openid

        user = get_or_create_user_by_openid(
            db_session,
            openid="wx_brand_new",
            unionid="wx_union_new",
            nickname="全新用户",
        )
        assert user.openid == "wx_brand_new"
        assert user.nickname == "全新用户"

    def test_update_user(self, db_session, user):
        from app.services.user_service import update_user

        result = update_user(
            db_session,
            user.id,
            nickname="修改后的昵称",
            avatar_url="http://new.avatar.com/2.jpg",
        )
        assert result["code"] == 0
        assert result["data"].nickname == "修改后的昵称"
        assert result["data"].avatar_url == "http://new.avatar.com/2.jpg"

    def test_update_user_partial(self, db_session, user):
        from app.services.user_service import update_user

        original_avatar = user.avatar_url
        result = update_user(db_session, user.id, nickname="只改昵称")
        assert result["code"] == 0
        assert result["data"].nickname == "只改昵称"
        assert result["data"].avatar_url == original_avatar

    def test_update_user_not_found(self, db_session):
        """测试更新不存在的用户"""
        from app.services.user_service import update_user
        from app.utils.error_codes import ErrorCode

        result = update_user(db_session, 99999, nickname="新昵称")
        assert result["code"] == ErrorCode.USER_NOT_FOUND

    def test_update_user_phone(self, db_session, user):
        """测试更新用户手机号"""
        from app.services.user_service import update_user

        result = update_user(db_session, user.id, phone="13999998888")
        assert result["code"] == 0
        assert result["data"].phone == "13999998888"

    def test_update_user_all_fields(self, db_session, user):
        """测试更新用户所有字段"""
        from app.services.user_service import update_user

        result = update_user(
            db_session,
            user.id,
            nickname="完整修改",
            avatar_url="http://full.avatar.com/3.jpg",
            phone="13800138001",
        )
        assert result["code"] == 0
        assert result["data"].nickname == "完整修改"
        assert result["data"].avatar_url == "http://full.avatar.com/3.jpg"
        assert result["data"].phone == "13800138001"

    def test_bind_phone(self, db_session, user):
        from app.services.user_service import bind_phone

        result = bind_phone(db_session, user.id, "13999998888")
        assert result["code"] == 0
        assert result["data"].phone == "13999998888"

    def test_bind_phone_user_not_found(self, db_session):
        from app.services.user_service import bind_phone
        from app.utils.error_codes import ErrorCode

        result = bind_phone(db_session, 99999, "13999998888")
        assert result["code"] == ErrorCode.USER_NOT_FOUND

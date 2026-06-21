"""认证服务层测试 - 微信登录 / Token 刷新"""
from unittest.mock import patch, MagicMock

import pytest

from app.models.user import User
from app.utils.error_codes import ErrorCode


# ---------- 公共 mock 工具 ----------

def _make_wx_success(openid: str = "wx_openid_abc",
                    unionid: str = "wx_union_xyz",
                    session_key: str = "skey_123"):
    """构造一个 code2session 成功返回"""
    return {
        "openid": openid,
        "unionid": unionid,
        "session_key": session_key,
    }


def _make_wx_error(errcode: int = 40029, errmsg: str = "invalid code"):
    """构造一个 code2session 失败返回"""
    return {"errcode": errcode, "errmsg": errmsg}


# ---------- code2session 工具函数测试 ----------

class TestCode2Session:
    """直接调用微信 code2session 的工具函数"""

    def test_code2session_success(self):
        from app.services import auth_service

        mock_resp = MagicMock()
        mock_resp.json.return_value = _make_wx_success()
        mock_resp.raise_for_status = MagicMock()

        with patch("app.services.auth_service.httpx.get", return_value=mock_resp) as mock_get:
            data = auth_service.code2session("any_code")

        assert data["openid"] == "wx_openid_abc"
        assert data["unionid"] == "wx_union_xyz"
        assert data["session_key"] == "skey_123"
        mock_get.assert_called_once()

    def test_code2session_wechat_returns_errcode(self):
        from app.services import auth_service

        mock_resp = MagicMock()
        mock_resp.json.return_value = _make_wx_error()
        mock_resp.raise_for_status = MagicMock()

        with patch("app.services.auth_service.httpx.get", return_value=mock_resp):
            with pytest.raises(auth_service.WxLoginError) as exc_info:
                auth_service.code2session("bad_code")

        assert exc_info.value.errcode == 40029


# ---------- wx_login 业务流程测试 ----------

class TestWxLogin:
    """微信登录主流程"""

    def test_wx_login_new_user(self, db_session):
        """新用户登录：自动创建 User，返回 token 和 user_info"""
        from app.services import auth_service

        with patch.object(auth_service, "code2session",
                          return_value=_make_wx_success(openid="new_openid")):
            result = auth_service.wx_login(
                db_session,
                code="valid_code",
                nickname="新用户",
                avatar_url="http://avatar/new.jpg",
            )

        assert result["code"] == ErrorCode.SUCCESS
        data = result["data"]
        assert "access_token" in data and data["access_token"]
        assert "refresh_token" in data and data["refresh_token"]
        assert data["user_info"]["nickname"] == "新用户"
        assert data["user_info"]["avatar_url"] == "http://avatar/new.jpg"

        # 数据库中应已落库
        created = db_session.query(User).filter(User.openid == "new_openid").first()
        assert created is not None
        assert created.nickname == "新用户"

    def test_wx_login_existing_user_not_duplicated(self, db_session):
        """老用户再次登录：不重复创建，且昵称/头像应保留原值（除非显式更新）"""
        from app.services import auth_service

        old = User(uid="old_uid", openid="old_openid", nickname="老用户",
                   avatar_url="http://avatar/old.jpg")
        db_session.add(old)
        db_session.flush()

        with patch.object(auth_service, "code2session",
                          return_value=_make_wx_success(openid="old_openid")):
            result = auth_service.wx_login(db_session, code="valid_code")

        assert result["code"] == ErrorCode.SUCCESS
        # 不重复创建
        count = db_session.query(User).filter(User.openid == "old_openid").count()
        assert count == 1
        # 返回的用户信息应是已有的
        assert result["data"]["user_info"]["nickname"] == "老用户"

    def test_wx_login_empty_code(self, db_session):
        """空 code 直接返回参数错误，不调用微信 API"""
        from app.services import auth_service

        with patch.object(auth_service, "code2session") as mock_c2s:
            result = auth_service.wx_login(db_session, code="")

        assert result["code"] == ErrorCode.PARAM_ERROR
        mock_c2s.assert_not_called()

    def test_wx_login_wechat_error_returns_sign_error(self, db_session):
        """微信侧返回 errcode：转为 SIGN_ERROR"""
        from app.services import auth_service

        def _raise(_code):
            raise auth_service.WxLoginError(errcode=40029, errmsg="invalid code")

        with patch.object(auth_service, "code2session", side_effect=_raise):
            result = auth_service.wx_login(db_session, code="bad_code")

        assert result["code"] == ErrorCode.SIGN_ERROR

    def test_wx_login_token_is_decodable(self, db_session):
        """签发的 access_token 可解码出 user uid"""
        from app.services import auth_service
        from app.core.security import decode_token

        with patch.object(auth_service, "code2session",
                          return_value=_make_wx_success(openid="decode_openid")):
            result = auth_service.wx_login(db_session, code="c", nickname="X")

        payload = decode_token(result["data"]["access_token"])
        assert payload is not None
        assert payload["type"] == "access"
        # sub 是 user.uid
        user = db_session.query(User).filter(User.openid == "decode_openid").first()
        assert payload["sub"] == user.uid


# ---------- refresh_access_token 测试 ----------

class TestRefreshAccessToken:
    """刷新 access_token"""

    def test_refresh_success(self, db_session):
        from app.services import auth_service
        from app.core.security import create_refresh_token, decode_token

        u = User(uid="refresh_uid", openid="refresh_openid", nickname="X")
        db_session.add(u)
        db_session.flush()

        refresh = create_refresh_token(u.uid)
        result = auth_service.refresh_access_token(db_session, refresh)

        assert result["code"] == ErrorCode.SUCCESS
        new_access = result["data"]["access_token"]
        payload = decode_token(new_access)
        assert payload["sub"] == u.uid
        assert payload["type"] == "access"

    def test_refresh_invalid_token(self, db_session):
        from app.services import auth_service

        result = auth_service.refresh_access_token(db_session, "not.a.valid.token")
        assert result["code"] == ErrorCode.TOKEN_EXPIRED

    def test_refresh_wrong_token_type(self, db_session):
        """access_token 不能用来刷新"""
        from app.services import auth_service
        from app.core.security import create_access_token

        u = User(uid="wrong_type_uid", openid="wt_openid")
        db_session.add(u)
        db_session.flush()

        access = create_access_token(u.uid)
        result = auth_service.refresh_access_token(db_session, access)
        assert result["code"] == ErrorCode.TOKEN_EXPIRED

    def test_refresh_user_not_exists(self, db_session):
        """refresh_token 解出的 uid 在数据库不存在"""
        from app.services import auth_service
        from app.core.security import create_refresh_token

        refresh = create_refresh_token("uid_that_never_existed")
        result = auth_service.refresh_access_token(db_session, refresh)
        assert result["code"] == ErrorCode.USER_NOT_FOUND

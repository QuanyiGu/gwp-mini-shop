"""认证 API 集成测试 - /api/auth/*"""
from unittest.mock import patch

from app.models.user import User
from app.core.security import create_refresh_token


class TestWxLoginAPI:
    """POST /api/auth/wxlogin"""

    API_URL = "/api/auth/wxlogin"

    def test_wxlogin_success(self, client, db_session):
        """正常登录返回 token 和 user_info"""
        from app.services import auth_service

        payload = {"code": "valid_code", "nickname": "新用户", "avatar_url": "http://a.jpg"}

        with patch.object(auth_service, "code2session",
                          return_value={"openid": "api_openid_001", "unionid": "api_union",
                                        "session_key": "skey"}):
            resp = client.post(self.API_URL, json=payload)

        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["access_token"]
        assert data["data"]["refresh_token"]
        assert data["data"]["user_info"]["nickname"] == "新用户"

    def test_wxlogin_required_code(self, client):
        """code 为空返回参数错误"""
        resp = client.post(self.API_URL, json={"code": ""})
        assert resp.status_code == 200
        assert resp.json()["code"] == 1001

    def test_wxlogin_missing_code_key(self, client):
        """不传 code 返回 422 验证错误"""
        resp = client.post(self.API_URL, json={"nickname": "X"})
        assert resp.status_code == 422

    def test_wxlogin_wechat_error(self, client, db_session):
        """微信接口异常时返回 SIGN_ERROR"""
        from app.services import auth_service

        with patch.object(auth_service, "code2session",
                          side_effect=auth_service.WxLoginError(40029, "invalid code")):
            resp = client.post(self.API_URL, json={"code": "bad"})

        assert resp.status_code == 200
        assert resp.json()["code"] == 1002


class TestRefreshTokenAPI:
    """POST /api/auth/refresh"""

    API_URL = "/api/auth/refresh"

    def test_refresh_success(self, client, db_session):
        """正常刷新返回新 access_token"""
        u = User(uid="api_ref_uid", openid="api_ref_openid")
        db_session.add(u)
        db_session.flush()

        refresh_token = create_refresh_token(u.uid)
        resp = client.post(self.API_URL, json={"refresh_token": refresh_token})

        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["access_token"]

    def test_refresh_invalid(self, client):
        """无效 token 返回 TOKEN_EXPIRED"""
        resp = client.post(self.API_URL, json={"refresh_token": "bad.token.xxx"})
        assert resp.status_code == 200
        assert resp.json()["code"] == 3002

    def test_refresh_missing(self, client):
        """不传 refresh_token 返回 422"""
        resp = client.post(self.API_URL, json={})
        assert resp.status_code == 422
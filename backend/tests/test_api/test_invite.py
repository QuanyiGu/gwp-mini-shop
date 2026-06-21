"""邀请 API 集成测试 - 验证 get_current_user 依赖接入"""
from app.core.security import create_access_token
from app.models.user import User


def _auth(uid: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token(uid)}"}


def _make_user(db_session, uid: str) -> User:
    u = User(uid=uid, openid=f"inv_{uid}")
    db_session.add(u)
    db_session.flush()
    return u


class TestInviteGenerateAPI:
    """POST /api/invites/generate"""

    def test_without_token_401(self, client):
        resp = client.post("/api/invites/generate")
        assert resp.status_code == 401

    def test_invalid_token_401(self, client):
        resp = client.post(
            "/api/invites/generate",
            headers={"Authorization": "Bearer bad"},
        )
        assert resp.status_code == 401

    def test_generate_success(self, client, db_session):
        u = _make_user(db_session, "inv_gen_uid")
        resp = client.post("/api/invites/generate", headers=_auth(u.uid))
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["invite_code"].startswith("INVITE_")


class TestInviteHistoryAPI:
    """GET /api/invites/history"""

    def test_without_token_401(self, client):
        resp = client.get("/api/invites/history")
        assert resp.status_code == 401

    def test_history_empty(self, client, db_session):
        u = _make_user(db_session, "inv_hist_uid")
        resp = client.get("/api/invites/history", headers=_auth(u.uid))
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"] == []
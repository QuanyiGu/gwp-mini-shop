"""地址 API 集成测试 - 验证 get_current_user 依赖接入

P1-3 任务驱动测试：
- 所有 /api/addresses 接口必须经过 Bearer Token 认证
- user_id 必须从 token 解析，不能信任前端入参
- 不同用户的数据严格隔离
"""
from app.core.security import create_access_token
from app.models.address import Address
from app.models.user import User


def _auth(uid: str) -> dict:
    return {"Authorization": f"Bearer {create_access_token(uid)}"}


def _make_user(db_session, uid: str) -> User:
    u = User(uid=uid, openid=f"openid_{uid}")
    db_session.add(u)
    db_session.flush()
    return u


class TestAddressListAPI:
    """GET /api/addresses"""

    def test_list_without_token_401(self, client):
        resp = client.get("/api/addresses")
        assert resp.status_code == 401

    def test_list_invalid_token_401(self, client):
        resp = client.get("/api/addresses", headers={"Authorization": "Bearer bad.token"})
        assert resp.status_code == 401

    def test_list_returns_only_own_addresses(self, client, db_session):
        """用户 A 只能看到自己的地址，看不到 B 的"""
        a = _make_user(db_session, "addr_uid_a")
        b = _make_user(db_session, "addr_uid_b")
        db_session.add(Address(
            user_id=a.id, name="NA", phone="111", province="P", city="C",
            district="D", detail="DA", is_default=1,
        ))
        db_session.add(Address(
            user_id=b.id, name="NB", phone="222", province="P", city="C",
            district="D", detail="DB", is_default=1,
        ))
        db_session.flush()

        resp = client.get("/api/addresses", headers=_auth(a.uid))
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert len(body["data"]) == 1
        assert body["data"][0]["name"] == "NA"


class TestAddressCreateAPI:
    """POST /api/addresses"""

    def test_create_without_token_401(self, client):
        resp = client.post("/api/addresses", json={
            "name": "n", "phone": "p", "province": "P",
            "city": "C", "district": "D", "detail": "X",
        })
        assert resp.status_code == 401

    def test_create_writes_token_user_id(self, client, db_session):
        """创建的地址 user_id 必须等于 token 解析出的用户 id"""
        u = _make_user(db_session, "addr_create_uid")
        resp = client.post(
            "/api/addresses",
            json={
                "name": "n", "phone": "p", "province": "P",
                "city": "C", "district": "D", "detail": "X",
            },
            headers=_auth(u.uid),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["user_id"] == u.id


class TestAddressUpdateDeleteAPI:
    """PUT/DELETE /api/addresses/{id}"""

    def test_update_cross_user_returns_not_found(self, client, db_session):
        """A 不能改 B 的地址 → 返回 NOT_FOUND"""
        a = _make_user(db_session, "addr_up_a")
        b = _make_user(db_session, "addr_up_b")
        addr_b = Address(
            user_id=b.id, name="B", phone="b", province="P", city="C",
            district="D", detail="DB", is_default=0,
        )
        db_session.add(addr_b)
        db_session.flush()

        resp = client.put(
            f"/api/addresses/{addr_b.id}",
            json={"name": "hack"},
            headers=_auth(a.uid),
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == 1004  # NOT_FOUND

    def test_delete_without_token_401(self, client):
        resp = client.delete("/api/addresses/1")
        assert resp.status_code == 401


class TestAddressDefaultAPI:
    """GET /api/addresses/default"""

    def test_default_without_token_401(self, client):
        resp = client.get("/api/addresses/default")
        assert resp.status_code == 401

    def test_default_invalid_token_401(self, client):
        resp = client.get(
            "/api/addresses/default",
            headers={"Authorization": "Bearer bad.token"},
        )
        assert resp.status_code == 401

    def test_default_success(self, client, db_session):
        u = _make_user(db_session, "addr_default_uid")
        first = Address(
            user_id=u.id, name="FIRST", phone="111", province="P", city="C",
            district="D", detail="D1", is_default=0,
        )
        default = Address(
            user_id=u.id, name="DEFAULT", phone="222", province="P", city="C",
            district="D", detail="D2", is_default=1,
        )
        db_session.add_all([first, default])
        db_session.flush()

        resp = client.get("/api/addresses/default", headers=_auth(u.uid))
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["name"] == "DEFAULT"

    def test_default_fallback_first_and_not_found(self, client, db_session):
        u = _make_user(db_session, "addr_default_fallback")
        empty = _make_user(db_session, "addr_default_empty")
        first = Address(
            user_id=u.id, name="FIRST", phone="111", province="P", city="C",
            district="D", detail="D1", is_default=0,
        )
        second = Address(
            user_id=u.id, name="SECOND", phone="222", province="P", city="C",
            district="D", detail="D2", is_default=0,
        )
        db_session.add_all([first, second])
        db_session.flush()

        resp = client.get("/api/addresses/default", headers=_auth(u.uid))
        assert resp.status_code == 200
        assert resp.json()["code"] == 0
        assert resp.json()["data"]["name"] == "FIRST"

        resp_empty = client.get("/api/addresses/default", headers=_auth(empty.uid))
        assert resp_empty.status_code == 200
        assert resp_empty.json()["code"] == 1004
        assert resp_empty.json()["message"] == "未找到地址"

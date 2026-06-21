"""收货地址服务层测试"""
import pytest

from app.models.user import User


@pytest.fixture
def user(db_session):
    u = User(uid="test_uid_addr", nickname="测试用户")
    db_session.add(u)
    db_session.flush()
    return u


class TestAddressService:
    def test_create_address(self, db_session, user):
        from app.services.address_service import create_address

        result = create_address(
            db_session,
            user_id=user.id,
            name="张三",
            phone="13800138000",
            province="广东省",
            city="深圳市",
            district="南山区",
            detail="科技园1号",
            is_default=1,
        )
        assert result["code"] == 0
        assert result["data"].name == "张三"
        assert result["data"].is_default == 1

    def test_create_address_sets_only_one_default(self, db_session, user):
        from app.services.address_service import create_address

        addr1 = create_address(
            db_session, user.id, "地址1", "13800000001",
            "广东", "深圳", "南山", "detail1", is_default=1
        )
        addr2 = create_address(
            db_session, user.id, "地址2", "13800000002",
            "广东", "广州", "天河", "detail2", is_default=1
        )

        assert addr1["data"].is_default == 0
        assert addr2["data"].is_default == 1

    def test_get_addresses(self, db_session, user):
        from app.services.address_service import create_address, get_addresses

        create_address(db_session, user.id, "地址1", "13800000001",
                       "广东", "深圳", "南山", "detail1")
        create_address(db_session, user.id, "地址2", "13800000002",
                       "广东", "广州", "天河", "detail2")

        result = get_addresses(db_session, user.id)
        assert result["code"] == 0
        assert len(result["data"]) == 2

    def test_get_address(self, db_session, user):
        from app.services.address_service import create_address, get_address

        created = create_address(db_session, user.id, "地址1", "13800000001",
                                 "广东", "深圳", "南山", "detail1")
        addr_id = created["data"].id

        result = get_address(db_session, addr_id, user.id)
        assert result["code"] == 0
        assert result["data"].name == "地址1"

    def test_get_address_not_found(self, db_session, user):
        from app.services.address_service import get_address
        from app.utils.error_codes import ErrorCode

        result = get_address(db_session, 99999, user.id)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_get_address_wrong_user(self, db_session, user):
        from app.services.address_service import create_address, get_address
        from app.utils.error_codes import ErrorCode

        created = create_address(db_session, user.id, "地址1", "13800000001",
                                 "广东", "深圳", "南山", "detail1")
        addr_id = created["data"].id

        result = get_address(db_session, addr_id, user_id=99999)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_update_address(self, db_session, user):
        from app.services.address_service import create_address, update_address

        created = create_address(db_session, user.id, "地址1", "13800000001",
                                 "广东", "深圳", "南山", "detail1")
        addr_id = created["data"].id

        result = update_address(db_session, addr_id, user.id, name="新名字")
        assert result["code"] == 0
        assert result["data"].name == "新名字"

    def test_update_address_set_default(self, db_session, user):
        from app.services.address_service import create_address, update_address

        addr1 = create_address(db_session, user.id, "地址1", "13800000001",
                                "广东", "深圳", "南山", "detail1", is_default=1)
        addr2 = create_address(db_session, user.id, "地址2", "13800000002",
                                "广东", "广州", "天河", "detail2")

        update_address(db_session, addr2["data"].id, user.id, is_default=1)

        # 刷新
        db_session.expire_all()
        import app.models.address
        addr1_result = db_session.get(app.models.address.Address, addr1["data"].id)
        addr2_result = db_session.get(app.models.address.Address, addr2["data"].id)

        assert addr1_result.is_default == 0
        assert addr2_result.is_default == 1

    def test_update_address_wrong_user(self, db_session, user):
        from app.services.address_service import create_address, update_address
        from app.utils.error_codes import ErrorCode

        created = create_address(db_session, user.id, "地址1", "13800000001",
                                 "广东", "深圳", "南山", "detail1")
        addr_id = created["data"].id

        # 用另一个用户ID更新，应该返回 NOT_FOUND
        result = update_address(db_session, addr_id, user_id=99999, name="新名字")
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_update_address_not_found(self, db_session, user):
        from app.services.address_service import update_address
        from app.utils.error_codes import ErrorCode

        result = update_address(db_session, 99999, user.id, name="新名字")
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_delete_address(self, db_session, user):
        from app.services.address_service import create_address, delete_address

        created = create_address(db_session, user.id, "地址1", "13800000001",
                                 "广东", "深圳", "南山", "detail1")
        addr_id = created["data"].id

        result = delete_address(db_session, addr_id, user.id)
        assert result["code"] == 0

    def test_delete_address_wrong_user(self, db_session, user):
        from app.services.address_service import create_address, delete_address
        from app.utils.error_codes import ErrorCode

        created = create_address(db_session, user.id, "地址1", "13800000001",
                                 "广东", "深圳", "南山", "detail1")
        addr_id = created["data"].id

        # 用另一个用户ID删除，应该返回 NOT_FOUND
        result = delete_address(db_session, addr_id, user_id=99999)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_delete_address_not_found(self, db_session, user):
        from app.services.address_service import delete_address
        from app.utils.error_codes import ErrorCode

        result = delete_address(db_session, 99999, user.id)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_set_default_address(self, db_session, user):
        from app.services.address_service import create_address, set_default_address

        created = create_address(db_session, user.id, "地址1", "13800000001",
                                 "广东", "深圳", "南山", "detail1", is_default=1)
        addr_id = created["data"].id

        result = set_default_address(db_session, addr_id, user.id)
        assert result["code"] == 0
        assert result["data"].is_default == 1

    def test_set_default_address_wrong_user(self, db_session, user):
        from app.services.address_service import create_address, set_default_address
        from app.utils.error_codes import ErrorCode

        created = create_address(db_session, user.id, "地址1", "13800000001",
                                 "广东", "深圳", "南山", "detail1", is_default=1)
        addr_id = created["data"].id

        # 用另一个用户ID设置默认，应该返回 NOT_FOUND
        result = set_default_address(db_session, addr_id, user_id=99999)
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_set_default_address_not_found(self, db_session, user):
        from app.services.address_service import set_default_address
        from app.utils.error_codes import ErrorCode

        result = set_default_address(db_session, 99999, user.id)
        assert result["code"] == ErrorCode.NOT_FOUND

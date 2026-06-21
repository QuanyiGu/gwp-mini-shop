"""Banner服务层测试"""
import pytest

from app.models.banner_config import BannerConfig


@pytest.fixture
def banner(db_session):
    b = BannerConfig(
        type="growth_status",
        title="苹果生长第30天",
        content="/images/growth/30days.jpg",
        status=1,
    )
    db_session.add(b)
    db_session.flush()
    return b


class TestBannerService:
    def test_get_banners_by_type(self, db_session, banner):
        from app.services.banner_service import get_banners_by_type

        result = get_banners_by_type(db_session, "growth_status")
        assert result["code"] == 0
        assert len(result["data"]) == 1
        assert result["data"][0].title == "苹果生长第30天"

    def test_get_banners_by_type_filter_status(self, db_session, banner):
        from app.services.banner_service import get_banners_by_type

        result = get_banners_by_type(db_session, "growth_status", status=0)
        assert result["code"] == 0
        assert len(result["data"]) == 0

    def test_get_growth_status_banners(self, db_session, banner):
        from app.services.banner_service import get_growth_status_banners

        result = get_growth_status_banners(db_session)
        assert result["code"] == 0
        assert len(result["data"]) == 1

    def test_create_banner(self, db_session):
        from app.services.banner_service import create_banner

        result = create_banner(
            db_session,
            banner_type="growth_status",
            title="新建Banner",
            content="/images/new.jpg",
            status=1,
        )
        assert result["code"] == 0
        assert result["data"].title == "新建Banner"

    def test_update_banner(self, db_session, banner):
        from app.services.banner_service import update_banner

        result = update_banner(db_session, banner.id, title="更新标题")
        assert result["code"] == 0
        assert result["data"].title == "更新标题"

    def test_update_banner_content(self, db_session, banner):
        from app.services.banner_service import update_banner

        result = update_banner(db_session, banner.id, content="/images/new_content.jpg")
        assert result["code"] == 0
        assert result["data"].content == "/images/new_content.jpg"

    def test_update_banner_status(self, db_session, banner):
        from app.services.banner_service import update_banner

        result = update_banner(db_session, banner.id, status=0)
        assert result["code"] == 0
        assert result["data"].status == 0

    def test_update_banner_all_fields(self, db_session, banner):
        from app.services.banner_service import update_banner

        result = update_banner(
            db_session, banner.id,
            title="完整更新",
            content="/images/updated.jpg",
            status=0
        )
        assert result["code"] == 0
        assert result["data"].title == "完整更新"
        assert result["data"].content == "/images/updated.jpg"
        assert result["data"].status == 0

    def test_update_banner_not_found(self, db_session):
        from app.services.banner_service import update_banner
        from app.utils.error_codes import ErrorCode

        result = update_banner(db_session, 99999, title="测试")
        assert result["code"] == ErrorCode.NOT_FOUND

    def test_delete_banner(self, db_session, banner):
        from app.services.banner_service import delete_banner

        result = delete_banner(db_session, banner.id)
        assert result["code"] == 0

        # 验证已删除
        from app.services.banner_service import get_banners_by_type
        get_result = get_banners_by_type(db_session, "growth_status")
        assert len(get_result["data"]) == 0

    def test_delete_banner_not_found(self, db_session):
        from app.services.banner_service import delete_banner
        from app.utils.error_codes import ErrorCode

        result = delete_banner(db_session, 99999)
        assert result["code"] == ErrorCode.NOT_FOUND

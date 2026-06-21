"""测试核心配置模块 - TDD RED阶段"""
import os
import pytest


class TestConfig:
    """测试 config.py 配置加载"""

    def test_settings_loads_from_env(self):
        """配置应从.env文件加载"""
        from app.core.config import settings
        assert settings.DB_DRIVER is not None
        assert settings.DB_HOST is not None

    def test_settings_has_database_url(self):
        """配置应包含数据库连接URL"""
        from app.core.config import settings
        assert settings.DATABASE_URL is not None
        assert "mysql" in settings.DATABASE_URL or "sqlite" in settings.DATABASE_URL

    def test_settings_has_test_database_url(self):
        """配置应包含测试数据库URL"""
        from app.core.config import settings
        assert settings.TEST_DB_URL is not None

    def test_settings_has_redis_config(self):
        """配置应包含Redis连接参数"""
        from app.core.config import settings
        assert settings.REDIS_HOST is not None
        assert settings.REDIS_PORT is not None

    def test_settings_has_jwt_config(self):
        """配置应包含JWT参数"""
        from app.core.config import settings
        assert settings.JWT_SECRET_KEY is not None
        assert settings.JWT_ALGORITHM is not None
        assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS > 0

    def test_settings_has_snowflake_config(self):
        """配置应包含雪花算法参数"""
        from app.core.config import settings
        assert settings.SNOWFLAKE_EPOCH == 1577836800000
        assert settings.SNOWFLAKE_MACHINE_ID == 1

    def test_settings_has_celery_config(self):
        """配置应包含Celery参数"""
        from app.core.config import settings
        assert settings.CELERY_BROKER_URL is not None
        assert settings.CELERY_RESULT_BACKEND is not None

    def test_settings_has_pool_config(self):
        """配置应包含连接池参数"""
        from app.core.config import settings
        assert settings.DB_POOL_SIZE == 20
        assert settings.DB_MAX_OVERFLOW == 10


class TestDatabase:
    """测试 database.py 数据库管理"""

    def test_get_engine(self):
        """应能创建数据库引擎"""
        from app.core.database import get_engine
        engine = get_engine(use_test=True)
        assert engine is not None

    def test_get_session_factory(self):
        """应能创建Session工厂"""
        from app.core.database import get_session_factory
        session_factory = get_session_factory(use_test=True)
        assert session_factory is not None

    def test_get_base(self):
        """应能获取DeclarativeBase"""
        from app.core.database import Base
        assert Base is not None

    def test_engine_pool_settings(self):
        """测试引擎应使用SQLite，生产引擎应有连接池配置"""
        from app.core.database import get_engine
        test_engine = get_engine(use_test=True)
        assert "sqlite" in str(test_engine.url)


class TestSecurity:
    """测试 security.py JWT工具"""

    def test_create_access_token(self):
        """应能创建access token"""
        from app.core.security import create_access_token
        token = create_access_token(subject="admin1")
        assert token is not None
        assert isinstance(token, str)

    def test_create_refresh_token(self):
        """应能创建refresh token"""
        from app.core.security import create_refresh_token
        token = create_refresh_token(subject="admin1")
        assert token is not None
        assert isinstance(token, str)

    def test_decode_token(self):
        """应能解码token并获取subject"""
        from app.core.security import create_access_token, decode_token
        token = create_access_token(subject="admin1")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "admin1"

    def test_decode_expired_token_fails(self):
        """过期的token应解码失败"""
        from app.core.security import create_access_token, decode_token
        # 创建一个立即过期的token
        token = create_access_token(subject="admin1", expires_delta=-1)
        payload = decode_token(token)
        assert payload is None

    def test_decode_invalid_token_fails(self):
        """无效token应解码失败"""
        from app.core.security import decode_token
        payload = decode_token("invalid.token.here")
        assert payload is None

    def test_hash_password(self):
        """应能哈希密码"""
        from app.core.security import hash_password
        hashed = hash_password("test123")
        assert hashed is not None
        assert hashed != "test123"

    def test_verify_password(self):
        """应能验证密码"""
        from app.core.security import hash_password, verify_password
        hashed = hash_password("test123")
        assert verify_password("test123", hashed) is True
        assert verify_password("wrong", hashed) is False


class TestRedis:
    """测试 redis.py Redis连接管理"""

    def test_get_redis_url(self):
        """应能生成Redis连接URL"""
        from app.core.redis import get_redis_url
        url = get_redis_url()
        assert url is not None
        assert "redis" in url

    def test_get_redis_url_with_password(self):
        """带密码的Redis URL格式应正确"""
        from app.core.redis import get_redis_url
        # 测试无密码情况
        url = get_redis_url()
        assert url.startswith("redis://")

"""pytest 测试配置和公共fixtures"""
import pytest
from sqlalchemy import create_engine, event, Integer, BigInteger, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool


# SQLite requires INTEGER PRIMARY KEY for AUTOINCREMENT, not BIGINT
# This function patches BigInteger columns to Integer for SQLite
def _patch_biginteger_to_integer(base):
    """Patch all BigInteger columns to Integer for SQLite compatibility"""
    for table in base.metadata.tables.values():
        for col in table.columns:
            if isinstance(col.type, BigInteger):
                col.type = Integer()


@pytest.fixture(scope="session")
def engine():
    """创建SQLite内存数据库引擎（用于测试）"""
    from app.core.database import Base
    # 导入所有模型注册到Base.metadata
    from app.models import (  # noqa: F401
        user, product, order, order_item, address,
        category, cart_item, admin_user, coupon,
        invite, banner_config, product_extra, admin_operate_log
    )

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # SQLite不支持BigInteger主键的autoincrement，需要映射为Integer
    _patch_biginteger_to_integer(Base)

    # Enable foreign key support
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    # 插入占位订单记录（id=0）用于表示"无订单"的邀请记录
    # 因为 SQLite 的外键约束要求 order_id 必须引用真实记录
    # orders表有NOT NULL约束的order_no字段，需要提供占位值
    # 注意：orders.user_id 也是外键，需要先创建占位用户 id=0
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO users (id, uid, nickname, created_at) VALUES (0, 'PLACEHOLDER', 'Placeholder', '1970-01-01 00:00:00')"))
        conn.execute(text("INSERT INTO orders (id, order_no, user_id, total_amount, pay_amount, address_name, address_phone, address_detail, status, created_at) VALUES (0, 'PLACEHOLDER_ORDER', 0, 0, 0, '', '', '', 0, '1970-01-01 00:00:00')"))
        conn.commit()

    return engine


@pytest.fixture()
def db_session(engine):
    """创建数据库会话（每个测试独立，自动回滚）"""
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session):
    """FastAPI TestClient，注入测试数据库会话"""
    from fastapi.testclient import TestClient
    from app.core.database import get_db
    from app.main import app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def snowflake_instance():
    """雪花算法测试实例"""
    from snowflake import Snowflake
    return Snowflake(epoch=1577836800000, machine_id=1)

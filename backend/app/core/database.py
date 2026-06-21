"""数据库管理模块 - SQLAlchemy引擎和会话管理"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator

from app.core.config import settings


class Base(DeclarativeBase):
    """ORM基类"""
    pass


def get_engine(use_test: bool = False):
    """创建数据库引擎

    Args:
        use_test: 是否使用测试数据库（SQLite）
    """
    if use_test:
        url = settings.TEST_DB_URL
        if "sqlite" in url:
            return create_engine(
                url,
                connect_args={"check_same_thread": False},
            )
        return create_engine(url)
    return create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,
    )


def get_session_factory(use_test: bool = False) -> sessionmaker:
    """创建Session工厂

    Args:
        use_test: 是否使用测试数据库
    """
    engine = get_engine(use_test=use_test)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator:
    """FastAPI依赖：获取数据库会话"""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

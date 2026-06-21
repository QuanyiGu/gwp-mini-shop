"""Redis连接管理模块"""
from app.core.config import settings


def get_redis_url() -> str:
    """生成Redis连接URL

    Returns:
        Redis连接URL字符串
    """
    password_part = f":{settings.REDIS_PASSWORD}@" if settings.REDIS_PASSWORD else ""
    return (
        f"redis://{password_part}{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        f"/{settings.REDIS_DB}"
    )

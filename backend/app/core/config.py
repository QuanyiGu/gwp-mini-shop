"""应用配置模块 - 从.env加载所有配置"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置，从.env文件加载"""

    # 数据库配置
    DB_DRIVER: str = "mysql+pymysql"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "gwp_shop"
    DB_CHARSET: str = "utf8mb4"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # 测试数据库
    TEST_DB_URL: str = "sqlite+aiosqlite:///./test_gwp.db"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # JWT配置
    JWT_SECRET_KEY: str = "change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 微信小程序配置
    WX_APPID: str = ""
    WX_SECRET: str = ""

    # 微信支付配置
    WX_PAY_MCH_ID: str = ""           # 商户号
    WX_PAY_KEY: str = ""              # 商户支付密钥（用于签名）
    WX_PAY_NOTIFY_URL: str = ""       # 支付结果回调地址（必须公网可访问）
    WX_PAY_SPBILL_IP: str = "127.0.0.1"  # 终端 IP（统一下单参数）

    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # 雪花算法配置
    SNOWFLAKE_EPOCH: int = 1577836800000  # 2020-01-01
    SNOWFLAKE_MACHINE_ID: int = 1

    @property
    def DATABASE_URL(self) -> str:
        """生成数据库连接URL"""
        if self.DB_DRIVER.startswith('sqlite'):
            return f"{self.DB_DRIVER}:///./{self.DB_NAME}.db"
        return (
            f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset={self.DB_CHARSET}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

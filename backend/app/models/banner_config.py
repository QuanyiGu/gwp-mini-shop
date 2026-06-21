"""Banner配置模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, String, Integer, Text, DateTime
from datetime import datetime

from app.core.database import Base


class BannerConfig(Base):
    """Banner配置表"""
    __tablename__ = 'banner_configs'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(64), index=True, nullable=False)  # growth_status, etc.
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=False, default='')  # image URL or text
    status = Column(Integer, nullable=False, default=1)  # 1=显示 0=隐藏
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

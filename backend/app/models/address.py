"""收货地址模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Address(Base):
    """收货地址表"""
    __tablename__ = 'addresses'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), index=True, nullable=False)
    name = Column(String(64), nullable=False)
    phone = Column(String(32), nullable=False)
    province = Column(String(64), nullable=False)
    city = Column(String(64), nullable=False)
    district = Column(String(64), nullable=False)
    detail = Column(String(512), nullable=False)
    is_default = Column(Integer, default=0)  # 0=非默认 1=默认

    # 关系
    user = relationship('User', back_populates='addresses')

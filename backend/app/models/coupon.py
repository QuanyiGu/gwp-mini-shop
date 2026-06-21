"""优惠券模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Coupon(Base):
    """优惠券表"""
    __tablename__ = 'coupons'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), index=True, nullable=False)
    type = Column(Integer, nullable=False, default=1)  # 1=满减券
    discount = Column(Numeric(10, 2), nullable=False)
    min_amount = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(Integer, nullable=False, default=0)  # 0=未使用 1=已使用 2=已过期
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship('User', back_populates='coupons')

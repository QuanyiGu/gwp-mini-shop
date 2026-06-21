"""商品扩展信息模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ProductExtra(Base):
    """商品扩展表"""
    __tablename__ = 'product_extras'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, ForeignKey('products.id'), unique=True, index=True, nullable=False)
    harvest_date = Column(Date, nullable=True)  # 采摘日期
    variety_info = Column(String(256), default='')  # 品种信息
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    product = relationship('Product', back_populates='extra')

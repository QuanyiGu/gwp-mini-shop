"""商品分类模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Category(Base):
    """商品分类表"""
    __tablename__ = 'categories'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    icon = Column(String(512), default='')
    sort = Column(Integer, default=0)

    # 关系
    products = relationship('Product', back_populates='category')

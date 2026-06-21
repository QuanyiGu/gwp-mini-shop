"""商品模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, String, Integer, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Product(Base):
    """商品表"""
    __tablename__ = 'products'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(BigInteger, ForeignKey('categories.id'), index=True, nullable=False)
    name = Column(String(256), nullable=False)
    main_image = Column(String(512), nullable=False, default='')
    images = Column(Text, default='[]')  # JSON array stored as text
    description = Column(Text, default='')
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=False, default=0)
    stock = Column(Integer, nullable=False, default=0)
    sales = Column(Integer, nullable=False, default=0)
    status = Column(Integer, nullable=False, default=1)  # 1=上架, 0=下架
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系
    category = relationship('Category', back_populates='products')
    order_items = relationship('OrderItem', back_populates='product')
    cart_items = relationship('CartItem', back_populates='product')
    extra = relationship('ProductExtra', back_populates='product', uselist=False, cascade='all, delete-orphan')

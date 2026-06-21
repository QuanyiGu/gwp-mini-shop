"""订单商品模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class OrderItem(Base):
    """订单商品表"""
    __tablename__ = 'order_items'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey('orders.id'), index=True, nullable=False)
    product_id = Column(BigInteger, ForeignKey('products.id'), index=True, nullable=False)
    product_name = Column(String(256), nullable=False)
    product_image = Column(String(512), nullable=False, default='')
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_price = Column(Numeric(10, 2), nullable=False)

    # 关系
    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')

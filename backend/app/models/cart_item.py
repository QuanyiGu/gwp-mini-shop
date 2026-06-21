"""购物车模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class CartItem(Base):
    """购物车表"""
    __tablename__ = 'cart_items'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), index=True, nullable=False)
    product_id = Column(BigInteger, ForeignKey('products.id'), index=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    selected = Column(Integer, default=1)  # 0=未选中 1=选中
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    user = relationship('User', back_populates='cart_items')
    product = relationship('Product', back_populates='cart_items')

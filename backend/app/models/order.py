"""订单模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, String, Integer, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal

from app.core.database import Base


class Order(Base):
    """订单表"""
    __tablename__ = 'orders'

    # 订单状态常量
    STATUS_PENDING = 0       # 待付款
    STATUS_PAID = 1          # 已付款(待发货)
    STATUS_SHIPPED = 2       # 已发货(待收货)
    STATUS_COMPLETED = 3     # 已完成
    STATUS_CANCELLED = 4     # 已取消
    STATUS_REFUNDED = 5      # 已退款
    STATUS_REFUNDING = 6     # 退款中

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_no = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), index=True, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    pay_amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=Decimal('0'))
    pay_time = Column(DateTime, nullable=True)
    address_name = Column(String(64), nullable=False)
    address_phone = Column(String(32), nullable=False)
    address_detail = Column(String(512), nullable=False)
    status = Column(Integer, nullable=False, default=0)
    gift_package = Column(Integer, default=0)  # 礼盒包装 0=否 1=是
    greeting_card = Column(Text, default='')
    tracking_node = Column(Text, default='[]')  # JSON array
    logistics_company = Column(String(64), default='')
    logistics_no = Column(String(128), default='')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    # 关系
    user = relationship('User', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

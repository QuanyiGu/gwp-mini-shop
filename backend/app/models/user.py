"""用户模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uid = Column(String(32), unique=True, nullable=False, index=True)
    openid = Column(String(64), unique=True, index=True)
    unionid = Column(String(64), unique=True)
    nickname = Column(String(128))
    avatar_url = Column(String(512), default='')
    phone = Column(String(32), default='')
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    addresses = relationship('Address', back_populates='user', cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan')
    cart_items = relationship('CartItem', back_populates='user', cascade='all, delete-orphan')
    coupons = relationship('Coupon', back_populates='user', cascade='all, delete-orphan')
    invites_as_inviter = relationship('Invite', foreign_keys='Invite.inviter_id', back_populates='inviter')
    invites_as_invitee = relationship('Invite', foreign_keys='Invite.invitee_id', back_populates='invitee')

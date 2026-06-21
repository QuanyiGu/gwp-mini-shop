"""邀请记录模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Invite(Base):
    """邀请记录表"""
    __tablename__ = 'invites'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    inviter_id = Column(BigInteger, ForeignKey('users.id'), index=True, nullable=False)
    invitee_id = Column(BigInteger, ForeignKey('users.id'), index=True, nullable=True)
    invite_code = Column(String(32), index=True, nullable=False)
    order_id = Column(BigInteger, ForeignKey('orders.id'), index=True, nullable=True)
    coupon_sent = Column(Integer, default=0)  # 0=未发送 1=已发送
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    inviter = relationship('User', foreign_keys=[inviter_id], back_populates='invites_as_inviter')
    invitee = relationship('User', foreign_keys=[invitee_id], back_populates='invites_as_invitee')

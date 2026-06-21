"""商家后台用户模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class AdminUser(Base):
    """商家后台用户表"""
    __tablename__ = 'admin_users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    nickname = Column(String(64), nullable=False, default='')
    role = Column(String(32), nullable=False, default='admin')  # admin, super_admin
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    operate_logs = relationship('AdminOperateLog', back_populates='admin', cascade='all, delete-orphan')

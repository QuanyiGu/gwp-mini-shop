"""管理员操作日志模型 - TDD GREEN阶段"""
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class AdminOperateLog(Base):
    """管理员操作日志表"""
    __tablename__ = 'admin_operate_logs'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger, ForeignKey('admin_users.id'), index=True, nullable=False)
    action = Column(String(64), nullable=False)  # create, update, delete, etc.
    target_type = Column(String(64), nullable=False)  # product, order, etc.
    target_id = Column(BigInteger, nullable=False)
    detail = Column(Text, default='')  # JSON detail
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    admin = relationship('AdminUser', back_populates='operate_logs')

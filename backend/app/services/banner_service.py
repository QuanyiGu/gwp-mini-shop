"""Banner服务层"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.banner_config import BannerConfig
from app.utils.error_codes import ErrorCode, error_response


def get_banners_by_type(db: Session, banner_type: str, status: int = 1) -> dict:
    """获取指定类型的Banner列表"""
    query = select(BannerConfig).where(
        BannerConfig.type == banner_type,
        BannerConfig.status == status,
    ).order_by(BannerConfig.id)
    banners = db.scalars(query).all()
    return {"code": ErrorCode.SUCCESS, "data": banners}


def get_growth_status_banners(db: Session) -> dict:
    """获取生长状态Banner（生长周期追踪）"""
    return get_banners_by_type(db, "growth_status")


def create_banner(
    db: Session,
    banner_type: str,
    title: str,
    content: str,
    status: int = 1,
) -> dict:
    """创建Banner配置"""
    banner = BannerConfig(
        type=banner_type,
        title=title,
        content=content,
        status=status,
    )
    db.add(banner)
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": banner}


def update_banner(
    db: Session,
    banner_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    status: Optional[int] = None,
) -> dict:
    """更新Banner配置"""
    banner = db.get(BannerConfig, banner_id)
    if not banner:
        return error_response(ErrorCode.NOT_FOUND)

    if title is not None:
        banner.title = title
    if content is not None:
        banner.content = content
    if status is not None:
        banner.status = status

    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": banner}


def delete_banner(db: Session, banner_id: int) -> dict:
    """删除Banner配置"""
    banner = db.get(BannerConfig, banner_id)
    if not banner:
        return error_response(ErrorCode.NOT_FOUND)

    db.delete(banner)
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": None}

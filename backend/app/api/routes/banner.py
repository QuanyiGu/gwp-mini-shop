"""Banner路由 - TDD GREEN阶段"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.banner import BannerResponse
from app.utils.error_codes import ErrorCode

router = APIRouter()


@router.get("/banners/growth-status", response_model=dict)
def get_growth_status_banners(
    db: Session = Depends(get_db)
) -> dict:
    """获取生长状态Banner列表

    Returns:
        统一响应格式
    """
    from app.models.banner_config import BannerConfig

    banners = db.query(BannerConfig).filter(
        BannerConfig.type == 'growth_status',
        BannerConfig.status == 1
    ).order_by(BannerConfig.created_at.desc()).all()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": [BannerResponse.model_validate(b).model_dump() for b in banners]
    }

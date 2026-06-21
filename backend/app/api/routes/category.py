"""商品分类路由 - TDD GREEN阶段"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any

from app.core.database import get_db
from app.schemas.category import CategoryResponse
from app.utils.error_codes import ErrorCode

router = APIRouter()


@router.get("/categories", response_model=dict)
def get_categories(db: Session = Depends(get_db)) -> dict:
    """获取分类列表

    Returns:
        统一响应格式，包含分类列表
    """
    from app.models.category import Category

    categories = db.query(Category).order_by(Category.sort).all()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": [CategoryResponse.model_validate(c).model_dump() for c in categories]
    }

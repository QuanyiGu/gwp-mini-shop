"""首页聚合数据路由 - TDD GREEN阶段"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.banner import BannerResponse
from app.schemas.category import CategoryResponse
from app.schemas.product import ProductResponse
from app.utils.error_codes import ErrorCode

router = APIRouter()


def banner_to_response(banner) -> dict:
    """将Banner模型转换为响应字典"""
    return BannerResponse.model_validate(banner).model_dump()


def category_to_response(category) -> dict:
    """将分类模型转换为响应字典"""
    return CategoryResponse.model_validate(category).model_dump()


def product_to_response(product) -> dict:
    """将商品模型转换为响应字典"""
    import json

    data = {
        "id": product.id,
        "category_id": product.category_id,
        "name": product.name,
        "main_image": product.main_image,
        "images": product.images,
        "description": product.description,
        "price": product.price,
        "original_price": product.original_price,
        "stock": product.stock,
        "sales": product.sales,
        "status": product.status,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }
    if isinstance(data.get('images'), str):
        try:
            data['images'] = json.loads(data['images'])
        except (json.JSONDecodeError, TypeError):
            data['images'] = []
    return ProductResponse.model_validate(data).model_dump()


def _column(model, preferred: str, fallback: str):
    """兼容不同命名的模型字段"""
    if hasattr(model, preferred):
        return getattr(model, preferred)
    return getattr(model, fallback)


@router.get("/home/data", response_model=dict)
def get_home_data(db: Session = Depends(get_db)) -> dict:
    """获取首页聚合数据

    Returns:
        统一响应格式，包含轮播图、分类、推荐商品和生长状态图
    """
    from app.models.banner_config import BannerConfig
    from app.models.category import Category
    from app.models.product import Product

    banner_active = _column(BannerConfig, "is_active", "status")
    banner_sort = _column(BannerConfig, "sort_order", "created_at")
    category_sort = _column(Category, "sort_order", "sort")

    banners = db.query(BannerConfig).filter(
        banner_active == 1
    ).order_by(banner_sort).all()
    categories = db.query(Category).order_by(category_sort).all()
    products = db.query(Product).filter(Product.status == 1).limit(10).all()
    growth_status = db.query(BannerConfig).filter(
        BannerConfig.type == 'growth',
        banner_active == 1
    ).first()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "banners": [banner_to_response(b) for b in banners],
            "categories": [category_to_response(c) for c in categories],
            "products": [product_to_response(p) for p in products],
            "growth_status": banner_to_response(growth_status) if growth_status else None,
        }
    }

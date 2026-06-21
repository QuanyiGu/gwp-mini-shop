"""商品路由 - TDD GREEN阶段"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.core.database import get_db
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate
from app.utils.error_codes import ErrorCode

router = APIRouter()


def product_to_response(product) -> dict:
    """将商品模型转换为响应字典"""
    data = ProductResponse.model_validate(product).model_dump()
    # 解析images JSON字段
    if isinstance(data.get('images'), str):
        try:
            data['images'] = json.loads(data['images'])
        except (json.JSONDecodeError, TypeError):
            data['images'] = []
    return data


@router.get("/products", response_model=dict)
def get_products(
    category_id: Optional[int] = None,
    status: Optional[int] = 1,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
) -> dict:
    """获取商品列表

    Args:
        category_id: 分类ID（可选）
        status: 商品状态（1=上架，0=下架）
        page: 页码
        page_size: 每页数量

    Returns:
        统一响应格式，包含商品列表和分页信息
    """
    from app.models.product import Product

    query = db.query(Product)

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)

    if status is not None:
        query = query.filter(Product.status == status)

    # 计算总数
    total = query.count()

    # 分页查询
    offset = (page - 1) * page_size
    products = query.order_by(Product.created_at.desc()).offset(offset).limit(page_size).all()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "list": [product_to_response(p) for p in products],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    }


@router.get("/products/{product_id}", response_model=dict)
def get_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    """获取商品详情

    Args:
        product_id: 商品ID

    Returns:
        统一响应格式，包含商品详情
    """
    from app.models.product import Product

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {
            "code": ErrorCode.NOT_FOUND,
            "message": "商品不存在",
            "data": None
        }

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": product_to_response(product)
    }

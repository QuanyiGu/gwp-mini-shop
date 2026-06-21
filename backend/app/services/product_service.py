"""商品服务层"""
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.product import Product
from app.utils.error_codes import ErrorCode, error_response
from app.utils.pagination import calculate_offset, calculate_total_pages


def get_products(
    db: Session,
    category_id: Optional[int] = None,
    status: int = 1,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """获取商品列表（分页）"""
    query = select(Product)
    count_query = select(func.count(Product.id))

    if category_id is not None:
        query = query.where(Product.category_id == category_id)
        count_query = count_query.where(Product.category_id == category_id)
    if status is not None:
        query = query.where(Product.status == status)
        count_query = count_query.where(Product.status == status)

    total = db.scalar(count_query)
    offset = calculate_offset(page, page_size)
    total_pages = calculate_total_pages(total, page_size)

    query = query.offset(offset).limit(page_size).order_by(Product.created_at.desc())
    products = db.scalars(query).all()

    return {
        "code": ErrorCode.SUCCESS,
        "data": {
            "items": products,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    }


def get_product(db: Session, product_id: int) -> dict:
    """获取商品详情"""
    product = db.get(Product, product_id)
    if not product:
        return error_response(ErrorCode.NOT_FOUND)
    return {"code": ErrorCode.SUCCESS, "data": product}


def create_product(db: Session, data: dict) -> dict:
    """创建商品"""
    product = Product(**data)
    db.add(product)
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": product}


def update_product(db: Session, product_id: int, data: dict) -> dict:
    """更新商品信息"""
    product = db.get(Product, product_id)
    if not product:
        return error_response(ErrorCode.NOT_FOUND)

    for key, value in data.items():
        if hasattr(product, key):
            setattr(product, key, value)
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": product}


def update_stock(db: Session, product_id: int, delta_quantity: int) -> dict:
    """更新库存（delta_quantity 正数加库存，负数减库存）"""
    product = db.get(Product, product_id)
    if not product:
        return error_response(ErrorCode.NOT_FOUND)

    new_stock = product.stock + delta_quantity
    if new_stock < 0:
        return error_response(ErrorCode.STOCK_NOT_ENOUGH)

    product.stock = new_stock
    db.flush()
    return {"code": ErrorCode.SUCCESS, "data": product}

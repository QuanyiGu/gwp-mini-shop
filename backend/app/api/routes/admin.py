"""商家后台路由 - TDD GREEN阶段"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal

from app.core.database import get_db
from app.core.security import create_access_token, verify_password, hash_password
from app.schemas.admin import AdminLogin, AdminTokenResponse
from app.utils.error_codes import ErrorCode

router = APIRouter()


def admin_to_response(admin) -> dict:
    """将管理员模型转换为响应字典"""
    return {
        "id": admin.id,
        "username": admin.username,
        "nickname": admin.nickname,
        "role": admin.role
    }


@router.post("/login", response_model=dict)
def admin_login(
    login_data: AdminLogin,
    db: Session = Depends(get_db)
) -> dict:
    """商家后台登录

    Args:
        login_data: 登录数据

    Returns:
        统一响应格式
    """
    from app.models.admin_user import AdminUser

    admin = db.query(AdminUser).filter(
        AdminUser.username == login_data.username
    ).first()

    if not admin or not verify_password(login_data.password, admin.password_hash):
        return {
            "code": ErrorCode.PARAM_ERROR,
            "message": "用户名或密码错误",
            "data": None
        }

    # 生成token
    access_token = create_access_token(
        data={"sub": str(admin.id), "role": admin.role},
        expires_delta=timedelta(minutes=15)
    )
    refresh_token = create_access_token(
        data={"sub": str(admin.id), "type": "refresh"},
        expires_delta=timedelta(days=7)
    )

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "admin": admin_to_response(admin)
        }
    }


def get_current_admin():
    """获取当前管理员（依赖项）"""
    from fastapi import Header, HTTPException
    from app.core.security import decode_token

    # 这里简化处理，实际应该从Authorization header获取token
    # TODO: 实现完整的JWT验证
    pass


@router.get("/stats", response_model=dict)
def get_admin_stats(
    db: Session = Depends(get_db)
) -> dict:
    """获取数据统计

    Returns:
        统一响应格式
    """
    from app.models.order import Order
    from app.models.product import Product
    from sqlalchemy import func

    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    # 今日销售额
    today_sales = db.query(func.sum(Order.pay_amount)).filter(
        Order.status >= 2,  # 已付款订单
        Order.created_at >= today_start,
        Order.created_at <= today_end
    ).scalar() or Decimal('0')

    # 今日订单量
    today_orders = db.query(func.count(Order.id)).filter(
        Order.created_at >= today_start,
        Order.created_at <= today_end
    ).scalar()

    # 全部销售额
    total_sales = db.query(func.sum(Order.pay_amount)).filter(
        Order.status >= 2
    ).scalar() or Decimal('0')

    # 商品数量
    total_products = db.query(func.count(Product.id)).filter(
        Product.status == 1
    ).scalar()

    # 待发货订单
    pending_orders = db.query(func.count(Order.id)).filter(
        Order.status == 1
    ).scalar()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "today_sales": str(today_sales),
            "today_orders": today_orders,
            "total_sales": str(total_sales),
            "total_products": total_products,
            "pending_orders": pending_orders
        }
    }


@router.get("/products", response_model=dict)
def get_admin_products(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
) -> dict:
    """获取商品列表（商家后台）

    Returns:
        统一响应格式
    """
    from app.models.product import Product
    from sqlalchemy import func
    import json

    total = db.query(func.count(Product.id)).scalar()
    offset = (page - 1) * page_size
    products = db.query(Product).order_by(
        Product.created_at.desc()
    ).offset(offset).limit(page_size).all()

    result = []
    for p in products:
        data = {
            "id": p.id,
            "category_id": p.category_id,
            "name": p.name,
            "main_image": p.main_image,
            "images": json.loads(p.images) if isinstance(p.images, str) else p.images,
            "price": str(p.price),
            "original_price": str(p.original_price),
            "stock": p.stock,
            "sales": p.sales,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        result.append(data)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "list": result,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    }


@router.post("/products", response_model=dict)
def create_admin_product(
    product_data: dict,
    db: Session = Depends(get_db)
) -> dict:
    """添加商品

    Returns:
        统一响应格式
    """
    from app.models.product import Product
    import json

    product = Product(
        category_id=product_data['category_id'],
        name=product_data['name'],
        main_image=product_data.get('main_image', ''),
        images=json.dumps(product_data.get('images', [])),
        description=product_data.get('description', ''),
        price=product_data['price'],
        original_price=product_data.get('original_price', product_data['price']),
        stock=product_data.get('stock', 0),
        status=product_data.get('status', 1)
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {"id": product.id}
    }


@router.put("/products/{product_id}", response_model=dict)
def update_admin_product(
    product_id: int,
    product_data: dict,
    db: Session = Depends(get_db)
) -> dict:
    """更新商品

    Returns:
        统一响应格式
    """
    from app.models.product import Product
    import json

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {
            "code": ErrorCode.NOT_FOUND,
            "message": "商品不存在",
            "data": None
        }

    # 更新字段
    for key in ['category_id', 'name', 'main_image', 'description',
                'price', 'original_price', 'stock', 'status']:
        if key in product_data:
            setattr(product, key, product_data[key])

    if 'images' in product_data:
        product.images = json.dumps(product_data['images'])

    db.commit()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {"id": product.id}
    }


@router.put("/products/{product_id}/status", response_model=dict)
def update_product_status(
    product_id: int,
    status: int,
    db: Session = Depends(get_db)
) -> dict:
    """更新商品上下架状态

    Returns:
        统一响应格式
    """
    from app.models.product import Product

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {
            "code": ErrorCode.NOT_FOUND,
            "message": "商品不存在",
            "data": None
        }

    product.status = status
    db.commit()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {"id": product.id, "status": status}
    }


@router.put("/products/{product_id}/extras", response_model=dict)
def update_product_extras(
    product_id: int,
    extras_data: dict,
    db: Session = Depends(get_db)
) -> dict:
    """更新商品扩展信息（采蜜日期/品种）

    Returns:
        统一响应格式
    """
    from app.models.product_extra import ProductExtra

    extra = db.query(ProductExtra).filter(
        ProductExtra.product_id == product_id
    ).first()

    if not extra:
        extra = ProductExtra(product_id=product_id)
        db.add(extra)

    if 'harvest_date' in extras_data:
        extra.harvest_date = extras_data['harvest_date']
    if 'variety_info' in extras_data:
        extra.variety_info = extras_data['variety_info']

    db.commit()
    db.refresh(extra)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {"id": extra.id}
    }


@router.get("/orders", response_model=dict)
def get_admin_orders(
    status: int = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
) -> dict:
    """获取订单列表（商家后台）

    Returns:
        统一响应格式
    """
    from app.models.order import Order
    from sqlalchemy import func

    query = db.query(Order)
    if status is not None:
        query = query.filter(Order.status == status)

    total = query.count()
    offset = (page - 1) * page_size
    orders = query.order_by(Order.created_at.desc()).offset(offset).limit(page_size).all()

    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "order_no": o.order_no,
            "user_id": o.user_id,
            "total_amount": str(o.total_amount),
            "pay_amount": str(o.pay_amount),
            "status": o.status,
            "address_name": o.address_name,
            "address_phone": o.address_phone,
            "created_at": o.created_at.isoformat() if o.created_at else None
        })

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "list": result,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    }


@router.put("/orders/{order_id}/ship", response_model=dict)
def ship_order(
    order_id: int,
    logistics_company: str,
    logistics_no: str,
    db: Session = Depends(get_db)
) -> dict:
    """订单发货

    Returns:
        统一响应格式
    """
    from app.models.order import Order

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {
            "code": ErrorCode.ORDER_NOT_FOUND,
            "message": "订单不存在",
            "data": None
        }

    if order.status != 1:  # 不是待发货状态
        return {
            "code": ErrorCode.ORDER_STATUS_ERROR,
            "message": "订单状态不允许此操作",
            "data": None
        }

    order.status = 2  # 待收货
    order.logistics_company = logistics_company
    order.logistics_no = logistics_no
    order.tracking_node = 2  # 已发货
    db.commit()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {"id": order.id, "status": order.status}
    }


@router.put("/orders/{order_id}/tracking", response_model=dict)
def update_order_tracking(
    order_id: int,
    tracking_node: int,
    db: Session = Depends(get_db)
) -> dict:
    """更新订单追踪节点

    Returns:
        统一响应格式
    """
    from app.models.order import Order

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {
            "code": ErrorCode.ORDER_NOT_FOUND,
            "message": "订单不存在",
            "data": None
        }

    order.tracking_node = tracking_node
    db.commit()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {"id": order.id, "tracking_node": tracking_node}
    }


@router.get("/banners", response_model=dict)
def get_admin_banners(
    db: Session = Depends(get_db)
) -> dict:
    """获取Banner配置列表

    Returns:
        统一响应格式
    """
    from app.models.banner_config import BannerConfig

    banners = db.query(BannerConfig).order_by(
        BannerConfig.created_at.desc()
    ).all()

    from app.schemas.banner import BannerResponse
    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": [BannerResponse.model_validate(b).model_dump() for b in banners]
    }


@router.post("/banners", response_model=dict)
def create_banner(
    banner_data: dict,
    db: Session = Depends(get_db)
) -> dict:
    """创建Banner

    Returns:
        统一响应格式
    """
    from app.models.banner_config import BannerConfig

    banner = BannerConfig(
        type=banner_data['type'],
        title=banner_data['title'],
        content=banner_data.get('content', ''),
        status=banner_data.get('status', 1)
    )
    db.add(banner)
    db.commit()
    db.refresh(banner)

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {"id": banner.id}
    }


@router.put("/banners/{banner_id}", response_model=dict)
def update_banner(
    banner_id: int,
    banner_data: dict,
    db: Session = Depends(get_db)
) -> dict:
    """更新Banner

    Returns:
        统一响应格式
    """
    from app.models.banner_config import BannerConfig

    banner = db.query(BannerConfig).filter(
        BannerConfig.id == banner_id
    ).first()

    if not banner:
        return {
            "code": ErrorCode.NOT_FOUND,
            "message": "Banner不存在",
            "data": None
        }

    for key in ['type', 'title', 'content', 'status']:
        if key in banner_data:
            setattr(banner, key, banner_data[key])

    db.commit()

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {"id": banner.id}
    }

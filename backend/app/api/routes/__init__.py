"""API路由汇总 - TDD GREEN阶段"""
from fastapi import APIRouter

router = APIRouter()

# 用户端API
from app.api.routes import (
    auth,
    product,
    category,
    cart,
    order,
    address,
    coupon,
    invite,
    banner,
    pay,
    user,
    home,
)

# 商家后台API
from app.api.routes import admin

# 注册用户端路由
router.include_router(auth.router, prefix="/api", tags=["认证"])
router.include_router(product.router, prefix="/api", tags=["商品"])
router.include_router(category.router, prefix="/api", tags=["分类"])
router.include_router(cart.router, prefix="/api", tags=["购物车"])
router.include_router(order.router, prefix="/api", tags=["订单"])
router.include_router(address.router, prefix="/api", tags=["收货地址"])
router.include_router(coupon.router, prefix="/api", tags=["优惠券"])
router.include_router(invite.router, prefix="/api", tags=["邀请"])
router.include_router(banner.router, prefix="/api", tags=["Banner"])
router.include_router(pay.router, prefix="/api", tags=["支付"])
router.include_router(user.router, prefix="/api", tags=["用户"])
router.include_router(home.router, prefix="/api", tags=["首页"])

# 注册商家后台路由
router.include_router(admin.router, prefix="/api/admin", tags=["商家后台"])

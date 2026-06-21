"""支付路由 - 预下单 / 回调"""
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.pay import PrepareRequest
from app.services import pay_service
from app.utils.wxpay import dict_to_xml

router = APIRouter()


@router.post("/pay/prepare", response_model=dict)
def prepay(
    payload: PrepareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """小程序端发起预下单

    需要 Authorization: Bearer <access_token>
    返回 wx.requestPayment 所需的 5 个字段。
    """
    return pay_service.create_prepay_order(
        db=db, user_id=current_user.id, order_no=payload.order_no
    )


@router.post("/pay/notify")
async def pay_notify(request: Request, db: Session = Depends(get_db)) -> Response:
    """微信支付回调（无认证，验签即认证）

    接收 XML，返回 XML。微信侧约定：
    - 收到 SUCCESS 后停止重试
    - 收到 FAIL 或解析错误时按指数退避重试 8 次
    """
    body_bytes = await request.body()
    try:
        body_str = body_bytes.decode("utf-8")
    except UnicodeDecodeError:
        body_str = ""

    result = pay_service.handle_pay_notify(db, body_str)
    return Response(content=dict_to_xml(result), media_type="application/xml")

"""微信支付服务

- create_prepay_order: 预下单，返回 wx.requestPayment 所需 5 元素
- handle_pay_notify:   处理微信回调，含签名验证与幂等
"""
import time
from decimal import Decimal
from typing import Dict

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.order import Order
from app.models.user import User
from app.utils.error_codes import ErrorCode, error_response
from app.utils.snowflake import generate_uid
from app.utils.wxpay import (
    build_sign,
    dict_to_xml,
    verify_sign,
    wx_unified_order,
    xml_to_dict,
)


# ---------- 内部辅助 ----------

def _get_pay_key() -> str:
    """获取商户支付密钥（独立函数便于测试 patch）"""
    return settings.WX_PAY_KEY


def _get_appid() -> str:
    return settings.WX_APPID


def _get_mch_id() -> str:
    return settings.WX_PAY_MCH_ID


def _get_notify_url() -> str:
    return settings.WX_PAY_NOTIFY_URL


def _success_xml() -> Dict[str, str]:
    """微信回调成功响应"""
    return {"return_code": "SUCCESS", "return_msg": "OK"}


def _fail_xml(msg: str = "FAIL") -> Dict[str, str]:
    """微信回调失败响应"""
    return {"return_code": "FAIL", "return_msg": msg}


# ---------- 预下单 ----------

def create_prepay_order(db: Session, user_id: int, order_no: str) -> dict:
    """创建预支付订单

    流程：
    1. 查订单 → 校验归属 → 校验状态=PENDING
    2. 取用户 openid
    3. 调微信统一下单 API
    4. 用 prepay_id 生成小程序前端 wx.requestPayment 所需 5 元素

    Returns:
        统一响应 {code, message, data}
    """
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        return error_response(ErrorCode.ORDER_NOT_FOUND)

    if order.user_id != user_id:
        return error_response(ErrorCode.NO_PERMISSION)

    if order.status != Order.STATUS_PENDING:
        return error_response(ErrorCode.ORDER_STATUS_ERROR)

    user = db.get(User, user_id)
    if not user:
        return error_response(ErrorCode.USER_NOT_FOUND)

    # 构造统一下单参数
    nonce_str = str(generate_uid())[:32]
    total_fee = int(Decimal(order.pay_amount) * 100)  # 元 → 分

    payload = {
        "appid": _get_appid(),
        "mch_id": _get_mch_id(),
        "nonce_str": nonce_str,
        "body": f"GWP小店-订单{order.order_no}",
        "out_trade_no": order.order_no,
        "total_fee": str(total_fee),
        "spbill_create_ip": settings.WX_PAY_SPBILL_IP,
        "notify_url": _get_notify_url(),
        "trade_type": "JSAPI",
        "openid": user.openid or "",
    }
    payload["sign"] = build_sign(payload, key=_get_pay_key())

    try:
        wx_resp = wx_unified_order(payload)
    except Exception:
        return error_response(ErrorCode.PAY_FAILED)

    if wx_resp.get("return_code") != "SUCCESS" or wx_resp.get("result_code") != "SUCCESS":
        return error_response(ErrorCode.PAY_FAILED)

    prepay_id = wx_resp.get("prepay_id", "")
    timestamp = str(int(time.time()))
    front_nonce = str(generate_uid())[:32]
    package = f"prepay_id={prepay_id}"

    pay_params = {
        "appId": _get_appid(),
        "timeStamp": timestamp,
        "nonceStr": front_nonce,
        "package": package,
        "signType": "MD5",
    }
    pay_sign = build_sign(pay_params, key=_get_pay_key())

    return {
        "code": ErrorCode.SUCCESS,
        "message": "success",
        "data": {
            "timeStamp": timestamp,
            "nonceStr": front_nonce,
            "package": package,
            "signType": "MD5",
            "paySign": pay_sign,
        },
    }


# ---------- 回调处理 ----------

def handle_pay_notify(db: Session, xml_body: str) -> Dict[str, str]:
    """处理微信支付回调

    Args:
        db: 数据库会话
        xml_body: 微信回调原始 XML

    Returns:
        要响应给微信的字典（路由层转 XML）

    幂等约定：
    - 同一订单二次回调（已是 PAID 状态）→ 直接 SUCCESS，不重复处理
    - 已取消订单 → SUCCESS（防微信重试），但不变更状态
    - 签名错误 / 订单不存在 → FAIL（让微信重试，因为可能是请求被篡改或暂时性问题）
    """
    # 1. 解析 XML
    try:
        params = xml_to_dict(xml_body)
    except ValueError:
        return _fail_xml("invalid xml")

    # 2. 验签
    if not verify_sign(params, key=_get_pay_key()):
        return _fail_xml("invalid sign")

    # 3. 微信侧业务结果
    if params.get("return_code") != "SUCCESS":
        # 微信本次通知本身就是失败的，对业务不做任何动作，但要回 SUCCESS 防止重试
        return _success_xml()

    if params.get("result_code") != "SUCCESS":
        return _success_xml()

    # 4. 取订单
    order_no = params.get("out_trade_no", "")
    order = db.query(Order).filter(Order.order_no == order_no).first()
    if not order:
        return _fail_xml("order not found")

    # 5. 幂等检查
    if order.status == Order.STATUS_PAID:
        return _success_xml()

    # 6. 已取消订单：不变更但回 SUCCESS（防重试）
    if order.status == Order.STATUS_CANCELLED:
        return _success_xml()

    # 7. 仅 PENDING 状态的订单允许变更为 PAID
    if order.status != Order.STATUS_PENDING:
        # 其他异常状态（已发货/已退款等）也直接回 SUCCESS，不二次处理
        return _success_xml()

    # 8. 状态推进 0 → 1
    order.status = Order.STATUS_PAID
    db.flush()
    db.commit()

    return _success_xml()

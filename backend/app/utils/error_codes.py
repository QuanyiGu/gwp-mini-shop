"""错误码定义和错误响应工具"""
from enum import IntEnum


class ErrorCode(IntEnum):
    """错误码枚举"""
    SUCCESS = 0
    PARAM_ERROR = 1001
    SIGN_ERROR = 1002
    NO_PERMISSION = 1003
    NOT_FOUND = 1004
    STOCK_NOT_ENOUGH = 2001
    ORDER_NOT_FOUND = 2002
    ORDER_STATUS_ERROR = 2003
    PAY_FAILED = 2004
    USER_NOT_FOUND = 3001
    TOKEN_EXPIRED = 3002
    COUPON_NOT_FOUND = 4001
    COUPON_EXPIRED = 4002
    COUPON_USED = 4003
    COUPON_CONDITION_NOT_MET = 4004
    ADMIN_NO_PERMISSION = 5001
    SERVER_ERROR = 5002


ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "成功",
    ErrorCode.PARAM_ERROR: "参数错误",
    ErrorCode.SIGN_ERROR: "签名验证失败",
    ErrorCode.NO_PERMISSION: "无访问权限",
    ErrorCode.NOT_FOUND: "资源不存在",
    ErrorCode.STOCK_NOT_ENOUGH: "库存不足",
    ErrorCode.ORDER_NOT_FOUND: "订单不存在",
    ErrorCode.ORDER_STATUS_ERROR: "订单状态不允许此操作",
    ErrorCode.PAY_FAILED: "支付失败",
    ErrorCode.USER_NOT_FOUND: "用户不存在",
    ErrorCode.TOKEN_EXPIRED: "登录凭证过期",
    ErrorCode.COUPON_NOT_FOUND: "优惠券不存在",
    ErrorCode.COUPON_EXPIRED: "优惠券已过期",
    ErrorCode.COUPON_USED: "优惠券已使用",
    ErrorCode.COUPON_CONDITION_NOT_MET: "不满足使用条件",
    ErrorCode.ADMIN_NO_PERMISSION: "商家后台权限不足",
    ErrorCode.SERVER_ERROR: "服务器内部错误",
}


def error_response(code: int) -> dict:
    """根据错误码构造错误响应"""
    message = ERROR_MESSAGES.get(code, "未知错误")
    return {"code": code, "message": message}

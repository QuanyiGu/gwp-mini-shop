"""支付相关 Schema"""
from pydantic import BaseModel, Field


class PrepareRequest(BaseModel):
    """预下单请求（user_id 从 token 解析，不接收前端入参）"""
    order_no: str = Field(..., description="订单号")


class PrepareData(BaseModel):
    """wx.requestPayment 直接使用的 5 个字段"""
    timeStamp: str
    nonceStr: str
    package: str  # 形如 prepay_id=xxx
    signType: str = "MD5"
    paySign: str

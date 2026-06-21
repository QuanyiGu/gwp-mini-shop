"""微信支付工具函数

提供：
- 签名生成与验证（MD5 模式）
- XML 序列化/反序列化（统一带 CDATA）
- 统一下单 HTTP 调用
"""
import hashlib
import xml.etree.ElementTree as ET
from typing import Dict


def build_sign(params: Dict[str, str], key: str) -> str:
    """生成微信支付签名（MD5）

    规则：
    1. 排除 sign 字段和值为空字符串的字段
    2. 按 key 字典序升序拼接 k=v&k=v
    3. 末尾追加 &key=<商户key>
    4. MD5 后转大写不变（微信原版要求大写，但比较时大小写不敏感）

    Args:
        params: 参数字典
        key: 商户支付密钥

    Returns:
        32 位 MD5 小写签名
    """
    filtered = {k: v for k, v in params.items() if k != "sign" and v != "" and v is not None}
    sorted_keys = sorted(filtered.keys())
    string_a = "&".join(f"{k}={filtered[k]}" for k in sorted_keys)
    string_sign_temp = f"{string_a}&key={key}"
    return hashlib.md5(string_sign_temp.encode("utf-8")).hexdigest()


def verify_sign(params: Dict[str, str], key: str) -> bool:
    """验证签名

    Args:
        params: 含 sign 字段的参数字典
        key: 商户支付密钥
    """
    received = params.get("sign", "")
    if not received:
        return False
    expected = build_sign(params, key=key)
    return expected.lower() == received.lower()


def dict_to_xml(data: Dict[str, str]) -> str:
    """字典 → 微信支付 XML 格式（统一加 CDATA）"""
    parts = ["<xml>"]
    for k, v in data.items():
        parts.append(f"<{k}><![CDATA[{v}]]></{k}>")
    parts.append("</xml>")
    return "".join(parts)


def xml_to_dict(xml_str: str) -> Dict[str, str]:
    """微信支付 XML → 字典

    Raises:
        ValueError: XML 不合法
    """
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError as e:
        raise ValueError(f"invalid xml: {e}")

    if root.tag != "xml":
        raise ValueError(f"root tag must be <xml>, got <{root.tag}>")

    result = {}
    for child in root:
        result[child.tag] = (child.text or "").strip()
    return result


def wx_unified_order(payload: Dict[str, str], timeout: int = 10) -> Dict[str, str]:
    """调用微信统一下单接口

    Args:
        payload: 已含签名的完整请求参数
        timeout: HTTP 超时秒数

    Returns:
        解析后的响应字典
    """
    import httpx  # 局部导入便于测试 patch

    url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    xml_body = dict_to_xml(payload)
    resp = httpx.post(url, content=xml_body.encode("utf-8"), timeout=timeout)
    resp.raise_for_status()
    return xml_to_dict(resp.text)

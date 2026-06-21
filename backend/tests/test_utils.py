"""测试工具函数 - TDD RED阶段"""
import pytest


class TestErrorCodeMapping:
    """测试错误码映射"""

    def test_error_codes_defined(self):
        """错误码常量应已定义"""
        from app.utils.error_codes import ErrorCode
        assert ErrorCode.SUCCESS == 0
        assert ErrorCode.PARAM_ERROR == 1001
        assert ErrorCode.SIGN_ERROR == 1002
        assert ErrorCode.NO_PERMISSION == 1003
        assert ErrorCode.NOT_FOUND == 1004
        assert ErrorCode.STOCK_NOT_ENOUGH == 2001
        assert ErrorCode.ORDER_NOT_FOUND == 2002
        assert ErrorCode.ORDER_STATUS_ERROR == 2003
        assert ErrorCode.PAY_FAILED == 2004
        assert ErrorCode.USER_NOT_FOUND == 3001
        assert ErrorCode.TOKEN_EXPIRED == 3002
        assert ErrorCode.COUPON_NOT_FOUND == 4001
        assert ErrorCode.COUPON_EXPIRED == 4002
        assert ErrorCode.COUPON_USED == 4003
        assert ErrorCode.COUPON_CONDITION_NOT_MET == 4004
        assert ErrorCode.ADMIN_NO_PERMISSION == 5001
        assert ErrorCode.SERVER_ERROR == 5002

    def test_error_code_messages(self):
        """错误码应有对应的消息"""
        from app.utils.error_codes import ERROR_MESSAGES
        assert ERROR_MESSAGES[0] is not None
        assert ERROR_MESSAGES[1001] is not None
        assert ERROR_MESSAGES[2001] is not None

    def test_error_response_helper(self):
        """应能通过错误码构造响应"""
        from app.utils.error_codes import error_response
        resp = error_response(1001)
        assert resp["code"] == 1001
        assert resp["message"] is not None


class TestPaginationHelper:
    """测试分页辅助函数"""

    def test_calculate_offset(self):
        """应能计算分页偏移量"""
        from app.utils.pagination import calculate_offset
        assert calculate_offset(page=1, page_size=10) == 0
        assert calculate_offset(page=2, page_size=10) == 10
        assert calculate_offset(page=3, page_size=20) == 40

    def test_calculate_total_pages(self):
        """应能计算总页数"""
        from app.utils.pagination import calculate_total_pages
        assert calculate_total_pages(total=0, page_size=10) == 0
        assert calculate_total_pages(total=10, page_size=10) == 1
        assert calculate_total_pages(total=11, page_size=10) == 2
        assert calculate_total_pages(total=25, page_size=10) == 3

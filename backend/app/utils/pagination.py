"""分页辅助函数"""
import math


def calculate_offset(page: int, page_size: int) -> int:
    """计算分页偏移量"""
    return (page - 1) * page_size


def calculate_total_pages(total: int, page_size: int) -> int:
    """计算总页数"""
    if total == 0:
        return 0
    return math.ceil(total / page_size)

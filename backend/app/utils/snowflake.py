"""雪花算法ID生成器 - TDD GREEN阶段"""
import threading
import time
from app.core.config import settings

# 雪花算法参数
WORKER_ID = settings.SNOWFLAKE_MACHINE_ID
EPOCH = settings.SNOWFLAKE_EPOCH
WORKER_ID_BITS = 5
SEQUENCE_BITS = 12

WORKER_ID_SHIFT = SEQUENCE_BITS
TIMESTAMP_LEFT_SHIFT = SEQUENCE_BITS + WORKER_ID_BITS
SEQUENCE_MASK = -1 ^ (-1 << SEQUENCE_BITS)

_lock = threading.Lock()
_last_timestamp = -1
_sequence = 0


def _current_time_millis() -> int:
    """获取当前时间戳（毫秒）"""
    return int(time.time() * 1000)


def generate_id() -> int:
    """生成雪花算法唯一ID"""
    global _last_timestamp, _sequence

    timestamp = _current_time_millis()

    with _lock:
        if timestamp < _last_timestamp:
            raise ValueError("Clock moved backwards.")

        if timestamp == _last_timestamp:
            _sequence = (_sequence + 1) & SEQUENCE_MASK
            if _sequence == 0:
                # 序列号溢出，等待下一毫秒
                while timestamp <= _last_timestamp:
                    timestamp = _current_time_millis()
        else:
            _sequence = 0

        _last_timestamp = timestamp

        snowflake_id = (
            (timestamp - EPOCH) << TIMESTAMP_LEFT_SHIFT
            | (WORKER_ID << WORKER_ID_SHIFT)
            | _sequence
        )

    return snowflake_id


# 别名
generate_uid = generate_id
generate_order_no = generate_id

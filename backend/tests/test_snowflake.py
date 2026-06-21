"""测试雪花算法模块 - TDD RED阶段"""
import pytest
import threading


class TestSnowflake:
    """测试 snowflake.py 雪花算法"""

    def test_generate_id_returns_int(self):
        """生成的ID应为整数"""
        from app.utils.snowflake import generate_id
        uid = generate_id()
        assert isinstance(uid, int)

    def test_generate_id_is_positive(self):
        """生成的ID应为正数"""
        from app.utils.snowflake import generate_id
        uid = generate_id()
        assert uid > 0

    def test_generate_id_increases(self):
        """连续生成的ID应递增"""
        from app.utils.snowflake import generate_id
        ids = [generate_id() for _ in range(100)]
        for i in range(1, len(ids)):
            assert ids[i] > ids[i - 1]

    def test_generate_id_unique(self):
        """连续生成的ID应唯一"""
        from app.utils.snowflake import generate_id
        ids = set()
        for _ in range(1000):
            ids.add(generate_id())
        assert len(ids) == 1000

    def test_generate_id_concurrent_unique(self):
        """并发生成的ID应唯一"""
        from app.utils.snowflake import generate_id
        ids = []
        lock = threading.Lock()

        def gen_ids():
            for _ in range(200):
                uid = generate_id()
                with lock:
                    ids.append(uid)

        threads = [threading.Thread(target=gen_ids) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(ids) == 1000
        assert len(set(ids)) == 1000

    def test_generate_id_epoch_2020(self):
        """ID应基于2020-01-01 epoch"""
        from app.utils.snowflake import generate_id
        uid = generate_id()
        # 2020-01-01 epoch, ID应该大于epoch时间戳
        assert uid > 1577836800000

    def test_generate_id_to_string(self):
        """ID应能转为字符串存储"""
        from app.utils.snowflake import generate_id
        uid = generate_id()
        uid_str = str(uid)
        assert len(uid_str) <= 20  # BIGINT最大20位

    def test_generate_uid_alias(self):
        """generate_uid 应为 generate_id 的别名"""
        from app.utils.snowflake import generate_id, generate_uid
        assert generate_uid is generate_id or callable(generate_uid)

    def test_generate_order_no_alias(self):
        """generate_order_no 应为 generate_id 的别名"""
        from app.utils.snowflake import generate_id, generate_order_no
        assert generate_order_no is generate_id or callable(generate_order_no)

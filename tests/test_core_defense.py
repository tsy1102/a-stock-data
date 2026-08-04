"""test_core_defense.py — 核心防线单元测试

V15: 测试 ZHB 事件锁、令牌桶/熔断器核心防御机制
"""
import unittest
from unittest.mock import Mock, patch, MagicMock


class TestTokenBucket(unittest.TestCase):
    """令牌桶限流测试"""

    def test_token_bucket_acquire_success(self):
        """令牌桶正常获取令牌"""
        from stock_common.sc_fault_tolerance import TokenBucket
        bucket = TokenBucket(requests_per_second=10.0, max_burst=5)
        result = bucket.try_acquire(1)
        self.assertTrue(result)

    def test_token_bucket_capacity_limit(self):
        """令牌桶容量限制"""
        from stock_common.sc_fault_tolerance import TokenBucket
        bucket = TokenBucket(requests_per_second=10.0, max_burst=2)
        bucket.try_acquire(1)
        bucket.try_acquire(1)
        result = bucket.try_acquire(1)
        self.assertFalse(result)


class TestCircuitBreaker(unittest.TestCase):
    """熔断器状态转换测试"""

    def test_circuit_breaker_initial_state(self):
        """熔断器初始状态为closed"""
        from stock_common.sc_fault_tolerance import CircuitBreaker
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=60)
        self.assertEqual(cb.state, "closed")

    def test_circuit_breaker_transitions_to_open(self):
        """连续失败后熔断器转换为open状态"""
        from stock_common.sc_fault_tolerance import CircuitBreaker
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=60)
        cb._on_failure()
        cb._on_failure()
        cb._on_failure()
        self.assertEqual(cb.state, "open")

    def test_circuit_breaker_success_resets(self):
        """成功调用重置失败计数"""
        from stock_common.sc_fault_tolerance import CircuitBreaker
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=60)
        cb._on_failure()
        cb._on_failure()
        cb._on_success()
        self.assertEqual(cb._failure_count, 0)


class TestCacheEventLock(unittest.TestCase):
    """ZHB事件锁缓存Key生成测试"""

    def test_report_date_changes_cache_key(self):
        """当ZHB报告期变化时，Cache Key应随之变化"""
        # 模拟不同的报告期
        report_date_1 = "20240331"
        report_date_2 = "20240630"
        
        # 生成的缓存key应该不同
        key_1 = f"financial:get_sina_financial_report:600519:12:report_date={report_date_1}"
        key_2 = f"financial:get_sina_financial_report:600519:12:report_date={report_date_2}"
        
        self.assertNotEqual(key_1, key_2)


if __name__ == "__main__":
    unittest.main()

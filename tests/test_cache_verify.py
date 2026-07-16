#!/usr/bin/env python3
"""test_cache_verify.py - 缓存交叉验证单元测试。

测试场景（V10.0 新逻辑：首次写入即验证，数据变化时自动更新并保持已验证）：
1. 首次写入 → 立即已验证 → get_cache 返回数据
2. 第二次写入（数据一致）→ 刷新过期时间 → get_cache 返回数据
3. 第二次写入（数据不一致）→ 用新数据替换并保持已验证 → get_cache 返回新数据
4. 已验证后写入不同数据 → 已验证数据被替换为新数据
5. @cached 装饰器集成测试（首次调用即写入已验证，二次调用走缓存）
6. 列表数据的交叉验证
7. 普通模式（cross_verify=False）不受影响
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCacheVerify(unittest.TestCase):
    """交叉验证机制单元测试。"""

    def setUp(self):
        """每个测试前使用独立的临时数据库。"""
        self.tmp_dir = tempfile.mkdtemp()
        self.tmp_db = os.path.join(self.tmp_dir, "test_cache.db")
        # 直接替换模块级变量
        import stock_cache
        self.cache_mod = stock_cache
        self._old_db_path = stock_cache._CACHE_DB
        self._old_db = stock_cache._db
        stock_cache._CACHE_DB = self.tmp_db
        stock_cache._db = None

    def tearDown(self):
        """清理临时文件。"""
        try:
            # 恢复原数据库
            self.cache_mod._CACHE_DB = self._old_db_path
            self.cache_mod._db = self._old_db
            # 删除临时文件
            if os.path.exists(self.tmp_db):
                os.remove(self.tmp_db)
            if os.path.exists(self.tmp_db + "-wal"):
                os.remove(self.tmp_db + "-wal")
            if os.path.exists(self.tmp_db + "-shm"):
                os.remove(self.tmp_db + "-shm")
            os.rmdir(self.tmp_dir)
        except Exception as _e:
            print(f"[tearDown] cleanup failed: {_e}", flush=True)

    def test_first_write_verified(self):
        """测试1：首次写入后立即标记为已验证，cross_verify 模式下读取返回数据。"""
        data = {"code": "600519", "name": "贵州茅台"}
        self.cache_mod.set_cache("basic_info", "test_func", data, 3600,
                                 cross_verify=True)
        # V10.0 新逻辑：首次写入即已验证，读取应返回数据
        result = self.cache_mod.get_cache("basic_info", "test_func",
                                          cross_verify=True)
        self.assertIsNotNone(result)
        self.assertEqual(result["code"], "600519")
        # 普通模式（不验证）也应能读取到
        result_normal = self.cache_mod.get_cache("basic_info", "test_func",
                                                  cross_verify=False)
        self.assertIsNotNone(result_normal)
        self.assertEqual(result_normal["code"], "600519")

    def test_second_write_same_refresh(self):
        """测试2：第二次写入相同数据 → 刷新过期时间 → 读取返回数据。"""
        data = {"code": "600519", "name": "贵州茅台"}
        # 第一次写入（立即已验证）
        self.cache_mod.set_cache("basic_info", "test_func", data, 3600,
                                 cross_verify=True)
        # 第二次写入相同数据（刷新过期时间）
        self.cache_mod.set_cache("basic_info", "test_func", data, 3600,
                                 cross_verify=True)
        # 已验证，读取应返回数据
        result = self.cache_mod.get_cache("basic_info", "test_func",
                                          cross_verify=True)
        self.assertIsNotNone(result)
        self.assertEqual(result["code"], "600519")
        self.assertEqual(result["name"], "贵州茅台")

    def test_second_write_diff_updates(self):
        """测试3：第二次写入不同数据 → 用新数据替换并保持已验证 → 读取返回新数据。"""
        data1 = {"code": "600519", "name": "贵州茅台"}
        data2 = {"code": "600519", "name": "贵州茅台2"}
        # 第一次写入
        self.cache_mod.set_cache("basic_info", "test_func", data1, 3600,
                                 cross_verify=True)
        # 第二次写入不同数据 → 用新数据替换，保持 verified=1
        self.cache_mod.set_cache("basic_info", "test_func", data2, 3600,
                                 cross_verify=True)
        # 读取应返回新数据 data2
        result = self.cache_mod.get_cache("basic_info", "test_func",
                                          cross_verify=True)
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "贵州茅台2")

    def test_verified_allows_overwrite(self):
        """测试4：已验证的数据会被新写入的不同数据替换。"""
        data1 = {"code": "600519", "name": "贵州茅台"}
        data2 = {"code": "600519", "name": "新数据"}
        # 验证通过
        self.cache_mod.set_cache("basic_info", "test_func", data1, 3600,
                                 cross_verify=True)
        # 写入不同数据 → 替换为新数据
        self.cache_mod.set_cache("basic_info", "test_func", data2, 3600,
                                 cross_verify=True)
        # 读取的是新数据 data2
        result = self.cache_mod.get_cache("basic_info", "test_func",
                                          cross_verify=True)
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "新数据")

    def test_cached_decorator_integration(self):
        """测试5：@cached 装饰器集成测试（首次调用即写入已验证，二次调用走缓存）。"""
        call_count = [0]
        data = {"code": "600519", "name": "贵州茅台"}

        @self.cache_mod.cached(category="basic_info", ttl_seconds=3600,
                               cross_verify=True)
        def my_func(code):
            call_count[0] += 1
            return data

        # 第一次调用：未命中缓存，执行函数，写入已验证
        call_count[0] = 0
        result1 = my_func("600519")
        self.assertEqual(call_count[0], 1)
        self.assertEqual(result1["code"], "600519")

        # 第二次调用：已验证，直接返回缓存，不执行函数
        result2 = my_func("600519")
        self.assertEqual(call_count[0], 1)
        self.assertEqual(result2["code"], "600519")

        # 第三次调用：仍走缓存，不执行函数
        result3 = my_func("600519")
        self.assertEqual(call_count[0], 1)
        self.assertEqual(result3["code"], "600519")

    def test_list_data_verify(self):
        """测试6：列表数据的交叉验证。"""
        data = [{"date": "2024-01-01", "value": 100},
                {"date": "2024-01-02", "value": 200}]
        # 第一次写入（立即已验证）
        self.cache_mod.set_cache("financial", "test_list", data, 3600,
                                 cross_verify=True)
        # 第二次写入相同数据（刷新过期时间）
        self.cache_mod.set_cache("financial", "test_list", data, 3600,
                                 cross_verify=True)
        # 验证通过
        result = self.cache_mod.get_cache("financial", "test_list",
                                          cross_verify=True)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["value"], 100)

    def test_normal_mode_no_verify(self):
        """测试7：普通模式（cross_verify=False）不受影响。"""
        data = {"code": "600519", "name": "贵州茅台"}
        self.cache_mod.set_cache("kline", "test_normal", data, 3600,
                                 cross_verify=False)
        # 普通模式读取应直接返回
        result = self.cache_mod.get_cache("kline", "test_normal",
                                          cross_verify=False)
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "贵州茅台")


if __name__ == "__main__":
    unittest.main(verbosity=2)

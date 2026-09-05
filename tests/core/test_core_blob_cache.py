# -*- coding: utf-8 -*-
"""tests/core/test_core_blob_cache.py — V17.0.15 通用对象磁盘缓存

审查背景（Request H：统一层 / 缓存层复核）：
  `em_get`（sc_network.py）只有**令牌桶限流 + 熔断**，**没有任何数据缓存**。
  V17.0.14 把 CYQ 接到东财 push2 kline 后，全仓扫描时 sht/med/lng 各调一次
  `get_cyq_distribution` → **3N 次东财请求**；而 push2 系是**连接级风控**
  （RemoteDisconnected，字典 §12.3 实测恢复 20+ 小时），会连带打挂资金流/行情。

  故 V17.0.15 在 sc_kline_cache 增加一对类型无关的 `get_cached_blob` /
  `set_cached_blob`（复用同一 TTL 24h / LRU 500MB / 原子写 / 锁），CYQ 走这对接口。

本文件验证**缓存层机制本身**（不依赖网络）：
  1. 往返一致性（任意 pickle 对象）
  2. 命名空间隔离（CYQ 与 D 不串）
  3. TTL 过期失效
  4. 损坏文件 → None（不抛异常，调用方回退网络）
  5. 写入失败静默（不可 pickle 对象不阻塞主流程）
  6. 原子写（不残留 .pkl.tmp）
"""
from __future__ import annotations

import os
import pickle
import sys
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_common import sc_kline_cache as kc


class _TempBlobCache(unittest.TestCase):
    """把缓存目录临时指向 tmp_path，避免污染真实 cache/kline/。

    注意：`_cache_path` 每次调用都会走 `_get_cache_dir()`，因此 patch
    `_get_cache_dir` 即可整体重定向，无需改模块常量。
    """

    def setUp(self):
        import tempfile
        from unittest.mock import patch

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp_dir = self._tmp.name
        _patcher = patch.object(kc, "_get_cache_dir", lambda: __import__("pathlib").Path(self.tmp_dir))
        _patcher.start()
        self.addCleanup(_patcher.stop)


class TestBlobRoundTrip(_TempBlobCache):
    """1. 任意可 pickle 对象的往返一致性。"""

    def test_dict_roundtrip(self):
        payload = {
            "benefit_pct": 62.5,
            "avg_cost": 11.83,
            "cost_90_low": 9.1,
            "cost_90_high": 14.7,
            "concentration_90": 0.235,
            "source": "eastmoney_kline_f61",
        }
        self.assertIsNone(kc.get_cached_blob("CYQ", "600519", 240))
        kc.set_cached_blob("CYQ", "600519", 240, payload)
        self.assertEqual(kc.get_cached_blob("CYQ", "600519", 240), payload)

    def test_list_and_scalar_roundtrip(self):
        kc.set_cached_blob("PAT", "000001", 60, ["bullish_engulfing", "hammer"])
        self.assertEqual(kc.get_cached_blob("PAT", "000001", 60), ["bullish_engulfing", "hammer"])
        kc.set_cached_blob("SCALAR", "000002", 1, 3.14159)
        self.assertEqual(kc.get_cached_blob("SCALAR", "000002", 1), 3.14159)

    def test_miss_returns_none(self):
        self.assertIsNone(kc.get_cached_blob("CYQ", "999999", 240))


class TestBlobNamespaceIsolation(_TempBlobCache):
    """2. 命名空间隔离：CYQ / D / PAT 互不串数据。"""

    def test_namespaces_do_not_collide(self):
        kc.set_cached_blob("CYQ", "600519", 240, {"kind": "cyq"})
        kc.set_cached_blob("D", "600519", 240, {"kind": "kline"})
        kc.set_cached_blob("PAT", "600519", 240, {"kind": "pattern"})
        self.assertEqual(kc.get_cached_blob("CYQ", "600519", 240), {"kind": "cyq"})
        self.assertEqual(kc.get_cached_blob("D", "600519", 240), {"kind": "kline"})
        self.assertEqual(kc.get_cached_blob("PAT", "600519", 240), {"kind": "pattern"})

    def test_count_param_is_part_of_key(self):
        kc.set_cached_blob("CYQ", "600519", 120, {"days": 120})
        kc.set_cached_blob("CYQ", "600519", 240, {"days": 240})
        self.assertEqual(kc.get_cached_blob("CYQ", "600519", 120), {"days": 120})
        self.assertEqual(kc.get_cached_blob("CYQ", "600519", 240), {"days": 240})

    def test_blob_does_not_pollute_kline_namespace(self):
        """get_cached_kline 与 get_cached_blob 共用目录但按 (period,code,count) 区分。"""
        kc.set_cached_blob("CYQ", "000651", 240, {"kind": "cyq"})
        # 同一 code/count 但 period="D" 的 K 线槽位应仍为空
        self.assertIsNone(kc.get_cached_kline("D", "000651", 240))


class TestBlobTTL(_TempBlobCache):
    """3. TTL 过期失效（默认 24h）。"""

    def test_expired_entry_returns_none_and_is_deleted(self):
        from pathlib import Path

        kc.set_cached_blob("CYQ", "600036", 240, {"v": 1})
        p = Path(self.tmp_dir) / "CYQ_600036_240_v2.pkl"
        self.assertTrue(p.exists())
        # 把 mtime 回拨到 TTL 之外
        old = time.time() - (kc.CACHE_TTL_SECONDS + 60)
        os.utime(p, (old, old))
        self.assertIsNone(kc.get_cached_blob("CYQ", "600036", 240))
        self.assertFalse(p.exists(), "过期文件应被主动删除，而不是留在盘上占 LRU 额度")

    def test_fresh_entry_survives(self):
        kc.set_cached_blob("CYQ", "600036", 240, {"v": 1})
        self.assertEqual(kc.get_cached_blob("CYQ", "600036", 240), {"v": 1})

    def test_schema_version_is_in_filename(self):
        """V16.2: 键含 schema 版本——升级后旧结构缓存自动失效而非静默复用。"""
        from pathlib import Path

        kc.set_cached_blob("CYQ", "600030", 240, {"v": 1})
        names = [f.name for f in Path(self.tmp_dir).glob("*.pkl")]
        self.assertTrue(any(kc._KLINE_CACHE_SCHEMA_VERSION in n for n in names), names)


class TestBlobRobustness(_TempBlobCache):
    """4-6. 鲁棒性：损坏文件 / 不可 pickle / 原子写。"""

    def test_corrupted_file_returns_none(self):
        from pathlib import Path

        p = Path(self.tmp_dir) / "CYQ_601318_240_v2.pkl"
        p.write_bytes(b"\x00\x01not-a-pickle\xff")
        # 不得抛异常——调用方要能回退到网络请求
        self.assertIsNone(kc.get_cached_blob("CYQ", "601318", 240))

    def test_unpicklable_object_does_not_raise(self):
        """写入失败必须静默（缓存是优化，不能阻塞主流程）。"""
        kc.set_cached_blob("CYQ", "601318", 240, lambda: None)  # lambda 不可 pickle
        self.assertIsNone(kc.get_cached_blob("CYQ", "601318", 240))

    def test_no_tmp_files_left_after_success(self):
        from pathlib import Path

        kc.set_cached_blob("CYQ", "600887", 240, {"v": 1})
        leftovers = list(Path(self.tmp_dir).glob("*.tmp"))
        self.assertEqual(leftovers, [], f"原子写应只留 .pkl，不应残留 {leftovers}")

    def test_clear_by_namespace(self):
        kc.set_cached_blob("CYQ", "000001", 240, {"v": 1})
        kc.set_cached_blob("CYQ", "000002", 240, {"v": 1})
        kc.set_cached_blob("PAT", "000001", 60, {"v": 1})
        cleared = kc.clear_kline_cache("CYQ")
        self.assertEqual(cleared, 2)
        self.assertIsNone(kc.get_cached_blob("CYQ", "000001", 240))
        self.assertEqual(kc.get_cached_blob("PAT", "000001", 60), {"v": 1})

    def test_blob_api_is_exported(self):
        self.assertIn("get_cached_blob", kc.__all__)
        self.assertIn("set_cached_blob", kc.__all__)


if __name__ == "__main__":
    unittest.main()

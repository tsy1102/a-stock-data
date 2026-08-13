"""test_cache.py — 统一缓存层 (stock_cache) 单元测试。

重点测试：
  - set_cache / get_cache 基本读写
  - TTL 过期行为
  - invalidate_category / invalidate_prefix
  - cached 装饰器
  - cache_stats
  - STOCK_NOCACHE=1 环境变量禁用
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path

import pytest


def test_set_get_cache_basic(tmp_path, monkeypatch):
    """set_cache → get_cache 读取同一值。"""
    import core.stock_cache as sc

    # 把缓存 DB 指到临时目录
    fake_cache_db = tmp_path / "stock_cache.db"
    monkeypatch.setattr(sc, "_CACHE_DB", str(fake_cache_db))
    # 重置 DB 连接
    monkeypatch.setattr(sc, "_db", None)
    # 清除禁用
    monkeypatch.setattr(sc, "_DISABLE_CACHE", False)

    sc.set_cache("basic", "test_func", {"value": 42}, 3600, "code-001")
    result = sc.get_cache("basic", "test_func", "code-001")
    assert result == {"value": 42}


def test_get_cache_missing_returns_none(tmp_path, monkeypatch):
    """未写入的数据应返回 None。"""
    import core.stock_cache as sc

    fake_cache_db = tmp_path / "stock_cache.db"
    monkeypatch.setattr(sc, "_CACHE_DB", str(fake_cache_db))
    monkeypatch.setattr(sc, "_db", None)
    monkeypatch.setattr(sc, "_DISABLE_CACHE", False)

    assert sc.get_cache("nonexist", "nothing") is None


def test_cache_ttl_expiry(tmp_path, monkeypatch):
    """TTL 过期后应返回 None。"""
    import core.stock_cache as sc

    fake_cache_db = tmp_path / "stock_cache.db"
    monkeypatch.setattr(sc, "_CACHE_DB", str(fake_cache_db))
    monkeypatch.setattr(sc, "_db", None)
    monkeypatch.setattr(sc, "_DISABLE_CACHE", False)

    _fake_time = [1000.0]
    monkeypatch.setattr(time, "time", lambda: _fake_time[0])

    sc.set_cache("ttl_test", "short_lived", {"data": "expired"}, 10)  # 10 秒 TTL
    assert sc.get_cache("ttl_test", "short_lived") == {"data": "expired"}

    # 模拟时间流逝到过期后
    _fake_time[0] = 1011.0  # 11 秒后，已过期
    assert sc.get_cache("ttl_test", "short_lived") is None


def test_invalidate_category(tmp_path, monkeypatch):
    """按分类批量删除（V12.1+ 自动同步清空 L1 内存缓存）。"""
    import core.stock_cache as sc

    fake_cache_db = tmp_path / "stock_cache.db"
    monkeypatch.setattr(sc, "_CACHE_DB", str(fake_cache_db))
    monkeypatch.setattr(sc, "_db", None)
    monkeypatch.setattr(sc, "_DISABLE_CACHE", False)

    sc.set_cache("cat_A", "f1", {"v": 1}, 3600, "code-1")
    sc.set_cache("cat_A", "f2", {"v": 2}, 3600, "code-2")
    sc.set_cache("cat_B", "f3", {"v": 3}, 3600, "code-3")

    deleted = sc.invalidate_category("cat_A")
    assert deleted >= 2  # 删除数应至少 2

    # V12.1: invalidate_category 已自动同步清空 L1，无需手动 _L1_CACHE.clear()

    # A 类应读不到
    assert sc.get_cache("cat_A", "f1", "code-1") is None
    assert sc.get_cache("cat_A", "f2", "code-2") is None
    # B 类应完好
    assert sc.get_cache("cat_B", "f3", "code-3") == {"v": 3}


def test_invalidate_prefix(tmp_path, monkeypatch):
    """按 key 前缀批量删除（V12.1+ 自动同步清空 L1 内存缓存）。"""
    import core.stock_cache as sc

    fake_cache_db = tmp_path / "stock_cache.db"
    monkeypatch.setattr(sc, "_CACHE_DB", str(fake_cache_db))
    monkeypatch.setattr(sc, "_db", None)
    monkeypatch.setattr(sc, "_DISABLE_CACHE", False)

    sc.set_cache("prefix_a", "f1", {"v": 1}, 3600)
    sc.set_cache("prefix_a", "f2", {"v": 2}, 3600, "x")
    sc.set_cache("other", "f3", {"v": 3}, 3600)

    # invalidate_prefix 匹配的是原始 key 前缀
    # key 格式为 "category:func_name[_arg1[_arg2]...]"（见 _build_key）
    deleted = sc.invalidate_prefix("prefix_a:")
    assert deleted >= 2

    # V12.1: invalidate_prefix 已自动同步清空 L1，无需手动 _L1_CACHE.clear()

    assert sc.get_cache("prefix_a", "f1") is None
    assert sc.get_cache("other", "f3") == {"v": 3}


def test_cache_stats(tmp_path, monkeypatch):
    """cache_stats 应返回 dict 且含 total_entries 字段。"""
    import core.stock_cache as sc

    fake_cache_db = tmp_path / "stock_cache.db"
    monkeypatch.setattr(sc, "_CACHE_DB", str(fake_cache_db))
    monkeypatch.setattr(sc, "_db", None)
    monkeypatch.setattr(sc, "_DISABLE_CACHE", False)

    sc.set_cache("stats_test", "f1", {"x": 1}, 3600)
    sc.set_cache("stats_test", "f2", {"x": 2}, 3600)

    stats = sc.cache_stats()
    assert isinstance(stats, dict)
    assert "total_entries" in stats
    assert stats["total_entries"] >= 2
    assert "db_size_bytes" in stats
    assert "by_category" in stats


def test_cached_decorator_sync(tmp_path, monkeypatch):
    """@cached 装饰器 - 二次调用应走缓存。"""
    import core.stock_cache as sc

    fake_cache_db = tmp_path / "stock_cache.db"
    monkeypatch.setattr(sc, "_CACHE_DB", str(fake_cache_db))
    monkeypatch.setattr(sc, "_db", None)
    monkeypatch.setattr(sc, "_DISABLE_CACHE", False)

    call_count = [0]

    @sc.cached(category="decorator_test", ttl_seconds=3600)
    def compute_value(code: str):
        call_count[0] += 1
        return {"code": code, "price": 42.0}

    # 首次调用
    r1 = compute_value("600519")
    assert r1["price"] == 42.0
    assert call_count[0] == 1

    # 二次调用应走缓存（函数不再被调用）
    r2 = compute_value("600519")
    assert r2["price"] == 42.0
    assert call_count[0] == 1  # 函数未被重新调用


def test_disable_cache_via_env(tmp_path, monkeypatch):
    """STOCK_NOCACHE=1 应禁用所有缓存。"""
    import core.stock_cache as sc

    fake_cache_db = tmp_path / "stock_cache.db"
    monkeypatch.setattr(sc, "_CACHE_DB", str(fake_cache_db))
    monkeypatch.setattr(sc, "_db", None)
    monkeypatch.setattr(sc, "_DISABLE_CACHE", True)  # 模拟环境变量

    sc.set_cache("disabled_test", "f1", {"v": 1}, 3600)
    assert sc.get_cache("disabled_test", "f1") is None


def test_empty_value_not_written(tmp_path, monkeypatch):
    """None / 空 list / 空 dict 不应被写入缓存。"""
    import core.stock_cache as sc

    fake_cache_db = tmp_path / "stock_cache.db"
    monkeypatch.setattr(sc, "_CACHE_DB", str(fake_cache_db))
    monkeypatch.setattr(sc, "_db", None)
    monkeypatch.setattr(sc, "_DISABLE_CACHE", False)

    sc.set_cache("empty_test", "f1", None, 3600)
    sc.set_cache("empty_test", "f2", [], 3600)
    sc.set_cache("empty_test", "f3", {}, 3600)

    assert sc.get_cache("empty_test", "f1") is None
    assert sc.get_cache("empty_test", "f2") is None
    assert sc.get_cache("empty_test", "f3") is None


def test_build_key(tmp_path, monkeypatch):
    """_build_key 应根据参数生成稳定的 key。"""
    import core.stock_cache as sc

    k1 = sc._build_key("cat", "func", "600519")
    k2 = sc._build_key("cat", "func", "600519")
    k3 = sc._build_key("cat", "func", "000001")

    assert k1 == k2
    assert k1 != k3
    assert isinstance(k1, str) and len(k1) > 0


class FakeDateTime:
    """模拟 datetime：now() 返回固定时刻，combine 委托真实 datetime。"""

    def __init__(self, target):
        from datetime import datetime as _real
        self._real = _real
        self._target = target

    def now(self):
        return self._target

    def combine(self, *args, **kwargs):
        return self._real.combine(*args, **kwargs)


@pytest.mark.parametrize(
    "fake_time, expect_date",
    [
        # 工作日 8:15 → 数据日=上一交易日 → 今天 9:30 过期
        ("2026-12-04 08:15:00", "2026-12-04"),
        # 工作日 9:00 → 同上（9:30 分界前）
        ("2026-12-04 09:00:00", "2026-12-04"),
        # 工作日 9:30 → 数据日=今天 → 下个交易日 9:30 过期
        ("2026-12-04 09:30:00", "2026-12-07"),
        # V16.3 O29 回归：周六 9:15 非交易日 → 下个交易日 9:30（原 bug：立即过期）
        ("2026-12-05 09:15:00", "2026-12-07"),
        # 国庆 9:00 非交易日 → 下个交易日 9:30（原 bug 同样命中）
        ("2026-10-01 09:00:00", "2026-10-08"),
    ],
)
def test_calc_trading_day_expiry(tmp_path, monkeypatch, fake_time, expect_date):
    """V16.3 O29 回归：_calc_trading_day_expiry 的 9:30 分界 + 非交易日不过期。

    注意：fake 时间必须用未来日期（真实运行时刻之后），否则 target 早于真实 now，
    触发内部"expires_at 必须大于 now"安全检查 → fallback +24h（这是正确行为，
    非测试目标）。本例验证的是分界逻辑本身。
    """
    from datetime import datetime as real_dt

    import core.stock_cache as sc

    fake = FakeDateTime(real_dt.strptime(fake_time, "%Y-%m-%d %H:%M:%S"))
    monkeypatch.setattr(sc, "datetime", fake)

    expiry = sc._calc_trading_day_expiry()
    expire_dt = real_dt.fromtimestamp(expiry)
    assert expire_dt.strftime("%Y-%m-%d %H:%M") == f"{expect_date} 09:30"

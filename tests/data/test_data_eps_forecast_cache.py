"""EPS 预测缓存合同：只持久化非空 DataFrame，保留原始列结构。"""

from __future__ import annotations

from datetime import datetime

import pandas as pd


def _run_immediate(awaitable):
    """驱动不含真实 I/O 的测试协程，避免 Windows Proactor socketpair 初始化。"""
    try:
        awaitable.send(None)
    except StopIteration as completed:
        return completed.value
    awaitable.close()
    raise AssertionError("test fetch unexpectedly suspended and requires an event loop")


def test_async_eps_forecast_uses_daily_cache(monkeypatch):
    from stock_common.sc_datasource import _financials

    calls = []

    async def fake_fetch(session, code):
        calls.append(code)
        return pd.DataFrame(
            [["2026E", 3, 1.1, 1.2, 1.3, 0.8]],
            columns=["年度", "机构数", "最小值", "均值", "最大值", "行业均值"],
        )

    monkeypatch.setattr(_financials, "_fetch_eps_forecast_async", fake_fetch)
    first = _run_immediate(_financials.get_eps_forecast_async(object(), "600519"))
    second = _run_immediate(_financials.get_eps_forecast_async(object(), "600519"))

    assert calls == ["600519"]
    assert list(first.columns) == ["年度", "机构数", "最小值", "均值", "最大值", "行业均值"]
    pd.testing.assert_frame_equal(first, second)


def test_empty_async_eps_forecast_is_not_cached(monkeypatch):
    from core.stock_cache import get_cache
    from stock_common.sc_datasource import _financials

    calls = []

    async def fake_fetch(session, code):
        calls.append(code)
        return pd.DataFrame()

    monkeypatch.setattr(_financials, "_fetch_eps_forecast_async", fake_fetch)
    _run_immediate(_financials.get_eps_forecast_async(object(), "000001"))
    _run_immediate(_financials.get_eps_forecast_async(object(), "000001"))

    cache_args = ("000001", datetime.now().strftime("%Y-%m-%d"))
    assert calls == ["000001", "000001"]
    assert get_cache("eps_forecast", "get_eps_forecast_async", *cache_args) is None


def test_sync_eps_forecast_network_path_uses_daily_cache(monkeypatch):
    from stock_common.sc_datasource import _financials

    calls = []
    expected = pd.DataFrame(
        [["2026E", 3, 1.1, 1.2, 1.3, 0.8]],
        columns=["年度", "机构数", "最小值", "均值", "最大值", "行业均值"],
    )

    def fake_fetch(code, local_only=False):
        calls.append((code, local_only))
        return expected

    monkeypatch.setattr(_financials, "_fetch_eps_forecast", fake_fetch)
    first = _financials.get_eps_forecast("600519")
    second = _financials.get_eps_forecast("600519")

    assert calls == [("600519", False)]
    pd.testing.assert_frame_equal(first, second)


def test_local_only_eps_forecast_bypasses_persistent_cache(monkeypatch):
    from stock_common.sc_datasource import _financials

    calls = []
    expected = pd.DataFrame([["2026E"]], columns=["年度"])

    def fake_fetch(code, local_only=False):
        calls.append(local_only)
        return expected

    monkeypatch.setattr(_financials, "_fetch_eps_forecast", fake_fetch)
    _financials.get_eps_forecast("600519", local_only=True)
    _financials.get_eps_forecast("600519", local_only=True)

    assert calls == [True, True]

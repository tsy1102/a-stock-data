"""test_data_prefetch.py — sht 批量行情预取字段映射（V16.4.0）。

覆盖：
  - prefetch_quote_batch 字段映射（f2 价格/f15-18 OHLC/f20-21 市值等）
  - 单位换算（f6 元→万、f20/f21 元→亿）
  - 估值字段不预取（ulist 实测不返回 → None/0）
  - 缓存命中（二次调用不重复请求）
"""
from __future__ import annotations

import pytest


@pytest.fixture()
def clean_batch_cache(monkeypatch):
    """清空并隔离 _BATCH_QUOTE_CACHE。"""
    import core.data_provider as dp

    monkeypatch.setattr(dp, "_BATCH_QUOTE_CACHE", {})
    monkeypatch.setattr(dp, "_BATCH_QUOTE_DATE", "")
    return dp


def _fake_ulist_response():
    """模拟 push2delay ulist 返回（f2 价格/f3 涨跌/f15-18 OHLC/f20-21 市值/估值缺失）。"""
    return {
        "rc": 0,
        "data": {
            "diff": [
                {
                    "f2": "1346.50", "f3": "-0.17", "f4": "-2.36", "f5": "27073",
                    "f6": "3640046368.00", "f8": "0.22", "f12": "600519", "f14": "贵州茅台",
                    "f15": "1352.65", "f16": "1338.00", "f17": "1348.00", "f18": "1348.86",
                    "f20": "1683234875747", "f21": "1683234875747",
                    # ulist 实测估值字段不返回（"-"）
                    "f51": "-", "f126": "-", "f162": "-", "f163": "-", "f167": "-", "f174": "-",
                }
            ]
        },
    }


def test_prefetch_field_mapping(clean_batch_cache, monkeypatch):
    """核心字段映射 + 单位换算正确。"""
    dp = clean_batch_cache
    captured = {}

    class FakeResp:
        def json(self):
            return _fake_ulist_response()

    def _fake_request(url, **kwargs):
        captured["url"] = url
        return FakeResp()

    monkeypatch.setattr("stock_common._quick_request", _fake_request)
    r = dp.prefetch_quote_batch(["600519"])
    assert "600519" in r
    d = r["600519"]
    assert d["price"] == pytest.approx(1346.50)
    assert d["change_pct"] == pytest.approx(-0.17)
    assert d["high"] == pytest.approx(1352.65)
    assert d["low"] == pytest.approx(1338.00)
    assert d["open"] == pytest.approx(1348.00)
    assert d["prev_close"] == pytest.approx(1348.86)
    assert d["amount_wan"] == pytest.approx(3640046368.0 / 1e4)   # 元 → 万
    assert d["mcap_yi"] == pytest.approx(1683234875747 / 1e8)     # 元 → 亿
    assert d["name"] == "贵州茅台"
    # 估值字段不预取（ulist 不返回）
    assert d.get("pe_ttm") in (None, 0.0)
    assert d.get("pb") in (None, 0.0)
    assert "ulist.np" in captured["url"]


def test_prefetch_cache_hit_no_duplicate(clean_batch_cache, monkeypatch):
    """二次调用命中缓存，不再发请求。"""
    dp = clean_batch_cache
    call_count = {"n": 0}

    class FakeResp:
        def json(self):
            return _fake_ulist_response()

    def _fake_request(url, **kwargs):
        call_count["n"] += 1
        return FakeResp()

    monkeypatch.setattr("stock_common._quick_request", _fake_request)
    dp.prefetch_quote_batch(["600519"])
    dp.prefetch_quote_batch(["600519"])   # 缓存命中
    assert call_count["n"] == 1


def test_prefetch_300_chunk(clean_batch_cache, monkeypatch):
    """>300 只按 300/批分块请求。"""
    dp = clean_batch_cache
    urls = []

    class FakeResp:
        def json(self):
            return {"rc": 0, "data": {"diff": []}}

    def _fake_request(url, **kwargs):
        urls.append(url)
        return FakeResp()

    monkeypatch.setattr("stock_common._quick_request", _fake_request)
    codes = [f"{i:06d}" for i in range(601)]
    dp.prefetch_quote_batch(codes)
    assert len(urls) == 3   # 300 + 300 + 1

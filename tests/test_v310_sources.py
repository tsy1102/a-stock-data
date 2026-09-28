# -*- coding: utf-8 -*-
"""tests/test_v310_sources.py — 上游 3.10.0 两个新取数能力(腾讯逐笔 / 新浪期货日K) 的移植测试.

同步范围(经 2026-09-23 上游 v3.10.0 核对 + 用户授权采纳):
  - 腾讯逐笔成交 tencent_ticks (上游 §1.4, 替代失效 mootdx transaction)
  - 新浪期货日K futures_kline_sina (上游 §13.7, 补大商所历史日线)

测试分层:
  1) 纯解析函数离线测试(_parse_*) — 用抓取的真实结构样本, 不触网。
  2) 错误契约测试(ValueError / RuntimeError 边界) — 不触网。
  3) 端到端测试 — 用 unittest.mock 替换 _quick_request, 复现网络返回结构。
  4) 联网冒烟测试(@pytest.mark.real_network) — 需 REAL_NETWORK=1 才运行, 默认跳过。

设计对齐上游错误契约: 参数错/确实无数据 → ValueError; 源格式变 → RuntimeError。
"""

from __future__ import annotations

import os
import sys
from unittest import mock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_common.sc_datasource._ticks import (
    tencent_ticks,
    _parse_qt_snapshot,
    _parse_tick_page,
    TENCENT_QT_URL,
    TENCENT_TICK_URL,
)
from stock_common.sc_datasource._futures_sina import (
    futures_kline_sina,
    _parse_futures_payload,
    SINA_FUT_KLINE_URL,
)


# ─── 离线夹具(结构取自 2026-09-22 实测的源返回) ───
def _make_snapshot(symbol, date14, amount):
    """构造腾讯行情快照文本: 50 个 ~ 分隔字段, [30]=14位日期, [35]=价/量/额。"""
    fields = [str(i) for i in range(50)]
    fields[30] = date14
    fields[35] = f"10.50/1000000/{amount}"
    return f'v_{symbol}="' + "~".join(fields) + '"'


SNAP_SH = _make_snapshot("sh600519", "20260922150000", "1500000000.00")

TICK_PAGE_0 = (
    'v_detail_data_sh600519=[0,'
    '"1/09:25:00/1500.00/0.00/100/15000000.00/B'
    '|2/09:30:05/1501.00/1.00/200/300200.00/S'
    '|3/15:01:00/1499.00/-2.00/50/74950.00/M"]'
)

FUT_RB0 = (
    'var _RB0=('
    '[{"d":"2026-09-18","o":"3500.0","h":"3520.0","l":"3490.0","c":"3510.0","v":"100000","p":"500000","s":"3512.0"},'
    '{"d":"2026-09-19","o":"3510.0","h":"3530.0","l":"3505.0","c":"3520.0","v":"120000","p":"510000","s":"0"}'
    '])'
)

FUT_NULL = 'var _RB9999=(null);'


class _FakeResp:
    """复现 requests.Response 的最小接口(.content / .url)。"""

    def __init__(self, content, url="http://fake.local"):
        self.content = (
            content if isinstance(content, (bytes, bytearray)) else content.encode("utf-8")
        )
        self.url = url
        self.status_code = 200


# ─── 1) 纯解析函数离线测试 ───
def test_parse_qt_snapshot_ok():
    day, clock, amount = _parse_qt_snapshot("sh600519", SNAP_SH)
    assert day == "2026-09-22"
    assert clock == "150000"
    assert amount == 1500000000.0


def test_parse_qt_snapshot_none_match():
    with pytest.raises(ValueError):
        _parse_qt_snapshot("sh600519", 'v_pv_none_match="1~...~"')


def test_parse_qt_snapshot_bad_fields():
    bad = 'v_sh600519="' + "~".join(["x"] * 10) + '"'  # 字段不足 36
    with pytest.raises(RuntimeError):
        _parse_qt_snapshot("sh600519", bad)


def test_parse_tick_page_ok():
    recs = _parse_tick_page("sh600519", 0, TICK_PAGE_0)
    assert recs is not None
    assert len(recs) == 3
    assert recs[0] == {
        "seq": 1,
        "time": "09:25:00",
        "price": 1500.0,
        "change": 0.0,
        "volume": 100,
        "amount": 15000000.0,
        "side": "B",
    }
    assert recs[2]["side"] == "M"


def test_parse_tick_page_empty():
    # 翻过末页腾讯返回空内容 → None
    assert _parse_tick_page("sh600519", 1, "") is None


def test_parse_tick_page_bad_format():
    with pytest.raises(RuntimeError):
        _parse_tick_page("sh600519", 0, "garbage not matching")


def test_parse_tick_page_bad_side():
    bad = 'v_detail_data_sh600519=[0,"1/09:30:00/1.0/0.0/10/10.0/X"]'
    with pytest.raises(RuntimeError):
        _parse_tick_page("sh600519", 0, bad)


def test_parse_futures_payload_ok():
    rows = _parse_futures_payload("RB0", FUT_RB0)
    assert len(rows) == 2
    assert rows[0]["date"] == "2026-09-18"
    assert rows[0]["open"] == 3500.0
    assert rows[0]["close"] == 3510.0
    assert rows[0]["settle"] == 3512.0  # 有结算价
    assert rows[1]["settle"] is None  # s=0 → None
    assert rows[1]["open_interest"] == 510000.0


def test_parse_futures_payload_sorted():
    rows = _parse_futures_payload("RB0", FUT_RB0)
    assert [r["date"] for r in rows] == sorted(r["date"] for r in rows)


def test_parse_futures_payload_null():
    with pytest.raises(ValueError):
        _parse_futures_payload("RB9999", FUT_NULL)


def test_parse_futures_payload_bad_jsonp():
    with pytest.raises(RuntimeError):
        _parse_futures_payload("RB0", "totally not jsonp")


# ─── 2) 错误契约(不触网) ───
def test_tencent_ticks_bj_rejected():
    with pytest.raises(ValueError):
        tencent_ticks("bj830799")


def test_tencent_ticks_index_rejected():
    with pytest.raises(ValueError):
        tencent_ticks("sh000001")  # 上证指数
    with pytest.raises(ValueError):
        tencent_ticks("399001")  # 深证成指(默认 sz)


def test_futures_code_format_rejected():
    with pytest.raises(ValueError):
        futures_kline_sina("not-a-code!!")


def test_futures_start_after_end():
    with pytest.raises(ValueError):
        futures_kline_sina("RB0", start="2026-09-20", end="2026-09-18")


# ─── 3) 端到端(mock 网络) ───
def test_futures_kline_sina_date_filter_and_settle():
    def fake_qr(url, **kw):
        assert url.startswith("https://stock2.finance.sina.com.cn")
        return _FakeResp(FUT_RB0.encode("gbk"), url)

    with mock.patch("stock_common.sc_datasource._futures_sina._quick_request", side_effect=fake_qr):
        df = futures_kline_sina("RB0", start="2026-09-19")
    assert len(df) == 1
    assert df.iloc[0]["date"] == "2026-09-19"
    assert df.iloc[0]["settle"] is None  # s=0 → None
    assert df.iloc[0]["source"] == "sina"
    assert "source_url" in df.columns


def test_futures_kline_sina_empty_interval():
    empty = 'var _RB0=([]);'
    with mock.patch(
        "stock_common.sc_datasource._futures_sina._quick_request",
        return_value=_FakeResp(empty.encode("gbk"), SINA_FUT_KLINE_URL.format(code="RB0")),
    ):
        with pytest.raises(ValueError):
            futures_kline_sina("RB0", start="1990-01-01", end="1990-12-31")


def test_tencent_ticks_end_to_end():
    def fake_qr(url, **kw):
        if url.startswith(TENCENT_QT_URL):
            return _FakeResp(SNAP_SH.encode("gbk"), url)
        # tick page: p=0 返回 1 笔且成交额==快照成交额(核对通过); p>=1 空页终止
        p = (kw.get("params") or {}).get("p")
        if p == 0:
            single = 'v_detail_data_sh600519=[0,"0/09:30:05/1500.00/0.00/100/1500000000.00/B"]'
            return _FakeResp(single.encode("gbk"), url)
        return _FakeResp(b"", url)

    with mock.patch("stock_common.sc_datasource._ticks._quick_request", side_effect=fake_qr):
        df = tencent_ticks("sh600519")
    assert len(df) == 1
    assert df.iloc[0]["code"] == "sh600519"
    assert df.iloc[0]["amount"] == 1500000000.0
    assert df.attrs["missing_seq"] == []
    assert "source_url" in df.columns


def test_tencent_ticks_integrity_mismatch():
    # 逐笔合计(1.4e9) 与快照成交额(1.5e9) 差 > 0.1% → 收盘后核对抛 RuntimeError
    snap = _make_snapshot("sh600519", "20260922150000", "1500000000.00")
    bad_tick = 'v_detail_data_sh600519=[0,"0/09:30:05/1500.00/0.00/100/1400000000.00/B"]'

    def fake_qr(url, **kw):
        if url.startswith(TENCENT_QT_URL):
            return _FakeResp(snap.encode("gbk"), url)
        p = (kw.get("params") or {}).get("p")
        if p == 0:
            return _FakeResp(bad_tick.encode("gbk"), url)
        return _FakeResp(b"", url)

    with mock.patch("stock_common.sc_datasource._ticks._quick_request", side_effect=fake_qr):
        with pytest.raises(RuntimeError):
            tencent_ticks("sh600519")


# ─── 4) 联网冒烟(受控, 需 REAL_NETWORK=1) ───
@pytest.mark.real_network
def test_tencent_ticks_live():
    df = tencent_ticks("000001")
    assert not df.empty
    assert {"date", "code", "time", "seq", "price", "volume", "amount", "side"} <= set(df.columns)


@pytest.mark.real_network
def test_futures_kline_sina_live():
    df = futures_kline_sina("RB0", start="2026-09-01", end="2026-09-22")
    assert not df.empty
    assert {"date", "open", "high", "low", "close"} <= set(df.columns)

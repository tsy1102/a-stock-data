"""test_data_prefetch.py — sht 批量行情预取（V16.4.0 建立，2026-09-03 扩充）。

被测对象：`core.data_provider.prefetch_quote_batch`（sht 批量 35 只热路径）。

覆盖：
  - 字段映射（f2 价格 / f3 涨跌 / f15-18 OHLC / f20-21 市值）
  - 单位换算（f6 元→万、f20/f21 元→亿）
  - 估值字段不预取（ulist 实测返回 "-"）
  - 进程内缓存命中（二次调用不重复请求）
  - >300 只按 300/批分块
  - [2026-09-03 新增] 请求参数（push2delay 安全域 / fields 集合 / secids）
  - [2026-09-03 新增] 异常与空结果降级（"-" / 空 diff / None 响应 / 抛异常 / 缺 f12）

----------------------------------------------------------------------
DEBT-011 说明（见 docs/DEBT_LEDGER.md）:
    该函数内部直连裸 HTTP（违反公理 A1），计划下沉为
    `sc_datasource.get_em_ulist_batch()` 适配器。

    本文件是**下沉重构的等价性基准**：所有断言均基于**公开行为**
    （输入 codes → 输出映射字典），不依赖取数逻辑位于哪一层。
    下沉后这些断言必须原样通过，通过即证明行为等价。

Mock 策略（对重构免疫）:
    拦截在 `_quick_request` 层，**同时 patch `stock_common` 与
    `stock_common.sc_network` 两个模块属性**。原因：
      - 若只 mock 单点，重构后适配器改用另一种 import 形式
        （`from stock_common.sc_network import _quick_request`）即失效；
      - data_provider 与 sc_datasource 对该函数均为**函数内 import**
        （运行时取模块属性），故 patch 模块属性有效；
      - 不 mock 在 HTTP Session 层：`_quick_request` 与 `em_get` 使用不同
        Session（`_HTTP_SESSION` vs `EM_SESSION`），且 Session 层会真实执行
        令牌桶/熔断/封禁跳过，受风控状态影响而**不稳定**。

依赖: pytest（仅 Python API，见 AGENTS.md §2.1.1）。全程离线，无真实网络。
"""
from __future__ import annotations

import pytest

import stock_common
from stock_common import sc_network


# ── 测试数据：模拟 push2delay ulist.np 返回 ──────────────────────────────
# 注意：东财真实返回多为**字符串**（含 "-" 表示无数据），故此处保留字符串形态，
# 以覆盖被测代码的字符串→float 转换路径。
_FAKE_ROW_MAOTAI = {
    "f2": "1346.50", "f3": "-0.17", "f4": "-2.36", "f5": "27073",
    "f6": "3640046368.00", "f8": "0.22", "f12": "600519", "f14": "贵州茅台",
    "f15": "1352.65", "f16": "1338.00", "f17": "1348.00", "f18": "1348.86",
    "f20": "1683234875747", "f21": "1683234875747",
    # ulist 实测估值字段不返回（"-"）
    "f51": "-", "f126": "-", "f162": "-", "f163": "-", "f167": "-", "f174": "-",
}


class _FakeResp:
    """最小 requests.Response 替身：只实现被测代码用到的 .json()。"""

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


@pytest.fixture()
def clean_batch_cache(monkeypatch):
    """隔离 _BATCH_QUOTE_CACHE / _BATCH_QUOTE_DATE，保证用例间互不污染。

    V17.3.12 起 prefetch_quote_batch 还会读/写 SQLite L2 跨进程缓存
    (read_quote_batch_l2 / persist_quote_batch_l2)，必须一并隔离，
    否则旧缓存会绕过 _quick_request mock 直接回填结果、并污染后续用例。
    """
    import core.data_provider as dp
    import core.stock_cache as sc

    monkeypatch.setattr(dp, "_BATCH_QUOTE_CACHE", {})
    monkeypatch.setattr(dp, "_BATCH_QUOTE_DATE", "")
    # 隔离跨进程 L2 缓存层：只读返回空、写入 no-op
    # （prefetch_quote_batch 内部 `from core.stock_cache import ...` 函数内导入，
    #  monkeypatch 模块属性即可在调用时生效）
    monkeypatch.setattr(sc, "read_quote_batch_l2", lambda codes, **kw: {})
    monkeypatch.setattr(sc, "persist_quote_batch_l2", lambda *a, **kw: None)
    return dp


def _install_fake_http(monkeypatch, handler):
    """在 _quick_request 层替换取数（双点 patch，重构前后均生效）。"""
    monkeypatch.setattr(stock_common, "_quick_request", handler)
    monkeypatch.setattr(sc_network, "_quick_request", handler)


def _make_handler(rows=None, calls=None, exc=None):
    """构造 _quick_request 替身；rows=None 表示返回 None（模拟风控跳过）。"""
    def handler(url, params=None, headers=None, timeout=None, **kwargs):
        if calls is not None:
            calls.append({"url": url, "params": params})
        if exc is not None:
            raise exc
        if rows is None:
            return None
        return _FakeResp({"rc": 0, "data": {"diff": rows}})
    return handler


# ── 用例 1（V16.4.0 原有）：核心字段映射 + 单位换算 ──────────────────────
def test_prefetch_field_mapping(clean_batch_cache, monkeypatch):
    """核心字段映射 + 单位换算正确。"""
    dp = clean_batch_cache
    captured = {}

    def _fake_request(url, **kwargs):
        captured["url"] = url
        return _FakeResp({"rc": 0, "data": {"diff": [dict(_FAKE_ROW_MAOTAI)]}})

    _install_fake_http(monkeypatch, _fake_request)

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


# ── 用例 2（V16.4.0 原有）：进程内缓存命中，不重复请求 ───────────────────
def test_prefetch_cache_hit_no_duplicate(clean_batch_cache, monkeypatch):
    """二次调用命中缓存，不再发请求。"""
    dp = clean_batch_cache
    call_count = {"n": 0}

    def _fake_request(url, **kwargs):
        call_count["n"] += 1
        return _FakeResp({"rc": 0, "data": {"diff": [dict(_FAKE_ROW_MAOTAI)]}})

    _install_fake_http(monkeypatch, _fake_request)

    first = dp.prefetch_quote_batch(["600519"])
    second = dp.prefetch_quote_batch(["600519"])   # 缓存命中
    assert call_count["n"] == 1
    assert first == second


# ── 用例 3（V16.4.0 原有）：>300 只按 300/批分块 ─────────────────────────
def test_prefetch_300_chunk(clean_batch_cache, monkeypatch):
    """>300 只按 300/批分块请求。"""
    dp = clean_batch_cache
    calls = []

    def _fake_request(url, **kwargs):
        calls.append(kwargs.get("params") or {})
        return _FakeResp({"rc": 0, "data": {"diff": []}})

    _install_fake_http(monkeypatch, _fake_request)

    codes = [f"{i:06d}" for i in range(601)]
    dp.prefetch_quote_batch(codes)
    assert len(calls) == 3   # 300 + 300 + 1
    assert len(calls[0]["secids"].split(",")) == 300
    assert len(calls[2]["secids"].split(",")) == 1


# ── 用例 4（新增）：请求参数 —— 安全域 + 字段集 + secids ─────────────────
def test_prefetch_request_params(clean_batch_cache, monkeypatch):
    """★安全域断言：必须走 push2delay 镜像域，严禁 push2 主域（45000/h 封禁 20h）。"""
    dp = clean_batch_cache
    calls = []
    _install_fake_http(monkeypatch, _make_handler([dict(_FAKE_ROW_MAOTAI)], calls))

    dp.prefetch_quote_batch(["600519"])

    assert len(calls) == 1, "单只股票应只发 1 次请求"
    call = calls[0]
    assert "push2delay.eastmoney.com" in call["url"], "必须用 push2delay 镜像域，不得打 push2 主域"
    assert "ulist.np" in call["url"]
    assert "600519" in call["params"]["secids"]
    # 字段集必须与映射用到的键一一对应（防字段集与映射漂移）
    assert set(call["params"]["fields"].split(",")) == {
        "f2", "f3", "f4", "f5", "f6", "f8", "f12", "f14",
        "f15", "f16", "f17", "f18", "f20", "f21",
    }


# ── 用例 5（新增）：缺失值 "-" 降级为 0.0 ─────────────────────────────────
def test_prefetch_dash_missing_value_becomes_zero(clean_batch_cache, monkeypatch):
    """东财用 "-" 表示无数据 → 必须降级为 0.0（不得抛异常、不得为 None）。"""
    dp = clean_batch_cache
    row = dict(_FAKE_ROW_MAOTAI)
    row["f2"] = "-"
    row["f20"] = "-"
    _install_fake_http(monkeypatch, _make_handler([row]))

    d = dp.prefetch_quote_batch(["600519"])["600519"]

    assert d["price"] == 0.0
    assert d["mcap_yi"] == 0.0
    assert d["name"] == "贵州茅台"   # 其他字段不受影响


# ── 用例 6（新增）：空 diff / 无 data → 空结果 ───────────────────────────
@pytest.mark.parametrize("rows", [[], None])
def test_prefetch_empty_payload_returns_empty(clean_batch_cache, monkeypatch, rows):
    """响应为空或取数返回 None（风控跳过）时，返回空字典而非抛异常。"""
    dp = clean_batch_cache
    _install_fake_http(monkeypatch, _make_handler(rows))

    assert dp.prefetch_quote_batch(["600519"]) == {}


# ── 用例 7（新增）：取数抛异常被吞掉（不得中断报告生成）──────────────────
def test_prefetch_exception_is_swallowed(clean_batch_cache, monkeypatch):
    """热路径必须容错：取数异常不得冒泡中断 sht 报告。"""
    dp = clean_batch_cache
    _install_fake_http(monkeypatch, _make_handler(exc=RuntimeError("boom")))

    assert dp.prefetch_quote_batch(["600519"]) == {}


# ── 用例 8（新增）：缺 f12 代码的记录被跳过 ──────────────────────────────
def test_prefetch_skips_rows_without_code(clean_batch_cache, monkeypatch):
    """无代码的脏记录不得写入缓存（否则污染后续按 code 取值）。"""
    dp = clean_batch_cache
    row = dict(_FAKE_ROW_MAOTAI)
    row["f12"] = ""
    _install_fake_http(monkeypatch, _make_handler([row]))

    assert dp.prefetch_quote_batch(["600519"]) == {}

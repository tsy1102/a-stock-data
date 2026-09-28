# -*- coding: utf-8 -*-
"""tests/core/test_core_cyq.py — 筹码分布 CYQ 单测 (V17.0.14)

覆盖三层：
  1. calculate_cyq 纯算法（sc_technical）：字段完整性 + 数值健全性 + 边界
  2. get_cyq_distribution 数据入口（sc_datasource）：东财 kline f61 换手率解析 + 降级
  3. _score_holder 筹码面评分（sc_scoring）：集中度/获利盘加减分

背景（为什么现在才补）：
  calculate_cyq 自 V17.0.7 实现后长期是**死代码**——报告此前只用「股东户数」代理筹码面，
  该函数从未被管线调用，也**从未有单测**（sc_datasource 里"已单测"的注释是错的）。
  V17.0.14 经 get_cyq_distribution 接入 sht/med/lng 三报告的章节与评分，本文件补齐测试缺口。

换手率口径（接入时的关键结论，勿忘）：
  TDX 0x0010 日K（mootdx bars）与腾讯 ifzq fqkline **均无换手率字段**，而 CYQ 必需 OHLC+换手率；
  仅东财 push2 kline 的 f61=换手率(%) 是权威口径，故 get_cyq_distribution 走东财。
  若日后有人"改用 TDX 日K 省一次请求"，CYQ 会直接失效——本文件 test_parses_f61_turnover 会拦住。
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import stock_common.sc_datasource as sc_datasource
from stock_common.sc_datasource import get_cyq_distribution, _eastmoney

# V17.2.18 重构后片段为独立模块: _em_fflow_request 定义在 _eastmoney, get_cyq_distribution 经
# _eastmoney 命名空间解析; 故补丁须打在 _eastmoney._em_fflow_request (而非包级 re-export 副本)。
from stock_common.sc_scoring import ScoreData, _score_holder
from stock_common.sc_technical import calculate_cyq

# calculate_cyq 默认 crange=120 / cyq_days=210 → 样本量必须 > 120 才有非空窗口
_MIN_BARS = 240


def _mk_ohlc(n=_MIN_BARS, base=10.0, turnover=1.0):
    """构造 n 根日K：温和上涨 + 固定换手率(百分数, 如 1.0=1%)。"""
    dates, opens, closes, highs, lows, turns = [], [], [], [], [], []
    for i in range(n):
        c = round(base + i * 0.01, 2)
        dates.append(f"2026-{1 + (i // 28) % 12:02d}-{1 + (i % 28):02d}")
        opens.append(round(c - 0.05, 2))
        closes.append(c)
        highs.append(round(c + 0.08, 2))
        lows.append(round(c - 0.10, 2))
        turns.append(turnover)
    return dates, opens, closes, highs, lows, turns


class TestCalculateCyq(unittest.TestCase):
    """第 1 层：CYQ 纯算法。"""

    def test_returns_expected_keys(self):
        r = calculate_cyq(*_mk_ohlc())
        self.assertTrue(r, "正常输入应返回非空 dict")
        for k in (
            "benefit_pct",
            "avg_cost",
            "concentration_90",
            "concentration_70",
            "cost_90_low",
            "cost_90_high",
            "cost_70_low",
            "cost_70_high",
        ):
            self.assertIn(k, r, f"返回缺少字段 {k}")

    def test_ranges_sane(self):
        r = calculate_cyq(*_mk_ohlc())
        self.assertGreaterEqual(r["benefit_pct"], 0.0)
        self.assertLessEqual(r["benefit_pct"], 1.0)
        self.assertGreaterEqual(r["concentration_90"], 0.0)
        self.assertLessEqual(r["concentration_90"], 1.0)
        # 70% 区间是 90% 区间的子集 → 集中度应更小（值越小越集中）
        self.assertLessEqual(r["concentration_70"], r["concentration_90"] + 1e-9)
        self.assertLessEqual(r["cost_90_low"], r["cost_90_high"])
        self.assertLessEqual(r["cost_70_low"], r["cost_70_high"])

    def test_avg_cost_within_price_range(self):
        d, o, c, h, l, t = _mk_ohlc(base=10.0)
        r = calculate_cyq(d, o, c, h, l, t)
        self.assertGreaterEqual(r["avg_cost"], min(l) - 1e-6)
        self.assertLessEqual(r["avg_cost"], max(h) + 1e-6)

    def test_price_far_below_cost_gives_low_benefit(self):
        """末根收盘价远低于历史成本区 → 获利盘应接近 0（深度套牢）。"""
        d, o, c, h, l, t = _mk_ohlc(n=_MIN_BARS, base=10.0, turnover=0.5)
        c, h, l = list(c), list(h), list(l)
        c[-1], h[-1], l[-1] = 5.0, 5.2, 4.8  # 历史成本区 9.9~12.5，末根砸到 5 元
        r = calculate_cyq(d, o, c, h, l, t)
        self.assertLess(r["benefit_pct"], 0.25, "深度套牢时获利盘应极低")

    def test_price_far_above_cost_gives_high_benefit(self):
        """末根收盘价远高于历史成本区 → 获利盘应接近 1（普遍浮盈）。"""
        d, o, c, h, l, t = _mk_ohlc(n=_MIN_BARS, base=10.0, turnover=0.5)
        c, h, l = list(c), list(h), list(l)
        c[-1], h[-1], l[-1] = 30.0, 30.2, 29.8
        r = calculate_cyq(d, o, c, h, l, t)
        self.assertGreater(r["benefit_pct"], 0.85, "全面浮盈时获利盘应接近 1")

    def test_empty_and_short_input(self):
        self.assertEqual(calculate_cyq([], [], [], [], [], []), {})
        d, o, c, h, l, t = _mk_ohlc(n=1)
        self.assertEqual(calculate_cyq(d, o, c, h, l, t), {}, "单根K线不足以计算 → {}")

    def test_zero_turnover_yields_no_chips(self):
        """换手率全 0 → 无成交即无成本分布，返回 {}(应优雅降级，非抛异常/非零结果)。"""
        self.assertEqual(calculate_cyq(*_mk_ohlc(turnover=0.0)), {})

    def test_tiny_turnover_still_works(self):
        """极小换手率仍应算出分布（防除零/下溢）。"""
        r = calculate_cyq(*_mk_ohlc(turnover=0.001))
        self.assertTrue(r)
        self.assertGreaterEqual(r["benefit_pct"], 0.0)

    def test_flat_prices_degrades_gracefully(self):
        """价格完全走平(hi==lo) → 网格退化，应返回 {} 而非崩溃。"""
        n = _MIN_BARS
        d = [f"2026-01-{i+1:02d}" for i in range(n)]
        o = c = h = l = [10.0] * n
        r = calculate_cyq(d, o, c, h, l, [1.0] * n)
        self.assertEqual(r, {})


class _FakeResp:
    """最小 Response 替身（get_cyq_distribution 只用 .json()）。"""

    def __init__(self, payload):
        self._p = payload

    def json(self):
        return self._p


def _mk_klines(n=_MIN_BARS, base=10.0, turnover=1.0):
    """东财 kline 行：f51~f61 共 11 列，末列 f61=换手率(%)。"""
    out = []
    for i in range(n):
        c = round(base + i * 0.01, 2)
        out.append(
            f"2026-01-01,{round(c - 0.05, 2)},{c},{round(c + 0.08, 2)},"
            f"{round(c - 0.10, 2)},100000,1000000,1.5,0.5,0.05,{turnover}"
        )
    return out


class _TmpCacheDir(unittest.TestCase):
    """把 sc_kline_cache 的目录重定向到临时目录。

    V17.0.15 必需：get_cyq_distribution 现在会写 24h 磁盘缓存到真实
    `cache/kline/`。若不隔离，本文件先跑的测试会留下 `CYQ_600519_240_v2.pkl`，
    后续测试命中缓存 → `_em_fflow_request` 不再被调用 → `m.call_args is None`，
    表现为**测试顺序相关的假失败**（首次跑绿、第二次跑红）。
    """

    def setUp(self):
        import tempfile
        from stock_common import sc_kline_cache as kc

        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp_dir = self._tmp.name
        _p = mock.patch.object(
            kc, "_get_cache_dir", lambda: __import__("pathlib").Path(self.tmp_dir)
        )
        _p.start()
        self.addCleanup(_p.stop)


class TestGetCyqDistribution(_TmpCacheDir):
    """第 2 层：数据入口（东财 kline f61）+ 失败降级。

    每个用例都用**空缓存目录**（见 _TmpCacheDir），确保断言的是网络行为而非命中缓存。
    """

    def _call(self, resp, code="600519"):
        with mock.patch.object(_eastmoney, "_em_fflow_request", return_value=resp) as m:
            r = get_cyq_distribution(code)
        return r, m

    def test_parses_f61_turnover(self):
        r, m = self._call(_FakeResp({"data": {"klines": _mk_klines()}}))
        self.assertTrue(r, "正常响应应返回 CYQ dict")
        self.assertEqual(r.get("source"), "eastmoney_kline_f61")
        self.assertIn("concentration_90", r)
        params = m.call_args[0][1]
        self.assertEqual(params["klt"], "101", "必须取日K")
        self.assertIn("f61", params["fields2"], "fields2 必须含 f61(换手率)")
        self.assertEqual(params["secid"], "1.600519")

    def test_kline_path(self):
        _, m = self._call(_FakeResp({"data": {"klines": _mk_klines()}}))
        self.assertEqual(m.call_args[0][0], "/api/qt/stock/kline/get")
        # prefer_his=True → 历史K线需全窗口(push2delay 会把窗口截成当日)
        self.assertTrue(m.call_args[1].get("prefer_his"))

    def test_secid_prefix_multimarket(self):
        for code, want in (
            ("600519", "1.600519"),  # 沪
            ("000001", "0.000001"),  # 深
            ("300750", "0.300750"),  # 创业板
            ("430047", "0.430047"),
        ):  # 北交所(V17.0 S3)
            _, m = self._call(_FakeResp({"data": {"klines": _mk_klines()}}), code=code)
            self.assertEqual(m.call_args[0][1]["secid"], want, f"{code} 前缀错误")

    def test_returns_empty_on_none_response(self):
        self.assertEqual(self._call(None)[0], {}, "响应为 None 应降级返回 {}")

    def test_returns_empty_on_missing_klines(self):
        for payload in ({}, {"data": None}, {"data": {}}, {"data": {"klines": []}}):
            self.assertEqual(
                self._call(_FakeResp(payload))[0], {}, f"payload={payload!r} 应降级返回 {{}}"
            )

    def test_skips_malformed_rows(self):
        kl = _mk_klines()
        kl.insert(0, "bad,row")  # 列数 < 11 → 应跳过
        kl.append("x,y,z")
        r, _ = self._call(_FakeResp({"data": {"klines": kl}}))
        self.assertTrue(r, "跳过坏行后仍应算出 CYQ")

    def test_returns_empty_when_all_rows_malformed(self):
        r, _ = self._call(_FakeResp({"data": {"klines": ["x,y", "z"]}}))
        self.assertEqual(r, {}, "全部坏行 → 有效收盘 < 2 → {}")

    def test_returns_empty_on_exception(self):
        with mock.patch.object(_eastmoney, "_em_fflow_request", side_effect=RuntimeError("boom")):
            self.assertEqual(
                get_cyq_distribution("600519"),
                {},
                "底层异常应被吞掉并返回 {}（报告不得因 CYQ 中断）",
            )

    def test_returns_empty_on_bad_json(self):
        class _Boom:
            def json(self):
                raise ValueError("not json")

        self.assertEqual(self._call(_Boom())[0], {})


class TestCyqDiskCache(_TmpCacheDir):
    """V17.0.15 缓存层：get_cyq_distribution 必须走 24h 磁盘缓存。

    为什么必须有这一组测试（`em_get` 无数据缓存，只有限流+熔断）：
      全仓扫描时 sht/med/lng 各调一次 → 未加缓存即 **3N 次东财请求**；
      东财 push2 系是**连接级风控**（RemoteDisconnected，字典 §12.3 实测
      恢复 20+ 小时），一旦触发会连带打挂资金流与行情。缓存是唯一解。

    同时钉住两个易错点：
      1. **只缓存非空结果**——把失败/空数据写进缓存 = 把一次瞬时故障固化 24h；
      2. 缓存命中时**不得**发起网络请求（`_em_fflow_request` 调用次数为 0）。
    """

    def _call(self, resp, code="600519"):
        with mock.patch.object(_eastmoney, "_em_fflow_request", return_value=resp) as m:
            r = get_cyq_distribution(code)
        return r, m

    def test_second_call_hits_cache_no_network(self):
        r1, m1 = self._call(_FakeResp({"data": {"klines": _mk_klines()}}))
        self.assertTrue(r1)
        r2, m2 = self._call(_FakeResp({"data": {"klines": _mk_klines()}}))
        self.assertEqual(r1, r2, "第二次应命中磁盘缓存，结果一致")
        self.assertEqual(m1.call_count, 1)
        self.assertEqual(m2.call_count, 0, "缓存命中时不得再发东财请求")

    def test_three_scripts_share_one_request(self):
        """sht/med/lng 串行各调一次 → 实际只应有 1 次东财请求（3N → N）。"""
        counts = []
        for _ in range(3):
            _, m = self._call(_FakeResp({"data": {"klines": _mk_klines()}}))
            counts.append(m.call_count)
        self.assertEqual(sum(counts), 1, f"三次调用应只发一次请求，实际 {counts}")

    def test_empty_result_is_not_cached(self):
        """空/失败结果不写缓存——否则一次瞬时故障被固化 24 小时。"""
        self._call(_FakeResp({"data": {"klines": []}}))
        r, m = self._call(_FakeResp({"data": {"klines": _mk_klines()}}))
        self.assertEqual(m.call_count, 1, "空结果未落盘，第二次必须重新请求")
        self.assertTrue(r, "重取后应得到真实 CYQ")

    def test_exception_result_is_not_cached(self):
        with mock.patch.object(_eastmoney, "_em_fflow_request", side_effect=RuntimeError("boom")):
            self.assertEqual(get_cyq_distribution("600519"), {})
        _, m = self._call(_FakeResp({"data": {"klines": _mk_klines()}}))
        self.assertEqual(m.call_count, 1, "异常结果不得毒化缓存")

    def test_cache_is_per_code(self):
        self._call(_FakeResp({"data": {"klines": _mk_klines(base=10.0)}}), code="600519")
        _, m = self._call(_FakeResp({"data": {"klines": _mk_klines(base=20.0)}}), code="000001")
        self.assertEqual(m.call_count, 1, "不同代码应有独立缓存键")

    def test_cache_is_per_days(self):
        """days 是缓存键的一部分：240 与 120 的窗口不可混用。"""
        with mock.patch.object(
            _eastmoney,
            "_em_fflow_request",
            return_value=_FakeResp({"data": {"klines": _mk_klines()}}),
        ) as m:
            get_cyq_distribution("600519", days=240)
            get_cyq_distribution("600519", days=240)  # 命中缓存
            self.assertEqual(m.call_count, 1)
            get_cyq_distribution("600519", days=120)  # 不同窗口 → 必须重新请求
            self.assertEqual(m.call_count, 2)

    def test_cached_payload_keeps_source_marker(self):
        r1, _ = self._call(_FakeResp({"data": {"klines": _mk_klines()}}))
        r2, _ = self._call(_FakeResp({"data": {"klines": _mk_klines()}}))
        self.assertEqual(r2.get("source"), "eastmoney_kline_f61")
        self.assertEqual(r1.get("source"), r2.get("source"))

    def test_cache_failure_does_not_break_cyq(self):
        """缓存层本身不可用（磁盘满/权限）时，CYQ 必须仍能走网络拿到结果。"""
        with mock.patch.object(
            _eastmoney,
            "_em_fflow_request",
            return_value=_FakeResp({"data": {"klines": _mk_klines()}}),
        ):
            with mock.patch(
                "stock_common.sc_kline_cache.get_cached_blob", side_effect=OSError("disk full")
            ):
                with mock.patch(
                    "stock_common.sc_kline_cache.set_cached_blob", side_effect=OSError("disk full")
                ):
                    r = get_cyq_distribution("600519")
        self.assertTrue(r, "缓存读写异常应被静默吞掉，CYQ 仍返回结果")


def _sd(**kw) -> ScoreData:
    """构造 ScoreData（CYQ 字段缺省 0 = 无数据）。"""
    d = ScoreData(code="600519", name="t", price=10.0)
    for k, v in kw.items():
        setattr(d, k, v)
    return d


class TestCyqScoring(unittest.TestCase):
    """第 3 层：筹码面评分接入（_score_holder）。"""

    def test_scoredata_has_cyq_defaults(self):
        d = _sd()
        for f in (
            "cyq_benefit_pct",
            "cyq_avg_cost",
            "cyq_concentration_90",
            "cyq_concentration_70",
        ):
            self.assertEqual(getattr(d, f), 0.0, f"{f} 缺省应为 0.0")

    def test_no_cyq_data_leaves_score_untouched(self):
        """CYQ 无数据(全 0) → 不加不扣，保持基准 50（不得因缺数据误判）。"""
        score, details = _score_holder(_sd())
        self.assertEqual(score, 50.0)
        self.assertFalse([x for x in details if "筹码" in x and "集中" in x])

    def test_tight_chips_bonus(self):
        score, details = _score_holder(_sd(cyq_concentration_90=0.10))
        self.assertEqual(score, 62.0, "高度集中(<0.12) 应 +12")
        self.assertIn("筹码高度集中", details)

    def test_focus_chips_bonus(self):
        score, details = _score_holder(_sd(cyq_concentration_90=0.15))
        self.assertEqual(score, 57.0, "较集中(<0.2) 应 +7")
        self.assertIn("筹码较集中", details)

    def test_spread_chips_penalty(self):
        score, details = _score_holder(_sd(cyq_concentration_90=0.40))
        self.assertEqual(score, 44.0, "分散(>0.35) 应 -6")
        self.assertIn("筹码分散", details)

    def test_neutral_concentration_no_effect(self):
        score, _ = _score_holder(_sd(cyq_concentration_90=0.25))
        self.assertEqual(score, 50.0, "中性区间(0.2~0.35) 不加不扣")

    def test_high_benefit_bonus(self):
        score, details = _score_holder(_sd(cyq_benefit_pct=0.90))
        self.assertEqual(score, 54.0, "获利盘>0.85 应 +4")
        self.assertIn("获利盘丰厚", details)

    def test_low_benefit_penalty(self):
        score, details = _score_holder(_sd(cyq_benefit_pct=0.10))
        self.assertEqual(score, 46.0, "套牢盘<0.25 应 -4")
        self.assertIn("套牢盘较重", details)

    def test_combined_cyq_effects(self):
        score, details = _score_holder(_sd(cyq_concentration_90=0.10, cyq_benefit_pct=0.90))
        self.assertEqual(score, 66.0, "集中 +12 与获利盘 +4 应叠加")
        self.assertIn("筹码高度集中", details)
        self.assertIn("获利盘丰厚", details)

    def test_cfg_overrides_tolerated(self):
        """传入自定义 cfg 时，缺省键回落内置默认值（不 KeyError）。"""
        score, _ = _score_holder(_sd(cyq_concentration_90=0.10), cfg={"holder_trend": 99})
        self.assertEqual(score, 62.0, "cfg 未提供 cyq_tight → 回落默认 12")


if __name__ == "__main__":
    unittest.main()

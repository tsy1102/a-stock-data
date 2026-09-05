# -*- coding: utf-8 -*-
"""tests/test_sc_technical_risk.py — V16.1 技术/风险引擎测试"""
from __future__ import annotations

import builtins
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_common.sc_technical import (
    calc_macd, calc_rsi, calc_bollinger, calc_kdj,
    calc_volume_analysis, calc_ma, analyze_technical,
    get_kline_patterns,
)
from stock_common.sc_risk import scan_financial_risk, scan_event_risk, combine_risk


def _mk_closes(n=100, base=100.0):
    return [base + i * 0.5 + (i % 7) * 0.3 for i in range(n)]


class TestTechnicalEngine(unittest.TestCase):
    """V16.1: 技术指标引擎（从 ful Layer1 迁移）"""

    def setUp(self):
        self.closes = _mk_closes()
        self.highs = [c + 1 for c in self.closes]
        self.lows = [c - 1 for c in self.closes]
        self.vols = [10000 + i * 10 for i in range(100)]

    def test_macd(self):
        r = calc_macd(self.closes)
        self.assertIn("dif", r)
        self.assertIn("dea", r)
        self.assertIn("macd", r)

    def test_macd_too_short(self):
        self.assertEqual(calc_macd([1, 2, 3]), {})

    def test_rsi(self):
        r = calc_rsi(self.closes)
        self.assertIn("rsi14", r)
        self.assertTrue(0 <= r["rsi14"] <= 100)

    def test_bollinger(self):
        r = calc_bollinger(self.closes)
        self.assertLess(r["lower"], r["mid"])
        self.assertLess(r["mid"], r["upper"])
        self.assertTrue(0 <= r["pos_pct"] <= 100)

    def test_kdj(self):
        r = calc_kdj(self.closes, self.highs, self.lows)
        self.assertIn("k", r)
        self.assertIn("j", r)

    def test_volume(self):
        r = calc_volume_analysis(self.vols)
        self.assertGreater(r["ratio"], 0)

    def test_ma(self):
        r = calc_ma(self.closes)
        self.assertIn("ma5", r)
        self.assertIn("ma60", r)

    def test_analyze_technical(self):
        r = analyze_technical(self.closes, self.highs, self.lows, self.vols)
        self.assertIn("ma", r)
        self.assertIn("macd", r)
        self.assertIn("rsi", r)
        self.assertIn("boll", r)
        self.assertIn("kdj", r)
        self.assertIn("volume", r)
        self.assertIn("ret_20d", r)
        self.assertIn("high_120d", r)


class TestRiskEngine(unittest.TestCase):
    """V16.1: 风险扫描引擎（从 ful layer_risk 迁移）"""

    def test_financial_high_risk(self):
        items = scan_financial_risk({
            "debt_ratio": 80.0, "gw_ratio": 35.0, "ar_ratio": 30.0,
            "inv_ratio": 35.0, "cash_debt_ratio": 0.3, "has_short_loan": True,
            "roe": 2.0, "profit_yoy": -30.0,
        })
        levels = [it["level"] for it in items]
        self.assertIn("高", levels)
        self.assertGreaterEqual(sum(it["score"] for it in items), 50)

    def test_financial_low_risk(self):
        items = scan_financial_risk({
            "debt_ratio": 30.0, "gw_ratio": 5.0, "ar_ratio": 10.0,
            "inv_ratio": 15.0, "cash_debt_ratio": 3.0, "has_short_loan": True,
            "roe": 20.0, "profit_yoy": 25.0,
        })
        self.assertTrue(all(it["level"] == "低" for it in items))

    def test_event_risk_pledge(self):
        items = scan_event_risk(pledge_hits=3)
        pledge = [it for it in items if it["name"] == "股权质押"][0]
        self.assertEqual(pledge["level"], "中")

    def test_event_risk_reduce(self):
        items = scan_event_risk(announcement_titles=["董事减持公告"])
        reduce = [it for it in items if it["name"] == "股东减持"][0]
        self.assertEqual(reduce["level"], "高")

    def test_combine_risk(self):
        fin = scan_financial_risk({
            "debt_ratio": 80.0, "gw_ratio": 5.0, "ar_ratio": 5.0,
            "inv_ratio": 5.0, "cash_debt_ratio": 3.0, "has_short_loan": False,
            "roe": 15.0, "profit_yoy": 10.0,
        })
        ev = scan_event_risk(lockup={"date": "2026-10-01", "ratio": 12.0}, pledge_hits=0)
        r = combine_risk(fin, ev)
        self.assertGreaterEqual(r["risk_score"], 30)
        self.assertTrue(r["signals"])


class TestKlinePattern(unittest.TestCase):
    """V17.0.15: TA-Lib 61 种 K 线形态（get_kline_patterns）。

    背景：该函数自 V17.0.7 实现后**零调用方零单测**；且环境未装 TA-Lib 时它恒返回 {}，
    若直接接入报告会变成"永远空白的假章节"（V17.0 已修过的 M1/M4 假成功类型）。
    本类固化两条契约：无 TA-Lib 静默降级 / 有 TA-Lib 正确出信号。
    """

    def _ohlc(self, n=60):
        o, h, l, c = [], [], [], []
        for i in range(n):
            base = 10.0 + i * 0.05
            o.append(round(base, 2))
            h.append(round(base + 0.30, 2))
            l.append(round(base - 0.30, 2))
            c.append(round(base + 0.02, 2))
        return o, h, l, c

    def test_short_input_returns_empty(self):
        self.assertEqual(get_kline_patterns([1.0], [1.0], [1.0], [1.0]), {})

    def test_missing_talib_degrades_to_empty(self):
        """无 TA-Lib 必须**静默**返回 {}（不抛异常），报告章节据此自动跳过。"""
        real_import = builtins.__import__

        def _blocked(name, *a, **k):
            if name == "talib":
                raise ImportError("No module named 'talib'")
            return real_import(name, *a, **k)

        with mock.patch.object(builtins, "__import__", _blocked):
            self.assertEqual(get_kline_patterns(*self._ohlc()), {})

    def test_with_talib_returns_signals(self):
        """有 TA-Lib 时应返回 61 形态，并能识别构造出的长下影线。"""
        try:
            import talib  # noqa: F401
        except ImportError:
            self.skipTest("TA-Lib 未安装（pip install TA-Lib）")
        o, h, l, c = self._ohlc()
        o[-1], h[-1], l[-1], c[-1] = 10.0, 10.05, 9.20, 9.95  # 长下影
        r = get_kline_patterns(o, h, l, c)
        self.assertEqual(len(r), 61)
        self.assertGreater(r.get("dragonfly_doji", 0), 0, "长下影应识别为蜻蜓十字(看涨)")
        self.assertGreater(r.get("takuri", 0), 0, "长下影应识别为探水竿(看涨)")


class TestAnalyzeTechnicalInputs(unittest.TestCase):
    """V17.0.15 回归保护：med 报告曾用 close 近似 highs/lows、volumes 传空列表。

    两处实质失真（数据源 TDX 日K 本就返回 high/low/volume，见 tdx_get_security_bars 的 keys）：
      ① KDJ 的 RSV=(C−L9)/(H9−L9) 分母退化成「9 日*收盘价*极差」——系统性小于真实振幅
         → RSV 被放大 → 金叉/超买信号过度敏感；
      ② analyze_technical 在 volumes 为空时**根本不产出 volume 键** → 量价分析全程缺失。
    """

    def _mk(self, n=60, amp=0.30):
        c = [round(10.0 + i * 0.05 + (0.1 if i % 3 else -0.1), 2) for i in range(n)]
        return c, [x + amp for x in c], [x - amp for x in c]

    def test_kdj_differs_with_real_high_low(self):
        """真实 high/low 与 close 近似**必须**算出不同 KDJ——若相同说明又退化成近似。"""
        c, h, l = self._mk()
        real = analyze_technical(c, h, l, [])["kdj"]
        approx = analyze_technical(c, c, c, [])["kdj"]
        self.assertNotEqual(real, approx,
                            "真实 high/low 与 close 近似结果相同 → highs/lows 未被真正使用")
        self.assertNotAlmostEqual(real["k"], approx["k"], places=1)

    def test_close_approx_distorts_kdj(self):
        """close 近似会缩小 (H9−L9) 分母 → 放大 RSV → K 值失真（过度极端）。"""
        c, h, l = self._mk()
        self.assertNotAlmostEqual(calc_kdj(c, h, l)["k"], calc_kdj(c, c, c)["k"], places=1)

    def test_kdj_flat_market_pinned_to_neutral(self):
        """H9==L9（一字板/停牌）时 RSV 被钉为 50 —— 已知降级行为，固化防回归。"""
        flat_c = [10.0] * 20
        r = calc_kdj(flat_c, flat_c, flat_c)
        self.assertEqual(r["k"], 50.0)

    def test_volume_key_absent_when_volumes_empty(self):
        """volumes 为空 → 不产出 volume 键（med 曾因此全程缺失量能分析）。"""
        c, h, l = self._mk()
        r = analyze_technical(c, h, l, [])
        self.assertNotIn("volume", r)
        self.assertIn("ma", r)

    def test_volume_key_present_when_volumes_given(self):
        c, h, l = self._mk()
        vols = [10000 + i * 100 for i in range(60)]
        r = analyze_technical(c, h, l, vols)
        self.assertIn("volume", r)
        self.assertGreater(r["volume"]["ratio"], 0)
        self.assertEqual(r["volume"]["today_wan"], round(vols[-1] / 10000, 1))

    def test_short_volumes_tolerated(self):
        """量序列偏短不应崩溃（均量退化为 0、ratio 回退 1.0）。"""
        c, h, l = self._mk()
        r = analyze_technical(c, h, l, [1.0, 2.0])
        self.assertIn("ma", r)


if __name__ == "__main__":
    unittest.main()

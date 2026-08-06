# -*- coding: utf-8 -*-
"""tests/test_sc_technical_risk.py — V16.1 技术/风险引擎测试"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_common.sc_technical import (
    calc_macd, calc_rsi, calc_bollinger, calc_kdj,
    calc_volume_analysis, calc_ma, analyze_technical,
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


if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
"""tests/test_field_routing.py — V12.6 field routing classification tests

Validates the REQUIRES_REALTIME_HTTP and ZHB_SUFFICIENT sets defined in
data_provider.py, plus the helper functions:
  - is_realtime_http_field()
  - is_zhb_sufficient_field()

These tests are pure-python, do not touch network, and do not depend on
ZHB files being installed.
"""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import data_provider as dp


class TestRealtimeHttpField(unittest.TestCase):
    """Fields that MUST use HTTP real-time API."""

    def test_quote_fields_are_realtime(self):
        """Quote-class fields must be in REQUIRES_REALTIME_HTTP."""
        for f in ["price", "change_pct", "amount", "volume",
                  "open", "high", "low", "prev_close"]:
            self.assertTrue(
                dp.is_realtime_http_field(f),
                f"{f} should be realtime HTTP field",
            )

    def test_fund_flow_fields_are_realtime(self):
        """Fund-flow fields must be in REQUIRES_REALTIME_HTTP."""
        for f in ["main_net_buy_hands", "main_net_buy_amount",
                  "main_net_buy_hands_1d", "main_net_buy_amount_1d"]:
            self.assertTrue(
                dp.is_realtime_http_field(f),
                f"{f} should be realtime HTTP field",
            )

    def test_valuation_fields_not_in_realtime(self):
        """Valuation fields must NOT be marked realtime HTTP (use ZHB)."""
        for f in ["pe_ttm", "pb", "dividend_yield"]:
            self.assertFalse(
                dp.is_realtime_http_field(f),
                f"{f} should NOT be realtime (T-1 is OK)",
            )

    def test_unknown_field_defaults_to_false(self):
        """Unknown field name returns False (safe default)."""
        self.assertFalse(dp.is_realtime_http_field("not_a_real_field"))


class TestZhbSufficientField(unittest.TestCase):
    """Fields that ZHB alone is sufficient for (no HTTP needed)."""

    def test_valuation_fields_zhb_sufficient(self):
        for f in ["pe_ttm", "pe_dynamic", "pb", "dividend_yield"]:
            self.assertTrue(
                dp.is_zhb_sufficient_field(f),
                f"{f} should be ZHB sufficient",
            )

    def test_finance_fields_zhb_sufficient(self):
        for f in ["net_profit", "revenue", "roe", "eps"]:
            self.assertTrue(
                dp.is_zhb_sufficient_field(f),
                f"{f} should be ZHB sufficient",
            )

    def test_share_capital_fields_zhb_sufficient(self):
        for f in ["total_shares", "float_shares", "mcap"]:
            self.assertTrue(
                dp.is_zhb_sufficient_field(f),
                f"{f} should be ZHB sufficient",
            )

    def test_sector_fields_zhb_sufficient(self):
        for f in ["industry", "industry_code", "board", "concept"]:
            self.assertTrue(
                dp.is_zhb_sufficient_field(f),
                f"{f} should be ZHB sufficient",
            )

    def test_historical_change_fields_zhb_sufficient(self):
        for f in ["change_5d", "change_10d", "change_20d", "change_ytd"]:
            self.assertTrue(
                dp.is_zhb_sufficient_field(f),
                f"{f} should be ZHB sufficient",
            )

    def test_realtime_fields_NOT_zhb_sufficient(self):
        """Realtime fields should NOT be in ZHB_SUFFICIENT
        (they need HTTP, not ZHB-only)."""
        for f in ["price", "change_pct", "amount"]:
            self.assertFalse(
                dp.is_zhb_sufficient_field(f),
                f"{f} should NOT be ZHB sufficient (needs HTTP)",
            )


class TestSetsDisjoint(unittest.TestCase):
    """REQUIRES_REALTIME_HTTP and ZHB_SUFFICIENT must be disjoint."""

    def test_sets_have_no_overlap(self):
        overlap = dp.REQUIRES_REALTIME_HTTP & dp.ZHB_SUFFICIENT
        self.assertEqual(
            overlap, set(),
            f"REQUIRES_REALTIME_HTTP and ZHB_SUFFICIENT must be disjoint, "
            f"but overlap = {overlap}",
        )


class TestLegacyThreeTierKept(unittest.TestCase):
    """V12.6 keeps legacy _REALTIME_FIELDS / _NEAR_REALTIME_FIELDS / _STATIC_FIELDS
    for backward compatibility with existing callers."""

    def test_legacy_realtime_set_exists(self):
        self.assertTrue(hasattr(dp, "_REALTIME_FIELDS"))
        self.assertIn("price", dp._REALTIME_FIELDS)

    def test_legacy_near_realtime_set_exists(self):
        self.assertTrue(hasattr(dp, "_NEAR_REALTIME_FIELDS"))
        self.assertIn("main_net_buy_amount", dp._NEAR_REALTIME_FIELDS)

    def test_legacy_static_set_exists(self):
        self.assertTrue(hasattr(dp, "_STATIC_FIELDS"))
        self.assertIn("pe_ttm", dp._STATIC_FIELDS)

    def test_legacy_helper_functions_still_work(self):
        self.assertTrue(dp._is_realtime("price"))
        self.assertTrue(dp._is_near_realtime("main_net_buy_amount"))
        self.assertTrue(dp._is_static("pe_ttm"))


class TestCanonicalDataAPI(unittest.TestCase):
    """V15 Unified Canonical Data API Tests."""

    def test_get_canonical_stock_data_returns_dataclass(self):
        cdata = dp.get_canonical_stock_data("600519")
        self.assertEqual(cdata.code, "600519")
        self.assertTrue(hasattr(cdata, "price"))
        self.assertTrue(hasattr(cdata, "pe_ttm"))
        self.assertTrue(hasattr(cdata, "data_source"))
        self.assertTrue(hasattr(cdata, "time_anchor"))

    def test_canonical_stock_data_to_dict(self):
        cdata = dp.get_canonical_stock_data("600519")
        d = cdata.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["code"], "600519")
        self.assertIn("price", d)

    def test_graceful_circuit_breaker_fallback(self):
        """当 TDX/腾讯/东财全部抛异常时，get_canonical_stock_data 不抛异常并降级为 ZHB。"""
        from unittest.mock import patch
        # data_provider 函数内 `from stock_common import get_tencent_quote`，patch 包属性
        with patch("tdx_client.tdx_get_quote_full", side_effect=RuntimeError("Circuit Breaker Open")):
            with patch("stock_common.get_tencent_quote", return_value={}):
                with patch("stock_common.sc_datasource.get_em_quote_full", return_value={}):
                    cdata = dp.get_canonical_stock_data("600519", force_realtime=True)
                    self.assertIsNotNone(cdata)
                    self.assertEqual(cdata.code, "600519")
                    self.assertEqual(cdata.data_source, "zhb")


if __name__ == "__main__":
    unittest.main()
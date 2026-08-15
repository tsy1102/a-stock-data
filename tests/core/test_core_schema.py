# -*- coding: utf-8 -*-
"""tests/test_sc_schema.py — V13.0/V13.1 dataclass schema tests

Validates:
  - stock_common.sc_schema imports successfully
  - All 34 FieldSpec entries are well-formed
  - field name uniqueness
  - REQUIRES_REALTIME_HTTP / ZHB_SUFFICIENT set compatibility with V12.6
  - stock_cache._serialize_for_cache handles dataclass / dict / list
  - stock_cache._deserialize_from_cache is callable
"""
from __future__ import annotations

import os
import sys
import unittest
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import stock_common.sc_schema as schema
import core.stock_cache as sc


# ═══════════════════════════════════════════════════
# V13.0: Schema 元数据测试
# ═══════════════════════════════════════════════════

class TestSchemaImport(unittest.TestCase):

    def test_module_imports(self):
        self.assertTrue(hasattr(schema, "TimeAnchor"))
        self.assertTrue(hasattr(schema, "DataSource"))
        self.assertTrue(hasattr(schema, "Unit"))
        self.assertTrue(hasattr(schema, "FieldSpec"))
        self.assertTrue(hasattr(schema, "FIELD_SPECS"))
        self.assertTrue(hasattr(schema, "NormalizedQuote"))

    def test_enum_values(self):
        self.assertEqual(schema.TimeAnchor.T_DAY.value, "t_day")
        self.assertEqual(schema.TimeAnchor.T_MINUS_1.value, "t-1")
        self.assertEqual(schema.DataSource.ZHB.value, "zhb")
        self.assertEqual(schema.DataSource.TDX.value, "tdx")


class TestFieldSpecTable(unittest.TestCase):

    def test_field_specs_not_empty(self):
        self.assertGreater(len(schema.FIELD_SPECS), 20)

    def test_field_names_unique(self):
        names = [s.name for s in schema.FIELD_SPECS]
        self.assertEqual(len(names), len(set(names)), "field names must be unique")

    def test_get_field_spec_returns_correct_spec(self):
        spec = schema.get_field_spec("price")
        self.assertEqual(spec.name, "price")
        self.assertEqual(spec.unit, schema.Unit.YUAN)
        self.assertTrue(spec.is_real_time)

    def test_get_field_spec_unknown_raises(self):
        with self.assertRaises(KeyError):
            schema.get_field_spec("nonexistent_field_xyz")

    def test_has_field_spec(self):
        self.assertTrue(schema.has_field_spec("pe_ttm"))
        self.assertFalse(schema.has_field_spec("nonexistent_field_xyz"))

    def test_list_field_names_complete(self):
        names = schema.list_field_names()
        self.assertIn("price", names)
        self.assertIn("pe_ttm", names)
        self.assertIn("pb", names)
        self.assertIn("main_net_buy_amount", names)

    def test_realtime_http_fields_include_quotes(self):
        rt = set(schema.list_realtime_http_fields())
        for f in ["price", "change_pct", "amount", "main_net_buy_hands"]:
            self.assertIn(f, rt, f"{f} should be realtime")

    def test_zhb_sufficient_fields_include_valuation(self):
        zhb = set(schema.list_zhb_sufficient_fields())
        for f in ["pe_ttm", "pb", "dividend_yield", "industry"]:
            self.assertIn(f, zhb, f"{f} should be ZHB sufficient")


# ═══════════════════════════════════════════════════
# V13.0: NormalizedQuote 骨架测试
# ═══════════════════════════════════════════════════

class TestNormalizedQuote(unittest.TestCase):

    def test_dataclass_instantiation(self):
        q = schema.NormalizedQuote(
            code="600519",
            data_date="20260722",
            price=1680.0,
            change_pct=2.5,
            source=schema.DataSource.ZHB,
            time_anchor=schema.TimeAnchor.T_MINUS_1,
        )
        self.assertEqual(q.code, "600519")
        self.assertEqual(q.price, 1680.0)
        self.assertEqual(q.change_pct, 2.5)

    def test_dataclass_is_immutable(self):
        q = schema.NormalizedQuote(
            code="000001",
            data_date="20260722",
            price=10.0,
            change_pct=1.0,
            source=schema.DataSource.ZHB,
            time_anchor=schema.TimeAnchor.T_MINUS_1,
        )
        with self.assertRaises(Exception):
            q.price = 20.0  # frozen=True

    def test_normalize_at_boundary_raises_not_implemented(self):
        # V16.0: normalize_at_boundary 已实现（非骨架），空 dict 抛 ValueError
        with self.assertRaises(ValueError):
            schema.normalize_at_boundary({}, schema.DataSource.ZHB)

    def test_normalize_at_boundary_zhb(self):
        """V16.0: ZHB 源归一化 — amount 已是万元直传，保留规范字段。"""
        raw = {
            "code": "600519", "name": "贵州茅台",
            "price": 1500.0, "change_pct": 1.2,
            "amount": 412922.85, "pe_ttm": 19.58,
        }
        out = schema.normalize_at_boundary(raw, schema.DataSource.ZHB)
        self.assertEqual(out["code"], "600519")
        self.assertEqual(out["name"], "贵州茅台")
        self.assertEqual(out["price"], 1500.0)
        self.assertEqual(out["change_pct"], 1.2)
        self.assertEqual(out["amount_wan"], 412922.85)  # ZHB 万元直传
        self.assertEqual(out["pe_ttm"], 19.58)

    def test_normalize_at_boundary_em_amount_unit(self):
        """V16.0: EM push2 源归一化 — f48 元 → 万元。"""
        raw = {"code": "600519", "price": 1500.0, "f48": 4129228500.0, "f116": 1900000000000.0}
        out = schema.normalize_at_boundary(raw, schema.DataSource.EASTMONEY)
        self.assertEqual(out["amount_wan"], 412922.85)  # 元→万元
        self.assertEqual(out["mcap_yi"], 19000.0)  # 元→亿元


# ═══════════════════════════════════════════════════
# V13.1: stock_cache 透明序列化测试
# ═══════════════════════════════════════════════════

@dataclass(slots=True, frozen=True)
class _SampleQuote:
    code: str
    price: float
    change_pct: float


@dataclass(slots=True, frozen=True)
class _SampleNested:
    code: str
    quote: _SampleQuote
    tags: tuple


class TestSerializeForCache(unittest.TestCase):

    def test_plain_dict_unchanged(self):
        d = {"a": 1, "b": "hello"}
        self.assertEqual(sc._serialize_for_cache(d), d)

    def test_dataclass_converted_to_dict(self):
        q = _SampleQuote(code="600519", price=1680.0, change_pct=2.5)
        result = sc._serialize_for_cache(q)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["code"], "600519")
        self.assertEqual(result["price"], 1680.0)

    def test_nested_dict_with_dataclass(self):
        q = _SampleQuote(code="000001", price=10.0, change_pct=1.0)
        d = {"quote": q, "source": "zhb"}
        result = sc._serialize_for_cache(d)
        self.assertEqual(result["quote"]["code"], "000001")
        self.assertEqual(result["source"], "zhb")

    def test_list_with_dataclass(self):
        quotes = [
            _SampleQuote(code="600519", price=1680.0, change_pct=2.5),
            _SampleQuote(code="000001", price=10.0, change_pct=1.0),
        ]
        result = sc._serialize_for_cache(quotes)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["code"], "600519")

    def test_primitives_unchanged(self):
        self.assertEqual(sc._serialize_for_cache(42), 42)
        self.assertEqual(sc._serialize_for_cache("hello"), "hello")
        self.assertEqual(sc._serialize_for_cache(None), None)
        self.assertEqual(sc._serialize_for_cache(3.14), 3.14)

    def test_dataclass_class_not_converted(self):
        # The class object itself is not a dataclass instance
        self.assertEqual(sc._serialize_for_cache(_SampleQuote), _SampleQuote)


class TestDeserializeFromCache(unittest.TestCase):

    def test_returns_input_when_no_target_cls(self):
        d = {"a": 1, "b": 2}
        self.assertEqual(sc._deserialize_from_cache(d), d)

    def test_dict_to_dataclass_when_target_cls_provided(self):
        d = {"code": "600519", "price": 1680.0, "change_pct": 2.5}
        result = sc._deserialize_from_cache(d, target_cls=_SampleQuote)
        self.assertIsInstance(result, _SampleQuote)
        self.assertEqual(result.code, "600519")
        self.assertEqual(result.price, 1680.0)

    def test_invalid_dict_returns_input_unchanged(self):
        # Missing required field should return original dict
        d = {"code": "600519"}  # missing price, change_pct
        result = sc._deserialize_from_cache(d, target_cls=_SampleQuote)
        self.assertIsInstance(result, dict)
        self.assertEqual(result, d)


class TestCacheRoundTrip(unittest.TestCase):
    """V13.1 集成测试：dataclass 写入 + 读出 dict。"""

    def setUp(self):
        # 隔离测试：使用临时数据库
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self._orig_db = sc._CACHE_DB
        self._orig_conn = sc._db
        sc._CACHE_DB = os.path.join(self._tmp.name, "test_cache.db")
        sc._db = None
        sc._DISABLE_CACHE = False

    def tearDown(self):
        # 关闭临时数据库连接，释放文件锁
        if sc._db is not None:
            try:
                sc._db.close()
            except Exception:
                pass
        sc._CACHE_DB = self._orig_db
        sc._db = None
        if self._orig_conn:
            sc._db = self._orig_conn
        self._tmp.cleanup()

    def test_dataclass_cache_round_trip(self):
        q = _SampleQuote(code="600519", price=1680.0, change_pct=2.5)
        sc.set_cache("test_cat", "test_func", q, ttl=3600)
        cached = sc.get_cache("test_cat", "test_func")
        # V13.1 阶段：反序列化返回 dict
        self.assertIsInstance(cached, dict)
        self.assertEqual(cached["code"], "600519")
        self.assertEqual(cached["price"], 1680.0)


# ═══════════════════════════════════════════════════
# V16.1: CanonicalStockData 扩展字段测试
# ═══════════════════════════════════════════════════

class TestCanonicalV161ExtendedFields(unittest.TestCase):
    """V16.1: push2 扩展字段（官方 TdxQuant 交叉验证）可实例化 + 默认值。"""

    def test_extended_fields_defaults(self):
        d = schema.CanonicalStockData(code="600519")
        self.assertEqual(d.limit_up, 0.0)
        self.assertEqual(d.limit_down, 0.0)
        self.assertEqual(d.bps, 0.0)
        self.assertEqual(d.pe_more, 0.0)
        self.assertEqual(d.industry_code_push2, "")
        self.assertEqual(d.report_period, "")
        self.assertEqual(d.quote_date, "")
        self.assertEqual(d.fund_main_today, 0.0)
        self.assertEqual(d.fund_main_5d, 0.0)
        self.assertEqual(d.fund_super_today, 0.0)
        self.assertEqual(d.fund_large_today, 0.0)
        self.assertEqual(d.fund_mid_today, 0.0)
        self.assertEqual(d.fund_small_today, 0.0)
        self.assertEqual(d.fund_5d_array, ())

    def test_extended_fields_set(self):
        d = schema.CanonicalStockData(
            code="600519",
            limit_up=1494.88,
            limit_down=1223.08,
            bps=216.32,
            pe_more=20.64,
            high_52w=1539.98,
            low_52w=1151.01,
            report_period="20260331",
            fund_main_today=-454739712.0,
            fund_5d_array=[{"date": "2026-08-03", "mainNetAmt": -22180448.0}],
        )
        self.assertEqual(d.limit_up, 1494.88)
        self.assertEqual(d.bps, 216.32)
        self.assertEqual(d.high_52w, 1539.98)
        self.assertEqual(d.report_period, "20260331")
        self.assertEqual(d.fund_main_today, -454739712.0)
        self.assertEqual(len(d.fund_5d_array), 1)

    def test_to_dict_includes_extended_fields(self):
        d = schema.CanonicalStockData(code="600519", limit_up=1494.88)
        dd = d.to_dict()
        self.assertEqual(dd["limit_up"], 1494.88)
        self.assertIn("fund_main_today", dd)
        self.assertIn("report_period", dd)


# ═══════════════════════════════════════════════════
# V16.1: 研报估值提取函数测试
# ═══════════════════════════════════════════════════

class TestExtractReportValuation(unittest.TestCase):
    """V16.1: extract_report_valuation 规范化研报估值/评级字段。"""

    def setUp(self):
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from stock_common.sc_datasource import extract_report_valuation
        self._fn = extract_report_valuation

    def test_empty_returns_defaults(self):
        out = self._fn([])
        self.assertEqual(out["eps_this"], 0.0)
        self.assertEqual(out["rating"], "")
        self.assertEqual(out["rating_change"], 0)

    def test_extracts_fields(self):
        reports = [
            {
                "publishDate": "2026-07-23 00:00:00",
                "predictThisYearEps": 67.19,
                "predictNextYearEps": 69.76,
                "predictNextTwoYearEps": 73.96,
                "predictThisYearPe": 19.42,
                "predictNextYearPe": 18.71,
                "predictNextTwoYearPe": 17.65,
                "emRatingName": "买入",
                "lastEmRatingName": "增持",
                "ratingChange": 3,
                "orgSName": "中邮证券",
                "attachPages": 5,
                "attachSize": 403,
            }
        ]
        out = self._fn(reports)
        self.assertEqual(out["eps_this"], 67.19)
        self.assertEqual(out["eps_next"], 69.76)
        self.assertEqual(out["eps_next2"], 73.96)
        self.assertEqual(out["pe_this"], 19.42)
        self.assertEqual(out["rating"], "买入")
        self.assertEqual(out["rating_last"], "增持")
        self.assertEqual(out["rating_change"], 3)
        self.assertEqual(out["org_name"], "中邮证券")
        self.assertEqual(out["attach_pages"], 5)
        self.assertEqual(out["publish_date"], "2026-07-23")

    def test_latest_report_priority(self):
        reports = [
            {"publishDate": "2026-06-01", "predictThisYearEps": 60.0, "emRatingName": "增持"},
            {"publishDate": "2026-07-01", "predictThisYearEps": 70.0, "emRatingName": "买入"},
        ]
        out = self._fn(reports)
        self.assertEqual(out["eps_this"], 70.0)
        self.assertEqual(out["rating"], "买入")


if __name__ == "__main__":
    unittest.main()
# -*- coding: utf-8 -*-
"""tests/data/test_data_em_fund_flow_tiers.py — 东财资金流四档层级回归（V17.0.16）。

**为什么需要这一组测试（真实 bug 回填）**

旧版把 push2 `stock/get` 的 f135–f146 当成**并列四档**（特大/大单/中单/小单），
并据此计算「主力净额 = f137 + f140」。**两层错误**：

1. **层级错位**：f137 不是"特大单净"，它是**合计档**。
2. **重复计数**：f137 已经含了 f140，再 + f140 → 主力净额虚高约 **40%**。

**三条独立铁证（2026-08-31，12 个采集日原始数据）**

① 结构自洽 + 全组合盲搜（169 样本，相对差 **0.00**，100% 命中）：
     f135 = f138 + f141      f136 = f139 + f142      f137 = f140 + f143
   → 旧命名下应推出 f137 = f138 − f139 = f140，但实测 **0/169 相等**（96.4% 显著分离）。

② ulist239 同名号段（236 样本）：**f62 == f66 + f72 命中 236/236 = 100%**
   → 东财标准：f62=主力净、f66=超大单净、f72=大单净、f78=中单净、f84=小单净。

③ 跨接口对撞（234 样本，2% 容差）：
     f62==f137 96.6%   f66==f140 98.3%   f72==f143 96.2%
     f78==f146 95.7%   f84==f149 96.2%   （f84==f146 仅 0.9%，排除）

**正确层级**

    f138/139/140 = 超大单 买/卖/净
    f141/142/143 = 大单   买/卖/净
    f135/136/137 = **主力** 买/卖/净   （= 超大单 + 大单）
    f144/145/146 = 中单   买/卖/净
    f149         = 小单净  （f135–f146 段内**没有**小单买/卖）

**数值取自 2026-08-12 茅台真值**（满足全部自洽关系，可直接肉眼验算）：
    f135=2,707,959,200 = f138(1,309,865,344) + f141(1,398,093,856)
    f137=   46,577,744 = f140(  31,916,032)  + f143(  14,661,712)
"""
from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stock_common import sc_datasource  # noqa: E402
from stock_common.sc_datasource import _em_quote_full_impl  # noqa: E402


class _FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _payload(**over):
    """2026-08-12 贵州茅台 600519 真实量级（元）。"""
    base = {
        "f57": "600519",
        "f58": "贵州茅台",
        # 主力（合计档 = 超大单 + 大单）
        "f135": 2707959200.0,   # 主力买入
        "f136": 2661381456.0,   # 主力卖出
        "f137": 46577744.0,     # 主力净  = f140 + f143  ← 旧版误标为"特大单净"
        # 超大单
        "f138": 1309865344.0,   # 超大单买入
        "f139": 1277949312.0,   # 超大单卖出
        "f140": 31916032.0,     # 超大单净 ← 旧版误标为"大单净"
        # 大单
        "f141": 1398093856.0,   # 大单买入 ← 旧版误标为"中单买入"
        "f142": 1383432144.0,   # 大单卖出 ← 旧版误标为"中单卖出"
        "f143": 14661712.0,     # 大单净   ← 旧版误标为"中单净"
        # 中单
        "f144": 1881712464.0,   # 中单买入 ← 旧版误标为"小单买入"
        "f145": 1928061792.0,   # 中单卖出 ← 旧版误标为"小单卖出"
        "f146": -46349328.0,    # 中单净   ← 旧版误标为"小单净"
        # 小单（f135-f146 段内只有净额，无买卖明细）
        "f149": -228434.0,      # 小单净 —— V17.0.16 新增
    }
    base.update(over)
    return {"data": base}


def _call(**over):
    with mock.patch.object(sc_datasource, "em_get", return_value=_FakeResp(_payload(**over))) as m:
        r = _em_quote_full_impl("600519")
    return r, m


class TestFundFlowTierMapping(unittest.TestCase):
    """核心：四档净额必须各自落在正确的 key 上。"""

    def test_main_net_is_f137_directly(self):
        """回归核心：fund_main_today 必须 == f137(46,577,744)，
        绝不能是 f137+f140(78,549,776)——旧 bug 会在此转红。"""
        r, _ = _call()
        self.assertAlmostEqual(r["fund_main_today"], 46577744.0, places=2,
                               msg="fund_main_today 必须直接取 f137；若为 f137+f140 说明重复计数回归")

    def test_main_net_is_not_double_counted(self):
        """反向钉死：绝不等于 f137 + f140。"""
        r, _ = _call()
        self.assertNotAlmostEqual(r["fund_main_today"], 46577744.0 + 31916032.0, places=2,
                                  msg="fund_main_today == f137+f140 → 超大单净被重复计入")

    def test_super_net_is_f140(self):
        r, _ = _call()
        self.assertAlmostEqual(r["fund_super_today"], 31916032.0, places=2,
                               msg="fund_super_today 必须取 f140=超大单净（旧版错取 f137）")

    def test_large_net_is_f143(self):
        r, _ = _call()
        self.assertAlmostEqual(r["fund_large_today"], 14661712.0, places=2,
                               msg="fund_large_today 必须取 f143=大单净（旧版错取 f140）")

    def test_mid_net_is_f146(self):
        r, _ = _call()
        self.assertAlmostEqual(r["fund_mid_today"], -46349328.0, places=2,
                               msg="fund_mid_today 必须取 f146=中单净（旧版错取 f143）")

    def test_small_net_is_f149(self):
        """f149 是 V17.0.16 新增的小单净——旧版把 f146 当小单，实为中单。"""
        r, _ = _call()
        self.assertAlmostEqual(r["fund_small_today"], -228434.0, places=2,
                               msg="fund_small_today 必须取 f149=小单净（旧版错取 f146=中单净）")

    def test_main_net_equals_super_plus_large(self):
        """结构不变量：主力净 == 超大单净 + 大单净（实测 169/169，相对差 0.00）。"""
        r, _ = _call()
        self.assertAlmostEqual(r["fund_main_today"],
                               r["fund_super_today"] + r["fund_large_today"], places=2,
                               msg="主力净必须等于 超大单净 + 大单净；不等说明档位映射错位")

    def test_super_and_large_are_distinct(self):
        """守卫：超大单净与大单净若相同，说明二者又指向同一字段。"""
        r, _ = _call()
        self.assertNotAlmostEqual(r["fund_super_today"], r["fund_large_today"], places=2,
                                  msg="超大单净 == 大单净 → 两档映射被混淆")

    def test_all_four_tiers_are_distinct(self):
        r, _ = _call()
        vals = [r["fund_super_today"], r["fund_large_today"],
                r["fund_mid_today"], r["fund_small_today"]]
        for i in range(len(vals)):
            for j in range(i + 1, len(vals)):
                self.assertNotAlmostEqual(vals[i], vals[j], places=2,
                                          msg=f"第 {i} 档与第 {j} 档净额相同 → 映射错位")


class TestFundFlowBuySellMapping(unittest.TestCase):
    """买/卖金额同样整体错位了一档，一并钉死。"""

    def test_main_buy_sell(self):
        r, _ = _call()
        self.assertAlmostEqual(r["fund_main_buy"], 2707959200.0, places=2)
        self.assertAlmostEqual(r["fund_main_sell"], 2661381456.0, places=2)

    def test_super_buy_sell(self):
        r, _ = _call()
        self.assertAlmostEqual(r["fund_super_buy"], 1309865344.0, places=2)
        self.assertAlmostEqual(r["fund_super_sell"], 1277949312.0, places=2)

    def test_large_buy_sell(self):
        """旧版这两键名叫 fund_mid_buy/mid_sell，实为大单。"""
        r, _ = _call()
        self.assertAlmostEqual(r["fund_large_buy"], 1398093856.0, places=2)
        self.assertAlmostEqual(r["fund_large_sell"], 1383432144.0, places=2)

    def test_mid_buy_sell(self):
        """旧版这两键名叫 fund_small_buy/small_sell，实为中单。"""
        r, _ = _call()
        self.assertAlmostEqual(r["fund_mid_buy"], 1881712464.0, places=2)
        self.assertAlmostEqual(r["fund_mid_sell"], 1928061792.0, places=2)

    def test_main_buy_equals_super_plus_large(self):
        r, _ = _call()
        self.assertAlmostEqual(r["fund_main_buy"],
                               r["fund_super_buy"] + r["fund_large_buy"], places=2)
        self.assertAlmostEqual(r["fund_main_sell"],
                               r["fund_super_sell"] + r["fund_large_sell"], places=2)


class TestFundFlowRequestFields(unittest.TestCase):
    """请求串必须覆盖全部用到的字段——缺 f149 会让小单净恒为 0。"""

    def test_request_includes_f149(self):
        _, m = _call()
        fields = m.call_args.kwargs.get("params", {}).get("fields", "")
        self.assertIn("f149", fields, "请求字段缺 f149 → 小单净恒为 0")

    def test_request_covers_all_consumed_fields(self):
        _, m = _call()
        fields = m.call_args.kwargs.get("params", {}).get("fields", "")
        for k in ("f135", "f136", "f137", "f138", "f139", "f140",
                  "f141", "f142", "f143", "f144", "f145", "f146", "f149"):
            self.assertIn(k, fields, f"请求字段缺 {k}")


class TestFundFlowRobustness(unittest.TestCase):
    """字段缺失/异常时不得抛错，且不得凭空造值。"""

    def test_missing_optional_fields_yields_no_key(self):
        """缺 f149 时不应产生 fund_small_today 键（保持 None/缺席，勿填 0）。"""
        p = _payload()
        del p["data"]["f149"]
        with mock.patch.object(sc_datasource, "em_get", return_value=_FakeResp(p)):
            r = _em_quote_full_impl("600519")
        self.assertIsNone(r.get("fund_small_today"),
                          "缺失字段应缺席而非填 0——填 0 会让下游误判为'小单净为 0'")

    def test_dash_value_skipped(self):
        r, _ = _call(f149="-")
        self.assertIsNone(r.get("fund_small_today"))

    def test_network_failure_returns_empty(self):
        with mock.patch.object(sc_datasource, "em_get", return_value=None):
            r = _em_quote_full_impl("600519")
        self.assertIsInstance(r, dict)

    def test_exception_swallowed(self):
        with mock.patch.object(sc_datasource, "em_get", side_effect=RuntimeError("boom")):
            r = _em_quote_full_impl("600519")
        self.assertIsInstance(r, dict)


if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
"""tests/data/test_data_em_board_members.py — 东财 clist 板块成分股字段映射回归。

**为什么需要这一组测试（V17.0.15 真实 bug 回填）**

`get_em_board_members` 长期把 **f23 当 PE(动)** 用，而 f23 实为**市净率 PB**。
该错误是静默的：不抛异常、不产生 NaN，只是让 `pe` 的数值小了一个量级。

后果链：
  `get_em_board_members` 的 `"pe"`（实为 PB）
    → `get_industry_peers` 的 `peers[]["pe"]`
    → `get_med_report.py` 的 `score_data.industry_pe`（行业平均 PE 变成行业平均 PB）
    → `sc_scoring.py:237` `if data.pe_ttm < data.industry_pe:` 判据
       —— 拿 PE(≈20) 去比 PB(≈2)，**几乎恒为 False**
       → 「PE低于行业均值」+15 分**永不触发**，属静默失效。

**铁证（2026-08-31 跨接口对撞，12 个采集日，2% 容差 100% 命中）**

  ulist f9   == push2 f162 = 市盈率(动态)   150/150
  ulist f114 == push2 f163 = 市盈率(静态)   190/190
  ulist f115 == push2 f164 = 市盈率(TTM)    166/166
  ulist f23  == push2 f167 = **市净率 PB**  238/238

  量级佐证：f9 中位 20.84 vs f23 中位 2.22（相差 9.4×），分属 PE 族与 PB 族。
  茅台 2026-08-28：price 1297.4，BPS ≈ 200.99 → PB = 6.456 ≈ f23 = 6.46 ✓

本文件钉死正确映射，任何人把 `"pe"` 改回 f23 都会被这里的断言拦住。
"""
from __future__ import annotations

import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from stock_common import sc_datasource  # noqa: E402
from stock_common.sc_datasource import get_em_board_members, _industry  # noqa: E402
# V17.2.18 重构后片段为独立模块: get_em_board_members 定义在 _industry, em_get 由其自身
# 命名空间解析; 故补丁须打在 _industry.em_get (而非包级 re-export 副本) 才能穿透。

from core.stock_cache import invalidate_category  # noqa: E402

# V17.0.26 DEBT-012: 本函数已加 @cached。测试共用一个 board_code("BK0447")，
# 若无隔离则「取到非空结果」的用例会把值写进 L2 SQLite，污染后续断言（例如
# test_missing_fields_default_zero 期望 pe=0，却会命中上一个用例缓存的 pe=18.22）。
_CACHE_ENABLED = os.environ.get("STOCK_NOCACHE", "") != "1"


def setUpModule():
    invalidate_category("board_members")


class _FakeResp:
    """最小响应桩：只需支持 .json()。"""

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _item(**over):
    """构造一只成分股。数值取自 2026-08-28 茅台真值量级：
    price 1297.4 / 动态PE(f9) 18.22 / PB(f23) 6.46 / 总市值 16218 亿。"""
    base = {
        "f12": "600519",
        "f14": "贵州茅台",
        "f2": 1297.4,
        "f3": 0.39,
        "f9": 18.22,          # 市盈率(动态)
        "f20": 1621855869137,  # 总市值(元)
        "f21": 1621855869137,  # 流通市值(元)
        "f23": 6.46,          # 市净率 PB —— 曾长期被误当 PE
        "f62": 12345678.0,    # 主力净流入额
        "f184": 0.28,         # 换手率
    }
    base.update(over)
    return base


def _call(payload, board_code="BK0447"):
    with mock.patch.object(_industry, "em_get", return_value=_FakeResp(payload)) as m:
        r = get_em_board_members(board_code)
    return r, m


class TestEmBoardMembersFieldMapping(unittest.TestCase):
    """核心：pe 必须来自 f9，pb 必须来自 f23。"""

    def setUp(self):
        # 缓存隔离：每个用例前清空 board_members 分类（L1 + L2）
        invalidate_category("board_members")

    def test_pe_comes_from_f9_not_f23(self):
        """回归核心：pe == f9(18.22)，绝不能是 f23(6.46)。"""
        r, _ = _call({"data": {"diff": [_item()]}})
        self.assertEqual(len(r), 1)
        self.assertAlmostEqual(r[0]["pe"], 18.22, places=4,
                               msg="pe 必须取 f9=市盈率(动态)，取到 f23 说明回归了旧 bug")

    def test_pb_comes_from_f23(self):
        r, _ = _call({"data": {"diff": [_item()]}})
        self.assertAlmostEqual(r[0]["pb"], 6.46, places=4,
                               msg="pb 必须取 f23=市净率")

    def test_pe_and_pb_are_distinct_values(self):
        """量级守卫：PE 与 PB 必须不同。若两者再次混淆（都取同一字段）则此处转红。"""
        r, _ = _call({"data": {"diff": [_item()]}})
        self.assertNotAlmostEqual(r[0]["pe"], r[0]["pb"], places=2,
                                  msg="pe 与 pb 数值相同 → 字段映射又被混用了")

    def test_request_fields_include_f9_and_f23(self):
        """请求串必须同时含 f9(PE) 与 f23(PB)——缺任一项都会让其中一个字段恒为 0。"""
        _, m = _call({"data": {"diff": [_item()]}})
        fields = m.call_args.kwargs.get("params", {}).get("fields", "")
        self.assertIn("f9", fields, "请求字段缺 f9 → pe 恒为 0")
        self.assertIn("f23", fields, "请求字段缺 f23 → pb 恒为 0")

    def test_mcap_yi_converted_from_yuan(self):
        """f20 单位是元 → 转亿元。"""
        r, _ = _call({"data": {"diff": [_item()]}})
        self.assertAlmostEqual(r[0]["mcap_yi"], 16218.55869137, places=2)

    def test_other_fields_mapping(self):
        r, _ = _call({"data": {"diff": [_item()]}})
        self.assertEqual(r[0]["code"], "600519")
        self.assertEqual(r[0]["name"], "贵州茅台")
        self.assertAlmostEqual(r[0]["price"], 1297.4, places=2)
        self.assertAlmostEqual(r[0]["change_pct"], 0.39, places=2)
        self.assertAlmostEqual(r[0]["turnover"], 0.28, places=2)
        self.assertAlmostEqual(r[0]["main_net_amount"], 12345678.0, places=2)


class TestEmBoardMembersRobustness(unittest.TestCase):
    """异常与边界：不得抛异常，一律降级为空列表。"""

    def setUp(self):
        invalidate_category("board_members")

    def test_empty_diff(self):
        r, _ = _call({"data": {"diff": []}})
        self.assertEqual(r, [])

    def test_missing_data(self):
        r, _ = _call({})
        self.assertEqual(r, [])

    def test_diff_as_dict(self):
        """东财有时把 diff 返回为 dict（按序索引），需能兼容。"""
        r, _ = _call({"data": {"diff": {"0": _item()}}})
        self.assertEqual(len(r), 1)
        self.assertAlmostEqual(r[0]["pe"], 18.22, places=4)

    def test_network_none_returns_empty(self):
        with mock.patch.object(_industry, "em_get", return_value=None):
            self.assertEqual(get_em_board_members("BK0447"), [])

    def test_exception_returns_empty(self):
        with mock.patch.object(_industry, "em_get", side_effect=RuntimeError("boom")):
            self.assertEqual(get_em_board_members("BK0447"), [])

    def test_missing_fields_default_zero(self):
        """只回 code/name 时，数值字段应回落 0 而非抛异常。"""
        r, _ = _call({"data": {"diff": [{"f12": "600519", "f14": "贵州茅台"}]}})
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["pe"], 0)
        self.assertEqual(r[0]["pb"], 0)


@unittest.skipIf(
    not _CACHE_ENABLED,
    "STOCK_NOCACHE=1 时 @cached 为纯透传（stock_cache.py L1087），缓存语义不适用",
)
class TestEmBoardMembersCache(unittest.TestCase):
    """DEBT-012 偿还验证：push2 主域接口必须自带缓存，且空结果不得入缓存。

    为什么单独钉死这两条：
      - 「有缓存」是 A4 公理的硬要求（push2 主域 45000/h 封禁 20h，全仓风控最严）；
      - 「空结果不缓存」是 DEBT-006 同一论证：一次网络抖动返回 []，若被缓存 15 分钟，
        会让 5 个消费方在整段窗口内静默拿到空成分股，且不报错。
    """

    def setUp(self):
        invalidate_category("board_members")

    def test_second_call_served_from_cache(self):
        """同一板块 15min 内二次调用不得再打 push2 主域。"""
        with mock.patch.object(
            _industry, "em_get", return_value=_FakeResp({"data": {"diff": [_item()]}})
        ) as m:
            r1 = get_em_board_members("BK0447")
            r2 = get_em_board_members("BK0447")
        self.assertEqual(m.call_count, 1, f"第二次调用应命中缓存，实际请求 {m.call_count} 次")
        self.assertEqual(len(r1), 1)
        self.assertEqual(len(r2), 1)
        self.assertAlmostEqual(r2[0]["pe"], 18.22, places=4)

    def test_empty_result_not_cached(self):
        """降级空列表不得写入缓存——下次调用必须真正重新取源（自愈）。"""
        with mock.patch.object(
            _industry, "em_get", return_value=_FakeResp({"data": {"diff": []}})
        ) as m:
            self.assertEqual(get_em_board_members("BK0447"), [])
        self.assertEqual(m.call_count, 1)

        # 同 key 再取：应重新发请求（证明 [] 未被缓存），且能拿到真实数据
        with mock.patch.object(
            _industry, "em_get", return_value=_FakeResp({"data": {"diff": [_item()]}})
        ) as m2:
            r = get_em_board_members("BK0447")
        self.assertEqual(m2.call_count, 1, "空结果被缓存了 → 抖动会被冻结 15 分钟")
        self.assertEqual(len(r), 1)

    def test_distinct_board_codes_not_shared(self):
        """缓存键必须按板块区分，不能张冠李戴。"""
        with mock.patch.object(
            _industry, "em_get", return_value=_FakeResp({"data": {"diff": [_item()]}})
        ) as m:
            get_em_board_members("BK0447")
            get_em_board_members("BK0448")
        self.assertEqual(m.call_count, 2)


if __name__ == "__main__":
    unittest.main()

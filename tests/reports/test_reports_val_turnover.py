# -*- coding: utf-8 -*-
"""tests/reports/test_reports_val_turnover.py — V17.0.15 换手率缺失值语义

统一层/缓存层复核（Request H）发现的**静默假信号**缺陷：

  `get_turnover_pct`（core/data_provider.py:1919）只查 ZHB 且**无实时兜底**，
  受 `_should_use_zhb_for_realtime()` 约束——交易日 **09:30-24:00**（最常运行的
  时段）恒返回 None。原策略 01 写的是：

      turnover = await get_turnover_pct_async(code) or 0

  于是 None 被 `or 0` 变成 0，三个后果叠加成**系统性结论虚高**：
    ① 文本输出「换手率仅 0.0%，缩量企稳，筹码沉淀充分」——**由数据缺失伪造的利好**；
    ② 0 ≤ turnover_cap(8.0) → 不会被过滤掉；
    ③ (8 - 0) * 0.1 = **0.8 分，是该项的理论最高加分**。
  即：数据缺失被当成了「极度缩量」这一**极值**，而不是「未知」。

修复约定（本文件锁死）：
  1. 取值次序 = 池内已有实时字段（腾讯批量预加载，V15.5.9）> ZHB 查询；
  2. 取不到时该判据**不参与**（加分 0.0 + 文本明说"数据缺失"），
     既不伪造利好，也不因此误剔除标的（保持原"缺失不过滤"的宽容度）。
"""

from __future__ import annotations

import asyncio
import inspect
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import get_val_report as val


def _kline(close=10.0, ma10=10.0):
    return {"close": close, "ma10avgprice": ma10}


def _stock(**kw):
    s = {"code": "600519", "name": "测试", "zhangfu": 6.0}
    s.update(kw)
    return s


def _run(fn, *a, **kw):
    """同步协程（asyncio.run 每次新事件循环，避免跨用例污染）。"""
    return asyncio.run(fn(*a, **kw))


class TestStrategy01Turnover(unittest.TestCase):
    """策略 01（龙回头）换手率判据的三种取值情形。"""

    def setUp(self):
        # 命中 K 线分支：`baidu_kline_last` 返回固定 K 线，避免真实网络
        self._p = mock.patch.object(val, "baidu_kline_last", return_value=_kline())
        self._p.start()
        self.addCleanup(self._p.stop)

    # ── 情形 1：池内已有实时 turnover_pct（腾讯批量预加载）──────────────────

    def test_uses_pool_realtime_turnover(self):
        # 显式禁止回落 ZHB：若有人改回"只查 ZHB"，此处立刻红而不是静默走网络
        with mock.patch.object(
            val,
            "get_turnover_pct_async",
            side_effect=AssertionError("池内已有实时值，不得回落 ZHB"),
        ):
            r = _run(val.strategy_01_longhuitou, [_stock(turnover_pct=2.0)], "2026-08-28")
        self.assertEqual(len(r), 1)
        self.assertIn("换手率仅2.0%，缩量企稳", r[0]["reason"])
        # 加分 (8-2)*0.1 = 0.6；乖离 0 → 总分 0.6
        self.assertAlmostEqual(r[0]["score"], 0.6, places=6)

    def test_pool_turnover_preferred_over_zhb(self):
        """池内有值时不查 ZHB（ZHB 是 T-1 口径，实时优先）。"""
        with mock.patch.object(val, "get_turnover_pct_async", return_value=7.0) as m:
            r = _run(val.strategy_01_longhuitou, [_stock(turnover_pct=2.0)], "2026-08-28")
        m.assert_not_called()
        self.assertIn("换手率仅2.0%", r[0]["reason"])

    # ── 情形 2：池内无值 → 回退 ZHB ───────────────────────────────────────

    def test_falls_back_to_zhb_when_pool_missing(self):
        async def _zhb(code):
            return 3.0

        with mock.patch.object(val, "get_turnover_pct_async", side_effect=_zhb) as m:
            r = _run(val.strategy_01_longhuitou, [_stock()], "2026-08-28")
        m.assert_called_once()
        self.assertIn("换手率仅3.0%，缩量企稳", r[0]["reason"])
        self.assertAlmostEqual(r[0]["score"], 0.5, places=6)  # (8-3)*0.1

    # ── 情形 3：全部取不到 → 判据不参与（核心回归点）─────────────────────

    def test_missing_turnover_does_not_fabricate_bullish_text(self):
        """🔴 核心：缺失时不得输出"缩量企稳/筹码沉淀充分"这类伪造利好。"""
        with mock.patch.object(val, "get_turnover_pct_async", return_value=None):
            r = _run(val.strategy_01_longhuitou, [_stock()], "2026-08-28")
        self.assertEqual(len(r), 1, "缺失换手率不应剔除标的（保持原宽容度）")
        txt = r[0]["reason"]
        self.assertNotIn("缩量企稳", txt)
        self.assertNotIn("筹码沉淀充分", txt)
        self.assertNotIn("换手率仅0.0%", txt)
        self.assertIn("换手率数据缺失", txt, "必须明说数据缺失，而不是沉默")

    def test_missing_turnover_scores_zero_not_max(self):
        """🔴 核心：缺失时加分为 0.0，而非 `or 0` 退化出的理论最高分 0.8。"""
        with mock.patch.object(val, "get_turnover_pct_async", return_value=None):
            r = _run(val.strategy_01_longhuitou, [_stock()], "2026-08-28")
        # 乖离 0 → 总分 = 0 + 0.0；若为旧实现此处会是 +0.8
        self.assertAlmostEqual(r[0]["score"], 0.0, places=6)
        self.assertLess(r[0]["score"], 0.8, "缺失值不得拿到最高加分")

    def test_missing_turnover_not_filtered_out(self):
        """缺失不参与判据 ≠ 过滤：标的仍应出现在结果里。"""
        with mock.patch.object(val, "get_turnover_pct_async", return_value=None):
            r = _run(val.strategy_01_longhuitou, [_stock()], "2026-08-28")
        self.assertEqual([x["code"] for x in r], ["600519"])

    def test_zhb_exception_treated_as_missing(self):
        with mock.patch.object(val, "get_turnover_pct_async", side_effect=RuntimeError("boom")):
            r = _run(val.strategy_01_longhuitou, [_stock()], "2026-08-28")
        self.assertEqual(len(r), 1)
        self.assertIn("换手率数据缺失", r[0]["reason"])

    # ── 过滤行为（> cap 剔除）保持原语义 ─────────────────────────────────

    def test_turnover_above_cap_filters_out(self):
        r = _run(val.strategy_01_longhuitou, [_stock(turnover_pct=12.0)], "2026-08-28")
        self.assertEqual(r, [], "换手率 12% > cap 8% 应剔除")

    def test_turnover_at_cap_is_kept(self):
        r = _run(val.strategy_01_longhuitou, [_stock(turnover_pct=8.0)], "2026-08-28")
        self.assertEqual(len(r), 1, "cap 是上界，等于 cap 不剔除")

    def test_zero_in_pool_falls_back_then_missing(self):
        """池内 0 视为缺失 → 回退 ZHB；ZHB 也 None → 判据不参与。"""
        with mock.patch.object(val, "get_turnover_pct_async", return_value=None) as m:
            r = _run(val.strategy_01_longhuitou, [_stock(turnover_pct=0)], "2026-08-28")
        m.assert_called_once()
        self.assertIn("换手率数据缺失", r[0]["reason"])

    def test_strategy_is_async(self):
        self.assertTrue(inspect.iscoroutinefunction(val.strategy_01_longhuitou))


if __name__ == "__main__":
    unittest.main()

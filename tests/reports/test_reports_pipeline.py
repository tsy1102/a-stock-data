# -*- coding: utf-8 -*-
"""tests/reports/test_reports_pipeline.py — 5 个 Runner 子类 `execute_pipeline` 装配契约

补齐 docs/roadmap.md 注记 B 记录的最后一块报告层盲区：此前 `tests/reports/` 只覆盖
基类骨架（`execute_batch_pipeline`）与 val 策略注册表，**5 个 Runner 子类各自的
`execute_pipeline` 装配逻辑**没有守护。

两条装配路线：

  A. 批量型（sht / med / lng）—— 构建缓存 → 装配参数 → 委托基类 `execute_batch_pipeline`
     · 缓存**只构建一次**并注入 `gen_kwargs`（重复拉 = 队列放大，V16.4.1 修过）
     · sht 的 `depth` → 席位开关（lite 关 / deep 开）
     · sht 的 prefetch 双钩子委托到正确的数据源函数
  B. 单文件型（val / mak）—— `asyncio.run` 生成单份 md 并返回路径
     · val 的「异步失败 → 同步回退」容错
     · val 的「asyncio 成功但文件不存在 → 不假报已保存」（V16.3 O39 回归守卫）
     · mak **无**同步回退，失败必须 raise

设计约束：**纯离线**——所有数据源函数与 I/O 一律 mock，不触网、不写仓库目录。
使用 `tempfile.TemporaryDirectory()` 作为输出目录，测试结束自动清理。
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest import mock

import get_lng_report as L
import get_mak_report as K
import get_med_report as M
import get_sht_report as S
import get_val_report as V
from core import data_provider
from stock_common import sc_datasource
from stock_common.sc_report_runner import BaseReportRunner

# sht 在 execute_pipeline 里逐个拉取的指数（顺序即源码中的顺序）
SHT_INDEXES = ("sh000001", "sz399106", "sz399102", "sh000688")


def _args(output: str, **kw) -> argparse.Namespace:
    """构造最小可用的 args（与 parse_args 产出的字段对齐）。"""
    base = dict(codes=[], output=output, no_upload=True, all=False)
    base.update(kw)
    return argparse.Namespace(**base)


def _closing_run(exc: BaseException | None = None, after=None):
    """构造 `asyncio.run` 的替身。

    asyncio.run 被 mock 后，传给它的协程对象永远不会被执行，Python 会在 GC 时
    抛出 `RuntimeWarning: coroutine ... was never awaited`。替身先 `close()` 掉协程，
    再按需要抛异常或执行副作用。
    """

    def _run(coro):
        close = getattr(coro, "close", None)
        if callable(close):
            close()
        if exc is not None:
            raise exc
        if after is not None:
            after()
        return None

    return _run


class _RunnerTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.addCleanup(self._tmp.cleanup)

    @staticmethod
    def _silence():
        """吞掉被测代码里的 print（Banner/进度/emoji 均不适合污染测试输出）。"""
        return redirect_stdout(io.StringIO())


class _BatchMixin:
    """批量型（sht/med/lng）公共装配契约。子类需给出 MOD / CLS / RTYPE。"""

    MOD = None
    CLS = ""
    RTYPE = ""
    # [(patch目标, 属性名, 返回值, 期望调用次数), ...]
    # 期望次数把"批量共享数据只拉一次"这条契约钉死——V16.4.1 修过缓存值未传入导致
    # 逐股重复拉取的 bug；而指数行情是按 4 个指数循环拉的，本就该 4 次。
    CACHE_PATCHES = ()

    def _make_runner(self, **arg_kw):
        """构造 runner 并补齐 args 默认值（sht 必须有 depth，否则装配时 AttributeError）。

        med/lng 多传一个 depth 无害——args 只是 Namespace，未使用的键不会参与装配。
        """
        arg_kw.setdefault("depth", "deep")
        runner = getattr(self.MOD, self.CLS)()
        runner.args = _args(self.tmp, **arg_kw)
        return runner

    def _invoke(self, **arg_kw):
        """执行 execute_pipeline，返回 (runner, 返回值, mock 掉的基类方法)。"""
        runner = self._make_runner(**arg_kw)
        with contextlib.ExitStack() as st:
            for target, name, ret, _n in self.CACHE_PATCHES:
                st.enter_context(mock.patch.object(target, name, return_value=ret))
            bp = st.enter_context(
                mock.patch.object(
                    BaseReportRunner, "execute_batch_pipeline", return_value="PIPELINE_RESULT"
                )
            )
            result = runner.execute_pipeline()
        return runner, result, bp

    # ---- 公共契约 ----

    def test_returns_pipeline_result(self):
        """返回值必须原样透传基类的结果，不能吞掉或改写。"""
        _r, result, _bp = self._invoke()
        self.assertEqual(result, "PIPELINE_RESULT")

    def test_report_type_matches_script(self):
        """第一个位置参数必须是本脚本的 report_type（影响输出文件名/上传目录）。"""
        _r, _res, bp = self._invoke()
        self.assertEqual(bp.call_args[0][0], self.RTYPE)

    def test_generator_is_module_generate_report_async(self):
        """第二个位置参数必须是本模块的 generate_report_async。"""
        _r, _res, bp = self._invoke()
        self.assertIs(bp.call_args[0][1], self.MOD.generate_report_async)

    def test_snapshot_proxy_passed_through(self):
        """snapshot_data 必须是模块级 SnapshotProxy，否则快照落盘失效。"""
        _r, _res, bp = self._invoke()
        self.assertIs(bp.call_args.kwargs.get("snapshot_data"), getattr(self.MOD, "_SNAPSHOT_DATA"))

    def test_upstream_call_counts_pinned(self):
        """上游数据函数的调用次数必须与装配契约一致。

        共享缓存（行业对比/北向）**只能拉一次**再注入 gen_kwargs——若被挪进逐股
        路径，N 只股票就会放大成 N 次查询（V16.4.1 修过）；而指数行情按 4 个指数
        循环拉取，本就该 4 次。次数变了说明装配逻辑被改动。
        """
        if not self.CACHE_PATCHES:
            self.skipTest("本 Runner 无缓存装配")
        runner = self._make_runner()
        with contextlib.ExitStack() as st:
            spies = [
                (n, st.enter_context(mock.patch.object(t, n, return_value=r)), exp)
                for t, n, r, exp in self.CACHE_PATCHES
            ]
            st.enter_context(
                mock.patch.object(BaseReportRunner, "execute_batch_pipeline", return_value=None)
            )
            runner.execute_pipeline()
        for name, spy, expected in spies:
            self.assertEqual(
                spy.call_count, expected, f"{name} 在单次 execute_pipeline 中应调用 {expected} 次"
            )

    def test_industry_comparison_injected_into_gen_kwargs(self):
        """缓存值必须真的进 gen_kwargs，否则 generate 内部会退化为逐股重拉。"""
        if not self.CACHE_PATCHES:
            self.skipTest("本 Runner 无行业对比缓存")
        _r, _res, bp = self._invoke()
        ind = bp.call_args.kwargs["gen_kwargs"].get("ind_comp")
        self.assertEqual(ind, self.CACHE_PATCHES[0][2])


class TestShtRunnerPipeline(_BatchMixin, _RunnerTestBase):
    """短线报告：装配最复杂（4 类缓存 + 双 prefetch 钩子 + depth 席位开关）。"""

    MOD, CLS, RTYPE = S, "ShtReportRunner", "sht"
    CACHE_PATCHES = (
        (S, "get_industry_comparison", "IND_COMP", 1),
        (S, "_get_index_quote", {"code": "IDX"}, len(SHT_INDEXES)),  # 4 个指数各拉一次
        (S, "get_hsgt_macro_flow", "HSGT", 1),
    )

    # ---- 缓存装配 ----

    def test_index_quotes_collect_all_four(self):
        """四个指数全部拉取成功时，idx_q 应含 4 个键。"""
        _r, _res, bp = self._invoke()
        idx_q = bp.call_args.kwargs["gen_kwargs"]["idx_q"]
        self.assertEqual(sorted(idx_q), sorted(SHT_INDEXES))

    def test_index_quote_failures_are_skipped(self):
        """单个指数拉不到（返回 falsy）时跳过，不能塞 None 进 idx_q 让下游崩。"""
        runner = self._make_runner()

        def _iq(code):
            return None if code == "sz399102" else {"code": code}

        with contextlib.ExitStack() as st:
            st.enter_context(mock.patch.object(S, "get_industry_comparison", return_value="IND"))
            st.enter_context(mock.patch.object(S, "get_hsgt_macro_flow", return_value="HSGT"))
            st.enter_context(mock.patch.object(S, "_get_index_quote", side_effect=_iq))
            bp = st.enter_context(
                mock.patch.object(BaseReportRunner, "execute_batch_pipeline", return_value=None)
            )
            runner.execute_pipeline()

        idx_q = bp.call_args.kwargs["gen_kwargs"]["idx_q"]
        self.assertNotIn("sz399102", idx_q)
        self.assertEqual(len(idx_q), 3)
        self.assertEqual(idx_q["sh000001"]["code"], "sh000001")

    def test_hsgt_macro_flow_injected(self):
        """北向资金是批量共享数据，必须注入 gen_kwargs（V16.4.1 修过逐股重拉）。"""
        _r, _res, bp = self._invoke()
        self.assertEqual(bp.call_args.kwargs["gen_kwargs"]["hsgt"], "HSGT")

    def test_depth_forwarded_to_gen_kwargs(self):
        """depth 决定报告篇幅，必须透传给 generate。"""
        _r, _res, bp = self._invoke(depth="lite")
        self.assertEqual(bp.call_args.kwargs["gen_kwargs"]["depth"], "lite")

    # ---- prefetch 双钩子 ----

    def test_prefetch_fn_delegates_to_quote_batch(self):
        """同步预取必须走 push2delay 批量接口（1 次请求拿全部行情）。"""
        _r, _res, bp = self._invoke()
        fn = bp.call_args.kwargs["prefetch_fn"]
        codes = ["600519", "000001"]
        with mock.patch.object(data_provider, "prefetch_quote_batch", return_value="Q") as pq:
            out = fn(codes)
        self.assertEqual(out, "Q")
        pq.assert_called_once_with(codes)

    def test_prefetch_async_fn_delegates_to_datacenter(self):
        """异步预取必须走 datacenter 五类流水线，并透传 session 与 codes。"""
        _r, _res, bp = self._invoke()
        fn = bp.call_args.kwargs["prefetch_async_fn"]
        session, codes = object(), ["600519"]
        with mock.patch.object(sc_datasource, "start_datacenter_prefetch", return_value="DC") as dc:
            out = asyncio.run(fn(session, codes))
        self.assertEqual(out, "DC")
        self.assertIs(dc.call_args[0][0], codes)
        self.assertIs(dc.call_args[0][1], session)

    # ---- depth → 席位开关 ----

    def _dragon_kwargs(self, depth):
        runner = self._make_runner(depth=depth)
        with contextlib.ExitStack() as st:
            st.enter_context(mock.patch.object(S, "get_industry_comparison", return_value="IND"))
            st.enter_context(mock.patch.object(S, "_get_index_quote", return_value={"code": "X"}))
            st.enter_context(mock.patch.object(S, "get_hsgt_macro_flow", return_value="HSGT"))
            bp = st.enter_context(
                mock.patch.object(BaseReportRunner, "execute_batch_pipeline", return_value=None)
            )
            runner.execute_pipeline()
        fn = bp.call_args.kwargs["prefetch_async_fn"]
        with mock.patch.object(sc_datasource, "start_datacenter_prefetch", return_value=None) as dc:
            asyncio.run(fn(None, []))
        return dc.call_args.kwargs["dragon_kwargs"]

    def test_depth_deep_enables_seats(self):
        kw = self._dragon_kwargs("deep")
        self.assertTrue(kw["include_seats"])
        self.assertTrue(kw["enhance_seats"])

    def test_depth_lite_disables_seats(self):
        """lite 模式关席位——席位解析开销大，是 lite 提速的主要来源。"""
        kw = self._dragon_kwargs("lite")
        self.assertFalse(kw["include_seats"])
        self.assertFalse(kw["enhance_seats"])

    def test_depth_none_defaults_to_deep(self):
        """depth 为 None 时源码用 `or "deep"` 兜底，必须按 deep（开席位）处理。"""
        kw = self._dragon_kwargs(None)
        self.assertTrue(kw["include_seats"])


class TestMedRunnerPipeline(_BatchMixin, _RunnerTestBase):
    """中线报告：最简批量装配——只有行业对比缓存。"""

    MOD, CLS, RTYPE = M, "MedReportRunner", "med"
    CACHE_PATCHES = ((M, "get_industry_comparison", "IND_COMP", 1),)

    def test_gen_kwargs_contains_only_ind_comp(self):
        """med 只需 ind_comp；多传参数会让 generate 签名漂移时静默出错。"""
        _r, _res, bp = self._invoke()
        self.assertEqual(set(bp.call_args.kwargs["gen_kwargs"]), {"ind_comp"})

    def test_med_prefetch_hook_is_eltdx_warming(self):
        """med 经 prefetch_fn 预热 eltdx 短线 bundle(批量 TCP + 300s TTL 缓存, V17.2.24),
        不应传逐股异步式 prefetch_async_fn。"""
        _r, _res, bp = self._invoke()
        self.assertIn("prefetch_fn", bp.call_args.kwargs)
        self.assertTrue(callable(bp.call_args.kwargs["prefetch_fn"]))
        self.assertNotIn("prefetch_async_fn", bp.call_args.kwargs)


class TestLngRunnerPipeline(_BatchMixin, _RunnerTestBase):
    """长线报告：用模块内 industry_comparison(20)，不走公共 get_industry_comparison。"""

    MOD, CLS, RTYPE = L, "LngReportRunner", "lng"

    def test_insider_change_window_uses_trading_calendar(self):
        with mock.patch(
            "stock_common.stock_calendar.trading_day_window",
            return_value=(date(2026, 9, 24), date(2026, 9, 28)),
        ) as trading_window:
            self.assertEqual(L._recent_insider_change_window_start(), "2026-09-24")
        trading_window.assert_called_once_with(180)

    CACHE_PATCHES = ((L, "industry_comparison", "IND_COMP_20", 1),)

    def test_uses_module_level_industry_comparison_with_20(self):
        """lng 有自己的行业对比实现，top_n 固定 20——口径变了报告排名就变了。"""
        _r, _res, bp = self._invoke()
        self.assertEqual(bp.call_args.kwargs["gen_kwargs"]["ind_comp"], "IND_COMP_20")
        # 由 CACHE_PATCHES 的 spy 在 test_industry_comparison_built_only_once 中校验调用次数；
        # 此处单独确认入参：
        runner = self._make_runner()
        with contextlib.ExitStack() as st:
            spy = st.enter_context(mock.patch.object(L, "industry_comparison", return_value="X"))
            st.enter_context(
                mock.patch.object(BaseReportRunner, "execute_batch_pipeline", return_value=None)
            )
            runner.execute_pipeline()
        self.assertEqual(spy.call_args[0], (20,))

    def test_prefetch_fn_registered_sync_only(self):
        """V17.3.10: Lng 对齐 med/sht 注册同步 prefetch_fn（行情 + eltdx 连板天梯批量预取），
        但不同于 sht 的双钩子，Lng 仅用同步 prefetch_fn、不注册 prefetch_async_fn。"""
        _r, _res, bp = self._invoke()
        self.assertIn("prefetch_fn", bp.call_args.kwargs)
        self.assertTrue(callable(bp.call_args.kwargs["prefetch_fn"]))
        self.assertNotIn("prefetch_async_fn", bp.call_args.kwargs)


class _SingleFileMixin:
    """单文件型（val/mak）公共契约：生成单份 md 并返回路径。"""

    MOD = None
    CLS = ""

    def _runner(self):
        r = getattr(self.MOD, self.CLS)()
        r.args = _args(self.tmp)
        return r

    def _expected_path(self, runner):
        raise NotImplementedError


class TestValRunnerPipeline(_SingleFileMixin, _RunnerTestBase):
    """val：唯一带「异步失败 → 同步回退」的 Runner，且有 O39 假成功守卫。"""

    MOD, CLS = V, "ValReportRunner"

    def _expected_path(self, runner):
        return os.path.join(self.tmp, f"get_val_report_{runner.report_ts}.md")

    def _run_with(self, run_replacement, sync_side=None):
        """用给定的 `asyncio.run` 替身执行一次 execute_pipeline。"""
        runner = self._runner()
        buf = io.StringIO()
        with contextlib.ExitStack() as st:
            ar = st.enter_context(mock.patch.object(V.asyncio, "run", side_effect=run_replacement))
            sy = st.enter_context(mock.patch.object(V, "run_discovery", side_effect=sync_side))
            with redirect_stdout(buf):
                result = runner.execute_pipeline()
        return runner, result, buf.getvalue(), ar, sy

    def test_returns_output_path(self):
        runner = self._runner()
        expected_path = self._expected_path(runner)
        run_replacement = _closing_run(
            after=lambda: Path(expected_path).write_text("# val report\n", encoding="utf-8")
        )
        with (
            mock.patch.object(V.asyncio, "run", side_effect=run_replacement),
            mock.patch.object(V, "run_discovery"),
            self._silence(),
        ):
            result = runner.execute_pipeline()
        self.assertEqual(result, expected_path)

    def test_output_path_uses_report_ts(self):
        """路径含基类统一的 report_ts（%Y%m%d_%H%M），不能用各脚本自定义口径。"""
        runner = self._runner()
        op = self._expected_path(runner)
        self.assertIn(runner.report_ts, os.path.basename(op))
        self.assertTrue(os.path.basename(op).startswith("get_val_report_"))
        self.assertTrue(op.endswith(".md"))

    def test_async_discovery_is_invoked(self):
        """正常路径走 asyncio.run(run_discovery_async(...))。"""
        runner = self._runner()
        expected_path = self._expected_path(runner)
        run_replacement = _closing_run(
            after=lambda: Path(expected_path).write_text("# val report\n", encoding="utf-8")
        )
        with (
            mock.patch.object(V, "run_discovery_async") as asy,
            mock.patch.object(V.asyncio, "run", side_effect=run_replacement),
        ):
            with self._silence():
                runner.execute_pipeline()
        asy.assert_called_once_with(expected_path)

    def test_falls_back_to_sync_when_async_fails(self):
        """asyncio 失败必须回退同步 run_discovery —— 否则全市场发现直接空手而归。"""
        sync_side = lambda output: Path(output).write_text("# val report\n", encoding="utf-8")
        runner, _res, out, _ar, sy = self._run_with(
            _closing_run(exc=RuntimeError("boom")), sync_side=sync_side
        )
        sy.assert_called_once_with(self._expected_path(runner))
        self.assertIn("退回同步模式", out)

    def test_no_false_success_when_file_missing(self):
        """V16.3 O39 回归守卫：asyncio 成功但文件不存在时，必须报「未生成」而非「已保存」。"""
        runner = self._runner()
        buf = io.StringIO()
        sy = mock.Mock()
        with (
            mock.patch.object(V, "run_discovery_async"),
            mock.patch.object(V.asyncio, "run", side_effect=_closing_run()),
            mock.patch.object(V, "run_discovery", sy),
            redirect_stdout(buf),
            self.assertRaisesRegex(RuntimeError, "报告未生成"),
        ):
            runner.execute_pipeline()
        out = buf.getvalue()
        self.assertNotIn("已保存", out)
        sy.assert_not_called()

    def test_reports_saved_when_file_exists(self):
        """对照上一条：文件真实存在时才允许打印「已保存」。"""
        runner = self._runner()
        op = self._expected_path(runner)
        run_repl = _closing_run(
            after=lambda: Path(op).write_text("# val report\n", encoding="utf-8")
        )
        _r, _res, out, _ar, sy = self._run_with(run_repl)
        self.assertIn("已保存", out)
        sy.assert_not_called()

    def test_raises_when_both_paths_fail(self):
        """异步与同步都失败时必须抛出，让 run() 捕获并记录失败。"""
        with self.assertRaises(RuntimeError):
            self._run_with(
                _closing_run(exc=RuntimeError("async boom")), sync_side=RuntimeError("sync boom")
            )


class TestMakRunnerPipeline(_SingleFileMixin, _RunnerTestBase):
    """mak：与 val 同构但**无同步回退**——失败必须直接 raise，不能静默。"""

    MOD, CLS = K, "MakReportRunner"

    def _expected_path(self, runner):
        return os.path.join(self.tmp, f"get_mak_report_{runner.report_ts}.md")

    def test_returns_output_path(self):
        runner = self._runner()
        with mock.patch.object(K.asyncio, "run", side_effect=_closing_run()):
            with self._silence():
                result = runner.execute_pipeline()
        self.assertEqual(result, self._expected_path(runner))

    def test_output_path_uses_report_ts(self):
        runner = self._runner()
        op = self._expected_path(runner)
        self.assertIn(runner.report_ts, os.path.basename(op))
        self.assertTrue(os.path.basename(op).startswith("get_mak_report_"))

    def test_raises_on_failure(self):
        """生成失败必须抛出（run() 会打印失败并汇总），不能吞异常返回路径。"""
        runner = self._runner()
        boom = _closing_run(exc=RuntimeError("boom"))
        with mock.patch.object(K.asyncio, "run", side_effect=boom):
            with self._silence():
                with self.assertRaises(RuntimeError):
                    runner.execute_pipeline()

    def test_no_sync_fallback(self):
        """mak 没有同步回退：asyncio.run 只允许被调用一次，失败即终止。"""
        runner = self._runner()
        buf = io.StringIO()
        boom = _closing_run(exc=RuntimeError("boom"))
        with mock.patch.object(K.asyncio, "run", side_effect=boom) as ar:
            with redirect_stdout(buf):
                with self.assertRaises(RuntimeError):
                    runner.execute_pipeline()
        self.assertEqual(ar.call_count, 1)
        self.assertIn("报告生成失败", buf.getvalue())


if __name__ == "__main__":
    unittest.main()

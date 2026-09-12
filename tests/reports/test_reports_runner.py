# -*- coding: utf-8 -*-
"""tests/reports/test_reports_runner.py — ReportRunner 基类与批量流水线骨架

填补 V17.0 之前的**报告层测试空白**（`reports/` 层一度规划过但从未落地，
见 docs/roadmap.md V17-1 注记 B / tests/README.md「已知测试缺口」）。

覆盖目标：
  1. BaseReportRunner 契约（未实现即抛、时间戳字段、batch 返回结构）
  2. execute_batch_pipeline 五大骨架能力
     - 代码清洗（clean_codes 真实调用，含中文粘连）
     - **并发上限 3**（asyncio.Semaphore(3)）
     - **单股失败隔离**（一只炸了不影响整批，状态标记"数据失败"）
     - prefetch_fn / prefetch_async_fn 钩子被调用且**异常不阻塞整批**
     - snapshot_data → save_snapshot 落盘
  3. upload_multi_reports 上传编排（跳过失败项 / name_resolver / GD 失败标记）

设计约束：**纯离线**——create_async_session 被替换为假 session，
generator_fn 只写本地临时文件；save_snapshot / GD 上传均打桩。
"""
from __future__ import annotations

import argparse
import asyncio
import os
import tempfile
import unittest
from unittest import mock

from stock_common import sc_report_runner
from stock_common.sc_report_runner import BaseReportRunner


class _FakeSession:
    """替身 session：只提供 execute_batch_pipeline 需要的 close()。"""

    def __init__(self):
        self.closed = False

    async def close(self):
        self.closed = True


def _make_runner(output_dir: str, codes=None):
    """构造一个 args 已就位的 runner（no_upload=True 关闭 GD 路径）。"""
    r = BaseReportRunner("test_script", "tst", "测试报告")
    r.args = argparse.Namespace(
        codes=codes if codes is not None else [],
        output=output_dir,
        no_upload=True,
        all=False,
    )
    return r


def _ok_generator_factory(record=None):
    """生成一个"成功"的 async generator_fn：写文件 + 可选记录调用。"""

    async def _gen(session, code, path, **_kw):
        if record is not None:
            record.append(code)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# report {code}\n")
    return _gen


class TestBaseRunnerContract(unittest.TestCase):
    """基类契约。"""

    def test_execute_pipeline_not_implemented(self):
        r = _make_runner(tempfile.gettempdir())
        with self.assertRaises(NotImplementedError):
            r.execute_pipeline()

    def test_init_sets_identifiers_and_timestamps(self):
        r = BaseReportRunner("get_x_report", "x", "某报告")
        self.assertEqual(r.script_name, "get_x_report")
        self.assertEqual(r.report_type, "x")
        self.assertEqual(r.description, "某报告")
        # report_ts = %Y%m%d_%H%M（文件名/上传用）；time_str = %Y%m%d_%H%M%S（秒级）
        self.assertEqual(len(r.report_ts), 13)
        self.assertEqual(len(r.time_str), 15)
        self.assertTrue(r.report_ts.startswith(r.today_str.replace("-", "")))

    def test_upload_reports_base_is_noop(self):
        """基类 upload_reports 是空实现（子类各自重写），调用不得抛异常。"""
        r = _make_runner(tempfile.gettempdir())
        self.assertIsNone(r.upload_reports(object(), "folder", None))


class TestExecuteBatchPipeline(unittest.TestCase):
    """execute_batch_pipeline 骨架行为。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _run(self, runner, generator_fn, **kw):
        """统一打桩 create_async_session 后执行批量流水线。"""
        sessions = []

        async def _fake_create():
            s = _FakeSession()
            sessions.append(s)
            return s

        with mock.patch.object(sc_report_runner, "create_async_session", _fake_create):
            result = runner.execute_batch_pipeline("tst", generator_fn, **kw)
        return result, sessions

    # ── 1. 空代码列表 ─────────────────────────────────────────────
    def test_empty_codes_returns_empty_results(self):
        r = _make_runner(self.out, codes=[])
        res, _ = self._run(r, _ok_generator_factory())
        self.assertEqual(res["results"], [])
        self.assertEqual(res["report_type"], "tst")
        self.assertEqual(res["time_str"], r.report_ts)

    def test_invalid_codes_are_cleaned_away(self):
        """clean_codes 真实生效：纯中文项被过滤，代码与中文粘连可提取。"""
        r = _make_runner(self.out, codes=["金发", "600519 茅台"])
        called = []
        res, _ = self._run(r, _ok_generator_factory(called))
        self.assertEqual(called, ["600519"])
        self.assertEqual(len(res["results"]), 1)

    # ── 2. 全部成功 ───────────────────────────────────────────────
    def test_all_success_paths_and_status(self):
        r = _make_runner(self.out, codes=["600519", "000001"])
        res, _ = self._run(r, _ok_generator_factory())
        self.assertEqual([x["status"] for x in res["results"]], ["成功", "成功"])
        for item in res["results"]:
            self.assertEqual(item["error"], "")
            expect = os.path.join(
                self.out, f"{item['code']}_tst_{r.report_ts}.md")
            self.assertEqual(item["path"], expect)
            self.assertTrue(os.path.exists(item["path"]))

    # ── 3. 并发上限 3 ─────────────────────────────────────────────
    def test_concurrency_capped_at_three(self):
        """Semaphore(3)：9 只股票并发峰值不得超过 3。"""
        state = {"cur": 0, "peak": 0}

        async def _gen(session, code, path, **_kw):
            state["cur"] += 1
            state["peak"] = max(state["peak"], state["cur"])
            await asyncio.sleep(0.01)
            state["cur"] -= 1

        r = _make_runner(self.out, codes=[f"6005{i:02d}" for i in range(9)])
        res, _ = self._run(r, _gen)
        self.assertEqual(len(res["results"]), 9)
        self.assertLessEqual(state["peak"], 3)
        self.assertGreater(state["peak"], 1)  # 确实并发了，不是串行

    # ── 4. 单股失败隔离 ───────────────────────────────────────────
    def test_single_failure_does_not_break_batch(self):
        async def _gen(session, code, path, **_kw):
            if code == "000001":
                raise ValueError("模拟数据缺失")
            with open(path, "w", encoding="utf-8") as f:
                f.write("ok")

        r = _make_runner(self.out, codes=["600519", "000001", "600036"])
        res, _ = self._run(r, _gen)
        by_code = {x["code"]: x for x in res["results"]}
        self.assertEqual(by_code["600519"]["status"], "成功")
        self.assertEqual(by_code["600036"]["status"], "成功")
        self.assertEqual(by_code["000001"]["status"], "数据失败")
        self.assertIn("模拟数据缺失", by_code["000001"]["error"])
        self.assertEqual(by_code["000001"]["path"], "")

    # ── 5. 预取钩子 ───────────────────────────────────────────────
    def test_prefetch_fn_invoked_with_codes(self):
        seen = {}

        def _prefetch(codes):
            seen["codes"] = list(codes)
            return {c: {"name": f"N{c}"} for c in codes}

        r = _make_runner(self.out, codes=["600519"])
        self._run(r, _ok_generator_factory(), prefetch_fn=_prefetch)
        self.assertEqual(seen["codes"], ["600519"])

    def test_prefetch_fn_exception_is_tolerated(self):
        def _boom(codes):
            raise RuntimeError("预取炸了")

        r = _make_runner(self.out, codes=["600519"])
        res, _ = self._run(r, _ok_generator_factory(), prefetch_fn=_boom)
        self.assertEqual(res["results"][0]["status"], "成功")

    def test_prefetch_async_fn_invoked_and_tolerated(self):
        seen = {}

        async def _aprefetch(session, codes):
            seen["codes"] = list(codes)
            return len(codes)

        r = _make_runner(self.out, codes=["600519", "600036"])
        res, _ = self._run(r, _ok_generator_factory(), prefetch_async_fn=_aprefetch)
        self.assertEqual(seen["codes"], ["600519", "600036"])
        self.assertEqual([x["status"] for x in res["results"]], ["成功", "成功"])

        async def _aboom(session, codes):
            raise RuntimeError("异步预取炸了")

        seen.clear()
        res2, _ = self._run(r, _ok_generator_factory(), prefetch_async_fn=_aboom)
        self.assertEqual([x["status"] for x in res2["results"]], ["成功", "成功"])

    # ── 6. 快照落盘 ───────────────────────────────────────────────
    def test_snapshot_data_triggers_save_snapshot(self):
        payload = {"600519": {"score": 88}}
        r = _make_runner(self.out, codes=["600519"])
        with mock.patch("stock_common.analyze_history.save_snapshot") as m:
            self._run(r, _ok_generator_factory(), snapshot_data=payload)
        m.assert_called_once_with("tst", payload)

    def test_snapshot_skipped_when_falsy(self):
        r = _make_runner(self.out, codes=["600519"])
        with mock.patch("stock_common.analyze_history.save_snapshot") as m:
            self._run(r, _ok_generator_factory(), snapshot_data=None)
        m.assert_not_called()

    # ── 7. session 必定关闭 ───────────────────────────────────────
    def test_session_is_closed_even_on_generator_failure(self):
        async def _gen(session, code, path, **_kw):
            raise RuntimeError("x")

        r = _make_runner(self.out, codes=["600519"])
        _, sessions = self._run(r, _gen)
        self.assertTrue(sessions and all(s.closed for s in sessions))

    # ── 8. gen_kwargs 透传 ────────────────────────────────────────
    def test_gen_kwargs_forwarded(self):
        seen = {}

        async def _gen(session, code, path, industry_map=None):
            seen["industry_map"] = industry_map

        r = _make_runner(self.out, codes=["600519"])
        self._run(r, _gen, gen_kwargs={"industry_map": {"600519": "白酒"}})
        self.assertEqual(seen["industry_map"], {"600519": "白酒"})


class TestUploadMultiReports(unittest.TestCase):
    """upload_multi_reports 上传编排（GD 打桩）。"""

    def _runner(self):
        r = _make_runner("/tmp/out", codes=[])
        return r

    def test_skips_failed_and_missing_status(self):
        r = self._runner()
        results = {
            "results": [
                {"code": "600519", "status": "成功", "path": "/tmp/a.md"},
                {"code": "000001", "status": "数据失败", "path": ""},
            ],
            "time_str": "20260830_1200",
            "report_type": "tst",
        }
        with mock.patch.object(sc_report_runner, "upload_stock_report_by_code",
                               return_value=True) as up:
            r.upload_multi_reports(object(), "folder", results,
                                   name_resolver=lambda c: "名字")
        self.assertEqual(up.call_count, 1)
        self.assertEqual(up.call_args[0][2], "600519")

    def test_marks_gd_failure_status(self):
        r = self._runner()
        results = {
            "results": [{"code": "600519", "status": "成功", "path": "/tmp/a.md"}],
            "time_str": "20260830_1200",
            "report_type": "tst",
        }
        with mock.patch.object(sc_report_runner, "upload_stock_report_by_code",
                               return_value=False):
            r.upload_multi_reports(object(), "folder", results,
                                   name_resolver=lambda c: "名字")
        self.assertEqual(results["results"][0]["status"], "GD上传失败")

    def test_gd_exception_marks_upload_error(self):
        r = self._runner()
        results = {
            "results": [{"code": "600519", "status": "成功", "path": "/tmp/a.md"}],
            "time_str": "20260830_1200",
            "report_type": "tst",
        }

        def _boom(*a, **k):
            raise RuntimeError("GD 炸了")

        with mock.patch.object(sc_report_runner, "upload_stock_report_by_code", _boom):
            r.upload_multi_reports(object(), "folder", results,
                                   name_resolver=lambda c: "名字")
        self.assertEqual(results["results"][0]["status"], "GD上传异常")

    def test_non_dict_or_empty_results_is_noop(self):
        r = self._runner()
        with mock.patch.object(sc_report_runner, "upload_stock_report_by_code") as up:
            r.upload_multi_reports(object(), "folder", None)
            r.upload_multi_reports(object(), "folder", "not-a-dict")
            r.upload_multi_reports(object(), "folder", {"results": []})
        up.assert_not_called()

    def test_default_path_used_when_args_missing(self):
        """self.args=None 分支：路径回退到 tempdir，不得抛 UnboundLocalError。"""
        r = BaseReportRunner("t", "tst", "t")
        r.args = None
        results = {
            "results": [{"code": "600519", "status": "成功", "path": ""}],
            "time_str": "20260830_1200",
            "report_type": "tst",
        }
        with mock.patch.object(sc_report_runner, "upload_stock_report_by_code",
                               return_value=True) as up:
            r.upload_multi_reports(object(), "folder", results,
                                   name_resolver=lambda c: "名字")
        self.assertEqual(up.call_count, 1)
        self.assertTrue(up.call_args[0][4].startswith(tempfile.gettempdir()))


class TestDefaultResolveName(unittest.TestCase):
    """_default_resolve_name：sc_snapshot 优先，异常回退空串。"""

    def test_resolves_from_sc_snapshot(self):
        r = _make_runner("/tmp/out")
        with mock.patch("stock_common.sc_snapshot.get",
                        return_value={"name": "贵州茅台"}, create=True):
            self.assertEqual(r._default_resolve_name("600519"), "贵州茅台")

    def test_falls_back_to_empty_string_on_error(self):
        r = _make_runner("/tmp/out")

        def _boom(code):
            raise RuntimeError("snapshot unavailable")

        with mock.patch("stock_common.sc_snapshot.get", _boom, create=True):
            # 二级 tdx_get_quote_full 在离线环境同样失败 → 必须回退为 ""
            self.assertEqual(r._default_resolve_name("600519"), "")


if __name__ == "__main__":
    unittest.main()

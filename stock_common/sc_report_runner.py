#!/usr/bin/env python3
"""sc_report_runner.py — 策略报告通用运行框架 (ReportRunner)

V12.4 核心框架：
  - 统一命令行 CLI 解析 (argparse)
  - 自动运行生命周期管理 (Banner 打印 / 开始结束耗时统计 / Summary 汇总)
  - 自动报告文件本地保存与落盘
  - 自动 Google Drive (GD) 部署与增量上传 (支持单文件与批处理模式)
  - 统一网络环境清理 (cleanup_tdx, cleanup_gd_proxy)
"""

from __future__ import annotations

import os
import sys
import time
import argparse
import asyncio
from datetime import datetime, date
from typing import Any, Callable, Coroutine, Optional, cast

from stock_common import parse_args, clean_codes, create_async_session, _debug_log

try:
    from core.tdx_client import cleanup_tdx
except ImportError:
    cleanup_tdx = lambda: None

init_gd: Optional[Callable[[str], tuple[Optional[Any], bool, Optional[str], bool]]] = None
cleanup_gd_proxy: Optional[Callable[[bool], None]] = None
upload_type_reports: Optional[Callable[[Any, str, str, Any], int]] = None
upload_stock_report_by_code: Optional[Callable[[Any, str, str, str, str], bool]] = None
try:
    from core.gd_uploader import (
        init_gd as _init_gd,
        cleanup_gd_proxy as _cleanup_gd_proxy,
        upload_type_reports as _upload_type_reports,
        upload_stock_report_by_code as _upload_stock_report_by_code,
    )
except ImportError as exc:
    _debug_log(f"Google Drive uploader unavailable: {exc}")
else:
    init_gd = _init_gd
    cleanup_gd_proxy = _cleanup_gd_proxy
    upload_type_reports = _upload_type_reports
    upload_stock_report_by_code = _upload_stock_report_by_code


class BaseReportRunner:
    """策略报告运行框架基类"""

    def __init__(self, script_name: str, report_type: str, description: str):
        """
        Args:
            script_name: 脚本标识（如 "get_val_report"）
            report_type: 报告简称（如 "val", "sht", "med", "lng", "ful", "mak"）
            description: 策略描述（用于 CLI --help 和 Banner 显示）
        """
        self.script_name = script_name
        self.report_type = report_type
        self.description = description
        self.args: Optional[argparse.Namespace] = None
        # V17.0 R1: ts 口径统一——report_ts=%Y%m%d_%H%M(报告文件名/上传用, 与 5 脚本原局部计算一致);
        # time_str=%H%M%S(秒级, 历史保留)
        self.time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_ts = datetime.now().strftime("%Y%m%d_%H%M")
        self.today_str = date.today().strftime("%Y-%m-%d")

    def run(self) -> Any:
        """主运行入口：执行 CLI 解析、生命周期 Banner、流水线计算、GD上传及耗时汇总。"""
        self.args = parse_args(self.description)
        mod = sys.modules.get(self.__class__.__module__)
        mod_file = getattr(mod, '__file__', None) if mod else None
        base_dir = os.path.dirname(os.path.abspath(mod_file)) if mod_file else os.getcwd()

        os.makedirs(self.args.output, exist_ok=True)

        start_time = time.time()
        self._print_banner()

        results = None
        try:
            results = self.execute_pipeline()
        except Exception as e:
            try:
                print(f"❌ {self.description} 执行失败: {e}", flush=True)
            except UnicodeEncodeError:
                print(f"[FAIL] {self.description} 执行失败: {e}", flush=True)
            _debug_log(f"{self.script_name} run error: {e}")
            # M1 修复：不再吞掉异常，让子进程以非零退出码结束，
            # 使 main.py 的 all_ok 真实反映批量失败（收口"假成功"）。
            raise
        finally:
            cleanup_tdx()
            elapsed = time.time() - start_time
            self._print_summary(elapsed, results)

        # GD 上传独立于流水线异常捕获：上传失败不应掩盖"报告已成功生成"的事实。
        # M6 修复：若 execute_batch_pipeline 已开启 pre_gd_init 做逐股上传
        # （self._gd_per_stock=True），则此处不再二次全量上传，避免重复上传。
        if not getattr(self, "_gd_per_stock", False):
            try:
                self._handle_gd_upload(base_dir, results)
            except Exception as e:
                print(f"  ⚠️ GD 上传异常（不影响报告生成结果）: {e}", flush=True)
                _debug_log(f"{self.script_name} gd upload error: {e}")
        else:
            _debug_log(f"{self.script_name} 已逐股上传 GD，跳过末尾全量上传")

        return results

    def _print_banner(self) -> None:
        try:
            print(f"\n🚀 {self.description} 启动 — {self.today_str}", flush=True)
        except UnicodeEncodeError:
            print(f"\n[START] {self.description} 启动 — {self.today_str}", flush=True)

    def execute_pipeline(self) -> Any:
        """子类必须实现具体计算流水线。"""
        raise NotImplementedError("Subclasses must implement execute_pipeline()")

    def execute_batch_pipeline(
        self,
        report_type: str,
        generator_fn: Any,
        gen_kwargs: Optional[dict[str, Any]] = None,
        prefetch_fn: Optional[Callable[[list[str]], Any]] = None,
        snapshot_data: Any = None,
        pre_gd_init: bool = False,
        prefetch_async_fn: Optional[Callable[..., Coroutine[Any, Any, Any]]] = None,
    ) -> dict[str, Any]:
        """V17.0 R4: 批量流水线骨架(med/lng/sht 原 execute_pipeline 90 行×3 收敛)。

        Args:
            report_type: 报告简称(sht/med/lng)
            generator_fn: async (session, code, path, **gen_kwargs) -> None(单股报告生成)
            gen_kwargs: 传给 generator_fn 的固定参数(行业对比等缓存)
            prefetch_fn: 可选钩子——批量行情预取 (codes) -> {code: info}(sht push2delay ulist)
            snapshot_data: 可选——非空时保存评分快照(save_snapshot)
            pre_gd_init: 可选——生成前早 init GD 并逐只上传(防超时全丢, sht V16.4.1 修复);
                         早 init 失败自动回退 upload_reports 批量上传(_gd_per_stock=False)
            prefetch_async_fn: 可选异步钩子(async (session, codes)->int, V17.0.7)——
                         session 建立后调度后台预取流水线(sht datacenter 五类),
                         与 worker 并行推进; 失败不阻塞批量
        返回: {"results": [{code,status,error,path}...], "time_str": ts, "report_type": report_type}
        """
        ts = self.report_ts
        args = cast(argparse.Namespace, self.args)
        gen_kwargs = gen_kwargs or {}

        self._gd_per_stock = False
        _gd_drive = _gd_folder = None
        if pre_gd_init and init_gd is not None and not getattr(args, "no_upload", False):
            try:
                mod = sys.modules.get(self.__class__.__module__)
                mod_file = getattr(mod, '__file__', None) if mod else None
                base_dir = os.path.dirname(os.path.abspath(mod_file)) if mod_file else os.getcwd()
                _gd_drive, _gd_proxy_set, _gd_parent, _gd_skip = init_gd(base_dir)
                if _gd_drive and not _gd_skip and _gd_parent:
                    _gd_folder = _gd_parent
                    self._gd_per_stock = True
            except Exception as _e:
                _debug_log(f"{self.script_name} early gd init: {_e}")

        async def _main_async() -> list[dict[str, str]]:
            codes = clean_codes(args.codes, verbose=True)
            if not codes:
                print("  ❌ 没有有效的股票代码")
                return []
            _pre: dict[str, Any] = {}
            if prefetch_fn is not None:
                try:
                    _pre = prefetch_fn(codes) or {}
                    print(f"  📡 批量行情预取: {len(_pre)}/{len(codes)} 只命中", flush=True)
                except Exception as _e:
                    _debug_log(f"{self.script_name} batch prefetch: {_e}")
            for code in codes:
                try:
                    print(f"  📋 加入队列: {code}", flush=True)
                except UnicodeEncodeError:
                    print(f"  [INFO] 加入队列: {code}", flush=True)

            _session = await create_async_session()
            _prefetch_task = None
            _gathered: list[dict[str, str]] = []
            try:
                # M5 修复：prefetch_async_fn 改为后台任务(asyncio.create_task)，
                # 与 3 条 worker 真正并行推进（原 await 在前置位置导致串行，
                # 注释"与 worker 并行"与实际行为不符）。它只做 datacenter 预热、
                # 不产出 _pre，故并行不影响逐股 GD 上传逻辑。
                if prefetch_async_fn is not None:
                    try:
                        _prefetch_task = asyncio.create_task(prefetch_async_fn(_session, codes))
                        print("  📡 datacenter 预取流水线: 已后台启动(与 worker 并行)", flush=True)
                    except Exception as _e:
                        _debug_log(f"{self.script_name} prefetch_async_fn schedule: {_e}")
                sem = asyncio.Semaphore(3)

                async def _limited(code: str) -> dict[str, str]:
                    async with sem:
                        result_path = os.path.join(args.output, f"{code}_{report_type}_{ts}.md")
                        try:
                            await generator_fn(_session, code, result_path, **gen_kwargs)
                            print(f"  ✅ 已保存: {result_path}", flush=True)
                            if _gd_folder and _gd_drive:
                                try:
                                    _nm = (_pre.get(code, {}) or {}).get("name", "") or code
                                    from core.gd_uploader import upload_stock_report_by_code as _up

                                    _up(_gd_drive, _gd_folder, code, _nm, result_path)
                                    print(f"  📎 已上传 GD: {code} ({_nm})", flush=True)
                                except Exception as _e:
                                    _debug_log(
                                        f"{self.script_name} per-stock gd upload {code}: {_e}"
                                    )
                            return {
                                "code": code,
                                "status": "成功",
                                "error": "",
                                "path": result_path,
                            }
                        except Exception as e:
                            import traceback as _tb

                            _tb.print_exc()  # V17.0.4: 数据失败打印完整堆栈(诊断价值)
                            print(f"❌ {code} 数据生成失败: {e}", flush=True)
                            return {"code": code, "status": "数据失败", "error": str(e), "path": ""}

                _gathered = await asyncio.gather(*[_limited(c) for c in codes])
            finally:
                await _session.close()
                if _prefetch_task is not None:
                    try:
                        _n = await _prefetch_task
                        print(f"  📡 datacenter 预取流水线: {_n} 项入队完成", flush=True)
                    except Exception as _e:
                        _debug_log(f"{self.script_name} prefetch_async_fn: {_e}")
            return _gathered

        _results = asyncio.run(_main_async())

        if snapshot_data:
            from stock_common.analyze_history import save_snapshot

            # V17.3.14 修复: snapshot_data 可能是 SnapshotProxy (V15.3.1 引入, 非 dict 子类)。
            # 原 M6 的 isinstance(snapshot_data, dict) 校验对其永远为 False → save_snapshot
            # 自 V17.1.0 起从未被调用 → 评分快照 JSON 永不落盘 → analyze_history 读空 →
            # 评分突变背离(≥15分)报告永久消失。现先规整为真实 dict 再走结构校验与保存。
            if isinstance(snapshot_data, dict):
                _snap = snapshot_data
            elif hasattr(snapshot_data, "items"):
                _snap = dict(snapshot_data.items())
            else:
                _snap = None

            # M6 修复：快照结构校验——只接受 {code: {name, total_score}} 形态。
            # 误传 pipeline results（非该形态）会让跨日期背离检测静默成空壳，故校验后保存。
            if _snap is not None and isinstance(_snap, dict):
                _bad = [
                    c
                    for c, v in _snap.items()
                    if not (isinstance(v, dict) and ("total_score" in v or "score" in v))
                ]
                if _bad:
                    _debug_log(f"{self.script_name} snapshot 结构异常，跳过保存: {_bad[:5]}")
                    print(
                        f"  ⚠️ 评分快照结构异常（{len(_bad)} 项缺 total_score/score），跳过保存",
                        flush=True,
                    )
                else:
                    save_snapshot(report_type, _snap)
            elif _snap is None:
                _debug_log(f"{self.script_name} snapshot_data 非字典且无可迭代 items，跳过保存")

        ok = [r for r in _results if r["status"] == "成功"]
        fd = [r for r in _results if r["status"] == "数据失败"]
        print(f"\n{'='*60}\n  批量执行完成 — 共处理 {len(_results)} 只股票\n{'='*60}")
        print(f"  ✅ 全部成功: {len(ok)}  |  ❌ 数据失败: {len(fd)}")
        for r in fd:
            print(f"    ❌ {r['code']} — {r['error'][:80]}")

        return {"results": _results, "time_str": ts, "report_type": report_type}

    def _handle_gd_upload(self, base_dir: str, results: Any) -> None:
        """统一 GD 上传逻辑。"""
        if self.args and getattr(self.args, 'no_upload', False):
            return

        if init_gd is None:
            return

        drive, gd_proxy_set, gd_parent_folder_id, skip_upload = init_gd(base_dir)
        try:
            if drive and not skip_upload and gd_parent_folder_id:
                self.upload_reports(drive, gd_parent_folder_id, results)
            elif skip_upload or not gd_parent_folder_id:
                print("  ⚠️ GD 云端同步跳过：未能获取云盘根文件夹「a-stock-data」", flush=True)
        except Exception as e:
            try:
                print(f"  ⚠️ GD 上传异常: {e}", flush=True)
            except UnicodeEncodeError:
                print(f"  [WARN] GD 上传异常: {e}", flush=True)
        finally:
            if cleanup_gd_proxy is not None:
                cleanup_gd_proxy(gd_proxy_set)

    def upload_reports(self, drive: Any, folder_id: str, results: Any) -> None:
        """子类可重写具体 GD 上传方式。
        基类提供两个辅助方法供子类直接调用：
          - upload_single_report: 单文件报告（如 val/mak/ful）
          - upload_multi_reports:  多文件报告（sht/med/lng）
        """
        pass

    def upload_single_report(self, drive: Any, folder_id: str, output_file: str) -> bool:
        """上传单文件报告 (val/mak/ful 等)。返回是否成功。"""
        if not output_file or not os.path.exists(output_file):
            return False
        if upload_type_reports is None:
            return False
        ok = upload_type_reports(drive, folder_id, self.report_type, [output_file])
        if ok <= 0:
            try:
                print("  ⚠️ GD 上传失败", flush=True)
            except UnicodeEncodeError:
                print("  [WARN] GD upload failed", flush=True)
            return False
        return True

    def upload_multi_reports(
        self,
        drive: Any,
        folder_id: str,
        results: dict[str, Any],
        name_resolver: Optional[Callable[[str], str]] = None,
    ) -> None:
        """批量上传多文件报告 (sht/med/lng 等)。

        Args:
            results: 标准格式 {"results": [...], "time_str": ts, "report_type": ...}
            name_resolver: 解析股票名称的可调用对象 fn(code) -> str
                          若未提供，默认使用 _SNAPSHOT_DATA 或 tdx_get_quote_full
        """
        if not results or not isinstance(results, dict):
            return
        if upload_stock_report_by_code is None:
            return
        ts = results.get("time_str", "")
        report_type = results.get("report_type", self.report_type)
        for r in results.get("results", []):
            if r.get("status") != "成功" or not drive or not folder_id:
                continue
            code = r.get("code", "")
            # V15.3 P0 修复: 原代码 `if self.args else path` 在 self.args=None 时
            # 引用未定义的 path → UnboundLocalError。重构为单步赋值。
            if self.args:
                default_path = os.path.join(self.args.output, f"{code}_{report_type}_{ts}.md")
            else:
                # self.args=None 时用临时目录兜底（仅作为库使用时不传 args 场景）
                from stock_common._temp import configure_project_temp

                default_path = os.path.join(
                    str(configure_project_temp()), f"{code}_{report_type}_{ts}.md"
                )
            path = r.get("path", default_path) or default_path
            try:
                q_name = ""
                if name_resolver is not None:
                    q_name = name_resolver(code)
                else:
                    q_name = self._default_resolve_name(code)
                if not upload_stock_report_by_code(drive, folder_id, code, q_name, path):
                    r["status"] = "GD上传失败"
            except Exception as gd_e:
                try:
                    print(f"  ⚠️ GD 上传异常: {gd_e}", flush=True)
                except UnicodeEncodeError:
                    print(f"  [WARN] GD upload error: {gd_e}", flush=True)
                r["status"] = "GD上传异常"

    def _default_resolve_name(self, code: str) -> str:
        """默认股票名解析器：先查 sc_snapshot，再退回 tdx_get_quote_full。

        V15.3 修复: 原代码用 globals().get("_SNAPSHOT_DATA") 跨报告查找，
        依赖模块级全局变量在多报告场景下不可靠。统一从 stock_common.sc_snapshot 查。
        """
        try:
            # V15.3: 优先从 sc_snapshot 查（4 大报告注册单一来源）
            from stock_common import sc_snapshot

            snap = sc_snapshot.get(code)
            name = snap.get("name") if snap else None
            if isinstance(name, str) and name:
                return name
            # 兼容：4 大报告的 _SNAPSHOT_DATA 代理对象也走 sc_snapshot
            snap = globals().get("_SNAPSHOT_DATA")
            if snap is not None:
                if hasattr(snap, "__contains__") and code in snap:
                    val = snap[code]
                    if isinstance(val, dict):
                        name = val.get("name")
                        if isinstance(name, str) and name:
                            return name
        except Exception:
            pass
        try:
            from core.tdx_client import tdx_get_quote_full

            quote = tdx_get_quote_full(code)
            name = quote.get("name") if isinstance(quote, dict) else None
            return name if isinstance(name, str) else ""
        except Exception:
            return ""

    def _print_summary(self, elapsed: float, results: Any) -> None:
        try:
            print(f"\n⏱ 执行完成，总耗时: {elapsed:.2f} 秒", flush=True)
        except UnicodeEncodeError:
            print(f"\n[TIME] 执行完成，总耗时: {elapsed:.2f} 秒", flush=True)

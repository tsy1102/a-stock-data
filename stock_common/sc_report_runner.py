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
from typing import Any, Dict, List, Optional, Tuple

from stock_common import (
    parse_args,
    _debug_log
)

try:
    from tdx_client import cleanup_tdx
except ImportError:
    cleanup_tdx = lambda: None

try:
    from gd_uploader import (
        init_gd,
        cleanup_gd_proxy,
        upload_type_reports,
        upload_stock_report_by_code
    )
except ImportError:
    init_gd = None
    cleanup_gd_proxy = None
    upload_type_reports = None
    upload_stock_report_by_code = None


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
        self.time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
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
            self._handle_gd_upload(base_dir, results)
        except Exception as e:
            try:
                print(f"❌ {self.description} 执行失败: {e}", flush=True)
            except UnicodeEncodeError:
                print(f"[FAIL] {self.description} 执行失败: {e}", flush=True)
            _debug_log(f"{self.script_name} run error: {e}")
        finally:
            if cleanup_tdx:
                cleanup_tdx()
            elapsed = time.time() - start_time
            self._print_summary(elapsed, results)

        return results

    def _print_banner(self) -> None:
        try:
            print(f"\n🚀 {self.description} 启动 — {self.today_str}", flush=True)
        except UnicodeEncodeError:
            print(f"\n[START] {self.description} 启动 — {self.today_str}", flush=True)

    def execute_pipeline(self) -> Any:
        """子类必须实现具体计算流水线。"""
        raise NotImplementedError("Subclasses must implement execute_pipeline()")

    def _handle_gd_upload(self, base_dir: str, results: Any) -> None:
        """统一 GD 上传逻辑。"""
        if self.args and getattr(self.args, 'no_upload', False):
            return

        if not init_gd:
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
            if cleanup_gd_proxy:
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
        if not upload_type_reports:
            return False
        ok = upload_type_reports(drive, folder_id, self.report_type, [output_file])
        if ok <= 0:
            try:
                print("  ⚠️ GD 上传失败", flush=True)
            except UnicodeEncodeError:
                print("  [WARN] GD upload failed", flush=True)
            return False
        return True

    def upload_multi_reports(self, drive: Any, folder_id: str, results: dict,
                             name_resolver: Optional[callable] = None) -> None:
        """批量上传多文件报告 (sht/med/lng 等)。

        Args:
            results: 标准格式 {"results": [...], "time_str": ts, "report_type": ...}
            name_resolver: 解析股票名称的可调用对象 fn(code) -> str
                          若未提供，默认使用 _SNAPSHOT_DATA 或 tdx_get_quote_full
        """
        if not results or not isinstance(results, dict):
            return
        if not upload_stock_report_by_code:
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
                default_path = os.path.join(
                    self.args.output, f"{code}_{report_type}_{ts}.txt"
                )
            else:
                # self.args=None 时用临时目录兜底（仅作为库使用时不传 args 场景）
                import tempfile
                default_path = os.path.join(
                    tempfile.gettempdir(), f"{code}_{report_type}_{ts}.txt"
                )
            path = r.get("path", default_path) or default_path
            try:
                q_name = ""
                if name_resolver:
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
            if snap and snap.get("name"):
                return snap["name"]
            # 兼容：4 大报告的 _SNAPSHOT_DATA 代理对象也走 sc_snapshot
            snap = globals().get("_SNAPSHOT_DATA")
            if snap is not None:
                if hasattr(snap, "__contains__") and code in snap:
                    val = snap[code]
                    if isinstance(val, dict) and val.get("name"):
                        return val["name"]
        except Exception:
            pass
        try:
            from tdx_client import tdx_get_quote_full
            return (tdx_get_quote_full(code) or {}).get("name", "")
        except Exception:
            return ""

    def _print_summary(self, elapsed: float, results: Any) -> None:
        try:
            print(f"\n⏱ 执行完成，总耗时: {elapsed:.2f} 秒", flush=True)
        except UnicodeEncodeError:
            print(f"\n[TIME] 执行完成，总耗时: {elapsed:.2f} 秒", flush=True)

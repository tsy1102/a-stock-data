#!/usr/bin/env python3
"""main.py — V8.4 统一 CLI 入口（脚本内 asyncio 并发 + 进程级串行防封）

并发策略（两层次序，确保东财接口不被封）：
  1) 进程级：asyncio.create_subprocess_exec 串行运行脚本（concurrency=1）
  2) 脚本级：每个脚本内部用 Semaphore(3) 并发 3 只股票
             (stock_common.py 的 Semaphore(3) + 1.1s 间隔统一控制)

使用方式与旧版完全兼容，仅内部优化：
  python main.py --sht 600519 --med 002310 --lng 688088 --ful 600519
  python main.py --all 600519 000858
  python main.py --val --mak --no-upload
"""

import argparse
import asyncio
import os
import sys
import time
from datetime import datetime

from stock_common import get_script_dir, ensure_output_dir, clean_codes

_SCRIPT_DIR = get_script_dir()


def check_dependencies():
    """V7.5: 检查必要依赖是否已安装，缺失时提示用户。"""
    missing = []
    try:
        import aiohttp
    except ImportError:
        missing.append("aiohttp")
    try:
        import yaml
    except ImportError:
        missing.append("yaml")
    try:
        import google.auth
    except ImportError:
        missing.append("google-auth")
    try:
        import google.oauth2
    except ImportError:
        missing.append("google-auth-oauthlib")
    try:
        import googleapiclient
    except ImportError:
        missing.append("google-api-python-client")
    try:
        import requests
    except ImportError:
        missing.append("requests")
    try:
        import easy_tdx
    except ImportError:
        missing.append("easy-tdx")

    if missing:
        print("=" * 60, flush=True)
        print("  ❌ 缺少必要依赖，请先安装:", flush=True)
        for pkg in missing:
            print(f"     pip install {pkg}", flush=True)
        print("=" * 60, flush=True)
        sys.exit(1)


# 程序启动前检查依赖
check_dependencies()
_MAX_CONCURRENCY = 1  # 关键：脚本内部已用 Semaphore(3) 并发 3 只股票，进程级串行脚本避免叠加


def parse_args():
    parser = argparse.ArgumentParser(
        description="V8.4: A股数据工具 — 统一入口（并发版，防封限流）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --sht 600519 002310 --med 002310 --lng 688088 --ful 600519 --val --mak
      顺序运行: 短线 + 中线 + 长线 + 全维度分析 + 全市场选股 + 异动扫描
      注意: 每个脚本内部以 Semaphore(3) 并发 3 只股票 —— 脚本串行避免请求叠加被封

  python main.py --all 600519 000858     所有报告共用同一股票列表
  python main.py --sht 600519            只跑短线
  python main.py --ful 600519           只跑全维度分析
  python main.py --val --no-upload        只跑全市场选股，不上传 GD
  python main.py --mak                    只跑异动扫描（不需要股票代码）
  python main.py --concurrency 3         自定义并发数（默认 1，不推荐超过 2，避免请求叠加风险）
""",
    )
    parser.add_argument(
        "--sht", nargs="*", default=[],
        help="短线报告股票代码（可多个）"
    )
    parser.add_argument(
        "--med", nargs="*", default=[],
        help="中线报告股票代码（可多个）"
    )
    parser.add_argument(
        "--lng", nargs="*", default=[],
        help="长线报告股票代码（可多个）"
    )
    parser.add_argument(
        "--ful", nargs="*", default=[],
        help="全维度分析报告股票代码（可多个）"
    )
    parser.add_argument(
        "--val", action="store_true",
        help="全市场选股报告（不需要股票代码）"
    )
    parser.add_argument(
        "--mak", action="store_true",
        help="异动扫描报告（不需要股票代码）"
    )
    parser.add_argument(
        "--all", nargs="*", default=[],
        help="所有报告共用此股票列表（优先级低于 --sht/--med/--lng 单独指定）"
    )
    parser.add_argument(
        "-o", "--output",
        default=os.path.join(_SCRIPT_DIR, "reports"),
        help="报告输出目录（默认: 脚本目录下的 reports/）"
    )
    parser.add_argument(
        "--no-upload", action="store_true",
        help="跳过 Google Drive 上传"
    )
    parser.add_argument(
        "--concurrency", type=int, default=_MAX_CONCURRENCY,
        help="最大并发脚本数（默认 2，不推荐超过 3）"
    )
    return parser.parse_args()


async def _run_script_async(script: str, stock_codes: list, output_dir: str,
                            no_upload: bool, label: str) -> tuple:
    """asyncio 子进程方式并发运行一个报告脚本。"""
    script_path = os.path.join(_SCRIPT_DIR, script)
    if not os.path.isfile(script_path):
        print(f"  [{label}] {script} 文件不存在，跳过", flush=True)
        return script, 0, 0.0, label

    cmd = [sys.executable, script_path]
    if stock_codes:
        cmd += stock_codes
    cmd += ["-o", output_dir]
    if no_upload:
        cmd.append("--no-upload")

    codes_str = " ".join(stock_codes) if stock_codes else "(无股票代码)"
    print(f"\n▶ [{label}] 启动: {script} {codes_str}", flush=True)

    t0 = time.time()
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=_SCRIPT_DIR,
            stdout=None,   # 继承父进程 stdout，让每个脚本的输出实时可见
            stderr=None,
        )
        rc = await proc.wait()
        dt = time.time() - t0
        status = "完成" if rc == 0 else f"失败({rc})"
        print(f"\n✔ [{label}] {script} {status} ({dt:.1f}s)", flush=True)
        return script, rc, dt, label
    except KeyboardInterrupt:
        print(f"\n⚠ [{label}] {script} 被用户中断", flush=True)
        return script, 130, time.time() - t0, label
    except Exception as e:
        print(f"\n✖ [{label}] {script} 运行异常: {e}", flush=True)
        return script, 1, time.time() - t0, label


async def main_async():
    args = parse_args()

    # 清洗股票代码：提取6位数字、去重、过滤无效项
    args.sht = clean_codes(args.sht, verbose=True)
    args.med = clean_codes(args.med, verbose=True)
    args.lng = clean_codes(args.lng, verbose=True)
    args.ful = clean_codes(args.ful, verbose=True)
    args.all = clean_codes(args.all, verbose=True)

    # 判断运行模式
    has_flag = any([args.sht, args.med, args.lng, args.ful, args.val, args.mak, args.all])
    is_all_mode = bool(args.all) and not any([args.sht, args.med, args.lng, args.ful, args.val, args.mak])

    if not has_flag:
        # 无任何标志：默认跑 --all（所有报告，共用空股票列表，即全市场扫描）
        args.all = []

    output_dir = ensure_output_dir(args.output)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conc = min(max(args.concurrency, 1), 5)
    print(f"[{ts}] V8.4 批量报告启动 | 并发度: {conc} | 输出目录: {output_dir}", flush=True)
    print(f"  GD上传: {'跳过' if args.no_upload else '启用'} | 防封限流: 文件协调 + 1.0s+ 间隔", flush=True)
    print("-" * 60, flush=True)

    # 确定每个脚本的股票代码列表
    sht_codes = args.sht if args.sht else args.all
    med_codes = args.med if args.med else args.all
    lng_codes = args.lng if args.lng else args.all
    full_codes = args.ful if args.ful else args.all

    # 构造所有待运行的任务
    tasks_info = []
    for script, codes, label in [
        ("get_sht_report.py", sht_codes, "短线"),
        ("get_med_report.py", med_codes, "中线"),
        ("get_lng_report.py", lng_codes, "长线"),
        ("get_ful_report.py", full_codes, "全维度"),
    ]:
        codes_to_use = args.all if is_all_mode else codes
        if codes_to_use:
            tasks_info.append((script, codes_to_use, output_dir, args.no_upload, label))

    if args.val:
        tasks_info.append(("get_val_report.py", [], output_dir, args.no_upload, "全市场选股"))
    if args.mak:
        tasks_info.append(("get_mak_report.py", [], output_dir, args.no_upload, "异动扫描"))

    if not tasks_info:
        print("  没有可运行的脚本，请检查参数。", flush=True)
        sys.exit(0)

    total_t0 = time.time()
    print(f"\n▶ 准备运行 {len(tasks_info)} 个报告脚本 (每批最多 {conc} 个并发)", flush=True)

    # 分批：每批最多 conc 个并发，避免瞬间发大量请求
    results_raw = []
    for batch_start in range(0, len(tasks_info), conc):
        batch = tasks_info[batch_start:batch_start + conc]
        batch_idx = batch_start // conc + 1
        print(f"\n  [第 {batch_idx} 批] 并发运行 {len(batch)} 个脚本: " +
              ", ".join(f"{t[4]}" for t in batch), flush=True)

        batch_tasks = [_run_script_async(*t) for t in batch]
        batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        results_raw.extend(batch_results)

        # 批与批之间留 2s 间隔，降低被封风险
        if batch_start + conc < len(tasks_info):
            print(f"  [第 {batch_idx} 批完成] 等待 2s 后启动下一批（降低东财接口压力）", flush=True)
            await asyncio.sleep(2.0)

    total_time = time.time() - total_t0
    results = {}
    for item in results_raw:
        if isinstance(item, Exception):
            print(f"  ✖ 任务异常: {item}", flush=True)
            continue
        script, rc, dt, label = item
        results[script] = (rc, dt, label, [])

    # 汇总
    print(f"\n{'=' * 60}", flush=True)
    print(f"[完成] V8.4 批量报告总耗时: {total_time:.1f} 秒 " +
          f"(每批 {conc} 并发，已做三层防封保护：线程锁 + 进程间文件协调 + 时间戳)",
          flush=True)
    for name, (rc, dt, label, _) in results.items():
        status = "OK" if rc == 0 else f"FAIL({rc})"
        print(f"  {label}: {status} ({dt:.1f}s)", flush=True)
    print(f"{'=' * 60}", flush=True)

    all_ok = all(v[0] == 0 for v in results.values())
    
    # V7.5 新增：自动运行历史快照分析
    try:
        from analyze_history import analyze_history
        print(f"\n{'=' * 60}", flush=True)
        print("[分析] 正在运行历史快照对比分析...", flush=True)
        report = analyze_history()
        print(report, flush=True)
    except ImportError as e:
        print(f"  ⚠️ 历史分析模块未找到: {e}", flush=True)
    except Exception as e:
        print(f"  ⚠️ 历史分析运行异常: {e}", flush=True)
    
    sys.exit(0 if all_ok else 1)


def main():
    """同步入口（向后兼容）"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n用户中断，退出。", flush=True)
        sys.exit(130)


if __name__ == "__main__":
    main()

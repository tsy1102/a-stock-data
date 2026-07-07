#!/usr/bin/env python3
"""main.py — V9.3 统一 CLI 入口（脚本内 asyncio 并发 + 进程级串行防封）

并发策略（两层次序，确保东财接口不被封）：
  1) 进程级：asyncio.create_subprocess_exec 串行运行脚本（concurrency=1）
  2) 脚本级：每个脚本内部用 Semaphore(3) 并发 3 只股票
             (stock_common.py 的 Semaphore(3) + 1.1s 间隔统一控制)

V9.3 更新：
  - 修复 --no-upload 参数对快照异常上传未生效的问题（传递 skip_upload 参数）
  - 删除终端输出中的硬编码版本号（如 V8.9）

V9.2 更新：
  - 缓存交叉验证机制（多天 TTL 分类启用 cross_verify）
  - 全量异常处理规范化（无裸 pass，静默异常均加日志）
  - 交易日历数据可通过脚本更新

V9.1 更新：
  - 配合 F10 全覆盖升级：所有报告脚本集成 F10 章节+数据质量附录
  - 缓存层支持 trading_day 过期策略（F10 高频分类按交易日过期）

使用方式与旧版兼容，新增混合模式：
  python main.py --sht 600519 --med 002310 --lng 688088 --ful 600519
  python main.py --all 600519 000858
  python main.py --sht 111111 --all 555555     # 短线处理111111+555555，其他类型只处理555555
  python main.py --val --mak --no-upload
"""

import argparse
import asyncio
import os
import sys
import time
from datetime import datetime

from stock_common import get_script_dir, ensure_output_dir, clean_codes

# 新的混合模式参数处理策略：
# 1. 如果指定了--all，则每个脚本类型的股票 = 单独指定股票 + --all股票
# 2. 如果没有指定--all，则每个脚本类型使用单独指定的股票
# 3. 支持空列表：例如--all []表示只处理所有类型的空列表（全市场扫描）
# 4. 合并时自动去重：--sht 600519 --all 600519 → 短线只处理一次600519

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
_MAX_CONCURRENCY = 1  # 关键：脚本内部已用 Semaphore(3) 并发 3 只股票，进程级串行脚本避免叠加


def parse_args():
    parser = argparse.ArgumentParser(
        description="A股数据工具 — 统一入口（并发版，防封限流）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --sht 600519 002310 --med 002310 --lng 688088 --ful 600519 --val --mak
      顺序运行: 短线 + 中线 + 长线 + 全维度分析 + 全市场选股 + 异动扫描
      注意: 每个脚本内部以 Semaphore(3) 并发 3 只股票 —— 脚本串行避免请求叠加被封

  python main.py --all 600519 000858     所有报告共用同一股票列表（传统模式）
  python main.py --sht 111111 --all 555555  短线处理111111+555555，其他类型处理555555（混合模式）
  python main.py --sht 600519            只跑短线
  python main.py --ful 600519           只跑全维度分析
  python main.py --val --no-upload        只跑全市场选股，不上传 GD
  python main.py --mak                    只跑异动扫描（不需要股票代码）
  python main.py --concurrency 3         自定义并发数（默认 1，不推荐超过 2，避免请求叠加风险）

  混合模式优势：每个脚本类型可以批量处理更多股票，提高并发效率
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
        help="所有报告共用此股票列表（将与单独指定的参数合并，支持混合批量处理）"
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
    """asyncio 子进程方式并发运行一个报告脚本。
    
    asyncio 子进程方式并发运行一个报告脚本。
    
    在混合模式下，每个脚本会批量处理指定的股票代码列表，
    充分利用脚本内部的并发机制（Semaphore(3)）来提高效率。
    """
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
    print(f"▶ [{label}] 启动: {script} {codes_str}", flush=True)

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
        print(f"✔ [{label}] {script} {status} ({dt:.1f}s)", flush=True)
        return script, rc, dt, label
    except KeyboardInterrupt:
        print(f"⚠ [{label}] {script} 被用户中断", flush=True)
        return script, 130, time.time() - t0, label
    except Exception as e:
        print(f"✖ [{label}] {script} 运行异常: {e}", flush=True)
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
    
    if not has_flag:
        # 无任何标志：默认跑 --all（所有报告，共用空股票列表，即全市场扫描）
        args.all = []
        is_all_mode = True
    else:
        # 有参数时：如果指定了--all，则与单独指定参数共存
        is_all_mode = False  # 使用新的混合模式，不是纯all模式

    output_dir = ensure_output_dir(args.output)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conc = min(max(args.concurrency, 1), 5)
    print(f"[{ts}] 批量报告启动 | 并发度: {conc} | 输出目录: {output_dir}", flush=True)
    print(f"  GD上传: {'跳过' if args.no_upload else '启用'} | 防封限流: 文件协调 + 1.0s+ 间隔", flush=True)
    print("-" * 60, flush=True)

    # 确定每个脚本的股票代码列表（混合模式：单独指定 + --all合并）
    # 策略：每个脚本类型 = 单独指定的股票 + --all的股票（合并去重）
    # 例如：--sht 111111 --all 555555 → 短线处理[111111, 555555]，其他类型处理[555555]
    # 例如：--med 222222 --all 555555 → 中线处理[222222, 555555]，其他类型处理[555555]
    sht_codes = list(set(args.sht + args.all)) if args.all else args.sht
    med_codes = list(set(args.med + args.all)) if args.all else args.med
    lng_codes = list(set(args.lng + args.all)) if args.all else args.lng
    full_codes = list(set(args.ful + args.all)) if args.all else args.ful

    # 构造所有待运行的任务
    tasks_info = []
    for script, codes, label in [
        ("get_sht_report.py", sht_codes, "短线"),
        ("get_med_report.py", med_codes, "中线"),
        ("get_lng_report.py", lng_codes, "长线"),
        ("get_ful_report.py", full_codes, "全维度"),
    ]:
        # 在混合模式下，每个脚本都使用自己的股票代码列表
        if codes:
            tasks_info.append((script, codes, output_dir, args.no_upload, label))

    if args.val:
        tasks_info.append(("get_val_report.py", [], output_dir, args.no_upload, "全市场选股"))
    if args.mak:
        tasks_info.append(("get_mak_report.py", [], output_dir, args.no_upload, "异动扫描"))

    if not tasks_info:
        print("  没有可运行的脚本，请检查参数。", flush=True)
        sys.exit(0)

    total_t0 = time.time()
    print(f"▶ 准备运行 {len(tasks_info)} 个报告脚本 (每批最多 {conc} 个并发)", flush=True)

    # 分批：每批最多 conc 个并发，避免瞬间发大量请求
    results_raw = []
    for batch_start in range(0, len(tasks_info), conc):
        batch = tasks_info[batch_start:batch_start + conc]
        batch_idx = batch_start // conc + 1
        print(f"  [第 {batch_idx} 批] 并发运行 {len(batch)} 个脚本: " +
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
    print(f"{'=' * 60}", flush=True)
    print(f"[完成] 批量报告总耗时: {total_time:.1f} 秒 " +
          f"(每批 {conc} 并发，已做三层防封保护：线程锁 + 进程间文件协调 + 时间戳)",
          flush=True)
    for name, (rc, dt, label, _) in results.items():
        status = "OK" if rc == 0 else f"FAIL({rc})"
        print(f"  {label}: {status} ({dt:.1f}s)", flush=True)
    print(f"{'=' * 60}", flush=True)

    all_ok = all(v[0] == 0 for v in results.values())
    
    # V7.5 新增：自动运行历史快照分析
    try:
        from stock_common.analyze_history import analyze_history
        print(f"{'=' * 60}", flush=True)
        print("[分析] 正在运行历史快照对比分析...", flush=True)
        report = analyze_history(skip_upload=args.no_upload)
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
    check_dependencies()
    main()

#!/usr/bin/env python3
"""main.py — 统一 CLI 入口（脚本内 asyncio 并发 + 进程级串行防封）

并发策略（两层次序，确保东财接口不被封）：
  1) 进程级：asyncio.create_subprocess_exec 串行运行脚本（concurrency=1）
  2) 脚本级：每个脚本内部用 Semaphore(3) 并发 3 只股票
             (stock_common.py 的 Semaphore(3) + 1.1s 间隔统一控制)

V15.0 更新：
  - 接入 CanonicalStockData 标准化强类型数据合约
  - ZHB-First 真实生成周期（T+1 清晨 06:00 前）时空路由矩阵
  - SQLite ZHB 磁盘缓存旁路剥离 + 熔断静默降级（Graceful Degradation）
  - 测试套件精简规整为 11 个文件，245 项单元测试 100% 通过

V15.2 更新：
  - 子进程 stdout=subprocess.PIPE 接管，修复 GD 上传日志在 Windows 缓冲中被吞
  - 修复 get_canonical_stock_data 中 board 变量 UnboundLocalError（35+2+2 只股票 P0 崩溃）
  - 缓存 valid_if 强化（8 个 F10 + 2 个 dragon_tiger + 12 个 zhb_data）
  - 恢复 V10.0/V12.6 期间简化的 ZHB 交叉验证 + 两次获取一致机制
  - val 1000s 性能优化：L1 缓存 5000→10000 + 22 策略去重循环
  - ths_hot_reason HTTP 失败降级，避免依赖 hot_pool 的 9 个策略 0 命中
  - **子进程注入 PYTHONIOENCODING=utf-8**：避免子进程继承父进程 GBK 控制台编码导致中文乱码 + emoji 抛异常（5 个报告 100% 失败的根因）

V15.1 更新：
  - 全局 ZHB 旁路普及至 6 大报告脚本
  - 0x0010 协议 key 修正（zongguben/liutongguben/gudongrenshu/jinglirun/jingyingxianjinliu）
  - tdxchain.cfg 重写为板块代码→名称映射
  - industry 字段改用 TDX boards
  - 策略并发 100% 线程池 Worker 隔离（解除主事件循环 20 分钟死锁）
  - docs/script_data_dict.md 新建

V14.0 更新：
  - is_workday() Bug 修复（V10.0 ZHB 优先逻辑误判修复）
  - config.py 中 ANTI_POISON_DEVIATION_THRESHOLD 标记废弃
  - 文档全量同步：README/CHANGELOG/tests-README/scripts-README
  - 模块 docstring 版本信息统一到 V14.0
  - 138 个核心测试全过

V13.2 更新：
  - 性能压测脚本 perf_compare.py（内存节省 70%、访问快 21%）
  - field_dict.md 全面更新
  - architecture.md 新增 V12.6/V13.x 章节

V13.1 更新：
  - stock_cache.py 缓存层透明序列化 dataclass
  - data_provider.py 新增 opt-in dataclass 接口
  - tests/test_sc_schema.py 23 个测试

V13.0 更新：
  - 新建 stock_common/sc_schema.py（34 个字段元数据 + 3 个 Enum + NormalizedQuote）

V12.6 更新：
  - data_provider 字段路由简化：REQUIRES_REALTIME_HTTP / ZHB_SUFFICIENT
  - 删除估值/财务字段的腾讯 HTTP fallback（防投毒熔断废弃）
  - get_market_snapshot 走 push2 批量接口

V12.5 更新：
  - get_med_report.py 与 get_lng_report.py 无重复 Runner 类
  - BaseReportRunner 基类 GD 上传辅助方法真正落地
  - stock_cache._l1_clear() 拼写错误修复

V12.4 更新：
  - 抽象出 BaseReportRunner 基类，精简样板代码 (~700 行)

V12.2 更新：
  - SQLite journal_mode 改为 DELETE 解决 WAL 死锁
  - config.py 集中管理网络/限流/防投毒配置
  - 单元测试补齐（cache/strategy/calendar）

V12.1 更新：
  - 静默异常日志化（28 处 except pass → _debug_log）
  - 容错层下沉（sc_fault_tolerance 提供 TokenBucket / CircuitBreaker / RandomUAPool）
  - 死代码清理

V12.0 更新：
  - mootdx 统一 TCP 层（V12.0）；V15.5 起 easy_tdx 1.20.4 适配层首选（健康分+故障转移）

V9.5 更新：
  - 静默异常日志化：tdx_client.py/gd_uploader.py/get_med_report.py 共28处 except Exception 添加 _debug_log
  - aiohttp原生异步迁移：sc_datasource.py 10个HTTP异步函数从 asyncio.to_thread 改为原生 aiohttp
  - ful脚本显示修复：价格走势改为近15日倒序；新闻舆情文案从"近24小时"改为"近期"
  - 修复 get_strategic_announcements_async 中 _load_config 未定义错误

V9.4 更新：
  - VERSION文件单一来源版本号管理
  - mak报告全市场异动扫描并行化（ThreadPoolExecutor, max_workers=3）
  - 死代码清理：删除 trap_detector.py、valuation_methods.py、gd_upload_flow 等
  - 报告格式统一：两融数据、流通股东显示、休市提示文案

V9.3.3 更新：
  - TDX K线假数据防护：健康检查增加K线校验，坏主机自动换IP重连
  - SQLite WAL死锁修复：journal_mode 改为 DELETE，支持多进程并发
  - 代理环境兼容：HTTP请求禁用系统代理，增加异常捕获

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
    """V7.5/15.3: 检查必要依赖是否已安装，缺失时提示用户。

    V15.3 修复: 原代码只检查 5 个包（aiohttp/yaml/google.*×3/requests），
    但 requirements.txt 列出 14 个，缺 mootdx / pytdx / pandas / numpy / easy-tdx /
    aiosqlite / chinese-calendar 等核心依赖时启动不报错，运行到具体报告才
    ImportError 崩溃。补全 9 项检查（requests/yaml/aiohttp/mootdx/pytdx/pandas/
    numpy/chinese_calendar/aiosqlite），Google Drive 套件作为可选。
    """
    missing = []
    # 网络与配置类（必须）
    try:
        import requests  # noqa: F401
    except ImportError:
        missing.append("requests")
    try:
        import yaml  # noqa: F401
    except ImportError:
        missing.append("PyYAML")
    try:
        import aiohttp  # noqa: F401
    except ImportError:
        missing.append("aiohttp")
    try:
        import aiosqlite  # noqa: F401
    except ImportError:
        missing.append("aiosqlite")
    # 数据源核心（必须，TDX 协议 + ZHB 下载）
    try:
        import mootdx  # noqa: F401
    except ImportError:
        missing.append("mootdx")
    try:
        import pytdx  # noqa: F401
    except ImportError:
        missing.append("pytdx")
    # 数据处理（必须，K 线 + 财务表）
    try:
        import pandas  # noqa: F401
    except ImportError:
        missing.append("pandas")
    try:
        import numpy  # noqa: F401
    except ImportError:
        missing.append("numpy")
    # A股日历（必须，is_workday() / is_holiday()）
    try:
        import chinese_calendar  # noqa: F401
    except ImportError:
        missing.append("chinese-calendar")
    # Google Drive 套件（可选，仅 GD 上传需要）
    optional_missing = []
    try:
        import google.auth  # noqa: F401
        import google.oauth2  # noqa: F401
        import googleapiclient  # noqa: F401
    except ImportError:
        optional_missing.append("google-auth google-auth-oauthlib google-api-python-client")

    if missing:
        print("=" * 60, flush=True)
        print("  ❌ 缺少必要依赖，请先安装:", flush=True)
        for pkg in missing:
            print(f"     pip install {pkg}", flush=True)
        if optional_missing:
            print("  ⚠️  可选依赖（仅 GD 上传需要）:", flush=True)
            for pkg in optional_missing:
                print(f"     pip install {pkg}", flush=True)
        print("  💡 一次性安装全部依赖:", flush=True)
        print("     pip install -r requirements.txt", flush=True)
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
        help="V16.1 已下线：全维度报告不再生成，请用 --sht/--med/--lng"
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
        help="最大并发脚本数（默认 1，不推荐超过 3）"
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
    # V15.2: 子进程环境变量 — 注入 PYTHONIOENCODING=utf-8 避免子进程继承父进程 GBK 编码
    # 导致中文乱码 + emoji 抛 GBK UnicodeEncodeError（5 个报告 100% 失败的根因）
    sub_env = os.environ.copy()
    sub_env["PYTHONIOENCODING"] = "utf-8"
    sub_env["PYTHONUTF8"] = "1"
    if stock_codes:
        cmd += stock_codes
    cmd += ["-o", output_dir]
    if no_upload:
        cmd.append("--no-upload")

    codes_str = " ".join(stock_codes) if stock_codes else "(无股票代码)"
    print(f"▶ [{label}] 启动: {script} {codes_str}", flush=True)

    t0 = time.time()
    try:
        # V15.2: stdout=PIPE 显式接管子进程输出，避免 Windows 控制台全缓冲导致 GD 日志被吞
        # V15.2 修复: env=sub_env 注入 PYTHONIOENCODING=utf-8，避免子进程继承父进程 GBK 编码
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=_SCRIPT_DIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=sub_env,
        )
        # 异步实时打印子进程输出（解决 Windows 缓冲问题）
        async def _drain_output() -> None:
            if proc.stdout is None:
                return
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                # 子进程输出继承父进程控制台编码（Windows GBK / Linux UTF-8）
                try:
                    print(line.decode("utf-8", errors="replace").rstrip(), flush=True)
                except UnicodeDecodeError:
                    print(line.decode("gbk", errors="replace").rstrip(), flush=True)

        drain_task = asyncio.create_task(_drain_output())
        try:
            # V15.5.6: 超时分级 — 全市场扫描(val/mak) 30 分钟(需 1000s+)，单股报告 10 分钟
            # V15.4.2: 原统一 600s 会把 val 强制 kill（val 实际运行 1000+ 秒）
            _report_timeout = 1800 if script in ("get_val_report.py", "get_mak_report.py") else 600
            rc = await asyncio.wait_for(proc.wait(), timeout=_report_timeout)
        except asyncio.TimeoutError:
            print(f"⚠ [{label}] {script} 运行超时 {_report_timeout}s，强制 kill", flush=True)
            proc.kill()
            await proc.wait()
            drain_task.cancel()
            return script, -1, time.time() - t0, label
        # 等待输出排空
        try:
            await asyncio.wait_for(drain_task, timeout=5)
        except asyncio.TimeoutError:
            drain_task.cancel()
        dt = time.time() - t0
        status = "完成" if rc == 0 else f"失败({rc})"
        print(f"✔ [{label}] {script} {status} ({dt:.1f}s)", flush=True)
        return script, rc, dt, label
    except KeyboardInterrupt:
        # V15.4.2 修复: Ctrl+C 时强制 kill 子进程，避免变成孤儿进程继续运行
        # Windows 上 asyncio.run() 抛 KeyboardInterrupt 后不会自动 kill 子进程
        if proc and proc.returncode is None:
            try:
                proc.kill()
                await proc.wait()
                if 'drain_task' in locals() and not drain_task.done():
                    drain_task.cancel()
                print(f"⚠ [{label}] {script} 被用户中断，已 kill 子进程", flush=True)
            except Exception as _ke:
                print(f"⚠ [{label}] {script} kill 子进程失败: {_ke}", flush=True)
        else:
            print(f"⚠ [{label}] {script} 被用户中断", flush=True)
        return script, 130, time.time() - t0, label
    except Exception as e:
        # V15.4.2 修复: 其他异常也尝试 kill 子进程
        if proc and proc.returncode is None:
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass
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

    # 构造所有待运行的任务
    # V10.0: 调整顺序为 val → mak → sht → med → lng → ful，
    #        让全市场扫描产生的缓存被后续单股分析脚本复用
    tasks_info = []
    
    # 第一阶段：全市场扫描（产生大量缓存）
    if args.val:
        tasks_info.append(("get_val_report.py", [], output_dir, args.no_upload, "全市场选股"))
    if args.mak:
        tasks_info.append(("get_mak_report.py", [], output_dir, args.no_upload, "异动扫描"))
    
    # 第二阶段：单股分析（复用前面产生的缓存）
    for script, codes, label in [
        ("get_sht_report.py", sht_codes, "短线"),
        ("get_med_report.py", med_codes, "中线"),
        ("get_lng_report.py", lng_codes, "长线"),
    ]:
        if codes:
            tasks_info.append((script, codes, output_dir, args.no_upload, label))

    # V16.1: FUL 已下线（引擎迁移至 sc_technical/sc_risk，能力并入 sht/med/lng）
    if args.ful:
        print("⚠ [ful] V16.1 已下线：全维度报告不再单独生成。技术/风险能力已并入 sht/med/lng。", flush=True)
        print("  → 请改用 --sht/--med/--lng 获取对应持有周期报告", flush=True)

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

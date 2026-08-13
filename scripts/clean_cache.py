#!/usr/bin/env python3
"""clean_cache.py - 缓存管理快捷脚本（封装 stock_cache.py CLI）

本脚本是 `stock_cache.py` 的便捷封装，避免用户记忆多个子命令参数。
所有实际逻辑仍由 `stock_cache.py` 实现，保证单一来源。

用法示例:
  python scripts/clean_cache.py                 # 清理全部缓存（等同于 stock_cache.py clear-all）
  python scripts/clean_cache.py --category <name>   # 按分类清理
  python scripts/clean_cache.py --pattern <code>    # 配合 --category，按代码过滤
  python scripts/clean_cache.py --expired           # 仅清理过期条目
  python scripts/clean_cache.py --stats             # 查看缓存统计
  python scripts/clean_cache.py --dry-run           # 仅显示统计，不实际清理
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# V16.4.1: 强制 UTF-8 输出（下沉到代码自身——任何 agent/机器/直接运行均 UTF-8，
# 不依赖系统代码页/环境变量/Profile；纯标准库，幂等）
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_stock_cache(args: list) -> int:
    """调用 stock_cache.py 的子命令并返回退出码（V17.0 包化: 改 -m core.stock_cache）。"""
    cmd = [sys.executable, "-m", "core.stock_cache"] + args
    return subprocess.call(cmd, cwd=str(PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(
        description="缓存管理快捷脚本（封装 stock_cache.py）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
常用场景:
  python scripts/clean_cache.py                            清理全部
  python scripts/clean_cache.py --category dragon_tiger    按分类清理
  python scripts/clean_cache.py --category financial -p 600519
                                                           按分类+股票代码清理
  python scripts/clean_cache.py --expired                  仅清理过期条目
  python scripts/clean_cache.py --stats                    查看统计
""",
    )
    parser.add_argument("--category", "-c", default="",
                        help="缓存分类名（如 dragon_tiger / hsgt / financial / calendar 等）")
    parser.add_argument("--pattern", "-p", default="",
                        help="股票代码过滤（仅在指定 --category 时生效）")
    parser.add_argument("--expired", action="store_true",
                        help="仅清理已过期的缓存条目")
    parser.add_argument("--stats", action="store_true",
                        help="显示缓存统计信息，不执行清理")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅显示将要执行的命令，不实际执行（仅与 --stats 配合时直接显示统计）")
    args = parser.parse_args()

    # 构造传递给 stock_cache.py 的参数
    if args.stats or args.dry_run:
        action_args = ["stats"]
    elif args.expired:
        action_args = ["clear-expired"]
    elif not args.category and not args.pattern:
        # 无参数 → 清空全部
        action_args = ["clear-all"]
    else:
        if not args.category:
            print("错误：--pattern 必须配合 --category 使用", file=sys.stderr)
            sys.exit(1)
        action_args = ["clear", "--category", args.category]
        if args.pattern:
            action_args += ["--pattern", args.pattern]

    cmd_desc = "python stock_cache.py " + " ".join(action_args)
    if args.dry_run:
        print(f"[dry-run] 将执行: {cmd_desc}")
        return 0

    print(f"→ {cmd_desc}", flush=True)
    return _run_stock_cache(action_args)


if __name__ == "__main__":
    sys.exit(main())

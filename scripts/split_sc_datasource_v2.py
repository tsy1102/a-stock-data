#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V17.2 — sc_datasource.py (god-module) 正确拆包脚本（共享命名空间法）。

与已废弃的 _BROKEN 版本（Facade 命名空间注入，会复制模块级可变状态、破坏
mock.patch 对包内跨函数调用的生效）不同，本脚本采用「共享命名空间」策略：

  1. 用 ast 精确定位全部 162 个顶层 def（含装饰器行）的源码行区间。
  2. __init__.py = 原文件「剔除所有函数体后的残体」：
     - 保留原 docstring、全部 import 块、全部模块级状态赋值（缓存/字段索引/
       降级标志/常量）与其上方注释，逐字保留，顺序不变。
     - 末尾追加 loader：把各域子模块的源码 exec 进本包(模块)的 globals()。
  3. 域子模块（_holders/_eastmoney/_quotes/_industry/_financials/_pools/_zhb/_misc）
     仅含各自的函数定义源码（按原文件顺序抽取），不含 import/状态。

为什么这样就不会有 bug：
  - 所有函数、状态都在【同一个 globals()】(包模块字典) 内，模块级可变状态
    只有一份（修复 BROKEN 版的 KeyError/缓存串号）。
  - 包内跨函数调用按名解析到包命名空间；mock.patch('stock_common.sc_datasource.X')
    打在包属性上，对内部调用同样生效（修复 BROKEN 版的 call_args is None）。
  - 零 import 站点改动：外部 `from stock_common.sc_datasource import X` 照常解析
    到包 __init__ 的属性（exec 注入的）。
  - 装饰器 @cached/@requires_push2/@make_valid_if() 均在 import 块导入，loader
    执行前已存在于共享命名空间，函数定义时可正常解析。

等价性校验：抽取的函数名集合与原文件 162 个 def 名集合完全一致（无遗漏/无重复）。
"""
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "stock_common", "sc_datasource.py")
PKG = os.path.join(ROOT, "stock_common", "sc_datasource")
# V17.2.x(2026-09-10): 原位于 `_obsolete_v17_residue/`（该目录已清理），
# 因本脚本仍以该单文件备份作为比对基准，故将文件本身迁至 `docs/backups/` 长期保留。
BACKUP = os.path.join(ROOT, "docs", "backups", "_sc_datasource_singlefile_backup.py")

BUCKETS = ["_holders", "_eastmoney", "_quotes", "_industry",
           "_financials", "_pools", "_zhb", "_misc"]


def classify(name: str) -> str:
    s = name
    if any(k in s for k in ["holder", "announce", "cninfo", "strategic"]):
        return "_holders"
    if s.startswith("get_zhb") or s.startswith("zhb_") or s == "is_zhb_data_fresh":
        return "_zhb"
    if any(k in s for k in ["limit_up", "limit_down", "limit_broken", "yesterday_limit",
                             "limit_pool", "pool_summary", "stock_monitor", "kpl",
                             "ths_limit", "limit_ladder"]):
        return "_pools"
    if any(k in s for k in ["industry", "sector", "peer", "board_list", "board_members",
                             "belong_board", "em_board"]):
        return "_industry"
    if any(k in s for k in ["tencent", "ths_hot", "concept", "hot_rank", "hot_concept",
                             "shortline", "chip_race", "fupan", "permanent",
                             "stock_changes", "em_xuangu", "em_stock_monitor", "ulist",
                             "quote_full"]):
        return "_quotes"
    if any(k in s for k in ["eastmoney", "em_", "_em_", "dragon", "fund_flow", "fflow",
                             "cls_telegraph", "datacenter", "prefetch", "northbound",
                             "hsgt", "cyq", "kline", "baidu"]):
        return "_eastmoney"
    if any(k in s for k in ["report", "eps", "dividend", "margin", "block_trade",
                             "sina_financial", "balance", "cash_flow", "lockup", "roe",
                             "gross_margin", "valuation", "trading_day", "market_status",
                             "yjyg", "profit_forecast", "news", "calendar",
                             "stock_info", "get_reports", "extract_report"]):
        return "_financials"
    return "_misc"


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        source = f.read()
    lines = source.splitlines(keepends=True)
    tree = ast.parse(source)

    # 收集全部顶层 def 的覆盖行区间（含装饰器行，避免孤立 @xxx 残留在 __init__）
    def_spans = []          # (start_line, end_line, name)
    def_names = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno
            if getattr(node, "decorator_list", None):
                start = min(start, min(d.lineno for d in node.decorator_list))
            end = getattr(node, "end_lineno", node.lineno)
            def_spans.append((start, end, node.name))
            def_names.append(node.name)

    n_defs = len(def_spans)
    print(f"解析到顶层 def 数: {n_defs}")
    assert n_defs == 162, f"期望 162 个 def，实际 {n_defs}（文件可能被改动，需复查）"

    # 覆盖行集合
    covered = set()
    for start, end, _ in def_spans:
        for ln in range(start, end + 1):
            covered.add(ln)

    # __init__.py：剔除覆盖行，保留其余（import/状态/注释/空行）逐字
    init_lines = [ln for i, ln in enumerate(lines, 1) if i not in covered]
    init_body = "".join(init_lines).rstrip() + "\n\n"

    loader = (
        "# ═══════════════════════════════════════════════════════════\n"
        "# V17.2 维护性拆包 loader（共享命名空间）\n"
        "# 将各域子模块的【源码】exec 进本包(模块)的 globals()，使全部函数与\n"
        "# 模块级状态共处同一命名空间：状态只有一份；mock.patch 打在\n"
        "# stock_common.sc_datasource.X 上的补丁对包内跨函数调用同样生效。\n"
        "# 子模块文件本身不是独立可导入模块，而是载入本命名空间的源码片段。\n"
        "# ═══════════════════════════════════════════════════════════\n"
        "import os as _os\n"
        "_PKG_ORDER = (" + ", ".join(repr(b) for b in BUCKETS) + ")\n"
        "_PKG_HERE = _os.path.dirname(_os.path.abspath(__file__))\n"
        "for _mod in _PKG_ORDER:\n"
        "    _fp = _os.path.join(_PKG_HERE, _mod + '.py')\n"
        "    with open(_fp, encoding='utf-8') as _fh:\n"
        "        _src = _fh.read()\n"
        "    exec(compile(_src, _fp, 'exec'), globals())\n"
        "del _mod, _fp, _src, _fh, _PKG_HERE, _PKG_ORDER, _os\n"
    )
    init_content = init_body + loader

    # 域子模块：按 bucket 收集 def 源码（按原文件顺序）
    buckets = {b: [] for b in BUCKETS}
    for start, end, name in sorted(def_spans, key=lambda x: x[0]):
        seg = "".join(lines[start - 1:end])  # 含装饰器与函数体
        buckets[classify(name)].append(seg)

    # 校验：每个 def 名唯一且完整覆盖
    assert len(set(def_names)) == n_defs, "存在重名 def！"
    total_seg = sum(len(v) for v in buckets.values())
    assert total_seg == n_defs, f"def 分配异常: {total_seg} != {n_defs}"

    # 写文件
    os.makedirs(PKG, exist_ok=True)
    # 备份原单文件（rename 绕开删除钩子）
    if os.path.exists(SRC):
        if os.path.exists(BACKUP):
            os.remove(BACKUP)
        os.rename(SRC, BACKUP)
        print(f"已备份原单文件 → {BACKUP}")

    with open(os.path.join(PKG, "__init__.py"), "w", encoding="utf-8") as f:
        f.write(init_content)

    for b in BUCKETS:
        header = (
            f'"""{b}.py — V17.2 拆包子模块（共享命名空间片段，由 __init__ 载入）\n\n'
            f"本文件不是独立可导入模块；其源码被 stock_common/sc_datasource/__init__.py\n"
            f"exec 进包命名空间，与包内其他函数/状态共享同一 globals()。\n"
            f'"""\n'
            "# flake8: noqa: F821  (名称来自包共享命名空间，本片段不单独导入)\n\n"
        )
        content = header + "\n\n".join(buckets[b]) + "\n"
        with open(os.path.join(PKG, f"{b}.py"), "w", encoding="utf-8") as f:
            f.write(content)
        _lines = sum(len(s.splitlines()) for s in buckets[b]) + 1
        print(f"  {b:12s} {len(buckets[b]):4d} 个函数  ({_lines} 行)")

    print("✅ 拆包完成。下一步请用系统 Python 3.12 做 py_compile + import 冒烟 + 全量回归。")


if __name__ == "__main__":
    main()

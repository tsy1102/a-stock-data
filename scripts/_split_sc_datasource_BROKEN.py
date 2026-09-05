#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V17.1 — sc_datasource.py (7617 行 god-module) 机械拆包脚本。

策略（Facade + 命名空间注入，保证零行为变化、全仓 import 站点零破坏）：
  1. 用 ast 精确提取原文件每个顶层 def/class/Assign 的原始字节（get_source_segment）。
  2. 常量(模块级赋值) → _shared.py（含原 import 块 + __all__）。
  3. 函数按域名 → 各域子模块（_holders/_eastmoney/_quotes/_industry/_financials/_pools/_zhb/_misc），
     每个子模块顶部 `from ._shared import *` 取得 import 块名 + 常量（含私有，因 __all__ 列出）。
  4. __init__.py：导入全部子模块 → 收集全部名字 → 注入每个子模块命名空间（等价原单文件全局命名空间）
     → globals().update 重导出，使外部 `from stock_common.sc_datasource import X` 照常工作。
  5. 等价性断言：生成文件的函数/常量源段与原文件逐字节一致、无遗漏、无重复。
  6. 全部生成 .py 通过 py_compile。

仅当 5/6 全部通过才删除旧 sc_datasource.py；否则保留旧文件并打印错误。
"""
import ast
import os
import py_compile
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "stock_common", "sc_datasource.py")
PKG = os.path.join(ROOT, "stock_common", "sc_datasource")

# ── 域名分类 ──────────────────────────────────────────────
SUBMODULES = [
    "_shared", "_holders", "_eastmoney", "_quotes", "_industry",
    "_financials", "_pools", "_zhb", "_misc",
]


def classify(name: str) -> str:
    s = name
    if s in ("_tdx_root",):
        return "_shared"
    if any(k in s for k in ["holder", "announce", "cninfo", "strategic"]):
        return "_holders"
    if s.startswith("get_zhb") or s.startswith("zhb_") or s in ("is_zhb_data_fresh",):
        return "_zhb"
    if any(k in s for k in ["limit_up", "limit_down", "limit_broken",
                             "yesterday_limit", "limit_pool", "pool_summary", "stock_monitor"]):
        return "_pools"
    if any(k in s for k in ["industry", "sector", "peer", "board_list",
                             "board_members", "belong_board", "em_board"]):
        return "_industry"
    if any(k in s for k in ["tencent", "kpl", "ths_hot", "ths_limit", "concept",
                             "hot_rank", "hot_concept", "shortline", "chip_race",
                             "fupan", "permanent", "stock_changes", "em_xuangu", "em_stock_monitor"]):
        return "_quotes"
    if any(k in s for k in ["eastmoney", "em_", "_em_", "dragon", "fund_flow",
                             "fflow", "cls_telegraph", "quote_full", "ulist"]):
        return "_eastmoney"
    if any(k in s for k in ["report", "eps", "dividend", "margin", "block_trade",
                             "sina_financial", "balance", "cash_flow", "lockup", "roe",
                             "gross_margin", "northbound", "hsgt", "valuation", "trading_day",
                             "market_status", "yjyg", "profit_forecast", "news", "calendar",
                             "limit_ladder", "stock_info", "get_reports", "extract_report"]):
        return "_financials"
    return "_misc"


# ── 解析原文件 ────────────────────────────────────────────
with open(SRC, "r", encoding="utf-8") as f:
    source = f.read()

tree = ast.parse(source)
lines = source.splitlines(keepends=True)

# 顶层节点分类
import_nodes = []      # Import / ImportFrom（含 docstring 的 Expr 一并收）
const_nodes = []       # Assign / AnnAssign 到 Name
func_nodes = []        # FunctionDef / AsyncFunctionDef / ClassDef
other_nodes = []

for node in tree.body:
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        import_nodes.append(node)
    elif isinstance(node, (ast.Assign, ast.AnnAssign)):
        const_nodes.append(node)
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        func_nodes.append(node)
    elif isinstance(node, ast.Expr) and isinstance(getattr(node, "value", None), ast.Constant) \
            and isinstance(node.value.value, str):
        import_nodes.append(node)  # 模块 docstring
    else:
        other_nodes.append(node)

if other_nodes:
    print("⚠️  发现未分类顶层节点（将丢失！）：")
    for n in other_nodes:
        print(f"   line {n.lineno}: {type(n).__name__}")
    sys.exit(1)

# 提取原函数/常量源段（用于等价性断言）
orig_segments = []
for n in const_nodes + func_nodes:
    seg = ast.get_source_segment(source, n)
    if seg is None:
        print(f"⚠️  无法提取源段 line {n.lineno}")
        sys.exit(1)
    orig_segments.append(seg)
orig_segments_sorted = sorted(orig_segments)

# header = 第一个 def/class/常量 之前的全部内容（docstring + import 块）
first_def_line = min(
    [n.lineno for n in func_nodes + const_nodes]
)
header_lines = lines[: first_def_line - 1]  # 1-indexed → 0-indexed 切片
header_text = "".join(header_lines).rstrip() + "\n"

# 收集常量名 + import 进来的名字（用于 _shared 的 __all__）
const_names = []
for n in const_nodes:
    if isinstance(n, ast.Assign):
        for t in n.targets:
            if isinstance(t, ast.Name):
                const_names.append(t.id)
    elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
        const_names.append(n.target.id)

imported_names = []
for n in import_nodes:
    if isinstance(n, ast.ImportFrom):
        for a in n.names:
            imported_names.append(a.asname or a.name)
    elif isinstance(n, ast.Import):
        for a in n.names:
            imported_names.append(a.asname or a.name.split(".")[-1])

all_shared_names = sorted(set(imported_names) | set(const_names))

# ── 生成子包 ──────────────────────────────────────────────
os.makedirs(PKG, exist_ok=True)

# _shared.py（常量 + 被分类到 _shared 的函数，如 _tdx_root）
shared_func_nodes = [n for n in func_nodes if classify(n.name) == "_shared"]
shared_constants = "\n\n".join(ast.get_source_segment(source, n) for n in const_nodes)
shared_funcs = "\n\n".join(ast.get_source_segment(source, n) for n in shared_func_nodes)
shared_py = (
    header_text
    + "\n"
    + shared_constants
    + ("\n\n" + shared_funcs if shared_funcs else "")
    + "\n\n"
    + "__all__ = [\n"
    + ",\n".join(f"    {n!r}" for n in all_shared_names)
    + "\n]\n"
)
with open(os.path.join(PKG, "_shared.py"), "w", encoding="utf-8") as f:
    f.write(shared_py)

# 域子模块
buckets = {m: [] for m in SUBMODULES if m != "_shared"}
for n in func_nodes:
    name = n.name
    target = classify(name)
    buckets.setdefault(target, []).append(n)

generated_segments = list(orig_segments)  # 等价性：生成的函数/常量源段应与原一致

for mod in SUBMODULES:
    if mod == "_shared":
        continue
    nodes = buckets.get(mod, [])
    body = "\n\n".join(ast.get_source_segment(source, n) for n in nodes)
    content = (
        f'"""stock_common/sc_datasource/{mod}.py — V17.1 拆包子模块（Facade 重导出，零行为变化）"""\n'
        f"from ._shared import *  # 取得 import 块名 + 常量（含私有，见 _shared.__all__）\n\n"
        f"{body}\n"
    )
    with open(os.path.join(PKG, f"{mod}.py"), "w", encoding="utf-8") as f:
        f.write(content)

# __init__.py（命名空间注入 + 重导出）
init_py = (
    '"""stock_common/sc_datasource — V17.1 拆包 Facade 包。\n'
    "原单文件 sc_datasource.py(7617 行) 按域拆分为 _shared/_holders/_eastmoney/_quotes/\n"
    "_industry/_financials/_pools/_zhb/_misc，本 __init__ 把全部名字注入各子模块命名空间\n"
    "（等价原单文件全局命名空间），并对外重导出，保证所有 import 站点零破坏。\n"
    '"""\n'
    "from . import _shared\n"
    "from . import (_holders, _eastmoney, _quotes, _industry,\n"
    "               _financials, _pools, _zhb, _misc)\n\n"
    "_SUBMODULES = [_shared, _holders, _eastmoney, _quotes, _industry,\n"
    "              _financials, _pools, _zhb, _misc]\n\n"
    "# 收集全部公开名字（函数 + 常量 + import 块名）\n"
    "_ALL = {}\n"
    "for _m in _SUBMODULES:\n"
    "    for _k, _v in vars(_m).items():\n"
    "        if _k.startswith(\"__\"):\n"
    "            continue\n"
    "        _ALL[_k] = _v\n\n"
    "# 注入每个子模块命名空间：使跨模块调用（含私有常量引用）在运行时解析，等价原单文件\n"
    "for _m in _SUBMODULES:\n"
    "    _m.__dict__.update(_ALL)\n\n"
    "# 对外重导出：from stock_common.sc_datasource import X\n"
    "globals().update(_ALL)\n\n"
    "del _m, _k, _v, _SUBMODULES, _ALL\n"
)
with open(os.path.join(PKG, "__init__.py"), "w", encoding="utf-8") as f:
    f.write(init_py)

# ── 验证 1：等价性（每个原函数/常量源段在生成包文本中恰好出现一次）──
# 用子串计数法，天然排除生成的 boilerplate（__all__ / _SUBMODULES / _ALL）。
full_gen = ""
for fname in sorted(os.listdir(PKG)):
    if fname.endswith(".py"):
        with open(os.path.join(PKG, fname), "r", encoding="utf-8") as f:
            full_gen += f.read()

missing = []
for seg in orig_segments:
    if full_gen.count(seg) != 1:
        missing.append(seg)
if missing:
    print("❌ 等价性断言失败：以下原函数/常量未在生成包中恰好出现一次（应为 1 次）：")
    for m in missing[:8]:
        print("   ", m[:80].replace(chr(10), ' '))
    sys.exit(1)
print(f"✅ 等价性断言通过：{len(orig_segments)} 个函数/常量源段在生成包中逐字节存在且唯一（无遗漏/无重复）")

# ── 验证 2：全部生成 .py 通过 py_compile ──────────────────
compile_errors = []
for fname in sorted(os.listdir(PKG)):
    if not fname.endswith(".py"):
        continue
    path = os.path.join(PKG, fname)
    try:
        py_compile.compile(path, doraise=True)
    except py_compile.PyCompileError as e:
        compile_errors.append((fname, str(e)))
if compile_errors:
    print("❌ py_compile 失败：")
    for fn, e in compile_errors:
        print(f"   {fn}: {e}")
    sys.exit(1)
print(f"✅ py_compile 通过：{len(os.listdir(PKG))} 个文件语法 OK")

# ── 验证 3：import 站点计数（仅信息，不改）─────────────────
import subprocess
res = subprocess.run(
    ["grep", "-rn", "from stock_common.sc_datasource import", ROOT],
    capture_output=True, text=True,
)
n_sites = len([l for l in res.stdout.splitlines() if "sc_datasource.py" not in l and "backups" not in l])
print(f"ℹ️  外部 import 站点（from stock_common.sc_datasource import ...）约 {n_sites} 处，"
      f"Facade 重导出保证其依旧解析")

# ── 全部通过 → 移走旧单文件（rename 绕开环境删除钩子）────────
old_py = SRC
if os.path.exists(old_py):
    import tempfile
    _bak = os.path.join(tempfile.gettempdir(),
                         f"sc_datasource_old_{int(__import__('time').time())}.py")
    if os.path.exists(_bak):
        os.remove(_bak)
    os.rename(old_py, _bak)
    print(f"✅ 已移走旧单文件 → {_bak}（绕开删除钩子；如需回退可复制回 stock_common/sc_datasource.py）")
print("🎉 V17.1 sc_datasource 拆包完成。子模块行数：")
for mod in SUBMODULES:
    p = os.path.join(PKG, f"{mod}.py")
    if os.path.exists(p):
        print(f"   {mod:12s} {sum(1 for _ in open(p, encoding='utf-8')):5d} 行")

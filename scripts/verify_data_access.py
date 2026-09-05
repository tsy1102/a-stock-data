#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_data_access.py — 公理 A1「数据访问收口」一致性闸门（离线，零网络）

用法:
    python scripts/verify_data_access.py [--repo DIR] [--strict] [--list-exempt]

理论依据:
    docs/ARCHITECTURE_THEORY.md  公理 A1（数据访问收口）
    docs/DEBT_LEDGER.md          DEBT-001（报告脚本直连裸 TDX）/ DEBT-002（scratch 探针豁免）

目的:
    防止生产脚本绕过统一层（Tier1 get_canonical_stock_data / Tier2 适配器）
    直连原始客户端，导致源选择、限流、缓存、口径治理失效。

检查项:
  HARD FAIL (退出码 1) —— 受检文件中出现任意「裸客户端入口」信号:
      - _get_tdx_client()                     裸 TDX TCP 客户端工厂
      - em_get() / tencent_get() / _quick_request()   裸 HTTP
      - _fuyao_raw()                          裸 fuyao REST
      - requests.get/post/put/request(...)    裸 HTTP 客户端
      - httpx.get/post/put/request(...)       裸 HTTP 客户端
      - 上述符号的 import 语句
  WARN (--strict 时升级为 FAIL):
      - 导入裸网络层 sc_network（应先经 Tier2 适配器封装）

误判防护（重要）:
    检测前用 tokenize 剥离**注释与字符串字面量**——否则文档中引用违规符号的说明性
    注释（如「不再直连 _get_tdx_client()」）会被误报为违规。

豁免区（不计入受检）:
    stock_common/       适配器层，按公理 A1 允许其直连原始客户端
    core/tdx_client.py  适配器本身（内含 _get_tdx_client 定义）
    scratch/            DEBT-002 显式豁免：一次性破解探针，本质需绕开归一化层观测原值
    tests/ docs/ scripts/ .workbuddy-ai/ 等非生产目录

退出码:
    有任何 HARD FAIL              → 1
    仅 WARN（且非 --strict）      → 0
    --strict 且 WARN 非空         → 1
    全过                          → 0

依赖: 纯标准库（re / os / sys / argparse / io / tokenize），Python 3.8+，无需联网。
"""

import argparse
import io
import os
import re
import sys
import tokenize

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)


# ----------------------------------------------------------------------------
# 裸客户端入口信号（HARD FAIL）
#   说明：均为「原始客户端」，不含 tdx_client.tdx_get_* 这类适配器公开函数。
# ----------------------------------------------------------------------------
HARD_SIGNALS = [
    (r"_get_tdx_client\s*\(", "裸 TDX TCP 客户端工厂 _get_tdx_client()"),
    (r"\bem_get\s*\(", "裸 HTTP em_get()（应经 sc_datasource 适配器）"),
    (r"\btencent_get\s*\(", "裸 HTTP tencent_get()（应经 sc_datasource 适配器）"),
    (r"\b_quick_request\s*\(", "裸 HTTP _quick_request()（应经 sc_datasource 适配器）"),
    (r"\b_fuyao_raw\s*\(", "裸 fuyao REST _fuyao_raw()（应经 sc_fuyao 适配器）"),
    (r"\brequests\s*\.\s*(get|post|put|request)\s*\(", "裸 requests 直连 HTTP"),
    (r"\bhttpx\s*\.\s*(get|post|put|request)\s*\(", "裸 httpx 直连 HTTP"),
    (r"^\s*import\s+(requests|httpx)\b", "裸 import requests/httpx（应经 sc_network 封装）"),
    (r"from\s+[\w\.]+\s+import\s+[^\n]*\b_get_tdx_client\b", "导入裸 TDX 客户端工厂"),
    (r"from\s+[\w\.]+\s+import\s+[^\n]*\bem_get\b", "导入裸 HTTP em_get"),
    (r"from\s+[\w\.]+\s+import\s+[^\n]*\btencent_get\b", "导入裸 HTTP tencent_get"),
    (r"from\s+[\w\.]+\s+import\s+[^\n]*\b_fuyao_raw\b", "导入裸 fuyao REST"),
]

# WARN 级信号（--strict 时升级为 FAIL）
WARN_SIGNALS = [
    (r"import\s+stock_common\.sc_network\b", "导入裸网络层 sc_network（应先经 Tier2 适配器封装）"),
]

# sc_network 中的**非数据获取**辅助符号：仅导入这些不算绕过统一层（如日志器）。
# 否则 `from stock_common.sc_network import _fallback_logger` 会被误报。
SC_NETWORK_AUX_ALLOWED = {"_fallback_logger"}

# from stock_common.sc_network import <symbols> —— 按符号名逐个判定
_FROM_SC_NETWORK_RE = re.compile(r"from\s+stock_common\.sc_network\s+import\s+([^\n]+)")
# from stock_common import (..., sc_network, ...) —— 单行场景可覆盖；多行 import 可能漏检，
# 由上方 `import stock_common.sc_network` 与函数级 import 形式兜底。
_FROM_STOCK_COMMON_SC_NETWORK_RE = re.compile(
    r"from\s+stock_common\s+import\s+[^\n]*\bsc_network\b"
)

# 豁免目录（相对 repo root 的 POSIX 前缀）
EXEMPT_DIRS = (
    "stock_common/",     # 适配器层（公理 A1 允许）
    "scratch/",          # DEBT-002 显式豁免
    "tests/",
    "docs/",
    "scripts/",          # 闸门工具自身
    ".workbuddy-ai/",
    ".git/",
    "__pycache__/",
    "venv/",
    ".venv/",
    "cache/",
    "logs/",
    "reports/",
    "snapshots/",
    "credentials/",
    "config/",
)

# 豁免文件（相对 repo root 的 POSIX 路径）
EXEMPT_FILES = {
    "core/tdx_client.py",   # 适配器本身，内含 _get_tdx_client 定义
}


def rel_posix(root, path):
    """返回相对 repo root 的 POSIX 风格路径，便于跨平台前缀匹配。"""
    return os.path.relpath(path, root).replace(os.sep, "/")


def is_exempt(rel):
    if rel in EXEMPT_FILES:
        return True
    for d in EXEMPT_DIRS:
        if rel.startswith(d):
            return True
    return False


def strip_comments_and_strings(src):
    """剔除注释与字符串字面量，返回同长度行列表（保持行号对齐）。

    用 tokenize 精确定位 COMMENT / STRING 区间并替换为空格，
    从而避免「说明性注释里引用了违规符号」被误报。
    tokenize 失败（语法错误）时返回 None，由调用方降级处理。
    """
    try:
        buf = [list(line) for line in src.splitlines()]
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type not in (tokenize.COMMENT, tokenize.STRING):
                continue
            (srow, scol), (erow, ecol) = tok.start, tok.end
            for r in range(srow, erow + 1):
                idx = r - 1
                if idx < 0 or idx >= len(buf):
                    continue
                cs = scol if r == srow else 0
                ce = ecol if r == erow else len(buf[idx])
                for c in range(cs, min(ce, len(buf[idx]))):
                    buf[idx][c] = " "
        return ["".join(line) for line in buf]
    except Exception:
        return None


def iter_python_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        # 原地剪枝隐藏目录与已知大目录，避免无谓遍历
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith(".")
            and d not in ("__pycache__", "venv", ".venv", "node_modules")
        ]
        for fn in filenames:
            if fn.endswith(".py"):
                yield os.path.join(dirpath, fn)


def scan(root):
    hard, warn = [], []
    scanned = 0
    degraded = []

    for path in iter_python_files(root):
        rel = rel_posix(root, path)
        if is_exempt(rel):
            continue
        scanned += 1
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                src = fh.read()
        except Exception as exc:  # pragma: no cover
            warn.append((rel, 0, "读取失败：%s" % exc, "读取失败"))
            continue

        lines = strip_comments_and_strings(src)
        if lines is None:
            # tokenize 失败（文件有语法错误）→ 降级为原始行扫描，可能含误报
            lines = src.splitlines()
            degraded.append(rel)

        for lineno, line in enumerate(lines, start=1):
            for pattern, desc in HARD_SIGNALS:
                if re.search(pattern, line):
                    hard.append((rel, lineno, desc, line.strip()[:90]))
            for pattern, desc in WARN_SIGNALS:
                if re.search(pattern, line):
                    warn.append((rel, lineno, desc, line.strip()[:90]))

            # sc_network 导入按**符号名**判定：仅导入辅助符号（日志器等）不算绕过统一层
            m = _FROM_SC_NETWORK_RE.search(line)
            if m:
                syms = [s.strip().split(" as ")[0].strip() for s in m.group(1).split(",")]
                bad = [s for s in syms if s and s not in SC_NETWORK_AUX_ALLOWED]
                if bad:
                    warn.append((
                        rel, lineno,
                        "导入裸网络层 sc_network 的数据获取符号：%s（应先经 Tier2 适配器封装）" % ", ".join(bad),
                        line.strip()[:90],
                    ))
            elif _FROM_STOCK_COMMON_SC_NETWORK_RE.search(line):
                warn.append((
                    rel, lineno,
                    "导入裸网络层 sc_network（应先经 Tier2 适配器封装）",
                    line.strip()[:90],
                ))

    return hard, warn, scanned, degraded


def main():
    ap = argparse.ArgumentParser(description="公理 A1 数据访问收口闸门")
    ap.add_argument("--repo", default=REPO_ROOT, help="仓库根目录（默认：脚本上级目录）")
    ap.add_argument("--strict", action="store_true", help="WARN 也视为失败")
    ap.add_argument("--list-exempt", action="store_true", help="仅打印豁免区配置后退出")
    args = ap.parse_args()

    if args.list_exempt:
        print("豁免目录：")
        for d in EXEMPT_DIRS:
            print("  - %s" % d)
        print("豁免文件：")
        for f in sorted(EXEMPT_FILES):
            print("  - %s" % f)
        return 0

    root = os.path.abspath(args.repo)
    hard, warn, scanned, degraded = scan(root)

    print("=" * 72)
    print("verify_data_access — 公理 A1 数据访问收口闸门")
    print("理论依据: docs/ARCHITECTURE_THEORY.md A1 | 债务台账: docs/DEBT_LEDGER.md")
    print("仓库: %s" % root)
    print("受检文件数: %d（已豁免 stock_common/ 适配器层、core/tdx_client.py、scratch/ 探针等）"
          % scanned)
    print("=" * 72)

    if degraded:
        print("\n[降级提示] 以下文件 tokenize 失败（可能有语法错误），已按原始文本扫描，结果可能含误报：")
        for rel in degraded:
            print("  - %s" % rel)

    if hard:
        print("\n[HARD FAIL] 生产脚本直连原始客户端（违反公理 A1），共 %d 处：" % len(hard))
        for rel, lineno, desc, snippet in hard:
            print("  - %s:%d  %s" % (rel, lineno, desc))
            if snippet:
                print("      > %s" % snippet)
        print("\n修法：改走统一层 —— Tier1 get_canonical_stock_data() 或 Tier2 适配器公开函数")
        print("      （如 tdx_client.tdx_get_finance_info / sc_datasource.get_* / sc_fuyao.get_fuyao_*）")
        print("      若确属有意偏离，必须在 docs/DEBT_LEDGER.md 登记（公理 A8 禁止静默迁就）。")
    else:
        print("\n[OK] HARD: 无生产脚本直连原始客户端。")

    if warn:
        tag = "[FAIL]" if args.strict else "[WARN]"
        print("\n%s 裸网络层引用，共 %d 处：" % (tag, len(warn)))
        for rel, lineno, desc, snippet in warn:
            print("  - %s:%d  %s" % (rel, lineno, desc))
            if snippet:
                print("      > %s" % snippet)
    else:
        print("[OK] WARN: 无裸网络层引用。")

    print("\n" + "-" * 72)
    print("HARD FAIL: %d | WARN: %d" % (len(hard), len(warn)))
    print("-" * 72)

    if hard:
        return 1
    if warn and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

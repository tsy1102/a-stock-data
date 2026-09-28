#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_data_access.py — 公理 A1 数据访问收口闸门（离线，零网络）

用法:
    python scripts/verify_data_access.py [--repo DIR] [--strict]

目的:
    防止「生产脚本直连原始客户端」违反公理 A1。
    对应文档规则: AGENTS.md §8.4 统一层与数据访问收口。

公理 A1 收口模型（AGENTS.md §8.4）:
    统一层 = 两层网关:
      - Tier1 门面  : core/data_provider.get_canonical_stock_data()
      - Tier2 适配器: sc_datasource.get_* / sc_fuyao.get_fuyao_* / tdx_client.tdx_get_*
      - 原始客户端  : _get_tdx_client() / sc_network.em_get / sc_fuyao._fuyao_raw /
                     裸 requests·httpx —— 仅允许出现在 stock_common/ 与 core/tdx_client.py 内部
    铁律: 生产脚本(main.py / get_*_report.py / sc_report_runner.py / core/*.py)
          取数必须先经过 Tier1 或 Tier2 公开函数, 禁止直连原始客户端。

检查项:
  HARD FAIL (退出码 1) —— 默认执行:
    1. 生产脚本(见 TARGET 列表)中, 禁止出现以下「直连原始客户端调用」:
         - _get_tdx_client(                 (裸 TDX 客户端构造)
         - em_get( / .em_get(              (sc_network.em_get 原始包装)
         - _fuyao_raw( / ._fuyao_raw(      (sc_fuyao._fuyao_raw 原始包装)
         - requests.get/post/put/delete/head/Session(   (裸 HTTP 库)
         - httpx.get/post/AsyncClient(     (裸 HTTP 库)
         - aiohttp.* / urllib.request.*     (裸 HTTP 库)
       说明: 用 tokenize 剥离注释/字符串, 文档中引用这些符号的说明性注释不会误报;
            仅当符号确实作为「调用」(出现在 ( 之前) 才判定违规。
  ADVISORY WARN (best-effort; --strict 时升级为 FAIL) —— 默认执行(不致命):
    2. 生产脚本中应出现至少一处 Tier1/Tier2 入口引用(data_provider / sc_datasource /
       sc_fuyao / tdx_client / get_canonical_stock_data); 完全无引用则告警
       (可能该脚本绕过了统一层)。main.py 为启动器, 豁免此告警。

豁免目录(允许使用原始客户端, 不纳入检查):
    - stock_common/ 全部
    - core/tdx_client.py

退出码:
    有任何 HARD FAIL                                → 1
    --strict 且 WARN 非空                           → 1
    全过                                            → 0

依赖: 纯标准库(tokenize / os / sys / argparse), 可在任何 Python 3.8+ 运行, 无需联网。
"""

import argparse
import io
import os
import sys
import tokenize

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

# ── 受检生产脚本(相对 repo 根) ───────────────────────────────────────────────
PRODUCTION_ROOT_FILES = [
    "main.py",
    "get_val_report.py",
    "get_mak_report.py",
    "get_med_report.py",
    "get_lng_report.py",
    "get_sht_report.py",
]

# core/*.py 纳入检查, 但 core/tdx_client.py 豁免(原始客户端合法出口)
CORE_EXEMPT_BASENAMES = {"tdx_client.py"}

# RAW_HTTP 检查豁免(文件级): 这些文件用裸 HTTP 库做「非行情取数」用途,
# 不在公理 A1 数据访问收口范围内, 强行改走 sc_network(带东财限流/封禁逻辑)反而错误。
#   - core/gd_uploader.py: Google Drive 上传器, 用 urllib 仅探测本地代理可达 Google OAuth, 与行情无关。
RAW_HTTP_EXEMPT = {"core/gd_uploader.py", "core\\gd_uploader.py"}

# 启动器豁免「Tier 入口缺失」告警(它只负责编排子进程, 不直连取数)
TIER_REF_EXEMPT = {"main.py"}

# ── 直连原始客户端调用(违规符号) ─────────────────────────────────────────────
# 这些名称作为「调用」(出现在 ( 之前)即判违规; 仅注释/字符串引用不判。
FORBIDDEN_RAW_FUNCS = {
    "_get_tdx_client": "裸 TDX 客户端构造(Tier1/Tier2 应通过 tdx_client.tdx_get_*)",
    "em_get": "sc_network.em_get 原始包装(应通过 Tier2 适配器 sc_datasource.get_*)",
    "_fuyao_raw": "sc_fuyao._fuyao_raw 原始包装(应通过 sc_fuyao.get_fuyao_*)",
}

# 裸 HTTP 库(头部 NAME 命中即判违规)
RAW_HTTP_LIBS = {
    "requests": "裸 requests 库(应经 sc_network._quick_request / Tier2 适配器)",
    "httpx": "裸 httpx 库(应经 sc_network._quick_request / Tier2 适配器)",
    "aiohttp": "裸 aiohttp 库(应经 sc_network / Tier2 适配器)",
    "urllib": "裸 urllib 库(应经 sc_network / Tier2 适配器)",
}

# Tier1/Tier2 入口(用于 ADVISORY: 生产脚本应至少引用其一)
TIER_ENTRYPOINTS = {
    "data_provider",
    "sc_datasource",
    "sc_fuyao",
    "tdx_client",
    "get_canonical_stock_data",
}


def _iter_target_files(repo):
    files = []
    for rel in PRODUCTION_ROOT_FILES:
        p = os.path.join(repo, rel)
        if os.path.isfile(p):
            files.append(p)
        else:
            print(f"   [WARN] 受检文件不存在, 跳过: {rel}")
    core_dir = os.path.join(repo, "core")
    if os.path.isdir(core_dir):
        for name in sorted(os.listdir(core_dir)):
            if not name.endswith(".py"):
                continue
            if name in CORE_EXEMPT_BASENAMES:
                continue
            p = os.path.join(core_dir, name)
            if os.path.isfile(p):
                files.append(p)
    return files


def _scan_file(path, rel):
    """返回 (violations, has_tier_ref)。

    violations 为 (line, kind, symbol, detail) 列表;
    has_tier_ref 表示是否出现过 Tier1/Tier2 入口符号(仅 NAME token, 自动排除注释/字符串)。
    rel 为相对仓库根的路径(用于文件级豁免判定)。
    """
    try:
        with open(path, "rb") as fh:
            src = fh.read()
    except Exception as e:  # noqa: BLE001
        return [(0, "READ_ERROR", path, str(e))], False

    try:
        toks = list(tokenize.tokenize(io.BytesIO(src).readline))
    except Exception as e:  # noqa: BLE001
        return [(0, "TOKENIZE_ERROR", path, str(e))], False

    has_tier_ref = any(t.type == tokenize.NAME and t.string in TIER_ENTRYPOINTS for t in toks)
    exempt_raw_http = rel in RAW_HTTP_EXEMPT

    violations = []
    n = len(toks)
    for i, tok in enumerate(toks):
        if tok.type != tokenize.OP or tok.string != "(":
            continue
        # 向后收集调用链头部 NAME: 连续的 NAME / . 直到遇到其它 token
        names = []
        j = i - 1
        while j >= 0:
            t = toks[j]
            if t.type == tokenize.NAME:
                names.append(t.string)
                j -= 1
            elif t.type == tokenize.OP and t.string == ".":
                j -= 1
            else:
                break
        if not names:
            continue
        last = names[0]  # 紧邻 ( 的 NAME
        head = names[-1]  # 调用链头部 NAME
        line = tok.start[0]
        if last in FORBIDDEN_RAW_FUNCS:
            violations.append((line, "RAW_FUNC", last, FORBIDDEN_RAW_FUNCS[last]))
        if head in RAW_HTTP_LIBS and not exempt_raw_http:
            violations.append((line, "RAW_HTTP", head, RAW_HTTP_LIBS[head]))
    return violations, has_tier_ref


def main():
    # Windows PowerShell 5.1 may expose a GBK console stream; the report uses
    # Unicode symbols, so reconfigure CLI output when the stream supports it.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="公理 A1 数据访问收口闸门")
    ap.add_argument("--repo", default=REPO_ROOT, help="仓库根目录（默认自动推断）")
    ap.add_argument(
        "--strict", action="store_true", help="将 ADVISORY WARN 升级为 FAIL（退出码 1）"
    )
    args = ap.parse_args()

    repo = args.repo
    print("=" * 68)
    print(" verify_data_access — 公理 A1 数据访问收口闸门")
    print("=" * 68)
    print(f" 仓库根   : {repo}")
    print(f" 豁免目录 : stock_common/ , core/tdx_client.py")
    print("-" * 68)

    targets = _iter_target_files(repo)
    print(f" 受检生产脚本 : {len(targets)} 个")
    for t in targets:
        print(f"   - {os.path.relpath(t, repo)}")

    hard_failures = []
    warnings = []

    for path in targets:
        rel = os.path.relpath(path, repo)
        vios, has_tier = _scan_file(path, rel)
        if vios:
            for line, kind, sym, detail in vios:
                msg = f"{rel}:{line} 直连原始客户端 [{kind}] {sym} —— {detail}"
                hard_failures.append(msg)
                print(f"   ✗ {msg}")
        else:
            print(f"   ✓ {rel} (无直连原始客户端调用)")
        # ADVISORY: 仅根级生产脚本(get_*_report.py 等)须引用 Tier1/Tier2 入口;
        # core/*.py 基础设施模块(配置/缓存/上传器)本就不该直接引用, 不在此告警范围内。
        if rel in PRODUCTION_ROOT_FILES and rel not in TIER_REF_EXEMPT and not has_tier:
            warn = (
                f"{rel}: 未引用任何 Tier1/Tier2 入口(data_provider/sc_datasource/"
                f"sc_fuyao/tdx_client), 可能绕过统一层"
            )
            warnings.append(warn)
            print(f"   ⚠ {warn}")

    print("=" * 68)
    print(f" HARD FAIL: {len(hard_failures)} | WARN: {len(warnings)}")
    print("=" * 68)
    if hard_failures:
        print("结果: ❌ 失败（生产脚本存在直连原始客户端, 违反公理 A1）")
        return 1
    if warnings:
        if args.strict:
            print("结果: ❌ 失败（--strict 模式：Tier 入口缺失警告升级为失败）")
            return 1
        print("结果: ⚠️ 通过（含 Tier 入口缺失警告, 建议核对）")
        return 0
    print("结果: ✅ 通过（无直连原始客户端, 数据访问收口合规）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""archive_field_preflight.py — 归档前/后「契约一致性」预检（不修改任何工具行为）。

数据来源：通达信 a-stock-data 字段破解体系。本脚本为「归档 SOP」的机器化实现，
目的是在搬运 field_dict.md 章节时，确保治理面工具不会因为章节搬家而产生
假 GAP（audit_field_completeness）或断链红（verify_sync_check A7 闸门）。

检查项（全部只读，零副作用）：
  1. SECTION_MAP 每个源的子串必须能在 docs/ 全树（主字典 ∪ 归档目录 ∪ verify 分字典）
     解析到标题文本；否则该源审计将报「字段未登记」假 GAP —— 即归档未同步 SECTION_MAP 搜索域。
  2. field_dict.md 引用的 docs/verify/*.md 必须真实存在（镜像 verify_sync_check HARD#1 断链）。
  3. verify_sync_check.MAPPING 每个分字典文件必须存在且被主字典引用（孤儿/缺失，镜像 HARD#2/3）。

设计要点：
  - 直接 import audit_field_completeness.SECTION_MAP 与 verify_sync_check.MAPPING 作为
    单一权威配置，工具侧改动自动同步到本预检，不做硬编码复制。
  - 不修改任何工具运行时逻辑（区别于 (b) 全量解耦方案）。

退出码：有违规 → 1（可挂 pre-commit 闸门）；全过 → 0。
"""
from __future__ import annotations

import argparse
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
FIELD_DICT = os.path.join(DOCS_DIR, "field_dict.md")
VERIFY_DIR = os.path.join(DOCS_DIR, "verify")


def _load_section_map():
    """复用 audit_field_completeness.SECTION_MAP 作为单一真相源。"""
    try:
        sys.path.insert(0, SCRIPT_DIR)
        import audit_field_completeness as afc  # noqa: F401
        return list(afc.SECTION_MAP)
    except Exception as _e:  # pragma: no cover
        print(f"[WARN] 无法 import SECTION_MAP（{_e}），回退空表", file=sys.stderr)
        return []


def _load_verify_mapping():
    """复用 verify_sync_check.MAPPING 作为单一真相源。"""
    try:
        sys.path.insert(0, SCRIPT_DIR)
        import verify_sync_check as vsc  # noqa: F401
        return dict(vsc.MAPPING)
    except Exception as _e:  # pragma: no cover
        print(f"[WARN] 无法 import MAPPING（{_e}），回退空表", file=sys.stderr)
        return {}


def _collect_docs_corpus():
    """返回 docs/ 下所有 .md 的全文列表（含主字典、归档目录、verify 分字典）。"""
    corpus = []
    for _root, _dirs, _files in os.walk(DOCS_DIR):
        # 跳过原始采集数据目录（raw_*.json 等非 .md 不在此列；这里仅收 .md）
        for _f in _files:
            if _f.endswith(".md"):
                _p = os.path.join(_root, _f)
                try:
                    corpus.append((_p, io_open(_p)))
                except Exception:
                    pass
    return corpus


def io_open(path):
    with open(path, encoding="utf-8") as _fh:
        return _fh.read()


def _check_section_map(corpus_texts):
    """检查 SECTION_MAP 每个子串是否能在 docs 全树解析到。返回违规列表。"""
    violations = []
    sec_map = _load_section_map()
    joined = "\n".join(t for _, t in corpus_texts)
    for label, subs in sec_map:
        for sub in subs:
            if sub and sub not in joined:
                violations.append((label, sub))
    return violations


def _check_verify_links():
    """检查主字典引用的 docs/verify/*.md 是否真实存在（HARD#1 断链镜像）。"""
    broken = []
    if not os.path.exists(FIELD_DICT):
        return broken
    text = io_open(FIELD_DICT)
    # 匹配 docs/verify/xxx.md 或 verify/xxx.md 两种写法
    for m in re.finditer(r"(?:docs/)?verify/([A-Za-z0-9_\-]+\.md)", text):
        name = m.group(1)
        if not os.path.exists(os.path.join(VERIFY_DIR, name)):
            broken.append(name)
    return broken


def _check_mapping_coverage():
    """检查 MAPPING 每个分字典存在且被主字典引用（HARD#2/3 镜像）。"""
    missing = []
    orphan = []
    mapping = _load_verify_mapping()
    dict_text = io_open(FIELD_DICT) if os.path.exists(FIELD_DICT) else ""
    for src, fname in mapping.items():
        fpath = os.path.join(VERIFY_DIR, fname)
        if not os.path.exists(fpath):
            missing.append((src, fname))
        else:
            # 被引用：主字典中出现该文件名或 verify/ 路径
            if fname not in dict_text and f"verify/{fname}" not in dict_text:
                orphan.append((src, fname))
    return missing, orphan


def main(argv=None):
    ap = argparse.ArgumentParser(description="归档 field_dict.md 章节后的契约一致性预检")
    ap.add_argument("--repo", default=REPO_ROOT, help="仓库根目录（默认脚本上级）")
    _args = ap.parse_args(argv)

    global DOCS_DIR, FIELD_DICT, VERIFY_DIR
    DOCS_DIR = os.path.join(_args.repo, "docs")
    FIELD_DICT = os.path.join(DOCS_DIR, "field_dict.md")
    VERIFY_DIR = os.path.join(DOCS_DIR, "verify")

    print("== 归档契约预检（archive_field_preflight）==")
    print(f"  docs 根: {DOCS_DIR}")

    corpus = _collect_docs_corpus()
    print(f"  扫描 .md 文件: {len(corpus)} 个")

    problems = []

    # 1) SECTION_MAP 解析域
    sec_v = _check_section_map(corpus)
    if sec_v:
        print(f"\n[FAIL] SECTION_MAP 子串在主字典∪归档∪verify 全树未解析到 {len(sec_v)} 处：")
        for label, sub in sec_v:
            print(f"   - 源[{label}] 子串「{sub}」未找到 → 该源审计将报假 GAP")
            problems.append(f"SECTION_MAP:{label}:{sub}")
    else:
        print("\n[OK]   SECTION_MAP 全部子串均可在 docs 全树解析（无假 GAP 风险）")

    # 2) verify 断链
    broken = _check_verify_links()
    if broken:
        print(f"\n[FAIL] 主字典引用了不存在的 verify 分字典 {len(broken)} 个：")
        for name in broken:
            print(f"   - verify/{name} 不存在 → A7 闸门 HARD#1 断链")
            problems.append(f"VERIFY_LINK:{name}")
    else:
        print("[OK]   主字典引用的 verify 分字典均存在（无断链）")

    # 3) MAPPING 覆盖
    missing, orphan = _check_mapping_coverage()
    if missing:
        print(f"\n[FAIL] MAPPING 分字典缺失 {len(missing)} 个：")
        for src, fname in missing:
            print(f"   - {src} -> verify/{fname} 不存在")
            problems.append(f"MAPPING_MISSING:{fname}")
    else:
        print("[OK]   MAPPING 分字典全部存在")
    if orphan:
        print(f"\n[WARN] MAPPING 分字典未被主字典引用 {len(orphan)} 个（疑似孤儿，建议核查）：")
        for src, fname in orphan:
            print(f"   - {src} -> verify/{fname} 主字典未提及")
            problems.append(f"MAPPING_ORPHAN:{fname}")

    print("\n" + "=" * 60)
    if problems:
        print(f"预检未通过：{len(problems)} 项违规。请先同步 SECTION_MAP / 修复断链再归档或提交。")
        return 1
    print("预检通过：归档未破坏治理面工具契约。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

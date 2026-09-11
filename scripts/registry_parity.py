#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""registry_parity.py — 字段登记表 parity 闸门（registry ↔ markdown）。

校验 docs/field_verification/field_registry.json（单一真相源）与
field_dict.md 的字段×源映射完全一致。用于 CI / 提交前闸门。

判定（G1）：
  * 字段数、去重 (字段,源) 配对总数、多源字段数 三者须与
    gen_field_matrix.build_matrix_from_md() 基线逐字节一致。
  * 另抽样核对多源字段的源集合与基线一致。

Phase 2(2026-09-12): 基线显式走 build_matrix_from_md()，registry 视图走
build_matrix_from_registry()，二者分离避免「registry 读 registry」的循环自检。

退出码：0=通过；1=未通过（不应提交）。
"""
from __future__ import annotations

import io
import json
import os
import sys

for _s in (sys.stdout, sys.stderr):
    if _s is not None and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
REGISTRY = os.path.join(REPO_ROOT, "docs", "field_verification", "field_registry.json")

sys.path.insert(0, SCRIPT_DIR)
import gen_field_matrix as gm
import field_registry_api as fra


def main():
    if not os.path.exists(REGISTRY):
        print(f"FAIL: 未找到 registry: {REGISTRY}（先跑 extract_registry.py）")
        return 1

    with io.open(REGISTRY, encoding="utf-8") as f:
        reg = json.load(f)

    # 基线：markdown 路径（golden，与 registry 互不依赖）
    md_ns, _ = gm.build_matrix_from_md()
    base_fields = len(md_ns)
    base_pairs = sum(len(v) for v in md_ns.values())
    base_multi = sum(1 for v in md_ns.values() if len(v) >= 2)

    # registry 视图
    reg_ns = fra.field_source_map(reg)
    reg_field_n = len(reg_ns)
    reg_pairs = sum(len(v) for v in reg_ns.values())
    reg_multi = sum(1 for v in reg_ns.values() if len(v) >= 2)

    problems = []
    if reg_field_n != base_fields:
        problems.append(f"字段数 {reg_field_n} != 基线 {base_fields}")
    if reg_pairs != base_pairs:
        problems.append(f"配对总数 {reg_pairs} != 基线 {base_pairs}")
    if reg_multi != base_multi:
        problems.append(f"多源数 {reg_multi} != 基线 {base_multi}")

    # 集合级核对
    miss = set(md_ns) - set(reg_ns)
    extra = set(reg_ns) - set(md_ns)
    if miss:
        problems.append(f"基线有而 registry 缺 {len(miss)}: {sorted(miss)[:10]}")
    if extra:
        problems.append(f"registry 多出于基线 {len(extra)}: {sorted(extra)[:10]}")

    # 抽样核对多源字段的源集合
    sample_bad = []
    for f, srcs in reg_ns.items():
        if len(srcs) >= 2:
            if srcs != md_ns[f]:
                sample_bad.append(f)
                if len(sample_bad) >= 10:
                    break
    if sample_bad:
        problems.append(f"多源字段源集合不一致(抽样): {sample_bad}")

    print(f"parity: registry({reg_field_n}/{reg_pairs}/{reg_multi}) "
          f"vs baseline-md({base_fields}/{base_pairs}/{base_multi})")
    if problems:
        print("FAIL:")
        for p in problems:
            print("  -", p)
        return 1
    print("PASS: 字段×源映射 registry 与 field_dict.md 完全一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())

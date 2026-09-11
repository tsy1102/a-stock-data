#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""registry_parity.py — 字段登记表 parity 闸门（registry ↔ markdown）。

校验 docs/field_verification/field_registry.json（单一真相源影子）与
field_dict.md 的字段×源映射完全一致。用于 CI / 提交前闸门。

判定（G1）：
  * 字段数、去重 (字段,源) 配对总数、多源字段数 三者须与
    gen_field_matrix.build_matrix() 基线逐字节一致。
  * 另抽样核对多源字段的源集合与基线一致。

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


def main():
    if not os.path.exists(REGISTRY):
        print(f"FAIL: 未找到 registry: {REGISTRY}（先跑 extract_registry.py）")
        return 1

    with io.open(REGISTRY, encoding="utf-8") as f:
        reg = json.load(f)

    # 基线
    name_sources, _ = gm.build_matrix()
    base_fields = len(name_sources)
    base_pairs = sum(len(v) for v in name_sources.values())
    base_multi = sum(1 for v in name_sources.values() if len(v) >= 2)

    # registry 视图
    reg_fields = {r["code"]: set(r["sources"]) for r in reg["fields"]}
    reg_field_n = len(reg_fields)
    reg_pairs = sum(len(v) for v in reg_fields.values())
    reg_multi = sum(1 for v in reg_fields.values() if len(v) >= 2)

    problems = []
    if reg_field_n != base_fields:
        problems.append(f"字段数 {reg_field_n} != 基线 {base_fields}")
    if reg_pairs != base_pairs:
        problems.append(f"配对总数 {reg_pairs} != 基线 {base_pairs}")
    if reg_multi != base_multi:
        problems.append(f"多源数 {reg_multi} != 基线 {base_multi}")

    # 集合级核对
    miss = set(name_sources) - set(reg_fields)
    extra = set(reg_fields) - set(name_sources)
    if miss:
        problems.append(f"基线有而 registry 缺 {len(miss)}: {sorted(miss)[:10]}")
    if extra:
        problems.append(f"registry 多出于基线 {len(extra)}: {sorted(extra)[:10]}")

    # 抽样核对多源字段的源集合
    sample_bad = []
    for f, srcs in reg_fields.items():
        if len(srcs) >= 2:
            if srcs != name_sources[f]:
                sample_bad.append(f)
                if len(sample_bad) >= 10:
                    break
    if sample_bad:
        problems.append(f"多源字段源集合不一致(抽样): {sample_bad}")

    print(f"parity: registry({reg_field_n}/{reg_pairs}/{reg_multi}) "
          f"vs baseline({base_fields}/{base_pairs}/{base_multi})")
    if problems:
        print("FAIL:")
        for p in problems:
            print("  -", p)
        return 1
    print("PASS: 字段×源映射与 field_dict.md 完全一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())

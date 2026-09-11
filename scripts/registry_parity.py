"""registry_parity.py — 字段登记表 parity 闸门（registry ↔ markdown 原生 token）。

校验 docs/field_verification/field_registry.json（单一真相源影子）与
field_dict.md 经 audit_field_completeness.registered_field_sets() 抽取出的
「原生 token × 源」集合完全一致。用于 CI / 提交前闸门。

判定（G1）：
  * 字段数、去重 (token,源) 配对总数、多源 token 数 三者须与
    audit_field_completeness.registered_field_sets() 基线逐字节一致。
  * 另抽样核对多源 token 的源集合与基线一致。

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
import field_registry_api as fra
import audit_field_completeness as afc
import gen_field_matrix as gm


def main():
    if not os.path.exists(REGISTRY):
        print(f"FAIL: 未找到 registry: {REGISTRY}（先跑 extract_registry.py）")
        return 1

    with io.open(REGISTRY, encoding="utf-8") as f:
        reg = json.load(f)

    # 基线（原生 token）：audit_field_completeness.registered_field_sets
    base_reg = afc.registered_field_sets()
    base_field_sources = {}
    for src, toks in base_reg.items():
        for t in toks:
            base_field_sources.setdefault(t, set()).add(src)
    base_fields = len(base_field_sources)
    base_records = sum(len(v) for v in base_reg.values())
    base_multi = sum(1 for s in base_field_sources.values() if len(s) >= 2)

    # registry 视图（原生 token）：code -> set(sources)
    reg_field_sources = {}
    for r in reg["fields"]:
        reg_field_sources.setdefault(r["code"], set()).update(r["sources"])
    reg_fields = len(reg_field_sources)
    reg_records = sum(len(v) for v in reg_field_sources.values())
    reg_multi = sum(1 for v in reg_field_sources.values() if len(v) >= 2)

    problems = []
    if reg_fields != base_fields:
        problems.append(f"字段数 {reg_fields} != 基线 {base_fields}")
    if reg_records != base_records:
        problems.append(f"配对总数 {reg_records} != 基线 {base_records}")
    if reg_multi != base_multi:
        problems.append(f"多源数 {reg_multi} != 基线 {base_multi}")

    # 集合级核对
    miss = set(base_field_sources) - set(reg_field_sources)
    extra = set(reg_field_sources) - set(base_field_sources)
    if miss:
        problems.append(f"基线有而 registry 缺 {len(miss)}: {sorted(miss)[:10]}")
    if extra:
        problems.append(f"registry 多出于基线 {len(extra)}: {sorted(extra)[:10]}")

    # 抽样核对多源 token 的源集合
    sample_bad = []
    for t, srcs in reg_field_sources.items():
        if len(srcs) >= 2:
            if srcs != base_field_sources.get(t):
                sample_bad.append(t)
                if len(sample_bad) >= 10:
                    break
    if sample_bad:
        problems.append(f"多源 token 源集合不一致(抽样): {sample_bad}")

    print(f"parity[native]: registry({reg_fields}/{reg_records}/{reg_multi}) "
          f"vs baseline({base_fields}/{base_records}/{base_multi})")
    if problems:
        print("  native FAIL:")
        for p in problems:
            print("   -", p)
    else:
        print("  native PASS: 原生 token × 源映射与 field_dict.md 完全一致")

    # ---- field_matrix 投影 parity（§零·B 生成一致性，G3 闸门）----
    fm_problems = check_field_matrix(reg)
    print(f"parity[field_matrix]: {'PASS' if not fm_problems else 'FAIL'}")
    for p in fm_problems:
        print("   -", p)

    all_problems = problems + fm_problems
    if all_problems:
        return 1
    print("PASS: registry 双重 parity 全部通过（原生 token + §零·B 投影）")
    return 0


def check_field_matrix(reg: dict) -> list:
    """§零·B 投影 parity：registry.field_matrix 须与 gen_field_matrix.build_matrix_from_md 同构。

    这是 G3 闸门的本质——§零·B 块由 field_matrix 渲染，必须与当前 field_dict.md 逐字节一致。
    """
    if "field_matrix" not in reg:
        return ["registry 缺少 field_matrix 投影（请重跑 extract_registry.py）"]
    fm = reg["field_matrix"]
    ns, _ = gm.build_matrix_from_md()
    base = {k: sorted(v) for k, v in ns.items()}
    problems = []
    if set(fm) != set(base):
        problems.append(f"field_matrix 字段集 != 基线 {len(fm)} vs {len(base)}; "
                        f"缺 {len(set(base) - set(fm))} 多 {len(set(fm) - set(base))}")
    bad = []
    for k in set(fm) & set(base):
        if sorted(fm[k]) != base[k]:
            bad.append(k)
            if len(bad) >= 10:
                break
    if bad:
        problems.append(f"field_matrix 源集合不一致(抽样): {bad}")
    return problems


if __name__ == "__main__":
    sys.exit(main())

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
import argparse

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
import audit_field_completeness as afc
import gen_field_matrix as gm
import field_registry_api as fra


def main(argv=None):
    parser = argparse.ArgumentParser(description="校验逐源字段与历史来源基线 parity")
    parser.add_argument("--registry", default=REGISTRY, help="待核对的 registry JSON")
    args = parser.parse_args(argv)
    if not os.path.exists(args.registry):
        print(f"FAIL: 未找到 registry: {args.registry}")
        return 1

    with io.open(args.registry, encoding="utf-8") as f:
        reg = json.load(f)

    # 基线（原生 token）：audit_field_completeness.registered_field_sets
    base_reg = afc.registered_field_sets()
    base_field_sources = {}
    for src, toks in base_reg.items():
        for t in toks:
            base_field_sources.setdefault(t, set()).add(src)
    base_pairs = {(src, token) for token, sources in base_field_sources.items() for src in sources}

    # registry 视图（原生 token）：code -> set(sources)
    try:
        source_records = fra.source_field_records(reg)
        reg_field_sources = fra.field_source_map(reg)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"parity[native]: FAIL — source_fields 无效: {exc}")
        return 1
    if not source_records:
        print("parity[native]: FAIL — registry 缺少 source_fields")
        return 1
    addenda_pairs, matrix_addenda, addenda_problems = _validated_addenda(
        reg, source_records, base_pairs
    )
    actual_pairs = {(record["source"], record["code"]) for record in source_records}
    expected_pairs = base_pairs | addenda_pairs
    expected_field_sources = _pairs_to_field_sources(expected_pairs)
    reg_fields = len(reg_field_sources)
    reg_records = len(actual_pairs)
    reg_multi = sum(1 for v in reg_field_sources.values() if len(v) >= 2)
    expected_fields = len(expected_field_sources)
    expected_multi = sum(1 for v in expected_field_sources.values() if len(v) >= 2)

    problems = list(addenda_problems)
    missing_pairs = expected_pairs - actual_pairs
    extra_pairs = actual_pairs - expected_pairs
    if missing_pairs:
        problems.append(
            f"基线或证据补录有而 registry 缺 {len(missing_pairs)}: {sorted(missing_pairs)[:10]}"
        )
    if extra_pairs:
        problems.append(
            f"registry 多出于基线及声明补录 {len(extra_pairs)}: {sorted(extra_pairs)[:10]}"
        )
    if reg_fields != expected_fields:
        problems.append(f"字段数 {reg_fields} != 基线加 E3 补录 {expected_fields}")
    if reg_records != len(expected_pairs):
        problems.append(f"配对总数 {reg_records} != 基线加 E3 补录 {len(expected_pairs)}")
    if reg_multi != expected_multi:
        problems.append(f"多源数 {reg_multi} != 基线加 E3 补录 {expected_multi}")

    print(
        f"parity[native]: registry({reg_fields}/{reg_records}/{reg_multi}) "
        f"vs baseline+E3-addenda({expected_fields}/{len(expected_pairs)}/{expected_multi})"
    )
    if problems:
        print("  native FAIL:")
        for p in problems:
            print("   -", p)
    else:
        print("  native PASS: 历史原文映射完整，且仅含具备 E3 证据的显式补录")

    aggregate_sources = {}
    for record in reg.get("fields", []):
        aggregate_sources.setdefault(record["code"], set()).update(record.get("sources", []))
    if aggregate_sources != reg_field_sources:
        problems.append("fields 兼容聚合视图与 source_fields 投影不一致")
        print("  projection FAIL: fields 与 source_fields 不一致")
    else:
        print("  projection PASS: fields 聚合视图与 source_fields 一致")
    expected_aggregates = fra.build_aggregate_fields(source_records)
    if reg.get("fields") != expected_aggregates:
        problems.append("fields 聚合语义/状态与 source_fields 重建结果不一致")
        print("  aggregate semantics FAIL: fields 不是安全的 source_fields 聚合投影")
    else:
        print("  aggregate semantics PASS: fields 的定义、状态和歧义标记与 source_fields 一致")

    # ---- field_matrix 投影 parity（§零·B 生成一致性，G3 闸门）----
    fm_problems = check_field_matrix(reg, matrix_addenda)
    print(f"parity[field_matrix]: {'PASS' if not fm_problems else 'FAIL'}")
    for p in fm_problems:
        print("   -", p)

    all_problems = problems + fm_problems
    if all_problems:
        return 1
    print("PASS: registry 双重 parity 全部通过（原生 token + §零·B 投影）")
    return 0


def _pairs_to_field_sources(pairs: set[tuple[str, str]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for source, code in pairs:
        out.setdefault(code, set()).add(source)
    return out


def _repo_file_exists(relative_path: str) -> bool:
    target = os.path.normcase(os.path.realpath(os.path.join(REPO_ROOT, relative_path)))
    root = os.path.normcase(os.path.realpath(REPO_ROOT))
    try:
        return os.path.commonpath([root, target]) == root and os.path.isfile(target)
    except ValueError:
        return False


def _validated_addenda(
    reg: dict, source_records: list[dict], base_pairs: set[tuple[str, str]]
) -> tuple[set, dict, list]:
    declarations = reg.get("source_field_addenda", [])
    if not isinstance(declarations, list):
        return set(), {}, ["source_field_addenda 必须是数组"]
    source_names = {item.get("name") for item in reg.get("sources", []) if isinstance(item, dict)}
    rows = {(row["source"], row["code"]): row for row in source_records}
    declared = set()
    matrix_addenda: dict[str, set[str]] = {}
    problems = []
    for item in declarations:
        if not isinstance(item, dict):
            problems.append("source_field_addenda 包含非对象记录")
            continue
        source, code = item.get("source"), item.get("code")
        if not isinstance(source, str) or not source or not isinstance(code, str) or not code:
            problems.append("source_field_addenda 需要非空 source/code")
            continue
        pair = (source, code)
        if pair in base_pairs:
            problems.append(f"source_field_addenda 不能重复声明历史基线字段: {source}::{code}")
            continue
        if pair in declared or pair not in rows or source not in source_names:
            problems.append(
                f"source_field_addenda 身份重复或 registry 无对应源字段: {source}::{code}"
            )
            continue
        declared.add(pair)
        row = rows[pair]
        if item.get("evidence_level") != "E3":
            problems.append(f"{source}::{code} 补录必须具备 E3 证据等级")
        evidence_file = item.get("evidence_file")
        if (
            not isinstance(evidence_file, str)
            or not evidence_file
            or not _repo_file_exists(evidence_file)
        ):
            problems.append(f"{source}::{code} 证据文件不存在或位于仓库外: {evidence_file}")
        for key in ("canonical", "meaning", "unit"):
            if row.get(key, "") != item.get(key, ""):
                problems.append(f"{source}::{code} 补录的 {key} 与 source_fields 不一致")
        if row.get("status") != "verified":
            problems.append(f"{source}::{code} E3 补录必须为 verified")
        matrix_field, matrix_source = item.get("matrix_field"), item.get("matrix_source")
        if not isinstance(matrix_field, str) or not matrix_field:
            problems.append(f"{source}::{code} 缺少 matrix_field")
        elif not isinstance(matrix_source, str) or not matrix_source:
            problems.append(f"{source}::{code} 缺少 matrix_source")
        else:
            matrix_addenda.setdefault(matrix_field, set()).add(matrix_source)
    return declared, matrix_addenda, problems


def check_field_matrix(reg: dict, addenda: dict | None = None) -> list:
    """§零·B 投影 parity：registry.field_matrix 须与 gen_field_matrix.build_matrix_from_md 同构。

    field_matrix 必须与只读历史来源文档 field_source_reference.md 解析结果一致。
    """
    if "field_matrix" not in reg:
        return ["registry 缺少 field_matrix 投影（请重跑 extract_registry.py）"]
    fm = reg["field_matrix"]
    ns, _ = gm.build_matrix_from_md()
    base_sets = {key: set(value) for key, value in ns.items()}
    for field, sources in (addenda or {}).items():
        base_sets.setdefault(field, set()).update(sources)
    base = {key: sorted(value) for key, value in base_sets.items()}
    problems = []
    if set(fm) != set(base):
        problems.append(
            f"field_matrix 字段集 != 基线 {len(fm)} vs {len(base)}; "
            f"缺 {len(set(base) - set(fm))} 多 {len(set(fm) - set(base))}"
        )
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

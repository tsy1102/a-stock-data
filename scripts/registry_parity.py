"""registry_parity.py — 字段登记表 parity 闸门（registry ↔ markdown 原生 token）。

校验 docs/field_verification/field_registry.json 与
field_source_reference.md 经 audit_field_completeness.registered_field_sets() 抽取出的
「原生 token × 源」集合完全一致。后者是只读历史来源档案，不是生成视图 field_dict.md。
用于 CI / 提交前闸门。

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
SCOPE_MANIFEST = os.path.join(REPO_ROOT, "docs", "field_verification", "registry_parity_scope.json")

sys.path.insert(0, SCRIPT_DIR)
import audit_field_completeness as afc
import gen_field_matrix as gm
import field_registry_api as fra


def main(argv=None):
    parser = argparse.ArgumentParser(description="校验逐源字段与历史来源基线 parity")
    parser.add_argument("--registry", default=REGISTRY, help="待核对的 registry JSON")
    parser.add_argument(
        "--accepted-debt-manifest",
        help="本地治理门禁使用的已接受缺失配对清单；默认仍执行严格 parity",
    )
    parser.add_argument(
        "--scope-manifest",
        default=SCOPE_MANIFEST,
        help="历史基线中非当前生产字段的逐项范围处置清单",
    )
    args = parser.parse_args(argv)
    if not os.path.exists(args.registry):
        print(f"FAIL: 未找到 registry: {args.registry}")
        return 1

    with io.open(args.registry, encoding="utf-8") as f:
        reg = json.load(f)

    # 基线（只读历史来源档案中的原生 token）：audit_field_completeness.registered_field_sets
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
    scope_entries, scope_problems = _load_scope_manifest(args.scope_manifest)
    if scope_entries is None:
        scope_entries = {}
    scope_pairs = set(scope_entries)
    stale_scope_pairs = scope_pairs - base_pairs
    registered_scope_pairs = scope_pairs & actual_pairs
    addenda_scope_pairs = scope_pairs & addenda_pairs
    if stale_scope_pairs:
        scope_problems.append(
            f"范围清单包含不再属于历史基线的配对: {sorted(stale_scope_pairs)[:10]}"
        )
    if registered_scope_pairs:
        scope_problems.append(
            f"范围清单排除项已登记在 registry 中: {sorted(registered_scope_pairs)[:10]}"
        )
    if addenda_scope_pairs:
        scope_problems.append(
            f"范围清单排除项与 source_field_addenda 重叠: {sorted(addenda_scope_pairs)[:10]}"
        )
    expected_pairs = (base_pairs - scope_pairs) | addenda_pairs
    accepted_missing_pairs = None
    debt_problems = []
    if args.accepted_debt_manifest:
        manifest_path = os.path.join(REPO_ROOT, args.accepted_debt_manifest)
        accepted_missing_pairs, debt_problems = _load_accepted_debt_manifest(manifest_path)
    reg_fields = len(reg_field_sources)
    reg_records = len(actual_pairs)
    reg_multi = sum(1 for v in reg_field_sources.values() if len(v) >= 2)

    missing_pairs, extra_pairs, pair_problems, pair_warnings = _native_pair_problems(
        expected_pairs, actual_pairs, accepted_missing_pairs
    )
    problems = list(addenda_problems) + scope_problems + debt_problems + pair_problems
    parity_expected_pairs = _pairs_for_count_check(
        expected_pairs, missing_pairs, accepted_missing_pairs
    )
    expected_field_sources = _pairs_to_field_sources(parity_expected_pairs)
    expected_fields = len(expected_field_sources)
    expected_multi = sum(1 for v in expected_field_sources.values() if len(v) >= 2)
    if reg_fields != expected_fields:
        problems.append(f"字段数 {reg_fields} != parity 预期 {expected_fields}")
    if reg_records != len(parity_expected_pairs):
        problems.append(f"配对总数 {reg_records} != parity 预期 {len(parity_expected_pairs)}")
    if reg_multi != expected_multi:
        problems.append(f"多源数 {reg_multi} != parity 预期 {expected_multi}")

    expected_label = "baseline-scope-adjusted+E3-addenda"
    if accepted_missing_pairs is not None:
        expected_label += "-accepted-debt-adjusted"
    print(
        f"parity[native]: registry({reg_fields}/{reg_records}/{reg_multi}) "
        f"vs {expected_label}({expected_fields}/{len(parity_expected_pairs)}/{expected_multi})"
    )
    disposition_counts = {}
    for entry in scope_entries.values():
        disposition = entry["disposition"]
        disposition_counts[disposition] = disposition_counts.get(disposition, 0) + 1
    scope_state = "PASS" if not scope_problems else "FAIL"
    print(f"parity[scope]: {scope_state} {len(scope_pairs)} 项范围处置 " f"({disposition_counts})")
    for problem in scope_problems:
        print("  scope FAIL:", problem)
    if problems:
        print("  native FAIL:")
        for p in problems:
            print("   -", p)
    elif accepted_missing_pairs is not None:
        print(
            "  native PASS: 当前缺失配对均在已登记的接受清单中 "
            f"({len(missing_pairs)}/{len(accepted_missing_pairs)} 个)"
        )
    else:
        print("  native PASS: 历史原文映射完整，且仅含具备 E3 证据的显式补录")
    for warning in pair_warnings:
        print(f"  native WARN: {warning}")

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


def _pairs_for_count_check(
    expected_pairs: set[tuple[str, str]],
    missing_pairs: set[tuple[str, str]],
    accepted_missing_pairs: set[tuple[str, str]] | None,
) -> set[tuple[str, str]]:
    """Keep strict parity counts against the full baseline; adjust only declared debt."""
    if accepted_missing_pairs is not None:
        return expected_pairs - missing_pairs
    return expected_pairs


def _load_scope_manifest(
    manifest_path: str,
) -> tuple[dict[tuple[str, str], dict] | None, list[str]]:
    """Load and validate the explicit distinction between archival and runtime scope."""
    if not _repo_file_exists(manifest_path):
        return None, [f"范围处置清单不存在或位于仓库外: {manifest_path}"]
    try:
        with io.open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, [f"范围处置清单无法读取: {exc}"]
    entries, problems = _validate_scope_manifest(manifest)
    if entries is None:
        return None, problems
    for pair, entry in entries.items():
        for evidence_file in entry["evidence_files"]:
            if not _repo_file_exists(evidence_file):
                problems.append(
                    f"范围处置项 {pair[0]}::{pair[1]} 的证据文件不存在或位于仓库外: "
                    f"{evidence_file}"
                )
    return (entries if not problems else None), problems


def _validate_scope_manifest(
    manifest: object,
) -> tuple[dict[tuple[str, str], dict] | None, list[str]]:
    """Validate explicit field-scope dispositions without repository I/O."""
    if not isinstance(manifest, dict):
        return None, ["范围处置清单必须是 JSON 对象"]
    if set(manifest) != {"schema_version", "purpose", "entries"}:
        return None, ["范围处置清单只允许 schema_version/purpose/entries"]
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        return None, ["范围处置清单 schema_version 必须为 1"]
    if not isinstance(manifest.get("purpose"), str) or not manifest["purpose"].strip():
        return None, ["范围处置清单缺少非空 purpose"]
    raw_entries = manifest.get("entries")
    if not isinstance(raw_entries, list):
        return None, ["范围处置清单 entries 必须是数组"]

    entries: dict[tuple[str, str], dict] = {}
    problems = []
    required = {"source", "code", "disposition", "reason", "evidence_files", "capture_path"}
    allowed_dispositions = {"archive_only", "captured_context", "captured_runtime"}
    for index, entry in enumerate(raw_entries):
        if not isinstance(entry, dict) or set(entry) != required:
            problems.append(
                f"entries[{index}] 必须包含且仅包含 "
                "source/code/disposition/reason/evidence_files/capture_path"
            )
            continue
        source, code = entry.get("source"), entry.get("code")
        if not isinstance(source, str) or not source.strip():
            problems.append(f"entries[{index}].source 必须是非空字符串")
            continue
        if not isinstance(code, str) or not code.strip():
            problems.append(f"entries[{index}].code 必须是非空字符串")
            continue
        pair = (source, code)
        if pair in entries:
            problems.append(f"范围处置清单包含重复配对: {source}::{code}")
            continue
        disposition = entry.get("disposition")
        if disposition not in allowed_dispositions:
            problems.append(
                f"entries[{index}].disposition 必须为 archive_only、captured_context 或 captured_runtime"
            )
            continue
        if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
            problems.append(f"entries[{index}].reason 必须是非空字符串")
            continue
        evidence_files = entry.get("evidence_files")
        if (
            not isinstance(evidence_files, list)
            or not evidence_files
            or any(not isinstance(path, str) or not path.strip() for path in evidence_files)
            or len(evidence_files) != len(set(evidence_files))
        ):
            problems.append(f"entries[{index}].evidence_files 必须是非空且不重复的路径数组")
            continue
        capture_path = entry.get("capture_path")
        if disposition in {"captured_context", "captured_runtime"}:
            if not isinstance(capture_path, str) or not capture_path.strip():
                problems.append(f"entries[{index}] {disposition} 必须声明 capture_path")
                continue
        elif capture_path is not None:
            problems.append(f"entries[{index}] archive_only 的 capture_path 必须为 null")
            continue
        entries[pair] = entry
    return (entries if not problems else None), problems


def _native_pair_problems(
    expected_pairs: set[tuple[str, str]],
    actual_pairs: set[tuple[str, str]],
    accepted_missing_pairs: set[tuple[str, str]] | None = None,
) -> tuple[set[tuple[str, str]], set[tuple[str, str]], list[str], list[str]]:
    """Compare source/code pairs, optionally allowing only documented missing pairs."""
    missing_pairs = expected_pairs - actual_pairs
    extra_pairs = actual_pairs - expected_pairs
    problems = []
    warnings = []

    if accepted_missing_pairs is None:
        if missing_pairs:
            problems.append(
                f"基线或证据补录有而 registry 缺 {len(missing_pairs)}: "
                f"{sorted(missing_pairs)[:10]}"
            )
    else:
        stale_debt = accepted_missing_pairs - expected_pairs
        new_missing = missing_pairs - accepted_missing_pairs
        resolved_debt = accepted_missing_pairs - missing_pairs
        if stale_debt:
            problems.append(f"接受清单包含不再属于基线的配对: {sorted(stale_debt)[:10]}")
        if new_missing:
            problems.append(
                f"出现未登记的新缺失配对 {len(new_missing)}: {sorted(new_missing)[:10]}"
            )
        if resolved_debt:
            warnings.append(
                "部分接受差异已补齐；建议从清单移除，避免以后回退时仍被视为已接受: "
                f"{sorted(resolved_debt)[:10]}"
            )

    if extra_pairs:
        problems.append(
            f"registry 多出于基线及声明补录 {len(extra_pairs)}: {sorted(extra_pairs)[:10]}"
        )
    return missing_pairs, extra_pairs, problems, warnings


def _load_accepted_debt_manifest(
    manifest_path: str,
) -> tuple[set[tuple[str, str]] | None, list[str]]:
    """Load a repository-local, reviewable exception for the exact open parity delta."""
    if not _repo_file_exists(manifest_path):
        return None, [f"接受差异清单不存在或位于仓库外: {manifest_path}"]
    try:
        with io.open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, [f"接受差异清单无法读取: {exc}"]
    return _validate_accepted_debt_manifest(manifest)


def _validate_accepted_debt_manifest(
    manifest: object,
) -> tuple[set[tuple[str, str]] | None, list[str]]:
    """Validate the manifest structure without reading repository files."""
    if not isinstance(manifest, dict):
        return None, ["接受差异清单必须是 JSON 对象"]
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        return None, ["接受差异清单 schema_version 必须为 1"]
    for key in ("debt_id", "reason", "review_trigger"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            return None, [f"接受差异清单缺少非空 {key}"]
    entries = manifest.get("accepted_missing_pairs")
    if not isinstance(entries, list):
        return None, ["accepted_missing_pairs 必须是数组"]

    pairs: set[tuple[str, str]] = set()
    problems = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {"source", "code"}:
            problems.append(f"accepted_missing_pairs[{index}] 必须仅包含 source/code")
            continue
        source, code = entry.get("source"), entry.get("code")
        if not isinstance(source, str) or not source.strip():
            problems.append(f"accepted_missing_pairs[{index}].source 必须是非空字符串")
            continue
        if not isinstance(code, str) or not code.strip():
            problems.append(f"accepted_missing_pairs[{index}].code 必须是非空字符串")
            continue
        pair = (source, code)
        if pair in pairs:
            problems.append(f"接受差异清单包含重复配对: {source}::{code}")
            continue
        pairs.add(pair)
    return (pairs if not problems else None), problems


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

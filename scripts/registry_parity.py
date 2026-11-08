"""字段登记表 parity 闸门：历史基线、声明补录与待核队列分层核验。

历史核心集合来自只读档案 field_source_reference.md，经
audit_field_completeness.registered_field_sets() 抽取。字段注册表还包含未验证候选，
它们留在 unknown_fields.md 队列，不冒充历史基线字段；证据补录和候选集合分别验证。
用于 CI / 提交前闸门。

判定（G1）：
  * 历史基线及经过验证的补录必须与注册表核心集合精确一致。
  * 未验证候选必须保持 unresolved 状态并出现在 unknown_fields.md。
  * 人工定案与采集根路径补录必须能追溯到决策文件或保留样本。
  * 原生 token 数、多源数与字段矩阵投影均须一致。

退出码：0=通过；1=未通过（不应提交）。
"""

from __future__ import annotations

import io
import json
import os
import sys
import argparse
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

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
CAPTURE_PATH_MANIFEST = os.path.join(
    REPO_ROOT, "docs", "field_verification", "registry_capture_path_addenda.json"
)
UNKNOWN_FIELDS = os.path.join(REPO_ROOT, "docs", "unknown_fields.md")

sys.path.insert(0, SCRIPT_DIR)
import audit_field_completeness as afc
import gen_field_matrix as gm
import field_registry_api as fra
import public_web_adjudications as pwa
import capture_retention


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
    e3_pairs, e3_matrix, e3_problems = _validated_addenda(reg, source_records, base_pairs)
    contract_pairs, contract_matrix, contract_problems = _validated_contract_addenda(
        reg, source_records, base_pairs
    )
    observation_pairs, observation_matrix, observation_problems = _validated_observation_addenda(
        reg, source_records, base_pairs
    )
    declared_pairs = e3_pairs | contract_pairs | observation_pairs
    adjudication_pairs, adjudication_matrix, adjudication_problems = (
        _validated_adjudication_addenda(reg, source_records, base_pairs | declared_pairs)
    )
    capture_path_pairs, capture_path_problems = _validated_capture_path_addenda(
        reg,
        source_records,
        base_pairs | declared_pairs | adjudication_pairs,
    )
    public_web_problems = pwa.validate_registry_adjudications(reg, Path(REPO_ROOT))
    addenda_pairs = declared_pairs | adjudication_pairs | capture_path_pairs
    matrix_addenda = {key: set(value) for key, value in e3_matrix.items()}
    for additional_matrix in (
        contract_matrix,
        observation_matrix,
        adjudication_matrix,
    ):
        for key, value in additional_matrix.items():
            matrix_addenda.setdefault(key, set()).update(value)
    addenda_problems = e3_problems + contract_problems + observation_problems
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
        scope_problems.append(f"范围清单排除项与字段补录重叠: {sorted(addenda_scope_pairs)[:10]}")
    expected_pairs = (base_pairs - scope_pairs) | addenda_pairs
    accepted_missing_pairs = None
    debt_problems = []
    if args.accepted_debt_manifest:
        manifest_path = os.path.join(REPO_ROOT, args.accepted_debt_manifest)
        accepted_missing_pairs, debt_problems = _load_accepted_debt_manifest(manifest_path)
    candidate_pairs, candidate_problems = _validated_unverified_candidates(
        expected_pairs, actual_pairs, source_records, UNKNOWN_FIELDS
    )
    parity_pairs = actual_pairs - candidate_pairs
    parity_field_sources = _pairs_to_field_sources(parity_pairs)
    reg_fields = len(parity_field_sources)
    reg_records = len(parity_pairs)
    reg_multi = sum(1 for v in parity_field_sources.values() if len(v) >= 2)

    missing_pairs, extra_pairs, pair_problems, pair_warnings = _native_pair_problems(
        expected_pairs, parity_pairs, accepted_missing_pairs
    )
    problems = (
        list(addenda_problems)
        + adjudication_problems
        + capture_path_problems
        + public_web_problems
        + scope_problems
        + candidate_problems
        + debt_problems
        + pair_problems
    )
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

    expected_label = (
        "baseline-scope-adjusted+E3+official-contract+observation+public-web+"
        "adjudication+capture-path-addenda"
    )
    if accepted_missing_pairs is not None:
        expected_label += "-accepted-debt-adjusted"
    print(
        f"parity[native]: registry-core({reg_fields}/{reg_records}/{reg_multi}) "
        f"vs {expected_label}({expected_fields}/{len(parity_expected_pairs)}/{expected_multi})"
    )
    candidate_counts: dict[str, int] = {}
    for source, _ in candidate_pairs:
        candidate_counts[source] = candidate_counts.get(source, 0) + 1
    print(
        f"parity[unverified-candidates]: {'PASS' if not candidate_problems else 'FAIL'} "
        f"{len(candidate_pairs)} 条未验证候选已列入 unknown_fields ({candidate_counts})"
    )
    print(
        f"parity[adjudication-addenda]: "
        f"{'PASS' if not adjudication_problems else 'FAIL'} {len(adjudication_pairs)} 条"
    )
    print(f"parity[public-web-adjudications]: " f"{'PASS' if not public_web_problems else 'FAIL'}")
    for problem in public_web_problems:
        print("  public-web FAIL:", problem)
    print(
        f"parity[capture-path-addenda]: "
        f"{'PASS' if not capture_path_problems else 'FAIL'} {len(capture_path_pairs)} 条"
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
        print("  native PASS: 历史基线及逐项声明补录完整；未验证候选另列待核")
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


def _validated_contract_addenda(
    reg: dict, source_records: list[dict], base_pairs: set[tuple[str, str]]
) -> tuple[set, dict, list]:
    """Validate fields whose meanings come from an explicit public API contract."""
    declarations = reg.get("source_contract_addenda", [])
    if not isinstance(declarations, list):
        return set(), {}, ["source_contract_addenda 必须是数组"]
    source_configs = {
        item.get("name"): item
        for item in reg.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    rows = {(row["source"], row["code"]): row for row in source_records}
    declared: set[tuple[str, str]] = set()
    matrix_addenda: dict[str, set[str]] = {}
    problems: list[str] = []
    catalog_path = os.path.join(REPO_ROOT, "docs", "ftshare_contract_catalog.json")
    try:
        with io.open(catalog_path, encoding="utf-8") as handle:
            catalog = json.load(handle)
    except (OSError, ValueError, TypeError) as exc:
        return set(), {}, [f"FTShare 官方契约目录无法读取: {exc}"]
    contracts = catalog.get("verified_contracts", {})
    if not isinstance(contracts, dict):
        return set(), {}, ["FTShare 官方契约目录缺少 verified_contracts 对象"]

    for item in declarations:
        if not isinstance(item, dict):
            problems.append("source_contract_addenda 包含非对象记录")
            continue
        source, code, contract_id = item.get("source"), item.get("code"), item.get("contract_id")
        if not all(isinstance(value, str) and value for value in (source, code, contract_id)):
            problems.append("source_contract_addenda 需要非空 source/code/contract_id")
            continue
        pair = (source, code)
        source_config = source_configs.get(source, {})
        contract = contracts.get(contract_id)
        if pair in base_pairs:
            problems.append(f"source_contract_addenda 不能重复声明历史基线字段: {source}::{code}")
            continue
        if pair in declared or pair not in rows or source not in source_configs:
            problems.append(
                f"source_contract_addenda 身份重复或 registry 无对应源字段: {source}::{code}"
            )
            continue
        declared.add(pair)
        if source_config.get("source_role") != "documented_contract_anchor":
            problems.append(f"{source}::{code} 来源未声明 documented_contract_anchor")
        if not isinstance(contract, dict):
            problems.append(f"{source}::{code} 引用未知契约: {contract_id}")
            continue
        if item.get("evidence_level") != "official_contract":
            problems.append(f"{source}::{code} 证据等级必须是 official_contract")
        field_names = {
            field.get("name")
            for field in contract.get("returned_fields", [])
            if isinstance(field, dict)
        }
        if code not in field_names:
            problems.append(f"{source}::{code} 不在 {contract_id} 官方返回字段表中")
        evidence_file = item.get("evidence_file")
        if (
            not isinstance(evidence_file, str)
            or not evidence_file
            or not _repo_file_exists(evidence_file)
        ):
            problems.append(f"{source}::{code} 官方契约证据文件不存在或位于仓库外: {evidence_file}")
        else:
            evidence_path = os.path.join(REPO_ROOT, evidence_file.replace("/", os.sep))
            with io.open(evidence_path, encoding="utf-8") as handle:
                evidence_text = handle.read()
            doc_url = contract.get("documentation_url")
            if not isinstance(doc_url, str) or doc_url not in evidence_text:
                problems.append(f"{source}::{code} 证据文件未链接对应的官方接口文档")
            if f"`{code}`" not in evidence_text:
                problems.append(f"{source}::{code} 证据文件未列出字段代码")
        row = rows[pair]
        raw_evidence = row.get("evidence")
        evidence: dict[str, Any] = raw_evidence if isinstance(raw_evidence, dict) else {}
        for key in ("canonical", "meaning", "unit"):
            if row.get(key, "") != item.get(key, ""):
                problems.append(f"{source}::{code} 契约补录的 {key} 与 source_fields 不一致")
        if row.get("status") != "verified":
            problems.append(f"{source}::{code} 官方契约字段必须为 verified")
        if (
            evidence.get("basis") != "official_contract"
            or evidence.get("contract_id") != contract_id
            or evidence.get("evidence_file") != evidence_file
        ):
            problems.append(f"{source}::{code} source_fields 缺少匹配的官方契约证据")
        matrix_field, matrix_source = item.get("matrix_field"), item.get("matrix_source")
        if not isinstance(matrix_field, str) or not matrix_field:
            problems.append(f"{source}::{code} 缺少 matrix_field")
        elif not isinstance(matrix_source, str) or not matrix_source:
            problems.append(f"{source}::{code} 缺少 matrix_source")
        elif matrix_source != source:
            problems.append(f"{source}::{code} matrix_source 必须等于源身份 {source}")
        else:
            matrix_addenda.setdefault(matrix_field, set()).add(matrix_source)

    for source, config in source_configs.items():
        if config.get("source_role") != "documented_contract_anchor":
            continue
        for row in source_records:
            if row.get("source") == source and row.get("status") == "verified":
                pair = (source, row.get("code"))
                if pair not in declared:
                    problems.append(f"{source}::{row.get('code')} 缺少官方契约补录")
    return declared, matrix_addenda, problems


def _validated_observation_addenda(
    reg: dict, source_records: list[dict], base_pairs: set[tuple[str, str]]
) -> tuple[set, dict, list]:
    """Track captured fields that are observed but not defined by a public contract."""
    declarations = reg.get("source_observation_addenda", [])
    if not isinstance(declarations, list):
        return set(), {}, ["source_observation_addenda 必须是数组"]
    rows = {(row["source"], row["code"]): row for row in source_records}
    source_names = {item.get("name") for item in reg.get("sources", []) if isinstance(item, dict)}
    declared: set[tuple[str, str]] = set()
    matrix_addenda: dict[str, set[str]] = {}
    problems: list[str] = []
    catalog_path = os.path.join(REPO_ROOT, "docs", "ftshare_contract_catalog.json")
    try:
        with io.open(catalog_path, encoding="utf-8") as handle:
            catalog = json.load(handle)
        contract = catalog["verified_contracts"]["a_share_realtime_quote"]
        observed_schema = contract["observed_response_schema"]
        observed_names = set(observed_schema["field_names"])
        documented_names = {item["name"] for item in contract["returned_fields"]}
        undocumented = observed_names - documented_names
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return set(), {}, [f"FTShare 单次观测目录无法读取: {exc}"]

    for item in declarations:
        if not isinstance(item, dict):
            problems.append("source_observation_addenda 包含非对象记录")
            continue
        source, code = item.get("source"), item.get("code")
        if not isinstance(source, str) or not source or not isinstance(code, str) or not code:
            problems.append("source_observation_addenda 需要非空 source/code")
            continue
        pair = (source, code)
        if pair in base_pairs or pair in declared or pair not in rows or source not in source_names:
            problems.append(
                f"source_observation_addenda 身份重复或 registry 无对应源字段: {source}::{code}"
            )
            continue
        declared.add(pair)
        row = rows[pair]
        if item.get("evidence_level") != "single_live_response_observation":
            problems.append(f"{source}::{code} 观测证据等级必须为 single_live_response_observation")
        if code not in undocumented:
            problems.append(f"{source}::{code} 不是文档之外的单次观测字段")
        if code not in observed_names:
            problems.append(f"{source}::{code} 不在目录记录的观测响应结构中")
        if row.get("status") not in {"unverified", "candidate"}:
            problems.append(f"{source}::{code} 单次观测字段不能标记为已验证")
        evidence_file = item.get("evidence_file")
        if (
            not isinstance(evidence_file, str)
            or not evidence_file
            or not _repo_file_exists(evidence_file)
        ):
            problems.append(f"{source}::{code} 观测证据文件不存在或位于仓库外: {evidence_file}")
        else:
            evidence_path = os.path.join(REPO_ROOT, evidence_file.replace("/", os.sep))
            with io.open(evidence_path, encoding="utf-8") as handle:
                if f"`{code}`" not in handle.read():
                    problems.append(f"{source}::{code} 证据文件未列出观测字段")
        matrix_field, matrix_source = item.get("matrix_field"), item.get("matrix_source")
        if not isinstance(matrix_field, str) or not matrix_field:
            problems.append(f"{source}::{code} 缺少 matrix_field")
        elif matrix_source != source:
            problems.append(f"{source}::{code} matrix_source 必须等于来源身份 {source}")
        else:
            matrix_addenda.setdefault(matrix_field, set()).add(matrix_source)
    return declared, matrix_addenda, problems


def _validated_adjudication_addenda(
    reg: dict,
    source_records: list[dict],
    declared_pairs: set[tuple[str, str]],
) -> tuple[set[tuple[str, str]], dict[str, set[str]], list[str]]:
    """Validate verified source paths admitted by persisted collision decisions."""
    rows = {(row["source"], row["code"]): row for row in source_records}
    verification_root = Path(REPO_ROOT, "docs", "field_verification").resolve()
    declared: set[tuple[str, str]] = set()
    matrix_addenda: dict[str, set[str]] = {}
    problems: list[str] = []
    seen_ids: set[str] = set()
    decision_cache: dict[str, dict[str, Any] | None] = {}

    for pair, row in rows.items():
        if (
            pair in declared_pairs
            or row.get("status_resolution") != "manual_collision_adjudication"
        ):
            continue
        row_valid = _validate_adjudicated_row(
            pair, row, verification_root, decision_cache, seen_ids, problems
        )
        if row_valid:
            declared.add(pair)
            canonical = row.get("canonical")
            if isinstance(canonical, str) and canonical:
                matrix_addenda.setdefault(canonical, set()).add(pair[0])

    return declared, matrix_addenda, problems


def _validate_adjudicated_row(
    pair: tuple[str, str],
    row: dict,
    verification_root: Path,
    decision_cache: dict[str, dict[str, Any] | None],
    seen_ids: set[str],
    problems: list[str],
) -> bool:
    if row.get("status") != "verified":
        problems.append(f"{pair[0]}::{pair[1]} 人工定案补录必须为 verified")
        return False
    adjudications = row.get("adjudications")
    if not isinstance(adjudications, list) or not adjudications:
        problems.append(f"{pair[0]}::{pair[1]} 缺少持久化人工定案记录")
        return False

    row_valid = True
    has_verified_decision = False
    for adjudication in adjudications:
        if not isinstance(adjudication, dict):
            problems.append(f"{pair[0]}::{pair[1]} 人工定案记录必须为对象")
            row_valid = False
            continue
        if adjudication.get("action") != "verify" or adjudication.get("status") != "verified":
            continue
        has_verified_decision = True
        if not _validate_adjudication_record(
            pair, row, adjudication, verification_root, decision_cache, seen_ids, problems
        ):
            row_valid = False
    if not has_verified_decision:
        problems.append(f"{pair[0]}::{pair[1]} 缺少 verify 定案")
        row_valid = False
    return row_valid


def _validate_adjudication_record(
    pair: tuple[str, str],
    row: dict,
    adjudication: dict,
    verification_root: Path,
    decision_cache: dict[str, dict[str, Any] | None],
    seen_ids: set[str],
    problems: list[str],
) -> bool:
    identity = _resolve_adjudication_files(
        pair, adjudication, verification_root, seen_ids, problems
    )
    if identity is None:
        return False
    decision_id, decision_path, report_file = identity
    plan = _load_adjudication_plan(pair, decision_id, decision_path, decision_cache, problems)
    if plan is None:
        return False
    candidate = _match_adjudication_plan(
        pair, adjudication, decision_id, report_file, plan, problems
    )
    if candidate is None:
        return False
    return _validate_adjudication_evidence(
        pair, row, adjudication, decision_id, candidate, problems
    )


def _resolve_adjudication_files(
    pair: tuple[str, str],
    adjudication: dict,
    verification_root: Path,
    seen_ids: set[str],
    problems: list[str],
) -> tuple[str, Path, str] | None:
    decision_id = adjudication.get("id")
    if not isinstance(decision_id, str) or not decision_id:
        problems.append(f"{pair[0]}::{pair[1]} 人工定案缺少 id")
        return None
    if decision_id in seen_ids:
        problems.append(f"人工定案 id 重复: {decision_id}")
        return None
    seen_ids.add(decision_id)
    decision_file, report_file = adjudication.get("decision_file"), adjudication.get("report")
    if not isinstance(decision_file, str) or not decision_file or not isinstance(report_file, str):
        problems.append(f"{pair[0]}::{pair[1]} 人工定案缺少决策文件或报告路径")
        return None
    decision_path = _safe_repo_path(verification_root, decision_file)
    report_path = _safe_repo_path(verification_root, report_file)
    if decision_path is None or not decision_path.is_file():
        problems.append(f"{pair[0]}::{pair[1]} 决策文件不存在或越界: {decision_file}")
        return None
    if report_path is None:
        problems.append(f"{pair[0]}::{pair[1]} 定案报告路径越界: {report_file}")
        return None
    # Full collision JSON reports are local, ignored artifacts; the persisted decision carries
    # the candidate, target identity, and sample statistics needed by the repository gate.
    return decision_id, decision_path, report_file


def _load_adjudication_plan(
    pair: tuple[str, str],
    decision_id: str,
    decision_path: Path,
    decision_cache: dict[str, dict[str, Any] | None],
    problems: list[str],
) -> dict[str, Any] | None:
    decision_key = str(decision_path)
    if decision_key not in decision_cache:
        try:
            with io.open(decision_path, encoding="utf-8") as handle:
                loaded = json.load(handle)
            decision_cache[decision_key] = loaded if isinstance(loaded, dict) else None
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            problems.append(f"{pair[0]}::{pair[1]} 决策文件无法读取: {exc}")
            decision_cache[decision_key] = None
    plan = decision_cache[decision_key]
    if plan is None:
        problems.append(f"{pair[0]}::{pair[1]} 人工定案文件无效: {decision_id}")
    return plan


def _match_adjudication_plan(
    pair: tuple[str, str],
    adjudication: dict,
    decision_id: str,
    report_file: str,
    plan: dict[str, Any],
    problems: list[str],
) -> dict[str, Any] | None:
    decisions = plan.get("decisions")
    if not isinstance(decisions, list):
        problems.append(f"{pair[0]}::{pair[1]} 决策文件缺少 decisions 数组")
        return None
    matching = [
        item for item in decisions if isinstance(item, dict) and item.get("id") == decision_id
    ]
    if len(matching) != 1:
        problems.append(f"{pair[0]}::{pair[1]} 决策文件未唯一列出 {decision_id}")
        return None
    candidate = adjudication.get("candidate")
    decision = matching[0]
    expected_target = {"source": pair[0], "code": pair[1]}
    if (
        decision.get("action") != "verify"
        or decision.get("candidate") != candidate
        or plan.get("report") != report_file
        or plan.get("reviewed_on") != adjudication.get("reviewed_on")
        or decision.get("target") != expected_target
        or (
            adjudication.get("target") is not None and adjudication.get("target") != expected_target
        )
    ):
        problems.append(f"{pair[0]}::{pair[1]} 人工定案、目标身份与决策文件不一致: {decision_id}")
        return None
    if (
        not isinstance(candidate, dict)
        or not isinstance(candidate.get("left"), str)
        or not candidate["left"].strip()
        or not isinstance(candidate.get("right"), str)
        or not candidate["right"].strip()
    ):
        problems.append(f"{pair[0]}::{pair[1]} 人工定案未指向完整字段路径")
        return None
    return candidate


def _validate_adjudication_evidence(
    pair: tuple[str, str],
    row: dict,
    adjudication: dict,
    decision_id: str,
    candidate: dict[str, Any],
    problems: list[str],
) -> bool:
    evidence = adjudication.get("evidence")
    if (
        not isinstance(evidence, dict)
        or not isinstance(evidence.get("n_days"), int)
        or evidence.get("n_days", 0) < 1
        or not isinstance(evidence.get("n_pairs"), int)
        or evidence.get("n_pairs", 0) < 1
        or not isinstance(evidence.get("evidence_sources"), list)
        or not evidence["evidence_sources"]
    ):
        problems.append(f"{pair[0]}::{pair[1]} 人工定案缺少可复核的碰撞统计")
        return False
    references = row.get("reference_evidence")
    if not isinstance(references, list):
        problems.append(f"{pair[0]}::{pair[1]} source_fields 缺少定案引用: {decision_id}")
        return False
    matching = [
        item
        for item in references
        if isinstance(item, dict) and item.get("adjudication_id") == decision_id
    ]
    if len(matching) != 1 or matching[0].get("status") != "verified":
        problems.append(f"{pair[0]}::{pair[1]} source_fields 未引用定案状态: {decision_id}")
        return False
    reference = matching[0]
    if any(row.get(key, "") != reference.get(key, "") for key in ("canonical", "meaning", "unit")):
        problems.append(f"{pair[0]}::{pair[1]} 定案语义与 source_fields 不一致: {decision_id}")
        return False
    return bool(candidate)


def _validated_capture_path_addenda(
    reg: dict,
    source_records: list[dict],
    declared_pairs: set[tuple[str, str]],
    manifest: object | None = None,
    repo_root: Path | str = REPO_ROOT,
) -> tuple[set[tuple[str, str]], list[str]]:
    """Validate retained raw-capture root paths without asserting field semantics."""
    if manifest is None:
        try:
            with io.open(CAPTURE_PATH_MANIFEST, encoding="utf-8") as handle:
                manifest = json.load(handle)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return set(), [f"采集路径补录清单无法读取: {exc}"]
    source_names: set[str] = set()
    for item in reg.get("sources", []):
        if isinstance(item, dict):
            name = item.get("name")
            if isinstance(name, str):
                source_names.add(name)
    return _validate_capture_path_manifest(
        manifest,
        source_records,
        source_names,
        declared_pairs,
        Path(repo_root),
        capture_retention.MIN_CAPTURE_DATE,
    )


def _validate_capture_path_manifest(
    manifest: object,
    source_records: list[dict],
    source_names: set[str],
    declared_pairs: set[tuple[str, str]],
    repo_root: Path,
    min_capture_date: date,
) -> tuple[set[tuple[str, str]], list[str]]:
    problems: list[str] = []
    entries = _capture_manifest_entries(manifest, problems)
    if entries is None:
        return set(), problems
    rows = {(row["source"], row["code"]): row for row in source_records}
    declared: set[tuple[str, str]] = set()
    root = repo_root.resolve()
    for index, entry in enumerate(entries):
        fields = _capture_path_entry_fields(entry, index, problems)
        if fields is None:
            continue
        source, code, evidence_file, capture_path = fields
        pair = (source, code)
        if (
            pair in declared
            or pair in declared_pairs
            or pair not in rows
            or source not in source_names
        ):
            problems.append(f"采集路径身份重复、已声明或 registry 无对应字段: {source}::{code}")
            continue
        row = rows[pair]
        if (
            row.get("status") != "verified"
            or row.get("status_resolution") != "registry_status_only_single_source"
            or any(str(row.get(key) or "").strip() for key in ("canonical", "meaning", "unit"))
            or row.get("reference_evidence")
        ):
            problems.append(f"{source}::{code} 采集路径补录只允许无语义声明的已观测根路径")
            continue
        if not _capture_path_matches_retention(
            source, code, evidence_file, capture_path, min_capture_date, problems
        ):
            continue
        if not _capture_path_sample_is_valid(root, source, code, evidence_file, problems):
            continue
        declared.add(pair)
    return declared, problems


def _capture_manifest_entries(manifest: object, problems: list[str]) -> list | None:
    if not isinstance(manifest, dict):
        problems.append("采集路径补录清单必须是 JSON 对象")
        return None
    if set(manifest) != {"schema_version", "purpose", "entries"}:
        problems.append("采集路径补录清单只允许 schema_version/purpose/entries")
        return None
    if manifest.get("schema_version") != 1 or type(manifest.get("schema_version")) is not int:
        problems.append("采集路径补录清单 schema_version 必须为 1")
        return None
    if not isinstance(manifest.get("purpose"), str) or not manifest["purpose"].strip():
        problems.append("采集路径补录清单缺少非空 purpose")
        return None
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        problems.append("采集路径补录清单 entries 必须是数组")
        return None
    return entries


def _capture_path_entry_fields(
    entry: object, index: int, problems: list[str]
) -> tuple[str, str, str, str] | None:
    required = {"source", "code", "evidence_file", "capture_path"}
    if not isinstance(entry, dict) or set(entry) != required:
        problems.append(f"entries[{index}] 必须包含且仅包含 source/code/evidence_file/capture_path")
        return None
    fields = tuple(entry.get(key) for key in ("source", "code", "evidence_file", "capture_path"))
    if any(not isinstance(value, str) or not value.strip() for value in fields):
        problems.append(
            f"entries[{index}] 的 source/code/evidence_file/capture_path 必须为非空字符串"
        )
        return None
    return fields  # type: ignore[return-value]


def _capture_path_matches_retention(
    source: str,
    code: str,
    evidence_file: str,
    capture_path: str,
    min_capture_date: date,
    problems: list[str],
) -> bool:
    relative = Path(evidence_file)
    match = re.fullmatch(
        r"docs/field_verification/(\d{8})/raw_([A-Za-z0-9_]+)\.json",
        relative.as_posix(),
    )
    source_match = re.search(r"\(([^()]+)\)$", source)
    if not match or not source_match:
        problems.append(f"{source}::{code} 证据必须是按日期归档的源 raw JSON")
        return False
    try:
        capture_date = datetime.strptime(match.group(1), "%Y%m%d").date()
    except ValueError:
        problems.append(f"{source}::{code} evidence_file 日期无效: {evidence_file}")
        return False
    if capture_date < min_capture_date:
        problems.append(
            f"{source}::{code} 证据早于保留起始日 {min_capture_date.isoformat()}: {evidence_file}"
        )
        return False
    if match.group(2) != source_match.group(1) or capture_path != f"/{code}":
        problems.append(f"{source}::{code} 采集文件名或根路径与来源身份不匹配")
        return False
    return True


def _capture_path_sample_is_valid(
    root: Path, source: str, code: str, evidence_file: str, problems: list[str]
) -> bool:
    evidence_path = _safe_repo_path(root, Path(evidence_file).as_posix())
    if evidence_path is None or not evidence_path.is_file():
        problems.append(f"{source}::{code} 采集证据不存在或位于仓库外: {evidence_file}")
        return False
    try:
        with io.open(evidence_path, encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        problems.append(f"{source}::{code} raw JSON 无法读取: {exc}")
        return False
    value = payload.get(code) if isinstance(payload, dict) else None
    if value is None or (isinstance(value, dict) and "__error__" in value) or value == []:
        problems.append(f"{source}::{code} raw JSON 中没有有效的非空根路径")
        return False
    return True


def _validated_unverified_candidates(
    expected_pairs: set[tuple[str, str]],
    actual_pairs: set[tuple[str, str]],
    source_records: list[dict],
    unknown_fields_path: str = UNKNOWN_FIELDS,
) -> tuple[set[tuple[str, str]], list[str]]:
    """Separate unresolved inventory rows from verified baseline/addenda parity."""
    extras = actual_pairs - expected_pairs
    rows = {(row["source"], row["code"]): row for row in source_records}
    try:
        with io.open(unknown_fields_path, encoding="utf-8") as handle:
            queue_counts = _markdown_field_pair_counts(handle.read())
    except (OSError, UnicodeDecodeError) as exc:
        return set(), [f"未知字段队列无法读取: {exc}"]

    allowed_resolutions = {
        "registry_status_only_single_source",
        "aggregate_status_scope_unresolved",
        "status_missing",
    }
    candidates: set[tuple[str, str]] = set()
    problems: list[str] = []
    for pair in extras:
        row = rows[pair]
        adjudications = row.get("adjudications")
        has_verified_decision = isinstance(adjudications, list) and any(
            isinstance(item, dict)
            and item.get("action") == "verify"
            and item.get("status") == "verified"
            for item in adjudications
        )
        if (
            has_verified_decision
            or row.get("status") not in {"unverified", "candidate"}
            or row.get("status_resolution") not in allowed_resolutions
        ):
            continue
        candidates.add(pair)
        count = queue_counts.get(pair, 0)
        if count != 1:
            problems.append(
                f"未验证候选 {pair[0]}::{pair[1]} 在 unknown_fields 中出现 {count} 次（应为 1 次）"
            )
    return candidates, problems


def _markdown_field_pair_counts(markdown: str) -> dict[tuple[str, str], int]:
    counts: dict[tuple[str, str], int] = {}
    for line in markdown.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not cells[1].startswith("`") or not cells[1].endswith("`"):
            continue
        pair = (cells[0], cells[1][1:-1])
        counts[pair] = counts.get(pair, 0) + 1
    return counts


def _safe_repo_path(repo_root: Path, relative_path: str) -> Path | None:
    relative = Path(relative_path)
    if relative.is_absolute():
        return None
    root = repo_root.resolve()
    candidate = (root / relative).resolve()
    if candidate == root or not candidate.is_relative_to(root):
        return None
    return candidate


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

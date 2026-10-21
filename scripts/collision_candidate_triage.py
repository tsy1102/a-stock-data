"""Field-evidence coverage loading and deterministic candidate triage.

This module reads only the project-local ignored coverage cache and receives source
identity normalization and reporting helpers from the compatibility façade.
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from datetime import date, timedelta

from scripts.collision_dates import TRADING, parse_date


def load_field_coverage_index(folder_paths, trading_dates, event_start, event_end, coverage_root):
    """Read the ignored per-capture coverage indices without changing capture data."""
    selected_day_keys = {f"T:{str(value).replace('-', '')}" for value in trading_dates}
    if isinstance(event_start, str):
        event_start = parse_date(event_start)
    if isinstance(event_end, str):
        event_end = parse_date(event_end)
    if isinstance(event_start, date) and isinstance(event_end, date):
        event_day = event_start
        while event_day <= event_end:
            selected_day_keys.add(f"C:{event_day:%Y%m%d}")
            event_day += timedelta(days=1)

    coverage_records = {}
    source_statuses = defaultdict(lambda: defaultdict(set))
    diagnostics = []
    coverage_paths = set()
    metadata_count = 0
    metadata_errors = 0
    for folder in folder_paths:
        folder_path = os.fspath(getattr(folder, "path", folder))
        meta_path = os.path.join(folder_path, "meta.json")
        if not os.path.isfile(meta_path):
            continue
        try:
            with open(meta_path, encoding="utf-8") as handle:
                metadata = json.load(handle)
        except (OSError, ValueError, TypeError) as exc:
            metadata_errors += 1
            diagnostics.append(
                f"字段覆盖索引跳过无效 meta.json：{os.path.basename(folder_path)} ({exc})"
            )
            continue
        if not isinstance(metadata, dict):
            metadata_errors += 1
            diagnostics.append(f"字段覆盖索引跳过非对象 meta.json：{os.path.basename(folder_path)}")
            continue
        metadata_count += 1
        capture_day = str(metadata.get("data_date") or os.path.basename(folder_path))
        capture_day = re.sub(r"[^0-9]", "", capture_day)
        source_records = metadata.get("sources")
        if not isinstance(source_records, dict):
            source_records = {}
        capture_day_selected = bool(
            re.fullmatch(r"\d{8}", capture_day)
            and (f"T:{capture_day}" in selected_day_keys or f"C:{capture_day}" in selected_day_keys)
        )
        if capture_day_selected:
            for source, status_record in source_records.items():
                if isinstance(status_record, dict):
                    status = status_record.get("status") or status_record.get("state") or "unknown"
                elif isinstance(status_record, str):
                    status = status_record
                else:
                    status = "unknown"
                source_statuses[str(source)][str(status)].add(capture_day)

        coverage_meta = metadata.get("field_evidence_coverage")
        if not isinstance(coverage_meta, dict):
            continue
        report_day = re.sub(r"[^0-9]", "", str(coverage_meta.get("report_date") or capture_day))
        if not re.fullmatch(r"\d{8}", report_day):
            continue
        coverage_path = os.path.join(coverage_root, f"coverage_{report_day}.json")
        if coverage_path in coverage_paths or not os.path.isfile(coverage_path):
            continue
        coverage_paths.add(coverage_path)
        try:
            with open(coverage_path, encoding="utf-8") as handle:
                coverage_doc = json.load(handle)
        except (OSError, ValueError, TypeError) as exc:
            diagnostics.append(f"字段覆盖详情读取失败：{os.path.basename(coverage_path)} ({exc})")
            continue
        rows = coverage_doc.get("fields") if isinstance(coverage_doc, dict) else None
        if not isinstance(rows, list):
            diagnostics.append(f"字段覆盖详情格式无效：{os.path.basename(coverage_path)}")
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            source = row.get("source")
            code = row.get("code")
            if not isinstance(source, str) or not isinstance(code, str):
                continue
            identity = (source, code)
            aggregate = coverage_records.setdefault(
                identity,
                {
                    "source": source,
                    "code": code,
                    "registry_status": row.get("registry_status"),
                    "target_kind": row.get("target_kind"),
                    "identity_status": row.get("identity_status"),
                    "runtime_aliases": set(),
                    "independence_family": row.get("independence_family"),
                    "independence_status": row.get("independence_status"),
                    "anchor_eligible": bool(row.get("anchor_eligible")),
                    "source_as_of_days": set(),
                    "candidate_days": set(),
                    "source_as_of_sample_counts": {},
                    "source_statuses": set(),
                },
            )
            aggregate["runtime_aliases"].update(
                alias for alias in row.get("runtime_aliases", []) if isinstance(alias, str)
            )
            aggregate["source_statuses"].update(
                status for status in row.get("source_statuses", []) if isinstance(status, str)
            )
            for date_key in row.get("source_as_of_days", []):
                if date_key in selected_day_keys:
                    aggregate["source_as_of_days"].add(date_key)
            for date_key in row.get("candidate_days", []):
                if date_key in selected_day_keys:
                    aggregate["candidate_days"].add(date_key)
            for date_key, count in (row.get("source_as_of_sample_counts") or {}).items():
                if date_key in selected_day_keys and isinstance(count, int):
                    aggregate["source_as_of_sample_counts"][date_key] = max(
                        count, aggregate["source_as_of_sample_counts"].get(date_key, 0)
                    )

    statuses = {}
    for source, by_status in sorted(source_statuses.items()):
        statuses[source] = {
            "status_counts": {status: len(days) for status, days in sorted(by_status.items())},
            "non_ok_dates": sorted(
                day
                for status, days in by_status.items()
                if status.lower() not in {"ok", "success", "completed"}
                for day in days
            ),
        }
    return {
        "records": coverage_records,
        "source_statuses": statuses,
        "summary": {
            "capture_metadata_files": metadata_count,
            "metadata_errors": metadata_errors,
            "coverage_detail_files": len(coverage_paths),
            "coverage_identity_count": len(coverage_records),
            "detail_status": "available" if coverage_paths else "unavailable",
        },
        "diagnostics": diagnostics,
        "selected_day_keys": selected_day_keys,
    }


def coverage_records_for_target(fid, coverage_index, alias_src, code_of, normalize_code):
    alias = alias_src(fid)
    target_code = code_of(fid)
    matches = []
    for record in coverage_index.get("records", {}).values():
        if alias not in record.get("runtime_aliases", set()):
            continue
        record_code = normalize_code(alias, record.get("code", ""))
        if target_code == record_code or (
            alias == "zhb" and target_code.endswith("." + record_code)
        ):
            matches.append(record)

    output = []
    covered_days = set()
    candidate_days = set()
    for record in matches:
        family = record.get("independence_family")
        source_days = sorted(record.get("source_as_of_days", set()))
        possible_days = sorted(record.get("candidate_days", set()))
        covered_days.update(source_days)
        candidate_days.update(possible_days)
        output.append(
            {
                "source": record["source"],
                "code": record["code"],
                "registry_status": record.get("registry_status"),
                "identity_status": record.get("identity_status"),
                "independence_family": family,
                "independence_status": record.get("independence_status"),
                "anchor_eligible": bool(record.get("anchor_eligible")),
                "source_as_of_days": source_days,
                "candidate_days": possible_days,
                "source_as_of_sample_counts": dict(
                    sorted(record.get("source_as_of_sample_counts", {}).items())
                ),
                "source_statuses": sorted(record.get("source_statuses", set())),
            }
        )
    output.sort(
        key=lambda item: (
            item["anchor_eligible"],
            len(item["source_as_of_days"]),
            item["source"],
            item["code"],
        ),
        reverse=True,
    )
    return {
        "status": (
            "available"
            if coverage_index.get("summary", {}).get("coverage_detail_files")
            else "unavailable"
        ),
        "source_count": len(output),
        "source_as_of_days": sorted(covered_days),
        "candidate_days": sorted(candidate_days),
        "sources": output[:8],
    }


def build_candidate_triage(
    left_ids,
    candidate_counts,
    pair_stats,
    method_candidates_by_left,
    coverage_index,
    formula_by_left,
    sample_by_left,
    coverage_records_for_target,
    method_candidate_summary,
    pair_family_counts=None,
):
    pair_family_counts = pair_family_counts or {}
    rows = []
    for left_id in left_ids:
        pair_counts = pair_stats.get(left_id, Counter())
        target_candidates = method_candidates_by_left.get(left_id, [])
        target_coverage = coverage_records_for_target(left_id, coverage_index)
        target_coverage["independent_anchor_families"] = sorted(
            family for family, count in pair_family_counts.get(left_id, {}).items() if count
        )
        target_coverage["independent_anchor_pairs"] = sum(
            pair_family_counts.get(left_id, {}).values()
        )
        formulas = formula_by_left.get(left_id, [])
        next_sample = sample_by_left.get(left_id)
        count = candidate_counts.get(left_id, 0)
        independent_comparisons = pair_counts.get("independent_pairs", 0)
        independent_family_count = len(target_coverage["independent_anchor_families"])
        if formulas:
            status = "formula_candidate_needs_independent_review"
            priority = 0
        elif count >= 2:
            status = "multiple_method_candidates_need_discrimination"
            priority = 1
        elif count == 1:
            status = "single_method_candidate_needs_external_check"
            priority = 2
        elif pair_counts.get("unknown_lineage_skips", 0) and not independent_comparisons:
            status = "source_lineage_gap"
            priority = 3
        elif target_coverage["source_count"] == 0 and target_coverage["status"] == "available":
            status = "field_coverage_identity_unmapped"
            priority = 4
        elif independent_family_count == 0 and target_coverage["status"] == "available":
            status = "independent_source_coverage_gap"
            priority = 5
        elif pair_counts.get("insufficient_numeric_samples", 0):
            status = "joint_sample_coverage_gap"
            priority = 6
        elif independent_comparisons:
            status = "no_current_method_signal"
            priority = 7
        else:
            status = "no_eligible_comparison"
            priority = 8
        rows.append(
            {
                "left": left_id,
                "status": status,
                "priority": priority,
                "candidate_count": count,
                "pair_counts": dict(pair_counts),
                "top_candidates": [
                    method_candidate_summary(candidate) for candidate in target_candidates[:2]
                ],
                "formula_candidates": formulas,
                "next_sample": next_sample,
                "coverage": target_coverage,
            }
        )
    rows.sort(
        key=lambda item: (
            item["priority"],
            -item["candidate_count"],
            -len(item["coverage"]["independent_anchor_families"]),
            item["left"],
        )
    )
    summary = {
        "target_count": len(rows),
        "targets_with_method_candidates": sum(row["candidate_count"] > 0 for row in rows),
        "targets_without_method_candidates": sum(row["candidate_count"] == 0 for row in rows),
        "targets_with_multiple_candidates": sum(row["candidate_count"] > 1 for row in rows),
        "targets_with_formula_candidates": sum(bool(row["formula_candidates"]) for row in rows),
        "targets_with_next_sample": sum(
            isinstance(row.get("next_sample"), dict)
            and row["next_sample"].get("status") == "prioritize_recheck"
            for row in rows
        ),
        "targets_with_independent_anchor_coverage": sum(
            bool(row["coverage"]["independent_anchor_families"]) for row in rows
        ),
        "coverage_detail_status": coverage_index.get("summary", {}).get(
            "detail_status", "unavailable"
        ),
        "status_counts": dict(Counter(row["status"] for row in rows)),
    }
    return {"summary": summary, "targets": rows}


def build_source_coverage_report(
    store,
    verified,
    anchors,
    contract_anchors,
    official_contract_verified,
    official_contract_anchors,
    left_ids,
    right_ids,
    pair_evaluations_by_source,
    l1_relations,
    l1_contract_relations,
    l4_relations,
    method_candidate_inventory,
    norm_src_of,
    code_of,
):
    """Summarize observed window coverage and actual collision participation by runtime source."""
    rows = defaultdict(
        lambda: {
            "observed_fields": set(),
            "observed_field_values": 0,
            "observed_trading_dates": set(),
            "verified_fields": set(),
            "official_contract_verified_fields": set(),
            "official_contract_anchor_fields": set(),
            "independent_anchor_fields": set(),
            "contract_only_anchor_fields": set(),
            "cracking_target_fields": set(),
            "comparison_fields": set(),
            "L1_relations": 0,
            "L1_C_relations": 0,
            "L4_relations": 0,
            "method_candidate_pairs": 0,
        }
    )

    for fid, info in store.items():
        source = norm_src_of(fid)
        row = rows[source]
        row["observed_fields"].add(code_of(fid))
        values = info.get("vals", {})
        metadata = info.get("sample_meta", {})
        row["observed_field_values"] += len(values)
        for key in values:
            sample_meta = metadata.get(key, {}) if isinstance(metadata, dict) else {}
            if sample_meta.get("domain") == TRADING and sample_meta.get("as_of_date"):
                row["observed_trading_dates"].add(sample_meta["as_of_date"])

    def add_identities(identity_set, target_key):
        for source, code in identity_set:
            rows[source][target_key].add(code)

    add_identities(verified, "verified_fields")
    add_identities(official_contract_verified, "official_contract_verified_fields")
    add_identities(official_contract_anchors, "official_contract_anchor_fields")
    add_identities(anchors, "independent_anchor_fields")
    add_identities(contract_anchors, "contract_only_anchor_fields")
    for fid in left_ids:
        rows[norm_src_of(fid)]["cracking_target_fields"].add(code_of(fid))
    for fid in right_ids:
        rows[norm_src_of(fid)]["comparison_fields"].add(code_of(fid))

    relation_sets = (
        (l1_relations, "L1_relations"),
        (l1_contract_relations, "L1_C_relations"),
        (l4_relations, "L4_relations"),
    )
    for relations, key in relation_sets:
        for relation in relations:
            fields = {
                fid for fid in (relation.get("left"), relation.get("right")) if isinstance(fid, str)
            }
            for fid in fields:
                rows[norm_src_of(fid)][key] += 1
    for candidate in method_candidate_inventory:
        fields = {
            fid for fid in (candidate.get("left"), candidate.get("right")) if isinstance(fid, str)
        }
        for fid in fields:
            rows[norm_src_of(fid)]["method_candidate_pairs"] += 1

    output = []
    for source in sorted(rows):
        row = rows[source]
        pair_stats = pair_evaluations_by_source.get(source, {})
        output.append(
            {
                "source": source,
                "verified_field_count": len(row["verified_fields"]),
                "official_contract_verified_field_count": len(
                    row["official_contract_verified_fields"]
                ),
                "official_contract_anchor_field_count": len(row["official_contract_anchor_fields"]),
                "independent_anchor_field_count": len(row["independent_anchor_fields"]),
                "contract_only_anchor_field_count": len(row["contract_only_anchor_fields"]),
                "observed_window_field_count": len(row["observed_fields"]),
                "observed_window_field_value_count": row["observed_field_values"],
                "observed_window_trading_day_count": len(row["observed_trading_dates"]),
                "cracking_target_field_count": len(row["cracking_target_fields"]),
                "comparison_field_count": len(row["comparison_fields"]),
                "comparisons_as_target": pair_stats.get("as_target", 0),
                "comparisons_as_right_field": pair_stats.get("as_right_field", 0),
                "L1_C_anchor_comparisons": pair_stats.get("l1c_anchor", 0),
                "L1_relation_count": row["L1_relations"],
                "L1_C_relation_count": row["L1_C_relations"],
                "L4_relation_count": row["L4_relations"],
                "method_candidate_pair_count": row["method_candidate_pairs"],
            }
        )
    return output

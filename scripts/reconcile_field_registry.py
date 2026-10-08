#!/usr/bin/env python3
"""One-time, evidence-preserving migration to source-scoped field records.

The archived dictionary is an evidence source. The current registry is a second
evidence source. Disagreements are retained and excluded from verified anchors.
The active registry is written only with the explicit ``--apply`` option.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import sys
from collections import defaultdict
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
REGISTRY_PATH = os.path.join(REPO_ROOT, "docs", "field_verification", "field_registry.json")

for stream in (sys.stdout, sys.stderr):
    if stream is not None and hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, SCRIPT_DIR)
import extract_registry as er

VALID_STATUSES = {"verified", "unverified", "candidate", "disproved", "conflict"}


def _registry_source_pairs(registry: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    pairs: dict[tuple[str, str], dict[str, Any]] = {}
    for field in registry.get("fields", []):
        for source in field.get("sources", []):
            pairs[(source, field["code"])] = field
    return pairs


def _effective_status(
    ref: dict[str, Any] | None, current: dict[str, Any] | None, source_count: int
) -> tuple[str, str, list[str]]:
    reference_statuses = sorted(set((ref or {}).get("reference_statuses", [])))
    registry_status = (current or {}).get("status")
    evidence: list[str] = []

    if len(reference_statuses) > 1:
        return "conflict", "reference_status_conflict", reference_statuses

    reference_status = reference_statuses[0] if reference_statuses else None
    if reference_status and registry_status:
        if reference_status == registry_status:
            return reference_status, "matched", [reference_status]
        return "conflict", "status_conflict", [reference_status, registry_status]

    if reference_status:
        if reference_status in {"candidate", "disproved"}:
            return reference_status, "reference_only_nonverified", [reference_status]
        return "unverified", "reference_only_unconfirmed", [reference_status]

    if registry_status:
        evidence.append(registry_status)
        # A status on a multi-source aggregate cannot safely be assigned to each
        # source unless the archived source-specific row independently agrees.
        if source_count == 1:
            return registry_status, "registry_status_only_single_source", evidence
        return "unverified", "aggregate_status_scope_unresolved", evidence

    return "unverified", "status_missing", evidence


def reconcile_registry(
    current: dict[str, Any], extracted: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a new registry and item counts without mutating either input."""
    if current.get("source_fields"):
        raise ValueError("registry already has source_fields; this migration is one-time")

    ref_pairs = {
        (record["source"], record["code"]): record for record in extracted.get("source_fields", [])
    }
    current_pairs = _registry_source_pairs(current)
    identities = sorted(set(ref_pairs) | set(current_pairs))
    source_fields: list[dict[str, Any]] = []
    counts = CounterLike()

    for source, code in identities:
        reference = ref_pairs.get((source, code))
        aggregate = current_pairs.get((source, code))
        all_sources = (aggregate or {}).get("sources", [])
        status, resolution, status_evidence = _effective_status(
            reference, aggregate, len(all_sources)
        )
        source_field = {
            "source": source,
            "code": code,
            "identity": f"{source}::{code}",
            "path": code,
            "canonical": (reference or {}).get("canonical", ""),
            "meaning": (reference or {}).get("meaning", ""),
            "unit": (reference or {}).get("unit", ""),
            "section": (reference or {}).get("section", ""),
            "sections": (reference or {}).get("sections", []),
            "status": status,
            "status_resolution": resolution,
            "status_evidence": {
                "reference_statuses": (reference or {}).get("reference_statuses", []),
                "reference_status_raw": (reference or {}).get("status_raw_values", []),
                "registry_aggregate_status": (aggregate or {}).get("status"),
                "registry_aggregate_sources": all_sources,
                "values": status_evidence,
            },
            "reference_evidence": (reference or {}).get("evidence", []),
            "attribute_conflicts": (reference or {}).get("attribute_conflicts", {}),
            "registry_aggregate": (
                {
                    key: copy.deepcopy(aggregate.get(key))
                    for key in (
                        "code",
                        "sources",
                        "status",
                        "status_raw",
                        "canonical",
                        "meaning",
                        "unit",
                        "section",
                    )
                }
                if aggregate
                else None
            ),
        }
        if reference is None:
            source_field["status_resolution"] = "registry_only_source_pair"
            source_field["reference_evidence"] = []
            source_field["status"] = "unverified"
        source_fields.append(source_field)
        counts.add(source_field)

    source_fields.sort(key=lambda record: (record["source"], record["code"]))
    by_code: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in source_fields:
        by_code[record["code"]].append(record)

    fields: list[dict[str, Any]] = []
    for code in sorted(by_code):
        records = by_code[code]
        sources = sorted({record["source"] for record in records})
        statuses = {record["status"] for record in records}
        if "conflict" in statuses:
            aggregate_status = "conflict"
        elif len(statuses) == 1:
            aggregate_status = next(iter(statuses))
        else:
            aggregate_status = "unverified"

        def common_value(key: str) -> str:
            values = {record.get(key, "") for record in records if record.get(key, "")}
            return next(iter(values)) if len(values) == 1 else ""

        raw_statuses = {
            raw
            for record in records
            for raw in record["status_evidence"].get("reference_status_raw", [])
        }
        fields.append(
            {
                "code": code,
                "source": sources[0] if len(sources) == 1 else None,
                "sources": sources,
                "section": common_value("section"),
                "canonical": common_value("canonical"),
                "meaning": common_value("meaning"),
                "unit": common_value("unit"),
                "status_raw": next(iter(raw_statuses)) if len(raw_statuses) == 1 else "",
                "status": aggregate_status,
                "source_statuses": {record["source"]: record["status"] for record in records},
            }
        )

    migrated = copy.deepcopy(current)
    migrated["meta"] = copy.deepcopy(current.get("meta", {}))
    migrated["meta"].update(
        {
            "version": 2,
            "updated": dt.date.today().isoformat(),
            "source_of_truth": "field_registry.json",
            "generated_by": "scripts/reconcile_field_registry.py",
            "note": (
                "source_fields 是逐源完整路径权威记录；fields 是兼容聚合视图。"
                "状态冲突与历史证据保存在 source_fields，不得用于 verified 锚点。"
            ),
        }
    )
    migrated["fields"] = fields
    migrated["source_fields"] = source_fields
    migrated["meta"]["source_field_stats"] = counts.as_dict()
    report = counts.as_dict()
    report["reference_identity_count"] = len(ref_pairs)
    report["registry_identity_count"] = len(current_pairs)
    report["union_identity_count"] = len(source_fields)
    report["reference_only_count"] = len(set(ref_pairs) - set(current_pairs))
    report["registry_only_count"] = len(set(current_pairs) - set(ref_pairs))
    return migrated, report


class CounterLike:
    def __init__(self) -> None:
        self.values: dict[str, int] = defaultdict(int)

    def add(self, record: dict[str, Any]) -> None:
        self.values[record["status"]] += 1
        self.values[record["status_resolution"]] += 1

    def as_dict(self) -> dict[str, int]:
        return dict(sorted(self.values.items()))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="保留证据并迁移逐源字段注册记录")
    parser.add_argument("--registry", default=REGISTRY_PATH, help="作为迁移输入的 registry")
    parser.add_argument("--output", help="应用时写入的目标 registry；默认与输入相同")
    parser.add_argument("--preview-output", help="将提案写到独立预览文件，不改动 registry")
    parser.add_argument("--apply", action="store_true", help="写入 --registry 指定的文件")
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="明确允许替换已包含 source_fields 的目标文件（例如从备份重建）",
    )
    args = parser.parse_args(argv)
    if args.apply and args.preview_output:
        parser.error("--apply 与 --preview-output 不能同时使用")
    if args.replace_existing and not args.apply:
        parser.error("--replace-existing 只能与 --apply 同用")

    source_path = os.path.abspath(args.registry)
    target_path = os.path.abspath(args.output or args.registry)
    backup_dir = os.path.abspath(os.path.join(os.path.dirname(REGISTRY_PATH), "..", "backups"))
    if args.apply:
        try:
            if os.path.commonpath([backup_dir, target_path]) == backup_dir:
                parser.error("禁止将迁移输出写入 docs/backups；请保留原始备份")
        except ValueError:
            pass
    if args.preview_output:
        preview_path = os.path.abspath(args.preview_output)
        if preview_path in {source_path, target_path}:
            parser.error("--preview-output 必须与输入、输出 registry 分离")

    with open(source_path, encoding="utf-8") as handle:
        current = json.load(handle)
    extracted, _stats = er.extract()
    migrated, report = reconcile_registry(current, extracted)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.apply:
        if args.preview_output:
            os.makedirs(os.path.dirname(preview_path), exist_ok=True)
            with open(preview_path, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(migrated, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            print(f"Wrote proposed registry to {preview_path}")
        print("Dry run only. Re-run with --apply after reviewing these counts.")
        return 0

    if os.path.isfile(target_path):
        with open(target_path, encoding="utf-8") as handle:
            target_registry = json.load(handle)
        if target_registry.get("source_fields") and not args.replace_existing:
            parser.error("目标 registry 已含 source_fields；需显式传 --replace-existing")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    temporary = target_path + ".tmp"
    with open(temporary, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(migrated, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, target_path)
    print(f"Updated {target_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

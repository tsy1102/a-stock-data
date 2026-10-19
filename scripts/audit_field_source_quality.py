#!/usr/bin/env python3
"""Audit verified registry rows for missing or conflicting semantic metadata."""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter, defaultdict
from typing import Any

for stream in (sys.stdout, sys.stderr):
    if stream is not None and hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import field_registry_api as fra

ISSUE_LABELS = {
    "meaning_missing": "含义为空/占位",
    "meaning_conflict": "含义冲突",
    "unit_conflict": "单位冲突",
    "meaning_alignment_ambiguous": "含义分组未对齐",
    "unit_alignment_ambiguous": "单位分组未对齐",
}


def audit_registry(registry: dict[str, Any]) -> dict[str, Any]:
    records = fra.source_field_records(registry)
    by_source: dict[str, Counter] = defaultdict(Counter)
    flagged = []
    canonical_aliases = []
    for record in records:
        source = record["source"]
        status = str(record.get("status") or "unverified")
        counts = by_source[source]
        counts["total"] += 1
        counts[status] += 1
        if status != "verified":
            continue
        issues = fra.source_field_semantic_issues(record)
        if issues:
            counts["verified_metadata_blocked"] += 1
            for issue in issues:
                counts[issue] += 1
            flagged.append({"record": record, "issues": issues})
        else:
            counts["verified_metadata_ready"] += 1
        conflicts = record.get("attribute_conflicts")
        if isinstance(conflicts, dict) and conflicts.get("canonical"):
            counts["canonical_alias_variants"] += 1
            canonical_aliases.append(record)
    return {
        "record_count": len(records),
        "source_count": len(by_source),
        "by_source": by_source,
        "flagged_verified": flagged,
        "canonical_alias_variants": canonical_aliases,
    }


def _cell(value: Any) -> str:
    return str(value or "—").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def render_report(registry: dict[str, Any]) -> str:
    audit = audit_registry(registry)
    counts = Counter(
        record.get("status", "unverified") for record in registry.get("source_fields", [])
    )
    blocked = len(audit["flagged_verified"])
    ready = sum(item["verified_metadata_ready"] for item in audit["by_source"].values())
    updated = registry.get("meta", {}).get("updated", "unknown")
    lines = [
        "# 主字典逐源定义质量审计",
        "",
        "> 由 `scripts/audit_field_source_quality.py` 从 `field_registry.json.source_fields` 生成；本报告只检查状态与逐源元数据的一致性，不代替原始数据或上游契约核验。",
        "> `verified_metadata_ready` 仅表示含义文本及含义/单位属性可用于锚点审核；还须满足来源独立性、运行时路径精确匹配等碰撞规则。",
        "> 规范名别名差异单列展示，不单独阻止锚；含义缺失/占位、含义或单位冲突/分组无法对齐会阻止 verified 字段作为已知项或锚。",
        "",
        f"> Registry 日期 {updated}；来源身份 {audit['source_count']} 个；逐源路径 {audit['record_count']} 条；verified {counts['verified']} 条，其中元数据可用 {ready} 条、需复核 {blocked} 条。",
        "",
        "## 全来源统计",
        "",
        "| 来源身份 | 路径数 | verified | 元数据可用 | 缺义/占位 | 含义冲突 | 单位冲突 | 对齐歧义 | 规范名变体 | conflict 状态 |",
        "|:--|--:|--:|--:|--:|--:|--:|--:|--:|--:|",
    ]
    for source, stats in sorted(audit["by_source"].items()):
        ambiguous = stats["meaning_alignment_ambiguous"] + stats["unit_alignment_ambiguous"]
        lines.append(
            "| {source} | {total} | {verified} | {ready} | {missing} | {meaning} | {unit} | {ambiguous} | {canonical} | {conflict} |".format(
                source=_cell(source),
                total=stats["total"],
                verified=stats["verified"],
                ready=stats["verified_metadata_ready"],
                missing=stats["meaning_missing"],
                meaning=stats["meaning_conflict"],
                unit=stats["unit_conflict"],
                ambiguous=ambiguous,
                canonical=stats["canonical_alias_variants"],
                conflict=stats["conflict"],
            )
        )
    lines.extend(["", "## Verified 路径的语义元数据复核项", ""])
    if not audit["flagged_verified"]:
        lines.append("_没有需复核的 verified 记录。_")
    else:
        lines.extend(
            [
                "| 来源身份 | 完整 code path | 含义 | 单位 | 复核原因 |",
                "|:--|:--|:--|:--|:--|",
            ]
        )
        for item in audit["flagged_verified"]:
            record = item["record"]
            reasons = "；".join(ISSUE_LABELS.get(issue, issue) for issue in item["issues"])
            lines.append(
                f"| {_cell(record['source'])} | `{_cell(record['code'])}` | "
                f"{_cell(record.get('meaning'))} | {_cell(record.get('unit'))} | {reasons} |"
            )
    lines.extend(["", "## 规范名变体（不单独阻止锚）", ""])
    if not audit["canonical_alias_variants"]:
        lines.append("_没有规范名变体记录。_")
    else:
        lines.extend(
            [
                "| 来源身份 | 完整 code path | 规范名候选 | 含义 |",
                "|:--|:--|:--|:--|",
            ]
        )
        for record in audit["canonical_alias_variants"]:
            values = record.get("attribute_conflicts", {}).get("canonical", [])
            lines.append(
                f"| {_cell(record['source'])} | `{_cell(record['code'])}` | "
                f"{_cell(' / '.join(map(str, values)))} | {_cell(record.get('meaning'))} |"
            )
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        default=fra.REGISTRY,
        help="registry JSON path (defaults to the project registry)",
    )
    parser.add_argument("--output", help="write Markdown report to this path")
    args = parser.parse_args(argv)
    registry = fra.load_registry(args.registry)
    report = render_report(registry)
    if args.output:
        output = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(report)
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())

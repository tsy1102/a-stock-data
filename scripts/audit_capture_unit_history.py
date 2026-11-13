#!/usr/bin/env python3
"""Read-only longitudinal audit of composite capture-unit metadata."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date, datetime
import json
from pathlib import Path
import re
from statistics import median
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CAPTURE_ROOT = ROOT / "docs" / "field_verification"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.capture_catalog import CAPTURE_UNIT_CATALOG
from scripts.capture_retention import MIN_CAPTURE_DATE


def _archive_dates() -> list[tuple[date, Path]]:
    found = []
    for path in CAPTURE_ROOT.iterdir():
        if not path.is_dir() or not re.fullmatch(r"\d{8}", path.name):
            continue
        try:
            archive_date = datetime.strptime(path.name, "%Y%m%d").date()
        except ValueError:
            continue
        if archive_date >= MIN_CAPTURE_DATE:
            found.append((archive_date, path))
    return sorted(found)


def _expected_path_observed(expected: list[str], observed_paths: list[str]) -> bool:
    pattern = "^" + r"\.".join(r"[^.]+" if part == "*" else re.escape(part) for part in expected)
    matcher = re.compile(pattern + r"(?:$|\.)")
    return any(matcher.search(path) for path in observed_paths)


def _read_evidence() -> (
    tuple[dict[str, list[dict[str, Any]]], list[dict[str, str]], list[dict[str, str]]]
):
    by_unit: dict[str, list[dict[str, Any]]] = defaultdict(list)
    archive_metadata_issues = []
    unit_evidence_gaps = []
    for archive_date, directory in _archive_dates():
        meta_path = directory / "meta.json"
        if not meta_path.is_file():
            if any(directory.glob("raw_*.json")):
                archive_metadata_issues.append(
                    {"data_date": archive_date.isoformat(), "issue": "capture metadata missing"}
                )
            continue
        try:
            with meta_path.open(encoding="utf-8") as stream:
                metadata = json.load(stream)
        except (OSError, json.JSONDecodeError):
            archive_metadata_issues.append(
                {"data_date": archive_date.isoformat(), "issue": "capture metadata unreadable"}
            )
            continue
        records = metadata.get("capture_units") if isinstance(metadata, dict) else None
        if not isinstance(records, dict):
            if any(directory.glob("raw_*.json")):
                unit_evidence_gaps.append(
                    {
                        "data_date": archive_date.isoformat(),
                        "issue": (
                            "capture-unit evidence absent (archive predates this instrumentation "
                            "or metadata is incomplete)"
                        ),
                    }
                )
            continue
        for unit_id, value in records.items():
            if unit_id not in CAPTURE_UNIT_CATALOG or not isinstance(value, dict):
                continue
            record = dict(value)
            record["archive_data_date"] = archive_date.isoformat()
            by_unit[unit_id].append(record)
    for records in by_unit.values():
        records.sort(
            key=lambda item: (
                item.get("requested_data_date") or "",
                item["archive_data_date"],
            )
        )
    return by_unit, archive_metadata_issues, unit_evidence_gaps


def _unit_summary(unit_id: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    spec = CAPTURE_UNIT_CATALOG[unit_id]
    statuses = Counter(str(item.get("status") or "unknown") for item in records)
    attempted = [
        item
        for item in records
        if item.get("collector_invoked", item.get("request_attempted", False))
    ]
    requested_dates = sorted(
        {str(item["requested_data_date"]) for item in attempted if item.get("requested_data_date")}
    )
    explicit_source_dates = sorted(
        {str(item["source_as_of_date"]) for item in attempted if item.get("source_as_of_date")}
    )
    explicit_source_date_bases = sorted(
        {
            str(item["source_as_of_date_basis"])
            for item in attempted
            if item.get("source_as_of_date_basis")
        }
    )
    schema_fingerprints = sorted(
        {
            str(item["observed_path_fingerprint"])
            for item in attempted
            if item.get("observed_path_fingerprint")
        }
    )
    durations = []
    for item in attempted:
        duration = item.get("collector_duration_seconds", item.get("request_duration_seconds"))
        if isinstance(duration, (int, float)):
            durations.append(float(duration))
    logical_call_counts = [
        int(item["logical_call_count"])
        for item in attempted
        if isinstance(item.get("logical_call_count"), (int, float))
    ]
    network_count_statuses = Counter(
        str(item.get("network_request_count_status") or "not_recorded") for item in attempted
    )
    response_dates: dict[str, set[str]] = defaultdict(set)
    for record in attempted:
        observations = record.get("date_value_observations")
        if not isinstance(observations, dict):
            continue
        for path, values in observations.items():
            if not isinstance(values, list):
                continue
            response_dates[str(path)].update(str(value) for value in values)
    latest_per_date_key: dict[str, dict[str, Any]] = {}
    for record in attempted:
        date_key = str(
            record.get("source_as_of_date")
            or record.get("requested_data_date")
            or record["archive_data_date"]
        )
        latest_per_date_key[date_key] = record
    ordered_date_records = [latest_per_date_key[key] for key in sorted(latest_per_date_key)]
    payload_fingerprints = [item.get("payload_fingerprint") for item in ordered_date_records]
    identical_adjacent = sum(
        1
        for previous, current in zip(payload_fingerprints, payload_fingerprints[1:])
        if previous and previous == current
    )
    path_hashes: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for record in ordered_date_records:
        requested_date = str(
            record.get("source_as_of_date")
            or record.get("requested_data_date")
            or record["archive_data_date"]
        )
        values = record.get("field_value_fingerprints")
        if not isinstance(values, dict):
            continue
        for path, fingerprint in values.items():
            path_hashes[str(path)].append((requested_date, str(fingerprint)))

    field_changes: list[dict[str, Any]] = []
    for path, observations in path_hashes.items():
        changes = [
            current_date
            for (previous_date, previous_hash), (current_date, current_hash) in zip(
                observations, observations[1:]
            )
            if previous_hash != current_hash
        ]
        field_changes.append(
            {
                "path": path,
                "observations": len(observations),
                "changes": len(changes),
                "last_change_sample_date": changes[-1] if changes else None,
            }
        )
    field_changes.sort(key=lambda item: (-item["changes"], item["path"]))

    coverage = []
    for expected in spec.get("output_paths", []):
        presence = sum(
            1
            for record in attempted
            if _expected_path_observed(
                list(expected),
                (
                    record.get("observed_paths", [])
                    if isinstance(record.get("observed_paths"), list)
                    else []
                ),
            )
        )
        coverage.append(
            {
                "path": list(expected),
                "observed_attempts": presence,
                "attempts": len(attempted),
            }
        )

    return {
        "unit_id": unit_id,
        "collector": spec["collector"],
        "interface_id": spec["interface_id"],
        "provider_hint": spec.get("provider_hint", "unconfirmed"),
        "identity_status": spec.get("identity_status", "unconfirmed"),
        "data_domain": spec.get("data_domain", "unknown"),
        "source_date_contract": spec.get(
            "source_date_contract",
            "unconfirmed; inspect response date observations against the source contract",
        ),
        "archive_observations": len(records),
        "collector_invocation_observations": len(attempted),
        "statuses": dict(sorted(statuses.items())),
        "distinct_archive_dates": sorted({item["archive_data_date"] for item in attempted}),
        "distinct_requested_data_dates": requested_dates,
        "explicit_source_as_of_dates": explicit_source_dates,
        "explicit_source_date_bases": explicit_source_date_bases,
        "source_date_qualification": (
            "explicit_source_as_of_date_recorded"
            if explicit_source_dates
            else "not_recorded; requested_data_date is not proof of response date"
        ),
        "distinct_schema_fingerprints": len(schema_fingerprints),
        "collector_duration_seconds": {
            "min": min(durations) if durations else None,
            "median": median(durations) if durations else None,
            "max": max(durations) if durations else None,
        },
        "logical_call_count": {
            "total": sum(logical_call_counts),
            "min": min(logical_call_counts) if logical_call_counts else None,
            "median": median(logical_call_counts) if logical_call_counts else None,
            "max": max(logical_call_counts) if logical_call_counts else None,
        },
        "network_request_count_statuses": dict(sorted(network_count_statuses.items())),
        "response_date_shape_observations": {
            path: sorted(values)[:20] for path, values in sorted(response_dates.items())
        },
        "identical_adjacent_payloads": identical_adjacent,
        "catalog_output_path_presence": coverage,
        "field_value_change_date_basis": (
            "source_as_of_date when explicitly recorded; otherwise requested_data_date proxy"
        ),
        "field_value_change_observations": field_changes,
        "repeated_same_data_date_attempts": sum(
            max(0, int(item.get("same_data_date_attempts", 1) or 1) - 1) for item in records
        ),
        "max_attempts_in_one_data_date": max(
            (int(item.get("same_data_date_attempts", 1) or 1) for item in records),
            default=0,
        ),
        "raw_update_statuses": dict(
            sorted(
                Counter(
                    str(item.get("raw_update_status") or "not_selectively_updated")
                    for item in records
                ).items()
            )
        ),
        "interpretation_guard": (
            "Descriptive evidence only. Catalog output-path presence is not full registry-field "
            "parity. Status reflects the collector payload shape; adapters may normalize transport "
            "failures as empty output. Collector invocations and logical call counts are not wire "
            "request counts; cache hits and internal retries require lower-layer instrumentation. "
            "Do not infer "
            "source-date qualification, equivalence, replacement, cadence reduction, or retirement "
            "from these counts alone."
        ),
    }


def build_report(selected_units: set[str] | None = None) -> dict[str, Any]:
    histories, archive_metadata_issues, unit_evidence_gaps = _read_evidence()
    unit_ids = sorted(selected_units or set(CAPTURE_UNIT_CATALOG))
    unknown = sorted(set(unit_ids) - set(CAPTURE_UNIT_CATALOG))
    if unknown:
        raise ValueError("unknown capture units: " + ", ".join(unknown))
    summaries = {
        unit_id: _unit_summary(unit_id, histories.get(unit_id, [])) for unit_id in unit_ids
    }
    return {
        "schema_version": 1,
        "read_only": True,
        "retention_floor": MIN_CAPTURE_DATE.isoformat(),
        "capture_root": str(CAPTURE_ROOT),
        "archive_metadata_issues": archive_metadata_issues,
        "unit_evidence_gaps": unit_evidence_gaps,
        "units": summaries,
        "retirement_decision": "not_evaluated",
        "cadence_recommendation": "not_evaluated",
        "decision_evidence_requirements": [
            "Confirmed provider/interface identity and response contract.",
            "Complete and stable field-path coverage, including unique paths and missing fields.",
            "Multiple distinct, source-date-qualified observations; repeated runs of one data date count once.",
            "Field-level value stability/change rates interpreted with each field's temporal policy.",
            "Direct same-date overlap evidence for replacement, plus fallback and failure behavior.",
            "Refresh timing around market sessions, reporting releases, and event-driven updates.",
        ],
    }


def _render_markdown(report: dict[str, Any], top_fields: int) -> str:
    lines = [
        "# 复合采集接口历史证据审计",
        "",
        f"- 只读范围：`{report['capture_root']}`",
        f"- 最早读取日期：`{report['retention_floor']}`（不读取更早归档）",
        "- 用途：积累接口字段覆盖、结构/值变化、请求状态和日期线索；不自动改变采集频率或退役来源。",
        "",
        "| 接口单元 | 采集器调用记录 | 状态 | 请求数据日 | 响应日期已明确记录 | 结构版本 | 相邻同值负载 | 同日重跑 | 采集器耗时中位数 |",
        "|:---|---:|:---|---:|---:|---:|---:|---:|---:|",
    ]
    for unit_id, summary in report["units"].items():
        lines.append(
            "| `{}` | {} | {} | {} | {} | {} | {} | {} | {} |".format(
                unit_id,
                summary["collector_invocation_observations"],
                ", ".join(f"{key}:{value}" for key, value in summary["statuses"].items()) or "—",
                len(summary["distinct_requested_data_dates"]),
                len(summary["explicit_source_as_of_dates"]),
                summary["distinct_schema_fingerprints"],
                summary["identical_adjacent_payloads"],
                summary["repeated_same_data_date_attempts"],
                (
                    f"{summary['collector_duration_seconds']['median']:.3f}s"
                    if summary["collector_duration_seconds"]["median"] is not None
                    else "—"
                ),
            )
        )
    lines.extend(["", "## 目录输出路径出现情况", ""])
    for unit_id, summary in report["units"].items():
        lines.append(f"### `{unit_id}`")
        lines.append("")
        lines.append(f"- 日期契约线索：{summary['source_date_contract']}")
        duration = summary["collector_duration_seconds"].get("median")
        if duration is not None:
            lines.append(
                f"- 采集器调用耗时中位数：{duration:.3f} 秒（可能命中缓存，不代表网络耗时）"
            )
        logical_calls = summary["logical_call_count"]
        if logical_calls["median"] is not None:
            lines.append(
                f"- 逻辑适配器调用数：中位数 {logical_calls['median']}, "
                f"范围 {logical_calls['min']}–{logical_calls['max']}；不等同线上 HTTP 请求数"
            )
        raw_updates = {
            key: value
            for key, value in summary["raw_update_statuses"].items()
            if key != "not_selectively_updated"
        }
        if raw_updates:
            lines.append(
                "- 子接口 raw 更新处置："
                + ", ".join(f"{key}:{value}" for key, value in raw_updates.items())
            )
        if summary["response_date_shape_observations"]:
            lines.append("- 响应日期形状字段观察（字段名/值尚须按契约解释）：")
            for path, values in list(summary["response_date_shape_observations"].items())[:5]:
                lines.append(f"  - `{path}`：{', '.join(f'`{value}`' for value in values[:5])}")
        for item in summary["catalog_output_path_presence"]:
            lines.append(
                f"- `{'.'.join(item['path'])}`：{item['observed_attempts']}/{item['attempts']} 次尝试出现"
            )
        changed = [item for item in summary["field_value_change_observations"] if item["changes"]]
        if changed:
            lines.append("- 有变化字段（按请求数据日去重，最多显示 {} 条）：".format(top_fields))
            for item in changed[:top_fields]:
                lines.append(
                    f"  - `{item['path']}`：{item['changes']}/"
                    f"{max(item['observations'] - 1, 0)} 次相邻比较有变化；"
                    f"最近样本日期 `{item['last_change_sample_date']}`"
                )
        else:
            lines.append("- 尚无跨请求数据日的字段值变化记录。")
        lines.append("")
    lines.extend(
        [
            "## 归档元数据完整性",
            "",
            (
                f"检测到 {len(report['archive_metadata_issues'])} 个日期目录缺少或无法读取 `meta.json`。"
                if report["archive_metadata_issues"]
                else "未发现缺失或无法读取 `meta.json` 的归档目录。"
            ),
        ]
    )
    for issue in report["archive_metadata_issues"]:
        lines.append(f"- `{issue['data_date']}`：{issue['issue']}")
    lines.extend(
        [
            "",
            "## 接口单元证据基线",
            "",
            (
                f"{len(report['unit_evidence_gaps'])} 个保留期内归档没有接口单元证据；"
                "这些是新增采集元数据前的历史目录或不完整元数据，不会从 raw 反向伪造请求状态。"
                if report["unit_evidence_gaps"]
                else "所有可读取的保留期归档均包含接口单元证据。"
            ),
        ]
    )
    for gap in report["unit_evidence_gaps"]:
        lines.append(f"- `{gap['data_date']}`：{gap['issue']}")
    lines.extend(
        [
            "## 解释边界",
            "",
            "报告中的请求数据日不等于来源实际数据日。只有接口契约或响应字段明确给出来源日期，"
            "并核实其语义后，样本才可作为独立来源日期证据。相同来源数据日的重复运行不得重复计数。"
            "目录输出路径出现情况不等同于注册表完整字段覆盖；字段稳定性、路径结构和日期线索只是后续审阅材料。"
            "状态仅根据采集器输出判断，适配器可能把传输失败归一为空结果；调用次数也不代表实际 HTTP 请求数，"
            "需结合底层缓存、错误和网络计数。替代关系、降频或退役还需要确认字段全集、独有路径、来源身份、"
            "备用源与故障回退行为。",
            "",
            "**本报告不作降频、替代或退役结论。**",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="只读审计复合采集接口的历史证据")
    parser.add_argument("--unit", default="", help="只审计指定接口单元，逗号分隔")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出完整审计结果")
    parser.add_argument("--top-fields", type=int, default=20, help="Markdown 最多显示的变化字段数")
    args = parser.parse_args()
    unit_ids = {item.strip() for item in args.unit.split(",") if item.strip()} or None
    report = build_report(unit_ids)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(_render_markdown(report, max(args.top_fields, 0)))


if __name__ == "__main__":
    main()

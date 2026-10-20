"""Read-only summaries of AxData daily evidence and retired FTShare records."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if not isinstance(value, dict):
        return None, "JSON root is not an object"
    return value, None


def _date_key(value: Any) -> str | None:
    if value is None:
        return None
    match = re.match(r"^(\d{4})-?(\d{2})-?(\d{2})", str(value).strip())
    return "".join(match.groups()) if match else None


def _nonnegative_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return None


def _counter_fields(passive: dict[str, Any]) -> dict[str, dict[str, int]]:
    totals: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for lane in ("axdata_shortline_vs_eltdx", "kph_limit_up_history_vs_kpl_detail"):
        result = passive.get(lane)
        if not isinstance(result, dict):
            continue
        field_comparisons = result.get("field_comparisons")
        if not isinstance(field_comparisons, dict):
            continue
        for field, counts in field_comparisons.items():
            if not isinstance(counts, dict):
                continue
            for name in ("equal", "different", "both_null", "missing"):
                count = _nonnegative_int(counts.get(name, 0))
                if count is not None:
                    totals[f"{lane}:{field}"][name] += count
    return {field: dict(counts) for field, counts in sorted(totals.items())}


def _passive_lane_summary(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"status": "unavailable"}
    result: dict[str, Any] = {"status": value.get("status", "unknown")}
    for key in ("paired_stocks", "kph_rows", "kpl_rows", "target_trade_date"):
        if value.get(key) is not None:
            result[key] = value[key]
    field_comparisons = value.get("field_comparisons")
    if isinstance(field_comparisons, dict):
        clean_counts = {}
        for field, counts in sorted(field_comparisons.items()):
            if not isinstance(counts, dict):
                continue
            normalized = {}
            for name in ("equal", "different", "both_null", "missing"):
                count = _nonnegative_int(counts.get(name))
                if count is not None:
                    normalized[name] = count
            clean_counts[str(field)] = normalized
        result["field_comparisons"] = clean_counts
    return result


def _axdata_record(
    folder: Any, allowed_dates: set[str], diagnostics: list[str]
) -> dict[str, Any] | None:
    folder_path = Path(folder.path)
    artifact_path = folder_path / "axdata_validation.json"
    meta = folder.meta if isinstance(folder.meta, dict) else {}
    artifact = None
    full_artifact = False
    if artifact_path.is_file():
        artifact, error = _read_json(artifact_path)
        if error:
            diagnostics.append(f"{folder.name}/axdata_validation.json: {error}")
        else:
            full_artifact = True
    if artifact is None:
        summary = meta.get("axdata_validation")
        if isinstance(summary, dict):
            artifact = summary
    if not isinstance(artifact, dict):
        return None

    data_date = _date_key(artifact.get("data_date"))
    if data_date is None and getattr(folder, "market_date", None) is not None:
        data_date = folder.market_date.strftime("%Y%m%d")
    if data_date is None:
        diagnostics.append(f"{folder.name}: AxData 轮验记录缺少有效数据日")
        return None
    if data_date not in allowed_dates:
        return None

    passive = artifact.get("passive_evidence")
    if not isinstance(passive, dict):
        passive = {}
    probe = artifact.get("probe")
    if not isinstance(probe, dict):
        probe = {}
    try:
        request_count = max(0, int(probe.get("request_count", 0) or 0))
    except (TypeError, ValueError, OverflowError):
        request_count = 0
    comparison = probe.get("comparison")
    if not isinstance(comparison, dict):
        comparison = {}
    probe_fields = comparison.get("field_comparisons")
    if not isinstance(probe_fields, dict):
        probe_fields = {}
    probe_statuses = [
        item.get("status") for item in probe_fields.values() if isinstance(item, dict)
    ]
    raw_identity = probe.get("source_identity")
    identity_keys = (
        "status",
        "interface_id",
        "reference_source",
        "minimum_data_dates",
        "minimum_distinct_symbols",
        "minimum_symbols_per_date",
        "minimum_fields",
        "minimum_matched_symbols",
        "matched_data_dates",
        "matched_symbols",
        "evidence_dates",
        "value_equivalent_fields",
        "confirmed_fields",
        "semantic_unresolved_fields",
        "unresolved_fields",
        "last_probe_data_date",
        "last_mismatch",
        "next_recheck_in_data_dates",
        "recheck_samples_collected",
        "reason",
    )
    source_identity = (
        {key: raw_identity.get(key) for key in identity_keys if raw_identity.get(key) is not None}
        if isinstance(raw_identity, dict)
        else {}
    )
    raw_endpoint_identities = artifact.get("endpoint_identities")
    endpoint_identities = {}
    if isinstance(raw_endpoint_identities, dict):
        for interface_id, identity_record in raw_endpoint_identities.items():
            if not isinstance(identity_record, dict):
                continue
            endpoint_identities[str(interface_id)] = {
                key: identity_record.get(key)
                for key in identity_keys
                if identity_record.get(key) is not None
            }
    probe_comparison_summary = {
        "comparison_status": comparison.get("status"),
        "compared_fields": sum(
            status in {"equal", "different", "value_equal_with_dictionary_semantic_conflict"}
            for status in probe_statuses
        ),
        "equal_fields": sum(status == "equal" for status in probe_statuses),
        "different_fields": sum(status == "different" for status in probe_statuses),
        "semantic_conflict_fields": sum(
            status == "value_equal_with_dictionary_semantic_conflict" for status in probe_statuses
        ),
        "dictionary_dynamic_pe_status": (comparison.get("dictionary_dynamic_pe_check") or {}).get(
            "status"
        ),
    }
    queue = artifact.get("queue")
    if not isinstance(queue, dict):
        queue = {}
    capture_day = getattr(folder, "capture_date", None)
    evaluated_at = str(artifact.get("evaluated_at") or "")
    return {
        "data_date": data_date,
        "capture_date": capture_day.isoformat() if capture_day else folder.name,
        "capture_folder": folder.name,
        "status": artifact.get("status", "unknown"),
        "market_phase": artifact.get("market_phase"),
        "evaluated_at": evaluated_at,
        "artifact_kind": "full" if full_artifact else "meta_summary",
        "queue": {
            key: queue.get(key)
            for key in (
                "status",
                "interface_count",
                "field_occurrence_count",
                "field_occurrences_below_e3",
                "interface_relation_status_counts",
                "active_probe_allowlist",
                "other_candidates",
            )
            if queue.get(key) is not None
        },
        "passive_evidence": {
            lane: _passive_lane_summary(passive.get(lane))
            for lane in ("axdata_shortline_vs_eltdx", "kph_limit_up_history_vs_kpl_detail")
            if isinstance(passive.get(lane), dict)
        },
        "endpoint_identities": endpoint_identities,
        "probe": {
            key: probe.get(key)
            for key in ("status", "interface_id", "request_count", "comparison_status")
            if probe.get(key) is not None
        }
        | {"request_count": request_count}
        | {key: value for key, value in probe_comparison_summary.items() if value is not None}
        | ({"source_identity": source_identity} if source_identity else {}),
        "_rank": (
            int(full_artifact),
            int(request_count > 0),
            sum(
                1
                for lane in passive.values()
                if isinstance(lane, dict) and lane.get("status") not in {None, "not_run"}
            ),
            evaluated_at,
            folder.name,
        ),
        "_field_totals": _counter_fields(passive),
    }


def _ftshare_record(folder: Any, allowed_dates: set[str]) -> dict[str, Any] | None:
    meta = folder.meta if isinstance(folder.meta, dict) else {}
    result = meta.get("source_identity_reconciliation")
    if not isinstance(result, dict):
        return None
    if result.get("status") == "retired":
        return None
    endpoints = result.get("endpoints")
    if not isinstance(endpoints, dict):
        endpoints = {}
    data_date = _date_key(meta.get("data_date"))
    if data_date is None and getattr(folder, "market_date", None) is not None:
        data_date = folder.market_date.strftime("%Y%m%d")
    if data_date is None or data_date not in allowed_dates:
        return None
    endpoint_statuses = {
        str(code): str(item.get("status", "unknown"))
        for code, item in endpoints.items()
        if isinstance(item, dict)
    }
    return {
        "data_date": data_date,
        "capture_date": (
            folder.capture_date.isoformat()
            if getattr(folder, "capture_date", None)
            else folder.name
        ),
        "capture_folder": folder.name,
        "status": result.get("status", "unknown"),
        "endpoint_status_counts": dict(Counter(endpoint_statuses.values())),
        "endpoint_statuses": endpoint_statuses,
    }


def _aggregate_field_totals(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    totals: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for record in records:
        for field, counts in record.get("_field_totals", {}).items():
            for name, value in counts.items():
                totals[field][name] += value
    return {field: dict(counts) for field, counts in sorted(totals.items())}


def _select_per_date(
    records: list[dict[str, Any]], *, ranking_key: str
) -> tuple[list[dict[str, Any]], int]:
    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_date[record["data_date"]].append(record)
    selected = []
    duplicates = 0
    for data_date, same_date in sorted(by_date.items()):
        duplicates += max(0, len(same_date) - 1)
        best = max(same_date, key=lambda item: item[ranking_key])
        clean = {
            key: value
            for key, value in best.items()
            if not key.startswith("_") or key == "_field_totals"
        }
        clean["capture_folders"] = sorted({item["capture_folder"] for item in same_date})
        selected.append(clean)
    return selected, duplicates


def build_daily_aggregate_evidence(
    folders: Iterable[Any],
    trading_dates: Iterable[str],
    *,
    include_retired_sources: bool = False,
) -> dict[str, Any]:
    """Summarize AxData checks and optionally selected retired-source history."""
    allowed_dates = {key for value in trading_dates if (key := _date_key(value))}
    diagnostics: list[str] = []
    axdata_raw = []
    ftshare_raw = []
    for folder in folders:
        axdata = _axdata_record(folder, allowed_dates, diagnostics)
        if axdata is not None:
            axdata_raw.append(axdata)
        if include_retired_sources:
            ftshare = _ftshare_record(folder, allowed_dates)
            if ftshare is not None:
                ftshare_raw.append(ftshare)

    axdata_records, axdata_duplicates = _select_per_date(axdata_raw, ranking_key="_rank")
    ftshare_records, ftshare_duplicates = _select_per_date(
        ftshare_raw,
        ranking_key="capture_date",
    )
    passive_totals = _aggregate_field_totals(axdata_records)
    for record in axdata_records:
        record.pop("_field_totals", None)
    latest_queue: dict[str, Any] = next(
        (
            item["queue"]
            for item in reversed(axdata_records)
            if isinstance(item.get("queue"), dict) and item["queue"]
        ),
        {},
    )
    probe_statuses = Counter(
        str(item.get("probe", {}).get("status", "unknown")) for item in axdata_records
    )
    identity_statuses = Counter(
        str(item.get("probe", {}).get("source_identity", {}).get("status", "unknown"))
        for item in axdata_records
        if isinstance(item.get("probe", {}).get("source_identity"), dict)
    )
    endpoint_identity_statuses: dict[str, Counter[str]] = defaultdict(Counter)
    for record in axdata_records:
        identities = record.get("endpoint_identities")
        if not isinstance(identities, dict):
            continue
        for interface_id, identity_record in identities.items():
            if isinstance(identity_record, dict):
                endpoint_identity_statuses[str(interface_id)][
                    str(identity_record.get("status", "unknown"))
                ] += 1
    result = {
        "schema_version": 1,
        "policy": (
            "Read-only evidence; AxData aggregate/framework records are not independent field "
            "anchors and do not promote dictionary status. Retired FTShare records are included "
            "only for explicitly selected historical research."
        ),
        "axdata": {
            "status": "observed" if axdata_records else "no_daily_evidence",
            "data_date_count": len(axdata_records),
            "duplicate_capture_records_deduplicated": axdata_duplicates,
            "probe_request_count": sum(
                int(item.get("probe", {}).get("request_count", 0) or 0) for item in axdata_records
            ),
            "probe_status_counts": dict(probe_statuses),
            "identity_status_counts": dict(identity_statuses),
            "endpoint_identity_status_counts": {
                interface_id: dict(counts)
                for interface_id, counts in sorted(endpoint_identity_statuses.items())
            },
            "queue": latest_queue,
            "passive_field_comparison_totals": passive_totals,
            "daily_records": axdata_records,
        },
        "diagnostics": diagnostics[:100],
    }

    if include_retired_sources:
        result["ftshare"] = {
            "status": "observed" if ftshare_records else "no_historical_meta_evidence",
            "data_date_count": len(ftshare_records),
            "duplicate_capture_records_deduplicated": ftshare_duplicates,
            "daily_records": ftshare_records,
        }
    return result


def _cell(value: Any) -> str:
    return str(value if value not in (None, "") else "—").replace("|", "\\|").replace("\n", " ")


def append_daily_aggregate_report(report_md: str, evidence: dict[str, Any]) -> str:
    lines = [
        report_md.rstrip(),
        "",
        "## AxData 每日接口核验",
        "",
        "> 此处汇总采集目录已保存的本地证据，不发起网络请求、不改变注册表状态；"
        "AxData 是多源框架，不作为独立字段锚。",
        "",
    ]
    if not isinstance(evidence, dict):
        lines.append("_本轮没有可读取的每日轮验摘要。_")
        return "\n".join(lines) + "\n"

    raw_axdata = evidence.get("axdata")
    axdata = raw_axdata if isinstance(raw_axdata, dict) else {}
    raw_queue = axdata.get("queue")
    queue = raw_queue if isinstance(raw_queue, dict) else {}
    daily_axdata = axdata.get("daily_records")
    daily_axdata = daily_axdata if isinstance(daily_axdata, list) else []
    lines.extend(
        [
            "### AxData",
            "",
            (
                f"窗口内有 {axdata.get('data_date_count', 0)} 个唯一数据日的轮验记录；"
                f"重复目录合并 {axdata.get('duplicate_capture_records_deduplicated', 0)} 条。"
            ),
            (
                "静态接口队列："
                f"{queue.get('interface_count', '未知')} 个接口，"
                f"{queue.get('field_occurrence_count', '未知')} 个字段出现项，"
                f"低于 E3 的字段出现项 {queue.get('field_occurrences_below_e3', '未知')}；"
                f"当前主动探针白名单 `{', '.join(queue.get('active_probe_allowlist', [])) or '未知'}`。"
            ),
        ]
    )
    if queue.get("other_candidates"):
        lines.append(f"静态候选策略：{_cell(queue['other_candidates'])}。")
    lines.extend(
        [
            "",
            "| 数据日 | 轮验状态 | 探针状态 / 请求数 | 来源身份状态 | 短线配对 | KPH/KPL 配对 | 证据文件 |",
            "|:--|:--|:--|:--|--:|--:|:--|",
        ]
    )
    for item in daily_axdata:
        passive = item.get("passive_evidence") or {}
        shortline = passive.get("axdata_shortline_vs_eltdx") or {}
        kph_kpl = passive.get("kph_limit_up_history_vs_kpl_detail") or {}
        probe = item.get("probe") or {}
        raw_identity = probe.get("source_identity")
        identity = raw_identity if isinstance(raw_identity, dict) else {}
        identities = {"tencent_realtime_snapshot": identity}
        raw_endpoint_identities = item.get("endpoint_identities")
        if isinstance(raw_endpoint_identities, dict):
            identities.update(raw_endpoint_identities)
        identity_labels = []
        for interface_id, identity_record in sorted(identities.items()):
            if not isinstance(identity_record, dict) or not identity_record:
                continue
            identity_status = identity_record.get("status", "未记录")
            recheck_after = identity_record.get("next_recheck_in_data_dates")
            if recheck_after is not None:
                identity_status = f"{identity_status}（{recheck_after} 个数据日后复验）"
            unresolved_fields = identity_record.get("unresolved_fields")
            if isinstance(unresolved_fields, list) and unresolved_fields:
                identity_status = f"{identity_status}；待核 {len(unresolved_fields)} 字段"
            identity_labels.append(f"{interface_id}: {identity_status}")
        identity_status = "；".join(identity_labels) or "未记录"
        lines.append(
            f"| {item.get('data_date')} | {item.get('status')} | "
            f"{probe.get('status', '未请求')} / {probe.get('request_count', 0)} "
            f"(字段相同/不同 {probe.get('equal_fields', '—')}/{probe.get('different_fields', '—')}) | "
            f"{_cell(identity_status)} | {shortline.get('paired_stocks', '—')} | "
            f"{kph_kpl.get('paired_stocks', '—')} | "
            f"{item.get('artifact_kind', 'meta_summary')} |"
        )
    if not daily_axdata:
        lines.append("| — | 当前窗口没有 AxData 日轮验证据 | — | — | — | — | — |")
    lines.append("")
    raw_passive_totals = axdata.get("passive_field_comparison_totals")
    passive_totals = raw_passive_totals if isinstance(raw_passive_totals, dict) else {}
    differing_fields = [
        (key, counts)
        for key, counts in passive_totals.items()
        if isinstance(counts, dict) and counts.get("different", 0)
    ]
    if differing_fields:
        lines.append("被动逐字段比较中的差异计数（跨本窗口唯一数据日累加，不含原始值）：")
        lines.append("")
        lines.append("| 比较路径 | 相同 | 不同 | 缺失/双方空值 |")
        lines.append("|:--|--:|--:|--:|")
        for field, counts in sorted(
            differing_fields, key=lambda item: (-item[1].get("different", 0), item[0])
        )[:30]:
            lines.append(
                f"| `{_cell(field)}` | {counts.get('equal', 0)} | {counts.get('different', 0)} | "
                f"{counts.get('missing', 0) + counts.get('both_null', 0)} |"
            )
        if len(differing_fields) > 30:
            lines.append(f"\n其余 {len(differing_fields) - 30} 个差异路径保留在碰撞 JSON 报告中。")
        lines.append("")

    raw_ftshare = evidence.get("ftshare")
    ftshare = raw_ftshare if isinstance(raw_ftshare, dict) else {}
    daily_ftshare = ftshare.get("daily_records")
    daily_ftshare = daily_ftshare if isinstance(daily_ftshare, list) else []
    if "ftshare" in evidence:
        lines.extend(
            [
                "### FTShare 退役来源历史记录（显式历史研究）",
                "",
                (
                    f"窗口内保留 {ftshare.get('data_date_count', 0)} 个唯一数据日的旧元数据；"
                    f"重复目录合并 {ftshare.get('duplicate_capture_records_deduplicated', 0)} 条。"
                ),
                "",
                "| 数据日 | 历史状态 | 旧接口状态计数 |",
                "|:--|:--|:--|",
            ]
        )
        for item in daily_ftshare:
            status_counts = item.get("endpoint_status_counts") or {}
            counts_text = (
                ", ".join(f"{key}: {value}" for key, value in sorted(status_counts.items())) or "—"
            )
            lines.append(
                f"| {item.get('data_date')} | {item.get('status')} | {_cell(counts_text)} |"
            )
        if not daily_ftshare:
            lines.append("| — | 所选历史窗口没有 FTShare 旧元数据 | — |")
        lines.append("")
    if evidence.get("diagnostics"):
        lines.append("读取诊断：")
        lines.extend(f"- {_cell(message)}" for message in evidence["diagnostics"])
        lines.append("")
    return "\n".join(lines) + "\n"

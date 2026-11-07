"""Per-source field volatility and date-evidence policy for collision analysis.

Semantic stability and source-date assurance are independent. A stable field may
support a semantic cross-source match without proving which date its value is
valid for; volatile or unclassified fields need an explicit source/effective date
before their samples can contribute to L1 evidence.
"""

from __future__ import annotations

import json
import hashlib
import math
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, cast

from scripts import field_registry_api as FRA
from scripts import source_lineage_api as SLA

POLICY_PATH = (
    Path(__file__).resolve().parents[1] / "docs" / "field_verification" / "temporal_policy.json"
)
TEMPORAL_CLASSES = {
    "intraday_sensitive",
    "daily_market",
    "periodic_or_event",
    "slow_changing",
    "static_reference",
    "unclassified",
}
STABLE_SEMANTIC_CLASSES = {"slow_changing", "static_reference"}
SOURCE_CONFIRMED_DATE_ORIGINS = {
    "source_as_of",
    "record.event_date",
    "record.trade_date",
    "record.timestamp",
}
CROSS_SOURCE_INFERRED_DATE_ORIGIN = "cross_source_value_witness"
DATE_EVIDENCE_ORIGINS = SOURCE_CONFIRMED_DATE_ORIGINS | {CROSS_SOURCE_INFERRED_DATE_ORIGIN}
PERIODIC_EFFECTIVE_DATE_ORIGINS = {
    "record.effective_date",
    "record.report_period",
    "record.event_date",
}


class TemporalPolicyError(ValueError):
    """Raised when a temporal policy cannot be tied to exact registry identities."""


def load_policy(path: str | Path = POLICY_PATH) -> dict[str, Any]:
    """Read and validate the sidecar policy's basic shape."""
    try:
        policy = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TemporalPolicyError(f"读取时效策略失败: {exc}") from exc
    if not isinstance(policy, dict) or policy.get("schema_version") != 1:
        raise TemporalPolicyError("时效策略 schema_version 必须为 1")
    entries = policy.get("entries")
    if not isinstance(entries, list):
        raise TemporalPolicyError("时效策略 entries 必须为列表")
    seen: set[tuple[str, str]] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise TemporalPolicyError("时效策略 entries 只能包含对象")
        source, code = entry.get("source"), entry.get("code")
        temporal_class, reason = entry.get("class"), entry.get("reason")
        if (
            not isinstance(source, str)
            or not source.strip()
            or not isinstance(code, str)
            or not code.strip()
            or not isinstance(reason, str)
            or not reason.strip()
        ):
            raise TemporalPolicyError("每条时效策略必须有 source、完整 code 和 reason")
        if temporal_class not in TEMPORAL_CLASSES - {"unclassified"}:
            raise TemporalPolicyError(f"不支持的时效分类: {temporal_class!r}")
        identity = (source, code)
        if identity in seen:
            raise TemporalPolicyError(f"时效策略身份重复: {source}::{code}")
        seen.add(identity)
    witnesses = policy.get("row_timestamp_witnesses", [])
    if not isinstance(witnesses, list):
        raise TemporalPolicyError("row_timestamp_witnesses 必须为列表")
    witness_seen: set[tuple[str, str]] = set()
    for witness in witnesses:
        if not isinstance(witness, dict):
            raise TemporalPolicyError("row_timestamp_witnesses 只能包含对象")
        source, code = witness.get("source"), witness.get("code")
        reason = witness.get("reason")
        if (
            not isinstance(source, str)
            or not source.strip()
            or not isinstance(code, str)
            or not code.strip()
            or not isinstance(reason, str)
            or not reason.strip()
        ):
            raise TemporalPolicyError("每条行时间戳见证必须有 source、完整 code 和 reason")
        if witness.get("timestamp_format") != "unix_seconds":
            raise TemporalPolicyError("当前只支持 Unix 秒行时间戳见证")
        unit = witness.get("unit")
        meaning_contains = witness.get("meaning_contains")
        if not isinstance(unit, str) or not unit.strip():
            raise TemporalPolicyError("行时间戳见证必须有 unit")
        if not isinstance(meaning_contains, str) or not meaning_contains.strip():
            raise TemporalPolicyError("行时间戳见证必须有 meaning_contains")
        identity = (source, code)
        if identity in witness_seen:
            raise TemporalPolicyError(f"行时间戳见证身份重复: {source}::{code}")
        witness_seen.add(identity)
    value_witnesses = policy.get("cross_source_value_witnesses", [])
    if not isinstance(value_witnesses, list):
        raise TemporalPolicyError("cross_source_value_witnesses 必须为列表")
    value_witness_seen: set[tuple[str, str]] = set()
    required_value_witness_keys = {
        "source",
        "code",
        "runtime_paths",
        "witness_source",
        "witness_code",
        "witness_runtime_path",
        "evidence_file",
        "evidence_sha256",
        "reason",
        "thresholds",
    }
    required_thresholds = {
        "min_distinct_days",
        "min_pairs",
        "min_nonzero_pairs",
        "min_daily_pairs",
        "min_daily_nonzero_pairs",
        "min_unique_nonzero_values",
        "min_exact_ratio",
        "min_nonzero_exact_ratio",
        "min_daily_exact_ratio",
        "min_daily_nonzero_exact_ratio",
    }
    for witness in value_witnesses:
        if not isinstance(witness, dict):
            raise TemporalPolicyError("cross_source_value_witnesses 只能包含对象")
        missing = required_value_witness_keys - set(witness)
        if missing:
            raise TemporalPolicyError(f"跨源值日期见证缺少字段: {', '.join(sorted(missing))}")
        source, code = witness.get("source"), witness.get("code")
        witness_source, witness_code = (
            witness.get("witness_source"),
            witness.get("witness_code"),
        )
        if not all(
            isinstance(value, str) and value.strip()
            for value in (source, code, witness_source, witness_code)
        ):
            raise TemporalPolicyError("跨源值日期见证必须有完整 source/code 身份")
        identity = (cast(str, source), cast(str, code))
        if identity in value_witness_seen:
            raise TemporalPolicyError(f"跨源值日期见证目标重复: {source}::{code}")
        value_witness_seen.add(identity)
        runtime_paths = witness.get("runtime_paths")
        if (
            not isinstance(runtime_paths, list)
            or not runtime_paths
            or any(not isinstance(path, str) or not path.strip() for path in runtime_paths)
            or len(set(runtime_paths)) != len(runtime_paths)
        ):
            raise TemporalPolicyError("跨源值日期见证 runtime_paths 必须是非空且唯一的路径列表")
        if (
            not isinstance(witness.get("witness_runtime_path"), str)
            or not witness["witness_runtime_path"].strip()
        ):
            raise TemporalPolicyError("跨源值日期见证必须有 witness_runtime_path")
        evidence_file, evidence_sha256 = (
            witness.get("evidence_file"),
            witness.get("evidence_sha256"),
        )
        if not isinstance(evidence_file, str) or not evidence_file.strip():
            raise TemporalPolicyError("跨源值日期见证必须引用证据文件")
        if not isinstance(evidence_sha256, str) or not re.fullmatch(
            r"[0-9a-f]{64}", evidence_sha256
        ):
            raise TemporalPolicyError("跨源值日期见证必须有小写 SHA-256")
        reason = witness.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise TemporalPolicyError("跨源值日期见证必须说明依据和范围")
        thresholds = witness.get("thresholds")
        if not isinstance(thresholds, dict) or set(thresholds) != required_thresholds:
            raise TemporalPolicyError("跨源值日期见证 thresholds 缺失或包含未知项")
        for key in required_thresholds - {
            "min_exact_ratio",
            "min_nonzero_exact_ratio",
            "min_daily_exact_ratio",
            "min_daily_nonzero_exact_ratio",
        }:
            value = thresholds.get(key)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise TemporalPolicyError(f"跨源值日期见证阈值 {key} 必须为正整数")
        for key in required_thresholds & {
            "min_exact_ratio",
            "min_nonzero_exact_ratio",
            "min_daily_exact_ratio",
            "min_daily_nonzero_exact_ratio",
        }:
            value = thresholds.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 < value <= 1:
                raise TemporalPolicyError(f"跨源值日期见证阈值 {key} 必须位于 (0, 1]")
    return policy


def _registry_identity_index(
    registry: dict[str, Any],
) -> dict[tuple[str, str], dict[str, Any]]:
    records = FRA.source_field_records(registry)
    return {(record["source"], record["code"]): record for record in records}


def build_runtime_policy_index(
    policy: dict[str, Any],
    registry: dict[str, Any],
    lineage: dict[str, Any],
) -> dict[tuple[str, str], dict[str, Any]]:
    """Map exact registry identities to runtime (source alias, full path) keys."""
    records = _registry_identity_index(registry)
    runtime_index: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for entry in policy["entries"]:
        identity = (entry["source"], entry["code"])
        record = records.get(identity)
        if record is None:
            raise TemporalPolicyError(
                f"策略字段不在逐源注册表中: {entry['source']}::{entry['code']}"
            )
        expected_status = entry.get("registry_status")
        if expected_status and record.get("status") != expected_status:
            raise TemporalPolicyError(
                f"策略字段注册表状态变化: {entry['source']}::{entry['code']} "
                f"期望 {expected_status}，当前 {record.get('status')}"
            )
        aliases = SLA.runtime_aliases_for_source(entry["source"], lineage)
        if not aliases:
            raise TemporalPolicyError(f"策略来源没有运行时别名: {entry['source']}")
        resolved = dict(entry)
        resolved["registry_status"] = record.get("status")
        for alias in aliases:
            runtime_code = SLA.normalize_runtime_field_code(alias, entry["code"])
            runtime_index[(alias, runtime_code)].append(resolved)
    ambiguous = [key for key, values in runtime_index.items() if len(values) != 1]
    if ambiguous:
        alias, code = ambiguous[0]
        raise TemporalPolicyError(f"时效策略映射到多个逐源身份: {alias}::{code}")
    return {key: values[0] for key, values in runtime_index.items()}


def _runtime_code(fid: str, source: str) -> str | None:
    if fid.startswith(f"{source}."):
        return fid[len(source) + 1 :]
    if fid.startswith(f"{source}["):
        return fid[len(source) :]
    return None


def _policy_failure_summary(store: dict[str, dict[str, Any]], exc: Exception) -> dict[str, Any]:
    count = len(store)
    return {
        "status": "invalid",
        "policy_version": None,
        "classified_fields": 0,
        "unclassified_fields": count,
        "class_counts": {"unclassified": count},
        "diagnostics": [f"时效策略未生效，全部字段按 unclassified 处理: {exc}"],
    }


def _classify_runtime_field(
    fid: str, info: dict[str, Any], runtime_index: dict[tuple[str, str], dict[str, Any]]
) -> str:
    source = info.get("src")
    code = _runtime_code(fid, str(source or "")) if source else None
    if code is None:
        return "unclassified"
    alias = str(source)
    normalized = SLA.normalize_runtime_field_code(alias, code)
    entry = runtime_index.get((alias, normalized))
    if entry:
        info["temporal_policy_identity"] = {
            "source": entry["source"],
            "code": entry["code"],
        }
        return cast(str, entry["class"])
    return "unclassified"


def _runtime_timestamp_witness_index(
    policy: dict[str, Any],
    registry: dict[str, Any],
    lineage: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Resolve trusted row timestamps to exact runtime source aliases."""
    records = _registry_identity_index(registry)
    runtime_index: dict[str, dict[str, Any]] = {}
    for witness in policy.get("row_timestamp_witnesses", []):
        source, code = witness["source"], witness["code"]
        record = records.get((source, code))
        if record is None:
            raise TemporalPolicyError(f"行时间戳见证不在逐源注册表中: {source}::{code}")
        if record.get("status") != "verified":
            raise TemporalPolicyError(f"行时间戳见证字段未验证: {source}::{code}")
        if record.get("unit") != witness["unit"]:
            raise TemporalPolicyError(f"行时间戳见证单位变化: {source}::{code}")
        meaning = record.get("meaning")
        if not isinstance(meaning, str) or witness["meaning_contains"] not in meaning:
            raise TemporalPolicyError(f"行时间戳见证语义变化: {source}::{code}")
        aliases = SLA.runtime_aliases_for_source(source, lineage)
        if not aliases:
            raise TemporalPolicyError(f"行时间戳见证来源没有运行时别名: {source}")
        for alias in aliases:
            if alias in runtime_index:
                raise TemporalPolicyError(f"运行时来源存在多个行时间戳见证: {alias}")
            runtime_code = SLA.normalize_runtime_field_code(alias, code)
            runtime_index[alias] = {
                "field_id": f"{alias}.{runtime_code}",
                "source": source,
                "code": code,
                "timestamp_format": witness["timestamp_format"],
            }
    return runtime_index


def _timestamp_day(value: Any, timestamp_format: str) -> date | None:
    """Convert a validated Unix-seconds value to its China market date."""
    if timestamp_format != "unix_seconds" or isinstance(value, bool):
        return None
    if not isinstance(value, (str, int, float)):
        return None
    try:
        seconds = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(seconds) or not 946684800 <= seconds < 4102444800:
        return None
    try:
        china_timezone = timezone(timedelta(hours=8))
        return datetime.fromtimestamp(seconds, tz=china_timezone).date()
    except (OverflowError, OSError, ValueError):
        return None


def _compact_day(value: Any) -> str | None:
    if isinstance(value, date):
        return value.strftime("%Y%m%d")
    if not isinstance(value, str):
        return None
    compact = value.strip().replace("-", "")
    if len(compact) >= 8 and compact[:8].isdigit():
        return compact[:8]
    return None


def _runtime_field_id(alias: str, runtime_path: str) -> str:
    return f"{alias}{runtime_path}" if runtime_path.startswith("[") else f"{alias}.{runtime_path}"


def _cross_source_value_witness_index(
    policy: dict[str, Any],
    registry: dict[str, Any],
    lineage: dict[str, Any],
    policy_path: str | Path,
) -> list[dict[str, Any]]:
    """Resolve reviewed cross-source date witnesses and fail closed on drift."""
    records = _registry_identity_index(registry)
    resolved: list[dict[str, Any]] = []
    policy_dir = Path(policy_path).resolve().parent
    for witness in policy.get("cross_source_value_witnesses", []):
        source, code = witness["source"], witness["code"]
        witness_source, witness_code = witness["witness_source"], witness["witness_code"]
        target_record = records.get((source, code))
        anchor_record = records.get((witness_source, witness_code))
        if target_record is None:
            raise TemporalPolicyError(f"跨源值日期见证目标不在逐源注册表中: {source}::{code}")
        if target_record.get("status") in {"conflict", "disproved"}:
            raise TemporalPolicyError(f"跨源值日期见证目标处于阻断状态: {source}::{code}")
        if anchor_record is None or anchor_record.get("status") != "verified":
            raise TemporalPolicyError(
                f"跨源值日期见证锚字段未验证: {witness_source}::{witness_code}"
            )
        target_aliases = SLA.runtime_aliases_for_source(source, lineage)
        anchor_aliases = SLA.runtime_aliases_for_source(witness_source, lineage)
        if not target_aliases or not anchor_aliases:
            raise TemporalPolicyError("跨源值日期见证来源缺少运行时别名")
        for target_alias in target_aliases:
            target_family = SLA.runtime_family(target_alias, lineage)
            for anchor_alias in anchor_aliases:
                anchor_family = SLA.runtime_family(anchor_alias, lineage)
                if not target_family or not anchor_family or target_family == anchor_family:
                    raise TemporalPolicyError(
                        f"跨源值日期见证来源族不独立: {target_alias} / {anchor_alias}"
                    )
        evidence_path = policy_dir / witness["evidence_file"]
        try:
            evidence_sha256 = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        except OSError as exc:
            raise TemporalPolicyError(
                f"跨源值日期见证证据文件无法读取: {evidence_path}: {exc}"
            ) from exc
        if evidence_sha256 != witness["evidence_sha256"]:
            raise TemporalPolicyError(f"跨源值日期见证证据哈希变化: {witness['evidence_file']}")
        for target_alias in target_aliases:
            expected_target_code = SLA.normalize_runtime_field_code(target_alias, code)
            for runtime_path in witness["runtime_paths"]:
                normalized_target_path = SLA.normalize_runtime_field_code(
                    target_alias, runtime_path
                )
                if normalized_target_path != expected_target_code:
                    raise TemporalPolicyError(
                        f"跨源值日期见证运行路径不对应注册身份: {source}::{runtime_path}"
                    )
                for anchor_alias in anchor_aliases:
                    expected_anchor_code = SLA.normalize_runtime_field_code(
                        anchor_alias, witness_code
                    )
                    normalized_anchor_path = SLA.normalize_runtime_field_code(
                        anchor_alias, witness["witness_runtime_path"]
                    )
                    if normalized_anchor_path != expected_anchor_code:
                        raise TemporalPolicyError(
                            "跨源值日期见证锚运行路径不对应注册身份: "
                            f"{witness_source}::{witness['witness_runtime_path']}"
                        )
                    resolved.append(
                        {
                            **witness,
                            "target_field_id": _runtime_field_id(target_alias, runtime_path),
                            "witness_field_id": _runtime_field_id(
                                anchor_alias, witness["witness_runtime_path"]
                            ),
                            "target_alias": target_alias,
                            "witness_alias": anchor_alias,
                        }
                    )
    return resolved


def _numeric_decimal(value: Any) -> Decimal | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError):
        return None
    return result if result.is_finite() else None


def _apply_cross_source_value_witnesses(
    store: dict[str, dict[str, Any]],
    witnesses: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[str]]:
    """Infer dates only for exact rows after a strict multi-day numeric audit."""
    summaries: dict[str, Any] = {}
    diagnostics: list[str] = []
    for witness in witnesses:
        target_id = witness["target_field_id"]
        anchor_id = witness["witness_field_id"]
        target_info = store.get(target_id)
        anchor_info = store.get(anchor_id)
        summary_key = f"{target_id} <- {anchor_id}"
        if target_info is None or anchor_info is None:
            summaries[summary_key] = {
                "status": "missing_runtime_field",
                "target_field_id": target_id,
                "witness_field_id": anchor_id,
                "evidence_file": witness["evidence_file"],
                "evidence_sha256": witness["evidence_sha256"],
            }
            diagnostics.append(f"跨源值日期见证缺少样本字段: {summary_key}")
            continue
        if (
            target_info.get("src") != witness["target_alias"]
            or anchor_info.get("src") != witness["witness_alias"]
        ):
            raise TemporalPolicyError(f"跨源值日期见证运行时来源不匹配: {summary_key}")

        target_values = target_info.get("vals", {})
        anchor_values = anchor_info.get("vals", {})
        target_metadata = target_info.get("sample_meta", {})
        anchor_metadata = anchor_info.get("sample_meta", {})
        common_keys = target_values.keys() & anchor_values.keys()
        per_day: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"pairs": 0, "exact": 0, "nonzero_pairs": 0, "nonzero_exact": 0}
        )
        exact_keys: list[tuple[Any, Any]] = []
        nonzero_values: set[Decimal] = set()
        pairs = exact = nonzero_pairs = nonzero_exact = 0
        for key in common_keys:
            if (
                not isinstance(key, tuple)
                or len(key) != 2
                or not isinstance(key[1], str)
                or not key[1].startswith("T:")
            ):
                continue
            day = key[1][2:]
            target_meta = target_metadata.get(key)
            anchor_meta = anchor_metadata.get(key)
            if not isinstance(target_meta, dict) or not isinstance(anchor_meta, dict):
                continue
            if target_meta.get("phase") not in {"closed", "calendar"}:
                continue
            if anchor_meta.get("phase") not in {"closed", "calendar"}:
                continue
            if anchor_meta.get("as_of_date_origin") not in SOURCE_CONFIRMED_DATE_ORIGINS:
                continue
            if _compact_day(target_meta.get("as_of_date")) != day:
                continue
            if _compact_day(anchor_meta.get("as_of_date")) != day:
                continue
            left = _numeric_decimal(target_values[key])
            right = _numeric_decimal(anchor_values[key])
            if left is None or right is None:
                continue
            pairs += 1
            matched = left == right
            row = per_day[day]
            row["pairs"] += 1
            row["exact"] += int(matched)
            if left != 0 and right != 0:
                nonzero_pairs += 1
                nonzero_exact += int(matched)
                nonzero_values.add(left)
                row["nonzero_pairs"] += 1
                row["nonzero_exact"] += int(matched)
            if matched:
                exact += 1
                exact_keys.append((key, target_meta))

        thresholds = witness["thresholds"]
        daily_qualified = {
            day: row
            for day, row in per_day.items()
            if row["pairs"] >= thresholds["min_daily_pairs"]
            and row["nonzero_pairs"] >= thresholds["min_daily_nonzero_pairs"]
            and row["exact"] / row["pairs"] >= thresholds["min_daily_exact_ratio"]
            and row["nonzero_exact"] / row["nonzero_pairs"]
            >= thresholds["min_daily_nonzero_exact_ratio"]
        }
        exact_ratio = exact / pairs if pairs else 0.0
        nonzero_exact_ratio = nonzero_exact / nonzero_pairs if nonzero_pairs else 0.0
        thresholds_met = (
            len(daily_qualified) >= thresholds["min_distinct_days"]
            and pairs >= thresholds["min_pairs"]
            and nonzero_pairs >= thresholds["min_nonzero_pairs"]
            and len(nonzero_values) >= thresholds["min_unique_nonzero_values"]
            and exact_ratio >= thresholds["min_exact_ratio"]
            and nonzero_exact_ratio >= thresholds["min_nonzero_exact_ratio"]
        )
        if thresholds_met:
            for key, metadata in exact_keys:
                day = key[1][2:]
                if day not in daily_qualified:
                    continue
                metadata["as_of_date_origin"] = CROSS_SOURCE_INFERRED_DATE_ORIGIN
                metadata["cross_source_date_witness"] = {
                    "source": witness["witness_source"],
                    "code": witness["witness_code"],
                    "date": day,
                    "evidence_file": witness["evidence_file"],
                    "evidence_sha256": witness["evidence_sha256"],
                    "validated": True,
                }
        summaries[summary_key] = {
            "status": "thresholds_met" if thresholds_met else "thresholds_not_met",
            "target_field_id": target_id,
            "witness_field_id": anchor_id,
            "evidence_file": witness["evidence_file"],
            "evidence_sha256": witness["evidence_sha256"],
            "distinct_days": sorted(daily_qualified),
            "pairs": pairs,
            "exact": exact,
            "exact_ratio": round(exact_ratio, 6),
            "nonzero_pairs": nonzero_pairs,
            "nonzero_exact": nonzero_exact,
            "nonzero_exact_ratio": round(nonzero_exact_ratio, 6),
            "distinct_nonzero_values": len(nonzero_values),
            "promoted_samples": len(exact_keys) if thresholds_met else 0,
            "daily": {
                day: {
                    **row,
                    "exact_ratio": round(row["exact"] / row["pairs"], 6),
                    "nonzero_exact_ratio": (
                        round(row["nonzero_exact"] / row["nonzero_pairs"], 6)
                        if row["nonzero_pairs"]
                        else 0.0
                    ),
                    "qualified": day in daily_qualified,
                }
                for day, row in sorted(per_day.items())
            },
        }
        diagnostics.append(
            f"跨源值日期见证 {summary_key}: {exact}/{pairs} 精确，"
            f"{nonzero_exact}/{nonzero_pairs} 非零精确，"
            f"{len(daily_qualified)} 个交易日满足日阈值；"
            f"{'日期推断已启用' if thresholds_met else '未达到门槛'}"
        )
    return {"configured_witness_count": len(witnesses), "by_witness": summaries}, diagnostics


def _apply_row_timestamp_witnesses(
    store: dict[str, dict[str, Any]],
    policy: dict[str, Any],
    registry: dict[str, Any],
    lineage: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    """Confirm daily sample dates only when the same-row timestamp agrees."""
    witness_index = _runtime_timestamp_witness_index(policy, registry, lineage)
    by_source: dict[str, dict[str, int]] = {}
    diagnostics: list[str] = []
    for alias, witness in witness_index.items():
        witness_info = store.get(witness["field_id"])
        if witness_info is None:
            diagnostics.append(
                f"{alias}: 已配置行时间戳见证，但碰撞样本未包含 {witness['field_id']}"
            )
            by_source[witness["source"]] = {
                "witness_rows": 0,
                "date_confirmed_rows": 0,
                "date_mismatch_rows": 0,
                "invalid_timestamp_rows": 0,
                "field_samples_updated": 0,
            }
            continue

        witness_values = witness_info.get("vals", {})
        source_fields = [info for info in store.values() if info.get("src") == alias]
        counts = {
            "witness_rows": 0,
            "date_confirmed_rows": 0,
            "date_mismatch_rows": 0,
            "invalid_timestamp_rows": 0,
            "field_samples_updated": 0,
        }
        for key, raw_timestamp in witness_values.items():
            if (
                not isinstance(key, tuple)
                or len(key) != 2
                or not isinstance(key[1], str)
                or not key[1].startswith("T:")
            ):
                continue
            counts["witness_rows"] += 1
            timestamp_day = _timestamp_day(raw_timestamp, witness["timestamp_format"])
            if timestamp_day is None:
                counts["invalid_timestamp_rows"] += 1
                continue
            timestamp_text = timestamp_day.strftime("%Y%m%d")
            indexed_day = key[1][2:]
            row_matches = timestamp_text == indexed_day
            row_updates = 0
            for field_info in source_fields:
                values = field_info.get("vals", {})
                if key not in values:
                    continue
                metadata = field_info.get("sample_meta", {}).get(key)
                if not isinstance(metadata, dict):
                    continue
                metadata_day = _compact_day(metadata.get("as_of_date"))
                if metadata_day is None:
                    metadata_day = indexed_day
                matches = row_matches and timestamp_text == metadata_day
                metadata["row_timestamp_witness"] = {
                    "source": witness["source"],
                    "code": witness["code"],
                    "timestamp_date": timestamp_text,
                    "indexed_date": indexed_day,
                }
                if matches:
                    metadata["as_of_date_origin"] = "record.timestamp"
                    row_updates += 1
                else:
                    metadata["as_of_date_origin"] = "timestamp_mismatch"
                    metadata["row_timestamp_witness"]["metadata_date"] = metadata_day
                counts["field_samples_updated"] += 1
            if row_matches and row_updates:
                counts["date_confirmed_rows"] += 1
            else:
                counts["date_mismatch_rows"] += 1
        by_source[witness["source"]] = counts
        if counts["date_confirmed_rows"] or counts["date_mismatch_rows"]:
            diagnostics.append(
                f"{witness['source']} 行时间戳日期见证："
                f"确认 {counts['date_confirmed_rows']} 行，"
                f"日期冲突 {counts['date_mismatch_rows']} 行，"
                f"无效时间戳 {counts['invalid_timestamp_rows']} 行"
            )
    return {
        "configured_source_count": len(witness_index),
        "by_source": by_source,
    }, diagnostics


def apply_store_policies(
    store: dict[str, dict[str, Any]],
    *,
    policy_path: str | Path = POLICY_PATH,
    registry: dict[str, Any] | None = None,
    lineage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Annotate collision fields; on policy errors, fail closed to unclassified."""
    for info in store.values():
        info["temporal_class"] = "unclassified"
        info["temporal_policy_identity"] = None
    try:
        policy = load_policy(policy_path)
        registry = FRA.load_registry() if registry is None else registry
        lineage = SLA.load_source_lineage() if lineage is None else lineage
        runtime_index = build_runtime_policy_index(policy, registry, lineage)
        value_witness_index = _cross_source_value_witness_index(
            policy, registry, lineage, policy_path
        )
    except (OSError, TypeError, ValueError) as exc:
        return _policy_failure_summary(store, exc)

    counts: Counter[str] = Counter()
    for fid, info in store.items():
        temporal_class = _classify_runtime_field(fid, info, runtime_index)
        info["temporal_class"] = temporal_class
        counts.update((temporal_class,))

    timestamp_witness_summary, witness_diagnostics = _apply_row_timestamp_witnesses(
        store, policy, registry, lineage
    )
    value_witness_summary, value_witness_diagnostics = _apply_cross_source_value_witnesses(
        store, value_witness_index
    )

    return {
        "status": "ok",
        "policy_version": policy.get("policy_version"),
        "classified_fields": sum(count for key, count in counts.items() if key != "unclassified"),
        "unclassified_fields": counts["unclassified"],
        "class_counts": dict(sorted(counts.items())),
        "row_timestamp_witnesses": timestamp_witness_summary,
        "cross_source_value_witnesses": value_witness_summary,
        "diagnostics": witness_diagnostics + value_witness_diagnostics,
    }


def l1_date_eligible(info: dict[str, Any], sample_meta: dict[str, Any]) -> bool:
    """Require source dates for volatile fields; allow stable semantic evidence explicitly."""
    if sample_meta.get("phase") not in {"closed", "calendar"}:
        return False
    temporal_class = info.get("temporal_class", "unclassified")
    date_origin = sample_meta.get("as_of_date_origin")
    if temporal_class in STABLE_SEMANTIC_CLASSES:
        return True
    if temporal_class == "periodic_or_event":
        return sample_meta.get("value_effective_date_origin") in PERIODIC_EFFECTIVE_DATE_ORIGINS
    if date_origin in SOURCE_CONFIRMED_DATE_ORIGINS:
        return True
    cross_source_witness = sample_meta.get("cross_source_date_witness")
    return (
        date_origin == CROSS_SOURCE_INFERRED_DATE_ORIGIN
        and isinstance(cross_source_witness, dict)
        and cross_source_witness.get("validated") is True
        and isinstance(cross_source_witness.get("evidence_sha256"), str)
    )


def relation_date_evidence(
    left: dict[str, Any], right: dict[str, Any], selected_days: set[str] | list[str]
) -> dict[str, Any]:
    """Summarize date certainty separately from the semantic relation level."""
    selected = set(selected_days)

    def side(info: dict[str, Any]) -> dict[str, Any]:
        metadata = info.get("sample_meta", {})
        origins = Counter(
            (metadata.get(key, {}) or {}).get("as_of_date_origin", "missing")
            for key in info.get("vals", {})
            if key[1] in selected
        )
        origins = Counter({key: count for key, count in origins.items() if count})
        source_confirmed = bool(origins) and set(origins).issubset(SOURCE_CONFIRMED_DATE_ORIGINS)
        cross_source_inferred = (
            bool(origins)
            and CROSS_SOURCE_INFERRED_DATE_ORIGIN in origins
            and set(origins).issubset(DATE_EVIDENCE_ORIGINS)
        )
        stable = info.get("temporal_class", "unclassified") in STABLE_SEMANTIC_CLASSES
        if source_confirmed:
            status = "source_date_confirmed"
        elif cross_source_inferred:
            status = "cross_source_date_inferred"
        elif stable:
            status = "semantic_only_date_unconfirmed"
        else:
            status = "date_unconfirmed"
        return {
            "temporal_class": info.get("temporal_class", "unclassified"),
            "date_status": status,
            "date_origin_counts": dict(sorted(origins.items())),
        }

    left_evidence, right_evidence = side(left), side(right)
    sides = (left_evidence, right_evidence)
    if all(item["date_status"] == "source_date_confirmed" for item in sides):
        alignment = "source_dates_confirmed"
    elif all(
        item["date_status"] in {"source_date_confirmed", "cross_source_date_inferred"}
        for item in sides
    ):
        alignment = "cross_source_dates_inferred"
    elif all(
        item["date_status"] in {"source_date_confirmed", "semantic_only_date_unconfirmed"}
        for item in sides
    ):
        alignment = "semantic_only_date_unconfirmed"
    else:
        alignment = "date_unconfirmed"
    return {
        "alignment_status": alignment,
        "left": left_evidence,
        "right": right_evidence,
    }

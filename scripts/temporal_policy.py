"""Per-source field volatility and date-evidence policy for collision analysis.

Semantic stability and source-date assurance are independent. A stable field may
support a semantic cross-source match without proving which date its value is
valid for; volatile or unclassified fields need an explicit source/effective date
before their samples can contribute to L1 evidence.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
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
}
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
    except (OSError, TypeError, ValueError) as exc:
        return _policy_failure_summary(store, exc)

    counts: Counter[str] = Counter()
    for fid, info in store.items():
        temporal_class = _classify_runtime_field(fid, info, runtime_index)
        info["temporal_class"] = temporal_class
        counts.update((temporal_class,))

    return {
        "status": "ok",
        "policy_version": policy.get("policy_version"),
        "classified_fields": sum(count for key, count in counts.items() if key != "unclassified"),
        "unclassified_fields": counts["unclassified"],
        "class_counts": dict(sorted(counts.items())),
        "diagnostics": [],
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
    return date_origin in SOURCE_CONFIRMED_DATE_ORIGINS


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
        confirmed = bool(origins) and set(origins).issubset(SOURCE_CONFIRMED_DATE_ORIGINS)
        stable = info.get("temporal_class", "unclassified") in STABLE_SEMANTIC_CLASSES
        if confirmed:
            status = "source_date_confirmed"
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

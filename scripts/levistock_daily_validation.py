"""Record daily evidence for Levistock adapters from already captured raw files.

This module is intentionally offline: it never imports or calls Levistock/network APIs.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from importlib import metadata
from pathlib import Path
from typing import Any

METHODS: dict[str, dict[str, str]] = {
    "cls_market_emotion": {
        "adapter": "levistock.market_emotion_cls",
        "provider_family": "cls",
    },
    "kph_limit_ladder": {
        "adapter": "levistock.get_zttt",
        "provider_family": "kph",
    },
}
_IGNORED_KEYS = frozenset(
    {"scheme", "field_meta", "__source_meta__", "__error__", "__skipped__", "probe_trading_day"}
)


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, "capture_file_missing"
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"capture_file_unreadable: {type(exc).__name__}: {str(exc)[:160]}"
    if not isinstance(value, dict):
        return None, "capture_file_root_is_not_object"
    return value, None


def _date_key(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    for pattern in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(normalized, pattern).date().isoformat()
        except ValueError:
            continue
    return None


def _explicit_dates(value: Any) -> set[str]:
    date_keys = {
        "as_of_date",
        "asof_date",
        "data_date",
        "date",
        "Date",
        "trade_date",
        "tradeDate",
    }
    found: set[str] = set()
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            for key, child in current.items():
                if key in date_keys:
                    normalized = _date_key(child)
                    if normalized:
                        found.add(normalized)
                elif key not in _IGNORED_KEYS and isinstance(child, (dict, list)):
                    pending.append(child)
        elif isinstance(current, list):
            pending.extend(current)
    return found


def _populated_fields(value: Any, prefix: str = "") -> set[str]:
    fields: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in _IGNORED_KEYS:
                continue
            path = f"{prefix}.{key}" if prefix else key
            fields.update(_populated_fields(child, path))
    elif isinstance(value, list):
        for child in value:
            fields.update(_populated_fields(child, prefix))
    elif value is not None and value != "" and prefix:
        fields.add(prefix)
    return fields


def _sample_count(value: Any) -> int:
    if isinstance(value, list):
        return sum(1 for item in value if isinstance(item, dict) and _populated_fields(item))
    if isinstance(value, dict):
        for key in ("stocks", "records", "items"):
            rows = value.get(key)
            if isinstance(rows, dict):
                return sum(1 for row in rows.values() if _populated_fields(row))
            if isinstance(rows, list):
                return sum(1 for row in rows if isinstance(row, dict) and _populated_fields(row))
        return int(bool(_populated_fields(value)))
    return 0


def _method_evidence(
    method: str,
    raw: dict[str, Any] | None,
    expected_trade_date: str | None,
) -> dict[str, Any]:
    info = METHODS[method]
    payload = raw.get(method) if raw else None
    source_meta = raw.get("__source_meta__", {}) if raw else {}
    method_meta = source_meta.get(method, {}) if isinstance(source_meta, dict) else {}
    method_meta = method_meta if isinstance(method_meta, dict) else {}

    result: dict[str, Any] = {
        **info,
        "raw_file": "raw_market_sources.json",
        "payload_path": method,
        "status": "missing",
        "field_count": 0,
        "fields": [],
        "sample_count": 0,
        "date_status": "unavailable",
        "eligible_for_date_comparison": False,
        "eligible_for_request_aligned_comparison": False,
    }
    if payload is None:
        return result
    if isinstance(payload, dict) and "__error__" in payload:
        result.update(status="error", error=str(payload["__error__"])[:200])
        return result
    if isinstance(payload, dict) and "__skipped__" in payload:
        result.update(status="skipped", reason=str(payload["__skipped__"])[:200])
        return result

    fields = sorted(_populated_fields(payload))
    result["fields"] = fields
    result["field_count"] = len(fields)
    result["sample_count"] = _sample_count(payload)
    result["status"] = "observed" if fields else "empty"

    explicit_dates = _explicit_dates(payload)
    requested_date = _date_key(method_meta.get("requested_trade_date"))
    if len(explicit_dates) == 1:
        explicit_date = next(iter(explicit_dates))
        result["source_as_of_date"] = explicit_date
        if requested_date and requested_date != explicit_date:
            result["date_status"] = "request_response_mismatch"
        else:
            result["date_status"] = (
                "explicit_match" if expected_trade_date == explicit_date else "explicit_mismatch"
            )
    elif len(explicit_dates) > 1:
        result["date_status"] = "multiple_explicit_dates"
        result["source_dates"] = sorted(explicit_dates)
    elif requested_date:
        result["requested_trade_date"] = requested_date
        result["date_status"] = (
            "request_parameter_match"
            if requested_date == expected_trade_date
            else "request_parameter_mismatch"
        )
    else:
        result["date_status"] = "not_exposed"

    result["eligible_for_date_comparison"] = result["date_status"] == "explicit_match"
    result["eligible_for_request_aligned_comparison"] = result["date_status"] in {
        "explicit_match",
        "request_parameter_match",
    }
    return result


def _candidate_evidence(
    output_dir: Path,
    raw_market_sources: dict[str, Any] | None,
    expected_trade_date: str | None,
    candidate_probe_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_meta = raw_market_sources.get("__source_meta__", {}) if raw_market_sources else {}
    if isinstance(candidate_probe_meta, dict):
        probe_meta = candidate_probe_meta
    elif isinstance(source_meta, dict):
        probe_meta = source_meta.get("levistock_daily_candidate", {})
    else:
        probe_meta = {}
    probe_meta = probe_meta if isinstance(probe_meta, dict) else {}
    evidence: dict[str, Any] = {
        "status": probe_meta.get("status", "not_run"),
        "candidate_id": probe_meta.get("candidate_id"),
        "adapter": probe_meta.get("adapter"),
        "provider_family": probe_meta.get("provider_family"),
        "request_count": int(probe_meta.get("request_count", 0) or 0),
        "raw_file": "levistock_candidate_raw.json",
        "field_count": 0,
        "fields": [],
        "sample_count": 0,
        "date_status": "unavailable",
        "eligible_for_date_comparison": False,
        "eligible_for_request_aligned_comparison": False,
    }
    probe_file = output_dir / "levistock_candidate_raw.json"
    if not probe_file.exists():
        if probe_meta.get("reason"):
            evidence["reason"] = str(probe_meta["reason"])[:200]
        return evidence

    record, error = _read_json(probe_file)
    if error or not isinstance(record, dict):
        evidence.update(status="unreadable", error=error or "candidate_file_invalid")
        return evidence
    if _date_key(record.get("data_date")) != expected_trade_date:
        evidence.update(status="stale", reason="candidate_file_date_mismatch")
        return evidence

    probe_value = record.get("probe")
    probe = probe_value if isinstance(probe_value, dict) else {}
    payload = record.get("payload")
    raw_request_count = probe.get("request_count", evidence["request_count"])
    try:
        request_count = int(raw_request_count or 0)
    except (TypeError, ValueError, OverflowError):
        request_count = 0
    request_params = probe.get("request_params", {})
    evidence.update(
        status=probe.get("status", evidence["status"]),
        candidate_id=probe.get("candidate_id", evidence["candidate_id"]),
        adapter=probe.get("adapter", evidence["adapter"]),
        provider_family=probe.get("provider_family", evidence["provider_family"]),
        request_count=request_count,
        package_version=probe.get("package_version"),
        expected_package_version=probe.get("expected_package_version"),
        version_matches_requirement=probe.get("version_matches_requirement"),
        request_params=request_params if isinstance(request_params, dict) else {},
    )
    if isinstance(payload, dict) and "__error__" in payload:
        evidence["error"] = str(payload["__error__"])[:200]
        return evidence
    if isinstance(payload, dict) and "__skipped__" in payload:
        evidence["reason"] = str(payload["__skipped__"])[:200]
        return evidence

    fields = sorted(_populated_fields(payload))
    evidence["fields"] = fields
    evidence["field_count"] = len(fields)
    evidence["sample_count"] = _sample_count(payload)
    requested_date = _date_key((evidence.get("request_params") or {}).get("date"))
    explicit_dates = _explicit_dates(payload)
    if len(explicit_dates) == 1:
        explicit_date = next(iter(explicit_dates))
        evidence["source_as_of_date"] = explicit_date
        if requested_date and requested_date != explicit_date:
            evidence["date_status"] = "request_response_mismatch"
        else:
            evidence["date_status"] = (
                "explicit_match" if explicit_date == expected_trade_date else "explicit_mismatch"
            )
    elif len(explicit_dates) > 1:
        evidence["source_dates"] = sorted(explicit_dates)
        evidence["date_status"] = (
            "multi_date_window_contains_target"
            if expected_trade_date in explicit_dates
            else "multiple_explicit_dates"
        )
    elif requested_date:
        evidence["requested_trade_date"] = requested_date
        evidence["date_status"] = (
            "request_parameter_match"
            if requested_date == expected_trade_date
            else "request_parameter_mismatch"
        )
    else:
        evidence["date_status"] = "not_exposed"
    evidence["eligible_for_date_comparison"] = evidence["date_status"] == "explicit_match"
    evidence["eligible_for_request_aligned_comparison"] = evidence["date_status"] in {
        "explicit_match",
        "request_parameter_match",
    }
    return evidence


def run_levistock_daily_validation(
    *,
    out_dir: str | Path,
    data_date: Any,
    latest_completed_trade_date: Any,
    data_date_domain: str,
    market_phase: str,
    only: str | None,
    source_meta: dict[str, Any] | None = None,
    candidate_probe_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist per-method evidence from an existing daily capture, without network I/O."""
    output_dir = Path(out_dir)
    target_date = _date_key(data_date)
    latest_date = _date_key(latest_completed_trade_date)
    source_state = (source_meta or {}).get("market_sources", {})
    source_state = source_state if isinstance(source_state, dict) else {}
    eligible_reason = None
    selected = {name.strip() for name in (only or "").split(",") if name.strip()}
    if selected and "market_sources" not in selected:
        eligible_reason = "market_sources_not_selected"
    elif data_date_domain not in {"trading", "trading_day"}:
        eligible_reason = "capture_date_is_not_a_trading_day"
    elif market_phase != "closed":
        eligible_reason = "capture_is_not_a_closed_market_snapshot"
    elif target_date is None or latest_date is None or target_date != latest_date:
        eligible_reason = "capture_is_not_the_latest_completed_trading_day"

    raw, raw_error = _read_json(output_dir / "raw_market_sources.json")
    methods = {name: _method_evidence(name, raw, target_date) for name in METHODS}
    candidate = _candidate_evidence(output_dir, raw, target_date, candidate_probe_meta)
    observed_count = sum(item["status"] == "observed" for item in methods.values())
    if raw_error:
        status = "failed_open"
    elif eligible_reason:
        status = "not_eligible"
    elif observed_count == len(METHODS):
        status = "observed"
    elif observed_count:
        status = "partial"
    else:
        status = "failed"

    try:
        package_version = metadata.version("levistock")
    except metadata.PackageNotFoundError:
        package_version = None

    result: dict[str, Any] = {
        "schema_version": "1.0",
        "status": status,
        "data_date": target_date,
        "latest_completed_trade_date": latest_date,
        "data_date_domain": data_date_domain,
        "market_phase": market_phase,
        "evaluated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "eligibility_reason": eligible_reason,
        "client": {
            "package": "levistock",
            "version": package_version,
            "role": "multi_provider_adapter",
        },
        "source_capture_status": source_state.get("status", "unknown"),
        "methods": methods,
        "candidate_probe": candidate,
        "capture_probe_request_count": candidate.get("request_count", 0),
        "network_requests_added": 0,
    }
    if raw_error:
        result["raw_error"] = raw_error
    result_path = output_dir / "levistock_validation.json"
    try:
        result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        result["file"] = str(result_path)
    except OSError as exc:
        result["status"] = "failed_open"
        result["write_error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
    return result

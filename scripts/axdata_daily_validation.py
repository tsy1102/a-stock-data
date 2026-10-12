"""Bounded AxData evidence collection for the daily field capture.

This module never promotes dictionary status. It reuses the day's captured raw
files, then may add one Tencent snapshot request with an explicit quote time.
"""

from __future__ import annotations

from datetime import date, datetime
import json
import logging
import math
import os
from pathlib import Path
import re
import time
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = PROJECT_ROOT / ".tmp" / "axdata_daily_validation_state.json"
_STATIC_QUEUE_CACHE: Optional[dict[str, Any]] = None
EVIDENCE_FILENAME = "axdata_validation.json"
ACTIVE_INTERFACE = "tencent_realtime_snapshot"
ACTIVE_FAMILY = "tencent"
TENCENT_RAW_INDEXES = {
    "symbol": 2,
    "name": 1,
    "quote_time": 30,
    "last_price": 3,
    "pre_close": 4,
    "open": 5,
    "volume": 6,
    "change": 31,
    "change_pct": 32,
    "high": 33,
    "low": 34,
    "turnover_rate": 38,
    # AxData currently labels raw index 39 as pe_dynamic. The project registry
    # identifies index 39 as PE(TTM); the current dynamic PE is looked up below.
    "pe_dynamic": 39,
    "total_market_value": 44,
    "float_market_value": 45,
    "pb": 46,
    "limit_up_price": 47,
    "limit_down_price": 48,
    "amount": 57,
}
SHORTLINE_META_FIELDS = {"stats_date", "trade_date", "as_of_date", "exchange"}
KPH_KPL_FIELD_PAIRS = {
    "limit_time": "zt_time",
    "seal_amount": "max_seal",
    "seal_money": "seal_amount",
    "net_inflow": "main_inflow",
    "turnover": "amount",
    "turnover_rate": "turnover_real",
}


def _read_json(path: Path) -> Optional[dict[str, Any]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = STATE_PATH.parent / f"{path.stem}.{os.getpid()}.tmp"
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    os.replace(temporary, path)


def _date_key(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    match = re.match(r"^(\d{4})-?(\d{2})-?(\d{2})", text)
    if not match:
        return None
    return "-".join(match.groups())


def _number(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(str(value).strip().replace(",", ""))
    except (TypeError, ValueError):
        return None


def _value_equal(left: Any, right: Any) -> bool:
    left_number = _number(left)
    right_number = _number(right)
    if left_number is not None and right_number is not None:
        return math.isclose(left_number, right_number, rel_tol=1e-7, abs_tol=1e-8)
    return str(left).strip() == str(right).strip()


def _record_date(record: dict[str, Any]) -> Optional[str]:
    for key in ("stats_date", "trade_date", "as_of_date", "quote_time", "question_time"):
        value = _date_key(record.get(key))
        if value:
            return value
    return None


def _capture_stocks(out_dir: Path, source: str) -> dict[str, Any]:
    payload = _read_json(out_dir / f"raw_{source}.json") or {}
    stocks = payload.get("stocks")
    return stocks if isinstance(stocks, dict) else {}


def _shortline_passive_evidence(out_dir: Path, target_date: str) -> dict[str, Any]:
    axdata = _capture_stocks(out_dir, "axdata")
    eltdx = _capture_stocks(out_dir, "eltdx")
    field_stats: dict[str, dict[str, int]] = {}
    paired_codes: list[str] = []
    dates_ax: set[str] = set()
    dates_eltdx: set[str] = set()

    for code in sorted(set(axdata) & set(eltdx)):
        ax_row = axdata[code]
        el_row = eltdx[code]
        ax_record = ax_row.get("data") if isinstance(ax_row, dict) else None
        el_record = el_row.get("shortline") if isinstance(el_row, dict) else None
        if not isinstance(ax_record, dict) or not isinstance(el_record, dict):
            continue
        ax_date = _record_date(ax_record)
        el_date = _record_date(el_record)
        if ax_date:
            dates_ax.add(ax_date)
        if el_date:
            dates_eltdx.add(el_date)
        if ax_date != target_date or el_date != target_date:
            continue
        paired_codes.append(code)
        for field in sorted(set(ax_record) | set(el_record)):
            if field in SHORTLINE_META_FIELDS:
                continue
            counts = field_stats.setdefault(field, {"equal": 0, "different": 0, "both_null": 0})
            left, right = ax_record.get(field), el_record.get(field)
            if left is None and right is None:
                counts["both_null"] += 1
            elif left is not None and right is not None and _value_equal(left, right):
                counts["equal"] += 1
            else:
                counts["different"] += 1

    status = "compared" if paired_codes else "date_or_sample_unavailable"
    return {
        "status": status,
        "target_trade_date": target_date,
        "axdata_observed_dates": sorted(dates_ax),
        "eltdx_observed_dates": sorted(dates_eltdx),
        "paired_stocks": len(paired_codes),
        "paired_codes": paired_codes,
        "field_comparisons": field_stats,
        "requests_added": 0,
    }


def _kph_kpl_passive_evidence(out_dir: Path, target_date: str) -> dict[str, Any]:
    kph_payload = _read_json(out_dir / "raw_kph.json") or {}
    kpl_payload = _read_json(out_dir / "raw_kpl.json") or {}
    kph_date = _date_key(kph_payload.get("trade_date"))
    kpl_date = _date_key(kpl_payload.get("trade_date"))
    kph_stocks = kph_payload.get("stocks")
    kpl_stocks = kpl_payload.get("stocks")
    if (
        kph_date != target_date
        or kpl_date != target_date
        or not isinstance(kph_stocks, dict)
        or not isinstance(kpl_stocks, dict)
    ):
        return {
            "status": "date_or_sample_unavailable",
            "target_trade_date": target_date,
            "kph_trade_date": kph_date,
            "kpl_trade_date": kpl_date,
            "requests_added": 0,
        }

    stats = {field: {"equal": 0, "different": 0, "missing": 0} for field in KPH_KPL_FIELD_PAIRS}
    paired = sorted(
        code
        for code in set(kph_stocks) & set(kpl_stocks)
        if isinstance(kph_stocks[code], dict) and isinstance(kpl_stocks[code], dict)
    )
    for code in paired:
        kph_row, kpl_row = kph_stocks[code], kpl_stocks[code]
        for kph_field, kpl_field in KPH_KPL_FIELD_PAIRS.items():
            left, right = kph_row.get(kph_field), kpl_row.get(kpl_field)
            if left is None or right is None:
                stats[kph_field]["missing"] += 1
            elif _value_equal(left, right):
                stats[kph_field]["equal"] += 1
            else:
                stats[kph_field]["different"] += 1
    return {
        "status": "compared",
        "target_trade_date": target_date,
        "kph_trade_date": kph_date,
        "kpl_trade_date": kpl_date,
        "kph_rows": len(kph_stocks),
        "kpl_rows": len(kpl_stocks),
        "paired_stocks": len(paired),
        "field_comparisons": stats,
        "requests_added": 0,
    }


def _static_queue_summary() -> dict[str, Any]:
    global _STATIC_QUEUE_CACHE
    if _STATIC_QUEUE_CACHE is not None:
        return dict(_STATIC_QUEUE_CACHE)
    path = PROJECT_ROOT / "docs" / "axdata_interface_crosswalk.json"
    crosswalk = _read_json(path)
    interfaces = crosswalk.get("interfaces") if crosswalk else None
    if not isinstance(interfaces, list):
        return {"status": "unavailable", "reason": "AxData crosswalk missing or unreadable"}
    field_count = 0
    pending_evidence_count = 0
    interface_statuses: dict[str, int] = {}
    for interface in interfaces:
        if not isinstance(interface, dict):
            continue
        relation = interface.get("static_reconciliation") or {}
        status = relation.get("relation_status", "unknown")
        interface_statuses[status] = interface_statuses.get(status, 0) + 1
        fields = interface.get("fields")
        if not isinstance(fields, list):
            continue
        field_count += len(fields)
        pending_evidence_count += sum(
            1
            for field in fields
            if (field.get("static_reconciliation") or {}).get("evidence_level") != "E3"
        )
    _STATIC_QUEUE_CACHE = {
        "status": "ok",
        "interface_count": len(interfaces),
        "field_occurrence_count": field_count,
        "field_occurrences_below_e3": pending_evidence_count,
        "interface_relation_status_counts": interface_statuses,
        "active_probe_allowlist": [ACTIVE_INTERFACE],
        "other_candidates": "static review only until route, parameters, date basis, and request safety are approved",
    }
    return dict(_STATIC_QUEUE_CACHE)


def _safe_error(exc: Exception) -> str:
    message = str(exc).replace("\r", " ").replace("\n", " ")[:300]
    message = re.sub(r"(https?://[^?\s]+)\?[^\s]+", r"\1?<query-redacted>", message)
    return re.sub(
        r"(?i)(token|api[_-]?key|authorization|cookie)(\s*[:=]\s*)[^&\s,;]+",
        r"\1\2<redacted>",
        message,
    )


def _http_status(exc: Exception) -> Optional[int]:
    for value in (
        getattr(exc, "status_code", None),
        getattr(exc, "status", None),
        getattr(getattr(exc, "response", None), "status_code", None),
    ):
        if value is None:
            continue
        try:
            status = int(str(value))
            if status in {403, 429}:
                return status
        except (TypeError, ValueError):
            pass
    match = re.search(r"\b(403|429)\b", str(exc))
    return int(match.group(1)) if match else None


def _blocked_error(exc: Exception) -> bool:
    if _http_status(exc) in {403, 429}:
        return True
    return bool(re.search(r"blocked|banned|rate.?limit|封禁|限流|访问频繁", str(exc), re.I))


def _source_has_rate_limit(source_state: dict[str, Any]) -> bool:
    details = " ".join(
        str(source_state.get(key) or "") for key in ("error", "error_sample", "status")
    )
    return bool(
        re.search(r"\b403\b|\b429\b|blocked|banned|rate.?limit|封禁|限流|访问频繁", details, re.I)
    )


def _stock_code(value: Any) -> str:
    return re.sub(r"\D", "", str(value or ""))[-6:]


def _tencent_symbol(code: str) -> str:
    if code.startswith(("92", "8", "4", "43", "83", "87")):
        suffix = "BJ"
    elif code.startswith(("6", "9", "5")):
        suffix = "SH"
    else:
        suffix = "SZ"
    return f"{code}.{suffix}"


def _choose_code(
    pool: list[dict[str, Any]], project_rows: dict[str, Any], last_code: str
) -> Optional[str]:
    codes = []
    for item in pool:
        if not isinstance(item, dict):
            continue
        code = _stock_code(item.get("code"))
        row = project_rows.get(code)
        fields = row.get("fields") if isinstance(row, dict) else None
        if code and isinstance(fields, list) and len(fields) > max(TENCENT_RAW_INDEXES.values()):
            codes.append(code)
    codes = [code for code in codes if code and isinstance(project_rows.get(code), dict)]
    if not codes:
        return None
    try:
        next_index = (codes.index(last_code) + 1) % len(codes)
    except ValueError:
        next_index = 0
    return codes[next_index]


def _dynamic_pe_index() -> Optional[int]:
    path = PROJECT_ROOT / "docs" / "field_verification" / "field_registry.json"
    registry = _read_json(path) or {}
    matches = [
        row
        for row in registry.get("source_fields", [])
        if row.get("source") == "腾讯(qt.gtimg)" and "动态" in str(row.get("meaning", ""))
    ]
    if len(matches) != 1:
        return None
    match = re.fullmatch(r"\[(\d+)\]", str(matches[0].get("code", "")))
    return int(match.group(1)) if match else None


def _compare_tencent_record(
    record: dict[str, Any], project_fields: list[Any], target_date: str
) -> dict[str, Any]:
    ax_quote_time = str(record.get("quote_time") or "").strip()
    project_quote_time = str(project_fields[30]).strip() if len(project_fields) > 30 else ""
    quote_dates_match = (
        _date_key(ax_quote_time) == target_date
        and _date_key(project_quote_time) == target_date
        and ax_quote_time == project_quote_time
    )
    result: dict[str, Any] = {
        "status": "compared" if quote_dates_match else "not_same_dated_snapshot",
        "axdata_quote_time": ax_quote_time or None,
        "project_quote_time": project_quote_time or None,
        "axdata_quote_date": _date_key(ax_quote_time),
        "project_quote_date": _date_key(project_quote_time),
        "target_trade_date": target_date,
        "field_comparisons": {},
    }
    if not quote_dates_match:
        return result

    result["field_comparisons"] = _compare_tencent_fields(record, project_fields)
    dictionary_check = _compare_dictionary_dynamic_pe(record, project_fields)
    if dictionary_check is not None:
        result["dictionary_dynamic_pe_check"] = dictionary_check
    return result


def _compare_tencent_fields(record: dict[str, Any], project_fields: list[Any]) -> dict[str, Any]:
    comparisons: dict[str, Any] = {}
    for field, index in TENCENT_RAW_INDEXES.items():
        if index >= len(project_fields):
            comparisons[field] = {"status": "project_index_missing", "index": index}
            continue
        ax_value = record.get(field)
        project_value = project_fields[index]
        if field == "amount":
            ax_number = _number(ax_value)
            ax_value = ax_number / 10000 if ax_number is not None else ax_value
        equal = _value_equal(ax_value, project_value)
        field_status = "equal" if equal else "different"
        if field == "pe_dynamic":
            field_status = "value_equal_with_dictionary_semantic_conflict" if equal else "different"
        comparisons[field] = {
            "status": field_status,
            "project_raw_index": index,
            "axdata_value": record.get(field),
            "project_value": project_value,
            "normalization": (
                "AxData yuan / 10000 = Tencent raw ten-thousand yuan" if field == "amount" else None
            ),
        }
    return comparisons


def _compare_dictionary_dynamic_pe(
    record: dict[str, Any], project_fields: list[Any]
) -> Optional[dict[str, Any]]:
    dynamic_index = _dynamic_pe_index()
    if dynamic_index is None or dynamic_index >= len(project_fields):
        return None
    ax_pe = _number(record.get("pe_dynamic"))
    dynamic_pe = _number(project_fields[dynamic_index])
    return {
        "registry_raw_index": dynamic_index,
        "axdata_value": record.get("pe_dynamic"),
        "project_value": project_fields[dynamic_index],
        "status": (
            "equal"
            if ax_pe is not None
            and dynamic_pe is not None
            and math.isclose(ax_pe, dynamic_pe, rel_tol=1e-7, abs_tol=1e-8)
            else "different_or_missing"
        ),
        "note": "Value check only; does not change the dictionary or settle AxData field semantics.",
    }


def _request_records(interface: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    from stock_common.sc_datasource import get_axdata_records

    return get_axdata_records(interface, params=params)


def _eligible_reason(
    data_date: str,
    data_date_domain: str,
    market_phase: str,
    latest_completed_trade_date: str,
    only: str,
) -> Optional[str]:
    if only:
        return "partial_source_selection"
    if data_date_domain not in {"trading", "mixed"}:
        return "not_trading_date_capture"
    if market_phase != "closed":
        return "capture_not_marked_closed"
    if _date_key(data_date) != _date_key(latest_completed_trade_date):
        return "not_latest_completed_trade_date"
    return None


def _tencent_candidate(
    out_dir: Path, pool: list[dict[str, Any]], state: dict[str, Any]
) -> tuple[Optional[str], Optional[list[Any]], Optional[dict[str, Any]]]:
    project_rows = _capture_stocks(out_dir, "tencent")
    code = _choose_code(pool, project_rows, str(state.get("last_code") or ""))
    if code is None:
        return (
            None,
            None,
            {
                "status": "skipped",
                "reason": "no_successful_project_tencent_sample",
                "request_count": 0,
            },
        )

    project_row = project_rows[code]
    project_fields = project_row.get("fields") if isinstance(project_row, dict) else None
    if not isinstance(project_fields, list) or len(project_fields) <= max(
        TENCENT_RAW_INDEXES.values()
    ):
        return (
            None,
            None,
            {
                "status": "skipped",
                "reason": "project_tencent_record_incomplete",
                "code": code,
                "request_count": 0,
            },
        )
    return code, project_fields, None


def _mark_probe_started(data_date: str, code: str, state: dict[str, Any]) -> dict[str, Any]:
    state = dict(state)
    state["last_attempted_data_date"] = data_date
    state["last_interface"] = ACTIVE_INTERFACE
    state["last_code"] = code
    state["last_outcome"] = "request_started"
    _write_json(STATE_PATH, state)
    return state


def _handle_tencent_request_error(
    exc: Exception, code: str, collected_at: str, state: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    blocked = _blocked_error(exc)
    if blocked:
        state["blocked_families"] = sorted(set(state.get("blocked_families", [])) | {ACTIVE_FAMILY})
    state["last_outcome"] = "blocked_until_manual_review" if blocked else "request_error"
    state["last_error"] = _safe_error(exc)
    _write_json(STATE_PATH, state)
    return {
        "status": state["last_outcome"],
        "interface_id": ACTIVE_INTERFACE,
        "family": ACTIVE_FAMILY,
        "code": code,
        "request_count": 1,
        "collected_at": collected_at,
        "http_status": _http_status(exc),
        "error": _safe_error(exc),
    }, state


def _handle_unmatched_tencent_response(
    records: list[dict[str, Any]], code: str, collected_at: str, state: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    empty_count = int(state.get("empty_response_streak", 0)) + 1
    state["empty_response_streak"] = empty_count
    if empty_count >= 2:
        state["blocked_families"] = sorted(set(state.get("blocked_families", [])) | {ACTIVE_FAMILY})
        state["last_outcome"] = "blocked_until_manual_review"
    else:
        state["last_outcome"] = "empty_or_unmatched_response"
    _write_json(STATE_PATH, state)
    return {
        "status": state["last_outcome"],
        "interface_id": ACTIVE_INTERFACE,
        "family": ACTIVE_FAMILY,
        "code": code,
        "request_count": 1,
        "returned_records": len(records),
        "collected_at": collected_at,
    }, state


def _handle_matched_tencent_response(
    record: dict[str, Any],
    code: str,
    project_fields: list[Any],
    data_date: str,
    collected_at: str,
    state: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    state["empty_response_streak"] = 0
    state["last_outcome"] = "sampled"
    state.pop("last_error", None)
    _write_json(STATE_PATH, state)
    project_date = _date_key(project_fields[30]) if len(project_fields) > 30 else None
    return {
        "status": "sampled",
        "interface_id": ACTIVE_INTERFACE,
        "family": ACTIVE_FAMILY,
        "code": code,
        "request_count": 1,
        "params": {"code": [_tencent_symbol(code)]},
        "collected_at": collected_at,
        "source_as_of_date": _date_key(record.get("quote_time")),
        "source_date_domain": "trading_day_realtime_snapshot",
        "source_relation": "same-provider comparison against the project's raw Tencent quote",
        "project_raw_file": "raw_tencent.json",
        "field_mapping_basis": "AxData reconciliation E2 sample plus current Tencent raw index registry",
        "project_source_as_of_date": project_date,
        "comparison": _compare_tencent_record(record, project_fields, data_date),
        "project_sample": {"n_fields": len(project_fields), "fields": project_fields},
        "axdata_record": record,
    }, state


def _run_tencent_probe(
    data_date: str,
    out_dir: Path,
    pool: list[dict[str, Any]],
    state: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    code, project_fields, skip_result = _tencent_candidate(out_dir, pool, state)
    if skip_result is not None or code is None or project_fields is None:
        return skip_result or {"status": "skipped", "request_count": 0}, state

    state = _mark_probe_started(data_date, code, state)
    time.sleep(1.0)
    collected_at = datetime.now().astimezone().isoformat(timespec="seconds")
    try:
        records = _request_records(ACTIVE_INTERFACE, {"code": [_tencent_symbol(code)]})
    except Exception as exc:
        return _handle_tencent_request_error(exc, code, collected_at, state)

    matched = [
        row for row in records if _stock_code(row.get("symbol") or row.get("instrument_id")) == code
    ]
    if len(matched) != 1:
        return _handle_unmatched_tencent_response(records, code, collected_at, state)
    return _handle_matched_tencent_response(
        matched[0], code, project_fields, data_date, collected_at, state
    )


def _summary(evidence: dict[str, Any], path: Optional[Path] = None) -> dict[str, Any]:
    probe = evidence.get("probe") or {}
    comparison = probe.get("comparison") or {}
    field_results = comparison.get("field_comparisons") or {}
    field_statuses = [
        value.get("status") for value in field_results.values() if isinstance(value, dict)
    ]
    probe_summary = {
        key: probe.get(key)
        for key in ("status", "interface_id", "family", "code", "request_count", "error")
        if probe.get(key) is not None
    }
    if comparison:
        probe_summary.update(
            {
                "comparison_status": comparison.get("status"),
                "compared_fields": sum(
                    status
                    in {"equal", "different", "value_equal_with_dictionary_semantic_conflict"}
                    for status in field_statuses
                ),
                "equal_fields": sum(status == "equal" for status in field_statuses),
                "different_fields": sum(status == "different" for status in field_statuses),
                "semantic_conflict_fields": sum(
                    status == "value_equal_with_dictionary_semantic_conflict"
                    for status in field_statuses
                ),
                "dictionary_dynamic_pe_status": (
                    comparison.get("dictionary_dynamic_pe_check") or {}
                ).get("status"),
            }
        )
    return {
        "status": evidence.get("status"),
        "file": path.name if path else None,
        "data_date": evidence.get("data_date"),
        "probe": probe_summary,
        "passive_evidence": evidence.get("passive_evidence", {}),
        "queue": evidence.get("queue", {}),
    }


def _base_evidence(
    target_date: str,
    data_date_domain: str,
    market_phase: str,
    reason: Optional[str],
    output_dir: Path,
    queue: dict[str, Any],
    evaluated_at: datetime,
) -> dict[str, Any]:
    passive: dict[str, Any]
    if reason is None:
        passive = {
            "axdata_shortline_vs_eltdx": _shortline_passive_evidence(output_dir, target_date),
            "kph_limit_up_history_vs_kpl_detail": _kph_kpl_passive_evidence(
                output_dir, target_date
            ),
        }
    else:
        passive = {"status": "not_run", "reason": reason, "requests_added": 0}
    return {
        "schema_version": "1.0",
        "status": "not_eligible" if reason else "eligible",
        "data_date": target_date,
        "data_date_domain": data_date_domain,
        "market_phase": market_phase,
        "evaluated_at": evaluated_at.isoformat(timespec="seconds"),
        "eligibility_reason": reason,
        "queue": queue,
        "passive_evidence": passive,
        "probe": {"status": "not_run", "request_count": 0},
    }


def _set_probe_policy_skip(evidence: dict[str, Any], status: str, **details: Any) -> None:
    evidence["status"] = "probe_skipped"
    evidence["probe"] = {"status": status, "request_count": 0, **details}


def _probe_request_count(value: Any) -> int:
    if not isinstance(value, dict):
        return 0
    try:
        return int(value.get("request_count") or 0)
    except (TypeError, ValueError, OverflowError):
        return 0


def _apply_counterpart_gate(
    evidence: dict[str, Any], source_meta: Optional[dict[str, Any]], state: dict[str, Any]
) -> bool:
    source_state = (source_meta or {}).get("tencent") or {}
    if _source_has_rate_limit(source_state):
        state["blocked_families"] = sorted(set(state.get("blocked_families", [])) | {ACTIVE_FAMILY})
        state["last_outcome"] = "blocked_by_project_counterpart"
        _write_json(STATE_PATH, state)
        evidence["status"] = "blocked_until_manual_review"
        evidence["probe"] = {
            "status": "blocked_by_project_counterpart",
            "family": ACTIVE_FAMILY,
            "request_count": 0,
        }
        return False
    if source_state.get("status") in {"failed", "deferred", "unwired", "deprecated"}:
        _set_probe_policy_skip(
            evidence,
            "skipped_project_counterpart_failed",
            family=ACTIVE_FAMILY,
        )
        return False
    return True


def _apply_probe_policy(
    evidence: dict[str, Any],
    target_date: str,
    output_dir: Path,
    pool: list[dict[str, Any]],
    source_meta: Optional[dict[str, Any]],
) -> None:
    state = _read_json(STATE_PATH) or {}
    if _date_key(state.get("last_attempted_data_date")) == target_date:
        _set_probe_policy_skip(
            evidence,
            "attempt_already_made_for_data_date",
            interface_id=state.get("last_interface"),
            family=ACTIVE_FAMILY,
            code=state.get("last_code"),
        )
        return
    if ACTIVE_FAMILY in state.get("blocked_families", []):
        _set_probe_policy_skip(
            evidence,
            "blocked_until_manual_review",
            family=ACTIVE_FAMILY,
            reason="previous 403/429/ban or consecutive empty responses; clear local state only after independent recovery check",
        )
        return
    if not _apply_counterpart_gate(evidence, source_meta, state):
        return
    probe, _updated_state = _run_tencent_probe(target_date, output_dir, pool, state)
    evidence["probe"] = probe
    evidence["status"] = probe.get("status", "sampled")


def _create_daily_lock(target_date: str) -> Optional[Path]:
    lock_dir = STATE_PATH.parent
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / f"axdata_daily_validation_{target_date.replace('-', '')}.lock"
    try:
        descriptor = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        try:
            if time.time() - lock_path.stat().st_mtime <= 1800:
                return None
        except (FileNotFoundError, OSError):
            return None
        stale_path = lock_path.with_name(f"{lock_path.name}.stale.{os.getpid()}.{time.time_ns()}")
        try:
            # Rename is atomic, so concurrent reclaimers cannot both take the
            # stale lock and issue the same daily probe.
            os.rename(lock_path, stale_path)
        except (FileNotFoundError, FileExistsError, OSError):
            return None
        try:
            descriptor = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return None
        finally:
            try:
                stale_path.unlink()
            except FileNotFoundError:
                pass
            except OSError as exc:
                logging.getLogger(__name__).warning(
                    "Could not remove reclaimed AxData lock %s: %s", stale_path, exc
                )
    try:
        with os.fdopen(descriptor, "w", encoding="ascii") as stream:
            stream.write(f"pid={os.getpid()}\nstarted={time.time():.3f}\n")
    except OSError:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass
        raise
    return lock_path


def _remove_daily_lock(lock_path: Path) -> None:
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def _record_validation_error(
    evidence: dict[str, Any], evidence_path: Path, error: str
) -> dict[str, Any]:
    evidence["status"] = "validation_error"
    evidence["probe"] = {
        "status": "validation_error",
        "request_count": 0,
        "error": error,
    }
    try:
        _write_json(evidence_path, evidence)
    except OSError:
        pass
    return _summary(evidence, evidence_path if evidence_path.exists() else None)


def _validation_context(
    data_date: str,
    data_date_domain: str,
    market_phase: str,
    latest_completed_trade_date: str,
    only: str,
    out_dir: str | Path,
    now: Optional[datetime],
) -> tuple[str, Path, dict[str, Any], datetime, Optional[str]]:
    target_date = _date_key(data_date) or data_date
    output_dir = Path(out_dir)
    queue = _static_queue_summary()
    evaluated_at = now or datetime.now().astimezone()
    reason = _eligible_reason(
        target_date,
        data_date_domain,
        market_phase,
        latest_completed_trade_date,
        only,
    )
    return target_date, output_dir, queue, evaluated_at, reason


def _run_eligible_validation(
    evidence: dict[str, Any],
    target_date: str,
    output_dir: Path,
    pool: list[dict[str, Any]],
    source_meta: Optional[dict[str, Any]],
) -> dict[str, Any]:
    evidence_path = output_dir / EVIDENCE_FILENAME
    lock_path = _create_daily_lock(target_date)
    if lock_path is None:
        _set_probe_policy_skip(evidence, "another_run_holds_daily_lock")
        return _summary(evidence)
    try:
        _apply_probe_policy(evidence, target_date, output_dir, pool, source_meta)
        _write_json(evidence_path, evidence)
        return _summary(evidence, evidence_path)
    except Exception as exc:
        return _record_validation_error(evidence, evidence_path, _safe_error(exc))
    finally:
        _remove_daily_lock(lock_path)


def run_axdata_daily_validation(
    *,
    data_date: str,
    data_date_domain: str,
    market_phase: str,
    latest_completed_trade_date: str,
    only: str,
    out_dir: str | Path,
    pool: list[dict[str, Any]],
    source_meta: Optional[dict[str, Any]] = None,
    now: Optional[datetime] = None,
) -> dict[str, Any]:
    """Summarize passive evidence and run at most one eligible AxData probe."""
    target_date, output_dir, queue, evaluated_at, reason = _validation_context(
        data_date,
        data_date_domain,
        market_phase,
        latest_completed_trade_date,
        only,
        out_dir,
        now,
    )
    evidence_path = output_dir / EVIDENCE_FILENAME
    existing = _read_json(evidence_path) if evidence_path.exists() else None
    normalized_target_date = _date_key(target_date)
    if (
        existing is not None
        and normalized_target_date is not None
        and _date_key(existing.get("data_date")) == normalized_target_date
    ):
        state = _read_json(STATE_PATH) or {}
        request_already_made = _probe_request_count(existing.get("probe")) > 0 or (
            _date_key(state.get("last_attempted_data_date")) == normalized_target_date
        )
        if request_already_made:
            existing["status"] = "already_recorded"
            existing["queue"] = queue
            return _summary(existing, evidence_path)

    evidence = _base_evidence(
        target_date,
        data_date_domain,
        market_phase,
        reason,
        output_dir,
        queue,
        evaluated_at,
    )
    if reason:
        return _summary(evidence)
    return _run_eligible_validation(evidence, target_date, output_dir, pool, source_meta)

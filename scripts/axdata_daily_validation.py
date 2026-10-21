"""Bounded AxData evidence collection for the daily field capture.

This module never promotes dictionary status. It reuses the day's captured raw
files, then may add one Tencent snapshot request with an explicit quote time.
"""

from __future__ import annotations

from datetime import datetime
import hashlib
from importlib.metadata import PackageNotFoundError, version as package_version
import json
import logging
import math
import os
from pathlib import Path
import re
import time
from typing import Any, Optional

from scripts.axdata_crosswalk_summary import read_summary

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
IDENTITY_MIN_CAPTURE_DATES = 3
IDENTITY_MIN_DISTINCT_SYMBOLS = 3
IDENTITY_MIN_INFORMATION_FIELDS = 5
IDENTITY_RECHECK_DATA_DATES = 20
IDENTITY_VALUE_MATCH_STATUSES = {"equal", "value_equal_with_dictionary_semantic_conflict"}
IDENTITY_INFORMATION_FIELDS = frozenset(TENCENT_RAW_INDEXES) - {
    "symbol",
    "name",
    "quote_time",
}
IDENTITY_REDUNDANT_STATUSES = {"partially_redundant", "operationally_redundant"}
SHORTLINE_META_FIELDS = {"stats_date", "trade_date", "as_of_date", "exchange"}
KPH_KPL_FIELD_PAIRS = {
    "limit_time": "zt_time",
    "seal_amount": "max_seal",
    "seal_money": "seal_amount",
    "net_inflow": "main_inflow",
    "turnover": "amount",
    "turnover_rate": "turnover_real",
}
CAPTURE_SHORTLINE_META_FIELDS = SHORTLINE_META_FIELDS | {
    "code",
    "symbol",
    "name",
    "quote_time",
    "question_time",
    "update_time",
    "source",
}
CAPTURE_IDENTITY_MIN_DATES = 3
CAPTURE_IDENTITY_MIN_SYMBOLS_PER_DATE = 18
CAPTURE_IDENTITY_MIN_FIELDS = 5
CAPTURE_IDENTITY_RECHECK_DATES = 20
CAPTURE_ENDPOINTS = {
    "stock_shortline_indicators_tdx": {
        "source": "axdata",
        "reference_source": "eltdx",
        "source_aliases": ["axdata"],
        "contract": {
            "adapter": "stock_common.get_shortline_indicators_result",
            "reference_path": "eltdx.stocks.*.shortline",
            "meta_fields": sorted(SHORTLINE_META_FIELDS),
        },
    },
    "kph_limit_up_history": {
        "source": "kph",
        "reference_source": "kpl",
        "source_aliases": ["kph"],
        "contract": {
            "adapter": "stock_common.sc_datasource.get_axdata_records",
            "reference_path": "kpl.stocks.*",
            "field_pairs": KPH_KPL_FIELD_PAIRS,
        },
    },
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


def _is_trading_date(value: Optional[str]) -> bool:
    date_key = _date_key(value)
    if date_key is None:
        return False
    try:
        parsed = datetime.strptime(re.sub(r"\D", "", date_key)[:8], "%Y%m%d").date()
    except ValueError:
        return False
    try:
        from scripts.collision_dates import is_trading_session
    except ModuleNotFoundError:
        from collision_dates import is_trading_session  # type: ignore[no-redef]
    return bool(is_trading_session(parsed))


def _capture_stocks(out_dir: Path, source: str) -> dict[str, Any]:
    payload = _read_json(out_dir / f"raw_{source}.json") or {}
    stocks = payload.get("stocks")
    return stocks if isinstance(stocks, dict) else {}


def _capture_identity_contract_fingerprint(interface_id: str) -> str:
    endpoint = CAPTURE_ENDPOINTS[interface_id]
    try:
        installed_axdata_version = package_version("axdata")
    except PackageNotFoundError:
        installed_axdata_version = "not_installed"
    contract = {
        "interface_id": interface_id,
        "axdata_package_version": installed_axdata_version,
        "source": endpoint["source"],
        "reference_source": endpoint["reference_source"],
        "contract": endpoint["contract"],
        "minimum_data_dates": CAPTURE_IDENTITY_MIN_DATES,
        "minimum_symbols_per_date": CAPTURE_IDENTITY_MIN_SYMBOLS_PER_DATE,
        "minimum_fields": CAPTURE_IDENTITY_MIN_FIELDS,
        "recheck_data_dates": CAPTURE_IDENTITY_RECHECK_DATES,
    }
    payload = json.dumps(contract, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _new_capture_identity(interface_id: str, reason: str) -> dict[str, Any]:
    endpoint = CAPTURE_ENDPOINTS[interface_id]
    return {
        "status": "observing",
        "interface_id": interface_id,
        "reference_source": endpoint["reference_source"],
        "contract_fingerprint": _capture_identity_contract_fingerprint(interface_id),
        "schema_fingerprint": None,
        "samples": [],
        "recheck_samples": [],
        "evidence_dates": [],
        "confirmed_fields": [],
        "unresolved_fields": [],
        "last_probe_data_date": None,
        "last_counted_data_date": None,
        "eligible_data_dates_since_probe": 0,
        "reason": reason,
    }


def _load_validation_state() -> tuple[Optional[dict[str, Any]], Optional[str]]:
    if not STATE_PATH.exists():
        return {}, None
    state = _read_json(STATE_PATH)
    if state is None:
        return None, "local AxData state is unreadable; manual review is required"
    return state, None


def _capture_identity_state(
    state: dict[str, Any], interface_id: str
) -> tuple[dict[str, Any], bool]:
    identities = state.get("capture_endpoint_identities")
    if not isinstance(identities, dict):
        identities = {}
        state["capture_endpoint_identities"] = identities
    current = identities.get(interface_id)
    fingerprint = _capture_identity_contract_fingerprint(interface_id)
    if isinstance(current, dict) and current.get("contract_fingerprint") == fingerprint:
        return current, False
    reason = (
        "contract_changed_reopened" if isinstance(current, dict) else "collecting_exact_samples"
    )
    identity = _new_capture_identity(interface_id, reason)
    if isinstance(current, dict) and current.get("status") == "blocked_until_manual_review":
        identity["status"] = "blocked_until_manual_review"
        identity["reason"] = "rate_limit_block_preserved_after_contract_change"
        if current.get("rate_limit_observed_data_date"):
            identity["rate_limit_observed_data_date"] = current["rate_limit_observed_data_date"]
    identities[interface_id] = identity
    return identity, isinstance(current, dict)


def _capture_identity_summary(identity: dict[str, Any]) -> dict[str, Any]:
    status = str(identity.get("status") or "observing")
    samples = identity.get("recheck_samples") if status == "rechecking" else identity.get("samples")
    samples = samples if isinstance(samples, list) else []
    summary = {
        key: identity.get(key)
        for key in (
            "status",
            "interface_id",
            "reference_source",
            "evidence_dates",
            "confirmed_fields",
            "unresolved_fields",
            "last_probe_data_date",
            "last_mismatch",
            "reason",
        )
        if identity.get(key) is not None
    }
    matched_symbols = []
    for item in samples:
        if not isinstance(item, dict):
            continue
        try:
            matched_symbols.append(max(0, int(item.get("matched_symbols", 0))))
        except (TypeError, ValueError, OverflowError):
            continue
    summary.update(
        {
            "minimum_data_dates": CAPTURE_IDENTITY_MIN_DATES,
            "minimum_symbols_per_date": CAPTURE_IDENTITY_MIN_SYMBOLS_PER_DATE,
            "minimum_fields": CAPTURE_IDENTITY_MIN_FIELDS,
            "matched_data_dates": len(
                {item.get("date") for item in samples if isinstance(item, dict)}
            ),
            "minimum_matched_symbols": min(matched_symbols, default=0),
        }
    )
    if status == "operationally_redundant":
        elapsed = _capture_identity_days_since_probe(identity)
        summary["next_recheck_in_data_dates"] = max(0, CAPTURE_IDENTITY_RECHECK_DATES - elapsed)
    if status == "rechecking":
        summary["recheck_samples_collected"] = len(samples)
    return summary


def _capture_identity_days_since_probe(identity: dict[str, Any]) -> int:
    try:
        return max(0, int(identity.get("eligible_data_dates_since_probe", 0)))
    except (TypeError, ValueError, OverflowError):
        return CAPTURE_IDENTITY_RECHECK_DATES


def _route_identity_summary_map(state: Optional[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if not isinstance(state, dict):
        return {
            interface_id: {
                "status": "state_unreadable_manual_review_required",
                "interface_id": interface_id,
                "reason": "local AxData state is unreadable; manual review is required",
            }
            for interface_id in CAPTURE_ENDPOINTS
        }
    result = {}
    for interface_id in CAPTURE_ENDPOINTS:
        identity, _ = _capture_identity_state(state, interface_id)
        result[interface_id] = _capture_identity_summary(identity)
    return result


def get_axdata_capture_identity_plan(
    data_date: str, *, force_reprobe: bool = False
) -> dict[str, Any]:
    """Stop confirmed redundant routes until a scheduled identity recheck.

    A due or explicitly requested recheck temporarily reopens collection. Other
    confirmed redundant routes are skipped, while their reference source continues
    to provide eligible data dates for the next recheck window.
    """
    state, error = _load_validation_state()
    if error:
        return {
            "status": "blocked_until_manual_review",
            "reason": error,
            "endpoints": {
                interface_id: {
                    "action": "skip",
                    "identity_validation_action": "blocked",
                    "reason": "state_unreadable_manual_review_required",
                    "identity": {
                        "status": "state_unreadable_manual_review_required",
                        "interface_id": interface_id,
                    },
                }
                for interface_id in CAPTURE_ENDPOINTS
            },
        }
    assert state is not None
    target_date = _date_key(data_date) or data_date
    endpoints: dict[str, dict[str, Any]] = {}
    changed = False
    for interface_id, endpoint in CAPTURE_ENDPOINTS.items():
        identity, contract_changed = _capture_identity_state(state, interface_id)
        changed = changed or contract_changed
        status = identity.get("status")
        action, reason = "collect", "identity_not_yet_confirmed"
        identity_validation_action = "sample"
        last_probe = _date_key(identity.get("last_probe_data_date"))
        if status == "blocked_until_manual_review":
            action, reason = "skip", "blocked_until_manual_review"
            identity_validation_action = "blocked"
        elif status == "operationally_redundant":
            if force_reprobe or (
                _capture_identity_days_since_probe(identity) >= CAPTURE_IDENTITY_RECHECK_DATES
            ):
                identity["status"] = "rechecking"
                identity["recheck_samples"] = []
                identity["reason"] = (
                    "manual_recheck_requested" if force_reprobe else "scheduled_recheck_due"
                )
                changed = True
                reason = identity["reason"]
            elif not last_probe:
                action, reason = "collect", "missing_last_probe_date_reopened"
                identity_validation_action = "sample"
            else:
                action = "skip"
                reason = (
                    "identity_validation_already_confirmed_for_date"
                    if target_date <= last_probe
                    else "endpoint_redundant_until_scheduled_recheck"
                )
                identity_validation_action = "suppress"
        endpoints[interface_id] = {
            "action": action,
            "identity_validation_action": identity_validation_action,
            "source": endpoint["source"],
            "reference_source": endpoint["reference_source"],
            "reason": reason,
            "identity": _capture_identity_summary(identity),
        }
    if changed:
        _write_json(STATE_PATH, state)
    return {"status": "ready", "endpoints": endpoints}


def get_axdata_collision_suppressions() -> dict[str, dict[str, Any]]:
    """Return only fully confirmed routes safe to omit from routine collisions."""
    state, error = _load_validation_state()
    if error or not isinstance(state, dict):
        return {}
    suppressions: dict[str, dict[str, Any]] = {}
    for interface_id, endpoint in CAPTURE_ENDPOINTS.items():
        identities = state.get("capture_endpoint_identities")
        identity = identities.get(interface_id) if isinstance(identities, dict) else None
        if not isinstance(identity, dict):
            continue
        if identity.get("contract_fingerprint") != _capture_identity_contract_fingerprint(
            interface_id
        ):
            continue
        status = identity.get("status")
        if status == "blocked_until_manual_review":
            status = identity.get("status_before_block")
        if status not in {"operationally_redundant", "rechecking"}:
            continue
        for source in endpoint["source_aliases"]:
            suppressions[source] = _capture_identity_summary(identity)
    return suppressions


def _schema_fingerprint(fields: set[str]) -> str:
    payload = json.dumps(sorted(fields), ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _latest_shortline_pairs(
    out_dir: Path, latest_allowed_date: str
) -> tuple[Optional[str], list[tuple[str, dict[str, Any], dict[str, Any]]], set[str], set[str]]:
    axdata = _capture_stocks(out_dir, "axdata")
    eltdx = _capture_stocks(out_dir, "eltdx")
    cutoff = _date_key(latest_allowed_date) or latest_allowed_date
    by_date: dict[str, list[tuple[str, dict[str, Any], dict[str, Any]]]] = {}
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
        if not ax_date or ax_date != el_date or ax_date > cutoff or not _is_trading_date(ax_date):
            continue
        by_date.setdefault(ax_date, []).append((str(code), ax_record, el_record))
    if not by_date:
        return None, [], dates_ax, dates_eltdx
    effective_date = max(by_date)
    return effective_date, by_date[effective_date], dates_ax, dates_eltdx


def _shortline_capture_sample(out_dir: Path, latest_allowed_date: str) -> Optional[dict[str, Any]]:
    effective_date, paired, _, _ = _latest_shortline_pairs(out_dir, latest_allowed_date)
    if effective_date is None or not paired:
        return None
    cutoff = _date_key(latest_allowed_date) or latest_allowed_date
    ax_fields: set[str] = set()
    reference_fields: set[str] = set()
    for _, ax_record, el_record in paired:
        ax_fields.update(set(ax_record) - CAPTURE_SHORTLINE_META_FIELDS)
        reference_fields.update(set(el_record) - CAPTURE_SHORTLINE_META_FIELDS)
    if not paired or not ax_fields:
        return None

    confirmed_fields = []
    different_fields = []
    for field in sorted(ax_fields):
        equal = 0
        different = 0
        missing = 0
        for _, ax_record, el_record in paired:
            left, right = ax_record.get(field), el_record.get(field)
            if left is None and right is None:
                missing += 1
            elif left is None or right is None:
                different += 1
            elif _value_equal(left, right):
                equal += 1
            else:
                different += 1
        if different:
            different_fields.append(field)
        if equal >= CAPTURE_IDENTITY_MIN_SYMBOLS_PER_DATE and different == 0 and missing == 0:
            confirmed_fields.append(field)

    unresolved_fields = sorted(ax_fields - set(confirmed_fields))
    reference_only = sorted(reference_fields - ax_fields)
    valid = (
        len(paired) >= CAPTURE_IDENTITY_MIN_SYMBOLS_PER_DATE
        and len(confirmed_fields) >= CAPTURE_IDENTITY_MIN_FIELDS
        and not unresolved_fields
    )
    reason = (
        "exact_full_route_match"
        if valid
        else (
            "field_value_mismatch"
            if different_fields
            else (
                "axdata_fields_not_fully_confirmed"
                if unresolved_fields
                else "insufficient_matched_symbols_or_fields"
            )
        )
    )
    return {
        "date": effective_date,
        "latest_allowed_data_date": cutoff,
        "schema_fingerprint": _schema_fingerprint(ax_fields),
        "matched_symbols": len(paired),
        "confirmed_fields": confirmed_fields,
        "unresolved_fields": unresolved_fields,
        "reference_only_fields": reference_only,
        "different_fields": different_fields,
        "qualifies": valid,
        "reason": reason,
    }


def _kph_capture_sample(out_dir: Path, latest_allowed_date: str) -> Optional[dict[str, Any]]:
    kph = _read_json(out_dir / "raw_kph.json") or {}
    kpl = _read_json(out_dir / "raw_kpl.json") or {}
    kph_date = _date_key(kph.get("trade_date"))
    kpl_date = _date_key(kpl.get("trade_date"))
    cutoff = _date_key(latest_allowed_date) or latest_allowed_date
    kph_stocks = kph.get("stocks")
    kpl_stocks = kpl.get("stocks")
    if (
        not kph_date
        or kph_date != kpl_date
        or kph_date > cutoff
        or not _is_trading_date(kph_date)
        or not isinstance(kph_stocks, dict)
        or not isinstance(kpl_stocks, dict)
    ):
        return None
    paired_codes = sorted(
        code
        for code in set(kph_stocks) & set(kpl_stocks)
        if isinstance(kph_stocks[code], dict) and isinstance(kpl_stocks[code], dict)
    )
    if not paired_codes:
        return None
    ax_fields = {field for row in kph_stocks.values() if isinstance(row, dict) for field in row}
    field_pairs = {}
    for ax_field, reference_field in KPH_KPL_FIELD_PAIRS.items():
        equal = different = missing = 0
        for code in paired_codes:
            left = kph_stocks[code].get(ax_field)
            right = kpl_stocks[code].get(reference_field)
            if left is None or right is None:
                missing += 1
            elif _value_equal(left, right):
                equal += 1
            else:
                different += 1
        field_pairs[ax_field] = {"equal": equal, "different": different, "missing": missing}

    confirmed_fields = sorted(
        field
        for field, counts in field_pairs.items()
        if counts["equal"] >= CAPTURE_IDENTITY_MIN_SYMBOLS_PER_DATE
        and counts["different"] == 0
        and counts["missing"] == 0
    )
    unresolved_fields = sorted(ax_fields - set(confirmed_fields))
    different_fields = sorted(field for field, counts in field_pairs.items() if counts["different"])
    valid = (
        len(paired_codes) >= CAPTURE_IDENTITY_MIN_SYMBOLS_PER_DATE
        and len(confirmed_fields) >= CAPTURE_IDENTITY_MIN_FIELDS
        and not unresolved_fields
    )
    reason = (
        "exact_full_route_match"
        if valid
        else (
            "field_value_mismatch"
            if different_fields
            else (
                "unmapped_or_incomplete_axdata_fields"
                if unresolved_fields
                else "insufficient_matched_symbols_or_fields"
            )
        )
    )
    return {
        "date": kph_date,
        "latest_allowed_data_date": cutoff,
        "schema_fingerprint": _schema_fingerprint(ax_fields),
        "matched_symbols": len(paired_codes),
        "confirmed_fields": confirmed_fields,
        "unresolved_fields": unresolved_fields,
        "different_fields": different_fields,
        "qualifies": valid,
        "reason": reason,
    }


def _finish_capture_identity(identity: dict[str, Any], samples: list[dict[str, Any]]) -> None:
    was_rechecking = identity.get("status") == "rechecking" or bool(
        identity.get("status_before_recheck")
    )
    evidence_dates = sorted({sample["date"] for sample in samples if sample.get("date")})
    confirmed_fields = set(samples[0].get("confirmed_fields", [])) if samples else set()
    for sample in samples[1:]:
        confirmed_fields.intersection_update(sample.get("confirmed_fields", []))
    unresolved_fields = (
        set().union(*(set(sample.get("unresolved_fields", [])) for sample in samples))
        if samples
        else set()
    )
    if unresolved_fields or not confirmed_fields:
        identity["status"] = "observing"
        identity["reason"] = "samples_do_not_cover_full_axdata_schema"
        return
    identity["status"] = "operationally_redundant"
    if was_rechecking:
        identity.setdefault("initial_evidence_dates", identity.get("evidence_dates", []))
        identity["samples"] = samples[-CAPTURE_IDENTITY_MIN_DATES:]
    identity["confirmed_fields"] = sorted(confirmed_fields)
    identity["unresolved_fields"] = []
    identity["evidence_dates"] = evidence_dates[-CAPTURE_IDENTITY_MIN_DATES:]
    identity["last_probe_data_date"] = evidence_dates[-1]
    identity["last_counted_data_date"] = evidence_dates[-1]
    identity["eligible_data_dates_since_probe"] = 0
    identity["reason"] = (
        "scheduled_recheck_matched" if was_rechecking else "minimum_exact_samples_matched"
    )
    identity.pop("status_before_recheck", None)
    identity["recheck_samples"] = []


def _record_capture_identity_sample(
    identity: dict[str, Any], sample: Optional[dict[str, Any]]
) -> None:
    if sample is None:
        identity["last_sample_issue"] = "same_dated_comparison_unavailable"
        return
    prior_schema = identity.get("schema_fingerprint")
    if prior_schema and prior_schema != sample["schema_fingerprint"]:
        prior_status = identity.get("status")
        identity.update(
            _new_capture_identity(identity["interface_id"], "response_schema_changed_reopened")
        )
        identity["schema_fingerprint"] = sample["schema_fingerprint"]
        if prior_status in {"operationally_redundant", "rechecking"}:
            identity["status"] = "observing"
            identity["reason"] = "response_schema_changed_reopened"
    identity["schema_fingerprint"] = sample["schema_fingerprint"]
    if sample.get("different_fields"):
        identity["last_mismatch"] = {
            "data_date": sample.get("date"),
            "fields": sample["different_fields"],
            "reason": sample.get("reason"),
        }
        if identity.get("status") in {"operationally_redundant", "rechecking"}:
            identity["status"] = "observing"
            identity["samples"] = []
            identity["recheck_samples"] = []
            identity["evidence_dates"] = []
            identity["confirmed_fields"] = []
            identity["unresolved_fields"] = sample.get("unresolved_fields", [])
            identity["reason"] = "value_mismatch_reopened"
        else:
            identity["reason"] = "value_mismatch_observed"
        return
    if not sample.get("qualifies"):
        identity["unresolved_fields"] = sample.get("unresolved_fields", [])
        identity["last_sample_issue"] = {
            "data_date": sample.get("date"),
            "reason": sample.get("reason"),
            "matched_symbols": sample.get("matched_symbols", 0),
            "unresolved_fields": sample.get("unresolved_fields", []),
        }
        return
    is_rechecking = identity.get("status") == "rechecking"
    key = "recheck_samples" if is_rechecking else "samples"
    samples = identity.get(key)
    samples = samples if isinstance(samples, list) else []
    samples = [
        item for item in samples if not isinstance(item, dict) or item.get("date") != sample["date"]
    ]
    samples.append(sample)
    identity[key] = samples[-CAPTURE_IDENTITY_MIN_DATES:]
    identity["last_probe_data_date"] = sample["date"]
    identity["last_counted_data_date"] = sample["date"]
    distinct_dates = {item.get("date") for item in samples if isinstance(item, dict)}
    if len(distinct_dates) >= CAPTURE_IDENTITY_MIN_DATES:
        if is_rechecking:
            identity["status_before_recheck"] = "rechecking"
        _finish_capture_identity(identity, samples)
    else:
        identity["reason"] = (
            "collecting_recheck_samples" if is_rechecking else "collecting_exact_samples"
        )


def update_axdata_capture_identities(
    *,
    out_dir: str | Path,
    data_date: str,
    source_meta: Optional[dict[str, Any]],
    requested_sources: Optional[set[str]] = None,
) -> dict[str, dict[str, Any]]:
    """Update identities from successful captures or dates eligible for recheck."""
    state, error = _load_validation_state()
    if error or not isinstance(state, dict):
        return _route_identity_summary_map(None)
    target_date = _date_key(data_date) or data_date
    output_dir = Path(out_dir)
    source_meta = source_meta if isinstance(source_meta, dict) else {}
    changed = False
    for interface_id, endpoint in CAPTURE_ENDPOINTS.items():
        source = str(endpoint["source"])
        reference_source = str(endpoint["reference_source"])
        if requested_sources is not None and not {source, reference_source}.issubset(
            requested_sources
        ):
            continue
        identity, contract_changed = _capture_identity_state(state, interface_id)
        changed = changed or contract_changed
        source_state = source_meta.get(source)
        reference_state = source_meta.get(reference_source)
        if not isinstance(reference_state, dict):
            continue
        payload = _read_json(output_dir / f"raw_{source}.json") or {}
        if (isinstance(source_state, dict) and _source_has_rate_limit(source_state)) or (
            _payload_has_rate_limit(payload)
        ):
            if identity.get("status") in {"operationally_redundant", "rechecking"}:
                identity["status_before_block"] = identity["status"]
            identity["status"] = "blocked_until_manual_review"
            identity["reason"] = "rate_limit_or_ban_observed"
            changed = True
            continue
        if identity.get("status") == "blocked_until_manual_review":
            continue
        if reference_state.get("ok") is not True:
            continue
        source_meta_block = payload.get("__source_meta__")
        capture_block = (
            source_meta_block.get("capture_block") if isinstance(source_meta_block, dict) else None
        )
        reference_date = _date_key(reference_state.get("as_of_date"))
        if (
            identity.get("status") == "operationally_redundant"
            and isinstance(capture_block, dict)
            and capture_block.get("status") == "operationally_redundant"
            and target_date
            and reference_date == target_date
        ):
            # The redundant route made no request. Count only a successful reference
            # snapshot whose effective date matches this completed capture date.
            last_counted = _date_key(identity.get("last_counted_data_date"))
            last_probe = _date_key(identity.get("last_probe_data_date"))
            if (
                (last_probe is None or target_date > last_probe)
                and target_date != last_counted
                and (last_counted is None or target_date > last_counted)
            ):
                identity["eligible_data_dates_since_probe"] = (
                    _capture_identity_days_since_probe(identity) + 1
                )
                identity["last_counted_data_date"] = target_date
                changed = True
            continue
        if not isinstance(source_state, dict) or source_state.get("ok") is not True:
            continue
        if reference_date != target_date:
            continue
        sample = (
            _shortline_capture_sample(output_dir, target_date)
            if interface_id == "stock_shortline_indicators_tdx"
            else _kph_capture_sample(output_dir, target_date)
        )
        previous = json.dumps(identity, ensure_ascii=True, sort_keys=True, default=str)
        _record_capture_identity_sample(identity, sample)
        changed = changed or previous != json.dumps(
            identity, ensure_ascii=True, sort_keys=True, default=str
        )
    if changed:
        _write_json(STATE_PATH, state)
    return _route_identity_summary_map(state)


def record_axdata_capture_rate_limits(
    *,
    data_date: str,
    source_meta: Optional[dict[str, Any]],
    collected_data: Optional[dict[str, Any]],
    requested_sources: set[str],
) -> dict[str, dict[str, Any]]:
    """Persist route blocks even when capture used --only and validation is ineligible."""
    state, error = _load_validation_state()
    if error or not isinstance(state, dict):
        return _route_identity_summary_map(None)
    source_meta = source_meta if isinstance(source_meta, dict) else {}
    collected_data = collected_data if isinstance(collected_data, dict) else {}
    changed = False
    observed_date = _date_key(data_date)
    for interface_id, endpoint in CAPTURE_ENDPOINTS.items():
        source = str(endpoint["source"])
        if source not in requested_sources:
            continue
        source_state = source_meta.get(source)
        payload = collected_data.get(source)
        has_rate_limit = (
            isinstance(source_state, dict) and _source_has_rate_limit(source_state)
        ) or _payload_has_rate_limit(payload)
        if not has_rate_limit:
            continue
        identity, contract_changed = _capture_identity_state(state, interface_id)
        previous = json.dumps(identity, ensure_ascii=True, sort_keys=True, default=str)
        if identity.get("status") in {"operationally_redundant", "rechecking"}:
            identity["status_before_block"] = identity["status"]
        identity["status"] = "blocked_until_manual_review"
        identity["reason"] = "rate_limit_or_ban_observed"
        identity["rate_limit_observed_data_date"] = observed_date
        changed = (
            changed
            or contract_changed
            or previous != json.dumps(identity, ensure_ascii=True, sort_keys=True, default=str)
        )
    if changed:
        _write_json(STATE_PATH, state)
    return _route_identity_summary_map(state)


def _payload_has_rate_limit(payload: Any) -> bool:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key in {"__error__", "error", "error_sample"} and _source_has_rate_limit(
                {"error_sample": value}
            ):
                return True
            if _payload_has_rate_limit(value):
                return True
    elif isinstance(payload, list):
        return any(_payload_has_rate_limit(value) for value in payload)
    return False


def _passive_capture_issue(
    required_sources: set[str],
    source_meta: Optional[dict[str, Any]],
    requested_sources: Optional[set[str]],
    market_phase: Optional[str],
) -> Optional[str]:
    if market_phase is not None and market_phase not in {
        "closed",
        "pre_open",
        "non_trading_day",
    }:
        return "capture_not_in_stable_data_window"
    if requested_sources is not None and not required_sources.issubset(requested_sources):
        return "required_sources_not_selected"
    if source_meta is not None:
        for source in sorted(required_sources):
            source_state = source_meta.get(source)
            if not isinstance(source_state, dict) or source_state.get("ok") is not True:
                return f"required_source_not_successful:{source}"
    return None


def _shortline_passive_evidence(
    out_dir: Path,
    latest_allowed_date: str,
    *,
    source_meta: Optional[dict[str, Any]] = None,
    requested_sources: Optional[set[str]] = None,
    market_phase: Optional[str] = None,
) -> dict[str, Any]:
    issue = _passive_capture_issue(
        {"axdata", "eltdx"}, source_meta, requested_sources, market_phase
    )
    if issue:
        return {"status": "not_run", "reason": issue, "requests_added": 0}
    effective_date, paired, dates_ax, dates_eltdx = _latest_shortline_pairs(
        out_dir, latest_allowed_date
    )
    field_stats: dict[str, dict[str, int]] = {}
    paired_codes: list[str] = []
    for code, ax_record, el_record in paired:
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
        "target_trade_date": _date_key(latest_allowed_date) or latest_allowed_date,
        "matched_trade_date": effective_date,
        "axdata_observed_dates": sorted(dates_ax),
        "eltdx_observed_dates": sorted(dates_eltdx),
        "paired_stocks": len(paired_codes),
        "paired_codes": paired_codes,
        "field_comparisons": field_stats,
        "requests_added": 0,
    }


def _kph_kpl_passive_evidence(
    out_dir: Path,
    latest_allowed_date: str,
    *,
    source_meta: Optional[dict[str, Any]] = None,
    requested_sources: Optional[set[str]] = None,
    market_phase: Optional[str] = None,
) -> dict[str, Any]:
    issue = _passive_capture_issue({"kph", "kpl"}, source_meta, requested_sources, market_phase)
    if issue:
        return {"status": "not_run", "reason": issue, "requests_added": 0}
    kph_payload = _read_json(out_dir / "raw_kph.json") or {}
    kpl_payload = _read_json(out_dir / "raw_kpl.json") or {}
    kph_date = _date_key(kph_payload.get("trade_date"))
    kpl_date = _date_key(kpl_payload.get("trade_date"))
    cutoff = _date_key(latest_allowed_date) or latest_allowed_date
    kph_stocks = kph_payload.get("stocks")
    kpl_stocks = kpl_payload.get("stocks")
    if (
        not kph_date
        or kph_date != kpl_date
        or kph_date > cutoff
        or not _is_trading_date(kph_date)
        or not isinstance(kph_stocks, dict)
        or not isinstance(kpl_stocks, dict)
    ):
        return {
            "status": "date_or_sample_unavailable",
            "target_trade_date": cutoff,
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
        "target_trade_date": cutoff,
        "matched_trade_date": kph_date,
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
    path = PROJECT_ROOT / "docs" / "axdata_interface_crosswalk_summary.json"
    summary = read_summary(path)
    if summary is None:
        return {"status": "unavailable", "reason": "AxData crosswalk missing or unreadable"}
    source_path = PROJECT_ROOT / "docs" / "axdata_interface_crosswalk.json"
    try:
        source_digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    except OSError:
        return {
            "status": "unavailable",
            "reason": "AxData canonical crosswalk missing or unreadable",
        }
    if source_digest != summary["source_sha256"]:
        return {"status": "unavailable", "reason": "AxData crosswalk summary is stale"}
    _STATIC_QUEUE_CACHE = {
        "status": "ok",
        "interface_count": summary["interface_count"],
        "field_occurrence_count": summary["field_occurrence_count"],
        "field_occurrences_below_e3": summary["field_occurrences_below_e3"],
        "interface_relation_status_counts": summary["interface_relation_status_counts"],
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


def _identity_contract_fingerprint() -> str:
    contract = {
        "interface": ACTIVE_INTERFACE,
        "raw_indexes": TENCENT_RAW_INDEXES,
        "dynamic_pe_index": _dynamic_pe_index(),
        "amount_normalization": "AxData yuan divided by 10000",
    }
    serialized = json.dumps(contract, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _new_endpoint_identity(reason: str = "collecting_exact_date_samples") -> dict[str, Any]:
    return {
        "status": "observing",
        "contract_fingerprint": _identity_contract_fingerprint(),
        "schema_fingerprint": None,
        "samples": [],
        "recheck_samples": [],
        "value_equivalent_fields": [],
        "semantic_unresolved_fields": [],
        "unresolved_fields": sorted(IDENTITY_INFORMATION_FIELDS),
        "evidence_dates": [],
        "distinct_symbols": [],
        "last_probe_data_date": None,
        "last_counted_data_date": None,
        "eligible_data_dates_since_probe": 0,
        "reason": reason,
    }


def _endpoint_identity_state(state: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    fingerprint = _identity_contract_fingerprint()
    current = state.get("endpoint_identity")
    if isinstance(current, dict) and current.get("contract_fingerprint") == fingerprint:
        return current, False
    reopened = isinstance(current, dict)
    reason = "contract_changed_reopened" if reopened else "collecting_exact_date_samples"
    identity = _new_endpoint_identity(reason)
    state["endpoint_identity"] = identity
    return identity, reopened


def _identity_value_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str) and value.strip().lower() in {"", "none", "null", "nan"}:
        return False
    number = _number(value)
    return math.isfinite(number) if number is not None else bool(str(value).strip())


def _identity_days_since_probe(identity: dict[str, Any]) -> int:
    try:
        return max(0, int(identity.get("eligible_data_dates_since_probe", 0)))
    except (TypeError, ValueError, OverflowError):
        return IDENTITY_RECHECK_DATA_DATES


def _identity_field_observations(
    comparison: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    field_results = comparison.get("field_comparisons")
    field_results = field_results if isinstance(field_results, dict) else {}
    different_fields = []
    incomplete_fields = []
    value_fields = []
    semantic_fields = []
    for field in TENCENT_RAW_INDEXES:
        item = field_results.get(field)
        status = item.get("status") if isinstance(item, dict) else None
        if status == "different":
            different_fields.append(field)
        elif status not in IDENTITY_VALUE_MATCH_STATUSES:
            incomplete_fields.append(field)
        if field not in IDENTITY_INFORMATION_FIELDS or not isinstance(item, dict):
            continue
        if not _identity_value_present(item.get("axdata_value")) or not _identity_value_present(
            item.get("project_value")
        ):
            continue
        if status in IDENTITY_VALUE_MATCH_STATUSES:
            value_fields.append(field)
        if status == "value_equal_with_dictionary_semantic_conflict":
            semantic_fields.append(field)

    dynamic_check = comparison.get("dictionary_dynamic_pe_check")
    if isinstance(dynamic_check, dict) and dynamic_check.get("status") != "equal":
        semantic_fields.append("pe_dynamic")
    return (
        sorted(set(different_fields)),
        sorted(set(incomplete_fields)),
        sorted(set(value_fields)),
        sorted(set(semantic_fields)),
    )


def _identity_sample_details(
    record: dict[str, Any], comparison: dict[str, Any], code: str, data_date: str
) -> dict[str, Any]:
    different_fields, incomplete_fields, value_fields, semantic_fields = (
        _identity_field_observations(comparison)
    )
    information_match_count = len(set(value_fields) - {"pe_dynamic"})
    same_dated = comparison.get("status") == "compared"
    qualifies = (
        same_dated
        and not different_fields
        and not incomplete_fields
        and information_match_count >= IDENTITY_MIN_INFORMATION_FIELDS
    )
    if not same_dated:
        reason = "not_same_dated_snapshot"
    elif different_fields:
        reason = "value_mismatch"
    elif incomplete_fields:
        reason = "comparison_fields_incomplete"
    elif information_match_count < IDENTITY_MIN_INFORMATION_FIELDS:
        reason = "insufficient_nonempty_information_fields"
    else:
        reason = "exact_value_sample"
    schema = json.dumps(
        sorted(str(key) for key in record), ensure_ascii=True, separators=(",", ":")
    )
    schema_fingerprint = hashlib.sha256(schema.encode("utf-8")).hexdigest()
    return {
        "qualifies": qualifies,
        "reason": reason,
        "date": _date_key(data_date),
        "code": code,
        "schema_fingerprint": schema_fingerprint,
        "value_fields": value_fields,
        "semantic_fields": semantic_fields,
        "different_fields": different_fields,
        "information_match_count": information_match_count,
    }


def _reset_identity_after_mismatch(
    identity: dict[str, Any], details: dict[str, Any], reason: str
) -> None:
    identity.update(_new_endpoint_identity(reason))
    identity["schema_fingerprint"] = details.get("schema_fingerprint")
    identity["last_probe_data_date"] = details.get("date")
    identity["last_counted_data_date"] = details.get("date")
    identity["last_mismatch"] = {
        "data_date": details.get("date"),
        "code": details.get("code"),
        "fields": details.get("different_fields", []),
        "reason": details.get("reason"),
    }


def _identity_has_confirmation(samples: list[dict[str, Any]]) -> bool:
    dates = {sample.get("date") for sample in samples if sample.get("date")}
    codes = {sample.get("code") for sample in samples if sample.get("code")}
    return (
        len(dates) >= IDENTITY_MIN_CAPTURE_DATES
        and len(codes) >= IDENTITY_MIN_DISTINCT_SYMBOLS
        and all(
            int(sample.get("information_match_count", 0)) >= IDENTITY_MIN_INFORMATION_FIELDS
            for sample in samples
        )
    )


def _finish_endpoint_identity(identity: dict[str, Any], samples: list[dict[str, Any]]) -> None:
    dates = sorted({sample["date"] for sample in samples if sample.get("date")})
    symbols = sorted({sample["code"] for sample in samples if sample.get("code")})
    semantic_fields = (
        set().union(*(set(sample.get("semantic_fields", [])) for sample in samples))
        if samples
        else set()
    )
    value_equivalent_fields = []
    for field in sorted(IDENTITY_INFORMATION_FIELDS):
        field_samples = [sample for sample in samples if field in sample.get("value_fields", [])]
        field_dates = {sample.get("date") for sample in field_samples}
        field_symbols = {sample.get("code") for sample in field_samples}
        if (
            len(field_dates) >= IDENTITY_MIN_CAPTURE_DATES
            and len(field_symbols) >= IDENTITY_MIN_DISTINCT_SYMBOLS
        ):
            value_equivalent_fields.append(field)
    confirmed_fields = sorted(set(value_equivalent_fields) - semantic_fields)
    unresolved = (set(IDENTITY_INFORMATION_FIELDS) - set(confirmed_fields)) | semantic_fields
    identity["status"] = "partially_redundant" if unresolved else "operationally_redundant"
    identity["value_equivalent_fields"] = value_equivalent_fields
    identity["confirmed_fields"] = confirmed_fields
    identity["semantic_unresolved_fields"] = sorted(semantic_fields)
    identity["unresolved_fields"] = sorted(unresolved)
    identity["evidence_dates"] = dates[-IDENTITY_MIN_CAPTURE_DATES:]
    identity["distinct_symbols"] = symbols
    identity["last_probe_data_date"] = dates[-1] if dates else None
    identity["last_counted_data_date"] = identity["last_probe_data_date"]
    identity["eligible_data_dates_since_probe"] = 0
    identity["samples"] = []
    identity["recheck_samples"] = []
    identity["reason"] = (
        "scheduled_recheck_matched"
        if identity.get("status_before_recheck")
        else "minimum_exact_samples_matched"
    )
    identity.pop("status_before_recheck", None)


def _record_endpoint_identity_sample(
    state: dict[str, Any],
    record: dict[str, Any],
    comparison: dict[str, Any],
    code: str,
    data_date: str,
) -> dict[str, Any]:
    identity, _contract_changed = _endpoint_identity_state(state)
    details = _identity_sample_details(record, comparison, code, data_date)
    old_schema = identity.get("schema_fingerprint")
    schema_changed = bool(old_schema and old_schema != details["schema_fingerprint"])
    if schema_changed:
        prior_status = identity.get("status")
        _reset_identity_after_mismatch(identity, details, "response_schema_changed_reopened")
        identity["status"] = "observing"
        identity["schema_fingerprint"] = details["schema_fingerprint"]
        if prior_status in IDENTITY_REDUNDANT_STATUSES or prior_status == "rechecking":
            identity["reason"] = "response_schema_changed_reopened"
    if details["different_fields"]:
        _reset_identity_after_mismatch(identity, details, "value_mismatch_reopened")
        return _identity_summary(identity)
    if not details["qualifies"]:
        identity["last_sample_issue"] = {
            "data_date": details["date"],
            "code": code,
            "reason": details["reason"],
        }
        return _identity_summary(identity)

    identity["schema_fingerprint"] = details["schema_fingerprint"]
    sample = {
        key: details[key]
        for key in ("date", "code", "value_fields", "semantic_fields", "information_match_count")
    }
    _append_identity_sample(identity, sample)
    identity["last_probe_data_date"] = details["date"]
    return _identity_summary(identity)


def _append_identity_sample(identity: dict[str, Any], sample: dict[str, Any]) -> None:
    rechecking = identity.get("status") == "rechecking"
    sample_key = "recheck_samples" if rechecking else "samples"
    samples = identity.get(sample_key)
    samples = samples if isinstance(samples, list) else []
    if not any(item.get("date") == sample["date"] for item in samples if isinstance(item, dict)):
        samples.append(sample)
    identity[sample_key] = samples[-30:]
    if _identity_has_confirmation(identity[sample_key]):
        if rechecking:
            identity["status_before_recheck"] = "rechecking"
        _finish_endpoint_identity(identity, identity[sample_key])
        return
    identity["last_sample_issue"] = None
    if identity.get("reason") not in {
        "contract_changed_reopened",
        "response_schema_changed_reopened",
    }:
        identity["reason"] = (
            "rechecking_exact_samples" if rechecking else "collecting_exact_date_samples"
        )


def _identity_summary(identity: dict[str, Any]) -> dict[str, Any]:
    status = str(identity.get("status") or "observing")
    samples = identity.get("recheck_samples") if status == "rechecking" else identity.get("samples")
    samples = samples if isinstance(samples, list) else []
    summary = {
        "status": status,
        "interface_id": ACTIVE_INTERFACE,
        "reference_source": "project_tencent",
        "minimum_data_dates": IDENTITY_MIN_CAPTURE_DATES,
        "minimum_distinct_symbols": IDENTITY_MIN_DISTINCT_SYMBOLS,
        "minimum_information_fields_per_sample": IDENTITY_MIN_INFORMATION_FIELDS,
        "matched_data_dates": (
            len(identity.get("evidence_dates", []))
            if status in IDENTITY_REDUNDANT_STATUSES
            else len({item.get("date") for item in samples if isinstance(item, dict)})
        ),
        "matched_symbols": (
            len(identity.get("distinct_symbols", []))
            if status in IDENTITY_REDUNDANT_STATUSES
            else len({item.get("code") for item in samples if isinstance(item, dict)})
        ),
        "evidence_dates": identity.get("evidence_dates", []),
        "value_equivalent_fields": identity.get("value_equivalent_fields", []),
        "confirmed_fields": identity.get("confirmed_fields", []),
        "semantic_unresolved_fields": identity.get("semantic_unresolved_fields", []),
        "unresolved_fields": identity.get("unresolved_fields", []),
        "last_probe_data_date": identity.get("last_probe_data_date"),
        "last_mismatch": identity.get("last_mismatch"),
        "reason": identity.get("reason"),
    }
    if status in IDENTITY_REDUNDANT_STATUSES:
        summary["next_recheck_in_data_dates"] = max(
            0,
            IDENTITY_RECHECK_DATA_DATES - _identity_days_since_probe(identity),
        )
    elif status == "rechecking":
        summary["recheck_samples_collected"] = len(samples)
    return summary


def _identity_should_probe(identity: dict[str, Any], data_date: str) -> bool:
    status = identity.get("status")
    date_key = _date_key(data_date)
    last_probe = _date_key(identity.get("last_probe_data_date"))
    last_counted = _date_key(identity.get("last_counted_data_date"))
    if status in IDENTITY_REDUNDANT_STATUSES or status == "rechecking":
        if status in IDENTITY_REDUNDANT_STATUSES and last_probe is None:
            identity["status_before_recheck"] = status
            identity["status"] = "rechecking"
            identity["recheck_samples"] = []
            identity["reason"] = "confirmed_state_missing_probe_date_rechecking"
            status = "rechecking"
        if date_key and date_key != last_counted and (last_probe is None or date_key > last_probe):
            identity["eligible_data_dates_since_probe"] = _identity_days_since_probe(identity) + 1
            identity["last_counted_data_date"] = date_key
        if (
            status in IDENTITY_REDUNDANT_STATUSES
            and _identity_days_since_probe(identity) >= IDENTITY_RECHECK_DATA_DATES
        ):
            identity["status_before_recheck"] = status
            identity["status"] = "rechecking"
            identity["recheck_samples"] = []
            identity["reason"] = "scheduled_recheck_due"
            status = "rechecking"
    return status not in IDENTITY_REDUNDANT_STATUSES


def _request_records(interface: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    from stock_common.sc_datasource import get_axdata_records

    return get_axdata_records(interface, params=params)


def _selected_source_names(only: Any, requested_sources: Optional[set[str]]) -> Optional[set[str]]:
    if requested_sources is not None:
        return {str(source).strip() for source in requested_sources if str(source).strip()}
    if isinstance(only, str):
        selected = {part.strip() for part in only.split(",") if part.strip()}
    elif isinstance(only, (list, tuple, set)):
        selected = {str(part).strip() for part in only if str(part).strip()}
    else:
        selected = set()
    return selected or None


def _eligible_reason(
    data_date: str,
    data_date_domain: str,
    market_phase: str,
    latest_completed_trade_date: str,
    only: Any,
    requested_sources: Optional[set[str]] = None,
) -> Optional[str]:
    selected = _selected_source_names(only, requested_sources)
    if selected is not None and not {"axdata", "tencent"}.issubset(selected):
        return "required_sources_not_selected"
    if data_date_domain not in {"trading", "mixed"}:
        return "not_trading_date_capture"
    if market_phase not in {"closed", "pre_open", "non_trading_day"}:
        return "capture_not_in_stable_data_window"
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
        "source_identity": _identity_summary(state.get("endpoint_identity", {})),
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
        "source_identity": _identity_summary(state.get("endpoint_identity", {})),
    }, state


def _handle_matched_tencent_response(
    record: dict[str, Any],
    code: str,
    project_fields: list[Any],
    data_date: str,
    collected_at: str,
    state: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    comparison = _compare_tencent_record(record, project_fields, data_date)
    identity_summary = _record_endpoint_identity_sample(state, record, comparison, code, data_date)
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
        "comparison": comparison,
        "source_identity": identity_summary,
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
    identity = probe.get("source_identity")
    if isinstance(identity, dict):
        probe_summary["source_identity"] = identity
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
        "capture_directory_date": evidence.get("capture_directory_date"),
        "latest_completed_trade_date": evidence.get("latest_completed_trade_date"),
        "probe": probe_summary,
        "passive_evidence": evidence.get("passive_evidence", {}),
        "endpoint_identities": evidence.get("endpoint_identities", {}),
        "queue": evidence.get("queue", {}),
    }


def _base_evidence(
    target_date: str,
    latest_completed_trade_date: str,
    data_date_domain: str,
    market_phase: str,
    reason: Optional[str],
    output_dir: Path,
    queue: dict[str, Any],
    evaluated_at: datetime,
    source_meta: Optional[dict[str, Any]],
    requested_sources: Optional[set[str]],
) -> dict[str, Any]:
    passive = {
        "axdata_shortline_vs_eltdx": _shortline_passive_evidence(
            output_dir,
            latest_completed_trade_date,
            source_meta=source_meta,
            requested_sources=requested_sources,
            market_phase=market_phase,
        ),
        "kph_limit_up_history_vs_kpl_detail": _kph_kpl_passive_evidence(
            output_dir,
            latest_completed_trade_date,
            source_meta=source_meta,
            requested_sources=requested_sources,
            market_phase=market_phase,
        ),
    }
    return {
        "schema_version": "1.2",
        "status": "not_eligible" if reason else "eligible",
        "data_date": target_date,
        "capture_directory_date": target_date,
        "latest_completed_trade_date": _date_key(latest_completed_trade_date)
        or latest_completed_trade_date,
        "data_date_domain": data_date_domain,
        "market_phase": market_phase,
        "evaluated_at": evaluated_at.isoformat(timespec="seconds"),
        "eligibility_reason": reason,
        "queue": queue,
        "passive_evidence": passive,
        "endpoint_identities": _current_capture_identity_summaries(),
        "probe": {"status": "not_run", "request_count": 0},
    }


def _current_capture_identity_summaries() -> dict[str, dict[str, Any]]:
    state, error = _load_validation_state()
    return _route_identity_summary_map(None if error else state)


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
    loaded_state = _read_json(STATE_PATH)
    if STATE_PATH.exists() and loaded_state is None:
        evidence["status"] = "blocked_until_manual_review"
        evidence["probe"] = {
            "status": "state_unreadable_until_manual_review",
            "interface_id": ACTIVE_INTERFACE,
            "family": ACTIVE_FAMILY,
            "request_count": 0,
            "source_identity": {
                "status": "state_unreadable_manual_review_required",
                "interface_id": ACTIVE_INTERFACE,
                "reason": "local AxData state is unreadable; inspect or explicitly reset it after recovery review",
            },
        }
        return
    state = loaded_state or {}
    identity, _contract_changed = _endpoint_identity_state(state)
    should_probe = _identity_should_probe(identity, target_date)
    _write_json(STATE_PATH, state)
    if _date_key(state.get("last_attempted_data_date")) == target_date:
        _set_probe_policy_skip(
            evidence,
            "attempt_already_made_for_data_date",
            interface_id=state.get("last_interface"),
            family=ACTIVE_FAMILY,
            code=state.get("last_code"),
        )
        evidence["probe"]["source_identity"] = _identity_summary(identity)
        return
    if ACTIVE_FAMILY in state.get("blocked_families", []):
        _set_probe_policy_skip(
            evidence,
            "blocked_until_manual_review",
            family=ACTIVE_FAMILY,
            reason="previous 403/429/ban or consecutive empty responses; clear local state only after independent recovery check",
        )
        evidence["probe"]["source_identity"] = _identity_summary(identity)
        return
    if not should_probe:
        _set_probe_policy_skip(
            evidence,
            "endpoint_redundant_until_scheduled_recheck",
            interface_id=ACTIVE_INTERFACE,
            family=ACTIVE_FAMILY,
            request_count=0,
        )
        evidence["probe"]["source_identity"] = _identity_summary(identity)
        return
    if not _apply_counterpart_gate(evidence, source_meta, state):
        evidence["probe"]["source_identity"] = _identity_summary(identity)
        return
    probe, updated_state = _run_tencent_probe(target_date, output_dir, pool, state)
    updated_identity = updated_state.get("endpoint_identity")
    if isinstance(updated_identity, dict):
        probe["source_identity"] = _identity_summary(updated_identity)
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
    only: Any,
    requested_sources: Optional[set[str]],
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
        requested_sources,
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
    only: Any,
    out_dir: str | Path,
    pool: list[dict[str, Any]],
    source_meta: Optional[dict[str, Any]] = None,
    requested_sources: Optional[set[str]] = None,
    now: Optional[datetime] = None,
) -> dict[str, Any]:
    """Summarize passive evidence and run at most one eligible AxData probe."""
    normalized_meta = source_meta if isinstance(source_meta, dict) else {}
    selected_sources = _selected_source_names(only, requested_sources)
    target_date, output_dir, queue, evaluated_at, reason = _validation_context(
        data_date,
        data_date_domain,
        market_phase,
        latest_completed_trade_date,
        only,
        selected_sources,
        out_dir,
        now,
    )
    stable_phase = market_phase in {"closed", "pre_open", "non_trading_day"}
    if stable_phase:
        endpoint_identities = update_axdata_capture_identities(
            out_dir=output_dir,
            data_date=latest_completed_trade_date,
            source_meta=normalized_meta,
            requested_sources=selected_sources,
        )
    else:
        endpoint_identities = _current_capture_identity_summaries()
    evidence = _base_evidence(
        target_date,
        latest_completed_trade_date,
        data_date_domain,
        market_phase,
        reason,
        output_dir,
        queue,
        evaluated_at,
        normalized_meta,
        selected_sources,
    )
    evidence["endpoint_identities"] = endpoint_identities
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
            existing["capture_directory_date"] = target_date
            existing["latest_completed_trade_date"] = evidence["latest_completed_trade_date"]
            existing["passive_evidence"] = evidence["passive_evidence"]
            existing["endpoint_identities"] = endpoint_identities
            _write_json(evidence_path, existing)
            return _summary(existing, evidence_path)

    if reason:
        if any(
            isinstance(item, dict) and item.get("status") == "compared"
            for item in evidence["passive_evidence"].values()
        ):
            _write_json(evidence_path, evidence)
            return _summary(evidence, evidence_path)
        return _summary(evidence)
    return _run_eligible_validation(evidence, target_date, output_dir, pool, normalized_meta)

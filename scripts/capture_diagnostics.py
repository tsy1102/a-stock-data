from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from scripts.capture_catalog import FULL_POOL_STOCK_SOURCES, SOURCE_REQUIRED_PATHS
from scripts.context_policy import CONTEXT_REQUIRED_PATHS


def _is_error_marker_key(key: Any) -> bool:
    text = str(key)
    return (
        text == "error"
        or text.endswith("_error")
        or (text.startswith("__error_") and text.endswith("__"))
    )


def _has_error_marker(value: Any) -> bool:
    if isinstance(value, dict):
        if any(
            key == "__error__" or (_is_error_marker_key(key) and bool(marker))
            for key, marker in value.items()
        ):
            return True
        return any(_has_error_marker(child) for child in value.values())
    if isinstance(value, list):
        return any(_has_error_marker(child) for child in value)
    return False


def _has_root_error_marker(value: Any) -> bool:
    return isinstance(value, dict) and any(
        key == "__error__" or (_is_error_marker_key(key) and bool(marker))
        for key, marker in value.items()
    )


def _source_expected_codes(source: str, pool: List[Dict[str, Any]]) -> Optional[List[str]]:
    if source in FULL_POOL_STOCK_SOURCES:
        return [str(item["code"]) for item in pool if item.get("code")]
    if source == "research_sina":
        return [str(item["code"]) for item in pool[:5] if item.get("code")]
    if source == "sse_e_interaction":
        return [
            str(item["code"])
            for item in pool[:3]
            if item.get("code") and str(item["code"]).startswith(("60", "68", "900"))
        ]
    return None


def _path_exists(data: Any, path: tuple) -> bool:
    current = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return False
        current = current[key]
    return current is not None


def _source_as_of_date(source: str, data: Any) -> Optional[str]:
    """Return only an explicit source date; never substitute the folder target date."""
    if not isinstance(data, dict):
        return None
    keys = (
        "zhb_date",
        "as_of_date",
        "asof_date",
        "data_date",
        "trade_date",
        "tradeDate",
        "probe_trading_day",
    )
    for key in keys:
        value = data.get(key)
        if isinstance(value, (str, date, datetime)) and str(value).strip():
            return value.strftime("%Y-%m-%d") if isinstance(value, (date, datetime)) else str(value)
    market = data.get("market")
    if isinstance(market, dict):
        for key in keys:
            value = market.get(key)
            if isinstance(value, (str, date, datetime)) and str(value).strip():
                return (
                    value.strftime("%Y-%m-%d")
                    if isinstance(value, (date, datetime))
                    else str(value)
                )
    return None


def _assess_zhb_freshness(data: Any, target_date: str) -> Dict[str, Any]:
    """Compare a ZHB package date with the latest market date on/before the target day."""
    actual_raw = _source_as_of_date("zhb", data)
    actual_day = None
    if actual_raw:
        for date_format in ("%Y%m%d", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
            try:
                actual_day = datetime.strptime(actual_raw, date_format).date()
                break
            except ValueError:
                continue

    try:
        target_day = datetime.strptime(str(target_date), "%Y%m%d").date()
        from stock_common.stock_calendar import latest_market_data_date

        expected_day = latest_market_data_date(target_day)
    except Exception as exc:
        return {
            "status": "unverified",
            "expected_as_of_date": None,
            "actual_as_of_date": actual_day.strftime("%Y%m%d") if actual_day else actual_raw,
            "matches_expected_date": False,
            "reason": f"无法校验 ZHB 来源日期: {type(exc).__name__}: {str(exc)[:160]}",
        }

    expected = expected_day.strftime("%Y%m%d")
    actual = actual_day.strftime("%Y%m%d") if actual_day else None
    if actual_day is None:
        status = "unknown"
        reason = f"ZHB 未提供可识别的数据日期；目标交易日为 {expected}"
    elif actual_day < expected_day:
        status = "stale"
        reason = f"ZHB 数据日期 {actual} 落后目标交易日 {expected}；数据已保留但不视为最新"
    elif actual_day > expected_day:
        status = "future"
        reason = f"ZHB 数据日期 {actual} 晚于目标交易日 {expected}；该样本不能与目标日对齐"
    else:
        status = "current"
        reason = None
    return {
        "status": status,
        "expected_as_of_date": expected,
        "actual_as_of_date": actual,
        "matches_expected_date": status == "current",
        "reason": reason,
    }


def _apply_zhb_freshness(
    ok: bool, info: Dict[str, Any], data: Any, target_date: str
) -> tuple[bool, Dict[str, Any]]:
    """Keep cached ZHB rows, but prevent a date-mismatched package from reporting ok."""
    result = dict(info)
    freshness = _assess_zhb_freshness(data, target_date)
    result["freshness"] = freshness
    if freshness["status"] != "current":
        result["freshness_issue"] = freshness["reason"]
        if result.get("status") == "ok":
            result["status"] = "partial"
        ok = False
    return ok, result


def _classify_capture_error(error: Any) -> tuple[str, str]:
    """Classify an error marker without treating a local skip as a remote failure.

    The classification is diagnostic only. The original marker remains in the raw
    archive, and ambiguous text is deliberately reported as unknown.
    """
    text = str(error or "")
    normalized = text.lower()
    attempts_match = re.search(r"\battempts?\s*[=:]\s*(\d+)", normalized)
    attempts = int(attempts_match.group(1)) if attempts_match else None
    suppressed = any(
        marker in normalized
        for marker in (
            "ip_banned",
            "circuit_open",
            "suppressed_after_failures",
            "blocked_until_manual_review",
            "封禁跳过",
            "已封禁",
            "熔断跳过",
        )
    )
    if suppressed and (attempts is None or attempts == 0):
        return "suppressed_before_request", "not_attempted"

    status_match = re.search(r"(?:http\s*|status\s*[=:]?\s*|http_)(\d{3})", normalized)
    status_code = int(status_match.group(1)) if status_match else None
    if status_code in (403, 429):
        return "rate_limited_response", "client_attempted"
    if status_code is not None and status_code >= 400:
        return "http_response_failure", "client_attempted"

    if any(
        marker in normalized
        for marker in (
            "timeout",
            "connectionerror",
            "connection_error",
            "remote disconnected",
            "connection reset",
            "proxyerror",
            "dns",
            "socket",
        )
    ):
        return "transport_failure", "client_attempted"
    if any(
        marker in normalized
        for marker in (
            "parse failed",
            "invalid json",
            "jsondecodeerror",
            "empty payload",
            "missing required",
            "missing contract",
            "unexpected payload",
            "response parse failed",
        )
    ):
        return "payload_or_contract_failure", "client_attempted"
    if attempts is not None and attempts > 0:
        return "request_failure", "client_attempted"
    return "other_failure", "unknown"


def _capture_error_diagnostic(error: Any, path: tuple) -> Dict[str, Any]:
    """Return additive, machine-readable context without changing collection decisions."""
    category, attempt_state = _classify_capture_error(error)
    text = " ".join(str(error or "").split())
    normalized = text.lower()
    status_match = re.search(r"(?:http\s*|status\s*[=:]?\s*|http_)(\d{3})", normalized)
    status_code = int(status_match.group(1)) if status_match else None
    host_match = re.search(r"https?://([^/:?#\s]+)", text, flags=re.IGNORECASE)
    host = host_match.group(1).lower() if host_match else None

    phase_by_category = {
        "suppressed_before_request": "request_admission",
        "rate_limited_response": "request",
        "http_response_failure": "request",
        "transport_failure": "request",
        "request_failure": "request",
        "payload_or_contract_failure": "response_validation",
        "other_failure": "unknown",
    }
    risk_by_category = {
        "suppressed_before_request": "circuit_breaker",
        "rate_limited_response": "rate_limit",
        "http_response_failure": "provider_response",
        "transport_failure": "transport",
        "request_failure": "request",
        "payload_or_contract_failure": "payload_contract",
        "other_failure": "unknown",
    }
    retryable_hint: Optional[bool]
    if category in {"suppressed_before_request", "rate_limited_response"}:
        retryable_hint = False
    elif category == "transport_failure" or (status_code is not None and status_code >= 500):
        retryable_hint = True
    elif status_code is not None and status_code >= 400:
        retryable_hint = False
    else:
        retryable_hint = None

    safe_error = re.sub(
        r"https?://([^\s?#]+)\?[^\s#]*",
        r"https://\1?[query redacted]",
        text,
        flags=re.IGNORECASE,
    )
    safe_error = re.sub(
        r"(?i)\b(token|api[_-]?key|password|secret|authorization)\b(\s*[=:]\s*)[^&\s,;]+",
        r"\1\2[redacted]",
        safe_error,
    )[:240]

    return {
        "code": category,
        "phase": phase_by_category.get(category, "unknown"),
        "request_attempt_state": attempt_state,
        "retryable_hint": retryable_hint,
        "risk_family": risk_by_category.get(category, "unknown"),
        "host": host,
        "http_status": status_code,
        "raw_error": safe_error,
        "path": ".".join(map(str, path))[:240],
    }


def assess_result(
    data: Any,
    expected_symbols: Optional[List[str]] = None,
    required_paths: Optional[List[tuple]] = None,
) -> tuple:
    """Assess errors, deferred work, source contract keys and requested stock coverage."""
    n_err = 0
    sample = None
    n_skipped = 0
    n_deferred = 0
    skip_sample = None
    error_categories: Dict[str, int] = {}
    request_attempt_states: Dict[str, int] = {}
    diagnostic_groups: Dict[tuple, Dict[str, Any]] = {}

    def record_error(error: Any, path: tuple) -> None:
        nonlocal n_err, sample
        n_err += 1
        text = str(error)
        if sample is None:
            sample = text[:160]
        category, attempt_state = _classify_capture_error(error)
        error_categories[category] = error_categories.get(category, 0) + 1
        request_attempt_states[attempt_state] = request_attempt_states.get(attempt_state, 0) + 1
        diagnostic = _capture_error_diagnostic(error, path)
        key = (
            diagnostic["code"],
            diagnostic["phase"],
            diagnostic["risk_family"],
            diagnostic["host"],
            diagnostic["http_status"],
            diagnostic["raw_error"],
        )
        grouped = diagnostic_groups.get(key)
        if grouped is None:
            grouped = {**diagnostic, "count": 0, "paths": []}
            diagnostic_groups[key] = grouped
        grouped["count"] += 1
        path_text = diagnostic["path"]
        if path_text and path_text not in grouped["paths"] and len(grouped["paths"]) < 5:
            grouped["paths"].append(path_text)

    def walk(value: Any, path: tuple = ()) -> None:
        nonlocal n_err, sample, n_skipped, n_deferred, skip_sample
        if isinstance(value, dict):
            if "__error__" in value:
                record_error(value["__error__"], path + ("__error__",))
                return
            if "__skipped__" in value:
                n_skipped += 1
                reason = str(value["__skipped__"])
                if reason.lower().startswith("deferred:"):
                    n_deferred += 1
                if skip_sample is None:
                    skip_sample = reason[:160]
                return
            for key, child in value.items():
                if _is_error_marker_key(key) and child:
                    record_error(child, path + (key,))
                else:
                    walk(child, path + (key,))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, path + (index,))

    walk(data)

    missing_symbols: List[str] = []
    n_total: Optional[int] = None
    n_dead = 0
    if expected_symbols is not None:
        expected = {str(code) for code in expected_symbols}
        stocks = data.get("stocks") if isinstance(data, dict) else None
        received = set(map(str, stocks)) if isinstance(stocks, dict) else set()
        missing_symbols = sorted(expected - received)
        n_total = len(expected)
        if isinstance(stocks, dict):
            n_dead = sum(1 for record in stocks.values() if _has_error_marker(record))
    elif isinstance(data, dict):
        for key in ("stocks", "records", "items"):
            container = data.get(key)
            if isinstance(container, (dict, list)):
                n_total = len(container)
                items = container.values() if isinstance(container, dict) else container
                n_dead = sum(1 for item in items if _has_error_marker(item))
                break

    missing_paths = [path for path in (required_paths or []) if not _path_exists(data, path)]
    n_missing = len(missing_symbols) + len(missing_paths)
    complete = n_err == 0 and n_deferred == 0 and n_missing == 0
    if complete:
        status = "ok"
        ok = True
    else:
        root_error = _has_root_error_marker(data)
        no_stock_response = (
            expected_symbols is not None and n_total and len(missing_symbols) == n_total
        )
        if (
            root_error
            or no_stock_response
            or (n_total is not None and n_total > 0 and n_dead >= n_total)
        ):
            status = "failed"
        else:
            status = "partial"
        ok = False

    info: Dict[str, Any] = {"status": status, "n_error": n_err}
    if n_skipped:
        info["n_skipped"] = n_skipped
        info["skip_sample"] = skip_sample
    if n_deferred:
        info["n_deferred"] = n_deferred
    if n_total is not None:
        info["n_total"] = n_total
        info["n_dead"] = n_dead
    if expected_symbols is not None:
        info["n_expected"] = n_total
        info["n_received"] = n_total - len(missing_symbols) if n_total is not None else 0
        info["n_missing_stocks"] = len(missing_symbols)
        if missing_symbols:
            info["missing_stocks_sample"] = missing_symbols[:10]
    if missing_paths:
        info["n_missing_contracts"] = len(missing_paths)
        info["missing_contracts"] = [".".join(map(str, path)) for path in missing_paths]
    if sample:
        info["error_sample"] = sample
    if error_categories:
        ordered_diagnostics = sorted(
            diagnostic_groups.values(),
            key=lambda item: (-item["count"], item["code"], item["path"]),
        )
        detail_limit = 20
        info["error_diagnostics"] = {
            "schema_version": 1,
            "classification_basis": "error_marker_text",
            "request_attempt_states": request_attempt_states,
            "categories": error_categories,
            "details": ordered_diagnostics[:detail_limit],
            "omitted_detail_groups": max(0, len(ordered_diagnostics) - detail_limit),
        }
    return ok, info


def _source_required_paths(source: str, include_context: bool = False) -> Optional[List[tuple]]:
    required_paths = list(SOURCE_REQUIRED_PATHS.get(source, []))
    if include_context:
        required_paths.extend(CONTEXT_REQUIRED_PATHS.get(source, []))
    return required_paths or None

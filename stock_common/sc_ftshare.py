"""Public FTShare REST adapter for bounded, documented A-share quote snapshots."""

from __future__ import annotations

import os
import json
import re
import threading
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo

import requests

from stock_common.symbol_norm import normalize_symbol

FTSHARE_BASE_URL = "https://market.ft.tech/gateway"
FTSHARE_QUOTE_PATH = "/api/v1/market/data/daec/stocks/all"
FTSHARE_QUOTE_DOC_URL = "https://market.ft.tech/gateway/doc/p/mdsj0xyo"
FTSHARE_INTERFACE_NAME = "A股行情列表"
FTSHARE_MAX_SYMBOLS = 200
FTSHARE_PAGE_SIZE = 40
FTSHARE_MAX_PAGES = 10
FTSHARE_TIMEOUT_SECONDS = 20
FTSHARE_MIN_REQUEST_INTERVAL_SECONDS = 2.0

_SHANGHAI = ZoneInfo("Asia/Shanghai")
_CREDENTIAL_PATH = Path(__file__).resolve().parents[1] / "credentials" / "ftshare_api_key.txt"
_MARKET_SUFFIX = {"SH": "XSHG", "SZ": "XSHE", "BJ": "BJSE"}
_RESPONSE_SUFFIX = re.compile(r"^(\d{6})\.(XSHG|XSHE|BJSE|SH|SZ|BJ)$", re.IGNORECASE)
_REQUEST_LOCK = threading.Lock()
_LAST_REQUEST_MONOTONIC = 0.0


class FTShareRequestError(RuntimeError):
    """A safe, credential-free FTShare REST failure."""


class FTShareRateLimitError(FTShareRequestError):
    """FTShare asked the client to stop because the request was limited."""


def _canonical_symbol(value: object) -> str:
    symbol = normalize_symbol(value)
    suffix = _MARKET_SUFFIX.get(symbol.market)
    if suffix is None:
        raise FTShareRequestError(f"Unsupported FTShare market for {value!r}")
    return f"{symbol.code}.{suffix}"


def _normalize_symbols(symbols: Sequence[object]) -> list[str]:
    if not symbols:
        raise FTShareRequestError("FTShare requires at least one stock symbol")
    if len(symbols) > FTSHARE_MAX_SYMBOLS:
        raise FTShareRequestError(
            f"FTShare capture is limited to {FTSHARE_MAX_SYMBOLS} symbols per invocation"
        )
    normalized: list[str] = []
    for raw_symbol in symbols:
        try:
            symbol = _canonical_symbol(raw_symbol)
        except (TypeError, ValueError) as exc:
            raise FTShareRequestError(f"Invalid FTShare symbol {raw_symbol!r}") from exc
        if symbol in normalized:
            raise FTShareRequestError(f"Duplicate FTShare symbol {symbol}")
        normalized.append(symbol)
    return normalized


def _load_api_key(
    credential_path: Path = _CREDENTIAL_PATH,
    *,
    environ: Mapping[str, str] | None = None,
) -> tuple[str, str]:
    environment = os.environ if environ is None else environ
    key = environment.get("FTSHARE_API_KEY", "").strip()
    if key:
        source = "environment:FTSHARE_API_KEY"
    else:
        try:
            key = credential_path.read_text(encoding="utf-8-sig").strip()
        except OSError as exc:
            raise FTShareRequestError(
                "FTShare key is unavailable; configure FTSHARE_API_KEY or "
                "credentials/ftshare_api_key.txt"
            ) from exc
        source = "credentials/ftshare_api_key.txt"
    if not key or any(character.isspace() for character in key):
        raise FTShareRequestError("FTShare key is empty or malformed")
    return key, source


def _build_filter(symbols: Sequence[str]) -> str:
    encoded_symbols = json.dumps(list(symbols), ensure_ascii=False, separators=(",", ":"))
    return f"symkey IN {encoded_symbols}"


def _parse_capture_date(value: str) -> date:
    text = str(value).strip().replace("-", "")
    try:
        return datetime.strptime(text, "%Y%m%d").date()
    except ValueError as exc:
        raise FTShareRequestError(
            "FTShare capture requires a valid effective trading date"
        ) from exc


def _response_symbol(value: object) -> tuple[str, str]:
    if not isinstance(value, str):
        raise FTShareRequestError("FTShare item is missing the documented symbol field")
    match = _RESPONSE_SUFFIX.fullmatch(value.strip())
    if not match:
        raise FTShareRequestError("FTShare returned a symbol with an unsupported exchange suffix")
    code, market_suffix = match.groups()
    market = {"XSHG": "SH", "XSHE": "SZ", "BJSE": "BJ"}.get(market_suffix.upper())
    if market is None:
        market = {"SH": "SH", "SZ": "SZ", "BJ": "BJ"}[market_suffix.upper()]
    canonical = f"{code}.{_MARKET_SUFFIX[market]}"
    return value.strip(), canonical


def _quote_date(item: Mapping[str, Any]) -> date | None:
    value = item.get("ts_millis")
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        return None
    try:
        timestamp = int(value)
        if timestamp <= 0:
            return None
        return datetime.fromtimestamp(timestamp / 1000, tz=_SHANGHAI).date()
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def _rate_limit_slot() -> None:
    global _LAST_REQUEST_MONOTONIC
    elapsed = time.monotonic() - _LAST_REQUEST_MONOTONIC
    delay = FTSHARE_MIN_REQUEST_INTERVAL_SECONDS - elapsed
    if delay > 0:
        time.sleep(delay)
    _LAST_REQUEST_MONOTONIC = time.monotonic()


def _fetch_page(
    api_key: str,
    *,
    page: int,
    page_size: int,
    filter_text: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    global _LAST_REQUEST_MONOTONIC
    params: dict[str, str | int] = {
        "page": page,
        "page_size": page_size,
        "filter": filter_text,
    }
    try:
        with _REQUEST_LOCK:
            _rate_limit_slot()
            response = requests.get(
                f"{FTSHARE_BASE_URL}{FTSHARE_QUOTE_PATH}",
                headers={"FTSHARE_API_KEY": api_key, "Accept": "application/json"},
                params=params,
                timeout=FTSHARE_TIMEOUT_SECONDS,
                allow_redirects=False,
            )
            _LAST_REQUEST_MONOTONIC = time.monotonic()
    except requests.RequestException as exc:
        raise FTShareRequestError(
            f"FTShare request failed ({type(exc).__name__}); no retry was attempted"
        ) from exc

    try:
        status_code = int(response.status_code)
        if status_code in (403, 429):
            raise FTShareRateLimitError(
                f"FTShare returned HTTP {status_code}; stop this source immediately, no retry was attempted"
            )
        if status_code != 200:
            raise FTShareRequestError(
                f"FTShare returned HTTP {status_code}; response body was not recorded"
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise FTShareRequestError(
                "FTShare returned invalid JSON; response body was not recorded"
            ) from exc
        if not isinstance(payload, dict):
            raise FTShareRequestError("FTShare response envelope is not an object")
        response_data = payload.get("data")
        if not isinstance(response_data, dict) or not isinstance(response_data.get("items"), list):
            raise FTShareRequestError("FTShare response has no paginated data.items list")
        items = response_data["items"]
        if any(not isinstance(item, dict) for item in items):
            raise FTShareRequestError("FTShare response contains a non-object item")
        metadata = {
            "page": response_data.get("page", page),
            "page_size": response_data.get("page_size", page_size),
            "total_pages": response_data.get("total_pages", 1),
            "total_items": response_data.get("total_items", len(items)),
            "api_code": payload.get("code"),
        }
        return items, metadata
    finally:
        response.close()


def get_a_share_quote_snapshot(
    symbols: Sequence[object],
    *,
    data_date: str,
    credential_path: Path = _CREDENTIAL_PATH,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Fetch a bounded real-time batch and keep only records matching its effective date.

    The endpoint has no historical dimension. ``data_date`` is therefore a validation
    boundary derived from the project trading calendar, never a request for old data.
    """
    selected_symbols = _normalize_symbols(symbols)
    target_date = _parse_capture_date(data_date)
    api_key, credential_source = _load_api_key(credential_path, environ=environ)
    filter_text = _build_filter(selected_symbols)
    page_size = min(FTSHARE_PAGE_SIZE, len(selected_symbols))
    items: list[dict[str, Any]] = []
    page_metadata: list[dict[str, Any]] = []

    page = 1
    total_pages = 1
    while page <= total_pages:
        if page > FTSHARE_MAX_PAGES:
            raise FTShareRequestError(
                f"FTShare response exceeds the {FTSHARE_MAX_PAGES}-page capture limit"
            )
        page_items, metadata = _fetch_page(
            api_key,
            page=page,
            page_size=page_size,
            filter_text=filter_text,
        )
        try:
            reported_pages = int(metadata.get("total_pages", 1))
        except (TypeError, ValueError):
            raise FTShareRequestError("FTShare returned an invalid total_pages value")
        if reported_pages < 1 or reported_pages > FTSHARE_MAX_PAGES:
            raise FTShareRequestError(
                f"FTShare returned an unsupported total_pages value: {reported_pages}"
            )
        if page == 1:
            total_pages = reported_pages
        elif reported_pages != total_pages:
            raise FTShareRequestError("FTShare pagination changed during one capture")
        items.extend(page_items)
        page_metadata.append(metadata)
        page += 1

    requested_set = set(selected_symbols)
    stocks: dict[str, dict[str, Any]] = {}
    quote_dates: set[date] = set()
    skipped: dict[str, str] = {}
    unexpected_symbols = 0
    for item in items:
        _raw_symbol, canonical_symbol = _response_symbol(item.get("symbol"))
        if canonical_symbol not in requested_set:
            unexpected_symbols += 1
            continue
        symbol_code = canonical_symbol.split(".", 1)[0]
        if symbol_code in stocks:
            raise FTShareRequestError("FTShare returned a duplicate stock symbol")
        observed_date = _quote_date(item)
        if observed_date is None:
            skipped[symbol_code] = "missing_or_invalid_exchange_quote_timestamp"
            continue
        quote_dates.add(observed_date)
        if observed_date != target_date:
            skipped[symbol_code] = f"quote_date_mismatch:{observed_date:%Y%m%d}"
            continue
        stocks[symbol_code] = dict(item)

    if not stocks:
        observed = ",".join(sorted(day.strftime("%Y%m%d") for day in quote_dates)) or "unknown"
        raise FTShareRequestError(
            f"FTShare quote date {observed} does not match requested effective date "
            f"{target_date:%Y%m%d}; no historical data was requested or substituted"
        )

    returned_symbols = sorted(
        f"{code}.{_MARKET_SUFFIX[normalize_symbol(code).market]}" for code in stocks
    )
    missing_symbols = sorted(requested_set - set(returned_symbols))
    if missing_symbols:
        for symbol in missing_symbols:
            skipped.setdefault(symbol.split(".", 1)[0], "not_returned_by_ftshare")

    captured_at = datetime.now(_SHANGHAI)
    source_meta = {
        "provider": "FTShare REST Gateway",
        "interface": FTSHARE_INTERFACE_NAME,
        "endpoint": FTSHARE_QUOTE_PATH,
        "documentation_url": FTSHARE_QUOTE_DOC_URL,
        "credential_source": credential_source,
        "capture_kind": "real_time_quote_snapshot",
        "historical_dimension": False,
        "collision_eligible": True,
        "collision_anchor_basis": "official_documented_field_contract",
        "upstream_lineage_status": "unverified",
        "captured_at": captured_at.isoformat(timespec="seconds"),
        "as_of_date": target_date.strftime("%Y-%m-%d"),
        "exchange_quote_dates_observed": sorted(day.strftime("%Y-%m-%d") for day in quote_dates),
        "requested_symbols": selected_symbols,
        "returned_symbols": returned_symbols,
        "missing_symbols": missing_symbols,
        "unexpected_response_symbol_count": unexpected_symbols,
        "pages_requested": len(page_metadata),
        "pagination": page_metadata,
    }
    result: dict[str, Any] = {
        "scheme": "ftshare.rest.a_share_quote",
        "as_of_date": target_date.strftime("%Y-%m-%d"),
        "captured_at": captured_at.isoformat(timespec="seconds"),
        "source_meta": source_meta,
        "stocks": stocks,
    }
    if skipped:
        result["__skipped__"] = skipped
    return result

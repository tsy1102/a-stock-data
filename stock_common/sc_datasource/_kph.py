"""Direct, paginated source adapter for KPH historical limit-up records.

AxData 0.1.4's ``kph_limit_up_history`` request reads only its first 50-row
page. This adapter follows the same KPH endpoint contract and field projection,
but reads every page and records completion metadata for capture evidence.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime
import re
from typing import Any

import requests

KPH_HISTORY_URL = "https://apphis.kaipanhong.com/w1/api/index.php"
PAGE_SIZE = 50
MAX_PAGES = 100

_BASE_PARAMS = {
    "PhoneOSNew": "1",
    "DeviceID": "1a609dd6-b2b8-3bf9-ac40-a77581551454",
    "VerSion": "6.0.6",
    "Token": "0",
    "UserID": "0",
    "Red": "1",
    "apiv": "w45",
}
_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; 2206123SC Build/c069a49.2)",
    "Accept-Encoding": "gzip",
}


def get_kph_limit_up_history(
    trade_date: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Fetch a complete historical KPH limit-up list without proxy or retries.

    Each page uses the shared KPH one-request-per-second process limiter. Any
    page failure aborts the batch so callers cannot mistake partial results for
    a complete source sample.
    """
    normalized_date = _normalize_trade_date(trade_date)
    session = requests.Session()
    session.trust_env = False
    try:
        return _fetch_pages(session, normalized_date)
    except Exception as exc:
        from stock_common import sc_network

        sc_network._mark_levistock_provider_block("kph", exc)
        raise
    finally:
        session.close()


def _fetch_pages(
    session: Any,
    trade_date: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from stock_common import sc_network

    records: list[dict[str, Any]] = []
    page_signatures: set[tuple[str | None, ...]] = set()
    offset = 0
    pages_fetched = 0

    for _ in range(MAX_PAGES):
        sc_network._kph_wait_process_interval()
        response = session.post(
            KPH_HISTORY_URL,
            data={
                **_BASE_PARAMS,
                "a": "HisDaBanList",
                "c": "HisHomeDingPan",
                "Order": "1",
                "st": str(PAGE_SIZE),
                "Index": str(offset),
                "Is_st": "1",
                "PidType": "4",
                "Type": "6",
                "FilterMotherboard": "0",
                "Filter": "0",
                "FilterTIB": "0",
                "FilterGem": "0",
                "Day": trade_date,
            },
            headers=_HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, Mapping):
            raise ValueError("KPH limit-up history returned a non-object response")
        errcode = payload.get("errcode")
        if errcode not in (None, "0", 0):
            raise RuntimeError(f"KPH limit-up history returned errcode={errcode}")
        raw_rows = payload.get("list", [])
        if not isinstance(raw_rows, list):
            raise ValueError("KPH limit-up history response list is not an array")
        if any(
            not isinstance(row, Sequence) or isinstance(row, (str, bytes, bytearray))
            for row in raw_rows
        ):
            raise ValueError("KPH limit-up history contains a malformed row")

        batch = list(raw_rows)
        pages_fetched += 1
        signature = tuple(_clean_text(_at(row, 0)) for row in batch)
        if batch and signature in page_signatures:
            raise RuntimeError(
                f"KPH limit-up history repeated a page at offset={offset}; refusing partial data"
            )
        if batch:
            page_signatures.add(signature)
        records.extend(_parse_limit_history_row(row, trade_date) for row in batch)

        if len(batch) < PAGE_SIZE:
            return records, {
                "page_size": PAGE_SIZE,
                "pages_fetched": pages_fetched,
                "returned_rows": len(records),
                "complete": True,
            }
        offset += len(batch)

    raise RuntimeError(f"KPH limit-up history exceeded {MAX_PAGES} pages")


def _normalize_trade_date(value: str) -> str:
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) != 8:
        raise ValueError("KPH trade_date must be YYYYMMDD or YYYY-MM-DD")
    try:
        parsed = datetime.strptime(digits, "%Y%m%d").date()
    except ValueError as exc:
        raise ValueError("KPH trade_date must be a valid date") from exc
    if parsed >= date.today():
        raise ValueError("KPH historical trade_date must be earlier than today")
    return parsed.isoformat()


def _parse_limit_history_row(row: Sequence[Any], trade_date: str) -> dict[str, Any]:
    return {
        "trade_date": trade_date.replace("-", ""),
        **_identity_from_symbol(_clean_text(_at(row, 0))),
        "name": _clean_text(_at(row, 1)),
        "limit_time": _parse_int(_at(row, 6)),
        "open_time": _parse_int(_at(row, 7)),
        "seal_amount": _parse_float(_at(row, 8)),
        "limit_tag": _clean_text(_at(row, 9)),
        "limit_count": _parse_int(_at(row, 10)),
        "themes": _clean_text(_at(row, 11)),
        "net_inflow": _parse_float(_at(row, 12)),
        "turnover": _parse_float(_at(row, 13)),
        "turnover_rate": _parse_float(_at(row, 14)),
        "market_cap": _parse_float(_at(row, 15)),
        "reason": _clean_text(_at(row, 16)),
        "seal_money": _parse_float(_at(row, 23)),
        "industry_id": _clean_text(_at(row, 26)),
        "industry_limit_up_count": _parse_int(_at(row, 27)),
    }


def _identity_from_symbol(symbol: str | None) -> dict[str, Any]:
    clean = re.sub(r"\D", "", str(symbol or ""))
    if len(clean) != 6:
        return {"instrument_id": None, "symbol": None, "exchange": None}
    if clean.startswith(("6", "5", "9")):
        exchange, suffix = "SSE", "SH"
    elif clean.startswith(("4", "8", "92")):
        exchange, suffix = "BSE", "BJ"
    else:
        exchange, suffix = "SZSE", "SZ"
    return {"instrument_id": f"{clean}.{suffix}", "symbol": clean, "exchange": exchange}


def _at(row: Sequence[Any], index: int) -> Any:
    return row[index] if index < len(row) else None


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return None if not text or text in {"-", "--", "null", "None"} else text


def _parse_float(value: Any) -> float | None:
    text = _clean_text(value)
    if text is None:
        return None
    try:
        return float(text.replace(",", "").replace("%", ""))
    except ValueError:
        return None


def _parse_int(value: Any) -> int | None:
    parsed = _parse_float(value)
    if parsed is None:
        return None
    try:
        return int(parsed)
    except (OverflowError, ValueError):
        return None


__all__ = ["get_kph_limit_up_history"]

from datetime import datetime

import core.tdx_client as tdx_client


def test_quote_trading_date_uses_calendar_for_preopen_and_closed_days():
    sunday = datetime(2026, 10, 18, 16, 0)
    monday_preopen = datetime(2026, 10, 19, 9, 29)
    monday_open = datetime(2026, 10, 19, 9, 30)

    assert tdx_client._is_before_market_open(sunday) is True
    assert tdx_client._get_trading_date_for_quote(sunday) == "2026-10-16"
    assert tdx_client._get_trading_date_for_quote(monday_preopen) == "2026-10-16"
    assert tdx_client._is_before_market_open(monday_open) is False
    assert tdx_client._get_trading_date_for_quote(monday_open) == "2026-10-19"


def test_quote_with_sources_keeps_legacy_dict_and_adds_sidecar(monkeypatch):
    code = "600519"
    cache_key = f"Q:{code}:2026-10-19"
    quote = {"price": 1500.0, "last_close": 1490.0}
    source_map = {"price": "realtime:tdx", "last_close": "zhb:cache"}

    monkeypatch.setattr(tdx_client, "_get_trading_date_for_quote", lambda _now=None: "2026-10-19")
    monkeypatch.setattr(tdx_client, "tdx_get_quote_full", lambda _code: quote)
    monkeypatch.setattr(tdx_client, "_TDX_QUOTE_FIELD_SOURCES_CACHE", {cache_key: source_map})

    returned_quote, returned_sources = tdx_client.tdx_get_quote_full_with_sources(code)

    assert returned_quote is quote
    assert returned_sources == source_map
    assert returned_sources is not source_map

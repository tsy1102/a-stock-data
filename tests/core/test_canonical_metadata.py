from datetime import date, datetime

from core.canonical_metadata import (
    build_field_as_of_dates,
    canonical_data_source,
    filter_zhb_snapshot_fields,
    normalize_as_of_date,
    quote_time_anchor,
)


def test_normalize_as_of_date_accepts_compact_iso_and_datetime():
    assert normalize_as_of_date("20261019") == "2026-10-19"
    assert normalize_as_of_date("2026-10-19") == "2026-10-19"
    assert normalize_as_of_date(datetime(2026, 10, 19, 9, 30)) == "2026-10-19"
    assert normalize_as_of_date("not-a-date") == ""


def test_build_field_as_of_dates_maps_only_known_source_dates():
    field_sources = {
        "price": "zhb:t-1",
        "pe_ttm": "realtime:fuyao",
        "roa": "realtime:tencent:batch",
        "fund_main_5d": "realtime:push2delay-ulist",
        "industry": "zhb:static",
        "shares": "static:tdx",
        "mcap_yi": "calculated",
        "employee_count": "zhb:static",
    }
    dates = build_field_as_of_dates(
        field_sources,
        {"fuyao": "2026-10-17", "tencent": "20261019", "push2delay": "20261019"},
        zhb_data_date="20261016",
    )

    assert dates == {
        "price": "2026-10-16",
        "pe_ttm": "2026-10-17",
        "roa": "2026-10-19",
        "fund_main_5d": "2026-10-19",
        "industry": "2026-10-16",
        "employee_count": "2026-10-16",
    }


def test_static_field_does_not_inherit_unrelated_live_source_date():
    dates = build_field_as_of_dates(
        {"shares": "static:tdx", "industry": "static:zhb"},
        {"tdx": "2026-10-19"},
        zhb_data_date="2026-10-16",
    )

    assert dates == {"industry": "2026-10-16"}


def test_filter_zhb_fields_uses_each_field_and_preserves_report_period():
    seen = []

    def safe_field(name, *, data_date, as_of):
        seen.append((name, data_date, as_of))
        return name == "pe_ttm"

    snapshot = {
        "price": 12.5,
        "pe_ttm": 10.2,
        "report_date": "20260630",
    }
    as_of = datetime(2026, 10, 19, 8, 0)
    result = filter_zhb_snapshot_fields(snapshot, "20261016", as_of=as_of, field_safe=safe_field)

    assert result == {"pe_ttm": 10.2, "report_date": "20260630"}
    assert seen == [
        ("price", "20261016", as_of),
        ("pe_ttm", "20261016", as_of),
    ]


def test_quote_time_anchor_requires_an_exact_date(monkeypatch):
    import stock_common.stock_calendar as calendar

    previous = date(2026, 10, 16)
    monkeypatch.setattr(calendar, "previous_trading_day", lambda *_a, **_k: previous)
    as_of = datetime(2026, 10, 19, 10, 0)

    assert quote_time_anchor("2026-10-19", as_of) == "t_day"
    assert quote_time_anchor("20261016", as_of) == "t-1"
    assert quote_time_anchor("2026-10-15", as_of) == "unknown"
    assert quote_time_anchor("", as_of) == "unknown"


def test_canonical_data_source_uses_stable_contract_values():
    assert canonical_data_source("zhb:cache") == "zhb"
    assert canonical_data_source("realtime:tdx") == "tdx"
    assert canonical_data_source("tdx:0x0010") == "tdx"
    assert canonical_data_source("realtime:tencent:batch") == "http"
    assert canonical_data_source("realtime:batch:source_unknown") == "unknown"
    assert canonical_data_source("calculated:price_change_pct") == "unknown"

from datetime import date

import pytest

from stock_common.sc_datasource._zhb import (
    zhb_field_max_delay_days,
    zhb_field_safe,
)


@pytest.mark.parametrize(
    ("field_name", "expected_days"),
    [
        ("price", 0),
        ("turnover_pct", 0),
        ("streak_days", 1),
        ("pe_ttm", 3),
        ("industry", 90),
    ],
)
def test_zhb_field_max_delay_matches_abcd_classes(field_name, expected_days):
    assert zhb_field_max_delay_days(field_name) == expected_days


def test_explicit_snapshot_date_uses_trading_day_age_and_field_class(monkeypatch):
    import stock_common.stock_calendar as calendar

    latest = date(2026, 10, 19)
    monkeypatch.setattr(calendar, "latest_market_data_date", lambda _as_of=None: latest)
    monkeypatch.setattr(
        calendar,
        "trading_days_between",
        lambda data_date, end: 1 if data_date == date(2026, 10, 16) and end == latest else 0,
    )

    assert not zhb_field_safe("price", data_date="20261016")
    assert zhb_field_safe("streak_days", data_date="20261016")
    assert zhb_field_safe("pe_ttm", data_date="20261016")
    assert zhb_field_safe("industry", data_date="20261016")


def test_future_or_invalid_snapshot_date_is_never_fresh(monkeypatch):
    import stock_common.stock_calendar as calendar

    latest = date(2026, 10, 19)
    monkeypatch.setattr(calendar, "latest_market_data_date", lambda _as_of=None: latest)
    monkeypatch.setattr(calendar, "trading_days_between", lambda *_a: -1)

    assert not zhb_field_safe("industry", data_date="20261020")
    assert not zhb_field_safe("industry", data_date="invalid")
    assert not zhb_field_safe("price", data_date="")

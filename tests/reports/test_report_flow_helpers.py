from datetime import date

import stock_common
from stock_common.sc_report_runner import report_fund_flow_120d
from stock_common.sc_report_runner import unique_trading_flow_rows


def test_unique_trading_flow_rows_filters_sorts_and_prefers_populated_duplicate(
    monkeypatch,
):
    monkeypatch.setattr(
        "stock_common.stock_calendar.is_trading_day",
        lambda day: day.weekday() < 5,
    )
    first_duplicate = {"date": "2026-11-06", "main_net": None, "row": "empty"}
    populated_duplicate = {
        "trade_date": "2026-11-06T15:00:00",
        "main_net": 12.5,
        "row": "populated",
    }
    rows = [
        first_duplicate,
        populated_duplicate,
        {"date": "2026-11-06", "main_net": 20.0, "row": "later duplicate"},
        {"date": "2026-11-05", "main_net": 3.0},
        {"date": "2026-11-07", "main_net": 99.0},
        {"date": "not-a-date", "main_net": 1.0},
        None,
    ]

    result = unique_trading_flow_rows(rows)

    assert result == [populated_duplicate, {"date": "2026-11-05", "main_net": 3.0}]


def test_unique_trading_flow_rows_skips_calendar_errors(monkeypatch):
    def is_trading_day(day: date) -> bool:
        if day.day == 5:
            raise NotImplementedError
        return True

    monkeypatch.setattr("stock_common.stock_calendar.is_trading_day", is_trading_day)

    assert unique_trading_flow_rows(
        [
            {"date": "2026-11-05", "main_net": 1.0},
            {"date": "2026-11-06", "main_net": 2.0},
        ]
    ) == [{"date": "2026-11-06", "main_net": 2.0}]


def test_report_fund_flow_uses_shared_history_adapter(monkeypatch):
    calls = []
    expected = {"data": [{"date": "2026-11-06", "main_net": 2.0}]}

    def fake_history(code, days, *, prefer):
        calls.append((code, days, prefer))
        return expected

    monkeypatch.setattr(stock_common, "get_history_fund_flow_120d", fake_history)

    assert report_fund_flow_120d("600519") is expected
    assert calls == [("600519", 60, "em")]

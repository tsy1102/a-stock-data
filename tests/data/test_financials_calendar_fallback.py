from datetime import date

import chinese_calendar

from stock_common import stock_calendar
from stock_common.sc_datasource import _financials


def test_calendar_fallback_does_not_open_makeup_weekends(monkeypatch):
    makeup_weekend = date(2026, 10, 10)
    assert chinese_calendar.is_workday(makeup_weekend) is True

    def calendar_out_of_range(_day):
        raise NotImplementedError("test calendar fallback")

    monkeypatch.setattr(stock_calendar, "is_workday", calendar_out_of_range)

    assert _financials.is_trading_day(makeup_weekend) is False

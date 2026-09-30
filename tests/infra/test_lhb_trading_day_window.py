from datetime import date
from core import stock_cache
from stock_common import stock_calendar
from stock_common.sc_datasource import _eastmoney


def test_market_and_single_stock_lhb_queries_use_trading_day_bounds(monkeypatch):
    expected_window = (date(2026, 9, 22), date(2026, 9, 28))
    monkeypatch.setattr(stock_calendar, "trading_day_window", lambda count: expected_window)

    market_calls = []

    class Response:
        def json(self):
            return {"result": {"data": []}}

    def fake_request(url, **kwargs):
        market_calls.append((url, kwargs))
        return Response()

    monkeypatch.setattr(_eastmoney, "_quick_request", fake_request)
    _eastmoney._get_recent_dragon_tiger_trading_window.__wrapped__(5)

    assert len(market_calls) == 1
    assert market_calls[0][1]["params"]["filter"] == (
        "(TRADE_DATE>='2026-09-22')(TRADE_DATE<='2026-09-28')"
    )

    stock_calls = []

    def fake_datacenter(code, report_name, **kwargs):
        stock_calls.append((code, report_name, kwargs))
        return []

    monkeypatch.setattr(_eastmoney, "eastmoney_datacenter", fake_datacenter)
    _eastmoney._get_dragon_tiger_board_trading_window.__wrapped__(
        "600000", days=5, include_seats=False, enhance_seats=False
    )

    assert len(stock_calls) == 1
    assert stock_calls[0][2]["filter_str"] == (
        '(SECURITY_CODE="600000")(TRADE_DATE>=\'2026-09-22\')' '(TRADE_DATE<=\'2026-09-28\')'
    )


def test_lhb_window_cache_namespace_changes_with_trading_day_semantics():
    old_key = stock_cache._build_key("dragon_tiger", "get_recent_dragon_tiger", 5)
    new_key = stock_cache._build_key("dragon_tiger", "_get_recent_dragon_tiger_trading_window", 5)

    assert old_key != new_key

import asyncio
from threading import get_ident

from stock_common import get_financial_report_with_fallback_async
from stock_common.sc_datasource import _financials


def test_financial_report_fallback_async_runs_once_in_worker_thread(monkeypatch):
    caller_thread = get_ident()
    calls = []
    expected = [
        {
            "报告日": "2026-06-30",
            "营业总收入": "1000",
            "营业成本": "600",
            "净利润": "100",
        }
    ]

    def fake_fallback(code, num_periods):
        calls.append((code, num_periods, get_ident()))
        return expected

    monkeypatch.setattr(_financials, "get_financial_report_with_fallback", fake_fallback)

    result = asyncio.run(get_financial_report_with_fallback_async("600000", num_periods=8))

    assert result == expected
    assert len(calls) == 1
    assert calls[0][:2] == ("600000", 8)
    assert calls[0][2] != caller_thread

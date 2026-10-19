import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import get_ident

from stock_common import get_financial_report_with_fallback_async
from stock_common.sc_datasource import _financials


class _ImmediateAwaitable:
    def __init__(self, value):
        self.value = value

    def __await__(self):
        if False:
            yield None
        return self.value


def _complete_without_event_loop(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as completed:
        return completed.value
    coroutine.close()
    raise AssertionError("coroutine unexpectedly suspended")


def test_financial_report_fallback_async_delegates_once_to_thread(monkeypatch):
    caller_thread = get_ident()
    dispatches = []
    fallback_calls = []
    expected = [
        {
            "报告日": "2026-06-30",
            "营业总收入": "1000",
            "营业成本": "600",
            "净利润": "100",
        }
    ]

    def fake_fallback(code, num_periods):
        fallback_calls.append((code, num_periods, get_ident()))
        return expected

    def fake_to_thread(function, /, *args, **kwargs):
        dispatches.append((function, args, kwargs))
        with ThreadPoolExecutor(max_workers=1) as executor:
            result = executor.submit(function, *args, **kwargs).result()
        return _ImmediateAwaitable(result)

    monkeypatch.setattr(_financials, "get_financial_report_with_fallback", fake_fallback)
    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)

    result = _complete_without_event_loop(
        get_financial_report_with_fallback_async("600000", num_periods=8)
    )

    assert result == expected
    assert len(fallback_calls) == 1
    assert fallback_calls[0][:2] == ("600000", 8)
    assert fallback_calls[0][2] != caller_thread
    assert dispatches == [(fake_fallback, ("600000", 8), {})]

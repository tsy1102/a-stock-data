from __future__ import annotations

from typing import Any

import pytest

from stock_common.sc_datasource import _eastmoney


class _Response:
    status_code = 200

    def json(self) -> dict[str, Any]:
        return {"result": {"data": [{"SECURITY_CODE": "600000"}, None, "invalid"]}}


def test_sync_datacenter_preserves_market_filter_paging_and_row_contract(monkeypatch):
    calls = []

    def fake_request(url, **kwargs):
        calls.append((url, kwargs))
        return _Response()

    monkeypatch.setattr(_eastmoney, "_quick_request", fake_request)

    rows = _eastmoney.eastmoney_datacenter(
        "",
        "RPT_MARKET",
        page_size=7,
        sort_columns="TRADE_DATE",
        sort_types="1",
        page_index=3,
    )

    assert rows == [{"SECURITY_CODE": "600000"}]
    assert len(calls) == 1
    url, kwargs = calls[0]
    assert url == _eastmoney.DATACENTER_URL
    assert kwargs["params"] == {
        "reportName": "RPT_MARKET",
        "columns": "ALL",
        "filter": "",
        "pageNumber": "3",
        "pageSize": "7",
        "sortColumns": "TRADE_DATE",
        "sortTypes": "1",
        "source": "WEB",
        "client": "WEB",
    }
    assert kwargs["headers"] == {"User-Agent": _eastmoney.UA}
    assert kwargs["timeout"] == 15


def test_async_datacenter_keeps_retry_adapter_and_market_filter_contract(monkeypatch):
    calls = []

    async def fake_request(session, url, **kwargs):
        calls.append((session, url, kwargs))
        return {"result": {"data": [{"SECURITY_CODE": "600000"}, None]}}

    monkeypatch.setattr(_eastmoney, "_async_request_with_retry", fake_request)
    session = object()

    request = _eastmoney.eastmoney_datacenter_async(
        session,
        "",
        "RPT_MARKET",
        page_size=9,
        sort_columns="TRADE_DATE",
        sort_types="1",
    )
    # Both the request stub and adapter complete without I/O, so drive the
    # coroutine directly and avoid Windows event-loop/socketpair setup here.
    with pytest.raises(StopIteration) as completed:
        request.send(None)
    rows = completed.value.value

    assert rows == [{"SECURITY_CODE": "600000"}]
    assert len(calls) == 1
    actual_session, url, kwargs = calls[0]
    assert actual_session is session
    assert url == _eastmoney.DATACENTER_URL
    assert kwargs["params"] == {
        "reportName": "RPT_MARKET",
        "columns": "ALL",
        "filter": "",
        "pageNumber": "1",
        "pageSize": "9",
        "sortColumns": "TRADE_DATE",
        "sortTypes": "1",
        "source": "WEB",
        "client": "WEB",
    }
    assert kwargs["headers"] == {"User-Agent": _eastmoney.UA}
    assert kwargs["timeout"] == 15

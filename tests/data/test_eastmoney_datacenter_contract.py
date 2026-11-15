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


def test_sync_northbound_keeps_missing_change_values_distinct_from_zero(monkeypatch):
    rows = [
        {
            "TRADE_DATE": "2026-09-30 00:00:00",
            "HOLD_SHARES": 100,
            "HOLD_MARKET_CAP": 250,
            "FREE_SHARES_RATIO": 1.25,
            "CHANGE_RATE": 0,
        },
        {
            "TRADE_DATE": "2026-06-30 00:00:00",
            "HOLD_SHARES": 90,
            "HOLD_MARKET_CAP": 200,
            "FREE_SHARES_RATIO": 1.0,
            "CHANGE_SHARES": 0,
            "CHANGE_RATE": "NaN",
        },
    ]
    monkeypatch.setattr(_eastmoney, "eastmoney_datacenter", lambda *_args, **_kwargs: rows)

    result = _eastmoney.get_northbound_hold.__wrapped__("600519", days=2)

    assert result[0]["change_shares"] is None
    assert result[0]["change_ratio"] == 0
    assert result[1]["change_shares"] == 0
    assert result[1]["change_ratio"] is None


def test_async_northbound_keeps_missing_change_values_distinct_from_zero(monkeypatch):
    rows = [
        {
            "TRADE_DATE": "2026-09-30 00:00:00",
            "HOLD_SHARES": 100,
            "HOLD_MARKET_CAP": 250,
            "FREE_SHARES_RATIO": 1.25,
            "CHANGE_RATE": 0,
        },
        {
            "TRADE_DATE": "2026-06-30 00:00:00",
            "HOLD_SHARES": 90,
            "HOLD_MARKET_CAP": 200,
            "FREE_SHARES_RATIO": 1.0,
            "CHANGE_SHARES": 0,
            "CHANGE_RATE": float("nan"),
        },
    ]

    async def fake_datacenter(*_args, **_kwargs):
        return rows

    monkeypatch.setattr(_eastmoney, "eastmoney_datacenter_async", fake_datacenter)
    request = _eastmoney.get_northbound_hold_async(object(), "600519", days=2)
    with pytest.raises(StopIteration) as completed:
        request.send(None)
    result = completed.value.value

    assert result[0]["change_shares"] is None
    assert result[0]["change_ratio"] == 0
    assert result[1]["change_shares"] == 0
    assert result[1]["change_ratio"] is None


def test_legacy_northbound_csv_does_not_treat_ambiguous_zero_as_real(monkeypatch, tmp_path):
    cache_path = tmp_path / "northbound_600519.csv"
    cache_path.write_text(
        "date,hold_shares,market_cap,hold_ratio,change_shares,change_ratio\n"
        "2026-09-30,100,250,1.25,0,0\n"
        "2026-06-30,90,200,1.0,12,-0.5\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(_eastmoney, "_northbound_cache_path", lambda _code: str(cache_path))

    result = _eastmoney._load_northbound_cache("600519", days=2)

    assert result[0]["change_shares"] is None
    assert result[0]["change_ratio"] is None
    assert result[1]["change_shares"] == 12
    assert result[1]["change_ratio"] == -0.5

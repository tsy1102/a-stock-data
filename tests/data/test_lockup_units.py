"""The lockup adapter returns share counts in individual shares."""

from datetime import date, timedelta

import pytest

from core import stock_cache
from stock_common.sc_datasource import _eastmoney, _financials


def _install_lockup_source_mocks(monkeypatch, history_rows, upcoming_rows):
    monkeypatch.setattr("core.tdx_client.tdx_get_share_capital", lambda _code: {})
    monkeypatch.setattr(_eastmoney, "_em_filter", lambda *_args, **_kwargs: history_rows)
    monkeypatch.setattr(
        _eastmoney,
        "eastmoney_datacenter",
        lambda *_args, **_kwargs: upcoming_rows,
    )


def test_history_and_upcoming_values_convert_wan_shares_to_shares(monkeypatch):
    monkeypatch.setattr(stock_cache, "_DISABLE_CACHE", True)
    future_date = (date.today() + timedelta(days=1)).isoformat()
    history_rows = [
        {
            "FREE_DATE": "2026-01-01",
            "FREE_SHARES_TYPE": "历史解禁",
            "FREE_SHARES": "12.5",
            "ABLE_FREE_SHARES": "9.25",
            "FREE_RATIO": 0.25,
        }
    ]
    upcoming_rows = [
        {
            "FREE_DATE": future_date,
            "FREE_SHARES_TYPE": "待解禁",
            "FREE_SHARES": "1.2",
            "ABLE_FREE_SHARES": "0.75",
            "FREE_RATIO": 0.125,
        }
    ]
    _install_lockup_source_mocks(monkeypatch, history_rows, upcoming_rows)

    result = _financials.get_lockup_expiry("600519", days=30, include_history=True)

    assert result["history"][0]["shares"] == pytest.approx(125_000)
    assert result["history"][0]["able_shares"] == pytest.approx(92_500)
    assert result["history"][0]["ratio"] == 25.0
    assert result["upcoming"][0]["shares"] == pytest.approx(12_000)
    assert result["upcoming"][0]["able_shares"] == pytest.approx(7_500)
    assert result["upcoming"][0]["ratio"] == 12.5


def test_unit_change_uses_a_new_cache_namespace(monkeypatch):
    reads = []
    future_date = (date.today() + timedelta(days=1)).isoformat()
    stale_result = [{"date": future_date, "shares": 1.2, "ratio": 1.0}]

    def fake_get_cache(category, *_args, **_kwargs):
        reads.append(category)
        return stale_result if category == "lockup_expiry" else None

    monkeypatch.setattr(stock_cache, "_DISABLE_CACHE", False)
    monkeypatch.setattr(stock_cache, "get_cache", fake_get_cache)
    monkeypatch.setattr(stock_cache, "set_cache", lambda *_args, **_kwargs: None)
    _install_lockup_source_mocks(
        monkeypatch,
        [],
        [
            {
                "FREE_DATE": future_date,
                "FREE_SHARES_TYPE": "待解禁",
                "FREE_SHARES": "1.2",
                "ABLE_FREE_SHARES": "0.75",
                "FREE_RATIO": 0.125,
            }
        ],
    )

    result = _financials.get_lockup_expiry("600519", days=30)

    assert result[0]["shares"] == pytest.approx(12_000)
    assert reads and set(reads) == {"lockup_expiry_shares_v2"}
    assert stock_cache.TTL["lockup_expiry_shares_v2"] == stock_cache.TTL["lockup_expiry"]
    assert (
        stock_cache._SOFT_EXPIRY_WINDOW["lockup_expiry_shares_v2"]
        == stock_cache._SOFT_EXPIRY_WINDOW["lockup_expiry"]
    )

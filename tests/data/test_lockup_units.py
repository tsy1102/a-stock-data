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

    assert result["history"][0]["shares"] == pytest.approx(92_500)
    assert result["history"][0]["able_shares"] == pytest.approx(92_500)
    assert result["history"][0]["free_shares"] == pytest.approx(125_000)
    assert result["history"][0]["shares_is_actual"] is True
    assert result["history"][0]["ratio"] == 25.0
    assert result["upcoming"][0]["shares"] == pytest.approx(7_500)
    assert result["upcoming"][0]["able_shares"] == pytest.approx(7_500)
    assert result["upcoming"][0]["free_shares"] == pytest.approx(12_000)
    assert result["upcoming"][0]["shares_is_actual"] is True
    assert result["upcoming"][0]["ratio"] == 12.5


def test_upcoming_rows_are_date_filtered_and_use_actual_available_shares(monkeypatch):
    monkeypatch.setattr(stock_cache, "_DISABLE_CACHE", True)
    today = date.today()
    past_date = (today - timedelta(days=1)).isoformat()
    today_date = today.isoformat()
    future_date = (today + timedelta(days=1)).isoformat()
    out_of_range_date = (today + timedelta(days=31)).isoformat()

    def row(event_date, free_shares, able_shares):
        return {
            "FREE_DATE": event_date,
            "FREE_SHARES_TYPE": "股权激励限售股份",
            "FREE_SHARES": free_shares,
            "ABLE_FREE_SHARES": able_shares,
            "FREE_RATIO": 0.0004,
        }

    _install_lockup_source_mocks(
        monkeypatch,
        [row(past_date, 336_502, 141.4), row(future_date, 8, 2)],
        [
            row(past_date, 336_502, 141.4),
            row(today_date, 10, 3),
            row(future_date, 20, 4),
            row(out_of_range_date, 30, 5),
            {
                "FREE_DATE": future_date,
                "FREE_SHARES_TYPE": "实际数量缺失",
                "FREE_SHARES": 40,
                "ABLE_FREE_SHARES": None,
                "FREE_RATIO": 0.0004,
            },
        ],
    )

    result = _financials.get_lockup_expiry("600519", days=30, include_history=True)

    assert [item["date"] for item in result["history"]] == [past_date]
    assert [item["date"] for item in result["upcoming"]] == [today_date, future_date, future_date]
    assert [item["shares"] for item in result["upcoming"]] == [30_000, 40_000, 400_000]
    assert [item["free_shares"] for item in result["upcoming"]] == [100_000, 200_000, 400_000]
    assert [item["shares_is_actual"] for item in result["upcoming"]] == [True, True, False]


def test_f10_lockup_rows_use_normalized_shares_and_current_date(monkeypatch):
    monkeypatch.setattr(stock_cache, "_DISABLE_CACHE", True)
    today = date.today()
    past_date = (today - timedelta(days=1)).isoformat()
    today_date = today.isoformat()
    out_of_range_date = (today + timedelta(days=31)).isoformat()
    monkeypatch.setattr(
        "core.tdx_client.tdx_get_share_capital",
        lambda _code: {
            "lockup_expiry": [
                {
                    "解禁日期": past_date,
                    "解禁类型": "历史解禁",
                    "解禁数量(万)": 100,
                    "解禁比例(%)": 0.5,
                },
                {
                    "解禁日期": today_date,
                    "解禁类型": "当日解禁",
                    "解禁数量(万)": 200,
                    "解禁比例(%)": 1.0,
                },
                {
                    "解禁日期": out_of_range_date,
                    "解禁类型": "窗口外",
                    "解禁数量(万)": 300,
                    "解禁比例(%)": 1.5,
                },
            ]
        },
    )

    result = _financials.get_lockup_expiry("600519", days=30, include_history=True)

    assert [item["date"] for item in result["history"]] == [past_date]
    assert [item["date"] for item in result["upcoming"]] == [today_date]
    assert result["history"][0]["shares"] == pytest.approx(1_000_000)
    assert result["upcoming"][0]["shares"] == pytest.approx(2_000_000)
    assert result["upcoming"][0]["able_shares"] is None
    assert result["upcoming"][0]["free_shares"] == pytest.approx(2_000_000)
    assert result["upcoming"][0]["shares_is_actual"] is False


def test_stale_upcoming_cache_is_rejected_and_new_namespace_is_used(monkeypatch):
    reads = []
    future_date = (date.today() + timedelta(days=1)).isoformat()
    stale_date = (date.today() - timedelta(days=1)).isoformat()
    stale_result = [{"date": stale_date, "shares": 1.2, "ratio": 1.0}]

    def fake_get_cache(category, *_args, **_kwargs):
        reads.append(category)
        return stale_result if category == "lockup_expiry_shares_v4" else None

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

    assert result[0]["shares"] == pytest.approx(7_500)
    assert reads and set(reads) == {"lockup_expiry_shares_v4"}
    assert stock_cache.TTL["lockup_expiry_shares_v4"] == stock_cache.TTL["lockup_expiry"]
    assert (
        stock_cache._SOFT_EXPIRY_WINDOW["lockup_expiry_shares_v4"]
        == stock_cache._SOFT_EXPIRY_WINDOW["lockup_expiry"]
    )

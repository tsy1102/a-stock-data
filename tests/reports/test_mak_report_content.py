import get_mak_report
import stock_common.sc_plate_rot as plate_rotation
from datetime import date as Date, datetime as DateTime, timedelta


def test_unqueried_and_unverified_limit_pool_sources_are_labeled_separately():
    source_text, status = get_mak_report._format_limit_pool_source_summary(
        {"cls": 47, "kpl": 47, "fupan": 47, "push2ex": None},
        47,
        unqueried_sources=["push2ex"],
    )

    assert "CLS=不纳入" in source_text
    assert "KPL(开盘啦)=47" in source_text
    assert "KPH复盘榜=不纳入" in source_text
    assert "东财Push2=未查询" in source_text
    assert "仅有 KPL 日期标签匹配的观测值" in status
    assert "来源实际数据日未核实" in status
    assert "失败" not in status


def test_missing_main_net_summary_explains_shared_cooldown():
    lines = get_mak_report._main_flow_summary_lines({}, 3159, 0, source_status="shared_cooldown")

    assert any("push2delay 共享风控冷却中" in line for line in lines)
    assert any("不代表零净流" in line for line in lines)


def test_main_net_date_filter_uses_only_verified_rows_matching_market_date():
    quotes = {
        "600001": {
            "_source_as_of_date": "2026-11-24",
            "_source_as_of_date_status": "verified",
            "main_net_inflow_wan": 12.5,
        },
        "600002": {
            "_source_as_of_date": "2026-11-23",
            "_source_as_of_date_status": "verified",
            "main_net_inflow_wan": -5.0,
        },
        "600003": {
            "_source_as_of_date": "",
            "_source_as_of_date_status": "conflict",
            "main_net_inflow_wan": 8.0,
        },
        "600004": {
            "_source_as_of_date": "2026-11-24",
            "_source_as_of_date_status": "verified",
            "main_net_inflow_wan": None,
        },
        "600005": {
            "_source_as_of_date": "2026-11-24",
            "_source_as_of_date_status": "verified",
            "main_net_inflow_wan": 0.0,
        },
    }

    flows, note, stats = get_mak_report._select_ulist_main_net_for_date(quotes, "2026-11-24")

    assert flows == {"600001": 125000.0, "600005": 0.0}
    assert stats == {
        "date_match_rows": 3,
        "date_mismatch_rows": 1,
        "unverified_rows": 1,
        "missing_flow_rows": 1,
    }
    assert "交易日历基准 2026-11-24" in note
    assert "日期不符 1 条" in note
    assert "日期锚缺失/冲突/不完整 1 条" in note


def test_main_net_summary_shows_row_date_conflict_without_reporting_flow_total():
    lines = get_mak_report._main_flow_summary_lines(
        {},
        100,
        0,
        source_status="date_mismatch",
        source_date_note="交易日历基准 2026-11-24；未汇总其他日期。",
    )

    assert any("Ulist 行日期核验" in line for line in lines)
    assert any("行日期与交易日历基准不符" in line for line in lines)
    assert not any("扫描样本主力净额合计" in line for line in lines)


def test_plate_rotation_top_preserves_source_date(monkeypatch):
    monkeypatch.setattr(
        plate_rotation,
        "get_plate_rotation_matrix",
        lambda **_kwargs: {
            "plates": [
                {
                    "rank": 1,
                    "cells": [
                        {
                            "date": "2026-11-24",
                            "code": "803001",
                            "name": "测试板块",
                            "value": "12.3",
                            "color": "red",
                        }
                    ],
                }
            ]
        },
    )

    assert plate_rotation.get_plate_rotation_top("kaipan", 20, 5) == [
        {
            "rank": 1,
            "code": "803001",
            "name": "测试板块",
            "date": "2026-11-24",
            "value": "12.3",
            "color": "red",
        }
    ]


def test_tencent_field_requires_matching_timestamp_and_date():
    quote = {
        "change_pct": 0.0,
        "_field_as_of_dates": {"change_pct": "2026-11-24"},
        "_field_as_of_timestamps": {"change_pct": "2026-11-24 15:01:00"},
    }

    assert get_mak_report._dated_tencent_value(quote, "change_pct") == (
        0.0,
        "2026-11-24",
        "2026-11-24 15:01:00",
    )

    quote["_field_as_of_timestamps"]["change_pct"] = "2026-11-23 15:01:00"
    assert get_mak_report._dated_tencent_value(quote, "change_pct") == (None, "", "")

    quote["_field_as_of_timestamps"].pop("change_pct")
    assert get_mak_report._dated_tencent_value(quote, "change_pct") == (None, "", "")


def test_close_metrics_accept_zero_but_reject_same_day_zhb_before_close(monkeypatch):
    metric_day = "2025-10-31"
    stock = {
        "ret_3d": 0.0,
        "_field_meta": {
            "ret_3d": {
                "source": "zhb:tdxstat",
                "as_of_date": metric_day,
                "status": "verified",
            }
        },
    }
    assert get_mak_report._metric_for_date(
        stock, "ret_3d", metric_day, require_close_quote=True
    ) == (0.0, "eligible")

    class BeforeClose(DateTime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 11, 25, 10, 0, 0)

    monkeypatch.setattr(get_mak_report, "datetime", BeforeClose)
    current_day = "2026-11-25"
    stock["_field_meta"]["ret_3d"]["as_of_date"] = current_day
    assert get_mak_report._metric_for_date(
        stock, "ret_3d", current_day, require_close_quote=True
    ) == (None, "snapshot_not_final_close")


def test_tencent_close_metric_requires_matching_timestamp_at_or_after_1500():
    metric_day = "2026-11-24"
    stock = {
        "ret_3d": 0.0,
        "_field_meta": {
            "ret_3d": {
                "source": "tencent+zhb:tdxstat",
                "as_of_date": metric_day,
                "observed_at": f"{metric_day} 14:59:59",
                "status": "verified",
            }
        },
    }

    assert get_mak_report._metric_for_date(
        stock, "ret_3d", metric_day, require_close_quote=True
    ) == (None, "quote_not_final_close")

    stock["_field_meta"]["ret_3d"]["observed_at"] = f"{metric_day} 15:00:00"
    assert get_mak_report._metric_for_date(
        stock, "ret_3d", metric_day, require_close_quote=True
    ) == (0.0, "eligible")

    stock["_field_meta"]["ret_3d"]["observed_at"] = "2026-11-23 15:00:00"
    assert get_mak_report._metric_for_date(
        stock, "ret_3d", metric_day, require_close_quote=True
    ) == (None, "quote_timestamp_date_mismatch")


def test_invalid_metadata_date_is_not_marked_verified():
    stock = {}
    get_mak_report._set_field_metadata(stock, "change_pct", "zhb:tdxstat", "not-a-date")

    assert stock["_field_meta"]["change_pct"]["status"] == "date_unconfirmed"
    assert stock["_field_meta"]["change_pct"]["as_of_date"] == ""


def test_zhb_annotation_prefers_date_from_the_snapshot_record():
    rows = [{"code": "600001", "_zhb_data_date": "2026-11-24", "change_pct": 0.0}]

    get_mak_report._annotate_zhb_market_fields(rows, "2026-11-25")

    assert rows[0]["_field_meta"]["change_pct"]["as_of_date"] == "2026-11-24"


def test_three_day_return_uses_verified_daily_chain_and_keeps_zero():
    daily = {"change_pct": 0.0, "change_pct_1d": 0.0, "change_pct_2d": 0.0}
    assert get_mak_report._calc_3d_from_daily(daily) == 0.0
    assert get_mak_report._calc_3d_from_daily({"change_pct": 0.0}) is None

    same_day = get_mak_report._calc_3d_from_daily(
        {"change_pct": 99.0, "change_pct_1d": 0.0, "change_pct_2d": 0.0},
        today_change_pct=0.0,
        quote_as_of_date="2026-11-24",
        zhb_as_of_date="2026-11-24",
    )
    assert same_day == 0.0


def test_zhb_builder_preserves_missing_metrics_instead_of_inventing_zero(monkeypatch):
    async def unused_snapshot():
        raise AssertionError("the provided snapshot should be reused")

    monkeypatch.setattr(get_mak_report, "get_market_snapshot_async", unused_snapshot)
    monkeypatch.setattr(get_mak_report, "get_zhb_data_date", lambda: "2026-11-24")
    monkeypatch.setattr(get_mak_report, "zhb_field_safe", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(get_mak_report, "_calc_mcap_yi", lambda *_args: 0.0)
    monkeypatch.setattr(get_mak_report, "_verified_main_net_amount", lambda _code: 0.0)
    monkeypatch.setattr("core.zhb_client.get_stock_name_from_zhb", lambda _code: "测试公司")

    snapshot = {
        "600001": {
            "name": "测试公司",
            "price": None,
            "turnover_pct": None,
            "change_pct": None,
            "amount": None,
        }
    }
    data = get_mak_report.asyncio.run(
        get_mak_report._get_zhb_market_data(snapshot=snapshot, tencent_map={})
    )

    assert len(data) == 1
    row = data[0]
    assert row["price"] is None
    assert row["change_pct"] is None
    assert row["turnover"] is None
    assert row["amount_yi"] is None
    assert "change_pct" not in row["_field_meta"]


def test_zhb_builder_ignores_tencent_values_with_mismatched_row_dates(monkeypatch):
    async def unused_snapshot():
        raise AssertionError("the provided snapshot should be reused")

    monkeypatch.setattr(get_mak_report, "get_market_snapshot_async", unused_snapshot)
    monkeypatch.setattr(get_mak_report, "get_zhb_data_date", lambda: "2026-11-24")
    monkeypatch.setattr(get_mak_report, "zhb_field_safe", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(get_mak_report, "_calc_mcap_yi", lambda *_args: 0.0)
    monkeypatch.setattr(get_mak_report, "_verified_main_net_amount", lambda _code: 0.0)
    monkeypatch.setattr("core.zhb_client.get_stock_name_from_zhb", lambda _code: "测试公司")
    snapshot = {
        "600001": {
            "name": "测试公司",
            "price": 10.0,
            "turnover_pct": 1.0,
            "change_pct": 0.0,
            "change_pct_1d": 0.0,
            "change_pct_2d": 0.0,
            "amount": 0.0,
        }
    }
    quote = {
        "name": "测试公司",
        "price": 99.0,
        "change_pct": 9.0,
        "turnover_pct": 9.0,
        "amount_wan": 9.0,
        "_field_as_of_dates": {
            "price": "2026-11-24",
            "change_pct": "2026-11-24",
            "turnover_pct": "2026-11-24",
            "amount_wan": "2026-11-24",
        },
        "_field_as_of_timestamps": {
            field: "2026-11-23 15:01:00"
            for field in ("price", "change_pct", "turnover_pct", "amount_wan")
        },
        "_field_sources": {
            field: "tencent:qt.gtimg"
            for field in ("price", "change_pct", "turnover_pct", "amount_wan")
        },
    }

    rows = get_mak_report.asyncio.run(
        get_mak_report._get_zhb_market_data(snapshot=snapshot, tencent_map={"600001": quote})
    )

    assert rows[0]["price"] == 10.0
    assert rows[0]["change_pct"] == 0.0
    assert rows[0]["turnover"] == 1.0
    assert rows[0]["amount_yi"] == 0.0
    for field in ("price", "change_pct", "turnover", "amount_yi", "ret_3d"):
        assert rows[0]["_field_meta"][field]["source"] == "zhb:tdxstat"
        assert rows[0]["_field_meta"][field]["as_of_date"] == "2026-11-24"


def test_index_return_requires_complete_exact_trading_date_window(monkeypatch):
    dates = [Date(2026, 11, 24), Date(2026, 11, 23), Date(2026, 11, 20), Date(2026, 11, 19)]
    monkeypatch.setattr(
        "stock_common.stock_calendar.recent_trading_dates",
        lambda count, as_of=None: dates[:count],
    )
    bars = [
        {"date": day.isoformat(), "close": close}
        for day, close in zip(reversed(dates), (10.0, 11.0, 12.0, 14.0))
    ]

    assert get_mak_report._index_return_for_date(bars, "2026-11-24", 3) == 40.0
    assert (
        get_mak_report._index_return_for_date(
            [bar for bar in bars if bar["date"] != "2026-11-20"], "2026-11-24", 3
        )
        is None
    )


def test_stock_rule_coverage_distinguishes_zero_from_unassessed(monkeypatch):
    monkeypatch.setattr(get_mak_report, "get_stock_index", lambda _code: "IDX")
    monkeypatch.setattr(get_mak_report, "get_board_name", lambda *_args: "主板")
    monkeypatch.setattr(get_mak_report, "limit_pct_for", lambda *_args: 10)
    metric_date = "2025-10-31"
    stock = {"code": "600001", "name": "样本", "_field_meta": {}}
    index_returns = {metric_date: {"IDX": {}}}
    for field, period in (("ret_3d", "3d"), ("ret_10d", "10d"), ("ret_20d", "20d")):
        stock[field] = 0.0
        stock["_field_meta"][field] = {
            "source": "zhb:tdxstat",
            "as_of_date": metric_date,
            "status": "verified",
        }
        index_returns[metric_date]["IDX"][field] = 0.0

    evaluated = get_mak_report._evaluate_stock(stock, index_returns, {})
    assert evaluated["signals"] == []
    assert evaluated["rule_status"] == {"3d": "evaluated", "10d": "evaluated", "20d": "evaluated"}

    stale = get_mak_report._evaluate_stock(
        stock, index_returns, {}, expected_data_date="2025-11-03"
    )
    assert stale["signals"] == []
    assert stale["rule_status"] == {
        "3d": "stock_metric_date_mismatch",
        "10d": "stock_metric_date_mismatch",
        "20d": "stock_metric_date_mismatch",
    }

    index_returns[metric_date]["IDX"].pop("ret_10d")
    unevaluated = get_mak_report._evaluate_stock(stock, index_returns, {})
    assert unevaluated["rule_status"]["10d"] == "index_window_missing_or_misaligned"


def test_history_deviation_count_needs_all_date_matched_windows(monkeypatch):
    trading_dates = [Date(2025, 1, 1) + timedelta(days=offset) for offset in range(14)]

    def recent_dates(count, as_of=None):
        index = trading_dates.index(as_of)
        start = max(0, index - count + 1)
        return list(reversed(trading_dates[start : index + 1]))

    monkeypatch.setattr("stock_common.stock_calendar.recent_trading_dates", recent_dates)
    bars = [{"date": day.isoformat(), "close": 100.0} for day in trading_dates]
    monkeypatch.setattr(get_mak_report, "_dated_stock_bars", lambda _code: bars)
    end_date = trading_dates[-1].isoformat()

    assert get_mak_report.count_history_deviations("600001", "IDX", {"IDX": bars}, end_date) == (
        0,
        None,
        10,
    )

    incomplete = [bar for bar in bars if bar["date"] != trading_dates[0].isoformat()]
    monkeypatch.setattr(get_mak_report, "_dated_stock_bars", lambda _code: incomplete)
    assert get_mak_report.count_history_deviations("600001", "IDX", {"IDX": bars}, end_date) == (
        None,
        None,
        9,
    )

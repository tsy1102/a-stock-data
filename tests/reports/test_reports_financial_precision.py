import asyncio
from types import SimpleNamespace

import get_mak_report
import get_val_report
from stock_common.sc_report_runner import (
    classify_price_range,
    format_52w_reference,
    format_quote_provenance,
    non_quarter_end_dates,
)


def _complete_without_event_loop(awaitable):
    iterator = awaitable.__await__()
    try:
        iterator.send(None)
    except StopIteration as completed:
        return completed.value
    raise AssertionError("expected the patched asynchronous path to complete without yielding")


def test_price_range_rejects_extrapolated_or_invalid_positions():
    assert classify_price_range(15, 10, 20) == ("within", 50.0, None)
    assert classify_price_range(9, 10, 20) == ("below", None, 10.0)
    assert classify_price_range(22, 10, 20) == ("above", None, 10.0)
    assert classify_price_range(15, 10, 10) == ("invalid", None, None)
    assert classify_price_range(float("nan"), 10, 20) == ("invalid", None, None)


def test_52_week_reference_labels_source_dates_and_outside_range():
    within = format_52w_reference(15, 10, 20, low_date="2026-10-01", high_date="2026-09-15")
    assert "现价在区间内位置 50.0%" in within
    assert "高点 2026-09-15 / 低点 2026-10-01" in within

    below = format_52w_reference(9, 10, 20)
    assert "区间外" in below
    assert "低于区间下沿 10.0%" in below
    assert "-10.0%" not in below


def test_quote_provenance_does_not_mislabel_unknown_batch_as_a_source():
    cdata = SimpleNamespace(
        quote_date="",
        field_as_of_dates={},
        field_sources={"price": "realtime:batch:source_unknown"},
        time_anchor="unknown",
    )
    rendered = format_quote_provenance(cdata)
    assert "行情有效日期未核实" in rendered
    assert "价格来源：未确认" in rendered
    assert "batch" not in rendered


def test_non_quarter_end_dates_preserve_source_dates_and_ignore_invalid_values():
    records = [
        {"date": "2026-06-30"},
        {"date": "2025-11-25"},
        {"date": "2025-11-25"},
        {"date": "not-a-date"},
        {"date": ""},
    ]
    assert non_quarter_end_dates(records) == ["2025-11-25"]


def test_val_52_week_candidates_exclude_out_of_range_and_invalid_pe():
    results = get_val_report.strategy_16_52w_position(
        [
            {"code": "inside", "price": 13, "low_52w": 10, "high_52w": 30, "pe_ttm": 20},
            {"code": "below", "price": 9, "low_52w": 10, "high_52w": 30, "pe_ttm": 20},
            {"code": "loss", "price": 12, "low_52w": 10, "high_52w": 30, "pe_ttm": -1},
        ]
    )
    assert [item["code"] for item in results] == ["inside"]
    assert "不等同于超卖" in results[0]["reason"]


def test_val_historical_price_selection_is_independent_of_kline_row_order():
    ascending = [
        ["2026-10-01", "10"],
        ["2026-10-03", "12"],
        ["2026-10-05", "15"],
    ]
    assert get_val_report._historical_close_on_or_before(ascending, 1, "2026-10-04") == 12.0
    assert (
        get_val_report._historical_close_on_or_before(list(reversed(ascending)), 1, "2026-10-04")
        == 12.0
    )
    assert get_val_report._historical_close_on_or_before(ascending, 1, "not-a-date") is None


def test_val_historical_pe_rejects_a_loss_making_latest_ttm(monkeypatch):
    periods = ("03-31", "06-30", "09-30", "12-31")
    profits = (10, 20, 30, 40, -10, -20, -30, -40)
    reports = [
        {"报告日": f"{year}-{period}", "净利润": str(profit)}
        for year, year_profits in ((2024, profits[:4]), (2025, profits[4:]))
        for period, profit in zip(periods, year_profits)
    ]
    monkeypatch.setattr(
        get_val_report,
        "get_financial_report_with_fallback",
        lambda _code, num_periods=12: reports,
    )

    def unexpected_kline(_code):
        raise AssertionError("loss-making TTM must stop before K-line selection")

    monkeypatch.setattr(
        get_val_report,
        "_fast_kline",
        unexpected_kline,
    )

    assert get_val_report.estimate_pe_range_position("600000", 10.0, 100) is None


def test_val_contrarian_candidates_are_selected_by_market_cap(monkeypatch):
    import stock_common.sc_datasource as datasource

    async def immediate_to_thread(function, /, *args, **kwargs):
        return function(*args, **kwargs)

    monkeypatch.setattr(
        get_val_report,
        "_load_strategy_config",
        lambda: {"fundamental": {"roe_good": 15.0, "pe_ceiling": 40.0}},
    )
    monkeypatch.setattr(datasource, "get_gross_margin_and_roe", lambda _code: {"roe": 20.0})
    monkeypatch.setattr(
        get_val_report,
        "_fast_kline",
        lambda _code: (["close"], [[100.0]] * 249 + [[50.0]]),
    )
    monkeypatch.setattr(get_val_report.asyncio, "to_thread", immediate_to_thread)
    results = _complete_without_event_loop(
        get_val_report.strategy_09_contrarian_value(
            [
                {"code": "small", "mcap_yi": 60, "pe_ttm": 20, "name": "small"},
                {"code": "large", "mcap_yi": 600, "pe_ttm": 20, "name": "large"},
            ],
            top_n=1,
        )
    )
    assert [item["code"] for item in results] == ["large"]


def test_market_breadth_handles_zero_decliners_without_fake_ratio():
    assert get_mak_report._market_breadth_display(0, 0) == ("N/A", "无有效涨跌方向样本")
    assert get_mak_report._market_breadth_display(10, 0) == ("∞", "上涨样本中无下跌")


def test_mak_limit_pool_consensus_distinguishes_majority_from_unanimity():
    source_text, status = get_mak_report._format_limit_pool_source_summary(
        {"cls": 54, "kpl": 54, "fupan": 52}, 54
    )
    assert "cls=54 / kpl=54 / fupan=52" == source_text
    assert "多数值 54" in status
    assert "2/3" in status
    assert "存在差异" in status
    assert "全数一致" not in status

    _, matching_status = get_mak_report._format_limit_pool_source_summary(
        {"cls": 54, "kpl": 54, "fupan": None}, 54
    )
    assert "全数一致（2/2）" in matching_status
    assert "1 个来源无有效值" in matching_status

    _, inconsistent_total_status = get_mak_report._format_limit_pool_source_summary(
        {"cls": 54, "kpl": 54, "fupan": 52}, 52
    )
    assert "多数值 54（2/3" in inconsistent_total_status
    assert "接口汇总值 52 与多数值不符" in inconsistent_total_status

    _, tied_status = get_mak_report._format_limit_pool_source_summary(
        {"a": 54, "b": 54, "c": 52, "d": 52}, 54
    )
    assert "来源计数并列（52、54 各 2 票）" in tied_status
    assert "无唯一多数结论" in tied_status


def test_mak_limit_pool_mismatch_note_keeps_pool_count_separate():
    note = get_mak_report._limit_pool_count_mismatch_note(54, 52)
    assert "多源统计值 54 只" in note
    assert "本节涨停池 52 只" in note
    assert "未逐只对齐名单" in note
    assert get_mak_report._limit_pool_count_mismatch_note(52, 52) == ""


def test_mak_flow_summary_reports_coverage_and_never_calls_auction_main_flow():
    partial = get_mak_report._main_flow_summary_lines({"600000": 1e9}, 10, 3)
    assert any("3/10" in line for line in partial)
    assert any("覆盖不完整" in line for line in partial)
    assert not any("完整扫描样本主力净额超过" in line for line in partial)

    fallback = get_mak_report._main_flow_summary_lines(
        {}, 10, 0, zhb_auction_amount_wan=10_000, zhb_data_date="2026-10-16"
    )
    auction = next(line for line in fallback if "ZHB竞价金额代理" in line)
    assert "不是主力净流入" in auction
    assert "不用于多空判断" in auction


def test_mak_zhb_auction_amount_never_enters_main_net_stock_field(monkeypatch):
    async def snapshot_with_auction_proxy():
        return {
            "600000": {
                "name": "浦发银行",
                "price": 10.0,
                "change_pct": 1.0,
                "main_net_buy_amount": 2500.0,
            }
        }

    monkeypatch.setattr(get_mak_report, "get_market_snapshot_async", snapshot_with_auction_proxy)
    monkeypatch.setattr(get_mak_report, "_MAIN_NET_MAP_GLOBAL", {})
    monkeypatch.setattr(get_mak_report, "_calc_mcap_yi", lambda _code, _price: 0.0)
    monkeypatch.setattr(get_mak_report, "_calc_3d_from_daily", lambda *_args, **_kwargs: 0.0)

    result = _complete_without_event_loop(get_mak_report._get_zhb_market_data(tencent_map={}))
    assert result[0]["main_net_amount"] == 0.0

    monkeypatch.setattr(get_mak_report, "_MAIN_NET_MAP_GLOBAL", {"600000": -1_250_000.0})
    result = _complete_without_event_loop(get_mak_report._get_zhb_market_data(tencent_map={}))
    assert result[0]["main_net_amount"] == -1_250_000.0

from concurrent.futures import ThreadPoolExecutor
from threading import get_ident
from types import SimpleNamespace

import core.data_provider as data_provider
import get_val_report


def test_snapshot_quality_notes_disclose_missing_coverage():
    notes = get_val_report._snapshot_quality_notes(8101, 0)

    assert notes[0] == "停牌状态未过滤（ZHB快照不含可靠成交量/停牌标记）"
    assert notes[1] == (
        "市值字段仅覆盖 0/8101 只；依赖市值的策略无法评估缺失样本，" "空结果不代表没有合格标的。"
    )
    assert get_val_report._snapshot_quality_notes(10, 10) == [notes[0]]


def test_failed_strategy_note_says_empty_result_is_incomplete():
    timeout_note = get_val_report._strategy_failure_note(timed_out=True, timeout_seconds=720)
    error_note = get_val_report._strategy_failure_note(timed_out=False, timeout_seconds=720)

    assert "扫描超时（720秒）" in timeout_note
    assert "扫描异常" in error_note
    assert "空结果不代表没有符合标的" in timeout_note
    assert "空结果不代表没有符合标的" in error_note


def test_closed_tencent_quotes_require_exact_date_and_matching_snapshot_change():
    snapshot = {
        "601233": {"date": "20261023", "change_pct": 2.95},
        "000001": {"date": "20261022", "change_pct": 2.95},
        "000002": {"date": "20261023", "change_pct": 2.95},
    }
    quotes = {
        "601233": {
            "price": 21.67,
            "last_close": 21.05,
            "change_pct": 2.95,
            "mcap_yi": 516.14,
        },
        "000001": {
            "price": 21.67,
            "last_close": 21.05,
            "change_pct": 2.95,
            "mcap_yi": 516.14,
        },
        "000002": {
            "price": 21.40,
            "last_close": 21.05,
            "change_pct": 2.95,
            "mcap_yi": 516.14,
        },
    }

    verified = get_val_report._verified_snapshot_tencent_quotes(
        snapshot, quotes, "20261023", "20261023"
    )

    assert set(verified) == {"601233"}
    assert (
        get_val_report._verified_snapshot_tencent_quotes(snapshot, quotes, "20261022", "20261023")
        == {}
    )


def test_val_local_day_close_must_match_exact_market_date():
    assert get_val_report._day_close_matches_market_date(
        {"date": "20261023"}, "20261023", "2026-10-23"
    )
    assert not get_val_report._day_close_matches_market_date(
        {"date": "20261016"}, "20261023", "2026-10-23"
    )
    assert not get_val_report._day_close_matches_market_date(
        {"date": "20261023"}, "20261022", "2026-10-23"
    )


def test_snapshot_quality_notes_report_closed_quote_validation_coverage():
    notes = get_val_report._snapshot_quality_notes(8101, 8000, 7860, "20261023")

    assert any("休市腾讯价格交叉核验通过 7860/8101 只" in note for note in notes)
    assert any("行情日按该 ZHB 日期交叉推定" in note for note in notes)


class _ImmediateAwaitable:
    def __init__(self, value):
        self.value = value

    def __await__(self):
        if False:
            yield None
        return self.value


def _complete_without_event_loop(coroutine):
    iterator = coroutine.__await__()
    try:
        next(iterator)
    except StopIteration as completed:
        return completed.value
    iterator.close()
    raise AssertionError("test coroutine unexpectedly suspended")


def test_liquidity_king_does_not_infer_money_flow_from_volume(monkeypatch):
    rows = [[100, 10.0] for _ in range(9)] + [[200, 10.5]]
    monkeypatch.setattr(
        get_val_report,
        "_fast_kline",
        lambda _code: (["volume", "close"], rows),
    )

    result = get_val_report.strategy_13_liquidity_king(
        [{"code": "600519", "name": "测试", "amount": 10000}]
    )

    assert len(result) == 1
    reason = result[0]["reason"]
    assert "成交量为5日均量的2.0倍" in reason
    assert "收盘价不低于前一交易日" in reason
    assert "仅凭量价无法判断资金主体或后续方向" in reason
    assert "主力资金" not in reason
    assert "流动性溢价" not in reason


def test_core_discount_offloads_pe_range_position_work(monkeypatch):
    caller_thread = get_ident()
    worker_threads = []
    monkeypatch.setattr(
        get_val_report,
        "_load_strategy_config",
        lambda: {
            "valuation": {"pe_high": 50.0, "pb_high": 8.0},
            "strategy": {
                "pe_percentile_warn": 15.0,
                "mcap_big_cap_min": 100.0,
                "top_n_cap": 10,
            },
        },
    )
    monkeypatch.setattr(
        data_provider,
        "get_canonical_stock_data",
        lambda _code: SimpleNamespace(pe_ttm=10.0, pb=1.0, mcap_yi=1000.0, price=10.0),
    )

    def fake_estimate(_code, _price, _total_shares):
        worker_threads.append(get_ident())
        return {
            "position_pct": 5.0,
            "pe_current": 10.0,
            "pe_min": 5.0,
            "pe_max": 20.0,
            "observations": 12,
            "financial_periods": 12,
        }

    monkeypatch.setattr(get_val_report, "estimate_pe_range_position", fake_estimate)

    def fake_to_thread(function, /, *args, **kwargs):
        with ThreadPoolExecutor(max_workers=1) as executor:
            result = executor.submit(function, *args, **kwargs).result()
        return _ImmediateAwaitable(result)

    monkeypatch.setattr(get_val_report.asyncio, "to_thread", fake_to_thread)
    result = _complete_without_event_loop(
        get_val_report.strategy_04_core_discount(
            [{"code": "600519", "name": "测试", "mcap_yi": 1000.0}]
        )
    )

    assert worker_threads and worker_threads[0] != caller_thread
    assert [item["code"] for item in result] == ["600519"]

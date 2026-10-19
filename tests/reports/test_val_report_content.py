from concurrent.futures import ThreadPoolExecutor
from threading import get_ident
from types import SimpleNamespace

import core.data_provider as data_provider
import get_val_report


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

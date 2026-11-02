from types import SimpleNamespace

from core import stock_cache, tdx_client
from core.eltdx_adapter import _EltdxAdapter


def test_eltdx_quote_adapter_preserves_all_five_book_prices_and_volumes():
    buy_levels = [SimpleNamespace(price=10.0 + i, volume=100 + i) for i in range(5)]
    sell_levels = [SimpleNamespace(price=11.0 + i, volume=200 + i) for i in range(5)]
    snapshot = SimpleNamespace(
        code="sh600519",
        last_price=10.5,
        pre_close_price=10.0,
        open_price=10.1,
        high_price=10.8,
        low_price=10.0,
        amount=123456.0,
        inside_dish=300,
        outer_disc=400,
        buy_levels=buy_levels,
        sell_levels=sell_levels,
    )
    quote_api = SimpleNamespace(get_snapshots=lambda symbols: [snapshot])
    client = SimpleNamespace(quotes=quote_api)

    row = _EltdxAdapter(client).quotes("sh600519").iloc[0]

    for level in range(1, 6):
        assert row[f"bid{level}"] == buy_levels[level - 1].price
        assert row[f"bid{level}_vol"] == buy_levels[level - 1].volume
        assert row[f"ask{level}"] == sell_levels[level - 1].price
        assert row[f"ask{level}_vol"] == sell_levels[level - 1].volume


def test_eltdx_xdxr_maps_capital_changes_to_mootdx_columns():
    calls = []
    records = [
        SimpleNamespace(
            date="2026-10-30",
            category=1,
            c1_value=0.5,
            c2_value=12.0,
            c3_value=2.0,
            c4_value=1.0,
        ),
        SimpleNamespace(date="2026-10-31", category=5, c1_value=0, c2_value=0),
    ]

    def capital_changes(code, *, include_raw):
        calls.append((code, include_raw))
        return SimpleNamespace(records=records)

    client = SimpleNamespace(corporate=SimpleNamespace(capital_changes=capital_changes))
    frame = _EltdxAdapter(client).xdxr("920306")

    assert calls == [("bj920306", False)]
    assert list(frame["category"]) == [1, 5]
    assert list(frame["date"]) == ["2026-10-30", "2026-10-31"]
    assert frame.loc[0, "fenhong"] == 0.5
    assert frame.loc[0, "peigu_price"] == 12.0
    assert frame.loc[0, "songzhuangu"] == 2.0
    assert frame.loc[0, "peigu"] == 1.0


def test_tdx_dividend_history_uses_eltdx_mapping_and_throttle(monkeypatch):
    record = SimpleNamespace(
        date="2026-10-30",
        category=1,
        c1_value=0.5,
        c2_value=12.0,
        c3_value=2.0,
        c4_value=1.0,
    )
    corporate = SimpleNamespace(
        capital_changes=lambda code, *, include_raw: SimpleNamespace(records=[record])
    )
    client = _EltdxAdapter(SimpleNamespace(corporate=corporate))
    throttle_calls = []
    monkeypatch.setattr(stock_cache, "_DISABLE_CACHE", True)
    monkeypatch.setattr(tdx_client, "_get_tdx_client", lambda: client)
    monkeypatch.setattr(tdx_client, "_tdx_throttle", lambda: throttle_calls.append(True))

    result = tdx_client.tdx_get_dividend_history("920306")

    assert throttle_calls == [True]
    assert result == [
        {
            "date": "2026-10-30",
            "bonus_rmb": 0.5,
            "bonus_ratio": 1.0,
            "transfer_ratio": 2.0,
        }
    ]

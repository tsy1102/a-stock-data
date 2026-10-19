from types import SimpleNamespace

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

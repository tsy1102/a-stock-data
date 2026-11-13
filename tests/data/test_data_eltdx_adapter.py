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


def test_eltdx_xdxr_normalizes_per_ten_values_to_mootdx_columns():
    calls = []
    records = [
        SimpleNamespace(
            date="2026-10-30",
            category=1,
            c1_value=5.0,
            c2_value=12.0,
            c3_value=20.0,
            c4_value=10.0,
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


def test_eltdx_finance_normalizes_share_and_reclassified_finance_slots():
    record = SimpleNamespace(
        liu_tong_gu_ben_raw_float=125008.15625,
        zong_gu_ben_raw_float=125008.15625,
        guo_jia_gu_raw_float=1215.0,
        fa_qi_ren_fa_ren_gu_raw_float=64626744.0,
        fa_ren_gu_raw_float=128453712.0,
        b_gu_raw_float=2.5,
        h_gu_raw_float=3.5,
        zong_zi_chan_raw_float=318304896.0,
        gu_dong_ren_shu_raw_float=567189.0,
        updated_date="2026-10-31",
        ipo_date="2001-08-27",
    )
    calls = []

    def finance_batch(symbol, *, include_raw):
        calls.append((symbol, include_raw))
        return SimpleNamespace(records=[record])

    client = SimpleNamespace(corporate=SimpleNamespace(finance_batch=finance_batch))
    row = _EltdxAdapter(client).finance("600519").iloc[0]

    assert calls == [("600519", False)]
    assert row["liutongguben"] == 1250081562.5
    assert row["zhongguben"] == 1250081562.5
    assert row["guojiagu"] == 12150000.0
    assert row["bgu"] == 25000.0
    assert row["hgu"] == 35000.0
    assert row["fajirenfarengu"] == 646267440000.0
    assert row["farengu"] == 1284537120000.0
    assert row["zongzichan"] == 3183048960000.0
    assert row["gudongrenshu"] == 567189.0


def test_tdx_dividend_history_uses_eltdx_mapping_and_throttle(monkeypatch):
    record = SimpleNamespace(
        date="2026-10-30",
        category=1,
        c1_value=5.0,
        c2_value=12.0,
        c3_value=20.0,
        c4_value=10.0,
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

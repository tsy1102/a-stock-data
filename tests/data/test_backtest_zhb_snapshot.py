from importlib import import_module
from types import SimpleNamespace

import pytest


def _load_backtest(monkeypatch):
    monkeypatch.syspath_prepend("scripts")
    return import_module("backtest_topn")


def test_load_zhb_snapshot_reports_parser_failure(tmp_path, monkeypatch):
    backtest = _load_backtest(monkeypatch)
    zip_path = tmp_path / "zhb_20261015.zip"
    zip_path.write_bytes(b"invalid zip payload")
    monkeypatch.setattr(backtest, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(backtest, "_parse_zhb_data", lambda _data, **_kwargs: None)

    with pytest.raises(ValueError, match="ZHB 包解析失败") as exc_info:
        backtest.load_zhb_snapshot("20261015")

    assert str(zip_path) in str(exc_info.value)


def test_load_zhb_snapshot_merges_stats_and_injects_codes(tmp_path, monkeypatch):
    backtest = _load_backtest(monkeypatch)
    (tmp_path / "zhb_20261015.zip").write_bytes(b"placeholder")
    monkeypatch.setattr(backtest, "CACHE_DIR", tmp_path)
    seen = {}

    def parse_zhb(_data, *, filename=None):
        seen["filename"] = filename
        return SimpleNamespace(
            stock_stats={"600519": {"price": 10}},
            stock_stats2={"600519": {"amount": 100}, "000001": {"amount": 50}},
        )

    monkeypatch.setattr(
        backtest,
        "_parse_zhb_data",
        parse_zhb,
    )

    result = backtest.load_zhb_snapshot("20261015")

    assert seen["filename"] == "zhb_20261015.zip"
    assert result == {
        "600519": {"price": 10, "amount": 100, "code": "600519"},
        "000001": {"amount": 50, "code": "000001"},
    }


def test_discover_days_uses_only_valid_retained_dates(tmp_path, monkeypatch):
    backtest = _load_backtest(monkeypatch)
    for name in (
        "zhb_20261014.zip",
        "zhb_20261015.zip",
        "zhb_20261106.zip",
        "zhb_20261131.zip",
        "zhb_99991231.zip",
        "zhb_not-a-date.zip",
    ):
        (tmp_path / name).touch()
    monkeypatch.setattr(backtest, "CACHE_DIR", tmp_path)

    assert backtest.discover_days() == ["20261015", "20261106"]


def test_discover_days_empty_folder_does_not_fall_back(tmp_path, monkeypatch):
    backtest = _load_backtest(monkeypatch)
    monkeypatch.setattr(backtest, "CACHE_DIR", tmp_path)

    assert backtest.discover_days() == []


@pytest.mark.parametrize("day", ["20261014", "99991231"])
def test_load_zhb_snapshot_rejects_dates_outside_retained_window(monkeypatch, day):
    backtest = _load_backtest(monkeypatch)
    monkeypatch.setattr(
        backtest, "_parse_zhb_data", lambda *_args, **_kwargs: pytest.fail("must not parse")
    )

    with pytest.raises(ValueError, match=day):
        backtest.load_zhb_snapshot(day)


def test_enrich_stock_labels_legacy_zhb_keys_as_auction_values(monkeypatch):
    backtest = _load_backtest(monkeypatch)
    monkeypatch.setattr(backtest, "calc_mcap_proxy", lambda _stock: 0.0)

    result = backtest.enrich_stock(
        {
            "amount": 100,
            "main_net_buy_amount": 4,
            "main_net_buy_amount_1d": 3,
            "main_net_buy_hands": 40,
            "main_net_buy_hands_1d": 30,
        }
    )

    assert result["open_auction_amount_wan"] == 4
    assert result["previous_open_auction_amount_wan"] == 3
    assert result["open_auction_volume_hand"] == 40
    assert result["previous_open_auction_volume_hand"] == 30


def test_auction_strategies_do_not_treat_legacy_aliases_as_main_flow(monkeypatch):
    backtest = _load_backtest(monkeypatch)
    stocks = [
        {
            "code": "600519",
            "amount": 100,
            "main_net_buy_amount": 99,
            "open_auction_amount_wan": 2,
            "previous_open_auction_amount_wan": 3,
        },
        {
            "code": "000001",
            "amount": 100,
            "open_auction_amount_wan": 4,
            "previous_open_auction_amount_wan": 3,
        },
    ]

    assert backtest.sim_strategy_20(stocks, 10) == ["000001"]
    assert backtest.sim_strategy_22(stocks, 10) == ["000001", "600519"]

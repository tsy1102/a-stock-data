from importlib import import_module
from types import SimpleNamespace

import pytest


def _load_backtest(monkeypatch):
    monkeypatch.syspath_prepend("scripts")
    return import_module("backtest_topn")


def test_load_zhb_snapshot_reports_parser_failure(tmp_path, monkeypatch):
    backtest = _load_backtest(monkeypatch)
    zip_path = tmp_path / "zhb_20260928.zip"
    zip_path.write_bytes(b"invalid zip payload")
    monkeypatch.setattr(backtest, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(backtest, "_parse_zhb_data", lambda _data: None)

    with pytest.raises(ValueError, match="ZHB 包解析失败") as exc_info:
        backtest.load_zhb_snapshot("20260928")

    assert str(zip_path) in str(exc_info.value)


def test_load_zhb_snapshot_merges_stats_and_injects_codes(tmp_path, monkeypatch):
    backtest = _load_backtest(monkeypatch)
    (tmp_path / "zhb_20260928.zip").write_bytes(b"placeholder")
    monkeypatch.setattr(backtest, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(
        backtest,
        "_parse_zhb_data",
        lambda _data: SimpleNamespace(
            stock_stats={"600519": {"price": 10}},
            stock_stats2={"600519": {"amount": 100}, "000001": {"amount": 50}},
        ),
    )

    result = backtest.load_zhb_snapshot("20260928")

    assert result == {
        "600519": {"price": 10, "amount": 100, "code": "600519"},
        "000001": {"amount": 50, "code": "000001"},
    }

"""Offline compatibility checks for the project's Levistock and AxData adapters."""

from __future__ import annotations

import glob
import inspect
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
from typing import Any, Callable, Iterator, Mapping, cast
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from stock_common import sc_network
from stock_common.sc_datasource import _misc, _pools, _quotes


def _uncached(function: Callable[..., Any]) -> Callable[..., Any]:
    return cast(Callable[..., Any], getattr(function, "__wrapped__"))


@pytest.fixture
def local_temp_dir() -> Iterator[Path]:
    parent = Path(__file__).resolve().parents[1] / ".pytest_cache"
    parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="adapter-compat-", dir=parent) as directory:
        yield Path(directory)


def _write_minimal_zhb_zip(path: Path, trade_date: str) -> Path:
    stats_row = [""] * 35
    stats_row[0] = "0"
    stats_row[1] = "000001"
    stats_row[4] = trade_date
    stats2_row = [""] * 21
    stats2_row[0] = "0"
    stats2_row[1] = "000001"
    stats2_row[2] = trade_date

    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("tdxstat.cfg", "|".join(stats_row))
        archive.writestr("tdxstat2.cfg", "|".join(stats2_row))
    return path


def test_installed_levistock_exposes_the_adapter_methods() -> None:
    import levistock
    from levistock.stock.stock_fupanla_kph import get_pmsl, get_zttt

    assert callable(levistock.market_emotion_cls)
    assert callable(levistock.get_zttt)
    assert callable(get_zttt)
    assert callable(get_pmsl)
    assert "date" in inspect.signature(levistock.get_zttt).parameters
    assert "date" in inspect.signature(get_zttt).parameters
    assert {"date", "st", "index"}.issubset(inspect.signature(get_pmsl).parameters)


def test_levistock_adapters_call_confirmed_methods_and_normalize_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, Any]] = []
    emotion = {"market_degree": "65", "up_down_dis": {"rise_num": 3200}}
    zttt = {"StockList": [["000001", "平安银行", 2, 93000, "BK0001", "银行", 0, 1, 3, 1000, 9000]]}
    pmsl = {"List": [{"TagName": "测试事件"}]}

    levistock = ModuleType("levistock")
    setattr(levistock, "__path__", [])

    def fake_market_emotion() -> dict[str, Any]:
        calls.append(("market_emotion_cls", None))
        return emotion

    def fake_get_zttt(**kwargs: Any) -> dict[str, Any]:
        calls.append(("get_zttt", kwargs.get("date")))
        return zttt

    setattr(levistock, "market_emotion_cls", fake_market_emotion)
    setattr(levistock, "get_zttt", fake_get_zttt)
    stock = ModuleType("levistock.stock")
    setattr(stock, "__path__", [])
    review = ModuleType("levistock.stock.stock_fupanla_kph")

    def fake_review_get_zttt() -> dict[str, Any]:
        calls.append(("review.get_zttt", None))
        return zttt

    def fake_get_pmsl() -> dict[str, Any]:
        calls.append(("get_pmsl", None))
        return pmsl

    setattr(review, "get_zttt", fake_review_get_zttt)
    setattr(review, "get_pmsl", fake_get_pmsl)
    monkeypatch.setitem(sys.modules, "levistock", levistock)
    monkeypatch.setitem(sys.modules, "levistock.stock", stock)
    monkeypatch.setitem(sys.modules, "levistock.stock.stock_fupanla_kph", review)
    monkeypatch.setattr(sc_network, "_em_wait_process_interval", lambda: None)

    assert _uncached(_misc.get_cls_market_emotion)() == emotion
    assert _uncached(_pools.get_kph_limit_ladder)("2026-10-07") == [
        {
            "code": "000001",
            "name": "平安银行",
            "limit_count": 2,
            "limit_time": 93000,
            "plate_code": "BK0001",
            "plate_name": "银行",
            "one_word": 0,
            "popular": 1,
            "plate_limit_up_count": 3,
            "amount": 1000,
            "plate_amount": 9000,
        }
    ]
    assert _uncached(_quotes.get_fupan_zttt)() == zttt
    assert _uncached(_quotes.get_fupan_pmsl)() == pmsl
    assert calls == [
        ("market_emotion_cls", None),
        ("get_zttt", "2026-10-07"),
        ("review.get_zttt", None),
        ("get_pmsl", None),
    ]


def test_shortline_adapter_uses_latest_local_zhb_zip_with_axdata(
    monkeypatch: pytest.MonkeyPatch,
    local_temp_dir: Path,
) -> None:
    import axdata_core
    from axdata_core.adapters.tdx.stats_resource import ensure_tdx_stats_resource

    older = _write_minimal_zhb_zip(local_temp_dir / "zhb_20261006.zip", "20261006")
    latest = _write_minimal_zhb_zip(local_temp_dir / "zhb_20261007.zip", "20261007")
    expected_pattern = str(
        Path(_quotes.__file__).resolve().parent.parent / "cache" / "zhb" / "zhb_*.zip"
    )
    original_glob = glob.glob
    seen: dict[str, Any] = {}

    def fake_glob(pattern: str, *args: Any, **kwargs: Any) -> list[str]:
        if os.path.normcase(pattern) == os.path.normcase(expected_pattern):
            seen["pattern"] = pattern
            return [str(latest), str(older)]
        return original_glob(pattern, *args, **kwargs)

    class OfflineStatsAdapter:
        source = "tdx"

        def supports(self, interface_name: str) -> bool:
            return interface_name == "stock_shortline_indicators_tdx"

        def request(self, interface_name: str, params: Mapping[str, Any]) -> list[dict[str, Any]]:
            stats, refreshed = ensure_tdx_stats_resource(object(), root=params["stats_root"])
            seen["interface"] = interface_name
            seen["params"] = dict(params)
            seen["stats_date"] = stats.stats_date
            seen["refreshed"] = refreshed
            return [{"symbol": params["code"], "stats_date": stats.stats_date}]

    request_interface = axdata_core.request_interface

    def offline_request(interface: str, **kwargs: Any) -> Any:
        seen["request_options"] = {
            "fields": kwargs["fields"],
            "persist": kwargs["persist"],
            "data_root": kwargs["data_root"],
        }
        return request_interface(interface, adapter=OfflineStatsAdapter(), **kwargs)

    monkeypatch.setattr(glob, "glob", fake_glob)
    monkeypatch.setattr(axdata_core, "request_interface", offline_request)

    result = _uncached(_quotes.get_shortline_indicators)("000001")

    assert result["symbol"] == "000001"
    assert result["stats_date"] == "20261007"
    assert seen["pattern"] == expected_pattern
    assert seen["interface"] == "stock_shortline_indicators_tdx"
    assert seen["request_options"] == {
        "fields": None,
        "persist": False,
        "data_root": None,
    }
    assert seen["params"] == {
        "code": "000001",
        "stats_root": str(latest),
    }
    assert seen["stats_date"] == "20261007"
    assert seen["refreshed"] is False

"""Offline compatibility checks for the project's Levistock and AxData adapters."""

from __future__ import annotations

import glob
import importlib
import inspect
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType, SimpleNamespace
from typing import Any, Callable, Iterator, Mapping, cast
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from stock_common import sc_network
from stock_common.sc_datasource import (
    _misc,
    _pools,
    _quotes,
    get_levistock_candidate_sample,
)


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
    monkeypatch.setattr(sc_network, "_cls_wait_process_interval", lambda: None)
    monkeypatch.setattr(sc_network, "_kph_wait_process_interval", lambda: None)

    assert _uncached(_misc.get_cls_market_emotion)() == emotion
    assert _uncached(_pools._get_kph_limit_ladder_for_date)("2026-10-09") == [
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
        ("get_zttt", "2026-10-09"),
        ("review.get_zttt", None),
        ("get_pmsl", None),
    ]


def test_public_kph_adapter_normalizes_and_validates_trade_date(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def capture_kph_date(trade_date: str) -> list[dict[str, str]]:
        calls.append(trade_date)
        return [{"code": "600000"}]

    monkeypatch.setattr(
        _pools,
        "_get_kph_limit_ladder_for_date",
        capture_kph_date,
    )

    assert _pools.get_kph_limit_ladder("20261009") == [{"code": "600000"}]
    assert _pools.get_kph_limit_ladder("20261010") == []
    assert calls == ["2026-10-09"]


def test_shortline_adapter_uses_latest_local_zhb_zip_with_axdata(
    monkeypatch: pytest.MonkeyPatch,
    local_temp_dir: Path,
) -> None:
    import axdata_core
    from axdata_core.adapters.tdx.stats_resource import ensure_tdx_stats_resource

    older = _write_minimal_zhb_zip(local_temp_dir / "zhb_20261006.zip", "20261006")
    latest = _write_minimal_zhb_zip(local_temp_dir / "zhb_20261007.zip", "20261007")
    expected_root = Path(__file__).resolve().parents[1] / "cache" / "zhb"
    assert Path(_quotes._axdata_zhb_cache_dir()).resolve() == expected_root.resolve()
    expected_pattern = str(expected_root / "zhb_*.zip")
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

    result = _uncached(_quotes.get_shortline_indicators_result)("000001")

    assert result["status"] == "ok"
    assert result["data"]["symbol"] == "000001"
    assert result["data"]["stats_date"] == "20261007"
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


def test_shortline_diagnostics_distinguish_missing_zhb_cache(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import axdata_core

    def unexpected_request(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("AxData request must not run without a local ZHB ZIP")

    monkeypatch.setattr(glob, "glob", lambda *args, **kwargs: [])
    monkeypatch.setattr(axdata_core, "request_interface", unexpected_request)

    result = _uncached(_quotes.get_shortline_indicators_result)("000001")

    assert result["status"] == "cache_missing"
    assert "cache/zhb" in result["error"]
    assert "interface was not called" in result["error"]


def test_shortline_routes_bse_symbols_with_explicit_market_suffix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import axdata_core

    seen: dict[str, Any] = {}

    def capture_request(interface: str, **kwargs: Any) -> Any:
        seen["interface"] = interface
        seen["params"] = dict(kwargs["params"])
        return SimpleNamespace(records=[{"code": kwargs["params"]["code"]}])

    monkeypatch.setattr(glob, "glob", lambda *args, **kwargs: ["zhb_20261007.zip"])
    monkeypatch.setattr(axdata_core, "request_interface", capture_request)

    result = _uncached(_quotes.get_shortline_indicators_result)("920118")

    assert result == {"status": "ok", "data": {"code": "920118.BJ"}}
    assert seen["interface"] == "stock_shortline_indicators_tdx"
    assert seen["params"]["code"] == "920118.BJ"
    assert seen["params"]["stats_root"] == "zhb_20261007.zip"


def test_shortline_diagnostics_distinguish_no_records(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import axdata_core

    monkeypatch.setattr(glob, "glob", lambda *args, **kwargs: ["zhb_20261007.zip"])
    monkeypatch.setattr(
        axdata_core,
        "request_interface",
        lambda *args, **kwargs: SimpleNamespace(records=[]),
    )

    result = _uncached(_quotes.get_shortline_indicators_result)("000001")

    assert result["status"] == "no_records"
    assert "stock_shortline_indicators_tdx" in result["error"]
    assert "(TDX)" in result["error"]


def test_shortline_diagnostics_distinguish_request_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import axdata_core

    def failed_request(*args: Any, **kwargs: Any) -> Any:
        raise TimeoutError("TDX connection timed out")

    monkeypatch.setattr(glob, "glob", lambda *args, **kwargs: ["zhb_20261007.zip"])
    monkeypatch.setattr(axdata_core, "request_interface", failed_request)

    result = _uncached(_quotes.get_shortline_indicators_result)("000001")

    assert result["status"] == "request_error"
    assert "TimeoutError" in result["error"]
    assert "TDX connection timed out" in result["error"]


def test_shortline_diagnostic_failures_are_not_cached(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import axdata_core
    from core import stock_cache

    request_calls = 0
    cache_writes: list[tuple[Any, ...]] = []

    def no_records(*args: Any, **kwargs: Any) -> Any:
        nonlocal request_calls
        request_calls += 1
        return SimpleNamespace(records=[])

    monkeypatch.setattr(glob, "glob", lambda *args, **kwargs: ["zhb_20261007.zip"])
    monkeypatch.setattr(axdata_core, "request_interface", no_records)
    monkeypatch.setattr(stock_cache, "_DISABLE_CACHE", False)
    monkeypatch.setattr(stock_cache, "get_cache", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        stock_cache,
        "set_cache",
        lambda *args, **kwargs: cache_writes.append(args),
    )

    first = _quotes.get_shortline_indicators_result("000005")
    second = _quotes.get_shortline_indicators_result("000005")

    assert first["status"] == second["status"] == "no_records"
    assert request_calls == 2
    assert cache_writes == []


def test_collect_axdata_keeps_stats_date_and_surfaces_diagnostics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import stock_common
    from scripts.capture_field_probe import collect_axdata

    diagnostics = {
        "000001": {
            "status": "ok",
            "data": {"symbol": "000001", "stats_date": "20261007"},
        },
        "000002": {
            "status": "cache_missing",
            "data": {},
            "error": "cache_missing: no project ZHB stats ZIP under cache/zhb",
        },
        "000003": {
            "status": "no_records",
            "data": {},
            "error": "no_records: AxData TDX returned no usable records",
        },
        "000004": {
            "status": "request_error",
            "data": {},
            "error": "request_error: AxData TDX failed: TimeoutError",
        },
    }
    monkeypatch.setattr(
        stock_common,
        "get_shortline_indicators_result",
        lambda code: diagnostics[code],
    )

    result = collect_axdata([{"code": code} for code in diagnostics])

    assert result["stocks"]["000001"]["data"]["stats_date"] == "20261007"
    assert result["stocks"]["000002"]["__error__"].startswith("cache_missing:")
    assert result["stocks"]["000003"]["__error__"].startswith("no_records:")
    assert result["stocks"]["000004"]["__error__"].startswith("request_error:")


def test_shortline_legacy_function_still_returns_field_dict(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = {"symbol": "000001", "stats_date": "20261007"}
    monkeypatch.setattr(
        _quotes,
        "get_shortline_indicators_result",
        lambda code: {"status": "ok", "data": record},
    )

    result = _uncached(_quotes.get_shortline_indicators)("000001")

    assert result == record


@pytest.mark.parametrize(
    "candidate_id,family,module_name,method_name,stock_code,expected_params",
    [
        (
            "cls_sector_industry",
            "cls",
            "levistock.sector.sector_cls",
            "sector_industry_cls",
            None,
            {},
        ),
        (
            "kph_market_emotion",
            "kph",
            "levistock.market.market_emotion_kph",
            "market_emotion_kph",
            None,
            {"date": "2026-10-09"},
        ),
        (
            "cls_sector_heat",
            "cls",
            "levistock.sector.sector_heat_cls",
            "get_sector_heat",
            None,
            {},
        ),
        (
            "kph_sector_ranking",
            "kph",
            "levistock.sector.sector_ranking_kph",
            "sector_ranking_kph",
            None,
            {"date": "2026-10-09", "zs_type": "7", "fetch_all": False},
        ),
        (
            "cls_sector_rotation",
            "cls",
            "levistock.sector.sector_rotation_cls",
            "get_sector_rotation",
            None,
            {"days": 4},
        ),
        (
            "cls_stock_kline",
            "cls",
            "levistock.stock.stock_kline_cls",
            "stock_kline_cls",
            "600000",
            {
                "stock_code": "600000",
                "kline_type": "daily",
                "limit": 5,
                "offset": 0,
            },
        ),
        (
            "cls_stock_timeline",
            "cls",
            "levistock.stock.stock_kline_cls",
            "stock_timeline_cls",
            "600000",
            {"stock_code": "600000"},
        ),
    ],
)
def test_levistock_candidate_adapter_routes_and_rate_limits_each_candidate(
    monkeypatch: pytest.MonkeyPatch,
    candidate_id: str,
    family: str,
    module_name: str,
    method_name: str,
    stock_code: str | None,
    expected_params: dict[str, Any],
) -> None:
    events: list[tuple[str, Any]] = []

    def candidate_method(**kwargs):
        events.append(("request", kwargs))
        return [{"sample": candidate_id}]

    def provider_is_blocked(checked_family: str) -> bool:
        events.append(("block_check", checked_family))
        return False

    monkeypatch.setattr(
        importlib,
        "import_module",
        lambda name: (
            SimpleNamespace(**{method_name: candidate_method})
            if name == module_name
            else pytest.fail(f"unexpected upstream module {name}")
        ),
    )
    monkeypatch.setattr(
        sc_network,
        "_levistock_provider_is_blocked",
        provider_is_blocked,
    )
    monkeypatch.setattr(
        sc_network,
        "_cls_wait_process_interval",
        lambda: events.append(("limit", "cls")),
    )
    monkeypatch.setattr(
        sc_network,
        "_kph_wait_process_interval",
        lambda: events.append(("limit", "kph")),
    )

    payload, params, adapter = get_levistock_candidate_sample(
        candidate_id,
        data_date="2026-10-09",
        stock_code=stock_code,
        expected_family=family,
    )

    assert payload == [{"sample": candidate_id}]
    assert params == expected_params
    assert adapter == f"{module_name}.{method_name}"
    assert events == [
        ("block_check", family),
        ("limit", family),
        ("request", expected_params),
    ]


def test_levistock_candidate_adapter_rejects_family_mismatch_before_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def record_block_check(_family: str) -> bool:
        calls.append("block_check")
        return False

    monkeypatch.setattr(
        sc_network,
        "_levistock_provider_is_blocked",
        record_block_check,
    )

    with pytest.raises(ValueError, match="family mismatch"):
        get_levistock_candidate_sample(
            "cls_sector_industry",
            data_date="2026-10-09",
            expected_family="kph",
        )

    assert calls == []

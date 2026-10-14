import sys
from datetime import date
from types import ModuleType

from scripts import capture_field_probe as capture_probe
import stock_common


def test_collect_axdata_skips_confirmed_redundant_route_without_calling_adapter(monkeypatch):
    called = False

    def fail_request(_code):
        nonlocal called
        called = True
        raise AssertionError("redundant shortline endpoint should not be requested")

    monkeypatch.setattr(stock_common, "get_shortline_indicators_result", fail_request, raising=False)
    result = capture_probe.collect_axdata(
        [{"code": "000001"}, {"code": "000002"}],
        identity_policy={
            "action": "skip",
            "reason": "endpoint_redundant_until_scheduled_recheck",
            "reference_source": "eltdx",
            "identity": {
                "status": "operationally_redundant",
                "interface_id": "stock_shortline_indicators_tdx",
                "evidence_dates": ["2026-10-08", "2026-10-09", "2026-10-12"],
            },
        },
    )

    assert not called
    assert set(result["stocks"]) == {"000001", "000002"}
    assert all("__skipped__" in item for item in result["stocks"].values())
    assert result["__source_meta__"]["identity_suppression"]["interface_id"] == (
        "stock_shortline_indicators_tdx"
    )


def test_collect_kph_history_does_not_request_a_confirmed_redundant_route(monkeypatch):
    called = False

    def fail_request(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("redundant KPH endpoint should not be requested")

    monkeypatch.setattr(capture_probe, "_kph_history_trade_date", lambda _value: date(2026, 10, 13))
    fake_adapter = ModuleType("stock_common.sc_datasource")
    fake_adapter.get_axdata_records = fail_request
    monkeypatch.setitem(sys.modules, "stock_common.sc_datasource", fake_adapter)
    result = capture_probe.collect_kph_history(
        "20261013",
        identity_policy={
            "action": "skip",
            "reason": "endpoint_redundant_until_scheduled_recheck",
            "reference_source": "kpl",
            "identity": {
                "status": "operationally_redundant",
                "interface_id": "kph_limit_up_history",
                "evidence_dates": ["2026-10-08", "2026-10-09", "2026-10-12"],
            },
        },
    )

    assert not called
    assert result["__skipped__"] == "endpoint_redundant_until_scheduled_recheck"
    assert result["trade_date"] == "2026-10-13"
    assert result["stocks"] == {}


def test_collect_axdata_stops_after_rate_limit_and_defers_remaining_codes(monkeypatch):
    calls = []

    def rate_limited(code):
        calls.append(code)
        return {"status": "request_error", "error": "HTTP 429 Too Many Requests"}

    monkeypatch.setattr(stock_common, "get_shortline_indicators_result", rate_limited, raising=False)
    result = capture_probe.collect_axdata(
        [{"code": "000001"}, {"code": "000002"}, {"code": "000003"}]
    )

    assert calls == ["000001"]
    assert "__error__" in result["stocks"]["000001"]
    assert result["stocks"]["000002"]["__skipped__"].startswith("deferred")
    assert result["stocks"]["000003"]["__skipped__"].startswith("deferred")
    assert result["__source_meta__"]["rate_limited"] is True

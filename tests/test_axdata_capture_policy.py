import sys
from datetime import date
from types import ModuleType

from scripts import capture_field_probe as capture_probe
import stock_common


def test_collect_axdata_skips_confirmed_redundant_route(monkeypatch):
    calls = []

    def capture(_code):
        calls.append(_code)
        return {"status": "ok", "data": {"f1": 1.0, "f2": 2.0}}

    monkeypatch.setattr(stock_common, "get_shortline_indicators_result", capture, raising=False)
    result = capture_probe.collect_axdata(
        [{"code": "000001"}, {"code": "000002"}],
        identity_policy={
            "action": "skip",
            "identity_validation_action": "suppress",
            "reason": "endpoint_redundant_until_scheduled_recheck",
            "reference_source": "eltdx",
            "identity": {
                "status": "operationally_redundant",
                "interface_id": "stock_shortline_indicators_tdx",
                "evidence_dates": ["2026-10-08", "2026-10-09", "2026-10-12"],
            },
        },
    )

    assert calls == []
    assert all(
        item["__skipped__"] == "endpoint_redundant_until_scheduled_recheck"
        for item in result["stocks"].values()
    )
    capture_block = result["__source_meta__"]["capture_block"]
    assert capture_block["interface_id"] == "stock_shortline_indicators_tdx"
    assert capture_block["capture_performed"] is False


def test_same_date_identity_skip_does_not_request_duplicate_data(monkeypatch):
    calls = []

    def capture(code):
        calls.append(code)
        return {"status": "ok", "data": {"f1": 10.0}}

    monkeypatch.setattr(stock_common, "get_shortline_indicators_result", capture, raising=False)
    result = capture_probe.collect_axdata(
        [{"code": "000001"}],
        identity_policy={
            "action": "skip",
            "identity_validation_action": "suppress",
            "reason": "data_date_already_confirmed",
            "reference_source": "eltdx",
            "identity": {
                "status": "operationally_redundant",
                "interface_id": "stock_shortline_indicators_tdx",
                "evidence_dates": ["2026-10-12"],
            },
        },
    )

    assert calls == []
    assert result["stocks"]["000001"]["__skipped__"] == "data_date_already_confirmed"
    assert result["__source_meta__"]["capture_block"]["capture_performed"] is False


def test_collect_kph_history_skips_confirmed_redundant_route(monkeypatch):
    calls = []

    def capture(*args, **kwargs):
        calls.append((args, kwargs))
        return [{"code": "000001", "trade_date": "2026-10-13", "sample_value": 9.0}]

    monkeypatch.setattr(capture_probe, "_kph_history_trade_date", lambda _value: date(2026, 10, 13))
    fake_adapter = ModuleType("stock_common.sc_datasource")
    fake_adapter.get_axdata_records = capture
    monkeypatch.setitem(sys.modules, "stock_common.sc_datasource", fake_adapter)
    result = capture_probe.collect_kph_history(
        "20261013",
        identity_policy={
            "action": "skip",
            "identity_validation_action": "suppress",
            "reason": "endpoint_redundant_until_scheduled_recheck",
            "reference_source": "kpl",
            "identity": {
                "status": "operationally_redundant",
                "interface_id": "kph_limit_up_history",
                "evidence_dates": ["2026-10-08", "2026-10-09", "2026-10-12"],
            },
        },
    )

    assert calls == []
    assert result["trade_date"] == "2026-10-13"
    assert result["stocks"] == {}
    assert result["__source_meta__"]["capture_block"]["interface_id"] == "kph_limit_up_history"
    assert result["__source_meta__"]["capture_block"]["capture_performed"] is False


def test_collect_axdata_stops_after_rate_limit_and_defers_remaining_codes(monkeypatch):
    calls = []

    def rate_limited(code):
        calls.append(code)
        return {"status": "request_error", "error": "HTTP 429 Too Many Requests"}

    monkeypatch.setattr(
        stock_common, "get_shortline_indicators_result", rate_limited, raising=False
    )
    result = capture_probe.collect_axdata(
        [{"code": "000001"}, {"code": "000002"}, {"code": "000003"}]
    )

    assert calls == ["000001"]
    assert "__error__" in result["stocks"]["000001"]
    assert result["stocks"]["000002"]["__skipped__"].startswith("deferred")
    assert result["stocks"]["000003"]["__skipped__"].startswith("deferred")
    assert result["__source_meta__"]["rate_limited"] is True

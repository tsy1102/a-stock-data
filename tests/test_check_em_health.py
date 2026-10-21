import json
from datetime import date
import sys

import pytest

from scripts import check_em_health
from stock_common import sc_network


def _spec(name="push2"):
    return next(
        item for item in check_em_health._build_probes(date(2026, 10, 20)) if item.name == name
    )


def test_probe_routes_one_attempt_through_shared_limiter_and_summarizes_shape(monkeypatch):
    calls = []

    class Response:
        status_code = 200
        content = b'{"rc":0,"data":{"f43":123,"f57":"600519"}}'
        headers = {"Content-Type": "application/json"}

        @staticmethod
        def json():
            return {"rc": 0, "data": {"f43": 123, "f57": "600519"}}

    def request(url, **kwargs):
        calls.append((url, kwargs))
        return Response()

    monkeypatch.setattr(sc_network, "_quick_request", request)

    result = check_em_health.probe(_spec())

    assert result["state"] == "ok"
    assert result["client_attempted"] is True
    assert result["client_attempts"] == 1
    assert result["response_bytes"] == len(Response.content)
    assert result["payload"] == {
        "root_type": "dict",
        "root_keys": ["data", "rc"],
        "data": {"type": "object", "keys": ["f43", "f57"]},
    }
    assert len(calls) == 1
    assert calls[0][1]["max_retries"] == 1
    assert "params" not in result


def test_probe_marks_persisted_ban_as_suppressed_without_network_attempt(monkeypatch):
    calls = []

    def request(_url, **kwargs):
        calls.append(kwargs)
        kwargs["error_out"].update(
            {"kind": "ip_banned", "domain": "push2.eastmoney.com", "attempts": 0}
        )
        return None

    monkeypatch.setattr(sc_network, "_quick_request", request)

    result = check_em_health.probe(_spec())

    assert result["state"] == "suppressed"
    assert result["stage"] == "local_guard"
    assert result["client_attempted"] is False
    assert result["client_attempts"] == 0
    assert result["stop_family"] is True
    assert len(calls) == 1


def test_run_probes_stops_failed_risk_family_but_checks_independent_family(monkeypatch):
    specs = [
        check_em_health.ProbeSpec(
            "push2", "push2", "push2.eastmoney.com", "/stock", (), "stock_get"
        ),
        check_em_health.ProbeSpec(
            "push2his", "push2", "push2his.eastmoney.com", "/kline", (), "kline"
        ),
        check_em_health.ProbeSpec(
            "push2delay", "delay", "push2delay.eastmoney.com", "/stock", (), "stock_get"
        ),
    ]
    calls = []

    def fake_probe(spec):
        calls.append(spec.name)
        if spec.name == "push2":
            return {
                "name": spec.name,
                "risk_family": spec.risk_family,
                "state": "transport_error",
                "client_attempted": True,
                "stop_family": True,
            }
        return {
            "name": spec.name,
            "risk_family": spec.risk_family,
            "state": "ok",
            "client_attempted": True,
            "stop_family": False,
        }

    monkeypatch.setattr(check_em_health, "probe", fake_probe)
    results = check_em_health.run_probes(specs, sleep=lambda _seconds: None)

    assert calls == ["push2", "push2delay"]
    assert results[1]["state"] == "not_probed"
    assert "risk family stopped" in results[1]["reason"]
    assert results[2]["state"] == "ok"


def test_probe_marks_json_contract_errors_without_calling_them_transport_failures(monkeypatch):
    class Response:
        status_code = 200
        content = b'{"rc":0,"data":null}'
        headers = {"Content-Type": "application/json"}

        @staticmethod
        def json():
            return {"rc": 0, "data": None}

    monkeypatch.setattr(sc_network, "_quick_request", lambda *_args, **_kwargs: Response())

    result = check_em_health.probe(_spec())

    assert result["state"] == "unexpected_payload"
    assert result["stage"] == "payload_contract"
    assert result["stop_family"] is False


@pytest.mark.parametrize(
    ("payload", "expected_state"),
    [
        ({"rc": 0, "data": {"pool": [{"c": "600519"}]}}, "ok"),
        ({"rc": 205, "data": None}, "empty_data"),
    ],
)
def test_push2ex_uses_pool_contract_and_accepts_no_data_code(monkeypatch, payload, expected_state):
    class Response:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        def __init__(self, response_payload):
            self.content = json.dumps(response_payload).encode("utf-8")
            self._payload = response_payload

        def json(self):
            return self._payload

    monkeypatch.setattr(sc_network, "_quick_request", lambda *_args, **_kwargs: Response(payload))

    result = check_em_health.probe(_spec("push2ex"))

    assert result["state"] == expected_state
    assert result["stop_family"] is False
    if expected_state == "empty_data":
        assert "rc=205" in result["reason"]


def test_main_writes_a_report_and_returns_inconclusive_for_suppressed_probe(monkeypatch, tmp_path):
    monkeypatch.setattr(check_em_health, "_latest_data_date", lambda: date(2026, 10, 20))
    monkeypatch.setattr(
        check_em_health,
        "run_probes",
        lambda probes: [
            {
                "name": probes[0].name,
                "host": "push2.eastmoney.com",
                "path": "/api/qt/stock/get",
                "state": "suppressed",
                "client_attempted": False,
                "client_attempts": 0,
            }
        ],
    )
    output = tmp_path / "health.json"

    exit_code = check_em_health.main(["--once", "--output", str(output)])

    report = json.loads(output.read_text(encoding="utf-8"))
    assert exit_code == 2
    assert report["status"] == "inconclusive"
    assert report["calendar_reference_date"] == "2026-10-20"
    assert report["probes"][0]["state"] == "suppressed"


def test_throttled_get_fails_closed_if_shared_request_adapter_cannot_import(monkeypatch):
    with monkeypatch.context() as scoped:
        scoped.setitem(sys.modules, "stock_common.sc_network", None)
        with pytest.raises(ModuleNotFoundError):
            check_em_health._throttled_get(_spec())

from datetime import date, datetime
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

import pytest

import stock_common
from stock_common import sc_network
from stock_common.sc_datasource import _st_list

_probe_path = Path(__file__).resolve().parents[1] / "scripts" / "capture_field_probe.py"
_probe_spec = spec_from_file_location("capture_field_probe_test_module", _probe_path)
assert _probe_spec is not None and _probe_spec.loader is not None
capture_probe = module_from_spec(_probe_spec)
_probe_spec.loader.exec_module(capture_probe)


def test_market_sources_queries_latest_dragon_tiger_snapshot(monkeypatch):
    calls = []

    monkeypatch.setattr(stock_common, "get_cls_market_emotion", lambda: {})
    monkeypatch.setattr(stock_common, "get_kph_limit_ladder", lambda: [])
    monkeypatch.setattr(stock_common, "get_stock_changes", lambda _code: [])
    monkeypatch.setattr(stock_common, "get_kpl_market_sentiment", lambda: {})
    monkeypatch.setattr(stock_common, "get_kpl_limit_up_detail", lambda: [])
    monkeypatch.setattr(stock_common, "get_kpl_broken_ratio", lambda: {})
    monkeypatch.setattr(stock_common, "get_kpl_up_down", lambda: {})
    monkeypatch.setattr(stock_common, "get_plate_rotation_matrix", lambda **_kwargs: [])
    monkeypatch.setattr(stock_common, "get_plate_rotation_top", lambda: [])

    def fake_datacenter(*args, **kwargs):
        calls.append((args, kwargs))
        return []

    monkeypatch.setattr(stock_common, "eastmoney_datacenter", fake_datacenter)
    monkeypatch.setattr(capture_probe, "_last_completed_trading_day", lambda: date(2026, 9, 24))

    result = capture_probe.collect_market_sources([])

    assert result["dragon_tiger_today"] == []
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args == ("", "RPT_DAILYBILLBOARD_DETAILSNEW")
    assert kwargs["filter_str"] == "(TRADE_DATE>='2026-09-24')(TRADE_DATE<='2026-09-24')"
    assert kwargs["page_size"] == 50
    assert kwargs["sort_columns"] == "TRADE_DATE"


def test_assess_result_counts_expected_skips_separately():
    ok, info = capture_probe.assess_result(
        {"stocks": {"bj920001": {"quote_snapshot": {"__skipped__": "BSE unsupported"}}}}
    )

    assert ok is True
    assert info["status"] == "ok"
    assert info["n_error"] == 0
    assert info["n_skipped"] == 1

    ok, info = capture_probe.assess_result(
        {
            "stocks": {
                "bj920001": {"quote_snapshot": {"__skipped__": "BSE unsupported"}},
                "sh600000": {"quote_snapshot": {"__error__": "timeout"}},
            }
        }
    )
    assert ok is False
    assert info["status"] == "partial"
    assert info["n_error"] == 1
    assert info["n_skipped"] == 1


def test_recent_trade_days_excludes_weekends_and_public_holidays():
    trade_days = capture_probe._recent_trade_days(6, date(2026, 10, 5))
    after_national_day = capture_probe._recent_trade_days(4, date(2026, 10, 12))
    calendar_days = capture_probe._recent_calendar_days(3, date(2026, 9, 28))

    assert "2026-10-05" not in trade_days
    assert after_national_day == ["2026-10-12", "2026-10-09", "2026-10-08", "2026-09-30"]
    assert "2026-10-10" not in after_national_day
    assert "2026-05-09" not in capture_probe._recent_trade_days(6, date(2026, 5, 11))
    assert all(date.fromisoformat(day).weekday() < 5 for day in trade_days)
    assert calendar_days == ["2026-09-28", "2026-09-27", "2026-09-26"]


def test_last_completed_trading_day_respects_close_and_exchange_holidays(monkeypatch):
    class FixedDateTime:
        value = datetime(2026, 9, 28, 14, 59)

        @classmethod
        def now(cls):
            return cls.value

    monkeypatch.setattr(capture_probe, "datetime", FixedDateTime)
    assert capture_probe._last_completed_trading_day() == date(2026, 9, 24)

    FixedDateTime.value = datetime(2026, 9, 28, 15, 0)
    assert capture_probe._last_completed_trading_day() == date(2026, 9, 28)

    FixedDateTime.value = datetime(2026, 10, 10, 16, 0)
    assert capture_probe._last_completed_trading_day() == date(2026, 10, 9)


def test_collect_etf_uses_recent_market_sessions(monkeypatch):
    attempted = []
    sessions = ["2026-09-28", "2026-09-24", "2026-09-23", "2026-09-22"]

    def fake_etf_shares(day, exchange):
        attempted.append((day, exchange))
        if exchange == "SH" and day == "2026-09-24":
            return [{"code": "510300", "shares": 123.0}]
        if exchange == "SZ":
            return [{"code": "159919", "shares": 456.0}]
        return []

    monkeypatch.setattr(stock_common.sc_datasource, "etf_shares", fake_etf_shares)
    monkeypatch.setattr(capture_probe, "_recent_trade_days", lambda _n: sessions)

    result = capture_probe.collect_etf([])

    assert attempted == [
        ("2026-09-28", "SH"),
        ("2026-09-24", "SH"),
        ("2026-09-28", "SZ"),
    ]
    assert result["etf_sh"][0]["code"] == "510300"
    assert result["etf_sz"][0]["code"] == "159919"


def test_capture_date_validation_uses_trading_days_for_market_sources():
    is_session = lambda day: day.weekday() < 5 and day != date(2026, 9, 25)

    with pytest.raises(ValueError, match="不是 A 股交易日"):
        capture_probe._validate_capture_data_date("20260927", ["push2"], is_session)
    with pytest.raises(ValueError, match="不是 A 股交易日"):
        capture_probe._validate_capture_data_date("20260925", ["tdx"], is_session)


def test_capture_date_validation_allows_natural_days_for_event_only_sources():
    capture_day, domain = capture_probe._validate_capture_data_date(
        "20260927", ["reports", "news_wscn_cctv"], lambda _day: False
    )

    assert capture_day == date(2026, 9, 27)
    assert domain == "calendar"


def test_capture_date_validation_rejects_malformed_dates():
    with pytest.raises(ValueError, match="YYYYMMDD"):
        capture_probe._validate_capture_data_date("2026-09-27", ["reports"])


def test_default_capture_date_uses_last_completed_session(monkeypatch):
    expected = date(2026, 9, 29)
    monkeypatch.setattr(capture_probe, "_last_completed_trading_day", lambda: expected)

    assert capture_probe._last_trading_day_str() == "20260929"


def test_push2_failures_include_domain_and_use_single_attempt(monkeypatch):
    calls = []

    def fake_request(url, **kwargs):
        calls.append((url, kwargs))
        kwargs["error_out"].update(
            {
                "kind": "ip_banned" if "push2.eastmoney.com" in url else "connection_error",
                "domain": url.split("/")[2],
                "attempts": 0 if "push2.eastmoney.com" in url else 1,
            }
        )
        return None

    monkeypatch.setattr(stock_common, "_quick_request", fake_request)
    monkeypatch.setattr(sc_network, "_em_is_banned", lambda _domain: False)

    result = capture_probe.collect_push2([{"code": "600000"}])

    error = result["stocks"]["600000"]["__error__"]
    assert len(calls) == 2
    assert all(kwargs["max_retries"] == 1 for _, kwargs in calls)
    assert "push2delay.eastmoney.com" in error
    assert "push2.eastmoney.com" in error
    assert "ip_banned" in error


def test_clist_failure_reports_both_domains(monkeypatch):
    def fake_request(url, **kwargs):
        kwargs["error_out"].update(
            {"kind": "http_403", "domain": url.split("/")[2], "status_code": 403}
        )
        return None

    monkeypatch.setattr(stock_common, "_quick_request", fake_request)

    result = capture_probe.collect_clist([])

    for label in ("industry", "concept", "area"):
        error = result["by_type"][label]["__error__"]
        assert "push2delay.eastmoney.com" in error
        assert "push2.eastmoney.com" in error
        assert "status=403" in error


def test_kline_and_fund_flow_failures_keep_transport_details(monkeypatch):
    def fake_request(url, **kwargs):
        kwargs["error_out"].update(
            {"kind": "ip_banned", "domain": url.split("/")[2], "attempts": 0}
        )
        return None

    monkeypatch.setattr(stock_common, "_quick_request", fake_request)
    pool = [{"code": "600000"}]

    kline = capture_probe.collect_em_kline_f61(pool)
    flow = capture_probe.collect_em_fund_flow(pool)

    assert "ip_banned" in kline["stocks"]["600000"]["__error__"]
    assert "push2his.eastmoney.com" in kline["stocks"]["600000"]["__error__"]
    assert "ip_banned" in flow["stocks"]["600000"]["__error__"]
    assert "push2delay.eastmoney.com" in flow["stocks"]["600000"]["__error__"]


def test_network_failure_diagnostics_redact_query_parameters(monkeypatch):
    class FailingSession:
        def get(self, *_args, **_kwargs):
            raise sc_network.requests.exceptions.ConnectionError(
                "RemoteDisconnected at /quote?ut=secret-token"
            )

    monkeypatch.setattr(sc_network, "_HTTP_SESSION", FailingSession())
    monkeypatch.setattr(sc_network, "_resolve_host_with_timeout", lambda _domain: None)
    monkeypatch.setattr(sc_network, "_em_wait_process_interval", lambda: None)
    detail = {}

    response = sc_network._do_request(
        "https://push2delay.eastmoney.com/quote?ut=secret-token",
        params=None,
        headers=None,
        timeout=1,
        max_retries=1,
        data=None,
        method="GET",
        verify=True,
        error_out=detail,
    )

    assert response is None
    assert detail["kind"] == "connection_error"
    assert detail["error_type"] == "ConnectionError"
    assert "secret-token" not in str(detail)


def test_network_diagnostics_are_opt_in_for_http_error_responses(monkeypatch):
    response = SimpleNamespace(status_code=503, headers={})

    class FailingSession:
        def get(self, *_args, **_kwargs):
            return response

    monkeypatch.setattr(sc_network, "_HTTP_SESSION", FailingSession())
    monkeypatch.setattr(sc_network, "_resolve_host_with_timeout", lambda _domain: None)
    monkeypatch.setattr(sc_network, "_em_wait_process_interval", lambda: None)
    detail = {}

    diagnosed = sc_network._do_request(
        "https://push2delay.eastmoney.com/quote",
        params=None,
        headers=None,
        timeout=1,
        max_retries=1,
        data=None,
        method="GET",
        verify=True,
        error_out=detail,
    )
    legacy = sc_network._do_request(
        "https://push2delay.eastmoney.com/quote",
        params=None,
        headers=None,
        timeout=1,
        max_retries=1,
        data=None,
        method="GET",
        verify=True,
    )

    assert diagnosed is None
    assert detail["kind"] == "http_error"
    assert detail["status_code"] == 503
    assert legacy is response


def test_quick_request_reports_preexisting_ban_without_request(monkeypatch):
    monkeypatch.setattr(sc_network, "_em_is_banned", lambda _domain: True)
    detail = {"stale": "previous request"}

    response = sc_network._quick_request(
        "https://push2delay.eastmoney.com/api/qt/stock/get?ut=secret-token",
        error_out=detail,
    )

    assert response is None
    assert detail["kind"] == "ip_banned"
    assert detail["domain"] == "push2delay.eastmoney.com"
    assert "stale" not in detail
    assert "secret-token" not in str(detail)


def test_em_get_ban_short_circuit_does_not_use_optional_request_details(monkeypatch):
    monkeypatch.setattr(sc_network, "_em_is_banned", lambda _domain: True)

    assert sc_network.em_get("https://push2.eastmoney.com/api/quote") is None


def test_baostock_fallback_uses_public_login_signature(monkeypatch):
    class FakeRows:
        error_code = "0"

        def __init__(self):
            self._read = False

        def next(self):
            if self._read:
                return False
            self._read = True
            return True

        def get_row_data(self):
            return ["sh.600001", "ST Sample"]

    fake_baostock = ModuleType("baostock")
    fake_baostock.login = lambda: SimpleNamespace(error_code="0", error_msg="success")
    fake_baostock.query_stock_basic = lambda: FakeRows()
    fake_baostock.logout = lambda: None
    monkeypatch.setitem(sys.modules, "baostock", fake_baostock)

    result = _st_list._st_list_baostock()

    assert result == [
        {
            "code": "600001",
            "market": "sh",
            "name": "ST Sample",
            "st_type": "ST",
            "price": None,
            "pct_change": None,
        }
    ]

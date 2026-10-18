from __future__ import annotations

import pytest

import get_val_report as val
from core import tdx_client


def test_fast_kline_does_not_repeat_default_tdx_request_for_short_data(monkeypatch):
    calls = []
    result = (["time"], [["2026-10-16"]] * 5)

    def fake_tdx(code, count):
        calls.append((code, count))
        return result

    def unexpected_legacy_fallback(*args, **kwargs):
        pytest.fail("legacy Baidu-named wrapper must not repeat the TDX request")

    monkeypatch.setattr(tdx_client, "tdx_get_security_bars", fake_tdx)
    monkeypatch.setattr(val, "common_baidu_kline_full", unexpected_legacy_fallback)

    assert val._fast_kline("600519") == result
    assert calls == [("600519", 800)]


def test_fast_kline_uses_one_larger_tdx_sample_when_requested_sample_is_short(monkeypatch):
    calls = []
    short_result = (["time"], [["2026-10-16"]] * 5)
    extended_result = (["time"], [["2026-10-16"]] * 70)

    def fake_tdx(code, count):
        calls.append((code, count))
        return {100: short_result, 800: extended_result}[count]

    monkeypatch.setattr(tdx_client, "tdx_get_security_bars", fake_tdx)

    assert val._fast_kline("600519", count=100) == extended_result
    assert calls == [("600519", 100), ("600519", 800)]


def test_fast_kline_returns_empty_after_tdx_failure_without_fake_fallback(monkeypatch):
    calls = []

    def fake_tdx(code, count):
        calls.append((code, count))
        raise TimeoutError("TDX timed out")

    def unexpected_legacy_fallback(*args, **kwargs):
        pytest.fail("legacy Baidu-named wrapper must not retry the TDX request")

    monkeypatch.setattr(tdx_client, "tdx_get_security_bars", fake_tdx)
    monkeypatch.setattr(val, "common_baidu_kline_full", unexpected_legacy_fallback)
    monkeypatch.setattr(val, "_debug_log", lambda _message: None)

    assert val._fast_kline("600519") == ([], [])
    assert calls == [("600519", 800)]

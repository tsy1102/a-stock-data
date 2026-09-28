from datetime import date
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import stock_common

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
    monkeypatch.setattr(capture_probe, "_last_completed_trading_day", lambda: date(2026, 9, 25))

    result = capture_probe.collect_market_sources([])

    assert result["dragon_tiger_today"] == []
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args == ("", "RPT_DAILYBILLBOARD_DETAILSNEW")
    assert kwargs["filter_str"] == "(TRADE_DATE>='2026-09-25')(TRADE_DATE<='2026-09-25')"
    assert kwargs["page_size"] == 50
    assert kwargs["sort_columns"] == "TRADE_DATE"

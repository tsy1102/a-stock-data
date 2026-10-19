from datetime import date, datetime
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from uuid import uuid4

import pytest

import stock_common
from stock_common import sc_fuyao
from stock_common import sc_network
from stock_common.sc_datasource import _st_list

_probe_path = Path(__file__).resolve().parents[1] / "scripts" / "capture_field_probe.py"
_probe_spec = spec_from_file_location("capture_field_probe_test_module", _probe_path)
assert _probe_spec is not None and _probe_spec.loader is not None
capture_probe = module_from_spec(_probe_spec)
_probe_spec.loader.exec_module(capture_probe)


def _fake_kpl_detail(pid_type=1, capture_raw=False):
    if pid_type != 1:
        return []
    return [{"code": "600000", "zt_time": 1790645140, "seal_amount": 1.0}]


def test_startup_scope_label_shows_selected_sources_and_context_mode():
    assert (
        capture_probe._startup_scope_label(["ftshare", "kph"], True)
        == "源范围: --only ftshare,kph | 市场上下文: 启用"
    )
    assert capture_probe._startup_scope_label([], False) == "源范围: 默认源集合 | 市场上下文: 跳过"


def test_market_sources_queries_latest_dragon_tiger_snapshot(monkeypatch):
    calls = []

    monkeypatch.setattr(stock_common, "get_cls_market_emotion", lambda: {})
    monkeypatch.setattr(stock_common, "get_kph_limit_ladder", lambda *_args: [])
    monkeypatch.setattr(stock_common, "get_stock_changes", lambda _code: [])
    monkeypatch.setattr(stock_common, "get_kpl_market_sentiment", lambda **_kwargs: {"strong": 1})
    monkeypatch.setattr(stock_common, "get_kpl_limit_up_detail", _fake_kpl_detail)
    monkeypatch.setattr(stock_common, "get_kpl_broken_ratio", lambda **_kwargs: {"zt": 1})
    monkeypatch.setattr(stock_common, "get_kpl_up_down", lambda **_kwargs: {"rise_num": 1})
    monkeypatch.setattr(
        stock_common, "get_kpl_plate_strength", lambda **_kwargs: [{"code": "BK0001"}]
    )
    monkeypatch.setattr(stock_common, "get_plate_rotation_matrix", lambda **_kwargs: [])
    monkeypatch.setattr(stock_common, "get_plate_rotation_top", lambda: [])

    def fake_datacenter(*args, **kwargs):
        calls.append((args, kwargs))
        return []

    monkeypatch.setattr(stock_common, "eastmoney_datacenter", fake_datacenter)
    monkeypatch.setattr(capture_probe, "_last_completed_trading_day", lambda: date(2026, 9, 24))

    result = capture_probe.collect_market_sources([], include_context=True)

    assert result["dragon_tiger_today"] == []
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args == ("", "RPT_DAILYBILLBOARD_DETAILSNEW")
    assert kwargs["filter_str"] == "(TRADE_DATE>='2026-09-24')(TRADE_DATE<='2026-09-24')"
    assert kwargs["page_size"] == 50
    assert kwargs["sort_columns"] == "TRADE_DATE"


def test_market_sources_skips_dragon_tiger_by_default(monkeypatch):
    calls = []
    monkeypatch.setattr(stock_common, "get_cls_market_emotion", lambda: {})
    kph_dates = []
    monkeypatch.setattr(
        stock_common,
        "get_kph_limit_ladder",
        lambda trade_date="": kph_dates.append(trade_date) or [],
    )
    monkeypatch.setattr(stock_common, "get_stock_changes", lambda _code: [])
    monkeypatch.setattr(stock_common, "get_kpl_market_sentiment", lambda **_kwargs: {"strong": 1})
    monkeypatch.setattr(stock_common, "get_kpl_limit_up_detail", _fake_kpl_detail)
    monkeypatch.setattr(stock_common, "get_kpl_broken_ratio", lambda **_kwargs: {"zt": 1})
    monkeypatch.setattr(stock_common, "get_kpl_up_down", lambda **_kwargs: {"rise_num": 1})
    monkeypatch.setattr(
        stock_common, "get_kpl_plate_strength", lambda **_kwargs: [{"code": "BK0001"}]
    )
    monkeypatch.setattr(stock_common, "get_plate_rotation_matrix", lambda **_kwargs: [])
    monkeypatch.setattr(stock_common, "get_plate_rotation_top", lambda: [])
    monkeypatch.setattr(
        stock_common,
        "eastmoney_datacenter",
        lambda *_args, **_kwargs: calls.append("requested") or [],
    )

    result = capture_probe.collect_market_sources([], trade_date="20261009")

    assert "dragon_tiger_today" not in result
    assert "trade_date" not in result
    assert calls == []
    assert kph_dates == ["2026-10-09"]
    assert result["__source_meta__"]["kph_limit_ladder"]["requested_trade_date"] == "2026-10-09"


def test_context_paths_are_optional_and_preserved_on_default_refresh(tmp_path):
    assert ("dragon_tiger_today",) not in capture_probe._source_required_paths("market_sources")
    assert ("dragon_tiger_today",) in capture_probe._source_required_paths(
        "market_sources", include_context=True
    )

    market_path = tmp_path / "raw_market_sources.json"
    market_path.write_text(
        json.dumps({"dragon_tiger_today": [{"amount": 1}], "kpl_sentiment": {}}),
        encoding="utf-8",
    )
    market_data = {"kpl_sentiment": {"sentiment": 0.5}}
    preserved, warnings = capture_probe._preserve_context_paths(
        "market_sources", market_data, str(tmp_path)
    )
    assert preserved == ["dragon_tiger_today"]
    assert warnings == []
    assert market_data["dragon_tiger_today"] == [{"amount": 1}]

    fuyao_path = tmp_path / "raw_fuyao.json"
    fuyao_path.write_text(
        json.dumps(
            {
                "market": {
                    "dragon_tiger": [{"amount": 2}],
                    "hot_list_hour": [{"heat": 3}],
                }
            }
        ),
        encoding="utf-8",
    )
    fuyao_data = {"stocks": {}, "market": {"short_term_benchmark": []}}
    preserved, warnings = capture_probe._preserve_context_paths("fuyao", fuyao_data, str(tmp_path))
    assert preserved == ["market.dragon_tiger", "market.hot_list_hour"]
    assert warnings == []
    assert fuyao_data["market"]["dragon_tiger"] == [{"amount": 2}]
    assert fuyao_data["market"]["hot_list_hour"] == [{"heat": 3}]


def test_context_only_sources_do_not_block_default_snapshot_check(tmp_path):
    collectors = {"exchange": lambda _pool: {}}

    assert capture_probe._has_complete_snapshot(collectors, {}, str(tmp_path), []) is True
    assert (
        capture_probe._has_complete_snapshot(
            collectors, {}, str(tmp_path), [], include_context=True
        )
        is False
    )


def test_market_source_failures_do_not_skip_sibling_calls(monkeypatch):
    def fail_cls():
        raise RuntimeError("CLS down")

    monkeypatch.setattr(stock_common, "get_cls_market_emotion", fail_cls)
    monkeypatch.setattr(stock_common, "get_kph_limit_ladder", lambda *_args: ["ladder"])
    monkeypatch.setattr(stock_common, "get_stock_changes", lambda _code: ["change"])
    monkeypatch.setattr(stock_common, "get_kpl_market_sentiment", lambda **_kwargs: {"strong": 1})
    monkeypatch.setattr(stock_common, "get_kpl_limit_up_detail", _fake_kpl_detail)
    monkeypatch.setattr(stock_common, "get_kpl_broken_ratio", lambda **_kwargs: {"zt": 1})
    monkeypatch.setattr(stock_common, "get_kpl_up_down", lambda **_kwargs: {"rise_num": 1})
    monkeypatch.setattr(
        stock_common, "get_kpl_plate_strength", lambda **_kwargs: [{"code": "BK0001"}]
    )
    monkeypatch.setattr(stock_common, "get_plate_rotation_matrix", lambda **_kwargs: [])
    monkeypatch.setattr(stock_common, "get_plate_rotation_top", lambda: [])
    monkeypatch.setattr(stock_common, "eastmoney_datacenter", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(capture_probe, "_last_completed_trading_day", lambda: date(2026, 9, 24))

    result = capture_probe.collect_market_sources([])

    assert result["cls_market_emotion"]["__error__"] == "CLS down"
    assert result["kph_limit_ladder"] == ["ladder"]
    assert result["stock_changes_8201"] == ["change"]
    ok, info = capture_probe.assess_result(
        result, required_paths=capture_probe.SOURCE_REQUIRED_PATHS["market_sources"]
    )
    assert ok is False
    assert info["status"] == "partial"
    assert info["n_error"] == 1


def test_market_source_none_response_is_an_error(monkeypatch):
    monkeypatch.setattr(stock_common, "get_cls_market_emotion", lambda: None)
    monkeypatch.setattr(stock_common, "get_kph_limit_ladder", lambda *_args: [])
    monkeypatch.setattr(stock_common, "get_stock_changes", lambda _code: [])
    monkeypatch.setattr(stock_common, "get_kpl_market_sentiment", lambda **_kwargs: {"strong": 1})
    monkeypatch.setattr(stock_common, "get_kpl_limit_up_detail", _fake_kpl_detail)
    monkeypatch.setattr(stock_common, "get_kpl_broken_ratio", lambda **_kwargs: {"zt": 1})
    monkeypatch.setattr(stock_common, "get_kpl_up_down", lambda **_kwargs: {"rise_num": 1})
    monkeypatch.setattr(
        stock_common, "get_kpl_plate_strength", lambda **_kwargs: [{"code": "BK0001"}]
    )
    monkeypatch.setattr(stock_common, "get_plate_rotation_matrix", lambda **_kwargs: [])
    monkeypatch.setattr(stock_common, "get_plate_rotation_top", lambda: [])
    monkeypatch.setattr(stock_common, "eastmoney_datacenter", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(capture_probe, "_last_completed_trading_day", lambda: date(2026, 9, 24))

    result = capture_probe.collect_market_sources([])

    assert result["cls_market_emotion"] == {"__error__": "collector returned None"}
    ok, info = capture_probe.assess_result(
        result, required_paths=capture_probe.SOURCE_REQUIRED_PATHS["market_sources"]
    )
    assert ok is False
    assert info["n_error"] == 2


def test_market_source_missing_export_does_not_skip_sibling_calls(monkeypatch):
    monkeypatch.delattr(stock_common, "get_cls_market_emotion")
    monkeypatch.setattr(stock_common, "get_kph_limit_ladder", lambda *_args: ["ladder"])
    monkeypatch.setattr(stock_common, "get_stock_changes", lambda _code: [])
    monkeypatch.setattr(stock_common, "get_kpl_market_sentiment", lambda **_kwargs: {"strong": 1})
    monkeypatch.setattr(stock_common, "get_kpl_limit_up_detail", _fake_kpl_detail)
    monkeypatch.setattr(stock_common, "get_kpl_broken_ratio", lambda **_kwargs: {"zt": 1})
    monkeypatch.setattr(stock_common, "get_kpl_up_down", lambda **_kwargs: {"rise_num": 1})
    monkeypatch.setattr(
        stock_common, "get_kpl_plate_strength", lambda **_kwargs: [{"code": "BK0001"}]
    )
    monkeypatch.setattr(stock_common, "get_plate_rotation_matrix", lambda **_kwargs: [])
    monkeypatch.setattr(stock_common, "get_plate_rotation_top", lambda: [])
    monkeypatch.setattr(stock_common, "eastmoney_datacenter", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(capture_probe, "_last_completed_trading_day", lambda: date(2026, 9, 24))

    result = capture_probe.collect_market_sources([])

    assert "get_cls_market_emotion" in result["cls_market_emotion"]["__error__"]
    assert result["kph_limit_ladder"] == ["ladder"]


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


def test_assess_result_distinguishes_all_stock_failures_from_partial_failure():
    all_failed = {
        "stocks": {
            "600000": {"quote_snapshot": {"__error__": "blocked"}},
            "000001": {"shortline": {"error": "unavailable"}},
        }
    }
    ok, failed_info = capture_probe.assess_result(all_failed, expected_symbols=["600000", "000001"])

    assert ok is False
    assert failed_info["status"] == "failed"
    assert failed_info["n_dead"] == 2

    partly_failed = {
        "stocks": {
            "600000": {"quote_snapshot": {"__error__": "blocked"}},
            "000001": {"quote_snapshot": {"last_price": 10}},
        }
    }
    ok, partial_info = capture_probe.assess_result(
        partly_failed, expected_symbols=["600000", "000001"]
    )

    assert ok is False
    assert partial_info["status"] == "partial"
    assert partial_info["n_dead"] == 1


def test_assess_result_detects_legacy_markers_deferred_and_missing_contracts():
    ok, info = capture_probe.assess_result(
        {
            "stocks": {"600000": {"quote_snapshot": {"last_price": 1.0}}},
            "market": {"shortline": {"__skipped__": "deferred: not ready before 09:25"}},
        },
        expected_symbols=["600000", "000001"],
        required_paths=[("records",)],
    )

    assert ok is False
    assert info["status"] == "partial"
    assert info["n_deferred"] == 1
    assert info["n_missing_stocks"] == 1
    assert info["n_missing_contracts"] == 1

    ok, legacy = capture_probe.assess_result(
        {"levistock_error": "blocked", "__error_szse__": "timeout", "error": "disabled"}
    )
    assert ok is False
    assert legacy["status"] == "failed"
    assert legacy["n_error"] == 3


def test_assess_result_treats_null_required_path_as_missing():
    ok, info = capture_probe.assess_result({"records": None}, required_paths=[("records",)])

    assert ok is False
    assert info["status"] == "partial"
    assert info["n_missing_contracts"] == 1


def test_capture_market_phase_tracks_actual_session(monkeypatch):
    checker = lambda _day: True

    assert capture_probe._capture_market_phase(datetime(2026, 9, 30, 8, 50), checker) == "pre_open"
    assert (
        capture_probe._capture_market_phase(datetime(2026, 9, 30, 9, 20), checker) == "call_auction"
    )
    assert (
        capture_probe._capture_market_phase(datetime(2026, 9, 30, 12, 0), checker) == "lunch_break"
    )
    assert capture_probe._capture_market_phase(datetime(2026, 9, 30, 15, 1), checker) == "closed"
    assert (
        capture_probe._capture_market_phase(datetime(2026, 9, 27, 10, 0), lambda _day: False)
        == "non_trading_day"
    )


def test_source_as_of_date_is_explicit_and_reads_market_metadata():
    assert capture_probe._source_as_of_date("zhb", {"zhb_date": "2026-09-29"}) == "2026-09-29"
    assert (
        capture_probe._source_as_of_date("ftshare", {"market": {"probe_trading_day": "20260929"}})
        == "20260929"
    )
    assert capture_probe._source_as_of_date("push2", {"stocks": {}}) is None


def test_zhb_freshness_uses_latest_trade_date_for_weekend_target():
    ok, info = capture_probe._apply_zhb_freshness(
        True,
        {"status": "ok", "n_error": 0, "n_received": 20},
        {"zhb_date": "20261016"},
        "20261017",
    )

    assert ok is True
    assert info["status"] == "ok"
    assert info["freshness"] == {
        "status": "current",
        "expected_as_of_date": "20261016",
        "actual_as_of_date": "20261016",
        "matches_expected_date": True,
        "reason": None,
    }


def test_zhb_stale_cache_is_partial_even_when_all_stocks_loaded(monkeypatch):
    from datetime import date

    from stock_common import stock_calendar

    monkeypatch.setattr(
        stock_calendar,
        "latest_market_data_date",
        lambda _target: date(2026, 10, 16),
    )
    ok, info = capture_probe._apply_zhb_freshness(
        True,
        {"status": "ok", "n_error": 0, "n_received": 20},
        {"zhb_date": "20261015"},
        "20261017",
    )

    assert ok is False
    assert info["status"] == "partial"
    assert info["n_error"] == 0
    assert info["freshness"]["status"] == "stale"
    assert info["freshness"]["expected_as_of_date"] == "20261016"
    assert info["freshness"]["actual_as_of_date"] == "20261015"
    assert "20261015" in info["freshness_issue"]


def test_zhb_future_or_missing_date_cannot_report_current(monkeypatch):
    from datetime import date

    from stock_common import stock_calendar

    monkeypatch.setattr(
        stock_calendar,
        "latest_market_data_date",
        lambda _target: date(2026, 10, 15),
    )
    ok, future = capture_probe._apply_zhb_freshness(
        True, {"status": "ok"}, {"zhb_date": "20261016"}, "20261015"
    )
    assert ok is False
    assert future["status"] == "partial"
    assert future["freshness"]["status"] == "future"

    ok, missing = capture_probe._apply_zhb_freshness(
        True, {"status": "ok"}, {"stocks": {}}, "20261017"
    )
    assert ok is False
    assert missing["status"] == "partial"
    assert missing["freshness"]["status"] == "unknown"


def test_zhb_calendar_failure_is_visible_and_fails_closed(monkeypatch):
    from stock_common import stock_calendar

    def unavailable(_target):
        raise RuntimeError("calendar unavailable")

    monkeypatch.setattr(stock_calendar, "latest_market_data_date", unavailable)
    ok, info = capture_probe._apply_zhb_freshness(
        True, {"status": "ok"}, {"zhb_date": "20261016"}, "20261017"
    )

    assert ok is False
    assert info["status"] == "partial"
    assert info["freshness"]["status"] == "unverified"
    assert "calendar unavailable" in info["freshness_issue"]


def test_stale_zhb_rerun_preserves_existing_current_snapshot(tmp_path, monkeypatch):
    from datetime import date

    from stock_common import stock_calendar

    monkeypatch.setattr(
        stock_calendar,
        "latest_market_data_date",
        lambda _target: date(2026, 10, 16),
    )
    path = tmp_path / "raw_zhb.json"
    existing_text = '{"zhb_date":"20261016","stocks":{"600000":{"full":{"x":1}}}}'
    path.write_text(existing_text, encoding="utf-8")
    attempted = {"zhb_date": "20261015", "stocks": {"600000": {"full": {"x": 0}}}}

    selected, write_raw, note = capture_probe._retain_current_zhb_snapshot(
        attempted, str(path), "20261017"
    )

    assert selected["zhb_date"] == "20261016"
    assert write_raw is False
    assert note["status"] == "noncurrent_refresh_rejected"
    assert note["attempted_freshness"]["status"] == "stale"
    assert note["retained_as_of_date"] == "20261016"
    assert path.read_text(encoding="utf-8") == existing_text


def test_older_stale_zhb_refresh_does_not_regress_existing_snapshot(tmp_path, monkeypatch):
    from datetime import date

    from stock_common import stock_calendar

    monkeypatch.setattr(
        stock_calendar,
        "latest_market_data_date",
        lambda _target: date(2026, 10, 16),
    )
    path = tmp_path / "raw_zhb.json"
    existing_text = '{"zhb_date":"20261015","stocks":{"600000":{"full":{"x":1}}}}'
    path.write_text(existing_text, encoding="utf-8")
    attempted = {"zhb_date": "20261014", "stocks": {"600000": {"full": {"x": 0}}}}

    selected, write_raw, note = capture_probe._retain_current_zhb_snapshot(
        attempted, str(path), "20261017"
    )

    assert selected["zhb_date"] == "20261015"
    assert write_raw is False
    assert note["status"] == "older_refresh_rejected"
    assert note["retained_as_of_date"] == "20261015"
    assert path.read_text(encoding="utf-8") == existing_text


def test_stale_zhb_rerun_does_not_overwrite_unreadable_snapshot(tmp_path, monkeypatch):
    from datetime import date

    from stock_common import stock_calendar

    monkeypatch.setattr(
        stock_calendar,
        "latest_market_data_date",
        lambda _target: date(2026, 10, 16),
    )
    path = tmp_path / "raw_zhb.json"
    path.write_text("unreadable", encoding="utf-8")
    attempted = {"zhb_date": "20261015", "stocks": {}}

    selected, write_raw, note = capture_probe._retain_current_zhb_snapshot(
        attempted, str(path), "20261017"
    )

    assert selected is attempted
    assert write_raw is False
    assert note["status"] == "existing_snapshot_unreadable"
    assert path.read_text(encoding="utf-8") == "unreadable"


def test_unverified_zhb_refresh_preserves_existing_snapshot(tmp_path, monkeypatch):
    from stock_common import stock_calendar

    def unavailable(_target):
        raise RuntimeError("calendar unavailable")

    monkeypatch.setattr(stock_calendar, "latest_market_data_date", unavailable)
    path = tmp_path / "raw_zhb.json"
    existing_text = '{"zhb_date":"20261016","stocks":{"600000":{"full":{"x":1}}}}'
    path.write_text(existing_text, encoding="utf-8")
    attempted = {"zhb_date": "20261015", "stocks": {"600000": {"full": {"x": 0}}}}

    selected, write_raw, note = capture_probe._retain_current_zhb_snapshot(
        attempted, str(path), "20261017"
    )

    assert selected["zhb_date"] == "20261016"
    assert write_raw is False
    assert note["status"] == "freshness_unverified"
    assert path.read_text(encoding="utf-8") == existing_text


def test_current_zhb_result_is_writable_when_no_snapshot_exists(tmp_path):
    path = tmp_path / "raw_zhb.json"
    current = {"zhb_date": "20261016", "stocks": {}}

    selected, write_raw, note = capture_probe._retain_current_zhb_snapshot(
        current, str(path), "20261017"
    )

    assert selected is current
    assert write_raw is True
    assert note is None


def test_fuyao_auction_timestamp_is_not_treated_as_source_data_date():
    meta = capture_probe._fuyao_auction_snapshot_meta(
        {
            "code": 0,
            "timestamp": "2026-09-29T09:25:00",
            "data": {"auction_phase": "final", "data_status": "ready", "item": []},
        },
        "final",
        date(2026, 9, 29),
    )

    assert meta["response_timestamp"] == "2026-09-29T09:25:00"
    assert meta["source_data_date"] is None
    assert meta["collision_eligible"] is False
    assert meta["exclusion_reason"] == "source_data_date_unavailable"


def test_fuyao_auction_requires_ready_status_and_matching_explicit_date():
    eligible = capture_probe._fuyao_auction_snapshot_meta(
        {
            "code": 0,
            "timestamp": "2026-09-29T09:25:00",
            "data": {
                "trade_date": "20260929",
                "auction_phase": "final",
                "data_status": "ready",
                "item": [],
            },
        },
        "final",
        date(2026, 9, 29),
    )
    not_ready = capture_probe._fuyao_auction_snapshot_meta(
        {
            "code": 0,
            "data": {"trade_date": "2026-09-29", "data_status": "not_ready", "item": []},
        },
        "final",
        date(2026, 9, 29),
    )
    mismatched = capture_probe._fuyao_auction_snapshot_meta(
        {
            "code": 0,
            "data": {"trade_date": "2026-09-30", "data_status": "ready", "item": []},
        },
        "final",
        date(2026, 9, 29),
    )

    assert eligible["source_data_date"] == "2026-09-29"
    assert eligible["collision_eligible"] is True
    assert eligible["exclusion_reason"] is None
    assert not_ready["collision_eligible"] is False
    assert not_ready["exclusion_reason"] == "source_status_not_confirmed_ready"
    assert mismatched["collision_eligible"] is False
    assert mismatched["exclusion_reason"] == "source_date_differs_from_snapshot_date"


def test_fuyao_auction_legacy_api_still_returns_item_list(monkeypatch):
    items = [{"ticker": "600000.SH", "auction_price": 10.0}]
    envelope = {"code": 0, "data": {"item": items}}
    calls = []
    stage = f"unit_test_{uuid4().hex}"

    def fake_raw(path, params):
        calls.append((path, params))
        return envelope

    monkeypatch.setattr(sc_fuyao, "_fuyao_raw", fake_raw)
    codes = ["600000", "000001"]

    assert stock_common.get_fuyao_auction_snapshot_envelope(codes, stage=stage) == envelope
    assert stock_common.get_fuyao_auction_snapshot(codes, stage=stage) == items
    assert calls == [
        (
            sc_fuyao.EP_AUCTION_SNAP,
            {"thscodes": "600000.SH,000001.SZ", "stage": stage},
        )
    ]
    assert callable(stock_common.get_fuyao_auction_snapshot_envelope)


@pytest.mark.parametrize("include_context", [False, True])
def test_collect_fuyao_preserves_auction_envelope_and_tags_rows(monkeypatch, include_context):
    envelope_calls = []
    context_calls = []
    auction_item = {"ticker": "600000", "auction_price": 10.2}

    monkeypatch.setattr(capture_probe, "_last_completed_trading_day", lambda: date(2026, 9, 29))
    monkeypatch.setattr(stock_common, "is_fuyao_enabled", lambda: True)
    monkeypatch.setattr(stock_common, "get_fuyao_snapshot", lambda _codes: [{"ticker": "600000"}])
    monkeypatch.setattr(stock_common, "get_fuyao_valuation", lambda _codes: [])
    monkeypatch.setattr(stock_common, "get_fuyao_fin_indicators", lambda *_args: None)

    def auction_envelope(codes, stage="final"):
        envelope_calls.append((codes, stage))
        return {
            "code": 0,
            "timestamp": "2026-09-29T09:25:00",
            "data": {
                "auction_phase": "final",
                "data_status": "ready",
                "item": [auction_item],
            },
        }

    monkeypatch.setattr(stock_common, "get_fuyao_auction_snapshot_envelope", auction_envelope)
    monkeypatch.setattr(stock_common, "get_fuyao_auction_benchmark", lambda _day: [])
    monkeypatch.setattr(
        stock_common,
        "get_fuyao_limit_pool",
        lambda *_args, **_kwargs: {"item": [], "pagination": {"total": 0}},
    )
    monkeypatch.setattr(stock_common, "get_fuyao_anomaly", lambda: [])
    monkeypatch.setattr(
        stock_common,
        "get_fuyao_dragon_tiger",
        lambda _day: context_calls.append("dragon_tiger") or [],
    )
    monkeypatch.setattr(
        stock_common,
        "get_fuyao_hot_list",
        lambda _period: context_calls.append("hot_list_hour") or [],
    )
    monkeypatch.setattr(sc_fuyao, "get_fuyao_financials", lambda *_args, **_kwargs: [])

    result = capture_probe.collect_fuyao([{"code": "600000"}], include_context=include_context)

    stock = result["stocks"]["600000"]
    assert envelope_calls == [(["600000"], "final")]
    assert result["probe_trading_day"] == "2026-09-29"
    assert result["auction_snapshot_meta"]["source_data_date"] is None
    assert stock["snapshot"] == {"ticker": "600000"}
    assert stock["auction_final"]["auction_price"] == auction_item["auction_price"]
    assert stock["auction_final"]["__source_meta__"]["collision_eligible"] is False
    assert context_calls == (["dragon_tiger", "hot_list_hour"] if include_context else [])
    assert ("dragon_tiger" in result["market"]) is include_context
    assert ("hot_list_hour" in result["market"]) is include_context


def test_axdata_scheme_describes_its_local_shortline_source():
    assert capture_probe.SOURCE_SCHEME["axdata"] == "axdata.shortline"


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
    known_trading_days = {date(2026, 9, 24), date(2026, 9, 28), date(2026, 10, 9)}
    monkeypatch.setattr(
        "stock_common.stock_calendar.is_workday_with_zhb_supplement",
        lambda value: value in known_trading_days,
    )
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


def test_rate_limit_detection_accepts_string_http_status():
    assert capture_probe._request_is_rate_limited({"status_code": "403"})
    assert capture_probe._request_is_rate_limited({"status_code": 429})
    assert not capture_probe._request_is_rate_limited({"status_code": "503"})


def test_push2_opens_local_circuit_after_explicit_ban(monkeypatch):
    calls = []

    def fake_request(url, **kwargs):
        calls.append((url, kwargs))
        if "push2delay.eastmoney.com" in url:
            kwargs["error_out"].update(
                {"kind": "ip_banned", "domain": "push2delay.eastmoney.com", "attempts": 1}
            )
            return None
        return SimpleNamespace(json=lambda: {"data": {"f1": "1", "f12": "600000"}})

    monkeypatch.setattr(stock_common, "_quick_request", fake_request)
    monkeypatch.setattr(sc_network, "_em_is_banned", lambda _domain: False)

    result = capture_probe.collect_push2([{"code": "600000"}, {"code": "000001"}])

    delay_calls = [call for call in calls if "push2delay.eastmoney.com" in call[0]]
    primary_calls = [call for call in calls if "push2.eastmoney.com" in call[0]]
    assert len(delay_calls) == 1
    assert len(primary_calls) == 2
    assert all(kwargs["max_retries"] == 1 for _, kwargs in calls)
    assert result["stocks"]["600000"]["host"] == "push2"


def test_clist_failure_reports_both_domains(monkeypatch):
    calls = []

    def fake_request(url, **kwargs):
        calls.append((url, kwargs))
        kwargs["error_out"].update(
            {"kind": "http_403", "domain": url.split("/")[2], "status_code": 403}
        )
        return None

    monkeypatch.setattr(stock_common, "_quick_request", fake_request)
    monkeypatch.setattr(sc_network, "_em_is_banned", lambda _domain: False)

    result = capture_probe.collect_clist([])

    assert len(calls) == 2
    assert all(kwargs["max_retries"] == 1 for _, kwargs in calls)
    for label in ("industry", "concept", "area"):
        error = result["by_type"][label]["__error__"]
        assert "push2delay.eastmoney.com" in error
        assert "push2.eastmoney.com" in error
        assert "status=403" in error


def test_slist_preserves_transport_details_and_stops_after_ban(monkeypatch):
    calls = []

    def fake_request(url, **kwargs):
        calls.append((url, kwargs))
        kwargs["error_out"].update(
            {"kind": "http_403", "domain": url.split("/")[2], "status_code": 403}
        )
        return None

    monkeypatch.setattr(stock_common, "_quick_request", fake_request)
    monkeypatch.setattr(sc_network, "_em_is_banned", lambda _domain: False)

    result = capture_probe.collect_slist([{"code": "600000"}, {"code": "000001"}])

    assert len(calls) == 2
    assert all(kwargs["max_retries"] == 1 for _, kwargs in calls)
    for code in ("600000", "000001"):
        error = result["stocks"][code]["__error__"]
        assert "push2delay.eastmoney.com" in error
        assert "push2.eastmoney.com" in error
        assert "status=403" in error


def test_ulist_reports_missing_pool_codes_and_limits_request_attempts(monkeypatch):
    calls = []

    class Response:
        def json(self):
            return {"data": {"diff": [{"f12": "600000", "f1": "1"}]}}

    def fake_request(url, **kwargs):
        calls.append((url, kwargs))
        return Response()

    monkeypatch.setattr(stock_common, "_quick_request", fake_request)
    result = capture_probe.collect_ulist239([{"code": "600000"}, {"code": "000001"}])

    assert calls[0][1]["max_retries"] == 1
    assert "missing" in result["stocks"]["000001"]["__error__"]
    ok, info = capture_probe.assess_result(result, expected_symbols=["600000", "000001"])
    assert ok is False
    assert info["status"] == "partial"
    assert info["n_error"] == 1


def test_eltdx_exposes_preopen_shortline_as_deferred(monkeypatch):
    readiness_error = RuntimeError("shortline indicators not ready before 09:25")

    class FakeHelpers:
        def limit_ladder(self, **_kwargs):
            raise readiness_error

        def theme_strength_rank(self, **_kwargs):
            raise readiness_error

        def stock_theme_strength_rank(self, **_kwargs):
            raise readiness_error

        def realtime_rank(self):
            return []

        def shortline_indicators(self, _codes):
            raise readiness_error

    client = SimpleNamespace(
        helpers=FakeHelpers(),
        quotes=SimpleNamespace(get_snapshots=lambda _codes: {"sh600000": {"last_price": 10.0}}),
        bars=SimpleNamespace(get=lambda *_args, **_kwargs: []),
        close=lambda: None,
    )
    fake_eltdx = ModuleType("eltdx")
    fake_eltdx.TdxClient = lambda **_kwargs: client
    fake_eltdx.F10Client = lambda **_kwargs: None
    monkeypatch.setitem(sys.modules, "eltdx", fake_eltdx)

    class FixedDateTime:
        @classmethod
        def now(cls):
            return datetime(2026, 9, 30, 8, 50)

    monkeypatch.setattr(capture_probe, "datetime", FixedDateTime)
    result = capture_probe.collect_eltdx([{"code": "600000"}], lite=True)

    assert result["stocks"]["600000"]["shortline"]["__skipped__"].startswith("deferred:")
    assert result["global_helpers"]["limit_ladder"]["__skipped__"].startswith("deferred:")
    ok, info = capture_probe.assess_result(result, expected_symbols=["600000"])
    assert ok is False
    assert info["status"] == "partial"
    assert info["n_error"] == 0
    assert info["n_deferred"] == 4


def test_eltdx_captures_bse_snapshot_and_shortline_with_bj_prefix(monkeypatch):
    pool_codes = ["920118", "920508"]
    requested_shortline = []
    requested_snapshots = []
    requested_bars = []
    requested_finance = []

    class FakeHelpers:
        def limit_ladder(self, codes=None):
            assert codes == ["bj920118", "bj920508"]
            return SimpleNamespace(rows=[])

        def theme_strength_rank(self, codes=None):
            assert codes == ["bj920118", "bj920508"]
            return SimpleNamespace(rows=[])

        def stock_theme_strength_rank(self, codes=None):
            assert codes == ["bj920118", "bj920508"]
            return SimpleNamespace(rows=[])

        def realtime_rank(self):
            return []

        def shortline_indicators(self, codes):
            requested_shortline.extend(codes)
            return SimpleNamespace(
                rows=[
                    {"full_code": code, "stats_date": "2026-10-09", "last_price": 12.34}
                    for code in codes
                ]
            )

    class FakeQuotes:
        def get_snapshots(self, codes):
            requested_snapshots.append(list(codes))
            return {code: {"code": code, "exchange": "bj", "last_price": 12.34} for code in codes}

    def get_bars(code, **_kwargs):
        requested_bars.append(code)
        return SimpleNamespace(bars=[{"code": code, "time": "2026-10-09"}])

    def get_finance(code, **_kwargs):
        requested_finance.append(code)
        return SimpleNamespace(records=[{"code": code, "market_id": 2}])

    client = SimpleNamespace(
        helpers=FakeHelpers(),
        quotes=FakeQuotes(),
        bars=SimpleNamespace(get=get_bars),
        corporate=SimpleNamespace(finance_batch=get_finance),
        close=lambda: None,
    )
    fake_eltdx = ModuleType("eltdx")
    fake_eltdx.TdxClient = lambda **_kwargs: client
    monkeypatch.setitem(sys.modules, "eltdx", fake_eltdx)

    result = capture_probe.collect_eltdx([{"code": code} for code in pool_codes], lite=False)

    assert requested_shortline == ["bj920118", "bj920508"]
    assert requested_snapshots == [["bj920118", "bj920508"]]
    assert requested_bars == ["sh880005", "bj920118", "bj920508"]
    assert requested_finance == ["bj920118", "bj920508"]
    for code in pool_codes:
        assert result["stocks"][code]["quote_snapshot"]["exchange"] == "bj"
        assert result["stocks"][code]["shortline"]["stats_date"] == "2026-10-09"
        assert result["stocks"][code]["kline_day"][0]["code"] == f"bj{code}"
        assert result["stocks"][code]["finance_batch"][0]["market_id"] == 2


def test_eltdx_capture_does_not_request_unused_f10_news(monkeypatch):
    class FakeHelpers:
        def limit_ladder(self, **_kwargs):
            return SimpleNamespace(rows=[])

        def theme_strength_rank(self, **_kwargs):
            return SimpleNamespace(rows=[])

        def stock_theme_strength_rank(self, **_kwargs):
            return SimpleNamespace(rows=[])

        def realtime_rank(self):
            return []

        def shortline_indicators(self, codes):
            return SimpleNamespace(rows=[{"full_code": codes[0], "stats_date": "2026-10-09"}])

    client = SimpleNamespace(
        helpers=FakeHelpers(),
        quotes=SimpleNamespace(
            get_snapshots=lambda codes: {code: {"code": code, "last_price": 10.0} for code in codes}
        ),
        bars=SimpleNamespace(get=lambda *_args, **_kwargs: SimpleNamespace(bars=[])),
        corporate=SimpleNamespace(
            finance_batch=lambda *_args, **_kwargs: SimpleNamespace(records=[])
        ),
        close=lambda: None,
    )

    def unexpected_f10_client(**_kwargs):
        raise AssertionError("unused F10 news must not be requested")

    fake_eltdx = ModuleType("eltdx")
    fake_eltdx.TdxClient = lambda **_kwargs: client
    fake_eltdx.F10Client = unexpected_f10_client
    monkeypatch.setitem(sys.modules, "eltdx", fake_eltdx)

    result = capture_probe.collect_eltdx([{"code": "600000"}], lite=False)

    assert "f10_news" not in result["stocks"]["600000"]


@pytest.mark.parametrize("failure_kind", ["http_403", "http_429", "ip_banned"])
@pytest.mark.parametrize(
    "collector", [capture_probe.collect_em_kline_f61, capture_probe.collect_em_fund_flow]
)
def test_eastmoney_collector_stops_after_rate_limit(monkeypatch, collector, failure_kind):
    calls = []

    def fake_request(url, **kwargs):
        calls.append(url)
        error = kwargs["error_out"]
        error.update({"kind": failure_kind, "domain": url.split("/")[2], "attempts": 1})
        if failure_kind in {"http_403", "http_429"}:
            error["status_code"] = int(failure_kind[-3:])
        return None

    monkeypatch.setattr(stock_common, "_quick_request", fake_request)
    pool = [{"code": "600000"}, {"code": "000001"}, {"code": "920118"}]

    result = collector(pool)

    assert len(calls) == 1
    assert failure_kind in result["stocks"]["600000"]["__error__"]
    assert "source paused after" in result["stocks"]["000001"]["__skipped__"]
    assert "source paused after" in result["stocks"]["920118"]["__skipped__"]


@pytest.mark.parametrize(
    "collector", [capture_probe.collect_em_kline_f61, capture_probe.collect_em_fund_flow]
)
def test_eastmoney_collector_stops_after_three_disconnects(monkeypatch, collector):
    calls = []

    def fake_request(url, **kwargs):
        calls.append(url)
        kwargs["error_out"].update(
            {"kind": "connection_error", "domain": url.split("/")[2], "attempts": 1}
        )
        return None

    monkeypatch.setattr(stock_common, "_quick_request", fake_request)
    pool = [{"code": f"60000{index}"} for index in range(4)]

    result = collector(pool)

    assert len(calls) == 3
    assert "connection_error" in result["stocks"]["600000"]["__error__"]
    assert "connection_error" in result["stocks"]["600002"]["__error__"]
    assert "consecutive connection_error failures" in result["stocks"]["600003"]["__skipped__"]


def test_kline_and_fund_flow_failures_keep_transport_details(monkeypatch):
    calls = []

    def fake_request(url, **kwargs):
        calls.append((url, kwargs))
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
    assert all(kwargs["max_retries"] == 1 for _, kwargs in calls)


def test_failed_raw_snapshot_does_not_pass_idempotency_check(tmp_path):
    raw_path = tmp_path / "raw_push2.json"
    pool = [{"code": "600000"}, {"code": "000001"}]
    collectors = {"push2": capture_probe.collect_push2}
    meta = {"sources": {"push2": {"ok": True, "status": "ok"}}}

    raw_path.write_text(
        '{"stocks":{"600000":{"data":{"f1":"1"}}},"scheme":"em.stock_get"}',
        encoding="utf-8",
    )
    assert not capture_probe._has_complete_snapshot(collectors, meta, str(tmp_path), pool)

    raw_path.write_text(
        '{"stocks":{"600000":{"data":{"f1":"1"}},"000001":{"data":{"f1":"2"}}},'
        '"scheme":"em.stock_get"}',
        encoding="utf-8",
    )
    assert capture_probe._has_complete_snapshot(collectors, meta, str(tmp_path), pool)

    raw_path.write_text(
        '{"stocks":{"600000":{"__error__":"ip_banned"},' '"000001":{"__error__":"ip_banned"}}}',
        encoding="utf-8",
    )
    assert not capture_probe._has_complete_snapshot(collectors, meta, str(tmp_path), pool)


def test_snapshot_idempotency_requires_prior_source_status(tmp_path):
    raw_path = tmp_path / "raw_push2.json"
    raw_path.write_text(
        '{"stocks":{"600000":{"data":{"f1":"1"}}},"scheme":"em.stock_get"}',
        encoding="utf-8",
    )
    collectors = {"push2": capture_probe.collect_push2}
    pool = [{"code": "600000"}]

    assert not capture_probe._has_complete_snapshot(collectors, {}, str(tmp_path), pool)
    assert capture_probe._has_complete_snapshot(
        collectors,
        {"sources": {"push2": {"ok": True, "status": "ok"}}},
        str(tmp_path),
        pool,
    )


def test_non_raw_source_states_are_complete_without_raw_files(tmp_path):
    collectors = {"future_source": lambda _pool: {}, "baidu": capture_probe.collect_baidu}
    meta = {
        "sources": {
            "future_source": {"ok": False, "status": "unwired"},
            "baidu": {"ok": False, "status": "pending_validation"},
        }
    }

    assert capture_probe._has_complete_snapshot(collectors, meta, str(tmp_path), [])

    meta["sources"]["baidu"]["status"] = "unwired"
    assert not capture_probe._has_complete_snapshot(collectors, meta, str(tmp_path), [])


def test_only_selection_reruns_a_complete_existing_source(tmp_path, monkeypatch):
    out_dir = tmp_path / "20260929"
    out_dir.mkdir()
    (out_dir / "raw_push2.json").write_text(
        '{"stocks":{"600000":{"data":{"f1":"old"}}},"scheme":"em.stock_get"}',
        encoding="utf-8",
    )
    (out_dir / "meta.json").write_text(
        '{"date":"20260929","data_date":"20260929","market_phase":"closed",'
        '"sources":{"push2":{"ok":true,"status":"ok"}}}',
        encoding="utf-8",
    )
    calls = []
    coverage_calls = []

    monkeypatch.setattr(capture_probe, "OUT_BASE", str(tmp_path))
    monkeypatch.setattr(
        capture_probe,
        "_refresh_field_evidence_coverage",
        lambda path, metadata: coverage_calls.append((path, metadata.get("data_date"))),
    )
    monkeypatch.setattr(capture_probe, "load_pool", lambda: [{"code": "600000"}])
    monkeypatch.setattr(
        sys,
        "argv",
        ["capture_field_probe.py", "--date", "20260929", "--only", "push2"],
    )
    monkeypatch.setattr(
        capture_probe, "_validate_capture_data_date", lambda *_args: (date(2026, 9, 29), "trading")
    )
    monkeypatch.setattr(capture_probe, "_is_closed_phase_now", lambda *_args: True)
    monkeypatch.setattr(capture_probe, "_capture_market_phase", lambda *_args: "closed")
    monkeypatch.setattr(capture_probe, "_last_trading_day_str", lambda: "20260929")
    axdata_validation = ModuleType("axdata_daily_validation")
    axdata_validation.run_axdata_daily_validation = lambda **_kwargs: {"status": "not_eligible"}
    monkeypatch.setitem(sys.modules, "axdata_daily_validation", axdata_validation)
    monkeypatch.setitem(sys.modules, "scripts.axdata_daily_validation", axdata_validation)
    source_identity = ModuleType("source_identity_reconciliation")
    source_identity.reconcile_source_identity = lambda **_kwargs: {"status": "ok"}
    monkeypatch.setitem(sys.modules, "source_identity_reconciliation", source_identity)
    monkeypatch.setitem(sys.modules, "scripts.source_identity_reconciliation", source_identity)

    def fake_push2(pool):
        calls.append([item["code"] for item in pool])
        return {"stocks": {"600000": {"data": {"f1": "new"}}}}

    monkeypatch.setattr(capture_probe, "collect_push2", fake_push2)
    capture_probe.main()

    assert calls == [["600000"]]
    assert coverage_calls == [(str(out_dir), "20260929")]
    raw = json.loads((out_dir / "raw_push2.json").read_text(encoding="utf-8"))
    assert raw["stocks"]["600000"]["data"]["f1"] == "new"


def test_field_evidence_coverage_hook_is_fail_open_and_does_not_change_dates_or_raw(
    tmp_path, monkeypatch
):
    from types import ModuleType

    out_dir = tmp_path / "20261014"
    out_dir.mkdir()
    raw_path = out_dir / "raw_push2.json"
    raw_path.write_text('{"scheme":"em.stock_get","stocks":{}}', encoding="utf-8")
    calls = []
    coverage_module = ModuleType("field_evidence_coverage")

    def fake_refresh(path, metadata, *, data_dir):
        calls.append((path, metadata["data_date"], data_dir))
        return {"status": "ok", "pending_source_fields": 10, "targets_observed": 2}

    coverage_module.refresh_daily_coverage = fake_refresh
    monkeypatch.setitem(sys.modules, "field_evidence_coverage", coverage_module)
    monkeypatch.setattr(capture_probe, "OUT_BASE", str(tmp_path))
    snapshot_meta = {"data_date": "20261014", "source_as_of_dates": {"push2": "20261014"}}

    capture_probe._refresh_field_evidence_coverage(str(out_dir), snapshot_meta)

    assert calls == [(str(out_dir), "20261014", str(tmp_path))]
    assert snapshot_meta["data_date"] == "20261014"
    assert snapshot_meta["source_as_of_dates"] == {"push2": "20261014"}
    assert snapshot_meta["field_evidence_coverage"]["status"] == "ok"
    assert raw_path.read_text(encoding="utf-8") == '{"scheme":"em.stock_get","stocks":{}}'
    saved_meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    assert saved_meta["field_evidence_coverage"]["pending_source_fields"] == 10


def test_field_evidence_coverage_failure_does_not_abort_capture(tmp_path, monkeypatch):
    from types import ModuleType

    out_dir = tmp_path / "20261014"
    out_dir.mkdir()
    raw_path = out_dir / "raw_push2.json"
    raw_path.write_text('{"stocks":{}}', encoding="utf-8")
    coverage_module = ModuleType("field_evidence_coverage")

    def fail_refresh(*_args, **_kwargs):
        raise OSError("offline index unavailable")

    coverage_module.refresh_daily_coverage = fail_refresh
    monkeypatch.setitem(sys.modules, "field_evidence_coverage", coverage_module)
    capture_probe._refresh_field_evidence_coverage(str(out_dir), {"data_date": "20261014"})

    assert raw_path.read_text(encoding="utf-8") == '{"stocks":{}}'
    saved_meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    assert saved_meta["field_evidence_coverage"]["status"] == "failed_open"
    assert "offline index unavailable" in saved_meta["field_evidence_coverage"]["reason"]


def test_network_failure_diagnostics_redact_query_parameters(monkeypatch):
    monkeypatch.setattr(sc_network, "_EM_BANNED_UNTIL", {})
    monkeypatch.setattr(sc_network, "_load_banned_file", lambda: {})
    monkeypatch.setattr(sc_network, "_record_em_disconnect", lambda _domain: None)
    monkeypatch.setattr(sc_network, "_HAS_FAULT_TOLERANCE", False)

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
    monkeypatch.setattr(sc_network, "_EM_BANNED_UNTIL", {})
    monkeypatch.setattr(sc_network, "_load_banned_file", lambda: {})
    monkeypatch.setattr(sc_network, "_HAS_FAULT_TOLERANCE", False)
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


def test_network_stream_option_reaches_requests_session(monkeypatch):
    captured = {}
    response = SimpleNamespace(status_code=200, headers={})

    class StreamingSession:
        def get(self, _url, **kwargs):
            captured.update(kwargs)
            return response

    monkeypatch.setattr(sc_network, "_HTTP_SESSION", StreamingSession())
    monkeypatch.setattr(sc_network, "_resolve_host_with_timeout", lambda _domain: None)
    monkeypatch.setattr(sc_network, "_em_wait_process_interval", lambda: None)

    result = sc_network._do_request(
        "https://stock.gtimg.cn/data/index.php",
        params=None,
        headers=None,
        timeout=(5, 15),
        max_retries=1,
        data=None,
        method="GET",
        verify=True,
        stream=True,
    )

    assert result is response
    assert captured["stream"] is True
    assert captured["timeout"] == (5, 15)


def test_streamed_http_error_closes_response(monkeypatch):
    closed = []
    response = SimpleNamespace(status_code=503, headers={}, close=lambda: closed.append(True))
    detail = {}

    class StreamingSession:
        def get(self, _url, **_kwargs):
            return response

    monkeypatch.setattr(sc_network, "_HTTP_SESSION", StreamingSession())
    monkeypatch.setattr(sc_network, "_resolve_host_with_timeout", lambda _domain: None)
    monkeypatch.setattr(sc_network, "_em_wait_process_interval", lambda: None)

    result = sc_network._do_request(
        "https://stock.gtimg.cn/data/index.php",
        params=None,
        headers=None,
        timeout=(5, 15),
        max_retries=1,
        data=None,
        method="GET",
        verify=True,
        error_out=detail,
        stream=True,
    )

    assert result is None
    assert closed == [True]
    assert detail["status_code"] == 503


def test_non_eastmoney_403_does_not_touch_eastmoney_ban_counter(monkeypatch):
    response = SimpleNamespace(status_code=403, headers={})

    class DeniedSession:
        def get(self, _url, **_kwargs):
            return response

    monkeypatch.setattr(sc_network, "_HTTP_SESSION", DeniedSession())
    monkeypatch.setattr(sc_network, "_resolve_host_with_timeout", lambda _domain: None)
    monkeypatch.setattr(sc_network, "_em_wait_process_interval", lambda: None)
    monkeypatch.setattr(sc_network, "_HAS_FAULT_TOLERANCE", False)
    monkeypatch.setitem(sc_network._CONSECUTIVE_403, "count", 0)
    monkeypatch.setitem(sc_network._CONSECUTIVE_403, "last_ts", 0.0)
    detail = {}

    result = sc_network._do_request(
        "https://stock.gtimg.cn/data/index.php",
        params=None,
        headers=None,
        timeout=1,
        max_retries=1,
        data=None,
        method="GET",
        verify=True,
        error_out=detail,
    )

    assert result is None
    assert detail["kind"] == "http_403"
    assert sc_network._CONSECUTIVE_403["count"] == 0


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


def test_kph_history_date_uses_trading_calendar_and_stays_before_today(monkeypatch):
    from stock_common import stock_calendar

    trading_days = {date(2026, 9, 28)}
    monkeypatch.setattr(
        stock_calendar,
        "is_workday_with_zhb_supplement",
        lambda candidate: candidate in trading_days,
    )

    assert capture_probe._kph_history_trade_date("20260930", today=date(2026, 9, 30)) == date(
        2026, 9, 28
    )
    with pytest.raises(ValueError, match="future"):
        capture_probe._kph_history_trade_date("20261001", today=date(2026, 9, 30))


def test_collect_kpl_detail_preserves_all_source_fields_and_row_identity(monkeypatch):
    rows_by_pid_type = {
        1: [
            {
                "code": "600000",
                "name": "浦发银行",
                "zt_time": 1790645140,
                "seal_amount": 12.0,
                "max_seal": 34.0,
                "main_inflow": 56.0,
                "amount": 78.0,
                "turnover_real": 0.37,
                "reason": "文字概念",
                "ready": False,
                "break_times": ["09:32:45", "09:33:15"],
                "detail": {"source_flag": "raw"},
            }
        ],
        2: [{"code": "000001", "name": "平安银行", "zt_time": 1790645140, "reason": "二板"}],
        3: [{"code": "600000", "name": "浦发银行", "zt_time": 1790645140, "reason": "重复接口行"}],
    }
    calls = []

    def fake_kpl_detail(pid_type=1, capture_raw=False):
        calls.append(pid_type)
        return rows_by_pid_type.get(pid_type, [])

    monkeypatch.setattr(stock_common, "get_kpl_limit_up_detail", fake_kpl_detail)

    result = capture_probe.collect_kpl_detail("20260929")

    assert calls == [1, 2, 3, 4, 5]
    assert result["trade_date"] == "2026-09-29"
    assert result["capture_date"] == "2026-09-29"
    assert result["pid_type_counts"] == {"1": 1, "2": 1, "3": 1, "4": 0, "5": 0}
    assert result["row_count"] == 2
    assert result["raw_row_count"] == 3
    assert result["duplicate_row_count"] == 1
    assert result["duplicate_rows"][0]["symbol"] == "600000"
    assert result["duplicate_rows"][0]["fields"]["__identity__"]["pid_type"] == 3
    assert result["stocks"]["600000"] == {
        "name": "浦发银行",
        "zt_time": 1790645140,
        "seal_amount": 12.0,
        "max_seal": 34.0,
        "main_inflow": 56.0,
        "amount": 78.0,
        "turnover_real": 0.37,
        "reason": "文字概念",
        "ready": False,
        "break_times": ["09:32:45", "09:33:15"],
        "detail": {"source_flag": "raw"},
        "__identity__": {"code": "600000", "pid_type": 1},
    }
    assert result["stocks"]["000001"]["__identity__"] == {
        "code": "000001",
        "pid_type": 2,
    }


def test_collect_kph_history_preserves_all_source_fields_and_separates_identity(monkeypatch):
    from stock_common import sc_datasource

    monkeypatch.setattr(
        capture_probe,
        "_kph_history_trade_date",
        lambda _capture_date: date(2026, 9, 29),
    )
    calls = []

    def fake_records(interface, *, params, fields=None):
        calls.append((interface, params, fields))
        return [
            {
                "trade_date": "20260929",
                "symbol": "920779",
                "instrument_id": "920779.SH",
                "exchange": "SSE",
                "name": "示例证券",
                "limit_time": 1790645140,
                "seal_amount": 100.0,
                "seal_money": 200.0,
                "net_inflow": 300.0,
                "turnover": 400.0,
                "turnover_rate": 0.5,
                "future_numeric_candidate": 12.5,
                "reason": "文本原因",
            }
        ]

    monkeypatch.setattr(sc_datasource, "get_axdata_records", fake_records)
    result = capture_probe.collect_kph_history("20260929")

    assert calls == [("kph_limit_up_history", {"trade_date": "2026-09-29"}, None)]
    assert result["trade_date"] == "2026-09-29"
    assert result["stocks"]["920779"] == {
        "limit_time": 1790645140,
        "seal_amount": 100.0,
        "seal_money": 200.0,
        "net_inflow": 300.0,
        "turnover": 400.0,
        "turnover_rate": 0.5,
        "future_numeric_candidate": 12.5,
        "name": "示例证券",
        "reason": "文本原因",
        "__identity__": {
            "trade_date": "20260929",
            "symbol": "920779",
            "instrument_id": "920779.SH",
            "exchange": "SSE",
        },
    }
    assert result["identity_observations"] == [
        "920779: reported_exchange=SSE; reported_instrument_id=920779.SH"
    ]
    assert any("as Shanghai" in warning for warning in result["warnings"])


def test_kph_ladder_rate_limit_skips_history_request(monkeypatch):
    from stock_common import sc_datasource

    monkeypatch.setattr(
        capture_probe,
        "_kph_history_trade_date",
        lambda _capture_date: date(2026, 9, 29),
    )
    monkeypatch.setattr(
        sc_datasource,
        "get_axdata_records",
        lambda *_args, **_kwargs: pytest.fail("request must be skipped after 429"),
    )

    result = capture_probe.collect_kph_history(
        "20260929",
        prior_market_sources={
            "kph_limit_ladder": {"__error__": "HTTP Error 429: Too Many Requests"}
        },
    )

    assert result["__skipped__"].startswith("KPH history skipped")
    assert result["stocks"] == {}


def test_market_sources_can_omit_kpl_detail_when_collected_separately(monkeypatch):
    monkeypatch.setattr(stock_common, "get_cls_market_emotion", lambda: {})
    monkeypatch.setattr(stock_common, "get_kph_limit_ladder", lambda *_args: [])
    monkeypatch.setattr(stock_common, "get_stock_changes", lambda _code: [])
    monkeypatch.setattr(stock_common, "get_kpl_market_sentiment", lambda **_kwargs: {"strong": 1})
    monkeypatch.setattr(stock_common, "get_kpl_up_down", lambda **_kwargs: {"rise_num": 1})
    monkeypatch.setattr(
        stock_common,
        "get_kpl_limit_up_detail",
        lambda **_kwargs: pytest.fail("KPL detail must be requested only by its own collector"),
    )
    monkeypatch.setattr(stock_common, "get_kpl_broken_ratio", lambda **_kwargs: {"zt": 1})
    monkeypatch.setattr(
        stock_common, "get_kpl_plate_strength", lambda **_kwargs: [{"code": "BK0001"}]
    )
    monkeypatch.setattr(stock_common, "get_plate_rotation_matrix", lambda **_kwargs: [])
    monkeypatch.setattr(stock_common, "get_plate_rotation_top", lambda: [])

    result = capture_probe.collect_market_sources([], include_kpl_detail=False)

    assert "kpl_limit_up_detail" not in result


def test_axdata_public_adapter_is_read_only_single_call_and_validates_records(monkeypatch):
    import axdata_core
    from stock_common.sc_datasource import get_axdata_records

    calls = []

    def fake_request(interface, **kwargs):
        calls.append((interface, kwargs))
        return SimpleNamespace(records=[{"symbol": "600000"}])

    monkeypatch.setattr(axdata_core, "request_interface", fake_request)
    assert get_axdata_records("kph_limit_up_history", params={"trade_date": "2026-09-29"}) == [
        {"symbol": "600000"}
    ]
    assert calls == [
        (
            "kph_limit_up_history",
            {"params": {"trade_date": "2026-09-29"}, "fields": None, "persist": False},
        )
    ]

    monkeypatch.setattr(
        axdata_core,
        "request_interface",
        lambda *_args, **_kwargs: SimpleNamespace(records=None),
    )
    with pytest.raises(TypeError, match="records must be a list"):
        get_axdata_records("kph_limit_up_history", params={"trade_date": "2026-09-29"})


def test_closed_snapshot_validation_refresh_reuses_raw_without_relabeling_mixed_date(
    tmp_path, monkeypatch
):
    output = tmp_path / "20261009"
    output.mkdir()
    market_data = {
        "cls_market_emotion": {"emotion_index": 1},
        "kph_limit_ladder": [{"trade_date": "2026-10-09", "code": "600519"}],
    }
    (output / "raw_market_sources.json").write_text(json.dumps(market_data), encoding="utf-8")
    calls = {}

    def fake_axdata(**kwargs):
        calls["axdata"] = kwargs
        return {"status": "already_recorded"}

    def fake_candidate(**kwargs):
        calls["candidate"] = kwargs
        return {
            "status": "observed",
            "candidate_id": "cls_sector_industry",
            "provider_family": "cls",
            "request_count": 1,
            "payload": {"field": 1},
        }

    def fake_levistock_validation(**kwargs):
        calls["levistock_validation"] = kwargs
        return {"status": "partial", "network_requests_added": 0}

    axdata_module = ModuleType("axdata_daily_validation")
    axdata_module.run_axdata_daily_validation = fake_axdata
    probe_module = ModuleType("levistock_daily_probe")
    probe_module.run_levistock_daily_probe = fake_candidate
    validation_module = ModuleType("levistock_daily_validation")
    validation_module.run_levistock_daily_validation = fake_levistock_validation
    monkeypatch.setitem(sys.modules, "axdata_daily_validation", axdata_module)
    monkeypatch.setitem(sys.modules, "levistock_daily_probe", probe_module)
    monkeypatch.setitem(sys.modules, "levistock_daily_validation", validation_module)
    monkeypatch.setattr(capture_probe, "_last_trading_day_str", lambda: "2026-10-09")

    snapshot_meta = {
        "data_date_domain": "mixed",
        "market_phase": "closed",
        "sources": {"market_sources": {"status": "ok"}},
    }
    capture_probe._refresh_closed_snapshot_validations(
        out_dir=str(output),
        data_date="20261009",
        pool=[{"code": "600519"}],
        snapshot_meta=snapshot_meta,
    )

    assert calls["axdata"]["data_date_domain"] == "mixed"
    assert calls["axdata"]["only"] == ""
    assert calls["candidate"]["data_date_domain"] == "trading"
    assert calls["candidate"]["market_data"] == market_data
    assert calls["levistock_validation"]["candidate_probe_meta"]["status"] == "observed"
    assert snapshot_meta["levistock_daily_candidate"]["request_count"] == 1
    assert "payload" not in snapshot_meta["levistock_daily_candidate"]
    persisted = json.loads((output / "meta.json").read_text(encoding="utf-8"))
    assert persisted["axdata_validation"]["status"] == "already_recorded"
    assert persisted["levistock_validation"]["status"] == "partial"


def test_ftshare_capture_keeps_confirmed_redundant_endpoint_values(monkeypatch):
    from scripts import source_identity_reconciliation
    from stock_common import sc_ftshare

    called = []
    monkeypatch.setattr(
        source_identity_reconciliation,
        "get_ftshare_identity_plan",
        lambda **_kwargs: {
            "status": "ready",
            "skip": {
                "ggmx": {
                    "reference_source": "tencent",
                    "reference_family": "tencent-family",
                    "evidence_dates": ["20261008", "20261009", "20261012"],
                }
            },
            "recheck": [],
            "contract_fingerprints": {"ggmx": "contract-v1"},
        },
    )
    monkeypatch.setattr(sc_ftshare, "is_ftshare_enabled", lambda: True)
    monkeypatch.setattr(sc_ftshare, "_clear_diagnostics", lambda: None)
    monkeypatch.setattr(sc_ftshare, "_ftshare_diagnostics_summary", lambda: "")

    def getter(name, value):
        def call(*_args):
            called.append(name)
            return value

        return call

    monkeypatch.setattr(sc_ftshare, "get_ft_comment_score_series", getter("comment_score", []))
    monkeypatch.setattr(sc_ftshare, "get_ft_comment_desire", getter("comment_desire", {}))
    monkeypatch.setattr(sc_ftshare, "get_ft_comment_focus", getter("comment_focus", {}))
    monkeypatch.setattr(sc_ftshare, "get_ft_comment_org_participate", getter("comment_org", {}))
    monkeypatch.setattr(sc_ftshare, "get_ft_ggmx_changes", getter("ggmx", [{"amount": 10}]))
    monkeypatch.setattr(sc_ftshare, "get_ft_goodwill_stock_detail", getter("goodwill_detail", []))
    monkeypatch.setattr(sc_ftshare, "get_ft_dapan_flow", getter("dapan_flow", [{"main_net": 12.5}]))
    monkeypatch.setattr(
        sc_ftshare, "get_ft_market_snapshot", getter("market_snapshot", {"change_rate": 1.2})
    )
    monkeypatch.setattr(
        sc_ftshare,
        "get_ft_suspension_list",
        getter("suspension_list", [{"symbol": "600000.XSHG"}]),
    )
    monkeypatch.setattr(
        sc_ftshare,
        "get_ft_limit_up_pool_yesterday",
        getter(
            "limit_up_pool_yesterday",
            [{"symbol": "600000.XSHG", "limit_up_break_count": 1}],
        ),
    )
    monkeypatch.setattr(
        sc_ftshare, "get_ft_unlock_by_date", getter("unlock_by_date", [{"stockCode": "600000"}])
    )
    monkeypatch.setattr(
        sc_ftshare, "get_ft_pledge_summary", getter("pledge_summary", {"pledge_total_ratio": 0})
    )
    monkeypatch.setattr(capture_probe, "_last_completed_trading_day", lambda: date(2026, 10, 12))

    result = capture_probe.collect_ftshare([{"code": "600000"}], data_date="20261012")

    assert called == [
        "comment_score",
        "comment_desire",
        "comment_focus",
        "comment_org",
        "ggmx",
        "goodwill_detail",
        "dapan_flow",
        "market_snapshot",
        "suspension_list",
        "limit_up_pool_yesterday",
        "unlock_by_date",
        "pledge_summary",
    ]
    assert result["stocks"]["600000"]["ggmx"] == [{"amount": 10}]
    assert result["market"]["dapan_flow"] == [{"main_net": 12.5}]
    assert result["market"]["market_snapshot"] == {"change_rate": 1.2}
    assert result["market"]["limit_up_pool_yesterday"] == [
        {"symbol": "600000.XSHG", "limit_up_break_count": 1}
    ]
    assert result["market"]["pledge_summary"] == {"pledge_total_ratio": 0}
    metadata = result["__source_meta__"]
    assert set(metadata["identity_validation_suppressed_endpoints"]) == {"ggmx"}
    assert metadata["identity_validation_suppressed_endpoints"]["ggmx"]["capture_performed"] is True
    assert "ggmx" not in metadata["identity_sampled_endpoints"]
    assert metadata["identity_contract_fingerprints"] == {"ggmx": "contract-v1"}


def test_tdx_capture_quote_normalization_handles_nullable_wire_values():
    from scripts.capture_field_probe import _normalize_tdx_capture_quote

    assert (
        _normalize_tdx_capture_quote(
            {"price": None, "last_close": None, "pre_close": None, "bid1": None}
        )
        is None
    )

    normalized = _normalize_tdx_capture_quote(
        {
            "price": "101",
            "pre_close": 100,
            "bid1": 100.9,
            "bid1_vol": 10,
            "ask1_vol": 20,
        }
    )

    assert normalized == {
        "price": "101",
        "last_close": 100,
        "bid1": 100.9,
        "bid1_vol": 10,
        "ask1_vol": 20,
        "change_pct": 1.0,
        "change_amt": 1.0,
    }

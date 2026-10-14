from __future__ import annotations

from datetime import datetime
import json
import os
import time

import pytest

from scripts import axdata_daily_validation as validation


def _project_fields(quote_time: str = "20261009161459", code: str = "600519") -> list[str]:
    fields = [""] * 88
    values = {
        "symbol": code,
        "name": "贵州茅台",
        "quote_time": quote_time,
        "last_price": "1263.00",
        "pre_close": "1255.79",
        "open": "1255.42",
        "volume": "35111",
        "change": "7.21",
        "change_pct": "0.57",
        "high": "1282.00",
        "low": "1255.42",
        "turnover_rate": "0.28",
        "pe_dynamic": "19.39",
        "total_market_value": "15788.53",
        "float_market_value": "15788.53",
        "pb": "6.28",
        "limit_up_price": "1381.37",
        "limit_down_price": "1130.21",
        "amount": "445322.3189",
    }
    for field, index in validation.TENCENT_RAW_INDEXES.items():
        fields[index] = values[field]
    fields[52] = "17.73"
    return fields


def _axdata_record(
    quote_time: str = "20261009161459", code: str = "600519"
) -> dict[str, object]:
    return {
        "symbol": code,
        "name": "贵州茅台",
        "quote_time": quote_time,
        "last_price": 1263.0,
        "pre_close": 1255.79,
        "open": 1255.42,
        "volume": 35111.0,
        "change": 7.21,
        "change_pct": 0.57,
        "high": 1282.0,
        "low": 1255.42,
        "turnover_rate": 0.28,
        "pe_dynamic": 19.39,
        "total_market_value": 15788.53,
        "float_market_value": 15788.53,
        "pb": 6.28,
        "limit_up_price": 1381.37,
        "limit_down_price": 1130.21,
        "amount": 4453223189.0,
    }


def _capture_dir(tmp_path, data_date="20261009", codes=None):
    output = tmp_path / data_date
    output.mkdir()
    codes = codes or ["600519"]
    payload = {
        "stocks": {
            code: {"fields": _project_fields(f"{data_date}161459", code)} for code in codes
        }
    }
    (output / "raw_tencent.json").write_text(json.dumps(payload), encoding="utf-8")
    return output


def _run_validation(
    output, *, data_date="20261009", only="", source_meta=None, now=None, pool=None
):
    parsed_date = datetime.strptime(data_date, "%Y%m%d")
    return validation.run_axdata_daily_validation(
        data_date=data_date,
        data_date_domain="mixed",
        market_phase="closed",
        latest_completed_trade_date=data_date,
        only=only,
        out_dir=output,
        pool=pool or [{"code": "600519"}],
        source_meta=source_meta or {"tencent": {"ok": True, "status": "ok"}},
        now=now or parsed_date.replace(hour=16),
    )


def test_validation_requires_complete_latest_market_close(tmp_path, monkeypatch):
    output = _capture_dir(tmp_path)
    monkeypatch.setattr(validation, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(validation, "_static_queue_summary", lambda: {"status": "test"})
    calls = []
    monkeypatch.setattr(
        validation, "_request_records", lambda *_args: calls.append(1) or [_axdata_record()]
    )

    result = _run_validation(output, only="tencent")

    assert result["status"] == "not_eligible"
    assert calls == []
    assert not (output / validation.EVIDENCE_FILENAME).exists()


@pytest.mark.parametrize(
    ("data_date", "domain", "phase", "expected"),
    [
        ("2026-10-09", "trading", "closed", None),
        ("2026-10-09", "calendar", "closed", "not_trading_date_capture"),
        ("2026-10-09", "trading", "intraday", "capture_not_marked_closed"),
        (
            "2026-10-08",
            "trading",
            "closed",
            "not_latest_completed_trade_date",
        ),
        ("2026-10-09", "mixed", "closed", None),
    ],
)
def test_eligibility_uses_latest_trade_date_and_capture_phase(data_date, domain, phase, expected):
    assert (
        validation._eligible_reason(
            data_date,
            domain,
            phase,
            "20261009",
            "",
        )
        == expected
    )


@pytest.mark.parametrize(
    "run_at",
    [datetime(2026, 10, 10, 8, 30), datetime(2026, 10, 12, 8, 30)],
    ids=["holiday", "pre_open"],
)
def test_probe_allows_latest_trade_date_on_holiday_or_before_open(tmp_path, monkeypatch, run_at):
    output = _capture_dir(tmp_path)
    monkeypatch.setattr(validation, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(validation, "_static_queue_summary", lambda: {"status": "test"})
    monkeypatch.setattr(validation, "_dynamic_pe_index", lambda: 52)
    monkeypatch.setattr(validation.time, "sleep", lambda _seconds: None)
    calls = []

    def fake_request(interface, params):
        calls.append((interface, params))
        return [_axdata_record()]

    monkeypatch.setattr(validation, "_request_records", fake_request)
    first = _run_validation(output, now=run_at)
    second = _run_validation(output, now=run_at)

    assert first["status"] == "sampled"
    assert first["probe"]["request_count"] == 1
    assert first["probe"]["compared_fields"] == 19
    assert first["probe"]["equal_fields"] == 18
    assert first["probe"]["semantic_conflict_fields"] == 1
    assert second["status"] == "already_recorded"
    assert len(calls) == 1
    assert calls[0][0] == "tencent_realtime_snapshot"
    evidence = json.loads((output / validation.EVIDENCE_FILENAME).read_text(encoding="utf-8"))
    comparison = evidence["probe"]["comparison"]
    assert comparison["status"] == "compared"
    assert comparison["field_comparisons"]["amount"]["status"] == "equal"
    assert (
        comparison["field_comparisons"]["pe_dynamic"]["status"]
        == "value_equal_with_dictionary_semantic_conflict"
    )
    assert comparison["dictionary_dynamic_pe_check"]["status"] == "different_or_missing"


def test_same_day_retries_after_zero_request_counterpart_skip(tmp_path, monkeypatch):
    output = _capture_dir(tmp_path)
    monkeypatch.setattr(validation, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(validation, "_static_queue_summary", lambda: {"status": "test"})
    monkeypatch.setattr(validation, "_dynamic_pe_index", lambda: 52)
    monkeypatch.setattr(validation.time, "sleep", lambda _seconds: None)
    calls = []
    monkeypatch.setattr(
        validation,
        "_request_records",
        lambda *_args: calls.append(1) or [_axdata_record()],
    )

    first = _run_validation(
        output,
        source_meta={"tencent": {"ok": False, "status": "deferred"}},
    )
    second = _run_validation(output)
    third = _run_validation(output)

    assert first["probe"]["status"] == "skipped_project_counterpart_failed"
    assert second["status"] == "sampled"
    assert third["status"] == "already_recorded"
    assert len(calls) == 1


def test_tencent_value_comparison_is_skipped_when_quote_times_differ():
    record = _axdata_record()
    fields = _project_fields("20261009161500")

    result = validation._compare_tencent_record(record, fields, "2026-10-09")

    assert result["status"] == "not_same_dated_snapshot"
    assert result["field_comparisons"] == {}


@pytest.mark.parametrize("status_code", [403, 429])
def test_http_ban_status_blocks_the_axdata_family_on_later_days(tmp_path, monkeypatch, status_code):
    first_output = _capture_dir(tmp_path, "20261009")
    second_output = _capture_dir(tmp_path, "20261012")
    monkeypatch.setattr(validation, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(validation, "_static_queue_summary", lambda: {"status": "test"})
    monkeypatch.setattr(validation.time, "sleep", lambda _seconds: None)
    calls = []

    def forbidden_request(*_args):
        calls.append(1)
        error = RuntimeError(f"HTTP {status_code}")
        error.status_code = status_code
        raise error

    monkeypatch.setattr(validation, "_request_records", forbidden_request)
    first = _run_validation(first_output)
    second = _run_validation(second_output, data_date="20261012")

    assert first["status"] == "blocked_until_manual_review"
    assert second["probe"]["status"] == "blocked_until_manual_review"
    assert second["probe"]["request_count"] == 0
    assert len(calls) == 1


def test_two_empty_responses_block_without_same_run_retry(tmp_path, monkeypatch):
    first_output = _capture_dir(tmp_path, "20261009")
    second_output = _capture_dir(tmp_path, "20261012")
    third_output = _capture_dir(tmp_path, "20261013")
    monkeypatch.setattr(validation, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(validation, "_static_queue_summary", lambda: {"status": "test"})
    monkeypatch.setattr(validation.time, "sleep", lambda _seconds: None)
    calls = []

    def empty_request(*_args):
        calls.append(1)
        return []

    monkeypatch.setattr(validation, "_request_records", empty_request)
    first = _run_validation(first_output)
    second = _run_validation(second_output, data_date="20261012")
    third = _run_validation(third_output, data_date="20261013")

    assert first["status"] == "empty_or_unmatched_response"
    assert second["status"] == "blocked_until_manual_review"
    assert third["probe"]["status"] == "blocked_until_manual_review"
    assert third["probe"]["request_count"] == 0
    assert len(calls) == 2


def test_project_counterpart_rate_limit_blocks_probe_and_persists(tmp_path, monkeypatch):
    first_output = _capture_dir(tmp_path, "20261009")
    second_output = _capture_dir(tmp_path, "20261012")
    monkeypatch.setattr(validation, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(validation, "_static_queue_summary", lambda: {"status": "test"})
    calls = []
    monkeypatch.setattr(
        validation,
        "_request_records",
        lambda *_args: calls.append(1) or [_axdata_record()],
    )

    first = _run_validation(
        first_output,
        source_meta={"tencent": {"ok": False, "status": "partial", "error_sample": "HTTP 429"}},
    )
    second = _run_validation(second_output, data_date="20261012")

    assert first["status"] == "blocked_until_manual_review"
    assert first["probe"]["status"] == "blocked_by_project_counterpart"
    assert second["probe"]["status"] == "blocked_until_manual_review"
    assert calls == []


def test_passive_shortline_compare_requires_matching_source_dates(tmp_path):
    output = tmp_path / "20261009"
    output.mkdir()
    axdata = {"stocks": {"600519": {"data": {"stats_date": "20261009", "x": 1, "y": None}}}}
    eltdx = {"stocks": {"600519": {"shortline": {"stats_date": "2026-10-09", "x": 1.0, "y": None}}}}
    (output / "raw_axdata.json").write_text(json.dumps(axdata), encoding="utf-8")
    (output / "raw_eltdx.json").write_text(json.dumps(eltdx), encoding="utf-8")

    result = validation._shortline_passive_evidence(output, "2026-10-09")

    assert result["status"] == "compared"
    assert result["paired_stocks"] == 1
    assert result["field_comparisons"]["x"]["equal"] == 1
    assert result["field_comparisons"]["y"]["both_null"] == 1
    assert result["requests_added"] == 0


def test_passive_kph_kpl_compare_uses_explicit_trade_dates_and_confirmed_mappings(tmp_path):
    output = tmp_path / "20261009"
    output.mkdir()
    kph = {
        "trade_date": "2026-10-09",
        "stocks": {
            "600519": {
                "limit_time": 1791530000,
                "seal_amount": 1.0,
                "seal_money": 2.0,
                "net_inflow": 3.0,
                "turnover": 4.0,
                "turnover_rate": 0.5,
            }
        },
    }
    kpl = {
        "trade_date": "2026-10-09",
        "stocks": {
            "600519": {
                "zt_time": 1791530000,
                "max_seal": 1.0,
                "seal_amount": 2.0,
                "main_inflow": 3.0,
                "amount": 4.0,
                "turnover_real": 0.5,
            }
        },
    }
    (output / "raw_kph.json").write_text(json.dumps(kph), encoding="utf-8")
    (output / "raw_kpl.json").write_text(json.dumps(kpl), encoding="utf-8")

    result = validation._kph_kpl_passive_evidence(output, "2026-10-09")

    assert result["status"] == "compared"
    assert result["paired_stocks"] == 1
    assert all(counts["equal"] == 1 for counts in result["field_comparisons"].values())


def test_daily_lock_reclaims_stale_file_and_rejects_a_live_lock(tmp_path, monkeypatch):
    monkeypatch.setattr(validation, "STATE_PATH", tmp_path / "state.json")
    stale_lock = tmp_path / "axdata_daily_validation_20261009.lock"
    stale_lock.write_text("pid=0\nstarted=0\n", encoding="ascii")
    stale_time = time.time() - 3601
    os.utime(stale_lock, (stale_time, stale_time))

    acquired = validation._create_daily_lock("2026-10-09")

    assert acquired == stale_lock
    assert "pid=" in stale_lock.read_text(encoding="ascii")
    assert validation._create_daily_lock("2026-10-09") is None
    validation._remove_daily_lock(acquired)
    assert validation._create_daily_lock("2026-10-09") == stale_lock


def test_confirmed_tencent_endpoint_is_suppressed_until_periodic_recheck(tmp_path, monkeypatch):
    codes = ["600519", "000001", "601138"]
    dates = ["20261009", "20261012", "20261013"]
    outputs = [_capture_dir(tmp_path, data_date, codes) for data_date in dates]
    monkeypatch.setattr(validation, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(validation, "_static_queue_summary", lambda: {"status": "test"})
    monkeypatch.setattr(validation, "_dynamic_pe_index", lambda: 52)
    monkeypatch.setattr(validation.time, "sleep", lambda _seconds: None)
    calls = []

    def fake_request(interface, params):
        code = params["code"][0].split(".")[0]
        calls.append((interface, code))
        return [_axdata_record(f"{dates[len(calls) - 1]}161459", code)]

    monkeypatch.setattr(validation, "_request_records", fake_request)
    pool = [{"code": code} for code in codes]
    results = [
        _run_validation(output, data_date=data_date, pool=pool)
        for output, data_date in zip(outputs, dates)
    ]

    identity = results[-1]["probe"]["source_identity"]
    assert identity["status"] == "partially_redundant"
    assert identity["matched_data_dates"] == 3
    assert identity["matched_symbols"] == 3
    assert identity["semantic_unresolved_fields"] == ["pe_dynamic"]
    assert len(calls) == 3

    next_date = "20261014"
    next_output = _capture_dir(tmp_path, next_date, codes)
    skipped = _run_validation(next_output, data_date=next_date, pool=pool)
    assert skipped["probe"]["status"] == "endpoint_redundant_until_scheduled_recheck"
    assert skipped["probe"]["request_count"] == 0
    assert skipped["probe"]["source_identity"]["next_recheck_in_data_dates"] == 19
    assert len(calls) == 3


def test_periodic_identity_recheck_requires_three_new_exact_samples(tmp_path, monkeypatch):
    codes = ["600519", "000001", "601138"]
    monkeypatch.setattr(validation, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(validation, "_static_queue_summary", lambda: {"status": "test"})
    monkeypatch.setattr(validation, "_dynamic_pe_index", lambda: 52)
    monkeypatch.setattr(validation, "IDENTITY_RECHECK_DATA_DATES", 2)
    monkeypatch.setattr(validation.time, "sleep", lambda _seconds: None)
    pool = [{"code": code} for code in codes]
    calls = []

    def fake_request(interface, params):
        code = params["code"][0].split(".")[0]
        calls.append(code)
        data_date = current_date[0]
        return [_axdata_record(f"{data_date}161459", code)]

    monkeypatch.setattr(validation, "_request_records", fake_request)
    current_date = [""]
    for data_date in ("20261009", "20261012", "20261013"):
        current_date[0] = data_date
        _run_validation(_capture_dir(tmp_path, data_date, codes), data_date=data_date, pool=pool)

    current_date[0] = "20261014"
    first_wait = _run_validation(
        _capture_dir(tmp_path, "20261014", codes), data_date="20261014", pool=pool
    )
    assert first_wait["probe"]["status"] == "endpoint_redundant_until_scheduled_recheck"

    current_date[0] = "20261015"
    first_recheck = _run_validation(
        _capture_dir(tmp_path, "20261015", codes), data_date="20261015", pool=pool
    )
    assert first_recheck["probe"]["source_identity"]["status"] == "rechecking"
    assert first_recheck["probe"]["source_identity"]["recheck_samples_collected"] == 1

    current_date[0] = "20261016"
    second_recheck = _run_validation(
        _capture_dir(tmp_path, "20261016", codes), data_date="20261016", pool=pool
    )
    assert second_recheck["probe"]["source_identity"]["status"] == "rechecking"

    current_date[0] = "20261019"
    final_recheck = _run_validation(
        _capture_dir(tmp_path, "20261019", codes), data_date="20261019", pool=pool
    )
    assert final_recheck["probe"]["source_identity"]["status"] == "partially_redundant"
    assert set(final_recheck["probe"]["source_identity"]["evidence_dates"]) == {
        "2026-10-15",
        "2026-10-16",
        "2026-10-19",
    }
    assert len(calls) == 6


def test_identity_mismatch_reopens_daily_sampling(tmp_path, monkeypatch):
    codes = ["600519", "000001", "601138"]
    monkeypatch.setattr(validation, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(validation, "_static_queue_summary", lambda: {"status": "test"})
    monkeypatch.setattr(validation, "_dynamic_pe_index", lambda: 52)
    monkeypatch.setattr(validation, "IDENTITY_RECHECK_DATA_DATES", 1)
    monkeypatch.setattr(validation.time, "sleep", lambda _seconds: None)
    pool = [{"code": code} for code in codes]
    calls = []
    current_date = [""]
    mismatch = [False]

    def fake_request(interface, params):
        code = params["code"][0].split(".")[0]
        calls.append(code)
        record = _axdata_record(f"{current_date[0]}161459", code)
        if mismatch[0]:
            record["last_price"] = 9999.0
        return [record]

    monkeypatch.setattr(validation, "_request_records", fake_request)
    for data_date in ("20261009", "20261012", "20261013"):
        current_date[0] = data_date
        _run_validation(_capture_dir(tmp_path, data_date, codes), data_date=data_date, pool=pool)

    current_date[0] = "20261014"
    _run_validation(_capture_dir(tmp_path, "20261014", codes), data_date="20261014", pool=pool)
    current_date[0] = "20261015"
    mismatch[0] = True
    reopened = _run_validation(
        _capture_dir(tmp_path, "20261015", codes), data_date="20261015", pool=pool
    )
    assert reopened["probe"]["source_identity"]["status"] == "observing"
    assert reopened["probe"]["source_identity"]["reason"] == "value_mismatch_reopened"
    assert reopened["probe"]["source_identity"]["last_mismatch"]["fields"] == ["last_price"]

    current_date[0] = "20261016"
    mismatch[0] = False
    resumed = _run_validation(
        _capture_dir(tmp_path, "20261016", codes), data_date="20261016", pool=pool
    )
    assert resumed["probe"]["status"] == "sampled"
    assert len(calls) == 6


def test_unreadable_state_blocks_probe_until_manual_review(tmp_path, monkeypatch):
    output = _capture_dir(tmp_path)
    state_path = tmp_path / "state.json"
    state_path.write_text("{invalid json", encoding="utf-8")
    monkeypatch.setattr(validation, "STATE_PATH", state_path)
    monkeypatch.setattr(validation, "_static_queue_summary", lambda: {"status": "test"})
    calls = []
    monkeypatch.setattr(
        validation,
        "_request_records",
        lambda *_args: calls.append(1) or [_axdata_record()],
    )

    result = _run_validation(output)

    assert result["status"] == "blocked_until_manual_review"
    assert result["probe"]["status"] == "state_unreadable_until_manual_review"
    assert result["probe"]["source_identity"]["status"] == "state_unreadable_manual_review_required"
    assert calls == []


def test_identity_contract_change_reopens_daily_probe(tmp_path, monkeypatch):
    codes = ["600519", "000001", "601138"]
    monkeypatch.setattr(validation, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(validation, "_static_queue_summary", lambda: {"status": "test"})
    monkeypatch.setattr(validation, "_dynamic_pe_index", lambda: 52)
    monkeypatch.setattr(validation.time, "sleep", lambda _seconds: None)
    pool = [{"code": code} for code in codes]
    current_date = [""]
    calls = []

    def fake_request(interface, params):
        code = params["code"][0].split(".")[0]
        calls.append(code)
        return [_axdata_record(f"{current_date[0]}161459", code)]

    monkeypatch.setattr(validation, "_request_records", fake_request)
    for data_date in ("20261009", "20261012", "20261013"):
        current_date[0] = data_date
        result = _run_validation(
            _capture_dir(tmp_path, data_date, codes), data_date=data_date, pool=pool
        )
    assert result["probe"]["source_identity"]["status"] == "partially_redundant"

    monkeypatch.setattr(validation, "_dynamic_pe_index", lambda: 53)
    current_date[0] = "20261014"
    reopened = _run_validation(
        _capture_dir(tmp_path, "20261014", codes), data_date="20261014", pool=pool
    )

    assert reopened["probe"]["status"] == "sampled"
    assert reopened["probe"]["source_identity"]["status"] == "observing"
    assert reopened["probe"]["source_identity"]["reason"] == "contract_changed_reopened"
    assert reopened["probe"]["source_identity"]["matched_data_dates"] == 1
    assert len(calls) == 4


def test_response_schema_change_reopens_daily_probe(tmp_path, monkeypatch):
    codes = ["600519", "000001", "601138"]
    monkeypatch.setattr(validation, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(validation, "_static_queue_summary", lambda: {"status": "test"})
    monkeypatch.setattr(validation, "_dynamic_pe_index", lambda: 52)
    monkeypatch.setattr(validation, "IDENTITY_RECHECK_DATA_DATES", 1)
    monkeypatch.setattr(validation.time, "sleep", lambda _seconds: None)
    pool = [{"code": code} for code in codes]
    current_date = [""]
    calls = []

    def fake_request(interface, params):
        code = params["code"][0].split(".")[0]
        calls.append(code)
        record = _axdata_record(f"{current_date[0]}161459", code)
        if current_date[0] == "20261014":
            record["new_field"] = 1
        return [record]

    monkeypatch.setattr(validation, "_request_records", fake_request)
    for data_date in ("20261009", "20261012", "20261013"):
        current_date[0] = data_date
        _run_validation(_capture_dir(tmp_path, data_date, codes), data_date=data_date, pool=pool)

    current_date[0] = "20261014"
    _run_validation(_capture_dir(tmp_path, "20261014", codes), data_date="20261014", pool=pool)
    current_date[0] = "20261015"
    reopened = _run_validation(
        _capture_dir(tmp_path, "20261015", codes), data_date="20261015", pool=pool
    )

    assert reopened["probe"]["source_identity"]["status"] == "observing"
    assert reopened["probe"]["source_identity"]["reason"] == "response_schema_changed_reopened"
    assert len(calls) == 5

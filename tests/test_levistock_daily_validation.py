import json

import pytest

from scripts.levistock_daily_validation import run_levistock_daily_validation

TRADE_DATE = "2026-10-09"


def _write_raw(out_dir, payload):
    (out_dir / "raw_market_sources.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def _run(out_dir, **overrides):
    arguments = {
        "out_dir": out_dir,
        "data_date": "20261009",
        "latest_completed_trade_date": "2026-10-09",
        "data_date_domain": "trading",
        "market_phase": "closed",
        "only": "",
        "source_meta": {"market_sources": {"status": "ok"}},
    }
    arguments.update(overrides)
    return run_levistock_daily_validation(**arguments)


def test_daily_validation_reuses_raw_capture_and_records_explicit_dates(tmp_path):
    _write_raw(
        tmp_path,
        {
            "cls_market_emotion": {"date": TRADE_DATE, "emotion_index": 0},
            "kph_limit_ladder": [{"trade_date": TRADE_DATE, "code": "600000", "limit_count": 2}],
            "__source_meta__": {"kph_limit_ladder": {"requested_trade_date": TRADE_DATE}},
        },
    )

    result = _run(tmp_path)

    assert result["status"] == "observed"
    assert result["network_requests_added"] == 0
    assert result["methods"]["cls_market_emotion"]["date_status"] == "explicit_match"
    assert result["methods"]["kph_limit_ladder"]["date_status"] == "explicit_match"
    assert result["methods"]["kph_limit_ladder"]["eligible_for_date_comparison"] is True
    assert result["methods"]["kph_limit_ladder"]["sample_count"] == 1
    saved = json.loads((tmp_path / "levistock_validation.json").read_text(encoding="utf-8"))
    assert saved["network_requests_added"] == 0
    assert saved["data_date"] == TRADE_DATE


def test_request_parameter_is_not_misreported_as_response_date(tmp_path):
    _write_raw(
        tmp_path,
        {
            "cls_market_emotion": {"emotion_index": 0},
            "kph_limit_ladder": [{"code": "600000", "limit_count": 2}],
            "__source_meta__": {"kph_limit_ladder": {"requested_trade_date": TRADE_DATE}},
        },
    )

    result = _run(tmp_path)
    kph = result["methods"]["kph_limit_ladder"]

    assert kph["date_status"] == "request_parameter_match"
    assert kph["eligible_for_date_comparison"] is False
    assert kph["eligible_for_request_aligned_comparison"] is True
    assert result["methods"]["cls_market_emotion"]["date_status"] == "not_exposed"


def test_daily_validation_flags_response_date_mismatch(tmp_path):
    _write_raw(
        tmp_path,
        {
            "cls_market_emotion": {"as_of_date": "2026-10-08", "emotion_index": 1},
            "kph_limit_ladder": {"__error__": "empty response from Levistock adapter"},
        },
    )

    result = _run(tmp_path)

    assert result["status"] == "partial"
    assert result["methods"]["cls_market_emotion"]["date_status"] == "explicit_mismatch"
    assert result["methods"]["cls_market_emotion"]["eligible_for_date_comparison"] is False
    assert result["methods"]["kph_limit_ladder"]["status"] == "error"


def test_daily_validation_flags_request_and_response_date_conflict(tmp_path):
    _write_raw(
        tmp_path,
        {
            "cls_market_emotion": {"emotion_index": 1},
            "kph_limit_ladder": [{"trade_date": TRADE_DATE, "code": "600000"}],
            "__source_meta__": {"kph_limit_ladder": {"requested_trade_date": "2026-10-08"}},
        },
    )

    result = _run(tmp_path)
    kph = result["methods"]["kph_limit_ladder"]

    assert kph["date_status"] == "request_response_mismatch"
    assert kph["eligible_for_date_comparison"] is False


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"only": "push2"}, "market_sources_not_selected"),
        ({"data_date_domain": "calendar"}, "capture_date_is_not_a_trading_day"),
        ({"market_phase": "intraday"}, "capture_is_not_a_closed_market_snapshot"),
        (
            {"data_date": "20261008", "latest_completed_trade_date": "20261009"},
            "capture_is_not_the_latest_completed_trading_day",
        ),
    ],
)
def test_daily_validation_gates_non_comparable_captures(tmp_path, overrides, reason):
    _write_raw(tmp_path, {"cls_market_emotion": {"emotion_index": 1}})

    result = _run(tmp_path, **overrides)

    assert result["status"] == "not_eligible"
    assert result["eligibility_reason"] == reason
    assert result["network_requests_added"] == 0


def test_missing_raw_file_is_reported_even_for_ineligible_capture(tmp_path):
    result = _run(tmp_path, market_phase="intraday")

    assert result["status"] == "failed_open"
    assert result["raw_error"] == "capture_file_missing"


def test_daily_validation_includes_rotating_candidate_evidence(tmp_path):
    _write_raw(
        tmp_path,
        {
            "cls_market_emotion": {"emotion_index": 1},
            "kph_limit_ladder": [{"trade_date": TRADE_DATE, "code": "600000"}],
            "__source_meta__": {
                "levistock_daily_candidate": {
                    "status": "observed",
                    "candidate_id": "kph_market_emotion",
                    "adapter": "levistock.market.market_emotion_kph.market_emotion_kph",
                    "provider_family": "kph",
                    "request_count": 1,
                }
            },
        },
    )
    (tmp_path / "levistock_candidate_raw.json").write_text(
        json.dumps(
            {
                "data_date": TRADE_DATE,
                "probe": {
                    "status": "observed",
                    "candidate_id": "kph_market_emotion",
                    "adapter": "levistock.market.market_emotion_kph.market_emotion_kph",
                    "provider_family": "kph",
                    "request_count": 1,
                    "package_version": "0.1.7",
                    "expected_package_version": "0.1.8",
                    "version_matches_requirement": False,
                    "request_params": {"date": TRADE_DATE},
                },
                "payload": {"zt": 0, "dt": 0, "rise_num": 3120},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = _run(tmp_path)

    candidate = result["candidate_probe"]
    assert candidate["status"] == "observed"
    assert candidate["candidate_id"] == "kph_market_emotion"
    assert candidate["request_count"] == 1
    assert candidate["fields"] == ["dt", "rise_num", "zt"]
    assert candidate["date_status"] == "request_parameter_match"
    assert candidate["eligible_for_request_aligned_comparison"] is True
    assert candidate["version_matches_requirement"] is False
    assert result["capture_probe_request_count"] == 1
    assert result["network_requests_added"] == 0


def test_daily_validation_uses_candidate_metadata_when_raw_sidecar_is_missing(tmp_path):
    _write_raw(
        tmp_path,
        {
            "cls_market_emotion": {"emotion_index": 1},
            "kph_limit_ladder": [{"trade_date": TRADE_DATE, "code": "600000"}],
        },
    )

    result = _run(
        tmp_path,
        candidate_probe_meta={
            "status": "already_recorded",
            "reason": "attempt_already_made_for_data_date",
            "candidate_id": "cls_sector_industry",
            "provider_family": "cls",
            "request_count": 0,
        },
    )

    candidate = result["candidate_probe"]
    assert candidate["status"] == "already_recorded"
    assert candidate["reason"] == "attempt_already_made_for_data_date"
    assert candidate["candidate_id"] == "cls_sector_industry"
    assert candidate["request_count"] == 0


def test_daily_validation_sanitizes_malformed_candidate_metadata(tmp_path):
    _write_raw(
        tmp_path,
        {
            "cls_market_emotion": {"date": TRADE_DATE, "emotion_index": 1},
            "kph_limit_ladder": [{"trade_date": TRADE_DATE, "code": "600000"}],
        },
    )
    (tmp_path / "levistock_candidate_raw.json").write_text(
        json.dumps(
            {
                "data_date": TRADE_DATE,
                "probe": {
                    "status": "observed",
                    "request_count": {"invalid": 1},
                    "request_params": [],
                },
                "payload": {"rise_num": 3000},
            }
        ),
        encoding="utf-8",
    )

    result = _run(tmp_path)

    candidate = result["candidate_probe"]
    assert candidate["request_count"] == 0
    assert candidate["request_params"] == {}

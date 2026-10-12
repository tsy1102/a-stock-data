import json
from datetime import datetime

import pytest

import scripts.levistock_daily_probe as probe


def _context(**overrides):
    values = {
        "out_dir": None,
        "data_date": "2026-10-09",
        "latest_completed_trade_date": "2026-10-09",
        "data_date_domain": "trading",
        "market_phase": "closed",
        "now": datetime(2026, 10, 9, 15, 30),
        "only": "",
        "market_data": {
            "cls_market_emotion": {"emotion_index": 0},
            "kph_limit_ladder": [{"code": "600000", "limit_count": 1}],
        },
        "pool": [{"code": "600000"}],
    }
    values.update(overrides)
    return values


def _configure(tmp_path, monkeypatch):
    state_path = tmp_path / "state.json"
    monkeypatch.setattr(probe, "LOCK_DIR", tmp_path / "locks")
    monkeypatch.setattr(probe.metadata, "version", lambda _name: "0.1.8")
    monkeypatch.setattr(probe, "_provider_is_blocked", lambda _family: False)
    monkeypatch.setattr(probe, "_mark_provider_block", lambda _family, _error: True)
    return state_path


def test_daily_candidate_records_one_numeric_sample_and_package_version(tmp_path, monkeypatch):
    state_path = _configure(tmp_path, monkeypatch)
    calls = []

    def requester(candidate_id, target_date, stock_code, expected_family):
        calls.append((candidate_id, target_date, stock_code, expected_family))
        return (
            [{"secu_name": "通信", "change": 0.0, "main_fund_diff": 0}],
            {},
            probe.CANDIDATES[0]["adapter"],
        )

    result = probe.run_levistock_daily_probe(
        **_context(out_dir=tmp_path),
        state_path=state_path,
        candidate_requester=requester,
    )

    assert result["status"] == "observed"
    assert result["candidate_id"] == "cls_sector_industry"
    assert result["request_count"] == 1
    assert result["package_version"] == "0.1.8"
    assert result["version_matches_requirement"] is True
    assert calls == [("cls_sector_industry", "2026-10-09", None, "cls")]
    saved = json.loads((tmp_path / "levistock_candidate_raw.json").read_text(encoding="utf-8"))
    assert saved["data_date"] == "2026-10-09"
    assert saved["payload"][0]["main_fund_diff"] == 0


def test_package_version_mismatch_skips_candidate_without_consuming_daily_slot(
    tmp_path, monkeypatch
):
    state_path = _configure(tmp_path, monkeypatch)
    monkeypatch.setattr(probe.metadata, "version", lambda _name: "0.1.7")
    calls = []

    result = probe.run_levistock_daily_probe(
        **_context(out_dir=tmp_path),
        state_path=state_path,
        candidate_requester=lambda *_args: calls.append("called"),
    )

    assert result["status"] == "skipped"
    assert result["reason"] == "installed_package_version_does_not_match_requirement"
    assert result["version_matches_requirement"] is False
    assert result["request_count"] == 0
    assert calls == []
    assert not state_path.exists()
    assert not (tmp_path / "levistock_candidate_raw.json").exists()


def test_daily_candidate_is_idempotent_for_same_data_date(tmp_path, monkeypatch):
    state_path = _configure(tmp_path, monkeypatch)
    calls = []
    values = _context(out_dir=tmp_path)
    options = {
        "state_path": state_path,
        "candidate_requester": lambda *_args: calls.append("called")
        or ([{"change": 1}], {}, probe.CANDIDATES[0]["adapter"]),
    }

    first = probe.run_levistock_daily_probe(**values, **options)
    second = probe.run_levistock_daily_probe(**values, **options)

    assert first["status"] == "observed"
    assert second["status"] == "already_recorded"
    assert second["request_count"] == 0
    assert calls == ["called"]


def test_daily_candidate_skips_intraday_capture_without_requests(tmp_path, monkeypatch):
    state_path = _configure(tmp_path, monkeypatch)
    calls = []

    result = probe.run_levistock_daily_probe(
        **_context(out_dir=tmp_path, market_phase="intraday"),
        state_path=state_path,
        candidate_requester=lambda *_args: calls.append("called"),
    )

    assert result["status"] == "skipped"
    assert result["reason"] == "capture_is_not_a_closed_market_snapshot"
    assert result["request_count"] == 0
    assert calls == []
    assert not (tmp_path / "levistock_candidate_raw.json").exists()


@pytest.mark.parametrize(
    "run_at",
    [datetime(2026, 10, 10, 8, 30), datetime(2026, 10, 12, 8, 30)],
    ids=["holiday", "pre_open"],
)
def test_daily_candidate_allows_previous_trade_date_on_holiday_or_before_open(
    tmp_path, monkeypatch, run_at
):
    state_path = _configure(tmp_path, monkeypatch)
    calls = []

    def requester(candidate_id, target_date, stock_code, expected_family):
        calls.append((candidate_id, target_date, stock_code, expected_family))
        return (
            [{"secu_name": "通信", "change": 0.0, "main_fund_diff": 0}],
            {},
            probe.CANDIDATES[0]["adapter"],
        )

    result = probe.run_levistock_daily_probe(
        **_context(out_dir=tmp_path, now=run_at),
        state_path=state_path,
        candidate_requester=requester,
    )

    assert result["status"] == "observed"
    assert result["request_count"] == 1
    assert calls == [("cls_sector_industry", "2026-10-09", None, "cls")]
    saved = json.loads((tmp_path / "levistock_candidate_raw.json").read_text(encoding="utf-8"))
    assert saved["data_date"] == "2026-10-09"
    assert saved["evaluated_at"].startswith(run_at.isoformat(timespec="seconds"))
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["last_attempted_data_date"] == "2026-10-09"


def test_daily_candidate_skips_missing_trade_date_without_consuming_slot(tmp_path, monkeypatch):
    state_path = _configure(tmp_path, monkeypatch)
    calls = []

    result = probe.run_levistock_daily_probe(
        **_context(out_dir=tmp_path, data_date=None),
        state_path=state_path,
        candidate_requester=lambda *_args: calls.append("called"),
    )

    assert result["status"] == "skipped"
    assert result["request_count"] == 0
    assert calls == []
    assert not state_path.exists()


def test_counterpart_403_blocks_only_that_provider_family(tmp_path, monkeypatch):
    state_path = _configure(tmp_path, monkeypatch)
    calls = []
    market_data = {
        "cls_market_emotion": {"__error__": "HTTP 403 forbidden"},
        "kph_limit_ladder": [{"code": "600000", "limit_count": 1}],
    }

    def requester(candidate_id, target_date, stock_code, expected_family):
        calls.append((candidate_id, target_date, stock_code, expected_family))
        candidate = next(item for item in probe.CANDIDATES if item["id"] == candidate_id)
        return {"zt": 0, "dt": 0}, {"date": target_date}, candidate["adapter"]

    result = probe.run_levistock_daily_probe(
        **_context(out_dir=tmp_path, market_data=market_data),
        state_path=state_path,
        candidate_requester=requester,
    )

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert result["status"] == "observed"
    assert result["candidate_id"] == "kph_market_emotion"
    assert result["request_params"] == {"date": "2026-10-09"}
    assert state["blocked_families"] == ["cls"]
    assert calls == [("kph_market_emotion", "2026-10-09", None, "kph")]


def test_candidate_request_429_persistently_blocks_provider_family(tmp_path, monkeypatch):
    state_path = _configure(tmp_path, monkeypatch)

    def raise_429(*_args):
        error = RuntimeError("429 Too Many Requests")
        error.request_started = True
        raise error

    result = probe.run_levistock_daily_probe(
        **_context(out_dir=tmp_path),
        state_path=state_path,
        candidate_requester=raise_429,
    )

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert result["status"] == "blocked"
    assert result["reason"] == "provider_rate_limited"
    assert result["request_count"] == 1
    assert state["blocked_families"] == ["cls"]


def test_zero_request_counterpart_skip_can_retry_same_trade_date(tmp_path, monkeypatch):
    state_path = _configure(tmp_path, monkeypatch)
    calls = []
    values = _context(
        out_dir=tmp_path,
        market_data={
            "cls_market_emotion": {"__error__": "temporary counterpart failure"},
            "kph_limit_ladder": [],
        },
    )
    first = probe.run_levistock_daily_probe(
        **values,
        state_path=state_path,
        candidate_requester=lambda *_args: calls.append("called"),
    )

    state_after_skip = json.loads(state_path.read_text(encoding="utf-8"))
    values["market_data"] = _context()["market_data"]
    second = probe.run_levistock_daily_probe(
        **values,
        state_path=state_path,
        candidate_requester=lambda *_args: calls.append("called")
        or ([{"change": 0}], {}, probe.CANDIDATES[0]["adapter"]),
    )
    third = probe.run_levistock_daily_probe(
        **values,
        state_path=state_path,
        candidate_requester=lambda *_args: calls.append("duplicate"),
    )

    assert first["status"] == "skipped"
    assert first["request_count"] == 0
    assert state_after_skip["last_outcome"] == "no_eligible_candidate"
    assert state_after_skip["last_evaluated_data_date"] == "2026-10-09"
    assert "last_attempted_data_date" not in state_after_skip
    assert second["status"] == "observed"
    assert third["status"] == "already_recorded"
    assert calls == ["called"]

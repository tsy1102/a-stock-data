import json

from scripts import axdata_daily_validation as validation


def _write_snapshot(
    output_dir,
    data_date,
    *,
    shortline_mismatch=False,
    kph_extra=False,
    shortline_schema_change=False,
):
    codes = [f"{index:06d}" for index in range(1, 21)]
    axdata_stocks = {}
    eltdx_stocks = {}
    kph_stocks = {}
    kpl_stocks = {}
    for code_index, code in enumerate(codes, start=1):
        shortline = {"stats_date": data_date}
        reference_shortline = {"stats_date": data_date}
        for field_index in range(1, 7):
            key = f"indicator_{field_index}"
            value = code_index * 10 + field_index
            shortline[key] = value
            reference_shortline[key] = value
        if shortline_mismatch and code_index == len(codes):
            reference_shortline["indicator_1"] += 1
        if shortline_schema_change:
            shortline["new_candidate"] = code_index
            reference_shortline["new_candidate"] = code_index
        axdata_stocks[code] = {"data": shortline}
        eltdx_stocks[code] = {"shortline": reference_shortline}

        kph_row = {
            "limit_time": code_index,
            "seal_amount": code_index * 2,
            "seal_money": code_index * 3,
            "net_inflow": code_index * 4,
            "turnover": code_index * 5,
            "turnover_rate": code_index * 6,
        }
        if kph_extra:
            kph_row["unmapped_candidate"] = code_index * 7
        kph_stocks[code] = kph_row
        kpl_stocks[code] = {
            "zt_time": kph_row["limit_time"],
            "max_seal": kph_row["seal_amount"],
            "seal_amount": kph_row["seal_money"],
            "main_inflow": kph_row["net_inflow"],
            "amount": kph_row["turnover"],
            "turnover_real": kph_row["turnover_rate"],
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    documents = {
        "raw_axdata.json": {"stocks": axdata_stocks},
        "raw_eltdx.json": {"stocks": eltdx_stocks},
        "raw_kph.json": {"trade_date": data_date, "stocks": kph_stocks},
        "raw_kpl.json": {"trade_date": data_date, "stocks": kpl_stocks},
    }
    for filename, document in documents.items():
        (output_dir / filename).write_text(json.dumps(document), encoding="utf-8")
    return {
        source: {"ok": True, "status": "ok"}
        for source in ("axdata", "eltdx", "kph", "kpl")
    }


def _confirm_both_routes(tmp_path, monkeypatch):
    state_path = tmp_path / ".tmp" / "axdata_state.json"
    monkeypatch.setattr(validation, "STATE_PATH", state_path)
    dates = ["2026-10-08", "2026-10-09", "2026-10-12"]
    for data_date in dates:
        output_dir = tmp_path / data_date.replace("-", "")
        source_meta = _write_snapshot(output_dir, data_date)
        validation.update_axdata_capture_identities(
            out_dir=output_dir,
            data_date=data_date,
            source_meta=source_meta,
        )
    return state_path, dates


def test_proven_axdata_capture_routes_are_skipped_and_excluded_from_routine_collisions(
    tmp_path, monkeypatch
):
    _confirm_both_routes(tmp_path, monkeypatch)

    plan = validation.get_axdata_capture_identity_plan("2026-10-13")
    assert plan["endpoints"]["stock_shortline_indicators_tdx"]["action"] == "skip"
    assert plan["endpoints"]["kph_limit_up_history"]["action"] == "skip"
    assert validation.get_axdata_collision_suppressions().keys() == {"axdata", "kph"}


def test_kph_unknown_fields_keep_the_route_active(tmp_path, monkeypatch):
    state_path = tmp_path / ".tmp" / "axdata_state.json"
    monkeypatch.setattr(validation, "STATE_PATH", state_path)
    dates = ["2026-10-08", "2026-10-09", "2026-10-12"]
    for data_date in dates:
        output_dir = tmp_path / data_date.replace("-", "")
        source_meta = _write_snapshot(output_dir, data_date, kph_extra=True)
        summaries = validation.update_axdata_capture_identities(
            out_dir=output_dir,
            data_date=data_date,
            source_meta=source_meta,
        )

    assert summaries["stock_shortline_indicators_tdx"]["status"] == "operationally_redundant"
    assert summaries["kph_limit_up_history"]["status"] == "observing"
    assert "unmapped_candidate" in summaries["kph_limit_up_history"]["unresolved_fields"]
    plan = validation.get_axdata_capture_identity_plan("2026-10-13")
    assert plan["endpoints"]["stock_shortline_indicators_tdx"]["action"] == "skip"
    assert plan["endpoints"]["kph_limit_up_history"]["action"] == "collect"
    assert validation.get_axdata_collision_suppressions().keys() == {"axdata"}


def test_scheduled_full_route_recheck_reopens_on_value_mismatch(tmp_path, monkeypatch):
    state_path, _ = _confirm_both_routes(tmp_path, monkeypatch)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    for identity in state["capture_endpoint_identities"].values():
        identity["eligible_data_dates_since_probe"] = validation.CAPTURE_IDENTITY_RECHECK_DATES
    state_path.write_text(json.dumps(state), encoding="utf-8")

    plan = validation.get_axdata_capture_identity_plan("2026-10-13")
    assert all(item["action"] == "collect" for item in plan["endpoints"].values())
    assert all(item["identity"]["status"] == "rechecking" for item in plan["endpoints"].values())

    output_dir = tmp_path / "20261013"
    source_meta = _write_snapshot(output_dir, "2026-10-13", shortline_mismatch=True)
    summaries = validation.update_axdata_capture_identities(
        out_dir=output_dir,
        data_date="2026-10-13",
        source_meta=source_meta,
    )
    shortline = summaries["stock_shortline_indicators_tdx"]
    assert shortline["status"] == "observing"
    assert shortline["reason"] == "value_mismatch_reopened"
    assert "indicator_1" in shortline["last_mismatch"]["fields"]
    kph = summaries["kph_limit_up_history"]
    assert kph["status"] == "rechecking"
    assert kph["matched_data_dates"] == 1
    assert validation.get_axdata_collision_suppressions().keys() == {"kph"}


def test_scheduled_recheck_requires_three_new_exact_data_dates(tmp_path, monkeypatch):
    state_path, _ = _confirm_both_routes(tmp_path, monkeypatch)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    for identity in state["capture_endpoint_identities"].values():
        identity["eligible_data_dates_since_probe"] = validation.CAPTURE_IDENTITY_RECHECK_DATES
    state_path.write_text(json.dumps(state), encoding="utf-8")

    validation.get_axdata_capture_identity_plan("2026-10-13")
    summaries = None
    for data_date in ("2026-10-13", "2026-10-14", "2026-10-15"):
        output_dir = tmp_path / data_date.replace("-", "")
        source_meta = _write_snapshot(output_dir, data_date)
        summaries = validation.update_axdata_capture_identities(
            out_dir=output_dir,
            data_date=data_date,
            source_meta=source_meta,
        )
        shortline = summaries["stock_shortline_indicators_tdx"]
        if data_date != "2026-10-15":
            assert shortline["status"] == "rechecking"
            assert validation.get_axdata_collision_suppressions().keys() == {"axdata", "kph"}

    assert summaries is not None
    for interface_id in validation.CAPTURE_ENDPOINTS:
        identity = summaries[interface_id]
        assert identity["status"] == "operationally_redundant"
        assert identity["matched_data_dates"] == 3
        assert identity["evidence_dates"] == ["2026-10-13", "2026-10-14", "2026-10-15"]
        assert identity["minimum_matched_symbols"] == 20


def test_due_route_remains_suppressed_until_capture_plan_starts_recheck(tmp_path, monkeypatch):
    state_path, _ = _confirm_both_routes(tmp_path, monkeypatch)
    state = json.loads(state_path.read_text(encoding="utf-8"))
    for identity in state["capture_endpoint_identities"].values():
        identity["eligible_data_dates_since_probe"] = validation.CAPTURE_IDENTITY_RECHECK_DATES
    state_path.write_text(json.dumps(state), encoding="utf-8")

    assert validation.get_axdata_collision_suppressions().keys() == {"axdata", "kph"}
    plan = validation.get_axdata_capture_identity_plan("2026-10-13")
    assert all(item["identity"]["status"] == "rechecking" for item in plan["endpoints"].values())
    assert validation.get_axdata_collision_suppressions().keys() == {"axdata", "kph"}


def test_repeated_same_data_date_does_not_add_an_identity_sample(tmp_path, monkeypatch):
    state_path = tmp_path / ".tmp" / "axdata_state.json"
    monkeypatch.setattr(validation, "STATE_PATH", state_path)
    dates = ["2026-10-08", "2026-10-09"]
    for data_date in dates:
        output_dir = tmp_path / data_date.replace("-", "")
        source_meta = _write_snapshot(output_dir, data_date)
        validation.update_axdata_capture_identities(
            out_dir=output_dir,
            data_date=data_date,
            source_meta=source_meta,
        )
    summaries = validation.update_axdata_capture_identities(
        out_dir=tmp_path / "20261009",
        data_date="2026-10-09",
        source_meta=_write_snapshot(tmp_path / "20261009", "2026-10-09"),
    )
    state = json.loads(state_path.read_text(encoding="utf-8"))
    samples = state["capture_endpoint_identities"]["stock_shortline_indicators_tdx"]["samples"]
    assert len(samples) == 2
    assert summaries["stock_shortline_indicators_tdx"]["matched_data_dates"] == 2


def test_unreadable_identity_state_fails_closed_for_capture_and_open_for_collision(
    tmp_path, monkeypatch
):
    state_path = tmp_path / ".tmp" / "axdata_state.json"
    state_path.parent.mkdir(parents=True)
    state_path.write_text("{broken", encoding="utf-8")
    monkeypatch.setattr(validation, "STATE_PATH", state_path)

    plan = validation.get_axdata_capture_identity_plan("2026-10-13")
    assert plan["status"] == "blocked_until_manual_review"
    assert all(item["action"] == "skip" for item in plan["endpoints"].values())
    assert validation.get_axdata_collision_suppressions() == {}


def test_partial_capture_rate_limit_blocks_only_the_route_that_ran(tmp_path, monkeypatch):
    state_path = tmp_path / ".tmp" / "axdata_state.json"
    monkeypatch.setattr(validation, "STATE_PATH", state_path)

    summaries = validation.record_axdata_capture_rate_limits(
        data_date="2026-10-13",
        source_meta={"axdata": {"ok": False, "error_sample": "HTTP 429 Too Many Requests"}},
        collected_data={"axdata": {"stocks": {"000001": {"__error__": "HTTP 429"}}}},
        requested_sources={"axdata"},
    )

    assert summaries["stock_shortline_indicators_tdx"]["status"] == (
        "blocked_until_manual_review"
    )
    assert summaries["stock_shortline_indicators_tdx"]["reason"] == (
        "rate_limit_or_ban_observed"
    )
    assert summaries["kph_limit_up_history"]["status"] == "observing"
    plan = validation.get_axdata_capture_identity_plan("2026-10-14")
    assert plan["endpoints"]["stock_shortline_indicators_tdx"]["action"] == "skip"
    assert plan["endpoints"]["kph_limit_up_history"]["action"] == "collect"


def test_rate_limit_block_survives_contract_change_and_keeps_prior_collision_exit(
    tmp_path, monkeypatch
):
    state_path, _ = _confirm_both_routes(tmp_path, monkeypatch)
    summaries = validation.record_axdata_capture_rate_limits(
        data_date="2026-10-13",
        source_meta={"axdata": {"ok": False, "error_sample": "HTTP 429 Too Many Requests"}},
        collected_data={"axdata": {"stocks": {"000001": {"__error__": "HTTP 429"}}}},
        requested_sources={"axdata"},
    )

    assert summaries["stock_shortline_indicators_tdx"]["status"] == (
        "blocked_until_manual_review"
    )
    assert validation.get_axdata_collision_suppressions().keys() == {"axdata", "kph"}

    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["capture_endpoint_identities"]["stock_shortline_indicators_tdx"][
        "contract_fingerprint"
    ] = "stale-contract"
    state_path.write_text(json.dumps(state), encoding="utf-8")

    plan = validation.get_axdata_capture_identity_plan("2026-10-14")
    assert plan["endpoints"]["stock_shortline_indicators_tdx"]["action"] == "skip"
    assert plan["endpoints"]["stock_shortline_indicators_tdx"]["identity"]["status"] == (
        "blocked_until_manual_review"
    )
    output_dir = tmp_path / "20261014"
    source_meta = _write_snapshot(output_dir, "2026-10-14")
    summaries = validation.update_axdata_capture_identities(
        out_dir=output_dir,
        data_date="2026-10-14",
        source_meta={"axdata": source_meta["axdata"], "eltdx": source_meta["eltdx"]},
    )
    assert summaries["stock_shortline_indicators_tdx"]["status"] == (
        "blocked_until_manual_review"
    )
    assert validation.get_axdata_collision_suppressions().keys() == {"kph"}

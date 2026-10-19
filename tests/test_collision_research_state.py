import gzip
import json

from scripts import collision_research_state as research


def _report(report_date, left="zhb.full.amount", right="sina[9]", hit=1.0):
    return {
        "schema_version": 2,
        "date": report_date,
        "collision_mode": "exploratory",
        "trading_window": ["20261009"],
        "event_window": {"start": report_date, "end": report_date},
        "L1": [
            {
                "left": left,
                "right": right,
                "level": "L1-U",
                "ratio": 10000,
                "overall_hit": hit,
                "n_days": 3,
                "n_pairs": 60,
                "distinct_days": ["T:20261007", "T:20261008", "T:20261009"],
                "evidence_sources": ["sina", "tdx"],
            }
        ],
        "L4": [
            {
                "left": left,
                "right": right,
                "level": "L4",
                "overall_hit": hit,
                "n_days": 3,
                "n_pairs": 60,
                "exploratory": True,
            }
        ],
        "method_candidates": [
            {
                "left": left,
                "right": right,
                "sample_count": 60,
                "sample_dates": ["T:20261007", "T:20261008", "T:20261009"],
                "evidence_sources": ["sina", "tdx"],
                "methods": ["scale"],
            }
        ],
    }


def test_exploratory_candidates_persist_and_rerun_is_idempotent():
    report = _report("20261011")
    first, first_run_id, first_stats = research.update_state(
        research.empty_state(), report, "collision_research_20261011/exploratory/report.json"
    )
    second, second_run_id, second_stats = research.update_state(
        first, report, "collision_research_20261011/exploratory/report.json"
    )

    assert second_run_id == first_run_id
    assert first_stats["current_candidate_pairs"] == 1
    assert first_stats["new_candidate_pairs"] == 1
    assert second_stats["new_candidate_pairs"] == 0
    assert second_stats["previously_tracked_pairs"] == 0
    assert len(second["candidates"]) == 1
    candidate = next(iter(second["candidates"].values()))
    assert candidate["observation_count"] == 1
    assert candidate["latest_evidence"]["L1"][0]["distinct_days"] == [
        "T:20261007",
        "T:20261008",
        "T:20261009",
    ]
    assert candidate["latest_evidence"]["method_candidates"][0]["methods"] == ["scale"]


def test_later_report_inherits_prior_pair_history_even_if_orientation_changes():
    first, _run_id, _stats = research.update_state(
        research.empty_state(),
        _report("20261011"),
        "collision_research_20261011/exploratory/report.json",
    )
    later_report = _report("20261012", left="sina[9]", right="zhb.full.amount", hit=0.99)
    updated, current_run_id, stats = research.update_state(
        first, later_report, "collision_research_20261012/exploratory/report.json"
    )

    matched = research.annotate_report(later_report, updated, current_run_id)

    assert stats["new_candidate_pairs"] == 0
    assert stats["previously_tracked_pairs"] == 1
    assert matched == 1
    assert later_report["L1"][0]["research_history"]["prior_observation_count"] == 1
    candidate = next(iter(updated["candidates"].values()))
    assert candidate["observation_count"] == 2
    assert candidate["last_seen"] == "20261012"


def test_registered_l1_revalidation_is_not_added_as_an_actionable_research_candidate():
    first, _run_id, _stats = research.update_state(
        research.empty_state(),
        _report("20261011"),
        "collision_research_20261011/exploratory/report.json",
    )
    mapped_report = _report("20261012")
    mapped_report["L1"][0]["in_registry"] = True
    mapped_report["actionable_L1"] = []
    mapped_report["mapped_pair_revalidations"] = mapped_report["L1"]
    mapped_report["L4"] = []
    mapped_report["method_candidates"] = []

    updated, run_id, stats = research.update_state(
        first, mapped_report, "collision_research_20261012/exploratory/report.json"
    )
    matched = research.annotate_report(mapped_report, updated, run_id)

    assert stats["current_candidate_pairs"] == 0
    assert stats["previously_tracked_pairs"] == 0
    assert matched == 0
    assert "research_history" not in mapped_report["L1"][0]
    assert len(updated["candidates"]) == 1  # historical observation is preserved


def test_rerun_removing_a_pair_recomputes_retained_history_summary():
    first, _run_id, _stats = research.update_state(
        research.empty_state(),
        _report("20261011"),
        "collision_research_20261011/exploratory/report.json",
    )
    later_report = _report("20261012")
    with_later, later_run_id, _stats = research.update_state(
        first,
        later_report,
        "collision_research_20261012/exploratory/report.json",
    )
    assert later_run_id

    rerun = _report("20261012")
    rerun["L1"] = []
    rerun["L4"] = []
    rerun["method_candidates"] = []
    updated, rerun_id, stats = research.update_state(
        with_later,
        rerun,
        "collision_research_20261012/exploratory/report.json",
    )

    assert rerun_id == later_run_id
    assert stats["current_candidate_pairs"] == 0
    candidate = next(iter(updated["candidates"].values()))
    assert candidate["observation_count"] == 1
    assert candidate["first_seen"] == "20261011"
    assert candidate["last_seen"] == "20261011"
    assert candidate["latest_evidence"]["L1"][0]["overall_hit"] == 1.0


def test_out_of_order_report_keeps_latest_date_and_report_reference():
    latest_path = "collision_research_20261012/exploratory/latest.json"
    state, _run_id, _stats = research.update_state(
        research.empty_state(), _report("20261012", hit=0.99), latest_path
    )
    older_path = "collision_research_20261011/exploratory/older.json"
    state, _run_id, _stats = research.update_state(state, _report("20261011", hit=0.75), older_path)
    later_report = _report("20261013")

    matched = research.annotate_report(later_report, state, "new-current-run")

    assert matched == 1
    history = later_report["L1"][0]["research_history"]
    assert history["last_seen"] == "20261012"
    assert history["latest_report"] == latest_path
    candidate = next(iter(state["candidates"].values()))
    assert candidate["first_seen"] == "20261011"
    assert candidate["last_seen"] == "20261012"
    assert candidate["latest_evidence"]["L1"][0]["overall_hit"] == 0.99
    assert state["updated"] == "20261012"


def test_context_scope_is_a_distinct_research_run():
    report = _report("20261011")
    state, first_run_id, _stats = research.update_state(
        research.empty_state(), report, "collision_research_20261011/exploratory/report.json"
    )
    context_report = _report("20261011")
    context_report["include_context"] = True
    updated, context_run_id, stats = research.update_state(
        state,
        context_report,
        "collision_research_20261011/exploratory/report.json",
    )

    assert context_run_id != first_run_id
    assert stats["previously_tracked_pairs"] == 1
    assert updated["runs"][context_run_id]["include_context"] is True
    candidate = next(iter(updated["candidates"].values()))
    assert candidate["observation_count"] == 2


def test_research_state_gzip_round_trips_without_duplicate_latest_evidence(tmp_path):
    path = tmp_path / "collision_research_state.json.gz"
    state, _run_id, _stats = research.update_state(
        research.empty_state(),
        _report("20261011"),
        "collision_research_20261011/exploratory/report.json",
    )
    research.save_state(state, path)
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        persisted = json.load(handle)
    persisted_candidate = next(iter(persisted["candidates"].values()))
    assert persisted["schema_version"] == research.SCHEMA_VERSION
    assert "latest_evidence" not in persisted_candidate
    assert (
        persisted_candidate["observations"][0]["sections"]
        == state["candidates"][next(iter(state["candidates"]))]["latest_evidence"]
    )

    loaded, warnings, writable = research.load_state(path)

    assert warnings == []
    assert writable is True
    assert loaded == state

    invalid_path = tmp_path / "invalid_research_state.json"
    invalid_text = json.dumps({"schema_version": 99})
    invalid_path.write_text(invalid_text, encoding="utf-8")
    invalid, warnings, writable = research.load_state(invalid_path)

    assert invalid["candidates"] == {}
    assert warnings
    assert writable is False
    assert invalid_path.read_text(encoding="utf-8") == invalid_text

    boolean_schema_path = tmp_path / "boolean_schema_research_state.json"
    boolean_schema_text = json.dumps({"schema_version": True, "runs": {}, "candidates": {}})
    boolean_schema_path.write_text(boolean_schema_text, encoding="utf-8")
    invalid, warnings, writable = research.load_state(boolean_schema_path)

    assert invalid["candidates"] == {}
    assert warnings
    assert writable is False
    assert boolean_schema_path.read_text(encoding="utf-8") == boolean_schema_text


def test_legacy_json_migrates_in_memory_and_writes_gzip_on_next_save(tmp_path):
    legacy_path = tmp_path / "collision_research_state.json"
    compressed_path = tmp_path / "collision_research_state.json.gz"
    state, _run_id, _stats = research.update_state(
        research.empty_state(),
        _report("20261011"),
        "collision_research_20261011/exploratory/report.json",
    )
    state["schema_version"] = 1
    legacy_path.write_text(json.dumps(state), encoding="utf-8")

    loaded, warnings, writable = research.load_state(compressed_path)

    assert writable is True
    assert warnings
    assert loaded["schema_version"] == research.SCHEMA_VERSION
    assert loaded == {**state, "schema_version": research.SCHEMA_VERSION}
    assert legacy_path.is_file()

    research.save_state(loaded, compressed_path)
    restored, warnings, writable = research.load_state(compressed_path)

    assert warnings == []
    assert writable is True
    assert restored == loaded

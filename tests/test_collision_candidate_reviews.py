import copy
import hashlib
import json

import pytest

from scripts import collision_candidate_reviews as reviews
from scripts import review_collision_candidates as review_cli


def _candidate(left="fuyao.snapshot.pe_ttm", right="zhb.stat.pe_ttm"):
    return {
        "left": left,
        "right": right,
        "sample_count": 40,
        "sample_dates": ["T:20261019", "T:20261020"],
        "sample_codes": ["000001", "600000"],
        "evidence_sources": ["fuyao", "zhb"],
        "methods": [{"method": "affine_formula", "formula": "right ≈ left", "r_squared": 1.0}],
    }


def _event(identity, identifier, *, disposition="needs_external_evidence", reviewed_at=None):
    return reviews.record_review(
        reviews.empty_state(),
        identity,
        candidate=identifier,
        disposition=disposition,
        reviewer="tester",
        reviewed_at=reviewed_at or "2026-10-21T10:00:00+08:00",
        rationale="Keep the candidate pending until independent evidence is available.",
        evidence_refs=[{"path": "20261020/report.json", "sha256": "a" * 64}],
    )


def test_candidate_id_binds_source_method_and_sample_evidence_but_ignores_review_annotations():
    candidate = _candidate()
    identifier = reviews.candidate_id(candidate, "method_pair")
    annotated = copy.deepcopy(candidate)
    annotated["candidate_id"] = identifier
    annotated["review_disposition"] = "needs_external_evidence"
    annotated["research_history"] = {"last_seen": "20261020"}

    assert reviews.candidate_id(annotated, "method_pair") == identifier
    changed_sample = copy.deepcopy(candidate)
    changed_sample["sample_dates"] = ["T:20261020"]
    assert reviews.candidate_id(changed_sample, "method_pair") != identifier
    assert reviews.candidate_id(candidate, "l1_candidate") != identifier


def test_formula_candidate_identity_accepts_target_and_inputs_without_right_field():
    candidate = {
        "left": "tdx.quote.close",
        "right_inputs": ["tencent[47]", "tencent[48]"],
        "operator": "sum",
        "sample_dates": ["T:20261020"],
    }

    assert reviews.candidate_id(candidate, "formula_candidate").startswith("cc1_")
    with pytest.raises(ValueError, match="field pair or a valid formula"):
        reviews.candidate_id(candidate, "method_pair")


def test_review_state_is_append_only_idempotent_and_report_summary_tracks_pending():
    candidate = _candidate()
    identifier = reviews.candidate_id(candidate, "method_pair")
    identity = reviews.candidate_identity_payload(candidate, "method_pair")
    state, changed = _event(identity, identifier)
    replay, replay_changed = reviews.record_review(
        state,
        identity,
        candidate=identifier,
        disposition="needs_external_evidence",
        reviewer="tester",
        reviewed_at="2026-10-21T10:00:00+08:00",
        rationale="Keep the candidate pending until independent evidence is available.",
        evidence_refs=[{"path": "20261020/report.json", "sha256": "a" * 64}],
    )
    assert changed is True
    assert replay_changed is False
    assert replay == state

    report = {
        "method_candidate_inventory": [copy.deepcopy(candidate), _candidate(right="tencent[4]")],
        "method_candidates": [],
        "method_candidate_frontier": [],
        "actionable_L1": [],
        "L1-C": [],
        "L4": [],
        "formula_candidates": [],
    }
    summary = reviews.annotate_report(report, state)
    assert summary["candidate_generation"]["generated_record_count"] == 2
    assert summary["human_review"]["reviewed_count"] == 1
    assert summary["human_review"]["pending_count"] == 1
    assert summary["human_review"]["status"] == "pending"
    assert report["method_candidate_inventory"][0]["review_disposition"] == (
        "needs_external_evidence"
    )
    assert report["method_candidate_inventory"][1]["review_disposition"] == "unreviewed"
    assert reviews.validate_report_summary(report)["status"] == "complete"

    report["method_candidate_inventory"][0]["review_disposition"] = "rejected"
    assert reviews.validate_report_summary(report)["status"] == "incomplete"


def test_duplicate_group_members_are_visible_in_reverse_traceability_summary():
    first = _candidate()
    second = _candidate(right="zhb.full.pe_ttm")
    first_id = reviews.candidate_id(first, "method_pair")
    second_id = reviews.candidate_id(second, "method_pair")
    state = reviews.empty_state()
    for member in (second,):
        identity = reviews.candidate_identity_payload(member, "method_pair")
        state, _changed = reviews.record_review(
            state,
            identity,
            candidate=second_id,
            disposition="duplicate_grouped",
            reviewer="tester",
            reviewed_at="2026-10-21T10:00:00+08:00",
            rationale="Both candidates are supported by the same observed relation.",
            evidence_refs=[{"path": "20261020/report.json", "sha256": "a" * 64}],
            duplicate_of=first_id,
        )
    report = {
        "method_candidate_inventory": [first, second],
        "actionable_L1": [],
        "L1-C": [],
        "L4": [],
        "formula_candidates": [],
    }

    summary = reviews.annotate_report(report, state)

    assert summary["human_review"]["duplicate_groups"] == [
        {"representative_id": first_id, "member_candidate_ids": [second_id]}
    ]
    assert reviews.validate_report_summary(report)["status"] == "complete"


def test_review_history_keeps_prior_dispositions_and_replaces_current_state():
    candidate = _candidate()
    identifier = reviews.candidate_id(candidate, "method_pair")
    identity = reviews.candidate_identity_payload(candidate, "method_pair")
    state, _ = _event(identity, identifier)
    updated, changed = reviews.record_review(
        state,
        identity,
        candidate=identifier,
        disposition="accepted_for_adjudication",
        reviewer="tester",
        reviewed_at="2026-10-22T09:00:00+08:00",
        rationale="The independent source contract and sample evidence now agree.",
        evidence_refs=[{"path": "20261021/report.json", "sha256": "b" * 64}],
    )

    assert changed is True
    entry = updated["reviews"][identifier]
    assert [event["disposition"] for event in entry["history"]] == [
        "needs_external_evidence",
        "accepted_for_adjudication",
    ]
    assert entry["current"]["disposition"] == "accepted_for_adjudication"
    assert reviews._validate_state(updated) == (True, None)


def test_duplicate_group_requires_distinct_target_candidate():
    candidate = _candidate()
    identifier = reviews.candidate_id(candidate, "method_pair")
    identity = reviews.candidate_identity_payload(candidate, "method_pair")
    with pytest.raises(ValueError, match="duplicate_grouped requires"):
        reviews.record_review(
            reviews.empty_state(),
            identity,
            candidate=identifier,
            disposition="duplicate_grouped",
            reviewer="tester",
            reviewed_at="2026-10-21T10:00:00+08:00",
            rationale="Duplicate.",
            evidence_refs=[{"path": "20261020/report.json", "sha256": "a" * 64}],
            duplicate_of=identifier,
        )


def test_invalid_or_newer_review_ledger_is_preserved_and_not_writable(tmp_path):
    path = tmp_path / "reviews.json"
    original = json.dumps({"schema_version": 88, "reviews": {}})
    path.write_text(original, encoding="utf-8")

    state, warnings, writable = reviews.load_state(path)

    assert state["reviews"] == {}
    assert warnings
    assert writable is False
    assert path.read_text(encoding="utf-8") == original


def test_invalid_event_values_do_not_crash_or_overwrite_the_ledger(tmp_path):
    candidate = _candidate()
    identifier = reviews.candidate_id(candidate, "method_pair")
    identity = reviews.candidate_identity_payload(candidate, "method_pair")
    state, _changed = _event(identity, identifier)
    state["reviews"][identifier]["current"]["disposition"] = []
    state["reviews"][identifier]["history"][-1]["disposition"] = []
    path = tmp_path / "malformed_reviews.json"
    original = json.dumps(state)
    path.write_text(original, encoding="utf-8")

    loaded, warnings, writable = reviews.load_state(path)

    assert loaded["reviews"] == {}
    assert warnings
    assert writable is False
    assert path.read_text(encoding="utf-8") == original


def test_review_ledger_atomic_save_and_load_round_trip(tmp_path):
    candidate = _candidate()
    identifier = reviews.candidate_id(candidate, "method_pair")
    identity = reviews.candidate_identity_payload(candidate, "method_pair")
    state, _changed = _event(identity, identifier)
    path = tmp_path / "reviews.json"

    reviews.save_state(state, path)
    loaded, warnings, writable = reviews.load_state(path)

    assert loaded == state
    assert warnings == []
    assert writable is True


def test_decision_must_reference_collision_report_that_contains_candidate(tmp_path):
    verification_dir = tmp_path / "field_verification"
    report_dir = verification_dir / "20261020"
    report_dir.mkdir(parents=True)
    candidate = _candidate()
    identifier = reviews.candidate_id(candidate, "method_pair")
    report = {
        "method_candidate_inventory": [candidate],
        "actionable_L1": [],
        "L1-C": [],
        "L4": [],
        "formula_candidates": [],
    }
    (report_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False), encoding="utf-8"
    )
    decision = {
        "schema_version": 1,
        "candidate_id": identifier,
        "disposition": "accepted_for_adjudication",
        "reviewer": "tester",
        "reviewed_at": "2026-10-21T10:00:00+08:00",
        "rationale": "Both source documentation and independent daily samples match.",
        "evidence_refs": ["20261020/report.json", "https://example.com/contract"],
    }

    prepared, identity = reviews.prepare_review_decision(
        decision, verification_dir=verification_dir
    )

    assert prepared["candidate_id"] == identifier
    assert identity["method_version"] == reviews.METHOD_VERSION
    assert prepared["resolved_evidence_refs"][0]["path"] == "20261020/report.json"
    assert (
        prepared["resolved_evidence_refs"][0]["sha256"]
        == hashlib.sha256((report_dir / "report.json").read_bytes()).hexdigest()
    )


def test_decision_rejects_path_traversal_and_unrelated_report(tmp_path):
    verification_dir = tmp_path / "field_verification"
    verification_dir.mkdir()
    candidate = _candidate()
    identifier = reviews.candidate_id(candidate, "method_pair")
    decision = {
        "schema_version": 1,
        "candidate_id": identifier,
        "disposition": "rejected",
        "reviewer": "tester",
        "reviewed_at": "2026-10-21T10:00:00+08:00",
        "rationale": "The fields are not equivalent.",
        "evidence_refs": ["../outside.json"],
    }

    with pytest.raises(ValueError, match="inside field_verification"):
        reviews.prepare_review_decision(decision, verification_dir=verification_dir)


def test_duplicate_group_batch_expands_to_independent_auditable_decisions():
    first = {
        "candidate_id": "cc1_" + "1" * 64,
        "disposition": "duplicate_grouped",
        "reviewer": "tester",
        "reviewed_at": "2026-10-21T10:00:00+08:00",
        "rationale": "Equivalent candidate from the same evidence group.",
        "evidence_refs": ["20261020/report.json"],
        "duplicate_of": "cc1_" + "2" * 64,
    }
    second = {**first, "candidate_id": "cc1_" + "3" * 64}

    expanded = review_cli._expand_decision_document(
        {"schema_version": 1, "decisions": [first, second]}
    )

    assert [item["candidate_id"] for item in expanded] == [
        first["candidate_id"],
        second["candidate_id"],
    ]
    assert all(item["schema_version"] == 1 for item in expanded)
    with pytest.raises(ValueError, match="non-empty list"):
        review_cli._expand_decision_document({"schema_version": 1, "decisions": []})
    with pytest.raises(ValueError, match="more than once"):
        review_cli._expand_decision_document({"schema_version": 1, "decisions": [first, first]})

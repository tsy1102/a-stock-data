import copy
import json
from pathlib import Path

import pytest

from scripts import collision_candidate_reviews, collision_reporting
from scripts.query_collision_report import (
    ReportQueryError,
    list_report_sections,
    query_collision_report,
)


def _candidate(left: str, right: str) -> dict:
    return {
        "left": left,
        "right": right,
        "sample_count": 12,
        "sample_dates": ["T:20261020"],
        "sample_codes": ["600000"],
        "evidence_sources": [left.split(".", 1)[0], right.split(".", 1)[0]],
        "methods": [{"method": "scale", "ratio": 1.0}],
    }


def _report() -> dict:
    candidates = [
        _candidate("source_a.turnover", "source_b.turnover"),
        _candidate("source_c.close", "source_d.close"),
    ]
    candidates[0]["research_history"] = {"last_seen": "20261020"}
    report = {
        "schema_version": 5,
        "date": "20261020",
        "L1": [],
        "L1-C": [],
        "source_coverage": [],
        "actionable_L1": [],
        "mapped_pair_revalidations": [],
        "L4": [],
        "guardrail_hits": [],
        "method_candidates": copy.deepcopy(candidates),
        "method_candidate_count": len(candidates),
        "method_candidate_inventory": candidates,
        "method_candidate_frontier": [],
        "candidate_triage": {
            "summary": {"target_count": 1},
            "targets": [{"left": "unknown.turnover", "candidate_count": len(candidates)}],
        },
        "formula_candidates": [],
        "diagnostics": [],
    }
    collision_candidate_reviews.annotate_report(report, collision_candidate_reviews.empty_state())
    report["report_completeness"] = collision_reporting.build_report_completeness(report)
    return report


def _write_report(tmp_path: Path, report: dict | None = None) -> Path:
    path = tmp_path / "collision_report.json"
    path.write_text(
        json.dumps(report if report is not None else _report(), ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def _unpack_compact(payload: dict) -> list[dict]:
    unpacked = []
    for values, present in zip(payload["rows"], payload["present_columns"]):
        record = {}
        meta = {}
        scalar = None
        for index in present:
            column = payload["columns"][index]
            value = values[index]
            if column["scope"] == "meta":
                meta[column["name"]] = value
            elif column["scope"] == "record":
                record[column["name"]] = value
            else:
                scalar = value
        meta["record"] = record if meta["record_type"] == "object" else scalar
        unpacked.append(meta)
    return unpacked


def test_list_sections_reports_integrity_counts_and_pending_review(tmp_path):
    report_path = _write_report(tmp_path)

    result = list_report_sections(report_path)

    sections = {row["name"]: row for row in result["sections"]}
    assert result["report_completeness"] == "complete"
    assert result["candidate_review"] == {
        "status": "pending",
        "reviewed_count": 0,
        "pending_count": 2,
    }
    assert sections["method_candidate_inventory"]["json_record_count"] == 2
    assert sections["method_candidate_inventory"]["markdown_display_count"] == 0
    assert sections["candidate_triage.targets"]["json_record_count"] == 1


def test_approximate_matches_are_queryable_but_not_formal_review_candidates(tmp_path):
    report = _report()
    report["candidate_triage"]["approximate_matches"] = [
        {
            "left": "unknown.turnover_rate",
            "right": "anchor.turnover_rate",
            "evidence_type": "rounding_near_match_screen",
            "status": "screening_only",
            "near_hit_rate": 0.95,
            "sample_count": 60,
        }
    ]
    report["candidate_triage"]["summary"]["approximate_match_count"] = 1
    report["report_completeness"] = collision_reporting.build_report_completeness(report)
    report_path = _write_report(tmp_path, report)

    sections = {row["name"]: row for row in list_report_sections(report_path)["sections"]}
    result = query_collision_report(report_path, source="unknown", output_format="json")

    assert sections["candidate_triage.approximate_matches"]["json_record_count"] == 1
    assert [item["section"] for item in result["items"]] == ["candidate_triage.approximate_matches"]
    assert result["items"][0]["record"]["status"] == "screening_only"
    assert "candidate_id" not in result["items"][0]["record"]
    assert result["candidate_review"]["pending_count"] == 2


def test_v1_candidate_report_remains_queryable_after_method_v2_upgrade(tmp_path):
    report = _report()
    old_version = "collision-candidate-v1"
    old_ids = {}
    for row in report["method_candidate_inventory"]:
        identity = collision_candidate_reviews.candidate_identity_payload(
            row, "method_pair", method_version=old_version
        )
        identifier = collision_candidate_reviews.candidate_id_from_payload(identity)
        row["candidate_id"] = identifier
        row["review_disposition"] = "unreviewed"
        old_ids[(row["left"], row["right"])] = identifier
    report["candidate_review"]["method_version"] = old_version
    report["report_completeness"] = collision_reporting.build_report_completeness(report)
    report_path = _write_report(tmp_path, report)

    result = query_collision_report(
        report_path, sections=["method_candidate_inventory"], limit=2, output_format="json"
    )

    assert result["report_completeness"] == "complete"
    assert {
        (item["record"]["left"], item["record"]["right"]): item["record"]["candidate_id"]
        for item in result["items"]
    } == old_ids


def test_filters_match_source_prefix_full_field_path_and_candidate_id(tmp_path):
    report_path = _write_report(tmp_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    first_id = report["method_candidate_inventory"][0]["candidate_id"]

    by_source = query_collision_report(report_path, source="SOURCE_A", output_format="json")
    by_field = query_collision_report(report_path, field="source_b.turnover", output_format="json")
    by_id = query_collision_report(report_path, candidate_id=first_id, output_format="json")

    assert [item["record"]["candidate_id"] for item in by_source["items"]] == [first_id]
    assert [item["record"]["candidate_id"] for item in by_field["items"]] == [first_id]
    assert [item["record"]["candidate_id"] for item in by_id["items"]] == [first_id]
    assert by_source["filters"]["source"] == "SOURCE_A"


def test_pagination_keeps_report_and_selection_proofs_stable(tmp_path):
    report_path = _write_report(tmp_path)

    first = query_collision_report(
        report_path, disposition="unreviewed", offset=0, limit=1, output_format="json"
    )
    second = query_collision_report(
        report_path, disposition="unreviewed", offset=1, limit=1, output_format="json"
    )

    first_id = first["items"][0]["record"]["candidate_id"]
    second_id = second["items"][0]["record"]["candidate_id"]
    assert first["matched_count"] == second["matched_count"] == 2
    assert first["report_sha256"] == second["report_sha256"]
    assert first["selection_sha256"] == second["selection_sha256"]
    assert first["next_offset"] == 1 and first["exhausted"] is False
    assert second["next_offset"] is None and second["exhausted"] is True
    assert first_id != second_id


def test_compact_page_round_trips_missing_keys_and_nested_evidence(tmp_path):
    report_path = _write_report(tmp_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))

    compact = query_collision_report(report_path, sections=["method_candidate_inventory"], limit=2)
    unpacked = _unpack_compact(compact)

    assert compact["format"] == "compact"
    assert [row["record"] for row in unpacked] == report["method_candidate_inventory"]
    assert "research_history" in report["method_candidate_inventory"][0]
    assert "research_history" not in report["method_candidate_inventory"][1]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("missing_completeness", "report_completeness"),
        ("stale_completeness", "does not match"),
        ("old_date", "predates"),
        ("old_schema", "unsupported schema_version"),
        ("tampered_candidate", "integrity checks failed"),
    ],
)
def test_query_fails_closed_on_incompatible_or_tampered_reports(tmp_path, mutation, message):
    report = _report()
    if mutation == "missing_completeness":
        report.pop("report_completeness")
    elif mutation == "stale_completeness":
        report["report_completeness"]["sections"]["method_candidate_inventory"][
            "json_record_count"
        ] += 1
    elif mutation == "old_date":
        report["date"] = "20261014"
    elif mutation == "old_schema":
        report["schema_version"] = 4
    else:
        report["method_candidate_inventory"][0]["candidate_id"] = "cc1_" + "0" * 64
    report_path = _write_report(tmp_path, report)

    with pytest.raises(ReportQueryError, match=message):
        query_collision_report(report_path, source="source_a")


def test_query_is_read_only_and_does_not_mark_candidates_reviewed(tmp_path):
    report_path = _write_report(tmp_path)
    original = report_path.read_bytes()

    result = query_collision_report(report_path, source="source_a")

    assert result["candidate_review"]["status"] == "pending"
    assert result["candidate_review"]["pending_count"] == 2
    assert report_path.read_bytes() == original


def test_query_requires_a_bounded_selection_and_rejects_unknown_sections(tmp_path):
    report_path = _write_report(tmp_path)

    with pytest.raises(ReportQueryError, match="choose --list-sections"):
        query_collision_report(report_path)
    with pytest.raises(ReportQueryError, match="unknown or non-list section"):
        query_collision_report(report_path, sections=["report_completeness"])
    with pytest.raises(ReportQueryError, match="between 1 and 100"):
        query_collision_report(report_path, source="source_a", limit=101)

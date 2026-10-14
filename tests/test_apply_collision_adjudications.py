import copy

import pytest

from scripts.apply_collision_adjudications import (
    REPO_ROOT,
    VERIFY_DIR,
    _inside_verification_dir,
    apply_adjudications,
)


def test_decision_and_report_paths_use_the_documented_bases():
    decision, decision_relative = _inside_verification_dir(
        "docs/field_verification/adjudications/review.json", "decision file"
    )
    report, report_relative = _inside_verification_dir(
        "collision_research_20261005/verified_anchor_only/20261005/report.json",
        "collision report",
        relative_base=VERIFY_DIR,
    )

    assert decision == REPO_ROOT / "docs" / "field_verification" / "adjudications" / "review.json"
    assert decision_relative == "adjudications/review.json"
    assert (
        report
        == VERIFY_DIR
        / "collision_research_20261005"
        / "verified_anchor_only"
        / "20261005"
        / "report.json"
    )
    assert (
        report_relative == "collision_research_20261005/verified_anchor_only/20261005/report.json"
    )


def _inputs(action="verify"):
    registry = {
        "meta": {},
        "sources": [],
        "mappings": [],
        "fields": [
            {
                "code": "unknown.value",
                "source": "target-source",
                "sources": ["target-source"],
                "status": "unverified",
            },
            {
                "code": "quote.value",
                "source": "anchor-source",
                "sources": ["anchor-source"],
                "status": "verified",
            },
        ],
        "source_fields": [
            {
                "source": "target-source",
                "code": "unknown.value",
                "canonical": "",
                "meaning": "",
                "unit": "",
                "section": "",
                "sections": [],
                "status": "unverified",
                "status_resolution": "registry_status_only_single_source",
                "status_evidence": {"reference_status_raw": []},
                "reference_evidence": [],
            },
            {
                "source": "anchor-source",
                "code": "quote.value",
                "canonical": "quote.value",
                "meaning": "已确认锚字段",
                "unit": "元",
                "section": "anchor.md",
                "sections": ["anchor.md"],
                "status": "verified",
                "status_resolution": "matched",
                "status_evidence": {"reference_status_raw": ["verified"]},
                "reference_evidence": [],
            },
        ],
    }
    lineage = {
        "sources": {
            "target-source": {
                "runtime_aliases": ["left"],
                "independence_family": "target-provider",
                "independence_status": "unconfirmed",
                "anchor_eligible": False,
            },
            "anchor-source": {
                "runtime_aliases": ["right"],
                "independence_family": "anchor-provider",
                "independence_status": "confirmed",
                "anchor_eligible": True,
            },
        },
        "runtime_sources": {
            "left": {
                "independence_family": "target-provider",
                "independence_status": "unconfirmed",
            },
            "right": {"independence_family": "anchor-provider", "independence_status": "confirmed"},
        },
        "source_aliases": {"target-source": "left", "anchor-source": "right"},
    }
    report = {
        "schema_version": 2,
        "collision_mode": "verified_anchor_only",
        "exploratory_pair_count": 0,
        "L1": [
            {
                "left": "left.unknown.value",
                "right": "right.quote.value",
                "level": "L1",
                "ratio": None,
                "overall_hit": 1.0,
                "n_days": 3,
                "n_pairs": 60,
                "distinct_days": ["T:20261001", "T:20261002", "T:20261005"],
                "daily_sample_counts": {"T:20261001": 20, "T:20261002": 20, "T:20261005": 20},
                "evidence_sources": ["target-provider", "anchor-provider"],
            }
        ],
    }
    decision_document = {
        "schema_version": 1,
        "report": "sample_report.json",
        "reviewer": "reviewer",
        "reviewed_on": "2026-10-06",
        "decisions": [
            {
                "id": "20261006-unknown-value",
                "candidate": {"left": "left.unknown.value", "right": "right.quote.value"},
                "target": {"source": "target-source", "code": "unknown.value"},
                "anchor": {"source": "anchor-source", "code": "quote.value"},
                "action": action,
                "canonical": "market.metric",
                "meaning": "目标字段含义",
                "unit": "元",
                "rationale": "经原始样本和三日证据逐项复核。",
            }
        ],
    }
    return registry, lineage, decision_document, report


def test_verify_adjudication_updates_source_record_aggregate_and_mapping():
    registry, lineage, document, report = _inputs()

    updated, stats = apply_adjudications(
        registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
    )

    target = next(row for row in updated["source_fields"] if row["source"] == "target-source")
    aggregate = next(row for row in updated["fields"] if row["code"] == "unknown.value")
    assert target["status"] == "verified"
    assert target["meaning"] == "目标字段含义"
    assert target["sections"] == ["sample_report.json"]
    assert target["adjudications"][0]["reviewer"] == "reviewer"
    assert aggregate["status"] == "verified"
    assert aggregate["source_statuses"] == {"target-source": "verified"}
    assert updated["mappings"][0]["relation"] == "same_number_same_meaning"
    assert stats == {
        "verified": 1,
        "metadata_enriched": 0,
        "linked": 0,
        "anchor_metadata_corrected": 0,
        "already_applied": 0,
        "mappings_added": 1,
    }
    assert registry["source_fields"][0]["status"] == "unverified"


def test_aggregate_projection_does_not_borrow_metadata_from_a_blank_source_row():
    registry, lineage, document, report = _inputs()
    registry["source_fields"].append(
        {
            "source": "other-source",
            "code": "unknown.value",
            "canonical": "",
            "meaning": "",
            "unit": "",
            "section": "",
            "sections": [],
            "status": "unverified",
            "status_resolution": "registry_status_only_single_source",
            "status_evidence": {"reference_status_raw": []},
            "reference_evidence": [],
        }
    )

    updated, _ = apply_adjudications(
        registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
    )

    aggregate = next(row for row in updated["fields"] if row["code"] == "unknown.value")
    assert aggregate["source"] is None
    assert aggregate["sources"] == ["other-source", "target-source"]
    assert aggregate["canonical"] == ""
    assert aggregate["meaning"] == ""
    assert aggregate["unit"] == ""


def test_external_evidence_is_preserved_with_verified_decision():
    registry, lineage, document, report = _inputs()
    document["decisions"][0]["external_evidence"] = ["https://example.com/field-spec"]

    updated, _ = apply_adjudications(
        registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
    )

    target = next(row for row in updated["source_fields"] if row["source"] == "target-source")
    assert target["adjudications"][0]["external_evidence"] == ["https://example.com/field-spec"]
    assert target["reference_evidence"][-1]["external_evidence"] == [
        "https://example.com/field-spec"
    ]


def test_verify_with_incomplete_anchor_requires_external_evidence():
    registry, lineage, document, report = _inputs()
    anchor = registry["source_fields"][1]
    anchor.update({"canonical": "", "meaning": "", "unit": ""})

    with pytest.raises(ValueError, match="external_evidence when the selected anchor metadata"):
        apply_adjudications(
            registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
        )

    document["decisions"][0]["external_evidence"] = ["https://example.com/field-spec"]
    updated, _ = apply_adjudications(
        registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
    )
    assert updated["source_fields"][0]["status"] == "verified"


def test_reapplying_the_same_decision_is_idempotent():
    registry, lineage, document, report = _inputs()
    once, _ = apply_adjudications(
        registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
    )

    twice, stats = apply_adjudications(
        once, lineage, document, report, "sample_report.json", "adjudications/review.json"
    )

    assert twice == once
    assert stats["already_applied"] == 1
    assert len(twice["mappings"]) == 1


def test_verified_metadata_enrichment_supports_reversed_pair_and_anchor_correction():
    registry, lineage, document, report = _inputs(action="enrich_metadata")
    target = registry["source_fields"][0]
    target.update(
        {
            "canonical": "unknown.value",
            "meaning": "",
            "unit": "",
            "status": "verified",
            "status_resolution": "matched",
        }
    )
    registry["fields"][0]["status"] = "verified"
    document["decisions"][0]["previous"] = {
        "canonical": "unknown.value",
        "meaning": "",
        "unit": "",
    }
    document["decisions"][0]["candidate"] = {
        "left": "right.quote.value",
        "right": "left.unknown.value",
    }
    report["L1"][0]["left"], report["L1"][0]["right"] = (
        report["L1"][0]["right"],
        report["L1"][0]["left"],
    )
    document["decisions"][0]["anchor_metadata_correction"] = {
        "previous": {
            "canonical": "quote.value",
            "meaning": "已确认锚字段",
            "unit": "元",
        },
        "updated": {
            "canonical": "quote.value",
            "meaning": "已校正锚字段",
            "unit": "元",
        },
        "rationale": "独立协议文档确认现有展示含义错误。",
        "external_evidence": ["https://example.com/field-spec"],
    }

    once, stats = apply_adjudications(
        registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
    )

    enriched = next(row for row in once["source_fields"] if row["source"] == "target-source")
    corrected_anchor = next(
        row for row in once["source_fields"] if row["source"] == "anchor-source"
    )
    assert enriched["status"] == "verified"
    assert enriched["status_resolution"] == "matched"
    assert enriched["canonical"] == "market.metric"
    assert enriched["meaning"] == "目标字段含义"
    assert enriched["adjudications"][0]["metadata_change"]["before"] == {
        "canonical": "unknown.value",
        "meaning": "",
        "unit": "",
    }
    assert corrected_anchor["meaning"] == "已校正锚字段"
    assert corrected_anchor["adjudications"][0]["action"] == "correct_metadata"
    assert once["mappings"][0]["from"] == {"source": "target-source", "code": "unknown.value"}
    assert stats == {
        "verified": 0,
        "metadata_enriched": 1,
        "linked": 0,
        "anchor_metadata_corrected": 1,
        "already_applied": 0,
        "mappings_added": 1,
    }

    twice, repeat_stats = apply_adjudications(
        once, lineage, document, report, "sample_report.json", "adjudications/review.json"
    )
    assert twice == once
    assert repeat_stats["already_applied"] == 1


def test_verified_metadata_enrichment_cannot_overwrite_existing_meaning():
    registry, lineage, document, report = _inputs(action="enrich_metadata")
    target = registry["source_fields"][0]
    target.update(
        {
            "canonical": "established.metric",
            "meaning": "既有含义",
            "unit": "元",
            "status": "verified",
        }
    )
    document["decisions"][0]["previous"] = {
        "canonical": "established.metric",
        "meaning": "既有含义",
        "unit": "元",
    }
    with pytest.raises(ValueError, match="cannot overwrite established metadata"):
        apply_adjudications(
            registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
        )
    assert target["meaning"] == "既有含义"


def test_link_verified_records_relation_without_changing_field_metadata():
    registry, lineage, document, report = _inputs(action="link_verified")
    target = registry["source_fields"][0]
    target.update(
        {
            "canonical": "market.metric",
            "meaning": "已确认的目标含义",
            "unit": "股",
            "status": "verified",
        }
    )
    registry["fields"][0]["status"] = "verified"
    before = copy.deepcopy(target)

    updated, stats = apply_adjudications(
        registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
    )

    linked = next(row for row in updated["source_fields"] if row["source"] == "target-source")
    assert {key: linked[key] for key in ("canonical", "meaning", "unit", "status")} == {
        key: before[key] for key in ("canonical", "meaning", "unit", "status")
    }
    assert linked["adjudications"][0]["action"] == "link_verified"
    assert len(updated["mappings"]) == 1
    assert stats == {
        "verified": 0,
        "metadata_enriched": 0,
        "linked": 1,
        "anchor_metadata_corrected": 0,
        "already_applied": 0,
        "mappings_added": 1,
    }


def test_pair_disproof_cannot_disprove_the_entire_target_field():
    registry, lineage, document, report = _inputs(action="disprove")

    with pytest.raises(ValueError, match="only verified semantic conclusions"):
        apply_adjudications(
            registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
        )

    assert registry["source_fields"][0]["status"] == "unverified"
    assert registry["mappings"] == []


@pytest.mark.parametrize(
    "report_change,match",
    [
        ({"collision_mode": "exploratory"}, "verified_anchor_only"),
        ({"exploratory_pair_count": 1}, "exploratory reports"),
        ({"L1": []}, "found 0"),
    ],
)
def test_non_default_or_missing_candidates_are_rejected(report_change, match):
    registry, lineage, document, report = _inputs()
    report.update(copy.deepcopy(report_change))

    with pytest.raises(ValueError, match=match):
        apply_adjudications(
            registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
        )


def test_runtime_id_must_match_explicit_source_and_full_code_path():
    registry, lineage, document, report = _inputs()
    document["decisions"][0]["target"]["code"] = "value"

    with pytest.raises(ValueError, match="does not match report field"):
        apply_adjudications(
            registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
        )


def test_runtime_id_normalizes_only_the_zhb_full_snapshot_wrapper():
    from scripts.apply_collision_adjudications import _runtime_identity

    lineage = {
        "sources": {"ZHB-tdxstat2": {"runtime_aliases": ["zhb"]}},
        "runtime_sources": {"zhb": {}},
        "source_aliases": {},
    }

    assert _runtime_identity("zhb.full.amount", "ZHB-tdxstat2", lineage) == (
        "zhb",
        "amount",
    )
    assert _runtime_identity("zhb.stat2.low_52w", "ZHB-tdxstat2", lineage) == (
        "zhb",
        "stat2.low_52w",
    )


def test_runtime_id_normalizes_the_tdx_finance_info_adapter_wrapper():
    from scripts.apply_collision_adjudications import _runtime_identity

    lineage = {
        "sources": {"TDX(双命名源)": {"runtime_aliases": ["tdx"]}},
        "runtime_sources": {"tdx": {}},
        "source_aliases": {},
    }

    assert _runtime_identity("tdx.finance_info.lirunzonghe", "TDX(双命名源)", lineage) == (
        "tdx",
        "lirunzonghe",
    )


def test_conflict_status_cannot_be_overridden_by_collision_adjudication():
    registry, lineage, document, report = _inputs()
    registry["source_fields"][0]["status"] = "conflict"

    with pytest.raises(ValueError, match="requires separate conflict review"):
        apply_adjudications(
            registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
        )

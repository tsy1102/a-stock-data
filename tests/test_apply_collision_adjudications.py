import copy
import hashlib
import json

import pytest

from scripts import apply_collision_adjudications as adjudication_module
from scripts import collision_candidate_reviews as candidate_reviews
from scripts import collision_adjudication_transformations as adjudication_transformations
from scripts import collide
from scripts.apply_collision_adjudications import (
    REPO_ROOT,
    VERIFY_DIR,
    _inside_verification_dir,
    apply_adjudications,
    apply_empirical_source_semantics_adjudications,
    apply_source_contract_adjudications,
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


def test_aggregate_projection_counts_null_status_resolution_as_unresolved():
    registry, _, _, _ = _inputs()
    registry["source_fields"][1]["status_resolution"] = None

    adjudication_transformations._refresh_aggregate_projection(registry, {"unknown.value"})

    assert registry["meta"]["source_field_stats"]["unresolved"] == 1
    assert None not in registry["meta"]["source_field_stats"]


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
        "schema_version": 3,
        "collision_mode": "verified_anchor_only",
        "exploratory_pair_count": 0,
        "method_candidate_count": 0,
        "method_candidate_inventory": [],
        "method_candidates": [],
        "method_candidate_frontier": [],
        "actionable_L1": [],
        "mapped_pair_revalidations": [],
        "source_coverage": [],
        "candidate_triage": {"summary": {"target_count": 0}, "targets": []},
        "report_completeness": {
            "schema_version": 1,
            "status": "complete",
            "issues": [],
            "method_candidate_inventory": {
                "generated_count": 0,
                "saved_count": 0,
                "unique_pair_count": 0,
                "missing_detail_count": 0,
                "excess_detail_count": 0,
                "duplicate_pair_count": 0,
                "invalid_pair_identity_count": 0,
                "target_candidate_count_sum": 0,
                "invalid_target_candidate_count_rows": 0,
            },
            "sections": {
                "L1": {"json_record_count": 1},
                "actionable_L1": {"json_record_count": 0},
                "mapped_pair_revalidations": {"json_record_count": 0},
                "source_coverage": {"json_record_count": 0},
                "candidate_triage.targets": {"json_record_count": 0},
            },
        },
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
    report["actionable_L1"] = copy.deepcopy(report["L1"])
    report["report_completeness"]["sections"]["actionable_L1"]["json_record_count"] = 1
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


@pytest.mark.parametrize("collision_schema_version", [3, 4])
def test_verify_adjudication_updates_source_record_aggregate_and_mapping(collision_schema_version):
    registry, lineage, document, report = _inputs()
    report["schema_version"] = collision_schema_version

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


def _prepare_schema5_report(report, review_disposition=None):
    report.update(
        {
            "schema_version": 5,
            "L1-C": [],
            "L4": [],
            "guardrail_hits": [],
            "method_candidates": [],
            "method_candidate_count": 0,
            "method_candidate_inventory": [],
            "method_candidate_frontier": [],
            "formula_candidates": [],
            "diagnostics": [],
            "source_relation_review": {"rows": []},
            "candidate_triage": {
                "summary": {"target_count": 0},
                "targets": [],
                "low_information_fields": [],
                "date_value_candidates": [],
            },
        }
    )
    state = candidate_reviews.empty_state()
    if review_disposition:
        row = report["actionable_L1"][0]
        identity = candidate_reviews.candidate_identity_payload(row, "l1_candidate")
        identifier = candidate_reviews.candidate_id_from_payload(identity)
        state, _changed = candidate_reviews.record_review(
            state,
            identity,
            candidate=identifier,
            disposition=review_disposition,
            reviewer="reviewer",
            reviewed_at="2026-10-06T12:00:00+08:00",
            rationale="Reviewed the candidate evidence before adjudication.",
            evidence_refs=[{"path": "sample_report.json", "sha256": "a" * 64}],
        )
    candidate_reviews.annotate_report(report, state)
    report["report_completeness"] = collide.build_report_completeness(report)
    return report


def test_schema5_registry_adjudication_requires_explicit_candidate_acceptance():
    registry, lineage, document, unreviewed_report = _inputs()
    _prepare_schema5_report(unreviewed_report)

    with pytest.raises(ValueError, match="accepted_for_adjudication"):
        apply_adjudications(
            registry,
            lineage,
            document,
            unreviewed_report,
            "sample_report.json",
            "adjudications/review.json",
        )

    registry, lineage, document, accepted_report = _inputs()
    _prepare_schema5_report(accepted_report, "accepted_for_adjudication")
    updated, stats = apply_adjudications(
        registry,
        lineage,
        document,
        accepted_report,
        "sample_report.json",
        "adjudications/review.json",
    )

    assert updated["source_fields"][0]["status"] == "verified"
    assert stats["verified"] == 1


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
    report["actionable_L1"][0]["left"], report["actionable_L1"][0]["right"] = (
        report["actionable_L1"][0]["right"],
        report["actionable_L1"][0]["left"],
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


def _source_contract_inputs():
    registry, _, _, _ = _inputs()
    decision_document = {
        "schema_version": 1,
        "evidence_basis": "source_contract",
        "reviewer": "reviewer",
        "reviewed_on": "2026-10-18",
        "decisions": [
            {
                "id": "20261018-source-contract",
                "action": "verify_source_contract",
                "target": {"source": "target-source", "code": "unknown.value"},
                "previous_status": "unverified",
                "previous_status_resolution": "registry_status_only_single_source",
                "previous": {"canonical": "", "meaning": "", "unit": ""},
                "canonical": "market.metric",
                "meaning": "由上游接口契约确认的字段含义",
                "unit": "元",
                "rationale": "已核对该运行字段到接口响应键的实际映射和上游契约。",
                "source_contract": {
                    "authority": "官方数据接口",
                    "revision": "接口文档 2026-10-10",
                    "path": "行情接口字段表",
                    "locator": "响应字段 unknown.value",
                    "url": "https://example.com/field-spec",
                },
            }
        ],
    }
    return registry, decision_document


def _same_source_alias_conflict_inputs(evidence_path):
    registry, document = _source_contract_inputs()
    target = registry["source_fields"][0]
    anchor_meaning = "由上游接口契约确认的字段含义"
    registry["source_fields"].append(
        {
            "source": "target-source",
            "code": "raw.value",
            "canonical": "raw.value",
            "meaning": anchor_meaning,
            "unit": "元",
            "status": "verified",
            "status_resolution": "matched",
            "status_evidence": {
                "reference_statuses": ["verified"],
                "registry_aggregate_status": "verified",
                "values": ["verified"],
            },
            "attribute_conflicts": {},
            "reference_evidence": [{"status": "verified"}],
        }
    )
    target.update(
        {
            "status": "conflict",
            "status_resolution": "status_conflict",
            "status_evidence": {
                "reference_statuses": ["candidate"],
                "reference_status_raw": ["候选"],
                "registry_aggregate_status": "verified",
                "registry_aggregate_sources": ["target-source"],
                "values": ["candidate", "verified"],
            },
            "reference_evidence": [{"status": "candidate"}],
            "attribute_conflicts": {},
        }
    )
    decision = document["decisions"][0]
    decision.update(
        {
            "previous_status": "conflict",
            "previous_status_resolution": "status_conflict",
            "meaning": anchor_meaning,
            "unit": "元",
            "same_source_alias": {
                "source": "target-source",
                "code": "raw.value",
                "evidence_path": str(evidence_path),
                "locator": "§3 表格第 1 行",
                "observed_pairs": 20,
                "mismatches": 0,
            },
        }
    )
    return registry, document


def test_source_contract_verifies_one_field_without_creating_cross_source_mapping():
    registry, document = _source_contract_inputs()

    updated, stats = apply_source_contract_adjudications(
        registry, document, "adjudications/source_contract_review.json"
    )

    target = next(row for row in updated["source_fields"] if row["source"] == "target-source")
    assert target["status"] == "verified"
    assert target["status_resolution"] == "verified_by_source_contract"
    assert target["canonical"] == "market.metric"
    assert target["meaning"] == "由上游接口契约确认的字段含义"
    assert target["adjudications"][0]["evidence_basis"] == "authoritative_source_contract"
    assert target["reference_evidence"][-1]["source_contract"]["revision"] == (
        "接口文档 2026-10-10"
    )
    assert updated["field_matrix"]["market.metric"] == ["target-source"]
    assert updated["mappings"] == []
    assert stats == {
        "source_contract_verified": 1,
        "status_conflicts_resolved": 0,
        "metadata_corrected": 0,
        "already_applied": 0,
        "mappings_added": 0,
    }


def test_source_contract_decision_is_idempotent():
    registry, document = _source_contract_inputs()
    once, _ = apply_source_contract_adjudications(
        registry, document, "adjudications/source_contract_review.json"
    )

    twice, stats = apply_source_contract_adjudications(
        once, document, "adjudications/source_contract_review.json"
    )

    assert twice == once
    assert stats == {
        "source_contract_verified": 0,
        "status_conflicts_resolved": 0,
        "metadata_corrected": 0,
        "already_applied": 1,
        "mappings_added": 0,
    }


def _set_status_only_conflict(registry, document):
    target = registry["source_fields"][0]
    target.update(
        {
            "status": "conflict",
            "status_resolution": "status_conflict",
            "status_evidence": {
                "reference_statuses": ["verified"],
                "reference_status_raw": ["已确认"],
                "registry_aggregate_status": "unverified",
                "registry_aggregate_sources": ["target-source"],
                "values": ["verified", "unverified"],
            },
            "reference_evidence": [
                {
                    "status": "verified",
                    "canonical": "",
                    "meaning": "",
                    "unit": "",
                }
            ],
            "attribute_conflicts": {},
        }
    )
    decision = document["decisions"][0]
    decision["previous_status"] = "conflict"
    decision["previous_status_resolution"] = "status_conflict"
    return target, decision


def _set_cross_source_aggregate_conflict(registry, document):
    target, decision = _set_status_only_conflict(registry, document)
    sources = ["target-source", "other-source"]
    target["status_evidence"].update(
        {
            "registry_aggregate_status": "conflict",
            "registry_aggregate_sources": sources,
            "values": ["verified", "candidate"],
        }
    )
    target["registry_aggregate"] = {"status": "conflict", "sources": sources}
    return target, decision


def test_source_contract_resolves_only_registry_aggregate_status_conflict():
    registry, document = _source_contract_inputs()
    _set_status_only_conflict(registry, document)

    updated, stats = apply_source_contract_adjudications(
        registry, document, "adjudications/source_contract_review.json"
    )

    target = next(row for row in updated["source_fields"] if row["source"] == "target-source")
    assert target["status"] == "verified"
    assert target["status_resolution"] == "verified_by_source_contract"
    assert updated["mappings"] == []
    assert stats == {
        "source_contract_verified": 1,
        "status_conflicts_resolved": 1,
        "metadata_corrected": 0,
        "already_applied": 0,
        "mappings_added": 0,
    }


def test_source_contract_resolves_cross_source_aggregate_conflict_source_locally():
    registry, document = _source_contract_inputs()
    _set_cross_source_aggregate_conflict(registry, document)

    updated, stats = apply_source_contract_adjudications(
        registry, document, "adjudications/source_contract_review.json"
    )

    target = next(row for row in updated["source_fields"] if row["source"] == "target-source")
    assert target["status"] == "verified"
    assert target["status_resolution"] == "verified_by_source_contract"
    assert target["registry_aggregate"]["status"] == "conflict"
    assert target["registry_aggregate"]["sources"] == ["target-source", "other-source"]
    assert updated["mappings"] == []
    assert stats["status_conflicts_resolved"] == 1
    assert stats["mappings_added"] == 0


@pytest.mark.parametrize(
    "mutate",
    [
        lambda target: target["status_evidence"].update(
            registry_aggregate_sources=["target-source"]
        ),
        lambda target: target["registry_aggregate"].update(
            sources=["target-source", "different-source"]
        ),
        lambda target: target["status_evidence"].update(values=["verified", "disproved"]),
        lambda target: target["reference_evidence"][0].update(status="candidate"),
        lambda target: target.update(attribute_ambiguities={"meaning": ["ambiguous"]}),
    ],
)
def test_source_contract_rejects_unsafe_cross_source_aggregate_conflict(mutate):
    registry, document = _source_contract_inputs()
    target, _ = _set_cross_source_aggregate_conflict(registry, document)
    mutate(target)

    with pytest.raises(ValueError, match="cannot resolve semantic or attribute conflicts"):
        apply_source_contract_adjudications(
            registry, document, "adjudications/source_contract_review.json"
        )


def test_source_contract_resolves_legacy_conflict_through_verified_same_source_alias(
    tmp_path, monkeypatch
):
    verify_dir = tmp_path / "docs" / "field_verification"
    evidence_path = verify_dir / "research" / "alias_evidence.md"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text("reviewed alias evidence\n", encoding="utf-8")
    monkeypatch.setattr(adjudication_module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    registry, document = _same_source_alias_conflict_inputs(evidence_path)

    updated, stats = apply_source_contract_adjudications(
        registry, document, "adjudications/source_contract_review.json"
    )

    target = next(row for row in updated["source_fields"] if row["code"] == "unknown.value")
    assert target["status"] == "verified"
    assert target["status_resolution"] == "verified_by_source_contract"
    assert target["adjudications"][0]["same_source_alias"] == {
        "source": "target-source",
        "code": "raw.value",
        "evidence_path": "research/alias_evidence.md",
        "locator": "§3 表格第 1 行",
        "observed_pairs": 20,
        "mismatches": 0,
    }
    assert updated["mappings"] == []
    assert stats["status_conflicts_resolved"] == 1
    repeated, repeat_stats = apply_source_contract_adjudications(
        updated, document, "adjudications/source_contract_review.json"
    )
    assert repeated == updated
    assert repeat_stats["already_applied"] == 1


def _verified_metadata_correction_inputs():
    registry, document = _source_contract_inputs()
    target = registry["source_fields"][0]
    previous = {"canonical": "legacy.metric", "meaning": "旧释义", "unit": "分钟"}
    updated = {"canonical": "market.metric", "meaning": "校正后的字段释义", "unit": "%"}
    target.update(
        {
            **previous,
            "status": "verified",
            "status_resolution": "matched",
            "status_evidence": {
                "reference_statuses": ["verified"],
                "registry_aggregate_status": "verified",
                "values": ["verified"],
            },
            "reference_evidence": [{"status": "verified"}],
            "attribute_conflicts": {},
        }
    )
    decision = document["decisions"][0]
    decision.update(
        {
            "id": "20261018-correct-verified-metadata",
            "action": "correct_verified_metadata",
            "previous_status": "verified",
            "previous_status_resolution": "matched",
            "previous": previous,
            **updated,
            "metadata_correction": {
                "previous": previous,
                "updated": updated,
                "rationale": "已核对固定来源契约，纠正旧的路径释义和单位。",
            },
        }
    )
    return registry, document


def test_source_contract_corrects_verified_metadata_with_explicit_evidence():
    registry, document = _verified_metadata_correction_inputs()

    updated, stats = apply_source_contract_adjudications(
        registry, document, "adjudications/verified_metadata_correction.json"
    )

    target = updated["source_fields"][0]
    assert target["status"] == "verified"
    assert target["status_resolution"] == "verified_by_source_contract"
    assert target["meaning"] == "校正后的字段释义"
    assert target["unit"] == "%"
    assert target["adjudications"][0]["action"] == "correct_verified_metadata"
    assert target["adjudications"][0]["metadata_correction"]["previous"]["meaning"] == "旧释义"
    assert stats["metadata_corrected"] == 1
    assert stats["mappings_added"] == 0
    assert updated["mappings"] == []


def test_source_contract_verified_metadata_correction_is_idempotent():
    registry, document = _verified_metadata_correction_inputs()

    once, _ = apply_source_contract_adjudications(
        registry, document, "adjudications/verified_metadata_correction.json"
    )
    twice, repeat_stats = apply_source_contract_adjudications(
        once, document, "adjudications/verified_metadata_correction.json"
    )

    assert twice == once
    assert repeat_stats["already_applied"] == 1
    assert repeat_stats["metadata_corrected"] == 0


def test_source_contract_verified_metadata_correction_requires_matched_resolution():
    registry, document = _verified_metadata_correction_inputs()
    document["decisions"][0]["previous_status_resolution"] = "status_conflict"

    with pytest.raises(ValueError, match="status_resolution='matched'"):
        apply_source_contract_adjudications(
            registry, document, "adjudications/verified_metadata_correction.json"
        )


def test_source_contract_rejects_verified_metadata_correction_without_diff_record():
    registry, document = _verified_metadata_correction_inputs()
    document["decisions"][0].pop("metadata_correction")

    with pytest.raises(ValueError, match="requires an explicit metadata_correction"):
        apply_source_contract_adjudications(
            registry, document, "adjudications/verified_metadata_correction.json"
        )


def test_source_contract_rejects_verified_metadata_correction_with_attribute_conflict():
    registry, document = _verified_metadata_correction_inputs()
    registry["source_fields"][0]["attribute_conflicts"] = {"unit": ["分钟", "%"]}

    with pytest.raises(ValueError, match="exact previous_attribute_conflicts snapshot"):
        apply_source_contract_adjudications(
            registry, document, "adjudications/verified_metadata_correction.json"
        )


def test_source_contract_metadata_correction_resolves_exact_attribute_conflict_snapshot():
    registry, document = _verified_metadata_correction_inputs()
    conflicts = {"meaning": ["旧释义", "冲突释义"], "unit": ["分钟", "%"]}
    registry["source_fields"][0]["attribute_conflicts"] = conflicts
    document["decisions"][0]["previous_attribute_conflicts"] = conflicts

    updated, stats = apply_source_contract_adjudications(
        registry, document, "adjudications/verified_metadata_correction.json"
    )

    target = updated["source_fields"][0]
    assert target["attribute_conflicts"] == {}
    assert target["adjudications"][0]["resolved_attribute_conflicts"] == conflicts
    assert stats["metadata_corrected"] == 1

    repeated, repeat_stats = apply_source_contract_adjudications(
        updated, document, "adjudications/verified_metadata_correction.json"
    )
    assert repeated == updated
    assert repeat_stats["already_applied"] == 1
    assert repeat_stats["metadata_corrected"] == 0


def test_source_contract_metadata_correction_rejects_mismatched_conflict_snapshot():
    registry, document = _verified_metadata_correction_inputs()
    registry["source_fields"][0]["attribute_conflicts"] = {"unit": ["分钟", "%"]}
    document["decisions"][0]["previous_attribute_conflicts"] = {"unit": ["分钟", "秒"]}

    with pytest.raises(ValueError, match="exact previous_attribute_conflicts snapshot"):
        apply_source_contract_adjudications(
            registry, document, "adjudications/verified_metadata_correction.json"
        )


def test_source_contract_conflict_resolution_can_fill_blank_metadata():
    registry, document = _verified_metadata_correction_inputs()
    target = registry["source_fields"][0]
    target.update(canonical="", meaning="", unit="")
    conflicts = {"canonical": ["old_name", "new_name"], "unit": ["", "YYYYMMDD"]}
    target["attribute_conflicts"] = conflicts
    decision = document["decisions"][0]
    previous = {"canonical": "", "meaning": "", "unit": ""}
    updated = {"canonical": "new_name", "meaning": "日期含义", "unit": "YYYYMMDD"}
    decision.update(
        {
            "previous": previous,
            "previous_attribute_conflicts": conflicts,
            **updated,
            "metadata_correction": {
                "previous": previous,
                "updated": updated,
                "rationale": "精确冲突快照证明旧属性为空且候选冲突，来源契约确认目标值。",
            },
        }
    )

    result, stats = apply_source_contract_adjudications(
        registry, document, "adjudications/verified_metadata_correction.json"
    )

    resolved = result["source_fields"][0]
    assert resolved["canonical"] == "new_name"
    assert resolved["meaning"] == "日期含义"
    assert resolved["unit"] == "YYYYMMDD"
    assert resolved["attribute_conflicts"] == {}
    assert resolved["adjudications"][0]["resolved_attribute_conflicts"] == conflicts
    assert stats["metadata_corrected"] == 1


@pytest.mark.parametrize(
    "change,match",
    [
        (
            lambda d: d["decisions"][0]["same_source_alias"].update(
                source="anchor-source", code="quote.value"
            ),
            "target's source",
        ),
        (
            lambda d: d["decisions"][0]["same_source_alias"].update(mismatches=1),
            "mismatches must be zero",
        ),
        (
            lambda d: d["decisions"][0]["same_source_alias"].update(
                evidence_path="C:\\outside\\evidence.md"
            ),
            "inside docs/field_verification",
        ),
    ],
)
def test_source_contract_rejects_unsafe_same_source_alias_evidence(
    change, match, tmp_path, monkeypatch
):
    verify_dir = tmp_path / "docs" / "field_verification"
    evidence_path = verify_dir / "research" / "alias_evidence.md"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text("reviewed alias evidence\n", encoding="utf-8")
    monkeypatch.setattr(adjudication_module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    registry, document = _same_source_alias_conflict_inputs(evidence_path)
    change(document)

    with pytest.raises(ValueError, match=match):
        apply_source_contract_adjudications(
            registry, document, "adjudications/source_contract_review.json"
        )


def test_source_contract_rejects_unverified_same_source_alias_anchor(tmp_path, monkeypatch):
    verify_dir = tmp_path / "docs" / "field_verification"
    evidence_path = verify_dir / "research" / "alias_evidence.md"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text("reviewed alias evidence\n", encoding="utf-8")
    monkeypatch.setattr(adjudication_module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    registry, document = _same_source_alias_conflict_inputs(evidence_path)
    next(row for row in registry["source_fields"] if row["code"] == "raw.value")[
        "status"
    ] = "candidate"

    with pytest.raises(ValueError, match="anchor must already be verified"):
        apply_source_contract_adjudications(
            registry, document, "adjudications/source_contract_review.json"
        )


def test_source_contract_rejects_missing_same_source_alias_evidence(tmp_path, monkeypatch):
    verify_dir = tmp_path / "docs" / "field_verification"
    evidence_path = verify_dir / "research" / "missing_evidence.md"
    evidence_path.parent.mkdir(parents=True)
    monkeypatch.setattr(adjudication_module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    registry, document = _same_source_alias_conflict_inputs(evidence_path)

    with pytest.raises(ValueError, match="evidence file does not exist"):
        apply_source_contract_adjudications(
            registry, document, "adjudications/source_contract_review.json"
        )


def test_source_contract_rejects_same_source_alias_metadata_mismatch(tmp_path, monkeypatch):
    verify_dir = tmp_path / "docs" / "field_verification"
    evidence_path = verify_dir / "research" / "alias_evidence.md"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text("reviewed alias evidence\n", encoding="utf-8")
    monkeypatch.setattr(adjudication_module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    registry, document = _same_source_alias_conflict_inputs(evidence_path)
    document["decisions"][0]["meaning"] = "不同字段含义"

    with pytest.raises(ValueError, match="meaning and unit must match"):
        apply_source_contract_adjudications(
            registry, document, "adjudications/source_contract_review.json"
        )


@pytest.mark.parametrize(
    "change",
    [
        lambda target: target.update(attribute_conflicts={"meaning": ["甲", "乙"]}),
        lambda target: target["status_evidence"].update(
            reference_statuses=["verified", "unverified"]
        ),
        lambda target: target["status_evidence"].update(registry_aggregate_status="conflict"),
        lambda target: target["reference_evidence"][0].update(status=[]),
        lambda target: target.update(reference_evidence=["verified"]),
    ],
)
def test_source_contract_rejects_real_or_unclassified_status_conflict(change):
    registry, document = _source_contract_inputs()
    target, _ = _set_status_only_conflict(registry, document)
    change(target)

    with pytest.raises(ValueError, match="cannot resolve semantic or attribute conflicts"):
        apply_source_contract_adjudications(
            registry, document, "adjudications/source_contract_review.json"
        )


def test_source_contract_corrects_established_metadata_only_with_explicit_snapshot():
    registry, document = _source_contract_inputs()
    target = registry["source_fields"][0]
    target["meaning"] = "旧登记释义"
    decision = document["decisions"][0]
    decision["previous"]["meaning"] = "旧登记释义"
    decision["metadata_correction"] = {
        "previous": {"canonical": "", "meaning": "旧登记释义", "unit": ""},
        "updated": {
            "canonical": "market.metric",
            "meaning": "由上游接口契约确认的字段含义",
            "unit": "元",
        },
        "rationale": "官方字段表纠正历史释义，并逐项记录了变更前后值。",
    }

    updated, stats = apply_source_contract_adjudications(
        registry, document, "adjudications/source_contract_review.json"
    )

    target = next(row for row in updated["source_fields"] if row["source"] == "target-source")
    assert target["meaning"] == "由上游接口契约确认的字段含义"
    assert target["adjudications"][0]["metadata_correction"]["previous"]["meaning"] == (
        "旧登记释义"
    )
    assert stats["metadata_corrected"] == 1


def test_cli_previews_source_contract_without_collision_report_or_file_changes(
    tmp_path, monkeypatch, capsys
):
    registry, document = _source_contract_inputs()
    verify_dir = tmp_path / "docs" / "field_verification"
    decisions_dir = verify_dir / "adjudications"
    decisions_dir.mkdir(parents=True)
    registry_path = verify_dir / "field_registry.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    decision_path = decisions_dir / "source_contract.json"
    decision_path.write_text(json.dumps(document), encoding="utf-8")

    monkeypatch.setattr(adjudication_module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    monkeypatch.setattr(adjudication_module, "REGISTRY_PATH", registry_path)
    monkeypatch.setattr(adjudication_module, "LINEAGE_PATH", verify_dir / "source_lineage.json")
    monkeypatch.setattr(
        adjudication_module.sla,
        "load_source_lineage",
        lambda *args, **kwargs: pytest.fail("source-contract preview must not load lineage"),
    )
    original_registry = registry_path.read_bytes()

    result = adjudication_module.main(["--decisions", str(decision_path)])

    assert result == 0
    assert '"source_contract_verified": 1' in capsys.readouterr().out
    assert registry_path.read_bytes() == original_registry


def test_cli_applies_source_contract_and_loads_lineage_for_generated_view(tmp_path, monkeypatch):
    registry, document = _source_contract_inputs()
    verify_dir = tmp_path / "docs" / "field_verification"
    decisions_dir = verify_dir / "adjudications"
    decisions_dir.mkdir(parents=True)
    registry_path = verify_dir / "field_registry.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    decision_path = decisions_dir / "source_contract.json"
    decision_path.write_text(json.dumps(document), encoding="utf-8")
    monkeypatch.setattr(adjudication_module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    monkeypatch.setattr(adjudication_module, "REGISTRY_PATH", registry_path)
    monkeypatch.setattr(adjudication_module, "LINEAGE_PATH", verify_dir / "source_lineage.json")
    lineage = {"sources": {}}
    lineage_calls = []

    def load_lineage(*args, **kwargs):
        lineage_calls.append((args, kwargs))
        return lineage

    captured_outputs = {}
    monkeypatch.setattr(adjudication_module.sla, "load_source_lineage", load_lineage)
    monkeypatch.setattr(adjudication_module.gfd, "render_field_dict", lambda _registry: "dict\n")
    monkeypatch.setattr(
        adjudication_module.gfd, "render_unknown_fields", lambda _registry: "unknown\n"
    )
    monkeypatch.setattr(
        adjudication_module.gfd,
        "render_source_repository_map",
        lambda _registry, rendered_lineage: (
            "source map\n" if rendered_lineage is lineage else pytest.fail("wrong lineage")
        ),
    )
    monkeypatch.setattr(
        adjudication_module.gfd,
        "render_field_metadata_gaps",
        lambda _registry: "metadata gaps\n",
    )
    monkeypatch.setattr(
        adjudication_module.gfd,
        "render_field_aggregate_review",
        lambda _registry: "aggregate review\n",
    )
    monkeypatch.setattr(adjudication_module, "_atomic_write_batch", captured_outputs.update)

    result = adjudication_module.main(["--decisions", str(decision_path), "--apply"])

    assert result == 0
    assert len(lineage_calls) == 1
    updated = json.loads(captured_outputs[registry_path])
    target = next(row for row in updated["source_fields"] if row["source"] == "target-source")
    assert target["status"] == "verified"
    assert captured_outputs[adjudication_module.SOURCE_MAP_PATH] == "source map\n"
    assert captured_outputs[adjudication_module.AGGREGATE_REVIEW_PATH] == "aggregate review\n"


def test_cli_idempotent_source_contract_repairs_missing_matrix_projection(
    tmp_path, monkeypatch, capsys
):
    registry, document = _source_contract_inputs()
    registry, _ = apply_source_contract_adjudications(
        registry, document, "adjudications/source_contract.json"
    )
    registry["field_matrix"].pop("market.metric")
    verify_dir = tmp_path / "docs" / "field_verification"
    decisions_dir = verify_dir / "adjudications"
    decisions_dir.mkdir(parents=True)
    registry_path = verify_dir / "field_registry.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    decision_path = decisions_dir / "source_contract.json"
    decision_path.write_text(json.dumps(document), encoding="utf-8")
    monkeypatch.setattr(adjudication_module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    monkeypatch.setattr(adjudication_module, "REGISTRY_PATH", registry_path)
    monkeypatch.setattr(
        adjudication_module, "FIELD_MATRIX_PATH", tmp_path / "docs" / "field_matrix.md"
    )
    monkeypatch.setattr(adjudication_module, "LINEAGE_PATH", verify_dir / "source_lineage.json")
    monkeypatch.setattr(
        adjudication_module.sla, "load_source_lineage", lambda *a, **k: {"sources": {}}
    )
    monkeypatch.setattr(adjudication_module.gfd, "render_field_dict", lambda _registry: "dict\n")
    monkeypatch.setattr(
        adjudication_module.gfd, "render_unknown_fields", lambda _registry: "unknown\n"
    )
    monkeypatch.setattr(
        adjudication_module.gfd,
        "render_source_repository_map",
        lambda _registry, _lineage: "source map\n",
    )
    monkeypatch.setattr(
        adjudication_module.gfd, "render_field_metadata_gaps", lambda _registry: "metadata gaps\n"
    )
    monkeypatch.setattr(
        adjudication_module.gfd,
        "render_field_aggregate_review",
        lambda _registry: "aggregate review\n",
    )
    monkeypatch.setattr(
        adjudication_module.gfm, "render_document", lambda _sources, _records: "field matrix\n"
    )
    captured_outputs = {}
    monkeypatch.setattr(adjudication_module, "_atomic_write_batch", captured_outputs.update)

    result = adjudication_module.main(["--decisions", str(decision_path), "--apply"])

    assert result == 0
    assert '"already_applied": 1' in capsys.readouterr().out
    updated = json.loads(captured_outputs[registry_path])
    assert updated["field_matrix"]["market.metric"] == ["target-source"]
    assert captured_outputs[adjudication_module.FIELD_MATRIX_PATH] == "field matrix\n"


@pytest.mark.parametrize(
    "change,match",
    [
        (
            lambda d: d["decisions"][0]["source_contract"].update(revision="latest"),
            "pinned version",
        ),
        (
            lambda d: d["decisions"][0]["source_contract"].update(url="http://example.com/spec"),
            "HTTPS",
        ),
        (
            lambda d: d["decisions"][0].update(previous_status="conflict"),
            "target status changed since review",
        ),
    ],
)
def test_source_contract_rejects_unpinned_weak_or_conflicting_decisions(change, match):
    registry, document = _source_contract_inputs()
    change(document)

    with pytest.raises(ValueError, match=match):
        apply_source_contract_adjudications(
            registry, document, "adjudications/source_contract_review.json"
        )


def test_source_contract_cannot_overwrite_an_existing_meaning():
    registry, document = _source_contract_inputs()
    target = registry["source_fields"][0]
    target["meaning"] = "已经登记的有效含义"
    document["decisions"][0]["previous"]["meaning"] = "已经登记的有效含义"

    with pytest.raises(ValueError, match="cannot overwrite established meaning"):
        apply_source_contract_adjudications(
            registry, document, "adjudications/source_contract_review.json"
        )


def _empirical_source_semantics_inputs(tmp_path, *, verified=False):
    verify_dir = tmp_path / "docs" / "field_verification"
    evidence_path = verify_dir / "adjudications" / "e3_evidence.md"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text("已逐项对照来源样本与公开财报。\n", encoding="utf-8")
    record = {
        "source": "target-source",
        "code": "finance.value",
        "identity": "target-source::finance.value",
        "canonical": "old_metric" if verified else "",
        "meaning": "旧释义" if verified else "",
        "unit": "万元" if verified else "",
        "section": "old reference" if verified else "",
        "sections": ["old reference"] if verified else [],
        "status": "verified" if verified else "unverified",
        "status_resolution": "matched" if verified else "registry_status_only_single_source",
        "status_evidence": {"values": ["verified" if verified else "unverified"]},
        "reference_evidence": [],
        "attribute_conflicts": {},
    }
    registry = {
        "meta": {},
        "sources": [],
        "mappings": [],
        "fields": [{"code": "finance.value"}],
        "source_fields": [record],
    }
    evidence_rel = "docs/field_verification/adjudications/e3_evidence.md"
    document = {
        "schema_version": 1,
        "evidence_basis": "empirical_source_field_semantics",
        "reviewer": "reviewer",
        "reviewed_on": "2026-11-11",
        "evidence_file": evidence_rel,
        "evidence_sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
        "decisions": [
            {
                "id": "20261111-e3-source-field",
                "action": "verify_empirical_source_semantics",
                "target": {"source": "target-source", "code": "finance.value"},
                "previous_status": record["status"],
                "previous_status_resolution": record["status_resolution"],
                "previous": {
                    "canonical": record["canonical"],
                    "meaning": record["meaning"],
                    "unit": record["unit"],
                },
                "canonical": "prior_year_profit",
                "meaning": "上年同期归母净利润",
                "unit": "元",
                "section": "E3 来源内实证定案",
                "rationale": "同一报告期的全部可比样本均吻合，且无反例。",
                "sample": {
                    "scope": "一个报告期内全部可比股票",
                    "comparison_count": 1,
                    "matched_count": 1,
                    "counterexample_count": 0,
                    "official_report_count": 1,
                },
            }
        ],
    }
    return registry, document, verify_dir


def test_empirical_source_semantics_accepts_one_complete_sample_and_corrects_metadata(
    tmp_path, monkeypatch
):
    registry, document, verify_dir = _empirical_source_semantics_inputs(tmp_path, verified=True)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)

    updated, stats = apply_empirical_source_semantics_adjudications(
        registry, document, "adjudications/e3.json", repo_root=tmp_path
    )

    row = updated["source_fields"][0]
    assert stats["empirical_source_semantics_verified"] == 1
    assert stats["empirical_metadata_corrected"] == 1
    assert row["status"] == "verified"
    assert row["status_resolution"] == "verified_by_empirical_addendum"
    assert row["meaning"] == "上年同期归母净利润"
    assert row["unit"] == "元"
    assert row["adjudications"][0]["evidence_level"] == "E3"
    assert updated["mappings"] == []

    legacy_row = copy.deepcopy(row)
    legacy_row.update(
        {
            "code": "legacy.finance.value",
            "identity": "target-source::legacy.finance.value",
            "canonical": "legacy_verified_metric",
            "meaning": "已有 E3 定案释义",
            "adjudications": [
                {
                    "id": "legacy-e3-decision",
                    "action": "empirical_semantic_adjudication",
                    "status": "verified",
                    "level": "E3",
                }
            ],
            "status_evidence": {
                "evidence_basis": "empirical_source_field_semantics",
                "evidence_level": "E3",
            },
        }
    )
    updated["source_fields"].append(legacy_row)
    updated["field_matrix"].pop("legacy_verified_metric", None)

    repaired, repeat_stats = apply_empirical_source_semantics_adjudications(
        updated, document, "adjudications/e3.json", repo_root=tmp_path
    )

    assert repeat_stats["already_applied"] == 1
    assert repaired["field_matrix"]["prior_year_profit"] == ["target-source"]
    assert repaired["field_matrix"]["legacy_verified_metric"] == ["target-source"]


def test_empirical_source_semantics_removes_explicit_stale_matrix_projection(tmp_path, monkeypatch):
    registry, document, verify_dir = _empirical_source_semantics_inputs(tmp_path)
    registry["field_matrix"] = {"eps_deduct_ttm(f108)": ["stale-fuyao"]}
    decision = document["decisions"][0]
    decision.update(
        {
            "canonical": "eps_ttm(f108)",
            "meaning": "归母净利润 TTM 按总股本折算的每股收益",
            "unit": "元/股",
            "matrix_projection_removals": [
                {"canonical": "eps_deduct_ttm(f108)", "source": "stale-fuyao"}
            ],
        }
    )
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)

    updated, stats = apply_empirical_source_semantics_adjudications(
        registry, document, "adjudications/e3.json", repo_root=tmp_path
    )

    assert stats["empirical_source_semantics_verified"] == 1
    assert "eps_deduct_ttm(f108)" not in updated["field_matrix"]
    assert updated["field_matrix"]["eps_ttm(f108)"] == ["target-source"]
    assert updated["source_fields"][0]["adjudications"][0]["matrix_projection_removals"] == [
        {"canonical": "eps_deduct_ttm(f108)", "source": "stale-fuyao"}
    ]

    replayed, replay_stats = apply_empirical_source_semantics_adjudications(
        updated, document, "adjudications/e3.json", repo_root=tmp_path
    )

    assert replay_stats["already_applied"] == 1
    assert replayed["field_matrix"] == updated["field_matrix"]


def test_empirical_source_evidence_followup_preserves_verified_metadata(tmp_path, monkeypatch):
    registry, first_document, verify_dir = _empirical_source_semantics_inputs(tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)

    updated, _ = apply_empirical_source_semantics_adjudications(
        registry, first_document, "adjudications/e3.json", repo_root=tmp_path
    )

    evidence_path = verify_dir / "adjudications" / "e3_followup.md"
    evidence_path.write_text(
        "补充 E3 证据支持既有来源内释义，不改变字段元数据。\n", encoding="utf-8"
    )
    evidence_rel = "docs/field_verification/adjudications/e3_followup.md"
    followup = copy.deepcopy(first_document)
    followup["evidence_file"] = evidence_rel
    followup["evidence_sha256"] = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    followup["decisions"][0].update(
        {
            "id": "20261111-e3-source-field-followup",
            "action": "append_empirical_source_evidence",
            "previous_status": "verified",
            "previous_status_resolution": "verified_by_empirical_addendum",
            "previous": {
                "canonical": "prior_year_profit",
                "meaning": "上年同期归母净利润",
                "unit": "元",
            },
            "canonical": "prior_year_profit",
            "meaning": "上年同期归母净利润",
            "unit": "元",
            "section": "E3 补充证据",
            "rationale": "新增的完整样本支持既有释义，不改变规范名、含义或单位。",
            "sample": {
                "scope": "同一报告期内新增的两个可比样本",
                "comparison_count": 2,
                "matched_count": 2,
                "counterexample_count": 0,
                "official_report_count": 1,
            },
        }
    )

    applied, stats = apply_empirical_source_semantics_adjudications(
        updated, followup, "adjudications/e3_followup.json", repo_root=tmp_path
    )

    row = applied["source_fields"][0]
    assert stats["empirical_source_evidence_appended"] == 1
    assert row["status"] == "verified"
    assert row["status_resolution"] == "verified_by_empirical_addendum"
    assert (row["canonical"], row["meaning"], row["unit"]) == (
        "prior_year_profit",
        "上年同期归母净利润",
        "元",
    )
    assert [item["action"] for item in row["adjudications"]] == [
        "verify_empirical_source_semantics",
        "append_empirical_source_evidence",
    ]
    assert row["status_evidence"]["evidence_file"] == "adjudications/e3_followup.md"
    assert row["status_evidence"]["adjudication_ids"] == [
        "20261111-e3-source-field",
        "20261111-e3-source-field-followup",
    ]

    replayed, replay_stats = apply_empirical_source_semantics_adjudications(
        applied, followup, "adjudications/e3_followup.json", repo_root=tmp_path
    )
    assert replay_stats["already_applied"] == 1
    assert replayed == applied


def test_empirical_source_evidence_followup_rejects_metadata_changes(tmp_path, monkeypatch):
    registry, first_document, verify_dir = _empirical_source_semantics_inputs(tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    updated, _ = apply_empirical_source_semantics_adjudications(
        registry, first_document, "adjudications/e3.json", repo_root=tmp_path
    )
    followup = copy.deepcopy(first_document)
    followup["decisions"][0].update(
        {
            "id": "20261111-e3-source-field-invalid-followup",
            "action": "append_empirical_source_evidence",
            "previous_status": "verified",
            "previous_status_resolution": "verified_by_empirical_addendum",
            "previous": {
                "canonical": "prior_year_profit",
                "meaning": "上年同期归母净利润",
                "unit": "元",
            },
            "canonical": "prior_year_profit",
            "meaning": "上年同期净利润",
            "unit": "元",
        }
    )

    with pytest.raises(ValueError, match="must preserve canonical, meaning, and unit"):
        apply_empirical_source_semantics_adjudications(
            updated, followup, "adjudications/e3_followup.json", repo_root=tmp_path
        )


def test_empirical_source_semantics_rejects_counterexamples(tmp_path, monkeypatch):
    registry, document, verify_dir = _empirical_source_semantics_inputs(tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    decision = document["decisions"][0]
    decision["sample"].update(comparison_count=2, matched_count=1, counterexample_count=1)

    with pytest.raises(ValueError, match="matched_count must equal comparison_count"):
        apply_empirical_source_semantics_adjudications(
            registry, document, "adjudications/e3.json", repo_root=tmp_path
        )


def test_empirical_source_semantics_resolves_snapshotted_reference_conflicts(tmp_path, monkeypatch):
    registry, document, verify_dir = _empirical_source_semantics_inputs(tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    row = registry["source_fields"][0]
    conflicts = {"meaning": ["旧参考释义", "报告实测候选释义"]}
    row.update(
        {
            "status": "conflict",
            "status_resolution": "reference_semantic_attribute_conflict",
            "attribute_conflicts": conflicts,
            "status_evidence": {"values": ["verified"]},
        }
    )
    decision = document["decisions"][0]
    decision.update(
        {
            "previous_status": "conflict",
            "previous_status_resolution": "reference_semantic_attribute_conflict",
            "previous_attribute_conflicts": copy.deepcopy(conflicts),
        }
    )

    updated, stats = apply_empirical_source_semantics_adjudications(
        registry, document, "adjudications/e3.json", repo_root=tmp_path
    )

    resolved = updated["source_fields"][0]
    assert stats["empirical_source_semantics_verified"] == 1
    assert resolved["status"] == "verified"
    assert resolved["status_resolution"] == "verified_by_empirical_addendum"
    assert resolved["attribute_conflicts"] == {}
    assert resolved["adjudications"][0]["previous_attribute_conflicts"] == conflicts


def test_empirical_source_semantics_records_empty_attribute_conflict_snapshot(
    tmp_path, monkeypatch
):
    registry, document, verify_dir = _empirical_source_semantics_inputs(tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    row = registry["source_fields"][0]
    row.update(
        {
            "status": "conflict",
            "status_resolution": "status_conflict",
            "status_evidence": {"values": ["verified", "unverified"]},
            "attribute_conflicts": {},
        }
    )
    document["decisions"][0].update(
        {
            "previous_status": "conflict",
            "previous_status_resolution": "status_conflict",
            "previous_attribute_conflicts": {},
        }
    )

    updated, stats = apply_empirical_source_semantics_adjudications(
        registry, document, "adjudications/e3.json", repo_root=tmp_path
    )

    resolved = updated["source_fields"][0]
    assert stats["empirical_source_semantics_verified"] == 1
    assert resolved["status"] == "verified"
    assert resolved["attribute_conflicts"] == {}
    assert resolved["adjudications"][0]["previous_attribute_conflicts"] == {}


def test_empirical_source_semantics_rejects_unrecognized_conflict_resolution(tmp_path, monkeypatch):
    registry, document, verify_dir = _empirical_source_semantics_inputs(tmp_path)
    monkeypatch.setattr(adjudication_module, "VERIFY_DIR", verify_dir)
    row = registry["source_fields"][0]
    row.update(
        {
            "status": "conflict",
            "status_resolution": "source_identity_unresolved",
            "attribute_conflicts": {},
        }
    )
    decision = document["decisions"][0]
    decision.update(
        {
            "previous_status": "conflict",
            "previous_status_resolution": "source_identity_unresolved",
        }
    )

    with pytest.raises(ValueError, match="only reference-status or reference-semantic conflicts"):
        apply_empirical_source_semantics_adjudications(
            registry, document, "adjudications/e3.json", repo_root=tmp_path
        )


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
    if "L1" in report_change:
        report["actionable_L1"] = copy.deepcopy(report["L1"])
        report["report_completeness"]["sections"]["L1"]["json_record_count"] = len(report["L1"])
        report["report_completeness"]["sections"]["actionable_L1"]["json_record_count"] = len(
            report["actionable_L1"]
        )

    with pytest.raises(ValueError, match=match):
        apply_adjudications(
            registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
        )


def test_incomplete_report_cannot_be_used_for_adjudication():
    registry, lineage, document, report = _inputs()
    report["report_completeness"]["status"] = "incomplete"

    with pytest.raises(ValueError, match="report_completeness is not complete"):
        apply_adjudications(
            registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
        )


def test_report_schema_two_is_rejected_without_full_inventory_contract():
    registry, lineage, document, report = _inputs()
    report["schema_version"] = 2

    with pytest.raises(ValueError, match="expected 3"):
        apply_adjudications(
            registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
        )


def test_report_inventory_mismatch_blocks_adjudication():
    registry, lineage, document, report = _inputs()
    report["method_candidate_inventory"] = [{"left": "left.x", "right": "right.y"}]

    with pytest.raises(ValueError, match="inventory mismatch: saved_count"):
        apply_adjudications(
            registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
        )


def test_registered_mapping_revalidation_is_not_an_actionable_adjudication_candidate():
    registry, lineage, document, report = _inputs()
    report["L1"][0]["in_registry"] = True
    report["actionable_L1"] = []
    report["report_completeness"]["sections"]["actionable_L1"]["json_record_count"] = 0

    with pytest.raises(ValueError, match="found 0"):
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


def test_runtime_id_normalizes_tdx_quote_raw_and_kpl_raw_columns():
    from scripts.apply_collision_adjudications import _runtime_identity
    from scripts import source_lineage_api

    lineage = source_lineage_api.load_source_lineage()

    assert _runtime_identity("tdx.quote_raw.open", "TDX(双命名源)", lineage) == (
        "tdx",
        "open",
    )
    assert _runtime_identity("kpl.raw_columns.col_06", "开盘啦(kpl_limit_up_detail)", lineage) == (
        "kpl",
        "seal_amount",
    )
    assert _runtime_identity("kpl.raw_columns.col_11", "开盘啦(kpl_limit_up_detail)", lineage) == (
        "kpl",
        "amount",
    )
    assert _runtime_identity("kpl.raw_columns.col_04", "开盘啦(kpl_limit_up_detail)", lineage) == (
        "kpl",
        "zt_time",
    )
    assert _runtime_identity("kpl.raw_columns.col_07", "开盘啦(kpl_limit_up_detail)", lineage) == (
        "kpl",
        "max_seal",
    )
    assert _runtime_identity("kpl.raw_columns.col_08", "开盘啦(kpl_limit_up_detail)", lineage) == (
        "kpl",
        "main_inflow",
    )
    assert _runtime_identity("kpl.raw_columns.col_14", "开盘啦(kpl_limit_up_detail)", lineage) == (
        "kpl",
        "turnover_real",
    )


def test_conflict_status_cannot_be_overridden_by_collision_adjudication():
    registry, lineage, document, report = _inputs()
    registry["source_fields"][0]["status"] = "conflict"

    with pytest.raises(ValueError, match="requires separate conflict review"):
        apply_adjudications(
            registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
        )

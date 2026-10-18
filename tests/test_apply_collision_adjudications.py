import copy
import json

import pytest

from scripts import apply_collision_adjudications as adjudication_module
from scripts.apply_collision_adjudications import (
    REPO_ROOT,
    VERIFY_DIR,
    _inside_verification_dir,
    apply_adjudications,
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
    monkeypatch.setattr(adjudication_module, "_atomic_write_batch", captured_outputs.update)

    result = adjudication_module.main(["--decisions", str(decision_path), "--apply"])

    assert result == 0
    assert len(lineage_calls) == 1
    updated = json.loads(captured_outputs[registry_path])
    target = next(row for row in updated["source_fields"] if row["source"] == "target-source")
    assert target["status"] == "verified"
    assert captured_outputs[adjudication_module.SOURCE_MAP_PATH] == "source map\n"


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


def test_registered_mapping_revalidation_is_not_an_actionable_adjudication_candidate():
    registry, lineage, document, report = _inputs()
    report["L1"][0]["in_registry"] = True
    report["actionable_L1"] = []

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


def test_conflict_status_cannot_be_overridden_by_collision_adjudication():
    registry, lineage, document, report = _inputs()
    registry["source_fields"][0]["status"] = "conflict"

    with pytest.raises(ValueError, match="requires separate conflict review"):
        apply_adjudications(
            registry, lineage, document, report, "sample_report.json", "adjudications/review.json"
        )

import json
import hashlib

from scripts import field_registry_api as FRA
from scripts import source_lineage_api as SLA
from scripts import temporal_policy as TP
from scripts import collision_reporting as CREP


def test_slow_changing_semantics_can_use_samples_without_asserting_source_date():
    info = {
        "temporal_class": "slow_changing",
        "vals": {("600000", "T:20261016"): "示例证券"},
        "sample_meta": {
            ("600000", "T:20261016"): {
                "phase": "closed",
                "as_of_date_origin": "folder_inferred",
            }
        },
    }

    assert TP.l1_date_eligible(info, info["sample_meta"][("600000", "T:20261016")])
    evidence = TP.relation_date_evidence(info, info, {"T:20261016"})
    assert evidence["alignment_status"] == "semantic_only_date_unconfirmed"
    assert evidence["left"]["date_status"] == "semantic_only_date_unconfirmed"


def test_daily_and_unclassified_fields_require_source_confirmed_date():
    sample_meta = {"phase": "closed", "as_of_date_origin": "folder_inferred"}
    daily = {"temporal_class": "daily_market"}
    unclassified = {"temporal_class": "unclassified"}

    assert not TP.l1_date_eligible(daily, sample_meta)
    assert not TP.l1_date_eligible(unclassified, sample_meta)
    assert not TP.l1_date_eligible(
        daily, {"phase": "closed", "as_of_date_origin": "meta_data_date"}
    )
    assert TP.l1_date_eligible(daily, {"phase": "closed", "as_of_date_origin": "source_as_of"})


def test_periodic_fields_need_a_value_level_effective_date():
    info = {"temporal_class": "periodic_or_event"}
    base = {"phase": "closed", "as_of_date_origin": "source_as_of"}

    assert not TP.l1_date_eligible(info, base)
    assert TP.l1_date_eligible(
        info, {**base, "value_effective_date_origin": "record.report_period"}
    )


def test_policy_resolves_exact_registry_identity_through_runtime_alias(tmp_path):
    policy_path = tmp_path / "temporal_policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "policy_version": "test",
                "entries": [
                    {
                        "source": "TDX(双命名源)",
                        "code": "amount",
                        "class": "daily_market",
                        "registry_status": "verified",
                        "reason": "测试精确映射",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    registry = {
        "source_fields": [
            {"source": "TDX(双命名源)", "code": "amount", "status": "verified"},
            {"source": "TDX(双命名源)", "code": "amount_raw", "status": "verified"},
        ]
    }
    lineage = {"sources": {"TDX(双命名源)": {"runtime_aliases": ["tdx"]}}}
    store = {
        "tdx.quote_raw.amount": {"src": "tdx", "vals": {}},
        "tdx.quote_raw.amount_raw": {"src": "tdx", "vals": {}},
    }

    summary = TP.apply_store_policies(
        store, policy_path=policy_path, registry=registry, lineage=lineage
    )

    assert summary["status"] == "ok"
    assert store["tdx.quote_raw.amount"]["temporal_class"] == "daily_market"
    assert store["tdx.quote_raw.amount"]["temporal_policy_identity"] == {
        "source": "TDX(双命名源)",
        "code": "amount",
    }
    assert store["tdx.quote_raw.amount_raw"]["temporal_class"] == "unclassified"


def test_policy_registry_status_drift_fails_closed(tmp_path):
    policy_path = tmp_path / "temporal_policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "entries": [
                    {
                        "source": "Source A",
                        "code": "field",
                        "class": "static_reference",
                        "registry_status": "verified",
                        "reason": "test",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    store = {"runtime.field": {"src": "runtime", "vals": {}}}

    summary = TP.apply_store_policies(
        store,
        policy_path=policy_path,
        registry={
            "source_fields": [{"source": "Source A", "code": "field", "status": "unverified"}]
        },
        lineage={"sources": {"Source A": {"runtime_aliases": ["runtime"]}}},
    )

    assert summary["status"] == "invalid"
    assert store["runtime.field"]["temporal_class"] == "unclassified"
    assert summary["diagnostics"]


def test_repository_temporal_policy_resolves_against_exact_registry_records():
    policy = TP.load_policy()
    runtime_index = TP.build_runtime_policy_index(
        policy, FRA.load_registry(), SLA.load_source_lineage()
    )

    assert len(runtime_index) == len(policy["entries"])


def test_report_explains_semantic_only_l1_without_claiming_date_confirmation():
    markdown = CREP.append_temporal_evidence_report(
        "# Collision",
        [
            {
                "left": "unknown.name",
                "right": "ftshare_rest.name",
                "temporal_evidence": {
                    "alignment_status": "semantic_only_date_unconfirmed",
                    "left": {
                        "temporal_class": "unclassified",
                        "date_status": "source_date_confirmed",
                    },
                    "right": {
                        "temporal_class": "slow_changing",
                        "date_status": "semantic_only_date_unconfirmed",
                    },
                },
            }
        ],
        [],
        {"status": "ok", "classified_fields": 1, "unclassified_fields": 1},
    )

    assert "semantic_only_date_unconfirmed" in markdown
    assert "不证明数据新鲜度" in markdown
    assert "`unknown.name` ↔ `ftshare_rest.name`" in markdown


def _cross_source_value_witness_fixture(tmp_path, *, values_match=True, all_zero=False):
    tmp_path.mkdir(parents=True, exist_ok=True)
    evidence_path = tmp_path / "witness.json"
    evidence_path.write_text('{"audit": true}', encoding="utf-8")
    evidence_sha256 = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    target_source = "Target Source"
    anchor_source = "Anchor Source"
    target_code = "field"
    anchor_code = "[10]"
    thresholds = {
        "min_distinct_days": 2,
        "min_pairs": 4,
        "min_nonzero_pairs": 4,
        "min_daily_pairs": 2,
        "min_daily_nonzero_pairs": 2,
        "min_unique_nonzero_values": 4,
        "min_exact_ratio": 1.0,
        "min_nonzero_exact_ratio": 1.0,
        "min_daily_exact_ratio": 1.0,
        "min_daily_nonzero_exact_ratio": 1.0,
    }
    witness = {
        "source": target_source,
        "code": target_code,
        "runtime_paths": [target_code],
        "witness_source": anchor_source,
        "witness_code": anchor_code,
        "witness_runtime_path": anchor_code,
        "evidence_file": evidence_path.name,
        "evidence_sha256": evidence_sha256,
        "reason": "fixture evidence",
        "thresholds": thresholds,
    }
    policy_path = tmp_path / "temporal_policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "policy_version": "test",
                "entries": [
                    {
                        "source": target_source,
                        "code": target_code,
                        "class": "daily_market",
                        "reason": "test target volatility",
                    }
                ],
                "cross_source_value_witnesses": [witness],
            }
        ),
        encoding="utf-8",
    )
    registry = {
        "source_fields": [
            {"source": target_source, "code": target_code, "status": "unverified"},
            {
                "source": anchor_source,
                "code": anchor_code,
                "status": "verified",
            },
        ]
    }
    lineage = {
        "sources": {
            target_source: {"runtime_aliases": ["tdx"]},
            anchor_source: {"runtime_aliases": ["tencent"]},
        },
        "runtime_sources": {
            "tdx": {
                "independence_status": "confirmed",
                "independence_family": "tdx",
            },
            "tencent": {
                "independence_status": "confirmed",
                "independence_family": "tencent",
            },
        },
    }
    target_values = {}
    anchor_values = {}
    target_meta = {}
    anchor_meta = {}
    for day_index, (day, date_text) in enumerate(
        (("T:20261016", "2026-10-16"), ("T:20261019", "2026-10-19")),
        start=1,
    ):
        for index, code in enumerate(("600000", "000001"), start=1):
            key = (code, day)
            anchor_value = 0 if all_zero else day_index * 100 + index
            target_value = anchor_value if values_match else anchor_value + 1
            target_values[key] = target_value
            anchor_values[key] = anchor_value
            target_meta[key] = {
                "phase": "closed",
                "as_of_date": date_text,
                "as_of_date_origin": "meta_data_date",
            }
            anchor_meta[key] = {
                "phase": "closed",
                "as_of_date": date_text,
                "as_of_date_origin": "source_as_of",
            }
    store = {
        "tdx.field": {
            "src": "tdx",
            "vals": target_values,
            "sample_meta": target_meta,
        },
        "tencent[10]": {
            "src": "tencent",
            "vals": anchor_values,
            "sample_meta": anchor_meta,
        },
    }
    return policy_path, registry, lineage, store


def test_cross_source_value_witness_confirms_only_exact_multiday_nonzero_samples(tmp_path):
    policy_path, registry, lineage, store = _cross_source_value_witness_fixture(tmp_path)

    summary = TP.apply_store_policies(
        store, policy_path=policy_path, registry=registry, lineage=lineage
    )

    target = store["tdx.field"]
    assert summary["status"] == "ok"
    assert (
        summary["cross_source_value_witnesses"]["by_witness"]["tdx.field <- tencent[10]"]["status"]
        == "thresholds_met"
    )
    assert all(
        metadata["as_of_date_origin"] == "cross_source_value_witness"
        for metadata in target["sample_meta"].values()
    )
    assert all(TP.l1_date_eligible(target, metadata) for metadata in target["sample_meta"].values())
    relation = TP.relation_date_evidence(target, store["tencent[10]"], {"T:20261016", "T:20261019"})
    assert relation["alignment_status"] == "cross_source_dates_inferred"
    assert relation["left"]["date_status"] == "cross_source_date_inferred"


def test_cross_source_value_witness_does_not_promote_mismatches_or_zero_only_pairs(
    tmp_path,
):
    policy_path, registry, lineage, mismatched_store = _cross_source_value_witness_fixture(
        tmp_path / "mismatch", values_match=False
    )
    mismatch_summary = TP.apply_store_policies(
        mismatched_store,
        policy_path=policy_path,
        registry=registry,
        lineage=lineage,
    )
    assert (
        mismatch_summary["cross_source_value_witnesses"]["by_witness"]["tdx.field <- tencent[10]"][
            "status"
        ]
        == "thresholds_not_met"
    )
    assert all(
        metadata["as_of_date_origin"] == "meta_data_date"
        for metadata in mismatched_store["tdx.field"]["sample_meta"].values()
    )

    zero_path, zero_registry, zero_lineage, zero_store = _cross_source_value_witness_fixture(
        tmp_path / "zero", all_zero=True
    )
    zero_summary = TP.apply_store_policies(
        zero_store, policy_path=zero_path, registry=zero_registry, lineage=zero_lineage
    )
    assert (
        zero_summary["cross_source_value_witnesses"]["by_witness"]["tdx.field <- tencent[10]"][
            "status"
        ]
        == "thresholds_not_met"
    )
    assert all(
        metadata["as_of_date_origin"] == "meta_data_date"
        for metadata in zero_store["tdx.field"]["sample_meta"].values()
    )

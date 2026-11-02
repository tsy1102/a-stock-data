import json

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

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
    assert not TP.l1_date_eligible(
        info,
        {
            **base,
            "as_of_date_origin": "same_source_row_date_witness",
            "same_source_row_date_witness": {
                "date": "20261118",
                "validated": True,
                "source": "Source",
                "code": "date",
            },
            "as_of_date": "20261118",
        },
    )
    assert TP.l1_date_eligible(
        info, {**base, "value_effective_date_origin": "record.report_period"}
    )


def _row_date_witness_fixture(
    tmp_path, *, row_date=20261118, timestamp_date=None, target_as_of_date="20261118"
):
    source = "东财-ulist239(np/get)"
    tmp_path.mkdir(parents=True, exist_ok=True)
    policy_path = tmp_path / "temporal_policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "policy_version": "test-row-date-witness",
                "entries": [
                    {
                        "source": source,
                        "code": "f2",
                        "class": "daily_market",
                        "registry_status": "verified",
                        "reason": "测试行情值日期资格",
                    }
                ],
                "row_date_witnesses": [
                    {
                        "source": source,
                        "code": "f297",
                        "date_format": "YYYYMMDD",
                        "unit": "YYYYMMDD（整数）",
                        "meaning_contains": "当前 Ulist239 行情记录对应的交易日期",
                        "reason": "同一 Ulist239 证券行日期见证测试",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    registry = {
        "source_fields": [
            {
                "source": source,
                "code": "f297",
                "status": "verified",
                "unit": "YYYYMMDD（整数）",
                "meaning": "该证券当前 Ulist239 行情记录对应的交易日期",
            },
            {
                "source": source,
                "code": "f2",
                "status": "verified",
                "unit": "元",
                "meaning": "现价",
            },
        ]
    }
    lineage = {"sources": {source: {"runtime_aliases": ["ulist239"]}}}
    key = ("600000", "T:20261118")
    anchor_meta = {
        "phase": "closed",
        "as_of_date": "20261118",
        "as_of_date_origin": "folder_inferred",
        "capture_folder": "capture-20261118",
    }
    target_meta = dict(anchor_meta)
    if target_as_of_date is None:
        target_meta.pop("as_of_date")
    else:
        target_meta["as_of_date"] = target_as_of_date
    if timestamp_date is not None:
        target_meta["row_timestamp_witness"] = {"timestamp_date": timestamp_date}
    store = {
        "ulist239.f297": {
            "src": "ulist239",
            "vals": {key: row_date},
            "sample_meta": {key: anchor_meta},
        },
        "ulist239.f2": {
            "src": "ulist239",
            "vals": {key: 10.25},
            "sample_meta": {key: target_meta},
        },
    }
    return policy_path, registry, lineage, store, key


def test_same_source_row_date_witness_infers_sibling_field_date(tmp_path):
    policy_path, registry, lineage, store, key = _row_date_witness_fixture(tmp_path)

    summary = TP.apply_store_policies(
        store, policy_path=policy_path, registry=registry, lineage=lineage
    )

    target = store["ulist239.f2"]
    metadata = target["sample_meta"][key]
    assert summary["status"] == "ok"
    assert (
        summary["row_date_witnesses"]["by_source"]["东财-ulist239(np/get)"]["date_confirmed_rows"]
        == 1
    )
    assert metadata["as_of_date_origin"] == "same_source_row_date_witness"
    assert metadata["same_source_row_date_witness"]["validated"] is True
    assert TP.l1_date_eligible(target, metadata)
    relation = TP.relation_date_evidence(target, target, {"T:20261118"})
    assert relation["left"]["date_status"] == "same_source_date_inferred"
    assert relation["alignment_status"] == "same_source_dates_inferred"


def test_same_source_row_date_witness_fills_missing_sibling_date(tmp_path):
    policy_path, registry, lineage, store, key = _row_date_witness_fixture(
        tmp_path, target_as_of_date=None
    )

    TP.apply_store_policies(store, policy_path=policy_path, registry=registry, lineage=lineage)

    metadata = store["ulist239.f2"]["sample_meta"][key]
    assert metadata["as_of_date"] == "20261118"
    assert metadata["as_of_date_origin"] == "same_source_row_date_witness"
    assert TP.l1_date_eligible(store["ulist239.f2"], metadata)


def test_same_source_row_date_witness_requires_same_capture_batch(tmp_path):
    policy_path, registry, lineage, store, key = _row_date_witness_fixture(tmp_path)
    store["ulist239.f2"]["sample_meta"][key]["capture_folder"] = "capture-20261119"

    TP.apply_store_policies(store, policy_path=policy_path, registry=registry, lineage=lineage)

    metadata = store["ulist239.f2"]["sample_meta"][key]
    assert metadata["as_of_date_origin"] == "folder_inferred"
    assert "same_source_row_date_witness" not in metadata
    assert not TP.l1_date_eligible(store["ulist239.f2"], metadata)


def test_same_source_row_date_witness_rejects_wrong_date_and_anchor_conflicts(tmp_path):
    policy_path, registry, lineage, wrong_day_store, key = _row_date_witness_fixture(
        tmp_path / "wrong-day", row_date=20261117
    )
    wrong_day_store["ulist239.f2"]["sample_meta"][key]["as_of_date_origin"] = "source_as_of"
    summary = TP.apply_store_policies(
        wrong_day_store, policy_path=policy_path, registry=registry, lineage=lineage
    )
    metadata = wrong_day_store["ulist239.f2"]["sample_meta"][key]
    assert (
        summary["row_date_witnesses"]["by_source"]["东财-ulist239(np/get)"]["date_mismatch_rows"]
        == 1
    )
    assert metadata["same_source_row_date_witness"]["validated"] is False
    assert metadata["as_of_date_origin"] == "same_source_row_date_conflict"
    assert not TP.l1_date_eligible(wrong_day_store["ulist239.f2"], metadata)

    conflict_path, conflict_registry, conflict_lineage, conflict_store, conflict_key = (
        _row_date_witness_fixture(tmp_path / "timestamp-conflict", timestamp_date="20261117")
    )
    TP.apply_store_policies(
        conflict_store,
        policy_path=conflict_path,
        registry=conflict_registry,
        lineage=conflict_lineage,
    )
    conflict_metadata = conflict_store["ulist239.f2"]["sample_meta"][conflict_key]
    assert conflict_metadata["same_source_row_date_witness"]["validated"] is False
    assert not TP.l1_date_eligible(conflict_store["ulist239.f2"], conflict_metadata)


def test_row_timestamp_witness_requires_same_capture_folder(tmp_path):
    source = "东财-push2(stock/get)"
    key = ("600519", "T:20261118")
    policy_path = tmp_path / "temporal_policy.json"
    policy_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "policy_version": "test-row-timestamp-witness",
                "entries": [],
                "row_timestamp_witnesses": [
                    {
                        "source": source,
                        "code": "f86",
                        "timestamp_format": "unix_seconds",
                        "unit": "Unix 秒",
                        "meaning_contains": "当日收盘/最后行情时间戳",
                        "reason": "同记录日期测试",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    registry = {
        "source_fields": [
            {
                "source": source,
                "code": "f86",
                "status": "verified",
                "unit": "Unix 秒",
                "meaning": "当日收盘/最后行情时间戳",
            }
        ]
    }
    lineage = {"sources": {source: {"runtime_aliases": ["push2"]}}}
    anchor_meta = {
        "phase": "closed",
        "as_of_date": "20261118",
        "as_of_date_origin": "folder_inferred",
        "capture_folder": "capture-20261118-a",
    }
    same_batch_meta = dict(anchor_meta)
    other_batch_meta = {**anchor_meta, "capture_folder": "capture-20261118-b"}
    store = {
        "push2.f86": {
            "src": "push2",
            "vals": {key: 1794989513},
            "sample_meta": {key: anchor_meta},
        },
        "push2.f59": {
            "src": "push2",
            "vals": {key: 1460.21},
            "sample_meta": {key: same_batch_meta},
        },
        "push2.f60": {
            "src": "push2",
            "vals": {key: 1442.66},
            "sample_meta": {key: other_batch_meta},
        },
    }

    summary = TP.apply_store_policies(
        store, policy_path=policy_path, registry=registry, lineage=lineage
    )

    same_metadata = store["push2.f59"]["sample_meta"][key]
    other_metadata = store["push2.f60"]["sample_meta"][key]
    assert same_metadata["as_of_date_origin"] == "record.timestamp"
    assert same_metadata["row_timestamp_witness"]["timestamp_date"] == "20261118"
    assert other_metadata["as_of_date_origin"] == "folder_inferred"
    assert "row_timestamp_witness" not in other_metadata
    assert (
        summary["row_timestamp_witnesses"]["by_source"][source][
            "field_samples_skipped_other_capture_folder"
        ]
        == 1
    )


def test_parse_row_date_requires_exact_valid_yyyymmdd():
    assert TP.parse_row_date(20261118, "YYYYMMDD").strftime("%Y%m%d") == "20261118"
    assert TP.parse_row_date("20260230", "YYYYMMDD") is None
    assert TP.parse_row_date(20261118.0, "YYYYMMDD") is None


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
    date_witness_index = TP.build_runtime_date_witness_index(
        policy, FRA.load_registry(), SLA.load_source_lineage()
    )

    assert len(runtime_index) == len(policy["entries"])
    assert date_witness_index["ulist239"]["code"] == "f297"


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
        {
            "status": "ok",
            "classified_fields": 1,
            "unclassified_fields": 1,
            "row_date_witnesses": {
                "by_source": {
                    "东财-ulist239(np/get)": {
                        "witness_rows": 2,
                        "date_confirmed_rows": 1,
                        "date_mismatch_rows": 1,
                        "invalid_date_rows": 0,
                        "field_samples_updated": 40,
                    }
                }
            },
        },
    )

    assert "semantic_only_date_unconfirmed" in markdown
    assert "不证明数据新鲜度" in markdown
    assert "same_source_dates_inferred" in markdown
    assert "| `row_date_witnesses` | `东财-ulist239(np/get)` | 2 | 1 | 1 | 0 | 40 |" in markdown
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

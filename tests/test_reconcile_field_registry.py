from scripts.reconcile_field_registry import reconcile_registry
import pytest


def _reference(source, code, statuses=()):
    return {
        "source": source,
        "code": code,
        "canonical": code,
        "meaning": "",
        "unit": "",
        "section": "",
        "sections": [],
        "evidence": [],
        "reference_statuses": list(statuses),
        "status_raw_values": [],
    }


def test_aggregate_status_is_not_distributed_to_unscoped_source_rows():
    current = {
        "meta": {},
        "fields": [
            {
                "code": "nested.value",
                "source": None,
                "sources": ["src-a", "src-b"],
                "status": "verified",
            }
        ],
        "mappings": [],
    }
    extracted = {
        "source_fields": [
            _reference("src-a", "nested.value"),
            _reference("src-b", "nested.value"),
        ]
    }

    migrated, report = reconcile_registry(current, extracted)

    assert report["union_identity_count"] == 2
    assert {record["status"] for record in migrated["source_fields"]} == {"unverified"}
    assert {record["status_resolution"] for record in migrated["source_fields"]} == {
        "aggregate_status_scope_unresolved"
    }
    assert all(
        record["status_evidence"]["registry_aggregate_status"] == "verified"
        for record in migrated["source_fields"]
    )


@pytest.mark.parametrize("aggregate_status", ["verified", "candidate", "disproved"])
def test_nonverified_aggregate_labels_are_not_distributed_to_multiple_sources(aggregate_status):
    current = {
        "meta": {},
        "fields": [
            {
                "code": "f59",
                "source": None,
                "sources": ["src-a", "src-b"],
                "status": aggregate_status,
            }
        ],
        "mappings": [],
    }
    extracted = {"source_fields": [_reference("src-a", "f59"), _reference("src-b", "f59")]}

    migrated, _ = reconcile_registry(current, extracted)

    assert {record["status"] for record in migrated["source_fields"]} == {"unverified"}
    assert {record["status_resolution"] for record in migrated["source_fields"]} == {
        "aggregate_status_scope_unresolved"
    }
    assert all(
        record["status_evidence"]["registry_aggregate_status"] == aggregate_status
        for record in migrated["source_fields"]
    )


def test_exact_source_evidence_preserves_verification_and_exposes_conflict():
    current = {
        "meta": {},
        "fields": [
            {"code": "value", "source": None, "sources": ["src-a", "src-b"], "status": "verified"}
        ],
        "mappings": [],
    }
    extracted = {
        "source_fields": [
            _reference("src-a", "value", ["unverified"]),
            _reference("src-b", "value", ["verified"]),
        ]
    }

    migrated, _ = reconcile_registry(current, extracted)
    by_source = {record["source"]: record for record in migrated["source_fields"]}

    assert by_source["src-a"]["status"] == "conflict"
    assert by_source["src-a"]["status_resolution"] == "status_conflict"
    assert by_source["src-b"]["status"] == "verified"
    assert by_source["src-b"]["status_resolution"] == "matched"
    assert migrated["fields"][0]["status"] == "conflict"


def test_conflicting_reference_rows_remain_conflict_without_guessing():
    current = {"meta": {}, "fields": [], "mappings": []}
    extracted = {"source_fields": [_reference("src-a", "value", ["verified", "unverified"])]}

    migrated, _ = reconcile_registry(current, extracted)

    field = migrated["source_fields"][0]
    assert field["status"] == "conflict"
    assert field["status_resolution"] == "reference_status_conflict"


def test_migration_does_not_mutate_input_registry():
    current = {
        "meta": {"version": 1},
        "fields": [{"code": "one", "source": "src-a", "sources": ["src-a"], "status": "verified"}],
        "mappings": [],
    }
    original = {
        key: value.copy() if isinstance(value, dict) else value for key, value in current.items()
    }

    reconcile_registry(current, {"source_fields": [_reference("src-a", "one", ["verified"])]})

    assert current == original

import pytest

from scripts import field_registry_api as registry_api


def test_source_fields_preserve_source_and_full_path_identity():
    registry = {
        "fields": [{"code": "value", "sources": ["tdx", "zhb"]}],
        "source_fields": [
            {"source": "tdx", "code": "quote.value"},
            {"source": "zhb", "code": "stat.value"},
        ],
    }

    assert registry_api.field_source_map(registry) == {
        "quote.value": {"tdx"},
        "stat.value": {"zhb"},
    }
    assert registry_api.fields_by_source(registry) == {
        "tdx": {"quote.value"},
        "zhb": {"stat.value"},
    }
    assert registry_api.record_count(registry) == 2


def test_explicit_empty_source_fields_are_authoritative():
    registry = {
        "fields": [{"code": "legacy", "sources": ["tdx"]}],
        "source_fields": [],
    }

    assert registry_api.field_source_map(registry) == {}
    assert registry_api.fields_by_source(registry) == {}
    assert registry_api.record_count(registry) == 0


def test_duplicate_source_path_identity_is_rejected():
    registry = {
        "source_fields": [
            {"source": "tdx", "code": "quote.value"},
            {"source": "tdx", "code": "quote.value"},
        ]
    }

    with pytest.raises(ValueError, match="duplicate registry.source_fields identity"):
        registry_api.source_field_records(registry)


def test_legacy_registry_without_source_fields_keeps_aggregate_fallback():
    registry = {"fields": [{"code": "value", "sources": ["tdx", "sina"]}]}

    assert registry_api.field_source_map(registry) == {"value": {"tdx", "sina"}}
    assert registry_api.fields_by_source(registry) == {"tdx": {"value"}, "sina": {"value"}}


def test_aggregate_projection_marks_same_code_different_meanings_as_ambiguous():
    source_fields = [
        {
            "source": "eastmoney.stock_get",
            "code": "f44",
            "canonical": "high_price",
            "meaning": "最高价",
            "unit": "元",
            "status": "verified",
            "status_evidence": {"reference_status_raw": ["✅"]},
        },
        {
            "source": "eastmoney.ulist_np",
            "code": "f44",
            "canonical": "total_profit",
            "meaning": "利润总额",
            "unit": "元",
            "status": "verified",
            "status_evidence": {"reference_status_raw": ["✅"]},
        },
    ]

    aggregate = registry_api.build_aggregate_fields(source_fields)[0]

    assert aggregate["source"] is None
    assert aggregate["sources"] == ["eastmoney.stock_get", "eastmoney.ulist_np"]
    assert aggregate["canonical"] == ""
    assert aggregate["meaning"] == ""
    assert aggregate["status"] == "conflict"
    assert aggregate["source_statuses"] == {
        "eastmoney.stock_get": "verified",
        "eastmoney.ulist_np": "verified",
    }
    assert aggregate["aggregation_status"] == "ambiguous"
    assert aggregate["aggregation_issues"] == ["canonical_differs", "meaning_differs"]
    assert {row["status"] for row in source_fields} == {"verified"}


def test_aggregate_projection_does_not_label_verified_blank_metadata_as_verified():
    aggregate = registry_api.build_aggregate_fields(
        [
            {
                "source": "source-a",
                "code": "missing.meaning",
                "canonical": "",
                "meaning": "",
                "unit": "",
                "status": "verified",
            }
        ]
    )[0]

    assert aggregate["status"] == "unverified"
    assert aggregate["aggregation_status"] == "incomplete"
    assert aggregate["aggregation_issues"] == ["canonical_incomplete", "meaning_incomplete"]


def test_aggregate_projection_preserves_consistent_verified_meaning():
    aggregate = registry_api.build_aggregate_fields(
        [
            {
                "source": source,
                "code": "same.meaning",
                "canonical": "last_price",
                "meaning": "最新价",
                "unit": "元",
                "status": "verified",
            }
            for source in ("source-a", "source-b")
        ]
    )[0]

    assert aggregate["canonical"] == "last_price"
    assert aggregate["meaning"] == "最新价"
    assert aggregate["status"] == "verified"
    assert aggregate["aggregation_status"] == "consistent"
    assert aggregate["aggregation_issues"] == []

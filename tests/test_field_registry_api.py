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

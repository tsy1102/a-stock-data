import copy
import hashlib
import json

from scripts import refresh_field_registry_projection as projection
from scripts.refresh_field_registry_projection import rebuild_projection


def test_rebuild_projection_changes_only_aggregate_fields_and_preserves_source_rows():
    registry = {
        "meta": {"version": 2},
        "fields": [{"code": "f44", "sources": ["source-a", "source-b"], "status": "verified"}],
        "source_fields": [
            {
                "source": "source-a",
                "code": "f44",
                "canonical": "high_price",
                "meaning": "最高价",
                "unit": "元",
                "status": "verified",
            },
            {
                "source": "source-b",
                "code": "f44",
                "canonical": "total_profit",
                "meaning": "利润总额",
                "unit": "元",
                "status": "verified",
            },
        ],
        "field_matrix": {"price": ["source-a"]},
    }
    original = copy.deepcopy(registry)

    updated, stats = rebuild_projection(registry)

    assert registry == original
    assert updated["source_fields"] == original["source_fields"]
    assert updated["meta"] == original["meta"]
    assert updated["field_matrix"] == original["field_matrix"]
    assert updated["fields"][0]["status"] == "conflict"
    assert updated["fields"][0]["aggregation_status"] == "ambiguous"
    assert stats["source_fields"] == 2
    assert stats["changed_aggregates"] == 1


def test_changed_aggregate_count_is_keyed_by_code_not_sorted_position():
    source_fields = [
        {"source": "source-a", "code": code, "status": "unverified"}
        for code in ("a-field", "b-field", "c-field")
    ]
    registry = {
        "fields": projection.fra.build_aggregate_fields(source_fields[1:]),
        "source_fields": source_fields,
    }

    _, stats = rebuild_projection(registry)

    assert stats["aggregate_fields_before"] == 2
    assert stats["aggregate_fields_after"] == 3
    assert stats["changed_aggregates"] == 1


def test_atomic_write_preserves_source_fields_and_uses_two_space_json(tmp_path, monkeypatch):
    registry = {
        "meta": {"version": 2},
        "fields": [],
        "source_fields": [
            {
                "source": "source-a",
                "code": "f44",
                "canonical": "high_price",
                "meaning": "最高价",
                "unit": "元",
                "status": "verified",
            }
        ],
    }
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(registry, ensure_ascii=False, indent=1), encoding="utf-8")
    original_digest = hashlib.sha256(path.read_bytes()).hexdigest()
    updated, _ = rebuild_projection(registry)
    monkeypatch.setattr(projection, "TEMP_DIR", str(tmp_path / "staging"))

    projection._write_atomically(str(path), updated, original_digest)

    raw = path.read_text(encoding="utf-8")
    persisted = json.loads(raw)
    assert raw.startswith('{\n  "meta":')
    assert persisted["source_fields"] == registry["source_fields"]
    assert persisted["fields"] == updated["fields"]


def test_check_flag_accepts_current_projection_without_rewriting(tmp_path):
    registry = {
        "meta": {"version": 2},
        "fields": [],
        "source_fields": [
            {
                "source": "source-a",
                "code": "f44",
                "canonical": "high_price",
                "meaning": "最高价",
                "unit": "元",
                "status": "verified",
            }
        ],
    }
    current, _ = rebuild_projection(registry)
    path = tmp_path / "registry.json"
    canonical_bytes = (json.dumps(current, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    path.write_bytes(canonical_bytes)
    original_bytes = path.read_bytes()

    assert projection.main(["--check", "--registry", str(path)]) == 0
    assert path.read_bytes() == original_bytes

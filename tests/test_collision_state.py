import json

from scripts import collision_state


def test_missing_state_uses_empty_v2_contract(tmp_path):
    state = collision_state.load_state(tmp_path / "missing.json")

    assert state == {"version": 2, "findings": {}, "warnings": []}


def test_v1_findings_are_archived_without_being_promoted(tmp_path):
    path = tmp_path / "legacy.json"
    legacy = {"version": 1, "findings": {"field": {"level": "L1"}}}
    path.write_text(json.dumps(legacy), encoding="utf-8")

    state = collision_state.load_state(path)

    assert state["version"] == 2
    assert state["findings"] == {}
    assert state["legacy_findings_v1"] == legacy["findings"]
    assert path.read_text(encoding="utf-8") == json.dumps(legacy)


def test_invalid_state_is_reported_without_overwriting_original(tmp_path):
    path = tmp_path / "invalid.json"
    original = "[]"
    path.write_text(original, encoding="utf-8")

    state = collision_state.load_state(path)

    assert state["read_error"] is True
    assert state["findings"] == {}
    assert state["warnings"]
    assert path.read_text(encoding="utf-8") == original


def test_v2_state_round_trips_through_existing_path_contract(tmp_path):
    path = tmp_path / "collision_state.json"
    state = {"version": 2, "findings": {"field": {"level": "L4"}}, "warnings": []}

    collision_state.save_state(path, state)

    assert collision_state.load_state(path) == state

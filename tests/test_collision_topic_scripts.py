from scripts import crack_push2_status_codes_20260921 as push2_topic
from scripts import crack_ulist_f88_95_20260921 as ulist_topic


def test_push2_topic_fields_preserve_snapshot_phase_for_shared_gate():
    push2_topic.SNAPSHOT_PHASES = {("push2_full", "20260929"): "unknown"}
    field = push2_topic._collision_field({"20260929": {"600000": 1.0}}, "push2_full")

    assert field["sample_meta"][("600000", "T:20260929")]["phase"] == "unknown"


def test_ulist_topic_fields_preserve_snapshot_phase_for_shared_gate():
    ulist_topic.SNAPSHOT_PHASES = {("ulist239", "20260929"): "closed"}
    field = ulist_topic._collision_field({"20260929": {"600000": 1.0}}, "ulist239")

    assert field["sample_meta"][("600000", "T:20260929")]["phase"] == "closed"

from importlib import import_module

import pytest

from scripts.crack_helpers import collision_field, parse_number


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        (10, 10.0),
        ("1,234.5%", 1234.5),
        ("", None),
        ("None", None),
        ("nan", None),
        ("NaN", None),
        ("--", None),
        ("bad", None),
        (True, 1.0),
    ],
)
def test_parse_number_preserves_archived_cracker_contract(value, expected):
    assert parse_number(value) == expected


def test_collision_field_preserves_date_keys_phases_and_constant_flag():
    phases = {("push2_full", "20261106"): "close"}

    result = collision_field(
        {"20261106": {600519: 2.5}, "20261105": {600519: 2.5}},
        "push2_full",
        phases,
    )

    assert result == {
        "vals": {("600519", "T:20261106"): 2.5, ("600519", "T:20261105"): 2.5},
        "src": "push2_full",
        "is_constant": True,
        "sample_meta": {
            ("600519", "T:20261106"): {"phase": "close", "source": "push2_full"},
            ("600519", "T:20261105"): {"phase": "unknown", "source": "push2_full"},
        },
    }


def test_archived_crackers_import_shared_helpers():
    modules = [
        import_module("scripts.crack_push2_status_codes_20260921"),
        import_module("scripts.crack_ulist_f88_95_20260921"),
        import_module("scripts.crack_zhb_anchored_20260921"),
    ]

    assert all(module.num is parse_number for module in modules)
    assert modules[0]._build_collision_field is collision_field
    assert modules[1]._build_collision_field is collision_field

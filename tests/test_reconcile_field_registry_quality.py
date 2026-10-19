from scripts.reconcile_field_registry import _effective_status


def test_verified_reference_with_missing_meaning_is_not_promoted():
    reference = {"reference_statuses": ["verified"], "meaning": ""}
    current = {"status": "verified"}

    assert _effective_status(reference, current, 1) == (
        "unverified",
        "reference_meaning_unresolved",
        ["verified"],
    )


def test_verified_reference_with_semantic_attribute_conflict_is_conflicted():
    reference = {
        "reference_statuses": ["verified"],
        "meaning": "净利润",
        "attribute_conflicts": {"unit": ["元", "万元"]},
    }
    current = {"status": "verified"}

    assert _effective_status(reference, current, 1) == (
        "conflict",
        "reference_semantic_attribute_conflict",
        ["verified"],
    )


def test_canonical_alias_difference_does_not_demote_a_clear_meaning():
    reference = {
        "reference_statuses": ["verified"],
        "meaning": "净利润",
        "attribute_conflicts": {"canonical": ["net_profit", "netProfit"]},
    }
    current = {"status": "verified"}

    assert _effective_status(reference, current, 1) == (
        "verified",
        "matched",
        ["verified"],
    )

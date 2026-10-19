from scripts import extract_registry as er


def test_grouped_meaning_aligns_by_cardinality_and_composite_unit_stays_scalar():
    tokens = ["f1", "f2"]

    attributes, ambiguities = er._row_attributes(
        "f1 / f2",
        ["f1 / f2", "行业名称/东财行业码", "元/股", "✅"],
        meaning_idx=1,
        unit_idx=2,
        tokens=tokens,
        index=1,
    )

    assert attributes == {
        "canonical": "f2",
        "meaning": "东财行业码",
        "unit": "元/股",
    }
    assert ambiguities == {}


def test_grouped_row_requires_all_tokens_to_be_registered():
    source = "东财-push2(stock/get)"

    assert er._registered_row_tokens("f1/f2", source, {(source, "f1")}) == []
    assert er._registered_row_tokens("f1/f2", source, {(source, "f1"), (source, "f2")}) == [
        "f1",
        "f2",
    ]


def test_api_path_slashes_are_not_mistaken_for_a_multi_field_row():
    source = "同花顺-fuyao"

    assert (
        er._registered_row_tokens("a-share/prices/snapshot", source, {(source, "snapshot")}) == []
    )


def test_unaligned_group_evidence_does_not_override_a_precise_field_meaning():
    evidence = [
        {"canonical": "f1", "meaning": "净利润", "unit": "元"},
        {
            "canonical": "",
            "meaning": "",
            "unit": "",
            "attribute_ambiguities": {"meaning": "资金流买卖净额"},
        },
    ]

    attributes, conflicts, ambiguities = er._resolve_evidence_attributes(evidence)

    assert attributes == {"canonical": "f1", "meaning": "净利润", "unit": "元"}
    assert conflicts == {}
    assert ambiguities == {}


def test_unaligned_group_is_retained_when_it_is_the_only_attribute_evidence():
    evidence = [
        {
            "canonical": "",
            "meaning": "",
            "unit": "",
            "attribute_ambiguities": {"meaning": "行业名称/东财行业码"},
        }
    ]

    attributes, conflicts, ambiguities = er._resolve_evidence_attributes(evidence)

    assert attributes["meaning"] == ""
    assert conflicts == {}
    assert ambiguities == {"meaning": ["行业名称/东财行业码"]}


def test_unresolved_placeholder_does_not_conflict_with_a_resolved_value():
    evidence = [
        {"canonical": "f1", "meaning": "待破解", "unit": "-"},
        {"canonical": "f1", "meaning": "净利润", "unit": "元"},
    ]

    attributes, conflicts, ambiguities = er._resolve_evidence_attributes(evidence)

    assert attributes == {"canonical": "f1", "meaning": "净利润", "unit": "元"}
    assert conflicts == {}
    assert ambiguities == {}

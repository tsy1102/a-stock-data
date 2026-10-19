from scripts import field_registry_api as registry_api


def test_blank_and_placeholder_meanings_are_unresolved():
    for meaning in (None, "", " 待破解 ", "UNKNOWN"):
        assert registry_api.source_field_semantic_issues({"meaning": meaning}) == [
            "meaning_missing"
        ]


def test_meaning_and_unit_conflicts_or_alignment_ambiguities_are_reported():
    record = {
        "meaning": "利润",
        "attribute_conflicts": {"meaning": ["利润", "利润率"], "unit": ["元", "万元"]},
        "attribute_ambiguities": {"unit": ["元/股 / 元"]},
    }

    assert registry_api.source_field_semantic_issues(record) == [
        "meaning_conflict",
        "unit_alignment_ambiguous",
        "unit_conflict",
    ]


def test_canonical_alias_variants_do_not_block_clear_semantics():
    record = {
        "canonical": "",
        "meaning": "市盈率（TTM）",
        "attribute_conflicts": {"canonical": ["pe_ttm", "PE_TTM"]},
        "attribute_ambiguities": {"canonical": ["pe_ttm/pe_dynamic"]},
    }

    assert registry_api.source_field_semantic_issues(record) == []

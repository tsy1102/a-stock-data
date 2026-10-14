import pytest

import get_mak_report


@pytest.mark.parametrize("value", [None, "", "   ", 0])
def test_blank_or_non_string_industries_map_to_other(value):
    assert get_mak_report.normalize_industry(value) == "其他"


def test_known_industry_alias_remains_normalized():
    alias, target = next(iter(get_mak_report._INDUSTRY_ALIASES.items()))

    assert get_mak_report.normalize_industry(alias) == target

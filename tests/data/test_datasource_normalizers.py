import math

import pytest

from stock_common.sc_datasource._normalizers import (
    normalize_compact_date,
    soft_optional_float,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        ("", None),
        (" - ", None),
        ("--", None),
        ("None", None),
        ("null", None),
        ("1,234.50", 1234.5),
        (True, None),
        ("not-a-number", None),
    ],
)
def test_soft_optional_float_preserves_legacy_contract(value, expected):
    assert soft_optional_float(value) == expected


def test_soft_optional_float_preserves_non_finite_float_behavior():
    assert math.isnan(soft_optional_float("NaN"))


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("20260921", "2026-09-21"),
        (" 20260921 ", "2026-09-21"),
        ("2026-09-21", "2026-09-21"),
        ("20261399", "2026-13-99"),
        (None, "None"),
    ],
)
def test_normalize_compact_date_preserves_permissive_contract(value, expected):
    assert normalize_compact_date(value) == expected

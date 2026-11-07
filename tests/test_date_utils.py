from datetime import date, datetime

import pytest

from scripts.date_utils import normalize_date_key


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (date(2026, 11, 7), "2026-11-07"),
        (datetime(2026, 11, 7, 15, 30), "2026-11-07"),
        (" 2026-11-07 ", "2026-11-07"),
        ("20261107", "2026-11-07"),
        ("2026-11-07T15:30:00", None),
        ("20260230", None),
        (123, None),
        (None, None),
    ],
)
def test_normalize_date_key_preserves_date_only_contract(value, expected):
    assert normalize_date_key(value) == expected

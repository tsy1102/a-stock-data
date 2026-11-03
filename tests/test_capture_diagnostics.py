from __future__ import annotations

import pytest

from scripts.capture_diagnostics import _source_as_of_date


def _quote_payload(timestamp_by_symbol: dict[str, str]) -> dict[str, object]:
    return {
        "stocks": {
            symbol: {"fields": [""] * 30 + [timestamp, ""]}
            for symbol, timestamp in timestamp_by_symbol.items()
        }
    }


@pytest.mark.parametrize(
    ("source", "timestamps", "expected"),
    [
        ("sina", {"600519": "2026-11-02", "000001": "2026-11-02"}, "2026-11-02"),
        (
            "tencent",
            {"600519": "20261102161455", "000001": "20261102161503"},
            "2026-11-02",
        ),
    ],
)
def test_quote_record_timestamps_supply_consistent_source_date(
    source: str, timestamps: dict[str, str], expected: str
) -> None:
    assert _source_as_of_date(source, _quote_payload(timestamps)) == expected


@pytest.mark.parametrize(
    ("source", "timestamps"),
    [
        ("sina", {"600519": "2026-11-02", "000001": "2026-11-03"}),
        ("tencent", {"600519": "20261102161455", "000001": "bad-timestamp"}),
    ],
)
def test_quote_record_timestamps_must_be_valid_and_consistent(
    source: str, timestamps: dict[str, str]
) -> None:
    assert _source_as_of_date(source, _quote_payload(timestamps)) is None


def test_quote_record_timestamp_layout_is_source_specific() -> None:
    payload = _quote_payload({"600519": "2026-11-02"})

    assert _source_as_of_date("push2", payload) is None
    assert _source_as_of_date("sina", {"stocks": {}}) is None

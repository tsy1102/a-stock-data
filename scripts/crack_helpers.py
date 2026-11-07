"""Shared pure helpers for archived field-cracking scripts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def parse_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("%", "")
    if text in ("", "None", "nan", "NaN", "-", "--", "null"):
        return None
    try:
        return float(text)
    except Exception:
        return None


def collision_field(
    per_date: Mapping[Any, Mapping[Any, Any]],
    source: str,
    snapshot_phases: Mapping[tuple[str, Any], str],
) -> dict[str, Any]:
    values: dict[tuple[str, str], Any] = {}
    sample_meta: dict[tuple[str, str], dict[str, str]] = {}
    for day, row in per_date.items():
        for code, value in row.items():
            sample_key = (str(code), f"T:{day}")
            values[sample_key] = value
            sample_meta[sample_key] = {
                "phase": snapshot_phases.get((source, day), "unknown"),
                "source": source,
            }
    distinct = set(values.values())
    return {
        "vals": values,
        "src": source,
        "is_constant": bool(values) and len(distinct) <= 1,
        "sample_meta": sample_meta,
    }

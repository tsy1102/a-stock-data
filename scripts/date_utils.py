"""Date-key normalization shared by capture and daily validation scripts."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional


def normalize_date_key(value: Any) -> Optional[str]:
    """Return an ISO date for date values or supported date strings, else ``None``."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    for date_format in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(normalized, date_format).date().isoformat()
        except ValueError:
            continue
    return None

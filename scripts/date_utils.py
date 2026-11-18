"""Date-key normalization shared by capture and daily validation scripts."""

from __future__ import annotations

import math
import re
from datetime import date, datetime, timedelta, timezone
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


def normalize_unix_seconds_date(value: Any) -> Optional[str]:
    """Return the Asia/Shanghai date of a strict 10-digit Unix-second value."""
    if isinstance(value, bool):
        return None
    if isinstance(value, float):
        if not math.isfinite(value) or not value.is_integer():
            return None
        value = int(value)
    if isinstance(value, int):
        normalized = str(value)
    elif isinstance(value, str):
        normalized = value.strip()
    else:
        return None
    if re.fullmatch(r"\d{10}", normalized) is None:
        return None
    try:
        utc_value = datetime.fromtimestamp(int(normalized), tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None
    return utc_value.astimezone(timezone(timedelta(hours=8))).date().isoformat()

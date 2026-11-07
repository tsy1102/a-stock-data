"""Small permissive value normalizers shared by datasource adapters."""

from __future__ import annotations

import re
from typing import Any, Optional


def soft_optional_float(value: Any) -> Optional[float]:
    """Parse legacy optional numeric fields without imposing strict source validation."""
    if value is None or value == "":
        return None
    text = str(value).replace(",", "").strip()
    if text in ("", "-", "--", "None", "null"):
        return None
    try:
        return float(text)
    except ValueError:
        return None


def normalize_compact_date(value: Any) -> str:
    """Format an eight-digit date as ISO text; preserve other trimmed source text."""
    text = str(value).strip()
    if re.fullmatch(r"[0-9]{8}", text):
        return f"{text[0:4]}-{text[4:6]}-{text[6:8]}"
    return text

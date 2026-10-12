"""Regression contract for the per-stock quote fallback after batch prefetch.

Report batch routing is a separate stage: push2delay supplies shared market fields,
then the Tencent batch supplies missing canonical fields. This tuple covers only the
per-stock fallback when those batch stages do not provide a valid quote.
"""

from typing import Tuple

QUOTE_FALLBACK_EXPECTED_ORDER: Tuple[str, ...] = (
    "tdx",
    "tencent",
    "eastmoney_push2delay",
    "eastmoney_push2",
)

"""Expected quote fallback order for regression tests.

The runtime route stays explicit in ``core.data_provider.get_canonical_stock_data``.
This tuple is a test contract, not a runtime routing source of truth.
"""

from typing import Tuple

QUOTE_FALLBACK_EXPECTED_ORDER: Tuple[str, ...] = (
    "tdx",
    "tencent",
    "eastmoney_push2delay",
    "eastmoney_push2",
)

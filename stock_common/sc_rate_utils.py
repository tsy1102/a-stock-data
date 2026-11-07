"""Small process-local timing helpers for datasource adapters."""

from __future__ import annotations

import time


def advance_interval_timestamp(last_request: float, interval: float) -> float:
    """Wait for a minimum interval and return the next request timestamp.

    Callers must hold their own source-specific lock while reading and updating
    ``last_request`` so independent providers keep independent rate-limit state.
    """
    now = time.time()
    wait = interval - (now - last_request)
    if wait > 0:
        time.sleep(wait)
    return time.time()

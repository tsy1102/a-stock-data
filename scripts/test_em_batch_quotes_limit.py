# -*- coding: utf-8 -*-
"""scripts/test_em_batch_quotes_limit.py - V12.6 HTTP batch limit probe

Goal: Determine empirically how get_em_batch_quotes performs across input
sizes. Internally it auto-chunks at 300 codes per HTTP request, so the test
is about overall throughput / latency / success rate, NOT about the API's
own per-request limit.

Stages:
  100, 500, 1000, 2000, 5000 stocks per call

Each stage prints:
  - Wall-clock seconds
  - Returned record count
  - HTTP chunk count (size 300 -> ceil(N/300))
  - Success flag (HTTP 200 + valid JSON)

The test uses REAL network and is marked @pytest.mark.real_network so
conftest.py's _no_real_network fixture does NOT block it.

Usage:
  .\\scripts\\run_with_system_python.bat scripts/test_em_batch_quotes_limit.py
  .\\scripts\\run_with_system_python.bat -m pytest scripts/test_em_batch_quotes_limit.py -v
"""
from __future__ import annotations

import sys
import os
import time
import math
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use a fixed list of well-known large-cap codes for repeatable probing.
# These are real A-share codes that have stable names on Eastmoney push2.
SAMPLE_CODES = [
    # 100 large caps (mostly banks, energy, consumer staples)
    "600519", "601318", "600036", "601398", "601939", "600276", "600887",
    "601988", "601288", "600000", "600030", "601166", "600585", "600031",
    "600050", "601012", "601628", "600016", "601888", "600196", "601800",
    "601857", "600028", "601088", "600188", "601668", "600104", "601398",
    "601658", "601336", "600837", "601169", "601818", "600029", "601229",
    "601633", "601995", "600188", "600547", "600436", "601319", "600570",
    "600583", "601766", "601877", "601618", "601669", "600690", "600703",
    "601111", "600795", "600406", "600089", "600362", "600905", "601728",
    "600886", "600018", "600019", "600023", "600027", "600115", "600170",
    "600177", "600188", "600196", "600208", "600219", "600221", "600233",
    "600256", "600276", "600297", "600309", "600332", "600340", "600352",
    "600362", "600372", "600380", "600383", "600406", "600415", "600418",
    "600436", "600487", "600498", "600519", "600522", "600535", "600547",
    "600570", "600583", "600585", "600588", "600600", "600660", "600690",
    "600703", "600795", "600809", "600837", "600886", "600887", "600893",
]


def make_codes(n: int) -> List[str]:
    """Return a deterministic list of n codes, repeating sample codes
    if needed (Eastmoney ignores dupes in fs= param)."""
    if n <= len(SAMPLE_CODES):
        return SAMPLE_CODES[:n]
    out = []
    while len(out) < n:
        out.extend(SAMPLE_CODES)
    return out[:n]


def probe(n: int, timeout: float = 60.0) -> dict:
    """Run get_em_batch_quotes on n codes; return timing + result summary."""
    from stock_common import get_em_batch_quotes
    codes = make_codes(n)
    chunk_size = 300
    expected_chunks = math.ceil(n / chunk_size)

    t0 = time.time()
    try:
        result = get_em_batch_quotes(codes)
        elapsed = time.time() - t0
        return {
            "n_requested": n,
            "n_returned": len(result) if isinstance(result, dict) else 0,
            "chunks": expected_chunks,
            "elapsed_sec": round(elapsed, 2),
            "success": bool(result),
            "error": None,
        }
    except Exception as e:
        elapsed = time.time() - t0
        return {
            "n_requested": n,
            "n_returned": 0,
            "chunks": expected_chunks,
            "elapsed_sec": round(elapsed, 2),
            "success": False,
            "error": str(e),
        }


def main() -> None:
    print("=" * 70)
    print("V12.6: get_em_batch_quotes 上限实测")
    print("=" * 70)
    print(f"sample pool size: {len(SAMPLE_CODES)}")
    print(f"chunk size: 300 (hardcoded inside get_em_batch_quotes)")
    print()

    stages = [100, 500, 1000, 2000, 5000]
    results = []
    for n in stages:
        print(f"--- probing N = {n} ---")
        r = probe(n)
        results.append(r)
        if r["success"]:
            print(
                f"  N={r['n_requested']:>5}  "
                f"chunks={r['chunks']:>2}  "
                f"returned={r['n_returned']:>4}  "
                f"elapsed={r['elapsed_sec']:>6.2f}s  "
                f"OK"
            )
        else:
            print(
                f"  N={r['n_requested']:>5}  "
                f"chunks={r['chunks']:>2}  "
                f"elapsed={r['elapsed_sec']:>6.2f}s  "
                f"FAIL: {r['error']}"
            )

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"{'N':>6}  {'Chunks':>7}  {'Returned':>9}  {'Time(s)':>9}  Result")
    print("-" * 70)
    for r in results:
        result_str = "OK" if r["success"] else "FAIL"
        print(
            f"{r['n_requested']:>6}  "
            f"{r['chunks']:>7}  "
            f"{r['n_returned']:>9}  "
            f"{r['elapsed_sec']:>9.2f}  "
            f"{result_str}"
        )

    successful = [r for r in results if r["success"]]
    if successful:
        max_n = max(r["n_requested"] for r in successful)
        print()
        print(f"==> max successful N = {max_n}")
    else:
        print()
        print("==> ALL STAGES FAILED. Check network / IP block.")


if __name__ == "__main__":
    main()
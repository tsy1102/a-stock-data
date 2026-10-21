"""Regenerate the compact runtime summary from the canonical AxData crosswalk."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from axdata_crosswalk_summary import summarize_crosswalk

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = PROJECT_ROOT / "docs" / "axdata_interface_crosswalk.json"
SUMMARY_PATH = PROJECT_ROOT / "docs" / "axdata_interface_crosswalk_summary.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="fail when the checked-in summary is stale"
    )
    args = parser.parse_args()

    raw = SOURCE_PATH.read_bytes()
    crosswalk = json.loads(raw.decode("utf-8"))
    if not isinstance(crosswalk, dict):
        raise ValueError("AxData crosswalk root must be an object")
    summary = summarize_crosswalk(crosswalk, hashlib.sha256(raw).hexdigest())
    encoded = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    if args.check:
        if not SUMMARY_PATH.is_file() or SUMMARY_PATH.read_text(encoding="utf-8") != encoded:
            raise SystemExit("AxData crosswalk summary is missing or stale")
        print("AxData crosswalk summary: PASS")
        return 0

    SUMMARY_PATH.write_text(encoded, encoding="utf-8", newline="\n")
    print(f"Wrote {SUMMARY_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

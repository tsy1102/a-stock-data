#!/usr/bin/env python3
"""Safely rebuild the compatibility aggregate from authoritative source_fields."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from typing import Any

for stream in (sys.stdout, sys.stderr):
    if stream is not None and hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_REGISTRY = os.path.join(REPO_ROOT, "docs", "field_verification", "field_registry.json")
TEMP_DIR = os.path.join(REPO_ROOT, ".tmp")

sys.path.insert(0, SCRIPT_DIR)
import field_registry_api as fra


def rebuild_projection(registry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, int]]:
    """Return a copy whose aggregate is rebuilt without changing source evidence."""
    source_fields = fra.source_field_records(registry)
    if not source_fields:
        raise ValueError("registry.source_fields is empty; refusing to rebuild projection")
    updated = dict(registry)
    updated["fields"] = fra.build_aggregate_fields(source_fields)
    if updated["source_fields"] != source_fields:
        raise AssertionError("source_fields changed while rebuilding aggregate projection")
    before_by_code = {row["code"]: row for row in registry.get("fields", [])}
    after_by_code = {row["code"]: row for row in updated["fields"]}
    stats = {
        "source_fields": len(source_fields),
        "aggregate_fields_before": len(registry.get("fields", [])),
        "aggregate_fields_after": len(updated["fields"]),
        "changed_aggregates": sum(
            before_by_code.get(code) != after_by_code.get(code)
            for code in set(before_by_code) | set(after_by_code)
        ),
        "ambiguous_aggregates": sum(
            row["aggregation_status"] == "ambiguous" for row in updated["fields"]
        ),
        "incomplete_aggregates": sum(
            row["aggregation_status"] == "incomplete" for row in updated["fields"]
        ),
    }
    return updated, stats


def _write_atomically(path: str, registry: dict[str, Any], expected_digest: str) -> None:
    with open(path, "rb") as current:
        actual_digest = hashlib.sha256(current.read()).hexdigest()
    if actual_digest != expected_digest:
        raise RuntimeError("registry changed during projection rebuild; refusing to overwrite")

    os.makedirs(TEMP_DIR, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=TEMP_DIR,
            prefix="field_registry_projection_",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temp_path = stream.name
            json.dump(registry, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=DEFAULT_REGISTRY, help="registry JSON path")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="check projection and formatting without writing (default)",
    )
    mode.add_argument("--apply", action="store_true", help="write the rebuilt fields projection")
    args = parser.parse_args(argv)

    with open(args.registry, "rb") as stream:
        original_bytes = stream.read()
    original_digest = hashlib.sha256(original_bytes).hexdigest()
    registry = json.loads(original_bytes.decode("utf-8"))
    updated, stats = rebuild_projection(registry)
    for key, value in stats.items():
        print(f"{key}: {value}")
    changed = updated.get("fields") != registry.get("fields")
    canonical_bytes = (json.dumps(updated, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    serialization_changed = original_bytes != canonical_bytes
    if not changed and not serialization_changed:
        print("Projection is current; source_fields are unchanged.")
        return 0
    if not args.apply:
        if changed:
            print("Projection is stale. Review the diff, then rerun with --apply.")
        else:
            print("Registry formatting is noncanonical; rerun with --apply to normalize it.")
        return 1
    _write_atomically(args.registry, updated, original_digest)
    with open(args.registry, encoding="utf-8") as stream:
        persisted = json.load(stream)
    if persisted.get("source_fields") != registry.get("source_fields"):
        raise AssertionError("source_fields changed after projection write")
    if persisted.get("fields") != fra.build_aggregate_fields(registry["source_fields"]):
        raise AssertionError("written aggregate does not match source_fields")
    print("Projection rebuilt; authoritative source_fields were preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Preview or record an explicit human disposition for a collision candidate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import collision_candidate_reviews as reviews


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {label} JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} JSON root must be an object: {path}")
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a collision-candidate review; use --apply to append it to the audit ledger."
    )
    parser.add_argument(
        "--decision",
        required=True,
        type=Path,
        help="JSON decision document based on docs/field_verification/review_templates/candidate_review_template.json",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="append this decision to collision_candidate_reviews.json; without this flag, only preview",
    )
    return parser


def _expand_decision_document(document: dict[str, Any]) -> list[Any]:
    if "decisions" not in document:
        return [document]
    if set(document) != {"schema_version", "decisions"}:
        raise ValueError("batch decision document only supports schema_version and decisions")
    if type(document.get("schema_version")) is not int or document["schema_version"] != 1:
        raise ValueError("unsupported batch decision schema_version")
    decisions = document.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise ValueError("batch decisions must be a non-empty list")
    expanded = [
        (
            {"schema_version": document["schema_version"], **item}
            if isinstance(item, dict) and "schema_version" not in item
            else item
        )
        for item in decisions
    ]
    candidate_ids = [item.get("candidate_id") for item in expanded if isinstance(item, dict)]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("batch decisions cannot contain a candidate more than once")
    return expanded


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        document = _read_json(args.decision, "decision")
        decisions = _expand_decision_document(document)
        prepared_items = [reviews.prepare_review_decision(item) for item in decisions]
        state, warnings, writable = reviews.load_state()
        if warnings:
            for warning in warnings:
                print(f"[candidate-review] WARNING: {warning}", file=sys.stderr)
        if args.apply and not writable:
            raise ValueError(
                "candidate review ledger is invalid/unwritable; original file was preserved"
            )
        updated = state
        results = []
        for prepared, identity in prepared_items:
            updated, changed = reviews.apply_prepared_review(updated, prepared, identity)
            results.append(
                {
                    "candidate_id": prepared["candidate_id"],
                    "disposition": prepared["disposition"],
                    "reviewer": prepared["reviewer"],
                    "reviewed_at": prepared["reviewed_at"],
                    "evidence_refs": prepared["resolved_evidence_refs"],
                    "idempotent_replay": not changed,
                }
            )
        result = {
            "mode": "apply" if args.apply else "preview",
            "decision_count": len(results),
            "decisions": results,
            "ledger": reviews.STATE_PATH.relative_to(reviews.VERIFY_DIR.parent).as_posix(),
        }
        if args.apply:
            reviews.save_state(updated)
            result["persisted"] = True
            print(
                "[candidate-review] 已记录审阅；后续碰撞报告会读取该状态。"
                "这不会修改主字典或字段注册表。",
                file=sys.stderr,
            )
        else:
            result["persisted"] = False
            print("[candidate-review] 预览通过；确认后添加 --apply 写入审阅台账。", file=sys.stderr)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, TypeError, ValueError) as exc:
        print(f"[candidate-review] ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

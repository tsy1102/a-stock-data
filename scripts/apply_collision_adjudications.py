#!/usr/bin/env python3
"""Apply explicitly reviewed collision decisions to the field registry.

Collision reports remain discovery-only. This command defaults to preview and
requires ``--apply`` before it updates the registry and generated dictionary views.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
VERIFY_DIR = REPO_ROOT / "docs" / "field_verification"
REGISTRY_PATH = VERIFY_DIR / "field_registry.json"
LINEAGE_PATH = VERIFY_DIR / "source_lineage.json"
FIELD_DICT_PATH = REPO_ROOT / "docs" / "field_dict.md"
UNKNOWN_FIELDS_PATH = REPO_ROOT / "docs" / "unknown_fields.md"
SOURCE_MAP_PATH = REPO_ROOT / "docs" / "source_repository_map.md"
METADATA_GAPS_PATH = REPO_ROOT / "docs" / "field_metadata_gaps.md"
sys.path.insert(0, str(SCRIPT_DIR))

import field_registry_api as fra
import gen_field_dict as gfd
import source_lineage_api as sla

VALID_ACTIONS = {"verify"}
VALID_LEVELS = {"L1", "L1-U"}
SAME_MEANING_RELATION = "same_number_same_meaning"


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{label} must be an object")
    return value


def _non_empty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _validate_iso_date(value: Any, label: str) -> str:
    text = _non_empty_string(value, label)
    try:
        if dt.date.fromisoformat(text).isoformat() != text:
            raise ValueError
    except ValueError as exc:
        raise ValueError(f"{label} must use YYYY-MM-DD") from exc
    return text


def _inside_verification_dir(
    path_value: str, label: str, relative_base: Path = REPO_ROOT
) -> tuple[Path, str]:
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = relative_base / candidate
    resolved = candidate.resolve()
    try:
        relative = resolved.relative_to(VERIFY_DIR.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} must be inside docs/field_verification") from exc
    return resolved, relative.as_posix()


def _runtime_identity(field_id: str, source: str, lineage: dict[str, Any]) -> tuple[str, str]:
    aliases = sla.runtime_aliases_for_source(source, lineage)
    matches: list[tuple[int, str, str]] = []
    for alias in aliases:
        if field_id.startswith(alias + "."):
            matches.append((len(alias), alias, field_id[len(alias) + 1 :]))
        elif field_id.startswith(alias + "["):
            matches.append((len(alias), alias, field_id[len(alias) :]))
    if not matches:
        raise ValueError(
            f"{source!r} does not map to runtime field {field_id!r} in the collision report"
        )
    longest = max(match[0] for match in matches)
    best = {(alias, code) for length, alias, code in matches if length == longest}
    if len(best) != 1:
        raise ValueError(f"runtime field identity is ambiguous: {field_id!r}")
    alias, code = next(iter(best))
    if not code:
        raise ValueError(f"runtime field has an empty code path: {field_id!r}")
    return alias, code


def _find_l1_candidate(report: dict[str, Any], left: str, right: str) -> dict[str, Any]:
    candidates = report.get("L1")
    if not isinstance(candidates, list):
        raise TypeError("collision report L1 must be a list")
    matches = [
        candidate
        for candidate in candidates
        if isinstance(candidate, dict)
        and candidate.get("left") == left
        and candidate.get("right") == right
    ]
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one report L1 candidate for {left!r} -> {right!r}; found {len(matches)}"
        )
    candidate = matches[0]
    if candidate.get("level") not in VALID_LEVELS:
        raise ValueError("only L1 and L1-U findings can be adjudicated")
    if candidate.get("hub_flag"):
        raise ValueError("hub-flagged collision candidates cannot be adjudicated")
    if int(candidate.get("n_days", 0)) < 3:
        raise ValueError("L1 candidate must contain at least three independent trading days")
    return candidate


def _mapping_key(mapping: dict[str, Any]) -> frozenset[tuple[str, str]] | None:
    left = mapping.get("from")
    right = mapping.get("to")
    if not isinstance(left, dict) or not isinstance(right, dict):
        return None
    left_source, left_code = left.get("source"), left.get("code")
    right_source, right_code = right.get("source"), right.get("code")
    if not isinstance(left_source, str) or not left_source:
        return None
    if not isinstance(left_code, str) or not left_code:
        return None
    if not isinstance(right_source, str) or not right_source:
        return None
    if not isinstance(right_code, str) or not right_code:
        return None
    return frozenset({(left_source, left_code), (right_source, right_code)})


def _add_verified_mapping(
    registry: dict[str, Any],
    target: tuple[str, str],
    anchor: tuple[str, str],
    evidence: str,
) -> bool:
    mappings = registry.setdefault("mappings", [])
    if not isinstance(mappings, list):
        raise TypeError("registry.mappings must be a list")
    wanted = frozenset({target, anchor})
    for mapping in mappings:
        if not isinstance(mapping, dict) or _mapping_key(mapping) != wanted:
            continue
        if mapping.get("relation") != SAME_MEANING_RELATION:
            raise ValueError(
                "an existing mapping for this pair has a different relation; resolve it manually"
            )
        return False
    mappings.append(
        {
            "from": {"source": target[0], "code": target[1]},
            "to": {"source": anchor[0], "code": anchor[1]},
            "relation": SAME_MEANING_RELATION,
            "evidence": evidence,
        }
    )
    return True


def _append_adjudication_evidence(field: dict[str, Any], adjudication: dict[str, Any]) -> None:
    history = field.setdefault("adjudications", [])
    if not isinstance(history, list):
        raise TypeError("source field adjudications must be a list")
    history.append(copy.deepcopy(adjudication))

    reference_evidence = field.setdefault("reference_evidence", [])
    if not isinstance(reference_evidence, list):
        raise TypeError("source field reference_evidence must be a list")
    reference_evidence.append(
        {
            "section": adjudication["report"],
            "canonical": field.get("canonical", ""),
            "meaning": field.get("meaning", ""),
            "unit": field.get("unit", ""),
            "status_raw": f"人工复核 {adjudication['reviewed_on']}：{adjudication['id']}",
            "status": adjudication["status"],
            "adjudication_id": adjudication["id"],
        }
    )
    sections = field.setdefault("sections", [])
    if not isinstance(sections, list):
        raise TypeError("source field sections must be a list")
    if adjudication["report"] not in sections:
        sections.append(adjudication["report"])
        sections.sort()
    if not field.get("section"):
        field["section"] = adjudication["report"]

    status_evidence = field.setdefault("status_evidence", {})
    if not isinstance(status_evidence, dict):
        raise TypeError("source field status_evidence must be an object")
    ids = status_evidence.setdefault("adjudication_ids", [])
    if not isinstance(ids, list):
        raise TypeError("source field status_evidence.adjudication_ids must be a list")
    ids.append(adjudication["id"])


def _refresh_aggregate_projection(registry: dict[str, Any], affected_codes: set[str]) -> None:
    fields = registry.get("fields")
    if not isinstance(fields, list):
        raise TypeError("registry.fields must be a list")
    source_fields = fra.source_field_records(registry)
    by_code: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in source_fields:
        if record["code"] in affected_codes:
            by_code[record["code"]].append(record)

    for code in affected_codes:
        aggregates = [record for record in fields if record.get("code") == code]
        if len(aggregates) != 1:
            raise ValueError(
                f"expected one compatibility aggregate for code {code!r}; found {len(aggregates)}"
            )
        records = by_code.get(code, [])
        if not records:
            raise ValueError(f"no source_fields remain for aggregate code {code!r}")
        sources = sorted({record["source"] for record in records})
        statuses = {record.get("status", "unverified") for record in records}
        if "conflict" in statuses:
            aggregate_status = "conflict"
        elif len(statuses) == 1:
            aggregate_status = next(iter(statuses))
        else:
            aggregate_status = "unverified"

        def common_value(key: str) -> str:
            values = {str(record.get(key, "")).strip() for record in records}
            values.discard("")
            return next(iter(values)) if len(values) == 1 else ""

        raw_statuses = {
            raw
            for record in records
            for raw in record.get("status_evidence", {}).get("reference_status_raw", [])
            if isinstance(raw, str) and raw
        }
        aggregate = aggregates[0]
        aggregate.update(
            {
                "source": sources[0] if len(sources) == 1 else None,
                "sources": sources,
                "section": common_value("section"),
                "canonical": common_value("canonical"),
                "meaning": common_value("meaning"),
                "unit": common_value("unit"),
                "status_raw": next(iter(raw_statuses)) if len(raw_statuses) == 1 else "",
                "status": aggregate_status,
                "source_statuses": {
                    record["source"]: record.get("status", "unverified") for record in records
                },
            }
        )

    meta = registry.setdefault("meta", {})
    if not isinstance(meta, dict):
        raise TypeError("registry.meta must be an object")
    meta["updated"] = dt.date.today().isoformat()
    counts: Counter[str] = Counter()
    for record in source_fields:
        counts[record.get("status", "unverified")] += 1
        counts[record.get("status_resolution", "unresolved")] += 1
    meta["source_field_stats"] = dict(sorted(counts.items()))


def apply_adjudications(
    registry: dict[str, Any],
    lineage: dict[str, Any],
    decision_document: dict[str, Any],
    report: dict[str, Any],
    report_path: str,
    decision_path: str,
) -> tuple[dict[str, Any], dict[str, int]]:
    """Validate decisions and return an updated copy without mutating inputs."""
    if decision_document.get("schema_version") != 1:
        raise ValueError("unsupported adjudication schema_version")
    if report.get("schema_version") != 2:
        raise ValueError("unsupported collision report schema_version")
    if report.get("collision_mode") != "verified_anchor_only":
        raise ValueError("only verified_anchor_only collision reports are accepted")
    if report.get("exploratory_pair_count", 0) != 0:
        raise ValueError("exploratory reports cannot be promoted to registry decisions")

    reviewer = _non_empty_string(decision_document.get("reviewer"), "reviewer")
    reviewed_on = _validate_iso_date(decision_document.get("reviewed_on"), "reviewed_on")
    decisions = decision_document.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise ValueError("decisions must be a non-empty list")

    updated = copy.deepcopy(registry)
    source_fields = fra.source_field_records(updated)
    by_identity = {(record["source"], record["code"]): record for record in source_fields}
    seen_ids: set[str] = set()
    seen_targets: set[tuple[str, str]] = set()
    affected_codes: set[str] = set()
    stats = {"verified": 0, "already_applied": 0, "mappings_added": 0}

    for raw_decision in decisions:
        decision = _require_object(raw_decision, "decision")
        decision_id = _non_empty_string(decision.get("id"), "decision.id")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,127}", decision_id):
            raise ValueError(f"decision.id contains unsupported characters: {decision_id!r}")
        if decision_id in seen_ids:
            raise ValueError(f"duplicate decision id: {decision_id}")
        seen_ids.add(decision_id)

        candidate_pair = _require_object(decision.get("candidate"), "decision.candidate")
        left_id = _non_empty_string(candidate_pair.get("left"), "candidate.left")
        right_id = _non_empty_string(candidate_pair.get("right"), "candidate.right")
        candidate = _find_l1_candidate(report, left_id, right_id)

        target_obj = _require_object(decision.get("target"), "decision.target")
        anchor_obj = _require_object(decision.get("anchor"), "decision.anchor")
        target = (
            _non_empty_string(target_obj.get("source"), "target.source"),
            _non_empty_string(target_obj.get("code"), "target.code"),
        )
        anchor = (
            _non_empty_string(anchor_obj.get("source"), "anchor.source"),
            _non_empty_string(anchor_obj.get("code"), "anchor.code"),
        )
        _target_alias, target_code = _runtime_identity(left_id, target[0], lineage)
        if target_code != target[1]:
            raise ValueError(
                f"target {target[0]}::{target[1]} does not match report field {left_id!r}"
            )
        anchor_alias, anchor_code = _runtime_identity(right_id, anchor[0], lineage)
        if anchor_code != anchor[1]:
            raise ValueError(
                f"anchor {anchor[0]}::{anchor[1]} does not match report field {right_id!r}"
            )
        if target not in by_identity:
            raise ValueError(f"unknown target source field: {target[0]}::{target[1]}")
        if anchor not in by_identity:
            raise ValueError(f"unknown anchor source field: {anchor[0]}::{anchor[1]}")
        if target == anchor:
            raise ValueError("target and anchor cannot be the same source field")

        target_record = by_identity[target]
        anchor_record = by_identity[anchor]
        anchor_lineage = lineage.get("sources", {}).get(anchor[0], {})
        anchor_family = sla.runtime_family(anchor_alias, lineage)
        if (
            anchor_record.get("status") != "verified"
            or not anchor_lineage.get("anchor_eligible")
            or anchor_lineage.get("independence_status") != "confirmed"
            or anchor_family != anchor_lineage.get("independence_family")
        ):
            raise ValueError(f"selected anchor is not currently verified and independent: {anchor}")

        action = _non_empty_string(decision.get("action"), "decision.action")
        if action not in VALID_ACTIONS:
            raise ValueError(
                f"unsupported adjudication action: {action!r}; only verified semantic conclusions can be written"
            )
        rationale = _non_empty_string(decision.get("rationale"), "decision.rationale")
        current_status = target_record.get("status", "unverified")
        if target in seen_targets:
            raise ValueError(f"multiple decisions target the same field: {target}")
        seen_targets.add(target)

        adjudication_status = "verified"
        adjudication = {
            "id": decision_id,
            "action": action,
            "status": adjudication_status,
            "reviewer": reviewer,
            "reviewed_on": reviewed_on,
            "report": report_path,
            "decision_file": decision_path,
            "candidate": {"left": left_id, "right": right_id},
            "level": candidate["level"],
            "rationale": rationale,
            "evidence": {
                key: copy.deepcopy(candidate[key])
                for key in (
                    "ratio",
                    "overall_hit",
                    "n_days",
                    "n_pairs",
                    "distinct_days",
                    "daily_sample_counts",
                    "evidence_sources",
                )
                if key in candidate
            },
        }

        history = target_record.get("adjudications", [])
        if not isinstance(history, list):
            raise TypeError("source field adjudications must be a list")
        prior = next(
            (item for item in history if isinstance(item, dict) and item.get("id") == decision_id),
            None,
        )
        if prior is not None:
            if prior != adjudication or current_status != adjudication_status:
                raise ValueError(
                    f"decision id already exists with different content: {decision_id}"
                )
            canonical = _non_empty_string(decision.get("canonical"), "decision.canonical")
            meaning = _non_empty_string(decision.get("meaning"), "decision.meaning")
            unit = decision.get("unit", "")
            if not isinstance(unit, str):
                raise TypeError("decision.unit must be a string")
            if (
                target_record.get("canonical") != canonical
                or target_record.get("meaning") != meaning
                or target_record.get("unit", "") != unit.strip()
            ):
                raise ValueError(f"decision id reuses different field attributes: {decision_id}")
            evidence = f"adjudication:{decision_path}#{decision_id};report:{report_path}"
            if _add_verified_mapping(updated, target, anchor, evidence):
                stats["mappings_added"] += 1
            stats["already_applied"] += 1
            continue

        if current_status not in {"unverified", "candidate"}:
            raise ValueError(
                f"target status {current_status!r} requires separate conflict review: {target}"
            )

        canonical = _non_empty_string(decision.get("canonical"), "decision.canonical")
        meaning = _non_empty_string(decision.get("meaning"), "decision.meaning")
        unit = decision.get("unit", "")
        if not isinstance(unit, str):
            raise TypeError("decision.unit must be a string")
        target_record.update(
            {
                "canonical": canonical,
                "meaning": meaning,
                "unit": unit.strip(),
                "status": "verified",
                "status_resolution": "manual_collision_adjudication",
            }
        )
        evidence = f"adjudication:{decision_path}#{decision_id};report:{report_path}"
        if _add_verified_mapping(updated, target, anchor, evidence):
            stats["mappings_added"] += 1
        stats["verified"] += 1
        affected_codes.add(target[1])

        _append_adjudication_evidence(target_record, adjudication)

    if affected_codes:
        _refresh_aggregate_projection(updated, affected_codes)
    return updated, stats


def _atomic_write_batch(outputs: dict[Path, str]) -> None:
    originals = {path: path.read_bytes() if path.exists() else None for path in outputs}
    staged: dict[Path, str] = {}
    replaced: list[Path] = []
    try:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary = tempfile.mkstemp(
                prefix=path.name + ".", suffix=".tmp", dir=path.parent
            )
            staged[path] = temporary
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
        for path, temporary in staged.items():
            os.replace(temporary, path)
            replaced.append(path)
    except Exception as original_error:
        rollback_errors = []
        for path in reversed(replaced):
            try:
                original = originals[path]
                if original is None:
                    path.unlink(missing_ok=True)
                else:
                    descriptor, temporary = tempfile.mkstemp(
                        prefix=path.name + ".rollback.", suffix=".tmp", dir=path.parent
                    )
                    with os.fdopen(descriptor, "wb") as handle:
                        handle.write(original)
                        handle.flush()
                        os.fsync(handle.fileno())
                    os.replace(temporary, path)
            except Exception as rollback_error:  # rollback failure must be surfaced
                rollback_errors.append(f"{path}: {rollback_error}")
        if rollback_errors:
            raise RuntimeError(
                f"write failed ({original_error}); rollback also failed: {'; '.join(rollback_errors)}"
            ) from original_error
        raise
    finally:
        for temporary in staged.values():
            if os.path.exists(temporary):
                os.remove(temporary)


def _load_json(path: Path, label: str) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    return _require_object(value, label)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="人工复核碰撞候选并同步字段注册表")
    parser.add_argument("--decisions", required=True, help="docs/field_verification 下的决策 JSON")
    parser.add_argument(
        "--apply", action="store_true", help="应用决策并原子更新 registry 与生成文档"
    )
    args = parser.parse_args(argv)

    try:
        decision_path, decision_rel = _inside_verification_dir(args.decisions, "decision file")
        decision_document = _load_json(decision_path, "decision document")
        report_value = _non_empty_string(
            decision_document.get("report"), "decision document.report"
        )
        report_path, report_rel = _inside_verification_dir(
            report_value, "collision report", relative_base=VERIFY_DIR
        )
        if not report_path.is_file():
            raise FileNotFoundError(f"collision report not found: {report_rel}")
        if not decision_path.is_file():
            raise FileNotFoundError(f"decision file not found: {decision_rel}")
        report = _load_json(report_path, "collision report")
        registry = fra.load_registry(str(REGISTRY_PATH))
        lineage = sla.load_source_lineage(str(LINEAGE_PATH), registry=registry)
        updated, stats = apply_adjudications(
            registry,
            lineage,
            decision_document,
            report,
            report_rel,
            decision_rel,
        )
        print(json.dumps(stats, ensure_ascii=False, sort_keys=True))
        if not args.apply:
            print("Preview only. Re-run with --apply after reviewing the proposed decisions.")
            return 0
        if stats["verified"] == 0 and stats["mappings_added"] == 0:
            print("All decisions were already applied; no files changed.")
            return 0

        outputs = {
            REGISTRY_PATH: json.dumps(updated, ensure_ascii=False, indent=2) + "\n",
            FIELD_DICT_PATH: gfd.render_field_dict(updated) + "\n",
            UNKNOWN_FIELDS_PATH: gfd.render_unknown_fields(updated) + "\n",
            SOURCE_MAP_PATH: gfd.render_source_repository_map(updated, lineage) + "\n",
            METADATA_GAPS_PATH: gfd.render_field_metadata_gaps(updated) + "\n",
        }
        _atomic_write_batch(outputs)
        print(
            "Updated field_registry.json and regenerated field_dict.md, unknown_fields.md, source_repository_map.md, field_metadata_gaps.md"
        )
        return 0
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

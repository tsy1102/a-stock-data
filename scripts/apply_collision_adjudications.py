#!/usr/bin/env python3
"""Apply explicitly reviewed collision, source-contract, or formula decisions.

Collision reports remain discovery-only. Source-contract and derived-relation
decisions use separate evidence routes and never create cross-source mappings.
This command defaults to preview and requires ``--apply`` before updating the
registry and generated views.
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
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import field_registry_api as fra
import collision_candidate_reviews as ccr
import derived_relation_evidence as dre
import gen_field_dict as gfd
import source_lineage_api as sla

from scripts.collision_adjudication_validation import (
    VALID_LEVELS,
    _candidate_identity_for_source,
    _find_l1_candidate,
    _is_placeholder_metadata,
    _is_registry_aggregate_status_conflict,
    _metadata,
    _metadata_snapshot,
    _non_empty_string,
    _require_object,
    _runtime_identity,
    _validate_anchor_metadata_correction,
    _validate_candidate_inventory,
    _validate_candidate_triage,
    _validate_collision_report_sections,
    _validate_complete_collision_report,
    _validate_external_evidence,
    _validate_iso_date,
    _validate_source_contract,
    _validate_source_contract_metadata_correction,
)
from scripts.collision_adjudication_transformations import (
    SAME_MEANING_RELATION,
    _add_verified_mapping,
    _append_adjudication_evidence,
    _append_derived_relation_decision,
    _mapping_key,
    _refresh_aggregate_projection,
)

VALID_ACTIONS = {"verify", "enrich_metadata", "link_verified"}


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
    if report.get("schema_version") not in {3, 4, 5}:
        raise ValueError("unsupported collision report schema_version; expected 3, 4, or 5")
    if report.get("collision_mode") != "verified_anchor_only":
        raise ValueError("only verified_anchor_only collision reports are accepted")
    if report.get("exploratory_pair_count", 0) != 0:
        raise ValueError("exploratory reports cannot be promoted to registry decisions")
    _validate_complete_collision_report(report)

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
    stats = {
        "verified": 0,
        "metadata_enriched": 0,
        "linked": 0,
        "anchor_metadata_corrected": 0,
        "already_applied": 0,
        "mappings_added": 0,
    }

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
        if (
            report.get("schema_version") == 5
            and candidate.get("review_disposition") != "accepted_for_adjudication"
        ):
            raise ValueError(
                "schema 5 collision candidates must be reviewed as "
                "accepted_for_adjudication before registry changes"
            )

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
        candidate_ids = (left_id, right_id)
        _target_field_id, _target_alias = _candidate_identity_for_source(
            candidate_ids, target, lineage, "target"
        )
        _anchor_field_id, anchor_alias = _candidate_identity_for_source(
            candidate_ids, anchor, lineage, "anchor"
        )
        if _target_field_id == _anchor_field_id:
            raise ValueError("target and anchor resolve to the same collision endpoint")
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
        external_evidence = _validate_external_evidence(
            decision.get("external_evidence"), "decision.external_evidence"
        )
        current_status = target_record.get("status", "unverified")
        if target in seen_targets:
            raise ValueError(f"multiple decisions target the same field: {target}")
        seen_targets.add(target)

        if action == "link_verified":
            canonical = ""
            meaning = ""
            unit = ""
        else:
            canonical = _non_empty_string(decision.get("canonical"), "decision.canonical")
            meaning = _non_empty_string(decision.get("meaning"), "decision.meaning")
            unit = decision.get("unit", "")
            if not isinstance(unit, str):
                raise TypeError("decision.unit must be a string")
            unit = unit.strip()

        previous_metadata: dict[str, str] | None = None
        if action == "enrich_metadata":
            previous_metadata = _metadata_snapshot(decision.get("previous"), "decision.previous")
            after_metadata = {"canonical": canonical, "meaning": meaning, "unit": unit}
            if current_status != "verified":
                raise ValueError(
                    f"enrich_metadata requires an already verified target: {target[0]}::{target[1]}"
                )
            if previous_metadata == after_metadata:
                raise ValueError("enrich_metadata must add or correct at least one metadata value")
        elif action == "verify" and current_status not in {"unverified", "candidate"}:
            target_history = target_record.get("adjudications", [])
            already_recorded = isinstance(target_history, list) and any(
                isinstance(item, dict) and item.get("id") == decision_id for item in target_history
            )
            if current_status != "verified" or not already_recorded:
                raise ValueError(
                    f"target status {current_status!r} requires separate conflict review: {target}"
                )
        elif action == "verify" and not all(_metadata(anchor_record).values()):
            if not external_evidence:
                raise ValueError(
                    "verify requires external_evidence when the selected anchor metadata is incomplete"
                )
        elif action == "link_verified":
            if current_status != "verified":
                raise ValueError(
                    f"link_verified requires verified target and anchor records: {target}"
                )
            if not all(_metadata(target_record).values()):
                raise ValueError(
                    f"link_verified requires complete target metadata: {target[0]}::{target[1]}"
                )
            if not all(_metadata(anchor_record).values()):
                raise ValueError(
                    f"link_verified requires complete anchor metadata: {anchor[0]}::{anchor[1]}"
                )

        anchor_correction = _validate_anchor_metadata_correction(
            decision.get("anchor_metadata_correction")
        )
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
        if action == "enrich_metadata":
            adjudication["metadata_change"] = {
                "before": previous_metadata,
                "after": {"canonical": canonical, "meaning": meaning, "unit": unit},
            }
        if anchor_correction:
            adjudication["anchor_metadata_correction"] = copy.deepcopy(anchor_correction)
        if action == "link_verified":
            adjudication["target"] = {"source": target[0], "code": target[1]}
            adjudication["anchor"] = {"source": anchor[0], "code": anchor[1]}
        if external_evidence:
            adjudication["external_evidence"] = external_evidence

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
            if action != "link_verified" and (
                target_record.get("canonical") != canonical
                or target_record.get("meaning") != meaning
                or target_record.get("unit", "") != unit
            ):
                raise ValueError(f"decision id reuses different field attributes: {decision_id}")
            if anchor_correction:
                anchor_id = f"{decision_id}-anchor"
                anchor_history = anchor_record.get("adjudications", [])
                anchor_prior = (
                    next(
                        (
                            item
                            for item in anchor_history
                            if isinstance(item, dict) and item.get("id") == anchor_id
                        ),
                        None,
                    )
                    if isinstance(anchor_history, list)
                    else None
                )
                expected_anchor_metadata = anchor_correction["updated"]
                if (
                    anchor_prior is None
                    or anchor_prior.get("metadata_change")
                    != {
                        "before": anchor_correction["previous"],
                        "after": expected_anchor_metadata,
                    }
                    or _metadata(anchor_record) != expected_anchor_metadata
                ):
                    raise ValueError(
                        f"anchor metadata correction is partially applied or differs: {anchor}"
                    )
            evidence = f"adjudication:{decision_path}#{decision_id};report:{report_path}"
            if _add_verified_mapping(updated, target, anchor, evidence):
                stats["mappings_added"] += 1
            stats["already_applied"] += 1
            continue

        if action == "enrich_metadata":
            current_metadata = _metadata(target_record)
            if current_metadata != previous_metadata:
                raise ValueError(f"target metadata changed since review: {target[0]}::{target[1]}")
            if (
                current_metadata["canonical"] not in {"", target[1], canonical}
                or current_metadata["meaning"] not in {"", meaning}
                or current_metadata["unit"] not in {"", unit}
            ):
                raise ValueError(
                    f"enrich_metadata cannot overwrite established metadata: {target[0]}::{target[1]}"
                )
            target_record.update({"canonical": canonical, "meaning": meaning, "unit": unit})
            stats["metadata_enriched"] += 1
        elif action == "link_verified":
            stats["linked"] += 1
        else:
            target_record.update(
                {
                    "canonical": canonical,
                    "meaning": meaning,
                    "unit": unit,
                    "status": "verified",
                    "status_resolution": "manual_collision_adjudication",
                }
            )
            stats["verified"] += 1
        evidence = f"adjudication:{decision_path}#{decision_id};report:{report_path}"
        if _add_verified_mapping(updated, target, anchor, evidence):
            stats["mappings_added"] += 1
        if action != "link_verified":
            affected_codes.add(target[1])

        _append_adjudication_evidence(target_record, adjudication)

        if anchor_correction:
            if _metadata(anchor_record) != anchor_correction["previous"]:
                raise ValueError(f"anchor metadata changed since review: {anchor[0]}::{anchor[1]}")
            anchor_id = f"{decision_id}-anchor"
            anchor_adjudication = {
                "id": anchor_id,
                "action": "correct_metadata",
                "status": anchor_record.get("status", "verified"),
                "reviewer": reviewer,
                "reviewed_on": reviewed_on,
                "report": report_path,
                "decision_file": decision_path,
                "candidate": {"left": left_id, "right": right_id},
                "level": candidate["level"],
                "rationale": anchor_correction["rationale"],
                "metadata_change": {
                    "before": anchor_correction["previous"],
                    "after": anchor_correction["updated"],
                },
                "external_evidence": anchor_correction["external_evidence"],
            }
            anchor_record.update(anchor_correction["updated"])
            _append_adjudication_evidence(anchor_record, anchor_adjudication)
            stats["anchor_metadata_corrected"] += 1
            affected_codes.add(anchor[1])

    if affected_codes:
        _refresh_aggregate_projection(updated, affected_codes)
    return updated, stats


def apply_source_contract_adjudications(
    registry: dict[str, Any], decision_document: dict[str, Any], decision_path: str
) -> tuple[dict[str, Any], dict[str, int]]:
    """Verify individual field contracts without asserting cross-source equivalence."""
    if decision_document.get("schema_version") != 1:
        raise ValueError("unsupported source-contract adjudication schema_version")
    if decision_document.get("evidence_basis") != "source_contract":
        raise ValueError("source-contract decisions require evidence_basis='source_contract'")
    if decision_document.get("report"):
        raise ValueError("source-contract decisions cannot include a collision report")

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
    stats = {
        "source_contract_verified": 0,
        "status_conflicts_resolved": 0,
        "metadata_corrected": 0,
        "already_applied": 0,
        "mappings_added": 0,
    }

    for raw_decision in decisions:
        decision = _require_object(raw_decision, "decision")
        decision_id = _non_empty_string(decision.get("id"), "decision.id")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,127}", decision_id):
            raise ValueError(f"decision.id contains unsupported characters: {decision_id!r}")
        if decision_id in seen_ids:
            raise ValueError(f"duplicate decision id: {decision_id}")
        seen_ids.add(decision_id)
        if decision.get("action") != "verify_source_contract":
            raise ValueError(
                "source-contract workflow only accepts action='verify_source_contract'"
            )

        target_obj = _require_object(decision.get("target"), "decision.target")
        target = (
            _non_empty_string(target_obj.get("source"), "target.source"),
            _non_empty_string(target_obj.get("code"), "target.code"),
        )
        if target in seen_targets:
            raise ValueError(f"multiple decisions target the same field: {target}")
        seen_targets.add(target)
        target_record = by_identity.get(target)
        if target_record is None:
            raise ValueError(f"unknown target source field: {target[0]}::{target[1]}")

        previous_status = _non_empty_string(
            decision.get("previous_status"), "decision.previous_status"
        )
        if previous_status not in {"unverified", "candidate", "conflict"}:
            raise ValueError(
                "source-contract verification only accepts unverified, candidate, "
                "or resolvable status-conflict fields"
            )
        previous_resolution = _non_empty_string(
            decision.get("previous_status_resolution"), "decision.previous_status_resolution"
        )
        previous_metadata = _metadata_snapshot(decision.get("previous"), "decision.previous")
        canonical = _non_empty_string(decision.get("canonical"), "decision.canonical")
        meaning = _non_empty_string(decision.get("meaning"), "decision.meaning")
        unit = decision.get("unit", "")
        if not isinstance(unit, str):
            raise TypeError("decision.unit must be a string")
        unit = unit.strip()
        rationale = _non_empty_string(decision.get("rationale"), "decision.rationale")
        source_contract = _validate_source_contract(
            decision.get("source_contract"), "decision.source_contract"
        )
        after_metadata = {"canonical": canonical, "meaning": meaning, "unit": unit}
        metadata_correction = _validate_source_contract_metadata_correction(
            decision.get("metadata_correction"), previous_metadata, after_metadata
        )
        section = (
            f"source contract: {source_contract['authority']} · {source_contract['path']}"
            f"#{source_contract['locator']} @ {source_contract['revision']}"
        )
        adjudication = {
            "id": decision_id,
            "action": "verify_source_contract",
            "status": "verified",
            "reviewer": reviewer,
            "reviewed_on": reviewed_on,
            "decision_file": decision_path,
            "evidence_basis": "authoritative_source_contract",
            "previous_status": previous_status,
            "status_resolution_change": {
                "before": previous_resolution,
                "after": "verified_by_source_contract",
            },
            "metadata_change": {"before": previous_metadata, "after": after_metadata},
            "rationale": rationale,
            "source_contract": source_contract,
        }
        if metadata_correction is not None:
            adjudication["metadata_correction"] = copy.deepcopy(metadata_correction)

        history = target_record.get("adjudications", [])
        if not isinstance(history, list):
            raise TypeError("source field adjudications must be a list")
        prior = next(
            (item for item in history if isinstance(item, dict) and item.get("id") == decision_id),
            None,
        )
        if prior is not None:
            if (
                prior != adjudication
                or target_record.get("status") != "verified"
                or _metadata(target_record) != after_metadata
                or target_record.get("status_resolution") != "verified_by_source_contract"
            ):
                raise ValueError(
                    f"decision id already exists with different content: {decision_id}"
                )
            stats["already_applied"] += 1
            continue

        current_status = target_record.get("status", "unverified")
        current_resolution = target_record.get("status_resolution") or "status_missing"
        if current_status != previous_status or current_resolution != previous_resolution:
            raise ValueError(f"target status changed since review: {target[0]}::{target[1]}")
        if previous_status == "conflict":
            if (
                previous_resolution != "status_conflict"
                or not _is_registry_aggregate_status_conflict(target_record)
            ):
                raise ValueError(
                    "source-contract verification cannot resolve semantic or attribute conflicts"
                )
        if _metadata(target_record) != previous_metadata:
            raise ValueError(f"target metadata changed since review: {target[0]}::{target[1]}")
        requires_correction = False
        for key, new_value in after_metadata.items():
            old_value = previous_metadata[key]
            if old_value != new_value and not _is_placeholder_metadata(old_value, key, target[1]):
                requires_correction = True
        if requires_correction and metadata_correction is None:
            changed_keys = [
                key
                for key, new_value in after_metadata.items()
                if previous_metadata[key] != new_value
                and not _is_placeholder_metadata(previous_metadata[key], key, target[1])
            ]
            raise ValueError(
                "source-contract verification cannot overwrite established "
                f"{', '.join(changed_keys)} without an explicit metadata_correction"
            )
        if not requires_correction and metadata_correction is not None:
            raise ValueError(
                "metadata_correction is only valid when correcting established metadata"
            )

        target_record.update(after_metadata)
        target_record["status"] = "verified"
        target_record["status_resolution"] = "verified_by_source_contract"
        target_record.setdefault("adjudications", []).append(copy.deepcopy(adjudication))

        reference_evidence = target_record.setdefault("reference_evidence", [])
        if not isinstance(reference_evidence, list):
            raise TypeError("source field reference_evidence must be a list")
        reference_evidence.append(
            {
                "section": section,
                **after_metadata,
                "status_raw": f"人工核验上游契约 {reviewed_on}：{decision_id}",
                "status": "verified",
                "adjudication_id": decision_id,
                "evidence_basis": "authoritative_source_contract",
                "source_contract": copy.deepcopy(source_contract),
                "metadata_change": copy.deepcopy(adjudication["metadata_change"]),
            }
        )
        sections = target_record.setdefault("sections", [])
        if not isinstance(sections, list):
            raise TypeError("source field sections must be a list")
        if section not in sections:
            sections.append(section)
            sections.sort()
        if not target_record.get("section"):
            target_record["section"] = section

        status_evidence = target_record.setdefault("status_evidence", {})
        if not isinstance(status_evidence, dict):
            raise TypeError("source field status_evidence must be an object")
        adjudication_ids = status_evidence.setdefault("adjudication_ids", [])
        if not isinstance(adjudication_ids, list):
            raise TypeError("source field status_evidence.adjudication_ids must be a list")
        if decision_id not in adjudication_ids:
            adjudication_ids.append(decision_id)
        contract_ids = status_evidence.setdefault("source_contract_adjudication_ids", [])
        if not isinstance(contract_ids, list):
            raise TypeError(
                "source field status_evidence.source_contract_adjudication_ids must be a list"
            )
        if decision_id not in contract_ids:
            contract_ids.append(decision_id)

        affected_codes.add(target[1])
        stats["source_contract_verified"] += 1
        if previous_status == "conflict":
            stats["status_conflicts_resolved"] += 1
        if metadata_correction is not None:
            stats["metadata_corrected"] += 1

    if affected_codes:
        _refresh_aggregate_projection(updated, affected_codes)
    return updated, stats


def _prepare_derived_relation_decision(
    raw_decision: Any,
    reviewer: str,
    reviewed_on: str,
    decision_path: str,
    by_identity: dict[tuple[str, str], dict[str, Any]],
    lineage: dict[str, Any],
) -> dict[str, Any]:
    decision = _require_object(raw_decision, "decision")
    if any(marker in reviewer.casefold() for marker in ("填写", "占位", "待确认", "待验证")):
        raise ValueError("reviewer must replace the template placeholder")
    decision_id = _non_empty_string(decision.get("id"), "decision.id")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,127}", decision_id):
        raise ValueError(f"decision.id contains unsupported characters: {decision_id!r}")
    if decision.get("action") != "verify_derived_relation":
        raise ValueError("derived-relation decisions require action='verify_derived_relation'")
    target_obj = _require_object(decision.get("target"), "decision.target")
    target = (
        _non_empty_string(target_obj.get("source"), "target.source"),
        _non_empty_string(target_obj.get("code"), "target.code"),
    )
    target_record = by_identity.get(target)
    if target_record is None:
        raise ValueError(f"unknown target source field: {target[0]}::{target[1]}")
    previous_status = _non_empty_string(decision.get("previous_status"), "decision.previous_status")
    if previous_status not in {"unverified", "candidate"}:
        raise ValueError(
            "derived-relation verification only accepts unverified or candidate fields"
        )
    previous_resolution = _non_empty_string(
        decision.get("previous_status_resolution"), "decision.previous_status_resolution"
    )
    previous_metadata = _metadata_snapshot(decision.get("previous"), "decision.previous")
    after_metadata = {
        key: _non_empty_string(decision.get(key), f"decision.{key}")
        for key in ("canonical", "meaning", "unit")
    }
    for key, new_value in after_metadata.items():
        if _is_placeholder_metadata(new_value, key, target[1]):
            raise ValueError(f"derived-relation evidence requires a concrete {key}")
        old_value = previous_metadata[key]
        if old_value != new_value and not _is_placeholder_metadata(old_value, key, target[1]):
            raise ValueError(f"derived-relation evidence cannot overwrite established {key}")
    rationale = _non_empty_string(decision.get("rationale"), "decision.rationale")
    if any(marker in rationale.casefold() for marker in ("填写", "占位", "待确认", "待验证")):
        raise ValueError("decision.rationale must replace the template placeholder")
    formula_evidence = dre.validate_derived_relation(
        decision.get("formula_evidence"), target, by_identity, lineage, VERIFY_DIR, reviewed_on
    )
    section = (
        f"derived relation: {formula_evidence['expression']} · {formula_evidence['sample_file']}"
    )
    adjudication = {
        "id": decision_id,
        "action": "verify_derived_relation",
        "status": "verified",
        "reviewer": reviewer,
        "reviewed_on": reviewed_on,
        "decision_file": decision_path,
        "evidence_basis": "derived_relation",
        "previous_status": previous_status,
        "status_resolution_change": {
            "before": previous_resolution,
            "after": "verified_by_derived_relation",
        },
        "metadata_change": {"before": previous_metadata, "after": after_metadata},
        "rationale": rationale,
        "formula_evidence": formula_evidence,
    }
    return {
        "id": decision_id,
        "target": target,
        "record": target_record,
        "previous_status": previous_status,
        "previous_status_resolution": previous_resolution,
        "previous_metadata": previous_metadata,
        "after_metadata": after_metadata,
        "adjudication": adjudication,
        "section": section,
    }


def apply_derived_relation_adjudications(
    registry: dict[str, Any],
    lineage: dict[str, Any],
    decision_document: dict[str, Any],
    decision_path: str,
) -> tuple[dict[str, Any], dict[str, int]]:
    """Verify unknown fields through independently sourced, replayable equations."""
    if decision_document.get("schema_version") != 1:
        raise ValueError("unsupported derived-relation schema_version")
    if decision_document.get("evidence_basis") != "derived_relation":
        raise ValueError("derived-relation decisions require evidence_basis='derived_relation'")
    if decision_document.get("report"):
        raise ValueError("derived-relation decisions cannot include a collision report")
    reviewer = _non_empty_string(decision_document.get("reviewer"), "reviewer")
    reviewed_on = _validate_iso_date(decision_document.get("reviewed_on"), "reviewed_on")
    decisions = decision_document.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise ValueError("decisions must be a non-empty list")

    updated = copy.deepcopy(registry)
    by_identity = {
        (record["source"], record["code"]): record for record in fra.source_field_records(updated)
    }
    seen_ids: set[str] = set()
    seen_targets: set[tuple[str, str]] = set()
    affected_codes: set[str] = set()
    stats = {"derived_relation_verified": 0, "already_applied": 0, "mappings_added": 0}
    for raw_decision in decisions:
        payload = _prepare_derived_relation_decision(
            raw_decision, reviewer, reviewed_on, decision_path, by_identity, lineage
        )
        decision_id = payload["id"]
        target = payload["target"]
        if decision_id in seen_ids:
            raise ValueError(f"duplicate decision id: {decision_id}")
        if target in seen_targets:
            raise ValueError(f"multiple decisions target the same field: {target}")
        seen_ids.add(decision_id)
        seen_targets.add(target)
        if _append_derived_relation_decision(payload):
            stats["derived_relation_verified"] += 1
            affected_codes.add(target[1])
        else:
            stats["already_applied"] += 1
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
    parser = argparse.ArgumentParser(description="复核字段证据并同步字段注册表")
    parser.add_argument("--decisions", required=True, help="docs/field_verification 下的决策 JSON")
    parser.add_argument(
        "--apply", action="store_true", help="应用决策并原子更新 registry 与生成文档"
    )
    args = parser.parse_args(argv)

    try:
        decision_path, decision_rel = _inside_verification_dir(args.decisions, "decision file")
        if not decision_path.is_file():
            raise FileNotFoundError(f"decision file not found: {decision_rel}")
        decision_document = _load_json(decision_path, "decision document")
        registry = fra.load_registry(str(REGISTRY_PATH))
        evidence_basis = decision_document.get("evidence_basis")
        lineage: dict[str, Any] | None = None
        if evidence_basis == "source_contract":
            updated, stats = apply_source_contract_adjudications(
                registry, decision_document, decision_rel
            )
        elif evidence_basis == "derived_relation":
            lineage = sla.load_source_lineage(str(LINEAGE_PATH), registry=registry)
            updated, stats = apply_derived_relation_adjudications(
                registry, lineage, decision_document, decision_rel
            )
        elif evidence_basis is None:
            lineage = sla.load_source_lineage(str(LINEAGE_PATH), registry=registry)
            report_value = _non_empty_string(
                decision_document.get("report"), "decision document.report"
            )
            report_path, report_rel = _inside_verification_dir(
                report_value, "collision report", relative_base=VERIFY_DIR
            )
            if not report_path.is_file():
                raise FileNotFoundError(f"collision report not found: {report_rel}")
            report = _load_json(report_path, "collision report")
            updated, stats = apply_adjudications(
                registry,
                lineage,
                decision_document,
                report,
                report_rel,
                decision_rel,
            )
        else:
            raise ValueError(f"unsupported adjudication evidence_basis: {evidence_basis!r}")
        print(json.dumps(stats, ensure_ascii=False, sort_keys=True))
        if not args.apply:
            print("Preview only. Re-run with --apply after reviewing the proposed decisions.")
            return 0
        if not any(
            stats.get(key, 0)
            for key in (
                "verified",
                "source_contract_verified",
                "derived_relation_verified",
                "metadata_enriched",
                "linked",
                "anchor_metadata_corrected",
                "mappings_added",
            )
        ):
            print("All decisions were already applied; no files changed.")
            return 0

        if lineage is None:
            lineage = sla.load_source_lineage(str(LINEAGE_PATH), registry=registry)
        outputs = {
            REGISTRY_PATH: json.dumps(updated, ensure_ascii=False, indent=2) + "\n",
            FIELD_DICT_PATH: gfd.render_field_dict(updated),
            UNKNOWN_FIELDS_PATH: gfd.render_unknown_fields(updated),
            SOURCE_MAP_PATH: gfd.render_source_repository_map(updated, lineage),
            METADATA_GAPS_PATH: gfd.render_field_metadata_gaps(updated),
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

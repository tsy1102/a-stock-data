"""Pure schema, identity, and evidence validation for adjudication inputs."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlsplit

import collision_candidate_reviews as ccr
import source_lineage_api as sla

VALID_LEVELS = {"L1", "L1-U"}


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
    return alias, sla.normalize_runtime_field_code(alias, code)


def _candidate_identity_for_source(
    candidate_ids: tuple[str, str],
    source_field: tuple[str, str],
    lineage: dict[str, Any],
    label: str,
) -> tuple[str, str]:
    """Resolve a registered identity to either endpoint of a symmetric pair."""
    source, expected_code = source_field
    aliases = sla.runtime_aliases_for_source(source, lineage)
    matches: list[tuple[str, str]] = []
    for field_id in candidate_ids:
        if not any(
            field_id.startswith(alias + ".") or field_id.startswith(alias + "[")
            for alias in aliases
        ):
            continue
        alias, code = _runtime_identity(field_id, source, lineage)
        if code == expected_code:
            matches.append((field_id, alias))
    if len(matches) != 1:
        raise ValueError(
            f"{label} {source}::{expected_code} does not match report field endpoint exactly once; "
            f"matched {len(matches)}"
        )
    return matches[0]


def _metadata_snapshot(value: Any, label: str) -> dict[str, str]:
    snapshot = _require_object(value, label)
    if set(snapshot) != {"canonical", "meaning", "unit"}:
        raise ValueError(f"{label} must contain exactly canonical, meaning, and unit")
    if any(not isinstance(snapshot[key], str) for key in snapshot):
        raise TypeError(f"{label} values must be strings")
    return {key: snapshot[key].strip() for key in ("canonical", "meaning", "unit")}


def _metadata(record: dict[str, Any]) -> dict[str, str]:
    return {key: str(record.get(key, "") or "").strip() for key in ("canonical", "meaning", "unit")}


def _validate_external_evidence(value: Any, label: str) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty URL list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{label} entries must be HTTPS URLs")
    urls = [item.strip() for item in value]
    if any(
        urlsplit(item).scheme != "https"
        or not urlsplit(item).hostname
        or urlsplit(item).username is not None
        for item in urls
    ):
        raise ValueError(f"{label} entries must be HTTPS URLs with a hostname")
    return urls


def _validate_source_contract(value: Any, label: str) -> dict[str, str]:
    contract = _require_object(value, label)
    required = {"authority", "revision", "path", "locator", "url"}
    if set(contract) != required:
        raise ValueError(f"{label} must contain exactly {', '.join(sorted(required))}")
    normalized = {
        key: _non_empty_string(contract.get(key), f"{label}.{key}")
        for key in ("authority", "revision", "path", "locator")
    }
    revision_key = normalized["revision"].casefold()
    if revision_key in {"main", "master", "latest", "current", "head"}:
        raise ValueError(f"{label}.revision must identify a pinned version or dated document")
    urls = _validate_external_evidence([contract.get("url")], f"{label}.url")
    if urls is None:
        raise ValueError(f"{label}.url must be an HTTPS evidence URL")
    normalized["url"] = urls[0]
    return normalized


def _is_registry_aggregate_status_conflict(record: dict[str, Any]) -> bool:
    """Identify a status-only conflict caused by the aggregate registry projection."""
    evidence = record.get("status_evidence")
    if not isinstance(evidence, dict):
        return False
    reference_statuses = evidence.get("reference_statuses")
    values = evidence.get("values")
    if not isinstance(reference_statuses, list) or any(
        not isinstance(status, str) for status in reference_statuses
    ):
        return False
    if set(reference_statuses) != {"verified"}:
        return False
    if not isinstance(values, list) or any(not isinstance(status, str) for status in values):
        return False
    if set(values) != {"verified", "unverified"}:
        return False
    if evidence.get("registry_aggregate_status") != "unverified":
        return False
    attribute_conflicts = record.get("attribute_conflicts")
    if attribute_conflicts not in (None, {}, []):
        return False
    reference_evidence = record.get("reference_evidence")
    if not isinstance(reference_evidence, list) or not reference_evidence:
        return False
    reference_evidence_statuses: set[str] = set()
    for item in reference_evidence:
        if not isinstance(item, dict):
            return False
        status = item.get("status")
        if not isinstance(status, str) or not status:
            return False
        reference_evidence_statuses.add(status)
    return reference_evidence_statuses == {"verified"}


def _validate_source_contract_metadata_correction(
    value: Any,
    previous: dict[str, str],
    updated: dict[str, str],
) -> dict[str, Any] | None:
    if value is None:
        return None
    correction = _require_object(value, "metadata_correction")
    if set(correction) != {"previous", "updated", "rationale"}:
        raise ValueError(
            "metadata_correction must contain exactly previous, updated, and rationale"
        )
    correction_previous = _metadata_snapshot(
        correction.get("previous"), "metadata_correction.previous"
    )
    correction_updated = _metadata_snapshot(
        correction.get("updated"), "metadata_correction.updated"
    )
    rationale = _non_empty_string(correction.get("rationale"), "metadata_correction.rationale")
    if correction_previous != previous or correction_updated != updated:
        raise ValueError("metadata_correction must exactly match the decision metadata snapshots")
    if correction_previous == correction_updated:
        raise ValueError("metadata_correction must change at least one established value")
    return {
        "previous": correction_previous,
        "updated": correction_updated,
        "rationale": rationale,
    }


def _is_placeholder_metadata(value: str, key: str, code: str) -> bool:
    normalized = value.strip()
    if not normalized:
        return True
    if key == "canonical" and normalized == code:
        return True
    return normalized.casefold() in {
        "待破解",
        "待确认",
        "待验证",
        "未验证",
        "未定义",
        "未知",
        "unknown",
        "tbd",
        "n/a",
        "na",
        "—",
        "-",
    }


def _validate_anchor_metadata_correction(
    value: Any, label: str = "anchor_metadata_correction"
) -> dict[str, Any] | None:
    if value is None:
        return None
    correction = _require_object(value, label)
    previous = _metadata_snapshot(correction.get("previous"), f"{label}.previous")
    updated = _metadata_snapshot(correction.get("updated"), f"{label}.updated")
    rationale = _non_empty_string(correction.get("rationale"), f"{label}.rationale")
    external_evidence = _validate_external_evidence(
        correction.get("external_evidence"), f"{label}.external_evidence"
    )
    if external_evidence is None:
        raise ValueError(f"{label}.external_evidence must be a non-empty URL list")
    if previous == updated:
        raise ValueError(f"{label} must change at least one metadata value")
    return {
        "previous": previous,
        "updated": updated,
        "rationale": rationale,
        "external_evidence": list(external_evidence),
    }


def _find_l1_candidate(report: dict[str, Any], left: str, right: str) -> dict[str, Any]:
    candidates = report.get("actionable_L1", report.get("L1"))
    if not isinstance(candidates, list):
        raise TypeError("collision report actionable_L1/L1 must be a list")
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
    if candidate.get("in_registry"):
        raise ValueError(
            "registered mappings are revalidation evidence, not new adjudication candidates"
        )
    if candidate.get("hub_flag"):
        raise ValueError("hub-flagged collision candidates cannot be adjudicated")
    if int(candidate.get("n_days", 0)) < 3:
        raise ValueError("L1 candidate must contain at least three independent trading days")
    return candidate


def _validate_candidate_inventory(report: dict[str, Any], summary: dict[str, Any]) -> int:
    method_candidate_count = report.get("method_candidate_count")
    inventory = report.get("method_candidate_inventory")
    if type(method_candidate_count) is not int or method_candidate_count < 0:
        raise ValueError("collision report has an invalid method_candidate_count")
    if not isinstance(inventory, list):
        raise ValueError("collision report has no complete method_candidate_inventory")

    candidate_pairs: list[tuple[str, str]] = []
    for row in inventory:
        if not isinstance(row, dict):
            raise ValueError("collision report method candidate inventory contains an invalid row")
        left, right = row.get("left"), row.get("right")
        if not isinstance(left, str) or not left or not isinstance(right, str) or not right:
            raise ValueError("collision report method candidate inventory contains an invalid pair")
        candidate_pairs.append((left, right))

    unique_pair_count = len(set(candidate_pairs))
    inventory_expectations = {
        "generated_count": method_candidate_count,
        "saved_count": len(inventory),
        "unique_pair_count": unique_pair_count,
        "missing_detail_count": max(0, method_candidate_count - len(inventory)),
        "excess_detail_count": max(0, len(inventory) - method_candidate_count),
        "duplicate_pair_count": len(candidate_pairs) - unique_pair_count,
        "invalid_pair_identity_count": 0,
    }
    for key, expected in inventory_expectations.items():
        if summary.get(key) != expected:
            raise ValueError(f"collision report completeness inventory mismatch: {key}")
    if any(
        summary.get(key) != 0
        for key in (
            "missing_detail_count",
            "excess_detail_count",
            "duplicate_pair_count",
            "invalid_pair_identity_count",
        )
    ):
        raise ValueError(
            "collision report completeness inventory contains missing or duplicate details"
        )
    return method_candidate_count


def _validate_candidate_triage(
    report: dict[str, Any], inventory_summary: dict[str, Any], method_candidate_count: int
) -> list[dict[str, Any]]:
    triage = report.get("candidate_triage")
    triage_summary = triage.get("summary") if isinstance(triage, dict) else None
    targets = triage.get("targets") if isinstance(triage, dict) else None
    if not isinstance(triage_summary, dict) or not isinstance(targets, list):
        raise ValueError("collision report is missing full candidate triage")
    target_candidate_count = 0
    for target in targets:
        count = target.get("candidate_count") if isinstance(target, dict) else None
        if type(count) is not int or count < 0:
            raise ValueError(
                "collision report candidate triage contains an invalid candidate count"
            )
        target_candidate_count += count
    if triage_summary.get("target_count") != len(targets):
        raise ValueError("collision report candidate triage target count mismatch")
    if target_candidate_count != method_candidate_count:
        raise ValueError("collision report candidate triage does not cover all method candidates")
    if inventory_summary.get("target_candidate_count_sum") != target_candidate_count:
        raise ValueError("collision report completeness candidate count sum mismatch")
    if inventory_summary.get("invalid_target_candidate_count_rows") != 0:
        raise ValueError("collision report completeness has invalid target candidate counts")
    return targets


def _validate_collision_report_sections(
    report: dict[str, Any], completeness: dict[str, Any], targets: list[dict[str, Any]]
) -> None:
    sections = completeness.get("sections")
    if not isinstance(sections, dict):
        raise ValueError("collision report completeness has no section inventory")
    section_records = {
        "L1": report.get("L1"),
        "actionable_L1": report.get("actionable_L1"),
        "mapped_pair_revalidations": report.get("mapped_pair_revalidations"),
        "candidate_triage.targets": targets,
    }
    if report.get("schema_version", 0) >= 4:
        section_records["source_coverage"] = report.get("source_coverage")
    for name, rows in section_records.items():
        section = sections.get(name)
        if not isinstance(rows, list) or not isinstance(section, dict):
            raise ValueError(f"collision report completeness is missing section {name}")
        if section.get("json_record_count") != len(rows):
            raise ValueError(f"collision report completeness section count mismatch: {name}")


def _validate_complete_collision_report(report: dict[str, Any]) -> None:
    """Require the current report schema and a self-consistent full-evidence inventory."""
    completeness = report.get("report_completeness")
    if not isinstance(completeness, dict) or completeness.get("schema_version") != 1:
        raise ValueError("collision report is missing supported report_completeness metadata")
    if completeness.get("status") != "complete" or completeness.get("issues") != []:
        raise ValueError("collision report report_completeness is not complete")
    inventory_summary = completeness.get("method_candidate_inventory")
    if not isinstance(inventory_summary, dict):
        raise ValueError("collision report completeness has no method inventory summary")
    method_candidate_count = _validate_candidate_inventory(report, inventory_summary)
    targets = _validate_candidate_triage(report, inventory_summary, method_candidate_count)
    _validate_collision_report_sections(report, completeness, targets)
    if report.get("schema_version", 0) >= 5:
        review_validation = ccr.validate_report_summary(report)
        if review_validation.get("status") != "complete":
            raise ValueError(
                "collision report candidate review identities/statuses are inconsistent"
            )
        recorded_review_validation = completeness.get("candidate_review")
        if recorded_review_validation != review_validation:
            raise ValueError("collision report candidate review completeness is inconsistent")

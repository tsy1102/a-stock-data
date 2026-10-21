"""Auditable human review state for collision candidates.

This ledger is deliberately separate from both exploratory history and the
field registry. A review disposition can organize evidence, but it cannot
promote a field or change collection behavior.
"""

from __future__ import annotations

import copy
import datetime as dt
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
# Bump when candidate methods, normalization, or sample-qualification semantics change.
METHOD_VERSION = "collision-candidate-v1"
DISPOSITIONS = frozenset(
    {
        "duplicate_grouped",
        "insufficient_evidence",
        "needs_external_evidence",
        "accepted_for_adjudication",
        "rejected",
    }
)
UNREVIEWED = "unreviewed"
ALL_DISPOSITIONS = tuple(sorted((*DISPOSITIONS, UNREVIEWED)))
VERIFY_DIR = Path(__file__).resolve().parents[1] / "docs" / "field_verification"
STATE_PATH = VERIFY_DIR / "collision_candidate_reviews.json"
TEMP_DIR = Path(__file__).resolve().parents[1] / ".tmp"
_CANDIDATE_ID_RE = re.compile(r"cc1_[0-9a-f]{64}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_TRANSIENT_CANDIDATE_KEYS = {
    "candidate_id",
    "review_disposition",
    "reviewed_at",
    "reviewer",
    "review_rationale",
    "review_evidence_refs",
    "review_event_id",
    "duplicate_of",
    "research_history",
}


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def candidate_identity_payload(candidate: dict[str, Any], kind: str) -> dict[str, Any]:
    """Bind an identity to the exact evidence, method version, and sample qualification."""
    if not isinstance(candidate, dict):
        raise TypeError("candidate must be an object")
    if not isinstance(kind, str) or not kind.strip():
        raise ValueError("candidate kind must be a non-empty string")
    left, right = candidate.get("left"), candidate.get("right")
    has_pair = isinstance(left, str) and bool(left) and isinstance(right, str) and bool(right)
    has_formula = (
        kind == "formula_candidate"
        and isinstance(left, str)
        and bool(left)
        and isinstance(candidate.get("right_inputs"), list)
        and bool(candidate["right_inputs"])
        and all(isinstance(item, str) and item for item in candidate["right_inputs"])
    )
    if not has_pair and not has_formula:
        raise ValueError("candidate must contain a field pair or a valid formula target and inputs")
    evidence = {
        key: value for key, value in candidate.items() if key not in _TRANSIENT_CANDIDATE_KEYS
    }
    # Serialization here also rejects non-JSON values and NaN/Infinity before an ID is issued.
    _canonical_json(evidence)
    return {
        "schema_version": SCHEMA_VERSION,
        "method_version": METHOD_VERSION,
        "kind": kind,
        "evidence": evidence,
    }


def candidate_id_from_payload(identity: dict[str, Any]) -> str:
    if not isinstance(identity, dict):
        raise TypeError("candidate identity must be an object")
    encoded = _canonical_json(identity).encode("utf-8")
    return "cc1_" + hashlib.sha256(encoded).hexdigest()


def candidate_id(candidate: dict[str, Any], kind: str) -> str:
    return candidate_id_from_payload(candidate_identity_payload(candidate, kind))


def _candidate_scopes(report: dict[str, Any]) -> list[tuple[str, Any]]:
    scopes: list[tuple[str, Any]] = []
    for section, kind in (
        ("method_candidate_inventory", "method_pair"),
        ("actionable_L1", "l1_candidate"),
        ("L1-C", "l1_contract_candidate"),
        ("L4", "l4_candidate"),
        ("formula_candidates", "formula_candidate"),
    ):
        rows = report.get(section)
        if isinstance(rows, list):
            scopes.extend((kind, row) for row in rows)
    if "actionable_L1" not in report:
        rows = report.get("L1")
        if isinstance(rows, list):
            scopes.extend(
                ("l1_candidate", row)
                for row in rows
                if isinstance(row, dict) and not row.get("in_registry")
            )
    return scopes


def candidate_ids_in_report(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return candidate IDs and their reviewable identity payloads for a report."""
    result: dict[str, dict[str, Any]] = {}
    for kind, row in _candidate_scopes(report):
        if not isinstance(row, dict):
            raise ValueError(f"candidate section contains a non-object row: {kind}")
        identity = candidate_identity_payload(row, kind)
        identifier = candidate_id_from_payload(identity)
        stored_identifier = row.get("candidate_id")
        if stored_identifier is not None and stored_identifier != identifier:
            raise ValueError(f"candidate identity mismatch: {stored_identifier}")
        existing = result.get(identifier)
        if existing is not None and existing != identity:
            raise ValueError(f"duplicate candidate ID has conflicting evidence: {identifier}")
        result[identifier] = identity
    return result


def empty_state() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "updated_at": "", "reviews": {}}


def _valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _validate_event(event: Any, candidate_key: str) -> bool:
    if not isinstance(event, dict):
        return False
    required = {
        "event_id",
        "candidate_id",
        "disposition",
        "reviewer",
        "reviewed_at",
        "rationale",
        "evidence_refs",
        "duplicate_of",
    }
    if set(event) != required:
        return False
    if event.get("candidate_id") != candidate_key:
        return False
    if not isinstance(event.get("event_id"), str) or not _SHA256_RE.fullmatch(event["event_id"]):
        return False
    if not isinstance(event.get("disposition"), str) or event["disposition"] not in DISPOSITIONS:
        return False
    if not isinstance(event.get("reviewer"), str) or not event["reviewer"].strip():
        return False
    if not _valid_timestamp(event.get("reviewed_at")):
        return False
    if not isinstance(event.get("rationale"), str) or not event["rationale"].strip():
        return False
    refs = event.get("evidence_refs")
    if not isinstance(refs, list) or not refs:
        return False
    for ref in refs:
        if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
            return False
        if not isinstance(ref.get("path"), str) or not ref["path"].strip():
            return False
        digest = ref.get("sha256")
        if digest is not None and (not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest)):
            return False
    duplicate_of = event.get("duplicate_of")
    if event["disposition"] == "duplicate_grouped":
        if (
            not isinstance(duplicate_of, str)
            or not _CANDIDATE_ID_RE.fullmatch(duplicate_of)
            or duplicate_of == candidate_key
        ):
            return False
    elif duplicate_of is not None:
        return False
    expected_id = _event_id({key: value for key, value in event.items() if key != "event_id"})
    return bool(event["event_id"] == expected_id)


def _validate_state(state: Any) -> tuple[bool, str | None]:
    if not isinstance(state, dict):
        return False, "candidate review ledger top level must be an object"
    if type(state.get("schema_version")) is not int or state["schema_version"] != SCHEMA_VERSION:
        return False, "candidate review ledger schema version is unsupported"
    if not isinstance(state.get("updated_at"), str):
        return False, "candidate review ledger updated_at must be a string"
    if state["updated_at"] and not _valid_timestamp(state["updated_at"]):
        return False, "candidate review ledger updated_at must be timezone-aware ISO 8601"
    reviews = state.get("reviews")
    if not isinstance(reviews, dict):
        return False, "candidate review ledger reviews must be an object"
    for candidate_key, entry in reviews.items():
        if not isinstance(candidate_key, str) or not _CANDIDATE_ID_RE.fullmatch(candidate_key):
            return False, "candidate review ledger contains an invalid candidate ID"
        if not isinstance(entry, dict) or set(entry) != {"identity", "history", "current"}:
            return False, "candidate review ledger entry has an invalid shape"
        identity = entry.get("identity")
        if (
            not isinstance(identity, dict)
            or set(identity) != {"schema_version", "method_version", "kind", "evidence"}
            or type(identity.get("schema_version")) is not int
            or identity.get("schema_version") != SCHEMA_VERSION
            or not isinstance(identity.get("method_version"), str)
            or not identity["method_version"].strip()
            or not isinstance(identity.get("kind"), str)
            or not identity["kind"].strip()
            or not isinstance(identity.get("evidence"), dict)
        ):
            return False, "candidate review ledger identity does not match its ID"
        try:
            if candidate_id_from_payload(identity) != candidate_key:
                return False, "candidate review ledger identity does not match its ID"
        except (TypeError, ValueError):
            return False, "candidate review ledger identity is not canonical JSON"
        history = entry.get("history")
        if not isinstance(history, list) or not history:
            return False, "candidate review ledger history must be a non-empty list"
        event_ids: set[str] = set()
        for event in history:
            if not _validate_event(event, candidate_key):
                return False, "candidate review ledger contains an invalid event"
            if event["event_id"] in event_ids:
                return False, "candidate review ledger contains a duplicate event"
            event_ids.add(event["event_id"])
        if entry.get("current") != history[-1]:
            return False, "candidate review ledger current event is not the latest history"
    if reviews and not state["updated_at"]:
        return False, "candidate review ledger with events must have updated_at"
    return True, None


def load_state(path: str | Path = STATE_PATH) -> tuple[dict[str, Any], list[str], bool]:
    """Load review state without permitting malformed/newer files to be overwritten."""
    state_path = Path(path)
    if not state_path.is_file():
        return empty_state(), [], True
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return empty_state(), [f"候选审阅台账读取失败，保留原文件且本轮不写回：{exc}"], False
    valid, reason = _validate_state(state)
    if not valid:
        return empty_state(), [f"{reason}；保留原文件且本轮不写回"], False
    return state, [], True


def _event_id(event: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(event).encode("utf-8")).hexdigest()


def record_review(
    state: dict[str, Any],
    identity: dict[str, Any],
    *,
    candidate: str,
    disposition: str,
    reviewer: str,
    reviewed_at: str,
    rationale: str,
    evidence_refs: list[dict[str, Any]],
    duplicate_of: str | None = None,
) -> tuple[dict[str, Any], bool]:
    """Append a human disposition; replaying the same decision is idempotent."""
    if candidate_id_from_payload(identity) != candidate:
        raise ValueError("candidate identity does not match candidate ID")
    event = {
        "candidate_id": candidate,
        "disposition": disposition,
        "reviewer": reviewer.strip() if isinstance(reviewer, str) else reviewer,
        "reviewed_at": reviewed_at,
        "rationale": rationale.strip() if isinstance(rationale, str) else rationale,
        "evidence_refs": evidence_refs,
        "duplicate_of": duplicate_of,
    }
    if not isinstance(disposition, str) or disposition not in DISPOSITIONS:
        raise ValueError(f"unsupported disposition: {disposition}")
    if not isinstance(event["reviewer"], str) or not event["reviewer"]:
        raise ValueError("reviewer must be a non-empty string")
    if not _valid_timestamp(reviewed_at):
        raise ValueError("reviewed_at must be an ISO 8601 timestamp with timezone")
    if not isinstance(event["rationale"], str) or not event["rationale"]:
        raise ValueError("rationale must be non-empty")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        raise ValueError("evidence_refs must be a non-empty list")
    if disposition == "duplicate_grouped":
        if (
            not isinstance(duplicate_of, str)
            or not _CANDIDATE_ID_RE.fullmatch(duplicate_of)
            or duplicate_of == candidate
        ):
            raise ValueError("duplicate_grouped requires a distinct duplicate_of candidate ID")
    elif duplicate_of is not None:
        raise ValueError("duplicate_of is only allowed for duplicate_grouped")
    event["event_id"] = _event_id(event)
    if not _validate_event(event, candidate):
        raise ValueError("review event failed schema validation")

    updated = copy.deepcopy(state)
    reviews = updated.setdefault("reviews", {})
    entry = reviews.get(candidate)
    if entry is None:
        entry = {"identity": copy.deepcopy(identity), "history": [], "current": None}
        reviews[candidate] = entry
    elif entry.get("identity") != identity:
        raise ValueError("candidate ID is already bound to different evidence")
    if any(item.get("event_id") == event["event_id"] for item in entry["history"]):
        return updated, False
    entry["history"].append(event)
    entry["current"] = event
    updated["schema_version"] = SCHEMA_VERSION
    updated["updated_at"] = reviewed_at
    return updated, True


def review_for_candidate(state: dict[str, Any], identifier: str) -> dict[str, Any] | None:
    entry = state.get("reviews", {}).get(identifier)
    if not isinstance(entry, dict):
        return None
    current = entry.get("current")
    return current if isinstance(current, dict) else None


def _annotate_row(row: Any, kind: str, state: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError(f"candidate row for {kind} must be an object")
    identity = candidate_identity_payload(row, kind)
    identifier = candidate_id_from_payload(identity)
    existing_id = row.get("candidate_id")
    if existing_id is not None and existing_id != identifier:
        raise ValueError(f"candidate identity mismatch: {existing_id}")
    review = review_for_candidate(state, identifier)
    row["candidate_id"] = identifier
    row["review_disposition"] = review["disposition"] if review else UNREVIEWED
    return {"candidate_id": identifier, "identity": identity, "review": review}


def annotate_report(
    report: dict[str, Any], state: dict[str, Any], *, available: bool = True, writable: bool = True
) -> dict[str, Any]:
    """Attach stable identities and current review state to report candidates."""
    by_id: dict[str, dict[str, Any]] = {}
    kind_counts: dict[str, int] = {}
    annotations: list[tuple[str, Any]] = []

    # The inventory is the canonical complete list; ranked summaries and frontiers
    # receive the same IDs for navigation but do not inflate review coverage.
    for section, kind in (
        ("method_candidate_inventory", "method_pair"),
        ("actionable_L1", "l1_candidate"),
        ("L1-C", "l1_contract_candidate"),
        ("L4", "l4_candidate"),
        ("formula_candidates", "formula_candidate"),
    ):
        rows = report.get(section)
        if isinstance(rows, list):
            for row in rows:
                annotations.append((kind, row))
    if "actionable_L1" not in report and isinstance(report.get("L1"), list):
        annotations.extend(
            ("l1_candidate", row)
            for row in report["L1"]
            if isinstance(row, dict) and not row.get("in_registry")
        )

    for kind, row in annotations:
        annotated = _annotate_row(row, kind, state)
        identifier = annotated["candidate_id"]
        previous = by_id.get(identifier)
        if previous is not None and previous["identity"] != annotated["identity"]:
            raise ValueError(f"candidate ID collision with conflicting evidence: {identifier}")
        by_id[identifier] = annotated
        kind_counts[kind] = kind_counts.get(kind, 0) + 1

    # Tag compact/alternate presentations with the same identity as their source row.
    for section, kind in (
        ("method_candidates", "method_pair"),
        ("method_candidate_frontier", "method_pair"),
        ("L1", "l1_candidate"),
        ("mapped_pair_revalidations", "l1_candidate"),
    ):
        rows = report.get(section)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"candidate row for {section} must be an object")
            # Registry revalidations are evidence rows, not new review candidates.
            row_kind = kind
            if section == "L1" and row.get("anchor_basis") == "official_contract":
                row_kind = "l1_contract_candidate"
            _annotate_row(row, row_kind, state)

    dispositions = {status: 0 for status in ALL_DISPOSITIONS}
    reviewed_candidates: list[dict[str, Any]] = []
    duplicate_groups: dict[str, list[str]] = {}
    invalid_id_count = 0
    for identifier, item in sorted(by_id.items()):
        if not _CANDIDATE_ID_RE.fullmatch(identifier):
            invalid_id_count += 1
            continue
        review = item["review"]
        disposition = review["disposition"] if review else UNREVIEWED
        dispositions[disposition] += 1
        if review:
            duplicate_of = review["duplicate_of"]
            if isinstance(duplicate_of, str):
                duplicate_groups.setdefault(duplicate_of, []).append(identifier)
            reviewed_candidates.append(
                {
                    "candidate_id": identifier,
                    "disposition": disposition,
                    "reviewer": review["reviewer"],
                    "reviewed_at": review["reviewed_at"],
                    "rationale": review["rationale"],
                    "evidence_refs": review["evidence_refs"],
                    "duplicate_of": review["duplicate_of"],
                    "event_id": review["event_id"],
                }
            )
    generated_count = len(annotations)
    unique_count = len(by_id)
    duplicate_id_count = generated_count - unique_count
    reviewed_count = unique_count - dispositions[UNREVIEWED]
    pending_count = dispositions[UNREVIEWED]
    if invalid_id_count or duplicate_id_count:
        human_status = "incomplete"
    elif not available:
        human_status = "unavailable"
    elif unique_count == 0:
        human_status = "no_candidates"
    elif pending_count == 0:
        human_status = "complete"
    else:
        human_status = "pending"
    summary = {
        "schema_version": SCHEMA_VERSION,
        "method_version": METHOD_VERSION,
        "ledger_path": STATE_PATH.name,
        "ledger_available": available,
        "ledger_writable": writable,
        "candidate_generation": {
            "generated_record_count": generated_count,
            "unique_candidate_count": unique_count,
            "duplicate_identity_count": duplicate_id_count,
            "invalid_identity_count": invalid_id_count,
            "by_kind": dict(sorted(kind_counts.items())),
        },
        "human_review": {
            "status": human_status,
            "reviewed_count": reviewed_count,
            "pending_count": pending_count,
            "coverage": (reviewed_count / unique_count) if unique_count else None,
            "disposition_counts": dispositions,
            "reviewed_candidates": reviewed_candidates,
            "duplicate_groups": [
                {
                    "representative_id": representative,
                    "member_candidate_ids": sorted(members),
                }
                for representative, members in sorted(duplicate_groups.items())
            ],
            "ledger_record_count": len(state.get("reviews", {})),
        },
    }
    report["candidate_review"] = summary
    return summary


def append_review_summary_report(markdown: str, summary: dict[str, Any]) -> str:
    generation = summary.get("candidate_generation", {})
    review = summary.get("human_review", {})
    dispositions = review.get("disposition_counts", {})
    coverage = review.get("coverage")
    coverage_text = "N/A" if coverage is None else f"{coverage:.1%}"
    lines = ["\n## 候选身份与人工审阅状态\n"]
    lines.append(
        f"- 候选身份：生成 {generation.get('generated_record_count', 0)} 条，"
        f"唯一候选 {generation.get('unique_candidate_count', 0)} 个，"
        f"重复身份 {generation.get('duplicate_identity_count', 0)}，"
        f"无效身份 {generation.get('invalid_identity_count', 0)}。"
    )
    lines.append(
        f"- 审阅台账：{'可用' if summary.get('ledger_available') else '不可用'}；"
        f"当前状态 `{review.get('status', 'unavailable')}`；"
        f"已审 {review.get('reviewed_count', 0)}，待处理 {review.get('pending_count', 0)}，"
        f"覆盖率 {coverage_text}。"
    )
    lines.append(
        f"- 重复归并组：{len(review.get('duplicate_groups', []))}；"
        "每个成员均保留到代表候选的反向追溯。"
    )
    lines.append(
        "- 处置计数："
        + "；".join(f"`{name}` {dispositions.get(name, 0)}" for name in ALL_DISPOSITIONS)
        + "。"
    )
    lines.append(
        "- `accepted_for_adjudication` 只表示可进入现有证据裁决流程；审阅台账不会修改主字典或字段注册表。"
    )
    if not summary.get("ledger_available"):
        lines.append("- 台账不可用时所有本轮候选按 `unreviewed` 展示，且不会覆盖原台账。")
    return markdown + "\n".join(lines) + "\n"


def validate_report_summary(report: dict[str, Any]) -> dict[str, Any]:
    """Recompute candidate identities and disposition totals from report rows."""
    summary = report.get("candidate_review")
    if not isinstance(summary, dict):
        return {"status": "incomplete", "issues": ["candidate_review: missing_or_invalid"]}
    generation = summary.get("candidate_generation")
    review = summary.get("human_review")
    if not isinstance(generation, dict) or not isinstance(review, dict):
        return {"status": "incomplete", "issues": ["candidate_review: summary_shape_invalid"]}

    scopes = _candidate_scopes(report)
    identities: dict[str, dict[str, Any]] = {}
    status_by_id: dict[str, str] = {}
    by_kind: dict[str, int] = {}
    invalid_identity_count = 0
    duplicate_identity_count = 0
    issues: list[str] = []
    for kind, row in scopes:
        if not isinstance(row, dict):
            invalid_identity_count += 1
            continue
        try:
            identity = candidate_identity_payload(row, kind)
            identifier = candidate_id_from_payload(identity)
        except (TypeError, ValueError):
            invalid_identity_count += 1
            continue
        by_kind[kind] = by_kind.get(kind, 0) + 1
        if row.get("candidate_id") != identifier:
            invalid_identity_count += 1
            continue
        disposition = row.get("review_disposition")
        if disposition not in ALL_DISPOSITIONS:
            invalid_identity_count += 1
            continue
        previous = identities.get(identifier)
        if previous is not None:
            if previous != identity:
                invalid_identity_count += 1
            else:
                duplicate_identity_count += 1
            if status_by_id.get(identifier) != disposition:
                invalid_identity_count += 1
        else:
            identities[identifier] = identity
            status_by_id[identifier] = disposition

    dispositions = {status: 0 for status in ALL_DISPOSITIONS}
    for disposition in status_by_id.values():
        dispositions[disposition] += 1
    reviewed = [identifier for identifier, value in status_by_id.items() if value != UNREVIEWED]
    reviewed_rows = review.get("reviewed_candidates")
    if not isinstance(reviewed_rows, list):
        reviewed_rows = []
        issues.append("candidate_review.reviewed_candidates: missing_or_invalid")
    reviewed_details: dict[str, dict[str, Any]] = {}
    for row in reviewed_rows:
        if not isinstance(row, dict):
            issues.append("candidate_review.reviewed_candidates: invalid_row")
            continue
        reviewed_identifier = row.get("candidate_id")
        disposition = row.get("disposition")
        if (
            not isinstance(reviewed_identifier, str)
            or reviewed_identifier not in status_by_id
            or not isinstance(disposition, str)
            or disposition not in DISPOSITIONS
            or status_by_id.get(reviewed_identifier) != disposition
            or reviewed_identifier in reviewed_details
        ):
            issues.append("candidate_review.reviewed_candidates: identity_or_status_mismatch")
            continue
        event = {
            "event_id": row.get("event_id"),
            "candidate_id": reviewed_identifier,
            "disposition": disposition,
            "reviewer": row.get("reviewer"),
            "reviewed_at": row.get("reviewed_at"),
            "rationale": row.get("rationale"),
            "evidence_refs": row.get("evidence_refs"),
            "duplicate_of": row.get("duplicate_of"),
        }
        if not _validate_event(event, reviewed_identifier):
            issues.append("candidate_review.reviewed_candidates: invalid_review_event")
            continue
        reviewed_details[reviewed_identifier] = row

    expected_duplicate_groups: dict[str, list[str]] = {}
    for identifier, row in reviewed_details.items():
        if row.get("disposition") == "duplicate_grouped":
            representative = row.get("duplicate_of")
            if not isinstance(representative, str):
                issues.append("candidate_review.duplicate_groups: missing_representative")
                continue
            expected_duplicate_groups.setdefault(representative, []).append(identifier)
    expected_duplicate_group_rows = [
        {
            "representative_id": representative,
            "member_candidate_ids": sorted(members),
        }
        for representative, members in sorted(expected_duplicate_groups.items())
    ]
    if review.get("duplicate_groups") != expected_duplicate_group_rows:
        issues.append("candidate_review.duplicate_groups: member_traceability_mismatch")

    expected_counts = {
        "generated_record_count": len(scopes),
        "unique_candidate_count": len(identities),
        "duplicate_identity_count": duplicate_identity_count,
        "invalid_identity_count": invalid_identity_count,
        "by_kind": dict(sorted(by_kind.items())),
    }
    for key, expected in expected_counts.items():
        if generation.get(key) != expected:
            issues.append(f"candidate_review.candidate_generation.{key}: mismatch")

    expected_review_counts = {
        "reviewed_count": len(reviewed),
        "pending_count": dispositions[UNREVIEWED],
        "disposition_counts": dispositions,
    }
    for key, expected in expected_review_counts.items():
        if review.get(key) != expected:
            issues.append(f"candidate_review.human_review.{key}: mismatch")
    if set(reviewed_details) != set(reviewed):
        issues.append("candidate_review.reviewed_candidates: coverage_mismatch")
    expected_coverage = (len(reviewed) / len(identities)) if identities else None
    if review.get("coverage") != expected_coverage:
        issues.append("candidate_review.human_review.coverage: mismatch")
    if invalid_identity_count or duplicate_identity_count:
        expected_status = "incomplete"
    elif summary.get("ledger_available") is not True:
        expected_status = "unavailable"
    elif not identities:
        expected_status = "no_candidates"
    elif dispositions[UNREVIEWED] == 0:
        expected_status = "complete"
    else:
        expected_status = "pending"
    if review.get("status") != expected_status:
        issues.append("candidate_review.human_review.status: mismatch")
    if type(review.get("ledger_record_count")) is not int or review["ledger_record_count"] < len(
        reviewed
    ):
        issues.append("candidate_review.human_review.ledger_record_count: invalid")
    if (
        type(summary.get("ledger_available")) is not bool
        or type(summary.get("ledger_writable")) is not bool
    ):
        issues.append("candidate_review: ledger_availability_invalid")
    if invalid_identity_count or duplicate_identity_count:
        issues.append("candidate_review: candidate_identity_integrity_failure")
    return {
        "status": "complete" if not issues else "incomplete",
        "candidate_record_count": len(scopes),
        "unique_candidate_count": len(identities),
        "invalid_identity_count": invalid_identity_count,
        "duplicate_identity_count": duplicate_identity_count,
        "reviewed_count": len(reviewed),
        "pending_count": dispositions[UNREVIEWED],
        "disposition_counts": dispositions,
        "issues": issues,
    }


def _decision_event_payload(
    decision: dict[str, Any], evidence_refs: list[dict[str, Any]]
) -> dict[str, Any]:
    required = {
        "schema_version",
        "candidate_id",
        "disposition",
        "reviewer",
        "reviewed_at",
        "rationale",
        "evidence_refs",
    }
    optional = {"duplicate_of"}
    if not isinstance(decision, dict) or not required.issubset(decision):
        raise ValueError(f"decision document must include {', '.join(sorted(required))}")
    if set(decision) - required - optional:
        raise ValueError("decision document contains unsupported keys")
    if type(decision.get("schema_version")) is not int or decision["schema_version"] != 1:
        raise ValueError("unsupported candidate review decision schema_version")
    identifier = decision.get("candidate_id")
    if not isinstance(identifier, str) or not _CANDIDATE_ID_RE.fullmatch(identifier):
        raise ValueError("candidate_id has an invalid format")
    disposition = decision.get("disposition")
    if not isinstance(disposition, str) or disposition not in DISPOSITIONS:
        raise ValueError(f"unsupported disposition: {disposition}")
    reviewer = decision.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("reviewer must be a non-empty string")
    reviewed_at = decision.get("reviewed_at")
    if not _valid_timestamp(reviewed_at):
        raise ValueError("reviewed_at must be an ISO 8601 timestamp with timezone")
    rationale = decision.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError("rationale must be a non-empty string")
    raw_refs = decision.get("evidence_refs")
    if (
        not isinstance(raw_refs, list)
        or not raw_refs
        or any(not isinstance(item, str) or not item.strip() for item in raw_refs)
    ):
        raise ValueError("evidence_refs must be a non-empty list of paths or HTTPS URLs")
    duplicate_of = decision.get("duplicate_of")
    if disposition == "duplicate_grouped":
        if (
            not isinstance(duplicate_of, str)
            or not _CANDIDATE_ID_RE.fullmatch(duplicate_of)
            or duplicate_of == identifier
        ):
            raise ValueError("duplicate_grouped requires a distinct duplicate_of ID")
    elif duplicate_of is not None:
        raise ValueError("duplicate_of is only allowed for duplicate_grouped")
    return {
        "candidate_id": identifier,
        "disposition": disposition,
        "reviewer": reviewer.strip(),
        "reviewed_at": reviewed_at,
        "rationale": rationale.strip(),
        "raw_evidence_refs": raw_refs,
        "duplicate_of": duplicate_of,
        "resolved_evidence_refs": evidence_refs,
    }


def _resolve_evidence_refs(
    decision: dict[str, Any], *, verification_dir: Path = VERIFY_DIR
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    from urllib.parse import urlsplit

    raw_refs = decision.get("evidence_refs")
    if not isinstance(raw_refs, list) or not raw_refs:
        raise ValueError("evidence_refs must be a non-empty list")
    resolved: list[dict[str, Any]] = []
    matching_reports: dict[str, dict[str, Any]] = {}
    report_found = False
    root = verification_dir.resolve()
    for raw_ref in raw_refs:
        if not isinstance(raw_ref, str) or not raw_ref.strip():
            raise ValueError("evidence_refs entries must be non-empty strings")
        value = raw_ref.strip()
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme != "https" or not parsed.hostname or parsed.username is not None:
                raise ValueError("external evidence references must be HTTPS URLs with a hostname")
            resolved.append({"path": value, "sha256": None})
            continue
        candidate_path = (root / value).resolve()
        try:
            relative = candidate_path.relative_to(root)
        except ValueError as exc:
            raise ValueError(
                "local evidence references must remain inside field_verification"
            ) from exc
        if not candidate_path.is_file():
            raise ValueError(f"evidence file does not exist: {relative.as_posix()}")
        content = candidate_path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        resolved.append({"path": relative.as_posix(), "sha256": digest})
        if candidate_path.suffix.lower() == ".json":
            try:
                report = json.loads(content.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise ValueError(f"evidence JSON is invalid: {relative.as_posix()}") from exc
            if not isinstance(report, dict):
                raise ValueError(f"evidence JSON root must be an object: {relative.as_posix()}")
            report_candidates = candidate_ids_in_report(report)
            identifier = decision.get("candidate_id")
            if identifier in report_candidates:
                report_found = True
                matching_reports[relative.as_posix()] = report
    if not report_found:
        raise ValueError("evidence_refs must include a collision report containing candidate_id")
    return resolved, matching_reports


def prepare_review_decision(
    decision: dict[str, Any], *, verification_dir: Path = VERIFY_DIR
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate a decision and bind it to its cited report bytes and candidate payload."""
    refs, reports = _resolve_evidence_refs(decision, verification_dir=verification_dir)
    prepared = _decision_event_payload(decision, refs)
    identifier = prepared["candidate_id"]
    candidate_identity: dict[str, Any] | None = None
    for report in reports.values():
        identities = candidate_ids_in_report(report)
        identity = identities.get(identifier)
        if identity is not None:
            if candidate_identity is not None and candidate_identity != identity:
                raise ValueError("evidence reports bind candidate ID to conflicting identities")
            candidate_identity = identity
    if candidate_identity is None:
        raise ValueError("candidate_id is absent from its cited collision report")
    duplicate_of = prepared.get("duplicate_of")
    if duplicate_of is not None:
        if not any(duplicate_of in candidate_ids_in_report(report) for report in reports.values()):
            raise ValueError("duplicate_of must be present in a cited collision report")
    return prepared, candidate_identity


def apply_prepared_review(
    state: dict[str, Any], prepared: dict[str, Any], identity: dict[str, Any]
) -> tuple[dict[str, Any], bool]:
    return record_review(
        state,
        identity,
        candidate=prepared["candidate_id"],
        disposition=prepared["disposition"],
        reviewer=prepared["reviewer"],
        reviewed_at=prepared["reviewed_at"],
        rationale=prepared["rationale"],
        evidence_refs=prepared["resolved_evidence_refs"],
        duplicate_of=prepared.get("duplicate_of"),
    )


def save_state(state: dict[str, Any], path: str | Path = STATE_PATH) -> None:
    valid, reason = _validate_state(state)
    if not valid:
        raise ValueError(f"refusing to save invalid candidate review ledger: {reason}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix="collision_candidate_reviews_", suffix=".tmp", dir=TEMP_DIR
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

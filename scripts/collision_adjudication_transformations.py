"""Deterministic in-memory registry and evidence transformations.

This module never reads or writes official files. The CLI remains the only
owner of registry/lineage output and its atomic rollback protocol.
"""

from __future__ import annotations

import copy
import datetime as dt
from collections import Counter
from typing import Any

import field_registry_api as fra
from scripts.collision_adjudication_validation import _metadata

SAME_MEANING_RELATION = "same_number_same_meaning"


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
    evidence_record = {
        "section": adjudication["report"],
        "canonical": field.get("canonical", ""),
        "meaning": field.get("meaning", ""),
        "unit": field.get("unit", ""),
        "status_raw": f"人工复核 {adjudication['reviewed_on']}：{adjudication['id']}",
        "status": adjudication["status"],
        "adjudication_id": adjudication["id"],
    }
    if "metadata_change" in adjudication:
        evidence_record["metadata_change"] = copy.deepcopy(adjudication["metadata_change"])
    if "external_evidence" in adjudication:
        evidence_record["external_evidence"] = copy.deepcopy(adjudication["external_evidence"])
    reference_evidence.append(evidence_record)
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
    projected = {
        record["code"]: record
        for record in fra.build_aggregate_fields(source_fields)
        if record["code"] in affected_codes
    }

    for code in affected_codes:
        aggregates = [record for record in fields if record.get("code") == code]
        if len(aggregates) != 1:
            raise ValueError(
                f"expected one compatibility aggregate for code {code!r}; found {len(aggregates)}"
            )
        aggregate = projected.get(code)
        if aggregate is None:
            raise ValueError(f"no source_fields remain for aggregate code {code!r}")
        aggregates[0].clear()
        aggregates[0].update(aggregate)

    meta = registry.setdefault("meta", {})
    if not isinstance(meta, dict):
        raise TypeError("registry.meta must be an object")
    meta["updated"] = dt.date.today().isoformat()
    counts: Counter[str] = Counter()
    for record in source_fields:
        counts[record.get("status", "unverified")] += 1
        counts[record.get("status_resolution", "unresolved")] += 1
    meta["source_field_stats"] = dict(sorted(counts.items()))


def _append_derived_relation_decision(payload: dict[str, Any]) -> bool:
    target_record = payload["record"]
    adjudication = payload["adjudication"]
    decision_id = payload["id"]
    after_metadata = payload["after_metadata"]
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
            or target_record.get("status_resolution") != "verified_by_derived_relation"
        ):
            raise ValueError(f"decision id already exists with different content: {decision_id}")
        return False

    if target_record.get("status", "unverified") != payload["previous_status"]:
        raise ValueError(f"target status changed since review: {payload['target']}")
    if (target_record.get("status_resolution") or "status_missing") != payload[
        "previous_status_resolution"
    ]:
        raise ValueError(f"target status resolution changed since review: {payload['target']}")
    if _metadata(target_record) != payload["previous_metadata"]:
        raise ValueError(f"target metadata changed since review: {payload['target']}")

    target_record.update(after_metadata)
    target_record["status"] = "verified"
    target_record["status_resolution"] = "verified_by_derived_relation"
    target_record.setdefault("adjudications", []).append(copy.deepcopy(adjudication))
    reference_evidence = target_record.setdefault("reference_evidence", [])
    if not isinstance(reference_evidence, list):
        raise TypeError("source field reference_evidence must be a list")
    reference_evidence.append(
        {
            "section": payload["section"],
            **after_metadata,
            "status_raw": f"人工复核公式关系 {adjudication['reviewed_on']}：{decision_id}",
            "status": "verified",
            "adjudication_id": decision_id,
            "evidence_basis": "derived_relation",
            "formula_evidence": copy.deepcopy(adjudication["formula_evidence"]),
            "metadata_change": copy.deepcopy(adjudication["metadata_change"]),
        }
    )
    sections = target_record.setdefault("sections", [])
    if not isinstance(sections, list):
        raise TypeError("source field sections must be a list")
    if payload["section"] not in sections:
        sections.append(payload["section"])
        sections.sort()
    if not target_record.get("section"):
        target_record["section"] = payload["section"]

    status_evidence = target_record.setdefault("status_evidence", {})
    if not isinstance(status_evidence, dict):
        raise TypeError("source field status_evidence must be an object")
    for key in ("adjudication_ids", "derived_relation_adjudication_ids"):
        ids = status_evidence.setdefault(key, [])
        if not isinstance(ids, list):
            raise TypeError(f"source field status_evidence.{key} must be a list")
        if decision_id not in ids:
            ids.append(decision_id)
    return True

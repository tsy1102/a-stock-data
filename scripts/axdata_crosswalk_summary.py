"""Build and validate the compact runtime summary of the AxData crosswalk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

SUMMARY_SCHEMA_VERSION = 1


def summarize_crosswalk(crosswalk: Mapping[str, Any], source_sha256: str) -> dict[str, Any]:
    """Return deterministic queue counts while validating every interface/field row."""
    interfaces = crosswalk.get("interfaces")
    if not isinstance(interfaces, list):
        raise ValueError("AxData crosswalk must contain an interfaces list")

    statuses: dict[str, int] = {}
    field_count = 0
    pending_count = 0
    for index, interface in enumerate(interfaces):
        if not isinstance(interface, dict):
            raise ValueError(f"interface row {index} must be an object")
        relation = interface.get("static_reconciliation", {})
        if relation is None:
            relation = {}
        if not isinstance(relation, dict):
            raise ValueError(f"interface row {index} static_reconciliation must be an object")
        status = relation.get("relation_status", "unknown")
        if not isinstance(status, str):
            raise ValueError(f"interface row {index} relation_status must be a string")
        statuses[status] = statuses.get(status, 0) + 1

        fields = interface.get("fields")
        if not isinstance(fields, list):
            raise ValueError(f"interface row {index} must contain a fields list")
        field_count += len(fields)
        for field_index, field in enumerate(fields):
            if not isinstance(field, dict):
                raise ValueError(f"interface row {index} field row {field_index} must be an object")
            field_relation = field.get("static_reconciliation", {})
            if field_relation is None:
                field_relation = {}
            if not isinstance(field_relation, dict):
                raise ValueError(
                    f"interface row {index} field row {field_index} static_reconciliation must be an object"
                )
            if field_relation.get("evidence_level") != "E3":
                pending_count += 1

    generated_date = crosswalk.get("generated_date")
    if not isinstance(generated_date, str):
        raise ValueError("AxData crosswalk must contain a generated_date string")
    if len(source_sha256) != 64 or any(
        char not in "0123456789abcdef" for char in source_sha256.lower()
    ):
        raise ValueError("source_sha256 must be a 64-character SHA-256 hex digest")

    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "generated_date": generated_date,
        "source_file": "axdata_interface_crosswalk.json",
        "source_sha256": source_sha256,
        "interface_count": len(interfaces),
        "field_occurrence_count": field_count,
        "field_occurrences_below_e3": pending_count,
        "interface_relation_status_counts": dict(sorted(statuses.items())),
    }


def read_summary(path: Path) -> dict[str, Any] | None:
    """Load a structurally valid compact summary; return None for unreadable/stale schema."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict) or value.get("schema_version") != SUMMARY_SCHEMA_VERSION:
        return None
    required_ints = (
        "interface_count",
        "field_occurrence_count",
        "field_occurrences_below_e3",
    )
    if any(type(value.get(key)) is not int or value[key] < 0 for key in required_ints):
        return None
    statuses = value.get("interface_relation_status_counts")
    if not isinstance(statuses, dict) or any(
        not isinstance(key, str) or type(count) is not int or count < 0
        for key, count in statuses.items()
    ):
        return None
    source_sha256 = value.get("source_sha256")
    if (
        not isinstance(source_sha256, str)
        or len(source_sha256) != 64
        or any(char not in "0123456789abcdef" for char in source_sha256.lower())
    ):
        return None
    if not isinstance(value.get("generated_date"), str):
        return None
    if value.get("source_file") != "axdata_interface_crosswalk.json":
        return None
    if sum(statuses.values()) != value["interface_count"]:
        return None
    if value["field_occurrences_below_e3"] > value["field_occurrence_count"]:
        return None
    return value

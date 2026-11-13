"""Interface-level capture evidence for composite field collectors.

The evidence contains hashes and path/date summaries, never a second copy of raw
values. Source-specific raw snapshots remain the authoritative payloads.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import datetime
import hashlib
import json
import re
from typing import Any

from scripts.capture_catalog import CAPTURE_UNIT_CATALOG

MAX_RECORDED_PATHS = 2000
MAX_DATE_VALUES_PER_PATH = 20
DATE_PATH_HINTS = re.compile(r"date|time|period|report|披露|日期", re.IGNORECASE)
SECURITY_KEY = re.compile(r"\d{6}")


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _diagnostic_fingerprints(values: list[str]) -> list[dict[str, Any]]:
    return [{"fingerprint": _digest(value), "length": len(value)} for value in values[:5]]


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone().isoformat(timespec="seconds")


def _scan_payload(value: Any) -> dict[str, Any]:
    path_values: dict[str, list[Any]] = defaultdict(list)
    errors: list[str] = []
    skipped: list[str] = []
    date_values: dict[str, set[str]] = defaultdict(set)
    record_count = 0
    nonempty_value_count = 0

    def walk(item: Any, path: tuple[str, ...] = ()) -> None:
        nonlocal record_count, nonempty_value_count
        if isinstance(item, dict):
            if not item and path:
                path_values[".".join(path)].append({})
            for key in sorted(item, key=str):
                child = item[key]
                key_text = str(key)
                if key_text == "__error__":
                    errors.append(str(child)[:240])
                    continue
                if key_text == "__skipped__":
                    skipped.append(str(child)[:240])
                    continue
                if key_text.startswith("__"):
                    continue
                path_key = "*" if SECURITY_KEY.fullmatch(key_text) else key_text
                walk(child, (*path, path_key))
            return
        if isinstance(item, list):
            record_count += len(item)
            if not item and path:
                path_values[".".join((*path, "[]"))].append([])
            for child in item:
                walk(child, (*path, "[]"))
            return
        if not path:
            return
        field_path = ".".join(path)
        path_values[field_path].append(item)
        if item is not None and item != "":
            nonempty_value_count += 1
        if DATE_PATH_HINTS.search(field_path) and item is not None:
            rendered = str(item).strip()
            if rendered:
                date_values[field_path].add(rendered)

    walk(value)
    normalized_paths = sorted(path_values)
    all_value_fingerprints = {path: _digest(values) for path, values in sorted(path_values.items())}
    value_fingerprints = dict(list(all_value_fingerprints.items())[:MAX_RECORDED_PATHS])
    return {
        "observed_paths": normalized_paths[:MAX_RECORDED_PATHS],
        "observed_paths_truncated": max(0, len(normalized_paths) - MAX_RECORDED_PATHS),
        "observed_path_count": len(normalized_paths),
        "observed_path_fingerprint": _digest(normalized_paths),
        "field_value_fingerprints": value_fingerprints,
        "field_value_fingerprints_truncated": max(
            0, len(all_value_fingerprints) - MAX_RECORDED_PATHS
        ),
        "payload_fingerprint": _digest(value),
        "scalar_observation_count": sum(len(values) for values in path_values.values()),
        "nonempty_value_count": nonempty_value_count,
        "record_count": record_count,
        "error_count": len(errors),
        "skip_count": len(skipped),
        "error_fingerprints": _diagnostic_fingerprints(errors),
        "skip_fingerprints": _diagnostic_fingerprints(skipped),
        "date_value_observations": {
            path: sorted(values)[:MAX_DATE_VALUES_PER_PATH]
            for path, values in sorted(date_values.items())
        },
    }


def build_capture_unit_evidence(
    unit_id: str,
    result: Any,
    *,
    collector_started_at: datetime | None,
    collector_finished_at: datetime | None,
    requested_data_date: str,
    market_phase: str,
    collector_invoked: bool = True,
    logical_call_count: int | None = None,
    skip_reason: str | None = None,
    request_parameters: dict[str, Any] | None = None,
    source_as_of_date: str | None = None,
    source_as_of_date_basis: str | None = None,
) -> dict[str, Any]:
    """Create a low-sensitivity, longitudinal record for one interface unit."""
    spec = CAPTURE_UNIT_CATALOG.get(unit_id)
    if not isinstance(spec, dict):
        raise ValueError(f"unknown capture unit: {unit_id}")
    evidence = _scan_payload(result)
    collector_duration_seconds = None
    if collector_started_at is not None and collector_finished_at is not None:
        collector_duration_seconds = round(
            max(0.0, (collector_finished_at - collector_started_at).total_seconds()), 3
        )
    if not collector_invoked:
        status = "skipped"
    elif evidence["error_count"] and evidence["nonempty_value_count"]:
        status = "partial"
    elif evidence["error_count"]:
        status = "failed"
    elif evidence["skip_count"] and not evidence["nonempty_value_count"]:
        status = "skipped"
    elif evidence["nonempty_value_count"]:
        status = "ok"
    else:
        status = "empty"
    return {
        "evidence_schema_version": 1,
        "unit_id": unit_id,
        "collector": spec["collector"],
        "interface_id": spec["interface_id"],
        "provider_hint": spec.get("provider_hint", "unconfirmed"),
        "identity_status": spec.get("identity_status", "unconfirmed"),
        "data_domain": spec.get("data_domain", "unknown"),
        "source_date_contract": spec.get(
            "source_date_contract",
            "unconfirmed; review response date observations against the source contract",
        ),
        "requested_data_date": requested_data_date,
        "source_as_of_date": source_as_of_date,
        "source_as_of_date_basis": source_as_of_date_basis,
        "market_phase": market_phase,
        "collector_started_at": _iso(collector_started_at),
        "collector_finished_at": _iso(collector_finished_at),
        "collector_duration_seconds": collector_duration_seconds,
        "collector_invoked": collector_invoked,
        "logical_call_count": max(0, logical_call_count or 0),
        "network_request_count": None,
        "network_request_count_status": "not_instrumented",
        "network_request_count_note": (
            "Adapter invocation does not prove a wire request; cache hits and internal "
            "retries are not exposed at this evidence layer."
        ),
        "request_parameters": request_parameters or {},
        "status": status,
        "status_basis": (
            "collector payload shape only; adapters may normalize transport failures as empty values"
        ),
        "skip_reason": skip_reason,
        "output_paths": [list(path) for path in spec.get("output_paths", [])],
        **evidence,
    }


def capture_units_for_collector(collector: str) -> set[str]:
    return {
        unit_id
        for unit_id, spec in CAPTURE_UNIT_CATALOG.items()
        if spec.get("collector") == collector
    }


def extract_capture_unit_payload(root: dict[str, Any], unit_id: str) -> dict[str, Any]:
    """Copy only catalogued raw paths for one unit into an evidence payload."""
    spec = CAPTURE_UNIT_CATALOG.get(unit_id)
    if not isinstance(spec, dict):
        raise ValueError(f"unknown capture unit: {unit_id}")
    payload: dict[str, Any] = {}

    def set_path(target: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
        node = target
        for part in path[:-1]:
            child = node.get(part)
            if not isinstance(child, dict):
                child = {}
                node[part] = child
            node = child
        node[path[-1]] = deepcopy(value)

    def walk(
        value: Any,
        pattern: tuple[str, ...],
        index: int = 0,
        concrete_path: tuple[str, ...] = (),
    ) -> None:
        if index == len(pattern):
            set_path(payload, concrete_path, value)
            return
        part = pattern[index]
        if part == "*":
            if isinstance(value, dict):
                for key, child in value.items():
                    walk(child, pattern, index + 1, (*concrete_path, str(key)))
            return
        if isinstance(value, dict) and part in value:
            walk(value[part], pattern, index + 1, (*concrete_path, part))

    for output_path in spec.get("output_paths", []):
        walk(root, tuple(output_path))
    return payload


def capture_unit_parents(unit_ids: set[str] | list[str]) -> set[str]:
    return {
        CAPTURE_UNIT_CATALOG[unit_id]["collector"]
        for unit_id in unit_ids
        if unit_id in CAPTURE_UNIT_CATALOG
    }


def merge_selected_unit_outputs(
    previous: dict[str, Any], current: dict[str, Any], unit_ids: set[str]
) -> dict[str, Any]:
    """Replace only selected unit paths while preserving sibling raw evidence."""
    merged = deepcopy(previous)

    def get_path(root: dict[str, Any], path: tuple[str, ...]) -> tuple[bool, Any]:
        value: Any = root
        for part in path:
            if not isinstance(value, dict) or part not in value:
                return False, None
            value = value[part]
        return True, value

    def set_path(root: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
        node = root
        for part in path[:-1]:
            child = node.get(part)
            if not isinstance(child, dict):
                child = {}
                node[part] = child
            node = child
        node[path[-1]] = deepcopy(value)

    for unit_id in unit_ids:
        spec = CAPTURE_UNIT_CATALOG.get(unit_id)
        if not isinstance(spec, dict):
            continue
        for path_parts in spec.get("output_paths", []):
            path = tuple(path_parts)
            if "*" not in path:
                exists, value = get_path(current, path)
                if exists:
                    set_path(merged, path, value)
                continue
            wildcard_index = path.index("*")
            prefix = path[:wildcard_index]
            suffix = path[wildcard_index + 1 :]
            exists, source_parent = get_path(current, prefix)
            if not exists or not isinstance(source_parent, dict):
                continue
            exists, target_parent = get_path(merged, prefix)
            if not exists or not isinstance(target_parent, dict):
                set_path(merged, prefix, {})
                _, target_parent = get_path(merged, prefix)
            for entity_key, source_entity in source_parent.items():
                if not isinstance(source_entity, dict):
                    continue
                child_path = (str(entity_key), *suffix)
                exists, value = get_path(source_parent, child_path)
                if exists:
                    set_path(target_parent, child_path, value)

    for key in ("scheme", "probe_trading_day", "date_ms"):
        if key in current:
            merged[key] = deepcopy(current[key])
    current_source_meta = current.get("__source_meta__")
    if isinstance(current_source_meta, dict):
        merged_source_meta = merged.get("__source_meta__")
        if not isinstance(merged_source_meta, dict):
            merged_source_meta = {}
        merged_source_meta.update(deepcopy(current_source_meta))
        merged["__source_meta__"] = merged_source_meta
    return merged


def validate_capture_unit_ids(unit_ids: list[str]) -> tuple[set[str], list[str]]:
    selected = {item.strip() for item in unit_ids if item.strip()}
    unknown = sorted(selected - set(CAPTURE_UNIT_CATALOG))
    return selected, unknown

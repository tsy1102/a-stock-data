#!/usr/bin/env python3
"""Build a local, read-only coverage index for unresolved registry fields."""

from __future__ import annotations

import datetime as dt
import json
import math
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from typing import Any

for stream in (sys.stdout, sys.stderr):
    if stream is not None and hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DEFAULT_DATA_DIR = os.path.join(REPO_ROOT, "docs", "field_verification")
LOCAL_STATE_DIR = os.path.join(REPO_ROOT, ".tmp", "field_evidence_coverage")
TRADING_WINDOW_DAYS = 7
ZHB_BRANCH_SOURCES = {
    "stat": "ZHB-tdxstat",
    "stat2": "ZHB-tdxstat2",
    "tipinfo": "ZHB-tipinfo",
}
COMPOSITE_TEXT = re.compile(r"[/／+＋、;；]|(?:或|兼)")

sys.path.insert(0, SCRIPT_DIR)
import collision_dates as cdates
import collide
import field_registry_api as fra
import source_lineage_api as sla


def _runtime_field_parts(fid: str) -> tuple[str, str]:
    if "." in fid:
        return tuple(fid.split(".", 1))  # type: ignore[return-value]
    if "[" in fid:
        split_at = fid.index("[")
        return fid[:split_at], fid[split_at:]
    return fid, ""


def _identity_index(
    source_fields: list[dict[str, Any]], lineage: dict[str, Any]
) -> tuple[dict[tuple[str, str], set[tuple[str, str]]], dict[tuple[str, str], dict[str, Any]]]:
    owners: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    records: dict[tuple[str, str], dict[str, Any]] = {}
    for record in source_fields:
        identity = (record["source"], record["code"])
        records[identity] = record
        for alias in sla.runtime_aliases_for_source(record["source"], lineage):
            normalized = sla.normalize_runtime_field_code(alias, record["code"])
            owners[(alias, normalized)].add(identity)
    return owners, records


def _target_route(
    identity: tuple[str, str],
    owners: dict[tuple[str, str], set[tuple[str, str]]],
    lineage: dict[str, Any],
) -> tuple[str, list[str]]:
    source, code = identity
    if source in ZHB_BRANCH_SOURCES.values():
        return "mapped_by_explicit_branch", ["zhb"]
    aliases = sla.runtime_aliases_for_source(source, lineage)
    if not aliases:
        return "unmapped_source_alias", []
    exact = []
    ambiguous = []
    for alias in aliases:
        normalized = sla.normalize_runtime_field_code(alias, code)
        matched = owners.get((alias, normalized), set())
        if matched == {identity}:
            exact.append(alias)
        elif identity in matched and len(matched) > 1:
            ambiguous.append(alias)
    if exact:
        return "mapped", sorted(set(exact))
    if ambiguous:
        return "ambiguous_runtime_identity", sorted(set(ambiguous))
    return "unmapped_runtime_path", sorted(set(aliases))


def _resolve_runtime_identity(
    fid: str,
    owners: dict[tuple[str, str], set[tuple[str, str]]],
    source_records: dict[tuple[str, str], dict[str, Any]],
    lineage: dict[str, Any],
) -> tuple[tuple[str, str] | None, str]:
    alias, code = _runtime_field_parts(fid)
    if alias == "zhb":
        prefix = "zhb."
        if not fid.startswith(prefix):
            return None, "unmapped_zhb_path"
        branch_path = fid[len(prefix) :]
        branch, separator, branch_code = branch_path.partition(".")
        if branch == "full":
            return None, "merged_zhb_full_view"
        source = ZHB_BRANCH_SOURCES.get(branch)
        identity = (source, branch_code) if source and separator else None
        if identity in source_records:
            return identity, "mapped_by_explicit_branch"
        return None, "unmapped_zhb_branch_or_code"

    if not code:
        return None, "runtime_path_has_no_field_code"
    if alias not in lineage.get("runtime_sources", {}):
        return None, "unknown_runtime_alias"
    normalized = sla.normalize_runtime_field_code(alias, code)
    matched = owners.get((alias, normalized), set())
    if len(matched) == 1:
        identity = next(iter(matched))
        return identity, "exact_runtime_identity"
    if len(matched) > 1:
        return None, "ambiguous_runtime_identity"
    return None, "unmapped_runtime_path"


def _has_value(value: Any) -> bool:
    if value is None or isinstance(value, bool):
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    return False


def _target_kind(record: dict[str, Any]) -> str | None:
    status = record.get("status", "unverified")
    if status == "disproved":
        return None
    if status in {"unverified", "candidate", "conflict"}:
        return "unresolved_status"
    if status != "verified":
        return "unresolved_status"
    if (
        not str(record.get("canonical") or "").strip()
        or not str(record.get("meaning") or "").strip()
    ):
        return "metadata_gap"
    if COMPOSITE_TEXT.search(
        " ".join(str(record.get(key) or "") for key in ("canonical", "meaning"))
    ):
        return "composite_text_review"
    return None


def build_field_coverage(
    snapshots: list[Any],
    registry: dict[str, Any],
    lineage: dict[str, Any],
    report_date: dt.date,
    *,
    trading_window_dates: list[dt.date],
    event_start: dt.date | None = None,
    event_end: dt.date | None = None,
    selection_warnings: list[str] | None = None,
) -> dict[str, Any]:
    """Summarize source-specific raw observations without retaining their values."""
    source_fields = fra.source_field_records(registry)
    owners, source_records = _identity_index(source_fields, lineage)
    targets: dict[tuple[str, str], dict[str, Any]] = {}
    for record in source_fields:
        kind = _target_kind(record)
        if kind is None:
            continue
        identity = (record["source"], record["code"])
        route_status, aliases = _target_route(identity, owners, lineage)
        source_lineage = lineage.get("sources", {}).get(record["source"], {})
        targets[identity] = {
            "source": record["source"],
            "code": record["code"],
            "registry_status": record.get("status", "unverified"),
            "target_kind": kind,
            "identity_status": route_status,
            "runtime_aliases": aliases,
            "independence_family": source_lineage.get("independence_family"),
            "independence_status": source_lineage.get("independence_status", "unconfirmed"),
            "anchor_eligible": bool(source_lineage.get("anchor_eligible", False)),
            "candidate_samples": defaultdict(set),
            "source_as_of_samples": defaultdict(set),
            "event_record_samples": defaultdict(set),
            "date_origins": set(),
            "phases": set(),
            "source_statuses": set(),
        }

    path_diagnostics: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    missing_event_dates = 0
    scheme_mismatches = 0
    snapshots_seen = 0
    for snapshot in snapshots:
        document = snapshot.document
        if not isinstance(document, dict):
            continue
        snapshots_seen += 1
        include_context = bool(snapshot.meta.get("include_context"))
        if snapshot.source in collide.CONTEXT_ONLY_SOURCES and not include_context:
            continue
        if not include_context:
            document, _ = collide._without_context_records(document, snapshot.source)
        scheme = document.get("scheme")
        meta_sources = snapshot.meta.get("sources")
        source_meta = (
            meta_sources.get(snapshot.source, {}) if isinstance(meta_sources, dict) else {}
        )
        meta_schemes = snapshot.meta.get("schemes")
        declared_scheme = source_meta.get("scheme") if isinstance(source_meta, dict) else None
        if not declared_scheme and isinstance(meta_schemes, dict):
            declared_scheme = meta_schemes.get(snapshot.source)
        scheme_ok = bool(scheme) and (not declared_scheme or scheme == declared_scheme)
        if not scheme_ok:
            scheme_mismatches += 1
            path_diagnostics[("scheme", snapshot.source, str(scheme or "missing"))].add(
                str(declared_scheme or "missing")
            )

        for container in collide._record_containers(
            document, snapshot.source, include_context=include_context
        ):
            for container_code, record in container.items():
                if not isinstance(record, dict):
                    continue
                event_source = snapshot.domain == cdates.CALENDAR
                if event_source:
                    sample_day = cdates.event_record_date(snapshot.source, record)
                    if sample_day is None:
                        missing_event_dates += 1
                        continue
                    if event_start is not None and sample_day < event_start:
                        continue
                    if event_end is not None and sample_day > event_end:
                        continue
                else:
                    sample_day = snapshot.sample_date
                if sample_day > report_date:
                    continue
                day_key = cdates.sample_date_key(snapshot.domain, sample_day)
                pairs: list[tuple[str, Any]] = []
                collide._flatten(
                    record, snapshot.source, scheme, str(container_code), day_key, pairs
                )
                for fid, value in pairs:
                    if not _has_value(value):
                        continue
                    runtime_identity, route_reason = _resolve_runtime_identity(
                        fid, owners, source_records, lineage
                    )
                    if runtime_identity is None:
                        alias, runtime_code = _runtime_field_parts(fid)
                        normalized = sla.normalize_runtime_field_code(alias, runtime_code)
                        path_diagnostics[(route_reason, alias, normalized)].add(fid)
                        continue
                    target = targets.get(runtime_identity)
                    if target is None:
                        continue
                    target["candidate_samples"][day_key].add(str(container_code))
                    target["date_origins"].add(snapshot.date_origin)
                    target["phases"].add(snapshot.phase)
                    target["source_statuses"].add(snapshot.status)
                    event_date_is_explicit = event_source
                    closed_snapshot = event_source or snapshot.phase == "closed"
                    source_date_is_explicit = snapshot.date_origin == "source_as_of"
                    status_is_usable = snapshot.status in {"ok", "partial"}
                    if scheme_ok and status_is_usable and event_date_is_explicit:
                        target["event_record_samples"][day_key].add(str(container_code))
                    elif (
                        scheme_ok
                        and status_is_usable
                        and closed_snapshot
                        and source_date_is_explicit
                    ):
                        target["source_as_of_samples"][day_key].add(str(container_code))

    field_rows = []
    for identity in sorted(targets):
        target = targets[identity]
        candidate_samples = target.pop("candidate_samples")
        source_as_of_samples = target.pop("source_as_of_samples")
        event_record_samples = target.pop("event_record_samples")
        date_origins = sorted(target.pop("date_origins"))
        phases = sorted(target.pop("phases"))
        source_statuses = sorted(target.pop("source_statuses"))
        valid_counts = {day: len(source_as_of_samples[day]) for day in sorted(source_as_of_samples)}
        candidate_counts = {day: len(candidate_samples[day]) for day in sorted(candidate_samples)}
        event_record_counts = {
            day: len(event_record_samples[day]) for day in sorted(event_record_samples)
        }
        target.update(
            {
                "source_as_of_days": sorted(source_as_of_samples),
                "event_record_days": sorted(event_record_samples),
                "candidate_days": sorted(candidate_samples),
                "source_as_of_sample_counts": valid_counts,
                "event_record_sample_counts": event_record_counts,
                "candidate_sample_counts": candidate_counts,
                "source_as_of_day_count": len(source_as_of_samples),
                "event_record_day_count": len(event_record_samples),
                "qualified_day_count": len(set(source_as_of_samples) | set(event_record_samples)),
                "candidate_day_count": len(candidate_samples),
                "latest_observed_day": max(candidate_samples) if candidate_samples else None,
                "date_origins": date_origins,
                "phases": phases,
                "source_statuses": source_statuses,
            }
        )
        field_rows.append(target)

    route_counts = Counter(reason for reason, _, _ in path_diagnostics)
    target_counts = Counter(row["identity_status"] for row in field_rows)
    summary = {
        "status": "ok",
        "report_date": report_date.isoformat(),
        "date_policy": "same as collision_dates; source_as_of or record event date required for qualified coverage",
        "trading_window_days": TRADING_WINDOW_DAYS,
        "trading_window_dates": [day.isoformat() for day in trading_window_dates],
        "event_window_start": event_start.isoformat() if event_start else None,
        "event_window_end": event_end.isoformat() if event_end else None,
        "snapshots_seen": snapshots_seen,
        "pending_source_fields": len(field_rows),
        "mapped_targets": target_counts.get("mapped", 0)
        + target_counts.get("mapped_by_explicit_branch", 0),
        "ambiguous_targets": target_counts.get("ambiguous_runtime_identity", 0),
        "unmapped_targets": sum(
            count
            for route, count in target_counts.items()
            if route not in {"mapped", "mapped_by_explicit_branch", "ambiguous_runtime_identity"}
        ),
        "targets_observed": sum(bool(row["candidate_days"]) for row in field_rows),
        "targets_with_3_source_as_of_days": sum(
            row["source_as_of_day_count"] >= 3 for row in field_rows
        ),
        "targets_with_7_source_as_of_days": sum(
            row["source_as_of_day_count"] >= TRADING_WINDOW_DAYS for row in field_rows
        ),
        "targets_with_3_event_record_days": sum(
            row["event_record_day_count"] >= 3 for row in field_rows
        ),
        "ambiguous_or_unmapped_runtime_paths": sum(
            count
            for reason, count in route_counts.items()
            if reason not in {"exact_runtime_identity", "mapped_by_explicit_branch"}
        ),
        "missing_event_date_records": missing_event_dates,
        "scheme_mismatches": scheme_mismatches,
    }
    diagnostics = list(selection_warnings or [])
    diagnostics.extend(
        f"{reason}: runtime={alias} path={path} examples={len(examples)}"
        for (reason, alias, path), examples in sorted(path_diagnostics.items())
    )
    return {
        "schema_version": 1,
        "summary": summary,
        "fields": field_rows,
        "diagnostics": diagnostics[:200],
    }


def _write_coverage(path: str, payload: dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=os.path.dirname(path),
            prefix="field_coverage_",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temp_path = stream.name
            json.dump(payload, stream, ensure_ascii=False, indent=1)
            stream.write("\n")
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def refresh_daily_coverage(
    out_dir: str,
    snapshot_meta: dict[str, Any],
    *,
    data_dir: str = DEFAULT_DATA_DIR,
) -> dict[str, Any]:
    """Recompute the seven-session coverage index from existing local snapshots."""
    report_day = cdates.parse_date(snapshot_meta.get("data_date"))
    if report_day is None:
        return {"status": "missing_data_date", "message": "meta.data_date is absent or invalid"}

    folders, discovery_warnings = cdates.discover_capture_folders(data_dir)
    folder_window = cdates.select_folder_window(
        folders,
        TRADING_WINDOW_DAYS,
        report_day,
        False,
        excluded_trading_dates=getattr(collide, "EXCLUDE_DIRS", set()),
    )
    snapshots, snapshot_warnings = cdates.select_snapshots(
        folder_window.folders,
        allowed_trading_folders=folder_window.market_folders,
        allowed_event_folders=folder_window.event_folders,
    )
    trading_window_dates = []
    for day_text in folder_window.trading_dates:
        day = cdates.parse_date(day_text)
        if day is None:
            raise ValueError(f"invalid trading-window date from collision_dates: {day_text!r}")
        trading_window_dates.append(day)
    registry = fra.load_registry()
    lineage = sla.load_source_lineage(registry=registry)
    coverage = build_field_coverage(
        snapshots,
        registry,
        lineage,
        report_day,
        trading_window_dates=trading_window_dates,
        event_start=folder_window.event_start,
        event_end=folder_window.event_end,
        selection_warnings=[
            *discovery_warnings,
            *folder_window.warnings,
            *snapshot_warnings,
        ],
    )
    capture_name = os.path.basename(os.path.normpath(out_dir))
    safe_capture_date = re.sub(r"[^0-9]", "", capture_name)
    if not re.fullmatch(r"\d{8}", safe_capture_date):
        safe_capture_date = report_day.strftime("%Y%m%d")
    os.makedirs(LOCAL_STATE_DIR, exist_ok=True)
    output_path = os.path.join(LOCAL_STATE_DIR, f"coverage_{safe_capture_date}.json")
    _write_coverage(output_path, coverage)
    return {
        **coverage["summary"],
        "file": os.path.relpath(output_path, REPO_ROOT).replace(os.sep, "/"),
    }


if __name__ == "__main__":
    raise SystemExit(
        "Run via capture_field_probe.py; this module intentionally has no network CLI."
    )

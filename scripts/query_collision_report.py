"""Validate and page through schema-5 collision report evidence without mutation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.capture_retention import MIN_CAPTURE_DATE
from scripts.collision_candidate_reviews import (
    ALL_DISPOSITIONS,
    candidate_ids_in_report,
)
from scripts.collision_reporting import build_report_completeness

SUPPORTED_SCHEMA_VERSION = 5
DEFAULT_CANDIDATE_SECTIONS = (
    "method_candidate_inventory",
    "actionable_L1",
    "L1-C",
    "L4",
    "formula_candidates",
)
MAX_PAGE_SIZE = 100
_DATE_RE = re.compile(r"\d{8}")
_CANDIDATE_ID_RE = re.compile(r"cc1_[0-9a-f]{64}")
_SOURCE_KEYS = frozenset(
    {"source", "source_id", "source_name", "sources", "evidence_sources", "provider"}
)
_FIELD_KEYS = frozenset(
    {"left", "right", "right_inputs", "field", "field_path", "target", "target_field"}
)
_DISPOSITION_KEYS = frozenset({"disposition", "review_disposition"})


class ReportQueryError(ValueError):
    """The report is not safe to query or the requested selection is invalid."""


@dataclass(frozen=True)
class VerifiedReport:
    data: dict[str, Any]
    label: str
    sha256: str
    completeness: dict[str, Any]


def _parse_report_date(value: Any) -> date:
    if not isinstance(value, str) or _DATE_RE.fullmatch(value) is None:
        raise ReportQueryError("report date must use YYYYMMDD format")
    try:
        report_day = datetime.strptime(value, "%Y%m%d").date()
        minimum_day = date.fromisoformat(str(MIN_CAPTURE_DATE))
    except ValueError as exc:
        raise ReportQueryError(f"invalid report or retention date: {exc}") from exc
    if report_day < minimum_day:
        raise ReportQueryError(
            f"report date {value} predates the retained evidence start {minimum_day:%Y%m%d}"
        )
    return report_day


def _reject_json_constant(value: str) -> None:
    raise ReportQueryError(f"non-standard JSON constant is not allowed: {value}")


def _load_verified_report(path: Path) -> VerifiedReport:
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise ReportQueryError(f"cannot read report {path}: {exc}") from exc
    try:
        report = json.loads(content.decode("utf-8"), parse_constant=_reject_json_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ReportQueryError(f"report is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(report, dict):
        raise ReportQueryError("report root must be a JSON object")
    if type(report.get("schema_version")) is not int:
        raise ReportQueryError("report schema_version must be an integer")
    if report["schema_version"] != SUPPORTED_SCHEMA_VERSION:
        raise ReportQueryError(
            f"unsupported schema_version {report['schema_version']}; "
            f"this tool requires {SUPPORTED_SCHEMA_VERSION}"
        )
    _parse_report_date(report.get("date"))
    if not isinstance(report.get("candidate_review"), dict):
        raise ReportQueryError("schema-5 candidate_review summary is missing or invalid")

    stored = report.get("report_completeness")
    if not isinstance(stored, dict) or stored.get("status") != "complete":
        raise ReportQueryError("report_completeness is missing or not complete")
    try:
        computed = build_report_completeness(report)
        candidate_ids_in_report(report)
    except (TypeError, ValueError, KeyError, AttributeError) as exc:
        raise ReportQueryError(f"report integrity checks failed: {exc}") from exc
    if computed != stored:
        raise ReportQueryError("stored report_completeness does not match recomputed evidence")
    if computed.get("status") != "complete":
        raise ReportQueryError("recomputed report completeness is not complete")

    try:
        label = path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        label = path.name
    return VerifiedReport(
        data=report,
        label=label,
        sha256=hashlib.sha256(content).hexdigest(),
        completeness=computed,
    )


def _resolve_section(report: dict[str, Any], completeness: dict[str, Any], name: str) -> list[Any]:
    section_info = completeness.get("sections", {}).get(name)
    if not isinstance(section_info, dict) or type(section_info.get("json_record_count")) is not int:
        raise ReportQueryError(f"section is not a recorded JSON list: {name}")
    value: Any = report
    for part in name.split("."):
        if not isinstance(value, dict) or part not in value:
            raise ReportQueryError(f"section path does not exist in report: {name}")
        value = value[part]
    if not isinstance(value, list):
        raise ReportQueryError(f"section is not a JSON list: {name}")
    expected_count = section_info["json_record_count"]
    if len(value) != expected_count:
        raise ReportQueryError(
            f"section count mismatch for {name}: metadata={expected_count}, actual={len(value)}"
        )
    return value


def _queryable_sections(verified: VerifiedReport) -> dict[str, dict[str, Any]]:
    result = {}
    sections = verified.completeness.get("sections", {})
    if not isinstance(sections, dict):
        raise ReportQueryError("report completeness sections are missing or invalid")
    for name, info in sections.items():
        if not isinstance(name, str) or not isinstance(info, dict):
            continue
        if type(info.get("json_record_count")) is not int:
            continue
        try:
            _resolve_section(verified.data, verified.completeness, name)
        except ReportQueryError:
            continue
        result[name] = info
    return result


def _nested_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _nested_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _nested_strings(item)


def _values_for_keys(value: Any, keys: frozenset[str]) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in keys:
                yield from _nested_strings(child)
            else:
                yield from _values_for_keys(child, keys)
    elif isinstance(value, list):
        for child in value:
            yield from _values_for_keys(child, keys)


def _source_prefix(field_path: str) -> str:
    boundaries = [index for token in (".", "[") if (index := field_path.find(token)) >= 0]
    return field_path[: min(boundaries)] if boundaries else field_path


def _matches(
    record: Any,
    *,
    candidate_id: str | None,
    source: str | None,
    field: str | None,
    disposition: str | None,
) -> bool:
    if not isinstance(record, dict):
        return not any((candidate_id, source, field, disposition))
    if candidate_id is not None and record.get("candidate_id") != candidate_id:
        return False
    if source is not None:
        sources = {value.casefold() for value in _values_for_keys(record, _SOURCE_KEYS)}
        sources.update(
            _source_prefix(value).casefold() for value in _values_for_keys(record, _FIELD_KEYS)
        )
        if source.casefold() not in sources:
            return False
    if field is not None and field not in set(_values_for_keys(record, _FIELD_KEYS)):
        return False
    if disposition is not None and disposition not in set(
        _values_for_keys(record, _DISPOSITION_KEYS)
    ):
        return False
    return True


def _review_status(report: dict[str, Any]) -> dict[str, Any]:
    summary = report.get("candidate_review", {})
    review = summary.get("human_review", {}) if isinstance(summary, dict) else {}
    return {
        "status": review.get("status"),
        "reviewed_count": review.get("reviewed_count"),
        "pending_count": review.get("pending_count"),
    }


def _report_header(verified: VerifiedReport) -> dict[str, Any]:
    return {
        "report": verified.label,
        "report_date": verified.data["date"],
        "report_schema_version": verified.data["schema_version"],
        "report_sha256": verified.sha256,
        "report_completeness": verified.completeness["status"],
        "candidate_review": _review_status(verified.data),
    }


def _section_summary(name: str, info: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "json_record_count": info["json_record_count"],
        "markdown_display_count": info.get("markdown_display_count"),
        "markdown_omitted_count": info.get("markdown_omitted_count"),
        "detail_scope": info.get("detail_scope"),
    }


def list_report_sections(report_path: Path) -> dict[str, Any]:
    verified = _load_verified_report(report_path)
    queryable = _queryable_sections(verified)
    return {
        "schema_version": 1,
        "kind": "collision_report_sections",
        **_report_header(verified),
        "sections": [_section_summary(name, info) for name, info in queryable.items()],
    }


def _selection_digest(rows: Sequence[tuple[str, int, Any]]) -> str:
    references = [
        [section, index, record.get("candidate_id") if isinstance(record, dict) else None]
        for section, index, record in rows
    ]
    payload = json.dumps(references, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _compact_page(
    rows: Sequence[tuple[str, int, Any]], all_matches: Sequence[tuple[str, int, Any]]
) -> dict[str, Any]:
    record_keys = sorted(
        {
            key
            for _section, _index, record in all_matches
            if isinstance(record, dict)
            for key in record
        }
    )
    columns = [
        {"scope": "meta", "name": "section"},
        {"scope": "meta", "name": "index"},
        {"scope": "meta", "name": "record_type"},
        *({"scope": "record", "name": key} for key in record_keys),
        {"scope": "scalar", "name": "value"},
    ]
    page_values = []
    present_columns = []
    for section, index, record in rows:
        is_object = isinstance(record, dict)
        values: list[Any] = [section, index, "object" if is_object else type(record).__name__]
        present = [0, 1, 2]
        for column_index, key in enumerate(record_keys, start=3):
            values.append(record.get(key) if is_object else None)
            if is_object and key in record:
                present.append(column_index)
        values.append(None if is_object else record)
        if not is_object:
            present.append(len(columns) - 1)
        page_values.append(values)
        present_columns.append(present)
    return {"columns": columns, "rows": page_values, "present_columns": present_columns}


def _validate_query_options(
    *,
    sections: Sequence[str] | None,
    candidate_id: str | None,
    source: str | None,
    field: str | None,
    disposition: str | None,
    offset: int,
    limit: int,
    output_format: str,
) -> None:
    if type(offset) is not int or offset < 0:
        raise ReportQueryError("offset must be a non-negative integer")
    if type(limit) is not int or not 1 <= limit <= MAX_PAGE_SIZE:
        raise ReportQueryError(f"limit must be between 1 and {MAX_PAGE_SIZE}")
    if output_format not in {"compact", "json"}:
        raise ReportQueryError("format must be compact or json")
    if candidate_id is not None and _CANDIDATE_ID_RE.fullmatch(candidate_id) is None:
        raise ReportQueryError("candidate-id must be a complete cc1_ SHA-256 identifier")
    if disposition is not None and disposition not in ALL_DISPOSITIONS:
        raise ReportQueryError(f"unknown disposition: {disposition}")
    if not any((candidate_id, source, field, disposition)) and not sections:
        raise ReportQueryError("choose --list-sections, --section, or at least one filter")


def _selected_sections(
    sections: Sequence[str] | None, queryable: dict[str, dict[str, Any]]
) -> list[str]:
    selected = list(dict.fromkeys(sections or DEFAULT_CANDIDATE_SECTIONS))
    unknown = [name for name in selected if name not in queryable]
    if unknown:
        available = ", ".join(queryable)
        raise ReportQueryError(
            f"unknown or non-list section {unknown[0]}; queryable sections: {available}"
        )
    return selected


def _collect_matches(
    verified: VerifiedReport,
    sections: Sequence[str],
    filters: dict[str, str | None],
) -> list[tuple[str, int, Any]]:
    matches: list[tuple[str, int, Any]] = []
    for section in sections:
        records = _resolve_section(verified.data, verified.completeness, section)
        matches.extend(
            (section, index, record)
            for index, record in enumerate(records)
            if _matches(record, **filters)
        )
    return matches


def _build_query_result(
    verified: VerifiedReport,
    selected_sections: Sequence[str],
    queryable: dict[str, dict[str, Any]],
    filters: dict[str, str | None],
    matches: Sequence[tuple[str, int, Any]],
    *,
    offset: int,
    limit: int,
    output_format: str,
) -> dict[str, Any]:
    page = matches[offset : offset + limit]
    next_offset = offset + len(page) if offset + len(page) < len(matches) else None
    result = {
        "schema_version": 1,
        "kind": "collision_report_query",
        **_report_header(verified),
        "sections": [_section_summary(name, queryable[name]) for name in selected_sections],
        "filters": filters,
        "offset": offset,
        "limit": limit,
        "matched_count": len(matches),
        "returned_count": len(page),
        "next_offset": next_offset,
        "exhausted": next_offset is None,
        "selection_sha256": _selection_digest(matches),
        "format": output_format,
    }
    if output_format == "json":
        result["items"] = [
            {"section": section, "index": index, "record": record}
            for section, index, record in page
        ]
    else:
        result.update(_compact_page(page, matches))
    return result


def query_collision_report(
    report_path: Path,
    *,
    sections: Sequence[str] | None = None,
    candidate_id: str | None = None,
    source: str | None = None,
    field: str | None = None,
    disposition: str | None = None,
    offset: int = 0,
    limit: int = 25,
    output_format: str = "compact",
) -> dict[str, Any]:
    _validate_query_options(
        sections=sections,
        candidate_id=candidate_id,
        source=source,
        field=field,
        disposition=disposition,
        offset=offset,
        limit=limit,
        output_format=output_format,
    )
    verified = _load_verified_report(report_path)
    queryable = _queryable_sections(verified)
    selected_sections = _selected_sections(sections, queryable)
    filters = {
        "candidate_id": candidate_id,
        "source": source,
        "field": field,
        "disposition": disposition,
    }
    matches = _collect_matches(verified, selected_sections, filters)
    return _build_query_result(
        verified,
        selected_sections,
        queryable,
        filters,
        matches,
        offset=offset,
        limit=limit,
        output_format=output_format,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only, integrity-checked query/export for schema-5 collision reports. "
            "Filtered queries without --section scan the canonical candidate lists."
        )
    )
    parser.add_argument("--report", required=True, type=Path, help="schema-5 collision JSON")
    parser.add_argument(
        "--section",
        action="append",
        dest="sections",
        help="queryable JSON list; repeatable (defaults to canonical candidate lists)",
    )
    parser.add_argument("--candidate-id", help="exact stable cc1_ candidate identifier")
    parser.add_argument("--source", help="exact source name, case-insensitive")
    parser.add_argument("--field", help="exact full field path, case-sensitive")
    parser.add_argument("--disposition", choices=ALL_DISPOSITIONS)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--format", choices=("compact", "json"), default="compact")
    parser.add_argument("--list-sections", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.list_sections:
            if any((args.sections, args.candidate_id, args.source, args.field, args.disposition)):
                parser.error("--list-sections cannot be combined with query filters or --section")
            result = list_report_sections(args.report)
        else:
            result = query_collision_report(
                args.report,
                sections=args.sections,
                candidate_id=args.candidate_id,
                source=args.source,
                field=args.field,
                disposition=args.disposition,
                offset=args.offset,
                limit=args.limit,
                output_format=args.format,
            )
    except (OSError, UnicodeError, ValueError) as exc:
        sys.stderr.write(f"query_collision_report: {exc}\n")
        return 2
    reconfigure_stdout = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure_stdout):
        reconfigure_stdout(encoding="utf-8")
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

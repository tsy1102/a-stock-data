"""Audited source-semantic decisions based on exact official-page observations.

This path records a direct mapping from a captured source field to a clearly
labelled official product-page metric. It does not establish a formal API
contract or a cross-source equivalence.
"""

from __future__ import annotations

import copy
from datetime import date
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
VERIFICATION_RELATIVE = Path("docs") / "field_verification"
VALID_ACTION = "verify_public_web_observation"
RESOLUTION = "verified_by_public_web_observation"
PLACEHOLDER_MEANINGS = {"", "待破解", "待确认", "待验证", "未验证", "未定义", "未知"}
OFFICIAL_PROVIDER_HOSTS = {"Eastmoney": {"data.eastmoney.com"}}


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{label} must be an object")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _decimal(value: Any, label: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"{label} must be a finite number")
    try:
        parsed = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{label} must be a finite number") from exc
    if not parsed.is_finite():
        raise ValueError(f"{label} must be a finite number")
    return parsed


def _safe_path(root: Path, relative: Any, label: str) -> Path:
    value = _text(relative, label)
    path = Path(value)
    if path.is_absolute():
        raise ValueError(f"{label} must be repository-relative")
    resolved_root = root.resolve()
    resolved = (resolved_root / path).resolve()
    if resolved == resolved_root or not resolved.is_relative_to(resolved_root):
        raise ValueError(f"{label} escapes the allowed directory")
    return resolved


def _verification_path(repo_root: Path, relative: Any, label: str) -> tuple[Path, str]:
    verification_root = (repo_root / VERIFICATION_RELATIVE).resolve()
    resolved = _safe_path(verification_root, relative, label)
    try:
        normalized = resolved.relative_to(verification_root).as_posix()
    except ValueError as exc:
        raise ValueError(f"{label} must stay inside docs/field_verification") from exc
    if not normalized.startswith("adjudications/public_web/"):
        raise ValueError(f"{label} must be under adjudications/public_web/")
    return resolved, normalized


def _sample_path(repo_root: Path, relative: Any, label: str) -> tuple[Path, str]:
    verification_root = (repo_root / VERIFICATION_RELATIVE).resolve()
    resolved = _safe_path(verification_root, relative, label)
    return resolved, resolved.relative_to(verification_root).as_posix()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} cannot be read: {exc}") from exc
    return _object(value, label)


def _stock_rows(payload: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    stocks = payload.get("stocks")
    rows: list[tuple[str, dict[str, Any]]] = []
    if isinstance(stocks, dict):
        for code, item in stocks.items():
            if isinstance(item, dict) and isinstance(item.get("data"), dict):
                rows.append((str(code), item["data"]))
    elif isinstance(stocks, list):
        for item in stocks:
            if isinstance(item, dict) and isinstance(item.get("data"), dict):
                rows.append((str(item.get("code", "")), item["data"]))
    return rows


def _raw_value(repo_root: Path, source_file: Any, stock_code: str, field_code: str) -> Any:
    path, _ = _sample_path(repo_root, source_file, "source_file")
    if not path.is_file() or path.name != "raw_push2.json":
        raise ValueError("source_file must reference an archived raw_push2.json")
    date_dir = path.parent.name
    if not re.fullmatch(r"20\d{6}", date_dir) or date_dir < "20261015":
        raise ValueError("source_file must use a retained sample date from 20261015 onward")
    payload = _read_json(path, "raw source sample")
    for code, data in _stock_rows(payload):
        if code == stock_code:
            if field_code not in data:
                raise ValueError(f"{stock_code} has no {field_code} in {source_file}")
            return data[field_code]
    raise ValueError(f"{stock_code} is absent from {source_file}")


def _validate_external_urls(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty HTTPS URL list")
    urls = []
    for item in value:
        url = _text(item, label)
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(f"{label} only accepts HTTPS links")
        if url not in urls:
            urls.append(url)
    return urls


def _validate_official_provider_urls(source: str, urls: list[str], repo_root: Path) -> None:
    lineage_path = repo_root / VERIFICATION_RELATIVE / "source_lineage.json"
    lineage = _read_json(lineage_path, "source lineage")
    sources = lineage.get("sources")
    if not isinstance(sources, dict) or not isinstance(sources.get(source), dict):
        raise ValueError(f"{source} is not an exact source in source_lineage.json")
    source_record = sources[source]
    provider = source_record.get("provider")
    if source_record.get("independence_status") != "confirmed":
        raise ValueError(f"{source} provider identity is not confirmed")
    allowed_hosts = OFFICIAL_PROVIDER_HOSTS.get(provider)
    if not allowed_hosts:
        raise ValueError(f"no official-page host allowlist is configured for provider {provider!r}")
    for url in urls:
        hostname = urlparse(url).hostname
        if hostname is None or hostname.lower() not in allowed_hosts:
            raise ValueError(f"{url} is not an allowlisted official {provider} page")


def _observation_evidence_line(source: str, code: str, observation: dict[str, Any]) -> str:
    payload = {
        "source": source,
        "code": code,
        "stock_code": observation["stock_code"],
        "data_date": observation["data_date"],
        "source_file": observation["source_file"],
        "raw_value": observation["raw_value"],
        "display_value": observation["display_value"],
        "display_increment": observation["display_increment"],
        "display_unit": observation["display_unit"],
        "page_url": observation["page_url"],
        "page_metric": observation["page_metric"],
        "display_text": observation["display_text"],
        "missing_as_zero": observation["missing_as_zero"],
    }
    return "[observation] " + json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def _validate_observations(
    decision: dict[str, Any], repo_root: Path, evidence_text: str
) -> list[dict[str, Any]]:
    source = _text(
        _object(decision.get("target"), "decision.target").get("source"), "target.source"
    )
    code = _text(decision["target"].get("code"), "target.code")
    if not re.fullmatch(r"f\d+", code):
        raise ValueError("public-page source observations currently require an fNN code path")
    unit = _text(decision.get("unit"), "decision.unit")
    urls = _validate_external_urls(decision.get("external_evidence"), "external_evidence")
    _validate_official_provider_urls(source, urls, repo_root)
    rows = decision.get("page_observations")
    if not isinstance(rows, list) or len(rows) < 2:
        raise ValueError("page_observations must contain at least two stock observations")

    checked: list[dict[str, Any]] = []
    seen_codes: set[str] = set()
    dates: set[str] = set()
    for raw_observation in rows:
        observation = _object(raw_observation, "page_observation")
        stock_code = _text(observation.get("stock_code"), "page_observation.stock_code")
        if stock_code in seen_codes:
            raise ValueError("page_observations must use distinct stock codes")
        seen_codes.add(stock_code)
        data_date = _text(observation.get("data_date"), "page_observation.data_date")
        try:
            if not re.fullmatch(r"20\d{6}", data_date):
                raise ValueError
            date.fromisoformat(f"{data_date[:4]}-{data_date[4:6]}-{data_date[6:8]}")
        except ValueError as exc:
            raise ValueError("page_observation.data_date must be YYYYMMDD") from exc
        dates.add(data_date)
        source_file = _text(observation.get("source_file"), "page_observation.source_file")
        source_path, _ = _sample_path(repo_root, source_file, "page_observation.source_file")
        if source_path.parent.name != data_date:
            raise ValueError("page observation date must match its raw source file directory")
        raw_value = _raw_value(repo_root, source_file, stock_code, code)
        declared_raw = observation.get("raw_value")
        if isinstance(raw_value, (int, float)) and isinstance(declared_raw, (int, float)):
            if _decimal(raw_value, "raw source value") != _decimal(
                declared_raw, "declared raw_value"
            ):
                raise ValueError(f"declared raw_value differs from archived {stock_code}::{code}")
        elif raw_value != declared_raw:
            raise ValueError(f"declared raw_value differs from archived {stock_code}::{code}")

        display_unit = _text(observation.get("display_unit"), "page_observation.display_unit")
        if display_unit != unit:
            raise ValueError("page display unit must match the adjudicated field unit")
        display_value = _decimal(observation.get("display_value"), "page_observation.display_value")
        increment = _decimal(
            observation.get("display_increment"), "page_observation.display_increment"
        )
        if increment <= 0:
            raise ValueError("display_increment must be positive")
        missing_as_zero = observation.get("missing_as_zero", False)
        if raw_value == "-":
            if missing_as_zero is not True or display_value != 0:
                raise ValueError("a raw '-' may map to zero only when the official page shows zero")
            comparison_value = Decimal(0)
        else:
            if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
                raise ValueError("raw source value must be numeric or the '-' sentinel")
            comparison_value = _decimal(raw_value, "raw source value")
        if abs(comparison_value - display_value) > increment / Decimal(2):
            raise ValueError(
                f"page value is outside its stated rounding precision for {stock_code}"
            )

        page_url = _text(observation.get("page_url"), "page_observation.page_url")
        if page_url not in urls:
            raise ValueError("page_url must appear in external_evidence")
        page_metric = _text(observation.get("page_metric"), "page_observation.page_metric")
        display_text = _text(observation.get("display_text"), "page_observation.display_text")
        normalized_observation = {
            "stock_code": stock_code,
            "data_date": data_date,
            "source_file": source_file.replace("\\", "/"),
            "raw_value": raw_value,
            "display_value": str(display_value),
            "display_increment": str(increment),
            "display_unit": display_unit,
            "page_url": page_url,
            "page_metric": page_metric,
            "display_text": display_text,
            "missing_as_zero": missing_as_zero,
        }
        required_line = _observation_evidence_line(source, code, normalized_observation)
        if required_line not in evidence_text:
            raise ValueError(
                f"evidence_file lacks the exact structured observation for {stock_code}::{code}"
            )
        checked.append(normalized_observation)
    if len(dates) != 1:
        raise ValueError("page observations for one field must align to a single data date")
    return checked


def _validate_formula_evidence(value: Any, repo_root: Path) -> dict[str, Any] | None:
    if value is None:
        return None
    formula = _object(value, "formula_validation")
    target_code = _text(formula.get("target_code"), "formula_validation.target_code")
    left_code = _text(formula.get("left_code"), "formula_validation.left_code")
    right_code = _text(formula.get("right_code"), "formula_validation.right_code")
    operator = _text(formula.get("operator"), "formula_validation.operator")
    if not all(re.fullmatch(r"f\d+", item) for item in (target_code, left_code, right_code)):
        raise ValueError("formula field names must be fNN paths")
    if operator not in {"+", "-"}:
        raise ValueError("formula operator must be '+' or '-'")
    files = formula.get("source_files")
    if not isinstance(files, list) or not files:
        raise ValueError("formula_validation.source_files must be a non-empty list")
    if len({str(item) for item in files}) != len(files):
        raise ValueError("formula_validation.source_files must be unique")

    dates: set[str] = set()
    codes: set[str] = set()
    seen_paths: set[Path] = set()
    numeric_samples = 0
    numeric_matches = 0
    dash_samples = 0
    dash_matches = 0
    for source_file in files:
        path, _ = _sample_path(repo_root, source_file, "formula_validation.source_file")
        if path in seen_paths:
            raise ValueError("formula_validation.source_files must resolve to unique files")
        seen_paths.add(path)
        if path.name != "raw_push2.json":
            raise ValueError("formula validation may only use archived raw_push2.json files")
        data_date = path.parent.name
        if not re.fullmatch(r"20\d{6}", data_date) or data_date < "20261015":
            raise ValueError("formula validation includes data before the retained sample start")
        try:
            date.fromisoformat(f"{data_date[:4]}-{data_date[4:6]}-{data_date[6:8]}")
        except ValueError as exc:
            raise ValueError("formula source date is not a valid YYYYMMDD date") from exc
        payload = _read_json(path, "formula source sample")
        file_samples = 0
        file_codes: set[str] = set()
        for stock_code, data in _stock_rows(payload):
            if not stock_code or stock_code in file_codes:
                raise ValueError(
                    f"formula source has a blank or duplicate stock code in {source_file}"
                )
            file_codes.add(stock_code)
            values = [data.get(target_code), data.get(left_code), data.get(right_code)]
            target_value, left_value, right_value = values
            if all(
                isinstance(item, (int, float)) and not isinstance(item, bool) for item in values
            ):
                file_samples += 1
                numeric_samples += 1
                codes.add(stock_code)
                expected = _decimal(left_value, left_code)
                expected = (
                    expected + _decimal(right_value, right_code)
                    if operator == "+"
                    else expected - _decimal(right_value, right_code)
                )
                if _decimal(target_value, target_code) == expected:
                    numeric_matches += 1
            elif (
                left_value == "-"
                and isinstance(target_value, (int, float))
                and isinstance(right_value, (int, float))
            ):
                file_samples += 1
                dash_samples += 1
                codes.add(stock_code)
                expected = (
                    Decimal(0) - _decimal(right_value, right_code)
                    if operator == "-"
                    else Decimal(0) + _decimal(right_value, right_code)
                )
                if _decimal(target_value, target_code) == expected:
                    dash_matches += 1
            else:
                raise ValueError(
                    f"formula source row {stock_code} in {source_file} has missing or non-numeric fields"
                )
        if file_samples == 0:
            raise ValueError(f"formula source file contains no formula rows: {source_file}")
        dates.add(data_date)

    if numeric_samples < 10 or len(dates) < 3 or len(codes) < 3:
        raise ValueError("formula validation needs 10 numeric rows, 3 data dates, and 3 stocks")
    expected_counts = {
        "numeric_samples": numeric_samples,
        "numeric_matches": numeric_matches,
        "dash_samples": dash_samples,
        "dash_matches": dash_matches,
        "distinct_dates": len(dates),
        "distinct_stocks": len(codes),
    }
    for key, actual in expected_counts.items():
        declared = formula.get(key)
        if type(declared) is not int or declared != actual:
            raise ValueError(f"formula_validation.{key} does not match archived data ({actual})")
    if numeric_matches != numeric_samples or dash_matches != dash_samples:
        raise ValueError("formula validation has mismatches")
    return {
        "target_code": target_code,
        "left_code": left_code,
        "right_code": right_code,
        "operator": operator,
        "source_files": [str(item).replace("\\", "/") for item in files],
        **expected_counts,
    }


def _validate_document_formula_summaries(
    document: dict[str, Any], decisions: list[Any], repo_root: Path
) -> dict[str, dict[str, Any]]:
    """Validate legacy and multi-formula evidence, keyed by target code."""
    formula_entries: list[Any] = []
    legacy = document.get("formula_validation")
    if legacy is not None:
        formula_entries.append(legacy)
    plural = document.get("formula_validations", [])
    if not isinstance(plural, list):
        raise ValueError("formula_validations must be an array")
    formula_entries.extend(plural)

    summaries: dict[str, dict[str, Any]] = {}
    for entry in formula_entries:
        summary = _validate_formula_evidence(entry, repo_root)
        if summary is None:
            continue
        target_code = summary["target_code"]
        if target_code in summaries:
            raise ValueError(f"duplicate formula validation target: {target_code}")
        summaries[target_code] = summary

    for target_code in summaries:
        matching_decisions = []
        for raw_decision in decisions:
            if not isinstance(raw_decision, dict):
                continue
            target = raw_decision.get("target")
            if isinstance(target, dict) and target.get("code") == target_code:
                matching_decisions.append(raw_decision)
        if len(matching_decisions) != 1:
            raise ValueError(
                f"formula validation target must match exactly one decision: {target_code}"
            )
    return summaries


def _metadata(row: dict[str, Any]) -> dict[str, str]:
    return {key: str(row.get(key) or "").strip() for key in ("canonical", "meaning", "unit")}


def _metadata_snapshot(value: Any, label: str) -> dict[str, str]:
    item = _object(value, label)
    if set(item) != {"canonical", "meaning", "unit"}:
        raise ValueError(f"{label} must contain exactly canonical, meaning, and unit")
    if any(not isinstance(item[key], str) for key in item):
        raise TypeError(f"{label} values must be strings")
    return {key: item[key].strip() for key in ("canonical", "meaning", "unit")}


def _safe_resolvable_conflict(row: dict[str, Any]) -> bool:
    evidence = row.get("status_evidence")
    if not isinstance(evidence, dict):
        return False
    values = evidence.get("values")
    if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
        return False
    if (
        evidence.get("reference_statuses") != ["verified"]
        or evidence.get("registry_aggregate_status") != "unverified"
        or set(values) != {"verified", "unverified"}
    ):
        return False
    reference_evidence = row.get("reference_evidence")
    if not isinstance(reference_evidence, list) or not reference_evidence:
        return False
    non_empty_statuses = [
        item.get("status")
        for item in reference_evidence
        if isinstance(item, dict) and item.get("status")
    ]
    if not non_empty_statuses or any(status != "verified" for status in non_empty_statuses):
        return False
    conflicts = row.get("attribute_conflicts")
    if not isinstance(conflicts, dict):
        return False
    if not conflicts:
        return True
    canonical_conflict = conflicts.get("canonical")
    return (
        set(conflicts) == {"canonical"}
        and isinstance(canonical_conflict, list)
        and bool(canonical_conflict)
    )


def _validate_prior_state(row: dict[str, Any], decision: dict[str, Any]) -> None:
    previous_status = _text(decision.get("previous_status"), "decision.previous_status")
    previous_resolution = _text(
        decision.get("previous_status_resolution"), "decision.previous_status_resolution"
    )
    if previous_status not in {"verified", "conflict", "candidate", "unverified"}:
        raise ValueError("unsupported previous status for public-page adjudication")
    if row.get("status") != previous_status or row.get("status_resolution") != previous_resolution:
        raise ValueError("target status changed since public-page review")
    previous = _metadata_snapshot(decision.get("previous"), "decision.previous")
    if _metadata(row) != previous:
        raise ValueError("target metadata changed since public-page review")
    previous_conflicts = decision.get("previous_attribute_conflicts")
    if not isinstance(previous_conflicts, dict):
        raise TypeError("previous_attribute_conflicts must be an object")
    if row.get("attribute_conflicts", {}) != previous_conflicts:
        raise ValueError("target attribute conflicts changed since public-page review")
    if set(previous_conflicts) - {"canonical"}:
        raise ValueError("public-page adjudication cannot resolve meaning or unit conflicts")
    if previous_status == "conflict":
        if previous_resolution != "status_conflict" or not _safe_resolvable_conflict(row):
            raise ValueError("public-page adjudication cannot resolve this status conflict")
    elif previous_status == "verified":
        if previous_resolution != "matched":
            raise ValueError("verified targets must have matched status before metadata enrichment")
    elif previous_status not in {"candidate", "unverified"}:
        raise ValueError("unsupported previous status")
    if previous["meaning"] not in PLACEHOLDER_MEANINGS:
        raise ValueError("public-page adjudication cannot overwrite an established meaning")
    if previous["canonical"] not in {"", row.get("code", "")}:
        raise ValueError("public-page adjudication cannot overwrite an established canonical name")
    if previous["unit"] not in {"", _text(decision.get("unit"), "decision.unit")}:
        raise ValueError("public-page adjudication cannot overwrite an established unit")


def _evidence_text(repo_root: Path, evidence_file: Any) -> tuple[Path, str, str]:
    path, normalized = _verification_path(repo_root, evidence_file, "evidence_file")
    if not path.is_file():
        raise FileNotFoundError(f"public-page evidence file not found: {normalized}")
    return path, normalized, path.read_text(encoding="utf-8")


def apply_public_web_observation_adjudications(
    registry: dict[str, Any],
    decision_document: dict[str, Any],
    decision_path: str,
    repo_root: Path = REPO_ROOT,
) -> tuple[dict[str, Any], dict[str, int]]:
    """Apply source-only semantics supported by exact official-page observations."""
    if decision_document.get("schema_version") != 1:
        raise ValueError("unsupported public-page adjudication schema_version")
    if decision_document.get("evidence_basis") != "public_web_observation":
        raise ValueError("public-page decisions require evidence_basis='public_web_observation'")
    if decision_document.get("report"):
        raise ValueError("public-page decisions cannot include a collision report")
    reviewer = _text(decision_document.get("reviewer"), "reviewer")
    reviewed_on = _text(decision_document.get("reviewed_on"), "reviewed_on")
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", reviewed_on):
            raise ValueError
        date.fromisoformat(reviewed_on)
    except ValueError as exc:
        raise ValueError("reviewed_on must be an ISO date") from exc
    _, evidence_file, evidence_text = _evidence_text(
        repo_root, decision_document.get("evidence_file")
    )
    decisions = decision_document.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise ValueError("decisions must be a non-empty list")
    formula_summaries = _validate_document_formula_summaries(
        decision_document, decisions, repo_root
    )

    updated = copy.deepcopy(registry)
    source_fields = updated.get("source_fields")
    if not isinstance(source_fields, list):
        raise ValueError("registry.source_fields must be a list")
    by_identity = {
        (row.get("source"), row.get("code")): row for row in source_fields if isinstance(row, dict)
    }
    seen_ids: set[str] = set()
    seen_targets: set[tuple[str, str]] = set()
    stats = {
        "public_web_observation_verified": 0,
        "status_conflicts_resolved": 0,
        "metadata_resolved": 0,
        "already_applied": 0,
        "mappings_added": 0,
    }

    for raw_decision in decisions:
        decision = _object(raw_decision, "decision")
        decision_id = _text(decision.get("id"), "decision.id")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,127}", decision_id):
            raise ValueError("decision.id contains unsupported characters")
        if decision_id in seen_ids:
            raise ValueError(f"duplicate decision id: {decision_id}")
        seen_ids.add(decision_id)
        if decision.get("action") != VALID_ACTION:
            raise ValueError(f"public-page decisions require action={VALID_ACTION!r}")
        target_object = _object(decision.get("target"), "decision.target")
        target = (
            _text(target_object.get("source"), "target.source"),
            _text(target_object.get("code"), "target.code"),
        )
        if target in seen_targets:
            raise ValueError(f"multiple decisions target the same field: {target}")
        seen_targets.add(target)
        row = by_identity.get(target)
        if row is None:
            raise ValueError(f"unknown target source field: {target[0]}::{target[1]}")

        observations = _validate_observations(decision, repo_root, evidence_text)
        canonical = _text(decision.get("canonical"), "decision.canonical")
        meaning = _text(decision.get("meaning"), "decision.meaning")
        unit = _text(decision.get("unit"), "decision.unit")
        if meaning in PLACEHOLDER_MEANINGS:
            raise ValueError("decision.meaning must resolve the placeholder")
        after = {"canonical": canonical, "meaning": meaning, "unit": unit}
        previous = _metadata_snapshot(decision.get("previous"), "decision.previous")
        previous_status = _text(decision.get("previous_status"), "decision.previous_status")
        previous_resolution = _text(
            decision.get("previous_status_resolution"), "decision.previous_status_resolution"
        )
        previous_conflicts = copy.deepcopy(decision.get("previous_attribute_conflicts"))
        rationale = _text(decision.get("rationale"), "decision.rationale")
        adjudication = {
            "id": decision_id,
            "action": VALID_ACTION,
            "status": "verified",
            "evidence_basis": "official_page_value_observation",
            "reviewer": reviewer,
            "reviewed_on": reviewed_on,
            "decision_file": decision_path.replace("\\", "/"),
            "evidence_file": evidence_file,
            "target": {"source": target[0], "code": target[1]},
            "previous_status": previous_status,
            "previous_status_resolution": previous_resolution,
            "previous_metadata": previous,
            "metadata_change": {"before": previous, "after": after},
            "previous_attribute_conflicts": previous_conflicts,
            "rationale": rationale,
            "external_evidence": _validate_external_urls(
                decision.get("external_evidence"), "external_evidence"
            ),
            "page_observations": observations,
        }
        formula_summary = formula_summaries.get(target[1])
        if formula_summary is not None:
            adjudication["formula_validation"] = formula_summary

        history = row.get("adjudications", [])
        if not isinstance(history, list):
            raise TypeError("source field adjudications must be a list")
        prior = next(
            (item for item in history if isinstance(item, dict) and item.get("id") == decision_id),
            None,
        )
        if prior is not None:
            if prior != adjudication or row.get("status") != "verified" or _metadata(row) != after:
                raise ValueError(
                    f"decision id already exists with different content: {decision_id}"
                )
            stats["already_applied"] += 1
            continue

        _validate_prior_state(row, decision)
        current_conflicts = row.get("attribute_conflicts", {})
        if not isinstance(previous_conflicts, dict) or not isinstance(current_conflicts, dict):
            raise TypeError("previous_attribute_conflicts and target conflicts must be objects")
        if previous_conflicts != current_conflicts:
            raise ValueError("previous_attribute_conflicts must snapshot the exact target conflict")
        row.update(
            {
                **after,
                "status": "verified",
                "status_resolution": RESOLUTION,
                "attribute_conflicts": {},
            }
        )
        section = f"Public page observation adjudication {reviewed_on}: {decision_id}"
        row.setdefault("sections", [])
        if not isinstance(row["sections"], list):
            raise TypeError("source field sections must be a list")
        if section not in row["sections"]:
            row["sections"].append(section)
            row["sections"].sort()
        if not row.get("section"):
            row["section"] = section
        row.setdefault("adjudications", []).append(copy.deepcopy(adjudication))
        references = row.setdefault("reference_evidence", [])
        if not isinstance(references, list):
            raise TypeError("source field reference_evidence must be a list")
        references.append(
            {
                "section": section,
                **after,
                "status": "verified",
                "status_raw": f"人工核对官方页面 {reviewed_on}: {decision_id}",
                "adjudication_id": decision_id,
                "evidence_basis": "official_page_value_observation",
                "evidence_file": evidence_file,
                "external_evidence": adjudication["external_evidence"],
                "page_observations": copy.deepcopy(observations),
            }
        )
        status_evidence = row.setdefault("status_evidence", {})
        if not isinstance(status_evidence, dict):
            raise TypeError("source field status_evidence must be an object")
        ids = status_evidence.setdefault("public_web_adjudication_ids", [])
        if not isinstance(ids, list):
            raise TypeError("status_evidence.public_web_adjudication_ids must be a list")
        if decision_id not in ids:
            ids.append(decision_id)
        if previous_status == "conflict":
            stats["status_conflicts_resolved"] += 1
        stats["metadata_resolved"] += 1
        stats["public_web_observation_verified"] += 1

    return updated, stats


def validate_registry_adjudications(
    registry: dict[str, Any], repo_root: Path = REPO_ROOT
) -> list[str]:
    """Check persisted public-page decisions, source snapshots, and evidence paths."""
    problems: list[str] = []
    rows = registry.get("source_fields", [])
    if not isinstance(rows, list):
        return ["registry.source_fields must be a list"]
    seen_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        source = row.get("source")
        code = row.get("code")
        if not isinstance(source, str) or not isinstance(code, str):
            problems.append("registry source_fields identity must contain string source and code")
            continue
        identity = (source, code)
        history = row.get("adjudications", [])
        if not isinstance(history, list):
            if row.get("status_resolution") == RESOLUTION:
                problems.append(
                    f"{identity[0]}::{identity[1]} public-web adjudications must be a list"
                )
            continue
        public_records = [
            item
            for item in history
            if isinstance(item, dict) and item.get("action") == VALID_ACTION
        ]
        if row.get("status_resolution") == RESOLUTION:
            if row.get("status") != "verified" or not all(_metadata(row).values()):
                problems.append(
                    f"{identity[0]}::{identity[1]} public-page verified row is incomplete"
                )
            if row.get("attribute_conflicts") not in (None, {}, []):
                problems.append(
                    f"{identity[0]}::{identity[1]} public-page verified row retains conflicts"
                )
            if not public_records:
                problems.append(f"{identity[0]}::{identity[1]} missing public-page adjudication")
        for record_index, record in enumerate(public_records):
            decision_id = record.get("id")
            if not isinstance(decision_id, str) or not decision_id:
                problems.append(f"{identity[0]}::{identity[1]} public-page adjudication lacks id")
                continue
            if decision_id in seen_ids:
                problems.append(f"duplicate public-page adjudication id: {decision_id}")
                continue
            seen_ids.add(decision_id)
            try:
                decision_path, decision_rel = _verification_path(
                    repo_root, record.get("decision_file"), "decision_file"
                )
                evidence_path, evidence_rel, evidence_text = _evidence_text(
                    repo_root, record.get("evidence_file")
                )
                if not decision_path.is_file():
                    raise FileNotFoundError(f"decision file not found: {decision_rel}")
                document = _read_json(decision_path, "public-page decision document")
                decisions = document.get("decisions")
                matching = (
                    [
                        item
                        for item in decisions
                        if isinstance(item, dict) and item.get("id") == decision_id
                    ]
                    if isinstance(decisions, list)
                    else []
                )
                if len(matching) != 1:
                    raise ValueError(f"decision file does not uniquely list {decision_id}")
                if not isinstance(decisions, list):
                    raise ValueError("public-page decision document requires a decisions array")
                formula_summaries = _validate_document_formula_summaries(
                    document, decisions, repo_root
                )
                decision = matching[0]
                target = decision.get("target", {})
                if target != {"source": identity[0], "code": identity[1]}:
                    raise ValueError("decision target does not match registry identity")
                if document.get("evidence_file") != evidence_rel:
                    raise ValueError("decision evidence_file differs from registry audit record")
                if document.get("reviewer") != record.get("reviewer") or document.get(
                    "reviewed_on"
                ) != record.get("reviewed_on"):
                    raise ValueError("decision reviewer/date differs from registry audit record")
                if (
                    record.get("action") != VALID_ACTION
                    or record.get("status") != "verified"
                    or record.get("evidence_basis") != "official_page_value_observation"
                    or record.get("metadata_change", {}).get("after")
                    != _metadata_from_decision(decision)
                    or record.get("metadata_change", {}).get("before")
                    != _metadata_snapshot(decision.get("previous"), "decision.previous")
                    or record.get("previous_metadata")
                    != _metadata_snapshot(decision.get("previous"), "decision.previous")
                    or record.get("previous_attribute_conflicts")
                    != decision.get("previous_attribute_conflicts")
                ):
                    raise ValueError(
                        "registry public-page adjudication differs from decision metadata"
                    )
                urls = _validate_external_urls(
                    decision.get("external_evidence"), "external_evidence"
                )
                _validate_official_provider_urls(str(identity[0]), urls, repo_root)
                if urls != record.get("external_evidence"):
                    raise ValueError(
                        "registry public-page adjudication differs from HTTPS evidence"
                    )
                checked_observations = _validate_observations(decision, repo_root, evidence_text)
                if record.get("page_observations") != checked_observations:
                    raise ValueError(
                        "registry public-page observations differ from decision evidence"
                    )
                expected_formula = formula_summaries.get(identity[1])
                if record.get("formula_validation") != expected_formula:
                    raise ValueError("registry formula evidence differs from its decision")
                if (
                    row.get("status_resolution") == RESOLUTION
                    and record_index == len(public_records) - 1
                ):
                    if _metadata(row) != _metadata_from_decision(decision):
                        raise ValueError(
                            "current row metadata differs from latest public-page decision"
                        )
                if record.get("evidence_file") != evidence_rel:
                    raise ValueError("registry adjudication evidence path is inconsistent")
            except (OSError, TypeError, ValueError, KeyError, AttributeError) as exc:
                problems.append(
                    f"{identity[0]}::{identity[1]} public-page adjudication invalid: {exc}"
                )
    return problems


def _metadata_from_decision(decision: dict[str, Any]) -> dict[str, str]:
    return {key: str(decision.get(key) or "").strip() for key in ("canonical", "meaning", "unit")}

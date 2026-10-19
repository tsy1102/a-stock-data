"""Validate reproducible formula evidence for individual registry fields.

This module checks a reviewed evidence bundle; it does not fetch web pages or
infer field meaning on its own. Public references and the formula rationale are
reviewed before the adjudication command is applied.
"""

from __future__ import annotations

import ast
import csv
import datetime as dt
from decimal import Decimal, DecimalException
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import collision_dates
import source_lineage_api as sla

MIN_ROWS = 10
MIN_INFORMATIVE_ROWS = 5
MIN_SYMBOLS = 3
MIN_TRADING_DATES = 3
MIN_REPORT_PERIODS = 2
MIN_PASS_RATE = Decimal("0.95")
MAX_RELATIVE_TOLERANCE = Decimal("0.01")
MAX_SAMPLE_BYTES = 10_000_000
MAX_SAMPLE_ROWS = 50_000
MAX_FORMULA_LENGTH = 240
MAX_FORMULA_NODES = 48
MAX_OUTLIERS = 10
PLACEHOLDER_MARKERS = ("填写", "占位", "待确认", "待验证", "yyyy", "example.")
PLACEHOLDER_VALUES = {
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
REFERENCE_KEYS = (
    "kind",
    "authority",
    "url",
    "revision",
    "locator",
    "accessed_on",
    "claim",
)
INPUT_KEYS = ("term", "source", "code", "unit", "date_column", "value_column")
ALLOWED_DOMAINS = {"trading_day", "report_period", "calendar_day"}
ALLOWED_REFERENCE_KINDS = {
    "formula_definition",
    "target_source_path",
    "input_source_definition",
    "official_data",
}


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise TypeError(f"{label} must be an object with string keys")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _concrete_string(value: Any, label: str) -> str:
    text = _string(value, label)
    folded = text.casefold()
    if any(marker in folded for marker in PLACEHOLDER_MARKERS):
        raise ValueError(f"{label} must replace the template placeholder")
    return text


def _placeholder_metadata(value: str, key: str, code: str) -> bool:
    normalized = value.strip()
    return (
        not normalized
        or (key == "canonical" and normalized == code)
        or normalized.casefold() in PLACEHOLDER_VALUES
    )


def _decimal(value: Any, label: str) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{label} must be a finite decimal")
    try:
        result = Decimal(str(value).strip())
    except (DecimalException, ValueError) as exc:
        raise ValueError(f"{label} must be a finite decimal") from exc
    if not result.is_finite():
        raise ValueError(f"{label} must be a finite decimal")
    return result


def _strict_date(value: Any, label: str) -> dt.date:
    text = _string(value, label)
    try:
        parsed = dt.date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{label} must use YYYY-MM-DD") from exc
    if parsed.isoformat() != text:
        raise ValueError(f"{label} must use YYYY-MM-DD")
    return parsed


def _confirmed_family(source: str, lineage: dict[str, Any], label: str) -> str:
    aliases = sla.runtime_aliases_for_source(source, lineage)
    families: set[str] = set()
    for alias in aliases:
        family = sla.runtime_family(alias, lineage)
        if family is not None:
            families.add(family)
    if len(families) != 1:
        raise ValueError(f"{label} must have one confirmed source independence family")
    return next(iter(families))


def _validate_references(value: Any, reviewed_on: dt.date) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise ValueError("formula_evidence.references must be a non-empty list")
    references: list[dict[str, str]] = []
    kinds: set[str] = set()
    required = set(REFERENCE_KEYS)
    for index, raw in enumerate(value):
        reference = _object(raw, f"formula_evidence.references[{index}]")
        if set(reference) != required:
            raise ValueError(f"formula_evidence.references[{index}] has unexpected keys")
        normalized = {
            key: _concrete_string(reference[key], f"reference.{key}") for key in REFERENCE_KEYS
        }
        if normalized["kind"] not in ALLOWED_REFERENCE_KINDS:
            raise ValueError(f"unsupported reference kind: {normalized['kind']}")
        try:
            url = urlsplit(normalized["url"])
        except ValueError as exc:
            raise ValueError("formula evidence reference URL is invalid") from exc
        if url.scheme != "https" or not url.hostname or url.username is not None:
            raise ValueError("formula evidence references must be HTTPS URLs")
        revision = normalized["revision"].casefold()
        if revision in {"main", "master", "latest", "current", "head"}:
            raise ValueError("reference.revision must be pinned or dated")
        accessed_on = _strict_date(normalized["accessed_on"], "reference.accessed_on")
        if accessed_on > reviewed_on:
            raise ValueError("reference.accessed_on cannot be later than reviewed_on")
        kinds.add(normalized["kind"])
        references.append(normalized)
    if "formula_definition" not in kinds or not kinds.intersection(
        {"target_source_path", "official_data"}
    ):
        raise ValueError(
            "references must include a formula_definition and target_source_path or official_data"
        )
    return references


def _formula_tree(expression: str, terms: set[str]) -> ast.Expression:
    if len(expression) > MAX_FORMULA_LENGTH:
        raise ValueError("formula expression is too long")
    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ValueError("formula expression is invalid") from exc
    nodes = list(ast.walk(parsed))
    if len(nodes) > MAX_FORMULA_NODES:
        raise ValueError("formula expression is too complex")
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.UnaryOp,
        ast.UAdd,
        ast.USub,
        ast.Name,
        ast.Constant,
        ast.Load,
    )
    if any(not isinstance(node, allowed) for node in nodes):
        raise ValueError(
            "formula permits only names, numeric constants, +, -, *, /, and parentheses"
        )
    names = {node.id for node in nodes if isinstance(node, ast.Name)}
    if names != terms:
        raise ValueError("formula names must match the declared input terms exactly")
    for node in nodes:
        if not isinstance(node, ast.Constant):
            continue
        if not isinstance(node.value, (int, float)) or isinstance(node.value, bool):
            raise ValueError("formula constants must be numeric")
        if not Decimal(str(node.value)).is_finite():
            raise ValueError("formula constants must be finite")
    return parsed


def _evaluate(node: ast.AST, values: dict[str, Decimal]) -> Decimal:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body, values)
    if isinstance(node, ast.Name):
        return values[node.id]
    if isinstance(node, ast.Constant):
        return Decimal(str(node.value))
    if isinstance(node, ast.UnaryOp):
        value = _evaluate(node.operand, values)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        left = _evaluate(node.left, values)
        right = _evaluate(node.right, values)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise ValueError("formula divides by zero")
            return left / right
    raise ValueError("unsupported formula expression")


def _validate_inputs(
    value: Any,
    target: tuple[str, str],
    records: dict[tuple[str, str], dict[str, Any]],
    lineage: dict[str, Any],
) -> tuple[list[dict[str, str]], set[str], set[str]]:
    if not isinstance(value, list) or not value:
        raise ValueError("formula_evidence.inputs must be a non-empty list")
    normalized: list[dict[str, str]] = []
    terms: set[str] = set()
    date_columns: set[str] = set()
    value_columns: set[str] = set()
    families: set[str] = set()
    required = set(INPUT_KEYS)
    for index, raw in enumerate(value):
        item = _object(raw, f"formula_evidence.inputs[{index}]")
        if set(item) != required:
            raise ValueError(f"formula_evidence.inputs[{index}] has unexpected keys")
        record = {key: _string(item[key], f"input.{key}") for key in INPUT_KEYS}
        term = record["term"]
        if not term.isascii() or not term.isidentifier() or term == "target" or term in terms:
            raise ValueError(f"input term is invalid or duplicated: {term!r}")
        terms.add(term)
        if record["date_column"] == record["value_column"]:
            raise ValueError(f"input {term} date and value columns must differ")
        date_column = record["date_column"]
        value_column = record["value_column"]
        if value_column in value_columns or value_column in date_columns:
            raise ValueError(f"duplicate formula sample value column: {value_column}")
        if date_column in value_columns:
            raise ValueError(f"formula sample date column overlaps a value column: {date_column}")
        date_columns.add(date_column)
        value_columns.add(value_column)
        identity = (record["source"], record["code"])
        if identity == target:
            raise ValueError("formula target cannot be one of its own inputs")
        source_field = records.get(identity)
        if source_field is None:
            raise ValueError(f"unknown formula input field: {identity[0]}::{identity[1]}")
        if source_field.get("status") != "verified":
            raise ValueError(f"formula input field is not verified: {identity[0]}::{identity[1]}")
        if source_field.get("attribute_conflicts"):
            raise ValueError(
                f"formula input field has metadata conflicts: {identity[0]}::{identity[1]}"
            )
        metadata = {
            key: str(source_field.get(key, "") or "").strip()
            for key in ("canonical", "meaning", "unit")
        }
        if any(_placeholder_metadata(value, key, identity[1]) for key, value in metadata.items()):
            raise ValueError(
                f"formula input field lacks verified metadata: {identity[0]}::{identity[1]}"
            )
        if record["unit"] != metadata["unit"]:
            raise ValueError(
                f"formula input unit differs from registry: {identity[0]}::{identity[1]}"
            )
        families.add(_confirmed_family(identity[0], lineage, f"formula input {identity[0]}"))
        normalized.append(record)
    if not terms:
        raise ValueError("formula_evidence.inputs must declare at least one term")
    return normalized, terms, families


def _sample_path(sample_file: str, verify_dir: Path) -> tuple[Path, Path]:
    candidate = (verify_dir / sample_file).resolve()
    allowed_root = (verify_dir / "derived_evidence").resolve()
    try:
        relative = candidate.relative_to(allowed_root)
    except ValueError as exc:
        raise ValueError(
            "sample_file must be inside docs/field_verification/derived_evidence"
        ) from exc
    if candidate.suffix.casefold() != ".csv" or not candidate.is_file():
        raise ValueError("sample_file must reference an existing CSV file")
    if candidate.stat().st_size > MAX_SAMPLE_BYTES:
        raise ValueError("formula sample CSV exceeds the 10 MB safety limit")
    return candidate, Path("derived_evidence") / relative


def _date_for_domain(value: Any, domain: str, label: str) -> dt.date:
    parsed = _strict_date(value, label)
    if domain == "trading_day":
        try:
            if not collision_dates.is_trading_session(parsed):
                raise ValueError(f"{label} is not a project trading day: {parsed.isoformat()}")
        except collision_dates.CalendarResolutionError as exc:
            raise ValueError(f"project calendar cannot validate {label}: {exc}") from exc
    return parsed


def _row_values(
    row: dict[str, str],
    target_columns: dict[str, str],
    inputs: list[dict[str, str]],
    domain: str,
    formula: ast.Expression,
) -> tuple[str, dt.date, Decimal, Decimal]:
    symbol = _string(row.get(target_columns["symbol"]), "sample symbol")
    target_date = _date_for_domain(row.get(target_columns["date"]), domain, target_columns["date"])
    observed = _decimal(row.get(target_columns["value"]), target_columns["value"])
    values: dict[str, Decimal] = {}
    for item in inputs:
        input_date = _date_for_domain(row.get(item["date_column"]), domain, item["date_column"])
        if input_date != target_date:
            raise ValueError(
                f"source dates are misaligned for {symbol}: {target_date} != {input_date}"
            )
        values[item["term"]] = _decimal(row.get(item["value_column"]), item["value_column"])
    try:
        expected = _evaluate(formula, values)
    except DecimalException as exc:
        raise ValueError(f"formula arithmetic failed for {symbol} on {target_date}") from exc
    if not expected.is_finite():
        raise ValueError(f"formula produced a non-finite result for {symbol} on {target_date}")
    return symbol, target_date, observed, expected


def _validate_sample_file(
    path: Path,
    target_columns: dict[str, str],
    inputs: list[dict[str, str]],
    domain: str,
    formula: ast.Expression,
    absolute_tolerance: Decimal,
    relative_tolerance: Decimal,
    reviewed_on: dt.date,
) -> dict[str, Any]:
    required_columns = set(target_columns.values())
    for item in inputs:
        required_columns.update((item["date_column"], item["value_column"]))
    informative_symbols: set[str] = set()
    informative_dates: set[dt.date] = set()
    seen_rows: set[tuple[str, dt.date]] = set()
    informative_scales: list[Decimal] = []
    outliers: list[dict[str, str]] = []
    rows = informative = passed = 0
    max_absolute = Decimal(0)
    max_relative = Decimal(0)
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if (
            not reader.fieldnames
            or any(not field.strip() for field in reader.fieldnames)
            or len(reader.fieldnames) != len(set(reader.fieldnames))
        ):
            raise ValueError("formula sample CSV must have unique header columns")
        missing = required_columns - set(reader.fieldnames)
        if missing:
            raise ValueError(f"formula sample CSV missing columns: {', '.join(sorted(missing))}")
        for row in reader:
            rows += 1
            if rows > MAX_SAMPLE_ROWS:
                raise ValueError("formula sample CSV exceeds 50,000 rows")
            if None in row or any(row.get(column) is None for column in required_columns):
                raise ValueError(f"formula sample row {rows + 1} has missing or extra columns")
            symbol, sample_date, observed, expected = _row_values(
                row, target_columns, inputs, domain, formula
            )
            if sample_date > reviewed_on:
                raise ValueError("formula sample date cannot be later than reviewed_on")
            key = (symbol, sample_date)
            if key in seen_rows:
                raise ValueError(f"duplicate symbol/date sample: {symbol} {sample_date}")
            seen_rows.add(key)
            if observed == 0 and expected == 0:
                continue
            informative += 1
            informative_symbols.add(symbol)
            informative_dates.add(sample_date)
            informative_scales.append(max(abs(observed), abs(expected)))
            try:
                error = abs(observed - expected)
                allowed = max(absolute_tolerance, abs(expected) * relative_tolerance)
                relative_error = error / max(abs(observed), abs(expected), Decimal("1e-30"))
            except DecimalException as exc:
                raise ValueError(f"formula comparison failed for sample row {rows + 1}") from exc
            max_absolute = max(max_absolute, error)
            max_relative = max(max_relative, relative_error)
            if error <= allowed:
                passed += 1
            elif len(outliers) < MAX_OUTLIERS:
                outliers.append(
                    {
                        "symbol": symbol,
                        "date": sample_date.isoformat(),
                        "observed": str(observed),
                        "expected": str(expected),
                        "absolute_error": str(error),
                    }
                )
    min_dates = MIN_REPORT_PERIODS if domain == "report_period" else MIN_TRADING_DATES
    if rows < MIN_ROWS or informative < MIN_INFORMATIVE_ROWS:
        raise ValueError("formula evidence requires at least 10 rows and 5 informative rows")
    if len(informative_symbols) < MIN_SYMBOLS or len(informative_dates) < min_dates:
        raise ValueError(
            f"formula evidence requires at least {MIN_SYMBOLS} informative symbols "
            f"and {min_dates} informative dates"
        )
    typical_scale = sorted(informative_scales)[len(informative_scales) // 2]
    if absolute_tolerance > typical_scale * MAX_RELATIVE_TOLERANCE:
        raise ValueError("absolute tolerance cannot exceed 1% of the typical informative value")
    pass_rate = Decimal(passed) / Decimal(informative)
    if pass_rate < MIN_PASS_RATE:
        raise ValueError(
            f"formula validation pass rate {pass_rate:.3%} is below {MIN_PASS_RATE:.0%}"
        )
    return {
        "row_count": rows,
        "informative_row_count": informative,
        "passed_row_count": passed,
        "pass_rate": float(pass_rate),
        "distinct_symbols": len(informative_symbols),
        "distinct_dates": sorted(day.isoformat() for day in informative_dates),
        "max_absolute_error": str(max_absolute),
        "max_relative_error": str(max_relative),
        "outlier_examples": outliers,
    }


def validate_derived_relation(
    value: Any,
    target: tuple[str, str],
    records: dict[tuple[str, str], dict[str, Any]],
    lineage: dict[str, Any],
    verify_dir: Path,
    reviewed_on_text: str,
) -> dict[str, Any]:
    """Validate source independence and replay formula evidence from a CSV bundle."""
    evidence = _object(value, "decision.formula_evidence")
    required = {
        "expression",
        "date_domain",
        "sample_file",
        "target_columns",
        "inputs",
        "tolerance",
        "references",
        "independence_rationale",
    }
    if set(evidence) != required:
        raise ValueError("formula_evidence contains missing or unsupported keys")
    reviewed_on = _strict_date(reviewed_on_text, "reviewed_on")
    expression = _string(evidence["expression"], "formula_evidence.expression")
    domain = _string(evidence["date_domain"], "formula_evidence.date_domain")
    if domain not in ALLOWED_DOMAINS:
        raise ValueError(f"formula_evidence.date_domain must be one of {sorted(ALLOWED_DOMAINS)}")
    target_columns = _object(evidence["target_columns"], "formula_evidence.target_columns")
    if set(target_columns) != {"symbol", "date", "value"}:
        raise ValueError("target_columns must contain exactly symbol, date, and value")
    target_columns = {
        key: _string(target_columns[key], f"target_columns.{key}")
        for key in ("symbol", "date", "value")
    }
    columns = list(target_columns.values())
    if len(columns) != len(set(columns)):
        raise ValueError("target sample columns must be unique")
    inputs, terms, input_families = _validate_inputs(evidence["inputs"], target, records, lineage)
    formula = _formula_tree(expression, terms)
    target_family = _confirmed_family(target[0], lineage, "formula target")
    if target_family in input_families:
        raise ValueError("formula inputs must come from source families independent of the target")
    rationale = _concrete_string(
        evidence["independence_rationale"], "formula_evidence.independence_rationale"
    )
    tolerance = _object(evidence["tolerance"], "formula_evidence.tolerance")
    if set(tolerance) != {"absolute", "relative"}:
        raise ValueError("tolerance must contain exactly absolute and relative")
    absolute_tolerance = _decimal(tolerance["absolute"], "tolerance.absolute")
    relative_tolerance = _decimal(tolerance["relative"], "tolerance.relative")
    if (
        absolute_tolerance < 0
        or relative_tolerance < 0
        or relative_tolerance > MAX_RELATIVE_TOLERANCE
    ):
        raise ValueError("tolerance must be nonnegative and relative tolerance cannot exceed 1%")
    references = _validate_references(evidence["references"], reviewed_on)
    sample_file = _string(evidence["sample_file"], "formula_evidence.sample_file")
    sample_path, sample_rel = _sample_path(sample_file, verify_dir)
    input_dates = {item["date_column"] for item in inputs}
    input_values = {item["value_column"] for item in inputs}
    if target_columns["symbol"] in input_dates | input_values:
        raise ValueError("target symbol column cannot be an input date or value column")
    if target_columns["value"] in input_dates | input_values:
        raise ValueError("target value column cannot be reused as an input column")
    if target_columns["date"] in input_values:
        raise ValueError("target date column cannot be reused as an input value column")
    if input_dates & (set(target_columns.values()) - {target_columns["date"]}):
        raise ValueError("input date columns may only share the target date column")
    summary = _validate_sample_file(
        sample_path,
        target_columns,
        inputs,
        domain,
        formula,
        absolute_tolerance,
        relative_tolerance,
        reviewed_on,
    )
    normalized_inputs = []
    for item in inputs:
        normalized_inputs.append({key: item[key] for key in INPUT_KEYS})
    return {
        "expression": expression,
        "date_domain": domain,
        "sample_file": sample_rel.as_posix(),
        "target_columns": target_columns,
        "inputs": normalized_inputs,
        "tolerance": {
            "absolute": str(absolute_tolerance),
            "relative": str(relative_tolerance),
        },
        "references": references,
        "independence": {
            "target_family": target_family,
            "input_families": sorted(input_families),
            "rationale": rationale,
        },
        "validation": summary,
    }

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline contract guard for the Tier 1 unified data layer."""

from __future__ import annotations

import ast
from dataclasses import fields
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CANONICAL_FIELDS = 113
EXPECTED_ELTDX_FIELDS = 12
RETIRED_UNCONSUMED_FIELDS = {"avg_price", "bid_ask_net"}
PRIVATE_CACHE_NAMES = {"_BATCH_QUOTE_CACHE", "_PD_EXTRA_CACHE", "_PD_EXTRA_CACHE_DATE"}
REPORT_FILES = (
    "main.py",
    "get_sht_report.py",
    "get_med_report.py",
    "get_lng_report.py",
    "get_mak_report.py",
    "get_val_report.py",
    "sc_report_runner.py",
)


def _parse(relative_path: str) -> ast.Module:
    return ast.parse((ROOT / relative_path).read_text(encoding="utf-8"), filename=relative_path)


def _function(tree: ast.AST, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    return next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
        ),
        None,
    )


def _check_private_cache_access(errors: list[str]) -> None:
    for relative_path in REPORT_FILES:
        path = ROOT / relative_path
        if not path.is_file():
            continue
        tree = _parse(relative_path)
        for node in ast.walk(tree):
            name = None
            if isinstance(node, ast.Attribute):
                name = node.attr
            elif isinstance(node, ast.Name):
                name = node.id
            if name in PRIVATE_CACHE_NAMES:
                errors.append(
                    f"{relative_path}:{getattr(node, 'lineno', '?')} references private cache {name}"
                )


def _check_canonical_assembly(errors: list[str]) -> None:
    tree = _parse("core/data_provider.py")
    assemble = _function(tree, "get_canonical_stock_data")
    if assemble is None:
        errors.append("get_canonical_stock_data is missing")
        return

    recorder = _function(assemble, "_record_source_as_of_date")
    if recorder is None:
        errors.append("explicit source date recorder is missing")
    else:
        payload_keys = {
            node.args[0].value
            for node in ast.walk(recorder)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        }
        if "as_of_date" not in payload_keys or "source_as_of_date" not in payload_keys:
            errors.append("source recorder must accept explicit as_of_date/source_as_of_date")
        if "data_date" in payload_keys or "collected_at" in payload_keys:
            errors.append("capture date must not be treated as an upstream effective date")

    canonical_call = next(
        (
            node
            for node in ast.walk(assemble)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "CanonicalStockData"
        ),
        None,
    )
    if canonical_call is None:
        errors.append("CanonicalStockData construction is missing")
        return
    keyword_values = {item.arg: item.value for item in canonical_call.keywords if item.arg}
    for key in ("quote_date", "collected_at", "field_as_of_dates"):
        if not isinstance(keyword_values.get(key), ast.Name):
            errors.append(f"CanonicalStockData.{key} must be supplied from explicit local metadata")
    quote_date_node = keyword_values.get("quote_date")
    if isinstance(quote_date_node, ast.Name) and quote_date_node.id != "quote_date":
        errors.append("quote_date must use the resolved field effective date")


def _check_tdx_calendar(errors: list[str]) -> None:
    tree = _parse("core/tdx_client.py")
    trading_date = _function(tree, "_get_trading_date_for_quote")
    before_open = _function(tree, "_is_before_market_open")
    if trading_date is None or not any(
        isinstance(node, ast.Name) and node.id == "latest_market_data_date"
        for node in ast.walk(trading_date)
    ):
        errors.append("TDX quote cache date must use latest_market_data_date")
    if before_open is None or not any(
        isinstance(node, ast.Name) and node.id == "is_trading_day" for node in ast.walk(before_open)
    ):
        errors.append("TDX pre-open routing must consult the project trading calendar")
    if _function(tree, "tdx_get_quote_full_with_sources") is None:
        errors.append("TDX field-source sidecar API is missing")


def _check_report_warnings(errors: list[str]) -> None:
    helper_tree = _parse("stock_common/sc_report_runner.py")
    provenance_helper = _function(helper_tree, "format_quote_provenance")
    helper_constants = (
        {
            node.value
            for node in ast.walk(provenance_helper)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        if provenance_helper is not None
        else set()
    )
    warning_text = "行情有效日期未核实"
    if provenance_helper is None or not any(warning_text in value for value in helper_constants):
        errors.append(
            "shared quote provenance formatter must warn when the effective date is unknown"
        )

    for relative_path in ("get_sht_report.py", "get_med_report.py"):
        tree = _parse(relative_path)
        uses_shared_formatter = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "format_quote_provenance"
            for node in ast.walk(tree)
        )
        if not uses_shared_formatter:
            errors.append(f"{relative_path} must use the shared quote provenance formatter")


def _check_canonical_consumer_coverage(canonical_names: set[str], errors: list[str]) -> int:
    from scripts.canonical_consumer_coverage import (
        CANONICAL_CONSUMER_EXEMPTIONS,
        CANONICAL_CONSUMER_FILES,
        find_canonical_consumer_reads,
    )

    missing_files = [
        relative_path
        for relative_path in CANONICAL_CONSUMER_FILES
        if not (ROOT / relative_path).is_file()
    ]
    if missing_files:
        errors.append(f"Canonical consumer source files are missing: {', '.join(missing_files)}")
        return 0

    sources = {
        relative_path: (ROOT / relative_path).read_text(encoding="utf-8")
        for relative_path in CANONICAL_CONSUMER_FILES
    }
    reads_by_field = find_canonical_consumer_reads(sources, canonical_names)
    read_fields = set(reads_by_field)
    exempt_fields = set(CANONICAL_CONSUMER_EXEMPTIONS)
    unclassified = canonical_names - read_fields - exempt_fields
    stale_exemptions = exempt_fields & read_fields
    removed_exemptions = exempt_fields - canonical_names
    if unclassified:
        errors.append(
            "Canonical fields have no report consumer or reviewed compatibility reason: "
            f"{sorted(unclassified)}"
        )
    if stale_exemptions:
        errors.append(
            "Canonical consumer exemptions now have report readers and need reclassification: "
            f"{sorted(stale_exemptions)}"
        )
    if removed_exemptions:
        errors.append(
            "Canonical consumer exemptions reference removed fields: "
            f"{sorted(removed_exemptions)}"
        )
    return len(read_fields)


def main() -> int:
    errors: list[str] = []
    consumer_field_count = 0
    try:
        sys.path.insert(0, str(ROOT))
        from core.canonical_metadata import build_field_as_of_dates, canonical_data_source
        from stock_common.sc_schema import CanonicalStockData, FIELD_SPECS

        canonical_names = {item.name for item in fields(CanonicalStockData)}
        extension_names = {name for name in canonical_names if name.startswith("eltdx_")}
        retained_orphans = canonical_names & RETIRED_UNCONSUMED_FIELDS
        if retained_orphans:
            errors.append(
                f"CanonicalStockData contains fields without report consumers: {sorted(retained_orphans)}"
            )
        if len(canonical_names) != EXPECTED_CANONICAL_FIELDS:
            errors.append(
                f"CanonicalStockData has {len(canonical_names)} fields; expected {EXPECTED_CANONICAL_FIELDS}"
            )
        if len(extension_names) != EXPECTED_ELTDX_FIELDS:
            errors.append(
                f"CanonicalStockData has {len(extension_names)} ELTDX fields; expected {EXPECTED_ELTDX_FIELDS}"
            )
        consumer_field_count = _check_canonical_consumer_coverage(canonical_names, errors)

        sample = CanonicalStockData(code="000001")
        if not isinstance(sample.field_sources, dict) or not isinstance(
            sample.field_as_of_dates, dict
        ):
            errors.append("field_sources and field_as_of_dates must default to dictionaries")
        if sample.time_anchor != "unknown" or sample.collected_at:
            errors.append("date metadata defaults must remain unknown/empty")

        spec_names = [spec.name for spec in FIELD_SPECS]
        if len(spec_names) != len(set(spec_names)):
            errors.append("FIELD_SPECS contains duplicate source-field metadata names")

        no_date = build_field_as_of_dates({"price": "realtime:tencent:batch"}, {}, zhb_data_date="")
        if no_date:
            errors.append(
                "field effective dates must not be inferred from collection time or source name"
            )
        zhb_dates = build_field_as_of_dates(
            {"price": "zhb:cache", "industry": "zhb:static"}, {}, zhb_data_date="20261016"
        )
        if zhb_dates != {"price": "2026-10-16", "industry": "2026-10-16"}:
            errors.append("ZHB field effective dates must come from the package data date")
        if canonical_data_source("realtime:tencent:batch") != "http":
            errors.append("batch source labels must preserve the HTTP source family")
        if canonical_data_source("realtime:batch:source_unknown") != "unknown":
            errors.append("unknown batch source labels must not be reported as HTTP")
    except Exception as exc:  # pragma: no cover - error path is the diagnostic result
        errors.append(f"contract imports/check failed: {type(exc).__name__}: {exc}")

    _check_private_cache_access(errors)
    _check_canonical_assembly(errors)
    _check_tdx_calendar(errors)
    _check_report_warnings(errors)

    if errors:
        print("Canonical contract verification: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Canonical contract verification: PASS")
    print("  - 113 attributes, including 12 ELTDX extensions")
    print(
        "  - "
        f"{consumer_field_count}/113 fields have report consumers; "
        "remaining fields have reviewed compatibility reasons"
    )
    print("  - date/source metadata and trading-calendar routing are explicit")
    print("  - report scripts use the public cache API and expose unknown dates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

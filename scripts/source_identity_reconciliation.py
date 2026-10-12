"""Conservative, per-endpoint source identity checks for service aggregators.

This lane answers whether an already understood endpoint is operationally
redundant with a verified project source. It does not establish field meaning,
change source lineage, or create an independent collision anchor.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Optional

try:
    from scripts import source_lineage_api as SLA
except ModuleNotFoundError:
    import source_lineage_api as SLA  # type: ignore[no-redef]


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "docs" / "field_verification"
REGISTRY_PATH = DATA_DIR / "field_registry.json"
ADAPTER_PATH = PROJECT_ROOT / "stock_common" / "sc_ftshare.py"
PROJECT_TMP = PROJECT_ROOT / ".tmp"
STATE_PATH = PROJECT_TMP / "source_identity_state.json"

MIN_CAPTURE_DATES = 3
MIN_MATCHED_SYMBOLS = 18
RECHECK_CAPTURE_DATES = 20


@dataclass(frozen=True)
class IdentityEndpoint:
    field_code: str
    output_key: str
    tool_name: str


# Keep endpoints separate: proving one redundant must not suppress other tools.
FTSHARE_ENDPOINTS = (
    IdentityEndpoint("comment_score", "comment_score", "ft_v1_stock_comment_score"),
    IdentityEndpoint("comment_desire", "comment_desire", "ft_v1_stock_comment_desire"),
    IdentityEndpoint("comment_focus", "comment_focus", "ft_v1_stock_comment_focus"),
    IdentityEndpoint("comment_org", "comment_org", "ft_v1_stock_comment_org_participate"),
    IdentityEndpoint("ggmx", "ggmx", "ft_v1_holder_stock_ggmx"),
    IdentityEndpoint("goodwill_detail", "goodwill_detail", "ft_v1_goodwill_stock_detail"),
)

_META_KEYS = {
    "crawl_batch_ts", "crawl_date", "fetch_time", "fetched_at", "request_id",
    "request_time", "url", "host", "secid", "seq", "sequence",
    "page", "page_no", "page_number", "rownum",
}
_IDENTITY_KEYS = {
    "code", "f12", "secucode", "security_code", "stock_code", "symbol",
    "ticker", "ts_code", "seq",
}
_DATE_KEYS = {
    "as_of_date", "date", "diagnose_date", "change_date", "notice_date",
    "report_date", "report_period", "trade_date", "tradedate",
}
_STOCK_CODE_KEYS = (
    "zqdm", "f12", "code", "stockcode", "stock_code", "security_code",
    "securitycode", "ticker", "ts_code",
)
_STOCK_VALUE_KEYS = {
    "code", "f12", "secucode", "security_code", "stock_code", "stockcode",
    "securitycode", "ticker", "ts_code",
}
_STOCK_CODE_PATTERN = re.compile(
    r"(?i)(?:SH|SZ|BJ)?(\d{6})(?:\.(?:SH|SZ|BJ))?"
)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def _is_project_trading_date(value: str) -> bool:
    try:
        calendar_module = importlib.import_module("scripts.collision_dates")
    except ModuleNotFoundError:
        calendar_module = importlib.import_module("collision_dates")
    checker = getattr(calendar_module, "is_trading_session")
    return bool(checker(datetime.strptime(value, "%Y%m%d").date()))


def _normalize_date(value: Any) -> Optional[str]:
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y%m%d")
    text = re.sub(r"\D", "", str(value or ""))
    if len(text) < 8:
        return None
    try:
        return datetime.strptime(text[:8], "%Y%m%d").strftime("%Y%m%d")
    except ValueError:
        return None


def _stock_code(value: Any) -> Optional[str]:
    match = _STOCK_CODE_PATTERN.fullmatch(str(value or "").strip())
    return match.group(1) if match else None


def _normalize_value(key: str, value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    text = str(value).strip()
    if key in _DATE_KEYS:
        return _normalize_date(value) or text
    if key in _STOCK_VALUE_KEYS:
        return _stock_code(value) or text
    if key in _IDENTITY_KEYS:
        return text
    try:
        number = Decimal(text.replace(",", ""))
    except (InvalidOperation, ValueError):
        return text
    if not number.is_finite():
        return text
    return format(number.normalize(), "f")


def _record_values(record: dict[str, Any]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for raw_key, value in record.items():
        key = str(raw_key).strip().casefold()
        if key in _META_KEYS or isinstance(value, (dict, list)):
            continue
        if isinstance(value, bool) or isinstance(value, (str, int, float)):
            values[key] = _normalize_value(key, value)
    return values


def _candidate_records(value: Any) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            direct = _record_values(node)
            if direct:
                records.append(direct)
            for child in node.values():
                if isinstance(child, (dict, list)):
                    walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(value)
    return records


def _anchor_records_for_symbol(document: Any, symbol: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def walk(node: Any, inherited_symbol: Optional[str] = None) -> None:
        if isinstance(node, dict):
            current_symbol = inherited_symbol
            normalized_keys = {
                str(key).strip().casefold(): value for key, value in node.items()
            }
            for key in _STOCK_CODE_KEYS:
                if key in normalized_keys:
                    explicit = _stock_code(normalized_keys[key])
                    if explicit:
                        if explicit != symbol:
                            return
                        current_symbol = explicit
                        break

            direct = _record_values(node)
            if current_symbol == symbol and direct:
                records.append(direct)

            stocks = normalized_keys.get("stocks")
            if isinstance(stocks, dict):
                for stock_key, stock_value in stocks.items():
                    walk(stock_value, _stock_code(stock_key) or current_symbol)

            for key, child in node.items():
                if str(key).strip().casefold() == "stocks":
                    continue
                walk(child, _stock_code(key) or current_symbol)
        elif isinstance(node, list):
            for child in node:
                walk(child, inherited_symbol)

    walk(document)
    return records


def _record_matches(candidate: dict[str, Any], reference: dict[str, Any]) -> bool:
    if not any(key in candidate for key in _DATE_KEYS):
        return False
    if not any(
        key not in (_IDENTITY_KEYS | _DATE_KEYS) and value is not None and value != ""
        for key, value in candidate.items()
    ):
        return False
    if not candidate.keys() <= reference.keys():
        return False
    return all(reference[key] == value for key, value in candidate.items())


def _symbol_endpoint_values(document: Any, endpoint: IdentityEndpoint) -> dict[str, Any]:
    stocks = document.get("stocks") if isinstance(document, dict) else None
    if not isinstance(stocks, dict):
        return {}
    values: dict[str, Any] = {}
    for raw_symbol, stock_record in stocks.items():
        symbol = _stock_code(raw_symbol)
        if symbol and isinstance(stock_record, dict):
            values[symbol] = stock_record.get(endpoint.output_key)
    return values


def _schema_fingerprint(values_by_symbol: dict[str, Any]) -> Optional[str]:
    schemas: list[tuple[tuple[str, str], ...]] = []
    for symbol in sorted(values_by_symbol):
        value = values_by_symbol[symbol]
        for record in _candidate_records(value):
            schemas.append(
                tuple(sorted((key, type(item).__name__) for key, item in record.items()))
            )
    if not schemas:
        return None
    payload = json.dumps(sorted(schemas), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _compare_endpoint_to_reference(
    candidate_values: dict[str, Any], reference_document: Any
) -> dict[str, Any]:
    candidate_symbols = {
        symbol: records
        for symbol, value in candidate_values.items()
        if (records := _candidate_records(value))
    }
    matched_symbols = 0
    total_records = 0
    matched_records = 0
    for symbol, candidate_records in candidate_symbols.items():
        total_records += len(candidate_records)
        remaining = _anchor_records_for_symbol(reference_document, symbol)
        symbol_matches = True
        for candidate in candidate_records:
            match_index = next(
                (
                    index
                    for index, reference in enumerate(remaining)
                    if _record_matches(candidate, reference)
                ),
                None,
            )
            if match_index is None:
                symbol_matches = False
            else:
                matched_records += 1
                remaining.pop(match_index)
        if symbol_matches and candidate_records:
            matched_symbols += 1

    return {
        "nonempty_symbols": len(candidate_symbols),
        "matched_symbols": matched_symbols,
        "candidate_records": total_records,
        "matched_records": matched_records,
        "record_match_rate": round(matched_records / total_records, 6) if total_records else 0.0,
        "qualifies": (
            len(candidate_symbols) >= MIN_MATCHED_SYMBOLS
            and matched_symbols >= MIN_MATCHED_SYMBOLS
            and total_records > 0
            and matched_records == total_records
        ),
    }


def _field_rows(registry: dict[str, Any], source: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    source_fields = registry.get("source_fields")
    if not isinstance(source_fields, list):
        return rows
    for row in source_fields:
        if (
            isinstance(row, dict)
            and row.get("source") == source
            and row.get("status") == "verified"
            and isinstance(row.get("code"), str)
        ):
            rows[row["code"]] = row
    return rows


def _load_policy_context(
    registry: Optional[dict[str, Any]] = None,
    lineage: Optional[dict[str, Any]] = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]], Optional[str]]:
    if registry is None:
        registry = _load_json(REGISTRY_PATH)
    if lineage is None:
        lineage = SLA.load_source_lineage(registry=registry)
    source_record = lineage.get("sources", {}).get("FTShare", {})
    if (
        not isinstance(source_record, dict)
        or source_record.get("anchor_eligible") is True
        or source_record.get("independence_status") == "confirmed"
    ):
        return registry, lineage, {}, "FTShare is no longer an unconfirmed service candidate"
    aliases = SLA.runtime_aliases_for_source("FTShare", lineage)
    if "ftshare" not in aliases:
        return registry, lineage, {}, "FTShare has no exact ftshare runtime mapping"
    rows = _field_rows(registry, "FTShare")
    endpoints = {
        endpoint.field_code: rows[endpoint.field_code]
        for endpoint in FTSHARE_ENDPOINTS
        if endpoint.field_code in rows
    }
    missing = [
        endpoint.field_code
        for endpoint in FTSHARE_ENDPOINTS
        if endpoint.field_code not in rows
    ]
    if missing:
        reason = "FTShare registry is missing verified fields: " + ", ".join(missing)
        return registry, lineage, {}, reason
    return registry, lineage, endpoints, None


def _anchor_aliases(registry: dict[str, Any], lineage: dict[str, Any]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for field in registry.get("source_fields", []):
        if not isinstance(field, dict) or field.get("status") != "verified":
            continue
        source = field.get("source")
        if not isinstance(source, str):
            continue
        source_record = lineage.get("sources", {}).get(source, {})
        if (
            not isinstance(source_record, dict)
            or source_record.get("anchor_eligible") is not True
            or source_record.get("independence_status") != "confirmed"
        ):
            continue
        for alias in SLA.runtime_aliases_for_source(source, lineage):
            if not isinstance(alias, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", alias):
                continue
            family = SLA.runtime_family(alias, lineage)
            if alias != "ftshare" and family:
                aliases[alias] = family
    return aliases


def _contract_fingerprint(
    endpoint: IdentityEndpoint, field_row: dict[str, Any], lineage: dict[str, Any]
) -> str:
    source_record = lineage.get("sources", {}).get("FTShare", {})
    try:
        adapter_hash = hashlib.sha256(ADAPTER_PATH.read_bytes()).hexdigest()
    except OSError:
        adapter_hash = "adapter-unavailable"
    contract = {
        "endpoint": endpoint.__dict__,
        "field": {
            key: field_row.get(key)
            for key in ("source", "code", "path", "canonical", "meaning", "unit", "status")
        },
        "lineage": {
            key: source_record.get(key)
            for key in (
                "runtime_aliases", "provider", "independence_family",
                "independence_status", "anchor_eligible",
            )
        },
        "adapter_sha256": adapter_hash,
    }
    payload = json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _source_entry(meta: dict[str, Any], source: str) -> dict[str, Any]:
    sources = meta.get("sources")
    if not isinstance(sources, dict):
        return {}
    for name, entry in sources.items():
        if str(name).casefold() == source.casefold() and isinstance(entry, dict):
            return entry
    return {}


def _source_date(meta: dict[str, Any], source: str) -> Optional[str]:
    entry = _source_entry(meta, source)
    value = entry.get("as_of_date")
    if value is None:
        dates = meta.get("source_as_of_dates")
        value = dates.get(source) if isinstance(dates, dict) else None
    return _normalize_date(value)


def _identity_meta(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        return {}
    meta = document.get("__source_meta__")
    return meta if isinstance(meta, dict) else {}


def _endpoint_skipped(
    endpoint: IdentityEndpoint, document: Any, source_meta: dict[str, Any]
) -> bool:
    for metadata in (_identity_meta(document), source_meta):
        skipped = metadata.get("identity_skipped_endpoints")
        if isinstance(skipped, dict) and endpoint.field_code in skipped:
            return True
    return False


def _endpoint_sampled(
    endpoint: IdentityEndpoint, document: Any, source_meta: dict[str, Any]
) -> bool:
    for metadata in (_identity_meta(document), source_meta):
        sampled = metadata.get("identity_sampled_endpoints")
        if isinstance(sampled, list):
            return endpoint.field_code in sampled
    return True


def _endpoint_contract_matches(
    endpoint: IdentityEndpoint,
    document: Any,
    source_meta: dict[str, Any],
    expected_fingerprint: str,
) -> bool:
    for metadata in (_identity_meta(document), source_meta):
        fingerprints = metadata.get("identity_contract_fingerprints")
        if isinstance(fingerprints, dict):
            return fingerprints.get(endpoint.field_code) == expected_fingerprint
    # Older captures predate this marker. They can form the initial baseline;
    # a saved baseline date bounds any later contract-change revalidation.
    return True


def _endpoint_recheck_requested(
    endpoint: IdentityEndpoint, document: Any, source_meta: dict[str, Any]
) -> bool:
    for metadata in (_identity_meta(document), source_meta):
        rechecks = metadata.get("identity_recheck_endpoints")
        if isinstance(rechecks, list):
            return endpoint.field_code in rechecks
    return False


def _date_folder(path: Path) -> Optional[str]:
    return _normalize_date(path.name) if re.fullmatch(r"\d{8}", path.name) else None


def _read_snapshot(
    folder: Path, current_meta: Optional[dict[str, Any]] = None
) -> Optional[dict[str, Any]]:
    folder_date = _date_folder(folder)
    raw_path = folder / "raw_ftshare.json"
    if folder_date is None or not raw_path.is_file():
        return None
    if current_meta is not None and _normalize_date(current_meta.get("data_date")) == folder_date:
        meta = current_meta
    elif (folder / "meta.json").is_file():
        try:
            meta = _load_json(folder / "meta.json")
        except (OSError, ValueError, TypeError):
            return None
    else:
        return None
    if (
        not isinstance(meta, dict)
        or meta.get("data_date_domain") not in {"trading", "mixed"}
        or _normalize_date(meta.get("data_date")) != folder_date
    ):
        return None
    try:
        if not _is_project_trading_date(folder_date):
            return None
    except (OSError, ValueError, TypeError):
        return None
    ftshare_meta = _source_entry(meta, "ftshare")
    if (
        ftshare_meta.get("ok") is not True
        or ftshare_meta.get("status") not in (None, "ok")
    ):
        return None
    try:
        document = _load_json(raw_path)
    except (OSError, ValueError, TypeError):
        return None
    if not isinstance(document, dict):
        return None
    return {"date": folder_date, "meta": meta, "document": document, "folder": folder}


def _read_anchor_document(snapshot: dict[str, Any], alias: str) -> Optional[dict[str, Any]]:
    meta = snapshot["meta"]
    entry = _source_entry(meta, alias)
    if entry.get("ok") is not True or entry.get("status") not in (None, "ok"):
        return None
    source_date = _source_date(meta, alias)
    if source_date != snapshot["date"]:
        return None
    path = snapshot["folder"] / f"raw_{alias}.json"
    if not path.is_file():
        return None
    try:
        document = _load_json(path)
    except (OSError, ValueError, TypeError):
        return None
    return document if isinstance(document, dict) else None


def _snapshot_samples(
    data_dir: Path,
    current_meta: Optional[dict[str, Any]],
    anchor_aliases: dict[str, str],
) -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    if not data_dir.is_dir():
        return snapshots
    for folder in sorted(data_dir.iterdir()):
        if not folder.is_dir():
            continue
        snapshot = _read_snapshot(folder, current_meta=current_meta)
        if snapshot is None or _source_date(snapshot["meta"], "ftshare") != snapshot["date"]:
            continue
        references: dict[str, dict[str, Any]] = {}
        for alias, family in anchor_aliases.items():
            document = _read_anchor_document(snapshot, alias)
            if document is not None:
                references[alias] = {"family": family, "document": document}
        snapshot["references"] = references
        snapshots.append(snapshot)
    return snapshots


def _endpoint_observations(
    endpoint: IdentityEndpoint,
    snapshots: list[dict[str, Any]],
    contract_fingerprint: str,
) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for snapshot in snapshots:
        document = snapshot["document"]
        source_meta = _source_entry(snapshot["meta"], "ftshare")
        if _endpoint_skipped(endpoint, document, source_meta):
            continue
        if not _endpoint_sampled(endpoint, document, source_meta):
            continue
        if not _endpoint_contract_matches(
            endpoint, document, source_meta, contract_fingerprint
        ):
            continue
        values = _symbol_endpoint_values(document, endpoint)
        schema = _schema_fingerprint(values)
        if schema is None:
            observations.append(
                {
                    "date": snapshot["date"],
                    "schema_fingerprint": None,
                    "references": {},
                    "sample_attempted": True,
                    "recheck_requested": _endpoint_recheck_requested(
                        endpoint, document, source_meta
                    ),
                }
            )
            continue
        references = {
            alias: {
                "family": reference["family"],
                **_compare_endpoint_to_reference(values, reference["document"]),
            }
            for alias, reference in snapshot["references"].items()
        }
        observations.append(
            {
                "date": snapshot["date"],
                "schema_fingerprint": schema,
                "candidate_symbols": len(values),
                "references": references,
                "sample_attempted": True,
                "recheck_requested": _endpoint_recheck_requested(
                    endpoint, document, source_meta
                ),
            }
        )
    return observations


def _best_reference_run(observations: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    if len(observations) < MIN_CAPTURE_DATES:
        return None
    recent = observations[-MIN_CAPTURE_DATES:]
    aliases = set(recent[0].get("references", {}))
    for item in recent[1:]:
        aliases.intersection_update(item.get("references", {}))
    candidates = []
    for alias in aliases:
        family = recent[0]["references"][alias]["family"]
        schema = recent[0].get("schema_fingerprint")
        if not schema:
            continue
        if any(
            not item.get("schema_fingerprint")
            or item["schema_fingerprint"] != schema
            or item["references"][alias]["family"] != family
            or item["references"][alias]["qualifies"] is not True
            for item in recent
        ):
            continue
        candidates.append(
            {
                "reference_source": alias,
                "reference_family": family,
                "schema_fingerprint": schema,
                "evidence_dates": [item["date"] for item in recent],
                "per_date": [
                    {
                        "date": item["date"],
                        **{
                            key: item["references"][alias][key]
                            for key in (
                                "nonempty_symbols", "matched_symbols",
                                "candidate_records", "matched_records", "record_match_rate",
                            )
                        },
                    }
                    for item in recent
                ],
            }
        )
    return sorted(candidates, key=lambda item: item["reference_source"])[0] if candidates else None


def _load_state(state_path: Path) -> tuple[dict[str, Any], Optional[str]]:
    if not state_path.exists():
        return {"schema_version": 1, "endpoints": {}}, None
    try:
        state = _load_json(state_path)
    except (OSError, ValueError, TypeError) as exc:
        return {"schema_version": 1, "endpoints": {}}, f"state unreadable: {type(exc).__name__}"
    if (
        not isinstance(state, dict)
        or state.get("schema_version") != 1
        or not isinstance(state.get("endpoints"), dict)
    ):
        return {"schema_version": 1, "endpoints": {}}, "state schema invalid"
    return state, None


def _write_state(state_path: Path, state: dict[str, Any]) -> None:
    PROJECT_TMP.mkdir(parents=True, exist_ok=True)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix="source_identity_", suffix=".json", dir=PROJECT_TMP
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp_name, state_path)
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)


def _trading_capture_dates(data_dir: Path, last_probe_date: str) -> set[str]:
    result: set[str] = set()
    if not data_dir.is_dir():
        return result
    for folder in data_dir.iterdir():
        if not folder.is_dir():
            continue
        capture_date = _date_folder(folder)
        if capture_date is None or capture_date <= last_probe_date:
            continue
        try:
            meta = _load_json(folder / "meta.json")
        except (OSError, ValueError, TypeError):
            continue
        if (
            isinstance(meta, dict)
            and meta.get("data_date_domain") in {"trading", "mixed"}
            and _normalize_date(meta.get("data_date")) == capture_date
        ):
            try:
                if _is_project_trading_date(capture_date):
                    result.add(capture_date)
            except (OSError, ValueError, TypeError):
                continue
    return result


def _plan_from_state(
    state: dict[str, Any],
    fingerprints: dict[str, str],
    data_dir: Path,
    data_date: Optional[str],
    force_reprobe: bool,
) -> dict[str, Any]:
    skipped: dict[str, dict[str, Any]] = {}
    recheck: list[str] = []
    for endpoint in FTSHARE_ENDPOINTS:
        record = state.get("endpoints", {}).get(endpoint.field_code)
        if not isinstance(record, dict) or record.get("status") not in {
            "operationally_redundant",
            "redundant",
        }:
            continue
        if record.get("contract_fingerprint") != fingerprints.get(endpoint.field_code):
            continue
        last_probe = _normalize_date(record.get("last_probe_date"))
        if force_reprobe:
            recheck.append(endpoint.field_code)
        elif last_probe is None:
            continue
        elif data_date and data_date <= last_probe:
            skipped[endpoint.field_code] = record
        elif len(_trading_capture_dates(data_dir, last_probe)) >= RECHECK_CAPTURE_DATES:
            recheck.append(endpoint.field_code)
        else:
            skipped[endpoint.field_code] = record
    return {"skip": skipped, "recheck": sorted(recheck)}


def get_ftshare_identity_plan(
    data_date: Optional[str] = None, *, force_reprobe: bool = False
) -> dict[str, Any]:
    """Return proven endpoint skips; malformed or missing evidence fails open."""
    try:
        registry, lineage, rows, policy_error = _load_policy_context()
        if policy_error:
            return {
                "skip": {}, "recheck": [], "status": "not_eligible", "reason": policy_error
            }
        fingerprints = {
            endpoint.field_code: _contract_fingerprint(
                endpoint, rows[endpoint.field_code], lineage
            )
            for endpoint in FTSHARE_ENDPOINTS
        }
        state, warning = _load_state(STATE_PATH)
        plan = _plan_from_state(
            state, fingerprints, DATA_DIR, _normalize_date(data_date), force_reprobe
        )
        plan["status"] = "ready" if warning is None else "failed_open"
        plan["contract_fingerprints"] = fingerprints
        if warning:
            plan["reason"] = warning
        return plan
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return {
            "skip": {}, "recheck": [], "status": "failed_open",
            "reason": f"{type(exc).__name__}: {exc}",
        }


def _endpoint_report(
    endpoint: IdentityEndpoint,
    field_row: dict[str, Any],
    lineage: dict[str, Any],
    snapshots: list[dict[str, Any]],
    old_record: Optional[dict[str, Any]],
    state_read_error: Optional[str],
) -> tuple[dict[str, Any], Optional[dict[str, Any]]]:
    fingerprint = _contract_fingerprint(endpoint, field_row, lineage)
    observations = _endpoint_observations(endpoint, snapshots, fingerprint)
    report: dict[str, Any] = {
        "field_code": endpoint.field_code,
        "endpoint": endpoint.tool_name,
        "status": "pending",
        "reason": "not enough matching completed trading-date samples",
        "observations": observations[-10:],
        "minimum_capture_dates": MIN_CAPTURE_DATES,
        "minimum_symbols_per_date": MIN_MATCHED_SYMBOLS,
    }
    if state_read_error:
        report["state_warning"] = state_read_error
        return report, None

    record_state = old_record if isinstance(old_record, dict) else {}
    old_proven = bool(
        record_state.get("status") in {"operationally_redundant", "redundant"}
    )
    old_resolved = bool(
        old_proven
        and record_state.get("contract_fingerprint") == fingerprint
    )
    old_probe_date = _normalize_date(record_state.get("last_probe_date"))
    contract_changed = bool(
        old_proven and record_state.get("contract_fingerprint") != fingerprint
    )
    revalidation_after = _normalize_date(
        record_state.get("revalidation_after_date")
    )
    if contract_changed:
        revalidation_after = old_probe_date
    attempted_after_old = [
        item
        for item in observations
        if old_probe_date is not None
        and (
            item["date"] > old_probe_date
            or (item["date"] == old_probe_date and item.get("recheck_requested"))
        )
        and item.get("sample_attempted")
    ]

    if old_resolved and not attempted_after_old:
        report.update(
            {
                "status": "operationally_redundant",
                "reason": (
                    "previous exact-match evidence remains valid; "
                    "endpoint probe is suppressed"
                ),
                "reference_source": record_state.get("reference_source"),
                "reference_family": record_state.get("reference_family"),
                "evidence_dates": record_state.get("evidence_dates", []),
                "next_recheck_after_capture_dates": RECHECK_CAPTURE_DATES,
            }
        )
        return report, dict(record_state)

    if old_resolved and attempted_after_old:
        latest = attempted_after_old[-1]
        alias = record_state.get("reference_source")
        latest_reference = latest.get("references", {}).get(alias)
        if (
            latest.get("schema_fingerprint") == record_state.get("schema_fingerprint")
            and isinstance(latest_reference, dict)
            and latest_reference.get("qualifies") is True
        ):
            refreshed = dict(record_state)
            refreshed["status"] = "operationally_redundant"
            refreshed["last_probe_date"] = latest["date"]
            report.update(
                {
                    "status": "operationally_redundant",
                    "reason": "scheduled endpoint recheck matched the stored contract and source",
                    "reference_source": alias,
                    "reference_family": record_state.get("reference_family"),
                    "evidence_dates": record_state.get("evidence_dates", []),
                    "last_probe_date": latest["date"],
                }
            )
            return report, refreshed
        report.update(
            {
                "status": "reopened",
                "reason": (
                    "scheduled recheck changed schema or did not match; "
                    "daily sampling resumes"
                ),
                "last_probe_date": latest["date"],
            }
        )
        return report, None

    if revalidation_after:
        observations_for_baseline = [
            item
            for item in observations
            if item["date"] > revalidation_after
            or (item["date"] == revalidation_after and item.get("recheck_requested"))
        ]
    else:
        observations_for_baseline = observations
    match = _best_reference_run(observations_for_baseline)
    if match is None:
        if revalidation_after:
            pending_record = {
                "status": "pending_revalidation",
                "contract_fingerprint": fingerprint,
                "revalidation_after_date": revalidation_after,
            }
            report.update(
                {
                    "status": "pending_revalidation",
                    "reason": (
                        "endpoint contract changed; collecting three new matching "
                        "closed trading-date samples"
                    ),
                    "revalidation_after_date": revalidation_after,
                }
            )
            return report, pending_record
        return report, None
    record = {
        "status": "operationally_redundant",
        "reference_source": match["reference_source"],
        "reference_family": match["reference_family"],
        "evidence_dates": match["evidence_dates"],
        "per_date": match["per_date"],
        "schema_fingerprint": match["schema_fingerprint"],
        "contract_fingerprint": fingerprint,
        "last_probe_date": match["evidence_dates"][-1],
    }
    report.update(
        {
            "status": "operationally_redundant",
            "reason": "every sampled record exactly matched one verified independent source",
            "reference_source": match["reference_source"],
            "reference_family": match["reference_family"],
            "evidence_dates": match["evidence_dates"],
            "per_date": match["per_date"],
        }
    )
    return report, record


def reconcile_source_identity(
    *,
    data_dir: Optional[Path] = None,
    state_path: Optional[Path] = None,
    current_meta: Optional[dict[str, Any]] = None,
    persist: bool = True,
) -> dict[str, Any]:
    """Analyze FTShare endpoint snapshots and persist only proven redundancy."""
    data_dir = Path(data_dir or DATA_DIR)
    state_path = Path(state_path or STATE_PATH)
    registry, lineage, rows, policy_error = _load_policy_context()
    if policy_error:
        return {"status": "not_eligible", "reason": policy_error, "endpoints": {}}

    anchor_aliases = _anchor_aliases(registry, lineage)
    snapshots = _snapshot_samples(data_dir, current_meta, anchor_aliases)
    state, state_warning = _load_state(state_path)
    new_endpoints: dict[str, Any] = dict(state.get("endpoints", {}))
    endpoint_reports: dict[str, Any] = {}
    changed = False
    for endpoint in FTSHARE_ENDPOINTS:
        report, record = _endpoint_report(
            endpoint,
            rows[endpoint.field_code],
            lineage,
            snapshots,
            state.get("endpoints", {}).get(endpoint.field_code),
            state_warning,
        )
        endpoint_reports[endpoint.field_code] = report
        if state_warning:
            continue
        if record is None:
            if endpoint.field_code in new_endpoints:
                new_endpoints.pop(endpoint.field_code, None)
                changed = True
        elif new_endpoints.get(endpoint.field_code) != record:
            new_endpoints[endpoint.field_code] = record
            changed = True

    result: dict[str, Any] = {
        "status": "ok" if state_warning is None else "failed_open",
        "minimum_capture_dates": MIN_CAPTURE_DATES,
        "minimum_symbols_per_date": MIN_MATCHED_SYMBOLS,
        "recheck_capture_dates": RECHECK_CAPTURE_DATES,
        "endpoints": endpoint_reports,
    }
    if state_warning:
        result["warning"] = state_warning
    if changed and persist and state_warning is None:
        _write_state(
            state_path,
            {
                "schema_version": 1,
                "updated": date.today().isoformat(),
                "endpoints": new_endpoints,
            },
        )
        result["state_updated"] = True
    return result

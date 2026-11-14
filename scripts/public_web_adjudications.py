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
DEFAULT_VERIFICATION_MODE = "resolve_placeholders"
CONFIRM_EXISTING_MODE = "confirm_existing"
REPORT_RECORD_CONFLICT_MODE = "resolve_report_record_conflict"
REPORT_SOURCE_RATING_CODE_MODE = "verify_report_source_rating_code"
REPORT_RECORD_OBSERVATION_TYPE = "report_author_list"
REPORT_RATING_OBSERVATION_TYPE = "report_previous_rating_name"
REPORT_EASTMONEY_RATING_CODE_OBSERVATION_TYPE = "report_eastmoney_rating_code"
REPORT_SOURCE_RATING_CODE_OBSERVATION_TYPE = "report_source_rating_code"
REPORT_RECORD_FIELDS = {
    "author",
    "researcher",
    "lastEmRatingName",
    "emRatingCode",
    "sRatingCode",
}
VERIFICATION_MODES = {
    DEFAULT_VERIFICATION_MODE,
    CONFIRM_EXISTING_MODE,
    REPORT_RECORD_CONFLICT_MODE,
    REPORT_SOURCE_RATING_CODE_MODE,
}
PLACEHOLDER_MEANINGS = {"", "待破解", "待确认", "待验证", "未验证", "未定义", "未知"}
OFFICIAL_PROVIDER_HOSTS = {"Eastmoney": {"data.eastmoney.com", "quote.eastmoney.com"}}


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{label} must be an object")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value.strip()


def _optional_text(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    return value.strip()


def _verification_mode(decision: dict[str, Any]) -> str:
    mode = _text(
        decision.get("verification_mode", DEFAULT_VERIFICATION_MODE),
        "decision.verification_mode",
    )
    if mode not in VERIFICATION_MODES:
        raise ValueError(f"unsupported public-page verification_mode: {mode}")
    return mode


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


def _raw_value(
    repo_root: Path,
    source: str,
    source_file: Any,
    stock_code: str,
    field_code: str,
    raw_collection: str | None = None,
) -> Any:
    path, _ = _sample_path(repo_root, source_file, "source_file")
    expected_files = {
        "东财-push2(stock/get)": "raw_push2.json",
        "东财-ulist239(np/get)": "raw_ulist239.json",
        "东财-push2ex": "raw_push2ex.json",
    }
    expected_file = expected_files.get(source)
    if expected_file is None:
        raise ValueError(f"public-page observation does not support source {source!r}")
    if not path.is_file() or path.name != expected_file:
        raise ValueError(f"source_file for {source} must reference an archived {expected_file}")
    date_dir = path.parent.name
    if not re.fullmatch(r"20\d{6}", date_dir) or date_dir < "20261015":
        raise ValueError("source_file must use a retained sample date from 20261015 onward")
    payload = _read_json(path, "raw source sample")
    if source == "东财-push2ex":
        allowed_collections = {"limit_up_pool", "limit_broken_pool", "limit_down_pool"}
        if not isinstance(raw_collection, str) or raw_collection not in allowed_collections:
            raise ValueError("Push2EX observations require a supported raw_collection")
        rows = payload.get(raw_collection)
        if not isinstance(rows, list):
            raise ValueError(f"{raw_collection} is not a list in {source_file}")
        matches = [
            item
            for item in rows
            if isinstance(item, dict) and str(item.get("code", "")) == stock_code
        ]
        if len(matches) != 1:
            raise ValueError(
                f"{stock_code} must occur exactly once in {raw_collection} of {source_file}"
            )
        if field_code not in matches[0]:
            raise ValueError(f"{stock_code} has no {field_code} in {source_file}")
        return matches[0][field_code]
    if raw_collection is not None:
        raise ValueError("raw_collection is only supported for 东财-push2ex")
    for code, data in _stock_rows(payload):
        if code == stock_code:
            if field_code not in data:
                raise ValueError(f"{stock_code} has no {field_code} in {source_file}")
            return data[field_code]
    raise ValueError(f"{stock_code} is absent from {source_file}")


def _report_record(
    repo_root: Path,
    source_file: Any,
    stock_code: str,
    record_identity: Any,
) -> dict[str, Any]:
    path, _ = _sample_path(repo_root, source_file, "source_file")
    if path.name != "raw_reports.json":
        raise ValueError("reports observations must reference raw_reports.json")
    date_dir = path.parent.name
    if not re.fullmatch(r"20\d{6}", date_dir) or date_dir < "20261015":
        raise ValueError("source_file must use a retained sample date from 20261015 onward")
    identity = _object(record_identity, "page_observation.record_identity")
    if set(identity) != {"infoCode", "title", "publishDate"}:
        raise ValueError("record_identity must contain exactly infoCode, title, and publishDate")
    for key in ("infoCode", "title", "publishDate"):
        _text(identity.get(key), f"record_identity.{key}")
    payload = _read_json(path, "raw reports sample")
    stocks = payload.get("stocks")
    if not isinstance(stocks, dict):
        raise ValueError("raw_reports.json stocks must be an object")
    records = stocks.get(stock_code)
    if not isinstance(records, list):
        raise ValueError(f"{stock_code} has no report records in {source_file}")
    matches = [
        record
        for record in records
        if isinstance(record, dict) and record.get("infoCode") == identity["infoCode"]
    ]
    if len(matches) != 1:
        raise ValueError("record_identity.infoCode must uniquely select one raw report")
    record = matches[0]
    if record.get("stockCode") != stock_code:
        raise ValueError("selected raw report stockCode differs from the stock key")
    for key in ("infoCode", "title", "publishDate"):
        if record.get(key) != identity[key]:
            raise ValueError(f"record_identity.{key} differs from the selected raw report")
    return record


def _report_rating_code_name_values(repo_root: Path, source_file: str) -> dict[str, set[str]]:
    path, _ = _sample_path(repo_root, source_file, "page_observation.source_file")
    payload = _read_json(path, "raw reports sample")
    stocks = payload.get("stocks")
    if not isinstance(stocks, dict):
        raise ValueError("raw_reports.json stocks must be an object")
    values: dict[str, set[str]] = {}
    for stock_code, stock_rows in stocks.items():
        if not isinstance(stock_rows, list):
            raise ValueError(f"raw report rows for {stock_code} must be a list")
        for record in stock_rows:
            if not isinstance(record, dict):
                raise ValueError(f"raw report rows for {stock_code} must contain objects")
            code = record.get("emRatingCode")
            name = record.get("emRatingName")
            if isinstance(code, str) and code and isinstance(name, str) and name:
                values.setdefault(code, set()).add(name)
    return values


def _report_source_rating_code_name_values(
    repo_root: Path, source_file: str
) -> tuple[dict[tuple[str, str], set[str]], dict[str, set[str]]]:
    path, _ = _sample_path(repo_root, source_file, "page_observation.source_file")
    payload = _read_json(path, "raw reports sample")
    stocks = payload.get("stocks")
    if not isinstance(stocks, dict):
        raise ValueError("raw_reports.json stocks must be an object")
    scoped_values: dict[tuple[str, str], set[str]] = {}
    global_values: dict[str, set[str]] = {}
    for stock_code, stock_rows in stocks.items():
        if not isinstance(stock_rows, list):
            raise ValueError(f"raw report rows for {stock_code} must be a list")
        for record in stock_rows:
            if not isinstance(record, dict):
                raise ValueError(f"raw report rows for {stock_code} must contain objects")
            organization = record.get("orgSName")
            code = record.get("sRatingCode")
            name = record.get("sRatingName")
            if code not in (None, "") and name not in (None, ""):
                if not isinstance(organization, str) or not organization:
                    raise ValueError("non-empty source rating code/name pair is missing orgSName")
                if not isinstance(code, str) or not isinstance(name, str):
                    raise ValueError("source rating code/name pairs must be strings")
            if (
                isinstance(organization, str)
                and organization
                and isinstance(code, str)
                and code
                and isinstance(name, str)
                and name
            ):
                scoped_values.setdefault((organization, code), set()).add(name)
                global_values.setdefault(code, set()).add(name)
    if any(len(names) != 1 for names in scoped_values.values()):
        raise ValueError("capture violates one sRatingName within its organization+code scope")
    return scoped_values, global_values


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
    if observation.get("observation_type") in {
        REPORT_RECORD_OBSERVATION_TYPE,
        REPORT_RATING_OBSERVATION_TYPE,
        REPORT_EASTMONEY_RATING_CODE_OBSERVATION_TYPE,
        REPORT_SOURCE_RATING_CODE_OBSERVATION_TYPE,
    }:
        payload = {
            "source": source,
            "code": code,
            "observation_type": observation["observation_type"],
            "stock_code": observation["stock_code"],
            "data_date": observation["data_date"],
            "source_file": observation["source_file"],
            "record_identity": observation["record_identity"],
            "raw_value": observation["raw_value"],
            "page_url": observation["page_url"],
            "page_metric": observation["page_metric"],
            "display_text": observation["display_text"],
        }
        if observation.get("observation_type") == REPORT_RECORD_OBSERVATION_TYPE:
            payload["page_authors"] = observation["page_authors"]
        elif observation.get("observation_type") == REPORT_RATING_OBSERVATION_TYPE:
            payload["page_current_rating"] = observation["page_current_rating"]
            payload["page_rating_change"] = observation["page_rating_change"]
        elif observation.get("observation_type") == REPORT_EASTMONEY_RATING_CODE_OBSERVATION_TYPE:
            payload["page_current_rating"] = observation["page_current_rating"]
        else:
            payload["raw_organization"] = observation["raw_organization"]
            payload["page_source_rating"] = observation["page_source_rating"]
            payload["match_type"] = observation["match_type"]
        return "[observation] " + json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
    payload = {
        "source": source,
        "code": code,
        "stock_code": observation["stock_code"],
        "data_date": observation["data_date"],
        "source_file": observation["source_file"],
        "raw_value": observation["raw_value"],
        "display_value": observation["display_value"],
        "display_unit": observation["display_unit"],
        "page_url": observation["page_url"],
        "page_metric": observation["page_metric"],
        "display_text": observation["display_text"],
        "missing_as_zero": observation["missing_as_zero"],
    }
    if "display_increment" in observation:
        payload["display_increment"] = observation["display_increment"]
    if "raw_collection" in observation:
        payload["raw_collection"] = observation["raw_collection"]
    if "value_transform" in observation:
        payload["value_transform"] = observation["value_transform"]
    if "raw_to_display_factor" in observation:
        payload["raw_to_display_factor"] = observation["raw_to_display_factor"]
    return "[observation] " + json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def _validate_report_record_observations(
    decision: dict[str, Any], repo_root: Path, evidence_text: str
) -> list[dict[str, Any]]:
    target = _object(decision.get("target"), "decision.target")
    source = _text(target.get("source"), "target.source")
    code = _text(target.get("code"), "target.code")
    if source != "reports" or code not in REPORT_RECORD_FIELDS:
        raise ValueError("report record observations do not support this reports field")
    expected_mode = (
        REPORT_SOURCE_RATING_CODE_MODE if code == "sRatingCode" else REPORT_RECORD_CONFLICT_MODE
    )
    if _verification_mode(decision) != expected_mode:
        raise ValueError("report record observations use a mode that does not match the target")
    unit = _optional_text(decision.get("unit"), "decision.unit")
    if unit:
        raise ValueError("report record fields must keep an empty physical unit")
    urls = _validate_external_urls(decision.get("external_evidence"), "external_evidence")
    _validate_official_provider_urls(source, urls, repo_root)
    rows = decision.get("page_observations")
    if not isinstance(rows, list) or len(rows) < 3:
        raise ValueError("report record observations require at least three stock records")

    checked: list[dict[str, Any]] = []
    seen_stocks: set[str] = set()
    seen_info_codes: set[str] = set()
    dates: set[str] = set()
    rating_code_names: dict[str, set[str]] | None = None
    source_rating_code_names: tuple[dict[tuple[str, str], set[str]], dict[str, set[str]]] | None = (
        None
    )
    source_rating_match_counts = {"exact": 0, "approximate": 0}
    for raw_observation in rows:
        observation = _object(raw_observation, "page_observation")
        expected_observation_type = (
            REPORT_RECORD_OBSERVATION_TYPE
            if code in {"author", "researcher"}
            else (
                REPORT_RATING_OBSERVATION_TYPE
                if code == "lastEmRatingName"
                else (
                    REPORT_SOURCE_RATING_CODE_OBSERVATION_TYPE
                    if code == "sRatingCode"
                    else REPORT_EASTMONEY_RATING_CODE_OBSERVATION_TYPE
                )
            )
        )
        if observation.get("observation_type") != expected_observation_type:
            raise ValueError("page_observation has an unsupported report observation_type")
        stock_code = _text(observation.get("stock_code"), "page_observation.stock_code")
        if not re.fullmatch(r"\d{6}", stock_code) or stock_code in seen_stocks:
            raise ValueError("report record observations require distinct six-digit stock codes")
        seen_stocks.add(stock_code)
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
        identity = _object(observation.get("record_identity"), "page_observation.record_identity")
        info_code = _text(identity.get("infoCode"), "record_identity.infoCode")
        if info_code in seen_info_codes:
            raise ValueError("report observations must use distinct infoCode values")
        seen_info_codes.add(info_code)
        record = _report_record(repo_root, source_file, stock_code, identity)
        raw_value = record.get(code)
        if raw_value is None or raw_value != observation.get("raw_value"):
            raise ValueError(f"declared raw_value differs from archived {stock_code}::{code}")

        normalized_details: dict[str, Any]
        if code in {"author", "researcher"}:
            author_ids = record.get("authorID")
            if (
                not isinstance(author_ids, list)
                or not author_ids
                or any(
                    not isinstance(item, str) or not re.fullmatch(r"\d+", item)
                    for item in author_ids
                )
            ):
                raise ValueError(
                    "selected raw report must contain a non-empty authorID string list"
                )
            page_authors_value = observation.get("page_authors")
            if not isinstance(page_authors_value, list) or not page_authors_value:
                raise ValueError("page_authors must be a non-empty list")
            page_authors: list[dict[str, str]] = []
            for raw_author in page_authors_value:
                author = _object(raw_author, "page_author")
                if set(author) != {"author_id", "name"}:
                    raise ValueError("page_author must contain exactly author_id and name")
                author_id = _text(author.get("author_id"), "page_author.author_id")
                name = _text(author.get("name"), "page_author.name")
                if not re.fullmatch(r"\d+", author_id):
                    raise ValueError("page_author.author_id must contain only digits")
                page_authors.append({"author_id": author_id, "name": name})
            page_ids = [author["author_id"] for author in page_authors]
            page_names = [author["name"] for author in page_authors]
            if page_ids != author_ids:
                raise ValueError("official author-link IDs differ from archived reports.authorID")
            if code == "author":
                if not isinstance(raw_value, list) or not raw_value:
                    raise ValueError("reports.author must be a non-empty string list")
                expected_authors: list[dict[str, str]] = []
                for item in raw_value:
                    if not isinstance(item, str):
                        raise ValueError("reports.author items must be strings")
                    author_id, separator, name = item.partition(".")
                    if not separator or not re.fullmatch(r"\d+", author_id) or not name.strip():
                        raise ValueError("reports.author items must use the ID.name format")
                    expected_authors.append({"author_id": author_id, "name": name.strip()})
                if expected_authors != page_authors:
                    raise ValueError("official author links differ from archived reports.author")
            else:
                if not isinstance(raw_value, str) or not raw_value:
                    raise ValueError(
                        "reports.researcher must be a non-empty comma-delimited string"
                    )
                raw_names = [name.strip() for name in raw_value.split(",")]
                if any(not name for name in raw_names) or raw_names != page_names:
                    raise ValueError(
                        "official author names differ from archived reports.researcher"
                    )
            expected_page_metric = "研报明细 > 作者"
            expected_display_text = " ".join(page_names)
            normalized_details = {"page_authors": page_authors}
        elif code == "lastEmRatingName":
            if not isinstance(raw_value, str) or not raw_value:
                raise ValueError("reports.lastEmRatingName must be a non-empty string")
            if record.get("ratingChange") != 3:
                raise ValueError("previous rating name can only be verified for unchanged ratings")
            page_current_rating = _text(
                observation.get("page_current_rating"), "page_observation.page_current_rating"
            )
            page_rating_change = _text(
                observation.get("page_rating_change"), "page_observation.page_rating_change"
            )
            if record.get("emRatingName") != page_current_rating:
                raise ValueError("official Eastmoney rating differs from archived emRatingName")
            if raw_value != page_current_rating or page_rating_change != "维持":
                raise ValueError("lastEmRatingName requires the current rating and 维持 page label")
            expected_page_metric = "研报明细 > 东财评级 / 评级变动"
            expected_display_text = f"{page_current_rating} / {page_rating_change}"
            normalized_details = {
                "page_current_rating": page_current_rating,
                "page_rating_change": page_rating_change,
            }
        elif code == "sRatingCode":
            if not isinstance(raw_value, str) or not re.fullmatch(r"\d+", raw_value):
                raise ValueError("reports.sRatingCode must be a non-empty decimal string")
            raw_source_rating = record.get("sRatingName")
            raw_organization = record.get("orgSName")
            if not isinstance(raw_source_rating, str) or not raw_source_rating:
                raise ValueError("selected raw report must contain a source sRatingName")
            if not isinstance(raw_organization, str) or not raw_organization:
                raise ValueError("selected raw report must contain orgSName for code scope")
            page_source_rating = _text(
                observation.get("page_source_rating"),
                "page_observation.page_source_rating",
            )
            if page_source_rating == raw_source_rating:
                match_type = "exact"
            elif raw_source_rating == "买入(Buy)" and page_source_rating == "买入":
                match_type = "approximate"
            else:
                raise ValueError("official source-rating text differs from archived sRatingName")
            if observation.get("match_type") != match_type:
                raise ValueError(
                    "match_type must distinguish exact from the supported Buy suffix match"
                )
            if observation.get("raw_organization") != raw_organization:
                raise ValueError("declared raw_organization differs from archived orgSName")
            if source_rating_code_names is None:
                source_rating_code_names = _report_source_rating_code_name_values(
                    repo_root, source_file
                )
            scoped_names, global_names = source_rating_code_names
            if scoped_names.get((raw_organization, raw_value)) != {raw_source_rating}:
                raise ValueError(
                    "archived sRatingCode does not have one sRatingName within its organization"
                )
            if len(global_names.get(raw_value, set())) < 2:
                raise ValueError(
                    "capture does not demonstrate that sRatingCode mappings are not globally unique"
                )
            source_rating_match_counts[match_type] += 1
            expected_page_metric = "研报正文 > 投资建议/评级原文"
            expected_display_text = _text(
                observation.get("display_text"), "page_observation.display_text"
            )
            if page_source_rating not in expected_display_text:
                raise ValueError("display_text must contain the observed source rating")
            normalized_details = {
                "raw_organization": raw_organization,
                "page_source_rating": page_source_rating,
                "match_type": match_type,
            }
        else:
            if not isinstance(raw_value, str) or not re.fullmatch(r"\d+", raw_value):
                raise ValueError("reports.emRatingCode must be a non-empty decimal string")
            page_current_rating = _text(
                observation.get("page_current_rating"), "page_observation.page_current_rating"
            )
            if record.get("emRatingName") != page_current_rating:
                raise ValueError("official Eastmoney rating differs from archived emRatingName")
            if rating_code_names is None:
                rating_code_names = _report_rating_code_name_values(repo_root, source_file)
            if rating_code_names.get(raw_value) != {page_current_rating}:
                raise ValueError(
                    "archived emRatingCode does not have one consistent emRatingName in this capture"
                )
            expected_page_metric = "研报明细 > 东财评级"
            expected_display_text = page_current_rating
            normalized_details = {"page_current_rating": page_current_rating}

        page_url = _text(observation.get("page_url"), "page_observation.page_url")
        if page_url not in urls:
            raise ValueError("page_url must appear in external_evidence")
        parsed_url = urlparse(page_url)
        expected_page = (
            f"/report/info/{info_code}.html"
            if code == "sRatingCode"
            else f"/report/{stock_code}.html"
        )
        if parsed_url.path != expected_page or parsed_url.query or parsed_url.fragment:
            raise ValueError("page_url must be the official page for the observed report record")
        page_metric = _text(observation.get("page_metric"), "page_observation.page_metric")
        if page_metric != expected_page_metric:
            raise ValueError("page_metric does not identify the official report columns")
        display_text = _text(observation.get("display_text"), "page_observation.display_text")
        if code != "sRatingCode" and display_text != expected_display_text:
            raise ValueError("display_text differs from the observed report fields")
        normalized_observation = {
            "observation_type": expected_observation_type,
            "stock_code": stock_code,
            "data_date": data_date,
            "source_file": source_file.replace("\\", "/"),
            "record_identity": {
                "infoCode": identity["infoCode"],
                "title": identity["title"],
                "publishDate": identity["publishDate"],
            },
            "raw_value": raw_value,
            "page_url": page_url,
            "page_metric": page_metric,
            "display_text": display_text,
            **normalized_details,
        }
        required_line = _observation_evidence_line(source, code, normalized_observation)
        if required_line not in evidence_text:
            raise ValueError(
                f"evidence_file lacks the exact structured report observation for {stock_code}::{code}"
            )
        checked.append(normalized_observation)
    if len(dates) != 1:
        raise ValueError("report observations for one field must use a single capture date")
    if code == "sRatingCode" and source_rating_match_counts["exact"] < 2:
        raise ValueError("sRatingCode requires at least two exact source-rating text matches")
    return checked


def _validate_observations(
    decision: dict[str, Any], repo_root: Path, evidence_text: str
) -> list[dict[str, Any]]:
    source = _text(
        _object(decision.get("target"), "decision.target").get("source"), "target.source"
    )
    code = _text(decision["target"].get("code"), "target.code")
    if source == "reports":
        return _validate_report_record_observations(decision, repo_root, evidence_text)
    unit = _optional_text(decision.get("unit"), "decision.unit") or ""
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
        raw_collection = observation.get("raw_collection")
        if source == "东财-push2ex":
            raw_collection = _text(raw_collection, "page_observation.raw_collection")
        elif raw_collection is not None:
            raise ValueError("raw_collection is only supported for 东财-push2ex")
        raw_value = _raw_value(
            repo_root, source, source_file, stock_code, code, raw_collection=raw_collection
        )
        declared_raw = observation.get("raw_value")
        if isinstance(raw_value, (int, float)) and isinstance(declared_raw, (int, float)):
            if _decimal(raw_value, "raw source value") != _decimal(
                declared_raw, "declared raw_value"
            ):
                raise ValueError(f"declared raw_value differs from archived {stock_code}::{code}")
        elif raw_value != declared_raw:
            raise ValueError(f"declared raw_value differs from archived {stock_code}::{code}")

        display_unit = (
            _optional_text(observation.get("display_unit"), "page_observation.display_unit") or ""
        )
        factor_value = observation.get("raw_to_display_factor")
        value_transform = observation.get("value_transform")
        missing_as_zero = observation.get("missing_as_zero", False)
        normalized_display_value: str
        if value_transform is None:
            if factor_value is None:
                if display_unit != unit:
                    raise ValueError("different page and raw units require raw_to_display_factor")
                raw_to_display_factor = Decimal(1)
            else:
                raw_to_display_factor = _decimal(
                    factor_value, "page_observation.raw_to_display_factor"
                )
                if raw_to_display_factor <= 0:
                    raise ValueError("raw_to_display_factor must be positive")
                if display_unit == unit and raw_to_display_factor != 1:
                    raise ValueError(
                        "raw_to_display_factor must be 1 when page and raw units are equal"
                    )
            display_value = _decimal(
                observation.get("display_value"), "page_observation.display_value"
            )
            increment = _decimal(
                observation.get("display_increment"), "page_observation.display_increment"
            )
            if increment <= 0:
                raise ValueError("display_increment must be positive")
            if raw_value == "-":
                if missing_as_zero is not True or display_value != 0:
                    raise ValueError(
                        "a raw '-' may map to zero only when the official page shows zero"
                    )
                comparison_value = Decimal(0)
            else:
                if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
                    raise ValueError(
                        "raw source value must be numeric or use an explicit text transform"
                    )
                comparison_value = _decimal(raw_value, "raw source value") * raw_to_display_factor
            if abs(comparison_value - display_value) > increment / Decimal(2):
                raise ValueError(
                    f"page value is outside its stated rounding precision for {stock_code}"
                )
            normalized_display_value = str(display_value)
        elif value_transform == "exact_text" or value_transform == "hhmmss":
            if factor_value is not None:
                raise ValueError("text observations cannot use raw_to_display_factor")
            if display_unit != unit:
                raise ValueError("text observations must keep the raw unit")
            if "display_increment" in observation:
                raise ValueError("text observations cannot use display_increment")
            if missing_as_zero is not False:
                raise ValueError("text observations cannot use missing_as_zero")
            if not isinstance(raw_value, str):
                raise ValueError("text observations require a string raw source value")
            normalized_display_value = _text(
                observation.get("display_value"), "page_observation.display_value"
            )
            if value_transform == "exact_text":
                expected_display = raw_value
            else:
                if not re.fullmatch(r"\d{1,6}", raw_value):
                    raise ValueError("hhmmss transform requires 1-6 decimal digits")
                digits = raw_value.zfill(6)
                hour, minute, second = int(digits[:2]), int(digits[2:4]), int(digits[4:6])
                if hour > 23 or minute > 59 or second > 59:
                    raise ValueError("hhmmss transform received an invalid clock time")
                expected_display = f"{digits[:2]}:{digits[2:4]}:{digits[4:6]}"
            if normalized_display_value != expected_display:
                raise ValueError(
                    f"page value differs from the {value_transform} transform for {stock_code}"
                )
            increment = None
        else:
            raise ValueError("unsupported page_observation.value_transform")

        page_url = _text(observation.get("page_url"), "page_observation.page_url")
        if page_url not in urls:
            raise ValueError("page_url must appear in external_evidence")
        page_metric = _text(observation.get("page_metric"), "page_observation.page_metric")
        display_text = _text(observation.get("display_text"), "page_observation.display_text")
        if value_transform is not None and display_text != normalized_display_value:
            raise ValueError("text observation display_text must equal display_value")
        normalized_observation = {
            "stock_code": stock_code,
            "data_date": data_date,
            "source_file": source_file.replace("\\", "/"),
            "raw_value": raw_value,
            "display_value": normalized_display_value,
            "display_unit": display_unit,
            "page_url": page_url,
            "page_metric": page_metric,
            "display_text": display_text,
            "missing_as_zero": missing_as_zero,
        }
        if increment is not None:
            normalized_observation["display_increment"] = str(increment)
        if raw_collection is not None:
            normalized_observation["raw_collection"] = raw_collection
        if value_transform is not None:
            normalized_observation["value_transform"] = value_transform
        if factor_value is not None:
            normalized_observation["raw_to_display_factor"] = format(
                raw_to_display_factor.normalize(), "f"
            )
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


def _validate_prior_state(
    row: dict[str, Any], decision: dict[str, Any], after: dict[str, str]
) -> None:
    verification_mode = _verification_mode(decision)
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
    if verification_mode == REPORT_SOURCE_RATING_CODE_MODE:
        target = _object(decision.get("target"), "decision.target")
        if (target.get("source"), target.get("code")) != ("reports", "sRatingCode"):
            raise ValueError("verify_report_source_rating_code only supports reports::sRatingCode")
        if (
            previous_status != "unverified"
            or previous_resolution != "registry_status_only_single_source"
            or previous_conflicts
        ):
            raise ValueError(
                "source rating code verification requires an unverified field without metadata conflicts"
            )
        if not after["canonical"] or after["meaning"] in PLACEHOLDER_MEANINGS:
            raise ValueError("source rating code verification requires a bounded meaning")
        if after["unit"] != previous["unit"]:
            raise ValueError("source rating code verification cannot alter the unit")
        return
    if verification_mode == REPORT_RECORD_CONFLICT_MODE:
        target = _object(decision.get("target"), "decision.target")
        identity = (target.get("source"), target.get("code"))
        if identity not in {
            ("reports", "author"),
            ("reports", "researcher"),
            ("reports", "lastEmRatingName"),
            ("reports", "emRatingCode"),
        }:
            raise ValueError(
                "resolve_report_record_conflict only supports reports::author, reports::researcher, reports::lastEmRatingName, and reports::emRatingCode"
            )
        if previous_status != "conflict" or previous_resolution != "reference_status_conflict":
            raise ValueError(
                "report record conflict resolution requires a reference-status conflict"
            )
        if not previous_conflicts or set(previous_conflicts) - {"canonical", "meaning"}:
            raise ValueError(
                "report record conflict resolution only accepts canonical/meaning conflicts"
            )
        for key in previous_conflicts:
            values = previous_conflicts[key]
            if (
                not isinstance(values, list)
                or not values
                or any(not isinstance(item, str) for item in values)
            ):
                raise ValueError(f"previous {key} conflict must be a non-empty string list")
        if not after["canonical"] or after["meaning"] in PLACEHOLDER_MEANINGS:
            raise ValueError("report record conflict resolution requires canonical and meaning")
        if after["unit"] != previous["unit"]:
            raise ValueError("report record conflict resolution cannot alter the unit")
        for key in ("canonical", "meaning"):
            if key not in previous_conflicts and after[key] != previous[key]:
                raise ValueError(
                    f"report record conflict resolution cannot alter established {key}"
                )
        return
    if verification_mode == CONFIRM_EXISTING_MODE:
        if previous_status not in {"candidate", "unverified"}:
            raise ValueError("confirm_existing only accepts candidate or unverified source fields")
        if after != previous:
            raise ValueError("confirm_existing requires unchanged canonical, meaning, and unit")
        if previous_conflicts:
            raise ValueError("confirm_existing cannot be used while attribute conflicts remain")
        return

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
    if previous["unit"] not in {
        "",
        _optional_text(decision.get("unit"), "decision.unit") or "",
    }:
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
        "metadata_confirmed": 0,
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
        verification_mode = _verification_mode(decision)
        canonical = _text(decision.get("canonical"), "decision.canonical")
        meaning = _text(decision.get("meaning"), "decision.meaning")
        unit = _optional_text(decision.get("unit"), "decision.unit")
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
        if "verification_mode" in decision:
            adjudication["verification_mode"] = verification_mode
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

        _validate_prior_state(row, decision, after)
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
        if verification_mode == CONFIRM_EXISTING_MODE:
            stats["metadata_confirmed"] += 1
        else:
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
            metadata = _metadata(row)
            unitless_report_record = (
                source == "reports"
                and code in REPORT_RECORD_FIELDS
                and bool(public_records)
                and all(
                    item.get("verification_mode") == REPORT_RECORD_CONFLICT_MODE
                    or item.get("verification_mode") == REPORT_SOURCE_RATING_CODE_MODE
                    for item in public_records
                )
            )
            unitless_exact_text_record = bool(public_records) and all(
                isinstance(item.get("metadata_change"), dict)
                and isinstance(item["metadata_change"].get("after"), dict)
                and item["metadata_change"]["after"].get("unit", "") == ""
                and isinstance(item.get("page_observations"), list)
                and bool(item["page_observations"])
                and all(
                    isinstance(observation, dict)
                    and observation.get("value_transform") == "exact_text"
                    and observation.get("display_unit", "") == ""
                    for observation in item["page_observations"]
                )
                for item in public_records
            )
            metadata_complete = bool(metadata["canonical"] and metadata["meaning"])
            metadata_complete = metadata_complete and bool(
                metadata["unit"] or unitless_report_record or unitless_exact_text_record
            )
            if row.get("status") != "verified" or not metadata_complete:
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
                    or record.get("verification_mode")
                    != (_verification_mode(decision) if "verification_mode" in decision else None)
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

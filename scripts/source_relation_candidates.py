"""Observed overlap between runtime sources for exact, normalized field paths.

This report is deliberately observational: matching values can identify a route
worth reviewing for redundancy, but cannot establish provider identity, field
meaning, or permission to suppress collection.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from itertools import combinations
import math
import re
from typing import Any, Callable

from scripts.collision_candidate_methods import _within_rounding_screen
from scripts.temporal_policy import SOURCE_CONFIRMED_DATE_ORIGINS

MIN_INFORMATIVE_PAIRS = 5
MIN_DISTINCT_DATES = 3
MIN_DISTINCT_SECURITIES = 3
MAX_SOURCE_PAIRS = 100
MAX_FIELD_PATHS_PER_PAIR = 40


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def _missing(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _date_token(value: Any) -> str | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        text = str(value)
    elif isinstance(value, float) and math.isfinite(value) and value.is_integer():
        text = str(int(value))
    else:
        text = str(value).strip()
    try:
        if re.fullmatch(r"\d{8}", text):
            parsed = date(int(text[:4]), int(text[4:6]), int(text[6:8]))
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            parsed = date.fromisoformat(text)
        else:
            return None
    except ValueError:
        return None
    if not 1900 <= parsed.year <= 2100:
        return None
    return parsed.isoformat()


def _same_observed_value(left: Any, right: Any, is_close: Callable[..., bool]) -> bool:
    left_number = _as_number(left)
    right_number = _as_number(right)
    if left_number is not None and right_number is not None:
        strict = left_number.is_integer() and right_number.is_integer()
        return is_close(left_number, right_number, strict=strict)
    return str(left).strip() == str(right).strip()


def _sample_context_matches(left_meta: dict, right_meta: dict) -> bool:
    if left_meta.get("domain") != right_meta.get("domain"):
        return False
    # Compare the actual dates, not the metadata mechanism: two sources can
    # establish the same date through different, independently confirmed rules.
    left_source_day = _date_token(left_meta.get("as_of_date"))
    right_source_day = _date_token(right_meta.get("as_of_date"))
    if not left_source_day or left_source_day != right_source_day:
        return False
    if left_meta.get("phase") not in {"closed", "calendar"}:
        return False
    if left_meta.get("phase") != right_meta.get("phase"):
        return False
    return True


def _compare_field_path(
    left_id: str,
    right_id: str,
    left: dict,
    right: dict,
    sample_eligible: Callable[[dict, Any], bool],
    is_close: Callable[..., bool],
) -> dict[str, Any]:
    left_values = left.get("vals", {})
    right_values = right.get("vals", {})
    common_keys = set(left_values) & set(right_values)
    left_meta = left.get("sample_meta", {})
    right_meta = right.get("sample_meta", {})
    left_eligible_keys = {
        key
        for key in left_values
        if sample_eligible(left, key)
        and isinstance(left_meta.get(key), dict)
        and left_meta[key].get("as_of_date")
        and left_meta[key].get("phase") in {"closed", "calendar"}
    }
    right_eligible_keys = {
        key
        for key in right_values
        if sample_eligible(right, key)
        and isinstance(right_meta.get(key), dict)
        and right_meta[key].get("as_of_date")
        and right_meta[key].get("phase") in {"closed", "calendar"}
    }
    left_only_sample_count = len(left_eligible_keys - right_eligible_keys)
    right_only_sample_count = len(right_eligible_keys - left_eligible_keys)
    comparable = exact = informative = mismatches = near_matches = 0
    sample_key_dates: set[str] = set()
    source_as_of_dates: set[str] = set()
    securities: set[str] = set()
    source_date_confirmed = True
    context_skips = 0
    mismatch_examples: list[dict[str, Any]] = []
    near_match_examples: list[dict[str, Any]] = []

    for key in sorted(common_keys, key=lambda item: (str(item[1]), str(item[0]))):
        left_sample_meta = left_meta.get(key, {})
        right_sample_meta = right_meta.get(key, {})
        if not (
            sample_eligible(left, key)
            and sample_eligible(right, key)
            and _sample_context_matches(left_sample_meta, right_sample_meta)
        ):
            context_skips += 1
            continue
        if (
            left_sample_meta.get("as_of_date_origin") not in SOURCE_CONFIRMED_DATE_ORIGINS
            or right_sample_meta.get("as_of_date_origin") not in SOURCE_CONFIRMED_DATE_ORIGINS
        ):
            source_date_confirmed = False
        left_value = left_values[key]
        right_value = right_values[key]
        comparable += 1
        sample_key_dates.add(str(key[1]))
        source_as_of_dates.add(str(left_sample_meta["as_of_date"]))
        securities.add(str(key[0]).split("#event:", 1)[0])
        if not (_missing(left_value) and _missing(right_value)) and not (
            _as_number(left_value) == 0 and _as_number(right_value) == 0
        ):
            informative += 1
        left_date = _date_token(left_value)
        right_date = _date_token(right_value)
        if left_date is not None and right_date is not None:
            exact_value = left_date == right_date
        elif (left.get("is_date_value_candidate") or right.get("is_date_value_candidate")) and (
            left_date is not None or right_date is not None
        ):
            exact_value = False
        else:
            exact_value = _same_observed_value(left_value, right_value, is_close)
        if exact_value:
            exact += 1
        else:
            mismatches += 1
            if len(mismatch_examples) < 5:
                mismatch_examples.append(
                    {
                        "security": str(key[0]),
                        "sample_date": str(key[1]),
                        "left": left_value,
                        "right": right_value,
                    }
                )
            if not (left.get("is_date_value_candidate") or right.get("is_date_value_candidate")):
                left_number = _as_number(left_value)
                right_number = _as_number(right_value)
                if (
                    left_number is not None
                    and right_number is not None
                    and _within_rounding_screen(left_number, right_number)
                ):
                    near_matches += 1
                    if len(near_match_examples) < 5:
                        absolute_error = abs(left_number - right_number)
                        near_match_examples.append(
                            {
                                "security": str(key[0]),
                                "sample_date": str(key[1]),
                                "left": left_number,
                                "right": right_number,
                                "absolute_error": absolute_error,
                                "relative_error": absolute_error
                                / max(abs(left_number), abs(right_number)),
                            }
                        )

    low_information = bool(left.get("is_low_information") or right.get("is_low_information"))
    strong = (
        mismatches == 0
        and context_skips == 0
        and informative >= MIN_INFORMATIVE_PAIRS
        and len(sample_key_dates) >= MIN_DISTINCT_DATES
        and len(securities) >= MIN_DISTINCT_SECURITIES
        and source_date_confirmed
        and left_only_sample_count == 0
        and right_only_sample_count == 0
        and not low_information
    )
    return {
        "left": left_id,
        "right": right_id,
        "common_sample_count": comparable,
        "left_only_sample_count": left_only_sample_count,
        "right_only_sample_count": right_only_sample_count,
        "exact_sample_count": exact,
        "informative_sample_count": informative,
        "mismatch_count": mismatches,
        "rounding_near_match_sample_count": near_matches,
        "context_skipped_count": context_skips,
        "low_information_path": low_information,
        "distinct_sample_key_dates": sorted(sample_key_dates),
        "distinct_source_as_of_dates": sorted(source_as_of_dates),
        "distinct_security_count": len(securities),
        "strong_path_evidence": strong,
        "source_date_confirmed": source_date_confirmed,
        "mismatch_examples": mismatch_examples,
        "rounding_near_match_examples": near_match_examples,
    }


def build_source_relation_review(
    store: dict[str, dict],
    source_of: Callable[[str], str],
    code_of: Callable[[str], str],
    family_of: Callable[[str], str | None],
    sample_eligible: Callable[[dict, Any], bool],
    is_close: Callable[..., bool],
    repositories_for_source: Callable[[str], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Summarize exact-path overlap while keeping route and semantic claims apart."""
    by_source: dict[str, dict[str, list[tuple[str, dict]]]] = defaultdict(lambda: defaultdict(list))
    for field_id, info in store.items():
        source = source_of(field_id)
        code = code_of(field_id)
        by_source[source][code].append((field_id, info))

    rows = []
    ambiguous_path_count = 0
    for left_source, right_source in combinations(sorted(by_source), 2):
        left_paths = by_source[left_source]
        right_paths = by_source[right_source]
        shared_codes = sorted(set(left_paths) & set(right_paths))
        if not shared_codes:
            continue
        field_rows = []
        ambiguous_codes = []
        for code in shared_codes:
            left_entries = left_paths[code]
            right_entries = right_paths[code]
            if len(left_entries) != 1 or len(right_entries) != 1:
                ambiguous_path_count += 1
                ambiguous_codes.append(code)
                continue
            left_id, left_info = left_entries[0]
            right_id, right_info = right_entries[0]
            field_result = _compare_field_path(
                left_id,
                right_id,
                left_info,
                right_info,
                sample_eligible,
                is_close,
            )
            field_result["code"] = code
            if field_result["common_sample_count"] or field_result["context_skipped_count"]:
                field_rows.append(field_result)

        comparable_paths = [row for row in field_rows if row["common_sample_count"]]
        if not comparable_paths and not any(row["context_skipped_count"] for row in field_rows):
            continue
        mismatched_paths = [row for row in comparable_paths if row["mismatch_count"]]
        near_match_paths = [
            row for row in comparable_paths if row["rounding_near_match_sample_count"]
        ]
        strong_paths = [row for row in comparable_paths if row["strong_path_evidence"]]
        left_unique_paths = sorted(set(left_paths) - set(right_paths))
        right_unique_paths = sorted(set(right_paths) - set(left_paths))
        left_family = family_of(left_source)
        right_family = family_of(right_source)
        if left_family and right_family and left_family == right_family:
            lineage_relation = "same_confirmed_provider_family"
        elif left_family and right_family:
            lineage_relation = "different_confirmed_provider_families"
        else:
            lineage_relation = "provider_relation_unconfirmed"

        if mismatched_paths:
            mismatch_samples = sum(row["mismatch_count"] for row in mismatched_paths)
            near_match_samples = sum(
                row["rounding_near_match_sample_count"] for row in mismatched_paths
            )
            observed_relation = (
                "rounding_near_match_candidate"
                if mismatch_samples == near_match_samples
                else "observed_value_differences"
            )
        elif (
            strong_paths
            and len(strong_paths) == len(shared_codes)
            and not ambiguous_codes
            and not left_unique_paths
            and not right_unique_paths
        ):
            observed_relation = "possible_duplicate_route_on_observed_scope"
        elif strong_paths:
            observed_relation = "partial_overlap_candidate"
        else:
            observed_relation = "insufficient_aligned_evidence"

        field_rows.sort(
            key=lambda row: (
                row["strong_path_evidence"],
                -row["mismatch_count"],
                row["informative_sample_count"],
                row["code"],
            ),
            reverse=True,
        )
        rows.append(
            {
                "left_source": left_source,
                "right_source": right_source,
                "left_provider_family": left_family,
                "right_provider_family": right_family,
                "left_repositories": (
                    repositories_for_source(left_source) if repositories_for_source else []
                ),
                "right_repositories": (
                    repositories_for_source(right_source) if repositories_for_source else []
                ),
                "lineage_relation": lineage_relation,
                "observed_relation": observed_relation,
                "left_field_path_count": len(left_paths),
                "right_field_path_count": len(right_paths),
                "shared_field_path_count": len(shared_codes),
                "ambiguous_field_path_count": len(ambiguous_codes),
                "comparable_field_path_count": len(comparable_paths),
                "strong_matching_field_path_count": len(strong_paths),
                "mismatched_field_path_count": len(mismatched_paths),
                "mismatch_sample_count": sum(row["mismatch_count"] for row in field_rows),
                "rounding_near_match_field_path_count": len(near_match_paths),
                "rounding_near_match_sample_count": sum(
                    row["rounding_near_match_sample_count"] for row in field_rows
                ),
                "context_skipped_sample_count": sum(
                    row["context_skipped_count"] for row in field_rows
                ),
                "left_unique_field_path_count": len(left_unique_paths),
                "right_unique_field_path_count": len(right_unique_paths),
                "field_paths": field_rows[:MAX_FIELD_PATHS_PER_PAIR],
                "ambiguous_field_paths": ambiguous_codes[:MAX_FIELD_PATHS_PER_PAIR],
                "field_path_details_truncated": max(0, len(field_rows) - MAX_FIELD_PATHS_PER_PAIR),
                "interpretation": (
                    "观测等价只表示所列完整路径与日期范围内的值一致；"
                    "不证明仓库关系、底层提供方相同或字段语义相同。"
                ),
            }
        )

    rows.sort(
        key=lambda row: (
            row["observed_relation"] == "possible_duplicate_route_on_observed_scope",
            row["strong_matching_field_path_count"],
            -row["mismatched_field_path_count"],
            row["shared_field_path_count"],
            row["left_source"],
            row["right_source"],
        ),
        reverse=True,
    )
    return {
        "status": "available",
        "source_pair_count": len(rows),
        "source_pair_details_retained": min(len(rows), MAX_SOURCE_PAIRS),
        "source_pair_details_truncated": max(0, len(rows) - MAX_SOURCE_PAIRS),
        "ambiguous_path_count": ambiguous_path_count,
        "thresholds": {
            "minimum_informative_samples_per_field_path": MIN_INFORMATIVE_PAIRS,
            "minimum_distinct_sample_key_dates_per_field_path": MIN_DISTINCT_DATES,
            "minimum_distinct_securities_per_field_path": MIN_DISTINCT_SECURITIES,
        },
        "automatic_collection_suppression": False,
        "rows": rows[:MAX_SOURCE_PAIRS],
        "interpretation": (
            "本节为接口/字段路径关系审阅队列。只有完成接口级覆盖核对、保留唯一字段并设置复验后，"
            "才能调整采集路由；本报告不自动停采。"
        ),
    }

"""Pure collision candidate measurements and deterministic candidate helpers.

This module deliberately has no registry, filesystem, network, cache, or report I/O.
The public collide.py façade re-exports these names for compatibility.
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Any, Dict, cast

try:
    from scripts import collision_rules as CR

    RULES_OK = True
except Exception:
    CR = cast(Any, None)
    RULES_OK = False

from scripts.collision_math import (
    fit_affine_feature as _fit_affine_feature,
    formula_feature as _formula_feature,
    formula_holdout as _formula_holdout,
    pearson as _pearson,
    r_squared as _r_squared,
    standard_deviation as _standard_deviation,
)

# 样本为 20 股（pool.json: fixed 15 + dynamic 5）。L1 命中率阈值 = HIT_RATE_L1(18)/20 = 0.9；
# 采用比率而非绝对 18/20，便于样本数变动时阈值自适应（符合四铁律精神）。
# 注：早期版本曾误记样本为 12 股，实际采集脚本 load_pool() 始终返回 20 只——采集无缩水。
HIT_RATE_L1_RATIO = (CR.HIT_RATE_L1 / 20.0) if RULES_OK else 0.9  # 0.9
MULTI_DAY_MIN = CR.MULTI_DAY_MIN if RULES_OK else 3
RATIO_CV_MAX = CR.RATIO_CV_MAX if RULES_OK else 1e-4
RATIO_STEPS_SIGNED = set()
if RULES_OK:
    for k in range(0, 5):
        RATIO_STEPS_SIGNED.add(10**k)
        RATIO_STEPS_SIGNED.add(10**-k)
else:
    RATIO_STEPS_SIGNED = {1, 10, 100, 1000, 10000, 0.1, 0.01, 0.001, 0.0001}

MIN_PAIR = 8  # 候选对最少总样本数
MIN_DAILY_L1 = CR.MIN_DAILY_SAMPLES_L1 if RULES_OK else 18
MIN_INFORMATIVE_DAILY_L1 = CR.MIN_INFORMATIVE_SAMPLES_L1 if RULES_OK else 5
MIN_DAILY_L4 = CR.MIN_DAILY_SAMPLES_L4 if RULES_OK else 8
MIN_CANDIDATE_PAIRS = 12  # 方法候选最少配对样本
MAX_METHOD_CANDIDATES = 500
MAX_TARGET_METHOD_CANDIDATES = 8
MAX_FIELD_FRONTIER_CANDIDATES = 1
MAX_FORMULA_CANDIDATES_PER_TARGET = 2
HUB_MAX = 6  # 单字段匹配超过此数 → 巧合，降级
CONST_MAX_DISTINCT = 1  # 不同值 ≤1 → 常量，跳过
ID_SUFFIX_HINTS = ("market", "code", "date", "name", "thscode", "ticker", "url", "host", "secid")


def to_num(v):
    """尽力把值转成 float；非数值返回 None。"""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip().replace(",", "")
        if s == "":
            return None
        try:
            return float(s)
        except ValueError:
            return None
    return None


def is_close(a: float, b: float) -> bool:
    """舍入感知容差：相对 1e-6，绝对值兜底 1e-9。"""
    if a == b:
        return True
    denom = max(1.0, abs(a), abs(b))
    return abs(a - b) <= 1e-6 * denom


def cv(xs):
    """变异系数 std/mean。"""
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    if m == 0:
        return 0.0
    var = sum((x - m) ** 2 for x in xs) / n
    return math.sqrt(var) / abs(m)


def classify(store):
    """为每个字段补充 type / n_distinct / is_constant / is_identifier。"""
    for fid, info in store.items():
        vals = [
            v for v in info["vals"].values() if v is not None and not isinstance(v, (dict, list))
        ]
        nums = [to_num(v) for v in vals]
        nums = [n for n in nums if n is not None]
        n_total = len(vals)
        n_num = len(nums)
        distinct = len(set(vals))
        info["n"] = n_total
        info["n_num"] = n_num
        info["n_distinct"] = distinct
        info["is_constant"] = distinct <= CONST_MAX_DISTINCT and n_total > 0
        low = fid.lower()
        info["is_identifier"] = any(h in low for h in ID_SUFFIX_HINTS)
        if n_total > 0 and n_num >= 0.8 * n_total:
            info["type"] = "num"
        elif distinct <= 30 and n_total > 0:
            info["type"] = "enum"
        else:
            info["type"] = "str"
        # 值域（用于快速预筛）
        if nums:
            info["vmin"] = min(nums)
            info["vmax"] = max(nums)
        else:
            info["vmin"] = None
            info["vmax"] = None


def _eligible_for_l1(info, key):
    sample_meta = info.get("sample_meta", {}).get(key, {})
    return sample_meta.get("phase") in {"closed", "calendar"}


def _median(values):
    ordered = sorted(values)
    if not ordered:
        return None
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def _informative_pair(a, b, left_num, right_num):
    """Ignore jointly missing and 0/0 pairs when exact matches could be coincidental."""
    left_missing = a is None or (isinstance(a, str) and not a.strip())
    right_missing = b is None or (isinstance(b, str) and not b.strip())
    if left_missing and right_missing:
        return False
    if left_num == 0 and right_num == 0:
        return False
    return True


def _ratio_step(value):
    for step in RATIO_STEPS_SIGNED:
        if step != 1 and math.isclose(value, step, rel_tol=0.005, abs_tol=1e-9):
            return step
    return None


def _temporal_candidate(common, left_values, right_values):
    per_code = defaultdict(list)
    for key in common:
        code, day_key = key
        if not str(day_key).startswith("T:"):
            continue
        left_num, right_num = to_num(left_values[key]), to_num(right_values[key])
        if left_num is not None and right_num is not None:
            per_code[code].append((day_key, left_num, right_num))
    correlations = []
    used_days = set()
    for code, rows in per_code.items():
        rows.sort(key=lambda item: item[0])
        if len(rows) < 3:
            continue
        value = _pearson([row[1] for row in rows], [row[2] for row in rows])
        if value is not None:
            correlations.append((code, value, [row[0] for row in rows]))
            used_days.update(row[0] for row in rows)
    if len(correlations) < 3:
        return None
    signs = [1 if value > 0 else -1 for _, value, _ in correlations if value != 0]
    if not signs:
        return None
    dominant = 1 if sum(signs) >= 0 else -1
    sign_consistency = sum(sign == dominant for sign in signs) / len(signs)
    median_abs = _median([abs(value) for _, value, _ in correlations]) or 0.0
    if median_abs < 0.7 or sign_consistency < 0.8:
        return None
    return {
        "method": "per_stock_time_series",
        "median_abs_pearson": round(median_abs, 4),
        "sign_consistency": round(sign_consistency, 4),
        "stocks": len(correlations),
        "stock_correlations": [
            {"code": code, "pearson": round(value, 4), "dates": dates}
            for code, value, dates in correlations[:20]
        ],
        "sample_dates": sorted(used_days),
    }


def formula_candidates_for_target(left_id, store, input_candidates):
    """Generate conservative two-input formula clues with stock-level holdout."""
    left = store.get(left_id)
    if not isinstance(left, dict) or left.get("type") != "num":
        return [], {"tested": 0, "validated": 0}

    input_ids = []
    for candidate in input_candidates:
        right_id = candidate.get("right")
        right = store.get(right_id)
        if (
            isinstance(right_id, str)
            and right_id != left_id
            and isinstance(right, dict)
            and right.get("type") == "num"
            and right_id not in input_ids
        ):
            input_ids.append(right_id)
        if len(input_ids) >= MAX_TARGET_METHOD_CANDIDATES:
            break

    operators = (
        ("product", "×"),
        ("ratio_left_right", "÷"),
        ("ratio_right_left", "÷"),
        ("sum", "+"),
        ("difference", "−"),
    )
    tested = 0
    accepted = []
    for first_index, first_id in enumerate(input_ids):
        first = store[first_id]
        for second_id in input_ids[first_index + 1 :]:
            second = store[second_id]
            common = set(left["vals"]) & set(first["vals"]) & set(second["vals"])
            rows = []
            for key in sorted(common, key=lambda item: (item[1], item[0])):
                if not str(key[1]).startswith("T:"):
                    continue
                if not all(_eligible_for_l1(info, key) for info in (left, first, second)):
                    continue
                values = tuple(to_num(info["vals"][key]) for info in (left, first, second))
                if any(value is None for value in values):
                    continue
                rows.append((key, values[0], values[1], values[2]))
            codes = {row[0][0] for row in rows}
            days = {row[0][1] for row in rows}
            if len(rows) < 36 or len(codes) < 10 or len(days) < 3:
                continue

            training = [row for row in rows if not _formula_holdout(row[0][0])]
            validation = [row for row in rows if _formula_holdout(row[0][0])]
            training_codes = {row[0][0] for row in training}
            validation_codes = {row[0][0] for row in validation}
            if (
                len(training) < 24
                or len(validation) < 8
                or len(training_codes) < 8
                or len(validation_codes) < 3
            ):
                continue

            for operator, symbol in operators:
                train_features = [_formula_feature(operator, row[2], row[3]) for row in training]
                validation_features = [
                    _formula_feature(operator, row[2], row[3]) for row in validation
                ]
                if any(value is None for value in train_features + validation_features):
                    continue
                tested += 1
                train_target = [row[1] for row in training]
                validation_target = [row[1] for row in validation]
                fit = _fit_affine_feature(train_features, train_target)
                if fit is None:
                    continue
                slope, intercept = fit
                predicted = [slope * value + intercept for value in validation_features]
                validation_r2 = _r_squared(validation_target, predicted)
                target_scale = _standard_deviation(train_target)
                if not target_scale or validation_r2 is None:
                    continue
                normalized_rmse = (
                    math.sqrt(
                        sum(
                            (actual - estimate) ** 2
                            for actual, estimate in zip(validation_target, predicted)
                        )
                        / len(validation_target)
                    )
                    / target_scale
                )

                baseline_scores = []
                for column in (2, 3):
                    single_train = [row[column] for row in training]
                    single_validation = [row[column] for row in validation]
                    single_fit = _fit_affine_feature(single_train, train_target)
                    if single_fit is None:
                        continue
                    single_slope, single_intercept = single_fit
                    single_predicted = [
                        single_slope * value + single_intercept for value in single_validation
                    ]
                    score = _r_squared(validation_target, single_predicted)
                    if score is not None:
                        baseline_scores.append(score)
                baseline_r2 = max(baseline_scores, default=-1.0)
                improvement = validation_r2 - baseline_r2
                if validation_r2 < 0.985 or normalized_rmse > 0.05 or improvement < 0.05:
                    continue

                formula = (
                    f"{left_id} ≈ {slope:.8g} × ({first_id} {symbol} {second_id}) "
                    f"+ {intercept:.8g}"
                )
                accepted.append(
                    {
                        "left": left_id,
                        "right_inputs": [first_id, second_id],
                        "operator": operator,
                        "formula": formula,
                        "training_samples": len(training),
                        "validation_samples": len(validation),
                        "validation_stocks": len(validation_codes),
                        "validation_dates": sorted({row[0][1] for row in validation}),
                        "validation_r2": round(validation_r2, 6),
                        "normalized_rmse": round(normalized_rmse, 6),
                        "best_single_input_r2": round(baseline_r2, 6),
                        "improvement_over_single_input": round(improvement, 6),
                        "evidence_sources": sorted(
                            {
                                str(left.get("src") or ""),
                                str(first.get("src") or ""),
                                str(second.get("src") or ""),
                            }
                            - {""}
                        ),
                        "adjudication_status": "candidate_only",
                    }
                )

    accepted.sort(
        key=lambda item: (
            item["validation_r2"],
            item["improvement_over_single_input"],
            item["validation_samples"],
            item["formula"],
        ),
        reverse=True,
    )
    unique = []
    seen = set()
    for candidate in accepted:
        key = (candidate["left"], tuple(candidate["right_inputs"]), candidate["operator"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
        if len(unique) >= MAX_FORMULA_CANDIDATES_PER_TARGET:
            break
    return unique, {"tested": tested, "validated": len(accepted)}


def discriminating_sample_for_target(left_id, store, input_candidates):
    """Find a stock whose held-out candidate predictions disagree most."""
    left = store.get(left_id)
    if not isinstance(left, dict):
        return None
    candidate_ids = []
    for candidate in input_candidates:
        right_id = candidate.get("right")
        if right_id in store and right_id != left_id and right_id not in candidate_ids:
            candidate_ids.append(right_id)
        if len(candidate_ids) >= MAX_TARGET_METHOD_CANDIDATES:
            break
    if len(candidate_ids) < 2:
        return None

    codes = set()
    for right_id in candidate_ids:
        right = store[right_id]
        codes.update(
            key[0] for key in set(left["vals"]) & set(right["vals"]) if str(key[1]).startswith("T:")
        )

    suggestions = []
    for code in sorted(codes):
        predictions_by_key = defaultdict(list)
        training_target_values = []
        usable_candidates = 0
        usable_candidate_ids = []
        for right_id in candidate_ids:
            right = store[right_id]
            common = set(left["vals"]) & set(right["vals"])
            numeric = []
            for key in common:
                if not str(key[1]).startswith("T:"):
                    continue
                if not all(_eligible_for_l1(info, key) for info in (left, right)):
                    continue
                left_num = to_num(left["vals"][key])
                right_num = to_num(right["vals"][key])
                if left_num is not None and right_num is not None:
                    numeric.append((key, left_num, right_num))
            train = [row for row in numeric if row[0][0] != code]
            held_out = [row for row in numeric if row[0][0] == code]
            if len(train) < MIN_CANDIDATE_PAIRS or not held_out:
                continue
            fit = _fit_affine_feature([row[2] for row in train], [row[1] for row in train])
            if fit is None:
                continue
            usable_candidates += 1
            usable_candidate_ids.append(right_id)
            slope, intercept = fit
            training_target_values.extend(row[1] for row in train)
            for key, _, right_value in held_out:
                predictions_by_key[key].append((right_id, slope * right_value + intercept))
        if usable_candidates < 2 or not training_target_values:
            continue

        scale = max(
            _standard_deviation(training_target_values),
            abs(_median(training_target_values) or 0.0) * 0.01,
            1e-12,
        )
        spreads = []
        for key, predictions in predictions_by_key.items():
            if len(predictions) < 2:
                continue
            values = [prediction for _, prediction in predictions]
            spreads.append((key[1], (max(values) - min(values)) / scale))
        if len({day for day, _ in spreads}) < 2:
            continue
        score = _median([spread for _, spread in spreads]) or 0.0
        suggestions.append(
            {
                "stock_code": code,
                "candidate_count": usable_candidates,
                "out_of_sample_dates": sorted({day for day, _ in spreads}),
                "normalized_prediction_spread": round(score, 6),
                "candidate_fields": usable_candidate_ids,
            }
        )

    if not suggestions:
        return {"status": "no_shared_stock_holdout", "candidate_fields": candidate_ids}
    suggestions.sort(
        key=lambda item: (
            item["normalized_prediction_spread"],
            len(item["out_of_sample_dates"]),
            item["stock_code"],
        ),
        reverse=True,
    )
    best = suggestions[0]
    if best["normalized_prediction_spread"] < 0.02:
        return {
            "status": "candidates_converge_on_existing_samples",
            "candidate_fields": candidate_ids,
            "best_observed_spread": best["normalized_prediction_spread"],
        }
    return {"status": "prioritize_recheck", **best}


__all__ = [
    "CR",
    "RULES_OK",
    "CONST_MAX_DISTINCT",
    "HIT_RATE_L1_RATIO",
    "HUB_MAX",
    "ID_SUFFIX_HINTS",
    "MAX_FIELD_FRONTIER_CANDIDATES",
    "MAX_FORMULA_CANDIDATES_PER_TARGET",
    "MAX_METHOD_CANDIDATES",
    "MAX_TARGET_METHOD_CANDIDATES",
    "MIN_CANDIDATE_PAIRS",
    "MIN_DAILY_L1",
    "MIN_DAILY_L4",
    "MIN_INFORMATIVE_DAILY_L1",
    "MIN_PAIR",
    "MULTI_DAY_MIN",
    "RATIO_CV_MAX",
    "RATIO_STEPS_SIGNED",
    "_eligible_for_l1",
    "_informative_pair",
    "_median",
    "_ratio_step",
    "_temporal_candidate",
    "classify",
    "cv",
    "discriminating_sample_for_target",
    "formula_candidates_for_target",
    "is_close",
    "to_num",
]

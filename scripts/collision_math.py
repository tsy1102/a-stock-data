"""Pure numerical helpers used by the collision candidate methods."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence


def pearson(x_values: Sequence[float], y_values: Sequence[float]) -> float | None:
    if len(x_values) != len(y_values) or len(x_values) < 3:
        return None
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)
    x_delta = [value - x_mean for value in x_values]
    y_delta = [value - y_mean for value in y_values]
    x_sum = sum(value * value for value in x_delta)
    y_sum = sum(value * value for value in y_delta)
    if x_sum <= 0 or y_sum <= 0:
        return None
    return sum(a * b for a, b in zip(x_delta, y_delta)) / math.sqrt(x_sum * y_sum)


def ranks(values: Sequence[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    result = [0.0] * len(values)
    offset = 0
    while offset < len(order):
        end = offset + 1
        while end < len(order) and values[order[end]] == values[order[offset]]:
            end += 1
        rank = ((offset + 1) + end) / 2.0
        for position in range(offset, end):
            result[order[position]] = rank
        offset = end
    return result


def correlation_metrics(
    x_values: Sequence[float], y_values: Sequence[float]
) -> dict[str, float | bool | None] | None:
    pearson_value = pearson(x_values, y_values)
    if pearson_value is None:
        return None
    spearman = pearson(ranks(x_values), ranks(y_values))
    leave_one_out = []
    if len(x_values) >= 5:
        count = len(x_values)
        x_mean = sum(x_values) / count
        y_mean = sum(y_values) / count
        x_delta = [value - x_mean for value in x_values]
        y_delta = [value - y_mean for value in y_values]
        covariance = sum(x * y for x, y in zip(x_delta, y_delta))
        x_variance = sum(x * x for x in x_delta)
        y_variance = sum(y * y for y in y_delta)
        multiplier = count / (count - 1)
        for x, y in zip(x_delta, y_delta):
            reduced_covariance = covariance - multiplier * x * y
            reduced_x_variance = x_variance - multiplier * x * x
            reduced_y_variance = y_variance - multiplier * y * y
            if reduced_x_variance <= 0 or reduced_y_variance <= 0:
                continue
            leave_one_out.append(
                reduced_covariance / math.sqrt(reduced_x_variance * reduced_y_variance)
            )
    sign_stable = (
        len(leave_one_out) == len(x_values)
        and pearson_value != 0
        and all(value != 0 and (value > 0) == (pearson_value > 0) for value in leave_one_out)
    )
    return {
        "pearson": pearson_value,
        "spearman": spearman,
        "leave_one_out_sign_stable": sign_stable,
        "leave_one_out_min": min(leave_one_out) if leave_one_out else None,
        "leave_one_out_max": max(leave_one_out) if leave_one_out else None,
    }


def fit_affine_feature(
    feature_values: Sequence[float], target_values: Sequence[float]
) -> tuple[float, float] | None:
    if len(feature_values) != len(target_values) or len(feature_values) < 2:
        return None
    feature_mean = sum(feature_values) / len(feature_values)
    target_mean = sum(target_values) / len(target_values)
    feature_variance = sum((value - feature_mean) ** 2 for value in feature_values)
    if feature_variance <= 1e-18:
        return None
    slope = (
        sum(
            (feature - feature_mean) * (target - target_mean)
            for feature, target in zip(feature_values, target_values)
        )
        / feature_variance
    )
    intercept = target_mean - slope * feature_mean
    if not math.isfinite(slope) or not math.isfinite(intercept):
        return None
    return slope, intercept


def r_squared(actual: Sequence[float], predicted: Sequence[float]) -> float | None:
    if len(actual) != len(predicted) or not actual:
        return None
    mean_value = sum(actual) / len(actual)
    total = sum((value - mean_value) ** 2 for value in actual)
    if total <= 1e-18:
        return None
    residual = sum((value - estimate) ** 2 for value, estimate in zip(actual, predicted))
    score = 1.0 - residual / total
    return score if math.isfinite(score) else None


def standard_deviation(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    mean_value = sum(values) / len(values)
    variance = sum((value - mean_value) ** 2 for value in values) / len(values)
    return math.sqrt(max(0.0, variance))


def formula_feature(operator: str, left_value: float, right_value: float) -> float | None:
    if operator == "product":
        value = left_value * right_value
    elif operator == "ratio_left_right":
        if abs(right_value) <= 1e-12 * max(1.0, abs(left_value)):
            return None
        value = left_value / right_value
    elif operator == "ratio_right_left":
        if abs(left_value) <= 1e-12 * max(1.0, abs(right_value)):
            return None
        value = right_value / left_value
    elif operator == "sum":
        value = left_value + right_value
    elif operator == "difference":
        value = left_value - right_value
    else:
        return None
    return value if math.isfinite(value) else None


def formula_holdout(code: str) -> bool:
    digest = hashlib.sha256(str(code).encode("utf-8")).digest()
    return int.from_bytes(digest[:2], "big") % 5 == 0

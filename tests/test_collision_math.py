import math

from scripts import collision_math, collide


def test_correlation_metrics_require_spread_and_preserve_rank_ties():
    assert collision_math.pearson([1.0, 2.0], [2.0, 4.0]) is None
    assert collision_math.ranks([10.0, 10.0, 20.0, 30.0]) == [1.5, 1.5, 3.0, 4.0]

    metrics = collision_math.correlation_metrics(
        [1.0, 2.0, 3.0, 4.0, 5.0], [2.0, 4.0, 6.0, 8.0, 10.0]
    )

    assert metrics is not None
    assert metrics["pearson"] == 1.0
    assert metrics["spearman"] == 1.0
    assert metrics["leave_one_out_sign_stable"] is True


def test_affine_fit_and_r_squared_keep_constant_target_ineligible():
    fit = collision_math.fit_affine_feature([1.0, 2.0, 3.0], [3.0, 5.0, 7.0])

    assert fit == (2.0, 1.0)
    assert collision_math.r_squared([3.0, 5.0, 7.0], [3.0, 5.0, 7.0]) == 1.0
    assert collision_math.fit_affine_feature([1.0, 1.0], [2.0, 3.0]) is None
    assert collision_math.r_squared([2.0, 2.0], [2.0, 2.0]) is None


def test_formula_features_reject_small_denominators_and_non_finite_results():
    assert collision_math.formula_feature("sum", 2.0, 3.0) == 5.0
    assert collision_math.formula_feature("ratio_left_right", 2.0, 0.0) is None
    assert collision_math.formula_feature("product", 1e308, 1e308) is None
    assert collision_math.formula_feature("unknown", 2.0, 3.0) is None


def test_formula_holdout_is_stable_and_compatibility_aliases_remain_available():
    assert collision_math.formula_holdout("000001") == collision_math.formula_holdout("000001")
    assert collide._pearson is collision_math.pearson
    assert collide._correlation_metrics is collision_math.correlation_metrics
    assert collide._formula_feature is collision_math.formula_feature
    assert math.isclose(collision_math.standard_deviation([1.0, 2.0, 3.0]), math.sqrt(2.0 / 3.0))

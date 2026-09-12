"""tests/test_sc_ta_core.py — sc_ta_core 原语库验证。

两类断言：
  1) 手算基准：对小型确定性序列逐函数验证（含空序列/NaN 边界）。
  2) 交叉一致性：用 sc_ta_core 原语重建 MACD/RSI/BOLL/KDJ，与 sc_technical 现有
     calc_* 实现比较（同一输入应得同量级结果；BOLL 因同为 ddof=0 应近似精确）。
"""
import math

import numpy as np
import pandas as pd
import pytest

from stock_common.sc_ta_core import (
    REF, DIFF, SUM, STD, HHV, LLV, HHVBARS, LLVBARS, AVEDEV,
    COUNT, EVERY, EXIST, SMA, EMA, WMA, DMA, SLOPE, FORCAST,
    BARSLAST, BARSLASTCOUNT, BARSSINCEN, CROSS, LONGCROSS, VALUEWHEN,
    FILTER, BETWEEN, TOPRANGE, LOWRANGE, CONST, IF, MAX, MIN,
    ABS, LN, POW, SQRT,
)
from stock_common.sc_technical import calc_macd, calc_rsi, calc_bollinger, calc_kdj


# ───────────────────────────── 1) 手算基准 ─────────────────────────────

def test_ref():
    s = pd.Series([1, 2, 3, 4, 5])
    out = REF(s, 1)
    assert out.tolist()[1:] == [1, 2, 3, 4]
    assert math.isnan(out.iloc[0])


def test_sum_rolling():
    s = pd.Series([1, 2, 3, 4, 5])
    assert SUM(s, 3).tolist() == [1, 3, 6, 9, 12]


def test_hhv_llv():
    s = pd.Series([1, 2, 3, 4, 5])
    assert HHV(s, 3).tolist() == [1, 2, 3, 4, 5]
    assert LLV(s, 3).tolist() == [1, 1, 1, 2, 3]


def test_sma_recursion():
    s = pd.Series([1, 2, 3, 4, 5])
    out = SMA(s, 3, 1)
    # (1*2 + 2*1)/3 = 1.333...; (1*3 + 2*1.333)/3 = 1.889...; ...
    np.testing.assert_allclose(
        out.tolist(),
        [1.0, 4 / 3, 17 / 9, 70 / 27, 275 / 81],
        rtol=1e-4,
    )


def test_dma_recursion():
    s = pd.Series([1, 2, 3, 4, 5])
    out = DMA(s, 0.3)
    np.testing.assert_allclose(
        out.tolist(), [1.0, 1.3, 1.81, 2.467, 3.2269], rtol=1e-4
    )


def test_cross():
    a = pd.Series([1, 2, 1, 3])
    b = pd.Series([2, 1, 2, 1])
    assert CROSS(a, b).tolist() == [False, True, False, True]


def test_barslast():
    x = pd.Series([False, True, False, False, True])
    out = BARSLAST(x)
    assert math.isnan(out.iloc[0])
    assert out.tolist()[1:] == [0.0, 1.0, 2.0, 0.0]


def test_between():
    x = pd.Series([1, 5, 10])
    assert BETWEEN(x, 3, 7).tolist() == [False, True, False]


def test_count_every_exist():
    x = pd.Series([True, False, True, True])
    assert COUNT(x, 3).tolist() == [1, 1, 2, 2]
    assert EVERY(x, 3).tolist() == [True, False, False, False]
    assert EXIST(x, 3).tolist() == [True, True, True, True]


def test_std_ddof0():
    s = pd.Series([2, 4, 4, 4, 5])
    # mean 3.8, pop var = 0.96, std = sqrt(0.96) = 0.979796
    np.testing.assert_allclose(STD(s, 5).iloc[-1], 0.979796, rtol=1e-4)


def test_hhvbars_llvbars():
    s = pd.Series([3, 1, 4, 1, 5])
    # HHV(3): i0 w=[3]->0; i1 w=[3,1]->1; i2 w=[3,1,4]->0; i3 w=[1,4,1]->1; i4 w=[4,1,5]->0
    np.testing.assert_allclose(HHVBARS(s, 3).tolist(), [0, 1, 0, 1, 0], rtol=0)


def test_valuewhen_forwardfill():
    a = pd.Series([False, True, False, True, False])
    b = pd.Series([0, 10, 0, 20, 0])
    np.testing.assert_array_equal(
        VALUEWHEN(a, b).to_numpy(), [np.nan, 10, 10, 20, 20]
    )


def test_toprange_lowrange():
    s = pd.Series([1.0, 2.0, 4.0, 3.0])
    tr = TOPRANGE(s)
    # cummax=4, cummin=1; at idx3: (3-1)/(4-1)*100=66.67
    np.testing.assert_allclose(tr.iloc[-1], 66.6667, rtol=1e-3)
    np.testing.assert_allclose(LOWRANGE(s).iloc[-1], 33.3333, rtol=1e-3)


def test_nan_boundary_no_crash():
    s = pd.Series([np.nan, 1.0, np.nan, 2.0])
    # 不应抛异常
    assert len(SMA(s, 2, 1)) == 4
    assert len(DMA(s, 0.5)) == 4
    assert len(EMA(s, 3)) == 4


# ───────────────────────────── 2) 交叉一致性（与 sc_technical） ─────────────────────────────

def _seed_close(n=60, start=100.0, step=1.3, seed=7):
    rng = np.random.RandomState(seed)
    return start + np.cumsum(rng.randn(n) * step)


def test_macd_cross_consistency():
    close = _seed_close(80)
    s = pd.Series(close)
    dif = EMA(s, 12) - EMA(s, 26)
    dea = EMA(dif, 9)
    hist = 2 * (dif - dea)
    ref = calc_macd(close.tolist())
    np.testing.assert_allclose(dif.iloc[-1], ref["dif"], atol=1e-2)
    np.testing.assert_allclose(dea.iloc[-1], ref["dea"], atol=1e-2)
    np.testing.assert_allclose(hist.iloc[-1], ref["macd"], atol=1e-2)


def test_boll_cross_consistency():
    close = _seed_close(60)
    s = pd.Series(close)
    mid = s.rolling(20).mean()
    std = STD(s, 20)
    upper = mid + 2 * std
    lower = mid - 2 * std
    ref = calc_bollinger(close.tolist(), period=20, std_dev=2.0)
    # 同为 ddof=0 总体标准差 + 末 20 窗口；calc_bollinger 将 mid 四舍五入到 2 位小数，故容差放宽到 1e-2
    np.testing.assert_allclose(mid.iloc[-1], ref["mid"], atol=1e-2)
    np.testing.assert_allclose(upper.iloc[-1], ref["upper"], atol=1e-2)
    np.testing.assert_allclose(lower.iloc[-1], ref["lower"], atol=1e-2)


def test_rsi_cross_consistency():
    close = _seed_close(60)
    s = pd.Series(close)
    chg = DIFF(s, 1)
    gains = chg.clip(lower=0)
    losses = (-chg).clip(lower=0)
    avg_gain = SMA(gains, 14, 1)  # Wilder 平滑 = SMA(.,14,1)
    avg_loss = SMA(losses, 14, 1)
    rsi = 100 - 100 / (1 + avg_gain / avg_loss.replace(0, np.nan))
    ref = calc_rsi(close.tolist(), period=14)
    np.testing.assert_allclose(rsi.iloc[-1], ref["rsi14"], atol=1.0)


def test_kdj_cross_consistency():
    rng = np.random.RandomState(3)
    n = 60
    close = 100 + np.cumsum(rng.randn(n) * 1.2)
    high = close + np.abs(rng.randn(n)) * 0.5
    low = close - np.abs(rng.randn(n)) * 0.5
    c, h, l = pd.Series(close), pd.Series(high), pd.Series(low)
    hh = HHV(h, 9)
    ll = LLV(l, 9)
    rsv = (c - ll) / (hh - ll).replace(0, np.nan) * 100
    rsv = rsv.fillna(50.0)
    k = SMA(rsv, 3, 1)
    d = SMA(k, 3, 1)
    j = 3 * k - 2 * d
    ref = calc_kdj(close.tolist(), high.tolist(), low.tolist())
    # K/D 初值差异（50 vs 首值）随递归收敛；断言同量级
    np.testing.assert_allclose(k.iloc[-1], ref["k"], atol=0.5)
    np.testing.assert_allclose(d.iloc[-1], ref["d"], atol=0.5)
    np.testing.assert_allclose(j.iloc[-1], ref["j"], atol=1.0)

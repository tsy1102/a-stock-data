"""sc_ta_core.py — 通达信/同花顺公式语言原语库（0 级/1 级核心函数）

来源说明（clean-room 重新实现）：
    参考 mpquant/MyTT（https://github.com/mpquant/MyTT）的指标公式原语设计，
    以独立方式基于 numpy/pandas 重新实现，零新增第三方依赖。MyTT 将通达信/同花顺/文华麦语言
    指标公式最简移植到 Python，核心是 一组向量化原语。本项目在此之上构建"用公式写指标"的能力，
    与现有 sc_technical.py 的平铺式 calc_* 实现**并行存在、不直接替换**。

设计约定：
    - 全部函数以 pandas.Series 为输入、pandas.Series 为输出（与 MyTT 一致），支持 NaN。
    - 纯 numpy/pandas 向量化；仅 SMA/DMA 因递归定义使用逐元素迭代（与 MyTT 一致，标 "除外"）。
    - 语义对齐通达信公式：SMA(X,N,M) 递归权重 M；DMA(X,A) 递归系数 A；STD 用总体标准差(ddof=0)。
    - 本模块为独立原语层，**不引入任何生产取数逻辑**；sc_technical.py 现有指标不受影响。

验证：tests/test_sc_ta_core.py 含手算基准 + 与 sc_technical 现有 MACD/RSI/BOLL/KDJ 的交叉一致性断言。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _s(x) -> pd.Series:
    return x if isinstance(x, pd.Series) else pd.Series(x, dtype="float64")


# ───────────────────────────── 0 级：序列引用 / 差分 / 统计 ─────────────────────────────

def REF(X, N: int = 1) -> pd.Series:
    """引用 N 周期前的值（通达信 REF）。"""
    return _s(X).shift(N)


def DIFF(X, N: int = 1) -> pd.Series:
    """差分（通达信 DIFF）。"""
    return _s(X).diff(N)


def SUM(X, N: int) -> pd.Series:
    """N 周期求和（通达信 SUM）。"""
    return _s(X).rolling(N, min_periods=1).sum()


def STD(X, N: int) -> pd.Series:
    """N 周期总体标准差（通达信 STD，ddof=0）。"""
    return _s(X).rolling(N, min_periods=1).std(ddof=0)


def HHV(X, N: int) -> pd.Series:
    """N 周期最高（通达信 HHV）。"""
    return _s(X).rolling(N, min_periods=1).max()


def LLV(X, N: int) -> pd.Series:
    """N 周期最低（通达信 LLV）。"""
    return _s(X).rolling(N, min_periods=1).min()


def HHVBARS(X, N: int) -> pd.Series:
    """N 周期内距最高点的距离（周期数）；窗口内最高在最后则为 0。

    距离 = (实际窗口长度-1) - 窗口内最高值位置。早期窗口长度小于 N 时按实际长度计算，
    故首根 K 线（仅自身）距离为 0。
    """
    s = _s(X)
    return s.rolling(N, min_periods=1).apply(
        lambda x: (len(x) - 1) - int(np.argmax(x)), raw=True
    )


def LLVBARS(X, N: int) -> pd.Series:
    """N 周期内距最低点的距离（周期数）。"""
    s = _s(X)
    return s.rolling(N, min_periods=1).apply(
        lambda x: (len(x) - 1) - int(np.argmin(x)), raw=True
    )


def AVEDEV(X, N: int) -> pd.Series:
    """N 周期平均绝对偏差（通达信 AVEDEV）。"""
    s = _s(X)
    return s.rolling(N, min_periods=1).apply(
        lambda x: np.mean(np.abs(x - np.mean(x))), raw=True
    )


def COUNT(X, N: int) -> pd.Series:
    """N 周期内条件为真（非零）的次数（通达信 COUNT）。"""
    return _s(X).astype(bool).rolling(N, min_periods=1).sum().astype(int)


def EVERY(X, N: int) -> pd.Series:
    """N 周期内条件是否全为真（通达信 EVERY）。"""
    return _s(X).astype(bool).rolling(N, min_periods=1).apply(lambda x: bool(np.all(x)), raw=True).astype(bool)


def EXIST(X, N: int) -> pd.Series:
    """N 周期内条件是否曾为真（通达信 EXIST）。"""
    return _s(X).astype(bool).rolling(N, min_periods=1).apply(lambda x: bool(np.any(x)), raw=True).astype(bool)


# ───────────────────────────── 1 级：移动平均 / 回归 / 时序 ─────────────────────────────

def SMA(X, N: int, M: int) -> pd.Series:
    """通达信 SMA(X,N,M)：SMA = (M*X + (N-M)*SMA[-1])/N，初值 SMA[0]=X[0]。

    注意：与指数平滑 EMA 不同，SMA 是带权重 M 的递归移动平均（通达信 MACD 的 DEA 即用此）。
    """
    s = _s(X)
    out = np.full(len(s), np.nan, dtype="float64")
    prev = np.nan
    for i in range(len(s)):
        v = s.iloc[i]
        if np.isnan(v):
            out[i] = prev
            continue
        prev = v if np.isnan(prev) else (M * v + (N - M) * prev) / N
        out[i] = prev
    return pd.Series(out, index=s.index)


def EMA(X, N: int) -> pd.Series:
    """指数移动平均（通达信 EMA，adjust=False 递推）。"""
    return _s(X).ewm(span=N, adjust=False).mean()


def WMA(X, N: int) -> pd.Series:
    """加权移动平均（通达信 WMA，权重 1..N 对齐窗口旧→新）。"""
    s = _s(X)
    w = np.arange(1, N + 1, dtype="float64")
    return s.rolling(N, min_periods=1).apply(
        lambda x: np.sum(x * w[: len(x)]) / np.sum(w[: len(x)]), raw=True
    )


def DMA(X, A: float) -> pd.Series:
    """通达信 DMA(X,A)：DMA = A*X + (1-A)*DMA[-1]，初值 DMA[0]=X[0]；A∈(0,1)。"""
    s = _s(X)
    out = np.full(len(s), np.nan, dtype="float64")
    prev = np.nan
    for i in range(len(s)):
        v = s.iloc[i]
        if np.isnan(v):
            out[i] = prev
            continue
        prev = v if np.isnan(prev) else A * v + (1 - A) * prev
        out[i] = prev
    return pd.Series(out, index=s.index)


def SLOPE(X, N: int) -> pd.Series:
    """N 周期线性回归斜率（通达信 SLOPE）。"""
    s = _s(X)
    return s.rolling(N, min_periods=2).apply(
        lambda x: np.polyfit(np.arange(len(x)), x, 1)[0], raw=True
    )


def FORCAST(X, N: int) -> pd.Series:
    """N 周期线性回归预测值（通达信 FORCAST，末点拟合值）。"""
    s = _s(X)
    return s.rolling(N, min_periods=2).apply(
        lambda x: np.polyval(np.polyfit(np.arange(len(x)), x, 1), len(x) - 1), raw=True
    )


def BARSLAST(X) -> pd.Series:
    """上一次条件为真到当前的周期数（当前为真=0；从未为真=NaN）。"""
    s = _s(X).astype(bool)
    out = np.full(len(s), np.nan, dtype="float64")
    last_true = -1
    for i in range(len(s)):
        if s.iloc[i]:
            out[i] = 0.0
            last_true = i
        elif last_true >= 0:
            out[i] = float(i - last_true)
    return pd.Series(out, index=s.index)


def BARSLASTCOUNT(X) -> pd.Series:
    """连续为真的周期数（断则归零）。"""
    s = _s(X).astype(bool)
    out = np.zeros(len(s), dtype="int64")
    c = 0
    for i in range(len(s)):
        c = c + 1 if s.iloc[i] else 0
        out[i] = c
    return pd.Series(out, index=s.index)


def BARSSINCEN(X, N: int) -> pd.Series:
    """最近 N 周期内 X 首次为真的位置（距当前的周期数）；N 内从未为真返回 N。"""
    s = _s(X).astype(bool)
    out = np.full(len(s), np.nan, dtype="float64")
    for i in range(len(s)):
        lo = max(0, i - N + 1)
        pos = np.where(s.iloc[lo : i + 1].to_numpy())[0]
        if pos.size == 0:
            out[i] = float(min(N, i - lo + 1))
        else:
            out[i] = float(i - (lo + int(pos[0])))
    return pd.Series(out, index=s.index)


def CROSS(A, B) -> pd.Series:
    """A 上穿 B（当前 A>B 且前一周期 A<=B）。"""
    a, b = _s(A), _s(B)
    return (a > b) & (a.shift(1) <= b.shift(1))


def LONGCROSS(A, B, N: int) -> pd.Series:
    """A 上穿 B 且当前 A>B，且上穿发生在最近 N 周期内。"""
    a, b = _s(A), _s(B)
    cross = (a > b) & (a.shift(1) <= b.shift(1))
    return (a > b) & cross.rolling(N, min_periods=1).apply(lambda x: bool(np.any(x)), raw=True)


def VALUEWHEN(A, B) -> pd.Series:
    """A 上一次为真时 B 的值，向前填充（通达信 VALUEWHEN）。"""
    a, b = _s(A).astype(bool), _s(B)
    out = np.full(len(b), np.nan, dtype="float64")
    last = np.nan
    for i in range(len(b)):
        if a.iloc[i]:
            last = b.iloc[i]
        out[i] = last
    return pd.Series(out, index=b.index)


def FILTER(X, N: int) -> pd.Series:
    """X 为真时，若前 N 周期内已触发过则抑制（通达信 FILTER）。"""
    s = _s(X).astype(bool)
    out = np.zeros(len(s), dtype=bool)
    last_true = -N - 1
    for i in range(len(s)):
        if s.iloc[i] and (i - last_true > N):
            out[i] = True
            last_true = i
    return pd.Series(out, index=s.index)


def BETWEEN(X, A, B) -> pd.Series:
    """X 是否在 [min(A,B), max(A,B)] 区间内（通达信 BETWEEN）。"""
    s = _s(X)
    lo, hi = min(A, B), max(A, B)
    return (s >= lo) & (s <= hi)


def TOPRANGE(X) -> pd.Series:
    """X 在历史区间中的位置百分比（0~100，相对累计极值）。"""
    s = _s(X)
    lo, hi = s.cummin(), s.cummax()
    rng = (hi - lo).replace(0, np.nan)
    return (s - lo) / rng * 100.0


def LOWRANGE(X) -> pd.Series:
    """100 - TOPRANGE（通达信 LOWRANGE）。"""
    return 100.0 - TOPRANGE(X)


# ───────────────────────────── 标量 / 数学原语 ─────────────────────────────

def CONST(X):
    """取序列末值作为标量（通达信 CONST）。"""
    return float(_s(X).iloc[-1])


def IF(A, B, C) -> pd.Series:
    """逐元素三元选择（通达信 IF）。"""
    a, b, c = _s(A).astype(bool), _s(B), _s(C)
    return pd.Series(np.where(a.to_numpy(), b.to_numpy(), c.to_numpy()), index=b.index)


def MAX(A, B) -> pd.Series:
    """逐元素取大（通达信 MAX）。"""
    return pd.concat([_s(A), _s(B)], axis=1).max(axis=1)


def MIN(A, B) -> pd.Series:
    """逐元素取小（通达信 MIN）。"""
    return pd.concat([_s(A), _s(B)], axis=1).min(axis=1)


def ABS(X) -> pd.Series:
    return _s(X).abs()


def LN(X) -> pd.Series:
    return np.log(_s(X))


def POW(X, Y) -> pd.Series:
    return np.power(_s(X), Y)


def SQRT(X) -> pd.Series:
    return np.sqrt(_s(X))


def SIN(X) -> pd.Series:
    return np.sin(_s(X))


def COS(X) -> pd.Series:
    return np.cos(_s(X))


def TAN(X) -> pd.Series:
    return np.tan(_s(X))


def LAST(X, A: int = 1):
    """通达信 LAST(X,A,B)：简化取 A 周期前的 X 值（B 未指定时等同于 REF(X,A)）。"""
    return REF(X, A)

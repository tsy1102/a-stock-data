# -*- coding: utf-8 -*-
"""sc_technical.py — 技术指标引擎（V16.1 从 get_ful_report.py Layer1 迁移）

包含：MACD / RSI / BOLL / KDJ / 量能分析 / MA 均线
供 sht/med 报告复用（原 ful Layer1 独有能力，ful 下线后保留）。
纯计算逻辑，无网络依赖。
"""

from __future__ import annotations

import math
from typing import Any, Dict, List


def calc_macd(closes: List[float]) -> Dict[str, float]:
    """MACD (12, 26, 9) — 返回 dif, dea, macd, hist"""
    if len(closes) < 30:
        return {}

    # 计算 EMA12 / EMA26
    def _ema(series: List[float], n: int) -> List[float]:
        k = 2 / (n + 1)
        ema_vals: List[float] = [sum(series[:n]) / n]
        for i in range(n, len(series)):
            ema_vals.append(series[i] * k + ema_vals[-1] * (1 - k))
        return ema_vals

    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)

    # DIF = EMA12 - EMA26（对齐长度）
    dif = []
    for i in range(len(ema26)):
        dif.append(ema12[i + (len(ema12) - len(ema26))] - ema26[i])

    # DEA = EMA(DIF, 9)
    if len(dif) < 9:
        return {}
    k_dea = 2 / (9 + 1)
    dea = [sum(dif[:9]) / 9]
    for i in range(9, len(dif)):
        dea.append(dif[i] * k_dea + dea[-1] * (1 - k_dea))

    # MACD 柱 = 2 × (DIF - DEA)
    latest_dif = dif[-1] if dif else 0
    latest_dea = dea[-1] if dea else 0
    hist = 2 * (latest_dif - latest_dea)

    return {
        "dif": round(latest_dif, 4),
        "dea": round(latest_dea, 4),
        "macd": round(hist, 4),
        "dif_prev": round(dif[-2] if len(dif) >= 2 else latest_dif, 4),
        "dea_prev": round(dea[-2] if len(dea) >= 2 else latest_dea, 4),
        "hist_prev": round(
            2
            * (
                (dif[-2] if len(dif) >= 2 else latest_dif)
                - (dea[-2] if len(dea) >= 2 else latest_dea)
            ),
            4,
        ),
    }


def calc_rsi(closes: List[float], period: int = 14) -> Dict[str, float]:
    """RSI 相对强弱指标（Wilder平滑）"""
    if len(closes) < period + 1:
        return {}

    # 计算每日涨跌幅
    changes: List[float] = []
    for i in range(1, len(closes)):
        changes.append(closes[i] - closes[i - 1])

    # 分离涨跌
    gains = [max(c, 0) for c in changes]
    losses = [max(-c, 0) for c in changes]

    # 第一个 RSI: 简单平均
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    # Wilder 平滑
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        rsi = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

    # 再算 RSI6 / RSI24 作为参考
    rsi6: float = 0.0
    if len(changes) >= 6:
        ag6 = sum(gains[:6]) / 6
        al6 = sum(losses[:6]) / 6
        for i in range(6, len(gains)):
            ag6 = (ag6 * 5 + gains[i]) / 6
            al6 = (al6 * 5 + losses[i]) / 6
        rsi6 = 100 - (100 / (1 + (ag6 / al6 if al6 > 0 else 999)))

    return {
        "rsi14": round(rsi, 2),
        "rsi6": round(rsi6, 2) if rsi6 else 0,
    }


def calc_bollinger(closes: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, float]:
    """布林带：中轨/上轨/下轨/带宽/当前位置%"""
    if len(closes) < period:
        return {}

    tail = closes[-period:]
    mid = sum(tail) / period
    variance = sum((c - mid) ** 2 for c in tail) / period
    std = math.sqrt(variance)

    upper = mid + std_dev * std
    lower = mid - std_dev * std
    latest = closes[-1]

    # 当前价在布林带中的位置（0=下轨, 100=上轨, 50=中轨）
    band_width = upper - lower
    pos_pct = ((latest - lower) / band_width * 100) if band_width > 0 else 50
    width_pct = (band_width / mid * 100) if mid > 0 else 0

    return {
        "mid": round(mid, 2),
        "upper": round(upper, 2),
        "lower": round(lower, 2),
        "width_pct": round(width_pct, 2),
        "pos_pct": round(pos_pct, 2),
        "price": round(latest, 2),
    }


def calc_kdj(
    closes: List[float], highs: List[float], lows: List[float], n: int = 9, m1: int = 3, m2: int = 3
) -> Dict[str, float]:
    """KDJ 随机指标"""
    if len(closes) < n or len(highs) < n or len(lows) < n:
        return {}

    # RSV = (C - Ln) / (Hn - Ln) × 100
    rsv_list: List[float] = []
    for i in range(n - 1, len(closes)):
        hh = max(highs[i - n + 1 : i + 1])
        ll = min(lows[i - n + 1 : i + 1])
        if hh == ll:
            rsv_list.append(50.0)
        else:
            rsv_list.append((closes[i] - ll) / (hh - ll) * 100)

    if not rsv_list:
        return {}

    # K = (m1-1)/m1 × K_prev + 1/m1 × RSV
    k_values: List[float] = []
    k = 50.0
    for rsv in rsv_list:
        k = ((m1 - 1) * k + rsv) / m1
        k_values.append(k)

    # D = (m2-1)/m2 × D_prev + 1/m2 × K
    d_values: List[float] = []
    d = 50.0
    for kv in k_values:
        d = ((m2 - 1) * d + kv) / m2
        d_values.append(d)

    # J = 3 × K - 2 × D
    j_values = [3 * k_values[i] - 2 * d_values[i] for i in range(len(k_values))]

    return {
        "k": round(k_values[-1], 2),
        "d": round(d_values[-1], 2),
        "j": round(j_values[-1], 2),
        "k_prev": round(k_values[-2] if len(k_values) >= 2 else k_values[-1], 2),
        "d_prev": round(d_values[-2] if len(d_values) >= 2 else d_values[-1], 2),
    }


def calc_volume_analysis(volumes: List[float]) -> Dict[str, float]:
    """量能分析：5日均量/20日均量 + 今日量比"""
    if not volumes:
        return {}

    latest = volumes[-1]
    ma5 = sum(volumes[-5:]) / 5 if len(volumes) >= 5 else 0
    ma20 = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else 0
    ratio = latest / ma5 if ma5 > 0 else 1.0

    # 量能趋势（近5日 vs 近10-5日）
    if len(volumes) >= 10:
        recent_5 = sum(volumes[-5:]) / 5
        prior_5 = sum(volumes[-10:-5]) / 5
        trend = (recent_5 - prior_5) / prior_5 * 100 if prior_5 > 0 else 0
    else:
        trend = 0

    return {
        "today_wan": round(latest / 10000, 1) if latest else 0,
        "ma5_wan": round(ma5 / 10000, 1) if ma5 else 0,
        "ma20_wan": round(ma20 / 10000, 1) if ma20 else 0,
        "ratio": round(ratio, 2),
        "trend_pct": round(trend, 2),
    }


def calc_ma(closes: List[float], periods: tuple = (5, 10, 20, 60, 120)) -> Dict[str, float]:
    """均线集合：ma5/ma10/ma20/ma60/ma120"""
    out: Dict[str, float] = {}
    for p in periods:
        out[f"ma{p}"] = round(sum(closes[-p:]) / p, 2) if len(closes) >= p else 0.0
    return out


def analyze_technical(
    closes: List[float], highs: List[float], lows: List[float], volumes: List[float]
) -> Dict[str, Any]:
    """统一技术分析入口（V16.1：sht/med 复用）。

    Args:
        closes: 收盘价序列（旧→新）
        highs: 最高价序列
        lows: 最低价序列
        volumes: 成交量序列

    Returns:
        {
            "ma": {ma5/ma10/ma20/ma60/ma120},
            "macd": {...}, "rsi": {...}, "boll": {...}, "kdj": {...},
            "volume": {...},
            "ret_20d": float, "ret_60d": float, "ret_250d": float,
            "high_120d": float, "low_120d": float,
        }
    """
    result: Dict[str, Any] = {}
    if not closes:
        return result

    result["ma"] = calc_ma(closes)
    if len(closes) >= 30:
        result["macd"] = calc_macd(closes)
    if len(closes) >= 15:
        result["rsi"] = calc_rsi(closes)
        result["boll"] = calc_bollinger(closes)
    if len(highs) >= 9 and len(lows) >= 9:
        result["kdj"] = calc_kdj(closes, highs, lows)
    if volumes:
        result["volume"] = calc_volume_analysis(volumes)

    latest = closes[-1]
    if len(closes) >= 21:
        result["ret_20d"] = round((latest / closes[-21] - 1) * 100, 2) if closes[-21] > 0 else 0.0
    if len(closes) >= 61:
        result["ret_60d"] = round((latest / closes[-61] - 1) * 100, 2) if closes[-61] > 0 else 0.0
    if len(closes) >= 251:
        result["ret_250d"] = (
            round((latest / closes[-251] - 1) * 100, 2) if closes[-251] > 0 else 0.0
        )
    if len(closes) >= 120:
        result["high_120d"] = max(closes[-120:])
        result["low_120d"] = min(closes[-120:])
    elif len(closes) > 0:
        result["high_120d"] = max(closes)
        result["low_120d"] = min(closes)
    return result


# ═══════════════════════════════════════════════════════════════
# V17.0.7: 筹码分布 CYQ 算法（来源 myhhub/stock instock/core/kline/cyq.py，
# MIT 许可；与通达信一致的经典"三角形分布 + 换手率衰减"模型）
# ═══════════════════════════════════════════════════════════════

def calculate_cyq(
    dates: list,
    opens: list,
    closes: list,
    highs: list,
    lows: list,
    turnovers: list,
    current_index: int = -1,
    accuracy_factor: int = 150,
    crange: int = 120,
    cyq_days: int = 210,
) -> dict:
    """筹码分布计算（Position Cost Distribution）。

    从日K的 OHLC+换手率 推演全市场持仓成本分布。
    经典"三角形分布 + 换手率衰减"模型，与通达信 CYQ 指标一致。

    Args:
        dates/closes/highs/lows/turnovers: K线序列(等长列表)
        current_index: 当前K线下标(-1=最后一根)
        accuracy_factor: 价格精度档数
        crange: 锚点偏移量
        cyq_days: 换手周期窗口(默认210交易日)

    Returns:
        {"benefit_pct": 获利盘比例(0~1),
         "avg_cost": 平均成本价,
         "cost_90_low": 90%筹码区间下界,
         "cost_90_high": 90%筹码区间上界,
         "concentration_90": 90%筹码集中度(0~1,越小越集中),
         "cost_70_low": 70%筹码区间下界,
         "cost_70_high": 70%筹码区间上界,
         "concentration_70": 70%筹码集中度}
    """
    n = len(closes)
    if n == 0:
        return {}
    idx = n + current_index if current_index < 0 else current_index
    if idx < 1:
        return {}

    # 确定窗口 [start:end)
    end = max(idx - crange + 1, 0)
    start = max(end - cyq_days, 0)
    if end <= start:
        start = max(0, end - cyq_days)

    # 窗口数据
    w_open = [opens[i] for i in range(start, end)]
    w_close = [closes[i] for i in range(start, end)]
    w_high = [highs[i] for i in range(start, end)]
    w_low = [lows[i] for i in range(start, end)]
    w_turn = [min(t / 100.0, 1.0) if t > 1 else min(t, 1.0)
              for t in (turnovers[i] for i in range(start, end))]
    cur_close = closes[idx]

    # 价格网格
    hi = max(w_high) if w_high else 0
    lo = min(w_low) if w_low else 0
    if hi <= lo or lo <= 0:
        return {}
    acc = max(0.01, (hi - lo) / (accuracy_factor - 1))
    yrange = [round(lo + acc * i, 2) for i in range(accuracy_factor)]

    # 构建分布
    xdata = [0.0] * accuracy_factor
    for j in range(len(w_close)):
        o, c = w_open[j], w_close[j]
        h, l = w_high[j], w_low[j]
        tr = w_turn[j]

        avg = (o + c + h + l) / 4.0
        H = int((h - lo) / acc)
        L = int((l - lo) / acc + 0.99)
        G = (accuracy_factor - 1) if h == l else 2.0 / (h - l)
        P = int((avg - lo) / acc)

        # 旧筹码衰减
        for k2 in range(accuracy_factor):
            xdata[k2] *= (1 - tr)

        # 当日新筹码三角形分布叠加
        if h == l:
            if 0 <= P < accuracy_factor:
                xdata[P] += G * tr / 2
        else:
            for k2 in range(max(0, L), min(H, accuracy_factor - 1) + 1):
                price_k = lo + acc * k2
                if abs(avg - l) < 1e-9 or abs(h - avg) < 1e-9:
                    w = 1.0
                elif price_k <= avg:
                    denom = avg - l
                    w = (price_k - l) / denom if denom > 0 else 0.0
                else:
                    denom = h - avg
                    w = (h - price_k) / denom if denom > 0 else 0.0
                xdata[k2] += w * G * tr

    total_chips = sum(xdata)
    if total_chips <= 0:
        return {}

    def _cost_by_chip(target_chip):
        """从低价累计筹码到 target_chip 总量时的价格"""
        cum = 0.0
        for k2 in range(accuracy_factor):
            cum += xdata[k2]
            if cum >= target_chip:
                return yrange[k2]
        return yrange[-1]

    def _benefit_part(price):
        """当前价格以下的筹码占比(获利盘比例)"""
        cum = 0.0
        for k2 in range(accuracy_factor):
            if yrange[k2] <= price:
                cum += xdata[k2]
        return cum / total_chips if total_chips > 0 else 0.0

    benefit = _benefit_part(cur_close)
    avg_cost = _cost_by_chip(total_chips * 0.5)

    def _pct_range(pct):
        lo_p = _cost_by_chip(total_chips * (1 - pct) / 2)
        hi_p = _cost_by_chip(total_chips * (1 + pct) / 2)
        conc = (hi_p - lo_p) / (hi_p + lo_p) if (hi_p + lo_p) > 0 else 0
        return lo_p, hi_p, conc

    c90_lo, c90_hi, c90_conc = _pct_range(0.9)
    c70_lo, c70_hi, c70_conc = _pct_range(0.7)

    return {
        "benefit_pct": round(benefit, 4),
        "avg_cost": round(avg_cost, 2),
        "cost_90_low": round(c90_lo, 2),
        "cost_90_high": round(c90_hi, 2),
        "concentration_90": round(c90_conc, 4),
        "cost_70_low": round(c70_lo, 2),
        "cost_70_high": round(c70_hi, 2),
        "concentration_70": round(c70_conc, 4),
    }


def get_kline_patterns(opens: list, highs: list, lows: list, closes: list) -> dict:
    """61 种 K 线形态识别（V17.0.7，来源 myhhub/stock——纯 TA-Lib CDL 函数族委托）。

    需安装 TA-Lib C 库（pip install TA-Lib）。未安装时返回 {}。
    返回 {形态名: 最新值}，正值=买入信号 / 负值=卖出信号 / 0=无信号。

    完整 61 形态清单见 docs/verify/ftshare_fields_mirror.md 同级注释或 myhhub/stock README。
    """
    result = {}
    try:
        import talib
        import numpy as np

        o = np.array(opens, dtype=np.float64)
        h = np.array(highs, dtype=np.float64)
        l = np.array(lows, dtype=np.float64)
        c = np.array(closes, dtype=np.float64)
        if len(c) < 3:
            return {}

        _cdl_map = {
            "two_crows": "CDL2CROWS", "three_black_crows": "CDL3BLACKCROWS",
            "three_inside_up_down": "CDL3INSIDE", "three_line_strike": "CDL3LINESTRIKE",
            "three_outside_up_down": "CDL3OUTSIDE", "three_stars_in_the_south": "CDL3STARSINSOUTH",
            "three_white_soldiers": "CDL3WHITESOLDIERS", "abandoned_baby": "CDLABANDONEDBABY",
            "advance_block": "CDLADVANCEBLOCK", "belt_hold": "CDLBELTHOLD",
            "breakaway": "CDLBREAKAWAY", "closing_marubozu": "CDLCLOSINGMARUBOZU",
            "concealing_baby_swallow": "CDLCONCEALBABYSWALL", "counterattack": "CDLCOUNTERATTACK",
            "dark_cloud_cover": "CDLDARKCLOUDCOVER", "doji": "CDLDOJI",
            "doji_star": "CDLDOJISTAR", "dragonfly_doji": "CDLDRAGONFLYDOJI",
            "engulfing_pattern": "CDLENGULFING", "evening_doji_star": "CDLEVENINGDOJISTAR",
            "evening_star": "CDLEVENINGSTAR", "up_down_gap": "CDLGAPSIDESIDEWHITE",
            "gravestone_doji": "CDLGRAVESTONEDOJI", "hammer": "CDLHAMMER",
            "hanging_man": "CDLHANGINGMAN", "harami_pattern": "CDLHARAMI",
            "harami_cross_pattern": "CDLHARAMICROSS", "high_wave_candle": "CDLHIGHWAVE",
            "hikkake_pattern": "CDLHIKKAKE", "modified_hikkake_pattern": "CDLHIKKAKEMOD",
            "homing_pigeon": "CDLHOMINGPIGEON", "identical_three_crows": "CDLIDENTICAL3CROWS",
            "in_neck_pattern": "CDLINNECK", "inverted_hammer": "CDLINVERTEDHAMMER",
            "kicking": "CDLKICKING", "kicking_bull_bear": "CDLKICKINGBYLENGTH",
            "ladder_bottom": "CDLLADDERBOTTOM", "long_legged_doji": "CDLLONGLEGGEDDOJI",
            "long_line_candle": "CDLLONGLINE", "marubozu": "CDLMARUBOZU",
            "matching_low": "CDLMATCHINGLOW", "mat_hold": "CDLMATHOLD",
            "morning_doji_star": "CDLMORNINGDOJISTAR", "morning_star": "CDLMORNINGSTAR",
            "on_neck_pattern": "CDLONNECK", "piercing_pattern": "CDLPIERCING",
            "rickshaw_man": "CDLRICKSHAWMAN", "rising_falling_three": "CDLRISEFALL3METHODS",
            "separating_lines": "CDLSEPARATINGLINES", "shooting_star": "CDLSHOOTINGSTAR",
            "short_line_candle": "CDLSHORTLINE", "spinning_top": "CDLSPINNINGTOP",
            "stalled_pattern": "CDLSTALLEDPATTERN", "stick_sandwich": "CDLSTICKSANDWICH",
            "takuri": "CDLTAKURI", "tasuki_gap": "CDLTASUKIGAP",
            "thrusting_pattern": "CDLTHRUSTING", "tristar_pattern": "CDLTRISTAR",
            "unique_3_river": "CDLUNIQUE3RIVER", "upside_gap_two_crows": "CDLUPSIDEGAP2CROWS",
            "up_downside_gap_three": "CDLXSIDEGAP3METHODS",
        }
        for field_name, func_name in _cdl_map.items():
            fn = getattr(talib, func_name, None)
            if fn is not None:
                vals = fn(o, h, l, c)
                result[field_name] = int(vals[-1]) if len(vals) else 0
    except ImportError:
        pass
    return result

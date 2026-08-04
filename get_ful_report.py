#!/usr/bin/env python3
"""
get_ful_report.py — A股七层全维度分析引擎（含行业对比/风险扫描/六维加权评分）

版本信息:
    V15.2  2026-07-28 - V15.2 缓存 valid_if 强化（dragon_tiger/zhb_data）+ ZHB 交叉验证恢复
    V15.1  2026-07-26 - V15.1 全局 ZHB 旁路普及：Layer 3 财务诊断与 Layer 6 行业对比初筛融入 ZHB 内存字典，行业比较速度提升 10 倍
    V15.0  2026-07-26 - 接入 CanonicalStockData 强类型数据合约，实施基于真实周期的 ZHB-First 离线优先路由
    V14.0  2026-07-22 - 文档同步：docstring 版本信息更新到 V14.0；is_workday() Bug 修复由 stock_common 上游提供
    V13.x  2026-07-22 - 受益于 stock_cache.py dataclass 透明序列化（脚本无改动）
    V12.6  2026-07-22 - 受益于字段路由简化（移除估值字段 HTTP fallback）
    V12.4  2026-07-22 - 抽象 BaseReportRunner 基类
    V12.4  2026-07-23 - 迁移至 BaseReportRunner 框架；修复 data_provider 错误导入
    V9.5   2026-07-11 - 价格走势改为近15日倒序显示；新闻舆情文案从"近24小时"改为"近期"
    V9.3.3 2026-07-11 - 新闻与舆情 page_size 从10增加到30；休市提示文案统一
    V9.3.2 2026-07-09 - 基础设施修复：TDX K线假数据防护、SQLite WAL死锁修复、代理环境兼容（脚本本身无改动，受益于底层修复）
    V9.3   2026-07-07 - 盘前行情模式：9:30前使用上一交易日日K线数据；修复成功/失败统计为0问题；删除报告标题硬编码版本号
    V9.2   2026-07-05 - 异常处理规范化；缓存交叉验证机制启用
    V9.1.1 2026-07-04 - 六维评分透明化（补全分红面）；修复 theme→holder 映射bug；F10死代码精简
    V9.1 2026-07-04 - F10 全覆盖：新增全部6个F10章节（异动/财务深度/股东行为/治理/研发/主营）+数据质量附录
    V9.0 2026-07-02 - 舆情互动层（Layer 10）；上市日期 push2 fallback；valid_if 校验；_has_zero_price 拦截
    V8.8 2026-06-25 - GD上传逻辑统一化 & 快照格式升级（TXT+自动上传）
    V8.7 2026-06-25 - 死代码清理：同步版替换为薄包装

架构:
  Layer 1  行情与技术指标（MA/成交量/MACD/RSI/布林带/KDJ）
  Layer 2  机构研报与估值（东财研报/同花顺一致预期）
  Layer_IND 行业对比（同行横向估值/走势对比）
  Layer 3  交易信号与题材（龙虎榜/概念板块/资金流/限售解禁）
  Layer 4  筹码与资金结构（股东户数/融资融券/大宗交易/机构持仓）
  Layer 5  新闻与舆情（东财个股新闻/同花顺热榜）
  Layer 6  基本面与财务健康（利润表/资产负债表/ROE/分红）
  Layer_RISK 风险扫描（8项：商誉/杠杆/回款/连续亏损/减持/质押/解禁/现金流）
  Layer 7  公告与重大事项（巨潮公告关键词过滤）
  综合评分: 技术面25% + 估值面20% + 基本面20% + 资金面15% + 筹码面10% + 分红面10%

特点:
  - 每层独立分析，单层失败不影响其他层（优雅降级）
  - 支持 ThreadPoolExecutor 并行获取（默认4线程）
  - 所有HTTP请求复用 stock_common 的统一限速器
  - 技术指标 (MACD/RSI/布林带/KDJ) 纯本地计算，零额外API
  - 输出: ./reports/{code}_ful_{YYYYMMDD}_{HHMM}.txt

用法:
  python get_ful_report.py 600519
  python get_ful_report.py 600519 000858 002310
  python get_ful_report.py 600519 --no-parallel --no-upload
  python get_ful_report.py 600519 -o ./my_reports
"""

import argparse
import logging
import os
import sys
import time
import math
import re
import asyncio
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

from data_provider import (
    get_stock_composite_async,
    get_main_net_buy_async,
    get_stock_price_async,
    get_pe_ttm_async,
    get_pb_async,
    get_change_pct_async,
    get_amount_wan_async,
    get_turnover_pct_async,
    get_canonical_stock_data,  # V15.3 强类型合约推广
    get_dividend_yield_async,
    get_52w_range_async,
    get_change_ytd_async,
)

from stock_common import (
    BaseReportRunner,
    _debug_log, _safe_float, UA,
    parse_args, clean_codes, ensure_output_dir, get_script_dir,
    _load_strategy_config,
    get_market_status,
    create_async_session,
    # HTTP 工具
    _em_filter, _quick_request, _request_with_retry, eastmoney_datacenter,
    # 舆情/新闻
    get_eastmoney_stock_news, cls_telegraph, cninfo_irm, ths_hot_list,
    # 行情工具
    is_limit_up, is_limit_down,
    # 股东/持仓
    get_holder_structure, holder_change,
    get_strategic_announcements,
    # ZHB 数据
    get_zhb_single_stock_data, is_zhb_data_fresh,
    get_zhb_industry_map, get_zhb_dividend_yield,
    get_zhb_change_ytd, get_zhb_amount_wan,
    get_zhb_ipo_price,
    get_zhb_main_net_buy, get_zhb_streak_days, get_zhb_tip_info,
    # 评分框架
    ScoreData, calculate_score,
    calculate_multi_school_scores,
)

from gd_uploader import init_gd, upload_stock_report_by_code, cleanup_gd_proxy

from tdx_client import (
    tdx_get_security_bars, tdx_get_quote_full, tdx_get_index_quote,
    tdx_get_fund_flow, tdx_get_history_fund_flow, tdx_get_eps_from_reports,
    tdx_get_latest_announcements, tdx_get_belong_boards, tdx_get_board_members,
    tdx_get_dividend_history, tdx_get_historical_high,
)

_SCRIPT_DIR = get_script_dir()
_sc = _load_strategy_config()

# 并行分析线程数（与 header 显示保持一致）
_MAX_WORKERS = 3

# V15.3 修复: 4 个报告模块同名 _SNAPSHOT_DATA 全局变量冲突
# 抽出到 stock_common.sc_snapshot 统一管理
# V15.3.1: 直接 import 共享的 SnapshotProxy 类，删除 20 行重复定义
from stock_common.sc_snapshot import SnapshotProxy as _SnapshotProxy  # noqa: E402

_SNAPSHOT_DATA = _SnapshotProxy()


# =====================================================================
# 工具函数层（含方案1：MACD/RSI/布林带/KDJ纯Python实现）
# =====================================================================

def _fmt_num(n: Any, digits: int = 2) -> str:
    if n is None:
        return "-"
    try:
        f = float(n)
        if abs(f) >= 10000:
            return f"{f:,.{digits}f}"
        return f"{f:.{digits}f}"
    except (ValueError, TypeError):
        return "-"


def _fmt_pct(n: Any, digits: int = 2) -> str:
    if n is None:
        return "-"
    try:
        return f"{float(n):+.{digits}f}%"
    except (ValueError, TypeError):
        return "-"


def _section(title: str) -> str:
    return f"\n{'═' * 78}\n{title}\n{'─' * 78}"


# ── 纯 Python 技术指标实现（方案1）──

def _calc_macd(closes: List[float]) -> Dict[str, float]:
    """MACD (12, 26, 9) — 返回 dif, dea, macd, hist"""
    if len(closes) < 30:
        return {}

    # 计算 EMA12 / EMA26
    def _ema(series, n):
        k = 2 / (n + 1)
        ema_vals = [sum(series[:n]) / n]
        for i in range(n, len(series)):
            ema_vals.append(series[i] * k + ema_vals[-1] * (1 - k))
        return ema_vals

    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)

    # DIF = EMA12 - EMA26（对齐长度）
    dif_start_offset = len(ema26)
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
        "hist_prev": round(2 * ((dif[-2] if len(dif) >= 2 else latest_dif) - (dea[-2] if len(dea) >= 2 else latest_dea)), 4),
    }


def _calc_rsi(closes: List[float], period: int = 14) -> Dict[str, float]:
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
    rsi6 = 0
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


def _calc_bollinger(closes: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, float]:
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


def _calc_kdj(closes: List[float], highs: List[float], lows: List[float], n: int = 9, m1: int = 3, m2: int = 3) -> Dict[str, float]:
    """KDJ 随机指标"""
    if len(closes) < n or len(highs) < n or len(lows) < n:
        return {}

    # RSV = (C - Ln) / (Hn - Ln) × 100
    rsv_list: List[float] = []
    for i in range(n - 1, len(closes)):
        hh = max(highs[i - n + 1: i + 1])
        ll = min(lows[i - n + 1: i + 1])
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


def _calc_volume_analysis(volumes: List[float]) -> Dict[str, float]:
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


# =====================================================================
# Layer 1: 行情层（增强版）
#   - 实时行情
#   - 120日K线 + MA/MACD/RSI/布林带/KDJ + 量能分析
#   - 相对指数收益
# =====================================================================

async def layer1_market(code: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "ok": True, "basic": {}, "kline": {},
        "tech": {}, "index_compare": {}, "signals": [],
    }

    # V15 统一数据中心：通过 get_canonical_stock_data 获取强类型标准化数据
    from data_provider import get_canonical_stock_data
    cdata = await asyncio.to_thread(get_canonical_stock_data, code)

    if not cdata:
        result["ok"] = False
        result["signals"].append("实时行情获取失败")
        return result

    result["basic"] = {
        "name": cdata.name,
        "price": cdata.price,
        "change_pct": cdata.change_pct,
        "open": cdata.open,
        "high": cdata.high,
        "low": cdata.low,
        "pe_ttm": cdata.pe_ttm,
        "pb": cdata.pb,
        "mcap_yi": cdata.mcap_yi,
        "float_mcap_yi": cdata.float_mcap_yi,
        "turnover_pct": cdata.turnover_pct,
        "amplitude": round((cdata.high - cdata.low) / cdata.prev_close * 100, 2) if cdata.prev_close > 0 else 0.0,
        "limit_up_price": round(cdata.prev_close * 1.10, 2) if cdata.prev_close > 0 else 0.0,
        "limit_down_price": round(cdata.prev_close * 0.90, 2) if cdata.prev_close > 0 else 0.0,
    }

    result["basic"]["zhb"] = {
        "pe_dynamic": cdata.pe_dynamic,
        "dividend_yield": cdata.dividend_yield,
        "change_ytd": cdata.change_ytd,
        "change_5d": cdata.change_5d,
        "change_10d": cdata.change_10d,
        "change_20d": cdata.change_20d,
        "change_30d": 0,
        "change_60d": cdata.change_60d,
        "high_52w": cdata.high_52w,
        "low_52w": cdata.low_52w,
        "amount_wan": cdata.amount_wan,
        "employee_count": cdata.employee_count,
        "ipo_price": cdata.ipo_price,
        "industry_code": cdata.industry_code,
        "main_net_buy_hands": cdata.main_net_buy_hands,
        "main_net_buy_hands_1d": 0,
        "main_net_buy_amount": cdata.main_net_buy_wan,
    }

    # 涨停/跌停
    name = result["basic"].get("name", "")
    chg = result["basic"]["change_pct"]
    if is_limit_up(code, name, chg):
        result["signals"].append(f"今日涨停 (+{chg:.2f}%)")
    elif is_limit_down(code, name, chg):
        result["signals"].append(f"今日跌停 ({chg:.2f}%)")

    # 800根日K线（足够计算所有长周期指标）
    kk, rows = await asyncio.to_thread(tdx_get_security_bars, code, count=800)
    closes_list, highs_list, lows_list, volumes_list = [], [], [], []
    if rows and len(rows) >= 20:
        idx_map = {k: i for i, k in enumerate(kk)}
        ci = idx_map.get("close", -1)
        hi = idx_map.get("high", -1)
        li = idx_map.get("low", -1)
        vi = idx_map.get("volume", -1)

        for r in rows:
            try:
                if ci >= 0 and ci < len(r):
                    closes_list.append(float(r[ci]))
                if hi >= 0 and hi < len(r):
                    highs_list.append(float(r[hi]))
                if li >= 0 and li < len(r):
                    lows_list.append(float(r[li]))
                if vi >= 0 and vi < len(r):
                    volumes_list.append(float(r[vi]))
            except (ValueError, TypeError):
                continue

    # MA均线 & 收益 & 偏离
    if closes_list:
        latest = closes_list[-1]
        ma5 = sum(closes_list[-5:]) / 5 if len(closes_list) >= 5 else 0
        ma10 = sum(closes_list[-10:]) / 10 if len(closes_list) >= 10 else 0
        ma20 = sum(closes_list[-20:]) / 20 if len(closes_list) >= 20 else 0
        ma60 = sum(closes_list[-60:]) / 60 if len(closes_list) >= 60 else 0
        ma120 = sum(closes_list[-120:]) / 120 if len(closes_list) >= 120 else 0

        # V10.1: 52周高低、阶段涨跌幅优先用zhb，无zhb时fallback到K线计算
        _zhb_sub = result["basic"].get("zhb", {})
        _high_52w = _zhb_sub.get("high_52w", 0)
        _low_52w = _zhb_sub.get("low_52w", 0)
        _change_20d = _zhb_sub.get("change_20d", 0)
        _change_60d = _zhb_sub.get("change_60d", 0)

        result["kline"] = {
            "price": round(latest, 2),
            "ma5": round(ma5, 2), "ma10": round(ma10, 2),
            "ma20": round(ma20, 2), "ma60": round(ma60, 2),
            "ma120": round(ma120, 2) if ma120 else 0,
            "high_120d": _high_52w if _high_52w > 0 else (max(closes_list[-120:]) if len(closes_list) >= 120 else max(closes_list)),
            "low_120d": _low_52w if _low_52w > 0 else (min(closes_list[-120:]) if len(closes_list) >= 120 else min(closes_list)),
            "ret_20d": _change_20d if _change_20d else (round((latest / closes_list[-20] - 1) * 100, 2) if len(closes_list) >= 20 else 0),
            "ret_60d": _change_60d if _change_60d else (round((latest / closes_list[-60] - 1) * 100, 2) if len(closes_list) >= 60 else 0),
            "ret_250d": round((latest / closes_list[-250] - 1) * 100, 2) if len(closes_list) >= 250 else 0,
            "closes": closes_list[-60:],  # 保留近60日收盘价画ASCII图
        }

        # 均线信号
        if ma5 and ma10 and ma20 and ma5 > ma10 > ma20:
            result["signals"].append("均线多头排列 (MA5>MA10>MA20)")
        elif ma5 and ma10 and ma20 and ma5 < ma10 < ma20:
            result["signals"].append("均线空头排列 (MA5<MA10<MA20)")

        if ma20 and latest < ma20 * 0.92:
            result["signals"].append("当前价低于MA20超过8%，短期超卖")
        if ma20 and latest > ma20 * 1.08:
            result["signals"].append("当前价高于MA20超过8%，短期超买")

    else:
        # K线数据不足，用实时行情价格填充基本字段
        _price = result["basic"].get("price", 0)
        if _price:
            result["kline"] = {"price": round(_price, 2)}
            result["signals"].append("K线数据获取不足，仅显示实时行情")

    # ── 技术指标计算 ──
    tech = {}
    if closes_list and len(closes_list) >= 30:
        # MACD
        macd = _calc_macd(closes_list)
        if macd:
            tech["macd"] = macd
            # 金叉/死叉判断
            if macd["dif_prev"] <= macd["dea_prev"] and macd["dif"] > macd["dea"]:
                result["signals"].append(f"MACD 金叉 (DIF {macd['dif']:.3f} 上穿 DEA {macd['dea']:.3f})")
            elif macd["dif_prev"] >= macd["dea_prev"] and macd["dif"] < macd["dea"]:
                result["signals"].append(f"⚠️ MACD 死叉 (DIF {macd['dif']:.3f} 下穿 DEA {macd['dea']:.3f})")
            if macd["dif"] > 0 and macd["dea"] > 0:
                result["signals"].append("MACD 处于零轴上方（中期强势）")
            elif macd["dif"] < 0 and macd["dea"] < 0:
                result["signals"].append("⚠️ MACD 处于零轴下方（中期弱势）")

        # RSI
        rsi = _calc_rsi(closes_list, 14)
        if rsi:
            tech["rsi"] = rsi
            if rsi["rsi14"] > 70:
                result["signals"].append(f"RSI={rsi['rsi14']:.1f}，超买区域")
            elif rsi["rsi14"] < 30:
                result["signals"].append(f"RSI={rsi['rsi14']:.1f}，超卖区域，或有反弹机会")

        # 布林带
        boll = _calc_bollinger(closes_list, 20, 2.0)
        if boll:
            tech["boll"] = boll
            if boll["pos_pct"] > 95:
                result["signals"].append(f"价格接近布林带上轨（位置 {boll['pos_pct']:.0f}%），短期强势但需警惕回调")
            elif boll["pos_pct"] < 5:
                result["signals"].append(f"价格接近布林带下轨（位置 {boll['pos_pct']:.0f}%），超跌或有支撑")

        # KDJ
        if highs_list and lows_list and len(highs_list) >= 9 and len(lows_list) >= 9:
            kdj = _calc_kdj(closes_list, highs_list, lows_list)
            if kdj:
                tech["kdj"] = kdj
                if kdj["j"] > 100:
                    result["signals"].append(f"KDJ J值 {kdj['j']:.1f}，超买")
                elif kdj["j"] < 0:
                    result["signals"].append(f"KDJ J值 {kdj['j']:.1f}，超卖")
                if kdj["k_prev"] <= kdj["d_prev"] and kdj["k"] > kdj["d"]:
                    result["signals"].append(f"KDJ K线金叉 D线 (K {kdj['k']:.1f}/D {kdj['d']:.1f})")

        # 量能分析
        if volumes_list:
            vol = _calc_volume_analysis(volumes_list)
            if vol:
                tech["volume"] = vol
                if vol["ratio"] > 2.5:
                    result["signals"].append(f"今日量比 {vol['ratio']:.2f}，显著放量")
                elif vol["ratio"] < 0.4:
                    result["signals"].append(f"今日量比 {vol['ratio']:.2f}，大幅缩量")

    result["tech"] = tech

    # 相对指数收益
    idx_q = await asyncio.to_thread(tdx_get_index_quote, "sh000300")
    if idx_q:
        result["index_compare"] = {
            "index_name": "沪深300",
            "index_chg": idx_q.get("change_pct", 0),
            "stock_minus_index": round(chg - idx_q.get("change_pct", 0), 2),
        }

    return result


# =====================================================================
# Layer 2: 研报层（保留原实现）
# =====================================================================

async def layer2_research(code: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "ok": True, "recent_reports": [],
        "rating_dist": {}, "eps_forecast": None,
        "valuation": {}, "signals": [],
    }

    try:
        r = await asyncio.to_thread(_request_with_retry,
            "https://reportapi.eastmoney.com/report/list",
            params={"pageSize": "20", "industry": "*", "rating": "*",
                    "beginTime": "2000-01-01", "endTime": "2030-01-01",
                    "pageNo": "1", "code": code, "qType": "0"},
            timeout=20,
        )
        if r is not None:
            rows = r.json().get("data", []) or []
            rating_count: Dict[str, int] = {}
            for row in rows[:15]:
                title = row.get("title", "") or row.get("infoTitle", "")
                pub_date = str(row.get("publishDate", ""))[:10]
                org = row.get("orgSName", "")
                rating = row.get("emRatingName", "") or row.get("rating", "")
                if rating:
                    rating_count[rating] = rating_count.get(rating, 0) + 1
                result["recent_reports"].append({
                    "title": title[:60], "date": pub_date,
                    "org": org, "rating": rating,
                })
            result["rating_dist"] = rating_count
    except Exception as _e:
        _debug_log(f"ful layer2 research reports error: {_e}")

    try:
        r = await asyncio.to_thread(_quick_request,
            f"https://basic.10jqka.com.cn/new/{code}/worth.html",
            headers={"User-Agent": UA, "Referer": "https://basic.10jqka.com.cn/"},
            timeout=15,
        )
        if r is not None:
            r.encoding = "gbk"
            m = re.search(r'汇总--预测年报每股收益.*?(<tbody>.*?</tbody>)', r.text, re.DOTALL)
            if m:
                rows_html = re.findall(r'<tr>(.*?)</tr>', m.group(1), re.DOTALL)
                eps_rows = []
                for row in rows_html:
                    cells = re.findall(r'<(?:th|td)[^>]*>(.*?)</(?:th|td)>', row, re.DOTALL)
                    cleaned = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
                    if len(cleaned) >= 4:
                        eps_rows.append(cleaned[:6])
                if eps_rows:
                    result["eps_forecast"] = eps_rows
    except Exception as _e:
        _debug_log(f"ful layer2 eps forecast error: {_e}")

    if not result["eps_forecast"]:
        em_eps = await asyncio.to_thread(tdx_get_eps_from_reports, code)
        if em_eps and em_eps.get("eps_cur"):
            result["eps_forecast"] = [
                ["预测今年", "1", "-", str(em_eps["eps_cur"]), "-", "-"],
                ["预测明年", "1", "-", str(em_eps.get("eps_next", "")), "-", "-"],
            ]

    try:
        # V15.2 修正: 复用 L360 的 cdata（price/pe_ttm/pb），不再重复调 get_pe_ttm_async 等触发冗余 zhb_data 缓存
        dp_price = cdata.price if cdata else 0
        dp_pe_ttm = cdata.pe_ttm if cdata else 0
        dp_pb = cdata.pb if cdata else 0

        # fallback 到 tdx（仅当 cdata 全 0 时）
        q = None
        if not dp_price or not dp_pe_ttm or not dp_pb:
            try:
                q = await asyncio.to_thread(tdx_get_quote_full, code)
            except Exception:
                q = None

        price = dp_price if dp_price else (q.get("price", 0) if q else 0)
        pe_ttm = dp_pe_ttm if dp_pe_ttm and dp_pe_ttm > 0 else (q.get("pe_ttm", 0) if q else 0)
        pb = dp_pb if dp_pb and dp_pb > 0 else (q.get("pb", 0) if q else 0)

        if price > 0 and result["eps_forecast"]:
            for row in result["eps_forecast"]:
                try:
                    eps_val = float(row[3]) if row[3] else 0
                    # EPS合理性检查：必须为正数才能计算前向PE
                    if eps_val <= 0:
                        continue
                    forward_pe = round(price / eps_val, 2)
                    # 注意：PEG计算需要机构一致预期增速，本脚本无此数据来源，不计算PEG
                    result["valuation"] = {
                        "year_label": row[0], "eps": eps_val,
                        "forward_pe": forward_pe,
                        "peg": None,  # 无机构一致预期，不计算PEG
                        "current_pe_ttm": pe_ttm,
                        "pb": pb,
                    }
                    if forward_pe < 15:
                        result["signals"].append(f"前向PE {forward_pe}，低估区")
                    elif forward_pe > 50:
                        result["signals"].append(f"前向PE {forward_pe}，估值偏高")
                    # PEG需机构一致预期增速，本脚本无此数据来源
                    break
                except (ValueError, TypeError):
                    continue
    except Exception as _e:
        _debug_log(f"ful layer2 valuation error: {_e}")

    return result


# =====================================================================
# Layer_IND: 行业对比（方案2新增）
# =====================================================================

async def layer_ind_industry(code: str, stock_mcap: float = 0) -> Dict[str, Any]:
    """
    行业对比分析（方案2增强）：
    1) 通过 tdx_get_belong_boards 获取行业板块代码
    2) 用 tdx_get_board_members 获取板块内其他成员
    3) 对市值在0.3x~3x范围内的同行做估值/涨跌幅对比
    4) 生成对比表 + 行业均值
    """
    result: Dict[str, Any] = {
        "ok": True, "industry_name": "", "peers": [],
        "peer_summary": {}, "signals": [],
    }

    try:
        # 1. 获取行业板块归属
        boards = await asyncio.to_thread(tdx_get_belong_boards, code)
        industries = (boards or {}).get("industry", []) or []
        if not industries:
            result["signals"].append("无明确行业归属")
            return result

        ind = industries[0]
        ind_code = ind.get("code", "")
        ind_name = ind.get("name", "")
        result["industry_name"] = ind_name
        if not ind_code:
            result["signals"].append(f"行业[{ind_name}]代码无效")
            return result

        # 2. 获取板块成员（优先用 tdx_get_board_members）
        all_peers = []
        try:
            bm = await asyncio.to_thread(tdx_get_board_members, ind_code)
            if bm:
                for m in bm:
                    mc = m.get("code", "")
                    if not mc:
                        continue
                    all_peers.append({
                        "code": mc,
                        "name": m.get("name", ""),
                        "pe_ttm": m.get("pe", 0) or 0,
                        "pb": m.get("pb", 0) or 0,
                        "mcap_yi": m.get("mcap_yi", 0) or 0,
                        "chg_pct": m.get("change_pct", 0) or 0,
                    })
        except Exception as _e:
            _debug_log(f"ful layer_ind board members error: {_e}")

        # 回退：东财 datacenter（当 tdx_get_board_members 失败时）
        if not all_peers:
            try:
                member_rows = await asyncio.to_thread(eastmoney_datacenter,
                    code, "LC_INDEX_ELT",
                    filter_str='',
                    sort_columns="MARKET_CAP", sort_types="-1",
                    page_size=20,
                )
                for mr in member_rows or []:
                    p_code = str(mr.get("SECUCODE", "") or mr.get("secu_code", ""))
                    if p_code and len(p_code) >= 6:
                        all_peers.append({
                            "code": p_code[:6],
                            "name": mr.get("SECNAME", ""),
                            "pe_ttm": 0, "pb": 0, "mcap_yi": 0, "chg_pct": 0,
                        })
            except Exception as _e:
                _debug_log(f"ful layer_ind eastmoney peers error: {_e}")

        # 去除自身
        all_peers = [p for p in all_peers if p["code"] != code]

        # 市值过滤（0.3x ~ 3x），但保证最少有3个同行
        # 若市值差距极大（如龙头股），则跳过市值过滤，直接用全部同行
        skip_mcap_filter = False
        if stock_mcap > 0 and all_peers:
            mcap_max = max(p.get("mcap_yi", 0) for p in all_peers)
            mcap_min = min(p.get("mcap_yi", 0) for p in all_peers if p.get("mcap_yi", 0) > 0)
            # 如果当前股市值远超所有同行（>5x最大同行），或远低于同行，跳过过滤
            if stock_mcap > mcap_max * 5 or stock_mcap < mcap_min / 5:
                skip_mcap_filter = True

        if not skip_mcap_filter and stock_mcap > 0 and all_peers:
            filtered = [p for p in all_peers
                        if p.get("mcap_yi", 0) > 0 and stock_mcap * 0.3 <= p["mcap_yi"] <= stock_mcap * 3]
            if len(filtered) >= 3:
                all_peers = filtered

        # 限制最多 8 只
        all_peers = all_peers[:8]
        if not all_peers:
            result["signals"].append("没有可对比的同行样本")
            return result

        # 3. 补全缺失行情信息（若没有 PE/PB）
        async def _ensure_full(p: Dict) -> Dict:
            try:
                if not p.get("pe_ttm") or not p.get("pb") or not p.get("price", 0):
                    # 优先使用 data_provider
                    _dp_comp = None
                    try:
                        _dp_comp = await get_stock_composite_async(p["code"])
                    except Exception:
                        _dp_comp = None

                    if _dp_comp:
                        if not p.get("price", 0):
                            p["price"] = _dp_comp.get("price", p.get("price", 0))
                        if not p.get("chg_pct"):
                            p["chg_pct"] = _dp_comp.get("change_pct", p.get("chg_pct", 0))
                        if not p.get("pe_ttm"):
                            p["pe_ttm"] = _dp_comp.get("pe_ttm", p.get("pe_ttm", 0))
                        if not p.get("pb"):
                            p["pb"] = _dp_comp.get("pb", p.get("pb", 0))
                        if not p.get("mcap_yi"):
                            p["mcap_yi"] = _dp_comp.get("mcap_yi", p.get("mcap_yi", 0))

                    # fallback 到 tdx
                    if not p.get("pe_ttm") or not p.get("pb") or not p.get("price", 0):
                        try:
                            q = await asyncio.to_thread(tdx_get_quote_full, p["code"])
                            if q:
                                if not p.get("price", 0):
                                    p["price"] = q.get("price", p.get("price", 0))
                                if not p.get("chg_pct"):
                                    p["chg_pct"] = q.get("change_pct", p.get("chg_pct", 0))
                                if not p.get("pe_ttm"):
                                    p["pe_ttm"] = q.get("pe_ttm", p.get("pe_ttm", 0))
                                if not p.get("pb"):
                                    p["pb"] = q.get("pb", p.get("pb", 0))
                                if not p.get("mcap_yi"):
                                    p["mcap_yi"] = q.get("mcap_yi", p.get("mcap_yi", 0))
                        except Exception:
                            pass
            except Exception as _e:
                _debug_log(f"ful layer_ind ensure_full quote error: {_e}")
            return p

        all_peers = await asyncio.gather(*[_ensure_full(p) for p in all_peers])

        # 筛选有效同行
        peer_data = [p for p in all_peers if p.get("pe_ttm", 0) > 0 or p.get("mcap_yi", 0) > 0]
        if not peer_data:
            result["signals"].append("同行数据获取失败")
            return result

        result["peers"] = peer_data

        # 4. 统计汇总（PE/PB中位数）
        pe_vals = [p["pe_ttm"] for p in peer_data if p.get("pe_ttm", 0) > 0]
        pb_vals = [p["pb"] for p in peer_data if p.get("pb", 0) > 0]
        chg_vals = [p["chg_pct"] for p in peer_data if p.get("chg_pct") is not None]
        mcap_vals = [p["mcap_yi"] for p in peer_data if p.get("mcap_yi", 0) > 0]

        def _median(vals):
            if not vals:
                return 0
            sorted_vals = sorted(vals)
            n = len(sorted_vals)
            return sorted_vals[n // 2] if n % 2 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2

        result["peer_summary"] = {
            "count": len(peer_data),
            "pe_median": round(_median(pe_vals), 2),
            "pb_median": round(_median(pb_vals), 2),
            "chg_avg": round(sum(chg_vals) / len(chg_vals), 2) if chg_vals else 0,
            "mcap_avg_yi": round(sum(mcap_vals) / len(mcap_vals), 2) if mcap_vals else 0,
            "best_peers": sorted([p for p in peer_data if p.get("pe_ttm", 0) > 0],
                                 key=lambda p: p.get("pe_ttm", 9999))[:2],
            "worst_peers": sorted([p for p in peer_data if p.get("pe_ttm", 0) > 0],
                                  key=lambda p: -p.get("pe_ttm", 0))[:2],
        }

        # 5. 获取当前股票的PE/PB做对比（优先使用 data_provider）
        stock_pe = 0
        stock_pb = 0
        stock_chg = 0
        try:
            _dp_comp = await get_stock_composite_async(code)
            if _dp_comp:
                stock_pe = _dp_comp.get("pe_ttm", 0) or 0
                stock_pb = _dp_comp.get("pb", 0) or 0
                stock_chg = _dp_comp.get("change_pct", 0) or 0

            # V15.3: 用 cdata 强类型合约覆盖（push2 实时源更权威）
            try:
                _cd = await asyncio.to_thread(get_canonical_stock_data, code)
                if _cd is not None:
                    if _cd.pe_ttm > 0:
                        stock_pe = _cd.pe_ttm
                    if _cd.pb > 0:
                        stock_pb = _cd.pb
                    if _cd.change_pct != 0:
                        stock_chg = _cd.change_pct
            except Exception:
                pass

            # fallback 到 tdx
            if not stock_pe or not stock_pb:
                try:
                    q = await asyncio.to_thread(tdx_get_quote_full, code)
                    if q:
                        if not stock_pe:
                            stock_pe = q.get("pe_ttm", 0) or 0
                        if not stock_pb:
                            stock_pb = q.get("pb", 0) or 0
                        if not stock_chg and stock_chg == 0:
                            stock_chg = q.get("change_pct", 0) or 0
                except Exception:
                    pass
        except Exception as _e:
            _debug_log(f"ful layer_ind stock quote error: {_e}")

        ps = result["peer_summary"]
        if stock_pe > 0 and ps["pe_median"] > 0:
            pe_ratio = stock_pe / ps["pe_median"]
            ps["pe_vs_industry"] = round(pe_ratio, 2)
            if pe_ratio < 0.7:
                result["signals"].append(f"PE相对行业偏低 ({stock_pe:.1f} vs 行业中位{ps['pe_median']:.1f})，或被低估")
            elif pe_ratio > 1.5:
                result["signals"].append(f"PE相对行业偏高 ({stock_pe:.1f} vs 行业中位{ps['pe_median']:.1f})，或被高估")

        if stock_pb > 0 and ps["pb_median"] > 0:
            pb_ratio = stock_pb / ps["pb_median"]
            ps["pb_vs_industry"] = round(pb_ratio, 2)
            if pb_ratio < 0.7:
                result["signals"].append("PB相对行业偏低，具备防御价值")
            elif pb_ratio > 1.8:
                result["signals"].append("PB相对行业偏高，估值偏贵")

        if ps["chg_avg"] != 0:
            diff = stock_chg - ps["chg_avg"]
            ps["chg_vs_industry"] = round(diff, 2)
            if diff > 2:
                result["signals"].append(f"今日表现显著强于行业平均（超额收益 {diff:+.2f}%）")
            elif diff < -2:
                result["signals"].append(f"今日表现显著弱于行业平均（超额收益 {diff:+.2f}%）")

        return result

    except Exception as e:
        result["ok"] = False
        result["signals"].append(f"行业对比分析异常: {e}")
        return result


# =====================================================================
# Layer 3: 信号层（保留原实现）
# =====================================================================

def layer3_signals(code: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "ok": True, "dragon_tiger": [], "boards": {},
        "fund_flow": {}, "lockup": [], "signals": [],
    }

    try:
        start = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
        dt = eastmoney_datacenter(code, "RPT_DAILYBILLBOARD_DETAILSNEW",
            filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{start}')",
            page_size=30, sort_columns="TRADE_DATE", sort_types="-1")
        for row in dt:
            result["dragon_tiger"].append({
                "date": str(row.get("TRADE_DATE", ""))[:10],
                "reason": row.get("EXPLANATION", ""),
                "close": _safe_float(row.get("CLOSE_PRICE")),
                "chg_pct": _safe_float(row.get("CHANGE_RATE")),
                "net_buy_wan": round(_safe_float(row.get("BILLBOARD_NET_AMT")) / 10000, 1) if row.get("BILLBOARD_NET_AMT") else 0,
            })
        if result["dragon_tiger"]:
            result["signals"].append(f"近30日龙虎榜上榜 {len(result['dragon_tiger'])} 次")
    except Exception as _e:
        _debug_log(f"ful layer3 dragon tiger error: {_e}")

    try:
        boards = tdx_get_belong_boards(code)
        if boards:
            industries = boards.get("industry", []) or []
            concepts = boards.get("concept", []) or []
            areas = boards.get("area", []) or []
            result["boards"] = {
                "industry": [x.get("name", "") for x in industries[:3]],
                "concept": [x.get("name", "") for x in concepts[:10]],
                "area": [x.get("name", "") for x in areas[:2]],
            }
    except Exception as _e:
        _debug_log(f"ful layer3 boards error: {_e}")

    try:
        ff = tdx_get_fund_flow(code)
        if ff:
            main_net = ff.get("main_net_wan", 0)
            result["fund_flow"]["today"] = {
                "main_net_wan": main_net,
                "super_in": ff.get("super_in", 0),
                "large_in": ff.get("large_in", 0),
                "medium_in": ff.get("medium_in", 0),
                "small_in": ff.get("small_in", 0),
            }
            if main_net > 5000:
                result["signals"].append(f"主力净流入 {main_net/1e4:.2f} 亿元，资金显著关注")
            elif main_net > 1000:
                result["signals"].append(f"主力净流入 {main_net/1e4:.2f} 亿元，资金关注")
            elif main_net < -5000:
                result["signals"].append(f"⚠️ 主力净流出 {abs(main_net)/1e4:.2f} 亿元，资金大幅离场")
            elif main_net < -1000:
                result["signals"].append(f"⚠️ 主力净流出 {abs(main_net)/1e4:.2f} 亿元，资金离场")

        hff = tdx_get_history_fund_flow(code, 30)
        if hff:
            recent_20 = hff[-20:]
            if recent_20:
                total_net = sum(_safe_float(d.get("main_net")) for d in recent_20)
                pos_days = sum(1 for d in recent_20 if _safe_float(d.get("main_net")) > 0)
                result["fund_flow"]["recent_20d"] = {
                    "total_net_wan": round(total_net / 10000, 1),
                    "positive_days": pos_days,
                    "total_days": len(recent_20),
                }
                if pos_days >= 15:
                    result["signals"].append(f"近20日主力净买入 {pos_days} 天，持续资金流入")
                elif pos_days <= 5:
                    result["signals"].append(f"⚠️ 近20日主力净买入仅 {pos_days} 天，资金持续流出")
    except Exception as _e:
        _debug_log(f"ful layer3 fund flow error: {_e}")

    try:
        end = (date.today() + timedelta(days=90)).strftime("%Y-%m-%d")
        today_s = date.today().strftime("%Y-%m-%d")
        ld = eastmoney_datacenter(code, "RPT_LIFT_STAGE",
            filter_str=f"(SECURITY_CODE=\"{code}\")(FREE_DATE>='{today_s}')(FREE_DATE<='{end}')",
            page_size=10, sort_columns="FREE_DATE", sort_types="1")
        for row in ld:
            shares = _safe_float(row.get("FREE_SHARES"))
            ratio = _safe_float(row.get("FREE_RATIO"))
            result["lockup"].append({
                "date": str(row.get("FREE_DATE", ""))[:10],
                "type": row.get("FREE_SHARES_TYPE", ""),
                "shares": shares, "ratio": ratio,
            })
        if result["lockup"]:
            next_lk = result["lockup"][0]
            if next_lk.get("ratio", 0) > 10:
                result["signals"].append(
                    f"⚠️ {next_lk['date']} 解禁 {next_lk.get('ratio', 0):.1f}%，规模较大需重点关注")
            elif next_lk.get("ratio", 0) > 3:
                result["signals"].append(
                    f"⚠️ {next_lk['date']} 有解禁 {next_lk.get('ratio', 0):.1f}%")
    except Exception as _e:
        _debug_log(f"ful layer3 lockup error: {_e}")

    return result


# =====================================================================
# Layer 4: 筹码/资金结构层（保留原实现）
# =====================================================================

def layer4_chips(code: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "ok": True, "holder_trend": [], "margin": [],
        "block_trade": [], "holder_structure": None, "signals": [],
    }

    try:
        holders = holder_change(code)
        if holders:
            result["holder_trend"] = holders[:6]
            if len(holders) >= 2:
                latest_chg = holders[0].get("change_ratio", 0)
                prev_chg = holders[1].get("change_ratio", 0)
                if latest_chg < 0 and prev_chg < 0:
                    result["signals"].append(
                        f"股东户数连续两季缩减（{holders[1]['date']}: {prev_chg:.1f}% → "
                        f"{holders[0]['date']}: {latest_chg:.1f}%），筹码集中")
                elif latest_chg > 10:
                    result["signals"].append(
                        f"⚠️ 股东户数环比 +{latest_chg:.1f}%，筹码显著分散")
    except Exception as _e:
        _debug_log(f"ful layer4 holder trend error: {_e}")

    try:
        md = eastmoney_datacenter(code, "RPTA_WEB_RZRQ_GGMX",
            filter_str=f'(SCODE="{code}")', page_size=15,
            sort_columns="DATE", sort_types="-1")
        for row in md:
            result["margin"].append({
                "date": str(row.get("DATE", ""))[:10],
                "rzye_wan": round(_safe_float(row.get("RZYE")) / 10000, 1) if row.get("RZYE") else 0,
                "rzmre_wan": round(_safe_float(row.get("RZMRE")) / 10000, 1) if row.get("RZMRE") else 0,
                "rqye_wan": round(_safe_float(row.get("RQYE")) / 10000, 1) if row.get("RQYE") else 0,
            })
        if len(result["margin"]) >= 5:
            latest_m = result["margin"][0]["rzye_wan"]
            avg_m = sum(r["rzye_wan"] for r in result["margin"][:5]) / 5
            if avg_m > 0:
                chg = (latest_m - avg_m) / avg_m * 100
                if abs(chg) > 15:
                    result["signals"].append(
                        f"融资余额较近5日均 {'上升' if chg > 0 else '下降'} {abs(chg):.1f}%")
    except Exception as _e:
        _debug_log(f"ful layer4 margin error: {_e}")

    try:
        bt = _em_filter(code, "RPT_DATA_BLOCKTRADE", page_size=15,
                         sort_columns="TRADE_DATE", sort_types="-1")
        for row in bt:
            close = _safe_float(row.get("CLOSE_PRICE"))
            dp = _safe_float(row.get("DEAL_PRICE"))
            premium = (dp / close - 1) * 100 if close else 0
            result["block_trade"].append({
                "date": str(row.get("TRADE_DATE", ""))[:10],
                "deal_price": dp, "close": close,
                "premium_pct": round(premium, 2),
                "amount_wan": round(_safe_float(row.get("DEAL_AMT")) / 10000, 1) if row.get("DEAL_AMT") else 0,
                "buyer": str(row.get("BUYER_NAME", ""))[:30],
                "seller": str(row.get("SELLER_NAME", ""))[:30],
            })
        if result["block_trade"] and result["block_trade"][0].get("premium_pct", 0) < -8:
            result["signals"].append(
                f"⚠️ 最近大宗交易折价 {result['block_trade'][0]['premium_pct']:.1f}%")
    except Exception as _e:
        _debug_log(f"ful layer4 block trade error: {_e}")

    try:
        hs = get_holder_structure(code)
        if hs:
            result["holder_structure"] = hs[:3]
            latest = hs[0]
            nb = latest.get("northbound", 0)
            if nb > 8:
                result["signals"].append(f"北向资金持股占比 {nb:.1f}%，外资重仓")
            elif nb > 3:
                result["signals"].append(f"北向资金持股 {nb:.1f}%，外资关注")
            dm_count = latest.get("domestic_count", 0)
            if dm_count >= 10:
                result["signals"].append(f"十大流通股东中机构席位 {dm_count} 家，机构高度集中")
            elif dm_count >= 5:
                result["signals"].append(f"十大流通股东中机构 {dm_count} 家")
    except Exception as _e:
        _debug_log(f"ful layer4 holder structure error: {_e}")

    return result


# =====================================================================
# Layer 5: 新闻层（保留原实现）
# =====================================================================

def layer5_news(code: str, stock_name: str = "") -> Dict[str, Any]:
    """Layer 5: 新闻与舆情 — 东财个股新闻 + 财联社快讯 + 互动易 + 同花顺热榜"""
    result: Dict[str, Any] = {
        "ok": True, "global_related": [],
        "cls_news": [], "irm_qa": [],
        "hot_list": [], "signals": [],
    }

    # 东财个股新闻（已按股票代码过滤，直接显示）
    try:
        stock_news = get_eastmoney_stock_news(code, page_size=30)
        for item in stock_news:
            title = str(item.get("title", "")).strip()
            summary = str(item.get("summary", "")).strip()
            if title:
                result["global_related"].append({
                    "time": str(item.get("publish_time", ""))[:16],
                    "title": title[:80],
                    "summary": summary[:120],
                })
    except Exception as _e:
        _debug_log(f"ful layer5 stock news error: {_e}")

    # 财联社快讯（近3天）
    try:
        cls_data = cls_telegraph(page_size=50)
        _cls_cutoff = datetime.now() - timedelta(days=3)
        for item in cls_data:
            t_str = str(item.get("time", ""))
            if t_str:
                try:
                    pub_dt = datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
                    if pub_dt < _cls_cutoff:
                        continue
                except (ValueError, TypeError):
                    pass
            title = str(item.get("title", "")).strip()
            if title:
                result["cls_news"].append({
                    "time": t_str[:16],
                    "title": title[:80],
                })
                if len(result["cls_news"]) >= 15:
                    break
    except Exception as _e:
        _debug_log(f"ful layer5 cls_telegraph error: {_e}")

    # 互动易问答（近15天）
    try:
        irm_data = cninfo_irm(code, page_size=30)
        _irm_cutoff = datetime.now() - timedelta(days=15)
        for item in irm_data:
            t_str = str(item.get("ask_time", ""))
            if t_str:
                try:
                    pub_dt = datetime.strptime(t_str, "%Y-%m-%d %H:%M")
                    if pub_dt < _irm_cutoff:
                        continue
                except (ValueError, TypeError):
                    pass
            q = str(item.get("question", "")).strip()[:80]
            if q:
                result["irm_qa"].append({
                    "time": t_str[:16],
                    "question": q,
                })
                if len(result["irm_qa"]) >= 10:
                    break
    except Exception as _e:
        _debug_log(f"ful layer5 cninfo_irm error: {_e}")

    # 同花顺热榜（取当前热度前5，看该股是否在榜）
    try:
        hot_all = ths_hot_list("hour")
        for h in hot_all[:5]:
            if h.get("code") == code or h.get("name") in stock_name:
                result["hot_list"].append(h)
                break
    except Exception as _e:
        _debug_log(f"ful layer5 hot list error: {_e}")

    total_related = len(result["global_related"])
    if total_related > 5:
        result["signals"].append(f"📢 近期相关新闻 {total_related} 条，市场关注度较高")
    if result["hot_list"]:
        result["signals"].append(f"🔥 该股当前在同花顺热榜 #{result['hot_list'][0]['rank']}，热度 {result['hot_list'][0]['heat']}")

    return result


# =====================================================================
# Layer 6: 基本面（保留原实现 + 增强ROE/分红字段）
# =====================================================================

async def layer6_fundamental(code: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "ok": True, "financials": [], "balance_sheet": [],
        "ratios": {}, "dividends": [], "historical_high": None,
        "signals": [],
    }

    try:
        prefix = "sh" if code.startswith("6") else "sz"
        paper_code = f"{prefix}{code}"
        url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
        r = _quick_request(url, params={
            "paperCode": paper_code, "source": "lrb",
            "type": "0", "page": "1", "num": "12",
        }, headers={"User-Agent": UA}, timeout=15)
        if r is not None:
            rl = (r.json().get("result") or {}).get("data", {}).get("report_list", {})
            rows = []
            for date_key, period in rl.items():
                item_map = {}
                for entry in period.get("data", []):
                    item_map[entry.get("item_title", "")] = entry.get("item_value")
                rows.append({
                    "date": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}",
                    "revenue_yi": _safe_float(item_map.get("营业总收入")) / 1e8 if item_map.get("营业总收入") else 0,
                    "profit_yi": _safe_float(item_map.get("归属于母公司所有者的净利润") or item_map.get("净利润")) / 1e8 if item_map.get("归属于母公司所有者的净利润") or item_map.get("净利润") else 0,
                })
            result["financials"] = rows

            if len(rows) >= 5:
                latest = rows[0]
                last_year_same = None
                for r in rows[1:]:
                    if r["date"][5:10] == latest["date"][5:10]:
                        last_year_same = r
                        break
                if last_year_same and last_year_same["profit_yi"] > 0:
                    rev_yoy = (latest["revenue_yi"] - last_year_same["revenue_yi"]) / last_year_same["revenue_yi"] * 100 if last_year_same["revenue_yi"] else 0
                    profit_yoy = (latest["profit_yi"] - last_year_same["profit_yi"]) / last_year_same["profit_yi"] * 100
                    result["ratios"]["revenue_yoy"] = round(rev_yoy, 2)
                    result["ratios"]["profit_yoy"] = round(profit_yoy, 2)

                    if profit_yoy > 30:
                        result["signals"].append(f"利润同比 +{profit_yoy:.1f}%，高速成长")
                    elif profit_yoy > 10:
                        result["signals"].append(f"利润同比 +{profit_yoy:.1f}%，稳健增长")
                    elif profit_yoy < -20:
                        result["signals"].append(f"⚠️ 利润同比 {profit_yoy:.1f}%，业绩下滑")
                    elif profit_yoy < 0:
                        result["signals"].append(f"⚠️ 利润同比 {profit_yoy:.1f}%，业绩承压")

            # 连续亏损判断
            if len(rows) >= 4:
                latest_4 = [r for r in rows[:4] if r["date"]]
                if len(latest_4) >= 2:
                    if all(r.get("profit_yi", 0) < 0 for r in latest_4[:2]):
                        result["signals"].append("⚠️ 最近两期连续亏损，警惕退市风险")
    except Exception as _e:
        _debug_log(f"ful layer6 financials error: {_e}")

    try:
        prefix = "sh" if code.startswith("6") else "sz"
        paper_code = f"{prefix}{code}"
        url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
        r = _quick_request(url, params={
            "paperCode": paper_code, "source": "fzb",
            "type": "0", "page": "1", "num": "2",
        }, headers={"User-Agent": UA}, timeout=15)
        if r is not None:
            rl = (r.json().get("result") or {}).get("data", {}).get("report_list", {})
            for date_key, period in rl.items():
                item_map = {}
                for entry in period.get("data", []):
                    item_map[entry.get("item_title", "")] = entry.get("item_value")
                total_assets = _safe_float(item_map.get("资产总计"))
                total_liab = _safe_float(item_map.get("负债合计"))
                equity = _safe_float(item_map.get("归属于母公司股东权益合计"))
                goodwill = _safe_float(item_map.get("商誉"))
                cash = _safe_float(item_map.get("货币资金"))
                short_loan = _safe_float(item_map.get("短期借款"))
                ar = _safe_float(item_map.get("应收账款"))
                inventory = _safe_float(item_map.get("存货"))

                debt_ratio = round(total_liab / total_assets * 100, 2) if total_assets else 0
                gw_ratio = round(goodwill / equity * 100, 2) if equity else 0
                cash_debt_ratio = round(cash / short_loan, 2) if short_loan else 0
                ar_ratio = round(ar / total_assets * 100, 2) if total_assets else 0
                inv_ratio = round(inventory / total_assets * 100, 2) if total_assets else 0

                result["balance_sheet"].append({
                    "date": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}",
                    "total_assets_yi": round(total_assets / 1e8, 2) if total_assets else 0,
                    "equity_yi": round(equity / 1e8, 2) if equity else 0,
                    "debt_ratio": debt_ratio, "gw_ratio": gw_ratio,
                    "cash_yi": round(cash / 1e8, 2) if cash else 0,
                    "short_loan_yi": round(short_loan / 1e8, 2) if short_loan else 0,
                    "cash_debt_ratio": cash_debt_ratio,
                    "ar_ratio": ar_ratio, "inv_ratio": inv_ratio,
                })

                if debt_ratio > 70:
                    result["signals"].append(f"⚠️ 资产负债率 {debt_ratio:.1f}%，杠杆偏高")
                elif debt_ratio > 50:
                    result["signals"].append(f"资产负债率 {debt_ratio:.1f}%，中杠杆")
                if gw_ratio > 30:
                    result["signals"].append(f"⚠️ 商誉/净资产 {gw_ratio:.1f}%，减值风险高")
                elif gw_ratio > 15:
                    result["signals"].append(f"商誉/净资产 {gw_ratio:.1f}%，需关注")
                if ar_ratio > 25:
                    result["signals"].append(f"⚠️ 应收账款/总资产 {ar_ratio:.1f}%，回款风险高")
                if inv_ratio > 30:
                    result["signals"].append(f"⚠️ 存货/总资产 {inv_ratio:.1f}%，库存积压风险")
                if short_loan and cash_debt_ratio < 0.5:
                    result["signals"].append(f"⚠️ 现金/短债 {cash_debt_ratio:.2f}，短期偿债承压")
                break
    except Exception as _e:
        _debug_log(f"ful layer6 balance sheet error: {_e}")

    # ROE 年化
    if result["financials"] and result["balance_sheet"]:
        profit = result["financials"][0].get("profit_yi", 0) * 1e8
        date_str = result["financials"][0].get("date", "")
        month = int(date_str[5:7]) if len(date_str) >= 7 and date_str[5:7].isdigit() else 12
        annualize_factor = 1
        if month == 3:
            annualize_factor = 4
        elif month == 6:
            annualize_factor = 2
        elif month == 9:
            annualize_factor = 4 / 3

        bs = result["balance_sheet"][0] if result["balance_sheet"] else {}
        equity = bs.get("equity_yi", 0) * 1e8
        if equity > 0 and profit:
            roe = round(profit * annualize_factor / equity * 100, 2)
            result["ratios"]["roe_annualized"] = roe
            if roe >= 20:
                result["signals"].append(f"年化ROE {roe:.1f}%，优质盈利能力")
            elif roe >= 10:
                result["signals"].append(f"年化ROE {roe:.1f}%，盈利能力良好")
            elif roe < 3:
                result["signals"].append(f"⚠️ 年化ROE {roe:.1f}%，盈利偏弱")

    # 分红历史
    try:
        # V10.1: 股息率优先用zhb数据，无zhb时fallback到tdx_get_dividend_history计算
        _zhb_div_yield = 0
        if _zhb_data:
            _zhb_div_yield = _zhb_data.get("dividend_yield", 0)
        if _zhb_div_yield and _zhb_div_yield > 0:
            result["ratios"]["dividend_yield"] = _zhb_div_yield
            if _zhb_div_yield > 5:
                result["signals"].append(f"股息率 {_zhb_div_yield:.2f}%，高股息标的")
            elif _zhb_div_yield > 3:
                result["signals"].append(f"股息率 {_zhb_div_yield:.2f}%，可作中长线配置")
        # 仍获取分红明细记录用于展示
        divs = tdx_get_dividend_history(code)
        if divs:
            result["dividends"] = divs[:5]
            if not _zhb_div_yield or _zhb_div_yield <= 0:
                try:
                    price = await get_stock_price_async(code) or 0
                except Exception:
                    price = 0
                latest_div = divs[0].get("bonus_rmb", 0) if divs else 0
                if price > 0 and latest_div > 0:
                    yield_rate = round(latest_div / price * 100, 2)
                    result["ratios"]["dividend_yield"] = yield_rate
                    if yield_rate > 5:
                        result["signals"].append(f"股息率 {yield_rate:.2f}%，高股息标的")
                    elif yield_rate > 3:
                        result["signals"].append(f"股息率 {yield_rate:.2f}%，可作中长线配置")
    except Exception as _e:
        _debug_log(f"ful layer6 dividends error: {_e}")

    # 历史高位
    try:
        hh = tdx_get_historical_high(code)
        if hh:
            result["historical_high"] = hh
            try:
                price = await get_stock_price_async(code) or 0
            except Exception:
                price = 0
            if hh > 0 and price > 0:
                pct_from_high = round((price / hh - 1) * 100, 2)
                result["ratios"]["pct_from_high"] = pct_from_high
                if pct_from_high < -60:
                    result["signals"].append(f"距历史高点 {pct_from_high:.1f}%，深度回撤")
                elif pct_from_high < -30:
                    result["signals"].append(f"距历史高点 {pct_from_high:.1f}%，已明显回撤")
    except Exception as _e:
        _debug_log(f"ful layer6 historical high error: {_e}")

    return result


# =====================================================================
# Layer_RISK: 风险扫描（方案3新增）
# =====================================================================

async def layer_risk(code: str, layers_ref: Optional[Dict] = None) -> Dict[str, Any]:
    """
    综合风险扫描：汇总层6的资产健康度 + 公告关键词风险 + 解禁风险 +
    质押风险 + 股东减持风险。
    输出每项风险等级（低/中/高）+ 描述，以及综合风险评分（0~100，越高风险越高）。
    """
    result: Dict[str, Any] = {
        "ok": True, "items": [], "risk_score": 30, "signals": [],
    }

    # 从已有层提取补充信息（如已计算的 debt_ratio / gw_ratio / pct_from_high）
    extra_l6 = {}
    if layers_ref and "layer6" in layers_ref:
        l6 = layers_ref["layer6"] or {}
        bs = (l6.get("balance_sheet") or [{}])[0] if l6.get("balance_sheet") else {}
        extra_l6 = {
            "debt_ratio": bs.get("debt_ratio", 0),
            "gw_ratio": bs.get("gw_ratio", 0),
            "ar_ratio": bs.get("ar_ratio", 0),
            "inv_ratio": bs.get("inv_ratio", 0),
            "cash_debt_ratio": bs.get("cash_debt_ratio", 0),
            "roe_annualized": (l6.get("ratios") or {}).get("roe_annualized", 0),
            "profit_yoy": (l6.get("ratios") or {}).get("profit_yoy", 0),
            "dividend_yield": (l6.get("ratios") or {}).get("dividend_yield", 0),
            "pct_from_high": (l6.get("ratios") or {}).get("pct_from_high", 0),
        }
    else:
        # V15.2 修正: 复用 L360 的 cdata，避免重复调 get_pe_ttm_async/get_pb_async 触发冗余 zhb_data 缓存
        try:
            if cdata and cdata.pe_ttm:
                extra_l6["pe_ttm"] = cdata.pe_ttm
            if cdata and cdata.pb:
                extra_l6["pb"] = cdata.pb
        except Exception as _e:
            _debug_log(f"ful layer_risk cdata quote error: {_e}")

    # 1) 资产负债健康
    dr = extra_l6.get("debt_ratio", 0)
    if dr > 75:
        result["items"].append({"name": "资产负债率", "level": "高", "score": 15, "text": f"{dr:.1f}%，杠杆过高"})
        result["risk_score"] += 15
    elif dr > 55:
        result["items"].append({"name": "资产负债率", "level": "中", "score": 8, "text": f"{dr:.1f}%，中等杠杆"})
        result["risk_score"] += 8
    else:
        result["items"].append({"name": "资产负债率", "level": "低", "score": 2, "text": f"{dr:.1f}%，稳健"})

    # 2) 商誉/净资产
    gw = extra_l6.get("gw_ratio", 0)
    if gw > 30:
        result["items"].append({"name": "商誉风险", "level": "高", "score": 12, "text": f"商誉占净资产 {gw:.1f}%，减值风险高"})
        result["risk_score"] += 12
    elif gw > 15:
        result["items"].append({"name": "商誉风险", "level": "中", "score": 6, "text": f"商誉占净资产 {gw:.1f}%，需关注"})
        result["risk_score"] += 6
    else:
        result["items"].append({"name": "商誉风险", "level": "低", "score": 1, "text": f"商誉 {gw:.1f}%，风险低"})

    # 3) 应收账款
    ar = extra_l6.get("ar_ratio", 0)
    if ar > 25:
        result["items"].append({"name": "应收账款", "level": "高", "score": 10, "text": f"应收账款/总资产 {ar:.1f}%，回款风险高"})
        result["risk_score"] += 10
    elif ar > 15:
        result["items"].append({"name": "应收账款", "level": "中", "score": 5, "text": f"应收账款/总资产 {ar:.1f}%，需关注"})
        result["risk_score"] += 5
    else:
        result["items"].append({"name": "应收账款", "level": "低", "score": 1, "text": f"应收账款占比 {ar:.1f}%，健康"})

    # 4) 盈利能力（ROE/利润增速可作为"加分项"反向扣减风险）
    roe = extra_l6.get("roe_annualized", 0)
    profit_yoy = extra_l6.get("profit_yoy", 0)
    if roe < 3:
        result["items"].append({"name": "盈利质量", "level": "高", "score": 10, "text": f"ROE {roe:.1f}%，盈利能力偏弱"})
        result["risk_score"] += 10
    elif roe >= 15:
        result["items"].append({"name": "盈利质量", "level": "低", "score": 0, "text": f"ROE {roe:.1f}%，优质"})
    else:
        result["items"].append({"name": "盈利质量", "level": "低", "score": 2, "text": f"ROE {roe:.1f}%，一般"})

    if profit_yoy < -20:
        result["items"].append({"name": "业绩趋势", "level": "高", "score": 12, "text": f"利润同比 {profit_yoy:.1f}%，业绩下滑"})
        result["risk_score"] += 12
    elif profit_yoy > 10:
        result["items"].append({"name": "业绩趋势", "level": "低", "score": 0, "text": f"利润同比 +{profit_yoy:.1f}%，成长"})

    # 5) 质押风险（尝试通过东财简单关键词查询"质押率"）
    try:
        import uuid
        # 通过东财公告API简单查询含"质押"关键词的近期公告条数
        url = "https://np-weblist.eastmoney.com/comm/web/getFastNewsList"
        r = _request_with_retry(url, params={
            "client": "web", "biz": "web_724", "fastColumn": "102",
            "sortEnd": "", "pageSize": "10", "req_trace": str(uuid.uuid4()),
        }, headers={"User-Agent": UA, "Referer": "https://kuaixun.eastmoney.com/"}, timeout=8)
        pledge_hit = 0
        if r is not None:
            items = r.json().get("data", {}).get("fastNewsList", []) or []
            for it in items:
                txt = (str(it.get("title", "")) + " " + str(it.get("summary", "")))
                if code in txt or "股权质押" in txt or "质押" in txt:
                    pledge_hit += 1
        if pledge_hit >= 2:
            result["items"].append({"name": "股权质押", "level": "中", "score": 8, "text": f"近一段时间质押相关资讯 {pledge_hit} 条，需关注"})
            result["risk_score"] += 8
        elif pledge_hit == 1:
            result["items"].append({"name": "股权质押", "level": "低", "score": 3, "text": "有质押相关资讯 1 条"})
        else:
            result["items"].append({"name": "股权质押", "level": "低", "score": 1, "text": "近期无明显质押相关资讯"})
    except Exception as _e:
        _debug_log(f"ful risk_pledge: {_e}")
        result["items"].append({"name": "股权质押", "level": "低", "score": 3, "text": "查询异常，默认无数据"})

    # 6) 股东减持（通过公告关键词）
    try:
        ann = get_strategic_announcements(code, page_size=20, days=90)
        if ann:
            titles = " ".join(a.get("title", "") for a in ann)
            reduce_hit = sum(1 for t in titles.split() if "减持" in t or "减" in t)
            if "董事" in titles and "减持" in titles:
                result["items"].append({"name": "股东减持", "level": "高", "score": 12, "text": "董事/高管有减持公告，需重点关注"})
                result["risk_score"] += 12
            elif "减持" in titles:
                result["items"].append({"name": "股东减持", "level": "中", "score": 6, "text": "有股东减持公告"})
                result["risk_score"] += 6
            elif "增持" in titles:
                result["items"].append({"name": "股东增持", "level": "低", "score": 0, "text": "有股东增持公告"})
            else:
                result["items"].append({"name": "股东增减持", "level": "低", "score": 1, "text": "近90日无增减持公告"})
        else:
            result["items"].append({"name": "股东增减持", "level": "低", "score": 1, "text": "近90日无相关公告"})
    except Exception as _e:
        _debug_log(f"ful risk_holder_change: {_e}")
        result["items"].append({"name": "股东增减持", "level": "低", "score": 1, "text": "查询异常"})

    # 7) 解禁压力（如已在layer3计算，直接复用）
    if layers_ref and "layer3" in layers_ref:
        l3 = layers_ref["layer3"] or {}
        if l3.get("lockup"):
            lk = l3["lockup"][0]
            ratio = lk.get("ratio", 0)
            if ratio > 10:
                result["items"].append({"name": "限售解禁", "level": "高", "score": 12, "text": f"{lk['date']} 解禁 {ratio:.1f}%"})
                result["risk_score"] += 12
            elif ratio > 3:
                result["items"].append({"name": "限售解禁", "level": "中", "score": 6, "text": f"{lk['date']} 解禁 {ratio:.1f}%"})
                result["risk_score"] += 6
            else:
                result["items"].append({"name": "限售解禁", "level": "低", "score": 1, "text": f"{lk['date']} 解禁 {ratio:.1f}%，影响有限"})
        else:
            result["items"].append({"name": "限售解禁", "level": "低", "score": 0, "text": "未来90日无解禁"})

    # 8) 资金面（主力流出/筹码分散作为风险项）
    if layers_ref and "layer4" in layers_ref:
        l4 = layers_ref["layer4"] or {}
        risk_msgs = []
        for s in (l4.get("signals") or []):
            if "离场" in s or "分散" in s:
                risk_msgs.append(s)
        if risk_msgs:
            result["items"].append({"name": "资金流向", "level": "中", "score": 8, "text": "; ".join(risk_msgs)})
            result["risk_score"] += 8
        else:
            result["items"].append({"name": "资金流向", "level": "低", "score": 2, "text": "资金面平稳"})

    # 综合风险评级
    rs = min(100, int(result["risk_score"]))
    if rs >= 70:
        result["signals"].append(f"⚠️ 综合风险评分 {rs}/100，多项风险叠加，建议谨慎")
    elif rs >= 40:
        result["signals"].append(f"综合风险评分 {rs}/100，中等风险，需关注相关风险项")
    else:
        result["signals"].append(f"综合风险评分 {rs}/100，风险可控")

    return result


# =====================================================================
# Layer 7: 公告层
# =====================================================================

def layer7_announcements(code: str, stock_name: str = "") -> Dict[str, Any]:
    result: Dict[str, Any] = {"ok": True, "announcements": [], "signals": []}

    try:
        anns = get_strategic_announcements(code, page_size=30, days=90)
        if anns:
            for a in anns:
                result["announcements"].append({
                    "title": str(a.get("title", "")).strip(),
                    "date": str(a.get("date", ""))[:10],
                    "type": str(a.get("type", "")).strip(),
                })
            titles = " ".join(a["title"] for a in result["announcements"])
            if "减持" in titles:
                result["signals"].append("⚠️ 有股东减持公告")
            if "回购" in titles:
                result["signals"].append("✅ 有回购公告")
            if "业绩预告" in titles:
                result["signals"].append("📊 有业绩预告")
            if "分红" in titles:
                result["signals"].append("💰 有分红派息公告")
            if "激励" in titles:
                result["signals"].append("🎯 有股权激励计划")
            if "严重异动" in titles:
                result["signals"].append("⚠️ 严重异动公告")
    except Exception as _e:
        _debug_log(f"ful layer7 announcements error: {_e}")

    return result


# =====================================================================
# 报告格式化 & 六维加权综合评分
# =====================================================================

def _scoring(layers: Dict[str, Any], _cfg_sc: Dict = None) -> Dict[str, float]:
    """
    V8.2: 使用统一评分接口计算六维评分
    基于各层数据计算六个维度的评分（0~100）：
    技术面/估值面/基本面/资金面/筹码面/分红面 六维加权综合评分
    """
    from stock_common import calculate_score as _calc_score
    
    # 从 layers 中提取数据构建 ScoreData
    l1 = layers.get("layer1") or {}
    l2 = layers.get("layer2") or {}
    l3 = layers.get("layer3") or {}
    l4 = layers.get("layer4") or {}
    l5 = layers.get("layer5") or {}
    l6 = layers.get("layer6") or {}
    li = layers.get("layer_ind") or {}
    
    kline = l1.get("kline") or {}
    tech = l1.get("tech") or {}
    val = l2.get("valuation") or {}
    ff = l3.get("fund_flow") or {}
    hs = (l4.get("holder_structure") or [{}])[0] if l4.get("holder_structure") else {}
    ht = l4.get("holder_trend") or []
    ratios6 = l6.get("ratios") or {}
    bs = (l6.get("balance_sheet") or [{}])[0]
    ps = li.get("peer_summary") or {}
    
    # 构建 ScoreData 对象
    data = ScoreData(
        code=layers.get("code", ""),
        name=layers.get("name", ""),
        price=kline.get("price", 0),
        change_pct=kline.get("change_pct", 0),
        # 技术面
        ma5=kline.get("ma5", 0),
        ma10=kline.get("ma10", 0),
        ma20=kline.get("ma20", 0),
        ret_20d=kline.get("ret_20d", 0),
        high_120d=kline.get("high_120d", 0),
        # MACD/RSI/KDJ
        macd_dif=tech.get("macd", {}).get("dif", 0) if isinstance(tech.get("macd"), dict) else 0,
        macd_dea=tech.get("macd", {}).get("dea", 0) if isinstance(tech.get("macd"), dict) else 0,
        rsi14=tech.get("rsi", {}).get("rsi14", 50) if isinstance(tech.get("rsi"), dict) else 50,
        kdj_k=tech.get("kdj", {}).get("k", 50) if isinstance(tech.get("kdj"), dict) else 50,
        kdj_d=tech.get("kdj", {}).get("d", 50) if isinstance(tech.get("kdj"), dict) else 50,
        kdj_j=tech.get("kdj", {}).get("j", 50) if isinstance(tech.get("kdj"), dict) else 50,
        boll_pos=tech.get("boll", {}).get("pos_pct", 50) if isinstance(tech.get("boll"), dict) else 50,
        volume_ratio=tech.get("volume", {}).get("ratio", 1) if isinstance(tech.get("volume"), dict) else 1,
        # 基本面
        roe=ratios6.get("roe_annualized", 0),
        gross_margin=ratios6.get("gross_margin", 0),
        net_profit_margin=ratios6.get("net_margin", 0),
        asset_liability_ratio=(bs.get("debt_ratio", 0) / 100) if isinstance(bs, dict) else 0,
        # 估值
        pe_ttm=val.get("pe_ttm", 0),
        pb=val.get("pb", 0),
        forward_pe=val.get("forward_pe", 0),
        industry_pe=ps.get("industry_pe", 0) if isinstance(ps, dict) else 0,
        # 资金面
        main_net_inflow=(ff.get("today") or {}).get("main_net_wan", 0) * 10000 if isinstance(ff.get("today"), dict) else 0,
        consecutive_inflow_days=(ff.get("recent_20d") or {}).get("positive_days", 0) if isinstance(ff.get("recent_20d"), dict) else 0,
        northbound_change=hs.get("northbound", 0) if isinstance(hs, dict) else 0,
        institution_holding_pct=hs.get("domestic", 0) if isinstance(hs, dict) else 0,
        # 筹码
        holder_change_ratio=ht[0].get("change_ratio", 0) if ht and isinstance(ht, list) else 0,
        # 分红
        dividend_yield=ratios6.get("dividend_yield", 0),
    )
    
    # 调用统一评分接口
    result = _calc_score("ful", data, _cfg_sc)
    
    # 返回六维评分
    dims = result.dimensions
    return {
        "technical": round(dims.get("technical", 50), 1),
        "valuation": round(dims.get("valuation", 50), 1),
        "fundamental": round(dims.get("fundamental", 50), 1),
        "flow": round(dims.get("flow", 50), 1),
        "holder": round(dims.get("holder", 50), 1),
        "dividend": round(dims.get("dividend", 50), 1),
        "total": round(result.total_score, 1),
    }


def format_report(code: str, layers: Dict[str, Any]) -> str:
    """将8层数据格式化为可读报告"""
    lines: List[str] = []
    L = lines.append
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _mkt_status, _mkt_note = get_market_status()

    L("═" * 78)
    L("  个股七层全维度分析报告")
    L(f"  股票代码: {code}")
    L(f"  生成时间: {now}")
    if _mkt_status == "closed":
        L("  ⚠️ 休市日：数据为最近交易日快照，实时行情已标注")
    elif _mkt_status == "lunch":
        L("  ⚠️ 午休时段（11:30-13:00）：行情暂停但基本面数据正常")
    elif _mkt_status in ("post_market", "pre_market"):
        L("  ⚠️ 非交易时段：数据为最近交易日快照，实时行情已标注")
    elif _mkt_status == "post_close":
        L("  ℹ️ 盘后收盘：数据为今日收盘快照，实时行情已标注")
    L("═" * 78)

    # 基本信息
    l1 = layers.get("layer1") or {}
    basic = l1.get("basic") or {}
    if basic:
        L("")
        L(f"  股票名称: {basic.get('name', '')}")
        L(f"  当前价: ¥{_fmt_num(basic.get('price'))}    "
          f"涨跌幅: {_fmt_pct(basic.get('change_pct'))}    "
          f"振幅: {_fmt_num(basic.get('amplitude'))}%")
        L(f"  PE(TTM): {_fmt_num(basic.get('pe_ttm'))}    "
          f"PB: {_fmt_num(basic.get('pb'))}    "
          f"总市值: {_fmt_num(basic.get('mcap_yi'))} 亿")
        L(f"  换手率: {_fmt_num(basic.get('turnover_pct'))}%    "
          f"流通市值: {_fmt_num(basic.get('float_mcap_yi'))} 亿")
        if basic.get("limit_up_price"):
            L(f"  涨停价: ¥{_fmt_num(basic.get('limit_up_price'))}    "
              f"跌停价: ¥{_fmt_num(basic.get('limit_down_price'))}")

    # 相对指数收益
    if l1.get("index_compare"):
        ic = l1["index_compare"]
        if isinstance(ic, dict):
            L(f"  vs {ic.get('index_name', '')}: 个股 {_fmt_pct(ic.get('index_chg'))}  "
              f"超额收益: {_fmt_pct(ic.get('stock_minus_index'))}")

    # ── Layer1 技术分析详情
    if l1.get("ok"):
        kl = l1.get("kline") or {}
        tech = l1.get("tech") or {}
        L("")
        L(f"{'─'*36}  1. 行情与技术分析  {'─'*26}")
        if isinstance(kl, dict) and kl.get("price"):
            L(f"  MA5: ¥{_fmt_num(kl.get('ma5'))}   MA10: ¥{_fmt_num(kl.get('ma10'))}   "
              f"MA20: ¥{_fmt_num(kl.get('ma20'))}   MA60: ¥{_fmt_num(kl.get('ma60'))}")
            L(f"  120日最高: ¥{_fmt_num(kl.get('high_120d'))}   "
              f"120日最低: ¥{_fmt_num(kl.get('low_120d'))}   "
              f"近20日: {_fmt_pct(kl.get('ret_20d'))}   "
              f"近60日: {_fmt_pct(kl.get('ret_60d'))}")

            # ASCII价格趋势
            closes_series = kl.get("closes") or []
            if closes_series and isinstance(closes_series, list) and len(closes_series) >= 10:
                last_15 = closes_series[-15:]
                L(f"  近{len(last_15)}日价格走势:")
                for i, price in enumerate(reversed(last_15)):
                    L(f"    Day-{i+1:>2d}  ¥{price:>8.2f}")
                lo = min(closes_series)
                hi = max(closes_series)
                rng = hi - lo if hi > lo else 1
                L(f"    区间: ¥{lo:.2f} ~ ¥{hi:.2f}   振幅: {rng/lo*100:.1f}%")

        # 技术指标摘要
        tech_items = []
        if tech.get("macd") and isinstance(tech["macd"], dict):
            m = tech["macd"]
            tech_items.append(f"MACD DIF={m.get('dif', 0):.2f} DEA={m.get('dea', 0):.2f}")
        if tech.get("rsi") and isinstance(tech["rsi"], dict):
            r = tech["rsi"]
            tech_items.append(f"RSI14={r.get('rsi14', 0):.1f}")
        if tech.get("boll") and isinstance(tech["boll"], dict):
            b = tech["boll"]
            tech_items.append(f"BOLL中轨={b.get('mid', 0):.2f} 位置={b.get('pos_pct', 0):.0f}%")
        if tech.get("kdj") and isinstance(tech["kdj"], dict):
            k = tech["kdj"]
            tech_items.append(f"KDJ K={k.get('k', 0):.1f} D={k.get('d', 0):.1f} J={k.get('j', 0):.1f}")
        if tech.get("volume") and isinstance(tech["volume"], dict):
            v = tech["volume"]
            tech_items.append(f"量比={v.get('ratio', 0):.1f}")
        if tech_items:
            L("  技术指标: " + " | ".join(tech_items))

        # 行情信号
        if l1.get("signals"):
            L("  信号提示:")
            for s in l1["signals"]:
                L(f"    · {s}")

    # ── Layer2 研报
    l2 = layers.get("layer2") or {}
    if l2.get("ok"):
        L("")
        L(f"{'─'*36}  2. 机构研报与估值  {'─'*26}")
        has_data = False
        if l2.get("recent_reports") and isinstance(l2["recent_reports"], list):
            has_data = True
            L("  近30日相关研报摘要（显示最近5条）:")
            for r in l2["recent_reports"][:5]:
                rating = f"[{r.get('rating', '')}]" if r.get("rating") else ""
                org = f"({r.get('org', '')})" if r.get("org") else ""
                L(f"    · [{r.get('date', '')}] {rating}{org} {r.get('title', '')}")
            if l2.get("rating_dist") and isinstance(l2["rating_dist"], dict):
                parts = [f"{k}:{v}" for k, v in sorted(l2["rating_dist"].items(), key=lambda x: -x[1])[:5]]
                L(f"  评级分布: {', '.join(parts)}")
        if l2.get("eps_forecast") and isinstance(l2["eps_forecast"], list):
            has_data = True
            L("  EPS预测:")
            for row in l2["eps_forecast"][:4]:
                if isinstance(row, list) and len(row) >= 4:
                    L(f"    · {row[0]}: EPS {row[3]} 元 (机构数: {row[1]})")
        if l2.get("valuation") and isinstance(l2["valuation"], dict):
            has_data = True
            v = l2["valuation"]
            L(f"  估值判断: 前向PE {_fmt_num(v.get('forward_pe'))}  | PEG {_fmt_num(v.get('peg'))}  "
              f"| PB {_fmt_num(v.get('pb'))}")
        if l2.get("signals"):
            has_data = True
            for s in l2["signals"]:
                L(f"    · {s}")
        if not has_data:
            reports_count = len(l2.get("recent_reports", []))
            if reports_count > 0:
                L(f"  近30日内无新研报（共 {reports_count} 篇历史研报）")
            else:
                L("  无机构覆盖数据")
                L("  无研报数据（该股可能无机构覆盖）")

    # ── Layer_IND 行业对比
    li = layers.get("layer_ind") or {}
    if li.get("ok"):
        L("")
        L(f"{'─'*36}  3. 行业对比分析  {'─'*28}")
        if li.get("industry_name"):
            L(f"  所属行业: {li['industry_name']}")
        if li.get("peers") and isinstance(li["peers"], list):
            ps = li.get("peer_summary") or {}
            if isinstance(ps, dict):
                L(f"  行业样本: {ps.get('count', 0)}只同行 | "
                  f"行业PE中位: {_fmt_num(ps.get('pe_median'))} | "
                  f"行业PB中位: {_fmt_num(ps.get('pb_median'))}")
                pe_vs = ps.get('pe_vs_industry')
                pb_vs = ps.get('pb_vs_industry')
                L(f"  本股相对行业: PE {_fmt_num(pe_vs) + 'x' if pe_vs is not None else 'N/A'} | "
                  f"PB {_fmt_num(pb_vs) + 'x' if pb_vs is not None else 'N/A'} | "
                  f"超额收益 {_fmt_pct(ps.get('chg_vs_industry'))}")
            L(f"  可比同行（Top{min(6, len(li['peers']))}）:")
            for p in li["peers"][:6]:
                L(f"    · {p.get('code', '')} {p.get('name', ''):>6}  "
                  f"¥{_fmt_num(p.get('price'))}  "
                  f"{_fmt_pct(p.get('chg_pct'))}  "
                  f"PE {_fmt_num(p.get('pe_ttm'))}  "
                  f"PB {_fmt_num(p.get('pb'))}  "
                  f"市值 {_fmt_num(p.get('mcap_yi'))}亿")
        if li.get("signals"):
            for s in li["signals"]:
                L(f"    · {s}")

    # ── Layer3 交易信号
    l3 = layers.get("layer3") or {}
    if l3.get("ok"):
        L("")
        L(f"{'─'*36}  4. 交易信号与题材  {'─'*26}")
        if l3.get("boards") and isinstance(l3["boards"], dict):
            bb = l3["boards"]
            if bb.get("concept"):
                L(f"  概念板块: {', '.join(bb['concept'][:8])}")
            if bb.get("area"):
                L(f"  地域板块: {', '.join(bb['area'][:2])}")
        if l3.get("fund_flow") and isinstance(l3["fund_flow"], dict):
            ff = l3["fund_flow"]
            if ff.get("today") and isinstance(ff["today"], dict):
                L(f"  今日主力净: {ff['today'].get('main_net_wan', 0):+.0f} 万元")
            if ff.get("recent_20d") and isinstance(ff["recent_20d"], dict):
                r = ff["recent_20d"]
                L(f"  近20日: 净 {r.get('total_net_wan', 0):+.0f}万, 净流入 {r.get('positive_days', 0)}/{r.get('total_days', 0)}日")
        if l3.get("dragon_tiger") and isinstance(l3["dragon_tiger"], list) and l3["dragon_tiger"]:
            L("  龙虎榜（近30日, 最近5条）:")
            for dt in l3["dragon_tiger"][:5]:
                L(f"    · [{dt.get('date', '')}] {dt.get('reason', '')} | "
                  f"收盘价 {_fmt_num(dt.get('close'))} | 净买 {dt.get('net_buy_wan', 0):+.0f}万")
        if l3.get("lockup") and isinstance(l3["lockup"], list) and l3["lockup"]:
            L("  限售解禁（未来90日）:")
            for lk in l3["lockup"][:5]:
                L(f"    · {lk.get('date', '')}: {lk.get('type', '')} {_fmt_num(lk.get('ratio'))}%")
        if l3.get("signals"):
            for s in l3["signals"]:
                L(f"    · {s}")

    # ── Layer4 筹码/资金结构
    l4 = layers.get("layer4") or {}
    if l4.get("ok"):
        L("")
        L(f"{'─'*36}  5. 筹码与资金结构  {'─'*26}")
        if l4.get("holder_trend") and isinstance(l4["holder_trend"], list) and l4["holder_trend"]:
            L("  股东户数变化（最近在前）:")
            L(f"    {'日期':<12} {'户数':>14} {'环比变化':>12} {'变化率':>10}")
            for h in l4["holder_trend"][:5]:
                _cr = h.get('change_ratio', 0)
                # 边界检查：变化率超过±500%视为异常数据，不显示
                _cr_disp = _cr if abs(_cr) <= 500 else (999.99 if _cr > 500 else -999.99)
                _cr_flag = " ⚠️" if abs(_cr) > 500 else ""
                L(f"    {h.get('date', ''):<12} {h.get('holder_num', 0):>14,} "
                  f"{h.get('change_num', 0):>+12,.0f} {_cr_disp:>+9.2f}%{_cr_flag}")
        if l4.get("margin") and isinstance(l4["margin"], list) and l4["margin"]:
            L("  融资融券余额（近5日）:")
            L(f"    {'日期':<12} {'融资余额(亿)':>14} {'融资买入(万)':>14} {'融券余额(万)':>14}")
            for m in l4["margin"][:5]:
                L(f"    {m.get('date', ''):<12} {m.get('rzye_wan', 0)/10000:>14.2f} "
                  f"{m.get('rzmre_wan', 0):>14,.0f} {m.get('rqye_wan', 0):>14,.0f}")
        if l4.get("block_trade") and isinstance(l4["block_trade"], list) and l4["block_trade"]:
            L("  大宗交易（近15条）:")
            for bt in l4["block_trade"][:5]:
                L(f"    · [{bt.get('date', '')}] {bt.get('amount_wan', 0):>8,.0f}万 @¥{_fmt_num(bt.get('deal_price'))} "
                  f"溢价 {_fmt_pct(bt.get('premium_pct'))} | 买方:{str(bt.get('buyer', ''))[:15]} → 卖方:{str(bt.get('seller', ''))[:15]}")
        if l4.get("holder_structure") and isinstance(l4["holder_structure"], list) and l4["holder_structure"]:
            L("  十大流通股东结构（最近3季度）:")
            for hs in l4["holder_structure"][:3]:
                L(f"    · [{hs.get('date', '')}] 总占比{_fmt_num(hs.get('total'))}% | "
                  f"北向 {_fmt_num(hs.get('northbound'))}% | "
                  f"机构 {_fmt_num(hs.get('domestic'))}%({hs.get('domestic_count', 0)}家) | "
                  f"个人 {_fmt_num(hs.get('individual'))}%")
        if l4.get("signals"):
            for s in l4["signals"]:
                L(f"    · {s}")

    # ── Layer5 新闻舆情
    l5 = layers.get("layer5") or {}
    if l5.get("ok"):
        L("")
        L(f"{'─'*36}  6. 新闻与舆情  {'─'*30}")
        total_g = len(l5.get("global_related") or [])
        hl = l5.get("hot_list") or []
        if total_g == 0 and not hl:
            L("  近期未检测到与该标的直接相关的重大新闻")
        else:
            if total_g > 0:
                L(f"  东财个股新闻（{total_g} 条）:")
                for n in l5["global_related"][:5]:
                    if isinstance(n, dict):
                        L(f"    · [{n.get('time', '')}] {n.get('title', '')}")
            if hl:
                L(f"  同花顺热榜: #{hl[0]['rank']} {hl[0]['name']} 热度{hl[0]['heat']}")
        # 财联社快讯（近3天）
        cls_list = l5.get("cls_news") or []
        if cls_list:
            L(f"  财联社快讯（近3天，{len(cls_list)} 条）:")
            for n in cls_list[:10]:
                if isinstance(n, dict):
                    L(f"    · [{n.get('time', '')}] {n.get('title', '')}")
        # 互动易问答（近15天）
        irm_list = l5.get("irm_qa") or []
        if irm_list:
            L(f"  互动易问答（近15天，{len(irm_list)} 条）:")
            for n in irm_list[:5]:
                if isinstance(n, dict):
                    L(f"    · [{n.get('time', '')}] {n.get('question', '')}")
        if l5.get("signals"):
            for s in l5["signals"]:
                L(f"    · {s}")

    # ── Layer6 基本面
    l6 = layers.get("layer6") or {}
    if l6.get("ok"):
        L("")
        L(f"{'─'*36}  7. 基本面与财务健康  {'─'*26}")
        if l6.get("financials") and isinstance(l6["financials"], list) and l6["financials"]:
            L("  利润表（最近4期）:")
            L(f"    {'日期':<12} {'营收(亿)':>12} {'净利润(亿)':>12}")
            for f in l6["financials"][:4]:
                L(f"    {f.get('date', ''):<12} {f.get('revenue_yi', 0):>12,.2f} {f.get('profit_yi', 0):>12,.2f}")
        ratios6 = l6.get("ratios") or {}
        if ratios6 and isinstance(ratios6, dict):
            items = []
            if "roe_annualized" in ratios6:
                items.append(f"ROE年化: {ratios6['roe_annualized']:.1f}%")
            if "profit_yoy" in ratios6:
                items.append(f"利润YoY: {_fmt_pct(ratios6['profit_yoy'])}")
            if "revenue_yoy" in ratios6:
                items.append(f"营收YoY: {_fmt_pct(ratios6['revenue_yoy'])}")
            if "dividend_yield" in ratios6:
                items.append(f"股息率: {ratios6['dividend_yield']:.2f}%")
            if "pct_from_high" in ratios6:
                items.append(f"距历史高点: {ratios6['pct_from_high']:.1f}%")
            if items:
                L("  关键指标: " + " | ".join(items))
        if l6.get("balance_sheet") and isinstance(l6["balance_sheet"], list) and l6["balance_sheet"]:
            bs = l6["balance_sheet"][0]
            if isinstance(bs, dict):
                L(f"  资产负债摘要({bs.get('date', '')}): "
                  f"总资产 {_fmt_num(bs.get('total_assets_yi'))}亿 | "
                  f"资产负债率 {_fmt_num(bs.get('debt_ratio'))}% | "
                  f"商誉/净资产 {_fmt_num(bs.get('gw_ratio'))}% | "
                  f"应收账款/总资产 {_fmt_num(bs.get('ar_ratio'))}% | "
                  f"现金/短债 {_fmt_num(bs.get('cash_debt_ratio'))}x")
        if l6.get("dividends") and isinstance(l6["dividends"], list) and l6["dividends"]:
            L("  最近分红记录:")
            for d in l6["dividends"][:5]:
                if isinstance(d, dict):
                    L(f"    · [{d.get('date', '')}] 每股派息 ¥{_fmt_num(d.get('bonus_rmb'))}")
        if l6.get("historical_high"):
            L(f"  历史最高价: ¥{_fmt_num(l6['historical_high'])}")
        if l6.get("signals"):
            for s in l6["signals"]:
                L(f"    · {s}")

    # ── Layer_RISK 风险扫描
    lr = layers.get("layer_risk") or {}
    if lr.get("ok"):
        L("")
        L(f"{'─'*36}  8. 风险扫描  {'─'*33}")
        items = lr.get("items") or []
        if items and isinstance(items, list):
            for it in items:
                if isinstance(it, dict):
                    level = it.get("level", "")
                    if level == "高":
                        marker = "⚠️[高]"
                    elif level == "中":
                        marker = "❗[中]"
                    else:
                        marker = "  [低]"
                    L(f"    {marker} {it.get('name', ''):>8} — {it.get('text', '')} "
                      f"(风险分: {it.get('score', 0)})")
        if lr.get("signals"):
            for s in lr["signals"]:
                L(f"    · {s}")

    # ── Layer7 公告
    l7 = layers.get("layer7") or {}
    if l7.get("ok"):
        L("")
        L(f"{'─'*36}  9. 公告与重大事项  {'─'*28}")
        anns = l7.get("announcements") or []
        if not anns:
            L("  近90日无匹配关键词的公告")
        else:
            L("  近90日公告摘要（显示最近10条）:")
            for a in anns[:10]:
                if isinstance(a, dict):
                    tag = f"[{a.get('type', '')}]" if a.get("type") else ""
                    L(f"    · [{a.get('date', '')}] {tag} {a.get('title', '')}")
        if l7.get("signals"):
            for s in l7["signals"]:
                L(f"    · {s}")

    # ── 综合评分（六维雷达图 ASCII）
    L("")
    L("═" * 78)
    scores = _scoring(layers, _cfg_sc=_sc.get("scoring"))
    L(f"  ★ 综合六维评分（总分: {scores.get('total', 0):.1f}/100）")
    L("")
    # 从配置读取权重，无配置则用默认值
    _weights = (_sc.get("scoring") or {}).get("weights", {}) if _sc else {}
    wt = f"{_weights.get('technical', 25)}%"
    wv = f"{_weights.get('valuation', 20)}%"
    wf = f"{_weights.get('fundamental', 20)}%"
    wfl = f"{_weights.get('flow', 15)}%"
    wth = f"{_weights.get('holder', 10)}%"
    wd = f"{_weights.get('dividend', 10)}%"
    dims = [
        ("技术面", scores.get("technical", 50), wt),
        ("估值面", scores.get("valuation", 50), wv),
        ("基本面", scores.get("fundamental", 50), wf),
        ("资金面", scores.get("flow", 50), wfl),
        ("筹码面", scores.get("holder", 50), wth),
        ("分红面", scores.get("dividend", 50), wd),
    ]
    L(f"    {'维度':<10} {'评分':>8} {'权重':>8}  {'图表':<55}")
    for name, score, weight in dims:
        # 图形长度按加权分数计算：原始分数 * 权重比例 / 100 * 50
        w = float(weight.rstrip('%')) / 100
        weighted_score = score * w
        if score >= 70:
            marker = "●"
        elif score >= 50:
            marker = "○"
        elif score >= 30:
            marker = "△"
        else:
            marker = "▲"
        L(f"    {name:<10} {score:>6.1f}  {weight:>8}  {marker}")
    L("")
    L(f"    {'综合':<10} {scores.get('total', 0):>6.1f}  {'100%':>8}  ★")

    # V8.5新增：多评委评审团评分
    L("\n  ★ 多评委评审团评分")
    L("  ─────────────────────────────────────────────────────────────────────")
    try:
        # 复用 _scoring 中的数据提取逻辑，路径与 _scoring() 一致
        _l1 = layers.get("layer1") or {}
        _l6 = layers.get("layer6") or {}
        _l6_ratios = _l6.get("ratios") or {}
        _l6_bs = (_l6.get("balance_sheet") or [{}])[0]
        score_data = ScoreData(
            code=code,
            name=basic.get('name', ''),
            price=basic.get('price', 0),
            pe_ttm=_l6_ratios.get('pe_ttm', 0),
            pb=_l6_ratios.get('pb', 0),
            roe=_l6_ratios.get('roe_annualized', 0),
            debt_ratio=(_l6_bs.get('debt_ratio', 0) / 100) if isinstance(_l6_bs, dict) else 0,
            change_pct=basic.get('change_pct', 0),
            volume_ratio=(_l1.get("tech") or {}).get("volume", {}).get("ratio", 1.0),
            rsi14=(_l1.get("tech") or {}).get("rsi", {}).get("rsi14", 50),
        )
        multi_scores = calculate_multi_school_scores(score_data)
        L(f"    价值派评分: {multi_scores['value'].total_score:.1f}分")
        L(f"    成长派评分: {multi_scores['growth'].total_score:.1f}分")
        L(f"    投机派评分: {multi_scores['speculator'].total_score:.1f}分")
        L(f"    综合共识: {multi_scores['consensus'].total_score:.1f}分")
    except Exception as e:
        L(f"    多评委评分计算异常: {str(e)}")

    # 投资建议
    total = scores.get("total", 50)
    if total >= 75:
        advice = "【偏乐观】五个维度表现优秀，适合深度研究后作为重点配置候选"
    elif total >= 60:
        advice = "【中性偏乐观】整体表现良好，但仍有短板，建议持续跟踪后分批配置"
    elif total >= 45:
        advice = "【中性】信号混杂，利弊参半，建议观望或小仓位试探"
    elif total >= 30:
        advice = "【中性偏谨慎】存在多项短板或风险，需谨慎评估后决定"
    else:
        advice = "【偏谨慎】多项指标不佳或风险较高，短期建议回避"
    L("")
    L(f"  综合投资建议: {advice}")

    # 总结所有各层信号
    all_signals_flat = []
    for layer_name, ld in layers.items():
        if isinstance(ld, dict) and ld.get("signals"):
            for s in ld["signals"]:
                all_signals_flat.append((layer_name, s))
    if all_signals_flat:
        L("")
        L(f"  ★ 全部关键信号汇总（共 {len(all_signals_flat)} 条）:")
        for ln, s in all_signals_flat:
            display = {
                "layer1": "行情", "layer2": "研报", "layer_ind": "行业对比",
                "layer3": "交易信号", "layer4": "筹码", "layer5": "新闻",
                "layer6": "基本面", "layer_risk": "风险", "layer7": "公告",
            }.get(ln, ln)
            L(f"    [{display}] {s}")

    # 失败层提示
    failed = [k for k, v in layers.items() if isinstance(v, dict) and not v.get("ok", True)]
    if failed:
        L("")
        L(f"  ⚠️ 以下层数据获取异常: {', '.join(failed)}")

    L("")
    L("═" * 78)

    output = "\n".join(filter(None, lines))

    return output


# =====================================================================
# 主流程: 9层并行分析（顺序版/并行版）
# =====================================================================

async def analyze_stock(code: str, parallel: bool = True) -> Tuple[str, str]:
    """
    执行9层分析并返回(股票名称, 报告文本)。
    策略: 先算L1/L2/L3/L4/L5/L6/L7（并行），再用已有结果驱动Layer_RISK（依赖L3/L4/L6）。
    """
    code = code.strip()
    if not code or not code.isdigit() or len(code) != 6:
        return code, f"【错误】股票代码 {code} 格式不正确（需要6位数字）"

    print(f"▶ 开始分析 {code} ...", flush=True)
    t0 = time.time()

    # 预热（获取股票名称和市值，用于行业对比过滤）
    stock_name = ""
    stock_mcap = 0
    price_local = 0
    try:
        # 股票名称：data_provider 暂无对应异步函数，保留原路径
        # V15.4.2: 同步 TDX 包 to_thread
        q = await asyncio.to_thread(tdx_get_quote_full, code)
        if q:
            stock_name = q.get("name", "")
            stock_mcap = q.get("mcap_yi", 0) or 0
        # 价格：从 data_provider 获取
        try:
            price_local = await get_stock_price_async(code) or 0
        except Exception:
            price_local = q.get("price", 0) if q else 0
        # 市值：优先从 data_provider 综合数据获取
        try:
            composite = await get_stock_composite_async(code)
            if composite and composite.get("mcap_yi", 0) > 0:
                stock_mcap = composite["mcap_yi"]
        except Exception:
            pass
    except Exception as _e:
        _debug_log(f"ful analyze_stock preheat quote error: {_e}")

    # 第1轮：7个独立层并行
    # 同步层用 asyncio.to_thread 包装，异步层直接调用
    async def _run_layer(name: str, fn) -> Any:
        try:
            result = await fn
            print(f"  ✓ {name} 完成", flush=True)
            return name, result
        except Exception as e:
            print(f"  ✓ {name} 完成", flush=True)
            return name, {"ok": False, "signals": [f"异常: {e}"]}

    first_round_coros = []
    # 异步层：直接调用
    first_round_coros.append(_run_layer("layer1", layer1_market(code)))
    first_round_coros.append(_run_layer("layer2", layer2_research(code)))
    first_round_coros.append(_run_layer("layer_ind", layer_ind_industry(code, stock_mcap)))
    first_round_coros.append(_run_layer("layer6", layer6_fundamental(code)))
    # 同步层：使用 asyncio.to_thread 包装
    first_round_coros.append(_run_layer("layer3", asyncio.to_thread(layer3_signals, code)))
    first_round_coros.append(_run_layer("layer4", asyncio.to_thread(layer4_chips, code)))
    first_round_coros.append(_run_layer("layer5", asyncio.to_thread(layer5_news, code, stock_name)))
    first_round_coros.append(_run_layer("layer7", asyncio.to_thread(layer7_announcements, code, stock_name)))

    layers: Dict[str, Any] = {}

    if parallel:
        results = await asyncio.gather(*first_round_coros)
        for name, result in results:
            layers[name] = result
    else:
        for coro in first_round_coros:
            name, result = await coro
            layers[name] = result

    # 第2轮：Layer_RISK（依赖L3/L4/L6已有数据）
    try:
        layers["layer_risk"] = await layer_risk(code, layers_ref=layers)
        print("  ✓ layer_risk 完成", flush=True)
    except Exception as e:
        layers["layer_risk"] = {"ok": False, "signals": [f"异常: {e}"]}

    # 按用户阅读顺序重排
    ordered_layers = {}
    for key in ["layer1", "layer2", "layer_ind", "layer3", "layer4",
                "layer5", "layer6", "layer_risk", "layer7"]:
        if key in layers:
            ordered_layers[key] = layers[key]

    report = format_report(code, ordered_layers)
    elapsed = time.time() - t0
    print(f"  完成分析，耗时 {elapsed:.1f}秒", flush=True)

    # V7.5 新增：保存评分快照
    # 在 analyze_stock 作用域内重新计算评分（format_report 内部的 scores 不可用）
    try:
        scores_local = _scoring(ordered_layers, _cfg_sc=_sc.get("scoring"))
        _SNAPSHOT_DATA[code] = {
            "name": stock_name,
            "total_score": scores_local.get("total", 0),
            "price": price_local,
            "report_source": "ful"
        }
    except Exception as _e:
        _debug_log(f"ful analyze_stock snapshot error: {_e}")

    return stock_name or code, report


# =====================================================================
# CLI
# =====================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="A股九层全维度分析报告生成器（行情/研报/行业/信号/筹码/新闻/基本面/风险/公告）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  python get_ful_report.py 600519
  python get_ful_report.py 600519 000858 002310
  python get_ful_report.py 600519 --no-parallel --no-upload
  python get_ful_report.py 600519 -o ./my_reports
""",
    )
    parser.add_argument("codes", nargs="+", help="股票代码，支持1个或多个（6位数字）")
    parser.add_argument("-o", "--output", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports"),
                        help="报告输出目录（默认: 脚本目录下的 reports/）")
    parser.add_argument("--no-parallel", action="store_true", help="禁用多线程并行，顺序执行（调试用）")
    parser.add_argument("--no-upload", action="store_true", help="跳过 Google Drive 上传")
    return parser.parse_args()


async def _generate_reports(codes: List[str], output_dir: str, now_str: str,
                      parallel: bool = True) -> Tuple[List[str], List[Dict[str, str]]]:
    """执行分析并生成报告文件。

    Args:
        codes: 股票代码列表
        output_dir: 输出目录
        now_str: 时间戳字符串（用于文件命名）
        parallel: 是否并行执行

    Returns:
        (generated_files, data_results) - 生成的文件路径列表和结果状态列表
    """
    generated_files: List[str] = []
    data_results: List[Dict[str, str]] = []

    for code in codes:
        try:
            name, report = await analyze_stock(code, parallel=parallel)
            fname = f"{code}_ful_{now_str}.txt"
            fpath = os.path.join(output_dir, fname)
            with open(fpath, "w", encoding="utf-8") as fp:
                fp.write(report)
            generated_files.append(fpath)
            data_results.append({"code": code, "status": "成功", "error": "", "name": name})
            print(f"✅ 报告已生成: {fpath}", flush=True)
        except Exception as e:
            data_results.append({"code": code, "status": "数据失败", "error": str(e), "name": ""})
            print(f"❌ {code} 数据生成失败: {e}", flush=True)
            logger.error(f"报告生成失败 {code}: {e}", exc_info=True)

    return generated_files, data_results


async def _upload_reports(generated_files: List[str], no_upload: bool, data_results: List[Dict[str, str]] = None) -> List[Dict[str, str]]:
    """上传报告到 Google Drive。

    Args:
        generated_files: 待上传的文件路径列表
        no_upload: 是否跳过上传
        data_results: 分析结果数据（包含股票名称，优先从此获取）

    Returns:
        上传结果状态列表
    """
    upload_results: List[Dict[str, str]] = []

    # 构建 code -> name 映射，优先使用已获取的名称
    name_map: Dict[str, str] = {}
    if data_results:
        for r in data_results:
            if r.get("code") and r.get("name"):
                name_map[r["code"]] = r["name"]

    drive, gd_proxy_set, gd_parent_folder_id, skip_upload = None, False, None, False
    if not no_upload:
        drive, gd_proxy_set, gd_parent_folder_id, skip_upload = init_gd(_SCRIPT_DIR)

    if drive and not skip_upload and generated_files:
        for file_path in generated_files:
            code = os.path.basename(file_path).split('_')[0]
            try:
                # 优先从已有的分析结果中获取名称，避免重复调用
                q_name = name_map.get(code, "")
                if not q_name:
                    # data_provider 暂无名称接口，fallback 到原方式
                    # V15.4.2: 同步 TDX 包 to_thread
                    _qn = await asyncio.to_thread(tdx_get_quote_full, code)
                    q_name = _qn.get("name", "")
                if upload_stock_report_by_code(drive, gd_parent_folder_id, code, q_name, file_path):
                    upload_results.append({"code": code, "status": "成功", "error": "", "path": file_path})
                else:
                    upload_results.append({"code": code, "status": "GD上传失败", "error": "上传失败", "path": file_path})
            except Exception as gd_e:
                print(f"  ⚠️ GD 上传异常: {gd_e}", flush=True)
                logger.error(f"GD上传异常 {code}: {gd_e}", exc_info=True)
                upload_results.append({"code": code, "status": "GD上传异常", "error": str(gd_e), "path": file_path})

    cleanup_gd_proxy(gd_proxy_set)
    return upload_results


def _print_summary(data_results: List[Dict[str, str]], upload_results: List[Dict[str, str]],
                   generated_files: List[str], elapsed: float) -> None:
    """打印批量执行汇总信息。"""
    print(f"{'=' * 78}", flush=True)
    print(f"全部完成！共分析 {len(data_results)} 只股票，总耗时 {elapsed:.1f} 秒", flush=True)
    for f in generated_files:
        print(f"  → {f}", flush=True)

    total = len(data_results)
    ok = [r for r in data_results if r["status"] == "成功"]
    fd = [r for r in data_results if r["status"] == "数据失败"]
    fg = [r for r in upload_results if r["status"] in ("GD上传失败", "GD上传异常", "GD未连接")]

    if total > 0:
        try:
            print(f"\n{'=' * 60}\n  批量执行完成 — 共处理 {total} 只股票\n{'=' * 60}")
            print(f"  ✅ 数据成功: {len(ok)}  |  ❌ 数据失败: {len(fd)}  |  ⚠️ GD上传失败: {len(fg)}")
            for r in fd:
                print(f"    ❌ {r['code']} — {r['error'][:80]}")
            for r in fg:
                print(f"    ⚠️ {r['code']}")
        except UnicodeEncodeError:
            # 子进程未设 PYTHONIOENCODING=utf-8 时的兜底
            print(f"\n{'=' * 60}\n  批量执行完成 — 共处理 {total} 只股票\n{'=' * 60}")
            print(f"  [OK] 数据成功: {len(ok)}  |  [FAIL] 数据失败: {len(fd)}  |  [WARN] GD上传失败: {len(fg)}")
            for r in fd:
                print(f"    [FAIL] {r['code']} — {r['error'][:80]}")
            for r in fg:
                print(f"    [WARN] {r['code']}")


async def _async_main():
    """异步主函数，执行实际的分析流程。"""
    args = parse_args()

    # 清洗股票代码：提取6位数字、去重、过滤无效项
    codes = clean_codes(args.codes, verbose=True)
    if not codes:
        print("  ❌ 没有有效的股票代码")
        return

    output_dir = ensure_output_dir(args.output)
    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    _mkt_status, _mkt_note = get_market_status()

    header_lines = []
    header_lines.append("=" * 78)
    header_lines.append("  A股九层全维度分析引擎")
    header_lines.append(f"  启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if _mkt_status == "closed":
        header_lines.append("  ⚠️ 休市日：数据为最近交易日快照，实时行情已标注")
    elif _mkt_status == "lunch":
        header_lines.append("  ⚠️ 午休时段（11:30-13:00）：行情暂停但基本面数据正常")
    elif _mkt_status in ("post_market", "pre_market"):
        header_lines.append("  ⚠️ 非交易时段：数据为最近交易日快照，实时行情已标注")
    elif _mkt_status == "post_close":
        header_lines.append("  ℹ️ 盘后收盘：数据为今日收盘快照，实时行情已标注")
    header_lines.append(f"  分析标的: {', '.join(codes)}")
    header_lines.append(f"  并行模式: {'OFF(顺序)' if args.no_parallel else f'ON({_MAX_WORKERS}并发)'}  |  GD上传: {'SKIP' if args.no_upload else '启用'}")
    header_lines.append(f"  输出目录: {output_dir}")
    header_lines.append("=" * 78)
    print("\n".join(header_lines), flush=True)

    t_total = time.time()
    generated_files, data_results = await _generate_reports(
        codes, output_dir, now_str, parallel=not args.no_parallel
    )
    elapsed_total = time.time() - t_total

    upload_results = await _upload_reports(generated_files, args.no_upload, data_results)
    _print_summary(data_results, upload_results, generated_files, elapsed_total)


class FulReportRunner(BaseReportRunner):
    """A股九层全维度分析引擎 Runner"""

    def __init__(self):
        super().__init__("get_ful_report", "ful", "A股九层全维度分析引擎")

    def execute_pipeline(self) -> Any:
        codes = clean_codes(self.args.codes, verbose=True)
        if not codes:
            print("  ❌ 没有有效的股票代码")
            return None

        output_dir = ensure_output_dir(self.args.output)
        # V15.4.2: 文件名时间戳格式与 sht/med/lng 保持一致 (%Y%m%d_%H%M 时分)
        # 之前用 self.time_str (BaseReportRunner 的 %Y%m%d_%H%M%S) 导致 ful 文件名带秒
        now_str = datetime.now().strftime("%Y%m%d_%H%M")
        _mkt_status, _mkt_note = get_market_status()

        header_lines = []
        header_lines.append("=" * 78)
        header_lines.append("  A股九层全维度分析引擎")
        header_lines.append(f"  启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if _mkt_status == "closed":
            header_lines.append("  ⚠️ 休市日：数据为最近交易日快照，实时行情已标注")
        elif _mkt_status == "lunch":
            header_lines.append("  ⚠️ 午休时段（11:30-13:00）：行情暂停但基本面数据正常")
        elif _mkt_status in ("post_market", "pre_market"):
            header_lines.append("  ⚠️ 非交易时段：数据为最近交易日快照，实时行情已标注")
        elif _mkt_status == "post_close":
            header_lines.append("  ℹ️ 盘后收盘：数据为今日收盘快照，实时行情已标注")
        header_lines.append(f"  分析标的: {', '.join(codes)}")
        header_lines.append(f"  并行模式: {'OFF(顺序)' if getattr(self.args, 'no_parallel', False) else f'ON({_MAX_WORKERS}并发)'}  |  GD上传: {'SKIP' if self.args.no_upload else '启用'}")
        header_lines.append(f"  输出目录: {output_dir}")
        header_lines.append("=" * 78)
        print("\n".join(header_lines), flush=True)

        async def _run_async_gen():
            return await _generate_reports(
                codes, output_dir, now_str, parallel=not getattr(self.args, 'no_parallel', False)
            )

        generated_files, data_results = asyncio.run(_run_async_gen())

        if _SNAPSHOT_DATA:
            from stock_common.analyze_history import save_snapshot
            save_snapshot("ful", _SNAPSHOT_DATA)

        # V8.3 修复: 转为基类 BaseReportRunner.upload_multi_reports 期望的标准格式
        # {"results": [{code,path,status,...}], "time_str": ts, "report_type": "ful"}
        standard_results: List[Dict[str, str]] = []
        for file_path, r in zip(generated_files, data_results):
            standard_results.append({
                "code": r.get("code", ""),
                "path": file_path,
                "status": r.get("status", "失败"),
                "error": r.get("error", ""),
                "name": r.get("name", ""),
            })
        return {
            "results": standard_results,
            "time_str": now_str,
            "report_type": "ful",
            # 保留原始字段供其他调用方使用
            "generated_files": generated_files,
            "data_results": data_results,
        }

    def upload_reports(self, drive: Any, folder_id: str, results: Any) -> None:
        # V8.3 修复: 委托基类 upload_multi_reports，删除 30 行自写实现
        # name_resolver 优先从 data_results 取 name（_generate_reports 已解析）
        # 兼容旧格式：如有 generated_files/data_results 旧字段，转标准格式
        if not results or not isinstance(results, dict):
            return
        if "results" not in results and "generated_files" in results:
            # 兼容老调用方传的旧格式
            generated_files = results.get("generated_files", [])
            data_results = results.get("data_results", [])
            now_str = results.get("time_str", "")
            standard_results = [
                {
                    "code": r.get("code", ""),
                    "path": fp,
                    "status": r.get("status", "失败"),
                    "error": r.get("error", ""),
                    "name": r.get("name", ""),
                }
                for fp, r in zip(generated_files, data_results)
            ]
            results = {
                "results": standard_results,
                "time_str": now_str,
                "report_type": "ful",
            }
        # 自定义 name_resolver 优先用 results["data_results"] 的 name
        data_results_raw = results.get("data_results")
        def _name_resolver(code: str) -> str:
            if data_results_raw:
                for r in data_results_raw:
                    if r.get("code") == code and r.get("name"):
                        return r["name"]
            return self._default_resolve_name(code)
        self.upload_multi_reports(drive, folder_id, results, name_resolver=_name_resolver)


if __name__ == "__main__":
    runner = FulReportRunner()
    runner.run()
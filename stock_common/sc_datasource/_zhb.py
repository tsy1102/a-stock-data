"""_zhb.py — V17.2 拆包子模块（共享命名空间片段，由 __init__ 载入）

本文件现为独立可导入子模块（不再经 exec 注入）。
由 stock_common/sc_datasource/__init__.py 通过  显式 re-export 到包命名空间；
跨片段符号由各子模块函数体内的局部懒导入（from ._DEFINER import NAME）提供，
共享可变状态集中于 _shared.py（单实例）。
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import code
from stock_common.sc_network import _debug_log
from ._shared import _ZHB_NEAR_REALTIME_FIELDS, _ZHB_REALTIME_FIELDS, _ZHB_STATIC_FIELDS
from core._accessors import (
    get_amount_wan,
    get_change_ytd,
    get_dividend_yield,
    get_main_net_buy,
    get_streak_days,
)


def get_zhb_industry_map() -> Dict[str, str]:
    """V9.6: 获取行业代码→名称映射（全类型，1000+条）。"""
    try:
        from core.zhb_client import get_industry_map

        return get_industry_map()
    except Exception as _e:
        _debug_log(f"datasource zhb industry_map: {_e}")
        return {}


def get_zhb_data_date() -> str:
    """V9.6: 获取 zhb 数据的日期（YYYYMMDD），用于报告中标注数据时效性。"""
    try:
        from core.zhb_client import get_zhb

        zhb = get_zhb()
        return zhb.date if zhb else ""
    except Exception as _e:
        _debug_log(f"datasource zhb data_date: {_e}")
        return ""


def get_zhb_market_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """V9.6: 全市场（或指定股票）统计快照。

    一次调用拿到全市场7938只股票的统计快照，用于val脚本初筛。
    数据可能有1-2天延迟，仅用于盘后初筛。
    """
    try:
        from core.zhb_client import market_stat_snapshot

        return market_stat_snapshot(codes)
    except Exception as _e:
        _debug_log(f"datasource zhb market_snapshot: {_e}")
        return {}


def is_zhb_data_fresh(max_delay_days: int = 3) -> bool:
    """检查 ZHB 数据是否新鲜（延迟不超过指定交易日数）。

    数据过旧时调用方应降级到原有HTTP/TCP接口。
    """
    try:
        from core.zhb_client import is_data_fresh

        return is_data_fresh(max_delay_days)
    except Exception as _e:
        _debug_log(f"datasource zhb is_fresh: {_e}")
        return False


def zhb_field_safe(field_name: str) -> bool:
    """V10.2: 判断 zhb 指定字段在当前数据滞后状态下是否安全可用。
    V10.3: 新增准实时字段分类（max_delay_days=1）。
    V16.3.3: ABCD 四级缓存分级正式化（字典 12.15.6 缓存维度）：
    - A 实时字段（change_pct/amount/price 等）：zhb 日期必须是当日有效行情日（max_delay_days=0）
    - B 准实时字段（main_net_buy/streak_days 等）：1个交易日延迟可接受（max_delay_days=1）
    - C 日频字段（pe_ttm/high_52w/dividend_yield 等）：3个交易日延迟可接受（max_delay_days=3）
    - D 静态字段（ipo_price/股本/行业等恒定数据）：90个交易日延迟可接受（max_delay_days=90）

    Args:
        field_name: zhb 字段名（如 "change_pct", "pe_ttm", "high_52w"）

    Returns:
        True=该字段当前可安全使用 zhb 数据，False=应 fallback 原接口
    """
    if field_name in _ZHB_REALTIME_FIELDS:
        # A 实时字段：zhb 日期必须是当日有效行情日（max_delay_days=0）
        return is_zhb_data_fresh(max_delay_days=0)
    if field_name in _ZHB_NEAR_REALTIME_FIELDS:
        # B 准实时字段：1个交易日延迟可接受（max_delay_days=1）
        return is_zhb_data_fresh(max_delay_days=1)
    if field_name in _ZHB_STATIC_FIELDS:
        # D 静态字段：90个交易日延迟可接受（max_delay_days=90）——恒定数据长假容忍
        return is_zhb_data_fresh(max_delay_days=90)
    # C 日频字段：3个交易日延迟可接受（max_delay_days=3）
    return is_zhb_data_fresh(max_delay_days=3)


def get_zhb_tip_info(code: str) -> Optional[Dict[str, Any]]:
    """V9.6: 获取个股财报日历信息（财报期/EPS/披露日/除权日/分红日）。"""
    try:
        from core.zhb_client import get_tip_info

        return get_tip_info(code)
    except Exception as _e:
        _debug_log(f"datasource zhb tip_info ({code}): {_e}")
        return None


def get_zhb_full_market_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """V10.1: 全市场合并快照（tdxstat + tdxstat2 合并）。

    一次调用拿到全市场7938只股票的完整统计+资金流向数据，
    包含涨跌幅、PE、股息率、52周高低价、成交额、行业代码等。
    """
    try:
        from core.zhb_client import full_market_snapshot

        return full_market_snapshot(codes)
    except Exception as _e:
        _debug_log(f"datasource zhb full_market_snapshot: {_e}")
        return {}


def get_zhb_market_stat2_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """V10.1: 全市场资金流向+板块归属快照（tdxstat2）。"""
    try:
        from core.zhb_client import market_stat2_snapshot

        return market_stat2_snapshot(codes)
    except Exception as _e:
        _debug_log(f"datasource zhb market_stat2_snapshot: {_e}")
        return {}


def get_zhb_dividend_yield(code: str) -> Optional[float]:
    """V10.1: 获取股息率(%)。"""
    try:
        from core.zhb_client import get_dividend_yield

        return get_dividend_yield(code)
    except Exception as _e:
        _debug_log(f"datasource zhb dividend_yield ({code}): {_e}")
        return None


def get_zhb_streak_days(code: str) -> Optional[int]:
    """V10.1: 获取连涨连跌天数（正=连涨，负=连跌）。"""
    try:
        from core.zhb_client import get_streak_days

        return get_streak_days(code)
    except Exception as _e:
        _debug_log(f"datasource zhb streak_days ({code}): {_e}")
        return None


def get_zhb_change_ytd(code: str) -> Optional[float]:
    """V10.1: 获取年初至今涨跌幅(%)。"""
    try:
        from core.zhb_client import get_change_ytd

        return get_change_ytd(code)
    except Exception as _e:
        _debug_log(f"datasource zhb change_ytd ({code}): {_e}")
        return None


def get_zhb_amount_wan(code: str) -> Optional[float]:
    """V10.1: 获取今日成交额(万元)。"""
    try:
        from core.zhb_client import get_amount_wan

        return get_amount_wan(code)
    except Exception as _e:
        _debug_log(f"datasource zhb amount_wan ({code}): {_e}")
        return None


def get_zhb_main_net_buy(code: str) -> Optional[Dict[str, Any]]:
    """V10.3: 获取主力资金流向数据。

    Returns:
        {
            "main_net_buy_hands": float,       # T日主力净买入量(手)
            "main_net_buy_hands_1d": float,    # T-1日主力净买入量(手)
            "main_net_buy_amount": float,      # T日主力净流入额(万元)
            "main_net_buy_amount_1d": float,   # T-1日主力净流入额(万元)
        }
        None if zhb不可用
    """
    try:
        from core.zhb_client import get_main_net_buy

        return get_main_net_buy(code)
    except Exception as _e:
        _debug_log(f"datasource zhb main_net_buy ({code}): {_e}")
        return None


def get_zhb_single_stock_data(code: str) -> Optional[Dict[str, Any]]:
    """V10.1: 获取单只股票的完整zhb数据（tdxstat + tdxstat2合并）。

    V16.0: 合并 tipinfo 的 report_period 为 report_date 字段，
    修复 ZHB 财报事件锁失效（get_sina_financial_report 读 zhb["report_date"] 恒空问题）。

    Returns:
        合并后的股票数据字典，包含涨跌幅、PE、阶段涨幅、52周高低、
        股息率、行业代码、成交额、IPO发行价等字段。
        获取失败返回 None。
    """
    try:
        from core.zhb_client import get_stock_stat, get_stock_stat2, get_tip_info

        stat1 = get_stock_stat(code)
        stat2 = get_stock_stat2(code)
        if not stat1 and not stat2:
            return None
        result = dict(stat1) if stat1 else {}
        if stat2:
            result.update(stat2)
        # V16.0: 合并 tipinfo report_period → report_date（ZHB 财报事件锁核心 Key）
        try:
            tip = get_tip_info(code)
            if tip and tip.get("report_period"):
                result["report_date"] = str(tip["report_period"]).strip()
        except Exception as _e:
            _debug_log(f"datasource zhb tipinfo merge ({code}): {_e}")
        return result
    except Exception as _e:
        _debug_log(f"datasource zhb single_stock_data ({code}): {_e}")
        return None


__all__ = [
    '_ZHB_NEAR_REALTIME_FIELDS',
    '_ZHB_REALTIME_FIELDS',
    '_ZHB_STATIC_FIELDS',
    '_debug_log',
    'code',
    'get_amount_wan',
    'get_change_ytd',
    'get_dividend_yield',
    'get_main_net_buy',
    'get_streak_days',
    'get_zhb_amount_wan',
    'get_zhb_change_ytd',
    'get_zhb_data_date',
    'get_zhb_dividend_yield',
    'get_zhb_full_market_snapshot',
    'get_zhb_industry_map',
    'get_zhb_main_net_buy',
    'get_zhb_market_snapshot',
    'get_zhb_market_stat2_snapshot',
    'get_zhb_single_stock_data',
    'get_zhb_streak_days',
    'get_zhb_tip_info',
    'is_zhb_data_fresh',
    'zhb_field_safe',
]

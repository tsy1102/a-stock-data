#!/usr/bin/env python3
"""
data_provider.py — 统一数据中心层 - V11.5正式启用

版本日期：2026-07-16

架构设计：
  - 实时类数据 → 盘中强制走API（极短缓存），盘前/盘后优先ZHB
  - T-1类数据 → 优先ZHB本地读取，失败fallback到API
  - 静态/财务数据 → 优先本地基础库，失败fallback到API
  - 市值动态计算：总股本(本地静态) × 实时价格(API)

核心特性：
  - 全函数缓存装饰器（基于 stock_cache）
  - 交易状态感知（盘前/盘中/盘后自动切换数据源策略）
  - 同步/异步双版本接口
  - ZHB全量数据预取优化（减少重复调用）
  - 完善的 fallback 机制和异常处理
"""

from typing import Any, Dict, Optional, List
from datetime import datetime, date
import asyncio

from stock_cache import cached, TTL


def _safe_float(v) -> float:
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


# ═══════════════════════════════════════════════════
# 字段时效性分级
# ═══════════════════════════════════════════════════

_REALTIME_FIELDS = frozenset({
    "change_pct", "amount", "price", "open", "high", "low", "prev_close",
})

_NEAR_REALTIME_FIELDS = frozenset({
    "main_net_buy_hands", "main_net_buy_hands_1d",
    "main_net_buy_amount", "main_net_buy_amount_1d",
    "streak_days",
})

_STATIC_FIELDS = frozenset({
    "pe_ttm", "pe_dynamic", "pb", "dividend_yield",
    "high_52w", "low_52w", "change_ytd",
    "change_5d", "change_10d", "change_20d", "change_30d", "change_60d",
    "employee_count", "ipo_price", "industry_code", "industry",
    "total_shares", "float_shares", "turnover_pct", "mcap", "float_mcap",
})


def _is_realtime(field: str) -> bool:
    return field in _REALTIME_FIELDS


def _is_near_realtime(field: str) -> bool:
    return field in _NEAR_REALTIME_FIELDS


def _is_static(field: str) -> bool:
    return field in _STATIC_FIELDS


# ═══════════════════════════════════════════════════
# 交易状态感知
# ═══════════════════════════════════════════════════

def _get_market_status() -> str:
    """获取当前市场状态（简化版，用于数据源选择策略）。

    Returns:
        'pre_market' - 盘前（< 9:30）
        'trading' - 盘中（9:30-11:30, 13:00-15:00）
        'post_market' - 盘后（>= 15:00 或 非交易日）
    """
    try:
        from stock_common.sc_datasource import get_market_status
        status, _ = get_market_status()
        if status in ("morning", "afternoon"):
            return "trading"
        elif status == "pre_market":
            return "pre_market"
        else:
            return "post_market"
    except Exception:
        pass
    now = datetime.now()
    t = now.hour * 100 + now.minute
    if t < 930:
        return "pre_market"
    elif 930 <= t < 1130 or 1300 <= t < 1500:
        return "trading"
    else:
        return "post_market"


def _should_use_zhb_for_realtime() -> bool:
    """判断实时字段是否可以使用ZHB数据。

    盘前或盘后可以用ZHB，盘中必须走API。
    """
    return _get_market_status() != "trading"


# ═══════════════════════════════════════════════════
# 原子数据获取函数
# ═══════════════════════════════════════════════════

@cached(category="stock_quote", ttl_seconds=60)
def get_stock_price(code: str) -> Optional[float]:
    """获取股票实时价格。

    交易状态策略：
      - 盘中：强制走API
      - 盘前/盘后：优先ZHB，失败fallback到API
    """
    if _should_use_zhb_for_realtime():
        try:
            from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh
            if is_zhb_data_fresh(max_delay_days=1):
                zhb = get_zhb_single_stock_data(code)
                if zhb:
                    price = _safe_float(zhb.get("price", 0))
                    if price > 0:
                        return price
        except Exception:
            pass

    try:
        from stock_common import get_tencent_quote
        q = get_tencent_quote(code)
        if q:
            return _safe_float(q.get("price", 0))
    except Exception:
        pass
    try:
        from tdx_client import tdx_get_quote_full
        q = tdx_get_quote_full(code)
        if q:
            return _safe_float(q.get("price", 0))
    except Exception:
        pass
    return None


@cached(category="zhb_data", ttl_seconds=TTL["f10_fund_flow"], trading_day=True)
def get_pe_ttm(code: str) -> Optional[float]:
    """获取PE_TTM。

    静态字段：优先ZHB，失败fallback到API。
    """
    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=3):
            zhb = get_zhb_single_stock_data(code)
            if zhb:
                pe = zhb.get("pe_ttm", 0)
                if pe and pe > 0:
                    return pe
    except Exception:
        pass
    try:
        from stock_common import get_tencent_quote
        q = get_tencent_quote(code)
        if q:
            return _safe_float(q.get("pe_ttm", 0))
    except Exception:
        pass
    return None


@cached(category="zhb_data", ttl_seconds=TTL["f10_fund_flow"], trading_day=True)
def get_pb(code: str) -> Optional[float]:
    """获取PB。

    静态字段：优先ZHB，失败fallback到API。
    """
    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=3):
            zhb = get_zhb_single_stock_data(code)
            if zhb:
                pb = zhb.get("pb", 0)
                if pb and pb > 0:
                    return pb
    except Exception:
        pass
    try:
        from stock_common import get_tencent_quote
        q = get_tencent_quote(code)
        if q:
            return _safe_float(q.get("pb", 0))
    except Exception:
        pass
    return None


@cached(category="zhb_data", ttl_seconds=TTL["f10_fund_flow"], trading_day=True)
def get_dividend_yield(code: str) -> Optional[float]:
    """获取股息率。

    静态字段：优先ZHB。
    """
    try:
        from stock_common import get_zhb_dividend_yield, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=3):
            yield_val = get_zhb_dividend_yield(code)
            if yield_val:
                return yield_val
    except Exception:
        pass
    return None


@cached(category="zhb_data", ttl_seconds=TTL["f10_fund_flow"], trading_day=True)
def get_52w_range(code: str) -> Optional[tuple]:
    """获取52周高低价区间。

    静态字段：优先ZHB。
    """
    try:
        from stock_common import get_zhb_52w_range, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=3):
            high, low = get_zhb_52w_range(code)
            if high > 0 and low > 0:
                return (high, low)
    except Exception:
        pass
    return None


@cached(category="stock_quote", ttl_seconds=60)
def get_change_pct(code: str) -> Optional[float]:
    """获取涨跌幅。

    交易状态策略：
      - 盘中：强制走API
      - 盘前/盘后：优先ZHB，失败fallback到API
    """
    if _should_use_zhb_for_realtime():
        try:
            from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh
            if is_zhb_data_fresh(max_delay_days=1):
                zhb = get_zhb_single_stock_data(code)
                if zhb:
                    change_pct = _safe_float(zhb.get("change_pct", 0))
                    if change_pct != 0 or zhb.get("price", 0) > 0:
                        return change_pct
        except Exception:
            pass

    try:
        from stock_common import get_tencent_quote
        q = get_tencent_quote(code)
        if q:
            return _safe_float(q.get("change_pct", 0))
    except Exception:
        pass
    try:
        from tdx_client import tdx_get_quote_full
        q = tdx_get_quote_full(code)
        if q:
            return _safe_float(q.get("change_pct", 0))
    except Exception:
        pass
    return None


@cached(category="zhb_data", ttl_seconds=TTL["f10_fund_flow"], trading_day=True)
def get_change_ytd(code: str) -> Optional[float]:
    """获取年初至今涨幅。

    静态字段：优先ZHB。
    """
    try:
        from stock_common import get_zhb_change_ytd, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=3):
            return get_zhb_change_ytd(code)
    except Exception:
        pass
    return None


@cached(category="stock_quote", ttl_seconds=60)
def get_amount_wan(code: str) -> Optional[float]:
    """获取成交额（万元）。

    交易状态策略：
      - 盘中：强制走API
      - 盘前/盘后：优先ZHB，失败fallback到API
    """
    if _should_use_zhb_for_realtime():
        try:
            from stock_common import get_zhb_amount_wan, is_zhb_data_fresh
            if is_zhb_data_fresh(max_delay_days=1):
                amount = get_zhb_amount_wan(code)
                if amount and amount > 0:
                    return amount
        except Exception:
            pass

    try:
        from stock_common import get_tencent_quote
        q = get_tencent_quote(code)
        if q:
            return _safe_float(q.get("amount", 0)) / 10000
    except Exception:
        pass
    try:
        from stock_common import get_zhb_amount_wan, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=0):
            return get_zhb_amount_wan(code)
    except Exception:
        pass
    return None


@cached(category="zhb_data", ttl_seconds=TTL["f10_fund_flow"], trading_day=True)
def get_main_net_buy(code: str) -> Optional[Dict[str, Any]]:
    """获取主力资金流向。

    准实时字段：优先ZHB（1天延迟可接受），失败fallback到API。
    """
    try:
        from stock_common import get_zhb_main_net_buy, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=1):
            data = get_zhb_main_net_buy(code)
            if data and any(data.values()):
                return data
    except Exception:
        pass
    try:
        from tdx_client import tdx_get_fund_flow
        ff = tdx_get_fund_flow(code)
        if ff:
            return {
                "main_net_buy_hands": _safe_float(ff.get("main_net_hands", 0)),
                "main_net_buy_hands_1d": 0,
                "main_net_buy_amount": _safe_float(ff.get("main_net_wan", 0)),
                "main_net_buy_amount_1d": 0,
            }
    except Exception:
        pass
    return None


def calc_mcap_yi(code: str, price: Optional[float] = None) -> Optional[float]:
    """计算总市值（亿元）。

    动态计算：总股本(本地静态) × 实时价格(API)。
    """
    if price is None:
        price = get_stock_price(code)
    if not price or price <= 0:
        return None
    try:
        from stock_common import get_share_capital
        cap = get_share_capital(code)
        total_wan = cap.get("total_shares", 0)
        if total_wan > 0:
            return price * total_wan / 10000.0
    except Exception:
        pass
    return None


@cached(category="basic_info_static", ttl_seconds=TTL["basic_info_static"])
def get_stock_info(code: str) -> Optional[Dict[str, Any]]:
    """获取股票基本信息（综合）。"""
    try:
        from stock_common import get_stock_info
        return get_stock_info(code)
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════
# 新增常用字段函数
# ═══════════════════════════════════════════════════

@cached(category="zhb_data", ttl_seconds=TTL["f10_fund_flow"], trading_day=True)
def get_turnover_pct(code: str) -> Optional[float]:
    """获取换手率（%）。

    静态/准实时字段：优先ZHB，失败fallback到API。
    """
    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=1):
            zhb = get_zhb_single_stock_data(code)
            if zhb:
                turnover = _safe_float(zhb.get("turnover_pct", 0))
                if turnover > 0:
                    return turnover
    except Exception:
        pass
    try:
        from stock_common import get_tencent_quote
        q = get_tencent_quote(code)
        if q:
            return _safe_float(q.get("turnover_rate", 0))
    except Exception:
        pass
    return None


@cached(category="share_capital", ttl_seconds=TTL["share_capital"])
def get_totals(code: str) -> Optional[float]:
    """获取总股本（万股）。

    静态字段：优先本地股本缓存，失败fallback到ZHB。
    """
    try:
        from stock_common import get_share_capital
        cap = get_share_capital(code)
        total = cap.get("total_shares", 0)
        if total > 0:
            return total
    except Exception:
        pass
    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=3):
            zhb = get_zhb_single_stock_data(code)
            if zhb:
                total = _safe_float(zhb.get("total_shares", 0))
                if total > 0:
                    return total
    except Exception:
        pass
    return None


@cached(category="zhb_data", ttl_seconds=TTL["f10_fund_flow"], trading_day=True)
def get_market_cap(code: str) -> Optional[float]:
    """获取流通市值（亿元）。

    静态字段：优先ZHB，失败则动态计算。
    """
    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=1):
            zhb = get_zhb_single_stock_data(code)
            if zhb:
                float_mcap = _safe_float(zhb.get("float_mcap", 0))
                if float_mcap > 0:
                    return float_mcap / 1e8
    except Exception:
        pass
    try:
        price = get_stock_price(code)
        if price and price > 0:
            from stock_common import get_share_capital
            cap = get_share_capital(code)
            float_shares = cap.get("float_shares", 0)
            if float_shares > 0:
                return price * float_shares / 10000.0
    except Exception:
        pass
    return None


@cached(category="zhb_data", ttl_seconds=TTL["industry_compare"], trading_day=True)
def get_industry(code: str) -> Optional[str]:
    """获取所属行业名称。

    静态字段：优先ZHB，失败fallback到TDX板块。
    """
    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=7):
            zhb = get_zhb_single_stock_data(code)
            if zhb:
                industry = zhb.get("industry", "")
                if industry:
                    return industry
    except Exception:
        pass
    try:
        from tdx_client import tdx_get_belong_boards
        boards = tdx_get_belong_boards(code)
        if boards and boards.get("industry"):
            return boards["industry"][0]["name"]
    except Exception:
        pass
    return None


@cached(category="zhb_data", ttl_seconds=TTL["f10_fund_flow"], trading_day=True)
def get_streak_days(code: str) -> Optional[int]:
    """获取连涨连跌天数。

    正=连涨，负=连跌，0=震荡。
    准实时字段：优先ZHB。
    """
    try:
        from stock_common import get_zhb_streak_days, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=1):
            return get_zhb_streak_days(code)
    except Exception:
        pass
    return None


# ═══════════════════════════════════════════════════
# 市场快照
# ═══════════════════════════════════════════════════

@cached(category="zhb_data", ttl_seconds=TTL["f10_fund_flow"], trading_day=True)
def get_market_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """获取市场快照。

    优先ZHB全量快照，失败fallback到TDX批量查询。
    """
    try:
        from stock_common import get_zhb_full_market_snapshot, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=3):
            snapshot = get_zhb_full_market_snapshot(codes)
            if snapshot:
                return snapshot
    except Exception:
        pass
    try:
        from tdx_client import tdx_get_quotes_batch
        if codes:
            return tdx_get_quotes_batch(codes)
    except Exception:
        pass
    return {}


# ═══════════════════════════════════════════════════
# 高级数据聚合接口
# ═══════════════════════════════════════════════════

def get_stock_composite(code: str) -> Dict[str, Any]:
    """获取股票综合数据（统一入口，优化版）。

    优化策略：
      1. 先尝试一次性获取ZHB全量数据（如果ZHB新鲜）
      2. 实时字段单独从API补
      3. 减少重复调用

    返回：
        {
            "price": float,           # 实时价格
            "change_pct": float,      # 实时涨跌幅
            "pe_ttm": float,          # PE_TTM
            "pb": float,              # PB
            "dividend_yield": float,  # 股息率
            "mcap_yi": float,         # 总市值（亿元）
            "main_net_buy": dict,     # 主力资金流向
            "high_52w": float,        # 52周最高价
            "low_52w": float,         # 52周最低价
            "change_ytd": float,      # 年初至今涨幅
            "amount_wan": float,      # 成交额（万元）
            "turnover_pct": float,    # 换手率
            "total_shares": float,    # 总股本（万股）
            "float_mcap_yi": float,   # 流通市值（亿元）
            "industry": str,          # 所属行业
            "streak_days": int,       # 连涨连跌天数
            "source": str,            # 数据来源标记
        }
    """
    result = {}
    zhb_data = None
    zhb_fresh = False

    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh
        if is_zhb_data_fresh(max_delay_days=1):
            zhb_data = get_zhb_single_stock_data(code)
            if zhb_data:
                zhb_fresh = True
    except Exception:
        pass

    if zhb_fresh and zhb_data:
        result["pe_ttm"] = _safe_float(zhb_data.get("pe_ttm", 0))
        result["pb"] = _safe_float(zhb_data.get("pb", 0))
        result["dividend_yield"] = _safe_float(zhb_data.get("dividend_yield", 0))
        result["high_52w"] = _safe_float(zhb_data.get("high_52w", 0))
        result["low_52w"] = _safe_float(zhb_data.get("low_52w", 0))
        result["change_ytd"] = _safe_float(zhb_data.get("change_ytd", 0))
        result["turnover_pct"] = _safe_float(zhb_data.get("turnover_pct", 0))
        result["total_shares"] = _safe_float(zhb_data.get("total_shares", 0))
        result["industry"] = zhb_data.get("industry", "")
        result["streak_days"] = int(zhb_data.get("streak_days", 0))

        float_mcap = _safe_float(zhb_data.get("float_mcap", 0))
        if float_mcap > 0:
            result["float_mcap_yi"] = float_mcap / 1e8
        else:
            result["float_mcap_yi"] = 0.0

        main_net_amount = _safe_float(zhb_data.get("main_net_buy_amount", 0))
        main_net_hands = _safe_float(zhb_data.get("main_net_buy_hands", 0))
        result["main_net_buy"] = {
            "main_net_buy_hands": main_net_hands,
            "main_net_buy_hands_1d": _safe_float(zhb_data.get("main_net_buy_hands_1d", 0)),
            "main_net_buy_amount": main_net_amount,
            "main_net_buy_amount_1d": _safe_float(zhb_data.get("main_net_buy_amount_1d", 0)),
        }

        if _should_use_zhb_for_realtime():
            result["price"] = _safe_float(zhb_data.get("price", 0))
            result["change_pct"] = _safe_float(zhb_data.get("change_pct", 0))
            result["amount_wan"] = _safe_float(zhb_data.get("amount", 0)) / 10000 if zhb_data.get("amount", 0) else 0
        else:
            result["price"] = get_stock_price(code)
            result["change_pct"] = get_change_pct(code)
            result["amount_wan"] = get_amount_wan(code)

        if result.get("total_shares", 0) > 0 and result.get("price", 0) > 0:
            result["mcap_yi"] = result["price"] * result["total_shares"] / 10000.0
        else:
            result["mcap_yi"] = calc_mcap_yi(code, result.get("price"))

        result["source"] = "zhb_optimized"
    else:
        result["price"] = get_stock_price(code)
        result["change_pct"] = get_change_pct(code)
        result["pe_ttm"] = get_pe_ttm(code)
        result["pb"] = get_pb(code)
        result["dividend_yield"] = get_dividend_yield(code)
        result["main_net_buy"] = get_main_net_buy(code)
        result["mcap_yi"] = calc_mcap_yi(code, result["price"])

        _range = get_52w_range(code)
        if _range:
            result["high_52w"], result["low_52w"] = _range
        else:
            result["high_52w"] = 0
            result["low_52w"] = 0

        result["change_ytd"] = get_change_ytd(code)
        result["amount_wan"] = get_amount_wan(code)
        result["turnover_pct"] = get_turnover_pct(code)
        result["total_shares"] = get_totals(code) or 0
        result["float_mcap_yi"] = get_market_cap(code) or 0
        result["industry"] = get_industry(code) or ""
        result["streak_days"] = get_streak_days(code) or 0

        result["source"] = "composite_fallback"

    return result


# ═══════════════════════════════════════════════════
# 通用字段获取接口
# ═══════════════════════════════════════════════════

def get_field_value(code: str, field_name: str) -> Optional[Any]:
    """通用字段获取接口。

    根据字段时效性自动选择最优数据源。
    """
    field_name = field_name.lower()

    if field_name == "price":
        return get_stock_price(code)
    elif field_name == "change_pct":
        return get_change_pct(code)
    elif field_name == "pe_ttm":
        return get_pe_ttm(code)
    elif field_name == "pb":
        return get_pb(code)
    elif field_name == "dividend_yield":
        return get_dividend_yield(code)
    elif field_name == "mcap_yi":
        return calc_mcap_yi(code)
    elif field_name == "main_net_buy":
        return get_main_net_buy(code)
    elif field_name == "high_52w":
        _range = get_52w_range(code)
        return _range[0] if _range else None
    elif field_name == "low_52w":
        _range = get_52w_range(code)
        return _range[1] if _range else None
    elif field_name == "change_ytd":
        return get_change_ytd(code)
    elif field_name == "amount_wan":
        return get_amount_wan(code)
    elif field_name == "turnover_pct":
        return get_turnover_pct(code)
    elif field_name == "total_shares" or field_name == "totals":
        return get_totals(code)
    elif field_name == "float_mcap_yi" or field_name == "market_cap":
        return get_market_cap(code)
    elif field_name == "industry":
        return get_industry(code)
    elif field_name == "streak_days":
        return get_streak_days(code)

    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh
        if _is_realtime(field_name):
            if is_zhb_data_fresh(max_delay_days=0):
                zhb = get_zhb_single_stock_data(code)
                if zhb:
                    return zhb.get(field_name)
        elif _is_near_realtime(field_name):
            if is_zhb_data_fresh(max_delay_days=1):
                zhb = get_zhb_single_stock_data(code)
                if zhb:
                    return zhb.get(field_name)
        else:
            if is_zhb_data_fresh(max_delay_days=3):
                zhb = get_zhb_single_stock_data(code)
                if zhb:
                    return zhb.get(field_name)
    except Exception:
        pass

    return None


# ═══════════════════════════════════════════════════
# 异步版本函数
# ═══════════════════════════════════════════════════

async def get_stock_price_async(code: str, session=None) -> Optional[float]:
    """异步版：获取股票实时价格。"""
    return await asyncio.to_thread(get_stock_price, code)


async def get_pe_ttm_async(code: str, session=None) -> Optional[float]:
    """异步版：获取PE_TTM。"""
    return await asyncio.to_thread(get_pe_ttm, code)


async def get_pb_async(code: str, session=None) -> Optional[float]:
    """异步版：获取PB。"""
    return await asyncio.to_thread(get_pb, code)


async def get_dividend_yield_async(code: str, session=None) -> Optional[float]:
    """异步版：获取股息率。"""
    return await asyncio.to_thread(get_dividend_yield, code)


async def get_52w_range_async(code: str, session=None) -> Optional[tuple]:
    """异步版：获取52周高低价区间。"""
    return await asyncio.to_thread(get_52w_range, code)


async def get_main_net_buy_async(code: str, session=None) -> Optional[Dict[str, Any]]:
    """异步版：获取主力资金流向。"""
    return await asyncio.to_thread(get_main_net_buy, code)


async def get_change_pct_async(code: str, session=None) -> Optional[float]:
    """异步版：获取涨跌幅。"""
    return await asyncio.to_thread(get_change_pct, code)


async def get_change_ytd_async(code: str, session=None) -> Optional[float]:
    """异步版：获取年初至今涨幅。"""
    return await asyncio.to_thread(get_change_ytd, code)


async def get_amount_wan_async(code: str, session=None) -> Optional[float]:
    """异步版：获取成交额（万元）。"""
    return await asyncio.to_thread(get_amount_wan, code)


async def get_turnover_pct_async(code: str, session=None) -> Optional[float]:
    """异步版：获取换手率。"""
    return await asyncio.to_thread(get_turnover_pct, code)


async def get_stock_composite_async(code: str, session=None) -> Dict[str, Any]:
    """异步版：获取股票综合数据（统一入口）。"""
    return await asyncio.to_thread(get_stock_composite, code)


async def get_market_snapshot_async(codes: Optional[List[str]] = None, session=None) -> Dict[str, Dict[str, Any]]:
    """异步版：获取市场快照。"""
    return await asyncio.to_thread(get_market_snapshot, codes)

#!/usr/bin/env python3
"""
data_provider.py — 统一数据中心层 - V11.5正式启用

版本日期：2026-07-28 (V15.2)
   - V15.2: P0 崩溃修复 - get_canonical_stock_data 中 board 变量初始化；12 个 zhb_data 函数补 valid_if；tdx_get_quote_full 重构为 ZHB→TDX→HTTP
   - V15.1: industry 字段改用 TDX boards；get_amount_wan 优先级 ZHB→腾讯→TDX；启用 change_30d 字段
   - V15.0: 标准化数据合约 CanonicalStockData + ZHB 时空路由矩阵 + 熔断静默降级
   - V14.2: ZHB 数据集深度集成 - profile.dat/concept_chain/neednote/xgsg/brkseat/special_tags
          新增 get_stock_basic_info_from_zhb / get_concept_from_zhb /
          get_new_share_calendar_from_zhb / get_special_tags_from_zhb
   - V14.0: is_workday() 修复由上游 stock_calendar 提供；ANTI_POISON_DEVIATION_THRESHOLD 标记废弃
   - V13.x: 字段路由简化 + sc_schema 元数据层
   - V12.6: REQUIRES_REALTIME_HTTP / ZHB_SUFFICIENT 字段分类

核心架构设计：
  - ZHB优先原则：所有能从ZHB获取的数据，优先使用ZHB本地快照
  - 实时类数据 → 盘中TDX(或腾讯)优先，盘前/盘后优先ZHB（延迟1-2交易日）
  - T-1类数据 → 优先ZHB本地读取，失败fallback到API
  - 静态/财务数据 → 优先ZHB本地基础库，失败fallback到腾讯HTTP
  - 市值动态计算：总股本(本地静态) × 实时价格(API)

ZHB时间体系说明：
  - ZHB文件次日更新机制：今日运行脚本，获取的是昨日(或上一交易日)的数据
  - 例如：7月17日运行 → zhb_20260716（7月16日数据）
  - 非交易日运行：获取最近一个交易日的数据
  - ZHB中的"基准日" = ZHB文件名日期
  - amount/main_net_buy_amount: 基准日数据
  - amount_1d/main_net_buy_amount_1d: 基准日前一交易日数据
  - amount_2d: 基准日前两交易日数据

接口优先级原则（按字段TDX支持情况分级）：
  - 实时字段（price/change_pct/amount）：ZHB(盘后)→TDX(盘中)→腾讯(fallback)
    * TDX TCP原生支持这些字段，真正高效
    * tdx_get_quote_full内部已含缓存+腾讯兜底补强
  - 估值字段（pe_ttm/pb/turnover_pct）：ZHB→腾讯
    * TDX TCP不返回这些字段，无需TDX中间层
  - 股息率：ZHB only
    * TDX和腾讯都不直接返回，ZHB有完整数据
  - 量能/资金因子（get_volume_acceleration/get_capital_momentum）：纯ZHB数据
    * 无需实时T数据，仅使用ZHB内部的amount/amount_1d/amount_2d等字段

核心特性：
  - 全函数缓存装饰器（基于 stock_cache，按字段变化频率分级TTL）
  - 交易状态感知（盘前/盘中/盘后自动切换数据源策略）
  - 同步/异步双版本接口
  - ZHB全量数据预取优化（减少重复调用）
  - 按TDX支持情况分级的fallback机制
  - 量能三连击因子和资金动量加速因子（纯ZHB数据，时间维度完全对齐）

TTL分级策略：
  - 实时层（price/change_pct/amount）：30分钟 + 交易日模式
  - 日变层（pe_ttm/pb/turnover_pct/main_net_buy/streak_days）：24小时 + 交易日模式
  - 周变层（52w_range）：7天
  - 季度层（total_shares/industry）：90天
  - 月变层（dividend_yield）：30天
"""

from typing import Any, Dict, Optional, List
from datetime import datetime, date, timedelta  # V16.2: timedelta 导入（_get_zhb_date_offset 使用）
import asyncio

from stock_cache import cached, TTL, make_valid_if  # V15.2: 强化 valid_if
from stock_common.sc_network import _fallback_logger


def _debug_log(msg: str) -> None:
    _fallback_logger.debug(msg)


def _safe_float(v) -> float:
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


# V12.6: field routing classification (run-time + field type)
#
# Decision rules:
#   if runtime == pre_market:
#       -> all fields use ZHB
#   elif field in REQUIRES_REALTIME_HTTP:
#       -> HTTP (quote / fund flow)
#   else:
#       -> ZHB (valuation / finance / share / sector)

# V14.2.1: 动态从 sc_schema.FIELD_SPECS 生成（避免重复维护）
# 单一权威源：sc_schema.FIELD_SPECS 的 is_real_time 字段
try:
    from stock_common.sc_schema import list_realtime_http_fields, list_zhb_sufficient_fields

    REQUIRES_REALTIME_HTTP = frozenset(list_realtime_http_fields())
    ZHB_SUFFICIENT = frozenset(list_zhb_sufficient_fields())
except ImportError:
    # Fallback: 如果 sc_schema 不可用（理论上不会发生），用静态定义
    REQUIRES_REALTIME_HTTP = frozenset(
        {
            "price",
            "change_pct",
            "amount",
            "volume",
            "open",
            "high",
            "low",
            "prev_close",
            "change_pct_1d",
            "change_pct_2d",
            "amount_1d",
            "amount_2d",
            "main_net_buy_hands",
            "main_net_buy_hands_1d",
            "main_net_buy_amount",
            "main_net_buy_amount_1d",
        }
    )
    ZHB_SUFFICIENT = frozenset(
        {
            # valuation
            "pe_ttm",
            "pe_dynamic",
            "pb",
            "dividend_yield",
            "turnover_pct",
            # finance
            "net_profit",
            "revenue",
            "roe",
            "eps",
            # share capital
            "total_shares",
            "float_shares",
            "mcap",
            "float_mcap",
            "holder_count",
            # sector
            "industry_code",
            "industry",
            "board",
            "concept",
            # historical change
            "change_5d",
            "change_10d",
            "change_20d",
            "change_30d",
            "change_60d",
            "change_ytd",
            "streak_days",
            # 52w / ipo / employees
            "high_52w",
            "low_52w",
            "ipo_price",
            "employee_count",
        }
    )

# V14.2.1: ZHB_SUFFICIENT 已在 try/except 块中通过 sc_schema 动态生成（或 Fallback 静态定义）


def is_realtime_http_field(field_name):
    # V12.6: True means must use HTTP real-time API
    return field_name in REQUIRES_REALTIME_HTTP


def is_zhb_sufficient_field(field_name):
    # V12.6: True means ZHB alone is sufficient
    return field_name in ZHB_SUFFICIENT


# ═══════════════════════════════════════════════════════════════
# V14.2 新增：ZHB 本地数据集获取函数（HTTP 调用减半）
# 数据源：field_dict.md 第三节第 4 小节
# ═══════════════════════════════════════════════════════════════


def get_stock_basic_info_from_zhb(code: str) -> Optional[Dict[str, Any]]:
    """从 ZHB profile.dat 获取股票基本信息（V14.2 新增，替代东财 HTTP）。

    Returns:
        {"code": "600519", "name": "贵州茅台", "source": "zhb"}
        ZHB 数据缺失时返回 None
    """
    try:
        from zhb_client import get_stock_name_from_zhb

        name = get_stock_name_from_zhb(code)
        if name:
            return {"code": code, "name": name, "source": "zhb"}
        return None
    except Exception:
        return None


def get_concept_from_zhb(code: str) -> List[str]:
    """从 ZHB tdxchain.cfg 获取股票所属概念/产业链节点（V14.2 新增）。

    Returns:
        概念名称列表（如 ["5G", "白酒", "MSCI"]），ZHB 缺失时返回空列表
    """
    try:
        from zhb_client import get_stock_concepts_from_zhb

        return get_stock_concepts_from_zhb(code)
    except Exception:
        return []


def get_new_share_calendar_from_zhb() -> List[Dict[str, Any]]:
    """从 ZHB xgsg.cfg 获取新股申购日历（V14.2 新增，替代东财新股 API）。

    Returns:
        新股列表 [{"code", "name", "issue_date", "ipo_price", ...}],
        ZHB 缺失时返回空列表
    """
    try:
        from zhb_client import get_ipo_list

        return get_ipo_list()
    except Exception:
        return []


def get_special_tags_from_zhb() -> Dict[str, List[str]]:
    """从 ZHB pttab.dat 获取特别标签（红筹/AH/概念 等，V14.2 新增）。

    Returns:
        {标签名: [股票代码列表]}，ZHB 缺失时返回空字典
    """
    try:
        from zhb_client import get_special_tags_from_zhb as _impl

        return _impl()
    except Exception:
        return {}


def is_zhb_dataset_available() -> bool:
    """检查 ZHB 6 个新数据集是否至少有一个可用（V14.2 新增）。

    Returns:
        True 表示 ZHB 数据已加载且 profile/concept_chain 至少一个有数据
    """
    try:
        from zhb_client import get_zhb

        zhb = get_zhb()
        if zhb is None:
            return False
        return bool(zhb.stock_profile) or bool(zhb.concept_chain)
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════
# 统一规范数据接口 (Canonical Data API)
# ═══════════════════════════════════════════════════════════════


def get_canonical_stock_data(code: str, force_realtime: bool = False) -> Any:
    """获取强类型统一规范数据合约对象 (Canonical Stock Data)

    遵从以下重构路由策略：
      1. T+1日盘前 (<09:30) / 假日：100% 走 ZHB 本地提取，零网络开销。
      2. T日盘后 (15:00-24:00): 因当天的 ZHB 包在深夜前未生成，行情与资金流字段强制走 HTTP/TDX 接口获取 T 日实际收盘数据。
      3. T日盘中 (09:30-15:00): 4 大行情/资金流字段走 HTTP/TDX 实时；静态/估值/财务/股本/概念等 30+ 项走 ZHB。
      4. Boundary Validator: 自动对单位、边界及异常值进行清洗与归一化补全。
    """
    from stock_common.sc_schema import CanonicalStockData
    from stock_common.stock_calendar import is_workday
    from zhb_client import get_stock_name_from_zhb

    code_str = str(code).zfill(6)
    now = datetime.now()
    is_today_trading = is_workday(now.date())

    t_val = now.hour * 100 + now.minute
    is_pre_market = t_val < 930
    is_post_market = is_today_trading and (t_val >= 1500)
    is_trading_hours = is_today_trading and (930 <= t_val < 1500)

    # 1. 提取 ZHB 本地快照
    zhb_dict = {}
    try:
        from stock_common import get_zhb_single_stock_data

        zhb_dict = get_zhb_single_stock_data(code_str) or {}
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data get_zhb error: {_e}")

    # 判断行情与资金流是否需要走 HTTP / TDX 实时
    need_realtime_quote = force_realtime or is_trading_hours or is_post_market or not zhb_dict

    # V15.4 方案 C: per-field source label
    # 字典 key = 字段名 (e.g. "price", "mcap_yi", "industry")
    # 字典 value = 数据来源标签 (e.g. "realtime:push2", "realtime:tencent", "calculated", "missing")
    field_sources: Dict[str, str] = {}

    # 2. 实时/收盘行情 — V15.4 4 级 fallback 链
    # V16.0: 原 PUSH2_FIELD_MAP（f43/f44→price/high 映射表）已删除——
    # get_em_quote_full 直接返回规范字段名，L3 push2 fallback 直接遍历 em_quote_raw。
    rt_quote: Dict[str, Any] = {}  # 最终的行情 dict (cdata 字段名为 key)
    em_quote_raw: Dict[str, Any] = {}  # push2 原始字段 (f43/f44/...)

    if need_realtime_quote:
        # L1: TDX 实时
        try:
            from tdx_client import tdx_get_quote_full

            _tdx = tdx_get_quote_full(code_str) or {}
            if _tdx.get("price"):
                rt_quote = _tdx
                for _k in _tdx:
                    field_sources[_k] = "realtime:tdx"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data tdx_get_quote_full error: {_e}")

        # L2: 腾讯行情 (V16 端口优先级: 不封 IP，优先于 push2；参考仓库: 腾讯/通达信优先)
        if not rt_quote.get("price"):
            try:
                from stock_common import get_tencent_quote

                _tencent = get_tencent_quote(code_str) or {}
                if _tencent.get("price"):
                    # 腾讯返回的字段名大多与 cdata 一致, 直接 update
                    for _k, _v in _tencent.items():
                        if _v not in (None, 0, '', '0', '0.0'):
                            rt_quote[_k] = _v
                            field_sources[_k] = "realtime:tencent"
                    if rt_quote.get("price"):
                        _debug_log(f"get_canonical_stock_data tencent fallback OK ({code_str})")
            except Exception as _e:
                _debug_log(f"get_canonical_stock_data tencent fallback error ({code_str}): {_e}")

        # L3: 东财 push2 最后手段 (V16 端口优先级: 风控最严，仅 TDX/腾讯都失败时用)
        if not rt_quote.get("price"):
            try:
                from stock_common.sc_datasource import get_em_quote_full

                em_quote_raw = get_em_quote_full(code_str) or {}
                if em_quote_raw:
                    # V16.0: get_em_quote_full 返回的已是规范字段名（price/high/low/...），
                    # 直接遍历合并。原 PUSH2_FIELD_MAP 用 f43/f44/... 去 .get() 拿不到值 → push2 兜底从未生效。
                    for f_cdata, _v in em_quote_raw.items():
                        if f_cdata in ("name", "industry", "board", "list_date", "data_date"):
                            rt_quote[f_cdata] = _v
                            field_sources[f_cdata] = "realtime:push2"
                            continue
                        if _v not in (None, 0, '', '0', '0.0'):
                            # 数值字段转 float（push2 数值可能为字符串）
                            try:
                                rt_quote[f_cdata] = float(_v) if not isinstance(_v, str) else _v
                            except (ValueError, TypeError):
                                rt_quote[f_cdata] = _v
                            field_sources[f_cdata] = "realtime:push2"
                    if rt_quote.get("price"):
                        _debug_log(
                            f"get_canonical_stock_data push2 fallback OK ({code_str}) — {len(rt_quote)} fields mapped"
                        )
            except Exception as _e:
                _debug_log(f"get_canonical_stock_data push2 fallback error ({code_str}): {_e}")

    # 3. 实时/收盘资金流
    rt_fund = {}
    if need_realtime_quote:
        try:
            from tdx_client import tdx_get_fund_flow

            rt_fund = tdx_get_fund_flow(code_str) or {}
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data tdx_get_fund_flow error: {_e}")

    # 4. 字段清洗与 Boundary Validation (V15.4: 每字段独立 source 标签)
    basic_info = get_stock_basic_info_from_zhb(code_str)
    zhb_name = basic_info.get('name', '') if isinstance(basic_info, dict) else ''
    # name: 优先级 push2/tencent/tdx > ZHB
    name = str(
        rt_quote.get('name')
        or zhb_dict.get('name')
        or zhb_name
        or get_stock_name_from_zhb(code_str)
        or ''
    )
    if not field_sources.get("name"):
        if name:
            field_sources["name"] = "zhb:static" if zhb_name == name else "calculated"

    # ─────────────────────────────────────────────────────────
    # 行情字段 (price/change_pct/open/high/low/amount/turnover)
    # V15.4: 已在 L1/L2/L3 标记 source, 这里仅做字段清洗
    # ─────────────────────────────────────────────────────────
    def _extract_with_source(field_name, rt_default=None, zhb_default=None):
        """V15.4: 提取字段并按 source 优先级处理。"""
        if rt_quote.get(field_name) not in (None, 0, '', '0', '0.0') and need_realtime_quote:
            return _safe_float(rt_quote.get(field_name)), field_sources.get(
                field_name, "realtime:unknown"
            )
        if zhb_dict.get(field_name) not in (None, 0, '', '0', '0.0'):
            return _safe_float(zhb_dict.get(field_name)), "zhb:t-1"
        return _safe_float(rt_default if rt_default is not None else 0), "missing"

    price, price_src = _extract_with_source("price", rt_quote.get("price"), zhb_dict.get("price"))
    # V15.5.3: ZHB tdxstat 无 price 字段，非交易日/盘前缺失时走 get_stock_price
    # 完整链（ZHB→TDX→腾讯，15s TTL）——修复 med/lng 报告 price=0.00
    if not price and price_src == "missing":
        try:
            _sp = get_stock_price(code_str)
            if _sp:
                price = _safe_float(_sp)
                price_src = "realtime:tdx"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data get_stock_price fallback error: {_e}")
    field_sources["price"] = price_src
    change_pct, _ = _extract_with_source(
        "change_pct", rt_quote.get("change_pct"), zhb_dict.get("change_pct")
    )
    field_sources["change_pct"] = field_sources.get("change_pct", _ if _ else price_src)
    open_p, _ = _extract_with_source("open", rt_quote.get("open"), zhb_dict.get("open"))
    field_sources["open"] = field_sources.get("open", price_src)
    high_p, _ = _extract_with_source("high", rt_quote.get("high"), zhb_dict.get("high"))
    field_sources["high"] = field_sources.get("high", price_src)
    low_p, _ = _extract_with_source("low", rt_quote.get("low"), zhb_dict.get("low"))
    field_sources["low"] = field_sources.get("low", price_src)
    prev_close, _ = _extract_with_source(
        "prev_close", rt_quote.get("last_close"), zhb_dict.get("prev_close")
    )
    field_sources["prev_close"] = field_sources.get("prev_close", price_src)
    amount_wan, amount_src = _extract_with_source(
        "amount_wan", rt_quote.get("amount_wan"), zhb_dict.get("amount")
    )
    field_sources["amount_wan"] = amount_src
    # V16.0: volume_hand 不再从 ZHB 兜底 — ZHB Col[24] 曾误映射为 volume(成交量)，
    # 经核实为恒定静态数据(非成交量，已改名 unknown_24)。真实成交量只能来自实时行情。
    volume_hand, _ = _extract_with_source(
        "volume_hand", rt_quote.get("volume_hand"), None
    )
    field_sources["volume_hand"] = field_sources.get("volume_hand", price_src)
    turnover_pct, _ = _extract_with_source(
        "turnover_pct", rt_quote.get("turnover_pct"), zhb_dict.get("turnover_pct")
    )
    # V16.2.3 修复: TDX 0x010C 无换手率、ZHB 无此字段 → sht 换手率恒 0。
    # 腾讯行情 f38 有换手率且 @cached（命中无网络开销），补作兜底。
    if not turnover_pct:
        try:
            from stock_common import get_tencent_quote

            _tq = get_tencent_quote(code_str) or {}
            _tv = _safe_float(_tq.get("turnover_pct") or 0)
            if _tv > 0:
                turnover_pct = _tv
                field_sources["turnover_pct"] = "realtime:tencent"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data turnover tencent fallback error: {_e}")
    field_sources["turnover_pct"] = field_sources.get("turnover_pct", price_src)

    # 估值类 (ZHB 优先, push2/tdx 兜底)
    pe_ttm = _safe_float(zhb_dict.get('pe_ttm') or rt_quote.get('pe_ttm'))
    if pe_ttm < 0 or pe_ttm > 10000:
        pe_ttm = 0.0
    field_sources["pe_ttm"] = (
        "zhb:static" if zhb_dict.get('pe_ttm') else field_sources.get("pe_ttm", "missing")
    )
    pe_dynamic = _safe_float(zhb_dict.get('pe_dynamic') or rt_quote.get('pe_dynamic'))
    field_sources["pe_dynamic"] = (
        "zhb:static" if zhb_dict.get('pe_dynamic') else field_sources.get("pe_dynamic", "missing")
    )
    pb = _safe_float(zhb_dict.get('pb') or rt_quote.get('pb'))
    # V15.5.3: pb 兜底 — ZHB 无 pb 字段，用 TDX 每股净资产计算 (price / bvps)
    if pb <= 0 and price > 0:
        try:
            from tdx_client import tdx_get_finance_info

            _fin = tdx_get_finance_info(code_str) or {}
            _bvps = _safe_float(_fin.get('meigujingzichan'))
            if _bvps > 0:
                pb = round(price / _bvps, 2)
                field_sources["pb"] = "calculated"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data pb calc error: {_e}")
    field_sources["pb"] = "zhb:static" if zhb_dict.get('pb') else field_sources.get("pb", "missing")
    # V16.2: 股息率主字段接入 push2 f126（ZHB 无值或旧值时用实时）
    dividend_yield = _safe_float(zhb_dict.get('dividend_yield') or rt_quote.get('dividend_yield'))
    field_sources["dividend_yield"] = (
        "zhb:static" if zhb_dict.get('dividend_yield') else field_sources.get("dividend_yield", "missing")
    )
    # V15.4: 振幅/量比 (push2 f171/f49)
    amplitude_pct = _safe_float(rt_quote.get('amplitude_pct') or zhb_dict.get('amplitude_pct') or 0)
    if amplitude_pct <= 0 and high_p > 0 and low_p > 0 and prev_close > 0:
        # L4 公式推算: 振幅 = (high - low) / last_close
        amplitude_pct = round((high_p - low_p) / prev_close * 100, 2)
        field_sources["amplitude_pct"] = "calculated"
    else:
        field_sources["amplitude_pct"] = field_sources.get("amplitude_pct", "missing")
    vol_ratio = _safe_float(rt_quote.get('vol_ratio') or 0)
    field_sources["vol_ratio"] = field_sources.get("vol_ratio", "missing")

    # 资金流类（V16.1.7 标签修正: tdx_get_fund_flow 实际委托东财 HTTP，标签应为 eastmoney 非 tdx）
    main_net_buy_wan = _safe_float(
        rt_fund.get('main_net_wan')
        if need_realtime_quote and rt_fund.get('main_net_wan') is not None
        else zhb_dict.get('main_net_buy_amount')
    )
    field_sources["main_net_buy_wan"] = (
        "realtime:eastmoney" if rt_fund.get('main_net_wan') is not None else "zhb:t-1"
    )
    main_net_buy_hands = _safe_float(
        rt_fund.get('main_net_hands') if need_realtime_quote else zhb_dict.get('main_net_buy_hands')
    )
    field_sources["main_net_buy_hands"] = (
        "realtime:eastmoney" if rt_fund.get('main_net_hands') is not None else "zhb:t-1"
    )
    main_net_buy_wan_1d = _safe_float(zhb_dict.get('main_net_buy_amount_1d'))
    field_sources["main_net_buy_wan_1d"] = "zhb:t-1"

    # 财务与股本类
    roe = _safe_float(zhb_dict.get('roe')) if zhb_dict.get('roe') is not None else None
    field_sources["roe"] = "zhb:static" if roe is not None else "missing"
    gross_margin = (
        _safe_float(zhb_dict.get('gross_margin'))
        if zhb_dict.get('gross_margin') is not None
        else None
    )
    field_sources["gross_margin"] = "zhb:static" if gross_margin is not None else "missing"
    net_profit_margin = (
        _safe_float(zhb_dict.get('net_profit_margin'))
        if zhb_dict.get('net_profit_margin') is not None
        else None
    )
    field_sources["net_profit_margin"] = (
        "zhb:static" if net_profit_margin is not None else "missing"
    )
    net_profit = _safe_float(zhb_dict.get('net_profit'))
    field_sources["net_profit"] = "zhb:static" if net_profit else "missing"
    revenue = _safe_float(zhb_dict.get('revenue'))
    field_sources["revenue"] = "zhb:static" if revenue else "missing"
    # V16.2: EPS 主字段接入 push2 f55（实时 T 日数据源优先，ZHB T-1 兜底）
    eps = _safe_float(rt_quote.get('eps') or zhb_dict.get('eps'))
    field_sources["eps"] = (
        "realtime:push2" if rt_quote.get('eps') else ("zhb:static" if eps else "missing")
    )

    # 股本类 — V15.4 4 级 fallback: push2/tdx/tencent > ZHB
    # V16.3 A2 注: rt_quote 若来自 get_stock_info(TDX finance) 其 total_shares 单位是**股**，
    # 直接当万股会错 10000 倍——当前实测 rt_quote 不含股本（走下方 capital_cache 万股兜底，
    # 值正确），此防御注释防止未来 rt_quote 加股本字段时误用。
    total_shares_wan = _safe_float(rt_quote.get('total_shares') or zhb_dict.get('total_shares'))
    # V15.5.3: 股本兜底 — sc_capital_cache（V10.1 全局股本缓存，ZHB 无 total_shares 字段）
    if not total_shares_wan:
        try:
            from stock_common.sc_capital_cache import get_share_capital as _get_cap

            _cap = _get_cap(code_str) or {}
            total_shares_wan = _safe_float(_cap.get('total_shares'))
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data total_shares fallback error: {_e}")
    if rt_quote.get('total_shares') and rt_quote.get('total_shares') > 0:
        field_sources["total_shares_wan"] = field_sources.get("total_shares", "realtime:unknown")
    else:
        field_sources["total_shares_wan"] = "zhb:static"
    float_shares_wan = _safe_float(rt_quote.get('float_shares') or zhb_dict.get('float_shares'))
    # V15.5.3: 流通股本兜底 — sc_capital_cache
    if not float_shares_wan:
        try:
            from stock_common.sc_capital_cache import get_share_capital as _get_cap

            _cap = _get_cap(code_str) or {}
            float_shares_wan = _safe_float(_cap.get('float_shares'))
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data float_shares fallback error: {_e}")
    if rt_quote.get('float_shares') and rt_quote.get('float_shares') > 0:
        field_sources["float_shares_wan"] = field_sources.get("float_shares", "realtime:unknown")
    else:
        field_sources["float_shares_wan"] = "zhb:static"

    # 市值类 — V15.4: 优先 rt_quote.mcap_yi, 否则 L4 公式推算
    mcap_yi = _safe_float(
        rt_quote.get('mcap_yi')
        if need_realtime_quote and rt_quote.get('mcap_yi')
        else zhb_dict.get('mcap_yi')
    )
    if mcap_yi <= 0 and total_shares_wan > 0 and price > 0:
        # L4 公式推算: mcap = total_shares * price / 1e8
        mcap_yi = round((total_shares_wan * 10000 * price) / 1e8, 2)
        field_sources["mcap_yi"] = "calculated"
    else:
        field_sources["mcap_yi"] = field_sources.get("mcap_yi", "missing")
    float_mcap_yi = _safe_float(
        rt_quote.get('float_mcap_yi')
        if need_realtime_quote and rt_quote.get('float_mcap_yi')
        else zhb_dict.get('float_mcap_yi')
    )
    if float_mcap_yi <= 0 and float_shares_wan > 0 and price > 0:
        float_mcap_yi = round((float_shares_wan * 10000 * price) / 1e8, 2)
        field_sources["float_mcap_yi"] = "calculated"
    else:
        field_sources["float_mcap_yi"] = field_sources.get("float_mcap_yi", "missing")

    holder_count = int(zhb_dict.get('holder_count') or 0)
    field_sources["holder_count"] = "zhb:static" if holder_count else "missing"

    # 历史衍生指标
    change_5d = _safe_float(zhb_dict.get('change_5d'))
    field_sources["change_5d"] = "zhb:static" if change_5d else "missing"
    change_10d = _safe_float(zhb_dict.get('change_10d'))
    field_sources["change_10d"] = "zhb:static" if change_10d else "missing"
    change_20d = _safe_float(zhb_dict.get('change_20d'))
    field_sources["change_20d"] = "zhb:static" if change_20d else "missing"
    # V15.1: 启用 change_30d（tdxstat.cfg Col[18]）
    change_30d = _safe_float(zhb_dict.get('change_30d'))
    field_sources["change_30d"] = "zhb:static" if change_30d else "missing"
    change_60d = _safe_float(zhb_dict.get('change_60d'))
    field_sources["change_60d"] = "zhb:static" if change_60d else "missing"
    change_ytd = _safe_float(zhb_dict.get('change_ytd'))
    field_sources["change_ytd"] = "zhb:static" if change_ytd else "missing"
    streak_days = int(zhb_dict.get('streak_days') or 0)
    field_sources["streak_days"] = "zhb:static" if streak_days else "missing"
    # V16.2: 52 周高低价主字段接入 push2 f174/f175（实时优先，ZHB T-1 兜底）
    high_52w = _safe_float(rt_quote.get('high_52w') or zhb_dict.get('high_52w'))
    field_sources["high_52w"] = (
        "realtime:push2" if rt_quote.get('high_52w') else ("zhb:static" if high_52w else "missing")
    )
    low_52w = _safe_float(rt_quote.get('low_52w') or zhb_dict.get('low_52w'))
    field_sources["low_52w"] = (
        "realtime:push2" if rt_quote.get('low_52w') else ("zhb:static" if low_52w else "missing")
    )
    ipo_price = _safe_float(zhb_dict.get('ipo_price'))
    field_sources["ipo_price"] = "zhb:static" if ipo_price else "missing"
    employee_count = int(zhb_dict.get('employee_count') or 0)
    field_sources["employee_count"] = "zhb:static" if employee_count else "missing"

    # V15.4 方案 C: industry fallback 链（V16.1.7 调整）
    # 优先级: push2 f127 (免费副产品, 行情 L3 已调 get_em_quote_full 零额外请求)
    #        > TDX boards (TCP 不易封禁, 行情走 TDX/腾讯时行业走此级)
    #        > ZHB static (盘前/静态兜底)
    # 注: 行情链正常(TDX/腾讯成功)时 em_quote_raw 为空 → 行业自动走 TDX TCP, 不碰东财;
    #     仅行情 fallback 到 push2 时行业才用 push2 f127 (此时零额外请求)。腾讯级已删(无 industry 字段, 死级)
    industry = ''
    board = ''
    industry_code = str(zhb_dict.get('industry_code') or '')
    # V16.2.17: L0 东财申万二级行业（datacenter 域低风险，全市场映射一次性缓存，零逐股请求；
    # 东财二级与申万二级同源（半导体/白酒Ⅱ/光学光电子），统一"申万二级"口径）
    try:
        from stock_common import get_em_industry_l2

        _em_ind = get_em_industry_l2(code_str)
        if _em_ind:
            industry = _em_ind
            field_sources["industry"] = "realtime:em-datacenter"
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data em industry: {_e}")
    # L1: push2 (em_quote_raw 已在 L3 push2 fallback 中填充, 免费副产品)
    # V16.0: get_em_quote_full 返回规范名 — f127→industry, f128→board(地域)
    if em_quote_raw.get('industry') and em_quote_raw['industry'] not in (None, '', 'None'):
        industry = str(em_quote_raw['industry']).strip()
        field_sources["industry"] = "realtime:push2"
    # get_em_quote_full 不返回 industry_code，industry_code 以 ZHB tdxstat2 Col[13] 为可靠来源
    if em_quote_raw.get('board') and em_quote_raw['board'] not in (None, '', 'None'):
        board = str(em_quote_raw['board']).strip()
        field_sources["board"] = "realtime:push2"
    # L2: TDX boards（TCP 不易封禁）
    if not industry:
        try:
            from tdx_client import tdx_get_belong_boards

            boards = tdx_get_belong_boards(code_str)
            if boards and boards.get("industry"):
                industry = boards["industry"][0].get("name", "")
                field_sources["industry"] = field_sources.get("industry", "tdx:boards")
            if not board and boards and boards.get("area"):
                board = boards["area"][0].get("name", "")
                field_sources["board"] = "tdx:boards"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data tdx boards error: {_e}")
    # L3: ZHB 静态（profile.dat）—— 最后的兜底
    if not industry:
        if basic_info and isinstance(basic_info, dict) and basic_info.get('industry'):
            industry = basic_info['industry']
            field_sources["industry"] = "zhb:static"
        elif zhb_dict.get('industry'):
            industry = zhb_dict['industry']
            field_sources["industry"] = "zhb:static"
    # 关键: 剥离"子"后缀（"光学光电子" → "光学光电"）
    if industry.endswith("子") and len(industry) > 2:
        industry = industry[:-1]
    if not industry:
        field_sources["industry"] = field_sources.get("industry", "missing")
    if not field_sources.get("industry_code"):
        field_sources["industry_code"] = field_sources.get("industry", "missing")
    if not field_sources.get("board"):
        field_sources["board"] = "missing"
    # concepts: 优先 TDX concept (TCP), 其次 push2 f129 (免费副产品), 最后 ZHB concept_chain
    concepts_list = []
    try:
        from tdx_client import tdx_get_belong_boards

        boards = tdx_get_belong_boards(code_str)
        if boards and boards.get("concept"):
            concepts_list = [c.get("name", "") for c in boards["concept"] if c.get("name")]
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data tdx concepts error: {_e}")
    # V16.1.7: push2 f129 概念列表兜底（get_em_quote_full 已解析 f129→concepts）
    if not concepts_list and em_quote_raw.get('concepts'):
        try:
            concepts_list = [str(c).strip() for c in em_quote_raw['concepts'] if str(c).strip()]
            field_sources["concepts"] = "realtime:push2"
        except Exception:
            pass
    # ZHB concept_chain 仅作补充（V15.1 后已重写为板块代码→名称映射，不再支持成分股）
    if not concepts_list:
        concepts_list = get_concept_from_zhb(code_str)
        field_sources["concepts"] = "zhb:concept_chain"
    else:
        field_sources["concepts"] = field_sources.get("concepts", "tdx:boards")

    # V16.0: 上市日期（list_date）— 从 push2 f189 / rt_quote / em_quote_raw 提取
    # V16.2 修复: 去掉 data_date 回退（data_date 是本机日期，上市日期缺失时置空而非写成当天）
    list_date = str(
        rt_quote.get("list_date")
        or em_quote_raw.get("list_date")
        or ""
    )
    if list_date and list_date not in ("None", "nan"):
        field_sources["list_date"] = "realtime:push2" if rt_quote.get("list_date") else "missing"
    else:
        list_date = ""

    source_tag = "http/tdx" if need_realtime_quote and rt_quote else "zhb"
    time_anchor_tag = "t_day" if (is_trading_hours or is_post_market) else "t-1"

    return CanonicalStockData(
        code=code_str,
        name=name,
        price=price,
        change_pct=change_pct,
        open=open_p,
        high=high_p,
        low=low_p,
        prev_close=prev_close,
        amount_wan=amount_wan,
        volume_hand=volume_hand,
        pe_ttm=pe_ttm,
        pe_dynamic=pe_dynamic,
        pb=pb,
        dividend_yield=dividend_yield,
        turnover_pct=turnover_pct,
        main_net_buy_wan=main_net_buy_wan,
        main_net_buy_hands=main_net_buy_hands,
        main_net_buy_wan_1d=main_net_buy_wan_1d,
        roe=roe,
        gross_margin=gross_margin,
        net_profit_margin=net_profit_margin,
        net_profit=net_profit,
        revenue=revenue,
        eps=eps,
        total_shares_wan=total_shares_wan,
        float_shares_wan=float_shares_wan,
        mcap_yi=mcap_yi,
        float_mcap_yi=float_mcap_yi,
        holder_count=holder_count,
        change_5d=change_5d,
        change_10d=change_10d,
        change_20d=change_20d,
        change_30d=change_30d,
        change_60d=change_60d,
        change_ytd=change_ytd,
        streak_days=streak_days,
        high_52w=high_52w,
        low_52w=low_52w,
        ipo_price=ipo_price,
        employee_count=employee_count,
        list_date=list_date,
        industry=industry,
        industry_code=industry_code,
        board=board,
        concepts=tuple(concepts_list),
        data_source=source_tag,
        time_anchor=time_anchor_tag,
        is_valid=True,
        # V15.4 方案 C: per-field source label
        field_sources=dict(field_sources),
        # V16.1: push2 扩展字段（f51/f52 涨停跌停、f55/f92 EPS/BPS、f126 股息率、
        # f162-167 PE/PB、f174/f175 52周、f137-146 资金流、f198 行业码、f80 交易时段、
        # f178 5日资金流数组、data_date 行情日期）— 从 rt_quote/em_quote_raw 透传
        limit_up=_safe_float(rt_quote.get("limit_up") or em_quote_raw.get("limit_up") or 0),
        limit_down=_safe_float(rt_quote.get("limit_down") or em_quote_raw.get("limit_down") or 0),
        bps=_safe_float(rt_quote.get("bps") or em_quote_raw.get("bps") or 0),
        pe_more=_safe_float(rt_quote.get("pe_more") or em_quote_raw.get("pe_more") or 0),
        industry_code_push2=str(
            rt_quote.get("industry_code_push2") or em_quote_raw.get("industry_code_push2") or ""
        ),
        trading_periods=tuple(
            rt_quote.get("trading_periods") or em_quote_raw.get("trading_periods") or ()
        ),
        report_period=str(rt_quote.get("report_period") or em_quote_raw.get("report_period") or ""),
        quote_date=str(rt_quote.get("data_date") or em_quote_raw.get("data_date") or ""),
        fund_main_today=_safe_float(rt_quote.get("fund_main_today") or em_quote_raw.get("fund_main_today") or 0),
        fund_super_today=_safe_float(rt_quote.get("fund_super_today") or em_quote_raw.get("fund_super_today") or 0),
        fund_large_today=_safe_float(rt_quote.get("fund_large_today") or em_quote_raw.get("fund_large_today") or 0),
        fund_mid_today=_safe_float(rt_quote.get("fund_mid_today") or em_quote_raw.get("fund_mid_today") or 0),
        fund_main_5d=_safe_float(rt_quote.get("fund_main_5d") or em_quote_raw.get("fund_main_5d") or 0),
        fund_super_5d=_safe_float(rt_quote.get("fund_super_5d") or em_quote_raw.get("fund_super_5d") or 0),
        fund_large_5d=_safe_float(rt_quote.get("fund_large_5d") or em_quote_raw.get("fund_large_5d") or 0),
        fund_main_10d=_safe_float(rt_quote.get("fund_main_10d") or em_quote_raw.get("fund_main_10d") or 0),
        fund_super_10d=_safe_float(rt_quote.get("fund_super_10d") or em_quote_raw.get("fund_super_10d") or 0),
        fund_large_10d=_safe_float(rt_quote.get("fund_large_10d") or em_quote_raw.get("fund_large_10d") or 0),
        fund_5d_array=tuple(rt_quote.get("fund_5d_array") or em_quote_raw.get("fund_5d_array") or ()),
    )


def get_canonical_stock_data_batch(codes: List[str]) -> Dict[str, Any]:
    """批量获取 CanonicalStockData 强类型字典。"""
    res = {}
    for c in codes:
        res[c] = get_canonical_stock_data(c)
    return res


# Legacy three-tier classification (kept for backward compat)

_REALTIME_FIELDS = frozenset(
    {
        "change_pct",
        "amount",
        "price",
        "open",
        "high",
        "low",
        "prev_close",
    }
)

_NEAR_REALTIME_FIELDS = frozenset(
    {
        "main_net_buy_hands",
        "main_net_buy_hands_1d",
        "main_net_buy_amount",
        "main_net_buy_amount_1d",
        "streak_days",
    }
)

_STATIC_FIELDS = frozenset(
    {
        "pe_ttm",
        "pe_dynamic",
        "pb",
        "dividend_yield",
        "high_52w",
        "low_52w",
        "change_ytd",
        "change_5d",
        "change_10d",
        "change_20d",
        "change_30d",
        "change_60d",
        "employee_count",
        "ipo_price",
        "industry_code",
        "industry",
        "total_shares",
        "float_shares",
        "turnover_pct",
        "mcap",
        "float_mcap",
    }
)


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
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
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
    """判断实时字段是否可以使用 ZHB 内存数据。

    规则（根据真实物理更新规律）：
    1. 休市日/周末/节假日：100% 走 ZHB 本地内存提取（T-1日即最新已闭市数据）。
    2. 交易日 00:00 - 09:30 (盘前)：100% 走 ZHB 本地内存提取（夜间已更新为 T-1日收盘数据）。
    3. 交易日 09:30 - 24:00 (含盘中 09:30-15:00 与盘后 15:00-24:00)：
       必须走 HTTP/TDX 实时行情（在 15:00-24:00 磁盘上的 ZHB 数据包仍然是 T-1 日，
       用户要获取的是今天 T 日的最新收盘数据）。
    """
    try:
        from stock_common import is_workday

        now = datetime.now()
        today = now.date()
        if not is_workday(today):
            return True
        t = now.hour * 100 + now.minute
        return t < 930
    except Exception as _e:
        _debug_log(f"data_provider _should_use_zhb_for_realtime error: {_e}")
        return _get_market_status() != "trading"


def _parse_zhb_date(zhb_date_str: str):
    """V16.2: 统一解析 ZHB 日期（支持 YYYYMMDD 与 YYYY-MM-DD 两种格式）。"""
    if not zhb_date_str:
        return None
    try:
        s = str(zhb_date_str).strip()
        if len(s) == 8 and s.isdigit():
            return datetime.strptime(s, "%Y%m%d").date()
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _get_zhb_date_offset() -> int:
    """计算ZHB数据日期相对于今天的交易日偏移。

    返回值：
      0 = ZHB数据就是今天的（只在盘前且当天ZHB已更新时可能）
      1 = ZHB数据是昨天的（最常见情况）
      2+ = ZHB数据是更早的（非交易日运行时）
    """
    try:
        from stock_common import get_zhb_data_date

        zhb_date_str = get_zhb_data_date()
        zhb_date = _parse_zhb_date(zhb_date_str)
        if zhb_date is None:
            return 99

        today = datetime.now().date()

        if zhb_date >= today:
            return 0
        return (today - zhb_date).days
    except Exception:
        return 99


def _get_trading_date_offset() -> int:
    """计算ZHB数据日期相对于最新交易日的偏移量（ΔT）。

    这是日期对齐器的核心函数。它比较的是：
    - ZHB数据日期（T_zhb）
    - API行情能够获取到的最新交易日期（T_quote）

    返回值（ΔT）：
      0 = ZHB与API基准同频（周末/盘前/16:30后）
      1 = ZHB比API慢一天（盘中运行）
      2+ = ZHB数据严重过期

    时间场景映射：
      盘前(00:00-09:15): ΔT=0（ZHB和API都是昨天收盘数据）
      盘中(09:30-15:00): ΔT=1（API是今天实时，ZHB是昨天）
      盘后(15:00-16:30): ΔT=1（API是今天收盘，ZHB是昨天）
      盘后(16:30后): ΔT=0（新ZHB已生成）
      非交易日: ΔT=0（都是上一交易日数据）
    """
    try:
        from stock_common import get_zhb_data_date
        from stock_common.stock_calendar import is_workday, get_last_trading_day

        zhb_date_str = get_zhb_data_date()
        zhb_date = _parse_zhb_date(zhb_date_str)
        if zhb_date is None:
            return 99

        today = datetime.now().date()
        now = datetime.now()

        last_td = get_last_trading_day(today)

        if is_workday(today):
            if now.hour < 9 or (now.hour == 9 and now.minute < 30):
                if zhb_date >= last_td - timedelta(days=1):
                    return 0
                return (last_td - zhb_date).days
            elif now.hour >= 16:
                if zhb_date >= last_td:
                    return 0
                return (last_td - zhb_date).days
            else:
                if zhb_date >= last_td - timedelta(days=1):
                    return 1
                return (last_td - zhb_date).days + 1
        else:
            if zhb_date >= last_td:
                return 0
            return (last_td - zhb_date).days
    except Exception:
        return _get_zhb_date_offset()


# ═══════════════════════════════════════════════════
# 原子数据获取函数
# ═══════════════════════════════════════════════════


@cached(category="stock_quote", ttl_seconds=15)
def get_stock_price(code: str) -> Optional[float]:
    """获取股票实时价格。

    优先级：ZHB(盘后) → TDX(TCP+内部缓存) → 腾讯(HTTP fallback)
    TTL：15秒（盘中快速刷新，盘后及开盘前走ZHB本地解析）
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
        except Exception as _e:
            _debug_log(f"data_provider error: {_e}")
            pass

    # TDX优先（TCP协议，内部含缓存+腾讯兜底补强）
    try:
        from tdx_client import tdx_get_quote_full

        q = tdx_get_quote_full(code)
        if q:
            p = _safe_float(q.get("price", 0))
            if p > 0:
                return p
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # 腾讯HTTP最后兜底
    try:
        from stock_common import get_tencent_quote

        q = get_tencent_quote(code)
        if q:
            return _safe_float(q.get("price", 0))
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False),
)  # V15.2: 拒绝 None/空（但允许 0 值）
def get_pe_ttm(code: str) -> Optional[float]:
    """V12.6: PE_TTM uses ZHB only, no HTTP fallback."""
    try:
        from stock_common import get_zhb_single_stock_data

        zhb = get_zhb_single_stock_data(code)
        if zhb:
            pe = _safe_float(zhb.get("pe_ttm", 0))
            if pe > 0:
                return pe
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False),
)  # V15.2: 拒绝 None/空（但允许 0 值）
def get_pb(code: str) -> Optional[float]:
    """V12.6: PB uses ZHB only, no HTTP fallback."""
    try:
        from stock_common import get_zhb_single_stock_data

        zhb = get_zhb_single_stock_data(code)
        if zhb:
            pb = _safe_float(zhb.get("pb", 0))
            if pb > 0:
                return pb
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["dividend"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False),
)  # V15.2: 拒绝 None/空（但允许 0 值）
def get_dividend_yield(code: str) -> Optional[float]:
    """获取股息率。

    静态字段：ZHB only（TDX和腾讯都不直接返回股息率，ZHB有完整数据）。
    TTL：30天（分红半年才变，价格驱动日变但30天足够）。
    """
    try:
        from stock_common import get_zhb_dividend_yield, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=3):
            yield_val = get_zhb_dividend_yield(code)
            if yield_val:
                return yield_val
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(category="zhb_data", ttl_seconds=TTL["basic_info"], trading_day=True)
def get_net_profit_kcf(code: str) -> Optional[float]:
    """获取扣非净利润（万元）。

    V16.0: tdxstat.cfg Col[14]，2026-08-03 联网核实与东财 KCFJCXSYJLR 14/14 匹配。
    静态字段（财报期更新），ZHB only。
    用途：净利润质量筛选（扣非 vs 归母差异）、基本面离线快照、盘前扫描。
    """
    try:
        from stock_common import get_zhb_net_profit_kcf, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=3):
            v = get_zhb_net_profit_kcf(code)
            if v is not None:
                return v
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data", ttl_seconds=7 * 86400, valid_if=make_valid_if(check_zeros=False)
)  # V15.2: tuple 不做空值检查，只拒 None
def get_52w_range(code: str) -> Optional[tuple]:
    """获取52周高低价区间。

    静态字段：优先ZHB → K线计算。
    TTL：7天（52周高低极少变化，仅创新高/低时变）
    """
    try:
        from stock_common import get_zhb_52w_range, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=7):
            high, low = get_zhb_52w_range(code)
            if high > 0 and low > 0:
                return (high, low)
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # Fallback：从TDX K线数据计算52周高低
    try:
        from tdx_client import tdx_get_security_bars

        keys, rows = tdx_get_security_bars(code, count=260)
        if keys and rows:
            idx_high = keys.index('high') if 'high' in keys else 3
            idx_low = keys.index('low') if 'low' in keys else 4
            highs = [_safe_float(r[idx_high]) for r in rows if r[idx_high]]
            lows = [_safe_float(r[idx_low]) for r in rows if r[idx_low]]
            if highs and lows:
                h, l = max(highs), min(lows)
                if h > 0 and l > 0:
                    return (h, l)
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(category="stock_quote", ttl_seconds=1800, trading_day=True)
def get_change_pct(code: str) -> Optional[float]:
    """获取涨跌幅。

    优先级：ZHB(盘后) → TDX(TCP+内部缓存) → 腾讯(HTTP fallback)
    TTL：30分钟 + 交易日模式
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
        except Exception as _e:
            _debug_log(f"data_provider error: {_e}")
            pass

    # TDX优先（TCP协议，内部含缓存+腾讯兜底补强）
    try:
        from tdx_client import tdx_get_quote_full

        q = tdx_get_quote_full(code)
        if q:
            return _safe_float(q.get("change_pct", 0))
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # 腾讯HTTP最后兜底
    try:
        from stock_common import get_tencent_quote

        q = get_tencent_quote(code)
        if q:
            return _safe_float(q.get("change_pct", 0))
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False),
)  # V15.2: 拒绝 None/空
def get_change_ytd(code: str) -> Optional[float]:
    """获取年初至今涨幅。

    静态字段：优先ZHB → K线计算。
    """
    try:
        from stock_common import get_zhb_change_ytd, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=3):
            return get_zhb_change_ytd(code)
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # Fallback：从TDX K线数据近似计算年初至今涨幅
    try:
        from tdx_client import tdx_get_security_bars

        keys, rows = tdx_get_security_bars(code, count=260)
        if keys and rows:
            idx_close = keys.index('close') if 'close' in keys else 2
            current_price = _safe_float(rows[0][idx_close])
            # rows从新到旧，取约250个交易日前作为年初近似
            if len(rows) >= 2:
                year_start_idx = min(len(rows) - 1, 243)
                year_start_price = _safe_float(rows[year_start_idx][idx_close])
                if year_start_price > 0 and current_price > 0:
                    return (current_price - year_start_price) / year_start_price * 100
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(category="stock_quote", ttl_seconds=1800, trading_day=True)
def get_amount_wan(code: str) -> Optional[float]:
    """获取成交额（万元）。

    V15.1: 优先级 ZHB（T-1）→ 腾讯 HTTP → TDX TCP
    盘中/盘后/盘前都用 ZHB T-1 数据（1 天延迟可接受），
    ZHB 缺失时降级到腾讯/TDX 实时数据。
    TTL：30分钟 + 交易日模式
    """
    # 优先级 1：ZHB（T-1 数据，1 天延迟可接受）
    try:
        from stock_common import get_zhb_amount_wan, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=1):
            amount = get_zhb_amount_wan(code)
            if amount and amount > 0:
                return amount
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass

    # Fallback 1：腾讯 HTTP（实时，但仅盘中使用）
    try:
        from stock_common import get_tencent_quote

        q = get_tencent_quote(code)
        if q:
            # V16.0: get_tencent_quote 返回的 amount_wan 已是万元（tdx_client.py:476），
            # 原代码读 amount 再 /10000 取不到值且单位错误
            amt = _safe_float(q.get("amount_wan", 0))
            if amt > 0:
                return amt
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # Fallback 2：TDX TCP
    try:
        from tdx_client import tdx_get_quote_full

        q = tdx_get_quote_full(code)
        if q:
            return _safe_float(q.get("amount_wan", 0))
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(),
)  # V15.2: 拒绝 None/空 dict/全 0
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
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    try:
        from tdx_client import tdx_get_fund_flow, tdx_get_history_fund_flow

        ff = tdx_get_fund_flow(code)
        if ff:
            history = tdx_get_history_fund_flow(code, days=5)
            main_net_buy_hands_1d = 0
            main_net_buy_amount_1d = 0
            if history and len(history) >= 2:
                prev_day = history[1]
                main_net_buy_hands_1d = _safe_float(prev_day.get("main_net", 0))
                main_net_buy_amount_1d = main_net_buy_hands_1d
            return {
                "main_net_buy_hands": _safe_float(ff.get("main_net_hands", 0)),
                "main_net_buy_hands_1d": main_net_buy_hands_1d,
                "main_net_buy_hands_2d": 0,
                "main_net_buy_amount": _safe_float(ff.get("main_net_wan", 0)),
                "main_net_buy_amount_1d": main_net_buy_amount_1d,
                "main_net_buy_amount_2d": 0,
            }
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
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
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(category="basic_info_static", ttl_seconds=TTL["basic_info_static"])
def get_stock_info(code: str) -> Optional[Dict[str, Any]]:
    """获取股票基本信息（综合）。"""
    try:
        from stock_common import get_stock_info

        return get_stock_info(code)
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


# ═══════════════════════════════════════════════════
# 新增常用字段函数
# ═══════════════════════════════════════════════════


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False),
)  # V15.2: 拒绝 None/空
def get_turnover_pct(code: str) -> Optional[float]:
    """V12.6: turnover_pct uses ZHB only, no HTTP fallback."""
    try:
        from stock_common import get_zhb_single_stock_data

        zhb = get_zhb_single_stock_data(code)
        if zhb:
            turnover = _safe_float(zhb.get("turnover_pct", 0))
            if turnover > 0:
                return turnover
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
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
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=3):
            zhb = get_zhb_single_stock_data(code)
            if zhb:
                total = _safe_float(zhb.get("total_shares", 0))
                if total > 0:
                    return total
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False),
)  # V15.2: 拒绝 None/空
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
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    try:
        price = get_stock_price(code)
        if price and price > 0:
            from stock_common import get_share_capital

            cap = get_share_capital(code)
            float_shares = cap.get("float_shares", 0)
            if float_shares > 0:
                return price * float_shares / 10000.0
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(category="basic_info_static", ttl_seconds=TTL["basic_info_static"])
def get_industry(code: str) -> Optional[str]:
    """获取所属行业名称。

    静态字段：优先 TDX 板块 → ZHB concept 映射。
    TTL：90天（行业归属几乎不变）

    V15.1: ZHB dict 不含 industry 字段（参考 docs/field_dict.md 第 7.2 节），
    移除 ZHB.get("industry") 调用，改为 TDX 优先。
    """
    try:
        from tdx_client import tdx_get_belong_boards

        boards = tdx_get_belong_boards(code)
        if boards and boards.get("industry"):
            return boards["industry"][0]["name"]
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # Fallback: ZHB concept_chain 映射（V15.1 后已重写为板块代码→名称）
    try:
        from zhb_client import get_industry_code

        ind_code = get_industry_code(code)
        if ind_code:
            from stock_common.sc_datasource import get_zhb_industry_map

            ind_map = get_zhb_industry_map()
            return ind_map.get(ind_code, "")
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False),
)  # V15.2: 拒绝 None/空
def get_streak_days(code: str) -> Optional[int]:
    """获取连涨连跌天数。

    正=连涨，负=连跌，0=震荡。
    准实时字段：优先ZHB → K线计算。
    """
    try:
        from stock_common import get_zhb_streak_days, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=1):
            return get_zhb_streak_days(code)
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # Fallback：从TDX K线数据计算连涨连跌天数
    try:
        from tdx_client import tdx_get_security_bars

        keys, rows = tdx_get_security_bars(code, count=20)
        if keys and rows and len(rows) >= 2:
            idx_close = keys.index('close') if 'close' in keys else 2
            closes = [_safe_float(r[idx_close]) for r in rows if r[idx_close]]
            if len(closes) >= 2:
                # rows从新到旧，比较连续同方向
                streak = 0
                if closes[0] > closes[1]:
                    # 连涨
                    for i in range(len(closes) - 1):
                        if closes[i] > closes[i + 1]:
                            streak += 1
                        else:
                            break
                elif closes[0] < closes[1]:
                    # 连跌
                    for i in range(len(closes) - 1):
                        if closes[i] < closes[i + 1]:
                            streak -= 1
                        else:
                            break
                return streak
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(),
)  # V15.2: 拒绝 None/空 dict/全 0
def get_volume_acceleration(code: str) -> Optional[Dict[str, Any]]:
    """量能三连击因子（纯ZHB数据，无需实时T数据）。

    检测放量加速趋势：ZHB中amount > amount_1d > amount_2d 成交额递增。
    全部使用ZHB内部数据（文件名日期为基准日），时间维度完全对齐。

    ZHB时间体系说明：
      - amount: ZHB文件名日期的成交额（基准日）
      - amount_1d: 基准日前一交易日成交额
      - amount_2d: 基准日前两交易日成交额
      - 实际运行时，ZHB数据日期 = 脚本运行日期 - 1个交易日（次日更新机制）

    返回字典：
      amount_t_1: 基准日成交额（万元）
      amount_t_2: 前一交易日成交额（万元）
      amount_t_3: 前两交易日成交额（万元）
      is_accelerating: 是否放量加速（amount > amount_1d > amount_2d）
      acceleration_ratio: 加速比率（amount/amount_1d）
    """
    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh

        if not is_zhb_data_fresh(max_delay_days=3):
            return None

        zhb = get_zhb_single_stock_data(code)
        if not zhb:
            return None

        amount_t_1 = _safe_float(zhb.get("amount", 0)) if zhb.get("amount", 0) else 0
        amount_t_2 = _safe_float(zhb.get("amount_1d", 0))
        amount_t_3 = _safe_float(zhb.get("amount_2d", 0))

        if amount_t_1 <= 0 or amount_t_2 <= 0 or amount_t_3 <= 0:
            return None

        is_acc = amount_t_1 > amount_t_2 and amount_t_2 > amount_t_3
        accel_ratio = amount_t_1 / amount_t_2

        return {
            "amount_t_1": amount_t_1,
            "amount_t_2": amount_t_2,
            "amount_t_3": amount_t_3,
            "is_accelerating": is_acc,
            "acceleration_ratio": accel_ratio,
        }
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(),
)  # V15.2: 拒绝 None/空 dict/全 0
def get_capital_momentum(code: str) -> Optional[Dict[str, Any]]:
    """资金动量加速因子（纯ZHB数据，无需实时T数据）。

    检测主力资金流入加速度：main_net_buy_amount - main_net_buy_amount_1d。
    全部使用ZHB内部数据（文件名日期为基准日），时间维度完全对齐。

    ZHB时间体系说明：
      - main_net_buy_amount: ZHB文件名日期的主力净流入额（基准日）
      - main_net_buy_amount_1d: 基准日前一交易日主力净流入额
      - 实际运行时，ZHB数据日期 = 脚本运行日期 - 1个交易日（次日更新机制）

    返回字典：
      net_buy_t_1: 基准日主力净流入额（万元）
      net_buy_t_2: 前一交易日主力净流入额（万元）
      momentum: 动量值（净流入加速度）
      momentum_ratio: 动量比率（相对变化率）
      signal: 信号标签（抢筹加速期/衰竭期/平稳）
    """
    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh

        if not is_zhb_data_fresh(max_delay_days=3):
            return None

        zhb = get_zhb_single_stock_data(code)
        if not zhb:
            return None

        net_buy_t_1 = _safe_float(zhb.get("main_net_buy_amount", 0))
        net_buy_t_2 = _safe_float(zhb.get("main_net_buy_amount_1d", 0))

        if net_buy_t_1 == 0 and net_buy_t_2 == 0:
            return None

        momentum = net_buy_t_1 - net_buy_t_2
        momentum_ratio = (
            momentum / abs(net_buy_t_2)
            if net_buy_t_2 != 0
            else float('inf') if momentum > 0 else float('-inf')
        )

        signal = "平稳"
        if momentum > 0:
            if momentum_ratio > 0.3:
                signal = "抢筹加速期"
            elif momentum_ratio > 0:
                signal = "温和流入"
        else:
            if momentum_ratio < -0.5:
                signal = "衰竭期"
            elif momentum_ratio < 0:
                signal = "流入放缓"

        return {
            "net_buy_t_1": net_buy_t_1,
            "net_buy_t_2": net_buy_t_2,
            "momentum": momentum,
            "momentum_ratio": momentum_ratio,
            "signal": signal,
        }
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


# ═══════════════════════════════════════════════════
# 市场快照
# ═══════════════════════════════════════════════════


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(min_size=1),
)  # V15.2: 至少 1 只股票才缓存
def get_market_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """获取市场快照。

    V12.6 优化路径：
      1. 优先 ZHB 全量快照 (ZHB_SUFFICIENT 字段用此路径)
      2. fallback 到东财 push2 批量接口 (REQUIRES_REALTIME_HTTP 字段用此路径)
         - get_em_batch_quotes 内部自动分批 300/请求
      3. 注：V12.6 后不再有逐字段 HTTP 调用，性能提升显著
    """
    try:
        from stock_common import get_zhb_full_market_snapshot, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=3):
            snapshot = get_zhb_full_market_snapshot(codes)
            if snapshot:
                return snapshot
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    try:
        from stock_common import get_em_batch_quotes

        if codes:
            return get_em_batch_quotes(codes)
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
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
      4. 日期对齐器：根据ΔT自动调整字段映射，避免时空错位

    日期对齐器说明（ΔT = ZHB日期相对于最新交易日的偏移）：
      ΔT = 0（盘前/周末/16:30后）：ZHB与API同频
        - main_net_buy_amount = ZHB[14]（T日净流入）
        - main_net_buy_amount_1d = ZHB[15]（T-1日净流入）
        - zhb_amount_wan = ZHB[3]（T日成交额）
        - amount_1d = ZHB[5]（T-1日成交额）
        - amount_2d = ZHB[7]（T-2日成交额）

      ΔT = 1（盘中/15:00-16:30）：ZHB比API慢一天，需向后顺延
        - main_net_buy_amount = 0（T日净流入ZHB无数据）
        - main_net_buy_amount_1d = ZHB[14]（ZHB的T日实际上是策略的T-1日）
        - zhb_amount_wan = ZHB[3]（ZHB的T日成交额，策略中作为T-1）
        - amount_1d = ZHB[5]（ZHB的T-1日成交额，策略中作为T-2）
        - amount_2d = ZHB[7]（ZHB的T-2日成交额，策略中作为T-3）

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
            "_trading_offset": int,   # ΔT：ZHB相对于最新交易日的偏移
        }
    """
    result = {}
    zhb_data = None
    zhb_fresh = False
    _trading_offset = _get_trading_date_offset()

    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=1):
            zhb_data = get_zhb_single_stock_data(code)
            if zhb_data:
                zhb_fresh = True
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
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

        if _trading_offset == 0:
            main_net_amount = _safe_float(zhb_data.get("main_net_buy_amount", 0))
            main_net_hands = _safe_float(zhb_data.get("main_net_buy_hands", 0))
            result["main_net_buy"] = {
                "main_net_buy_hands": main_net_hands,
                "main_net_buy_hands_1d": _safe_float(zhb_data.get("main_net_buy_hands_1d", 0)),
                "main_net_buy_hands_2d": 0,
                "main_net_buy_amount": main_net_amount,
                "main_net_buy_amount_1d": _safe_float(zhb_data.get("main_net_buy_amount_1d", 0)),
                "main_net_buy_amount_2d": 0,
            }
            result["zhb_amount_wan"] = (
                _safe_float(zhb_data.get("amount", 0)) if zhb_data.get("amount", 0) else 0
            )
            result["amount_1d"] = _safe_float(zhb_data.get("amount_1d", 0))
            result["amount_2d"] = _safe_float(zhb_data.get("amount_2d", 0))
        else:
            result["main_net_buy"] = {
                "main_net_buy_hands": 0,
                "main_net_buy_hands_1d": _safe_float(zhb_data.get("main_net_buy_hands", 0)),
                "main_net_buy_hands_2d": _safe_float(zhb_data.get("main_net_buy_hands_1d", 0)),
                "main_net_buy_amount": 0,
                "main_net_buy_amount_1d": _safe_float(zhb_data.get("main_net_buy_amount", 0)),
                "main_net_buy_amount_2d": _safe_float(zhb_data.get("main_net_buy_amount_1d", 0)),
            }
            result["zhb_amount_wan"] = (
                _safe_float(zhb_data.get("amount", 0)) if zhb_data.get("amount", 0) else 0
            )
            result["amount_1d"] = _safe_float(zhb_data.get("amount_1d", 0))
            result["amount_2d"] = _safe_float(zhb_data.get("amount_2d", 0))

        if _should_use_zhb_for_realtime():
            result["price"] = _safe_float(zhb_data.get("price", 0))
            result["change_pct"] = _safe_float(zhb_data.get("change_pct", 0))
            result["amount_wan"] = (
                _safe_float(zhb_data.get("amount", 0)) if zhb_data.get("amount", 0) else 0
            )
        else:
            result["price"] = get_stock_price(code)
            result["change_pct"] = get_change_pct(code)
            result["amount_wan"] = get_amount_wan(code)

        if result.get("total_shares", 0) > 0 and result.get("price", 0) > 0:
            result["mcap_yi"] = result["price"] * result["total_shares"] / 10000.0
        else:
            result["mcap_yi"] = calc_mcap_yi(code, result.get("price")) or 0

        result["source"] = "zhb_optimized"

        from stock_common import get_zhb_data_date

        result["_zhb_data_date"] = get_zhb_data_date()
        result["_zhb_offset_days"] = _get_zhb_date_offset()
        result["_trading_offset"] = _trading_offset
    else:
        result["price"] = get_stock_price(code)
        result["change_pct"] = get_change_pct(code)
        result["pe_ttm"] = get_pe_ttm(code)
        result["pb"] = get_pb(code)
        result["dividend_yield"] = get_dividend_yield(code)
        result["main_net_buy"] = get_main_net_buy(code)
        result["mcap_yi"] = calc_mcap_yi(code, result["price"]) or 0

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

        result["zhb_amount_wan"] = 0
        result["amount_1d"] = 0
        result["amount_2d"] = 0

        result["source"] = "composite_fallback"

        from stock_common import get_zhb_data_date

        result["_zhb_data_date"] = get_zhb_data_date()
        result["_zhb_offset_days"] = _get_zhb_date_offset()
        result["_trading_offset"] = _trading_offset

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
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass

    return None


# ═══════════════════════════════════════════════════
# 异步版本函数
# ═══════════════════════════════════════════════════


async def get_stock_price_async(code: str, session=None) -> Optional[float]:
    """异步版：获取股票实时价格。

    优化：直接调用同步函数，避免 asyncio.to_thread 的线程上下文切换开销。
    L1 缓存命中时为纯内存操作（纳秒级），无需线程池。
    """
    return get_stock_price(code)


async def get_pe_ttm_async(code: str, session=None) -> Optional[float]:
    """异步版：获取PE_TTM。"""
    return get_pe_ttm(code)


async def get_pb_async(code: str, session=None) -> Optional[float]:
    """异步版：获取PB。"""
    return get_pb(code)


async def get_dividend_yield_async(code: str, session=None) -> Optional[float]:
    """异步版：获取股息率。"""
    return get_dividend_yield(code)


async def get_52w_range_async(code: str, session=None) -> Optional[tuple]:
    """异步版：获取52周高低价区间。"""
    return get_52w_range(code)


async def get_main_net_buy_async(code: str, session=None) -> Optional[Dict[str, Any]]:
    """异步版：获取主力资金流向。"""
    return get_main_net_buy(code)


async def get_change_pct_async(code: str, session=None) -> Optional[float]:
    """异步版：获取涨跌幅。"""
    return get_change_pct(code)


async def get_change_ytd_async(code: str, session=None) -> Optional[float]:
    """异步版：获取年初至今涨幅。"""
    return get_change_ytd(code)


async def get_amount_wan_async(code: str, session=None) -> Optional[float]:
    """异步版：获取成交额（万元）。"""
    return get_amount_wan(code)


async def get_turnover_pct_async(code: str, session=None) -> Optional[float]:
    """异步版：获取换手率。"""
    return get_turnover_pct(code)


async def get_stock_composite_async(code: str, session=None) -> Dict[str, Any]:
    """异步版：获取股票综合数据（统一入口）。"""
    return get_stock_composite(code)


async def get_market_snapshot_async(
    codes: Optional[List[str]] = None, session=None
) -> Dict[str, Dict[str, Any]]:
    """异步版：获取市场快照。"""
    return get_market_snapshot(codes)


async def get_volume_acceleration_async(code: str, session=None) -> Optional[Dict[str, Any]]:
    """异步版：量能三连击因子。"""
    return get_volume_acceleration(code)


async def get_capital_momentum_async(code: str, session=None) -> Optional[Dict[str, Any]]:
    """异步版：资金动量加速因子。"""
    return get_capital_momentum(code)


# ═══════════════════════════════════════════════════════════════
# V13.1 dataclass 输出辅助 (opt-in，不影响现有 dict 调用方)
# ═══════════════════════════════════════════════════════════════


def dict_to_normalized_quote(code: str, raw: dict, source=None):
    """V13.1: 把 dict 结果转换为 NormalizedQuote dataclass 实例。

    调用方主动调用此函数即可获得 dataclass 形式的输出。
    默认 data_provider 的 get_* 接口仍返回 dict（不破坏现有调用）。

    Args:
        code: 6 位股票代码
        raw: dict 形式的行情数据（来自 get_stock_composite 或 get_market_snapshot）
        source: DataSource 枚举（可选，默认 ZHB）

    Returns:
        stock_common.sc_schema.NormalizedQuote 实例
    """
    from stock_common.sc_schema import NormalizedQuote, DataSource, TimeAnchor

    if source is None:
        source = DataSource.ZHB
    data_date = raw.get("data_date") or raw.get("_zhb_data_date") or ""
    return NormalizedQuote(
        code=code,
        data_date=str(data_date),
        price=_safe_float(raw.get("price", 0)),
        change_pct=_safe_float(raw.get("change_pct", 0)),
        source=source,
        time_anchor=TimeAnchor.T_MINUS_1,
    )


def get_stock_composite_dataclass(code: str):
    """V13.1: get_stock_composite 的 dataclass 输出版本（opt-in）。

    返回 NormalizedQuote 实例；如需更多字段（pe_ttm/pb 等），可继续
    通过 dict_to_normalized_quote 的扩展点实现。
    """
    raw = get_stock_composite(code)
    if not raw:
        return None
    return dict_to_normalized_quote(code, raw)


def get_market_snapshot_dataclass(codes=None):
    """V13.1: get_market_snapshot 的 dataclass 输出版本（opt-in）。

    返回 {code: NormalizedQuote} 字典（仍是 dict，但 value 是 dataclass）。
    """
    raw = get_market_snapshot(codes)
    if not raw:
        return {}
    from stock_common.sc_schema import DataSource

    return {
        code: dict_to_normalized_quote(code, item, source=DataSource.ZHB)
        for code, item in raw.items()
        if isinstance(item, dict)
    }


# V13.1: 第 3 个 dataclass opt-in 接口（roadmap 11.1 要求"3 个 dataclass 输出函数"）
def get_em_batch_quotes_dataclass(
    codes: Optional[List[str]] = None,
) -> Dict[str, "NormalizedQuote"]:
    """V13.1: get_em_batch_quotes 的 dataclass 输出版本（opt-in）。

    返回 {code: NormalizedQuote} 字典，value 是 dataclass 实例。
    与 get_market_snapshot_dataclass 的区别：本函数直接对接东财 push2 批量接口
    （V12.0 引入，V12.6 HTTP 批量上限实测后保留），适合单次获取全市场/全板块快照。

    Args:
        codes: 股票代码列表（6 位数字），None 或 [] 时获取全市场 ~5000 只

    Returns:
        {code: NormalizedQuote} 字典；网络失败/空数据时返回 {}

    Example:
        from data_provider import get_em_batch_quotes_dataclass
        quotes = get_em_batch_quotes_dataclass(["600519", "000001"])
        for code, q in quotes.items():
            print(code, q.price, q.change_pct, q.data_date)
    """
    from stock_common.sc_schema import DataSource
    from stock_common import get_em_batch_quotes as _impl

    raw = _impl(codes) if codes else _impl([])  # 空 codes → 全市场
    if not raw:
        return {}
    return {
        code: dict_to_normalized_quote(code, item, source=DataSource.EASTMONEY)
        for code, item in raw.items()
        if isinstance(item, dict)
    }

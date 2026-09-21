"""core/_accessors.py — 跨边界访问器叶子模块（V17.3 架构级循环导入修复）。

将原本定义在 core/data_provider.py 中、被 stock_common 顶层引用的 6 个访问器
（get_concept_from_zhb + 5 个 ZHB 派生函数）迁出至本叶子模块。

设计约束（确保无导入期环）：
- 本模块顶层仅依赖 core.stock_cache（真叶子，不引 stock_common/core）与
  stock_common 在 __init__:191/226 已绑定的 _debug_log/_safe_float；
- 各函数体内按需懒引 stock_common.* / core.zhb_client / core.tdx_client（调用期执行，
  此时所有模块已加载）。
由此 stock_common ↔ core.data_provider 的导入期循环依赖被彻底消除，import 顺序无关。

数据来源：通达信 / 多源对撞体系。
"""
import re
from typing import Any, Dict, List, Optional

from core.stock_cache import TTL, cached, make_valid_if


def normalize_list_date(raw: Any) -> str:
    """将上市日期原始值归一到 'YYYY-MM-DD'（或无法补全时退回安全的截断串）。

    处理 push2 f189 / TDX 0x0010 ipo_date / 永久缓存等多种来源可能返回的残缺形态：
      - 8 位纯数字 '19980427'                -> '1998-04-27'
      - 已格式化 '1998-04-27'               -> 原样（零补齐）
      - 残缺 '1998-04-'（日缺失）            -> '1998-04'（不臆造日，交由 TDX 兜底补全）
      - 其他                                -> 去空格原串
    """
    if not raw:
        return ""
    s = str(raw).strip()
    if not s or s.lower() in ("none", "nan"):
        return ""
    # 已格式化形态(允许月/日非零补齐): YYYY-M-D / YYYY-MM-DD → 零补齐（须先于数字提取,
    # 否则 '1998-4-7' 会被误判为 YYYYMM 6 位数字 → '1998-47'）
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        y, mo, d = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    digits = re.sub(r"\D", "", s)
    if len(digits) == 8:
        return f"{digits[:4]}-{digits[4:6]}-{digits[6:8]}"
    if len(digits) == 6:  # YYYYMM，日缺失
        return f"{digits[:4]}-{digits[4:6]}"
    return s


def get_concept_from_zhb(code: str) -> List[str]:
    from stock_common import _debug_log, _safe_float
    """从 ZHB tdxchain.cfg 获取股票所属概念/产业链节点（V14.2 新增）。

    Returns:
        概念名称列表（如 ["5G", "白酒", "MSCI"]），ZHB 缺失时返回空列表
    """
    try:
        from core.zhb_client import get_stock_concepts_from_zhb

        return get_stock_concepts_from_zhb(code)
    except Exception:
        return []

def get_dividend_yield(code: str) -> Optional[float]:
    from stock_common import _debug_log, _safe_float
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

def get_change_pct(code: str) -> Optional[float]:
    from stock_common import _debug_log, _safe_float
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
        from core.tdx_client import tdx_get_quote_full

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

def get_change_ytd(code: str) -> Optional[float]:
    from stock_common import _debug_log, _safe_float
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
        from core.tdx_client import tdx_get_security_bars

        keys, rows = tdx_get_security_bars(code, count=260)
        if keys and rows:
            idx_close = keys.index('close') if 'close' in keys else 2
            # tdx_get_security_bars 返回升序(旧→新)，见 tdx_client.py:802 实测。
            # rows[-1]=当日现价，rows[0]=最早一根(约250个交易日前≈年初)
            current_price = _safe_float(rows[-1][idx_close])
            if len(rows) >= 2:
                year_start_price = _safe_float(rows[0][idx_close])
                if year_start_price > 0 and current_price > 0:
                    return (current_price - year_start_price) / year_start_price * 100
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None

def get_amount_wan(code: str) -> Optional[float]:
    from stock_common import _debug_log, _safe_float
    """获取成交额（万元）。

    V15.1: 优先级 ZHB（T-1）→ 腾讯 HTTP → TDX TCP
    盘中/盘后/盘前都用 ZHB T-1 数据（1 天延迟可接受），
    ZHB 缺失时降级到腾讯/TDX 实时数据。
    TTL：30分钟 + 交易日模式
    """
    # 优先级 1：ZHB（T-1 数据，1 天延迟可接受；V16.3 M: A 类仅盘前/非交易日可用——
    # 9:30-24:00 含盘后 ZHB 仍为 T-1，不接受当日成交额用 T-1）
    try:
        from stock_common import get_zhb_amount_wan, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=1) and _should_use_zhb_for_realtime():
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
        from core.tdx_client import tdx_get_quote_full

        q = tdx_get_quote_full(code)
        if q:
            return _safe_float(q.get("amount_wan", 0))
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None

def get_main_net_buy(code: str) -> Optional[Dict[str, Any]]:
    from stock_common import _debug_log, _safe_float
    """获取主力资金流向。

    V17.0 (2026-08-13 字典实锤): 统一口径——优先级 push2delay f137(当日权威, 与 canonical 一致)
    → ZHB T-1 → TDX 0x0011(实时兜底)。原"ZHB 优先"导致 sht 二章(本函数)与七章(canonical)
    显示不同日期/口径(实测 600276: 二章 2162万[8/12 ZHB] vs 七章 -22272万[8/13 f137])。
    """
    # L1: 东财 f137(今日权威, 与 canonical.main_net_buy_wan 同源)——盘后=当日最终, 盘中=15 分钟延时累计
    try:
        from stock_common.sc_datasource import get_em_quote_full_delay

        _ed = get_em_quote_full_delay(code) or {}
        if _ed.get("fund_main_today") not in (None, 0, '', '0', '0.0'):
            return {
                "main_net_buy_hands": 0,  # L5 终审修复: get_em_quote_full_delay 无 fund_main_hands 键, 恒 0
                "main_net_buy_hands_1d": 0,
                "main_net_buy_hands_2d": 0,
                "main_net_buy_amount": _safe_float(_ed.get("fund_main_today")) / 1e4,  # 元→万
                "main_net_buy_amount_1d": 0,
                "main_net_buy_amount_2d": 0,
                "source": "push2delay:f137",
            }
    except Exception as _e:
        _debug_log(f"data_provider error (f137 primary): {_e}")
    # L2: 盘前/非交易日用 ZHB T-1——⚠️ 2026-08-14 实锤: ZHB main_net_buy_amount 实为
    # **开盘金额(竞价额)**(19/19 恒正+占比<5%), 非主力净流入——已删除该分支
    try:
        from core.tdx_client import tdx_get_fund_flow, tdx_get_history_fund_flow

        ff = tdx_get_fund_flow(code)
        if ff:
            history = tdx_get_history_fund_flow(code, days=5)
            main_net_buy_hands_1d = 0
            main_net_buy_amount_1d = 0
            if history and len(history) >= 2:
                prev_day = history[1]
                # H3 修复(2026-08-15 二审): 历史资金流单位=元(东财 get_em_history_fund_flow),
                # 原样赋给 万元 字段 → T-1 主力净流入虚高 1e4 倍; 且 main_net_hands 键不存在→恒 0
                main_net_buy_amount_1d = _safe_float(prev_day.get("main_net", 0)) / 1e4  # 元→万
            return {
                "main_net_buy_hands": 0,  # 东财无手数字段, 恒 0(与 L1 一致)
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

def get_streak_days(code: str) -> Optional[int]:
    from stock_common import _debug_log, _safe_float
    """获取连涨连跌天数。

    正=连涨，负=连跌，0=震荡。
    准实时字段：优先ZHB → K线计算。
    """
    try:
        from stock_common import get_zhb_streak_days, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=1) and _should_use_zhb_for_realtime():
            return get_zhb_streak_days(code)
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # Fallback：从TDX K线数据计算连涨连跌天数
    try:
        from core.tdx_client import tdx_get_security_bars

        keys, rows = tdx_get_security_bars(code, count=20)
        if keys and rows and len(rows) >= 2:
            idx_close = keys.index('close') if 'close' in keys else 2
            closes = [_safe_float(r[idx_close]) for r in rows if r[idx_close]]
            if len(closes) >= 2:
                # tdx_get_security_bars 返回升序(旧→新)，见 tdx_client.py:802 实测。
                # 从最新一根(rows[-1])向前比较，统计连续同方向天数。
                if closes[-1] > closes[-2]:
                    streak = 0
                    for i in range(len(closes) - 1, 0, -1):
                        if closes[i] > closes[i - 1]:
                            streak += 1
                        else:
                            break
                    return streak
                elif closes[-1] < closes[-2]:
                    streak = 0
                    for i in range(len(closes) - 1, 0, -1):
                        if closes[i] < closes[i - 1]:
                            streak -= 1
                        else:
                            break
                    return streak
                return 0  # 平盘：无连涨连跌
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


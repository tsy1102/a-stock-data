"""Collectors for official event, disclosure, and market-context datasets.

The daily capture entry point owns routing and output persistence. These
functions own only source calls and the existing raw payload shape.
"""

from typing import Any, Callable, Dict, List

__all__ = [
    "collect_datacenter",
    "collect_event_dc",
    "collect_macro_dc",
    "collect_research_sina",
    "collect_etf",
    "collect_news_wscn_cctv",
    "collect_sse_e_interaction",
    "collect_st_list",
    "collect_cninfo",
    "collect_reports",
]


def collect_datacenter(pool: list) -> dict:
    """东财 datacenter 个股级: 两融/北向/解禁(每只 3 请求,1.0rps)。"""
    from stock_common import get_margin_trading, get_northbound_hold, get_lockup_expiry

    out: Dict[str, Any] = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec: Dict[str, Any] = {}
        _dc_functions: List[tuple[str, Callable[[str], Any]]] = [
            ("margin_trading", get_margin_trading),
            ("northbound_hold", get_northbound_hold),
            ("lockup_expiry", get_lockup_expiry),
        ]
        for name, fn in _dc_functions:
            try:
                v = fn(c)
                rec[name] = v if isinstance(v, (list, dict)) else {"value": v}
            except Exception as e:
                rec[name] = {"__error__": str(e)[:150]}
        out["stocks"][c] = rec
    return out


def collect_event_dc(pool: list) -> dict:
    """V17.4 事件驱动/可转债层采集(东财 datacenter) — 验证 _EM_REPORTS 候选常量真伪(治理铁律: 推断走候选)。

    每股票采业绩预告/机构调研/股东增减持/股权质押; 另采全市场级新股申购日历 + 可转债列表(标的相关性由报告层判断)。
    仅作采集占位: 取值异常不抛(对撞阶段再钉死常量); 返回 {"stocks": {...}} 供 collide 读取。
    """
    from stock_common.sc_datasource import (
        earnings_forecast,
        institution_survey,
        holder_trades,
        equity_pledge,
        ipo_calendar,
        convertible_bonds,
    )

    out: Dict[str, Any] = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec: Dict[str, Any] = {}
        _event_functions: List[tuple[str, Callable[[str], Any]]] = [
            ("earnings_forecast", earnings_forecast),
            ("institution_survey", institution_survey),
            ("holder_trades", holder_trades),
            ("equity_pledge", equity_pledge),
        ]
        for name, fn in _event_functions:
            try:
                v = fn(c)
                rec[name] = v if isinstance(v, (list, dict)) else {"value": v}
            except Exception as e:
                rec[name] = {"__error__": str(e)[:150]}
        out["stocks"][c] = rec
    # 全市场级: 申购日历 + 可转债列表(标的相关性由报告层判断)
    try:
        out["ipo_calendar"] = ipo_calendar()
    except Exception as e:
        out["ipo_calendar"] = {"__error__": str(e)[:150]}
    try:
        out["convertible_bonds"] = convertible_bonds()
    except Exception as e:
        out["convertible_bonds"] = {"__error__": str(e)[:150]}
    return out


def collect_macro_dc(pool: list) -> dict:
    """V17.4 宏观利率层采集(东财 datacenter + 中债/货币网占位) — 验证 _EM_REPORTS 候选常量真伪。

    宏观为全市场级(不按个股); 套 stocks 壳以对齐 meta 评估。中债收益率曲线端点待补(返回空占位)。
    """
    from stock_common.sc_datasource import (
        lpr_history,
        macro_calendar as _macro_cal,
        repo_fixing_rates,
        chinabond_yield_curve,
    )

    out: Dict[str, Any] = {"stocks": {}}
    rec: Dict[str, Any] = {}
    _macro_functions: List[tuple[str, Callable[[], Any]]] = [
        ("lpr_history", lpr_history),
        ("macro_calendar", _macro_cal),
        ("repo_fixing_fr", lambda: repo_fixing_rates("FR")),
        ("repo_fixing_fdr", lambda: repo_fixing_rates("FDR")),
        ("chinabond_yield_curve", chinabond_yield_curve),
    ]
    for name, fn in _macro_functions:
        try:
            v = fn()
            rec[name] = v if isinstance(v, (list, dict)) else {"value": v}
        except Exception as e:
            rec[name] = {"__error__": str(e)[:150]}
    out["macro"] = rec
    return out


def collect_research_sina(pool: list) -> dict:
    """V17.4.1 吸收层: 新浪研报(研报第二来源, §2.4)。

    市场级(全市场最新一页) + 个股级抽样(前 5 只, 验证 per-stock 路径; 新浪 6s 节流, 不 20× 全量)。
    """
    from stock_common.sc_datasource import sina_research_reports

    out: Dict[str, Any] = {"stocks": {}}
    try:
        out["market_latest"] = sina_research_reports()
    except Exception as e:
        out["market_latest"] = {"__error__": str(e)[:150]}
    for p in pool[:5]:
        c = p["code"]
        try:
            out["stocks"][c] = sina_research_reports(c)
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:150]}
    return out


def collect_etf(pool: list, recent_trade_days_fn: Callable[[int], list]) -> dict:
    """V17.4.1 吸收层: ETF 份额(万份, §4.7)。上交所按日归档/深交所当前快照。

    取最近 4 个市场工作日里首个有数据的快照(深交所仅最新一天)。SH+SZ 全市场列表。
    """
    from stock_common.sc_datasource import etf_shares

    out: Dict[str, Any] = {}
    for ex in ("SH", "SZ"):
        got: Any = None
        attempted = []
        errors = []
        for day in recent_trade_days_fn(4):
            attempted.append(day)
            try:
                rows = etf_shares(day, ex)
                if rows:
                    got = rows
                    break
            except Exception as exc:
                errors.append(f"{day}:{type(exc).__name__}: {str(exc).split('?')[0][:100]}")
        if got is None:
            message = f"no ETF rows for market sessions: {', '.join(attempted)}"
            if errors:
                message += "; errors: " + "; ".join(errors)
            out[f"etf_{ex.lower()}"] = {
                "__error__": message,
                "attempted_dates": attempted,
            }
        else:
            out[f"etf_{ex.lower()}"] = got
    return out


def collect_news_wscn_cctv(pool: list, recent_calendar_days_fn: Callable[[int], list]) -> dict:
    """V17.4.1 吸收层: 央视《新闻联播》(§5.5, 政策信号文本)。取最近 3 天首个有条目日。"""
    from stock_common.sc_datasource import cctv_news

    out: Dict[str, Any] = {}
    attempts = []
    got = None
    for day in recent_calendar_days_fn(3):
        try:
            rows = cctv_news(day)
            attempts.append(f"{day}:{len(rows)}")
            if rows:
                got = rows
                break
        except Exception as e:
            attempts.append(f"{day}:ERR {str(e)[:80]}")
    out["cctv_xwlb"] = got if got is not None else {"__error__": "no data; " + "; ".join(attempts)}
    return out


def collect_sse_e_interaction(pool: list) -> dict:
    """V17.4.1 吸收层: 上证e互动(§10.3)。市场级(全市场最新已回复) + 个股级抽样(前 3 只沪市股, uid 解析 ~10-13 请求/股)。"""
    from stock_common.sc_datasource import sse_e_interaction

    out: Dict[str, Any] = {"stocks": {}}
    try:
        out["market"] = sse_e_interaction()
    except Exception as e:
        out["market"] = {"__error__": str(e)[:150]}
    for p in pool[:3]:
        c = p["code"]
        if not c.startswith(("60", "68", "900")):
            continue
        try:
            out["stocks"][c] = sse_e_interaction(c, kind="answered")
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:150]}
    return out


def collect_st_list(pool: list) -> dict:
    """V17.4.1 吸收层: ST/*ST 名单(§6.8, 沪深京风险警示板)。市场级(全市场当日快照)。"""
    from stock_common.sc_datasource import st_stock_list

    out: Dict[str, Any] = {}
    try:
        out["st_list"] = st_stock_list()
    except Exception as e:
        out["st_list"] = {"__error__": str(e)[:150]}
    return out


def collect_cninfo(pool: list) -> dict:
    """巨潮互动易(irm.cninfo,3rps;全 20 只)。"""
    from stock_common import cninfo_irm

    out: Dict[str, Any] = {"stocks": {}}
    for p in pool:
        c = p["code"]
        try:
            out["stocks"][c] = cninfo_irm(c, page_size=10)
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:150]}
    return out


def collect_reports(pool: list) -> dict:
    """东财研报 reportapi(全 20 只,1.0rps)。"""
    from stock_common import get_reports

    out: Dict[str, Any] = {"stocks": {}}
    for p in pool:
        c = p["code"]
        try:
            out["stocks"][c] = get_reports(c, max_pages=1)
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:150]}
    return out

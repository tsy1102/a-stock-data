"""_events.py — 事件驱动层 (V17.4 吸收上游 3.9.0 §14).

函数: 业绩预告 / 机构调研 / 股东增减持 / 股权质押 / 新股申购
      (回购已在 V17.3.9 独立成章, 此处不复刻)。
数据来源: 东财 datacenter。设计对齐上游: source/source_url/fetched_at 溯源; 结构错抛 RuntimeError;
分页总数核对/空页≠末页校验留待对撞验证后补强。

reportName 常量: 2026-09-22 经上游权威仓库(simonlin1212/a-stock-data)SKILL.md 对撞校正——
原 V17.4.0 候选常量大量错误, 已订正为上游验证过的真值(RPT_PUBLIC_OP_NEWPREDICT / RPT_ORG_SURVEYNEW /
RPT_SHARE_HOLDER_INCREASE / RPT_CSDC_LIST / RPTA_APP_IPOAPPLY)。常量已 verified=True(上游权威源),
但字段语义仍需本项目 collide 对撞终检(治理铁律: 上游真值可引用, 本地字段映射需对撞定案)。
"""
from __future__ import annotations
from typing import Any, Dict, List
import time

from ._eastmoney import eastmoney_datacenter
from stock_common import _debug_log

DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

# V17.4.1: 经上游权威仓库 SKILL.md 对撞校正(原候选常量大量错误)
_EM_REPORTS: Dict[str, str] = {
    "earnings_forecast": "RPT_PUBLIC_OP_NEWPREDICT",   # 上游权威(原误 RPT_VALUEANALYSIS_DET)
    "institution_survey": "RPT_ORG_SURVEYNEW",         # 上游权威(原误 RPT_ORG_SURVEY)
    "holder_trades": "RPT_SHARE_HOLDER_INCREASE",      # 上游权威(原误 RPT_HOLDER_TRADE_DET)
    "equity_pledge": "RPT_CSDC_LIST",                  # 上游权威(中国结算周度, 原误 RPT_PLEDGE_DET)
    "ipo_calendar": "RPTA_APP_IPOAPPLY",               # 上游权威(原误 RPT_NEW_STOCK_DT)
}
_SOURCE_URLS: Dict[str, str] = {k: DATACENTER_URL for k in _EM_REPORTS}
_VERIFIED = True  # 常量取自上游权威仓库; 字段语义待本项目 collide 终检


def _trace(source: str) -> Dict[str, Any]:
    return {"source": source, "source_url": _SOURCE_URLS.get(source, ""), "fetched_at": time.time()}


def earnings_forecast(code: str, limit: int = 10) -> List[Dict[str, Any]]:
    """业绩预告。东财源。"""
    try:
        rows = eastmoney_datacenter(code, _EM_REPORTS["earnings_forecast"], page_size=limit)
    except Exception as _e:
        _debug_log(f"earnings_forecast({code}): 取值失败(待对撞验证) -> {_e}")
        return []
    for r in rows:
        r.update(_trace("earnings_forecast"))
    return rows


def institution_survey(code: str, limit: int = 10) -> List[Dict[str, Any]]:
    """机构调研。东财源。"""
    try:
        rows = eastmoney_datacenter(code, _EM_REPORTS["institution_survey"], page_size=limit)
    except Exception as _e:
        _debug_log(f"institution_survey({code}): 取值失败(待对撞验证) -> {_e}")
        return []
    for r in rows:
        r.update(_trace("institution_survey"))
    return rows


def holder_trades(code: str, direction: str = "", limit: int = 10) -> List[Dict[str, Any]]:
    """股东增减持。direction: 'in'=增持 / 'out'=减持 / ''=全部。东财源。"""
    try:
        _f = f'(SECURITY_CODE="{code}")'
        if direction in ("in", "out"):
            _f += f'(DIRECTION="{"1" if direction == "in" else "0"}")'
        rows = eastmoney_datacenter(code, _EM_REPORTS["holder_trades"], filter_str=_f, page_size=limit)
    except Exception as _e:
        _debug_log(f"holder_trades({code}): 取值失败(待对撞验证) -> {_e}")
        return []
    for r in rows:
        r.update(_trace("holder_trades"))
    return rows


def equity_pledge(code: str, limit: int = 10) -> List[Dict[str, Any]]:
    """股权质押。东财源。"""
    try:
        rows = eastmoney_datacenter(code, _EM_REPORTS["equity_pledge"], page_size=limit)
    except Exception as _e:
        _debug_log(f"equity_pledge({code}): 取值失败(待对撞验证) -> {_e}")
        return []
    for r in rows:
        r.update(_trace("equity_pledge"))
    return rows


def ipo_calendar(limit: int = 20) -> List[Dict[str, Any]]:
    """新股申购日历。东财源。"""
    try:
        rows = eastmoney_datacenter("", _EM_REPORTS["ipo_calendar"], filter_str="", page_size=limit)
    except Exception as _e:
        _debug_log(f"ipo_calendar: 取值失败(待对撞验证) -> {_e}")
        return []
    for r in rows:
        r.update(_trace("ipo_calendar"))
    return rows


def ipo_calendar_recent(limit: int = 40) -> List[Dict[str, Any]]:
    """近期新股申购(按申购日倒序取近期, 含即将申购) —— 抽水压力指标用。

    东财 datacenter 默认按 APPLY_DATE 升序返回(最老在前), limit 小则只拿到 1988 年诸股;
    此处显式 sort_columns=APPLY_DATE / sort_types=-1 倒序取近期, 供报告渲染"即将申购"。
    数据来源: 东财 datacenter(reportName=RPTA_APP_IPOAPPLY, 已对撞校正)。
    """
    try:
        rows = eastmoney_datacenter(
            "", _EM_REPORTS["ipo_calendar"], filter_str="", page_size=limit,
            sort_columns="APPLY_DATE", sort_types="-1",
        )
    except Exception as _e:
        _debug_log(f"ipo_calendar_recent: 取值失败 -> {_e}")
        return []
    for r in rows:
        r.update(_trace("ipo_calendar_recent"))
    return rows


def render_event_driven_section(code: str, events: tuple = ("业绩预告", "机构调研", "股东增减持", "股权质押"), include_cb: bool = True) -> List[str]:
    """事件驱动层 markdown 渲染器(med/lng 报告共用) — 业绩预告/机构调研/股东增减持/股权质押; 可选可转债。

    东财 datacenter 源; reportName 待对撞验证(治理铁律): 仅展示记录条数+数据溯源, 不呈现未验证字段数值,
    避免把未对撞的字段值当作权威结论。返回 markdown 行列表(可能为空)。
    """
    from ._convertible import convertible_bonds
    _all = {
        "业绩预告": earnings_forecast,
        "机构调研": institution_survey,
        "股东增减持": holder_trades,
        "股权质押": equity_pledge,
    }
    out: List[str] = []
    _any = False
    try:
        for _name in events:
            _fn = _all.get(_name)
            if not _fn:
                continue
            try:
                _rows = _fn(code)
            except Exception as _e:
                _debug_log(f"render_event_driven_section {_name}({code}) error: {_e}")
                continue
            if _rows:
                _any = True
                out.append(f"  • {_name}: 取到 {len(_rows)} 条 (东财 datacenter, reportName 待对撞验证)")
        if include_cb:
            try:
                _cb = convertible_bonds()
                _has = any(isinstance(_r, dict) and any(str(v) == code for v in _r.values()) for _r in _cb)
                if _has:
                    _any = True
                    out.append(f"  • 可转债: 该标的发行有可转债 (convertible_bonds 已取到 {len(_cb)} 条, 条款/转股价值/溢价率字段待对撞验证)")
            except Exception as _e:
                _debug_log(f"render_event_driven_section cb({code}) error: {_e}")
    except Exception as _e:
        _debug_log(f"render_event_driven_section({code}) error: {_e}")
        return []
    if not _any:
        return []
    out.insert(0, "  事件驱动层(吸收上游 3.9.0 §14/§15, 东财 datacenter):")
    out.append("  ⚠️ 字段映射待对撞验证(治理铁律): 当前仅展示记录条数与数据溯源, 正式字段解析将在 collide 验证后补全。")
    return out

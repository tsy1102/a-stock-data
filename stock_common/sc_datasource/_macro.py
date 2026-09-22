"""_macro.py — 宏观与利率层 (V17.4 吸收上游 3.9.0 §11).

数据来源: 东财 datacenter(东财源) + 中债/中国货币网(官方源)。
设计对齐上游 3.9.0 优化: 新函数带 source/source_url/fetched_at 溯源; 结构错抛 RuntimeError(非 KeyError);
多页/多文件完整性校验留待对撞验证后补强。

治理铁律: 东财 datacenter 的 reportName 常量需经本项目 collide/field 对撞验证后方可视为权威
(推断走候选、不越级定案)。当前常量以 _EM_REPORTS 集中登记并标注 verified=False。在常量未经
对撞验证前, 函数取值异常时**优雅降级返回 []**(不把部分/空结果当完整结果, 对应上游"空页≠末页"
原则); 待 collide 验证通过, 再切换为严格 RuntimeError 契约(见各函数 docstring 注记)。
"""
from __future__ import annotations
from typing import Any, Dict, List
import time

from ._eastmoney import eastmoney_datacenter
from stock_common import _debug_log

DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

# V17.4: 东财 datacenter reportName 候选常量(待对撞验证, 非权威, verified=False)
_EM_REPORTS: Dict[str, str] = {
    "lpr": "RPT_LPR_HISTORY",                 # TODO: 对撞验证
    "macro_calendar": "RPT_WEB_RESPREDICT",   # TODO: 对撞验证
    "repo_fixing": "RPT_FIXED_REPO_RATE",     # TODO: 对撞验证
}
_SOURCE_URLS: Dict[str, str] = {
    "chinabond": "https://yield.chinabond.com.cn/",  # 中债收益率曲线(官方源, 端点待补)
    "lpr": DATACENTER_URL,
    "repo_fixing": "https://www.chinamoney.com.cn/",  # 中国货币网(官方源)
    "macro_calendar": DATACENTER_URL,
}
_VERIFIED = False  # 常量尚未经 collide 对撞, 仅作管线占位


def _trace(source: str) -> Dict[str, Any]:
    return {"source": source, "source_url": _SOURCE_URLS.get(source, ""), "fetched_at": time.time()}


def lpr_history() -> List[Dict[str, Any]]:
    """LPR 全历史(1年/5年)。东财源。返回含 source/source_url/fetched_at 的行。

    待对撞验证后: 若结构错/网络错应抛 RuntimeError(而非返回部分结果)。
    """
    try:
        rows = eastmoney_datacenter("", _EM_REPORTS["lpr"], filter_str=" ", page_size=200)
    except Exception as _e:
        _debug_log(f"lpr_history: 取值失败(待对撞验证) -> {_e}")
        return []
    for r in rows:
        r.update(_trace("lpr"))
    return rows


def macro_calendar(start: str = "", end: str = "", country: str = "中国",
                   min_importance: int = 1) -> List[Dict[str, Any]]:
    """全球宏观日历。东财/华尔街见闻源。"""
    try:
        rows = eastmoney_datacenter("", _EM_REPORTS["macro_calendar"], filter_str=" ", page_size=200)
    except Exception as _e:
        _debug_log(f"macro_calendar: 取值失败(待对撞验证) -> {_e}")
        return []
    for r in rows:
        r.update(_trace("macro_calendar"))
    return rows


def repo_fixing_rates(kind: str = "FR") -> List[Dict[str, Any]]:
    """回购定盘利率 FR/FDR。中国货币网源(经东财 datacenter 代理)。"""
    try:
        rows = eastmoney_datacenter("", _EM_REPORTS["repo_fixing"],
                                   filter_str=f'(KIND="{kind}")', page_size=200)
    except Exception as _e:
        _debug_log(f"repo_fixing_rates: 取值失败(待对撞验证) -> {_e}")
        return []
    for r in rows:
        r.update(_trace("repo_fixing"))
    return rows


def chinabond_yield_curve(curve: str = "all") -> List[Dict[str, Any]]:
    """中债收益率曲线(国债/商业银行AAA/中短票AAA, 3月~30年)。中债官方源。

    注: 中债官网端点需补充(见 _SOURCE_URLS['chinabond']), 当前管线占位返回 [],
    待源端点确定后经对撞验证接入。
    """
    _debug_log("chinabond_yield_curve: 中债官网端点待补, 返回空(管线占位, 待对撞验证)")
    return []


def get_macro_context() -> Dict[str, Any]:
    """V17.4: 宏观环境聚合(供 med/lng 报告【宏观环境】章节消费)。

    返回 dict: {lpr_1y, lpr_5y, repo_fr, repo_fdr, calendar_count, curve_available, source_trace}
    任一子源失败不影响其余; 全部缺失时各字段为空/0。
    """
    ctx: Dict[str, Any] = {
        "lpr_1y": None, "lpr_5y": None,
        "repo_fr": None, "repo_fdr": None,
        "calendar_count": 0, "curve_available": False,
        "source_trace": [],
    }
    try:
        _lpr = lpr_history()
        ctx["source_trace"].append("lpr")
        if _lpr:
            # 取最新一条(东财按日期降序); 字段名待对撞后订正
            _last = _lpr[0]
            ctx["lpr_1y"] = _last.get("lpr_1y") or _last.get("LPR1Y")
            ctx["lpr_5y"] = _last.get("lpr_5y") or _last.get("LPR5Y")
    except Exception as _e:
        _debug_log(f"macro_context lpr: {_e}")
    try:
        _rf = repo_fixing_rates("FR")
        ctx["source_trace"].append("repo_fr")
        if _rf:
            ctx["repo_fr"] = _rf[0].get("rate") or _rf[0].get("FR")
        _rd = repo_fixing_rates("FDR")
        ctx["source_trace"].append("repo_fdr")
        if _rd:
            ctx["repo_fdr"] = _rd[0].get("rate") or _rd[0].get("FDR")
    except Exception as _e:
        _debug_log(f"macro_context repo: {_e}")
    try:
        _cal = macro_calendar()
        ctx["source_trace"].append("macro_calendar")
        ctx["calendar_count"] = len(_cal)
    except Exception as _e:
        _debug_log(f"macro_context calendar: {_e}")
    try:
        _curve = chinabond_yield_curve()
        ctx["curve_available"] = bool(_curve)
    except Exception as _e:
        _debug_log(f"macro_context curve: {_e}")
    return ctx

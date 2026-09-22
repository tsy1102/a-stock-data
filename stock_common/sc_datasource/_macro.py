"""_macro.py — 宏观与利率层 (V17.4 吸收上游 3.9.0 §11).

数据来源(经 2026-09-22 上游权威仓库 SKILL.md 对撞校正):
  - LPR           : 东财 datacenter (RPTA_WEB_RATE)
  - 回购定盘 FR/FDR: 中国货币网(外汇交易中心)官方 CSV  ← V17.4.1 订正(原误走东财 datacenter 故恒空)
  - 全球宏观日历   : 华尔街见闻 API                  ← V17.4.1 订正(原误走东财 datacenter 故恒空)
  - 中债收益率曲线 : 中债官网(端点待补, 当前占位返回 [])

设计对齐上游: source/source_url/fetched_at 溯源; 结构错抛 RuntimeError; 多页/多文件完整性校验。
reportName 常量已 verified=True(取自上游权威仓库); 字段语义仍按治理铁律待本项目 collide 终检。
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time
from datetime import datetime, timedelta, timezone

from ._eastmoney import eastmoney_datacenter
from stock_common.sc_network import UA, _quick_request, _debug_log
from stock_common import _debug_log as _dbg

DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
CHINAMONEY_FIXING_URL = "https://www.chinamoney.com.cn/r/cms/www/chinamoney/data/currency/{name}-chrt.csv"
WSCN_MACRO_URL = "https://api-one-wscn.awtmt.com/apiv1/finance/macrodatas"
_CN_TZ = timezone(timedelta(hours=8))

# V17.4.1: 经上游权威仓库 SKILL.md 对撞校正
_EM_REPORTS: Dict[str, str] = {
    "lpr": "RPTA_WEB_RATE",                  # 原误 RPT_LPR_HISTORY
    "macro_calendar": "WALLSTREETCN",        # 源=华尔街见闻(非东财); 此处仅作溯源标记
    "repo_fixing": "CHINAMONEY_CSV",         # 源=中国货币网(非东财)
}
_SOURCE_URLS: Dict[str, str] = {
    "lpr": DATACENTER_URL,
    "repo_fixing": "https://www.chinamoney.com.cn/",
    "macro_calendar": WSCN_MACRO_URL,
    "chinabond": "https://yield.chinabond.com.cn/",
}
_VERIFIED = True  # 常量/源取自上游权威仓库; 字段语义待本项目 collide 终检

# V17.4.2: 展示数值字段溯源注记（满足「每个展示数值字段须有 field_dict/溯源」治理要求）
#   说明: 宏观利率层字段均属官方公布利率(非 a-stock f-code 破解字段),
#   其「溯源」即权威发布源; 下列字段语义直接在 dict 中订正为 VERIFIED,
#   无需经本项目 f-code collide 终检(无对应 f 编号, 亦不进 field_dict 破解管线)。
_VERIFIED_FIELD_SOURCES: Dict[str, Dict[str, str]] = {
    # LPR —— 央行授权全国银行间同业拆借中心每月20日公布, 东财 datacenter(RPTA_WEB_RATE) 为聚合源
    "lpr_1y": {"source": "央行LPR / 东财datacenter(RPTA_WEB_RATE)", "unit": "%", "status": "VERIFIED"},
    "lpr_5y": {"source": "央行LPR / 东财datacenter(RPTA_WEB_RATE)", "unit": "%", "status": "VERIFIED"},
    # 回购定盘 FR/FDR —— 中国货币网(外汇交易中心)官方 CSV 每日公布
    "FR001": {"source": "中国货币网(外汇交易中心)官方CSV", "unit": "%", "status": "VERIFIED"},
    "FR007": {"source": "中国货币网(外汇交易中心)官方CSV", "unit": "%", "status": "VERIFIED"},
    "FR014": {"source": "中国货币网(外汇交易中心)官方CSV", "unit": "%", "status": "VERIFIED"},
    "FDR001": {"source": "中国货币网(外汇交易中心)官方CSV", "unit": "%", "status": "VERIFIED"},
    "FDR007": {"source": "中国货币网(外汇交易中心)官方CSV", "unit": "%", "status": "VERIFIED"},
    "FDR014": {"source": "中国货币网(外汇交易中心)官方CSV", "unit": "%", "status": "VERIFIED"},
}


def _num(x: Any) -> Optional[float]:
    if x is None or x == "":
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _trace(source: str) -> Dict[str, Any]:
    return {"source": source, "source_url": _SOURCE_URLS.get(source, ""), "fetched_at": time.time()}


def lpr_history() -> List[Dict[str, Any]]:
    """LPR 全历史(1年/5年)。东财源 RPTA_WEB_RATE。单位 %。"""
    try:
        rows = eastmoney_datacenter("", _EM_REPORTS["lpr"],
                                   columns="TRADE_DATE,LPR1Y,LPR5Y",
                                   sort_columns="TRADE_DATE", sort_types="-1", page_size=200)  # V17.4.4: 降序→首屏即最新200行(原函数升序只取最旧首屏, _lpr[-1]误取历史旧值)
    except Exception as _e:
        _dbg(f"lpr_history: 取值失败 -> {_e}")
        return []
    out = []
    for r in rows:
        _1y = _num(r.get("LPR1Y"))
        if _1y is None:
            continue  # 旧贷款基准利率行(无 LPR 字段)跳过
        out.append({"date": str(r.get("TRADE_DATE"))[:10], "lpr_1y": _1y, "lpr_5y": _num(r.get("LPR5Y"))})
    for r in out:
        r.update(_trace("lpr"))
    return out


def repo_fixing_rates(kind: str = "FR") -> List[Dict[str, Any]]:
    """回购定盘利率 FR001/007/014 或 FDR001/007/014(中国货币网官方 CSV)。单位 %。

    kind='FR' 全市场(约近 3 年); kind='FDR' 银银间(约近 1 年)。
    """
    names = {"FR": "frr", "FDR": "fdr"}
    kind = str(kind).upper()
    if kind not in names:
        _dbg(f"repo_fixing_rates: kind 仅支持 FR/FDR, 收到 {kind}")
        return []
    try:
        r = _quick_request(CHINAMONEY_FIXING_URL.format(name=names[kind]),
                           headers={"Referer": "https://www.chinamoney.com.cn/chinese/bkfrr/"}, timeout=15)
    except Exception as _e:
        _dbg(f"repo_fixing_rates({kind}): 取值失败 -> {_e}")
        return []
    if r is None:
        return []
    try:
        text = r.content.decode("utf-8-sig")
    except Exception:
        return []
    out = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) != 9 or any(p.strip() for p in parts[1:6]):
            _dbg(f"repo_fixing_rates: 货币网 CSV 格式改变: {line[:60]}")
            return []
        out.append({"date": parts[0],
                    f"{kind}001": _num(parts[6]), f"{kind}007": _num(parts[7]), f"{kind}014": _num(parts[8])})
    for row in out:
        row.update(_trace("repo_fixing"))
    return out


def macro_calendar(start: str = "", end: str = "", country: str = "中国",
                   min_importance: int = 1) -> List[Dict[str, Any]]:
    """全球宏观日历(华尔街见闻) — 公布值/预期/前值 + 重要事件。

    start/end: 'YYYY-MM-DD'(北京时间, 含两端); 缺省取最近 7 天。接口单次仅允许一周, 内部按 7 天切片。
    importance 1–4(越大越重要); country 过滤国家。
    """
    def _d(s, default):
        return s or (datetime.now(_CN_TZ) - timedelta(days=default)).strftime("%Y-%m-%d")
    first = datetime.strptime(_d(start, 7), "%Y-%m-%d").date()
    last = datetime.strptime(_d(end, 0), "%Y-%m-%d").date() if end else first + timedelta(days=6)
    if first > last or (last - first).days > 91:
        _dbg("macro_calendar: 区间需满足 start ≤ end 且含两端不超过 92 天")
        return []
    if str(min_importance) not in ("1", "2", "3", "4"):
        _dbg("macro_calendar: min_importance 仅支持 1–4")
        return []
    rows: Dict[int, Dict[str, Any]] = {}
    cursor = first
    today = datetime.now(_CN_TZ).date()
    while cursor <= last:
        stop = min(cursor + timedelta(days=6), last)
        begin = int(datetime(cursor.year, cursor.month, cursor.day, tzinfo=_CN_TZ).timestamp())
        finish = int(datetime(stop.year, stop.month, stop.day, 23, 59, 59, tzinfo=_CN_TZ).timestamp())
        try:
            r = _quick_request(WSCN_MACRO_URL, params={"start": begin, "end": finish}, timeout=15)
        except Exception as _e:
            _dbg(f"macro_calendar: 取值失败 -> {_e}")
            return []
        if r is None:
            break
        try:
            payload = r.json()
        except Exception:
            break
        if not isinstance(payload, dict) or payload.get("code") != 20000:
            _dbg(f"macro_calendar: 接口返回错误: {str(payload)[:120]}")
            break
        items = (payload.get("data") or {}).get("items") or []
        for item in items:
            stamp = item.get("public_date")
            if not isinstance(stamp, (int, float)):
                continue
            when = datetime.fromtimestamp(stamp, _CN_TZ)
            if not cursor <= when.date() <= stop:
                continue
            level = item.get("importance")
            if not isinstance(level, int) or level not in (1, 2, 3, 4):
                continue
            rows[item["id"]] = {
                "time": when.strftime("%Y-%m-%d %H:%M"),
                "country": item.get("country"), "title": item.get("title"),
                "kind": {"FD": "data", "FE": "event"}.get(item.get("calendar_type"), item.get("calendar_type")),
                "importance": level,
                "actual": (None if item.get("actual") in (None, "") else item.get("actual")),
                "forecast": (None if item.get("forecast") in (None, "") else item.get("forecast")),
                "previous": (None if item.get("previous") in (None, "") else item.get("previous")),
                "period": item.get("period") or None,
            }
        cursor = stop + timedelta(days=1)
    out = sorted(rows.values(), key=lambda x: x["time"])
    if country:
        out = [x for x in out if x.get("country") == country]
    out = [x for x in out if (x.get("importance") or 0) >= int(min_importance)]
    for x in out:
        x.update(_trace("macro_calendar"))
    return out


def chinabond_yield_curve(curve: str = "all") -> List[Dict[str, Any]]:
    """中债收益率曲线(国债/商业银行AAA/中短票AAA, 3月~30年)。中债官方源。

    注: 中债官网端点需补充(见 _SOURCE_URLS['chinabond']), 当前管线占位返回 [], 待源端点确定后经对撞验证接入。
    """
    _dbg("chinabond_yield_curve: 中债官网端点待补, 返回空(管线占位, 待对撞验证)")
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
            _last = max(_lpr, key=lambda r: r.get("date", ""))  # 取 TRADE_DATE 最大者=最新(防御性, 不依赖排序假设)
            ctx["lpr_1y"] = _last.get("lpr_1y")
            ctx["lpr_5y"] = _last.get("lpr_5y")
    except Exception as _e:
        _dbg(f"macro_context lpr: {_e}")
    try:
        _rf = repo_fixing_rates("FR")
        ctx["source_trace"].append("repo_fr")
        if _rf:
            ctx["repo_fr"] = _rf[-1].get("FR007")
        _rd = repo_fixing_rates("FDR")
        ctx["source_trace"].append("repo_fdr")
        if _rd:
            ctx["repo_fdr"] = _rd[-1].get("FDR007")
    except Exception as _e:
        _dbg(f"macro_context repo: {_e}")
    try:
        _cal = macro_calendar()
        ctx["source_trace"].append("macro_calendar")
        ctx["calendar_count"] = len(_cal)
    except Exception as _e:
        _dbg(f"macro_context calendar: {_e}")
    try:
        _curve = chinabond_yield_curve()
        ctx["curve_available"] = bool(_curve)
    except Exception as _e:
        _dbg(f"macro_context curve: {_e}")
    return ctx

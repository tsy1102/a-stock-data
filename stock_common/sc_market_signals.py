"""sc_market_signals.py — 吸收层市场级信号渲染器 (V17.4.1).

把新接入的吸收层数据源(申购日历/ETF份额/新浪研报/央视新闻联播/上证e互动/ST名单)
渲染为 markdown 行列表, 供 val/mak/med/lng 报告的市场级/个股级章节调用。

治理铁律(对齐 render_event_driven_section):
  - 每个源独立 try/except —— 单源失败仅在该章节显示"数据暂不可用", 不连累整份报告。
  - 字段语义以来源自身命名列(东财 datacenter 命名列/各源原生字段)为准;
    渲染时标注数据来源(通达信/东财/新浪/上交所/深交所/央视/上证e互动)。
  - 未对撞验证的字段仅展示记录条数+数据溯源, 不把未验证数值当权威结论(申购日历/ETF
    的命名列已为东财权威列, 可直接呈现; ST 名单源不可达时显式"暂缓接入"而非空名单)。

对外接口:
  render_market_signals_section(today_str) -> List[str]   # val/mak 市场级附录(6 源合一)
  render_stock_research_section(code) -> List[str]        # med/lng 个股研报
  render_stock_einteraction_section(code) -> List[str]     # med/lng 个股 e 互动
"""

from __future__ import annotations

import re
import threading
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from stock_common import _debug_log


# ---------------------------------------------------------------------------
# 内部工具
# ---------------------------------------------------------------------------
def _num(v: Any) -> Optional[float]:
    """转 float, 失败/空返回 None。"""
    if v is None or v == "":
        return None
    t = str(v).replace(",", "").strip()
    if t in ("", "-", "--", "None", "null", "NaN"):
        return None
    try:
        return float(t)
    except (ValueError, TypeError):
        return None


def _parse_date(s: Any) -> Optional[datetime]:
    """兼容 'YYYY-MM-DD' / 'YYYY-MM-DD HH:MM:SS' / 含时间戳字符串。"""
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except (ValueError, TypeError):
            continue
    m = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    return None


def _backtrack_days(n: int = 10) -> List[str]:
    """最近 n 个自然日 YYYY-MM-DD(含今天, 倒序无意义, 正序返回)。"""
    out, d = [], date.today()
    for _ in range(n):
        out.append(d.strftime("%Y-%m-%d"))
        d -= timedelta(days=1)
    return out


# ---------------------------------------------------------------------------
# 1) 申购日历 · 资金抽水压力
# ---------------------------------------------------------------------------
def render_ipo_calendar_section(
    today_str: Optional[str] = None, lookahead_days: int = 21
) -> List[str]:
    """近期新股申购日历 → 资金分流/抽水压力监测。

    抽水压力 = 未来 lookahead_days 日内申购新股数 + 预计募资合计(亿元, 已对撞订正)。
    募资额字段(TOTAL_RAISE_FUNDS/PREDICT_RAISE_FUNDS)单位=亿元: 对撞确认
    TOTAL_ISSUE_NUM(万股)*ISSUE_PRICE(元)/1e4 == TOTAL_RAISE_FUNDS(28点误差0)。
    数据来源: 东财 datacenter(reportName=RPTA_APP_IPOAPPLY, 已对撞校正)。
    """
    out: List[str] = ["## 【G. 近期新股申购日历 · 资金抽水压力监测】", ""]
    try:
        from stock_common.sc_datasource import ipo_calendar_recent

        rows = ipo_calendar_recent(40) or []
    except Exception as e:
        out.append(
            f"  ⚠️ 申购日历数据暂不可用（东财 datacenter, reportName=RPTA_APP_IPOAPPLY 已对撞校正）: {str(e)[:100]}"
        )
        return out
    if not rows:
        out.append("  （暂无申购日历数据）")
        return out

    today = _parse_date(today_str) or datetime.now()
    horizon = today + timedelta(days=lookahead_days)

    def _ad(r: Dict[str, Any]) -> Optional[datetime]:
        return _parse_date(r.get("APPLY_DATE"))

    def _rf(r: Dict[str, Any]) -> Optional[float]:
        # 募资额单位: 亿元(对撞确认, 见模块 docstring)
        return _num(r.get("TOTAL_RAISE_FUNDS")) or _num(r.get("PREDICT_RAISE_FUNDS"))

    upcoming: List[Dict[str, Any]] = []
    recent: List[Dict[str, Any]] = []
    in_horizon: List[Dict[str, Any]] = []
    for row in rows:
        apply_date = _ad(row)
        if apply_date is None:
            continue
        if apply_date >= today:
            upcoming.append(row)
            if apply_date <= horizon:
                in_horizon.append(row)
        else:
            recent.append(row)

    total_raise = 0.0
    for row in in_horizon:
        raise_amount = _rf(row)
        if raise_amount is not None:
            total_raise += raise_amount

    out.append(
        f"  💧 **抽水压力(以申购只数计)**: 未来 {lookahead_days} 日内有 **{len(in_horizon)}** 只新股申购"
        + (
            f"，预计募资约 **{total_raise:.1f} 亿元**（已定价/预测口径，待定价以预测值占位）"
            if total_raise > 0
            else ""
        )
        + f"（数据来源: 东财 datacenter, reportName=RPTA_APP_IPOAPPLY, 已对撞校正, 单位亿元）。"
    )
    out.append("")
    out.append("  **即将申购（按申购日）:**")
    out.append("  | 申购日 | 代码 | 名称 | 发行价 | 募资(亿) | 市场 | 状态 |")
    out.append("  |---|---|---|---|---|---|---|")
    for r in sorted(upcoming, key=lambda r: (_ad(r) or datetime.max))[:12]:
        ad = (r.get("APPLY_DATE") or "")[:10]
        code = r.get("SECURITY_CODE") or r.get("SECUCODE") or ""
        name = r.get("SECURITY_NAME_ABBR") or r.get("SECURITY_NAME") or ""
        price = _num(r.get("ISSUE_PRICE"))
        rf = _rf(r)
        rf_s = f"{rf:.2f}" if rf is not None else "待定"
        mkt = r.get("TRADE_MARKET") or r.get("MARKET_TYPE_NEW") or ""
        apply_date = _ad(r)
        state = "待申购" if apply_date is not None and apply_date >= today else "已申购"
        out.append(
            f"  | {ad} | {code} | {name} | {price if price is not None else '待定'} "
            f"| {rf_s} | {mkt} | {state} |"
        )
    if recent:
        out.append("")
        out.append("  **近期已申购（参考）:**")
        for r in recent[:5]:
            ad = (r.get("APPLY_DATE") or "")[:10]
            name = r.get("SECURITY_NAME_ABBR") or ""
            out.append(f"  • {ad} {name}（已申购）")
    out.append("")
    out.append(
        "  ⚠️ 抽水压力为定性监测指标：申购冻结资金会阶段性抽离二级市场流动性；"
        "募资额为已定价口径，待定价新股以预测值占位，不构成投资建议。"
    )
    return out


# ---------------------------------------------------------------------------
# 2) ETF 份额规模
# ---------------------------------------------------------------------------
def render_etf_shares_section(today_str: Optional[str] = None) -> List[str]:
    """ETF 份额(万份) → 市场资金载体规模。单日快照, 无环比。
    数据来源: 上交所 query.sse.com.cn / 深交所 www.szse.cn(主) + fund.szse.cn(兜底)。
    """
    out: List[str] = ["## 【H. ETF 份额规模（市场资金载体）】", ""]

    def _fetch_etf(
        exchange: str,
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
        """取最近一个有数据的快照。SH 按日归档可回退; SZ 仅最新一日快照(不回退历史日)。"""
        if exchange == "SZ":
            # 深交所仅提供最新一日快照, 单次尝试 + 硬超时(避免受限网络下逐日回退×多主机挂死报告)
            box: Dict[str, Optional[List[Dict[str, Any]]]] = {}

            def _run() -> None:
                try:
                    box["rows"] = etf_shares(
                        today_str[:10] if today_str else date.today().strftime("%Y-%m-%d"), "SZ"
                    )
                except Exception:
                    box["rows"] = None

            t = threading.Thread(target=_run, daemon=True)
            t.start()
            t.join(timeout=25)
            if t.is_alive():
                return None, None
            return box.get("rows"), (today_str[:10] if today_str else None)
        for day in _backtrack_days(10):
            try:
                rows = etf_shares(day, exchange)
            except Exception:
                rows = None
            if rows:
                return rows, day
        return None, None

    try:
        from stock_common.sc_datasource import etf_shares

        sh_rows, sh_day = _fetch_etf("SH")
        sz_rows, sz_day = _fetch_etf("SZ")
    except Exception as e:
        out.append(f"  ⚠️ ETF份额数据暂不可用（上交所/深交所）: {str(e)[:100]}")
        return out

    if not sh_rows and not sz_rows:
        out.append("  （近日暂无 ETF 份额数据）")
        return out

    sh_rows = sh_rows or []
    sz_ok = sz_rows is not None  # None = 深交所接口暂不可用; [] = 确无数据
    sz_rows = sz_rows or []
    sh_total = sum(_num(r.get("shares_10k")) or 0.0 for r in sh_rows)
    sz_total = sum(_num(r.get("shares_10k")) or 0.0 for r in sz_rows)
    sz_part = (
        f"深市 {len(sz_rows)} 只(总份额 {sz_total / 1e4:.1f} 亿份"
        + (f", 截至 {sz_day}" if sz_day else "")
        + ")"
        if sz_ok
        else "深市 ETF 数据暂不可用（深交所接口, 待恢复）"
    )
    out.append(
        f"  数据来源: 上交所/深交所（单日快照, 无环比）｜"
        f"沪市 {len(sh_rows)} 只(总份额 {sh_total / 1e4:.1f} 亿份"
        + (f", 截至 {sh_day}" if sh_day else "")
        + ")｜"
        + sz_part
    )
    out.append("")
    out.append("  **沪市 ETF 份额 TOP10:**")
    out.append("  | 代码 | 名称 | 类型 | 份额(万份) |")
    out.append("  |---|---|---|---|")
    for r in sorted(sh_rows, key=lambda r: _num(r.get("shares_10k")) or 0.0, reverse=True)[:10]:
        out.append(
            f"  | {r.get('code')} | {r.get('name')} | {r.get('etf_type') or ''} "
            f"| {_num(r.get('shares_10k')) or 0:,.0f} |"
        )
    return out


# ---------------------------------------------------------------------------
# 3) 新浪研报风向（市场级）
# ---------------------------------------------------------------------------
def render_sina_research_section(today_str: Optional[str] = None) -> List[str]:
    """全市场最新研报风向。数据来源: 新浪财经研报。"""
    out: List[str] = ["## 【I. 新浪研报风向（全市场最新）】", ""]
    try:
        from stock_common.sc_datasource import sina_research_reports

        rows = sina_research_reports(page=1) or []
    except Exception as e:
        out.append(f"  ⚠️ 新浪研报数据暂不可用: {str(e)[:100]}")
        return out
    if not rows:
        out.append("  （暂无研报）")
        return out
    out.append(
        f"  数据来源: 新浪财经研报（最新 {len(rows)} 条）｜仅展示标题与机构, 字段语义待对撞订正"
    )
    out.append("")
    for r in rows[:15]:
        d = (r.get("date") or "")[:10]
        t = r.get("title") or ""
        org = r.get("org") or ""
        rtype = r.get("type") or ""
        out.append(f"  • [{d}] 【{rtype}】{t} — {org}")
    return out


# ---------------------------------------------------------------------------
# 4) 央视《新闻联播》要闻
# ---------------------------------------------------------------------------
def render_cctv_news_section(today_str: Optional[str] = None) -> List[str]:
    """央视《新闻联播》要闻 → 政策情绪。数据来源: 央视网。"""
    out: List[str] = ["## 【J. 央视《新闻联播》要闻（政策情绪）】", ""]
    try:
        from stock_common.sc_datasource import cctv_news

        rows = None
        for day in _backtrack_days(7):
            try:
                rows = cctv_news(day)
            except Exception:
                rows = None
            if rows:
                break
    except Exception as e:
        out.append(f"  ⚠️ 央视新闻数据暂不可用: {str(e)[:100]}")
        return out
    if not rows:
        out.append("  （近日无《新闻联播》条目）")
        return out
    out.append("  数据来源: 央视网《新闻联播》（最近有条目日）")
    out.append("")
    for r in rows[:12]:
        d = (r.get("date") or "")[:10]
        t = r.get("title") or ""
        out.append(f"  • [{d}] {t}")
    return out


# ---------------------------------------------------------------------------
# 5) 上证 e 互动（市场级）
# ---------------------------------------------------------------------------
def render_sse_e_interaction_section(today_str: Optional[str] = None) -> List[str]:
    """上证 e 互动市场级问答 → 投资者关切。数据来源: 上证 e 互动(sns.sseinfo.com)。"""
    out: List[str] = ["## 【K. 上证e互动 · 市场级问答（投资者关切）】", ""]
    try:
        from stock_common.sc_datasource import sse_e_interaction

        rows = sse_e_interaction(kind="answered", page=1, page_size=15) or []
    except Exception as e:
        out.append(f"  ⚠️ 上证e互动数据暂不可用: {str(e)[:100]}")
        return out
    if not rows:
        out.append("  （暂无问答）")
        return out
    out.append("  数据来源: 上证e互动（sns.sseinfo.com, 市场级最新已回答）")
    out.append("")
    for r in rows[:12]:
        code = r.get("code") or ""
        name = r.get("name") or ""
        q = (r.get("question") or "").replace("\n", " ")[:60]
        qt = (r.get("question_time") or "")[:10]
        out.append(f"  • {code} {name}（{qt}）: {q}…")
    return out


# ---------------------------------------------------------------------------
# 6) ST / *ST 名单（源不可达时显式暂缓, 不伪装空名单）
# ---------------------------------------------------------------------------
def render_st_list_section(today_str: Optional[str] = None) -> List[str]:
    """沪深京 ST/*ST 风险警示名单。数据来源: 东财风险警示板 + 北交所全表按名筛。
    源(东财 push2 clist)不可达时显式"暂缓接入", 不展示空名单(治理铁律)。
    """
    _title = "## 【L. 风险警示（ST/*ST）名单"
    out: List[str] = []
    try:
        from stock_common.sc_datasource import st_stock_list

        rows = st_stock_list()
    except Exception as e:
        out.append(f"{_title} · 待源恢复】")
        out.append("")
        out.append(
            "  ⚠️ ST名单源(东财 push2 clist)当前不可达，本信号**暂缓接入**；源恢复后自动显示（不展示空名单）。"
        )
        out.append(f"  （诊断: {str(e)[:90]}）")
        return out
    if not rows:
        out.append(f"{_title} · 无数据】")
        out.append("")
        out.append("  （当前无 ST/*ST 名单数据）")
        return out
    out.append(f"{_title}】")
    out.append("")
    from collections import Counter

    c = Counter(r.get("market") for r in rows)
    out.append(
        f"  数据来源: 东财风险警示板（沪深）+ 北交所全表按名筛 ｜ 共 {len(rows)} 只: "
        + ", ".join(f"{k} {v}" for k, v in c.items())
    )
    out.append("")
    out.append("  | 代码 | 市场 | 名称 | 类型 | 现价 | 涨跌幅 |")
    out.append("  |---|---|---|---|---|---|")

    def _cell(v: Any) -> Any:
        return "—" if v is None or v == "" else v

    for r in rows[:30]:
        out.append(
            f"  | {_cell(r.get('code'))} | {_cell(r.get('market'))} | {_cell(r.get('name'))} | {_cell(r.get('st_type'))} "
            f"| {_cell(r.get('price'))} | {_cell(r.get('pct_change'))} |"
        )
    return out


# ---------------------------------------------------------------------------
# 组合: val/mak 市场级附录
# ---------------------------------------------------------------------------
def render_market_signals_section(today_str: Optional[str] = None) -> List[str]:
    """val/mak 市场级附录: 6 源合一。每个源独立渲染, 互不影响。"""
    parts: List[str] = []
    parts += render_ipo_calendar_section(today_str)
    parts += ["", "---", ""]
    parts += render_etf_shares_section(today_str)
    parts += ["", "---", ""]
    parts += render_sina_research_section(today_str)
    parts += ["", "---", ""]
    parts += render_cctv_news_section(today_str)
    parts += ["", "---", ""]
    parts += render_sse_e_interaction_section(today_str)
    parts += ["", "---", ""]
    parts += render_st_list_section(today_str)
    return parts


# ---------------------------------------------------------------------------
# 个股级( med/lng ): 研报 + e 互动
# ---------------------------------------------------------------------------
def render_stock_research_section(code: str) -> List[str]:
    """个股新浪研报(med/lng 个股报告补充)。数据来源: 新浪财经研报。"""
    out: List[str] = ["## 【补充·个股研报（新浪）】", ""]
    if not code:
        out.append("  （无个股代码）")
        return out
    try:
        from stock_common.sc_datasource import sina_research_reports

        rows = sina_research_reports(code=code, page=1) or []
    except Exception as e:
        out.append(f"  ⚠️ 个股研报数据暂不可用: {str(e)[:100]}")
        return out
    if not rows:
        out.append(f"  （{code} 近暂无新浪研报）")
        return out
    out.append(f"  数据来源: 新浪财经研报（{code}）")
    out.append("")
    for r in rows[:10]:
        d = (r.get("date") or "")[:10]
        t = r.get("title") or ""
        org = r.get("org") or ""
        out.append(f"  • [{d}] {t} — {org}")
    return out


def render_stock_einteraction_section(code: str) -> List[str]:
    """个股上证 e 互动(med/lng 个股报告补充)。数据来源: 上证 e 互动。"""
    out: List[str] = ["## 【补充·个股上证e互动】", ""]
    if not code:
        out.append("  （无个股代码）")
        return out
    try:
        from stock_common.sc_datasource import sse_e_interaction

        rows = sse_e_interaction(code=code, kind="answered", page=1, page_size=10) or []
    except Exception as e:
        out.append(f"  ⚠️ 个股e互动数据暂不可用: {str(e)[:100]}")
        return out
    if not rows:
        out.append(f"  （{code} 近暂无 e 互动问答）")
        return out
    out.append(f"  数据来源: 上证e互动（{code}）")
    out.append("")
    for r in rows[:10]:
        q = (r.get("question") or "").replace("\n", " ")[:70]
        qt = (r.get("question_time") or "")[:10]
        out.append(f"  • [{qt}] {q}…")
    return out

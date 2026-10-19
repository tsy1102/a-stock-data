# -*- coding: utf-8 -*-
"""数据维度充实辅助（V17.2.x 字段治理补充）。

设计铁律（防止引入 bug）：
- 本模块为**纯函数 + 只读**，不发起任何网络/IO，不修改任何全局状态。
- 所有取值走 `_v()` 统一安全访问（canonical dataclass 用 getattr，dict 用 .get），
  缺失/None/非数字一律回退 0，绝不抛异常。
- 所有除法前做分母保护，避免 ZeroDivisionError。
- 每个对外函数均包裹防御，即使内部异常也返回 []，由调用方 try/except 兜底。
- 仅消费已在统一层 CanonicalStockData 归一化（已取数、已清洗、已 QC）的字段，
  不新增任何采集。契合项目"轻量优先"铁律。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List

__all__ = [
    "earnings_quality_lines",
    "cash_content_lines",
    "fuyao_report_period_candidates",
    "tdx_snapshot_period_context",
    "fund_flow_detail_lines",
    "order_book_lines",
    "rotation_context_lines",
    "long_term_return_lines",
    "quality_gate_lines",
    "mak_stock_lines",
    "sec_type_label",
]


def _v(obj: Any, name: str, default: float = 0.0) -> float:
    """统一安全取值：canonical dataclass 走 getattr，dict 走 .get。"""
    try:
        if isinstance(obj, dict):
            v = obj.get(name, default)
        else:
            v = getattr(obj, name, default)
        if v is None or v == "":
            return default
        return float(v)
    except (TypeError, ValueError, AttributeError):
        return default


def _fmt_pct(v: float, sign: bool = True) -> str:
    if sign and v > 0:
        return f"+{v:.2f}%"
    return f"{v:.2f}%"


def _safe_div(a: float, b: float) -> float:
    try:
        if b == 0:
            return 0.0
        return a / b
    except Exception:
        return 0.0


def _report_period_label(cdata: Any) -> str:
    raw = (
        cdata.get("report_period", "")
        if isinstance(cdata, dict)
        else getattr(cdata, "report_period", "")
    )
    digits = "".join(char for char in str(raw or "") if char.isdigit())
    if len(digits) >= 8:
        try:
            report_date = datetime.strptime(digits[:8], "%Y%m%d")
        except ValueError:
            return "未标注"
        return report_date.strftime("%Y-%m-%d")
    return "未标注"


def fuyao_report_period_candidates(report_period: Any, limit: int = 2) -> List[str]:
    """按统一层最新财报日期生成 Fuyao 季度查询键，最多回退到前一季度。"""
    try:
        digits = "".join(char for char in str(report_period or "") if char.isdigit())
        if len(digits) < 8:
            return []
        report_date = datetime.strptime(digits[:8], "%Y%m%d")
        if report_date.month not in (3, 6, 9, 12):
            return []
        candidate_count = max(0, min(int(limit), 4))
        if candidate_count == 0:
            return []
        year = report_date.year
        quarter = (report_date.month - 1) // 3 + 1
        candidates: List[str] = []
        for _ in range(candidate_count):
            candidates.append(f"{year}-{quarter}")
            quarter -= 1
            if quarter == 0:
                year -= 1
                quarter = 4
        return candidates
    except (TypeError, ValueError, OverflowError):
        return []


def tdx_snapshot_period_context(report_period: Any, disclosure_date: Any = "") -> str:
    """明确区分统一层财报期参考值与 TDX 0x0010 快照自身的期别信息。"""
    canonical_period = _report_period_label({"report_period": report_period})
    if canonical_period == "未标注":
        context = "TDX 快照报告期未由接口字段确认"
    else:
        context = f"统一层参考报告期 {canonical_period}（TDX 未独立确认期别）"
    raw_disclosure_date = str(disclosure_date or "").strip()
    if raw_disclosure_date:
        context += f"，TDX 披露日 {raw_disclosure_date}"
    return context


def earnings_quality_lines(cdata: Any) -> List[str]:
    """列示盈利质量字段；期间不一致或缺失时不计算虚假的质量比值。"""
    try:
        eps = _v(cdata, "eps")
        eps_d = _v(cdata, "eps_deduct_ttm")
        roe = _v(cdata, "roe")
        roe_d = _v(cdata, "roe_deduct_ttm")
        if eps == 0 and eps_d == 0 and roe == 0 and roe_d == 0:
            return []
        out: List[str] = []
        report_period = _report_period_label(cdata)
        out.append("  📊 **盈利质量字段核对**")
        if eps != 0:
            out.append(f"  - 归母EPS(统一层字段)={eps:.2f}元/股（报告期 {report_period}）")
        else:
            out.append("  - 归母EPS(统一层字段)未取到")
        if eps_d != 0:
            out.append(f"  - 扣非EPS(TTM)={eps_d:.2f}元/股")
        else:
            out.append("  - 扣非EPS(TTM)未取到")
        if eps != 0 or eps_d != 0:
            out.append("  - ℹ️ 归母EPS字段与扣非EPS(TTM)期间未确认一致，不计算占比。")
        if roe != 0:
            out.append(f"  - ROE(报告期 {report_period})={roe:.1f}%")
        if roe_d != 0:
            out.append(f"  - 扣非ROE(TTM)={roe_d:.1f}%")
        if roe != 0 and roe_d != 0:
            out.append("  - ℹ️ ROE 与扣非ROE统计期间不同，不以差额推断非经常性损益影响。")
        return out
    except Exception:
        return []


def cash_content_lines(cdata: Any) -> List[str]:
    """列示现金流与净利润；未确认同期间前不计算现金含量比。"""
    try:
        ocf = _v(cdata, "ocf_ttm")
        npf = _v(cdata, "net_profit")
        if ocf == 0 and npf == 0:
            return []
        out: List[str] = []
        out.append("  💰 **现金流与净利润期间核对**")
        report_period = _report_period_label(cdata)
        ocf_label = (
            f"经营现金流净额(TTM)={ocf/1e8:.2f}亿" if ocf != 0 else "经营现金流净额(TTM)未取到"
        )
        if npf != 0:
            np_label = f"净利润(报告期 {report_period})={npf/1e8:.2f}亿"
        else:
            np_label = f"净利润(报告期 {report_period})未取到"
        out.append(f"  - {ocf_label}；{np_label}")
        if ocf != 0 and npf != 0:
            out.append("  - ℹ️ TTM现金流与最新报告期净利润期间不同，不计算现金含量比。")
        elif report_period == "未标注":
            out.append("  - ℹ️ 净利润报告期未标注，无法确认期间匹配，不计算现金含量比。")
        return out
    except Exception:
        return []


def fund_flow_detail_lines(cdata: Any) -> List[str]:
    """主力/超大单/大单买卖毛额 + 主买占比。短线识别对倒虚量。"""
    try:
        mb = _v(cdata, "fund_main_buy")
        ms = _v(cdata, "fund_main_sell")
        sb = _v(cdata, "fund_super_buy")
        ss = _v(cdata, "fund_super_sell")
        lb = _v(cdata, "fund_large_buy")
        ls = _v(cdata, "fund_large_sell")
        if mb == 0 and ms == 0 and sb == 0 and ss == 0 and lb == 0 and ls == 0:
            return []
        out: List[str] = []
        out.append("  🔥 **主力资金买卖毛额（今日，识别对倒虚量）**")
        total = mb + ms
        if total > 0:
            buy_ratio = _safe_div(mb, total) * 100
            out.append(
                f"  - 主力买入={mb/1e8:.2f}亿 / 卖出={ms/1e8:.2f}亿 → 主买占比{buy_ratio:.1f}%（>55%为真金做多，≈50%警惕对倒）"
            )
        else:
            out.append(f"  - 主力买入={mb/1e8:.2f}亿 / 卖出={ms/1e8:.2f}亿（净额数据缺失）")
        stotal = sb + ss
        if stotal > 0:
            out.append(f"  - 超大单: 买={sb/1e8:.2f}亿 / 卖={ss/1e8:.2f}亿（机构力道）")
        ltotal = lb + ls
        if ltotal > 0:
            out.append(f"  - 大单: 买={lb/1e8:.2f}亿 / 卖={ls/1e8:.2f}亿（游资/大户力道）")
        return out
    except Exception:
        return []


def order_book_lines(cdata: Any) -> List[str]:
    """盘口：委比、内外盘、买卖二价、涨速。短线情绪锋利信号。

    注：买二/卖二(bid2/ask2) 统一层自承口径未定案(L4)，且实测常出现与现价
    偏离数倍的脏回退值。故加带宽 sanity gate：仅当与现价(price)同量级
    (±15%)且买二<=卖二时渲染，越界视为脏数据隐藏，避免误导。
    """
    try:
        er = _v(cdata, "entrust_ratio")
        bv = _v(cdata, "b_vol")
        sv = _v(cdata, "s_vol")
        bid2 = _v(cdata, "bid2")
        ask2 = _v(cdata, "ask2")
        rs = _v(cdata, "rise_speed")
        price = _v(cdata, "price")
        if er == 0 and bv == 0 and sv == 0 and bid2 == 0 and ask2 == 0 and rs == 0:
            return []
        out: List[str] = []
        out.append("  📗 **盘口与实时情绪**")
        if er != 0:
            tag = "买盘挂单占优" if er > 0 else "卖盘挂单占优"
            out.append(f"  - 委比={er:.1f}%（{tag}）")
        tot = bv + sv
        if tot > 0:
            out.append(
                f"  - 外盘(主动买)={bv/1e4:.1f}万手 / 内盘(主动卖)={sv/1e4:.1f}万手 → 主动买占比{_safe_div(bv,tot)*100:.1f}%"
            )
        # 买二/卖二 sanity gate：L4 未定案字段, 仅当与现价同量级且买二<=卖二时渲染, 越界隐藏
        if bid2 > 0 and ask2 > 0 and price > 0:
            _in_band = (price * 0.85 <= bid2 <= price * 1.15) and (
                price * 0.85 <= ask2 <= price * 1.15
            )
            _no_cross = bid2 <= ask2
            if _in_band and _no_cross:
                out.append(f"  - 买二={bid2:.2f}元 / 卖二={ask2:.2f}元（盘口支撑/压力位）")
        if rs != 0:
            out.append(f"  - 涨速={rs:.2f}%/min（异动启动先行指标）")
        return out
    except Exception:
        return []


def rotation_context_lines(cdata: Any) -> List[str]:
    """区间涨跌（60日/YTD/20日）识别中期主线，过滤一日游。"""
    try:
        c60 = _v(cdata, "change_60d")
        cytd = _v(cdata, "change_ytd")
        c20 = _v(cdata, "change_20d")
        if c60 == 0 and cytd == 0 and c20 == 0:
            return []
        out: List[str] = []
        out.append("  🧭 **中期区间表现（主线识别）**")
        out.append(
            f"  - 近20日={_fmt_pct(c20)} | 近60日={_fmt_pct(c60)} | 年初至今={_fmt_pct(cytd)}"
        )
        if c60 > 30:
            out.append("  - 60日强势，属中期主线候选；注意高位回撤风险")
        elif c60 < -20:
            out.append("  - 60日深度调整，关注超跌修复机会")
        return out
    except Exception:
        return []


def long_term_return_lines(cdata: Any) -> List[str]:
    """长线股东回报质量：未分配利润可持续性 + 业绩连续性。"""
    try:
        udp = _v(cdata, "undist_profit_ps")
        eps_d = _v(cdata, "eps_deduct_ttm")
        if udp == 0 and eps_d == 0:
            return []
        out: List[str] = []
        out.append("  🏦 **长效股东回报质量**")
        if udp != 0:
            tag = "分红底仓厚实" if udp > 3 else ("分红空间有限" if udp < 1 else "中性")
            out.append(f"  - 每股未分配利润={udp:.2f}元（{tag}，高未分配利润+稳定分红=可持续）")
        if eps_d != 0:
            out.append(f"  - 扣非EPS(TTM)={eps_d:.2f}元/股（长线看业绩连续性，扣非口径剔除噪音）")
        return out
    except Exception:
        return []


def quality_gate_lines(cdata: Any) -> List[str]:
    """核心行情有效性与关键字段来源；is_valid 不代表报告各章节数据完整。"""
    try:
        is_valid = getattr(cdata, "is_valid", True)
        fs = getattr(cdata, "field_sources", None) or {}
        price_src = fs.get("price", "")
        pe_src = fs.get("pe_ttm", "")
        out: List[str] = []
        out.append("  🔎 **核心行情有效性**")
        out.append(f"  - 现价/昨收校验(is_valid)={'通过' if is_valid else '未通过'}")
        out.append("  - 校验范围仅限证券代码与现价/昨收，不代表资金流、筹码等章节完整")
        if price_src:
            out.append(f"  - 价格来源={price_src}（实时路径优先，缺失回落兜底）")
        if pe_src:
            out.append(f"  - PE(TTM)来源={pe_src}")
        if not is_valid:
            out.append("  - ⚠️ 核心行情校验未通过，价格相关结论仅供参考")
        return out
    except Exception:
        return []


def mak_stock_lines(s: dict) -> List[str]:
    """mak 全市场扫描场景：仅用 ZHB 快照 dict 已有字段（零新增取数）。

    s 可用键（已核实 get_market_abnormal_data 返回）：ret_60d/ret_20d/ret_10d/ret_5d、
    turnover、mcap_yi、main_inflow、code、name、change_pct。
    sec_type 由 code 前缀派生（与 sec_type_market_label 同口径），不取数。
    """
    try:
        if not isinstance(s, dict):
            return []
        r60 = float(s.get("ret_60d", 0) or 0)
        r20 = float(s.get("ret_20d", 0) or 0)
        r10 = float(s.get("ret_10d", 0) or 0)
        r5 = float(s.get("ret_5d", 0) or 0)
        turnover = float(s.get("turnover", 0) or 0)
        mcap = float(s.get("mcap_yi", 0) or 0)
        inflow = float(s.get("main_inflow", 0) or 0)
        code = str(s.get("code", "") or "")
        if (
            r60 == 0
            and r20 == 0
            and r10 == 0
            and r5 == 0
            and turnover == 0
            and mcap == 0
            and inflow == 0
        ):
            return []
        out: List[str] = []
        out.append(
            f"  区间收益: 5日{_fmt_pct(r5)} | 10日{_fmt_pct(r10)} | 20日{_fmt_pct(r20)} | 60日{_fmt_pct(r60)}"
        )
        if turnover > 0:
            out.append(f"  换手率={turnover:.2f}% | 总市值={mcap:.1f}亿")
        if inflow != 0:
            out.append(f"  主力净流入={inflow/1e8:+.2f}亿")
        # 市场分层（code 前缀派生，零取数）
        if code:
            _lay = _sec_type_label(code)
            out.append(f"  市场分层: {_lay}")
        return out
    except Exception:
        return []


def _sec_type_label(code: str) -> str:
    """code 前缀 → 市场类型标签（与 sec_type_market_label 同口径，避免重复取数）。"""
    try:
        if code.startswith("688") or code.startswith("689"):
            return "科创板"
        if code.startswith("8") or code.startswith("4"):
            return "北交所"
        if code.startswith("30"):
            return "创业板"
        if code.startswith("00") or code.startswith("60"):
            return "主板"
        if code.startswith("20") or code.startswith("39"):
            return "北交所/其他"
        return "其他"
    except Exception:
        return "其他"


def sec_type_label(code: str) -> str:
    """公开：code 前缀 → 市场类型标签（零取数，供 val/mak 选股分层标注）。"""
    return _sec_type_label(code)

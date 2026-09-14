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

from typing import Any, List

__all__ = [
    "earnings_quality_lines",
    "cash_content_lines",
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


def earnings_quality_lines(cdata: Any) -> List[str]:
    """盈利质量（扣非 vs 归母、ROE 扣非）。med/lng 排雷用。"""
    try:
        eps = _v(cdata, "eps")
        eps_d = _v(cdata, "eps_deduct_ttm")
        roe = _v(cdata, "roe")
        roe_d = _v(cdata, "roe_deduct_ttm")
        if eps == 0 and eps_d == 0 and roe == 0 and roe_d == 0:
            return []
        out: List[str] = []
        out.append("  📊 **盈利质量（扣非口径排雷）**")
        if eps != 0:
            ratio = _safe_div(eps_d, eps)
            tag = "健康" if ratio >= 0.85 else ("⚠️非经常性损益占比偏高" if ratio < 0.7 else "中性")
            out.append(f"  - 扣非EPS(TTM)={eps_d:.2f}元/股，占归母EPS({eps:.2f})的{ratio*100:.0f}%（{tag}）")
        else:
            out.append(f"  - 扣非EPS(TTM)={eps_d:.2f}元/股（归母EPS缺失，以扣非口径为准）")
        if roe != 0 or roe_d != 0:
            diff = roe - roe_d
            out.append(f"  - ROE={roe:.1f}% / 扣非ROE={roe_d:.1f}%（差额{diff:+.1f}pt，差额为正=非经常性损益撑净资产收益）")
        return out
    except Exception:
        return []


def cash_content_lines(cdata: Any) -> List[str]:
    """净利现金含量（OCF/净利润）。中线排雷核心。"""
    try:
        ocf = _v(cdata, "ocf_ttm")
        npf = _v(cdata, "net_profit")
        if ocf == 0 and npf == 0:
            return []
        out: List[str] = []
        out.append("  💰 **净利现金含量（经营现金流/净利润）**")
        if npf > 0:
            ratio = _safe_div(ocf, npf)
            tag = "✅真金白银" if ratio >= 0.8 else ("⚠️盈利含金量偏低（赊销/应收注水风险）" if ratio < 0.5 else "中性")
            # net_profit 单位元；ocf_ttm 单位元，比值无量纲
            out.append(f"  - OCF(TTM)={ocf/1e8:.2f}亿 / 净利润={npf/1e8:.2f}亿 → 比值{ratio:.2f}（{tag}）")
        elif npf < 0:
            out.append(f"  - 净利润为负({npf/1e8:.2f}亿)，OCF(TTM)={ocf/1e8:.2f}亿（关注是否靠经营回款续命）")
        else:
            out.append(f"  - OCF(TTM)={ocf/1e8:.2f}亿（净利润缺失，仅列经营现金流）")
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
            out.append(f"  - 主力买入={mb/1e8:.2f}亿 / 卖出={ms/1e8:.2f}亿 → 主买占比{buy_ratio:.1f}%（>55%为真金做多，≈50%警惕对倒）")
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
    """盘口：委比、内外盘、买卖二价、涨速。短线情绪锋利信号。"""
    try:
        er = _v(cdata, "entrust_ratio")
        bv = _v(cdata, "b_vol")
        sv = _v(cdata, "s_vol")
        bid2 = _v(cdata, "bid2")
        ask2 = _v(cdata, "ask2")
        rs = _v(cdata, "rise_speed")
        if er == 0 and bv == 0 and sv == 0 and bid2 == 0 and ask2 == 0 and rs == 0:
            return []
        out: List[str] = []
        out.append("  📗 **盘口与实时情绪**")
        if er != 0:
            tag = "买盘挂单占优" if er > 0 else "卖盘挂单占优"
            out.append(f"  - 委比={er:.1f}%（{tag}）")
        tot = bv + sv
        if tot > 0:
            out.append(f"  - 外盘(主动买)={bv/1e4:.1f}万手 / 内盘(主动卖)={sv/1e4:.1f}万手 → 主动买占比{_safe_div(bv,tot)*100:.1f}%")
        if bid2 > 0 and ask2 > 0:
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
        out.append(f"  - 近20日={_fmt_pct(c20)} | 近60日={_fmt_pct(c60)} | 年初至今={_fmt_pct(cytd)}")
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
    """数据质量门禁：is_valid + 关键字段来源标注。"""
    try:
        is_valid = getattr(cdata, "is_valid", True)
        fs = getattr(cdata, "field_sources", None) or {}
        price_src = fs.get("price", "")
        pe_src = fs.get("pe_ttm", "")
        out: List[str] = []
        out.append("  🔎 **数据质量门禁**")
        out.append(f"  - 数据合法性(is_valid)={is_valid}")
        if price_src:
            out.append(f"  - 价格来源={price_src}（实时路径优先，缺失回落兜底）")
        if pe_src:
            out.append(f"  - PE(TTM)来源={pe_src}")
        if not is_valid:
            out.append("  - ⚠️ 本标的快照合法性校验未通过，以上数值仅供参考")
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
        if r60 == 0 and r20 == 0 and r10 == 0 and r5 == 0 and turnover == 0 and mcap == 0 and inflow == 0:
            return []
        out: List[str] = []
        out.append(f"  区间收益: 5日{_fmt_pct(r5)} | 10日{_fmt_pct(r10)} | 20日{_fmt_pct(r20)} | 60日{_fmt_pct(r60)}")
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

#!/usr/bin/env python3
"""valuation_methods.py — 机构级估值方法库 V1.0 (V8.5内置模块)

版本信息:
    V1.0 2026-06-22 - 初始版本，支持DCF/DDM/PEG/LBO等估值方法
    V8.5 - 集成到个股分析系统

支持多种估值方法：
1. DCF (现金流折现)
2. 股息折现模型 (DDM)
3. PEG估值
4. LBO (杠杆收购)
5. PEGY (股息调整后PEG)
6. 行业PE比较
7. PB-ROE矩阵
8. 股价/自由现金流

Usage:
    from valuation_methods import (
        dcf_valuation, ddm_valuation, peg_valuation,
        lbo_valuation, industry_pe_compare,
        pb_roe_matrix, get_intrinsic_value
    )
"""

import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValuationResult:
    """估值结果"""
    method: str
    intrinsic_value: float
    current_price: float
    upside: float  # 上涨空间百分比
    downside: float  # 下跌空间百分比
    verdict: str  # 低估/合理/高估
    confidence: str  # 高/中/低
    details: Dict[str, Any] = None
    notes: str = ""

    def __post_init__(self):
        if self.details is None:
            self.details = {}


def _safe_float(val: Any, default: float = 0.0) -> float:
    """安全转换为float"""
    try:
        v = float(val)
        return v if math.isfinite(v) else default
    except (TypeError, ValueError):
        return default


def _calc_upside_downside(intrinsic: float, current: float) -> Tuple[float, float]:
    """计算上涨/下跌空间"""
    if current <= 0:
        return 0.0, 0.0
    upside = (intrinsic - current) / current * 100
    downside = (current - intrinsic * 0.8) / current * 100  # 假设合理价位是内在价值的80%
    return round(upside, 1), round(downside, 1)


def _verdict_from_upside(upside: float) -> str:
    """根据上涨空间判断估值"""
    if upside > 30:
        return "低估"
    elif upside > 10:
        return "偏低"
    elif upside > -10:
        return "合理"
    elif upside > -30:
        return "偏高"
    else:
        return "高估"


def dcf_valuation(fcf_forecast: List[float],
                 wacc: float = 0.10,
                 terminal_growth: float = 0.03,
                 shares_outstanding: float = 1.0,
                 terminal_multiple: float = 15.0) -> ValuationResult:
    """DCF现金流折现估值

    Args:
        fcf_forecast: 未来各年自由现金流预测 [year1, year2, year3, ...]
        wacc: 加权平均资本成本 (默认10%)
        terminal_growth: 永续增长率 (默认3%)
        shares_outstanding: 流通股数(亿股)
        terminal_multiple: 永续年金倍数 (默认15倍)

    Returns:
        ValuationResult: DCF估值结果
    """
    if not fcf_forecast or wacc <= terminal_growth:
        return ValuationResult(
            method="DCF",
            intrinsic_value=0,
            current_price=0,
            upside=0,
            downside=0,
            verdict="无法估值",
            confidence="低",
            notes="现金流预测为空或WACC<=终端增长率"
        )

    # 计算预测期现金流现值
    pv_sum = 0.0
    for i, fcf in enumerate(fcf_forecast):
        discount_factor = (1 + wacc) ** (i + 1)
        pv_sum += fcf / discount_factor

    # 计算终值 (TV = FCF_n * (1+g) / (WACC - g) 或使用倍数法)
    last_fcf = fcf_forecast[-1] if fcf_forecast else 0
    # 永续年金法
    # terminal_value = last_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
    # 倍数法 (更常用)
    terminal_value = last_fcf * terminal_multiple

    # 折现终值
    n = len(fcf_forecast)
    pv_terminal = terminal_value / (1 + wacc) ** n

    # 企业价值 = 预测期现值 + 终值现值
    enterprise_value = pv_sum + pv_terminal

    # 股权价值 = 企业价值 - 净债务 (简化处理，假设无净债务)
    equity_value = enterprise_value

    # 每股价值
    if shares_outstanding > 0:
        intrinsic_value = equity_value / shares_outstanding
    else:
        intrinsic_value = 0

    upside, downside = _calc_upside_downside(intrinsic_value, 0)  # current_price需要外部传入

    return ValuationResult(
        method="DCF",
        intrinsic_value=round(intrinsic_value, 2),
        current_price=0,
        upside=0,
        downside=0,
        verdict="需要当前价格",
        confidence="中",
        details={
            "wacc": wacc,
            "terminal_growth": terminal_growth,
            "terminal_multiple": terminal_multiple,
            "pv_sum": round(pv_sum, 2),
            "pv_terminal": round(pv_terminal, 2),
            "enterprise_value": round(enterprise_value, 2),
            "fcf_forecast": fcf_forecast
        },
        notes=f"WACC={wacc*100:.1f}%, 永续增长率={terminal_growth*100:.1f}%"
    )


def ddm_valuation(dividend_forecast: List[float],
                  required_return: float = 0.10,
                  terminal_growth: float = 0.03,
                  shares_outstanding: float = 1.0) -> ValuationResult:
    """股息折现模型 (DDM)

    适用于高分红、稳定的蓝筹股

    Args:
        dividend_forecast: 未来各年股息预测 [year1, year2, year3, ...]
        required_return: 必要收益率 (默认10%)
        terminal_growth: 永续增长率 (默认3%)
        shares_outstanding: 流通股数(亿股)

    Returns:
        ValuationResult: DDM估值结果
    """
    if not dividend_forecast or required_return <= terminal_growth:
        return ValuationResult(
            method="DDM",
            intrinsic_value=0,
            current_price=0,
            upside=0,
            downside=0,
            verdict="无法估值",
            confidence="低",
            notes="股息预测为空或必要收益率<=终端增长率"
        )

    pv_sum = 0.0
    for i, div in enumerate(dividend_forecast):
        discount_factor = (1 + required_return) ** (i + 1)
        pv_sum += div / discount_factor

    # Gordon增长模型计算永续价值
    last_div = dividend_forecast[-1] if dividend_forecast else 0
    terminal_value = last_div * (1 + terminal_growth) / (required_return - terminal_growth)
    n = len(dividend_forecast)
    pv_terminal = terminal_value / (1 + required_return) ** n

    equity_value = pv_sum + pv_terminal

    if shares_outstanding > 0:
        intrinsic_value = equity_value / shares_outstanding
    else:
        intrinsic_value = 0

    return ValuationResult(
        method="DDM",
        intrinsic_value=round(intrinsic_value, 2),
        current_price=0,
        upside=0,
        downside=0,
        verdict="需要当前价格",
        confidence="中",
        details={
            "required_return": required_return,
            "terminal_growth": terminal_growth,
            "pv_sum": round(pv_sum, 2),
            "pv_terminal": round(pv_terminal, 2),
            "dividend_forecast": dividend_forecast
        },
        notes=f"必要收益率={required_return*100:.1f}%, 永续增长率={terminal_growth*100:.1f}%"
    )


def peg_valuation(eps_growth_rate: float,
                  pe_ttm: float,
                  shares_outstanding: float = 1.0,
                  current_price: float = 0.0) -> ValuationResult:
    """PEG估值

    PEG = PE / Growth Rate
    PEG < 1 表示可能被低估

    Args:
        eps_growth_rate: EPS增长率 (如0.20表示20%)
        pe_ttm: 市盈率(TTM)
        shares_outstanding: 流通股数(亿股)
        current_price: 当前股价

    Returns:
        ValuationResult: PEG估值结果
    """
    if eps_growth_rate <= 0 or pe_ttm <= 0:
        return ValuationResult(
            method="PEG",
            intrinsic_value=0,
            current_price=current_price,
            upside=0,
            downside=0,
            verdict="无法估值",
            confidence="低",
            notes="增长率或PE为负数"
        )

    peg = pe_ttm / (eps_growth_rate * 100)  # 转为倍数

    # 合理PE = 增长率 * 100 * 1.5 (经验值)
    fair_pe = eps_growth_rate * 100 * 1.5
    intrinsic_value = fair_pe * (pe_ttm / pe_ttm) if current_price > 0 else fair_pe

    if current_price > 0 and pe_ttm > 0:
        intrinsic_value = fair_pe * (current_price / pe_ttm)

    upside, downside = _calc_upside_downside(intrinsic_value, current_price)
    verdict = _verdict_from_upside(upside)

    return ValuationResult(
        method="PEG",
        intrinsic_value=round(intrinsic_value, 2),
        current_price=current_price,
        upside=upside,
        downside=downside,
        verdict=verdict,
        confidence="中",
        details={
            "peg": round(peg, 2),
            "fair_pe": round(fair_pe, 1),
            "eps_growth_rate": eps_growth_rate * 100,
            "pe_ttm": pe_ttm
        },
        notes=f"PEG={peg:.2f}, 合理PE={fair_pe:.1f}x" + ("(低估)" if peg < 1 else "(高估)" if peg > 2 else "(合理)")
    )


def lbo_valuation(entry_ebitda: float,
                 entry_multiple: float = 8.0,
                 exit_multiple: float = 10.0,
                 debt_ratio: float = 0.6,
                 interest_rate: float = 0.05,
                 years: int = 5,
                 tax_rate: float = 0.25,
                 shares_outstanding: float = 1.0) -> ValuationResult:
    """LBO杠杆收购估值

    估算在杠杆收购情景下的估值

    Args:
        entry_ebitda: 入门年份EBITDA
        entry_multiple: 入门EV/EBITDA倍数 (默认8倍)
        exit_multiple: 退出EV/EBITDA倍数 (默认10倍)
        debt_ratio: 债务比例 (默认60%)
        interest_rate: 贷款利率 (默认5%)
        years: 持有年数 (默认5年)
        tax_rate: 税率 (默认25%)
        shares_outstanding: 流通股数(亿股)

    Returns:
        ValuationResult: LBO估值结果
    """
    if entry_ebitda <= 0:
        return ValuationResult(
            method="LBO",
            intrinsic_value=0,
            current_price=0,
            upside=0,
            downside=0,
            verdict="无法估值",
            confidence="低",
            notes="EBITDA必须为正数"
        )

    # 入门企业价值
    entry_ev = entry_ebitda * entry_multiple

    # 债务和股权分配
    entry_debt = entry_ev * debt_ratio
    entry_equity = entry_ev * (1 - debt_ratio)

    # 模拟还款过程
    debt_balance = entry_debt
    for year in range(years):
        interest_expense = debt_balance * interest_rate
        ebit = entry_ebitda  # 简化假设EBITDA不变
        ebt = ebit - interest_expense
        tax = max(0, ebt * tax_rate)
        net_income = ebt - tax
        # 简化: 用净利润偿还债务
        debt_repayment = min(debt_balance, max(0, net_income))
        debt_balance -= debt_repayment

    # 退出时的企业价值
    exit_ev = entry_ebitda * exit_multiple  # 简化假设EBITDA不变

    # 退出时债务
    exit_debt = debt_balance

    # 退出时股权价值
    exit_equity = max(0, exit_ev - exit_debt)

    # IRR计算
    if entry_equity > 0 and exit_equity > 0:
        irr = (exit_equity / entry_equity) ** (1 / years) - 1
    else:
        irr = 0

    # 每股价值
    if shares_outstanding > 0:
        intrinsic_value = exit_equity / shares_outstanding
    else:
        intrinsic_value = 0

    return ValuationResult(
        method="LBO",
        intrinsic_value=round(intrinsic_value, 2),
        current_price=0,
        upside=0,
        downside=0,
        verdict="并购估值参考",
        confidence="中",
        details={
            "entry_ev": round(entry_ev, 2),
            "exit_ev": round(exit_ev, 2),
            "entry_equity": round(entry_equity, 2),
            "exit_equity": round(exit_equity, 2),
            "irr": round(irr * 100, 1),
            "debt_ratio": debt_ratio * 100,
            "years": years
        },
        notes=f"Entry EV={entry_ev:.1f}, Exit EV={exit_ev:.1f}, IRR={irr*100:.1f}%"
    )


def industry_pe_compare(pe_ttm: float,
                       industry_pe: float,
                       current_price: float = 0.0,
                       premium: float = 0.0) -> ValuationResult:
    """行业PE比较估值

    Args:
        pe_ttm: 当前PE
        industry_pe: 行业平均PE
        current_price: 当前股价
        premium: 行业溢价 (如0.2表示比行业贵20%)

    Returns:
        ValuationResult: 行业比较估值结果
    """
    if pe_ttm <= 0 or industry_pe <= 0:
        return ValuationResult(
            method="行业PE比较",
            intrinsic_value=0,
            current_price=current_price,
            upside=0,
            downside=0,
            verdict="无法估值",
            confidence="低",
            notes="PE数据无效"
        )

    # 合理PE = 行业PE * (1 + 溢价)
    fair_pe = industry_pe * (1 + premium)

    if current_price > 0 and pe_ttm > 0:
        eps = current_price / pe_ttm
        intrinsic_value = eps * fair_pe
    else:
        intrinsic_value = 0

    upside, downside = _calc_upside_downside(intrinsic_value, current_price)
    verdict = _verdict_from_upside(upside)

    return ValuationResult(
        method="行业PE比较",
        intrinsic_value=round(intrinsic_value, 2),
        current_price=current_price,
        upside=upside,
        downside=downside,
        verdict=verdict,
        confidence="高",
        details={
            "pe_ttm": pe_ttm,
            "industry_pe": industry_pe,
            "fair_pe": round(fair_pe, 1),
            "premium": premium * 100
        },
        notes=f"当前PE={pe_ttm:.1f}x, 行业PE={industry_pe:.1f}x, 合理PE={fair_pe:.1f}x"
    )


def pb_roe_matrix(pb: float,
                  roe: float,
                  current_price: float = 0.0,
                  risk_free_rate: float = 0.03) -> ValuationResult:
    """PB-ROE矩阵估值

    基于PB-ROE关系判断估值高低
    合理PB ≈ ROE / RiskFreeRate (简化模型)

    Args:
        pb: 市净率
        roe: 净资产收益率 (如0.15表示15%)
        current_price: 当前股价
        risk_free_rate: 无风险利率 (默认3%)

    Returns:
        ValuationResult: PB-ROE估值结果
    """
    if pb <= 0 or roe <= 0:
        return ValuationResult(
            method="PB-ROE矩阵",
            intrinsic_value=0,
            current_price=current_price,
            upside=0,
            downside=0,
            verdict="无法估值",
            confidence="低",
            notes="PB或ROE为负数"
        )

    # 合理PB = ROE / RiskFreeRate * 100 (经验公式)
    fair_pb = (roe / risk_free_rate) * 1.0  # 简化模型，ROE15%/无风险3%=5倍PB

    if current_price > 0 and pb > 0:
        book_value_per_share = current_price / pb
        intrinsic_value = book_value_per_share * fair_pb
    else:
        intrinsic_value = 0

    upside, downside = _calc_upside_downside(intrinsic_value, current_price)
    verdict = _verdict_from_upside(upside)

    return ValuationResult(
        method="PB-ROE矩阵",
        intrinsic_value=round(intrinsic_value, 2),
        current_price=current_price,
        upside=upside,
        downside=downside,
        verdict=verdict,
        confidence="中",
        details={
            "pb": pb,
            "roe": roe * 100,
            "fair_pb": round(fair_pb, 1),
            "risk_free_rate": risk_free_rate * 100
        },
        notes=f"当前PB={pb:.2f}, ROE={roe*100:.1f}%, 合理PB={fair_pb:.1f}"
    )


def get_intrinsic_value(code: str,
                        current_price: float,
                        pe_ttm: float,
                        eps_ttm: float,
                        eps_growth_rate: float,
                        roe: float,
                        pb: float,
                        industry_pe: float,
                        dividend_yield: float = 0.0,
                        shares_outstanding: float = 1.0,
                        fcf_forecast: List[float] = None) -> Dict[str, Any]:
    """综合内在价值评估

    综合多种估值方法给出最终判断

    Args:
        code: 股票代码
        current_price: 当前股价
        pe_ttm: 市盈率(TTM)
        eps_ttm: EPS(TTM)
        eps_growth_rate: EPS增长率 (如0.20表示20%)
        roe: 净资产收益率 (如0.15表示15%)
        pb: 市净率
        industry_pe: 行业平均PE
        dividend_yield: 股息率 (如0.03表示3%)
        shares_outstanding: 流通股数(亿股)
        fcf_forecast: 自由现金流预测 [year1, year2, year3, ...] (可选)

    Returns:
        dict: 综合估值结果 {
            "verdict": str,  # 综合判断
            "upside_avg": float,  # 平均上涨空间
            "methods": [ValuationResult],  # 各方法结果
            "dominant_verdict": str,  # 多数方法判断
            "confidence": str  # 置信度
        }
    """
    methods = []

    # PEG估值
    if pe_ttm > 0 and eps_growth_rate > 0:
        peg_result = peg_valuation(eps_growth_rate, pe_ttm, shares_outstanding, current_price)
        peg_result.intrinsic_value = current_price * (peg_result.details.get("fair_pe", pe_ttm) / pe_ttm) if current_price > 0 else 0
        if current_price > 0:
            peg_result.upside, peg_result.downside = _calc_upside_downside(peg_result.intrinsic_value, current_price)
            peg_result.verdict = _verdict_from_upside(peg_result.upside)
        methods.append(peg_result)

    # PB-ROE估值
    if pb > 0 and roe > 0:
        pb_result = pb_roe_matrix(pb, roe, current_price)
        methods.append(pb_result)

    # 行业PE比较
    if pe_ttm > 0 and industry_pe > 0:
        ind_result = industry_pe_compare(pe_ttm, industry_pe, current_price)
        methods.append(ind_result)

    # DCF估值
    if fcf_forecast:
        dcf_result = dcf_valuation(fcf_forecast, shares_outstanding=shares_outstanding)
        if current_price > 0:
            dcf_result.upside, dcf_result.downside = _calc_upside_downside(dcf_result.intrinsic_value, current_price)
        methods.append(dcf_result)

    # 计算平均上涨空间
    valid_upside = [m.upside for m in methods if m.upside != 0]
    upside_avg = sum(valid_upside) / len(valid_upside) if valid_upside else 0

    # 多数投票
    verdicts = [m.verdict for m in methods if m.verdict not in ("无法估值", "需要当前价格")]
    if verdicts:
        from collections import Counter
        vote = Counter(verdicts).most_common(1)[0][0]
    else:
        vote = "数据不足"

    # 置信度
    confidence_count = sum(1 for m in methods if m.confidence == "高")
    if confidence_count >= 3:
        confidence = "高"
    elif confidence_count >= 1:
        confidence = "中"
    else:
        confidence = "低"

    return {
        "verdict": _verdict_from_upside(upside_avg),
        "upside_avg": round(upside_avg, 1),
        "methods": methods,
        "dominant_verdict": vote,
        "confidence": confidence,
        "method_count": len(methods)
    }


def format_valuation_report(valuations: List[ValuationResult], code: str = "") -> str:
    """格式化估值报告"""
    lines = []
    lines.append("=" * 50)
    lines.append(f"【机构估值报告】{code}")
    lines.append("=" * 50)

    for v in valuations:
        lines.append(f"\n📊 {v.method}")
        lines.append("-" * 40)
        if v.current_price > 0:
            lines.append(f"  当前价格: {v.current_price:.2f}")
            lines.append(f"  内在价值: {v.intrinsic_value:.2f}")
            lines.append(f"  上涨空间: {v.upside:+.1f}%")
            lines.append(f"  下跌风险: {v.downside:.1f}%")
        else:
            lines.append(f"  内在价值: {v.intrinsic_value:.2f} (需要当前价格)")

        verdict_emoji = "🟢" if v.verdict in ("低估", "偏低") else ("🔴" if v.verdict in ("高估", "偏高") else "🟡")
        lines.append(f"  估值判断: {verdict_emoji} {v.verdict} (置信度:{v.confidence})")

        if v.details:
            detail_lines = []
            for k, val in v.details.items():
                if isinstance(val, float):
                    detail_lines.append(f"{k}={val:.2f}")
                else:
                    detail_lines.append(f"{k}={val}")
            lines.append(f"  详情: {', '.join(detail_lines[:3])}")

        if v.notes:
            lines.append(f"  备注: {v.notes}")

    lines.append("")
    return "\n".join(lines)


# 测试
if __name__ == "__main__":
    print("=== 估值方法测试 ===\n")

    # 测试PEG估值
    peg = peg_valuation(eps_growth_rate=0.20, pe_ttm=30, current_price=30)
    print(f"PEG估值: 内在价值={peg.intrinsic_value}, 判断={peg.verdict}")

    # 测试PB-ROE
    pb_roe = pb_roe_matrix(pb=3.0, roe=0.15, current_price=45)
    print(f"PB-ROE: 内在价值={pb_roe.intrinsic_value}, 判断={pb_roe.verdict}")

    # 综合估值
    result = get_intrinsic_value(
        code="600519",
        current_price=1800,
        pe_ttm=35,
        eps_ttm=51.4,
        eps_growth_rate=0.15,
        roe=0.25,
        pb=12.0,
        industry_pe=30,
        dividend_yield=0.015,
        shares_outstanding=12.56
    )
    print(f"\n综合估值: {result['verdict']}, 上涨空间:{result['upside_avg']}%, 置信度:{result['confidence']}")
    print(f"各方法判断: {result['dominant_verdict']}")

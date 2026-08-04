# -*- coding: utf-8 -*-
"""sc_risk.py — 风险扫描引擎（V16.1 从 get_ful_report.py layer_risk 迁移）

9 项风险清单：资产负债率/商誉/应收账款/存货/现金短债/解禁/减持/质押/盈利质量。
纯计算逻辑 + 可选数据回调（解禁/减持/质押数据由调用方传入），供 med/lng 复用。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def scan_financial_risk(fin: Dict[str, Any]) -> List[Dict[str, Any]]:
    """资产负债健康风险项（基于财务比率）。

    Args:
        fin: {debt_ratio, gw_ratio, ar_ratio, inv_ratio, cash_debt_ratio,
              roe, profit_yoy}（百分比数值）

    Returns:
        items: [{name, level, score, text}, ...]
    """
    items: List[Dict[str, Any]] = []
    total = 0

    # 1) 资产负债健康
    dr = fin.get("debt_ratio", 0)
    if dr > 75:
        items.append(
            {"name": "资产负债率", "level": "高", "score": 15, "text": f"{dr:.1f}%，杠杆过高"}
        )
        total += 15
    elif dr > 55:
        items.append(
            {"name": "资产负债率", "level": "中", "score": 8, "text": f"{dr:.1f}%，中等杠杆"}
        )
        total += 8
    else:
        items.append({"name": "资产负债率", "level": "低", "score": 2, "text": f"{dr:.1f}%，稳健"})

    # 2) 商誉/净资产
    gw = fin.get("gw_ratio", 0)
    if gw > 30:
        items.append(
            {
                "name": "商誉风险",
                "level": "高",
                "score": 12,
                "text": f"商誉占净资产 {gw:.1f}%，减值风险高",
            }
        )
        total += 12
    elif gw > 15:
        items.append(
            {
                "name": "商誉风险",
                "level": "中",
                "score": 6,
                "text": f"商誉占净资产 {gw:.1f}%，需关注",
            }
        )
        total += 6
    else:
        items.append(
            {"name": "商誉风险", "level": "低", "score": 1, "text": f"商誉 {gw:.1f}%，风险低"}
        )

    # 3) 应收账款
    ar = fin.get("ar_ratio", 0)
    if ar > 25:
        items.append(
            {
                "name": "应收账款",
                "level": "高",
                "score": 10,
                "text": f"应收账款/总资产 {ar:.1f}%，回款风险高",
            }
        )
        total += 10
    elif ar > 15:
        items.append(
            {
                "name": "应收账款",
                "level": "中",
                "score": 5,
                "text": f"应收账款/总资产 {ar:.1f}%，需关注",
            }
        )
        total += 5
    else:
        items.append(
            {"name": "应收账款", "level": "低", "score": 1, "text": f"应收账款占比 {ar:.1f}%，健康"}
        )

    # 4) 存货
    inv = fin.get("inv_ratio", 0)
    if inv > 30:
        items.append(
            {
                "name": "存货风险",
                "level": "高",
                "score": 8,
                "text": f"存货/总资产 {inv:.1f}%，库存积压风险",
            }
        )
        total += 8
    elif inv > 20:
        items.append(
            {
                "name": "存货风险",
                "level": "中",
                "score": 4,
                "text": f"存货/总资产 {inv:.1f}%，需关注",
            }
        )
        total += 4
    else:
        items.append(
            {"name": "存货风险", "level": "低", "score": 1, "text": f"存货占比 {inv:.1f}%，正常"}
        )

    # 5) 现金短债
    cdr = fin.get("cash_debt_ratio", 0)
    if fin.get("has_short_loan") and cdr < 0.5:
        items.append(
            {
                "name": "短期偿债",
                "level": "高",
                "score": 10,
                "text": f"现金/短债 {cdr:.2f}，短期偿债承压",
            }
        )
        total += 10
    elif fin.get("has_short_loan") and cdr < 1.0:
        items.append(
            {"name": "短期偿债", "level": "中", "score": 5, "text": f"现金/短债 {cdr:.2f}，需关注"}
        )
        total += 5
    else:
        items.append({"name": "短期偿债", "level": "低", "score": 1, "text": "现金覆盖短债充足"})

    # 6) 盈利质量（ROE/利润增速）
    roe = fin.get("roe", 0)
    profit_yoy = fin.get("profit_yoy", 0)
    if roe < 3:
        items.append(
            {
                "name": "盈利质量",
                "level": "高",
                "score": 10,
                "text": f"ROE {roe:.1f}%，盈利能力偏弱",
            }
        )
        total += 10
    elif roe >= 15:
        items.append(
            {"name": "盈利质量", "level": "低", "score": 0, "text": f"ROE {roe:.1f}%，优质"}
        )
    else:
        items.append(
            {"name": "盈利质量", "level": "低", "score": 2, "text": f"ROE {roe:.1f}%，一般"}
        )

    if profit_yoy < -20:
        items.append(
            {
                "name": "业绩趋势",
                "level": "高",
                "score": 12,
                "text": f"利润同比 {profit_yoy:.1f}%，业绩下滑",
            }
        )
        total += 12
    elif profit_yoy > 10:
        items.append(
            {
                "name": "业绩趋势",
                "level": "低",
                "score": 0,
                "text": f"利润同比 +{profit_yoy:.1f}%，成长",
            }
        )
    elif profit_yoy < 0:
        items.append(
            {
                "name": "业绩趋势",
                "level": "中",
                "score": 6,
                "text": f"利润同比 {profit_yoy:.1f}%，业绩承压",
            }
        )
        total += 6

    return items


def scan_event_risk(
    lockup: Optional[Dict[str, Any]] = None,
    announcement_titles: Optional[List[str]] = None,
    pledge_hits: int = 0,
) -> List[Dict[str, Any]]:
    """事件类风险项（解禁/减持/质押）。

    Args:
        lockup: {date, ratio} 未来最近解禁（ratio 为 %）
        announcement_titles: 近 N 日公告标题列表
        pledge_hits: 质押相关资讯命中条数

    Returns:
        items: [{name, level, score, text}, ...]
    """
    items: List[Dict[str, Any]] = []
    total = 0

    # 7) 解禁压力
    if lockup:
        ratio = lockup.get("ratio", 0)
        if ratio > 10:
            items.append(
                {
                    "name": "限售解禁",
                    "level": "高",
                    "score": 12,
                    "text": f"{lockup.get('date','')} 解禁 {ratio:.1f}%",
                }
            )
            total += 12
        elif ratio > 3:
            items.append(
                {
                    "name": "限售解禁",
                    "level": "中",
                    "score": 6,
                    "text": f"{lockup.get('date','')} 解禁 {ratio:.1f}%",
                }
            )
            total += 6
        else:
            items.append(
                {
                    "name": "限售解禁",
                    "level": "低",
                    "score": 1,
                    "text": f"{lockup.get('date','')} 解禁 {ratio:.1f}%，影响有限",
                }
            )
    else:
        items.append({"name": "限售解禁", "level": "低", "score": 0, "text": "未来无重大解禁"})

    # 8) 股东减持（公告关键词）
    if announcement_titles:
        titles = " ".join(str(t) for t in announcement_titles)
        if "董事" in titles and "减持" in titles:
            items.append(
                {
                    "name": "股东减持",
                    "level": "高",
                    "score": 12,
                    "text": "董事/高管有减持公告，需重点关注",
                }
            )
            total += 12
        elif "减持" in titles:
            items.append({"name": "股东减持", "level": "中", "score": 6, "text": "有股东减持公告"})
            total += 6
        elif "增持" in titles:
            items.append({"name": "股东增持", "level": "低", "score": 0, "text": "有股东增持公告"})
        else:
            items.append(
                {"name": "股东增减持", "level": "低", "score": 1, "text": "近90日无增减持公告"}
            )
    else:
        items.append({"name": "股东增减持", "level": "低", "score": 1, "text": "近90日无相关公告"})

    # 9) 股权质押（资讯命中）
    if pledge_hits >= 2:
        items.append(
            {
                "name": "股权质押",
                "level": "中",
                "score": 8,
                "text": f"质押相关资讯 {pledge_hits} 条，需关注",
            }
        )
        total += 8
    elif pledge_hits == 1:
        items.append({"name": "股权质押", "level": "低", "score": 3, "text": "有质押相关资讯 1 条"})
    else:
        items.append(
            {"name": "股权质押", "level": "低", "score": 1, "text": "近期无明显质押相关资讯"}
        )

    return items


def combine_risk(
    fin_items: List[Dict[str, Any]], event_items: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """合并财务+事件风险项，输出综合风险评分（0~100，越高风险越高）。"""
    items = list(fin_items) + list(event_items)
    base = 30  # 默认基准分
    risk_score = base
    for it in items:
        risk_score += it.get("score", 0)
    risk_score = min(100, max(0, risk_score))

    signals = []
    if risk_score >= 70:
        signals.append(f"⚠️ 综合风险评分 {risk_score}/100，多项风险叠加，建议谨慎")
    elif risk_score >= 40:
        signals.append(f"综合风险评分 {risk_score}/100，中等风险，需关注相关风险项")
    else:
        signals.append(f"综合风险评分 {risk_score}/100，风险可控")

    return {"ok": True, "items": items, "risk_score": risk_score, "signals": signals}

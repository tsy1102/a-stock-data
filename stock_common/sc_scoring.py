#!/usr/bin/env python3
"""sc_scoring.py — 评分系统 / 多评委评审团 (V9.0 模块化重构)

从原 stock_common.py 提取的统一评分系统：
  - ScoreData / ScoreResult 数据结构
  - 六维度评分函数 (_score_technical / fundamental / valuation / flow / holder / dividend)
  - 统一评分接口 calculate_score (sht/med/lng/ful)
  - 多评委评审团系统 (calculate_multi_school_scores)
  - 多评委报告格式化 (format_multi_school_report)

依赖关系：
  - 无外部子模块依赖（纯计算逻辑）
  - 仅使用 dataclasses, typing 标准库
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# ═══════════════════════════════════════
# 导出接口
# ═══════════════════════════════════════
__all__ = [
    'ScoreData', 'ScoreResult',
    '_score_technical', '_score_fundamental', '_score_valuation',
    '_score_flow', '_score_holder', '_score_dividend',
    'calculate_score', 'calculate_score_by_school',
    'calculate_multi_school_scores', 'format_multi_school_report',
    'SCHOOL_CONFIGS',
]


# ═══════════════════════════════════════════════════════════
# V8.2: 统一评分接口 - 数据结构
# ═══════════════════════════════════════════════════════════

@dataclass
class ScoreData:
    """评分输入数据结构"""
    # 基本信息
    code: str = ""
    name: str = ""
    price: float = 0.0
    change_pct: float = 0.0

    # 技术面数据
    ma5: float = 0.0
    ma10: float = 0.0
    ma20: float = 0.0
    macd_dif: float = 0.0
    macd_dea: float = 0.0
    rsi14: float = 50.0
    kdj_k: float = 50.0
    kdj_d: float = 50.0
    kdj_j: float = 50.0
    boll_pos: float = 50.0
    volume_ratio: float = 1.0
    ret_20d: float = 0.0
    high_120d: float = 0.0
    is_limit_up: bool = False

    # 基本面数据
    roe: float = 0.0
    gross_margin: float = 0.0
    net_profit_margin: float = 0.0
    debt_ratio: float = 0.0
    asset_liability_ratio: float = 0.0
    ocf_ratio: float = 0.0  # 经营现金流/净利润

    # 估值数据
    pe_ttm: float = 0.0
    pb: float = 0.0
    forward_pe: float = 0.0
    industry_pe: float = 0.0
    drawdown_from_high: float = 0.0

    # 资金面数据
    main_net_inflow: float = 0.0
    consecutive_inflow_days: int = 0
    northbound_change: float = 0.0
    institution_net_buy: float = 0.0
    margin_short_decline: bool = False

    # 筹码数据
    holder_change_ratio: float = 0.0
    holder_consecutive_decrease: bool = False
    institution_holding_pct: float = 0.0

    # 分红数据
    dividend_yield: float = 0.0
    consecutive_dividend_years: int = 0


@dataclass
class ScoreResult:
    """评分结果数据结构"""
    total_score: float = 0.0
    dimensions: Dict[str, float] = field(default_factory=dict)
    details: List[str] = field(default_factory=list)
    report_source: str = ""


# ═══════════════════════════════════════════════════════════
# V8.2: 六维度评分函数
# ═══════════════════════════════════════════════════════════

def _score_technical(data: ScoreData, cfg: Optional[Dict] = None) -> tuple:
    """技术面评分（0-100基准，加减分）"""
    score = 50.0
    details = []
    tc = cfg or {}

    # 均线系统
    if data.ma5 > 0 and data.ma10 > 0 and data.ma20 > 0:
        if data.ma5 > data.ma10 > data.ma20:
            score += tc.get("ma_golden_cross", 10)
            details.append("均线多头排列")
        elif data.ma5 < data.ma10 < data.ma20:
            score += tc.get("ma_death_cross", -10)
        else:
            score += 3

    # 涨跌幅
    if data.change_pct > 0:
        add_score = min(int(data.change_pct * 0.5), 15)
        score += add_score
        details.append(f"涨跌+{data.change_pct:.1f}%")
    elif data.change_pct < -3:
        score += max(int(data.change_pct * 0.5), -10)
        details.append(f"涨跌{data.change_pct:.1f}%")

    # 涨停封板
    if data.is_limit_up:
        score += tc.get("limit_up", 15)
        details.append("涨停封板")

    # MACD
    if data.macd_dif > data.macd_dea > 0:
        score += tc.get("macd_bull", 8)
        details.append("MACD金叉")
    elif data.macd_dif < data.macd_dea < 0:
        score += tc.get("macd_bear", -8)

    # RSI
    if 40 <= data.rsi14 <= 70:
        score += tc.get("rsi_optimal", 5)
    elif data.rsi14 < 30:
        score += tc.get("rsi_oversold", 3)
        details.append("RSI超卖")
    elif data.rsi14 > 80:
        score += tc.get("rsi_overbought", -4)

    # KDJ
    if data.kdj_k > data.kdj_d and data.kdj_k < 80:
        score += tc.get("kdj_golden", 3)
    elif data.kdj_j > 110:
        score += tc.get("kdj_overbought", -3)

    # 20日涨跌幅
    if data.ret_20d < -30:
        score += tc.get("ret_20d_drop", -6)
    elif data.ret_20d > 15:
        score += tc.get("ret_20d_rally", 5)

    # 距高点回撤
    if data.high_120d > 0 and data.price > 0:
        ratio = (data.price / data.high_120d - 1) * 100
        if ratio < -30:
            score += tc.get("depth_pullback", 4)
            details.append(f"距高点回撤{abs(ratio):.0f}%")

    return max(0, min(100, score)), details


def _score_fundamental(data: ScoreData, cfg: Optional[Dict] = None) -> tuple:
    """基本面评分（0-100基准，加减分）"""
    score = 50.0
    details = []
    fc = cfg or {}

    # ROE
    if data.roe >= 20:
        score += fc.get("roe_excellent", 25)
        details.append(f"ROE={data.roe:.1f}%优秀")
    elif data.roe >= 15:
        score += fc.get("roe_good", 15)
        details.append(f"ROE={data.roe:.1f}%良好")
    elif data.roe >= 10:
        score += fc.get("roe_medium", 8)
        details.append(f"ROE={data.roe:.1f}%中等")
    elif data.roe < 0:
        # 亏损股：强制评分下限为20分
        details.append(f"⚠️ ROE={data.roe:.1f}%亏损，基本面严重恶化")
        score = min(score, 20.0)  # 强制下限20分

    # 毛利率
    if data.gross_margin >= 40:
        score += fc.get("gross_margin_high", 10)
        details.append(f"毛利率{data.gross_margin:.1f}%")

    # 净利率
    if data.net_profit_margin >= 15:
        score += fc.get("net_margin_high", 10)
        details.append(f"净利率{data.net_profit_margin:.1f}%")

    # 资产负债率（越低越好）
    if data.asset_liability_ratio > 0:
        equity_ratio = 1 - data.asset_liability_ratio
        if equity_ratio > 0.6:
            score += fc.get("low_debt", 15)
            details.append("资产负债率低")

    # 现金流
    if data.ocf_ratio >= 0.8:
        score += fc.get("cash_flow_good", 10)
        details.append("现金流充裕")

    return max(0, min(100, score)), details


def _score_valuation(data: ScoreData, cfg: Optional[Dict] = None) -> tuple:
    """估值面评分（0-100基准，加减分）"""
    score = 50.0
    details = []
    vc = cfg or {}

    # PE相对行业
    if data.pe_ttm > 0 and data.industry_pe > 0:
        if data.pe_ttm < data.industry_pe:
            score += vc.get("pe_below_industry", 15)
            details.append("PE低于行业均值")

    # 前向PE
    if data.forward_pe > 0:
        if data.forward_pe < 15:
            score += vc.get("forward_pe_low", 20)
            details.append(f"前向PE={data.forward_pe:.1f}x低估")
        elif data.forward_pe < 25:
            score += vc.get("forward_pe_medium", 10)
            details.append(f"前向PE={data.forward_pe:.1f}x合理")

    # PB
    if data.pb > 0 and data.pb < 2:
        score += vc.get("pb_low", 5)

    # 回撤幅度（长线视角）
    if data.drawdown_from_high <= -40:
        score += vc.get("golden_drawdown", 15)
        details.append(f"距高点回撤{abs(data.drawdown_from_high):.0f}%（黄金坑）")
    elif data.drawdown_from_high <= -20:
        score += vc.get("normal_drawdown", 8)
        details.append(f"距高点回撤{abs(data.drawdown_from_high):.0f}%")

    return max(0, min(100, score)), details


def _score_flow(data: ScoreData, cfg: Optional[Dict] = None) -> tuple:
    """资金面评分（0-100基准，加减分）"""
    score = 50.0
    details = []
    flc = cfg or {}

    # 主力净流入
    if data.main_net_inflow > 0:
        score += flc.get("main_inflow", 10)
        details.append(f"主力净流入{data.main_net_inflow/1e8:.1f}亿")

    # 连续流入天数
    if data.consecutive_inflow_days >= 12:
        score += flc.get("consecutive_inflow", 10)
        details.append(f"连续{data.consecutive_inflow_days}日流入")

    # 北向增持
    if data.northbound_change > 0:
        score += flc.get("northbound_increase", 8)
        details.append("北向增持")

    # 机构净买入
    if data.institution_net_buy > 0:
        score += flc.get("institution_buy", 10)
        details.append("机构净买入")

    # 融券下降
    if data.margin_short_decline:
        score += flc.get("margin_decline", 5)
        details.append("融券持续下降")

    return max(0, min(100, score)), details


def _score_holder(data: ScoreData, cfg: Optional[Dict] = None) -> tuple:
    """筹码面评分（0-100基准，加减分）"""
    score = 50.0
    details = []
    hc = cfg or {}

    # 筹码集中
    if data.holder_change_ratio < 0:
        if data.holder_consecutive_decrease:
            score += hc.get("holder_concentrate", 15)
            details.append("筹码持续集中")
        else:
            score += hc.get("holder_trend", 8)
            details.append("筹码趋于集中")

    # 机构持仓
    if data.institution_holding_pct > 0:
        score += hc.get("institution_hold", 10)
        details.append(f"机构持仓{data.institution_holding_pct:.1f}%")

    return max(0, min(100, score)), details


def _score_dividend(data: ScoreData, cfg: Optional[Dict] = None) -> tuple:
    """分红面评分（0-100基准，加减分）"""
    score = 50.0
    details = []
    dc = cfg or {}

    # 股息率
    if data.dividend_yield >= 3:
        score += dc.get("dividend_high", 10)
        details.append(f"股息率{data.dividend_yield:.1f}%")

    # 持续分红
    if data.consecutive_dividend_years >= 5:
        score += dc.get("dividend_continuous", 5)
        details.append("持续分红5年+")

    return max(0, min(100, score)), details


# ═══════════════════════════════════════════════════════════
# V8.2: 统一评分接口
# ═══════════════════════════════════════════════════════════

def calculate_score(score_type: str, data: ScoreData, cfg: Optional[Dict] = None) -> ScoreResult:
    """
    统一评分接口

    Args:
        score_type: 评分类型 "sht"/"med"/"lng"/"ful"
        data: ScoreData 输入数据
        cfg: 评分配置（可选）

    Returns:
        ScoreResult 评分结果
    """
    result = ScoreResult(report_source=score_type)
    sc = cfg or {}

    # 计算各维度评分
    tech_score, tech_details = _score_technical(data, sc.get("technical", {}))
    fund_score, fund_details = _score_fundamental(data, sc.get("fundamental", {}))
    val_score, val_details = _score_valuation(data, sc.get("valuation", {}))
    flow_score, flow_details = _score_flow(data, sc.get("flow", {}))
    holder_score, holder_details = _score_holder(data, sc.get("holder", {}))
    div_score, div_details = _score_dividend(data, sc.get("dividend", {}))

    result.dimensions = {
        "technical": tech_score,
        "fundamental": fund_score,
        "valuation": val_score,
        "flow": flow_score,
        "holder": holder_score,
        "dividend": div_score
    }

    # 根据评分类型组合
    if score_type == "sht":
        # 短线：技术面 + 资金面 + 筹码面
        result.total_score = (
            tech_score * 0.4 +
            flow_score * 0.35 +
            holder_score * 0.25
        )
        result.details = tech_details + flow_details + holder_details

    elif score_type == "med":
        # 中线：基本面 + 估值面 + 资金面 + 筹码面
        result.total_score = (
            fund_score * 0.35 +
            val_score * 0.25 +
            flow_score * 0.2 +
            holder_score * 0.2
        )
        result.details = fund_details + val_details + flow_details + holder_details

    elif score_type == "lng":
        # 长线：基本面 + 估值面 + 分红面 + 筹码面
        result.total_score = (
            fund_score * 0.3 +
            val_score * 0.3 +
            div_score * 0.2 +
            holder_score * 0.2
        )
        result.details = fund_details + val_details + div_details + holder_details

    elif score_type == "ful":
        # 完整：五维综合
        # 注意：配置文件中权重为百分比形式（如25），需除以100转为小数
        _cfg_weights = sc.get("weights", {}) if sc else {}
        weights = {
            "technical": (_cfg_weights.get("technical", 25) / 100),
            "valuation": (_cfg_weights.get("valuation", 20) / 100),
            "fundamental": (_cfg_weights.get("fundamental", 20) / 100),
            "flow": (_cfg_weights.get("flow", 15) / 100),
            "holder": (_cfg_weights.get("holder", 10) / 100),
            "dividend": (_cfg_weights.get("dividend", 10) / 100),
        }
        result.total_score = (
            tech_score * weights.get("technical", 0.25) +
            val_score * weights.get("valuation", 0.20) +
            fund_score * weights.get("fundamental", 0.20) +
            flow_score * weights.get("flow", 0.15) +
            holder_score * weights.get("holder", 0.10) +
            div_score * weights.get("dividend", 0.10)
        )
        result.details = tech_details + fund_details + val_details + flow_details + holder_details + div_details

    else:
        result.total_score = 50.0

    return result


# ═══════════════════════════════════════════════════════════
# V8.5: 多评委评审团评分接口
# ═══════════════════════════════════════════════════════════

# 评委派别定义
SCHOOL_CONFIGS = {
    "value": {
        "name": "价值派",
        "persona": "巴菲特式价值投资者",
        "weights": {
            "fundamental": 0.40,
            "valuation": 0.30,
            "dividend": 0.20,
            "holder": 0.10,
            "technical": 0.00,
            "flow": 0.00,
        },
        "focus": "低估值、高ROE、稳定分红",
        "keywords": ["价值投资", "低估", "高ROE", "稳定分红", "长期持有"]
    },
    "growth": {
        "name": "成长派",
        "persona": "林奇式成长投资者",
        "weights": {
            "technical": 0.35,
            "flow": 0.30,
            "holder": 0.20,
            "fundamental": 0.15,
            "valuation": 0.00,
            "dividend": 0.00,
        },
        "focus": "技术突破、资金流入、筹码集中",
        "keywords": ["成长股", "技术突破", "资金流入", "赛道股", "高增长"]
    },
    "speculator": {
        "name": "游资派",
        "persona": "赵老哥式游资操盘手",
        "weights": {
            "technical": 0.40,
            "flow": 0.35,
            "holder": 0.25,
            "fundamental": 0.00,
            "valuation": 0.00,
            "dividend": 0.00,
        },
        "focus": "涨停板、游资席位、情绪热度",
        "keywords": ["涨停", "游资", "龙头", "情绪", "打板", "题材"]
    },
    "consensus": {
        "name": "综合派",
        "persona": "均衡型投资者",
        "weights": {
            "technical": 0.20,
            "fundamental": 0.25,
            "valuation": 0.20,
            "flow": 0.15,
            "holder": 0.10,
            "dividend": 0.10,
        },
        "focus": "五维均衡",
        "keywords": ["综合", "均衡", "全面"]
    }
}


def calculate_score_by_school(school: str, data: ScoreData, cfg: Optional[Dict] = None,
                              precomputed_dimensions: Optional[Dict[str, Tuple[float, List[str]]]] = None) -> ScoreResult:
    """按指定派别计算评分

    Args:
        school: 派别名称 ("value"/"growth"/"speculator"/"consensus")
        data: ScoreData 评分数据
        cfg: 评分配置（可选）
        precomputed_dimensions: 预计算的维度评分（可选），用于避免重复计算

    Returns:
        ScoreResult 评分结果
    """
    school_cfg = SCHOOL_CONFIGS.get(school, SCHOOL_CONFIGS["consensus"])
    weights = school_cfg["weights"]

    result = ScoreResult(report_source=f"{school}_{school_cfg['name']}")
    sc = cfg or {}

    # 使用预计算的维度评分或重新计算
    if precomputed_dimensions:
        tech_score, tech_details = precomputed_dimensions.get("technical", (0, []))
        fund_score, fund_details = precomputed_dimensions.get("fundamental", (0, []))
        val_score, val_details = precomputed_dimensions.get("valuation", (0, []))
        flow_score, flow_details = precomputed_dimensions.get("flow", (0, []))
        holder_score, holder_details = precomputed_dimensions.get("holder", (0, []))
        div_score, div_details = precomputed_dimensions.get("dividend", (0, []))
    else:
        # 计算各维度评分
        tech_score, tech_details = _score_technical(data, sc.get("technical", {}))
        fund_score, fund_details = _score_fundamental(data, sc.get("fundamental", {}))
        val_score, val_details = _score_valuation(data, sc.get("valuation", {}))
        flow_score, flow_details = _score_flow(data, sc.get("flow", {}))
        holder_score, holder_details = _score_holder(data, sc.get("holder", {}))
        div_score, div_details = _score_dividend(data, sc.get("dividend", {}))

    result.dimensions = {
        "technical": tech_score,
        "fundamental": fund_score,
        "valuation": val_score,
        "flow": flow_score,
        "holder": holder_score,
        "dividend": div_score
    }

    # 计算加权总分
    result.total_score = (
        tech_score * weights.get("technical", 0) +
        fund_score * weights.get("fundamental", 0) +
        val_score * weights.get("valuation", 0) +
        flow_score * weights.get("flow", 0) +
        holder_score * weights.get("holder", 0) +
        div_score * weights.get("dividend", 0)
    )

    # 收集有意义的细节
    all_details = []
    if weights.get("technical", 0) > 0:
        all_details.extend(tech_details)
    if weights.get("fundamental", 0) > 0:
        all_details.extend(fund_details)
    if weights.get("valuation", 0) > 0:
        all_details.extend(val_details)
    if weights.get("flow", 0) > 0:
        all_details.extend(flow_details)
    if weights.get("holder", 0) > 0:
        all_details.extend(holder_details)
    if weights.get("dividend", 0) > 0:
        all_details.extend(div_details)

    result.details = all_details[:10]  # 最多保留10条
    return result


def calculate_multi_school_scores(data: ScoreData, cfg: Optional[Dict] = None) -> Dict[str, Any]:
    """计算多派别评分（多评委评审团）

    Args:
        data: ScoreData 评分数据
        cfg: 评分配置（可选）

    Returns:
        dict: {
            "value": ScoreResult,    # 价值派评分
            "growth": ScoreResult,  # 成长派评分
            "speculator": ScoreResult,  # 游资派评分
            "consensus": ScoreResult,  # 综合派评分
            "consensus_score": float,  # 三派均值（不含综合派）
            "dispersion": float,  # 派别分歧度（标准差）
            "dominant_school": str,  # 主导派别
            "school_labels": dict  # 各派别标签信息
        }
    """
    results = {}
    scores = []
    sc = cfg or {}

    # 预计算所有维度评分（只计算一次，各派别共享）
    precomputed_dimensions = {
        "technical": _score_technical(data, sc.get("technical", {})),
        "fundamental": _score_fundamental(data, sc.get("fundamental", {})),
        "valuation": _score_valuation(data, sc.get("valuation", {})),
        "flow": _score_flow(data, sc.get("flow", {})),
        "holder": _score_holder(data, sc.get("holder", {})),
        "dividend": _score_dividend(data, sc.get("dividend", {})),
    }

    # 使用预计算的维度评分计算各派别评分
    for school in ["value", "growth", "speculator", "consensus"]:
        result = calculate_score_by_school(school, data, cfg, precomputed_dimensions)
        results[school] = result
        scores.append(result.total_score)

    # 计算三派均值（不含综合派）
    consensus_score = sum(scores[:3]) / 3

    # 计算分歧度（标准差）
    if len(scores) > 1:
        mean = consensus_score
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        dispersion = variance ** 0.5
    else:
        dispersion = 0

    # 确定主导派别
    dominant = max(results.items(), key=lambda x: x[1].total_score)
    dominant_school = dominant[0]

    # 派别标签
    school_labels = {
        school: {
            "name": SCHOOL_CONFIGS[school]["name"],
            "persona": SCHOOL_CONFIGS[school]["persona"],
            "focus": SCHOOL_CONFIGS[school]["focus"],
            "score": results[school].total_score,
            "dimensions": results[school].dimensions
        }
        for school in SCHOOL_CONFIGS
    }

    return {
        "value": results["value"],
        "growth": results["growth"],
        "speculator": results["speculator"],
        "consensus": results["consensus"],
        "consensus_score": round(consensus_score, 1),
        "dispersion": round(dispersion, 1),
        "dominant_school": dominant_school,
        "school_labels": school_labels
    }


def format_multi_school_report(scores_result: Dict[str, Any], code: str = "", name: str = "") -> str:
    """格式化多评委评审团报告

    Args:
        scores_result: calculate_multi_school_scores 返回的结果
        code: 股票代码
        name: 股票名称

    Returns:
        str: 格式化的报告字符串
    """
    lines = []
    header = f"【多评委评审团】{code} {name}"
    lines.append("=" * 50)
    lines.append(header)
    lines.append("=" * 50)

    # 派别评分
    lines.append("\n📊 各派评委评分:")
    lines.append("-" * 40)

    school_emojis = {
        "value": "💰",
        "growth": "📈",
        "speculator": "🔥",
        "consensus": "⚖️"
    }

    for school, label in scores_result["school_labels"].items():
        emoji = school_emojis.get(school, "📊")
        score = label["score"]
        # 评分转星级
        stars = "★" * int(score / 20) + "☆" * (5 - int(score / 20))
        lines.append(f"  {emoji} {label['name']:<8} {score:>5.1f}分 {stars} ({label['persona']})")
        lines.append(f"      关注点: {label['focus']}")

    # 综合评分
    lines.append("-" * 40)
    lines.append(f"\n🎯 综合评分(三派均值): {scores_result['consensus_score']}分")
    lines.append(f"   分歧度: {scores_result['dispersion']:.1f} (越小表示派别分歧越小)")
    lines.append(f"   主导派别: {school_emojis.get(scores_result['dominant_school'], '')} {scores_result['school_labels'][scores_result['dominant_school']]['name']}")

    # 投资建议
    dominant = scores_result["dominant_school"]
    dominant_score = scores_result["school_labels"][dominant]["score"]

    lines.append("\n💡 投资建议:")
    if dominant == "value":
        lines.append("  价值派主导：适合长期持有，关注基本面和分红")
    elif dominant == "growth":
        lines.append("  成长派主导：适合中期持有，关注技术突破和资金流向")
    elif dominant == "speculator":
        lines.append("  游资派主导：适合短线操作，关注情绪和涨停板机会")
    else:
        lines.append("  各派别分歧较小，适合均衡配置")

    # 风险提示
    if scores_result["dispersion"] > 15:
        lines.append("\n⚠️ 警告：派别分歧度较大，投资决策需谨慎！")
        lines.append("   价值派和游资派可能出现完全相反的判断")

    lines.append("")
    return "\n".join(lines)

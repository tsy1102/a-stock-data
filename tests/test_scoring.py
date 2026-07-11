"""test_scoring.py — 评分系统 (ScoreData / calculate_score) 单元测试。

重点测试：
  - _score_technical: 均线系统、涨跌幅、涨停、MACD、RSI 等
  - _score_fundamental: ROE、毛利率、资产负债率
  - _score_valuation: PE相对行业、前向PE、回撤
  - _score_flow: 主力净流入、连续流入天数
  - _score_holder: 筹码集中度
  - _score_dividend: 股息率
  - calculate_score 综合评分
"""
from __future__ import annotations

import sys
from pathlib import Path

# 确保项目根目录在 path 中
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from stock_common import (
    ScoreData,
    ScoreResult,
    _score_technical,
    _score_fundamental,
    _score_valuation,
    _score_flow,
    _score_holder,
    _score_dividend,
    calculate_score,
)


# ── 基础数据工厂 ─────────────────────────────────────────

def _make_bullish() -> ScoreData:
    """构造一个“技术面看多”的股票数据"""
    d = ScoreData()
    d.code = "600519"
    d.name = "测试股票"
    d.price = 100.0
    # 均线多头排列
    d.ma5 = 100.0
    d.ma10 = 98.0
    d.ma20 = 95.0
    d.change_pct = 3.5  # 上涨
    d.macd_dif = 2.0
    d.macd_dea = 1.0  # MACD 金叉且>0
    d.rsi14 = 55  # 合理区间
    d.kdj_k = 70
    d.kdj_d = 50  # KDJ 金叉
    return d


def _make_bearish() -> ScoreData:
    """构造一个“技术面看空”的股票数据"""
    d = ScoreData()
    d.code = "000001"
    d.name = "测试股票2"
    # 均线空头
    d.ma5 = 95.0
    d.ma10 = 98.0
    d.ma20 = 100.0
    d.change_pct = -5.0
    d.macd_dif = -2.0
    d.macd_dea = -1.0  # MACD 死叉
    d.rsi14 = 85  # 超买
    return d


# ── 技术面评分测试 ───────────────────────────────────────

def test_score_technical_bullish_higher_than_bearish():
    bull = _make_bullish()
    bear = _make_bearish()
    bull_score, _ = _score_technical(bull)
    bear_score, _ = _score_technical(bear)
    assert bull_score > bear_score


def test_score_technical_limit_up_adds_points():
    d = _make_bullish()
    s1, _ = _score_technical(d)
    d.is_limit_up = True
    s2, _ = _score_technical(d)
    assert s2 > s1


def test_score_technical_bounded():
    """评分应限制在 [0, 100] 范围内。"""
    d = _make_bullish()
    d.is_limit_up = True
    d.change_pct = 10.0
    score, _ = _score_technical(d)
    assert 0 <= score <= 100


def test_score_technical_returns_details():
    d = _make_bullish()
    _, details = _score_technical(d)
    assert isinstance(details, list)
    assert any(isinstance(x, str) for x in details)


# ── 基本面评分测试 ───────────────────────────────────────

def test_score_fundamental_high_roe():
    d = ScoreData()
    d.roe = 25.0  # 优秀
    d.gross_margin = 50.0
    d.asset_liability_ratio = 0.3  # 较低

    score, details = _score_fundamental(d)
    assert score > 50.0
    assert any("ROE" in x for x in details)


def test_score_fundamental_mid_roe():
    d = ScoreData()
    d.roe = 12.0
    score, _ = _score_fundamental(d)
    assert score >= 50  # 中等 ROE 也应给分


def test_score_fundamental_bounded():
    d = ScoreData()
    d.roe = 50.0
    d.gross_margin = 80.0
    d.net_profit_margin = 50.0
    score, _ = _score_fundamental(d)
    assert 0 <= score <= 100


# ── 估值面评分测试 ───────────────────────────────────────

def test_score_valuation_low_pe():
    d = ScoreData()
    d.pe_ttm = 10.0
    d.industry_pe = 20.0
    d.forward_pe = 8.0
    score, _ = _score_valuation(d)
    assert score > 50.0


def test_score_valuation_drawdown():
    d = ScoreData()
    d.drawdown_from_high = -50.0  # 距高点腰斩
    score, _ = _score_valuation(d)
    assert score > 50


def test_score_valuation_high_pe_not_penalized_by_default():
    # 不低于行业 PE 的情况下，评分应不显著低于基准
    d = ScoreData()
    d.pe_ttm = 100.0
    d.industry_pe = 15.0
    score, _ = _score_valuation(d)
    # 应仍在有效范围
    assert 0 <= score <= 100


# ── 资金面评分测试 ───────────────────────────────────────

def test_score_flow_net_inflow():
    d = ScoreData()
    d.main_net_inflow = 100000000.0  # 1亿净流入
    d.consecutive_inflow_days = 15
    d.northbound_change = 100000.0
    score, _ = _score_flow(d)
    assert score > 50


def test_score_flow_zero_data():
    d = ScoreData()
    score, details = _score_flow(d)
    assert 0 <= score <= 100
    assert isinstance(details, list)


# ── 筹码面评分测试 ───────────────────────────────────────

def test_score_holder_concentration():
    d = ScoreData()
    d.holder_change_ratio = -0.05  # 股东数下降（筹码集中）
    d.holder_consecutive_decrease = True
    score, details = _score_holder(d)
    assert score > 50
    assert any("筹码" in x for x in details)


def test_score_holder_no_change():
    d = ScoreData()
    score, _ = _score_holder(d)
    assert 0 <= score <= 100


# ── 分红面评分测试 ───────────────────────────────────────

def test_score_dividend_high_yield():
    d = ScoreData()
    d.dividend_yield = 5.0
    d.consecutive_dividend_years = 10
    score, _ = _score_dividend(d)
    assert score > 50


def test_score_dividend_no_yield():
    d = ScoreData()
    score, _ = _score_dividend(d)
    assert 0 <= score <= 100


# ── 综合评分测试 ─────────────────────────────────────────

def test_calculate_score_full_structure():
    d = _make_bullish()
    d.roe = 20.0
    d.pe_ttm = 12.0
    d.forward_pe = 10.0
    d.dividend_yield = 3.0
    d.main_net_inflow = 50000000.0

    result = calculate_score("full", d)
    assert isinstance(result, ScoreResult)
    assert isinstance(result.total_score, float)
    assert 0 <= result.total_score <= 100
    assert isinstance(result.details, list)
    assert result.report_source == "full"


def test_calculate_score_dimensions_dict():
    d = _make_bullish()
    result = calculate_score("full", d)
    assert isinstance(result.dimensions, dict)


def test_calculate_score_med_and_lng():
    d = ScoreData()
    d.roe = 15.0
    d.pe_ttm = 15.0
    d.price = 50.0

    r1 = calculate_score("med", d)
    r2 = calculate_score("lng", d)
    assert isinstance(r1.total_score, float)
    assert isinstance(r2.total_score, float)


def test_calculate_score_returns_valid_score_for_empty_data():
    d = ScoreData()
    result = calculate_score("full", d)
    # 空数据仍应有评分（0-100）
    assert 0 <= result.total_score <= 100


# ── ScoreData 可修改性测试 ───────────────────────────────

def test_score_data_mutability():
    d = ScoreData()
    d.code = "600519"
    d.name = "测试"
    assert d.code == "600519"
    assert d.name == "测试"
    assert isinstance(d.price, float)

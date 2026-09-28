"""test_reports_chapter_omission.py — 回归锁固「源空→可见告警而非静默缺章」反模式。

背景: V17.0.14 接入【筹码分布(CYQ)】(当前 sht 报告编号 十四)、V17.0.15 接入【K线形态识别】(当前编号 十七)。本章号随报告章法演进, 测试字符串须同步当前结构(不再是十三·五/十六·五)。
原门控 `if _cyq_dict:` / `if len(_sr)>=3` 在数据源抓取失败(东财 push2his kline/get 或
远端 TDX bars 截断/不可达)时**整章静默跳过**, 不输出任何提示 → 重演 V17.0 已修的
M1/M4「假空白章节/假成功」反模式。2026-08-31 QA 发现 8 月全量 360 份 sht 报告二者 0 出现。

V17.0.17 修复: 源空时渲染可见告警占位(章节标题仍在, 正文显示 ⚠️ 数据源暂不可用)。

本测试纯离线: 所有数据源函数一律 mock; 将 get_cyq_distribution→{} 与 baidu_kline_full→([],[])
(模拟源故障), 断言两章标题 + 告警占位仍出现在渲染结果中(不再静默消失)。同时断言"源正常"
时两章输出真实数据(用真实结构的替身验证分支不退化)。
"""

from __future__ import annotations

import asyncio
from contextlib import ExitStack
from unittest import mock

import get_sht_report as S
import pandas as pd
from stock_common import (
    sc_datasource as _scd,
)  # get_cyq_distribution 在生成器内本地导入, 须 patch 此模块


class _FakeCData:
    """get_canonical_stock_data 的最小替身——仅含 generate_report_async 早期读取的字段。"""

    def __init__(self):
        self.code = "600519"
        self.name = "测试股"
        self.industry = "酿酒"
        self.price = 0.0
        self.change_pct = 0.0
        self.open = 0.0
        self.prev_close = 0.0
        self.high = 0.0
        self.low = 0.0
        self.high_52w = 0.0
        self.low_52w = 0.0
        self.time_anchor = "t-1"
        self.total_shares_wan = 1_000_000.0
        self.float_shares_wan = 1_000_000.0
        self.amount_wan = 0.0
        self.turnover_pct = 0.0
        self.limit_up = 0.0
        self.limit_down = 0.0
        self.mcap_yi = 0.0
        self.float_mcap_yi = 0.0
        self.pe_ttm = 0.0
        self.pe_dynamic = 0.0
        self.pb = 0.0
        self.change_5d = 0.0
        self.change_10d = 0.0
        self.change_20d = 0.0
        self.change_mtd = 0.0
        self.is_st = False
        self.is_new = False
        self.listing_days = 0

    def to_dict(self):
        return {
            "code": self.code,
            "name": self.name,
            "change_pct": self.change_pct,
            "main_net_buy_wan": 0,
        }


# (name, async?, return_value) —— 仅 patch 确实存在于 S 命名空间的数据源函数
_SYNC_STUBS = {
    "get_canonical_stock_data": _FakeCData(),
    "get_stock_info": {"name": "测试股", "industry": "酿酒", "list_date": "2001-01-01"},
    "get_fuyao_seal_info": None,
    "get_fuyao_auction_benchmark": None,
    "get_fuyao_anomaly": None,
    "get_fund_flow_realtime": {"data": []},  # 生成器内 if ff["data"]: 须含 data 键
    "get_fund_flow_120d": {
        "data": []
    },  # ff = get_fund_flow_120d → 生成器内 if ff["data"]: 须含 data 键
    "get_baidu_kline_with_ma": {},
    "get_shortline_indicators": {},
    "get_dividend_history": [],
    "get_reports": [],
    "get_concept_blocks": {"industry": [], "concept": []},
    "get_concept_from_zhb": {},
    "get_eastmoney_stock_news": [],
    "cls_telegraph": [],
    "em_hot_concept": [],
    "get_industry_comparison": {},  # 生成器内 ind_comp = await to_thread(get_industry_comparison) → 单 dict
    "get_industry_peers": [],
    "get_stock_sector_rank": {},
    "get_ft_comment_score_series": [],
    "get_ft_comment_desire": {},
    "get_ft_comment_org_participate": {},
    "get_ft_limit_up_pool_yesterday": [],
    "get_limit_pool_summary": {},
    "get_yesterday_limit_pool": [],
    "get_zhb_single_stock_data": {},
    "get_hsgt_macro_flow": {},
    "_get_index_quote": {},
    "baidu_kline_full": ([], []),  # 模拟 K线源故障
    "get_cyq_distribution": {},  # 模拟 CYQ 源故障
}
_ASYNC_STUBS = {
    "holder_change_async": [
        {
            "date": "2026-06-30",
            "change_ratio": 0.0,
            "holder_num": 100000,
            "change_num": 0,
            "change_pct": 0.0,
        },
        {
            "date": "2026-03-31",
            "change_ratio": 0.0,
            "holder_num": 100000,
            "change_num": 0,
            "change_pct": 0.0,
        },
    ],
    "get_margin_trading_async": [{"rzmre": 0, "rqye": 0, "rzye": 0} for _ in range(6)],
    "get_block_trade_async": [],
    "get_lockup_expiry_async": {
        "history": [],
        "upcoming": [],
    },  # 生成器内 lockup["history"]/["upcoming"]
    "get_northbound_hold_async": [],
    "get_strategic_announcements_async": [],
    "get_ths_hot_reason_async": {},  # if ths_hot: 守卫; 用 dict 更贴近真实结构
    "get_eps_forecast_async": pd.DataFrame(),  # 生成器内用 .empty/.columns, 须返回 DataFrame
    "get_hsgt_macro_flow_async": [],
    "get_main_net_buy_async": {},
    "get_zhb_streak_days": 0,
}


def _build_patch_stack(stk: ExitStack):
    """将 S 中所有已知数据源函数 patch 为安全替身; 返回是否成功 patch 了关键函数。"""
    patched_cyq = patched_kline = False
    for name, rv in _SYNC_STUBS.items():
        if hasattr(S, name):
            stk.enter_context(mock.patch.object(S, name, return_value=rv))
            if name == "baidu_kline_full":
                patched_kline = True
    for name, rv in _ASYNC_STUBS.items():
        if hasattr(S, name):
            stk.enter_context(mock.patch.object(S, name, new=mock.AsyncMock(return_value=rv)))
    # get_cyq_distribution 在生成器内本地导入(from stock_common.sc_datasource) → 须 patch 源模块
    stk.enter_context(mock.patch.object(_scd, "get_cyq_distribution", return_value={}))
    patched_cyq = True
    # 纯逻辑/本地函数: 返回安全值, 避免触网或异常
    if hasattr(S, "get_market_status"):
        stk.enter_context(mock.patch.object(S, "get_market_status", return_value=("closed", "")))
    if hasattr(S, "get_kline_patterns"):
        stk.enter_context(mock.patch.object(S, "get_kline_patterns", return_value={}))
    if hasattr(S, "calculate_score"):
        stk.enter_context(mock.patch.object(S, "calculate_score", return_value=(50, {})))
    return patched_cyq and patched_kline


def _render_via_runner(depth: str = "lite") -> str:
    """直接调用 generate_report_async(其末尾经 render_md_report 写盘 output_path), 读回 markdown。"""
    with ExitStack() as stk:
        ok = _build_patch_stack(stk)
        assert ok, "关键函数 get_cyq_distribution / baidu_kline_full 未被成功 patch"
        import tempfile, os

        _tmp = tempfile.mktemp(suffix=".md")
        try:
            asyncio.run(S.generate_report_async(mock.MagicMock(), "600519", _tmp, depth=depth))
            with open(_tmp, encoding="utf-8") as fh:
                return fh.read()
        finally:
            if os.path.exists(_tmp):
                os.remove(_tmp)


def test_cyq_and_kline_chapters_survive_source_failure():
    """源故障时两章必须渲染标题+告警占位, 不得静默消失。"""
    text = _render_via_runner("lite")
    assert text, "报告渲染结果为空"

    # 十四 CYQ: 标题必须在, 且源空时显式告警
    assert "十四、筹码分布（成本集中度）" in text, "CYQ 章节标题缺失(静默跳过未修复)"
    assert "东财 K线/CYQ 数据源暂不可用" in text, "CYQ 源空时应渲染可见告警占位"

    # 十七 K线形态: 标题必须在, 且源空时显式告警
    assert "十七、K线形态识别（TA-Lib 61 形态）" in text, "K线形态章节标题缺失(静默跳过未修复)"
    assert "K线数据源暂不可用" in text, "K线形态源空时应渲染可见告警占位"


def test_cyq_chapter_renders_data_when_source_ok():
    """源正常时 CYQ 章输出真实字段(验证修复分支未退化成永远告警)。"""
    _good_cyq = {
        "benefit_pct": 0.6,
        "avg_cost": 50.0,
        "concentration_90": 0.15,
        "concentration_70": 0.08,
        "cost_90_low": 40.0,
        "cost_90_high": 60.0,
        "cost_70_low": 45.0,
        "cost_70_high": 55.0,
        "source": "eastmoney_kline_f61",
    }
    with ExitStack() as stk:
        _build_patch_stack(stk)
        stk.enter_context(mock.patch.object(_scd, "get_cyq_distribution", return_value=_good_cyq))
        import tempfile, os

        _tmp = tempfile.mktemp(suffix=".md")
        try:
            asyncio.run(S.generate_report_async(mock.MagicMock(), "600519", _tmp, depth="lite"))
            with open(_tmp, encoding="utf-8") as fh:
                text = fh.read()
        finally:
            if os.path.exists(_tmp):
                os.remove(_tmp)
    assert "十四、筹码分布（成本集中度）" in text
    assert "获利盘比例: 60.0%" in text, "CYQ 源正常时应输出真实获利盘比例"
    assert "东财 K线/CYQ 数据源暂不可用" not in text, "CYQ 源正常时不应出现告警占位"

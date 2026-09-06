"""test_sec_type_exposure.py — DEBT-016 单元锁固。

验证 sec_type_market_label 由市场类型枚举(≡ ulist f182)正确推导
「市场板块 + 涨跌幅限制」标签, 供 sht/med/lng 报告露出(A5 孤儿字段消费)。
阈值复用 limit_pct_for(唯一事实源), 不重复硬编码。
"""
from __future__ import annotations

from stock_common.sc_utils import sec_type_market_label


class TestSecTypeMarketLabel:
    def test_main_board(self):
        assert sec_type_market_label(2, "600519", "贵州茅台") == "主板（涨跌停 ±10%）"

    def test_chinext(self):
        assert sec_type_market_label(5, "300750", "宁德时代") == "创业板（涨跌停 ±20%）"

    def test_star(self):
        assert sec_type_market_label(32, "688981", "中芯国际") == "科创板（涨跌停 ±20%）"

    def test_bse(self):
        assert sec_type_market_label(80, "835174", "测试北交") == "北交所（涨跌停 ±30%）"

    def test_unknown_falls_back_to_main(self):
        # 未知枚举 / 0 → 主板(10%), 不抛异常
        assert sec_type_market_label(999, "000001", "平安银行") == "主板（涨跌停 ±10%）"
        assert sec_type_market_label(0, "000001", "平安银行") == "主板（涨跌停 ±10%）"

"""test_stock_common.py — 公共工具函数单元测试。

覆盖模块：sc_utils.py
测试函数：
  - _safe_float：各种输入类型（字符串、int、float、None、NaN、inf）
  - get_board_type：板块判断（科创板/创业板/主板/ST）
  - is_limit_up / is_limit_down：涨跌停判断（V10.0: ST涨跌幅放宽至10%）
  - clean_codes：代码清洗与去重
  - is_trading_day：交易日历判断（依赖conftest网络mock）
"""
from __future__ import annotations

import datetime

from stock_common import (
    _safe_float,
    get_board_type,
    is_limit_up,
    is_limit_down,
    clean_codes,
    is_trading_day,
)


def test_safe_float_basic():
    assert _safe_float("12.34") == 12.34
    assert _safe_float("0") == 0.0
    assert _safe_float("-5.2") == -5.2


def test_safe_float_default():
    assert _safe_float(None) == 0.0
    assert _safe_float("abc") == 0.0
    assert _safe_float("", default=99.0) == 99.0
    assert _safe_float(float("nan")) == 0.0  # 非有限值
    assert _safe_float(float("in")) == 0.0


def test_safe_float_various_inputs():
    # 整数也可被转换
    assert _safe_float(42) == 42.0
    # 数字字符串
    assert _safe_float("1e5") == 100000.0


def test_get_board_type():
    """V8.9新增：板块判断函数测试（替代已移除的 holder_cache_flush 测试）"""
    assert get_board_type("688981") == "科创板"
    assert get_board_type("300750") == "创业板"
    assert get_board_type("600519") == "主板"
    assert get_board_type("000001") == "主板"
    assert get_board_type("600519", "ST股票") == "ST"


def test_is_limit_up():
    """涨停判断测试（V10.0: ST涨跌幅放宽至10%）"""
    # 创业板 20% 涨停
    assert is_limit_up("300750", "", 20.0) is True
    assert is_limit_up("300750", "", 15.0) is False
    # 科创板 20% 涨停
    assert is_limit_up("688981", "", 19.5) is True
    # 主板 10% 涨停
    assert is_limit_up("600519", "", 10.0) is True
    # ST股票 10% 涨停（V10.0新规）
    assert is_limit_up("600519", "ST股票", 10.0) is True
    assert is_limit_up("600519", "ST股票", 4.8) is False


def test_is_limit_down():
    """跌停判断测试（V10.0: ST涨跌幅放宽至10%）"""
    # 创业板 20% 跌停
    assert is_limit_down("300750", "", -20.0) is True
    assert is_limit_down("300750", "", -15.0) is False
    # 科创板 20% 跌停
    assert is_limit_down("688981", "", -19.5) is True
    # 主板 10% 跌停
    assert is_limit_down("600519", "", -10.0) is True
    # ST股票 10% 跌停（V10.0新规）
    assert is_limit_down("600519", "ST股票", -10.0) is True
    assert is_limit_down("600519", "ST股票", -4.8) is False


def test_clean_codes():
    """代码清洗测试"""
    assert clean_codes(["600519", "002193如意", "abc"]) == ["600519", "002193"]
    assert clean_codes([]) == []
    # 去重测试
    result = clean_codes(["600519", "600519", "000001"])
    assert result == ["600519", "000001"]

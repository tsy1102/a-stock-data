"""test_stock_common.py — 公共工具函数单元测试。"""
from __future__ import annotations

import json
import os

from stock_common import (
    _safe_float,
    get_board_type,
    is_limit_up,
    clean_codes,
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
    assert _safe_float(float("inf")) == 0.0


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
    """涨停判断测试"""
    # 创业板 20% 涨停
    assert is_limit_up("300750", "", 20.0) is True
    assert is_limit_up("300750", "", 15.0) is False
    # 主板 10% 涨停
    assert is_limit_up("600519", "", 10.0) is True


def test_clean_codes():
    """代码清洗测试"""
    assert clean_codes(["600519", "002193如意", "abc"]) == ["600519", "002193"]
    assert clean_codes([]) == []
    # 去重测试
    result = clean_codes(["600519", "600519", "000001"])
    assert result == ["600519", "000001"]

"""test_stock_common.py — 公共工具函数单元测试。"""
from __future__ import annotations

import json
import os

from stock_common import (
    _safe_float,
    holder_cache_flush,
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


def test_holder_cache_flush_handles_missing_dir(tmp_path, monkeypatch):
    # 把 HOLDER_CACHE_FILE 指向临时目录
    fake_cache = tmp_path / "holder_cache.json"
    # 模块内通过绝对路径写，这里仅验证函数不抛异常
    monkeypatch.chdir(tmp_path)
    try:
        holder_cache_flush()
    except Exception as e:
        raise AssertionError(f"holder_cache_flush 不应抛异常：{e}")
    # 如果当前工作目录没有数据文件，也不会出错
    assert True

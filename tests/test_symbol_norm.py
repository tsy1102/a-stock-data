"""P2-A：normalize_symbol 代码格式归一测试。

覆盖：裸码 / 前缀(sh|sz|bj) / 后缀(.XSHG|.XSHE|.BJ|.SH|.SZ) 三种书写，
沪深主板 / 创业板 / 科创板 / 北交所(92 新号段 + 43/83/87/8/4 老号段) 全市场段，
以及“显式前缀/后缀与号段矛盾时显式报错”的纪律（A5：不静默猜测）。
"""

import pytest

from stock_common.symbol_norm import Symbol, market_of, normalize_symbol

# ───────────── 裸 6 位：市场段推导 ─────────────


def test_market_of_segments():
    assert market_of("600519") == "SH"  # 沪主板
    assert market_of("000001") == "SZ"  # 深主板
    assert market_of("300750") == "SZ"  # 创业板
    assert market_of("688981") == "SH"  # 科创板
    assert market_of("830799") == "BJ"  # 北交所 83
    assert market_of("920002") == "BJ"  # 北交所 92
    assert market_of("430047") == "BJ"  # 北交所 43（老）
    assert market_of("870000") == "BJ"  # 北交所 87（老）
    assert market_of("400000") == "BJ"  # 老三板 4
    assert market_of("800000") == "BJ"  # 老三板 8


# ───────────── 裸码归一 ─────────────


def test_normalize_plain():
    assert normalize_symbol("600519") == Symbol("600519", "SH")
    assert normalize_symbol("000001") == Symbol("000001", "SZ")
    assert normalize_symbol("830799") == Symbol("830799", "BJ")


# ───────────── 前缀风格 sh/sz/bj ─────────────


def test_normalize_prefix():
    assert normalize_symbol("sh600519") == Symbol("600519", "SH")
    assert normalize_symbol("SH600519") == Symbol("600519", "SH")
    assert normalize_symbol("sz000001") == Symbol("000001", "SZ")
    assert normalize_symbol("bj830799") == Symbol("830799", "BJ")
    assert normalize_symbol("BJ830799") == Symbol("830799", "BJ")


# ───────────── 后缀风格 .XSHG/.XSHE/.BJ/.SH/.SZ ─────────────


def test_normalize_suffix():
    assert normalize_symbol("600519.XSHG") == Symbol("600519", "SH")
    assert normalize_symbol("600519.SH") == Symbol("600519", "SH")
    assert normalize_symbol("000001.XSHE") == Symbol("000001", "SZ")
    assert normalize_symbol("000001.SZ") == Symbol("000001", "SZ")
    assert normalize_symbol("830799.BJ") == Symbol("830799", "BJ")


# ───────────── 矛盾输入显式报错（不静默猜测） ─────────────


def test_contradiction_raises():
    # 前缀 sh 暗示 SH，但 000001 号段为 SZ
    with pytest.raises(ValueError):
        normalize_symbol("sh000001")
    # 后缀 .XSHE 暗示 SZ，但 600519 号段为 SH
    with pytest.raises(ValueError):
        normalize_symbol("600519.XSHE")
    # 前缀 bj 暗示 BJ，但 600519 号段为 SH
    with pytest.raises(ValueError):
        normalize_symbol("bj600519")
    # 空 / 无法解析
    with pytest.raises(ValueError):
        normalize_symbol("")
    with pytest.raises(ValueError):
        normalize_symbol("abc")


# ───────────── 各源格式输出 ─────────────


def test_formatters():
    sh = Symbol("600519", "SH")
    sz = Symbol("000001", "SZ")
    bj = Symbol("830799", "BJ")

    # 东财 secid
    assert sh.eastmoney() == "1.600519"
    assert sz.eastmoney() == "0.000001"
    assert bj.eastmoney() == "0.830799"

    # 腾讯 / 新浪（小写前缀）
    assert sh.tencent() == "sh600519"
    assert sz.sina() == "sz000001"
    assert bj.tencent() == "bj830799"

    # 聚宽后缀
    assert sh.joinquant() == "600519.XSHG"
    assert sz.joinquant() == "000001.XSHE"
    assert bj.joinquant() == "830799.BJ"

    # 大写后缀（fuyao 等）
    assert sh.upper_suffix() == "600519.SH"
    assert sz.upper_suffix() == "000001.SZ"
    assert bj.upper_suffix() == "830799.BJ"

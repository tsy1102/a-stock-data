#!/usr/bin/env python3
"""test_tdx_health.py — V15.5 easy_tdx 适配层单元测试

覆盖:
  - _FREQ_TO_CATEGORY 映射（mootdx freq → easy_tdx category）
  - _easy_market 市场判断（股票/ETF/指数）
  - _EasyTdxAdapter 字段对齐（vol 股→手、pre_close→last_close、finance 去下划线、datetime 列）
  - 空 DataFrame / 异常降级（不崩溃）
离线测试（mock DataFrame，不联网）。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import pytest

import tdx_client as tc


# ── _FREQ_TO_CATEGORY 映射 ──

class TestFreqToCategory:
    def test_day_freq9(self):
        assert tc._FREQ_TO_CATEGORY[9] == 4  # mootdx 9=日线 → easy_tdx DAY

    def test_week_freq5(self):
        assert tc._FREQ_TO_CATEGORY[5] == 5  # WEEK

    def test_min_freqs(self):
        assert tc._FREQ_TO_CATEGORY[0] == 0  # 5min
        assert tc._FREQ_TO_CATEGORY[1] == 1  # 15min
        assert tc._FREQ_TO_CATEGORY[2] == 2  # 30min
        assert tc._FREQ_TO_CATEGORY[3] == 3  # 60min
        assert tc._FREQ_TO_CATEGORY[7] == 7  # 1min

    def test_unknown_freq_default_day(self):
        assert tc._FREQ_TO_CATEGORY.get(999, 4) == 4


# ── _easy_market 市场判断 ──

class TestEasyMarket:
    def test_sh_stock(self):
        assert tc._easy_market("600519") == 1  # 沪市股票

    def test_sz_stock(self):
        assert tc._easy_market("000001") == 0  # 平安银行（深）
        assert tc._easy_market("300750") == 0  # 创业板（深）

    def test_etf_sh(self):
        assert tc._easy_market("510300") == 1  # 沪深300ETF（沪）

    def test_bse(self):
        # V16.2.2: 北交所 8/4/92 段 → 北京（原映射到深圳/上海导致 K 线空响应）
        assert tc._easy_market("832000") == 2
        assert tc._easy_market("430047") == 2
        assert tc._easy_market("920001") == 2
        assert tc._market_prefix("920001") == "bj"
        assert tc._market_from_code("920001") == 2

    def test_index_sh(self):
        assert tc._easy_market("000001", is_index=True) == 1  # 上证指数

    def test_index_sz(self):
        assert tc._easy_market("399006", is_index=True) == 0  # 创业板指
        assert tc._easy_market("399001", is_index=True) == 0  # 深证成指


# ── _EasyTdxAdapter 字段对齐 ──

class _MockClient:
    """mock easy_tdx TdxClient。"""

    def __init__(self, bars_df=None, quotes_df=None, finance_df=None, index_df=None,
                 raise_on=None):
        self.bars_df = bars_df
        self.quotes_df = quotes_df
        self.finance_df = finance_df
        self.index_df = index_df
        self.raise_on = raise_on or set()
        self.closed_flag = False

    def get_security_bars(self, *a, **k):
        if "bars" in self.raise_on:
            raise RuntimeError("bars fail")
        return self.bars_df

    def get_index_bars(self, *a, **k):
        if "index" in self.raise_on:
            raise RuntimeError("index fail")
        return self.index_df

    def get_security_quotes(self, *a, **k):
        if "quotes" in self.raise_on:
            raise RuntimeError("quotes fail")
        return self.quotes_df

    def get_finance_info(self, *a, **k):
        if "finance" in self.raise_on:
            raise RuntimeError("finance fail")
        return self.finance_df

    def close(self):
        self.closed_flag = True


def _make_bars_df(vol=5512752.0, amount=7.3e9):
    return pd.DataFrame([{
        "date": "2026-07-31", "open": 1330.03, "close": 1350.6,
        "high": 1355.72, "low": 1325.77, "vol": vol, "amount": amount,
    }])


class TestAdapterBars:
    def test_vol_stock_to_hand(self):
        """easy_tdx vol(股) → mootdx vol(手) /100。"""
        a = tc._EasyTdxAdapter(_MockClient(bars_df=_make_bars_df(vol=5512752.0)))
        df = a.bars(symbol="600519", frequency=9, offset=1)
        assert abs(df.iloc[0]["vol"] - 55127.52) < 0.01

    def test_datetime_column_added(self):
        a = tc._EasyTdxAdapter(_MockClient(bars_df=_make_bars_df()))
        df = a.bars(symbol="600519")
        assert "datetime" in df.columns
        assert df.iloc[0]["datetime"].startswith("2026-07-31")

    def test_empty_df(self):
        a = tc._EasyTdxAdapter(_MockClient(bars_df=pd.DataFrame()))
        df = a.bars(symbol="600519")
        assert df is not None and df.empty  # 不崩溃

    def test_exception_returns_empty(self):
        a = tc._EasyTdxAdapter(_MockClient(raise_on={"bars"}))
        df = a.bars(symbol="600519")
        assert df is not None and df.empty  # 异常降级为空表


class TestAdapterQuotes:
    def test_pre_close_renamed(self):
        qdf = pd.DataFrame([{"price": 1350.6, "pre_close": 1361.76,
                             "open": 1330.03, "vol": 55127.52}])
        a = tc._EasyTdxAdapter(_MockClient(quotes_df=qdf))
        q = a.quotes(symbol="600519")
        assert "last_close" in q.columns
        assert q.iloc[0]["last_close"] == 1361.76

    def test_empty_quotes(self):
        a = tc._EasyTdxAdapter(_MockClient(quotes_df=pd.DataFrame()))
        q = a.quotes(symbol="600519")
        assert q is not None and q.empty


class TestAdapterFinance:
    def test_columns_underscore_removed(self):
        fdf = pd.DataFrame([{"zong_guben": 12.5e8, "jing_lirun": 2.7e11,
                             "liutong_guben": 12.5e8}])
        a = tc._EasyTdxAdapter(_MockClient(finance_df=fdf))
        f = a.finance(symbol="600519")
        cols = set(f.columns)
        assert "zongguben" in cols and "jinglirun" in cols and "liutongguben" in cols

    def test_empty_finance(self):
        a = tc._EasyTdxAdapter(_MockClient(finance_df=pd.DataFrame()))
        f = a.finance(symbol="600519")
        assert f is not None and f.empty


class TestAdapterIndexBars:
    def test_index_bars_basic(self):
        idf = pd.DataFrame([{"date": "2026-07-31", "open": 3820.0,
                             "close": 3832.26, "high": 3840.0, "low": 3810.0,
                             "vol": 5e8, "amount": 5e11}])
        a = tc._EasyTdxAdapter(_MockClient(index_df=idf))
        df = a.index_bars(symbol="000001", frequency=9)
        assert len(df) == 1
        assert df.iloc[0]["close"] == 3832.26
        assert "datetime" in df.columns


class TestAdapterClose:
    def test_close_propagates(self):
        mc = _MockClient()
        a = tc._EasyTdxAdapter(mc)
        a.close()
        assert a.closed is True
        assert mc.closed_flag is True


# ── 服务器白名单 ──

class TestServerWhitelist:
    def test_primary_host_known(self):
        assert tc._EASY_TDX_PRIMARY_HOST == "180.153.18.170"

    def test_preferred_hosts_contains_primary(self):
        assert tc._EASY_TDX_PREFERRED_HOSTS[0] == tc._EASY_TDX_PRIMARY_HOST
        assert len(tc._EASY_TDX_PREFERRED_HOSTS) >= 1

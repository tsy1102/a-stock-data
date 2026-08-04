#!/usr/bin/env python3
"""easy_tdx 1.20.4 vs mootdx 0.11.7 实证对比（K 线稳定性 + 字段差异）"""
import sys
sys.path.insert(0, r"D:\GitHub\test")
CODE = "600519"

print(f"=== 1. easy_tdx {__import__('easy_tdx').__version__ if hasattr(__import__('easy_tdx'),'__version__') else '?'} K 线 ===")
try:
    from easy_tdx.client import TdxClient
    with TdxClient.from_best_host() as client:
        df = client.get_security_bars(1, CODE, 4, 0, 5)  # SH=1, DAY=4
        print(f"  成功: {len(df)} 根")
        print(f"  列: {list(df.columns)}")
        if len(df):
            row = df.iloc[-1]
            print(f"  最新: open={row['open']} close={row['close']} high={row['high']} "
                  f"low={row['low']} vol={row['vol']} amount={row['amount']}")
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {str(e)[:100]}")

print(f"\n=== 2. mootdx 0.11.7 K 线（对比）===")
try:
    from mootdx.quotes import Quotes
    c = Quotes.factory(market='std', bestip=False)
    df2 = c.bars(symbol=CODE, frequency=9, start=0, offset=5)
    print(f"  成功: {len(df2)} 根")
    if len(df2):
        row = df2.iloc[-1]
        print(f"  列: {list(df2.columns)[:12]}")
        print(f"  最新: close={row['close']} vol={row.get('vol')} amount={row.get('amount')}")
except Exception as e:
    print(f"  FAIL: {type(e).__name__}: {str(e)[:100]}")

print(f"\n=== 3. easy_tdx 字段 vs 本项目 cdata 字段（关键差异）===")
print("""
| 数据 | easy_tdx | 本项目 tdx_client | 差异 |
|:---|:---|:---|:---|
| K线 vol | 股（×100） | 手 | 需 ×100 适配 |
| K线 datetime | year/month/day/hour/minute int×5 | YYYYMMDD str | 需转换 |
| 五档盘口 | SecurityQuote.bid1-5/ask1-5 | 无 | easy_tdx 新增 |
| 内外盘 | s_vol/b_vol | 无 | easy_tdx 新增 |
| 涨速 | rise_speed | 无 | easy_tdx 新增（sht 有用）|
| 除权除息 | XdxrRecord | V15 删了 qfq | 前复权基础 |
| 财务 | FinanceInfo 22 字段 | 只用 3 个股本 | easy_tdx 更丰富 |
| 前复权 | --adjust QFQ (v1.20+) | V15 无 | easy_tdx 新增 |
| 34 技术指标 | 内置 | 无 | easy_tdx 新增 |
""")

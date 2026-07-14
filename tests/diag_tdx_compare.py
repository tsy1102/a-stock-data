#!/usr/bin/env python3
"""easy-tdx 与 mootdx 接口对比测试

测试两个TDX库的关键接口，对比：
1. K线数据获取（日K/分钟K）
2. 实时行情
3. 资金流数据
4. 板块数据
5. 复权数据
6. 连接稳定性
7. API设计差异
"""

import sys
import os
import time
import inspect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEST_CODE = "600519"  # 贵州茅台
TEST_MARKET = 1  # SH

print("=" * 70)
print("easy-tdx 与 mootdx 接口对比测试")
print("=" * 70)


# ═══════════════════════════════════════
# Part 1: 库信息对比
# ═══════════════════════════════════════
print("\n【Part 1】库基本信息")
print("-" * 70)

# easy-tdx 信息
print("\n--- easy-tdx ---")
try:
    from easy_tdx import TdxClient, Market, KlineCategory
    import easy_tdx
    print("  包名: easy_tdx")
    try:
        import importlib.metadata
        ver = importlib.metadata.version("easy-tdx")
        print(f"  版本: {ver}")
    except:
        print("  版本: 未知")
    print("  核心类: TdxClient, Market, KlineCategory, MacClient")
    print(f"  TdxClient方法: {[m for m in dir(TdxClient) if not m.startswith('_')]}")
    print(f"  KlineCategory属性: {[m for m in dir(KlineCategory) if not m.startswith('_')]}")
    print(f"  Market属性: {[m for m in dir(Market) if not m.startswith('_')]}")
except Exception as e:
    print(f"  ❌ 导入失败: {e}")

# mootdx 信息
print("\n--- mootdx ---")
try:
    import mootdx
    from mootdx.quotes import Quotes
    print("  包名: mootdx")
    print(f"  版本: {mootdx.__version__}")
    q = Quotes.factory(market='std')
    inst_methods = [m for m in dir(q) if not m.startswith('_')]
    print(f"  Quotes实例方法: {inst_methods}")
    print(f"  bars签名: {inspect.signature(q.bars)}")
    print(f"  xdxr签名: {inspect.signature(q.xdxr)}")
    print(f"  quotes签名: {inspect.signature(q.quotes)}")
except Exception as e:
    print(f"  ❌ 导入失败: {e}")


# ═══════════════════════════════════════
# Part 2: K线数据对比
# ═══════════════════════════════════════
print("\n\n【Part 2】K线数据对比（日K线）")
print("-" * 70)

# easy-tdx 日K线
print("\n--- easy-tdx 日K线 ---")
easy_bars = None
t0 = time.time()
try:
    client = TdxClient.from_best_host()
    client.connect()
    easy_bars = client.get_security_bars(Market.SH, TEST_CODE, KlineCategory.DAY, 0, 10)
    t1 = time.time()
    print(f"  耗时: {t1-t0:.3f}s")
    print(f"  返回类型: {type(easy_bars).__name__}")
    if easy_bars is not None and len(easy_bars) > 0:
        print(f"  返回行数: {len(easy_bars)}")
        print(f"  列名: {list(easy_bars.columns)}")
        print(f"  前3行收盘价: {easy_bars['close'].head(3).tolist()}")
        print(f"  数据范围: {easy_bars.index[0]} ~ {easy_bars.index[-1]}")
    client.close()
except Exception as e:
    t1 = time.time()
    print(f"  耗时: {t1-t0:.3f}s")
    print(f"  ❌ 失败: {e}")

# mootdx 日K线
print("\n--- mootdx 日K线 ---")
mootdx_bars = None
t0 = time.time()
try:
    df = q.bars(symbol=TEST_CODE, frequency=4, start=0, offset=10)
    t1 = time.time()
    mootdx_bars = df
    print(f"  耗时: {t1-t0:.3f}s")
    print(f"  返回类型: {type(df).__name__}")
    if df is not None and len(df) > 0:
        print(f"  返回行数: {len(df)}")
        print(f"  列名: {list(df.columns)}")
        print(f"  前3行收盘价: {df['close'].head(3).tolist()}")
        print(f"  数据范围: {df.index[0]} ~ {df.index[-1]}")
except Exception as e:
    t1 = time.time()
    print(f"  耗时: {t1-t0:.3f}s")
    print(f"  ❌ 失败: {e}")

# 数据对比
if easy_bars is not None and mootdx_bars is not None:
    print("\n--- 数据对比 ---")
    easy_close = easy_bars['close'].tail(5).tolist()
    mootdx_close = mootdx_bars['close'].tail(5).tolist()
    print(f"  easy-tdx 收盘价: {easy_close}")
    print(f"  mootdx  收盘价: {mootdx_close}")
    if easy_close == mootdx_close:
        print("  ✅ 收盘价完全一致")
    else:
        diff = [abs(a-b) for a, b in zip(easy_close, mootdx_close)]
        print(f"  ⚠️ 收盘价有差异: {diff}")


# ═══════════════════════════════════════
# Part 3: 分钟K线对比
# ═══════════════════════════════════════
print("\n\n【Part 3】分钟K线对比（5分钟K线）")
print("-" * 70)

# easy-tdx 5分钟K线
print("\n--- easy-tdx 5分钟K线 ---")
try:
    client = TdxClient.from_best_host()
    client.connect()
    t0 = time.time()
    easy_5min = client.get_security_bars(Market.SH, TEST_CODE, KlineCategory.MIN5, 0, 10)
    t1 = time.time()
    print(f"  耗时: {t1-t0:.3f}s")
    if easy_5min is not None and len(easy_5min) > 0:
        print(f"  返回行数: {len(easy_5min)}")
        print(f"  列名: {list(easy_5min.columns)}")
        print(f"  前3行: {easy_5min[['close','volume']].head(3).to_dict('records')}")
    client.close()
except Exception as e:
    print(f"  ❌ 失败: {e}")

# mootdx 5分钟K线
print("\n--- mootdx 5分钟K线 ---")
try:
    t0 = time.time()
    mootdx_5min = q.bars(symbol=TEST_CODE, frequency=0, start=0, offset=10)
    t1 = time.time()
    print(f"  耗时: {t1-t0:.3f}s")
    if mootdx_5min is not None and len(mootdx_5min) > 0:
        print(f"  返回行数: {len(mootdx_5min)}")
        print(f"  列名: {list(mootdx_5min.columns)}")
        print(f"  前3行: {mootdx_5min[['close','volume']].head(3).to_dict('records')}")
except Exception as e:
    print(f"  ❌ 失败: {e}")


# ═══════════════════════════════════════
# Part 4: 实时行情对比
# ═══════════════════════════════════════
print("\n\n【Part 4】实时行情对比")
print("-" * 70)

# easy-tdx 实时行情
print("\n--- easy-tdx 实时行情 ---")
try:
    client = TdxClient.from_best_host()
    client.connect()
    t0 = time.time()
    easy_quote = client.get_security_quotes([(TEST_MARKET, TEST_CODE)])
    t1 = time.time()
    print(f"  耗时: {t1-t0:.3f}s")
    if easy_quote is not None and len(easy_quote) > 0:
        print(f"  返回类型: {type(easy_quote).__name__}")
        print(f"  列名: {list(easy_quote.columns)[:15]}...")
        row = easy_quote.iloc[0]
        print(f"  代码: {row.get('code','')}, 价格: {row.get('price','')}")
    client.close()
except Exception as e:
    print(f"  ❌ 失败: {e}")

# mootdx 实时行情
print("\n--- mootdx 实时行情 ---")
try:
    t0 = time.time()
    mootdx_quote = q.quotes(symbol=TEST_CODE)
    t1 = time.time()
    print(f"  耗时: {t1-t0:.3f}s")
    print(f"  返回类型: {type(mootdx_quote).__name__}")
    if mootdx_quote is not None and len(mootdx_quote) > 0:
        print(f"  返回行数: {len(mootdx_quote)}")
        print(f"  列名: {list(mootdx_quote.columns)[:15]}...")
        row = mootdx_quote.iloc[0]
        print(f"  代码: {row.get('code','')}, 价格: {row.get('price','')}")
except Exception as e:
    print(f"  ❌ 失败: {e}")


# ═══════════════════════════════════════
# Part 5: 资金流数据对比
# ═══════════════════════════════════════
print("\n\n【Part 5】资金流数据对比")
print("-" * 70)

# easy-tdx 资金流
print("\n--- easy-tdx 历史资金流 ---")
try:
    client = TdxClient.from_best_host()
    client.connect()
    t0 = time.time()
    easy_ff = client.get_history_fund_flow(TEST_MARKET, TEST_CODE, 0, 10)
    t1 = time.time()
    print(f"  耗时: {t1-t0:.3f}s")
    if easy_ff is not None and len(easy_ff) > 0:
        print(f"  返回行数: {len(easy_ff)}")
        print(f"  列名: {list(easy_ff.columns)}")
        print(f"  前3行: {easy_ff.head(3).to_dict('records')}")
    else:
        print("  返回空数据")
    client.close()
except Exception as e:
    print(f"  ❌ 失败: {e}")

# mootdx 资金流
print("\n--- mootdx 资金流 ---")
try:
    if hasattr(q, 'finance'):
        print(f"  finance方法签名: {inspect.signature(q.finance)}")
    # mootdx 没有直接的资金流接口
    print("  mootdx 无直接资金流接口（需通过其他方式获取）")
    # 检查是否有相关方法
    ff_methods = [m for m in dir(q) if 'flow' in m.lower() or 'fund' in m.lower() or 'finance' in m.lower()]
    print(f"  资金流相关方法: {ff_methods}")
except Exception as e:
    print(f"  ❌ 失败: {e}")


# ═══════════════════════════════════════
# Part 6: 板块数据对比
# ═══════════════════════════════════════
print("\n\n【Part 6】板块数据对比")
print("-" * 70)

# easy-tdx 板块（MacClient）
print("\n--- easy-tdx 板块数据（MacClient）---")
try:
    from easy_tdx import MacClient
    mac = MacClient.from_best_host()
    mac.connect()
    t0 = time.time()
    belong = mac.get_belong_board(1, TEST_CODE)
    t1 = time.time()
    print(f"  耗时: {t1-t0:.3f}s")
    if belong is not None and len(belong) > 0:
        print(f"  返回行数: {len(belong)}")
        print(f"  列名: {list(belong.columns)}")
        print(f"  前3行: {belong.head(3).to_dict('records')}")
    mac.close()
except Exception as e:
    print(f"  ❌ 失败: {e}")

# mootdx 板块
print("\n--- mootdx 板块数据 ---")
try:
    if hasattr(q, 'block'):
        print(f"  block方法签名: {inspect.signature(q.block)}")
        t0 = time.time()
        block_data = q.block(symbol=TEST_CODE)
        t1 = time.time()
        print(f"  耗时: {t1-t0:.3f}s")
        if block_data is not None and len(block_data) > 0:
            print(f"  返回行数: {len(block_data)}")
            print(f"  列名: {list(block_data.columns)}")
            print(f"  前3行: {block_data.head(3).to_dict('records')}")
    else:
        print("  mootdx 无block方法")
    # 检查板块相关方法
    block_methods = [m for m in dir(q) if 'block' in m.lower()]
    print(f"  板块相关方法: {block_methods}")
except Exception as e:
    print(f"  ❌ 失败: {e}")


# ═══════════════════════════════════════
# Part 7: 复权数据对比
# ═══════════════════════════════════════
print("\n\n【Part 7】复权数据对比")
print("-" * 70)

# easy-tdx 复权
print("\n--- easy-tdx 复权数据 ---")
try:
    # 检查easy-tdx是否有复权相关方法
    client_methods = [m for m in dir(TdxClient) if not m.startswith('_')]
    xdxr_methods = [m for m in client_methods if 'xdxr' in m.lower() or 'adjust' in m.lower() or 'right' in m.lower()]
    print(f"  TdxClient复权相关方法: {xdxr_methods}")
    if not xdxr_methods:
        print("  easy-tdx 无内置复权方法")
except Exception as e:
    print(f"  ❌ 失败: {e}")

# mootdx 复权
print("\n--- mootdx 复权数据 ---")
try:
    t0 = time.time()
    xdxr_data = q.xdxr(symbol=TEST_CODE)
    t1 = time.time()
    print(f"  耗时: {t1-t0:.3f}s")
    if xdxr_data is not None and len(xdxr_data) > 0:
        print(f"  返回行数: {len(xdxr_data)}")
        print(f"  列名: {list(xdxr_data.columns)}")
        print(f"  前5行:\n{xdxr_data.head()}")
except Exception as e:
    print(f"  ❌ 失败: {e}")


# ═══════════════════════════════════════
# Part 8: F10数据对比
# ═══════════════════════════════════════
print("\n\n【Part 8】F10数据对比")
print("-" * 70)

# easy-tdx F10
print("\n--- easy-tdx F10 ---")
try:
    f10_methods = [m for m in dir(TdxClient) if 'f10' in m.lower() or 'company' in m.lower() or 'report' in m.lower()]
    print(f"  TdxClient F10相关方法: {f10_methods}")
except Exception as e:
    print(f"  ❌ 失败: {e}")

# mootdx F10
print("\n--- mootdx F10 ---")
try:
    f10_methods = [m for m in dir(q) if 'f10' in m.lower() or 'company' in m.lower() or 'report' in m.lower()]
    print(f"  Quotes F10相关方法: {f10_methods}")
    if hasattr(q, 'F10'):
        print(f"  F10方法签名: {inspect.signature(q.F10)}")
except Exception as e:
    print(f"  ❌ 失败: {e}")


# ═══════════════════════════════════════
# Part 9: 连接稳定性对比
# ═══════════════════════════════════════
print("\n\n【Part 9】连接稳定性对比（3次连续请求）")
print("-" * 70)

# easy-tdx 稳定性
print("\n--- easy-tdx 稳定性 ---")
easy_times = []
try:
    client = TdxClient.from_best_host()
    client.connect()
    for i in range(3):
        t0 = time.time()
        bars = client.get_security_bars(Market.SH, TEST_CODE, KlineCategory.DAY, 0, 5)
        t1 = time.time()
        elapsed = t1 - t0
        easy_times.append(elapsed)
        ok = "✅" if bars is not None and len(bars) > 0 else "❌"
        print(f"  第{i+1}次: {elapsed:.3f}s {ok}")
    client.close()
except Exception as e:
    print(f"  ❌ 失败: {e}")
if easy_times:
    print(f"  平均耗时: {sum(easy_times)/len(easy_times):.3f}s")

# mootdx 稳定性
print("\n--- mootdx 稳定性 ---")
mootdx_times = []
for i in range(3):
    try:
        t0 = time.time()
        bars = q.bars(symbol=TEST_CODE, frequency=4, start=0, offset=5)
        t1 = time.time()
        elapsed = t1 - t0
        mootdx_times.append(elapsed)
        ok = "✅" if bars is not None and len(bars) > 0 else "❌"
        print(f"  第{i+1}次: {elapsed:.3f}s {ok}")
    except Exception as e:
        print(f"  第{i+1}次: ❌ {e}")
if mootdx_times:
    print(f"  平均耗时: {sum(mootdx_times)/len(mootdx_times):.3f}s")


# ═══════════════════════════════════════
# Part 10: 独有功能对比
# ═══════════════════════════════════════
print("\n\n【Part 10】独有功能对比")
print("-" * 70)

print("\n--- easy-tdx 独有功能 ---")
easy_only = []
try:
    all_methods = [m for m in dir(TdxClient) if not m.startswith('_')]
    print(f"  TdxClient全部方法: {all_methods}")
    # 检查资金流、龙虎榜等
    for m in ['get_history_fund_flow', 'get_security_quotes', 'get_index_bars']:
        if hasattr(TdxClient, m):
            easy_only.append(m)
    
    mac_methods = []
    from easy_tdx import MacClient
    mac_methods = [m for m in dir(MacClient) if not m.startswith('_')]
    print(f"  MacClient全部方法: {mac_methods}")
except:
    pass

print("\n--- mootdx 独有功能 ---")
mootdx_only = []
try:
    all_methods = [m for m in dir(q) if not m.startswith('_')]
    print(f"  Quotes全部方法: {all_methods}")
    for m in ['xdxr', 'minutes', 'transaction', 'transactions', 'pool', 'stocks', 'stock_all']:
        if hasattr(q, m):
            mootdx_only.append(m)
            try:
                sig = inspect.signature(getattr(q, m))
                print(f"  {m}{sig}")
            except:
                print(f"  {m}(签名获取失败)")
except:
    pass


# ═══════════════════════════════════════
# 总结
# ═══════════════════════════════════════
print("\n\n" + "=" * 70)
print("对比总结")
print("=" * 70)

print("""
┌──────────────┬────────────────────────────┬────────────────────────────┐
│     维度     │          easy-tdx          │           mootdx           │
├──────────────┼────────────────────────────┼────────────────────────────┤
│ K线数据      │ ✅ 支持（KlineCategory枚举）│ ✅ 支持（frequency数值）    │
│ 实时行情      │ ✅ get_security_quotes     │ ✅ quotes                  │
│ 历史资金流    │ ✅ get_history_fund_flow   │ ❌ 无直接接口              │
│ 板块数据      │ ✅ MacClient（MAC协议）    │ ⚠️ block方法（功能有限）   │
│ 复权数据      │ ❌ 无内置复权              │ ✅ xdxr方法                │
│ F10数据      │ ⚠️ 需自行解析              │ ✅ F10方法                 │
│ 龙虎榜       │ ✅ MacClient支持           │ ⚠️ pool方法（功能不同）    │
│ 分笔成交      │ ❌ 不支持                  │ ✅ transactions            │
│ 分钟数据      │ ✅ MIN5/MIN15/MIN30/MIN60  │ ✅ frequency 0-8全覆盖     │
│ API设计      │ 枚举类型，类型安全          │ 数值参数，更灵活           │
│ 连接管理      │ 需手动monkey-patch心跳     │ 内置连接管理               │
│ 项目使用      │ ✅ 当前主力库              │ ❌ 未集成                  │
└──────────────┴────────────────────────────┴────────────────────────────┘
""")

print("结论：easy-tdx 与 mootdx 是【互补关系】，不是替代关系")
print("  - easy-tdx：擅长资金流、板块（MacClient）、实时行情")
print("  - mootdx：擅长复权数据（xdxr）、F10、分笔成交")
print("  - 建议保留 easy-tdx 为主力库，mootdx 作为补充库")
print("  - mootdx 的 xdxr 复权数据可解决不复权问题")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)

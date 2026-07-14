#!/usr/bin/env python3
"""mootdx API测试"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mootdx
from mootdx.quotes import Quotes
import inspect

print(f"mootdx版本: {mootdx.__version__}")
print("\nQuotes类属性:")
attrs = [a for a in dir(Quotes) if not a.startswith('_')]
print(f"  {attrs}")

print("\nQuotes类方法签名:")
for name in attrs:
    try:
        obj = getattr(Quotes, name)
        if callable(obj):
            sig = inspect.signature(obj)
            print(f"  {name}{sig}")
    except:
        pass

print("\n--- 测试获取分钟线 ---")
try:
    q = Quotes.factory(market='std')
    print("\nQuotes实例方法:")
    inst_attrs = [a for a in dir(q) if not a.startswith('_')]
    print(f"  {inst_attrs}")
    
    if hasattr(q, 'bars'):
        print(f"\nbars方法签名: {inspect.signature(q.bars)}")
    elif hasattr(q, 'min_bar'):
        print(f"\nmin_bar方法签名: {inspect.signature(q.min_bar)}")
    elif hasattr(q, 'kline'):
        print(f"\nkline方法签名: {inspect.signature(q.kline)}")
    
except Exception as e:
    print(f"初始化Quotes失败: {e}")
    import traceback
    traceback.print_exc()

print("\n--- 测试实际获取K线 ---")
try:
    q = Quotes.factory(market='std')
    
    if hasattr(q, 'kline'):
        print("\n测试kline方法...")
        df = q.kline(symbol='600519', freq='1d', start=0, count=30)
        print(f"日K线返回类型: {type(df).__name__}")
        if df is not None and len(df) > 0:
            print(f"返回行数: {len(df)}")
            print(f"列名: {list(df.columns)}")
            print(f"前5行:\n{df.head()}")
    
    if hasattr(q, 'min_bar'):
        print("\n测试min_bar方法...")
        df = q.min_bar(symbol='600519', freq='5')
        print(f"5分钟K线返回类型: {type(df).__name__}")
        if df is not None and len(df) > 0:
            print(f"返回行数: {len(df)}")
            print(f"列名: {list(df.columns)}")
            print(f"前5行:\n{df.head()}")
            
except Exception as e:
    print(f"获取K线失败: {e}")
    import traceback
    traceback.print_exc()
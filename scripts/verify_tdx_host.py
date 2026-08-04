#!/usr/bin/env python3
"""显式指定 ping 通的服务器取 K 线（验证 easy_tdx 数据可用性）"""
import sys
sys.path.insert(0, r"D:\GitHub\test")

HOSTS = ["111.229.247.189", "150.158.160.2", "180.153.18.170", "124.71.187.122", "115.238.56.198"]
CODE = "600519"

print("=== easy_tdx 显式服务器取日 K ===")
from easy_tdx.client import TdxClient
found = False
for h in HOSTS:
    try:
        c = TdxClient(host=h, port=7709)
        c.connect()
        df = c.get_security_bars(1, CODE, 4, 0, 5)  # SH=1 DAY=4
        if df is not None and len(df) > 0:
            print(f"  [{h}] 成功 {len(df)} 根, 最新 close={df.iloc[-1]['close']}")
            found = True
            c.close()
            break
        else:
            print(f"  [{h}] 返回空")
        c.close()
    except Exception as e:
        print(f"  [{h}] {type(e).__name__}: {str(e)[:60]}")
if not found:
    print("  所有候选服务器均返空（网络环境对 7709 端口整体受限或服务器列表失效）")

print("\n=== mootdx 显式 server 对比 ===")
try:
    from mootdx.quotes import Quotes
    for h in HOSTS[:3]:
        try:
            c = Quotes.factory(market='std', bestip=False, server=(h, 7709))
            df2 = c.bars(symbol=CODE, frequency=9, start=0, offset=5)
            if df2 is not None and len(df2) > 0:
                print(f"  [{h}] 成功 {len(df2)} 根, 最新 close={df2.iloc[-1]['close']}")
                break
            else:
                print(f"  [{h}] 返回空")
        except Exception as e:
            print(f"  [{h}] {type(e).__name__}: {str(e)[:60]}")
except Exception as e:
    print(f"  mootdx 导入/使用失败: {e}")

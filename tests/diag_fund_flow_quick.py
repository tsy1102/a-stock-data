"""
精简诊断：只测最关键的问题
1. 为什么 _get_tdx_client() 返回 None
2. 可用的 TDX 服务器有多少支持历史资金流
3. 东财 push2 接口到底能不能用
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(f"=== 精简诊断 {datetime.now().strftime('%H:%M:%S')} ===")

# ============================================================
# 问题1：_check_tdx 为什么失败
# ============================================================
print(f"\n--- 问题1: _check_tdx 为什么失败 ---")
import socket

# 先看 _check_tdx 源码
import tdx_client
import inspect
source = inspect.getsource(tdx_client._check_tdx)
print(f"_check_tdx 前25行:")
for i, line in enumerate(source.split('\n')[:30]):
    print(f"  {i+1:2d}: {line}")

# 手动测试 _check_tdx 用的 socket 方式
print(f"\n手动测试 socket 连接前8个服务器:")
import re
# 从源码里提取 IP 列表
ips = re.findall(r"'(\d+\.\d+\.\d+\.\d+)'", source)
print(f"从源码提取到 {len(ips)} 个IP")
for i, ip in enumerate(ips[:8]):
    try:
        t0 = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((ip, 7709))
        s.close()
        print(f"  {i+1}. {ip}: ✅ {time.time()-t0:.2f}s")
    except Exception as e:
        print(f"  {i+1}. {ip}: ❌ {str(e)[:40]}")

# ============================================================
# 问题2：测试 10 个服务器，看多少支持历史资金流
# ============================================================
print(f"\n--- 问题2: 多少服务器支持历史资金流 ---")
from easy_tdx import TdxClient
from easy_tdx.config import get_known_hosts

hosts = get_known_hosts()
print(f"总服务器数: {len(hosts)}")

kline_ok = []
hff_ok = []
hff_fail_reasons = {}

for i, host in enumerate(hosts[:15]):
    try:
        client = TdxClient(host=host, port=7709)
        client.connect()
    except Exception:
        print(f"  {i+1:2d}. {host:18s} ❌ 连不上")
        continue
    
    # 测试K线
    try:
        from easy_tdx import KlineCategory, Market
        bars = client.get_security_bars(Market.SH, "600519", KlineCategory.DAY, 0, 3)
        kline_good = bars is not None and not bars.empty and len(bars) >= 2
    except Exception:
        kline_good = False
    
    if kline_good:
        kline_ok.append(host)
    
    # 测试历史资金流
    try:
        df = client.get_history_fund_flow(1, "600519", 0, 30)
        hff_good = df is not None and not df.empty and len(df) >= 20
        if hff_good:
            hff_ok.append(host)
            status = "✅"
        else:
            status = f"⚠️({len(df) if df is not None and not df.empty else 0}条)"
    except Exception as e:
        hff_good = False
        err = type(e).__name__
        hff_fail_reasons[err] = hff_fail_reasons.get(err, 0) + 1
        status = f"❌{err[:12]}"
    
    kline_status = "✅K线" if kline_good else "❌K线"
    print(f"  {i+1:2d}. {host:18s} {kline_status} {status}")
    
    try:
        client.close()
    except Exception:
        pass
    time.sleep(0.1)

print(f"\nK线正常: {len(kline_ok)} 台")
print(f"历史资金流正常: {len(hff_ok)} 台: {hff_ok}")
if hff_fail_reasons:
    print(f"历史资金流失败原因分布: {hff_fail_reasons}")

# ============================================================
# 问题3：东财 push2 接口测试
# ============================================================
print(f"\n--- 问题3: 东财 push2 接口 ---")
import requests
session = requests.Session()
session.trust_env = False

# 用 push2.eastmoney.com 的 stock/get 是能用的，试试其他 push2 路径
test_cases = [
    ("push2 stock/get (已知可用)", "https://push2.eastmoney.com/api/qt/stock/get",
     {"secid": "1.600519", "fields": "f43,f57,f58"}),
    ("push2 fflow/daykline", "https://push2.eastmoney.com/api/qt/stock/fflow/daykline/get",
     {"secid": "1.600519", "klt": 101, "fields1": "f1,f2,f3,f7", "fields2": "f51,f52,f53,f54,f55,f56,f57"}),
    ("push2his fflow/daykline", "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get",
     {"secid": "1.600519", "klt": 101, "fields1": "f1,f2,f3,f7", "fields2": "f51,f52,f53,f54,f55,f56,f57"}),
    ("push2 clist", "https://push2.eastmoney.com/api/qt/clist/get",
     {"pn": 1, "pz": 3, "po": 1, "np": 1, "fltt": 2, "invt": 2, "fid": "f3", "fs": "m:0+t:6", "fields": "f2,f3,f12,f14"}),
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

for name, url, params in test_cases:
    try:
        t0 = time.time()
        r = session.get(url, params=params, headers=headers, timeout=8)
        dt = time.time() - t0
        size = len(r.content)
        status = f"HTTP{r.status_code}"
        
        # 看看有没有数据
        has_data = False
        if r.status_code == 200:
            try:
                d = r.json()
                if d.get('data') and (isinstance(d['data'], dict) and len(d['data']) > 0 or isinstance(d['data'], list) and len(d['data']) > 0):
                    has_data = True
                    if isinstance(d['data'], dict):
                        klines = d['data'].get('klines', [])
                        if klines:
                            status += f" ✅klines={len(klines)}"
                        else:
                            status += f" ✅data有{len(d['data'])}个key"
                    else:
                        status += f" ✅list={len(d['data'])}"
                else:
                    status += f" ⚠️data空"
            except Exception:
                status += f" ⚠️非JSON"
        
        print(f"  {name}: {status} ({size}B, {dt:.2f}s)")
    except Exception as e:
        print(f"  {name}: ❌{type(e).__name__}")

print(f"\n=== 诊断结束 ===")

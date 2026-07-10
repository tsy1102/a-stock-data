"""
验证修复效果：测试资金流数据获取
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(f"=== 修复验证 {datetime.now().strftime('%H:%M:%S')} ===")

# 测试1：预扫描是否生效
print(f"\n--- 测试1: 预扫描 ---")
from tdx_client import _pre_scan_tdx_hosts, _debug_log, cleanup_tdx

cleanup_tdx()

# 删除旧缓存，强制重新扫描
cache_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache", "tdx_hosts_cache.json")
if os.path.exists(cache_file):
    os.remove(cache_file)
    print(f"  已删除旧缓存")

start = time.time()
good_hosts = _pre_scan_tdx_hosts()
elapsed = time.time() - start
print(f"  预扫描完成，找到 {len(good_hosts)} 台可用服务器，耗时 {elapsed:.1f}s")
if good_hosts:
    print(f"  可用服务器: {good_hosts}")

# 测试2：获取TDX客户端
print(f"\n--- 测试2: 获取TDX客户端 ---")
from tdx_client import _get_tdx_client
client = _get_tdx_client()
print(f"  客户端: {'成功' if client else '失败'}")
if client:
    print(f"  主机: {client._host}")

# 测试3：获取历史资金流
print(f"\n--- 测试3: 获取历史资金流 ---")
from tdx_client import tdx_get_history_fund_flow

test_stocks = [
    ("600519", "贵州茅台"),
    ("000100", "TCL科技"),
    ("300750", "宁德时代"),
    ("688981", "中芯国际"),
    ("000977", "浪潮信息"),
]

for code, name in test_stocks:
    start = time.time()
    data = tdx_get_history_fund_flow(code, 60)
    elapsed = time.time() - start
    count = len(data)
    status = "✅" if count >= 50 else "⚠️" if count > 0 else "❌"
    print(f"  {status} {code} {name}: {count} 条, 耗时 {elapsed:.2f}s")
    if data:
        print(f"    首条日期: {data[0].get('date', 'N/A')}, 末条日期: {data[-1].get('date', 'N/A')}")

# 测试4：调用sht报告的资金流函数
print(f"\n--- 测试4: sht报告资金流函数 ---")
from get_sht_report import get_fund_flow_120d

for code, name in test_stocks:
    start = time.time()
    result = get_fund_flow_120d(code)
    elapsed = time.time() - start
    data = result.get("data", [])
    error = result.get("error", "")
    source = result.get("source", "")
    count = len(data)
    status = "✅" if count >= 50 else "⚠️" if count > 0 else "❌"
    print(f"  {status} {code} {name}: {count} 条, 来源: {source}, 错误: {error}, 耗时 {elapsed:.2f}s")

cleanup_tdx()
print(f"\n=== 验证完成 ===")

"""
诊断第4轮：核心问题定位
1. TDX 客户端自动选择的是哪个服务器？是否支持历史资金流？
2. TDX 健康检查是否包含历史资金流校验？
3. 东财 push2his 接口的问题
4. tdx_get_history_fund_flow 为什么返回空（是连接问题还是解码错误被吞了？）
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(f"{'='*70}")
print(f"  诊断第4轮：核心问题定位  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}")


# ============================================================
# 第一部分：追踪 tdx_get_history_fund_flow 的实际调用路径
# ============================================================
print(f"\n{'='*70}")
print(f"  【第一部分】追踪 tdx_get_history_fund_flow 调用路径")
print(f"{'='*70}")

# 先检查装饰器和缓存
import inspect
from tdx_client import tdx_get_history_fund_flow, _get_tdx_client, cleanup_tdx

print(f"\n  1. tdx_get_history_fund_flow 函数信息:")
print(f"     函数对象: {tdx_get_history_fund_flow}")
print(f"     函数名: {tdx_get_history_fund_flow.__name__}")
print(f"     有装饰器包装: {hasattr(tdx_get_history_fund_flow, '__wrapped__')}")

# 看源码（部分）
try:
    source = inspect.getsource(tdx_get_history_fund_flow)
    print(f"\n  2. 函数源码前30行:")
    lines = source.split('\n')[:30]
    for i, line in enumerate(lines):
        print(f"    {i+1:2d}: {line}")
except Exception as e:
    print(f"  获取源码失败: {e}")

print(f"\n  3. 直接调用 tdx_get_history_fund_flow (带缓存):")
t0 = time.time()
result = tdx_get_history_fund_flow("600519", 60)
elapsed = time.time() - t0
print(f"     返回: {len(result)} 条数据, 耗时 {elapsed:.2f}s")
if result:
    print(f"     首条: {result[0]}")
    print(f"     末条: {result[-1]}")

print(f"\n  4. 设置 STOCK_NOCACHE 绕过缓存调用:")
os.environ["STOCK_NOCACHE"] = "1"
# 重新导入可能不行，直接手动测试底层
from tdx_client import _TDX_CALL_LOCK, _market_from_code

# 手动模拟 tdx_get_history_fund_flow 的核心逻辑
print(f"     手动调用底层逻辑:")
with _TDX_CALL_LOCK:
    client = _get_tdx_client()
    print(f"     客户端: {client}")
    if client is not None:
        print(f"     客户端 host: {client._host if hasattr(client, '_host') else 'N/A'}")
        print(f"     客户端 port: {client._port if hasattr(client, '_port') else 'N/A'}")
        
        # 测试实时资金流
        try:
            df_ff = client.get_fund_flow(_market_from_code("600519"), "600519")
            print(f"     实时资金流: {len(df_ff) if df_ff is not None and not df_ff.empty else 0} 条")
        except Exception as e:
            print(f"     实时资金流异常: {type(e).__name__}: {e}")
        
        # 测试历史资金流
        try:
            t0 = time.time()
            df_hff = client.get_history_fund_flow(_market_from_code("600519"), "600519", 0, 60)
            elapsed = time.time() - t0
            count = len(df_hff) if df_hff is not None and not df_hff.empty else 0
            print(f"     历史资金流: {count} 条, 耗时 {elapsed:.2f}s")
            if count > 0:
                print(f"       列: {list(df_hff.columns)}")
        except Exception as e:
            print(f"     历史资金流异常: {type(e).__name__}: {e}")

cleanup_tdx()
del os.environ["STOCK_NOCACHE"]


# ============================================================
# 第二部分：检查 TDX 服务器选择逻辑
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第二部分】TDX 服务器选择逻辑分析")
print(f"{'='*70}")

# 读取 _get_tdx_client 源码
from tdx_client import _get_tdx_client
print(f"\n  1. _get_tdx_client 源码:")
try:
    source = inspect.getsource(_get_tdx_client)
    lines = source.split('\n')
    for i, line in enumerate(lines):
        print(f"    {i+1:2d}: {line}")
except Exception as e:
    print(f"  获取失败: {e}")

# 检查 from_best_host
print(f"\n  2. 检查 from_best_host 逻辑:")
try:
    from easy_tdx import TdxClient
    # 看看 TdxClient.from_best_host 方法
    if hasattr(TdxClient, 'from_best_host'):
        source = inspect.getsource(TdxClient.from_best_host)
        lines = source.split('\n')[:40]
        for i, line in enumerate(lines):
            print(f"    {i+1:2d}: {line}")
except Exception as e:
    print(f"  获取失败: {e}")

# 检查 tdx_client.py 中的健康检查是否包含历史资金流
print(f"\n  3. 检查 tdx_client.py 健康检查:")
import tdx_client
source_file = inspect.getfile(tdx_client)
print(f"  源码文件: {source_file}")

# 搜索健康检查相关的代码
with open(source_file, 'r', encoding='utf-8') as f:
    content = f.read()
    
# 查找健康检查函数
import re
health_check_match = re.search(r'def (_check_tdx.*?|.*health.*?)\(.*?\).*?:', content)
if health_check_match:
    print(f"  找到健康检查相关函数: {health_check_match.group(0)}")


# ============================================================
# 第三部分：东财 push2his 接口深度分析
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第三部分】东财 push2his 接口深度分析")
print(f"{'='*70}")

import requests
TEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://quote.eastmoney.com/",
    "Accept": "application/json, text/plain, */*",
}

session = requests.Session()
session.trust_env = False

# 测试不同域名的同一个接口
domains = [
    "push2his.eastmoney.com",
    "push2.eastmoney.com",
    "data.eastmoney.com",
    "emweb.securities.eastmoney.com",
]

endpoint = "/api/qt/stock/fflow/daykline/get"
params = {
    "secid": "1.600519",
    "klt": 101,
    "fields1": "f1,f2,f3,f7",
    "fields2": "f51,f52,f53,f54,f55,f56,f57",
}

print(f"\n  测试不同域名的资金流接口:")
for domain in domains:
    url = f"https://{domain}{endpoint}"
    try:
        t0 = time.time()
        r = session.get(url, params=params, headers=TEST_HEADERS, timeout=10)
        elapsed = time.time() - t0
        print(f"\n  {domain}:")
        print(f"    HTTP {r.status_code}, {len(r.content)} bytes, {elapsed:.2f}s")
        if r.status_code == 200:
            try:
                d = r.json()
                data = d.get("data", {})
                klines = data.get("klines", []) if data else []
                print(f"    klines: {len(klines)} 条")
                if klines:
                    print(f"    首条: {klines[0]}")
                else:
                    print(f"    完整响应前500字: {str(d)[:500]}")
            except Exception as je:
                print(f"    JSON解析失败: {je}")
                print(f"    响应文本前300字: {r.text[:300]}")
    except Exception as e:
        print(f"\n  {domain}: ❌ {type(e).__name__}: {str(e)[:80]}")

# 测试 data.eastmoney.com 的资金流页面（看看有没有其他API）
print(f"\n  测试 data.eastmoney.com 资金流相关API:")
data_em_urls = [
    ("zjlx 列表", "https://data.eastmoney.com/zjlx/list.html", {}),
    ("zjlx detail", "https://data.eastmoney.com/zjlx/600519.html", {}),
]
# 尝试 data 接口
data_api_url = "https://data.eastmoney.com/dataapi/zlsj/zjlx"
print(f"\n  尝试 data.eastmoney.com dataapi:")
try:
    r = session.get("https://data.eastmoney.com/dataapi/zlsj/zjlx/zjlrxq", 
                    params={"code": "600519", "market": "SH", "page": "1", "pageSize": "60"},
                    headers=TEST_HEADERS, timeout=10)
    print(f"    dataapi zjlrxq: HTTP {r.status_code}, {len(r.content)} bytes")
    if r.status_code == 200:
        print(f"    响应前500字: {r.text[:500]}")
except Exception as e:
    print(f"    ❌ {type(e).__name__}: {e}")


# ============================================================
# 第四部分：缓存分类名检查
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第四部分】缓存分类与装饰器检查")
print(f"{'='*70}")

import sqlite3
cache_db = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache", "stock_cache.db")

if os.path.exists(cache_db):
    conn = sqlite3.connect(cache_db)
    cur = conn.cursor()
    
    # 看看 key 里有没有和资金相关的
    print(f"\n  1. 搜索 key 中包含 'fund' 或 'flow' 或 '资金' 的缓存:")
    cur.execute("SELECT key, length(value) FROM cache_entries WHERE key LIKE '%fund%' OR key LIKE '%flow%' LIMIT 20")
    rows = cur.fetchall()
    print(f"  找到 {len(rows)} 条:")
    for key, vlen in rows:
        print(f"    {key[:80]} ({vlen} bytes)")
    
    # 看看所有 key 的前缀（分类可能编码在 key 里）
    print(f"\n  2. 抽样查看缓存 key 格式:")
    cur.execute("SELECT key FROM cache_entries LIMIT 20")
    rows = cur.fetchall()
    for i, (key,) in enumerate(rows):
        print(f"    {i+1:2d}. {key[:100]}")
    
    # 检查 key 的结构规律
    print(f"\n  3. 统计不同前缀的 key:")
    cur.execute("SELECT key FROM cache_entries LIMIT 500")
    rows = cur.fetchall()
    prefixes = {}
    for (key,) in rows:
        # 取第一个冒号前的部分作为前缀
        prefix = key.split(':')[0] if ':' in key else key[:20]
        prefixes[prefix] = prefixes.get(prefix, 0) + 1
    for prefix, count in sorted(prefixes.items(), key=lambda x: -x[1]):
        print(f"    {prefix}: {count} 条")
    
    conn.close()

# 检查 cached 装饰器的使用
print(f"\n  4. 检查 tdx_get_history_fund_flow 的装饰器:")
from stock_cache import cached
# 看函数的 __wrapped__ 或者其他属性
print(f"     函数: {tdx_get_history_fund_flow}")
print(f"     类型: {type(tdx_get_history_fund_flow).__name__}")
if hasattr(tdx_get_history_fund_flow, '__closure__'):
    print(f"     closure 变量:")
    if tdx_get_history_fund_flow.__closure__:
        for i, cell in enumerate(tdx_get_history_fund_flow.__closure__):
            try:
                val = cell.cell_contents
                print(f"       [{i}]: {type(val).__name__} = {str(val)[:80]}")
            except ValueError:
                print(f"       [{i}]: <empty>")


print(f"\n\n{'='*70}")
print(f"  第4轮诊断完成！")
print(f"{'='*70}")

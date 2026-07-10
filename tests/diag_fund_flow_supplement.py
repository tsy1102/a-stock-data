"""
补充诊断：代理环境、TDX连接详情、缓存数据检查
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(f"{'='*70}")
print(f"  补充诊断：代理/TDX/缓存  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}")

# ============================================================
# 第一部分：代理环境检查
# ============================================================
print(f"\n{'='*70}")
print(f"  【第一部分】代理环境检查")
print(f"{'='*70}")

import os
print(f"\n  环境变量中的代理设置:")
for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy']:
    val = os.environ.get(key, '')
    if val:
        print(f"    {key} = {val}")
    else:
        print(f"    {key} = (未设置)")

# 测试不使用代理的请求
print(f"\n  测试绕过代理直接请求东财接口:")
import requests
EM_URL = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
TEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://quote.eastmoney.com/",
}
params = {
    "secid": "1.600519",
    "klt": 101,
    "fields1": "f1,f2,f3,f7",
    "fields2": "f51,f52,f53,f54,f55,f56,f57",
}

# 方法1: 使用 proxies=None
print(f"\n  方法1: proxies=None (强制不使用代理):")
try:
    t0 = time.time()
    r = requests.get(EM_URL, params=params, headers=TEST_HEADERS, timeout=15, proxies=None)
    elapsed = time.time() - t0
    print(f"    HTTP {r.status_code}, {elapsed:.2f}s, {len(r.content)} bytes")
    if r.status_code == 200:
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        print(f"    klines数量: {len(klines)}")
        if klines:
            print(f"    首条: {klines[0]}")
            print(f"    末条日期: {klines[-1].split(',')[0]}")
except Exception as e:
    print(f"    ❌ 异常: {type(e).__name__}: {e}")

# 方法2: 设置 trust_env=False
print(f"\n  方法2: trust_env=False (忽略环境变量代理):")
try:
    session = requests.Session()
    session.trust_env = False
    t0 = time.time()
    r = session.get(EM_URL, params=params, headers=TEST_HEADERS, timeout=15)
    elapsed = time.time() - t0
    print(f"    HTTP {r.status_code}, {elapsed:.2f}s, {len(r.content)} bytes")
    if r.status_code == 200:
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        print(f"    klines数量: {len(klines)}")
        if klines:
            print(f"    首条: {klines[0]}")
            print(f"    末条日期: {klines[-1].split(',')[0]}")
except Exception as e:
    print(f"    ❌ 异常: {type(e).__name__}: {e}")

# 方法3: 测试其他东财域名是否可用
print(f"\n  测试其他东财相关接口:")
test_urls = [
    ("push2.eastmoney.com", "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6&fields=f2,f3,f12,f14"),
    ("quote.eastmoney.com", "https://quote.eastmoney.com/sh600519.html"),
    ("data.eastmoney.com", "https://data.eastmoney.com/zjlx/600519.html"),
    ("emweb.securities.eastmoney.com", "https://emweb.securities.eastmoney.com/PC_HSF10/OperationsRequired/Index?type=web&code=SH600519"),
]

for name, url in test_urls:
    try:
        t0 = time.time()
        r = requests.get(url, headers=TEST_HEADERS, timeout=10, proxies=None)
        elapsed = time.time() - t0
        print(f"    {name}: HTTP {r.status_code}, {elapsed:.2f}s, {len(r.content)} bytes")
    except Exception as e:
        print(f"    {name}: ❌ {type(e).__name__}: {str(e)[:50]}")


# ============================================================
# 第二部分：TDX 连接深度诊断
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第二部分】TDX 连接深度诊断")
print(f"{'='*70}")

# 手动测试 TDX 服务器连接
print(f"\n  手动测试 TDX 服务器 TCP 连接 (端口 7709):")
from easy_tdx.config import get_known_hosts
hosts = get_known_hosts()
print(f"  共 {len(hosts)} 个服务器，测试前 10 个:")

import socket
good_hosts = []
for i, host in enumerate(hosts[:10]):
    try:
        t0 = time.time()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((host, 7709))
        s.close()
        elapsed = time.time() - t0
        print(f"    {i+1}. {host}: ✅ 连通 ({elapsed:.2f}s)")
        good_hosts.append(host)
    except Exception as e:
        print(f"    {i+1}. {host}: ❌ {str(e)[:40]}")

print(f"\n  前10个中可用: {len(good_hosts)} 个")

# 用第一个可用服务器手动连接测试
if good_hosts:
    print(f"\n  使用 {good_hosts[0]} 手动连接测试:")
    try:
        from easy_tdx import TdxClient
        client = TdxClient(host=good_hosts[0], port=7709)
        client.connect()
        print(f"    ✅ 连接成功")
        
        # 测试行情接口
        try:
            df = client.get_security_bars(9, 1, "600519", 0, 5)
            print(f"    get_security_bars: {len(df) if df is not None and not df.empty else 0} 条")
        except Exception as e:
            print(f"    get_security_bars 异常: {type(e).__name__}: {e}")
        
        # 测试实时资金流
        try:
            df_ff = client.get_fund_flow(1, "600519")
            if df_ff is not None and not df_ff.empty:
                print(f"    get_fund_flow: ✅ {len(df_ff)} 条, 列={list(df_ff.columns)}")
            else:
                print(f"    get_fund_flow: ⚠️  空数据")
        except Exception as e:
            print(f"    get_fund_flow 异常: {type(e).__name__}: {e}")
        
        # 测试历史资金流
        try:
            df_hff = client.get_history_fund_flow(1, "600519", 0, 60)
            if df_hff is not None and not df_hff.empty:
                print(f"    get_history_fund_flow: ✅ {len(df_hff)} 条")
                print(f"      列名: {list(df_hff.columns)}")
                print(f"      首条: {df_hff.iloc[0].to_dict()}")
                print(f"      末条: {df_hff.iloc[-1].to_dict()}")
            else:
                print(f"    get_history_fund_flow: ⚠️  空数据 (df={'None' if df_hff is None else 'empty'})")
        except Exception as e:
            print(f"    get_history_fund_flow 异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        # 测试不同市场的股票
        print(f"\n  测试不同市场股票的历史资金流:")
        test_cases = [
            ("600519", 1, "沪市主板"),
            ("000100", 0, "深市主板"),
            ("300750", 0, "创业板"),
            ("688981", 1, "科创板"),
            ("000977", 0, "深市主板"),
        ]
        for code, market, desc in test_cases:
            try:
                df = client.get_history_fund_flow(market, code, 0, 60)
                count = len(df) if df is not None and not df.empty else 0
                status = "✅" if count > 0 else "❌"
                print(f"    {status} {code} ({desc}): {count} 条")
            except Exception as e:
                print(f"    ❌ {code} ({desc}): {type(e).__name__}: {e}")
        
        client.close()
    except Exception as e:
        print(f"    ❌ 连接失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


# ============================================================
# 第三部分：缓存深度检查
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第三部分】缓存深度检查")
print(f"{'='*70}")

import sqlite3
cache_db = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache", "stock_cache.db")

if os.path.exists(cache_db):
    conn = sqlite3.connect(cache_db)
    cur = conn.cursor()
    
    # 查表结构
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print(f"\n  缓存表: {tables}")
    
    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        cols = cur.fetchall()
        print(f"\n  {table} 表结构:")
        for col in cols:
            print(f"    {col[1]} ({col[2]})")
        
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        total = cur.fetchone()[0]
        print(f"  总记录数: {total}")
    
    # 查找资金流相关缓存
    if "cache_entries" in tables:
        print(f"\n  查找资金流相关缓存:")
        cur.execute("SELECT category, COUNT(*) FROM cache_entries GROUP BY category")
        cats = cur.fetchall()
        print(f"  所有分类:")
        for cat, cnt in cats:
            print(f"    {cat}: {cnt} 条")
        
        # 查 f10_fund_flow 分类详情
        cur.execute("SELECT key, created_at, expires_at FROM cache_entries WHERE category='f10_fund_flow' LIMIT 10")
        rows = cur.fetchall()
        print(f"\n  f10_fund_flow 样本 ({len(rows)} 条):")
        for key, created, expires in rows:
            print(f"    key={key}, created={created}, expires={expires}")
    
    conn.close()
else:
    print(f"  缓存文件不存在")


print(f"\n\n{'='*70}")
print(f"  补充诊断完成！")
print(f"{'='*70}")

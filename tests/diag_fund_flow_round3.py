"""
深度诊断第3轮：
1. push2.eastmoney.com 返回的393字节到底是什么
2. TDX 哪些服务器支持 get_history_fund_flow（逐台测试）
3. 缓存中的资金流数据详情
4. 检查 pytdx 原生库是否可用
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(f"{'='*70}")
print(f"  深度诊断第3轮  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}")


# ============================================================
# 第一部分：push2.eastmoney.com 返回内容分析
# ============================================================
print(f"\n{'='*70}")
print(f"  【第一部分】push2.eastmoney.com 返回内容深度分析")
print(f"{'='*70}")

import requests
TEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

# 测试多个 push2 接口
test_urls = [
    ("push2his fflow", "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get", {
        "secid": "1.600519", "klt": 101,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }),
    ("push2 clist", "https://push2.eastmoney.com/api/qt/clist/get", {
        "pn": 1, "pz": 5, "po": 1, "np": 1, "fltt": 2, "invt": 2,
        "fid": "f3", "fs": "m:0+t:6", "fields": "f2,f3,f12,f14",
    }),
    ("push2 stock/get", "https://push2.eastmoney.com/api/qt/stock/get", {
        "secid": "1.600519",
        "fields": "f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f60,f107,f116,f117,f162,f167,f168,f169,f170,f171",
    }),
]

for name, url, params in test_urls:
    print(f"\n  --- {name} ---")
    try:
        session = requests.Session()
        session.trust_env = False
        r = session.get(url, params=params, headers=TEST_HEADERS, timeout=15)
        print(f"    HTTP {r.status_code}, {len(r.content)} bytes")
        print(f"    Content-Type: {r.headers.get('Content-Type', 'N/A')}")
        print(f"    完整响应文本:")
        print(f"    {r.text[:800]}")
        if len(r.text) > 800:
            print(f"    ... (共 {len(r.text)} 字符)")
    except Exception as e:
        print(f"    ❌ 异常: {type(e).__name__}: {e}")


# ============================================================
# 第二部分：逐台测试 TDX 服务器的历史资金流接口
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第二部分】逐台测试 TDX 服务器的历史资金流支持")
print(f"{'='*70}")

from easy_tdx.config import get_known_hosts
from easy_tdx import TdxClient

hosts = get_known_hosts()
print(f"\n  共 {len(hosts)} 个服务器，逐一测试 get_history_fund_flow:")

good_fflow_hosts = []
bad_fflow_hosts = []

for i, host in enumerate(hosts[:20]):  # 测试前20个
    try:
        client = TdxClient(host=host, port=7709)
        client.connect()
        
        # 先测试K线是否正常（排除假数据服务器）
        try:
            df_kline = client.get_security_bars(9, 1, "600519", 0, 5)
            kline_ok = df_kline is not None and not df_kline.empty and len(df_kline) >= 5
        except Exception:
            kline_ok = False
        
        # 测试实时资金流
        try:
            df_ff = client.get_fund_flow(1, "600519")
            ff_ok = df_ff is not None and not df_ff.empty
        except Exception:
            ff_ok = False
        
        # 测试历史资金流
        try:
            df_hff = client.get_history_fund_flow(1, "600519", 0, 10)
            hff_ok = df_hff is not None and not df_hff.empty and len(df_hff) >= 3
            hff_count = len(df_hff) if df_hff is not None and not df_hff.empty else 0
        except Exception as e:
            hff_ok = False
            hff_count = 0
            hff_err = type(e).__name__
        
        status = "✅" if hff_ok else "❌"
        kline_status = "✅" if kline_ok else "⚠️"
        ff_status = "✅" if ff_ok else "⚠️"
        
        info = f"K线{kline_status} 实时FF{ff_status} 历史FF{status}"
        if hff_ok:
            info += f" ({hff_count}条)"
            good_fflow_hosts.append(host)
        else:
            info += f" (err: {hff_err if 'hff_err' in dir() else 'empty'})"
            bad_fflow_hosts.append((host, hff_err if 'hff_err' in dir() else 'empty'))
        
        print(f"  {i+1:2d}. {host:18s} {info}")
        
        client.close()
    except Exception as e:
        print(f"  {i+1:2d}. {host:18s} ❌ 连接失败: {type(e).__name__}")
        bad_fflow_hosts.append((host, f"connect: {type(e).__name__}"))
    
    time.sleep(0.2)

print(f"\n  历史资金流可用服务器: {len(good_fflow_hosts)} 个")
if good_fflow_hosts:
    print(f"  列表: {good_fflow_hosts}")

# 用第一个好的服务器测试更多股票
if good_fflow_hosts:
    print(f"\n  用 {good_fflow_hosts[0]} 测试多只股票的历史资金流:")
    try:
        client = TdxClient(host=good_fflow_hosts[0], port=7709)
        client.connect()
        
        test_cases = [
            ("600519", 1, "贵州茅台"),
            ("000100", 0, "TCL科技"),
            ("300750", 0, "宁德时代"),
            ("688981", 1, "中芯国际"),
            ("000977", 0, "浪潮信息"),
            ("600036", 1, "招商银行"),
        ]
        
        for code, market, name in test_cases:
            try:
                df = client.get_history_fund_flow(market, code, 0, 60)
                count = len(df) if df is not None and not df.empty else 0
                if count > 0:
                    cols = list(df.columns)
                    first_date = df.iloc[0].get('date', 'N/A')
                    last_date = df.iloc[-1].get('date', 'N/A')
                    print(f"    ✅ {code} {name}: {count}条, 列={cols}, 日期={first_date}~{last_date}")
                else:
                    print(f"    ❌ {code} {name}: 空数据")
            except Exception as e:
                print(f"    ❌ {code} {name}: {type(e).__name__}: {e}")
        
        client.close()
    except Exception as e:
        print(f"  连接失败: {e}")


# ============================================================
# 第三部分：pytdx 原生库测试
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第三部分】pytdx 原生库测试（对比 easy_tdx）")
print(f"{'='*70}")

try:
    from pytdx.hq import TdxHq_API
    print(f"  pytdx 可用")
    
    if good_fflow_hosts:
        host = good_fflow_hosts[0]
        print(f"  连接 {host}:7709 ...")
        api = TdxHq_API()
        if api.connect(host, 7709):
            print(f"  ✅ 连接成功")
            
            # 测试获取历史资金流
            try:
                # pytdx 的历史资金流接口
                data = api.get_history_fund_flow(1, "600519", 0, 60)
                if data:
                    print(f"  ✅ get_history_fund_flow 返回 {len(data)} 条")
                    print(f"  样本: {data[0] if data else '无'}")
                else:
                    print(f"  ⚠️  get_history_fund_flow 返回空")
            except Exception as e:
                print(f"  ❌ get_history_fund_flow 异常: {type(e).__name__}: {e}")
            
            api.disconnect()
        else:
            print(f"  ❌ 连接失败")
except ImportError:
    print(f"  pytdx 未安装")


# ============================================================
# 第四部分：缓存资金流数据详情
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第四部分】缓存中的资金流数据详情")
print(f"{'='*70}")

import sqlite3
import pickle
cache_db = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache", "stock_cache.db")

if os.path.exists(cache_db):
    conn = sqlite3.connect(cache_db)
    cur = conn.cursor()
    
    # 用 LIKE 查找 fund_flow 相关的 key
    cur.execute("SELECT key, created_at, expires_at, length(value) as val_len FROM cache_entries WHERE key LIKE '%fund_flow%' LIMIT 20")
    rows = cur.fetchall()
    print(f"\n  包含 'fund_flow' 的缓存条目: {len(rows)} 条")
    for key, created, expires, val_len in rows:
        created_str = datetime.fromtimestamp(created).strftime('%Y-%m-%d %H:%M') if created else 'N/A'
        expires_str = datetime.fromtimestamp(expires).strftime('%Y-%m-%d %H:%M') if expires else 'N/A'
        is_expired = "已过期" if expires and expires < time.time() else "有效"
        print(f"    key: {key[:80]}")
        print(f"      value大小: {val_len} bytes, 创建: {created_str}, 过期: {expires_str} [{is_expired}]")
    
    # 取第一条解析看看内容
    if rows:
        cur.execute("SELECT key, value FROM cache_entries WHERE key LIKE '%fund_flow%' LIMIT 1")
        row = cur.fetchone()
        if row:
            key, value_blob = row
            print(f"\n  第一条缓存内容解析 ({key}):")
            try:
                data = pickle.loads(value_blob)
                print(f"    类型: {type(data).__name__}")
                if isinstance(data, list):
                    print(f"    列表长度: {len(data)}")
                    if data:
                        print(f"    首元素: {data[0]}")
                        print(f"    末元素: {data[-1]}")
                elif isinstance(data, dict):
                    print(f"    字典keys: {list(data.keys())[:10]}")
                else:
                    print(f"    值: {str(data)[:200]}")
            except Exception as e:
                print(f"    解析失败: {e}")
                print(f"    原始数据前100字节: {value_blob[:100]}")
    
    conn.close()


print(f"\n\n{'='*70}")
print(f"  第3轮诊断完成！")
print(f"{'='*70}")

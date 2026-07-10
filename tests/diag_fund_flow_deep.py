"""
资金流数据深度诊断脚本
逐层排查 TDX 和东财接口的问题：
1. TDX 层：连接状态、客户端实例、原始 API 返回、错误详情
2. 东财层：直接 HTTP 请求、多域名测试、返回格式分析
3. 缓存层：检查是否缓存了空数据
4. 批量场景：模拟连续请求测试稳定性
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(f"{'='*70}")
print(f"  资金流深度诊断  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}")


# ============================================================
# 第一部分：TDX 深度诊断
# ============================================================
print(f"\n{'='*70}")
print(f"  【第一部分】TDX 接口深度诊断")
print(f"{'='*70}")

from tdx_client import (_get_tdx_client, _market_from_code, _TDX_BAD_HOSTS,
                         cleanup_tdx, _debug_log as tdx_debug_log)

print(f"\n  1. TDX 服务器列表:")
try:
    from easy_tdx.config import get_known_hosts
    _all_hosts = get_known_hosts()
    print(f"     easy_tdx 已知主机: {len(_all_hosts)} 个")
    print(f"     前5个: {_all_hosts[:5]}")
    print(f"     坏主机黑名单: {len(_TDX_BAD_HOSTS)} 个")
except Exception as e:
    print(f"     获取主机列表失败: {e}")

print(f"\n  2. 获取 TDX 客户端实例:")
client = _get_tdx_client()
if client is None:
    print(f"     ❌ 客户端为 None，连接失败")
else:
    print(f"     ✅ 客户端已获取: {type(client).__name__}")
    print(f"     客户端地址: {client._host if hasattr(client, '_host') else '未知'}")
    
    print(f"\n  3. 测试基础行情接口（验证连接是否正常）:")
    try:
        from pytdx.hq import TdxHq_API
        df = client.get_security_bars(9, 1, "600519", 0, 5)
        if df is not None and not df.empty:
            print(f"     ✅ K线接口正常，返回 {len(df)} 条数据")
            print(f"     样本: {df.iloc[0].to_dict() if len(df) > 0 else '无'}")
        else:
            print(f"     ❌ K线接口返回空数据")
    except Exception as e:
        print(f"     ❌ K线接口异常: {type(e).__name__}: {e}")

    print(f"\n  4. 测试实时资金流接口 get_fund_flow:")
    try:
        df_ff = client.get_fund_flow(1, "600519")
        if df_ff is not None and not df_ff.empty:
            print(f"     ✅ 实时资金流正常，返回 {len(df_ff)} 条数据")
            print(f"     列名: {list(df_ff.columns)}")
            print(f"     样本: {df_ff.iloc[0].to_dict() if len(df_ff) > 0 else '无'}")
        else:
            print(f"     ⚠️  实时资金流返回空 (df={'None' if df_ff is None else 'empty'})")
    except Exception as e:
        print(f"     ❌ 实时资金流异常: {type(e).__name__}: {e}")

    print(f"\n  5. 测试历史资金流接口 get_history_fund_flow (原始调用):")
    test_cases = [
        ("600519", 1, "沪市主板"),
        ("000100", 0, "深市主板"),
        ("300750", 0, "创业板"),
        ("688981", 1, "科创板"),
    ]
    for code, market, desc in test_cases:
        try:
            t0 = time.time()
            df_hff = client.get_history_fund_flow(market, code, 0, 60)
            elapsed = time.time() - t0
            if df_hff is not None and not df_hff.empty:
                print(f"     ✅ {code} ({desc}): {len(df_hff)} 条, {elapsed:.2f}s")
                print(f"        列名: {list(df_hff.columns)}")
                if len(df_hff) > 0:
                    print(f"        首条: {df_hff.iloc[0].to_dict()}")
                    print(f"        末条: {df_hff.iloc[-1].to_dict()}")
            else:
                print(f"     ❌ {code} ({desc}): 空数据 (df={'None' if df_hff is None else 'empty'}), {elapsed:.2f}s")
        except Exception as e:
            print(f"     ❌ {code} ({desc}): 异常 {type(e).__name__}: {e}")

    print(f"\n  6. 测试不同数量的历史资金流:")
    for n in [10, 30, 60, 120]:
        try:
            df_test = client.get_history_fund_flow(1, "600519", 0, n)
            count = len(df_test) if df_test is not None and not df_test.empty else 0
            print(f"     请求 {n} 条 → 返回 {count} 条")
        except Exception as e:
            print(f"     请求 {n} 条 → 异常: {type(e).__name__}: {e}")

cleanup_tdx()


# ============================================================
# 第二部分：东财 push2 深度诊断
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第二部分】东财 push2 接口深度诊断")
print(f"{'='*70}")

import requests

EM_URL = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
TEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://quote.eastmoney.com/",
    "Accept": "application/json, text/plain, */*",
}

print(f"\n  1. 直接用 requests 测试（绕过 em_get 封装）:")
test_stocks = [
    ("600519", "1.600519", "贵州茅台"),
    ("000100", "0.000100", "TCL科技"),
]

for code, secid, name in test_stocks:
    print(f"\n     --- {code} {name} ---")
    params = {
        "secid": secid,
        "klt": 101,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }
    
    for attempt in range(3):
        try:
            t0 = time.time()
            r = requests.get(EM_URL, params=params, headers=TEST_HEADERS, timeout=15)
            elapsed = time.time() - t0
            print(f"     第{attempt+1}次: HTTP {r.status_code}, {elapsed:.2f}s, {len(r.content)} bytes")
            
            if r.status_code == 200:
                try:
                    d = r.json()
                    data = d.get("data", {})
                    klines = data.get("klines", [])
                    print(f"          klines数量: {len(klines)}")
                    if klines:
                        print(f"          首条kline: {klines[0][:80]}...")
                        parts = klines[0].split(",")
                        print(f"          字段数: {len(parts)}")
                        print(f"          各字段值: {parts}")
                        # 检查最后几条
                        if len(klines) >= 3:
                            print(f"          最后3条日期: {[k.split(',')[0] for k in klines[-3:]]}")
                    else:
                        print(f"          ⚠️  klines 为空数组")
                        print(f"          完整响应 data 部分 keys: {list(data.keys()) if data else 'data is None/falsy'}")
                        print(f"          完整响应 (前500字): {str(d)[:500]}")
                    break  # 成功就不用重试了
                except Exception as je:
                    print(f"          JSON解析失败: {je}")
                    print(f"          响应文本 (前300字): {r.text[:300]}")
            else:
                print(f"          响应文本 (前200字): {r.text[:200]}")
        except Exception as e:
            print(f"     第{attempt+1}次异常: {type(e).__name__}: {e}")
        
        if attempt < 2:
            time.sleep(2)

print(f"\n  2. 测试不同的请求参数组合:")
code = "600519"
secid = f"1.{code}"

param_variants = [
    ("标准参数", {
        "secid": secid, "klt": 101,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }),
    ("更多fields1", {
        "secid": secid, "klt": 101,
        "fields1": "f1,f2,f3,f4,f5,f6,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }),
    ("只有fields2", {
        "secid": secid, "klt": 101,
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }),
    ("lmt限制数量", {
        "secid": secid, "klt": 101, "lmt": 60,
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }),
]

for name, params in param_variants:
    try:
        r = requests.get(EM_URL, params=params, headers=TEST_HEADERS, timeout=15)
        d = r.json()
        klines = d.get("data", {}).get("klines", []) if d.get("data") else []
        print(f"     {name}: {len(klines)} 条 klines")
        if not klines and d.get("data"):
            print(f"       data keys: {list(d['data'].keys())}")
    except Exception as e:
        print(f"     {name}: 异常 {type(e).__name__}: {e}")
    time.sleep(1)

print(f"\n  3. 测试通过 em_get 封装调用（检查是否有区别）:")
try:
    from stock_common import em_get
    from stock_common.sc_network import EM_SESSION, EM_MIN_INTERVAL, _EM_LAST_CALL
    
    print(f"     EM_MIN_INTERVAL: {EM_MIN_INTERVAL}")
    print(f"     _EM_LAST_CALL: {_EM_LAST_CALL[0]}")
    print(f"     EM_SESSION type: {type(EM_SESSION).__name__}")
    print(f"     EM_SESSION headers: {dict(EM_SESSION.headers)}")
    
    secid = "1.600519"
    params = {
        "secid": secid, "klt": 101,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }
    r = em_get(EM_URL, params=params, headers=TEST_HEADERS, timeout=15)
    if r is None:
        print(f"     ❌ em_get 返回 None")
    else:
        print(f"     ✅ em_get 返回: HTTP {r.status_code}, {len(r.content)} bytes")
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        print(f"     klines数量: {len(klines)}")
except Exception as e:
    print(f"     ❌ em_get 异常: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()


# ============================================================
# 第三部分：缓存诊断
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第三部分】缓存诊断")
print(f"{'='*70}")

# 检查缓存文件
cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
cache_db = os.path.join(cache_dir, "stock_cache.db")
print(f"\n  缓存目录: {cache_dir}")
print(f"  缓存文件存在: {os.path.exists(cache_db)}")
if os.path.exists(cache_db):
    size_kb = os.path.getsize(cache_db) / 1024
    print(f"  缓存文件大小: {size_kb:.1f} KB")

# 检查是否有 f10_fund_flow 缓存
import sqlite3
if os.path.exists(cache_db):
    try:
        conn = sqlite3.connect(cache_db)
        cur = conn.cursor()
        
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print(f"  缓存表: {tables}")
        
        if "stock_cache" in tables:
            cur.execute("SELECT COUNT(*) FROM stock_cache WHERE category='f10_fund_flow'")
            count = cur.fetchone()[0]
            print(f"  f10_fund_flow 缓存条数: {count}")
            
            if count > 0:
                cur.execute("SELECT key, value, created_at, expires_at FROM stock_cache WHERE category='f10_fund_flow' LIMIT 5")
                rows = cur.fetchall()
                print(f"  样本:")
                for key, value, created, expires in rows:
                    val_preview = str(value)[:100] if value else "None"
                    print(f"    key={key}, value_len={len(str(value)) if value else 0}, created={created}, expires={expires}")
                    print(f"      value预览: {val_preview}")
        conn.close()
    except Exception as e:
        print(f"  读取缓存失败: {e}")

# 测试用 STOCK_NOCACHE 环境变量绕过缓存
print(f"\n  测试无缓存模式下的 tdx_get_history_fund_flow:")
os.environ["STOCK_NOCACHE"] = "1"
from tdx_client import tdx_get_history_fund_flow
try:
    data = tdx_get_history_fund_flow("600519", 60)
    print(f"  600519 (无缓存): {len(data)} 条")
except Exception as e:
    print(f"  异常: {type(e).__name__}: {e}")
del os.environ["STOCK_NOCACHE"]


# ============================================================
# 第四部分：连续请求稳定性测试
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第四部分】连续请求稳定性测试（模拟批量场景）")
print(f"{'='*70}")

TEST_CODES_BATCH = [
    "600519", "000100", "600036", "000858", "601318",
    "000001", "600276", "002594", "601899", "300750",
]
ROUND_COUNT = 3

print(f"\n  测试股票: {len(TEST_CODES_BATCH)} 只, 每只 {ROUND_COUNT} 轮")
print(f"  使用直接 requests 调用东财接口")

em_results = []
for i in range(ROUND_COUNT):
    print(f"\n  --- 第 {i+1} 轮 ---")
    success_count = 0
    for code in TEST_CODES_BATCH:
        secid = f"1.{code}" if code.startswith("6") else f"0.{code}"
        params = {
            "secid": secid, "klt": 101,
            "fields1": "f1,f2,f3,f7",
            "fields2": "f51,f52,f53,f54,f55,f56,f57",
        }
        try:
            r = requests.get(EM_URL, params=params, headers=TEST_HEADERS, timeout=10)
            d = r.json()
            klines = d.get("data", {}).get("klines", []) if d.get("data") else []
            count = len(klines)
            success = count > 0
            if success:
                success_count += 1
            em_results.append({"round": i+1, "code": code, "count": count, "success": success})
            status = "✅" if success else "❌"
            print(f"    {code}: {status} {count}条", end="")
            if not success:
                print(f" (data={'None' if not d.get('data') else 'empty'})", end="")
            print()
        except Exception as e:
            em_results.append({"round": i+1, "code": code, "count": 0, "success": False, "error": str(e)})
            print(f"    {code}: ❌ 异常 {type(e).__name__}")
        
        time.sleep(0.5)  # 每只股票间隔0.5s
    
    print(f"  本轮成功率: {success_count}/{len(TEST_CODES_BATCH)}")

# 统计汇总
print(f"\n  东财接口汇总:")
total = len(em_results)
success_total = sum(1 for r in em_results if r["success"])
print(f"  总请求数: {total}")
print(f"  成功数: {success_total} ({success_total/total*100:.1f}%)")
print(f"  失败数: {total - success_total}")

# 分析失败原因
failures = [r for r in em_results if not r["success"]]
if failures:
    error_types = {}
    for f in failures:
        err = f.get("error", "空数据")
        if "HTTPSConnectionPool" in err or "ConnectionError" in err:
            key = "连接错误"
        elif "空数据" in err:
            key = "返回空数据"
        else:
            key = err[:30]
        error_types[key] = error_types.get(key, 0) + 1
    print(f"  失败原因分布:")
    for etype, cnt in error_types.items():
        print(f"    {etype}: {cnt}次")

cleanup_tdx()
print(f"\n\n{'='*70}")
print(f"  诊断完成！")
print(f"{'='*70}")

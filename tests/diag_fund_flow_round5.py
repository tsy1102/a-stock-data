"""
诊断第5轮：
1. 追踪 _get_tdx_client 失败的具体原因
2. 测试 TDX 服务器的 K线接口（看健康检查是否会排除）
3. 模拟批量请求场景（多只股票连续请求）
4. 东财 push2 接口的其他可用替代方案
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(f"{'='*70}")
print(f"  诊断第5轮：失败追踪 & 批量模拟  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}")


# ============================================================
# 第一部分：手动追踪 _get_tdx_client 全流程
# ============================================================
print(f"\n{'='*70}")
print(f"  【第一部分】手动追踪 _get_tdx_client 全流程")
print(f"{'='*70}")

# 1. 检查 _check_tdx
print(f"\n  1. 调用 _check_tdx():")
from tdx_client import _check_tdx, _TDX_AVAILABLE, _TDX_BAD_HOSTS, _TDX_CLIENT
print(f"     调用前 _TDX_AVAILABLE = {_TDX_AVAILABLE}")
print(f"     调用前 _TDX_BAD_HOSTS 数量 = {len(_TDX_BAD_HOSTS)}")
result = _check_tdx()
print(f"     调用结果: {result}")
print(f"     调用后 _TDX_AVAILABLE = {_TDX_AVAILABLE}")

# 2. 手动模拟 from_best_host + connect + health_check
print(f"\n  2. 手动模拟完整连接流程:")
from easy_tdx import TdxClient
from easy_tdx.config import get_known_hosts
from tdx_client import _tdx_health_check

_all_hosts = get_known_hosts()
_good_hosts = [h for h in _all_hosts if h not in _TDX_BAD_HOSTS]
print(f"     总主机数: {len(_all_hosts)}, 可用(未被标记坏): {len(_good_hosts)}")
print(f"     坏主机列表: {list(_TDX_BAD_HOSTS)}")

# 手动 ping 前几个
print(f"\n  3. 手动测试前 10 个主机的 K线接口（健康检查关键项）:")
kline_good = []
kline_bad = []
for i, host in enumerate(_good_hosts[:10]):
    try:
        client = TdxClient(host=host, port=7709)
        client.connect()
        try:
            from easy_tdx import KlineCategory, Market
            bars = client.get_security_bars(Market.SH, "600519", KlineCategory.DAY, 0, 5)
            if bars is not None and not bars.empty and len(bars) >= 3:
                print(f"    {i+1:2d}. {host:18s} ✅ K线正常 ({len(bars)}条)")
                kline_good.append(host)
            else:
                print(f"    {i+1:2d}. {host:18s} ❌ K线空数据")
                kline_bad.append((host, "empty"))
        except Exception as e:
            err_name = type(e).__name__
            if 'Decode' in err_name or '数据不足' in str(e):
                print(f"    {i+1:2d}. {host:18s} ❌ K线解码错误: {str(e)[:50]}")
                kline_bad.append((host, f"decode: {err_name}"))
            else:
                print(f"    {i+1:2d}. {host:18s} ⚠️  K线异常: {err_name}")
                kline_bad.append((host, err_name))
        client.close()
    except Exception as e:
        print(f"    {i+1:2d}. {host:18s} ❌ 连接失败: {type(e).__name__}")
        kline_bad.append((host, f"connect: {type(e).__name__}"))
    time.sleep(0.1)

print(f"\n  K线正常: {len(kline_good)} 台, K线异常: {len(kline_bad)} 台")

# 在 K线正常的服务器中，进一步测试历史资金流
if kline_good:
    print(f"\n  4. 在 K线正常的服务器中测试历史资金流:")
    hff_good = []
    hff_bad = []
    for host in kline_good:
        try:
            client = TdxClient(host=host, port=7709)
            client.connect()
            try:
                df = client.get_history_fund_flow(1, "600519", 0, 60)
                if df is not None and not df.empty and len(df) >= 30:
                    print(f"    {host}: ✅ 历史资金流正常 ({len(df)}条)")
                    hff_good.append(host)
                else:
                    count = len(df) if df is not None and not df.empty else 0
                    print(f"    {host}: ⚠️  历史资金流不足 ({count}条)")
                    hff_bad.append((host, f"only {count}"))
            except Exception as e:
                print(f"    {host}: ❌ 历史资金流异常: {type(e).__name__}")
                hff_bad.append((host, type(e).__name__))
            client.close()
        except Exception as e:
            print(f"    {host}: ❌ 连接失败")
            hff_bad.append((host, "connect fail"))
        time.sleep(0.1)
    
    print(f"\n  历史资金流可用: {len(hff_good)} 台: {hff_good}")
    print(f"  历史资金流不可用: {len(hff_bad)} 台")


# ============================================================
# 第二部分：模拟批量场景
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第二部分】模拟批量请求场景")
print(f"{'='*70}")

# 用一个确认可用的服务器来测试
if hff_good:
    test_host = hff_good[0]
    print(f"\n  使用 {test_host} 模拟批量请求（20只股票 x 3轮）:")
    
    from tdx_client import _market_from_code, _safe_float
    
    test_stocks = [
        "600519", "000100", "600036", "000858", "601318",
        "000001", "600276", "002594", "601899", "300750",
        "600900", "000333", "601012", "002594", "300059",
        "601888", "000568", "600809", "002230", "600030",
    ]
    
    client = TdxClient(host=test_host, port=7709)
    client.connect()
    
    results = []
    for round_num in range(3):
        round_success = 0
        round_fail = 0
        for code in test_stocks:
            try:
                market = _market_from_code(code)
                df = client.get_history_fund_flow(market, code, 0, 60)
                count = len(df) if df is not None and not df.empty else 0
                success = count >= 50
                if success:
                    round_success += 1
                else:
                    round_fail += 1
                results.append({"round": round_num+1, "code": code, "count": count, "success": success})
            except Exception as e:
                round_fail += 1
                results.append({"round": round_num+1, "code": code, "count": 0, "success": False, "error": str(e)})
            time.sleep(0.1)  # 模拟请求间隔
        
        print(f"  第{round_num+1}轮: 成功 {round_success}/{len(test_stocks)}, 失败 {round_fail}")
    
    client.close()
    
    # 统计分析
    total = len(results)
    success_total = sum(1 for r in results if r["success"])
    print(f"\n  汇总:")
    print(f"    总请求: {total}")
    print(f"    成功: {success_total} ({success_total/total*100:.1f}%)")
    print(f"    失败: {total - success_total}")
    
    # 失败的具体情况
    failures = [r for r in results if not r["success"]]
    if failures:
        print(f"    失败详情:")
        fail_by_code = {}
        for f in failures:
            code = f["code"]
            fail_by_code[code] = fail_by_code.get(code, 0) + 1
        # 按失败次数排序
        sorted_fails = sorted(fail_by_code.items(), key=lambda x: -x[1])
        for code, cnt in sorted_fails[:10]:
            # 找一个失败样本看原因
            sample = next((f for f in failures if f["code"] == code), None)
            reason = sample.get("error", f"数据不足({sample.get('count', 0)}条)") if sample else "未知"
            print(f"      {code}: 失败{cnt}次, 原因: {reason[:50]}")
    
    # 数据条数分布
    success_results = [r for r in results if r["success"]]
    if success_results:
        counts = [r["count"] for r in success_results]
        print(f"\n    成功请求的数据条数:")
        print(f"      最小: {min(counts)}, 最大: {max(counts)}, 平均: {sum(counts)/len(counts):.1f}")
        # 检查是否有数据条数不一致的股票
        code_counts = {}
        for r in success_results:
            code = r["code"]
            if code not in code_counts:
                code_counts[code] = []
            code_counts[code].append(r["count"])
        
        inconsistent = []
        for code, cnts in code_counts.items():
            if len(set(cnts)) > 1:
                inconsistent.append((code, cnts))
        if inconsistent:
            print(f"    ⚠️  数据条数不一致的股票:")
            for code, cnts in inconsistent[:5]:
                print(f"      {code}: {cnts}")


# ============================================================
# 第三部分：东财接口的替代方案测试
# ============================================================
print(f"\n\n{'='*70}")
print(f"  【第三部分】东财资金流替代接口测试")
print(f"{'='*70}")

import requests
session = requests.Session()
session.trust_env = False
TEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://data.eastmoney.com/zjlx/600519.html",
}

# 测试几个可能的 API 端点
test_apis = [
    ("push2.eastmoney.com 个股资金流", 
     "https://push2.eastmoney.com/api/qt/stock/get",
     {"secid": "1.600519", "fields": "f43,f44,f45,f46,f47,f48,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f83,f84,f85,f86,f87"}),
    ("data.eastmoney.com zjlx detail",
     "https://data.eastmoney.com/zjlx/detail.html",
     {"code": "600519"}),
    ("push2.eastmoney.com fflow/kline/get",
     "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get",
     {"secid": "1.600519", "klt": 101, "fields1": "f1,f2,f3,f7", "fields2": "f51,f52,f53,f54,f55,f56,f57"}),
    ("push2his.eastmoney.com fflow/daykline/get (重试)",
     "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get",
     {"secid": "1.600519", "klt": 101, "fields1": "f1,f2,f3,f7", "fields2": "f51,f52,f53,f54,f55,f56,f57"}),
]

print(f"\n  测试可能的东财资金流 API:")
for name, url, params in test_apis:
    try:
        t0 = time.time()
        r = session.get(url, params=params, headers=TEST_HEADERS, timeout=10)
        elapsed = time.time() - t0
        print(f"\n  {name}:")
        print(f"    HTTP {r.status_code}, {len(r.content)} bytes, {elapsed:.2f}s")
        if r.status_code == 200 and len(r.content) > 500:
            try:
                d = r.json()
                # 看看有没有数据
                if isinstance(d, dict):
                    keys = list(d.keys())[:10]
                    print(f"    JSON keys: {keys}")
                    if 'data' in d and d['data']:
                        data_keys = list(d['data'].keys())[:10] if isinstance(d['data'], dict) else f"list len={len(d['data'])}"
                        print(f"    data keys: {data_keys}")
                        # 看看有没有 f51 f52 之类的
                        if isinstance(d['data'], dict):
                            for k, v in list(d['data'].items())[:5]:
                                print(f"      {k}: {str(v)[:60]}")
            except Exception:
                print(f"    非JSON或解析失败，前300字: {r.text[:300]}")
        elif r.status_code == 200:
            print(f"    响应太短: {r.text[:300]}")
        else:
            print(f"    响应前200字: {r.text[:200]}")
    except Exception as e:
        print(f"\n  {name}: ❌ {type(e).__name__}: {str(e)[:80]}")


print(f"\n\n{'='*70}")
print(f"  第5轮诊断完成！")
print(f"{'='*70}")

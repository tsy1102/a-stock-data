"""
资金流数据稳定性诊断脚本
- 测试 TDX TCP 接口 (tdx_get_history_fund_flow)
- 测试 东财 push2 接口 (_get_eastmoney_fund_flow_120d)
- 多次调用对比，检测接口稳定性和数据完整性
- 检查数据格式是否正确
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_client import tdx_get_history_fund_flow, cleanup_tdx
from get_sht_report import _get_eastmoney_fund_flow_120d, get_fund_flow_120d


TEST_CODES = [
    "000100",  # TCL科技 (深市)
    "600519",  # 贵州茅台 (沪市)
    "300750",  # 宁德时代 (创业板)
    "688981",  # 中芯国际 (科创板)
    "000977",  # 浪潮信息
]

ROUND_COUNT = 5  # 每只股票调用5次测试稳定性


def test_tdx(code: str, round_num: int) -> dict:
    """测试 TDX 接口"""
    t0 = time.time()
    try:
        data = tdx_get_history_fund_flow(code, 60)
        elapsed = time.time() - t0
        
        if not data:
            return {"source": "tdx", "code": code, "round": round_num,
                    "success": False, "count": 0, "elapsed": elapsed,
                    "error": "返回空数据", "sample": None}
        
        # 检查数据格式
        first = data[0] if data else None
        last = data[-1] if data else None
        
        # 检查必需字段
        required_fields = ["date", "main_net", "super_net", "large_net", "mid_net", "small_net"]
        missing_fields = [f for f in required_fields if f not in first] if first else []
        
        # 检查日期连续性（粗略检查最后5天）
        recent_dates = [d["date"] for d in data[-5:]] if len(data) >= 5 else [d["date"] for d in data]
        
        return {"source": "tdx", "code": code, "round": round_num,
                "success": True, "count": len(data), "elapsed": elapsed,
                "missing_fields": missing_fields,
                "first_date": first.get("date") if first else None,
                "last_date": last.get("date") if last else None,
                "recent_dates": recent_dates,
                "sample_main_net": [d["main_net"] for d in data[-3:]] if len(data) >= 3 else [],
                "error": None}
    except Exception as e:
        elapsed = time.time() - t0
        return {"source": "tdx", "code": code, "round": round_num,
                "success": False, "count": 0, "elapsed": elapsed,
                "error": f"{type(e).__name__}: {e}", "sample": None}


def test_eastmoney(code: str, round_num: int) -> dict:
    """测试东财 push2 接口"""
    t0 = time.time()
    try:
        data = _get_eastmoney_fund_flow_120d(code)
        elapsed = time.time() - t0
        
        if not data:
            return {"source": "eastmoney", "code": code, "round": round_num,
                    "success": False, "count": 0, "elapsed": elapsed,
                    "error": "返回空数据", "sample": None}
        
        return {"source": "eastmoney", "code": code, "round": round_num,
                "success": True, "count": len(data), "elapsed": elapsed,
                "sample_last3": data[-3:],
                "all_positive": all(x > 0 for x in data),  # 检查是否全正（可疑）
                "all_negative": all(x < 0 for x in data),  # 检查是否全负（可疑）
                "error": None}
    except Exception as e:
        elapsed = time.time() - t0
        return {"source": "eastmoney", "code": code, "round": round_num,
                "success": False, "count": 0, "elapsed": elapsed,
                "error": f"{type(e).__name__}: {e}", "sample": None}


def test_raw_eastmoney_api(code: str) -> dict:
    """直接测试东财 push2 API 原始返回，检查数据格式"""
    import requests
    from stock_common import em_get
    
    secid = f"1.{code}" if code.startswith("6") else f"0.{code}"
    url = "https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get"
    params = {
        "secid": secid,
        "klt": 101,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com/"}
    
    try:
        r = em_get(url, params=params, headers=headers, timeout=15)
        if r is None:
            return {"success": False, "error": "请求返回 None (em_get)"}
        
        d = r.json()
        data = d.get("data", {})
        klines = data.get("klines", [])
        
        if not klines:
            return {"success": False, "error": f"klines 为空, 完整响应: {d}",
                    "data_keys": list(data.keys()) if data else []}
        
        # 检查第一条kline格式
        first = klines[0]
        parts = first.split(",")
        
        # 检查字段含义
        result = {
            "success": True,
            "total_klines": len(klines),
            "first_date_str": parts[0] if len(parts) > 0 else None,
            "num_fields": len(parts),
            "all_fields_sample": parts[:7],
            "field_names": ["f51(日期)", "f52(主力净流入)", "f53(小单)", "f54(中单)", "f55(大单)", "f56(超大单)", "f57(主力净流入占比)"],
        }
        
        # 取最后5天数据检查
        if len(klines) >= 5:
            result["last_5_dates"] = [k.split(",")[0] for k in klines[-5:]]
            result["last_5_main_net"] = [k.split(",")[1] if len(k.split(",")) > 1 else "N/A" for k in klines[-5:]]
        
        # 检查是否有异常数据（全0）
        zero_count = 0
        for k in klines:
            parts_k = k.split(",")
            if len(parts_k) >= 2:
                try:
                    if float(parts_k[1]) == 0:
                        zero_count += 1
                except ValueError:
                    pass
        result["zero_value_count"] = zero_count
        
        return result
    except Exception as e:
        return {"success": False, "error": f"{type(e).__name__}: {e}"}


def print_result(results: list, source: str):
    """打印测试结果汇总"""
    print(f"\n{'='*70}")
    print(f"  {source.upper()} 接口测试结果")
    print(f"{'='*70}")
    
    for code in TEST_CODES:
        code_results = [r for r in results if r["code"] == code and r["source"] == source]
        success_count = sum(1 for r in code_results if r["success"])
        counts = [r["count"] for r in code_results if r["success"]]
        elapsed_times = [r["elapsed"] for r in code_results]
        
        print(f"\n  股票: {code}")
        print(f"    成功率: {success_count}/{len(code_results)}")
        print(f"    平均耗时: {sum(elapsed_times)/len(elapsed_times):.2f}s")
        
        if counts:
            print(f"    数据条数: min={min(counts)}, max={max(counts)}, avg={sum(counts)/len(counts):.0f}")
            if min(counts) != max(counts):
                print(f"    ⚠️ 数据条数不一致！各轮数据量: {counts}")
        
        # 打印失败详情
        failures = [r for r in code_results if not r["success"]]
        if failures:
            for i, f in enumerate(failures):
                print(f"    ❌ 第{f['round']}轮失败: {f['error']}")
        
        # 打印成功样本
        successes = [r for r in code_results if r["success"]]
        if successes:
            sample = successes[0]
            if source == "tdx":
                print(f"    首条日期: {sample.get('first_date')}")
                print(f"    末条日期: {sample.get('last_date')}")
                if sample.get("missing_fields"):
                    print(f"    ⚠️ 缺失字段: {sample['missing_fields']}")
            elif source == "eastmoney":
                print(f"    最后3日主力净流入(万元): {sample.get('sample_last3', [])}")
                if sample.get("all_positive"):
                    print(f"    ⚠️ 全部为正值（可疑）")
                if sample.get("all_negative"):
                    print(f"    ⚠️ 全部为负值（可疑）")


def main():
    print(f"{'='*70}")
    print(f"  资金流数据稳定性诊断  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  测试股票: {', '.join(TEST_CODES)}")
    print(f"  每只股票测试轮数: {ROUND_COUNT}")
    print(f"{'='*70}")
    
    all_results = []
    
    # 第一轮: 测试东财原始API格式
    print(f"\n{'='*70}")
    print(f"  第0轮: 东财 push2 API 原始数据格式检查")
    print(f"{'='*70}")
    for code in TEST_CODES[:2]:  # 只测2只，节省时间
        print(f"\n  股票: {code}")
        result = test_raw_eastmoney_api(code)
        if result["success"]:
            print(f"    总K线数: {result['total_klines']}")
            print(f"    字段数: {result['num_fields']}")
            print(f"    字段说明: {result['field_names']}")
            print(f"    首条日期: {result['first_date_str']}")
            print(f"    首条各字段值: {result['all_fields_sample']}")
            if "last_5_dates" in result:
                print(f"    最后5日: {result['last_5_dates']}")
                print(f"    最后5日主力净流入(元): {result['last_5_main_net']}")
            print(f"    零值数据条数: {result['zero_value_count']}")
        else:
            print(f"    ❌ 失败: {result['error']}")
    
    # 多轮测试
    for i in range(ROUND_COUNT):
        print(f"\n\n{'='*70}")
        print(f"  第 {i+1}/{ROUND_COUNT} 轮测试")
        print(f"{'='*70}")
        
        for code in TEST_CODES:
            tdx_r = test_tdx(code, i+1)
            em_r = test_eastmoney(code, i+1)
            all_results.extend([tdx_r, em_r])
            
            status_tdx = "✅" if tdx_r["success"] else "❌"
            status_em = "✅" if em_r["success"] else "❌"
            print(f"  {code}  TDX: {status_tdx} {tdx_r['count']}条/{tdx_r['elapsed']:.2f}s  "
                  f"EM: {status_em} {em_r['count']}条/{em_r['elapsed']:.2f}s")
        
        if i < ROUND_COUNT - 1:
            print(f"  等待 2s 后进行下一轮...")
            time.sleep(2)
    
    # 汇总报告
    print_result(all_results, "tdx")
    print_result(all_results, "eastmoney")
    
    # 交叉对比：同一只股票同一轮，TDX和东财数据条数对比
    print(f"\n{'='*70}")
    print(f"  TDX vs 东财 数据条数交叉对比")
    print(f"{'='*70}")
    for code in TEST_CODES:
        for i in range(ROUND_COUNT):
            tdx_r = next((r for r in all_results if r["code"] == code and r["source"] == "tdx" and r["round"] == i+1), None)
            em_r = next((r for r in all_results if r["code"] == code and r["source"] == "eastmoney" and r["round"] == i+1), None)
            if tdx_r and em_r and tdx_r["success"] and em_r["success"]:
                diff = abs(tdx_r["count"] - em_r["count"])
                if diff > 5:
                    print(f"  ⚠️ {code} 第{i+1}轮: TDX={tdx_r['count']}条, EM={em_r['count']}条, 差{diff}条")
    
    cleanup_tdx()
    print(f"\n  诊断完成！")


if __name__ == "__main__":
    main()

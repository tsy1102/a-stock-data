#!/usr/bin/env python3
"""同花顺接口诊断脚本 - 测试同花顺HTTP接口

V1.0 2026-07-09 - V9.3.1 新增（按数据源重组）
覆盖接口：
- get_ths_hot_reason    热点原因
- ths_hot_list          热榜
"""
import sys
import os
import time
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REQUEST_INTERVAL = 1.5


def _result(status, data="", error=""):
    return {"status": status, "data": data, "error": error}


def test_ths_hot_reason():
    """测试同花顺热点原因"""
    try:
        from stock_common import get_ths_hot_reason
        # 热点原因只在涨停日有数据，用近5个交易日尝试
        for i in range(5):
            d_str = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            data = get_ths_hot_reason("600519", d_str)
            if data and data.get("reason"):
                return _result("success",
                    f"{d_str} 热点原因: {data['reason'][:50]}...")
        return _result("warning", "近5日无热点原因数据（未涨停或接口无数据）", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_ths_hot_list():
    """测试同花顺热榜"""
    try:
        from stock_common import ths_hot_list
        data = ths_hot_list(period="hour")
        if data and len(data) > 0:
            return _result("success", f"返回 {len(data)} 只热榜股票")
        return _result("warning", "返回空列表", "")
    except Exception as e:
        return _result("failed", "", str(e))


def main():
    print("=" * 70)
    print("同花顺接口诊断测试 V1.0")
    print("=" * 70)
    print(f"测试日期: {date.today().strftime('%Y-%m-%d')}")
    print(f"HTTP间隔: {REQUEST_INTERVAL}s")
    print("数据源: 同花顺HTTP接口")

    tests = [
        ("热点原因", test_ths_hot_reason),
        ("热榜", test_ths_hot_list),
    ]

    results = []
    for name, func in tests:
        print(f"\n测试: {name}...", end="", flush=True)
        result = func()
        results.append((name, result))

        if result["status"] == "success":
            print(f" ✅ {result['data']}")
        elif result["status"] == "warning":
            print(f" ⚠️ {result['data']}")
        else:
            print(f" ❌ {result['error']}")

        time.sleep(REQUEST_INTERVAL)

    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    success = sum(1 for _, r in results if r["status"] == "success")
    warning = sum(1 for _, r in results if r["status"] == "warning")
    fail = len(results) - success - warning
    print(f"成功: {success}/{len(results)}  警告: {warning}/{len(results)}  失败: {fail}/{len(results)}")

    print()


if __name__ == "__main__":
    main()
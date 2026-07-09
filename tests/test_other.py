#!/usr/bin/env python3
"""其他接口诊断脚本 - 测试腾讯/新浪/百度/巨潮等接口

V1.0 2026-07-09 - V9.3.1 新增（按数据源重组）
覆盖接口：
- get_tencent_quote           腾讯行情
- get_sina_financial_report   新浪财报
- baidu_kline_full            百度K线
- get_strategic_announcements 巨潮公告
- get_hsgt_macro_flow         沪深港通宏观资金流
"""
import sys
import os
import time
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REQUEST_INTERVAL = 1.0


def _result(status, data="", error=""):
    return {"status": status, "data": data, "error": error}


def test_tencent_quote():
    """测试腾讯行情"""
    try:
        from stock_common import get_tencent_quote
        data = get_tencent_quote("600519")
        if data and isinstance(data, dict) and data.get("price"):
            return _result("success",
                f"价格={data['price']}, 涨跌幅={data.get('change_pct',0)}%")
        return _result("failed", "", "返回空或格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def test_sina_financial_report():
    """测试新浪财报"""
    try:
        from stock_common import get_sina_financial_report
        data = get_sina_financial_report("600519", num_periods=3)
        if data and isinstance(data, dict):
            periods = len(data.get("periods", []))
            return _result("success", f"返回 {periods} 期财报数据")
        return _result("warning", "返回空或格式异常", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_baidu_kline():
    """测试百度K线（deprecated）"""
    try:
        from stock_common import baidu_kline_full
        keys, rows = baidu_kline_full("600519")
        if rows and len(rows) > 0:
            return _result("success", f"返回 {len(rows)} 根K线（百度fallback）")
        return _result("warning", "返回空（TDX正常时不走百度）", "")
    except Exception as e:
        return _result("warning", f"百度K线异常: {e}", "")


def test_strategic_announcements():
    """测试巨潮公告"""
    try:
        from stock_common import get_strategic_announcements
        data = get_strategic_announcements("600519", page_size=10, days=30)
        if data and len(data) > 0:
            return _result("success", f"返回 {len(data)} 条公告")
        return _result("warning", "30日内无匹配关键词的公告", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_hsgt_macro_flow():
    """测试沪深港通宏观资金流"""
    try:
        from stock_common import get_hsgt_macro_flow
        data = get_hsgt_macro_flow()
        if data and isinstance(data, dict):
            total = data.get("total", 0)
            return _result("success",
                f"沪股通 {data.get('hgt',0):.2f} 亿 + 深股通 {data.get('sgt',0):.2f} 亿 = 合计 {total:.2f} 亿")
        return _result("failed", "", "返回空或格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def main():
    print("=" * 70)
    print("其他接口诊断测试 V1.0")
    print("=" * 70)
    print(f"测试日期: {date.today().strftime('%Y-%m-%d')}")
    print(f"HTTP间隔: {REQUEST_INTERVAL}s")
    print("数据源: 腾讯/新浪/百度/巨潮/同花顺宏观")

    tests = [
        ("腾讯行情", test_tencent_quote),
        ("新浪财报", test_sina_financial_report),
        ("百度K线", test_baidu_kline),
        ("巨潮公告", test_strategic_announcements),
        ("沪深港通宏观", test_hsgt_macro_flow),
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
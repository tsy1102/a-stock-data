#!/usr/bin/env python3
"""TDX F10接口诊断脚本 - 测试通达信F10各分类接口

V1.0 2026-07-09 - V9.3.1 新增（按数据源重组）
覆盖接口：
- tdx_get_financial_analysis      财务分析
- tdx_get_shareholder_research    股东研究
- tdx_get_share_capital           股本结构
- tdx_get_latest_reminders        最新提示
- tdx_get_company_news_f10        公司新闻
- tdx_get_latest_announcements    最新公告
"""
import sys
import os
import time
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TDX_INTERVAL = 0.3


def _result(status, data="", error=""):
    return {"status": status, "data": data, "error": error}


def test_tdx_financial_analysis():
    """测试TDX财务分析(F10)"""
    try:
        from tdx_client import tdx_get_financial_analysis
        data = tdx_get_financial_analysis("600519")
        if data and isinstance(data, dict):
            main = data.get("main_indicators", [])
            prof = data.get("profitability", [])
            return _result("success",
                f"主要指标 {len(main)} 期, 盈利能力 {len(prof)} 期")
        return _result("failed", "", "返回格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_shareholder_research():
    """测试TDX股东研究(F10)"""
    try:
        from tdx_client import tdx_get_shareholder_research
        data = tdx_get_shareholder_research("600519")
        if data and isinstance(data, dict):
            holder_count = data.get("holder_count", [])
            changes = data.get("shareholder_changes", [])
            return _result("success",
                f"股东人数变化 {len(holder_count)} 期, 十大股东 {len(changes)} 期")
        return _result("failed", "", "返回格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_share_capital():
    """测试TDX股本结构(F10)"""
    try:
        from tdx_client import tdx_get_share_capital
        data = tdx_get_share_capital("600519")
        if data and isinstance(data, dict):
            structure = data.get("structure", [])
            lockup = data.get("lockup_expiry", [])
            return _result("success",
                f"股本结构 {len(structure)} 期, 限售解禁 {len(lockup)} 条")
        return _result("failed", "", "返回格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_latest_reminders():
    """测试TDX最新提示(F10)"""
    try:
        from tdx_client import tdx_get_latest_reminders
        data = tdx_get_latest_reminders("600519")
        if data and isinstance(data, dict):
            indicators = data.get("latest_indicators", {})
            news = data.get("latest_news", [])
            margin = data.get("margin_trading", [])
            return _result("success",
                f"最新指标 {len(indicators)} 项, 最新报道 {len(news)} 条, 融资融券 {len(margin)} 条")
        return _result("failed", "", "返回格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_company_news_f10():
    """测试TDX公司新闻(F10)"""
    try:
        from tdx_client import tdx_get_company_news_f10
        data = tdx_get_company_news_f10("600519", count=5)
        if data and isinstance(data, list):
            if len(data) > 0:
                return _result("success", f"返回 {len(data)} 条公司新闻")
            return _result("warning", "返回空列表", "")
        return _result("failed", "", "返回格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_latest_announcements():
    """测试TDX最新公告"""
    try:
        from tdx_client import tdx_get_latest_announcements
        data = tdx_get_latest_announcements("600519", days=7)
        if data and isinstance(data, list):
            if len(data) > 0:
                return _result("success", f"返回 {len(data)} 条公告")
            return _result("warning", "近7日无公告", "")
        return _result("failed", "", "返回格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def main():
    print("=" * 70)
    print("TDX F10接口诊断测试 V1.0")
    print("=" * 70)
    print(f"测试日期: {date.today().strftime('%Y-%m-%d')}")
    print(f"TDX间隔: {TDX_INTERVAL}s")
    print("数据源: 通达信F10接口")

    tests = [
        ("财务分析(F10)", test_tdx_financial_analysis),
        ("股东研究(F10)", test_tdx_shareholder_research),
        ("股本结构(F10)", test_tdx_share_capital),
        ("最新提示(F10)", test_tdx_latest_reminders),
        ("公司新闻(F10)", test_tdx_company_news_f10),
        ("最新公告", test_tdx_latest_announcements),
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

        time.sleep(TDX_INTERVAL)

    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    success = sum(1 for _, r in results if r["status"] == "success")
    warning = sum(1 for _, r in results if r["status"] == "warning")
    fail = len(results) - success - warning
    print(f"成功: {success}/{len(results)}  警告: {warning}/{len(results)}  失败: {fail}/{len(results)}")

    if fail > 0 or warning > 0:
        print("\n需关注接口:")
        for name, r in results:
            if r["status"] == "failed":
                print(f"  ❌ {name}: {r['error']}")
            elif r["status"] == "warning":
                print(f"  ⚠️ {name}: {r['data']}")

    print()


if __name__ == "__main__":
    main()
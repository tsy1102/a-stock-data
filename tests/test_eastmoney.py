#!/usr/bin/env python3
"""东财接口诊断脚本 - 测试东方财富HTTP接口

V1.0 2026-07-09 - V9.3.1 新增（按数据源重组）
覆盖接口：
- eastmoney_datacenter          数据中心
- get_reports                    研报列表
- get_eastmoney_stock_news       个股新闻
- get_holder_structure           股东结构
- get_northbound_hold            北向持仓
- get_margin_trading             融资融券
- get_block_trade                大宗交易
- get_lockup_expiry              限售解禁
- get_industry_comparison        行业对比
- get_industry_peers             行业同行
- get_stock_sector_rank          板块排名
- get_gross_margin_and_roe       毛利率/ROE
- em_hot_concept                 概念命中
- eastmoney_stock_info_push2     push2基本面
"""
import sys
import os
import time
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REQUEST_INTERVAL = 1.5  # 东财HTTP请求间隔（秒）


def _result(status, data="", error=""):
    return {"status": status, "data": data, "error": error}


def test_eastmoney_datacenter():
    """测试东财数据中心接口"""
    try:
        from stock_common import eastmoney_datacenter
        data = eastmoney_datacenter("600519", "RPT_DAILYBILLBOARD_DETAILSNEW",
                                    columns="SECURITY_CODE,SECURITY_NAME_ABBR,TRADE_DATE",
                                    page_size=5, sort_columns="TRADE_DATE", sort_types="-1")
        if data and len(data) > 0:
            return _result("success", f"返回 {len(data)} 条龙虎榜数据")
        return _result("warning", "返回空（可能今日无数据）", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_get_reports():
    """测试东财研报列表"""
    try:
        from stock_common import get_reports
        data = get_reports("600519", max_pages=1)
        if data and len(data) > 0:
            return _result("success", f"返回 {len(data)} 条研报")
        return _result("warning", "返回空列表", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_eastmoney_stock_news():
    """测试东财个股新闻"""
    try:
        from stock_common import get_eastmoney_stock_news
        data = get_eastmoney_stock_news("600519", page_size=5)
        if data and len(data) > 0:
            return _result("success", f"返回 {len(data)} 条新闻")
        return _result("warning", "返回空列表", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_holder_structure():
    """测试东财股东结构"""
    try:
        from stock_common import get_holder_structure
        data = get_holder_structure("600519")
        if data and len(data) > 0:
            first = data[0]
            return _result("success",
                f"返回 {len(data)} 期数据，最新期 {first.get('date','')} 总占比 {first.get('total',0)}%")
        return _result("warning", "返回空列表", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_northbound_hold():
    """测试东财北向持仓"""
    try:
        from stock_common import get_northbound_hold
        data = get_northbound_hold("600519", days=5)
        if data and len(data) > 0:
            return _result("success", f"返回 {len(data)} 天北向持仓数据")
        return _result("warning", "返回空列表", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_margin_trading():
    """测试东财融资融券"""
    try:
        from stock_common import get_margin_trading
        data = get_margin_trading("600519")
        if data and len(data) > 0:
            return _result("success", f"返回 {len(data)} 天融资融券数据")
        return _result("warning", "返回空列表", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_block_trade():
    """测试东财大宗交易"""
    try:
        from stock_common import get_block_trade
        data = get_block_trade("600519")
        if data and isinstance(data, list):
            if len(data) > 0:
                return _result("success", f"返回 {len(data)} 条大宗交易记录")
            return _result("warning", "30日内无大宗交易", "")
        return _result("failed", "", "返回格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def test_lockup_expiry():
    """测试东财限售解禁"""
    try:
        from stock_common import get_lockup_expiry
        today = date.today().strftime("%Y-%m-%d")
        data = get_lockup_expiry("600519", today, days=90)
        if data and isinstance(data, list):
            return _result("success", f"未来90天 {len(data)} 条解禁记录")
        return _result("warning", "未来90天无限售解禁", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_industry_comparison():
    """测试东财行业对比"""
    try:
        from stock_common import get_industry_comparison
        data = get_industry_comparison(top_n=5)
        if data and isinstance(data, dict):
            return _result("success",
                f"共 {data.get('total',0)} 个行业，返回涨幅TOP {len(data.get('top',[]))}")
        return _result("failed", "", "返回格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def test_industry_peers():
    """测试东财行业同行"""
    try:
        from stock_common import get_industry_peers
        data = get_industry_peers("600519", top_n=3)
        if data and isinstance(data, dict):
            peers = data.get("peers", [])
            return _result("success", f"返回 {len(peers)} 家同行对比")
        return _result("warning", "返回空", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_stock_sector_rank():
    """测试东财板块排名"""
    try:
        from stock_common import get_stock_sector_rank
        data = get_stock_sector_rank("600519")
        if data and isinstance(data, dict):
            sectors = data.get("sectors", [])
            return _result("success", f"返回 {len(sectors)} 个板块排名")
        return _result("warning", "返回空", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_gross_margin_and_roe():
    """测试东财毛利率/ROE"""
    try:
        from stock_common import get_gross_margin_and_roe
        data = get_gross_margin_and_roe("600519")
        if data and isinstance(data, dict):
            gm = data.get("gross_margin")
            roe = data.get("roe")
            if gm is not None or roe is not None:
                return _result("success", f"毛利率={gm}%, ROE={roe}%")
        return _result("warning", "返回空", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_em_hot_concept():
    """测试东财概念命中"""
    try:
        from stock_common import em_hot_concept
        data = em_hot_concept("600519")
        if data and len(data) > 0:
            return _result("success", f"返回 {len(data)} 个热门概念命中")
        return _result("warning", "返回空列表", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_eastmoney_push2():
    """测试东财push2基本面"""
    try:
        from stock_common import eastmoney_stock_info_push2
        data = eastmoney_stock_info_push2("600519")
        if data and isinstance(data, dict) and data.get("list_date"):
            return _result("success",
                f"上市日期={data['list_date']}, 总市值={data.get('total_mcap',0)}亿")
        return _result("failed", "", "返回格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def main():
    print("=" * 70)
    print("东财接口诊断测试 V1.0")
    print("=" * 70)
    print(f"测试日期: {date.today().strftime('%Y-%m-%d')}")
    print(f"HTTP间隔: {REQUEST_INTERVAL}s")
    print("数据源: 东方财富HTTP接口")

    tests = [
        ("数据中心", test_eastmoney_datacenter),
        ("研报列表", test_get_reports),
        ("个股新闻", test_eastmoney_stock_news),
        ("股东结构", test_holder_structure),
        ("北向持仓", test_northbound_hold),
        ("融资融券", test_margin_trading),
        ("大宗交易", test_block_trade),
        ("限售解禁", test_lockup_expiry),
        ("行业对比", test_industry_comparison),
        ("行业同行", test_industry_peers),
        ("板块排名", test_stock_sector_rank),
        ("毛利率/ROE", test_gross_margin_and_roe),
        ("概念命中", test_em_hot_concept),
        ("push2基本面", test_eastmoney_push2),
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
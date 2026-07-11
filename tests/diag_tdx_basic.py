#!/usr/bin/env python3
"""TDX基础接口诊断脚本 - 测试通达信行情/K线/资金流/财务基础接口

覆盖接口：
- tdx_get_security_bars        K线行情
- tdx_get_quote_full           实时行情
- tdx_get_index_quote          指数行情
- tdx_get_fund_flow            资金流
- tdx_get_history_fund_flow    历史资金流
- tdx_get_finance_info         财务信息
- tdx_get_dividend_history     分红历史
- tdx_get_eps_from_reports     研报EPS
"""
import sys
import os
import time
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TDX_INTERVAL = 0.3  # TDX请求间隔（秒）


def _result(status, data="", error=""):
    return {"status": status, "data": data, "error": error}


def test_tdx_security_bars():
    """测试TDX K线行情"""
    try:
        from tdx_client import tdx_get_security_bars
        keys, rows = tdx_get_security_bars("600519", count=10)
        if rows and len(rows) > 0:
            return _result("success", f"返回 {len(rows)} 根K线")
        return _result("warning", "返回空列表", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_quote_full():
    """测试TDX实时行情"""
    try:
        from tdx_client import tdx_get_quote_full
        data = tdx_get_quote_full("600519")
        if data and isinstance(data, dict) and data.get("price"):
            return _result("success",
                f"价格={data['price']}, 涨跌幅={data.get('change_pct',0)}%")
        return _result("failed", "", "返回空或格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_index_quote():
    """测试TDX指数行情"""
    try:
        from tdx_client import tdx_get_index_quote
        data = tdx_get_index_quote("sh000001")
        if data and isinstance(data, dict) and data.get("price"):
            return _result("success",
                f"上证指数 价格={data['price']}, 涨跌幅={data.get('change_pct',0)}%")
        return _result("failed", "", "返回空或格式异常")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_fund_flow():
    """测试TDX资金流"""
    try:
        from tdx_client import tdx_get_fund_flow
        data = tdx_get_fund_flow("600519")
        if data and isinstance(data, dict) and data.get("main_net"):
            return _result("success",
                f"主力净额={data['main_net_wan']:.0f}万")
        return _result("warning", "返回空（可能非交易时段）", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_history_fund_flow():
    """测试TDX历史资金流"""
    try:
        from tdx_client import tdx_get_history_fund_flow
        data = tdx_get_history_fund_flow("600519", days=10)
        if data and isinstance(data, list) and len(data) > 0:
            return _result("success", f"返回 {len(data)} 天历史资金流")
        return _result("warning", "返回空列表", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_finance_info():
    """测试TDX财务信息"""
    try:
        from tdx_client import _get_tdx_client, _check_tdx
        if not _check_tdx():
            return _result("failed", "", "TDX连接失败")
        client = _get_tdx_client()
        if client is None:
            return _result("failed", "", "获取TDX客户端失败")
        info = client.get_finance_info(1, "600519")
        if info is not None and not info.empty:
            ipo_date = info.iloc[0].get('ipo_date', 0)
            return _result("success", f"获取成功，上市日期={ipo_date}")
        return _result("failed", "", "get_finance_info返回空数据")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_dividend_history():
    """测试TDX分红历史"""
    try:
        from tdx_client import tdx_get_dividend_history
        data = tdx_get_dividend_history("600519")
        if data and isinstance(data, list) and len(data) > 0:
            first = data[0]
            return _result("success",
                f"返回 {len(data)} 条记录，最新 {first.get('date','')} 分红 {first.get('bonus_rmb',0)} 元")
        return _result("warning", "返回空列表（新股或无分红）", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_eps_from_reports():
    """测试TDX研报EPS"""
    try:
        from tdx_client import tdx_get_eps_from_reports
        data = tdx_get_eps_from_reports("600519")
        if data and isinstance(data, dict) and data.get("eps_cur"):
            return _result("success",
                f"今年EPS={data['eps_cur']}, 明年EPS={data.get('eps_next')}")
        return _result("warning", "返回空（可能无研报覆盖）", "")
    except Exception as e:
        return _result("failed", "", str(e))


def main():
    print("=" * 70)
    print("TDX基础接口诊断测试 V1.0")
    print("=" * 70)
    print(f"测试日期: {date.today().strftime('%Y-%m-%d')}")
    print(f"TDX间隔: {TDX_INTERVAL}s")
    print("数据源: 通达信TCP接口")

    tests = [
        ("K线行情", test_tdx_security_bars),
        ("实时行情", test_tdx_quote_full),
        ("指数行情", test_tdx_index_quote),
        ("资金流", test_tdx_fund_flow),
        ("历史资金流", test_tdx_history_fund_flow),
        ("财务信息", test_tdx_finance_info),
        ("分红历史", test_tdx_dividend_history),
        ("研报EPS", test_tdx_eps_from_reports),
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
#!/usr/bin/env python3
"""TDX板块接口诊断脚本 - 测试通达信板块/全市场接口

覆盖接口：
- tdx_get_belong_boards    所属板块
- tdx_get_board_list       板块列表
- tdx_get_board_members    板块成员
- tdx_get_all_stocks       全市场股票
"""
import sys
import os
import time
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TDX_INTERVAL = 0.3


def _result(status, data="", error=""):
    return {"status": status, "data": data, "error": error}


def test_tdx_belong_boards():
    """测试TDX所属板块"""
    try:
        from tdx_client import tdx_get_belong_boards
        # 测试上交所股票
        sh_data = tdx_get_belong_boards("600519")
        # 测试深交所股票
        sz_data = tdx_get_belong_boards("000001")
        
        sh_industry = len(sh_data.get("industry", [])) if sh_data else 0
        sz_industry = len(sz_data.get("industry", [])) if sz_data else 0
        
        if sh_industry > 0 or sz_industry > 0:
            return _result("success",
                f"上交所600519: {sh_industry}个行业板块, 深交所000001: {sz_industry}个行业板块")
        return _result("failed", "", "上交所和深交所板块获取均失败")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_board_list():
    """测试TDX板块列表"""
    try:
        from tdx_client import tdx_get_board_list
        data = tdx_get_board_list(0)  # 行业一级
        if data and isinstance(data, list) and len(data) > 0:
            return _result("success", f"返回 {len(data)} 个行业板块")
        return _result("warning", "返回空列表", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_board_members():
    """测试TDX板块成员"""
    try:
        from tdx_client import tdx_get_board_members, tdx_get_belong_boards
        # 先获取板块代码
        boards = tdx_get_belong_boards("600519")
        if not boards or not boards.get("industry"):
            return _result("warning", "无法获取板块代码", "")
        
        board_code = boards["industry"][0]["code"]
        members = tdx_get_board_members(board_code)
        
        if members and len(members) > 0:
            return _result("success",
                f"板块 {board_code} 成员 {len(members)} 只股票")
        return _result("warning", "板块成员列表为空", "")
    except Exception as e:
        return _result("failed", "", str(e))


def test_tdx_all_stocks():
    """测试TDX全市场股票"""
    try:
        from tdx_client import tdx_get_all_stocks
        data = tdx_get_all_stocks()
        if data and isinstance(data, list) and len(data) > 0:
            return _result("success", f"返回 {len(data)} 只股票")
        return _result("failed", "", "返回空列表")
    except Exception as e:
        return _result("failed", "", str(e))


def main():
    print("=" * 70)
    print("TDX板块接口诊断测试 V1.0")
    print("=" * 70)
    print(f"测试日期: {date.today().strftime('%Y-%m-%d')}")
    print(f"TDX间隔: {TDX_INTERVAL}s")
    print("数据源: 通达信MacClient接口")

    tests = [
        ("所属板块", test_tdx_belong_boards),
        ("板块列表", test_tdx_board_list),
        ("板块成员", test_tdx_board_members),
        ("全市场股票", test_tdx_all_stocks),
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
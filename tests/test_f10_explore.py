#!/usr/bin/env python3
"""探索 F10 最新提示分类的原始数据格式"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_client import _get_tdx_client, _market_from_code, _TDX_CALL_LOCK, _tdx_throttle

code = "600519"
market = _market_from_code(code)

with _TDX_CALL_LOCK:
    client = _get_tdx_client()
    if client is None:
        print("TDX client None")
        sys.exit(1)

    cats = client.get_company_info_category(market, code)
    print("=== F10 分类列表 ===")
    if cats is not None and not cats.empty:
        for _, row in cats.iterrows():
            print(f"  {row['name']}")

    # 只获取「最新提示」
    target = cats[cats['name'] == '最新提示']
    if target.empty:
        print("最新提示: 未找到")
        sys.exit(0)
    row = target.iloc[0]
    _tdx_throttle()
    content = client.get_company_info_content(
        market, code,
        row['filename'], int(row['start']), int(row['length'])
    )
    print(f"\n=== 最新提示 (length={len(content) if content else 0}) ===")
    if content:
        print(content[:5000])
        if len(content) > 5000:
            print(f"\n... (省略 {len(content) - 5000} 字符)")

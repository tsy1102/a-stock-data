#!/usr/bin/env python3
"""探索 F10 最新提示分类后半部分"""
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
    target = cats[cats['name'] == '最新提示']
    row = target.iloc[0]
    _tdx_throttle()
    content = client.get_company_info_content(
        market, code,
        row['filename'], int(row['start']), int(row['length'])
    )
    # 打印 5000-15000 范围
    print(content[5000:])

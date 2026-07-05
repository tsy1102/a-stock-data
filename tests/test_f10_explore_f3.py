#!/usr/bin/env python3
"""探索 F10 财务分析分类的原始数据格式"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_client import _get_tdx_client, _market_from_code, _TDX_CALL_LOCK, _tdx_throttle

code = "600519"  # 贵州茅台
market = _market_from_code(code)

with _TDX_CALL_LOCK:
    client = _get_tdx_client()
    if client is None:
        print("TDX client None")
        sys.exit(1)

    cats = client.get_company_info_category(market, code)
    target = cats[cats['name'] == '财务分析']
    if target.empty:
        print("财务分析: 未找到")
        sys.exit(0)
    row = target.iloc[0]
    _tdx_throttle()
    content = client.get_company_info_content(
        market, code,
        row['filename'], int(row['start']), int(row['length'])
    )
    print(f"=== 财务分析 (length={len(content) if content else 0}) ===")
    # 写入 UTF-8 文件以便分析
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'f3_content_600519.txt'), 'w', encoding='utf-8') as f:
        f.write(content or '')
    # 列出所有子栏目位置
    import re
    matches = list(re.finditer(r'【(\d+)\.(.+?)】', content or ''))
    print(f"\n找到 {len(matches)} 个子栏目:")
    for m in matches:
        print(f"  section {m.group(1)}: {m.group(2)} at pos {m.start()}")

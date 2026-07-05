#!/usr/bin/env python3
"""探索 000001 的 F3 财务分析结构 + 调试 600519 指标变动重复问题"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_client import _get_tdx_client, _market_from_code, _TDX_CALL_LOCK, _tdx_throttle
from stock_common.f10_parser import split_sections, parse_table, parse_tables, merge_continuation_lines
import re

# 1. 检查 000001 是否有「资产负债表摘要」
code = "000001"
market = _market_from_code(code)
with _TDX_CALL_LOCK:
    client = _get_tdx_client()
    if client is None:
        print("TDX client None")
        sys.exit(1)
    cats = client.get_company_info_category(market, code)
    target = cats[cats['name'] == '财务分析']
    row = target.iloc[0]
    _tdx_throttle()
    content = client.get_company_info_content(
        market, code, row['filename'], int(row['start']), int(row['length'])
    )
    print(f"=== 000001 财务分析 (length={len(content)}) ===")
    sections = split_sections(content)
    print("子栏目:", list(sections.keys()))

# 2. 调试 600519 的 2026-03-31 指标变动重复问题
print("\n" + "="*60)
print("调试 600519 指标变动说明")
print("="*60)
code = "600519"
market = _market_from_code(code)
with _TDX_CALL_LOCK:
    cats = client.get_company_info_category(market, code)
    target = cats[cats['name'] == '财务分析']
    row = target.iloc[0]
    _tdx_throttle()
    content = client.get_company_info_content(
        market, code, row['filename'], int(row['start']), int(row['length'])
    )
    sections = split_sections(content)
    s6 = sections.get('指标变动说明', '')
    # 按截止日期分割
    parts = re.split(r'截止日期[:：]\s*(\d{4}-\d{2}-\d{2})', s6)
    for i in range(1, len(parts), 2):
        period = parts[i]
        block_text = parts[i + 1] if i + 1 < len(parts) else ''
        print(f"\n--- 期 {period} ---")
        merged = merge_continuation_lines(block_text, num_text_cols=2)
        rows = parse_table(merged)
        print(f"  解析到 {len(rows)} 行")
        for idx, r in enumerate(rows):
            print(f"  行{idx}: subject={r.get('变动科目','')[:40]!r}, current={r.get('本期数值(万)','')}")

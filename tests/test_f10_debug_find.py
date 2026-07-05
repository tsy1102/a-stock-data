#!/usr/bin/env python3
"""调试 find_subsection 对 600519 的行为"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_client import _f10_get_content, _TDX_CALL_LOCK
from stock_common.f10_parser import split_sections, find_subsection, parse_tables

code = "600519"
with _TDX_CALL_LOCK:
    content = _f10_get_content(code, '财务分析')
    print(f"content length: {len(content)}")

sections = split_sections(content)
print(f"sections keys: {list(sections.keys())}")

# 测试 find_subsection
for name in ['主要财务指标', '偿债能力指标', '盈利能力指标', '资产负债表摘要']:
    s = find_subsection(sections, name)
    print(f"\nfind_subsection({name!r}): length={len(s)}")
    if s:
        print(f"  前100字符: {s[:100]!r}")
        tables = parse_tables(s)
        print(f"  parse_tables 返回 {len(tables)} 个表格")

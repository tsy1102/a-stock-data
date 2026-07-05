#!/usr/bin/env python3
"""探索阶段一函数3-7所需的F10分类结构（F4/F5/F13/F15/F16）"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tdx_client import _f10_get_content, _TDX_CALL_LOCK
from stock_common.f10_parser import split_sections
import re

code = "600519"

categories = [
    ('F4', '股本结构'),
    ('F5', '股东研究'),
    ('F13', '公司报道'),
    ('F15', '行业分析'),
    ('F16', '研报评级'),
]

for label, cat_name in categories:
    print(f"\n{'='*70}")
    print(f"{label} {cat_name} — {code}")
    print('='*70)
    with _TDX_CALL_LOCK:
        content = _f10_get_content(code, cat_name)
    if not content:
        print("  ❌ 无内容")
        continue
    print(f"内容长度: {len(content)} 字符")
    # 打印 header（前3行）
    header_lines = content.split('\n')[:4]
    for h in header_lines:
        print(f"  HDR: {h[:120]}")
    # split_sections
    sections = split_sections(content)
    print(f"\n  sections ({len(sections)} 个):")
    for k, v in sections.items():
        # 检查是否有暂无数据
        has_data = '暂无数据' not in v[:50]
        # 检查是否有表格
        has_table = '┌' in v
        # 检查是否有段落块
        has_para = bool(re.search(r'\d{4}-\d{2}-\d{2}', v))
        print(f"    {k!r}: len={len(v):5d} data={'Y' if has_data else 'N'} table={'Y' if has_table else 'N'} para={'Y' if has_para else 'N'}")
        # 显示前80字符
        if v:
            preview = v[:80].replace('\n', ' | ').replace('\r', '')
            print(f"      preview: {preview!r}")

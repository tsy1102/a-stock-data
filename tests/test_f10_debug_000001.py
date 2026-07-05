#!/usr/bin/env python3
"""直接测试 split_sections 对 000001 的行为"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_common.f10_parser import split_sections

content = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'f3_content_000001.txt'), encoding='utf-8').read()
print(f"总长度: {len(content)}")

sections = split_sections(content)
print(f"\nsplit_sections 返回 {len(sections)} 个子栏目:")
for k, v in sections.items():
    print(f"  {k!r}: 长度={len(v)}, 前80字符={v[:80]!r}")

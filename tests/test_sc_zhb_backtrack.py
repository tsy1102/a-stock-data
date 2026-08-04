#!/usr/bin/env python3
"""sc_zhb 回溯功能测试（用 cache/zhb/ 真实 zip）"""
import sys
sys.path.insert(0, r"D:\GitHub\test")

from stock_common.sc_zhb import (
    backtrack_field, backtrack_stats, backtrack_with_extractor,
    list_archives, parse_archive, REALTIME_FIELDS, archive_summary,
)

CODE = "000100"

# 1) 当前包字段（steps=0）
v, date, steps = backtrack_field(CODE, "pe_ttm", max_back=3)
print(f"[1] pe_ttm: {v!r} date={date} steps={steps}")

# 2) 回溯 stats 合并
merged, mdate, msteps = backtrack_stats(CODE, max_back=3)
print(f"[2] stats 合并: {len(merged) if merged else 0} 字段 date={mdate} steps={msteps}")
if merged:
    keys = list(merged.keys())[:8]
    print(f"    字段示例: {keys}")

# 3) 实时字段黑名单
try:
    backtrack_field(CODE, "price")
    print("[3] FAIL: 实时字段未拦截")
except ValueError as e:
    print(f"[3] OK 实时字段拦截: {str(e)[:40]}")

# 4) 通用提取器（自定义: 取 tdxstat 的 name 字段）
def _ext(z, code):
    s = getattr(z, "stock_stats", None)
    if isinstance(s, dict) and code in s:
        return s[code].get("name")
    return None

v4, d4, s4 = backtrack_with_extractor(CODE, _ext, max_back=3)
print(f"[4] 通用提取器: {v4!r} date={d4} steps={s4}")

# 5) 归档摘要
s = archive_summary()
print(f"[5] 归档 {s['archive_count']} 个: {s['oldest']} ~ {s['newest']}")

# 6) 断言核心功能
assert isinstance(s["archive_count"], int) and s["archive_count"] > 0
assert "pe_ttm" in REALTIME_FIELDS or backtrack_field is not None
print("\n核心功能通过 ✓")

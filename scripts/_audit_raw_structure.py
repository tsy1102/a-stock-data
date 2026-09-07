#!/usr/bin/env python3
"""_audit_raw_structure.py — 探查各源 raw_*.json 原始结构，为字段命名对齐做准备。

仅打印结构（顶层类型 / 键数 / 样本），不写盘。
"""
from __future__ import annotations
import io, os, json

for _s in (io,):
    pass
CAP = "docs/field_verification/20260904"

def info(p):
    d = json.load(io.open(p, encoding="utf-8"))
    t = type(d).__name__
    if isinstance(d, dict):
        keys = list(d.keys())
        n = len(keys)
        # classify
        sample_v = next(iter(d.values())) if keys else None
        svt = type(sample_v).__name__
        extra = ""
        if isinstance(sample_v, dict):
            extra = f" inner_keys={list(sample_v.keys())[:12]}"
        elif isinstance(sample_v, list):
            extra = f" inner_is_list len={len(sample_v)}"
        return f"dict n={n} val_type={svt} keys[:12]={keys[:12]}{extra}"
    if isinstance(d, list):
        return f"list len={len(d)} elem0_type={type(d[0]).__name__ if d else 'NA'}"
    if isinstance(d, str):
        return f"str len={len(d)} head={d[:80]!r}"
    return f"{t} val={repr(d)[:80]}"

files = sorted(os.listdir(CAP))
print(f"=== {CAP} ({len(files)} files) ===")
for f in files:
    if not f.startswith("raw_") or not f.endswith(".json"):
        continue
    p = os.path.join(CAP, f)
    try:
        s = info(p)
    except Exception as e:
        s = f"ERR {e!r}"
    print(f"{f:32s} {s}")

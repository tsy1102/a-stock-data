#!/usr/bin/env python3
"""_audit_raw_deep.py — 深入探查各源 raw 内层字段名，对照 field_dict.md 命名约定。"""
from __future__ import annotations
import io, os, json

CAP = "docs/field_verification/20260904"

def load(f):
    return json.load(io.open(os.path.join(CAP, f), encoding="utf-8"))

def leaf_paths(obj, prefix="", depth=0, out=None):
    if out is None:
        out = []
    if depth > 6:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.startswith("__"):
                continue
            p = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, (dict, list)) and v and depth < 6:
                leaf_paths(v, p, depth+1, out)
            else:
                out.append(p)
    elif isinstance(obj, list) and obj:
        # sample first non-empty element
        for el in obj[:3]:
            if isinstance(el, (dict, list)):
                leaf_paths(el, prefix, depth+1, out)
                break
    return out

# ---- stocks-wrapped dict sources ----
print("### push2_full inner keys (one stock) ###")
d = load("raw_push2_full.json")
stk = next(iter(d["stocks"].values()))
print("  type:", type(stk).__name__, "n=", len(stk) if isinstance(stk, dict) else "NA")
if isinstance(stk, dict):
    print("  keys:", sorted(stk.keys())[:40])

print("### ulist239 inner keys (one stock) ###")
d = load("raw_ulist239.json")
stk = next(iter(d["stocks"].values()))
if isinstance(stk, dict):
    print("  n=", len(stk), "keys:", sorted(stk.keys())[:40])

print("### tencent inner keys (one stock) ###")
d = load("raw_tencent.json")
stk = next(iter(d["stocks"].values()))
if isinstance(stk, dict):
    print("  n=", len(stk), "keys[:20]:", sorted(stk.keys())[:20])
    # show a couple samples
    for k in sorted(stk.keys())[:3]:
        print(f"    {k} = {repr(stk[k])[:60]}")

print("### sina inner keys (one stock) ###")
d = load("raw_sina.json")
stk = next(iter(d["stocks"].values()))
if isinstance(stk, dict):
    print("  n=", len(stk), "keys[:20]:", sorted(stk.keys())[:20])
elif isinstance(stk, str):
    print("  STR head:", stk[:120])

print("### tdx inner keys (one stock) ###")
d = load("raw_tdx.json")
stk = next(iter(d["stocks"].values()))
if isinstance(stk, dict):
    print("  n=", len(stk), "keys[:30]:", sorted(stk.keys())[:30])

print("### tdx_f10 inner keys (one stock) ###")
d = load("raw_tdx_f10.json")
stk = next(iter(d["stocks"].values()))
if isinstance(stk, dict):
    print("  n=", len(stk), "keys[:30]:", sorted(stk.keys())[:30])

print("### fuyao one stock leaf paths ###")
d = load("raw_fuyao.json")
stk = next(iter(d["stocks"].values()))
paths = leaf_paths(stk)
print("  leaf count:", len(paths))
print("  sample:", sorted(paths)[:40])

print("### fuyao top-level (non-stocks) keys ###")
print("  ", [k for k in d.keys()])

print("### cls telegraph item keys ###")
d = load("raw_cls.json")
item = d["telegraph"][0]
print("  type:", type(item).__name__, "keys:", list(item.keys()) if isinstance(item, dict) else repr(item)[:80])

print("### em_hot hot_rank item keys ###")
d = load("raw_em_hot.json")
item = d["hot_rank"][0]
print("  type:", type(item).__name__, "keys:", list(item.keys()) if isinstance(item, dict) else repr(item)[:80])

print("### push2ex pools ###")
d = load("raw_push2ex.json")
for k, v in d.items():
    if isinstance(v, list) and v:
        print(f"  {k}: list n={len(v)} item_keys={list(v[0].keys())[:20] if isinstance(v[0],dict) else type(v[0]).__name__}")

print("### market_sources sub-keys ###")
d = load("raw_market_sources.json")
for k, v in d.items():
    if isinstance(v, list) and v:
        print(f"  {k}: list n={len(v)} item_keys={list(v[0].keys())[:20] if isinstance(v[0],dict) else type(v[0]).__name__}")
    elif isinstance(v, dict):
        print(f"  {k}: dict n={len(v)} keys={list(v.keys())[:15]}")
    else:
        print(f"  {k}: {type(v).__name__} = {repr(v)[:40]}")

print("### zhb structure ###")
d = load("raw_zhb.json")
print("  zhb_date:", repr(d.get("zhb_date"))[:60])
st = d.get("stocks")
print("  stocks type:", type(st).__name__, "len:", len(st) if hasattr(st,'__len__') else 'NA')
if isinstance(st, str):
    print("  stocks head:", st[:200])
elif isinstance(st, dict):
    print("  stocks keys:", list(st.keys())[:10])

print("### thsdk ###")
d = load("raw_thsdk.json")
print("  keys:", list(d.keys()))
print("  stocks:", d.get("stocks"))
print("  error:", repr(d.get("error"))[:200])

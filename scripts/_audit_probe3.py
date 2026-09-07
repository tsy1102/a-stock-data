#!/usr/bin/env python3
"""_audit_probe3.py v2 — data 是 dict，直接枚举 fN 键。"""
from __future__ import annotations
import io, os, json, re
CAP = "docs/field_verification/20260904"
def load(f): return json.load(io.open(os.path.join(CAP, f), encoding="utf-8"))

def dump_dict_keys(name, d):
    if isinstance(d, dict):
        ks = list(d.keys())
        print(f"  {name}: dict n={len(ks)} keys[:50]={ks[:50]}")
        return ks
    print(f"  {name}: {type(d).__name__}")
    return []

print("### push2_full ###")
d = load("raw_push2_full.json"); stk = next(iter(d["stocks"].values()))
print("  stock keys:", list(stk.keys()))
data = stk.get("data")
fns = dump_dict_keys("data", data)
fnset = sorted(set(int(k[1:]) for k in fns if re.fullmatch(r"f\d+", str(k))))
print("  fN numeric set size:", len(fnset), "min:", fnset[0] if fnset else None, "max:", fnset[-1] if fnset else None)
print("  fnset sample:", [f"f{x}" for x in fnset[:8]], "...", [f"f{x}" for x in fnset[-8:]])

print("### ulist239 ###")
d = load("raw_ulist239.json"); stk = next(iter(d["stocks"].values()))
data = stk.get("data")
fns = dump_dict_keys("data", data)
fnset = sorted(set(int(k[1:]) for k in fns if re.fullmatch(r"f\d+", str(k)))
               | set(int(k) for k in fns if re.fullmatch(r"\d+", str(k))))
print("  fN numeric set size:", len(fnset), "min:", fnset[0], "max:", fnset[-1])
print("  sample:", [str(x) for x in fnset[:10]], "...", [str(x) for x in fnset[-10:]])

print("### tencent ###")
d = load("raw_tencent.json"); stk = next(iter(d["stocks"].values()))
fields = stk.get("fields")
print("  n_fields:", stk.get("n_fields"), "fields type:", type(fields).__name__, "len:", len(fields) if isinstance(fields,(list,str)) else None)
if isinstance(fields, list): print("  fields[:5]:", fields[:5])

print("### zhb ###")
d = load("raw_zhb.json")
stocks = d.get("stocks")
print("  zhb_date:", d.get("zhb_date"), "stocks type:", type(stocks).__name__)
if isinstance(stocks, dict):
    sk = next(iter(stocks.values()))
    print("  one stock type:", type(sk).__name__)
    if isinstance(sk, dict):
        print("  one stock keys (first 60):", list(sk.keys())[:60], "n=", len(sk))
    elif isinstance(sk, str):
        print("  one stock str head:", sk[:300])

print("### sina ###")
d = load("raw_sina.json"); stk = next(iter(d["stocks"].values()))
print("  stock keys:", list(stk.keys()), "n_fields:", stk.get("n_fields"))
fld = stk.get("fields")
print("  fields type:", type(fld).__name__, "len:", len(fld) if isinstance(fld,(list,str)) else None)
if isinstance(fld, str): print("  fields head:", fld[:200])

print("### tdx ###")
d = load("raw_tdx.json"); stk = next(iter(d["stocks"].values()))
fi = stk.get("finance_info"); qf = stk.get("quote_full")
print("  finance_info type:", type(fi).__name__, "keys:", list(fi.keys())[:25] if isinstance(fi,dict) else None, "n=", len(fi) if isinstance(fi,dict) else None)
print("  quote_full type:", type(qf).__name__, "keys:", list(qf.keys())[:25] if isinstance(qf,dict) else None, "n=", len(qf) if isinstance(qf,dict) else None)

print("### tdx_f10 ###")
d = load("raw_tdx_f10.json"); stk = next(iter(d["stocks"].values()))
print("  keys:", list(stk.keys()))
for k,v in stk.items():
    if isinstance(v, dict): print(f"    {k}: dict n={len(v)} keys[:15]={list(v.keys())[:15]}")
    elif isinstance(v, list): print(f"    {k}: list n={len(v)}")

print("### datacenter ###")
d = load("raw_datacenter.json"); stk = next(iter(d["stocks"].values()))
print("  one stock type:", type(stk).__name__)
if isinstance(stk, dict): print("  one stock keys (first 30):", list(stk.keys())[:30], "n=", len(stk))

print("### em_fund_flow ###")
d = load("raw_em_fund_flow.json"); stk = next(iter(d["stocks"].values()))
if isinstance(stk, dict): print("  one stock keys:", list(stk.keys())[:30], "n=", len(stk))

print("### ftshare ###")
d = load("raw_ftshare.json")
print("  top keys:", list(d.keys()))
stk = next(iter(d["stocks"].values()))
if isinstance(stk, dict): print("  one stock keys:", list(stk.keys())[:30], "n=", len(stk))

print("### axdata ###")
d = load("raw_axdata.json"); stk = next(iter(d["stocks"].values()))
if isinstance(stk, dict): print("  one stock keys:", list(stk.keys())[:20], "n=", len(stk))

print("### cninfo ###")
d = load("raw_cninfo.json"); stk = next(iter(d["stocks"].values()))
if isinstance(stk, dict): print("  one stock keys:", list(stk.keys())[:20], "n=", len(stk))

print("### reports ###")
d = load("raw_reports.json"); stk = next(iter(d["stocks"].values()))
if isinstance(stk, dict): print("  one stock keys:", list(stk.keys())[:20], "n=", len(stk))

print("### em_kline_f61 ###")
d = load("raw_em_kline_f61.json"); stk = next(iter(d["stocks"].values()))
if isinstance(stk, dict): print("  one stock keys:", list(stk.keys())[:20], "n=", len(stk))

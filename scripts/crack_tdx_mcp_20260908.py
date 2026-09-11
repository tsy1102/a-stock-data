# -*- coding: utf-8 -*-
"""第十二轮字段破解：以通达信(TDX)云行情 MCP 快照为独立第四源，与腾讯/push2/ZHB 全域对撞。

设计要点（遵循 docs/field_verification/CRACKING_METHODOLOGY.md 四铁律）：
  1. 精度对齐：|a-b| <= max(ulp(a),ulp(b)) * tol_ulp  判定「等值」
  2. 命中率分层：>=18/20 -> L1 候选；8~17 -> L4；<8 -> 噪声
  3. 全域扫描：不预设假设，用 TDX 锚点扫描腾讯 fields[0..87] 与 push2 全部 fX
  4. ZHB 按 zhb_date 对齐（T-1），不与 T 日行情混算

TDX MCP 仅作破解真值锚点，不进入运行时取数路径。
"""
from __future__ import annotations

import io
import json
import math
import os
import sys
from collections import OrderedDict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAY = "20260908"
FV = os.path.join(BASE, "docs", "field_verification")
DDIR = os.path.join(FV, DAY)


def load(name, day=DAY):
    p = os.path.join(FV, day, name)
    if not os.path.exists(p):
        return None
    with io.open(p, encoding="utf-8") as fh:
        return json.load(fh)


def to_f(v):
    """宽松转 float：'-' / '' / None / 非数 -> None"""
    if v is None:
        return None
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        f = float(v)
        return None if (math.isnan(f) or math.isinf(f)) else f
    s = str(v).strip().replace(",", "")
    if s in ("", "-", "--", "null", "None", "N/A"):
        return None
    try:
        f = float(s)
    except Exception:
        return None
    return None if (math.isnan(f) or math.isinf(f)) else f


def ulp_of(v):
    """按字面量小数位推 ulp；float 用机器 ulp 兜底。"""
    s = repr(v)
    if "e" in s or "E" in s:
        return abs(v) * 1e-12 if v else 1e-12
    if "." in s:
        dec = len(s.split(".")[1])
        return 10.0 ** (-dec)
    return 1.0


def eq_ulp(a, b, tol_ulp=1.0):
    if a is None or b is None:
        return False
    return abs(a - b) <= max(ulp_of(a), ulp_of(b)) * tol_ulp


def rel_err(a, b):
    if a is None or b is None:
        return None
    d = max(abs(a), abs(b))
    if d == 0:
        return 0.0
    return abs(a - b) / d


# ---------------------------------------------------------------- 数据装载
tdx = load("raw_tdx_mcp.json")
tx = load("raw_tencent.json")
p2 = load("raw_push2_full.json")
zhb = load("raw_zhb.json")

assert tdx and tx and p2, "缺少必要数据源"

TDXS = tdx["stocks"]
TXS = tx["stocks"]
P2S = p2["stocks"]
CODES = sorted(set(TDXS) & set(TXS) & set(P2S))

print("=" * 78)
print("第十二轮 · 通达信 MCP 四源对撞  采集日=%s  TDX HQDate=%s" % (DAY, tdx["hq_date"]))
print("样本 %d 只：%s" % (len(CODES), ",".join(CODES)))
print("=" * 78)


def tx_field(code, idx):
    f = TXS.get(code, {}).get("fields") or []
    return to_f(f[idx]) if idx < len(f) else None


def p2_field(code, key):
    return to_f((P2S.get(code, {}).get("data") or {}).get(key))


TX_MAX = max(len(TXS[c].get("fields") or []) for c in CODES)
P2_KEYS = sorted(
    {k for c in CODES for k in (P2S[c].get("data") or {}).keys()},
    key=lambda s: (len(s), s),
)
print("腾讯字段位宽=%d   push2 字段数=%d" % (TX_MAX, len(P2_KEYS)))


# ------------------------------------------------- 通用：TDX 锚点全域扫描
def scan_anchor(anchor_name, anchor_fn, transforms=None):
    """用一个 TDX 锚点扫描腾讯全字段 + push2 全字段，返回命中排行。

    transforms: [(标签, lambda 锚值 -> 期望值)]，用于比值族（如 手<->股）
    """
    transforms = transforms or [("原值", lambda x: x)]
    rows = []
    for tag, fn in transforms:
        # 腾讯
        for idx in range(TX_MAX):
            hit = 0
            tot = 0
            errs = []
            for c in CODES:
                a = anchor_fn(c)
                b = tx_field(c, idx)
                if a is None or b is None:
                    continue
                try:
                    a2 = fn(a)
                except Exception:
                    continue
                if a2 is None:
                    continue
                tot += 1
                if eq_ulp(a2, b):
                    hit += 1
                e = rel_err(a2, b)
                if e is not None:
                    errs.append(e)
            if tot >= 8:
                rows.append(("tx[%d]" % idx, tag, hit, tot,
                             (sum(errs) / len(errs)) if errs else None))
        # push2
        for k in P2_KEYS:
            hit = 0
            tot = 0
            errs = []
            for c in CODES:
                a = anchor_fn(c)
                b = p2_field(c, k)
                if a is None or b is None:
                    continue
                try:
                    a2 = fn(a)
                except Exception:
                    continue
                if a2 is None:
                    continue
                tot += 1
                if eq_ulp(a2, b):
                    hit += 1
                e = rel_err(a2, b)
                if e is not None:
                    errs.append(e)
            if tot >= 8:
                rows.append(("p2.%s" % k, tag, hit, tot,
                             (sum(errs) / len(errs)) if errs else None))
    rows.sort(key=lambda r: (-r[2], r[4] if r[4] is not None else 9e9))
    print("\n" + "-" * 78)
    print("【锚点扫描】TDX %s" % anchor_name)
    print("-" * 78)
    print("%-12s %-8s %-9s %s" % ("字段", "变换", "等值命中", "平均相对误差"))
    shown = 0
    for name, tag, hit, tot, ae in rows:
        if hit == 0 and (ae is None or ae > 0.05):
            continue
        lvl = "L1" if hit >= 18 else ("L4" if hit >= 8 else "  ")
        print("%-12s %-8s %2d/%-6d %s  %s" % (
            name, tag, hit, tot,
            ("%.6f%%" % (ae * 100)) if ae is not None else "n/a", lvl))
        shown += 1
        if shown >= 12:
            break
    if shown == 0:
        print("(无命中，且无字段平均相对误差 <5%)")
    return rows


A = lambda c: TDXS[c].get("average")
IN = lambda c: TDXS[c].get("inside")
OUT = lambda c: TDXS[c].get("outside")
VOL = lambda c: TDXS[c].get("volume")
AMT = lambda c: TDXS[c].get("amount")
WTB = lambda c: TDXS[c].get("wtb")
PE = lambda c: TDXS[c].get("pe_ttm")

scan_anchor("HQInfo.Average 均价", A)
scan_anchor("ProInfo.Wtb 委比%", WTB)
scan_anchor("HQInfo.Inside 内盘(手)", IN,
            [("原值(手)", lambda x: x), ("x100(股)", lambda x: x * 100.0)])
scan_anchor("HQInfo.Outside 外盘(手)", OUT,
            [("原值(手)", lambda x: x), ("x100(股)", lambda x: x * 100.0)])
scan_anchor("HQInfo.Volume 成交量(手)", VOL,
            [("原值(手)", lambda x: x), ("x100(股)", lambda x: x * 100.0)])
scan_anchor("HQInfo.Amount 成交额(元)", AMT,
            [("原值(元)", lambda x: x), ("/1e4(万元)", lambda x: x / 1e4)])
scan_anchor("ProInfo TTM市盈率", PE)


# ------------------------------------------- 焦点一：tx[85] 是否真是均价
print("\n" + "=" * 78)
print("【焦点一】tx[85] vs 通达信均价（精确锚）—— 检验 L1-U 定级是否站得住")
print("=" * 78)
print("%-8s %12s %12s %10s %12s %12s %10s" % (
    "code", "TDX均价", "tx[85]", "误差%", "VWAP(p2)", "tx[51]", "tx[51]误差%"))
n85_ok = n85_tot = 0
n51_ok = n51_tot = 0
vwap_ok = vwap_tot = 0
for c in CODES:
    a = A(c)
    v85 = tx_field(c, 85)
    v51 = tx_field(c, 51)
    f47 = p2_field(c, "f47")
    f48 = p2_field(c, "f48")
    vwap = (f48 / (f47 * 100.0)) if (f47 and f48) else None
    e85 = rel_err(a, v85)
    e51 = rel_err(a, v51)
    if a is not None and vwap is not None:
        vwap_tot += 1
        if rel_err(a, vwap) is not None and rel_err(a, vwap) < 1e-5:
            vwap_ok += 1
    if a is not None and v85 is not None:
        n85_tot += 1
        if eq_ulp(a, v85, 2.0):
            n85_ok += 1
    if a is not None and v51 is not None:
        n51_tot += 1
        if eq_ulp(a, v51, 2.0):
            n51_ok += 1
    print("%-8s %12s %12s %10s %12s %12s %10s" % (
        c,
        "%.6f" % a if a is not None else "-",
        "%.4f" % v85 if v85 is not None else "-",
        "%.4f" % (e85 * 100) if e85 is not None else "-",
        "%.6f" % vwap if vwap is not None else "-",
        "%.4f" % v51 if v51 is not None else "-",
        "%.4f" % (e51 * 100) if e51 is not None else "-",
    ))
print("\nTDX均价 == push2 VWAP(f48/f47/100) 精确一致: %d/%d" % (vwap_ok, vwap_tot))
print("TDX均价 == tx[85] 精度对齐命中: %d/%d" % (n85_ok, n85_tot))
print("TDX均价 == tx[51] 精度对齐命中: %d/%d" % (n51_ok, n51_tot))

# tx[85] 若非均价，扫描其他可能：最高/最低/昨收/振幅相关
print("\n>>> tx[85] 另寻其解：与腾讯自身/push2 各字段等值扫描")
rows = []
for idx in range(TX_MAX):
    if idx == 85:
        continue
    hit = tot = 0
    for c in CODES:
        a = tx_field(c, 85)
        b = tx_field(c, idx)
        if a is None or b is None:
            continue
        tot += 1
        if eq_ulp(a, b):
            hit += 1
    if tot >= 8:
        rows.append(("tx[%d]" % idx, hit, tot))
for k in P2_KEYS:
    hit = tot = 0
    for c in CODES:
        a = tx_field(c, 85)
        b = p2_field(c, k)
        if a is None or b is None:
            continue
        tot += 1
        if eq_ulp(a, b):
            hit += 1
    if tot >= 8:
        rows.append(("p2.%s" % k, hit, tot))
rows.sort(key=lambda r: -r[1])
for name, hit, tot in rows[:10]:
    if hit == 0:
        break
    print("   tx[85] == %-10s %2d/%d" % (name, hit, tot))

# 派生假设：(high+low)/2, (high+low+close)/3, (open+high+low+close)/4
print("\n>>> tx[85] 价格派生假设检验（用 push2 f44高/f45低/f43现/f46开/f60昨收）")
cand = OrderedDict([
    ("(H+L)/2", lambda d: (d["h"] + d["l"]) / 2 if d["h"] and d["l"] else None),
    ("(H+L+C)/3", lambda d: (d["h"] + d["l"] + d["c"]) / 3 if d["h"] and d["l"] and d["c"] else None),
    ("(O+H+L+C)/4", lambda d: (d["o"] + d["h"] + d["l"] + d["c"]) / 4 if all([d["o"], d["h"], d["l"], d["c"]]) else None),
    ("H最高", lambda d: d["h"]),
    ("L最低", lambda d: d["l"]),
    ("PC昨收", lambda d: d["pc"]),
])
res = {k: [0, 0, []] for k in cand}
for c in CODES:
    d = {"h": p2_field(c, "f44"), "l": p2_field(c, "f45"), "c": p2_field(c, "f43"),
         "o": p2_field(c, "f46"), "pc": p2_field(c, "f60")}
    v85 = tx_field(c, 85)
    for k, fn in cand.items():
        try:
            x = fn(d)
        except Exception:
            x = None
        if x is None or v85 is None:
            continue
        res[k][1] += 1
        if eq_ulp(x, v85, 2.0):
            res[k][0] += 1
        e = rel_err(x, v85)
        if e is not None:
            res[k][2].append(e)
for k, (hit, tot, errs) in res.items():
    ae = (sum(errs) / len(errs) * 100) if errs else None
    print("   %-14s 命中 %2d/%-3d 平均误差 %s" % (
        k, hit, tot, ("%.4f%%" % ae) if ae is not None else "n/a"))


# --------------------------------------- 焦点二：tx[86] 委差 & push2 f191/f192
print("\n" + "=" * 78)
print("【焦点二】tx[86] vs 委差族（push2 f192 委差 / f191 委比 / TDX Wtb）")
print("=" * 78)
print("%-8s %10s %10s %10s %10s %8s %8s" % (
    "code", "tx[86]", "p2.f192", "p2.f191", "TDX_Wtb", "f191=Wtb", "同号"))
same_sign = sign_tot = 0
f191_eq = f191_tot = 0
f192_eq = f192_tot = 0
ratio = []
for c in CODES:
    v86 = tx_field(c, 86)
    f192 = p2_field(c, "f192")
    f191 = p2_field(c, "f191")
    w = WTB(c)
    if f191 is not None and w is not None:
        f191_tot += 1
        if eq_ulp(f191, w, 2.0):
            f191_eq += 1
    if v86 is not None and f192 is not None:
        f192_tot += 1
        if eq_ulp(v86, f192, 2.0):
            f192_eq += 1
        if f192 != 0:
            ratio.append(v86 / f192)
    ok_sign = ""
    if v86 is not None and w is not None:
        sign_tot += 1
        if (v86 >= 0) == (w >= 0):
            same_sign += 1
            ok_sign = "Y"
        else:
            ok_sign = "N"
    print("%-8s %10s %10s %10s %10s %8s %8s" % (
        c,
        "%.0f" % v86 if v86 is not None else "-",
        "%.0f" % f192 if f192 is not None else "-",
        "%.2f" % f191 if f191 is not None else "-",
        "%.2f" % w if w is not None else "-",
        "Y" if (f191 is not None and w is not None and eq_ulp(f191, w, 2.0)) else "N",
        ok_sign,
    ))
print("\npush2 f191 == TDX 委比 命中: %d/%d" % (f191_eq, f191_tot))
print("tx[86] == push2 f192 等值命中: %d/%d" % (f192_eq, f192_tot))
print("tx[86] 与 TDX 委比 同号率: %d/%d (%.1f%%)" % (
    same_sign, sign_tot, 100.0 * same_sign / sign_tot if sign_tot else 0))
if ratio:
    ratio_s = sorted(ratio)
    print("tx[86]/f192 比值：min=%.4f  median=%.4f  max=%.4f" % (
        ratio_s[0], ratio_s[len(ratio_s) // 2], ratio_s[-1]))

# 委差自洽检验：委比 = (委买-委卖)/(委买+委卖)*100
print("\n>>> 委比自洽：TDX Wtb 是否 = f192/(委买+委卖)*100 ? 反解隐含总委托量")
for c in CODES:
    f192 = p2_field(c, "f192")
    w = WTB(c)
    v86 = tx_field(c, 86)
    if f192 and w:
        tot_ord = f192 / (w / 100.0)
        imp86 = (v86 / (w / 100.0)) if v86 else None
        print("   %-8s f192=%8.0f Wtb=%7.2f -> 隐含总委托=%10.1f 手 | tx[86]=%8s 隐含=%s" % (
            c, f192, w, tot_ord,
            "%.0f" % v86 if v86 is not None else "-",
            "%.1f" % imp86 if imp86 is not None else "-"))


# ------------------------------------------------- 焦点三：tx[7]/tx[8] 内外盘
print("\n" + "=" * 78)
print("【焦点三】内/外盘复核 tx[7]/tx[8] vs TDX Inside/Outside")
print("=" * 78)
print("%-8s %10s %10s %10s %10s %10s %10s" % (
    "code", "tx[7]", "TDX_In", "In*100", "tx[8]", "TDX_Out", "Out*100"))
in_hit = in_tot = out_hit = out_tot = 0
for c in CODES:
    t7, t8 = tx_field(c, 7), tx_field(c, 8)
    i, o = IN(c), OUT(c)
    if t7 is not None and i is not None:
        in_tot += 1
        if eq_ulp(t7, i * 100.0, 200.0) or eq_ulp(t7, i, 2.0):
            in_hit += 1
    if t8 is not None and o is not None:
        out_tot += 1
        if eq_ulp(t8, o * 100.0, 200.0) or eq_ulp(t8, o, 2.0):
            out_hit += 1
    print("%-8s %10s %10s %10s %10s %10s %10s" % (
        c,
        "%.0f" % t7 if t7 is not None else "-",
        "%.0f" % i if i is not None else "-",
        "%.0f" % (i * 100) if i is not None else "-",
        "%.0f" % t8 if t8 is not None else "-",
        "%.0f" % o if o is not None else "-",
        "%.0f" % (o * 100) if o is not None else "-"))
print("\ntx[7] 对齐 TDX 内盘: %d/%d    tx[8] 对齐 TDX 外盘: %d/%d" % (
    in_hit, in_tot, out_hit, out_tot))
# 内外盘和 = 成交量 自洽
print("\n>>> 自洽：TDX Inside+Outside 是否 = Volume ?")
ok = tot = 0
for c in CODES:
    i, o, v = IN(c), OUT(c), VOL(c)
    if None in (i, o, v):
        continue
    tot += 1
    if abs(i + o - v) <= 2:
        ok += 1
    else:
        print("   偏差 %-8s In+Out=%d Vol=%d diff=%d" % (c, i + o, v, i + o - v))
print("   自洽 %d/%d" % (ok, tot))


# --------------------------------------------- 焦点四：tx[56] Beta 族复核
print("\n" + "=" * 78)
print("【焦点四】tx[56] 复核（TDX 锚点中是否存在等值物）")
print("=" * 78)
print("%-8s %10s %10s %10s %10s" % ("code", "tx[56]", "TDX均价/现价", "换手f168", "振幅f171"))
for c in CODES:
    v56 = tx_field(c, 56)
    a = A(c)
    cl = p2_field(c, "f43")
    print("%-8s %10s %10s %10s %10s" % (
        c,
        "%.4f" % v56 if v56 is not None else "-",
        "%.4f" % (a / cl) if (a and cl) else "-",
        "%.2f" % p2_field(c, "f168") if p2_field(c, "f168") is not None else "-",
        "%.2f" % p2_field(c, "f171") if p2_field(c, "f171") is not None else "-"))
scan_anchor("tx[56] 反向：用 tx[56] 当锚扫 push2", lambda c: tx_field(c, 56))


# ------------------------------------------------------ ZHB（T-1 对齐）
print("\n" + "=" * 78)
print("【焦点五】ZHB 对撞（zhb_date=%s，按 T-1 铁律与 %s 采集对齐）" % (
    zhb.get("zhb_date"), zhb.get("zhb_date")))
print("=" * 78)
zday = str(zhb.get("zhb_date"))
tx_prev = load("raw_tencent.json", zday)
p2_prev = load("raw_push2_full.json", zday)
zs = zhb.get("stocks") or {}
print("ZHB 股票数=%d  T-1 采集目录存在: tencent=%s push2=%s" % (
    len(zs), bool(tx_prev), bool(p2_prev)))
if zs:
    k0 = sorted(zs.keys())[0]
    sample = zs[k0]
    keys = sorted(sample.keys()) if isinstance(sample, dict) else []
    print("ZHB 字段(%d): %s" % (len(keys), ", ".join(keys[:40])))
    # 数值型 ZHB 字段 与 T-1 push2 全域对撞
    if p2_prev:
        P2P = p2_prev["stocks"]
        zcodes = sorted(set(zs) & set(P2P))
        print("ZHB ∩ T-1 push2 交集 %d 只" % len(zcodes))
        num_keys = []
        for k in keys:
            vals = [to_f(zs[c].get(k)) for c in zcodes if isinstance(zs.get(c), dict)]
            if sum(1 for v in vals if v is not None) >= max(3, len(zcodes) // 2):
                num_keys.append(k)
        print("数值型 ZHB 字段 %d 个: %s" % (len(num_keys), ", ".join(num_keys)))
        p2p_keys = sorted({kk for c in zcodes for kk in (P2P[c].get("data") or {}).keys()})
        found = []
        for zk in num_keys:
            best = None
            for pk in p2p_keys:
                hit = tot = 0
                for c in zcodes:
                    a = to_f(zs[c].get(zk))
                    b = to_f((P2P[c].get("data") or {}).get(pk))
                    if a is None or b is None:
                        continue
                    tot += 1
                    if eq_ulp(a, b, 2.0):
                        hit += 1
                if tot >= 3 and (best is None or hit > best[1]):
                    best = (pk, hit, tot)
            if best and best[1] > 0:
                found.append((zk, best))
        for zk, (pk, hit, tot) in sorted(found, key=lambda x: -x[1][1]):
            lvl = "强" if tot and hit / tot >= 0.9 else "弱"
            print("   ZHB.%-24s == push2(T-1).%-8s %2d/%-3d %s" % (zk, pk, hit, tot, lvl))
        if not found:
            print("   (无 ZHB 数值字段与 T-1 push2 等值命中 —— 符合 ZHB 为竞价独立口径的既有结论)")

print("\n" + "=" * 78)
print("对撞结束")
print("=" * 78)

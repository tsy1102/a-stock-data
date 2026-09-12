#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多日精确对撞破解引擎 v2 (2026-09-12, 精炼版)
=============================================
针对 ulist239 的 f1-f34 未知字段, 用「数值精确对撞(对撞四铁律)」破解。锚源 = push2_full + tencent。

v2 相对 v1 的精炼(修正同族巧合假阳性):
- 排除**近常量连续锚**(std < 1e-3*(|mean|+1)): 常量字段(如 push2 f123=0)不可能是某变动目标的真同字段。
- 命中判定仍用舍入感知容差 |a-b| ≤ max(ulp_a, ulp_b)(同 vendor 东财, 真同字段应末位一致)。
- 输出 tightness = 跨所有 stock×day 的 median|Δ| / max|Δ|, 用于区分"精确同字段"(max|Δ|≈0)
  与"同族巧合"(max|Δ| 偏大)。
- hub 检测: 某锚同时成为 ≥2 个目标的 ≥18/20 候选 → 标记为巧合枢纽, 该锚下所有匹配降级为"存疑"。

铁律: 不靠同序号同义(ulist 与 push2 共享 f 号但语义可能异); 排除同源对与标识符(market/code/name)。
输出: docs/field_verification/20260912_ulist_collision.md  (不改 field_dict.md)
"""
import json, os, glob, re, sys, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH_RE = re.compile(r"(\d{8})$")
EXCL_TARGET = {"f12", "f13", "f14"}
EXCL_ANCHOR_TX = {0, 1, 2}

def is_num(x):
    if x is None or isinstance(x, bool):
        return False
    if isinstance(x, (int, float)):
        return True
    if isinstance(x, str):
        s = x.strip()
        if s in ("-", "", "None", "null"):
            return False
        try:
            float(s); return True
        except ValueError:
            return False
    return False

def to_f(x):
    return float(x)

def decimals(x):
    fx = float(x)
    if fx == int(fx):
        return 0
    s = f"{fx:.12f}".rstrip("0").rstrip(".")
    return len(s.split(".")[1]) if "." in s else 0

def match(a, b, enum_mode):
    if not (is_num(a) and is_num(b)):
        return False
    fa, fb = float(a), float(b)
    if enum_mode:
        return abs(fa - fb) <= 1e-9
    ulp = max(10.0 ** (-decimals(fa)), 10.0 ** (-decimals(fb)))
    return abs(fa - fb) <= ulp

def batch_dirs():
    ds = []
    for d in glob.glob(os.path.join(ROOT, "docs", "field_verification", "2026*")):
        if not os.path.isdir(d):
            continue
        m = BATCH_RE.search(d)
        if not m:
            continue
        if all(os.path.exists(os.path.join(d, f)) for f in
               ("raw_ulist239.json", "raw_push2_full.json", "raw_tencent.json")):
            ds.append((m.group(1), d))
    ds.sort()
    return ds

def load_batch(d):
    u = json.load(open(os.path.join(d, "raw_ulist239.json"), encoding="utf-8"))
    p = json.load(open(os.path.join(d, "raw_push2_full.json"), encoding="utf-8"))
    t = json.load(open(os.path.join(d, "raw_tencent.json"), encoding="utf-8"))
    return ({"ulist": {c: (v.get("data") or {}) for c, v in u.get("stocks", {}).items()},
            "push2": {c: (v.get("data") or {}) for c, v in p.get("stocks", {}).items()},
            "tx": {c: (v.get("fields") or []) for c, v in t.get("stocks", {}).items()}})

def main():
    batches = batch_dirs()
    print(f"[load] {len(batches)} 批次三源齐全: {batches[0][0]}..{batches[-1][0]}", file=sys.stderr)
    data = {date: load_batch(d) for date, d in batches}

    targets = [f"f{i}" for i in range(1, 35) if f"f{i}" not in EXCL_TARGET]

    # 枚举模式判定
    enum_mode = {}
    for uf in targets:
        vals = [ud[uf] for date in data for ud in data[date]["ulist"].values()
                if uf in ud and is_num(ud[uf])]
        if not vals:
            enum_mode[uf] = False
        else:
            ints = sum(1 for v in vals if float(v) == int(float(v)))
            enum_mode[uf] = (ints / len(vals)) >= 0.9

    # 锚点池 + 预计算方差(排除近常量连续锚)
    push2_fields, tx_len = set(), 0
    for date in data:
        for pd in data[date]["push2"].values():
            push2_fields.update(pd.keys())
        for tx in data[date]["tx"].values():
            tx_len = max(tx_len, len(tx))

    # 收集每个锚的全部数值, 算 std
    anchor_vals = {}
    for date in data:
        for code, pd in data[date]["push2"].items():
            for k, v in pd.items():
                if is_num(v):
                    anchor_vals.setdefault(("push2", k), []).append(float(v))
        for code, tx in data[date]["tx"].items():
            for i, v in enumerate(tx):
                if i in EXCL_ANCHOR_TX:
                    continue
                if is_num(v):
                    anchor_vals.setdefault(("tx", i), []).append(float(v))

    def near_const(kind, ak):
        if kind == "tx":
            return False  # 枚举/字符串混合, 不在此过滤
        vals = anchor_vals.get(("push2", ak), [])
        if len(vals) < 20:
            return False
        m = statistics.mean(vals)
        sd = statistics.pstdev(vals)
        # 近常量: 绝对波动极小 且 相对波动极小
        return sd < 1e-3 * (abs(m) + 1) and sd < 1e-2

    # 对撞
    results = {}
    for uf in targets:
        em = enum_mode[uf]
        anchor_hits = {}
        anchor_diffs = {}
        for pf in push2_fields:
            if not em and near_const("push2", pf):
                continue
            anchor_hits[("push2", pf)] = {}
            anchor_diffs[("push2", pf)] = []
        for i in range(tx_len):
            if i in EXCL_ANCHOR_TX:
                continue
            anchor_hits[("tx", i)] = {}
            anchor_diffs[("tx", i)] = []

        for date in data:
            ul = data[date]["ulist"]; pu = data[date]["push2"]; tx = data[date]["tx"]
            codes = {c for c in (set(ul) & set(pu) & set(tx)) if uf in ul.get(c, {})}
            if not codes:
                continue
            for key in list(anchor_hits.keys()):
                kind, ak = key
                hits = 0
                for c in codes:
                    a = ul[c].get(uf)
                    b = pu[c].get(ak) if kind == "push2" else (tx[c][ak] if ak < len(tx[c]) else None)
                    if match(a, b, em):
                        hits += 1
                        if not em:
                            anchor_diffs[key].append(abs(float(a) - float(b)))
                if hits > 0:
                    anchor_hits[key][date] = hits

        cands = []
        for key, perday in anchor_hits.items():
            if not perday:
                continue
            n_days = sum(1 for h in perday.values() if h >= 8)
            max_hit = max(perday.values())
            if n_days >= 3:
                diffs = anchor_diffs[key]
                med = statistics.median(diffs) if diffs else 0.0
                mx = max(diffs) if diffs else 0.0
                cands.append((key, n_days, max_hit, perday, med, mx))
        cands.sort(key=lambda x: (x[1], -x[4], x[2]), reverse=True)
        results[uf] = cands

    # hub 检测: 锚同时成为 ≥2 目标的 ≥18/20 候选
    hub_anchors = {}
    for uf in targets:
        for key, n_days, max_hit, perday, med, mx in results[uf]:
            if max_hit >= 18 and n_days >= 3:
                hub_anchors.setdefault(key, []).append(uf)
    hub_anchors = {k: v for k, v in hub_anchors.items() if len(v) >= 2}

    # ---------- 输出 ----------
    L = []
    L.append("# ulist239 f1–f34 多日数值对撞破解报告 v2 (2026-09-12)\n")
    L.append(f"> 引擎 v2: `scripts/crack_ulist_residuals_20260912.py` | 批次 **{len(batches)}** "
             f"({batches[0][0]}→{batches[-1][0]}) | 20 股 | 锚: push2_full + tencent\n")
    L.append("> 精炼: 排除近常量连续锚(hub 巧合源); tightness=跨样本 median|Δ|/max|Δ|; hub 锚降级存疑。\n")
    L.append("> ⚠️ 仅给证据与候选, 不改 `field_dict.md`; 定案需用户按对撞四铁律确认。\n")

    L.append("\n## 一、L1 定案候选 (≥3日 且 max≥18/20, 非 hub, tightness 小)\n")
    L.append("| 目标 | 模式 | 最佳锚 | max命中 | ≥8日 | median|Δ| | max|Δ| | 判定 |")
    L.append("|---|---|---|---|---|---|---|---|")
    l1 = 0
    for uf in targets:
        cands = results[uf]
        if not cands:
            continue
        best = cands[0]
        key, n_days, max_hit, perday, med, mx = best
        if max_hit >= 18 and n_days >= 3 and key not in hub_anchors:
            l1 += 1
            verdict = "L1(精确同字段)" if mx < 0.05 else "L1(近精确,间隔精度差)"
            L.append(f"| **{uf}** | {'枚举' if enum_mode[uf] else '连续'} | {key[0]}[{key[1]}] | "
                     f"{max_hit}/20 | {n_days} | {med:.4g} | {mx:.4g} | {verdict} |")
    L.append(f"\n> L1 候选数: **{l1}**\n")

    L.append("\n## 二、存疑 / hub 巧合 (锚命中 ≥2 目标, 降级)\n")
    L.append("| hub锚 | 命中目标 | 说明 |")
    L.append("|---|---|---|")
    for key, targs in sorted(hub_anchors.items(), key=lambda x: -len(x[1])):
        L.append(f"| {key[0]}[{key[1]}] | {', '.join(targs)} | 单锚多目标→同族巧合, 非真同字段 |")

    L.append("\n## 三、各目标 Top 候选 (tightness 辅助判真)\n")
    for uf in targets:
        cands = results[uf]
        if not cands:
            L.append(f"### {uf}: 无候选\n")
            continue
        em = "枚举" if enum_mode[uf] else "连续"
        L.append(f"### {uf} (模式={em})\n")
        for key, n_days, max_hit, perday, med, mx in cands[:3]:
            flag = " ⚠hub" if key in hub_anchors else ""
            L.append(f"- {key[0]}[{key[1]}]{flag}: max={max_hit}/20, ≥8日={n_days}, "
                     f"median|Δ|={med:.4g}, max|Δ|={mx:.4g}")

    out = os.path.join(ROOT, "docs", "field_verification", "20260912_ulist_collision.md")
    open(out, "w", encoding="utf-8").write("\n".join(L))
    print(f"[done] {out}", file=sys.stderr)
    print(f"[summary] L1={l1}, hub锚={len(hub_anchors)}, 有候选字段={sum(1 for uf in targets if results[uf])}", file=sys.stderr)

if __name__ == "__main__":
    main()

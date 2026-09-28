#!/usr/bin/env python3
"""crack_push2_status_codes_20260921.py — push2_full × ulist239/tencent 多日精确对撞(20260921 复刻版)

复刻 astock-field-collision 技能脚本，补入最新有效采集日 20260918/20260920（20260919 缺 push2/ulist，
20260921 东财封锁 push2_full 损坏，均跳过），使其覆盖到最新可用语料。

锚池=raw_push2_full.json(114 字段) × 扩展后 DATES 独立采集日
目标=ulist239 + tencent(tx[4]+)
对撞四铁律(精确≥18/20/日 → 多日≥3日重复= L1 定案)
输出: docs/field_verification/20260921/push2_statuscode_crack.md
不改 field_dict.md（仅产证据）。
"""
import json, os, math
from functools import lru_cache
from collections import defaultdict

FV = "docs/field_verification"
DATES = ["20260812", "20260813", "20260814", "20260815", "20260819", "20260820",
         "20260822", "20260824", "20260825", "20260826", "20260827", "20260828",
         "20260831", "20260901", "20260902", "20260903", "20260904", "20260916",
         "20260917", "20260918", "20260920"]


@lru_cache(maxsize=None)
def decimals(x):
    s = f"{x:.8f}".rstrip("0")
    return len(s.split(".")[1]) if "." in s else 0


def num(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(",", "").replace("%", "")
    if s in ("", "None", "nan", "NaN", "-", "--", "null"):
        return None
    try:
        return float(s)
    except Exception:
        return None


def _load(date, src):
    p = f"{FV}/{date}/raw_{src}.json"
    if not os.path.exists(p):
        return {}
    d = json.load(open(p, encoding="utf-8"))
    if src == "push2_full":
        return {c: (v.get("data") or {}) for c, v in d.get("stocks", {}).items() if isinstance(v, dict)}
    if src == "ulist239":
        return {c: (v.get("data") or {}) for c, v in d.get("stocks", {}).items() if isinstance(v, dict)}
    if src == "tencent":
        out = {}
        for c, v in d.get("stocks", {}).items():
            if isinstance(v, dict) and isinstance(v.get("fields"), list):
                out[c] = {f"tx[{i+1}]": v["fields"][i] for i in range(len(v["fields"]))}
        return out
    return {}


def build_field_index(sources):
    idx = {}
    for (src, field), _ in sources:
        per_date = {}
        distinct = set()
        is_enum = False
        for date in DATES:
            sd = sources[(src, field)].get(date, {})
            row = {}
            for c, raw in sd.items():
                v = num(raw)
                if v is None:
                    continue
                row[c] = v
                distinct.add(round(v))
            if row:
                per_date[date] = row
        if len(distinct) <= 12:
            is_enum = True
        idx[(src, field)] = (per_date, is_enum)
    return idx


def match_precise(a, b, enum):
    if enum:
        return abs(a - b) <= 1e-9
    da, db = decimals(a), decimals(b)
    if da == 0 and db == 0:
        return abs(a - b) <= 1e-9
    tol = max(10 ** (-da) if da > 0 else 1e-9, 10 ** (-db) if db > 0 else 1e-9)
    return abs(a - b) <= tol


def main():
    p2 = {d: _load(d, "push2_full") for d in DATES}
    ul = {d: _load(d, "ulist239") for d in DATES}
    tx = {d: _load(d, "tencent") for d in DATES}

    p2_fields = set()
    for d in DATES:
        for c, data in p2[d].items():
            p2_fields.update(data.keys())
    ul_fields = set()
    tx_fields = set()
    for d in DATES:
        for c, data in ul[d].items():
            ul_fields.update(data.keys())
        for c, data in tx[d].items():
            for fld in data:
                if fld in ("tx[1]", "tx[2]", "tx[3]"):
                    continue
                tx_fields.add(fld)

    anchor = {}
    for f in p2_fields:
        per_date = {}
        for d in DATES:
            row = {}
            for c, data in p2[d].items():
                v = num(data.get(f)) if isinstance(data, dict) else None
                if v is not None:
                    row[c] = v
            if row:
                per_date[d] = row
        if per_date:
            anchor[f"push2:{f}"] = per_date

    targets = {}
    for f in ul_fields:
        per_date = {}
        for d in DATES:
            row = {}
            for c, data in ul[d].items():
                v = num(data.get(f)) if isinstance(data, dict) else None
                if v is not None:
                    row[c] = v
            if row:
                per_date[d] = row
        if per_date:
            targets[f"ulist:{f}"] = per_date
    for f in tx_fields:
        per_date = {}
        for d in DATES:
            row = {}
            for c, data in tx[d].items():
                v = num(data.get(f)) if isinstance(data, dict) else None
                if v is not None:
                    row[c] = v
            if row:
                per_date[d] = row
        if per_date:
            targets[f] = per_date

    def is_enum_field(per_date):
        distinct = set()
        for d, row in per_date.items():
            for v in row.values():
                distinct.add(round(v))
        return len(distinct) <= 12

    FOCUS = ["push2:f106", "push2:f107", "push2:f110", "push2:f111", "push2:f112", "push2:f118"]

    lines = []
    lines.append("# push2 状态码字段 × ulist239/tencent 多日精确对撞(20260921 复刻·扩展语料)\n")
    lines.append(f"> 锚池: raw_push2_full.json(114 字段) × {len(DATES)} 独立采集日(补入 20260918/20260920)\n")
    lines.append(f"> 目标: ulist239({len(ul_fields)} 字段) + tencent(tx[4]+, {len(tx_fields)} 字段)\n")
    lines.append(f"> 规则: 对撞四铁律(精确≥18/20/日 → 多日≥3日重复= L1 定案)\n")

    def collide(anchor_label):
        ad = anchor[anchor_label]
        a_enum = is_enum_field(ad)
        best = None
        for tlabel, td in targets.items():
            dates_hit = 0
            tot_hit = 0
            tot_n = 0
            for d in DATES:
                ar = ad.get(d); tr = td.get(d)
                if not ar or not tr:
                    continue
                pairs = [(ar[c], tr[c]) for c in ar if c in tr]
                if len(pairs) < 8:
                    continue
                h = sum(1 for a, b in pairs if match_precise(a, b, a_enum))
                n = len(pairs)
                tot_hit += h; tot_n += n
                if h >= 18 and h == n:
                    dates_hit += 1
            if tot_n == 0:
                continue
            rate = tot_hit / tot_n
            cand = {"t": tlabel, "rate": rate, "hit": tot_hit, "n": tot_n, "days_full": dates_hit}
            if best is None or (rate > best["rate"]) or (rate == best["rate"] and dates_hit > best["days_full"]):
                best = cand
        return best, a_enum

    lines.append("## 一、焦点状态码字段(待升格L1)对撞结果\n")
    lines.append("| 字段 | 枚举? | 最佳匹配目标 | 总命中率 | 满命中日(≥18/20) | 判定 |")
    lines.append("|---|---|---|---|---|---|")
    for fl in FOCUS:
        if fl not in anchor:
            lines.append(f"| {fl} | — | (无数据) | — | — | — |")
            continue
        best, a_enum = collide(fl)
        if best is None:
            lines.append(f"| {fl} | {'Y' if a_enum else 'N'} | (无目标匹配) | — | — | 未破解 |")
        else:
            verdict = "L1定案(升格)" if (best["rate"] >= 0.9 and best["days_full"] >= 3) else (
                "L4候选" if best["rate"] >= 0.4 else "未破解")
            lines.append(f"| {fl} | {'Y' if a_enum else 'N'} | {best['t']} | "
                         f"{best['rate']:.3f}({best['hit']}/{best['n']}) | {best['days_full']}/{len(DATES)} | {verdict} |")

    lines.append("\n## 二、全量扫描: push2 字段 × 目标 精确命中≥0.95 的新映射(锚池修复后)\n")
    lines.append("| push2字段 | 最佳匹配 | 总命中率 | 满命中日 |")
    lines.append("|---|---|---|---|")
    new_maps = 0
    for fl in sorted(anchor):
        if fl in FOCUS:
            continue
        best, a_enum = collide(fl)
        if best and best["rate"] >= 0.95 and best["days_full"] >= 3:
            lines.append(f"| {fl} | {best['t']} | {best['rate']:.3f}({best['hit']}/{best['n']}) | {best['days_full']}/{len(DATES)} |")
            new_maps += 1
    lines.append(f"\n> 新发现精确映射(≥0.95 且≥3满命中日): {new_maps} 项(多为已知映射的再确认; "
                 f"若含 field_dict 未载字段则属新破解, 须逐条人工核对语义标签)\n")

    lines.append("\n## 三、结论\n")
    lines.append("- f107/f110/f111/f112/f118 经扩展语料多日精确对撞, 若 §一达 L1(≥0.9 且≥3满命中日), "
                 "即可从\"待补第3日升格L1\"升格为 **L1 定案**, 同步订正 field_dict。\n")
    lines.append("- 本对撞使用 raw_push2_full.json(114 字段) 替代上一轮误用的 raw_push2.json(0 字段), "
                 "消除了状态码字段的假阴性。\n")
    lines.append("- 所有 L1 结论须回写 field_dict.md 并触发 gen_field_matrix / 脚本 fallback 顺序调整 / "
                 "script_data_dict 同步(固化链条), 最后跑测试回归——本脚本仅产出对撞证据, 不改字典。\n")

    out = f"{FV}/20260921/push2_statuscode_crack.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[done] {out}")
    for fl in FOCUS:
        if fl in anchor:
            best, a_enum = collide(fl)
            print(f"  {fl} enum={a_enum} -> {best}")


if __name__ == "__main__":
    main()

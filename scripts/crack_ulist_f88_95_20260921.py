#!/usr/bin/env python3
"""crack_ulist_f88_95_20260921.py — ulist239 f88-f95(资金流细分小比率块) 定向对撞

背景: f88-f95 是 ulist239 中"资金流细分小比率块"(工作记忆定论), 值域多在 [-1,1],
      属真未知待破项。本脚本将其作为锚, 对撞:
        - push2_full 全部字段(同一采集日 D)
        - tencent tx[4+] 全部字段(同一采集日 D)
        - ZHB 全部数值字段(按 zhb_date==D 对齐)
      跨所有"push2_full+ulist239+tencent 三者俱全"的有效采集日, 套对撞四铁律。

对撞四铁律:
  ① 精度对齐(整数/枚举 1e-9; 连续值舍入感知)
  ② 命中率分层(≥18/20 且可解释 → L1; 8~17 → L4 候选)
  ③ 比值族(单位换算: CV<1e-4 且 比值∈{0.001..1e8 十幂} → L1-U)
  ④ 多日复核(≥3 独立日重复方可定案)
  ⑤ 相关性仅候选(不直接定案)

输出: docs/field_verification/20260921/ulist_f88_95_crack.md
不改 field_dict.md（仅产证据）。
"""
import json, os, math, statistics
from collections import defaultdict

FV = "docs/field_verification"
FOCUS_ULIST = [f"f{i}" for i in range(88, 96)]   # f88..f95


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


def decimals(x):
    s = f"{x:.8f}".rstrip("0")
    return len(s.split(".")[1]) if "." in s else 0


def match_precise(a, b):
    da, db = decimals(a), decimals(b)
    if da == 0 and db == 0:
        return abs(a - b) <= 1e-9
    ulpa = 10 ** (-da) if da > 0 else 1e-9
    ulpb = 10 ** (-db) if db > 0 else 1e-9
    return abs(a - b) <= max(ulpa, ulpb)


def load(date, src):
    p = f"{FV}/{date}/raw_{src}.json"
    if not os.path.exists(p):
        return None
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        return None
    if src == "push2_full":
        return {c: (v.get("data") or {}) for c, v in d.get("stocks", {}).items() if isinstance(v, dict)}
    if src == "ulist239":
        return {c: (v.get("data") or {}) for c, v in d.get("stocks", {}).items() if isinstance(v, dict)}
    if src == "tencent":
        out = {}
        for c, v in d.get("stocks", {}).items():
            if isinstance(v, dict) and isinstance(v.get("fields"), list):
                out[c] = v["fields"]
        return out
    return None


def load_zhb_by_tradingdate():
    """扫描所有 raw_zhb.json, 返回 {trading_date(str): {code: full_dict}}。"""
    out = {}
    for name in os.listdir(FV):
        d = os.path.join(FV, name)
        if not os.path.isdir(d):
            continue
        p = os.path.join(d, "raw_zhb.json")
        if not os.path.exists(p):
            continue
        try:
            j = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        zb = j.get("zhb_date")
        if not zb:
            continue
        stocks = {}
        for c, v in j.get("stocks", {}).items():
            full = v.get("full") or {}
            if full:
                stocks[c] = full
        if stocks:
            out[zb] = stocks
    return out


def main():
    # 选取 push2_full + ulist239 + tencent 三者俱全的日期
    cand = []
    for name in os.listdir(FV):
        d = os.path.join(FV, name)
        if not os.path.isdir(d):
            continue
        if not all(os.path.exists(os.path.join(d, f"raw_{s}.json"))
                   for s in ("push2_full", "ulist239", "tencent")):
            continue
        p2 = load(name, "push2_full"); ul = load(name, "ulist239"); tx = load(name, "tencent")
        if not (p2 and ul and tx):
            continue
        # 确认 ulist 含 f88-f95 数据
        has = False
        for c, data in ul.items():
            if any(f in data for f in FOCUS_ULIST):
                has = True; break
        if has:
            cand.append(name)
    cand.sort()
    print(f"[dates] valid multi-source dates ({len(cand)}): {cand}")

    zhb_by_td = load_zhb_by_tradingdate()
    print(f"[zhb] trading-date snapshots available: {sorted(zhb_by_td.keys())}")

    # 锚: ulist f88-f95 per date
    anchors = {}
    for f in FOCUS_ULIST:
        per_date = {}
        for D in cand:
            ul = load(D, "ulist239")
            row = {}
            for c, data in ul.items():
                v = num(data.get(f)) if isinstance(data, dict) else None
                if v is not None:
                    row[c] = v
            if row:
                per_date[D] = row
        if per_date:
            anchors[f] = per_date

    # 目标池: 每个目标 = {date(对齐后): {code: value}}
    # push2_full / tencent 直接用采集日 D; ZHB 用 zhb_date==D 的快照
    targets = defaultdict(dict)
    for D in cand:
        p2 = load(D, "push2_full"); tx = load(D, "tencent")
        zhb = zhb_by_td.get(D)   # 仅当某 ZHB 快照的 zhb_date==D 时才有
        # push2
        for c, data in p2.items():
            for k, v in data.items():
                nv = num(v)
                if nv is not None:
                    targets[f"push2:{k}"].setdefault(D, {})[c] = nv
        # tencent
        for c, flds in tx.items():
            if not isinstance(flds, list):
                continue
            for i, v in enumerate(flds):
                if (i + 1) in (1, 2, 3):
                    continue
                nv = num(v)
                if nv is not None:
                    targets[f"tx[{i+1}]"].setdefault(D, {})[c] = nv
        # zhb
        if zhb:
            for c, full in zhb.items():
                for k, v in full.items():
                    if k in ("market", "code", "date", "name"):
                        continue
                    nv = num(v)
                    if nv is not None:
                        targets[f"zhb:{k}"].setdefault(D, {})[c] = nv

    print(f"[targets] {len(targets)} target fields")

    # 对撞
    results = []
    for f, ad in anchors.items():
        best = None
        for tk, td in targets.items():
            dates_hit = 0
            tot_hit = 0
            tot_n = 0
            ratio_info = None
            for D in cand:
                ar = ad.get(D); tr = td.get(D)
                if not ar or not tr:
                    continue
                pairs = [(ar[c], tr[c]) for c in ar if c in tr]
                if len(pairs) < 8:
                    continue
                h = sum(1 for a, b in pairs if match_precise(a, b))
                n = len(pairs)
                tot_hit += h; tot_n += n
                if h >= 18 and h == n:
                    dates_hit += 1
                if h < n * 0.9:
                    ratios = [b / a for a, b in pairs if abs(a) > 1e-9]
                    if len(ratios) >= 8:
                        m = statistics.mean(ratios); sd = statistics.pstdev(ratios)
                        cv = sd / m if m else 9
                        if cv < 1e-4 and any(abs(m - k) < 0.005 * k for k in
                                            (1e8, 1e6, 1000, 100, 10, 1, 0.1, 0.01, 0.001)):
                            ratio_info = round(m, 6)
            if tot_n == 0:
                continue
            rate = tot_hit / tot_n
            cand_res = {"anchor": f"ulist:{f}", "target": tk, "n": tot_n, "hit": tot_hit,
                        "rate": round(rate, 3), "days_full": dates_hit, "ratio": ratio_info}
            if ratio_info is not None and tot_n >= 18:
                cand_res["verdict"] = "L1-U(比值族)"
            elif rate >= 0.9 and dates_hit >= 3:
                cand_res["verdict"] = "L1(精确)"
            elif rate >= 0.4:
                cand_res["verdict"] = "L4候选"
            else:
                cand_res["verdict"] = "无"
            if cand_res["verdict"] != "无":
                if best is None or _vrank(cand_res["verdict"]) > _vrank(best["verdict"]) or \
                   (cand_res["verdict"] == best["verdict"] and cand_res["rate"] > best["rate"]):
                    best = cand_res
        if best:
            results.append(best)

    results.sort(key=lambda c: (-_vrank(c["verdict"]), -c["rate"]))

    # 输出
    lines = []
    lines.append(f"# ulist239 f88-f95 定向对撞（资金流细分小比率块）· 20260921\n")
    lines.append(f"> 锚: ulist239 f88-f95 × {len(cand)} 个有效采集日({cand[0]}..{cand[-1]})\n")
    lines.append(f"> 目标: push2_full + tencent(tx[4+]) + ZHB(按 zhb_date 对齐) 共 {len(targets)} 字段\n")
    lines.append(f"> 规则: 对撞四铁律(精确≥18/20且≥3满命中日→L1 / 比值族 CV<1e-4→L1-U / 相关性仅候选)\n")
    lines.append("\n## 一、f88-f95 对撞最佳命中（按评级）\n")
    if not results:
        lines.append("（无 ≥8/20 命中 —— f88-f95 与已知字段无数值重合，倾向为 ulist 自含比率块，见 §二）\n")
    else:
        lines.append("| ulist锚 | 最佳目标 | n | 命中率 | 满命中日 | 比值族 | 评级 |")
        lines.append("|---|---|---|---|---|---|---|")
        for c in results:
            lines.append(f"| {c['anchor']} | {c['target']} | {c['n']} | "
                         f"{c['rate']:.3f}({c['hit']}/{c['n']}) | {c['days_full']}/{len(cand)} | "
                         f"{c['ratio'] if c['ratio'] else '—'} | {c['verdict']} |")

    # §二: 各 f 的描述性统计 + 可能的内部分层
    lines.append("\n## 二、f88-f95 描述性统计与内部分层\n")
    lines.append("| 字段 | 跨日均值 | 跨日std | 值域(min,max) | 疑似性质 |")
    lines.append("|---|---|---|---|---|")
    for f in FOCUS_ULIST:
        vals = []
        for D in cand:
            ul = load(D, "ulist239")
            for c, data in ul.items():
                v = num(data.get(f)) if isinstance(data, dict) else None
                if v is not None:
                    vals.append(v)
        if vals:
            mean = statistics.mean(vals); sd = statistics.pstdev(vals) if len(vals) > 1 else 0
            mn = min(vals); mx = max(vals)
            nature = "常量/近似常量" if sd < 1e-6 else ("比率[-1,1]" if mx <= 1.0001 and mn >= -1.0001 else "离群量值")
            lines.append(f"| ulist:{f} | {mean:.4f} | {sd:.4f} | ({mn:.4f},{mx:.4f}) | {nature} |")
        else:
            lines.append(f"| ulist:{f} | — | — | — | 无数据 |")

    lines.append("\n## 三、结论\n")
    n_l1 = sum(1 for c in results if c["verdict"].startswith("L1"))
    lines.append(f"- f88-f95 × 已知字段 对撞命中 L1/L1-U = {n_l1} 项（详见 §一）。\n")
    lines.append("- 若 §一为空或仅 L4候选: f88-f95 大概率为 ulist 自含的「资金流细分构成比率」"
                 "（如 主力买入占比/卖出占比/中单净额占比 等）, 无单一直达外部同名源, 属 ulist 内部语义, "
                 "须走东方财富 ulist.np 字段文档/网页锚定(黄金锚)而非跨源对撞破解。\n")
    lines.append("- 所有结论均待多日复核 + 黄金锚订正; 本脚本仅产出对撞证据, 不改 field_dict.md。\n")

    out = f"{FV}/20260921/ulist_f88_95_crack.md"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"[done] {out} | L1={n_l1} results={len(results)}")


def _vrank(v):
    return {"L1(精确)": 3, "L1-U(比值族)": 3, "L4候选": 1, "无": 0}.get(v, 0)


if __name__ == "__main__":
    main()

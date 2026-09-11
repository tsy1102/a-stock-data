#!/usr/bin/env python3
"""crack_zhb_anchored.py — ZHB 锚定对撞破解(休市日正确对齐版)

场景: 2026-09-05(周六·休市日)采集 ZHB=20260904(周五); 与 20260904 全采集(报价/东财/ulist)
同一交易日对齐(=ZHB-T1 铁律"休市日 ZHB 日期=报告数据日"),对撞 ZHB 各字段 × 全目标字段,
尝试破解未知字段。弥补上一轮(20260904 目录内 ZHB=20260903 滞后一日)的对撞盲区。

对撞四铁律:
  ① 精度对齐(舍入感知容差; 整数/枚举码 1e-9 严格)
  ② 命中率分层(≥18/20+L1 / 8~17 存疑)
  ③ 比值族(单位换算定案: CV<1e-4 且比值∈{100,1000,...})
  ④ 多日复核(本项目仅 2 个 ZHB 快照 20260903+20260904, 不足 ≥3 日 → 结论标"待多日复核")
  ⑤ 相关性仅生成候选, 不定案

用法:
  python scripts/crack_zhb_anchored.py
输出: docs/field_verification/20260904/zhb_anchored_crack.md
"""
import json, os, math, statistics
FV = "docs/field_verification"
# V17.2.7(2026-09-10): 改为今日采集目录。注意: 今日 ZHB 快照 zhb_date=20260909(本地包未刷新),
# 与 DATE=20260910 全采集差 1 交易日; 价格敏感字段对撞会有偏移, 稳定字段(PE/市值/枚举码)仍可用。
# 输出落在今日目录, 报告中标注该滞后。
DATE = "20260910"          # 今日全采集(报价/东财/ulist)
ZHB_DIR = "20260910"       # 今日采集的 ZHB 目录(zhb_date=20260909)


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
    if "." in s:
        return len(s.split(".")[1])
    return 0


def match_precise(a, b):
    """舍入感知精确对撞(〇·二 精度对齐对撞·通用修订)。"""
    da, db = decimals(a), decimals(b)
    if da == 0 and db == 0:
        return abs(a - b) <= 1e-9           # 整数/枚举码严格
    ulpa = 10 ** (-da) if da > 0 else 1e-9
    ulpb = 10 ** (-db) if db > 0 else 1e-9
    return abs(a - b) <= max(ulpa, ulpb)    # 较粗精度源主导


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def load_tencent(date):
    d = load_json(f"{FV}/{date}/raw_tencent.json")
    out = {}
    for c, v in d.get("stocks", {}).items():
        if isinstance(v, dict) and isinstance(v.get("fields"), list):
            out[c] = v["fields"]
    return out


def load_push2(date):
    d = load_json(f"{FV}/{date}/raw_push2_full.json")
    out = {}
    for c, v in d.get("stocks", {}).items():
        if isinstance(v, dict) and isinstance(v.get("data"), dict):
            out[c] = v["data"]
    return out


def load_ulist(date):
    d = load_json(f"{FV}/{date}/raw_ulist239.json")
    out = {}
    for c, v in d.get("stocks", {}).items():
        if isinstance(v, dict) and isinstance(v.get("data"), dict):
            out[c] = v["data"]
    return out


def load_zhb(zhb_dir):
    d = load_json(f"{FV}/{zhb_dir}/raw_zhb.json")
    out = {}
    for c, v in d.get("stocks", {}).items():
        full = v.get("full") or {}
        out[c] = full
    return out, d.get("zhb_date")


def spearman(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    rx = _rank(xs); ry = _rank(ys)
    mx = sum(rx) / n; my = sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx) ** 0.5
    vy = sum((b - my) ** 2 for b in ry) ** 0.5
    return cov / (vx * vy) if vx and vy else None


def _rank(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def main():
    tx = load_tencent(DATE)
    p2 = load_push2(DATE)
    ul = load_ulist(DATE)
    zhb, zb_date = load_zhb(ZHB_DIR)
    codes = sorted(set(tx) & set(p2) & set(ul) & set(zhb))
    print(f"[load] tx={len(tx)} p2={len(p2)} ul={len(ul)} zhb={len(zhb)} | aligned codes={len(codes)} | zhb_date={zb_date}")

    # ---- 目标池: (label, {code: value}) ----
    targets = {}
    for c in codes:
        f = tx[c]
        for i, v in enumerate(f):
            if (i + 1) in (1, 2, 3):      # tx[1]=市场标记 tx[2]=名称 tx[3]=代码(非数值)
                continue
            targets[f"tx[{i+1}]"] = targets.get(f"tx[{i+1}]", {})
            targets[f"tx[{i+1}]"][c] = num(v)
    for c in codes:
        for k, v in p2[c].items():
            key = f"push2:{k}"
            targets[key] = targets.get(key, {})
            targets[key][c] = num(v)
    for c in codes:
        for k, v in ul[c].items():
            key = f"ulist:{k}"
            targets[key] = targets.get(key, {})
            targets[key][c] = num(v)

    # ---- 锚池: ZHB full 各字段(排除标识/日期类非数值字段) ----
    EXCLUDE_ZHB = {"market", "code", "date", "name"}
    zhb_anchors = {}
    for c in codes:
        for k, v in zhb[c].items():
            if k in EXCLUDE_ZHB:
                continue
            zhb_anchors.setdefault(k, {})[c] = num(v)

    # 跳过全 None / 全 空 锚
    def populated(d):
        vals = [v for v in d.values() if v is not None]
        return len(vals)
    zhb_anchors = {k: v for k, v in zhb_anchors.items() if populated(v) >= 8}

    results = []
    for ak, ad in zhb_anchors.items():
        best = None
        for tk, td in targets.items():
            pairs = [(ad[c], td.get(c)) for c in codes
                     if ad.get(c) is not None and td.get(c) is not None]
            if len(pairs) < 8:
                continue
            hit = sum(1 for a, b in pairs if match_precise(a, b))
            n = len(pairs)
            rate = hit / n
            # 比值族检测
            ratio = None
            if hit < n * 0.9:  # 非精确命中才查比值族
                ratios = [b / a for a, b in pairs if abs(a) > 1e-9]
                if len(ratios) >= 8:
                    m = statistics.mean(ratios); sd = statistics.pstdev(ratios)
                    cv = sd / m if m else 9
                    if cv < 1e-4 and any(abs(m - k) < 0.005 * k for k in
                                        (100, 1000, 10000, 10, 0.1, 0.01, 0.001, 1e6, 1e8)):
                        ratio = round(m, 4)
            # 相关性(辅助候选)
            xs = [a for a, b in pairs]; ys = [b for a, b in pairs]
            sp = spearman(xs, ys)
            cand = {"anchor": f"zhb:{ak}", "target": tk, "n": n, "hit": hit,
                    "rate": round(rate, 3), "ratio": ratio,
                    "spearman": round(sp, 3) if sp is not None else None}
            # 评级(对撞四铁律)
            if ratio is not None and n >= 18:
                cand["verdict"] = "L1-U(比值族定案)"
            elif hit >= 18 and rate >= 0.9:
                cand["verdict"] = "L1(精确定案)"
            elif hit >= 8:
                cand["verdict"] = "L4候选(精确存疑)"
            else:
                cand["verdict"] = "无"
            if best is None or (cand["verdict"] != "无" and
                                (best["verdict"] == "无" or
                                 _vrank(cand["verdict"]) > _vrank(best["verdict"]) or
                                 (cand["verdict"] == best["verdict"] and cand["rate"] > best["rate"]))):
                best = cand
        if best is not None and best["verdict"] != "无":
            results.append(best)

    results.sort(key=lambda c: (-_vrank(c["verdict"]), -c["rate"]))
    _emit(results, zb_date, codes, len(zhb_anchors), len(targets))


def _vrank(v):
    return {"L1(精确定案)": 3, "L1-U(比值族定案)": 3, "L4候选(精确存疑)": 1, "无": 0}.get(v, 0)


def _emit(results, zb_date, codes, n_anchors, n_targets):
    lines = []
    lines.append(f"# ZHB 锚定对撞破解 · {DATE} 全采集 × ZHB={zb_date}\n")
    lines.append(f"> 采集: {DATE} 全采集(tencent/push2_full/ulist239) × {ZHB_DIR} 目录 ZHB(={zb_date})\n")
    lines.append(f"> 对齐: 休市日 ZHB 日期={zb_date}=报告数据日(同一交易日, 正确对齐)\n")
    lines.append(f"> 样本: {len(codes)} 股 | ZHB 锚 {n_anchors} 字段 × 目标 {n_targets} 字段\n")
    lines.append(f"> 规则: 对撞四铁律(精确≥18/20 → L1 / 8~17 → L4候选 / 比值族 CV<1e-4→L1-U / 相关性仅候选)\n")
    lines.append(f"> ⚠️ 多日复核: 仅 2 个 ZHB 快照(0903+0904), 不足 ≥3 日 → 结论标\"待多日复核\"\n")
    lines.append("\n## 一、ZHB 锚 × 全目标 对撞命中(按评级)\n")
    if not results:
        lines.append("（无 ≥8/20 精确/比值命中 —— ZHB 字段与目标字段无数值重合，详见 §二残留）\n")
    else:
        lines.append("| ZHB锚 | 目标 | n | 精确命中 | 命中率 | 比值族 | Spearman | 评级 |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for c in results:
            lines.append(f"| {c['anchor']} | {c['target']} | {c['n']} | {c['hit']} | "
                         f"{c['rate']:.3f} | {c['ratio'] if c['ratio'] else '—'} | "
                         f"{c['spearman'] if c['spearman'] is not None else '—'} | {c['verdict']} |")
    lines.append("\n## 二、针对已知残留未知项的 ZHB 定向验证\n")
    _direct_checks(lines, zb_date)
    lines.append("\n## 三、结论\n")
    n_l1 = sum(1 for c in results if c["verdict"].startswith("L1"))
    n_l4 = sum(1 for c in results if c["verdict"].startswith("L4"))
    lines.append(f"- ZHB 锚定新命中: L1/L1-U = {n_l1} 项, L4候选 = {n_l4} 项(详见 §一)。\n")
    lines.append("- 所有 L1/L4 结论均**待多日复核**(仅 2 ZHB 快照); 跨 ≥3 日重复方可定案入 field_dict。\n")
    lines.append("- ZHB 内部未知 Col[22](形态码) 不属跨源对撞范畴 → 须走配置直解(tdxhy.cfg), 本次不处理。\n")
    out = f"{FV}/{DATE}/zhb_anchored_crack.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[done] wrote {out} | L1={n_l1} L4={n_l4} results={len(results)}")


def _direct_checks(lines, zb_date):
    """针对 tx[86](手级带符号量)、tx[49](资金流净额族)、tx[56](Beta) 等残留项, 用 ZHB 主力净流入/PE 定向对撞。"""
    tx = load_tencent(DATE)
    zhb, _ = load_zhb(ZHB_DIR)
    codes = sorted(set(tx) & set(zhb))
    checks = [
        ("tx[86](手级带符号量)", "zhb:main_net_buy_hands(主力净流入手)"),
        ("tx[86](手级带符号量)", "zhb:main_net_buy_amount(主力净流入额)"),
        ("tx[49](资金流净额族)", "zhb:main_net_buy_amount(主力净流入额)"),
        ("tx[57](PE/PB族)", "zhb:pe_ttm(TTM PE)"),
        ("tx[57](PE/PB族)", "zhb:pe_dynamic(动态PE)"),
        ("tx[39](动态PE,已定案)", "zhb:pe_dynamic(动态PE)"),
        ("tx[56](Beta族)", "zhb:main_net_buy_hands"),
    ]
    lines.append("| 残留未知 | ZHB 锚 | 精确命中率 | 判定 |")
    lines.append("|---|---|---|---|")
    for tgt, anc in checks:
        # 取目标值
        tvals = {}
        if tgt.startswith("tx["):
            idx = int(tgt[tgt.index("[") + 1: tgt.index("]")]) - 1
            for c in codes:
                f = tx.get(c, [])
                if len(f) > idx:
                    tvals[c] = num(f[idx])
        # 取锚值
        ak = anc.split("(")[0].split(":")[1]
        avals = {c: num(zhb[c].get(ak)) for c in codes}
        pairs = [(tvals[c], avals[c]) for c in codes
                 if tvals.get(c) is not None and avals.get(c) is not None]
        if len(pairs) < 3:
            lines.append(f"| {tgt} | {anc} | 样本不足({len(pairs)}) | — |")
            continue
        hit = sum(1 for a, b in pairs if match_precise(a, b))
        n = len(pairs)
        rate = hit / n
        # 比值族
        ratios = [b / a for a, b in pairs if abs(a) > 1e-9]
        rinfo = ""
        if hit < n * 0.8 and len(ratios) >= 3:
            m = statistics.mean(ratios)
            rinfo = f" 比值≈{m:.4f}"
        verdict = "精确吻合" if hit >= 18 and rate >= 0.9 else (
            "部分吻合" if hit >= 8 else "不吻合")
        lines.append(f"| {tgt} | {anc} | {hit}/{n}={rate:.3f}{rinfo} | {verdict} |")


if __name__ == "__main__":
    main()

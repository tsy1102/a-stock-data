#!/usr/bin/env python3
"""verify_cross_source_crack.py — 78 个待核实 ulist239 字段的跨源数值对撞破解

目标: 对 docs/field_dict.md §12.3.2.3 中标记 `⚠️ 同号同义·未实证·待核实` 的 78 个
ulist239 字段(fN), 在全部采集日(19 个)逐一与多源锚( push2_full / em_fund_flow / zhb /
tencent / fuyao / sina / tdx )做 **精度对齐数值对撞**, 依据 CRACKING_METHODOLOGY.md
四铁律定案:

  ① 精度对齐(舍入感知容差; 整数/枚举码 1e-9 严格)
  ② 命中率分层(≥18/20+L1 / 8~17 → L4候选 / <8 → 无)
  ③ 比值族(单位换算定案: CV<1e-4 且比值∈{100,1000,...})
  ④ 多日复核(≥3 个独立采集日重复方定案 L1; 单日/双日一律 L4候选)
  ⑤ 相关性仅生成候选, 不定案(须 Spearman 同号 + 留一法不翻号, 但仅作辅助)

铁律适用:
  - 东财跨端点「同号异义」: ulist fN 与 em_fund_flow/push2 同号字段**不假设同义**,
    一切以数值对撞为准(同号命中才算, 同号不命中即证伪跨端点同义)。
  - ZHB main_net_buy_amount/1d = 竞价额(历史遗留键名, 非主力净)——作锚时按实测值对撞。
  - 对撞假阴性(目标在锚源全空)→ 转主动法(命名规律/相关性)给 L4 候选, 不收口为未知。

用法:
  python scripts/verify_cross_source_crack.py [--json OUT.json]
输出:
  docs/field_verification/20260907_round9_cross_source_crack.md
"""
import json
import os
import re
import statistics
import glob
from collections import defaultdict

FV = "docs/field_verification"
OUT_MD = os.path.join(FV, "20260907_round9_cross_source_crack.md")

# ── 数值工具 ──────────────────────────────────────────────────────────────
def num(x):
    if x is None:
        return None
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(",", "").replace("%", "")
    if s in ("", "None", "nan", "NaN", "-", "--", "null", "NoneType"):
        return None
    try:
        return float(s)
    except Exception:
        return None


def decimals(x):
    s = f"{x:.8f}".rstrip("0")
    return len(s.split(".")[1]) if "." in s else 0


def match_precise(a, b):
    """舍入感知精确对撞(〇·二 精度对齐对撞·通用修订)。"""
    if a is None or b is None:
        return False
    da, db = decimals(a), decimals(b)
    if da == 0 and db == 0:
        return abs(a - b) <= 1e-9            # 整数/枚举码严格
    ulpa = 10 ** (-da) if da > 0 else 1e-9
    ulpb = 10 ** (-db) if db > 0 else 1e-9
    return abs(a - b) <= max(ulpa, ulpb)     # 较粗精度源主导


def spearman(xs, ys):
    n = len(xs)
    if n < 3:
        return None

    def rank(vals):
        order = sorted(range(n), key=lambda i: vals[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx) ** 0.5
    vy = sum((b - my) ** 2 for b in ry) ** 0.5
    return cov / (vx * vy) if vx and vy else None


def _flatten(obj, prefix=""):
    """递归展开嵌套 dict/list 为 {flattened_key: numeric}。"""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            if isinstance(v, dict):
                out.update(_flatten(v, key))
            elif isinstance(v, list):
                # 仅展开"标量列表"(tencent/sina fields), 跳过对象列表
                nums = [num(x) for x in v]
                if any(n is not None for n in nums) and not any(
                    isinstance(x, (dict, list)) for x in v
                ):
                    for i, n in enumerate(nums, 1):
                        if n is not None:
                            out[f"{key}[{i}]"] = n
            else:
                n = num(v)
                if n is not None:
                    out[key] = n
    return out


def load_raw(date, fname):
    p = os.path.join(FV, date, fname)
    if not os.path.exists(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return None


def extract_source(date, name):
    """返回 {code: {field_key: numeric_value}}。"""
    if name == "ulist239":
        o = load_raw(date, "raw_ulist239.json")
        if not o:
            return {}
        return {c: {k: num(v) for k, v in rec.get("data", {}).items() if num(v) is not None}
                for c, rec in o.get("stocks", {}).items()}
    if name in ("push2_full", "axdata", "em_fund_flow"):
        o = load_raw(date, f"raw_{name}.json")
        if not o:
            return {}
        return {c: {k: num(v) for k, v in rec.get("data", {}).items() if num(v) is not None}
                for c, rec in o.get("stocks", {}).items()}
    if name == "zhb":
        o = load_raw(date, "raw_zhb.json")
        if not o:
            return {}
        return {c: {k: num(v) for k, v in rec.get("full", {}).items() if num(v) is not None}
                for c, rec in o.get("stocks", {}).items()}
    if name in ("tencent", "sina"):
        o = load_raw(date, f"raw_{name}.json")
        if not o:
            return {}
        out = {}
        for c, rec in o.get("stocks", {}).items():
            fld = rec.get("fields")
            if isinstance(fld, list):
                d = {}
                for i, v in enumerate(fld, 1):
                    n = num(v)
                    if n is not None:
                        d[f"{name}[{i}]"] = n
                out[c] = d
        return out
    if name == "fuyao":
        o = load_raw(date, "raw_fuyao.json")
        if not o:
            return {}
        return {c: _flatten(rec) for c, rec in o.get("stocks", {}).items() if isinstance(rec, dict)}
    if name == "tdx":
        o = load_raw(date, "raw_tdx.json")
        if not o:
            return {}
        out = {}
        for c, rec in o.get("stocks", {}).items():
            if isinstance(rec, dict):
                d = _flatten(rec)
                # tdx finance_info 等含大量非数值对象, 仅保留标量数值键
                out[c] = {k: v for k, v in d.items() if isinstance(v, (int, float))}
        return out
    return {}


ANCHOR_SOURCES = ["push2_full", "em_fund_flow", "zhb", "tencent", "fuyao", "sina", "tdx"]


def get_unverified_fields():
    lines = open("docs/field_dict.md", encoding="utf-8").read().splitlines()
    in_sec = False
    out = []
    for ln in lines:
        if re.match(r"#### .*12\.3\.2\.3", ln):
            in_sec = True
            continue
        if in_sec and re.match(r"#### ", ln):
            break
        m = re.match(r"\s*\|\s*f(\d{1,3})\s*\|", ln)
        if not m:
            continue
        if "未实证·待核实" in ln:
            out.append(int(m.group(1)))
    return sorted(out)


def is_constant(vals):
    vals = [v for v in vals if v is not None]
    if len(vals) < 8:
        return True
    return len(set(round(v, 6) for v in vals)) <= 1


def anchor_degenerate(vals):
    """锚源字段若由单一值(含 0/-)主导 → 易与稀疏目标产生'都空=都空'伪命中。

    例: tdx hgu(纯A样本 95% 为 0)、push2 f78(98.9% 为 0)、push2 f250(95% 为 '-')。
    这些字段与任何稀疏目标都能撞出高命中率, 必须剔除, 否则污染定案。
    守卫: ①众数占比 > 90% 视为退化; ②不同数值 ≤ 2 个(仅 {0, 单一非0})视为退化。
    """
    from collections import Counter
    vals = [v for v in vals if v is not None]
    if len(vals) < 8:
        return True
    cnt = Counter(round(v, 6) for v in vals)
    top_frac = cnt.most_common(1)[0][1] / len(vals)
    if top_frac > 0.90:
        return True
    if len(cnt) <= 2:
        return True
    return False


def collide(target_by_code, anchor_by_code):
    """对单日: 返回 (n, hit, ratio_or_None, spearman_or_None)。"""
    codes = sorted(set(target_by_code) & set(anchor_by_code))
    if not codes:
        return None
    tvals = [target_by_code[c] for c in codes]
    avals = [anchor_by_code[c] for c in codes]
    pairs = [(t, a) for t, a in zip(tvals, avals)
             if t is not None and a is not None]
    n = len(pairs)
    if n < 8:
        return None
    hit = sum(1 for a, b in pairs if match_precise(a, b))
    rate = hit / n
    # 比值族检测
    ratio = None
    if hit < n * 0.9:
        ratios = [b / a for a, b in pairs if abs(a) > 1e-9]
        if len(ratios) >= 8:
            m = statistics.mean(ratios)
            sd = statistics.pstdev(ratios)
            cv = sd / m if m else 9
            if cv < 1e-4 and any(abs(m - k) < 0.005 * k for k in
                                  (100, 1000, 10000, 10, 0.1, 0.01, 0.001, 1e6, 1e8, 1e5)):
                ratio = round(m, 4)
    sp = spearman(tvals, avals)
    return n, hit, rate, ratio, sp


def main():
    targets = get_unverified_fields()
    print(f"[targets] {len(targets)} 个待核实 ulist239 字段: {targets}")

    dates = sorted(glob.glob(os.path.join(FV, "[0-9]" * 8)))
    dates = [os.path.basename(d) for d in dates]
    print(f"[dates] {len(dates)} 个采集日")

    # 预载: 每 (date, source) 仅加载一次, 缓存避免 78×19×8 次重复读盘
    cache = {}
    def get(date, src):
        k = (date, src)
        if k not in cache:
            cache[k] = extract_source(date, src)
        return cache[k]

    # 结构: records[(fN, src, field)] = [per-date dict]
    records = defaultdict(list)

    for date in dates:
        ul = get(date, "ulist239")
        if not ul:
            continue
        # 预取各锚源(本日)
        anc_by_src = {src: get(date, src) for src in ANCHOR_SOURCES}
        for fN in targets:
            tgt = {c: (ul.get(c) or {}).get(f"f{fN}") for c in ul}
            tgt = {c: v for c, v in tgt.items() if v is not None}
            if len(tgt) < 8 or is_constant(list(tgt.values())):
                continue
            for src in ANCHOR_SOURCES:
                anc = anc_by_src[src]
                if not anc:
                    continue
                # 锚字段全集
                fields = set()
                for c in anc:
                    fields.update(anc[c].keys())
                for fk in fields:
                    av = {c: (anc.get(c) or {}).get(fk) for c in anc}
                    av = {c: v for c, v in av.items() if v is not None}
                    if len(av) < 8 or is_constant(list(av.values())):
                        continue
                    if anchor_degenerate(list(av.values())):
                        continue
                    res = collide(tgt, av)
                    if res is None:
                        continue
                    n, hit, rate, ratio, sp = res
                    if hit < 8:
                        continue
                    records[(fN, src, fk)].append({
                        "date": date, "n": n, "hit": hit, "rate": rate,
                        "ratio": ratio, "sp": sp,
                    })

    # ── 聚合 + 定案 ──
    result = {}  # fN -> list of candidate dicts
    for (fN, src, fk), perdates in records.items():
        if fN not in result:
            result[fN] = []
        n_days = len(perdates)
        l1_days = sum(1 for d in perdates if d["hit"] >= 18 and d["rate"] >= 0.9)
        hit8_days = sum(1 for d in perdates if d["hit"] >= 8)
        median_rate = statistics.median(d["rate"] for d in perdates)
        # 比值族(任意一日满足)
        ratio_vals = [d["ratio"] for d in perdates if d["ratio"] is not None]
        ratio_ok = bool(ratio_vals)
        best_sp = max((d["sp"] for d in perdates if d["sp"] is not None), default=None)
        # 定案判定
        if l1_days >= 3:
            verdict = "L1(精确定案)" if not ratio_ok else "L1-U(比值族定案)"
        elif l1_days >= 1 or hit8_days >= 1:
            verdict = "L4候选(存疑)"
        else:
            verdict = "无"
        if verdict == "无":
            continue
        result[fN].append({
            "src": src, "field": fk, "n_days": n_days,
            "l1_days": l1_days, "hit8_days": hit8_days,
            "median_rate": round(median_rate, 3),
            "ratio": (statistics.median(ratio_vals) if ratio_vals else None),
            "best_spearman": round(best_sp, 3) if best_sp is not None else None,
            "verdict": verdict,
        })
    # 排序: 每 fN 取最佳候选在前
    for fN in result:
        result[fN].sort(key=lambda c: (-_vrank(c["verdict"]), -c["l1_days"], -c["median_rate"]))

    # ── 统计 ──
    cracked_l1 = [fN for fN in targets if any(c["verdict"].startswith("L1") for c in result.get(fN, []))]
    cand_l4 = [fN for fN in targets if fN not in cracked_l1
               and any(c["verdict"] == "L4候选(存疑)" for c in result.get(fN, []))]
    unresolved = [fN for fN in targets if fN not in cracked_l1 and fN not in cand_l4]

    print(f"[done] L1定案={len(cracked_l1)} L4候选={len(cand_l4)} 未解={len(unresolved)}")

    # ── 写出 JSON ──
    dump = {"targets": targets, "cracked_l1": cracked_l1,
            "cand_l4": cand_l4, "unresolved": unresolved,
            "result": {str(fN): result.get(fN, []) for fN in targets}}
    if "--json" in __import__("sys").argv:
        jp = __import__("sys").argv[__import__("sys").argv.index("--json") + 1]
        json.dump(dump, open(jp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"[json] -> {jp}")

    _emit_md(dump)
    return dump


def _vrank(v):
    return {"L1(精确定案)": 3, "L1-U(比值族定案)": 3, "L4候选(存疑)": 1, "无": 0}.get(v, 0)


def _emit_md(dump):
    L = []
    L.append("# 第九轮 跨源数值对撞破解 · 78 待核实 ulist239 字段\n")
    L.append("> 方法论: CRACKING_METHODOLOGY.md 四铁律(精度对齐 / 命中率分层 / 比值族 / ≥3日复核)\n")
    L.append("> 目标: §12.3.2.3 标记 `⚠️ 同号同义·未实证·待核实` 的 78 个 ulist239 字段\n")
    L.append("> 锚源: push2_full / em_fund_flow / zhb / tencent / fuyao / sina / tdx (19 采集日 × 20 股)\n")
    L.append("> 铁律: 东财跨端点同号异义(ulist 与 em_fund_flow/push2 同号不假设同义, 以对撞为准); "
             "ZHB main_net_buy_* = 竞价额(键名历史遗留)\n")
    L.append(f"> 数据时间: 2026-08-12 ~ 2026-09-07 | 生成: 2026-09-07\n")
    L.append("")
    L.append(f"## 〇、定案总览\n")
    L.append(f"- **L1/L1-U 定案(≥3 独立日 ≥18/20)**: **{len(dump['cracked_l1'])}** 个")
    if dump["cracked_l1"]:
        L.append(f"  → {dump['cracked_l1']}")
    L.append(f"- **L4 候选(存疑, 单/双日命中或 8~17/20)**: **{len(dump['cand_l4'])}** 个")
    if dump["cand_l4"]:
        L.append(f"  → {dump['cand_l4']}")
    L.append(f"- **未解(全部锚源 0 命中, 转主动法)**: **{len(dump['unresolved'])}** 个")
    if dump["unresolved"]:
        L.append(f"  → {dump['unresolved']}")
    L.append("")

    L.append("## 一、跨源定案明细(按字段)\n")
    L.append("| ulist fN | 最佳跨源映射 | 锚源 | 命中日(≥18) | 命中日(≥8) | 中位命中率 | 比值族 | Spearman | 定案 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for fN in dump["targets"]:
        cands = dump["result"].get(str(fN), [])
        if not cands:
            L.append(f"| f{fN} | — | — | — | — | — | — | — | 未解 |")
            continue
        c = cands[0]
        ratio_s = f"{c['ratio']}" if c["ratio"] is not None else "—"
        sp_s = f"{c['best_spearman']}" if c["best_spearman"] is not None else "—"
        L.append(f"| f{fN} | {c['field']} | {c['src']} | {c['l1_days']} | {c['hit8_days']} | "
                 f"{c['median_rate']:.3f} | {ratio_s} | {sp_s} | {c['verdict']} |")

    # 附录: 全部候选(含次选)
    L.append("\n## 二、全部候选(含次选映射)\n")
    for fN in dump["targets"]:
        cands = dump["result"].get(str(fN), [])
        if not cands:
            continue
        L.append(f"\n### f{fN}")
        for c in cands:
            ratio_s = f" 比值={c['ratio']}" if c["ratio"] is not None else ""
            sp_s = f" sp={c['best_spearman']}" if c["best_spearman"] is not None else ""
            L.append(f"- `{c['src']}:{c['field']}` → {c['verdict']} "
                     f"(n日={c['n_days']}, L1日={c['l1_days']}, 命中8日={c['hit8_days']}, "
                     f"中位率={c['median_rate']:.3f}{ratio_s}{sp_s})")

    L.append("\n## 三、铁律合规与说明\n")
    L.append("- 东财跨端点同号异义: 本轮 ulist fN 与 em_fund_flow/push2_full 同号字段均经数值对撞, "
             "同号不命中者不视为同义(见 §一 未解项与次选中无对撞证据者)。")
    L.append("- ZHB 锚: `main_net_buy_amount`/`main_net_buy_hands` 按实测值对撞(=竞价额/竞价量, "
             "键名历史遗留, 非主力净), 不以键名定语义。")
    L.append("- 对撞假阴性(目标在锚源全空→0 命中)一律转 L4 候选或主动法, 不收口为未知。")
    L.append("- 整数/枚举码(状态/板级/计数)用 1e-9 严格相等; 连续值用舍入感知容差(较粗精度源主导)。")
    L.append("\n## 四、后续(主动法 / 待补)\n")
    L.append("- 未解字段建议转向: ①配置直解(tdxhy.cfg/hy_tree 行业板块) ②时间序列(连续 ZHB 包) "
             "③本机二进制矿(东财 fullfinnew/datacenter 财务顺序) ④扩大个股采样。")
    L.append("- 本轮未接入 datacenter/cninfo/cls/ftshare 等嵌套源(结构异质), 后续可补为锚扩展覆盖率。")

    open(OUT_MD, "w", encoding="utf-8").write("\n".join(L))
    print(f"[md] -> {OUT_MD}")


if __name__ == "__main__":
    main()

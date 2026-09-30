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

import statistics
from collections import defaultdict
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from scripts.collision_dates import discover_capture_folders, select_snapshots
    from scripts.collide import EXCLUDE_DIRS, collide_pair
else:
    try:
        from collision_dates import discover_capture_folders, select_snapshots
    except ImportError:
        from scripts.collision_dates import discover_capture_folders, select_snapshots

    try:
        from collide import EXCLUDE_DIRS, collide_pair
    except ImportError:
        from scripts.collide import EXCLUDE_DIRS, collide_pair

FV = "docs/field_verification"
SNAPSHOT_DOCS: dict[tuple[str, str], dict[str, Any]] = {}
SNAPSHOT_PHASES: dict[tuple[str, str], str] = {}
FOCUS_ULIST = [f"f{i}" for i in range(88, 96)]  # f88..f95


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


def load(date, src):
    d = SNAPSHOT_DOCS.get((src, date))
    if not isinstance(d, dict):
        return None
    if src == "push2_full":
        return {
            c: (v.get("data") or {}) for c, v in d.get("stocks", {}).items() if isinstance(v, dict)
        }
    if src == "ulist239":
        return {
            c: (v.get("data") or {}) for c, v in d.get("stocks", {}).items() if isinstance(v, dict)
        }
    if src == "tencent":
        out = {}
        for c, v in d.get("stocks", {}).items():
            if isinstance(v, dict) and isinstance(v.get("fields"), list):
                out[c] = v["fields"]
        return out
    return None


def load_zhb_by_tradingdate():
    """返回按 ZHB 有效 as-of 交易日归一后的股票快照。"""
    out = {}
    for (source, day), j in SNAPSHOT_DOCS.items():
        if source != "zhb":
            continue
        stocks = {}
        for c, v in j.get("stocks", {}).items():
            full = v.get("full") or {}
            if full:
                stocks[c] = full
        if stocks:
            out[day] = stocks
    return out


def _collision_field(per_date, source):
    values = {}
    sample_meta = {}
    for day, row in per_date.items():
        for code, value in row.items():
            sample_key = (str(code), f"T:{day}")
            values[sample_key] = value
            sample_meta[sample_key] = {
                "phase": SNAPSHOT_PHASES.get((source, day), "unknown"),
                "source": source,
            }
    distinct = set(values.values())
    return {
        "vals": values,
        "src": source,
        "is_constant": bool(values) and len(distinct) <= 1,
        "sample_meta": sample_meta,
    }


def main():
    global SNAPSHOT_DOCS, SNAPSHOT_PHASES
    sources = {"push2_full", "ulist239", "tencent", "zhb"}
    folders, folder_warnings = discover_capture_folders(FV)
    snapshots, snapshot_warnings = select_snapshots(folders, sources=sources)
    SNAPSHOT_DOCS = {}
    SNAPSHOT_PHASES = {}
    dates_by_source = defaultdict(set)
    for snapshot in snapshots:
        if snapshot.phase == "intraday":
            snapshot_warnings.append(
                f"{snapshot.folder}/{snapshot.source}: 盤中快照不納入專題多日定案"
            )
            continue
        day = snapshot.sample_date.strftime("%Y%m%d")
        if day in EXCLUDE_DIRS:
            snapshot_warnings.append(
                f"{snapshot.folder}/{snapshot.source}: 异常交易日 {day} 已排除"
            )
            continue
        SNAPSHOT_DOCS[(snapshot.source, day)] = snapshot.document
        SNAPSHOT_PHASES[(snapshot.source, day)] = snapshot.phase
        dates_by_source[snapshot.source].add(day)
    required_sources = ("push2_full", "ulist239", "tencent")
    available_days = set().union(*(dates_by_source[source] for source in required_sources))
    for day in sorted(available_days):
        missing = sorted(
            source for source in required_sources if day not in dates_by_source[source]
        )
        if missing:
            snapshot_warnings.append(f"{day}: 缺少有效来源快照 {', '.join(missing)}")
    cand = sorted(set.intersection(*(dates_by_source[source] for source in required_sources)))
    for day in cand:
        if day not in dates_by_source["zhb"]:
            snapshot_warnings.append(f"{day}: 没有 zhb_date 与行情日完全匹配的 ZHB 快照")
    folder_warnings = list(dict.fromkeys(folder_warnings))
    snapshot_warnings = list(dict.fromkeys(snapshot_warnings))
    for warning in (folder_warnings + snapshot_warnings)[:100]:
        print(f"[date-warning] {warning}")
    if not cand:
        print("[date-warning] 沒有同時具备 push2_full/ulist239/tencent 的有效交易日")
        return
    print(f"[dates] 去重后的有效交易日 ({len(cand)}): {cand}")

    valid_cand = []
    for D in cand:
        p2 = load(D, "push2_full")
        ul = load(D, "ulist239")
        tx = load(D, "tencent")
        if not (p2 and ul and tx):
            continue
        # 确认 ulist 含 f88-f95 数据
        has = False
        for c, data in ul.items():
            if any(f in data for f in FOCUS_ULIST):
                has = True
                break
        if has:
            valid_cand.append(D)
    cand = valid_cand
    if not cand:
        print("[date-warning] 有效交易日中没有包含 ulist239 f88-f95 的样本")
        return

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
        p2 = load(D, "push2_full")
        tx = load(D, "tencent")
        zhb = zhb_by_td.get(D)  # 仅当某 ZHB 快照的 zhb_date==D 时才有
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
        left_field = _collision_field(ad, "ulist239")
        for tk, td in targets.items():
            if tk.startswith("push2:"):
                target_source = "push2_full"
            elif tk.startswith("tx["):
                target_source = "tencent"
            else:
                target_source = "zhb"
            result = collide_pair(left_field, _collision_field(td, target_source))
            if result is None:
                continue
            level_to_verdict = {"L1": "L1(精确)", "L1-U": "L1-U(比值族)", "L4": "L4候选"}
            cand_res = {
                "anchor": f"ulist:{f}",
                "target": tk,
                "n": result["n_pairs"],
                "hit": round(result["overall_hit"] * result["n_pairs"]),
                "rate": result["overall_hit"],
                "days_full": result["days_ge_threshold"],
                "n_days": result["n_days"],
                "daily_sample_counts": result["daily_sample_counts"],
                "dates": result["distinct_days"],
                "ratio": result["ratio"],
                "evidence_sources": ["ulist239", target_source],
                "verdict": level_to_verdict[result["level"]],
            }
            if best is None or (
                _vrank(cand_res["verdict"]),
                cand_res["rate"],
                cand_res["n_days"],
            ) > (_vrank(best["verdict"]), best["rate"], best["n_days"]):
                best = cand_res
        if best:
            results.append(best)

    results.sort(key=lambda c: (-_vrank(c["verdict"]), -c["rate"]))

    # 输出
    lines = []
    lines.append(f"# ulist239 f88-f95 定向对撞（资金流细分小比率块）· 20260921\n")
    lines.append(f"> 锚: ulist239 f88-f95 × {len(cand)} 个有效采集日({cand[0]}..{cand[-1]})\n")
    lines.append(
        f"> 目标: push2_full + tencent(tx[4+]) + ZHB(按 zhb_date 对齐) 共 {len(targets)} 字段\n"
    )
    lines.append(
        "> 规则: 每个独立交易日有效配对样本≥18、命中率≥90%、至少3日；"
        "仅已确认收盘样本计入L1，盘中/时段未知仅作候选；同源镜像不作独立证据。\n"
    )
    all_warnings = folder_warnings + snapshot_warnings
    if all_warnings:
        lines.append(f"\n## 日期与采集质量告警（{len(all_warnings)}）\n")
        lines.extend(f"- {warning}\n" for warning in all_warnings[:100])
        if len(all_warnings) > 100:
            lines.append(f"\n_另有 {len(all_warnings) - 100} 条告警仅在控制台列示。_\n")
    lines.append("\n## 一、f88-f95 对撞最佳命中（按评级）\n")
    if not results:
        lines.append(
            "（无 ≥8/20 命中 —— f88-f95 与已知字段无数值重合，倾向为 ulist 自含比率块，见 §二）\n"
        )
    else:
        lines.append("| ulist锚 | 最佳目标 | n | 命中率 | 满命中日 | 日期 | 来源 | 比值族 | 评级 |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for c in results:
            dates = ", ".join(c["dates"])
            sources = ", ".join(c["evidence_sources"])
            lines.append(
                f"| {c['anchor']} | {c['target']} | {c['n']} | "
                f"{c['rate']:.3f}({c['hit']}/{c['n']}) | {c['days_full']}/{len(cand)} | "
                f"{dates} | {sources} | "
                f"{c['ratio'] if c['ratio'] else '—'} | {c['verdict']} |"
            )

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
            mean = statistics.mean(vals)
            sd = statistics.pstdev(vals) if len(vals) > 1 else 0
            mn = min(vals)
            mx = max(vals)
            nature = (
                "常量/近似常量"
                if sd < 1e-6
                else ("比率[-1,1]" if mx <= 1.0001 and mn >= -1.0001 else "离群量值")
            )
            lines.append(f"| ulist:{f} | {mean:.4f} | {sd:.4f} | ({mn:.4f},{mx:.4f}) | {nature} |")
        else:
            lines.append(f"| ulist:{f} | — | — | — | 无数据 |")

    lines.append("\n## 三、结论\n")
    n_l1 = sum(1 for c in results if c["verdict"].startswith("L1"))
    lines.append(f"- f88-f95 × 已知字段 对撞命中 L1/L1-U = {n_l1} 项（详见 §一）。\n")
    lines.append(
        "- 若 §一为空或仅 L4候选: f88-f95 大概率为 ulist 自含的「资金流细分构成比率」"
        "（如 主力买入占比/卖出占比/中单净额占比 等）, 无单一直达外部同名源, 属 ulist 内部语义, "
        "须走东方财富 ulist.np 字段文档/网页锚定(黄金锚)而非跨源对撞破解。\n"
    )
    lines.append(
        "- 所有结论均待多日复核 + 黄金锚订正; 本脚本仅产出对撞证据, 不改 field_dict.md。\n"
    )

    out = f"{FV}/20260921/ulist_f88_95_crack.md"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"[done] {out} | L1={n_l1} results={len(results)}")


def _vrank(v):
    return {"L1(精确)": 3, "L1-U(比值族)": 3, "L4候选": 1, "无": 0}.get(v, 0)


if __name__ == "__main__":
    main()

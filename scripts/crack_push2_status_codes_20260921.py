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
DATES = [
    "20260812",
    "20260813",
    "20260814",
    "20260815",
    "20260819",
    "20260820",
    "20260822",
    "20260824",
    "20260825",
    "20260826",
    "20260827",
    "20260828",
    "20260831",
    "20260901",
    "20260902",
    "20260903",
    "20260904",
    "20260916",
    "20260917",
    "20260918",
    "20260920",
]


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
    d = SNAPSHOT_DOCS.get((src, date))
    if not isinstance(d, dict):
        return {}
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
                out[c] = {f"tx[{i+1}]": v["fields"][i] for i in range(len(v["fields"]))}
        return out
    return {}


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
    global DATES, SNAPSHOT_DOCS, SNAPSHOT_PHASES
    requested_folders = set(DATES)
    sources = {"push2_full", "ulist239", "tencent"}
    folders, folder_warnings = discover_capture_folders(FV)
    found_folders = {folder.name for folder in folders}
    folder_warnings.extend(
        f"{folder}: 专题指定采集目录不存在" for folder in sorted(requested_folders - found_folders)
    )
    folders = [folder for folder in folders if folder.name in requested_folders]
    snapshots, snapshot_warnings = select_snapshots(
        folders,
        sources=sources,
        allowed_trading_folders=requested_folders,
    )
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
    available_days = set().union(*(dates_by_source[source] for source in sources))
    for day in sorted(available_days):
        missing = sorted(source for source in sources if day not in dates_by_source[source])
        if missing:
            snapshot_warnings.append(f"{day}: 缺少有效来源快照 {', '.join(missing)}")
    DATES = sorted(set.intersection(*(dates_by_source[source] for source in sources)))
    folder_warnings = list(dict.fromkeys(folder_warnings))
    snapshot_warnings = list(dict.fromkeys(snapshot_warnings))
    for warning in (folder_warnings + snapshot_warnings)[:80]:
        print(f"[date-warning] {warning}")
    if not DATES:
        print("[date-warning] 沒有同時具備 push2_full/ulist239/tencent 的有效交易日")
        return

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
    lines.append(f"> 锚池: raw_push2_full.json(114 字段) × {len(DATES)} 个归一去重后的有效交易日\n")
    lines.append(
        f"> 目标: ulist239({len(ul_fields)} 字段) + tencent(tx[4]+, {len(tx_fields)} 字段)\n"
    )
    lines.append(
        "> 规则: 每个独立交易日有效配对样本≥18、命中率≥90%、至少3日；"
        "仅已确认收盘样本计入L1，盘中/时段未知仅作候选；同源镜像不作独立证据。\n"
    )
    all_warnings = folder_warnings + snapshot_warnings
    if all_warnings:
        lines.append(f"\n## 日期与采集质量告警（{len(all_warnings)}）\n")
        lines.extend(f"- {warning}\n" for warning in all_warnings[:80])
        if len(all_warnings) > 80:
            lines.append(f"\n_另有 {len(all_warnings) - 80} 条告警仅在控制台列示。_\n")

    def collide(anchor_label):
        ad = anchor[anchor_label]
        a_enum = is_enum_field(ad)
        left_field = _collision_field(ad, "push2_full")
        best = None
        for tlabel, td in targets.items():
            target_source = "ulist239" if tlabel.startswith("ulist:") else "tencent"
            result = collide_pair(left_field, _collision_field(td, target_source))
            if result is None:
                continue
            level_to_verdict = {"L1": "L1定案(升格)", "L1-U": "L1-U(比值族)", "L4": "L4候选"}
            cand = {
                "t": tlabel,
                "rate": result["overall_hit"],
                "hit": round(result["overall_hit"] * result["n_pairs"]),
                "n": result["n_pairs"],
                "days_full": result["days_ge_threshold"],
                "n_days": result["n_days"],
                "daily_sample_counts": result["daily_sample_counts"],
                "dates": result["distinct_days"],
                "ratio": result["ratio"],
                "evidence_sources": ["push2", target_source],
                "verdict": level_to_verdict[result["level"]],
            }
            rank = {"L1定案(升格)": 3, "L1-U(比值族)": 3, "L4候选": 1}
            if best is None or (rank[cand["verdict"]], cand["rate"], cand["n_days"]) > (
                rank[best["verdict"]],
                best["rate"],
                best["n_days"],
            ):
                best = cand
        return best, a_enum

    lines.append("## 一、焦点状态码字段(待升格L1)对撞结果\n")
    lines.append(
        "| 字段 | 枚举? | 最佳匹配目标 | 总命中率 | 满命中日(≥18/20) | 有效日期 | 来源 | 判定 |"
    )
    lines.append("|---|---|---|---|---|---|---|---|")
    for fl in FOCUS:
        if fl not in anchor:
            lines.append(f"| {fl} | — | (无数据) | — | — | — | — | — |")
            continue
        best, a_enum = collide(fl)
        if best is None:
            lines.append(
                f"| {fl} | {'Y' if a_enum else 'N'} | (无目标匹配) | — | — | — | — | 未破解 |"
            )
        else:
            verdict = best["verdict"]
            dates = ", ".join(best["dates"])
            sources = ", ".join(best["evidence_sources"])
            lines.append(
                f"| {fl} | {'Y' if a_enum else 'N'} | {best['t']} | "
                f"{best['rate']:.3f}({best['hit']}/{best['n']}) | {best['days_full']}/{len(DATES)} | "
                f"{dates} | {sources} | {verdict} |"
            )

    lines.append("\n## 二、全量扫描: push2 字段 × 目标 精确命中≥0.95 的新映射(锚池修复后)\n")
    lines.append("| push2字段 | 最佳匹配 | 总命中率 | 满命中日 | 有效日期 | 来源 |")
    lines.append("|---|---|---|---|---|---|")
    new_maps = 0
    for fl in sorted(anchor):
        if fl in FOCUS:
            continue
        best, a_enum = collide(fl)
        if best and best["rate"] >= 0.95 and best["days_full"] >= 3:
            dates = ", ".join(best["dates"])
            sources = ", ".join(best["evidence_sources"])
            lines.append(
                f"| {fl} | {best['t']} | {best['rate']:.3f}({best['hit']}/{best['n']}) | "
                f"{best['days_full']}/{len(DATES)} | {dates} | {sources} |"
            )
            new_maps += 1
    lines.append(
        f"\n> 新发现精确映射(≥0.95 且≥3满命中日): {new_maps} 项(多为已知映射的再确认; "
        f"若含 field_dict 未载字段则属新破解, 须逐条人工核对语义标签)\n"
    )

    lines.append("\n## 三、结论\n")
    lines.append(
        "- f107/f110/f111/f112/f118 经扩展语料多日精确对撞, 若 §一达 L1(≥0.9 且≥3满命中日), "
        "即可从\"待补第3日升格L1\"升格为 **L1 定案**, 同步订正 field_dict。\n"
    )
    lines.append(
        "- 本对撞使用 raw_push2_full.json(114 字段) 替代上一轮误用的 raw_push2.json(0 字段), "
        "消除了状态码字段的假阴性。\n"
    )
    lines.append(
        "- 所有 L1 结论须回写 field_dict.md 并触发 gen_field_matrix / 脚本 fallback 顺序调整 / "
        "script_data_dict 同步(固化链条), 最后跑测试回归——本脚本仅产出对撞证据, 不改字典。\n"
    )

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

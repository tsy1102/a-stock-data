# -*- coding: utf-8 -*-
"""
ulist239 ↔ push2 跨源数值对撞工具（第七轮碰撞审计配套，2026-09-07）。

用途：给定一组 ulist 字段编号（默认 = 字典 §12.3.2.3 中「⚠️ 同号同义·未实证·待核实」的 78 条），
对每一只样本股做 ulist239 全字段 × push2_full 全字段的**精确数值相等**对撞，并辅以**秩/Pearson
相关**作为次级证据，判定该 ulist 字段的 push2 语义归属。结果交叉引用权威对齐表
`docs/verify/ulist_push2_align.md`（ulist fN → push2 fM），产出可机读的证据结论。

这是「同号即同义」lint 规则的**证据生成器**：新增字段登记声明 push2 映射前，必须用本工具
在现成语料（docs/field_verification/YYYYMMDD/raw_ulist239.json × raw_push2_full.json 配对目录）
产出实证，并将 (ulist fN, push2 fM) 写入对齐表，lint_field_same_number.py 才会放行。

判定（每字段）：
  SAME_NUMBER_TRUE : 最佳匹配 push2 fM == 自身 fN，且精确匹配率≥0.95（同号真同义）
  CONFIRMED_CROSS  : 最佳匹配 push2 fM ≠ fN，匹配率≥0.95，且对齐表已登记 ulist fN→fM（异号映射）
  WEAK_HINT        : 匹配率 0.5~0.95，给出候选 push2 fM，建议人工复核
  CONSTANT_DEGEN   : ulist 字段在各样本恒为同一值（恒空/恒0/恒常量）→ ulist 专属退化字段，无 push2 对应
  NO_MATCH         : 全样本无数值对应 → 大概率为 ulist 专属字段

防误判：ulist 侧或 push2 侧任一方为「常量」（跨样本不变化）时，精确匹配视为无证据力，
evidence_rate 计 0，避免「恒0↔恒0」式伪匹配。

用法：
  python scripts/verify_ulist_push2_collision.py                 # 默认对撞 78 条待核实
  python scripts/verify_ulist_push2_collision.py --all          # 对撞全部 239 个 ulist 字段
  python scripts/verify_ulist_push2_collision.py --fields f43,f50,f164
  python scripts/verify_ulist_push2_collision.py --json out.json
"""
import argparse
import io
import json
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FV = ROOT / "docs" / "field_verification"
ALIGN = ROOT / "docs" / "verify" / "ulist_push2_align.md"
DICT = ROOT / "docs" / "field_dict.md"


# 空标记：两侧任意一方为这些值时，视为「无数据」，不参与精确匹配（避免「都空↔都空」式伪匹配）。
SENTINELS = {None, "", "-", "—", "−", "null", "None", "NaN", "nan", "无", "空"}


def num_eq(a, b):
    # 空标记不计入匹配：ulist/push2 双方多为 '-'/空时，emptiness 不是字段同一性的证据。
    if a in SENTINELS or b in SENTINELS:
        return False
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= max(1e-9, 1e-6 * max(abs(a), abs(b)))
    return str(a).strip() == str(b).strip()


def _norm_keys(d):
    """把 {'f43': v, 43: v, 'f57': v} 归一为 {43: v}。"""
    out = {}
    if not isinstance(d, dict):
        return out
    for k, v in d.items():
        if isinstance(k, int):
            out[k] = v
        else:
            s = str(k).strip()
            m = re.match(r"f?(\d{1,4})$", s)
            if m:
                out[int(m.group(1))] = v
    return out


def load_align():
    align = {}
    if ALIGN.exists():
        for line in ALIGN.read_text(encoding="utf-8").splitlines():
            for mm in re.finditer(r"ulist\s*f(\d{1,3})\s*\|\s*f(\d{1,3})", line):
                align[int(mm.group(1))] = int(mm.group(2))
    return align


def load_corpus():
    """返回 [(date, {code: ulist_data_norm}, {code: push2_data_norm}), ...]。"""
    pairs = []
    if not FV.exists():
        return pairs
    for d in sorted(FV.iterdir()):
        if not d.is_dir():
            continue
        u = d / "raw_ulist239.json"
        p = d / "raw_push2_full.json"
        if not (u.exists() and p.exists()):
            continue
        try:
            ud = json.loads(u.read_text(encoding="utf-8")).get("stocks", {})
            pd = json.loads(p.read_text(encoding="utf-8")).get("stocks", {})
        except Exception:
            continue
        u_norm = {c: _norm_keys(rec.get("data", rec)) for c, rec in ud.items() if isinstance(rec, dict)}
        p_norm = {c: _norm_keys(rec.get("data", rec)) for c, rec in pd.items() if isinstance(rec, dict)}
        # 仅保留两侧都出现的 code
        common = sorted(set(u_norm) & set(p_norm))
        if not common:
            continue
        pairs.append((d.name, {c: u_norm[c] for c in common}, {c: p_norm[c] for c in common}))
    return pairs


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = sum((x - mx) ** 2 for x in xs) ** 0.5
    dy = sum((y - my) ** 2 for y in ys) ** 0.5
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def is_const(vals):
    nn = [v for v in vals if v is not None]
    return len(set(nn)) <= 1


def load_unverified_targets():
    """从字典 §12.3.2.3 解析「⚠️ 同号同义·未实证·待核实」的 fN 列表。"""
    txt = DICT.read_text(encoding="utf-8")
    targets = []
    in_sec = False
    for ln in txt.splitlines():
        if "12.3.2.3" in ln and "ulist239" in ln:
            in_sec = True
            continue
        if in_sec and ln.lstrip().startswith("#### "):
            break
        if in_sec:
            m = re.match(r"\s*\|\s*f(\d{1,3})\s*\|\s*[^|]*未实证[^|]*\|\s*(.*?)\s*\|", ln)
            if m:
                targets.append(int(m.group(1)))
    return targets


def collide(targets, corpus, align):
    results = {}
    # 预构建每只样本的 ulist/push2 归一数据
    samples = []  # (ulist_dict, push2_dict)
    for _, u_norm, p_norm in corpus:
        for c in u_norm:
            samples.append((u_norm[c], p_norm[c]))
    # push2 字段并集
    push2_keys = set()
    for _, pd in samples:
        push2_keys |= set(pd.keys())

    for X in targets:
        u_series = []  # 每只样本 ulist fX 值
        present = 0
        for ud, _ in samples:
            v = ud.get(X)
            if v is not None:
                u_series.append(v)
                present += 1
        if present == 0:
            results[X] = dict(verdict="NO_MATCH", reason="ulist f%d 在所有样本均缺失" % X,
                              n_samples=len(samples), best_Y=None, rate=0.0, corr=None,
                              align_backed=None)
            continue
        u_const = is_const(u_series)
        # 对每候选 push2 字段累计精确匹配
        match = {}      # Y -> matches
        raw_rate = {}   # Y -> (matches, n)
        corr_series = {}  # Y -> ([u_vals],[p_vals])
        for ud, pd in samples:
            uv = ud.get(X)
            if uv is None:
                continue
            for Y in push2_keys:
                pv = pd.get(Y)
                if pv is None:
                    continue
                raw_rate.setdefault(Y, [0, 0])
                raw_rate[Y][1] += 1
                if num_eq(uv, pv):
                    match[Y] = match.get(Y, 0) + 1
                    raw_rate[Y][0] += 1
                if isinstance(uv, (int, float)) and isinstance(pv, (int, float)) \
                        and not isinstance(uv, bool) and not isinstance(pv, bool):
                    corr_series.setdefault(Y, ([], []))
                    corr_series[Y][0].append(uv)
                    corr_series[Y][1].append(pv)
        # 计算 evidence_rate（剔除常量侧）
        ev = {}
        for Y in push2_keys:
            m, n = raw_rate.get(Y, (0, 0))
            if n == 0:
                continue
            p_vals = [pd.get(Y) for _, pd in samples if pd.get(Y) is not None]
            p_const = is_const(p_vals)
            if u_const or p_const:
                ev[Y] = 0.0  # 任一侧常量 → 无证据力
            else:
                ev[Y] = match.get(Y, 0) / n
        # 选最佳
        best_Y = max(ev, key=lambda y: ev[y]) if ev else None
        best_rate = ev.get(best_Y, 0.0) if best_Y is not None else 0.0
        # 次级 pearson（仅对最佳及对齐表候选）
        cand_corr = None
        for Y in (set([best_Y] if best_Y is not None else []) | (set([align[X]]) if X in align else set())):
            if Y is None:
                continue
            cs = corr_series.get(Y)
            if cs and len(cs[0]) >= 3:
                r = pearson(cs[0], cs[1])
                if r is not None and (cand_corr is None or abs(r) > abs(cand_corr)):
                    cand_corr = r
        # 判定
        aligned = align.get(X)
        if u_const:
            verdict = "CONSTANT_DEGEN"
            reason = "ulist f%d 跨样本恒为同一值（恒空/恒0/恒常量）→ ulist 专属退化字段" % X
        elif best_Y is not None and best_Y == X and best_rate >= 0.95:
            verdict = "SAME_NUMBER_TRUE"
            reason = "最佳匹配=自身 f%d，精确率 %.2f" % (X, best_rate)
        elif best_Y is not None and best_Y != X and best_rate >= 0.95 and aligned == best_Y:
            verdict = "CONFIRMED_CROSS"
            reason = "最佳匹配=push2 f%d，精确率 %.2f，对齐表已登记" % (best_Y, best_rate)
        elif best_Y is not None and best_rate >= 0.5:
            verdict = "WEAK_HINT"
            reason = "候选 push2 f%d，精确率 %.2f，建议人工复核" % (best_Y, best_rate)
        else:
            verdict = "NO_MATCH"
            reason = "全样本无数值对应（最佳 push2 f%s 率 %.2f）" % (best_Y, best_rate)
        results[X] = dict(verdict=verdict, reason=reason, n_samples=len(samples),
                          present=present, best_Y=best_Y, rate=round(best_rate, 3),
                          corr=(round(cand_corr, 3) if cand_corr is not None else None),
                          align_backed=(aligned == best_Y) if (aligned is not None and best_Y is not None) else None,
                          align_target=aligned)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="对撞全部 239 个 ulist 字段")
    ap.add_argument("--fields", default="", help="逗号分隔 f 编号，如 f43,f50,f164")
    ap.add_argument("--json", default="", help="结果写出 JSON 路径")
    args = ap.parse_args()

    align = load_align()
    corpus = load_corpus()
    if not corpus:
        print("❌ 未找到任何 raw_ulist239.json × raw_push2_full.json 配对目录（docs/field_verification/YYYYMMDD/）")
        sys.exit(2)
    print("语料：%d 个配对目录，共 %d 只样本股；对齐表条目 %d" % (
        len(corpus), sum(len(u) for _, u, _ in corpus), len(align)))
    dates = ", ".join(d for d, _, _ in corpus)
    print("  日期：%s" % dates)

    if args.all:
        targets = list(range(1, 240))
    elif args.fields:
        targets = [int(x.strip().lstrip("f")) for x in args.fields.split(",") if x.strip()]
    else:
        targets = load_unverified_targets()
        print("目标：字典 §12.3.2.3 中「未实证·待核实」字段 %d 条" % len(targets))

    results = collide(targets, corpus, align)

    # 汇总
    from collections import Counter
    cnt = Counter(r["verdict"] for r in results.values())
    print("\n对撞结论分布：")
    for k in ("SAME_NUMBER_TRUE", "CONFIRMED_CROSS", "WEAK_HINT", "CONSTANT_DEGEN", "NO_MATCH"):
        if cnt.get(k):
            print("  %-16s %d" % (k, cnt[k]))

    print("\n明细（按字段号）：")
    for X in sorted(results):
        r = results[X]
        extra = ""
        if r["best_Y"] is not None:
            extra = " → push2 f%d (rate=%.2f" % (r["best_Y"], r["rate"])
            if r["corr"] is not None:
                extra += ", corr=%.2f" % r["corr"]
            extra += ")"
        flag = ""
        if r["align_target"] is not None and r["best_Y"] != r["align_target"]:
            flag = "  ⚠️对齐表记 f%d 但与对撞最佳不符" % r["align_target"]
        print("  f%-4d %-15s %s%s%s" % (X, r["verdict"], r["reason"], extra, flag))

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"corpus_dates": dates, "align_count": len(align), "results": results},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print("\nJSON 已写出：%s" % args.json)


if __name__ == "__main__":
    main()

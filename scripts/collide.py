#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collide.py — 全源全字段通用对撞引擎（每日增量、按字典状态跟进）

设计目标
--------
取代原先"针对个别字段"的定向脚本（crack_zhb_col22 / crack_ulist_residuals）。
本引擎对 **全部采集数据** 做完整的跨源对撞：

  1. 加载 docs/field_verification/<date>/raw_*.json（默认近 N 天窗口，--all 全历史）
  2. 统一适配各源异构结构（fN 字典 / 位置列表 / 嵌套名典 / 标量），归一为
     ``(source, field_token) -> {(code, date): value}``
  3. 读取 field_registry.json 的状态（status==verified 即已定案）作为"跟进口碑"：
     - 已 verified 字段从「主攻目标」剔除，改作对齐锚 / 真值参考
     - 仅对 unverified（FOCUS）字段跑主攻对撞
  4. 对所有 (左=unverified, 右=任意源字段) 做两两对撞，严格套用 collision_rules 四铁律：
     - 类型感知（数值 / 枚举 / 字符串）
     - 精度对齐（舍入感知容差）
     - 比值族（单位换算 L1-U）：CV≤1e-4 且比值∈{10^k}
     - 多日复核（≥3 独立采集日，每日命中率≥0.9）
     - hub 巧合排除（单字段匹配过多判巧合）
  5. 增量状态追踪（collision_state.json）：跨日累积 findings，不重复刷屏
  6. 输出 <date>_collision_report.md / .json

治理约束（重要）
----------------
本引擎 **绝不手改** field_dict.md / field_registry.json（那是单一真相源，
手工 JSON 注入会被 G1 parity 闸门拦截）。它只负责"发现"，新定案经人工订正
field_dict.md 后由 sanctioned 管线（extract_registry → gen_field_dict → parity）
正式 ingest。引擎与治理闸门正交、互补。

用法
----
    python scripts/collide.py                 # 默认近 7 天窗口，全量对撞
    python scripts/collide.py --window 14     # 近 14 天
    python scripts/collide.py --all           # 全部历史日期
    python scripts/collide.py --date 20260913 # 指定报告日期戳
    python scripts/collide.py --limit 20      # 仅取前 20 个左字段（自测用）
    python scripts/collide.py --min-hit 0.95  # 自定义 L1 命中率阈值（默认 0.9）
"""
from __future__ import annotations

import os
import sys
import json
import math
import glob
import argparse
from collections import defaultdict
from datetime import date, datetime

try:
    import collision_rules as CR
    RULES_OK = True
except Exception:
    RULES_OK = False

# ───────────────────────────────────────────────────────────────────────
# 路径与常量
# ───────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "docs", "field_verification")
REG_PATH = os.path.join(DATA_DIR, "field_registry.json")
STATE_PATH = os.path.join(DATA_DIR, "collision_state.json")

# 样本为 12 股，故 18/20 绝对阈值改为比率（符合四铁律精神）
HIT_RATE_L1_RATIO = (CR.HIT_RATE_L1 / 20.0) if RULES_OK else 0.9   # 0.9
MULTI_DAY_MIN = CR.MULTI_DAY_MIN if RULES_OK else 3
RATIO_CV_MAX = CR.RATIO_CV_MAX if RULES_OK else 1e-4
RATIO_STEPS_SIGNED = set()
if RULES_OK:
    for k in range(0, 5):
        RATIO_STEPS_SIGNED.add(10 ** k)
        RATIO_STEPS_SIGNED.add(10 ** -k)
else:
    RATIO_STEPS_SIGNED = {1, 10, 100, 1000, 10000, 0.1, 0.01, 0.001, 0.0001}

MIN_PAIR = 8          # 一对字段最少需对齐的 (code,date) 样本数
HUB_MAX = 6           # 单字段匹配超过此数 → 巧合，降级
CONST_MAX_DISTINCT = 1  # 不同值 ≤1 → 常量，跳过
ID_SUFFIX_HINTS = ("market", "code", "date", "name", "thscode", "ticker", "url", "host", "secid")


# ───────────────────────────────────────────────────────────────────────
# 数值工具
# ───────────────────────────────────────────────────────────────────────
def to_num(v):
    """尽力把值转成 float；非数值返回 None。"""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip().replace(",", "")
        if s == "":
            return None
        try:
            return float(s)
        except ValueError:
            return None
    return None


def is_close(a: float, b: float) -> bool:
    """舍入感知容差：相对 1e-6，绝对值兜底 1e-9。"""
    if a == b:
        return True
    denom = max(1.0, abs(a), abs(b))
    return abs(a - b) <= 1e-6 * denom


def cv(xs):
    """变异系数 std/mean。"""
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    if m == 0:
        return 0.0
    var = sum((x - m) ** 2 for x in xs) / n
    return math.sqrt(var) / abs(m)


# ───────────────────────────────────────────────────────────────────────
# 原始数据加载与字段扁平化
# ───────────────────────────────────────────────────────────────────────
def _flatten(rec, source, scheme, code, date, out):
    """把单只股票的原始记录扁平化为 (fid, value) 列表，写入 out。"""
    if not isinstance(rec, dict):
        return
    if rec.get("__error__"):
        return

    # 形态 A：fN 字典（ulist239 / push2_full / push2）
    data = rec.get("data")
    if isinstance(data, dict) and any(
        (isinstance(k, str) and (k.startswith("f") and k[1:].isdigit())) for k in data
    ):
        for k, v in data.items():
            out.append((f"{source}.{k}", v))
        return

    # 形态 B：位置列表（tencent / sina）
    flds = rec.get("fields")
    if isinstance(flds, list):
        for i, v in enumerate(flds):
            out.append((f"{source}[{i}]", v))
        return

    # 形态 C：嵌套名典 / 标量（zhb full/stat/stat2/tipinfo、tdx quote_full/finance_info、fuyao *、…）
    for sub, subv in rec.items():
        if sub in ("scheme", "n_fields", "url", "host", "secid", "zhb_date"):
            continue
        if isinstance(subv, dict):
            for k, v in subv.items():
                if isinstance(v, (dict, list)):
                    continue
                out.append((f"{source}.{sub}.{k}", v))
        elif isinstance(subv, (int, float, str)) and not isinstance(subv, bool):
            out.append((f"{source}.{sub}", subv))
        # 列表 / None 跳过


def load_date(date_dir, store):
    """加载某个日期目录下的所有 raw_*.json，累加到 store。"""
    d = os.path.join(DATA_DIR, date_dir)
    if not os.path.isdir(d):
        return 0
    cnt = 0
    for fp in sorted(glob.glob(os.path.join(d, "raw_*.json"))):
        base = os.path.basename(fp)
        src = base[len("raw_"):-len(".json")]
        if src in ("meta", "completeness_audit"):
            continue
        try:
            doc = json.load(open(fp, encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(doc, dict):
            continue
        scheme = doc.get("scheme")
        stocks = doc.get("stocks")
        if not isinstance(stocks, dict):
            continue
        for code, rec in stocks.items():
            pairs = []
            _flatten(rec, src, scheme, code, date_dir, pairs)
            for fid, val in pairs:
                store[fid]["vals"][(code, date_dir)] = val
                store[fid]["scheme"] = scheme
                store[fid]["src"] = src
            cnt += len(pairs)
    return cnt


# ───────────────────────────────────────────────────────────────────────
# 字段分类（数值 / 枚举 / 字符串 / 常量 / 标识符）
# ───────────────────────────────────────────────────────────────────────
def classify(store):
    """为每个字段补充 type / n_distinct / is_constant / is_identifier。"""
    for fid, info in store.items():
        vals = [v for v in info["vals"].values()
                if v is not None and not isinstance(v, (dict, list))]
        nums = [to_num(v) for v in vals]
        nums = [n for n in nums if n is not None]
        n_total = len(vals)
        n_num = len(nums)
        distinct = len(set(vals))
        info["n"] = n_total
        info["n_num"] = n_num
        info["n_distinct"] = distinct
        info["is_constant"] = distinct <= CONST_MAX_DISTINCT and n_total > 0
        low = fid.lower()
        info["is_identifier"] = any(h in low for h in ID_SUFFIX_HINTS)
        if n_total > 0 and n_num >= 0.8 * n_total:
            info["type"] = "num"
        elif distinct <= 30 and n_total > 0:
            info["type"] = "enum"
        else:
            info["type"] = "str"
        # 值域（用于快速预筛）
        if nums:
            info["vmin"] = min(nums)
            info["vmax"] = max(nums)
        else:
            info["vmin"] = None
            info["vmax"] = None


# ───────────────────────────────────────────────────────────────────────
# 对撞核心
# ───────────────────────────────────────────────────────────────────────
def collide_pair(L, R):
    """对撞两个字段；返回结果 dict 或 None。"""
    lv, rv = L["vals"], R["vals"]
    common = set(lv) & set(rv)
    if len(common) < MIN_PAIR:
        return None

    day_stat = defaultdict(lambda: [0, 0])   # date -> [hits, total]
    ratios = []
    exact_enum = 0
    enum_total = 0
    for k in common:
        a, b = lv[k], rv[k]
        da, db = to_num(a), to_num(b)
        d = k[1]
        day_stat[d][1] += 1
        if da is not None and db is not None:
            if is_close(da, db):
                day_stat[d][0] += 1
            elif da != 0 and db != 0:
                ratios.append(db / da)
        else:
            enum_total += 1
            if str(a) == str(b):
                day_stat[d][0] += 1
                exact_enum += 1

    day_rates = [h / t for h, t in day_stat.values() if t > 0]
    n_days = len(day_rates)
    days_ge = sum(1 for r in day_rates if r >= HIT_RATE_L1_RATIO)
    total_h = sum(h for h, _ in day_stat.values())
    total_t = sum(t for _, t in day_stat.values())
    overall = (total_h / total_t) if total_t else 0.0

    # 比值族（单位换算）
    ratio_info = None
    if ratios:
        med = sorted(ratios)[len(ratios) // 2]
        if med in RATIO_STEPS_SIGNED and cv(ratios) <= RATIO_CV_MAX and med != 1:
            ratio_info = med

    # 判定
    l1_ok = (days_ge >= MULTI_DAY_MIN and n_days >= MULTI_DAY_MIN
             and overall >= HIT_RATE_L1_RATIO and not L["is_constant"] and not R["is_constant"])
    if l1_ok:
        level = "L1-U" if ratio_info else "L1"
    elif overall >= 0.4 and days_ge >= 1:
        level = "L4"
    else:
        level = None

    if level is None:
        return None

    return {
        "left": None, "right": None,           # 由调用方填
        "level": level,
        "ratio": ratio_info,
        "overall_hit": round(overall, 4),
        "days_ge_threshold": days_ge,
        "n_days": n_days,
        "n_pairs": total_t,
        "distinct_days": sorted(day_stat.keys()),
    }


def range_overlap(L, R):
    if L["vmin"] is None or R["vmin"] is None:
        return True
    return not (L["vmax"] < R["vmin"] or R["vmax"] < L["vmin"])


# ───────────────────────────────────────────────────────────────────────
# 状态读取（registry）+ 增量状态
# ───────────────────────────────────────────────────────────────────────
REG_ALIAS = {
    "TDX(双命名源)": "tdx", "TDX": "tdx",
    "东财-ulist239": "ulist239", "ulist": "ulist239", "ulist239": "ulist239",
    "东财-push2": "push2", "push2": "push2", "push2_full": "push2",
    "em_fund_flow": "push2", "push2ex": "push2", "push2delay": "push2",
    "腾讯": "tencent", "tencent": "tencent",
    "ZHB": "zhb", "ZHB-tdxstat": "zhb",
    "同花顺": "thsdk", "thsdk": "thsdk",
    "AxData": "axdata", "axdata": "axdata",
    "FTShare": "ftshare", "ftshare": "ftshare",
    "fuyao": "fuyao",
    "新浪": "sina", "sina": "sina",
}


def load_registry_state():
    """返回 (verified_set, known_mapping_pairs)。best-effort，匹配不上则放行。"""
    verified = set()
    mappings = set()
    if not os.path.exists(REG_PATH):
        return verified, mappings
    try:
        reg = json.load(open(REG_PATH, encoding="utf-8"))
    except Exception:
        return verified, mappings
    for f in reg.get("fields", []):
        if f.get("status") == "verified":
            src = REG_ALIAS.get(f.get("source", ""), f.get("source", ""))
            verified.add((src, str(f.get("code", ""))))
    for m in reg.get("mappings", []):
        a = m.get("from", {})
        b = m.get("to", {})
        sa = REG_ALIAS.get(a.get("source", ""), a.get("source", ""))
        sb = REG_ALIAS.get(b.get("source", ""), b.get("source", ""))
        mappings.add((sa, str(a.get("code", "")), sb, str(b.get("code", ""))))
        mappings.add((sb, str(b.get("code", "")), sa, str(a.get("code", ""))))
    return verified, mappings


def norm_src_of(fid):
    if "." in fid:
        return fid.split(".")[0]
    if "[" in fid:
        return fid.split("[")[0]
    return fid


def alias_src(fid):
    return REG_ALIAS.get(norm_src_of(fid), norm_src_of(fid))


def code_of(fid):
    if "[" in fid:
        return fid[fid.index("["):]
    if "." in fid:
        return fid.rsplit(".", 1)[-1]
    return fid


def is_verified(fid, verified):
    return (alias_src(fid), code_of(fid)) in verified


def load_state():
    if os.path.exists(STATE_PATH):
        try:
            return json.load(open(STATE_PATH, encoding="utf-8"))
        except Exception:
            pass
    return {"version": 1, "findings": {}}


def save_state(st):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


# ───────────────────────────────────────────────────────────────────────
# 主流程
# ───────────────────────────────────────────────────────────────────────
def run(args):
    # 1) 收集日期窗口
    all_dates = sorted(
        d for d in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, d)) and d[:2] == "20"
    )
    if args.all:
        window_dates = all_dates
    else:
        window_dates = all_dates[-max(1, args.window):]

    # 2) 加载数据
    store = defaultdict(lambda: {"vals": {}, "scheme": None, "src": None})
    total = 0
    for d in window_dates:
        total += load_date(d, store)
    classify(store)
    print(f"[collide] 加载 {len(window_dates)} 个日期、{len(store)} 个字段、{total} 条样本值",
          file=sys.stderr)

    # 3) registry 状态
    verified, known_maps = load_registry_state()

    # 4) 候选左字段 = unverified 且非标识符、非常量、有数值
    left_ids = [
        fid for fid, info in store.items()
        if not info["is_identifier"]
        and not info["is_constant"]
        and info["type"] in ("num", "enum")
        and not is_verified(fid, verified)
    ]
    # 右字段 = 全部（含 verified 作锚）
    right_ids = [fid for fid, info in store.items()
                 if not info["is_identifier"] and not info["is_constant"]
                 and info["type"] in ("num", "enum")]

    if args.limit:
        left_ids = left_ids[:args.limit]
    print(f"[collide] 主攻目标(left)={len(left_ids)}，锚+未知(right)={len(right_ids)}",
          file=sys.stderr)

    # 5) 两两对撞
    raw_pairs = []          # (left, right, result)
    for li in left_ids:
        L = store[li]
        for ri in right_ids:
            if li == ri:
                continue
            R = store[ri]
            if L["type"] != R["type"]:
                continue
            if L["type"] == "num" and not range_overlap(L, R):
                continue
            res = collide_pair(L, R)
            if res:
                res["left"] = li
                res["right"] = ri
                res["same_code"] = (code_of(li) == code_of(ri))
                raw_pairs.append(res)

    # 6) hub 巧合排除：单字段匹配过多 → 降级
    left_count = defaultdict(int)
    right_count = defaultdict(int)
    for p in raw_pairs:
        left_count[p["left"]] += 1
        right_count[p["right"]] += 1
    for p in raw_pairs:
        if left_count[p["left"]] > HUB_MAX or right_count[p["right"]] > HUB_MAX:
            if p["level"] in ("L1", "L1-U"):
                p["level"] = "L4"
                p["hub_flag"] = True

    # 7) 增量状态合并
    st = load_state()
    today = args.date or date.today().strftime("%Y%m%d")
    findings = st["findings"]
    new_count = 0
    for p in raw_pairs:
        if p["level"] not in ("L1", "L1-U"):
            continue
        key = "||".join(sorted([p["left"], p["right"]]))
        prev = findings.get(key)
        rec = {
            "left": p["left"], "right": p["right"],
            "level": p["level"], "ratio": p["ratio"],
            "overall_hit": p["overall_hit"],
            "n_days": p["n_days"], "n_pairs": p["n_pairs"],
            "hub_flag": p.get("hub_flag", False),
            "last_seen": today,
        }
        # 是否已在 registry 映射中（已定案）
        lv = (alias_src(p["left"]), code_of(p["left"]))
        rv = (alias_src(p["right"]), code_of(p["right"]))
        rec["in_registry"] = (lv + rv in known_maps) or (rv + lv in known_maps)
        if prev is None:
            rec["first_seen"] = today
            rec["status"] = "new"
            new_count += 1
        else:
            rec["first_seen"] = prev.get("first_seen", today)
            rec["status"] = "confirmed" if (prev.get("status") == "confirmed" or rec["in_registry"]) else "repeated"
        p["in_registry"] = rec["in_registry"]   # 回写供报告读取
        findings[key] = rec
    st["findings"] = findings
    st["updated"] = today
    save_state(st)

    # 8) 输出报告
    l1 = [p for p in raw_pairs if p["level"] in ("L1", "L1-U")]
    l4 = [p for p in raw_pairs if p["level"] == "L4"]
    l1.sort(key=lambda p: (-p["overall_hit"], -p["n_days"]))
    l4.sort(key=lambda p: -p["overall_hit"])

    report_md = build_report_md(today, window_dates, len(store), total,
                                left_ids, l1, l4, new_count, verified)
    out_dir = os.path.join(DATA_DIR, today)
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, f"{today}_collision_report.md")
    json_path = os.path.join(out_dir, f"{today}_collision_report.json")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"date": today, "window": window_dates, "L1": l1, "L4": l4,
                   "new_count": new_count}, f, ensure_ascii=False, indent=2)

    print(f"[collide] L1 候选={len(l1)}，L4 候选={len(l4)}，新增定案={new_count}",
          file=sys.stderr)
    print(f"[collide] 报告: {md_path}", file=sys.stderr)
    return md_path, json_path


def _l1_row(p):
    return (f"| `{p['left']}` | `{p['right']}` | {p['level']} | "
            f"{p['overall_hit']:.2%} | {p['n_days']} | {p['n_pairs']} | "
            f"{p.get('ratio') or '-'} | {'⚠' if p.get('hub_flag') else ''} | "
            f"{'✅' if p.get('in_registry') else '—'} |")


def build_report_md(today, window, nfields, nsamples, left_ids, l1, l4,
                    new_count, verified):
    # 拆分：异号同义（跨编号，高价值）优先；同号镜像（同编号）次之
    cross = [p for p in l1 if not p.get("same_code")]
    same = [p for p in l1 if p.get("same_code")]
    cross.sort(key=lambda p: (not p.get("in_registry", False), -p["overall_hit"], -p["n_days"]))
    same.sort(key=lambda p: (not p.get("in_registry", False), -p["overall_hit"], -p["n_days"]))

    L = []
    L.append(f"# 全源对撞报告（{today}）\n")
    L.append(f"> 数据窗口：{window[0]} ~ {window[-1]}（{len(window)} 天）｜"
             f"字段 {nfields} 个｜样本值 {nsamples} 条")
    L.append(f"> 主攻目标（unverified）={len(left_ids)}｜新增 L1/L1-U 定案={new_count}｜"
             f"异号同义 {len(cross)} / 同号镜像 {len(same)}\n")
    L.append("> **规则**：精度对齐 + 每日命中率≥0.9 + ≥3 独立日 + hub 巧合排除"
             "（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；"
             "新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。\n")
    L.append("---\n")
    L.append(f"## 一、L1 / L1-U 定案候选 — 异号同义（跨编号，高价值）({len(cross)})\n")
    if cross:
        L.append("| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 比值 | hub | registry |")
        L.append("|:--|:--|:--|--:|--:|--:|--:|:--|:--|")
        for p in cross:
            L.append(_l1_row(p))
    else:
        L.append("_本轮无异号同义候选。_\n")
    L.append(f"\n## 二、L1 / L1-U 定案候选 — 同号镜像（同编号，低优先级）({len(same)})\n")
    if same:
        L.append("| 左字段 | 右字段 | 等级 | 命中率 | 天数 | 样本 | 比值 | hub | registry |")
        L.append("|:--|:--|:--|--:|--:|--:|--:|:--|:--|")
        for p in same:
            L.append(_l1_row(p))
    else:
        L.append("_本轮无同号镜像候选。_\n")
    L.append("\n## 三、L4 存疑候选（{0}）\n".format(len(l4)))
    if l4:
        L.append("| 左字段 | 右字段 | 命中率 | 天数 | 样本 |")
        L.append("|:--|:--|--:|--:|--:|")
        for p in l4[:60]:
            L.append(f"| `{p['left']}` | `{p['right']}` | {p['overall_hit']:.2%} | "
                     f"{p['n_days']} | {p['n_pairs']} |")
        if len(l4) > 60:
            L.append(f"\n_（仅显示前 60 / 共 {len(l4)}）_")
    else:
        L.append("_本轮无 L4 候选。_\n")
    L.append("\n---\n")
    L.append("> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。\n")
    return "\n".join(L)


def main():
    if RULES_OK:
        CR.print_active_rules()
    ap = argparse.ArgumentParser(description="全源通用对撞引擎")
    ap.add_argument("--window", type=int, default=7, help="近 N 天窗口（默认 7）")
    ap.add_argument("--all", action="store_true", help="使用全部历史日期")
    ap.add_argument("--date", type=str, default="", help="报告日期戳（默认今天）")
    ap.add_argument("--limit", type=int, default=0, help="仅取前 N 个左字段（自测）")
    ap.add_argument("--min-hit", type=float, default=0.0, help="自定义 L1 命中率（调试）")
    args = ap.parse_args()
    if args.min_hit:
        global HIT_RATE_L1_RATIO
        HIT_RATE_L1_RATIO = args.min_hit
    run(args)


if __name__ == "__main__":
    main()

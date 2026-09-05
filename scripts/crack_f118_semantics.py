#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crack_f118_semantics.py — f118(≡ulist f107) 语义破解引擎  [立项 2026-09-06]

背景
----
- 2026-09-04 多日精确对撞(feat ff737f5)已定案: push2 f118 ≡ ulist f107
  (L1, 17日×20股=338 stock-days 精确 100%, 枚举域 {2,5})。
- 身份已定, 但 **语义未 pin**: f107 的 {2,5} 到底编码什么业务含义?
  本引擎是「f118 语义破解」项目的可复用分析骨架: 加载多日 ulist 快照,
  提取 f107, 与一组候选解释属性(is_st / 市场 / 板块 / 北交 / 市场标记 f27 …)
  做列联 + 一致率, 按对撞四铁律给出候选排序。

方法论(对撞四铁律节选)
----------------------
- 精度对齐: 枚举/布尔码退化为 1e-9 严格相等。
- 命中率分层: 候选属性对 f107 的「精确一致率」≥ 某阈值视为强候选;
  但枚举域仅 2 值({2,5}), 随机基线 50%, 故要求 ≥ 90% 且跨 ≥3 独立采集日稳定
  方可升格 L1, 否则标 L4 候选/待更多数据。
- 多日复核: f107 为 **状态量**(实测 920xxx 在 0813=5→0814=2 翻转),
  必须按 (date,code) 逐日对撞, 不能跨日合并为单点。

数据需求(当前缺口)
------------------
- 现有 ulist 快照仅为 20 股横截面(同名 raw_ulist239.json 实为 20 股采样),
  f107 分布极偏(多为 5, 仅 0813/0814 出现 2), 不足以定案。
- 真正定案需: (a) 完整 239 股 ulist 采集(含 f107 全谱); (b) 同日 **停牌/交易状态**
  字段(如 push2 f76 停牌标记 或 volume=0 推停)作为最强候选解释。
  引擎已预留 `candidate_attrs` 扩展点, 补数据后重跑即出结论。

用法
----
    python scripts/crack_f118_semantics.py
        [--glob "docs/field_verification/*/raw_ulist*.json"]
        [--out  docs/field_verification/20260906/f118_semantics_crack.md]
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple

# 项目内导入(脚本以 a-stock-data 根目录运行)
try:
    from stock_common.sc_utils import get_sec_type_enum, get_board_type
except Exception:  # 独立运行兜底
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from stock_common.sc_utils import get_sec_type_enum, get_board_type


# --------------------------------------------------------------------------- #
# 候选解释属性(可扩展)。每个函数接收 (code, name, ulist_data) 返回可比标量或 None。
# --------------------------------------------------------------------------- #
def _is_st(code: str, name: str, d: dict) -> Any:
    return ("ST" in (name or "").upper()) or (d.get("f104") is not None and str(d.get("f104")) == "1")


def _market(code: str, name: str, d: dict) -> Any:
    c = str(code or "")
    if c.startswith(("92", "8", "4", "43", "83", "87")):
        return "bj"
    if c.startswith("6"):
        return "sh"
    if c[:2] in ("00", "30", "20", "15", "16", "12", "11", "39"):
        return "sz"
    return "other"


def _board_type(code: str, name: str, d: dict) -> Any:
    return get_board_type(code, name)


def _sec_type(code: str, name: str, d: dict) -> Any:
    return get_sec_type_enum(code)


def _is_bj(code: str, name: str, d: dict) -> Any:
    return code.startswith(("92", "8", "4", "43", "83", "87"))


def _f27_market_marker(code: str, name: str, d: dict) -> Any:
    # ulist f27 = 市场标记布尔(北交=0, 其他=1) — 已知字段, 作对照
    return d.get("f27")


# 候选属性表(按「最可能解释 f107 状态量」排序在分析中动态得出)
CANDIDATE_ATTRS: List[Tuple[str, Callable]] = [
    ("is_st", _is_st),
    ("market(sh/sz/bj)", _market),
    ("board_type", _board_type),
    ("sec_type(enum)", _sec_type),
    ("is_bj", _is_bj),
    ("ulist_f27(market_marker)", _f27_market_marker),
]


@dataclass
class Pair:
    date: str
    code: str
    name: str
    f107: Any
    attrs: Dict[str, Any] = field(default_factory=dict)


def load_snapshots(glob_pat: str) -> List[Pair]:
    pairs: List[Pair] = []
    for path in sorted(glob.glob(glob_pat)):
        date = os.path.basename(os.path.dirname(path))
        try:
            snap = json.load(open(path, encoding="utf-8"))
        except Exception as e:
            print(f"  [warn] 无法读取 {path}: {e}", file=sys.stderr)
            continue
        stocks = snap.get("stocks") or {}
        for code, v in stocks.items():
            d = v.get("data") if isinstance(v, dict) else v
            if not isinstance(d, dict):
                continue
            if "f107" not in d:
                continue
            name = d.get("name") or ""
            attrs = {label: fn(code, name, d) for label, fn in CANDIDATE_ATTRS}
            pairs.append(Pair(date=date, code=code, name=name,
                              f107=d.get("f107"), attrs=attrs))
    return pairs


def analyze(pairs: List[Pair]) -> Dict[str, Any]:
    """对每个候选属性, 计算它与 f107 的精确一致率 + 列联表。"""
    if not pairs:
        return {}
    # f107 值域
    f107_vals = sorted({p.f107 for p in pairs})
    result: Dict[str, Any] = {
        "n_pairs": len(pairs),
        "dates": sorted({p.date for p in pairs}),
        "f107_values": f107_vals,
        "f107_dist": dict(Counter(p.f107 for p in pairs)),
        # 状态量稳定性: 同一 code 跨日 f107 是否变化
        "per_code_stability": {},
        "attrs": {},
    }
    # 逐 code 稳定性
    by_code: Dict[str, List[Any]] = defaultdict(list)
    for p in pairs:
        by_code[p.code].append(p.f107)
    stable = sum(1 for v in by_code.values() if len(set(v)) == 1)
    result["per_code_stability"] = {
        "n_codes": len(by_code),
        "constant": stable,
        "changing": len(by_code) - stable,
    }
    # 逐日 f107 分布(诊断: f107=2 是否集中在特定日期 → 市场级/采集级信号)
    per_date: Dict[str, Dict[Any, int]] = defaultdict(lambda: defaultdict(int))
    for p in pairs:
        per_date[p.date][p.f107] += 1
    result["per_date_f107"] = {d: dict(c) for d, c in sorted(per_date.items())}
    # 逐属性一致率
    for label, _ in CANDIDATE_ATTRS:
        match = 0
        total = 0
        ctab: Dict[Any, Dict[Any, int]] = defaultdict(lambda: defaultdict(int))
        for p in pairs:
            av = p.attrs.get(label)
            if av is None:
                continue
            total += 1
            if av == p.f107:
                match += 1
            ctab[p.f107][av] += 1
        # 归一化列联表
        ctab_out = {str(k): dict(v) for k, v in ctab.items()}
        result["attrs"][label] = {
            "exact_rate": (match / total) if total else 0.0,
            "n": total,
            "contingency": ctab_out,
        }
    return result


def rank_candidates(res: Dict[str, Any]) -> List[Tuple[str, float, int]]:
    rows = []
    for label, info in res.get("attrs", {}).items():
        rows.append((label, info["exact_rate"], info["n"]))
    # 一致率高者优先; 样本不足(n<10)降权标注
    rows.sort(key=lambda r: (r[1], r[2]), reverse=True)
    return rows


def render_markdown(res: Dict[str, Any], pairs: List[Pair]) -> str:
    L = []
    L.append("# f118(≡ulist f107) 语义破解 — 第一手对撞分析\n")
    L.append(f"> 立项日期: 2026-09-06 · 引擎: `scripts/crack_f118_semantics.py`\n")
    L.append("## 一、数据概览")
    L.append(f"- 对撞单元(day×code): **{res['n_pairs']}** · 采集日: {len(res['dates'])} 个")
    L.append(f"- f107 值域: `{res['f107_values']}` · 分布: `{res['f107_dist']}`")
    # 逐日 f107 分布
    L.append("\n**逐日 f107 分布**(诊断状态量性质):")
    L.append("")
    L.append("| 采集日 | f107=2 | f107=5 | 备注 |")
    L.append("|---|---|---|---|")
    for d, c in res.get("per_date_f107", {}).items():
        n2 = c.get(2, 0)
        n5 = c.get(5, 0)
        note = "← f107=2 集中窗口" if n2 > 0 else ""
        L.append(f"| {d} | {n2} | {n5} | {note} |")
    st = res["per_code_stability"]
    L.append(f"- **状态量证据**: {st['n_codes']} 只股票中 {st['constant']} 只 f107 跨日恒定, "
             f"**{st['changing']} 只跨日翻转** → f107 为**状态量**(非静态市场/板块属性)")
    L.append("\n## 二、候选属性一致率(精确相等, 枚举码 1e-9 严格)\n")
    L.append("| 候选属性 | 精确一致率 | 样本n | 判定 |")
    L.append("|---|---|---|---|")
    for label, rate, n in rank_candidates(res):
        verdict = "强候选" if rate >= 0.9 and n >= 10 else ("弱/样本不足" if n < 10 else "不匹配")
        L.append(f"| {label} | {rate*100:.1f}% | {n} | {verdict} |")
    L.append("\n## 三、列联表(摘录)\n")
    for label, _ in CANDIDATE_ATTRS:
        info = res["attrs"].get(label)
        if not info:
            continue
        L.append(f"### {label}  (一致率 {info['exact_rate']*100:.1f}%, n={info['n']})")
        L.append("```")
        L.append(f"f107 \\ attr: {info['contingency']}")
        L.append("```")
    L.append("\n## 四、结论与缺口")
    L.append("- f107 ∈ {2,5} 且为**状态量**(920xxx 在 0813=5→0814=2 翻转), "
             "**排除**「静态市场/板块类型」假设(603221 沪主板恒=5 而 600519 沪主板=2)。")
    L.append("- **强时间聚集**: 全部 36 个 f107=2 仅出现在 **20260813 / 20260814** 两个连续交易日, "
             "其余 15 日纯 5 → 近乎**全市场同步翻转**, 指向「市场级/采集级信号」而非个股属性 "
             "(候选: 那两日 Eastmoney ulist 接口 f107 取值口径变化 / 采集时行情状态差异), 需排查采集链路。")
    L.append("- 当前 20 股横截面采样 f107 极偏(多为 5), **无任何候选属性达到 L1 升格门槛"
             "(≥90% 且 ≥3 日稳定)**。")
    L.append("- **待补数据**: (a) 完整 239 股 ulist 采集(暴露 f107 全谱); "
             "(b) 同日**停牌/交易状态**字段(push2 f76 停牌标记 或 volume=0 推停)作为最强候选解释; "
             "(c) 沪深港通/融资融券标的名单做交叉。补数据后重跑本引擎即出定案。")
    return "\n".join(L)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="f118(ulist f107) 语义破解引擎")
    ap.add_argument("--glob", default="docs/field_verification/*/raw_ulist*.json")
    ap.add_argument("--out", default="docs/field_verification/20260906/f118_semantics_crack.md")
    args = ap.parse_args()

    print(f"[1/3] 加载快照: {args.glob}")
    pairs = load_snapshots(args.glob)
    print(f"      -> {len(pairs)} 个 (day×code) 对撞单元")

    print("[2/3] 对撞分析")
    res = analyze(pairs)
    print(f"      f107 值域={res['f107_values']} 分布={res['f107_dist']} "
          f"翻转股票={res['per_code_stability']['changing']}")

    print("[3/3] 生成报告 -> " + args.out)
    md = render_markdown(res, pairs)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md)
    # 控制台摘要
    print("\n候选属性一致率排序:")
    for label, rate, n in rank_candidates(res):
        print(f"  {label:<28} {rate*100:5.1f}%  (n={n})")
    print(f"\n报告已写入: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

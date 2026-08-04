#!/usr/bin/env python3
"""compare_baseline.py — 差异分析引擎（Auto-Fix Pipeline 子项目 2: diff-engine）

输入两份基线 JSON（capture_baseline.py 输出），逐维度对比，生成 diff_specs/*.yaml。

对比维度（优先级递减）：
  P0  值归零      v9.6 非零 / v15 为 0 或空（仅两个 runtime 基线可判定）
  P1  存在性翻转   v9.6 有（标签/字段/数据源调用/章节）→ v15 完全没有
  P2  数据源丢失   v9.6 有数据源调用 → v15 数据源调用减少（static 对比）
  P3  格式差异     语义等价但形式不同（仅记录）

用法示例:
  python scripts/compare_baseline.py --v9 baselines/v9_6_static_xxx.json \
      --v15 baselines/v15_4_static_yyy.json --out diff_specs
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_SPECS_DIR = Path(__file__).resolve().parent.parent / "diff_specs"

# YAML 安全标量转义（避免特殊字符破坏 YAML）
def _yaml_scalar(s: str) -> str:
    if s == "" or re.search(r"[:#\[\]{}&*!|>'\",%@`]", s) or s != s.strip():
        return json.dumps(s, ensure_ascii=False)
    return s


def _write_spec(specs_dir: Path, spec: dict) -> bool:
    """写入一个 diff_spec；若已存在（同 id）则不覆盖（保留 Agent 工作进度）。"""
    out = specs_dir / f"{spec['id']}.yaml"
    if out.exists():
        return False
    lines = [
        f"id: {_yaml_scalar(spec['id'])}",
        f"report: {_yaml_scalar(spec['report'])}",
        f"kind: {_yaml_scalar(spec['kind'])}",
        f"name: {_yaml_scalar(spec['name'])}",
        f"priority: {spec['priority']}",
        f"status: pending",
        f"v9_present: {str(spec.get('v9_present', True)).lower()}",
        f"v15_present: {str(spec.get('v15_present', False)).lower()}",
        "",
        "detail: |",
    ]
    for line in spec["detail"].splitlines():
        lines.append(f"  {line}" if line else "  ")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return True


def _gen_specs(report: str, kind: str, name: str, v9_present: bool, v15_present: bool,
               priority: str, detail: str) -> dict:
    return {
        "id": f"{report}.{kind}.{name}",
        "report": report,
        "kind": kind,
        "name": name,
        "priority": priority,
        "v9_present": v9_present,
        "v15_present": v15_present,
        "detail": detail,
    }


def _extract_label_counts(r: dict) -> dict:
    """归一化: labels 或 stocks[code].fields（runtime）→ {名称: 是否非空}"""
    out: dict[str, bool] = {}
    labels = r.get("labels", {})
    for name, info in labels.items():
        out[name] = bool(info)
    return out


def _extract_runtime_label_counts(r: dict) -> dict:
    """runtime 基线的输出字段（按'名称: 值'提取）→ {名称: 是否非空}"""
    out: dict[str, bool] = {}
    stocks = r.get("stocks", {})
    for code, st in stocks.items():
        for name, val in st.get("fields", {}).items():
            out[name] = bool(val and val not in ("0", "0.00", "0.0", "N/A", "无"))
    return out


def _numeric(val) -> float | None:
    """从值字符串提取数值（'981.80亿元' → 981.8）；失败返回 None。"""
    if val is None:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", str(val))
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def compare_static_static(v9: dict, v15: dict, specs_dir: Path) -> list[dict]:
    """static vs static: 存在性 + 数据源调用差异。

    只对比双方 meta.reports 都声明采集过的报告（未采集 ≠ 缺失）。
    """
    created: list[dict] = []
    v15_collected = set(v15.get("meta", {}).get("reports", [])) or set(v15.get("reports", {}).keys())
    for rep, v9_r in v9.get("reports", {}).items():
        if rep not in v15_collected:
            continue
        v15_r = v15.get("reports", {}).get(rep)
        if v15_r is None:
            spec = _gen_specs(rep, "report", "whole_report", True, False, "P0",
                              f"v9.6 有报告 {rep}，v15 完全没有该报告")
            if _write_spec(specs_dir, spec):
                created.append(spec)
            continue

        # 1) 数据源调用差异（丢失的信号）
        v9_calls = set(v9_r.get("data_calls", []))
        v15_calls = set(v15_r.get("data_calls", []))
        for call in sorted(v9_calls - v15_calls):
            detail = (f"v9.6 报告 {rep} 调用数据源函数 {call}\n"
                      f"v15 报告 {rep} 未找到该调用（数据源丢失或改名）")
            spec = _gen_specs(rep, "data_call", call, True, False, "P1", detail)
            if _write_spec(specs_dir, spec):
                created.append(spec)

        # 2) 中文标签差异
        v9_labels = set(v9_r.get("labels", {}).keys())
        v15_labels = set(v15_r.get("labels", {}).keys())
        for lab in sorted(v9_labels - v15_labels):
            detail = (f"v9.6 报告 {rep} 有输出标签「{lab}」\n"
                      f"v15 报告 {rep} 无此标签（字段缺失或输出行被删）")
            spec = _gen_specs(rep, "label", lab, True, False, "P1", detail)
            if _write_spec(specs_dir, spec):
                created.append(spec)

        # 3) 表达式字段差异
        v9_fields = set(v9_r.get("fields", {}).keys())
        v15_fields = set(v15_r.get("fields", {}).keys())
        for fld in sorted(v9_fields - v15_fields):
            detail = (f"v9.6 报告 {rep} 有表达式字段 {fld}\n"
                      f"v15 报告 {rep} 无此字段")
            spec = _gen_specs(rep, "field", fld, True, False, "P2", detail)
            if _write_spec(specs_dir, spec):
                created.append(spec)

        # 4) 章节差异
        v9_secs = set(v9_r.get("sections", []))
        v15_secs = set(v15_r.get("sections", []))
        for sec in sorted(v9_secs - v15_secs):
            detail = f"v9.6 有章节「{sec}」，v15 缺失"
            spec = _gen_specs(rep, "section", sec, True, False, "P1", detail)
            if _write_spec(specs_dir, spec):
                created.append(spec)
    return created


def compare_static_runtime(v9: dict, v15: dict, specs_dir: Path) -> list[dict]:
    """v9 static vs v15 runtime: 标签存在性 + 值归零。"""
    created: list[dict] = []
    v15_collected = set(v15.get("meta", {}).get("reports", [])) or set(v15.get("reports", {}).keys())
    for rep, v9_r in v9.get("reports", {}).items():
        if rep not in v15_collected:
            continue
        v15_r = v15.get("reports", {}).get(rep)
        if v15_r is None:
            continue
        v9_labels = set(v9_r.get("labels", {}).keys())
        rt_labels = _extract_runtime_label_counts(v15_r)
        for lab in sorted(v9_labels - set(rt_labels.keys())):
            detail = (f"v9.6 报告 {rep} 有标签「{lab}」\n"
                      f"v15 实跑输出无此标签行（输出缺失）")
            spec = _gen_specs(rep, "label_missing", lab, True, False, "P0", detail)
            if _write_spec(specs_dir, spec):
                created.append(spec)
        # 值归零: v9.6 static 无法给期望值，仅记录 v15 输出中为 0 的标签
        for name, present in rt_labels.items():
            if not present:
                detail = f"v15 实跑 {rep} 输出「{name}」为空/0（需对照 v9.6 确认是否退化）"
                spec = _gen_specs(rep, "label_zero", name, True, False, "P2", detail)
                if _write_spec(specs_dir, spec):
                    created.append(spec)
    return created


def compare_runtime_runtime(v9: dict, v15: dict, specs_dir: Path) -> list[dict]:
    """runtime vs runtime: 值归零 + 精度下降。"""
    created: list[dict] = []
    v15_collected = set(v15.get("meta", {}).get("reports", [])) or set(v15.get("reports", {}).keys())
    for rep, v9_r in v9.get("reports", {}).items():
        if rep not in v15_collected:
            continue
        v15_r = v15.get("reports", {}).get(rep)
        if v15_r is None:
            continue
        v9_fields = _extract_runtime_label_counts(v9_r)
        v15_fields = _extract_runtime_label_counts(v15_r)
        for name, v9_present in v9_fields.items():
            v15_present = v15_fields.get(name, None)
            if v15_present is None:
                detail = f"v9.6 实跑 {rep} 有「{name}」，v15 实跑无此字段"
                spec = _gen_specs(rep, "field_missing", name, True, False, "P1", detail)
            elif v9_present and not v15_present:
                detail = f"v9.6 实跑 {rep}「{name}」非空，v15 实跑为空/0（数据归零）"
                spec = _gen_specs(rep, "field_zero", name, True, False, "P0", detail)
            else:
                continue
            if _write_spec(specs_dir, spec):
                created.append(spec)
    return created


def main() -> int:
    ap = argparse.ArgumentParser(description="基线差异分析 → diff_specs")
    ap.add_argument("--v9", required=True, help="v9.6 基线 JSON")
    ap.add_argument("--v15", required=True, help="v15 基线 JSON")
    ap.add_argument("--out", default=str(DEFAULT_SPECS_DIR), help="diff_specs 输出目录")
    ap.add_argument("--min-priority", default="P3", choices=["P0", "P1", "P2", "P3"],
                    help="最低输出优先级（默认 P3 全部输出）")
    args = ap.parse_args()

    v9 = json.loads(Path(args.v9).read_text(encoding="utf-8"))
    v15 = json.loads(Path(args.v15).read_text(encoding="utf-8"))
    specs_dir = Path(args.out)
    specs_dir.mkdir(parents=True, exist_ok=True)

    v9_mode, v15_mode = v9["meta"]["mode"], v15["meta"]["mode"]
    print(f"[compare_baseline] v9.mode={v9_mode} v15.mode={v15_mode} → {specs_dir}")

    if v9_mode == "static" and v15_mode == "static":
        created = compare_static_static(v9, v15, specs_dir)
    elif v9_mode == "static" and v15_mode == "runtime":
        created = compare_static_runtime(v9, v15, specs_dir)
    elif v9_mode == "runtime" and v15_mode == "runtime":
        created = compare_runtime_runtime(v9, v15, specs_dir)
    else:
        print("[compare_baseline] 不支持的基线组合（v9=runtime 且 v15=static）")
        return 1

    prio_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    created.sort(key=lambda s: (prio_order[s["priority"]], s["id"]))
    stats: dict[str, int] = {}
    for s in created:
        stats[s["priority"]] = stats.get(s["priority"], 0) + 1
    print(f"[compare_baseline] 新增 {len(created)} 个 diff_spec（"
          + ", ".join(f"{k}={v}" for k, v in sorted(stats.items())) + "）")
    for s in created:
        print(f"  [{s['priority']}] {s['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""auto_fix_pipeline.py — 自动化修复流水线总入口（Auto-Fix Pipeline v1.0）

把"分析 v9.6 → 对比 v15 → 修改 → 测试 → 验证"的人工迭代自动化。
Agent（Reasonix）通过本脚本 CLI 驱动，每个 diff_spec 原子化、可回滚、可恢复。

子命令:
  init            初始化: 创建 baselines/ diff_specs/ 目录 + pipeline_state.json
                  [--snapshot] 可选: git add -A + commit 当前工作区（基线快照）
  analyze         基线捕获(v9.6 static + v15 static) + 对比 → diff_specs/*.yaml
                  --stocks 000100  --reports sht,med,lng,ful
  fix             --spec <id>          标记 spec pending → fixing（Agent 开始改代码）
                  --spec <id> --result ok|fail|blocked --note "..."   标记修复结果
  verify          --spec <id>          重跑 static 采集+对比 → resolved/blocked
                  --runtime            可选: 实跑报告验证（慢，需网络）
  status          查看 pipeline_state.json + diff_specs 状态汇总
  report          生成 docs/fix_report.md（含 CHANGELOG 建议）

用法示例:
  python scripts/auto_fix_pipeline.py init
  python scripts/auto_fix_pipeline.py analyze --reports sht,med
  python scripts/auto_fix_pipeline.py fix --spec sht.data_call.tdx_get_quote_full
  python scripts/auto_fix_pipeline.py fix --spec <id> --result fail --note "需要人工决策"
  python scripts/auto_fix_pipeline.py verify --spec <id>
  python scripts/auto_fix_pipeline.py status
  python scripts/auto_fix_pipeline.py report
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
SPECS_DIR = ROOT / "diff_specs"
BASELINES_DIR = ROOT / "baselines"
STATE_FILE = ROOT / "pipeline_state.json"
FIX_REPORT = ROOT / "docs" / "fix_report.md"

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}

# ---------- 工具 ----------

def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "phase": "init", "specs_total": 0, "specs_resolved": 0,
        "specs_blocked": 0, "current_spec": None,
        "last_run": _now(), "history": [],
    }


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _log(state: dict, action: str, detail: str) -> None:
    state.setdefault("history", []).append({"ts": _now(), "action": action, "detail": detail})
    state["last_run"] = _now()


def _list_specs() -> list[Path]:
    if not SPECS_DIR.exists():
        return []
    return sorted(SPECS_DIR.glob("*.yaml"))


def _read_spec_status(spec_path: Path) -> str:
    """从 YAML 读取 status 字段（纯正则，不依赖 PyYAML）。"""
    try:
        for line in spec_path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^status:\s*(\S+)", line)
            if m:
                return m.group(1)
    except OSError:
        pass
    return "unknown"


def _write_spec_status(spec_path: Path, status: str) -> None:
    """就地更新 YAML 的 status 字段（保留其余内容）。"""
    txt = spec_path.read_text(encoding="utf-8")
    new_txt = re.sub(r"^status:\s*\S+", f"status: {status}", txt, count=1, flags=re.M)
    if new_txt == txt:  # 没有 status 行，追加
        new_txt = txt.rstrip() + f"\nstatus: {status}\n"
    spec_path.write_text(new_txt, encoding="utf-8")


def _refresh_spec_stats(state: dict) -> dict:
    """从磁盘扫描 diff_specs 刷新统计。"""
    specs = _list_specs()
    counts = {"pending": 0, "fixing": 0, "verifying": 0, "resolved": 0, "blocked": 0, "unknown": 0}
    for p in specs:
        s = _read_spec_status(p)
        counts[s] = counts.get(s, 0) + 1
    state["specs_total"] = len(specs)
    state["specs_resolved"] = counts["resolved"]
    state["specs_blocked"] = counts["blocked"]
    return counts


def _find_spec(spec_id: str) -> Path | None:
    p = SPECS_DIR / f"{spec_id}.yaml"
    return p if p.exists() else None


# ---------- 子命令 ----------

def cmd_init(args) -> int:
    SPECS_DIR.mkdir(parents=True, exist_ok=True)
    BASELINES_DIR.mkdir(parents=True, exist_ok=True)
    state = _load_state()
    state["phase"] = "init"
    _log(state, "init", f"目录就绪: {SPECS_DIR.name}/ {BASELINES_DIR.name}/")
    _save_state(state)
    print(f"[init] 目录就绪: {SPECS_DIR} / {BASELINES_DIR}")
    if args.snapshot:
        # git 快照: 把当前工作区固化为 commit（v10-v15 无 git 历史，快照是版本回溯的前提）
        tag = f"snapshot-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        r = subprocess.run(["git", "add", "-A"], cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[init] git add 失败: {r.stderr[-300:]}")
            return 1
        r = subprocess.run(["git", "commit", "-m", f"pipeline snapshot before auto-fix ({tag})"],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[init] git commit 失败（可能无变更）: {r.stderr[-300:]}")
            return 1
        subprocess.run(["git", "tag", tag], cwd=ROOT, capture_output=True)
        _log(state, "init", f"git 快照 tag={tag}")
        _save_state(state)
        print(f"[init] git 快照完成: tag={tag}")
    return 0


def cmd_analyze(args) -> int:
    reports = args.reports
    # 1) 采集 v9.6 static
    print("=== 采集 v9.6 static 基线 ===")
    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "capture_baseline.py"),
         "--mode", "static", "--version", "v9.6", "--reports", reports,
         "--out", str(BASELINES_DIR)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr[-500:])
        return 1
    v9_file = _latest_baseline("v9_6_static")
    # 2) 采集 v15 static
    print("=== 采集 v15 static 基线 ===")
    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "capture_baseline.py"),
         "--mode", "static", "--version", args.v15_version, "--reports", reports,
         "--out", str(BASELINES_DIR)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr[-500:])
        return 1
    v15_file = _latest_baseline(f"{args.v15_version.replace('.', '_')}_static")
    # 3) 对比
    print("=== 差异对比 ===")
    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "compare_baseline.py"),
         "--v9", str(v9_file), "--v15", str(v15_file), "--out", str(SPECS_DIR)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr[-500:])
        return 1
    state = _load_state()
    state["phase"] = "analyze"
    counts = _refresh_spec_stats(state)
    _log(state, "analyze", f"生成 diff_specs: {counts}")
    _save_state(state)
    print(f"[analyze] 完成。diff_specs 状态: {counts}")
    return 0


def _latest_baseline(prefix: str) -> Path:
    files = sorted(BASELINES_DIR.glob(f"{prefix}_*.json"))
    if not files:
        print(f"[error] 未找到基线: {prefix}_*.json，请先运行 analyze 或 capture_baseline")
        sys.exit(1)
    return files[-1]


def cmd_fix(args) -> int:
    spec_path = _find_spec(args.spec)
    if spec_path is None:
        print(f"[fix] 未找到 spec: {args.spec}")
        return 1
    state = _load_state()
    if args.result:
        # 标记修复结果
        if args.result == "ok":
            _write_spec_status(spec_path, "fixing_ready")
            state["current_spec"] = None
            _log(state, "fix", f"{args.spec}: 修复完成，等待 verify")
            print(f"[fix] {args.spec} → fixing_ready（请运行 verify 确认）")
        elif args.result == "fail":
            _write_spec_status(spec_path, "blocked")
            state["current_spec"] = None
            _log(state, "fix", f"{args.spec}: 修复失败，已标记 blocked。note={args.note or ''}")
            print(f"[fix] {args.spec} → blocked（note={args.note or '无'}）")
        elif args.result == "blocked":
            _write_spec_status(spec_path, "blocked")
            state["current_spec"] = None
            _log(state, "fix", f"{args.spec}: 挂起 blocked（需人工决策）。note={args.note or ''}")
            print(f"[fix] {args.spec} → blocked（需人工决策，note={args.note or '无'}）")
    else:
        # 开始修复: pending → fixing
        status = _read_spec_status(spec_path)
        if status not in ("pending", "fixing"):
            print(f"[fix] {args.spec} 当前状态 {status}，不能重复开始修复")
            return 1
        _write_spec_status(spec_path, "fixing")
        state["current_spec"] = args.spec
        _log(state, "fix", f"{args.spec}: 开始修复（pending→fixing）")
        print(f"[fix] {args.spec} → fixing（Agent 现在修改代码，改完跑 verify）")
    state["phase"] = "fix"
    _save_state(state)
    return 0


def cmd_verify(args) -> int:
    spec_path = _find_spec(args.spec)
    if spec_path is None:
        print(f"[verify] 未找到 spec: {args.spec}")
        return 1
    spec_id = args.spec
    report, kind, name = spec_id.split(".", 2)

    # 1) 重新采集 v15 static（快速）并对比：若该 spec 不再生成 → 修复有效
    print(f"[verify] 重跑 v15 static 采集 + 对比（验证 {spec_id}）...")
    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "capture_baseline.py"),
         "--mode", "static", "--version", args.v15_version, "--reports", report,
         "--out", str(BASELINES_DIR)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stderr[-500:])
        return 1
    # 暂存当前 spec 的 diff_spec 文件，重跑对比
    v15_file = _latest_baseline(f"{args.v15_version.replace('.', '_')}_static")
    # 用最小对比：直接查新基线中该元素是否恢复
    new_baseline = json.loads(v15_file.read_text(encoding="utf-8"))
    rep_data = new_baseline.get("reports", {}).get(report, {})
    present = False
    if kind == "data_call":
        present = name in rep_data.get("data_calls", [])
    elif kind == "label":
        present = name in rep_data.get("labels", {})
    elif kind == "field":
        present = name in rep_data.get("fields", {})
    elif kind == "section":
        present = any(name in s for s in rep_data.get("sections", []))

    state = _load_state()
    if present:
        _write_spec_status(spec_path, "resolved")
        _log(state, "verify", f"{spec_id}: 静态验证通过（v15 已恢复该元素）→ resolved")
        print(f"[verify] {spec_id} → resolved（static 验证通过）")
        if args.runtime:
            print("[verify] --runtime 模式：请手动运行 python main.py --<report> <code> --no-upload 实跑确认")
    else:
        _write_spec_status(spec_path, "blocked")
        _log(state, "verify", f"{spec_id}: 静态验证失败（v15 仍缺该元素）→ blocked")
        print(f"[verify] {spec_id} → blocked（static 验证未通过，请检查修复）")
    state["phase"] = "verify"
    _refresh_spec_stats(state)
    _save_state(state)
    return 0


def cmd_status(args) -> int:
    state = _load_state()
    counts = _refresh_spec_stats(state)
    _save_state(state)
    print(f"phase: {state['phase']}")
    print(f"diff_specs: total={counts['pending'] + counts['fixing'] + counts['verifying'] + counts['resolved'] + counts['blocked']} "
          f"(pending={counts['pending']} fixing={counts['fixing']} verifying={counts['verifying']} "
          f"resolved={counts['resolved']} blocked={counts['blocked']})")
    print(f"current_spec: {state['current_spec']}")
    print(f"last_run: {state['last_run']}")
    print("\n未解决 spec（按优先级）:")
    specs = _list_specs()
    rows = []
    for p in specs:
        st = _read_spec_status(p)
        if st not in ("resolved",):
            txt = p.read_text(encoding="utf-8")
            m = re.search(r"^priority:\s*(\S+)", txt, re.M)
            prio = m.group(1) if m else "P9"
            rows.append((PRIORITY_ORDER.get(prio, 9), prio, p.stem, st))
    for _, prio, sid, st in sorted(rows):
        print(f"  [{prio}] {sid} ({st})")
    return 0


def cmd_report(args) -> int:
    state = _load_state()
    counts = _refresh_spec_stats(state)
    _save_state(state)
    specs = _list_specs()
    lines = [
        "# 自动修复流水线报告（Auto-Fix Pipeline）",
        "",
        f"- 生成时间: {_now()}",
        f"- Phase: {state['phase']}",
        f"- diff_specs 总数: {len(specs)}（resolved={counts['resolved']} blocked={counts['blocked']} "
        f"进行中={counts['fixing'] + counts['verifying'] + counts['pending']}）",
        "",
        "## 未解决 diff_specs",
        "",
        "| 优先级 | ID | 状态 |",
        "|:---:|:---|:---:|",
    ]
    for p in specs:
        st = _read_spec_status(p)
        if st == "resolved":
            continue
        txt = p.read_text(encoding="utf-8")
        m = re.search(r"^priority:\s*(\S+)", txt, re.M)
        prio = m.group(1) if m else "P9"
        lines.append(f"| {prio} | `{p.stem}` | {st} |")
    lines += ["", "## 已解决 diff_specs", "", "| 优先级 | ID | 状态 |", "|:---:|:---|:---:|"]
    for p in specs:
        st = _read_spec_status(p)
        if st != "resolved":
            continue
        txt = p.read_text(encoding="utf-8")
        m = re.search(r"^priority:\s*(\S+)", txt, re.M)
        prio = m.group(1) if m else "P9"
        lines.append(f"| {prio} | `{p.stem}` | {st} |")
    lines += [
        "",
        "## CHANGELOG 建议",
        "",
        "全部 P0/P1 解决后，建议在 CHANGELOG.md 顶部新增:",
        "```",
        "## [15.x] - <日期>",
        "**数据精度回归修复**：对照 a-stock-data-v9.6 恢复字段（详见 docs/fix_report.md）",
        "```",
        "",
    ]
    FIX_REPORT.parent.mkdir(parents=True, exist_ok=True)
    FIX_REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"[report] 已生成 {FIX_REPORT}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="自动化修复流水线总入口")
    sub = ap.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="初始化目录 + 可选 git 快照")
    p_init.add_argument("--snapshot", action="store_true", help="git add -A + commit + tag 当前工作区")

    p_an = sub.add_parser("analyze", help="基线捕获 + 差异对比 → diff_specs")
    p_an.add_argument("--reports", default="sht,med,lng,ful", help="报告类型，逗号分隔")
    p_an.add_argument("--v15-version", default="v15.4", help="v15 版本标识")

    p_fix = sub.add_parser("fix", help="标记修复状态")
    p_fix.add_argument("--spec", required=True, help="diff_spec id，如 sht.data_call.tdx_get_quote_full")
    p_fix.add_argument("--result", choices=["ok", "fail", "blocked"], help="修复结果标记")
    p_fix.add_argument("--note", default="", help="结果备注")

    p_ver = sub.add_parser("verify", help="验证修复（重跑 static 采集对比）")
    p_ver.add_argument("--spec", required=True, help="diff_spec id")
    p_ver.add_argument("--v15-version", default="v15.4", help="v15 版本标识")
    p_ver.add_argument("--runtime", action="store_true", help="提示实跑验证（需网络）")

    sub.add_parser("status", help="查看流水线状态")
    sub.add_parser("report", help="生成 docs/fix_report.md")

    args = ap.parse_args()
    if args.command == "init":
        return cmd_init(args)
    if args.command == "analyze":
        return cmd_analyze(args)
    if args.command == "fix":
        return cmd_fix(args)
    if args.command == "verify":
        return cmd_verify(args)
    if args.command == "status":
        return cmd_status(args)
    if args.command == "report":
        return cmd_report(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())

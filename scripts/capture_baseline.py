#!/usr/bin/env python3
"""capture_baseline.py — 基线捕获脚本（Auto-Fix Pipeline 子项目 1: baseline-capture）

两种模式：
  static  从源码静态提取字段契约（不运行代码）
          - v9.6: 读取 a-stock-data-v9.6/ 下的报告脚本
          - v15.x: 读取当前工作区报告脚本
  runtime 实跑当前工作区报告脚本，解析 reports/ 输出 txt 提取字段实际值

输出: baselines/<version>_<mode>_<ts>.json
      {meta, reports: {<report>: {sections: [...], fields: {<name>: {value, source, line}}, data_calls: [...]}}}

用法示例:
  python scripts/capture_baseline.py --mode static --version v9.6 --reports sht,med
  python scripts/capture_baseline.py --mode static --version v15.4 --reports sht
  python scripts/capture_baseline.py --mode runtime --version v15.4 --stocks 000100 --reports sht,med --timeout 900
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ---- 路径 ----
ROOT = Path(__file__).resolve().parent.parent          # 项目根 D:\GitHub\test
V9_DIR = ROOT / "a-stock-data-v9.6"                    # v9.6 独立副本
REPORTS_DIR = ROOT / "reports"                         # 报告输出目录
DEFAULT_OUT = ROOT / "baselines"

REPORT_SCRIPTS = {
    "sht": "get_sht_report.py",
    "med": "get_med_report.py",
    "lng": "get_lng_report.py",
    "ful": "get_ful_report.py",
    "val": "get_val_report.py",
    "mak": "get_mak_report.py",
}

# 章节标题模式: 【一、xxx】 / 【二、xxx】
SECTION_RE = re.compile(r"【([一二三四五六七八九十百]+)、([^】]+)】")
# 输出行字段模式: L(f"xxx: {q.get('yyy', 0)}") 或 L(f"总市值: {q.get('mcap_yi', 0)}亿元")
# 提取 L("..." 与 L(f"..." 中的字符串片段
OUTPUT_LINE_RE = re.compile(r"L\(\s*(?:f?)([\"'])(.*?)\1", re.DOTALL)
# 数据源函数调用: get_xxx( / tdx_get_xxx( / em_xxx( / to_thread(func, ...) 包装
DATA_CALL_RE = re.compile(
    r"(?:(?:tdx_|em_|ths_|get_|zhb_|sina_|tencent_)[a-z0-9_]+)\(|"
    r"to_thread\(\s*((?:tdx_|em_|ths_|get_|zhb_|sina_|tencent_)[a-z0-9_]+)"
)
# 字段占位符: {xxx} / {q.get('yyy', 0):.2f} / {cdata.mcap_yi} / {q['pe']}
# 注意: f-string 格式化占位符 {expr:format} 的 expr 部分不含 ':'，故用 [^{}:]+ 捕获
PLACEHOLDER_RE = re.compile(r"\{([^{}:]+)(?::[^}]*)?\}")

# runtime 输出值提取: "总市值:   981.80亿元" → ("总市值", "981.80亿元")
RUNTIME_VALUE_RE = re.compile(r"^\s*([^:：]{2,24})[:：]\s*([^\s].*)$")


# ---------- static 模式 ----------

def extract_sections(src: str) -> list[str]:
    """提取报告章节标题列表。"""
    return [f"【{num}、{title}】" for num, title in SECTION_RE.findall(src)]


def extract_data_calls(src: str) -> list[str]:
    """提取数据源函数调用（去重、保序）。

    兼容两种调用形态:
      blocks = get_concept_blocks(code)              # 直接调用
      await asyncio.to_thread(get_concept_blocks, code)  # to_thread 包装
    """
    calls = []
    for m in DATA_CALL_RE.finditer(src):
        if m.group(1):                       # to_thread(func, ...) 分支
            name = m.group(1)
        else:                                # 直接调用分支，去掉尾部 '('
            name = m.group(0).rstrip("(")
        if name not in calls:
            calls.append(name)
    return calls


def extract_fields(src: str) -> tuple[dict, dict]:
    """从输出行提取字段契约。

    返回 (fields, labels):
      fields: {表达式字段名: {output_lines, exprs}}  如 mcap_yi / change_pct
      labels: {中文标签: {output_lines}}              如 总市值 / 概念板块
    """
    fields: dict[str, dict] = {}
    labels: dict[str, dict] = {}
    for m in OUTPUT_LINE_RE.finditer(src):
        line_content = m.group(2)
        if not line_content:
            continue
        # 中文标签: "总市值: {q.get(...)}亿元" → "总市值"
        # 注意: 源码中 \n \t 是字面转义序列（2 字符），先 unescape 再匹配空白
        unescaped = line_content.replace("\\n", "\n").replace("\\t", "\t")
        tag_m = re.match(r"^\s*([^:：{]{2,24})[:：]", unescaped)
        if tag_m and re.search(r"[\u4e00-\u9fff]", tag_m.group(1)):
            tag = tag_m.group(1).strip()
            if tag not in labels:
                labels[tag] = {"output_lines": []}
            if line_content[:60] not in labels[tag]["output_lines"]:
                labels[tag]["output_lines"].append(line_content[:60])
        for pm in PLACEHOLDER_RE.finditer(line_content):
            expr = pm.group(1)
            # 字段名提取: q.get('mcap_yi', 0) → mcap_yi ; q['pe'] → pe ;
            #             cdata.mcap_yi → mcap_yi ; 纯标识符 → 自身
            name = None
            m_get = re.search(r"[.\[]get\(\s*['\"]([^'\"]+)['\"]", expr)
            m_key = re.search(r"\[['\"]([^'\"]+)['\"]\]", expr)
            m_attr = re.search(r"\.([a-zA-Z_][a-zA-Z0-9_]*)$", expr)
            m_plain = re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", expr)
            if m_get:
                name = m_get.group(1)
            elif m_key:
                name = m_key.group(1)
            elif m_attr:
                name = m_attr.group(1)
            elif m_plain:
                name = expr
            if not name:
                continue
            if name not in fields:
                fields[name] = {"output_lines": [], "exprs": []}
            if line_content[:60] not in fields[name]["output_lines"]:
                fields[name]["output_lines"].append(line_content[:60])
            if expr not in fields[name]["exprs"]:
                fields[name]["exprs"].append(expr[:60])
    return fields, labels


def capture_static(version: str, reports: list[str]) -> dict:
    """static 模式：从源码提取字段契约。"""
    src_dir = V9_DIR if version.startswith("v9") else ROOT
    result: dict = {"meta": {}, "reports": {}}
    for rep in reports:
        script = REPORT_SCRIPTS.get(rep)
        if not script:
            print(f"  [skip] 未知报告类型: {rep}")
            continue
        src_path = src_dir / script
        if not src_path.exists():
            print(f"  [skip] 源码不存在: {src_path}")
            continue
        src = src_path.read_text(encoding="utf-8", errors="replace")
        fields, labels = extract_fields(src)
        result["reports"][rep] = {
            "sections": extract_sections(src),
            "data_calls": extract_data_calls(src),
            "fields": fields,
            "labels": labels,
            "script": str(src_path),
            "script_size": src_path.stat().st_size,
        }
        print(f"  [ok] {rep}: {src_path.name} 章节={len(result['reports'][rep]['sections'])} "
              f"数据源调用={len(result['reports'][rep]['data_calls'])} 字段={len(fields)} 标签={len(labels)}")
    return result


# ---------- runtime 模式 ----------

def run_report(rep: str, code: str, timeout: int) -> tuple[bool, str]:
    """实跑报告脚本（走 main.py 子进程入口），返回 (成功?, 输出文件路径)。"""
    cmd = [sys.executable, "main.py", f"--{rep}", code, "--no-upload"]
    print(f"  [run] {' '.join(cmd)} (timeout={timeout}s)")
    try:
        proc = subprocess.run(
            cmd, cwd=ROOT, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
        print(f"  [run] exit={proc.returncode}")
        if proc.returncode != 0:
            tail = proc.stderr[-800:] if proc.stderr else proc.stdout[-800:]
            print(f"  [run] 失败输出尾部: {tail}")
            return False, ""
    except subprocess.TimeoutExpired:
        print(f"  [run] 超时 ({timeout}s)，跳过")
        return False, ""
    except Exception as e:
        print(f"  [run] 异常: {e}")
        return False, ""
    return True, ""


def find_latest_report_file(rep: str, code: str) -> Path | None:
    """在 reports/ 下找最新生成的 <code>_<rep>_*.txt。"""
    pattern = f"{code}_{rep}_*.txt"
    matches = sorted(REPORTS_DIR.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def parse_report_output(txt: str) -> dict:
    """解析报告输出文本 → {字段名: 值}（按 '名称: 值' 模式）。"""
    fields: dict[str, str] = {}
    for line in txt.splitlines():
        m = RUNTIME_VALUE_RE.match(line)
        if m:
            name = m.group(1).strip()
            val = m.group(2).strip()
            # 只收含数字/单位/列表的值，过滤纯标题行
            if re.search(r"[\d%亿万股元:：/.-]|、", val) and len(val) < 120:
                if name not in fields:
                    fields[name] = val
    return fields


def capture_runtime(version: str, reports: list[str], stocks: list[str], timeout: int) -> dict:
    """runtime 模式：实跑报告并解析输出。"""
    result: dict = {"meta": {}, "reports": {}}
    for rep in reports:
        result["reports"][rep] = {"stocks": {}, "data_calls": []}
        for code in stocks:
            ok, _ = run_report(rep, code, timeout)
            if not ok:
                result["reports"][rep]["stocks"][code] = {"status": "run_failed", "fields": {}}
                continue
            out_file = find_latest_report_file(rep, code)
            if out_file is None:
                result["reports"][rep]["stocks"][code] = {"status": "no_output", "fields": {}}
                continue
            txt = out_file.read_text(encoding="utf-8", errors="replace")
            fields = parse_report_output(txt)
            result["reports"][rep]["stocks"][code] = {
                "status": "ok",
                "output_file": str(out_file),
                "fields": fields,
            }
            print(f"  [ok] {rep}/{code}: {out_file.name} 提取字段={len(fields)}")
    return result


# ---------- main ----------

def main() -> int:
    ap = argparse.ArgumentParser(description="基线捕获（static 源码提取 / runtime 实跑提取）")
    ap.add_argument("--mode", choices=["static", "runtime"], required=True)
    ap.add_argument("--version", default="v15.4", help="版本标识，如 v9.6 / v15.4")
    ap.add_argument("--reports", default="sht,med,lng,ful", help="报告类型，逗号分隔")
    ap.add_argument("--stocks", default="000100", help="runtime 模式: 股票代码，逗号分隔")
    ap.add_argument("--out", default=str(DEFAULT_OUT), help="输出目录")
    ap.add_argument("--timeout", type=int, default=900, help="runtime 模式: 单报告超时秒数")
    args = ap.parse_args()

    reports = [r.strip() for r in args.reports.split(",") if r.strip()]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{args.version.replace('.', '_')}_{args.mode}_{ts}.json"
    out_path = out_dir / fname

    print(f"[capture_baseline] mode={args.mode} version={args.version} reports={reports}")
    t0 = time.time()

    if args.mode == "static":
        data = capture_static(args.version, reports)
    else:
        stocks = [s.strip() for s in args.stocks.split(",") if s.strip()]
        data = capture_runtime(args.version, reports, stocks, args.timeout)

    data["meta"] = {
        "version": args.version,
        "mode": args.mode,
        "captured_at": datetime.now().isoformat(timespec="seconds"),
        "stocks": [s.strip() for s in args.stocks.split(",") if s.strip()],
        "reports": reports,
        "elapsed_sec": round(time.time() - t0, 1),
    }

    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[capture_baseline] 完成，耗时 {data['meta']['elapsed_sec']}s → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

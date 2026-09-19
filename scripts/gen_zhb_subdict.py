#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_zhb_subdict.py — 生成 ZHB 镜像分字典 docs/verify/zhb_verify.md

设计契约（用户 2026-09-19 裁定）：
- 《主字典》field_dict.md §三 的 ZHB 三章（tdxstat / tdxstat2 / tipinfo）是**唯一权威源**。
- docs/verify/zhb_verify.md 是主字典 ZHB 章的**镜像备份**：逐字段复制主字典内容，
  不引入任何主字典之外的字段定名或状态判定，自身不持有独立决策权。
- 覆盖闸门 verify_sync_check.check_zhb_mirror_coverage 强制：
    zhb_verify.md 的 Col[N] 集合 == 主字典 ZHB 位置式契约表 Col[N] 集合
  （完全覆盖、不得越权发明字段）。
- 每次主字典 ZHB 章改动后，重跑本脚本即可使镜像回到 parity。

本模块 import-safe：verify_sync_check 直接 import 其中的
extract_main_zhb() / extract_subdict_zhb() 做覆盖比对，无需重新生成文件。
"""
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(_HERE)
MAIN = os.path.join(REPO, "docs", "field_dict.md")
OUT = os.path.join(REPO, "docs", "verify", "zhb_verify.md")

# (subsection header regex, source key, human title)
_SOURCES = [
    (r"^###\s*1\.\s*`tdxstat\.cfg`", "tdxstat", "tdxstat.cfg（个股综合统计快照）"),
    (r"^###\s*2\.\s*`tdxstat2\.cfg`", "tdxstat2", "tdxstat2.cfg（成交与资金流向表）"),
    (r"^###\s*3\.\s*`tipinfo\.dat`", "tipinfo", "tipinfo.dat（财报日历与业绩快照）"),
]

# positional row:  | **[N]** | ... |
_ROW_RE = re.compile(r"^\|\s*\*\*\[(\d+)\]\*\*\s*\|(.*)\|\s*$")
# contract table row inside §1.1 / §2.1 / §3.1:  | stat.xxx | ... |
_CONTRACT_RE = re.compile(r"^\|\s*(stat2?|tipinfo)\.(\w+)\s*\|(.*)\|\s*$")
# subsection header for standard contract tables §1.1 / §2.1 / §3.1
_CONTRACT_HDR_RE = re.compile(r"^\####\s*\d+\.1\s+(\S+?)\s+标准契约表")


def _zhb_section(md: str) -> str:
    """Return the text of §三 (ZHB) from the main dict."""
    m = re.search(r"^##\s*三、.*ZHB", md, re.M)
    if not m:
        raise RuntimeError("§三 ZHB section not found in main dict")
    rest = md[m.end():]
    nxt = re.search(r"^##\s", rest, re.M)
    end = nxt.start() if nxt else len(rest)
    return rest[:end]


def _subsection(sec: str, frag: str, boundary_re: str = r"^#{2,4}\s"):
    """Return the text of one ZHB source subsection, from its `### N.` header
    up to (but not including) the next header line matching `boundary_re`.

    - positional table: boundary = next `## `/`### `/`#### ` (default `^#{2,4}\\s`)
      so it stops just *before* the `#### N.1` contract table.
    - contract table: boundary = next `## `/`### ` (`^#{2,3}\\s`) so it *includes*
      the `#### N.1` contract table and stops at the next source.
    """
    hm = re.search(frag, sec, re.M)
    if not hm:
        return None
    lines = sec[hm.start():].splitlines()
    end = len(lines)
    for i, ln in enumerate(lines):
        if i == 0:
            continue  # the header itself
        if re.match(boundary_re, ln):
            end = i
            break
    return "\n".join(lines[:end])


def _positional_rows(sec: str, frag: str):
    """Return positional `**[N]**` table rows (raw line strings) for one source."""
    sub = _subsection(sec, frag, r"^#{2,4}\s")
    if sub is None:
        return []
    return [ln for ln in sub.splitlines() if _ROW_RE.match(ln)]


def _contract_rows(sec: str, frag: str):
    """Return standard-contract-table rows (`| stat.xxx | ... |`) for one source.

    The contract table lives in the `#### N.1` subsection that follows the
    positional table; we bound the block at the next `### ` (next source) so the
    `#### N.1` table is included, then scan for its header and capture the body.
    """
    sub = _subsection(sec, frag, r"^#{2,3}\s")
    if sub is None:
        return []
    rows = []
    capture = False
    for ln in sub.splitlines():
        if _CONTRACT_HDR_RE.match(ln):
            capture = True
            continue
        # each ZHB source has exactly one §N.1 contract table; once inside it,
        # every `stat.*` / `stat2.*` / `tipinfo.*` row belongs to the table.
        if capture and _CONTRACT_RE.match(ln):
            rows.append(ln)
    return rows


def extract_main_zhb(main_path: str = MAIN) -> dict:
    """{source_key: set(int cols)} from main dict positional tables (authority)."""
    md = open(main_path, encoding="utf-8").read()
    sec = _zhb_section(md)
    out = {}
    for frag, key, _ in _SOURCES:
        cols = set()
        for ln in _positional_rows(sec, frag):
            m = _ROW_RE.match(ln)
            if m:
                cols.add(int(m.group(1)))
        out[key] = cols
    return out


def extract_main_contract(main_path: str = MAIN) -> dict:
    """{source_key: set(token)} standard-contract tokens from main dict."""
    md = open(main_path, encoding="utf-8").read()
    sec = _zhb_section(md)
    out = {}
    for frag, key, _ in _SOURCES:
        toks = set()
        for ln in _contract_rows(sec, frag):
            m = _CONTRACT_RE.match(ln)
            if m:
                toks.add(f"{m.group(1)}.{m.group(2)}")
        out[key] = toks
    return out


def extract_subdict_zhb(subdict_path: str = OUT) -> dict:
    """{source_key: set(int cols)} from the generated mirror (must == main)."""
    if not os.path.exists(subdict_path):
        return {}
    text = open(subdict_path, encoding="utf-8").read()
    out = {}
    cur = None
    for ln in text.splitlines():
        hm = re.match(r"^#{2,3}\s+(tdxstat|tdxstat2|tipinfo)\b", ln)
        if hm:
            cur = hm.group(1)
            out.setdefault(cur, set())
            continue
        rm = _ROW_RE.match(ln)
        if rm and cur:
            out[cur].add(int(rm.group(1)))
    return out


def extract_subdict_contract(subdict_path: str = OUT) -> dict:
    """{source_key: set(token)} contract tokens parsed from the mirror file."""
    if not os.path.exists(subdict_path):
        return {}
    text = open(subdict_path, encoding="utf-8").read()
    out = {}
    cur = None
    capture = False
    for ln in text.splitlines():
        hm = re.match(r"^#{2,3}\s+(tdxstat|tdxstat2|tipinfo)\b", ln)
        if hm:
            cur = hm.group(1)
            out.setdefault(cur, set())
            capture = False
            continue
        if ln.startswith("### 附录") or "标准契约表" in ln:
            capture = True
            continue
        # each source has exactly one appendix contract table; once inside it,
        # collect every `stat.*`/`stat2.*`/`tipinfo.*` row until the next source.
        if capture and cur:
            m = _CONTRACT_RE.match(ln)
            if m:
                out[cur].add(f"{m.group(1)}.{m.group(2)}")
    return out


def build_mirror(main_path: str = MAIN) -> str:
    """Return the full markdown content of the mirror sub-dict."""
    md = open(main_path, encoding="utf-8").read()
    sec = _zhb_section(md)

    parts = []
    parts.append(
        "# ZHB 镜像分字典（zhb_verify.md）\n"
        "\n"
        "> **治理定位**：本文件是《主字典》`field_dict.md` §三 ZHB 三章的**镜像备份**。\n"
        "> - **主字典始终是唯一权威源**；本文件逐字段复制主字典内容，**不引入任何主字典之外"
        "的字段定名或状态判定**，自身不持有独立决策权。\n"
        "> - 由 `scripts/gen_zhb_subdict.py` 从主字典抽取生成；主字典 ZHB 章改动后须重跑该脚本。\n"
        "> - 覆盖闸门 `verify_sync_check.check_zhb_mirror_coverage` 强制本文件 Col[N] 集合"
        "与主字典逐字段一致（完全覆盖、不得越权发明字段）。\n"
        "> - 字段语义、层级（L1/L2/⚠️/❌）、单位、实测值均以主字典为准，争议以主字典现行条文裁决。\n"
    )
    parts.append(
        "## 覆盖范围\n\n"
        "| 源 | 主字典章节 | 位置式契约列数 | 标准契约 token 数 |\n"
        "|---|---|---|---|"
    )

    for frag, key, title in _SOURCES:
        pos = _positional_rows(sec, frag)
        con = _contract_rows(sec, frag)
        parts.append(f"| {key} | §三 {title} | {len(pos)} | {len(con)} |")

    parts.append("")

    for frag, key, title in _SOURCES:
        pos = _positional_rows(sec, frag)
        con = _contract_rows(sec, frag)
        parts.append(f"## {key}（镜像自 §三 {title}）\n")
        parts.append(
            "> 下表逐行复制主字典位置式 `**[N]**` 契约表，列定义与主字典完全一致："
            "索引 / 代码变量名 / 字段含义 / 核实状态 / 数据格式 / 实测值 / 策略价值。\n"
        )
        # reconstruct a markdown table header matching the main dict's positional table
        parts.append(
            "| 索引 | 代码变量名 | 字段含义 | 核实状态 | 数据格式 | 实测值 | 策略价值 |\n"
            "|---|---|---|---|---|---|---|"
        )
        parts.extend(pos)
        parts.append("")

        if con:
            parts.append(f"### 附录：{key} 标准契约表（镜像自 §三 对应标准契约表）\n")
            parts.append("| 字段 | 含义 | 单位 | 状态 |\n|---|---|---|---|")
            parts.extend(con)
            parts.append("")

    return "\n".join(parts) + "\n"


def main():
    content = build_mirror()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(content)
    main_cols = extract_main_zhb()
    sub_cols = extract_subdict_zhb(OUT)
    print(f"wrote {OUT}")
    for k in sorted(set(main_cols) | set(sub_cols)):
        mc, sc = main_cols.get(k, set()), sub_cols.get(k, set())
        flag = "OK" if mc == sc else f"MISMATCH main={len(mc)} sub={len(sc)}"
        print(f"  {k}: main_cols={len(mc)} sub_cols={len(sc)} [{flag}]")
    if main_cols != sub_cols:
        print("ERROR: parity mismatch after generation", file=sys.stderr)
        sys.exit(1)
    print("parity OK")


if __name__ == "__main__":
    main()

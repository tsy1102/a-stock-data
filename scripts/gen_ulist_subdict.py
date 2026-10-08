#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_ulist_subdict.py — 生成 ulist239 镜像分字典 docs/verify/ulist_verify.md

设计契约（用户 2026-09-19 裁定，与 ZHB 镜像同源同构）：
- 《主字典》field_dict.md §12.3.2.3 登记 239 个实际返回字段；另保留未返回的 f93
- 编号空位，因此表格有 240 行。协议索引从 `docs/field_source_reference.md` 的历史章节读取。
- docs/verify/ulist_verify.md 镜像 fN 与列索引，便于按字段核查；不承载逐源字段状态。
- 覆盖闸门 verify_sync_check.check_ulist_mirror_coverage 强制：
    ulist_verify.md 的 fN 集合 == 主字典 §12.3.2.3 fN 集合
  （精确集合相等、完全覆盖、不得越权发明字段；实际字段数与文档占位数分别统计）。
- 每次主字典 ulist239 章改动后，重跑本脚本即可使镜像回到 parity。

本模块 import-safe：verify_sync_check 直接 import 其中的
extract_main_ulist() / extract_subdict_ulist() 做覆盖比对，无需重新生成文件。
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(_HERE)
MAIN = os.path.join(REPO, "docs", "field_source_reference.md")
OUT = os.path.join(REPO, "docs", "verify", "ulist_verify.md")

# ulist239 章节锚点（匹配整行标题，含末尾（np/get ...）副标题，避免残留到 preface）
_SECTION_RE = re.compile(r"^####\s*12\.3\.2\.3\s+ulist239\s+全字段清单.*$", re.M)
# 字段行:  | fN | 状态 | 备注 |
_ROW_RE = re.compile(r"^\|\s*f(\d+)\s*\|(.*)\|\s*$")
# 表头行:  | fN | 状态 | 备注 |
_TABLE_HDR_RE = re.compile(r"^\|\s*fN\s*\|", re.I)
# 分隔行:  | :--: | :--- | :--- |
_SEP_RE = re.compile(r"^\|[\s:|-]+\|$")


def _ulist_section(md: str) -> str:
    """Return the text of §12.3.2.3 (ulist239) from the main dict."""
    m = _SECTION_RE.search(md)
    if not m:
        raise RuntimeError("§12.3.2.3 ulist239 section not found in main dict")
    rest = md[m.end() :]
    nxt = re.search(r"^#{2,4}\s", rest, re.M)
    end = nxt.start() if nxt else len(rest)
    return rest[:end]


def _table_block(sec: str):
    """Return (preface_lines, table_rows) for the ulist239 field table.

    - preface_lines: blockquote/other lines before the `| fN |` table header.
    - table_rows: the verbatim `| fN | 状态 | 备注 |` rows (excludes the header
      and separator lines). Collected until a non-field-row line.
    """
    lines = sec.splitlines()
    # find table header index
    hdr_idx = None
    for i, ln in enumerate(lines):
        if _TABLE_HDR_RE.match(ln):
            hdr_idx = i
            break
    if hdr_idx is None:
        return lines, []

    # strip leading/trailing blank lines from preface for clean rendering
    preface = lines[:hdr_idx]
    while preface and not preface[0].strip():
        preface = preface[1:]
    while preface and not preface[-1].strip():
        preface = preface[:-1]
    # skip header + separator
    j = hdr_idx + 1
    if j < len(lines) and _SEP_RE.match(lines[j]):
        j += 1
    rows = []
    for ln in lines[j:]:
        if _ROW_RE.match(ln):
            rows.append(ln)
        else:
            break
    return preface, rows


def _trailing_block(sec: str):
    """Return blockquote lines after the field table (statistics summary etc.)."""
    lines = sec.splitlines()
    hdr_idx = None
    for i, ln in enumerate(lines):
        if _TABLE_HDR_RE.match(ln):
            hdr_idx = i
            break
    if hdr_idx is None:
        return []
    # skip to end of field rows
    j = hdr_idx + 1
    if j < len(lines) and _SEP_RE.match(lines[j]):
        j += 1
    while j < len(lines) and _ROW_RE.match(lines[j]):
        j += 1
    tail = lines[j:]
    # keep only blockquote lines (drop blank separators); strip surrounding blanks
    blk = [ln for ln in tail if ln.lstrip().startswith(">")]
    while blk and not blk[0].strip():
        blk = blk[1:]
    while blk and not blk[-1].strip():
        blk = blk[:-1]
    return blk


def extract_main_ulist_details(main_path: str = MAIN) -> tuple[set[int], set[int]]:
    """Return (documented fN rows, explicitly marked non-returned placeholders)."""
    md = open(main_path, encoding="utf-8").read()
    sec = _ulist_section(md)
    _, rows = _table_block(sec)
    fields = set()
    placeholders = set()
    for ln in rows:
        m = _ROW_RE.match(ln)
        if m:
            field_number = int(m.group(1))
            fields.add(field_number)
            if "恒空占位" in ln or "未返回的编号空位" in ln:
                placeholders.add(field_number)
    return fields, placeholders


def extract_main_ulist(main_path: str = MAIN) -> set[int]:
    """Return every documented fN row, including placeholders, for mirror parity."""
    fields, _ = extract_main_ulist_details(main_path)
    return fields


def extract_subdict_ulist(subdict_path: str = OUT) -> set:
    """{int fN} parsed from the generated mirror (must == main)."""
    if not os.path.exists(subdict_path):
        return set()
    text = open(subdict_path, encoding="utf-8").read()
    # only the field table region (between `| fN |` header and the next non-row)
    lines = text.splitlines()
    hdr_idx = None
    for i, ln in enumerate(lines):
        if _TABLE_HDR_RE.match(ln):
            hdr_idx = i
            break
    if hdr_idx is None:
        return set()
    j = hdr_idx + 1
    if j < len(lines) and _SEP_RE.match(lines[j]):
        j += 1
    out = set()
    for ln in lines[j:]:
        match = _ROW_RE.match(ln)
        if match:
            out.add(int(match.group(1)))
        else:
            break
    return out


def build_mirror(main_path: str = MAIN) -> str:
    """Return the full markdown content of the ulist239 mirror sub-dict."""
    md = open(main_path, encoding="utf-8").read()
    sec = _ulist_section(md)
    preface, rows = _table_block(sec)
    trailing = _trailing_block(sec)

    parts = []
    parts.append(
        "# ulist239 镜像分字典（ulist_verify.md）\n"
        "\n"
        "> **治理定位**：本文件镜像 `field_source_reference.md` 中的 ulist239 字段与列索引。\n"
        "> - 当前逐源字段状态以 `field_verification/field_registry.json` 为准；本文件只便于按字段核查。\n"
        "> - 由 `scripts/gen_ulist_subdict.py` 从历史参考文档抽取生成；源协议章节变动后须重跑。\n"
        "> - 覆盖闸门 `verify_sync_check.check_ulist_mirror_coverage` 强制本文件 fN 集合"
        "与主字典逐字段一致（精确集合相等、完全覆盖、不得越权发明字段）。\n"
        "> - 字段语义、层级（✅/⚠️/❌）、单位、实测值均以主字典为准，争议以主字典现行条文裁决。\n"
    )

    # 前置治理 blockquote（主字典原样，已含 ulist239 索引≠push2 索引等约束）
    if preface:
        parts.append("\n".join(preface))
        parts.append("")

    # 字段表（逐行复制主字典，列定义完全一致：fN / 状态 / 备注）
    parts.append("## ulist239 全字段清单（镜像自 §12.3.2.3）\n")
    parts.append("> 下表逐行复制主字典 `**| fN | 状态 | 备注 |**` 契约表，列定义与主字典完全一致。")
    parts.append("")
    parts.append("| fN | 状态 | 备注 |")
    parts.append("| :--: | :--- | :--- |")
    parts.extend(rows)
    parts.append("")

    # 尾部统计 blockquote
    if trailing:
        parts.append("\n".join(trailing))
        parts.append("")

    return "\n".join(parts) + "\n"


def main():
    content = build_mirror()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(content)
    main_fns, placeholders = extract_main_ulist_details()
    sub_fns = extract_subdict_ulist(OUT)
    print(f"wrote {OUT}")
    actual_count = len(main_fns - placeholders)
    print(
        f"  main ulist239 rows: {len(main_fns)} "
        f"({actual_count} returned fields; placeholders={sorted(placeholders)}) "
        f"(min={min(main_fns)} max={max(main_fns)})"
    )
    print(f"  sub  ulist239 documented rows: {len(sub_fns)}")
    miss = sorted(main_fns - sub_fns)
    extra = sorted(sub_fns - main_fns)
    if miss:
        print(f"  ✗ 缺失 {len(miss)} 个: {miss[:20]}")
    if extra:
        print(f"  ✗ 越权 {len(extra)} 个: {extra[:20]}")
    if main_fns == sub_fns:
        print("parity OK")
    else:
        print("ERROR: parity mismatch after generation", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

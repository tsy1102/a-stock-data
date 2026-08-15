# -*- coding: utf-8 -*-
"""md_render.py — 报告文本→Markdown 排版转换器(V17.0 2026-08-15 C 方案).

原则(用户指示): 不拘泥 txt 原排版——根据数据与字段格式重新合理排版, 以阅读效果为准。
转换规则:
  1. 章节标题 【...】→ ## 标题
  2. 分隔线 ─/=/− 连续 → ---
  3. F10 边框表格(┌─┬─┐/│)→ md 表格(按 │ 切列)
  4. 空格对齐表 → 数据驱动切分: 每数据行按自身 ≥2 空格间隙切分(列数=表头列数),
     表头仅取列名——不再依赖 txt 表头边界(解决表头列宽≠数据列宽错位)
  5. 无法可靠切分 → 原样保留(纯文本, 不产生错误数据)
"""
from __future__ import annotations

import re
from typing import List

_BORDER_OPEN = re.compile(r"^\s*[┌├└]")
_BORDER_ROW = re.compile(r"^\s*│")
_LINE_ONLY = re.compile(r"^\s*[─=\-]{8,}\s*$")
_HEADING = re.compile(r"^\s*【[^】]{1,40}】")
_HEADING_BRACKET = re.compile(r"^\s*\[\d{1,2}[^\]]{1,30}\]\s*$")  # val 格式: [01 龙回头]
_SPACE_TABLE_HEADER = re.compile(r"^\s*[^\s│┌]")
_SPACE_TABLE_SEP = re.compile(r"^\s*[─\-]{4,}(\s*[─\-]{4,})*\s*$")
_SPLITTER = re.compile(r"[│｜|]")
_BORDER_DECOR = re.compile(r"^[─┬┴┼├┌└┤┐┘\s]+$")


def _split_by_sep(r: str) -> List[str]:
    return [p.strip() for p in _SPLITTER.split(r) if p.strip()]


def _split_by_row_gaps(r: str, max_cols: int) -> List[str]:
    """数据驱动切分: 按该行自身 ≥2 空格间隙切分(列数上限 max_cols).

    间隙取"最大间隙集合"——为稳定, 按间隙宽度降序取 max_cols-1 个(合并窄间隙)。
    """
    r = r.strip()
    if not r:
        return []
    gaps = [(m.start(), m.end()) for m in re.finditer(r" {2,}", r)]
    if not gaps:
        return [r]
    # 按宽度降序取 max_cols-1 个边界(窄间隙=列间分隔, 宽间隙=列宽补齐, 取宽的更稳)
    gaps.sort(key=lambda g: -(g[1] - g[0]))
    bounds = sorted([0] + [g[0] for g in gaps[: max_cols - 1]] + [len(r)])
    cells = [r[bounds[k]:bounds[k + 1]].strip() for k in range(len(bounds) - 1)]
    return [c for c in cells if c != ""]


def _border_rows_to_md(rows: List[str]) -> List[str]:
    out: List[str] = []
    cells: List[List[str]] = []
    for r in rows:
        if _BORDER_DECOR.match(r):
            continue
        parts = _split_by_sep(r)
        if parts:
            cells.append(parts)
    if not cells:
        return out
    ncol = max(len(c) for c in cells)
    head = cells[0]
    out.append("| " + " | ".join(head) + " |")
    out.append("|" + "---|" * ncol)
    for c in cells[1:]:
        c = (c + [""] * ncol)[:ncol]
        out.append("| " + " | ".join(c) + " |")
    return out


def _space_table_to_md(block: List[str]) -> List[str]:
    """数据驱动空格表转换: 表头取列名(按自身间隙), 数据行按自身间隙切分.

    校验: 数据行列数 ≥ 表头列数-1 且 ≥2 列才成表; 否则原样保留。
    """
    data_rows = [r for r in block[1:] if not _SPACE_TABLE_SEP.match(r)]
    if len(data_rows) < 1:
        return block
    # 表头列名: 按表头自身间隙切分
    header = block[0].strip()
    hdr_cells = _split_by_row_gaps(header, 8)
    # 列数参考: 数据行间隙数众数
    from collections import Counter

    n_gaps = Counter(len(_split_by_row_gaps(r, 16)) for r in data_rows)
    if not n_gaps:
        return block
    cols = n_gaps.most_common(1)[0][0]
    if cols < 2:
        return block
    # 表头列名与列数对齐: 不足补空, 超出截断
    head = (hdr_cells + [""] * cols)[:cols]
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * cols]
    for r in data_rows:
        cells = _split_by_row_gaps(r, cols)
        if not cells:
            continue
        if len(cells) < cols - 1:
            return block  # 某行明显少列 → 非表格, 原样
        cells = (cells + [""] * cols)[:cols]
        out.append("| " + " | ".join(cells) + " |")
    return out


def text_to_md(lines: List[str]) -> List[str]:
    out: List[str] = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        if _LINE_ONLY.match(ln):
            out.append("---")
            i += 1
            continue
        if _HEADING.match(ln) or _HEADING_BRACKET.match(ln):
            out.append("## " + ln.strip())
            i += 1
            continue
        if _BORDER_OPEN.match(ln):
            block = []
            j = i
            while j < n and (_BORDER_OPEN.match(lines[j]) or _BORDER_ROW.match(lines[j])):
                block.append(lines[j])
                j += 1
            out.extend(_border_rows_to_md(block))
            i = j
            continue
        if _SPACE_TABLE_HEADER.match(ln) and i + 1 < n and _SPACE_TABLE_SEP.match(lines[i + 1]):
            block = []
            j = i
            while j < n and lines[j].strip() and not _HEADING.match(lines[j]) \
                    and not _BORDER_OPEN.match(lines[j]):
                block.append(lines[j])
                j += 1
            out.extend(_space_table_to_md(block))
            i = j
            continue
        out.append(ln)
        i += 1
    return out


def render_md_report(path_md: str, lines: List[str]) -> str:
    md_lines = text_to_md([ln for ln in lines if ln])
    output = "\n".join(md_lines)
    with open(path_md, "w", encoding="utf-8") as _f:
        _f.write(output)
    return output

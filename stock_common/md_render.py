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
_SECTION_SEP = re.compile(r"^\s*[─=]{8,}\s*$")  # V17.0.2: 全角长线=章节分隔(表格块收集时挡); 半角 - 短横=表内分隔线(允许进块)
_HEADING = re.compile(r"^\s*【[^】]{1,40}】")
_HEADING_BRACKET = re.compile(r"^\s*\[\d{1,2}[^\]]{1,30}\]\s*$")  # val 格式: [01 龙回头]
_SPACE_TABLE_HEADER = re.compile(r"^\s*[^\s│┌]")
_SPACE_TABLE_SEP = re.compile(r"^\s*[─\-]{4,}(\s*[─\-]{4,})*\s*$")
_SPLITTER = re.compile(r"[│｜|]")
_BORDER_DECOR = re.compile(r"^[─┬┴┼├┌└┤┐┘\s]+$")
# V17.0.2c: "字段: 值"对齐块推断(用户: md 折叠空格, 竖排对齐失效 → 对齐即表格)
# 单字段值行: 字段名(1-14 字符, 无冒号) + 冒号 + ≥1 空格 + 值(值不含管道)
# V17.0.2e: 排除行首 emoji/状态符号(✅⚡📊📋⏱ 等日志状态行不转表——用户: 无用 |---|---|)
_FIELD_VAL = re.compile(r"^ {0,4}\S[^:：]{1,14}[:：]\s{1,}\S[^|]*$")
_EMOJI_LEAD = re.compile(r"^ {0,4}(?:[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]|[✅⚡📊📋⏱⚠️📌💰🚀🔥📐📈📉💎🟢🟡🔴])")


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


def _space_table_to_md(block: List[str]) -> "tuple[list, list]":
    """数据驱动空格表转换: 表头取列名(按自身间隙), 数据行按自身间隙切分.

    V17.0.2(2026-08-16): 返回 (md_rows, rest)——数据行中段数不足的"信号/统计"文本行
    从失败行起截断为 rest, 不参与表格(原整块回退导致股东户数/资金流/两融表全部不转)。
    返回: (表格 md 行, 剩余普通行(可空))；无法成表时返回 (原 block, [])。
    """
    data_rows = [r for r in block[1:] if not _SPACE_TABLE_SEP.match(r)]
    if len(data_rows) < 1:
        return block, []
    # 表头列名: 按表头自身间隙切分
    header = block[0].strip()
    hdr_cells = _split_by_row_gaps(header, 8)
    # 列数参考: 数据行间隙数众数
    from collections import Counter

    n_gaps = Counter(len(_split_by_row_gaps(r, 16)) for r in data_rows)
    if not n_gaps:
        return block, []
    cols = n_gaps.most_common(1)[0][0]
    if cols < 2:
        return block, []
    # 表头列名与列数对齐: 不足补空, 超出截断
    head = (hdr_cells + [""] * cols)[:cols]
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * cols]
    for idx, r in enumerate(data_rows):
        cells = _split_by_row_gaps(r, cols)
        if len(cells) >= cols - 1:
            cells = (cells + [""] * cols)[:cols]
            out.append("| " + " | ".join(cells) + " |")
        else:
            # 段数不足 → 该行及之后非表格(信号/统计文本), 截断为 rest
            if len(out) <= 2:  # 连一行有效数据都没有 → 整块非表格
                return block, []
            return out, data_rows[idx:]
    return out, []


def _fieldval_block_to_md(block: List[str]) -> List[str]:
    """V17.0.2c: "字段: 值"对齐块 → md 2 列表格.

    推断规则(用户引导: 对齐如何推断表格): 连续 ≥3 行"字段: 值" → 转 | 字段 | 值 | 表;
    行内多字段("今开: 205.00 元  昨收: 204.33 元")按 2+ 空格 + 短字段 + 冒号拆分各成一行;
    不足 3 行 → 原样(竖排保留)。
    """
    rows: List[str] = []
    for r in block:
        m = _FIELD_VAL.match(r)
        if not m:
            return block
        field, _, rest = r.partition(":")
        rest = rest.strip()
        if not rest:
            return block
        # 行内多字段拆分: 2+ 空格 + 字段名(1-12) + 冒号 + 空格
        parts = re.split(r" {2,}(?=\S[^:：]{1,12}[:：] )", rest)
        segs = [(field.strip(), parts[0].strip())]
        for p in parts[1:]:
            p = p.strip()
            if not p:
                continue
            f2, _, v2 = p.partition(":")
            segs.append((f2.strip(), v2.strip()))
        rows.extend("| " + f + " | " + v + " |" for f, v in segs if v)
    if len(rows) < 3:
        return block
    return [rows[0], "|---|---|"] + rows[1:]


def text_to_md(lines: List[str]) -> List[str]:
    out: List[str] = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        # V17.0.2e: 独立分隔线(--- 或长线)丢弃——md 标题字体/加粗已够区分, 用户要求去除
        if _LINE_ONLY.match(ln) or ln.strip() == "---":
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
        # V17.0.2c: "字段: 值"对齐块 → 2 列表格(章节一/三基本信息与预期)
        if _FIELD_VAL.match(ln) and not _EMOJI_LEAD.match(ln):
            block = []
            j = i
            while j < n and lines[j].strip() and _FIELD_VAL.match(lines[j]) \
                    and not _HEADING.match(lines[j]) and not _SECTION_SEP.match(lines[j]) \
                    and not lines[j].lstrip().startswith("## "):
                block.append(lines[j])
                j += 1
            if len(block) >= 3:
                out.extend(_fieldval_block_to_md(block))
                if out and out[-1].startswith("| "):
                    out.append("")
                i = j
                continue
            # 不足 3 行 → 逐行走普通行清理
            out.append(_clean_text_line(ln))
            i += 1
            continue
        if _SPACE_TABLE_HEADER.match(ln) and i + 1 < n and _SPACE_TABLE_SEP.match(lines[i + 1]):
            # V17.0.1 修复(2026-08-16): 表头间隙预检——表头行须有 ≥2 个连续空格(≥3 列)才可能是表格;
            # 报告标题行(如 "A 股策略发现报告  [时间]")恰有 1 个 2+ 空格间隙, 误判会吞掉后续全部行
            _hdr_gaps = len(re.findall(r" {2,}", ln.lstrip()))
            if _hdr_gaps < 2:
                out.append(ln)  # 非表格: 原样输出, 后续分隔线/标题继续正常处理
                i += 1
                continue
            block = []
            j = i
            # V17.0.2: 章节分隔(全角 ─ 长线)不收集进表格块; 半角 - 表内分隔线允许进块
            # V17.0.2b: 脚本直接输出 md 后, 块边界还需终止: ## 标题行(带前缀)与 ---(3 短横装饰)
            while j < n and lines[j].strip() and not _HEADING.match(lines[j]) \
                    and not _BORDER_OPEN.match(lines[j]) and not _SECTION_SEP.match(lines[j]) \
                    and not lines[j].lstrip().startswith("## ") \
                    and lines[j].strip() != "---":
                block.append(lines[j])
                j += 1
            tbl_rows, rest = _space_table_to_md(block)
            out.extend(tbl_rows)
            if rest:
                i = j - len(rest)  # 尾部非表格行交回主循环(去缩进/继续处理)
                continue
            if out and not out[-1].startswith("| ") and out[-1] != "":
                out.append("")  # B 修复: 表格块后补空行, 防与下一标题粘连
            elif out and out[-1].startswith("| "):
                out.append("")
            i = j
            continue
        # C/D/E 修复: 行首缩进去除 + ──装饰行 → ### + #N 编号 → **#N**(防被当标题)
        _cleaned = _clean_text_line(ln)
        out.append(_cleaned)
        i += 1
    return out


_DECO_LINE = re.compile(r"^\s*[─\-=]+\s*(.*?)\s*[─\-=]+\s*$")
_HASH_NUM = re.compile(r"^\s*#(\d{1,3})\s+")


def _clean_text_line(ln: str) -> str:
    """V17.0.1b(2026-08-16 排版优化): 普通行清理——去行首缩进/─装饰行转小节标题/#N 编号粗体/冒号对齐空格."""
    # D: ── 装饰小节行 → ### 小节标题(如 "── 游资活跃度诊断 ──")
    m = _DECO_LINE.match(ln)
    if m and m.group(1).strip():
        return "### " + m.group(1).strip()
    # E: #N 编号行 → **#N**(防 md 把 #1 当 h1 标题)
    m2 = _HASH_NUM.match(ln)
    if m2:
        return "  **#" + m2.group(1) + "** " + ln[m2.end():].strip()
    # C: 去行首 1-4 空格缩进(保留列表语义行如 "  - "/"  1. ")
    stripped = ln.lstrip()
    if stripped.startswith(("- ", "* ", "1. ", "2. ", "> ")):
        return ln.rstrip()
    if len(ln) - len(stripped) <= 4:
        ln = stripped
    # 冒号对齐空格 → 单空格
    ln = re.sub(r":\s{3,}", ": ", ln)
    return ln.rstrip()


def render_md_report(path_md: str, lines: List[str]) -> str:
    # V17.0.2b: 不过滤空行——空行是表格块收集的边界(过滤后块越过 ---/下一标题 → 列数污染 → 0 表格)
    md_lines = text_to_md(lines)
    output = "\n".join(md_lines)
    with open(path_md, "w", encoding="utf-8") as _f:
        _f.write(output)
    return output

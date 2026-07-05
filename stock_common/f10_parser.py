#!/usr/bin/env python3
"""f10_parser.py — F10 文本表格解析器 (V9.1)

解析通达信 F10 的纯文本表格格式（GBK 编码，ASCII 制表符绘制表格）。
支持：
  - 按 【N.标题】 分割子栏目
  - 解析 ┌┬┐├┼┤└┴┘─│ 格式的表格
  - 解析 ───── 分隔的段落块（公告/报道格式）

V9.1 新增函数：
  - _normalize_pipes: 全角/半角竖线归一化（｜→│）
  - find_subsection: 按关键字定位子栏目
  - parse_tables: 批量解析所有表格
  - merge_continuation_lines: 合并跨行续行
  - transpose_table: 表格转置（横向表头→纵向）
  - parse_text_table: 解析纯文本表格
  - 修复 parse_table 重复行 bug
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# 表格装饰字符
_TABLE_BORDER_CHARS = set('┌┬┐├┼┤└┴┘─│━┃｜')


def _normalize_pipes(text: str) -> str:
    """将全角竖线 ｜ (U+FF5C) 归一化为半角 │ (U+2502)。

    F10 不同数据源（港澳资讯 vs 通达信）使用不同的竖线字符绘制表格：
    - 600519 等使用 │ (U+2502, box drawing vertical)
    - 000001 等银行股（港澳资讯源）使用 ｜ (U+FF5C, fullwidth vertical bar)
    归一化后解析逻辑只需处理一种字符。
    """
    if not text:
        return text
    return text.replace('｜', '│')


def split_sections(content: str) -> Dict[str, str]:
    """按 【N.标题】 分割 F10 内容为子栏目。

    Args:
        content: F10 分类的完整文本内容

    Returns:
        dict: {栏目标题: 栏目文本}，标题不含【】和序号
    """
    if not content:
        return {}
    # 匹配 【1.最新提示】 【2.互动问答】 等格式
    pattern = re.compile(r'【(\d+)\.(.+?)】')
    matches = list(pattern.finditer(content))
    if not matches:
        return {}

    sections: Dict[str, str] = {}
    for i, m in enumerate(matches):
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        sections[title] = content[start:end].strip()
    return sections


def find_subsection(sections: Dict[str, str], name: str,
                    aliases: Optional[List[str]] = None) -> str:
    """从 split_sections 结果中查找子栏目，支持嵌套结构（银行股等）。

    F10 内容有两种结构：
    - 平铺式（如 600519）：所有子栏目都是 【N.标题】 格式，split_sections 直接返回
    - 嵌套式（如 000001 银行股）：顶层是 【1.财务指标】，子栏目 【主要财务指标】 无序号

    本函数先在顶层查找 name，若未找到，则在各 section 内容中搜索 【name】 子栏目。

    Args:
        sections: split_sections 的返回值
        name: 子栏目名称（如 '主要财务指标'）
        aliases: 可选的别名列表（如银行股用 '发展能力指标' 替代 '成长能力指标'）

    Returns:
        str: 子栏目文本内容，未找到返回空字符串
    """
    # 候选名称列表
    candidates = [name] + (aliases or [])

    # 1. 顶层查找
    for candidate in candidates:
        if candidate in sections:
            return sections[candidate]

    # 2. 嵌套查找：在各 section 内容中搜索 【candidate】
    for candidate in candidates:
        marker = '【' + candidate + '】'
        for section_content in sections.values():
            idx = section_content.find(marker)
            if idx < 0:
                continue
            start = idx + len(marker)
            # 找下一个 【...】 标记作为结束
            next_match = re.search(r'【[^】]+】', section_content[start:])
            if next_match:
                end = start + next_match.start()
                return section_content[start:end].strip()
            else:
                return section_content[start:].strip()
    return ''


def _is_border_line(line: str) -> bool:
    """判断是否为表格边框线（仅含 ┌┬┐├┼┤└┴┘─ 等字符和空格）。"""
    if not line:
        return False
    stripped = line.strip()
    if not stripped:
        return False
    return all(c in _TABLE_BORDER_CHARS or c == ' ' for c in stripped)


def parse_table(text: str) -> List[Dict[str, str]]:
    """解析 F10 表格格式文本，返回字典列表。

    自动识别表头（第一个 ┌ 开头的行），跳过分隔线，合并跨行字段。

    Args:
        text: 包含表格的文本

    Returns:
        list[dict]: 每行一个字典，key 为表头列名
    """
    if not text:
        return []

    # 归一化全角竖线 ｜ → 半角 │（港澳资讯源使用全角）
    text = _normalize_pipes(text)
    lines = text.split('\n')
    # 找到表头行（┌ 开头）
    table_start = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('┌'):
            table_start = i
            break

    if table_start < 0:
        return []

    # 找列名行（│ 分隔的行，紧接在 ┌ 行之后）
    col_names: List[str] = []
    col_name_line_idx = table_start + 1
    while col_name_line_idx < len(lines):
        line = lines[col_name_line_idx].strip()
        if line.startswith('│'):
            col_names = [p.strip() for p in line.strip('│').split('│')]
            break
        elif _is_border_line(line):
            col_name_line_idx += 1
            continue
        else:
            break

    if not col_names:
        return []

    num_cols = len(col_names)

    # 收集数据行
    rows: List[Dict[str, str]] = []
    current_row: Optional[List[str]] = None

    for i in range(col_name_line_idx + 1, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
        if line.startswith('└'):
            # 表格结束
            if current_row is not None and len(current_row) == num_cols:
                rows.append(dict(zip(col_names, current_row)))
                current_row = None  # 防止循环后再次追加
            break
        if _is_border_line(line):
            # 分隔线，当前行结束
            if current_row is not None and len(current_row) == num_cols:
                rows.append(dict(zip(col_names, current_row)))
            current_row = None
            continue
        if line.startswith('│'):
            # 数据行
            parts = [p.strip() for p in line.strip('│').split('│')]
            if len(parts) == num_cols:
                # 完整新行 — 先保存上一行
                if current_row is not None:
                    rows.append(dict(zip(col_names, current_row)))
                current_row = parts
            elif current_row is not None and len(parts) < num_cols:
                # 跨行字段：合并到上一行对应位置
                for j, p in enumerate(parts):
                    if j < len(current_row) and p:
                        if current_row[j] == '---' or current_row[j] == '':
                            current_row[j] = p
                        elif p != '---':
                            current_row[j] = (current_row[j] + p).strip()
            continue
        else:
            # 非表格行，表格可能已结束
            if current_row is not None:
                rows.append(dict(zip(col_names, current_row)))
                current_row = None
            break

    # 处理最后一行（如果没有 └ 结束符）
    if current_row is not None and len(current_row) == len(col_names):
        rows.append(dict(zip(col_names, current_row)))

    return rows


def parse_paragraph_blocks(text: str) -> List[Dict[str, str]]:
    """解析用 ───── 分隔的段落块（公告/报道格式）。

    格式：
    ─────────┬───────────────────
      2026-06-21 15:31│标题
    ─────────┴───────────────────
        摘要内容
    http://链接

    Args:
        text: 包含段落块的文本

    Returns:
        list[dict]: 每块一个字典，含 date/title/summary/url
    """
    if not text:
        return []

    results: List[Dict[str, str]] = []
    lines = text.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # 查找日期时间行（YYYY-MM-DD HH:MM）
        m = re.match(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})[│|]?\s*(.+)', line)
        if m:
            date = f"{m.group(1)} {m.group(2)}"
            title = m.group(3).strip()
            # 收集后续摘要和链接
            summary_parts: List[str] = []
            url = ''
            for j in range(i + 1, min(i + 20, len(lines))):
                next_line = lines[j].strip()
                if not next_line:
                    continue
                # 检查是否是下一个条目的开始
                if re.match(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}', next_line):
                    break
                if next_line.startswith('─'):
                    break
                if next_line.startswith('【'):
                    break
                # 检查 URL
                url_match = re.search(r'https?://\S+', next_line)
                if url_match:
                    url = url_match.group(0)
                    # URL 前面可能有摘要
                    before_url = next_line[:url_match.start()].strip()
                    if before_url:
                        summary_parts.append(before_url)
                else:
                    summary_parts.append(next_line)

            summary = ' '.join(summary_parts)[:300] if summary_parts else ''
            results.append({
                "date": date,
                "title": title[:120],
                "summary": summary,
                "url": url
            })
            i = j
        else:
            i += 1

    return results


def extract_field(text: str, pattern: str) -> Optional[str]:
    """从文本中提取匹配正则的第一个字段值。

    Args:
        text: 待搜索文本
        pattern: 正则表达式（含一个捕获组）

    Returns:
        str: 匹配值，未找到返回 None
    """
    m = re.search(pattern, text)
    if m:
        return m.group(1).strip()
    return None


def parse_key_value_table(text: str) -> Dict[str, str]:
    """解析键值对表格（如风险提示中的违规稽查）。

    格式：
    ┌────────┬───────────┬────────┬───────────┐
    │立案日期        │2026-03-13  │处罚披露日      │---       │
    ├────────┼───────────┼────────┼───────────┤
    │立案类型        │董监高违法违规│案情进展        │被留置调查  │
    ├────────┼───────────┴────────┴───────────┤
    │违法事实        │---                                   │
    ├────────┼────────────────────────────────┤
    │收件决定        │---                                   │
    └────────┴────────────────────────────────┘

    Args:
        text: 包含键值对表格的文本

    Returns:
        dict: {键: 值}
    """
    result: Dict[str, str] = {}
    if not text:
        return result

    # 归一化全角竖线 ｜ → 半角 │
    text = _normalize_pipes(text)
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line.startswith('│'):
            continue
        if _is_border_line(line):
            continue
        # 用 │ 分割
        parts = [p.strip() for p in line.strip('│').split('│')]
        # 键值交替：键1 值1 键2 值2 ...
        i = 0
        while i + 1 < len(parts):
            key = parts[i].strip()
            value = parts[i + 1].strip()
            if key and key != '---':
                result[key] = value if value else '---'
            i += 2

    return result


def parse_tables(text: str) -> List[List[Dict[str, str]]]:
    """解析文本中的所有表格（多个 ┌...└ 块）。

    Args:
        text: 包含多个表格的文本

    Returns:
        list[list[dict]]: 每个表格一个列表，每个列表含多行字典
    """
    if not text:
        return []
    tables: List[List[Dict[str, str]]] = []
    remaining = text
    while True:
        rows = parse_table(remaining)
        if not rows:
            break
        tables.append(rows)
        # 找到第一个 └ 行的位置，从其后继续
        end_idx = remaining.find('└')
        if end_idx < 0:
            break
        newline_after = remaining.find('\n', end_idx)
        if newline_after < 0:
            break
        remaining = remaining[newline_after + 1:]
    return tables


def merge_continuation_lines(text: str, num_text_cols: int = 2) -> str:
    """预处理表格文本：合并跨行文本单元格。

    F10 部分表格（如指标变动说明）的文本列会跨多行显示，例如：
        │经营活动产生│公司控股子公司贵│  2690989.13│  880919.56│  205.48│
        │的现金流量净│州茅台集团财务有│            │           │         │
        │额          │限公司不可随时支│            │           │         │

    本函数将后两行合并到第一行的前 num_text_cols 列，便于 parse_table 解析。

    Args:
        text: 包含表格的文本
        num_text_cols: 前几列是文本列（可跨行），默认 2

    Returns:
        str: 合并后的文本
    """
    if not text:
        return text
    # 归一化全角竖线 ｜ → 半角 │
    text = _normalize_pipes(text)
    lines = text.split('\n')
    result: List[str] = []
    last_data_idx = -1  # result 中最近一个数据行的索引

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('│') or _is_border_line(stripped):
            result.append(line)
            continue
        parts = [p.strip() for p in stripped.strip('│').split('│')]
        if len(parts) <= num_text_cols:
            result.append(line)
            last_data_idx = len(result) - 1
            continue
        text_cols = parts[:num_text_cols]
        rest_cols = parts[num_text_cols:]
        text_has_content = any(text_cols)
        rest_empty = all(not p or p == '---' for p in rest_cols)

        if text_has_content and rest_empty and last_data_idx >= 0:
            # 合并到上一个数据行的前 num_text_cols 列
            last_line = result[last_data_idx].strip()
            last_parts = [p.strip() for p in last_line.strip('│').split('│')]
            for j in range(min(num_text_cols, len(last_parts))):
                if text_cols[j] and text_cols[j] != '---':
                    if last_parts[j] in ('', '---'):
                        last_parts[j] = text_cols[j]
                    else:
                        last_parts[j] = last_parts[j] + text_cols[j]
            # 重建行（保留 │ 分隔，不保留原始空格对齐 — parse_table 会 strip）
            result[last_data_idx] = '│' + '│'.join(last_parts) + '│'
        else:
            result.append(line)
            last_data_idx = len(result) - 1

    return '\n'.join(result)


def transpose_table(rows: List[Dict[str, str]], key_col: str) -> List[Dict[str, str]]:
    """转置 F10 表格：原 rows 每行一个指标，转置后每行一个时期。

    F10 表格原始格式：指标为行，时期为列（如 2026-03-31, 2025-12-31）。
    转置后时期为行，便于按期查询。

    Args:
        rows: parse_table 的输出（每行一个指标字典）
        key_col: 指标列名（如 '财务指标'、'偿债能力指标'）

    Returns:
        list[dict]: 每个时期一个字典，含 'period' 字段 + 各指标值
    """
    if not rows:
        return []
    # 收集所有时期列名（去掉 key_col）
    periods = [c for c in rows[0].keys() if c != key_col]
    result: List[Dict[str, str]] = []
    for period in periods:
        entry: Dict[str, str] = {'period': period.strip()}
        for row in rows:
            indicator = (row.get(key_col) or '').strip()
            if indicator:
                entry[indicator] = (row.get(period) or '').strip()
        result.append(entry)
    return result


def parse_text_table(text: str, min_spaces: int = 2) -> List[Dict[str, str]]:
    """解析空格分隔的文本表格（F15 排名表、F16 评级统计等）。

    格式示例（F16 盈利预测明细）：
        日期           评级       评级变化       目标价    2026EPS    研究机构
        ─────────────────────────────────────────────────
        2026-06-14     买入       维持          2001.98      67.74       华创证券

    解析策略：
    1. 找到 ──── 分隔线，其上一行为表头
    2. 用 2+ 空格分割表头得到列名
    3. 用 2+ 空格分割数据行，按列名组装字典
    4. 跳过分隔线和空行

    Args:
        text: 包含空格分隔表格的文本
        min_spaces: 列分隔的最小空格数，默认 2

    Returns:
        list[dict]: 每行一个字典
    """
    if not text:
        return []
    lines = text.split('\n')
    # 找到分隔线 ────
    sep_idx = -1
    for i, line in enumerate(lines):
        if '──' in line and len(line.strip()) > 5:
            sep_idx = i
            break
    if sep_idx < 1:
        return []
    # 表头行：分隔线上一行（跳过空行）
    header_idx = sep_idx - 1
    while header_idx >= 0 and not lines[header_idx].strip():
        header_idx -= 1
    if header_idx < 0:
        return []
    col_names = [p.strip() for p in re.split(r'\s{' + str(min_spaces) + ',}', lines[header_idx].strip()) if p.strip()]
    if not col_names:
        return []

    rows: List[Dict[str, str]] = []
    for i in range(sep_idx + 1, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
        if '──' in line and len(line) > 5:
            # 遇到下一个分隔线，表格结束
            break
        parts = [p.strip() for p in re.split(r'\s{' + str(min_spaces) + ',}', line) if p.strip()]
        if not parts:
            continue
        # 列数匹配或接近匹配时才组装
        if len(parts) >= len(col_names):
            rows.append(dict(zip(col_names, parts[:len(col_names)])))
        elif len(parts) >= len(col_names) - 1:
            # 最后一列可能缺失，补 ---
            parts_padded = parts + ['---'] * (len(col_names) - len(parts))
            rows.append(dict(zip(col_names, parts_padded)))
    return rows


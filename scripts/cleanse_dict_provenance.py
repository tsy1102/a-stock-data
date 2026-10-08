#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 field_dict.md 字段表中的「过程/猜测/证伪」叙述从 含义/状态 列迁出到独立溯源层。

设计原则（结论/过程分层）：
- 字段表只保留「结论投影」：
  * 状态列 -> 纯标记(✅/❌/⏸️/⚠️) + 证据层级(L1/L2/定案/跨源/官方命名/fuyao锚)
  * 含义列 -> 仅结论中文名（已定案字段）；未破解字段写「待破解」
- 被剥离的过程/猜测/证伪文本原样迁移到 docs/field_verification/PROVENANCE.md，
  按 (源, 字段) 归档，可复核、不丢失 provenance。
- 仅处理「含过程指示词」的单元格；干净单元格不改动 -> 最小 diff。
- 保持表格列数/表头不变，确保 parse_tables/extract_registry 兼容。

用法：
  python cleanse_dict_provenance.py            # dry-run，打印拟改动摘要
  python cleanse_dict_provenance.py --apply    # 实际改写并生成 PROVENANCE.md
"""

import argparse
import sys, os, re, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import extract_registry as er
import gen_field_matrix as gm
import audit_field_completeness as afc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT = os.path.join(ROOT, "docs", "field_source_reference.md")
GENERATED_DICT = os.path.join(ROOT, "docs", "field_dict.md")
PRE_RESTRUCTURE_BACKUP = os.path.join(
    ROOT, "docs", "backups", "field_dict_pre_restructure_20261005.md"
)
PROV = os.path.join(ROOT, "docs", "field_verification", "PROVENANCE.md")

# 过程/猜测指示词：单元格含其一才视为需要净化（避免动干净单元格）
PROC_KW = [
    "猜测",
    "推断",
    "疑",
    "可能",
    "待破解",
    "待核",
    "推翻",
    "证伪",
    "旧标注",
    "疑似",
    "暂定",
    "待验证",
    "大概率",
    "应为",
    "怀疑",
    "原注",
    "原标",
    "原以为",
    "旧标",
    "口径",
    "实测",
    "样本",
    "对撞",
    "锚",
    "命中",
    "留待",
    "弃用",
    "未接入",
    "退役",
    "deprecated",
    "→",
    "＝",
    "=",
    "：",
    ":",
    "（",
    "(",
    "—",
    "·",
    "```",
]
# 已定案指示
DECIDED = ["✅"]
# 未破解指示（不含 ✅ 时）
UNDEC = ["❌", "⏸️", "待破解", "候选", "未知", "未实证"]

TIER_RE = re.compile(r"(L1|L2|定案|跨源|官方命名|fuyao锚|数值实证|结构化|交叉)")
MARK_RE = re.compile(r"(✅|❌|⏸️|⚠️)")
ARROW = "→"


def is_proc(cell):
    return any(k in cell for k in PROC_KW)


def clean_status(raw):
    """返回 (new_marker, provenance_text)。new_marker 仅含标记+层级。"""
    raw = raw.strip()
    if not raw:
        return "", ""
    # 箭头取最终状态
    if ARROW in raw:
        final = raw.split(ARROW)[-1]
    else:
        final = raw
    mk = MARK_RE.search(final)
    if not mk:
        mk = MARK_RE.search(raw)
    marker = mk.group(1) if mk else "⚠️"
    tier = TIER_RE.search(raw)
    tier_s = (" " + tier.group(1)) if tier else ""
    new = (marker + tier_s).strip()
    prov = raw if raw != new else ""
    return new, prov


def _strip_marker(s):
    """去掉开头的状态标记（✅/❌/⏸️/⚠️）及其后空白，保留 ** 加粗结构。"""
    s = re.sub(r"^[✅❌⏸⚠]\s*", "", s)
    s = re.sub(r"^[\uFE0F\u200b-\u200f‍]*", "", s)  # 去变体选择符/零宽
    return s.strip()


def _clean_concl(c):
    """结论收尾清理：去首尾 **/*、前导等号/空格。"""
    c = c.strip().strip("*").strip()
    c = re.sub(r"^[=＝\s]+", "", c)
    return c.strip()


def clean_meaning(raw, decoded):
    """返回 (new_meaning, provenance_text)。"""
    s = raw.strip()
    if re.match(r"^[*(]?\s*丢弃\s*[)*]?$", s):
        return s, ""
    s2 = _strip_marker(s)
    if not s2:
        return "", raw
    if not decoded:
        # 未破解：含义列只留「待破解」，全部原文本迁溯源
        return "待破解", raw
    # 已定案：提取结论
    mb = re.search(r"\*\*(.+?)\*\*", s2)
    if mb:
        concl = _clean_concl(mb.group(1))
        rest = (s2[: mb.start()] + s2[mb.end() :]).strip().strip("*").strip()
        if concl:
            return concl, rest
    m = re.search(r"[（(=—·：:、]", s2)
    if m:
        concl = _clean_concl(s2[: m.start()])
        rest = s2[m.start() :].strip().strip("*").strip()
        if concl:
            return concl, rest
    return _clean_concl(s2), ""


def iter_table_rows(lines):
    cur_sec = ""
    i, n = 0, len(lines)
    while i < n:
        l = lines[i]
        m = re.match(r"^#{1,4} (.*)", l)
        if m:
            cur_sec = m.group(1).strip()
        if l.strip().startswith("|"):
            j = i
            block = []
            while j < n and lines[j].strip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip()[1:-1].split("|")]
                block.append((j, cells))
                j += 1
            if len(block) >= 3:
                sep = block[1][1]
                is_sep = len(sep) >= 2 and all(re.match(r"^:?-{2,}:?$", c or "-") for c in sep)
                if is_sep:
                    header = block[0][1]
                    for ln, row in block[2:]:
                        yield (ln, cur_sec, header, row)
            i = j
        else:
            i += 1


def main():
    parser = argparse.ArgumentParser(description="清理字段表过程叙述并保留溯源")
    parser.add_argument(
        "--apply", action="store_true", help="写入 --output 指定的新文件并更新 PROVENANCE"
    )
    parser.add_argument("--source", default=DICT, help="输入字段历史参考文件")
    parser.add_argument("--output", help="--apply 时必填；不得覆盖归档源或生成字典")
    args = parser.parse_args()
    if args.apply and not args.output:
        parser.error("--apply 必须显式指定 --output；归档源与生成主字典不可直接改写")
    source_path = os.path.abspath(args.source)
    output_path = os.path.abspath(args.output) if args.output else None
    protected_paths = {
        source_path,
        os.path.abspath(DICT),
        os.path.abspath(GENERATED_DICT),
        os.path.abspath(PRE_RESTRUCTURE_BACKUP),
        os.path.abspath(PROV),
    }
    if args.apply and output_path in protected_paths:
        parser.error("--output 不得覆盖 field_source_reference、field_dict 或重整前备份")
    lines = open(source_path, encoding="utf-8").read().split("\n")
    prov = {}  # token -> {section -> {"meaning":..., "status":...}}
    changes = []  # (ln, col_type, old, new)

    for ln, sec, header, row in iter_table_rows(lines):
        if any(kw in sec for kw in gm.NON_FIELD_SEC):
            continue
        srcs = afc.section_to_sources(sec)
        if not srcs:
            continue
        t_idx, m_idx, u_idx, s_idx = er.locate_columns(header)
        if t_idx is None or t_idx >= len(row):
            continue
        token_cell = row[t_idx]
        tokens = er.extract_tokens_from_cell(token_cell, srcs)
        if not tokens:
            continue
        new_line = lines[ln]
        parts = new_line.split("|")
        # parts[k+1] 对应第 k 个单元格
        changed = False

        # 状态列
        if s_idx is not None and s_idx < len(row):
            sc = row[s_idx]
            if is_proc(sc):
                new_s, sprov = clean_status(sc)
                if new_s and new_s != sc.strip():
                    # 保留原单元格前后空格
                    orig = parts[s_idx + 1]
                    lead = re.match(r"^(\s*)", orig).group(1)
                    trail = re.match(r".*?(\s*)$", orig).group(1)
                    parts[s_idx + 1] = lead + new_s + trail
                    changed = True
                    changes.append((ln, "status", sc.strip(), new_s))
                    if sprov:
                        for tk in tokens:
                            prov.setdefault(tk, {}).setdefault(sec, {"meaning": "", "status": ""})
                            prov[tk][sec]["status"] = sprov

        # 含义列
        if m_idx is not None and m_idx < len(row):
            mc = row[m_idx]
            if is_proc(mc):
                decoded = any(
                    k in (row[s_idx] if s_idx is not None and s_idx < len(row) else "")
                    for k in DECIDED
                )
                undecided = (not decoded) and any(
                    k in (row[s_idx] if s_idx is not None and s_idx < len(row) else "")
                    for k in UNDEC
                )
                new_m, mprov = clean_meaning(mc, decoded)
                if new_m and new_m != mc.strip():
                    orig = parts[m_idx + 1]
                    lead = re.match(r"^(\s*)", orig).group(1)
                    trail = re.match(r".*?(\s*)$", orig).group(1)
                    parts[m_idx + 1] = lead + new_m + trail
                    changed = True
                    changes.append((ln, "meaning", mc.strip(), new_m))
                    if mprov:
                        for tk in tokens:
                            prov.setdefault(tk, {}).setdefault(sec, {"meaning": "", "status": ""})
                            prov[tk][sec]["meaning"] = mprov

        if changed:
            lines[ln] = "|".join(parts)

    if not args.apply:
        print(f"[DRY-RUN] 拟改动单元格数: {len(changes)}；溯源条目(字段): {len(prov)}")
        print("--- 前 50 条改动预览 ---")
        for ln, ctype, old, new in changes[:50]:
            print(f"  L{ln} [{ctype}] {old!r}  ->  {new!r}")
        print("--- 溯源条目样例(前 20) ---")
        for i, (tk, secs) in enumerate(prov.items()):
            if i >= 20:
                break
            for sec, d in secs.items():
                print(f"  {tk} @ {sec[:30]}")
                if d["meaning"]:
                    print(f"     含义过程: {d['meaning'][:80]}")
                if d["status"]:
                    print(f"     状态过程: {d['status'][:80]}")
        return

    # apply
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    # 写 PROVENANCE.md
    out = [
        "<!-- AUTO-GEN: provenance -->",
        "# 字段过程/猜测/证伪溯源档案",
        "",
        "> 本文件由 `scripts/cleanse_dict_provenance.py` 从 `docs/field_source_reference.md` 字段表净化迁出。",
        "> 字段表本身仅保留「结论投影」（含义=中文名 / 状态=标记+层级）；",
        "> 此处按 (源, 字段) 归档被迁出的碰撞过程、猜测与证伪叙述，供复核与再对撞使用。",
        "> 内容均为原文迁移，未做删改。",
        "",
    ]
    for tk in sorted(prov.keys()):
        secs = prov[tk]
        out.append(f"## {tk}")
        for sec in sorted(secs.keys()):
            d = secs[sec]
            out.append(f"### {sec}")
            if d["meaning"]:
                out.append(f"- 含义原过程: {d['meaning']}")
            if d["status"]:
                out.append(f"- 状态原过程: {d['status']}")
            out.append("")
    with open(PROV, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"[APPLY] 改动单元格: {len(changes)}；溯源条目: {len(prov)}")
    print(f"[APPLY] 已写入 {output_path}")
    print(f"[APPLY] 已生成 {PROV}")


if __name__ == "__main__":
    main()

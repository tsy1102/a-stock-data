#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Second-pass layered cleansing of docs/field_dict.md.

The first pass (cleanse_dict_provenance.py, commit c6f976d) only stripped
guess/inference process words. This pass targets the SECOND category of residue
the user flagged: **verification-result narratives** still embedded in the
conclusion columns (状态 / 含义) of field tables, e.g.

  status : ✅ 跨源|Δ|=0 / max|Δ|≤0.19，见 docs/...碰撞报告
  meaning: ✅ **东财网页CDP对撞**：ulist f80=39.97 ↔ 中单流出(...)三锚样本算术吻合

Policy (user-approved 2026-09-21):
  - Status column  -> keep only marker + evidence tier (✅ 跨源 / ⚠️ ...).
  - Meaning column -> extract the clean Chinese name; move the verification
                       narrative to PROVENANCE.md.
  - High-confidence extraction (backticked name, or 待破解 for unresolved) -> no flag.
  - Uncertain extraction (↔ w/o backtick, K线/AH known-map, fallback) -> append
    `⚠️待核` so the human validates before it is treated as a settled name.
  - Genuinely unresolved cells (异索引待数值对撞 / 具体语义待定 / 资金流细分小比率)
    -> meaning collapses to `待破解` (per user rule: too much guessing is harmful).

Dry-run by default; --apply modifies field_dict.md + appends to PROVENANCE.md.
"""
import re
import sys

SRC = "docs/field_dict.md"
PROV = "docs/field_verification/PROVENANCE.md"

MARK_RE = re.compile(r"^[✅❌⏸️⚠️]")
# markers that indicate a verification-result narrative (not a clean conclusion)
NARR_RE = re.compile(
    r"(对撞|↔|≡|精确吻合|算术吻合|见\s*`?docs|\\|Δ\\|=0|K线实证|跨源数值实证|"
    r"系误判|已证伪|原待核实|待重定|三锚样本|四铁律|第九轮审计|勾稽|跨源对齐|"
    r"待数值对撞|具体语义待定|资金流细分小比率|报价页)"
)
UNRES_RE = re.compile(r"具体语义待定|资金流细分小比率|待数值对撞|异索引，同号≠同义")
# evidence tier tokens
TIERS = ["L1", "L2", "定案", "跨源", "官方命名", "fuyao锚", "变量名"]


def strip_marker(s: str) -> str:
    return re.sub(r"^[✅❌⏸️⚠️]\s*", "", s).strip()


def marker_of(s: str) -> str:
    m = MARK_RE.match(s.strip())
    return m.group(0) if m else ""


def tier_of(s: str) -> str:
    # return the EARLIEST-occurring evidence tier in the text (most salient)
    best = None
    for t in TIERS:
        pos = s.find(t)
        if pos != -1 and (best is None or pos < best[1]):
            best = (t, pos)
    return best[0] if best else ""


def strip_method_prefix(s: str) -> str:
    """Remove leading `✅ **METHOD**：` / `⚠️ **METHOD**：` prefix."""
    m = re.match(r"^[✅❌⏸️⚠️]\s*\*\*([^*]+)\*\*[:：]\s*", s)
    if m:
        return s[m.end():]
    return s


KNOWN_MEANING = {
    "f24": "涨跌幅(60日)",
    "f25": "涨跌幅(年初至今/YTD)",
    "f109": "涨跌幅(5日)",
    "f110": "涨跌幅(20日)",
    "f160": "涨跌幅(10日)",
    "f190": "AH上市标识(枚举{0,3})",
    "f191": "H股代码",
    "f193": "H股名称",
}

HEADER_WORDS = {"字段", "字段名", "token", "代码", "源", "含义", "状态", "字段代码", "项目"}

# Curated clean Chinese names for the verification-narrative meaning cells.
# Derived from each narrative's explicit field labels (backticked 报价页/F10
# field names, stated financial-field names, ratio/period structure). This is
# deterministic and reviewed against the narrative text — NOT a fragile regex.
# Keys not present fall through to the heuristic (kept only as a safety net).
OVERRIDE = {
    "f2": "最新价", "f12": "股票代码", "f14": "股票名称",
    "f20": "总市值", "f21": "流通市值",
    "f24": "涨跌幅(60日)", "f25": "涨跌幅(年初至今)",
    "f31": "买一价", "f32": "卖一价", "f35": "内盘",
    "f36": "户均流通股",  # ambiguous: 流通股/股东户数≈值 — kept ⚠️待核
    "f37": "净资产收益率(加权)", "f38": "总股本", "f39": "流通股",
    "f40": "营业总收入", "f41": "营业总收入同比增长", "f42": "营业利润",
    "f43": "投资收益", "f44": "利润总额", "f47": "未分配利润",
    "f50": "资产总计", "f51": "流动资产合计", "f52": "固定资产",
    "f53": "无形资产", "f54": "负债合计", "f55": "流动负债合计",
    "f56": "非流动负债合计", "f57": "资产负债率", "f59": "收盘价",
    "f60": "资本公积", "f61": "每股公积金",
    "f62": "主力净流入",
    "f64": "超大单流入", "f65": "超大单流出", "f66": "超大单净流入",
    "f67": "超大单流入占比", "f68": "超大单流出占比", "f69": "超大单净占比",
    "f70": "大单流入", "f71": "大单流出", "f72": "大单净流入",
    "f73": "大单流入占比", "f74": "大单流出占比", "f75": "大单净占比",
    "f76": "中单流入", "f77": "中单流出", "f78": "中单净流入",
    "f79": "中单流入占比", "f80": "中单流出占比", "f81": "中单净占比",
    "f82": "小单流入", "f83": "小单流出", "f84": "小单净流入",
    "f85": "小单流入占比", "f86": "小单流出占比", "f87": "小单净占比",
    "f100": "行业标签", "f101": "领涨股", "f102": "地域板块",
    "f109": "涨跌幅(5日)", "f110": "涨跌幅(20日)",
    "f144": "最新价", "f146": "关联股票代码", "f160": "涨跌幅(10日)",
    "f164": "5日主力净流入", "f165": "5日主力净占比",
    "f166": "5日超大单净流入", "f167": "5日超大单净占比",
    "f168": "5日大单净流入", "f169": "5日大单净占比",
    "f170": "5日中单净流入", "f171": "5日中单净占比",
    "f172": "5日小单净流入", "f173": "5日小单净占比",
    "f174": "10日主力净流入", "f175": "10日主力净占比",
    "f176": "10日超大单净流入", "f177": "10日超大单净占比",
    "f178": "10日大单净流入", "f179": "10日大单净占比",
    "f180": "10日中单净流入", "f181": "10日中单净占比",
    "f182": "10日小单净流入", "f183": "10日小单净占比",
    "f184": "主力净比",
    "f190": "AH上市标识", "f191": "H股代码", "f193": "H股名称",
    "f200": "B股市场码", "f211": "买一量", "f212": "卖一量",
    "f221": "中报报告期",
}
# Names that are genuinely ambiguous -> keep ⚠️待核 even with override.
AMBIG = {"f36"}


def propose_meaning(tok: str, raw: str):
    """Return (clean_meaning, confidence, provenance_text).

    confidence: 'HIGH' (no flag), 'MED'/'LOW' (append ⚠️待核).
    """
    # 1) curated override (deterministic, reviewed against narrative)
    if tok in OVERRIDE:
        conf = "HIGH" if tok not in AMBIG else "MED"
        return OVERRIDE[tok], conf, raw

    marker = marker_of(raw)
    body = strip_method_prefix(raw)

    # 2) backticked name after ↔  -> high confidence
    bt = re.search(r"↔\s*`([^`]+)`", raw)
    if bt:
        return bt.group(1).strip(), "HIGH", raw

    # 3) unresolved narrative -> collapse to 待破解 (policy: no guessing)
    if UNRES_RE.search(raw):
        return "待破解", "HIGH", raw

    # 4) ↔ then Chinese term before a delimiter -> medium
    ar = re.search(
        r"↔\s*([\u4e00-\u9fff][\u4e00-\u9fffA-Za-z0-9%/_.（）()\-]*?)"
        r"(?:[\(（]|\s*[，,；;。]|精确|≡|=|$)",
        raw,
    )
    if ar:
        cand = ar.group(1).strip()
        if cand:
            return cand, "MED", raw

    # 5) known map (K线 / AH)
    if tok in KNOWN_MEANING:
        return KNOWN_MEANING[tok], "MED", raw

    # 6) fallback
    ch = re.search(r"[\u4e00-\u9fff][\u4e00-\u9fffA-Za-z0-9%/_.（）()\-]*", body)
    if ch:
        return ch.group(0).strip(), "LOW", raw

    return None, "LOW", raw


def propose_status(raw: str):
    """Strip verification narrative from a status cell, keep marker+tier."""
    marker = marker_of(raw)
    tier = tier_of(raw)
    new = marker
    if tier:
        new = f"{marker} {tier}" if marker else tier
    # provenance = everything after marker+tier
    rest = raw.strip()
    rest = re.sub(r"^[\u4e00-\u9fffA-Za-z0-9%/_.（）()\-]*", "", rest)  # drop leading tier-ish
    rest = rest[len(marker):].strip() if marker else rest
    # remove the tier token from rest
    for t in TIERS:
        rest = rest.replace(t, "")
    rest = rest.strip(" |")
    return new.strip(), (rest if rest else raw.strip())


def main():
    apply = "--apply" in sys.argv
    lines = open(SRC, encoding="utf-8").read().splitlines()
    out = []
    plan = []  # (line_no, token, col, old, new, conf, prov)
    prov_entries = []  # (token, section_hint, col, prov_text)

    for idx, ln in enumerate(lines):
        if not ln.startswith("|") or ln.count("|") < 3:
            out.append(ln)
            continue
        # Robust 3-column parse that PRESERVES literal '|' inside cells
        # (e.g. `|Δ|=0` in a status cell). token = between 1st & 2nd pipe,
        # meaning = between last & 2nd-last pipe, status = everything between.
        first = ln.find("|")
        second = ln.find("|", first + 1)
        last = ln.rfind("|")
        second_last = ln.rfind("|", 0, last)
        if second == -1 or second_last <= second or last <= second_last:
            out.append(ln)
            continue
        token = ln[first + 1:second].strip()
        if token in HEADER_WORDS or not token:
            out.append(ln)
            continue
        status = ln[second + 1:second_last].strip()
        meaning = ln[second_last + 1:last].strip()

        new_status = status
        new_meaning = meaning
        changed = False

        # --- status column residue ---
        if MARK_RE.match(status) and NARR_RE.search(status) and len(status) > 12:
            ns, sprov = propose_status(status)
            if ns != status:
                plan.append((idx + 1, token, "状态", status, ns, "HIGH", sprov))
                prov_entries.append((token, "状态列验证叙述", "状态", sprov))
                new_status = ns
                changed = True

        # --- meaning column residue ---
        if MARK_RE.match(status) and NARR_RE.search(meaning) and (
            "**" in meaning or "对撞" in meaning or "↔" in meaning
            or "K线实证" in meaning or UNRES_RE.search(meaning)
        ):
            cm, conf, mprov = propose_meaning(token, meaning)
            if cm is None:
                cm = "待破解"
                conf = "HIGH"
            disp = cm + (" ⚠️待核" if conf in ("MED", "LOW") else "")
            if disp != meaning:
                plan.append((idx + 1, token, "含义", meaning, disp, conf, mprov))
                prov_entries.append((token, "含义列验证叙述", "含义", mprov))
                new_meaning = disp
                changed = True

        if changed:
            out.append(f"| {token} | {new_status} | {new_meaning} |")
        else:
            out.append(ln)

    if not apply:
        # ---- DRY RUN: emit review plan ----
        print(f"[DRY-RUN] would change {len(plan)} cells "
              f"({sum(1 for p in plan if p[2]=='状态')} status, "
              f"{sum(1 for p in plan if p[2]=='含义')} meaning)")
        print(f"[DRY-RUN] provenance entries to archive: {len(prov_entries)}")
        # write plan file
        lines_out = ["# 二次分层清理 · 待复核方案（DRY-RUN，未落盘）", ""]
        lines_out.append(f"共拟改动 **{len(plan)}** 处单元格（状态 "
                         f"{sum(1 for p in plan if p[2]=='状态')} / 含义 "
                         f"{sum(1 for p in plan if p[2]=='含义')}），"
                         f"迁移验证叙述 **{len(prov_entries)}** 条至 PROVENANCE.md。")
        lines_out.append("")
        lines_out.append("> 含义列中标注 `⚠️待核` 者为抽取置信度不足、需人工确认的建议名；"
                         "其余为高置信（反引号名 / 未破解→待破解）。")
        lines_out.append("")
        cur = None
        for ln, tok, col, old, new, conf, prov in plan:
            tag = "" if conf == "HIGH" else f" 【{conf}·⚠️待核】"
            lines_out.append(f"### L{ln} `{tok}` · {col}{tag}")
            lines_out.append(f"- 原: `{old[:160]}`")
            lines_out.append(f"- 拟: `{new[:120]}`")
            lines_out.append("")
        open("docs/field_verification/SECOND_PASS_PLAN.md", "w", encoding="utf-8").write(
            "\n".join(lines_out) + "\n"
        )
        print("[DRY-RUN] review plan -> docs/field_verification/SECOND_PASS_PLAN.md")
        return

    # ---- APPLY ----
    open(SRC, "w", encoding="utf-8").write("\n".join(out) + "\n")
    # append provenance section
    block = ["", "## 二次分层清理·验证叙述溯源（自动归档，未做删改）", ""]
    for tok, sec, col, prov in prov_entries:
        block.append(f"### {tok} · {sec}")
        block.append(f"- {col}原过程: {prov}")
        block.append("")
    with open(PROV, "a", encoding="utf-8") as f:
        f.write("\n".join(block) + "\n")
    print(f"[APPLY] changed {len(plan)} cells; archived {len(prov_entries)} provenance entries")


if __name__ == "__main__":
    main()

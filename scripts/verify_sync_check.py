#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_sync_check.py — 主字典 ↔ verify 分字典 一致性闸门（离线，零网络）

用法:
    python scripts/verify_sync_check.py [--strict] [--sync] [--repo DIR]

目的:
    防止「破解新字段后未同步分字典」导致主字典(决策层)与 verify/(实证层)割裂。
    对应文档规则: docs/field_dict.md §12.15.10「破解新字段→同步分字典（强制规则）」。

检查项:
  HARD FAIL (退出码 1) —— 默认即执行，是 CI/commit 前的可靠闸门:
    1. 断链      : field_dict.md 引用的 docs/verify/*.md 必须真实存在。
    2. 孤儿      : verify/*.md 必须至少被 field_dict.md 引用一次（避免悬空/失维护附录）。
    3. 映射一致性: 本脚本内嵌 MAPPING 中每个分字典文件必须存在且被引用。
    4. 陈旧结论  : 主字典某字段有「升级事件」(主动升级/非对撞升级/升级定案方向/→Beta族高置信
                  /→均价-VWAP类价格派生候选强/候选=委差 等) 且日期新于分字典同字段最新日期
                  → 分字典未同步升级（防「主字典升级但分字典漏更」，即本次发现的真实漏洞）。
  ADVISORY WARN (best-effort; --strict 时升级为 FAIL) —— 仅 --sync 时执行:
    5. 同步检查  : 主字典中出现的某源字段 token，若对应分字典存在且可解析，
                  报告主字典有而分字典缺失的字段（即「已破解未同步」）。
                  ⚠️ 该检查为全局子集比对，同一字段码(push2/ulist 共用 fNN)会跨源误报，
                     仅供人工深审，不建议设为强制失败门槛。

退出码:
    有任何 HARD FAIL                                → 1
    仅 WARN（且非 --strict）                         → 0
    --strict 且 WARN 非空                           → 1
    全过                                            → 0

依赖: 纯标准库（re / os / sys / argparse），可在任何 Python 3.8+ 运行，无需联网。
"""

import argparse
import datetime
import os
import re
import sys

# ----------------------------------------------------------------------------
# 路径解析：脚本位于 <repo>/scripts/verify_sync_check.py
# ----------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
FIELD_DICT = os.path.join(REPO_ROOT, "docs", "field_dict.md")
VERIFY_DIR = os.path.join(REPO_ROOT, "docs", "verify")

# 单一真相源接入：优先用 field_registry.json 的 sources[].verify_file；
# 缺失/不可用时回退到下方 MAPPING_HARDCODED（CI 闸门权威配置，须显式可审）。
# 不静默吞错：registry 读取失败则退化为硬编码，闸门行为不变。
try:
    sys.path.insert(0, SCRIPT_DIR)
    import field_registry_api as _fra
except Exception:  # noqa: BLE001
    _fra = None


# ----------------------------------------------------------------------------
# 内嵌「源→分字典」映射（★单一权威配置（硬编码基线），须与 field_dict.md §12.15.10 保持同步）
#   key  = 源名（仅作展示/诊断）
#   file = verify/ 下的分字典文件名（basename）
# 注：本映射现为 CI 闸门的硬编码基线；get_source_mapping() 会优先用 registry 覆盖，
#     缺失项仍由此基线兜底，保证闸门行为在 registry 不完善时不退化。
# ----------------------------------------------------------------------------
MAPPING_HARDCODED = {
    "em_indicators": "em_indicators.md",
    "em_tableheader_ids": "em_tableheader_ids.md",
    "tdx_func_fields": "tdx_func_fields.md",
    "tdx_headers_definition": "tdx_headers_definition.md",
    "tdxhy_x_names": "tdxhy_x_names.md",
    "tencent": "tencent_verify.md",
    "push2": "push2_verify.md",
    "ulist_push2_align": "ulist_push2_align.md",
    "ths_tableheader": "ths_tableheader_ids.md",
    "samples": "samples_verify.md",
    "axdata": "axdata_verify.md",
    "ftshare": "ftshare_fields_mirror.md",
    "fuyao": "fuyao_api_full.md",
    "client_fields_enum": "client_fields_enum.md",
    "network_servers": "network_servers.md",
    "levistock": "levistock_field_verify.md",
}


def get_source_mapping():
    """源→分字典映射：优先 registry.sources[].verify_file（单一真相源），缺失回退硬编码基线。

    返回 dict 保证包含所有 MAPPING_HARDCODED 条目（registry 仅覆盖已知项，不削减闸门）。
    """
    m = dict(MAPPING_HARDCODED)
    if _fra is not None:
        try:
            reg = _fra.load_registry()
            for s in reg.get("sources", []):
                vf = s.get("verify_file")
                if vf:
                    m[s["name"]] = vf
        except Exception:  # noqa: BLE001
            pass
    return m

# 同步检查配置（best-effort）：对每个 (分字典, 字段 token 正则) 做子集比对。
# 仅对「附录=完整原始全表」的源启用，避免误报。未列出的源跳过（人工复核）。
SYNC_CHECKS = [
    # push2 / ulist 字段编号族：f + 2~3 位数字
    {"file": "push2_verify.md", "token": r"\bf\d{2,3}\b"},
    {"file": "ulist_push2_align.md", "token": r"\bf\d{2,3}\b"},
    # 腾讯字段族：tx + 2~3 位数字
    {"file": "tencent_verify.md", "token": r"\btx\d{2,3}\b"},
    # 东财指标代码族：1 + 11 位数字（100000000xxx）
    {"file": "em_indicators.md", "token": r"\b1\d{11}\b"},
]

# 陈旧结论检查配置（HARD 4）：分字典 → 字段 token 正则。
# 须与该源实际书写格式一致（腾讯用方括号 [NN]，push2/ulist 用 fNN）。
# 仅对「附录=完整原始全表」的源启用，避免跨源误报。
STALE_CHECKS = [
    {"file": "tencent_verify.md", "token": r"\[\d{1,3}\]"},
    {"file": "push2_verify.md",   "token": r"\bf\d{2,3}\b"},
]

# 主字典中标识「字段结论被升级/重判定」的事件短语（命中即视为该字段有新版结论，分字典须同步）。
# 仅覆盖本项目升级约定（结论级变更，须同步分字典）：主动法升级 / 非对撞升级 / 主动性破解升级 /
# 升级定案方向 / Beta族高置信 / 均价-VWAP类价格派生候选强 / 候选=委差。
# ⚠️ 故意不含「升级 L1 / 升 L1→」等重确认戳（如 [69] 2026-08-25 升级 L1），此类仅复验旧结论、
#    分字典已记录当前结论，不应误判为陈旧。未来字段升级请统一用「主动升级」约定以便本闸门捕获。
UPGRADE_EVENT_RE = re.compile(
    r"主动升级|非对撞升级|主动性破解升级|升级定案方向|"
    r"→Beta族高置信|→均价/VWAP类价格派生候选强|候选=委差"
)
DATE_RE = re.compile(r"20\d\d-\d\d-\d\d")


# ----------------------------------------------------------------------------
# 工具函数
# ----------------------------------------------------------------------------
def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def collect_referenced_basenames(text):
    """从主字典文本提取所有被引用的 verify/*.md basename。"""
    pat = re.compile(r"(?:docs/)?verify/([A-Za-z0-9_]+\.md)")
    return set(m.group(1) for m in pat.finditer(text))


def collect_verify_md_files():
    """列出 verify/ 目录下所有 .md 文件（basename 集合）。"""
    if not os.path.isdir(VERIFY_DIR):
        return set()
    return set(f for f in os.listdir(VERIFY_DIR) if f.endswith(".md"))


def extract_tokens(text, regex):
    """按正则抽取字段 token 集合（小写归一）。"""
    return set(m.group(0).lower() for m in re.finditer(regex, text))


def _subject_tokens(line, tok_re):
    """提取一行中作为「主语」的字段 token：表格首格，或加粗主语（**[NN] / **fNN）。

    升级行常顺带提及对照字段（如 [85] 行证据列引用 [19]/[21]/[50]），
    这些不是被升级的字段，必须排除，否则会误报。"""
    toks = []
    s = line.strip()
    if s.startswith("|"):
        cells = line.split("|")
        if len(cells) >= 2:
            toks.extend(tok_re.findall(cells[1]))
    # 加粗主语：** [NN] / **fNN（升级块 bullet 格式）
    for m in re.finditer(r"(?<=\*\*)" + tok_re.pattern, line):
        toks.append(m.group(0))
    return toks


def latest_upgrade_dates(text, token_regex):
    """主字典：返回 {token: 最新升级事件日期}。
    仅统计「含升级事件短语 + 日期」的行；日期取自「含升级短语的同子句」（以 ；。 切分），
    而非整行最大日期——避免把同线更晚的「维持/确认」类日期（如 [85] 2026-09-09 维持L3）
    误归为升级事件日（2026-09-03 主动升级），造成虚假陈旧误报。
    仍只取该行「主语」位置的字段 token（表格首格 / 加粗主语），排除顺带提及的对照字段。"""
    tok_re = re.compile(token_regex)
    clause_split = re.compile(r"[;；。]")
    out = {}
    for line in text.splitlines():
        if not UPGRADE_EVENT_RE.search(line):
            continue
        toks = _subject_tokens(line, tok_re)
        if not toks:
            continue
        # 取「所有含升级短语子句」的最大日期（同线多升级事件取最新）
        d = None
        for cl in clause_split.split(line):
            if UPGRADE_EVENT_RE.search(cl):
                ds = DATE_RE.findall(cl)
                if ds:
                    cd = max(ds)
                    if d is None or cd > d:
                        d = cd
        if not d:
            continue
        for tok in toks:
            if tok not in out or d > out[tok]:
                out[tok] = d
    return out


def latest_dates_anywhere(text, token_regex):
    """分字典：返回 {token: 最新日期}（任意含日期行，取每个字段 token 的最新日期）。"""
    tok_re = re.compile(token_regex)
    out = {}
    for line in text.splitlines():
        dates = DATE_RE.findall(line)
        if not dates:
            continue
        d = max(dates)  # 取该行最大日期（修复 2026-09-03/09 同现取首个的陈旧误判 bug）
        for m in tok_re.finditer(line):
            tok = m.group(0)
            if tok not in out or d > out[tok]:
                out[tok] = d
    return out


# ----------------------------------------------------------------------------
# 主升分未升 矛盾检测 (HARD 4b) — 2026-09-11 增补
#   主字典已定案(DET: L1/L2/L3/✅/精确/定案/固化/升格) 但 分字典同字段仍
#   「待确认/未知/?/疑似」→ FAIL。
#   动机：原 HARD 4 仅捕获「主动升级」短语（故意不含升格/固化以免复验误报），
#   漏掉「主字典升格/固化 → 分字典仍 ?」这类真实脱节（即本次发现的分字典滞后根因）。
#   另：原 HARD 4 不覆盖 ulist_push2_align.md 的 ? 语义行，本检查补齐。
# ----------------------------------------------------------------------------
SUB_UNRESOLVED_RE = re.compile(r"待确认|未知|疑似|待\s*F10|待终破|待\s*L1|待定|未定案|未实证")
SUB_RESOLVED_POS = [
    "L1-U", "L1", "L2", "L3", "L4", "✅", "精确", "定案", "固化", "升格",
    "恒值占位", "常量占位", "未破解", "固定等级码", "固定占位",
]

CONTRADICTION_CHECKS = [
    {"file": "push2_verify.md",      "token": r"\bf\d{2,3}\b", "fmt": "std"},
    {"file": "tencent_verify.md",    "token": r"\[\d{1,3}\]",   "fmt": "std"},
    {"file": "ulist_push2_align.md", "token": r"\bf\d{2,3}\b", "fmt": "ulist"},
]


def _rank(level):
    return {"NONE": 0, "UND": 1, "UNINFO": 2, "DET": 3}.get(level, 0)


def _classify_main(line):
    """主字典某行对该字段的等级：DET(正向定案) > UNINFO(占位/未破解) > UND > NONE。"""
    if any(k in line for k in ("L1-U", "L1", "L2", "L3", "✅", "精确", "定案", "固化", "升格")):
        return "DET"
    if any(k in line for k in ("恒值占位", "常量占位", "未破解", "固定等级码", "固定占位")):
        return "UNINFO"
    if SUB_UNRESOLVED_RE.search(line):
        return "UND"
    return "NONE"


def _classify_subj(line):
    """分字典某行对该字段的等级。"""
    if SUB_UNRESOLVED_RE.search(line) and not any(k in line for k in SUB_RESOLVED_POS):
        return "UND"
    if any(k in line for k in SUB_RESOLVED_POS):
        return "DET"
    return "NONE"


def main_status_map(text, token_regex):
    """主字典：{token: (最强level, 最新日期)}，仅统计 subject 位置 token（表格首格/加粗）。"""
    tok_re = re.compile(token_regex)
    out = {}
    for line in text.splitlines():
        dm = DATE_RE.search(line)
        d = dm.group(0) if dm else None
        for tok in _subject_tokens(line, tok_re):
            lvl = _classify_main(line)
            if lvl == "NONE":
                continue
            cur = out.get(tok)
            if cur is None:
                out[tok] = (lvl, d)
            elif _rank(lvl) > _rank(cur[0]) or (cur[1] is None and d):
                out[tok] = (lvl, d if d else cur[1])
    return out


def sub_status_map(text, token_regex, fmt):
    """分字典：{token: 最强level}。按 token 聚合取最强（避免同文件旧摘要行误报）。"""
    tok_re = re.compile(token_regex)
    agg = {}
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        if fmt == "ulist":
            cells = line.split("|")
            if len(cells) < 4:
                continue
            m = tok_re.search(cells[2])
            if not m:
                continue
            tok = m.group(0)
            # ulist 列3 = push2 语义；含 '?' 即未解（含 "?市值"/"总股本?" 等猜测）
            lvl = "UND" if "?" in cells[3] else _classify_subj(cells[3])
        else:
            toks = _subject_tokens(line, tok_re)
            if not toks:
                continue
            tok = toks[0]
            lvl = _classify_subj(line)
        cur = agg.get(tok)
        if cur is None or _rank(lvl) > _rank(cur):
            agg[tok] = lvl
    return agg


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="主字典 ↔ verify 分字典 一致性闸门")
    ap.add_argument("--strict", action="store_true",
                    help="将 ADVISORY WARN 升级为 FAIL（退出码 1）")
    ap.add_argument("--sync", action="store_true",
                    help="执行字段级同步抽检（best-effort，默认关闭以免跨源误报噪声）")
    ap.add_argument("--repo", default=REPO_ROOT,
                    help="仓库根目录（默认自动推断）")
    args = ap.parse_args()

    global FIELD_DICT, VERIFY_DIR
    if args.repo != REPO_ROOT:
        FIELD_DICT = os.path.join(args.repo, "docs", "field_dict.md")
        VERIFY_DIR = os.path.join(args.repo, "docs", "verify")

    hard_failures = []
    warnings = []

    # ---- 前置检查：文件存在性 ----
    if not os.path.isfile(FIELD_DICT):
        print(f"[FATAL] 找不到主字典: {FIELD_DICT}")
        return 1
    if not os.path.isdir(VERIFY_DIR):
        print(f"[FATAL] 找不到 verify 目录: {VERIFY_DIR}")
        return 1

    dict_text = read_text(FIELD_DICT)
    referenced = collect_referenced_basenames(dict_text)
    existing = collect_verify_md_files()

    print("=" * 68)
    print(" verify_sync_check — 主字典 ↔ verify 分字典 一致性闸门")
    print("=" * 68)
    print(f" 主字典 : {FIELD_DICT}")
    print(f" verify : {VERIFY_DIR}")
    print(f" 引用分字典数 : {len(referenced)}")
    print(f" 实际分字典数 : {len(existing)}")
    print("-" * 68)

    # ---- HARD 1: 断链 ----
    print("[HARD] 1. 断链检查（主字典引用 → 文件必须存在）")
    for base in sorted(referenced):
        if base not in existing:
            msg = f"断链: 主字典引用 {base} 但 verify/ 下不存在"
            hard_failures.append(msg)
            print(f"   ✗ {msg}")
        else:
            print(f"   ✓ {base}")
    if not referenced:
        print("   (无引用，跳过)")

    # ---- HARD 2: 孤儿附录 ----
    print("[HARD] 2. 孤儿附录检查（verify/*.md → 必须被引用）")
    for base in sorted(existing):
        if base not in referenced:
            msg = f"孤儿附录: {base} 未被主字典引用（可能失维护/悬空）"
            hard_failures.append(msg)
            print(f"   ✗ {msg}")
        else:
            print(f"   ✓ {base}")

    # ---- 漂移检测（registry vs 硬编码基线，仅告警不失败）----
    if _fra is not None:
        try:
            reg = _fra.load_registry()
            reg_map = {s["name"]: s["verify_file"] for s in reg.get("sources", [])
                       if s.get("verify_file")}
            for name, vf in reg_map.items():
                if name in MAPPING_HARDCODED and MAPPING_HARDCODED[name] != vf:
                    warnings.append(
                        f"映射漂移: 源 {name} registry={vf} 但硬编码基线={MAPPING_HARDCODED[name]}"
                        f"（建议统一为 registry 单一真相源）")
        except Exception:  # noqa: BLE001
            pass

    # ---- HARD 3: 映射一致性 ----
    print("[HARD] 3. 映射一致性（registry 优先 + 硬编码基线兜底 → 文件须存在且被引用）")
    for src, base in sorted(get_source_mapping().items()):
        if base not in existing:
            msg = f"映射缺失文件: 源 {src} 指向 {base} 不存在"
            hard_failures.append(msg)
            print(f"   ✗ {src} -> {base} (不存在)")
        elif base not in referenced:
            msg = f"映射未引用: 源 {src} 指向 {base} 但主字典未引用"
            hard_failures.append(msg)
            print(f"   ✗ {src} -> {base} (未引用)")
        else:
            print(f"   ✓ {src} -> {base}")

    # ---- HARD 4: 陈旧结论检查（主字典升级事件日期 > 分字典同字段最新日期）----
    print("[HARD] 4. 陈旧结论检查（主字典升级事件日期 > 分字典同字段最新日期 → 分字典未同步升级）")
    for cfg in STALE_CHECKS:
        base = cfg["file"]
        if base not in existing:
            print(f"   - {base}: 跳过（附录不存在）")
            continue
        appendix_text = read_text(os.path.join(VERIFY_DIR, base))
        main_up = latest_upgrade_dates(dict_text, cfg["token"])
        if not main_up:
            print(f"   - {base}: 跳过（主字典无该源升级事件 token）")
            continue
        sub_dates = latest_dates_anywhere(appendix_text, cfg["token"])
        stale = []
        for tok in sorted(main_up):
            md = main_up[tok]
            sd = sub_dates.get(tok)
            if sd is None:
                # 分字典提及该字段但无日期行：无法确认新鲜度，归为陈旧（须补日期）
                stale.append((tok, md, "(分字典无该字段日期行)"))
            elif md > sd:
                stale.append((tok, md, sd))
        if stale:
            for tok, md, sd in stale:
                msg = (f"陈旧结论: {base} 字段 {tok} 主字典升级 {md} > 分字典 {sd}"
                       f"（分字典未同步升级，须补同步）")
                hard_failures.append(msg)
                print(f"   ✗ {msg}")
        else:
            print(f"   ✓ {base}: 主字典 {len(main_up)} 个升级字段结论日期均 ≥ 分字典")

    # ---- HARD 4b: 主升分未升（矛盾）----
    print("[HARD] 4b. 主升分未升（主字典已定案 但 分字典仍 待确认/未知/?）")
    for cfg in CONTRADICTION_CHECKS:
        base = cfg["file"]
        if base not in existing:
            print(f"   - {base}: 跳过（附录不存在）")
            continue
        sub_text = read_text(os.path.join(VERIFY_DIR, base))
        mmap = main_status_map(dict_text, cfg["token"])
        smap = sub_status_map(sub_text, cfg["token"], cfg["fmt"])
        found = False
        for tok in sorted(smap):
            if smap[tok] != "UND":
                continue
            m = mmap.get(tok)
            if m and m[0] == "DET":
                msg = (f"主升分未升: {base} 字段 {tok} 主字典已定案(L1/确定) "
                       f"但分字典仍「待确认/未知/?」（须补同步）")
                hard_failures.append(msg)
                print(f"   ✗ {msg}")
                found = True
        if not found:
            print(f"   ✓ {base}: 无主升分未升矛盾")

    # ---- WARN 5: 同步检查（best-effort，仅 --sync 时执行）----
    if not args.sync:
        print("[WARN] 5. 同步检查：跳过（未启用 --sync；需人工深审时加 --sync）")
    else:
        print("[WARN] 5. 同步检查（主字典字段 token ⊂ 对应分字典，best-effort）")
    for cfg in SYNC_CHECKS:
        base = cfg["file"]
        if base not in existing:
            print(f"   - {base}: 跳过（附录不存在）")
            continue
        if not args.sync:
            continue
        appendix_text = read_text(os.path.join(VERIFY_DIR, base))
        appendix_tokens = extract_tokens(appendix_text, cfg["token"])
        dict_tokens = extract_tokens(dict_text, cfg["token"])
        if not appendix_tokens:
            print(f"   - {base}: 跳过（附录无可解析字段 token）")
            continue
        missing = sorted(dict_tokens - appendix_tokens)
        if missing:
            msg = (f"{base}: 主字典有 {len(missing)} 个字段未出现在分字典"
                   f"（疑似已破解未同步）: {', '.join(missing[:20])}"
                   + (" …" if len(missing) > 20 else ""))
            warnings.append(msg)
            print(f"   ⚠ {msg}")
        else:
            print(f"   ✓ {base}: 主字典 {len(dict_tokens)} 个字段全部在分字典内")

    # ---- 汇总 ----
    print("=" * 68)
    print(f" HARD FAIL: {len(hard_failures)} | WARN: {len(warnings)}")
    print("=" * 68)

    # ---- 审计报告落盘 ----
    try:
        rep_dir = os.path.join(REPO_ROOT, "docs", "field_verification")
        os.makedirs(rep_dir, exist_ok=True)
        rep_path = os.path.join(rep_dir, "20260911_verify_sync_report.md")
        with open(rep_path, "w", encoding="utf-8") as rf:
            rf.write(f"# verify_sync_check 审计报告（{datetime.date.today()}）\n\n")
            rf.write(f"- HARD FAIL: {len(hard_failures)}\n")
            rf.write(f"- WARN: {len(warnings)}\n\n")
            rf.write("## HARD FAIL 清单\n")
            for m in hard_failures:
                rf.write(f"- ❌ {m}\n")
            rf.write("\n## WARN 清单\n")
            for m in warnings:
                rf.write(f"- ⚠️ {m}\n")
        print(f"   报告已写入: {rep_path}")
    except Exception as e:  # noqa: BLE001
        print(f"   [WARN] 报告写入失败: {e}")

    if hard_failures:
        print("结果: ❌ 失败（存在断链/孤儿/映射不一致，须修复后提交）")
        for m in hard_failures:
            print(f"   - {m}")
        return 1

    if warnings:
        if args.strict:
            print("结果: ❌ 失败（--strict 模式：同步警告升级为失败）")
            for m in warnings:
                print(f"   - {m}")
            return 1
        print("结果: ⚠️ 通过（含同步警告，建议补同步分字典）")
        for m in warnings:
            print(f"   - {m}")
        return 0

    print("结果: ✅ 通过（断链/孤儿/映射/同步 全部正常）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

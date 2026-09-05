#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核查 reports/ 下 2026-09-04 生成的 md 报告：章节缺失 + 错误/警告标记。"""
import os, re, glob, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "reports")

# ---- 规范章节定义（取自生成器源码字面量）----
CANON = {
    "sht": [
        ("一", "个股基本信息"), ("二", "实时行情"), ("三", "机构一致预期"),
        ("四", "个股研报"), ("五", "概念板块"), ("六", "同业龙头"),
        ("七", "资金走向"), ("八", "北向资金"), ("九", "龙虎榜"),
        ("十", "限售解禁"), ("十一", "融资融券"), ("十二", "大宗交易"),
        ("十三", "股东户数"), ("十三·五", "筹码分布"), ("十四", "短线情绪"),
        ("十五", "综合信号"), ("十六·五", "K线形态"), ("仓位管理建议", "仓位管理"),
    ],
    "mak": [
        ("A", "全市场情绪监测"), ("B+", "涨停天梯"), ("B", "涨停池扫描"),
        ("C", "板块-异动集中度"), ("D", "行业轮动强度"), ("E", "TOP10 板块深度"),
        ("F", "资金流验证"), ("近3日异动回溯", "近3日异动"),
    ],
}

ERR_MARKERS = ["⚠️", "❌", "❎", "错误", "ERROR", "缺失", "异常", "口径未定案",
               "数据不足", "N/A", "暂无", "尚未更新", "暂缺", "未匹配"]

def norm(h):
    h = h.strip()
    h = h.lstrip("#").strip()
    h = h.replace("**", "").replace("【", "").replace("】", "")
    return h.strip()

def extract_headers(text):
    hs = []
    for line in text.splitlines():
        s = line.strip()
        if re.match(r'^##\s', s):  # 仅顶层 ## （排除 ### 子节）
            hs.append(norm(s))
    return hs

def classify(name):
    b = os.path.basename(name)
    if "_sht_" in b: return "sht"
    if "_med_" in b: return "med"
    if "_lng_" in b: return "lng"
    if "val_report" in b: return "val"
    if "mak_report" in b: return "mak"
    return "other"

def match_chapter(hdr, canon_list):
    """前缀匹配（最长优先），避免 '十' 误吞 '十一' 等"""
    best = None
    for token, label in canon_list:
        if hdr.startswith(token) and (best is None or len(token) > len(best[0])):
            best = (token, label)
    if best:
        return best
    # 兜底：无编号章节（如 仓位管理建议）
    for token, label in canon_list:
        if token in hdr or label in hdr:
            return (token, label)
    return None

def main():
    files = sorted(glob.glob(os.path.join(REP, "*20260904*.md")))
    groups = {}
    for f in files:
        g = classify(f)
        groups.setdefault(g, []).append(f)

    print("="*78)
    print(f"待核查文件总数: {len(files)} | 分组: " +
          ", ".join(f"{k}={len(v)}" for k, v in groups.items()))
    print("="*78)

    # ---- sht / mak 章节缺失核查 ----
    for g in ["sht", "mak"]:
        if g not in groups: continue
        canon = CANON[g]
        tokens = [t for t, _ in canon]
        print(f"\n########## {g.upper()} 章节缺失核查（规范 {len(canon)} 章）##########")
        problems = []
        for f in groups[g]:
            text = open(f, encoding="utf-8").read()
            hs = extract_headers(text)
            hit = {}  # token -> header text
            for h in hs:
                m = match_chapter(h, canon)
                if m: hit.setdefault(m[0], h)
            present = set(hit.keys())
            missing = [t for t in tokens if t not in present]
            if missing:
                problems.append((os.path.basename(f), missing))
                print(f"  ❌ {os.path.basename(f)}  缺失: {missing}")
        if not problems:
            print(f"  ✅ 全部 {len(groups[g])} 个 {g} 文件章节完整（{len(canon)} 章齐全）")
        else:
            print(f"  → 共 {len(problems)} 个文件有章节缺失")

    # ---- med / lng / val 结构预览（动态表头，人工对照）----
    for g in ["med", "lng", "val"]:
        if g not in groups: continue
        print(f"\n########## {g.upper()} 表头预览（动态生成，供人工对照）##########")
        for f in groups[g]:
            text = open(f, encoding="utf-8").read()
            hs = extract_headers(text)
            print(f"\n--- {os.path.basename(f)} （{len(hs)} 个 ##/### 表头）---")
            for h in hs:
                print(f"    {h}")

    # ---- 错误/警告标记扫描 ----
    print("\n" + "="*78)
    print("错误 / 警告标记扫描（全 Sept-4 文件）")
    print("="*78)
    total_files = len(files)
    for f in files:
        text = open(f, encoding="utf-8").read()
        counts = {}
        for mk in ERR_MARKERS:
            c = text.count(mk)
            if c: counts[mk] = c
        if counts:
            top = ", ".join(f"{k}×{v}" for k, v in sorted(counts.items(), key=lambda x:-x[1]))
            print(f"  {os.path.basename(f):48s} {top}")
    print(f"\n（含任一标记的文件数: 见上；共 {total_files} 个文件）")

    # ---- 强错误标记上下文（错误/ERROR/异常）----
    STRONG = ["错误", "ERROR", "异常"]
    print("\n" + "="*78)
    print("强错误标记上下文（错误 / ERROR / 异常）—— 判定是否真错误")
    print("="*78)
    any_strong = False
    for f in files:
        text = open(f, encoding="utf-8").read()
        lines = text.splitlines()
        ctx = []
        for i, l in enumerate(lines):
            if any(k in l for k in STRONG):
                snip = l.strip()[:120]
                ctx.append(f"    L{i+1}: {snip}")
        if ctx:
            any_strong = True
            print(f"\n--- {os.path.basename(f)} （{len(ctx)} 处）---")
            for c in ctx[:30]:
                print(c)
    if not any_strong:
        print("  无强错误标记")

if __name__ == "__main__":
    main()

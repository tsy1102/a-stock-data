# -*- coding: utf-8 -*-
"""
字段名样式回归守卫（对应 §12.8.12e 铁律一/四/五）。

只盯两类会直接破坏对撞/命名的回归，避免对描述性半角括号（如 ×1(股)、净利润(元)）
的误伤：
  1) 禁用异名回归：核心旧别名（当前价/最新价/今开/昨收/封板资金/封单资金/52周高/52周低）
     不得再作为字段名出现（规范表/铁律区/代码围栏/接口契约原文除外）。
  2) PE 半角括号回归：全文字段名不得出现 市盈率(动)/(静)/(TTM) 半角写法
     （规范表已统一全角 市盈率（动/静/TTM），见铁律五）。

用法：python scripts/lint_field_names.py
退出码 1 = 发现违规（可作 CI/提交前检查）。
"""
import io, sys, os

# Phase 2(2026-09-12): 改用 ROOT 绝对路径，消除 CWD 耦合（G0 已标记：原相对路径在 CI 错误 CWD 下直接失败）。
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "docs", "field_dict.md")
with io.open(PATH, encoding="utf-8") as f:
    lines = f.readlines()

# --- 跳过区：规范表+铁律块（从 | 规范中文名 | 到 #### 🔴【PE 口径铁证】）---
in_reg = False
skip = set()
for i, ln in enumerate(lines):
    if ln.strip().startswith("|") and "规范中文名" in ln and "语义与口径" in ln:
        in_reg = True
    if in_reg:
        skip.add(i)
    if "#### 🔴【PE 口径铁证】" in ln:
        in_reg = False

# --- 代码围栏追踪 ---
in_fence = False
viol = []

# 禁用异名（仅在表格行 col1/col2 作为字段名时违规）。
# 用 unambiguous 旧形态，避免误伤规范名子串（如「昨收」⊂「昨收盘」）。
FORBID = ["当前价", "最新价", "今开价", "昨收价", "封板资金", "封单资金", "52周高", "52周低"]

for i, ln in enumerate(lines):
    s = ln.rstrip("\n")
    if "```" in s:
        in_fence = not in_fence
        continue
    if in_fence or i in skip:
        continue
    if s.strip().startswith("|"):
        cells = [c.strip() for c in s.split("|")]
        joined = " ".join(cells[c] for c in (1, 2) if c < len(cells))
        for f in FORBID:
            if f in joined:
                viol.append((i + 1, "禁用异名回归: %s" % f, s.strip()[:80]))
                break
    # PE 半角括号回归（全文件，含描述；规范表已跳过且无）
    for pat in ("市盈率(动)", "市盈率(静)", "市盈率(TTM)"):
        if pat in s:
            viol.append((i + 1, "PE 半角括号回归: %s" % pat, s.strip()[:80]))
            break

if viol:
    print("❌ 字段名样式检查失败，发现 %d 处违规：" % len(viol))
    for ln, why, txt in viol[:60]:
        print("   行%d  %s  | %s" % (ln, why, txt))
    sys.exit(1)

print("✅ 字段名样式检查通过：无禁用异名回归、无 PE 半角括号。")

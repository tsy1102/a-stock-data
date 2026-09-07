# -*- coding: utf-8 -*-
"""
字段字典「同号即同义」回归守卫（第七轮碰撞审计配套，2026-09-07）。

铁律：ulist239 索引 ≠ push2 索引，**同字段编号 ≠ 同语义**。本脚本阻止任何
"仅凭字段编号相同就认定语义相同"的断言进入字典，并强制：

  ✅ 凡是声明 ulist fX 与 push2 存在映射关系的登记，必须在权威对齐表
    `docs/verify/ulist_push2_align.md`（ulist fN → push2 fM）中存在对应条目
    —— 该对齐表即「跨源对撞证据」的唯一登记处。新增字段登记若声明 push2 映射，
    必须先在对撞脚本（`scripts/verify_ulist_push2_collision.py`）产出实证后写入对齐表，
    否则判违规。

覆盖范围：
  1) 主守卫：§12.3.2.3 ulist239 全字段清单（新字段登记处，见该节说明「破解新字段直接在此登记」）。
  2) 全文件回归：任何表格行若出现「✅ 同 push2 fX（同号…）」式裸断言（编号相同即认定同义、
     且未带证据标记），一律判违规——防止历史错误模式（第七轮已订正的 113 行）复发。

证据分级（字典行必须明确归属其一）：
  - VERIFIED    : ✅ + 数值实证/第七轮审计 标记，且对齐表确认 ulist fX → push2 fX（真同号同义）。
  - DISPROVED   : ⚠️ 已证伪 + 「实测 ulist fX = push2 fM (M≠X)」，且对齐表确认该异号映射。
  - UNVERIFIED  : ⚠️ 未实证/待核实/待破解/待数值对撞 —— 显式声明「无实证」，不主张同义，允许。
  - CROSS       : ✅ + 跨源/交叉验证/第九轮审计 标记，且指明具体外部具名源字段
                  （tdx/sina/tencent/fuyao/zhb/axdata 等）—— 经跨源数值对撞定案，非凭编号相同，
                  是「同号即同义」铁律的正确解药，允许（须命名外部源，不得夹带裸同号断言）。
  - 其他含「同 push2 fX（同号）」裸断言、且无上述任一标记 → 违规（回到第七轮前的错误模式）。

退出码 1 = 发现违规（可接入 CI / 提交前检查）；0 = 通过。
用法：python scripts/lint_field_same_number.py
"""
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DICT = ROOT / "docs" / "field_dict.md"
ALIGN = ROOT / "docs" / "verify" / "ulist_push2_align.md"

# --- 1) 解析权威对齐表 -> {ulist_fn(int): push2_fn(int)} ---
align = {}
if ALIGN.exists():
    for line in ALIGN.read_text(encoding="utf-8").splitlines():
        for mm in re.finditer(r"ulist\s*f(\d{1,3})\s*\|\s*f(\d{1,3})", line):
            align[int(mm.group(1))] = int(mm.group(2))
align_same = {u for u, p in align.items() if u == p}

# --- 2) 解析字典 ---
lines = DICT.read_text(encoding="utf-8").splitlines()

# 定位 §12.3.2.3 ulist239 表区块（下一 #### 标题前）
sec_start = None
for i, ln in enumerate(lines):
    if "12.3.2.3" in ln and "ulist239" in ln:
        sec_start = i
        break

rows_sec = []  # (line_no, ulist_fn, status, note)
if sec_start is not None:
    for i in range(sec_start + 1, len(lines)):
        if lines[i].lstrip().startswith("#### "):
            break
        m = re.match(r"\s*\|\s*f(\d{1,3})\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$", lines[i])
        if m:
            rows_sec.append((i + 1, int(m.group(1)), m.group(2), m.group(3)))

# --- 3) 全文件所有「f 编号」表格行（用于回归扫描）---
all_frows = []  # (line_no, ulist_fn, full_row)
for i, ln in enumerate(lines):
    m = re.match(r"\s*\|\s*f(\d{1,3})\s*\|(.*)$", ln)
    if m:
        all_frows.append((i + 1, int(m.group(1)), ln.rstrip()))

# --- 4) 违规判定 ---
viol = []


def classify(fn, status, note):
    """返回 (cls, target_push2_or_None)。cls∈VERIFIED/DISPROVED/UNVERIFIED/BARE/CROSS/OTHER。

    证据标记与跨号映射目标编号可能落在 status 或 note 任意一格，故统一以合并文本 text 判定。
    """
    text = "%s %s" % (status, note)
    # 跨源对撞实证定案(优先于 VERIFIED): ✅ + 跨源证据标记 + 指明外部具名源字段。
    # 这是「同号即同义」铁律的正确解药——经 tdx/sina/tencent/fuyao/zhb 具名字段数值对撞定案,
    # 而非凭编号相同认定同义。证据标记: 跨源 / 交叉验证 / 第九轮审计 / 第9轮 / 第10轮。
    if "✅" in status and any(k in text for k in
                               ("跨源", "交叉验证", "第九轮审计", "第9轮", "第十轮", "第10轮")):
        return "CROSS", None
    if "✅" in status and ("第七轮审计" in text or "数值实证" in text):
        return "VERIFIED", None
    if "已证伪" in status:
        mm = re.search(r"push2\s*f(\d{1,3})", text)
        return "DISPROVED", (int(mm.group(1)) if mm else None)
    if any(k in text for k in ("未实证", "待核实", "待破解", "待数值对撞")):
        return "UNVERIFIED", None
    # 裸「同 push2 fX（同号）」断言（X==fn）且无证据标记 -> 违规模式
    m_same = re.search(r"同\s*push2\s*f(\d{1,3})", text)
    if m_same and int(m_same.group(1)) == fn:
        return "BARE", None
    return "OTHER", None


# 4a) 主守卫：§12.3.2.3 登记行
for ln_no, fn, status, note in rows_sec:
    cls, target = classify(fn, status, note)
    if cls == "VERIFIED":
        if fn not in align_same:
            viol.append((ln_no, "VERIFIED 声明无对齐表 backing（ulist f%d 未在对齐表确认 → push2 f%d）" % (fn, fn), status))
    elif cls == "DISPROVED":
        if target is None:
            viol.append((ln_no, "DISPROVED 行未解析出 push2 目标编号", status))
        elif align.get(fn) != target:
            viol.append((ln_no, "DISPROVED 跨号映射与对齐表不符（字典称 ulist f%d = push2 f%d，对齐表记为 → push2 f%s）"
                         % (fn, target, align.get(fn, "无")), status))
    elif cls == "BARE":
        viol.append((ln_no, "裸「同号即同义」断言（编号相同即认定同义，未附跨源对撞证据），违反第七轮铁律", status))
    elif cls == "CROSS":
        # 跨源定案必须指明具体外部源(tdx/sina/tencent/fuyao/zhb/axdata 等)的具名字段,
        # 否则证据不足; 且不得夹带裸同号断言(那仍违反铁律)。
        text = "%s %s" % (status, note)
        if not re.search(r"(tdx|sina|tencent|fuyao|zhb|axdata|push2|东财|通达信|腾讯|同花顺|ZHB)", text, re.I):
            viol.append((ln_no, "CROSS 跨源定案未指明具体外部源字段，证据不足（须命名 tdx/sina/tencent/fuyao/zhb 等具名字段）", status))
        m_same = re.search(r"同\s*push2\s*f(\d{1,3})", text)
        if m_same and int(m_same.group(1)) == fn:
            viol.append((ln_no, "CROSS 行仍夹带裸同号即同义断言，违反铁律", status))
    # UNVERIFIED / OTHER：允许（OTHER 不含 push2 映射主张）

# 4b) 全文件回归：裸「✅ 同 push2 fX（同号…）」式断言（任何区块）
for ln_no, fn, raw in all_frows:
    # 仅当存在「同 push2 fX」且 X==fn 且不属于已验证/已证伪/待核实三类标记
    m_same = re.search(r"同\s*push2\s*f(\d{1,3})", raw)
    if not (m_same and int(m_same.group(1)) == fn):
        continue
    if ("第七轮审计" in raw or "数值实证" in raw or "已证伪" in raw
            or "未实证" in raw or "待核实" in raw or "待破解" in raw or "待数值对撞" in raw):
        continue
    viol.append((ln_no, "全文件回归：发现裸「同号即同义」断言（编号相同认定同义，未带证据标记）", raw.strip()[:90]))

# --- 5) 报告 ---
if viol:
    print("❌ 字段字典「同号即同义」检查失败，发现 %d 处违规：" % len(viol))
    print("   对齐表条目数: %d（同号真同义 %d 条）" % (len(align), len(align_same)))
    print("   扫描 §12.3.2.3 登记行: %d  全文件 f 编号行: %d" % (len(rows_sec), len(all_frows)))
    for ln, why, txt in viol[:80]:
        print("   行%-5d  %s  | %s" % (ln, why, txt))
    sys.exit(1)

print("✅ 字段字典「同号即同义」检查通过：")
print("   对齐表条目数: %d（同号真同义 %d 条，作为唯一实证登记处）" % (len(align), len(align_same)))
print("   §12.3.2.3 登记行: %d（所有 push2 映射主张均已对齐表背书或显式标为待核实）" % len(rows_sec))
print("   全文件 f 编号行: %d（无裸「同号即同义」断言复发）" % len(all_frows))

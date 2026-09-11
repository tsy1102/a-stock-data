# -*- coding: utf-8 -*-
"""L3 前置防护 Dry-Run（只读）：P1 token×固化 diff / P2 HARD4 升级叙事覆盖 / P3 §零·B 标记。
不修改主字典，仅产出报告 docs/field_verification/20260911_L3_preflight_dryrun.md。
数据来源：docs/field_dict.md 实测。"""
import re

P = "docs/field_dict.md"
lines = open(P, encoding="utf-8").read().split("\n")

# 搬迁区（1-index 闭区间，来自 L3_archive_plan.md §1.2 精确行号）
MOVE = [(947, 1152), (1153, 1203), (4398, 5540)]  # §七 / §八 / §三

def in_range(one_idx):
    for a, b in MOVE:
        if a <= one_idx <= b:
            return True
    return False

keep_lines = [l for i, l in enumerate(lines, 1) if not in_range(i)]
move_lines = [l for i, l in enumerate(lines, 1) if in_range(i)]
keep_text = "\n".join(keep_lines)
move_text = "\n".join(move_lines)

# token 提取：fNN 与 [NN]，排除 Col[数字]（ZHB 列，非注册表 token）
TOK = re.compile(r'(?<!Col)\b\[(\d{1,3})\]|(?<!Col)f(\d{1,3})\b')

def tokens(text):
    out = {}
    for m in TOK.finditer(text):
        t = m.group(1) or m.group(2)
        out[t] = out.get(t, 0) + 1
    return out

mt = tokens(move_text)
kt = tokens(keep_text)

# 闸门原版 UPGRADE_EVENT_RE（来自 verify_sync_check.py latest_upgrade_dates）
UPG = re.compile(r"主动升级|非对撞升级|主动性破解升级|升级定案方向|→Beta族高置信|→均价/VWAP类价格派生候选强|候选=委差")

# 定案等级词（判断"保留区是否含状态声明"）
LEVEL = re.compile(r'\b(L[1-4]|✅|≡|等价|身份确认|定案|未知|占位符|恒空|恒0|❓|🟢|🔥|L1-U|L3 价格类候选强|升格|撤销|回退)')

def tok_in_text(t, text):
    return list(re.finditer(r'(?<!Col)\b\[?' + re.escape(t) + r'\]?', text))

# ---- P1 ----
p1_need_port = []      # 保留区零提及
p1_mention_only = []   # 保留区提及但附近无等级词
for t in sorted(mt, key=lambda x: int(x)):
    cnt_m = mt[t]
    cnt_k = kt.get(t, 0)
    if cnt_k == 0:
        p1_need_port.append((t, cnt_m))
    else:
        has_level = False
        for m in tok_in_text(t, keep_text):
            s = max(0, m.start() - 90)
            e = min(len(keep_text), m.end() + 90)
            if LEVEL.search(keep_text[s:e]):
                has_level = True
                break
        if not has_level:
            p1_mention_only.append((t, cnt_m, cnt_k))

# ---- P2 ----
p2_leak = []
for l in move_lines:
    if not UPG.search(l):
        continue
    for m in TOK.finditer(l):
        t = m.group(1) or m.group(2)
        leak = True
        for kl in keep_lines:
            if UPG.search(kl) and tok_in_text(t, kl):
                leak = False
                break
        if leak and t not in p2_leak:
            p2_leak.append(t)

# ---- P3 ----
gen_mark = "<!-- GEN:field-matrix -->" in keep_text
zero_b_in_move = "<!-- GEN:field-matrix -->" in move_text

# P1 补充：mention_only 整行复核（90 字符窗口可能过窄，长表格行等级词在行尾）
p1_still = []
for t, c, k in p1_mention_only:
    if not any(LEVEL.search(kl) for kl in keep_lines if tok_in_text(t, kl)):
        p1_still.append((t, c, k))

# ---- 报告 ----
R = []
R.append("# L3 前置防护 Dry-Run 报告（2026-09-11）")
R.append("")
R.append("> 只读校验，不修改主字典。数据来源：通达信字段破解文档 `docs/field_dict.md` 实测。不构成投资建议。")
R.append("")
R.append("## 0. 范围")
R.append(f"- 搬迁区(§七+§八+§三)合计: {sum(b-a+1 for a,b in MOVE)} 行")
R.append(f"- 保留区(去掉搬迁区后): {len(keep_lines)} 行")
R.append("")
R.append("## 1. P1｜token×固化 diff（搬迁区 fNN/[NN] vs 保留区）")
R.append(f"- 搬迁区 fNN/[NN] token 种类数: **{len(mt)}**")
R.append(f"- **需在迁移前 port 进注册表的 token（保留区零提及）: {len(p1_need_port)}**")
for t, c in p1_need_port:
    R.append(f"  - `[{t}]`/`f{t}`：搬迁区 {c} 次，保留区 0 次 → 须先固化进 §12.8.12e 再迁")
R.append(f"- 保留区仅提及、90字符窗口无等级词（初筛黄）: {len(p1_mention_only)}；整行复核后仍无定案等级词: **{len(p1_still)}**")
for t, c, k in p1_still[:60]:
    R.append(f"  - `[{t}]`/`f{t}`：搬迁区 {c} 次 / 保留区 {k} 次，保留区整行无定案等级词 → 须人工核对是否漏固化")
R.append("")
R.append("## 2. P2｜HARD4 升级叙事覆盖复算（闸门 UPGRADE_EVENT_RE 原版口径）")
R.append(f"- **迁移后闸门静默漏检 token: {len(p2_leak)}**")
if p2_leak:
    for t in p2_leak:
        R.append(f"  - `[{t}]`/`f{t}`：搬迁区有升级事件，保留区无 → 漏检")
else:
    R.append("  - 无（与 L3_archive_plan §0 实测漏检=0 一致）")
R.append("")
R.append("## 3. P3｜§零·B 标记（gen_field_matrix.py 依赖）")
R.append(f"- `<!-- GEN:field-matrix -->` 位于保留区且在位: **{gen_mark}**（搬迁区含该标记: {zero_b_in_move}）")
R.append("")
R.append("## 4. 结论")
if not p1_need_port and not p2_leak and gen_mark and not p1_still:
    R.append("- **P1+P2+P3 全过，无阻塞**：所有搬迁区 token 已在保留区固化（整行复核确认）；闸门升级叙事零漏检；§零·B 标记在位。可进入正式迁移。")
elif p1_still:
    R.append(f"- **存在需先处置项**：P1 整行复核仍 {len(p1_still)} 个 token 在保留区无定案等级词，须先人工核对/固化再迁移。")
elif p1_need_port or p2_leak:
    R.append(f"- **存在需先处置项**：P1 需 port {len(p1_need_port)} 个 token、P2 漏检 {len(p2_leak)} 个 token，须先固化再迁移。")
else:
    R.append("- P3 异常（§零·B 标记缺失），须先定位。")

open("docs/field_verification/20260911_L3_preflight_dryrun.md", "w", encoding="utf-8").write("\n".join(R))

print("P1 need_port:", len(p1_need_port), p1_need_port[:20])
print("P1 mention_only:", len(p1_mention_only), [t for t,_,_ in p1_mention_only][:20])
print("P2 leak:", len(p2_leak), p2_leak)
print("P3 zero_b(keep):", gen_mark, "in_move:", zero_b_in_move)
print("move_lines:", sum(b-a+1 for a,b in MOVE), "keep_lines:", len(keep_lines), "move_tokens:", len(mt))

# -*- coding: utf-8 -*-
"""确定性回写 2026-09-12 破解定案到 field_dict.md（含断言防静默丢改）。"""
import os
import sys

PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "docs", "field_dict.md")

with open(PATH, "r", encoding="utf-8") as f:
    s = f.read()

# ── (1) Col[22] 定案（行 26）──
OLD_COL22 = "> Col[22] 需通达信官方文档或更大样本。"
NEW_COL22 = ("> **Col[22] = `shape_value` 个股形态/板块代码（TDX 官方 TdxQuant 确认，"
             "5–6 位动态分类码，日更；完整码表枚举待补，属源覆盖盲区）**——性质已于 "
             "2026-09-12 经 31 日快照结构实证 + 跨日聚类升 L1（见 "
             "`docs/field_verification/20260912_zhb_col22_crack.md`）。")
assert OLD_COL22 in s, "Col[22] 旧锚未命中"
s = s.replace(OLD_COL22, NEW_COL22, 1)

# ── (2) ulist f1–f34 中 21 个 L1 定案候选 ──
# (ulist fX ↔ push2 fYY 异号同义；多日精确对撞 23 批次 median|Δ|=0, max|Δ|≤0.19)
L1 = {
    "f1":  ("f59",  "枚举(全市场恒=2,非市场码)"),
    "f3":  ("f170", "涨跌幅%(=push2 f170)"),
    "f4":  ("f169", "涨跌额(=push2 f169)"),
    "f5":  ("f47",  "成交量(=push2 f47)"),
    "f6":  ("f48",  "成交额(=push2 f48)"),
    "f7":  ("f171", "量比(=push2 f171)"),
    "f8":  ("f168", "=push2 f168"),
    "f9":  ("f162", "连续(=push2 f162)"),
    "f10": ("f50",  "连续(=push2 f50)"),
    "f15": ("f44",  "最高价(=push2 f44)"),
    "f16": ("f45",  "最低价(=push2 f45)"),
    "f17": ("f46",  "开盘价(=push2 f46)"),
    "f18": ("f60",  "昨收盘价(=push2 f60)"),
    "f19": ("f111", "板级枚举{2,6,23,80,81}(=push2 f111)"),
    "f23": ("f167", "连续(=push2 f167)"),
    "f24": ("f121", "连续(=push2 f121)"),
    "f25": ("f122", "连续(=push2 f122)"),
    "f26": ("f189", "上市日期(枚举,YYYYMMDD)(=push2 f189)"),
    "f29": ("f180", "枚举(=push2 f180)"),
    "f33": ("f191", "连续(=push2 f191)"),
    "f34": ("f49",  "枚举(=push2 f49)"),
}

done = 0
for fn, (fy, meaning) in L1.items():
    old = f"| {fn} | ⚠️ ulist 专属 · 待破解 | np/get 返回但未破解（恒空/恒0 亦照登） |"
    assert old in s, f"ulist {fn} 旧行未命中"
    new = (f"| {fn} | ✅ **跨源定案·异号同义**：ulist {fn} ↔ push2 {fy}（多日精确对撞 L1："
           f"23 批次 / median|Δ|=0 / max|Δ|≤0.19，见 `docs/field_verification/20260912_ulist_collision.md`）"
           f" | {meaning} |")
    s = s.replace(old, new, 1)
    done += 1
assert done == 21, f"L1 写入数={done}"

# ── (3) 尾部统计块一致性（进度指示，非精确划分）──
OLD_STAT = ("> 统计：共 **239** 字段｜✅ 已破解 **127**（经 2026-09-09 P0-a 订正：原记 131，"
            "扣除 f49/f133/f135/f221 四字段其 §12.3 行仍 ⚠️/待破解、未实际升 ✅；详见下方订正注）"
            "｜⚠️ ulist 专属待破解 **119**（115 + 上述 4 回归待破解）。")
NEW_STAT = ("> 统计：共 **239** 字段｜✅ 已破解 **148**（127 + 2026-09-12 增 21：ulist f1–f34 中 "
            "21 个经 23 批次精确对撞升 L1，见 `docs/field_verification/20260912_ulist_collision.md`）"
            "｜⚠️ ulist 专属待破解 **98**（119 − 本轮 21；进度指示非精确划分）。")
assert OLD_STAT in s, "统计块旧锚未命中"
s = s.replace(OLD_STAT, NEW_STAT, 1)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(s)
print(f"OK: Col[22]+{done} ulist L1 + 统计块 已回写 field_dict.md")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collision_rules.py — 对撞四铁律 + 定案状态机（对撞破解运行时规则真相源）

每次运行对撞破解脚本（scripts/crack_*.py）时，由脚本在入口调用
``print_active_rules()`` 自动「查询」本规则并打印横幅，确保破解严格遵循
下方硬阈值与判定逻辑，而非依赖记忆或散落注释。

设计要点
--------
- 以本文件的 Python 常量为**唯一权威**（single source of truth）；
  人读文档 ``docs/field_verification/COLLISION_RULES.md`` 由本模块派生
  （``python scripts/collision_rules.py --emit``），避免双源漂移。
- ``print_active_rules()`` 默认输出到 **stderr**，不污染对撞脚本自身的
  stdout 报告（报告通常重定向到 .md）。

用法
----
    python scripts/collision_rules.py            # 打印规则横幅（stderr）
    python scripts/collision_rules.py --emit     # 派生 COLLISION_RULES.md
在对撞脚本入口：
    from collision_rules import print_active_rules
    if __name__ == "__main__":
        print_active_rules()   # 每次运行自动查询规则
        main()
"""
from __future__ import annotations

import os
import sys
from datetime import date

# ───────────────────────────────────────────────────────────────────────
# 对撞四铁律（硬阈值，不可在脚本内随意下调）
# ───────────────────────────────────────────────────────────────────────
# 1. 精度对齐
PRECISION = "|a−b| ≤ max(ulp_a, ulp_b)（舍入感知）；整数/枚举降级为严格 1e-9"
# 2. 命中率分层
HIT_RATE_L1 = 18          # 每采样日 ≥18/20 且可解释 → L1 定案
HIT_RATE_L4 = 8           # 8~17 → L4 候选（存疑）
# 3. 比值族（单位换算定案）
RATIO_CV_MAX = 1e-4       # 变异系数阈值（CV = std/mean）
RATIO_STEPS = (10, 100, 1000, 10000)   # 合法单位换算比集合
# 4. 多日复核
MULTI_DAY_MIN = 3         # 至少 3 个独立采集日重复方可定案
# 5. 相关性仅生成候选
CORR_SPEARMAN_MIN = 0.6   # |Spearman| 阈值；且需 Pearson+Spearman 同号 + 留一法不翻号

# ───────────────────────────────────────────────────────────────────────
# 定案状态机 L1~L4（升格路径与含义）
# ───────────────────────────────────────────────────────────────────────
LEVELS = [
    ("L1", "定案（最高置信）", "多源对撞实锤，四铁律全满足"),
    ("L2", "官方/强锚定", "fuyao 官方三表锚 / TDX 官方命名语义终止器"),
    ("L3", "方向确证·覆盖不完整", "H12 实测方向对、样本不全"),
    ("L4", "候选存疑", f"命中率 {HIT_RATE_L4}~{HIT_RATE_L1 - 1}，仅候选"),
]

# ───────────────────────────────────────────────────────────────────────
# 不对撞（跳过）规则
# ───────────────────────────────────────────────────────────────────────
SKIP_IDENTIFIERS = ["market", "code", "date", "name", "tx[1]", "tx[2]", "tx[3]"]
SKIP_CONSTANTS = ["push2:f106（恒=100）", "f123/f124/f125/f134（恒=0）"]
SKIP_RULES = [
    "已 L1 定案字段：移出 FOCUS，不再主攻；仅进全历史复核的回归保护池",
    "标识符字段（market/code/date/name/tx[1..3]）：排除出数值对撞目标，防 false L1",
    "常量占位字段（f106 恒100 / f123..f134 恒0）：无信息量，登记为占位而非未知语义",
    "20 股 ZHB 锚巧合陷阱：任何新映射若与已确立映射矛盾，判为巧合而非发现，须打印原数据人工核实",
    "相关性（Pearson/Spearman）只生成候选，绝不定案",
    f"单日 20 股快照不足以定案，须 ≥{MULTI_DAY_MIN} 个独立采集日重复",
]


def print_active_rules(stream=None):
    """运行时自动查询并打印当前生效的对撞规则横幅。

    默认输出到 stderr，以免污染对撞脚本 stdout 上的 .md 报告。
    返回被写入的流对象。
    """
    out = stream or sys.stderr
    bar = "=" * 66
    print(bar, file=out)
    print("【对撞四铁律 · 运行时生效规则】每次对撞自动查询", file=out)
    print(bar, file=out)
    print(f"1. 精度对齐 : {PRECISION}", file=out)
    print(f"2. 命中率分层: 每采样日 ≥{HIT_RATE_L1}/20 且可解释 → L1 定案；"
          f"{HIT_RATE_L4}~{HIT_RATE_L1 - 1} → L4 候选（存疑）", file=out)
    print(f"3. 比值族   : CV≤{RATIO_CV_MAX:g} 且比值∈{RATIO_STEPS} → L1-U 单位换算定案",
          file=out)
    print(f"4. 多日复核 : ≥{MULTI_DAY_MIN} 个独立采集日重复方可定案；单日快照不够", file=out)
    print(f"5. 相关性   : 仅 Pearson+Spearman 同号且 |Spearman|≥{CORR_SPEARMAN_MIN} "
          f"且留一法不翻号 → 候选，绝不定案", file=out)
    print("-" * 66, file=out)
    print("定案状态机 L1~L4:", file=out)
    for code, name, desc in LEVELS:
        print(f"  {code} {name}: {desc}", file=out)
    print("-" * 66, file=out)
    print("不对撞（跳过）规则:", file=out)
    for r in SKIP_RULES:
        print(f"  ✗ {r}", file=out)
    print(bar, file=out)
    print("⚠ L1 为当前最强结论，遇矛盾新证据可降级/重议；日常不再无故复撞。", file=out)
    print(bar, file=out)
    return out


def emit_markdown(path: str | None = None) -> str:
    """由本模块派生 COLLISION_RULES.md（与代码常量一致，避免双源漂移）。"""
    L = []
    L.append("# 对撞四铁律与定案状态机（运行时规则真相源）\n")
    L.append(f"> 本文件由 `scripts/collision_rules.py` 自动派生"
             f"（`python scripts/collision_rules.py --emit`），生成日 {date.today().isoformat()}。\n")
    L.append("> 对撞脚本运行时自动 `print_active_rules()` 查询本规则；"
             "以代码常量（`collision_rules.py`）为唯一权威，本文档为其人读镜像。\n")
    L.append("## 一、对撞四铁律（硬阈值）\n")
    L.append("| # | 铁律 | 阈值 / 判定 |")
    L.append("|:--|:--|:--|")
    L.append(f"| 1 | 精度对齐 | {PRECISION} |")
    L.append(f"| 2 | 命中率分层 | 每采样日 ≥{HIT_RATE_L1}/20 且可解释 → **L1 定案**；"
             f"{HIT_RATE_L4}~{HIT_RATE_L1 - 1} → L4 候选（存疑） |")
    L.append(f"| 3 | 比值族 | CV≤{RATIO_CV_MAX:g} 且比值∈{RATIO_STEPS} → L1-U 单位换算定案 |")
    L.append(f"| 4 | 多日复核 | ≥{MULTI_DAY_MIN} 个独立采集日重复方可定案；单日 20 股快照不够 |")
    L.append(f"| 5 | 相关性 | 仅 Pearson+Spearman 同号且 |Spearman|≥{CORR_SPEARMAN_MIN} "
             f"且留一法不翻号 → 候选，绝不定案 |\n")
    L.append("## 二、定案状态机 L1~L4\n")
    L.append("| 层级 | 名称 | 升格来源 |")
    L.append("|:--|:--|:--|")
    for code, name, desc in LEVELS:
        L.append(f"| {code} | {name} | {desc} |")
    L.append("")
    L.append("## 三、不对撞（跳过）规则\n")
    for r in SKIP_RULES:
        L.append(f"- {r}")
    L.append("")
    L.append("## 四、对撞 / 不降解撞的判定边界\n")
    L.append("- **主攻对撞（crack）**：仅对 `FOCUS` 内未定案的 residual unknowns 跑；"
             "已 **L1** 字段从攻击目标移除。")
    L.append("- **全历史复核 / 再确认（re-validation）**：全量扫描会顺带扫到已定案字段，"
             "结果标注「再确认 / 强化现有结论，未改动语义」，作为回归保护。")
    L.append("- **锁定点 = 升到 L1**：该字段转为对齐锚 / 真值参考，"
             "用于破解其他未知字段时的核对与跨源一致性校验。")
    L.append("- **双向可修正**：L1 遇矛盾新证据可降级或重议"
             "（如 tx[85] 均价候选因锚仅 3/20 回退 L3；tdxstat[31] 对撞东财仅 77% 匹配降级）。\n")
    L.append("---\n")
    L.append("> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。\n")

    text = "\n".join(L)
    if path is None:
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "docs", "field_verification", "COLLISION_RULES.md",
        )
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[collision_rules] 已派生 {path}", file=sys.stderr)
    return path


if __name__ == "__main__":
    if "--emit" in sys.argv:
        emit_markdown()
    else:
        print_active_rules()

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
from typing import TextIO, TypedDict

# ───────────────────────────────────────────────────────────────────────
# 对撞四铁律（硬阈值，不可在脚本内随意下调）
# ───────────────────────────────────────────────────────────────────────
# 1. 精度对齐
PRECISION = "|a−b| ≤ max(ulp_a, ulp_b)（舍入感知）；整数/枚举降级为严格 1e-9"
# 2. 命中率分层
HIT_RATE_L1 = 18  # 每采样日 ≥18/20 且可解释 → L1 定案
HIT_RATE_L4 = 8  # 8~17 → L4 候选（存疑）
# 3. 比值族（单位换算定案）
RATIO_CV_MAX = 1e-4  # 变异系数阈值（CV = std/mean）
RATIO_STEPS = (10, 100, 1000, 10000)  # 合法单位换算比集合
# 4. 多日复核
MULTI_DAY_MIN = 3  # 至少 3 个独立采集日重复方可定案
# 5. 相关性仅生成候选
CORR_SPEARMAN_MIN = 0.6  # |Spearman| 阈值；且需 Pearson+Spearman 同号 + 留一法不翻号

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


# ───────────────────────────────────────────────────────────────────────
# 已证伪结论护栏（2026-09-16 立规，源自对 Gemini 跨源对撞报告的实证核查）
# ───────────────────────────────────────────────────────────────────────
# 用途：把经数值实证推翻的「伪结论」固化为对撞反例，使后续自动对撞一旦产出
# 同类候选直接判伪，防止污染 field_dict.md。护栏只拒绝、不新增字段。
#   false_claim   : 伪主张原文
#   correct       : 已定案真相（L1）
#   evidence      : 可复现数值证据（采集快照 / 字典行号）
#   blocked_pairs : 若两 token 相等即代表该伪结论，collide 直接跳过
#   settled       : 该 token 语义已定，若作为对撞左字段被赋新含义即翻案，判伪
class RefutedConclusion(TypedDict):
    id: str
    false_claim: str
    correct: str
    evidence: str
    blocked_pairs: list[list[str]]
    settled: list[str]


REFUTED_CONCLUSIONS: list[RefutedConclusion] = [
    {
        "id": "R1_tencent_shares_reversed",
        "false_claim": "tencent[72]=总股本、tencent[73]=流通股本",
        "correct": "tencent[72]=A股流通股本、tencent[73]=总股本（[76]=A股流通=[72]）",
        "evidence": "raw_tencent.json 农行601288(含H股): [72]=3192.442亿 < [73]=3499.830亿 → [72]为流通、[73]为总本",
        "blocked_pairs": [["tencent[72]", "tencent[73]"]],
        "settled": ["tencent[72]", "tencent[73]"],
    },
    {
        "id": "R2_tipinfo_unlock_mislabel",
        "false_claim": "tipinfo Col[7~9]/[13~16]=限售解禁(召开日/预告日/净利润/解禁日/股数/前次解禁)",
        "correct": "Col[7]=异动日(未定)、Col[8]=分红日、Col[9]=分红金额(每10股,元)、Col[13]=股权登记日、"
        "Col[14]=配股/除权金额(万元)、Col[15]=增发事件日、Col[16]=增发募集金额(万元)",
        "evidence": "field_dict:611-635(TdxQuant实锤+单位万元)；Col[14]=25224.80与字典配股金额逐字一致",
        "blocked_pairs": [],
        "settled": [
            "tipinfo.Col[7]",
            "tipinfo.Col[8]",
            "tipinfo.Col[9]",
            "tipinfo.Col[13]",
            "tipinfo.Col[14]",
            "tipinfo.Col[15]",
            "tipinfo.Col[16]",
        ],
    },
    {
        "id": "R3_tdxstat_col22_shape",
        "false_claim": "tdxstat Col[22]=三周期(K线)走势形态复合码 A*10000+B*100+C",
        "correct": "tdxstat Col[22]=概念/热点分类码（50913/110113 等对应具体概念，tdxhy.cfg 实锤）",
        "evidence": "field_dict:26/3414 据 tdxhy.cfg 概念树定案；多位数分解对任意整数恒成立，不证形态语义",
        "blocked_pairs": [],
        "settled": ["tdxstat.Col[22]"],
    },
    {
        "id": "R4_finance_info_raw_index_shift",
        "false_claim": "eltdx finance_info_raw 槽位：总股本[1]/EPS[8]/总资产[9]/归母净利润[29] …",
        "correct": "34 槽结构正确但索引偏移+2：总股本[4]/EPS[10]/总资产[11]/归母净利润[30]；"
        "field_dict §二 0x0010 财务协议36字段表已正确收录",
        "evidence": "raw_eltdx.json 茅台600519 finance_info_raw 34浮点解析：槽[4]=125008.1562(总本)≠Gemini[1]；"
        "槽[30]=44516880(归母)≠Gemini[29]",
        "blocked_pairs": [],
        "settled": [],
    },
    {
        "id": "R5_tipinfo_col11_not_ipo",
        "false_claim": "tipinfo Col[11]=ipo_date/自由流通股本/配股比例",
        "correct": "Col[11]=最新业绩预告发布日(YYYYMMDD); 跨期跳变实证(002475 20260429->20260825 等); "
        "tdxstat Col[11]=free_ltgb 为另一文件, 与 tipinfo 不同源",
        "evidence": "20260923_tipinfo_verify.md: 002475/300497/000100 跨期跳变精确命中; 000100 H1 后转空; 非空率 0.7%",
        "blocked_pairs": [],
        "settled": ["tipinfo.Col[11]"],
    },
    {
        "id": "R7_f113xb38_not_rigid_identity",
        "false_claim": "f113 x f38 是 f58(归母) 或 f135(合并) 的刚性恒等式（比值恒 1.000000）",
        "correct": "f113=每股净资产(BPS); f113xf38 在 18/20 股精确=f58(归母BPS口径), 但高少数股东股(000568) f113 为合并BPS 使 f113xf38~=f135(合并, 比值0.9967), 600309 介于二者(1.023); 即 f113 母/合口径与快照刷新漂移 → 既不能证 f58 也不能证 f135, 禁作刚性恒等式定案",
        "evidence": "20260923 raw_ulist239 全20股扫描: f113xf38/f58 18/20=1.000000(000568=1.1657/600309=1.0228例外); f47/f38=f48 18/20(000568=25.3279=官方每股未分配利润, 证 f47=未分配利润总额非留存收益)",
        "blocked_pairs": [],
        "settled": ["ulist.f113", "ulist.f58", "ulist.f135"],
    },
    {
        "id": "R8_f129_not_f45_div_f132",
        "false_claim": "f129 = f45 / f132 x 100（销售净利率 = 归母净利/TTM营收, 残差小）",
        "correct": "f129 = 销售净利率%(同报告期); f45=单报告期归母净利(茅台445亿=2026H1)/f132=TTM营收(1732亿) 周期错配 -> 比值!=净利率(误差35~77%); 正确≈ f45/f40(同报告期营收, 全样本误差<2.5pp), 禁 f45/f132 身份证定案",
        "evidence": "20260923_gemini_analysis_verify_round2.md: 600519 f129=50.75% vs f45/f132=25.70% 误差49%; 本轮20股复算 f129 vs f45/f40 误差<2.5pp(茅台2.5pp/600309 1.3pp/其余<0.5pp)",
        "blocked_pairs": [],
        "settled": ["ulist.f129"],
    },
    {
        "id": "R9_zhb_unknown2_not_volratio_minus1",
        "false_claim": "stat.unknown_2 (tdxstat Col[2]) = 量比−1",
        "correct": "stat.unknown_2 真义仍未知（⚠️候选）；同日量比源(由 cache/kline 日K线 volume 计算 量比=vtoday/mean(v_prev5)) 与 unknown_2 全市场 1000 股同码比对 corr≈−0.08，证伪量比−1 假设",
        "evidence": "probe5: 1000 matched stocks (2026-09-22), corr(unknown_2,量比)=−0.0807, corr(unknown_2,量比−1)=−0.0807, 回归残差中位 0.70（非量比−1）",
        "blocked_pairs": [],
        "settled": [],
    },
    {
        "id": "R10_zhb_unknown26_not_concept_count",
        "false_claim": "stat.unknown_26 (tdxstat Col[26]) = 概念板块成分计数",
        "correct": "概念计数假设被证伪（⚠️候选维持）；tdxstat Col[26] 为有界分类码(0-62,42类)，板块分层极清晰：中小板6.14>深主板5.72>沪主板4.95，而创业板0.88/科创板0.86(中位0)。科创板概念最密集却 unknown_26≈0，故'概念成分计数'不成立。最一致假设=主板专属 指数/名单 成分计数(沪深300/中证100/上证50·180/深证成指·100/红利等，天然排除双创)，待主板指数成分股名单反查。",
        "evidence": "probe_b_unknown26: 8058股解析/5576非空；按板块 unknown_26 均值 中小板6.14/深主板5.72/沪主板4.95/创业板0.88/科创板0.86；规模代理 corr=-0.17(非单调)；与股息率-0.37/年初至今+0.39(主板子样本)无单一驱动",
        "blocked_pairs": [],
        "settled": [],
    },
]

# 语义已定 token 集合（合并各条 settled），左字段若为其中之一且属新主张 → 翻案，判伪
SETTLED_REFUTED: set[str] = set()
for _c in REFUTED_CONCLUSIONS:
    SETTLED_REFUTED.update(_c.get("settled", []))


def match_refuted(left: str, right: str) -> RefutedConclusion | None:
    """若 (left,right) 命中已证伪结论，返回该结论 dict；否则 None。

    命中条件：
      * 显式 blocked_pairs（双向相等）；
      * 或 left 属于 SETTLED_REFUTED（对撞左字段=待破解侧，对已定语义 token
        提出新映射即翻案类伪结论）。
    注：right 为已 verified 锚属正常破解用法，不拦截。
    """
    for c in REFUTED_CONCLUSIONS:
        for a, b in c.get("blocked_pairs", []):
            if (left == a and right == b) or (left == b and right == a):
                return c
    if left in SETTLED_REFUTED:
        for c in REFUTED_CONCLUSIONS:
            if left in c.get("settled", []):
                return c
    return None


def print_active_rules(stream: TextIO | None = None) -> TextIO:
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
    print(
        f"2. 命中率分层: 每采样日 ≥{HIT_RATE_L1}/20 且可解释 → L1 定案；"
        f"{HIT_RATE_L4}~{HIT_RATE_L1 - 1} → L4 候选（存疑）",
        file=out,
    )
    print(f"3. 比值族   : CV≤{RATIO_CV_MAX:g} 且比值∈{RATIO_STEPS} → L1-U 单位换算定案", file=out)
    print(f"4. 多日复核 : ≥{MULTI_DAY_MIN} 个独立采集日重复方可定案；单日快照不够", file=out)
    print(
        f"5. 相关性   : 仅 Pearson+Spearman 同号且 |Spearman|≥{CORR_SPEARMAN_MIN} "
        f"且留一法不翻号 → 候选，绝不定案",
        file=out,
    )
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
    L.append(
        f"> 本文件由 `scripts/collision_rules.py` 自动派生"
        f"（`python scripts/collision_rules.py --emit`），生成日 {date.today().isoformat()}。\n"
    )
    L.append(
        "> 对撞脚本运行时自动 `print_active_rules()` 查询本规则；"
        "以代码常量（`collision_rules.py`）为唯一权威，本文档为其人读镜像。\n"
    )
    L.append("## 一、对撞四铁律（硬阈值）\n")
    L.append("| # | 铁律 | 阈值 / 判定 |")
    L.append("|:--|:--|:--|")
    L.append(f"| 1 | 精度对齐 | {PRECISION} |")
    L.append(
        f"| 2 | 命中率分层 | 每采样日 ≥{HIT_RATE_L1}/20 且可解释 → **L1 定案**；"
        f"{HIT_RATE_L4}~{HIT_RATE_L1 - 1} → L4 候选（存疑） |"
    )
    L.append(f"| 3 | 比值族 | CV≤{RATIO_CV_MAX:g} 且比值∈{RATIO_STEPS} → L1-U 单位换算定案 |")
    L.append(f"| 4 | 多日复核 | ≥{MULTI_DAY_MIN} 个独立采集日重复方可定案；单日 20 股快照不够 |")
    L.append(
        f"| 5 | 相关性 | 仅 Pearson+Spearman 同号且 |Spearman|≥{CORR_SPEARMAN_MIN} "
        f"且留一法不翻号 → 候选，绝不定案 |\n"
    )
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
    L.append(
        "- **主攻对撞（crack）**：仅对 `FOCUS` 内未定案的 residual unknowns 跑；"
        "已 **L1** 字段从攻击目标移除。"
    )
    L.append(
        "- **全历史复核 / 再确认（re-validation）**：全量扫描会顺带扫到已定案字段，"
        "结果标注「再确认 / 强化现有结论，未改动语义」，作为回归保护。"
    )
    L.append(
        "- **锁定点 = 升到 L1**：该字段转为对齐锚 / 真值参考，"
        "用于破解其他未知字段时的核对与跨源一致性校验。"
    )
    L.append(
        "- **双向可修正**：L1 遇矛盾新证据可降级或重议"
        "（如 tx[85] 均价候选因锚仅 3/20 回退 L3；tdxstat[31] 对撞东财仅 77% 匹配降级）。\n"
    )
    L.append("")
    L.append("## 五、已证伪结论护栏（回归反例，2026-09-16 立规）\n")
    L.append(
        "> 经数值实证推翻的伪结论，固化为对撞反例；`collide.py` 命中即跳过该候选并记入报告，"
        "防止污染 field_dict.md。护栏只拒绝、不新增字段。\n"
    )
    for c in REFUTED_CONCLUSIONS:
        L.append(f"- **{c['id']}**｜伪主张：`{c['false_claim']}`")
        L.append(f"  - 真相（L1）：{c['correct']}")
        L.append(f"  - 证据：{c['evidence']}")
    L.append("")
    L.append("---\n")
    L.append("> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。\n")

    text = "\n".join(L)
    if path is None:
        path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "docs",
            "field_verification",
            "COLLISION_RULES.md",
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

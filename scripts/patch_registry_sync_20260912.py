#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_registry_sync_20260912.py — 将本轮字段破解「新定案」合规同步进 field_registry.json。

═══════════════════════════════════════════════════════════════════════════════
⚠️ 设计铁律（单一真相源治理）：
    field_registry.json 是「字段登记表」的影子单一真相源，必须由
    docs/field_dict.md（主字典）+ audit_field_completeness（审计注册集）
    经 sanctioned 管线派生。**绝不允许手工注入 JSON 字段**——那会破坏
    G1 parity 闸门（registry 的原生 token×源 必须与审计基线逐字节一致），
    导致提交被 pre-commit 治理闸门拦截。

    本脚本的「同步」= 跑 sanctioned 管线 + 校验新定案已落地，**不做任何 JSON 改写**。
═══════════════════════════════════════════════════════════════════════════════

本轮新定案来源（单一真相）：
  * docs/field_verification/20260912_ulist_collision.md  — ulist f1-f34 多日对撞 21 个 L1（异号同义）
  * docs/field_verification/20260912_zhb_col22_crack.md  — ZHB tdxstat Col[22]=shape_value (L1)
  * core/zhb_client.py (V17.2.7)                          — 8 个 tdxstat 遗漏列解析补抽 + 解析器 schema bump

同步动作（确定性，只读 + 派生）：
  1) extract_registry.py   —— 从 field_dict.md + audit 重建 field_registry.json（Layer1 token 与基线一致）
  2) gen_field_dict.py      —— 由 registry 重写 field_dict.md 的 §零·B（GEN:field-matrix）投影块（幂等）
  3) registry_parity.py     —— G1(原生 token×源) + G3(§零·B 投影) 双重 parity，必须 PASS
  4) 校验新定案已落地：
       - ZHB-tdxstat Col[22] 字段存在于 registry（Col[22]=shape_value 已由主字典驱动登记）
       - 21 对 ulist→push2 跨源映射存在于 registry.mappings（来自 ulist_push2_align.md）
       - field_matrix（§零·B 投影）含 ZHB-tdxstat 源行

退出码：0=同步+校验全部通过；非 0=闸门未过（不应提交）。
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
REG = os.path.join(REPO_ROOT, "docs", "field_verification", "field_registry.json")

# 本轮新定案断言清单（用于同步后校验，不从本脚本写入，仅读取验证）
EXPECT_ZHB_COL22 = "[22]"  # ZHB-tdxstat Col[22] = shape_value
EXPECT_ULIST_PUSH2_PAIRS = 21  # ulist→push2 跨源异号同义映射数（来自 ulist_push2_align.md）

# 21 个 ulist L1 候选：ulist code -> push2 anchor（仅用于报告，不写 JSON）
ULIST_L1 = {
    "f1": 59,
    "f3": 170,
    "f4": 169,
    "f5": 47,
    "f6": 48,
    "f7": 171,
    "f8": 162,
    "f9": 162,
    "f10": 50,
    "f15": 44,
    "f16": 45,
    "f17": 46,
    "f18": 60,
    "f19": 111,
    "f23": 167,
    "f24": 121,
    "f25": 122,
    "f26": 189,
    "f29": 180,
    "f33": 191,
    "f34": 49,
}


def run(step_name: str, *args) -> int:
    """运行一个治理脚本，透传退出码。"""
    print(f"\n==> [{step_name}] {' '.join(args)}")
    proc = subprocess.run([sys.executable, *args], cwd=REPO_ROOT)
    if proc.returncode == 0:
        print(f"[{step_name}] PASS")
    else:
        print(f"[{step_name}] FAIL (exit {proc.returncode})")
    return proc.returncode


def verify_determinations() -> bool:
    """读取 extract 产出的 registry，确认新定案已落地（不写任何内容）。"""
    print("\n==> [verify] 校验本轮新定案已落地（只读）")
    if not os.path.exists(REG):
        print("  FAIL: registry 缺失，请先跑 extract_registry.py")
        return False

    reg = json.load(io.open(REG, encoding="utf-8"))
    fields = reg.get("fields", [])
    fm = reg.get("field_matrix", {})
    mappings = reg.get("mappings", [])

    ok = True

    # 1) ZHB Col[22] 字段存在（由主字典 ZHB tdxstat.cfg 表驱动登记）
    zhb22 = [
        f
        for f in fields
        if f.get("code") == EXPECT_ZHB_COL22 and "ZHB-tdxstat" in f.get("sources", [])
    ]
    if zhb22:
        f = zhb22[0]
        print(
            f"  [✓] ZHB Col[22] 已登记: sources={f.get('sources')} "
            f"status={f.get('status')} meaning={str(f.get('meaning'))[:24]!r}"
        )
    else:
        print("  [✗] ZHB Col[22] 未在 registry 找到（主字典 ZHB tdxstat.cfg 表可能缺 Col[22] 行）")
        ok = False

    # 2) 21 对 ulist→push2 跨源映射（来自 ulist_push2_align.md，由 extract 解析进 mappings）
    ulist_push2 = [
        m
        for m in mappings
        if isinstance(m, dict)
        and m.get("from", {}).get("source", "").startswith("东财-ulist")
        and m.get("to", {}).get("source", "").startswith("东财-push2")
    ]
    n = len(ulist_push2)
    if n >= EXPECT_ULIST_PUSH2_PAIRS:
        print(f"  [✓] ulist→push2 跨源映射 = {n} 对（≥ 期望 {EXPECT_ULIST_PUSH2_PAIRS}）")
    else:
        print(f"  [✗] ulist→push2 跨源映射仅 {n} 对（期望 ≥ {EXPECT_ULIST_PUSH2_PAIRS}）")
        ok = False

    # 3) §零·B 投影含 ZHB 源（field_matrix 用 'ZHB' 源标签，与 build_matrix_from_md 一致）
    #    注：8 个新列在 registry.fields 已登记（ZHB-tdxstat 源），§零·B 投影经 md 解析后
    #    以「字段含义」为 key（如 日 Beta / 自由流通股本 / 年内涨停数 / 连板统计），
    #    属 gen_field_matrix 对宽表 ZHB.cfg 的解析投影，不阻断 G3 parity。
    zhb_in_fm = [k for k, v in fm.items() if isinstance(v, list) and "ZHB" in v]
    if zhb_in_fm:
        print(f"  [✓] §零·B 投影含 ZHB 源行 = {len(zhb_in_fm)} 条（如 {zhb_in_fm[:3]}）")
    else:
        print("  [✗] §零·B 投影 (field_matrix) 未含 ZHB 源行")
        ok = False

    # 3b) 8 个新破解 ZHB 列已在 registry.fields 以 ZHB-tdxstat 源登记
    new_cols = ["[2]", "[11]", "[16]", "[22]", "[23]", "[25]", "[26]", "[34]"]
    got = [
        c
        for c in new_cols
        if any(f.get("code") == c and "ZHB-tdxstat" in f.get("sources", []) for f in fields)
    ]
    if len(got) == len(new_cols):
        print(f"  [✓] 8 个新破解 ZHB 列全部登记于 registry.fields: {got}")
    else:
        print(f"  [✗] 新破解 ZHB 列仅 {len(got)}/{len(new_cols)} 登记: {got}")
        ok = False

    return ok


def main() -> int:
    print("═══════════════════════════════════════════════════════════════════")
    print(" 字段登记表单一真相源 · 合规同步（extract → gen → parity → verify）")
    print("═══════════════════════════════════════════════════════════════════")

    # 任何一步失败即中止（不写 JSON，闸门未过绝不提交）
    rc = 0
    rc |= run("G1-extract", os.path.join(SCRIPT_DIR, "extract_registry.py"))
    if rc != 0:
        print("\n[ABORT] extract_registry.py 失败，停止同步。")
        return rc

    rc |= run("G3-gen", os.path.join(SCRIPT_DIR, "gen_field_dict.py"))
    if rc != 0:
        print("\n[ABORT] gen_field_dict.py 失败，停止同步。")
        return rc

    rc |= run("parity", os.path.join(SCRIPT_DIR, "registry_parity.py"))
    if rc != 0:
        print("\n[ABORT] registry_parity.py 未过：手工注入或派生不一致，请检查主字典与审计。")
        return rc

    if not verify_determinations():
        print("\n[ABORT] 新定案校验未通过：本轮破解结论未在主字典/审计中落地。")
        return 1

    print("\n═══════════════════════════════════════════════════════════════════")
    print(" ✅ 同步完成：registry 经 sanctioned 管线重建，G1+G3 通过，新定案已落地。")
    print("   下一步：git add 改动文件 → git commit（pre-commit 治理闸门将复跑并放行）。")
    print("═══════════════════════════════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())

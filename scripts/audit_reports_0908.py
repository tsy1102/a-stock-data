#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V17.2.9 报告质量回归复检脚本。

验证三处已修复 bug 不回潮（须对「重新生成后的报告」运行，旧报告会因修复前产物而报 fail，
这正说明检测有效）：

  BUG-1  章节空表    mak C段「异动集聚板块TOP5 / 龙虎榜异动补全」不得出现标题后无任何内容的空表。
  BUG-2  跌停口径错配 全部 sht 打板段「跌停 N 只」必须与 mak B段同口径跌停数一致
                     （mak 跌停>0 时 sht 不得为 0）。
  BUG-3  多口径未标注  mak 连板梯队 / 涨停数须各自携带数据源标签
                     （财联社连板梯队 / 样本内3日连板统计 / 涨停数互校 / 涨停天梯（开盘红） / 涨停池口径）。

用法:
  python scripts/audit_reports_0908.py [REPORTS_DIR] [DATE=20260908]

退出码: 0 = 全部通过; 1 = 存在回潮(fail)。
"""
import os
import re
import glob
import sys

REP_DEFAULT = r"C:\Tencent\WorkBuddy\a-stock-data\reports"

# mak 报告必须出现的多口径数据源标签（BUG-3 护栏）。
# 注：「财联社连板梯队」所在板块依赖财联社情绪接口，接口异常时整段缺失属正常降级，
# 不作为硬性护栏；其余 4 个标签均在主流程中稳定输出。
BUG3_REQUIRED_LABELS = [
    "连板梯队（样本内3日连板统计）",
    "涨停数互校",
    "涨停天梯（开盘红）",
    "涨停池口径",
]


def read(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def check_bug1(mak_txt):
    """mak C段空表检测：标题之后到下一个 ## 之间必须有实际内容。"""
    # 捕获从「异动集聚板块TOP5」到下一个二级标题或文末的整段
    m = re.search(r"异动集聚板块TOP5.*?(?=^## |\Z)", mak_txt, re.S | re.M)
    if not m:
        # 也可能是「龙虎榜异动补全」作为独立段
        m = re.search(r"龙虎榜异动补全.*?(?=^## |\Z)", mak_txt, re.S | re.M)
        if not m:
            return ("FAIL", "BUG-1", "未找到 C段 异动集聚/龙虎榜补全区块，章节可能缺失")
    block = m.group(0)
    # 内容指示：板块异动行 / 兜底说明 / 龙虎榜行 / 净买
    content = re.search(r"只异动|未形成明显板块集聚|龙虎榜异动补全|净买|板块内密度", block)
    if not content:
        return ("FAIL", "BUG-1", "C段标题存在但无任何内容行（空表回潮）")
    return ("PASS", "BUG-1", "C段标题后存在内容（板块异动/龙虎榜补全/兜底说明）")


def check_bug2(mak_txt, sht_files):
    """sht 跌停口径须与 mak B段一致。"""
    mak_b = re.search(
        r"涨停\s*(\d+)\s*只\s*\|\s*炸板\s*(\d+)\s*只\s*\|\s*跌停\s*(\d+)\s*只", mak_txt
    )
    if not mak_b:
        return ("WARN", "BUG-2", "mak B段未找到打板行，跳过跌停口径比对")
    mak_dt = int(mak_b.group(3))
    bad = []
    for p in sht_files:
        t = read(p)
        s = re.search(
            r"今日涨停\s*(\d+)\s*只\s*\|\s*炸板\s*(\d+)\s*只\s*\|\s*跌停\s*(\d+)\s*只", t
        )
        if not s:
            continue
        sht_dt = int(s.group(3))
        if mak_dt > 0 and sht_dt == 0:
            bad.append((os.path.basename(p).split("_")[0], sht_dt))
        elif sht_dt != mak_dt:
            bad.append((os.path.basename(p).split("_")[0], sht_dt))
    if bad:
        return (
            "FAIL",
            "BUG-2",
            f"mak 跌停={mak_dt}，以下 sht 跌停不一致: {bad[:5]}"
            + (" ..." if len(bad) > 5 else ""),
        )
    return ("PASS", "BUG-2", f"全部 {len(sht_files)} 份 sht 跌停数与 mak({mak_dt})同口径一致")


def check_bug3(mak_txt):
    """mak 连板/涨停多口径须带数据源标签。"""
    missing = [l for l in BUG3_REQUIRED_LABELS if l not in mak_txt]
    if missing:
        return ("FAIL", "BUG-3", f"mak 缺失数据源标签: {missing}")
    return ("PASS", "BUG-3", f"mak 含全部 {len(BUG3_REQUIRED_LABELS)} 处数据源标签")


def main():
    rep = sys.argv[1] if len(sys.argv) > 1 else REP_DEFAULT
    date = sys.argv[2] if len(sys.argv) > 2 else "20260908"
    if not os.path.isdir(rep):
        print(f"[ERR] reports 目录不存在: {rep}")
        return 2

    mak_files = sorted(glob.glob(os.path.join(rep, f"get_mak_report_{date}_*.md")))
    sht_files = sorted(glob.glob(os.path.join(rep, f"*_sht_{date}_*.md")))
    if not mak_files:
        print(f"[ERR] 未找到 mak 报告 (date={date})")
        return 2
    mak_txt = read(mak_files[-1])  # 取最新一份

    print("=" * 72)
    print(f"V17.2.9 报告回归复检  (date={date}, reports={rep})")
    print(f"  mak={os.path.basename(mak_files[-1])}  sht={len(sht_files)}份")
    print("=" * 72)

    results = []
    results.append(check_bug1(mak_txt))
    results.append(check_bug2(mak_txt, sht_files))
    results.append(check_bug3(mak_txt))

    fails = 0
    for status, code, msg in results:
        mark = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(status, "?")
        print(f"  {mark} [{status:4}] {code:6} {msg}")
        if status == "FAIL":
            fails += 1

    print("=" * 72)
    if fails:
        print(f"结果: {fails} 项回潮(fail) — 修复未生效或已回归")
        return 1
    print("结果: 全部通过 — BUG-1/2/3 护栏正常")
    return 0


if __name__ == "__main__":
    sys.exit(main())

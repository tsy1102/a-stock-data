#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""crack_zhb_col22_20260912.py
针对 ZHB 缓存（cache/zhb/zhb_YYYYMMDD.zip 内 tdxstat.cfg）重新破解 Col[22]。

背景：
- core/zhb_client.py 的 _parse_tdxstat() 解析 35 字段，但**遗漏 Col[22]**（docstring 标称
  shape_value，官方 TdxQuant 确认 50101/50109，但解析代码不抽取、marshal bin 亦不含）。
- 因此 marshal bin 缓存与 raw_zhb.json 均无 Col[22]，唯一权威来源是原始 tdxstat.cfg。

本脚本跨全部 31 个 zhb 快照（20260731→20260911）抽取 Col[22]，做：
  1. 单日分布（distinct 数、top 频次）
  2. 跨日结构（稳定码 vs 瞬态码）
  3. 个股 Col[22] 轨迹 + 日际变化率
  4. 码值聚类（前缀/首位 digit 结构）
  5. Col[22] 变动是否与当日涨跌幅相关（热点轮动性质判定）
严格遵循对撞四铁律：本字段属"配置直解 / 源覆盖盲区"，不做跨源等号对撞，仅做结构刻画。
"""
from __future__ import annotations
import os, re, zipfile, glob, json, statistics
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZHBDIR = os.path.join(ROOT, "cache", "zhb")

# A 股 20 样本池（跨行业，覆盖主板/创业板/科创板）
SAMPLE = ["600519","000001","300750","600036","000858","601318","002594","600276",
          "000333","601012","600900","002415","300059","600030","000651","601888",
          "600887","300760","002475","688981"]

def find_tdxstat(zf: zipfile.ZipFile):
    for n in zf.namelist():
        if n.lower().endswith("tdxstat.cfg"):
            return n
    return None

def load_col22(date: str):
    """返回 {code: dict(col22,col23,col33,chg)}，仅成功解析行。"""
    fp = os.path.join(ZHBDIR, f"zhb_{date}.zip")
    if not os.path.exists(fp):
        return None
    out = {}
    with zipfile.ZipFile(fp) as zf:
        name = find_tdxstat(zf)
        if not name:
            return None
        data = zf.read(name)
    text = data.decode("gbk", errors="ignore")
    for line in text.splitlines():
        parts = line.split("|")
        if len(parts) < 34:
            continue
        code = parts[1].strip()
        if not code:
            continue
        out[code] = {
            "c22": parts[22].strip(),
            "c23": parts[23].strip(),   # zt_type_code 当日行情类型分档
            "c33": parts[33].strip(),   # zt_lianban 连板数
            "chg": parts[6].strip(),    # 当日涨跌幅
        }
    return out

def main():
    dates = sorted(d for d in [os.path.basename(p)[4:12]
                  for p in glob.glob(os.path.join(ZHBDIR, "zhb_*.zip"))])
    print(f"== 发现 {len(dates)} 个 ZHB 快照: {dates[0]}..{dates[-1]}")

    daily = {}          # date -> {code: {c22,c23,c33,chg}}
    for d in dates:
        m = load_col22(d)
        if m is None:
            print(f"  !! {d} 缺失或无法解析")
            continue
        daily[d] = m
    print(f"== 成功加载 {len(daily)} 个快照")

    # 1) 单日分布
    print("\n## 1. 单日 Col[22] 分布（采样 6 个代表日）")
    rep_days = [dates[0], dates[len(dates)//4], dates[len(dates)//2],
                dates[3*len(dates)//4], dates[-2], dates[-1]]
    for d in rep_days:
        if d not in daily: continue
        vals = [r["c22"] for r in daily[d].values() if r["c22"] != ""]
        c = Counter(vals)
        top = c.most_common(5)
        print(f"  {d}: 个股数={len(vals)} distinct={len(c)} top5={top}")

    # 2) 跨日结构：稳定码（每日均现） vs 瞬态码（仅 1 日）
    val_on_days = defaultdict(set)
    for d, m in daily.items():
        for code, r in m.items():
            v = r["c22"]
            if v:
                val_on_days[v].add(d)
    total_distinct = len(val_on_days)
    stable = [v for v, ds in val_on_days.items() if len(ds) == len(daily)]
    ephemeral = [v for v, ds in val_on_days.items() if len(ds) == 1]
    print(f"\n## 2. 跨日结构")
    print(f"  总 distinct Col[22] = {total_distinct}")
    print(f"  稳定码（每快照均现, {len(daily)} 日全勤）= {len(stable)} 例: {sorted(stable)[:15]}")
    print(f"  瞬态码（仅 1 日出现）= {len(ephemeral)} 例（占比 {len(ephemeral)/total_distinct*100:.1f}%）")

    # 3) 个股轨迹 + 日际变化率
    print(f"\n## 3. 20 样本池 Col[22] 轨迹（日际变化率）")
    traj_lines = []
    for code in SAMPLE:
        seq = []
        prev = None
        changes = 0
        n = 0
        for d in dates:
            if code in daily[d]:
                v = daily[d][code]["c22"]
                seq.append(v)
                if v != "":
                    n += 1
                    if prev is not None and v != prev:
                        changes += 1
                    prev = v
        distinct = len(set(seq) - {""})
        rate = changes / max(n-1, 1) * 100 if n > 1 else 0
        traj_lines.append((code, distinct, rate, seq))
        print(f"  {code}: 有值日={n} distinct={distinct} 变化率={rate:.0f}% 轨迹={seq}")

    # 4) 码值聚类：前缀 / 首位 digit
    print(f"\n## 4. Col[22] 码值聚类（全样本合并）")
    allvals = [v for ds in val_on_days for v in [ds]]  # keys
    # 实际把所有出现过的码（带频次）聚类
    allc = Counter()
    for d, m in daily.items():
        for code, r in m.items():
            v = r["c22"]
            if v:
                allc[v] += 1
    # 前缀两位
    pref2 = Counter()
    firstdigit = Counter()
    lens = Counter()
    for v in allc:
        if re.fullmatch(r"\d+", v):
            pref2[v[:2]] += allc[v]
            firstdigit[v[0]] += allc[v]
            lens[len(v)] += allc[v]
    print(f"  长度分布(按出现次数): {dict(sorted(lens.items()))}")
    print(f"  首位 digit 分布(按出现次数): {dict(sorted(firstdigit.items()))}")
    print(f"  前缀2位 Top12(按出现次数): {pref2.most_common(12)}")

    # 5) Col[22] 变动 vs 当日涨跌幅：变化是否伴随价格异动（热点轮动判定）
    print(f"\n## 5. Col[22] 变动与涨跌幅关联（热点轮动性质）")
    # 对每只股票，构造 (col22_changed, |chg_pct|) 配对，做变化日 vs 不变日的涨跌幅均值
    changed_chg = []
    unchanged_chg = []
    for d_idx in range(1, len(dates)):
        d0, d1 = dates[d_idx-1], dates[d_idx]
        if d0 not in daily or d1 not in daily: continue
        m0, m1 = daily[d0], daily[d1]
        for code in set(m0) & set(m1):
            v0 = m0[code]["c22"]; c0 = m0[code]["chg"]
            v1 = m1[code]["c22"]; c1 = m1[code]["chg"]
            try:
                chg1 = float(c1)
            except: 
                continue
            if v0 == "" or v1 == "":
                continue
            if v0 != v1:
                changed_chg.append(chg1)
            else:
                unchanged_chg.append(chg1)
    def avg(x):
        return statistics.mean(x) if x else float("nan")
    def med(x):
        return statistics.median(x) if x else float("nan")
    print(f"  Col[22] 变化日数={len(changed_chg)} 不变日数={len(unchanged_chg)}")
    print(f"  变化日 |涨跌幅| 均值={avg(changed_chg):.2f}% 中位={med(changed_chg):.2f}%")
    print(f"  不变日 |涨跌幅| 均值={avg(unchanged_chg):.2f}% 中位={med(unchanged_chg):.2f}%")

    # 6) Col[22] vs Col[23](zt_type_code) 与 涨跌停状态 交叉验证
    print(f"\n## 6. Col[22] 与 行情类型(Col[23])/涨跌停 交叉验证")
    # 涨停/跌停判定：change_pct >= +9.5 / <= -9.5（近似板幅）；同时看 Col[23] 分布
    c22_by_limit = {"涨停": Counter(), "跌停": Counter(), "普通": Counter()}
    c23_by_limit = {"涨停": Counter(), "跌停": Counter(), "普通": Counter()}
    for d in dates:
        m = daily[d]
        for code, r in m.items():
            try:
                chg = float(r["chg"])
            except:
                continue
            if chg >= 9.5:
                bucket = "涨停"
            elif chg <= -9.5:
                bucket = "跌停"
            else:
                bucket = "普通"
            if r["c22"]:
                c22_by_limit[bucket][r["c22"][:2]] += 1   # 仅看前缀2位
            if r["c23"]:
                c23_by_limit[bucket][r["c23"]] += 1
    for bucket in ("涨停", "跌停", "普通"):
        top22 = c22_by_limit[bucket].most_common(5)
        top23 = c23_by_limit[bucket].most_common(5)
        print(f"  [{bucket}] Col[22]前缀Top5={top22}  Col[23]Top5={top23}")
    # Col[22] 首位 digit 在 涨停 vs 普通 的比例对比
    def digit_profile(bucket):
        c = c22_by_limit[bucket]
        tot = sum(c.values())
        return {d: c[d]/tot*100 for d in sorted(c)} if tot else {}
    print(f"  涨停 Col[22]首位分布%={digit_profile('涨停')}")
    print(f"  普通 Col[22]首位分布%={digit_profile('普通')}")

    # 输出 JSON 供报告引用
    out = {
        "dates": dates,
        "n_snapshots": len(daily),
        "total_distinct_col22": total_distinct,
        "stable_count": len(stable),
        "ephemeral_count": len(ephemeral),
        "sample_trajectories": {c: {"distinct": di, "change_rate_pct": r, "seq": s}
                                 for c, di, r, s in traj_lines},
        "len_dist": dict(sorted(lens.items())),
        "first_digit_dist": dict(sorted(firstdigit.items())),
        "prefix2_top": pref2.most_common(12),
        "changed_days": len(changed_chg), "unchanged_days": len(unchanged_chg),
        "changed_abs_chg_mean": avg(changed_chg), "unchanged_abs_chg_mean": avg(unchanged_chg),
        "c22_prefix_by_limit": {b: dict(c22_by_limit[b].most_common(8)) for b in ("涨停","跌停","普通")},
        "c23_by_limit": {b: dict(c23_by_limit[b].most_common(8)) for b in ("涨停","跌停","普通")},
        "c22_firstdigit涨停%": digit_profile("涨停"),
        "c22_firstdigit普通%": digit_profile("普通"),
    }
    with open(os.path.join(ROOT, "docs", "field_verification",
              "20260912_zhb_col22_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n== 已写出 docs/field_verification/20260912_zhb_col22_analysis.json")

if __name__ == "__main__":
    main()

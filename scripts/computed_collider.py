#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""computed_collider.py — computed 字段通用独立锚重算对撞器 (V17.2.7, 2026-09-09)

将 round13 的 TDX K线 Beta 锚重算固化为一等方法: 对任意标记 anchor_source='tdx_kline'
的 COMPUTED 字段, 从 K线缓存(raw_tdx_kline_full.json)读取个股序列, 用注册的
indicator 函数独立重算该指标, 再与腾讯 tx[field] 对撞, 输出完整统计证据:

    Pearson / Spearman / R² / 斜率 / 截距 / 留一法最小 Pearson / 最大残差

设计要点:
  1) 与采集层解耦 —— 锚数据来自已落盘的 K线缓存(由 TDX MCP / 运行时 easy_tdx 预先提取),
     不在运行时强依赖网络; 实时刷新可经 core/tdx_client 的 bars()/index_bars() 重建缓存。
  2) 按 anchor_source 分发 —— 字段身份来自 field_meta.py; 本器只负责"重算+对撞",
     不知道字段语义, 只认 (anchor_source, indicator) 注册项。
  3) 相关性只生成候选 —— 依对撞铁律#5, 输出永不自称 L1 定案, 仅给身份确认级证据。
     (tx[51] 因独立重算 Pearson=1.0000/斜率=1.000 属精确数值命中, 可升 L1 定案,
      此为四铁律"同源精确对撞"例外路径; 其余相关量仅身份确认。)

已注册指标:
  - ("tdx_kline","beta") : 个股相对基准指数 Beta(OLS 斜率), 需 closes 序列
  - ("tdx_kline","vwap") : 个股最新非空 bar 均价 = 成交额÷成交量(元/股), 需 amount/volume

用法:
  python scripts/computed_collider.py --field 56
  python scripts/computed_collider.py --field 51        # VWAP 验证
  python scripts/computed_collider.py --field 85         # tx[85] 是否 VWAP 判别
  python scripts/computed_collider.py --field 56 --benchmark 000985
"""
from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_KLINE = os.path.join(ROOT, "docs", "field_verification", "raw_tdx_kline_full.json")
DEFAULT_TX = os.path.join(ROOT, "docs", "field_verification", "20260908", "raw_tencent.json")
DEFAULT_BENCHMARK = "000985"  # 中证全指: round13 定位的宽基全市场基准


# --------------------------- 统计原语(从 round13 验证脚本提炼) ---------------------------
def daily_returns(dates, closes):
    """收益率序列 [(date, ret)], ret=(c-p)/p。"""
    out = []
    for i in range(1, len(closes)):
        p, c = closes[i - 1], closes[i]
        out.append((dates[i], (c - p) / p if p else 0.0))
    return out


def beta_of(stock_ret, mkt_ret) -> float:
    """OLS 斜率 = Cov/Var。"""
    n = len(stock_ret)
    if n < 2:
        return 0.0
    ms = sum(stock_ret) / n
    mm = sum(mkt_ret) / n
    cov = sum((a - ms) * (b - mm) for a, b in zip(stock_ret, mkt_ret))
    var = sum((b - mm) ** 2 for b in mkt_ret)
    return cov / var if var else 0.0


def pearson(xs, ys) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sx = math.sqrt(sum((a - mx) ** 2 for a in xs))
    sy = math.sqrt(sum((b - my) ** 2 for b in ys))
    return cov / (sx * sy) if sx and sy else 0.0


def spearman(xs, ys) -> float:
    def _rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        rk = [0.0] * len(v)
        cur = 0
        while cur < len(v):
            j = cur
            while j + 1 < len(v) and v[order[j + 1]] == v[order[cur]]:
                j += 1
            avg = (cur + j) / 2.0 + 1
            for k in range(cur, j + 1):
                rk[order[k]] = avg
            cur = j + 1
        return rk
    return pearson(_rank(xs), _rank(ys))


def linfit(xs, ys) -> Tuple[float, float]:
    n = len(xs)
    if n < 2:
        return (0.0, 0.0)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx if sxx else 0.0
    return slope, my - slope * mx


# --------------------------- 重算指标注册表(anchor_source='tdx_kline') ---------------------------
def _indicator_beta(kline_cache: dict, code: str, benchmark: str) -> Optional[float]:
    """从 K线缓存算个股相对基准的 Beta(OLS 斜率)。仅用 close 序列。"""
    if code not in kline_cache or benchmark not in kline_cache:
        return None
    s = kline_cache[code]
    b = kline_cache[benchmark]
    sd = {d: c for d, c in zip(s["dates"], s["closes"])}
    bd = {d: c for d, c in zip(b["dates"], b["closes"])}
    common = sorted(set(sd) & set(bd))
    if len(common) < 5:
        return None
    rs = daily_returns(common, [sd[d] for d in common])
    rm = daily_returns(common, [bd[d] for d in common])
    if not rs or not rm:
        return None
    return beta_of([r[1] for r in rs], [r[1] for r in rm])


def _latest_nonempty_idx(s: dict):
    """返回最新一根成交量>0(非盘前空量)的 bar 下标; 无则返回 None。"""
    vols = s.get("volumes") or []
    for i in range(len(vols) - 1, -1, -1):
        try:
            if float(vols[i]) > 0:
                return i
        except Exception:
            continue
    return None


def _indicator_vwap(kline_cache: dict, code: str, benchmark: str) -> Optional[float]:
    """个股最新非空 bar 均价(VWAP, 元/股) = 成交额 ÷ 成交量。

    单位处理(关键边界):
      TDX K线每行含 Amount(元, 已终值) 与 Volume(手, 已按 Unit 换算) 及
      RawAmount/RawVolume(未换算原生值)。经 2026-09-09 实测:
        RawAmount/RawVolume 直接给出 元/股 均价(与腾讯 tx[51] 残差 <0.005, Pearson=1.0);
        故优先用 RawAmount/RawVolume; 仅当原生值为 0 时回退 Amount/(Volume×100)
        (Volume 单位为手, 1手=100股 → 元/股 = 元/(手×100))。
    benchmark 参数对本指标无意义(均价是单 bar 价格, 无基准), 占位忽略。
    """
    if code not in kline_cache:
        return None
    s = kline_cache[code]
    vols = s.get("volumes") or []
    rawv = s.get("rawvolumes") or []
    rawa = s.get("rawamounts") or []
    amts = s.get("amounts") or []
    idx = _latest_nonempty_idx(s)
    if idx is None:
        return None
    try:
        rv = float(rawv[idx]) if idx < len(rawv) else 0.0
        ra = float(rawa[idx]) if idx < len(rawa) else 0.0
        v = float(vols[idx]) if idx < len(vols) else 0.0
        a = float(amts[idx]) if idx < len(amts) else 0.0
    except Exception:
        return None
    if rv > 0 and ra > 0:
        return ra / rv
    if v > 0 and a > 0:
        return a / (v * 100.0)   # 回退: 元/股 = 元/(手×100)
    return None


# 指标注册表: 键 = (anchor_source, indicator_name)
INDICATORS: Dict[Tuple[str, str], Callable] = {
    ("tdx_kline", "beta"): _indicator_beta,
    ("tdx_kline", "vwap"): _indicator_vwap,
}

# 字段 -> 指标映射(从 field_meta 派生的 COMPUTED + tdx_kline 字段)
# tx[51]=均价(VWAP, L1 第四源精确命中); tx[85]=价格类(实测非 VWAP, 近似当前价, 见报告)
FIELD_INDICATOR: Dict[int, Tuple[str, str]] = {
    51: ("tdx_kline", "vwap"),
    56: ("tdx_kline", "beta"),
    85: ("tdx_kline", "vwap"),
}


@dataclass
class CollisionResult:
    field: int
    n: int
    pearson: float
    spearman: float
    r2: float
    slope: float
    intercept: float
    loo_min_pearson: float
    residual_max: float
    benchmark: str
    indicator: str
    ok: bool
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "field": self.field,
            "n": self.n,
            "pearson": round(self.pearson, 4),
            "spearman": round(self.spearman, 4),
            "r2": round(self.r2, 4),
            "slope": round(self.slope, 4),
            "intercept": round(self.intercept, 4),
            "loo_min_pearson": round(self.loo_min_pearson, 4),
            "residual_max": round(self.residual_max, 4),
            "benchmark": self.benchmark,
            "indicator": self.indicator,
            "ok": self.ok,
            "note": self.note,
        }


def collide_field(field: int, kline_cache_path: str = DEFAULT_KLINE,
                  tencent_path: str = DEFAULT_TX,
                  benchmark: str = DEFAULT_BENCHMARK) -> CollisionResult:
    """对单个 computed 字段执行独立锚重算 + 对撞。"""
    if field not in FIELD_INDICATOR:
        return CollisionResult(field, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                               benchmark, "?", False,
                               "field 未注册 indicator(见 FIELD_INDICATOR)")
    a_src, ind_name = FIELD_INDICATOR[field]
    ind_fn = INDICATORS.get((a_src, ind_name))
    if ind_fn is None:
        return CollisionResult(field, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                               benchmark, ind_name, False, "indicator 未实现")

    kc = json.load(open(kline_cache_path, encoding="utf-8"))
    # VWAP 为单 bar 价格, 无需市场基准; 仅 Beta 类要求 benchmark 在缓存中
    if ind_name == "beta" and benchmark not in kc:
        return CollisionResult(field, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                               benchmark, ind_name, False,
                               "基准 %s 不在 K线缓存" % benchmark)

    tx = json.load(open(tencent_path, encoding="utf-8"))["stocks"]
    xs, ys = [], []
    for code, rec in tx.items():
        if code not in kc:
            continue
        fields = rec.get("fields")
        if not fields or field >= len(fields):
            continue
        try:
            val = float(fields[field])
        except Exception:
            continue
        if field in (29, 83) and val == 0:  # 占位符跳过
            continue
        indep = ind_fn(kc, code, benchmark)
        if indep is None:
            continue
        xs.append(indep)
        ys.append(val)

    if len(xs) < 5:
        return CollisionResult(field, len(xs), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                               benchmark, ind_name, False,
                               "有效样本不足(%d)" % len(xs))

    pr = pearson(xs, ys)
    sp = spearman(xs, ys)
    slope, intercept = linfit(xs, ys)
    r2 = pr * pr
    loo = [pearson(xs[:i] + xs[i + 1:], ys[:i] + ys[i + 1:]) for i in range(len(xs))]
    loo_min = min(loo) if loo else 0.0
    resid_max = max(abs(y - (slope * x + intercept)) for x, y in zip(xs, ys)) if xs else 0.0
    note = "tx[%d] = %.3f + %.3f * indep(%s)" % (field, intercept, slope, ind_name)
    disp_bench = "-" if ind_name == "vwap" else benchmark
    return CollisionResult(field, len(xs), pr, sp, r2, slope, intercept, loo_min, resid_max,
                           disp_bench, ind_name, True, note)


def main():
    ap = argparse.ArgumentParser(description="computed 字段通用独立锚重算对撞器")
    ap.add_argument("--field", type=int, required=True, help="腾讯字段索引, 如 56")
    ap.add_argument("--kline-cache", default=DEFAULT_KLINE)
    ap.add_argument("--tencent", default=DEFAULT_TX)
    ap.add_argument("--benchmark", default=DEFAULT_BENCHMARK, help="基准指数代码, 默认 000985 中证全指")
    args = ap.parse_args()
    res = collide_field(args.field, args.kline_cache, args.tencent, args.benchmark)
    print(json.dumps(res.to_dict(), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

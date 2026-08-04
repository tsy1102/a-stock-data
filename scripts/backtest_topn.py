#!/usr/bin/env python3
"""backtest_topn.py — V14.3.2 top_n 回测验证脚本

目的：
  - 用 cache/zhb 目录下连续 4 天 (7/21, 7/22, 7/23, 7/24) 的 ZHB 数据
  - 验证不同 top_n (100/200/300/500/1000) 对 22 策略的选股质量
  - 给出每个策略的"推荐 top_n"差异化建议

方法：
  1. 加载 4 天 ZHB zip 包
  2. 对每天数据用 get_market_snapshot_dataclass 模拟 val 入口
  3. 对 8 个纯 ZHB 策略（04/11/12/13/19/20/21/22）+ 4 个网络策略（02/05/06/17）模拟跑
  4. 对每个 top_n 计算覆盖率/命中率/稳定性
  5. 输出 CSV 报告

注意：
  - mcap_yi 不在 ZHB 中，回测用 amount 作为"活跃度代理"（与排序键一致）
  - 网络策略（02/05/06/17）用 ZHB 近似 K 线
"""
from __future__ import annotations

import csv
import json
import sys
import time
import zipfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

# 路径设置
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from zhb_client import _parse_zhb_data


# ═══════════════════════════════════════
# 配置
# ═══════════════════════════════════════

DAYS = ["20260721", "20260722", "20260723", "20260724"]
TOP_N_CANDIDATES = [100, 200, 300, 500, 1000]
CACHE_DIR = ROOT / "cache" / "zhb"
OUTPUT_DIR = ROOT / "docs" / "backtest_v1432"

# 8 个纯 ZHB 策略 + 4 个网络策略
ZHB_PURE_STRATEGIES = {
    "04_core_discount": "核心打折（mcap_yi>=100 + PE 估值）",
    "11_holder_concentration": "筹码集中（按 mcap_yi 排序）",
    "12_divergence_warning": "量价信号（按 mcap_yi 排序）",
    "13_dividend_yield": "高股息（mcap_yi>=50 + dividend_yield）",
    "19_52w_position": "52周低位（high_52w/low_52w）",
    "20_main_fund_ratio": "主力资金（main_net_buy_amount）",
    "21_volume_acceleration": "量能三连击（vol_ratio_5d + turnover_5d）",
    "22_capital_momentum": "资金动量（main_net_buy_amount）",
}
NETWORK_STRATEGIES = {
    "02_weekly_ma": "周线多头（需 TDX 周K线）",
    "05_double_bottom": "W底形态（需 TDX 日K线）",
    "06_three_soldiers": "红三兵（需 TDX 日K线）",
    "17_northbound_top": "北向Top（需东财 HTTP）",
}


# ═══════════════════════════════════════
# 数据加载
# ═══════════════════════════════════════

def load_zhb_snapshot(day: str) -> Dict[str, Dict[str, Any]]:
    """加载 ZHB zip 包，返回 {code: {字段}} 快照（合并 tdxstat + tdxstat2）。"""
    zip_path = CACHE_DIR / f"zhb_{day}.zip"
    if not zip_path.exists():
        raise FileNotFoundError(f"ZHB 包不存在: {zip_path}")
    with open(zip_path, "rb") as f:
        data = f.read()
    zhb = _parse_zhb_data(data)
    # 合并 tdxstat + tdxstat2
    merged: Dict[str, Dict[str, Any]] = {}
    for code, stat in zhb.stock_stats.items():
        merged[code] = dict(stat)
    for code, stat2 in zhb.stock_stats2.items():
        if code not in merged:
            merged[code] = {}
        merged[code].update(stat2)
    return merged


def calc_mcap_proxy(stock: Dict[str, Any]) -> float:
    """V14.3.2: mcap_yi 代理 = amount × pe_ttm × 0.5 (粗略，反映活跃度+估值)。"""
    amount = stock.get("amount", 0) or 0
    pe = stock.get("pe_ttm", 0) or 0
    if amount <= 0 or pe <= 0:
        return 0.0
    return amount * pe * 0.5


def enrich_stock(stock: Dict[str, Any]) -> Dict[str, Any]:
    """为 ZHB stock 补全策略需要的字段（mcap_yi 代理等）。"""
    s = dict(stock)
    s["mcap_yi"] = calc_mcap_proxy(stock) / 10000  # 转换为亿
    s["amount_yi"] = (stock.get("amount", 0) or 0) / 10000
    # 主力净流入（万元）
    s["main_net_buy_amount"] = stock.get("main_net_buy_amount", 0) or 0
    return s


# ═══════════════════════════════════════
# 纯 ZHB 策略模拟
# ═══════════════════════════════════════

def _safe_float(v, default: float = 0.0) -> float:
    try:
        return float(v) if v is not None else default
    except (ValueError, TypeError):
        return default


def sim_strategy_04(stocks: List[Dict], top_n: int) -> List[str]:
    """策略 04: 核心打折（mcap_yi >= 100 + PE 估值）。"""
    candidates = [s for s in stocks if s.get("mcap_yi", 0) >= 100]
    candidates = sorted(candidates, key=lambda x: x.get("mcap_yi", 0), reverse=True)[:top_n]
    result = []
    for s in candidates:
        pe = _safe_float(s.get("pe_ttm", 0))
        if 0 < pe <= 50:
            result.append(s["code"])
    # V14.3.2: 真实代码中用 _top5_sorted 截断到 10
    return result[:10]


def sim_strategy_11(stocks: List[Dict], top_n: int) -> List[str]:
    """策略 11: 筹码集中（按 mcap_yi 排序，依赖 ZHB holder 数据）。"""
    candidates = sorted(stocks, key=lambda x: x.get("mcap_yi", 0), reverse=True)[:top_n]
    return [s["code"] for s in candidates[:10]]


def sim_strategy_12(stocks: List[Dict], top_n: int) -> List[str]:
    """策略 12: 量价信号（按 mcap_yi 排序）。"""
    candidates = sorted(stocks, key=lambda x: x.get("mcap_yi", 0), reverse=True)[:top_n]
    return [s["code"] for s in candidates[:10]]


def sim_strategy_13(stocks: List[Dict], top_n: int) -> List[str]:
    """策略 13: 高股息（mcap_yi >= 50 + dividend_yield 排序）。"""
    candidates = [s for s in stocks if s.get("mcap_yi", 0) >= 50][:top_n]
    candidates = sorted(candidates, key=lambda x: _safe_float(x.get("dividend_yield", 0)), reverse=True)
    return [s["code"] for s in candidates[:10]]


def sim_strategy_19(stocks: List[Dict], top_n: int) -> List[str]:
    """策略 19: 52周低位（high_52w/low_52w + change_5d）。

    V14.3.2: 实际 val 中传 all_stocks（不限范围），回测中模拟"在 top_n 范围内找超卖股"
    """
    result = []
    for s in stocks:
        high_52w = _safe_float(s.get("high_52w", 0))
        low_52w = _safe_float(s.get("low_52w", 0))
        pe = _safe_float(s.get("pe_ttm", 0))
        if not high_52w or not low_52w or high_52w <= low_52w:
            continue
        if pe is not None and pe != 0 and pe < 0:
            continue
        position_pct = (1 - low_52w / high_52w) * 100  # 简化的位置百分位
        if position_pct < 30:  # 超卖
            result.append((s["code"], -position_pct))  # 越低越好
    result.sort(key=lambda x: x[1])
    return [r[0] for r in result[:10]]


def sim_strategy_20(stocks: List[Dict], top_n: int) -> List[str]:
    """策略 20: 主力资金（main_net_buy_amount 占比）。

    V14.3.2: 实际 val 中传 all_stocks，回测在 top_n 范围内找主力净流入占比 >= 3%
    """
    result = []
    for s in stocks:
        main_net = _safe_float(s.get("main_net_buy_amount", 0))
        amount = _safe_float(s.get("amount", 0))
        if main_net is None or amount is None or main_net <= 0 or amount <= 0:
            continue
        ratio = main_net / amount
        if ratio >= 0.03:  # 主力净流入占比 >= 3%
            result.append((s["code"], ratio))
    result.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in result[:10]]


def sim_strategy_21(stocks: List[Dict], top_n: int) -> List[str]:
    """策略 21: 量能三连击（amount 5d/1d 比率 + turnover）。"""
    result = []
    for s in stocks:
        amount = _safe_float(s.get("amount", 0))
        amount_1d = _safe_float(s.get("amount_1d", 0))
        if not amount_1d or amount_1d <= 0:
            continue
        if amount <= 0:
            continue
        vol_ratio = amount / amount_1d
        if vol_ratio >= 1.5:  # 5d/1d 至少 1.5 倍
            result.append((s["code"], vol_ratio))
    result.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in result[:10]]


def sim_strategy_22(stocks: List[Dict], top_n: int) -> List[str]:
    """策略 22: 资金动量（main_net_buy_amount 连续 2 天）。"""
    result = []
    for s in stocks:
        main_net = _safe_float(s.get("main_net_buy_amount", 0))
        main_net_1d = _safe_float(s.get("main_net_buy_amount_1d", 0))
        if main_net is not None and main_net_1d is not None and main_net > 0 and main_net_1d > 0:
            momentum = main_net + main_net_1d
            result.append((s["code"], momentum))
    result.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in result[:10]]


# 网络策略模拟（用 ZHB 字段近似 K 线）
def sim_strategy_02(stocks: List[Dict], top_n: int) -> List[str]:
    """策略 02: 周线多头（用 change_5d/20d/60d 近似周线趋势）。"""
    candidates = sorted(stocks, key=lambda x: x.get("mcap_yi", 0), reverse=True)[:top_n]
    result = []
    for s in candidates:
        c5 = _safe_float(s.get("change_5d", 0))
        c20 = _safe_float(s.get("change_20d", 0))
        c60 = _safe_float(s.get("change_60d", 0))
        # 简化版"周线多头"：5d > 0 且 20d > 0 且 60d > 0
        if c5 > 0 and c20 > 0 and c60 > 0:
            result.append(s["code"])
    return result[:10]


def sim_strategy_05(stocks: List[Dict], top_n: int) -> List[str]:
    """策略 05: W底形态（用 change_60d<-10 + change_20d>0 近似）。"""
    candidates = sorted(stocks, key=lambda x: _safe_float(x.get("amount", 0)), reverse=True)[:top_n]
    result = []
    for s in candidates:
        c60 = _safe_float(s.get("change_60d", 0))
        c20 = _safe_float(s.get("change_20d", 0))
        if c60 < -10 and c20 > 0:  # 60日大跌 + 20日反弹
            result.append(s["code"])
    return result[:10]


def sim_strategy_06(stocks: List[Dict], top_n: int) -> List[str]:
    """策略 06: 红三兵（用 streak_days >= 2 + change_5d > 0 近似）。"""
    candidates = sorted(stocks, key=lambda x: _safe_float(x.get("amount", 0)), reverse=True)[:top_n]
    result = []
    for s in candidates:
        streak = int(s.get("streak_days", 0) or 0)
        c5 = _safe_float(s.get("change_5d", 0))
        if streak >= 2 and c5 > 0:
            result.append(s["code"])
    return result[:10]


def sim_strategy_17(stocks: List[Dict], top_n: int) -> List[str]:
    """策略 17: 北向Top（北向数据不在 ZHB，用 mcap_yi 排序近似）。"""
    candidates = sorted(stocks, key=lambda x: x.get("mcap_yi", 0), reverse=True)[:top_n]
    return [s["code"] for s in candidates[:10]]


# 策略注册
SIM_STRATEGIES: Dict[str, Callable[[List[Dict], int], List[str]]] = {
    "04_core_discount": sim_strategy_04,
    "11_holder_concentration": sim_strategy_11,
    "12_divergence_warning": sim_strategy_12,
    "13_dividend_yield": sim_strategy_13,
    "19_52w_position": sim_strategy_19,
    "20_main_fund_ratio": sim_strategy_20,
    "21_volume_acceleration": sim_strategy_21,
    "22_capital_momentum": sim_strategy_22,
    "02_weekly_ma": sim_strategy_02,
    "05_double_bottom": sim_strategy_05,
    "06_three_soldiers": sim_strategy_06,
    "17_northbound_top": sim_strategy_17,
}


# ═══════════════════════════════════════
# 评估指标
# ═══════════════════════════════════════

def calc_coverage(top_n_stocks: Set[str], strategy_results: Dict[str, Set[str]]) -> Dict[str, float]:
    """计算每个策略的覆盖率（top_n 中被选中的占比）。"""
    result = {}
    for strategy_name, selected in strategy_results.items():
        if not selected:
            result[strategy_name] = 0.0
            continue
        # 策略选中的股票是否在 top_n 范围内
        hit = len(selected & top_n_stocks)
        result[strategy_name] = hit / len(selected) if selected else 0.0
    return result


def calc_stability(day_results: List[Set[str]]) -> float:
    """计算 4 天结果的稳定性（0-1，越高越稳定）。"""
    if len(day_results) < 2:
        return 0.0
    # 用 Jaccard 相似度的平均值
    jaccards = []
    for i in range(len(day_results)):
        for j in range(i + 1, len(day_results)):
            a, b = day_results[i], day_results[j]
            if not a and not b:
                continue
            jaccards.append(len(a & b) / len(a | b) if a | b else 0.0)
    return sum(jaccards) / len(jaccards) if jaccards else 0.0


# ═══════════════════════════════════════
# 主回测流程
# ═══════════════════════════════════════

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📊 V14.3.2 Top-N 回测验证（{len(DAYS)} 天 × {len(TOP_N_CANDIDATES)} 个 top_n × {len(SIM_STRATEGIES)} 个策略）")
    print(f"  输出目录: {OUTPUT_DIR.relative_to(ROOT)}")
    print()

    # 1. 加载 4 天 ZHB 数据
    snapshots: Dict[str, List[Dict]] = {}
    for day in DAYS:
        raw = load_zhb_snapshot(day)
        # 补全字段
        stocks = [enrich_stock(s) for s in raw.values()]
        # 过滤停牌股（amount=0 或 None）
        stocks = [s for s in stocks if s.get("amount") is not None and s.get("amount", 0) > 0]
        snapshots[day] = stocks
        print(f"  ✅ {day}: {len(stocks)} 只非停牌股")

    # 2. 每天对每个 top_n 跑每个策略
    # 核心评估指标（V14.3.2 修正）：
    #   - "selected_count" = 策略在该 top_n 下选出的数量（反映 top_n 是否够大）
    #   - "hit_in_top_n" = 策略选中的股票是否在 top_n 范围内
    #   - "stability_score" = 与下一个 top_n 候选的 Jaccard 相似度（稳定性）
    # 核心目标：找出"能稳定选到 5+ 个结果的最小 top_n"
    results: List[Dict[str, Any]] = []
    # 跨天结果缓存：{(strategy, top_n): [day1_results, day2_results, day3_results, day4_results]}
    cross_day_results: Dict[Tuple[str, int], List[Set[str]]] = {}
    for day in DAYS:
        all_stocks = snapshots[day]
        # 按 amount 排序的全市场 top_n 集合
        by_amount = sorted(all_stocks, key=lambda x: _safe_float(x.get("amount", 0)), reverse=True)
        for top_n in TOP_N_CANDIDATES:
            top_n_stocks = {s["code"] for s in by_amount[:top_n]}
            for strategy_name, strategy_fn in SIM_STRATEGIES.items():
                try:
                    candidates = by_amount[:top_n]
                    selected = strategy_fn(candidates, top_n)
                    selected_set = set(selected)
                    if (strategy_name, top_n) not in cross_day_results:
                        cross_day_results[(strategy_name, top_n)] = []
                    cross_day_results[(strategy_name, top_n)].append(selected_set)
                    in_topn = len(selected_set & top_n_stocks)
                    coverage = in_topn / top_n if top_n > 0 else 0
                    results.append({
                        "day": day,
                        "top_n": top_n,
                        "strategy": strategy_name,
                        "selected_count": len(selected_set),
                        "hit_in_top_n": in_topn,
                        "coverage": round(coverage, 4),
                    })
                except Exception as e:
                    print(f"  ⚠️ {day} top_n={top_n} {strategy_name} 失败: {e}")

    # 3. 输出 daily CSV
    daily_csv = OUTPUT_DIR / "backtest_daily.csv"
    with open(daily_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["day", "top_n", "strategy", "selected_count", "hit_in_top_n", "coverage"])
        writer.writeheader()
        writer.writerows(results)
    print(f"\n  📄 每日明细: {daily_csv.relative_to(ROOT)}")

    # 4. 汇总：每个策略 × top_n 在 4 天的平均选择数 + 稳定性
    summary: Dict[str, Dict[int, Dict[str, float]]] = {}
    for r in results:
        strategy = r["strategy"]
        top_n = r["top_n"]
        if strategy not in summary:
            summary[strategy] = {}
        if top_n not in summary[strategy]:
            summary[strategy][top_n] = {"selected_sum": 0, "count": 0, "hit_sum": 0}
        summary[strategy][top_n]["selected_sum"] += r["selected_count"]
        summary[strategy][top_n]["count"] += 1
        summary[strategy][top_n]["hit_sum"] += r["hit_in_top_n"]

    # V14.3.2: 计算 4 天 Jaccard 稳定性
    def _jaccard_stability(day_results: List[Set[str]]) -> float:
        """计算跨天 Jaccard 相似度均值（0-1）。"""
        if len(day_results) < 2:
            return 0.0
        jaccards = []
        for i in range(len(day_results)):
            for j in range(i + 1, len(day_results)):
                a, b = day_results[i], day_results[j]
                if not a and not b:
                    continue
                union = a | b
                if not union:
                    continue
                jaccards.append(len(a & b) / len(union))
        return sum(jaccards) / len(jaccards) if jaccards else 0.0

    # 输出汇总 CSV（含稳定性）
    summary_csv = OUTPUT_DIR / "backtest_summary.csv"
    with open(summary_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["strategy", "top_n", "avg_selected", "avg_hit_in_top_n", "stability_jaccard", "sample_size"])
        for strategy in sorted(summary.keys()):
            for top_n in TOP_N_CANDIDATES:
                if top_n in summary[strategy]:
                    d = summary[strategy][top_n]
                    avg_sel = d["selected_sum"] / d["count"] if d["count"] else 0
                    avg_hit = d["hit_sum"] / d["count"] if d["count"] else 0
                    stab = _jaccard_stability(cross_day_results.get((strategy, top_n), []))
                    writer.writerow([strategy, top_n, round(avg_sel, 2), round(avg_hit, 2), round(stab, 4), d["count"]])
    print(f"  📄 汇总表: {summary_csv.relative_to(ROOT)}")

    # 5. 推荐每个策略的最优 top_n（V14.3.2 改进：稳定性优先）
    # 规则：找"能稳定选到 8+ 结果的最小 top_n"（_top5_sorted 实际返回 10）
    #     + 4 天 Jaccard 稳定性 >= 0.5（说明选股稳定）
    recommendations: Dict[str, Dict[str, Any]] = {}
    for strategy in sorted(summary.keys()):
        # 按 top_n 升序找到第一个"平均选中数 >= 8 且 4 天 Jaccard >= 0.5"的 top_n
        recommended = None
        saturation_data: Dict[int, float] = {}
        stability_data: Dict[int, float] = {}
        for top_n in TOP_N_CANDIDATES:
            if top_n in summary[strategy]:
                avg_sel = summary[strategy][top_n]["selected_sum"] / summary[strategy][top_n]["count"]
                saturation_data[top_n] = avg_sel
                stability_data[top_n] = _jaccard_stability(cross_day_results.get((strategy, top_n), []))
        # 规则 1：第一个"平均 >= 8 且 Jaccard >= 0.5"的 top_n
        for top_n in TOP_N_CANDIDATES:
            if top_n in saturation_data and saturation_data[top_n] >= 8 and stability_data[top_n] >= 0.5:
                recommended = top_n
                break
        # 规则 2：如果都 < 8，取"max selected"的 top_n
        if recommended is None and saturation_data:
            recommended = max(saturation_data, key=lambda t: saturation_data[t])
        recommendations[strategy] = {
            "recommended_top_n": recommended,
            "saturation_curve": saturation_data,
            "stability_curve": stability_data,
        }

    rec_json = OUTPUT_DIR / "backtest_recommendations.json"
    with open(rec_json, "w", encoding="utf-8") as f:
        json.dump(recommendations, f, ensure_ascii=False, indent=2)
    print(f"  📄 推荐表: {rec_json.relative_to(ROOT)}")

    # 6. 输出报告
    print(f"\n📋 推荐 Top-N（按策略）：")
    print(f"{'策略':<32} {'推荐 top_n':<10} {'选中数曲线':<55} {'稳定性曲线':<25}")
    print("-" * 130)
    for strategy in sorted(recommendations.keys()):
        r = recommendations[strategy]
        sat_curve = r["saturation_curve"]
        stab_curve = r.get("stability_curve", {})
        sat_str = " | ".join(f"{t}:{sat_curve.get(t, 0):.1f}" for t in TOP_N_CANDIDATES)
        stab_str = " | ".join(f"{t}:{stab_curve.get(t, 0):.2f}" for t in TOP_N_CANDIDATES)
        print(f"{strategy:<32} {str(r['recommended_top_n']):<10} {sat_str:<55} {stab_str:<25}")

    print(f"\n✅ 回测完成！详见 {OUTPUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""analyze_history.py — V8 A股历史快照对比分析

独立脚本，用于检测评分与股价的背离信号。
仅读取本地快照，不发起网络请求。

目录结构：
snapshots/
├── snapshot_YYYYMMDD_script.json  # 评分快照（保留4天）
└── analyze_YYYYMMDD.txt           # 分析报告（保留2天）

使用方式：
1. 手动运行: python analyze_history.py
2. 自动运行: main.py 末尾自动调用

背离信号检测：
- 连续3天评分上升但股价不涨（或涨幅很小）
- 连续3天评分下降但股价上涨
"""

from __future__ import annotations

import os
import sys
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# 配置
SNAPSHOT_DIR = "snapshots"
SNAPSHOT_RETENTION_DAYS = 4  # JSON快照保留4天
REPORT_RETENTION_DAYS = 2     # TXT报告保留2天
MAX_LOOKBACK_DAYS = 30        # 最多往前找30天
MIN_CHANGE_THRESHOLD = 3.0    # 评分变化阈值（%）
MIN_PRICE_CHANGE = 2.0        # 股价变化阈值（%）

# 脚本优先级：full > val > mak > med > lng > sht
SCRIPT_PRIORITY = {"full": 6, "val": 5, "mak": 4, "med": 3, "lng": 2, "sht": 1}


def ensure_snapshot_dir():
    """确保 snapshots/ 目录存在"""
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def cleanup_old_files():
    """清理过期文件"""
    now = datetime.now()
    
    for f in os.listdir(SNAPSHOT_DIR):
        filepath = os.path.join(SNAPSHOT_DIR, f)
        if not os.path.isfile(filepath):
            continue
        
        # 解析日期
        match = re.match(r'snapshot_(\d{8})_', f)
        if match:
            # JSON快照：保留4天
            try:
                file_date = datetime.strptime(match.group(1), "%Y%m%d")
                if (now - file_date).days > SNAPSHOT_RETENTION_DAYS:
                    os.remove(filepath)
            except Exception:
                pass
        
        match = re.match(r'analyze_(\d{8})\.txt', f)
        if match:
            # TXT报告：保留2天
            try:
                file_date = datetime.strptime(match.group(1), "%Y%m%d")
                if (now - file_date).days > REPORT_RETENTION_DAYS:
                    os.remove(filepath)
            except Exception:
                pass


def load_snapshot(date_str: str, script_type: str = None) -> Dict[str, Any]:
    """加载某一天的快照
    
    Args:
        date_str: 日期字符串 YYYYMMDD
        script_type: 脚本类型（ful/val/mak/med/lng/sht），None表示加载所有并按优先级合并
    
    Returns:
        股票评分数据 {"code": {"name": "...", "total_score": 85.2, "price": 1680.5, "report_source": "ful"}}
    """
    if script_type:
        # 加载指定类型的快照
        filepath = os.path.join(SNAPSHOT_DIR, f"snapshot_{date_str}_{script_type}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("stocks", {})
            except Exception:
                pass
        return {}
    
    # 原始逻辑：按优先级合并所有类型
    merged = {}
    for script, _ in SCRIPT_PRIORITY.items():
        filepath = os.path.join(SNAPSHOT_DIR, f"snapshot_{date_str}_{script}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    stocks = data.get("stocks", {})
                    for code, info in stocks.items():
                        if code not in merged or SCRIPT_PRIORITY.get(info.get("report_source", ""), 0) > SCRIPT_PRIORITY.get(merged[code].get("report_source", ""), 0):
                            merged[code] = info
            except Exception:
                pass
    return merged


def find_recent_snapshots(today_date: datetime) -> List[str]:
    """找最近的有效快照日期（跳过非交易日）"""
    valid_dates = []
    
    for offset in range(1, MAX_LOOKBACK_DAYS + 1):
        check_date = today_date - timedelta(days=offset)
        date_str = check_date.strftime("%Y%m%d")
        
        # 检查是否有快照文件
        has_snapshot = False
        for script in SCRIPT_PRIORITY.keys():
            if os.path.exists(os.path.join(SNAPSHOT_DIR, f"snapshot_{date_str}_{script}.json")):
                has_snapshot = True
                break
        
        if has_snapshot:
            valid_dates.append(date_str)
            if len(valid_dates) >= 3:
                break
    
    return valid_dates


def detect_divergence(stocks_history: Dict[str, List[Dict]]) -> List[Dict]:
    """检测背离信号"""
    signals = []
    
    for code, history in stocks_history.items():
        if len(history) < 3:
            continue
        
        # 按日期排序（最近的在前）
        history_sorted = sorted(history, key=lambda x: x["date"], reverse=True)
        
        # 最近3天的数据
        d1 = history_sorted[0]  # 最近
        d2 = history_sorted[1]  # 中间
        d3 = history_sorted[2]  # 最远
        
        score_d1 = d1.get("total_score", 0)
        score_d2 = d2.get("total_score", 0)
        score_d3 = d3.get("total_score", 0)
        
        price_d1 = d1.get("price", 0)
        price_d2 = d2.get("price", 0)
        price_d3 = d3.get("price", 0)
        
        # 计算变化
        score_change = score_d1 - score_d3
        if score_d3 > 0:
            score_change_pct = score_change / score_d3 * 100
        else:
            score_change_pct = 0
        
        price_change = 0
        price_change_pct = 0
        if price_d3 > 0:
            price_change = price_d1 - price_d3
            price_change_pct = price_change / price_d3 * 100
        
        name = d1.get("name", "")
        
        # 信号1：评分连续上升但股价涨幅小
        if score_d1 > score_d2 > score_d3 and score_change_pct >= MIN_CHANGE_THRESHOLD and abs(price_change_pct) < MIN_PRICE_CHANGE:
            signals.append({
                "code": code,
                "name": name,
                "type": "bullish_divergence",
                "score_trend": f"{score_d3:.1f} → {score_d2:.1f} → {score_d1:.1f}",
                "price_trend": f"{price_d3:.2f} → {price_d2:.2f} → {price_d1:.2f}",
                "score_change_pct": round(score_change_pct, 1),
                "price_change_pct": round(price_change_pct, 1),
                "dates": [d3["date"], d2["date"], d1["date"]],
            })
        
        # 信号2：评分连续下降但股价上涨
        if score_d1 < score_d2 < score_d3 and score_change_pct <= -MIN_CHANGE_THRESHOLD and price_change_pct >= MIN_PRICE_CHANGE:
            signals.append({
                "code": code,
                "name": name,
                "type": "bearish_divergence",
                "score_trend": f"{score_d3:.1f} → {score_d2:.1f} → {score_d1:.1f}",
                "price_trend": f"{price_d3:.2f} → {price_d2:.2f} → {price_d1:.2f}",
                "score_change_pct": round(score_change_pct, 1),
                "price_change_pct": round(price_change_pct, 1),
                "dates": [d3["date"], d2["date"], d1["date"]],
            })
    
    return signals


def generate_report(signals: List[Dict], today_str: str, recent_dates: List[str]) -> str:
    """生成分析报告"""
    lines = []
    lines.append("═" * 70)
    lines.append(f"  A股历史快照对比分析报告 {today_str}")
    lines.append("═" * 70)
    lines.append("")
    
    if not recent_dates:
        lines.append("  ⚠️ 警告：未找到历史快照数据")
        lines.append("  请先运行 main.py 抓取数据，快照会自动保存到 snapshots/ 目录")
        lines.append("")
        lines.append("═" * 70)
        return "\n".join(filter(None, lines))
    
    lines.append(f"  📊 分析周期: {recent_dates[-1]} → {recent_dates[0]}")
    lines.append(f"  📈 对比天数: {len(recent_dates)} 天")
    lines.append("")
    
    if not signals:
        lines.append("  ✅ 未检测到明显背离信号")
        lines.append("")
        lines.append("═" * 70)
        return "\n".join(filter(None, lines))
    
    # 按类型分组
    bullish = [s for s in signals if s["type"] == "bullish_divergence"]
    bearish = [s for s in signals if s["type"] == "bearish_divergence"]
    
    if bullish:
        lines.append("  🔥 看涨背离信号（评分上升，股价横盘）")
        lines.append("  ──────────────────────────────────────")
        for s in bullish:
            lines.append(f"")
            lines.append(f"  ⚠️ {s['code']} {s['name']}")
            lines.append(f"     评分趋势: {s['score_trend']} ({s['score_change_pct']:+.1f}%)")
            lines.append(f"     股价趋势: {s['price_trend']} ({s['price_change_pct']:+.1f}%)")
            lines.append(f"     日期范围: {s['dates'][0]} ~ {s['dates'][2]}")
            lines.append(f"     建议: 关注潜在上涨机会")
    
    if bearish:
        lines.append("")
        lines.append("  💀 看跌背离信号（评分下降，股价上涨）")
        lines.append("  ──────────────────────────────────────")
        for s in bearish:
            lines.append(f"")
            lines.append(f"  ⚠️ {s['code']} {s['name']}")
            lines.append(f"     评分趋势: {s['score_trend']} ({s['score_change_pct']:+.1f}%)")
            lines.append(f"     股价趋势: {s['price_trend']} ({s['price_change_pct']:+.1f}%)")
            lines.append(f"     日期范围: {s['dates'][0]} ~ {s['dates'][2]}")
            lines.append(f"     建议: 警惕回调风险")
    
    lines.append("")
    lines.append("═" * 70)
    lines.append(f"  注：报告保留 {REPORT_RETENTION_DAYS} 天，快照保留 {SNAPSHOT_RETENTION_DAYS} 天")
    
    return "\n".join(filter(None, lines))


def analyze_history(force_run: bool = False) -> str:
    """核心分析函数（可被 main.py 调用）"""
    ensure_snapshot_dir()
    cleanup_old_files()
    
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    
    # 找最近的快照日期
    recent_dates = find_recent_snapshots(today)
    
    if not recent_dates and not force_run:
        return "⚠️ 未找到历史快照数据，跳过分析"
    
    # 加载历史数据
    stocks_history: Dict[str, List[Dict]] = {}
    for date_str in recent_dates:
        snapshot = load_snapshot(date_str)
        for code, info in snapshot.items():
            if code not in stocks_history:
                stocks_history[code] = []
            stocks_history[code].append({
                "date": date_str,
                "total_score": info.get("total_score", 0),
                "price": info.get("price", 0),
                "name": info.get("name", ""),
            })
    
    # 检测背离信号
    signals = detect_divergence(stocks_history)
    
    # 生成报告
    report = generate_report(signals, today_str, recent_dates)
    
    # 保存报告
    report_file = os.path.join(SNAPSHOT_DIR, f"analyze_{today.strftime('%Y%m%d')}.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report


def save_snapshot(script_type: str, stocks_data: Dict[str, Any]):
    """保存快照（智能合并模式）
    
    Args:
        script_type: 脚本类型（ful/val/mak/med/lng/sht）
        stocks_data: 股票评分数据 {"code": {"name": "...", "total_score": 85.2, "price": 1680.5}}
    """
    ensure_snapshot_dir()
    
    today = datetime.now()
    date_str = today.strftime("%Y%m%d")
    snapshot_file = os.path.join(SNAPSHOT_DIR, f"snapshot_{date_str}_{script_type}.json")
    
    # 加载现有数据（如果存在）
    existing = {}
    if os.path.exists(snapshot_file):
        try:
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                existing = data.get("stocks", {})
        except Exception:
            pass
    
    # 合并：新数据覆盖旧数据（同股票）
    existing.update(stocks_data)
    
    # 保存
    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump({
            "date": date_str,
            "script_type": script_type,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stock_count": len(existing),
            "stocks": existing
        }, f, ensure_ascii=False, indent=2)


def main():
    """命令行运行入口"""
    report = analyze_history(force_run=True)
    print(report)
    print()


if __name__ == "__main__":
    main()
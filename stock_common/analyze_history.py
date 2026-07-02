#!/usr/bin/env python3
"""analyze_history.py — 评分快照历史分析与背离检测 (V9.0)

功能：
  - save_snapshot(): 保存单只股票评分快照（智能合并模式）
  - analyze_history(): 扫描 snapshots/ 目录，做跨日期趋势背离检测，返回文本报告
  - 生成分析记录文件：reports/analysis_history_<YYYYMMDD>.txt
  - 自动GD上传：快照文件自动上传到 a-stock-data/snapshot/ 文件夹

背离检测语义（跨日期趋势背离）：
  对同一只股票的同一报告类型(sht/med/lng/ful)，比较其在不同交易日的评分：
  - 突变背离：单日评分变化幅度 ≥ DIVERGENCE_THRESHOLD（默认 ±15 分）
  - 趋势信号：连续同向变化 ≥ TREND_MIN_DAYS 天且每日变化 ≥ TREND_STEP_THRESHOLD（默认 ±5 分）

调用方：
  - stock_common.save_score_snapshot() → save_snapshot(script_type, stocks_dict)
  - main.py → analyze_history() 无参数，返回 str 直接 print

快照文件格式（snapshots/snapshot_YYYYMMDD_HHmm.txt）：
  # 评分快照生成时间: 2026-06-25 10:30:45
  # 生成脚本类型: ful
  # 股票总数: 31
  #
  # 股票数据格式：股票代码: {'name': 名称, 'total_score': 评分, 'price': 价格, 'report_source': 类型}
  #================================================================================
  
  600519: {'name': '贵州茅台', 'total_score': 72.5, 'price': 1680.50, 'report_source': 'ful'}

GD上传功能：
  - 自动上传快照文件到 Google Drive
  - 上传路径：a-stock-data/snapshot/
  - 支持错误处理和重试机制
  - 上传失败不影响快照文件本地保存
"""

from __future__ import annotations

import json
import os
import glob
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# 导入GD上传相关模块
try:
    from gd_uploader import init_gd, upload_type_reports, cleanup_gd_proxy, retry_get_folder_interactive, upload_report_to_drive
    GD_AVAILABLE = True
except ImportError:
    GD_AVAILABLE = False

# ═══════════════════════════════════════════════════════════
# 路径与阈值配置
# ═══════════════════════════════════════════════════════════
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOT_DIR = os.path.join(_SCRIPT_DIR, "snapshots")

# 单日评分突变阈值（分）：|Δ| ≥ 此值视为背离
DIVERGENCE_THRESHOLD = 15.0
# 趋势检测：连续同向变化的最小天数
TREND_MIN_DAYS = 3
# 趋势检测：显著性门槛（总变化幅度需达到此值才算显著趋势，复用突变阈值）
TREND_SIGNIFICANCE = DIVERGENCE_THRESHOLD

# 报告类型中文名
TYPE_LABELS = {"sht": "短线", "med": "中线", "lng": "长线", "ful": "全维度", "val": "估值", "mak": "热点"}


# ═══════════════════════════════════════════════════════════
# save_snapshot：智能合并写盘
# ═══════════════════════════════════════════════════════════
def save_snapshot(script_type: str, stocks: Dict[str, Any]) -> None:
    """保存每日快照（JSON格式）到 snapshots/ 目录。

    每个脚本类型运行完成后调用，生成JSON快照。
    跨日期对比分析统一由 analyze_history() 在 main.py 末尾完成。
    """
    if not stocks:
        return
    generate_daily_snapshot(script_type, stocks)


def _upload_snapshot_to_gd(snapshot_path: str) -> None:
    """上传快照文件到Google Drive的snapshot文件夹"""
    try:
        # 初始化GD连接
        drive, proxy_set, parent_id, skip_upload = init_gd(os.path.dirname(SNAPSHOT_DIR))
        
        if not drive or skip_upload:
            print("  ⚠️ GD连接失败或用户选择跳过上传", flush=True)
            return
            
        # 确保snapshot文件夹存在
        snapshot_id = retry_get_folder_interactive(drive, "snapshot", parent_id, max_auto_retry=3)
        if not snapshot_id:
            print("  ⚠️ GD snapshot文件夹获取失败", flush=True)
            return
        
        # 上传快照文件
        filename = os.path.basename(snapshot_path)
        if upload_report_to_drive(drive, snapshot_path, snapshot_id, filename):
            print(f"  ✅ 快照已上传到GD: snapshot/{filename}", flush=True)
        else:
            print(f"  ⚠️ 快照GD上传失败: {filename}", flush=True)
            
        # 清理代理
        cleanup_gd_proxy(proxy_set)
        
    except Exception as e:
        print(f"  ⚠️ GD上传过程异常: {e}", flush=True)


# ═══════════════════════════════════════════════════════════
# analyze_history：扫描快照 + 跨日期趋势背离检测
# ═══════════════════════════════════════════════════════════
def _load_all_snapshots() -> List[Dict[str, Any]]:
    """加载 snapshots/ 目录下所有快照文件，按日期升序返回。"""
    pattern = os.path.join(SNAPSHOT_DIR, "snapshot_*.json")
    snapshots: List[Dict[str, Any]] = []
    for path in sorted(glob.glob(pattern)):
        try:
            with open(path, "r", encoding="utf-8") as f:
                snapshot_data = json.load(f)
                snapshots.append(snapshot_data)
        except Exception as e:
            print(f"  ⚠️ 加载快照文件失败 {os.path.basename(path)}: {e}")
            continue
    # 按日期升序排序
    snapshots.sort(key=lambda x: x.get("date", ""))
    return snapshots


def _build_series(snapshots: List[Dict[str, Any]]) -> Dict[Tuple[str, str], List[Tuple[str, float, str]]]:
    """按 (股票代码, 报告类型) 分组，收集「日期→评分」序列。

    Returns:
        {(code, script_type): [(date_str, score, name), ...]} 每个序列按日期升序
    """
    series: Dict[Tuple[str, str], List[Tuple[str, float, str]]] = {}
    for snap in snapshots:
        date_str = snap.get("date", "")
        script_type = snap.get("script_type", "")
        for code, info in snap.get("stocks", {}).items():
            if not isinstance(info, dict):
                continue
            try:
                score = round(float(info.get("total_score", 0)), 1)
            except (TypeError, ValueError):
                continue
            name = info.get("name", "")
            key = (code, script_type)
            series.setdefault(key, []).append((date_str, score, name))
    return series


def _detect_divergences(series: Dict[Tuple[str, str], List[Tuple[str, float, str]]]
                        ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """检测突变背离与连续趋势。

    Returns:
        (divergences, trends)
        divergences: 单日评分突变列表，按变化幅度降序
        trends: 连续同向趋势列表
    """
    divergences: List[Dict[str, Any]] = []
    trends: List[Dict[str, Any]] = []

    for (code, script_type), points in series.items():
        if len(points) < 2:
            continue
        # points 已按日期升序
        name = points[-1][2] or code

        # —— 突变检测：相邻日期评分变化 ——
        for i in range(1, len(points)):
            prev_date, prev_score, _ = points[i - 1]
            curr_date, curr_score, _ = points[i]
            delta = round(curr_score - prev_score, 1)
            if abs(delta) >= DIVERGENCE_THRESHOLD:
                divergences.append({
                    "code": code, "name": name, "type": script_type,
                    "from_date": prev_date, "to_date": curr_date,
                    "from_score": prev_score, "to_score": curr_score,
                    "delta": delta,
                })

        # —— 趋势检测：连续同向变化（允许中间小幅波动）——
        if len(points) >= TREND_MIN_DAYS:
            # 计算每步变化
            steps = []
            for i in range(1, len(points)):
                d = round(points[i][1] - points[i - 1][1], 1)
                steps.append(d)
            # 寻找最长连续同向子序列（每个非零 step 方向一致即连续，0 视为可忽略）
            best_run: Optional[Tuple[int, int, int]] = None  # (start_idx, length, direction)
            run_start = 0
            run_dir = 0
            run_len = 0
            for i, d in enumerate(steps):
                cur_dir = 1 if d > 0 else (-1 if d < 0 else 0)
                if cur_dir == 0:
                    # 变化为0，跳过但不打断当前趋势
                    continue
                if run_dir != 0 and cur_dir == run_dir:
                    run_len += 1
                else:
                    # 方向反转或首次，开启新序列
                    run_start = i
                    run_dir = cur_dir
                    run_len = 1
                if run_len + 1 >= TREND_MIN_DAYS and (best_run is None or run_len > best_run[1]):
                    best_run = (run_start, run_len, run_dir)
            if best_run is not None:
                start_idx, length, direction = best_run
                # 趋势覆盖的日期区间：start_idx 对应 points[start_idx] 到 points[start_idx+length]
                from_date = points[start_idx][0]
                to_date = points[start_idx + length][0]
                from_score = points[start_idx][1]
                to_score = points[start_idx + length][1]
                total_delta = round(to_score - from_score, 1)
                # 总变化幅度需达到显著性门槛才算显著趋势，避免小步累加的噪音
                if abs(total_delta) >= TREND_SIGNIFICANCE:
                    arrow = "持续上涨📈" if direction > 0 else "持续下跌📉"
                    trends.append({
                        "code": code, "name": name, "type": script_type,
                        "from_date": from_date, "to_date": to_date,
                        "from_score": from_score, "to_score": to_score,
                        "delta": total_delta, "days": length + 1,
                        "arrow": arrow,
                    })

    # 突变按变化幅度绝对值降序
    divergences.sort(key=lambda x: abs(x["delta"]), reverse=True)
    # 趋势按总变化幅度绝对值降序
    trends.sort(key=lambda x: abs(x["delta"]), reverse=True)
    return divergences, trends


def _fmt_score(s: float) -> str:
    """格式化评分为字符串，去除浮点尾差。"""
    return f"{round(s, 1):.1f}"


def analyze_history() -> str:
    """扫描 snapshots/ 目录，做跨日期趋势背离检测，返回文本报告。

    无参数，返回可直接 print 的字符串。
    """
    lines: List[str] = []
    L = lines.append

    L("=" * 60)
    L("  📈 评分快照历史分析（跨日期趋势背离检测）")
    L("=" * 60)

    snapshots = _load_all_snapshots()
    if not snapshots:
        L("  📝 未找到历史评分，本次评分已写入缓存。")
        L("  📈 跨日期分析需要至少两个交易日的数据进行对比。")
        L("=" * 60)
        return "\n".join(lines)

    # 概览统计
    dates = sorted({s.get("date", "") for s in snapshots})
    types = sorted({s.get("script_type", "") for s in snapshots})
    all_codes = set()
    for snap in snapshots:
        all_codes.update(snap.get("stocks", {}).keys())

    L(f"  覆盖交易日   : {len(dates)} 天 ({dates[0]} ~ {dates[-1]})" if len(dates) > 1
      else f"  覆盖交易日   : {dates[0] if dates else '无'}")
    L(f"  报告类型     : {', '.join(TYPE_LABELS.get(t, t) for t in types)}")
    L(f"  涉及股票数   : {len(all_codes)} 只")
    L("-" * 60)

    series = _build_series(snapshots)
    # 只有多日数据的序列才有分析价值
    multi_day_series = {k: v for k, v in series.items() if len(v) >= 2}

    if not multi_day_series:
        L("  ℹ️ 当前仅有单日快照数据，无法进行跨日期趋势分析。")
        L("  积累多日快照后即可自动检测评分突变与连续趋势背离。")
        L("=" * 60)
        return "\n".join(lines)

    divergences, trends = _detect_divergences(multi_day_series)

    # 多日序列统计
    multi_count = len(multi_day_series)
    L(f"  可分析序列   : {multi_count} 个（同一股票同一类型有多日数据）")
    L("=" * 60)

    # —— 突变背离清单 ——
    L("")
    L("【一、评分突变背离】")
    L(f"  阈值：单日评分变化 |Δ| ≥ {DIVERGENCE_THRESHOLD:.0f} 分")
    if divergences:
        L(f"  共检测到 {len(divergences)} 处突变：")
        L("")
        L(f"  {'代码':<8} {'名称':<10} {'类型':<6} {'日期区间':<22} {'评分变化':<16} {'幅度':>7}")
        L("  " + "-" * 80)
        for d in divergences[:30]:  # 最多展示30条
            date_range = f"{d['from_date']}→{d['to_date']}"
            score_chg = f"{_fmt_score(d['from_score'])}→{_fmt_score(d['to_score'])}"
            arrow = "↑" if d["delta"] > 0 else "↓"
            delta_str = f"{arrow}{abs(d['delta']):.1f}"
            L(f"  {d['code']:<8} {d['name'][:8]:<10} {TYPE_LABELS.get(d['type'], d['type']):<6} "
              f"{date_range:<22} {score_chg:<16} {delta_str:>7}")
        if len(divergences) > 30:
            L(f"  ... 另有 {len(divergences) - 30} 处未展示")
    else:
        L("  ✅ 未检测到单日评分突变，近期评分波动平稳。")

    # —— 连续趋势清单 ——
    L("")
    L("【二、连续趋势信号】")
    L(f"  阈值：连续 ≥ {TREND_MIN_DAYS} 天同向变化，总变化幅度 ≥ {TREND_SIGNIFICANCE:.0f} 分")
    if trends:
        L(f"  共检测到 {len(trends)} 个连续趋势：")
        L("")
        L(f"  {'代码':<8} {'名称':<10} {'类型':<6} {'日期区间':<22} {'评分变化':<16} {'方向':<10}")
        L("  " + "-" * 80)
        for t in trends[:30]:
            date_range = f"{t['from_date']}→{t['to_date']}"
            score_chg = f"{_fmt_score(t['from_score'])}→{_fmt_score(t['to_score'])}({t['days']}日)"
            L(f"  {t['code']:<8} {t['name'][:8]:<10} {TYPE_LABELS.get(t['type'], t['type']):<6} "
              f"{date_range:<22} {score_chg:<16} {t['arrow']:<10}")
        if len(trends) > 30:
            L(f"  ... 另有 {len(trends) - 30} 个趋势未展示")
    else:
        L("  ➖ 未检测到明显的连续同向趋势。")

    # —— 汇总结论 ——
    L("")
    L("=" * 60)
    if not divergences and not trends:
        L("  ✅ 近期评分整体平稳，未检测到明显背离或趋势。")
    else:
        parts = []
        if divergences:
            parts.append(f"{len(divergences)}处突变")
        if trends:
            parts.append(f"{len(trends)}个趋势")
        L(f"  📊 检测到 {'/'.join(parts)}，详情见上。建议关注评分剧烈变化的个股。")
    L("=" * 60)
    result = "\n".join(lines)
    # 仅在有异常时保存报告并上传GD
    if divergences or trends:
        try:
            txt_path = _save_analysis_report(result)
            if GD_AVAILABLE:
                _upload_snapshot_to_gd(txt_path)
        except Exception:
            pass
    return result


def _generate_analysis_report(snapshots, divergences, trends, dates, types, all_codes) -> str:
    """生成详细的分析报告文件内容"""
    from datetime import datetime
    
    content = []
    content.append(f"评分快照历史分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("=" * 80)
    content.append(f"分析日期范围: {dates[0] if dates else '无'} ~ {dates[-1] if dates else '无'}")
    content.append(f"覆盖报告类型: {', '.join(types)}")
    content.append(f"涉及股票数量: {len(all_codes)} 只")
    content.append(f"可分析序列数: {len([k for k, v in _build_series(snapshots).items() if len(v) >= 2])} 个")
    content.append("")
    
    if divergences:
        content.append("【评分突变背离记录】")
        content.append(f"阈值：单日评分变化 |Δ| ≥ {DIVERGENCE_THRESHOLD:.0f} 分")
        content.append(f"共检测到 {len(divergences)} 处突变：")
        content.append("")
        for d in divergences:
            content.append(f"股票代码: {d['code']} ({d['name']})")
            content.append(f"报告类型: {d['type']}")
            content.append(f"日期区间: {d['from_date']} → {d['to_date']}")
            content.append(f"评分变化: {d['from_score']} → {d['to_score']} (Δ={d['delta']:+.1f})")
            content.append("")
    
    if trends:
        content.append("【连续趋势信号记录】")
        content.append(f"阈值：连续 ≥ {TREND_MIN_DAYS} 天同向变化，总变化幅度 ≥ {TREND_SIGNIFICANCE:.0f} 分")
        content.append(f"共检测到 {len(trends)} 个连续趋势：")
        content.append("")
        for t in trends:
            content.append(f"股票代码: {t['code']} ({t['name']})")
            content.append(f"报告类型: {t['type']}")
            content.append(f"日期区间: {t['from_date']} → {t['to_date']} ({t['days']}日)")
            content.append(f"评分变化: {t['from_score']} → {t['to_score']} (Δ={t['delta']:+.1f})")
            content.append(f"趋势方向: {t['arrow']}")
            content.append("")
    
    if not divergences and not trends:
        content.append("分析结论：近期评分整体平稳，未检测到明显背离或趋势。")
    else:
        content.append("分析结论：检测到评分变化，建议关注相关个股的动态。")
    
    return "\n".join(content)


def _save_analysis_report(content: str) -> str:
    """保存异常分析报告到 snapshots/ 目录，返回文件路径"""
    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"anomaly_{now_str}.txt"
    filepath = os.path.join(SNAPSHOT_DIR, filename)
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  📄 异常报告已保存: {filepath}")
    return filepath


# ────────────────────────────────────────────────────────────────
# 4. 快照管理：按交易日清理和跨日期分析
# ────────────────────────────────────────────────────────────────
def generate_daily_snapshot(script_type: str, stocks: Dict[str, Any]) -> None:
    """生成每日快照（JSON格式）。
    
    每个脚本类型运行完成后调用，生成对应类型的JSON快照文件。
    
    Args:
        script_type: 报告类型（sht/med/lng/ful/val/mak）
        stocks: {股票代码: {name, total_score, price, report_source}} 本次要写入的股票
    """
    if not stocks:
        return
    try:
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)
        
        # 生成日期（使用当天的日期）
        today_str = datetime.now().strftime("%Y%m%d")
        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # JSON文件名：snapshot_YYYYMMDD_scriptType.json
        json_path = os.path.join(SNAPSHOT_DIR, f"snapshot_{today_str}_{script_type}.json")
        
        # 读取已有数据并合并
        existing_stocks: Dict[str, Any] = {}
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    existing_stocks = data.get("stocks", {})
            except (json.JSONDecodeError, OSError):
                existing_stocks = {}

        # 合并数据
        merged_stocks = existing_stocks.copy()
        merged_stocks.update(stocks)

        # 生成JSON快照
        snapshot_data = {
            "date": today_str,
            "script_type": script_type,
            "last_updated": now_ts,
            "stock_count": len(merged_stocks),
            "stocks": merged_stocks,
        }
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
        
        print(f"  📄 JSON快照已保存: {json_path}")
        
        # 清理旧文件
        cleanup_old_snapshots(script_type, keep_days=4)
        
    except Exception as e:
        print(f"  ⚠️ 快照保存失败: {e}")


def cleanup_old_snapshots(script_type: str, keep_days: int = 4) -> None:
    """清理旧的快照文件。
    
    保留每个脚本类型最近 keep_days 个交易日的文件，删除更早的。
    
    Args:
        script_type: 报告类型
        keep_days: 保留的交易日数量
    """
    try:
        pattern = os.path.join(SNAPSHOT_DIR, f"snapshot_*_{script_type}.json")
        snapshot_files = glob.glob(pattern)
        
        if len(snapshot_files) <= keep_days:
            return
        
        # 提取日期并排序
        date_files = []
        for file_path in snapshot_files:
            filename = os.path.basename(file_path)
            # 格式：snapshot_YYYYMMDD_scriptType.json
            date_part = filename.split('_')[1]  # YYYYMMDD
            date_files.append((date_part, file_path))
        
        # 按日期排序，保留最新的 keep_days 个
        date_files.sort(key=lambda x: x[0])
        files_to_keep = date_files[-keep_days:] if len(date_files) > keep_days else date_files
        files_to_delete = [f for f in date_files if f not in files_to_keep]
        
        # 删除旧文件
        for _, file_path in files_to_delete:
            try:
                os.remove(file_path)
                print(f"  🗑️ 已清理旧文件: {os.path.basename(file_path)}")
            except OSError:
                pass
                
    except Exception as e:
        print(f"  ⚠️ 清理旧文件失败: {e}")


def analyze_script_type(script_type: str, days: int = 3) -> Optional[Dict[str, Any]]:
    """分析特定脚本类型的跨日期趋势。
    
    Args:
        script_type: 报告类型
        days: 分析的交易日数量
        
    Returns:
        分析结果字典，包含突变和趋势信息，如果没有异常则返回None
    """
    try:
        # 获取指定类型的所有快照文件
        pattern = os.path.join(SNAPSHOT_DIR, f"snapshot_*_{script_type}.json")
        snapshot_files = glob.glob(pattern)
        
        if len(snapshot_files) < 2:
            return None  # 需要至少2天的数据才能分析
        
        # 提取日期并排序，取最近的days天
        date_files = []
        for file_path in snapshot_files:
            filename = os.path.basename(file_path)
            date_part = filename.split('_')[1]  # YYYYMMDD
            date_files.append((date_part, file_path))
        
        date_files.sort(key=lambda x: x[0])
        recent_files = date_files[-days:] if len(date_files) >= days else date_files
        
        # 加载数据
        snapshots = []
        for _, file_path in recent_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    snapshots.append(data)
            except (json.JSONDecodeError, OSError):
                continue
        
        if len(snapshots) < 2:
            return None
        
        # 分析趋势
        analysis_result = _analyze_snapshots_trend(snapshots)
        if analysis_result:
            analysis_result["script_type"] = script_type
            analysis_result["analysis_date"] = datetime.now().strftime("%Y-%m-%d")
            
        return analysis_result
        
    except Exception as e:
        print(f"  ⚠️ 分析趋势失败: {e}")
        return None


def _analyze_snapshots_trend(snapshots: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """分析快照数据中的趋势异常。"""
    try:
        anomalies = []
        
        # 获取所有股票代码
        all_codes = set()
        for snapshot in snapshots:
            all_codes.update(snapshot.get("stocks", {}).keys())
        
        # 对每个股票进行分析
        for code in all_codes:
            code_snapshots = []
            for snapshot in snapshots:
                stock_data = snapshot.get("stocks", {}).get(code)
                if stock_data:
                    code_snapshots.append({
                        "date": snapshot["date"],
                        "score": stock_data.get("total_score", 0)
                    })
            
            # 至少需要2天的数据才能分析
            if len(code_snapshots) >= 2:
                # 按日期排序
                code_snapshots.sort(key=lambda x: x["date"])
                
                # 检查突变背离
                for i in range(1, len(code_snapshots)):
                    prev_score = code_snapshots[i-1]["score"]
                    curr_score = code_snapshots[i]["score"]
                    score_diff = abs(curr_score - prev_score)
                    
                    if score_diff >= DIVERGENCE_THRESHOLD:
                        anomalies.append({
                            "type": "突变背离",
                            "code": code,
                            "date_from": code_snapshots[i-1]["date"],
                            "date_to": code_snapshots[i]["date"],
                            "score_change": f"{prev_score:.1f} → {curr_score:.1f}",
                            "diff": f"Δ={score_diff:+.1f}"
                        })
                
                # 检查连续趋势（至少3天）
                if len(code_snapshots) >= 3:
                    total_change = code_snapshots[-1]["score"] - code_snapshots[0]["score"]
                    if abs(total_change) >= 15:  # 总变化幅度≥15
                        # 检查是否连续同向
                        same_direction = True
                        for i in range(1, len(code_snapshots)):
                            prev = code_snapshots[i-1]["score"]
                            curr = code_snapshots[i]["score"]
                            if (prev - curr) * (total_change) < 0:
                                same_direction = False
                                break
                        
                        if same_direction:
                            anomalies.append({
                                "type": "连续趋势",
                                "code": code,
                                "date_range": f"{code_snapshots[0]['date']} → {code_snapshots[-1]['date']}",
                                "total_change": f"{total_change:+.1f}",
                                "days": len(code_snapshots)
                            })
        
        if anomalies:
            return {
                "has_anomaly": True,
                "anomalies": anomalies,
                "snapshot_count": len(snapshots)
            }
        else:
            return None
            
    except Exception as e:
        print(f"  ⚠️ 趋势分析失败: {e}")
        return None


def generate_warning_txt(analysis_result: Dict[str, Any]) -> str:
    """生成预警TXT文件。"""
    try:
        now_str = datetime.now().strftime("%Y%m%d_%H%M")
        txt_path = os.path.join(SNAPSHOT_DIR, f"snapshot_{now_str}.txt")
        
        script_type = analysis_result["script_type"]
        anomalies = analysis_result["anomalies"]
        
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"评分快照历史分析报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"分析日期: {analysis_result['analysis_date']}\n")
            f.write(f"报告类型: {TYPE_LABELS.get(script_type, script_type)}\n")
            f.write(f"快照数量: {analysis_result['snapshot_count']} 个\n")
            f.write(f"异常数量: {len(anomalies)} 处\n\n")
            
            f.write("【评分突变背离记录】\n")
            f.write("阈值：单日评分变化 |Δ| ≥ 15 分\n")
            f.write("-" * 80 + "\n")
            
            mutation_count = 0
            for anomaly in anomalies:
                if anomaly["type"] == "突变背离":
                    mutation_count += 1
                    f.write(f"股票代码: {anomaly['code']}\n")
                    f.write(f"日期区间: {anomaly['date_from']} → {anomaly['date_to']}\n")
                    f.write(f"评分变化: {anomaly['score_change']} ({anomaly['diff']})\n\n")
            
            if mutation_count == 0:
                f.write("未检测到突变背离\n\n")
            
            f.write("【连续趋势信号记录】\n")
            f.write("阈值：连续 ≥ 3 天同向变化，总变化幅度 ≥ 15 分\n")
            f.write("-" * 80 + "\n")
            
            trend_count = 0
            for anomaly in anomalies:
                if anomaly["type"] == "连续趋势":
                    trend_count += 1
                    f.write(f"股票代码: {anomaly['code']}\n")
                    f.write(f"日期区间: {anomaly['date_range']} ({anomaly['days']}日)\n")
                    f.write(f"评分变化: {anomaly['total_change']}\n")
                    f.write(f"趋势方向: {'↗️ 上升' if float(anomaly['total_change']) > 0 else '↘️ 下降'}\n\n")
            
            if trend_count == 0:
                f.write("未检测到连续趋势\n\n")
            
            f.write("分析结论：检测到评分异常变化，建议关注相关个股的动态。\n")
        
        print(f"  📄 预警TXT已生成: {txt_path}")
        return txt_path
        
    except Exception as e:
        print(f"  ⚠️ 生成预警TXT失败: {e}")
        return ""


if __name__ == "__main__":
    print(analyze_history())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collide.py — 全源全字段通用对撞引擎（每日增量、按字典状态跟进）

设计目标
--------
取代原先"针对个别字段"的定向脚本（crack_zhb_col22 / crack_ulist_residuals）。
本引擎对 **全部采集数据** 做完整的跨源对撞：

  1. 加载 docs/field_verification/<date>/raw_*.json（默认近 N 天窗口，--all 全历史）
  2. 统一适配各源异构结构（fN 字典 / 位置列表 / 嵌套名典 / 标量），归一为
     ``(source, field_token) -> {(code, date): value}``
   3. 读取 field_registry.json 的逐源状态和来源谱系：
      - verified 精确路径从主攻目标剔除；只有独立性已确认的 verified 路径可作锚
      - 默认只对未验证字段与 verified 锚碰撞；未知×未知仅由 --exploratory 显式开启
   4. 对候选字段与允许的独立来源字段做两两对撞，严格套用 collision_rules 四铁律：
     - 类型感知（数值 / 枚举 / 字符串）
     - 精度对齐（舍入感知容差）
     - 比值族（单位换算 L1-U）：CV≤1e-4 且比值∈{10^k}
     - 多日复核（≥3 独立采集日，每日命中率≥0.9）
     - hub 巧合排除（单字段匹配过多判巧合）
  5. 增量状态追踪（collision_state.json）：跨日累积 findings，不重复刷屏
  6. 输出 <date>_collision_report.md / .json

治理约束（重要）
----------------
本引擎 **绝不写入** field_registry.json 或生成文档。字段机器权威为 registry；
field_dict.md、field_matrix.md 与 unknown_fields.md 均由 registry 生成。它只负责"发现"，
新结论应先核验源、完整路径和证据，再更新逐源 registry 并重生成文档。引擎与治理闸门正交、互补。

用法
----
    python scripts/collide.py                 # 默认近 7 个交易日，事件源按近 7 个自然日
    python scripts/collide.py --window 14     # 近 14 个交易日 + 14 个自然日事件窗口
    python scripts/collide.py --all           # 全部历史日期
    python scripts/collide.py --date 20260913 # 指定报告日期戳
    python scripts/collide.py --limit 20      # 仅取前 20 个左字段（自测用）
    python scripts/collide.py --min-hit 0.95  # 自定义 L1 命中率阈值（默认 0.9）
    python scripts/collide.py --exploratory  # 额外探索未知字段关系；结果不自动定案
"""

from __future__ import annotations

import os
import sys
import json
import hashlib
import heapq
import math
import argparse
import re
from collections import defaultdict
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.collision_dates import (
        CALENDAR,
        EXCLUDED_MARKET_DATES,
        TRADING,
        discover_capture_folders,
        event_record_date,
        is_calendar_event_source,
        parse_date,
        sample_date_key,
        select_folder_window,
        select_snapshots,
    )
else:
    try:
        from collision_dates import (
            CALENDAR,
            EXCLUDED_MARKET_DATES,
            TRADING,
            discover_capture_folders,
            event_record_date,
            is_calendar_event_source,
            parse_date,
            sample_date_key,
            select_folder_window,
            select_snapshots,
        )
    except ImportError:
        from scripts.collision_dates import (
            CALENDAR,
            EXCLUDED_MARKET_DATES,
            TRADING,
            discover_capture_folders,
            event_record_date,
            is_calendar_event_source,
            parse_date,
            sample_date_key,
            select_folder_window,
            select_snapshots,
        )

try:
    import collision_rules as CR

    RULES_OK = True
except Exception:
    RULES_OK = False

try:
    import source_lineage_api as SLA
except ImportError:
    from scripts import source_lineage_api as SLA

try:
    _SOURCE_LINEAGE = SLA.load_source_lineage()
except (OSError, ValueError, TypeError):
    _SOURCE_LINEAGE = {"sources": {}, "source_aliases": {}, "runtime_sources": {}}

# ───────────────────────────────────────────────────────────────────────
# 路径与常量
# ───────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "docs", "field_verification")
REG_PATH = os.path.join(DATA_DIR, "field_registry.json")
STATE_PATH = os.path.join(DATA_DIR, "collision_state.json")

# 样本为 20 股（pool.json: fixed 15 + dynamic 5）。L1 命中率阈值 = HIT_RATE_L1(18)/20 = 0.9；
# 采用比率而非绝对 18/20，便于样本数变动时阈值自适应（符合四铁律精神）。
# 注：早期版本曾误记样本为 12 股，实际采集脚本 load_pool() 始终返回 20 只——采集无缩水。
HIT_RATE_L1_RATIO = (CR.HIT_RATE_L1 / 20.0) if RULES_OK else 0.9  # 0.9
MULTI_DAY_MIN = CR.MULTI_DAY_MIN if RULES_OK else 3
RATIO_CV_MAX = CR.RATIO_CV_MAX if RULES_OK else 1e-4
RATIO_STEPS_SIGNED = set()
if RULES_OK:
    for k in range(0, 5):
        RATIO_STEPS_SIGNED.add(10**k)
        RATIO_STEPS_SIGNED.add(10**-k)
else:
    RATIO_STEPS_SIGNED = {1, 10, 100, 1000, 10000, 0.1, 0.01, 0.001, 0.0001}

MIN_PAIR = 8  # 候选对最少总样本数
MIN_DAILY_L1 = CR.MIN_DAILY_SAMPLES_L1 if RULES_OK else 18
MIN_DAILY_L4 = CR.MIN_DAILY_SAMPLES_L4 if RULES_OK else 8
MIN_CANDIDATE_PAIRS = 12  # 方法候选最少配对样本
MAX_METHOD_CANDIDATES = 500
HUB_MAX = 6  # 单字段匹配超过此数 → 巧合，降级
CONST_MAX_DISTINCT = 1  # 不同值 ≤1 → 常量，跳过
ID_SUFFIX_HINTS = ("market", "code", "date", "name", "thscode", "ticker", "url", "host", "secid")
# 剔除已知异常采集日（数据质量缺陷，不可参与对撞）：
# - 20260814：盘中快照（采集 start=10:49:53，其余日均为 15:00–17:09 收盘后）→
#   当日 change_pct 在 19/20 股同时失配（单日全市场同向，是采集时点问题非字段问题）。
# - 20260815 等周末/节假日目录: 已随 V17.4.21 历史清理被删除(数据回退至真实数据日目录), 不再存在, 故移除。
#   仅保留 20260814(盘中10:49快照, 无法回溯为收盘数据, 仍剔除避免对撞污染)。
EXCLUDE_DIRS = set(EXCLUDED_MARKET_DATES)


# ───────────────────────────────────────────────────────────────────────
# 数值工具
# ───────────────────────────────────────────────────────────────────────
def to_num(v):
    """尽力把值转成 float；非数值返回 None。"""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        s = v.strip().replace(",", "")
        if s == "":
            return None
        try:
            return float(s)
        except ValueError:
            return None
    return None


def is_close(a: float, b: float) -> bool:
    """舍入感知容差：相对 1e-6，绝对值兜底 1e-9。"""
    if a == b:
        return True
    denom = max(1.0, abs(a), abs(b))
    return abs(a - b) <= 1e-6 * denom


def cv(xs):
    """变异系数 std/mean。"""
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    if m == 0:
        return 0.0
    var = sum((x - m) ** 2 for x in xs) / n
    return math.sqrt(var) / abs(m)


# ───────────────────────────────────────────────────────────────────────
# 原始数据加载与字段扁平化
# ───────────────────────────────────────────────────────────────────────
def _flatten(rec, source, scheme, code, date, out):
    """把单只股票的原始记录扁平化为 (fid, value) 列表，写入 out。"""
    if not isinstance(rec, dict):
        return
    if rec.get("__error__") or "__skipped__" in rec:
        return

    # 形态 A：fN 字典（ulist239 / push2_full / push2）
    data = rec.get("data")
    if isinstance(data, dict) and any(
        (isinstance(k, str) and (k.startswith("f") and k[1:].isdigit())) for k in data
    ):
        for k, v in data.items():
            if k in ("__error__", "__skipped__", "__source_meta__"):
                continue
            out.append((f"{source}.{k}", v))
        return

    # 形态 B：位置列表（tencent / sina）
    flds = rec.get("fields")
    if isinstance(flds, list):
        for i, v in enumerate(flds):
            out.append((f"{source}[{i}]", v))
        return

    # 形态 C：嵌套名典 / 标量（zhb full/stat/stat2/tipinfo、tdx quote_full/finance_info、fuyao *、…）
    for sub, subv in rec.items():
        if sub in (
            "scheme",
            "n_fields",
            "url",
            "host",
            "secid",
            "zhb_date",
            "__error__",
            "__skipped__",
            "__source_meta__",
            "auction_snapshot_meta",
        ):
            continue
        if isinstance(subv, dict):
            source_meta = subv.get("__source_meta__")
            if isinstance(source_meta, dict) and source_meta.get("collision_eligible") is False:
                continue
            for k, v in subv.items():
                if k in ("__error__", "__skipped__", "__source_meta__") or isinstance(
                    v, (dict, list)
                ):
                    continue
                out.append((f"{source}.{sub}.{k}", v))
        elif isinstance(subv, (int, float, str)) and not isinstance(subv, bool):
            out.append((f"{source}.{sub}", subv))
        # 列表 / None 跳过


def _record_containers(doc, source=None):
    """Return supported stock, record, and market-level record containers."""
    containers = []
    stocks = doc.get("stocks")
    if isinstance(stocks, dict):
        containers.append(stocks)
        if source and is_calendar_event_source(source):
            for stock_code, stock_record in stocks.items():
                if isinstance(stock_record, list):
                    containers.append(
                        {
                            f"{stock_code}#event{index}": record
                            for index, record in enumerate(stock_record)
                            if isinstance(record, dict)
                        }
                    )
                elif isinstance(stock_record, dict):
                    for key in ("records", "items", "announcements", "reports", "news"):
                        nested = stock_record.get(key)
                        if isinstance(nested, list):
                            containers.append(
                                {
                                    f"{stock_code}#{key}{index}": record
                                    for index, record in enumerate(nested)
                                    if isinstance(record, dict)
                                }
                            )
    records = doc.get("records")
    if isinstance(records, dict):
        containers.append(records)
    elif isinstance(records, list):
        containers.append({f"__{i}": value for i, value in enumerate(records)})
    for key, value in doc.items():
        if key in (
            "scheme",
            "field_meta",
            "zhb_date",
            "stocks",
            "records",
            "auction_snapshot_meta",
        ):
            continue
        if (
            isinstance(value, dict)
            and value
            and all(isinstance(item, (dict, list)) for item in value.values())
        ):
            containers.append(value)
        elif isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            containers.append({f"__{i}": item for i, item in enumerate(value)})
    return containers


def _event_identity(source, record, container_code, entity_code):
    """Use a shared title fingerprint or a source-scoped fallback event id."""
    title = next(
        (
            record.get(key)
            for key in ("title", "announcementTitle", "announcement_title", "headline", "question")
            if record.get(key) not in (None, "")
        ),
        None,
    )
    if title is not None:
        normalized_title = re.sub(r"\s+", " ", str(title)).strip().casefold()
        if normalized_title:
            fingerprint = hashlib.sha256(normalized_title.encode("utf-8")).hexdigest()[:20]
            return f"shared:{entity_code}:{fingerprint}"
    source_id = (
        record.get("id")
        or record.get("announcementId")
        or record.get("reportId")
        or record.get("question_id")
        or record.get("answer_id")
        or container_code
    )
    return f"source:{source}:{source_id}"


def load_snapshots(snapshots, store, diagnostics, event_start=None, event_end=None):
    """Flatten selected source snapshots using domain-qualified sample dates."""
    total = 0
    sample_ranks = {}
    duplicate_count = 0
    duplicate_examples = []
    undated_event_counts = defaultdict(int)
    future_event_counts = defaultdict(int)
    for snapshot in snapshots:
        doc = snapshot.document
        scheme = doc.get("scheme")
        auction_meta = doc.get("auction_snapshot_meta")
        if isinstance(auction_meta, dict) and auction_meta.get("collision_eligible") is False:
            diagnostic = (
                f"{snapshot.folder}/{snapshot.source}/stocks.*.auction_final: "
                f"竞价子树已排除；reason={auction_meta.get('exclusion_reason') or 'unspecified'}，"
                f"data_status={auction_meta.get('data_status')!r}，"
                f"source_data_date={auction_meta.get('source_data_date')!r}，"
                f"response_timestamp={auction_meta.get('response_timestamp')!r}，"
                f"记录数={auction_meta.get('item_count', 0)}"
            )
            diagnostics.append(diagnostic)
        for container in _record_containers(doc, snapshot.source):
            for container_code, rec in container.items():
                if not isinstance(rec, dict):
                    continue
                sample_day = snapshot.sample_date
                if snapshot.domain == CALENDAR:
                    event_day = event_record_date(snapshot.source, rec)
                    if event_day is None:
                        undated_event_counts[(snapshot.folder, snapshot.source)] += 1
                        continue
                    if event_start is not None and event_day < event_start:
                        continue
                    if event_end is not None and event_day > event_end:
                        future_event_counts[(snapshot.folder, snapshot.source)] += 1
                        continue
                    sample_day = event_day
                    day_key = sample_date_key(CALENDAR, event_day)
                else:
                    day_key = snapshot.day_key

                raw_code = (
                    rec.get("zqdm")
                    or rec.get("f12")
                    or rec.get("code")
                    or rec.get("stockCode")
                    or rec.get("stock_code")
                    or rec.get("SECURITY_CODE")
                    or rec.get("ticker")
                )
                code = str(raw_code or container_code)
                if snapshot.domain == CALENDAR:
                    entity_code = str(raw_code or "")
                    if not entity_code and re.fullmatch(r"\d{6,}", str(container_code)):
                        entity_code = str(container_code)
                    event_id = _event_identity(snapshot.source, rec, container_code, entity_code)
                    code = f"{code}#event:{event_id}"
                pairs = []
                _flatten(rec, snapshot.source, scheme, code, day_key, pairs)
                for fid, value in pairs:
                    key = (code, day_key)
                    rank_key = (fid, key)
                    previous_rank = sample_ranks.get(rank_key)
                    if previous_rank is not None and snapshot.rank < previous_rank:
                        duplicate_count += 1
                        if len(duplicate_examples) < 10:
                            duplicate_examples.append(f"{fid}/{code}/{day_key}")
                        continue
                    if previous_rank is not None:
                        duplicate_count += 1
                        if len(duplicate_examples) < 10:
                            duplicate_examples.append(f"{fid}/{code}/{day_key}")
                    store[fid]["vals"][key] = value
                    store[fid].setdefault("sample_meta", {})[key] = {
                        "phase": snapshot.phase,
                        "source": snapshot.source,
                        "capture_folder": snapshot.folder,
                        "capture_date": snapshot.capture_date.strftime("%Y%m%d"),
                        "as_of_date": sample_day.strftime("%Y%m%d"),
                        "as_of_date_origin": snapshot.date_origin,
                        "captured_at": (
                            snapshot.captured_at.isoformat(timespec="seconds")
                            if snapshot.captured_at
                            else None
                        ),
                        "status": snapshot.status,
                        "domain": snapshot.domain,
                    }
                    store[fid]["scheme"] = scheme
                    store[fid]["src"] = snapshot.source
                    sample_ranks[rank_key] = snapshot.rank
                    total += 1
    if duplicate_count:
        diagnostics.append(
            f"折叠 {duplicate_count} 条重复字段样本，按快照质量择优；示例: "
            + ", ".join(duplicate_examples)
        )
    for (folder, source), count in sorted(undated_event_counts.items()):
        diagnostics.append(f"{folder}/{source}: {count} 条事件记录缺少可解析的自然日，已跳过")
    for (folder, source), count in sorted(future_event_counts.items()):
        diagnostics.append(f"{folder}/{source}: {count} 条事件记录晚于报告日，已跳过")
    return total


# ───────────────────────────────────────────────────────────────────────
# 字段分类（数值 / 枚举 / 字符串 / 常量 / 标识符）
# ───────────────────────────────────────────────────────────────────────
def classify(store):
    """为每个字段补充 type / n_distinct / is_constant / is_identifier。"""
    for fid, info in store.items():
        vals = [
            v for v in info["vals"].values() if v is not None and not isinstance(v, (dict, list))
        ]
        nums = [to_num(v) for v in vals]
        nums = [n for n in nums if n is not None]
        n_total = len(vals)
        n_num = len(nums)
        distinct = len(set(vals))
        info["n"] = n_total
        info["n_num"] = n_num
        info["n_distinct"] = distinct
        info["is_constant"] = distinct <= CONST_MAX_DISTINCT and n_total > 0
        low = fid.lower()
        info["is_identifier"] = any(h in low for h in ID_SUFFIX_HINTS)
        if n_total > 0 and n_num >= 0.8 * n_total:
            info["type"] = "num"
        elif distinct <= 30 and n_total > 0:
            info["type"] = "enum"
        else:
            info["type"] = "str"
        # 值域（用于快速预筛）
        if nums:
            info["vmin"] = min(nums)
            info["vmax"] = max(nums)
        else:
            info["vmin"] = None
            info["vmax"] = None


# ───────────────────────────────────────────────────────────────────────
# 对撞核心
# ───────────────────────────────────────────────────────────────────────
def _eligible_for_l1(info, key):
    sample_meta = info.get("sample_meta", {}).get(key, {})
    return sample_meta.get("phase") in {"closed", "calendar"}


def _median(values):
    ordered = sorted(values)
    if not ordered:
        return None
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def _ratio_step(value):
    for step in RATIO_STEPS_SIGNED:
        if step != 1 and math.isclose(value, step, rel_tol=0.005, abs_tol=1e-9):
            return step
    return None


def collide_pair(L, R):
    """Compare fields with per-session sample floors and independent-day gates."""
    left_source = str(L.get("src") or "")
    right_source = str(R.get("src") or "")
    independent_sources = bool(left_source and right_source) and are_independent_sources(
        left_source, right_source
    )
    if left_source and right_source and not independent_sources:
        return None
    lv, rv = L["vals"], R["vals"]
    common = set(lv) & set(rv)
    if len(common) < MIN_PAIR:
        return None

    exact_all = defaultdict(lambda: [0, 0])
    exact_l1 = defaultdict(lambda: [0, 0])
    ratios_by_day = defaultdict(list)
    for key in common:
        a, b = lv[key], rv[key]
        left_num, right_num = to_num(a), to_num(b)
        day_key = key[1]
        exact_all[day_key][1] += 1
        l1_eligible = _eligible_for_l1(L, key) and _eligible_for_l1(R, key)
        if l1_eligible:
            exact_l1[day_key][1] += 1
        if left_num is not None and right_num is not None:
            matched = is_close(left_num, right_num)
            if matched:
                exact_all[day_key][0] += 1
                if l1_eligible:
                    exact_l1[day_key][0] += 1
            if left_num != 0 and right_num != 0:
                ratios_by_day[day_key].append((right_num / left_num, l1_eligible))
        else:
            matched = str(a) == str(b)
            if matched:
                exact_all[day_key][0] += 1
                if l1_eligible:
                    exact_l1[day_key][0] += 1

    l1_days = {day: counts for day, counts in exact_l1.items() if counts[1] >= MIN_DAILY_L1}
    exact_days_ge = sum(hits / total >= HIT_RATE_L1_RATIO for hits, total in l1_days.values())
    exact_total_hits = sum(hits for hits, _ in l1_days.values())
    exact_total = sum(total for _, total in l1_days.values())
    exact_overall = exact_total_hits / exact_total if exact_total else 0.0
    exact_l1_ok = (
        len(l1_days) >= MULTI_DAY_MIN
        and exact_days_ge >= MULTI_DAY_MIN
        and exact_overall >= HIT_RATE_L1_RATIO
        and not L["is_constant"]
        and not R["is_constant"]
        and independent_sources
    )

    # A unit-ratio conclusion needs enough independent non-zero observations on
    # every day; exact hits and undefined 0/0 ratios cannot establish a scale.
    all_ratios = [
        ratio for values in ratios_by_day.values() for ratio, l1_eligible in values if l1_eligible
    ]
    ratio_info = None
    ratio_days = {}
    ratio_days_ge = 0
    ratio_overall = 0.0
    if all_ratios:
        median_ratio = _median(all_ratios)
        ratio_info = _ratio_step(median_ratio)
        if (
            ratio_info is not None
            and len(all_ratios) >= MIN_DAILY_L1 * MULTI_DAY_MIN
            and cv(all_ratios) <= RATIO_CV_MAX
        ):
            for day, observations in ratios_by_day.items():
                valid_ratios = [ratio for ratio, eligible in observations if eligible]
                if len(valid_ratios) < MIN_DAILY_L1:
                    continue
                hits = sum(
                    math.isclose(ratio, ratio_info, rel_tol=0.005, abs_tol=1e-9)
                    for ratio in valid_ratios
                )
                ratio_days[day] = (hits, len(valid_ratios))
            ratio_days_ge = sum(
                hits / total >= HIT_RATE_L1_RATIO for hits, total in ratio_days.values()
            )
            ratio_total_hits = sum(hits for hits, _ in ratio_days.values())
            ratio_total = sum(total for _, total in ratio_days.values())
            ratio_overall = ratio_total_hits / ratio_total if ratio_total else 0.0
            if not (
                len(ratio_days) >= MULTI_DAY_MIN
                and ratio_days_ge >= MULTI_DAY_MIN
                and ratio_overall >= HIT_RATE_L1_RATIO
            ):
                ratio_info = None
        else:
            ratio_info = None

    if exact_l1_ok:
        level = "L1"
        selected_days = l1_days
        overall = exact_overall
        days_ge = exact_days_ge
    elif (
        ratio_info is not None
        and not L["is_constant"]
        and not R["is_constant"]
        and independent_sources
    ):
        level = "L1-U"
        selected_days = ratio_days
        overall = ratio_overall
        days_ge = ratio_days_ge
    else:
        l4_days = {day: counts for day, counts in exact_all.items() if counts[1] >= MIN_DAILY_L4}
        l4_total = sum(total for _, total in l4_days.values())
        l4_hits = sum(hits for hits, _ in l4_days.values())
        l4_overall = l4_hits / l4_total if l4_total else 0.0
        if l4_overall >= 0.4 and l4_days:
            level = "L4"
            selected_days = l4_days
            overall = l4_overall
            days_ge = sum(hits / total >= HIT_RATE_L1_RATIO for hits, total in l4_days.values())
        else:
            return None

    return {
        "left": None,
        "right": None,
        "level": level,
        "ratio": ratio_info if level == "L1-U" else None,
        "overall_hit": round(overall, 4),
        "days_ge_threshold": days_ge,
        "n_days": len(selected_days),
        "n_pairs": sum(total for _, total in selected_days.values()),
        "distinct_days": sorted(selected_days),
        "daily_sample_counts": {day: total for day, (_, total) in selected_days.items()},
        "excluded_intraday_pairs": sum(
            1
            for key in common
            if L.get("sample_meta", {}).get(key, {}).get("phase") == "intraday"
            or R.get("sample_meta", {}).get(key, {}).get("phase") == "intraday"
        ),
        "excluded_unknown_phase_pairs": sum(
            1
            for key in common
            if L.get("sample_meta", {}).get(key, {}).get("phase") not in {"closed", "calendar"}
            or R.get("sample_meta", {}).get(key, {}).get("phase") not in {"closed", "calendar"}
        ),
    }


def _pearson(x_values, y_values):
    if len(x_values) != len(y_values) or len(x_values) < 3:
        return None
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)
    x_delta = [value - x_mean for value in x_values]
    y_delta = [value - y_mean for value in y_values]
    x_sum = sum(value * value for value in x_delta)
    y_sum = sum(value * value for value in y_delta)
    if x_sum <= 0 or y_sum <= 0:
        return None
    return sum(a * b for a, b in zip(x_delta, y_delta)) / math.sqrt(x_sum * y_sum)


def _ranks(values):
    order = sorted(range(len(values)), key=values.__getitem__)
    result = [0.0] * len(values)
    offset = 0
    while offset < len(order):
        end = offset + 1
        while end < len(order) and values[order[end]] == values[order[offset]]:
            end += 1
        rank = ((offset + 1) + end) / 2.0
        for position in range(offset, end):
            result[order[position]] = rank
        offset = end
    return result


def _correlation_metrics(x_values, y_values):
    pearson = _pearson(x_values, y_values)
    if pearson is None:
        return None
    spearman = _pearson(_ranks(x_values), _ranks(y_values))
    leave_one_out = []
    if len(x_values) >= 5:
        count = len(x_values)
        x_mean = sum(x_values) / count
        y_mean = sum(y_values) / count
        x_delta = [value - x_mean for value in x_values]
        y_delta = [value - y_mean for value in y_values]
        covariance = sum(x * y for x, y in zip(x_delta, y_delta))
        x_variance = sum(x * x for x in x_delta)
        y_variance = sum(y * y for y in y_delta)
        multiplier = count / (count - 1)
        for x, y in zip(x_delta, y_delta):
            reduced_covariance = covariance - multiplier * x * y
            reduced_x_variance = x_variance - multiplier * x * x
            reduced_y_variance = y_variance - multiplier * y * y
            if reduced_x_variance <= 0 or reduced_y_variance <= 0:
                continue
            leave_one_out.append(
                reduced_covariance / math.sqrt(reduced_x_variance * reduced_y_variance)
            )
    sign_stable = (
        len(leave_one_out) == len(x_values)
        and pearson != 0
        and all(value != 0 and (value > 0) == (pearson > 0) for value in leave_one_out)
    )
    return {
        "pearson": pearson,
        "spearman": spearman,
        "leave_one_out_sign_stable": sign_stable,
        "leave_one_out_min": min(leave_one_out) if leave_one_out else None,
        "leave_one_out_max": max(leave_one_out) if leave_one_out else None,
    }


def _temporal_candidate(common, left_values, right_values):
    per_code = defaultdict(list)
    for key in common:
        code, day_key = key
        if not str(day_key).startswith("T:"):
            continue
        left_num, right_num = to_num(left_values[key]), to_num(right_values[key])
        if left_num is not None and right_num is not None:
            per_code[code].append((day_key, left_num, right_num))
    correlations = []
    used_days = set()
    for code, rows in per_code.items():
        rows.sort(key=lambda item: item[0])
        if len(rows) < 3:
            continue
        value = _pearson([row[1] for row in rows], [row[2] for row in rows])
        if value is not None:
            correlations.append((code, value, [row[0] for row in rows]))
            used_days.update(row[0] for row in rows)
    if len(correlations) < 3:
        return None
    signs = [1 if value > 0 else -1 for _, value, _ in correlations if value != 0]
    if not signs:
        return None
    dominant = 1 if sum(signs) >= 0 else -1
    sign_consistency = sum(sign == dominant for sign in signs) / len(signs)
    median_abs = _median([abs(value) for _, value, _ in correlations]) or 0.0
    if median_abs < 0.7 or sign_consistency < 0.8:
        return None
    return {
        "method": "per_stock_time_series",
        "median_abs_pearson": round(median_abs, 4),
        "sign_consistency": round(sign_consistency, 4),
        "stocks": len(correlations),
        "stock_correlations": [
            {"code": code, "pearson": round(value, 4), "dates": dates}
            for code, value, dates in correlations[:20]
        ],
        "sample_dates": sorted(used_days),
    }


def _semantic_tokens(fid):
    label = code_of(fid).lower()
    if re.fullmatch(r"(?:f\d+|tx\[\d+\])", label):
        return set()
    tokens = set(re.findall(r"[a-z]+|\d+|[\u4e00-\u9fff]+", label))
    return {token for token in tokens if not token.isdigit()}


def method_candidates_for_pair(left_id, right_id, L, R):
    """Return non-final semantic, formula, temporal, and robust-correlation clues."""
    common = sorted(set(L["vals"]) & set(R["vals"]), key=lambda item: (item[1], item[0]))
    if len(common) < MIN_CANDIDATE_PAIRS:
        return None
    numeric = []
    for key in common:
        left_num = to_num(L["vals"][key])
        right_num = to_num(R["vals"][key])
        if left_num is not None and right_num is not None:
            numeric.append((key, left_num, right_num))
    if len(numeric) < MIN_CANDIDATE_PAIRS:
        return None

    x_values = [row[1] for row in numeric]
    y_values = [row[2] for row in numeric]
    correlations = _correlation_metrics(x_values, y_values)
    methods = []
    if correlations is not None:
        pearson = correlations["pearson"]
        spearman = correlations["spearman"]
        if (
            spearman is not None
            and abs(spearman) >= (CR.CORR_SPEARMAN_MIN if RULES_OK else 0.6)
            and pearson * spearman > 0
            and correlations["leave_one_out_sign_stable"]
        ):
            methods.append(
                {
                    "method": "robust_correlation",
                    **{
                        key: round(value, 4) if isinstance(value, float) else value
                        for key, value in correlations.items()
                    },
                }
            )
        if abs(pearson) >= 0.98:
            x_mean = sum(x_values) / len(x_values)
            y_mean = sum(y_values) / len(y_values)
            x_var = sum((value - x_mean) ** 2 for value in x_values)
            if x_var > 0:
                slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values)) / x_var
                intercept = y_mean - slope * x_mean
                methods.append(
                    {
                        "method": "affine_formula",
                        "formula": f"right ≈ {slope:.8g} × left + {intercept:.8g}",
                        "r_squared": round(pearson * pearson, 6),
                    }
                )
    temporal = _temporal_candidate([row[0] for row in numeric], L["vals"], R["vals"])
    if temporal is not None:
        methods.append(temporal)

    left_tokens = _semantic_tokens(left_id)
    right_tokens = _semantic_tokens(right_id)
    if left_tokens and right_tokens:
        overlap = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
        if overlap >= 0.5:
            methods.append(
                {
                    "method": "semantic_label",
                    "shared_tokens": sorted(left_tokens & right_tokens),
                    "token_jaccard": round(overlap, 4),
                }
            )
    if not methods:
        return None

    sample_dates = sorted({row[0][1] for row in numeric})
    evidence_sources = sorted({str(L.get("src") or ""), str(R.get("src") or "")})
    evidence_sources = [source for source in evidence_sources if source]
    return {
        "left": left_id,
        "right": right_id,
        "methods": methods,
        "sample_count": len(numeric),
        "sample_dates": sample_dates,
        "evidence_sources": evidence_sources,
        "sample_codes": sorted({row[0][0] for row in numeric})[:20],
    }


def range_overlap(L, R):
    if L["vmin"] is None or R["vmin"] is None:
        return True
    return not (L["vmax"] < R["vmin"] or R["vmax"] < L["vmin"])


# ───────────────────────────────────────────────────────────────────────
# 状态读取（registry）+ 增量状态
# ───────────────────────────────────────────────────────────────────────
# V17.3 同步更新（2026-09-20）：主字典 field_registry.json 现以「显示名」登记源
# （如 `TDX-eltdx(适配层)` / `ZHB-tipinfo` / `东财-datacenter(英文键)`），而采集脚本
# 以「短键」产出 raw_<key>.json（scheme=短键）。旧 REG_ALIAS 仅覆盖早期 4 源，
# 致 22 个源的已验证字段无法被 is_verified() 识别 → 反复被当作 unverified 主攻目标
# 重对撞、且 findings 的 in_registry 标记恒为 False。
# 本表分两段：① 采集器短键自映射到规范键（保证 raw 字段源名解析一致）；② 主字典
# 显示名 → 规范短键（保证 verified 集合与 raw 字段同源同名）。两路解析到同一规范键即匹配。
def _lineage_aliases(source, lineage):
    """Resolve an exact registry source to its runtime source identity or identities."""
    if not isinstance(source, str) or not source:
        return []
    runtime_sources = lineage.get("runtime_sources", {})
    if source in runtime_sources:
        return [source]
    aliases = SLA.runtime_aliases_for_source(source, lineage)
    return [alias for alias in aliases if alias in runtime_sources]


def load_registry_context():
    """Load field status, exact anchors, mappings, lineage and visible diagnostics."""
    context = {
        "verified": set(),
        "disproved": set(),
        "anchors": set(),
        "known_mappings": set(),
        "diagnostics": [],
        "unmapped_verified": 0,
        "unconfirmed_verified": 0,
        "source_fields": 0,
        "safe_to_run": False,
    }
    if not os.path.exists(REG_PATH):
        context["diagnostics"].append(f"字段注册表不存在：{REG_PATH}；本轮无已知字段锚")
        return context
    try:
        with open(REG_PATH, encoding="utf-8") as handle:
            registry = json.load(handle)
    except (OSError, ValueError, TypeError) as exc:
        context["diagnostics"].append(f"字段注册表读取失败；本轮无已知字段锚：{exc}")
        return context

    try:
        lineage = SLA.load_source_lineage(registry=registry)
        lineage_valid = True
    except (OSError, ValueError, TypeError) as exc:
        lineage = {"sources": {}, "source_aliases": {}, "runtime_sources": {}}
        context["diagnostics"].append(f"来源血缘校验失败；禁止生成已确认锚：{exc}")
        lineage_valid = False
    global _SOURCE_LINEAGE
    _SOURCE_LINEAGE = lineage
    if not lineage_valid:
        return context

    source_fields = registry.get("source_fields")
    if source_fields is None:
        # Compatibility for old one-source aggregate rows only. A multi-source
        # aggregate status cannot safely be attributed to any individual source.
        source_fields = []
        for field in registry.get("fields", []):
            sources = field.get("sources", [])
            source = field.get("source")
            if not source and len(sources) == 1:
                source = sources[0]
            if isinstance(source, str) and source and len(sources or [source]) == 1:
                source_fields.append({**field, "source": source})
        context["diagnostics"].append(
            "注册表没有 source_fields；仅使用可精确归属的单源旧记录，多源汇总状态不分摊"
        )
    if not isinstance(source_fields, list):
        context["diagnostics"].append("注册表 source_fields 格式无效；本轮无已知字段锚")
        return context

    context["source_fields"] = len(source_fields)
    seen_source_identities = set()
    for field in source_fields:
        if not isinstance(field, dict):
            context["diagnostics"].append("source_fields 含非对象记录；已禁用本轮字段对撞")
            return context
        source = field.get("source")
        code = field.get("code")
        if not isinstance(source, str) or not isinstance(code, str) or not code:
            context["diagnostics"].append("source_fields 含无效来源/完整路径；已禁用本轮字段对撞")
            return context
        if field.get("status") not in {
            "verified",
            "unverified",
            "candidate",
            "conflict",
            "disproved",
        }:
            context["diagnostics"].append(
                f"source_fields 含未知状态 {source}::{code}；已禁用本轮字段对撞"
            )
            return context
        identity = (source, code)
        if identity in seen_source_identities:
            context["diagnostics"].append(
                f"source_fields 存在重复身份 {source}::{code}；已禁用全部 registry 锚"
            )
            context["verified"].clear()
            context["disproved"].clear()
            context["anchors"].clear()
            context["known_mappings"].clear()
            return context
        seen_source_identities.add(identity)
        aliases = _lineage_aliases(source, lineage)
        if field.get("status") == "disproved":
            context["disproved"].update((alias, code) for alias in aliases)
            continue
        if field.get("status") != "verified":
            continue
        if not aliases:
            context["unmapped_verified"] += 1
            continue
        for alias in aliases:
            identity = (alias, code)
            context["verified"].add(identity)
            family = SLA.runtime_family(alias, lineage)
            source_record = lineage.get("sources", {}).get(source, {})
            if (
                source_record.get("anchor_eligible")
                and source_record.get("independence_status") == "confirmed"
                and family == source_record.get("independence_family")
            ):
                context["anchors"].add(identity)
            else:
                context["unconfirmed_verified"] += 1

    for mapping in registry.get("mappings", []):
        if not isinstance(mapping, dict):
            continue
        left = mapping.get("from", {})
        right = mapping.get("to", {})
        if not isinstance(left, dict) or not isinstance(right, dict):
            continue
        left_aliases = _lineage_aliases(left.get("source"), lineage)
        right_aliases = _lineage_aliases(right.get("source"), lineage)
        left_code = left.get("code")
        right_code = right.get("code")
        if not isinstance(left_code, str) or not isinstance(right_code, str):
            continue
        for left_alias in left_aliases:
            for right_alias in right_aliases:
                context["known_mappings"].add((left_alias, left_code, right_alias, right_code))
                context["known_mappings"].add((right_alias, right_code, left_alias, left_code))

    context["safe_to_run"] = True

    if context["unmapped_verified"]:
        context["diagnostics"].append(
            f"{context['unmapped_verified']} 条 verified 源字段无法映射到运行时来源，未作锚"
        )
    if context["unconfirmed_verified"]:
        context["diagnostics"].append(
            f"{context['unconfirmed_verified']} 条 verified 源字段来源未确认独立性，作为已知字段跳过重解但不作锚"
        )
    if not context["anchors"]:
        context["diagnostics"].append("没有可用的已确认独立锚；默认模式不会把未知字段互相定案")
    return context


def load_registry_state():
    """Compatibility contract: return (verified_set, known_mapping_pairs)."""
    context = load_registry_context()
    return context["verified"], context["known_mappings"]


def norm_src_of(fid):
    if "." in fid:
        return fid.split(".")[0]
    if "[" in fid:
        return fid.split("[")[0]
    return fid


def alias_src(fid):
    source = norm_src_of(fid)
    if source in _SOURCE_LINEAGE.get("runtime_sources", {}):
        return source
    aliases = _lineage_aliases(source, _SOURCE_LINEAGE)
    return aliases[0] if aliases else source


def evidence_source_family(fid):
    """Return a confirmed producer family, or None when lineage is unknown."""
    return SLA.runtime_family(alias_src(fid), _SOURCE_LINEAGE)


def are_independent_sources(left_fid, right_fid):
    left_family = evidence_source_family(left_fid)
    right_family = evidence_source_family(right_fid)
    return left_family is not None and right_family is not None and left_family != right_family


def code_of(fid):
    if "[" in fid:
        return fid[fid.index("[") :]
    if "." in fid:
        return fid.split(".", 1)[1]
    return fid


def is_verified(fid, verified):
    return (alias_src(fid), code_of(fid)) in verified


def is_disproved(fid, disproved):
    return (alias_src(fid), code_of(fid)) in disproved


def select_collision_fields(store, verified, disproved, anchors, exploratory=False):
    """Return eligible unknown targets and the allowed right-hand field set."""
    eligible = [
        fid
        for fid, info in store.items()
        if not info["is_identifier"]
        and not info["is_constant"]
        and info["type"] in ("num", "enum")
        and not is_disproved(fid, disproved)
    ]
    left = [fid for fid in eligible if not is_verified(fid, verified)]
    if exploratory:
        return left, eligible
    right = [fid for fid in eligible if (alias_src(fid), code_of(fid)) in anchors]
    return left, right


def mark_exploratory_candidate(result, right_is_anchor):
    """Keep non-anchor exploratory matches visible without promoting them to L1."""
    if result is None or right_is_anchor:
        return False
    result["exploratory"] = True
    if result.get("level") in ("L1", "L1-U"):
        result["level"] = "L4"
    return True


def load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, encoding="utf-8") as handle:
                state = json.load(handle)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            return {
                "version": 2,
                "findings": {},
                "warnings": [f"state 读取失败，未覆盖原文件: {exc}"],
                "read_error": True,
            }
        if not isinstance(state, dict):
            return {
                "version": 2,
                "findings": {},
                "warnings": ["state 顶层不是对象，未覆盖原文件"],
                "read_error": True,
            }
        if not isinstance(state.get("findings", {}), dict):
            return {
                "version": 2,
                "findings": {},
                "warnings": ["state.findings 格式无效，未覆盖原文件"],
                "read_error": True,
            }
        version = state.get("version", 1)
        if not isinstance(version, int) or version > 2:
            return {
                "version": 2,
                "findings": {},
                "warnings": [f"collision_state 版本 {version!r} 不受支持，未覆盖原文件"],
                "read_error": True,
            }
        if version < 2:
            old_findings = state.get("findings", {})
            migrated = {
                "version": 2,
                "findings": {},
                "legacy_findings_v1": old_findings,
                "legacy_state_version": version,
                "warnings": [
                    f"collision_state v{version} 已归档到 legacy_findings_v1；旧 L1 不再自动视为当前确认"
                ],
            }
            return migrated
        state.setdefault("findings", {})
        state.setdefault("warnings", [])
        return state
    return {"version": 2, "findings": {}, "warnings": []}


def save_state(st):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)


# ───────────────────────────────────────────────────────────────────────
# 主流程
# ───────────────────────────────────────────────────────────────────────
def run(args):
    report_day = parse_date(args.date) if args.date else date.today()
    if report_day is None:
        raise ValueError(f"报告日期格式无效: {args.date}")
    today = report_day.strftime("%Y%m%d")

    # 1) Use distinct source data sessions and a separate natural-day event window.
    folders, discovery_warnings = discover_capture_folders(DATA_DIR)
    diagnostics = list(discovery_warnings)
    folder_window = select_folder_window(
        folders,
        args.window,
        report_day,
        args.all,
        excluded_trading_dates=EXCLUDE_DIRS,
    )
    diagnostics.extend(folder_window.warnings)
    snapshots, snapshot_warnings = select_snapshots(
        folder_window.folders,
        allowed_trading_folders=folder_window.market_folders,
        allowed_event_folders=folder_window.event_folders,
    )
    diagnostics.extend(snapshot_warnings)
    usable_snapshots = []
    for snapshot in snapshots:
        if snapshot.domain == TRADING and snapshot.sample_date > report_day:
            diagnostics.append(
                f"{snapshot.folder}/{snapshot.source}: as_of_date {snapshot.sample_date:%Y%m%d} "
                f"晚于报告日 {today}，行情快照不纳入本轮"
            )
            continue
        if snapshot.domain == TRADING and snapshot.sample_date.strftime("%Y%m%d") in EXCLUDE_DIRS:
            diagnostics.append(
                f"{snapshot.folder}/{snapshot.source}: 异常行情数据日 "
                f"{snapshot.sample_date:%Y%m%d} 已排除；同目录自然日事件仍可参与"
            )
            continue
        usable_snapshots.append(snapshot)
    snapshots = usable_snapshots

    # 2) Load only quality-selected source snapshots; sample keys include date domain.
    store = defaultdict(lambda: {"vals": {}, "scheme": None, "src": None, "sample_meta": {}})
    total = load_snapshots(
        snapshots,
        store,
        diagnostics,
        event_start=folder_window.event_start,
        event_end=folder_window.event_end,
    )
    classify(store)
    print(
        f"[collide] 加载 {len(folder_window.folders)} 个采集目录、"
        f"{len(folder_window.trading_dates)} 个有效交易日、{len(store)} 个字段、"
        f"{total} 条样本值",
        file=sys.stderr,
    )

    # 3) Registry identities and independently confirmed anchors.
    registry_context = load_registry_context()
    verified = registry_context["verified"]
    disproved = registry_context["disproved"]
    anchors = registry_context["anchors"]
    known_maps = registry_context["known_mappings"]
    diagnostics.extend(registry_context["diagnostics"])

    # 4) Candidate targets exclude verified and explicitly disproved identities.
    if registry_context["safe_to_run"]:
        left_ids, safe_right_ids = select_collision_fields(
            store, verified, disproved, anchors, exploratory=False
        )
    else:
        left_ids, safe_right_ids = [], []
        diagnostics.append("注册表或来源谱系未通过完整性校验；本轮不执行字段对撞")
    if args.exploratory and registry_context["safe_to_run"]:
        # Opt-in only: useful for candidate discovery, but unknown×unknown must
        # never be mistaken for a verified anchor.
        _, right_ids = select_collision_fields(
            store, verified, disproved, anchors, exploratory=True
        )
        diagnostics.append("已启用探索模式：未知字段间也会生成候选；须独立复核后才能定案")
    elif registry_context["safe_to_run"]:
        right_ids = safe_right_ids
    else:
        right_ids = []
    diagnostics.append(
        f"对撞模式：{'exploratory' if args.exploratory else 'verified_anchor_only'}；"
        f"待破解字段={len(left_ids)}，verified 字段={len(verified)}，"
        f"可用独立锚={len(anchors)}，right 字段={len(right_ids)}"
    )

    if args.limit:
        left_ids = left_ids[: args.limit]
    print(
        f"[collide] 主攻目标(left)={len(left_ids)}，"
        f"{'探索字段(right)' if args.exploratory else '已确认独立锚(right)'}={len(right_ids)}",
        file=sys.stderr,
    )

    # 5) 两两对撞
    raw_pairs = []  # (left, right, result)
    guardrail_hits = []  # 命中 REFUTED_CONCLUSIONS 被拦截的伪结论候选
    method_candidate_heap = []
    method_candidate_count = 0
    method_candidate_sequence = 0
    skipped_same_family = 0
    skipped_unknown_lineage = 0
    skipped_duplicate_unknown_pairs = 0
    exploratory_pair_count = 0
    for li in left_ids:
        L = store[li]
        for ri in right_ids:
            if li == ri:
                continue
            right_is_anchor = (alias_src(ri), code_of(ri)) in anchors
            if not args.exploratory and not right_is_anchor:
                continue
            if args.exploratory and not right_is_anchor and ri in left_ids and li > ri:
                skipped_duplicate_unknown_pairs += 1
                continue
            left_family = evidence_source_family(li)
            right_family = evidence_source_family(ri)
            if left_family is None or right_family is None:
                skipped_unknown_lineage += 1
                continue
            if left_family == right_family:
                skipped_same_family += 1
                continue
            R = store[ri]
            if L["type"] != R["type"]:
                continue
            if L["type"] == "num" and not range_overlap(L, R):
                continue
            res = collide_pair(L, R)
            if args.exploratory and mark_exploratory_candidate(res, right_is_anchor):
                exploratory_pair_count += 1
            refuted = CR.match_refuted(li, ri) if RULES_OK else None
            if refuted is None:
                method_candidate = method_candidates_for_pair(li, ri, L, R)
                if method_candidate is not None:
                    method_candidate_count += 1
                    method_candidate_sequence += 1
                    score = (
                        len(method_candidate["methods"]),
                        method_candidate["sample_count"],
                        method_candidate["left"],
                        method_candidate["right"],
                    )
                    item = (score, method_candidate_sequence, method_candidate)
                    if len(method_candidate_heap) < MAX_METHOD_CANDIDATES:
                        heapq.heappush(method_candidate_heap, item)
                    elif score > method_candidate_heap[0][0]:
                        heapq.heapreplace(method_candidate_heap, item)
            if res:
                if refuted is not None:
                    guardrail_hits.append(
                        {
                            "left": li,
                            "right": ri,
                            "id": refuted["id"],
                            "false_claim": refuted["false_claim"],
                        }
                    )
                    continue
                res["left"] = li
                res["right"] = ri
                res["same_code"] = code_of(li) == code_of(ri)
                res["evidence_sources"] = sorted(
                    {evidence_source_family(li), evidence_source_family(ri)}
                )
                raw_pairs.append(res)

    method_candidates = [item[2] for item in method_candidate_heap]
    method_candidates.sort(
        key=lambda candidate: (
            len(candidate["methods"]),
            candidate["sample_count"],
            candidate["left"],
            candidate["right"],
        ),
        reverse=True,
    )
    if method_candidate_count > len(method_candidates):
        diagnostics.append(
            f"主动方法候选共 {method_candidate_count} 条，报告保留优先级最高的 "
            f"{len(method_candidates)} 条"
        )
    if skipped_same_family:
        diagnostics.append(f"跳过同一来源家族字段对：{skipped_same_family}")
    if skipped_unknown_lineage:
        diagnostics.append(f"跳过来源独立性未确认的字段对：{skipped_unknown_lineage}")
    if skipped_duplicate_unknown_pairs:
        diagnostics.append(f"探索模式去重未知字段对：{skipped_duplicate_unknown_pairs}")
    if exploratory_pair_count:
        diagnostics.append(
            f"探索模式产生非锚候选：{exploratory_pair_count} 对；即使数值高度吻合也降为 L4，不写入定案状态"
        )

    # 6) hub 巧合排除：单字段匹配过多 → 降级
    left_count = defaultdict(int)
    right_count = defaultdict(int)
    for p in raw_pairs:
        left_count[p["left"]] += 1
        right_count[p["right"]] += 1
    for p in raw_pairs:
        if left_count[p["left"]] > HUB_MAX or right_count[p["right"]] > HUB_MAX:
            if p["level"] in ("L1", "L1-U"):
                p["level"] = "L4"
                p["hub_flag"] = True

    # 7) 增量状态合并
    st = load_state()
    diagnostics.extend(st.pop("warnings", []))
    state_save_allowed = not st.pop("read_error", False)
    findings = st["findings"]
    new_count = 0
    for p in raw_pairs:
        if p["level"] not in ("L1", "L1-U"):
            continue
        key = "||".join(sorted([p["left"], p["right"]]))
        prev = findings.get(key)
        rec = {
            "left": p["left"],
            "right": p["right"],
            "level": p["level"],
            "ratio": p["ratio"],
            "overall_hit": p["overall_hit"],
            "n_days": p["n_days"],
            "n_pairs": p["n_pairs"],
            "sample_dates": p["distinct_days"],
            "evidence_sources": sorted(
                {evidence_source_family(p["left"]), evidence_source_family(p["right"])}
            ),
            "hub_flag": p.get("hub_flag", False),
            "last_seen": today,
        }
        # 是否已在 registry 映射中（已定案）
        lv = (alias_src(p["left"]), code_of(p["left"]))
        rv = (alias_src(p["right"]), code_of(p["right"]))
        rec["in_registry"] = (lv + rv in known_maps) or (rv + lv in known_maps)
        if prev is None:
            rec["first_seen"] = today
            rec["status"] = "new"
            new_count += 1
        else:
            rec["first_seen"] = prev.get("first_seen", today)
            rec["status"] = (
                "confirmed"
                if (prev.get("status") == "confirmed" or rec["in_registry"])
                else "repeated"
            )
        p["in_registry"] = rec["in_registry"]  # 回写供报告读取
        findings[key] = rec
    st["findings"] = findings
    st["updated"] = today
    if state_save_allowed:
        save_state(st)
    else:
        diagnostics.append("collision_state 未写回：原状态文件格式/读取异常，已保留现场")
    diagnostics = list(dict.fromkeys(diagnostics))

    # 8) 输出报告
    l1 = [p for p in raw_pairs if p["level"] in ("L1", "L1-U")]
    l4 = [p for p in raw_pairs if p["level"] == "L4"]
    l1.sort(key=lambda p: (-p["overall_hit"], -p["n_days"]))
    l4.sort(key=lambda p: -p["overall_hit"])

    report_md = build_report_md(
        today,
        list(folder_window.trading_dates),
        len(store),
        total,
        left_ids,
        l1,
        l4,
        new_count,
        verified,
        guardrail_hits,
        method_candidates=method_candidates,
        diagnostics=diagnostics,
        event_window=(folder_window.event_start, folder_window.event_end),
    )
    out_dir = os.path.join(DATA_DIR, today)
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, f"{today}_collision_report.md")
    json_path = os.path.join(out_dir, f"{today}_collision_report.json")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "schema_version": 2,
                "date": today,
                "collision_mode": "exploratory" if args.exploratory else "verified_anchor_only",
                "target_count": len(left_ids),
                "verified_identity_count": len(verified),
                "anchor_identity_count": len(anchors),
                "right_field_count": len(right_ids),
                "exploratory_pair_count": exploratory_pair_count,
                "skipped_pairs": {
                    "same_family": skipped_same_family,
                    "unknown_lineage": skipped_unknown_lineage,
                    "duplicate_unknown_exploration": skipped_duplicate_unknown_pairs,
                },
                "trading_window": list(folder_window.trading_dates),
                "event_window": {
                    "start": folder_window.event_start.strftime("%Y%m%d"),
                    "end": folder_window.event_end.strftime("%Y%m%d"),
                },
                "L1": l1,
                "L4": l4,
                "method_candidates": method_candidates[:MAX_METHOD_CANDIDATES],
                "method_candidate_count": method_candidate_count,
                "diagnostics": list(dict.fromkeys(diagnostics)),
                "new_count": new_count,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(
        f"[collide] L1 候选={len(l1)}，L4 候选={len(l4)}，新增定案={new_count}，"
        f"护栏拦截={len(guardrail_hits)}",
        file=sys.stderr,
    )
    print(f"[collide] 报告: {md_path}", file=sys.stderr)
    return md_path, json_path


def _l1_row(p):
    return (
        f"| `{p['left']}` | `{p['right']}` | {p['level']} | "
        f"{p['overall_hit']:.2%} | {p['n_days']} | {p['n_pairs']} | "
        f"{p.get('ratio') or '-'} | {'⚠' if p.get('hub_flag') else ''} | "
        f"{'✅' if p.get('in_registry') else '—'} |"
    )


def build_report_md(
    today,
    window,
    nfields,
    nsamples,
    left_ids,
    l1,
    l4,
    new_count,
    verified,
    guardrail_hits,
    method_candidates=None,
    diagnostics=None,
    event_window=None,
):
    # 拆分：异号同义（跨编号，高价值）优先；同号镜像（同编号）次之
    cross = [p for p in l1 if not p.get("same_code")]
    same = [p for p in l1 if p.get("same_code")]
    cross.sort(key=lambda p: (not p.get("in_registry", False), -p["overall_hit"], -p["n_days"]))
    same.sort(key=lambda p: (not p.get("in_registry", False), -p["overall_hit"], -p["n_days"]))

    L = []
    L.append(f"# 全源对撞报告（{today}）\n")
    trading_window = f"{window[0]} ~ {window[-1]}" if window else "无有效交易日样本"
    L.append(
        f"> 行情窗口：{trading_window}（{len(window)} 个不同交易日）｜"
        f"字段 {nfields} 个｜样本值 {nsamples} 条"
    )
    if event_window:
        L.append(f"> 新闻/公告自然日窗口：{event_window[0]:%Y%m%d} ~ {event_window[1]:%Y%m%d}")
    L.append(
        f"> 主攻目标（unverified）={len(left_ids)}｜新增 L1/L1-U 定案={new_count}｜"
        f"异号同义 {len(cross)} / 同号镜像 {len(same)}\n"
    )
    L.append(
        f"> **规则**：每个定案日有效样本≥{MIN_DAILY_L1}，命中率≥{HIT_RATE_L1_RATIO:.0%}，"
        f"至少 {MULTI_DAY_MIN} 个独立交易日/自然事件日；同一来源族不作为跨源证据；"
        "盘中快照不计入 L1。"
        "（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；"
        "新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。\n"
    )
    L.append("---\n")
    L.append(f"## 一、L1 / L1-U 定案候选 — 异号同义（跨编号，高价值）({len(cross)})\n")
    if cross:
        L.append(
            "| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 比值 | hub | registry |"
        )
        L.append("|:--|:--|:--|--:|--:|--:|--:|:--|:--|")
        for p in cross:
            L.append(_l1_row(p))
    else:
        L.append("_本轮无异号同义候选。_\n")
    L.append(f"\n## 二、L1 / L1-U 定案候选 — 同号镜像（同编号，低优先级）({len(same)})\n")
    if same:
        L.append("| 左字段 | 右字段 | 等级 | 命中率 | 天数 | 样本 | 比值 | hub | registry |")
        L.append("|:--|:--|:--|--:|--:|--:|--:|:--|:--|")
        for p in same:
            L.append(_l1_row(p))
    else:
        L.append("_本轮无同号镜像候选。_\n")
    L.append("\n## 三、L4 存疑候选（{0}）\n".format(len(l4)))
    if l4:
        L.append("| 左字段 | 右字段 | 命中率 | 天数 | 样本 |")
        L.append("|:--|:--|--:|--:|--:|")
        for p in l4[:60]:
            L.append(
                f"| `{p['left']}` | `{p['right']}` | {p['overall_hit']:.2%} | "
                f"{p['n_days']} | {p['n_pairs']} |"
            )
        if len(l4) > 60:
            L.append(f"\n_（仅显示前 60 / 共 {len(l4)}）_")
    else:
        L.append("_本轮无 L4 候选。_\n")
    L.append("\n## 四、已证伪护栏命中（被拦截的伪结论候选）（{0}）\n".format(len(guardrail_hits)))
    if guardrail_hits:
        L.append("| 左字段 | 右字段 | 命中护栏ID | 伪主张 |")
        L.append("|:--|:--|:--|:--|")
        for h in guardrail_hits:
            L.append(f"| `{h['left']}` | `{h['right']}` | {h['id']} | {h['false_claim']} |")
        L.append("\n_以上候选因命中 REFUTED_CONCLUSIONS（数值实证推翻）已被自动判伪，未进入 L1。_")
    else:
        L.append("_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_\n")
    method_candidates = method_candidates or []
    L.append(f"\n## 五、主动方法候选（不直接定案）（{len(method_candidates)}）\n")
    L.append(
        "_候选可能来自稳健相关、仿射公式、逐股时间序列或字段标签线索；"
        "每项保留样本日期和来源，仍需人工复核并以独立证据终判。_\n"
    )
    if method_candidates:
        L.append("| 左字段 | 右字段 | 方法 | 样本 | 日期 | 来源 | 证据摘要 |")
        L.append("|:--|:--|:--|--:|:--|:--|:--|")
        for candidate in method_candidates[:100]:
            method_names = ", ".join(method["method"] for method in candidate["methods"])
            dates = ", ".join(candidate["sample_dates"][:6])
            sources = ", ".join(candidate["evidence_sources"])
            evidence = candidate["methods"][0]
            if evidence["method"] == "robust_correlation":
                summary = (
                    f"Pearson={evidence['pearson']}, Spearman={evidence['spearman']}, "
                    f"LOO稳号={evidence['leave_one_out_sign_stable']}"
                )
            elif evidence["method"] == "affine_formula":
                summary = evidence["formula"]
            elif evidence["method"] == "per_stock_time_series":
                summary = (
                    f"逐股相关={evidence['median_abs_pearson']}, "
                    f"方向一致={evidence['sign_consistency']}"
                )
            else:
                summary = ", ".join(evidence.get("shared_tokens", [])) or "标签线索"
            L.append(
                f"| `{candidate['left']}` | `{candidate['right']}` | {method_names} | "
                f"{candidate['sample_count']} | {dates} | {sources} | {summary} |"
            )
        if len(method_candidates) > 100:
            L.append(f"\n_仅显示前 100 / 共 {len(method_candidates)} 条。_\n")
    else:
        L.append("_本轮无达到门槛的主动方法候选。_\n")

    diagnostics = list(dict.fromkeys(diagnostics or []))
    L.append(f"\n## 六、日期与数据质量告警（{len(diagnostics)}）\n")
    if diagnostics:
        for message in diagnostics[:100]:
            L.append(f"- {message}")
        if len(diagnostics) > 100:
            L.append(f"- 另有 {len(diagnostics) - 100} 条告警，详见同名 JSON 报告。")
    else:
        L.append("_无日期或数据质量告警。_")
    L.append("\n---\n")
    L.append("> 数据来源：通达信 / 项目字段对撞体系。以上为方法论梳理，不构成投资建议。\n")
    return "\n".join(L)


def main():
    if RULES_OK:
        CR.print_active_rules()
    ap = argparse.ArgumentParser(description="全源通用对撞引擎")
    ap.add_argument(
        "--window", type=int, default=7, help="近 N 个交易日；新闻/公告另取近 N 个自然日（默认 7）"
    )
    ap.add_argument("--all", action="store_true", help="使用全部历史日期")
    ap.add_argument("--date", type=str, default="", help="报告日期戳（默认今天）")
    ap.add_argument("--limit", type=int, default=0, help="仅取前 N 个左字段（自测）")
    ap.add_argument(
        "--exploratory",
        action="store_true",
        help="额外探索未知字段之间的候选关系；结果不会因此自动定案",
    )
    ap.add_argument("--min-hit", type=float, default=0.0, help="自定义 L1 命中率（调试）")
    args = ap.parse_args()
    if args.min_hit:
        global HIT_RATE_L1_RATIO
        HIT_RATE_L1_RATIO = args.min_hit
    run(args)


if __name__ == "__main__":
    main()

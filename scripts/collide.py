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
from collections import Counter, defaultdict
from datetime import date, timedelta
from typing import Any

if __package__ in (None, ""):
    _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)

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
from scripts.context_policy import CONTEXT_ONLY_SOURCES, CONTEXT_RECORD_PATHS
from scripts import collision_candidate_triage as CCT
from scripts import collision_registry_context as CRCX

_lineage_aliases = CRCX._lineage_aliases
_verified_official_contract_kind = CRCX._verified_official_contract_kind
from scripts.collision_candidate_methods import (
    CR,
    RULES_OK,
    CONST_MAX_DISTINCT,
    HIT_RATE_L1_RATIO,
    HUB_MAX,
    ID_SUFFIX_HINTS,
    MAX_FIELD_FRONTIER_CANDIDATES,
    MAX_FORMULA_CANDIDATES_PER_TARGET,
    MAX_METHOD_CANDIDATES,
    MAX_TARGET_METHOD_CANDIDATES,
    MIN_CANDIDATE_PAIRS,
    MIN_DAILY_L1,
    MIN_DAILY_L4,
    MIN_INFORMATIVE_DAILY_L1,
    MIN_PAIR,
    MULTI_DAY_MIN,
    RATIO_CV_MAX,
    RATIO_STEPS_SIGNED,
    _eligible_for_l1,
    _informative_pair,
    _median,
    _ratio_step,
    _temporal_candidate,
    classify,
    cv,
    discriminating_sample_for_target,
    formula_candidates_for_target,
    is_close,
    to_num,
)
from scripts import collision_auxiliary_evidence as CAE
from scripts import collision_candidate_reviews as CCR
from scripts import collision_research_state as CRS
from scripts import field_name_candidates as FNC
from scripts import field_registry_api as FRA


from scripts import source_lineage_api as SLA
from scripts.collision_snapshots import (
    _collision_value,
    _event_identity,
    _flatten,
    _is_ftshare_limit_up_record,
    _ftshare_limit_up_trade_date,
    _record_code,
    _record_containers,
    _without_context_records,
    load_snapshots,
)
from scripts.collision_candidate_ranking import (
    _compact_method_candidate,
    _method_candidate_score,
    _method_candidate_summary,
    select_method_candidate_frontier as _select_method_candidate_frontier,
)
from scripts.collision_state import load_state as _load_collision_state
from scripts.collision_state import save_state as _save_collision_state
from scripts import collision_reporting as CREP

append_source_coverage_report = CREP.append_source_coverage_report
append_source_identity_report = CREP.append_source_identity_report
append_contract_anchor_candidates = CREP.append_contract_anchor_candidates
append_research_state_report = CREP.append_research_state_report
_l1_row = CREP._l1_row
build_report_completeness = CREP.build_report_completeness
append_report_completeness_report = CREP.append_report_completeness_report
from scripts.collision_math import (
    correlation_metrics as _correlation_metrics,
    fit_affine_feature as _fit_affine_feature,
    formula_feature as _formula_feature,
    formula_holdout as _formula_holdout,
    pearson as _pearson,
    r_squared as _r_squared,
    ranks as _ranks,
    standard_deviation as _standard_deviation,
)

try:
    _SOURCE_LINEAGE = SLA.load_source_lineage()
except (OSError, ValueError, TypeError):
    _SOURCE_LINEAGE = {"sources": {}, "source_aliases": {}, "runtime_sources": {}}


# ───────────────────────────────────────────────────────────────────────
# 路径与常量
# ───────────────────────────────────────────────────────────────────────
def _set_source_lineage(lineage):
    global _SOURCE_LINEAGE
    _SOURCE_LINEAGE = lineage


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "docs", "field_verification")
REG_PATH = os.path.join(DATA_DIR, "field_registry.json")
STATE_PATH = os.path.join(DATA_DIR, "collision_state.json")
RESEARCH_STATE_PATH = os.path.join(DATA_DIR, "collision_research_state.json.gz")

# 剔除已知异常采集日（数据质量缺陷，不可参与对撞）：
# - 20260814：盘中快照（采集 start=10:49:53，其余日均为 15:00–17:09 收盘后）→
#   当日 change_pct 在 19/20 股同时失配（单日全市场同向，是采集时点问题非字段问题）。
# - 20260815 等周末/节假日目录: 已随 V17.4.21 历史清理被删除(数据回退至真实数据日目录), 不再存在, 故移除。
#   仅保留 20260814(盘中10:49快照, 无法回溯为收盘数据, 仍剔除避免对撞污染)。
EXCLUDE_DIRS = set(EXCLUDED_MARKET_DATES)


# ───────────────────────────────────────────────────────────────────────
# 数值工具
# ───────────────────────────────────────────────────────────────────────


# ───────────────────────────────────────────────────────────────────────
# 原始数据加载与字段扁平化
# ───────────────────────────────────────────────────────────────────────


# ───────────────────────────────────────────────────────────────────────
# 字段分类（数值 / 枚举 / 字符串 / 常量 / 标识符）
# ───────────────────────────────────────────────────────────────────────


# ───────────────────────────────────────────────────────────────────────
# 对撞核心
# ───────────────────────────────────────────────────────────────────────


def collide_pair(L, R, *, contract_anchor=False):
    """Compare fields with per-session sample floors and independent-day gates."""
    left_source = str(L.get("src") or "")
    right_source = str(R.get("src") or "")
    independent_sources = bool(left_source and right_source) and are_independent_sources(
        left_source, right_source
    )
    if left_source and right_source and not independent_sources and not contract_anchor:
        return None
    evidence_gate = independent_sources or contract_anchor
    lv, rv = L["vals"], R["vals"]
    common = set(lv) & set(rv)
    if len(common) < MIN_PAIR:
        return None

    exact_all = defaultdict(lambda: [0, 0])
    exact_l1 = defaultdict(lambda: [0, 0])
    informative_l1 = defaultdict(lambda: [0, 0])
    ratios_by_day = defaultdict(list)
    for key in common:
        a, b = lv[key], rv[key]
        left_num, right_num = to_num(a), to_num(b)
        day_key = key[1]
        exact_all[day_key][1] += 1
        l1_eligible = _eligible_for_l1(L, key) and _eligible_for_l1(R, key)
        informative = _informative_pair(a, b, left_num, right_num)
        if l1_eligible:
            exact_l1[day_key][1] += 1
            if informative:
                informative_l1[day_key][1] += 1
        if left_num is not None and right_num is not None:
            matched = is_close(left_num, right_num)
            if matched:
                exact_all[day_key][0] += 1
                if l1_eligible:
                    exact_l1[day_key][0] += 1
                    if informative:
                        informative_l1[day_key][0] += 1
            if left_num != 0 and right_num != 0:
                ratios_by_day[day_key].append((right_num / left_num, l1_eligible))
        else:
            matched = str(a) == str(b)
            if matched:
                exact_all[day_key][0] += 1
                if l1_eligible:
                    exact_l1[day_key][0] += 1
                    if informative:
                        informative_l1[day_key][0] += 1

    l1_days = {
        day: counts
        for day, counts in exact_l1.items()
        if counts[1] >= MIN_DAILY_L1 and informative_l1[day][1] >= MIN_INFORMATIVE_DAILY_L1
    }
    exact_days_ge = sum(
        informative_l1[day][0] / informative_l1[day][1] >= HIT_RATE_L1_RATIO for day in l1_days
    )
    exact_total_hits = sum(informative_l1[day][0] for day in l1_days)
    exact_total = sum(informative_l1[day][1] for day in l1_days)
    exact_overall = exact_total_hits / exact_total if exact_total else 0.0
    exact_l1_ok = (
        len(l1_days) >= MULTI_DAY_MIN
        and exact_days_ge >= MULTI_DAY_MIN
        and exact_overall >= HIT_RATE_L1_RATIO
        and not L["is_constant"]
        and not R["is_constant"]
        and evidence_gate
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
        selected_evidence_days = informative_l1
        overall = exact_overall
        days_ge = exact_days_ge
    elif ratio_info is not None and not L["is_constant"] and not R["is_constant"] and evidence_gate:
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

    statistical_level = level
    if contract_anchor and not independent_sources and level in ("L1", "L1-U"):
        level = "L1-C"

    if statistical_level == "L1":
        informative_report_days = informative_l1
        n_informative_pairs = sum(total for _, total in selected_evidence_days.values())
    elif statistical_level == "L1-U":
        informative_report_days = ratio_days
        n_informative_pairs = None
    else:
        informative_report_days = informative_l1
        n_informative_pairs = None

    return {
        "left": None,
        "right": None,
        "level": level,
        "statistical_level": statistical_level,
        "ratio": ratio_info if statistical_level == "L1-U" else None,
        "anchor_basis": "official_contract" if contract_anchor else "independent_source",
        "source_independence_confirmed": independent_sources,
        "overall_hit": round(overall, 4),
        "days_ge_threshold": days_ge,
        "n_days": len(selected_days),
        "n_pairs": sum(total for _, total in selected_days.values()),
        "n_informative_pairs": n_informative_pairs,
        "distinct_days": sorted(selected_days),
        "daily_sample_counts": {day: total for day, (_, total) in selected_days.items()},
        "daily_informative_sample_counts": {
            day: informative_report_days[day][1]
            for day in selected_days
            if day in informative_report_days
        },
        "daily_informative_hit_counts": {
            day: informative_report_days[day][0]
            for day in selected_days
            if day in informative_report_days
        },
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


def _semantic_tokens(fid):
    label = code_of(fid).lower()
    if re.fullmatch(r"(?:f\d+|tx\[\d+\])", label):
        return set()
    tokens = set(re.findall(r"[a-z]+|\d+|[\u4e00-\u9fff]+", label))
    return {token for token in tokens if not token.isdigit()}


def _method_candidate_for_pair(left_id, right_id, L, R):
    """Return a non-final candidate and the reason when no method signal is found."""
    common = sorted(set(L["vals"]) & set(R["vals"]), key=lambda item: (item[1], item[0]))
    if len(common) < MIN_CANDIDATE_PAIRS:
        return None, "insufficient_common_samples"
    numeric = []
    for key in common:
        left_num = to_num(L["vals"][key])
        right_num = to_num(R["vals"][key])
        if left_num is not None and right_num is not None:
            numeric.append((key, left_num, right_num))
    if len(numeric) < MIN_CANDIDATE_PAIRS:
        return None, "insufficient_numeric_samples"

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
        return None, "no_method_signal"

    sample_dates = sorted({row[0][1] for row in numeric})
    evidence_sources = sorted({str(L.get("src") or ""), str(R.get("src") or "")})
    evidence_sources = [source for source in evidence_sources if source]
    return (
        {
            "left": left_id,
            "right": right_id,
            "methods": methods,
            "sample_count": len(numeric),
            "sample_dates": sample_dates,
            "evidence_sources": evidence_sources,
            "sample_codes": sorted({row[0][0] for row in numeric})[:20],
        },
        "candidate",
    )


def method_candidates_for_pair(left_id, right_id, L, R):
    """Compatibility wrapper returning a candidate or ``None``."""
    return _method_candidate_for_pair(left_id, right_id, L, R)[0]


def select_method_candidate_frontier(method_candidates_by_left, global_candidates):
    return _select_method_candidate_frontier(
        method_candidates_by_left, global_candidates, MAX_FIELD_FRONTIER_CANDIDATES
    )


def load_field_coverage_index(folder_paths, trading_dates, event_start, event_end):
    coverage_root = os.path.join(ROOT, ".tmp", "field_evidence_coverage")
    return CCT.load_field_coverage_index(
        folder_paths, trading_dates, event_start, event_end, coverage_root
    )


def _coverage_records_for_target(fid, coverage_index):
    return CCT.coverage_records_for_target(
        fid, coverage_index, alias_src, code_of, SLA.normalize_runtime_field_code
    )


def build_candidate_triage(
    left_ids,
    candidate_counts,
    pair_stats,
    method_candidates_by_left,
    coverage_index,
    formula_by_left,
    sample_by_left,
    pair_family_counts=None,
):
    return CCT.build_candidate_triage(
        left_ids,
        candidate_counts,
        pair_stats,
        method_candidates_by_left,
        coverage_index,
        formula_by_left,
        sample_by_left,
        _coverage_records_for_target,
        _method_candidate_summary,
        pair_family_counts,
    )


def _known_mapping_candidate_controls(store, known_mappings):
    identity_index = defaultdict(list)
    for fid in store:
        identity_index[(alias_src(fid), code_of(fid))].append(fid)
    pair_keys = set()
    for left_alias, left_code, right_alias, right_code in known_mappings:
        left_identity = (left_alias, left_code)
        right_identity = (right_alias, right_code)
        if left_identity == right_identity:
            continue
        pair_keys.add(tuple(sorted((left_identity, right_identity))))
    counts = Counter()
    for left_identity, right_identity in sorted(pair_keys):
        left_ids = identity_index.get(left_identity, [])
        right_ids = identity_index.get(right_identity, [])
        if len(left_ids) != 1 or len(right_ids) != 1:
            counts["missing_or_ambiguous_runtime_pairs"] += 1
            continue
        left_id, right_id = left_ids[0], right_ids[0]
        if not are_independent_sources(left_id, right_id):
            counts["same_or_unconfirmed_family_pairs"] += 1
            continue
        left, right = store[left_id], store[right_id]
        if left.get("type") != "num" or right.get("type") != "num":
            counts["non_numeric_pairs"] += 1
            continue
        eligible, pair_reason = _pair_analysis_eligibility(left, right)
        if not eligible:
            counts["incompatible_type_pairs"] += 1
            continue
        if pair_reason == "range_disjoint":
            counts["range_disjoint_pairs"] += 1
        counts["eligible_numeric_pairs"] += 1
        candidate, reason = _method_candidate_for_pair(left_id, right_id, left, right)
        if candidate is not None:
            counts["with_method_signal"] += 1
        elif reason.startswith("insufficient"):
            counts["insufficient_numeric_samples"] += 1
        else:
            counts["without_method_signal"] += 1
    return {
        "positive_control": {
            "control": "observed, independently mapped numeric pairs in the current window",
            "eligible_numeric_pairs": counts["eligible_numeric_pairs"],
            "with_method_signal": counts["with_method_signal"],
            "without_method_signal": counts["without_method_signal"],
            "insufficient_numeric_samples": counts["insufficient_numeric_samples"],
            "same_or_unconfirmed_family_pairs": counts["same_or_unconfirmed_family_pairs"],
            "missing_or_ambiguous_runtime_pairs": counts["missing_or_ambiguous_runtime_pairs"],
            "non_numeric_pairs": counts["non_numeric_pairs"],
            "incompatible_type_pairs": counts["incompatible_type_pairs"],
            "range_disjoint_pairs": counts["range_disjoint_pairs"],
            "interpretation": (
                "数值区间不相交只作诊断，仍会检查比值和仿射关系；覆盖率用于检查候选方法能否找回已登记映射，"
                "不是准确率或定案条件。"
            ),
        }
    }


def _pair_analysis_eligibility(left, right):
    """Report type compatibility and range diagnostics without pruning numeric pairs.

    Unit conversions and affine relationships can place valid fields in disjoint
    numeric ranges, so range separation is diagnostic only.
    """
    if left.get("type") != right.get("type"):
        return False, "incompatible_type"
    if left.get("type") != "num":
        return True, "eligible"
    if any(left.get(key) is None or right.get(key) is None for key in ("vmin", "vmax")):
        return True, "eligible"
    if left["vmax"] < right["vmin"] or right["vmax"] < left["vmin"]:
        return True, "range_disjoint"
    return True, "eligible"


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


def load_registry_context():
    """Load the read-only context through the compatibility façade."""
    return CRCX.load_registry_context(REG_PATH, SLA.load_source_lineage, _set_source_lineage)


def load_registry_state():
    """Compatibility contract: return (verified_set, known_mapping_pairs)."""
    context = load_registry_context()
    return context["verified"], context["known_mappings"]


norm_src_of = CRCX.norm_src_of


def alias_src(fid):
    return CRCX.alias_source(fid, _SOURCE_LINEAGE)


def evidence_source_family(fid):
    return CRCX.evidence_source_family(fid, _SOURCE_LINEAGE)


def are_independent_sources(left_fid, right_fid):
    return CRCX.are_independent_sources(left_fid, right_fid, _SOURCE_LINEAGE)


def code_of(fid):
    return CRCX.code_of(fid, SLA.normalize_runtime_field_code)


def is_verified(fid, verified):
    return CRCX.is_verified(fid, verified, _SOURCE_LINEAGE)


def is_disproved(fid, disproved):
    return CRCX.is_disproved(fid, disproved, _SOURCE_LINEAGE)


def select_collision_fields(
    store, verified, disproved, anchors, exploratory=False, contract_anchors=None
):
    return CRCX.select_collision_fields(
        store, verified, disproved, anchors, exploratory, contract_anchors, _SOURCE_LINEAGE
    )


def build_source_coverage_report(
    store,
    verified,
    anchors,
    contract_anchors,
    official_contract_verified,
    official_contract_anchors,
    left_ids,
    right_ids,
    pair_evaluations_by_source,
    l1_relations,
    l1_contract_relations,
    l4_relations,
    method_candidate_inventory,
):
    return CCT.build_source_coverage_report(
        store,
        verified,
        anchors,
        contract_anchors,
        official_contract_verified,
        official_contract_anchors,
        left_ids,
        right_ids,
        pair_evaluations_by_source,
        l1_relations,
        l1_contract_relations,
        l4_relations,
        method_candidate_inventory,
        norm_src_of,
        code_of,
    )


def mark_exploratory_candidate(result, right_is_anchor):
    """Keep non-anchor exploratory matches visible without promoting them to L1."""
    if result is None or right_is_anchor:
        return False
    result["exploratory"] = True
    if result.get("level") in ("L1", "L1-U"):
        result["level"] = "L4"
    return True


# ───────────────────────────────────────────────────────────────────────
# 主流程
# ───────────────────────────────────────────────────────────────────────
def load_state():
    return _load_collision_state(STATE_PATH)


def save_state(st):
    return _save_collision_state(STATE_PATH, st)


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
        allowed_trading_dates=frozenset(folder_window.trading_dates),
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

    routine_suppression = {"sources": {}}
    if not args.all and not args.exploratory:
        try:
            try:
                from scripts.axdata_daily_validation import get_axdata_collision_suppressions
            except ModuleNotFoundError:
                from axdata_daily_validation import get_axdata_collision_suppressions

            routine_suppression["sources"].update(get_axdata_collision_suppressions())
        except Exception as exc:
            diagnostics.append(
                f"AxData 日常碰撞排除状态读取失败，保留所有样本: {type(exc).__name__}: {exc}"
            )
        routine_suppression["sources"]["ftshare"] = {
            "status": "retired",
            "interface_id": "FTShare private hosted MCP",
            "reason": "底层公开来源无法验证，当前仅保留历史证据",
        }
    if routine_suppression["sources"]:
        diagnostics.append(
            "日常碰撞排除来源: "
            + ", ".join(
                f"{source}={identity.get('interface_id', 'unknown')}"
                for source, identity in sorted(routine_suppression["sources"].items())
            )
        )
    # 2) Load only quality-selected source snapshots; sample keys include date domain.
    store = defaultdict(lambda: {"vals": {}, "scheme": None, "src": None, "sample_meta": {}})
    total = load_snapshots(
        snapshots,
        store,
        diagnostics,
        event_start=folder_window.event_start,
        event_end=folder_window.event_end,
        include_context=getattr(args, "include_context", False),
        excluded_sources=routine_suppression["sources"],
        allowed_trading_dates=folder_window.trading_dates,
    )
    classify(store)
    print(
        f"[collide] 加载 {len(folder_window.folders)} 个采集目录、"
        f"{len(folder_window.trading_dates)} 个有效交易日、{len(store)} 个字段、"
        f"{total} 条样本值",
        file=sys.stderr,
    )

    # 3) Registry identities, reviewed contract evidence and eligible anchors.
    registry_context = load_registry_context()
    verified = registry_context["verified"]
    disproved = registry_context["disproved"]
    anchors = registry_context["anchors"]
    contract_anchors = registry_context["contract_anchors"]
    official_contract_verified = registry_context["official_contract_verified"]
    official_contract_anchors = registry_context["official_contract_anchors"]
    known_maps = registry_context["known_mappings"]
    diagnostics.extend(registry_context["diagnostics"])

    # 4) Candidate targets exclude verified and explicitly disproved identities.
    if registry_context["safe_to_run"]:
        left_ids, safe_right_ids = select_collision_fields(
            store,
            verified,
            disproved,
            anchors,
            exploratory=False,
            contract_anchors=contract_anchors,
        )
    else:
        left_ids, safe_right_ids = [], []
        diagnostics.append("注册表或来源谱系未通过完整性校验；本轮不执行字段对撞")
    if args.exploratory and registry_context["safe_to_run"]:
        # Opt-in only: useful for candidate discovery, but unknown×unknown must
        # never be mistaken for a verified anchor.
        _, right_ids = select_collision_fields(
            store,
            verified,
            disproved,
            anchors,
            exploratory=True,
            contract_anchors=contract_anchors,
        )
        diagnostics.append("已启用探索模式：未知字段间也会生成候选；须独立复核后才能定案")
    elif registry_context["safe_to_run"]:
        right_ids = safe_right_ids
    else:
        right_ids = []
    diagnostics.append(
        f"对撞模式：{'exploratory' if args.exploratory else 'verified_anchor_only'}；"
        f"待破解字段={len(left_ids)}，verified 字段={len(verified)}，"
        f"可用独立锚={len(anchors)}，官方契约字段={len(official_contract_verified)}，"
        f"L1-C 契约锚={len(contract_anchors)}，"
        f"right 字段={len(right_ids)}"
    )

    if args.limit:
        left_ids = left_ids[: args.limit]
    print(
        f"[collide] 主攻目标(left)={len(left_ids)}，"
        f"{'探索字段(right)' if args.exploratory else '已确认独立锚/官方契约锚(right)'}={len(right_ids)}",
        file=sys.stderr,
    )

    # 5) 两两对撞
    raw_pairs = []  # (left, right, result)
    guardrail_hits = []  # 命中 REFUTED_CONCLUSIONS 被拦截的伪结论候选
    method_candidate_heap = []
    method_candidate_inventory = []
    method_candidates_by_left = defaultdict(list)
    method_candidate_counts = Counter()
    pair_stats_by_left = defaultdict(Counter)
    pair_evaluations_by_source = defaultdict(Counter)
    anchor_family_counts_by_left = defaultdict(Counter)
    method_candidate_count = 0
    method_candidate_sequence = 0
    refuted_candidate_controls = Counter()
    refuted_candidate_examples = []
    skipped_same_family = 0
    skipped_unknown_lineage = 0
    contract_anchor_pair_count = 0
    skipped_duplicate_unknown_pairs = 0
    exploratory_pair_count = 0
    for li in left_ids:
        L = store[li]
        for ri in right_ids:
            if li == ri:
                continue
            right_identity = (alias_src(ri), code_of(ri))
            right_is_independent_anchor = right_identity in anchors
            right_is_contract_anchor = right_identity in contract_anchors
            right_is_anchor = right_is_independent_anchor or right_is_contract_anchor
            if not args.exploratory and not right_is_anchor:
                continue
            if args.exploratory and not right_is_anchor and ri in left_ids and li > ri:
                skipped_duplicate_unknown_pairs += 1
                continue
            left_family = evidence_source_family(li)
            right_family = evidence_source_family(ri)
            if (left_family is None or right_family is None) and not right_is_contract_anchor:
                skipped_unknown_lineage += 1
                pair_stats_by_left[li]["unknown_lineage_skips"] += 1
                continue
            if left_family is not None and left_family == right_family:
                skipped_same_family += 1
                pair_stats_by_left[li]["same_family_skips"] += 1
                continue
            R = store[ri]
            eligible, pair_reason = _pair_analysis_eligibility(L, R)
            if not eligible:
                pair_stats_by_left[li]["incompatible_type_skips"] += 1
                continue
            pair_evaluations_by_source[norm_src_of(li)]["as_target"] += 1
            pair_evaluations_by_source[norm_src_of(ri)]["as_right_field"] += 1
            if right_is_contract_anchor and not right_is_independent_anchor:
                pair_evaluations_by_source[norm_src_of(ri)]["l1c_anchor"] += 1
            if pair_reason == "range_disjoint":
                pair_stats_by_left[li]["range_disjoint_evaluated"] += 1
            if right_is_contract_anchor and not right_is_independent_anchor:
                contract_anchor_pair_count += 1
                pair_stats_by_left[li]["contract_anchor_pairs"] += 1
            else:
                pair_stats_by_left[li]["independent_pairs"] += 1
            if right_is_independent_anchor and right_family is not None:
                anchor_family_counts_by_left[li][right_family] += 1
            res = collide_pair(L, R, contract_anchor=right_is_contract_anchor)
            if args.exploratory and mark_exploratory_candidate(res, right_is_anchor):
                exploratory_pair_count += 1
            refuted = CR.match_refuted(li, ri) if RULES_OK else None
            if refuted is None:
                method_candidate, candidate_reason = _method_candidate_for_pair(li, ri, L, R)
                if candidate_reason.startswith("insufficient"):
                    pair_stats_by_left[li]["insufficient_numeric_samples"] += 1
                elif candidate_reason == "no_method_signal":
                    pair_stats_by_left[li]["no_method_signal"] += 1
                if method_candidate is not None:
                    method_candidate_count += 1
                    method_candidate_inventory.append(method_candidate)
                    method_candidate_counts[li] += 1
                    method_candidate_sequence += 1
                    pair_stats_by_left[li]["method_candidates"] += 1
                    score = _method_candidate_score(method_candidate)
                    item = (score, method_candidate_sequence, method_candidate)
                    if len(method_candidate_heap) < MAX_METHOD_CANDIDATES:
                        heapq.heappush(method_candidate_heap, item)
                    elif score > method_candidate_heap[0][0]:
                        heapq.heapreplace(method_candidate_heap, item)
                    target_candidates = method_candidates_by_left[li]
                    target_candidates.append(method_candidate)
                    target_candidates.sort(key=_method_candidate_score, reverse=True)
                    del target_candidates[MAX_TARGET_METHOD_CANDIDATES:]
            else:
                if L["type"] == "num" and R["type"] == "num":
                    refuted_candidate_controls["numeric_refuted_pairs"] += 1
                    candidate, reason = _method_candidate_for_pair(li, ri, L, R)
                    if candidate is not None:
                        refuted_candidate_controls["with_method_signal"] += 1
                        if len(refuted_candidate_examples) < 20:
                            refuted_candidate_examples.append(
                                {"left": li, "right": ri, "refuted_id": refuted["id"]}
                            )
                    elif reason.startswith("insufficient"):
                        refuted_candidate_controls["insufficient_numeric_samples"] += 1
                    else:
                        refuted_candidate_controls["without_method_signal"] += 1
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
                    family
                    for family in {evidence_source_family(li), evidence_source_family(ri)}
                    if family is not None
                )
                raw_pairs.append(res)

    method_candidates = [item[2] for item in method_candidate_heap]
    method_candidates.sort(key=_method_candidate_score, reverse=True)
    method_candidate_inventory.sort(key=_method_candidate_score, reverse=True)
    method_candidate_frontier = select_method_candidate_frontier(
        method_candidates_by_left, method_candidates
    )
    formula_candidates = []
    formula_search_counts = Counter()
    formula_by_left = {}
    sample_by_left = {}
    for left_id in left_ids:
        target_candidates = method_candidates_by_left.get(left_id, [])
        if not target_candidates:
            continue
        formulas, formula_stats = formula_candidates_for_target(left_id, store, target_candidates)
        formula_by_left[left_id] = formulas
        formula_search_counts.update(formula_stats)
        formula_candidates.extend(formulas)
        if len(target_candidates) >= 2:
            sample_by_left[left_id] = discriminating_sample_for_target(
                left_id, store, target_candidates
            )

    field_coverage_index = load_field_coverage_index(
        folder_window.folders,
        folder_window.trading_dates,
        folder_window.event_start,
        folder_window.event_end,
    )
    diagnostics.extend(field_coverage_index["diagnostics"])
    candidate_triage = build_candidate_triage(
        left_ids,
        method_candidate_counts,
        pair_stats_by_left,
        method_candidates_by_left,
        field_coverage_index,
        formula_by_left,
        sample_by_left,
        anchor_family_counts_by_left,
    )
    candidate_controls = _known_mapping_candidate_controls(store, known_maps)
    candidate_controls["negative_control"] = {
        "control": "candidate method signals against exact pairs listed in REFUTED_CONCLUSIONS",
        "numeric_refuted_pairs": refuted_candidate_controls.get("numeric_refuted_pairs", 0),
        "with_method_signal": refuted_candidate_controls.get("with_method_signal", 0),
        "without_method_signal": refuted_candidate_controls.get("without_method_signal", 0),
        "insufficient_numeric_samples": refuted_candidate_controls.get(
            "insufficient_numeric_samples", 0
        ),
        "examples": refuted_candidate_examples,
        "interpretation": "负向样本若仍出现方法信号，报告会展示为反例；这些信号不会进入普通候选或定案。",
    }
    candidate_triage["summary"]["candidate_pairs_generated"] = method_candidate_count
    candidate_triage["summary"]["global_detail_limit"] = MAX_METHOD_CANDIDATES
    candidate_triage["summary"]["global_details_retained"] = len(method_candidates)
    candidate_triage["summary"]["field_frontier_details_retained"] = len(method_candidate_frontier)
    candidate_triage["summary"]["candidate_pairs_without_full_detail"] = max(
        0, method_candidate_count - len(method_candidate_inventory)
    )
    candidate_triage["summary"]["candidate_pairs_outside_primary_and_frontier"] = max(
        0, method_candidate_count - len(method_candidates) - len(method_candidate_frontier)
    )
    candidate_triage["summary"]["method_candidate_inventory_count"] = len(
        method_candidate_inventory
    )
    candidate_triage["summary"]["formula_combinations_tested"] = formula_search_counts.get(
        "tested", 0
    )
    candidate_triage["summary"]["formula_candidates_validated"] = formula_search_counts.get(
        "validated", 0
    )
    candidate_triage["summary"]["field_coverage"] = field_coverage_index["summary"]
    candidate_triage["summary"]["capture_source_statuses"] = field_coverage_index["source_statuses"]
    if method_candidate_count > len(method_candidates):
        diagnostics.append(
            f"主动方法候选共 {method_candidate_count} 条；全局保留 {len(method_candidates)} 条，"
            f"另按目标字段补充 {len(method_candidate_frontier)} 条字段前沿候选；"
            "完整方法明细保存在 JSON `method_candidate_inventory`"
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
    if contract_anchor_pair_count:
        diagnostics.append(
            f"官方契约锚参与字段对撞 {contract_anchor_pair_count} 对；底层来源独立性未确认，强匹配单列 L1-C"
        )

    # 6) hub 巧合排除：单字段匹配过多 → 降级
    left_count = defaultdict(int)
    right_count = defaultdict(int)
    for p in raw_pairs:
        left_count[p["left"]] += 1
        right_count[p["right"]] += 1
    for p in raw_pairs:
        if left_count[p["left"]] > HUB_MAX or right_count[p["right"]] > HUB_MAX:
            if p["level"] in ("L1", "L1-U", "L1-C"):
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
            if rec["in_registry"]:
                rec["status"] = "confirmed"
            else:
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
    l1_contract = [p for p in raw_pairs if p["level"] == "L1-C"]
    actionable_l1 = [p for p in l1 if not p.get("in_registry", False)]
    mapped_pair_revalidations = [p for p in l1 if p.get("in_registry", False)]
    l4 = [p for p in raw_pairs if p["level"] == "L4"]
    l1.sort(key=lambda p: (-p["overall_hit"], -p["n_days"]))
    l4.sort(key=lambda p: -p["overall_hit"])
    source_coverage = build_source_coverage_report(
        store,
        verified,
        anchors,
        contract_anchors,
        official_contract_verified,
        official_contract_anchors,
        left_ids,
        right_ids,
        pair_evaluations_by_source,
        l1,
        l1_contract,
        l4,
        method_candidate_inventory,
    )
    source_identity = {
        "status": "active_with_historical_legacy",
        "active_runtime_source": "ftshare_rest",
        "active_interface": "FTShare public REST A-share quote list",
        "active_semantic_anchor": "official_documented_contract",
        "upstream_lineage": "unconfirmed",
        "legacy_runtime_source": "ftshare",
        "legacy_status": "retired",
        "legacy_interface": "FTShare private hosted MCP",
        "reason": "FTShare REST contract fields participate as semantic anchors; underlying data independence remains unconfirmed",
        "endpoints": {"a_share_realtime_quote": "/api/v1/market/data/daec/stocks/all"},
    }
    daily_aggregate_evidence = CAE.build_daily_aggregate_evidence(
        folder_window.folders,
        folder_window.trading_dates,
        include_retired_sources=bool(args.all or args.exploratory),
    )
    name_candidate_report = FNC.build_field_name_candidates(
        store, list(store), REG_PATH, _SOURCE_LINEAGE
    )
    diagnostics.extend(daily_aggregate_evidence.get("diagnostics", []))
    diagnostics.extend(name_candidate_report.get("diagnostics", []))

    collision_mode = "exploratory" if args.exploratory else "verified_anchor_only"
    window_selection = {
        "mode": "all_history" if args.all else "trading_days",
        "requested_trading_days": None if args.all else args.window,
    }
    if args.exploratory:
        research_scope = "exploratory_with_context" if args.include_context else "exploratory"
        out_dir = os.path.join(DATA_DIR, f"collision_research_{today}", research_scope, today)
    else:
        out_dir = os.path.join(DATA_DIR, today)
    os.makedirs(out_dir, exist_ok=True)
    md_path = os.path.join(out_dir, f"{today}_collision_report.md")
    json_path = os.path.join(out_dir, f"{today}_collision_report.json")
    report_relative_path = os.path.relpath(json_path, DATA_DIR).replace("\\", "/")
    report_data = {
        "schema_version": 5,
        "date": today,
        "collision_mode": collision_mode,
        "anchor_policy": (
            "verified_independent_and_official_contract" if not args.exploratory else "exploratory"
        ),
        "include_context": bool(args.include_context),
        "window_selection": window_selection,
        "target_count": len(left_ids),
        "verified_identity_count": len(verified),
        "anchor_identity_count": len(anchors),
        "contract_anchor_identity_count": len(contract_anchors),
        "official_contract_verified_identity_count": len(official_contract_verified),
        "official_contract_anchor_identity_count": len(official_contract_anchors),
        "source_coverage": source_coverage,
        "right_field_count": len(right_ids),
        "exploratory_pair_count": exploratory_pair_count,
        "contract_anchor_pair_count": contract_anchor_pair_count,
        "skipped_pairs": {
            "same_family": skipped_same_family,
            "unknown_lineage": skipped_unknown_lineage,
            "duplicate_unknown_exploration": skipped_duplicate_unknown_pairs,
        },
        "routine_collision_suppression": {
            "sources": routine_suppression["sources"],
        },
        "trading_window": list(folder_window.trading_dates),
        "event_window": {
            "start": folder_window.event_start.strftime("%Y%m%d"),
            "end": folder_window.event_end.strftime("%Y%m%d"),
        },
        "L1": l1,
        "L1-C": l1_contract,
        "actionable_L1": actionable_l1,
        "mapped_pair_revalidations": mapped_pair_revalidations,
        "L4": l4,
        "guardrail_hits": guardrail_hits,
        "method_candidates": method_candidates[:MAX_METHOD_CANDIDATES],
        "method_candidate_count": method_candidate_count,
        "method_candidate_inventory": method_candidate_inventory,
        "method_candidate_frontier": method_candidate_frontier,
        "candidate_triage": candidate_triage,
        "formula_candidates": formula_candidates,
        "candidate_controls": candidate_controls,
        "diagnostics": list(dict.fromkeys(diagnostics)),
        "new_candidate_pair_count": new_count,
        # Backward-compatible alias: counts first-seen candidate pairs, not confirmed semantics.
        "new_count": new_count,
        "source_identity_reconciliation": source_identity,
        "daily_aggregate_evidence": daily_aggregate_evidence,
        "field_name_candidates": name_candidate_report,
    }

    candidate_review_state, candidate_review_warnings, candidate_review_writable = CCR.load_state()
    diagnostics.extend(candidate_review_warnings)
    candidate_review_summary = CCR.annotate_report(
        report_data,
        candidate_review_state,
        available=not candidate_review_warnings,
        writable=candidate_review_writable,
    )

    research_state, research_warnings, research_state_writable = CRS.load_state(RESEARCH_STATE_PATH)
    diagnostics.extend(research_warnings)
    research_run_id = None
    research_update = None
    if args.exploratory and research_state_writable:
        research_state, research_run_id, research_update = CRS.update_state(
            research_state, report_data, report_relative_path
        )
    matched_research_pairs = CRS.annotate_report(report_data, research_state, research_run_id)
    current_candidate_pairs = CRS.candidate_pair_count(report_data)
    if research_update is None:
        research_update = {
            "current_candidate_pairs": current_candidate_pairs,
            "new_candidate_pairs": 0,
            "previously_tracked_pairs": matched_research_pairs,
            "total_candidate_pairs": len(research_state.get("candidates", {})),
        }
    report_data["research_state"] = {
        "schema_version": CRS.SCHEMA_VERSION,
        "path": "collision_research_state.json.gz",
        "available": research_state_writable,
        "tracked_candidate_pairs": research_update["total_candidate_pairs"],
        "current_candidate_pairs": research_update["current_candidate_pairs"],
        "new_candidate_pairs": research_update["new_candidate_pairs"],
        "previously_tracked_pairs": research_update["previously_tracked_pairs"],
        "persisted": None,
    }
    report_data["diagnostics"] = list(dict.fromkeys(diagnostics))

    def render_report() -> str:
        rendered = build_report_md(
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
            diagnostics=report_data["diagnostics"],
            event_window=(folder_window.event_start, folder_window.event_end),
            window_selection=window_selection,
        )
        rendered = append_source_identity_report(rendered, source_identity)
        rendered = append_contract_anchor_candidates(rendered, report_data.get("L1-C", []))
        rendered = append_source_coverage_report(rendered, report_data.get("source_coverage", []))
        rendered = CAE.append_daily_aggregate_report(rendered, daily_aggregate_evidence)
        rendered = FNC.append_field_name_candidate_report(rendered, name_candidate_report)
        rendered = append_research_state_report(rendered, report_data["research_state"])
        rendered = append_candidate_triage_report(
            rendered,
            candidate_triage,
            method_candidate_frontier,
            formula_candidates,
            candidate_controls,
        )
        rendered = CCR.append_review_summary_report(rendered, candidate_review_summary)
        return append_report_completeness_report(rendered, report_data["report_completeness"])

    def write_report() -> None:
        report_data["report_completeness"] = build_report_completeness(report_data)
        with open(md_path, "w", encoding="utf-8") as handle:
            handle.write(render_report())
        with open(json_path, "w", encoding="utf-8") as handle:
            json.dump(report_data, handle, ensure_ascii=False, indent=2)

    write_report()
    if args.exploratory and research_state_writable:
        try:
            CRS.save_state(research_state, RESEARCH_STATE_PATH)
            report_data["research_state"]["persisted"] = True
        except (OSError, TypeError, ValueError) as exc:
            warning = f"探索研究台账写入失败；本轮报告已保留，后续可重试：{exc}"
            report_data["diagnostics"].append(warning)
            report_data["diagnostics"] = list(dict.fromkeys(report_data["diagnostics"]))
            diagnostics.append(warning)
            report_data["research_state"]["persisted"] = False
    elif args.exploratory:
        report_data["research_state"]["persisted"] = False
    else:
        report_data["research_state"]["persisted"] = None
    write_report()

    print(
        f"[collide] L1 候选={len(l1)}，L1-C 契约锚候选={len(l1_contract)}，"
        f"L4 候选={len(l4)}，首次发现候选对={new_count}，"
        f"护栏拦截={len(guardrail_hits)}",
        file=sys.stderr,
    )
    print(f"[collide] 报告: {md_path}", file=sys.stderr)
    return md_path, json_path


def append_candidate_triage_report(markdown, triage, frontier, formulas, controls):
    return CREP.append_candidate_triage_report(
        markdown, triage, frontier, formulas, controls, MAX_METHOD_CANDIDATES
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
    window_selection=None,
):
    return CREP.build_report_md(
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
        method_candidates,
        diagnostics,
        event_window,
        window_selection,
        hit_rate_l1_ratio=HIT_RATE_L1_RATIO,
        min_daily_l1=MIN_DAILY_L1,
        min_informative_daily_l1=MIN_INFORMATIVE_DAILY_L1,
        multi_day_min=MULTI_DAY_MIN,
    )


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
        "--include-context",
        action="store_true",
        help="将龙虎榜、人气榜等上下文记录加入研究性碰撞；默认排除",
    )
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

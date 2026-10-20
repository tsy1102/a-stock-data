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
from scripts import collision_auxiliary_evidence as CAE
from scripts import collision_research_state as CRS
from scripts import field_name_candidates as FNC
from scripts import field_registry_api as FRA

try:
    from scripts import collision_rules as CR

    RULES_OK = True
except Exception:
    RULES_OK = False

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
RESEARCH_STATE_PATH = os.path.join(DATA_DIR, "collision_research_state.json.gz")

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
MIN_INFORMATIVE_DAILY_L1 = CR.MIN_INFORMATIVE_SAMPLES_L1 if RULES_OK else 5
MIN_DAILY_L4 = CR.MIN_DAILY_SAMPLES_L4 if RULES_OK else 8
MIN_CANDIDATE_PAIRS = 12  # 方法候选最少配对样本
MAX_METHOD_CANDIDATES = 500
MAX_TARGET_METHOD_CANDIDATES = 8
MAX_FIELD_FRONTIER_CANDIDATES = 1
MAX_FORMULA_CANDIDATES_PER_TARGET = 2
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
def _collision_value(value, *, include_structured=False):
    """Convert JSON source values into stable values the pair matcher can compare."""
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, (int, float, str)):
        return value
    if include_structured and isinstance(value, (list, dict)):
        try:
            return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError):
            return None
    return None


def _flatten(rec, source, scheme, code, date, out, *, include_structured_values=False):
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
            if not isinstance(k, str) or k.startswith("__"):
                continue
            value = _collision_value(v, include_structured=include_structured_values)
            if value is not None:
                out.append((f"{source}.{k}", value))
        return

    # 形态 B：位置列表（tencent / sina）
    flds = rec.get("fields")
    if isinstance(flds, list):
        for i, v in enumerate(flds):
            value = _collision_value(v, include_structured=include_structured_values)
            if value is not None:
                out.append((f"{source}[{i}]", value))
        return

    # 形态 C：嵌套名典 / 标量（zhb full/stat/stat2/tipinfo、tdx quote_full/finance_info、fuyao *、…）
    for sub, subv in rec.items():
        if (
            not isinstance(sub, str)
            or sub.startswith("__")
            or sub
            in (
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
            )
        ):
            continue
        if isinstance(subv, dict):
            source_meta = subv.get("__source_meta__")
            if isinstance(source_meta, dict) and source_meta.get("collision_eligible") is False:
                continue
            for k, v in subv.items():
                if not isinstance(k, str) or k.startswith("__"):
                    continue
                value = _collision_value(v, include_structured=include_structured_values)
                if value is not None:
                    out.append((f"{source}.{sub}.{k}", value))
        else:
            value = _collision_value(subv, include_structured=include_structured_values)
            if value is not None:
                out.append((f"{source}.{sub}", value))


def _is_ftshare_limit_up_record(source, container_code):
    return source == "ftshare" and str(container_code).startswith(
        "__market_limit_up_pool_yesterday_"
    )


def _ftshare_limit_up_trade_date(source, container_code, record):
    if not _is_ftshare_limit_up_record(source, container_code) or not isinstance(record, dict):
        return None
    return parse_date(record.get("trade_date"))


def _record_code(record, container_code, source=None):
    raw_code = (
        record.get("zqdm")
        or record.get("f12")
        or record.get("code")
        or record.get("stockCode")
        or record.get("stock_code")
        or record.get("SECURITY_CODE")
        or record.get("ticker")
        or record.get("symbol")
    )
    code = str(raw_code or container_code)
    if source == "ftshare_rest":
        match = re.fullmatch(r"(?i)(\d{6})(?:\.(?:xshg|xshe|bjse|sh|sz|bj))?", code)
        if match:
            return match.group(1)
    if source == "ftshare" and _is_ftshare_limit_up_record(source, container_code):
        match = re.fullmatch(r"(?i)(\d{6})(?:\.[a-z]+)?", code)
        if match:
            return match.group(1)
    return code


def _without_context_records(doc, source):
    """Return a shallow copy with context-only record paths removed."""
    paths = CONTEXT_RECORD_PATHS.get(source, [])
    if not paths or not isinstance(doc, dict):
        return doc, []
    sanitized = dict(doc)
    excluded = []
    for path in paths:
        node = sanitized
        for part in path[:-1]:
            child = node.get(part) if isinstance(node, dict) else None
            if not isinstance(child, dict):
                node = None
                break
            child_copy = dict(child)
            node[part] = child_copy
            node = child_copy
        if not isinstance(node, dict) or path[-1] not in node:
            continue
        value = node.pop(path[-1])
        count = len(value) if isinstance(value, (dict, list)) else int(value is not None)
        excluded.append((".".join(path), count))
    return sanitized, excluded


def _record_containers(doc, source=None, include_context=False):
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
        if source == "ftshare" and key == "market":
            continue
        if (
            isinstance(value, dict)
            and value
            and all(isinstance(item, (dict, list)) for item in value.values())
        ):
            containers.append(value)
        elif isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            containers.append({f"__{i}": item for i, item in enumerate(value)})
    if include_context and source == "fuyao":
        market = doc.get("market")
        if isinstance(market, dict):
            for key in ("dragon_tiger", "hot_list_hour"):
                records = market.get(key)
                if isinstance(records, list):
                    containers.append(
                        {
                            f"__{key}_{index}": record
                            for index, record in enumerate(records)
                            if isinstance(record, dict)
                        }
                    )
    if include_context and source == "ftshare":
        market = doc.get("market")
        records = market.get("limit_up_pool_yesterday") if isinstance(market, dict) else None
        if isinstance(records, list):
            containers.append(
                {
                    f"__market_limit_up_pool_yesterday_{index}": record
                    for index, record in enumerate(records)
                    if isinstance(record, dict)
                }
            )
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


def load_snapshots(
    snapshots,
    store,
    diagnostics,
    event_start=None,
    event_end=None,
    include_context=False,
    excluded_sources=None,
    allowed_trading_dates=None,
):
    """Flatten selected source snapshots using domain-qualified sample dates."""
    total = 0
    sample_ranks = {}
    duplicate_count = 0
    duplicate_examples = []
    undated_event_counts = defaultdict(int)
    future_event_counts = defaultdict(int)
    undated_market_counts = defaultdict(int)
    out_of_window_market_counts = defaultdict(int)
    allowed_trading_dates = (
        {
            day.strftime("%Y%m%d") if isinstance(day, date) else str(day).replace("-", "")
            for day in allowed_trading_dates
        }
        if allowed_trading_dates is not None
        else None
    )
    for snapshot in snapshots:
        if isinstance(excluded_sources, dict) and snapshot.source in excluded_sources:
            identity = excluded_sources[snapshot.source]
            interface_id = identity.get("interface_id") if isinstance(identity, dict) else identity
            diagnostics.append(
                f"{snapshot.folder}/{snapshot.source}: 日常碰撞已排除来源身份 "
                f"{interface_id or (identity.get('status') if isinstance(identity, dict) else 'unknown')}"
            )
            continue
        if snapshot.source in CONTEXT_ONLY_SOURCES and not include_context:
            diagnostics.append(
                f"{snapshot.folder}/{snapshot.source}: 纯市场上下文源已按默认策略排除；"
                "如需研究性碰撞请使用 --include-context"
            )
            continue
        doc = snapshot.document
        if not include_context:
            doc, excluded_context = _without_context_records(doc, snapshot.source)
            for path, count in excluded_context:
                diagnostics.append(
                    f"{snapshot.folder}/{snapshot.source}/{path}: 默认碰撞已排除上下文记录"
                    f"（{count} 条）"
                )
        scheme = doc.get("scheme")
        auction_meta = doc.get("auction_snapshot_meta")
        if isinstance(auction_meta, dict) and auction_meta.get("collision_eligible") is False:
            diagnostic = (
                f"{snapshot.folder}/{snapshot.source}/stocks.*.auction_final: "
                f"竞价子树已排除；reason={auction_meta.get('exclusion_reason') or 'unspecified'}，"
                f"data_status={auction_meta.get('data_status')!r}，"
                f"source_data_date={auction_meta.get('source_data_date')!r}，"
                f"source_data_date_basis={auction_meta.get('source_data_date_basis')!r}，"
                f"response_timestamp={auction_meta.get('response_timestamp')!r}，"
                f"response_timestamp_date={auction_meta.get('response_timestamp_date')!r}"
                "（仅响应组装时间，不作为数据日期），"
                f"记录数={auction_meta.get('item_count', 0)}"
            )
            diagnostics.append(diagnostic)
        for container in _record_containers(doc, snapshot.source, include_context=include_context):
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
                    sample_date_origin = "record.event_date"
                else:
                    ftshare_trade_day = _ftshare_limit_up_trade_date(
                        snapshot.source, container_code, rec
                    )
                    if _is_ftshare_limit_up_record(snapshot.source, container_code):
                        if ftshare_trade_day is None:
                            undated_market_counts[(snapshot.folder, snapshot.source)] += 1
                            continue
                        trade_day_text = ftshare_trade_day.strftime("%Y%m%d")
                        if ftshare_trade_day > snapshot.sample_date or (
                            allowed_trading_dates is not None
                            and trade_day_text not in allowed_trading_dates
                        ):
                            out_of_window_market_counts[(snapshot.folder, snapshot.source)] += 1
                            continue
                        sample_day = ftshare_trade_day
                        day_key = sample_date_key(TRADING, ftshare_trade_day)
                        sample_date_origin = "record.trade_date"
                    else:
                        day_key = snapshot.day_key
                        sample_date_origin = snapshot.date_origin

                raw_code = (
                    rec.get("zqdm")
                    or rec.get("f12")
                    or rec.get("code")
                    or rec.get("stockCode")
                    or rec.get("stock_code")
                    or rec.get("SECURITY_CODE")
                    or rec.get("ticker")
                )
                code = (
                    str(raw_code or container_code)
                    if snapshot.domain == CALENDAR
                    else _record_code(rec, container_code, source=snapshot.source)
                )
                if snapshot.domain == CALENDAR:
                    entity_code = str(raw_code or "")
                    if not entity_code and re.fullmatch(r"\d{6,}", str(container_code)):
                        entity_code = str(container_code)
                    event_id = _event_identity(snapshot.source, rec, container_code, entity_code)
                    code = f"{code}#event:{event_id}"
                pairs = []
                _flatten(
                    rec,
                    snapshot.source,
                    scheme,
                    code,
                    day_key,
                    pairs,
                    include_structured_values=_is_ftshare_limit_up_record(
                        snapshot.source, container_code
                    ),
                )
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
                        "as_of_date_origin": sample_date_origin,
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
    for (folder, source), count in sorted(undated_market_counts.items()):
        diagnostics.append(f"{folder}/{source}: {count} 条市场记录缺少可解析的来源交易日，已跳过")
    for (folder, source), count in sorted(out_of_window_market_counts.items()):
        diagnostics.append(f"{folder}/{source}: {count} 条市场记录不在所选交易日窗口内，已跳过")
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


def _informative_pair(a, b, left_num, right_num):
    """Ignore jointly missing and 0/0 pairs when exact matches could be coincidental."""
    left_missing = a is None or (isinstance(a, str) and not a.strip())
    right_missing = b is None or (isinstance(b, str) and not b.strip())
    if left_missing and right_missing:
        return False
    if left_num == 0 and right_num == 0:
        return False
    return True


def _ratio_step(value):
    for step in RATIO_STEPS_SIGNED:
        if step != 1 and math.isclose(value, step, rel_tol=0.005, abs_tol=1e-9):
            return step
    return None


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


def _method_candidate_score(candidate):
    return (
        len(candidate["methods"]),
        candidate["sample_count"],
        candidate["left"],
        candidate["right"],
    )


def _compact_method_candidate(candidate):
    """Keep useful method evidence while bounding the target-frontier report size."""
    compact = {key: value for key, value in candidate.items()}
    compact_methods = []
    for method in candidate.get("methods", []):
        item = dict(method)
        if item.get("method") == "per_stock_time_series":
            item["stock_correlations"] = item.get("stock_correlations", [])[:5]
        compact_methods.append(item)
    compact["methods"] = compact_methods
    return compact


def _method_candidate_summary(candidate):
    details = []
    for method in candidate.get("methods", []):
        detail = dict(method)
        if detail.get("method") == "per_stock_time_series":
            detail["stock_correlations"] = detail.get("stock_correlations", [])[:5]
        details.append(detail)
    return {
        "right": candidate["right"],
        "methods": details,
        "sample_count": candidate["sample_count"],
        "sample_dates": candidate["sample_dates"],
        "evidence_sources": candidate["evidence_sources"],
    }


def select_method_candidate_frontier(method_candidates_by_left, global_candidates):
    """Retain one best candidate per target when it falls outside the global cap."""
    global_pairs = {(row["left"], row["right"]) for row in global_candidates}
    frontier = []
    for left_id in sorted(method_candidates_by_left):
        candidates = method_candidates_by_left[left_id]
        for candidate in candidates:
            if (candidate["left"], candidate["right"]) in global_pairs:
                continue
            frontier.append(_compact_method_candidate(candidate))
            if len(frontier) >= MAX_FIELD_FRONTIER_CANDIDATES:
                break
    return frontier


def _fit_affine_feature(feature_values, target_values):
    if len(feature_values) != len(target_values) or len(feature_values) < 2:
        return None
    feature_mean = sum(feature_values) / len(feature_values)
    target_mean = sum(target_values) / len(target_values)
    feature_variance = sum((value - feature_mean) ** 2 for value in feature_values)
    if feature_variance <= 1e-18:
        return None
    slope = (
        sum(
            (feature - feature_mean) * (target - target_mean)
            for feature, target in zip(feature_values, target_values)
        )
        / feature_variance
    )
    intercept = target_mean - slope * feature_mean
    if not math.isfinite(slope) or not math.isfinite(intercept):
        return None
    return slope, intercept


def _r_squared(actual, predicted):
    if len(actual) != len(predicted) or not actual:
        return None
    mean_value = sum(actual) / len(actual)
    total = sum((value - mean_value) ** 2 for value in actual)
    if total <= 1e-18:
        return None
    residual = sum((value - estimate) ** 2 for value, estimate in zip(actual, predicted))
    score = 1.0 - residual / total
    return score if math.isfinite(score) else None


def _standard_deviation(values):
    if not values:
        return 0.0
    mean_value = sum(values) / len(values)
    variance = sum((value - mean_value) ** 2 for value in values) / len(values)
    return math.sqrt(max(0.0, variance))


def _formula_feature(operator, left_value, right_value):
    if operator == "product":
        value = left_value * right_value
    elif operator == "ratio_left_right":
        if abs(right_value) <= 1e-12 * max(1.0, abs(left_value)):
            return None
        value = left_value / right_value
    elif operator == "ratio_right_left":
        if abs(left_value) <= 1e-12 * max(1.0, abs(right_value)):
            return None
        value = right_value / left_value
    elif operator == "sum":
        value = left_value + right_value
    elif operator == "difference":
        value = left_value - right_value
    else:
        return None
    return value if math.isfinite(value) else None


def _formula_holdout(code):
    digest = hashlib.sha256(str(code).encode("utf-8")).digest()
    return int.from_bytes(digest[:2], "big") % 5 == 0


def formula_candidates_for_target(left_id, store, input_candidates):
    """Generate conservative two-input formula clues with stock-level holdout."""
    left = store.get(left_id)
    if not isinstance(left, dict) or left.get("type") != "num":
        return [], {"tested": 0, "validated": 0}

    input_ids = []
    for candidate in input_candidates:
        right_id = candidate.get("right")
        right = store.get(right_id)
        if (
            isinstance(right_id, str)
            and right_id != left_id
            and isinstance(right, dict)
            and right.get("type") == "num"
            and right_id not in input_ids
        ):
            input_ids.append(right_id)
        if len(input_ids) >= MAX_TARGET_METHOD_CANDIDATES:
            break

    operators = (
        ("product", "×"),
        ("ratio_left_right", "÷"),
        ("ratio_right_left", "÷"),
        ("sum", "+"),
        ("difference", "−"),
    )
    tested = 0
    accepted = []
    for first_index, first_id in enumerate(input_ids):
        first = store[first_id]
        for second_id in input_ids[first_index + 1 :]:
            second = store[second_id]
            common = set(left["vals"]) & set(first["vals"]) & set(second["vals"])
            rows = []
            for key in sorted(common, key=lambda item: (item[1], item[0])):
                if not str(key[1]).startswith("T:"):
                    continue
                if not all(_eligible_for_l1(info, key) for info in (left, first, second)):
                    continue
                values = tuple(to_num(info["vals"][key]) for info in (left, first, second))
                if any(value is None for value in values):
                    continue
                rows.append((key, values[0], values[1], values[2]))
            codes = {row[0][0] for row in rows}
            days = {row[0][1] for row in rows}
            if len(rows) < 36 or len(codes) < 10 or len(days) < 3:
                continue

            training = [row for row in rows if not _formula_holdout(row[0][0])]
            validation = [row for row in rows if _formula_holdout(row[0][0])]
            training_codes = {row[0][0] for row in training}
            validation_codes = {row[0][0] for row in validation}
            if (
                len(training) < 24
                or len(validation) < 8
                or len(training_codes) < 8
                or len(validation_codes) < 3
            ):
                continue

            for operator, symbol in operators:
                train_features = [_formula_feature(operator, row[2], row[3]) for row in training]
                validation_features = [
                    _formula_feature(operator, row[2], row[3]) for row in validation
                ]
                if any(value is None for value in train_features + validation_features):
                    continue
                tested += 1
                train_target = [row[1] for row in training]
                validation_target = [row[1] for row in validation]
                fit = _fit_affine_feature(train_features, train_target)
                if fit is None:
                    continue
                slope, intercept = fit
                predicted = [slope * value + intercept for value in validation_features]
                validation_r2 = _r_squared(validation_target, predicted)
                target_scale = _standard_deviation(train_target)
                if not target_scale or validation_r2 is None:
                    continue
                normalized_rmse = (
                    math.sqrt(
                        sum(
                            (actual - estimate) ** 2
                            for actual, estimate in zip(validation_target, predicted)
                        )
                        / len(validation_target)
                    )
                    / target_scale
                )

                baseline_scores = []
                for column in (2, 3):
                    single_train = [row[column] for row in training]
                    single_validation = [row[column] for row in validation]
                    single_fit = _fit_affine_feature(single_train, train_target)
                    if single_fit is None:
                        continue
                    single_slope, single_intercept = single_fit
                    single_predicted = [
                        single_slope * value + single_intercept for value in single_validation
                    ]
                    score = _r_squared(validation_target, single_predicted)
                    if score is not None:
                        baseline_scores.append(score)
                baseline_r2 = max(baseline_scores, default=-1.0)
                improvement = validation_r2 - baseline_r2
                if validation_r2 < 0.985 or normalized_rmse > 0.05 or improvement < 0.05:
                    continue

                formula = (
                    f"{left_id} ≈ {slope:.8g} × ({first_id} {symbol} {second_id}) "
                    f"+ {intercept:.8g}"
                )
                accepted.append(
                    {
                        "left": left_id,
                        "right_inputs": [first_id, second_id],
                        "operator": operator,
                        "formula": formula,
                        "training_samples": len(training),
                        "validation_samples": len(validation),
                        "validation_stocks": len(validation_codes),
                        "validation_dates": sorted({row[0][1] for row in validation}),
                        "validation_r2": round(validation_r2, 6),
                        "normalized_rmse": round(normalized_rmse, 6),
                        "best_single_input_r2": round(baseline_r2, 6),
                        "improvement_over_single_input": round(improvement, 6),
                        "evidence_sources": sorted(
                            {
                                str(left.get("src") or ""),
                                str(first.get("src") or ""),
                                str(second.get("src") or ""),
                            }
                            - {""}
                        ),
                        "adjudication_status": "candidate_only",
                    }
                )

    accepted.sort(
        key=lambda item: (
            item["validation_r2"],
            item["improvement_over_single_input"],
            item["validation_samples"],
            item["formula"],
        ),
        reverse=True,
    )
    unique = []
    seen = set()
    for candidate in accepted:
        key = (candidate["left"], tuple(candidate["right_inputs"]), candidate["operator"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
        if len(unique) >= MAX_FORMULA_CANDIDATES_PER_TARGET:
            break
    return unique, {"tested": tested, "validated": len(accepted)}


def discriminating_sample_for_target(left_id, store, input_candidates):
    """Find a stock whose held-out candidate predictions disagree most."""
    left = store.get(left_id)
    if not isinstance(left, dict):
        return None
    candidate_ids = []
    for candidate in input_candidates:
        right_id = candidate.get("right")
        if right_id in store and right_id != left_id and right_id not in candidate_ids:
            candidate_ids.append(right_id)
        if len(candidate_ids) >= MAX_TARGET_METHOD_CANDIDATES:
            break
    if len(candidate_ids) < 2:
        return None

    codes = set()
    for right_id in candidate_ids:
        right = store[right_id]
        codes.update(
            key[0] for key in set(left["vals"]) & set(right["vals"]) if str(key[1]).startswith("T:")
        )

    suggestions = []
    for code in sorted(codes):
        predictions_by_key = defaultdict(list)
        training_target_values = []
        usable_candidates = 0
        usable_candidate_ids = []
        for right_id in candidate_ids:
            right = store[right_id]
            common = set(left["vals"]) & set(right["vals"])
            numeric = []
            for key in common:
                if not str(key[1]).startswith("T:"):
                    continue
                if not all(_eligible_for_l1(info, key) for info in (left, right)):
                    continue
                left_num = to_num(left["vals"][key])
                right_num = to_num(right["vals"][key])
                if left_num is not None and right_num is not None:
                    numeric.append((key, left_num, right_num))
            train = [row for row in numeric if row[0][0] != code]
            held_out = [row for row in numeric if row[0][0] == code]
            if len(train) < MIN_CANDIDATE_PAIRS or not held_out:
                continue
            fit = _fit_affine_feature([row[2] for row in train], [row[1] for row in train])
            if fit is None:
                continue
            usable_candidates += 1
            usable_candidate_ids.append(right_id)
            slope, intercept = fit
            training_target_values.extend(row[1] for row in train)
            for key, _, right_value in held_out:
                predictions_by_key[key].append((right_id, slope * right_value + intercept))
        if usable_candidates < 2 or not training_target_values:
            continue

        scale = max(
            _standard_deviation(training_target_values),
            abs(_median(training_target_values) or 0.0) * 0.01,
            1e-12,
        )
        spreads = []
        for key, predictions in predictions_by_key.items():
            if len(predictions) < 2:
                continue
            values = [prediction for _, prediction in predictions]
            spreads.append((key[1], (max(values) - min(values)) / scale))
        if len({day for day, _ in spreads}) < 2:
            continue
        score = _median([spread for _, spread in spreads]) or 0.0
        suggestions.append(
            {
                "stock_code": code,
                "candidate_count": usable_candidates,
                "out_of_sample_dates": sorted({day for day, _ in spreads}),
                "normalized_prediction_spread": round(score, 6),
                "candidate_fields": usable_candidate_ids,
            }
        )

    if not suggestions:
        return {"status": "no_shared_stock_holdout", "candidate_fields": candidate_ids}
    suggestions.sort(
        key=lambda item: (
            item["normalized_prediction_spread"],
            len(item["out_of_sample_dates"]),
            item["stock_code"],
        ),
        reverse=True,
    )
    best = suggestions[0]
    if best["normalized_prediction_spread"] < 0.02:
        return {
            "status": "candidates_converge_on_existing_samples",
            "candidate_fields": candidate_ids,
            "best_observed_spread": best["normalized_prediction_spread"],
        }
    return {"status": "prioritize_recheck", **best}


def load_field_coverage_index(folder_paths, trading_dates, event_start, event_end):
    """Read the ignored per-capture coverage indices without changing capture data."""
    coverage_root = os.path.join(ROOT, ".tmp", "field_evidence_coverage")
    selected_day_keys = {f"T:{str(value).replace('-', '')}" for value in trading_dates}
    if isinstance(event_start, str):
        event_start = parse_date(event_start)
    if isinstance(event_end, str):
        event_end = parse_date(event_end)
    if isinstance(event_start, date) and isinstance(event_end, date):
        event_day = event_start
        while event_day <= event_end:
            selected_day_keys.add(f"C:{event_day:%Y%m%d}")
            event_day += timedelta(days=1)

    coverage_records = {}
    source_statuses = defaultdict(lambda: defaultdict(set))
    diagnostics = []
    coverage_paths = set()
    metadata_count = 0
    metadata_errors = 0
    for folder in folder_paths:
        folder_path = os.fspath(getattr(folder, "path", folder))
        meta_path = os.path.join(folder_path, "meta.json")
        if not os.path.isfile(meta_path):
            continue
        try:
            with open(meta_path, encoding="utf-8") as handle:
                metadata = json.load(handle)
        except (OSError, ValueError, TypeError) as exc:
            metadata_errors += 1
            diagnostics.append(
                f"字段覆盖索引跳过无效 meta.json：{os.path.basename(folder_path)} ({exc})"
            )
            continue
        if not isinstance(metadata, dict):
            metadata_errors += 1
            diagnostics.append(f"字段覆盖索引跳过非对象 meta.json：{os.path.basename(folder_path)}")
            continue
        metadata_count += 1
        capture_day = str(metadata.get("data_date") or os.path.basename(folder_path))
        capture_day = re.sub(r"[^0-9]", "", capture_day)
        source_records = metadata.get("sources")
        if not isinstance(source_records, dict):
            source_records = {}
        capture_day_selected = bool(
            re.fullmatch(r"\d{8}", capture_day)
            and (f"T:{capture_day}" in selected_day_keys or f"C:{capture_day}" in selected_day_keys)
        )
        if capture_day_selected:
            for source, status_record in source_records.items():
                if isinstance(status_record, dict):
                    status = status_record.get("status") or status_record.get("state") or "unknown"
                elif isinstance(status_record, str):
                    status = status_record
                else:
                    status = "unknown"
                source_statuses[str(source)][str(status)].add(capture_day)

        coverage_meta = metadata.get("field_evidence_coverage")
        if not isinstance(coverage_meta, dict):
            continue
        report_day = re.sub(r"[^0-9]", "", str(coverage_meta.get("report_date") or capture_day))
        if not re.fullmatch(r"\d{8}", report_day):
            continue
        coverage_path = os.path.join(coverage_root, f"coverage_{report_day}.json")
        if coverage_path in coverage_paths or not os.path.isfile(coverage_path):
            continue
        coverage_paths.add(coverage_path)
        try:
            with open(coverage_path, encoding="utf-8") as handle:
                coverage_doc = json.load(handle)
        except (OSError, ValueError, TypeError) as exc:
            diagnostics.append(f"字段覆盖详情读取失败：{os.path.basename(coverage_path)} ({exc})")
            continue
        rows = coverage_doc.get("fields") if isinstance(coverage_doc, dict) else None
        if not isinstance(rows, list):
            diagnostics.append(f"字段覆盖详情格式无效：{os.path.basename(coverage_path)}")
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            source = row.get("source")
            code = row.get("code")
            if not isinstance(source, str) or not isinstance(code, str):
                continue
            identity = (source, code)
            aggregate = coverage_records.setdefault(
                identity,
                {
                    "source": source,
                    "code": code,
                    "registry_status": row.get("registry_status"),
                    "target_kind": row.get("target_kind"),
                    "identity_status": row.get("identity_status"),
                    "runtime_aliases": set(),
                    "independence_family": row.get("independence_family"),
                    "independence_status": row.get("independence_status"),
                    "anchor_eligible": bool(row.get("anchor_eligible")),
                    "source_as_of_days": set(),
                    "candidate_days": set(),
                    "source_as_of_sample_counts": {},
                    "source_statuses": set(),
                },
            )
            aggregate["runtime_aliases"].update(
                alias for alias in row.get("runtime_aliases", []) if isinstance(alias, str)
            )
            aggregate["source_statuses"].update(
                status for status in row.get("source_statuses", []) if isinstance(status, str)
            )
            for date_key in row.get("source_as_of_days", []):
                if date_key in selected_day_keys:
                    aggregate["source_as_of_days"].add(date_key)
            for date_key in row.get("candidate_days", []):
                if date_key in selected_day_keys:
                    aggregate["candidate_days"].add(date_key)
            for date_key, count in (row.get("source_as_of_sample_counts") or {}).items():
                if date_key in selected_day_keys and isinstance(count, int):
                    aggregate["source_as_of_sample_counts"][date_key] = max(
                        count, aggregate["source_as_of_sample_counts"].get(date_key, 0)
                    )

    statuses = {}
    for source, by_status in sorted(source_statuses.items()):
        statuses[source] = {
            "status_counts": {status: len(days) for status, days in sorted(by_status.items())},
            "non_ok_dates": sorted(
                day
                for status, days in by_status.items()
                if status.lower() not in {"ok", "success", "completed"}
                for day in days
            ),
        }
    return {
        "records": coverage_records,
        "source_statuses": statuses,
        "summary": {
            "capture_metadata_files": metadata_count,
            "metadata_errors": metadata_errors,
            "coverage_detail_files": len(coverage_paths),
            "coverage_identity_count": len(coverage_records),
            "detail_status": "available" if coverage_paths else "unavailable",
        },
        "diagnostics": diagnostics,
        "selected_day_keys": selected_day_keys,
    }


def _coverage_records_for_target(fid, coverage_index):
    alias = alias_src(fid)
    target_code = code_of(fid)
    matches = []
    for record in coverage_index.get("records", {}).values():
        if alias not in record.get("runtime_aliases", set()):
            continue
        record_code = SLA.normalize_runtime_field_code(alias, record.get("code", ""))
        if target_code == record_code or (
            alias == "zhb" and target_code.endswith("." + record_code)
        ):
            matches.append(record)

    output = []
    covered_days = set()
    candidate_days = set()
    for record in matches:
        family = record.get("independence_family")
        source_days = sorted(record.get("source_as_of_days", set()))
        possible_days = sorted(record.get("candidate_days", set()))
        covered_days.update(source_days)
        candidate_days.update(possible_days)
        output.append(
            {
                "source": record["source"],
                "code": record["code"],
                "registry_status": record.get("registry_status"),
                "identity_status": record.get("identity_status"),
                "independence_family": family,
                "independence_status": record.get("independence_status"),
                "anchor_eligible": bool(record.get("anchor_eligible")),
                "source_as_of_days": source_days,
                "candidate_days": possible_days,
                "source_as_of_sample_counts": dict(
                    sorted(record.get("source_as_of_sample_counts", {}).items())
                ),
                "source_statuses": sorted(record.get("source_statuses", set())),
            }
        )
    output.sort(
        key=lambda item: (
            item["anchor_eligible"],
            len(item["source_as_of_days"]),
            item["source"],
            item["code"],
        ),
        reverse=True,
    )
    return {
        "status": (
            "available"
            if coverage_index.get("summary", {}).get("coverage_detail_files")
            else "unavailable"
        ),
        "source_count": len(output),
        "source_as_of_days": sorted(covered_days),
        "candidate_days": sorted(candidate_days),
        "sources": output[:8],
    }


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
    pair_family_counts = pair_family_counts or {}
    rows = []
    for left_id in left_ids:
        pair_counts = pair_stats.get(left_id, Counter())
        target_candidates = method_candidates_by_left.get(left_id, [])
        target_coverage = _coverage_records_for_target(left_id, coverage_index)
        target_coverage["independent_anchor_families"] = sorted(
            family for family, count in pair_family_counts.get(left_id, {}).items() if count
        )
        target_coverage["independent_anchor_pairs"] = sum(
            pair_family_counts.get(left_id, {}).values()
        )
        formulas = formula_by_left.get(left_id, [])
        next_sample = sample_by_left.get(left_id)
        count = candidate_counts.get(left_id, 0)
        independent_comparisons = pair_counts.get("independent_pairs", 0)
        independent_family_count = len(target_coverage["independent_anchor_families"])
        if formulas:
            status = "formula_candidate_needs_independent_review"
            priority = 0
        elif count >= 2:
            status = "multiple_method_candidates_need_discrimination"
            priority = 1
        elif count == 1:
            status = "single_method_candidate_needs_external_check"
            priority = 2
        elif pair_counts.get("unknown_lineage_skips", 0) and not independent_comparisons:
            status = "source_lineage_gap"
            priority = 3
        elif target_coverage["source_count"] == 0 and target_coverage["status"] == "available":
            status = "field_coverage_identity_unmapped"
            priority = 4
        elif independent_family_count == 0 and target_coverage["status"] == "available":
            status = "independent_source_coverage_gap"
            priority = 5
        elif pair_counts.get("insufficient_numeric_samples", 0):
            status = "joint_sample_coverage_gap"
            priority = 6
        elif independent_comparisons:
            status = "no_current_method_signal"
            priority = 7
        else:
            status = "no_eligible_comparison"
            priority = 8
        rows.append(
            {
                "left": left_id,
                "status": status,
                "priority": priority,
                "candidate_count": count,
                "pair_counts": dict(pair_counts),
                "top_candidates": [
                    _method_candidate_summary(candidate) for candidate in target_candidates[:2]
                ],
                "formula_candidates": formulas,
                "next_sample": next_sample,
                "coverage": target_coverage,
            }
        )
    rows.sort(
        key=lambda item: (
            item["priority"],
            -item["candidate_count"],
            -len(item["coverage"]["independent_anchor_families"]),
            item["left"],
        )
    )
    summary = {
        "target_count": len(rows),
        "targets_with_method_candidates": sum(row["candidate_count"] > 0 for row in rows),
        "targets_without_method_candidates": sum(row["candidate_count"] == 0 for row in rows),
        "targets_with_multiple_candidates": sum(row["candidate_count"] > 1 for row in rows),
        "targets_with_formula_candidates": sum(bool(row["formula_candidates"]) for row in rows),
        "targets_with_next_sample": sum(
            isinstance(row.get("next_sample"), dict)
            and row["next_sample"].get("status") == "prioritize_recheck"
            for row in rows
        ),
        "targets_with_independent_anchor_coverage": sum(
            bool(row["coverage"]["independent_anchor_families"]) for row in rows
        ),
        "coverage_detail_status": coverage_index.get("summary", {}).get(
            "detail_status", "unavailable"
        ),
        "status_counts": dict(Counter(row["status"] for row in rows)),
    }
    return {"summary": summary, "targets": rows}


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
    """Load verified identities, contract evidence, anchors, mappings and diagnostics."""
    context = {
        "verified": set(),
        "disproved": set(),
        "anchors": set(),
        "contract_anchors": set(),
        "official_contract_verified": set(),
        "official_contract_anchors": set(),
        "known_mappings": set(),
        "diagnostics": [],
        "unmapped_verified": 0,
        "unconfirmed_verified": 0,
        "ambiguous_verified": 0,
        "unresolved_verified_metadata": 0,
        "unresolved_verified_metadata_by_issue": {},
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
    registry_sources = {
        item.get("name"): item
        for item in registry.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    adjudications = {}
    adjudication_sources = [registry.get("adjudications", [])]
    adjudication_sources.extend(
        field.get("adjudications", []) for field in source_fields if isinstance(field, dict)
    )
    for records in adjudication_sources:
        if not isinstance(records, list):
            continue
        for record in records:
            if isinstance(record, dict) and isinstance(record.get("id"), str):
                adjudications[record["id"]] = record
    alias_identity_owners = defaultdict(set)
    for candidate in source_fields:
        if not isinstance(candidate, dict):
            continue
        candidate_source = candidate.get("source")
        candidate_code = candidate.get("code")
        if not isinstance(candidate_source, str) or not isinstance(candidate_code, str):
            continue
        for alias in _lineage_aliases(candidate_source, lineage):
            alias_identity_owners[(alias, candidate_code)].add((candidate_source, candidate_code))

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
            context["contract_anchors"].clear()
            context["official_contract_verified"].clear()
            context["official_contract_anchors"].clear()
            context["known_mappings"].clear()
            return context
        seen_source_identities.add(identity)
        aliases = _lineage_aliases(source, lineage)
        if field.get("status") == "disproved":
            for alias in aliases:
                if alias != "zhb" or len(alias_identity_owners[(alias, code)]) == 1:
                    context["disproved"].add((alias, code))
            continue
        if field.get("status") != "verified":
            continue
        metadata_issues = FRA.source_field_semantic_issues(field)
        if metadata_issues:
            context["unresolved_verified_metadata"] += 1
            for issue in metadata_issues:
                issue_counts = context["unresolved_verified_metadata_by_issue"]
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
            continue
        if not aliases:
            context["unmapped_verified"] += 1
            continue
        for alias in aliases:
            if alias == "zhb" and len(alias_identity_owners[(alias, code)]) != 1:
                context["ambiguous_verified"] += 1
                continue
            identity = (alias, code)
            context["verified"].add(identity)
            family = SLA.runtime_family(alias, lineage)
            source_record = lineage.get("sources", {}).get(source, {})
            source_config = registry_sources.get(source, {})
            contract_evidence_kind = _verified_official_contract_kind(
                field, source_config, source_record, adjudications
            )
            if contract_evidence_kind:
                context["official_contract_verified"].add(identity)
            if (
                source_record.get("anchor_eligible")
                and source_record.get("independence_status") == "confirmed"
                and family == source_record.get("independence_family")
            ):
                context["anchors"].add(identity)
                if contract_evidence_kind:
                    context["official_contract_anchors"].add(identity)
            elif (
                contract_evidence_kind == "semantic_anchor_contract"
                and source_record.get("semantic_anchor_basis") == "official_contract"
            ):
                context["contract_anchors"].add(identity)
                context["official_contract_anchors"].add(identity)
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
                normalized_left_code = SLA.normalize_runtime_field_code(left_alias, left_code)
                normalized_right_code = SLA.normalize_runtime_field_code(right_alias, right_code)
                if (
                    left_alias == "zhb"
                    and len(alias_identity_owners[(left_alias, normalized_left_code)]) != 1
                ):
                    continue
                if (
                    right_alias == "zhb"
                    and len(alias_identity_owners[(right_alias, normalized_right_code)]) != 1
                ):
                    continue
                context["known_mappings"].add(
                    (left_alias, normalized_left_code, right_alias, normalized_right_code)
                )
                context["known_mappings"].add(
                    (right_alias, normalized_right_code, left_alias, normalized_left_code)
                )

    context["safe_to_run"] = True

    if context["unmapped_verified"]:
        context["diagnostics"].append(
            f"{context['unmapped_verified']} 条 verified 源字段无法映射到运行时来源，未作锚"
        )
    if context["unconfirmed_verified"]:
        context["diagnostics"].append(
            f"{context['unconfirmed_verified']} 条 verified 源字段来源未确认独立性，作为已知字段跳过重解但不作锚"
        )
    if context["contract_anchors"]:
        context["diagnostics"].append(
            f"{len(context['contract_anchors'])} 条官方契约语义锚可参与对撞；底层来源独立性未确认，强候选标为 L1-C"
        )
    if context["ambiguous_verified"]:
        context["diagnostics"].append(
            f"{context['ambiguous_verified']} 条 verified 源字段映射到重复运行时身份，未作为已知字段或锚"
        )
    if context["unresolved_verified_metadata"]:
        issue_labels = {
            "meaning_missing": "缺义/占位",
            "meaning_conflict": "含义冲突",
            "unit_conflict": "单位冲突",
            "meaning_alignment_ambiguous": "含义分组待对齐",
            "unit_alignment_ambiguous": "单位分组待对齐",
        }
        issue_summary = "、".join(
            f"{issue_labels.get(issue, issue)} {count} 条"
            for issue, count in sorted(context["unresolved_verified_metadata_by_issue"].items())
        )
        context["diagnostics"].append(
            f"{context['unresolved_verified_metadata']} 条 verified 源字段元数据未达锚点条件"
            f"（{issue_summary}），已重新纳入待破解目标且不作碰撞锚"
        )
    if not context["anchors"] and not context["contract_anchors"]:
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
        code = fid[fid.index("[") :]
    elif "." in fid:
        code = fid.split(".", 1)[1]
    else:
        return fid
    return SLA.normalize_runtime_field_code(norm_src_of(fid), code)


def _verified_official_contract_kind(field, source_config, source_record, adjudications):
    """Return the reviewed contract-evidence kind for an active verified identity."""
    if source_config.get("status") != "active":
        return None

    direct = field.get("evidence")
    source_contract = source_record.get("contract")
    contract_ids = source_config.get("contract_ids")
    if (
        source_config.get("source_role") == "documented_contract_anchor"
        and source_record.get("semantic_anchor_basis") == "official_contract"
        and isinstance(direct, dict)
        and direct.get("basis") == "official_contract"
        and isinstance(source_contract, dict)
        and direct.get("contract_id") == source_contract.get("contract_id")
        and isinstance(contract_ids, list)
        and direct.get("contract_id") in contract_ids
        and direct.get("evidence_file") == source_contract.get("evidence_file")
        and direct.get("documentation_url") == source_contract.get("documentation_url")
    ):
        return "semantic_anchor_contract"

    status_evidence = field.get("status_evidence")
    adjudication_ids = (
        status_evidence.get("source_contract_adjudication_ids", [])
        if isinstance(status_evidence, dict)
        else []
    )
    if not isinstance(adjudication_ids, list):
        return None
    reference_evidence = field.get("reference_evidence", [])
    if not isinstance(reference_evidence, list):
        return None
    for evidence in reference_evidence:
        if not isinstance(evidence, dict):
            continue
        if evidence.get("status") != "verified":
            continue
        if evidence.get("evidence_basis") not in {
            "authoritative_source_contract",
            "official_contract",
        }:
            continue
        contract = evidence.get("source_contract")
        adjudication_id = evidence.get("adjudication_id")
        if (
            not isinstance(contract, dict)
            or not all(contract.get(key) for key in ("authority", "path", "locator", "url"))
            or not isinstance(adjudication_id, str)
            or adjudication_id not in adjudication_ids
        ):
            continue
        adjudication = adjudications.get(adjudication_id, {})
        adjudicated_contract = adjudication.get("source_contract")
        if (
            adjudication.get("action") != "verify_source_contract"
            or adjudication.get("status") != "verified"
            or adjudication.get("evidence_basis") != evidence.get("evidence_basis")
            or not isinstance(adjudicated_contract, dict)
            or any(adjudicated_contract.get(key) != contract.get(key) for key in contract)
        ):
            continue
        return "source_contract"
    return None


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
    """Summarize observed window coverage and actual collision participation by runtime source."""
    rows = defaultdict(
        lambda: {
            "observed_fields": set(),
            "observed_field_values": 0,
            "observed_trading_dates": set(),
            "verified_fields": set(),
            "official_contract_verified_fields": set(),
            "official_contract_anchor_fields": set(),
            "independent_anchor_fields": set(),
            "contract_only_anchor_fields": set(),
            "cracking_target_fields": set(),
            "comparison_fields": set(),
            "L1_relations": 0,
            "L1_C_relations": 0,
            "L4_relations": 0,
            "method_candidate_pairs": 0,
        }
    )

    for fid, info in store.items():
        source = norm_src_of(fid)
        row = rows[source]
        row["observed_fields"].add(code_of(fid))
        values = info.get("vals", {})
        metadata = info.get("sample_meta", {})
        row["observed_field_values"] += len(values)
        for key in values:
            sample_meta = metadata.get(key, {}) if isinstance(metadata, dict) else {}
            if sample_meta.get("domain") == TRADING and sample_meta.get("as_of_date"):
                row["observed_trading_dates"].add(sample_meta["as_of_date"])

    def add_identities(identity_set, target_key):
        for source, code in identity_set:
            rows[source][target_key].add(code)

    add_identities(verified, "verified_fields")
    add_identities(official_contract_verified, "official_contract_verified_fields")
    add_identities(official_contract_anchors, "official_contract_anchor_fields")
    add_identities(anchors, "independent_anchor_fields")
    add_identities(contract_anchors, "contract_only_anchor_fields")
    for fid in left_ids:
        rows[norm_src_of(fid)]["cracking_target_fields"].add(code_of(fid))
    for fid in right_ids:
        rows[norm_src_of(fid)]["comparison_fields"].add(code_of(fid))

    relation_sets = (
        (l1_relations, "L1_relations"),
        (l1_contract_relations, "L1_C_relations"),
        (l4_relations, "L4_relations"),
    )
    for relations, key in relation_sets:
        for relation in relations:
            fields = {
                fid for fid in (relation.get("left"), relation.get("right")) if isinstance(fid, str)
            }
            for fid in fields:
                rows[norm_src_of(fid)][key] += 1
    for candidate in method_candidate_inventory:
        fields = {
            fid for fid in (candidate.get("left"), candidate.get("right")) if isinstance(fid, str)
        }
        for fid in fields:
            rows[norm_src_of(fid)]["method_candidate_pairs"] += 1

    output = []
    for source in sorted(rows):
        row = rows[source]
        pair_stats = pair_evaluations_by_source.get(source, {})
        output.append(
            {
                "source": source,
                "verified_field_count": len(row["verified_fields"]),
                "official_contract_verified_field_count": len(
                    row["official_contract_verified_fields"]
                ),
                "official_contract_anchor_field_count": len(row["official_contract_anchor_fields"]),
                "independent_anchor_field_count": len(row["independent_anchor_fields"]),
                "contract_only_anchor_field_count": len(row["contract_only_anchor_fields"]),
                "observed_window_field_count": len(row["observed_fields"]),
                "observed_window_field_value_count": row["observed_field_values"],
                "observed_window_trading_day_count": len(row["observed_trading_dates"]),
                "cracking_target_field_count": len(row["cracking_target_fields"]),
                "comparison_field_count": len(row["comparison_fields"]),
                "comparisons_as_target": pair_stats.get("as_target", 0),
                "comparisons_as_right_field": pair_stats.get("as_right_field", 0),
                "L1_C_anchor_comparisons": pair_stats.get("l1c_anchor", 0),
                "L1_relation_count": row["L1_relations"],
                "L1_C_relation_count": row["L1_C_relations"],
                "L4_relation_count": row["L4_relations"],
                "method_candidate_pair_count": row["method_candidate_pairs"],
            }
        )
    return output


def append_source_coverage_report(markdown, source_coverage):
    """Render complete per-source contract, observed-data, and collision coverage."""
    lines = [markdown.rstrip(), "", "## 来源字段覆盖与碰撞参与", ""]
    lines.append(
        "_窗口字段值样本是经日期筛选、重复折叠和快照择优后载入的非空值；"
        "右侧比较次数另受字段类型及来源规则筛选。官方契约字段须有逐字段审定证据，"
        "契约语义本身不证明底层数据来源独立。_"
    )
    lines.extend(
        [
            "",
            "| 来源 | 已确认字段 | 契约已确认 | 契约锚 | 独立锚 | L1-C 锚 | 窗口字段 / 字段值样本 / 交易日 |",
            "|:--|--:|--:|--:|--:|--:|--:|",
        ]
    )
    for row in source_coverage:
        lines.append(
            "| {source} | {verified_field_count} | {official_contract_verified_field_count} | "
            "{official_contract_anchor_field_count} | {independent_anchor_field_count} | "
            "{contract_only_anchor_field_count} | {observed_window_field_count} / "
            "{observed_window_field_value_count} / {observed_window_trading_day_count} |".format(
                **row
            )
        )
    if not source_coverage:
        lines.append("| _无来源数据_ | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |")
    lines.extend(
        [
            "",
            "| 来源 | 破解目标 | 比较字段 | 作目标比较 | 作右侧比较 | L1-C 锚比较 | L1 / L1-C / L4 关系 | 方法候选涉及 |",
            "|:--|--:|--:|--:|--:|--:|--:|--:|",
        ]
    )
    for row in source_coverage:
        lines.append(
            "| {source} | {cracking_target_field_count} | {comparison_field_count} | "
            "{comparisons_as_target} | {comparisons_as_right_field} | {L1_C_anchor_comparisons} | "
            "{L1_relation_count} / {L1_C_relation_count} / {L4_relation_count} | "
            "{method_candidate_pair_count} |".format(**row)
        )
    if not source_coverage:
        lines.append("| _无来源数据_ | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 | 0 |")
    lines.append("")
    return "\n".join(lines) + "\n"


def is_verified(fid, verified):
    return (alias_src(fid), code_of(fid)) in verified


def is_disproved(fid, disproved):
    return (alias_src(fid), code_of(fid)) in disproved


def select_collision_fields(
    store, verified, disproved, anchors, exploratory=False, contract_anchors=None
):
    """Return unknown cracking targets and the allowed comparison field set.

    Verified status removes an identity only from the left-hand cracking targets.
    Independently confirmed verified fields remain on the right as anchors; capture
    routing is source-level and never consults this field status.
    """
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
    contract_anchors = contract_anchors or set()
    right = [
        fid
        for fid in eligible
        if (alias_src(fid), code_of(fid)) in anchors
        or (alias_src(fid), code_of(fid)) in contract_anchors
    ]
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
        "schema_version": 4,
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


def append_source_identity_report(report_md, result):
    """Append active REST and retired legacy FTShare identities to the report."""
    lines = [report_md.rstrip(), "", "## 来源身份状态（不参与字段语义定案）", ""]
    if isinstance(result, dict) and result.get("active_runtime_source") == "ftshare_rest":
        lines.append(
            "_FTShare 公共 REST 接口已进入日常采集；官方字段契约作为语义锚，"
            "底层数据提供方仍未确认。与其匹配的强候选列在 L1-C，不混入独立来源 L1。_"
        )
        lines.append("_旧私有托管 MCP 采集器已退役，历史样本仅供 `--all` / `--exploratory` 追溯。_")
    else:
        lines.append("_当前没有运行来源身份核验；历史核验摘要见每日辅助证据。_")
    lines.append("")
    return "\n".join(lines) + "\n"


def append_contract_anchor_candidates(report_md, candidates):
    """Render contract-backed candidates without presenting them as independent-source L1."""
    lines = [
        report_md.rstrip(),
        "",
        f"## 官方契约锚候选 L1-C（{len(candidates)}）",
        "",
        "_L1-C 使用逐字段审定的官方接口契约语义作锚，并满足多日数值匹配门槛；"
        "仅当该接口底层数据来源独立性未确认时才列入此处，不属于独立来源 L1，也不自动定案。_",
        "",
    ]
    if candidates:
        lines.extend(
            [
                "| 左字段（待确认） | 官方契约字段 | 等级 | 命中率 | 交易日数 | 样本 | 信息样本 | 比值 | hub | registry |",
                "|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|",
            ]
        )
        lines.extend(_l1_row(candidate) for candidate in candidates)
    else:
        lines.append("_本轮无达到多日门槛的官方契约锚候选。_")
    lines.append("")
    return "\n".join(lines) + "\n"


def append_research_state_report(report_md: str, state_summary: dict) -> str:
    """Show research carry-forward status without promoting candidates."""
    lines = [report_md.rstrip(), "", "## 探索候选持续跟踪", ""]
    lines.append(
        f"研究台账：`{state_summary.get('path', 'collision_research_state.json.gz')}`；"
        f"累计历史跟踪候选对 {state_summary.get('tracked_candidate_pairs', 0)}，"
        f"本报告候选对 {state_summary.get('current_candidate_pairs', 0)}，"
        f"历史复现 {state_summary.get('previously_tracked_pairs', 0)}，"
        f"新发现 {state_summary.get('new_candidate_pairs', 0)}。"
    )
    lines.append(
        "台账保留报告引用、证据交易日、来源和碰撞指标；仅供后续研究回看，"
        "不会自动改变字段状态、碰撞锚或主字典。新报告只将 `actionable_L1`、L4 和主动方法候选"
        "写入待研究队列；已登记关系的复验单独展示，历史跟踪记录不会被删除。"
    )
    if state_summary.get("persisted") is False:
        lines.append("_本轮台账没有写入；请查看诊断，已有台账保持原样。_")
    lines.append("")
    return "\n".join(lines) + "\n"


def _l1_row(p):
    return (
        f"| `{p['left']}` | `{p['right']}` | {p['level']} | "
        f"{p['overall_hit']:.2%} | {p['n_days']} | {p['n_pairs']} | "
        f"{p.get('n_informative_pairs') if p.get('n_informative_pairs') is not None else '—'} | "
        f"{p.get('ratio') or '-'} | {'⚠' if p.get('hub_flag') else ''} | "
        f"{'✅' if p.get('in_registry') else '—'} |"
    )


def append_candidate_triage_report(
    markdown: str,
    triage: dict[str, Any],
    frontier: list[dict[str, Any]],
    formulas: list[dict[str, Any]],
    controls: dict[str, Any],
) -> str:
    summary = triage.get("summary", {})
    targets = triage.get("targets", [])
    lines = ["\n## 候选覆盖、公式与下一步采样\n"]
    lines.append(
        "本节用于定位证据缺口和安排后续取样。相关性、公式与样本优先级均为探索候选；"
        "不会改变 L1/L1-U 门槛、来源独立性或主字典。\n"
    )
    lines.append(
        f"- 未知目标 {summary.get('target_count', 0)} 个；其中有方法候选 "
        f"{summary.get('targets_with_method_candidates', 0)} 个、无候选 "
        f"{summary.get('targets_without_method_candidates', 0)} 个；多候选目标 "
        f"{summary.get('targets_with_multiple_candidates', 0)} 个。"
    )
    lines.append(
        f"- 方法候选生成 {summary.get('candidate_pairs_generated', 0)} 条；"
        f"全局详细项保留 {summary.get('global_details_retained', 0)}/"
        f"{summary.get('global_detail_limit', MAX_METHOD_CANDIDATES)}，"
        f"另按目标字段保留 {summary.get('field_frontier_details_retained', 0)} 条；"
        f"完整明细 {summary.get('method_candidate_inventory_count', 0)} 条在 JSON "
        "`method_candidate_inventory`；"
        f"未归档明细 {summary.get('candidate_pairs_without_full_detail', 0)} 条。"
    )
    field_coverage = summary.get("field_coverage", {})
    lines.append(
        f"- 字段覆盖详情：{field_coverage.get('detail_status', 'unavailable')}；"
        f"覆盖身份 {field_coverage.get('coverage_identity_count', 0)}，"
        f"读取 {field_coverage.get('coverage_detail_files', 0)} 份本地索引。"
    )

    status_labels = {
        "formula_candidate_needs_independent_review": "公式候选待独立复核",
        "multiple_method_candidates_need_discrimination": "存在多个候选，需区分",
        "single_method_candidate_needs_external_check": "单候选，需外部证据",
        "source_lineage_gap": "来源血缘缺口",
        "field_coverage_identity_unmapped": "覆盖字段未映射到运行路径",
        "independent_source_coverage_gap": "独立来源覆盖缺口",
        "joint_sample_coverage_gap": "共同样本不足",
        "no_current_method_signal": "当前方法未发现信号",
        "no_eligible_comparison": "无可用独立对比",
    }
    lines.append("\n### 优先处理字段\n")
    lines.append(
        "| 未知字段 | 当前诊断 | 独立对比/候选数 | 独立锚家族/本源日期 | 建议复核股票 | 最强候选线索 |"
    )
    lines.append("|:--|:--|--:|:--|:--|:--|")
    for target in targets[:50]:
        coverage = target.get("coverage", {})
        families = coverage.get("independent_anchor_families", [])
        dates = coverage.get("source_as_of_days", [])
        candidate_names = [
            (
                f"{item.get('right')} "
                f"({','.join(m.get('method', '') for m in item.get('methods', []))})"
            )
            for item in target.get("top_candidates", [])
        ]
        candidate_text = "; ".join(candidate_names) or "—"
        formula_text = "; ".join(
            item.get("formula", "") for item in target.get("formula_candidates", [])
        )
        evidence_text = (candidate_text + ("; " + formula_text if formula_text else ""))[:240]
        sample = target.get("next_sample") or {}
        sample_text = (
            f"{sample.get('stock_code')} ({sample.get('normalized_prediction_spread')})"
            if sample.get("status") == "prioritize_recheck"
            else sample.get("status", "—")
        )
        pair_counts = target.get("pair_counts", {})
        comparisons = (
            f"{pair_counts.get('independent_pairs', 0)} / {target.get('candidate_count', 0)}"
        )
        anchor_text = f"{len(families)} 家族 / {coverage.get('independent_anchor_pairs', 0)} 对"
        coverage_text = (
            f"{anchor_text} / 本源 {len(dates)} 日"
            if coverage.get("status") == "available"
            else f"{anchor_text} / 本源详情不可用"
        )
        label = status_labels.get(target.get("status"), target.get("status", "未知"))
        lines.append(
            f"| `{target.get('left', '')}` | {label} | {comparisons} | "
            f"{coverage_text} | {sample_text} | {evidence_text} |"
        )
    if len(targets) > 50:
        lines.append(f"\n_此表显示优先级最高的 50 / 共 {len(targets)} 个目标；完整清单见 JSON。_\n")

    if frontier:
        lines.append(f"\n### 补足全局截断的字段候选（{len(frontier)}）\n")
        lines.append("| 未知字段 | 候选字段 | 方法 | 样本 | 日期 | 来源 |")
        lines.append("|:--|:--|:--|--:|:--|:--|")
        for candidate in frontier[:100]:
            lines.append(
                f"| `{candidate.get('left')}` | `{candidate.get('right')}` | "
                f"{', '.join(item.get('method', '') for item in candidate.get('methods', []))} | "
                f"{candidate.get('sample_count', 0)} | "
                f"{', '.join(candidate.get('sample_dates', [])[:5])} | "
                f"{', '.join(candidate.get('evidence_sources', []))} |"
            )
        if len(frontier) > 100:
            lines.append(f"\n_仅显示前 100 / 共 {len(frontier)} 条字段前沿候选。_\n")

    if formulas:
        lines.append(f"\n### 双输入公式候选（{len(formulas)}）\n")
        lines.append(
            "公式使用按股票代码分组的留出样本验证；至少 3 个留出股票，验证 R²≥0.985、"
            "误差不超过训练目标标准差的 5%，并要求优于最佳单输入线性模型至少 0.05。"
            "这些阈值只筛选探索候选，不构成语义证明。\n"
        )
        lines.append("| 目标字段 | 候选公式 | 留出 R² | 相对误差尺度 | 验证样本/股票 |")
        lines.append("|:--|:--|--:|--:|--:|")
        for formula in formulas[:50]:
            lines.append(
                f"| `{formula.get('left')}` | `{formula.get('formula')}` | "
                f"{formula.get('validation_r2')} | {formula.get('normalized_rmse')} | "
                f"{formula.get('validation_samples')}/{formula.get('validation_stocks')} |"
            )
        if len(formulas) > 50:
            lines.append(f"\n_仅显示前 50 / 共 {len(formulas)} 条公式候选。_\n")
    else:
        lines.append(
            f"\n### 双输入公式候选\n本轮未发现通过留出筛选的公式候选；"
            f"测试组合 {summary.get('formula_combinations_tested', 0)} 个。\n"
        )

    positive = controls.get("positive_control", {})
    negative = controls.get("negative_control", {})
    lines.append("\n### 已知映射与已证伪关系的候选校准\n")
    lines.append(
        f"- 已登记正向对照：当前窗口有 {positive.get('eligible_numeric_pairs', 0)} 组独立数值关系可评估，"
        f"{positive.get('with_method_signal', 0)} 组被方法候选识别；样本不足 "
        f"{positive.get('insufficient_numeric_samples', 0)} 组。此计数仅检查方法覆盖，不是准确率。"
    )
    lines.append(
        f"- 已证伪负向对照：数值关系 {negative.get('numeric_refuted_pairs', 0)} 组，"
        f"其中仍有方法信号 {negative.get('with_method_signal', 0)} 组；这些信号被隔离，不进入普通候选。"
    )
    failed_sources = []
    for source, status in summary.get("capture_source_statuses", {}).items():
        if status.get("non_ok_dates"):
            failed_sources.append(
                f"{source}: {', '.join(status['non_ok_dates'][-3:])} "
                f"({status.get('status_counts', {})})"
            )
    if failed_sources:
        lines.append("\n### 采集覆盖异常源\n")
        lines.extend(f"- {item}" for item in failed_sources[:30])
        if len(failed_sources) > 30:
            lines.append(
                f"- 另有 {len(failed_sources) - 30} 个来源见 JSON "
                "`candidate_triage.summary.capture_source_statuses`。"
            )
    return markdown.rstrip() + "\n" + "\n".join(lines) + "\n"


def build_report_completeness(report_data: dict[str, Any]) -> dict[str, Any]:
    """Reconcile complete JSON evidence against intentionally summarized Markdown views."""
    triage = report_data.get("candidate_triage")
    triage = triage if isinstance(triage, dict) else {}
    triage_summary = triage.get("summary")
    triage_summary = triage_summary if isinstance(triage_summary, dict) else {}
    targets = triage.get("targets")
    if not isinstance(targets, list):
        targets = []

    section_specs = {
        "L1": (report_data.get("L1"), None, "完整 L1 关系清单"),
        "L1-C": (report_data.get("L1-C"), None, "完整官方契约锚候选清单"),
        "actionable_L1": (report_data.get("actionable_L1"), None, "完整新候选清单"),
        "mapped_pair_revalidations": (
            report_data.get("mapped_pair_revalidations"),
            None,
            "完整已登记映射复验清单",
        ),
        "L4": (report_data.get("L4"), 60, "完整 L4 清单"),
        "source_coverage": (
            report_data.get("source_coverage"),
            None,
            "完整逐来源契约定义、窗口观察与碰撞参与统计",
        ),
        "guardrail_hits": (
            report_data.get("guardrail_hits"),
            None,
            "完整证伪护栏命中清单",
        ),
        "method_candidates": (
            report_data.get("method_candidates"),
            100,
            "全局排序摘要；完整清单见 method_candidate_inventory",
        ),
        "method_candidate_inventory": (
            report_data.get("method_candidate_inventory"),
            0,
            "完整方法候选明细；仅存于 JSON",
        ),
        "method_candidate_frontier": (
            report_data.get("method_candidate_frontier"),
            100,
            "按目标补充的前沿清单；完整清单见 JSON",
        ),
        "candidate_triage.targets": (
            targets,
            50,
            "逐个未知目标的完整诊断清单；完整清单见 JSON",
        ),
        "formula_candidates": (
            report_data.get("formula_candidates"),
            50,
            "完整通过筛选的公式候选；完整清单见 JSON",
        ),
        "diagnostics": (report_data.get("diagnostics"), 100, "完整告警清单"),
    }

    issues = []
    sections = {}
    markdown_omissions = []
    for name, (records, markdown_limit, scope) in section_specs.items():
        if not isinstance(records, list):
            issues.append(f"{name}: missing_or_invalid_json_list")
            records = []
        record_count = len(records)
        visible_count = (
            record_count if markdown_limit is None else min(record_count, markdown_limit)
        )
        omitted_count = record_count - visible_count
        if omitted_count:
            markdown_omissions.append(
                {
                    "section": name,
                    "available": record_count,
                    "visible": visible_count,
                    "omitted_from_markdown": omitted_count,
                }
            )
        sections[name] = {
            "json_record_count": record_count,
            "markdown_display_limit": markdown_limit,
            "markdown_display_count": visible_count,
            "markdown_omitted_count": omitted_count,
            "detail_scope": scope,
        }

    generated_count = report_data.get("method_candidate_count")
    if type(generated_count) is not int or generated_count < 0:
        generated_count = 0
        issues.append("method_candidate_count: missing_or_invalid")
    inventory = report_data.get("method_candidate_inventory")
    if not isinstance(inventory, list):
        inventory = []
    candidate_pairs = []
    invalid_pair_identity_count = 0
    for row in inventory:
        if not isinstance(row, dict):
            invalid_pair_identity_count += 1
            continue
        left, right = row.get("left"), row.get("right")
        if not isinstance(left, str) or not left or not isinstance(right, str) or not right:
            invalid_pair_identity_count += 1
            continue
        candidate_pairs.append((left, right))
    unique_pair_count = len(set(candidate_pairs))
    missing_detail_count = max(0, generated_count - len(inventory))
    excess_detail_count = max(0, len(inventory) - generated_count)
    duplicate_pair_count = len(candidate_pairs) - unique_pair_count

    summary_rows = report_data.get("method_candidates")
    if not isinstance(summary_rows, list):
        summary_rows = []
    summary_pairs = []
    invalid_summary_pair_count = 0
    for row in summary_rows:
        if not isinstance(row, dict):
            invalid_summary_pair_count += 1
            continue
        left, right = row.get("left"), row.get("right")
        if isinstance(left, str) and left and isinstance(right, str) and right:
            summary_pairs.append((left, right))
        else:
            invalid_summary_pair_count += 1
    if invalid_summary_pair_count or summary_pairs != candidate_pairs[: len(summary_pairs)]:
        issues.append("method_candidates: ranked_summary_not_a_prefix_of_full_inventory")

    frontier_rows = report_data.get("method_candidate_frontier")
    if not isinstance(frontier_rows, list):
        frontier_rows = []
    frontier_pairs = []
    invalid_frontier_pair_count = 0
    for row in frontier_rows:
        if not isinstance(row, dict):
            invalid_frontier_pair_count += 1
            continue
        left, right = row.get("left"), row.get("right")
        if isinstance(left, str) and left and isinstance(right, str) and right:
            frontier_pairs.append((left, right))
        else:
            invalid_frontier_pair_count += 1
    inventory_pair_set = set(candidate_pairs)
    summary_pair_set = set(summary_pairs)
    if (
        invalid_frontier_pair_count
        or len({left for left, _ in frontier_pairs}) != len(frontier_pairs)
        or any(
            pair not in inventory_pair_set or pair in summary_pair_set for pair in frontier_pairs
        )
    ):
        issues.append("method_candidate_frontier: pair_identity_mismatch")

    if (
        missing_detail_count
        or excess_detail_count
        or duplicate_pair_count
        or invalid_pair_identity_count
    ):
        issues.append("method_candidate_inventory: count_or_pair_identity_mismatch")

    expected_target_count = triage_summary.get("target_count")
    if type(expected_target_count) is not int or expected_target_count != len(targets):
        issues.append("candidate_triage.targets: count_mismatch")
    target_candidate_count_sum = 0
    invalid_target_candidate_counts = 0
    for target in targets:
        count = target.get("candidate_count") if isinstance(target, dict) else None
        if type(count) is not int or count < 0:
            invalid_target_candidate_counts += 1
        else:
            target_candidate_count_sum += count
    if invalid_target_candidate_counts or target_candidate_count_sum != generated_count:
        issues.append("candidate_triage.targets: candidate_count_mismatch")

    top_level_sections = {}
    for name, value in report_data.items():
        if name == "report_completeness":
            continue
        if name not in sections:
            sections[name] = {
                "json_record_count": len(value) if isinstance(value, (list, dict)) else None,
                "markdown_display_limit": None,
                "markdown_display_count": None,
                "markdown_omitted_count": None,
                "detail_scope": "完整 JSON 顶层内容；需按实际结构逐项审阅",
            }
        top_level_sections[name] = {
            "value_type": type(value).__name__,
            "record_count": len(value) if isinstance(value, (list, dict)) else None,
        }

    return {
        "schema_version": 1,
        "status": "complete" if not issues else "incomplete",
        "markdown_is_summary": True,
        "top_level_sections": top_level_sections,
        "method_candidate_inventory": {
            "generated_count": generated_count,
            "saved_count": len(inventory),
            "unique_pair_count": unique_pair_count,
            "missing_detail_count": missing_detail_count,
            "excess_detail_count": excess_detail_count,
            "duplicate_pair_count": duplicate_pair_count,
            "invalid_pair_identity_count": invalid_pair_identity_count,
            "target_candidate_count_sum": target_candidate_count_sum,
            "invalid_target_candidate_count_rows": invalid_target_candidate_counts,
            "json_key": "method_candidate_inventory",
        },
        "sections": sections,
        "markdown_omissions": markdown_omissions,
        "issues": issues,
    }


def append_report_completeness_report(markdown: str, completeness: dict[str, Any]) -> str:
    """Expose truncation and completeness checks at the end of the human-readable report."""
    inventory = completeness.get("method_candidate_inventory", {})
    lines = ["\n## 报告完整性与审阅范围\n"]
    lines.append(
        f"- 机器可读完整性：`{completeness.get('status', 'incomplete')}`；"
        f"方法候选生成 {inventory.get('generated_count', 0)} 条，"
        f"完整明细保存 {inventory.get('saved_count', 0)} 条，"
        f"缺失 {inventory.get('missing_detail_count', 0)} 条，"
        f"多余 {inventory.get('excess_detail_count', 0)} 条，"
        f"重复 {inventory.get('duplicate_pair_count', 0)} 条，"
        f"身份无效 {inventory.get('invalid_pair_identity_count', 0)} 条。"
    )
    lines.append(
        "- 全量方法候选位于同名 JSON 的 `method_candidate_inventory`；"
        "Markdown 的 Top-N 表格是导航摘要，不能代替全量 JSON 审阅。"
    )
    omissions = completeness.get("markdown_omissions", [])
    if omissions:
        lines.append("- Markdown 未逐行展示、但 JSON 保留的部分：")
        lines.extend(
            f"  - `{item.get('section')}`：展示 {item.get('visible', 0)} / "
            f"{item.get('available', 0)}，摘要省略 {item.get('omitted_from_markdown', 0)} 条。"
            for item in omissions
        )
    issues = completeness.get("issues", [])
    if issues:
        lines.append("- **审阅阻断**：完整性对账失败；不得据此断言无候选、无字段或提交定案。")
        lines.extend(f"  - `{issue}`" for issue in issues)
    else:
        lines.append(
            "- 完整性对账通过；逐目标复核仍须覆盖 JSON 的全部明细，并为每项记录"
            "已检查、重复归并、证据不足或需外部核验的处置。"
        )
    return markdown.rstrip() + "\n" + "\n".join(lines) + "\n"


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
    # Keep already-registered pairs visible for revalidation, outside the new-candidate queue.
    revalidations = [p for p in l1 if p.get("in_registry", False)]
    actionable = [p for p in l1 if not p.get("in_registry", False)]
    cross = [p for p in actionable if not p.get("same_code")]
    same = [p for p in actionable if p.get("same_code")]
    cross.sort(key=lambda p: (-p["overall_hit"], -p["n_days"]))
    same.sort(key=lambda p: (-p["overall_hit"], -p["n_days"]))
    revalidations.sort(key=lambda p: (-p["overall_hit"], -p["n_days"]))

    L = []
    L.append(f"# 全源对撞报告（{today}）\n")
    if window_selection:
        if window_selection.get("mode") == "all_history":
            L.append("> 交易数据窗口配置：全部历史日期（`--all`）")
        else:
            requested_days = window_selection.get("requested_trading_days")
            L.append(f"> 交易数据窗口配置：近 {requested_days} 个交易日（`--window`）")
    trading_window = f"{window[0]} ~ {window[-1]}" if window else "无有效交易日样本"
    L.append(
        f"> 行情窗口：{trading_window}（{len(window)} 个不同交易日）｜"
        f"字段 {nfields} 个｜样本值 {nsamples} 条"
    )
    if event_window:
        L.append(f"> 新闻/公告自然日窗口：{event_window[0]:%Y%m%d} ~ {event_window[1]:%Y%m%d}")
    L.append(
        f"> 主攻目标（unverified）={len(left_ids)}｜可审定新候选={len(actionable)}｜"
        f"首次发现新候选对={new_count}｜已登记关系复验={len(revalidations)}｜"
        f"异号同义 {len(cross)} / 同号镜像 {len(same)}\n"
    )
    L.append(
        f"> **规则**：L1 每日需≥{MIN_DAILY_L1} 组有效配对，并至少有"
        f"{MIN_INFORMATIVE_DAILY_L1} 组信息配对；双方同时为 0 或同时缺失不计命中率，"
        f"一侧为 0、另一侧非 0 按失配计。信息配对命中率≥{HIT_RATE_L1_RATIO:.0%}，"
        f"且覆盖至少 {MULTI_DAY_MIN} 个独立交易日/自然事件日；同一来源族不作为跨源证据；"
        "盘中快照不计入 L1。JSON `daily_sample_counts` 与 `daily_informative_sample_counts`"
        "分别保留每日有效配对数和 L1 信息配对数。"
        "（详见 `COLLISION_RULES.md`）。本引擎只发现、不写字典；"
        "新定案经 field_dict.md 订正后由 sanctioned 管线 ingest。\n"
    )
    L.append("---\n")
    L.append(f"## 一、L1 / L1-U 新候选 — 异号同义（跨编号，高价值）({len(cross)})\n")
    if cross:
        L.append(
            "| 左字段(unverified) | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |"
        )
        L.append("|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|")
        for p in cross:
            L.append(_l1_row(p))
    else:
        L.append("_本轮无异号同义候选。_\n")
    L.append(f"\n## 二、L1 / L1-U 新候选 — 同号镜像（同编号，低优先级）({len(same)})\n")
    if same:
        L.append(
            "| 左字段 | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |"
        )
        L.append("|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|")
        for p in same:
            L.append(_l1_row(p))
    else:
        L.append("_本轮无同号镜像候选。_\n")
    L.append(f"\n## 三、已登记映射的本窗口复验（{len(revalidations)}）\n")
    L.append(
        "_这些关系已在主注册表登记，只用于观察当前样本是否仍支持既有映射；"
        "它们不是新的未知字段候选，也不能再次提交为新定案。_\n"
    )
    if revalidations:
        L.append(
            "| 左字段 | 右字段 | 等级 | 命中率 | 天数 | 样本 | 信息样本 | 比值 | hub | registry |"
        )
        L.append("|:--|:--|:--|--:|--:|--:|--:|--:|:--|:--|")
        for pair in revalidations:
            L.append(_l1_row(pair))
    else:
        L.append("_本轮没有已登记关系进入复验窗口。_\n")
    L.append("\n## 四、L4 存疑候选（{0}）\n".format(len(l4)))
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
    L.append("\n## 五、已证伪护栏命中（被拦截的伪结论候选）（{0}）\n".format(len(guardrail_hits)))
    if guardrail_hits:
        L.append("| 左字段 | 右字段 | 命中护栏ID | 伪主张 |")
        L.append("|:--|:--|:--|:--|")
        for h in guardrail_hits:
            L.append(f"| `{h['left']}` | `{h['right']}` | {h['id']} | {h['false_claim']} |")
        L.append("\n_以上候选因命中 REFUTED_CONCLUSIONS（数值实证推翻）已被自动判伪，未进入 L1。_")
    else:
        L.append("_本轮无护栏命中（未产出与已证伪结论冲突的候选）。_\n")
    method_candidates = method_candidates or []
    L.append(f"\n## 六、主动方法候选（不直接定案）（{len(method_candidates)}）\n")
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
    L.append(f"\n## 七、日期与数据质量告警（{len(diagnostics)}）\n")
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

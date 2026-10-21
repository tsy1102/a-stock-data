from __future__ import annotations

import hashlib
import json
import math
import re
from collections import defaultdict
from datetime import date

from scripts.collision_dates import (
    CALENDAR,
    TRADING,
    event_record_date,
    is_calendar_event_source,
    parse_date,
    sample_date_key,
)
from scripts.context_policy import CONTEXT_ONLY_SOURCES, CONTEXT_RECORD_PATHS


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

from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, List, Optional

from scripts.capture_catalog import NON_RAW_SOURCE_STATUS
from scripts.capture_diagnostics import (
    _assess_zhb_freshness,
    _source_expected_codes,
    _source_required_paths,
    assess_result,
)
from scripts.context_policy import CONTEXT_ONLY_SOURCES, CONTEXT_RECORD_PATHS as CONTEXT_RAW_PATHS


def _retain_current_zhb_snapshot(
    data: Any, path: str, target_date: str
) -> tuple[Any, bool, Optional[Dict[str, Any]]]:
    """Prevent a non-current or older refresh from replacing an existing ZHB snapshot."""
    attempted_freshness = _assess_zhb_freshness(data, target_date)
    if attempted_freshness["status"] == "current" or not os.path.exists(path):
        return data, True, None

    try:
        with open(path, "r", encoding="utf-8") as f:
            existing = json.load(f)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return (
            data,
            False,
            {
                "status": "existing_snapshot_unreadable",
                "attempted_freshness": attempted_freshness,
                "reason": (
                    f"现有 ZHB 快照无法安全比较，已保留原文件: "
                    f"{type(exc).__name__}: {str(exc)[:120]}"
                ),
            },
        )

    if not isinstance(existing, dict):
        return (
            data,
            False,
            {
                "status": "existing_snapshot_unreadable",
                "attempted_freshness": attempted_freshness,
                "reason": "现有 ZHB 快照不是对象，已保留原文件",
            },
        )

    existing_freshness = _assess_zhb_freshness(existing, target_date)
    if existing_freshness["status"] == "current":
        return (
            existing,
            False,
            {
                "status": "noncurrent_refresh_rejected",
                "attempted_freshness": attempted_freshness,
                "retained_as_of_date": existing_freshness["actual_as_of_date"],
                "reason": attempted_freshness["reason"],
            },
        )
    if attempted_freshness["status"] in {"unknown", "unverified", "future"}:
        refresh_status = (
            "future_refresh_rejected"
            if attempted_freshness["status"] == "future"
            else "freshness_unverified"
        )
        return (
            existing,
            False,
            {
                "status": refresh_status,
                "attempted_freshness": attempted_freshness,
                "retained_as_of_date": existing_freshness["actual_as_of_date"],
                "reason": (f"{attempted_freshness['reason']}；为避免覆盖现有证据，已保留原文件"),
            },
        )
    if existing_freshness["status"] in {"unknown", "unverified"}:
        return (
            existing,
            False,
            {
                "status": "existing_freshness_unverified",
                "attempted_freshness": attempted_freshness,
                "retained_as_of_date": existing_freshness["actual_as_of_date"],
                "reason": (f"{existing_freshness['reason']}；为避免覆盖现有证据，已保留原文件"),
            },
        )
    if (
        existing_freshness["status"] == "stale"
        and existing_freshness["actual_as_of_date"]
        and attempted_freshness["actual_as_of_date"]
        and existing_freshness["actual_as_of_date"] > attempted_freshness["actual_as_of_date"]
    ):
        return (
            existing,
            False,
            {
                "status": "older_refresh_rejected",
                "attempted_freshness": attempted_freshness,
                "retained_as_of_date": existing_freshness["actual_as_of_date"],
                "reason": (
                    f"重采数据日 {attempted_freshness['actual_as_of_date']} "
                    f"早于现有数据日 {existing_freshness['actual_as_of_date']}，已保留原文件"
                ),
            },
        )
    return data, True, None


def _preserve_context_paths(
    source: str, data: Dict[str, Any], out_dir: str
) -> tuple[List[str], List[str]]:
    """Carry forward opt-in context subtrees when refreshing a default snapshot."""
    paths: List[tuple] = list(CONTEXT_RAW_PATHS.get(source, ()))
    raw_path = os.path.join(out_dir, f"raw_{source}.json")
    if not paths or not os.path.isfile(raw_path):
        return [], []
    try:
        with open(raw_path, encoding="utf-8") as stream:
            previous = json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"{source}: cannot preserve prior context from {raw_path}: {exc}"]
    if not isinstance(previous, dict):
        return [], [f"{source}: cannot preserve prior context; previous raw root is not an object"]

    preserved: List[str] = []
    warnings: List[str] = []
    for path in paths:
        old_node: Any = previous
        new_node: Any = data
        found = True
        for part in path[:-1]:
            if not isinstance(old_node, dict) or not isinstance(old_node.get(part), dict):
                found = False
                break
            old_node = old_node[part]
            if not isinstance(new_node, dict):
                found = False
                break
            if not isinstance(new_node.get(part), dict):
                new_node[part] = {}
            new_node = new_node[part]
        if not found or not isinstance(old_node, dict) or path[-1] not in old_node:
            continue
        if not isinstance(new_node, dict):
            warnings.append(f"{source}: cannot preserve context path {'.'.join(path)}")
            continue
        if path[-1] not in new_node:
            new_node[path[-1]] = old_node[path[-1]]
            preserved.append(".".join(path))
    return preserved, warnings


def _has_complete_snapshot(
    collectors: Dict[str, Callable[..., Dict[str, Any]]],
    meta: dict,
    out_dir: str,
    pool: List[Dict[str, Any]],
    include_context: bool = False,
) -> bool:
    """Only skip when each requested producer has a complete, assessable snapshot."""
    source_meta = meta.get("sources") if isinstance(meta.get("sources"), dict) else {}
    for source in collectors:
        if source in CONTEXT_ONLY_SOURCES and not include_context:
            continue
        entry = source_meta.get(source) if isinstance(source_meta, dict) else None
        if not isinstance(entry, dict):
            return False
        status = entry.get("status")
        expected_non_raw_status = NON_RAW_SOURCE_STATUS.get(source)
        if expected_non_raw_status:
            if status != expected_non_raw_status:
                return False
            continue
        if status in {"unwired", "deprecated"}:
            continue
        if entry.get("ok") is not True or status not in (None, "ok"):
            return False
        raw_path = os.path.join(out_dir, f"raw_{source}.json")
        if not os.path.isfile(raw_path):
            return False
        try:
            with open(raw_path, encoding="utf-8") as stream:
                document = json.load(stream)
        except (OSError, json.JSONDecodeError):
            return False
        ok, _ = assess_result(
            document,
            expected_symbols=_source_expected_codes(source, pool),
            required_paths=_source_required_paths(source, include_context),
        )
        if not ok:
            return False
    return True


def _refresh_closed_snapshot_validations(
    *,
    out_dir: str,
    data_date: str,
    pool: List[Dict[str, Any]],
    snapshot_meta: Dict[str, Any],
    latest_trading_day_str,
) -> None:
    """Refresh daily evidence from a complete snapshot without recapturing sources."""
    market_path = os.path.join(out_dir, "raw_market_sources.json")
    market_data: Optional[Dict[str, Any]] = None
    try:
        with open(market_path, encoding="utf-8") as stream:
            loaded_market_data = json.load(stream)
        if isinstance(loaded_market_data, dict):
            market_data = loaded_market_data
    except (OSError, json.JSONDecodeError) as exc:
        print(f"  ⚠ 已有市场源 raw 不可读取，跳过 Levistock 候选请求: {exc}", flush=True)

    try:
        try:
            from axdata_daily_validation import run_axdata_daily_validation
        except ModuleNotFoundError:
            from scripts.axdata_daily_validation import run_axdata_daily_validation

        snapshot_meta["axdata_validation"] = run_axdata_daily_validation(
            data_date=data_date,
            data_date_domain=snapshot_meta.get("data_date_domain", "trading"),
            market_phase=snapshot_meta.get("market_phase", "unknown"),
            latest_completed_trade_date=latest_trading_day_str(),
            only="",
            out_dir=out_dir,
            pool=pool,
            source_meta=snapshot_meta.get("sources", {}),
        )
    except Exception as exc:
        snapshot_meta["axdata_validation"] = {
            "status": "failed_open",
            "error": str(exc)[:300],
            "request_count": 0,
        }
        print(f"  ⚠ AxData 每日验证刷新失败: {exc}", flush=True)

    if market_data is not None:
        try:
            try:
                from levistock_daily_probe import run_levistock_daily_probe
            except ModuleNotFoundError:
                from scripts.levistock_daily_probe import run_levistock_daily_probe

            probe = run_levistock_daily_probe(
                out_dir=out_dir,
                data_date=data_date,
                latest_completed_trade_date=latest_trading_day_str(),
                # This is a trading-date market source even when the full meta is mixed
                # with natural-day news/announcement sources.
                data_date_domain="trading",
                market_phase=snapshot_meta.get("market_phase", "unknown"),
                only=None,
                market_data=market_data,
                pool=pool,
            )
            snapshot_meta["levistock_daily_candidate"] = {
                key: value for key, value in probe.items() if key != "payload"
            }
        except Exception as exc:
            snapshot_meta["levistock_daily_candidate"] = {
                "status": "failed_open",
                "reason": f"probe_integration_error:{type(exc).__name__}",
                "request_count": 0,
            }
            print(f"  ⚠ Levistock 每日候选刷新失败: {exc}", flush=True)

    try:
        try:
            from levistock_daily_validation import run_levistock_daily_validation
        except ModuleNotFoundError:
            from scripts.levistock_daily_validation import run_levistock_daily_validation

        snapshot_meta["levistock_validation"] = run_levistock_daily_validation(
            out_dir=out_dir,
            data_date=data_date,
            latest_completed_trade_date=latest_trading_day_str(),
            data_date_domain="trading",
            market_phase=snapshot_meta.get("market_phase", "unknown"),
            only=None,
            source_meta=snapshot_meta.get("sources", {}),
            candidate_probe_meta=snapshot_meta.get("levistock_daily_candidate"),
        )
    except Exception as exc:
        snapshot_meta["levistock_validation"] = {
            "status": "failed_open",
            "error": str(exc)[:300],
            "network_requests_added": 0,
        }
        print(f"  ⚠ Levistock 离线验证刷新失败: {exc}", flush=True)

    try:
        with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as stream:
            json.dump(snapshot_meta, stream, ensure_ascii=False, indent=1)
    except OSError as exc:
        print(f"  ⚠ 每日验证摘要未能更新到 meta.json: {exc}", flush=True)


def _refresh_field_evidence_coverage(out_dir: str, snapshot_meta: dict, *, out_base: str) -> None:
    """Refresh local unresolved-field coverage from archived raw snapshots only."""
    try:
        try:
            from field_evidence_coverage import refresh_daily_coverage
        except ModuleNotFoundError:
            from scripts.field_evidence_coverage import refresh_daily_coverage

        coverage = refresh_daily_coverage(out_dir, snapshot_meta, data_dir=out_base)
        snapshot_meta["field_evidence_coverage"] = coverage
        print(
            "  字段证据覆盖: "
            f"目标 {coverage.get('pending_source_fields', 0)} | "
            f"有样本 {coverage.get('targets_observed', 0)} | "
            f"精确来源日期覆盖≥3日 {coverage.get('targets_with_3_source_as_of_days', 0)} | "
            f"文件 {coverage.get('file', coverage.get('status', 'unavailable'))}",
            flush=True,
        )
    except Exception as exc:
        snapshot_meta["field_evidence_coverage"] = {
            "status": "failed_open",
            "reason": f"{type(exc).__name__}: {exc}"[:300],
        }
        print(f"  ⚠ 字段证据覆盖刷新失败，不影响已采集 raw: {exc}", flush=True)

    try:
        with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as stream:
            json.dump(snapshot_meta, stream, ensure_ascii=False, indent=1)
    except OSError as exc:
        print(f"  ⚠ 字段证据覆盖摘要未能更新到 meta.json: {exc}", flush=True)

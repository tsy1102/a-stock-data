"""Collectors for project-specific verified source families.

This module captures AxData, Fuyao, FTShare REST, and KPH/KPL evidence. The
entry point passes its patchable policy/date helpers through a frozen dependency
record; source adapters and their network state remain owned by ``stock_common``.
"""

from dataclasses import dataclass
from datetime import datetime, time as dt_time
from typing import Any, Callable, Dict, List, Optional


@dataclass(frozen=True)
class CaptureSourceDependencies:
    identity_capture_block_reason: Callable[..., Any]
    attach_identity_validation_suppression: Callable[..., Any]
    request_is_rate_limited: Callable[..., Any]
    defer_axdata_codes: Callable[..., Any]
    capture_source_fields: Callable[..., Any]
    kpl_timestamp_date: Callable[..., Any]
    parse_capture_date: Callable[..., Any]
    six_digit_symbol: Callable[..., Any]
    kph_history_trade_date: Callable[..., Any]
    kph_ladder_blocks_followup: Callable[..., Any]
    fuyao_auction_items: Callable[..., Any]
    fuyao_auction_snapshot_meta: Callable[..., Any]
    last_completed_trading_day: Callable[..., Any]


__all__ = [
    "CaptureSourceDependencies",
    "collect_axdata",
    "collect_kpl_detail",
    "collect_kph_history",
    "collect_fuyao",
    "collect_ftshare",
    "collect_ftshare_rest",
]


def collect_axdata(
    pool: list, deps: CaptureSourceDependencies, identity_policy: Optional[dict] = None
) -> dict:
    """采集 AxData 的 TDX 短线接口；ZHB 统计文件本地读取，接口仍可能访问网络。"""
    policy = identity_policy if isinstance(identity_policy, dict) else {}
    block_reason = deps.identity_capture_block_reason(policy)
    if block_reason:
        reason = str(policy.get("reason") or "endpoint_redundant")
        identity = policy.get("identity")
        identity = identity if isinstance(identity, dict) else {}
        interface_id = identity.get("interface_id")
        return {
            "stocks": {item["code"]: {"__skipped__": reason} for item in pool},
            "__source_meta__": {
                "capture_block": {
                    "status": identity.get("status"),
                    "interface_id": interface_id,
                    "reference_source": policy.get("reference_source"),
                    "reason": reason,
                    "evidence_dates": identity.get("evidence_dates", []),
                    "capture_performed": False,
                }
            },
        }
    from stock_common import get_shortline_indicators_result

    out: Dict[str, Any] = {"stocks": {}}
    deps.attach_identity_validation_suppression(out, identity_policy)
    for index, p in enumerate(pool):
        c = p["code"]
        try:
            result = get_shortline_indicators_result(c)
            if result.get("status") != "ok":
                error = result.get("error") or (
                    "request_error: AxData stock_shortline_indicators_tdx (TDX) "
                    f"failed with status {result.get('status', 'unknown')}"
                )
                out["stocks"][c] = {"__error__": str(error)[:200]}
                detail = {
                    "kind": result.get("kind") or result.get("status"),
                    "status_code": result.get("status_code") or result.get("http_status"),
                    "message": str(error),
                }
                if deps.request_is_rate_limited(detail):
                    deps.defer_axdata_codes(out, pool, index + 1, c)
                    break
                continue

            rec = result.get("data")
            if not isinstance(rec, dict) or not rec:
                out["stocks"][c] = {
                    "__error__": (
                        "no_records: AxData stock_shortline_indicators_tdx "
                        "(TDX) returned no usable records"
                    )
                }
            else:
                out["stocks"][c] = {"n_fields": len(rec), "data": rec}
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
            if deps.request_is_rate_limited({"kind": type(e).__name__, "message": str(e)}):
                deps.defer_axdata_codes(out, pool, index + 1, c)
                break
    return out


def collect_kpl_detail(capture_date: Any, deps: CaptureSourceDependencies) -> dict:
    """Collect all five KPL limit-up ladders with source and date provenance."""
    import stock_common

    rows = []
    warnings = []
    pid_type_counts = {}
    for pid_type in range(1, 6):
        try:
            ladder_rows = stock_common.get_kpl_limit_up_detail(pid_type=pid_type, capture_raw=True)
        except Exception as exc:
            warnings.append(f"PidType={pid_type} request failed: {str(exc)[:160]}")
            continue
        if ladder_rows is None or not isinstance(ladder_rows, list):
            warnings.append(f"PidType={pid_type} returned an invalid response")
            continue
        if len(ladder_rows) == 1 and isinstance(ladder_rows[0], dict):
            error = ladder_rows[0].get("__error__")
            if error:
                warnings.append(f"PidType={pid_type} request failed: {str(error)[:160]}")
                continue
        pid_type_counts[str(pid_type)] = len(ladder_rows)
        for row in ladder_rows:
            if isinstance(row, dict):
                row.setdefault("pid_type", pid_type)
                rows.append(row)
    if not rows:
        return {
            "stocks": {},
            "capture_date": deps.parse_capture_date(capture_date).isoformat(),
            "pid_type_counts": pid_type_counts,
            "warnings": warnings,
            "__error__": "KPL detail returned no rows across PidType=1..5",
        }

    dated_rows = []
    trade_dates = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        row_date = deps.kpl_timestamp_date(row.get("zt_time"))
        if row_date is not None:
            trade_dates.add(row_date)
            dated_rows.append((row, row_date))
    if len(trade_dates) != 1:
        return {
            "stocks": {},
            "capture_date": deps.parse_capture_date(capture_date).isoformat(),
            "__error__": (
                "KPL detail must contain exactly one date derived from zt_time; "
                f"observed {sorted(day.isoformat() for day in trade_dates)}"
            ),
        }

    trade_date = next(iter(trade_dates))
    stocks: Dict[str, Any] = {}
    duplicate_rows = []
    missing_date_rows = len(rows) - len(dated_rows)
    if missing_date_rows:
        warnings.append(f"excluded {missing_date_rows} KPL rows without a valid zt_time")
    for row, row_date in dated_rows:
        if row_date != trade_date:
            continue
        symbol = deps.six_digit_symbol(row)
        if symbol is None:
            warnings.append("excluded a KPL row without a six-digit stock code")
            continue
        captured_fields = deps.capture_source_fields(row)
        if symbol in stocks:
            warnings.append(f"duplicate KPL stock code {symbol}; preserved first row")
            duplicate_rows.append({"symbol": symbol, "fields": captured_fields})
            continue
        stocks[symbol] = captured_fields

    return {
        "trade_date": trade_date.isoformat(),
        "capture_date": deps.parse_capture_date(capture_date).isoformat(),
        "stocks": stocks,
        "row_count": len(stocks),
        "raw_row_count": len(dated_rows),
        "duplicate_row_count": len(duplicate_rows),
        "duplicate_rows": duplicate_rows,
        "pid_type_counts": pid_type_counts,
        "warnings": warnings,
    }


def collect_kph_history(
    capture_date: Any,
    deps: CaptureSourceDependencies,
    prior_market_sources: Any = None,
    identity_policy: Optional[dict] = None,
) -> dict:
    """Request one AxData KPH historical batch; never retry or persist it."""
    try:
        trade_date = deps.kph_history_trade_date(capture_date)
    except Exception as exc:
        return {"stocks": {}, "__error__": f"KPH date selection failed: {str(exc)[:240]}"}

    policy = identity_policy if isinstance(identity_policy, dict) else {}
    block_reason = deps.identity_capture_block_reason(policy)
    if block_reason:
        reason = str(policy.get("reason") or "endpoint_redundant")
        identity = policy.get("identity")
        identity = identity if isinstance(identity, dict) else {}
        return {
            "trade_date": trade_date.isoformat(),
            "requested_trade_date": trade_date.isoformat(),
            "stocks": {},
            "__skipped__": reason,
            "__source_meta__": {
                "capture_block": {
                    "status": identity.get("status"),
                    "interface_id": identity.get("interface_id"),
                    "reference_source": policy.get("reference_source"),
                    "reason": reason,
                    "evidence_dates": identity.get("evidence_dates", []),
                    "capture_performed": False,
                }
            },
        }

    if deps.kph_ladder_blocks_followup(prior_market_sources):
        return {
            "trade_date": trade_date.isoformat(),
            "stocks": {},
            "__skipped__": (
                "KPH history skipped because the same-run Levistock sample was "
                "empty, failed, or throttled"
            ),
        }

    try:
        from stock_common.sc_datasource import get_axdata_records

        records = get_axdata_records(
            "kph_limit_up_history",
            params={"trade_date": trade_date.isoformat()},
        )
    except Exception as exc:
        return {
            "trade_date": trade_date.isoformat(),
            "stocks": {},
            "__error__": f"KPH history request failed: {type(exc).__name__}: {str(exc)[:240]}",
        }
    if not records:
        return {
            "trade_date": trade_date.isoformat(),
            "stocks": {},
            "__error__": f"KPH history returned no records for {trade_date.isoformat()}",
        }

    stocks: Dict[str, Any] = {}
    identity_observations: List[str] = []
    warnings = []
    response_dates = set()
    for row in records:
        raw_date = row.get("trade_date")
        if raw_date is not None:
            try:
                response_dates.add(deps.parse_capture_date(str(raw_date)).isoformat())
            except ValueError:
                warnings.append(f"unparseable KPH row trade_date: {raw_date!r}")
        symbol = deps.six_digit_symbol(row)
        if symbol is None:
            warnings.append("excluded KPH row without a six-digit stock code")
            continue
        if row.get("exchange") is not None and symbol.startswith("92"):
            exchange = str(row.get("exchange")).strip().upper()
            instrument_id = str(row.get("instrument_id") or "")
            if exchange in {"SSE", "SH", "SHSE", "SHANGHAI"} or instrument_id.upper().endswith(
                ".SH"
            ):
                identity_observations.append(
                    f"{symbol}: reported_exchange={row.get('exchange')}; "
                    f"reported_instrument_id={row.get('instrument_id')}"
                )
                warnings.append(
                    f"KPH reports Beijing code {symbol} as Shanghai; raw identity preserved separately"
                )
        # Keep every JSON-safe source field, including text, flags, and arrays.
        # Identity/date metadata remains available under __identity__ but is not
        # exposed as a candidate metric by the collision flattener.
        captured_fields = deps.capture_source_fields(row)
        if symbol in stocks:
            warnings.append(f"duplicate KPH stock code {symbol}; preserved first row")
            continue
        stocks[symbol] = captured_fields

    if response_dates and response_dates != {trade_date.isoformat()}:
        return {
            "trade_date": trade_date.isoformat(),
            "stocks": {},
            "__error__": (
                f"KPH response trade dates {sorted(response_dates)} do not match "
                f"requested {trade_date.isoformat()}"
            ),
            "warnings": warnings,
        }
    if not stocks:
        return {
            "trade_date": trade_date.isoformat(),
            "stocks": {},
            "__error__": f"KPH response had no usable stock records for {trade_date.isoformat()}",
            "warnings": warnings,
            "identity_observations": identity_observations,
        }

    output = {
        "trade_date": trade_date.isoformat(),
        "requested_trade_date": trade_date.isoformat(),
        "capture_date": deps.parse_capture_date(capture_date).isoformat(),
        "stocks": stocks,
        "row_count": len(stocks),
        "warnings": warnings,
    }
    deps.attach_identity_validation_suppression(output, identity_policy)
    if identity_observations:
        output["identity_observations"] = identity_observations
    if trade_date != deps.parse_capture_date(capture_date):
        output["date_selection_note"] = (
            "AxData KPH history requires a date before the natural current day; "
            "the source trade date is recorded explicitly."
        )
    return output


def collect_fuyao(
    pool: list, deps: CaptureSourceDependencies, include_context: bool = False
) -> dict:
    """fuyao 官方 REST 全景采集（V17.0.5 新源——字典 §12.8.12c，全量契约见 verify/fuyao_api_full.md）。

    个股级: 行情快照 / 估值(ps_ttm·pcf_ttm 新维度) / 集合竞价终态 /
            五类财务指标(ROE·扣非ROE·ROA 官方口径——tx65/tx66 对撞终判源)
    市场级: 短线风向标基准 / 涨跌停炸板池(date_ms 任意交易日回查) / 异动原因
    龙虎榜与热股榜仅在 include_context=True 时请求。
    无 Key 时自动禁用(meta 标记 no_key)；~35 请求 @2rps(sc_network 域限流)。
    """
    from stock_common import (
        get_fuyao_snapshot,
        get_fuyao_valuation,
        get_fuyao_fin_indicators,
        get_fuyao_auction_snapshot_envelope,
        get_fuyao_auction_benchmark,
        get_fuyao_limit_pool,
        get_fuyao_anomaly,
        is_fuyao_enabled,
    )

    out: dict = {"stocks": {}, "market": {}}
    if not is_fuyao_enabled():
        out["error"] = "no_key_disabled"
        return out
    codes = [p["code"] for p in pool]
    td = deps.last_completed_trading_day()
    date_ms = int(datetime.combine(td, dt_time()).timestamp() * 1000)
    out["probe_trading_day"] = td.isoformat()
    out["date_ms"] = date_ms

    snap = {r.get("ticker"): r for r in (get_fuyao_snapshot(codes) or [])}
    val = {r.get("ticker"): r for r in (get_fuyao_valuation(codes) or [])}
    auction_envelope = get_fuyao_auction_snapshot_envelope(codes, stage="final")
    auction_items = deps.fuyao_auction_items(auction_envelope)
    auction_meta = deps.fuyao_auction_snapshot_meta(auction_envelope, "final", td)
    auction_meta["item_count"] = len(auction_items)
    out["auction_snapshot_meta"] = auction_meta
    auction = {}
    for item in auction_items:
        enriched_item = dict(item)
        enriched_item["__source_meta__"] = dict(auction_meta)
        auction[item.get("ticker")] = enriched_item
    # V17.0.24: 三大报表(近 8 期 quarterly + 年报 annual)——财务 TTM 族主源原始锚:
    # f163 静态PE=现价÷f160(年报EPS) 闭环验证 + ocf_ttm/revenue_ttm TTM 重建(R_YTD+FY−H1)
    finrep: Dict[str, Any] = {}
    try:
        from stock_common.sc_fuyao import get_fuyao_financials as _gff

        for p in pool:
            c = p["code"]
            finrep[c] = {
                "income_q": _gff("income", c, limit=8, period="quarterly") or [],
                "balance_q": _gff("balance", c, limit=8, period="quarterly") or [],
                "cashflow_q": _gff("cashflow", c, limit=8, period="quarterly") or [],
                "income_a": _gff("income", c, limit=3, period="annual") or [],
            }
    except Exception as _e:
        finrep["__error__"] = str(_e)[:200]
    for p in pool:
        c = p["code"]
        ind = None
        used_report = None
        for rpt in (
            deps.last_completed_trading_day().strftime("%Y") + "-2",
            deps.last_completed_trading_day().strftime("%Y") + "-1",
        ):
            ind = get_fuyao_fin_indicators(c, rpt)
            if ind:
                used_report = rpt
                break
        out["stocks"][c] = {
            "snapshot": snap.get(c),
            "valuation": val.get(c),
            "auction_final": auction.get(c),
            "fin_indicators": ind,
            "fin_report": used_report,
            # V17.0.24: 三大报表原始数据(TTM 重建/静态PE 闭环锚)
            "financials": finrep.get(c) if isinstance(finrep.get(c), dict) else None,
        }

    mkt = out["market"]
    bench = get_fuyao_auction_benchmark(td.isoformat())
    mkt["short_term_benchmark"] = bench[:80] if isinstance(bench, list) else bench

    # ── 中报(yyyy-2)就绪自动探测——tx[65]=扣非加权ROE(TTM) 的 L1 终判数据源 ──
    # 哨兵: 首只股探 2026-2；上游入库滞后(披露日≠入库日, code=5003)时跳过全量拉取省配额
    year = td.strftime("%Y")
    sentinel = get_fuyao_fin_indicators(codes[0], year + "-2")
    mkt["h1_indicators_ready"] = bool(sentinel)
    mkt["h1_indicators"] = {}
    if sentinel:
        for c in codes:
            ind = get_fuyao_fin_indicators(c, year + "-2") or {}
            p = ind.get("profitability") or {}
            if p:
                mkt["h1_indicators"][c] = {
                    "ded_weighted_roe": p.get("index_deduct_weighted_avg_roe"),
                    "weighted_roe": p.get("index_weighted_avg_roe"),
                    "roa": p.get("total_assets_net_ratio"),
                }
        print(f"  ⭐ 中报指标已入库({len(mkt['h1_indicators'])} 只)——tx65/tx66 L1 终判条件达成")

    for kind in ("up", "down", "break"):
        pd_ = get_fuyao_limit_pool(kind, page=1, size=200, date_ms=date_ms)
        items = (pd_ or {}).get("item") or []
        mkt[f"limit_{kind}_pool"] = {
            "total": ((pd_ or {}).get("pagination") or {}).get("total"),
            "count_captured": len(items),
            "item": items,
        }
    mkt["anomaly_list"] = (get_fuyao_anomaly() or [])[:60]
    if include_context:
        from stock_common import get_fuyao_dragon_tiger, get_fuyao_hot_list

        mkt["dragon_tiger"] = (get_fuyao_dragon_tiger(td.isoformat()) or [])[:60]
        mkt["hot_list_hour"] = (get_fuyao_hot_list("hour") or [])[:50]
    return out


def collect_ftshare(pool: list, *, data_date: str = "", force_reprobe: bool = False) -> dict:
    """Keep legacy private-MCP captures visible without making requests."""
    del pool, data_date, force_reprobe
    return {
        "__unwired__": "deprecated",
        "registry_name": "FTShare",
        "reason": (
            "Retired: legacy FTShare private MCP captures are historical only; "
            "the public REST collector uses the separate ftshare_rest identity."
        ),
    }


def collect_ftshare_rest(pool: list, *, data_date: str = "", force_reprobe: bool = False) -> dict:
    """Capture the documented FTShare REST quote contract for the configured stock pool."""
    del force_reprobe
    from stock_common.sc_ftshare import FTShareRequestError, get_a_share_quote_snapshot

    codes = list(
        dict.fromkeys(
            str(item.get("code", "")).strip()
            for item in pool
            if isinstance(item, dict) and str(item.get("code", "")).strip()
        )
    )
    if not codes:
        return {
            "__skipped__": "stock pool is empty; no FTShare request was sent",
            "registry_name": "FTShare REST",
        }
    try:
        result = get_a_share_quote_snapshot(codes, data_date=data_date)
    except FTShareRequestError as exc:
        return {"__error__": str(exc), "registry_name": "FTShare REST"}
    result["registry_name"] = "FTShare REST"
    return result

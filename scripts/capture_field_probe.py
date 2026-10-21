#!/usr/bin/env python3
"""Collect daily raw field evidence for the project's registered sources.

The collector writes source payloads and run metadata under
``docs/field_verification/{YYYYMMDD}/``. It records observations for later field
analysis; it does not adjudicate meanings or update the field registry.

Source routing and capture orchestration live here. Shared source metadata,
diagnostics, and archive handling are maintained in ``capture_catalog.py``,
``capture_diagnostics.py``, and ``capture_archive.py``. See ``scripts/README.md``
and ``docs/field_verification/DAILY_RUNBOOK.md`` for the current workflow.

Examples::

    python scripts/capture_field_probe.py
    python scripts/capture_field_probe.py --date 20261021
    python scripts/capture_field_probe.py --only zhb,tdx,tencent
    python scripts/capture_field_probe.py --include-context
    python scripts/capture_field_probe.py --dry-run
    python scripts/capture_field_probe.py --refresh-pool

Market context such as exchange notices and popularity lists is opt-in with
``--include-context``; selecting ``exchange`` or ``em_hot`` through ``--only``
enables it automatically. A successful collection is evidence, not a field
definition or registry decision.
"""

import sys, os, json, time, argparse, glob, math, re
from datetime import date, datetime, time as dt_time, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional, cast

for _s in (sys.stdout, sys.stderr):
    if _s is not None and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
# V17.2.7: 确保本脚本目录(含 field_meta.py)在 sys.path, 使采集时懒加载 field_meta 必然可达
_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)
from scripts.context_policy import (
    CONTEXT_EXCLUDED_PATHS,
    CONTEXT_ONLY_SOURCES,
    CONTEXT_RECORD_PATHS as CONTEXT_RAW_PATHS,
    CONTEXT_REQUIRED_PATHS,
)

from scripts.capture_catalog import (
    BAIDU_PENDING_FIELD_CODES,
    EM_FULL_FIELDS,
    EVENT_ONLY_CAPTURE_SOURCES,
    FULL_POOL_STOCK_SOURCES,
    NON_RAW_SOURCE_STATUS,
    SINA_CAPTURED_FIELD_CODES,
    SINA_PAUSED_OPTION_FIELDS,
    SINA_REQUIRED_FLOW_FIELDS,
    SINA_UNRESOLVED_FIELD_CODES,
    SOURCE_REQUIRED_PATHS,
    SOURCE_SCHEME,
)

from stock_common.sc_utils import em_secid_prefix  # V17.0 S3: 统一 secid 前缀
from core.zhb_client import (
    get_stock_name_from_zhb,
    _lookup_name_persist,
)  # V17.4.10 修复: 供模块级 _resolve_zhb_name 使用(原仅 collect_zhb 局部导入 → NameError)

from scripts.capture_diagnostics import (
    _apply_zhb_freshness,
    _assess_zhb_freshness,
    _capture_error_diagnostic,
    _classify_capture_error,
    _has_error_marker,
    _has_root_error_marker,
    _is_error_marker_key,
    _path_exists,
    _source_as_of_date,
    _source_expected_codes,
    _source_required_paths,
    assess_result,
)

from scripts import capture_archive as CAPA
from scripts.capture_archive import (
    _has_complete_snapshot,
    _preserve_context_paths,
    _retain_current_zhb_snapshot,
)

from scripts import capture_http_collectors as _capture_http_collectors
from scripts.capture_http_collectors import (
    collect_cls,
    collect_em_hot,
    collect_push2ex,
    collect_sina,
    collect_tencent,
)


def _capture_http_dependencies() -> _capture_http_collectors.CaptureHttpDependencies:
    """Snapshot patchable entry-point policies for one collector invocation."""
    return _capture_http_collectors.CaptureHttpDependencies(
        em_full_fields=EM_FULL_FIELDS,
        request_failure_summary=_request_failure_summary,
        request_is_rate_limited=_request_is_rate_limited,
        em_secid_prefix=em_secid_prefix,
        sina_captured_field_codes=SINA_CAPTURED_FIELD_CODES,
        sina_paused_option_fields=SINA_PAUSED_OPTION_FIELDS,
        sina_required_flow_fields=SINA_REQUIRED_FLOW_FIELDS,
        sina_unresolved_field_codes=SINA_UNRESOLVED_FIELD_CODES,
        baidu_pending_field_codes=BAIDU_PENDING_FIELD_CODES,
        parse_baidu_kline_probe=_parse_baidu_kline_probe,
        last_completed_trading_day=_last_completed_trading_day,
        em_capture_pause_reason=_em_capture_pause_reason,
    )


from scripts import capture_verified_collectors as _capture_verified_collectors
from scripts.capture_verified_collectors import collect_ftshare, collect_ftshare_rest


def _capture_source_dependencies() -> _capture_verified_collectors.CaptureSourceDependencies:
    """Build a per-call snapshot of the entry point's injectable helpers."""
    return _capture_verified_collectors.CaptureSourceDependencies(
        identity_capture_block_reason=_identity_capture_block_reason,
        attach_identity_validation_suppression=_attach_identity_validation_suppression,
        request_is_rate_limited=_request_is_rate_limited,
        defer_axdata_codes=_defer_axdata_codes,
        capture_source_fields=_capture_source_fields,
        kpl_timestamp_date=_kpl_timestamp_date,
        parse_capture_date=_parse_capture_date,
        six_digit_symbol=_six_digit_symbol,
        kph_history_trade_date=_kph_history_trade_date,
        kph_ladder_blocks_followup=_kph_ladder_blocks_followup,
        fuyao_auction_items=_fuyao_auction_items,
        fuyao_auction_snapshot_meta=_fuyao_auction_snapshot_meta,
        last_completed_trading_day=_last_completed_trading_day,
    )


from scripts import capture_tcp_collectors as _capture_tcp_collectors
from scripts.capture_tcp_collectors import collect_tdx_f10, collect_tdx_f10_more

from scripts import capture_context_collectors as _capture_context_collectors
from scripts.capture_context_collectors import (
    collect_cninfo,
    collect_datacenter,
    collect_event_dc,
    collect_macro_dc,
    collect_reports,
    collect_research_sina,
    collect_sse_e_interaction,
    collect_st_list,
)

POOL_PATH = os.path.join(_ROOT, "docs", "field_verification", "pool.json")
OUT_BASE = os.path.join(_ROOT, "docs", "field_verification")


# 模块文档未改动处见上方 docstring; 输出文件新增 scheme 标注(见 main)。


def load_pool() -> List[Dict[str, Any]]:
    with open(POOL_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("pool.json must contain a JSON object")
    fixed = data.get("fixed")
    dynamic = data.get("dynamic")
    if not isinstance(fixed, list) or not isinstance(dynamic, list):
        raise ValueError("pool.json must contain fixed and dynamic lists")
    entries = fixed + dynamic
    if not all(isinstance(item, dict) for item in entries):
        raise ValueError("pool entries must be JSON objects")
    return cast(List[Dict[str, Any]], entries)


def _last_trading_day_str() -> str:
    """返回最近已收盘交易日 YYYYMMDD(涨停池按交易日快照)。"""
    return _last_completed_trading_day().strftime("%Y%m%d")


def _validate_capture_data_date(value: str, only_sources=None, session_checker=None):
    """Validate capture target date according to its data domain."""
    text = str(value or "").strip()
    if len(text) != 8 or not text.isdigit():
        raise ValueError("--date 必须是 YYYYMMDD")
    try:
        capture_day = datetime.strptime(text, "%Y%m%d").date()
    except ValueError as exc:
        raise ValueError(f"--date 不是有效日期: {text}") from exc
    if capture_day.strftime("%Y%m%d") != text:
        raise ValueError(f"--date 不是有效日期: {text}")

    selected = {name.strip() for name in (only_sources or []) if name.strip()}
    event_only = bool(selected) and selected.issubset(EVENT_ONLY_CAPTURE_SOURCES)
    if not event_only:
        if session_checker is None:
            from stock_common.stock_calendar import is_workday_with_zhb_supplement

            session_checker = is_workday_with_zhb_supplement
        if not session_checker(capture_day):
            raise ValueError(
                f"--date {text} 不是 A 股交易日；行情采集必须使用交易日。"
                "仅新闻/公告源可在 --only 中单独选择并使用自然日"
            )
    return capture_day, "calendar" if event_only else "trading"


def _market_close_dt(date_str: str) -> datetime:
    """数据日 15:00(收盘)时间点; A股收盘后视为完整(收盘)数据。"""
    return datetime(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]), 15, 0, 0)


def _capture_market_phase(now: Optional[datetime] = None, session_checker=None) -> str:
    """按实际采集时刻标记交易时段，与 meta.market_phase 的数据完整度口径分开。"""
    current = now or datetime.now()
    if session_checker is None:
        from stock_common.stock_calendar import is_workday_with_zhb_supplement

        session_checker = is_workday_with_zhb_supplement
    try:
        if not session_checker(current.date()):
            return "non_trading_day"
    except Exception:
        return "unknown"

    clock = current.time()
    if clock < dt_time(9, 15):
        return "pre_open"
    if clock < dt_time(9, 25):
        return "call_auction"
    if clock < dt_time(9, 30):
        return "pre_open"
    if clock < dt_time(11, 30):
        return "morning_session"
    if clock < dt_time(13, 0):
        return "lunch_break"
    if clock < dt_time(15, 0):
        return "afternoon_session"
    return "closed"


def _is_closed_phase_now(date_str: str) -> bool:
    """本次运行是否处于数据日收盘之后(即采集到的是完整收盘数据)。"""
    return datetime.now() >= _market_close_dt(date_str)


def _is_closed_phase_existing(meta_path: str, date_str: str) -> bool:
    """已有采集物是否收盘后(完整)。无 start 记录则保守当作盘中(可被刷新)。"""
    try:
        with open(meta_path, encoding="utf-8") as f:
            m = json.load(f)
        start = m.get("start") or m.get("run_datetime")
        if not start:
            return False
        sd = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        return sd >= _market_close_dt(date_str)
    except Exception:
        return False


def _board_of(code: str, name: str = "", market_type: str = "") -> str:
    """根据代码前缀(优先)与市场类型文本推导板块中文名。"""
    c = str(code or "")
    if c.startswith("688"):
        return "科创板"
    if c.startswith(("300", "301")):
        return "创业板"
    if c.startswith(("8", "92", "43")):
        return "北交所"
    if c.startswith("60"):
        return "沪主板"
    if c.startswith("002"):
        return "中小板"
    if c.startswith(("000", "003", "004")):
        return "深主板"
    mt = str(market_type)
    if "科创" in mt:
        return "科创板"
    if "创业" in mt:
        return "创业板"
    if "北交" in mt:
        return "北交所"
    if "沪" in mt or "SH" in mt.upper():
        return "沪主板"
    if "深" in mt or "SZ" in mt.upper():
        return "深主板"
    return "其他"


def _parse_consecutive_boards(high_days: str) -> int:
    """从涨停池 high_days 文本解析连板数。

    同花顺返回格式: '首板' / '2天2板' / '4天3板' / '4天4板' ...
    其中末位 'M板' 的 M 即连续涨停板数(4天3板=近4交易日封3板);
    '首板' 记为 1。上游 ths_limit_up_pool 的 limit_count 字段解析 'N天M板' 失败恒为 1,
    故此处独立解析 high_days, 不依赖该字段。
    """
    import re

    s = str(high_days or "")
    if "首板" in s:
        return 1
    nums = re.findall(r"(\d+)板", s)  # 取 'M板' 的数字
    if not nums:
        nums = re.findall(r"\d+", s)  # 兜底: 任意数字取末位
    return int(nums[-1]) if nums else 1


def refresh_dynamic_layer(trade_date: str = "", write: bool = True) -> list:
    """每日刷新动态层: 从涨停池挑选 5 只覆盖特殊状态(连板/新股/涨停)的股票。

    挑选层级(呼应 pool_rules.dynamic_refresh「连板(ZHB streak>=5)/涨停池/新股」):
      ① 连板(lc>=2) 按连板数降序
      ② 新股(is_new) 按连板数降序(保证新股覆盖)
      ③ 其余涨停(lc==1) 按涨幅降序
    拼接至满 5 只; 剔除固定层代码与同代码重复, 保证与固定层不重叠。
    写回 pool.json 的 dynamic(仅覆盖面, 不动 fixed), 并回填 date=实际交易日。
    网络/解析失败时保留原动态层(返回 [] 并告警), 绝不破坏后续采集。

    Args:
        trade_date: 交易日 YYYYMMDD; 为空则取最近交易日。若指定日无数据(如周末)自动回退最近交易日。
        write: True=写回 pool.json; False=仅返回候选(预览/--dry-run)。
    Returns:
        新动态层列表(每项 {code,name,tags,date}); 失败时返回 []。
    """
    if not trade_date:
        trade_date = _last_trading_day_str()
    used_date = trade_date

    def _fetch(d: str):
        try:
            from stock_common import ths_limit_up_pool

            p = ths_limit_up_pool(d)
            if not p:
                from stock_common import get_limit_up_pool

                p = get_limit_up_pool(d)
            return p or []
        except Exception as e:
            print(f"  ⚠ 动态层刷新失败(网络/依赖异常): {e}; 保留旧动态层", flush=True)
            return None

    pool = _fetch(trade_date)
    if pool is None:
        return []
    # 指定日无数据 → 回退最近交易日
    if not pool and trade_date != (last := _last_trading_day_str()):
        pool = _fetch(last)
        if pool is None:
            return []
        used_date = last
    if not pool:
        print("  ⚠ 涨停池为空(可能非交易日/接口空), 保留旧动态层", flush=True)
        return []

    # 固定层代码, 剔除与固定层重叠
    try:
        with open(POOL_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        fixed_codes = {str(p.get("code")) for p in data.get("fixed", [])}
    except Exception:
        fixed_codes = set()

    seen, parsed = set(), []
    for it in pool:
        code = str(it.get("code") or "")
        if not code or code in seen or code in fixed_codes:
            continue
        seen.add(code)
        lc = _parse_consecutive_boards(it.get("high_days")) or int(
            it.get("limit_count") or it.get("zt_days") or 1
        )
        is_new = bool(it.get("is_new"))
        name = it.get("name") or ""
        is_st = name.startswith("*ST") or name.startswith("ST")
        pct = float(it.get("change_pct") or 0)
        parsed.append(
            {
                "code": code,
                "name": name,
                "lc": lc,
                "is_new": is_new,
                "is_st": is_st,
                "pct": pct,
                "market_type": it.get("market_type", ""),
            }
        )

    cont = sorted(
        [x for x in parsed if x["lc"] >= 2], key=lambda x: (x["lc"], x["pct"]), reverse=True
    )
    newp = sorted(
        [x for x in parsed if x["is_new"]], key=lambda x: (x["lc"], x["pct"]), reverse=True
    )
    zt = sorted([x for x in parsed if x["lc"] < 2], key=lambda x: x["pct"], reverse=True)

    ordered, _seen = [], set()
    for bucket in (cont, newp, zt):
        for x in bucket:
            if x["code"] in _seen:
                continue
            _seen.add(x["code"])
            ordered.append(x)

    picks_raw = ordered[:5]
    if not picks_raw:
        print("  ⚠ 有效候选为空, 保留旧动态层", flush=True)
        return []

    picks = []
    for x in picks_raw:
        board = _board_of(x["code"], x["name"], x["market_type"])
        tags = [f"动态-{board}"]
        tags.append(f"连板{x['lc']}" if x["lc"] >= 2 else "涨停")
        if x["is_new"]:
            tags.append("新股")
        if x["is_st"]:
            tags.append("ST")
        picks.append({"code": x["code"], "name": x["name"], "tags": tags, "date": used_date})

    if write:
        try:
            with open(POOL_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["dynamic"] = picks
            with open(POOL_PATH, "w", encoding="utf-8") as f:
                # 沿用 pool.json 原始 1 空格缩进风格, 仅重写 dynamic 块, 避免每次刷新整文件重排(diff 噪声)
                json.dump(data, f, ensure_ascii=False, indent=1)
            print(
                f"  ✔ 动态层刷新成功(交易日 {used_date}, 涨停池 {len(pool)} 只 → 选 {len(picks)} 只): "
                + ", ".join(f"{p['code']}/{p['name']}" for p in picks),
                flush=True,
            )
        except Exception as e:
            print(f"  ⚠ 动态层写回失败: {e}; 本次采集仍用内存候选", flush=True)
    return picks


def collect_zhb(pool: list) -> dict:
    """Compatibility wrapper preserving ZHB name-resolution injection."""
    return _capture_tcp_collectors.collect_zhb(pool, _resolve_zhb_name)


def _resolve_zhb_name(code: str) -> Optional[str]:
    """ZHB 名称解析: 离线合并字典 → 持久化缓存(full 字典, 网络种子, 覆盖 ZHB 离线未含代码如 600519)。

    V17.3.3: get_stock_name_from_zhb 已实现该回退链(离线→持久化); 此处显式化以保证
    采集血缘不受后续重构影响, 并消除「采集时持久化缓存尚未播种导致 name=None」的瞬时现象
    (重跑即能回退到缓存中的 贵州茅台/宁德时代 等正确名)。
    """
    n = get_stock_name_from_zhb(code)
    if n:
        return n
    return _lookup_name_persist(code)


def _capture_float(value: Any) -> Optional[float]:
    """Convert one optional wire value to float without leaking type errors."""
    if not isinstance(value, (int, float, str)):
        return None
    try:
        return float(value)
    except (ValueError, OverflowError):
        return None


def _normalize_tdx_capture_quote(raw_quote: Any) -> Optional[Dict[str, Any]]:
    """Expose stable TDX quote paths while keeping the adapter's raw row separately."""
    if not isinstance(raw_quote, dict):
        return None

    result: Dict[str, Any] = {}
    aliases = {
        "price": ("price",),
        "last_close": ("last_close", "pre_close"),
        "open": ("open",),
        "high": ("high",),
        "low": ("low",),
        "s_vol": ("s_vol",),
        "b_vol": ("b_vol",),
        "rise_speed": ("rise_speed",),
        "avg_price": ("avg_price", "average_price"),
        "entrust_ratio": ("entrust_ratio",),
        "pe_ttm": ("pe_ttm",),
        "pb": ("pb",),
        "turnover_pct": ("turnover_pct",),
    }
    for target, candidates in aliases.items():
        for source_key in candidates:
            value = raw_quote.get(source_key)
            if value is not None and value != "":
                result[target] = value
                break

    for level in range(1, 6):
        for side in ("bid", "ask"):
            for suffix in ("", "_vol"):
                key = f"{side}{level}{suffix}"
                value = raw_quote.get(key)
                if value is not None and value != "":
                    result[key] = value

    amount = raw_quote.get("amount")
    if amount is not None and amount != "":
        try:
            result["amount_wan"] = float(amount) / 10000.0
        except (TypeError, ValueError, OverflowError):
            pass

    last_close_value = raw_quote.get("last_close")
    if last_close_value is None or last_close_value == "":
        last_close_value = raw_quote.get("pre_close")
    price = _capture_float(raw_quote.get("price"))
    last_close = _capture_float(last_close_value)
    if last_close is not None and price is not None and last_close > 0 and price > 0:
        result["change_pct"] = (price - last_close) / last_close * 100.0
        result["change_amt"] = price - last_close

    return result or None


def collect_tdx(pool: list) -> dict:
    """Compatibility wrapper preserving TDX normalization injection."""
    return _capture_tcp_collectors.collect_tdx(
        pool, _normalize_tdx_capture_quote, _has_populated_capture_value
    )


def _eltdx_preopen_not_ready(exc: Exception) -> bool:
    """Recognize the known shortline readiness message only before the 09:25 cut-off."""
    message = str(exc).lower()
    not_ready = any(
        marker in message
        for marker in (
            "shortline indicators not ready before 09:25",
            "shortline indicators not ready before 9:25",
            "短线指标尚未就绪",
            "短线指标未就绪",
        )
    )
    return not_ready and datetime.now().time() < dt_time(9, 25)


def _eltdx_failure_marker(exc: Exception) -> dict:
    message = str(exc)[:200]
    if _eltdx_preopen_not_ready(exc):
        return {"__skipped__": f"deferred: {message}"}
    return {"__error__": message}


def collect_eltdx(pool: list, lite: bool = False) -> dict:
    """Compatibility wrapper preserving ELTDX diagnostic injection."""
    return _capture_tcp_collectors.collect_eltdx(pool, _eltdx_failure_marker, lite=lite)


def _request_failure_summary(label: str, detail: dict) -> str:
    """Render a compact transport failure without exposing request parameters."""
    parts = [str(detail.get("kind") or "no_response")]
    if detail.get("domain"):
        parts.append(f"domain={detail['domain']}")
    if detail.get("status_code") is not None:
        parts.append(f"status={detail['status_code']}")
    if detail.get("error_type"):
        parts.append(str(detail["error_type"]))
    if detail.get("attempts") is not None:
        parts.append(f"attempts={detail['attempts']}")
    if detail.get("message"):
        parts.append(str(detail["message"]).split("?", 1)[0][:160])
    return f"{label}: " + ", ".join(parts)


def _request_is_rate_limited(detail: dict) -> bool:
    """Whether a response means this capture source should stop requesting."""
    kind = str(detail.get("kind") or "").lower()
    status = detail.get("status_code")
    status_code: Optional[int] = None
    if isinstance(status, int):
        status_code = status
    elif isinstance(status, str):
        try:
            status_code = int(status)
        except ValueError:
            status_code = None
    message = " ".join(str(detail.get(key) or "") for key in ("message", "error", "status"))
    return (
        kind
        in {
            "ip_banned",
            "http_403",
            "http_429",
            "rate_limited",
            "circuit_open",
            "suppressed_after_failures",
        }
        or status_code
        in (
            403,
            429,
        )
        or bool(
            re.search(
                r"\b403\b|\b429\b|blocked|banned|rate.?limit|封禁|限流|访问频繁",
                message,
                re.I,
            )
        )
    )


def _em_capture_pause_reason(
    label: str, detail: dict, consecutive_disconnects: int
) -> Optional[str]:
    """Stop a capture source on throttling, bans, or three consecutive transport failures."""
    if _request_is_rate_limited(detail):
        return _request_failure_summary(label, detail)
    kind = str(detail.get("kind") or "").lower()
    if kind in {"connection_error", "timeout"} and consecutive_disconnects >= 3:
        domain = str(detail.get("domain") or label)
        return f"{domain}: paused after {consecutive_disconnects} consecutive {kind} failures"
    return None


def collect_push2(pool: list) -> dict:
    """Compatibility wrapper preserving capture-entry dependency injection."""
    return _capture_http_collectors.collect_push2(pool, _capture_http_dependencies())


# NOTE(V17.3.1): collect_push2_full 已移除——与 collect_push2 逐字同构(同端点 push2/push2delay
#   stock/get、同 f1-f250、同兜底域), 实测 114 字段值级 114/114 全相等, 属纯冗余负载。
#   日常采集改走 collect_push2 即可; 如需对撞复核原 push2_full 号段, 用 `--only push2`。
#   本函数不再保留(避免与 collect_push2 双份维护); 历史说明见 field_source_reference.md §12.9.1
#   push2_full 条目作运行时 fallback 参考(语义等价, 见「同源同步治理规则」)。


def collect_sina_extended(pool: list) -> dict:
    """Compatibility wrapper preserving capture-entry dependency injection."""
    return _capture_http_collectors.collect_sina_extended(pool, _capture_http_dependencies())


def _defer_axdata_codes(
    output: dict[str, Any], pool: list[dict[str, Any]], next_index: int, stopped_code: str
) -> None:
    deferred = pool[next_index:]
    reason = "deferred after AxData HTTP 403/429 or ban signal"
    for item in deferred:
        output["stocks"][item["code"]] = {"__skipped__": reason}
    source_meta = output.setdefault("__source_meta__", {})
    source_meta.update(
        {
            "rate_limited": True,
            "interface_id": "stock_shortline_indicators_tdx",
            "stopped_after_code": stopped_code,
            "deferred_codes": [item["code"] for item in deferred],
        }
    )


def _identity_capture_block_reason(identity_policy: Optional[dict]) -> Optional[str]:
    """Return a reason when the identity policy says not to call the endpoint."""
    if not isinstance(identity_policy, dict) or identity_policy.get("action") != "skip":
        return None
    identity = identity_policy.get("identity")
    identity = identity if isinstance(identity, dict) else {}
    status = identity.get("status")
    reason = str(identity_policy.get("reason") or "capture_policy_skip")
    validation_action = identity_policy.get("identity_validation_action")
    if status == "operationally_redundant":
        return reason
    if validation_action == "suppress" or status == "partially_redundant":
        return None
    return reason


def _identity_validation_suppression(identity_policy: Optional[dict]) -> Optional[dict[str, Any]]:
    if not isinstance(identity_policy, dict):
        return None
    identity = identity_policy.get("identity")
    identity = identity if isinstance(identity, dict) else {}
    if identity_policy.get("identity_validation_action") != "suppress" and identity.get(
        "status"
    ) not in {"operationally_redundant", "partially_redundant"}:
        return None
    return {
        "status": identity.get("status"),
        "interface_id": identity.get("interface_id"),
        "reference_source": identity_policy.get("reference_source"),
        "reason": str(identity_policy.get("reason") or "identity_already_confirmed"),
        "evidence_dates": identity.get("evidence_dates", []),
        "capture_performed": True,
    }


def _attach_identity_validation_suppression(
    output: dict[str, Any], identity_policy: Optional[dict]
) -> None:
    suppression = _identity_validation_suppression(identity_policy)
    if suppression is not None:
        output.setdefault("__source_meta__", {})["identity_validation_suppression"] = suppression


def collect_axdata(pool: list, identity_policy: Optional[dict] = None) -> dict:
    """Compatibility wrapper preserving policy and rate-limit patch seams."""
    return _capture_verified_collectors.collect_axdata(
        pool, _capture_source_dependencies(), identity_policy
    )


def collect_market_sources(
    pool: list,
    include_context: bool = False,
    include_kpl_detail: bool = True,
    trade_date: Optional[str] = None,
) -> dict:
    """采集市场数值指标；龙虎榜和 KPL 明细均可由调用方单独控制。"""
    import stock_common

    out: Dict[str, Any] = {}

    def capture_one(name: str, function_name: str, *args, **kwargs) -> None:
        try:
            fn = getattr(stock_common, function_name)
            result = fn(*args, **kwargs)
            if result is None:
                out[name] = {"__error__": "collector returned None"}
            elif (
                name
                in {
                    "cls_market_emotion",
                    "kph_limit_ladder",
                    "kpl_sentiment",
                    "kpl_up_down",
                    "kpl_plate_strength",
                    "kpl_broken_ratio",
                    "kpl_limit_up_detail",
                }
                and isinstance(result, dict)
                and ("__error__" in result or "__skipped__" in result)
            ):
                out[name] = result
            elif name in {
                "cls_market_emotion",
                "kph_limit_ladder",
                "kpl_sentiment",
                "kpl_up_down",
                "kpl_plate_strength",
                "kpl_broken_ratio",
                "kpl_limit_up_detail",
            } and not (_has_populated_capture_value(result)):
                out[name] = {"__error__": f"empty response from {name} adapter"}
            else:
                out[name] = result
        except Exception as exc:
            out[name] = {"__error__": str(exc)[:200]}

    try:
        if trade_date:
            try:
                kph_trade_date = datetime.strptime(trade_date, "%Y%m%d").date().isoformat()
            except ValueError:
                kph_trade_date = datetime.strptime(trade_date, "%Y-%m-%d").date().isoformat()
        else:
            kph_trade_date = _last_completed_trading_day().isoformat()
    except Exception as exc:
        kph_trade_date = None
        out["kph_limit_ladder"] = {
            "__error__": f"KPH trade-date selection failed: {str(exc)[:160]}"
        }

    out["__source_meta__"] = {
        "cls_market_emotion": {
            "adapter": "levistock.market_emotion_cls",
            "provider_family": "cls",
            "date_domain": "trading_day",
            "date_evidence": "response_only",
            "collection_path": "existing_market_sources_call",
        },
        "kph_limit_ladder": {
            "adapter": "levistock.get_zttt",
            "provider_family": "kph",
            "date_domain": "trading_day",
            "requested_trade_date": kph_trade_date,
            "date_evidence": "request_parameter" if kph_trade_date else "unavailable",
            "collection_path": "existing_market_sources_call",
        },
    }
    capture_one("cls_market_emotion", "get_cls_market_emotion")
    if kph_trade_date:
        capture_one("kph_limit_ladder", "get_kph_limit_ladder", kph_trade_date)
    capture_one("stock_changes_8201", "get_stock_changes", "8201")
    capture_one("kpl_sentiment", "get_kpl_market_sentiment", capture_raw=True)
    capture_one("kpl_up_down", "get_kpl_up_down", capture_raw=True)
    capture_one("kpl_plate_strength", "get_kpl_plate_strength", capture_raw=True)
    if include_kpl_detail:
        try:
            out["kpl_limit_up_detail"] = collect_kpl_detail(trade_date or datetime.now().date())
        except Exception as exc:
            out["kpl_limit_up_detail"] = {"__error__": str(exc)[:200]}
    capture_one("kpl_broken_ratio", "get_kpl_broken_ratio", capture_raw=True)
    capture_one(
        "plate_rotation_matrix",
        "get_plate_rotation_matrix",
        source="kaipan",
        days=20,
        top_n=30,
    )
    capture_one("plate_rotation_top", "get_plate_rotation_top")
    if not include_context:
        return out
    try:
        trade_date = _last_completed_trading_day().strftime("%Y-%m-%d")
    except Exception as exc:
        out["trade_date"] = None
        out["dragon_tiger_today"] = {"__error__": f"query date unavailable: {str(exc)[:160]}"}
        return out
    out["trade_date"] = trade_date
    capture_one(
        "dragon_tiger_today",
        "eastmoney_datacenter",
        "",
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(TRADE_DATE>='{trade_date}')(TRADE_DATE<='{trade_date}')",
        page_size=50,
        sort_columns="TRADE_DATE",
        sort_types="-1",
    )
    return out


def _parse_capture_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError("capture date must be YYYYMMDD or YYYY-MM-DD")
    text = value.strip()
    for date_format in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            continue
    raise ValueError(f"invalid capture date: {value!r}")


def _kph_history_trade_date(capture_date: Any, today: Optional[date] = None) -> date:
    """Choose a valid trade date strictly before AxData's natural-day cutoff."""
    from stock_common.stock_calendar import is_workday_with_zhb_supplement

    requested = _parse_capture_date(capture_date)
    natural_today = today or date.today()
    if requested > natural_today:
        raise ValueError(f"KPH capture date {requested} is in the future")
    candidate = min(requested, natural_today - timedelta(days=1))
    for _ in range(370):
        if is_workday_with_zhb_supplement(candidate):
            return candidate
        candidate -= timedelta(days=1)
    raise RuntimeError("ZHB calendar has no previous valid trading day for KPH history")


def _kph_ladder_blocks_followup(market_sources: Any) -> bool:
    """Avoid a second same-family request when the existing KPH sample is unavailable."""
    if not isinstance(market_sources, dict):
        return False
    ladder = market_sources.get("kph_limit_ladder")
    if not isinstance(ladder, dict):
        return False
    if "__error__" in ladder or "__skipped__" in ladder:
        return True
    detail = " ".join(str(value) for value in ladder.values()).casefold()
    return any(
        marker in detail
        for marker in (
            "403",
            "429",
            "forbidden",
            "too many requests",
            "rate limit",
            "rate-limit",
            "banned",
            "blocked",
            "封禁",
            "限流",
        )
    )


def _six_digit_symbol(row: Dict[str, Any]) -> Optional[str]:
    raw = row.get("symbol") or row.get("instrument_id") or row.get("code")
    if raw is None:
        return None
    match = re.search(r"(?<!\d)(\d{6})(?!\d)", str(raw).strip())
    return match.group(1) if match else None


_SOURCE_IDENTITY_FIELDS = frozenset(
    {
        "code",
        "id",
        "symbol",
        "stock_code",
        "stockcode",
        "instrument_id",
        "pid_type",
        "exchange",
        "trade_date",
    }
)


def _json_safe_source_value(value: Any) -> Any:
    """Preserve a source value in JSON form without dropping non-numeric fields."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe_source_value(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe_source_value(child) for child in value]
    return str(value)


def _capture_source_fields(row: Dict[str, Any]) -> Dict[str, Any]:
    """Keep all response fields and retain row identity under a non-field key."""
    fields: Dict[str, Any] = {}
    identity: Dict[str, Any] = {}
    for key, value in row.items():
        field_name = str(key)
        target = identity if field_name.casefold() in _SOURCE_IDENTITY_FIELDS else fields
        target[field_name] = _json_safe_source_value(value)
    if identity:
        fields["__identity__"] = identity
    return fields


def _kpl_timestamp_date(value: Any) -> Optional[date]:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return None
    timestamp = float(value)
    if timestamp > 100_000_000_000:
        timestamp /= 1000
    try:
        return datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=8))).date()
    except (OverflowError, OSError, ValueError):
        return None


def collect_kpl_detail(capture_date: Any) -> dict:
    """Compatibility wrapper preserving source parsing helper patch seams."""
    return _capture_verified_collectors.collect_kpl_detail(
        capture_date, _capture_source_dependencies()
    )


def collect_kph_history(
    capture_date: Any,
    prior_market_sources: Any = None,
    identity_policy: Optional[dict] = None,
) -> dict:
    """Compatibility wrapper preserving date and identity policy patch seams."""
    return _capture_verified_collectors.collect_kph_history(
        capture_date, _capture_source_dependencies(), prior_market_sources, identity_policy
    )


def _parse_baidu_kline_probe(payload: Any) -> Optional[Dict[str, Any]]:
    """Validate and retain Baidu's raw K-line shape, exposing its three MA values."""
    if not isinstance(payload, dict):
        return None
    result = payload.get("Result")
    market = result.get("newMarketData") if isinstance(result, dict) else None
    if not isinstance(market, dict):
        return None
    keys = market.get("keys")
    market_data = market.get("marketData")
    if not isinstance(keys, list) or not isinstance(market_data, str):
        return None
    required_ma = set(BAIDU_PENDING_FIELD_CODES)
    if not required_ma.issubset({key for key in keys if isinstance(key, str)}):
        return None
    rows = [row for row in market_data.split(";") if row.strip()]
    if not rows:
        return None
    values = rows[-1].split(",")
    record: Dict[str, Any] = {
        "newMarketData": market,
        "keys": keys,
        "marketData": market_data,
        "rows": rows,
    }
    for key, value in zip(keys, values):
        if key in required_ma:
            record[key] = value
    if not required_ma.issubset(record):
        return None
    return record


def collect_baidu(pool: list, probe: bool = False) -> dict:
    """Compatibility wrapper preserving the explicit one-probe API."""
    return _capture_http_collectors.collect_baidu(pool, _capture_http_dependencies(), probe=probe)


def collect_clist(pool: list) -> dict:
    """Compatibility wrapper preserving capture-entry dependency injection."""
    return _capture_http_collectors.collect_clist(pool, _capture_http_dependencies())


def collect_slist(pool: list) -> dict:
    """Compatibility wrapper preserving capture-entry dependency injection."""
    return _capture_http_collectors.collect_slist(pool, _capture_http_dependencies())


def collect_exchange(pool: list) -> dict:
    """Compatibility wrapper preserving capture-entry dependency injection."""
    return _capture_http_collectors.collect_exchange(pool, _capture_http_dependencies())


def _last_completed_trading_day() -> date:
    """返回最近已收盘的 A 股交易日，覆盖周末、法定节假日和调休补班周末。"""
    from stock_common.stock_calendar import is_workday_with_zhb_supplement

    now = datetime.now()
    today = now.date()
    candidate = today
    include_current = is_workday_with_zhb_supplement(today) and now.time() >= dt_time(15, 0)
    if not include_current:
        candidate -= timedelta(days=1)
    for _ in range(370):
        if is_workday_with_zhb_supplement(candidate):
            return candidate
        candidate -= timedelta(days=1)
    raise RuntimeError("ZHB 补充日历中无法找到最近已收盘交易日")


def _normalize_fuyao_source_date(value: Any) -> Optional[str]:
    """Normalize a date explicitly labeled as source data date; never parse timestamps."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    for date_format in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(normalized, date_format).date().isoformat()
        except ValueError:
            continue
    return None


def _normalize_fuyao_response_timestamp_date(value: Any) -> Optional[str]:
    """Return the Shanghai calendar date of response assembly time, never a data date."""
    shanghai = timezone(timedelta(hours=8))
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, datetime):
        timestamp = value if value.tzinfo else value.replace(tzinfo=shanghai)
        return timestamp.astimezone(shanghai).date().isoformat()
    if isinstance(value, date):
        return value.isoformat()

    numeric = None
    if isinstance(value, (int, float)):
        numeric = float(value)
    elif isinstance(value, str):
        normalized = value.strip()
        if not normalized:
            return None
        try:
            numeric = float(normalized)
        except ValueError:
            try:
                timestamp = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
            except ValueError:
                return None
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=shanghai)
            return timestamp.astimezone(shanghai).date().isoformat()
    else:
        return None

    if numeric is None or not math.isfinite(numeric) or numeric <= 0:
        return None
    epoch_seconds = numeric / 1000 if numeric >= 100_000_000_000 else numeric
    try:
        return datetime.fromtimestamp(epoch_seconds, tz=shanghai).date().isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def _fuyao_auction_snapshot_meta(envelope: Any, stage: str, expected_trading_day: date) -> dict:
    """Build provenance metadata without treating response assembly time as data time."""
    envelope = envelope if isinstance(envelope, dict) else {}
    data = envelope.get("data")
    data = data if isinstance(data, dict) else {}

    def envelope_value(key: str) -> Any:
        value = envelope.get(key)
        return data.get(key) if value is None else value

    source_data_date = None
    source_data_date_field = None
    for key in ("data_date", "trade_date", "tradeDate", "as_of_date", "asof_date"):
        source_data_date = _normalize_fuyao_source_date(envelope_value(key))
        if source_data_date:
            source_data_date_field = key
            break

    raw_status = envelope_value("data_status")
    status = str(raw_status or "").strip().lower().replace("-", "_").replace(" ", "_")
    response_timestamp = envelope_value("timestamp")
    response_timestamp_date = _normalize_fuyao_response_timestamp_date(response_timestamp)
    auction_phase = envelope_value("auction_phase")

    eligible = False
    if not envelope:
        reason = "source_response_missing"
    elif envelope.get("code") != 0:
        reason = "source_response_not_successful"
    elif source_data_date is None:
        reason = "source_data_date_unavailable"
    elif status not in {
        "ready",
        "complete",
        "completed",
        "final",
        "success",
        "ok",
        "available",
        "done",
    }:
        reason = "source_status_not_confirmed_ready"
    elif source_data_date != expected_trading_day.isoformat():
        reason = "source_date_differs_from_snapshot_date"
    else:
        eligible = True
        reason = None

    return {
        "requested_stage": stage,
        "response_code": envelope.get("code"),
        "data_status": raw_status,
        "auction_phase": auction_phase,
        "response_timestamp": response_timestamp,
        "response_timestamp_date": response_timestamp_date,
        "response_timestamp_semantics": "response_assembly_time_only",
        "source_data_date": source_data_date,
        "source_data_date_basis": (
            f"explicit_response_field:{source_data_date_field}"
            if source_data_date_field
            else "not_exposed_by_auction_snapshot_contract"
        ),
        "expected_trading_day": expected_trading_day.isoformat(),
        "collision_eligible": eligible,
        "exclusion_reason": reason,
    }


def _fuyao_auction_items(envelope: Any) -> list:
    """Extract auction items from the preserved Fuyao response envelope."""
    if not isinstance(envelope, dict):
        return []
    data = envelope.get("data")
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("item") or []
    else:
        return []
    return [item for item in items if isinstance(item, dict)] if isinstance(items, list) else []


def collect_fuyao(pool: list, include_context: bool = False) -> dict:
    """Compatibility wrapper preserving Fuyao date and auction metadata seams."""
    return _capture_verified_collectors.collect_fuyao(
        pool, _capture_source_dependencies(), include_context
    )


def _has_populated_capture_value(value: Any, key: str = "") -> bool:
    """Treat zero/False as data but ignore empty containers and capture metadata."""
    if key in {
        "probe_trading_day",
        "scheme",
        "field_meta",
        "__source_meta__",
        "__error__",
        "__skipped__",
    }:
        return False
    if isinstance(value, dict):
        return any(
            _has_populated_capture_value(child, child_key) for child_key, child in value.items()
        )
    if isinstance(value, list):
        return any(_has_populated_capture_value(child) for child in value)
    return value is not None and value != ""


def collect_em_kline_f61(pool: list) -> dict:
    """Compatibility wrapper preserving capture-entry dependency injection."""
    return _capture_http_collectors.collect_em_kline_f61(pool, _capture_http_dependencies())


def collect_em_fund_flow(pool: list) -> dict:
    """Compatibility wrapper preserving capture-entry dependency injection."""
    return _capture_http_collectors.collect_em_fund_flow(pool, _capture_http_dependencies())


def collect_ulist239(pool: list) -> dict:
    """Compatibility wrapper preserving capture-entry dependency injection."""
    return _capture_http_collectors.collect_ulist239(pool, _capture_http_dependencies())


def _recent_calendar_days(n: int = 4, today=None) -> List[str]:
    """Return the most recent calendar dates, including weekends and holidays."""
    from datetime import date, timedelta

    current = today or date.today()
    out: List[str] = []
    for _ in range(max(0, n)):
        out.append(current.strftime("%Y-%m-%d"))
        current -= timedelta(days=1)
    return out


def _recent_trade_days(n: int = 4, today=None) -> List[str]:
    """Return recent A-share sessions, excluding exchange holidays and make-up weekends."""
    from stock_common.stock_calendar import recent_trading_dates

    return [day.strftime("%Y-%m-%d") for day in recent_trading_dates(max(0, n), today)]


def collect_etf(pool: list) -> dict:
    """Compatibility wrapper preserving the entry point's date-helper patch seam."""
    return _capture_context_collectors.collect_etf(pool, _recent_trade_days)


def collect_news_wscn_cctv(pool: list) -> dict:
    """Compatibility wrapper preserving the entry point's calendar-helper patch seam."""
    return _capture_context_collectors.collect_news_wscn_cctv(pool, _recent_calendar_days)


def dry_run(pool: list) -> None:
    print(f"[dry-run] pool={len(pool)} 只")
    from core.zhb_client import get_zhb, is_data_fresh

    zhb = get_zhb()
    print(f"  ZHB     : date={zhb.date if zhb else 'N/A'} fresh={is_data_fresh()}")
    from core.tdx_client import _check_tdx

    print(f"  TDX     : {_check_tdx()}")
    from stock_common import _quick_request

    r = _quick_request("https://qt.gtimg.cn/q=sh600519", timeout=8)
    print(f"  腾讯    : {'OK' if r is not None else 'FAIL'}")
    r = _quick_request(
        "https://push2.eastmoney.com/api/qt/stock/get",
        params={"secid": "1.600519", "fltt": "2", "invt": "2"},
        headers={"Referer": "https://quote.eastmoney.com/"},
        timeout=8,
    )
    print(f"  push2   : {'OK' if r is not None else 'FAIL'}")


def _startup_scope_label(selected_sources: list[str], include_context: bool) -> str:
    source_scope = f"--only {','.join(selected_sources)}" if selected_sources else "默认源集合"
    context_scope = "启用" if include_context else "跳过"
    return f"源范围: {source_scope} | 市场上下文: {context_scope}"


def _refresh_closed_snapshot_validations(out_dir, data_date, pool, snapshot_meta):
    return CAPA._refresh_closed_snapshot_validations(
        out_dir=out_dir,
        data_date=data_date,
        pool=pool,
        snapshot_meta=snapshot_meta,
        latest_trading_day_str=_last_trading_day_str,
    )


def _refresh_field_evidence_coverage(out_dir, snapshot_meta):
    return CAPA._refresh_field_evidence_coverage(out_dir, snapshot_meta, out_base=OUT_BASE)


def build_collectors() -> Dict[str, Callable[..., Dict[str, Any]]]:
    """Return the single runtime source-to-collector map.

    Collector registration is source-level and independent of field semantic status.
    A verified field remains collected; field status controls collision targeting only.
    """
    return {
        "zhb": collect_zhb,
        "tdx": collect_tdx,
        "eltdx": collect_eltdx,
        "tencent": collect_tencent,
        "push2": collect_push2,
        "sina": collect_sina,
        "sina_extended": collect_sina_extended,
        "axdata": collect_axdata,
        "market_sources": collect_market_sources,
        "kpl": collect_kpl_detail,
        "kph": collect_kph_history,
        "tdx_f10": collect_tdx_f10,
        "fuyao": collect_fuyao,
        "em_kline_f61": collect_em_kline_f61,
        "em_fund_flow": collect_em_fund_flow,
        "ulist239": collect_ulist239,
        "push2ex": collect_push2ex,
        "em_hot": collect_em_hot,
        "cls": collect_cls,
        "datacenter": collect_datacenter,
        "tdx_f10_more": collect_tdx_f10_more,
        "cninfo": collect_cninfo,
        "reports": collect_reports,
        "ftshare": collect_ftshare,
        "ftshare_rest": collect_ftshare_rest,
        "baidu": collect_baidu,
        "clist": collect_clist,
        "slist": collect_slist,
        "exchange": collect_exchange,
        "event_dc": collect_event_dc,
        "macro_dc": collect_macro_dc,
        "research_sina": collect_research_sina,
        "etf": collect_etf,
        "news_wscn_cctv": collect_news_wscn_cctv,
        "sse_e_interaction": collect_sse_e_interaction,
        "st_list": collect_st_list,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="字段验证采集")
    # V17.4.x: 默认数据日=最近交易日(而非运行日) —— 周末/法定节假日运行时自动回退上一交易日,
    # 使文件夹名恒为"实际数据日"(收盘数据所属交易日), 根除"文件夹名是假日但数据是上一交易日"的根因。
    ap.add_argument("--date", default="", help="数据日期 YYYYMMDD；行情日按交易日校验")
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="强制覆盖重采: 清空既有同数据日目标源 raw_*.json 与 meta 记录后重新采集; "
        "默认: 盘后→盘后幂等跳过, 盘中→盘后自动刷新为收盘数据, 盘中→盘中跳过",
    )
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--only",
        default="",
        help="只采指定源(逗号分隔；可显式选择 pending_validation 源进行限量验证)",
    )
    ap.add_argument(
        "--include-context",
        action="store_true",
        help="额外采集龙虎榜/人气榜等市场上下文；--only 明确指定 exchange 或 em_hot 时自动启用",
    )
    ap.add_argument(
        "--refresh-pool",
        action="store_true",
        help="采集前刷新动态层(从涨停池选 5 只连板/新股/涨停写回 pool.json)",
    )
    ap.add_argument(
        "--refresh-pool-only", action="store_true", help="只刷新动态层并写回 pool.json, 不执行采集"
    )
    ap.add_argument(
        "--eltdx-lite",
        action="store_true",
        help="eltdx 采集瘦身: 跳过与 tdx 源冗余的 kline_day/finance_batch, "
        "仅采 quote_snapshot+shortline+连板天梯(对撞真正消费项), 大幅加速每日字段对撞采集",
    )
    args = ap.parse_args()

    date_was_explicit = bool(args.date)
    if not args.date:
        args.date = _last_trading_day_str()
    selected_only = [name.strip() for name in args.only.split(",") if name.strip()]
    include_context = args.include_context or bool(set(selected_only) & CONTEXT_ONLY_SOURCES)
    try:
        _, data_date_domain = _validate_capture_data_date(args.date, selected_only)
    except ValueError as exc:
        ap.error(str(exc))
    if data_date_domain == "calendar" and (args.refresh_pool or args.refresh_pool_only):
        ap.error("新闻/公告自然日采集不能同时刷新股票池")

    if args.refresh_pool_only:
        picks = refresh_dynamic_layer(trade_date=args.date)
        if picks:
            print(
                "动态层候选:\n" + "\n".join(f"  {p['code']} {p['name']} {p['tags']}" for p in picks)
            )
        else:
            print("动态层刷新未产生候选(保留旧层)。")
        return

    if args.refresh_pool:
        refresh_dynamic_layer(trade_date=args.date)

    pool = load_pool()
    if args.dry_run:
        dry_run(pool)
        return

    t0 = time.time()
    startup_scope = _startup_scope_label(selected_only, include_context)
    print(
        f"▶ 采集开始: 数据日={args.date} (运行日={datetime.now().strftime('%Y%m%d')}) | 股票 {len(pool)} 只 | {startup_scope}",
        flush=True,
    )

    out_dir = os.path.join(OUT_BASE, args.date)
    os.makedirs(out_dir, exist_ok=True)
    meta_path = os.path.join(out_dir, "meta.json")

    _now = datetime.now()
    meta = {
        "date": args.date,
        "data_date": args.date,
        "data_date_domain": data_date_domain,
        "date_selection": "explicit" if date_was_explicit else "latest_completed_session",
        "capture_date": _now.strftime("%Y%m%d"),
        "run_date": _now.strftime("%Y%m%d"),
        "run_datetime": _now.strftime("%Y-%m-%d %H:%M:%S"),
        "start": _now.strftime("%Y-%m-%d %H:%M:%S"),
        "market_phase": (
            "calendar"
            if data_date_domain == "calendar"
            else "closed" if _is_closed_phase_now(args.date) else "intraday"
        ),
        "capture_market_phase": _capture_market_phase(_now),
        "sources": {},
        "source_as_of_dates": {},
    }
    # V17.2.9 修复: --only 增量采集必须**合并**已有 meta.json, 而非整份覆盖 ——
    # 否则未参与本次采集的源会从元数据中消失(曾致 22 源元数据被单源覆写)。
    if args.only and os.path.isfile(meta_path):
        try:
            with open(meta_path, encoding="utf-8") as f:
                _prev = json.load(f)
            if isinstance(_prev.get("sources"), dict):
                meta["sources"].update(_prev["sources"])
            previous_source_meta = _prev.get("sources")
            previous_sources = (
                set(previous_source_meta) if isinstance(previous_source_meta, dict) else set()
            )
            previous_raw_sources = {
                os.path.basename(path)[len("raw_") : -len(".json")]
                for path in glob.glob(os.path.join(out_dir, "raw_*.json"))
            }
            previous_market_sources = {
                source
                for source in previous_sources | previous_raw_sources
                if source not in EVENT_ONLY_CAPTURE_SOURCES
            }
            if data_date_domain == "calendar" and previous_market_sources:
                previous_data_date = _prev.get("data_date")
                if previous_data_date:
                    meta["data_date"] = previous_data_date
                else:
                    meta.pop("data_date", None)
                meta["data_date_domain"] = "mixed"
            if isinstance(_prev.get("schemes"), dict):
                meta["schemes"] = dict(_prev["schemes"])
            if isinstance(_prev.get("source_as_of_dates"), dict):
                meta["source_as_of_dates"] = dict(_prev["source_as_of_dates"])
            if isinstance(_prev.get("axdata_validation"), dict):
                meta["axdata_validation"] = _prev["axdata_validation"]
            for _k in ("start", "zhb_data_date", "levistock_validation"):
                if _prev.get(_k):
                    meta[_k] = _prev[_k]
            if _prev.get("end"):
                meta["prev_end"] = _prev["end"]
        except Exception as e:
            print(f"  ⚠ 已有 meta.json 读取失败, 本次将整份覆盖: {e}", flush=True)
    meta["only"] = args.only or None
    meta["include_context"] = include_context

    collectors = build_collectors()
    if args.only:
        unknown_sources = set(selected_only) - set(collectors)
        if unknown_sources:
            ap.error("--only 含未知源: " + ", ".join(sorted(unknown_sources)))
        collectors = {k: v for k, v in collectors.items() if k in selected_only}
    active_source_names = set(collectors)
    if not include_context:
        active_source_names.difference_update(CONTEXT_ONLY_SOURCES)
    source_names_to_refresh = set(active_source_names)
    if not args.only:
        # Pending endpoint probes are not part of the default network pass; preserve
        # any prior explicit probe file and its evidence when refreshing other sources.
        source_names_to_refresh.difference_update(NON_RAW_SOURCE_STATUS)
    raw_clear_source_names = set(source_names_to_refresh)
    if not include_context:
        raw_clear_source_names.difference_update(CONTEXT_RAW_PATHS)
    existing_source_names = {
        os.path.basename(path)[len("raw_") : -len(".json")]
        for path in glob.glob(os.path.join(out_dir, "raw_*.json"))
    }
    combined_source_names = set(meta.get("sources", {})) | existing_source_names | set(collectors)
    has_event_sources = bool(combined_source_names & EVENT_ONLY_CAPTURE_SOURCES)
    has_market_sources = bool(combined_source_names - EVENT_ONLY_CAPTURE_SOURCES)
    if has_event_sources and has_market_sources:
        meta["data_date_domain"] = "mixed"
    elif has_event_sources:
        meta["data_date_domain"] = "calendar"
    else:
        meta["data_date_domain"] = "trading"

    # ── 幂等/覆盖：文件夹名已=数据日(交易日)。
    #    盘后运行发现盘中已采快照 → 默认刷新为收盘数据(覆盖重采); 盘后→盘后默认幂等跳过; 盘中→盘中默认跳过。
    #    --overwrite 强制重采(上方已清空目标源)。假日重复采集无同名覆盖问题(目录名=数据日)。 ──
    _existing_raws = sorted(glob.glob(os.path.join(out_dir, "raw_*.json")))
    if args.overwrite:
        # 仅清空本次将重采源(raw + meta 记录), 保留其他源采集物, 避免误删增量补采之外的数据
        _clear_raw = {os.path.join(out_dir, f"raw_{n}.json") for n in raw_clear_source_names}
        for _p in _existing_raws:
            if _p in _clear_raw:
                try:
                    os.remove(_p)
                except Exception:
                    pass
        if os.path.isfile(meta_path):
            try:
                _m = json.load(open(meta_path, encoding="utf-8"))
                for _n in [k for k in _m.get("sources", {}) if k in source_names_to_refresh]:
                    del _m["sources"][_n]
                with open(meta_path, "w", encoding="utf-8") as _f:
                    json.dump(_m, _f, ensure_ascii=False, indent=1)
            except Exception:
                try:
                    os.remove(meta_path)
                except Exception:
                    pass
        _existing_raws = sorted(glob.glob(os.path.join(out_dir, "raw_*.json")))
    if not args.only and (
        _existing_raws or any(source in NON_RAW_SOURCE_STATUS for source in collectors)
    ):
        _have = {os.path.basename(p)[len("raw_") : -len(".json")] for p in _existing_raws}
        snapshot_meta = {}
        if os.path.isfile(meta_path):
            try:
                with open(meta_path, encoding="utf-8") as stream:
                    candidate_meta = json.load(stream)
                if isinstance(candidate_meta, dict):
                    snapshot_meta = candidate_meta
                else:
                    print("  ⚠ 已有 meta.json 结构异常，将按需重采。", flush=True)
            except (OSError, json.JSONDecodeError) as exc:
                print(f"  ⚠ 已有 meta.json 不可读取，将按需重采: {exc}", flush=True)
        if _has_complete_snapshot(
            collectors, snapshot_meta, out_dir, pool, include_context=include_context
        ):
            if data_date_domain == "calendar":
                _refresh_field_evidence_coverage(out_dir, snapshot_meta)
                print(
                    f"⏭ 自然日数据 {args.date} 已有完整源快照，默认幂等跳过；如需重采请加 --overwrite。",
                    flush=True,
                )
                return
            # 完整度判定: 盘中快照(收盘前)应被盘后重采刷新为收盘数据, 避免对撞污染
            _existing_closed = _is_closed_phase_existing(meta_path, args.date)
            _new_closed = _is_closed_phase_now(args.date)
            if _existing_closed and _new_closed:
                _refresh_closed_snapshot_validations(
                    out_dir=out_dir,
                    data_date=args.date,
                    pool=pool,
                    snapshot_meta=snapshot_meta,
                )
                _refresh_field_evidence_coverage(out_dir, snapshot_meta)
                print(
                    f"⏭ 数据日 {args.date} 已存在完整(盘后)采集物 (raw {len(_existing_raws)} 个, 源: {sorted(_have)}), "
                    f"主采集幂等跳过；只刷新每日验证摘要，已有候选样本不会重复请求。",
                    flush=True,
                )
                return
            if (not _existing_closed) and (not _new_closed):
                _refresh_field_evidence_coverage(out_dir, snapshot_meta)
                print(
                    f"⏭ 数据日 {args.date} 已存在盘中快照且本次仍为盘中运行, 默认幂等跳过。",
                    flush=True,
                )
                return
            # 已有=盘中快照, 本次=盘后运行 → 刷新为收盘数据(覆盖重采目标源)
            print(
                f"🔄 数据日 {args.date} 现有采集物为盘中快照(非收盘), 本次盘后运行将刷新为收盘数据。",
                flush=True,
            )
            _clear_raw = {os.path.join(out_dir, f"raw_{n}.json") for n in raw_clear_source_names}
            for _p in _existing_raws:
                if _p in _clear_raw:
                    try:
                        os.remove(_p)
                    except Exception:
                        pass
            if os.path.isfile(meta_path):
                try:
                    _m = json.load(open(meta_path, encoding="utf-8"))
                    for _n in [k for k in _m.get("sources", {}) if k in source_names_to_refresh]:
                        del _m["sources"][_n]
                    with open(meta_path, "w", encoding="utf-8") as _f:
                        json.dump(_m, _f, ensure_ascii=False, indent=1)
                except Exception:
                    try:
                        os.remove(meta_path)
                    except Exception:
                        pass
            # 清空后 fall through 进入采集

    axdata_identity_plan: dict[str, Any] = {"status": "not_requested", "endpoints": {}}
    if {"axdata", "kph"} & set(collectors):
        try:
            try:
                from axdata_daily_validation import get_axdata_capture_identity_plan
            except ModuleNotFoundError:
                from scripts.axdata_daily_validation import get_axdata_capture_identity_plan

            axdata_identity_plan = get_axdata_capture_identity_plan(
                args.date,
                force_reprobe=args.overwrite,
            )
        except Exception as exc:
            # An unexpected policy error must not silently suppress production data.
            axdata_identity_plan = {
                "status": "failed_open",
                "reason": f"{type(exc).__name__}: {exc}"[:240],
                "endpoints": {},
            }
        meta["axdata_capture_identity_plan"] = axdata_identity_plan
    axdata_identity_endpoints: dict[str, Any] = {}
    endpoint_candidates = axdata_identity_plan.get("endpoints")
    if isinstance(endpoint_candidates, dict):
        axdata_identity_endpoints = endpoint_candidates

    collected_data: Dict[str, Any] = {}
    for name, fn in collectors.items():
        if name in CONTEXT_ONLY_SOURCES and not include_context:
            meta["sources"][name] = {
                "scheme": SOURCE_SCHEME.get(name, "unknown"),
                "ok": True,
                "status": "context_only",
                "context_excluded_paths": CONTEXT_EXCLUDED_PATHS[name],
                "reason": "默认字段破解采集不请求纯市场上下文源",
                "secs": 0.0,
            }
            print(f"  ⊘ {name}: context_only (默认跳过)", flush=True)
            continue
        try:
            t1 = time.time()
            meta["source_as_of_dates"].pop(name, None)
            # V17.2.28: eltdx 瘦身开关——仅 eltdx 支持 lite(跳过冗余/能力登记载荷)
            if name == "eltdx":
                data = fn(pool, lite=args.eltdx_lite)
            elif name == "market_sources":
                data = fn(
                    pool,
                    include_context=include_context,
                    include_kpl_detail=False,
                    trade_date=args.date,
                )
                try:
                    try:
                        from levistock_daily_probe import run_levistock_daily_probe
                    except ModuleNotFoundError:
                        from scripts.levistock_daily_probe import run_levistock_daily_probe

                    _levistock_probe = run_levistock_daily_probe(
                        out_dir=out_dir,
                        data_date=args.date,
                        latest_completed_trade_date=_last_trading_day_str(),
                        # market_sources contains trading-date data even when full
                        # meta is mixed with natural-day event sources.
                        data_date_domain="trading",
                        market_phase=meta.get("market_phase", "unknown"),
                        only=args.only or None,
                        market_data=data,
                        pool=pool,
                    )
                    meta["levistock_daily_candidate"] = {
                        key: value for key, value in _levistock_probe.items() if key != "payload"
                    }
                    if isinstance(data, dict):
                        _source_meta = data.setdefault("__source_meta__", {})
                        if isinstance(_source_meta, dict):
                            _source_meta["levistock_daily_candidate"] = {
                                key: value
                                for key, value in _levistock_probe.items()
                                if key != "payload"
                            }
                except Exception as exc:
                    # Candidate verification is auxiliary; it cannot invalidate the primary capture.
                    if isinstance(data, dict):
                        _source_meta = data.setdefault("__source_meta__", {})
                        if isinstance(_source_meta, dict):
                            _source_meta["levistock_daily_candidate"] = {
                                "status": "failed_open",
                                "reason": f"probe_integration_error:{type(exc).__name__}",
                                "request_count": 0,
                            }
                    print(f"  ⚠ Levistock 候选核验失败，不影响市场源采集: {exc}", flush=True)
            elif name == "kpl":
                data = fn(capture_date=args.date)
            elif name == "kph":
                data = fn(
                    capture_date=args.date,
                    prior_market_sources=collected_data.get("market_sources"),
                    identity_policy=axdata_identity_endpoints.get("kph_limit_up_history"),
                )
            elif name == "axdata":
                data = fn(
                    pool,
                    identity_policy=axdata_identity_endpoints.get("stock_shortline_indicators_tdx"),
                )
            elif name == "fuyao":
                data = fn(pool, include_context=include_context)
            elif name == "baidu":
                # The Baidu endpoint is pending validation and is probed only when
                # the caller explicitly selects it with --only baidu.
                data = fn(pool, probe="baidu" in selected_only)
            elif name == "ftshare_rest":
                # This live-snapshot contract must validate against the selected
                # effective trading date; calling it with only the pool always fails
                # before sending a request.
                data = fn(pool, data_date=args.date)
            else:
                data = fn(pool)
            if isinstance(data, dict):
                collected_data[name] = data
            # V17.2.12 主字典对齐: registry 已登记但本脚本暂无 producer 的源返回 __unwired__ 占位,
            # 显式记为 unwired/deprecated(区别于 ok/partial/failed), 不写 raw 文件、不计入异常源清单。
            _uw = data.get("__unwired__") if isinstance(data, dict) else None
            if _uw:
                _kind = _uw if _uw in {"deprecated", "pending_validation"} else "unwired"
                meta["sources"][name] = {
                    "scheme": SOURCE_SCHEME.get(name, "unknown"),
                    "ok": False,
                    "status": _kind,
                    "registry_name": data.get("registry_name"),
                    "section": data.get("section"),
                    "reason": data.get("reason"),
                    "previous_probe_snapshot_preserved": (
                        _kind == "pending_validation"
                        and os.path.isfile(os.path.join(out_dir, f"raw_{name}.json"))
                    ),
                    "secs": round(time.time() - t1, 1),
                }
                print(f"  ⊘ {name}: {_kind} (按来源生命周期策略不发默认请求)", flush=True)
                continue
            preserved_context_paths: List[str] = []
            if not include_context and name in CONTEXT_RAW_PATHS and isinstance(data, dict):
                preserved_context_paths, preservation_warnings = _preserve_context_paths(
                    name, data, out_dir
                )
                for warning in preservation_warnings:
                    print(f"  ⚠ {warning}", flush=True)
            # A 方案: 标注字段体系(scheme)血缘, 写入 raw 文件顶层 + meta, 供对撞工具/lint 校验
            _scheme = SOURCE_SCHEME.get(name, "unknown")
            if isinstance(data, dict):
                data["scheme"] = _scheme
            # V17.2.7: 字段级 raw/computed + 窗口溯源元数据, 嵌入 raw 文件顶层 `field_meta` 键,
            # 使原始采集物自带字段身份溯源(供跨源对撞/血缘分析消费)。懒加载, 失败不影响采集。
            _fm = None
            try:
                from field_meta import field_meta_block

                _fm = field_meta_block(name)
            except Exception:
                _fm = None
            if _fm is not None and isinstance(data, dict):
                data["field_meta"] = _fm
            path = os.path.join(out_dir, f"raw_{name}.json")
            _zhb_refresh_note = None
            _write_raw = True
            if name == "zhb":
                data, _write_raw, _zhb_refresh_note = _retain_current_zhb_snapshot(
                    data, path, args.date
                )
                if isinstance(data, dict):
                    collected_data[name] = data
            if _write_raw:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=1, default=str)
            # 采集函数会**内部吞异常**并返回 {"__error__": ...} 占位，预期跳过用 __skipped__ 标记，
            # 旧逻辑只要 fn(pool) 不抛异常就记 ok=True(曾致 em_kline_f61 20/20 全失败仍标 ok)。
            # 现按 __error__ 判定 status，并在元数据/日志中单独报告 __skipped__。
            _ok, _info = assess_result(
                data,
                expected_symbols=_source_expected_codes(name, pool),
                required_paths=_source_required_paths(name, include_context),
            )
            if name == "zhb":
                _ok, _info = _apply_zhb_freshness(_ok, _info, data, args.date)
                if _zhb_refresh_note is not None:
                    _info["refresh_attempt"] = _zhb_refresh_note
            _as_of_date = _source_as_of_date(name, data)
            _entry = {
                "scheme": _scheme,
                "ok": _ok,
                "field_meta": _fm is not None,
                "secs": round(time.time() - t1, 1),
                "file": path,
            }
            if _as_of_date:
                _entry["as_of_date"] = _as_of_date
                meta["source_as_of_dates"][name] = _as_of_date
            _entry.update(_info)
            if name in {"axdata", "kph"} and isinstance(data, dict):
                _identity = data.get("__source_meta__")
                if isinstance(_identity, dict) and isinstance(
                    _identity.get("identity_validation_suppression"), dict
                ):
                    _entry["identity_validation_suppression"] = _identity[
                        "identity_validation_suppression"
                    ]
            if not include_context and name in CONTEXT_EXCLUDED_PATHS:
                _entry["context_excluded_paths"] = CONTEXT_EXCLUDED_PATHS[name]
            if preserved_context_paths:
                _entry["preserved_context_paths"] = preserved_context_paths
            meta["sources"][name] = _entry
            _skip_count = _entry.get("n_skipped", 0)
            _refresh_attempt = _entry.get("refresh_attempt")
            if _refresh_attempt:
                if _refresh_attempt["status"] == "noncurrent_refresh_rejected":
                    _refresh_message = (
                        f"非最新回退未写入，保留现有 ZHB 数据 "
                        f"{_refresh_attempt['retained_as_of_date']}"
                    )
                else:
                    _refresh_message = _refresh_attempt["reason"]
                print(
                    f"  ⚠ {name}: {_entry['secs']}s | {_entry['status']} | "
                    f"{_refresh_message} | 错误 {_entry['n_error']} | "
                    f"缺股票 {_entry.get('n_missing_stocks', 0)}",
                    flush=True,
                )
            elif _ok:
                _skip_summary = f" | 跳过 {_skip_count} 处" if _skip_count else ""
                print(f"  ✔ {name}: {_entry['secs']}s{_skip_summary}", flush=True)
            elif _entry.get("freshness_issue"):
                print(
                    f"  ⚠ {name}: {_entry['secs']}s | {_entry['status']} | "
                    f"{_entry['freshness_issue']} | 错误 {_entry['n_error']} | "
                    f"缺股票 {_entry.get('n_missing_stocks', 0)}",
                    flush=True,
                )
            else:
                _nt = _entry.get("n_total")
                _cnt = f"{_entry['n_error']}/{_nt}" if _nt else str(_entry["n_error"])
                print(
                    f"  ⚠ {name}: {_entry['secs']}s | {_entry['status']} | "
                    f"{_cnt} 处错误 | 缺股票 {_entry.get('n_missing_stocks', 0)} | "
                    f"deferred {_entry.get('n_deferred', 0)} | 跳过 {_skip_count} 处 | "
                    f"{_entry.get('error_sample') or _entry.get('skip_sample') or _entry.get('missing_stocks_sample', '')}",
                    flush=True,
                )
        except Exception as e:
            meta["sources"][name] = {
                "scheme": SOURCE_SCHEME.get(name, "unknown"),
                "ok": False,
                "error": str(e)[:300],
            }
            print(f"  ✖ {name}: {e}", flush=True)

    # Persist AxData route bans independently of the daily validation eligibility
    # gate, so partial `--only` runs cannot forget a 403/429 observation.
    if {"axdata", "kph"} & set(collectors):
        try:
            try:
                from axdata_daily_validation import record_axdata_capture_rate_limits
            except ModuleNotFoundError:
                from scripts.axdata_daily_validation import record_axdata_capture_rate_limits

            meta["axdata_capture_endpoint_identities"] = record_axdata_capture_rate_limits(
                data_date=args.date,
                source_meta=meta.get("sources", {}),
                collected_data=collected_data,
                requested_sources=set(collectors),
            )
        except Exception as exc:
            meta["axdata_capture_endpoint_identities"] = {
                "status": "failed_open",
                "reason": f"{type(exc).__name__}: {exc}"[:240],
            }
            print(f"  ⚠ AxData 路由状态记录失败: {exc}", flush=True)

    # AxData reconciliation stays inside the daily capture loop. Passive route
    # checks use successful, explicitly selected source pairs and their shared
    # effective trade date. The whitelisted active probe runs at most once per
    # latest completed data date in a stable window. It never updates dictionary status.
    try:
        try:
            from axdata_daily_validation import run_axdata_daily_validation
        except ModuleNotFoundError:
            from scripts.axdata_daily_validation import run_axdata_daily_validation

        meta["axdata_validation"] = run_axdata_daily_validation(
            data_date=args.date,
            data_date_domain=meta.get("data_date_domain", data_date_domain),
            market_phase=meta.get("market_phase", "unknown"),
            latest_completed_trade_date=_last_trading_day_str(),
            only=args.only,
            out_dir=out_dir,
            pool=pool,
            source_meta=meta.get("sources", {}),
            requested_sources=set(collectors),
        )
        _validation_status = meta["axdata_validation"].get("status")
        if _validation_status != "not_eligible":
            _validation_probe = meta["axdata_validation"].get("probe", {})
            _validation_fields = _validation_probe.get("compared_fields")
            _validation_comparison = (
                f" | 字段相等 {_validation_probe.get('equal_fields', 0)}/" f"{_validation_fields}"
                if _validation_fields is not None
                else ""
            )
            _validation_identity = _validation_probe.get("source_identity")
            if not isinstance(_validation_identity, dict):
                _validation_identity = {}
            _identity_status = _validation_identity.get("status", "未确认")
            _identity_recheck = _validation_identity.get("next_recheck_in_data_dates")
            _identity_label = f" | 来源身份 {_identity_status}"
            if _identity_recheck is not None:
                _identity_label += f"（{_identity_recheck} 个数据日后复验）"
            print(
                f"  AxData 验证: {_validation_status} | "
                f"接口 {_validation_probe.get('interface_id') or '—'} | "
                f"代码 {_validation_probe.get('code') or '—'}"
                f"{_validation_comparison}{_identity_label} | "
                f"{meta['axdata_validation'].get('file') or ''}",
                flush=True,
            )
    except Exception as exc:
        # Reconciliation is auxiliary: an error must not discard otherwise
        # successful daily captures or prevent their metadata from being saved.
        meta["axdata_validation"] = {
            "status": "failed_open",
            "error": str(exc)[:300],
        }
        print(f"  ⚠ AxData 验证流程失败，不影响原始采集: {exc}", flush=True)

    # Levistock is a multi-provider client, not an independent source family. The
    # validator reuses captured CLS/KPH data; the bounded candidate probe is recorded
    # separately and never changes dictionary status.
    if not args.only or "market_sources" in selected_only:
        try:
            try:
                from levistock_daily_validation import run_levistock_daily_validation
            except ModuleNotFoundError:
                from scripts.levistock_daily_validation import run_levistock_daily_validation

            meta["levistock_validation"] = run_levistock_daily_validation(
                out_dir=out_dir,
                data_date=args.date,
                latest_completed_trade_date=_last_trading_day_str(),
                data_date_domain="trading",
                market_phase=meta.get("market_phase", "unknown"),
                only=args.only or None,
                source_meta=meta.get("sources", {}),
                candidate_probe_meta=meta.get("levistock_daily_candidate"),
            )
            _levistock_validation = meta["levistock_validation"]
            _levistock_methods = _levistock_validation.get("methods", {})
            _levistock_fields = sum(
                int(item.get("field_count", 0))
                for item in _levistock_methods.values()
                if isinstance(item, dict)
            )
            print(
                f"  Levistock 核验: {_levistock_validation.get('status')} | "
                f"字段 {_levistock_fields} | "
                f"核验器请求 {_levistock_validation.get('network_requests_added', 0)} | "
                f"轮换请求 {_levistock_validation.get('capture_probe_request_count', 0)} | "
                f"{_levistock_validation.get('file') or ''}",
                flush=True,
            )
        except Exception as exc:
            # Evidence generation must never discard successfully captured raw data.
            meta["levistock_validation"] = {
                "status": "failed_open",
                "error": str(exc)[:300],
                "network_requests_added": 0,
            }
            print(f"  ⚠ Levistock 核验流程失败，不影响原始采集: {exc}", flush=True)

    meta["end"] = time.strftime("%Y-%m-%d %H:%M:%S")
    meta["total_secs"] = round(time.time() - t0, 1)
    # A 方案: 本日各源字段体系(scheme)血缘总览, 供对撞工具/lint 直接读取
    # V17.2.9: 与已有 schemes 合并(--only 时不得丢失未采源的血缘标注)
    meta["schemes"] = {
        **(meta.get("schemes") or {}),
        **{k: SOURCE_SCHEME.get(k, "unknown") for k in collectors},
    }
    # V17.0.10: 记录 ZHB 数据日期(T-1 规则)——对撞破解必须先核对此字段再定对撞报告日期
    try:
        _zhb = json.load(open(os.path.join(out_dir, "raw_zhb.json"), encoding="utf-8")).get(
            "zhb_date", ""
        )
        meta["zhb_data_date"] = _zhb or meta.get("zhb_data_date", "")
    except Exception:
        meta.setdefault("zhb_data_date", "")

    # V17.2.9: 本次运行的源级健康度汇总(--only 时只统计本次 collectors, 不误报历史源)
    # V17.2.12: unwired/deprecated 为 registry 已登记但无 producer / 已废弃的预期态, 不计入异常源。
    def _is_abnormal(s: dict) -> bool:
        st = s.get("status")
        if st in ("ok", "unwired", "deprecated", "context_only"):
            return False
        return not s.get("ok", True)

    _bad = [k for k in collectors if _is_abnormal(meta["sources"].get(k, {}))]
    meta["run"] = {
        "only": args.only or None,
        "include_context": include_context,
        "n_sources": len(collectors),
        "context_only_sources": [
            name for name in collectors if name in CONTEXT_ONLY_SOURCES and not include_context
        ],
        "n_abnormal": len(_bad),
        "abnormal": _bad,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    _refresh_field_evidence_coverage(out_dir, meta)
    print(
        f"✔ 完成: {out_dir} | 总耗时 {meta['total_secs']}s | ZHB={meta.get('zhb_data_date')}",
        flush=True,
    )
    if _bad:
        print(f"⚠ 本次存在异常源 {len(_bad)}/{len(collectors)}: {', '.join(_bad)}", flush=True)


if __name__ == "__main__":
    main()

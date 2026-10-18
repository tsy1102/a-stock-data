# -*- coding: utf-8 -*-
"""FTShare MCP 客户端统一封装（V17.0.7 新源——字典 §12.20，实测后采纳）。

接入形态：公共网关 MCP Streamable HTTP(JSON-RPC)，兼容无鉴权会话和可选环境变量 API Key。
支持有状态与无状态会话，90 分钟续期；HTTP/JSON-RPC/工具错误保留诊断。
限流：模块级所有 POST 至少间隔 500ms；403/429 或连续三次错误时停止请求。
服务端明确返回匿名额度等待时立即停止请求，并将冷却截止时间保存在 Git 忽略的项目 .tmp/；配置 API Key 可绕过匿名额度冷却。
"""

from typing import Any, Dict, List, Optional, cast
from datetime import date
import json
import logging
import math
import os
from pathlib import Path
import re
import threading
import time
import uuid

import requests

_BASE = "https://market.ft.tech/gateway/mcp"
_HEADERS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
_SID: Optional[str] = None
_SESSION_READY = False
_LAST_INIT: float = 0.0
_SESSION_TTL = 5400  # 90 min
_LAST_POST: float = 0.0
_MIN_POST_INTERVAL = 0.5
_MAX_CONSECUTIVE_ERRORS = 3
_MAX_DIAGNOSTICS = 32
_RPC_LOCK = threading.RLock()
_DIAGNOSTICS: List[Dict[str, Any]] = []
_CONSECUTIVE_ERRORS = 0
_BLOCKED_REASON: Optional[str] = None
_BLOCKED_UNTIL: Optional[float] = None
_BLOCKED_REQUIRES_API_KEY = False
_RATE_LIMIT_STATE_PATH = Path(__file__).resolve().parents[1] / ".tmp" / "ftshare_rate_limit.json"
_LOGGER = logging.getLogger(__name__)
_RATE_LIMIT_WAIT = re.compile(
    r"请等待\s*(?:(\d+)\s*天)?\s*(?:(\d+)\s*小时)?\s*(?:(\d+)\s*分钟)?\s*(?:(\d+)\s*秒)?\s*后再试"
)
_GOODWILL_LOCK = threading.Lock()
_GOODWILL_BY_CODE: Dict[str, List[Dict[str, Any]]] = {}
_GOODWILL_CACHE_EXPIRES_AT = 0.0
_GOODWILL_CACHE_TTL = 6 * 60 * 60
_GOODWILL_FAILURE_CACHE_TTL = 60
_GOODWILL_PAGE_SIZE = 500
_GOODWILL_MAX_PAGES = 100
_GGMX_PAGE_SIZE = 200
_LIMIT_LIST_PAGE_SIZE = 100


def _parse_upstream_retry_after(message: str) -> Optional[int]:
    """Extract an explicit wait from a quota/rate-limit response, in seconds."""
    lowered = message.casefold()
    quota_markers = ("最多访问", "访问额度", "限流", "rate limit", "quota")
    if not any(marker in lowered for marker in quota_markers):
        return None
    match = _RATE_LIMIT_WAIT.search(message)
    if match is None:
        return None
    days, hours, minutes, seconds = (int(value or 0) for value in match.groups())
    wait_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
    return wait_seconds if wait_seconds > 0 else None


def _write_rate_limit_state(blocked_until: float, requires_api_key: bool) -> None:
    """Persist only anonymous-quota cooldown metadata under the ignored project temp dir."""
    path = _RATE_LIMIT_STATE_PATH
    temp_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    payload = {
        "version": 1,
        "blocked_until_epoch": blocked_until,
        "requires_api_key": requires_api_key,
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temp_path.open("w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    except OSError as exc:
        _LOGGER.warning("Could not persist FTShare cooldown state at %s: %s", path, exc)
        try:
            temp_path.unlink(missing_ok=True)
        except OSError as cleanup_exc:
            _LOGGER.warning(
                "Could not remove partial FTShare cooldown file %s: %s", temp_path, cleanup_exc
            )


def _remove_rate_limit_state() -> None:
    try:
        _RATE_LIMIT_STATE_PATH.unlink(missing_ok=True)
    except OSError as exc:
        _LOGGER.warning(
            "Could not remove expired FTShare cooldown state at %s: %s",
            _RATE_LIMIT_STATE_PATH,
            exc,
        )


def _rate_limit_active() -> bool:
    """Return true when an in-process or persisted upstream cooldown blocks requests."""
    global _BLOCKED_REASON, _BLOCKED_UNTIL, _BLOCKED_REQUIRES_API_KEY
    global _CONSECUTIVE_ERRORS, _SESSION_READY, _SID
    with _RPC_LOCK:
        api_key_present = bool(os.environ.get("FTSHARE_API_KEY", "").strip())
        now = time.time()
        if _BLOCKED_UNTIL is not None:
            if _BLOCKED_REQUIRES_API_KEY and api_key_present:
                _BLOCKED_REASON = None
                _BLOCKED_UNTIL = None
                _BLOCKED_REQUIRES_API_KEY = False
                _CONSECUTIVE_ERRORS = 0
                _SID = None
                _SESSION_READY = False
                return False
            if _BLOCKED_UNTIL > now:
                return True
            _BLOCKED_REASON = None
            _BLOCKED_UNTIL = None
            _BLOCKED_REQUIRES_API_KEY = False
            _CONSECUTIVE_ERRORS = 0
            _SID = None
            _SESSION_READY = False
            _remove_rate_limit_state()
        elif _BLOCKED_REASON:
            return True

        try:
            state = json.loads(_RATE_LIMIT_STATE_PATH.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return False
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            _BLOCKED_REASON = "persisted FTShare cooldown state is unreadable; inspect .tmp/ftshare_rate_limit.json"
            _SESSION_READY = False
            _LOGGER.error(
                "Cannot read FTShare cooldown state at %s: %s", _RATE_LIMIT_STATE_PATH, exc
            )
            return True

        if not isinstance(state, dict) or state.get("version") != 1:
            _BLOCKED_REASON = "persisted FTShare cooldown state has an unsupported format; inspect .tmp/ftshare_rate_limit.json"
            _SESSION_READY = False
            _LOGGER.error("Unsupported FTShare cooldown state format at %s", _RATE_LIMIT_STATE_PATH)
            return True
        try:
            blocked_until = float(state["blocked_until_epoch"])
        except (KeyError, TypeError, ValueError):
            _BLOCKED_REASON = "persisted FTShare cooldown state has no valid expiry; inspect .tmp/ftshare_rate_limit.json"
            _SESSION_READY = False
            _LOGGER.error("Invalid FTShare cooldown expiry at %s", _RATE_LIMIT_STATE_PATH)
            return True
        if not math.isfinite(blocked_until):
            _BLOCKED_REASON = "persisted FTShare cooldown expiry is not finite; inspect .tmp/ftshare_rate_limit.json"
            _SESSION_READY = False
            _LOGGER.error("Non-finite FTShare cooldown expiry at %s", _RATE_LIMIT_STATE_PATH)
            return True

        requires_api_key = bool(state.get("requires_api_key"))
        if requires_api_key and api_key_present:
            return False
        if blocked_until <= now:
            _remove_rate_limit_state()
            return False
        _BLOCKED_UNTIL = blocked_until
        _BLOCKED_REQUIRES_API_KEY = requires_api_key
        remaining = max(1, int(blocked_until - now))
        _BLOCKED_REASON = f"upstream quota cooldown active; retry in about {remaining}s"
        _SESSION_READY = False
        return True


def is_ftshare_enabled() -> bool:
    import os

    return os.environ.get("FTSHARE_ENABLED", "1") != "0"


def _parse(r: requests.Response) -> Optional[Dict[str, Any]]:
    """Parse one JSON-RPC response from either JSON or an SSE event stream."""
    content = getattr(r, "content", b"")
    txt = content.decode("utf-8", errors="replace") if isinstance(content, bytes) else str(content)
    try:
        obj = json.loads(txt)
        if isinstance(obj, dict) and ("result" in obj or "error" in obj):
            return obj
    except json.JSONDecodeError:
        pass

    events: List[str] = []
    current: List[str] = []
    for line in txt.splitlines():
        if line == "":
            if current:
                events.append("\n".join(current))
                current = []
        elif line.startswith("data:"):
            current.append(line[5:].lstrip())
    if current:
        events.append("\n".join(current))

    for event in events:
        try:
            obj = json.loads(event.strip())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and ("result" in obj or "error" in obj):
            return obj
    return None


def _record_failure(
    stage: str,
    message: str,
    status: Optional[int] = None,
    tool: Optional[str] = None,
    retry_after_seconds: Optional[int] = None,
) -> None:
    global _CONSECUTIVE_ERRORS, _BLOCKED_REASON, _BLOCKED_UNTIL
    global _BLOCKED_REQUIRES_API_KEY, _SESSION_READY
    with _RPC_LOCK:
        entry: Dict[str, Any] = {"stage": stage, "message": str(message).strip()[:180]}
        if status is not None:
            entry["status"] = status
        if tool:
            entry["tool"] = tool
        _DIAGNOSTICS.append(entry)
        del _DIAGNOSTICS[:-_MAX_DIAGNOSTICS]
        _CONSECUTIVE_ERRORS += 1
        if status in (403, 429):
            _BLOCKED_REASON = f"HTTP {status} at {stage}; further FTShare requests paused"
            _SESSION_READY = False
        elif retry_after_seconds is not None and retry_after_seconds > 0:
            _BLOCKED_UNTIL = time.time() + retry_after_seconds
            _BLOCKED_REQUIRES_API_KEY = not bool(os.environ.get("FTSHARE_API_KEY", "").strip())
            _BLOCKED_REASON = (
                f"upstream quota exhausted; retry after approximately {retry_after_seconds}s"
            )
            _SESSION_READY = False
            if _BLOCKED_REQUIRES_API_KEY:
                _write_rate_limit_state(_BLOCKED_UNTIL, requires_api_key=True)
        elif _CONSECUTIVE_ERRORS >= _MAX_CONSECUTIVE_ERRORS:
            _BLOCKED_REASON = (
                f"circuit breaker opened after {_CONSECUTIVE_ERRORS} consecutive failures"
            )
            _SESSION_READY = False


def _record_success() -> None:
    global _CONSECUTIVE_ERRORS
    with _RPC_LOCK:
        _CONSECUTIVE_ERRORS = 0


def _clear_diagnostics() -> None:
    """Clear the per-capture error list without resetting a source circuit breaker."""
    with _RPC_LOCK:
        _DIAGNOSTICS.clear()


def _ftshare_diagnostics_summary() -> str:
    with _RPC_LOCK:
        entries = list(_DIAGNOSTICS)
        blocked = _BLOCKED_REASON
    messages = []
    for entry in entries:
        parts = [str(entry.get("stage", "FTShare"))]
        if entry.get("tool"):
            parts.append(str(entry["tool"]))
        if entry.get("status") is not None:
            parts.append(f"HTTP {entry['status']}")
        parts.append(str(entry.get("message", "request failed")))
        messages.append(": ".join(parts))
    if blocked and not any(blocked in message for message in messages):
        messages.append(f"source paused: {blocked}")
    return "; ".join(messages[:8])[:1200]


def _request_stage(body: Dict[str, Any]) -> tuple[str, Optional[str]]:
    method = str(body.get("method", "unknown"))
    params = body.get("params")
    tool = None
    if method == "tools/call" and isinstance(params, dict):
        name = params.get("name")
        tool = str(name) if name else None
    return method, tool


def _wait_for_rate_limit() -> None:
    global _LAST_POST
    now = time.monotonic()
    elapsed = now - _LAST_POST
    if elapsed < _MIN_POST_INTERVAL:
        time.sleep(_MIN_POST_INTERVAL - elapsed)
    _LAST_POST = time.monotonic()


def _handle_response(
    response: requests.Response,
    stage: str,
    tool: Optional[str],
    include_session: bool,
    expect_empty_response: bool,
) -> Optional[Dict[str, Any]]:
    global _SID, _SESSION_READY
    status = getattr(response, "status_code", None)
    if not isinstance(status, int) or not 200 <= status < 300:
        _record_failure(stage, "HTTP request failed", status=status, tool=tool)
        if status == 404 and include_session and _SID:
            _SID = None
            _SESSION_READY = False
        return None

    if expect_empty_response:
        if not getattr(response, "content", b""):
            return {}
        _record_failure(stage, "notification returned an unexpected response body", tool=tool)
        return None

    obj = _parse(response)
    if obj is None:
        headers = getattr(response, "headers", {})
        content_type = headers.get("Content-Type", "unknown content type")
        _record_failure(
            stage,
            f"unrecognized MCP response ({content_type})",
            status=status,
            tool=tool,
        )
        return None
    if "error" in obj:
        error = obj.get("error")
        if isinstance(error, dict):
            error_code = str(error.get("code", "JSON-RPC error"))
            error_message = str(error.get("message", error_code))
            error_detail = f"{error_code}: {error_message}"
        else:
            error_message = str(error)
            error_detail = f"JSON-RPC error: {error_message}"
        retry_after_seconds = _parse_upstream_retry_after(error_message)
        _record_failure(
            stage,
            error_detail,
            tool=tool,
            retry_after_seconds=retry_after_seconds,
        )
        return obj
    if stage == "initialize":
        new_sid = getattr(response, "headers", {}).get("Mcp-Session-Id")
        _SID = str(new_sid) if new_sid else None
    return obj


def _post(
    body: Dict[str, Any],
    timeout: int = 60,
    *,
    include_session: bool = True,
    expect_empty_response: bool = False,
) -> Optional[Dict[str, Any]]:
    """POST one MCP message, enforce the shared rate limit, and record failures."""
    global _SID, _SESSION_READY
    stage, tool = _request_stage(body)
    with _RPC_LOCK:
        if _rate_limit_active():
            return None
        _wait_for_rate_limit()
        headers = dict(_HEADERS)
        api_key = os.environ.get("FTSHARE_API_KEY", "").strip()
        if api_key:
            headers["FTSHARE_API_KEY"] = api_key
        if include_session and _SID:
            headers["Mcp-Session-Id"] = _SID
        try:
            response = requests.post(
                _BASE,
                data=json.dumps(body).encode("utf-8"),
                headers=headers,
                timeout=timeout,
            )
        except Exception as exc:
            _record_failure(stage, f"{type(exc).__name__}: {exc}", tool=tool)
            return None
        return _handle_response(response, stage, tool, include_session, expect_empty_response)


def _reinit() -> bool:
    global _SID, _SESSION_READY, _LAST_INIT
    with _RPC_LOCK:
        if _BLOCKED_REASON:
            return False
        _SID = None
        _SESSION_READY = False
        body = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "a-stock-data", "version": "0.1"},
            },
        }
        obj = _post(body, timeout=30, include_session=False)
        if not isinstance((obj or {}).get("result"), dict):
            if obj is not None and "error" not in obj:
                _record_failure("initialize", "initialize response omitted result")
            return False

        notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        if (
            _post(
                notification,
                timeout=15,
                include_session=True,
                expect_empty_response=True,
            )
            is None
        ):
            return False
        _SESSION_READY = True
        _LAST_INIT = time.monotonic()
        _record_success()
        return True


def _ensure_session() -> bool:
    with _RPC_LOCK:
        if _rate_limit_active():
            return False
        expired = time.monotonic() - _LAST_INIT > _SESSION_TTL
        if not _SESSION_READY or expired:
            return _reinit()
        return True


def _rpc(method: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Perform an MCP request, renewing an expired session once when required."""
    global _SID, _SESSION_READY
    with _RPC_LOCK:
        if not _ensure_session():
            return None
        body = (
            {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method, "params": params}
            if params
            else {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method}
        )
        obj = _post(body)
        if obj is not None:
            return obj
        if _BLOCKED_REASON or _SESSION_READY:
            return None
        # Streamable HTTP requires a fresh InitializeRequest after a session 404.
        if _reinit():
            return _post(body)
        return None


def _content_text(result: Dict[str, Any]) -> str:
    content = result.get("content")
    if not isinstance(content, list):
        return ""
    return " ".join(
        str(item.get("text", ""))
        for item in content
        if isinstance(item, dict) and item.get("type") == "text" and item.get("text")
    )[:180]


def _record_tool_failure(stage: str, detail: str, tool: Optional[str] = None) -> None:
    """Record an MCP tool error, including upstream errors encoded as text JSON."""
    message = detail
    diagnostic = detail
    try:
        payload = json.loads(detail)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
        error = payload["error"]
        message = str(error.get("message", detail))
        code = str(error.get("code", "")).strip()
        diagnostic = f"{code}: {message}" if code else message
    _record_failure(
        stage,
        diagnostic,
        tool=tool,
        retry_after_seconds=_parse_upstream_retry_after(message),
    )


def _call_payload(tool: str, args: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Return the full structured MCP payload, including pagination metadata."""
    obj = _rpc("tools/call", {"name": tool, "arguments": args or {}})
    if obj is None or "error" in obj:
        return None
    result = obj.get("result")
    if not isinstance(result, dict):
        _record_failure("tools/call", "tool response omitted result", tool=tool)
        return None
    if result.get("isError"):
        detail = _content_text(result) or "tool reported isError"
        _record_tool_failure("tools/call", detail, tool=tool)
        return None

    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        _record_success()
        return structured

    # Some MCP tools return JSON text content when structuredContent is absent.
    content = result.get("content")
    if isinstance(content, list):
        for item in content:
            if not isinstance(item, dict) or item.get("type") != "text":
                continue
            try:
                decoded = json.loads(str(item.get("text", "")))
            except json.JSONDecodeError:
                continue
            _record_success()
            return decoded if isinstance(decoded, dict) else {"data": decoded}
    _record_failure(
        "tools/call",
        "tool response omitted structuredContent"
        + (f": {_content_text(result)}" if content else ""),
        tool=tool,
    )
    return None


def _call(tool: str, args: Optional[Dict[str, Any]] = None) -> Any:
    """Call an MCP tool and unwrap business data while preserving its shape."""
    payload = _call_payload(tool, args)
    if payload is None:
        return None
    return payload.get("data", payload)


# ── 代码格式转换 ──


def ft_plain(code: str) -> str:
    return str(code).strip()[:6]


def ft_sfx(code: str) -> str:
    from stock_common.symbol_norm import normalize_symbol

    return normalize_symbol(code).upper_suffix()


# ── 业务函数 ──


def get_ft_comment_score_series(code: str) -> List[Dict[str, Any]]:
    d = _call("ft_v1_stock_comment_score", {"symbol": ft_plain(code)})
    return cast(List[Dict[str, Any]], d) if isinstance(d, list) else []


def get_ft_comment_desire(code: str) -> Optional[Dict[str, Any]]:
    d = _call("ft_v1_stock_comment_desire", {"symbol": ft_plain(code)})
    if isinstance(d, list) and d:
        return cast(Dict[str, Any], d[0])
    return cast(Dict[str, Any], d) if isinstance(d, dict) else None


def get_ft_comment_focus(code: str) -> Optional[Dict[str, Any]]:
    d = _call("ft_v1_stock_comment_focus", {"symbol": ft_plain(code)})
    if isinstance(d, list) and d:
        return cast(Dict[str, Any], d[0])
    return cast(Dict[str, Any], d) if isinstance(d, dict) else None


def get_ft_comment_org_participate(code: str) -> Optional[Dict[str, Any]]:
    d = _call("ft_v1_stock_comment_org_participate", {"symbol": ft_plain(code)})
    if isinstance(d, list) and d:
        return cast(Dict[str, Any], d[0])
    return cast(Dict[str, Any], d) if isinstance(d, dict) else None


def get_ft_comment_all(page: int = 1, page_size: int = 200) -> List[Dict[str, Any]]:
    d = _call("ft_v1_stock_comment_index", {"page": page, "page_size": page_size})
    return cast(List[Dict[str, Any]], d) if isinstance(d, list) else []


def get_ft_limit_up_pool_yesterday(
    trade_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    if trade_date is None:
        from stock_common.stock_calendar import previous_trading_day

        trade_date = previous_trading_day(date.today()).strftime("%Y%m%d")
    return _call_all_pages(
        "ft_v1_limit_list",
        {"limit_type": "up", "trade_date": trade_date},
        page_size=_LIMIT_LIST_PAGE_SIZE,
    )


def get_ft_limit_event_timeline(symbol: str, trade_date: str) -> List[Dict[str, Any]]:
    d = _call(
        "ft_v2_limit_event_timeline_3s",
        {"symbol": ft_sfx(symbol), "trade_date": trade_date},
    )
    return cast(List[Dict[str, Any]], d) if isinstance(d, list) else []


def get_ft_ggmx_changes(code: str) -> List[Dict[str, Any]]:
    return _call_all_pages(
        "ft_v1_holder_stock_ggmx",
        {"stock_code": ft_plain(code)},
        page_size=_GGMX_PAGE_SIZE,
    )


def _goodwill_data_rows(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    data = payload.get("data")
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    return []


def _call_all_pages(
    tool: str,
    args: Dict[str, Any],
    *,
    page_size: int,
    max_pages: int = 100,
) -> List[Dict[str, Any]]:
    """Fetch one paginated dataset completely or return no partial result."""
    rows: List[Dict[str, Any]] = []
    page_count: Optional[int] = None
    total: Optional[int] = None
    for page in range(1, max_pages + 1):
        payload = _call_payload(tool, {**args, "page": page, "page_size": page_size})
        if payload is None:
            return []
        metadata = payload.get("metadata")
        pagination = metadata.get("pagination") if isinstance(metadata, dict) else None
        raw_page_count = pagination.get("pages") if isinstance(pagination, dict) else None
        if raw_page_count is None or isinstance(raw_page_count, bool):
            _record_failure(
                "tools/call",
                "paginated response omitted a valid page count",
                tool=tool,
            )
            return []
        try:
            current_page_count = int(raw_page_count)
        except (TypeError, ValueError):
            _record_failure(
                "tools/call",
                "paginated response omitted a valid page count",
                tool=tool,
            )
            return []

        raw_total = metadata.get("total") if isinstance(metadata, dict) else None
        current_total: Optional[int] = None
        if raw_total is not None:
            try:
                if isinstance(raw_total, bool):
                    raise ValueError("boolean total")
                current_total = int(raw_total)
            except (TypeError, ValueError):
                _record_failure(
                    "tools/call",
                    "paginated response omitted a valid total count",
                    tool=tool,
                )
                return []
            if total is None:
                total = current_total
            elif total != current_total:
                _record_failure(
                    "tools/call",
                    f"total count changed during pagination: {total} to {current_total}",
                    tool=tool,
                )
                return []

        if current_page_count == 0:
            raw_returned = metadata.get("returned") if isinstance(metadata, dict) else None
            returned_count: Optional[int] = None
            if raw_returned is not None:
                try:
                    if isinstance(raw_returned, bool):
                        raise ValueError("boolean returned count")
                    returned_count = int(raw_returned)
                except (TypeError, ValueError):
                    returned_count = -1
            raw_data = payload.get("data")
            has_more = pagination.get("has_more") if isinstance(pagination, dict) else None
            if (
                page == 1
                and page_count is None
                and current_total == 0
                and isinstance(raw_data, list)
                and not raw_data
                and returned_count in (None, 0)
                and (has_more is None or has_more is False)
            ):
                return []
            _record_failure(
                "tools/call",
                "zero-page response is inconsistent with an empty result",
                tool=tool,
            )
            return []

        if current_page_count < 1:
            _record_failure(
                "tools/call",
                f"invalid page count: {current_page_count}",
                tool=tool,
            )
            return []
        if page_count is None:
            page_count = current_page_count
            if page_count > max_pages:
                _record_failure(
                    "tools/call",
                    f"page count {page_count} exceeds safety limit {max_pages}",
                    tool=tool,
                )
                return []
        elif page_count != current_page_count:
            _record_failure(
                "tools/call",
                f"page count changed during pagination: {page_count} to {current_page_count}",
                tool=tool,
            )
            return []

        rows.extend(_goodwill_data_rows(payload))
        if page >= page_count:
            break

    if page_count is None or page < page_count:
        _record_failure(
            "tools/call",
            f"pagination stopped before page {page_count}",
            tool=tool,
        )
        return []
    if len(rows) == 0 and total not in (None, 0):
        _record_failure("tools/call", "paginated response returned no rows", tool=tool)
        return []
    if total is not None:
        try:
            expected_rows = int(total)
        except (TypeError, ValueError):
            expected_rows = len(rows)
        if len(rows) != expected_rows:
            _record_failure(
                "tools/call",
                f"incomplete pages: read {len(rows)} of {expected_rows} rows",
                tool=tool,
            )
            return []
    return rows


def _goodwill_report_date() -> Optional[str]:
    payload = _call_payload("ft_v1_goodwill_market_overview")
    if payload is None:
        return None
    dates = set()
    for row in _goodwill_data_rows(payload):
        for key, value in row.items():
            if "report" not in key.lower() and "period" not in key.lower():
                continue
            match = re.search(r"(20\d{2})[-/]?(\d{2})[-/]?(\d{2})", str(value))
            if match:
                dates.add("".join(match.groups()))
    if not dates:
        _record_failure(
            "tools/call",
            "goodwill market overview omitted a report date",
            tool="ft_v1_goodwill_market_overview",
        )
        return None
    return max(dates)


def _load_goodwill_cache() -> None:
    global _GOODWILL_BY_CODE, _GOODWILL_CACHE_EXPIRES_AT
    with _GOODWILL_LOCK:
        now = time.monotonic()
        if now < _GOODWILL_CACHE_EXPIRES_AT:
            return

        report_date = _goodwill_report_date()
        if report_date is None:
            _GOODWILL_BY_CODE = {}
            _GOODWILL_CACHE_EXPIRES_AT = time.monotonic() + _GOODWILL_FAILURE_CACHE_TTL
            return

        first_page = _call_payload(
            "ft_v1_goodwill_stock_detail",
            {"date": report_date, "page": 1, "page_size": _GOODWILL_PAGE_SIZE},
        )
        if first_page is None:
            _GOODWILL_BY_CODE = {}
            _GOODWILL_CACHE_EXPIRES_AT = time.monotonic() + _GOODWILL_FAILURE_CACHE_TTL
            return

        pagination = first_page.get("metadata", {}).get("pagination", {})
        try:
            page_count = max(1, int(pagination.get("pages", 1)))
        except (TypeError, ValueError):
            page_count = 0
        if page_count > _GOODWILL_MAX_PAGES or page_count == 0:
            _record_failure(
                "tools/call",
                f"invalid goodwill pagination page count: {pagination.get('pages')}",
                tool="ft_v1_goodwill_stock_detail",
            )
            _GOODWILL_BY_CODE = {}
            _GOODWILL_CACHE_EXPIRES_AT = time.monotonic() + _GOODWILL_FAILURE_CACHE_TTL
            return

        records: Dict[str, List[Dict[str, Any]]] = {}
        rows_read = 0
        total = first_page.get("metadata", {}).get("total")
        failed = False
        for page in range(1, page_count + 1):
            payload = (
                first_page
                if page == 1
                else _call_payload(
                    "ft_v1_goodwill_stock_detail",
                    {"date": report_date, "page": page, "page_size": _GOODWILL_PAGE_SIZE},
                )
            )
            if payload is None:
                records = {}
                failed = True
                break
            rows = _goodwill_data_rows(payload)
            rows_read += len(rows)
            for row in rows:
                raw_code = row.get("security_code") or row.get("stock_code") or ""
                digits = re.sub(r"\D", "", str(raw_code))
                code = digits[-6:] if len(digits) >= 6 else ""
                if code:
                    records.setdefault(code, []).append(row)

        if not failed and total is not None:
            try:
                expected_rows = int(total)
            except (TypeError, ValueError):
                expected_rows = rows_read
            if rows_read != expected_rows:
                _record_failure(
                    "tools/call",
                    f"incomplete goodwill pages: read {rows_read} of {expected_rows} rows",
                    tool="ft_v1_goodwill_stock_detail",
                )
                records = {}
                failed = True

        success = bool(records) and not failed
        _GOODWILL_BY_CODE = records if success else {}
        ttl = _GOODWILL_CACHE_TTL if success else _GOODWILL_FAILURE_CACHE_TTL
        _GOODWILL_CACHE_EXPIRES_AT = time.monotonic() + ttl


def get_ft_goodwill_stock_detail(code: str) -> List[Dict[str, Any]]:
    """Return the latest report-period goodwill rows for one stock.

    The current FTShare endpoint is market-wide and paginated. Load it once per
    process, then restore the project's prior per-stock return contract.
    """
    _load_goodwill_cache()
    digits = re.sub(r"\D", "", str(code))
    symbol = digits[-6:] if len(digits) >= 6 else ""
    return [dict(row) for row in _GOODWILL_BY_CODE.get(symbol, [])]


def get_ft_pledge_summary() -> Optional[Dict[str, Any]]:
    d = _call("ft_v1_pledge_pledge_summary")
    if isinstance(d, list) and d:
        return cast(Dict[str, Any], d[0])
    return cast(Dict[str, Any], d) if isinstance(d, dict) else None


def get_ft_unlock_by_date(date_yyyymmdd: str) -> List[Dict[str, Any]]:
    d = _call(
        "ft_v1_unlock_stock_unlock",
        {"start_date": date_yyyymmdd, "end_date": date_yyyymmdd},
    )
    return cast(List[Dict[str, Any]], d) if isinstance(d, list) else []


def get_ft_dapan_flow(trade_date: Optional[str] = None) -> Any:
    args = {"trade_date": trade_date} if trade_date else None
    return _call("ft_v1_eastmoney_dapan_flow", args)


def get_ft_market_snapshot() -> Any:
    return _call("ft_v1_daec_market_snapshot")


def get_ft_suspension_list(trade_date: Optional[str] = None) -> Any:
    args = {"trade_date": trade_date} if trade_date else None
    return _call("ft_v1_suspension_list", args)


def get_ft_mainline_cls() -> Optional[Dict[str, Any]]:
    """财联社主线机会（主线方向/龙头/催化剂——字典外全新维度）。"""
    result = _call("market_mainline_cls")
    return cast(Dict[str, Any], result) if isinstance(result, dict) else None

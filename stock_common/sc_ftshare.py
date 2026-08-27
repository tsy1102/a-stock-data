# -*- coding: utf-8 -*-
"""FTShare MCP 客户端统一封装（V17.0.7 新源——字典 §12.20，实测后采纳）。

接入形态：公共网关 MCP Streamable HTTP(JSON-RPC)，无鉴权。
⚠️ 会话 TTL≈2 小时且过期后所有调用**静默返回空**——本模块自动 re-init。
限流：market.ft.tech @2rps（sc_network._DOMAIN_LIMITS）+ 模块内 500ms 间隔。
"""
from typing import Any, Dict, List, Optional
import json
import time
import uuid

import requests

_BASE = "https://market.ft.tech/gateway/mcp"
_HEADERS = {"Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"}
_SID: Optional[str] = None
_LAST_INIT: float = 0.0
_SESSION_TTL = 5400  # 90 min
_LAST_POST: float = 0.0


def is_ftshare_enabled() -> bool:
    import os
    return os.environ.get("FTSHARE_ENABLED", "1") != "0"


def _parse(r) -> Optional[dict]:
    txt = r.content.decode("utf-8", errors="replace")
    events, cur = [], []
    for line in txt.splitlines():
        if line.startswith("data:"):
            cur.append(line[5:].lstrip())
        elif cur:
            events.append("\n".join(cur)); cur = []
    if cur:
        events.append("\n".join(cur))
    for e in events:
        e = e.strip()
        if not e:
            continue
        try:
            obj = json.loads(e)
            if isinstance(obj, dict) and ("result" in obj or "error" in obj):
                return obj
        except json.JSONDecodeError:
            continue
    return None


def _post(body: dict, timeout: int = 60) -> Optional[dict]:
    """POST + 自动限流(≥500ms) + SSE 解析。"""
    global _LAST_POST
    el = time.time() - _LAST_POST
    if el < 0.5:
        time.sleep(0.5 - el)
    _LAST_POST = time.time()
    h = dict(_HEADERS)
    if _SID:
        h["Mcp-Session-Id"] = _SID
    try:
        r = requests.post(_BASE, data=json.dumps(body).encode("utf-8"),
                          headers=h, timeout=timeout)
        return _parse(r)
    except Exception:
        return None


def _reinit() -> None:
    global _SID, _LAST_INIT, _LAST_POST
    # initialize 必须用直接 requests.post 以捕获响应头中的 Mcp-Session-Id
    body = {"jsonrpc": "2.0", "id": str(uuid.uuid4()),
            "method": "initialize",
            "params": {"protocolVersion": "2025-03-26",
                       "capabilities": {},
                       "clientInfo": {"name": "a-stock-data", "version": "0.1"}}}
    try:
        el = time.time() - _LAST_POST
        if el < 0.5:
            time.sleep(0.5 - el)
        _LAST_POST = time.time()
        r = requests.post(_BASE,
                          data=json.dumps(body).encode("utf-8"),
                          headers=dict(_HEADERS), timeout=30)
        obj = _parse(r)
        if obj and obj.get("result"):
            new_sid = r.headers.get("Mcp-Session-Id")
            if new_sid:
                _SID = new_sid
            _LAST_INIT = time.time()
            # 发送 initialized 通知
            time.sleep(0.3)
            notif_body = json.dumps({"jsonrpc": "2.0",
                                     "method": "notifications/initialized"})
            requests.post(_BASE, data=notif_body.encode("utf-8"),
                          headers={**_HEADERS, "Mcp-Session-Id": _SID or ""},
                          timeout=15)
    except Exception:
        pass


def _ensure_session() -> None:
    global _SID, _LAST_INIT
    if not _SID or (time.time() - _LAST_INIT) > _SESSION_TTL:
        _SID = None
        _reinit()
    if not _SID:
        raise ConnectionError("FTShare MCP 会话建立失败")


def _rpc(method: str, params: dict = None) -> Optional[dict]:
    """JSON-RPC 调用；空响应自动 re-init 重试一次。"""
    _ensure_session()
    for attempt in range(2):
        obj = _post({"jsonrpc": "2.0", "id": str(uuid.uuid4()),
                     "method": method, "params": params} if params else
                    {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method})
        if obj is not None:
            return obj
        if attempt == 0:
            _SID = None
            _reinit()
    return None


def _call(tool: str, args: dict = None):
    """tools/call 并解包 structuredContent.data；isError 返回 None。"""
    obj = _rpc("tools/call", {"name": tool, "arguments": args or {}})
    res = (obj or {}).get("result") or {}
    if res.get("isError"):
        return None
    sc = res.get("structuredContent")
    if sc is None:
        return None
    return sc.get("data", sc)


# ── 代码格式转换 ──

def ft_plain(code: str) -> str:
    return str(code).strip()[:6]


def ft_sfx(code: str) -> str:
    c = str(code).strip()[:6]
    if c.startswith("6"):
        return c + ".XSHG"
    if c.startswith("9"):
        return c + ".BJ"
    return c + ".XSHE"


# ── 业务函数 ──

def get_ft_comment_score_series(code: str) -> List[Dict]:
    d = _call("ft_stock_comment_score_em", {"symbol": ft_plain(code)})
    return d if isinstance(d, list) else []


def get_ft_comment_desire(code: str) -> Optional[Dict]:
    d = _call("ft_stock_comment_desire_em", {"symbol": ft_plain(code)})
    if isinstance(d, list) and d:
        return d[0]
    return d if isinstance(d, dict) else None


def get_ft_comment_focus(code: str) -> Optional[Dict]:
    d = _call("ft_stock_comment_focus_em", {"symbol": ft_plain(code)})
    if isinstance(d, list) and d:
        return d[0]
    return d if isinstance(d, dict) else None


def get_ft_comment_org_participate(code: str) -> Optional[Dict]:
    d = _call("ft_stock_comment_org_participate_em", {"symbol": ft_plain(code)})
    if isinstance(d, list) and d:
        return d[0]
    return d if isinstance(d, dict) else None


def get_ft_comment_all(page: int = 1, page_size: int = 200) -> List[Dict]:
    d = _call("ft_stock_comment_em", {"page": page, "page_size": page_size})
    return d if isinstance(d, list) else []


def get_ft_limit_up_pool_yesterday() -> List[Dict]:
    d = _call("ft_limit_up_pool_yesterday")
    return d if isinstance(d, list) else []


def get_ft_limit_event_timeline(symbol: str, trade_date: str) -> List[Dict]:
    d = _call("ft_limit_event_timeline_3s",
              {"symbol": ft_sfx(symbol), "trade_date": trade_date})
    return d if isinstance(d, list) else []


def get_ft_ggmx_changes(code: str) -> List[Dict]:
    d = _call("ft_stock_ggmx_handler", {"symbol": ft_plain(code)})
    return d if isinstance(d, list) else []


def get_ft_goodwill_stock_detail(code: str) -> List[Dict]:
    d = _call("ft_goodwill_stock_detail", {"symbol": ft_plain(code)})
    return d if isinstance(d, list) else []


def get_ft_pledge_summary() -> Optional[Dict]:
    d = _call("ft_stock_pledge_summary")
    if isinstance(d, list) and d:
        return d[0]
    return d if isinstance(d, dict) else None


def get_ft_unlock_by_date(date_yyyymmdd: str) -> List[Dict]:
    d = _call("ft_stock_unlock_by_date_handler", {"date": date_yyyymmdd})
    return d if isinstance(d, list) else []


def get_ft_dapan_flow():
    return _call("ft_get_eastmoney_dapan_flow")


def get_ft_market_snapshot():
    return _call("ft_daec_market_snapshot")


def get_ft_suspension_list():
    return _call("ft_suspension_list")


def get_ft_mainline_cls() -> Optional[Dict]:
    """财联社主线机会（主线方向/龙头/催化剂——字典外全新维度）。"""
    obj = _rpc("tools/call", {"name": "market_mainline_cls", "arguments": {}})
    res = (obj or {}).get("result") or {}
    if res.get("isError"):
        return None
    sc = res.get("structuredContent")
    if sc is None:
        return None
    return sc.get("data", sc)

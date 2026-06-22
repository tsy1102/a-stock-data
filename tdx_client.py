#!/usr/bin/env python3
"""tdx_client.py — V8 通达信共享行情模块。

提供统一的 easy-tdx 数据访问接口，所有适配器函数返回格式与 V3 完全兼容。
当 TDX 服务器不可达时自动回退到原始 HTTP 源（百度K线/腾讯行情）。
"""
from __future__ import annotations

import time
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple, cast

import requests

from stock_common import _safe_float, UA, _request_with_retry, _quick_request

# ═══════════════════════════════════════
# V7.5: Monkey-patch easy_tdx 心跳线程 + 全局调用锁
# 问题 1：easy_tdx 的 TdxConnection.stop_heartbeat 会把 self._stop_event 置为 None，
#          而 _heartbeat_loop 仍在运行 self._stop_event.wait(...) → 潜在 AttributeError。
# 问题 2：_heartbeat_loop 内部只 except OSError，而 _recv_exact_sock 抛的是 TdxConnectionError
#         （非 OSError 子类），所以"连接被服务器关闭"会直接穿透整个线程 → 打印满屏堆栈。
# 问题 3：`_TDX_CLIENT` / `_TDX_MAC_CLIENT` 是单例，多线程并发读写同一个 socket
#         → 协议包错乱卡死。
# 解决：重写 stop_heartbeat（只 set 不置 None）；给 _heartbeat_loop 加最外层 Exception 保护，
#       让心跳线程静默死亡而不泄漏堆栈；加 `_TDX_CALL_LOCK = RLock()`，让 TDX 请求串行。
# ═══════════════════════════════════════
import threading as _tdx_th


def _patch_easy_tdx_heartbeat() -> None:
    try:
        from easy_tdx.transport import sync as _tdx_sync_mod
        _TdxConnection = getattr(_tdx_sync_mod, "TdxConnection", None)
        if _TdxConnection is None:
            return

        def _safe_stop_heartbeat(self) -> None:
            """温柔停止：只 set 事件，不将 _stop_event 置 None。"""
            se = getattr(self, "_stop_event", None)
            if isinstance(se, _tdx_th.Event):
                try:
                    se.set()
                except Exception:
                    pass
            hb = getattr(self, "_heartbeat_thread", None)
            if isinstance(hb, _tdx_th.Thread) and hb.is_alive():
                try:
                    hb.join(timeout=0.5)
                except Exception:
                    pass
            try:
                setattr(self, "_heartbeat_thread", None)
            except Exception:
                pass

        _orig_heartbeat_loop = getattr(_TdxConnection, "_heartbeat_loop", None)

        def _safe_heartbeat_loop(self, *args: Any, **kwargs: Any) -> None:
            """_heartbeat_loop 的最外层保护：捕获所有异常，静默死亡不打印堆栈。"""
            try:
                se = getattr(self, "_stop_event", None)
                if not isinstance(se, _tdx_th.Event):
                    return
                if _orig_heartbeat_loop is not None:
                    _orig_heartbeat_loop(self, *args, **kwargs)
            except Exception:
                return

        _TdxConnection.stop_heartbeat = _safe_stop_heartbeat
        if _orig_heartbeat_loop is not None:
            _TdxConnection._heartbeat_loop = _safe_heartbeat_loop
    except Exception:
        pass

_patch_easy_tdx_heartbeat()

_TDX_AVAILABLE: Optional[bool] = None
_TDX_CLIENT: Optional[Any] = None
_TDX_MAC_CLIENT: Optional[Any] = None
_last_request_time: float = 0.0
_TDX_RECONNECT_ATTEMPTS: int = 3
_TDX_RECONNECT_DELAY: float = 0.5
# V7.5: 全局调用锁 — `_TDX_CLIENT` / `_TDX_MAC_CLIENT` 是单例，多线程并发
# 调用时读写同一个 socket 会导致协议错乱卡死。用 RLock 让同一线程可重入。
_TDX_CALL_LOCK = _tdx_th.RLock()

# ── V7.5: 进程内缓存 ─────────────────────────────────────────────
# 策略并发阶段只做纯 CPU 计算，不再触发网络 IO。
# key 格式: f"{period}:{code}:{count}"，period: D=日线, W=周线, Q=行情
_TDX_KLINE_CACHE: Dict[str, Tuple[List[str], List[List[str]]]] = {}
_TDX_WKLINE_CACHE: Dict[str, Tuple[List[str], List[List[str]]]] = {}
_TDX_QUOTE_CACHE: Dict[str, Dict[str, Any]] = {}

def tdx_cache_preload_ks(code: str, count: int = 800) -> None:
    """预热单只股票的日线 K线（调用者负责外部循环/并发控制）。"""
    tdx_get_security_bars(code, count)

def tdx_cache_preload_wk(code: str, count: int = 100) -> None:
    """预热单只股票的周线 K线。"""
    tdx_get_weekly_bars(code, count)

def tdx_cache_preload_q(code: str) -> None:
    """预热单只股票的行情快照。"""
    tdx_get_quote_full(code)

def tdx_cache_clear() -> None:
    """清空缓存（跨日期/跨报告需要时调用）。"""
    with _TDX_CALL_LOCK:
        _TDX_KLINE_CACHE.clear()
        _TDX_WKLINE_CACHE.clear()
        _TDX_QUOTE_CACHE.clear()

_BAIDU_PAE_HEADERS: Dict[str, str] = {
    "Host": "finance.pae.baidu.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0",
    "Accept": "application/vnd.finance-web.v1+json",
    "Origin": "https://gushitong.baidu.com",
    "Referer": "https://gushitong.baidu.com/",
}

# ═══════════════════════════════════════
# 基础工具
# ═══════════════════════════════════════
def _market_prefix(code: str) -> str:
    if code.startswith(("6", "9")): return "sh"
    elif code.startswith("8"): return "bj"
    return "sz"

def _market_from_code(code: str) -> int:
    if code.startswith(("6", "9")): return 1
    elif code.startswith("8"): return 2
    return 0

def _index_to_market_code(idx_code: str) -> Tuple[int, str]:
    prefix = idx_code[:2]
    num = idx_code[2:]
    m = 1 if prefix == "sh" else 0
    return (m, num)

# ═══════════════════════════════════════
# 按域名独立限流配置（基于诊断脚本实测）
# ═══════════════════════════════════════
# 腾讯行情 qt.gtimg.cn:      并发10, sleep=0ms → 100% 成功
# 新浪财报 quotes.sina.cn:    并发10, sleep=0ms → 100% 成功
# 同花顺强势 zx.10jqka.com.cn: 并发10, sleep=0ms → 100% 成功
# 东财 datacenter-web.eastmoney.com: 并发3, sleep=100ms → 100% 成功
# ═══════════════════════════════════════
_DOMAIN_LIMITS: Dict[str, Dict[str, Any]] = {
    "qt.gtimg.cn": {"sleep_ms": 0, "semaphore": None},
    "quotes.sina.cn": {"sleep_ms": 0, "semaphore": None},
    "finance.pae.baidu.com": {"sleep_ms": 0, "semaphore": None},
    "zx.10jqka.com.cn": {"sleep_ms": 100, "semaphore": None},
    "datacenter-web.eastmoney.com": {"sleep_ms": 100, "semaphore": None},
    "push2.eastmoney.com": {"sleep_ms": 100, "semaphore": None},
    "reportapi.eastmoney.com": {"sleep_ms": 100, "semaphore": None},
}
# 每个域名独立的最后请求时间
_DOMAIN_LAST_TIME: Dict[str, float] = {}


def _http_get(url: str, params: Optional[Dict[str, Any]] = None,
              headers: Optional[Dict[str, str]] = None, timeout: int = 15) -> Optional[requests.Response]:
    """按域名独立限流的 HTTP GET 请求（基于诊断脚本实测参数）。"""
    import random as _rand

    # 解析域名
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc

    # 获取该域名的限流配置（默认 sleep=100ms 作为兜底）
    limit = _DOMAIN_LIMITS.get(domain, {"sleep_ms": 100})
    sleep_ms = limit["sleep_ms"]

    # 按域名独立 sleep
    last_time = _DOMAIN_LAST_TIME.get(domain, 0.0)
    now = time.time()
    elapsed_ms = (now - last_time) * 1000
    if sleep_ms > 0 and last_time > 0 and elapsed_ms < sleep_ms:
        time.sleep((sleep_ms - elapsed_ms) / 1000.0)
    _DOMAIN_LAST_TIME[domain] = time.time()

    try:
        return requests.get(url, params=params, headers=headers or {"User-Agent": UA}, timeout=timeout)
    except Exception:
        return None

# ═══════════════════════════════════════
# TDX 连接管理
# ═══════════════════════════════════════
def _check_tdx() -> bool:
    global _TDX_AVAILABLE
    if _TDX_AVAILABLE is not None:
        return _TDX_AVAILABLE
    with _TDX_CALL_LOCK:
        if _TDX_AVAILABLE is not None:
            return _TDX_AVAILABLE
        try:
            from easy_tdx import TdxClient
            c = TdxClient()
            c.connect()
            quotes = c.get_security_quotes(cast(List[Tuple[Any, str]], [(1, "600519")]))
            _TDX_AVAILABLE = quotes is not None and len(quotes) > 0
            c.close()
        except Exception:
            _TDX_AVAILABLE = False
    return _TDX_AVAILABLE

def _get_tdx_client() -> Optional[Any]:
    """V7.5: 获取 TdxClient（加锁，线程安全），连接异常时自动重连。"""
    with _TDX_CALL_LOCK:
        global _TDX_CLIENT
        for attempt in range(_TDX_RECONNECT_ATTEMPTS):
            if _TDX_CLIENT is not None:
                try:
                    _TDX_CLIENT.ensure_connected()
                    return _TDX_CLIENT
                except Exception:
                    _TDX_CLIENT = None
                    time.sleep(_TDX_RECONNECT_DELAY)
                    continue
            if not _check_tdx():
                return None
            try:
                from easy_tdx import TdxClient
                _TDX_CLIENT = TdxClient()
                _TDX_CLIENT.connect()
                return _TDX_CLIENT
            except Exception:
                _TDX_CLIENT = None
                if attempt < _TDX_RECONNECT_ATTEMPTS - 1:
                    time.sleep(_TDX_RECONNECT_DELAY * (attempt + 1))
        return None

def _get_mac_client() -> Optional[Any]:
    """V7.5: 获取 MacClient（加锁，线程安全），连接异常时自动重连。"""
    with _TDX_CALL_LOCK:
        global _TDX_MAC_CLIENT
        for attempt in range(_TDX_RECONNECT_ATTEMPTS):
            if _TDX_MAC_CLIENT is not None:
                try:
                    _TDX_MAC_CLIENT.ensure_connected()
                    return _TDX_MAC_CLIENT
                except Exception:
                    _TDX_MAC_CLIENT = None
                    time.sleep(_TDX_RECONNECT_DELAY)
                    continue
            try:
                from easy_tdx import MacClient
                _TDX_MAC_CLIENT = MacClient.from_best_host()
                _TDX_MAC_CLIENT.connect()
                return _TDX_MAC_CLIENT
            except Exception:
                _TDX_MAC_CLIENT = None
                if attempt < _TDX_RECONNECT_ATTEMPTS - 1:
                    time.sleep(_TDX_RECONNECT_DELAY * (attempt + 1))
        return None

def _reset_tdx_connections() -> None:
    """V7.5: 重置所有 TDX 缓存引用（加锁）。"""
    with _TDX_CALL_LOCK:
        global _TDX_CLIENT, _TDX_MAC_CLIENT, _TDX_AVAILABLE
        _TDX_CLIENT = None
        _TDX_MAC_CLIENT = None
        _TDX_AVAILABLE = None

def cleanup_tdx() -> None:
    """V7.5: 脚本退出前清理（加锁）。"""
    with _TDX_CALL_LOCK:
        global _TDX_CLIENT, _TDX_MAC_CLIENT, _TDX_AVAILABLE
        try:
            if _TDX_CLIENT is not None:
                _stop_ev = getattr(_TDX_CLIENT, '_stop_event', None)
                if _stop_ev is not None:
                    _stop_ev.set()
                time.sleep(0.05)
        except Exception:
            pass
        try:
            if _TDX_MAC_CLIENT is not None:
                _stop_ev = getattr(_TDX_MAC_CLIENT, '_stop_event', None)
                if _stop_ev is not None:
                    _stop_ev.set()
                time.sleep(0.05)
        except Exception:
            pass
        _TDX_CLIENT = None
        _TDX_MAC_CLIENT = None
        _TDX_AVAILABLE = None

# ═══════════════════════════════════════
# Fallback: 原始 V3 HTTP 源
# ═══════════════════════════════════════
def _baidu_kline_full_fallback(code: str, is_index: bool = False) -> Tuple[List[str], List[List[str]]]:
    """百度 K 线兜底 → (keys, rows)。"""
    url = "https://finance.pae.baidu.com/selfselect/getstockquotation"
    p = {"all":"1","isIndex":"true" if is_index else "false","isBk":"false","isBlock":"false",
         "isFutures":"false","isStock":"true","newFormat":"1","group":"quotation_kline_ab",
         "finClientType":"pc","code":code,"start_time":"","ktype":"1"}
    try:
        r = _http_get(url, params=p, headers=_BAIDU_PAE_HEADERS, timeout=10)
        if r is None: return [], []
        d = r.json()
        md = d.get("Result", {}).get("newMarketData", {})
        ks = md.get("keys", [])
        rows = []
        for row in md.get("marketData", "").split(";"):
            if not row: continue
            rows.append(row.split(","))
        return ks, rows
    except Exception:
        return [], []

def _tencent_quote_full_fallback(code: str) -> Dict[str, Any]:
    """腾讯行情兜底 → dict(含 name, price, change_pct, pe, pb 等)。"""
    try:
        url = f"https://qt.gtimg.cn/q={_market_prefix(code)}{code}"
        r = _quick_request(url, headers={"User-Agent": UA}, timeout=10)
        if r is None: return {}
        r.encoding = "gbk"
        vals = r.text.split('"')[1].split("~")
        if len(vals) < 53: return {}
        return {
            "name": vals[1], "price": _safe_float(vals[3]), "last_close": _safe_float(vals[4]),
            "open": _safe_float(vals[5]), "change_amt": _safe_float(vals[31]),
            "change_pct": _safe_float(vals[32]), "high": _safe_float(vals[33]),
            "low": _safe_float(vals[34]), "amount_wan": _safe_float(vals[37]),
            "turnover_pct": _safe_float(vals[38]), "pe_ttm": _safe_float(vals[39]),
            "amplitude_pct": _safe_float(vals[43]), "float_mcap_yi": _safe_float(vals[44]),
            "mcap_yi": _safe_float(vals[45]), "pb": _safe_float(vals[46]),
            "limit_up": _safe_float(vals[47]), "limit_down_price": _safe_float(vals[48]),
            "vol_ratio": _safe_float(vals[49]), "pe_static": _safe_float(vals[52]),
            "bid1_vol": _safe_float(vals[10]) * 100,
        }
    except Exception:
        return {}

def _tencent_batch_fallback(codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """腾讯批量行情 → {code: {name, price, change_pct, ...}}。"""
    if not codes: return {}
    result: Dict[str, Dict[str, Any]] = {}
    prefixed = []
    for c in codes:
        prefixed.append(f"{_market_prefix(c)}{c}")
    try:
        r = _http_get("https://qt.gtimg.cn/q=" + ",".join(prefixed), timeout=15)
        if r is None: return result
        for line in r.text.strip().split(";"):
            if "=" not in line or '"' not in line: continue
            key = line.split("=")[0].split("_")[-1]
            vals = line.split('"')[1].split("~")
            if len(vals) < 53: continue
            cv = key[2:]
            try:
                result[cv] = {
                    "name": vals[1], "price": float(vals[3]) if vals[3] else 0,
                    "change_pct": float(vals[32]) if vals[32] else 0,
                    "mcap_yi": float(vals[45]) if vals[45] else 0,
                    "pe_ttm": float(vals[39]) if vals[39] else 0,
                    "turnover_pct": float(vals[38]) if vals[38] else 0,
                }
            except (ValueError, TypeError): pass
    except Exception: pass
    return result

# ═══════════════════════════════════════
# 行情 + K线适配器
# ═══════════════════════════════════════
def tdx_get_security_bars(code: str, count: int = 800) -> Tuple[List[str], List[List[str]]]:
    """获取日 K 线 → (keys, rows)，V7.5: 进程内缓存 + 全局锁。"""
    cache_key = f"D:{code}:{count}"
    cached = _TDX_KLINE_CACHE.get(cache_key)
    if cached is not None:
        return cached
    with _TDX_CALL_LOCK:
        cached = _TDX_KLINE_CACHE.get(cache_key)
        if cached is not None:
            return cached
        for _retry in range(2):
            client = _get_tdx_client()
            if client is None:
                result = _baidu_kline_full_fallback(code)
                _TDX_KLINE_CACHE[cache_key] = result
                return result
            try:
                from easy_tdx import KlineCategory
                bars = client.get_security_bars(_market_from_code(code), code, KlineCategory.DAY, 0, count)
                if bars is None: 
                    result = _baidu_kline_full_fallback(code)
                    _TDX_KLINE_CACHE[cache_key] = result
                    return result
                keys = ['time', 'open', 'close', 'high', 'low', 'volume', 'amount']
                rows = []
                if hasattr(bars, 'columns'):
                    if bars.empty:
                        result = _baidu_kline_full_fallback(code)
                        _TDX_KLINE_CACHE[cache_key] = result
                        return result
                    for _, row in bars.iterrows():
                        rows.append([
                            str(row.get('date', ''))[:10],
                            str(row.get('open', '')),
                            str(row.get('close', '')),
                            str(row.get('high', '')),
                            str(row.get('low', '')),
                            str(row.get('vol', '')),
                            str(row.get('amount', '')),
                        ])
                else:
                    if not bars:
                        result = _baidu_kline_full_fallback(code)
                        _TDX_KLINE_CACHE[cache_key] = result
                        return result
                    for bar in bars:
                        time_str = f"{bar.year:04d}-{bar.month:02d}-{bar.day:02d}"
                        rows.append([time_str, f"{bar.open:.2f}", f"{bar.close:.2f}", f"{bar.high:.2f}",
                                     f"{bar.low:.2f}", f"{bar.vol:.0f}", f"{bar.amount:.2f}"])
                result = (keys, rows)
                _TDX_KLINE_CACHE[cache_key] = result
                return result
            except Exception:
                _reset_tdx_connections()
                continue
        result = _baidu_kline_full_fallback(code)
        _TDX_KLINE_CACHE[cache_key] = result
        return result

def tdx_get_latest_bar_with_ma(code: str):
    keys, rows = tdx_get_security_bars(code, count=120)
    if not keys or not rows: return {}
    idx_map = {k: i for i, k in enumerate(keys)}
    ci = idx_map.get('close', -1)
    if ci < 0 or len(rows) < 20: return {}
    closes = [_safe_float(r[ci]) for r in rows if len(r) > ci]
    closes = [c for c in closes if c > 0]
    def _sma(data, n):
        if len(data) < n: return 0
        return sum(data[-n:]) / n
    last = rows[-1]
    result = {}
    for i, k in enumerate(keys):
        if i < len(last): result[k] = last[i]
    result['ma5avgprice'] = f"{_sma(closes, 5):.2f}"
    result['ma10avgprice'] = f"{_sma(closes, 10):.2f}"
    result['ma20avgprice'] = f"{_sma(closes, 20):.2f}"
    return result

def tdx_get_quote_full(code: str) -> Dict[str, Any]:
    """获取个股完整行情（腾讯兜底，TDX 补强，V7.5 加锁 + 缓存）。"""
    cache_key = f"Q:{code}"
    cached = _TDX_QUOTE_CACHE.get(cache_key)
    if cached is not None:
        return cached
    result = _tencent_quote_full_fallback(code)
    with _TDX_CALL_LOCK:
        cached = _TDX_QUOTE_CACHE.get(cache_key)
        if cached is not None:
            return cached
        client = _get_tdx_client()
        if client is not None:
            try:
                quotes = client.get_security_quotes([(_market_from_code(code), code)])
                if quotes and len(quotes) > 0:
                    q = quotes[0]
                    if q.price: result['price'] = q.price
                    if q.pre_close: result['last_close'] = q.pre_close
                    if q.open: result['open'] = q.open
                    if q.high: result['high'] = q.high
                    if q.low: result['low'] = q.low
                    if q.amount: result['amount_wan'] = q.amount / 10000.0
                    if q.pre_close and q.pre_close > 0:
                        result['change_pct'] = (q.price - q.pre_close) / q.pre_close * 100
                        result['change_amt'] = q.price - q.pre_close
                    result['bid1'] = q.bid1; result['bid2'] = q.bid2; result['bid3'] = q.bid3
                    result['bid4'] = q.bid4; result['bid5'] = q.bid5
                    result['ask1'] = q.ask1; result['ask2'] = q.ask2; result['ask3'] = q.ask3
                    result['ask4'] = q.ask4; result['ask5'] = q.ask5
            except Exception: pass
    _TDX_QUOTE_CACHE[cache_key] = result
    return result

def tdx_get_quotes_batch(codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """批量获取行情（腾讯批量查询，TDX 增量修正）。"""
    if not codes: return {}
    result = _tencent_batch_fallback(codes)
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is not None:
            try:
                stocks = [(_market_from_code(c), c) for c in codes]
                quotes = client.get_security_quotes(stocks)
                if quotes:
                    for q in quotes:
                        if q.code in result and q.price:
                            result[q.code]['price'] = q.price
                            if q.pre_close and q.pre_close > 0:
                                result[q.code]['change_pct'] = round((q.price - q.pre_close) / q.pre_close * 100, 2)
            except Exception: pass
    return result

def tdx_get_index_quote(idx_code: str) -> Dict[str, Any]:
    """获取指数行情（TDX 优先，腾讯兜底）。"""
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is not None:
            try:
                from easy_tdx import KlineCategory
                market, code = _index_to_market_code(idx_code)
                bars = client.get_index_bars(market, code, KlineCategory.DAY, 0, 2)
                if bars is not None and not (hasattr(bars, 'empty') and bars.empty):
                    if hasattr(bars, 'columns'):
                        if len(bars) >= 2:
                            last_c = float(bars.iloc[-1]['close']); prev_c = float(bars.iloc[-2]['close'])
                            last_o = float(bars.iloc[-1]['open'])
                            chg = (last_c - prev_c) / prev_c * 100 if prev_c > 0 else 0
                            return {"price": round(last_c, 2), "open": round(last_o, 2), "change_pct": round(chg, 2)}
                    elif len(bars) >= 2:
                        last = bars[-1]; prev = bars[-2]
                        chg = (last.close - prev.close) / prev.close * 100 if prev.close > 0 else 0
                        return {"price": round(last.close, 2), "open": round(last.open, 2), "change_pct": round(chg, 2)}
            except Exception: pass
    try:
        url = f"https://qt.gtimg.cn/q={idx_code}"
        r = _quick_request(url, headers={"User-Agent": UA}, timeout=10)
        if r is None: return {}
        r.encoding = "gbk"
        v = r.text.split('"')[1].split("~")
        return {"price": _safe_float(v[3]), "open": _safe_float(v[5]), "change_pct": _safe_float(v[32])}
    except Exception: return {}

def tdx_get_historical_high(code: str) -> Optional[float]:
    """历史最高价（800 根日 K 线内）。"""
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None: return None
        try:
            from easy_tdx import KlineCategory
            bars = client.get_security_bars(_market_from_code(code), code, KlineCategory.DAY, 0, 8000)
            if bars is None: return None
            if hasattr(bars, 'columns'):
                if bars.empty: return None
                return max(float(bars.iloc[i]['high']) for i in range(len(bars)) if float(bars.iloc[i]['high']) > 0)
            if not bars: return None
            values = [b.high for b in bars if b.high > 0]
            return max(values) if values else None
        except Exception: return None

def tdx_get_index_bars(idx_code: str, count: int = 250):
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None:
            return _baidu_kline_full_fallback(idx_code, is_index=True)
        try:
            from easy_tdx import KlineCategory
            market, code = _index_to_market_code(idx_code)
            bars = client.get_index_bars(market, code, KlineCategory.DAY, 0, count)
            if bars is None: return _baidu_kline_full_fallback(idx_code, is_index=True)
            keys = ['time', 'open', 'close', 'high', 'low', 'volume', 'amount']
            rows = []
            if hasattr(bars, 'columns'):
                if bars.empty: return _baidu_kline_full_fallback(idx_code, is_index=True)
                for _, row in bars.iterrows():
                    rows.append([str(row.get('date',''))[:10], str(row.get('open','')), str(row.get('close','')),
                                 str(row.get('high','')), str(row.get('low','')), str(row.get('vol','')),
                                 str(row.get('amount',''))])
            else:
                if not bars: return _baidu_kline_full_fallback(idx_code, is_index=True)
                for bar in bars:
                    time_str = f"{bar.year:04d}-{bar.month:02d}-{bar.day:02d}"
                    rows.append([time_str, f"{bar.open:.2f}", f"{bar.close:.2f}", f"{bar.high:.2f}",
                                 f"{bar.low:.2f}", f"{bar.vol:.0f}", f"{bar.amount:.2f}"])
            return keys, rows
        except Exception:
            return _baidu_kline_full_fallback(idx_code, is_index=True)

def tdx_get_weekly_bars(code: str, count: int = 100):
    cache_key = f"W:{code}:{count}"
    cached = _TDX_WKLINE_CACHE.get(cache_key)
    if cached is not None:
        return cached
    with _TDX_CALL_LOCK:
        cached = _TDX_WKLINE_CACHE.get(cache_key)
        if cached is not None:
            return cached
        client = _get_tdx_client()
        if client is None:
            result: Tuple[List[Any], List[Any]] = ([], [])
            _TDX_WKLINE_CACHE[cache_key] = result
            return result
        try:
            from easy_tdx import KlineCategory
            bars = client.get_security_bars(_market_from_code(code), code, KlineCategory.WEEK, 0, count)
            if bars is None:
                result = ([], [])
                _TDX_WKLINE_CACHE[cache_key] = result
                return result
            keys = ['time', 'open', 'close', 'high', 'low', 'volume', 'amount']
            rows = []
            if hasattr(bars, 'columns'):
                if bars.empty:
                    result = ([], [])
                    _TDX_WKLINE_CACHE[cache_key] = result
                    return result
                for _, row in bars.iterrows():
                    rows.append([str(row.get('date',''))[:10], str(row.get('open','')), str(row.get('close','')),
                                 str(row.get('high','')), str(row.get('low','')), str(row.get('vol','')),
                                 str(row.get('amount',''))])
            else:
                if not bars:
                    result = ([], [])
                    _TDX_WKLINE_CACHE[cache_key] = result
                    return result
                for bar in bars:
                    time_str = f"{bar.year:04d}-{bar.month:02d}-{bar.day:02d}"
                    rows.append([time_str, f"{bar.open:.2f}", f"{bar.close:.2f}", f"{bar.high:.2f}",
                                 f"{bar.low:.2f}", f"{bar.vol:.0f}", f"{bar.amount:.2f}"])
            result = (keys, rows)
            _TDX_WKLINE_CACHE[cache_key] = result
            return result
        except Exception:
            result = ([], [])
            _TDX_WKLINE_CACHE[cache_key] = result
            return result

# ═══════════════════════════════════════
# 资金流适配器
# ═══════════════════════════════════════
def tdx_get_fund_flow(code: str):
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None: return {}
        try:
            df = client.get_fund_flow(_market_from_code(code), code)
            if df is None or df.empty: return {}
            row = df.iloc[0] if len(df) > 0 else None
            if row is None: return {}
            super_in = _safe_float(row.get('super_in', 0))
            large_in = _safe_float(row.get('large_in', 0))
            medium_in = _safe_float(row.get('medium_in', 0))
            small_in = _safe_float(row.get('small_in', 0))
            super_out = _safe_float(row.get('super_out', 0))
            large_out = _safe_float(row.get('large_out', 0))
            medium_out = _safe_float(row.get('medium_out', 0))
            small_out = _safe_float(row.get('small_out', 0))
            main_net = (super_in + large_in) - (super_out + large_out)
            total_in = super_in + large_in + medium_in + small_in
            total_out = super_out + large_out + medium_out + small_out
            total_net = total_in - total_out
            return {
                "main_net": main_net, "main_net_wan": main_net / 10000.0,
                "total_net": total_net,
                "super_in": super_in, "super_out": super_out,
                "large_in": large_in, "large_out": large_out,
                "medium_in": medium_in, "medium_out": medium_out,
                "small_in": small_in, "small_out": small_out,
            }
        except Exception: return {}

def tdx_get_history_fund_flow(code: str, days: int = 120):
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None: return []
        try:
            df = client.get_history_fund_flow(_market_from_code(code), code, 0, days)
            if df is None or df.empty: return []
            rows = []
            for _, row in df.iterrows():
                super_in = _safe_float(row.get('super_in', 0))
                large_in = _safe_float(row.get('large_in', 0))
                medium_in = _safe_float(row.get('medium_in', 0))
                small_in = _safe_float(row.get('small_in', 0))
                super_out = _safe_float(row.get('super_out', 0))
                large_out = _safe_float(row.get('large_out', 0))
                medium_out = _safe_float(row.get('medium_out', 0))
                small_out = _safe_float(row.get('small_out', 0))
                main_net = (super_in + large_in) - (super_out + large_out)
                super_net = super_in - super_out
                large_net = large_in - large_out
                mid_net = medium_in - medium_out
                small_net = small_in - small_out
                date_str = str(row.get('date', ''))[:10]
                rows.append({
                    "date": date_str, "main_net": main_net,
                    "super_net": super_net, "large_net": large_net,
                    "mid_net": mid_net, "small_net": small_net,
                })
            return rows
        except Exception: return []

# ═══════════════════════════════════════
# 除权除息 + 公告适配器
# ═══════════════════════════════════════
def tdx_get_finance_roe(code: str):
    """
    TDX 最新 ROE → 替换 eastmoney MAINFINADATA 单期查询

    返回: ROE% (float) 或 None
    """
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None: return None
        try:
            info = client.get_finance_info(_market_from_code(code), code)
            if info is None: return None
            profit = _safe_float(getattr(info, 'jing_lirun', 0))
            equity = _safe_float(getattr(info, 'jing_zichan', 0))
            if equity <= 0: return None
            return round(profit / equity * 100, 2)
        except Exception:
            return None


def tdx_get_dividend_history(code: str):
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None: return []
        try:
            df = client.get_xdxr_info(_market_from_code(code), code)
            if df is None or df.empty: return []
            rows = []
            for _, row in df.iterrows():
                cat = int(row.get('category', 0))
                if cat != 1: continue
                fh = _safe_float(row.get('fenhong', 0))
                szg = _safe_float(row.get('songzhuangu', 0))
                pg = _safe_float(row.get('peigu', 0))
                rows.append({
                    "date": str(row.get('date', ''))[:10],
                    "bonus_rmb": fh,
                    "bonus_ratio": pg,
                    "transfer_ratio": szg,
                })
            rows.sort(key=lambda x: x["date"], reverse=True)
            return rows
        except Exception: return []

def tdx_get_eps_from_reports(code: str):
    try:
        api = "https://reportapi.eastmoney.com/report/list"
        for page in range(1, 3):
            params = {"pageSize":"50","industry":"*","rating":"*","beginTime":"2000-01-01","endTime":"2030-01-01","pageNo":str(page),"code":code,"qType":"0"}
            r = _request_with_retry(api, params=params, timeout=30)
            if r is None: break
            rows = r.json().get("data") or []
            if not rows: break
            this_year = next_year = None
            for r2 in rows:
                ty = r2.get("predictThisYearEps")
                ny = r2.get("predictNextYearEps")
                if ty is not None: this_year = float(ty)
                if ny is not None: next_year = float(ny)
                if this_year is not None:
                    return {"eps_cur": this_year, "eps_next": next_year, "analyst_count": 1, "source": "东财研报"}
        return None
    except Exception: return None

def tdx_get_latest_announcements(code: str, days: int = 7):
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None: return []
        try:
            from easy_tdx import CompanyInfoCategory
            cats = client.get_company_info_category(_market_from_code(code), code)
            if not cats: return []
            anns = []
            for cat in cats:
                content = client.get_company_info_content(_market_from_code(code), code, cat.name, 0, 100)
                if content:
                    for item in content:
                        title = getattr(item, 'title', '') or str(item)
                        dt = getattr(item, 'date', '') or ''
                        anns.append({"title": str(title)[:120], "date": str(dt)[:10], "category": str(cat.name) if hasattr(cat, 'name') else ''})
                if len(anns) >= 10: break
            return anns[:10]
        except Exception: return []

# ═══════════════════════════════════════
# 行业板块适配器
# ═══════════════════════════════════════
def tdx_get_belong_boards(code: str):
    with _TDX_CALL_LOCK:
        client = _get_mac_client()
        if client is None: return {}
        try:
            df = client.get_belong_board(_market_from_code(code), code)
            if df is None or df.empty: return {}
            result: Dict[str, List[Any]] = {"industry": [], "concept": [], "area": [], "style": []}
            type_map = {0: "industry", 1: "industry", 12: "industry", 3: "area", 4: "concept", 5: "style"}
            for _, row in df.iterrows():
                bt = int(row.get('board_type', -1))
                cat = type_map.get(bt, None)
                if cat is None: continue
                result[cat].append({"code": str(row.get('board_code', '')), "name": str(row.get('board_name', ''))})
            return result
        except Exception: return {}

def tdx_get_board_list(board_type=0):
    with _TDX_CALL_LOCK:
        client = _get_mac_client()
        if client is None: return []
        try:
            from easy_tdx.mac.enums import BoardType
            df = client.get_board_list(BoardType(board_type))
            if df is None or df.empty: return []
            sectors = []
            for i, (_, row) in enumerate(df.iterrows()):
                price = _safe_float(row.get('price', 0))
                pre_close = _safe_float(row.get('pre_close', 0))
                chg_pct = round((price - pre_close) / pre_close * 100, 2) if pre_close > 0 else 0.0
                sectors.append({
                    "rank": i + 1, "code": str(row.get('code', '')), "name": str(row.get('name', '')),
                    "price": price, "change_pct": chg_pct,
                    "leader_name": str(row.get('symbol_name', '')),
                    "leader_change": _safe_float(row.get('symbol_rise_speed', 0)),
                    "up_count": 0, "down_count": 0,
                })
            return sectors
        except Exception: return []

def tdx_get_board_members(board_code: str, sort_by_change: bool = True):
    with _TDX_CALL_LOCK:
        client = _get_mac_client()
        if client is None: return []
        try:
            df = client.get_board_members(board_code)
            if df is None or df.empty: return []
            members = []
            for _, row in df.iterrows():
                close = _safe_float(row.get('close', 0))
                pre_close = _safe_float(row.get('pre_close', 0))
                chg = round((close - pre_close) / pre_close * 100, 2) if pre_close > 0 else _safe_float(row.get('speed_pct', 0))
                members.append({
                    "code": str(row.get('code', '')), "name": str(row.get('name', '')),
                    "price": close, "change_pct": chg,
                    "mcap_yi": _safe_float(row.get('total_market_cap_ab', 0)) / 1e8,
                    "turnover": _safe_float(row.get('turnover', 0)),
                    "pe": _safe_float(row.get('pe_dynamic', row.get('pe_ttm', 0))),
                    "main_net_amount": _safe_float(row.get('main_net_amount', 0)),
                })
            return members
        except Exception: return []

def tdx_get_board_by_name(board_name: str, board_type: int = 0):
    with _TDX_CALL_LOCK:
        client = _get_mac_client()
        if client is None: return []
        try:
            from easy_tdx.mac.enums import BoardType
            bt = BoardType(board_type)
        except Exception: return []
        try:
            board_df = client.get_board_list(bt)
            if board_df is None or board_df.empty: return []
        except Exception: return []
        _name_clean = board_name.replace("行业","").replace("板块","").replace("Ⅱ","").replace("Ⅲ","")
        matched_code = None
        for _, row in board_df.iterrows():
            row_name = str(row.get('name', ''))
            row_clean = row_name.replace("行业","").replace("板块","").replace("Ⅱ","").replace("Ⅲ","")
            if board_name in row_name or row_name in board_name or _name_clean in row_clean or row_clean in _name_clean:
                matched_code = str(row.get('code', ''))
                break
        if matched_code is None: return []
        return tdx_get_board_members(matched_code)

# ═══════════════════════════════════════
# 全市场股票列表
# ═══════════════════════════════════════

def tdx_get_market_abnormal_data():
    """
    TDX 全市场A股+多周期涨幅 → 替换 push2 get_market_abnormal_data

    返回:
        [{code, name, price, change_pct, turnover, mcap_yi,
          ret_3d, ret_5d, ret_10d, ret_20d, ret_60d}]
    或 [] 当 MacClient 不可用时
    """
    with _TDX_CALL_LOCK:
        client = _get_mac_client()
        if client is None:
            return []

        try:
            from easy_tdx.mac.enums import Category
            from easy_tdx.codec.bitmap import FieldBit

            fields = [
                FieldBit.CLOSE, FieldBit.PRE_CLOSE,
                FieldBit.TURNOVER, FieldBit.AMOUNT,
                FieldBit.CHANGE_3D_PCT, FieldBit.CHANGE_5D_PCT,
                FieldBit.CHANGE_10D_PCT, FieldBit.CHANGE_20D_PCT,
                FieldBit.CHANGE_60D_PCT,
                FieldBit.MAIN_NET_AMOUNT,
            ]

            all_stocks = []
            start = 0
            page_size = 80
            for _ in range(100):
                df = client.get_stock_quotes_list(Category.A, start, page_size, fields=fields)
                if df is None or df.empty:
                    break
                for _, row in df.iterrows():
                    code = str(row.get('code', ''))
                    name = str(row.get('name', ''))
                    if not code or not name:
                        continue
                    if 'ST' in name or '退' in name:
                        continue
                    close = _safe_float(row.get('close', 0))
                    pre_close = _safe_float(row.get('pre_close', 0))
                    chg = round((close - pre_close) / pre_close * 100, 2) if pre_close > 0 else 0
                    all_stocks.append({
                        'code': code, 'name': name,
                        'price': close, 'change_pct': chg,
                        'turnover': _safe_float(row.get('turnover', 0)),
                        'mcap_yi': _safe_float(row.get('amount', 0)) / 1e8 * 50,
                        'ret_3d': _safe_float(row.get('change_3d_pct', 0)),
                        'ret_5d': _safe_float(row.get('change_5d_pct', 0)),
                        'ret_10d': _safe_float(row.get('change_10d_pct', 0)),
                        'ret_20d': _safe_float(row.get('change_20d_pct', 0)),
                        'ret_60d': _safe_float(row.get('change_60d_pct', 0)),
                        'main_net_amount': _safe_float(row.get('main_net_amount', 0)),
                    })
                start += page_size
                if len(df) < page_size:
                    break
            return all_stocks
        except Exception:
            return []


def tdx_get_all_stocks():
    """V7.5: 全市场A股列表（MacClient，连接中断自动重置并重试）。"""
    for _retry in range(2):
        with _TDX_CALL_LOCK:
            client = _get_mac_client()
            if client is None: return []
            try:
                from easy_tdx.mac.enums import Category
                all_stocks = []
                start = 0
                page_size = 80
                for _ in range(100):
                    df = client.get_stock_quotes_list(Category.A, start, page_size)
                    if df is None or df.empty: break
                    for _, row in df.iterrows():
                        code = str(row.get('code', ''))
                        name = str(row.get('name', ''))
                        if not code or not name: continue
                        if 'ST' in name or '退' in name: continue
                        close = _safe_float(row.get('close', 0))
                        pre_close = _safe_float(row.get('pre_close', 0))
                        chg = round((close - pre_close) / pre_close * 100, 2) if pre_close > 0 else 0
                        turnover = _safe_float(row.get('turnover', 0))
                        amount = _safe_float(row.get('amount', 0)) / 1e8
                        mcap_est = amount * 50 if turnover > 0 else 0
                        all_stocks.append({
                            'code': code, 'name': name, 'price': close,
                            'change_pct': chg, 'mcap_yi': mcap_est,
                            'turnover_pct': turnover,
                            'amount_yi': amount,
                        })
                    start += page_size
                    if len(df) < page_size: break
                return all_stocks
            except Exception:
                _reset_tdx_connections()
                continue
    return []

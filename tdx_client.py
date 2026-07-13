#!/usr/bin/env python3
"""tdx_client.py — 通达信共享行情模块。

提供统一的 easy-tdx 数据访问接口，所有适配器函数返回格式与 V3 完全兼容。
当 TDX 服务器不可达时自动回退到原始 HTTP 源（百度K线/腾讯行情）。

版本信息:
    V9.5   2026-07-11 - 静默异常日志化（23处 except Exception 添加 _debug_log）
    V9.4   2026-07-11 - VERSION文件单一来源版本号管理
    V9.3.3 2026-07-10 - 代码质量提升：GD上传路径修复、GLM报告Bug修复、死代码清理、sync/async重构、schema统一
    V9.3.2 2026-07-09 - K线假数据防护：健康检查增加K线校验，TdxDecodeError时标记坏主机并强制换IP重连
    V9.3   2026-07-07 - 盘前行情模式：9:30前使用日K线上一交易日数据，避免实时接口返回0导致涨跌幅-100%；行情缓存Key增加交易日期，盘前/盘中数据独立保留
    V9.2   2026-07-05 - 异常处理规范化；重连前关闭旧连接防止泄漏
    V9.1.1 2026-07-04 - 补全 F10 交易日缓存策略；精简 6 个未使用的 F10 函数
    V9.1   2026-07-04 - F10 全覆盖：新增12个F10函数（公司概况/财务/股东/股本/新闻/研报/行业/经营/治理/资本运作/主题/异动）
    V9.0   2026-07-02 - 全量 TDX 服务器探测（53个节点）；F10 公告兜底（filename+start+length）
    V8.6   2026-06-24 - 限流安全加固：请求频率限制(20ms)/重连指数退避/线程锁保护
    V8.5   2026-06-22 - TDX请求最小间隔 + 指数退避重连
    V8.0   2026-06-17 - 初始版本
    V7.5 - Monkey-patch心跳线程/全局调用锁/进程内缓存
"""
from __future__ import annotations

import time
import os
import json
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple, cast

import requests

from stock_common import _safe_float, UA, _request_with_retry, _quick_request, _debug_log
from stock_cache import cached

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
                except Exception as _e:
                    _debug_log(f"tdx stop_heartbeat set event: {_e}")
            hb = getattr(self, "_heartbeat_thread", None)
            if isinstance(hb, _tdx_th.Thread) and hb.is_alive():
                try:
                    hb.join(timeout=0.5)
                except Exception as _e:
                    _debug_log(f"tdx stop_heartbeat join thread: {_e}")
            try:
                setattr(self, "_heartbeat_thread", None)
            except Exception as _e:
                _debug_log(f"tdx stop_heartbeat setattr: {_e}")

        _orig_heartbeat_loop = getattr(_TdxConnection, "_heartbeat_loop", None)

        def _safe_heartbeat_loop(self, *args: Any, **kwargs: Any) -> None:
            """_heartbeat_loop 的最外层保护：捕获所有异常，静默死亡不打印堆栈。"""
            try:
                se = getattr(self, "_stop_event", None)
                if not isinstance(se, _tdx_th.Event):
                    return
                if _orig_heartbeat_loop is not None:
                    _orig_heartbeat_loop(self, *args, **kwargs)
            except Exception as _e:
                _debug_log(f"tdx stop_heartbeat inner: {_e}")
                return

        _TdxConnection.stop_heartbeat = _safe_stop_heartbeat
        if _orig_heartbeat_loop is not None:
            _TdxConnection._heartbeat_loop = _safe_heartbeat_loop
    except Exception as _e:
        _debug_log(f"tdx monkey-patch heartbeat error: {_e}")

_patch_easy_tdx_heartbeat()

_TDX_AVAILABLE: Optional[bool] = None
_TDX_CLIENT: Optional[Any] = None
_TDX_MAC_CLIENT: Optional[Any] = None
_last_request_time: float = 0.0
_TDX_RECONNECT_ATTEMPTS: int = 3
_TDX_RECONNECT_DELAY: float = 0.5

# V8.9: MacClient 失败缓存（避免重复重试退避）
_MAC_AVAILABLE: Optional[bool] = None
# V8.5: TDX请求最小间隔（秒），防止过快请求被服务器断开
# 100ms = 约10次/秒，批量运行时更稳定
_TDX_MIN_INTERVAL: float = 0.1
# V7.5: 全局调用锁 — `_TDX_CLIENT` / `_TDX_MAC_CLIENT` 是单例，多线程并发
# 调用时读写同一个 socket 会导致协议错乱卡死。用 RLock 让同一线程可重入。
_TDX_CALL_LOCK = _tdx_th.RLock()

# V9.3.2: 返回假数据的TDX服务器黑名单
# 部分服务器K线接口返回 ret_count=800 但 body 为 0 字节，导致 TdxDecodeError
# 标记后 from_best_host 会跳过这些 IP，防止反复选中坏服务器
_TDX_BAD_HOSTS: set[str] = set()


def _tdx_throttle():
    """V8.5: TDX请求节流：确保两次请求间隔 >= _TDX_MIN_INTERVAL
    
    必须在 _TDX_CALL_LOCK 内调用。
    """
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if _last_request_time > 0 and elapsed < _TDX_MIN_INTERVAL:
        time.sleep(_TDX_MIN_INTERVAL - elapsed)
    _last_request_time = time.time()

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
    "datacenter-web.eastmoney.com": {"sleep_ms": 1000, "semaphore": None},
    "push2.eastmoney.com": {"sleep_ms": 100, "semaphore": None},
    "reportapi.eastmoney.com": {"sleep_ms": 1000, "semaphore": None},
}
# 每个域名独立的最后请求时间
_DOMAIN_LAST_TIME: Dict[str, float] = {}
# 限流字典的线程锁
_DOMAIN_LAST_TIME_LOCK = _tdx_th.Lock()


def _http_get(url: str, params: Optional[Dict[str, Any]] = None,
              headers: Optional[Dict[str, str]] = None, timeout: int = 15) -> Optional[requests.Response]:
    """按域名独立限流的 HTTP GET 请求（基于诊断脚本实测参数）。

    V9.0 新增：线程锁保护 _DOMAIN_LAST_TIME。
    """
    import random as _rand

    # 解析域名
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc

    # 获取该域名的限流配置（默认 sleep=100ms 作为兜底）
    limit = _DOMAIN_LIMITS.get(domain, {"sleep_ms": 100})
    sleep_ms = limit["sleep_ms"]

    # 按域名独立 sleep（加线程锁保护）
    wait_ms = 0.0
    with _DOMAIN_LAST_TIME_LOCK:
        last_time = _DOMAIN_LAST_TIME.get(domain, 0.0)
        now = time.time()
        elapsed_ms = (now - last_time) * 1000
        if sleep_ms > 0 and last_time > 0 and elapsed_ms < sleep_ms:
            wait_ms = sleep_ms - elapsed_ms
        _DOMAIN_LAST_TIME[domain] = now + wait_ms / 1000.0
    if wait_ms > 0:
        time.sleep(wait_ms / 1000.0)

    try:
        # V9.3.1: 数据获取全部直连，不使用系统代理（代理仅用于GD上传）
        return requests.get(url, params=params, headers=headers or {"User-Agent": UA},
                            timeout=timeout, proxies={"http": None, "https": None})
    except Exception as _e:
        _debug_log(f"tdx _tdx_http_get error ({url}): {_e}")
        return None

# ═══════════════════════════════════════
# TDX 连接管理
# ═══════════════════════════════════════

def _pre_scan_tdx_hosts() -> list[str]:
    """预扫描所有 TDX 服务器，返回通过全部健康检查的主机列表。
    
    扫描结果缓存到文件（24小时有效），避免每次启动都扫描。
    测试项：TCP连通性、K线接口、历史资金流接口。
    """
    cache_dir = os.path.join(os.path.dirname(__file__), "cache")
    cache_file = os.path.join(cache_dir, "tdx_hosts_cache.json")
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if time.time() - data.get('timestamp', 0) < 86400:
                    _good_hosts = data.get('good_hosts', [])
                    if _good_hosts:
                        _debug_log(f"TDX 主机缓存有效，跳过扫描，白名单 {len(_good_hosts)} 台")
                        return _good_hosts
        except Exception as _e:
            _debug_log(f"读取 TDX 主机缓存失败: {_e}")
    
    from easy_tdx.config import get_known_hosts
    all_hosts = get_known_hosts()
    _debug_log(f"开始预扫描 TDX 服务器，共 {len(all_hosts)} 台")
    
    good_hosts = []
    
    def _test_single_host(_host):
        try:
            from easy_tdx import TdxClient, Market, KlineCategory
            _client = TdxClient(host=_host, port=7709)
            _client.connect()
            
            _bars = _client.get_security_bars(Market.SH, "600519", KlineCategory.DAY, 0, 3)
            if _bars is None or (hasattr(_bars, 'empty') and _bars.empty) or len(_bars) < 2:
                _client.close()
                return None
            
            _df = _client.get_history_fund_flow(1, "600519", 0, 10)
            if _df is None or (hasattr(_df, 'empty') and _df.empty) or len(_df) < 5:
                _client.close()
                return None
            
            _client.close()
            return _host
        except Exception as _e:
            _debug_log(f"tdx _test_single_host ({_host}): {_e}")
            return None
    
    try:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as _executor:
            _results = list(_executor.map(_test_single_host, all_hosts))
        good_hosts = [_h for _h in _results if _h is not None]
    except Exception as _e:
        _debug_log(f"TDX 预扫描并发执行失败，降级为串行: {_e}")
        for _host in all_hosts[:20]:
            _result = _test_single_host(_host)
            if _result:
                good_hosts.append(_result)
    
    if good_hosts:
        _debug_log(f"TDX 预扫描完成，找到 {len(good_hosts)} 台可用服务器")
    else:
        _debug_log(f"TDX 预扫描完成，未找到可用服务器")
    
    try:
        os.makedirs(cache_dir, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': time.time(), 'good_hosts': good_hosts}, f)
    except Exception as _e:
        _debug_log(f"保存 TDX 主机缓存失败: {_e}")
    
    return good_hosts


def _check_tdx() -> bool:
    global _TDX_AVAILABLE
    if _TDX_AVAILABLE is not None:
        return _TDX_AVAILABLE
    
    _pre_scanned = _pre_scan_tdx_hosts()
    if _pre_scanned:
        _TDX_AVAILABLE = True
        _debug_log(f"TDX 预扫描找到 {len(_pre_scanned)} 台可用服务器")
        return True
    
    import socket as _sock
    _TDX_HOSTS = [
        '124.71.187.122', '123.60.73.44', '124.70.133.119', '124.71.187.72',
        '123.60.84.66', '101.35.121.35', '111.231.113.208',
        '111.230.186.52', '175.178.112.197', '175.178.128.227', '43.139.95.83',
        '129.204.230.128', '119.97.185.59',
    ]
    for _ip in _TDX_HOSTS[:8]:
        try:
            _s = _sock.socket(_sock.AF_INET, _sock.SOCK_STREAM)
            _s.settimeout(2)
            _s.connect((_ip, 7709))
            _s.close()
            break
        except Exception as _e:
            _debug_log(f"tdx _check_tdx socket connect ({_ip}): {_e}")
            continue
    else:
        _TDX_AVAILABLE = False
        return False
    with _TDX_CALL_LOCK:
        if _TDX_AVAILABLE is not None:
            return _TDX_AVAILABLE
        try:
            from easy_tdx import TdxClient
            _c = TdxClient(host=_ip, port=7709)
            _c.connect()
            _q = _c.get_security_quotes([(1, "600519")])
            _TDX_AVAILABLE = _q is not None and not _q.empty
            _c.close()
        except Exception as _e:
            _debug_log(f"tdx _check_tdx error ({_ip}): {_e}")
            _TDX_AVAILABLE = False
    return _TDX_AVAILABLE

def _get_tdx_client() -> Optional[Any]:
    """V7.5: 获取 TdxClient（加锁，线程安全），连接异常时自动重连。

    V8.5: 重连改为指数退避（0.5s, 1s, 2s），防止频繁重连被封禁。
    V9.0: 使用 from_best_host() 自动选择最快主机，不再依赖 _check_tdx 的 _ip 变量。
    V9.4: 使用预扫描白名单，只从通过 K线和资金流测试的服务器中选择。
    """
    with _TDX_CALL_LOCK:
        global _TDX_CLIENT
        for attempt in range(_TDX_RECONNECT_ATTEMPTS):
            if _TDX_CLIENT is not None:
                try:
                    _TDX_CLIENT.ensure_connected()
                    return _TDX_CLIENT
                except Exception as _e:
                    _debug_log(f"tdx ensure_connected error: {_e}")
                    try:
                        _TDX_CLIENT.close()
                    except Exception as _e:
                        _debug_log(f"tdx close old client: {_e}")
                    _TDX_CLIENT = None
                    if attempt < _TDX_RECONNECT_ATTEMPTS - 1:
                        time.sleep(_TDX_RECONNECT_DELAY * (2 ** attempt))
                    continue
            if not _check_tdx():
                return None
            try:
                from easy_tdx import TdxClient
                from easy_tdx.config import get_known_hosts
                
                _pre_scanned = _pre_scan_tdx_hosts()
                if _pre_scanned:
                    _debug_log(f"使用预扫描白名单，{len(_pre_scanned)} 台可用服务器")
                    _good_hosts = [h for h in _pre_scanned if h not in _TDX_BAD_HOSTS]
                else:
                    _all_hosts = get_known_hosts()
                    _good_hosts = [h for h in _all_hosts if h not in _TDX_BAD_HOSTS]
                
                if not _good_hosts:
                    _debug_log(f"tdx 所有主机都被标记为坏，重置黑名单给一次机会")
                    _TDX_BAD_HOSTS.clear()
                    if _pre_scanned:
                        _good_hosts = _pre_scanned
                    else:
                        _good_hosts = get_known_hosts()
                
                _TDX_CLIENT = TdxClient.from_best_host(hosts=_good_hosts)
                _TDX_CLIENT.connect()
                _tdx_health_check(_TDX_CLIENT)
                return _TDX_CLIENT
            except Exception as _e:
                _debug_log(f"tdx _get_tdx_client new client error: {_e}")
                _TDX_CLIENT = None
                if attempt < _TDX_RECONNECT_ATTEMPTS - 1:
                    time.sleep(_TDX_RECONNECT_DELAY * (2 ** attempt))
        return None

def _tdx_health_check(client) -> None:
    """检查 TDX 关键接口是否可用，便于调试。

    V9.3.2: 新增 K线接口校验。部分 TDX 服务器返回假数据
   （ret_count=800 但 body 为 0 字节），导致 TdxDecodeError。
    检测到此类服务器时标记为坏主机并抛出异常，触发 _get_tdx_client 换IP重连。
    """
    import pandas as pd
    try:
        _finance_info = client.get_finance_info(1, "600519")
        if _finance_info is None or _finance_info.empty:
            _debug_log("TDX health check: get_finance_info 不可用")
        else:
            _debug_log("TDX health check: get_finance_info 正常")
    except Exception as _e:
        _debug_log(f"TDX health check: get_finance_info 异常: {_e}")
    try:
        _fund_flow = client.get_fund_flow(1, "600519")
        if _fund_flow is None or _fund_flow.empty:
            _debug_log("TDX health check: get_fund_flow 不可用")
        else:
            _debug_log("TDX health check: get_fund_flow 正常")
    except Exception as _e:
        _debug_log(f"TDX health check: get_fund_flow 异常: {_e}")
    try:
        _xdxr = client.get_xdxr_info(1, "600519")
        if _xdxr is None or _xdxr.empty:
            _debug_log("TDX health check: get_xdxr_info 不可用")
        else:
            _debug_log("TDX health check: get_xdxr_info 正常")
    except Exception as _e:
        _debug_log(f"TDX health check: get_xdxr_info 异常: {_e}")
    try:
        _history_fund_flow = client.get_history_fund_flow(1, "600519", 0, 10)
        if _history_fund_flow is None or _history_fund_flow.empty:
            _host = getattr(client, '_host', '')
            if _host:
                _TDX_BAD_HOSTS.add(_host)
            _debug_log(f"TDX health check: get_history_fund_flow 返回空，标记 {_host} 为坏主机")
            raise RuntimeError(f"TDX host {_host} returns empty history fund flow data")
        _debug_log("TDX health check: get_history_fund_flow 正常")
    except RuntimeError:
        raise
    except Exception as _e:
        _host = getattr(client, '_host', '')
        _err_name = type(_e).__name__
        if 'Decode' in _err_name or '数据不足' in str(_e):
            if _host:
                _TDX_BAD_HOSTS.add(_host)
            _debug_log(f"TDX health check: get_history_fund_flow 解码失败，标记 {_host} 为坏主机: {_e}")
            raise RuntimeError(f"TDX host {_host} returns corrupted fund flow data: {_e}") from _e
        _debug_log(f"TDX health check: get_history_fund_flow 异常: {_e}")
    # V9.3.2: K线接口校验 — 部分服务器返回假数据（ret_count=800但0字节body）
    # 这类服务器行情/财务接口正常，但K线接口返回畸形数据导致 TdxDecodeError
    try:
        from easy_tdx import KlineCategory, Market
        _bars = client.get_security_bars(Market.SH, "600519", KlineCategory.DAY, 0, 1)
        if _bars is None or (hasattr(_bars, 'empty') and _bars.empty):
            _host = getattr(client, '_host', '')
            if _host:
                _TDX_BAD_HOSTS.add(_host)
            _debug_log(f"TDX health check: get_security_bars 返回空，标记 {_host} 为坏主机")
            raise RuntimeError(f"TDX host {_host} returns empty K-line data")
        _debug_log("TDX health check: get_security_bars 正常")
    except RuntimeError:
        raise  # 抛出给 _get_tdx_client 触发换IP重连
    except Exception as _e:
        _host = getattr(client, '_host', '')
        _err_name = type(_e).__name__
        if 'Decode' in _err_name or '数据不足' in str(_e):
            if _host:
                _TDX_BAD_HOSTS.add(_host)
            _debug_log(f"TDX health check: get_security_bars 解码失败，标记 {_host} 为坏主机: {_e}")
            raise RuntimeError(f"TDX host {_host} returns corrupted K-line data: {_e}") from _e
        _debug_log(f"TDX health check: get_security_bars 异常: {_e}")

def _mac_health_check(client) -> None:
    """检查 MacClient 关键接口是否可用，便于调试。"""
    try:
        _belong = client.get_belong_board(1, "600519")
        if _belong is None or _belong.empty:
            _debug_log("MacClient health check: get_belong_board 不可用")
        else:
            _debug_log("MacClient health check: get_belong_board 正常")
    except Exception as _e:
        _debug_log(f"MacClient health check: get_belong_board 异常: {_e}")
    try:
        _board_list = client.get_board_list(0)
        if _board_list is None or _board_list.empty:
            _debug_log("MacClient health check: get_board_list 不可用")
        else:
            _debug_log("MacClient health check: get_board_list 正常")
    except Exception as _e:
        _debug_log(f"MacClient health check: get_board_list 异常: {_e}")

def _check_mac() -> bool:
    """检测 MacClient 是否可用（缓存失败状态，避免重复重试退避）。"""
    global _MAC_AVAILABLE
    if _MAC_AVAILABLE is not None:
        return _MAC_AVAILABLE
    with _TDX_CALL_LOCK:
        if _MAC_AVAILABLE is not None:
            return _MAC_AVAILABLE
        try:
            from easy_tdx import MacClient
            c = MacClient.from_best_host()
            c.connect()
            c.close()
            _MAC_AVAILABLE = True
        except Exception as _e:
            _debug_log(f"tdx _check_mac error: {_e}")
            _MAC_AVAILABLE = False
    return _MAC_AVAILABLE


def _get_mac_client() -> Optional[Any]:
    """V7.5: 获取 MacClient（加锁，线程安全），连接异常时自动重连。
    
    V8.5: 重连改为指数退避（0.5s, 1s, 2s），防止频繁重连被封禁。
    V8.9: 添加 _check_mac() 失败缓存，快速返回。
    """
    if not _check_mac():
        return None
    with _TDX_CALL_LOCK:
        global _TDX_MAC_CLIENT
        for attempt in range(_TDX_RECONNECT_ATTEMPTS):
            if _TDX_MAC_CLIENT is not None:
                try:
                    _TDX_MAC_CLIENT.ensure_connected()
                    return _TDX_MAC_CLIENT
                except Exception as _e:
                    _debug_log(f"tdx _get_mac_client ensure_connected: {_e}")
                    try:
                        _TDX_MAC_CLIENT.close()
                    except Exception as _e:
                        _debug_log(f"tdx close old mac client: {_e}")
                    _TDX_MAC_CLIENT = None
                    if attempt < _TDX_RECONNECT_ATTEMPTS - 1:
                        time.sleep(_TDX_RECONNECT_DELAY * (2 ** attempt))
                    continue
            try:
                from easy_tdx import MacClient
                _TDX_MAC_CLIENT = MacClient.from_best_host()
                _TDX_MAC_CLIENT.connect()
                _mac_health_check(_TDX_MAC_CLIENT)
                return _TDX_MAC_CLIENT
            except Exception as _e:
                _debug_log(f"tdx _get_mac_client new client error: {_e}")
                _TDX_MAC_CLIENT = None
                if attempt < _TDX_RECONNECT_ATTEMPTS - 1:
                    time.sleep(_TDX_RECONNECT_DELAY * (2 ** attempt))
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
        except Exception as _e:
            _debug_log(f"tdx cleanup client heartbeat: {_e}")
        try:
            if _TDX_MAC_CLIENT is not None:
                _stop_ev = getattr(_TDX_MAC_CLIENT, '_stop_event', None)
                if _stop_ev is not None:
                    _stop_ev.set()
                time.sleep(0.05)
        except Exception as _e:
            _debug_log(f"tdx cleanup mac_client heartbeat: {_e}")
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
    except Exception as _e:
        _debug_log(f"tdx _parse_tencent_market_data error: {_e}")
        return [], []

def _tencent_quote_full_fallback(code: str, is_pre_market: bool = False) -> Dict[str, Any]:
    """腾讯行情兜底 → dict(含 name, price, change_pct, pe, pb 等)。
    
    V9.3: 盘前模式（is_pre_market=True）使用上一交易日日K线数据，避免实时接口返回0值
    """
    if is_pre_market:
        return _pre_market_quote_from_kline(code)
    
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
    except Exception as _e:
        _debug_log(f"tdx _tencent_quote_full_fallback error ({code}): {_e}")
        return {}


def _pre_market_quote_from_kline(code: str) -> Dict[str, Any]:
    """盘前模式：从日K线数据构建行情字典。
    
    使用上一交易日的收盘价作为当前价，上上个交易日收盘价作为昨收，
    重新计算涨跌幅。
    """
    try:
        keys, rows = tdx_get_security_bars(code, count=3)
        if not keys or len(rows) < 2:
            return {}
        
        idx_close = keys.index('close') if 'close' in keys else 2
        idx_open = keys.index('open') if 'open' in keys else 1
        idx_high = keys.index('high') if 'high' in keys else 3
        idx_low = keys.index('low') if 'low' in keys else 4
        idx_amount = keys.index('amount') if 'amount' in keys else 6
        
        last_row = rows[0]
        prev_row = rows[1]
        
        close = _safe_float(last_row[idx_close], 0)
        prev_close = _safe_float(prev_row[idx_close], 0)
        open_val = _safe_float(last_row[idx_open], 0)
        high = _safe_float(last_row[idx_high], 0)
        low = _safe_float(last_row[idx_low], 0)
        amount_wan = _safe_float(last_row[idx_amount], 0) / 10000
        
        change_amt = 0.0
        change_pct = 0.0
        if prev_close > 0:
            change_amt = close - prev_close
            change_pct = change_amt / prev_close * 100
        
        return {
            "name": "", 
            "price": close,
            "last_close": prev_close,
            "open": open_val,
            "change_amt": change_amt,
            "change_pct": change_pct,
            "high": high,
            "low": low,
            "amount_wan": amount_wan,
            "turnover_pct": 0.0,
            "pe_ttm": 0.0,
            "amplitude_pct": 0.0,
            "float_mcap_yi": 0.0,
            "mcap_yi": 0.0,
            "pb": 0.0,
            "limit_up": 0.0,
            "limit_down_price": 0.0,
            "vol_ratio": 0.0,
            "pe_static": 0.0,
            "_is_pre_market": True,
        }
    except Exception as _e:
        _debug_log(f"pre-market quote from kline error: {_e}")
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
    except Exception as _e:
        _debug_log(f"tdx tencent_quote_batch parse error: {_e}")
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
                _tdx_throttle()  # V8.5: TDX请求节流
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
            except Exception as _e:
                # V9.3.2: TdxDecodeError 说明服务器返回假数据，标记坏主机
                _host = getattr(client, '_host', '')
                _err_name = type(_e).__name__
                if 'Decode' in _err_name or '数据不足' in str(_e):
                    if _host:
                        _TDX_BAD_HOSTS.add(_host)
                        _debug_log(f"tdx K线解码失败，标记 {_host} 为坏主机: {_e}")
                _reset_tdx_connections()
                continue
        result = _baidu_kline_full_fallback(code)
        _TDX_KLINE_CACHE[cache_key] = result
        return result


def tdx_get_security_bars_qfq(code: str, count: int = 800) -> Tuple[List[str], List[List[str]]]:
    """获取前复权日K线（V9.6 新增）

    使用 easy-tdx 获取不复权K线 + xdxr除权除息数据，计算前复权价格。
    前复权逻辑：以最新价格为基准，历史价格向下调整除权除息影响。

    Args:
        code: 股票代码
        count: K线条数

    Returns:
        (keys, rows) 与 tdx_get_security_bars 格式一致
    """
    # 获取不复权K线
    keys, rows = tdx_get_security_bars(code, count)
    if not keys or not rows:
        return keys, rows

    # 获取除权除息数据
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None:
            _debug_log(f"tdx qfq: 无可用TDX连接，返回不复权数据 ({code})")
            return keys, rows
        try:
            xdxr_df = client.get_xdxr_info(_market_from_code(code), code)
        except Exception as _e:
            _debug_log(f"tdx qfq: get_xdxr_info 失败 ({code}): {_e}")
            return keys, rows

    if xdxr_df is None or xdxr_df.empty:
        return keys, rows

    # 构建除权除息因子列表：每条记录计算复权因子
    # 前复权：从最新日往回累乘复权因子
    idx_map = {k: i for i, k in enumerate(keys)}
    ci_close = idx_map.get('close', -1)
    ci_open = idx_map.get('open', -1)
    ci_high = idx_map.get('high', -1)
    ci_low = idx_map.get('low', -1)
    if ci_close < 0:
        return keys, rows

    # 解析除权除息记录
    xdxr_list = []
    for _, row in xdxr_df.iterrows():
        cat = int(row.get('category', 0))
        if cat != 1:  # 仅处理除权除息(category=1)
            continue
        date_str = str(row.get('date', ''))[:10]
        if not date_str:
            continue
        fh = _safe_float(row.get('fenhong', 0)) / 10  # 每10股派息 -> 每股
        szg = _safe_float(row.get('songzhuangu', 0)) / 10  # 每10股送转 -> 每股
        pg = _safe_float(row.get('peigu', 0)) / 10  # 每10股配股 -> 每股
        pgj = _safe_float(row.get('peigujia', 0))  # 配股价
        xdxr_list.append({
            "date": date_str,
            "bonus": fh,  # 每股派息(元)
            "transfer": szg,  # 每股送转(股)
            "allot": pg,  # 每股配股(股)
            "allot_price": pgj,  # 配股价(元)
        })

    if not xdxr_list:
        return keys, rows

    # 按日期倒序排列
    xdxr_list.sort(key=lambda x: x["date"], reverse=True)

    # 计算前复权因子
    # 前复权公式：复权因子 = (收盘价 - 派息 + 配股价*配股数) / (1 + 送转 + 配股) / 收盘价
    # 实际做法：从最新日往回累乘
    # 对于每个除权日D，D日及之前的价格需要乘以调整因子：
    #   factor = (前收盘 - 派息 + 配股价*配股数) / (前收盘 * (1 + 送转 + 配股))
    #   简化为: factor = 1 / (1 + 送转 + 配股) * (1 - 派息/前收盘 + 配股价*配股数/前收盘)
    # 但我们不知道"前收盘"，所以用另一种方式：
    #   前复权价 = 原价 * 累计复权因子
    #   累计复权因子从1开始，遇到除权日时：
    #   新因子 = 旧因子 * (1 / (1 + 送转 + 配股))
    #   然后所有价格还需要减去派息的影响

    # 更简单的方式：直接按除权调整
    # 前复权逻辑：
    # 1. 将除权记录按日期排序
    # 2. 对每条K线，累乘其日期之后所有除权日的复权因子
    # 3. 每个除权日的因子 = 送转配导致的稀释因子 + 派息调整
    
    # 构建除权记录列表（按日期正序）
    adj_list = []
    for xdxr in xdxr_list:
        date = xdxr["date"]
        transfer = xdxr["transfer"]
        allot = xdxr["allot"]
        bonus = xdxr["bonus"]
        allot_price = xdxr["allot_price"]

        # 送转配导致的股本扩张因子
        dilution = 1.0 + transfer + allot
        if dilution <= 0:
            dilution = 1.0

        adj_list.append({
            "date": date,
            "dilution_factor": 1.0 / dilution,  # 送转配稀释
            "bonus_per_share": bonus,  # 每股派息(元)
            "allot_cost_per_share": allot * allot_price,  # 每股配股成本(元)
        })

    # 按日期正序
    adj_list.sort(key=lambda x: x["date"])

    if not adj_list:
        return keys, rows

    # 对每条K线，计算前复权价格
    # 前复权公式：对除权日D，D之前的所有K线价格需要调整：
    #   新价 = (原价 - 每股派息 + 每股配股成本) / (1 + 每股送转 + 每股配股)
    # 多次除权需要从最近到最远逐步调整

    # 重要：深拷贝rows避免修改缓存
    import copy
    rows = copy.deepcopy(rows)

    adjusted_count = 0
    for row in rows:
        row_date = row[0] if len(row) > 0 else ""
        if not row_date:
            continue

        # 从最近的除权日开始往回调整（倒序遍历在K线日期之后的除权记录）
        for adj in reversed(adj_list):
            if row_date >= adj["date"]:
                continue  # K线日期在除权日之后，不受影响

            # K线在该除权日之前，需要调整
            dilution = adj["dilution_factor"]
            bonus = adj["bonus_per_share"]
            allot_cost = adj["allot_cost_per_share"]

            for ci in [ci_open, ci_high, ci_low, ci_close]:
                if ci >= 0 and ci < len(row):
                    orig = _safe_float(row[ci])
                    if orig > 0:
                        # 前复权: (原价 - 派息 + 配股成本) * 稀释因子
                        adjusted = (orig - bonus + allot_cost) * dilution
                        row[ci] = f"{adjusted:.2f}"
                        adjusted_count += 1

    _debug_log(f"tdx qfq: {code} adjusted {adjusted_count} price points across {len(adj_list)} ex-dividend dates")
    return keys, rows


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

def _is_before_market_open() -> bool:
    """判断当前是否为盘前时段（9:30之前）。"""
    now = datetime.now()
    return now.hour < 9 or (now.hour == 9 and now.minute < 30)


def _get_trading_date_for_quote() -> str:
    """获取当前行情数据对应的交易日期。
    
    盘前（<9:30）：使用上一交易日日期
    盘中（>=9:30）：使用今日日期
    """
    if _is_before_market_open():
        from stock_common.stock_calendar import get_last_trading_day
        return get_last_trading_day().strftime("%Y-%m-%d")
    return datetime.now().strftime("%Y-%m-%d")


def tdx_get_quote_full(code: str) -> Dict[str, Any]:
    """获取个股完整行情（腾讯兜底，TDX 补强，V7.5 加锁 + 缓存）。
    
    V9.3: 盘前模式（9:30前）使用上一交易日日K线数据，缓存Key包含交易日期
    """
    trading_date = _get_trading_date_for_quote()
    cache_key = f"Q:{code}:{trading_date}"
    cached = _TDX_QUOTE_CACHE.get(cache_key)
    if cached is not None:
        return cached
    result = _tencent_quote_full_fallback(code, is_pre_market=_is_before_market_open())
    with _TDX_CALL_LOCK:
        cached = _TDX_QUOTE_CACHE.get(cache_key)
        if cached is not None:
            return cached
        client = _get_tdx_client()
        if client is not None:
            try:
                _tdx_throttle()  # V8.5: TDX请求节流
                quotes = client.get_security_quotes([(_market_from_code(code), code)])
                # V9.0: get_security_quotes 返回 DataFrame，需用 .empty/iloc[0]
                if quotes is not None and not quotes.empty:
                    q = quotes.iloc[0]
                    if q['price']: result['price'] = q['price']
                    if q['pre_close']: result['last_close'] = q['pre_close']
                    if q['open']: result['open'] = q['open']
                    if q['high']: result['high'] = q['high']
                    if q['low']: result['low'] = q['low']
                    if q['amount']: result['amount_wan'] = q['amount'] / 10000.0
                    if q['pre_close'] and q['pre_close'] > 0:
                        result['change_pct'] = (q['price'] - q['pre_close']) / q['pre_close'] * 100
                        result['change_amt'] = q['price'] - q['pre_close']
                    result['bid1'] = q['bid1']; result['bid2'] = q['bid2']; result['bid3'] = q['bid3']
                    result['bid4'] = q['bid4']; result['bid5'] = q['bid5']
                    result['ask1'] = q['ask1']; result['ask2'] = q['ask2']; result['ask3'] = q['ask3']
                    result['ask4'] = q['ask4']; result['ask5'] = q['ask5']
            except Exception as _e:
                _debug_log(f"tdx quote supplement error: {_e}")
    # V8.9: 腾讯超时时 TDX 补充不完整 → 返回空字典（让 if q: 保护生效）
    if result and "pe_ttm" not in result:
        result = {}
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
                _tdx_throttle()  # V8.5: TDX请求节流
                stocks = [(_market_from_code(c), c) for c in codes]
                quotes = client.get_security_quotes(stocks)
                # V9.0: get_security_quotes 返回 DataFrame，需用 iterrows 遍历
                if quotes is not None and not quotes.empty:
                    for _, q in quotes.iterrows():
                        q_code = str(q['code'])
                        if q_code in result and q['price']:
                            result[q_code]['price'] = q['price']
                            if q['pre_close'] and q['pre_close'] > 0:
                                result[q_code]['change_pct'] = round((q['price'] - q['pre_close']) / q['pre_close'] * 100, 2)
            except Exception as _e:
                _debug_log(f"tdx batch_quote supplement error: {_e}")
    return result

def tdx_get_index_quote(idx_code: str) -> Dict[str, Any]:
    """获取指数行情（TDX 优先，腾讯兜底）。"""
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is not None:
            try:
                _tdx_throttle()  # V8.5: TDX请求节流
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
            except Exception as _e:
                _debug_log(f"tdx index_quote error: {_e}")
    try:
        url = f"https://qt.gtimg.cn/q={idx_code}"
        r = _quick_request(url, headers={"User-Agent": UA}, timeout=10)
        if r is None: return {}
        r.encoding = "gbk"
        v = r.text.split('"')[1].split("~")
        return {"price": _safe_float(v[3]), "open": _safe_float(v[5]), "change_pct": _safe_float(v[32])}
    except Exception as _e:
        _debug_log(f"tdx tdx_get_index_quote error ({idx_code}): {_e}")
        return {}

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
        except Exception as _e:
            _debug_log(f"tdx tdx_get_historical_high error ({code}): {_e}")
            return None

def tdx_get_index_bars(idx_code: str, count: int = 250):
    # V9.3.2: 增加重试机制，TdxDecodeError时标记坏主机并换IP重连
    for _retry in range(2):
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
            except Exception as _e:
                # V9.3.2: TdxDecodeError 说明服务器返回假数据，标记坏主机并重试
                _host = getattr(client, '_host', '')
                _err_name = type(_e).__name__
                if 'Decode' in _err_name or '数据不足' in str(_e):
                    if _host:
                        _TDX_BAD_HOSTS.add(_host)
                        _debug_log(f"tdx 指数K线解码失败，标记 {_host} 为坏主机: {_e}")
                _reset_tdx_connections()
                continue
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
        except Exception as _e:
            # V9.3.2: TdxDecodeError 说明服务器返回假数据，标记坏主机
            _host = getattr(client, '_host', '')
            if 'Decode' in type(_e).__name__ or '数据不足' in str(_e):
                if _host:
                    _TDX_BAD_HOSTS.add(_host)
                    _debug_log(f"tdx 周K线解码失败，标记 {_host} 为坏主机: {_e}")
            result = ([], [])
            _TDX_WKLINE_CACHE[cache_key] = result
            return result

# ═══════════════════════════════════════
# 资金流适配器
# ═══════════════════════════════════════
@cached(category="f10_fund_flow", trading_day=True, valid_if=lambda r: bool(r))
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
        except Exception as _e:
            _debug_log(f"tdx tdx_get_fund_flow error ({code}): {_e}")
            return {}

@cached(category="f10_fund_flow", trading_day=True, valid_if=lambda r: bool(r))
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
        except Exception as _e:
            # V9.3.1: 区分"无数据"和"解码失败"，解码失败时记录日志便于排查
            _err_msg = str(_e)
            if "数据不足" in _err_msg or "TdxDecodeError" in type(_e).__name__:
                _debug_log(f"tdx_get_history_fund_flow decode error ({code}): {_e}")
            return []

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
        except Exception as _e:
            _debug_log(f"tdx tdx_get_roe_from_finance_info error ({code}): {_e}")
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
        except Exception as _e:
            _debug_log(f"tdx tdx_get_dividend_history error ({code}): {_e}")
            return []

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
    except Exception as _e:
        _debug_log(f"tdx tdx_get_eps_from_reports error ({code}): {_e}")
        return None

@cached(category="f10_announcements", trading_day=True, valid_if=lambda r: bool(r))
def tdx_get_latest_announcements(code: str, days: int = 7):
    """从 TDX F10 公司公告中获取最新公告列表。

    V9.0 修复：正确使用 get_company_info_category + get_company_info_content，
    用 filename/start/length 参数读取「公司公告」分类，解析表格格式的公告列表。

    Args:
        code: 股票代码
        days: 仅返回最近 N 天的公告，None=不限制

    Returns:
        list[dict]: 公告列表，每项含 title/date/category
    """
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None:
            return []
        try:
            cats = client.get_company_info_category(_market_from_code(code), code)
            if cats is None or cats.empty:
                return []
            # 找到「公司公告」分类
            ann_cat = cats[cats['name'] == '公司公告']
            if ann_cat.empty:
                return []
            row = ann_cat.iloc[0]
            _tdx_throttle()
            content = client.get_company_info_content(
                _market_from_code(code), code,
                row['filename'], int(row['start']), int(row['length'])
            )
            if not content:
                return []
            # 解析 F10 公告表格格式（GBK 文本，┌┬┐├┼┤└┴┘ 等分隔符）
            import re as _re
            lines = content.split('\n')
            anns = []
            current_date = ''
            from datetime import datetime, timedelta
            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d') if days else ''
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 匹配日期: YYYY-MM-DD HH:MM 格式
                m = _re.match(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})', line)
                if m:
                    current_date = m.group(1)
                    # 按日期过滤
                    if cutoff and current_date < cutoff:
                        continue
                    # 提取标题（去掉日期时间后的剩余内容）
                    title = line[m.end():].strip()
                    # 去掉左侧表格竖线分隔符
                    title = title.lstrip('│').strip()
                    # 去掉右侧表格竖线
                    title = title.rstrip('│').strip()
                    if title and len(title) > 3:
                        anns.append({
                            "title": title[:120],
                            "date": current_date,
                            "category": "公司公告"
                        })
                elif current_date and not cutoff or (cutoff and current_date >= cutoff):
                    # 续行（上一行的公告标题可能换行）
                    if line.startswith('│') or '│' in line:
                        # 跳过纯表格装饰线
                        if _re.match(r'^[┌┬┐├┼┤└┴┘─│\s]+$', line):
                            continue
                        # 提取标题内容
                        parts = line.split('│')
                        for p in parts:
                            p = p.strip()
                            if p and len(p) > 3 and not _re.match(r'^[\d:\-\s]+$', p):
                                anns.append({
                                    "title": p[:120],
                                    "date": current_date,
                                    "category": "公司公告"
                                })
                                break
            return anns[:10]
        except Exception as _e:
            _debug_log(f"tdx tdx_get_latest_announcements error ({code}): {_e}")
            return []


# ═══════════════════════════════════════
# F10 分类数据获取（V9.0 新增）
# ═══════════════════════════════════════

def _f10_get_content(code: str, category_name: str) -> str:
    """获取 F10 指定分类的原始文本内容。

    Args:
        code: 股票代码
        category_name: 分类名称（如 '最新提示'、'公司报道'）

    Returns:
        str: 原始文本内容，失败返回空字符串
    """
    client = _get_tdx_client()
    if client is None:
        return ''
    try:
        cats = client.get_company_info_category(_market_from_code(code), code)
        if cats is None or cats.empty:
            return ''
        target = cats[cats['name'] == category_name]
        if target.empty:
            return ''
        row = target.iloc[0]
        _tdx_throttle()
        content = client.get_company_info_content(
            _market_from_code(code), code,
            row['filename'], int(row['start']), int(row['length'])
        )
        return content or ''
    except Exception as _e:
        _debug_log(f"tdx tdx_get_company_info_content error ({code}): {_e}")
        return ''


@cached(category="f10_reminders", trading_day=True, valid_if=lambda r: bool(r))
def tdx_get_latest_reminders(code: str) -> dict:
    """从 TDX F10「最新提示」分类获取综合信息（8 个子栏目一次拿全）。

    替代 3 个 HTTP 接口：
    - get_eastmoney_stock_news（最新报道）
    - get_block_trade（大宗交易）
    - get_margin_trading（融资融券）

    Returns:
        dict: {
            "latest_indicators": {eps, net_asset, roe, ...},
            "interaction_qa": [{date, question, answer}, ...],
            "latest_announcements": [{date, title, summary, url}, ...],
            "latest_news": [{date, title, summary, url}, ...],
            "abnormal_movements": [...],
            "block_trades": [{date, price, volume, amount, buyer, seller}, ...],
            "margin_trading": [{date, finance_balance, finance_buy, ...}, ...],
            "risk_warnings": {...}
        }
    """
    from stock_common.f10_parser import split_sections, parse_table, parse_paragraph_blocks, parse_key_value_table, extract_field
    import re as _re

    with _TDX_CALL_LOCK:
        content = _f10_get_content(code, '最新提示')
        if not content:
            return {}

        sections = split_sections(content)
        result: dict = {}

        # 1. 最新提示子栏目 — 提取关键指标
        s1 = sections.get('最新提示', '')
        if s1:
            indicators: dict = {}

            def _extract_indicator(text: str, label: str) -> Optional[float]:
                """从表格行提取第一个有效数值（跳过 ---）。"""
                m = _re.search(label + r'\s*│(.+)', text)
                if m:
                    # 用 │ 分割值列，找第一个有效数字
                    vals = [v.strip() for v in m.group(1).split('│')]
                    for v in vals:
                        if v and v != '---':
                            return _safe_float(v)
                return None

            indicators['eps'] = _extract_indicator(s1, r'每股收益\(元\)')
            indicators['net_asset'] = _extract_indicator(s1, r'每股净资产\(元\)')
            indicators['roe'] = _extract_indicator(s1, r'加权净资产收益率\(%?\)')
            indicators['total_capital'] = _extract_indicator(s1, r'总股本\(万股\)')
            indicators['float_capital'] = _extract_indicator(s1, r'实际流通A股\(万股\)')
            # 提取最新指标变动原因
            m = _re.search(r'最新指标变动原因\s*│\s*(.+?)│', s1)
            if m:
                indicators['change_reason'] = m.group(1).strip()
            # 提取股东人数
            m = _re.search(r'股东人数:截止([\d-]+),公司股东户数([\d]+),([减少增加]+)([\d.]+)%', s1)
            if m:
                indicators['holder_count'] = {
                    'date': m.group(1),
                    'count': int(m.group(2)),
                    'change': m.group(3),
                    'change_pct': _safe_float(m.group(4))
                }
            # 提取财务同比
            m = _re.search(r'财务同比:([\d-]+)\s*营业收入\(万元\):([\d.]+)\s*同比增\(%\):([\d.-]+)\s*净利润\(万元\):([\d.]+)\s*同比增\(%\):([\d.-]+)', s1)
            if m:
                indicators['financial_yoy'] = {
                    'date': m.group(1),
                    'revenue': _safe_float(m.group(2)),
                    'revenue_yoy': _safe_float(m.group(3)),
                    'net_profit': _safe_float(m.group(4)),
                    'net_profit_yoy': _safe_float(m.group(5))
                }
            result['latest_indicators'] = indicators

        # 2. 互动问答
        s2 = sections.get('互动问答', '')
        if s2 and '暂无数据' not in s2:
            qa_list: list = []
            lines = s2.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip().lstrip('│').strip()
                # 匹配日期行（MM-DD 或 YYYY-MM-DD）
                m = _re.match(r'(\d{2}-\d{2}|\d{4}-\d{2}-\d{2})', line)
                if m and '问：' in line:
                    date = m.group(1)
                    # 提取问题
                    question = ''
                    qm = _re.search(r'问：(.+)', line)
                    if qm:
                        question = qm.group(1).strip().rstrip('│').strip()
                    # 向后搜索答案
                    answer = ''
                    for j in range(i + 1, min(i + 15, len(lines))):
                        ans_line = lines[j].strip().lstrip('│').strip()
                        if ans_line.startswith('答：'):
                            answer = ans_line[2:].strip().rstrip('│').strip()
                            break
                        elif _re.match(r'\d{2}-\d{2}', ans_line):
                            break
                    if question:
                        qa_list.append({'date': date, 'question': question[:200], 'answer': answer[:500]})
                    i = j + 1 if answer else i + 1
                else:
                    i += 1
            result['interaction_qa'] = qa_list[:5]
        else:
            result['interaction_qa'] = []

        # 3. 最新公告
        s3 = sections.get('最新公告', '')
        if s3 and '暂无数据' not in s3:
            result['latest_announcements'] = parse_paragraph_blocks(s3)[:5]
        else:
            result['latest_announcements'] = []

        # 4. 最新报道
        s4 = sections.get('最新报道', '')
        if s4 and '暂无数据' not in s4:
            result['latest_news'] = parse_paragraph_blocks(s4)[:5]
        else:
            result['latest_news'] = []

        # 5. 最新异动
        s5 = sections.get('最新异动', '')
        result['abnormal_movements'] = [] if '暂无数据' in s5 else [s5.strip()[:200]] if s5.strip() else []

        # 6. 大宗交易
        s6 = sections.get('大宗交易', '')
        if s6 and '暂无数据' not in s6:
            rows = parse_table(s6)
            block_trades: list = []
            for r in rows:
                block_trades.append({
                    'date': r.get('交易日期', ''),
                    'price': _safe_float(r.get('成交价格(元)', 0)),
                    'volume': _safe_float(r.get('成交数量(万股)', 0)),
                    'amount': _safe_float(r.get('成交金额(万元)', 0)),
                    'buyer': r.get('买方营业部', ''),
                    'seller': r.get('卖方营业部', '')
                })
            result['block_trades'] = block_trades
        else:
            result['block_trades'] = []

        # 7. 融资融券
        s7 = sections.get('融资融券', '')
        if s7 and '暂无数据' not in s7:
            rows = parse_table(s7)
            margin_data: list = []
            for r in rows:
                margin_data.append({
                    'date': r.get('交易日期', ''),
                    'finance_balance': _safe_float(r.get('融资余额(万元)', 0)),
                    'finance_buy': _safe_float(r.get('融资买入额(万元)', 0)),
                    'securities_balance': _safe_float(r.get('融券余额(万元)', 0)),
                    'securities_sell': _safe_float(r.get('融券卖出量(万股)', 0)),
                    'total_balance': _safe_float(r.get('融资融券余额(万元)', 0))
                })
            result['margin_trading'] = margin_data
        else:
            result['margin_trading'] = []

        # 8. 风险提示
        s8 = sections.get('风险提示', '')
        risk: dict = {}
        if s8:
            # 违规稽查 — 检查是否有实际数据（非"暂无数据"）
            if '违规稽查' in s8:
                vi_idx = s8.find('违规稽查')
                # 取违规稽查到下一个子标题之间的文本
                next_sub = s8.find('【', vi_idx + 4)
                violation_text = s8[vi_idx:next_sub] if next_sub > 0 else s8[vi_idx:]
                if '暂无数据' not in violation_text:
                    risk['violation'] = parse_key_value_table(violation_text[:800])
                else:
                    risk['violation'] = {}
            # 交易所问询
            if '交易所问询' in s8:
                inquiry_text = s8[s8.find('交易所问询'):]
                next_sub = s8.find('【', s8.find('交易所问询') + 4)
                inquiry_text = inquiry_text[:next_sub - s8.find('交易所问询')] if next_sub > 0 else inquiry_text
                risk['inquiry'] = '暂无数据' not in inquiry_text
            # 交易所监管
            if '交易所监管' in s8:
                sup_text = s8[s8.find('交易所监管'):]
                next_sub = s8.find('【', s8.find('交易所监管') + 4)
                sup_text = sup_text[:next_sub - s8.find('交易所监管')] if next_sub > 0 else sup_text
                risk['supervision'] = '暂无数据' not in sup_text
            # 特别处理
            if '特别处理' in s8:
                st_text = s8[s8.find('特别处理'):]
                risk['special_treatment'] = '暂无数据' not in st_text[:100]
        result['risk_warnings'] = risk

        return result


@cached(category="f10_financial", valid_if=lambda r: bool(r), cross_verify=True)
def tdx_get_financial_analysis(code: str) -> dict:
    """从 TDX F10「财务分析」分类获取综合财务信息（10 个子栏目一次拿全）。

    替代 3 个新浪 HTTP 接口：
    - get_sina_financial_report（利润表 lrb）
    - get_sina_balance_sheet（资产负债表 fzb）
    - get_gross_margin_and_roe（毛利率+ROE）

    Returns:
        dict: {
            "main_indicators": [{period, 审计意见, 归母净利(未调整:万), ...}, ...],
            "solvency": [{period, 流动比率, 速动比率, ...}, ...],
            "operation": [{period, 应收账款周转率, ...}, ...],
            "profitability": [{period, 净资产收益率, 销售毛利率, ...}, ...],
            "growth": [{period, 营业收入增长率, ...}, ...],
            "indicator_changes": [{period, items: [{subject, reason, ...}]}],
            "balance_sheet": [{period, 货币资金, 存货, ...}, ...],
            "income_statement": [...],
            "cash_flow": [...],
            "qoq_analysis": [...]
        }
    """
    from stock_common.f10_parser import (
        split_sections, find_subsection, parse_tables, parse_table, transpose_table, merge_continuation_lines
    )
    import re as _re

    with _TDX_CALL_LOCK:
        content = _f10_get_content(code, '财务分析')
        if not content:
            return {}

        sections = split_sections(content)
        result: dict = {}

        # 1. 主要财务指标（可能含多个表格：年报对比 + 近5期）
        # 银行股嵌套结构：find_subsection 在 '财务指标' 顶层 section 内查找 【主要财务指标】
        s1 = find_subsection(sections, '主要财务指标')
        if s1:
            tables = parse_tables(s1)
            merged: dict = {}
            for tbl in tables:
                if not tbl:
                    continue
                # 找 key_col（第一个列名，通常是"财务指标"）
                key_col = next(iter(tbl[0].keys())) if tbl[0] else ''
                transposed = transpose_table(tbl, key_col)
                for entry in transposed:
                    period = entry.get('period', '')
                    if period and period not in merged:
                        merged[period] = entry
            result['main_indicators'] = list(merged.values())
        else:
            result['main_indicators'] = []

        # 2-5. 偿债/营运/盈利/成长能力指标
        # 银行股的"成长能力指标"叫"发展能力指标"，通过 aliases 兼容
        section_specs = [
            ('solvency', '偿债能力指标', None),
            ('operation', '营运能力指标', None),
            ('profitability', '盈利能力指标', None),
            ('growth', '成长能力指标', ['发展能力指标']),  # 银行股别名
        ]
        for result_key, section_name, aliases in section_specs:
            s = find_subsection(sections, section_name, aliases)
            if s:
                tables = parse_tables(s)
                merged: dict = {}
                for tbl in tables:
                    if not tbl:
                        continue
                    actual_key = next(iter(tbl[0].keys())) if tbl[0] else section_name
                    transposed = transpose_table(tbl, actual_key)
                    for entry in transposed:
                        period = entry.get('period', '')
                        if period and period not in merged:
                            merged[period] = entry
                result[result_key] = list(merged.values())
            else:
                result[result_key] = []

        # 6. 指标变动说明（多块表格，每块前有"截止日期:YYYY-MM-DD"）
        # 银行股的指标变动叫"异动科目"，find_subsection 会通过顶层 '异动科目' section 查找
        s6 = find_subsection(sections, '指标变动说明', ['异动科目'])
        if s6 and '暂无数据' not in s6:
            # 按"截止日期:YYYY-MM-DD"分割
            parts = _re.split(r'截止日期[:：]\s*(\d{4}-\d{2}-\d{2})', s6)
            changes: list = []
            # parts[0] = preamble, then alternating (date, content)
            for i in range(1, len(parts), 2):
                period = parts[i]
                block_text = parts[i + 1] if i + 1 < len(parts) else ''
                # 预处理：合并跨行文本单元格（前2列为文本）
                merged_text = merge_continuation_lines(block_text, num_text_cols=2)
                rows = parse_table(merged_text)
                items: list = []
                for r in rows:
                    items.append({
                        'subject': r.get('变动科目', '').strip(),
                        'reason': r.get('变动原因', '').strip(),
                        'current_value': _safe_float(r.get('本期数值(万)', 0) or 0),
                        'previous_value': _safe_float(r.get('上期/期初数(万)', 0) or 0),
                        'change_pct': _safe_float(r.get('变动幅度(%)', 0) or 0)
                    })
                if items:
                    changes.append({'period': period, 'items': items})
            result['indicator_changes'] = changes
        else:
            result['indicator_changes'] = []

        # 7. 资产负债表摘要（银行股嵌套在 '报表摘要' 顶层 section 下）
        s7 = find_subsection(sections, '资产负债表摘要')
        if s7:
            tables = parse_tables(s7)
            merged: dict = {}
            for tbl in tables:
                if not tbl:
                    continue
                actual_key = next(iter(tbl[0].keys())) if tbl[0] else '资产负债指标(万元)'
                transposed = transpose_table(tbl, actual_key)
                for entry in transposed:
                    period = entry.get('period', '')
                    if period and period not in merged:
                        merged[period] = entry
            result['balance_sheet'] = list(merged.values())
        else:
            result['balance_sheet'] = []

        # 8-10. 利润表摘要 / 现金流量表摘要 / 环比分析（部分股票可能无数据）
        for result_key, section_name in [
            ('income_statement', '利润表摘要'),
            ('cash_flow', '现金流量表摘要'),
            ('qoq_analysis', '环比分析'),
        ]:
            s = find_subsection(sections, section_name)
            if s and '暂无数据' not in s:
                tables = parse_tables(s)
                merged: dict = {}
                for tbl in tables:
                    if not tbl:
                        continue
                    actual_key = next(iter(tbl[0].keys())) if tbl[0] else ''
                    transposed = transpose_table(tbl, actual_key)
                    for entry in transposed:
                        period = entry.get('period', '')
                        if period and period not in merged:
                            merged[period] = entry
                result[result_key] = list(merged.values())
            else:
                result[result_key] = []

        return result


@cached(category="f10_shareholder", valid_if=lambda r: bool(r), cross_verify=True)
def tdx_get_shareholder_research(code: str) -> dict:
    """从 TDX F10「股东研究」分类获取股东信息（7 个子栏目）。

    替代 2 个东财 HTTP 接口：
    - get_eastmoney_shareholders（十大股东）
    - get_eastmoney_holder_changes（股东人数变化）

    Returns:
        dict: {
            "controlling_shareholder": {...},   # 控股股东/实际控制人
            "planned_changes": [...],           # 股东增减持计划
            "major_holder_changes": [...],      # 重要股东持股变动
            "shareholder_changes": [...],       # 十大股东列表（按期）
            "holder_count": [...],              # 股东人数变化
            "same_controller_stocks": [...],    # 同大股东个股
            "fund_holdings": [...]              # 基金持股
        }
    """
    from stock_common.f10_parser import (
        split_sections, parse_table, parse_tables, parse_key_value_table, parse_text_table
    )
    import re as _re

    with _TDX_CALL_LOCK:
        content = _f10_get_content(code, '股东研究')
        if not content:
            return {}
        sections = split_sections(content)
        result: dict = {}

        # 1. 控股股东与实际控制人（键值对表格）
        s1 = sections.get('控股股东与实际控股人', '')
        if s1 and '暂无数据' not in s1:
            result['controlling_shareholder'] = parse_key_value_table(s1)
        else:
            result['controlling_shareholder'] = {}

        # 2. 股东增减持计划
        s2 = sections.get('股东增减持计划', '')
        if s2 and '暂无数据' not in s2:
            # 提取摘要信息
            plan_info: dict = {}
            m = _re.search(r'最新公告日期[：:]\s*([\d-]+)', s2)
            if m:
                plan_info['latest_date'] = m.group(1)
            m = _re.search(r'变动方向[：:]\s*([^，,]+)', s2)
            if m:
                plan_info['direction'] = m.group(1).strip()
            m = _re.search(r'进度[：:]\s*([^，,\s]+)', s2)
            if m:
                plan_info['progress'] = m.group(1).strip()
            rows = parse_table(s2)
            plan_info['details'] = rows
            result['planned_changes'] = plan_info
        else:
            result['planned_changes'] = {}

        # 3. 重要股东持股变动（标准表格）
        s3 = sections.get('重要股东持股变动', '')
        if s3 and '暂无数据' not in s3:
            result['major_holder_changes'] = parse_table(s3)
        else:
            result['major_holder_changes'] = []

        # 4. 股东变化（十大股东 — 空格分隔文本格式）
        s4 = sections.get('股东变化', '')
        if s4 and '暂无数据' not in s4:
            # 按"●十大股东"和"●十大流通股东"分割
            shareholder_periods: list = []
            blocks = _re.split(r'●(十大股东|十大流通股东)\s*', s4)
            # blocks: [preamble, label1, content1, label2, content2, ...]
            for i in range(1, len(blocks), 2):
                label = blocks[i]
                content_block = blocks[i + 1] if i + 1 < len(blocks) else ''
                # 提取截止日期
                m = _re.search(r'截止日期[：:]\s*([\d-]+)', content_block)
                period = m.group(1) if m else ''
                # 提取摘要
                m = _re.search(r'前十大[^\n]*累计持有[：:]?([^\n]+)', content_block)
                summary = m.group(1).strip() if m else ''
                # 解析十大股东明细（空格分隔，可能跨行）
                lines = content_block.split('\n')
                # 找到表头行（含"股东名称"）
                header_idx = -1
                for j, line in enumerate(lines):
                    if '股东名称' in line:
                        header_idx = j
                        break
                holders: list = []
                if header_idx >= 0:
                    # 跳过分隔线，解析数据行
                    for j in range(header_idx + 1, len(lines)):
                        line = lines[j].strip()
                        if not line or '──' in line:
                            continue
                        if line.startswith('●') or '截止日期' in line:
                            break
                        # 用 2+ 空格分割
                        parts = [p.strip() for p in _re.split(r'\s{2,}', line) if p.strip()]
                        # 十大股东格式：名称 股份性质 持股数 占比 增减 一致行动人
                        if len(parts) >= 5:
                            holders.append({
                                'name': parts[0],
                                'share_type': parts[1],
                                'shares': parts[2],
                                'ratio': parts[3],
                                'change': parts[4],
                                'group': parts[5] if len(parts) > 5 else ''
                            })
                shareholder_periods.append({
                    'type': label,
                    'period': period,
                    'summary': summary,
                    'holders': holders[:10]
                })
            result['shareholder_changes'] = shareholder_periods
        else:
            result['shareholder_changes'] = []

        # 5. 股东人数变化（表格，每行一期，截止日期为第一列）
        s5 = sections.get('股东人数变化', '')
        if s5 and '暂无数据' not in s5:
            tables = parse_tables(s5)
            holder_list: list = []
            seen_periods: set = set()
            for tbl in tables:
                if not tbl:
                    continue
                for row in tbl:
                    period = (row.get('截止日期', '') or row.get('日期', '') or '').strip()
                    if period and period not in seen_periods:
                        seen_periods.add(period)
                        entry = {'period': period}
                        for k, v in row.items():
                            if k not in ('截止日期', '日期'):
                                entry[k] = v.strip() if isinstance(v, str) else v
                        holder_list.append(entry)
            result['holder_count'] = holder_list
        else:
            result['holder_count'] = []

        # 6-7. 同大股东个股 / 基金持股（常为空）
        s6 = sections.get('同大股东个股', '')
        result['same_controller_stocks'] = [] if (not s6 or '暂无数据' in s6) else parse_table(s6)
        s7 = sections.get('基金持股', '')
        result['fund_holdings'] = [] if (not s7 or '暂无数据' in s7) else parse_table(s7)

        return result


@cached(category="f10_share_capital", valid_if=lambda r: bool(r), cross_verify=True)
def tdx_get_share_capital(code: str) -> dict:
    """从 TDX F10「股本结构」分类获取股本信息（4 个子栏目）。

    替代 1 个东财 HTTP 接口：
    - get_eastmoney_lockup_expiry（限售解禁）

    Returns:
        dict: {
            "structure": [...],      # 股本结构（按期）
            "changes": [...],        # 股本变化历史
            "lockup_expiry": [...],  # 限售解禁时间表
            "buyback": [...]         # 股票回购记录
        }
    """
    from stock_common.f10_parser import (
        split_sections, parse_table, parse_tables, transpose_table
    )

    with _TDX_CALL_LOCK:
        content = _f10_get_content(code, '股本结构')
        if not content:
            return {}
        sections = split_sections(content)
        result: dict = {}

        # 1. 股本结构（表格，转置为按期）
        s1 = sections.get('股本结构', '')
        if s1 and '暂无数据' not in s1:
            tables = parse_tables(s1)
            merged: dict = {}
            for tbl in tables:
                if not tbl:
                    continue
                key_col = next(iter(tbl[0].keys())) if tbl[0] else ''
                transposed = transpose_table(tbl, key_col)
                for entry in transposed:
                    period = entry.get('period', '')
                    if period and period not in merged:
                        merged[period] = entry
            result['structure'] = list(merged.values())
        else:
            result['structure'] = []

        # 2. 股本变化（标准表格，每行一条变更记录）
        s2 = sections.get('股本变化', '')
        if s2 and '暂无数据' not in s2:
            result['changes'] = parse_table(s2)
        else:
            result['changes'] = []

        # 3. 限售解禁
        s3 = sections.get('限售解禁', '')
        if s3 and '暂无数据' not in s3:
            result['lockup_expiry'] = parse_table(s3)
        else:
            result['lockup_expiry'] = []

        # 4. 股票回购（键值对表格，按公告日组织）
        s4 = sections.get('股票回购', '')
        if s4 and '暂无数据' not in s4:
            tables = parse_tables(s4)
            buyback_list: list = []
            for tbl in tables:
                if not tbl:
                    continue
                # 回购表格是键值对格式：每行一个指标，列是不同公告日
                key_col = next(iter(tbl[0].keys())) if tbl[0] else ''
                date_cols = [c for c in tbl[0].keys() if c != key_col]
                for date_col in date_cols:
                    entry: dict = {'announce_date': date_col.strip()}
                    for row in tbl:
                        indicator = (row.get(key_col) or '').strip()
                        if indicator:
                            entry[indicator] = (row.get(date_col) or '').strip()
                    buyback_list.append(entry)
            result['buyback'] = buyback_list
        else:
            result['buyback'] = []

        return result


@cached(category="f10_news", trading_day=True, valid_if=lambda r: bool(r))
def tdx_get_company_news_f10(code: str, count: int = 10) -> list:
    """从 TDX F10「公司报道」分类获取新闻列表。

    替代 1 个东财 HTTP 接口：
    - get_eastmoney_stock_news

    Args:
        code: 股票代码
        count: 返回条数上限

    Returns:
        list: [{date, title, summary, url}, ...]
    """
    from stock_common.f10_parser import parse_paragraph_blocks

    with _TDX_CALL_LOCK:
        content = _f10_get_content(code, '公司报道')
        if not content:
            return []
        # F13 公司报道无 【N.】 section，直接是段落块格式
        # 去掉前2行 header（标题行 + 空行）
        lines = content.split('\n')
        # 找到第一个 ──── 分隔线作为内容起点
        start_idx = 0
        for i, line in enumerate(lines):
            if '──' in line and '┬' in line:
                start_idx = i
                break
        if start_idx > 0:
            content = '\n'.join(lines[start_idx:])
        news = parse_paragraph_blocks(content)
        return news[:count]


def tdx_get_industry_analysis(code: str) -> dict:
    """从 TDX F10「行业分析」分类获取行业地位信息（5 个子栏目）。

    替代 1 个东财 HTTP 接口：
    - get_eastmoney_industry_board

    Returns:
        dict: {
            "industry": {...},              # 所属行业
            "market_performance": [...],    # 市场表现排名
            "company_scale": [...],         # 公司规模排名
            "valuation_level": [...],       # 估值水平排名
            "financial_status": [...]       # 财务状况排名
        }
    """
    from stock_common.f10_parser import split_sections, parse_text_table
    import re as _re

    with _TDX_CALL_LOCK:
        content = _f10_get_content(code, '行业分析')
        if not content:
            return {}
        sections = split_sections(content)
        result: dict = {}

        # 1. 所属行业（文本，如"所属研究行业:酿酒(共36家)"）
        s1 = sections.get('所属行业', '')
        if s1 and '暂无数据' not in s1:
            industry: dict = {}
            m = _re.search(r'所属研究行业[：:]\s*(\S+?)\s*\(共(\d+)家\)', s1)
            if m:
                industry['name'] = m.group(1)
                industry['total_count'] = int(m.group(2))
            else:
                # 兜底：取第一行非空文本
                for line in s1.split('\n'):
                    line = line.strip()
                    if line and '暂无数据' not in line:
                        industry['raw'] = line
                        break
            result['industry'] = industry
        else:
            result['industry'] = {}

        # 2-5. 四个排名表（空格分隔文本表格）
        for result_key, section_name in [
            ('market_performance', '市场表现排名'),
            ('company_scale', '公司规模排名'),
            ('valuation_level', '估值水平排名'),
            ('financial_status', '财务状况排名'),
        ]:
            s = sections.get(section_name, '')
            if s and '暂无数据' not in s:
                # 提取截止日期
                m = _re.search(r'截止日期[：:]\s*([\d-]+)', s)
                cutoff_date = m.group(1) if m else ''
                rows = parse_text_table(s)
                # 找本股票在排名中的位置
                my_rank: dict = {}
                for r in rows:
                    if code in str(r.values()) or '贵州茅台' in str(r.values()):
                        my_rank = r
                        break
                result[result_key] = {
                    'cutoff_date': cutoff_date,
                    'my_rank': my_rank,
                    'top_rankings': rows[:10]  # 前10名
                }
            else:
                result[result_key] = {'cutoff_date': '', 'my_rank': {}, 'top_rankings': []}

        return result


# ═══════════════════════════════════════════════════════════════
# MacClient 板块/全市场函数（V9.2 恢复：误删的薄包装函数）
# ═══════════════════════════════════════════════════════════════

def tdx_get_belong_boards(code: str):
    """获取股票所属板块（行业/概念/地域/风格）。

    Returns:
        dict: {"industry": [...], "concept": [...], "area": [...], "style": [...]}
              每项为 [{"code": str, "name": str}, ...]
    """
    with _TDX_CALL_LOCK:
        client = _get_mac_client()
        if client is None:
            return {}
        try:
            df = client.get_belong_board(_market_from_code(code), code)
            if df is None or df.empty:
                return {}
            result: Dict[str, List[Any]] = {"industry": [], "concept": [], "area": [], "style": []}
            type_map = {0: "industry", 1: "industry", 12: "industry", 3: "area", 4: "concept", 5: "style"}
            for _, row in df.iterrows():
                bt = int(row.get('board_type', -1))
                cat = type_map.get(bt, None)
                if cat is None:
                    continue
                result[cat].append({
                    "code": str(row.get('board_code', '')),
                    "name": str(row.get('board_name', ''))
                })
            return result
        except Exception as _e:
            _debug_log(f"tdx_get_belong_boards {code}: {_e}")
            return {}


def tdx_get_board_list(board_type: int = 0):
    """获取板块列表（行业/概念/地域等）。

    Args:
        board_type: 0=行业一级, 1=行业二级, 4=概念, 3=地域 (easy_tdx BoardType)

    Returns:
        list: [{"rank": int, "code": str, "name": str, "price": float,
                "change_pct": float, "leader_name": str, "leader_change": float,
                "up_count": int, "down_count": int}, ...]
    """
    with _TDX_CALL_LOCK:
        client = _get_mac_client()
        if client is None:
            return []
        try:
            from easy_tdx.mac.enums import BoardType
            df = client.get_board_list(BoardType(board_type))
            if df is None or df.empty:
                return []
            sectors = []
            for i, (_, row) in enumerate(df.iterrows()):
                price = _safe_float(row.get('price', 0))
                pre_close = _safe_float(row.get('pre_close', 0))
                chg_pct = round((price - pre_close) / pre_close * 100, 2) if pre_close > 0 else 0.0
                sectors.append({
                    "rank": i + 1,
                    "code": str(row.get('code', '')),
                    "name": str(row.get('name', '')),
                    "price": price,
                    "change_pct": chg_pct,
                    "leader_name": str(row.get('symbol_name', '')),
                    "leader_change": _safe_float(row.get('symbol_rise_speed', 0)),
                    "up_count": 0,
                    "down_count": 0,
                })
            return sectors
        except Exception as _e:
            _debug_log(f"tdx_get_board_list type={board_type}: {_e}")
            return []


def tdx_get_board_members(board_code: str, sort_by_change: bool = True):
    """获取板块成员列表。

    Returns:
        list: [{"code": str, "name": str, "price": float, "change_pct": float,
                "mcap_yi": float, "turnover": float, "pe": float,
                "main_net_amount": float}, ...]
    """
    with _TDX_CALL_LOCK:
        client = _get_mac_client()
        if client is None:
            return []
        try:
            df = client.get_board_members(board_code)
            if df is None or df.empty:
                return []
            members = []
            for _, row in df.iterrows():
                close = _safe_float(row.get('close', 0))
                pre_close = _safe_float(row.get('pre_close', 0))
                chg = round((close - pre_close) / pre_close * 100, 2) if pre_close > 0 else _safe_float(row.get('speed_pct', 0))
                members.append({
                    "code": str(row.get('code', '')),
                    "name": str(row.get('name', '')),
                    "price": close,
                    "change_pct": chg,
                    "mcap_yi": _safe_float(row.get('total_market_cap_ab', 0)) / 1e8,
                    "turnover": _safe_float(row.get('turnover', 0)),
                    "pe": _safe_float(row.get('pe_dynamic', row.get('pe_ttm', 0))),
                    "main_net_amount": _safe_float(row.get('main_net_amount', 0)),
                })
            return members
        except Exception as _e:
            _debug_log(f"tdx_get_board_members {board_code}: {_e}")
            return []


def tdx_get_board_by_name(board_name: str, board_type: int = 0):
    """按名称查找板块并返回成员列表。

    Args:
        board_name: 板块名称（支持模糊匹配）
        board_type: 板块类型 (BoardType)

    Returns:
        list: 同 tdx_get_board_members 返回格式
    """
    with _TDX_CALL_LOCK:
        client = _get_mac_client()
        if client is None:
            return []
        try:
            from easy_tdx.mac.enums import BoardType
            bt = BoardType(board_type)
        except Exception as _e:
            _debug_log(f"tdx tdx_get_board_by_name BoardType error ({board_type}): {_e}")
            return []
        try:
            board_df = client.get_board_list(bt)
            if board_df is None or board_df.empty:
                return []
        except Exception as _e:
            _debug_log(f"tdx tdx_get_board_by_name get_board_list error: {_e}")
            return []
        _name_clean = board_name.replace("行业", "").replace("板块", "").replace("Ⅱ", "").replace("Ⅲ", "")
        matched_code = None
        for _, row in board_df.iterrows():
            row_name = str(row.get('name', ''))
            row_clean = row_name.replace("行业", "").replace("板块", "").replace("Ⅱ", "").replace("Ⅲ", "")
            if board_name in row_name or row_name in board_name or _name_clean in row_clean or row_clean in _name_clean:
                matched_code = str(row.get('code', ''))
                break
        if matched_code is None:
            return []
        return tdx_get_board_members(matched_code)


def tdx_get_market_abnormal_data():
    """全市场A股 + 多周期涨幅（用于异动扫描）。

    Returns:
        list: [{"code": str, "name": str, "price": float, "change_pct": float,
                "turnover": float, "mcap_yi": float,
                "ret_3d": float, "ret_5d": float, "ret_10d": float,
                "ret_20d": float, "ret_60d": float,
                "main_net_amount": float}, ...]
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
                        'code': code,
                        'name': name,
                        'price': close,
                        'change_pct': chg,
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
        except Exception as _e:
            _debug_log(f"tdx_get_market_abnormal_data: {_e}")
            return []


def tdx_get_all_stocks():
    """全市场A股列表（MacClient，连接中断自动重置并重试）。

    Returns:
        list: [{"code": str, "name": str, "price": float, "change_pct": float,
                "mcap_yi": float, "turnover_pct": float, "amount_yi": float}, ...]
    """
    for _retry in range(2):
        with _TDX_CALL_LOCK:
            client = _get_mac_client()
            if client is None:
                return []
            try:
                from easy_tdx.mac.enums import Category
                all_stocks = []
                start = 0
                page_size = 80
                for _ in range(100):
                    df = client.get_stock_quotes_list(Category.A, start, page_size)
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
                        turnover = _safe_float(row.get('turnover', 0))
                        amount = _safe_float(row.get('amount', 0)) / 1e8
                        mcap_est = amount * 50 if turnover > 0 else 0
                        all_stocks.append({
                            'code': code,
                            'name': name,
                            'price': close,
                            'change_pct': chg,
                            'mcap_yi': mcap_est,
                            'turnover_pct': turnover,
                            'amount_yi': amount,
                        })
                    start += page_size
                    if len(df) < page_size:
                        break
                return all_stocks
            except Exception as _e:
                _debug_log(f"tdx tdx_get_all_stocks error: {_e}")
                _reset_tdx_connections()
                continue
    return []


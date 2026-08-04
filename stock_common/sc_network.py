#!/usr/bin/env python3
"""sc_network.py — 网络层 / 限流 / Session 管理

从原 stock_common.py 提取的底层网络基础设施：
  - 日志配置 (http_errors / biz_errors)
  - HTTP 请求层 (requests + 重试 + 429 退避)
  - 按域名独立限流 + 进程间文件锁协调
  - asyncio / aiohttp 异步请求层
  - 东财统一 Session 管理 (Keep-Alive)

依赖关系：本模块是整个包的底层，不依赖其他子模块。
"""

from __future__ import annotations

import os
import sys
import time
import math
import re
import threading
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse
from tempfile import gettempdir as _gettempdir

import requests
import urllib3
from datetime import datetime, timedelta

try:
    from config import EM_MIN_INTERVAL, HTTP_TIMEOUT_SECONDS
    _USE_CONFIG = True
except ImportError:
    EM_MIN_INTERVAL = 1.0
    HTTP_TIMEOUT_SECONDS = 15
    _USE_CONFIG = False

try:
    from stock_common.sc_fault_tolerance import (
        get_random_ua, get_random_referer, exponential_backoff,
        get_domain_token_bucket, get_domain_circuit_breaker, CircuitBreakerError
    )
    _HAS_FAULT_TOLERANCE = True
except ImportError:
    _HAS_FAULT_TOLERANCE = False

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════════════════════
# 导出接口
# ═══════════════════════════════════════
__all__ = [
    # 日志
    '_LOG_DIR', '_http_logger', '_biz_logger', '_fallback_logger', '_DEBUG', '_debug_log',
    # 常量
    'UA', 'DATACENTER_URL', 'JP_URL',
    # Session
    'EM_SESSION', 'EM_MIN_INTERVAL', '_EM_LAST_CALL',
    # 限流
    '_DOMAIN_LIMITS', '_DOMAIN_LAST_TIME', '_DOMAIN_LAST_TIME_LOCK', '_RL_STATS',
    # 进程间锁
    '_em_lock_dir', '_em_lock_file', '_gen_lock_file',
    '_file_lock_acquire', '_file_lock_release',
    # 同步请求
    'em_get', '_em_wait_process_interval', '_gen_wait_process_interval',
    '_request_with_retry', '_quick_request', '_do_request',
    '_log_rate_limit', 'print_rate_limit_stats', '_market_code',
    # 异步请求
    '_em_async_lock', '_gen_async_lock', '_em_async_last_request',
    '_gen_async_last_request', '_HAS_ASYNCIO', '_HAS_AIOHTTP',
    '_ensure_async_locks', '_em_wait_process_interval_async',
    '_gen_wait_process_interval_async', 'create_async_session',
    'get_em_async_session',  # V12.2: 全局异步Session单例
    '_async_request_with_retry', '_async_quick_request',
    'requires_push2',
    'RateLimitBlockedError',
]

# ═══════════════════════════════════════
# 日志配置（V12.2 三级日志规范）
# ═══════════════════════════════════════
# 三级日志分类：
#   FATAL/BIZ_ERROR: 业务层面严重错误，影响核心功能（如数据获取完全失败）
#   NETWORK_ERROR:   网络/HTTP异常，可重试或降级
#   FALLBACK:        数据缺省/Fallback正常触发，不视为错误，仅记录统计
#
# 日志目录: stock_common/../logs = 项目根目录下的 logs
_LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

_http_logger = logging.getLogger("http_errors")
_http_handler = logging.FileHandler(os.path.join(_LOG_DIR, "http_errors.log"), encoding="utf-8")
_http_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
_http_logger.addHandler(_http_handler)
_http_logger.setLevel(logging.WARNING)

_biz_logger = logging.getLogger("biz_errors")
_biz_handler = logging.FileHandler(os.path.join(_LOG_DIR, "biz_errors.log"), encoding="utf-8")
_biz_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
_biz_logger.addHandler(_biz_handler)
_biz_logger.setLevel(logging.WARNING)

_fallback_logger = logging.getLogger("fallback")
_fallback_handler = logging.FileHandler(os.path.join(_LOG_DIR, "fallback.log"), encoding="utf-8")
_fallback_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
_fallback_logger.addHandler(_fallback_handler)
_fallback_logger.setLevel(logging.INFO)

# ═══════════════════════════════════════
# 调试开关（设为 True 可在 stderr 看到静默异常）
# ═══════════════════════════════════════
_DEBUG = os.environ.get("STOCK_DEBUG", "") == "1"

def _debug_log(msg: str) -> None:
    """仅在 _DEBUG 模式下输出到 stderr。"""
    if _DEBUG:
        print(f"[stock_common] {msg}", file=sys.stderr, flush=True)

# ═══════════════════════════════════════
# 常量
# ═══════════════════════════════════════
UA: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
DATACENTER_URL: str = "https://datacenter-web.eastmoney.com/api/data/v1/get"
JP_URL: str = "http://83.push2.eastmoney.com/api/qt/clist/get"

# ═══════════════════════════════════════
# 东财统一Session管理（SKILL.md V3.2 推荐）
# ═══════════════════════════════════════
# 所有东财接口共用同一个Session，实现Keep-Alive复用连接
# V9.3.1: 禁用系统代理，数据获取全部直连（代理仅用于GD上传）
EM_SESSION = requests.Session()
EM_SESSION.headers.update({"User-Agent": UA})
EM_SESSION.trust_env = False  # 不读取系统代理环境变量
_EM_LAST_CALL = [0.0]          # 模块级上次请求时间戳（列表实现可变）

# V16 增强: 通用 Session（非东财域名也复用 keep-alive，降低 TCP 握手开销）
_HTTP_SESSION = requests.Session()
_HTTP_SESSION.headers.update({"User-Agent": UA})
_HTTP_SESSION.trust_env = False


class RateLimitBlockedError(Exception):
    """V16: 东财连续 403，疑似 IP 被封。

    参考仓库 FAQ: 东财系共用一套风控，403 = IP 级临时封。
    处理三步: ① 停止请求等 30-60 分钟 / 换网络; ② 长批任务全走 em_get + 调大
    EM_MIN_INTERVAL; ③ 用备胎源（交易所官方/新浪/同花顺，不同风控面）。
    """


# 连续 403 计数（模块级，跨调用累积）
_CONSECUTIVE_403 = {"count": 0, "last_ts": 0.0}

# ═══════════════════════════════════════
# 全局异步 Session 单例（V12.2）
# ═══════════════════════════════════════
# 与同步 EM_SESSION 对应，提供全局共享的 aiohttp.ClientSession
# 避免每次异步请求都创建/销毁连接，提高全市场扫描性能
_EM_ASYNC_SESSION = None
_EM_ASYNC_SESSION_LOCK = threading.Lock()

# ═══════════════════════════════════════
# 按域名独立限流配置（基于诊断脚本实测）
# ═══════════════════════════════════════
# 注意: 增加 sleep_ms 防止被服务器限流/封禁
_DOMAIN_LIMITS: Dict[str, Dict[str, Any]] = {
    "qt.gtimg.cn": {"sleep_ms": 150, "semaphore": None, "rps": 5.0},
    "quotes.sina.cn": {"sleep_ms": 150, "semaphore": None, "rps": 5.0},
    "finance.pae.baidu.com": {"sleep_ms": 150, "semaphore": None, "rps": 5.0},
    "zx.10jqka.com.cn": {"sleep_ms": 150, "semaphore": None, "rps": 5.0},
    "datacenter-web.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "push2.eastmoney.com": {"sleep_ms": 1500, "semaphore": None, "rps": 0.6},
    # V16.0: push2ex（涨停/炸板/跌停池）与 push2 共用东财风控面，
    # 原缺省 100ms=10rps 无令牌桶 → 最高封禁风险点，补限流对齐 push2
    "push2ex.eastmoney.com": {"sleep_ms": 1500, "semaphore": None, "rps": 0.6},
    "reportapi.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "np-weblist.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    # V16.0.2: 补齐遗漏的东财域名限流（参考仓库"东财所有域名统一限流"原则）
    # 之前以下域名落入默认 100ms=10rps → 封禁隐患（尤其 emappdata 热榜高频）
    "83.push2.eastmoney.com": {"sleep_ms": 1500, "semaphore": None, "rps": 0.6},
    "push2his.eastmoney.com": {"sleep_ms": 1500, "semaphore": None, "rps": 0.6},
    "emappdata.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "datacenter.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "data.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "kuaixun.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "quote.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "vipmoney.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "www.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "mobappconfig.securities.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "search-api-web.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "dycalchis.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "np-anotice-stock.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "www.cninfo.com.cn": {"sleep_ms": 200, "semaphore": None, "rps": 3.0},
    "basic.10jqka.com.cn": {"sleep_ms": 150, "semaphore": None, "rps": 5.0},
    "www.cls.cn": {"sleep_ms": 200, "semaphore": None, "rps": 3.0},
    "irm.cninfo.com.cn": {"sleep_ms": 200, "semaphore": None, "rps": 3.0},
    "www.szse.cn": {"sleep_ms": 200, "semaphore": None, "rps": 3.0},
    "query.sse.com.cn": {"sleep_ms": 200, "semaphore": None, "rps": 3.0},
    "vip.stock.finance.sina.com.cn": {"sleep_ms": 150, "semaphore": None, "rps": 5.0},
    "data.10jqka.com.cn": {"sleep_ms": 150, "semaphore": None, "rps": 5.0},
}
# 每个域名独立的最后请求时间
_DOMAIN_LAST_TIME: Dict[str, float] = {}
# 限流字典的线程锁（方案1：线程安全修复）
_DOMAIN_LAST_TIME_LOCK = threading.Lock()
# 限流统计计数器（方案5：限流监控统计）
_RL_STATS = {
    "em_request_count": 0,
    "em_rate_limit_count": 0,
    "em_429_count": 0,
    "em_403_count": 0,
    "start_time": time.time(),
}

# ═══════════════════════════════════════
# 全局状态（进程内限流 + 进程间协调，V7.5 防封版）
# ═══════════════════════════════════════
# V9.3.3: 废弃 _em_last_request_time / _gen_last_request_time
# 改用 _DOMAIN_LAST_TIME + _DOMAIN_LAST_TIME_LOCK（线程安全）

# ── 进程间协调: 通过文件 mtime 实现跨进程请求间隔 ──
_em_lock_dir = os.path.join(_gettempdir(), "a_stock_data_v7")
try:
    os.makedirs(_em_lock_dir, exist_ok=True)
except Exception as _e:
    _debug_log(f"sc_network makedirs lock_dir: {_e}")
_em_lock_file = os.path.join(_em_lock_dir, "em_rate_limit")
_gen_lock_file = os.path.join(_em_lock_dir, "gen_rate_limit")


def _file_lock_acquire(lock_path: str, timeout: float = 10.0) -> bool:
    """跨进程互斥：尝试创建唯一文件做锁。成功返回 True，超时返回 False。"""
    _deadline = time.time() + timeout
    _pid_str = str(os.getpid())
    _unique_path = lock_path + "_" + _pid_str
    while time.time() < _deadline:
        try:
            _fd = os.open(_unique_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.close(_fd)
            return True
        except FileExistsError:
            # 已被其他进程持有，短暂让出
            time.sleep(0.05)
        except Exception as _e:
            _debug_log(f"file_lock_acquire error ({lock_path}): {_e}")
            return False
    return False


def _file_lock_release(lock_path: str) -> None:
    """释放跨进程锁：删除自己创建的文件。"""
    _unique_path = lock_path + "_" + str(os.getpid())
    try:
        if os.path.exists(_unique_path):
            os.remove(_unique_path)
    except Exception as _e:
        _debug_log(f"sc_network file_lock_release: {_e}")


def em_get(url: str, params: dict | None = None, headers: dict | None = None,
           timeout: int = 15, **kwargs):
    """东财统一请求入口（SKILL.md V3.2 推荐）：自动节流 + 复用session + 默认UA。

    V12.1: 集成容错层 - 令牌桶限流 + 熔断器 + 随机UA

    所有 eastmoney.com 接口都应通过它请求，避免高频被封IP。

    Args:
        url: 请求URL
        params: 请求参数
        headers: 请求头（会与Session默认头合并）
        timeout: 超时时间
        **kwargs: 其他requests参数

    Returns:
        requests.Response 对象
    """
    import random as _rand
    from urllib.parse import urlparse
    from stock_common.sc_fault_tolerance import (
        get_domain_token_bucket, get_domain_circuit_breaker, 
        get_random_ua, CircuitBreakerError
    )

    _domain = urlparse(url).netloc

    # V12.1: 熔断器保护 - 如果该域名熔断器处于 Open 状态，直接拒绝
    try:
        _circuit_breaker = get_domain_circuit_breaker(_domain)
        if _circuit_breaker.state == "open":
            _debug_log(f"em_get: domain {_domain} circuit breaker is open, request rejected")
            raise CircuitBreakerError(f"Domain {_domain} is circuit-broken")
    except Exception as _e:
        _debug_log(f"em_get: circuit breaker check failed: {_e}")

    # V12.1: 令牌桶限流 - 替代原有简单 sleep
    # V16.0: rps 从 _DOMAIN_LIMITS 读取（push2=0.6, push2ex=0.6, datacenter=1.0），
    # 不再硬编码 1.0；EM_MIN_INTERVAL 作为硬性全局下限（两者取严），使"调大 EM_MIN_INTERVAL"真正生效
    try:
        _cfg_rps = _DOMAIN_LIMITS.get(_domain, {}).get("rps", 1.0)
        _bucket = get_domain_token_bucket(_domain, rps=_cfg_rps)
        _bucket.acquire(1)
        # V16.0: EM_MIN_INTERVAL 作为硬性下限（参考仓库: 每请求强制 ≥EM_MIN_INTERVAL，无突发）
        _min_interval = max(float(EM_MIN_INTERVAL), 1.0 / max(_cfg_rps, 1e-6))
        _elapsed = time.time() - _EM_LAST_CALL[0]
        if _elapsed < _min_interval:
            time.sleep(_min_interval - _elapsed)
    except Exception as _e:
        _debug_log(f"em_get: token bucket acquire failed: {_e}")
        # Fallback: 使用原有 sleep 逻辑
        wait = EM_MIN_INTERVAL - (time.time() - _EM_LAST_CALL[0])
        if wait > 0:
            time.sleep(wait + _rand.uniform(0.10, 0.50))

    # V16.0: 接通同步进程间文件锁（_em_wait_process_interval 原本定义但无调用方），
    # 使 --concurrency 3 时跨进程仍 ≤1 rps
    try:
        _em_wait_process_interval()
    except Exception as _e:
        _debug_log(f"em_get: process interval: {_e}")

    # V12.1: 同步更新 per-domain 限流器状态
    with _DOMAIN_LAST_TIME_LOCK:
        _DOMAIN_LAST_TIME[_domain] = time.time()

    try:
        # 合并headers：Session默认头 + 用户传入头 + V12.1 随机UA
        session_headers = EM_SESSION.headers.copy()
        if headers:
            session_headers.update(headers)
        # V12.1: 随机UA增加反爬能力
        if "User-Agent" not in session_headers:
            session_headers["User-Agent"] = get_random_ua()

        _response = EM_SESSION.get(url, params=params, headers=session_headers,
                                   timeout=timeout, **kwargs)

        # V16.0: 统一 403 处理（对齐 _do_request）— 403 = 东财风控明确信号
        if _response.status_code == 403:
            _RL_STATS["em_403_count"] += 1
            try:
                _biz_logger.warning(f"EM 403 rate-limited: {_domain} {url[:120]}")
            except Exception:
                pass
            _CONSECUTIVE_403["count"] += 1
            _CONSECUTIVE_403["last_ts"] = time.time()
            if _CONSECUTIVE_403["count"] >= 3:
                raise RateLimitBlockedError(
                    f"EM 连续 {_CONSECUTIVE_403['count']} 次 403，疑似 IP 被封。"
                    f"建议: 停止 30-60 分钟 / 换网络 / 调大 EM_MIN_INTERVAL / 切换备胎源"
                )
            try:
                get_domain_circuit_breaker(_domain)._on_failure()
            except Exception:
                pass
            time.sleep(exponential_backoff(0, base=2.0, max_wait=60.0))

        # V12.1: 成功则重置熔断器
        try:
            _circuit_breaker = get_domain_circuit_breaker(_domain)
            _circuit_breaker._on_success()
        except Exception:
            pass

        return _response
    except Exception as _e:
        # V12.1: 失败则记录到熔断器
        try:
            _circuit_breaker = get_domain_circuit_breaker(_domain)
            _circuit_breaker._on_failure()
        except Exception:
            pass
        raise
    finally:
        _EM_LAST_CALL[0] = time.time()
        with _DOMAIN_LAST_TIME_LOCK:
            _DOMAIN_LAST_TIME[_domain] = time.time()
        _RL_STATS["em_request_count"] += 1


def _em_wait_process_interval() -> float:
    """进程间协调：检查距上次东财请求的间隔，不够则 sleep。

    返回实际等待的秒数（0 表示无需等待）。
    """
    import random as _rand
    _target_interval = 1.0 + _rand.uniform(0.10, 0.30)
    try:
        if os.path.exists(_em_lock_file):
            _elapsed = time.time() - os.path.getmtime(_em_lock_file)
            if _elapsed < _target_interval:
                _wait = _target_interval - _elapsed
                time.sleep(_wait)
                # touch 文件标记本次请求
                with open(_em_lock_file, "w") as _f:
                    _f.write(str(time.time()))
                return _wait
        # 无论是否等待，都 touch 文件标记本次请求
        with open(_em_lock_file, "w") as _f:
            _f.write(str(time.time()))
    except Exception as _e:
        _debug_log(f"sc_network em_wait_process_interval: {_e}")
    return 0.0


def _gen_wait_process_interval() -> float:
    """进程间协调：检查距上次通用请求的间隔（0.2s 礼貌限速）。"""
    import random as _rand
    _target_interval = 0.2 + _rand.uniform(0.01, 0.05)
    try:
        if os.path.exists(_gen_lock_file):
            _elapsed = time.time() - os.path.getmtime(_gen_lock_file)
            if _elapsed < _target_interval:
                _wait = _target_interval - _elapsed
                time.sleep(_wait)
                with open(_gen_lock_file, "w") as _f:
                    _f.write(str(time.time()))
                return _wait
        with open(_gen_lock_file, "w") as _f:
            _f.write(str(time.time()))
    except Exception as _e:
        _debug_log(f"sc_network em_wait_process_interval: {_e}")
    return 0.0


def _request_with_retry(url: str, params: Optional[Dict[str, Any]] = None,
                        headers: Optional[Dict[str, str]] = None, timeout: int = 15,
                        max_retries: int = 3, data: Optional[Dict[str, Any]] = None,
                        method: str = "GET", verify: bool = False) -> Optional[requests.Response]:
    """带并发限流的 HTTP 请求（按域名独立限流）。

    V7.5 优化版：按域名独立控制并发和 sleep，不再使用全局 Semaphore。
    V8.5 新增：添加随机抖动防止被限流。
    V9.0 新增：线程锁保护 + 限流统计。
    V11.5 新增：令牌桶限流 + 熔断器模式 + 随机UA/Referer
    """
    import random as _rand

    parsed = urlparse(url)
    domain = parsed.netloc
    is_em = "eastmoney.com" in domain

    if _HAS_FAULT_TOLERANCE:
        try:
            cb = get_domain_circuit_breaker(domain)
            if cb.state == "open":
                _debug_log(f"Circuit breaker open for {domain}, skipping request")
                return None

            rps = _DOMAIN_LIMITS.get(domain, {"sleep_ms": 100}).get("rps", 1.0)
            tb = get_domain_token_bucket(domain, rps=rps)
            tb.acquire()
        except Exception as _e:
            _debug_log(f"Fault tolerance init error ({domain}): {_e}")

    limit = _DOMAIN_LIMITS.get(domain, {"sleep_ms": 100})
    sleep_ms = limit["sleep_ms"]

    wait_ms = 0.0
    with _DOMAIN_LAST_TIME_LOCK:
        last_time = _DOMAIN_LAST_TIME.get(domain, 0.0)
        now = time.time()
        elapsed_ms = (now - last_time) * 1000
        jitter_ms = _rand.uniform(10, 30)
        total_sleep_ms = sleep_ms + jitter_ms
        if total_sleep_ms > 0 and last_time > 0 and elapsed_ms < total_sleep_ms:
            wait_ms = total_sleep_ms - elapsed_ms
        _DOMAIN_LAST_TIME[domain] = now + wait_ms / 1000.0
    if wait_ms > 0:
        time.sleep(wait_ms / 1000.0)
        if is_em:
            _RL_STATS["em_rate_limit_count"] += 1
            _log_rate_limit(domain, wait_ms)
    if is_em:
        _RL_STATS["em_request_count"] += 1

    return _do_request(url, params, headers, timeout, max_retries, data, method, verify)


def _quick_request(url: str, params: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None, timeout: int = 15,
                   max_retries: int = 3, data: Optional[Dict[str, Any]] = None,
                   method: str = "GET", verify: bool = False) -> Optional[requests.Response]:
    """通用 HTTP 请求（按域名独立限流）。

    V7.5 优化版：按域名独立控制并发和 sleep，不再使用全局 Semaphore。
    V8.5 新增：添加随机抖动防止被限流。
    V9.0 新增：线程锁保护 + 限流统计。
    """
    import random as _rand

    # 解析域名
    parsed = urlparse(url)
    domain = parsed.netloc

    # 获取该域名的限流配置（默认 sleep=100ms 作为兜底）
    limit = _DOMAIN_LIMITS.get(domain, {"sleep_ms": 100})
    sleep_ms = limit["sleep_ms"]

    # 按域名独立 sleep，添加 10-30ms 随机抖动
    is_em = "eastmoney.com" in domain
    wait_ms = 0.0
    with _DOMAIN_LAST_TIME_LOCK:
        last_time = _DOMAIN_LAST_TIME.get(domain, 0.0)
        now = time.time()
        elapsed_ms = (now - last_time) * 1000
        jitter_ms = _rand.uniform(10, 30)
        total_sleep_ms = sleep_ms + jitter_ms
        if total_sleep_ms > 0 and last_time > 0 and elapsed_ms < total_sleep_ms:
            wait_ms = total_sleep_ms - elapsed_ms
        _DOMAIN_LAST_TIME[domain] = now + wait_ms / 1000.0
    if wait_ms > 0:
        time.sleep(wait_ms / 1000.0)
        if is_em:
            _RL_STATS["em_rate_limit_count"] += 1
            _log_rate_limit(domain, wait_ms)
    if is_em:
        _RL_STATS["em_request_count"] += 1

    return _do_request(url, params, headers, timeout, max_retries, data, method, verify)


def _do_request(url: str, params: Optional[Dict[str, Any]],
                headers: Optional[Dict[str, str]], timeout: int, max_retries: int,
                data: Optional[Dict[str, Any]], method: str, verify: bool) -> Optional[requests.Response]:
    """内部：执行 HTTP 请求 + 重试（由 _request_with_retry / _quick_request 调用）。

    V9.0 新增：429状态码检测 + 指数退避重试。
    V9.3.2 新增：禁用系统代理（数据获取全部直连）+ 捕获 ProxyError 和兜底 Exception。
    V11.5 新增：随机UA/Referer + 指数退避 + 熔断器模式
    """
    is_em = "eastmoney.com" in urlparse(url).netloc
    domain = urlparse(url).netloc
    # V9.3.2: 数据获取全部直连，不使用系统代理（代理仅用于GD上传）
    _no_proxy = {"http": None, "https": None}

    for attempt in range(max_retries):
        try:
            _req_headers = headers.copy() if headers else {}
            if not _req_headers.get("User-Agent"):
                if _HAS_FAULT_TOLERANCE:
                    _req_headers["User-Agent"] = get_random_ua()
                else:
                    _req_headers["User-Agent"] = UA
            if is_em and not _req_headers.get("Referer"):
                if _HAS_FAULT_TOLERANCE:
                    _req_headers["Referer"] = get_random_referer()

            if method == "POST":
                r = _HTTP_SESSION.post(url, data=data, params=params,
                                       headers=_req_headers,
                                       timeout=timeout, verify=verify, proxies=_no_proxy)
            elif method == "GET":
                r = _HTTP_SESSION.get(url, params=params,
                                      headers=_req_headers,
                                      timeout=timeout, verify=verify, proxies=_no_proxy)
            else:
                return None

            if r.status_code == 403:
                # V16 增强: 403 = 东财风控明确信号（参考仓库 FAQ: IP 级临时封）
                # 长指数退避 + 熔断器 Open + 连续计数，避免继续试探加重封禁
                if is_em:
                    _RL_STATS["em_403_count"] += 1
                    try:
                        _biz_logger.warning(f"EM 403 rate-limited: {domain} {url[:120]}")
                    except Exception:
                        pass
                # 连续 403 计数: 达 3 次视为 IP 被封，抛 RateLimitBlockedError
                _CONSECUTIVE_403["count"] += 1
                _CONSECUTIVE_403["last_ts"] = time.time()
                if _CONSECUTIVE_403["count"] >= 3:
                    raise RateLimitBlockedError(
                        f"EM 连续 {_CONSECUTIVE_403['count']} 次 403，疑似 IP 被封。"
                        f"建议: 停止 30-60 分钟 / 换网络 / 调大 EM_MIN_INTERVAL / 切换备胎源"
                    )
                if _HAS_FAULT_TOLERANCE:
                    try:
                        get_domain_circuit_breaker(domain)._on_failure()
                    except Exception:
                        pass
                if attempt < max_retries - 1:
                    wait_s = exponential_backoff(attempt, base=2.0, max_wait=60.0)
                    time.sleep(wait_s)
                    continue
                return None
            if r.status_code == 429:
                if is_em:
                    _RL_STATS["em_429_count"] += 1
                if attempt < max_retries - 1:
                    retry_after = r.headers.get("Retry-After")
                    if retry_after:
                        # V16.0: Retry-After 可能非数字，加 try/except 防 ValueError 吞掉重试
                        try:
                            wait_s = float(retry_after)
                        except (ValueError, TypeError):
                            if _HAS_FAULT_TOLERANCE:
                                wait_s = exponential_backoff(attempt)
                            else:
                                wait_s = 1.0 * (2 ** attempt)
                    else:
                        if _HAS_FAULT_TOLERANCE:
                            wait_s = exponential_backoff(attempt)
                        else:
                            wait_s = 1.0 * (2 ** attempt)
                    time.sleep(wait_s)
                    continue
                return None
            # V16: 成功响应（<400）重置连续 403 计数
            if _CONSECUTIVE_403["count"] > 0 and r.status_code < 400:
                _CONSECUTIVE_403["count"] = 0
            return r
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ProxyError):
            if attempt < max_retries - 1:
                if _HAS_FAULT_TOLERANCE:
                    # V16 增强: HTTP 000 连接被拒 = 间歇风控，长退避等待恢复
                    wait_s = exponential_backoff(attempt, base=1.0, max_wait=60.0)
                else:
                    wait_s = 1.0 * (2 ** attempt)
                time.sleep(wait_s)
                continue
            return None
        except Exception as _e:
            _debug_log(f"sc_network _do_request unexpected error ({url}): {_e}")
            return None
    return None


def _log_rate_limit(domain: str, wait_ms: float) -> None:
    """记录限流等待日志到 rate_limit.log（方案5：限流监控统计）。"""
    try:
        log_path = os.path.join(_LOG_DIR, "rate_limit.log")
        now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        line = f"{now_str} | {domain} | 等待 {wait_ms:.0f}ms | 总请求={_RL_STATS['em_request_count']} | 限流等待={_RL_STATS['em_rate_limit_count']}次 | 429={_RL_STATS['em_429_count']}次 | 403={_RL_STATS['em_403_count']}次\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as _e:
        _debug_log(f"sc_network log_rate_limit: {_e}")


def print_rate_limit_stats() -> None:
    """打印东财限流统计信息（方案5：限流监控统计）。"""
    total_s = time.time() - _RL_STATS["start_time"]
    total_req = _RL_STATS["em_request_count"]
    rl_count = _RL_STATS["em_rate_limit_count"]
    qps = total_req / total_s if total_s > 0 else 0
    rl_pct = (rl_count / total_req * 100) if total_req > 0 else 0
    print("=" * 50)
    print("  东财限流统计")
    print("=" * 50)
    print(f"  总请求数: {total_req}")
    print(f"  限流等待: {rl_count}次 ({rl_pct:.1f}%)")
    print(f"  429错误: {_RL_STATS['em_429_count']}次")
    print(f"  403错误: {_RL_STATS['em_403_count']}次")
    print(f"  平均QPS: {qps:.2f}")
    print(f"  运行时长: {total_s:.0f}秒")
    print("=" * 50)


def requires_push2(fn):
    """V16 审计装饰器: 标记使用 push2 端点的函数。

    push2 是东财风控最严的域名（参考仓库 FAQ），每次调用打 WARNING 日志，
    便于审计 push2 使用频率、督促优先走 ZHB/mootdx/腾讯。
    用法:
        @requires_push2
        def get_x(...): ...
    """
    import functools

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            _biz_logger.warning(f"PUSH2 used: {fn.__module__}.{fn.__name__}")
        except Exception:
            pass
        _RL_STATS.setdefault("push2_call_count", _RL_STATS.get("push2_call_count", 0) + 1)
        return fn(*args, **kwargs)

    return wrapper


def _market_code(code: str) -> int:
    """6位代码 → TDX 市场代码 (0=深圳, 1=上海)"""
    return 1 if code.startswith("6") else 0


# ══════════════════════════════════════════════════════════════════════════════
# V7.5: asyncio 异步请求层 (aiohttp + asyncio.Semaphore)
# 功能: 在异步模式下替代 threading.Lock + requests，实现 2-3x 性能提升
# ══════════════════════════════════════════════════════════════════════════════

_em_async_lock = None      # asyncio.Semaphore(3) — 测试 45 请求 0 次 429，安全
_gen_async_lock = None
_em_async_last_request: float = 0.0  # async 版东财时间戳
_gen_async_last_request: float = 0.0  # async 版通用时间戳

try:
    import asyncio
    _HAS_ASYNCIO = True
except ImportError:
    _HAS_ASYNCIO = False

try:
    import aiohttp
    _HAS_AIOHTTP = True
except ImportError:
    _HAS_AIOHTTP = False


def _ensure_async_locks():
    """懒加载: 创建 asyncio.Semaphore（统一 Semaphore(3)）。"""
    global _em_async_lock, _gen_async_lock
    if _em_async_lock is None and _HAS_ASYNCIO:
        _em_async_lock = asyncio.Semaphore(3)   # 东财: 最多 3 并发请求
    if _gen_async_lock is None and _HAS_ASYNCIO:
        _gen_async_lock = asyncio.Semaphore(3)  # 通用: 与东财保持一致


async def _em_wait_process_interval_async() -> float:
    """async 版进程间协调：与同步版共用同一文件。"""
    import random as _rand
    _target_interval = 1.0 + _rand.uniform(0.10, 0.30)
    try:
        if os.path.exists(_em_lock_file):
            _elapsed = time.time() - os.path.getmtime(_em_lock_file)
            if _elapsed < _target_interval:
                _wait = _target_interval - _elapsed
                await asyncio.sleep(_wait)
                with open(_em_lock_file, "w") as _f:
                    _f.write(str(time.time()))
                return _wait
        with open(_em_lock_file, "w") as _f:
            _f.write(str(time.time()))
    except Exception as _e:
        _debug_log(f"sc_network em_wait_process_interval: {_e}")
    return 0.0


async def _gen_wait_process_interval_async() -> float:
    """async 版通用进程间协调：与同步版共用同一文件。"""
    import random as _rand
    _target_interval = 0.2 + _rand.uniform(0.01, 0.05)
    try:
        if os.path.exists(_gen_lock_file):
            _elapsed = time.time() - os.path.getmtime(_gen_lock_file)
            if _elapsed < _target_interval:
                _wait = _target_interval - _elapsed
                await asyncio.sleep(_wait)
                with open(_gen_lock_file, "w") as _f:
                    _f.write(str(time.time()))
                return _wait
        with open(_gen_lock_file, "w") as _f:
            _f.write(str(time.time()))
    except Exception as _e:
        _debug_log(f"sc_network gen_wait_process_interval_async: {_e}")
    return 0.0


async def create_async_session():
    """创建一个 aiohttp ClientSession（调用方负责关闭）。

    V9.3.2: 禁用系统代理，数据获取全部直连。
    """
    if not _HAS_AIOHTTP:
        raise RuntimeError("aiohttp 未安装，请先运行: pip install aiohttp")
    # V9.3.2: trust_env=False → 不读取系统代理环境变量，数据获取全部直连
    return aiohttp.ClientSession(headers={"User-Agent": UA}, trust_env=False)


async def get_em_async_session():
    """获取全局异步 Session 单例（V12.2）。

    与同步 EM_SESSION 对应，提供全局共享的 aiohttp.ClientSession，
    在单个脚本执行期间贯穿复用同一个 TCP 连接池。

    返回: aiohttp.ClientSession 对象
    """
    global _EM_ASYNC_SESSION
    if _EM_ASYNC_SESSION is not None:
        return _EM_ASYNC_SESSION
    with _EM_ASYNC_SESSION_LOCK:
        if _EM_ASYNC_SESSION is not None:
            return _EM_ASYNC_SESSION
        if not _HAS_AIOHTTP:
            raise RuntimeError("aiohttp 未安装，请先运行: pip install aiohttp")
        _EM_ASYNC_SESSION = aiohttp.ClientSession(headers={"User-Agent": UA}, trust_env=False)
        _debug_log("Created global async session")
        return _EM_ASYNC_SESSION


async def _async_request_with_retry(session, url: str, params=None,
                                    headers=None, timeout: int = 15,
                                    max_retries: int = 3, method: str = "GET"):
    """异步版: 带并发限流的东财请求（Semaphore(3) + 统一间隔保护）。

    修复V7.5.1: 在async with块内读取完JSON再返回，避免response对象在块外失效。
    V11.5 新增: 熔断器模式 + 随机UA/Referer + 指数退避
    返回: parsed JSON dict 或 None（失败时）
    """
    if not _HAS_ASYNCIO or not _HAS_AIOHTTP:
        return None

    domain = urlparse(url).netloc

    if _HAS_FAULT_TOLERANCE:
        try:
            cb = get_domain_circuit_breaker(domain)
            if cb.state == "open":
                _debug_log(f"Circuit breaker open for {domain}, skipping request")
                return None
        except Exception as _e:
            _debug_log(f"Async fault tolerance init error ({domain}): {_e}")

    _ensure_async_locks()
    global _em_async_last_request
    import random as _rand

    async with _em_async_lock:
        now = time.time()
        elapsed = now - _em_async_last_request
        interval = 1.0 + _rand.uniform(0.10, 0.30)
        if _em_async_last_request > 0 and elapsed < interval:
            await asyncio.sleep(interval - elapsed)
        _em_async_last_request = time.time()

        await _em_wait_process_interval_async()

        _req_headers = headers.copy() if headers else {}
        if not _req_headers.get("User-Agent"):
            if _HAS_FAULT_TOLERANCE:
                _req_headers["User-Agent"] = get_random_ua()
            else:
                _req_headers["User-Agent"] = UA
        if "eastmoney.com" in domain and not _req_headers.get("Referer"):
            if _HAS_FAULT_TOLERANCE:
                _req_headers["Referer"] = get_random_referer()

        for attempt in range(max_retries):
            try:
                timeout_obj = aiohttp.ClientTimeout(total=timeout)
                async with session.get(url, params=params, headers=_req_headers,
                                       timeout=timeout_obj) as response:
                    if response.status == 200:
                        return await response.json(content_type=None)
                    if response.status == 429:
                        if attempt < max_retries - 1:
                            if _HAS_FAULT_TOLERANCE:
                                wait_s = exponential_backoff(attempt)
                            else:
                                wait_s = 1.0 * (2 ** attempt)
                            await asyncio.sleep(wait_s)
                            continue
                        return None
                    await asyncio.sleep(1.0 * (attempt + 1))
            except (aiohttp.ClientError, asyncio.TimeoutError):
                if attempt < max_retries - 1:
                    if _HAS_FAULT_TOLERANCE:
                        wait_s = exponential_backoff(attempt)
                    else:
                        wait_s = 2.0 * (attempt + 1)
                    await asyncio.sleep(wait_s)
                    continue
                return None
            except Exception as _e:
                _debug_log(f"async_request_with_retry unexpected error ({url}): {_e}")
                return None
        return None


async def _async_quick_request(session, url: str, params=None,
                               headers=None, timeout: int = 15,
                               max_retries: int = 3,
                               data=None, method: str = "GET",
                               is_json: bool = True, encoding=None):
    """异步版: 通用 HTTP 请求（腾讯/新浪/同花顺/巨潮等，Semaphore(5) + 统一间隔保护）。

    V7.5.1修复: 在 async with 块内读取完数据再返回，避免 response 连接释放后读取失败。
    V11.5 新增: 熔断器模式 + 随机UA/Referer + 指数退避

    Args:
        is_json:  True (默认) → 解析为 JSON，返回 dict/list。False → 返回原始文本 str
        encoding: 文本模式下的解码方式（如 'gbk'），None 表示用 aiohttp 自动检测
    Returns:
        dict/list (is_json=True), str (is_json=False), 或 None（失败时）
    """
    if not _HAS_ASYNCIO or not _HAS_AIOHTTP:
        return None

    domain = urlparse(url).netloc

    if _HAS_FAULT_TOLERANCE:
        try:
            cb = get_domain_circuit_breaker(domain)
            if cb.state == "open":
                _debug_log(f"Circuit breaker open for {domain}, skipping request")
                return None
        except Exception as _e:
            _debug_log(f"Async quick fault tolerance init error ({domain}): {_e}")

    _ensure_async_locks()
    global _gen_async_last_request
    import random as _rand
    import json as _json

    async with _gen_async_lock:
        now = time.time()
        elapsed = now - _gen_async_last_request
        interval = 0.2 + _rand.uniform(0.01, 0.05)
        if _gen_async_last_request > 0 and elapsed < interval:
            await asyncio.sleep(interval - elapsed)
        _gen_async_last_request = time.time()

        await _gen_wait_process_interval_async()

        _req_headers = headers.copy() if headers else {}
        if not _req_headers.get("User-Agent"):
            if _HAS_FAULT_TOLERANCE:
                _req_headers["User-Agent"] = get_random_ua()
            else:
                _req_headers["User-Agent"] = UA

        for attempt in range(max_retries):
            try:
                timeout_obj = aiohttp.ClientTimeout(total=timeout)
                if method == "POST":
                    async with session.post(url, data=data, params=params,
                                            headers=_req_headers,
                                            timeout=timeout_obj) as response:
                        if response.status == 200:
                            if is_json:
                                return await response.json(content_type=None)
                            return await response.text(encoding=encoding)
                        if response.status == 429 and attempt < max_retries - 1:
                            if _HAS_FAULT_TOLERANCE:
                                wait_s = exponential_backoff(attempt)
                            else:
                                wait_s = 1.0 * (2 ** attempt)
                            await asyncio.sleep(wait_s)
                            continue
                else:
                    async with session.get(url, params=params, headers=_req_headers,
                                           timeout=timeout_obj) as response:
                        if response.status == 200:
                            if is_json:
                                return await response.json(content_type=None)
                            return await response.text(encoding=encoding)
                        if response.status == 429 and attempt < max_retries - 1:
                            if _HAS_FAULT_TOLERANCE:
                                wait_s = exponential_backoff(attempt)
                            else:
                                wait_s = 1.0 * (2 ** attempt)
                            await asyncio.sleep(wait_s)
                            continue
                await asyncio.sleep(0.5 * (attempt + 1))
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError, _json.JSONDecodeError):
                if attempt < max_retries - 1:
                    if _HAS_FAULT_TOLERANCE:
                        wait_s = exponential_backoff(attempt)
                    else:
                        wait_s = 1.0 * (attempt + 1)
                    await asyncio.sleep(wait_s)
                    continue
                return None
        return None

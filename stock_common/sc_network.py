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

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════════════════════
# 导出接口
# ═══════════════════════════════════════
__all__ = [
    # 日志
    '_LOG_DIR', '_http_logger', '_biz_logger', '_DEBUG', '_debug_log',
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
    '_async_request_with_retry', '_async_quick_request',
]

# ═══════════════════════════════════════
# 日志配置
# ═══════════════════════════════════════
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
EM_MIN_INTERVAL = 1.0          # 东财请求最小间隔(秒)
_EM_LAST_CALL = [0.0]          # 模块级上次请求时间戳（列表实现可变）

# ═══════════════════════════════════════
# 按域名独立限流配置（基于诊断脚本实测）
# ═══════════════════════════════════════
# 注意: 增加 sleep_ms 防止被服务器限流/封禁
_DOMAIN_LIMITS: Dict[str, Dict[str, Any]] = {
    "qt.gtimg.cn": {"sleep_ms": 150, "semaphore": None},
    "quotes.sina.cn": {"sleep_ms": 150, "semaphore": None},
    "finance.pae.baidu.com": {"sleep_ms": 150, "semaphore": None},
    "zx.10jqka.com.cn": {"sleep_ms": 150, "semaphore": None},
    "datacenter-web.eastmoney.com": {"sleep_ms": 1000, "semaphore": None},
    "push2.eastmoney.com": {"sleep_ms": 1000, "semaphore": None},
    "reportapi.eastmoney.com": {"sleep_ms": 1000, "semaphore": None},
    "www.cninfo.com.cn": {"sleep_ms": 200, "semaphore": None},
    "basic.10jqka.com.cn": {"sleep_ms": 150, "semaphore": None},
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

    # 进程内节流（最小间隔 + 100-500ms随机抖动）
    wait = EM_MIN_INTERVAL - (time.time() - _EM_LAST_CALL[0])
    if wait > 0:
        time.sleep(wait + _rand.uniform(0.10, 0.50))  # 增强抖动：100-500ms

    # V9.2: 同步更新 per-domain 限流器状态，避免与 _quick_request 交替调用时碰撞
    from urllib.parse import urlparse
    _domain = urlparse(url).netloc
    with _DOMAIN_LAST_TIME_LOCK:
        _DOMAIN_LAST_TIME[_domain] = time.time()

    try:
        # 合并headers：Session默认头 + 用户传入头
        session_headers = EM_SESSION.headers.copy()
        if headers:
            session_headers.update(headers)

        return EM_SESSION.get(url, params=params, headers=session_headers,
                             timeout=timeout, **kwargs)
    finally:
        _EM_LAST_CALL[0] = time.time()
        # V9.2: 双向同步 per-domain 限流器
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
    """
    is_em = "eastmoney.com" in urlparse(url).netloc
    # V9.3.2: 数据获取全部直连，不使用系统代理（代理仅用于GD上传）
    _no_proxy = {"http": None, "https": None}
    for attempt in range(max_retries):
        try:
            if method == "POST":
                r = requests.post(url, data=data, params=params,
                                  headers=headers or {"User-Agent": UA},
                                  timeout=timeout, verify=verify, proxies=_no_proxy)
            elif method == "GET":
                r = requests.get(url, params=params,
                                 headers=headers or {"User-Agent": UA},
                                 timeout=timeout, verify=verify, proxies=_no_proxy)
            else:
                return None
            # 方案2：检测429状态码
            if r.status_code == 429:
                if is_em:
                    _RL_STATS["em_429_count"] += 1
                if attempt < max_retries - 1:
                    retry_after = r.headers.get("Retry-After")
                    if retry_after:
                        wait_s = float(retry_after)
                    else:
                        wait_s = 1.0 * (2 ** attempt)
                    time.sleep(wait_s)
                    continue
                return None
            return r
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout,
                requests.exceptions.ProxyError):
            if attempt < max_retries - 1:
                time.sleep(1.0 * (2 ** attempt))
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
        line = f"{now_str} | {domain} | 等待 {wait_ms:.0f}ms | 总请求={_RL_STATS['em_request_count']} | 限流等待={_RL_STATS['em_rate_limit_count']}次 | 429={_RL_STATS['em_429_count']}次\n"
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
    print(f"  平均QPS: {qps:.2f}")
    print(f"  运行时长: {total_s:.0f}秒")
    print("=" * 50)


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


async def _async_request_with_retry(session, url: str, params=None,
                                    headers=None, timeout: int = 15,
                                    max_retries: int = 3, method: str = "GET"):
    """异步版: 带并发限流的东财请求（Semaphore(3) + 统一间隔保护）。

    修复V7.5.1: 在async with块内读取完JSON再返回，避免response对象在块外失效。
    返回: parsed JSON dict 或 None（失败时）
    """
    if not _HAS_ASYNCIO or not _HAS_AIOHTTP:
        return None
    _ensure_async_locks()
    global _em_async_last_request
    import random as _rand

    # Semaphore(3): 最多 3 个协程同时进入 — 完整流程（sleep + 请求发送 + JSON解析）都在锁内
    async with _em_async_lock:
        # 1. 先确保与上一批请求之间有足够间隔
        now = time.time()
        elapsed = now - _em_async_last_request
        interval = 1.0 + _rand.uniform(0.10, 0.30)
        if _em_async_last_request > 0 and elapsed < interval:
            await asyncio.sleep(interval - elapsed)
        _em_async_last_request = time.time()

        await _em_wait_process_interval_async()

        # 2. 在 Semaphore 内发出请求并在块内解析 — 避免response在块外失效
        for attempt in range(max_retries):
            try:
                timeout_obj = aiohttp.ClientTimeout(total=timeout)
                async with session.get(url, params=params, headers=headers or {},
                                       timeout=timeout_obj) as response:
                    if response.status == 200:
                        # ✅ 在 async with 块内读取完数据再返回；content_type=None 跳过响应头校验
                        return await response.json(content_type=None)
                    await asyncio.sleep(1.0 * (attempt + 1))
            except (aiohttp.ClientError, asyncio.TimeoutError):
                if attempt < max_retries - 1:
                    await asyncio.sleep(2.0 * (attempt + 1))
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

    Args:
        is_json:  True (默认) → 解析为 JSON，返回 dict/list。False → 返回原始文本 str
        encoding: 文本模式下的解码方式（如 'gbk'），None 表示用 aiohttp 自动检测
    Returns:
        dict/list (is_json=True), str (is_json=False), 或 None（失败时）
    """
    if not _HAS_ASYNCIO or not _HAS_AIOHTTP:
        return None
    _ensure_async_locks()
    global _gen_async_last_request
    import random as _rand
    import json as _json

    # Semaphore(5): 最多 5 个协程同时进入 — 完整流程（sleep + 请求发送 + 数据读取）都在锁内
    async with _gen_async_lock:
        now = time.time()
        elapsed = now - _gen_async_last_request
        interval = 0.2 + _rand.uniform(0.01, 0.05)
        if _gen_async_last_request > 0 and elapsed < interval:
            await asyncio.sleep(interval - elapsed)
        _gen_async_last_request = time.time()

        await _gen_wait_process_interval_async()

        # 在 Semaphore 内发出请求并在块内读取数据 — 避免 response 在块外失效
        for attempt in range(max_retries):
            try:
                timeout_obj = aiohttp.ClientTimeout(total=timeout)
                if method == "POST":
                    async with session.post(url, data=data, params=params,
                                            headers=headers or {},
                                            timeout=timeout_obj) as response:
                        if response.status == 200:
                            if is_json:
                                return await response.json(content_type=None)
                            return await response.text(encoding=encoding)
                else:
                    async with session.get(url, params=params, headers=headers or {},
                                           timeout=timeout_obj) as response:
                        if response.status == 200:
                            if is_json:
                                return await response.json(content_type=None)
                            return await response.text(encoding=encoding)
                await asyncio.sleep(0.5 * (attempt + 1))
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError, _json.JSONDecodeError):
                if attempt < max_retries - 1:
                    await asyncio.sleep(1.0 * (attempt + 1))
                    continue
                return None
        return None

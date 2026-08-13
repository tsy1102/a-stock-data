#!/usr/bin/env python3
"""sc_fault_tolerance.py — 网络容错层 / 令牌桶限流 / 熔断器模式 / UA池

借鉴 stock-sdk 仓库的三大防封机制：
  1. 令牌桶限流器: 设定 requestsPerSecond 和 maxBurst，强制串行排队扣减令牌
  2. 熔断器模式: 三态转换 Closed→Open→Half-Open，连续N次失败后断路
  3. 指数退避重试 + UA池: 重试等待时间翻倍，随机轮换请求头

依赖：本模块是独立模块，不依赖其他子模块。
"""

from __future__ import annotations

import time
import math
import random
import threading
from typing import Any, Callable, Dict, Optional

_USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/126.0.0.0",
]

_REFERERS = [
    "https://quote.eastmoney.com/",
    "https://datacenter.eastmoney.com/",
    "https://www.eastmoney.com/",
    "https://push2.eastmoney.com/",
    "https://xueqiu.com/",
    "https://www.baidu.com/",
    "https://www.google.com/",
]


class TokenBucket:
    """令牌桶限流器。

    参考 stock-sdk rateLimiter.ts 实现：
    - 设定 requestsPerSecond 每秒请求数
    - maxBurst 最大突发量
    - 通过 sleep 强制串行排队扣减令牌
    """

    def __init__(self, requests_per_second: float, max_burst: int = 5):
        self._rate = requests_per_second
        self._max_burst = max_burst
        self._tokens = max_burst
        self._last_refill = time.time()
        self._lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> None:
        """获取指定数量的令牌，阻塞直到获取成功。"""
        with self._lock:
            self._refill()
            while self._tokens < tokens:
                needed = tokens - self._tokens
                wait_time = needed / self._rate
                time.sleep(wait_time)
                self._refill()
            self._tokens -= tokens

    def try_acquire(self, tokens: int = 1) -> bool:
        """尝试获取令牌，非阻塞，返回是否成功。"""
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

    def _refill(self) -> None:
        """补充令牌。"""
        now = time.time()
        elapsed = now - self._last_refill
        new_tokens = elapsed * self._rate
        self._tokens = min(self._tokens + new_tokens, self._max_burst)
        self._last_refill = now


class CircuitBreaker:
    """熔断器模式。

    参考 stock-sdk circuitBreaker.ts 实现：
    - Closed: 正常通行，计数失败次数
    - Open: 断路状态，直接拒绝请求
    - Half-Open: 半开状态，允许少量请求试探

    状态转换：
      Closed → Open: 连续 failure_threshold 次失败
      Open → Half-Open: 等待 reset_timeout 秒
      Half-Open → Closed: 试探请求成功
      Half-Open → Open: 试探请求失败
    """

    STATE_CLOSED = "closed"
    STATE_OPEN = "open"
    STATE_HALF_OPEN = "half_open"

    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 30.0):
        self._failure_threshold = failure_threshold
        self._reset_timeout = reset_timeout
        self._state = self.STATE_CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._lock = threading.Lock()

    def call(self, func: Callable[[], Any]) -> Any:
        """执行函数，根据熔断器状态决定是否放行。

        V15.3 TOCTOU 修复: 原代码 _maybe_transition() 与读 self._state 之间无锁，
        多线程可能同时看到 HALF_OPEN 状态都去试探。修复方案：
        - _maybe_transition() 在锁内执行（已锁，已原子化）
        - 状态读取改为锁内 `with self._lock` 块，避免 race condition
        - func() 阻塞调用在锁外执行（避免长持锁）
        - _on_success/_on_failure 在锁内执行
        """
        with self._lock:
            self._maybe_transition_locked()
            if self._state == self.STATE_OPEN:
                raise CircuitBreakerError("Circuit breaker is open")
            # 已放行，状态在锁内一致
        try:
            result = func()
        except Exception:
            self._on_failure()  # 内部自带锁
            raise
        self._on_success()  # 内部自带锁
        return result

    async def call_async(self, func: Callable[[], Any]) -> Any:
        """异步版：执行函数。V15.3 同样 TOCTOU 修复。"""
        with self._lock:
            self._maybe_transition_locked()
            if self._state == self.STATE_OPEN:
                raise CircuitBreakerError("Circuit breaker is open")
        try:
            result = await func()
        except Exception:
            self._on_failure()
            raise
        self._on_success()
        return result

    def _maybe_transition(self) -> None:
        """检查是否需要状态转换（自动加锁版，向后兼容）。"""
        with self._lock:
            self._maybe_transition_locked()

    def _maybe_transition_locked(self) -> None:
        """检查是否需要状态转换（V15.3：不带锁版，调用方必须持锁）。

        用于 call/call_async 在外层 with self._lock 块内调用，避免双重加锁。
        """
        if self._state == self.STATE_OPEN:
            elapsed = time.time() - self._last_failure_time
            if elapsed >= self._reset_timeout:
                self._state = self.STATE_HALF_OPEN
                self._failure_count = 0

    def _on_success(self) -> None:
        """成功处理：重置失败计数，回到 Closed 状态。"""
        with self._lock:
            self._failure_count = 0
            self._state = self.STATE_CLOSED

    def _on_failure(self) -> None:
        """失败处理：增加失败计数，可能触发 Open 状态。"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._failure_count >= self._failure_threshold:
                self._state = self.STATE_OPEN

    @property
    def state(self) -> str:
        """当前状态。"""
        self._maybe_transition()
        return self._state


class CircuitBreakerError(Exception):
    """熔断器断路异常。"""

    pass


def get_random_ua() -> str:
    """获取随机 User-Agent。"""
    return random.choice(_USER_AGENTS)


def get_random_referer() -> str:
    """获取随机 Referer。"""
    return random.choice(_REFERERS)


def exponential_backoff(attempt: int, base: float = 1.0, max_wait: float = 32.0) -> float:
    """指数退避计算等待时间。

    Args:
        attempt: 当前重试次数（从0开始）
        base: 基础等待时间（秒）
        max_wait: 最大等待时间（秒）

    Returns:
        float: 等待时间（秒），带随机抖动
    """
    wait = base * (2 ** attempt)
    wait = min(wait, max_wait)
    jitter = random.uniform(0.5, 1.5)
    return wait * jitter


_DOMAIN_TOKEN_BUCKETS: Dict[str, TokenBucket] = {}
_DOMAIN_CIRCUIT_BREAKERS: Dict[str, CircuitBreaker] = {}
_DOMAIN_FT_LOCK = threading.Lock()


def get_domain_token_bucket(domain: str, rps: float = 1.0) -> TokenBucket:
    """获取指定域名的令牌桶限流器（懒加载）。"""
    # V16.0: max_burst 1（消除突发连发，参考仓库全局时间戳强制每请求 ≥1s 无突发模式）
    with _DOMAIN_FT_LOCK:
        if domain not in _DOMAIN_TOKEN_BUCKETS:
            _DOMAIN_TOKEN_BUCKETS[domain] = TokenBucket(requests_per_second=rps, max_burst=1)
        return _DOMAIN_TOKEN_BUCKETS[domain]


def get_domain_circuit_breaker(domain: str) -> CircuitBreaker:
    """获取指定域名的熔断器（懒加载）。"""
    # V16.0: 阈值对齐 config.py（原硬编码 5 vs config 10），避免脱节
    try:
        from core.config import CIRCUIT_BREAKER_FAILURE_THRESHOLD, CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS
        _fail_thr = int(CIRCUIT_BREAKER_FAILURE_THRESHOLD)
        _reset_to = float(CIRCUIT_BREAKER_RESET_TIMEOUT_SECONDS)
    except Exception:
        _fail_thr, _reset_to = 10, 60.0
    with _DOMAIN_FT_LOCK:
        if domain not in _DOMAIN_CIRCUIT_BREAKERS:
            _DOMAIN_CIRCUIT_BREAKERS[domain] = CircuitBreaker(
                failure_threshold=_fail_thr,
                reset_timeout=_reset_to
            )
        return _DOMAIN_CIRCUIT_BREAKERS[domain]


__all__ = [
    "TokenBucket",
    "CircuitBreaker",
    "CircuitBreakerError",
    "get_random_ua",
    "get_random_referer",
    "exponential_backoff",
    "get_domain_token_bucket",
    "get_domain_circuit_breaker",
]
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
import json
import math
import threading
import socket
import logging
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    ParamSpec,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)
from urllib.parse import urlparse

import requests
import urllib3
from . import sc_network_limits as _network_limits
from stock_common._temp import configure_project_temp

P = ParamSpec("P")
R = TypeVar("R")

try:
    from core.config import EM_MIN_INTERVAL, HTTP_TIMEOUT_SECONDS

    _USE_CONFIG = True
except ImportError:
    EM_MIN_INTERVAL = 1.0
    HTTP_TIMEOUT_SECONDS = 15
    _USE_CONFIG = False

try:
    from stock_common.sc_fault_tolerance import (
        get_random_ua,
        get_random_referer,
        exponential_backoff,
        get_domain_circuit_breaker,
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
    '_LOG_DIR',
    '_http_logger',
    '_biz_logger',
    '_fallback_logger',
    '_DEBUG',
    '_debug_log',
    # 常量
    'UA',
    'DATACENTER_URL',
    'JP_URL',
    # Session
    'EM_SESSION',
    'EM_MIN_INTERVAL',
    '_EM_LAST_CALL',
    # 限流
    '_DOMAIN_LIMITS',
    '_DOMAIN_LAST_TIME',
    '_DOMAIN_LAST_TIME_LOCK',
    '_RL_STATS',
    # 进程间锁
    '_em_lock_dir',
    '_em_lock_file',
    '_gen_lock_file',
    '_file_lock_acquire',
    '_file_lock_release',
    # 同步请求
    'em_get',
    '_em_wait_process_interval',
    '_gen_wait_process_interval',
    '_request_with_retry',
    '_quick_request',
    '_do_request',
    '_log_rate_limit',
    'print_rate_limit_stats',
    '_market_code',
    # 异步请求
    '_em_async_lock',
    '_gen_async_lock',
    '_em_async_last_request',
    '_gen_async_last_request',
    '_HAS_ASYNCIO',
    '_HAS_AIOHTTP',
    '_ensure_async_locks',
    '_em_wait_process_interval_async',
    '_gen_wait_process_interval_async',
    'create_async_session',
    '_async_request_with_retry',
    '_async_quick_request',
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
UA: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
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
_EM_LAST_CALL = [0.0]  # 模块级上次请求时间戳（列表实现可变）

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


# 连续 403 按风控组隔离；push2 家族共享，push2delay 与 push2ex 各自独立。
_CONSECUTIVE_403: Dict[str, int] = {}
_EM_403_LOCK = threading.Lock()
_EM_COOKIE_FAIL_COUNT = 0  # V17.0.7: Cookie 过期检测计数器

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
# ⚠️ V17.2.x(2026-09-10) 治理说明：本表与 `core/tdx_client.py::_DOMAIN_LIMITS` (6 域)
# **有意保持独立、不合并**（用户决策 Q5）——本表为 **HTTP 请求级**节流，
# tdx_client 表为 **TDX TCP 长连接级**节流，语义不同不可统一。
#   本表 40 域覆盖 HTTP 数据源；tdx_client 的 6 域是其子集（走 TCP 通道）。
#   **新增/调整域名时须两处同步评估**（详见 tdx_client 侧同名说明）。
_DOMAIN_LIMITS: Dict[str, Dict[str, Any]] = {
    "qt.gtimg.cn": {"sleep_ms": 150, "semaphore": None, "rps": 5.0},
    "quotes.sina.cn": {"sleep_ms": 150, "semaphore": None, "rps": 5.0},
    "finance.pae.baidu.com": {"sleep_ms": 150, "semaphore": None, "rps": 5.0},
    "zx.10jqka.com.cn": {"sleep_ms": 150, "semaphore": None, "rps": 5.0},
    "datacenter-web.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    # Push2 家族由统一风险组以 0.25 RPS 限制；跨进程调度再与东财总速率门槛取严。
    "push2.eastmoney.com": {"sleep_ms": 4000, "semaphore": None, "rps": 0.25},
    # push2ex 使用独立分组节奏；仍受所有 Eastmoney 请求共享的总速率限制。
    "push2ex.eastmoney.com": {"sleep_ms": 1700, "semaphore": None, "rps": 0.6},
    "reportapi.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    "np-weblist.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
    # V16.0.2: 补齐遗漏的东财域名限流（参考仓库"东财所有域名统一限流"原则）
    # 之前以下域名落入默认 100ms=10rps → 封禁隐患（尤其 emappdata 热榜高频）
    "83.push2.eastmoney.com": {"sleep_ms": 4000, "semaphore": None, "rps": 0.25},
    # 历史封禁证据下，push2his 的 0.25 RPS 作为整个 push2 家族的保守速率锚。
    "push2his.eastmoney.com": {"sleep_ms": 4000, "semaphore": None, "rps": 0.25},
    # V16.2.4: push2delay（延时 15 分钟镜像域，fflow 资金流主入口——push2/push2his 连接级风控时唯一可用）
    "push2delay.eastmoney.com": {"sleep_ms": 1000, "semaphore": None, "rps": 1.0},
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
    # V16.3.3: 同花顺官方金融数据 REST（fuyao，字典 §12.8.12c）——官方 4001 限流 + 本地 500ms/2rps 保守
    "fuyao.aicubes.cn": {"sleep_ms": 500, "semaphore": None, "rps": 2.0},
    # V17.0.7: 开盘啦(KPL) longhuvip.com 四子域——Dalvik UA 必须，自行限流 >=200ms
    "apphwhq.longhuvip.com": {"sleep_ms": 200, "semaphore": None, "rps": 5.0},
    "apphis.longhuvip.com": {"sleep_ms": 200, "semaphore": None, "rps": 5.0},
    "applhb.longhuvip.com": {"sleep_ms": 200, "semaphore": None, "rps": 5.0},
    "apparticle.longhuvip.com": {"sleep_ms": 200, "semaphore": None, "rps": 5.0},
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
_em_lock_dir = os.path.join(str(configure_project_temp()), "a_stock_data_v7")
try:
    os.makedirs(_em_lock_dir, exist_ok=True)
except Exception as _e:
    _debug_log(f"sc_network makedirs lock_dir: {_e}")
_em_lock_file = os.path.join(_em_lock_dir, "em_rate_limit")
_gen_lock_file = os.path.join(_em_lock_dir, "gen_rate_limit")
_cls_lock_file = os.path.join(_em_lock_dir, "levistock_cls_rate_limit")
_kph_lock_file = os.path.join(_em_lock_dir, "levistock_kph_rate_limit")
_cls_state_file = os.path.join(_em_lock_dir, "levistock_cls_last_request")
_kph_state_file = os.path.join(_em_lock_dir, "levistock_kph_last_request")
_LEVISTOCK_BLOCK_FILE = os.path.join(_em_lock_dir, "levistock_provider_blocks.json")
_LEVISTOCK_BLOCK_LOCK_FILE = os.path.join(_em_lock_dir, "levistock_provider_blocks.lock")
_LEVISTOCK_BLOCKED_LOCAL: set[str] = set()

# push2 家族共用一个节流/熔断组；push2delay 与 push2ex 使用各自的组策略。
# 三组仍共享下面的 Eastmoney 全局跨进程间隔，避免域名轮换叠加总请求速率。
_EM_PUSH2_FAMILY = (
    "push2.eastmoney.com",
    "push2his.eastmoney.com",
    "83.push2.eastmoney.com",
    "1.push2.eastmoney.com",
    "2.push2.eastmoney.com",
)

# V16.2.8: 参考仓库 PR#36 防封铁律（luodada99 实战案例）——
# 连续 3 次 RemoteDisconnected → 标记该风控面封禁 → 后续请求直接跳过（不浪费请求、不加重封禁）。
# IP 级封禁实测恢复 **20+ 小时**（远超原文档"30-60 分钟"估计，文案已同步修正）。
_EM_BAN_STREAK: Dict[str, int] = {}  # 归一化域 → 连续断连次数
_EM_BANNED_UNTIL: Dict[str, float] = {}  # 归一化域 → 封禁解除时间戳
_EM_BAN_THRESHOLD = 3
_EM_BAN_COOLDOWN = 20 * 3600  # 20 小时


# V17.3.17: 封禁状态跨进程共享文件（与限流文件锁同一目录）。
# 根因：原 _EM_BANNED_UNTIL 仅模块级内存态 → 5 大脚本 + 采集脚本作为独立进程各自为政，
# 任一进程检测到 push2 族封禁后仅自身停火，其余进程毫不知情继续狂轰 → 持续/反复触发东财 IP 级封禁。
# 限流器本身已是跨进程文件锁协调，但封禁态未共享，是真正的"遗漏的限流"一环。
_EM_BANNED_FILE = os.path.join(_em_lock_dir, "em_banned_state")
_EM_BANNED_CACHE: Dict[str, Any] = {"ts": 0.0, "data": {}}  # 进程内缓存（5s TTL，避免每次请求读盘）


def _load_banned_file() -> Dict[str, float]:
    """读取跨进程封禁态（带 5s 进程内缓存）。"""
    _now = time.time()
    cached_data = _EM_BANNED_CACHE.get("data")
    if _now - _EM_BANNED_CACHE.get("ts", 0.0) < 5.0 and isinstance(cached_data, dict):
        return {
            str(key): float(value)
            for key, value in cached_data.items()
            if isinstance(value, (int, float))
        }
    _data: Dict[str, float] = {}
    try:
        if os.path.exists(_EM_BANNED_FILE):
            with open(_EM_BANNED_FILE, "r", encoding="utf-8") as _f:
                _raw = json.load(_f)
                if isinstance(_raw, dict):
                    _data = {k: float(v) for k, v in _raw.items() if isinstance(v, (int, float))}
    except Exception as _e:
        _debug_log(f"sc_network load banned file: {_e}")
    _EM_BANNED_CACHE["ts"] = _now
    _EM_BANNED_CACHE["data"] = _data
    return _data


def _save_banned_file(data: Dict[str, float]) -> None:
    """持久化跨进程封禁态；同时刷新进程内缓存。"""
    try:
        with open(_EM_BANNED_FILE, "w", encoding="utf-8") as _f:
            json.dump(data, _f)
        _EM_BANNED_CACHE["ts"] = time.time()
        _EM_BANNED_CACHE["data"] = data
    except Exception as _e:
        _debug_log(f"sc_network save banned file: {_e}")


def _mark_em_banned(ft_domain: str) -> None:
    """V17.3.17: 标记某风控面 IP 级封禁，跨进程持久化（本进程 + 同机其他进程/脚本全部停火 20h）。

    统一收口自 _record_em_disconnect（连接级断连）与 em_get/_do_request 的连续 403 路径——
    原两条路径只有前者写内存态，403 路径仅在本进程抛错不共享；现统一经此函数写入共享文件。
    """
    _until = time.time() + _EM_BAN_COOLDOWN
    _EM_BANNED_UNTIL[ft_domain] = _until
    _EM_BAN_STREAK[ft_domain] = 0
    try:
        _data = _load_banned_file()
        _data[ft_domain] = _until
        _save_banned_file(_data)
    except Exception as _e:
        _debug_log(f"sc_network mark banned: {_e}")
    try:
        _biz_logger.warning(
            f"EM {ft_domain} 标记 IP 级封禁（实测恢复 20+ 小时）→ 本进程及同机其他进程/脚本"
            f"后续请求均跳过该风控面 {_EM_BAN_COOLDOWN/3600:.0f}h"
        )
    except Exception:
        pass


def _record_em_disconnect(ft_domain: str) -> None:
    """V16.2.8: 记录连接级断连（RemoteDisconnected 等），连续 N 次标记该风控面封禁。"""
    _EM_BAN_STREAK[ft_domain] = _EM_BAN_STREAK.get(ft_domain, 0) + 1
    if _EM_BAN_STREAK[ft_domain] >= _EM_BAN_THRESHOLD:
        _mark_em_banned(ft_domain)


def _em_is_banned(ft_domain: str) -> bool:
    """V16.2.8: 该风控面是否处于封禁跳过期。

    V17.3.17: 先查本进程内存态，再查跨进程共享文件（其他脚本/进程已标记封禁时本进程也停火）。
    """
    _until = _EM_BANNED_UNTIL.get(ft_domain, 0.0)
    if _until > 0:
        if time.time() >= _until:
            _EM_BANNED_UNTIL.pop(ft_domain, None)
        else:
            return True
    # 跨进程：其他进程/脚本写入的封禁态
    _data = _load_banned_file()
    _fu = _data.get(ft_domain, 0.0)
    if _fu > 0:
        if time.time() >= _fu:
            _data.pop(ft_domain, None)
            _save_banned_file(_data)
        else:
            _EM_BANNED_UNTIL[ft_domain] = _fu  # 同步进内存，避免重复读盘
            return True
    return False


def _normalize_em_domain(domain: str) -> str:
    """V16.2.6: 东财 push2 系域名归一化（同风控面共享限流/熔断），其余域名原样返回。"""
    if domain in _EM_PUSH2_FAMILY:
        return "push2.eastmoney.com"
    return domain


def _em_rate_limit_policy(domain: str) -> Tuple[str, float]:
    """Return the Eastmoney risk-group key and its conservative requests-per-second cap."""
    risk_group = _normalize_em_domain(domain)
    if risk_group == "push2.eastmoney.com":
        family_rates = [
            float(_DOMAIN_LIMITS.get(member, {}).get("rps", 1.0)) for member in _EM_PUSH2_FAMILY
        ]
        return risk_group, min(family_rates)
    rps = float(_DOMAIN_LIMITS.get(domain, {}).get("rps", 1.0))
    return risk_group, max(rps, 1e-6)


def _record_em_403(domain: str) -> int:
    """Increment the consecutive 403 counter for one normalized Eastmoney risk group."""
    risk_group = _normalize_em_domain(domain)
    with _EM_403_LOCK:
        count = _CONSECUTIVE_403.get(risk_group, 0) + 1
        _CONSECUTIVE_403[risk_group] = count
    if count >= 3:
        try:
            _mark_em_banned(risk_group)
        except Exception as exc:
            _debug_log(f"could not persist Eastmoney 403 ban for {risk_group}: {exc}")
    return count


def _reset_em_403(domain: str) -> None:
    """Reset only the consecutive 403 counter belonging to this risk group."""
    risk_group = _normalize_em_domain(domain)
    with _EM_403_LOCK:
        _CONSECUTIVE_403.pop(risk_group, None)


def _file_lock_acquire(lock_path: str, timeout: float = 10.0) -> bool:
    """Acquire the shared OS mutex; process termination automatically releases it."""
    return _network_limits.file_lock_acquire(
        lock_path,
        timeout,
        os_module=os,
        time_module=time,
        debug_log=_debug_log,
    )


def _file_lock_release(lock_path: str) -> None:
    """Release the shared OS mutex acquired by this thread."""
    _network_limits.file_lock_release(
        lock_path,
        os_module=os,
        debug_log=_debug_log,
    )


_EM_COOKIE: str | None = None
_EM_COOKIE_LOADED = False


def _get_eastmoney_cookie() -> str:
    """V17.0.7: 东财 Cookie 获取（参考 myhhub/stock eastmoney_fetcher 方案）。

    优先级: 环境变量 EAST_MONEY_COOKIE > credentials/eastmoney_cookie.txt（兼容旧 config/ 路径）> 空。
    Cookie 过期(数天~数周)后需重新从浏览器获取——登录态请求大幅提高 push2 系阈值。
    """
    global _EM_COOKIE, _EM_COOKIE_LOADED
    if _EM_COOKIE_LOADED:
        return _EM_COOKIE or ""
    import os as _os

    # 1) 环境变量
    val = _os.environ.get("EAST_MONEY_COOKIE", "")
    if val:
        _EM_COOKIE = val.strip()
        _EM_COOKIE_LOADED = True
        return _EM_COOKIE
    # 2) 配置文件（V17.0.13: 凭据集中 credentials/，旧 config/ 路径保留兼容）
    for candidate in (
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "credentials", "eastmoney_cookie.txt"
        ),
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "config", "eastmoney_cookie.txt"
        ),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "eastmoney_cookie.txt"),
    ):
        p = os.path.normpath(candidate)
        if os.path.isfile(p):
            try:
                val = open(p, encoding="utf-8").read().strip()
                if val:
                    _EM_COOKIE = val
                    break
            except Exception:
                pass
    _EM_COOKIE_LOADED = True
    return _EM_COOKIE or ""


def em_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
    **kwargs: Any,
) -> Optional[requests.Response]:
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
        get_domain_token_bucket,
        get_domain_circuit_breaker,
        get_random_ua,
        CircuitBreakerError,
    )

    # V17.2.x: _EM_COOKIE_FAIL_COUNT 是模块级全局(151 行初始化), 本函数内 += / = 重绑定,
    # 必须声明 global, 否则 403/429 命中时抛 UnboundLocalError(引用前赋值)。
    global _EM_COOKIE_FAIL_COUNT

    _domain = urlparse(url).netloc
    # push2 家族共享归一化风险组；令牌桶按该组内最严格配置统一限速。
    _ft_domain, _cfg_rps = _em_rate_limit_policy(_domain)

    # V16.2.8: 封禁跳过期直接拒绝（参考仓库 PR#36：连续 3 次断连标记封禁，不再浪费请求）
    if _em_is_banned(_ft_domain):
        _RL_STATS["em_rate_limit_count"] = _RL_STATS.get("em_rate_limit_count", 0) + 1
        _debug_log(f"em_get: {_ft_domain} 封禁跳过中（20h 冷却），拒绝 {url[:80]}")
        return None

    # V12.1: 熔断器保护 - 如果该域名熔断器处于 Open 状态，直接拒绝
    # V16.2 修复: CircuitBreakerError 是 Exception 子类，原 try/except 会吞掉它 → open 时仍发请求。
    # 现在只在"熔断器检查本身失败"时吞错；open 状态直接 raise。
    try:
        _circuit_breaker = get_domain_circuit_breaker(_ft_domain)
    except Exception as _e:
        _debug_log(f"em_get: circuit breaker init failed: {_e}")
        _circuit_breaker = None
    if _circuit_breaker is not None and _circuit_breaker.state == "open":
        _debug_log(f"em_get: domain {_domain} circuit breaker is open, request rejected")
        raise CircuitBreakerError(f"Domain {_domain} is circuit-broken")

    # V12.1: 令牌桶限流 - 替代原有简单 sleep
    # 令牌桶按风险组归一化；push2 家族统一使用家族内最严格的 RPS。
    try:
        _bucket = get_domain_token_bucket(_ft_domain, rps=_cfg_rps)
        _bucket.acquire(1)
        # 本地全东财间隔只承担总量保护，风险组间隔由令牌桶与跨进程调度独立执行。
        _min_interval = max(float(EM_MIN_INTERVAL), 1.0)
        _elapsed = time.time() - _EM_LAST_CALL[0]
        if _elapsed < _min_interval:
            time.sleep(_min_interval - _elapsed)
        _EM_LAST_CALL[0] = time.time()
    except Exception as _e:
        _debug_log(f"em_get: token bucket acquire failed: {_e}")
        # Fallback: 使用原有 sleep 逻辑
        wait = max(float(EM_MIN_INTERVAL), 1.0) - (time.time() - _EM_LAST_CALL[0])
        if wait > 0:
            time.sleep(wait + _rand.uniform(0.10, 0.50))

    def _wait_for_retry_slot() -> None:
        """Reserve another fully rate-limited Eastmoney request slot."""
        try:
            get_domain_token_bucket(_ft_domain, rps=_cfg_rps).acquire(1)
            _min_interval = max(float(EM_MIN_INTERVAL), 1.0)
            _elapsed = time.time() - _EM_LAST_CALL[0]
            if _elapsed < _min_interval:
                time.sleep(_min_interval - _elapsed)
        except Exception as _e:
            _debug_log(f"em_get: retry token bucket acquire failed: {_e}")
            _min_interval = max(float(EM_MIN_INTERVAL), 1.0)
            _elapsed = time.time() - _EM_LAST_CALL[0]
            if _elapsed < _min_interval:
                time.sleep(_min_interval - _elapsed + _rand.uniform(0.10, 0.50))
        _EM_LAST_CALL[0] = time.time()
        _em_wait_process_interval(_domain)

    # V16.0: 接通同步进程间文件锁（_em_wait_process_interval 原本定义但无调用方），
    # 使 --concurrency 3 时跨进程仍 ≤1 rps
    try:
        _em_wait_process_interval(_domain)
    except Exception as _e:
        _debug_log(f"em_get: process interval: {_e}")
        return None

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

        # V17.0.7: 东财 Cookie 注入——登录态请求大幅提高 push2 系封禁阈值
        # (参考 myhhub/stock eastmoney_fetcher.py 方案)
        _em_cookie = _get_eastmoney_cookie()
        if _em_cookie:
            session_headers["Cookie"] = _em_cookie

        # 一次采集调用最多重试一次明确的临时网络错误或 HTTP 408/5xx。
        # 每次重试重新取得令牌并经过跨进程间隔；403/429 不在此重试。
        _response = None
        for _attempt in range(2):
            try:
                # DNS 解析阶段硬超时护栏，挂起转换为可控的 ConnectionError。
                _resolve_host_with_timeout(_domain)
                _response = EM_SESSION.get(
                    url, params=params, headers=session_headers, timeout=timeout, **kwargs
                )
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as _e:
                if _attempt >= 1:
                    raise
                if isinstance(_e, requests.exceptions.ConnectionError):
                    _record_em_disconnect(_ft_domain)
                    if _em_is_banned(_ft_domain):
                        _debug_log(f"em_get: {_ft_domain} ban threshold reached; retry stopped")
                        return None
                time.sleep(exponential_backoff(_attempt, base=1.0, max_wait=30.0))
                _wait_for_retry_slot()
                _RL_STATS["em_request_count"] += 1
                continue

            if (
                _response.status_code == 408 or 500 <= _response.status_code < 600
            ) and _attempt < 1:
                _response.close()
                time.sleep(exponential_backoff(_attempt, base=1.0, max_wait=30.0))
                _wait_for_retry_slot()
                _RL_STATS["em_request_count"] += 1
                continue
            break

        if _response is None:
            return None

        # V16.2 修复: 403/429 统一走失败路径 —— 不再返回响应走"成功"分支（原 403 后仍 _on_success 并返回 403 响应）
        _status = _response.status_code
        if _status in (403, 429):
            # V17.0.7: Cookie 过期检测——已配置 Cookie 时连续 403/429 说明登录态失效
            if _em_cookie:
                _EM_COOKIE_FAIL_COUNT += 1
                if _EM_COOKIE_FAIL_COUNT >= 5:
                    print(
                        "\n" + "⚠️" * 20 + "\n"
                        "  ⚠️ 东财 Cookie 疑似过期！已配置 Cookie 但连续 "
                        f"{_EM_COOKIE_FAIL_COUNT} 次 403/429。\n"
                        "  请更新 Cookie：\n"
                        "    1. Chrome 打开 quote.eastmoney.com 并登录\n"
                        "    2. F12 → Console → 输入 document.cookie → 回车\n"
                        "    3. 复制输出内容，替换 credentials/eastmoney_cookie.txt 文件全文\n"
                        "    4. 或执行: setx EAST_MONEY_COOKIE \"粘贴的内容\" 后重启终端\n"
                        + "⚠️" * 20
                        + "\n",
                        flush=True,
                    )
                    _EM_COOKIE_FAIL_COUNT = 0  # 只提醒一次，重置计数
            else:
                _EM_COOKIE_FAIL_COUNT = 0
            _RL_STATS["em_403_count"] += 1 if _status == 403 else 0
            _RL_STATS["em_429_count"] = _RL_STATS.get("em_429_count", 0) + (
                1 if _status == 429 else 0
            )
            try:
                _biz_logger.warning(f"EM {_status} rate-limited: {_domain} {url[:120]}")
            except Exception:
                pass
            if _status == 403:
                _consecutive_403 = _record_em_403(_domain)
                if _consecutive_403 >= 3:
                    raise RateLimitBlockedError(
                        f"EM 风险组 {_ft_domain} 连续 {_consecutive_403} 次 403，疑似被限。"
                        f"建议: 停止 20+ 小时（参考仓库 PR#36 实测恢复时间）/ 换网络 / 调大 EM_MIN_INTERVAL / 切换备胎源"
                    )
            else:
                _reset_em_403(_domain)  # 429 不算同风险组的连续 403
            # 熔断失败计数 + 退避
            try:
                get_domain_circuit_breaker(_ft_domain)._on_failure()
            except Exception:
                pass
            return None  # V16.2: 明确失败语义（对齐调用方 `if r is None` 约定），不再当成功返回

        if _response.status_code >= 400:
            try:
                get_domain_circuit_breaker(_ft_domain)._on_failure()
            except Exception:
                pass
            return _response

        _reset_em_403(_domain)

        # V12.1: 成功则重置熔断器 + 清零断连计数（V16.2.8）
        try:
            _circuit_breaker = get_domain_circuit_breaker(_ft_domain)
            _circuit_breaker._on_success()
        except Exception:
            pass
        _EM_BAN_STREAK.pop(_ft_domain, None)

        return _response
    except Exception as _e:
        # V12.1: 失败则记录到熔断器
        try:
            _circuit_breaker = get_domain_circuit_breaker(_ft_domain)
            _circuit_breaker._on_failure()
        except Exception:
            pass
        # V16.2.8: 连接级断连（RemoteDisconnected 等）累计 → 标记封禁跳过（参考仓库 PR#36）
        if isinstance(
            _e, (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout)
        ):
            _record_em_disconnect(_ft_domain)
        raise
    finally:
        _EM_LAST_CALL[0] = time.time()
        with _DOMAIN_LAST_TIME_LOCK:
            _DOMAIN_LAST_TIME[_domain] = time.time()
        _RL_STATS["em_request_count"] += 1


def _process_interval_wait(
    lock_file: str, target_interval: float, use_lock: bool = True, use_content_ts: bool = True
) -> float:
    """Shared sync interval gate used by both Eastmoney and general HTTP requests.
    Return actual sleep seconds after reserving the next cross-process request slot.

    ``use_lock`` and ``use_content_ts`` are kept for compatibility with the old private
    helper signature; the gate always uses the OS mutex and versioned content state.
    """
    return _network_limits.process_interval_wait(
        lock_file,
        target_interval,
        use_lock,
        use_content_ts,
        file_lock_acquire=_file_lock_acquire,
        file_lock_release=_file_lock_release,
        debug_log=_debug_log,
        os_module=os,
        open_file=open,
        time_module=time,
    )


def _provider_interval_wait(lock_file: str, state_file: str, target_interval: float) -> float:
    """Reserve a cross-process request slot for clients that bypass ``_quick_request``.

    The OS mutex file is persistent and separate from the state file. Reserving the next slot
    before releasing the mutex keeps concurrent processes from sending requests back-to-back.
    """
    return _network_limits.provider_interval_wait(
        lock_file,
        state_file,
        target_interval,
        file_lock_acquire=_file_lock_acquire,
        file_lock_release=_file_lock_release,
        debug_log=_debug_log,
        open_file=open,
        time_module=time,
    )


def _em_wait_process_interval(domain: Optional[str] = None) -> float:
    """Atomically reserve the Eastmoney global slot and optional risk-group slot."""
    import random as _rand

    if domain:
        risk_group, rps = _em_rate_limit_policy(domain)
        group_interval = 1.0 / rps
    else:
        risk_group, group_interval = "__all__", 0.0
    global_interval = max(1.0, float(EM_MIN_INTERVAL)) + _rand.uniform(0.10, 0.30)
    return _network_limits.process_rate_limit_wait(
        _em_lock_file,
        global_interval,
        risk_group,
        group_interval,
        file_lock_acquire=_file_lock_acquire,
        file_lock_release=_file_lock_release,
        debug_log=_debug_log,
        os_module=os,
        open_file=open,
        time_module=time,
    )


def _gen_wait_process_interval() -> float:
    """GEN sync gate with the same cross-process mutex as the async path."""
    import random as _rand

    return _process_interval_wait(
        _gen_lock_file,
        0.2 + _rand.uniform(0.01, 0.05),
        use_lock=True,
        use_content_ts=True,
    )


def _levistock_provider_is_blocked(family: str) -> bool:
    """Fail closed for a Levistock provider family after a confirmed ban signal."""
    if family in _LEVISTOCK_BLOCKED_LOCAL:
        return True
    if family not in {"cls", "kph"}:
        raise ValueError(f"unknown Levistock provider family: {family}")
    try:
        with open(_LEVISTOCK_BLOCK_FILE, "r", encoding="utf-8") as stream:
            state = json.load(stream)
    except FileNotFoundError:
        return False
    except (OSError, json.JSONDecodeError) as exc:
        _debug_log(f"Levistock block state unreadable; fail closed: {type(exc).__name__}")
        return True
    if not isinstance(state, dict):
        _debug_log("Levistock block state root invalid; fail closed")
        return True
    entry = state.get(family)
    return isinstance(entry, dict) and entry.get("blocked") is True


def _mark_levistock_provider_block(family: str, error: Any) -> bool:
    """Persist a 403/429 or explicit ban signal until the user verifies recovery."""
    import re

    if family not in {"cls", "kph"}:
        raise ValueError(f"unknown Levistock provider family: {family}")
    response = getattr(error, "response", None)
    status_values = (getattr(response, "status_code", None), getattr(error, "status_code", None))
    status_code = None
    for value in status_values:
        if value is None:
            continue
        try:
            candidate = int(value)
        except (TypeError, ValueError):
            continue
        if candidate in {403, 429}:
            status_code = candidate
            break
    message = str(error or "")[:300]
    if status_code is None:
        match = re.search(r"\b(403|429)\b", message)
        if match:
            status_code = int(match.group(1))
    blocked_signal = status_code in {403, 429} or bool(
        re.search(r"\b403\b|\b429\b|blocked|banned|rate.?limit|封禁|限流|访问频繁", message, re.I)
    )
    if not blocked_signal:
        return False

    _LEVISTOCK_BLOCKED_LOCAL.add(family)
    if not _file_lock_acquire(_LEVISTOCK_BLOCK_LOCK_FILE, timeout=3.0):
        _debug_log(f"Levistock {family} block could not be shared across processes")
        return True
    try:
        try:
            with open(_LEVISTOCK_BLOCK_FILE, "r", encoding="utf-8") as stream:
                state = json.load(stream)
        except FileNotFoundError:
            state = {}
        except (OSError, json.JSONDecodeError) as exc:
            _debug_log(f"Levistock block state unreadable while updating: {type(exc).__name__}")
            return True
        if not isinstance(state, dict):
            _debug_log("Levistock block state root invalid while updating")
            return True
        state[family] = {
            "blocked": True,
            "status_code": status_code,
            "blocked_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "reason": message,
        }
        temporary = f"{_LEVISTOCK_BLOCK_FILE}.{os.getpid()}.tmp"
        with open(temporary, "w", encoding="utf-8") as stream:
            json.dump(state, stream, ensure_ascii=False, indent=2)
        os.replace(temporary, _LEVISTOCK_BLOCK_FILE)
    except OSError as exc:
        _debug_log(f"Levistock {family} block persistence failed: {type(exc).__name__}")
    finally:
        _file_lock_release(_LEVISTOCK_BLOCK_LOCK_FILE)
    return True


def _cls_wait_process_interval() -> float:
    """Levistock CLS direct calls: reserve a cross-process slot at 2.5 requests/second."""
    import random as _rand

    if _levistock_provider_is_blocked("cls"):
        raise RuntimeError("Levistock CLS provider family is blocked until manual recovery review")
    return _provider_interval_wait(
        _cls_lock_file,
        _cls_state_file,
        0.4 + _rand.uniform(0.02, 0.10),
    )


def _kph_wait_process_interval() -> float:
    """Levistock KPH direct calls: reserve at most one request per second across processes."""
    import random as _rand

    if _levistock_provider_is_blocked("kph"):
        raise RuntimeError("Levistock KPH provider family is blocked until manual recovery review")
    return _provider_interval_wait(
        _kph_lock_file,
        _kph_state_file,
        1.0 + _rand.uniform(0.10, 0.25),
    )


def _request_with_retry(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Union[int, Tuple[float, float]] = HTTP_TIMEOUT_SECONDS,
    max_retries: int = 3,
    data: Optional[Union[Dict[str, Any], str, bytes]] = None,
    method: str = "GET",
    verify: bool = True,
) -> Optional[requests.Response]:  # V16.2: 默认校验证书
    """V17.0 S2: 兼容别名——统一走 _quick_request(封禁跳过 + EM 容错 + 跨进程锁)。

    历史: 原独立实现缺 EM 封禁跳过/域容错; V16.2.10 起新代码全部迁移 _quick_request,
    V17.0 将剩余 4 个调用点(东财域)迁移后本函数仅作外部兼容保留。
    """
    return _quick_request(url, params, headers, timeout, max_retries, data, method, verify)


def _quick_request(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Union[int, Tuple[float, float]] = HTTP_TIMEOUT_SECONDS,
    max_retries: int = 3,
    data: Optional[Union[Dict[str, Any], str, bytes]] = None,
    method: str = "GET",
    verify: bool = True,
    error_out: Optional[Dict[str, Any]] = None,
    stream: bool = False,
) -> Optional[requests.Response]:  # V16.2: 默认校验证书
    """通用 HTTP 请求（按域名独立限流）。

    V7.5 优化版：按域名独立控制并发和 sleep，不再使用全局 Semaphore。
    V8.5 新增：添加随机抖动防止被限流。
    V9.0 新增：线程锁保护 + 限流统计。
    V16.2 新增：eastmoney 域接入 TokenBucket + CircuitBreaker + 跨进程文件锁（消除限流旁路）。

    ``max_retries`` 是总尝试次数（含首次请求）；连接/超时类异常和 HTTP 408/5xx
    使用有界退避，HTTP 403/429 不重试。
    """
    import random as _rand

    if error_out is not None:
        error_out.clear()

    # 解析域名
    parsed = urlparse(url)
    domain = parsed.netloc

    is_em = "eastmoney.com" in domain
    if is_em:
        # V16.2.8: 封禁跳过期直接返回 None（参考仓库 PR#36：不浪费请求、不加重封禁）
        _ft_domain = _normalize_em_domain(domain)
        if _em_is_banned(_ft_domain):
            _RL_STATS["em_rate_limit_count"] = _RL_STATS.get("em_rate_limit_count", 0) + 1
            _debug_log(f"quick_request: {_ft_domain} 封禁跳过中（20h 冷却），拒绝 {url[:80]}")
            _record_request_failure(error_out, kind="ip_banned", domain=_ft_domain, attempt=0)
            return None
        # V16.2: 东财域统一走容错层（令牌桶 + 熔断），与 em_get 同口径
        # V16.2.6: 桶/熔断按归一化 key（push2 系共享风控面）；consume() 方法不存在
        # （原调用每次抛 AttributeError 被吞 → 桶从未生效，只剩 1s 文件锁）→ 改阻塞 acquire()
        try:
            from stock_common.sc_fault_tolerance import (
                get_domain_token_bucket,
                get_domain_circuit_breaker,
            )

            _cb = get_domain_circuit_breaker(_ft_domain)
            if _cb.state == "open":
                # V16.2: 返回 None 而非抛异常（对齐调用方 `if r is None` 约定，69 处调用方无需全改）
                _RL_STATS["em_rate_limit_count"] = _RL_STATS.get("em_rate_limit_count", 0) + 1
                _log_rate_limit(domain, 0.0)
                _record_request_failure(
                    error_out, kind="circuit_open", domain=_ft_domain, attempt=0
                )
                return None
            _risk_group, _cfg_rps = _em_rate_limit_policy(domain)
            try:
                get_domain_token_bucket(_ft_domain, rps=float(_cfg_rps)).acquire(1)
            except Exception as _e:
                _debug_log(f"quick_request token bucket acquire failed ({domain}): {_e}")
            # 全局节奏和风险组节奏由 _do_request 的原子跨进程调度统一执行；
            # 此处只预取进程内风险组令牌，避免重复预留全局时隙。
        except Exception as _e:
            _debug_log(f"quick_request ft init error ({domain}): {_e}")

    # 获取该域名的限流配置（默认 sleep=100ms 作为兜底）
    limit = _DOMAIN_LIMITS.get(domain, {"sleep_ms": 100})
    sleep_ms = limit["sleep_ms"]

    # 按域名独立 sleep，添加 10-30ms 随机抖动
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

    return _do_request(
        url,
        params,
        headers,
        timeout,
        max_retries,
        data,
        method,
        verify,
        error_out,
        stream=stream,
    )


# ─── DNS 解析阶段硬超时护栏（根因修复，2026-09-09）───
# requests 的 timeout 仅覆盖 connect/read，不覆盖 DNS 解析（socket.getaddrinfo 不受其约束）。
# 上游 DNS/路由间歇挂起时 requests 会无限阻塞而不抛异常，绕过所有 exception-based fallback，
# 最终表现为 asyncio.gather 整批停滞 → main.py 900s 卡死强杀(-1)。此护栏用独立线程 +
# join(timeout) 给 DNS 阶段加墙：挂起即快速抛 ConnectionError，落入既有 fallback 路径
# （如 _do_request 的 ConnectionError except → 重试 → return None → 调用方降级）。
# 带 TTL 缓存：命中缓存仅字典查找（零额外 DNS 查询）；仅缓存失效时做真实解析（此时才有线程超时护栏）。
_DNS_CACHE: Dict[str, Tuple[Optional[str], float]] = {}
_DNS_CACHE_TTL = 300.0
_DNS_CACHE_LOCK = threading.Lock()
_DNS_RESOLVE_TIMEOUT = 5.0
_DNS_PREFLIGHT_RETRIES = 1
_DNS_PREFLIGHT_RETRY_DELAY = 0.25


class DNSResolutionError(requests.exceptions.ConnectionError):
    """A hostname lookup failed before any HTTP request could reach the provider."""

    def __init__(self, message: str, *, timed_out: bool = False) -> None:
        super().__init__(message)
        self.timed_out = timed_out


def _resolve_host_with_timeout(host: str, timeout: float = _DNS_RESOLVE_TIMEOUT) -> None:
    """对 host 做带硬超时的 DNS 解析预检。解析挂起/失败即抛 requests.exceptions.ConnectionError。

    已为 IP 的 host 直接跳过（无需 DNS）。成功解析结果按 TTL 缓存，避免热路径每请求真实查询。
    """
    if not host:
        return
    _h = host.split(":")[0]
    # 已是 IP（v4/v6）则跳过 DNS
    if _h.replace(".", "").isdigit() or (_h.startswith("[") and _h.endswith("]")):
        return
    _now = time.time()
    with _DNS_CACHE_LOCK:
        _cached = _DNS_CACHE.get(_h)
    if _cached is not None and _now - _cached[1] < _DNS_CACHE_TTL:
        return  # 缓存命中（含此前成功解析的 IP），跳过预检
    for dns_attempt in range(_DNS_PREFLIGHT_RETRIES + 1):
        _res: Dict[str, Any] = {}

        def _resolve() -> None:
            try:
                _res["ip"] = socket.gethostbyname(_h)
            except Exception as _e:  # DNS 失败（NXDOMAIN / 临时错误 / 等服务端拒绝）
                _res["err"] = _e

        _th = threading.Thread(target=_resolve, daemon=True)
        _th.start()
        _th.join(timeout)
        if _th.is_alive():
            # 不能再启动并行解析线程：首次解析仍在后台运行。
            raise DNSResolutionError(
                f"DNS resolution timeout for {_h} (>={timeout}s, 疑似解析挂起)",
                timed_out=True,
            )
        if "err" in _res:
            if dns_attempt < _DNS_PREFLIGHT_RETRIES:
                # 只重试 DNS；此时尚未发出 HTTP 请求，不增加上游请求频率或封禁风险。
                time.sleep(_DNS_PREFLIGHT_RETRY_DELAY)
                continue
            raise DNSResolutionError(f"DNS resolution failed for {_h}: {_res['err']}") from _res[
                "err"
            ]
        with _DNS_CACHE_LOCK:
            _DNS_CACHE[_h] = (_res.get("ip"), _now)
        return


def _is_dns_resolution_error(error: BaseException) -> bool:
    """Recognize resolver failures so they do not count as provider disconnects."""
    markers = (
        "dns resolution",
        "getaddrinfo failed",
        "name resolution",
        "failed to resolve",
        "nameresolutionerror",
        "temporary failure in name resolution",
    )
    pending: List[BaseException] = [error]
    seen: set[int] = set()
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, (DNSResolutionError, socket.gaierror)):
            return True
        if any(marker in str(current).lower() for marker in markers):
            return True
        for attr in ("__cause__", "__context__", "reason", "original_error"):
            nested = getattr(current, attr, None)
            if isinstance(nested, BaseException):
                pending.append(nested)
        for arg in getattr(current, "args", ()):
            if isinstance(arg, BaseException):
                pending.append(arg)
    return False


def _record_request_failure(
    error_out: Optional[Dict[str, Any]],
    *,
    kind: str,
    domain: str,
    attempt: Optional[int] = None,
    status_code: Optional[int] = None,
    error: Optional[BaseException] = None,
) -> None:
    """Fill opt-in, query-string-free details for a failed HTTP request."""
    if error_out is None:
        return
    error_out.update({"kind": kind, "domain": domain})
    if attempt is not None:
        error_out["attempts"] = attempt
    if status_code is not None:
        error_out["status_code"] = status_code
    if error is not None:
        error_out["error_type"] = type(error).__name__
        message = str(error).split("?", 1)[0].strip()
        if message:
            error_out["message"] = message[:160]


def _do_request(
    url: str,
    params: Optional[Dict[str, Any]],
    headers: Optional[Dict[str, str]],
    timeout: Union[int, Tuple[float, float]],
    max_retries: int,
    data: Optional[Union[Dict[str, Any], str, bytes]],
    method: str,
    verify: bool,
    error_out: Optional[Dict[str, Any]] = None,
    stream: bool = False,
) -> Optional[requests.Response]:
    """内部：执行 HTTP 请求 + 重试（由 _request_with_retry / _quick_request 调用）。

    Transient connection/timeouts and HTTP 408/5xx receive bounded backoff retries.
    HTTP 403/429 stop immediately so a ban or rate limit is not amplified.
    V9.3.2 新增：禁用系统代理（数据获取全部直连）+ 捕获 ProxyError 和兜底 Exception。
    V11.5 新增：随机UA/Referer + 指数退避 + 熔断器模式
    """
    is_em = "eastmoney.com" in urlparse(url).netloc
    domain = urlparse(url).netloc
    # V9.3.2: 数据获取全部直连，不使用系统代理（代理仅用于GD上传）
    _no_proxy = {"http": None, "https": None}

    for attempt in range(max_retries):
        try:
            # 东财全局时隙与 endpoint 风险组时隙在同一文件锁内原子预留，
            # 所有 Eastmoney 域名共享总速率门槛，push2 / push2ex / push2delay 再各自限速。
            if is_em:
                _ft_domain = _normalize_em_domain(domain)
                if _em_is_banned(_ft_domain):
                    _record_request_failure(
                        error_out, kind="ip_banned", domain=_ft_domain, attempt=attempt
                    )
                    return None
                if attempt > 0:
                    _risk_group, _retry_rps = _em_rate_limit_policy(domain)
                    try:
                        from stock_common.sc_fault_tolerance import get_domain_token_bucket

                        get_domain_token_bucket(_ft_domain, rps=float(_retry_rps)).acquire(1)
                    except Exception as _e:
                        _debug_log(f"quick_request retry token bucket failed ({domain}): {_e}")
                        _min_interval = max(float(EM_MIN_INTERVAL), 1.0)
                        _elapsed = time.time() - _EM_LAST_CALL[0]
                        if _elapsed < _min_interval:
                            time.sleep(_min_interval - _elapsed)
                    _EM_LAST_CALL[0] = time.time()
                    _RL_STATS["em_request_count"] += 1
                _em_wait_process_interval(domain)
            _req_headers = headers.copy() if headers else {}
            if not _req_headers.get("User-Agent"):
                if _HAS_FAULT_TOLERANCE:
                    _req_headers["User-Agent"] = get_random_ua()
                else:
                    _req_headers["User-Agent"] = UA
            if is_em and not _req_headers.get("Referer"):
                if _HAS_FAULT_TOLERANCE:
                    _req_headers["Referer"] = get_random_referer()

            # V17.2.x: DNS 解析阶段硬超时护栏——在 connect/read 之前先把"解析挂起"转换为
            # ConnectionError，使其落入下方 except（重试→return None）的既有 fallback 路径。
            _resolve_host_with_timeout(domain)

            if method == "POST":
                r = _HTTP_SESSION.post(
                    url,
                    data=data,
                    params=params,
                    headers=_req_headers,
                    timeout=timeout,
                    verify=verify,
                    proxies=cast(Dict[str, str], _no_proxy),
                    stream=stream,
                )
            elif method == "GET":
                r = _HTTP_SESSION.get(
                    url,
                    params=params,
                    headers=_req_headers,
                    timeout=timeout,
                    verify=verify,
                    proxies=cast(Dict[str, str], _no_proxy),
                    stream=stream,
                )
            else:
                _record_request_failure(
                    error_out, kind="invalid_method", domain=domain, attempt=attempt + 1
                )
                return None

            if stream and r.status_code >= 400:
                r.close()

            if r.status_code == 403:
                # Eastmoney 403 counts only within its normalized risk group.
                if is_em:
                    _RL_STATS["em_403_count"] += 1
                    try:
                        _biz_logger.warning(f"EM 403 rate-limited: {domain} {url[:120]}")
                    except Exception:
                        pass
                    # Three consecutive 403s stop only this normalized risk group.
                    _consecutive_403 = _record_em_403(domain)
                    if _consecutive_403 >= 3:
                        raise RateLimitBlockedError(
                            f"EM 风险组 {_normalize_em_domain(domain)} 连续 "
                            f"{_consecutive_403} 次 403，疑似被限。"
                            f"建议: 停止 20+ 小时（参考仓库 PR#36 实测恢复时间）/ 换网络 / 调大 EM_MIN_INTERVAL / 切换备胎源"
                        )
                if _HAS_FAULT_TOLERANCE:
                    try:
                        get_domain_circuit_breaker(
                            _normalize_em_domain(domain) if is_em else domain
                        )._on_failure()
                    except Exception:
                        pass
                _record_request_failure(
                    error_out,
                    kind="http_403",
                    domain=domain,
                    attempt=attempt + 1,
                    status_code=403,
                )
                return None
            if r.status_code == 429:
                if is_em:
                    _RL_STATS["em_429_count"] += 1
                    _reset_em_403(domain)
                    if _HAS_FAULT_TOLERANCE:
                        try:
                            get_domain_circuit_breaker(_normalize_em_domain(domain))._on_failure()
                        except Exception:
                            pass
                _record_request_failure(
                    error_out,
                    kind="http_429",
                    domain=domain,
                    attempt=attempt + 1,
                    status_code=429,
                )
                return None
            if r.status_code == 408 or 500 <= r.status_code < 600:
                if attempt < max_retries - 1:
                    r.close()
                    wait_s = exponential_backoff(attempt, base=1.0, max_wait=30.0)
                    time.sleep(wait_s)
                    continue
            # Opt-in diagnostics treat other HTTP errors as failed responses for
            # collectors, while callers without error_out retain the raw Response.
            if r.status_code >= 400 and error_out is not None:
                _record_request_failure(
                    error_out,
                    kind="http_error",
                    domain=domain,
                    attempt=attempt + 1,
                    status_code=r.status_code,
                )
                return None
            # V16: 成功响应（<400）重置连续 403 计数
            if is_em and r.status_code < 400:
                _reset_em_403(domain)
            if is_em and r.status_code < 400:
                _ft_domain = _normalize_em_domain(domain)
                _EM_BAN_STREAK.pop(_ft_domain, None)
                if _HAS_FAULT_TOLERANCE:
                    try:
                        get_domain_circuit_breaker(_ft_domain)._on_success()
                    except Exception:
                        pass
            return r
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ProxyError,
        ) as _e:
            _dns_failure = _is_dns_resolution_error(_e)
            if is_em and _HAS_FAULT_TOLERANCE and not _dns_failure:
                try:
                    get_domain_circuit_breaker(_normalize_em_domain(domain))._on_failure()
                except Exception:
                    pass
            if (
                is_em
                and isinstance(
                    _e, (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout)
                )
                and not _dns_failure
            ):
                _ft_domain = _normalize_em_domain(domain)
                _record_em_disconnect(_ft_domain)
                if _em_is_banned(_ft_domain):
                    _record_request_failure(
                        error_out,
                        kind="ip_banned",
                        domain=_ft_domain,
                        attempt=attempt + 1,
                        error=_e,
                    )
                    return None
            if attempt < max_retries - 1:
                if _HAS_FAULT_TOLERANCE:
                    # V16 增强: HTTP 000 连接被拒 = 间歇风控，长退避等待恢复
                    wait_s = exponential_backoff(attempt, base=1.0, max_wait=60.0)
                else:
                    wait_s = 1.0 * (2**attempt)
                time.sleep(wait_s)
                continue
            failure_kind = (
                "timeout"
                if isinstance(
                    _e,
                    (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout),
                )
                else "connection_error"
            )
            _record_request_failure(
                error_out,
                kind=failure_kind,
                domain=domain,
                attempt=0 if _dns_failure else attempt + 1,
                error=_e,
            )
            return None
        except Exception as _e:
            _record_request_failure(
                error_out,
                kind=(
                    "rate_limited"
                    if type(_e).__name__ == "RateLimitBlockedError"
                    else "request_error"
                ),
                domain=domain,
                attempt=attempt + 1,
                error=_e,
            )
            _debug_log(f"sc_network _do_request unexpected error ({url}): {_e}")
            return None
    if error_out is not None and max_retries <= 0:
        _record_request_failure(error_out, kind="no_attempts", domain=domain, attempt=0)
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


def requires_push2(fn: Callable[P, R]) -> Callable[P, R]:
    """Audit-only decorator for functions that depend on push2 endpoints.

    This decorator only logs and counts calls; it does not throttle requests.
    Eastmoney throttling is enforced by ``em_get``, ``_quick_request`` and the
    shared process risk-group scheduler.
    用法:
        @requires_push2
        def get_x(...): ...
    """
    import functools

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            _biz_logger.warning(f"PUSH2 used: {fn.__module__}.{fn.__name__}")
        except Exception:
            pass
        # V16.4.1: 原 setdefault 第二次起不生效 → push2 审计计数恒为 1
        _RL_STATS["push2_call_count"] = _RL_STATS.get("push2_call_count", 0) + 1
        return fn(*args, **kwargs)

    return wrapper


def _market_code(code: str) -> int:
    """6位代码 → TDX 市场代码 (0=深圳, 1=上海, 2=北交所)。

    V16.3 O16: 补北交所分支——920 号段（2024-10 起启用）及 8/4 老号段返回 2，
    此前 920 落到 0(深圳)，TDX finance_info 等按错误市场请求（参考仓库 v3.5.1 同款修复）。
    V17.0 S3: 补 9 开头沪 B 股(900xxx) → 1，与 tdx_client._market_from_code 口径对齐。
    """
    if code.startswith(("92", "8", "4", "43", "83", "87")):
        return 2
    return 1 if code.startswith(("6", "9")) else 0


# ══════════════════════════════════════════════════════════════════════════════
# V7.5: asyncio 异步请求层 (aiohttp + asyncio.Semaphore)
# 功能: 在异步模式下替代 threading.Lock + requests，实现 2-3x 性能提升
# ══════════════════════════════════════════════════════════════════════════════

_em_async_lock = None  # asyncio.Semaphore(3) — 测试 45 请求 0 次 429，安全
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


def _ensure_async_locks() -> None:
    """懒加载: 创建 asyncio.Semaphore（统一 Semaphore(3)）。"""
    global _em_async_lock, _gen_async_lock
    if _em_async_lock is None and _HAS_ASYNCIO:
        _em_async_lock = asyncio.Semaphore(3)  # 东财: 最多 3 并发请求
    if _gen_async_lock is None and _HAS_ASYNCIO:
        _gen_async_lock = asyncio.Semaphore(3)  # 通用: 与东财保持一致


async def _process_interval_wait_async(
    lock_file: str, target_interval: float, use_content_ts: bool = False
) -> float:
    """Run the sync cross-process gate off-loop so async and sync share one lock/state."""
    try:
        return await asyncio.to_thread(
            _process_interval_wait,
            lock_file,
            target_interval,
            True,
            True,
        )
    except Exception as _e:
        _debug_log(f"sc_network process_interval_wait_async: {_e}")
        raise


async def _em_wait_process_interval_async(domain: Optional[str] = None) -> float:
    """Use the same atomic global-plus-group EM gate as synchronous requests."""
    return await asyncio.to_thread(_em_wait_process_interval, domain)


async def _gen_wait_process_interval_async() -> float:
    """GEN async gate sharing the sync cross-process mutex and state."""
    import random as _rand

    return await _process_interval_wait_async(
        _gen_lock_file,
        0.2 + _rand.uniform(0.01, 0.05),
        use_content_ts=True,
    )


async def create_async_session() -> aiohttp.ClientSession:
    """创建一个 aiohttp ClientSession（调用方负责关闭）。

    V9.3.2: 禁用系统代理，数据获取全部直连。
    """
    if not _HAS_AIOHTTP:
        raise RuntimeError("aiohttp 未安装，请先运行: pip install aiohttp")
    # V9.3.2: trust_env=False → 不读取系统代理环境变量，数据获取全部直连
    return aiohttp.ClientSession(headers={"User-Agent": UA}, trust_env=False)


async def _async_request_with_retry(
    session: aiohttp.ClientSession,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
    max_retries: int = 3,
    method: str = "GET",
) -> Optional[Union[Dict[str, Any], List[Any], str]]:
    """V17.0 S2: 兼容别名——统一走 _async_quick_request(其内部已按域名分流 EM/GEN)。

    历史: 原独立实现为东财专用(EM 锁+1.0-1.3s 间隔+封禁跳过); V17.0 将 EM 分流
    并入 _async_quick_request 后本函数仅作外部兼容保留, 语义等价。
    返回: parsed JSON dict 或 None（失败时）
    """
    return await _async_quick_request(
        session,
        url,
        params=params,
        headers=headers,
        timeout=timeout,
        max_retries=max_retries,
        method=method,
    )


@overload
async def _async_quick_request(
    session: aiohttp.ClientSession,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
    max_retries: int = 3,
    data: Optional[Union[Dict[str, Any], str, bytes]] = None,
    method: str = "GET",
    *,
    is_json: Literal[False],
    encoding: Optional[str] = None,
) -> Optional[str]: ...


@overload
async def _async_quick_request(
    session: aiohttp.ClientSession,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
    max_retries: int = 3,
    data: Optional[Union[Dict[str, Any], str, bytes]] = None,
    method: str = "GET",
    *,
    is_json: Literal[True] = True,
    encoding: Optional[str] = None,
) -> Optional[Union[Dict[str, Any], List[Any]]]: ...


@overload
async def _async_quick_request(
    session: aiohttp.ClientSession,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
    max_retries: int = 3,
    data: Optional[Union[Dict[str, Any], str, bytes]] = None,
    method: str = "GET",
    *,
    is_json: bool,
    encoding: Optional[str] = None,
) -> Optional[Union[Dict[str, Any], List[Any], str]]: ...


async def _async_quick_request(
    session: aiohttp.ClientSession,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
    max_retries: int = 3,
    data: Optional[Union[Dict[str, Any], str, bytes]] = None,
    method: str = "GET",
    is_json: bool = True,
    encoding: Optional[str] = None,
) -> Optional[Union[Dict[str, Any], List[Any], str]]:
    """异步版: 通用 HTTP 请求（腾讯/新浪/同花顺/巨潮等，Semaphore(3) + 统一间隔保护, EM 域自动分流）。

    V7.5.1修复: 在 async with 块内读取完数据再返回，避免 response 连接释放后读取失败。
    V11.5 新增: 熔断器模式 + 随机UA/Referer + 指数退避
    V17.0 S2: 按域名分流 EM/GEN——EM 域(原 _async_request_with_retry 语义): 封禁跳过 +
    EM 锁 + 全局及风险组跨进程时隙 + Referer 注入;
    GEN 域: 0.2s 间隔 + GEN 跨进程节奏。

    Args:
        max_retries: 总尝试次数（含首次请求）；传输异常和 HTTP 408/5xx 有界重试。
        is_json:  True (默认) → 解析为 JSON，返回 dict/list。False → 返回原始文本 str
        encoding: 文本模式下的解码方式（如 'gbk'），None 表示用 aiohttp 自动检测
    Returns:
        dict/list (is_json=True), str (is_json=False), 或 None（失败时）

    HTTP 403/429 立即失败；其它 HTTP 408/5xx 最多按 ``max_retries`` 总尝试次数退避重试。
    """
    if not _HAS_ASYNCIO or not _HAS_AIOHTTP:
        return None

    domain = urlparse(url).netloc
    # V16.2.6: 熔断器按风控面归一化（东财 push2 系共享）
    _ft_domain = _normalize_em_domain(domain)

    if _HAS_FAULT_TOLERANCE:
        try:
            cb = get_domain_circuit_breaker(_ft_domain)
            if cb.state == "open":
                _debug_log(f"Circuit breaker open for {domain}, skipping request")
                return None
        except Exception as _e:
            _debug_log(f"Async quick fault tolerance init error ({domain}): {_e}")

    _ensure_async_locks()
    # V17.0 S2: 按域名分流 EM/GEN——EM 域(原 _async_request_with_retry 语义):
    #   封禁跳过 + EM 锁 + 全局及风险组跨进程时隙;
    #   GEN 域: 0.2s 间隔 + GEN 跨进程节奏。
    is_em = "eastmoney.com" in domain
    import random as _rand
    import json as _json

    async def _wait_for_retry_slot() -> None:
        global _em_async_last_request, _gen_async_last_request

        now = time.time()
        if is_em:
            interval = max(1.0, float(EM_MIN_INTERVAL)) + _rand.uniform(0.10, 0.30)
            last_request = max(_em_async_last_request, _EM_LAST_CALL[0])
            if last_request > 0 and now - last_request < interval:
                await asyncio.sleep(interval - (now - last_request))
            _em_async_last_request = time.time()
            _EM_LAST_CALL[0] = time.time()
            await _em_wait_process_interval_async(domain)
        else:
            interval = 0.2 + _rand.uniform(0.01, 0.05)
            if _gen_async_last_request > 0 and now - _gen_async_last_request < interval:
                await asyncio.sleep(interval - (now - _gen_async_last_request))
            _gen_async_last_request = time.time()
            await _gen_wait_process_interval_async()

    if is_em:
        # V16.2.8: 封禁跳过期直接返回 None（参考仓库 PR#36：不浪费请求、不加重封禁）
        if _em_is_banned(_ft_domain):
            _RL_STATS["em_rate_limit_count"] = _RL_STATS.get("em_rate_limit_count", 0) + 1
            _debug_log(f"async quick_request: {_ft_domain} 封禁跳过中（20h 冷却），拒绝 {url[:80]}")
            return None

    request_lock = _em_async_lock if is_em else _gen_async_lock
    if request_lock is None:
        return None
    async with request_lock:
        now = time.time()
        if is_em:
            global _em_async_last_request  # noqa: PLW0603
            # 同步/异步共用东财全局间隔；跨进程风险组时隙另由同一调度器限制。
            interval = max(1.0, float(EM_MIN_INTERVAL)) + _rand.uniform(0.10, 0.30)
            _last = max(_em_async_last_request, _EM_LAST_CALL[0])
            if _last > 0 and now - _last < interval:
                await asyncio.sleep(interval - (now - _last))
            _em_async_last_request = time.time()
            _EM_LAST_CALL[0] = time.time()
        else:
            global _gen_async_last_request  # noqa: PLW0603
            interval = 0.2 + _rand.uniform(0.01, 0.05)
            if _gen_async_last_request > 0 and now - _gen_async_last_request < interval:
                await asyncio.sleep(interval - (now - _gen_async_last_request))
            _gen_async_last_request = time.time()

        if is_em:
            await _em_wait_process_interval_async(domain)
        else:
            await _gen_wait_process_interval_async()

        _req_headers = headers.copy() if headers else {}
        if not _req_headers.get("User-Agent"):
            if _HAS_FAULT_TOLERANCE:
                _req_headers["User-Agent"] = get_random_ua()
            else:
                _req_headers["User-Agent"] = UA
        if is_em and not _req_headers.get("Referer"):
            # V17.0 S2: 继承原 _async_request_with_retry 的 EM 域 Referer 注入
            if _HAS_FAULT_TOLERANCE:
                _req_headers["Referer"] = get_random_referer()

        # M8 修复：异步通道原从不更新熔断器(成功/失败都不调 _on_success/_on_failure)，
        # 且 403 不计入封禁机制 → EM 异步路径完全绕过熔断/20h 封禁。现对齐同步 em_get：
        #   成功 → _on_success；失败 → _on_failure；403 → 计入 _EM_BAN_STREAK(达阈值触发 20h 跳过)。
        _cb = None
        if _HAS_FAULT_TOLERANCE:
            try:
                _cb = get_domain_circuit_breaker(_ft_domain)
            except Exception as _e:
                _debug_log(f"Async quick cb init error ({domain}): {_e}")
                _cb = None

        _result: Optional[Union[Dict[str, Any], List[Any], str]] = None
        _got_403 = False
        _got_429 = False
        for attempt in range(max_retries):
            try:
                timeout_obj = aiohttp.ClientTimeout(total=timeout)
                if method == "POST":
                    async with session.post(
                        url, data=data, params=params, headers=_req_headers, timeout=timeout_obj
                    ) as response:
                        if response.status == 200:
                            if is_json:
                                payload = await response.json(content_type=None)
                                _result = payload if isinstance(payload, (dict, list)) else None
                            else:
                                _result = await response.text(encoding=encoding)
                            break
                        if response.status == 403:
                            _got_403 = True
                            break
                        if response.status == 429:
                            _got_429 = True
                            break
                        if (
                            response.status == 408 or 500 <= response.status < 600
                        ) and attempt < max_retries - 1:
                            wait_s = exponential_backoff(attempt, base=1.0, max_wait=30.0)
                            await asyncio.sleep(wait_s)
                            await _wait_for_retry_slot()
                            continue
                        break
                else:
                    async with session.get(
                        url, params=params, headers=_req_headers, timeout=timeout_obj
                    ) as response:
                        if response.status == 200:
                            if is_json:
                                payload = await response.json(content_type=None)
                                _result = payload if isinstance(payload, (dict, list)) else None
                            else:
                                _result = await response.text(encoding=encoding)
                            break
                        if response.status == 403:
                            _got_403 = True
                            break
                        if response.status == 429:
                            _got_429 = True
                            break
                        if (
                            response.status == 408 or 500 <= response.status < 600
                        ) and attempt < max_retries - 1:
                            wait_s = exponential_backoff(attempt, base=1.0, max_wait=30.0)
                            await asyncio.sleep(wait_s)
                            await _wait_for_retry_slot()
                            continue
                        break
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError, _json.JSONDecodeError):
                if attempt < max_retries - 1:
                    if _HAS_FAULT_TOLERANCE:
                        wait_s = exponential_backoff(attempt)
                    else:
                        wait_s = 1.0 * (attempt + 1)
                    await asyncio.sleep(wait_s)
                    await _wait_for_retry_slot()
                    continue
                break

        if _got_403 and is_em:
            _RL_STATS["em_403_count"] = _RL_STATS.get("em_403_count", 0) + 1
            _consecutive_403 = _record_em_403(domain)
            if _consecutive_403 >= 3:
                _debug_log(
                    f"Async quick stopped Eastmoney risk group {_ft_domain} "
                    f"after {_consecutive_403} consecutive 403 responses"
                )
        elif _got_429 and is_em:
            _RL_STATS["em_429_count"] = _RL_STATS.get("em_429_count", 0) + 1
            _reset_em_403(domain)
        elif _result is not None and is_em:
            _reset_em_403(domain)

        if _cb is not None:
            try:
                if _result is not None:
                    _cb._on_success()
                else:
                    _cb._on_failure()
            except Exception as _e:
                _debug_log(f"Async quick cb update error ({domain}): {_e}")

        return _result

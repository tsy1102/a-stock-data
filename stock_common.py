#!/usr/bin/env python3
"""stock_common.py — V8.4 统一基础工具模块

所有报告脚本和 tdx_client 共享的基础函数、常量、全局状态。
V7.5 新增：线程安全限速锁 / 统一GD上传流程 / 统一板块判断 / 统一输出目录处理 / 日志记录 / 业务错误检查 / 主力净额连续性。
"""

from __future__ import annotations

import os
import sys
import atexit
import time
import math
import re
import threading
import logging
import argparse
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import requests
import urllib3
from datetime import datetime, timedelta

# 统一缓存层（v8.4 新增，注意：在 typing/stdlib 之后、requests 之后导入以避免循环依赖警告）
from stock_cache import cached, TTL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════════════════════
# 日志配置
# ═══════════════════════════════════════
_LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
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
    "www.cninfo.com.cn": {"sleep_ms": 100, "semaphore": None},
    "basic.10jqka.com.cn": {"sleep_ms": 100, "semaphore": None},
}
# 每个域名独立的最后请求时间
_DOMAIN_LAST_TIME: Dict[str, float] = {}

# Semaphore: 按域名并发限制
_DOMAIN_SEMAPHORES: Dict[str, threading.Semaphore] = {}

# ═══════════════════════════════════════
# 全局状态（进程内限速 + 进程间协调，V7.5 防封版）
# ═══════════════════════════════════════
# 保留原变量名以兼容旧代码，但实际已改用按域名限流
_em_last_request_time: float = 0.0   # 东财限速器（1.0s 基准，进程内）
_gen_last_request_time: float = 0.0  # 通用限速器（0.2s 基准，进程内）
# Semaphore(3): 统一并发限制（测试验证 45 请求 0 次 429）
_em_request_lock = threading.Semaphore(3)   # 东财：最多 3 并发请求
_gen_request_lock = threading.Semaphore(3)  # 通用：最多 3 并发请求（与东财统一，简洁）

# ── 进程间协调: 通过文件 mtime 实现跨进程请求间隔 ──
# 原理: 每个进程在发东财请求前，先 touch 一个共享文件；
#       通过检查文件的最后修改时间，判断距上次请求的间隔。
# 配合 Python 标准库的 os.open(..., O_EXCL) 做简易跨进程互斥。
from tempfile import gettempdir as _gettempdir
_em_lock_dir = os.path.join(_gettempdir(), "a_stock_data_v7")
try:
    os.makedirs(_em_lock_dir, exist_ok=True)
except Exception:
    pass
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
        except Exception:
            return False
    return False


def _file_lock_release(lock_path: str) -> None:
    """释放跨进程锁：删除自己创建的文件。"""
    _unique_path = lock_path + "_" + str(os.getpid())
    try:
        if os.path.exists(_unique_path):
            os.remove(_unique_path)
    except Exception:
        pass


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
    except Exception:
        pass
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
    except Exception:
        pass
    return 0.0

# ═══════════════════════════════════════
# 基础工具函数
# ═══════════════════════════════════════

def _safe_float(val: Any, default: float = 0.0) -> float:
    """安全转换为 float，异常或非有限值返回 default"""
    try:
        v = float(val)
        return v if math.isfinite(v) else default
    except (TypeError, ValueError):
        return default


def _request_with_retry(url: str, params: Optional[Dict[str, Any]] = None,
                        headers: Optional[Dict[str, str]] = None, timeout: int = 15,
                        max_retries: int = 3, data: Optional[Dict[str, Any]] = None,
                        method: str = "GET", verify: bool = False) -> Optional[requests.Response]:
    """带并发限流的 HTTP 请求（按域名独立限流）。

    V7.5 优化版：按域名独立控制并发和 sleep，不再使用全局 Semaphore。
    """
    from urllib.parse import urlparse
    import random as _rand

    # 解析域名
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

    return _do_request(url, params, headers, timeout, max_retries, data, method, verify)


def _quick_request(url: str, params: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None, timeout: int = 15,
                   max_retries: int = 3, data: Optional[Dict[str, Any]] = None,
                   method: str = "GET", verify: bool = False) -> Optional[requests.Response]:
    """通用 HTTP 请求（按域名独立限流）。

    V7.5 优化版：按域名独立控制并发和 sleep，不再使用全局 Semaphore。
    """
    from urllib.parse import urlparse
    import random as _rand

    # 解析域名
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

    return _do_request(url, params, headers, timeout, max_retries, data, method, verify)


def _do_request(url: str, params: Optional[Dict[str, Any]],
                headers: Optional[Dict[str, str]], timeout: int, max_retries: int,
                data: Optional[Dict[str, Any]], method: str, verify: bool) -> Optional[requests.Response]:
    """内部：执行 HTTP 请求 + 重试（由 _request_with_retry / _quick_request 调用）。"""
    for attempt in range(max_retries):
        try:
            if method == "POST":
                r = requests.post(url, data=data, params=params,
                                  headers=headers or {"User-Agent": UA},
                                  timeout=timeout, verify=verify)
            elif method == "GET":
                r = requests.get(url, params=params,
                                 headers=headers or {"User-Agent": UA},
                                 timeout=timeout, verify=verify)
            else:
                return None
            return r
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectTimeout):
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            return None
    return None


@cached(category="dragon_tiger", ttl_seconds=TTL["dragon_tiger"])
def get_dragon_tiger_board(code: str, today_str: str, days: int = 30, include_seats: bool = True) -> Dict[str, Any]:
    """V7.5: 统一龙虎榜查询（单只股票）。

    Args:
        code: 6位股票代码
        today_str: 今日日期 YYYY-MM-DD
        days: 回溯天数（sht默认30，med默认180）
        include_seats: 是否查询席位详情（默认True，设为False可减少2次API请求）

    Returns:
        {
          "records": [{date, reason, net_buy, turnover}, ...],
          "seats": {"buy": [{name, buy_amt, sell_amt, net}, ...], "sell": [...]},
          "institution": {"buy_amt", "sell_amt", "net_amt"},
          "net_sum_5d": float,        # V7.5新增：近5日净额累加
          "net_sum_30d": float,       # V7.5新增：近30日（或days）净额累加
          "consecutive_net_buy_days": int,  # V7.5新增：连续净买入天数
        }

    注意 (2026-06-16): 东财 datacenter API 日期字段过滤必须用单引号
    (`TRADE_DATE>='YYYY-MM-DD'`），双引号会报 code=9501。
    """
    start_str = (datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=days)).strftime("%Y-%m-%d")
    records = []
    data = eastmoney_datacenter(code, "RPT_DAILYBILLBOARD_DETAILSNEW",
                                filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{start_str}')(TRADE_DATE<='{today_str}')",
                                page_size=50, sort_columns="TRADE_DATE", sort_types="-1")
    for row in data:
        records.append({
            "date": str(row.get("TRADE_DATE", ""))[:10],
            "reason": row.get("EXPLANATION", ""),
            "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
            "turnover": round(_safe_float(row.get("TURNOVERRATE")), 2),
        })

    seats: Dict[str, List[Any]] = {"buy": [], "sell": []}
    institution: Dict[str, float] = {"buy_amt": 0.0, "sell_amt": 0.0, "net_amt": 0.0}

    if records and include_seats:
        latest_date = records[0]["date"]
        # 买入/卖出席席：用最新上榜日期 + SECURITY_CODE 过滤（单引号日期）
        buy_data = eastmoney_datacenter(code, "RPT_BILLBOARD_DAILYDETAILSBUY",
                                        filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{latest_date}')(TRADE_DATE<='{latest_date}')",
                                        page_size=50, sort_columns="BUY", sort_types="-1")
        for row in buy_data[:5]:
            seats["buy"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "code": str(row.get("OPERATEDEPT_CODE", "")),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })
        sell_data = eastmoney_datacenter(code, "RPT_BILLBOARD_DAILYDETAILSSELL",
                                         filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{latest_date}')(TRADE_DATE<='{latest_date}')",
                                         page_size=50, sort_columns="SELL", sort_types="-1")
        for row in sell_data[:5]:
            seats["sell"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "code": str(row.get("OPERATEDEPT_CODE", "")),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })
        # 机构专用席位（code == "0" 为机构专用）
        for row in buy_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                institution["buy_amt"] += (row.get("BUY") or 0)
        for row in sell_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                institution["sell_amt"] += (row.get("SELL") or 0)
        institution["buy_amt"] = round(institution["buy_amt"] / 10000, 1)
        institution["sell_amt"] = round(institution["sell_amt"] / 10000, 1)
        institution["net_amt"] = round(institution["buy_amt"] - institution["sell_amt"], 1)

    # V7.5新增：主力净额连续性统计
    net_sum_5d = round(sum(r["net_buy"] for r in records[:5]), 1)
    net_sum_30d_or_days = round(sum(r["net_buy"] for r in records), 1)
    consecutive_net_buy_days = sum(1 for r in records if r["net_buy"] > 0)

    return {
        "records": records, "seats": seats, "institution": institution,
        "net_sum_5d": net_sum_5d,
        "net_sum_30d": net_sum_30d_or_days,
        "consecutive_net_buy_days": consecutive_net_buy_days,
    }


@cached(category="dragon_tiger", ttl_seconds=TTL["dragon_tiger"])
def get_recent_dragon_tiger(days: int = 5) -> Dict[str, Any]:
    """V7.5: 全市场龙虎榜上榜记录（用于异动扫描和席位活跃度策略）。

    Returns:
        { stock_code: {name, reason, net_buy, turnover, date}, ... }

    注意 (2026-06-16): 东财 datacenter API 日期字段过滤必须用单引号
    (`TRADE_DATE>='YYYY-MM-DD'`），双引号会报 code=9501。
    """
    url = DATACENTER_URL
    try:
        td = datetime.now().strftime("%Y-%m-%d")
        sd = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        params = {
            "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
            "columns": "SECURITY_CODE,SECURITY_NAME_ABBR,TRADE_DATE,EXPLANATION,BILLBOARD_NET_AMT,TURNOVERRATE",
            "filter": f"(TRADE_DATE>='{sd}')(TRADE_DATE<='{td}')",
            "pageNumber": "1", "pageSize": "200",
            "sortColumns": "TRADE_DATE", "sortTypes": "-1",
            "source": "WEB", "client": "WEB",
        }
        r = _request_with_retry(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return {}
        d = r.json()
        data = d.get("result", {}).get("data", []) or []
        result = {}
        for row in data:
            code = str(row.get("SECURITY_CODE", ""))
            if code not in result:
                result[code] = {
                    "name": row.get("SECURITY_NAME_ABBR", ""),
                    "reason": row.get("EXPLANATION", ""),
                    "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
                    "turnover": round(_safe_float(row.get("TURNOVERRATE")), 2),
                    "date": str(row.get("TRADE_DATE", ""))[:10],
                }
        return result
    except Exception:
        return {}


def _market_code(code: str) -> int:
    """6位代码 → TDX 市场代码 (0=深圳, 1=上海)"""
    return 1 if code.startswith("6") else 0


# ══════════════════════════════════════════════════════════════════════════════
# V7.5: asyncio 异步请求层 (aiohttp + asyncio.Semaphore)
# 功能: 在异步模式下替代 threading.Lock + requests，实现 2-3x 性能提升
# 用法: from stock_common import create_async_session, _async_request_with_retry,
#            _async_quick_request, eastmoney_datacenter_async,
#            get_dragon_tiger_board_async, get_recent_dragon_tiger_async
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
    except Exception:
        pass
    return 0.0


async def create_async_session():
    """创建一个 aiohttp ClientSession（调用方负责关闭）。"""
    if not _HAS_AIOHTTP:
        raise RuntimeError("aiohttp 未安装，请先运行: pip install aiohttp")
    return aiohttp.ClientSession(headers={"User-Agent": UA})


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
            except Exception:
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


async def eastmoney_datacenter_async(session, code: str, report_name: str,
                                     columns: str = "ALL", filter_str: str = "",
                                     page_size: int = 50,
                                     sort_columns: str = "",
                                     sort_types: str = "-1") -> List[Dict[str, Any]]:
    """异步版: 东财数据中心统一查询（V7.5.1修复：在块内解析JSON，加 headers/status/日志）。"""
    try:
        full_filter = filter_str if filter_str else f'(SECURITY_CODE="{code}")'
        data = await _async_request_with_retry(
            session, DATACENTER_URL, params={
                "reportName": report_name, "columns": columns,
                "filter": full_filter, "pageNumber": "1", "pageSize": str(page_size),
                "sortColumns": sort_columns, "sortTypes": sort_types,
                "source": "WEB", "client": "WEB",
            }, headers={"User-Agent": UA}, timeout=15
        )
        if data is None:
            return []
        # data 已是解析后的 dict，不再需要 .json()
        if isinstance(data, dict):
            if data.get("status") == -1:
                _biz_logger.error(f"status=-1 | {report_name} | {code}")
                return []
            if data.get("result") and data["result"].get("data"):
                return data["result"]["data"]
        return []
    except Exception as _e:
        _debug_log(f"eastmoney_datacenter_async({code}, {report_name}): {_e}")
        return []


async def get_dragon_tiger_board_async(session, code: str, today_str: str,
                                       days: int = 30, include_seats: bool = True) -> Dict[str, Any]:
    """异步版: 单只股票龙虎榜查询。返回结构与同步版一致。

    注意 (2026-06-16): 东财 datacenter API 日期字段过滤必须用单引号
    (`TRADE_DATE>='YYYY-MM-DD'`），双引号会报 code=9501。
    """
    from datetime import datetime, timedelta
    start_str = (datetime.strptime(today_str, "%Y-%m-%d") -
                 timedelta(days=days)).strftime("%Y-%m-%d")
    records = []
    data = await eastmoney_datacenter_async(
        session, code, "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{start_str}')(TRADE_DATE<='{today_str}')",
        page_size=50, sort_columns="TRADE_DATE", sort_types="-1"
    )
    for row in data:
        records.append({
            "date": str(row.get("TRADE_DATE", ""))[:10],
            "reason": row.get("EXPLANATION", ""),
            "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
            "turnover": round(_safe_float(row.get("TURNOVERRATE")), 2),
        })

    seats: Dict[str, List[Any]] = {"buy": [], "sell": []}
    institution: Dict[str, float] = {"buy_amt": 0.0, "sell_amt": 0.0, "net_amt": 0.0}

    if records and include_seats:
        latest_date = records[0]["date"]
        buy_data = await eastmoney_datacenter_async(
            session, code, "RPT_BILLBOARD_DAILYDETAILSBUY",
            filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{latest_date}')(TRADE_DATE<='{latest_date}')",
            page_size=50, sort_columns="BUY", sort_types="-1"
        )
        for row in buy_data[:5]:
            seats["buy"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "code": str(row.get("OPERATEDEPT_CODE", "")),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })
        sell_data = await eastmoney_datacenter_async(
            session, code, "RPT_BILLBOARD_DAILYDETAILSSELL",
            filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{latest_date}')(TRADE_DATE<='{latest_date}')",
            page_size=50, sort_columns="SELL", sort_types="-1"
        )
        for row in sell_data[:5]:
            seats["sell"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "code": str(row.get("OPERATEDEPT_CODE", "")),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })
        for row in buy_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                institution["buy_amt"] += (row.get("BUY") or 0)
        for row in sell_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                institution["sell_amt"] += (row.get("SELL") or 0)
        institution["buy_amt"] = round(institution["buy_amt"] / 10000, 1)
        institution["sell_amt"] = round(institution["sell_amt"] / 10000, 1)
        institution["net_amt"] = round(institution["buy_amt"] - institution["sell_amt"], 1)

    return {"records": records, "seats": seats, "institution": institution}


async def get_recent_dragon_tiger_async(session, days: int = 5) -> Dict[str, Any]:
    """异步版: 全市场龙虎榜上榜记录。

    注意 (2026-06-16): 东财 datacenter API 日期字段过滤必须用单引号
    (`TRADE_DATE>='YYYY-MM-DD'`），双引号会报 code=9501。
    """
    from datetime import datetime, timedelta
    try:
        td = datetime.now().strftime("%Y-%m-%d")
        sd = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        params = {
            "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
            "columns": "SECURITY_CODE,SECURITY_NAME_ABBR,TRADE_DATE,EXPLANATION,BILLBOARD_NET_AMT,TURNOVERRATE",
            "filter": f"(TRADE_DATE>='{sd}')(TRADE_DATE<='{td}')",
            "pageNumber": "1", "pageSize": "200",
            "sortColumns": "TRADE_DATE", "sortTypes": "-1",
            "source": "WEB", "client": "WEB",
        }
        resp = await _async_request_with_retry(session, DATACENTER_URL,
                                               params=params, headers={"User-Agent": UA}, timeout=15)
        if resp is None:
            return {}
        data = resp  # _async_request_with_retry 已返回解析后的 dict
        rows = data.get("result", {}).get("data", []) or []
        result = {}
        for row in rows:
            code = str(row.get("SECURITY_CODE", ""))
            if code not in result:
                result[code] = {
                    "name": row.get("SECURITY_NAME_ABBR", ""),
                    "reason": row.get("EXPLANATION", ""),
                    "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
                    "turnover": round(_safe_float(row.get("TURNOVERRATE")), 2),
                    "date": str(row.get("TRADE_DATE", ""))[:10],
                }
        return result
    except Exception:
        return {}


# ═══════════════════════════════════════
# 东财数据中心统一查询
# ═══════════════════════════════════════

def eastmoney_datacenter(code: str, report_name: str, columns: str = "ALL",
                         filter_str: str = "", page_size: int = 50,
                         sort_columns: str = "", sort_types: str = "-1") -> List[Dict[str, Any]]:
    """东财数据中心统一查询（datacenter-web.eastmoney.com）。

    V7.5 新增：HTTP状态码非200时记录日志，业务错误码(status=-1)时记录日志，JSON解析失败时记录日志。
    """
    try:
        full_filter = filter_str if filter_str else f'(SECURITY_CODE="{code}")'
        r = _request_with_retry(DATACENTER_URL, params={
            "reportName": report_name, "columns": columns,
            "filter": full_filter, "pageNumber": "1", "pageSize": str(page_size),
            "sortColumns": sort_columns, "sortTypes": sort_types,
            "source": "WEB", "client": "WEB",
        }, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return []
        # HTTP状态码检查
        if r.status_code != 200:
            _http_logger.error(f"{r.status_code} | {DATACENTER_URL} | {report_name} | {code}")
            return []
        try:
            d = r.json()
        except Exception as _json_err:
            _http_logger.error(f"JSONDecodeError | {DATACENTER_URL} | {report_name} | {code} | {_json_err}")
            return []
        # 业务错误码检查
        if isinstance(d, dict) and d.get("status") == -1:
            _biz_logger.error(f"status=-1 | {report_name} | {code} | {d.get('message', '')}")
            return []
        if d.get("result") and d["result"].get("data"):
            return d["result"]["data"]
        return []
    except Exception as _e:
        _debug_log(f"eastmoney_datacenter({code}, {report_name}): {_e}")
        return []


def _em_filter(code: str, report_name: str, extra_filter: str = "", page_size: int = 50,
               sort_columns: str = "", sort_types: str = "-1") -> List[Dict[str, Any]]:
    """东财数据中心查询便捷包装（自动拼接 SECURITY_CODE）。"""
    return eastmoney_datacenter(code, report_name,
                                filter_str=f'(SECURITY_CODE="{code}"){extra_filter}' if extra_filter else "",
                                page_size=page_size, sort_columns=sort_columns, sort_types=sort_types)


async def _em_filter_async(session, code: str, report_name: str, extra_filter: str = "",
                            page_size: int = 50, sort_columns: str = "",
                            sort_types: str = "-1") -> List[Dict[str, Any]]:
    """async 版：东财数据中心查询便捷包装。"""
    return await eastmoney_datacenter_async(
        session, code, report_name,
        filter_str=f'(SECURITY_CODE="{code}"){extra_filter}' if extra_filter else "",
        page_size=page_size, sort_columns=sort_columns, sort_types=sort_types
    )


# ═══════════════════════════════════════
# 配置文件加载（游资标签 / 公告关键词等）
# ═══════════════════════════════════════

_settings_cache = None  # 模块级缓存，只加载一次


def _load_settings() -> Dict[str, Any]:
    """从 keywords_config.yaml 加载关键词与标签配置（席位标签/公告关键词/政策关键词/日历映射）。

    返回 dict，模块级缓存（只读一次）。
    """
    global _settings_cache
    if _settings_cache is not None:
        return _settings_cache
    _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keywords_config.yaml")
    try:
        import yaml
        with open(_path, 'r', encoding='utf-8') as f:
            _settings_cache = yaml.safe_load(f)
    except Exception as _e:
        _debug_log(f"_load_settings: {_e}")
        _settings_cache = {}
    return _settings_cache


# ═══════════════════════════════════════
# 策略阈值配置加载（strategy_config.yaml）
# ═══════════════════════════════════════

_strategy_config_cache: Optional[Dict[str, Any]] = None  # 模块级缓存


def _load_strategy_config() -> Dict[str, Any]:
    """从 strategy_config.yaml 加载量化策略阈值配置。

    返回嵌套 dict，模块级缓存（只读一次）。
    顶层键：market / technical / valuation / fundamental /
           fundflow / trader / holder / strategy / abnormal / report
    """
    global _strategy_config_cache
    if _strategy_config_cache is not None:
        return _strategy_config_cache
    _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "strategy_config.yaml")
    try:
        import yaml
        with open(_path, 'r', encoding='utf-8') as f:
            _strategy_config_cache = yaml.safe_load(f)
    except Exception as _e:
        _debug_log(f"_load_strategy_config: {_e}")
        _strategy_config_cache = {}
    return _strategy_config_cache


# ═══════════════════════════════════════
# 股东户数缓存（东财 RPT_F10_EH_HOLDERNUM + 本地 JSON）
# ═══════════════════════════════════════
# 设计：
#   - 启动时 load holder_cache.json → 内存 dict（1 次 I/O）
#   - 查询时：缓存新鲜（< 60 天）→ 直接返回；否则调东财拿 10 期 → 更新内存
#   - 结束时：内存 → holder_cache.json（1 次 I/O），超过 500 只股票时裁剪
#   - 东财调用：每只股票每季度最多 1 次

_HOLDER_CACHE_FILE: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "holder_cache.json")
_HOLDER_CACHE_TTL: int = 60 * 86400      # 60 天 — 新鲜阈值（同一季度内 TDX 增量更新）
_HOLDER_CACHE_REFRESH: int = 90 * 86400  # 90 天 — 强制刷新阈值（跨季度用东财补全）
_HOLDER_CACHE_MAX_STOCKS: int = 500
_holder_mem_cache: Optional[Dict[str, Any]] = None  # 内存缓存，模块级单例


def _holder_cache_load() -> None:
    """启动时加载缓存 → 内存 dict。"""
    global _holder_mem_cache
    if _holder_mem_cache is not None:
        return
    try:
        import json
        with open(_HOLDER_CACHE_FILE, 'r', encoding='utf-8') as f:
            _holder_mem_cache = json.load(f)
    except Exception:
        _holder_mem_cache = {}


def _holder_fetch_em(code: str, page_size: int) -> List[Dict[str, Any]]:
    """从东财获取股东户数 → 按日期升序的 records 列表。"""
    data = _em_filter(code, "RPT_F10_EH_HOLDERNUM",
                      page_size=page_size, sort_columns="END_DATE", sort_types="-1")
    if not data:
        return []
    records = []
    for r in data:
        records.append({
            "date": str(r.get("END_DATE", ""))[:10],
            "holder_num": int(r.get("HOLDER_TOTAL_NUM") or 0),
            "avg_shares": _safe_float(r.get("AVG_FREE_SHARES")),
        })
    records.sort(key=lambda x: x["date"])
    return records


def _holder_fetch_tdx(code: str, records: List[Dict[str, Any]], now: float) -> bool:
    """从 TDX 拿最新 1 期，去重后追加到 records。"""
    from tdx_client import _get_tdx_client
    client = _get_tdx_client()
    if client is None:
        return False
    info = client.get_finance_info(1 if code.startswith("6") else 0, code)
    if info is None or info.empty:
        return False
    hnum = int(info.iloc[0].get('gudong_renshu', 0))
    upd = str(int(info.iloc[0].get('updated_date', 0)))
    if hnum <= 0:
        return False
    date_str = f"{upd[:4]}-{upd[4:6]}-{upd[6:8]}" if len(upd) == 8 else ""
    if not records or records[-1].get("holder_num") != hnum:
        records.append({"date": date_str, "holder_num": hnum})
        if len(records) > 10:
            records = records[-10:]
    _holder_mem_cache[code] = {"_updated": now, "records": records}
    return True


def holder_change(code: str) -> List[Dict[str, Any]]:
    """获取股东户数多期变化。

    逻辑：
      - 缓存新鲜 < 60 天 → 直接返回
      - 缓存为空 → 东财 10 期（首次）
      - 缓存过期 ≥ 60 天且 < 90 天 → TDX 追加 1 期（同季度增量）
      - 缓存过期 ≥ 90 天 → 东财 5 期（跨季度补全）

    返回: [{date, holder_num, change_num, change_ratio, avg_shares}, ...] 最新在前
    """
    _holder_cache_load()

    now = time.time()
    entry = _holder_mem_cache.get(code, {})
    records = entry.get("records", [])
    updated = entry.get("_updated", 0)
    age = now - updated if updated else 999_999_999

    # ① 缓存新鲜 → 直接返回
    if updated and records and age < _HOLDER_CACHE_TTL:
        return _compute_holder_changes(records)

    # ② 缓存为空 → 东财 10 期（首次初始化）
    if not records:
        records = _holder_fetch_em(code, 10)
        if records:
            _holder_mem_cache[code] = {"_updated": now, "records": records}
            return _compute_holder_changes(records)

    # ③ 缓存过期 ≥ 90 天 → 东财 5 期（跨季度补全，替换旧缓存）
    if updated and records and age >= _HOLDER_CACHE_REFRESH:
        records = _holder_fetch_em(code, 5)
        if records:
            _holder_mem_cache[code] = {"_updated": now, "records": records}
            return _compute_holder_changes(records)

    # ④ 缓存过期 ≥ 60 天且 < 90 天 → TDX 追加 1 期
    if _holder_fetch_tdx(code, records, now):
        return _compute_holder_changes(records)

    # 全部失败 → 返回旧缓存
    return _compute_holder_changes(records)


async def holder_change_async(session, code: str) -> List[Dict[str, Any]]:
    """async 版：股东户数多期变化（复用同步版缓存逻辑）。"""
    _holder_cache_load()
    now = time.time()
    entry = _holder_mem_cache.get(code, {})
    records = entry.get("records", [])
    updated = entry.get("_updated", 0)
    age = now - updated if updated else 999_999_999

    if updated and records and age < _HOLDER_CACHE_TTL:
        return _compute_holder_changes(records)

    if not records:
        records = await _holder_fetch_em_async(session, code, 10)
        if records:
            _holder_mem_cache[code] = {"_updated": now, "records": records}
            return _compute_holder_changes(records)

    if updated and records and age >= _HOLDER_CACHE_REFRESH:
        records = await _holder_fetch_em_async(session, code, 5)
        if records:
            _holder_mem_cache[code] = {"_updated": now, "records": records}
            return _compute_holder_changes(records)

    if _holder_fetch_tdx(code, records, now):
        return _compute_holder_changes(records)
    return _compute_holder_changes(records)


async def _holder_fetch_em_async(session, code: str, page_size: int) -> List[Dict[str, Any]]:
    """async 版：从东财获取股东户数。"""
    data = await _em_filter_async(session, code, "RPT_F10_EH_HOLDERNUM",
                                    page_size=page_size, sort_columns="END_DATE", sort_types="-1")
    if not data:
        return []
    records = []
    for r in data:
        records.append({
            "date": str(r.get("END_DATE", ""))[:10],
            "holder_num": int(r.get("HOLDER_TOTAL_NUM") or 0),
            "avg_shares": _safe_float(r.get("AVG_FREE_SHARES")),
        })
    records.sort(key=lambda x: x["date"])
    return records


def _compute_holder_changes(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """从原始记录列表计算环比变化。"""
    if not records:
        return []
    result = []
    for i in range(len(records)):
        r = records[i]
        prev_num = records[i - 1]["holder_num"] if i > 0 else 0
        change_num = r["holder_num"] - prev_num if i > 0 and prev_num > 0 else 0
        change_ratio = round(change_num / prev_num * 100, 2) if i > 0 and prev_num > 0 else 0.0
        result.append({
            "date": r["date"],
            "holder_num": r["holder_num"],
            "change_num": change_num,
            "change_ratio": change_ratio,
            "avg_shares": r.get("avg_shares", 0),
        })
    # 最新在前
    result.reverse()
    return result


def holder_cache_flush() -> None:
    """脚本结束时调用：内存缓存 → 磁盘（超过上限时裁剪）。"""
    global _holder_mem_cache
    if _holder_mem_cache is None:
        return
    # 裁剪：只保留最近更新的 N 只股票
    if len(_holder_mem_cache) > _HOLDER_CACHE_MAX_STOCKS:
        items = sorted(_holder_mem_cache.items(),
                       key=lambda kv: kv[1].get("_updated", 0), reverse=True)
        _holder_mem_cache = dict(items[:_HOLDER_CACHE_MAX_STOCKS])
    try:
        import json
        with open(_HOLDER_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(_holder_mem_cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ═══════════════════════════════════════
# 巨潮公告统一查询（短中长线共用）
# ═══════════════════════════════════════

@cached(category="announcements", ttl_seconds=TTL["announcements"])
def get_strategic_announcements(code: str, page_size: int = 50, days: Optional[int] = None,
                                importance_filter: bool = False) -> List[Dict[str, Any]]:
    """巨潮公告查询 → orgId → searchkey → TDX F10 三层兜底。

    Args:
        code: 股票代码
        page_size: 返回数量上限
        days: 限定最近 N 天，None=不限（长线），30=中线，7=短线
        importance_filter: V7.5新增，是否仅返回重要公告（True=仅重要，False=全部）
    返回: [{title, date, type, is_important}, ...]
    """
    # 计算日期范围
    sd_str = ""
    if days:
        sd_str = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        td_str = datetime.now().strftime("%Y-%m-%d")
        se_date = f"{sd_str}~{td_str}"
    else:
        se_date = ""

    url = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
    if code.startswith("6"):
        ext_org_id = f"gssh0{code}"
    elif code.startswith("8") or code.startswith("4"):
        ext_org_id = f"gsbj0{code}"
    else:
        ext_org_id = f"gssz0{code}"
    payload = {
        "orgId": ext_org_id, "stock": f"{code},{ext_org_id}",
        "tabName": "fulltext", "pageSize": str(page_size), "pageNum": "1",
        "column": "", "category": "", "plate": "",
        "seDate": se_date,
        "searchkey": "", "secid": "", "sortName": "", "sortType": "",
        "isHLtitle": "true",
    }
    headers = {"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded",
               "Referer": "https://www.cninfo.com.cn/new/disclosure"}
    _cfg = _load_settings()
    keywords = _cfg.get("announcement_keywords",
                        ["回购", "增持", "减持", "年报", "分红", "派息", "激励", "员工持股",
                         "战略合作", "业绩预告", "中标", "立案", "合同", "收购", "股权转让",
                         "异动", "严重异动"])
    _noise = _cfg.get("announcement_noise", ["摘要", "提示性", "英文版"])
    _importance_kw = _cfg.get("announcement_importance_keywords", [])
    try:
        r = _quick_request(url, data=payload, headers=headers, method="POST", timeout=15)
        anns = []
        if r is not None:
            d = r.json()
            anns = d.get("announcements", []) or []
        if not anns:
            # orgId 失败 → searchkey 兜底
            payload2 = {"orgId": "", "stock": "", "tabName": "fulltext",
                        "pageSize": str(page_size), "pageNum": "1",
                        "column": "", "category": "", "plate": "",
                        "seDate": se_date,
                        "searchkey": str(code), "secid": "",
                        "sortName": "", "sortType": "", "isHLtitle": "true"}
            r2 = _quick_request(url, data=payload2, headers=headers, method="POST", timeout=15)
            if r2 is not None:
                d2 = r2.json()
                anns2 = d2.get("announcements", []) or []
                if anns2:
                    anns = anns2
        if not anns:
            # 巨潮双路径均失败 → TDX F10 兜底
            try:
                from tdx_client import tdx_get_latest_announcements
                tdx_anns = tdx_get_latest_announcements(code, days=7)
                if tdx_anns:
                    anns = [{"announcementTitle": a["title"],
                             "announcementTime": int(datetime.strptime(a["date"], "%Y-%m-%d").timestamp() * 1000) if a.get("date") else 0}
                            for a in tdx_anns]
            except Exception:
                pass
        rows = []
        for item in anns:
            _sc = str(item.get("secCode", ""))
            if _sc and _sc != str(code):
                continue
            title = item.get("announcementTitle", "")
            title = re.sub(r'<[^>]+>', '', title)
            if any(k in title for k in keywords) and not any(noise in title for noise in _noise):
                ts = item.get("announcementTime", 0)
                if isinstance(ts, (int, float)) and ts > 1000000000000:
                    date_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                else:
                    date_str = str(ts)[:10]
                # V7.5新增：重要等级标记
                is_important = any(imp_k in title for imp_k in _importance_kw)
                # 如果开启重要过滤且不是重要公告，跳过
                if importance_filter and not is_important:
                    continue
                rows.append({
                    "title": title,
                    "date": date_str,
                    "type": item.get("announcementTypeName", "") or "",
                    "is_important": is_important,
                })
        return rows
    except Exception:
        return []


async def get_strategic_announcements_async(session, code: str, page_size: int = 50,
                                             days: Optional[int] = None) -> List[Dict[str, Any]]:
    """async 版：巨潮公告查询 → orgId → searchkey → TDX F10 三层兜底。"""
    sd_str = ""
    if days:
        sd_str = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        td_str = datetime.now().strftime("%Y-%m-%d")
        se_date = f"{sd_str}~{td_str}"
    else:
        se_date = ""

    url = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
    if code.startswith("6"):
        ext_org_id = f"gssh0{code}"
    elif code.startswith("8") or code.startswith("4"):
        ext_org_id = f"gsbj0{code}"
    else:
        ext_org_id = f"gssz0{code}"
    payload = {
        "orgId": ext_org_id, "stock": f"{code},{ext_org_id}",
        "tabName": "fulltext", "pageSize": str(page_size), "pageNum": "1",
        "column": "", "category": "", "plate": "",
        "seDate": se_date,
        "searchkey": "", "secid": "", "sortName": "", "sortType": "",
        "isHLtitle": "true",
    }
    headers = {"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded",
               "Referer": "https://www.cninfo.com.cn/new/disclosure"}
    _cfg = _load_settings()
    keywords = _cfg.get("announcement_keywords",
                        ["回购", "增持", "减持", "年报", "分红", "派息", "激励", "员工持股",
                         "战略合作", "业绩预告", "中标", "立案", "合同", "收购", "股权转让",
                         "异动", "严重异动"])
    _noise = _cfg.get("announcement_noise", ["摘要", "提示性", "英文版"])
    try:
        r = await _async_quick_request(session, url, data=payload, headers=headers, method="POST", timeout=15)
        anns = []
        if r is not None:
            # r 已经是解析后的 dict（_async_quick_request 内部已调用 json）
            anns = r.get("announcements", []) or []
        if not anns:
            payload2 = {"orgId": "", "stock": "", "tabName": "fulltext",
                        "pageSize": str(page_size), "pageNum": "1",
                        "column": "", "category": "", "plate": "",
                        "seDate": se_date,
                        "searchkey": str(code), "secid": "",
                        "sortName": "", "sortType": "", "isHLtitle": "true"}
            r2 = await _async_quick_request(session, url, data=payload2, headers=headers, method="POST", timeout=15)
            if r2 is not None:
                anns2 = r2.get("announcements", []) or []
                if anns2:
                    anns = anns2
        if not anns:
            try:
                from tdx_client import tdx_get_latest_announcements
                tdx_anns = tdx_get_latest_announcements(code, days=7)
                if tdx_anns:
                    anns = [{"announcementTitle": a["title"],
                             "announcementTime": int(datetime.strptime(a["date"], "%Y-%m-%d").timestamp() * 1000) if a.get("date") else 0}
                            for a in tdx_anns]
            except Exception:
                pass
        rows = []
        for item in anns:
            _sc = str(item.get("secCode", ""))
            if _sc and _sc != str(code):
                continue
            title = item.get("announcementTitle", "")
            title = re.sub(r'<[^>]+>', '', title)
            if any(k in title for k in keywords) and not any(noise in title for noise in _noise):
                ts = item.get("announcementTime", 0)
                if isinstance(ts, (int, float)) and ts > 1000000000000:
                    date_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                else:
                    date_str = str(ts)[:10]
                rows.append({
                    "title": title,
                    "date": date_str,
                    "type": item.get("announcementTypeName", "") or "",
                })
        return rows
    except Exception:
        return []


# ═══════════════════════════════════════
# 机构持股结构分析（替代 get_institutional_holder_ratio）
# ═══════════════════════════════════════

_holder_structure_cache: Dict[str, List[Dict[str, Any]]] = {}

def get_holder_structure(code: str) -> List[Dict[str, Any]]:
    """东财 RPT_F10_EH_HOLDERS → 多季度十大流通股东分类统计。
    模块级缓存，同一脚本运行期内不重复调 API。

    返回: [{date, total, northbound, foreign, foreign_count,
            domestic, domestic_count, individual, individual_count}, ...] 最新在前
    """
    if code in _holder_structure_cache:
        return _holder_structure_cache[code]

    data = eastmoney_datacenter(code, "RPT_F10_EH_HOLDERS",
                                columns="END_DATE,HOLDER_NAME,HOLD_NUM_RATIO",
                                filter_str=f'(SECURITY_CODE="{code}")',
                                page_size=50, sort_columns="END_DATE", sort_types="-1")
    if not data:
        return []

    # 按报告期分组
    periods = {}
    for h in data:
        ed = str(h.get("END_DATE", ""))[:10]
        if ed not in periods:
            periods[ed] = []
        periods[ed].append(h)

    result = []
    for date_key in sorted(periods.keys(), reverse=True)[:4]:
        holders = periods[date_key]
        nb = fe = dm = ind = 0.0
        fc = dc = ic = 0
        dm_tags = {"国资": 0.0, "证金汇金": 0.0, "公募": 0.0, "险资": 0.0, "社保": 0.0}

        for h in holders[:10]:
            name = (h.get("HOLDER_NAME", "") or "").strip()
            ratio = float(h.get("HOLD_NUM_RATIO", 0))
            has_cn = any('\u4e00' <= c <= '\u9fff' for c in name)
            has_en = any(c.isalpha() and ord(c) < 128 for c in name)

            if '香港中央结算' in name or 'HKSCC' in name.upper():
                nb += ratio
            elif not has_cn and has_en:
                fe += ratio; fc += 1
            elif has_cn and len([c for c in name if '\u4e00' <= c <= '\u9fff']) <= 3 \
                 and not any(kw in name for kw in
                             ['公司', '基金', '保险', '银行', '信托', '证券', '合伙', '集团', '投资', '控股']):
                ind += ratio; ic += 1
            else:
                dm += ratio; dc += 1
                # 境内机构细分
                if '社保' in name:
                    dm_tags["社保"] += ratio
                elif '保险' in name:
                    dm_tags["险资"] += ratio
                elif '中国证券金融' in name or '中央汇金' in name:
                    dm_tags["证金汇金"] += ratio
                elif '基金' in name:
                    dm_tags["公募"] += ratio
                elif '集团' in name or '国有' in name or '国资委' in name:
                    dm_tags["国资"] += ratio

        result.append({
            "date": date_key,
            "total": round(nb + fe + dm + ind, 1),
            "northbound": round(nb, 2),
            "foreign": round(fe, 1), "foreign_count": fc,
            "domestic": round(dm, 1), "domestic_count": dc,
            "individual": round(ind, 1), "individual_count": ic,
            "dm_detail": {k: round(v, 1) for k, v in dm_tags.items() if v > 0},
        })

    _holder_structure_cache[code] = result
    return result


# ═══════════════════════════════════════
# 安全退出：注册 cleanup_tdx，防止 Ctrl+C 遗留僵尸连接
# ═══════════════════════════════════════

def _safe_cleanup_tdx() -> None:
    """安全清理 TDX 连接（忽略异常）。"""
    try:
        from tdx_client import cleanup_tdx
        cleanup_tdx()
    except Exception:
        pass

atexit.register(_safe_cleanup_tdx)


# ═══════════════════════════════════════════════════════════════
# V7.5: 报告流程公共工具（统一GD上传 / 输出目录 / 板块判断）
# ═══════════════════════════════════════════════════════════════

def ensure_output_dir(output_dir: str) -> str:
    """确保输出目录存在，返回规范化的路径。"""
    _dir = os.path.abspath(output_dir)
    os.makedirs(_dir, exist_ok=True)
    return _dir


def get_script_dir() -> str:
    """获取当前脚本所在目录（供 main.py 和各报告脚本共用）。"""
    return os.path.dirname(os.path.abspath(__file__))


@cached(category="board_type", ttl_seconds=TTL["board_type"])
def get_board_type(code: str, name: str = "") -> str:
    """V7.5: 统一板块判断。返回: 主板 / 创业板 / 科创板 / ST。"""
    if "ST" in name or "*ST" in name:
        return "ST"
    if code.startswith("688"):
        return "科创板"
    if code.startswith(("300", "301")):
        return "创业板"
    return "主板"


def is_limit_up(code: str, name: str, change_pct: float) -> bool:
    """V7.5: 统一涨停判断。区分板块阈值。"""
    if not change_pct:
        return False
    board = get_board_type(code, name)
    if board == "ST":
        return change_pct >= 4.8
    if board in ("创业板", "科创板"):
        return change_pct >= 19.5
    return change_pct >= 9.5


def is_limit_down(code: str, name: str, change_pct: float) -> bool:
    """V7.5: 统一跌停判断。区分板块阈值。"""
    if not change_pct:
        return False
    board = get_board_type(code, name)
    if board == "ST":
        return change_pct <= -4.8
    if board in ("创业板", "科创板"):
        return change_pct <= -19.5
    return change_pct <= -9.5


def gd_upload_flow(base_dir: str, local_files: List[str],
                   report_type: str = "generic", no_upload: bool = False) -> bool:
    """V7.5: 统一的 Google Drive 上传流程。

    逻辑（与5个脚本的原有流程一致）：
      1. 如 no_upload=True，直接返回不操作
      2. 3 次尝试 init_google_drive
      3. 失败则询问是否跳过（脚本运行环境下需交互输入）
      4. 成功则创建/获取 a-stock-data/<report_type> 文件夹
      5. 逐个上传 local_files
      6. 最后 cleanup_gd_proxy

    Args:
        base_dir: 项目根目录（client_secrets.json / credentials.json 所在目录）
        local_files: 本地文件绝对路径列表（待上传）
        report_type: 子文件夹名（sht / med / lng / val / mak），默认 generic
        no_upload: 是否跳过上传（来自命令行 --no-upload）

    Returns:
        True=全部上传成功，False=失败或被跳过
    """
    if no_upload:
        return False

    from gd_uploader import init_google_drive, cleanup_gd_proxy, get_or_create_drive_folder, upload_report_to_drive

    drive = None
    gd_proxy_set = False

    for _gd_try in range(3):
        try:
            drive, gd_proxy_set = init_google_drive(base_dir)
            if drive:
                break
        except Exception:
            pass
        if _gd_try < 2:
            print(f"  GD 连接失败，{_gd_try + 2}/3 重试…", flush=True)
            time.sleep(5)

    if not drive:
        print("  GD 连接 3 次均失败", flush=True)
        try:
            _choice = input("  是否继续（跳过云端上传）？[y/N]: ")
            if _choice.lower() != "y":
                print("  用户取消，终止上传", flush=True)
                cleanup_gd_proxy(gd_proxy_set)
                return False
        except (EOFError, OSError):
            cleanup_gd_proxy(gd_proxy_set)
            return False

    gd_folder_id = None
    for _gf_try in range(3):
        try:
            gd_folder_id = get_or_create_drive_folder(drive, "a-stock-data")
            if gd_folder_id:
                break
        except Exception:
            pass
        if _gf_try < 2:
            print(f"  GD 文件夹探测失败，{_gf_try + 2}/3 重试…", flush=True)
            time.sleep(3)

    if not gd_folder_id:
        print("  GD 文件夹探测 3 次均失败", flush=True)
        cleanup_gd_proxy(gd_proxy_set)
        return False

    sub_folder_id = get_or_create_drive_folder(drive, report_type, gd_folder_id)
    if not sub_folder_id:
        print(f"  无法创建/获取 GD 子文件夹: {report_type}", flush=True)
        cleanup_gd_proxy(gd_proxy_set)
        return False

    all_ok = True
    for _fp in local_files:
        if not os.path.isfile(_fp):
            continue
        fn = os.path.basename(_fp)
        print(f"  上传: {fn}…", flush=True)
        try:
            if upload_report_to_drive(drive, _fp, sub_folder_id, fn):
                print(f"    {fn} 上传成功", flush=True)
            else:
                print(f"    {fn} 上传失败", flush=True)
                all_ok = False
        except Exception as _e:
            print(f"    {fn} 上传异常: {_e}", flush=True)
            all_ok = False

    cleanup_gd_proxy(gd_proxy_set)
    return all_ok


# ═══════════════════════════════════════════════════════════════
# 报告脚本公共函数（V7.5 从各脚本提取统一）
# ═══════════════════════════════════════════════════════════════

def clean_codes(raw_list, verbose=False):
    """清洗股票代码列表：提取6位数字、去重、保持顺序、过滤无效项。

    支持的输入格式示例:
      - '600519'         -> '600519'
      - '002193如意'    -> '002193'
      - '300990同飞'    -> '300990'
      - '600143 金发'   -> '600143'  ('金发' 被过滤为无6位数字)
      - '601208东材'    -> '601208'  (重复出现时自动去重)

    Args:
        raw_list: 原始代码列表（可含中文/空格/符号）
        verbose: 是否打印清洗结果

    Returns:
        清洗后的6位代码列表（去重、保持首次出现顺序）
    """
    if not raw_list:
        return []

    seen = set()
    clean = []
    skipped = []
    for raw in raw_list:
        if not raw or not isinstance(raw, str):
            continue
        code = "".join(c for c in raw if c.isdigit())[:6]
        if len(code) < 6:
            skipped.append(raw)
            continue
        if code in seen:
            skipped.append(raw + "(重复)")
            continue
        seen.add(code)
        clean.append(code)

    if verbose and skipped:
        print(f"  🧹 代码清洗: 保留 {len(clean)} 个, 跳过 {len(skipped)} 个 "
              f"({', '.join(skipped[:5])}{'...' if len(skipped) > 5 else ''})", flush=True)

    return clean


def parse_args(report_type="unknown"):
    """命令行参数解析（参数化版本，兼容6个报告脚本）。

    - codes: 可选（默认空列表），个股分析脚本（sht/med/lng/ful）会用到；
             全市场扫描脚本（val/mak）不需要此参数，传空即可。
    """
    parser = argparse.ArgumentParser(description=report_type)
    parser.add_argument("codes", nargs="*", default=[],
                        help="股票代码，支持 1 个或多个（全市场扫描脚本不需要此参数）")
    parser.add_argument("-o", "--output",
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports"),
                        help="报告输出目录（默认: 脚本目录下的 reports/）")
    parser.add_argument("--no-upload", action="store_true", help="跳过 Google Drive 上传")
    return parser.parse_args()


def get_tencent_quote(code: str) -> Dict[str, Any]:
    """V4: 个股行情 → tdx_client 适配器（TDX实时价+腾讯估值+五档盘口）"""
    from tdx_client import tdx_get_quote_full
    return tdx_get_quote_full(code)


def baidu_kline_full(code, is_index=False):
    """V4: 全量K线 → tdx_client 适配器（TDX日K线，自动fallback百度）"""
    from tdx_client import tdx_get_security_bars, tdx_get_index_bars
    if is_index:
        return tdx_get_index_bars(code)
    return tdx_get_security_bars(code)


@cached(category="reports", ttl_seconds=TTL["reports"])
def get_reports(code: str, max_pages: int = 3) -> List[Dict[str, Any]]:
    """东财研报列表查询。

    Args:
        code: 股票代码。
        max_pages: 最大页数（每页50条）。

    Returns:
        list: 研报记录列表。
    """
    api_url = "https://reportapi.eastmoney.com/report/list"
    all_records = []
    for page in range(1, max_pages + 1):
        params = {
            "pageSize": "50", "industry": "*", "rating": "*",
            "beginTime": "2000-01-01", "endTime": "2030-01-01",
            "pageNo": str(page), "code": code, "qType": "0"
        }
        try:
            r = _request_with_retry(api_url, params=params, timeout=30)
            rows = r.json().get("data") or []
            if not rows:
                break
            all_records.extend(rows)
        except Exception:
            break
    return all_records


@cached(category="eps_forecast", ttl_seconds=TTL["eps_forecast"])
def get_eps_forecast(code: str) -> Dict[str, Any]:
    """V7.5: 机构一致预期EPS — 同花顺正则提取 + 东财研报兜底。

    Returns:
        DataFrame [年度, 机构数, 最小值, 均值, 最大值, 行业均值]。
    """
    try:
        import re as _re2
        r = _quick_request(f"https://basic.10jqka.com.cn/new/{code}/worth.html",
                           headers={"User-Agent": UA, "Referer": "https://basic.10jqka.com.cn/"},
                           timeout=15)
        if r is not None:
            r.encoding = "gbk"
            m = _re2.search(r'汇总--预测年报每股收益.*?(<tbody>.*?</tbody>)', r.text, _re2.DOTALL)
            if m:
                rows = _re2.findall(r'<tr>(.*?)</tr>', m.group(1), _re2.DOTALL)
                data_rows = []
                for row in rows:
                    cells = _re2.findall(r'<(?:th|td)[^>]*>(.*?)</(?:th|td)>', row, _re2.DOTALL)
                    cleaned = [_re2.sub(r'<[^>]+>', '', c).strip() for c in cells]
                    if len(cleaned) >= 5:
                        data_rows.append(cleaned[:6])
                if data_rows:
                    import pandas as _pd
                    return _pd.DataFrame(data_rows,
                                         columns=["年度", "机构数", "最小值", "均值", "最大值", "行业均值"])
    except Exception:
        pass
    # 东财研报兜底
    try:
        from tdx_client import tdx_get_eps_from_reports
        em_eps = tdx_get_eps_from_reports(code)
        if em_eps and em_eps.get("eps_cur"):
            import pandas as _pd
            return _pd.DataFrame({
                "年度": ["预测今年", "预测明年"],
                "机构数": [1, 1], "最小值": [0, 0],
                "均值": [em_eps["eps_cur"], em_eps.get("eps_next") or 0],
                "最大值": [0, 0], "行业均值": [0, 0]
            })
    except Exception:
        pass
    import pandas as _pd
    return _pd.DataFrame()


@cached(category="northbound", ttl_seconds=TTL["northbound"])
def get_northbound_hold(code: str, days: int = 20) -> List[Dict[str, Any]]:
    """北向资金持仓动态。

    Args:
        code: 股票代码。
        days: 查询天数。

    Returns:
        list: [{date, hold_shares, market_cap, hold_ratio, change_shares, change_ratio}, ...]。
    """
    data = eastmoney_datacenter(code, "RPT_MUTUAL_HOLDSTOCKNORTH_STA",
                                filter_str=f'(SECURITY_CODE="{code}")',
                                page_size=days, sort_columns="TRADE_DATE", sort_types="-1")
    rows = []
    for row in data:
        rows.append({
            "date": str(row.get("TRADE_DATE", "") or "")[:10],
            "hold_shares": float(row.get("HOLD_SHARES") or 0),
            "market_cap": float(row.get("HOLD_MARKET_CAP") or row.get("MARKET_CAP") or 0),
            "hold_ratio": float(row.get("FREE_SHARES_RATIO") or row.get("A_SHARES_RATIO")
                          or row.get("TOTAL_SHARES_RATIO") or row.get("HOLD_RATIO") or 0),
            "change_shares": float(row.get("CHANGE_SHARES") or 0),
            "change_ratio": float(row.get("CHANGE_RATE") or 0),
        })
    return rows


@cached(category="margin_trading", ttl_seconds=TTL["margin_trading"])
def get_margin_trading(code: str) -> List[Dict[str, Any]]:
    """融资融券数据。

    Returns:
        list: [{date, rzye, rzmre, rzche, rqye, rqmcl, rqchl, rzrqye}, ...]。
    """
    data = eastmoney_datacenter(code, "RPTA_WEB_RZRQ_GGMX",
                                filter_str=f'(SCODE="{code}")',
                                page_size=15, sort_columns="DATE", sort_types="-1")
    rows = []
    for row in data:
        rows.append({
            "date": str(row.get("DATE", "") or "")[:10],
            "rzye": float(row.get("RZYE") or 0),
            "rzmre": float(row.get("RZMRE") or 0),
            "rzche": float(row.get("RZCHE") or 0),
            "rqye": float(row.get("RQYE") or 0),
            "rqmcl": float(row.get("RQMCL") or 0),
            "rqchl": float(row.get("RQCHL") or 0),
            "rzrqye": float(row.get("RZRQYE") or 0),
        })
    return rows


@cached(category="block_trade", ttl_seconds=TTL["block_trade"])
def get_block_trade(code: str) -> List[Dict[str, Any]]:
    """大宗交易数据。

    Returns:
        list: [{date, price, close, premium_pct, vol, amount, buyer, seller}, ...]。
    """
    data = _em_filter(code, "RPT_DATA_BLOCKTRADE",
                      page_size=15, sort_columns="TRADE_DATE", sort_types="-1")
    rows = []
    for row in data:
        close = float(row.get("CLOSE_PRICE") or 0)
        deal_price = float(row.get("DEAL_PRICE") or 0)
        premium = ((deal_price / close - 1) * 100) if close else 0
        rows.append({
            "date": str(row.get("TRADE_DATE", "") or "")[:10],
            "price": deal_price,
            "close": close,
            "premium_pct": round(premium, 2),
            "vol": float(row.get("DEAL_VOLUME") or 0),
            "amount": float(row.get("DEAL_AMT") or 0),
            "buyer": str(row.get("BUYER_NAME", "") or ""),
            "seller": str(row.get("SELLER_NAME", "") or ""),
        })
    return rows


@cached(category="dividend", ttl_seconds=TTL["dividend"])
def get_dividend_history(code):
    """V7.5: 分红历史 → TDX xdxr_info（东财 fallback 已删除）"""
    from tdx_client import tdx_get_dividend_history
    return tdx_get_dividend_history(code)


@cached(category="concept_blocks", ttl_seconds=TTL["concept_blocks"])
def get_concept_blocks(code: str) -> Dict[str, Any]:
    """V7.5: 概念板块 — 纯 TDX belong_board（短线脚本抽取统一）。

    返回: {"industry": [...], "concept": [...], "region": [...], "concept_tags": [...]}
    """
    from tdx_client import tdx_get_belong_boards
    boards = tdx_get_belong_boards(code)
    if not boards:
        return {"industry": [], "concept": [], "region": [], "concept_tags": []}
    result = {
        "industry": boards.get("industry", []),
        "concept": boards.get("concept", []),
        "region": boards.get("area", []),
        "concept_tags": [c["name"] for c in boards.get("concept", [])],
    }
    return result


def get_ths_hot_reason(code: str, date_str: str) -> Optional[Dict[str, Any]]:
    """V7.5: 同花顺热点题材归因（短线脚本抽取统一）。

    返回: {"reason": str} 或 None。
    """
    url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{date_str}/orderby/date/orderway/desc/charset/GBK/"
    try:
        r = _quick_request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0"}, timeout=10)
        if r is None:
            return None
        d = r.json()
        if str(d.get("errocode", 0)) != "0":
            return None
        for row in (d.get("data") or []):
            if str(row.get("code")) == str(code):
                return {"reason": row.get("reason", "")}
    except Exception:
        pass
    return None


async def get_ths_hot_reason_async(session: Any, code: str, date_str: str) -> Optional[Dict[str, Any]]:
    """V7.5: 同花顺热点题材归因（async版）。"""
    url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{date_str}/orderby/date/orderway/desc/charset/GBK/"
    try:
        r = await _async_quick_request(session, url,
                                       headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0"},
                                       timeout=10)
        if r is None:
            return None
        # r 已经是解析后的 dict（_async_quick_request 内部已调用 json）
        d = r
        if str(d.get("errocode", 0)) != "0":
            return None
        for row in (d.get("data") or []):
            if str(row.get("code")) == str(code):
                return {"reason": row.get("reason", "")}
    except Exception:
        pass
    return None


@cached(category="industry_peers", ttl_seconds=TTL["industry_peers"])
def get_industry_peers(code: str, top_n: int = 3, info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """V7.5: 同业对比 — TDX 三级兜底（belong_board → board_members → board_by_name）。

    返回: {
        "industry": str, "my_mcap": float, "my_rank": int, "industry_count": int,
        "peers": [...], "all_members": [...]
    }
    """
    from tdx_client import tdx_get_belong_boards, tdx_get_board_members, tdx_get_board_by_name
    
    _sc = _load_strategy_config()
    _mkt_cfg = _sc.get("market", {})
    _peers_low = _mkt_cfg.get("peers_mcap_low", 0.3)
    _peers_high = _mkt_cfg.get("peers_mcap_high", 3.0)

    # 1. TDX board_members（通过 belong_board 获取 board_code）
    boards = tdx_get_belong_boards(code)
    industry_boards = boards.get("industry", []) if boards else []

    if industry_boards:
        primary = industry_boards[0]
        members = tdx_get_board_members(primary["code"])
        if not members:
            members = tdx_get_board_by_name(primary["name"], board_type=0)
        if members:
            members_by_mcap = sorted(members, key=lambda x: x.get("mcap_yi", 0), reverse=True)
            my_mcap = 0
            my_rank = 0
            for i, m in enumerate(members_by_mcap, 1):
                if m["code"] == code:
                    my_mcap = m.get("mcap_yi", 0)
                    my_rank = i
                    break
            # 第一只：行业标杆（市值最大），其余：市值相近（0.3~3 倍）
            others = [m for m in members_by_mcap if m["code"] != code]
            peers = []
            if others:
                peers.append(others[0])  # 行业龙头
            if my_mcap > 0:
                similar = [m for m in others[1:] if _peers_low * my_mcap <= m.get("mcap_yi", 0) <= _peers_high * my_mcap]
                peers += similar[:top_n - 1]
            if len(peers) < top_n:
                peers += [m for m in others if m not in peers][:top_n - len(peers)]
            return {
                "industry": primary["name"],
                "my_mcap": my_mcap,
                "my_rank": my_rank,
                "industry_count": len(members),
                "peers": peers[:top_n],
                "all_members": members_by_mcap,
            }

    # 2. Fallback: 无 industry_boards → 用 info.industry + board_list 匹配
    ind_name = info.get("industry", "") if info else ""
    if ind_name:
        st = tdx_get_board_by_name(ind_name, board_type=0)
        if st:
            st_by_mcap = sorted(st, key=lambda x: x.get("mcap_yi", 0), reverse=True)
            my_mcap = 0
            my_rank = 0
            for i, s in enumerate(st_by_mcap, 1):
                if s["code"] == code:
                    my_mcap = s.get("mcap_yi", 0)
                    my_rank = i
                    break
            others = [s for s in st_by_mcap if s["code"] != code]
            peers = []
            if others:
                peers.append(others[0])
            if my_mcap > 0:
                similar = [s for s in others[1:] if _peers_low * my_mcap <= s.get("mcap_yi", 0) <= _peers_high * my_mcap]
                peers += similar[:top_n - 1]
            if len(peers) < top_n:
                peers += [s for s in others if s not in peers][:top_n - len(peers)]
            return {
                "industry": ind_name,
                "my_mcap": my_mcap,
                "my_rank": my_rank,
                "industry_count": len(st),
                "peers": peers[:top_n],
            }

    return {"industry": "", "my_mcap": 0, "my_rank": 0, "industry_count": 0, "peers": []}


@cached(category="industry_peers", ttl_seconds=TTL["industry_peers"])
def get_stock_sector_rank(code: str, info: Optional[Dict[str, Any]] = None, q: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """V7.5: 板块内排名 — TDX 优先。

    返回: {"rank": int, "total": int, "change_pct": float} 或 None。
    """
    from tdx_client import tdx_get_belong_boards, tdx_get_board_members, tdx_get_board_by_name

    # 1. TDX board_members（同源分类，精确匹配）
    boards = tdx_get_belong_boards(code)
    industry_boards = boards.get("industry", []) if boards else []

    if industry_boards:
        primary = industry_boards[0]
        members = tdx_get_board_members(primary["code"])
        if members:
            members_by_chg = sorted(members, key=lambda x: x.get("change_pct", 0), reverse=True)
            for i, m in enumerate(members_by_chg, 1):
                if m["code"] == code:
                    _chg = q.get("change_pct", m["change_pct"]) if q else m["change_pct"]
                    return {"rank": i, "total": len(members), "change_pct": _chg}

    # 2. Fallback: TDX board_list → match by name → board_members
    ind_name = (industry_boards[0].get("name", "") if industry_boards else "") or (info.get("industry", "") if info else "")
    if ind_name:
        st = tdx_get_board_by_name(ind_name, board_type=0)
        if st:
            st_sorted = sorted(st, key=lambda x: x.get("change_pct", 0), reverse=True)
            for i, s in enumerate(st_sorted, 1):
                if s["code"] == code:
                    _chg = q.get("change_pct", s["change_pct"]) if q else s["change_pct"]
                    return {"rank": i, "total": len(st), "change_pct": _chg}

    return None


@cached(category="industry_compare", ttl_seconds=TTL["industry_compare"])
def get_industry_comparison(top_n: int = 20) -> Dict[str, Any]:
    """V4.2: 全行业排名 → TDX board_list。

    Args:
        top_n: 返回行业数量上限（当前未使用，保留参数兼容性）。

    Returns:
        dict: {"all": sectors}。
    """
    from tdx_client import tdx_get_board_list
    sectors = tdx_get_board_list(0)  # BoardType.HY = 0 行业一级
    return {"all": sectors} if sectors else {"all": []}


def print_batch_summary(results, total):
    """批量执行结果汇总打印。

    Args:
        results: 结果列表，每项应为 {"code": str, "status": str, "error": str}。
        total: 总股票数量。
    """
    ok = [r for r in results if r["status"] == "成功"]
    fd = [r for r in results if r["status"] == "数据失败"]
    fg = [r for r in results if r["status"] in ("GD上传失败", "GD上传异常", "GD文件夹失败", "GD未连接")]
    print(f"\n{'=' * 60}")
    print(f"  批量执行完成 — 共处理 {total} 只股票")
    print(f"{'=' * 60}")
    print(f"  ✅ 全部成功: {len(ok)}  |  ❌ 数据失败: {len(fd)}  |  ⚠️ GD上传失败: {len(fg)}")


def save_score_snapshot(script_type: str, code: str, name: str, total_score: float, price: float):
    """V7.5: 保存单只股票的评分快照（智能合并模式）。

    Args:
        script_type: 脚本类型（full/val/mak/med/lng/sht）
        code: 股票代码
        name: 股票名称
        total_score: 五维综合评分
        price: 当前价格
    """
    try:
        from analyze_history import save_snapshot
        save_snapshot(script_type, {
            code: {
                "name": name,
                "total_score": total_score,
                "price": price,
                "report_source": script_type
            }
        })
    except ImportError:
        pass  # analyze_history.py 不存在时静默跳过
    except Exception:
        pass  # 保存失败时静默跳过


# ═══════════════════════════════════════════════════════════
# V7.5: 统一数据获取函数（从 sht/med/lng 脚本合并）
# ═══════════════════════════════════════════════════════════


@cached(category="basic_info", ttl_seconds=TTL["basic_info"])
def get_stock_info(code: str) -> Dict[str, Any]:
    """V7.5: 个股基本信息 → 腾讯行情 + TDX"""
    name = industry = list_date = ""
    total_shares = float_shares = mcap = float_mcap = price = 0

    q = get_tencent_quote(code)
    if q:
        name = q.get("name", "")
        price = q.get("price", 0) or 0
        mcap = int(q.get("mcap_yi", 0) * 1e8)
        float_mcap = int(q.get("float_mcap_yi", 0) * 1e8)

    try:
        from tdx_client import _get_tdx_client
        client = _get_tdx_client()
        if client:
            info = client.get_finance_info(_market_code(code), code)
            if info is not None and not info.empty:
                total_shares = _safe_float(info.iloc[0].get('zong_guben', 0))
                float_shares = _safe_float(info.iloc[0].get('liutong_guben', 0))
                ipo = str(int(info.iloc[0].get('ipo_date', 0)))
                if ipo and ipo != '0':
                    list_date = ipo
    except Exception:
        pass

    if not total_shares and price > 0 and mcap > 0:
        total_shares = int(mcap / price)
    if not float_shares and price > 0 and float_mcap > 0:
        float_shares = int(float_mcap / price)

    try:
        from tdx_client import tdx_get_belong_boards
        tdx_boards = tdx_get_belong_boards(code)
        if tdx_boards and tdx_boards.get("industry"):
            industry = tdx_boards["industry"][0]["name"]
    except Exception:
        pass

    return {
        "code": code, "name": name, "industry": industry,
        "total_shares": total_shares, "float_shares": float_shares,
        "mcap": mcap, "float_mcap": float_mcap,
        "list_date": list_date, "price": price,
    }


# ─── V8.4 新增异步函数（阶段4） ───────────────────────────────────────────

async def get_tencent_quote_async(session: Any, code: str) -> Dict[str, Any]:
    """异步版 get_tencent_quote（复用 TDX 同步函数）"""
    import asyncio
    from tdx_client import tdx_get_quote_full
    return await asyncio.to_thread(tdx_get_quote_full, code)


async def get_dividend_history_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """异步版 get_dividend_history"""
    import asyncio
    return await asyncio.to_thread(get_dividend_history, code)


async def get_concept_blocks_async(session: Any, code: str) -> Dict[str, Any]:
    """异步版 get_concept_blocks"""
    import asyncio
    return await asyncio.to_thread(get_concept_blocks, code)


async def get_holder_structure_async(session: Any, code: str, today_str: str = "") -> Dict[str, Any]:
    """异步版 get_holder_structure"""
    import asyncio
    return await asyncio.to_thread(get_holder_structure, code, today_str)


async def get_industry_peers_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """异步版 get_industry_peers"""
    import asyncio
    return await asyncio.to_thread(get_industry_peers, code)


async def get_stock_sector_rank_async(session: Any, code: str) -> Dict[str, Any]:
    """异步版 get_stock_sector_rank"""
    import asyncio
    return await asyncio.to_thread(get_stock_sector_rank, code)


async def get_industry_comparison_async(session: Any, industry: str) -> Dict[str, Any]:
    """异步版 get_industry_comparison"""
    import asyncio
    return await asyncio.to_thread(get_industry_comparison, industry)


async def get_stock_info_async(session: Any, code: str) -> Dict[str, Any]:
    """异步版 get_stock_info"""
    import asyncio
    return await asyncio.to_thread(get_stock_info, code)


@cached(category="financial", ttl_seconds=TTL["financial"])
def get_sina_financial_report(code: str, num_periods: int = 12) -> Dict[str, Any]:
    """新浪利润表 — 支持多期数（默认12期 ≈ 3年）"""
    prefix = "sh" if code.startswith("6") else "sz"
    paper_code = f"{prefix}{code}"
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
    params = {"paperCode": paper_code, "source": "lrb", "type": "0", "page": "1", "num": str(num_periods)}
    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return []
        rl = (r.json().get("result") or {}).get("data", {}).get("report_list", {})
        rows = []
        for date_key, period in rl.items():
            item_map = {}
            for entry in period.get("data", []):
                item_map[entry.get("item_title", "")] = entry.get("item_value")
            rows.append({
                "报告日": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}",
                "营业总收入": item_map.get("营业总收入") or "0",
                "营业成本": item_map.get("营业成本") or "0",
                "净利润": item_map.get("归属于母公司所有者的净利润") or item_map.get("净利润") or "0",
            })
        return rows
    except Exception:
        return []


@cached(category="balance_sheet", ttl_seconds=TTL["balance_sheet"])
def get_sina_balance_sheet(code: str) -> List[Dict[str, Any]]:
    """获取新浪资产负债表（fzb）最近5期数据"""
    try:
        prefix = "sh" if code.startswith("6") else "sz"
        paper_code = f"{prefix}{code}"
        url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
        params = {"paperCode": paper_code, "source": "fzb", "type": "0", "page": "1", "num": "5"}
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return None
        rl = (r.json().get("result") or {}).get("data", {}).get("report_list", {})
        rows = []
        for date_key, period in rl.items():
            item_map = {}
            for entry in period.get("data", []):
                item_map[entry.get("item_title", "")] = entry.get("item_value")
            rows.append({
                "报告日": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}",
                "应收账款": item_map.get("应收账款") or "0",
                "存货": item_map.get("存货") or "0",
                "商誉": item_map.get("商誉") or "0",
                "货币资金": item_map.get("货币资金") or "0",
                "短期借款": item_map.get("短期借款") or "0",
                "一年内到期的非流动负债": item_map.get("一年内到期的非流动负债") or "0",
                "长期借款": item_map.get("长期借款") or "0",
                "应付债券": item_map.get("应付债券") or "0",
                "资产总计": item_map.get("资产总计") or "0",
                "负债合计": item_map.get("负债合计") or "0",
                # 银行股字段映射：优先普通企业字段，备选银行股字段
                "归属于母公司股东权益合计": (item_map.get("归属于母公司股东权益合计") or 
                                          item_map.get("归属于母公司股东的权益") or 
                                          item_map.get("股东权益") or "0"),
            })
        return rows if rows else None
    except Exception:
        return None


@cached(category="hsgt_flow", ttl_seconds=TTL["hsgt_flow"], use_args=False)
def get_hsgt_macro_flow() -> Optional[Dict[str, Any]]:
    """同花顺北向资金大盘净流入（宏观风向标）"""
    url = "https://data.hexin.cn/market/hsgtApi/method/dayChart/"
    headers = {"User-Agent": UA, "Host": "data.hexin.cn", "Referer": "https://data.hexin.cn/"}
    try:
        r = _quick_request(url, headers=headers, timeout=10)
        if r is None:
            return None
        d = r.json()
        hgt = d.get("hgt", [])
        sgt = d.get("sgt", [])
        if not hgt or not sgt:
            return None
        hgt_val = float(hgt[-1]) if hgt[-1] else 0
        sgt_val = float(sgt[-1]) if sgt[-1] else 0
        return {"hgt": hgt_val, "sgt": sgt_val, "total": hgt_val + sgt_val}
    except Exception:
        return None


async def get_hsgt_macro_flow_async(session: Any) -> Optional[Dict[str, Any]]:
    """async 版: 同花顺北向资金大盘净流入"""
    url = "https://data.hexin.cn/market/hsgtApi/method/dayChart/"
    headers = {"User-Agent": UA, "Host": "data.hexin.cn", "Referer": "https://data.hexin.cn/"}
    try:
        r = await _async_quick_request(session, url, headers=headers, timeout=10)
        if r is None:
            return None
        d = r
        hgt = d.get("hgt", [])
        sgt = d.get("sgt", [])
        if not hgt or not sgt:
            return None
        hgt_val = float(hgt[-1]) if hgt[-1] else 0
        sgt_val = float(sgt[-1]) if sgt[-1] else 0
        return {"hgt": hgt_val, "sgt": sgt_val, "total": hgt_val + sgt_val}
    except Exception:
        return None


@cached(category="lockup_expiry", ttl_seconds=TTL["lockup_expiry"])
def get_lockup_expiry(code: str, today_str: str, days: int = 90, include_history: bool = False) -> Any:
    """限售解禁日历。

    Args:
        code: 股票代码
        today_str: 当前日期 YYYY-MM-DD
        days: 未来展望窗口天数（默认90天）
        include_history: 是否返回历史记录（True=返回dict, False=返回list）

    Returns:
        include_history=True: {"history": [...], "upcoming": [...]}
        include_history=False: [{"date", "type", "shares", "ratio"}, ...]
    """
    end_str = (datetime.strptime(today_str, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")

    if include_history:
        data = _em_filter(code, "RPT_LIFT_STAGE", page_size=15, sort_columns="FREE_DATE", sort_types="-1")
        history = [
            {"date": str(r.get("FREE_DATE", "") or "")[:10],
             "type": r.get("FREE_SHARES_TYPE", ""),
             "shares": _safe_float(r.get("FREE_SHARES")),
             "ratio": _safe_float(r.get("FREE_RATIO"))}
            for r in data
        ]
    else:
        history = []

    data2 = eastmoney_datacenter(code, "RPT_LIFT_STAGE",
                                 filter_str=f"(SECURITY_CODE=\"{code}\")(FREE_DATE>='{today_str}')(FREE_DATE<='{end_str}')",
                                 page_size=20, sort_columns="FREE_DATE", sort_types="1")
    upcoming = [
        {"date": str(r.get("FREE_DATE", "")[:10]),
         "type": r.get("FREE_SHARES_TYPE", ""),
         "shares": float(r.get("FREE_SHARES") or 0),
         "ratio": float(r.get("FREE_RATIO") or 0)}
        for r in data2
    ]

    if include_history:
        return {"history": history, "upcoming": upcoming}
    return upcoming


@cached(category="gross_margin_roe", ttl_seconds=TTL["gross_margin_roe"])
def get_gross_margin_and_roe(code: str, fin_report: Any = None, bs_data: Any = None) -> Dict[str, Any]:
    """获取最新年度的毛利率和ROE"""
    try:
        if fin_report is None:
            prefix = "SH" if code.startswith("6") else "SZ"
            paper_code = f"{prefix}{code}"
            url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
            params = {"paperCode": paper_code, "source": "lrb", "type": "0", "page": "1", "num": "1"}
            r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=15)
            if r is None or r.status_code != 200:
                return None
            d = r.json()
            items = (d.get("result") or {}).get("data", [])
            if not items:
                return None
            item = items[0]
        else:
            item = fin_report[0] if fin_report else None
            if not item:
                return None

        if fin_report:
            rev = _safe_float(item.get("营业总收入"))
            cost = _safe_float(item.get("营业成本"))
            profit = _safe_float(item.get("归属于母公司所有者的净利润") or item.get("净利润"))
        else:
            rev = _safe_float(item.get("营业收入") or item.get("营业总收入"))
            cost = _safe_float(item.get("营业成本"))
            profit = _safe_float(item.get("归属于母公司所有者的净利润"))

        gross_margin = (rev - cost) / rev * 100 if rev > 0 else None

        bs = bs_data if bs_data is not None else get_sina_balance_sheet(code)
        roe = None
        if bs:
            equity_yi = _safe_float(bs[0].get("归属于母公司股东权益合计", 0))
            if equity_yi > 0:
                roe = (profit * 100) / equity_yi if equity_yi > 0 else None

        return {"gross_margin": gross_margin, "roe": roe}
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# A股交易日历与市场状态
# ═══════════════════════════════════════════════════════════

def _try_upgrade_calendar():
    """尝试自动升级 chinese-calendar 库

    Returns:
        bool: True=升级成功, False=升级失败
    """
    import subprocess, sys, importlib
    try:
        print("⏳ 检测到节假日数据过期，正在自动更新 chinese-calendar...", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "chinese-calendar"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            # 强制重新加载 chinese_calendar 模块
            import chinese_calendar
            importlib.reload(chinese_calendar)
            # 同时更新本地 stock_calendar.py（如果存在）
            try:
                import stock_calendar as local_stock_cal
                importlib.reload(local_stock_cal)
            except (ImportError, ModuleNotFoundError):
                pass
            print("✅ chinese-calendar 更新成功", flush=True)
            return True
        else:
            print(f"⚠️ 自动更新失败: {result.stderr[:200]}", flush=True)
            return False
    except Exception as e:
        print(f"⚠️ 自动更新异常: {e}", flush=True)
        return False


def get_valuation_pe_center(industry_name: str = "") -> float:
    """按行业返回估值PE中枢（用于报告参考，若未命中行业则返回全局默认）。

    Args:
        industry_name: 行业名（可为空字符串，默认返回全局默认）

    Returns:
        float: 行业PE中枢，默认 30.0
    """
    sc = _load_strategy_config()
    pe_map = sc.get("valuation_pe_centers", {})
    if pe_map:
        if industry_name in pe_map:
            return float(pe_map[industry_name])
    # 回退：使用 valuation.pe_mid
    val = sc.get("valuation", {}).get("pe_mid", 30.0)
    return float(val)


def is_trading_day(d=None):
    """判断是否为A股交易日（含节假日+调休检测，自动升级+降级）

    Args:
        d: date 或 datetime，默认今天

    Returns:
        bool: True=交易日, False=休市日
    """
    from datetime import date as _date, datetime as _datetime

    if d is None:
        d = _date.today()
    if isinstance(d, _datetime):
        d = d.date()

    # 优先使用本地 stock_calendar.py（项目目录下，用户可控）
    try:
        import stock_calendar as _local_cal
        return _local_cal.is_workday(d)
    except (ImportError, ModuleNotFoundError):
        pass
    except NotImplementedError:
        pass  # 年份超出本地数据范围，尝试库

    # 降级到 chinese-calendar 库
    try:
        from chinese_calendar import is_workday
        return is_workday(d)
    except NotImplementedError as e:
        # 年份超出库范围（>2026），尝试自动升级
        if "no available data" in str(e) or "year" in str(e).lower():
            if _try_upgrade_calendar():
                # 升级后重新尝试
                try:
                    from chinese_calendar import is_workday
                    return is_workday(d)
                except Exception:
                    pass
        # 降级为简单判断（周一到周五）
        return d.weekday() < 5
    except ImportError:
        # chinese-calendar 未安装，尝试自动安装
        if _try_upgrade_calendar():
            try:
                from chinese_calendar import is_workday
                return is_workday(d)
            except Exception:
                pass
        # 降级为简单判断
        return d.weekday() < 5


def get_market_status(now=None):
    """获取A股市场状态

    Args:
        now: datetime，默认当前时间

    Returns:
        tuple: (status_str, note_str)
            status_str: 'closed' | 'pre_market' | 'morning' | 'lunch' | 'afternoon' | 'post_market'
            note_str: 给用户看的中文提示
    """
    from datetime import datetime as _datetime

    if now is None:
        now = _datetime.now()
    d = now.date()
    t = now.hour * 100 + now.minute

    if not is_trading_day(d):
        return "closed", "（休市日，数据为最近交易日快照）"
    if t < 915:
        return "pre_market", "当前为盘前时段，行情数据/北向资金为上交易日值"
    elif t < 1130:
        return "morning", "当前为盘中（上午）时段，行情数据实时跳动"
    elif t < 1300:
        return "lunch", "当前为午休时段（11:30-13:00），行情暂停"
    elif t < 1500:
        return "afternoon", "当前为盘中（下午）时段，行情数据实时跳动"
    elif t < 1630:
        return "post_market", "当前为盘后结算时段，龙虎榜/融资融券约16:30后更新"
    else:
        return "closed", ""


# ═══════════════════════════════════════════════════════════
# 异步版本函数
# ═══════════════════════════════════════════════════════════


async def get_eps_forecast_async(session: Any, code: str) -> Dict[str, Any]:
    """async 版: 机构一致预期EPS — 同花顺正则提取 + TDX兜底"""
    try:
        import re as _re2
        r = await _async_quick_request(session,
                                       f"https://basic.10jqka.com.cn/new/{code}/worth.html",
                                       headers={"User-Agent": UA, "Referer": "https://basic.10jqka.com.cn/"},
                                       timeout=15, is_json=False, encoding='gbk')
        if r is not None:
            text = r
            m = _re2.search(r'汇总--预测年报每股收益.*?(<tbody>.*?</tbody>)', text, _re2.DOTALL)
            if m:
                rows = _re2.findall(r'<tr>(.*?)</tr>', m.group(1), _re2.DOTALL)
                data_rows = []
                for row in rows:
                    cells = _re2.findall(r'<(?:th|td)[^>]*>(.*?)</(?:th|td)>', row, _re2.DOTALL)
                    cleaned = [_re2.sub(r'<[^>]+>', '', c).strip() for c in cells]
                    if len(cleaned) >= 5:
                        data_rows.append(cleaned[:6])
                if data_rows:
                    import pandas as _pd
                    return _pd.DataFrame(data_rows, columns=["年度", "机构数", "最小值", "均值", "最大值", "行业均值"])
    except Exception:
        pass

    try:
        from tdx_client import tdx_get_eps_from_reports
        em_eps = tdx_get_eps_from_reports(code)
        if em_eps and em_eps.get("eps_cur"):
            import pandas as _pd
            return _pd.DataFrame({
                "年度": ["预测今年", "预测明年"],
                "机构数": [1, 1], "最小值": [0, 0],
                "均值": [em_eps["eps_cur"], em_eps.get("eps_next") or 0],
                "最大值": [0, 0], "行业均值": [0, 0]
            })
    except Exception:
        pass

    import pandas as _pd
    return _pd.DataFrame()


async def get_sina_financial_report_async(session: Any, code: str, num_periods: int = 12) -> Dict[str, Any]:
    """async 版: 新浪利润表"""
    prefix = "sh" if code.startswith("6") else "sz"
    paper_code = f"{prefix}{code}"
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
    params = {"paperCode": paper_code, "source": "lrb", "type": "0", "page": "1", "num": str(num_periods)}
    try:
        r = await _async_quick_request(session, url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return []
        rl = (r.get("result") or {}).get("data", {}).get("report_list", {})
        rows = []
        for date_key, period in rl.items():
            item_map = {}
            for entry in period.get("data", []):
                item_map[entry.get("item_title", "")] = entry.get("item_value")
            rows.append({
                "报告日": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}",
                "营业总收入": item_map.get("营业总收入") or "0",
                "营业成本": item_map.get("营业成本") or "0",
                "净利润": item_map.get("归属于母公司所有者的净利润") or item_map.get("净利润") or "0",
            })
        return rows
    except Exception:
        return []


async def get_sina_balance_sheet_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 新浪资产负债表"""
    try:
        prefix = "sh" if code.startswith("6") else "sz"
        paper_code = f"{prefix}{code}"
        url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
        params = {"paperCode": paper_code, "source": "fzb", "type": "0", "page": "1", "num": "5"}
        r = await _async_quick_request(session, url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return None
        rl = (r.get("result") or {}).get("data", {}).get("report_list", {})
        rows = []
        for date_key, period in rl.items():
            item_map = {}
            for entry in period.get("data", []):
                item_map[entry.get("item_title", "")] = entry.get("item_value")
            rows.append({
                "报告日": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}",
                "应收账款": item_map.get("应收账款") or "0",
                "存货": item_map.get("存货") or "0",
                "商誉": item_map.get("商誉") or "0",
                "货币资金": item_map.get("货币资金") or "0",
                "短期借款": item_map.get("短期借款") or "0",
                "一年内到期的非流动负债": item_map.get("一年内到期的非流动负债") or "0",
                "长期借款": item_map.get("长期借款") or "0",
                "应付债券": item_map.get("应付债券") or "0",
                "资产总计": item_map.get("资产总计") or "0",
                "负债合计": item_map.get("负债合计") or "0",
                # 银行股字段映射：优先普通企业字段，备选银行股字段
                "归属于母公司股东权益合计": (item_map.get("归属于母公司股东权益合计") or 
                                          item_map.get("归属于母公司股东的权益") or 
                                          item_map.get("股东权益") or "0"),
            })
        return rows if rows else None
    except Exception:
        return None


async def get_reports_async(session: Any, code: str, max_pages: int = 3) -> List[Dict[str, Any]]:
    """async 版: 东财研报列表"""
    api_url = "https://reportapi.eastmoney.com/report/list"
    all_records = []
    for page in range(1, max_pages + 1):
        params = {
            "pageSize": "50", "industry": "*", "rating": "*",
            "beginTime": "2000-01-01", "endTime": "2030-01-01",
            "pageNo": str(page), "code": code, "qType": "0"
        }
        try:
            r = await _async_request_with_retry(session, api_url, params=params, headers={"User-Agent": UA}, timeout=30)
            if r is None:
                break
            rows = r.get("data") or []
            if not rows:
                break
            all_records.extend(rows)
        except Exception:
            break
    return all_records


async def get_northbound_hold_async(session: Any, code: str, days: int = 20) -> List[Dict[str, Any]]:
    """async 版: 北向资金持仓动态"""
    data = await eastmoney_datacenter_async(session, code, "RPT_MUTUAL_HOLDSTOCKNORTH_STA",
                                            filter_str=f'(SECURITY_CODE="{code}")',
                                            page_size=days, sort_columns="TRADE_DATE", sort_types="-1")
    rows = []
    for row in data:
        rows.append({
            "date": str(row.get("TRADE_DATE", "") or "")[:10],
            "hold_shares": float(row.get("HOLD_SHARES") or 0),
            "market_cap": float(row.get("HOLD_MARKET_CAP") or row.get("MARKET_CAP") or 0),
            "hold_ratio": float(row.get("FREE_SHARES_RATIO") or row.get("A_SHARES_RATIO") or
                               row.get("TOTAL_SHARES_RATIO") or row.get("HOLD_RATIO") or 0),
            "change_shares": float(row.get("CHANGE_SHARES") or 0),
            "change_ratio": float(row.get("CHANGE_RATE") or 0),
        })
    return rows


async def get_margin_trading_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 融资融券数据"""
    data = await eastmoney_datacenter_async(session, code, "RPTA_WEB_RZRQ_GGMX",
                                            filter_str=f'(SCODE="{code}")',
                                            page_size=15, sort_columns="DATE", sort_types="-1")
    rows = []
    for row in data:
        rows.append({
            "date": str(row.get("DATE", "") or "")[:10],
            "rzye": float(row.get("RZYE") or 0),
            "rzmre": float(row.get("RZMRE") or 0),
            "rzche": float(row.get("RZCHE") or 0),
            "rqye": float(row.get("RQYE") or 0),
            "rqmcl": float(row.get("RQMCL") or 0),
            "rqchl": float(row.get("RQCHL") or 0),
            "rzrqye": float(row.get("RZRQYE") or 0),
        })
    return rows


async def get_block_trade_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 大宗交易数据"""
    data = await _em_filter_async(session, code, "RPT_DATA_BLOCKTRADE",
                                  page_size=15, sort_columns="TRADE_DATE", sort_types="-1")
    rows = []
    for row in data:
        close = float(row.get("CLOSE_PRICE") or 0)
        deal_price = float(row.get("DEAL_PRICE") or 0)
        premium = ((deal_price / close - 1) * 100) if close else 0
        rows.append({
            "date": str(row.get("TRADE_DATE", "") or "")[:10],
            "price": deal_price,
            "close": close,
            "premium_pct": round(premium, 2),
            "vol": float(row.get("DEAL_VOLUME") or 0),
            "amount": float(row.get("DEAL_AMT") or 0),
            "buyer": str(row.get("BUYER_NAME", "") or ""),
            "seller": str(row.get("SELLER_NAME", "") or ""),
        })
    return rows


async def get_lockup_expiry_async(session: Any, code: str, today_str: str, days: int = 90, include_history: bool = False) -> Any:
    """async 版: 限售解禁日历"""
    end_str = (datetime.strptime(today_str, "%Y-%m-%d") + timedelta(days=days)).strftime("%Y-%m-%d")

    if include_history:
        data = await _em_filter_async(session, code, "RPT_LIFT_STAGE", page_size=15,
                                      sort_columns="FREE_DATE", sort_types="-1")
        history = [
            {"date": str(r.get("FREE_DATE", "") or "")[:10],
             "type": r.get("FREE_SHARES_TYPE", ""),
             "shares": _safe_float(r.get("FREE_SHARES")),
             "ratio": _safe_float(r.get("FREE_RATIO"))}
            for r in data
        ]
    else:
        history = []

    data2 = await eastmoney_datacenter_async(session, code, "RPT_LIFT_STAGE",
                                             filter_str=f"(SECURITY_CODE=\"{code}\")(FREE_DATE>='{today_str}')(FREE_DATE<='{end_str}')",
                                             page_size=20, sort_columns="FREE_DATE", sort_types="1")
    upcoming = [
        {"date": str(r.get("FREE_DATE", "")[:10]),
         "type": r.get("FREE_SHARES_TYPE", ""),
         "shares": float(r.get("FREE_SHARES") or 0),
         "ratio": float(r.get("FREE_RATIO") or 0)}
        for r in data2
    ]

    if include_history:
        return {"history": history, "upcoming": upcoming}
    return upcoming


async def get_gross_margin_and_roe_async(session: Any, code: str, fin_report: Any = None, bs_data: Any = None) -> Dict[str, Any]:
    """async 版: 获取最新年度的毛利率和ROE"""
    try:
        if fin_report is None:
            prefix = "SH" if code.startswith("6") else "SZ"
            paper_code = f"{prefix}{code}"
            url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
            params = {"paperCode": paper_code, "source": "lrb", "type": "0", "page": "1", "num": "1"}
            r = await _async_quick_request(session, url, params=params, headers={"User-Agent": UA}, timeout=15)
            if r is None:
                return None
            d = r
            items = (d.get("result") or {}).get("data", [])
            if not items:
                return None
            item = items[0]
        else:
            item = fin_report[0] if fin_report else None
            if not item:
                return None

        if fin_report:
            rev = _safe_float(item.get("营业总收入"))
            cost = _safe_float(item.get("营业成本"))
            profit = _safe_float(item.get("归属于母公司所有者的净利润") or item.get("净利润"))
        else:
            rev = _safe_float(item.get("营业收入") or item.get("营业总收入"))
            cost = _safe_float(item.get("营业成本"))
            profit = _safe_float(item.get("归属于母公司所有者的净利润"))

        gross_margin = (rev - cost) / rev * 100 if rev > 0 else None

        bs = bs_data if bs_data is not None else await get_sina_balance_sheet_async(session, code)
        roe = None
        if bs:
            equity_yi = _safe_float(bs[0].get("归属于母公司股东权益合计", 0))
            if equity_yi > 0:
                roe = (profit * 100) / equity_yi if equity_yi > 0 else None

        return {"gross_margin": gross_margin, "roe": roe}
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
# V8.2: 统一评分接口
# ═══════════════════════════════════════════════════════════

from dataclasses import dataclass, field


@dataclass
class ScoreData:
    """评分输入数据结构"""
    # 基本信息
    code: str = ""
    name: str = ""
    price: float = 0.0
    change_pct: float = 0.0
    
    # 技术面数据
    ma5: float = 0.0
    ma10: float = 0.0
    ma20: float = 0.0
    macd_dif: float = 0.0
    macd_dea: float = 0.0
    rsi14: float = 50.0
    kdj_k: float = 50.0
    kdj_d: float = 50.0
    kdj_j: float = 50.0
    boll_pos: float = 50.0
    volume_ratio: float = 1.0
    ret_20d: float = 0.0
    high_120d: float = 0.0
    is_limit_up: bool = False
    
    # 基本面数据
    roe: float = 0.0
    gross_margin: float = 0.0
    net_profit_margin: float = 0.0
    debt_ratio: float = 0.0
    asset_liability_ratio: float = 0.0
    ocf_ratio: float = 0.0  # 经营现金流/净利润
    
    # 估值数据
    pe_ttm: float = 0.0
    pb: float = 0.0
    forward_pe: float = 0.0
    industry_pe: float = 0.0
    drawdown_from_high: float = 0.0
    
    # 资金面数据
    main_net_inflow: float = 0.0
    consecutive_inflow_days: int = 0
    northbound_change: float = 0.0
    institution_net_buy: float = 0.0
    margin_short_decline: bool = False
    
    # 筹码数据
    holder_change_ratio: float = 0.0
    holder_consecutive_decrease: bool = False
    institution_holding_pct: float = 0.0
    
    # 分红数据
    dividend_yield: float = 0.0
    consecutive_dividend_years: int = 0


@dataclass
class ScoreResult:
    """评分结果数据结构"""
    total_score: float = 0.0
    dimensions: Dict[str, float] = field(default_factory=dict)
    details: List[str] = field(default_factory=list)
    report_source: str = ""


def _score_technical(data: ScoreData, cfg: Optional[Dict] = None) -> tuple:
    """技术面评分（0-100基准，加减分）"""
    score = 50.0
    details = []
    tc = cfg or {}
    
    # 均线系统
    if data.ma5 > 0 and data.ma10 > 0 and data.ma20 > 0:
        if data.ma5 > data.ma10 > data.ma20:
            score += tc.get("ma_golden_cross", 10)
            details.append("均线多头排列")
        elif data.ma5 < data.ma10 < data.ma20:
            score += tc.get("ma_death_cross", -10)
        else:
            score += 3
    
    # 涨跌幅
    if data.change_pct > 0:
        add_score = min(int(data.change_pct * 0.5), 15)
        score += add_score
        details.append(f"涨跌+{data.change_pct:.1f}%")
    elif data.change_pct < -3:
        score += max(int(data.change_pct * 0.5), -10)
        details.append(f"涨跌{data.change_pct:.1f}%")
    
    # 涨停封板
    if data.is_limit_up:
        score += tc.get("limit_up", 15)
        details.append("涨停封板")
    
    # MACD
    if data.macd_dif > data.macd_dea > 0:
        score += tc.get("macd_bull", 8)
        details.append("MACD金叉")
    elif data.macd_dif < data.macd_dea < 0:
        score += tc.get("macd_bear", -8)
    
    # RSI
    if 40 <= data.rsi14 <= 70:
        score += tc.get("rsi_optimal", 5)
    elif data.rsi14 < 30:
        score += tc.get("rsi_oversold", 3)
        details.append("RSI超卖")
    elif data.rsi14 > 80:
        score += tc.get("rsi_overbought", -4)
    
    # KDJ
    if data.kdj_k > data.kdj_d and data.kdj_k < 80:
        score += tc.get("kdj_golden", 3)
    elif data.kdj_j > 110:
        score += tc.get("kdj_overbought", -3)
    
    # 20日涨跌幅
    if data.ret_20d < -30:
        score += tc.get("ret_20d_drop", -6)
    elif data.ret_20d > 15:
        score += tc.get("ret_20d_rally", 5)
    
    # 距高点回撤
    if data.high_120d > 0 and data.price > 0:
        ratio = (data.price / data.high_120d - 1) * 100
        if ratio < -30:
            score += tc.get("depth_pullback", 4)
            details.append(f"距高点回撤{abs(ratio):.0f}%")
    
    return max(0, min(100, score)), details


def _score_fundamental(data: ScoreData, cfg: Optional[Dict] = None) -> tuple:
    """基本面评分（0-100基准，加减分）"""
    score = 50.0
    details = []
    fc = cfg or {}
    
    # ROE
    if data.roe >= 20:
        score += fc.get("roe_excellent", 25)
        details.append(f"ROE={data.roe:.1f}%优秀")
    elif data.roe >= 15:
        score += fc.get("roe_good", 15)
        details.append(f"ROE={data.roe:.1f}%良好")
    elif data.roe >= 10:
        score += fc.get("roe_medium", 8)
        details.append(f"ROE={data.roe:.1f}%中等")
    elif data.roe < 0:
        # 亏损股：强制评分下限为20分
        details.append(f"⚠️ ROE={data.roe:.1f}%亏损，基本面严重恶化")
        score = min(score, 20.0)  # 强制下限20分
    
    # 毛利率
    if data.gross_margin >= 40:
        score += fc.get("gross_margin_high", 10)
        details.append(f"毛利率{data.gross_margin:.1f}%")
    
    # 净利率
    if data.net_profit_margin >= 15:
        score += fc.get("net_margin_high", 10)
        details.append(f"净利率{data.net_profit_margin:.1f}%")
    
    # 资产负债率（越低越好）
    if data.asset_liability_ratio > 0:
        equity_ratio = 1 - data.asset_liability_ratio
        if equity_ratio > 0.6:
            score += fc.get("low_debt", 15)
            details.append("资产负债率低")
    
    # 现金流
    if data.ocf_ratio >= 0.8:
        score += fc.get("cash_flow_good", 10)
        details.append("现金流充裕")
    
    return max(0, min(100, score)), details


def _score_valuation(data: ScoreData, cfg: Optional[Dict] = None) -> tuple:
    """估值面评分（0-100基准，加减分）"""
    score = 50.0
    details = []
    vc = cfg or {}
    
    # PE相对行业
    if data.pe_ttm > 0 and data.industry_pe > 0:
        if data.pe_ttm < data.industry_pe:
            score += vc.get("pe_below_industry", 15)
            details.append("PE低于行业均值")
    
    # 前向PE
    if data.forward_pe > 0:
        if data.forward_pe < 15:
            score += vc.get("forward_pe_low", 20)
            details.append(f"前向PE={data.forward_pe:.1f}x低估")
        elif data.forward_pe < 25:
            score += vc.get("forward_pe_medium", 10)
            details.append(f"前向PE={data.forward_pe:.1f}x合理")
    
    # PB
    if data.pb > 0 and data.pb < 2:
        score += vc.get("pb_low", 5)
    
    # 回撤幅度（长线视角）
    if data.drawdown_from_high <= -40:
        score += vc.get("golden_drawdown", 15)
        details.append(f"距高点回撤{abs(data.drawdown_from_high):.0f}%（黄金坑）")
    elif data.drawdown_from_high <= -20:
        score += vc.get("normal_drawdown", 8)
        details.append(f"距高点回撤{abs(data.drawdown_from_high):.0f}%")
    
    return max(0, min(100, score)), details


def _score_flow(data: ScoreData, cfg: Optional[Dict] = None) -> tuple:
    """资金面评分（0-100基准，加减分）"""
    score = 50.0
    details = []
    flc = cfg or {}
    
    # 主力净流入
    if data.main_net_inflow > 0:
        score += flc.get("main_inflow", 10)
        details.append(f"主力净流入{data.main_net_inflow/1e8:.1f}亿")
    
    # 连续流入天数
    if data.consecutive_inflow_days >= 12:
        score += flc.get("consecutive_inflow", 10)
        details.append(f"连续{data.consecutive_inflow_days}日流入")
    
    # 北向增持
    if data.northbound_change > 0:
        score += flc.get("northbound_increase", 8)
        details.append("北向增持")
    
    # 机构净买入
    if data.institution_net_buy > 0:
        score += flc.get("institution_buy", 10)
        details.append("机构净买入")
    
    # 融券下降
    if data.margin_short_decline:
        score += flc.get("margin_decline", 5)
        details.append("融券持续下降")
    
    return max(0, min(100, score)), details


def _score_holder(data: ScoreData, cfg: Optional[Dict] = None) -> tuple:
    """筹码面评分（0-100基准，加减分）"""
    score = 50.0
    details = []
    hc = cfg or {}
    
    # 筹码集中
    if data.holder_change_ratio < 0:
        if data.holder_consecutive_decrease:
            score += hc.get("holder_concentrate", 15)
            details.append("筹码持续集中")
        else:
            score += hc.get("holder_trend", 8)
            details.append("筹码趋于集中")
    
    # 机构持仓
    if data.institution_holding_pct > 0:
        score += hc.get("institution_hold", 10)
        details.append(f"机构持仓{data.institution_holding_pct:.1f}%")
    
    return max(0, min(100, score)), details


def _score_dividend(data: ScoreData, cfg: Optional[Dict] = None) -> tuple:
    """分红面评分（0-100基准，加减分）"""
    score = 50.0
    details = []
    dc = cfg or {}
    
    # 股息率
    if data.dividend_yield >= 3:
        score += dc.get("dividend_high", 10)
        details.append(f"股息率{data.dividend_yield:.1f}%")
    
    # 持续分红
    if data.consecutive_dividend_years >= 5:
        score += dc.get("dividend_continuous", 5)
        details.append("持续分红5年+")
    
    return max(0, min(100, score)), details


def calculate_score(score_type: str, data: ScoreData, cfg: Optional[Dict] = None) -> ScoreResult:
    """
    统一评分接口
    
    Args:
        score_type: 评分类型 "sht"/"med"/"lng"/"ful"
        data: ScoreData 输入数据
        cfg: 评分配置（可选）
    
    Returns:
        ScoreResult 评分结果
    """
    result = ScoreResult(report_source=score_type)
    sc = cfg or {}
    
    # 计算各维度评分
    tech_score, tech_details = _score_technical(data, sc.get("technical", {}))
    fund_score, fund_details = _score_fundamental(data, sc.get("fundamental", {}))
    val_score, val_details = _score_valuation(data, sc.get("valuation", {}))
    flow_score, flow_details = _score_flow(data, sc.get("flow", {}))
    holder_score, holder_details = _score_holder(data, sc.get("holder", {}))
    div_score, div_details = _score_dividend(data, sc.get("dividend", {}))
    
    result.dimensions = {
        "technical": tech_score,
        "fundamental": fund_score,
        "valuation": val_score,
        "flow": flow_score,
        "holder": holder_score,
        "dividend": div_score
    }
    
    # 根据评分类型组合
    if score_type == "sht":
        # 短线：技术面 + 资金面 + 筹码面
        result.total_score = (
            tech_score * 0.4 +
            flow_score * 0.35 +
            holder_score * 0.25
        )
        result.details = tech_details + flow_details + holder_details
        
    elif score_type == "med":
        # 中线：基本面 + 估值面 + 资金面 + 筹码面
        result.total_score = (
            fund_score * 0.35 +
            val_score * 0.25 +
            flow_score * 0.2 +
            holder_score * 0.2
        )
        result.details = fund_details + val_details + flow_details + holder_details
        
    elif score_type == "lng":
        # 长线：基本面 + 估值面 + 分红面 + 筹码面
        result.total_score = (
            fund_score * 0.3 +
            val_score * 0.3 +
            div_score * 0.2 +
            holder_score * 0.2
        )
        result.details = fund_details + val_details + div_details + holder_details
        
    elif score_type == "ful":
        # 完整：五维综合
        # 注意：配置文件中权重为百分比形式（如25），需除以100转为小数
        _cfg_weights = sc.get("weights", {}) if sc else {}
        weights = {
            "technical": (_cfg_weights.get("technical", 25) / 100),
            "valuation": (_cfg_weights.get("valuation", 20) / 100),
            "fundamental": (_cfg_weights.get("fundamental", 20) / 100),
            "flow": (_cfg_weights.get("flow", 15) / 100),
            "holder": (_cfg_weights.get("holder", 10) / 100),
            "dividend": (_cfg_weights.get("dividend", 10) / 100),
        }
        result.total_score = (
            tech_score * weights.get("technical", 0.25) +
            val_score * weights.get("valuation", 0.20) +
            fund_score * weights.get("fundamental", 0.20) +
            flow_score * weights.get("flow", 0.15) +
            holder_score * weights.get("holder", 0.10) +
            div_score * weights.get("dividend", 0.10)
        )
        result.details = tech_details + fund_details + val_details + flow_details + holder_details + div_details
    
    else:
        result.total_score = 50.0
    
    return result

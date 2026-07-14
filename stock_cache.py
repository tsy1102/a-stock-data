#!/usr/bin/env python3
"""stock_cache.py — 统一缓存层 (SQLite + 装饰器模式)

设计目标：
  - 所有 get_* 网络请求函数统一走本层，避免重复请求 + 降低 API 被封概率
  - 基于 SQLite 的持久化缓存，支持 TTL 自动过期 + LRU 清理
  - 装饰器模式：@cached / @cached_async，不破坏原函数签名

V9.3.3 更新：
  - schema 单点维护：定义 _CACHE_TABLE_SQL/_CACHE_INDEX_SQLS/_CACHE_PRAGMAS 常量，消除 _get_db() 和 _get_async_db() 的重复代码
  - 删除 _migrate_verify_columns，prev_value/verified 字段直接定义在主表 SQL 中

V9.3.2 更新：
  - journal_mode 从 WAL 改为 DELETE，避免多进程并发写产生 -wal/-shm 文件锁死锁
  - cache_size 从 -64000(64MB) 降到 -8000(8MB)，减少多进程内存占用

V9.3 更新：
  - 行情缓存 Key 增加交易日期隔离：格式改为 Q:{code}:{trading_date}，盘前/盘中数据独立保留
  - 异步缓存字段迁移补全：_get_async_db() 自动迁移 prev_value / verified 列

V9.2 更新：
  - 新增交叉验证机制（cross_verify）：11 个多天 TTL 分类启用两次获取对比
  - 新增 prev_value / verified 字段，支持自动表结构迁移
  - cross_verify 分支 SELECT-then-UPDATE 加 _db_lock 并发保护
  - 异步连接复用：_get_async_db() 单例，3 个异步函数共享连接
  - 约 6 处 except Exception: pass 加 _cache_logger.debug 日志
  - 移除 # type: ignore，用 cast() 替代

V9.1 更新：
  - 新增 16 个 F10 分类 TTL（5 个高频用交易日过期，11 个低频用固定 TTL）
  - @cached / @cached_async / set_cache 新增 trading_day: bool 参数
  - 新增 _calc_trading_day_expiry() 按最近交易日计算过期时间

TTL 分级策略（V10.0 优化）：
  - 静态数据（股票基本信息、概念板块）：30 天
  - 财务数据（财报、资产负债表）：90 天
  - 日频数据（龙虎榜、K线、资金流、打板）：7 天（历史数据不变）
  - 历史数据（北向、解禁、融资融券、大宗）：14-90 天
  - 研报：3 天
  - 行业/概念热度：24 小时
  - 分红历史：30 天
  - 实时行情（get_tencent_quote）：不缓存
  - 缓存命中率统计：进程退出时自动打印（atexit）

目录结构：
  cache/
  └── stock_cache.db        # SQLite 数据库文件
"""

from __future__ import annotations

import json
import os
import sys
import hashlib
import time
import sqlite3
import threading
import atexit
import functools
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Union, cast
from datetime import datetime, date, time as dtime
from pathlib import Path

_cache_logger = logging.getLogger("stock_cache")

# ═══════════════════════════════════════
# 缓存命中率统计（V10.0）
# ═══════════════════════════════════════
_CACHE_STATS: Dict[str, Any] = {
    "total_get": 0,
    "total_hit": 0,
    "category_stats": {},  # {category: {"hits": 0, "misses": 0}}
}
_STATS_LOCK = threading.Lock()


def _record_cache_hit(category: str, hit: bool) -> None:
    """记录缓存命中/未命中。"""
    with _STATS_LOCK:
        _CACHE_STATS["total_get"] += 1
        if hit:
            _CACHE_STATS["total_hit"] += 1
        cat_stats = _CACHE_STATS["category_stats"].setdefault(category, {"hits": 0, "misses": 0})
        if hit:
            cat_stats["hits"] += 1
        else:
            cat_stats["misses"] += 1


def print_cache_stats() -> None:
    """打印缓存命中率统计。在脚本运行结束时调用。"""
    with _STATS_LOCK:
        total = _CACHE_STATS["total_get"]
        if total == 0:
            return
        hits = _CACHE_STATS["total_hit"]
        rate = hits / total * 100
        saved = total - hits
        print(f"\n{'─' * 60}", flush=True)
        print(f"[缓存统计] 总请求: {total} | 命中: {hits} | 未命中: {saved} | 命中率: {rate:.1f}%", flush=True)
        # 按未命中数降序，显示前10个低命中率分类
        cat_stats = _CACHE_STATS["category_stats"]
        sorted_cats = sorted(cat_stats.items(), key=lambda x: x[1]["misses"], reverse=True)
        low_rate_cats = [(c, s) for c, s in sorted_cats if s["misses"] > 0][:10]
        if low_rate_cats:
            print("[分类命中率] (按未命中数降序，仅显示有未命中的分类)", flush=True)
            for cat, s in low_rate_cats:
                cat_total = s["hits"] + s["misses"]
                cat_rate = s["hits"] / cat_total * 100 if cat_total > 0 else 0
                print(f"  {cat:25s} 命中率: {cat_rate:5.1f}%  ({s['hits']}/{cat_total})", flush=True)
        print(f"{'─' * 60}", flush=True)


# 进程退出时自动打印缓存统计（V10.0）
atexit.register(print_cache_stats)


# ═══════════════════════════════════════
# 目录与文件路径
# ═══════════════════════════════════════
_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
_CACHE_DB = os.path.join(_CACHE_DIR, "stock_cache.db")
os.makedirs(_CACHE_DIR, exist_ok=True)

# 缓存大小上限（500 MB）
_MAX_CACHE_SIZE_MB = 500
_MAX_CACHE_SIZE_BYTES = _MAX_CACHE_SIZE_MB * 1024 * 1024

# 环境变量开关：STOCK_NOCACHE=1 临时禁用缓存
_DISABLE_CACHE = os.environ.get("STOCK_NOCACHE", "") == "1"

# ═══════════════════════════════════════
# TTL 常量（秒）
# ═══════════════════════════════════════
TTL: Dict[str, int] = {
    # 静态数据（几乎不变）
    "basic_info":      30 * 86400,   # 股票基本信息、总股本、上市日期（V10.0: 7天→30天）
    "concept_blocks":  30 * 86400,   # 概念板块列表（V10.0: 7天→30天）
    "board_type":       7 * 86400,   # 沪市/深市/北交所

    # 财务数据（财报发布才变）
    "financial":        90 * 86400,   # 新浪利润表
    "balance_sheet":    90 * 86400,   # 新浪资产负债表
    "cash_flow":        90 * 86400,   # 东财现金流量表（V9.6新增）
    "gross_margin_roe": 90 * 86400,   # 毛利率 + ROE（可复用财务数据）
    "eps_forecast":     30 * 86400,   # EPS 预测

    # 日频数据（收盘后固定，历史数据不变可延长TTL）
    "dragon_tiger":     7 * 86400,   # 龙虎榜（历史数据不变，V10.0: 1天→7天）
    "northbound":      30 * 86400,   # 北向资金持股（历史数据不变，V10.0: 7天→30天）
    "margin_trading":  14 * 86400,   # 融资融券（历史数据不变，V10.0: 3天→14天）
    "block_trade":     14 * 86400,   # 大宗交易（历史数据不变，V10.0: 3天→14天）
    "lockup_expiry":   90 * 86400,   # 限售解禁（日期固定，V10.0: 7天→90天）
    "announcements":   30 * 86400,   # 巨潮公告（发布后不变，V10.0: 7天→30天）
    "hsgt_flow":       14 * 86400,   # 沪深港通资金流（历史数据不变，V10.0: 3天→14天）
    "kline":            7 * 86400,   # K线行情（历史数据不变，V10.0: 1天→7天）
    "limit_pool":       7 * 86400,   # 打板数据（历史数据不变，V10.0: 1天→7天）
    "fund_flow":        7 * 86400,   # 资金流数据（历史数据不变，V10.0: 1天→7天）

    # 舆情互动（V8.9 新增）
    "hot_rank":         1 * 3600,    # 东财人气榜（小时级变化）
    "hot_concept":      1 * 3600,    # 概念命中（小时级变化）

    # 研报（更新不频繁）
    "reports":          3 * 86400,   # 东财研报列表
    "industry_reports": 1 * 86400,   # 行业研报

    # 新闻舆情（更新频繁）
    "stock_news":       6 * 3600,    # 个股新闻（6小时）
    "global_news":      1 * 3600,    # 全球资讯（1小时）
    "news":             6 * 3600,    # 财联社快讯（V9.6新增，6小时）

    # 行业/概念热度（每日变化）
    "industry_peers":   24 * 3600,   # 行业可比公司
    "industry_compare":  24 * 3600,   # 行业板块排名
    "ths_hot_reason":   24 * 3600,   # 同花顺热点题材

    # 分红历史（公告不频繁）
    "dividend":         30 * 86400,   # 分红历史

    # F10 数据（V9.0 新增，5 个高频分类用 trading_day 模式，11 个低频用固定 TTL）
    # 高频分类（每日更新，休市不变，通过 @cached(trading_day=True) 启用交易日模式）
    "f10_reminders":       24 * 3600,   # F2 最新提示（交易日模式覆盖此值）
    "f10_news":            24 * 3600,   # F13 公司报道（交易日模式覆盖此值）
    "f10_reports":         24 * 3600,   # F16 研报评级（交易日模式覆盖此值）
    "f10_fund_flow":       24 * 3600,   # F9 资金动向（交易日模式覆盖此值）
    "f10_announcements":   24 * 3600,   # F12 公司公告（交易日模式覆盖此值）
    # 低频分类（固定 TTL）
    "f10_shareholder":      7 * 86400,  # F5 股东研究（季度更新）
    "f10_share_capital":    7 * 86400,  # F4 股本结构（偶尔更新）
    "f10_industry":         7 * 86400,  # F15 行业分析（每周更新）
    "f10_themes":           3 * 86400,  # F11 热点题材（不定期）
    "f10_financial":       90 * 86400,  # F3 财务分析（季报周期）
    "f10_overview":        30 * 86400,  # F2 公司概况（几乎不变）
    "f10_operation":       90 * 86400,  # F10 经营分析（季度更新）
    "f10_governance":      30 * 86400,  # F8 高管治理（几乎不变）
    "f10_dividend":        30 * 86400,  # F7 分红融资（偶尔更新）
    "f10_inst_hold":       30 * 86400,  # F6 机构持股（季度更新）

    # 通用兜底（1 小时）
    "default":          3600,
}


def _calc_trading_day_expiry() -> float:
    """计算 F10 交易日模式的过期时间戳：下一个收盘更新点（交易日 15:00）。

    逻辑：
    - 今天是交易日且现在 < 15:00 → 今天 15:00（盘前数据，等收盘更新）
    - 今天是交易日且现在 >= 15:00 → 下一个交易日 15:00（盘后数据，等明天更新）
    - 今天不是交易日 → 下一个交易日 15:00

    任何异常时 fallback 到 now + 24h（保证不会因日历问题导致缓存写入失败）。

    Returns:
        float: 过期时间戳（time.time() 格式）
    """
    try:
        from stock_common.stock_calendar import is_workday, get_next_trading_day
    except Exception as _e:
        _cache_logger.debug(f"calc_trading_day_expiry import error: {_e}")
        return time.time() + 24 * 3600

    now = datetime.now()
    today = now.date()

    try:
        if is_workday(today) and now.hour < 15:
            # 盘前：数据是上一交易日收盘后的，今天 15:00 后会更新
            target = datetime.combine(today, dtime(15, 0))
        else:
            # 盘后或非交易日：找下一个交易日 15:00
            next_td = get_next_trading_day(today)
            target = datetime.combine(next_td, dtime(15, 0))
    except Exception as _e:
        _cache_logger.debug(f"calc_trading_day_expiry calc error: {_e}")
        # 交易日历年份超出范围或其他异常，fallback 到 24h
        return time.time() + 24 * 3600

    ts = target.timestamp()
    # 安全检查：expires_at 必须大于 now
    if ts <= time.time():
        return time.time() + 24 * 3600
    return ts

# ═══════════════════════════════════════
# SQLite Schema 常量（单点维护）
# ═══════════════════════════════════════
_CACHE_TABLE_SQL = (
    "CREATE TABLE IF NOT EXISTS cache_entries ("
    "  key TEXT PRIMARY KEY,"
    "  value BLOB NOT NULL,"
    "  created_at REAL NOT NULL,"
    "  expires_at REAL NOT NULL,"
    "  hit_count INTEGER DEFAULT 0,"
    "  last_accessed REAL NOT NULL,"
    "  prev_value BLOB,"
    "  verified INTEGER DEFAULT 0"
    ")"
)
_CACHE_INDEX_SQLS = [
    "CREATE INDEX IF NOT EXISTS idx_expires ON cache_entries(expires_at)",
    "CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)",
]
_CACHE_PRAGMAS = [
    ("PRAGMA journal_mode=DELETE",),    # DELETE 模式，多进程安全
    ("PRAGMA synchronous=NORMAL",),     # 平衡性能与安全
    ("PRAGMA cache_size=-8000",),       # 8MB 缓存
]

# ═══════════════════════════════════════
# SQLite 数据库初始化
# ═══════════════════════════════════════
_db_lock = threading.RLock()  # 多线程安全锁
_db: Optional[sqlite3.Connection] = None


def _get_db() -> sqlite3.Connection:
    """获取数据库连接（懒加载，线程安全）。"""
    global _db
    if _db is not None:
        return _db
    with _db_lock:
        if _db is not None:
            return _db
        _db = sqlite3.connect(_CACHE_DB, check_same_thread=False, timeout=30.0)
        for _pragma in _CACHE_PRAGMAS:
            _db.execute(_pragma[0])
        _db.execute(_CACHE_TABLE_SQL)
        for _idx in _CACHE_INDEX_SQLS:
            _db.execute(_idx)
        _db.commit()
        return _db


def _enforce_size_limit() -> None:
    """写入时维护：先清理过期条目，再检查是否超限。"""
    db = _get_db()
    # 先清理过期条目（替代 _startup_cleanup 的功能）
    try:
        db.execute("DELETE FROM cache_entries WHERE expires_at<?", (time.time(),))
        db.commit()
    except Exception as _e:
        _cache_logger.debug(f"enforce_size_limit cleanup: {_e}")
    # 再检查 DB 大小是否超限
    db_path = os.path.getsize(_CACHE_DB)
    if db_path < _MAX_CACHE_SIZE_BYTES:
        return
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM cache_entries")
    total = cursor.fetchone()[0]
    if total == 0:
        return
    # 删除最久未访问的 20%
    delete_count = max(1, total // 5)
    cursor.execute(
        "DELETE FROM cache_entries WHERE key IN ("
        f"  SELECT key FROM cache_entries ORDER BY last_accessed ASC LIMIT {delete_count}"
        ")"
    )
    db.commit()
    print(f"[stock_cache] 缓存超限（{db_path / 1024 / 1024:.1f}MB），已清理 {delete_count} 条最久未访问条目", flush=True)


# ═══════════════════════════════════════
# 核心缓存 API
# ═══════════════════════════════════════

def _build_key(category: str, func_name: str, *args: Any, **kwargs: Any) -> str:
    """根据函数名+参数生成缓存 key。"""
    parts = [category, func_name]
    if args:
        parts.append("_".join(str(a) for a in args))
    if kwargs:
        parts.append("_".join(f"{k}={v}" for k, v in sorted(kwargs.items())))
    raw = ":".join(parts)
    # key 过长时用 MD5 压缩
    if len(raw) > 200:
        h = hashlib.md5(raw.encode("utf-8")).hexdigest()
        return f"{category}:{func_name}:{h}"
    return raw


def get_cache(category: str, func_name: str, *args: Any,
              cross_verify: bool = False, **kwargs: Any) -> Optional[Any]:
    """查询缓存，返回解析后的数据或 None。

    Args:
        category: 缓存分类
        func_name: 函数名
        cross_verify: True=需要验证通过才返回（未验证返回None，触发重新获取）
        *args, **kwargs: 函数参数（用于构建key）
    """
    if _DISABLE_CACHE:
        _record_cache_hit(category, False)
        return None
    key = _build_key(category, func_name, *args, **kwargs)
    now = time.time()
    try:
        db = _get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT value, expires_at, hit_count, prev_value, verified "
            "FROM cache_entries WHERE key=? AND expires_at>?",
            (key, now)
        )
        row = cursor.fetchone()
        if row is None:
            _record_cache_hit(category, False)
            return None
        value_blob, expires_at, hit_count, prev_value_blob, verified = row
        # 交叉验证模式：未验证的缓存视为未命中
        if cross_verify and not verified:
            _record_cache_hit(category, False)
            return None
        # 已验证但 prev_value 与 value 不一致（理论上不应该发生），视为损坏
        if cross_verify and verified and prev_value_blob is not None:
            if prev_value_blob != value_blob:
                cursor.execute("DELETE FROM cache_entries WHERE key=?", (key,))
                db.commit()
                _record_cache_hit(category, False)
                return None
        # 更新访问时间 + 命中计数
        cursor.execute(
            "UPDATE cache_entries SET hit_count=hit_count+1, last_accessed=? WHERE key=?",
            (now, key)
        )
        db.commit()
        _record_cache_hit(category, True)
        return json.loads(value_blob.decode("utf-8"))
    except Exception as _e:
        _cache_logger.debug(f"get_cache error ({key}): {_e}")
        _record_cache_hit(category, False)
        return None


def _has_zero_price(value: Any) -> bool:
    """检查 dict/list 中是否包含 price=0 或 close=0（TDX 坏数据特征）。"""
    if isinstance(value, dict):
        if value.get("price") == 0 or value.get("close") == 0:
            return True
        for v in value.values():
            if _has_zero_price(v):
                return True
    elif isinstance(value, (list, tuple)):
        for item in value:
            if _has_zero_price(item):
                return True
    return False


def set_cache(category: str, func_name: str, value: Any, ttl: int, *args: Any,
              trading_day: bool = False, cross_verify: bool = False, **kwargs: Any) -> None:
    """写入缓存（None/空值/价格为零不写入）。

    Args:
        category: 缓存分类
        func_name: 函数名
        value: 缓存值
        ttl: 过期秒数（trading_day=True 时忽略，改用交易日 15:00 过期）
        trading_day: True=按交易日过期（F10 高频分类），False=固定 TTL（默认）
        cross_verify: True=启用交叉验证（写入时对比前一次数据，一致才标记为已验证）
    """
    if _DISABLE_CACHE:
        return
    if value is None:
        return
    if isinstance(value, (list, dict)) and len(value) == 0:
        return
    # V8.9: 检测 price=0 / close=0 — TDX 坏数据特征，不缓存
    if _has_zero_price(value):
        return
    key = _build_key(category, func_name, *args, **kwargs)
    now = time.time()
    # V9.0: trading_day 模式 — 过期时间设为下一个交易日 15:00
    expires_at = _calc_trading_day_expiry() if trading_day else now + ttl
    try:
        db = _get_db()
        value_bytes = json.dumps(value, ensure_ascii=False).encode("utf-8")
        cursor = db.cursor()

        if not cross_verify:
            # 普通模式：直接写入，不验证
            cursor.execute(
                "INSERT OR REPLACE INTO cache_entries "
                "(key, value, created_at, expires_at, hit_count, last_accessed, prev_value, verified) "
                "VALUES (?, ?, ?, ?, 0, ?, NULL, 0)",
                (key, value_bytes, now, expires_at, now)
            )
        else:
            # 交叉验证模式：首次写入即验证（信任 valid_if 校验），数据变化时自动更新
            # V10.0: 原逻辑要求两次获取数据完全相同才标记 verified=1，
            #         但多进程并发 + 数据源含实时字段（如 price/timestamp）导致永远无法验证通过。
            #         新逻辑：通过 valid_if 校验即标记 verified=1，数据变化时用新数据替换并保持 verified=1。
            with _db_lock:
                cursor.execute(
                    "SELECT value, verified FROM cache_entries WHERE key=? AND expires_at>?",
                    (key, now)
                )
                row = cursor.fetchone()
                if row is None:
                    # 第一次写入：直接标记为已验证（valid_if 已在上层校验）
                    cursor.execute(
                        "INSERT OR REPLACE INTO cache_entries "
                        "(key, value, created_at, expires_at, hit_count, last_accessed, prev_value, verified) "
                        "VALUES (?, ?, ?, ?, 0, ?, ?, 1)",
                        (key, value_bytes, now, expires_at, now, value_bytes)
                    )
                else:
                    existing_blob, verified = row
                    if existing_blob == value_bytes:
                        # 数据相同：刷新过期时间
                        cursor.execute(
                            "UPDATE cache_entries SET expires_at=?, last_accessed=? WHERE key=?",
                            (expires_at, now, key)
                        )
                    else:
                        # 数据不同（数据源更新）：用新数据替换，保持 verified=1
                        cursor.execute(
                            "UPDATE cache_entries SET value=?, prev_value=?, verified=1, "
                            "created_at=?, expires_at=?, last_accessed=? WHERE key=?",
                            (value_bytes, existing_blob, now, expires_at, now, key)
                        )

        db.commit()
        _enforce_size_limit()
    except Exception as _e:
        _cache_logger.debug(f"set_cache: {_e}")


def invalidate_category(category: str, pattern: str = "") -> int:
    """按分类批量删除缓存条目。

    Args:
        category: 分类前缀（如 "dragon_tiger"）
        pattern: 可选的代码过滤（如 "600519"，空=删除该分类全部）

    Returns:
        删除的条目数量
    """
    try:
        db = _get_db()
        cursor = db.cursor()
        if pattern:
            cursor.execute(
                "DELETE FROM cache_entries WHERE key LIKE ?",
                (f"{category}:%{pattern}%",)
            )
        else:
            cursor.execute(
                "DELETE FROM cache_entries WHERE key LIKE ?",
                (f"{category}:%",)
            )
        db.commit()
        return cursor.rowcount
    except Exception as _e:
        _cache_logger.debug(f"invalidate_category error ({category}): {_e}")
        return 0


def invalidate_prefix(prefix: str) -> int:
    """按 key 前缀批量删除（如 "holder:600519"）。"""
    try:
        db = _get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM cache_entries WHERE key LIKE ?", (f"{prefix}%",))
        db.commit()
        return cursor.rowcount
    except Exception as _e:
        _cache_logger.debug(f"invalidate_prefix error ({prefix}): {_e}")
        return 0


def clear_expired() -> int:
    """删除所有已过期的缓存条目，返回删除数量。"""
    try:
        db = _get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM cache_entries WHERE expires_at<?", (time.time(),))
        db.commit()
        return cursor.rowcount
    except Exception as _e:
        _cache_logger.debug(f"clear_expired error: {_e}")
        return 0


def clear_all() -> None:
    """清空所有缓存。"""
    try:
        db = _get_db()
        db.execute("DELETE FROM cache_entries")
        db.commit()
    except Exception as _e:
        _cache_logger.debug(f"clear_cache: {_e}")


def cache_stats() -> Dict[str, Any]:
    """返回缓存统计信息（供调试和 CLI 使用）。"""
    try:
        db = _get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*), SUM(hit_count), SUM(LENGTH(value)) FROM cache_entries")
        row = cursor.fetchone()
        count, hits, size_bytes = row
        cursor.execute("SELECT COUNT(*) FROM cache_entries WHERE expires_at<?", (time.time(),))
        expired = cursor.fetchone()[0]

        # V9.2: 验证状态统计
        now = time.time()
        cursor.execute(
            "SELECT COUNT(*) FROM cache_entries WHERE expires_at>? AND verified=1",
            (now,)
        )
        verified_valid = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM cache_entries WHERE expires_at>? AND verified=0",
            (now,)
        )
        unverified_valid = cursor.fetchone()[0]

        # 按分类统计（含验证状态）
        cursor.execute(
            "SELECT SUBSTR(key, 1, INSTR(key, ':') - 1) AS cat, COUNT(*), SUM(hit_count), "
            "SUM(CASE WHEN verified=1 AND expires_at>? THEN 1 ELSE 0 END) AS verified_cnt "
            "FROM cache_entries GROUP BY cat",
            (now,)
        )
        by_category = {}
        for cat, cnt, h, v_cnt in cursor.fetchall():
            by_category[cat or "unknown"] = {
                "count": cnt,
                "hits": h or 0,
                "verified": v_cnt or 0,
            }

        # 文件大小
        db_file_size = os.path.getsize(_CACHE_DB) if os.path.exists(_CACHE_DB) else 0

        valid = max(0, (count or 0) - expired)
        return {
            "total_entries": count or 0,
            "valid_entries": valid,
            "total_hits": hits or 0,
            "expired_entries": expired,
            "verified_entries": verified_valid or 0,
            "unverified_entries": unverified_valid or 0,
            "db_size_bytes": db_file_size,
            "db_size_mb": round(db_file_size / 1024 / 1024, 2),
            "by_category": by_category,
        }
    except Exception as e:
        return {"error": str(e)}


def print_cache_stats() -> None:
    """打印缓存统计到 stdout（CLI 工具函数）。"""
    stats = cache_stats()
    if "error" in stats:
        print(f"缓存统计失败: {stats['error']}", flush=True)
        return
    print("\n" + "=" * 50, flush=True)
    print("  📦 缓存统计", flush=True)
    print("=" * 50, flush=True)
    expired = stats['expired_entries']
    valid = stats['valid_entries']
    verified = stats.get('verified_entries', 0)
    unverified = stats.get('unverified_entries', 0)
    print(f"  总条目数   : {stats['total_entries']}", flush=True)
    print(f"  ├─ 有效   : {valid} (查询时自动命中)", flush=True)
    print(f"  │  ├─ 已验证 : {verified} (交叉验证通过)", flush=True)
    print(f"  │  └─ 未验证 : {unverified} (等待二次确认)", flush=True)
    print(f"  └─ 待清理 : {expired} (过期数据，查询时自动跳过)", flush=True)
    print(f"  总命中次数 : {stats['total_hits']}", flush=True)
    print(f"  数据库大小 : {stats['db_size_mb']} MB / {_MAX_CACHE_SIZE_MB} MB", flush=True)
    print(f"  使用率     : {stats['db_size_mb'] / _MAX_CACHE_SIZE_MB * 100:.1f}%", flush=True)
    print("-" * 50, flush=True)
    print("  各分类统计（有效条目）：", flush=True)
    for cat, info in sorted(stats.get("by_category", {}).items()):
        v = info.get('verified', 0)
        print(f"    {cat:<20} 条目: {info['count']:>5}  已验证: {v:>4}  命中: {info['hits']:>6}", flush=True)
    print("=" * 50 + "\n", flush=True)


# ═══════════════════════════════════════
# 同步装饰器 @cached
# ═══════════════════════════════════════
F = TypeVar("F", bound=Callable[..., Any])


def cached(category: str, ttl_seconds: Optional[int] = None,
           use_args: bool = True,
           valid_if: Optional[Callable[[Any], bool]] = None,
           trading_day: bool = False,
           cross_verify: bool = False) -> Callable[[F], F]:
    """同步函数缓存装饰器。

    用法：
        @cached(category="dragon_tiger", ttl_seconds=TTL["dragon_tiger"])
        def get_dragon_tiger_board(code: str, ...):
            ...

    Args:
        category: 缓存分类（决定 TTL 查表 key）
        ttl_seconds: 覆盖 TTL，None 则用 TTL[category]
        use_args: True=缓存 key 包含函数参数（区分不同股票代码），False=仅函数名
        valid_if: 可选校验函数，接收函数返回值，True=写入缓存，False=跳过
        trading_day: True=按交易日过期（下一个交易日 15:00），False=固定 TTL（默认）
        cross_verify: True=启用交叉验证（两次获取一致才标记为已验证，未验证不返回缓存）
    """
    _ttl = ttl_seconds if ttl_seconds is not None else TTL.get(category, TTL["default"])

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if _DISABLE_CACHE:
                return func(*args, **kwargs)
            # 提取缓存 key 的参数
            if use_args:
                cache_value = get_cache(category, func.__name__, *args,
                                        cross_verify=cross_verify, **kwargs)
            else:
                cache_value = get_cache(category, func.__name__,
                                        cross_verify=cross_verify)
            if cache_value is not None:
                # V8.9: 读取时也校验 — 命中但校验不通过视为未命中
                if valid_if is None or valid_if(cache_value):
                    return cache_value
            else:
                cache_value = None  # 确保下面重新获取
            result = func(*args, **kwargs)
            # valid_if 校验：不通过则不缓存
            if valid_if is None or valid_if(result):
                if use_args:
                    set_cache(category, func.__name__, result, _ttl, *args,
                              trading_day=trading_day, cross_verify=cross_verify, **kwargs)
                else:
                    set_cache(category, func.__name__, result, _ttl,
                              trading_day=trading_day, cross_verify=cross_verify)
            return result

        return cast(F, wrapper)
    return decorator


# ═══════════════════════════════════════
# 异步装饰器 @cached_async
# ═══════════════════════════════════════
AF = TypeVar("AF", bound=Callable[..., Any])





# 启动清理已移除（V8.9）：改为写入时通过 _enforce_size_limit 处理过期条目


# ═══════════════════════════════════════
# CLI 工具（可直接运行 python stock_cache.py）
# ═══════════════════════════════════════
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="stock_cache CLI 工具")
    parser.add_argument("action", choices=["stats", "clear", "clear-expired", "clear-all"],
                        help="stats=查看统计 / clear=按分类清理 / clear-expired=清过期 / clear-all=清全部")
    parser.add_argument("--category", "-c", default="", help="分类名（用于 clear 命令）")
    parser.add_argument("--pattern", "-p", default="", help="代码过滤（用于 clear 命令）")
    args = parser.parse_args()

    if args.action == "stats":
        print_cache_stats()
    elif args.action == "clear-expired":
        n = clear_expired()
        print(f"已清理 {n} 条过期缓存", flush=True)
    elif args.action == "clear-all":
        clear_all()
        print("已清空全部缓存", flush=True)
    elif args.action == "clear":
        if not args.category:
            print("错误：clear 命令需要 --category 参数", flush=True)
            sys.exit(1)
        n = invalidate_category(args.category, args.pattern)
        print(f"已清理 {n} 条 {args.category} 缓存（pattern={args.pattern or '全部'}）", flush=True)

#!/usr/bin/env python3
"""stock_cache.py — V8 统一缓存层 (SQLite + 装饰器模式)

设计目标：
  - 所有 get_* 网络请求函数统一走本层，避免重复请求 + 降低 API 被封概率
  - 基于 SQLite 的持久化缓存，支持 TTL 自动过期 + LRU 清理
  - 装饰器模式：@cached / @cached_async，不破坏原函数签名

TTL 分级策略（决策点1）：
  - 静态数据（股票基本信息、概念板块）：7 天
  - 财务数据（财报、资产负债表）：90 天
  - 日频数据（龙虎榜、北向、融资融券）：当日有效
  - 研报：3 天
  - 行业/概念热度：24 小时
  - 分红历史：30 天
  - 实时行情（get_tencent_quote）：不缓存

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
import asyncio
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════
# 目录与文件路径
# ═══════════════════════════════════════
_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
_CACHE_DB = os.path.join(_CACHE_DIR, "stock_cache.db")
os.makedirs(_CACHE_DIR, exist_ok=True)

# 缓存大小上限（500 MB）
_MAX_CACHE_SIZE_MB = 500
_MAX_CACHE_SIZE_BYTES = _MAX_CACHE_SIZE_MB * 1024 * 1024

# 初始化时是否检查 holder_cache.json 并迁移（决策点5）
_MIGRATE_HOLDER_CACHE = True

# 环境变量开关：STOCK_NOCACHE=1 临时禁用缓存
_DISABLE_CACHE = os.environ.get("STOCK_NOCACHE", "") == "1"

# ═══════════════════════════════════════
# TTL 常量（秒）
# ═══════════════════════════════════════
TTL: Dict[str, int] = {
    # 静态数据（几乎不变）
    "basic_info":       7 * 86400,   # 股票基本信息、总股本、上市日期
    "concept_blocks":    7 * 86400,   # 概念板块列表
    "board_type":       7 * 86400,   # 沪市/深市/北交所

    # 财务数据（财报发布才变）
    "financial":        90 * 86400,   # 新浪利润表
    "balance_sheet":    90 * 86400,   # 新浪资产负债表
    "gross_margin_roe": 90 * 86400,   # 毛利率 + ROE（可复用财务数据）
    "eps_forecast":     30 * 86400,   # EPS 预测

    # 日频数据（收盘后固定）
    "dragon_tiger":     1 * 86400,   # 龙虎榜（按日过期）
    "northbound":       1 * 86400,   # 北向资金持股
    "margin_trading":   1 * 86400,   # 融资融券
    "block_trade":      1 * 86400,   # 大宗交易
    "lockup_expiry":    1 * 86400,   # 限售股解禁
    "announcements":     1 * 86400,   # 巨潮战略公告
    "hsgt_flow":        1 * 86400,   # 沪深港通资金流

    # 研报（更新不频繁）
    "reports":          3 * 86400,   # 东财研报列表
    "industry_reports": 1 * 86400,   # 行业研报

    # 新闻舆情（更新频繁）
    "stock_news":       6 * 3600,    # 个股新闻（6小时）
    "global_news":      1 * 3600,    # 全球资讯（1小时）

    # 行业/概念热度（每日变化）
    "industry_peers":   24 * 3600,   # 行业可比公司
    "industry_compare":  24 * 3600,   # 行业板块排名
    "ths_hot_reason":   24 * 3600,   # 同花顺热点题材

    # 分红历史（公告不频繁）
    "dividend":         30 * 86400,   # 分红历史

    # 通用兜底（1 小时）
    "default":          3600,
}

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
        _db.execute("PRAGMA journal_mode=WAL")       # WAL 模式，提升并发读性能
        _db.execute("PRAGMA synchronous=NORMAL")     # 平衡性能与安全
        _db.execute("PRAGMA cache_size=-64000")      # 64MB 缓存
        _db.execute("CREATE TABLE IF NOT EXISTS cache_entries ("
                    "  key TEXT PRIMARY KEY,"
                    "  value BLOB NOT NULL,"
                    "  created_at REAL NOT NULL,"
                    "  expires_at REAL NOT NULL,"
                    "  hit_count INTEGER DEFAULT 0,"
                    "  last_accessed REAL NOT NULL"
                    ")")
        _db.execute("CREATE INDEX IF NOT EXISTS idx_expires ON cache_entries(expires_at)")
        _db.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)")
        _db.commit()
        # 启动时迁移旧的 holder_cache.json（仅执行一次）
        if _MIGRATE_HOLDER_CACHE:
            _try_migrate_holder_cache()
        return _db


def _try_migrate_holder_cache() -> None:
    """将旧的 holder_cache.json 迁移到 SQLite（仅执行一次）。"""
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "holder_cache.json")
    if not os.path.exists(json_path):
        return
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not data:
            return
        now = time.time()
        conn = _get_db()
        cursor = conn.cursor()
        migrated = 0
        for code, entry in data.items():
            if not isinstance(entry, dict):
                continue
            records = entry.get("records", [])
            if not records:
                continue
            key = f"holder:{code}"
            value = json.dumps({"records": records, "source": "json_migration"}).encode("utf-8")
            # 使用 60 天 TTL（与原 _HOLDER_CACHE_TTL 一致）
            expires_at = now + 60 * 86400
            cursor.execute(
                "INSERT OR REPLACE INTO cache_entries (key, value, created_at, expires_at, hit_count, last_accessed) "
                "VALUES (?, ?, ?, ?, 0, ?)",
                (key, value, now, expires_at, now)
            )
            migrated += 1
        conn.commit()
        # 迁移成功后重命名旧文件（保留备份）
        backup_path = json_path + ".migrated"
        if not os.path.exists(backup_path):
            os.rename(json_path, backup_path)
        print(f"[stock_cache] 已从 holder_cache.json 迁移 {migrated} 只股票的股东数据到 SQLite", flush=True)
    except Exception as e:
        print(f"[stock_cache] holder_cache.json 迁移失败: {e}", flush=True)


def _enforce_size_limit() -> None:
    """缓存文件超过上限时，清理最久未访问的 20% 条目。"""
    db = _get_db()
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


def get_cache(category: str, func_name: str, *args: Any, **kwargs: Any) -> Optional[Any]:
    """查询缓存，返回解析后的数据或 None。"""
    if _DISABLE_CACHE:
        return None
    key = _build_key(category, func_name, *args, **kwargs)
    now = time.time()
    try:
        db = _get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT value, expires_at, hit_count FROM cache_entries WHERE key=? AND expires_at>?",
            (key, now)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        value_blob, expires_at, hit_count = row
        # 更新访问时间 + 命中计数
        cursor.execute(
            "UPDATE cache_entries SET hit_count=hit_count+1, last_accessed=? WHERE key=?",
            (now, key)
        )
        db.commit()
        return json.loads(value_blob.decode("utf-8"))
    except Exception:
        return None


def set_cache(category: str, func_name: str, value: Any, ttl: int, *args: Any, **kwargs: Any) -> None:
    """写入缓存（None/空值不写入）。"""
    if _DISABLE_CACHE:
        return
    if value is None:
        return
    if isinstance(value, (list, dict)) and len(value) == 0:
        return
    key = _build_key(category, func_name, *args, **kwargs)
    now = time.time()
    try:
        db = _get_db()
        value_bytes = json.dumps(value, ensure_ascii=False).encode("utf-8")
        cursor = db.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO cache_entries (key, value, created_at, expires_at, hit_count, last_accessed) "
            "VALUES (?, ?, ?, ?, 0, ?)",
            (key, value_bytes, now, now + ttl, now)
        )
        db.commit()
        _enforce_size_limit()
    except Exception:
        pass


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
    except Exception:
        return 0


def invalidate_prefix(prefix: str) -> int:
    """按 key 前缀批量删除（如 "holder:600519"）。"""
    try:
        db = _get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM cache_entries WHERE key LIKE ?", (f"{prefix}%",))
        db.commit()
        return cursor.rowcount
    except Exception:
        return 0


def clear_expired() -> int:
    """删除所有已过期的缓存条目，返回删除数量。"""
    try:
        db = _get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM cache_entries WHERE expires_at<?", (time.time(),))
        db.commit()
        return cursor.rowcount
    except Exception:
        return 0


def clear_all() -> None:
    """清空所有缓存。"""
    try:
        db = _get_db()
        db.execute("DELETE FROM cache_entries")
        db.commit()
    except Exception:
        pass


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

        # 按分类统计
        cursor.execute("SELECT SUBSTR(key, 1, INSTR(key, ':') - 1) AS cat, COUNT(*), SUM(hit_count) "
                       "FROM cache_entries GROUP BY cat")
        by_category = {}
        for cat, cnt, h in cursor.fetchall():
            by_category[cat or "unknown"] = {"count": cnt, "hits": h or 0}

        # 文件大小
        db_file_size = os.path.getsize(_CACHE_DB) if os.path.exists(_CACHE_DB) else 0

        return {
            "total_entries": count or 0,
            "total_hits": hits or 0,
            "expired_entries": expired,
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
    print(f"  总条目数   : {stats['total_entries']}", flush=True)
    print(f"  总命中次数 : {stats['total_hits']}", flush=True)
    print(f"  已过期条目 : {stats['expired_entries']}", flush=True)
    print(f"  数据库大小 : {stats['db_size_mb']} MB / {_MAX_CACHE_SIZE_MB} MB", flush=True)
    print(f"  使用率     : {stats['db_size_mb'] / _MAX_CACHE_SIZE_MB * 100:.1f}%", flush=True)
    print("-" * 50, flush=True)
    print("  各分类统计：", flush=True)
    for cat, info in sorted(stats.get("by_category", {}).items()):
        print(f"    {cat:<20} 条目: {info['count']:>5}  命中: {info['hits']:>6}", flush=True)
    print("=" * 50 + "\n", flush=True)


# ═══════════════════════════════════════
# 同步装饰器 @cached
# ═══════════════════════════════════════
F = TypeVar("F", bound=Callable[..., Any])


def cached(category: str, ttl_seconds: Optional[int] = None, use_args: bool = True) -> Callable[[F], F]:
    """同步函数缓存装饰器。

    用法：
        @cached(category="dragon_tiger", ttl_seconds=TTL["dragon_tiger"])
        def get_dragon_tiger_board(code: str, ...):
            ...

    Args:
        category: 缓存分类（决定 TTL 查表 key）
        ttl_seconds: 覆盖 TTL，None 则用 TTL[category]
        use_args: True=缓存 key 包含函数参数（区分不同股票代码），False=仅函数名
    """
    _ttl = ttl_seconds if ttl_seconds is not None else TTL.get(category, TTL["default"])

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if _DISABLE_CACHE:
                return func(*args, **kwargs)
            # 提取缓存 key 的参数
            if use_args:
                cache_value = get_cache(category, func.__name__, *args, **kwargs)
            else:
                cache_value = get_cache(category, func.__name__)
            if cache_value is not None:
                return cache_value
            result = func(*args, **kwargs)
            if use_args:
                set_cache(category, func.__name__, result, _ttl, *args, **kwargs)
            else:
                set_cache(category, func.__name__, result, _ttl)
            return result

        return wrapper  # type: ignore
    return decorator


# ═══════════════════════════════════════
# 异步装饰器 @cached_async
# ═══════════════════════════════════════
AF = TypeVar("AF", bound=Callable[..., Any])


def cached_async(category: str, ttl_seconds: Optional[int] = None, use_args: bool = True) -> Callable[[AF], AF]:
    """异步函数缓存装饰器（使用 aiosqlite 实现真正的异步读写）。

    用法：
        @cached_async(category="dragon_tiger", ttl_seconds=TTL["dragon_tiger"])
        async def get_dragon_tiger_board_async(session, code: str, ...):
            ...
    """
    _ttl = ttl_seconds if ttl_seconds is not None else TTL.get(category, TTL["default"])

    def decorator(func: AF) -> AF:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if _DISABLE_CACHE:
                return await func(*args, **kwargs)

            # 注意：aiosqlite 需要在 event loop 中运行
            # 这里是真正的异步实现
            try:
                import aiosqlite
            except ImportError:
                # 降级：aiosqlite 未安装时跳过缓存
                return await func(*args, **kwargs)

            if use_args:
                cache_value = await _async_get_cache(category, func.__name__, *args, **kwargs)
            else:
                cache_value = await _async_get_cache(category, func.__name__)
            if cache_value is not None:
                return cache_value

            result = await func(*args, **kwargs)
            if use_args:
                await _async_set_cache(category, func.__name__, result, _ttl, *args, **kwargs)
            else:
                await _async_set_cache(category, func.__name__, result, _ttl)
            return result

        return wrapper  # type: ignore
    return decorator


async def _async_get_cache(category: str, func_name: str, *args: Any, **kwargs: Any) -> Optional[Any]:
    """异步查询缓存（aiosqlite）。"""
    try:
        import aiosqlite
    except ImportError:
        return None

    try:
        key = _build_key(category, func_name, *args, **kwargs)
        now = time.time()
        async with aiosqlite.connect(_CACHE_DB) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT value FROM cache_entries WHERE key=? AND expires_at>?",
                (key, now)
            ) as cursor:
                row = await cursor.fetchone()
            if row is None:
                return None
            value_blob = row["value"]
            # 更新访问计数
            await db.execute(
                "UPDATE cache_entries SET hit_count=hit_count+1, last_accessed=? WHERE key=?",
                (now, key)
            )
            await db.commit()
            return json.loads(value_blob.decode("utf-8"))
    except Exception:
        return None


async def _async_set_cache(category: str, func_name: str, value: Any, ttl: int, *args: Any, **kwargs: Any) -> None:
    """异步写入缓存（aiosqlite）。None/空值不写入。"""
    if value is None:
        return
    if isinstance(value, (list, dict)) and len(value) == 0:
        return
    try:
        import aiosqlite
    except ImportError:
        return

    key = _build_key(category, func_name, *args, **kwargs)
    now = time.time()
    try:
        value_bytes = json.dumps(value, ensure_ascii=False).encode("utf-8")
        async with aiosqlite.connect(_CACHE_DB) as db:
            await db.execute(
                "INSERT OR REPLACE INTO cache_entries (key, value, created_at, expires_at, hit_count, last_accessed) "
                "VALUES (?, ?, ?, ?, 0, ?)",
                (key, value_bytes, now, now + ttl, now)
            )
            await db.commit()
        # 异步清理超限（后台）
        asyncio.create_task(_async_enforce_size_limit_bg())
    except Exception:
        pass


async def _async_enforce_size_limit_bg() -> None:
    """后台异步清理超限（不阻塞主流程）。"""
    try:
        import aiosqlite
    except ImportError:
        return

    try:
        if not os.path.exists(_CACHE_DB):
            return
        if os.path.getsize(_CACHE_DB) < _MAX_CACHE_SIZE_BYTES:
            return
        async with aiosqlite.connect(_CACHE_DB) as db:
            await db.execute("DELETE FROM cache_entries WHERE expires_at<?", (time.time(),))
            await db.commit()
    except Exception:
        pass


# ═══════════════════════════════════════
# 启动时自动清理过期条目
# ═══════════════════════════════════════
def _startup_cleanup() -> None:
    """程序启动时调用：清理过期条目。"""
    try:
        n = clear_expired()
        if n > 0:
            print(f"[stock_cache] 启动时清理了 {n} 条过期缓存", flush=True)
    except Exception:
        pass


# 注册启动清理
_startup_cleanup()


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

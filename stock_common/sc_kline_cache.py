"""sc_kline_cache.py — 跨进程 K 线磁盘缓存（V14.3 P3 + V14.3.1 增强）

解决问题：
  - val 报告周日首次运行时 1000+ 次 TDX TCP 请求导致 15 分钟卡死
  - 进程级缓存（_TDX_KLINE_CACHE）重启后失效
  - TDX TCP 节点在休市日可能超时

方案：
  - 将 K 线数据序列化到本地磁盘（pickle）
  - 缓存 key: f"{period}:{code}:{count}"
  - TTL: 24 小时（T+1 数据稳定后不再变化）
  - 缓存目录: <repo_root>/.cache/kline/

V14.3.1 增强（缓存失效机制）：
  - 启动清理：模块导入时自动清理 24h+ 过期文件
  - 总大小限制：>500MB 时按 mtime 升序 LRU 清理
  - 定期检查：每次写入前检查大小，必要时清理
  - 手动接口：clear_expired() / enforce_size_limit()

使用：
  from stock_common.sc_kline_cache import get_cached_kline, set_cached_kline
  cached = get_cached_kline("D", "600519", 800)
  if cached is not None:
      return cached
  # 否则从网络获取后：
  set_cached_kline("D", "600519", 800, (keys, rows))
"""
from __future__ import annotations

import os
import pickle
import threading
import time
from pathlib import Path
from typing import Any, Optional, Tuple


# ═══════════════════════════════════════
# 缓存配置
# ═══════════════════════════════════════

# 缓存 TTL：24 小时（T+1 数据稳定后不再变化）
CACHE_TTL_SECONDS = 86400

# V14.3.1: 缓存总大小上限（500 MB）
CACHE_SIZE_LIMIT_BYTES = 500 * 1024 * 1024

# V14.3.1: 每次写入后检查大小，超限时清理到的目标大小（400 MB）
CACHE_SIZE_TARGET_BYTES = 400 * 1024 * 1024

# V14.3.1: 锁（pickle 文件操作并发安全）
_cache_lock = threading.Lock()


# ═══════════════════════════════════════
# 路径与目录
# ═══════════════════════════════════════

def _get_cache_dir() -> Path:
    """获取 K 线缓存目录。

    V16.3 O23: 统一到 cache/kline/（原 .cache/kline 为 V14.3 隐藏目录设计遗留，
    与主缓存 cache/ 不一致——已迁移现有缓存文件）。
    """
    repo_root = Path(__file__).parent.parent.resolve()
    cache_dir = repo_root / "cache" / "kline"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


_KLINE_CACHE_SCHEMA_VERSION = "v2"  # V16.2: schema 版本（数据格式/列变更时 +1，旧缓存自动失效）


def _cache_path(period: str, code: str, count: int) -> Path:
    """生成缓存文件路径。V16.2: 键含 schema 版本，避免旧结构缓存被静默复用。"""
    return _get_cache_dir() / f"{period}_{code}_{count}_{_KLINE_CACHE_SCHEMA_VERSION}.pkl"


# ═══════════════════════════════════════
# V14.3.1: 启动清理（模块导入时执行一次）
# ═══════════════════════════════════════

def clear_expired() -> int:
    """V14.3.1: 清理过期缓存（mtime > TTL_SECONDS）。

    Returns:
        清理的文件数
    """
    try:
        cache_dir = _get_cache_dir()
        now = time.time()
        cleared = 0
        for p in cache_dir.glob("*.pkl"):
            try:
                if now - p.stat().st_mtime > CACHE_TTL_SECONDS:
                    p.unlink()
                    cleared += 1
            except Exception:
                pass
        return cleared
    except Exception:
        return 0


def enforce_size_limit() -> int:
    """V14.3.1: 强制执行缓存大小限制。

    当总大小 > CACHE_SIZE_LIMIT_BYTES 时，按 mtime 升序（最旧优先）删除，
    直到总大小 < CACHE_SIZE_TARGET_BYTES。

    Returns:
        清理的文件数
    """
    try:
        cache_dir = _get_cache_dir()
        files = [(p, p.stat().st_mtime, p.stat().st_size) for p in cache_dir.glob("*.pkl")]
        total_size = sum(f[2] for f in files)
        if total_size <= CACHE_SIZE_LIMIT_BYTES:
            return 0
        # 按 mtime 升序（最旧优先）
        files.sort(key=lambda x: x[1])
        target = CACHE_SIZE_TARGET_BYTES
        cleared = 0
        current_size = total_size
        for p, mtime, size in files:
            if current_size <= target:
                break
            try:
                p.unlink()
                current_size -= size
                cleared += 1
            except Exception:
                pass
        return cleared
    except Exception:
        return 0


# V14.3.1: 模块导入时自动清理过期文件（一次）
try:
    _initial_cleared = clear_expired()
    if _initial_cleared > 0:
        import sys
        _dbg = "V14.3.1 sc_kline_cache: cleared %d expired files on init" % _initial_cleared
        # 静默清理，仅在 DEBUG 模式可见
        if os.environ.get("STOCK_CACHE_DEBUG"):
            print(_dbg, file=sys.stderr)
except Exception:
    pass


# ═══════════════════════════════════════
# 核心接口
# ═══════════════════════════════════════

def get_cached_kline(period: str, code: str, count: int) -> Optional[Tuple[list, list]]:
    """V14.3 P3: 读取跨进程 K 线缓存。

    Args:
        period: "D" 日线 / "W" 周线 / "Q" 行情
        code: 股票代码
        count: K 线根数

    Returns:
        (keys, rows) 元组，缓存不存在或已过期返回 None
    """
    with _cache_lock:
        try:
            p = _cache_path(period, code, count)
            if not p.exists():
                return None
            # 检查 TTL
            mtime = p.stat().st_mtime
            if time.time() - mtime > CACHE_TTL_SECONDS:
                try:
                    p.unlink()  # 过期清理
                except Exception:
                    pass
                return None
            with open(p, "rb") as f:
                return pickle.load(f)
        except Exception:
            return None


def set_cached_kline(period: str, code: str, count: int, data: Tuple[list, list]) -> None:
    """V14.3 P3: 写入跨进程 K 线缓存。

    V14.3.1: 写入后检查总大小，超限时 LRU 清理。

    Args:
        period: "D" 日线 / "W" 周线 / "Q" 行情
        code: 股票代码
        count: K 线根数
        data: (keys, rows) 元组
    """
    with _cache_lock:
        try:
            p = _cache_path(period, code, count)
            # V16.2: 原子写（临时文件 + os.replace，避免其他进程读到半写入文件）
            tmp = p.with_suffix(".pkl.tmp")
            with open(tmp, "wb") as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            try:
                os.replace(tmp, p)
            except OSError:
                tmp.unlink(missing_ok=True)
            # V14.3.1: 写入后检查总大小（异步线程友好，不阻塞主流程）
            # 仅在缓存大小可能接近上限时检查（每 100 次写入检查一次）
            enforce_size_limit()
        except Exception:
            pass  # 缓存写入失败不阻塞主流程


def clear_kline_cache(period: Optional[str] = None) -> int:
    """V14.3 P3: 清理 K 线缓存。

    Args:
        period: 指定周期（"D"/"W"/"Q"），None 清理全部

    Returns:
        清理的文件数
    """
    with _cache_lock:
        try:
            cache_dir = _get_cache_dir()
            if period is None:
                pattern = "*.pkl"
            else:
                pattern = f"{period}_*.pkl"
            cleared = 0
            for p in cache_dir.glob(pattern):
                try:
                    p.unlink()
                    cleared += 1
                except Exception:
                    pass
            return cleared
        except Exception:
            return 0


def get_cache_stats() -> dict:
    """V14.3 P3 + V14.3.1: 返回缓存统计信息（用于调试/监控）。"""
    try:
        cache_dir = _get_cache_dir()
        all_files = list(cache_dir.glob("*.pkl"))
        d_files = [f for f in all_files if f.name.startswith("D_")]
        w_files = [f for f in all_files if f.name.startswith("W_")]
        total_size = sum(f.stat().st_size for f in all_files)
        return {
            "total_files": len(all_files),
            "d_files": len(d_files),
            "w_files": len(w_files),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "size_limit_mb": CACHE_SIZE_LIMIT_BYTES / 1024 / 1024,
            "size_target_mb": CACHE_SIZE_TARGET_BYTES / 1024 / 1024,
            "ttl_seconds": CACHE_TTL_SECONDS,
            "cache_dir": str(cache_dir),
        }
    except Exception:
        return {}


__all__ = [
    "get_cached_kline",
    "set_cached_kline",
    "clear_kline_cache",
    "clear_expired",
    "enforce_size_limit",
    "get_cache_stats",
    "CACHE_TTL_SECONDS",
    "CACHE_SIZE_LIMIT_BYTES",
    "CACHE_SIZE_TARGET_BYTES",
]

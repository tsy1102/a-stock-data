"""sc_kline_cache.py — 跨进程 K 线磁盘缓存（V14.3 P3 + V14.3.1 增强）

解决问题：
  - val 报告周日首次运行时 1000+ 次 TDX TCP 请求导致 15 分钟卡死
  - 进程级缓存（_TDX_KLINE_CACHE）重启后失效
  - TDX TCP 节点在休市日可能超时

方案：
  - 将 K 线数据序列化到本地磁盘（pickle）
  - 缓存 key: f"{period}:{code}:{count}"
   - 有效期：按项目交易日历到下一数据交易日 09:30；日历不可用时回退 24 小时
  - 缓存目录: <repo_root>/.cache/kline/

V14.3.1 增强（缓存失效机制）：
   - 启动清理：模块导入时扫描已超过 24 小时的文件，并按封套中的交易日失效时间清理
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
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional, Tuple

# ═══════════════════════════════════════
# 缓存配置
# ═══════════════════════════════════════

# 旧格式缓存回收与交易日历异常时的兜底窗口；新缓存按交易日 09:30 过期。
CACHE_TTL_SECONDS = 86400

# V14.3.1: 缓存总大小上限（500 MB）
CACHE_SIZE_LIMIT_BYTES = 500 * 1024 * 1024

# V14.3.1: 每次写入后检查大小，超限时清理到的目标大小（400 MB）
CACHE_SIZE_TARGET_BYTES = 400 * 1024 * 1024

# V14.3.1: 锁（pickle 文件操作并发安全）
_cache_lock = threading.RLock()


def _debug_log(msg: str) -> None:
    """V17.0.25: 调试日志（仅 STOCK_CACHE_DEBUG 环境变量置位时输出, 避免污染正常输出）。"""
    if os.environ.get("STOCK_CACHE_DEBUG"):
        try:
            print(f"[sc_kline_cache] {msg}", file=sys.stderr)
        except Exception:
            pass


# ═══════════════════════════════════════
# V17.0.25(2026-09-03): 非空守卫（实现项目铁律"只缓存非空结果"）
# ═══════════════════════════════════════
# 背景：em_get 等网络层只有令牌桶+熔断、无任何数据缓存；新接口须自加缓存(sc_kline_cache),
# 否则 N 倍请求打挂 push2 连接级风控（字典 §12.3 实测恢复 20+ 小时）。但若把"空/失败结果"
# 也写进磁盘, 会被后续缓存有效期内的调用命中并当作"有效空数据"返回 → 投毒 + 掩盖源故障。
# 故写入前强制校验非空, 空结果直接丢弃(不写盘, 调用方回退到网络重取)。


def _kline_is_non_empty(data: Any) -> bool:
    """K线数据 (keys, rows) 是否可缓存（非空）。"""
    if not isinstance(data, (tuple, list)) or len(data) != 2:
        return False
    keys, rows = data[0], data[1]
    if not isinstance(keys, (list, tuple)) or not isinstance(rows, (list, tuple)):
        return False
    return len(keys) > 0 and len(rows) > 0


def _blob_is_non_empty(data: Any) -> bool:
    """通用 blob（CYQ 等）是否可缓存（非空）。"""
    if data is None:
        return False
    if isinstance(data, (dict, list, tuple, str)):
        return len(data) > 0
    # 其他标量类型（int/float/bool）视为非空可缓存
    return True


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


_KLINE_CACHE_SCHEMA_VERSION = "v3"  # V17.4.65: 缓存封套增加交易日过期时间
_CACHE_ENVELOPE_KEY = "__stock_cache_envelope__"


def _cache_path(period: str, code: str, count: int) -> Path:
    """生成缓存文件路径。V16.2: 键含 schema 版本，避免旧结构缓存被静默复用。"""
    return _get_cache_dir() / f"{period}_{code}_{count}_{_KLINE_CACHE_SCHEMA_VERSION}.pkl"


def _cache_expiry() -> float:
    """使用项目交易日历设置下一数据交易日 09:30 的失效点。"""
    try:
        from core.stock_cache import _calc_trading_day_expiry

        return _calc_trading_day_expiry()
    except Exception as _e:
        _debug_log(f"cache expiry calendar fallback: {_e}")
        return time.time() + CACHE_TTL_SECONDS


def _cache_envelope(data: Any) -> dict:
    """封装缓存值及其绝对过期时间，数据值本身保持原有调用契约。"""
    return {
        _CACHE_ENVELOPE_KEY: _KLINE_CACHE_SCHEMA_VERSION,
        "expires_at": _cache_expiry(),
        "payload": data,
    }


def _read_cache_envelope(path: Path) -> Optional[Tuple[Any, float]]:
    """读取新格式缓存封套；旧格式或损坏值一律视为缓存未命中。"""
    try:
        with open(path, "rb") as cache_file:
            entry = pickle.load(cache_file)
    except Exception:
        return None
    if not isinstance(entry, dict) or entry.get(_CACHE_ENVELOPE_KEY) != _KLINE_CACHE_SCHEMA_VERSION:
        return None
    expires_at = entry.get("expires_at")
    if not isinstance(expires_at, (int, float)):
        return None
    return entry.get("payload"), float(expires_at)


# ═══════════════════════════════════════
# V14.3.1: 启动清理（模块导入时执行一次）
# ═══════════════════════════════════════


def clear_expired() -> int:
    """清理过期缓存；长周末内仍有效的交易日缓存会保留。

    Returns:
        清理的文件数
    """
    with _cache_lock:
        try:
            cache_dir = _get_cache_dir()
            now = time.time()
            cleared = 0
            for p in cache_dir.glob("*.pkl"):
                try:
                    # 最近 24 小时的文件无需启动扫描：读取入口会按封套中的
                    # expires_at 拒绝并删除过期项，避免每次导入遍历/反序列化热缓存。
                    if now - p.stat().st_mtime <= CACHE_TTL_SECONDS:
                        continue
                    envelope = _read_cache_envelope(p)
                    # 文件年龄只限制清理扫描成本；有效性始终以封套时间为准。
                    expired = envelope is None or envelope[1] <= now
                    if expired:
                        p.unlink()
                        cleared += 1
                except Exception:
                    continue
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
    with _cache_lock:
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
            entry = _read_cache_envelope(p)
            if entry is None:
                return None
            data, expires_at = entry
            if time.time() >= expires_at:
                try:
                    p.unlink()  # 过期清理
                except Exception:
                    pass
                return None
            if not isinstance(data, tuple) or len(data) != 2:
                return None
            keys, rows = data
            if not isinstance(keys, list) or not isinstance(rows, list):
                return None
            return keys, rows
        except Exception:
            return None


def set_cached_kline(period: str, code: str, count: int, data: Tuple[list, list]) -> None:
    """V14.3 P3: 写入跨进程 K 线缓存。

    V14.3.1: 写入后检查总大小，超限时 LRU 清理。
    V17.0.25(2026-09-03): 写入前强制非空校验——空/失败结果不写盘（项目铁律"只缓存非空结果"），
        避免空数据投毒缓存有效期并掩盖源故障（调用方应回退网络重取）。

    Args:
        period: "D" 日线 / "W" 周线 / "Q" 行情
        code: 股票代码
        count: K 线根数
        data: (keys, rows) 元组
    """
    if not _kline_is_non_empty(data):
        _debug_log(f"sc_kline_cache: 跳过空 K线缓存 {period}:{code}:{count}（非空守卫）")
        return
    with _cache_lock:
        try:
            p = _cache_path(period, code, count)
            # 临时名含 PID/线程号，避免多个进程同时写同一条目时抢用同一 .tmp 文件。
            tmp = p.with_name(f"{p.name}.{os.getpid()}.{threading.get_ident()}.tmp")
            with open(tmp, "wb") as f:
                pickle.dump(_cache_envelope(data), f, protocol=pickle.HIGHEST_PROTOCOL)
            try:
                os.replace(tmp, p)
            except OSError:
                try:
                    tmp.unlink()
                except FileNotFoundError:
                    pass
            # V14.3.1: 写入后检查总大小（异步线程友好，不阻塞主流程）
            # 仅在缓存大小可能接近上限时检查（每 100 次写入检查一次）
            enforce_size_limit()
        except Exception:
            pass  # 缓存写入失败不阻塞主流程


# ═══════════════════════════════════════
# V17.0.15: 通用对象缓存（非 K 线数据）
# ═══════════════════════════════════════


def get_cached_blob(period: str, code: str, count: int) -> Optional[Any]:
    """V17.0.15: 通用跨进程缓存读取——**任意可 pickle 对象**（如 CYQ 结果 dict）。

    为什么单独开一对接口而不是直接复用 get_cached_kline：
      后者的签名与 docstring 都绑定 TDX K 线语义（返回 `Tuple[list, list]` 的
      (keys, rows)），拿它存 dict 虽能跑但会误导维护者。本接口机制完全相同
      （同一交易日失效点 / 同一 LRU 500MB / 同一原子写 / 同一锁），仅放宽类型约束。

    首要用途（V17.0.15 审查发现）：`get_cyq_distribution` 走东财 push2 kline，
    而 `em_get` **只有令牌桶限流与熔断、没有任何数据缓存** —— 未加缓存前，
    全仓扫描时 sht/med/lng 三脚本各调一次 → **3N 次东财请求**。东财 push2 系是
    **连接级风控**（RemoteDisconnected，字典 §12.3 实测恢复 20+ 小时），风险极高。
    CYQ 依赖的 240 根日K+换手率属 T+1 稳定数据，与 K 线同性质，故按同一交易日规则缓存。

    Args:
        period: 命名空间。当前**实际在用**的只有 `"CYQ"`（筹码分布）；
            另有 `"D"`/"60" 等由 `get_cached_kline` 使用的日K命名空间（同一目录，
            但走 K线专用接口）。
            ⚠️ **"PAT"（K线形态）不是生产命名空间，勿据此认为已接入形态缓存**：
            `get_kline_patterns` 是**纯本地 CPU 计算**（TA-Lib，输入为已缓存的
            60 根日K），本身无网络请求，再缓存一次属冗余。
            "PAT" 仅出现在 `tests/core/test_core_blob_cache.py` 中，作为
            **与 CYQ 不同的第二个命名空间**来验证隔离性——是测试夹具，勿删，
            也不要把生产代码指向它。此处澄清是为避免误判"形态已缓存"
            而漏掉真正的网络热点。
        code: 股票代码
        count: 业务参数（CYQ = 换手窗口天数；K线 = 根数）

    Returns:
        pickle 对象；缓存不存在 / 已过期 / 损坏 → None（调用方应回退到网络请求）
    """
    with _cache_lock:
        try:
            p = _cache_path(period, code, count)
            if not p.exists():
                return None
            entry = _read_cache_envelope(p)
            if entry is None:
                return None
            data, expires_at = entry
            if time.time() >= expires_at:
                try:
                    p.unlink()
                except Exception:
                    pass
                return None
            return data
        except Exception:
            return None


def set_cached_blob(period: str, code: str, count: int, data: Any) -> None:
    """V17.0.15: 通用跨进程缓存写入（配套 get_cached_blob，失败静默不阻塞主流程）。

    V17.0.25(2026-09-03): 写入前强制非空校验——空/失败结果不写盘（项目铁律"只缓存非空结果"）。
    """
    if not _blob_is_non_empty(data):
        _debug_log(f"sc_kline_cache: 跳过空 blob 缓存 {period}:{code}:{count}（非空守卫）")
        return
    with _cache_lock:
        try:
            p = _cache_path(period, code, count)
            tmp = p.with_name(f"{p.name}.{os.getpid()}.{threading.get_ident()}.tmp")
            with open(tmp, "wb") as f:
                pickle.dump(_cache_envelope(data), f, protocol=pickle.HIGHEST_PROTOCOL)
            try:
                os.replace(tmp, p)
            except OSError:
                try:
                    tmp.unlink()
                except FileNotFoundError:
                    pass
            enforce_size_limit()
        except Exception:
            pass


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
        with _cache_lock:
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
    # V17.0.15: 通用对象缓存（CYQ / 形态等非 K 线数据）
    "get_cached_blob",
    "set_cached_blob",
    "clear_kline_cache",
    "clear_expired",
    "enforce_size_limit",
    "get_cache_stats",
    "CACHE_TTL_SECONDS",
    "CACHE_SIZE_LIMIT_BYTES",
    "CACHE_SIZE_TARGET_BYTES",
]

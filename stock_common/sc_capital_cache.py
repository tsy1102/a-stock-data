#!/usr/bin/env python3
"""sc_capital_cache.py — 全局股本缓存层（总股本/流通股 + 市值计算）

设计目标：
  - 股本数据（总股本、流通股）属于极低频变动数据，长TTL缓存
  - 全局JSON文件缓存 + SQLite双层缓存，加载速度极快
  - 市值 = 收盘价 × 总股本，纯内存计算，零网络请求

V10.1 新增：
    - 全局股本缓存文件（cache/share_capital.json）
    - 被动累积式构建（脚本运行时逐步填充）
    - 市值内存计算（price × total_shares）
"""

from __future__ import annotations

import json
import math
import os
import threading
from typing import Any, Dict, Optional
from datetime import date, datetime

from core.stock_cache import cached


def _debug_log(msg: str) -> None:
    try:
        from stock_common.sc_network import _fallback_logger

        _fallback_logger.debug(msg)
    except Exception:
        pass


_CAPITAL_CACHE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "cache", "share_capital.json"
)

_CAPITAL_TTL_DAYS = 90

_capital_memory_cache: Optional[Dict[str, Dict[str, Any]]] = None
_capital_cache_meta: Dict[str, Any] = {}
_cache_lock = threading.RLock()


def _ensure_cache_dir() -> None:
    d = os.path.dirname(_CAPITAL_CACHE_FILE)
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


_CAPITAL_SCHEMA_VERSION = (
    2  # V16.3.10: v2=万股单位规范（v1 旧缓存为"股"单位，版本不符自动失效重建）
)


def _load_capital_cache() -> Dict[str, Dict[str, Any]]:
    """从磁盘加载全局股本缓存。"""
    global _capital_memory_cache, _capital_cache_meta

    if _capital_memory_cache is not None:
        return _capital_memory_cache

    with _cache_lock:
        if _capital_memory_cache is not None:
            return _capital_memory_cache

        _ensure_cache_dir()
        if os.path.exists(_CAPITAL_CACHE_FILE):
            try:
                with open(_CAPITAL_CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # V16.3.10: schema 版本校验——规范变更（单位/结构）时递增 _CAPITAL_SCHEMA_VERSION，
                # 旧版本缓存直接失效重建（防止"规范改了、旧缓存跨时点继续被信任"）
                if data.get("meta", {}).get("schema_version", 1) != _CAPITAL_SCHEMA_VERSION:
                    _debug_log("capital cache schema mismatch, rebuild")
                    _capital_memory_cache = {}
                    _capital_cache_meta = {"updated_at": ""}
                    return _capital_memory_cache
                _capital_cache_meta = data.get("meta", {})
                _capital_memory_cache = data.get("data", {})
                return _capital_memory_cache
            except (json.JSONDecodeError, OSError):
                pass

        _capital_memory_cache = {}
        _capital_cache_meta = {"updated_at": ""}
        return _capital_memory_cache


def _save_capital_cache() -> None:
    """保存全局股本缓存到磁盘。"""
    with _cache_lock:
        _ensure_cache_dir()
        data = {
            "meta": {
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "schema_version": _CAPITAL_SCHEMA_VERSION,
                "ttl_days": _CAPITAL_TTL_DAYS,
                "count": len(_capital_memory_cache or {}),
            },
            "data": _capital_memory_cache or {},
        }
        tmp_path = f"{_CAPITAL_CACHE_FILE}.{os.getpid()}.{threading.get_ident()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, _CAPITAL_CACHE_FILE)
        except OSError as _e:
            _debug_log(f"capital cache save error: {_e}")
            try:
                os.unlink(tmp_path)
            except FileNotFoundError:
                pass


def _capital_cache_is_fresh(cached: Dict[str, Any], today: Optional[date] = None) -> bool:
    """按每条记录的采集日期执行配置的自然日 TTL。"""
    updated_at = cached.get("updated_at")
    try:
        cached_date = datetime.strptime(str(updated_at), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return False
    reference_date = today or datetime.now().date()
    age_days = (reference_date - cached_date).days
    return 0 <= age_days < _CAPITAL_TTL_DAYS


def _normalize_capital_record(cached: Dict[str, Any]) -> Dict[str, Any]:
    """将历史单位错误值规范为万股，并保留采集日期。"""

    def normalize(value: Any) -> float:
        try:
            number = float(value or 0)
        except (TypeError, ValueError):
            return 0.0
        if not math.isfinite(number) or number < 0:
            return 0.0
        return number / 10000.0 if number > 1e9 else number

    return {
        "total_shares": normalize(cached.get("total_shares")),
        "float_shares": normalize(cached.get("float_shares")),
        "updated_at": str(cached.get("updated_at", "")),
    }


def _valid_capital_result(value: Any) -> bool:
    """只缓存日期有效且有正总股本的结果；零值代表源失败或数据尚未就绪。"""
    if not isinstance(value, dict):
        return False
    try:
        shares = float(value.get("total_shares") or 0)
        return math.isfinite(shares) and shares > 0 and _capital_cache_is_fresh(value)
    except (TypeError, ValueError):
        return False


def get_share_capital(code: str) -> Dict[str, Any]:
    """获取单只股票的股本数据（优先全局缓存，否则实时获取并写入缓存）。

    Returns:
        {"total_shares": float, "float_shares": float, "updated_at": str}
        单位：万股
    """

    cap_cache = _load_capital_cache()
    with _cache_lock:
        cached = cap_cache.get(code)
    # V15.2 P0 修复: 脏数据保护 —— 缓存里 total_shares=0 时也视为未命中，重新拉取
    if isinstance(cached, dict) and _valid_capital_result(cached):
        return _normalize_capital_record(cached)

    result = _normalize_capital_record(_fetch_share_capital(code) or {})
    # V15.2 P0 修复: 只有 total_shares > 0 才写入缓存（避免脏数据污染）
    if _valid_capital_result(result):
        with _cache_lock:
            cap_cache[code] = result
        _save_capital_cache()
        return result

    return {"total_shares": 0, "float_shares": 0, "updated_at": ""}


@cached(
    category="share_capital",
    ttl_seconds=_CAPITAL_TTL_DAYS * 86400,
    valid_if=_valid_capital_result,
)
def _fetch_share_capital(code: str) -> Dict[str, Any]:
    """从数据源获取股本数据（带SQLite缓存）。

    Returns:
        {"total_shares": float, "float_shares": float, "updated_at": str}
        单位：万股
    """
    total = 0.0
    float_shares = 0.0

    try:
        from core.tdx_client import tdx_get_finance_info

        fin = tdx_get_finance_info(code)
        if fin:
            # V16.2.3 修正: 0x0010 协议 zongguben/liutongguben 实为**股**（easy_tdx 源码
            # 注释"万股"错误，_SCALE=10000 乘出股）；本缓存统一输出**万股**（与 push2 f84 路径一致）。
            # 参考 docs/field_dict.md 第 7.1 节
            total = float(fin.get("zongguben", 0) or 0) / 10000.0
            float_shares = float(fin.get("liutongguben", 0) or 0) / 10000.0
            # 注：原代码期望 fin["latest_indicators"]（F10 接口），但 tdx_get_finance_info
            #     实际是 0x0010 协议，不含 latest_indicators key。已修正。
    except Exception:
        # V16.3 C5: TDX 股本获取失败(网络/TCP)——下方有 push2 兜底 + 0 值保护，
        # 吞掉属有意容错（具体错误可查日志层）
        pass

    if total == 0:
        try:
            from stock_common.sc_datasource import eastmoney_stock_info_push2

            info = eastmoney_stock_info_push2(code)
            if info:
                total = float(info.get("total_shares", 0) or 0) / 10000.0
                float_shares = float(info.get("float_shares", 0) or 0) / 10000.0
        except Exception:
            # V16.3 C5: push2 兜底失败——返回 0 值由调用方决定是否使用（有意容错）
            pass

    return {
        "total_shares": total,
        "float_shares": float_shares,
        "updated_at": datetime.now().strftime("%Y-%m-%d"),
    }


def calc_mcap_yi(code: str, price: float) -> float:
    """计算总市值（亿元）。

    Args:
        code: 股票代码
        price: 现价（元）

    Returns:
        总市值（亿元），失败返回0
    """
    if not price or price <= 0:
        return 0.0
    cap = get_share_capital(code)
    total_wan = float(cap.get("total_shares", 0) or 0)
    if not total_wan:
        return 0.0
    return price * total_wan / 10000.0


def calc_float_mcap_yi(code: str, price: float) -> float:
    """计算流通市值（亿元）。

    Args:
        code: 股票代码
        price: 现价（元）

    Returns:
        流通市值（亿元），失败返回0
    """
    if not price or price <= 0:
        return 0.0
    cap = get_share_capital(code)
    float_wan = float(cap.get("float_shares", 0) or 0)
    if not float_wan:
        return 0.0
    return price * float_wan / 10000.0


def get_capital_cache_stats() -> Dict[str, Any]:
    """获取股本缓存统计信息。"""
    cap_cache = _load_capital_cache()
    return {
        "total_cached": len(cap_cache),
        "meta": _capital_cache_meta,
        "cache_file": _CAPITAL_CACHE_FILE,
    }


if __name__ == "__main__":
    print("=== sc_capital_cache.py 自测 ===")
    stats = get_capital_cache_stats()
    print(f"已缓存股票数: {stats['total_cached']}")
    print(f"缓存文件: {stats['cache_file']}")
    print()
    print("测试获取 600519 股本:")
    cap = get_share_capital("600519")
    print(f"  总股本: {cap['total_shares']:.2f} 万股")
    print(f"  流通股: {cap['float_shares']:.2f} 万股")
    print()
    print("测试计算市值 (价格=1700元):")
    mcap = calc_mcap_yi("600519", 1700.0)
    print(f"  总市值: {mcap:.2f} 亿元")

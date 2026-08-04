#!/usr/bin/env python3
"""sc_zhb.py — V16 连续 ZHB 文件回溯补充未知字段

用户需求（2026-08-01 补充）:
  "cache 下有连续的 zhb 文件，可以再次尝试获取未知的字段，并补充在字典中"

背景:
  cache/zhb/ 下有每日一个 zip 包（zhb_20260721.zip ~ zhb_20260731.zip），
  每个包含 tdxstat.cfg（35 字段全市场统计）+ tdxstat2.cfg（21 字段资金/板块）。
  最新包某字段缺失/为空时，回溯更早包（数值字段跨天基本不变）可补充。

设计:
  - backtrack_field(code, field, max_back): 对任意 tdxstat 字段回溯
    （先当前包，缺失则回溯更早 zip）→ 返回 (value, source_date, back_steps)
  - backtrack_stats(code, max_back): 回溯返回整只股票的统计 dict
  - 每次回溯写 fallback.log，字段字典可据此核实来源

注意:
  - 仅适用于"跨天稳定的数值/静态字段"（pe_ttm/pb/股本/行业代码等）。
    实时字段（price/change_pct/amount）禁用回溯（旧值无意义）。
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

_CACHE_DIR = Path(__file__).resolve().parent.parent / "cache" / "zhb"

# 日志（logs/fallback.log，与 sc_network 同级）
_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
os.makedirs(_LOG_DIR, exist_ok=True)
_fallback_logger = logging.getLogger("zhb_backtrack")
if not _fallback_logger.handlers:
    _h = logging.FileHandler(str(_LOG_DIR / "fallback.log"), encoding="utf-8")
    _h.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    _fallback_logger.addHandler(_h)
    _fallback_logger.setLevel(logging.INFO)

# 实时字段黑名单：回溯旧值会误导，禁用
REALTIME_FIELDS = {
    "price", "change_pct", "amount", "volume", "high", "low", "open",
    "last_close", "amount_wan", "change_30d", "change_60d",
}


# ─────────────────────────────────────────────────────────
# 核心函数
# ─────────────────────────────────────────────────────────

def list_archives() -> List[Path]:
    """按日期降序返回 cache/zhb/ 下的 zip 文件列表。"""
    return sorted(_CACHE_DIR.glob("zhb_*.zip"), reverse=True)


def parse_archive(zip_path: Path) -> Optional[Any]:
    """解析单个 zip 为 ZhbData（复用 zhb_client._parse_zhb_data，懒解析）。"""
    try:
        from zhb_client import _parse_zhb_data
        return _parse_zhb_data(zip_path.read_bytes())
    except Exception as _e:
        _fallback_logger.warning(f"zhb backtrack parse {zip_path.name} error: {_e}")
        return None


def _is_empty(value: Any) -> bool:
    """空值判断: None / 空串 / 空容器 / 0。"""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() in ("", "0", "0.0", "None")
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    if isinstance(value, (int, float)):
        return value == 0
    return False


def _stats_of(z: Any, code: str) -> Dict[str, Any]:
    """取单只股票统计 dict（tdxstat + tdxstat2 合并）。"""
    out: Dict[str, Any] = {}
    try:
        s1 = getattr(z, "stock_stats", None)
        if isinstance(s1, dict):
            d = s1.get(code) or {}
            if isinstance(d, dict):
                out.update(d)
    except Exception:
        pass
    try:
        s2 = getattr(z, "stock_stats2", None)
        if isinstance(s2, dict):
            d = s2.get(code) or {}
            if isinstance(d, dict):
                out.update(d)
    except Exception:
        pass
    return out


def backtrack_field(code: str, field: str, max_back: int = 5) -> Tuple[Optional[Any], Optional[str], int]:
    """对任意 tdxstat 字段回溯：先当前包，缺失则回溯更早 zip。

    Args:
        code: 6 位股票代码
        field: tdxstat 字段名（如 pe_ttm / pb / total_shares）
        max_back: 最多回溯几个历史包（默认 5）

    Returns:
        (value, source_date, back_steps):
          value 非空则回溯成功；source_date 来源包日期；back_steps 回溯步数(0=当前包)
    """
    if field in REALTIME_FIELDS:
        raise ValueError(f"字段 {field} 是实时字段，禁止回溯旧值（会误导）")

    # 1) 当前包
    try:
        from zhb_client import get_zhb
        cur = get_zhb()
        if cur is not None:
            stats = _stats_of(cur, code)
            if field in stats and not _is_empty(stats[field]):
                return stats[field], getattr(cur, "date", "") or "", 0
    except Exception:
        pass

    # 2) 回溯更早 zip
    for step, zpath in enumerate(list_archives(), start=1):
        if step > max_back:
            break
        z = parse_archive(zpath)
        if z is None:
            continue
        stats = _stats_of(z, code)
        if field in stats and not _is_empty(stats[field]):
            src_date = getattr(z, "date", "") or zpath.stem.replace("zhb_", "")
            _fallback_logger.info(
                f"zhb backtrack: {code} field={field} <- {zpath.name} (steps={step})")
            return stats[field], src_date, step
    return None, None, -1


def backtrack_stats(code: str, max_back: int = 5) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
    """回溯返回单只股票完整统计 dict（当前包缺失字段的合并结果）。"""
    merged: Dict[str, Any] = {}
    src_date: Optional[str] = None
    steps = -1
    try:
        from zhb_client import get_zhb
        cur = get_zhb()
        if cur is not None:
            merged.update(_stats_of(cur, code))
            src_date = getattr(cur, "date", "") or ""
            steps = 0
    except Exception:
        pass
    for step, zpath in enumerate(list_archives(), start=1):
        if step > max_back:
            break
        z = parse_archive(zpath)
        if z is None:
            continue
        stats = _stats_of(z, code)
        if not stats:
            continue
        # 只补充缺失字段
        missing = {k: v for k, v in stats.items() if k not in merged or _is_empty(merged[k])}
        if missing:
            merged.update(missing)
            src_date = getattr(z, "date", "") or zpath.stem.replace("zhb_", "")
            steps = step
            _fallback_logger.info(
                f"zhb backtrack merge: {code} +{len(missing)} fields <- {zpath.name}")
    if not merged:
        return None, None, -1
    return merged, src_date, steps


def backtrack_with_extractor(code: str, extractor: Callable[[Any, str], Any],
                             max_back: int = 5) -> Tuple[Optional[Any], Optional[str], int]:
    """通用回溯：调用方自定义提取函数。

    Args:
        code: 股票代码
        extractor: callable(ZhbData, code) -> value（None/空 = 无此字段）
        max_back: 最多回溯包数

    Returns:
        (value, source_date, back_steps)
    """
    try:
        from zhb_client import get_zhb
        cur = get_zhb()
        if cur is not None:
            try:
                v = extractor(cur, code)
            except Exception:
                v = None
            if not _is_empty(v):
                return v, getattr(cur, "date", "") or "", 0
    except Exception:
        pass

    for step, zpath in enumerate(list_archives(), start=1):
        if step > max_back:
            break
        z = parse_archive(zpath)
        if z is None:
            continue
        try:
            v = extractor(z, code)
        except Exception:
            continue
        if not _is_empty(v):
            src_date = getattr(z, "date", "") or zpath.stem.replace("zhb_", "")
            _fallback_logger.info(
                f"zhb backtrack: {code} <- {zpath.name} (steps={step})")
            return v, src_date, step
    return None, None, -1


def archive_summary() -> Dict[str, Any]:
    """返回 cache/zhb/ 连续文件摘要（供字段字典核实）。"""
    archives = list_archives()
    return {
        "archive_count": len(archives),
        "oldest": archives[-1].name if archives else None,
        "newest": archives[0].name if archives else None,
        "date_range": [p.stem.replace("zhb_", "") for p in archives],
    }

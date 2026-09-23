"""_v39_compat.py — 上游 3.x 共用 helper 的忠实复刻(取数层契约, 不进字段字典).

本模块集中实现上游 SKILL.md 中 _v39_* 系列 helper 的语义, 供本仓库吸收的上游取数函数
(腾讯逐笔 _ticks / 新浪期货 _futures_sina 等) 复用, 避免各模块重复定义与命名空间冲突。

错误契约(对齐上游):
  - 必填数值缺/非有限 → RuntimeError(不是参数错的 ValueError)。
  - 来源给了布尔值当数值 / 非数字字符串 → RuntimeError(格式变了, 不是参数写错)。
  - 来源日期认不出 → RuntimeError。

注意: 这些函数刻意与 stock_common.sc_utils._safe_float 区分 —— 后者缺值/异常返回 default,
用于字段治理层; 此处用于取数层契约, 缺值必须显式报错(否则会把"源格式变了"静默写成价格/成交量)。
"""
from __future__ import annotations

import functools
import math
import re
from datetime import date as _date_cls, datetime, timezone

import pandas as pd

__all__: list[str] = []  # 仅被兄弟模块显式 import; 不进入 sc_datasource 的 import * 表面


def _to_num(value):
    """'1,234.50' → 1234.5; 空/'-'/'--'/None → None; 非数字/布尔/inf → RuntimeError(上游 _v39_num)。"""
    if value is None:
        return None
    if isinstance(value, bool):
        raise RuntimeError(f"来源在数值字段给了布尔值 {value!r}")
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            return None
        return float(value)
    text = str(value).replace(",", "").strip()
    if text in ("", "-", "--", "None", "null"):
        return None
    try:
        number = float(text)
    except ValueError as exc:
        raise RuntimeError(f"来源返回了无法识别的数值 {value!r}") from exc
    return number if math.isfinite(number) else None


def _req_num(value, what):
    """必填数值(价/量/额): 空/NaN/inf 也抛 RuntimeError, 不能当缺失放过(上游 _v39_req_num)。"""
    number = _to_num(value)
    if number is None:
        raise RuntimeError(f"来源的 {what} 为空或不是有限数值: {value!r}")
    return number


def _fut_price(value):
    """期货/期权价格: 0 不是有效价格(无成交时交易所填 0 或空), 统一成 None(上游 _fut_price)。"""
    number = _to_num(value)
    return None if number == 0 else number


def _parse_date(value):
    """'2026-09-18' / '20260918' / date 对象 → 'YYYY-MM-DD'; 其他写法抛 ValueError(上游 _v39_date)。"""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, _date_cls):
        return value.isoformat()
    text = str(value).strip()
    fmt = "%Y%m%d" if re.fullmatch(r"[0-9]{8}", text) else "%Y-%m-%d"
    return datetime.strptime(text, fmt).date().isoformat()


def _src_date(value):
    """来源返回的日期 → 'YYYY-MM-DD'; 认不出抛 RuntimeError(上游 _v39_src_date)。"""
    try:
        return _parse_date(value)
    except ValueError as exc:
        raise RuntimeError(f"来源返回了无法识别的日期 {value!r}") from exc


def _rows(value, what):
    """来源里可能整段缺失的行列表: 字段 None 按空处理, 其余必须是对象列表(上游 _v39_rows)。"""
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(row, dict) for row in value):
        raise RuntimeError(f"{what} 应为对象列表，实际是 {type(value).__name__}: {str(value)[:120]}")
    return value


def _frame(rows, source, url, columns=None):
    """统一出表: 附 source/source_url/fetched_at(上游 _v39_frame)。"""
    frame = pd.DataFrame(rows, columns=columns)
    frame["source"] = source
    frame["source_url"] = url
    frame["fetched_at"] = datetime.now(timezone.utc).isoformat()
    return frame


def _contract(func):
    """统一异常契约: 来源行缺字段时 row['X'] 漏出 KeyError → 转带函数名 RuntimeError(上游 _v39_contract)。"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as exc:
            raise RuntimeError(f"{func.__name__}: 来源数据缺少字段 {exc}，格式可能已变") from exc
    return wrapper

"""日期与来源元数据的统一处理。

此模块只处理可以明确核实的日期和字段来源，不从采集时间推断上游有效日期。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Callable, Dict, Mapping, Optional


def normalize_as_of_date(value: Any) -> str:
    """将明确提供的日期规范为 ``YYYY-MM-DD``；无法确认时返回空字符串。"""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str):
        return ""

    text = value.strip()
    if not text:
        return ""
    candidates = [text]
    if len(text) >= 10 and text[4:5] == "-":
        candidates.append(text[:10])
    if len(text) >= 8 and text[:8].isdigit():
        candidates.append(text[:8])
    for candidate in candidates:
        for fmt in ("%Y-%m-%d", "%Y%m%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(candidate, fmt).date().isoformat()
            except ValueError:
                continue
    return ""


def _source_family(source_label: str) -> str:
    """从展示标签中提取稳定来源族；不把计算值或未知值伪装成来源。"""
    parts = source_label.split(":")
    if len(parts) < 2:
        return ""
    if parts[0] == "realtime":
        family = parts[1]
        return "push2delay" if family == "push2delay-ulist" else family
    if parts[0] == "zhb":
        return "zhb"
    if parts[0] == "tdx":
        return "tdx"
    if parts[0] == "static":
        # A dynamic TDX quote date cannot establish the effective date of a
        # separate static-cache value. ZHB static values may use the package date.
        return "zhb" if parts[1] == "zhb" else ""
    if parts[0] == "sina":
        return "sina"
    return ""


def canonical_data_source(source_label: Any) -> str:
    """把价格来源标签压成稳定的契约枚举；未知或计算来源保持 unknown。"""
    if not isinstance(source_label, str):
        return "unknown"
    if source_label.startswith("zhb:"):
        return "zhb"
    if source_label.startswith(("tdx:", "static:tdx", "realtime:tdx")):
        return "tdx"
    if source_label.startswith("realtime:") and "unknown" not in source_label:
        return "http"
    return "unknown"


def build_field_as_of_dates(
    field_sources: Mapping[str, str],
    source_as_of_dates: Mapping[str, Any],
    *,
    zhb_data_date: Any = "",
) -> Dict[str, str]:
    """按字段来源建立有效日期表，仅包含能够核实日期的字段。"""
    source_dates = {
        str(family): normalized
        for family, value in source_as_of_dates.items()
        if (normalized := normalize_as_of_date(value))
    }
    normalized_zhb_date = normalize_as_of_date(zhb_data_date)
    result: Dict[str, str] = {}
    for field_name, source_label in field_sources.items():
        if not isinstance(source_label, str):
            continue
        family = _source_family(source_label)
        source_date = normalized_zhb_date if family == "zhb" else source_dates.get(family, "")
        if source_date:
            result[field_name] = source_date
    return result


def filter_zhb_snapshot_fields(
    snapshot: Mapping[str, Any],
    data_date: Any,
    *,
    as_of: Optional[datetime] = None,
    field_safe: Optional[Callable[..., bool]] = None,
) -> Dict[str, Any]:
    """按原始 ZHB 字段的 ABCD 分类过滤过期值。

    ``report_date`` 是财报期标识而不是行情日期，因此一直保留，避免破坏财报事件锁。
    测试可以注入 ``field_safe``，生产环境使用 stock_common 的公共适配器。
    """
    if field_safe is None:
        from stock_common.sc_datasource import zhb_field_safe

        field_safe = zhb_field_safe

    result: Dict[str, Any] = {}
    for field_name, value in snapshot.items():
        if field_name == "report_date":
            result[field_name] = value
            continue
        if field_safe(field_name, data_date=data_date, as_of=as_of):
            result[field_name] = value
    return result


def quote_time_anchor(quote_date: Any, as_of: Optional[datetime] = None) -> str:
    """依据价格字段的有效日期返回兼容锚点；缺少确切日期时返回 ``unknown``。"""
    normalized = normalize_as_of_date(quote_date)
    if not normalized:
        return "unknown"

    quote_day = date.fromisoformat(normalized)
    reference = as_of or datetime.now()
    reference_day = reference.date() if isinstance(reference, datetime) else reference
    if quote_day == reference_day:
        return "t_day"

    from stock_common.stock_calendar import previous_trading_day

    previous = previous_trading_day(reference_day, include_current=False)
    if quote_day == previous:
        return "t-1"
    return "unknown"

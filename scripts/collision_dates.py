"""Date domains, trading-session validation, and deterministic snapshot selection.

Capture folder names record where a run was stored; they are not always the
date represented by the source data. This module keeps those concepts separate
for the generic and topic-specific collision analyzers.
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Callable, Iterable

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

TRADING = "trading"
CALENDAR = "calendar"
EVENT_SOURCES = frozenset(
    {
        "cninfo",
        "reports",
        "research_sina",
        "news_wscn_cctv",
        "sse_e_interaction",
        "cls",
    }
)
EXCLUDED_MARKET_DATES = frozenset({"20260814"})
_FOLDER_RE = re.compile(r"^\d{8}$")
_DATE_KEYS = {
    "news_wscn_cctv": ("date", "publish_date", "publishDate", "pubDate", "time"),
    "reports": ("publishDate", "publish_date", "pubDate", "date"),
    "research_sina": ("publishDate", "publish_date", "pubDate", "reportDate", "date"),
    "cninfo": (
        "announcementTime",
        "announcement_time",
        "announcementDate",
        "publishDate",
        "pubDate",
        "date",
    ),
    "sse_e_interaction": ("answer_time", "answerTime", "question_time", "questionTime", "date"),
    "cls": ("pub_time", "pubTime", "ctime", "datetime", "date", "time"),
}


class CalendarResolutionError(RuntimeError):
    """Raised when a market date cannot safely be classified as a session."""


@dataclass(frozen=True)
class CaptureFolder:
    name: str
    path: str
    folder_date: date
    capture_date: date
    market_date: date | None
    meta: dict[str, Any]
    market_date_origin: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class FolderWindow:
    folders: tuple[CaptureFolder, ...]
    market_folders: frozenset[str]
    event_folders: frozenset[str]
    trading_dates: tuple[str, ...]
    event_start: date
    event_end: date
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class Snapshot:
    source: str
    domain: str
    sample_date: date
    capture_date: date
    folder: str
    path: str
    document: dict[str, Any]
    meta: dict[str, Any]
    phase: str
    status: str
    record_count: int
    captured_at: datetime | None
    date_origin: str

    @property
    def day_key(self) -> str:
        prefix = "C" if self.domain == CALENDAR else "T"
        return f"{prefix}:{self.sample_date:%Y%m%d}"

    @property
    def rank(self) -> tuple[int, int, int, int, str, str]:
        status_rank = {"ok": 3, "partial": 2, "unknown": 1}.get(self.status, 0)
        phase_rank = {"closed": 2, "unknown": 1, "intraday": 0, "calendar": 2}.get(self.phase, 1)
        origin_rank = {"source_as_of": 3, "meta_data_date": 2, "folder_inferred": 1}.get(
            self.date_origin, 0
        )
        captured = self.captured_at.isoformat(timespec="seconds") if self.captured_at else ""
        return phase_rank, status_rank, self.record_count, origin_rank, captured, self.folder


def parse_date(value: Any) -> date | None:
    """Parse supported compact, ISO-date, or ISO-datetime representations."""
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone(timedelta(hours=8))).date()
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        if not float(value).is_integer():
            return None
        value = str(int(value))
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.isdigit() and len(text) in {10, 13, 16, 19}:
        scale = {10: 1, 13: 1_000, 16: 1_000_000, 19: 1_000_000_000}[len(text)]
        try:
            utc_value = datetime.fromtimestamp(int(text) / scale, tz=timezone.utc)
            china_time = utc_value.astimezone(timezone(timedelta(hours=8)))
            return china_time.date()
        except (OverflowError, OSError, ValueError):
            return None
    try:
        timestamp = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        pass
    else:
        if timestamp.tzinfo is not None:
            timestamp = timestamp.astimezone(timezone(timedelta(hours=8)))
        return timestamp.date()
    if re.fullmatch(r"\d{8}", text):
        try:
            return datetime.strptime(text, "%Y%m%d").date()
        except ValueError:
            return None
    match = re.search(r"(?<!\d)(\d{4})[-/]?(\d{2})[-/]?(\d{2})(?!\d)", text)
    if match is None:
        return None
    try:
        return date(*(int(part) for part in match.groups()))
    except ValueError:
        return None


def is_trading_session(day: date) -> bool:
    """Use the project's local calendar plus its cached ZHB supplement."""
    try:
        from stock_common.stock_calendar import is_workday_with_zhb_supplement

        return bool(is_workday_with_zhb_supplement(day))
    except Exception as exc:
        raise CalendarResolutionError(f"交易日历无法判定 {day.isoformat()}: {exc}") from exc


def previous_trading_session(
    day: date, checker: Callable[[date], bool] | None = None, max_days: int = 370
) -> date:
    """Return the closest valid market session strictly before ``day``."""
    is_session = checker or is_trading_session
    candidate = day - timedelta(days=1)
    for _ in range(max_days):
        if is_session(candidate):
            return candidate
        candidate -= timedelta(days=1)
    raise CalendarResolutionError(f"{day.isoformat()} 前 {max_days} 日没有可确认的交易日")


def _read_json(path: str) -> dict[str, Any] | None:
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _capture_datetime(meta: dict[str, Any]) -> datetime | None:
    for key in ("start", "run_datetime", "end"):
        value = meta.get(key)
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                continue
            if parsed.tzinfo is not None:
                parsed = parsed.astimezone(timezone(timedelta(hours=8))).replace(tzinfo=None)
            return parsed
    return None


def discover_capture_folders(
    data_dir: str, checker: Callable[[date], bool] | None = None
) -> tuple[list[CaptureFolder], list[str]]:
    """List valid capture folders and safely infer legacy weekend data dates."""
    is_session = checker or is_trading_session
    folders: list[CaptureFolder] = []
    warnings: list[str] = []
    try:
        names = sorted(os.listdir(data_dir))
    except OSError as exc:
        raise OSError(f"无法读取采集目录 {data_dir}: {exc}") from exc

    for name in names:
        path = os.path.join(data_dir, name)
        if not os.path.isdir(path):
            continue
        if not _FOLDER_RE.fullmatch(name):
            if name.startswith("20") and any(
                filename.startswith("raw_") and filename.endswith(".json")
                for filename in os.listdir(path)
            ):
                warnings.append(f"非标准日期目录已跳过: {name}")
            continue
        folder_day = parse_date(name)
        if folder_day is None:
            warnings.append(f"无效日期目录已跳过: {name}")
            continue

        meta_path = os.path.join(path, "meta.json")
        meta = _read_json(meta_path) if os.path.isfile(meta_path) else {}
        local_warnings: list[str] = []
        if os.path.isfile(meta_path) and meta is None:
            local_warnings.append(f"{name}: meta.json 无法解析")
            meta = {}
        if not isinstance(meta, dict):
            meta = {}

        raw_capture = meta.get("capture_date")
        capture_day = parse_date(raw_capture)
        if raw_capture not in (None, "") and capture_day is None:
            local_warnings.append(f"{name}: meta.capture_date 格式无效，尝试 run_date")
        if capture_day is None:
            capture_day = parse_date(meta.get("run_date")) or folder_day
        explicit_data_date = meta.get("data_date")
        if meta.get("data_date_domain") == CALENDAR:
            market_day = None
            origin = "calendar_only"
        elif explicit_data_date not in (None, ""):
            market_day = parse_date(explicit_data_date)
            origin = "meta_data_date"
            if market_day is None:
                local_warnings.append(f"{name}: meta.data_date 格式无效，行情快照将跳过")
            else:
                try:
                    valid = is_session(market_day)
                except CalendarResolutionError as exc:
                    local_warnings.append(f"{name}: {exc}，行情快照将跳过")
                    market_day = None
                else:
                    if not valid:
                        local_warnings.append(
                            f"{name}: 显式 data_date {market_day:%Y%m%d} 不是交易日，行情快照将跳过"
                        )
                        market_day = None
        else:
            try:
                if is_session(folder_day):
                    market_day = folder_day
                    origin = "folder_date"
                else:
                    market_day = previous_trading_session(folder_day, is_session)
                    origin = "folder_inferred"
                    local_warnings.append(
                        f"{name}: 旧式非交易日目录按前一交易日 {market_day:%Y%m%d} 归并；目录未改名"
                    )
            except CalendarResolutionError as exc:
                market_day = None
                origin = "invalid"
                local_warnings.append(f"{name}: {exc}，行情快照将跳过")

        folders.append(
            CaptureFolder(
                name=name,
                path=path,
                folder_date=folder_day,
                capture_date=capture_day,
                market_date=market_day,
                meta=meta,
                market_date_origin=origin,
                warnings=tuple(local_warnings),
            )
        )
        warnings.extend(local_warnings)
    return folders, warnings


def select_folder_window(
    folders: Iterable[CaptureFolder],
    window: int,
    report_date: date,
    all_history: bool = False,
    excluded_trading_dates: set[str] | frozenset[str] = frozenset(),
) -> FolderWindow:
    """Select N distinct trading sessions and N natural capture days."""
    all_folders = tuple(folders)
    warnings = [
        f"{folder.name}: 行情数据日 {folder.market_date:%Y%m%d} 晚于报告日，行情快照不纳入本轮"
        for folder in all_folders
        if folder.market_date is not None and folder.market_date > report_date
    ]
    is_excluded = lambda day: day.strftime("%Y%m%d") in excluded_trading_dates
    warnings.extend(
        f"{folder.name}: 行情数据日 {folder.market_date:%Y%m%d} 属于配置的异常日，行情快照排除"
        for folder in all_folders
        if folder.market_date is not None and is_excluded(folder.market_date)
    )
    if all_history:
        market_dates = sorted(
            {
                folder.market_date
                for folder in all_folders
                if folder.market_date
                and folder.market_date <= report_date
                and not is_excluded(folder.market_date)
            }
        )
        market_names = frozenset(
            folder.name for folder in all_folders if folder.market_date in market_dates
        )
        event_names = frozenset(folder.name for folder in all_folders)
        event_start = min((folder.capture_date for folder in all_folders), default=report_date)
    else:
        n = max(1, int(window))
        eligible_market = sorted(
            {
                folder.market_date
                for folder in all_folders
                if folder.market_date
                and folder.market_date <= report_date
                and not is_excluded(folder.market_date)
            }
        )
        market_dates = eligible_market[-n:]
        event_start = report_date - timedelta(days=n - 1)
        market_names = frozenset(
            folder.name for folder in all_folders if folder.market_date in market_dates
        )
        event_names = frozenset(
            folder.name for folder in all_folders if folder.capture_date >= event_start
        )
    chosen = tuple(
        folder
        for folder in all_folders
        if folder.name in market_names or folder.name in event_names
    )
    return FolderWindow(
        folders=chosen,
        market_folders=market_names,
        event_folders=event_names,
        trading_dates=tuple(day.strftime("%Y%m%d") for day in market_dates),
        event_start=event_start,
        event_end=report_date,
        warnings=tuple(warnings),
    )


def is_calendar_event_source(source: str) -> bool:
    return source in EVENT_SOURCES


def event_record_date(source: str, record: dict[str, Any]) -> date | None:
    """Extract the natural publication/event date for a known event source."""
    keys = _DATE_KEYS.get(source, ())
    pending: list[dict[str, Any]] = [record]
    seen: set[int] = set()
    while pending:
        current = pending.pop(0)
        if id(current) in seen:
            continue
        seen.add(id(current))
        for key in keys:
            if key in current:
                parsed = parse_date(current[key])
                if parsed is not None:
                    return parsed
        for value in current.values():
            if isinstance(value, dict):
                pending.append(value)
    return None


def _source_status(meta: dict[str, Any], source: str) -> str:
    sources = meta.get("sources")
    value = sources.get(source) if isinstance(sources, dict) else None
    if not isinstance(value, dict):
        return "unknown"
    status = str(value.get("status") or "").lower()
    if status in {"ok", "partial", "failed", "unwired", "deprecated", "no_key"}:
        return status
    if value.get("ok") is True:
        return "ok"
    if value.get("ok") is False:
        return "failed"
    return "unknown"


def _record_count(document: dict[str, Any]) -> int:
    metadata_keys = {
        "scheme",
        "field_meta",
        "source",
        "source_url",
        "fetched_at",
        "__error__",
        "__skipped__",
        "__source_meta__",
        "auction_snapshot_meta",
    }

    def count_node(value: Any) -> int:
        if isinstance(value, list):
            return sum(count_node(item) for item in value if isinstance(item, (dict, list)))
        if not isinstance(value, dict) or value.get("__error__") or "__skipped__" in value:
            return 0
        children = [
            item
            for key, item in value.items()
            if key not in metadata_keys and isinstance(item, (dict, list))
        ]
        nested_count = sum(count_node(item) for item in children)
        if nested_count:
            return nested_count
        return int(
            any(
                key not in metadata_keys and not isinstance(item, (dict, list))
                for key, item in value.items()
            )
        )

    return count_node(document)


def _source_as_of(meta: dict[str, Any], document: dict[str, Any], source: str) -> Any:
    if source == "zhb":
        if document.get("zhb_date"):
            return document["zhb_date"], "source_as_of"
        return None, "missing_zhb_as_of"
    source_meta = meta.get("sources")
    one_source = source_meta.get(source) if isinstance(source_meta, dict) else None
    if isinstance(one_source, dict):
        for key in ("as_of_date", "data_date", "trade_date"):
            if one_source.get(key):
                return one_source[key], "source_as_of"
    source_dates = meta.get("source_as_of_dates")
    if isinstance(source_dates, dict) and source_dates.get(source):
        return source_dates[source], "source_as_of"
    for key in ("as_of_date", "asof_date", "data_date", "trade_date", "tradeDate"):
        if document.get(key):
            return document[key], "source_as_of"
    if meta.get("data_date"):
        return meta["data_date"], "meta_data_date"
    return None, "folder_inferred"


def _phase(meta: dict[str, Any], capture_day: date, sample_day: date, event: bool) -> str:
    if event:
        return "calendar"
    captured = _capture_datetime(meta)
    if sample_day < capture_day:
        return "closed"
    if captured is not None:
        if captured.time() >= time(15, 0):
            return "closed"
        return "intraday"
    value = str(meta.get("market_phase") or "").lower()
    if value in {"closed", "intraday"}:
        return value
    return "unknown"


def build_snapshot(
    folder: CaptureFolder,
    source: str,
    path: str,
    document: dict[str, Any],
    checker: Callable[[date], bool] | None = None,
) -> tuple[Snapshot | None, list[str]]:
    """Resolve a raw file's date domain and return its auditable snapshot record."""
    is_session = checker or is_trading_session
    warnings: list[str] = []
    event = is_calendar_event_source(source)
    sample_day: date | None
    if event:
        sample_day = folder.capture_date
        origin = "folder_inferred"
        domain = CALENDAR
    else:
        raw_day, origin = _source_as_of(folder.meta, document, source)
        if source == "zhb" and raw_day is None:
            warnings.append(f"{folder.name}/zhb: 缺少 zhb_date as-of，快照跳过")
            return None, warnings
        sample_day = parse_date(raw_day) if raw_day is not None else folder.market_date
        if sample_day is None:
            warnings.append(f"{folder.name}/{source}: 缺少可用行情 as_of_date，快照跳过")
            return None, warnings
        try:
            valid = is_session(sample_day)
        except CalendarResolutionError as exc:
            warnings.append(f"{folder.name}/{source}: {exc}，快照跳过")
            return None, warnings
        if not valid:
            warnings.append(
                f"{folder.name}/{source}: 来源日期 {sample_day:%Y%m%d} 不是交易日，快照跳过"
            )
            return None, warnings
        if sample_day > folder.capture_date:
            warnings.append(
                f"{folder.name}/{source}: 来源 as_of_date {sample_day:%Y%m%d} 晚于采集日 "
                f"{folder.capture_date:%Y%m%d}，快照跳过"
            )
            return None, warnings
        domain = TRADING

    status = _source_status(folder.meta, source)
    if status in {"failed", "unwired", "deprecated", "no_key"}:
        warnings.append(f"{folder.name}/{source}: 来源状态为 {status}，快照跳过")
        return None, warnings
    if status == "partial":
        warnings.append(f"{folder.name}/{source}: 来源状态为 partial，样本按部分快照参与")
    if document.get("__error__"):
        warnings.append(f"{folder.name}/{source}: 原始文件包含整体错误，快照跳过")
        return None, warnings
    record_count = _record_count(document)
    if record_count == 0:
        warnings.append(f"{folder.name}/{source}: 没有可用记录，快照跳过")
        return None, warnings

    phase = _phase(folder.meta, folder.capture_date, sample_day, event)
    captured = _capture_datetime(folder.meta)
    declared_phase = str(folder.meta.get("market_phase") or "").lower()
    if (
        not event
        and captured is not None
        and sample_day == folder.capture_date
        and declared_phase in {"closed", "intraday"}
    ):
        observed_phase = "closed" if captured.time() >= time(15, 0) else "intraday"
        if observed_phase != declared_phase:
            warnings.append(
                f"{folder.name}/{source}: market_phase={declared_phase} 与采集时间矛盾，"
                f"按采集时间判为 {observed_phase}"
            )
    if phase == "intraday":
        warnings.append(f"{folder.name}/{source}: 盘中快照，保留为候选样本但不计入 L1")
    elif phase == "unknown":
        warnings.append(f"{folder.name}/{source}: 采集时段未知，保留为候选样本但不计入 L1")
    captured_at = captured
    snapshot = Snapshot(
        source=source,
        domain=domain,
        sample_date=sample_day,
        capture_date=folder.capture_date,
        folder=folder.name,
        path=path,
        document=document,
        meta=folder.meta,
        phase=phase,
        status=status,
        record_count=record_count,
        captured_at=captured_at,
        date_origin=origin,
    )
    return snapshot, warnings


def select_snapshots(
    folders: Iterable[CaptureFolder],
    sources: set[str] | None = None,
    allowed_trading_folders: set[str] | frozenset[str] | None = None,
    allowed_event_folders: set[str] | frozenset[str] | None = None,
    checker: Callable[[date], bool] | None = None,
) -> tuple[list[Snapshot], list[str]]:
    """Load, validate, and deterministically deduplicate per-source snapshots."""
    candidates: list[Snapshot] = []
    warnings: list[str] = []
    for folder in folders:
        warnings.extend(folder.warnings)
        try:
            filenames = sorted(os.listdir(folder.path))
        except OSError as exc:
            warnings.append(f"{folder.name}: 无法列出目录内容: {exc}")
            continue
        raw_sources = {
            filename[len("raw_") : -len(".json")]
            for filename in filenames
            if filename.startswith("raw_") and filename.endswith(".json")
        }
        meta_sources = folder.meta.get("sources")
        if isinstance(meta_sources, dict):
            for source, info in meta_sources.items():
                if not isinstance(info, dict):
                    continue
                status = str(info.get("status") or "").lower()
                if status in {"failed", "partial"}:
                    warnings.append(f"{folder.name}/{source}: 采集状态 {status}")
                if status in {"ok", "partial"} and source not in raw_sources:
                    warnings.append(f"{folder.name}/{source}: meta 标记 {status} 但 raw 文件缺失")

        for source in sorted(raw_sources):
            if sources is not None and source not in sources:
                continue
            event = is_calendar_event_source(source)
            if (
                event
                and allowed_event_folders is not None
                and folder.name not in allowed_event_folders
            ):
                continue
            if (
                not event
                and allowed_trading_folders is not None
                and folder.name not in allowed_trading_folders
            ):
                continue
            path = os.path.join(folder.path, f"raw_{source}.json")
            document = _read_json(path)
            if document is None:
                warnings.append(f"{folder.name}/{source}: raw JSON 无法解析或不是对象")
                continue
            snapshot, problems = build_snapshot(folder, source, path, document, checker)
            warnings.extend(problems)
            if snapshot is not None:
                candidates.append(snapshot)

    chosen: dict[tuple[str, str, str], Snapshot] = {}
    for snapshot in candidates:
        # Event runs may contain updates on later calendar days; preserve those
        # captures and let record-level event dates drive their sample identity.
        dedupe_date = (
            snapshot.capture_date.strftime("%Y%m%d")
            if snapshot.domain == CALENDAR
            else snapshot.sample_date.strftime("%Y%m%d")
        )
        key = (snapshot.source, snapshot.domain, dedupe_date)
        current = chosen.get(key)
        if current is None or snapshot.rank > current.rank:
            if current is not None:
                warnings.append(
                    f"重复快照 {snapshot.source}/{dedupe_date}: 选择 {snapshot.folder}，"
                    f"忽略 {current.folder}"
                )
            chosen[key] = snapshot
        else:
            warnings.append(
                f"重复快照 {snapshot.source}/{dedupe_date}: 保留 {current.folder}，"
                f"忽略 {snapshot.folder}"
            )
    return (
        sorted(chosen.values(), key=lambda item: (item.source, item.sample_date, item.folder)),
        warnings,
    )


def sample_date_key(domain: str, day: date) -> str:
    """Build a collision key that cannot mix trading and natural calendar days."""
    prefix = "C" if domain == CALENDAR else "T"
    return f"{prefix}:{day:%Y%m%d}"

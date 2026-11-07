#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit retained capture/data/source date mappings from meta.json only.

This is a read-only, offline audit. It never opens raw capture files and never
uses a folder name as a source date.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)

from scripts.collision_dates import MIN_CAPTURE_DATE, parse_date

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "docs" / "field_verification"
RETENTION_START = MIN_CAPTURE_DATE


def _source_date(entry: dict[str, Any], source_dates: Any, source: str):
    for key in ("as_of_date", "data_date", "trade_date"):
        parsed = parse_date(entry.get(key))
        if parsed is not None:
            return parsed, f"sources.{source}.{key}"
    if isinstance(source_dates, dict):
        parsed = parse_date(source_dates.get(source))
        if parsed is not None:
            return parsed, f"source_as_of_dates.{source}"
    return None, "missing_source_date"


def _source_capture_date(entry: dict[str, Any], folder_capture_day: date):
    parsed = parse_date(entry.get("source_capture_date"))
    if parsed is not None:
        return parsed, str(entry.get("source_capture_date_origin") or "sources.source_capture_date")
    return folder_capture_day, "meta.capture_date_fallback"


def _retained_date_folders(root: Path, since: date):
    for folder in sorted(root.iterdir(), key=lambda item: item.name):
        if not folder.is_dir() or len(folder.name) != 8 or not folder.name.isdigit():
            continue
        folder_day = parse_date(folder.name)
        if folder_day is not None and folder_day >= since:
            yield folder


def _read_meta(folder: Path) -> tuple[dict[str, Any] | None, str | None]:
    meta_path = folder / "meta.json"
    if not meta_path.is_file():
        return None, f"{folder.name}: 缺少 meta.json，未纳入日期映射"
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"{folder.name}: meta.json 无法读取，未纳入日期映射: {exc}"
    if not isinstance(meta, dict):
        return None, f"{folder.name}: meta.json 根结构不是对象，未纳入日期映射"
    return meta, None


def _target_dates(
    folder: Path, meta: dict[str, Any], since: date
) -> tuple[date | None, date | None, str | None]:
    capture_day = parse_date(meta.get("capture_date"))
    data_day = parse_date(meta.get("data_date"))
    if capture_day is None or capture_day < since:
        return None, None, f"{folder.name}: capture_date 缺失或早于审计起点，已跳过"
    if data_day is None or data_day < since:
        return None, None, f"{folder.name}: data_date 缺失或早于审计起点，已跳过"
    return capture_day, data_day, None


def _source_observations(
    folder: Path,
    sources: dict[str, Any],
    source_dates: Any,
    capture_day: date,
    data_day: date,
    since: date,
    missing_dates: Counter[str],
    excluded_pre_retention: Counter[str],
    excluded_status: Counter[str],
) -> list[dict[str, Any]]:
    observations = []
    for source, raw_entry in sorted(sources.items()):
        if not isinstance(raw_entry, dict):
            continue
        source_day, basis = _source_date(raw_entry, source_dates, source)
        status = raw_entry.get("status")
        if source_day is None:
            missing_dates[source] += 1
            continue
        if status not in {"ok", "partial"}:
            excluded_status[f"{source}:{status or 'unknown'}"] += 1
            continue
        if source_day < since:
            excluded_pre_retention[source] += 1
            continue
        source_capture_day, source_capture_basis = _source_capture_date(raw_entry, capture_day)
        observations.append(
            {
                "folder": folder.name,
                "capture_date": capture_day.strftime("%Y%m%d"),
                "source_capture_date": source_capture_day.strftime("%Y%m%d"),
                "source_capture_date_basis": source_capture_basis,
                "target_data_date": data_day.strftime("%Y%m%d"),
                "source": source,
                "source_date": source_day.strftime("%Y%m%d"),
                "source_date_basis": basis,
                "source_status": status,
                "capture_minus_data_calendar_days": (capture_day - data_day).days,
                "source_minus_data_calendar_days": (source_day - data_day).days,
                "source_minus_capture_calendar_days": (source_day - capture_day).days,
                "source_minus_source_capture_calendar_days": (source_day - source_capture_day).days,
            }
        )
    return observations


def _date_gap_diagnostics(
    missing_dates: Counter[str],
    excluded_pre_retention: Counter[str],
    excluded_status: Counter[str],
) -> list[str]:
    diagnostics = []
    summaries = (
        (missing_dates, "缺少来源级日期且未作推断的次数"),
        (excluded_pre_retention, "早于保留起点并排除的来源日期次数"),
        (excluded_status, "来源状态不为 ok/partial 而排除的次数"),
    )
    for counts, label in summaries:
        if counts:
            summary = ", ".join(f"{key}={count}" for key, count in sorted(counts.items()))
            diagnostics.append(f"{label}: {summary}")
    return diagnostics


def collect_observations(
    data_dir: str | Path = DATA_DIR,
    since: date = RETENTION_START,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Read retained meta.json files and return source-specific date observations."""
    if since < RETENTION_START:
        raise ValueError(f"审计起点不能早于样本保留边界 {RETENTION_START:%Y%m%d}")
    root = Path(data_dir)
    observations: list[dict[str, Any]] = []
    diagnostics: list[str] = []
    missing_dates: Counter[str] = Counter()
    excluded_pre_retention: Counter[str] = Counter()
    excluded_status: Counter[str] = Counter()
    if not root.is_dir():
        raise FileNotFoundError(f"采集归档目录不存在: {root}")

    for folder in _retained_date_folders(root, since):
        meta, issue = _read_meta(folder)
        if issue:
            diagnostics.append(issue)
            continue
        if meta is None:
            continue
        capture_day, data_day, issue = _target_dates(folder, meta, since)
        if issue:
            diagnostics.append(issue)
            continue
        if capture_day is None or data_day is None:
            continue
        sources = meta.get("sources")
        if not isinstance(sources, dict):
            diagnostics.append(f"{folder.name}: sources 元数据缺失，未纳入来源日期映射")
            continue
        observations.extend(
            _source_observations(
                folder,
                sources,
                meta.get("source_as_of_dates"),
                capture_day,
                data_day,
                since,
                missing_dates,
                excluded_pre_retention,
                excluded_status,
            )
        )
    diagnostics.extend(
        _date_gap_diagnostics(missing_dates, excluded_pre_retention, excluded_status)
    )
    return observations, diagnostics


def summarize_observations(
    observations: list[dict[str, Any]], since: date = RETENTION_START
) -> dict[str, Any]:
    """Summarize observed date offsets without promoting them to source contracts."""
    by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for observation in observations:
        by_source[observation["source"]].append(observation)
    sources = []
    for source, rows in sorted(by_source.items()):
        data_offsets = Counter(row["source_minus_data_calendar_days"] for row in rows)
        capture_offsets = Counter(row["source_minus_capture_calendar_days"] for row in rows)
        source_capture_offsets = Counter(
            row.get(
                "source_minus_source_capture_calendar_days",
                row["source_minus_capture_calendar_days"],
            )
            for row in rows
        )
        data_matches = sum(offset == 0 for offset in data_offsets.elements())
        capture_matches = sum(offset == 0 for offset in capture_offsets.elements())
        source_capture_matches = sum(offset == 0 for offset in source_capture_offsets.elements())
        if len(rows) < 3:
            pattern = "insufficient_observations"
        elif len(data_offsets) == 1:
            pattern = "repeated_offset_observed_not_contract"
        else:
            pattern = "variable_offset_observed"
        sources.append(
            {
                "source": source,
                "observation_count": len(rows),
                "source_date_equals_target_count": data_matches,
                "source_date_equals_capture_count": capture_matches,
                "source_date_equals_source_capture_count": source_capture_matches,
                "source_minus_data_calendar_days": dict(sorted(data_offsets.items())),
                "source_minus_capture_calendar_days": dict(sorted(capture_offsets.items())),
                "source_minus_source_capture_calendar_days": dict(
                    sorted(source_capture_offsets.items())
                ),
                "observed_pattern": pattern,
                "observations": rows,
            }
        )
    return {
        "schema_version": 2,
        "audit_scope": "retained meta.json only; no raw files or network",
        "retention_start": RETENTION_START.strftime("%Y%m%d"),
        "audit_since": since.strftime("%Y%m%d"),
        "observation_count": len(observations),
        "source_count": len(sources),
        "sources": sources,
    }


def render_markdown(summary: dict[str, Any], diagnostics: list[str]) -> str:
    """Render a concise report while retaining per-capture date evidence."""
    lines = [
        "# 来源日期历史映射审计",
        "",
        f"- 审计边界：采集与目标数据日均不早于 `{summary['audit_since']}`；硬性保留边界为 `{summary['retention_start']}`。",
        "- 读取范围：仅保留期内 `meta.json`；不读取 raw 样本、不请求网络、不用目录名推断来源日期。",
        f"- 有效来源日期观察：{summary['observation_count']} 条，涉及 {summary['source_count']} 个来源。",
        "- 偏移单位：自然日；周末与节假日会影响自然日偏移，不等同于交易日延迟。",
        "",
        "## 来源汇总",
        "",
        "| 来源 | 样本数 | 来源日=目标日 | 来源日=运行日 | 来源日=逐源采集日 | 来源日-目标日 | 来源日-运行日 | 来源日-逐源采集日 | 观察结论 |",
        "|:--|--:|--:|--:|--:|:--|:--|:--|:--|",
    ]
    lines.extend(_render_source_summary_rows(summary["sources"]))
    lines.extend(
        [
            "",
            "`repeated_offset_observed_not_contract` 仅代表当前样本出现相同偏移，不能代替上游契约；"
            "`variable_offset_observed` 表示不能用固定的采集日/目标日换算来源日期。每条样本仍须优先使用来源自己的日期。",
            "",
            "## 逐次采集证据",
            "",
            "| 采集目录 | 实际运行日 | 逐源采集日 | 逐源采集日依据 | 目标数据日 | 来源 | 来源日期 | 日期依据 | 状态 | 来源日-目标日 | 来源日-运行日 | 来源日-逐源采集日 |",
            "|:--|:--|:--|:--|:--|:--|:--|:--|:--|--:|--:|--:|",
        ]
    )
    lines.extend(_render_observation_rows(summary["sources"]))
    if diagnostics:
        lines.extend(["", "## 未纳入或数据缺口", ""])
        lines.extend(f"- {item}" for item in diagnostics)
    lines.append("")
    return "\n".join(lines)


def _render_source_summary_rows(sources: list[dict[str, Any]]) -> list[str]:
    rows = []
    for source in sources:
        offsets = (
            ", ".join(
                f"{offset:+d}天×{count}"
                for offset, count in source["source_minus_data_calendar_days"].items()
            )
            or "—"
        )
        capture_offsets = (
            ", ".join(
                f"{offset:+d}天×{count}"
                for offset, count in source["source_minus_capture_calendar_days"].items()
            )
            or "—"
        )
        source_capture_offsets = (
            ", ".join(
                f"{offset:+d}天×{count}"
                for offset, count in source["source_minus_source_capture_calendar_days"].items()
            )
            or "—"
        )
        rows.append(
            f"| {source['source']} | {source['observation_count']} | "
            f"{source['source_date_equals_target_count']} | "
            f"{source['source_date_equals_capture_count']} | "
            f"{source['source_date_equals_source_capture_count']} | {offsets} | "
            f"{capture_offsets} | {source_capture_offsets} | "
            f"{source['observed_pattern']} |"
        )
    return rows


def _render_observation_rows(sources: list[dict[str, Any]]) -> list[str]:
    rows = []
    for source in sources:
        for row in source["observations"]:
            rows.append(
                f"| {row['folder']} | {row['capture_date']} | {row['source_capture_date']} | "
                f"{row['source_capture_date_basis']} | {row['target_data_date']} | "
                f"{row['source']} | {row['source_date']} | {row['source_date_basis']} | "
                f"{row.get('source_status') or 'unknown'} | "
                f"{row['source_minus_data_calendar_days']:+d} | "
                f"{row['source_minus_capture_calendar_days']:+d} | "
                f"{row['source_minus_source_capture_calendar_days']:+d} |"
            )
    return rows


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--since", default=RETENTION_START.strftime("%Y%m%d"))
    parser.add_argument("--format", choices=("md", "json"), default="md")
    parser.add_argument("--output", type=Path, help="可选输出路径；省略时打印到 stdout")
    args = parser.parse_args(argv)
    since = parse_date(args.since)
    if since is None:
        parser.error("--since 必须是有效日期")
    if since < RETENTION_START:
        parser.error(f"--since 不能早于保留边界 {RETENTION_START:%Y%m%d}")
    args.since_date = since
    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    observations, diagnostics = collect_observations(args.data_dir, args.since_date)
    summary = summarize_observations(observations, args.since_date)
    output = (
        json.dumps({**summary, "diagnostics": diagnostics}, ensure_ascii=False, indent=2)
        if args.format == "json"
        else render_markdown(summary, diagnostics)
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        sys.stdout.write(output + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

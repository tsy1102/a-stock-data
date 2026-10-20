"""Persistent, non-authoritative history for exploratory collision candidates."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 2
REPORT_SECTIONS = ("L1", "L4", "method_candidates", "method_candidate_frontier")
STATE_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "field_verification"
    / "collision_research_state.json.gz"
)
TEMP_DIR = Path(__file__).resolve().parents[1] / ".tmp"


def empty_state() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "updated": "", "runs": {}, "candidates": {}}


def load_state(path: str | Path = STATE_PATH) -> tuple[dict[str, Any], list[str], bool]:
    """Load the ledger; malformed or newer state is never eligible for overwrite."""
    state_path = Path(path)
    read_path = state_path
    legacy_path = state_path.with_suffix("") if state_path.name.endswith(".json.gz") else None
    if not read_path.is_file() and legacy_path is not None and legacy_path.is_file():
        read_path = legacy_path
    if not read_path.is_file():
        return empty_state(), [], True
    try:
        if read_path.suffix == ".gz":
            with gzip.open(read_path, "rt", encoding="utf-8") as handle:
                state = json.load(handle)
        else:
            with read_path.open("r", encoding="utf-8") as handle:
                state = json.load(handle)
    except (OSError, EOFError, UnicodeError, json.JSONDecodeError) as exc:
        return empty_state(), [f"研究台账读取失败，保留原文件且本轮不写回：{exc}"], False
    if not isinstance(state, dict):
        return empty_state(), ["研究台账顶层不是对象，保留原文件且本轮不写回"], False
    schema_version = state.get("schema_version")
    if type(schema_version) is not int or schema_version not in (1, SCHEMA_VERSION):
        return empty_state(), ["研究台账版本不受当前脚本支持，保留原文件且本轮不写回"], False
    if not isinstance(state.get("runs"), dict) or not isinstance(state.get("candidates"), dict):
        return empty_state(), ["研究台账 runs/candidates 格式无效，保留原文件且本轮不写回"], False
    for key, candidate in state["candidates"].items():
        if not isinstance(key, str) or not isinstance(candidate, dict):
            return empty_state(), ["研究台账候选记录格式无效，保留原文件且本轮不写回"], False
        observations = candidate.get("observations")
        if not isinstance(observations, list):
            return (
                empty_state(),
                ["研究台账候选 observations 格式无效，保留原文件且本轮不写回"],
                False,
            )
        if any(
            not isinstance(item, dict)
            or not isinstance(item.get("run_id"), str)
            or not isinstance(item.get("date"), str)
            or re.fullmatch(r"\d{8}", item.get("date", "")) is None
            or not isinstance(item.get("report_path"), str)
            or not isinstance(item.get("sections"), dict)
            for item in observations
        ):
            return (
                empty_state(),
                ["研究台账 observation 字段格式无效，保留原文件且本轮不写回"],
                False,
            )
    state["schema_version"] = SCHEMA_VERSION
    for candidate in state["candidates"].values():
        _refresh_candidate_summary(candidate)
    warnings = []
    if read_path != state_path or schema_version != SCHEMA_VERSION:
        warnings.append("研究台账已从旧 JSON 格式读取；下次探索运行会写入压缩格式")
    return state, warnings, True


def _pair_key(left: str, right: str) -> str:
    endpoints = sorted((left, right))
    payload = "\0".join(endpoints).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _run_id(report: dict[str, Any], report_path: str) -> str:
    signature = {
        "date": report.get("date"),
        "mode": report.get("collision_mode"),
        "trading_window": report.get("trading_window", []),
        "event_window": report.get("event_window", {}),
        "report_path": report_path.replace("\\", "/"),
    }
    if report.get("include_context") is True:
        signature["include_context"] = True
    encoded = json.dumps(signature, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]
    return f"{report.get('date', 'unknown')}:{digest}"


def _evidence_summary(candidate: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "level",
        "ratio",
        "overall_hit",
        "n_days",
        "n_pairs",
        "sample_count",
        "sample_dates",
        "distinct_days",
        "evidence_sources",
        "methods",
        "exploratory",
        "hub_flag",
    )
    return {key: candidate[key] for key in keys if key in candidate}


def _report_rows(report: dict[str, Any], section: str) -> Any:
    if section == "L1" and "actionable_L1" in report:
        return report.get("actionable_L1")
    return report.get(section, [])


def _candidate_groups(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for section in REPORT_SECTIONS:
        rows = _report_rows(report, section)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            left, right = row.get("left"), row.get("right")
            if not isinstance(left, str) or not left or not isinstance(right, str) or not right:
                continue
            if left == right:
                continue
            key = _pair_key(left, right)
            entry = grouped.setdefault(
                key,
                {"left": left, "right": right, "sections": {}},
            )
            section_rows = entry["sections"].setdefault(section, [])
            summary = _evidence_summary(row)
            if summary not in section_rows:
                section_rows.append(summary)
    return grouped


def candidate_pair_count(report: dict[str, Any]) -> int:
    """Return the number of unique field pairs represented in a report."""
    return len(_candidate_groups(report))


def update_state(
    state: dict[str, Any], report: dict[str, Any], report_path: str
) -> tuple[dict[str, Any], str, dict[str, int]]:
    """Record an exploratory report once, replacing a rerun of the same window."""
    if report.get("collision_mode") != "exploratory":
        raise ValueError("only exploratory reports can update collision research state")
    report_date = report.get("date")
    if not isinstance(report_date, str) or re.fullmatch(r"\d{8}", report_date) is None:
        raise ValueError("exploratory report date must be YYYYMMDD")
    run_id = _run_id(report, report_path)
    updated = json.loads(json.dumps(state, ensure_ascii=False))
    candidates = updated["candidates"]
    existing_run_keys = {
        key
        for key, entry in candidates.items()
        if any(item.get("run_id") == run_id for item in entry.get("observations", []))
    }
    historical_keys = {
        key
        for key, entry in candidates.items()
        if any(item.get("run_id") != run_id for item in entry.get("observations", []))
    }
    _remove_run_observations(candidates, run_id)
    groups = _candidate_groups(report)
    for key, group in groups.items():
        _append_candidate_observation(candidates, key, group, run_id, report_date, report_path)

    updated["runs"][run_id] = {
        "date": report_date,
        "mode": "exploratory",
        "include_context": (
            report.get("include_context")
            if isinstance(report.get("include_context"), bool)
            else None
        ),
        "report_path": report_path.replace("\\", "/"),
        "trading_window": report.get("trading_window", []),
        "event_window": report.get("event_window", {}),
        "candidate_pair_count": len(groups),
        "candidate_observation_count": sum(
            len(rows) for group in groups.values() for rows in group["sections"].values()
        ),
    }
    last_updated = updated.get("updated")
    if not isinstance(last_updated, str) or re.fullmatch(r"\d{8}", last_updated) is None:
        last_updated = report_date
    updated["updated"] = max(last_updated, report_date)
    newly_tracked = len(set(groups) - historical_keys - existing_run_keys)
    previously_tracked = len(set(groups) & historical_keys)
    return (
        updated,
        run_id,
        {
            "current_candidate_pairs": len(groups),
            "new_candidate_pairs": newly_tracked,
            "previously_tracked_pairs": previously_tracked,
            "total_candidate_pairs": len(candidates),
        },
    )


def _remove_run_observations(candidates: dict[str, Any], run_id: str) -> None:
    for key in list(candidates):
        entry = candidates[key]
        observations = entry.get("observations", [])
        if not isinstance(observations, list):
            raise ValueError(f"research candidate {key} observations must be a list")
        entry["observations"] = [item for item in observations if item.get("run_id") != run_id]
        if not entry["observations"]:
            del candidates[key]
        else:
            _refresh_candidate_summary(entry)


def _refresh_candidate_summary(entry: dict[str, Any]) -> None:
    observations = entry.get("observations", [])
    if not observations:
        entry["observation_count"] = 0
        entry.pop("latest_evidence", None)
        return
    if any(not isinstance(item.get("date"), str) for item in observations):
        raise ValueError("research candidate observations must include a date")
    entry["observation_count"] = len(observations)
    entry["first_seen"] = min(item["date"] for item in observations)
    entry["last_seen"] = max(item["date"] for item in observations)
    latest = max(
        enumerate(observations),
        key=lambda indexed: (indexed[1]["date"], indexed[0]),
    )[1]
    entry["latest_evidence"] = latest.get("sections", {})


def _append_candidate_observation(
    candidates: dict[str, Any],
    key: str,
    group: dict[str, Any],
    run_id: str,
    report_date: str,
    report_path: str,
) -> None:
    entry = candidates.get(key)
    if not isinstance(entry, dict):
        entry = {
            "left": group["left"],
            "right": group["right"],
            "first_seen": report_date,
            "last_seen": report_date,
            "observation_count": 0,
            "observations": [],
        }
        candidates[key] = entry
    entry["left"] = group["left"]
    entry["right"] = group["right"]
    entry["first_seen"] = min(entry.get("first_seen", report_date), report_date)
    entry["last_seen"] = max(entry.get("last_seen", report_date), report_date)
    observation = {
        "run_id": run_id,
        "date": report_date,
        "report_path": report_path.replace("\\", "/"),
        "sections": group["sections"],
    }
    entry["observations"].append(observation)
    _refresh_candidate_summary(entry)


def annotate_report(
    report: dict[str, Any], state: dict[str, Any], current_run_id: str | None
) -> int:
    """Attach compact prior-run references to candidates that reappear."""
    candidates = state.get("candidates", {})
    matched: set[str] = set()
    for section in REPORT_SECTIONS:
        rows = _report_rows(report, section)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            left, right = row.get("left"), row.get("right")
            if not isinstance(left, str) or not isinstance(right, str):
                continue
            key = _pair_key(left, right)
            entry = candidates.get(key)
            if not isinstance(entry, dict):
                continue
            observations = entry.get("observations", [])
            if not isinstance(observations, list):
                continue
            prior = [item for item in observations if item.get("run_id") != current_run_id]
            if not prior:
                continue
            matched.add(key)
            latest_prior = max(
                enumerate(prior),
                key=lambda indexed: (indexed[1].get("date", ""), indexed[0]),
            )[1]
            row["research_history"] = {
                "first_seen": entry.get("first_seen"),
                "last_seen": entry.get("last_seen"),
                "prior_observation_count": len(prior),
                "latest_report": latest_prior.get("report_path"),
            }
    return len(matched)


def save_state(state: dict[str, Any], path: str | Path = STATE_PATH) -> None:
    """Atomically write a compact gzip ledger using the repository's ignored .tmp directory."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    serialized_state = {
        "schema_version": SCHEMA_VERSION,
        "updated": state.get("updated", ""),
        "runs": state.get("runs", {}),
        "candidates": {
            key: {name: value for name, value in candidate.items() if name != "latest_evidence"}
            for key, candidate in state.get("candidates", {}).items()
        },
    }
    descriptor, temporary = tempfile.mkstemp(
        prefix="collision_research_", suffix=".tmp", dir=TEMP_DIR
    )
    try:
        if target.suffix == ".gz":
            with os.fdopen(descriptor, "wb") as raw_handle:
                compressed = gzip.GzipFile(
                    fileobj=raw_handle,
                    mode="wb",
                    filename="",
                    compresslevel=9,
                    mtime=0,
                )
                with io.TextIOWrapper(compressed, encoding="utf-8", newline="\n") as handle:
                    json.dump(serialized_state, handle, ensure_ascii=False, indent=2)
                    handle.write("\n")
        else:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(serialized_state, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

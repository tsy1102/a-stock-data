"""Generate non-authoritative lexical clues for observed registry fields."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from scripts import field_registry_api as FRA
from scripts import source_lineage_api as SLA

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = (
    PROJECT_ROOT
    / "docs"
    / "field_verification"
    / "20261014"
    / "20261014_alphabetic_field_name_inventory.csv"
)
_EXCLUDED_NAME_FORMS = {
    "numeric_api_index",
    "api_route_or_nested_path",
    "composite_reference_not_single_field",
    "sample_or_record_identifier",
    "sample_or_security_identifier",
}
_IDENTIFIER_ONLY = re.compile(r"^(?:f|field)?\d+$", re.IGNORECASE)


def _display_path(path: str | Path) -> str:
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def _runtime_parts(field_id: str) -> tuple[str, str] | None:
    if "." in field_id:
        return tuple(field_id.split(".", 1))  # type: ignore[return-value]
    if "[" in field_id:
        alias, code = field_id.split("[", 1)
        return alias, f"[{code}"
    return None


def _tokenize(code: str) -> list[str]:
    leaf = code.rsplit(".", 1)[-1]
    split = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", leaf)
    split = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", split)
    return re.findall(r"[A-Za-z]+|\d+", split.replace("_", " "))


def _read_inventory(path: Path) -> tuple[dict[tuple[str, str], dict[str, str]], str | None]:
    if not path.is_file():
        return {}, f"name candidate inventory is missing: {path}"
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
    except (OSError, csv.Error, UnicodeError) as exc:
        return {}, f"name candidate inventory could not be read: {type(exc).__name__}: {exc}"
    records: dict[tuple[str, str], dict[str, str]] = {}
    duplicate_keys: set[tuple[str, str]] = set()
    for row in rows:
        source = (row.get("source") or "").strip()
        code = (row.get("path") or row.get("code") or "").strip()
        if not source or not code:
            continue
        key = (source, code)
        if key in records:
            duplicate_keys.add(key)
        else:
            records[key] = {str(name): str(value or "").strip() for name, value in row.items()}
    for key in duplicate_keys:
        records.pop(key, None)
    warning = (
        f"name candidate inventory has {len(duplicate_keys)} ambiguous exact identities; they were ignored"
        if duplicate_keys
        else None
    )
    return records, warning


def _metadata_needs_review(record: dict[str, Any]) -> bool:
    if record.get("status") != "verified":
        return True
    return any(not str(record.get(key) or "").strip() for key in ("canonical", "meaning", "unit"))


def build_field_name_candidates(
    store: dict[str, dict[str, Any]],
    target_ids: list[str],
    registry_path: str | Path,
    lineage: dict[str, Any],
    inventory_path: str | Path = DEFAULT_INVENTORY,
) -> dict[str, Any]:
    """Match observed target paths to exact registry identities and lexical clues."""
    try:
        registry = json.loads(Path(registry_path).read_text(encoding="utf-8"))
        source_fields = FRA.source_field_records(registry)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return {
            "status": "unavailable",
            "candidate_count": 0,
            "candidates": [],
            "diagnostics": [f"registry unavailable for name clues: {type(exc).__name__}: {exc}"],
        }

    inventory, inventory_warning = _read_inventory(Path(inventory_path))
    owners: dict[tuple[str, str], set[tuple[str, str]]] = defaultdict(set)
    records: dict[tuple[str, str], dict[str, Any]] = {}
    for record in source_fields:
        source, code = record["source"], record["code"]
        identity = (source, code)
        records[identity] = record
        aliases = SLA.runtime_aliases_for_source(source, lineage)
        if source in {"ZHB-tdxstat", "ZHB-tdxstat2", "ZHB-tipinfo"}:
            aliases = ["zhb"]
        for alias in aliases:
            owners[(alias, SLA.normalize_runtime_field_code(alias, code))].add(identity)

    diagnostics = [inventory_warning] if inventory_warning else []
    candidates: list[dict[str, Any]] = []
    unmapped = 0
    ambiguous = 0
    for field_id in target_ids:
        parts = _runtime_parts(field_id)
        if parts is None:
            continue
        alias, runtime_code = parts
        identity_set = owners.get(
            (alias, SLA.normalize_runtime_field_code(alias, runtime_code)), set()
        )
        if len(identity_set) != 1:
            if len(identity_set) > 1:
                ambiguous += 1
            else:
                unmapped += 1
            continue
        identity = next(iter(identity_set))
        record = records[identity]
        code = identity[1]
        if not re.search(r"[A-Za-z]", code) or not _metadata_needs_review(record):
            continue
        candidate = inventory.get(identity, {})
        name_form = candidate.get("name_form", "runtime_tokenization_only")
        if name_form in _EXCLUDED_NAME_FORMS or _IDENTIFIER_ONLY.fullmatch(code):
            continue
        tokens = candidate.get("lexical_tokens") or " ".join(_tokenize(code))
        hint = candidate.get("lexical_token_hint_not_meaning", "")
        field_info = store.get(field_id, {})
        values = field_info.get("vals", {})
        dates = sorted(
            {
                str(key[1])
                for key in values
                if isinstance(key, tuple) and len(key) > 1 and isinstance(key[1], str)
            }
        )
        candidates.append(
            {
                "source": identity[0],
                "path": code,
                "runtime_field": field_id,
                "registry_status": record.get("status", "unverified"),
                "review_scope": (
                    "unverified_semantics"
                    if record.get("status") != "verified"
                    else "verified_metadata_gap"
                ),
                "canonical": record.get("canonical"),
                "current_meaning": record.get("meaning"),
                "unit": record.get("unit"),
                "name_form": name_form,
                "lexical_tokens": tokens,
                "lexical_hint_not_meaning": hint,
                "inventory_path": _display_path(inventory_path),
                "sample_count": len(values),
                "sample_dates": dates,
                "evidence_basis": "field name only; requires value and independent-source review",
            }
        )

    candidates.sort(
        key=lambda item: (
            not bool(item["lexical_hint_not_meaning"]),
            -item["sample_count"],
            item["source"],
            item["path"],
        )
    )
    return {
        "status": "ok",
        "inventory_path": _display_path(inventory_path),
        "candidate_count": len(candidates),
        "hinted_candidate_count": sum(
            bool(item["lexical_hint_not_meaning"]) for item in candidates
        ),
        "tokenization_only_count": sum(not item["lexical_hint_not_meaning"] for item in candidates),
        "ambiguous_runtime_paths": ambiguous,
        "unmapped_runtime_paths": unmapped,
        "candidates": candidates,
        "diagnostics": diagnostics,
        "promotion_policy": "name candidates are non-authoritative and never change registry status",
    }


def append_field_name_candidate_report(report_md: str, result: dict[str, Any]) -> str:
    lines = [report_md.rstrip(), "", "## 字母字段名语义提示（仅候选）", ""]
    if not isinstance(result, dict) or result.get("status") != "ok":
        details = (result.get("diagnostics") or ["候选提示生成不可用"])[0]
        lines.append(f"_本轮未生成字段名提示：{details}_")
        return "\n".join(lines) + "\n"

    candidates = result.get("candidates") or []
    lines.append(
        f"窗口内观察到 {result.get('candidate_count', 0)} 条需审阅的字母字段路径："
        f"含词义线索 {result.get('hinted_candidate_count', 0)} 条，"
        f"仅拆词 {result.get('tokenization_only_count', 0)} 条。"
    )
    lines.append(
        f"完整逐条记录保存在碰撞 JSON；名称线索清单：`{result.get('inventory_path', '')}`。"
    )
    lines.append(
        "> 拼音、英文、缩写和混合拆词只用于检索候选；必须结合原始值、接口定义和独立来源复核，"
        "不得据此定案或改写主字典。"
    )
    lines.extend(
        [
            "",
            "| 逐源字段路径 | 状态/审阅范围 | 名称形式与拆词 | 词义线索（非释义） | 样本日期 |",
            "|:--|:--|:--|:--|:--|",
        ]
    )
    display_limit = 100
    for item in candidates[:display_limit]:
        lines.append(
            f"| `{item['source']}::{item['path']}` | {item['registry_status']} / {item['review_scope']} | "
            f"{item['name_form']}: {_cell(item['lexical_tokens'])} | "
            f"{_cell(item['lexical_hint_not_meaning'])} | "
            f"{_cell(', '.join(item['sample_dates']))} |"
        )
    if len(candidates) > display_limit:
        lines.append(
            f"\nMarkdown 显示前 {display_limit} 条；其余 {len(candidates) - display_limit} 条完整保留在 JSON。"
        )
    if not candidates:
        lines.append("| — | 当前窗口没有需审阅的字母字段 | — | — | — |")
    lines.append("")
    return "\n".join(lines) + "\n"


def _cell(value: Any) -> str:
    return str(value if value not in (None, "") else "—").replace("|", "\\|").replace("\n", " ")

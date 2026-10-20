#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the field dictionary entrypoint and the unresolved-field queue."""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Any

for stream in (sys.stdout, sys.stderr):
    if stream is not None and hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
DICT = os.path.join(DOCS_DIR, "field_dict.md")
UNKNOWN = os.path.join(DOCS_DIR, "unknown_fields.md")
SOURCE_MAP = os.path.join(DOCS_DIR, "source_repository_map.md")
METADATA_GAPS = os.path.join(DOCS_DIR, "field_metadata_gaps.md")
AGGREGATE_REVIEW = os.path.join(DOCS_DIR, "field_aggregate_review.md")

sys.path.insert(0, SCRIPT_DIR)
import field_registry_api as fra
import source_lineage_api as sla


def _cell(value: Any) -> str:
    text = str(value or "").replace("\r", " ").replace("\n", " ").replace("|", "\\|")
    return text.strip() or "—"


def _source_field_counts(records: list[dict[str, Any]]) -> Counter:
    return Counter(record.get("status", "unverified") for record in records)


_STATUS_RESOLUTION_NOTES = {
    "registry_status_only_single_source": "只有来源自身状态，历史聚合信息不足以进一步归属",
    "aggregate_status_scope_unresolved": "历史聚合状态尚不能可靠映射到逐源身份",
    "matched": "历史逐源状态与聚合状态一致，但仍未定案",
    "status_missing": "缺少可用的历史状态记录",
    "reference_meaning_unresolved": "含义缺失或属性未能对齐，不能作为已定语义",
    "reference_semantic_attribute_conflict": "来源参考记录中的含义或单位互相冲突",
}


def _meaning_annotation_state(record: dict[str, Any]) -> str:
    """Describe whether a meaning annotation exists; this is not a truth claim."""
    if "meaning_missing" in fra.source_field_semantic_issues(record):
        return "含义栏为空/占位"
    return "含义栏有文本（仍未验证）"


def _status_resolution(record: dict[str, Any]) -> str:
    return str(record.get("status_resolution") or "status_missing")


_SOURCE_ROLE_LABELS = {
    "provider_component": "已映射提供方的接口组件",
    "service_endpoint": "服务接口（底层来源族未确认）",
    "framework_reference": "多源框架参考（非独立来源）",
    "historical_unattributed": "历史未归属（不作来源锚）",
    "retired_service_endpoint": "已退役的托管服务（仅保留历史证据）",
    "documented_contract_anchor": "官方文档定义字段语义的契约锚（底层数据来源未确认）",
}


def _source_role_label(source: dict[str, Any]) -> str:
    if source.get("status") in {"historical", "retired"}:
        return _SOURCE_ROLE_LABELS.get(
            str(source.get("source_role") or ""), "已退役来源（仅保留历史证据）"
        )
    if source.get("status") == "retired_duplicate":
        replacement = source.get("replacement_source")
        if replacement:
            return f"已停用的重复采集入口（历史身份；由 {replacement} 覆盖）"
        return "已停用的重复采集入口（仅留历史身份）"
    role = source.get("source_role")
    if isinstance(role, str) and role in _SOURCE_ROLE_LABELS:
        return _SOURCE_ROLE_LABELS[role]
    return "运行时来源身份（独立性按来源谱系判定）"


def render_field_dict(registry: dict[str, Any]) -> str:
    records = fra.source_field_records(registry)
    if not records:
        raise ValueError(
            "registry.source_fields is empty; refusing to generate an incomplete entrypoint"
        )
    counts = _source_field_counts(records)
    verified_records = [record for record in records if record.get("status") == "verified"]
    missing_meaning = sum(
        "meaning_missing" in fra.source_field_semantic_issues(record) for record in verified_records
    )
    missing_canonical = sum(not record.get("canonical") for record in verified_records)
    sources = registry.get("sources", [])
    verify_sources = [source for source in sources if source.get("verify_file")]
    lines = [
        "# 主字段字典",
        "",
        "> 本页是字段治理入口与权威规则索引。机器字段记录以 `field_registry.json` 为准；",
        "> 字段状态、来源路径和证据均按 `(source, 完整 code path)` 登记。",
        "> 本页及矩阵/待破解队列由 `scripts/gen_field_dict.py` 生成，请勿手改。",
        "",
        "## 权威顺序",
        "",
        "1. `field_verification/field_registry.json`：逐源字段、完整路径、状态与证据的机器权威。",
        "2. `field_verification/source_lineage.json`：运行时来源别名、独立来源族与仓库关系。",
        "3. `field_verification/source_identity_reclassifications.json`：旧混合来源字段在历史档案与当前来源身份之间的显式映射。",
        "4. 本页：治理入口；`field_matrix.md` 与 `unknown_fields.md` 是 registry 派生视图。",
        "5. `field_source_reference.md`：重整前完整原文，逐字节保留作历史证据；不得用它覆盖当前状态。",
        "",
        "## 状态与锚点规则",
        "",
        "- 普通来源的 `verified` 字段要成为独立来源碰撞锚，还要求含义非空且非占位、含义/单位无冲突或对齐歧义、来源独立性已确认，并且运行时来源与完整路径精确匹配。",
        "- `source_role=documented_contract_anchor` 且字段证据为 `official_contract` 时，官方文档可直接确认该来源字段含义；其多日强匹配单列 `L1-C`，不声称上游来源独立，也不自动定案。",
        "- 规范名的别名差异不会单独阻止碰撞；字段含义缺失/占位或含义/单位存在冲突时，碰撞器会将该 verified 路径重新纳入待破解目标，并排除为锚。",
        "- `unverified`、`candidate` 是默认破解目标；`conflict` 可作为待复核目标但不能作锚，碰撞候选不能替代证据冲突复核。",
        "- `disproved` 单独归档，不进入默认破解队列。",
        "- 未登记来源、路径不完整或来源独立性未确认时，不参与默认 L1 定案。",
        "- AxData 是多提供方接口框架；当前 `stock_shortline_indicators_tdx` 属于 TDX 来源族。AxData 接口盘点只作框架参考，不能作为独立来源或锚；详见 [`axdata_field_reconciliation_20261010.md`](axdata_field_reconciliation_20261010.md)。",
        "- Levistock 是多源客户端包装库。已归属的 KPH 记录映射到 KPH 来源族；FTShare 私有托管 MCP 集成已退役，其字段仅留作历史证据，底层来源未确认、不作独立锚。其余历史记录保留为未归属证据，不计为 Levistock 数据源；字段映射见 [`source_identity_reclassifications.json`](field_verification/source_identity_reclassifications.json) 与 [`levistock_source_reconciliation_20261010.md`](field_verification/levistock_source_reconciliation_20261010.md)。",
        "",
        "## 当前覆盖",
        "",
        f"- 来源身份与参考登记：{len(sources)} 项；是否可作独立锚由来源谱系单独判定。",
        f"- 逐源字段路径：{len(records)} 条；verified {counts['verified']}、unverified {counts['unverified']}、candidate {counts['candidate']}、conflict {counts['conflict']}、disproved {counts['disproved']}。",
        "- 矩阵：[`field_matrix.md`](field_matrix.md)。",
        "- 待破解与状态冲突：[`unknown_fields.md`](unknown_fields.md)。",
        "- 来源与 GitHub 仓库映射：[`source_repository_map.md`](source_repository_map.md)。",
        f"- 已验证字段描述缺口：{missing_meaning} 条含义为空/占位、{missing_canonical} 条缺少规范名，见 [`field_metadata_gaps.md`](field_metadata_gaps.md)；质量问题会阻止其作为碰撞锚。",
        "- 同短 code 的聚合歧义、缺失定义和疑似合并文本单独列在 [`field_aggregate_review.md`](field_aggregate_review.md)；该清单不覆盖逐源定义，也不自动拆分字段。",
        "- 完整历史正文：[`field_source_reference.md`](field_source_reference.md)。",
        "",
        "## 规则和方法",
        "",
        "- 对撞规则：[`field_verification/COLLISION_RULES.md`](field_verification/COLLISION_RULES.md)。",
        "- 破解方法：[`field_verification/CRACKING_METHODOLOGY.md`](field_verification/CRACKING_METHODOLOGY.md)。",
        "- 字段验证记录：[`field_verification/`](field_verification/)。每条结论须保留日期、样本、来源和证据。",
        "- 已验证字段描述缺口：[`field_metadata_gaps.md`](field_metadata_gaps.md)。",
        "- 对撞结果不会自动定案；人工复核和注册表同步流程见 [`field_verification/ADJUDICATION_WORKFLOW.md`](field_verification/ADJUDICATION_WORKFLOW.md)。",
        "- 无独立数值锚但有权威单源接口/协议定义的字段，可按上游契约流程核验；该结论不建立跨源映射或来源锚。",
        "- 来源分组及 GitHub 对应关系以 `field_verification/source_lineage.json` 为准；未确认项明确标为 unconfirmed。",
        "",
        "## 来源身份与框架参考索引",
        "",
        "登记类别说明：框架、包装适配器、服务接口与历史未归属记录均明确标注；跨源定案仍按来源谱系的 `independence_family` 和 `anchor_eligible` 判定。",
        "",
        "| 来源身份 | 登记性质 | 分字典 | 主要章节 |",
        "|:--|:--|:--|:--|",
    ]
    for source in verify_sources:
        verify_file = _cell(source.get("verify_file"))
        name = _cell(source.get("name"))
        section = _cell((source.get("section_patterns") or [""])[0])
        role = _cell(_source_role_label(source))
        lines.append(
            f"| {name} | {role} | [verify/{verify_file}](verify/{verify_file}) | {section} |"
        )
    lines.extend(
        [
            "",
            "## 维护命令",
            "",
            "```powershell",
            ".\\scripts\\run_with_system_python.ps1 scripts\\gen_field_dict.py",
            ".\\scripts\\run_with_system_python.ps1 scripts\\gen_field_matrix.py",
            ".\\scripts\\run_with_system_python.ps1 scripts\\verify_sync_check.py",
            ".\\scripts\\run_with_system_python.ps1 scripts\\registry_parity.py",
            ".\\scripts\\run_with_system_python.ps1 scripts\\refresh_field_registry_projection.py --check",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def render_unknown_fields(registry: dict[str, Any]) -> str:
    records = fra.source_field_records(registry)
    if not records:
        raise ValueError(
            "registry.source_fields is empty; refusing to generate an incomplete queue"
        )
    source_statuses = {
        str(source.get("name")): str(source.get("status", "active"))
        for source in registry.get("sources", [])
        if isinstance(source, dict) and source.get("name")
    }
    historical_statuses = {"historical", "retired"}
    active_records = [
        record
        for record in records
        if source_statuses.get(str(record.get("source")), "active") not in historical_statuses
    ]
    historical_records = [
        record
        for record in records
        if source_statuses.get(str(record.get("source")), "active") in historical_statuses
    ]
    counts = _source_field_counts(active_records)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in active_records:
        status = record.get("status", "unverified")
        if status in {"unverified", "candidate", "conflict", "disproved"}:
            groups[status].append(record)
    verified_quality_review = [
        record
        for record in active_records
        if record.get("status") == "verified" and fra.source_field_semantic_issues(record)
    ]
    unverified = groups["unverified"]
    meaning_counts = Counter(_meaning_annotation_state(record) for record in unverified)
    resolution_counts = Counter(_status_resolution(record) for record in unverified)

    lines = [
        "# 未知字段与状态冲突队列",
        "",
        "> 由 `field_registry.json.source_fields` 自动生成；每行身份是来源加完整 code path。",
        "> 修改状态必须先核对 `reference_evidence` 与 `registry_aggregate`，并保留证据来源。",
        "> 碰撞候选须人工复核后使用 `apply_collision_adjudications.py` 同步状态；流程见 `field_verification/ADJUDICATION_WORKFLOW.md`。",
        "> 聚合层的同码异义与定义缺口见 [`field_aggregate_review.md`](field_aggregate_review.md)，不代表逐源记录状态冲突。",
        "",
        f"> 注册字段路径 {len(records)}；日常来源路径 {len(active_records)}：unverified {counts['unverified']}、candidate {counts['candidate']}、conflict {counts['conflict']}、disproved {counts['disproved']}；历史来源路径 {len(historical_records)}。",
        f"> 另有 {len(verified_quality_review)} 条虽标 verified、但含义/单位元数据未达到碰撞锚条件；这些记录会重新进入碰撞目标，详见 [字段元数据复核](field_metadata_gaps.md)。",
        "> 以下两组未验证字段统计是不同维度，不能相加：含义栏文本只表示存在文字，不代表语义正确；状态判定反映旧字典状态证据能否映射到逐源身份。",
        "",
        "## 未验证字段的复核分层",
        "",
        "### 含义栏状态（仅表示文字是否存在）",
        "",
        "| 分类 | 数量 |",
        "|:--|--:|",
    ]
    for label in ("含义栏为空/占位", "含义栏有文本（仍未验证）"):
        lines.append(f"| {label} | {meaning_counts[label]} |")
    lines.extend(
        [
            "",
            "### 历史状态证据的解析结果",
            "",
            "| 状态判定 | 数量 | 说明 |",
            "|:--|--:|:--|",
        ]
    )
    for resolution, count in sorted(resolution_counts.items()):
        note = _STATUS_RESOLUTION_NOTES.get(resolution, "按注册表原始状态判定代码保留")
        lines.append(f"| `{_cell(resolution)}` | {count} | {_cell(note)} |")
    headings = [
        ("conflict", "一、状态冲突（禁止作为锚点，优先复核）"),
        ("candidate", "二、候选字段"),
        ("unverified", "三、待破解字段"),
        ("disproved", "四、已证伪（默认不重复破解）"),
    ]
    for status, heading in headings:
        group = sorted(groups[status], key=lambda record: (record["source"], record["code"]))
        lines.extend(["", f"## {heading}（{len(group)}）", ""])
        if not group:
            lines.append("_无记录。_")
            continue
        lines.extend(
            [
                "| 来源 | 完整 code path | 规范名 | 含义 | 单位 | 含义栏提示 | 状态判定 | 证据章节 |",
                "|:--|:--|:--|:--|:--|:--|:--|:--|",
            ]
        )
        for record in group:
            sections = record.get("sections") or (
                [record.get("section")] if record.get("section") else []
            )
            lines.append(
                "| {source} | `{code}` | {canonical} | {meaning} | {unit} | {meaning_state} | {resolution} | {section} |".format(
                    source=_cell(record.get("source")),
                    code=str(record.get("code", "")).replace("`", "\\`"),
                    canonical=_cell(record.get("canonical")),
                    meaning=_cell(record.get("meaning")),
                    unit=_cell(record.get("unit")),
                    meaning_state=_meaning_annotation_state(record),
                    resolution=_cell(_status_resolution(record)),
                    section=_cell("；".join(sections)),
                )
            )
    if historical_records:
        historical_by_source: dict[str, Counter] = defaultdict(Counter)
        for record in historical_records:
            historical_by_source[str(record.get("source", "unknown"))][
                str(record.get("status", "unverified"))
            ] += 1
        lines.extend(
            [
                "",
                "## 已退出来源字段（仅历史证据，不进入默认破解）",
                "",
                "| 来源 | 路径数 | verified | unverified | candidate | conflict | disproved |",
                "|:--|--:|--:|--:|--:|--:|--:|",
            ]
        )
        for source, status_counts in sorted(historical_by_source.items()):
            lines.append(
                f"| {_cell(source)} | {sum(status_counts.values())} | "
                f"{status_counts['verified']} | {status_counts['unverified']} | "
                f"{status_counts['candidate']} | {status_counts['conflict']} | "
                f"{status_counts['disproved']} |"
            )
        lines.append("")
    lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def render_field_aggregate_review(registry: dict[str, Any]) -> str:
    """Render aggregate-only ambiguity and composite-text candidates."""
    records = fra.source_field_records(registry)
    if not records:
        raise ValueError("registry.source_fields is empty; refusing to generate aggregate review")
    historical_statuses = {"historical", "retired"}
    source_statuses = {
        str(source.get("name")): str(source.get("status", "active"))
        for source in registry.get("sources", [])
        if isinstance(source, dict) and source.get("name")
    }
    records = [
        record
        for record in records
        if source_statuses.get(str(record.get("source")), "active") not in historical_statuses
    ]
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[record["code"]].append(record)
    aggregates = {row["code"]: row for row in fra.build_aggregate_fields(records)}
    review_groups = []
    for code in sorted(groups):
        aggregate = aggregates[code]
        source_rows = groups[code]
        multi_source = len({row["source"] for row in source_rows}) > 1
        has_any_metadata = any(
            str(row.get(key) or "").strip()
            for row in source_rows
            for key in ("canonical", "meaning", "unit")
        )
        issues = set(aggregate["aggregation_issues"])
        if (
            aggregate["aggregation_status"] == "ambiguous"
            or "source_statuses_differ" in issues
            or "source_status_conflict" in issues
            or (
                multi_source
                and aggregate["aggregation_status"] == "incomplete"
                and has_any_metadata
            )
        ):
            review_groups.append(aggregate)
    composite_pattern = re.compile(r"[/／+＋、;；]|(?:或|兼)")
    composites = [
        row
        for row in records
        if composite_pattern.search(
            " ".join(str(row.get(key) or "") for key in ("canonical", "meaning"))
        )
    ]
    ambiguous = sum(row["aggregation_status"] == "ambiguous" for row in review_groups)
    incomplete = sum(row["aggregation_status"] == "incomplete" for row in review_groups)
    lines = [
        "# 字段聚合歧义与待拆分复核",
        "",
        "> 本文由 `field_registry.json.source_fields` 生成。逐源完整路径记录是权威定义；本文只揭示按短 code 聚合时无法安全呈现的差异。",
        "> `aggregation_status` 只描述兼容聚合视图，不会改写逐源 `status`。疑似合并文本由分隔符启发式识别，仅供人工检查，不自动拆字段或定案。",
        "> 本文统计的定义缺口仅限列出的复核组；单来源或全空的定义缺口仍见 [元数据缺口](field_metadata_gaps.md) 与 [未知字段队列](unknown_fields.md)。",
        "",
        f"> 聚合歧义 {ambiguous} 个 code；聚合定义不完整 {incomplete} 个 code；疑似合并文本 {len(composites)} 条逐源记录。",
        "",
        "## 同码聚合存在差异或定义缺口",
        "",
    ]
    if not review_groups:
        lines.append("_无记录。_")
    for aggregate in review_groups:
        code = aggregate["code"]
        lines.extend(
            [
                f"### `{code}` — {aggregate['aggregation_status']}",
                "",
                f"聚合问题：{_cell('；'.join(aggregate['aggregation_issues']))}；聚合状态：`{aggregate['status']}`。",
                "",
                "| 来源身份 | 规范名 | 含义 | 单位 | 逐源状态 |",
                "|:--|:--|:--|:--|:--|",
            ]
        )
        for record in sorted(groups[code], key=lambda item: (item["source"], item["code"])):
            lines.append(
                f"| {_cell(record['source'])} · `{_cell(record['code'])}` | "
                f"{_cell(record.get('canonical'))} | {_cell(record.get('meaning'))} | "
                f"{_cell(record.get('unit'))} | `{_cell(record.get('status'))}` |"
            )
        lines.append("")
    lines.extend(
        [
            "## 疑似合并文本（启发式候选）",
            "",
            "下列规范名或含义包含 `/`、`+`、`、`、分号、`或` 或 `兼`。分隔符可能只是正常描述格式，需结合原始路径和证据判断。",
            "",
        ]
    )
    if not composites:
        lines.append("_无记录。_")
    else:
        lines.extend(
            [
                "| 来源身份 | 完整 code path | 规范名 | 含义 | 状态 |",
                "|:--|:--|:--|:--|:--|",
            ]
        )
        for record in sorted(composites, key=lambda item: (item["source"], item["code"])):
            lines.append(
                f"| {_cell(record['source'])} | `{_cell(record['code'])}` | "
                f"{_cell(record.get('canonical'))} | {_cell(record.get('meaning'))} | "
                f"`{_cell(record.get('status'))}` |"
            )
    lines.append("")
    return "\n".join(lines)


def render_field_metadata_gaps(registry: dict[str, Any]) -> str:
    records = fra.source_field_records(registry)
    if not records:
        raise ValueError("registry.source_fields is empty; refusing to generate a metadata audit")
    gaps = [
        record
        for record in records
        if record.get("status") == "verified"
        and (
            not str(record.get("canonical") or "").strip()
            or fra.source_field_semantic_issues(record)
        )
    ]
    missing_meaning = sum(
        "meaning_missing" in fra.source_field_semantic_issues(record) for record in gaps
    )
    missing_canonical = sum(not str(record.get("canonical") or "").strip() for record in gaps)
    issue_counts = Counter(
        issue for record in gaps for issue in fra.source_field_semantic_issues(record)
    )
    issue_labels = {
        "meaning_missing": "含义为空/占位",
        "meaning_conflict": "含义冲突",
        "unit_conflict": "单位冲突",
        "meaning_alignment_ambiguous": "含义分组未能逐字段对齐",
        "unit_alignment_ambiguous": "单位分组未能逐字段对齐",
    }
    lines = [
        "# 已验证字段的元数据与锚点复核",
        "",
        "> 由 `field_registry.json.source_fields` 自动生成；逐源状态仍保留原始登记，但下表记录不会作为碰撞锚，且会重新进入待破解目标。",
        "> 规范名别名差异单独审查，不自动阻止锚；含义/单位冲突、无法对齐或含义为空/占位会阻止锚。",
        "> 请依据来源定义、原始样本和已存证据逐条复核，禁止按相邻字段或字段代码猜测含义。",
        "",
        f"> 复核记录 {len(gaps)} 条；含义为空/占位 {missing_meaning} 条；规范名为空 {missing_canonical} 条。",
        "> 语义问题："
        + "；".join(
            f"{issue_labels.get(issue, issue)} {count} 条"
            for issue, count in sorted(issue_counts.items())
        ),
        "",
    ]
    if not gaps:
        lines.append("_没有需复核锚点元数据的 verified 字段。_")
        return "\n".join(lines) + "\n"
    lines.extend(
        [
            "| 来源 | 完整 code path | 规范名 | 含义 | 单位 | 复核原因 | 证据章节 |",
            "|:--|:--|:--|:--|:--|:--|:--|",
        ]
    )
    for record in sorted(gaps, key=lambda item: (item["source"], item["code"])):
        sections = record.get("sections") or (
            [record.get("section")] if record.get("section") else []
        )
        issues = fra.source_field_semantic_issues(record)
        if not str(record.get("canonical") or "").strip():
            issues = ["canonical_missing", *issues]
        reason_labels = {"canonical_missing": "规范名为空", **issue_labels}
        lines.append(
            "| {source} | `{code}` | {canonical} | {meaning} | {unit} | {reason} | {section} |".format(
                source=_cell(record.get("source")),
                code=str(record.get("code", "")).replace("`", "\\`"),
                canonical=_cell(record.get("canonical")),
                meaning=_cell(record.get("meaning")),
                unit=_cell(record.get("unit")),
                reason=_cell("；".join(reason_labels.get(issue, issue) for issue in issues)),
                section=_cell("；".join(sections)),
            )
        )
    lines.append("")
    return "\n".join(lines)


def render_source_repository_map(registry: dict[str, Any], lineage: dict[str, Any]) -> str:
    sources = registry.get("sources", [])
    lineage_sources = lineage["sources"]
    lines = [
        "# 数据源与 GitHub 仓库谱系",
        "",
        "> 由 `field_verification/source_lineage.json` 自动生成。只记录有项目内或上游证据的关系；",
        "> 项目证据状态与对话确认状态分列；确认某客户端仓库不等于确认它是底层数据提供方。",
        "",
        "| 字典来源 | 采集器状态 | 运行时命名空间 | 数据提供方 | 独立来源族 | 可作锚 | 项目证据 | 对话确认 |",
        "|:--|:--|:--|:--|:--|:--:|:--|:--|",
    ]
    for source in sources:
        name = source["name"]
        record = lineage_sources[name]
        aliases = ", ".join(record.get("runtime_aliases", [])) or "未确认"
        family = record.get("independence_family") or "未确认"
        anchor = "是" if record.get("anchor_eligible") else "否"
        collection_status = _cell(source.get("status", "active"))
        replacement = source.get("replacement_source")
        if replacement:
            collection_status += " → " + _cell(replacement)
        repo_status = record.get("repository_mapping_status", "unconfirmed")
        dialog = record.get("dialog_confirmation", {"status": "pending"})
        dialog_status = _cell(dialog.get("status", "pending"))
        if dialog.get("confirmed_on"):
            dialog_status += "（" + _cell(dialog["confirmed_on"]) + "）"
        lines.append(
            "| {name} | {collection_status} | {aliases} | {provider} | {family}（{family_status}） | {anchor} | {repo_status} | {dialog_status} |".format(
                name=_cell(name),
                collection_status=collection_status,
                aliases=_cell(aliases),
                provider=_cell(record.get("provider")),
                family=_cell(family),
                family_status=_cell(record.get("independence_status")),
                anchor=anchor,
                repo_status=_cell(repo_status),
                dialog_status=dialog_status,
            )
        )
    project_reference = lineage.get("project_reference")
    if project_reference:
        project_url = project_reference["url"]
        project_relation = _cell(project_reference["relation"])
        project_status = _cell(project_reference["status"])
        project_confirmed_on = _cell(project_reference["confirmed_on"])
        project_note = _cell(project_reference["note"])
        lines.extend(
            [
                "",
                "## 项目级历史参考基线",
                "",
                f"- [{project_url}]({project_url}) — {project_relation}；{project_status}（{project_confirmed_on}）。{project_note}",
            ]
        )
    lines.extend(["", "## 仓库证据", ""])
    for source in sources:
        name = source["name"]
        record = lineage_sources[name]
        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"- 来源说明：{_cell(record.get('anchor_note'))}。")
        dialog = record.get("dialog_confirmation", {"status": "pending"})
        lines.append(
            "- 对话确认：{status}{date}。{note}".format(
                status=_cell(dialog.get("status", "pending")),
                date=(
                    ("（" + _cell(dialog["confirmed_on"]) + "）")
                    if dialog.get("confirmed_on")
                    else ""
                ),
                note=(
                    _cell(dialog.get("note")) if dialog.get("note") else "关系待通过对话逐项确认。"
                ),
            )
        )
        repositories = record.get("repositories", [])
        if repositories:
            for repository in repositories:
                url = repository["url"]
                relation = _cell(repository.get("relation"))
                status = _cell(repository.get("status"))
                note = _cell(repository.get("note"))
                evidence = ", ".join(repository.get("evidence_files", [])) or "未列出"
                lines.append(f"- [{url}]({url}) — {relation}；{status}。{note}")
                lines.append(f"  - 项目内证据：{evidence}")
        else:
            lines.append(
                "- GitHub 对应仓库：**unconfirmed**。现有材料不足以证明某个仓库就是本项目使用的采集实现；等待后续证据或用户确认。"
            )
        lines.append("")
    lines.extend(
        [
            "## 解释口径",
            "",
            "- GitHub 仓库可能是客户端、SDK、镜像或上游 API 契约仓库，不自动等同于数据提供方。",
            "- `独立来源族` 用于碰撞证据去重；同一提供方的不同接口不能互相充当独立 L1 证据。",
            "- `可作锚` 还要求字段状态 verified、含义/单位没有质量问题，且完整 code path 与运行时字段精确匹配。",
            "- 未确认的来源族在默认碰撞中 fail closed；确认后更新 JSON 并重生成本页。",
            "",
        ]
    )
    return "\n".join(lines)


def _write_if_changed(path: str, content: str, check: bool) -> bool:
    current = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            current = handle.read()
    changed = current != content
    if changed and not check:
        temporary = path + ".tmp"
        with open(temporary, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temporary, path)
    return changed


def generate(check: bool = False) -> int:
    registry = fra.load_registry()
    lineage = sla.load_source_lineage(registry=registry)
    outputs = {
        DICT: render_field_dict(registry),
        UNKNOWN: render_unknown_fields(registry),
        SOURCE_MAP: render_source_repository_map(registry, lineage),
        METADATA_GAPS: render_field_metadata_gaps(registry),
        AGGREGATE_REVIEW: render_field_aggregate_review(registry),
    }
    changed = []
    for path, content in outputs.items():
        if _write_if_changed(path, content, check):
            changed.append(os.path.relpath(path, REPO_ROOT))
    if check:
        if changed:
            print("DIFF: 生成文档过期: " + ", ".join(changed))
            return 1
        print("OK: 字段导航、待破解队列、来源映射、元数据缺口和聚合复核文档均为最新生成结果")
        return 0
    print("OK: 已生成 " + ", ".join(os.path.relpath(path, REPO_ROOT) for path in outputs))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成主字段字典入口和未知字段队列")
    parser.add_argument("--check", action="store_true", help="仅检查生成物是否过期")
    sys.exit(generate(check=parser.parse_args().check))

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


_SOURCE_ROLE_LABELS = {
    "provider_component": "已映射提供方的接口组件",
    "service_endpoint": "服务接口（底层来源族未确认）",
    "framework_reference": "多源框架参考（非独立来源）",
    "historical_unattributed": "历史未归属（不作来源锚）",
}


def _source_role_label(source: dict[str, Any]) -> str:
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
    missing_meaning = sum(not record.get("meaning") for record in verified_records)
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
        "- `verified` 表示字段语义已经确认。只有来源谱系可确认、运行时来源匹配且完整路径精确相同时，才可作为碰撞锚点。",
        "- `unverified`、`candidate` 是默认破解目标；`conflict` 可作为待复核目标但不能作锚，碰撞候选不能替代证据冲突复核。",
        "- `disproved` 单独归档，不进入默认破解队列。",
        "- 未登记来源、路径不完整或来源独立性未确认时，不参与默认 L1 定案。",
        "- AxData 是多提供方接口框架；当前 `stock_shortline_indicators_tdx` 属于 TDX 来源族。AxData 接口盘点只作框架参考，不能作为独立来源或锚；详见 [`axdata_field_reconciliation_20261010.md`](axdata_field_reconciliation_20261010.md)。",
        "- Levistock 是多源客户端包装库。已归属的 KPH 记录映射到 KPH 来源族；FTShare MCP 记录归到项目独立接入的 FTShare 服务接口，但其底层来源族未确认，不能作独立锚。其余历史记录保留为未归属证据，不计为 Levistock 数据源；字段映射见 [`source_identity_reclassifications.json`](field_verification/source_identity_reclassifications.json) 与 [`levistock_source_reconciliation_20261010.md`](levistock_source_reconciliation_20261010.md)。",
        "",
        "## 当前覆盖",
        "",
        f"- 来源身份与参考登记：{len(sources)} 项；是否可作独立锚由来源谱系单独判定。",
        f"- 逐源字段路径：{len(records)} 条；verified {counts['verified']}、unverified {counts['unverified']}、candidate {counts['candidate']}、conflict {counts['conflict']}、disproved {counts['disproved']}。",
        "- 矩阵：[`field_matrix.md`](field_matrix.md)。",
        "- 待破解与状态冲突：[`unknown_fields.md`](unknown_fields.md)。",
        "- 来源与 GitHub 仓库映射：[`source_repository_map.md`](source_repository_map.md)。",
        f"- 已验证字段描述缺口：{missing_meaning} 条缺少含义、{missing_canonical} 条缺少规范名，见 [`field_metadata_gaps.md`](field_metadata_gaps.md)；缺口本身不自动改变状态。",
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
    counts = _source_field_counts(records)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        status = record.get("status", "unverified")
        if status in {"unverified", "candidate", "conflict", "disproved"}:
            groups[status].append(record)

    lines = [
        "# 未知字段与状态冲突队列",
        "",
        "> 由 `field_registry.json.source_fields` 自动生成；每行身份是来源加完整 code path。",
        "> 修改状态必须先核对 `reference_evidence` 与 `registry_aggregate`，并保留证据来源。",
        "> 碰撞候选须人工复核后使用 `apply_collision_adjudications.py` 同步状态；流程见 `field_verification/ADJUDICATION_WORKFLOW.md`。",
        "> 聚合层的同码异义与定义缺口见 [`field_aggregate_review.md`](field_aggregate_review.md)，不代表逐源记录状态冲突。",
        "",
        f"> 总字段路径 {len(records)}；unverified {counts['unverified']}、candidate {counts['candidate']}、conflict {counts['conflict']}、disproved {counts['disproved']}。",
    ]
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
                "| 来源 | 完整 code path | 规范名 | 含义 | 单位 | 状态判定 | 证据章节 |",
                "|:--|:--|:--|:--|:--|:--|:--|",
            ]
        )
        for record in group:
            sections = record.get("sections") or (
                [record.get("section")] if record.get("section") else []
            )
            lines.append(
                "| {source} | `{code}` | {canonical} | {meaning} | {unit} | {resolution} | {section} |".format(
                    source=_cell(record.get("source")),
                    code=str(record.get("code", "")).replace("`", "\\`"),
                    canonical=_cell(record.get("canonical")),
                    meaning=_cell(record.get("meaning")),
                    unit=_cell(record.get("unit")),
                    resolution=_cell(record.get("status_resolution")),
                    section=_cell("；".join(sections)),
                )
            )
    lines.append("")
    return "\n".join(lines)


def render_field_aggregate_review(registry: dict[str, Any]) -> str:
    """Render aggregate-only ambiguity and composite-text candidates."""
    records = fra.source_field_records(registry)
    if not records:
        raise ValueError("registry.source_fields is empty; refusing to generate aggregate review")
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
        and (not record.get("meaning") or not record.get("canonical"))
    ]
    missing_meaning = sum(not record.get("meaning") for record in gaps)
    missing_canonical = sum(not record.get("canonical") for record in gaps)
    lines = [
        "# 已验证字段的描述缺口",
        "",
        "> 由 `field_registry.json.source_fields` 自动生成；本表只发现缺失的展示元数据，不改变字段状态或锚点资格。",
        "> 请依据来源定义、原始样本和已存证据逐条补充，禁止按相邻字段或字段代码猜测含义。",
        "",
        f"> 缺口记录 {len(gaps)} 条；缺少含义 {missing_meaning} 条；缺少规范名 {missing_canonical} 条。",
        "",
    ]
    if not gaps:
        lines.append("_没有缺少规范名或含义的 verified 字段。_")
        return "\n".join(lines) + "\n"
    lines.extend(
        [
            "| 来源 | 完整 code path | 规范名 | 含义 | 单位 | 证据章节 |",
            "|:--|:--|:--|:--|:--|:--|",
        ]
    )
    for record in sorted(gaps, key=lambda item: (item["source"], item["code"])):
        sections = record.get("sections") or (
            [record.get("section")] if record.get("section") else []
        )
        lines.append(
            "| {source} | `{code}` | {canonical} | {meaning} | {unit} | {section} |".format(
                source=_cell(record.get("source")),
                code=str(record.get("code", "")).replace("`", "\\`"),
                canonical=_cell(record.get("canonical")),
                meaning=_cell(record.get("meaning")),
                unit=_cell(record.get("unit")),
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
        "| 字典来源 | 运行时命名空间 | 数据提供方 | 独立来源族 | 可作锚 | 项目证据 | 对话确认 |",
        "|:--|:--|:--|:--|:--:|:--|:--|",
    ]
    for source in sources:
        name = source["name"]
        record = lineage_sources[name]
        aliases = ", ".join(record.get("runtime_aliases", [])) or "未确认"
        family = record.get("independence_family") or "未确认"
        anchor = "是" if record.get("anchor_eligible") else "否"
        repo_status = record.get("repository_mapping_status", "unconfirmed")
        dialog = record.get("dialog_confirmation", {"status": "pending"})
        dialog_status = _cell(dialog.get("status", "pending"))
        if dialog.get("confirmed_on"):
            dialog_status += "（" + _cell(dialog["confirmed_on"]) + "）"
        lines.append(
            "| {name} | {aliases} | {provider} | {family}（{family_status}） | {anchor} | {repo_status} | {dialog_status} |".format(
                name=_cell(name),
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
            "- `可作锚` 还要求字段状态 verified 且完整 code path 与运行时字段精确匹配。",
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

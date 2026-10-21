"""Read-only registry and source-lineage context for collision analysis.

The caller supplies the registry path, lineage loader, and state-update callback so
the collision façade retains its path and monkeypatch compatibility contract.
"""

from __future__ import annotations

import json
import os
from collections import defaultdict

from scripts import field_registry_api as FRA
from scripts import source_lineage_api as SLA


def _lineage_aliases(source, lineage):
    """Resolve an exact registry source to its runtime source identity or identities."""

    if not isinstance(source, str) or not source:

        return []

    runtime_sources = lineage.get("runtime_sources", {})

    if source in runtime_sources:

        return [source]

    aliases = SLA.runtime_aliases_for_source(source, lineage)

    return [alias for alias in aliases if alias in runtime_sources]


def _verified_official_contract_kind(field, source_config, source_record, adjudications):
    """Return the reviewed contract-evidence kind for an active verified identity."""

    if source_config.get("status") != "active":

        return None

    direct = field.get("evidence")

    source_contract = source_record.get("contract")

    contract_ids = source_config.get("contract_ids")

    if (
        source_config.get("source_role") == "documented_contract_anchor"
        and source_record.get("semantic_anchor_basis") == "official_contract"
        and isinstance(direct, dict)
        and direct.get("basis") == "official_contract"
        and isinstance(source_contract, dict)
        and direct.get("contract_id") == source_contract.get("contract_id")
        and isinstance(contract_ids, list)
        and direct.get("contract_id") in contract_ids
        and direct.get("evidence_file") == source_contract.get("evidence_file")
        and direct.get("documentation_url") == source_contract.get("documentation_url")
    ):

        return "semantic_anchor_contract"

    status_evidence = field.get("status_evidence")

    adjudication_ids = (
        status_evidence.get("source_contract_adjudication_ids", [])
        if isinstance(status_evidence, dict)
        else []
    )

    if not isinstance(adjudication_ids, list):

        return None

    reference_evidence = field.get("reference_evidence", [])

    if not isinstance(reference_evidence, list):

        return None

    for evidence in reference_evidence:

        if not isinstance(evidence, dict):

            continue

        if evidence.get("status") != "verified":

            continue

        if evidence.get("evidence_basis") not in {
            "authoritative_source_contract",
            "official_contract",
        }:

            continue

        contract = evidence.get("source_contract")

        adjudication_id = evidence.get("adjudication_id")

        if (
            not isinstance(contract, dict)
            or not all(contract.get(key) for key in ("authority", "path", "locator", "url"))
            or not isinstance(adjudication_id, str)
            or adjudication_id not in adjudication_ids
        ):

            continue

        adjudication = adjudications.get(adjudication_id, {})

        adjudicated_contract = adjudication.get("source_contract")

        if (
            adjudication.get("action") != "verify_source_contract"
            or adjudication.get("status") != "verified"
            or adjudication.get("evidence_basis") != evidence.get("evidence_basis")
            or not isinstance(adjudicated_contract, dict)
            or any(adjudicated_contract.get(key) != contract.get(key) for key in contract)
        ):

            continue

        return "source_contract"

    return None


def load_registry_context(registry_path, source_lineage_loader, set_source_lineage):
    """Load verified identities, contract evidence, anchors, mappings and diagnostics."""
    context = {
        "verified": set(),
        "disproved": set(),
        "anchors": set(),
        "contract_anchors": set(),
        "official_contract_verified": set(),
        "official_contract_anchors": set(),
        "known_mappings": set(),
        "diagnostics": [],
        "unmapped_verified": 0,
        "unconfirmed_verified": 0,
        "ambiguous_verified": 0,
        "unresolved_verified_metadata": 0,
        "unresolved_verified_metadata_by_issue": {},
        "source_fields": 0,
        "safe_to_run": False,
    }
    if not os.path.exists(registry_path):
        context["diagnostics"].append(f"字段注册表不存在：{registry_path}；本轮无已知字段锚")
        return context
    try:
        with open(registry_path, encoding="utf-8") as handle:
            registry = json.load(handle)
    except (OSError, ValueError, TypeError) as exc:
        context["diagnostics"].append(f"字段注册表读取失败；本轮无已知字段锚：{exc}")
        return context

    try:
        lineage = source_lineage_loader(registry=registry)
        lineage_valid = True
    except (OSError, ValueError, TypeError) as exc:
        lineage = {"sources": {}, "source_aliases": {}, "runtime_sources": {}}
        context["diagnostics"].append(f"来源血缘校验失败；禁止生成已确认锚：{exc}")
        lineage_valid = False
    set_source_lineage(lineage)
    if not lineage_valid:
        return context

    source_fields = registry.get("source_fields")
    if source_fields is None:
        # Compatibility for old one-source aggregate rows only. A multi-source
        # aggregate status cannot safely be attributed to any individual source.
        source_fields = []
        for field in registry.get("fields", []):
            sources = field.get("sources", [])
            source = field.get("source")
            if not source and len(sources) == 1:
                source = sources[0]
            if isinstance(source, str) and source and len(sources or [source]) == 1:
                source_fields.append({**field, "source": source})
        context["diagnostics"].append(
            "注册表没有 source_fields；仅使用可精确归属的单源旧记录，多源汇总状态不分摊"
        )
    if not isinstance(source_fields, list):
        context["diagnostics"].append("注册表 source_fields 格式无效；本轮无已知字段锚")
        return context

    context["source_fields"] = len(source_fields)
    registry_sources = {
        item.get("name"): item
        for item in registry.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    adjudications = {}
    adjudication_sources = [registry.get("adjudications", [])]
    adjudication_sources.extend(
        field.get("adjudications", []) for field in source_fields if isinstance(field, dict)
    )
    for records in adjudication_sources:
        if not isinstance(records, list):
            continue
        for record in records:
            if isinstance(record, dict) and isinstance(record.get("id"), str):
                adjudications[record["id"]] = record
    alias_identity_owners = defaultdict(set)
    for candidate in source_fields:
        if not isinstance(candidate, dict):
            continue
        candidate_source = candidate.get("source")
        candidate_code = candidate.get("code")
        if not isinstance(candidate_source, str) or not isinstance(candidate_code, str):
            continue
        for alias in _lineage_aliases(candidate_source, lineage):
            alias_identity_owners[(alias, candidate_code)].add((candidate_source, candidate_code))

    seen_source_identities = set()
    for field in source_fields:
        if not isinstance(field, dict):
            context["diagnostics"].append("source_fields 含非对象记录；已禁用本轮字段对撞")
            return context
        source = field.get("source")
        code = field.get("code")
        if not isinstance(source, str) or not isinstance(code, str) or not code:
            context["diagnostics"].append("source_fields 含无效来源/完整路径；已禁用本轮字段对撞")
            return context
        if field.get("status") not in {
            "verified",
            "unverified",
            "candidate",
            "conflict",
            "disproved",
        }:
            context["diagnostics"].append(
                f"source_fields 含未知状态 {source}::{code}；已禁用本轮字段对撞"
            )
            return context
        identity = (source, code)
        if identity in seen_source_identities:
            context["diagnostics"].append(
                f"source_fields 存在重复身份 {source}::{code}；已禁用全部 registry 锚"
            )
            context["verified"].clear()
            context["disproved"].clear()
            context["anchors"].clear()
            context["contract_anchors"].clear()
            context["official_contract_verified"].clear()
            context["official_contract_anchors"].clear()
            context["known_mappings"].clear()
            return context
        seen_source_identities.add(identity)
        aliases = _lineage_aliases(source, lineage)
        if field.get("status") == "disproved":
            for alias in aliases:
                if alias != "zhb" or len(alias_identity_owners[(alias, code)]) == 1:
                    context["disproved"].add((alias, code))
            continue
        if field.get("status") != "verified":
            continue
        metadata_issues = FRA.source_field_semantic_issues(field)
        if metadata_issues:
            context["unresolved_verified_metadata"] += 1
            for issue in metadata_issues:
                issue_counts = context["unresolved_verified_metadata_by_issue"]
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
            continue
        if not aliases:
            context["unmapped_verified"] += 1
            continue
        for alias in aliases:
            if alias == "zhb" and len(alias_identity_owners[(alias, code)]) != 1:
                context["ambiguous_verified"] += 1
                continue
            identity = (alias, code)
            context["verified"].add(identity)
            family = SLA.runtime_family(alias, lineage)
            source_record = lineage.get("sources", {}).get(source, {})
            source_config = registry_sources.get(source, {})
            contract_evidence_kind = _verified_official_contract_kind(
                field, source_config, source_record, adjudications
            )
            if contract_evidence_kind:
                context["official_contract_verified"].add(identity)
            if (
                source_record.get("anchor_eligible")
                and source_record.get("independence_status") == "confirmed"
                and family == source_record.get("independence_family")
            ):
                context["anchors"].add(identity)
                if contract_evidence_kind:
                    context["official_contract_anchors"].add(identity)
            elif (
                contract_evidence_kind == "semantic_anchor_contract"
                and source_record.get("semantic_anchor_basis") == "official_contract"
            ):
                context["contract_anchors"].add(identity)
                context["official_contract_anchors"].add(identity)
            else:
                context["unconfirmed_verified"] += 1

    for mapping in registry.get("mappings", []):
        if not isinstance(mapping, dict):
            continue
        left = mapping.get("from", {})
        right = mapping.get("to", {})
        if not isinstance(left, dict) or not isinstance(right, dict):
            continue
        left_aliases = _lineage_aliases(left.get("source"), lineage)
        right_aliases = _lineage_aliases(right.get("source"), lineage)
        left_code = left.get("code")
        right_code = right.get("code")
        if not isinstance(left_code, str) or not isinstance(right_code, str):
            continue
        for left_alias in left_aliases:
            for right_alias in right_aliases:
                normalized_left_code = SLA.normalize_runtime_field_code(left_alias, left_code)
                normalized_right_code = SLA.normalize_runtime_field_code(right_alias, right_code)
                if (
                    left_alias == "zhb"
                    and len(alias_identity_owners[(left_alias, normalized_left_code)]) != 1
                ):
                    continue
                if (
                    right_alias == "zhb"
                    and len(alias_identity_owners[(right_alias, normalized_right_code)]) != 1
                ):
                    continue
                context["known_mappings"].add(
                    (left_alias, normalized_left_code, right_alias, normalized_right_code)
                )
                context["known_mappings"].add(
                    (right_alias, normalized_right_code, left_alias, normalized_left_code)
                )

    context["safe_to_run"] = True

    if context["unmapped_verified"]:
        context["diagnostics"].append(
            f"{context['unmapped_verified']} 条 verified 源字段无法映射到运行时来源，未作锚"
        )
    if context["unconfirmed_verified"]:
        context["diagnostics"].append(
            f"{context['unconfirmed_verified']} 条 verified 源字段来源未确认独立性，作为已知字段跳过重解但不作锚"
        )
    if context["contract_anchors"]:
        context["diagnostics"].append(
            f"{len(context['contract_anchors'])} 条官方契约语义锚可参与对撞；底层来源独立性未确认，强候选标为 L1-C"
        )
    if context["ambiguous_verified"]:
        context["diagnostics"].append(
            f"{context['ambiguous_verified']} 条 verified 源字段映射到重复运行时身份，未作为已知字段或锚"
        )
    if context["unresolved_verified_metadata"]:
        issue_labels = {
            "meaning_missing": "缺义/占位",
            "meaning_conflict": "含义冲突",
            "unit_conflict": "单位冲突",
            "meaning_alignment_ambiguous": "含义分组待对齐",
            "unit_alignment_ambiguous": "单位分组待对齐",
        }
        issue_summary = "、".join(
            f"{issue_labels.get(issue, issue)} {count} 条"
            for issue, count in sorted(context["unresolved_verified_metadata_by_issue"].items())
        )
        context["diagnostics"].append(
            f"{context['unresolved_verified_metadata']} 条 verified 源字段元数据未达锚点条件"
            f"（{issue_summary}），已重新纳入待破解目标且不作碰撞锚"
        )
    if not context["anchors"] and not context["contract_anchors"]:
        context["diagnostics"].append("没有可用的已确认独立锚；默认模式不会把未知字段互相定案")
    return context


def norm_src_of(fid):
    if "." in fid:
        return fid.split(".")[0]
    if "[" in fid:
        return fid.split("[")[0]
    return fid


def alias_source(fid, lineage):
    source = norm_src_of(fid)
    if source in lineage.get("runtime_sources", {}):
        return source
    aliases = _lineage_aliases(source, lineage)
    return aliases[0] if aliases else source


def evidence_source_family(fid, lineage):
    """Return a confirmed producer family, or None when lineage is unknown."""
    return SLA.runtime_family(alias_source(fid, lineage), lineage)


def are_independent_sources(left_fid, right_fid, lineage):
    left_family = evidence_source_family(left_fid, lineage)
    right_family = evidence_source_family(right_fid, lineage)
    return left_family is not None and right_family is not None and left_family != right_family


def code_of(fid, normalize_runtime_field_code):
    if "[" in fid:
        code = fid[fid.index("[") :]
    elif "." in fid:
        code = fid.split(".", 1)[1]
    else:
        return fid
    return normalize_runtime_field_code(norm_src_of(fid), code)


def is_verified(fid, verified, lineage):
    return (alias_source(fid, lineage), code_of(fid, SLA.normalize_runtime_field_code)) in verified


def is_disproved(fid, disproved, lineage):
    return (alias_source(fid, lineage), code_of(fid, SLA.normalize_runtime_field_code)) in disproved


def select_collision_fields(
    store, verified, disproved, anchors, exploratory=False, contract_anchors=None, lineage=None
):
    """Return unknown cracking targets and the allowed comparison field set.

    Verified status removes an identity only from the left-hand cracking targets.
    Independently confirmed verified fields remain on the right as anchors; capture
    routing is source-level and never consults this field status.
    """
    eligible = [
        fid
        for fid, info in store.items()
        if not info["is_identifier"]
        and not info["is_constant"]
        and info["type"] in ("num", "enum")
        and not is_disproved(fid, disproved, lineage)
    ]
    left = [fid for fid in eligible if not is_verified(fid, verified, lineage)]
    if exploratory:
        return left, eligible
    contract_anchors = contract_anchors or set()
    right = [
        fid
        for fid in eligible
        if (alias_source(fid, lineage), code_of(fid, SLA.normalize_runtime_field_code)) in anchors
        or (alias_source(fid, lineage), code_of(fid, SLA.normalize_runtime_field_code))
        in contract_anchors
    ]
    return left, right

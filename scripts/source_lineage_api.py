"""Validated access to source-family and repository-lineage metadata."""

from __future__ import annotations

import datetime
import json
import os
from typing import Any

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
LINEAGE_PATH = os.path.join(REPO_ROOT, "docs", "field_verification", "source_lineage.json")


def load_source_lineage(
    path: str = LINEAGE_PATH, registry: dict[str, Any] | None = None
) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        raw_lineage = json.load(handle)
    if not isinstance(raw_lineage, dict) or not all(isinstance(key, str) for key in raw_lineage):
        raise TypeError("source_lineage root must be an object with string keys")
    lineage: dict[str, Any] = raw_lineage
    if lineage.get("schema_version") != 1:
        raise ValueError("unsupported source_lineage schema_version")
    sources = lineage.get("sources")
    runtime_sources = lineage.get("runtime_sources")
    aliases = lineage.get("source_aliases")
    if (
        not isinstance(sources, dict)
        or not isinstance(runtime_sources, dict)
        or not isinstance(aliases, dict)
    ):
        raise ValueError(
            "source_lineage requires sources, source_aliases, and runtime_sources objects"
        )
    project_reference = lineage.get("project_reference")
    if project_reference is not None:
        if not isinstance(project_reference, dict):
            raise TypeError("source_lineage project_reference must be an object")
        reference_url = project_reference.get("url")
        relation = project_reference.get("relation")
        status = project_reference.get("status")
        confirmed_on = project_reference.get("confirmed_on")
        note = project_reference.get("note")
        if not isinstance(reference_url, str) or not reference_url.startswith("https://"):
            raise ValueError("project_reference requires an HTTPS URL")
        if not isinstance(relation, str) or not relation.strip():
            raise ValueError("project_reference requires a relation")
        if status != "confirmed":
            raise ValueError("project_reference status must be confirmed")
        if not isinstance(confirmed_on, str):
            raise ValueError("project_reference requires confirmed_on")
        try:
            if datetime.date.fromisoformat(confirmed_on).isoformat() != confirmed_on:
                raise ValueError
        except ValueError as exc:
            raise ValueError("project_reference.confirmed_on must be YYYY-MM-DD") from exc
        if not isinstance(note, str) or not note.strip():
            raise ValueError("project_reference requires a note")
    if registry is not None:
        expected = {record.get("name") for record in registry.get("sources", [])}
        actual = set(sources)
        if expected != actual:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            raise ValueError(f"source lineage mismatch; missing={missing}; extra={extra}")

    alias_families: dict[str, tuple[str, str]] = {}
    repository_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(path))))
    repository_root = os.path.normcase(os.path.realpath(repository_root))
    for source_name, alias in aliases.items():
        if alias is not None and not isinstance(alias, str):
            raise TypeError(f"source alias {source_name!r} must be a string or null")
        if alias is not None and alias not in runtime_sources:
            raise ValueError(
                f"source alias {source_name!r} points to unknown runtime alias {alias!r}"
            )
    for source_name, record in sources.items():
        if not isinstance(record, dict):
            raise TypeError(f"source lineage entry {source_name!r} must be an object")
        aliases = record.get("runtime_aliases", [])
        if not isinstance(aliases, list) or any(not isinstance(alias, str) for alias in aliases):
            raise TypeError(f"{source_name}.runtime_aliases must be a string list")
        family = record.get("independence_family")
        status = record.get("independence_status")
        if status not in {"confirmed", "unconfirmed"}:
            raise ValueError(f"{source_name}.independence_status is invalid")
        anchor_eligible = record.get("anchor_eligible")
        if not isinstance(anchor_eligible, bool):
            raise TypeError(f"{source_name}.anchor_eligible must be boolean")
        if anchor_eligible and (status != "confirmed" or not family or not aliases):
            raise ValueError(f"{source_name} cannot be anchor eligible without confirmed lineage")
        for alias in aliases:
            runtime = runtime_sources.get(alias)
            if not isinstance(runtime, dict):
                raise ValueError(f"{source_name} references unknown runtime alias {alias!r}")
            runtime_family = runtime.get("independence_family")
            runtime_status = runtime.get("independence_status")
            if status == "confirmed" and (
                runtime_status != "confirmed" or runtime_family != family
            ):
                raise ValueError(f"{source_name} disagrees with runtime family for {alias!r}")
            if status == "confirmed":
                prior = alias_families.get(alias)
                current = (str(family), str(status))
                if prior is not None and prior != current:
                    raise ValueError(f"runtime alias {alias!r} maps to conflicting families")
                alias_families[alias] = current
        repository_status = record.get("repository_mapping_status", "unconfirmed")
        repositories = record.get("repositories", [])
        if repository_status not in {"confirmed", "unconfirmed"}:
            raise ValueError(f"{source_name}.repository_mapping_status is invalid")
        if not isinstance(repositories, list):
            raise TypeError(f"{source_name}.repositories must be a list")
        dialog_confirmation = record.get("dialog_confirmation", {"status": "pending"})
        if not isinstance(dialog_confirmation, dict):
            raise TypeError(f"{source_name}.dialog_confirmation must be an object")
        dialog_status = dialog_confirmation.get("status", "pending")
        if dialog_status not in {"confirmed", "pending"}:
            raise ValueError(f"{source_name}.dialog_confirmation.status is invalid")
        if dialog_status == "confirmed":
            confirmed_on = dialog_confirmation.get("confirmed_on")
            note = dialog_confirmation.get("note")
            if not isinstance(confirmed_on, str):
                raise ValueError(f"{source_name} dialog confirmation requires confirmed_on")
            try:
                if datetime.date.fromisoformat(confirmed_on).isoformat() != confirmed_on:
                    raise ValueError
            except ValueError as exc:
                raise ValueError(
                    f"{source_name}.dialog_confirmation.confirmed_on must be YYYY-MM-DD"
                ) from exc
            if not isinstance(note, str) or not note.strip():
                raise ValueError(f"{source_name} dialog confirmation requires a note")
            if not repositories or not any(
                isinstance(repository, dict)
                and isinstance(repository.get("url"), str)
                and repository["url"].startswith("https://")
                for repository in repositories
            ):
                raise ValueError(
                    f"{source_name} dialog confirmation requires an HTTPS repository relation"
                )
        confirmed_repositories = 0
        for repository in repositories:
            if not isinstance(repository, dict):
                raise TypeError(f"{source_name}.repositories entries must be objects")
            repository_state = repository.get("status")
            if repository_state not in {"confirmed", "unconfirmed"}:
                raise ValueError(f"{source_name} repository status is invalid")
            if repository_state != "confirmed":
                continue
            confirmed_repositories += 1
            url = repository.get("url")
            evidence_files = repository.get("evidence_files")
            if not isinstance(url, str) or not url.startswith("https://"):
                raise ValueError(f"{source_name} confirmed repository requires an HTTPS URL")
            if not isinstance(evidence_files, list) or not evidence_files:
                raise ValueError(f"{source_name} confirmed repository requires project evidence")
            for evidence_file in evidence_files:
                if not isinstance(evidence_file, str) or not evidence_file:
                    raise ValueError(f"{source_name} repository evidence paths must be strings")
                evidence_path = os.path.normcase(
                    os.path.realpath(os.path.join(repository_root, evidence_file))
                )
                if os.path.commonpath(
                    [repository_root, evidence_path]
                ) != repository_root or not os.path.isfile(evidence_path):
                    raise ValueError(
                        f"{source_name} repository evidence is missing or outside repo: {evidence_file}"
                    )
        if repository_status == "confirmed" and not confirmed_repositories:
            raise ValueError(f"{source_name} confirmed mapping has no confirmed repository")
    return lineage


def runtime_family(alias: str, lineage: dict[str, Any]) -> str | None:
    record = lineage.get("runtime_sources", {}).get(alias)
    if not isinstance(record, dict):
        return None
    if record.get("independence_status") != "confirmed":
        return None
    family = record.get("independence_family")
    return family if isinstance(family, str) and family else None


def source_aliases(source: str, lineage: dict[str, Any]) -> list[str]:
    record = lineage.get("sources", {}).get(source, {})
    if not record.get("anchor_eligible"):
        return []
    return list(record.get("runtime_aliases", []))


def runtime_aliases_for_source(source: str, lineage: dict[str, Any]) -> list[str]:
    """Return every runtime identity linked to a registry source, including unconfirmed ones."""
    record = lineage.get("sources", {}).get(source, {})
    aliases = record.get("runtime_aliases", [])
    if aliases:
        return list(aliases)
    alias = lineage.get("source_aliases", {}).get(source)
    return [alias] if isinstance(alias, str) and alias in lineage.get("runtime_sources", {}) else []

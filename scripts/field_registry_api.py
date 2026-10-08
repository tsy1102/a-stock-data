#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""field_registry_api.py — 字段登记表单一真相源(registry) 的结构化访问层。

为 Phase 2「治理脚本改读 registry」提供统一读取入口，替代各脚本自带的
markdown 解析逻辑。所有函数只读 docs/field_verification/field_registry.json，
不解析 field_dict.md。

设计原则（安全优先）：
  * 纯 stdlib json，零依赖（本环境无 pyyaml/ruamel）。
  * 核心视图 `field_source_map()` 与 gen_field_matrix.build_matrix() 同构
    （{code: set(sources)}），便于逐字节 parity 比对。
  * 任何读取失败（文件缺失 / 格式错 / 缺 key）直接抛异常，由调用方决定是否
    fallback 到 markdown 路径——本模块不静默吞错。
"""

from __future__ import annotations

import json
import os
from collections import defaultdict
from typing import Dict, List, Optional, Set, cast

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
REGISTRY = os.path.join(REPO_ROOT, "docs", "field_verification", "field_registry.json")


def load_registry(path: str = REGISTRY) -> dict:
    """读取 registry。失败抛异常（不静默兜底）。"""
    with open(path, encoding="utf-8") as f:
        return cast(dict, json.load(f))


def field_source_map(reg: Optional[dict] = None) -> Dict[str, Set[str]]:
    """核心视图：{code: set(sources)}，与 audit_field_completeness.registered_field_sets() 同构
    （原生 token × 源）。供 audit_field_completeness 的 REG 半边与 RAW 对撞，及 lint 等消费。

    ⚠️ 注意：此视图的 code 为**原生 token**（f144 / [1] / amount / SH600519 ...），并非
    §零·B 展示用的清洗字段名。§零·B 生成请改用 `field_matrix_map()`。
    """
    if reg is None:
        reg = load_registry()
    out: Dict[str, Set[str]] = defaultdict(set)
    source_fields = source_field_records(reg)
    if "source_fields" in reg:
        for record in source_fields:
            out[record["code"]].add(record["source"])
        return dict(out)
    for r in reg["fields"]:
        out[r["code"]].update(r["sources"])
    return out


def field_matrix_map(reg: Optional[dict] = None) -> Dict[str, List[str]]:
    """返回字段矩阵投影：{clean_field_name: [sources]}。

    专供 gen_field_matrix 生成独立的 field_matrix.md。registry 缺失 field_matrix 时抛异常，
    由调用方回退只读历史参考文档。
    """
    if reg is None:
        reg = load_registry()
    fm = reg.get("field_matrix")
    if not fm:
        raise KeyError("registry 缺少 field_matrix 投影（请重跑 extract_registry.py）")
    return {k: list(v) for k, v in fm.items()}


def record_count(reg: Optional[dict] = None) -> int:
    """去重 (字段,源) 配对总数 = sum(len(sources)) for each field。"""
    if reg is None:
        reg = load_registry()
    source_fields = source_field_records(reg)
    if "source_fields" in reg:
        return len(source_fields)
    return sum(len(r["sources"]) for r in reg["fields"])


def multi_source_count(reg: Optional[dict] = None) -> int:
    if reg is None:
        reg = load_registry()
    return sum(1 for source_set in field_source_map(reg).values() if len(source_set) >= 2)


def fields_by_source(reg: Optional[dict] = None) -> Dict[str, Set[str]]:
    """{source: set(codes)}，供 audit / landing / 按源聚合消费。"""
    if reg is None:
        reg = load_registry()
    out: Dict[str, Set[str]] = defaultdict(set)
    source_fields = source_field_records(reg)
    if "source_fields" in reg:
        for record in source_fields:
            out[record["source"]].add(record["code"])
        return dict(out)
    for r in reg["fields"]:
        for s in r["sources"]:
            out[s].add(r["code"])
    return dict(out)


def source_field_records(reg: Optional[dict] = None) -> List[dict]:
    """Return validated source-specific records keyed by ``(source, full code path)``.

    Older registries do not contain ``source_fields``; in that case an empty list
    signals callers to use the compatibility aggregate view.
    """
    if reg is None:
        reg = load_registry()
    if "source_fields" not in reg:
        return []
    records = reg.get("source_fields")
    if not isinstance(records, list):
        raise TypeError("registry.source_fields must be a list")
    seen = set()
    for record in records:
        if not isinstance(record, dict):
            raise TypeError("registry.source_fields entries must be objects")
        source = record.get("source")
        code = record.get("code")
        if not isinstance(source, str) or not source or not isinstance(code, str) or not code:
            raise ValueError("registry.source_fields entries require non-empty source and code")
        key = (source, code)
        if key in seen:
            raise ValueError(f"duplicate registry.source_fields identity: {source}::{code}")
        seen.add(key)
    return cast(List[dict], records)


def field_records(reg: Optional[dict] = None) -> List[dict]:
    """返回完整字段记录列表（含 canonical/meaning/unit/status/status_raw 等）。"""
    if reg is None:
        reg = load_registry()
    return cast(List[dict], reg["fields"])


def sources(reg: Optional[dict] = None) -> List[dict]:
    if reg is None:
        reg = load_registry()
    return cast(List[dict], reg.get("sources", []))


def mappings(reg: Optional[dict] = None) -> List[dict]:
    if reg is None:
        reg = load_registry()
    return cast(List[dict], reg.get("mappings", []))


def source_by_verify_file(verify_file: str, reg: Optional[dict] = None) -> Optional[dict]:
    for s in sources(reg):
        if s.get("verify_file") == verify_file:
            return s
    return None


def source_name_by_verify_file(verify_file: str, reg: Optional[dict] = None) -> Optional[str]:
    s = source_by_verify_file(verify_file, reg)
    return s["name"] if s else None

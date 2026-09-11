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
from typing import Dict, List, Optional, Set

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
REGISTRY = os.path.join(REPO_ROOT, "docs", "field_verification", "field_registry.json")


def load_registry(path: str = REGISTRY) -> dict:
    """读取 registry。失败抛异常（不静默兜底）。"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def field_source_map(reg: Optional[dict] = None) -> Dict[str, Set[str]]:
    """核心视图：{code: set(sources)}，与 gen_field_matrix.build_matrix() 同构。

    这是单一真相源的字段归属关系，parity 比对即对比此视图与 markdown 路径输出。
    """
    if reg is None:
        reg = load_registry()
    out: Dict[str, Set[str]] = {}
    for r in reg["fields"]:
        out[r["code"]] = set(r["sources"])
    return out


def record_count(reg: Optional[dict] = None) -> int:
    """去重 (字段,源) 配对总数 = sum(len(sources)) for each field。"""
    if reg is None:
        reg = load_registry()
    return sum(len(r["sources"]) for r in reg["fields"])


def multi_source_count(reg: Optional[dict] = None) -> int:
    if reg is None:
        reg = load_registry()
    return sum(1 for r in reg["fields"] if len(r["sources"]) >= 2)


def fields_by_source(reg: Optional[dict] = None) -> Dict[str, Set[str]]:
    """{source: set(codes)}，供 audit / landing / 按源聚合消费。"""
    if reg is None:
        reg = load_registry()
    out: Dict[str, Set[str]] = defaultdict(set)
    for r in reg["fields"]:
        for s in r["sources"]:
            out[s].add(r["code"])
    return dict(out)


def field_records(reg: Optional[dict] = None) -> List[dict]:
    """返回完整字段记录列表（含 canonical/meaning/unit/status/status_raw 等）。"""
    if reg is None:
        reg = load_registry()
    return reg["fields"]


def sources(reg: Optional[dict] = None) -> List[dict]:
    if reg is None:
        reg = load_registry()
    return reg.get("sources", [])


def mappings(reg: Optional[dict] = None) -> List[dict]:
    if reg is None:
        reg = load_registry()
    return reg.get("mappings", [])


def source_by_verify_file(verify_file: str, reg: Optional[dict] = None) -> Optional[dict]:
    for s in sources(reg):
        if s.get("verify_file") == verify_file:
            return s
    return None


def source_name_by_verify_file(verify_file: str, reg: Optional[dict] = None) -> Optional[str]:
    s = source_by_verify_file(verify_file, reg)
    return s["name"] if s else None

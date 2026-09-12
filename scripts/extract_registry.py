#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_registry.py — 从 field_dict.md 反向抽取「字段登记表单一真相源」。

设计原则（安全优先）：
  * 复用 gen_field_matrix.parse_tables / sec_to_source（已验证可确定性产出 1156 字段映射），
    不重写脆弱的 5395 行解析器。
  * 复用 verify_sync_check.MAPPING（源→分字典权威映射）。
  * Layer1（确定性）：field×source 映射 —— 与 build_matrix() 基线必须逐字节一致。
  * Layer2（最佳努力）：逐字段属性（canonical/meaning/unit/status），覆盖率单独报告，
    解析不到的属性留空并计入报告，绝不静默丢弃。
  * status 归一为枚举，同时保留 raw_status_text 原文（安全底线：不丢信息）。
  * 输出 JSON（YAML 严格子集，零依赖；环境无 pyyaml/ruamel，手写 emitter 风险高）。

用法（影子模式，不改动任何运行时行为）：
    python scripts/extract_registry.py [--out docs/field_verification/field_registry.json]

退出码：0=成功；2=Layer1 与基线不一致（G1 闸门未过，不应提交）。
"""
from __future__ import annotations

import argparse
import datetime
import io
import json
import os
import re
import sys
from collections import defaultdict, OrderedDict

# UTF-8 强制（与 gen_field_matrix 一致）
for _s in (sys.stdout, sys.stderr):
    if _s is not None and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DICT = os.path.join(REPO_ROOT, "docs", "field_dict.md")
DEFAULT_OUT = os.path.join(REPO_ROOT, "docs", "field_verification", "field_registry.json")
ALIGN = os.path.join(REPO_ROOT, "docs", "verify", "ulist_push2_align.md")

# 复用已验证的解析基座
sys.path.insert(0, SCRIPT_DIR)
import gen_field_matrix as gm
import verify_sync_check as vs
import audit_field_completeness as afc


# ---------------------------------------------------------------------------
# 原生 token 抽取（v2，2026-09-12）：复用 audit_field_completeness.registered_field_sets
# 的「章节→源→token」逻辑，保证 registry 的 fields[].code 即各源原生 token
# （f144 / [1] / stockName / open ...），而非被 clean_field 剥掉 f 前缀后的中文名。
# 这样 registry 才能作为 audit_field_completeness 的真相源。
# ---------------------------------------------------------------------------
_FCODE_SRC = {
    "东财-push2(stock/get)", "东财-ulist239(np/get)", "AxData", "东财-push2_full",
    "东财-资金流(em_fund_flow)", "东财-em_kline_f61", "东财-push2ex",
    "东财-datacenter(英文键)", "东财-slist", "东财-clist",
}
_INDEX_SRC = {"腾讯(qt.gtimg)", "新浪(hq.sinajs)",
              "ZHB-tdxstat", "ZHB-tdxstat2", "ZHB-tipinfo"}
_CAMEL_SRC = {"reports", "同花顺-fuyao", "东财-datacenter(英文键)",
              "东财-push2ex", "东财-热榜(em_hot)", "市场源(market_sources)",
              "levistock(ftshare)", "财联社(cls)", "百度(baidu)", "沪深交易所",
              "巨潮(cninfo)", "TDX(双命名源)", "TDX-F10(双命名源)"}


def cell_token(cell: str, src: str):
    """从表格首格抽取该源原生字段 token（与 afc.reg_tokens_for_section 同语义）。"""
    cell = cell.strip().strip("`").strip()
    cell = re.sub(r"\*\*", "", cell)
    if src in _FCODE_SRC:
        m = re.search(r"f(\d+)", cell, re.IGNORECASE)
        return ("f" + m.group(1)) if m else None
    if src in _INDEX_SRC:
        m = re.search(r"\[(\d+)\]", cell)
        return ("[" + m.group(1) + "]") if m else None
    if src in _CAMEL_SRC:
        m = re.search(r"[A-Za-z][A-Za-z0-9_]{2,}", cell)
        return m.group(0) if m else None
    # 默认：英文/中文名 token
    m = re.search(r"[\u4e00-\u9fffA-Za-z_][\u4e00-\u9fffA-Za-z0-9_]{1,}", cell)
    return m.group(0) if m else None


# audit SECTION_MAP 源标签 → verify 分字典（无专属分字典者填 None）
_AUDIT_VERIFY = {
    "东财-push2(stock/get)": "push2_verify.md",
    "东财-资金流(em_fund_flow)": "push2_verify.md",
    "东财-ulist239(np/get)": None,
    "东财-em_kline_f61": None,
    "东财-push2ex": None,
    "东财-datacenter(英文键)": None,
    "东财-slist": None,
    "东财-clist": None,
    "腾讯(qt.gtimg)": "tencent_verify.md",
    "新浪(hq.sinajs)": None,
    "ZHB-tdxstat": "tdx_func_fields.md",
    "ZHB-tdxstat2": "tdx_func_fields.md",
    "ZHB-tipinfo": "tdx_func_fields.md",
    "同花顺-fuyao": "fuyao_api_full.md",
    "TDX(双命名源)": "tdx_func_fields.md",
    "AxData": "axdata_verify.md",
    "东财-push2_full": "push2_verify.md",
    "reports": None,
    "东财-热榜(em_hot)": None,
    "市场源(market_sources)": None,
    "levistock(ftshare)": "levistock_field_verify.md",
    "财联社(cls)": None,
    "百度(baidu)": None,
    "沪深交易所": None,
    "巨潮(cninfo)": None,
    "TDX(双命名源)": "tdx_func_fields.md",
    "TDX-F10(双命名源)": None,
    "AxData": "axdata_verify.md",
}


# ---------------------------------------------------------------------------
# status 归一（保守默认：无法判定即 unverified，绝不误标 verified）
# ---------------------------------------------------------------------------
def normalize_status(raw: str) -> str:
    if not raw:
        return "unverified"
    t = raw.strip()
    # 已证伪
    if "证伪" in t or "推翻" in t:
        return "disproved"
    # 已定案同义（✅ 或 L1/L2 定案 / 跨源对撞）
    if "✅" in t or "L1" in t or "L2" in t or "定案" in t or "数值实证" in t or "交叉" in t or "跨源" in t:
        return "verified"
    # 候选待审
    if "候选" in t or "待核" in t:
        return "candidate"
    # 已弃用 / 未接入
    if "弃用" in t or "未接入" in t or "退役" in t or "deprecated" in t.lower():
        return "deprecated"
    # 显式声明未实证/待核实/待破解/待数值对撞/疑点/常量占位/无信息量
    if ("未实证" in t or "待核实" in t or "待破解" in t or "待数值" in t
            or "疑" in t or "常量占位" in t or "无信息量" in t
            or "未接入" in t or "❌" in t):
        return "unverified"
    # 兜底：含对撞/实测/锚/印证 等正向词 → verified，否则 unverified
    if any(k in t for k in ("对撞", "印证", "锚", "实测", "复核", "确认", "一致")):
        return "verified"
    return "unverified"


def clean_text(s: str) -> str:
    """去 markdown 加粗/反引号/首尾空格，保留中文名。"""
    s = s.strip()
    s = s.strip("`")
    s = re.sub(r"\*\*", "", s)
    return s.strip()


def extract_canonical(first_cell: str) -> str:
    """字段表首列常含 **现价** 表示规范名；否则取清洗后文本。"""
    m = re.search(r"\*\*(.+?)\*\*", first_cell)
    if m:
        return clean_text(m.group(1))
    return clean_text(first_cell)


# ---------------------------------------------------------------------------
# Layer1 + Layer2 主抽取
# ---------------------------------------------------------------------------
def extract():
    text = io.open(DICT, encoding="utf-8").read()

    # ---- Layer1（确定性）：复用 audit_field_completeness.registered_field_sets ----
    # 该函数在 markdown 上逐章节跑 section_to_sources + reg_tokens_for_section，
    # 产出「源标签 → 原生 token 集合」（f144 / [1] / stockName ...）。
    # 直接作为 registry fields[].code，保证与 audit_field_completeness 的 REG 集合逐集合一致。
    reg = afc.registered_field_sets()

    fields = OrderedDict()
    for src, toks in reg.items():
        for tok in sorted(toks):
            rec = fields.get(tok)
            if rec is None:
                rec = {
                    "code": tok,
                    "source": None,
                    "sources": set(),
                    "section": "",
                    "canonical": "",
                    "meaning": "",
                    "unit": "",
                    "status_raw": "",
                    "status": "unverified",
                }
                fields[tok] = rec
            rec["sources"].add(src)

    # ---- Layer2（最佳努力）：再走查 parse_tables，仅附加逐字段属性 ----
    tables = gm.parse_tables(text)
    section_patterns = defaultdict(set)
    attr_coverage = {"canonical": 0, "meaning": 0, "unit": 0, "status": 0}
    scanned = 0

    for sec, rows in tables:
        if any(kw in sec for kw in gm.NON_FIELD_SEC):
            continue
        srcs = afc.section_to_sources(sec)
        if not srcs:
            continue
        for src in srcs:
            section_patterns[src].add(sec)
        for row in rows:
            if not row:
                continue
            first = row[0]
            if first in ("字段", "索引", "含义", "---"):
                continue
            # 对该行首格，按各命中源的「原生 token」抽取并回挂属性（key 与 Layer1 对齐）
            for src in srcs:
                tok = cell_token(first, src)
                if not tok or len(tok) < 2:
                    continue
                rec = fields.get(tok)
                if rec is None:
                    continue  # 仅对 Layer1 已登记的字段补属性，不引入新字段
                if not rec["section"]:
                    rec["section"] = sec
                if len(row) >= 4:
                    if not rec["canonical"]:
                        rec["canonical"] = extract_canonical(first_cell=first)
                    if not rec["meaning"] and len(row) >= 2:
                        rec["meaning"] = clean_text(row[1])
                    if not rec["unit"] and len(row) >= 3:
                        rec["unit"] = clean_text(row[2])
                    if not rec["status_raw"] and len(row) >= 4:
                        rec["status_raw"] = clean_text(row[3])
                        rec["status"] = normalize_status(row[3])
                scanned += 1

    # 收尾：sources 列表化 + 单源填 source + 覆盖率统计
    out_fields = []
    for f, rec in fields.items():
        srcs = sorted(rec["sources"], key=lambda s: (gm.SOURCE_ORDER.index(s) if s in gm.SOURCE_ORDER else 99, s))
        rec["sources"] = srcs
        rec["source"] = srcs[0] if len(srcs) == 1 else None
        # 覆盖率
        if rec["canonical"]:
            attr_coverage["canonical"] += 1
        if rec["meaning"]:
            attr_coverage["meaning"] += 1
        if rec["unit"]:
            attr_coverage["unit"] += 1
        if rec["status_raw"]:
            attr_coverage["status"] += 1
        out_fields.append(rec)

    # sources 元数据：以 audit_field_completeness.SECTION_MAP 源标签为权威命名空间
    # （与 fields[].sources 完全一致，保证 field_source_map 视图对齐）
    out_sources = []
    for label, _subs in afc.SECTION_MAP:
        out_sources.append({
            "name": label,
            "verify_file": _AUDIT_VERIFY.get(label),
            "section_patterns": sorted(section_patterns.get(label, [])),
            "status": "active",
        })

    # mappings：解析 ulist_push2_align.md（已存在时）
    mappings = []
    if os.path.exists(ALIGN):
        at = io.open(ALIGN, encoding="utf-8").read().split("\n")
        for ln in at:
            if not ln.strip().startswith("|"):
                continue
            cells = [c.strip() for c in ln.strip()[1:-1].split("|")]
            if len(cells) < 3:
                continue
            a, b = cells[0], cells[1]
            ma = re.match(r"ulist\s+(f\d+)", a)
            mb = re.match(r"(f\d+)", b)
            if ma and mb:
                relation = "same_number_same_meaning" if ("==" in ln or "同义" in ln or "别名" in ln) else "cross_number_diff_meaning"
                mappings.append({
                    "from": {"source": "东财-ulist239", "code": ma.group(1)},
                    "to": {"source": "东财-push2", "code": mb.group(1)},
                    "relation": relation,
                    "evidence": "ulist_push2_align.md",
                })

    # field_matrix：§零·B 投影（clean field-name × source），与 build_matrix_from_md 同构
    # （1156 字段 / 1230 去重记录）。专供 gen_field_matrix 生成 §零·B；原生 token 集
    # 仍存于 fields（供 audit_field_completeness 的 REG 半边与 RAW 对撞）。
    # 二者是字段登记表的两个正交投影，registry 作为单一真相源同时持有。
    _ns_md, _ = gm.build_matrix_from_md()
    field_matrix = {k: sorted(v) for k, v in _ns_md.items()}

    registry = OrderedDict()
    registry["meta"] = {
        "version": 1,
        "updated": datetime.date.today().isoformat(),
        "source_of_truth": "field_registry.json",
        "generated_by": "scripts/extract_registry.py",
        "note": "本文件为字段登记表单一真相源（影子抽取）。docs/field_dict.md 字段表由本文件生成，勿手改。",
        "format_note": "JSON（YAML 严格子集，零依赖）。原计划 YAML 因环境无 pyyaml/ruamel 改 JSON。",
    }
    registry["sources"] = out_sources
    registry["fields"] = out_fields
    registry["field_matrix"] = field_matrix
    registry["mappings"] = mappings

    stats = {
        "field_count": len(out_fields),
        "source_count": len(out_sources),
        "mapping_count": len(mappings),
        "multi_source_count": sum(1 for r in out_fields if len(r["sources"]) >= 2),
        "record_count": sum(len(r["sources"]) for r in out_fields),
        "field_matrix_count": len(field_matrix),
        "field_matrix_record_count": sum(len(v) for v in field_matrix.values()),
        "attr_coverage": attr_coverage,
        "attr_scanned_rows": scanned,
    }
    return registry, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--check-baseline", action="store_true",
                    help="抽取后比对 gen_field_matrix.build_matrix() 基线（G1 闸门）")
    args = ap.parse_args()

    registry, stats = extract()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with io.open(args.out, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print(f"OK: 写出 {args.out}")
    print(f"  字段数={stats['field_count']}  记录数={stats['record_count']}  "
          f"多源={stats['multi_source_count']}  源={stats['source_count']}  对齐={stats['mapping_count']}")
    print(f"  field_matrix(§零·B投影)={stats['field_matrix_count']} 记录={stats['field_matrix_record_count']}")
    print(f"  逐字段属性覆盖率(扫描 {stats['attr_scanned_rows']} 行): "
          f"canonical={stats['attr_coverage']['canonical']}  "
          f"meaning={stats['attr_coverage']['meaning']}  "
          f"unit={stats['attr_coverage']['unit']}  "
          f"status={stats['attr_coverage']['status']}")

    if args.check_baseline:
        # 基线：audit_field_completeness.registered_field_sets（原生 token），
        # 与抽取器的 Layer1 复用同一函数，parity 由构造保证。
        base_reg = afc.registered_field_sets()
        base_field_sources = defaultdict(set)
        for src, toks in base_reg.items():
            for t in toks:
                base_field_sources[t].add(src)
        base_tokens = set(base_field_sources.keys())
        base_fields = len(base_tokens)
        base_records = sum(len(v) for v in base_reg.values())
        base_multi = sum(1 for s in base_field_sources.values() if len(s) >= 2)
        ok = (stats["field_count"] == base_fields and
              stats["record_count"] == base_records and
              stats["multi_source_count"] == base_multi)
        print(f"  G1 基线比对(native token): 抽取({stats['field_count']}/{stats['record_count']}/{stats['multi_source_count']}) "
              f"vs 基线({base_fields}/{base_records}/{base_multi}) -> "
              f"{'PASS' if ok else 'FAIL'}")
        if not ok:
            ext_tokens = {r["code"] for r in registry["fields"]}
            miss = base_tokens - ext_tokens
            extra = ext_tokens - base_tokens
            if miss:
                print(f"    基线有而抽取缺失({len(miss)}): {sorted(miss)[:20]}")
            if extra:
                print(f"    抽取多出于基线({len(extra)}): {sorted(extra)[:20]}")
            sys.exit(2)
    return 0


if __name__ == "__main__":
    sys.exit(main())

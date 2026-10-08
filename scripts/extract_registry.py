#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_registry.py — 从只读历史字典提取逐源字段证据，用于迁移与 parity。

设计原则（安全优先）：
  * 复用 gen_field_matrix.parse_tables / sec_to_source（已验证可确定性产出 1156 字段映射），
    不重写脆弱的 5395 行解析器。
  * 复用 verify_sync_check.MAPPING（源→分字典权威映射）。
  * Layer1（确定性）：field×source 映射 —— 与 build_matrix() 基线必须逐字节一致。
  * Layer2（最佳努力）：逐字段属性（canonical/meaning/unit/status），覆盖率单独报告，
    解析不到的属性留空并计入报告，绝不静默丢弃。
  * status 归一为枚举，同时保留 raw_status_text 原文（安全底线：不丢信息）。
  * 输出 JSON（YAML 严格子集，零依赖；环境无 pyyaml/ruamel，手写 emitter 风险高）。

用法（必须显式指定临时输出，不覆盖权威 registry）：
    python scripts/extract_registry.py --out .codex_tmp/field_reference_extract.json

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
DICT = os.path.join(REPO_ROOT, "docs", "field_source_reference.md")
ALIGN = os.path.join(REPO_ROOT, "docs", "verify", "ulist_push2_align.md")
# 通用跨源对齐表（非 ulist239↔push2 的等价/同义关系统一存储，sanctioned 入库）
CROSS_ALIGN = os.path.join(REPO_ROOT, "docs", "verify", "cross_source_align.md")

# 复用已验证的解析基座
sys.path.insert(0, SCRIPT_DIR)
import gen_field_matrix as gm
import audit_field_completeness as afc

# ---------------------------------------------------------------------------
# 原生 token 抽取（v2，2026-09-12）：复用 audit_field_completeness.registered_field_sets
# 的「章节→源→token」逻辑，保证 registry 的 fields[].code 即各源原生 token
# （f144 / [1] / stockName / open ...），而非被 clean_field 剥掉 f 前缀后的中文名。
# 这样 registry 才能作为 audit_field_completeness 的真相源。
# ---------------------------------------------------------------------------
_FCODE_SRC = {
    "东财-push2(stock/get)",
    "东财-ulist239(np/get)",
    "AxData",
    "东财-push2_full",
    "东财-资金流(em_fund_flow)",
    "东财-em_kline_f61",
    "东财-datacenter(英文键)",
    "东财-slist",
    "东财-clist",
}
# 注意：东财-push2ex 已从 _FCODE_SRC 移除（2026-09-20 复核修正）。
# push2ex 涨停/炸板池字段为纯英文键（c/n/p/tshare/fund/lbc...），无 f 编号；
# 原误列入 _FCODE_SRC 导致 cell_token 走 f(\d+) 分支恒返 None、全部短名字段漏挂属性。
# 现归位 _CAMEL_SRC（line 67 已在列），由 camel 英文键分支正确抽取。
_INDEX_SRC = {"腾讯(qt.gtimg)", "新浪(hq.sinajs)", "ZHB-tdxstat", "ZHB-tdxstat2", "ZHB-tipinfo"}
_CAMEL_SRC = {
    "reports",
    "同花顺-fuyao",
    "东财-datacenter(英文键)",
    "东财-push2ex",
    "东财-热榜(em_hot)",
    "市场源(market_sources)",
    "levistock(ftshare)",
    "财联社(cls)",
    "百度(baidu)",
    "沪深交易所",
    "巨潮(cninfo)",
    "TDX(双命名源)",
    "TDX-F10(双命名源)",
    # V17.3 (2026-09-18): eltdx 适配层 + ZHB 三组纳入 camel 抽取，
    # 使其带点 token(quote_snapshot.*/shortline.*/stat.*/stat2.*/tipinfo.*)
    # 在 Layer2 保留完整带点形态，与 registered_field_sets 收录形态一致，方能回挂 meaning + 标 ✅ verified。
    "TDX-eltdx(适配层)",
    "ZHB-tdxstat",
    "ZHB-tdxstat2",
    "ZHB-tipinfo",
}


def cell_token(cell: str, src: str):
    """从表格首格抽取该源原生字段 token（与 afc.reg_tokens_for_section 同语义）。"""
    cell = cell.strip().strip("`").strip()
    cell = re.sub(r"\*\*", "", cell)
    # 带点字段（quote_full.*/stat.*/snapshot.*/shortline.*）：统一优先保留完整带点 token。
    # 必须排在 _INDEX_SRC 的 [N] 分支之前——ZHB 同源既走 positional [N] 又走 stat.* 带点，
    # 否则带点 token 被 _INDEX_SRC 误判 None，导致 Layer2 无法回挂 meaning + 标 ✅ verified。
    if "." in cell and (src in _CAMEL_SRC or src in _INDEX_SRC):
        m = re.search(r"[A-Za-z_][A-Za-z0-9_.]*", cell)
        return m.group(0) if m else None
    if src in _FCODE_SRC:
        m = re.search(r"f(\d+)", cell, re.IGNORECASE)
        return ("f" + m.group(1)) if m else None
    if src in _INDEX_SRC:
        m = re.search(r"\[(\d+)\]", cell)
        return ("[" + m.group(1) + "]") if m else None
    if src in _CAMEL_SRC:
        # 不带点英文/中文名 token（与 registered_field_sets 收录形态一致）。
        m = re.search(r"[A-Za-z][A-Za-z0-9_]{2,}", cell)
        return m.group(0) if m else None
    # 默认：英文/中文名 token
    m = re.search(r"[\u4e00-\u9fffA-Za-z_][\u4e00-\u9fffA-Za-z0-9_]{1,}", cell)
    return m.group(0) if m else None


def _clean_header(h: str) -> str:
    return h.strip().strip("`").strip()


def locate_columns(header):
    """按表头列名定位「token / meaning / unit / status」列索引（兼容非标准表）。

    适用表头：
      - 标准 4 列 `| 字段 | 含义 | 单位 | 状态 |`
      - §2.1 `| 协议偏移 | 字段名(key) | 中文含义 | 类型 | 协议单位 | 还原后单位 | 字段分组 | 项目代码使用 |`
        → token=1, meaning=2, unit=5(还原后单位, 末位单位列), status=7(项目代码使用含"使用")
      - §12.8.1 `| 原始字段 | 含义 | 单位 | 项目映射 | 状态 |`
        → token=0, meaning=1, unit=2, status=4(状态, 跳过项目映射)
      - §12.8.17 `| 字段 | 含义 | 项目映射 | 状态 |` → token=0, meaning=1, status=3, 无 unit
    找不到返回 None。
    """
    token = meaning = unit = status = None
    for i, h in enumerate(header):
        c = _clean_header(h)
        if token is None:
            # 命中「字段名 / 原始字段」或精确「字段」；排除「字段分组」等含「分组」者
            if "字段名" in c or "原始字段" in c or c == "字段":
                token = i
        if meaning is None and "含义" in c:
            meaning = i
        if status is None and ("状态" in c or "使用" in c):
            # "使用" 覆盖 §2.1 末列「项目代码使用」(承载 ✅/❌)
            status = i
    # 兜底：未命中任何 token 关键字表头（如 §12.10.7a「原始键」）→ 首列为字段名列，
    # 兼容旧行为（row[0] 即 token），避免长名表（price/change_pct/limit_count 等）整体漏抽。
    if token is None:
        token = 0
    # unit：取最后一个含「单位」的列（还原后单位 在 协议单位 之后 → 优先还原后单位）
    for i, h in enumerate(header):
        if "单位" in _clean_header(h):
            unit = i
    return token, meaning, unit, status


def extract_tokens_from_cell(cell, srcs):
    """从表格首/字段列单元格抽取全部原生 token（支持 `/` 分隔多字段）。

    优先用 cell_token（按各源命名空间正确抽取 f 编号 / [索引] / 带点 / camel）；
    仅当所有 src 的 cell_token 均失败（如 1~2 字符短名 c/n/p/hs/pe/oc）时，
    兜底取单元格内 1+ 字符英文/带点 token，使其能回挂属性。
    返回保序去重 token 列表（未注册者由调用方据 fields 字典过滤）。
    """
    cell = cell.strip().strip("`").strip()
    cell = re.sub(r"\*\*", "", cell)
    out, seen = [], set()
    for part in re.split(r"[/／\s]+", cell):
        p = part.strip().strip("`*").strip()
        if not p:
            continue
        got = None
        for src in srcs:
            t = cell_token(p, src)
            if t:
                got = t
                break
        if got is None:
            m = re.search(r"[A-Za-z_][A-Za-z0-9_.]*", p)
            got = m.group(0) if m else None
        if got and got not in seen:
            seen.add(got)
            out.append(got)
    return out


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
    # 已定案同义（✅ 或 L1/L2 定案 / 跨源对撞）优先于 证伪/推翻：
    # 字段自身以 ✅ 标记即权威「已定案」，正文内 "证伪/推翻" 多指「被否决的其它次级主张」
    # （如 shuihoulirun「✅ L1…推翻旧 ❌ 标注」、tipinfo.zt_date_recent「✅…原 ex_date 误标 已证伪」），
    # 不应据此将字段整体判为 disproved。
    if (
        "✅" in t
        or "L1" in t
        or "L2" in t
        or "定案" in t
        or "数值实证" in t
        or "交叉" in t
        or "跨源" in t
    ):
        return "verified"
    # 已证伪（字段自身未标 ✅ 的纯证伪/推翻情境）
    if "证伪" in t or "推翻" in t:
        return "disproved"
    # 候选待审
    if "候选" in t or "待核" in t:
        return "candidate"
    # 已弃用 / 未接入
    if "弃用" in t or "未接入" in t or "退役" in t or "deprecated" in t.lower():
        return "deprecated"
    # 显式声明未实证/待核实/待破解/待数值对撞/疑点/常量占位/无信息量
    if (
        "未实证" in t
        or "待核实" in t
        or "待破解" in t
        or "待数值" in t
        or "疑" in t
        or "常量占位" in t
        or "无信息量" in t
        or "未接入" in t
        or "❌" in t
    ):
        return "unverified"
    # 兜底：含对撞/实测/锚/印证 等正向词 → verified，否则 unverified
    if any(k in t for k in ("对撞", "印证", "锚", "实测", "复核", "确认", "一致")):
        return "verified"
    return "unverified"


# 通用跨源对齐表(cross_source_align.md)的 id 解析：源前缀(短别名).字段 / 源前缀[索引]
# -> (source短别名, code)；code 取 collide.code_of 形态(最后一个 '.' 之后 / '[索引]')，
# 保证 collide.load_registry_state 能据 mappings 标 in_registry(durable 定案)。
_ALIGN_SRCS = {
    "fuyao",
    "tdx",
    "eltdx",
    "zhb",
    "tencent",
    "push2",
    "push2_full",
    "ulist239",
    "sina",
    "em_fund_flow",
    "event_dc",
    "push2ex",
    "em_hot",
    "exchange",
}


def _parse_align_id(idstr: str):
    s = idstr.strip().strip("`").strip()
    s = re.sub(r"\*\*", "", s)
    if not s:
        return None, None
    if "[" in s:  # tencent[52] / sina[8] -> ('tencent', '[52]')
        pre = s[: s.index("[")]
        return pre, s[s.index("[") :]
    if "." in s:  # fuyao.snapshot.price_change -> ('fuyao', 'price_change')
        # 源前缀=首个 '.' 之前(对齐 collide.alias_src); code=末个 '.' 之后(对齐 collide.code_of)
        pre = s.split(".", 1)[0]
        code = s.rsplit(".", 1)[-1]
        return pre, code
    return None, None


# 状态标记（用于行内状态信号定位；⏸ 覆盖 ⏸️ 变体）
_STATUS_MARKS = (
    "✅",
    "❌",
    "⏸",
    "证伪",
    "推翻",
    "候选",
    "待核",
    "弃用",
    "未接入",
    "退役",
    "deprecated",
)


def _row_status(row, status_idx):
    """定位行内状态信号：优先 status 列，否则扫描整行首个含状态标记的单元格。

    兼容表头与数据列数错位的行（如 §12.10.7a 的 change_pct 行多插了一个单位列，
    使 ✅ 落在 status_idx 之后的单元格）。避免 header-driven 定位时误取单位列（如 '%'）。
    """
    if status_idx is not None and status_idx < len(row):
        s = clean_text(row[status_idx])
        if s and any(m in s for m in _STATUS_MARKS):
            return s
    for cell in row:
        c = clean_text(cell)
        if c and any(m in c for m in _STATUS_MARKS):
            return c
    return ""


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
    source_fields = OrderedDict()
    for src, toks in reg.items():
        for tok in sorted(toks):
            source_fields[(src, tok)] = {
                "source": src,
                "code": tok,
                "canonical": "",
                "meaning": "",
                "unit": "",
                "status_raw": "",
                "status": "unverified",
                "section": "",
                "sections": [],
                "evidence": [],
            }
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

    for sec, header, rows in tables:
        if any(kw in sec for kw in gm.NON_FIELD_SEC):
            continue
        srcs = afc.section_to_sources(sec)
        if not srcs:
            continue
        for src in srcs:
            section_patterns[src].add(sec)
        # 表头驱动列定位：兼容标准 4 列表 & §2.1/§12.8.1/§12.8.17 非标准表
        t_idx, m_idx, u_idx, s_idx = locate_columns(header)
        if t_idx is None:
            continue
        for row in rows:
            if not row or t_idx >= len(row):
                continue
            tok_cell = row[t_idx].strip().strip("`").strip()
            # 跳过表头残留 / 分隔行关键字（按字段列判定）
            if tok_cell in ("字段", "索引", "含义", "---", "协议偏移", "原始字段"):
                continue
            # 首列/`/` 分隔的多字段（zqdm/zqjc、zttj.days/zttj.ct、yfbt/ylbc）逐 token 回挂同一属性
            for tok in extract_tokens_from_cell(tok_cell, srcs):
                if not tok:
                    continue
                rec = fields.get(tok)
                if rec is None:
                    continue  # 仅对 Layer1 已登记的字段补属性，不引入新字段
                if not rec["section"]:
                    rec["section"] = sec
                if not rec["canonical"]:
                    rec["canonical"] = extract_canonical(first_cell=tok_cell)
                if m_idx is not None and m_idx < len(row) and not rec["meaning"]:
                    rec["meaning"] = clean_text(row[m_idx])
                if u_idx is not None and u_idx < len(row) and not rec["unit"]:
                    rec["unit"] = clean_text(row[u_idx])
                if not rec["status_raw"]:
                    sr = _row_status(row, s_idx)
                    if sr:
                        rec["status_raw"] = sr
                        rec["status"] = normalize_status(sr)
                scanned += 1

            # Source-scoped pass: never attach one source's table metadata to
            # another source that happens to share the same bare token.
            for src in srcs:
                for tok in extract_tokens_from_cell(tok_cell, [src]):
                    rec = source_fields.get((src, tok))
                    if rec is None:
                        continue
                    status_raw = _row_status(row, s_idx)
                    evidence = {
                        "section": sec,
                        "canonical": extract_canonical(first_cell=tok_cell),
                        "meaning": (
                            clean_text(row[m_idx]) if m_idx is not None and m_idx < len(row) else ""
                        ),
                        "unit": (
                            clean_text(row[u_idx]) if u_idx is not None and u_idx < len(row) else ""
                        ),
                        "status_raw": status_raw,
                        "status": normalize_status(status_raw) if status_raw else "",
                    }
                    rec["evidence"].append(evidence)

    # 收尾：sources 列表化 + 单源填 source + 覆盖率统计
    out_fields = []
    for f, rec in fields.items():
        srcs = sorted(
            rec["sources"],
            key=lambda s: (gm.SOURCE_ORDER.index(s) if s in gm.SOURCE_ORDER else 99, s),
        )
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

    out_source_fields = []
    for rec in source_fields.values():
        evidence = rec["evidence"]
        for key in ("canonical", "meaning", "unit"):
            values = sorted({item[key] for item in evidence if item.get(key)})
            rec[key] = values[0] if len(values) == 1 else ""
            if len(values) > 1:
                rec.setdefault("attribute_conflicts", {})[key] = values
        sections = sorted({item["section"] for item in evidence if item.get("section")})
        rec["sections"] = sections
        rec["section"] = sections[0] if len(sections) == 1 else ""
        explicit_statuses = sorted({item["status"] for item in evidence if item.get("status")})
        raw_statuses = sorted({item["status_raw"] for item in evidence if item.get("status_raw")})
        rec["reference_statuses"] = explicit_statuses
        rec["status_raw_values"] = raw_statuses
        if len(explicit_statuses) == 1:
            rec["status"] = explicit_statuses[0]
        elif len(explicit_statuses) > 1:
            rec["status"] = "conflict"
            rec["status_resolution"] = "reference_status_conflict"
        else:
            rec["status"] = "unverified"
            rec["status_resolution"] = "reference_status_missing"
        rec["status_raw"] = raw_statuses[0] if len(raw_statuses) == 1 else ""
        out_source_fields.append(rec)

    # sources 元数据：以 audit_field_completeness.SECTION_MAP 源标签为权威命名空间
    # （与 fields[].sources 完全一致，保证 field_source_map 视图对齐）
    out_sources = []
    seen_source_labels = set()
    for label, _subs in afc.SECTION_MAP:
        if label in seen_source_labels:
            continue
        seen_source_labels.add(label)
        out_sources.append(
            {
                "name": label,
                "verify_file": _AUDIT_VERIFY.get(label),
                "section_patterns": sorted(section_patterns.get(label, [])),
                "status": "active",
            }
        )

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
                relation = (
                    "same_number_same_meaning"
                    if ("==" in ln or "同义" in ln or "别名" in ln)
                    else "cross_number_diff_meaning"
                )
                mappings.append(
                    {
                        "from": {"source": "东财-ulist239", "code": ma.group(1)},
                        "to": {"source": "东财-push2", "code": mb.group(1)},
                        "relation": relation,
                        "evidence": "ulist_push2_align.md",
                    }
                )

    # 通用跨源对齐（非 ulist239↔push2）：cross_source_align.md
    # 承载 fuyao/tdx/eltdx/zhb/tencent/push2/push2_full/sina/em_fund_flow/event_dc/push2ex/em_hot/exchange 任意源对的等价/同义关系，
    # 经 _parse_align_id 解析为 (源短别名, code)，collide 标 in_registry 后 durable 定案。
    if os.path.exists(CROSS_ALIGN):
        for ln in io.open(CROSS_ALIGN, encoding="utf-8").read().split("\n"):
            if not ln.strip().startswith("|"):
                continue
            cells = [c.strip() for c in ln.strip()[1:-1].split("|")]
            if len(cells) < 2:
                continue
            pa, ca = _parse_align_id(cells[0])
            pb, cb = _parse_align_id(cells[1])
            # 仅接受已知源前缀（表头/分隔行等非源前缀自动跳过，避免污染 mappings）
            if not (pa and ca and pb and cb and pa in _ALIGN_SRCS and pb in _ALIGN_SRCS):
                continue
            relation = (
                "same_number_same_meaning"
                if ("==" in ln or "同义" in ln or "别名" in ln)
                else "cross_number_diff_meaning"
            )
            evidence = cells[4] if len(cells) >= 5 else "cross_source_align.md"
            mappings.append(
                {
                    "from": {"source": pa, "code": ca},
                    "to": {"source": pb, "code": cb},
                    "relation": relation,
                    "evidence": evidence,
                }
            )

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
    registry["source_fields"] = out_source_fields
    registry["field_matrix"] = field_matrix
    registry["mappings"] = mappings

    stats = {
        "field_count": len(out_fields),
        "source_field_count": len(out_source_fields),
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
    ap.add_argument(
        "--out",
        required=True,
        help="必填：输出到临时/比较路径；本脚本不直接覆盖权威 field_registry.json",
    )
    ap.add_argument(
        "--check-baseline",
        action="store_true",
        help="抽取后比对 gen_field_matrix.build_matrix() 基线（G1 闸门）",
    )
    args = ap.parse_args()

    registry, stats = extract()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with io.open(args.out, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    print(f"OK: 写出 {args.out}")
    print(
        f"  字段数={stats['field_count']}  记录数={stats['record_count']}  "
        f"多源={stats['multi_source_count']}  源={stats['source_count']}  对齐={stats['mapping_count']}"
    )
    print(
        f"  field_matrix(§零·B投影)={stats['field_matrix_count']} 记录={stats['field_matrix_record_count']}"
    )
    print(
        f"  逐字段属性覆盖率(扫描 {stats['attr_scanned_rows']} 行): "
        f"canonical={stats['attr_coverage']['canonical']}  "
        f"meaning={stats['attr_coverage']['meaning']}  "
        f"unit={stats['attr_coverage']['unit']}  "
        f"status={stats['attr_coverage']['status']}"
    )

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
        ok = (
            stats["field_count"] == base_fields
            and stats["record_count"] == base_records
            and stats["multi_source_count"] == base_multi
        )
        print(
            f"  G1 基线比对(native token): 抽取({stats['field_count']}/{stats['record_count']}/{stats['multi_source_count']}) "
            f"vs 基线({base_fields}/{base_records}/{base_multi}) -> "
            f"{'PASS' if ok else 'FAIL'}"
        )
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

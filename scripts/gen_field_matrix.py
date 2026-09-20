#!/usr/bin/env python3
"""gen_field_matrix.py — 从 field_dict.md 生成 §零·B 字段×源总表（自动生成，勿手改）。

用法: python scripts/gen_field_matrix.py
幂等: 读取 field_dict.md，替换 <!-- GEN:field-matrix --> 标记区间，原地更新。
"""
from __future__ import annotations

import io
import json
import os
import re
import sys
from collections import defaultdict

# Phase 2(2026-09-12): registry 单一真相源访问层。治理脚本改读 registry 而非解析 markdown。
# 本模块既产 extract_registry 的抽取源，也消费 registry——通过 build_matrix() 的
# use_registry 开关切换，避免 extract（须读 markdown）与运行时（读 registry）互相污染。
import field_registry_api as fra

# V16.4.1: 强制 UTF-8 输出（下沉到代码自身——任何 agent/机器/直接运行均 UTF-8，
# 不依赖系统代码页/环境变量/Profile；纯标准库，幂等）
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT = os.path.join(ROOT, "docs", "field_dict.md")

# 源排序（易→难，V16.3 O18 修正——依据参考仓库 v3.2 数据源优先级 + 实测：
# ZHB 离线零网络 → TDX TCP/腾讯 不封 IP 首选 → 新浪/巨潮 低风险其次 → 同花顺 有 401 反爬史 →
# AxData local 未充分验证 → 东财 最难（45000/h 封禁 20h + 观察期 + 共享风控）仅独有数据）
SOURCE_ORDER = [
    "ZHB",
    "TDX-0x0010/F10",
    "TDX-eltdx",
    "腾讯",
    # V17.0.7 层级定案: 同花顺-fuyao(REST) 升至腾讯之后——官方口径/盘后可查/
    # 独立风控域(4001 退避), 已升为财务 TTM 族主源; thsdk(TCP) 盘后关闸 →
    # 盘中专属特殊层, 排其后、东财前。
    "同花顺-fuyao",
    "新浪",
    "巨潮",
    "同花顺",
    "财联社",
    "开盘红",
    "akshare",
    "levistock",
    "百度",
    "沪深交易所",
    "AxData",
    "东财",
]
# 非真实源（不参与字段×源投影）：聚合/对照标签 + 已退役源。
# 2026-09-12: 追加 "同花顺-thsdk" —— 该源已于 V17.0.29(2026-09-07) 从项目彻底移除
# （仅盘中可用，与盘后/盘前场景不符，且无不可替代字段），其 §12.8.12b 章节保留为退役追溯记录，
# 但字段不再进入活体投影（避免误导为可用源）。
NOT_REAL_SOURCE = ("跨源对照", "其他", "同花顺-thsdk")

# 非字段表过滤
NON_FIELD_SEC = ("覆盖统计", "文件元信息", "接口分类全景", "已解析并使用", "未被代码解析",
                 "辅助文件", "域名管理", "策略中的典型应用", "数据流", "调用链路",
                 "典型应用公式", "字段源状态码",
                 # 2026-09-19: §12.15.10 治理元表（源→分字典映射手写表 + GEN 自动索引）非字段表，
                 # 其单元格含 `东财-ulist239(np/get)` 等源名，按 `/` 切分会被 clean_field 误判为伪字段 token；
                 # 排除后 §零·B 对照基线不再被 §12.15.10 污染（不影响 §零·B 渲染，其读 registry）。
                 "同步分字典", "分字典索引")


def sec_to_source(sec: str) -> str:
    s = sec
    # V17.0.7: THS 族识别——必须在东财分支之前(12.8.12c/d 含 "12.8" 子串会被误判)
    if "fuyao" in s or "12.8.12c" in s or "12.8.12d" in s:
        return "同花顺-fuyao"
    if "thsdk" in s or "sc_ths" in s or "12.8.12b" in s:
        return "同花顺-thsdk"
    if "腾讯" in s:
        return "腾讯"
    if "新浪" in s:
        return "新浪"
    if "tdxstat" in s or "tipinfo" in s or "ZHB" in s or "zhb" in s:
        return "ZHB"
    if ("push2" in s or "datacenter" in s or "clist" in s or "slist" in s
            or "12.8" in s or "12.9" in s or "东财" in s):
        return "东财"
    if "同花顺" in s:
        return "同花顺"
    if "财联社" in s:
        return "财联社"
    if "巨潮" in s:
        return "巨潮"
    if "开盘红" in s or "kph" in s:
        return "开盘红"
    if "akshare" in s:
        return "akshare"
    if "AxData" in s or "axdata" in s or "12.12" in s:
        return "AxData"
    if "eltdx" in s or "easy_tdx" in s or "12.13" in s:
        return "TDX-eltdx"
    if "F10" in s or "0x0010" in s or "协议完整" in s or "Gemini 核实" in s or "2.1" in s or "2.2" in s:
        return "TDX-0x0010/F10"
    if "百度" in s:
        return "百度"
    if "交易所" in s or "沪深" in s:
        return "沪深交易所"
    if "levistock" in s or "12.10" in s:
        return "levistock"
    if "多源" in s or "对照" in s or "优先级" in s or "矩阵" in s or "状态码" in s or "12.5" in s or "12.4" in s:
        return "跨源对照"
    return "其他"


def parse_tables(text: str):
    """提取 (章节, 表头, 数据行) 列表。表头=首行（block[0]），block[1] 为分隔行。"""
    lines = text.split("\n")
    cur_sec = ""
    tables = []
    i, n = 0, len(lines)
    while i < n:
        l = lines[i]
        m = re.match(r"^#{1,4} (.*)", l)
        if m:
            cur_sec = m.group(1).strip()
        if l.strip().startswith("|"):
            j = i
            block = []
            while j < n and lines[j].strip().startswith("|"):
                cells = [c.strip() for c in lines[j].strip()[1:-1].split("|")]
                if cells:
                    block.append(cells)
                j += 1
            if len(block) >= 3:
                sep = block[1]
                is_sep = len(sep) >= 2 and all(re.match(r"^:?-{2,}:?$", c or "-") for c in sep)
                if is_sep:
                    tables.append((cur_sec, block[0], block[2:]))
            i = j
        else:
            i += 1
    return tables


def clean_field(name: str) -> str:
    s = name.strip("` |")
    s = re.sub(r"\*\*", "", s)  # markdown 加粗
    # 索引/序号/示例日期（须在 `**` 剥离后逐轮清理）
    s = re.sub(r"^[\[（(][一二三四五六七八九十]+[\]）)]", "", s)  # 中文序号 (三)
    s = re.sub(r"^\d{8}\s*", "", s)  # 示例日期 20260727
    s = re.sub(r"^[-—–]?\[?\d+\]?$", "", s)  # 纯索引 [0] / -[18]
    s = re.sub(r"^\[?\d+\]?\s*-\s*\[?\d+\]?$", "", s)  # 范围 [9]-[18]
    s = re.sub(r"^0x[0-9A-Fa-f]+", "", s)
    s = re.sub(r"^[fF]\d+", "", s)
    s = re.sub(r"^Col\[\d+\]", "", s)
    s = re.sub(r"^【", "", s)
    s = re.sub(r"^[\d\]]+", "", s)  # markdown 链接截断残留：'8] 涨跌幅滑动对' → '涨跌幅滑动对'
    s = s.strip()
    if not s or len(s) < 2:
        return ""
    if re.fullmatch(r"[\*\-\s—–·]+", s):
        return ""
    if re.fullmatch(r"[（(][一二三四五六七八九十]+[）)]", s):  # 残留中文序号 (一)
        return ""
    if s in ("字段", "索引", "含义", "---"):
        return ""
    return s


# Phase 2(2026-09-12): 抽离纯 markdown 路径为 build_matrix_from_md（golden baseline）。
# extract_registry 与 registry_parity 的 golden 对照均调用此函数，避免与 registry 路径互相污染。
def build_matrix_from_md():
    text = io.open(DICT, encoding="utf-8").read()
    name_sources = defaultdict(set)
    records = 0
    for sec, _header, rows in parse_tables(text):
        if any(kw in sec for kw in NON_FIELD_SEC):
            continue
        src = sec_to_source(sec)
        if src in NOT_REAL_SOURCE:
            continue
        for row in rows:
            if not row:
                continue
            first = row[0]
            if first in ("字段", "索引", "含义", "---"):
                continue
            for part in re.split(r"[/／]", first):
                f = clean_field(part)
                if len(f) < 2:
                    continue
                name_sources[f].add(src)
                records += 1
    return name_sources, records


# Phase 2/3(2026-09-12): registry 单一真相源路径（与 build_matrix_from_md 同构：{clean_name: set(sources)}）。
# 由 field_registry_api.field_matrix_map 提供 §零·B 投影视图（1156 清洗字段名 / 1230 去重记录）；
# 任何读取失败抛异常交由 build_matrix 回退 markdown。
def build_matrix_from_registry():
    reg = fra.load_registry()
    fm = fra.field_matrix_map(reg)
    name_sources = defaultdict(set)
    for code, srcs in fm.items():
        name_sources[code].update(srcs)
    records = sum(len(v) for v in fm.values())
    return name_sources, records


def build_matrix(use_registry: bool = False):
    """Phase 2 统一入口。

    - use_registry=True（默认给更新路径）：读 field_registry.json，不再解析 markdown 体积。
    - use_registry=False（extract / parity golden 必须走此）：读 markdown，作为回退与对照基线。
    失败时回退 markdown，保证脚本永不因 registry 缺失而硬失败。
    """
    if use_registry:
        try:
            return build_matrix_from_registry()
        except Exception as _e:  # registry 缺失/损坏 → 回退 markdown
            print(f"[gen_field_matrix] registry 读取失败，回退 markdown: {_e}", file=sys.stderr)
            return build_matrix_from_md()
    return build_matrix_from_md()


def render(name_sources, records) -> str:
    order = {s: i for i, s in enumerate(SOURCE_ORDER)}

    def sort_sources(srcs):
        return sorted(srcs, key=lambda s: (order.get(s, 99), s))

    multi = {f: srcs for f, srcs in name_sources.items() if len(srcs) >= 2}
    single = defaultdict(list)
    for f, srcs in name_sources.items():
        if len(srcs) == 1:
            single[next(iter(srcs))].append(f)

    out = []
    out.append("### 零·B 字段×源总表（自动生成，勿手改）\n")
    out.append(f"> 生成：`scripts/gen_field_matrix.py`（Phase 2 起从 field_registry.json 单一真相源读取，"
               f"不再解析 field_dict.md 体积）。共 {len(name_sources)} 个字段 / {records} 条字段×源记录"
               f"（去重配对口径，取代旧版按行出现的 1412 重复计数）。\n")
    out.append("> 源排序按易→难（V17.0.7 层级定案；2026-09-07 thsdk 已退役，不再列为活体源）："
               "ZHB（离线零网络）→ TDX TCP（0x0010/F10/eltdx）→ "
               "腾讯（不封 IP）→ **同花顺-fuyao（官方 REST，盘后可查+独立风控域，V17.0.7 升为财务 TTM 族主源）** → "
               "新浪 → 巨潮 → 东财（限流最严）→ 其他。\n")
    out.append("> 字段名基于章节标题分类推断，精确接口见各节；正文修改后重跑本脚本即同步。\n")
    out.append(f"**B.1 多源字段（{len(multi)} 个，fallback 路由表）**\n")
    out.append("| 字段 | 源数 | 源（按易→难） |")
    out.append("|:---|:---:|:---|")
    for f in sorted(multi, key=lambda x: -len(multi[x])):
        srcs = sort_sources(multi[f])
        out.append(f"| {f} | {len(srcs)} | {'、'.join(srcs)} |")
    out.append("")
    out.append(f"**B.2 单源字段（{len(name_sources) - len(multi)} 个，无 fallback）**\n")
    for src in SOURCE_ORDER:
        fields = sorted(single.get(src, []))
        if not fields:
            continue
        out.append(f"- **{src}（{len(fields)}）**：{'、'.join(fields[:60])}")
        if len(fields) > 60:
            out.append(f"  - … 其余 {len(fields) - 60} 个见正文")
    out.append("")
    return "\n".join(out)


# P0(2026-09-11): §零·B 写回收缩护栏。
# 基线不取 §零·B 自身——其 B.2 单源列表按源截断至 60 条（render 刻意摘要），非全量镜像，
# 用作基线会严重低估。改为用「最近一次成功生成」的字段数快照 sidecar 作权威基线；
# 该 sidecar 须随字典一并提交，CI 方能生效。
_ZERO_B_SHRINK_RATIO = 0.90
_ZERO_B_BASELINE = os.path.join(ROOT, "docs", "field_verification", "zero_b_field_baseline.json")


def _load_baseline() -> int:
    """返回最近一次成功生成的字段数；无快照返回 -1（首次运行不护栏）。"""
    try:
        with io.open(_ZERO_B_BASELINE, encoding="utf-8") as _fh:
            return int(json.load(_fh).get("count", -1))
    except Exception:
        return -1


def _save_baseline(count: int) -> None:
    import datetime as _dt
    with io.open(_ZERO_B_BASELINE, "w", encoding="utf-8") as _fh:
        json.dump({"count": count, "updated": _dt.date.today().isoformat()},
                  _fh, ensure_ascii=False, indent=2)
def update_dict(force: bool = False, use_registry: bool = True) -> None:
    # Phase 2: 默认从 registry 读取（单一真相源），不再依赖 markdown 体积。
    # --from-md 时回退 markdown 以做回归对照。
    name_sources, records = build_matrix(use_registry=use_registry)
    content = render(name_sources, records)
    text = io.open(DICT, encoding="utf-8").read()
    # ---- P0 护栏 ----
    baseline = _load_baseline()
    new_count = len(name_sources)
    if baseline > 0 and new_count < baseline * _ZERO_B_SHRINK_RATIO and not force:
        raise SystemExit(
            f"ABORT §零·B 写回: 字段数 {baseline} → {new_count}（骤降 "
            f"{100 * (1 - new_count / baseline):.1f}% > "
            f"{100 * (1 - _ZERO_B_SHRINK_RATIO):.0f}%）\n"
            f"  疑似主字典章节被归档/误删导致输入萎缩。若确认系字段真实下线，"
            f"请加 --force 重跑：python scripts/gen_field_matrix.py --force"
        )
    marker = "<!-- GEN:field-matrix -->"
    start = text.find(marker)
    end_marker = "<!-- /GEN:field-matrix -->"
    end = text.find(end_marker)
    if start == -1:
        raise SystemExit("field_dict.md 缺少 §零·B 标记，先手动插入占位")
    head = text[: start + len(marker)]
    tail = text[end:] if end != -1 else text[text.find("\n", start):]
    # 保持尾部缩进（marker 后紧跟换行）
    io.open(DICT, "w", encoding="utf-8").write(head + "\n\n" + content + "\n" + tail)
    _save_baseline(new_count)
    print(f"OK: {len(name_sources)} 字段 / {records} 记录 / 多源 {len([s for s in name_sources.values() if len(s) >= 2])}")


if __name__ == "__main__":
    import argparse

    _ap = argparse.ArgumentParser(description="从 field_registry.json 生成 §零·B 字段×源总表（marker 区间原地写回）")
    _ap.add_argument("--force", action="store_true",
                     help="忽略 §零·B 写回收缩护栏（仅当确认字段真实下线时使用）")
    _ap.add_argument("--from-md", action="store_true",
                     help="回归模式：从 field_dict.md 读取而非 registry（用于 parity 对照）")
    _args = _ap.parse_args()
    update_dict(force=_args.force, use_registry=not _args.from_md)

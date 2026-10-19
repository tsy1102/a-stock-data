#!/usr/bin/env python3
"""audit_field_completeness.py — 主字典字段完整性审计（v4 双向覆盖）。

RAW = 指定采集目录中各源用「源原生命名」提取的真实返回字段集。
REG = 优先读取 registry.source_fields；缺失时从 field_source_reference.md 提取已登记字段集。
RAW-only = RAW − REG —— 源返回了但字段登记中没有的字段，供人工复核。
REG-only = REG − RAW —— 本次归档未观察到的登记字段，可能是未采源、请求失败、稀疏字段或采集覆盖缺口。

v4 修正点：
  - 每个字段集合合并采样目录中所有成功或部分成功股票，并遍历列表全部行，避免首股/首行缺字段造成漏报。
  - 报告双向差异；RAW-only 与 REG-only 分栏，REG-only 不直接定性为采集器错误。
  - 失败/跳过记录中仍有有效字段时保留部分证据，纯错误占位记录仍排除。
v3 修正点 vs v2：
  - split_sections 返回 (level, title, text)；registered_field_sets 按标题层级继承源：
    子章节(如 #### 12.10.1)若自身标题不匹配任何源关键词，则继承最近祖先标题匹配的源
    （如 ### 12.10 levistock）。修复 v2 因「仅看当前标题」导致 levistock/datacenter/市场源 reg=0 的假缺口。
  - section_to_source → section_to_sources 返回「匹配到的所有源」列表（一个章节可归属多源，
    如 §12.3.4 资金流四档既属 push2 又属 em_fund_flow），REG 令牌累加到每个源。
  - ZHB 登记记号统一为表格首列加粗索引 **[N]**（非 Col[N]）；RAW 端也改为 0 索引 [N]，与字典对齐。
  - 新增 em_fund_flow 专属 SECTION_MAP（§12.3.4），同时保留在 push2 列表（共享 f135-f149）。
  - TDX / TDX-F10 仍标「双命名源」，reg 扫描 snake_case 叶名仅供人工复核参考，不强行 diff。
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import glob
from functools import lru_cache
from collections import defaultdict

# (b) 架构根治：优先从 field_registry.json 单一真相源读取「已登记字段集」，
# 使 §零·A 主路径不再依赖 SECTION_MAP / section_to_sources 的字典章节解析（G0 标记脆弱点）。
# registry 缺失或读失败时回退 registered_field_sets()（字典解析）。
import field_registry_api as _fra

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT = os.path.join(ROOT, "docs", "field_source_reference.md")
SOURCE_IDENTITY_RECLASSIFICATIONS = os.path.join(
    ROOT, "docs", "field_verification", "source_identity_reclassifications.json"
)
# v3.1 (2026-09-06): CAP/OUT 日期参数化 —— 每次全源采集后必须对「当日 raw」重跑本审计,
# 否则审计永远停在上一次捕获日, 形成 A7(文档代码同真) 口径漂移。
# 用法: python scripts/audit_field_completeness.py [CAP_DATE] [OUT_DATE]
#   例: python scripts/audit_field_completeness.py 20260906 20260906
#   不带参数则沿用历史默认: CAP=20260904, OUT=20260906。
# 导入本模块只初始化历史默认值；CLI 参数仅在 main() 中解析，避免污染导入方参数。
DEFAULT_CAPTURE_DATE = "20260904"
DEFAULT_OUTPUT_DATE = "20260906"
CAP = os.path.join(ROOT, "docs", "field_verification", DEFAULT_CAPTURE_DATE)
OUTDIR = os.path.join(ROOT, "docs", "field_verification", DEFAULT_OUTPUT_DATE)


def loadjson(f):
    path = os.path.join(CAP, f)
    try:
        with io.open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return {}


_CAPTURE_METADATA_KEYS = frozenset(
    {
        "__error__",
        "__skipped__",
        "__unwired__",
        "__source_meta__",
        "__identity__",
        "auction_snapshot_meta",
        "field_meta",
        "scheme",
    }
)


def _has_capture_value(value):
    if isinstance(value, dict):
        return any(
            key not in _CAPTURE_METADATA_KEYS and _has_capture_value(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(_has_capture_value(child) for child in value)
    return value is not None and value != ""


def _stock_records(document):
    stocks = document.get("stocks") if isinstance(document, dict) else None
    if not isinstance(stocks, dict):
        return []
    return [
        record
        for record in stocks.values()
        if isinstance(record, dict) and _has_capture_value(record)
    ]


def first_stock(d):
    return next(iter(_stock_records(d)), {})


def all_stock_leaves(document):
    """Return the union of observed leaf keys across all usable stock records."""
    fields = set()
    for record in _stock_records(document):
        fields.update(_leaf_keys(record))
    return fields


def compare_field_sets(raw_fields, registered_fields):
    """Split observed-unregistered and registered-unobserved names explicitly."""
    raw_set = set(raw_fields)
    registered_set = set(registered_fields)
    return {
        "matched": raw_set & registered_set,
        "unregistered_raw": raw_set - registered_set,
        "registered_not_observed": registered_set - raw_set,
    }


def _field_union_from_captures(filenames, container="data", pattern=r"f\d+"):
    fields = set()
    for filename in filenames:
        document = loadjson(filename)
        for record in _stock_records(document):
            values = record.get(container)
            if isinstance(values, dict):
                fields.update(key for key in values if re.fullmatch(pattern, key))
    return fields


def split_sections(text):
    """返回 [(level, title, text)]，按 Markdown 标题切分，level=标题 # 个数。"""
    lines = text.split("\n")
    secs = []
    cur = None
    cur_lv = 0
    buf = []
    for l in lines:
        m = re.match(r"^(#{1,6}) (.*)", l)
        if m:
            if cur is not None:
                secs.append((cur_lv, cur, "\n".join(buf)))
            cur = m.group(2).strip()
            cur_lv = len(m.group(1))
            buf = []
        else:
            if cur is not None:
                buf.append(l)
    if cur is not None:
        secs.append((cur_lv, cur, "\n".join(buf)))
    return secs


# 源章节归属（sub 为章节标题子串；一个章节可命中多个源）
SECTION_MAP = [
    (
        "东财-push2(stock/get)",
        [
            "12.3.1 单股行情",
            "12.3.1.1",
            "12.3.1.2",
            "12.9.1 push2 stock/get",
            "12.9.2",
            "12.3.3 日K线",
            "12.8.2 东财 push2 历史",
            "12.8.7 东财 push2 资金流",
            "12.3.4 资金流四档",
        ],
    ),
    ("东财-资金流(em_fund_flow)", ["12.3.4 资金流四档", "12.8.7 东财 push2 资金流"]),
    ("东财-ulist239(np/get)", ["12.3.2"]),
    ("东财-push2ex", ["12.8.1 东财 push2ex"]),
    ("东财-datacenter(英文键)", ["12.8.3 东财 datacenter"]),
    ("东财-slist", ["12.8.5 东财 slist"]),
    ("东财-clist", ["12.8.6 东财 clist"]),
    ("腾讯(qt.gtimg)", ["12.1 腾讯"]),
    ("新浪(hq.sinajs)", ["12.2 新浪"]),
    ("新浪(扩展API)", ["12.8.14 新浪"]),
    (
        "同花顺-fuyao",
        [
            "12.8.12c",
            "12.8.12e",
            "12.8.12d",
            "12.8.12i fuyao 财务报表叶字段补录",
            "12.8.12f fuyao 财务指标 index_id",
            "12.8.12g fuyao 黄金锚",
            "12.8.12k fuyao 网站中文名黄金锚",
        ],
    ),
    # V17.2.13 补登：TDX / AxData / push2_full 此前从未进 SECTION_MAP（仅 _CAMEL_SRC/_FCODE_SRC
    # 预留了命名空间），导致 registry/§零·B/field_matrix 长期漏抽这三源——与 capture_field_probe.py
    # 实际采集清单（e63edbd 起即含 tdx/axdata/push2_full）严重脱节。现据主字典正文章节补登。
    (
        "TDX(双命名源)",
        [
            "零·A TDX F10",
            "TCP GetFinanceInfo",
            "TDX tdx_quotes",
            "12.8.19 通达信问小达",
            "12.13.2 财务批量",
            "2.2 字段组分类与策略价值",
            "2.3 项目实际使用情况",
            "2.4 字段组在策略中的典型应用公式",
            "2.5 协议调用链路与数据流",
            "2.6 与 Gemini 核实 18 字段的对比",
            "12.13.3 除权除息",
            # 2026-09-20：补登 §2.1 协议完整 36 字段表（用户称 §2.2 静态股本节）。
            # 该节 37 个拼音/英文名 token 早已经 RAW_FIELD_KEYS 注册于本源，
            # 但此前 SECTION_MAP 缺登 → section_to_sources 返回 [] → Layer2 永不处理
            # → meaning/status 全空。补登后 Layer2 据表头列名（token=col1 字段名、
            # meaning=col2 中文含义、status=col7 项目代码使用）回挂属性。
            # 0 新增 token（仅激活既有 token 的属性回挂），registered_field_sets 自洽、G1 parity-safe。
            "2.1 协议完整 36 字段表",
        ],
    ),
    (
        "AxData",
        [
            "12.12 AxData 接口全景",
            "12.12.0 AxData 全量接口目录",
            "12.12.8 跨源接口实测确认",
            "12.14 多源字段补齐矩阵",
        ],
    ),
    ("东财-push2_full", ["12.3.1 单股行情"]),
    # 同花顺-thsdk 已于 V17.0.29 从项目删除（sc_ths.py 移除、sc_datasource 不再 import），
    # 属死源，依规退役（12.8.12b 章节保留为历史文档，不再进 registry/§零·B）。
    ("ZHB-tdxstat", ["tdxstat.cfg"]),
    ("ZHB-tdxstat2", ["tdxstat2.cfg"]),
    ("ZHB-tipinfo", ["tipinfo.dat"]),
    # V17.3 (2026-09-18): 新增 eltdx 适配层源。此前 eltdx 在 §12.13.10/§12.13.11 有字段章节但
    # 无 SECTION_MAP 条目 → registered_field_sets() 恒产 0 token → 审计/registry 长期漏抽 eltdx。
    # 现据主字典章节补登，使其 quote_snapshot.* / shortline.* 带点 token 与 tdx/zhb 同权 registered + verified。
    (
        "TDX-eltdx(适配层)",
        [
            "12.13.4 涨跌停限制",
            "12.13.5 K线",
            "12.13.6 行情列表",
            "12.13.7 服务器统计资源",
            "12.13.10",
            "12.13.11",
        ],
    ),
    ("财联社(cls)", ["12.8.13 财联社", "12.8.13.1 财联社快讯", "12.10.5 板块轮动与热度"]),
    ("百度(baidu)", ["12.8.16 百度"]),
    ("沪深交易所", ["12.8.17 沪深交易所"]),
    ("巨潮(cninfo)", ["12.8.15 巨潮"]),
    # V17.1.x 补：reports(东财 reportapi) 与 em_kline_f61(日K线端点) 此前无任何 SECTION_MAP 条目，
    # 导致 reg 恒 0、审计永久报「无 raw 捕获」假象——实为工具缺陷，非未采集。
    (
        "reports",
        [
            "12.8.4 东财 reportapi",
            "12.8.4.1 东财 reportapi 全量 51 字段表",  # V17.1.x 全量登记
            "12.9.2 其他接口实测发现",
        ],
    ),  # §12.9.2 含「reportapi 研报（实测 51 字段）」全表
    ("东财-em_kline_f61", ["12.3.3 日K线"]),
    ("东财-datacenter(英文键)", ["12.8.3.1 datacenter 北向持股"]),
    ("东财-热榜(em_hot)", ["em_hot", "热榜"]),
    ("市场源(market_sources)", ["market_sources", "市场源", "市场情绪"]),
    (
        "开盘啦(kpl)",
        [
            "12.17 KPL 开盘啦",
            "12.17.1 kaipanla-data-parser 补充",
            "12.21 开盘啦 App 数据解析工具",
            "12.21.1 ZhiShuStockList_W8",
            "12.21.2 GetPanKou",
            "12.21.3 SonPlate_Info",
            "12.21.4 Socket Protobuf",
            "12.21.5 无 Token 穷尽实测",
        ],
    ),
    # 历史原文是只读档案，仍按旧混合标题解析；registered_field_sets 在解析后
    # 通过 source_identity_reclassifications.json 显式映射到当前来源身份。
    ("levistock(ftshare)", ["ftshare", "FTShare", "开盘红", "levistock"]),
]


def section_to_sources(sec):
    out = []
    for label, subs in SECTION_MAP:
        for sub in subs:
            if sub in sec:
                out.append(label)
                break
    return out


@lru_cache(maxsize=1)
def source_identity_reclassification():
    """Load the explicit migration map for the immutable legacy source archive."""
    with io.open(SOURCE_IDENTITY_RECLASSIFICATIONS, encoding="utf-8") as f:
        return json.load(f)


def reclassified_source_for_token(source, token):
    """Return the current source identity for an archived source/token pair.

    `None` means the legacy parser found an archive-only token that was never part
    of the structured registry and must not be promoted automatically.
    """
    spec = source_identity_reclassification()
    if source != spec["from_source"]:
        return source
    mapping = {row["code"]: row["to_source"] for row in spec["mappings"]}
    return mapping.get(token)


# ---------------------------------------------------------------------------
# RAW
# ---------------------------------------------------------------------------
def raw_field_sets():
    raw = {}

    # Current collector is raw_push2.json; raw_push2_full.json is retained only as
    # a legacy capture name. Both represent the same stock/get contract.
    raw["东财-push2(stock/get)"] = _field_union_from_captures(
        ("raw_push2.json", "raw_push2_full.json")
    )

    d = loadjson("raw_ulist239.json")
    raw["东财-ulist239(np/get)"] = _field_union_from_captures(("raw_ulist239.json",))

    d = loadjson("raw_tencent.json")
    tencent_records = _stock_records(d)
    n = max(
        (record.get("n_fields") or len(record.get("fields", [])) for record in tencent_records),
        default=0,
    )
    raw["腾讯(qt.gtimg)"] = {f"[{i}]" for i in range(n)}

    d = loadjson("raw_sina.json")
    sina_records = _stock_records(d)
    n = max(
        (record.get("n_fields") or len(record.get("fields", [])) for record in sina_records),
        default=0,
    )
    raw["新浪(hq.sinajs)"] = {f"[{i}]" for i in range(n)}  # 统一为索引命名

    # ZHB 三组 positional [N]（0 索引，与字典表格首列 **[N]** 对齐）
    d = loadjson("raw_zhb.json")
    stocks = _stock_records(d)
    for grp, key in (("tdxstat", "stat"), ("tdxstat2", "stat2"), ("tipinfo", "tipinfo")):
        indexes = [
            len(record[key]) for record in stocks if isinstance(record.get(key), (list, dict))
        ]
        raw[f"ZHB-{grp}"] = {f"[{i}]" for i in range(max(indexes, default=0))}

    # fuyao 叶名末段
    d = loadjson("raw_fuyao.json")
    raw["同花顺-fuyao"] = {x.split(".")[-1] for x in _all_stock_dotted_leaves(d)}

    # 财联社 / 热榜 / push2ex / 市场源 —— 列表项英文键
    d = loadjson("raw_cls.json")
    items = d.get("telegraph", [])
    if items:
        raw["财联社(cls)"] = set().union(*[set(it.keys()) for it in items if isinstance(it, dict)])
    d = loadjson("raw_em_hot.json")
    items = d.get("hot_rank", [])
    if items:
        raw["东财-热榜(em_hot)"] = set().union(
            *[set(it.keys()) for it in items if isinstance(it, dict)]
        )
    d = loadjson("raw_push2ex.json")
    pe = set()
    for k, v in d.items():
        if isinstance(v, list) and v:
            pe |= set().union(*[set(it.keys()) for it in v if isinstance(it, dict)])
    raw["东财-push2ex"] = pe
    d = loadjson("raw_market_sources.json")
    ms = set()
    for k, v in d.items():
        if isinstance(v, list) and v:
            ms |= set().union(*[set(it.keys()) for it in v if isinstance(it, dict)])
        elif isinstance(v, dict):
            ms |= {kk for kk in v.keys()}
    raw["市场源(market_sources)"] = ms
    # market_sources 是聚合容器；将已知 KPL 子接口和 Levistock 的 KPH
    # 天梯分别映射到各自的注册身份，避免“有 raw 文件却显示零字段”。
    kpl_market_fields = set()
    for key in ("kpl_sentiment", "kpl_up_down", "kpl_broken_ratio"):
        value = d.get(key) if isinstance(d, dict) else None
        if isinstance(value, (dict, list)):
            kpl_market_fields |= _leaf_keys(value)
    raw["开盘啦(kpl)"] = kpl_market_fields
    kph_ladder = d.get("kph_limit_ladder") if isinstance(d, dict) else None
    raw["开盘红(Levistock适配)"] = _leaf_keys(kph_ladder)
    # 独立 KPL/KPH 明细适配器保存逐股行；将其全量字段叶键计入双向审计。
    raw["开盘啦(kpl_limit_up_detail)"] = all_stock_leaves(loadjson("raw_kpl.json"))
    raw["开盘红"] = all_stock_leaves(loadjson("raw_kph.json"))
    # 新浪扩展接口保留结构化三表/资金流原始响应；期权字段仍因无合约池暂停。
    d = loadjson("raw_sina_extended.json")
    raw["新浪(扩展API)"] = all_stock_leaves(d) - _CAPTURE_CONTAINER_TOKENS.get(
        "新浪(扩展API)", set()
    )
    d = loadjson("raw_ftshare.json")
    # Phase 3 (2026-09-12): 改用叶键命名空间(与 reg_tokens_for_section 新逻辑对齐),
    # 旧版 set(_leaves(...)) 产出的 dotted 路径(stocks.600xxx.high) 与 registry 命名空间错位,
    # 会令 gap 审计产生假缺口。除个股字段外，FTShare 的 market.* 也是采集器真实保留的
    # 接口响应；将其纳入同一来源集合，防止市场级字段被完整性审计静默漏掉。采集器自加的
    # probe_trading_day 仅是日期元数据，不作为上游字段。
    ftshare_fields = all_stock_leaves(d)
    if isinstance(d.get("stocks"), dict):
        for record in _stock_records(d):
            ftshare_fields |= {key for key in record if key not in _CAPTURE_METADATA_KEYS}
    market_payload = d.get("market") if isinstance(d, dict) else None
    if isinstance(market_payload, dict):
        ftshare_fields |= _leaf_keys(market_payload) - {"probe_trading_day"}
    raw["FTShare"] = ftshare_fields

    # Levistock candidate probes are stored separately from source captures. Keep
    # observed candidate payload fields visible without assigning them to the
    # CLS registry identity or treating the wrapper as an independent anchor.
    candidate_doc = loadjson("levistock_candidate_raw.json")
    candidate_probe = candidate_doc.get("probe") if isinstance(candidate_doc, dict) else None
    if (
        isinstance(candidate_probe, dict)
        and candidate_probe.get("status") == "observed"
        and candidate_probe.get("candidate_id")
    ):
        candidate_id = str(candidate_probe["candidate_id"])
        candidate_family = str(candidate_probe.get("provider_family") or "unknown").strip()
        candidate_label = f"Levistock候选({candidate_id}; 来源族={candidate_family},非独立锚)"
        raw[candidate_label] = _leaf_keys(candidate_doc.get("payload"))

    # datacenter / axdata / em_fund_flow / tdx 双命名源
    d = loadjson("raw_datacenter.json")
    # raw 用 dotted 叶路径(margin_trading.rqjmg)，REG 抽 bare 令牌 → 取末段对齐
    raw["东财-datacenter(英文键)"] = {x.split(".")[-1] for x in _all_stock_dotted_leaves(d)}
    d = loadjson("raw_axdata.json")
    axdata_fields = set()
    for record in _stock_records(d):
        data = record.get("data")
        if isinstance(data, dict):
            axdata_fields.update(k for k in data if re.fullmatch(r"f\d+", k))
    raw["AxData"] = axdata_fields
    d = loadjson("raw_em_fund_flow.json")
    fund_flow_fields = set()
    for record in _stock_records(d):
        data = record.get("data")
        if isinstance(data, dict):
            fund_flow_fields.update(k for k in data if re.fullmatch(r"f\d+", k))
    raw["东财-资金流(em_fund_flow)"] = fund_flow_fields

    # 双命名源（手工复核，不强行 diff）
    d = loadjson("raw_tdx.json")
    tdx = set()
    for stock in _stock_records(d):
        for grp in ("finance_info", "quote_full", "quote_raw"):
            if isinstance(stock.get(grp), dict):
                tdx |= {f"{grp}.{k}" for k in stock[grp].keys()}
    raw["TDX(双命名源)"] = tdx
    d = loadjson("raw_tdx_f10.json")
    raw["TDX-F10(双命名源)"] = set(_all_stock_dotted_leaves(d))

    # ------------------------------------------------------------------
    # V17.1.x (2026-09-06): 以下三源此前被硬编码为 set()（"无 raw 捕获"假象），
    # 实为提取器缺失 —— raw 文件一直都在，只是结构与 dict 型源不同（列表 / 位置串）。
    # 现已按各源真实原生命名提取，审计口径才真正闭合。
    # ------------------------------------------------------------------
    # 巨潮(cninfo)：stocks[code] = list[dict]（互动易问答），取全样本键并集
    d = loadjson("raw_cninfo.json")
    cn = set()
    for _code, _v in (d.get("stocks") or {}).items():
        if isinstance(_v, list):
            for it in _v:
                if isinstance(it, dict):
                    cn |= set(it.keys())
    raw["巨潮(cninfo)"] = cn

    # reports（东财 reportapi）：stocks[code] = list[dict]（研报条目），取全样本键并集
    d = loadjson("raw_reports.json")
    rp = set()
    for _code, _v in (d.get("stocks") or {}).items():
        if isinstance(_v, list):
            for it in _v:
                if isinstance(it, dict):
                    rp |= set(it.keys())
    raw["reports"] = rp

    # em_kline_f61（日K线端点）：stocks[code].klines_all = ["日期,开,收,高,低,量,额,振幅,涨跌幅,涨跌额,换手率"]
    # 逗号分隔**位置串**，字段编号固定 f51..f61（见 §12.3.3）；按实际段数生成 f 编号集。
    d = loadjson("raw_em_kline_f61.json")
    kl = set()
    for _code, _v in (d.get("stocks") or {}).items():
        if isinstance(_v, dict):
            for _row in _v.get("klines_all") or _v.get("klines_tail30") or []:
                if isinstance(_row, str) and _row.strip():
                    _n = len(_row.split(","))
                    kl |= {f"f{51 + i}" for i in range(_n)}
                    break  # 同一源所有行段数一致，取首行即可
    raw["东财-em_kline_f61"] = kl

    # thsdk：TCP 盘后关闸 + 依赖未装时会写 error 字段；无数据则仍为空集（审计标注，不作假闭合）
    d = loadjson("raw_thsdk.json")
    th = set()
    if isinstance(d.get("stocks"), dict) and d["stocks"]:
        for _code, _v in d["stocks"].items():
            if isinstance(_v, dict):
                th |= {k for k in _v.keys()}
    if d.get("error"):
        print(f"   [note] thsdk raw 含 error: {d['error']}  → 依赖已装后需重抓")
    raw["同花顺-thsdk"] = th
    return raw


def _leaves(o, pre=""):
    out = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k in _CAPTURE_METADATA_KEYS:
                continue
            p = f"{pre}.{k}" if pre else k
            if isinstance(v, (dict, list)) and v:
                out += _leaves(v, p)
            else:
                out.append(p)
    elif isinstance(o, list) and o:
        for e in o:
            if isinstance(e, (dict, list)):
                out += _leaves(e, pre)
    return out


def _all_stock_dotted_leaves(document):
    fields = set()
    for record in _stock_records(document):
        fields.update(_leaves(record))
    return fields


_RAW_METADATA_CONTAINERS = _CAPTURE_METADATA_KEYS


def _leaf_keys(o):
    """提取 raw 叶字段，跳过采集器附加的元数据容器。"""
    out = set()
    if isinstance(o, dict):
        for k, v in o.items():
            if k in _RAW_METADATA_CONTAINERS:
                continue
            if isinstance(v, list) and v and not any(isinstance(item, (dict, list)) for item in v):
                out.add(k)
            elif isinstance(v, (dict, list)) and v:
                out |= _leaf_keys(v)
            else:
                out.add(k)
    elif isinstance(o, list) and o:
        for item in o:
            out |= _leaf_keys(item)
    return out


# ---------------------------------------------------------------------------
# Phase 3 (2026-09-12): 根治 snake_case 源的「散文过度抽取」污染。
#
# 旧分支 `re.findall(r"[a-z][a-z0-9_]{2,}", text)` 把章节散文里的端点 URL / 请求参数
# (ut/fs/pz/pn/sort/dpt...) / 函数名(get_*/sc_*/tdx_*) / 跨源 f 编号(f43/f57...) / 乱码碎片
# 当成「本源字段」登记 → 污染 field_registry.json 核心资产(如 fuyao 原 699 令牌仅约 200 真)。
#
# 改为「真值三源并集」(已用 scripts/_diag_extract.py 验证 DROPPED 集合为纯污染):
#   RAW_FIELD_KEYS[src] = 各源 raw_*.json 叶键(跨 docs/field_verification/2026* 全部 dated 目录聚合)
#   _table_codes(stext) = 章节表格首列 / 全列英文代码单元 / 反引号令牌(无中文单元)
#   CANON_ALIASES[src]  = §12.8.12e 规范注册表「各源字段对照」列中本源前缀的别名(仅本源, 严禁跨源串味)
# 三者并集后剔除 f\d+ (f 编号属 push2/ulist/AxData, 永不属这些 snake 源)。
# ---------------------------------------------------------------------------
_RAW_FILE_FOR_SRC = {
    "同花顺-fuyao": ["raw_fuyao.json"],
    "东财-datacenter(英文键)": ["raw_datacenter.json"],
    "东财-push2ex": ["raw_push2ex.json"],
    "东财-热榜(em_hot)": ["raw_em_hot.json"],
    "市场源(market_sources)": ["raw_market_sources.json"],
    "levistock(ftshare)": ["raw_ftshare.json"],
    "财联社(cls)": ["raw_cls.json"],
    "巨潮(cninfo)": ["raw_cninfo.json"],
    "TDX(双命名源)": ["raw_tdx.json", "raw_tdxquant.json"],
    "TDX-F10(双命名源)": ["raw_tdx_f10.json"],
    # V17.3 (2026-09-18): eltdx 适配层源 raw 捕获（raw_eltdx.json, 自 20260915 起常态化采集）。
    # 聚合 leaf keys 供 snake 路径补全；带点 token(quote_snapshot.*/shortline.*) 另经 §12.13.10/§12.13.11
    # 标准契约表由 _table_codes 抽取，与 fuyao snapshot.* 同机制。
    "TDX-eltdx(适配层)": ["raw_eltdx.json"],
    # 新浪三表与个股资金流原始载荷；期权合约路径仍不采集。
    "新浪(扩展API)": ["raw_sina_extended.json"],
    # ZHB 三组已走 positional **[N]** 分支注册；此处挂空 list 以启用 snake 路径的 _table_codes，
    # 使标准契约表的带点 token(stat.*/stat2.*/tipinfo.*) 亦能 registered（与 [N] 并存，不冲突）。
    "ZHB-tdxstat": [],
    "ZHB-tdxstat2": [],
    "ZHB-tipinfo": [],
    # 百度 K 线仅在显式 --only baidu 探针成功时产生 raw。
    "百度(baidu)": ["raw_baidu.json"],
}
# §12.8.12e「各源字段对照」列中各 snake 源的真实前缀(仅本源, 绝不含其他源别名)。
# datacenter/em_hot/market_sources/cls/cninfo/baidu 在 §12.8.12e 无自身价格类别名
# (其真实字段来自 raw + 表格), 故前缀为空列表 —— 这些源切勿串味抓取 开盘啦/东财 等别名。
_CANON_PREFIX_FOR_SRC = {
    "同花顺-fuyao": ["fuyao"],
    "东财-datacenter(英文键)": [],
    "东财-push2ex": ["push2ex"],
    "东财-热榜(em_hot)": [],
    "市场源(market_sources)": [],
    "levistock(ftshare)": ["开盘啦", "开盘红", "KPL", "levistock", "ftshare"],
    "财联社(cls)": [],
    "巨潮(cninfo)": [],
    "百度(baidu)": [],
    "TDX(双命名源)": ["TDX快照", "TDX财务"],
    "新浪(扩展API)": [],
    # TDX-F10 为 F10 报告结构源, §12.8.12e 的 TDX 快照/财务别名属另一语境, 不串入
    "TDX-F10(双命名源)": [],
}

# Capture-envelope / dataset-container keys, not source response fields. Some
# archived probes store these as None or empty containers on failed/empty fetches;
# _leaf_keys intentionally preserves null/empty leaves, so exclude the known
# wrapper names at the source-aware token boundary instead of weakening leaf extraction.
_CAPTURE_CONTAINER_TOKENS = {
    "TDX(双命名源)": {"finance_info", "quote_full"},
    "同花顺-fuyao": {
        "auction_final",
        "balance_q",
        "cashflow_q",
        "fin_indicators",
        "income_a",
        "income_q",
        "short_term_benchmark",
        "valuation",
    },
    "财联社(cls)": {"telegraph"},
    "新浪(扩展API)": {
        "financial_reports",
        "report_list",
        "data",
        "item_title",
        "item_field",
        "item_display_type",
        "item_display",
        "item_precision",
        "item_group_no",
        "item_source",
        "money_flow",
        "newMarketData",
        "marketData",
        "keys",
        "rows",
    },
    "百度(baidu)": {"newMarketData", "marketData", "keys", "rows"},
}


def _agg_raw_leaf_keys(filenames):
    """聚合 docs/field_verification/2026* 下所有 dated 目录的 raw 叶键(真实返回字段)。

    剔除 _RAW_DENY(采集元数据键如 scheme, 非市场字段)后返回。
    """
    ks = set()
    for fn in filenames:
        for f in sorted(glob.glob(os.path.join(ROOT, "docs", "field_verification", "2026*", fn))):
            try:
                d = json.load(io.open(f, encoding="utf-8"))
            except Exception:
                continue
            ks |= _leaf_keys(d)
    return {k for k in ks if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{1,}", k) and k not in _RAW_DENY}


def _build_raw_field_keys():
    return {src: _agg_raw_leaf_keys(fns) for src, fns in _RAW_FILE_FOR_SRC.items()}


# 跨源串味黑名单: 这些 token 是「源名 / 端点名 / 生成区块产物 / 采集元数据」, 绝非某源的真实字段。
# _table_codes 扫描对比矩阵/全量字段表时, 单元格常出现其他源名(如 §12.13.8 含 reportapi、
# §12.15.5 含 push2ex), 或不该登记的代码标识符(§12.10.9/§12.20 的 ft_* 函数、*_cls 类、
# tdxstat/tdxchain 模块、push2delay 端点), 若不拦截会被错误登记到当前继承源的 registry 下。
_DENY_TOKENS = {
    # 各源 slug
    "push2",
    "push2ex",
    "push2_full",
    "ulist",
    "ulist239",
    "ulistnp",
    "tencent",
    "qt",
    "gtimg",
    "sina",
    "sinajs",
    "hq",
    "fuyao",
    "ths",
    "thsdk",
    "sdk",
    "tdx",
    "tdx_f10",
    "tdxquant",
    "tdxhub",
    "tqlex",
    "zhb",
    "cls",
    "baidu",
    "cninfo",
    "axdata",
    "datacenter",
    "slist",
    "clist",
    "em_hot",
    "emappdata",
    "em_fund_flow",
    "em_kline",
    "em_kline_f61",
    "market_sources",
    "levistock",
    "ftshare",
    "kpl",
    "eastmoney",
    "reports",
    "reportapi",
    "webstock",
    "westock",
    "mx_ds",
    # 端点 / 模块名(非字段)
    "push2delay",
    "tdxstat",
    "tdxstat2",
    "tdxchain",
    # ZHB 字段(previx zhb_) 仅在 ZHB 源登记, 不得经对比矩阵串入 fuyao 等源
    "zhb_date",
    "zhb_",
    # 生成区块产物 / 采集元数据(非市场字段)
    "subdict",
    "field_registry",
    "field_matrix",
    "gen_field_dict",
    "scheme",
    "scheme_grounded",
    # 项目模块 / 目录名, 仅经「项目代码正确使用/Bug」表、架构附录串入, 非字段
    "stock_common",
    "field_verification",
    # 实现符号(类/模块/布尔), 仅经对比/函数核实表串入, 非字段
    "true",
    "false",
    "action",
    "controller",
    "detail",
    "index",
    "zscode",
    "zsname",
    "apphis",
    "apphwhq",
    "apphlb",
    "cny",
}
# 前缀黑名单(源字段命名空间 / Python 函数名 / 代码命名空间, 经对比矩阵串入他源时拦截)
_DENY_PREFIXES = ("zhb_", "get_", "sc_", "tdx_", "wenda_", "f10_")
# raw 捕获里的采集元数据键(非市场字段), 仅在聚合 raw 叶键时剔除
_RAW_DENY = {"scheme"}


def _is_denied(tok):
    """token 是否为代码标识符/源名/端点名(非真实市场字段), 须从 registry 抽取中排除。"""
    t = tok.lower()
    if t in _DENY_TOKENS:
        return True
    for p in _DENY_PREFIXES:
        if t.startswith(p):
            return True
    # Python 代码标识符(函数/类/模块名), 非字段:
    #   *_cls        —— 类(如 market_wind_cls / stock_zt_pool_cls)
    #   ft_*         —— ftshare 模块函数(如 ft_get_eastmoney_dapan_flow)
    #   *_ths        —— 同花顺代码标识符(如 stock_hot_rank_ths)
    #   tdx\w+       —— tdx 模块变体(tdxstat/tdxchain...)
    #   内部驼峰 aB   —— 表格里的 GetStockList/HomeDingPan/ZhiShuL2Data 等实现符号
    #                   (真实驼峰字段如 TDX LastClose / fuyao BPS 来自 raw 捕获, 不经表格抽取,
    #                    故此处拒绝表格驼峰不会丢失真实字段)
    if t.endswith("_cls") or t.startswith("ft_") or t.endswith("_ths"):
        return True
    if re.fullmatch(r"tdx\w+", t):
        return True
    # 内部驼峰 aB(用原始大小写判断, 不能在 lower() 后判断): 表格里的 GetStockList/HomeDingPan/
    # ZhiShuL2Data/TagID/Index 等实现符号。真实驼峰字段(LastClose/BPS)来自 raw 捕获, 不经表格抽取。
    if re.search(r"[a-z][A-Z]", tok):
        return True
    return False


def _table_codes(stext):
    """从章节表格抽取真实英文代码: 首列(无中文)/全列无中文单元的字段清单/反引号令牌。

    凡命中 _is_denied(源名/端点名/代码标识符/生成产物/采集元数据)的 token 一律丢弃, 杜绝跨源串味。
    """
    codes = set()
    for line in stext.split("\n"):
        s = line.strip()
        if not s.startswith("|"):
            continue
        if re.match(r"^\|[\s:|-]+\|?\s*$", s):  # 分隔行
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells:
            continue
        # 首列(英文代码)
        first = cells[0]
        if not re.search(r"[一-鿿]", first):
            for tok in re.split(r"[/,\s]+", first):
                tok = tok.strip("`*")
                if _is_denied(tok):
                    continue
                if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{1,}", tok) or re.fullmatch(
                    r"[A-Za-z][A-Za-z0-9_]*\.[A-Za-z0-9_]+", tok
                ):
                    codes.add(tok)
        # 全列: 无中文的「字段清单」单元(端点全量响应字段列等), 逗号/空格分隔 + 反引号
        for cell in cells:
            if re.search(r"[一-鿿]", cell):
                continue
            for bt in re.findall(r"`([A-Za-z][A-Za-z0-9_./]{1,})`", cell):
                if not _is_denied(bt):
                    codes.add(bt)
            for tok in re.split(r"[/,\s;]+", cell):
                tok = tok.strip("`*()")
                if _is_denied(tok):
                    continue
                if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{2,}", tok):
                    codes.add(tok)
    return codes


def _kpl_field_tokens(stext):
    """提取 KPL 文档中字段列，排除接口名和“对应项目字段”列。"""
    tokens = set()
    field_col = None
    for line in stext.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            if re.match(r"^\|[\s:|-]+\|?\s*$", stripped):
                continue
            cells = [cell.strip().strip("`") for cell in stripped.strip("|").split("|")]
            header = any(
                any(mark in cell for mark in ("关键字段", "实测字段", "字段名")) for cell in cells
            )
            if header:
                field_col = next(
                    (
                        i
                        for i, cell in enumerate(cells)
                        if any(mark in cell for mark in ("关键字段", "实测字段", "字段名"))
                    ),
                    None,
                )
                continue
            if cells and any(mark in cells[0].lower() for mark in ("接口", "action")):
                field_col = None
                continue
            if field_col is None or field_col >= len(cells):
                continue
            values = re.findall(
                r"(?<![A-Za-z0-9_])([A-Za-z][A-Za-z0-9_]{1,})(?![A-Za-z0-9_])", cells[field_col]
            )
        else:
            # Socket-only fields are documented as key=value in prose rather than a table.
            values = re.findall(r"(?<![A-Za-z0-9_])([A-Za-z][A-Za-z0-9_]{1,})\s*=", line)
        for value in values:
            is_camel_case = re.search(r"[a-z][A-Z]", value) is not None
            if value.lower() not in _DENY_TOKENS and (is_camel_case or not _is_denied(value)):
                tokens.add(value)
    return tokens


def _build_canon_aliases():
    """扫描 §12.8.12e 规范注册表, 按各源自身前缀抽取其别名令牌。"""
    text = io.open(DICT, encoding="utf-8").read()
    text = re.sub(r"<!-- GEN:.*?-->\n.*?<!-- /GEN:.*?-->\n?", "", text, flags=re.DOTALL)
    canon_text = ""
    for lv, t, s in split_sections(text):
        if "12.8.12e" in t:
            canon_text = s
            break
    out = {}
    for src, prefixes in _CANON_PREFIX_FOR_SRC.items():
        s = set()
        for pre in prefixes:
            pat = re.compile(rf"{re.escape(pre)}\s*`?([A-Za-z][A-Za-z0-9_.]+)`?")
            for m in pat.finditer(canon_text):
                s.add(m.group(1))
        out[src] = s
    return out


RAW_FIELD_KEYS = _build_raw_field_keys()
CANON_ALIASES = _build_canon_aliases()


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# REG（兼容解析器；常规审计优先读取 registry.source_fields）
# ---------------------------------------------------------------------------
def reg_tokens_for_section(src, text):
    toks = set()
    if src == "开盘啦(kpl)":
        return _kpl_field_tokens(text)
    # 沪深交易所(§12.8.17): 官方龙虎榜端点为 pinyin+CamelCase 混合命名, 通用 snake_case
    # 抽取会把端点散文(szse/sse/com/api/market/snap/ann/anotice/dragon_tiger_backup/...)当字段
    # 登记 → 污染 registry 核心资产。显式白名单仅取 §12.8.17 字段表登记的真实源字段
    # (沪市全文以 sse_raw 映射名登记), 严格对齐单源真相。
    if src == "沪深交易所":
        return {"zqdm", "zqjc", "cjje", "plyy", "sse_raw"}
    if src in (
        "东财-push2(stock/get)",
        "东财-ulist239(np/get)",
        "AxData",
        "东财-资金流(em_fund_flow)",
        "东财-em_kline_f61",
        "东财-slist",
        "东财-clist",
    ):
        for m in re.findall(r"\bf(\d+)\b", text):
            toks.add(f"f{m}")
    if src == "腾讯(qt.gtimg)":
        for m in re.findall(r"\[(\d+)\]", text):
            toks.add(f"[{m}]")
        for a, b in re.findall(r"\[(\d+)\]\s*[-—–]\s*\[(\d+)\]", text):
            for i in range(int(a), int(b) + 1):
                toks.add(f"[{i}]")
    if src == "新浪(hq.sinajs)":
        for m in re.findall(r"\[(\d+)\]", text):
            toks.add(f"[{m}]")
        for m in re.findall(r"字段\s*(\d+)", text):
            toks.add(f"[{m}]")
        for a, b in re.findall(r"\[(\d+)\]\s*[-—–]\s*\[(\d+)\]", text):
            for i in range(int(a), int(b) + 1):
                toks.add(f"[{i}]")
    if src.startswith("ZHB-"):
        # ZHB 表格首列加粗索引 **[N]**
        for m in re.findall(r"\*\*\[(\d+)\]\*\*", text):
            toks.add(f"[{m}]")
    # reports（东财 reportapi）：研报条目键为 **camelCase**（stockName / predictThisYearEps ...）。
    # 只从「表格首列」与「反引号」精确抽取，避免把正文英文单词当成已登记字段而制造假闭合。
    if src == "reports":
        for line in text.split("\n"):
            m = re.match(
                r"^\s*\|\s*([A-Za-z][A-Za-z0-9_]{2,}" r"(?:\s*/\s*[A-Za-z][A-Za-z0-9_]{2,})*)\s*\|",
                line,
            )
            if m:
                for name in re.split(r"\s*/\s*", m.group(1)):
                    toks.add(name)
            for m2 in re.findall(r"`([A-Za-z][A-Za-z0-9_]{2,})`", line):
                toks.add(m2)
    # 英文 snake_case 字段（fuyao/datacenter/push2ex/热榜/市场源/levistock/财联社/百度/巨潮/TDX/TDX-F10）
    # —— Phase 3 (2026-09-12) 根治: 不再用 [a-z][a-z0-9_]{2,} 抓取章节散文(会把端点 URL / 请求参数
    # / 函数名 / 跨源 f 编号当字段登记, 污染 registry)。改用「真值三源并集」:
    #   RAW_FIELD_KEYS[src] ∪ _table_codes(text) ∪ CANON_ALIASES[src], 剔除 f\d+。
    # 该并集经 scripts/_diag_extract.py 验证: 当前 registry 减该并集的 DROPPED 集合为纯污染,
    # 不丢任何真实字段(同花顺-thsdk 已退役, 不在 _RAW_FILE_FOR_SRC 内)。
    if src in _RAW_FILE_FOR_SRC:
        toks |= RAW_FIELD_KEYS.get(src, set())
        toks |= _table_codes(text)
        toks |= CANON_ALIASES.get(src, set())
        toks = {t for t in toks if not re.fullmatch(r"f\d+", t)}
        if src == "TDX-eltdx(适配层)":
            # bars.get 的请求参数不是响应字段。
            toks -= {"adjust", "period"}
    toks -= _CAPTURE_CONTAINER_TOKENS.get(src, set())
    return toks


def registered_field_sets():
    text = io.open(DICT, encoding="utf-8").read()
    # Phase 3(2026-09-12): 排除自动生成区块（<!-- GEN:* --> ... <!-- /GEN:* -->）。
    # 这些区块由 field_registry.json / field_matrix 派生，不是手写字段契约，不应反馈进
    # REG 基线 / registry 抽取——否则生成器自身的文件名/标记词（gen_field_dict / subdict /
    # field_registry ...）会被误识为字段。§零·B 区块的 token 均为正文表格的重复项，
    # 排除后 REG 集合与排除前完全一致（已验证：2252 不变）。
    text = re.sub(r"<!-- GEN:.*?-->\n.*?<!-- /GEN:.*?-->\n?", "", text, flags=re.DOTALL)
    secs = split_sections(text)
    reg = defaultdict(set)
    stack = {}  # level -> [sources]; entries are strict Markdown ancestors
    for lv, title, stext in secs:
        for k in list(stack):
            if k >= lv:
                del stack[k]
        matched = section_to_sources(title)
        eff = matched or next((stack[k] for k in sorted(stack, reverse=True) if k < lv), None)
        if eff:
            for src in eff:
                reg[src] |= reg_tokens_for_section(src, stext)
        if matched:
            stack[lv] = matched

    # The historical reference combines several API identities under one label.
    # The migration manifest preserves the pre-migration registry pairs. The
    # legacy Markdown parser is intentionally lossy, so it cannot be used to
    # require every mapped token to still be discoverable in the archive text.
    # It can still detect newly extracted tokens that need explicit review.
    spec = source_identity_reclassification()
    old_source = spec["from_source"]
    if old_source not in reg:
        return reg
    old_tokens = reg.pop(old_source, set())
    mapping_rows = spec["mappings"]
    mapping = {row["code"]: row["to_source"] for row in mapping_rows}
    if len(mapping) != len(mapping_rows):
        raise ValueError("Source identity manifest contains duplicate field tokens")
    mapped_tokens = set(mapping)
    archive_only = set(spec.get("archive_only_tokens", []))
    if mapped_tokens & archive_only:
        raise ValueError(
            "Source identity manifest marks fields as both mapped and archive-only: "
            + ", ".join(sorted(mapped_tokens & archive_only))
        )
    unexpected_tokens = old_tokens - mapped_tokens - archive_only
    if unexpected_tokens:
        raise ValueError(
            "Legacy archive parser found tokens missing from the source identity manifest: "
            + ", ".join(sorted(unexpected_tokens))
        )
    for token, target_source in mapping.items():
        reg[target_source].add(token)
    return reg


def registry_field_sets():
    """(b) 架构根治：从 field_registry.json 单一真相源读取「已登记字段集」。

    与 registered_field_sets() 语义等价（两者源标签 / token 完全一致，已 parity 验证），
    但主路径不再解析 field_dict.md 章节，故不受章节搬家 / SECTION_MAP 硬编码影响。
    若 registry 不可用（文件缺失 / 读取异常 / 空），返回 None 由调用方回退。
    """
    try:
        reg = _fra.fields_by_source()
    except Exception as _e:
        print(f"   [warn] registry_field_sets 读取失败，回退 registered_field_sets: {_e}")
        return None
    if not reg:
        return None
    return reg


# ---------------------------------------------------------------------------
def build_argument_parser():
    parser = argparse.ArgumentParser(description="审计采集字段与字段登记表之间的覆盖差异")
    parser.add_argument(
        "capture_date", nargs="?", default=DEFAULT_CAPTURE_DATE, help="采集目录日期 YYYYMMDD"
    )
    parser.add_argument(
        "output_date", nargs="?", default=DEFAULT_OUTPUT_DATE, help="报告目录日期 YYYYMMDD"
    )
    parser.add_argument(
        "--report-output", help="报告 JSON 完整路径（默认写入 output_date/completeness_audit.json）"
    )
    return parser


def main(argv=None):
    args = build_argument_parser().parse_args(argv)
    global CAP, OUTDIR
    CAP = os.path.join(ROOT, "docs", "field_verification", args.capture_date)
    OUTDIR = os.path.join(ROOT, "docs", "field_verification", args.output_date)
    report_path = args.report_output or os.path.join(OUTDIR, "completeness_audit.json")
    report_path = os.path.abspath(report_path)

    raw = raw_field_sets()
    reg = registry_field_sets()
    if reg is None:
        reg = registered_field_sets()
        print("   [info] reg 数据来源: field_source_reference.md (legacy parser fallback)")
    else:
        print("   [info] reg 数据来源: field_registry.json.source_fields")
    # Keep registry-only sources visible as NO-RawDATA instead of silently omitting
    # them from this capture's completeness report.
    for source in reg:
        raw.setdefault(source, set())
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    report = {}
    print("=" * 82)
    print("主字典字段双向覆盖审计 v4  (所有成功样本并集; REG-only 仅表示本次未观察到)")
    print("=" * 82)
    for src in sorted(raw):
        r = raw[src]
        g = reg.get(src, set())
        differences = compare_field_sets(r, g)
        matched = differences["matched"]
        unregistered_raw = sorted(differences["unregistered_raw"], key=lambda x: (len(x), x))
        registered_not_observed = sorted(
            differences["registered_not_observed"], key=lambda x: (len(x), x)
        )
        if not r:
            flag = "NO-RawDATA"
        elif unregistered_raw and registered_not_observed:
            flag = "BIDIRECTIONAL-GAP"
        elif unregistered_raw:
            flag = "RAW-UNREGISTERED"
        elif registered_not_observed:
            flag = "REGISTERED-UNOBSERVED"
        else:
            flag = "OK"
        report[src] = {
            "raw_count": len(r),
            "reg_count": len(g),
            "matched_count": len(matched),
            "unregistered_raw_count": len(unregistered_raw),
            "unregistered_raw_fields": unregistered_raw,
            "registered_not_observed_count": len(registered_not_observed),
            "registered_not_observed_fields": registered_not_observed,
            # Compatibility aliases: "missing" historically meant RAW − REG.
            "reg_eff_count": len(matched),
            "missing_count": len(unregistered_raw),
            "missing": unregistered_raw,
            "has_raw_data": len(r) > 0,
            "status": flag,
        }
        print(f"\n[{flag}] {src}")
        print(
            f"   raw={len(r)}  reg={len(g)}  matched={len(matched)}  "
            f"raw_only={len(unregistered_raw)}  reg_only={len(registered_not_observed)}"
        )
        for label, fields in (
            ("raw not registered", unregistered_raw),
            ("registered not observed", registered_not_observed if r else []),
        ):
            if fields:
                shown = fields if len(fields) <= 80 else fields[:80] + [f"...+{len(fields)-80}"]
                print(f"   {label}: " + ", ".join(shown))
    with io.open(report_path, "w", encoding="utf-8") as output:
        output.write(json.dumps(report, ensure_ascii=False, indent=2))
    print("\n写出:", report_path)


if __name__ == "__main__":
    main()

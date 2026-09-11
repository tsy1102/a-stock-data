#!/usr/bin/env python3
"""audit_field_completeness.py — 主字典字段完整性审计（v3 修正版）。

RAW = 各源最新 raw 捕获(20260904)用「源原生命名」提取的真实返回字段集。
REG = field_dict.md 各源章节(正文+表格全文)用「同源原生命名」提取的已登记字段集。
GAP = RAW − (REG ∩ RAW宇宙)  —— 源返回了但主字典没登记的字段 = 历史债务。

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
import io, os, re, json, sys
from collections import defaultdict

# (b) 架构根治：优先从 field_registry.json 单一真相源读取「已登记字段集」，
# 使 §零·A 主路径不再依赖 SECTION_MAP / section_to_sources 的字典章节解析（G0 标记脆弱点）。
# registry 缺失或读失败时回退 registered_field_sets()（字典解析）。
import field_registry_api as _fra

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICT = os.path.join(ROOT, "docs", "field_dict.md")
# v3.1 (2026-09-06): CAP/OUT 日期参数化 —— 每次全源采集后必须对「当日 raw」重跑本审计,
# 否则审计永远停在上一次捕获日, 形成 A7(文档代码同真) 口径漂移。
# 用法: python scripts/audit_field_completeness.py [CAP_DATE] [OUT_DATE]
#   例: python scripts/audit_field_completeness.py 20260906   -> 读 20260906 raw, 写 20260906
#   不带参数则沿用历史默认: CAP=20260904, OUT=20260906
_args = [a for a in sys.argv[1:] if not a.startswith("-")]
CAP = os.path.join(ROOT, "docs", "field_verification", _args[0] if _args else "20260904")
OUTDIR = os.path.join(ROOT, "docs", "field_verification", _args[1] if len(_args) > 1 else "20260906")

def loadjson(f):
    return json.load(io.open(os.path.join(CAP, f), encoding="utf-8"))

def first_stock(d):
    return next(iter(d["stocks"].values()))

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
    ("东财-push2(stock/get)", ["12.3.1 单股行情", "12.3.1.1", "12.3.1.2", "12.9.1 push2 stock/get",
                                "12.9.2", "12.3.3 日K线", "12.8.2 东财 push2 历史",
                                "12.8.7 东财 push2 资金流", "12.3.4 资金流四档"]),
    ("东财-资金流(em_fund_flow)", ["12.3.4 资金流四档", "12.8.7 东财 push2 资金流"]),
    ("东财-ulist239(np/get)", ["12.3.2"]),
    ("东财-push2ex", ["12.8.1 东财 push2ex"]),
    ("东财-datacenter(英文键)", ["12.8.3 东财 datacenter"]),
    ("东财-slist", ["12.8.5 东财 slist"]),
    ("东财-clist", ["12.8.6 东财 clist"]),
    ("腾讯(qt.gtimg)", ["12.1 腾讯"]),
    ("新浪(hq.sinajs)", ["12.2 新浪"]),
    ("同花顺-fuyao", ["12.8.12c", "12.8.12e", "12.8.12d"]),
    ("同花顺-thsdk", ["12.8.12b"]),
    ("ZHB-tdxstat", ["tdxstat.cfg"]),
    ("ZHB-tdxstat2", ["tdxstat2.cfg"]),
    ("ZHB-tipinfo", ["tipinfo.dat"]),
    ("财联社(cls)", ["12.8.13 财联社"]),
    ("百度(baidu)", ["12.8.16 百度"]),
    ("沪深交易所", ["12.8.17 沪深交易所"]),
    ("巨潮(cninfo)", ["12.8.15 巨潮"]),
    # V17.1.x 补：reports(东财 reportapi) 与 em_kline_f61(日K线端点) 此前无任何 SECTION_MAP 条目，
    # 导致 reg 恒 0、审计永久报「无 raw 捕获」假象——实为工具缺陷，非未采集。
    ("reports", ["12.8.4 东财 reportapi",
                 "12.8.4.1 东财 reportapi 全量 51 字段表",   # V17.1.x 全量登记
                 "12.9.2 其他接口实测发现"]),   # §12.9.2 含「reportapi 研报（实测 51 字段）」全表
    ("东财-em_kline_f61", ["12.3.3 日K线"]),
    ("东财-热榜(em_hot)", ["em_hot", "热榜"]),
    ("市场源(market_sources)", ["market_sources", "市场源", "市场情绪"]),
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

# ---------------------------------------------------------------------------
# RAW
# ---------------------------------------------------------------------------
def raw_field_sets():
    raw = {}

    d = loadjson("raw_push2_full.json")
    data = first_stock(d)["data"]
    raw["东财-push2(stock/get)"] = {k for k in data.keys() if re.fullmatch(r"f\d+", k)}

    d = loadjson("raw_ulist239.json")
    data = first_stock(d)["data"]
    raw["东财-ulist239(np/get)"] = {k for k in data.keys() if re.fullmatch(r"f\d+", k)}

    d = loadjson("raw_tencent.json")
    n = first_stock(d).get("n_fields") or len(first_stock(d).get("fields", []))
    raw["腾讯(qt.gtimg)"] = {f"[{i}]" for i in range(n)}

    d = loadjson("raw_sina.json")
    n = first_stock(d).get("n_fields") or len(first_stock(d).get("fields", []))
    raw["新浪(hq.sinajs)"] = {f"[{i}]" for i in range(n)}   # 统一为索引命名

    # ZHB 三组 positional [N]（0 索引，与字典表格首列 **[N]** 对齐）
    d = loadjson("raw_zhb.json")
    stocks = d.get("stocks", {})
    if isinstance(stocks, dict) and stocks:
        sk = next(iter(stocks.values()))
        for grp, key in (("tdxstat", "stat"), ("tdxstat2", "stat2"), ("tipinfo", "tipinfo")):
            obj = sk.get(key)
            if isinstance(obj, (list, dict)):
                L = len(obj)
                raw[f"ZHB-{grp}"] = {f"[{i}]" for i in range(L)}

    # fuyao 叶名末段
    d = loadjson("raw_fuyao.json")
    raw["同花顺-fuyao"] = {x.split(".")[-1] for x in _leaves(first_stock(d))}

    # 财联社 / 热榜 / push2ex / 市场源 —— 列表项英文键
    d = loadjson("raw_cls.json")
    items = d.get("telegraph", [])
    if items:
        raw["财联社(cls)"] = set().union(*[set(it.keys()) for it in items if isinstance(it, dict)])
    d = loadjson("raw_em_hot.json")
    items = d.get("hot_rank", [])
    if items:
        raw["东财-热榜(em_hot)"] = set().union(*[set(it.keys()) for it in items if isinstance(it, dict)])
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
    d = loadjson("raw_ftshare.json")
    raw["levistock(ftshare)"] = set(_leaves(first_stock(d)))

    # datacenter / axdata / em_fund_flow / tdx 双命名源
    d = loadjson("raw_datacenter.json")
    # raw 用 dotted 叶路径(margin_trading.rqjmg)，REG 抽 bare 令牌 → 取末段对齐
    raw["东财-datacenter(英文键)"] = {x.split(".")[-1] for x in _leaves(first_stock(d))}
    d = loadjson("raw_axdata.json")
    data = first_stock(d).get("data")
    if isinstance(data, dict):
        raw["AxData"] = {k for k in data.keys() if re.fullmatch(r"f\d+", k)}
    d = loadjson("raw_em_fund_flow.json")
    data = first_stock(d).get("data")
    if isinstance(data, dict):
        raw["东财-资金流(em_fund_flow)"] = {k for k in data.keys() if re.fullmatch(r"f\d+", k)}

    # 双命名源（手工复核，不强行 diff）
    d = loadjson("raw_tdx.json")
    stk = first_stock(d)
    tdx = set()
    for grp in ("finance_info", "quote_full"):
        if isinstance(stk.get(grp), dict):
            tdx |= {f"{grp}.{k}" for k in stk[grp].keys()}
    raw["TDX(双命名源)"] = tdx
    d = loadjson("raw_tdx_f10.json")
    raw["TDX-F10(双命名源)"] = set(_leaves(first_stock(d)))

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
            for _row in (_v.get("klines_all") or _v.get("klines_tail30") or []):
                if isinstance(_row, str) and _row.strip():
                    _n = len(_row.split(","))
                    kl |= {f"f{51 + i}" for i in range(_n)}
                    break   # 同一源所有行段数一致，取首行即可
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
            p = f"{pre}.{k}" if pre else k
            if isinstance(v, (dict, list)) and v:
                out += _leaves(v, p)
            else:
                out.append(p)
    elif isinstance(o, list) and o:
        for e in o[:1]:
            if isinstance(e, (dict, list)):
                out += _leaves(e, pre)
    return out

# ---------------------------------------------------------------------------
# REG（扫描章节全文，按标题层级继承源）
# ---------------------------------------------------------------------------
INDEXED = ("东财-push2(stock/get)", "东财-ulist239(np/get)", "AxData",
           "东财-资金流(em_fund_flow)", "腾讯(qt.gtimg)", "新浪(hq.sinajs)",
           "ZHB-tdxstat", "ZHB-tdxstat2", "ZHB-tipinfo")

def reg_tokens_for_section(src, text):
    toks = set()
    if src in ("东财-push2(stock/get)", "东财-ulist239(np/get)", "AxData", "东财-资金流(em_fund_flow)",
               "东财-em_kline_f61"):
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
            m = re.match(r"^\s*\|\s*([A-Za-z][A-Za-z0-9_]{2,}"
                         r"(?:\s*/\s*[A-Za-z][A-Za-z0-9_]{2,})*)\s*\|", line)
            if m:
                for name in re.split(r"\s*/\s*", m.group(1)):
                    toks.add(name)
            for m2 in re.findall(r"`([A-Za-z][A-Za-z0-9_]{2,})`", line):
                toks.add(m2)
    # 英文 snake_case 字段（fuyao/datacenter/push2ex/热榜/市场源/levistock/财联社/thsdk）
    if src in ("同花顺-fuyao", "同花顺-thsdk", "东财-datacenter(英文键)", "东财-push2ex",
               "东财-热榜(em_hot)", "市场源(market_sources)", "levistock(ftshare)", "财联社(cls)",
               "百度(baidu)", "沪深交易所", "巨潮(cninfo)", "东财-slist", "东财-clist",
               "TDX(双命名源)", "TDX-F10(双命名源)"):
        for m in re.findall(r"[a-z][a-z0-9_]{2,}", text):
            toks.add(m)
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
    stack = {}  # level -> [sources]
    for lv, title, stext in secs:
        for k in list(stack):
            if k > lv:
                del stack[k]
        matched = section_to_sources(title)
        if matched:
            stack[lv] = matched
        eff = None
        for k in sorted(stack, reverse=True):
            if k <= lv:
                eff = stack[k]
                break
        if eff:
            for src in eff:
                reg[src] |= reg_tokens_for_section(src, stext)
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
def main():
    raw = raw_field_sets()
    reg = registry_field_sets()
    if reg is None:
        reg = registered_field_sets()
        print("   [info] reg 数据来源: field_dict.md (registered_field_sets 回退)")
    else:
        print("   [info] reg 数据来源: field_registry.json (单一真相源)")
    os.makedirs(OUTDIR, exist_ok=True)

    report = {}
    print("=" * 82)
    print("主字典字段完整性审计 v3  (REG 按标题层级继承源; ZHB 记号 **[N]**; em_fund_flow 共享 §12.3.4)")
    print("=" * 82)
    for src in sorted(raw):
        r = raw[src]
        g = reg.get(src, set())
        # 索引源：REG 限制在 RAW 宇宙(去跨源叙述污染)
        if src in INDEXED:
            g_eff = g & r
        else:
            g_eff = g & r
        missing = sorted(r - g_eff, key=lambda x: (len(x), x))
        report[src] = {"raw_count": len(r), "reg_count": len(g),
                       "reg_eff_count": len(g_eff), "missing_count": len(missing),
                       "missing": missing, "has_raw_data": len(r) > 0}
        flag = "NO-RawDATA" if not r else ("OK" if not missing else "GAP")
        print(f"\n[{flag}] {src}")
        print(f"   raw={len(r)}  reg(全文)={len(g)}  reg∩raw={len(g_eff)}  missing={len(missing)}")
        if missing:
            shown = missing if len(missing) <= 80 else missing[:80] + [f"...+{len(missing)-80}"]
            print("   missing: " + ", ".join(shown))
    io.open(os.path.join(OUTDIR, "completeness_audit.json"), "w", encoding="utf-8").write(
        json.dumps(report, ensure_ascii=False, indent=2))
    print("\n写出:", os.path.join(OUTDIR, "completeness_audit.json"))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""capture_field_probe.py — 字段实测验证采集脚本(V17.0.24)

固定股票池(docs/field_verification/pool.json)20 股,按天采集各源全字段:
  - ZHB    : full/stat/stat2/tipinfo 全字段(本地解析,零网络)
  - TDX    : 行情快照 + 财务 0x0010(TCP)
  - 腾讯   : qt.gtimg 单股全字段(~90 位,保存原始 split 数组)
  - 东财   : push2 stock/get 全字段(f1-f239,原样保存)
  - fuyao  : 官方 REST 快照/估值/竞价/财务指标/三大报表(V17.0.7 财务TTM族主源)

V17.0.24(2026-09-01) 据主字典最新定案更新:
  - 新增 em_kline_f61: 东财日K(f61 换手率)——CYQ 筹码分布唯一源(字典 V17.0.14)
  - 新增 em_fund_flow: push2delay f137/f140/f143/f146/f149 资金流四档——主力净额
    唯一同口径源(V17.0.16: 主力净=f137, 勿 f137+f140); 走 delay 域不碰 push2 主域
  - collect_fuyao 补 fin_report 三大报表(income/balance/cashflow)——f163 静态PE
    闭环(f160 年报EPS)与 ocf_ttm/revenue_ttm TTM 重建的原始锚数据(V17.0.7)
输出: docs/field_verification/{YYYYMMDD}/raw_{source}.json + meta.json
用法:
  python scripts/capture_field_probe.py                 # 采今天(用现有 ZHB 包)
  python scripts/capture_field_probe.py --date 20260812
  python scripts/capture_field_probe.py --dry-run       # 只检查源可用性,不发请求
  python scripts/capture_field_probe.py --only zhb,tdx,tencent   # 只采指定源
"""
import sys, io, os, json, time, argparse
from datetime import datetime, time as dt_time

for _s in (sys.stdout, sys.stderr):
    if _s is not None and hasattr(_s, "reconfigure"):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from stock_common.sc_utils import em_secid_prefix  # V17.0 S3: 统一 secid 前缀

POOL_PATH = os.path.join(_ROOT, "docs", "field_verification", "pool.json")
OUT_BASE = os.path.join(_ROOT, "docs", "field_verification")

# V17.1.x: 东财 stock/get 全字段(与主字典登记口径对齐 f1-f250, 保证采集不遗漏任何字段)。
# 统一供 push2 / push2_full / ulist239 / em_fund_flow 等东财 f 编号端点复用;
# 主字典 push2/ulist 最高登记到 f250, 故 range(1,251) 即全量。新增 f 编号时只需改此处。
PUSH2_FULL_FIELDS = ",".join(f"f{i}" for i in range(1, 251))


def load_pool() -> list:
    with open(POOL_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["fixed"] + data["dynamic"]


def collect_zhb(pool: list) -> dict:
    """ZHB 全字段(本地,零网络)。"""
    from core.zhb_client import (
        full_market_snapshot, market_stat_snapshot, market_stat2_snapshot,
        get_tip_info, get_stock_name_from_zhb, get_zhb,
    )

    zhb = get_zhb()
    zhb_date = zhb.date if zhb is not None else ""
    full = full_market_snapshot([p["code"] for p in pool]) or {}
    stat = market_stat_snapshot([p["code"] for p in pool]) or {}
    stat2 = market_stat2_snapshot([p["code"] for p in pool]) or {}
    out = {"zhb_date": zhb_date, "stocks": {}}
    for p in pool:
        c = p["code"]
        tip = get_tip_info(c)
        out["stocks"][c] = {
            "name": get_stock_name_from_zhb(c),
            "full": full.get(c),
            "stat": stat.get(c),
            "stat2": stat2.get(c),
            "tipinfo": tip,
        }
    return out


def collect_tdx(pool: list) -> dict:
    """TDX 行情快照 + 财务(失败标的记 None,不中断)。"""
    from core.tdx_client import tdx_get_quote_full, tdx_get_finance_info

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec = {}
        try:
            rec["quote_full"] = tdx_get_quote_full(c)
        except Exception as e:
            rec["quote_full"] = {"__error__": str(e)[:200]}
        try:
            rec["finance_info"] = tdx_get_finance_info(c)
        except Exception as e:
            rec["finance_info"] = {"__error__": str(e)[:200]}
        out["stocks"][c] = rec
    return out


def collect_tencent(pool: list) -> dict:
    """腾讯 qt.gtimg 单股全字段(保存原始 split 数组 + 索引名说明)。"""
    from stock_common import _quick_request

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        # V17.0 审查: 原三元 9 先于 92 → 北交所 920 误判 sh(昨日采集 920118/920508 空数据实证);
        # 92 北交所必须先行(与 em_secid_prefix 同口径)
        market = "bj" if c.startswith(("92", "8", "4", "43", "83", "87")) else (
            "sh" if c.startswith(("6", "9", "5")) else "sz")
        url = f"https://qt.gtimg.cn/q={market}{c}"
        try:
            r = _quick_request(url, timeout=10)
            if r is None:
                out["stocks"][c] = {"__error__": "request failed"}
                continue
            line = r.text.strip()
            if "=" not in line or '"' not in line:
                out["stocks"][c] = {"__error__": f"parse failed: {line[:100]}"}
                continue
            body = line.split('"')[1]
            fields = body.split("~")
            out["stocks"][c] = {
                "url": url,
                "n_fields": len(fields),
                "fields": fields,  # 原始全字段数组,索引对照 docs/verify/tencent_verify.md
            }
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_push2(pool: list) -> dict:
    """东财 push2 stock/get 显式全字段(f1-f250, PUSH2_FULL_FIELDS)。

    V16.4.1 实测: 不指定 fields 时服务端仅返回 58 字段基础子集(缺 f162/f167 等估值字段),
    故此处显式请求全字段, 与主字典登记口径对齐, 采集不遗漏。2026-08-12 实测: push2 半恢复状态——
    连接级风控仍在,首次连接约 50%
    概率 RemoteDisconnected(健康探测单次连接恰好成功)。V16.4.1 防封:
    失败**不再重试**(重试叠加失败连接会触发封禁),失败即记 error。
    V17.0.24: 补域级熔断——首连失败即停止整段 push2 采集(剩余全记
    error 不再发请求)。push2_full 已有 3 连失败熔断, 此处对齐。
    push2 主域数据 push2delay 已镜像覆盖(collect_push2_full 兜底), 损失可接受。
    """
    from stock_common import _quick_request

    out = {"stocks": {}}
    domain_dead = False  # V17.0.24: 域级熔断旗标
    for p in pool:
        c = p["code"]
        if domain_dead:
            out["stocks"][c] = {"__error__": "push2 domain circuit-broken (no retry)"}
            continue
        secid = em_secid_prefix(c) + c  # V17.0 S3: 统一(修复 92 北交所误判 1.)
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        try:
            r = _quick_request(
                url,
                params={"secid": secid, "fltt": "2", "invt": "2", "fields": PUSH2_FULL_FIELDS,
                        "ut": "fa5fd1943c7b386f172d6893dbfba10b"},
                headers={"Referer": "https://quote.eastmoney.com/"},
                timeout=10,
            )
        except Exception:
            r = None
        if r is None:
            out["stocks"][c] = {"__error__": "request failed (no retry)"}
            domain_dead = True  # V17.0.24: 失败即熔断整域, 不再连打
            continue
        data = (r.json() or {}).get("data") or {}
        out["stocks"][c] = {"secid": secid, "n_fields": len(data), "data": data}
    return out


def collect_push2_full(pool: list) -> dict:
    """东财 push2 stock/get **显式全字段**(f1-f250)。

    V16.4.1: 原 collect_push2 未指定 fields → 服务端仅返回 58 字段基础子集
    (无 f162/f167 等估值字段)。字典 §12.9 破解为 f1~f250 全字段——
    此处显式请求全字段。失败重试一次(半恢复期连接级拒绝)。
    2026-08-12 实测: push2 半恢复期间歇全拒 → 自动切 push2delay 镜像域
    (字段同构, 字典 §12.15.5; 独立风控面, 1.0rps)。
    V16.4.1 防封(2026-08-12 封禁复盘): 失败**不再重试**——失败连接本身
    积累服务器侧风控(当日 ~300 次连接尝试含半数失败 → 触发连接级封禁)。
    每只: push2 一次 → 失败直接切 push2delay 一次; 连续 3 只 push2 失败
    → 剩余股票全部走 push2delay(域级熔断, 不继续捅 push2)。
    """
    from stock_common import _quick_request

    fields = PUSH2_FULL_FIELDS  # f1-f250 显式全字段(与主字典口径对齐)
    push2_fail_streak = 0
    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        secid = em_secid_prefix(c) + c  # V17.0 S3: 统一(修复 92 北交所误判 1.)
        r = None
        used_host = ""
        if push2_fail_streak < 3:
            try:
                r = _quick_request(
                    "https://push2.eastmoney.com/api/qt/stock/get",
                    params={"secid": secid, "fltt": "2", "invt": "2", "fields": fields,
                            "ut": "fa5fd1943c7b386f172d6893dbfba10b"},
                    headers={"Referer": "https://quote.eastmoney.com/"},
                    timeout=10,
                )
                if r is not None:
                    used_host = "push2"
                    push2_fail_streak = 0
                else:
                    push2_fail_streak += 1
            except Exception:
                push2_fail_streak += 1
                r = None
        if r is None:
            try:
                r = _quick_request(
                    "https://push2delay.eastmoney.com/api/qt/stock/get",
                    params={"secid": secid, "fltt": "2", "invt": "2", "fields": fields,
                            "ut": "fa5fd1943c7b386f172d6893dbfba10b"},
                    headers={"Referer": "https://quote.eastmoney.com/"},
                    timeout=10,
                )
                if r is not None:
                    used_host = "push2delay"
            except Exception:
                r = None
        if r is None:
            out["stocks"][c] = {"__error__": "request failed (push2+delay, no retry)"}
            continue
        data = (r.json() or {}).get("data") or {}
        out["stocks"][c] = {"secid": secid, "host": used_host, "n_fields": len(data), "data": data}
    return out


def collect_sina(pool: list) -> dict:
    """新浪行情 hq.sinajs 全字段(需 Referer)。"""
    from stock_common import _quick_request, UA

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        # M13 修复：原来只把 "6" 判沪市，漏 "5"(沪ETF)/"9"(沪B) → 新浪源误判 sz 污染跨源对照。
        # 与 collect_tencent(:97) 同口径：92/8/4/43/83/87→bj，6/9/5→sh，其余→sz。
        pre = "bj" if c.startswith(("92", "8", "4", "43", "83", "87")) else (
            "sh" if c.startswith(("6", "9", "5")) else "sz")
        try:
            r = _quick_request(
                f"https://hq.sinajs.cn/list={pre}{c}",
                headers={"Referer": "https://finance.sina.com.cn/", "User-Agent": UA},
                timeout=8,
            )
            if r is None:
                out["stocks"][c] = {"__error__": "request failed"}
                continue
            text = r.text.strip()
            if "=" not in text:
                out["stocks"][c] = {"__error__": f"parse failed: {text[:80]}"}
                continue
            payload = text.split('"')[1] if '"' in text else ""
            fields = payload.split(",")
            out["stocks"][c] = {"n_fields": len(fields), "fields": fields}
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_axdata(pool: list) -> dict:
    """AxData 短线指标 34 字段(零网络,直读项目 zhb.zip,字典 §12.12.1)。"""
    from stock_common import get_shortline_indicators

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        try:
            rec = get_shortline_indicators(c) or {}
            out["stocks"][c] = {"n_fields": len(rec), "data": rec}
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_market_sources(pool: list) -> dict:
    """市场级源(一次性): 财联社情绪/涨停天梯/盘口异动 + KPL + 板块轮动 + 龙虎榜。"""
    out = {}
    try:
        from stock_common import get_cls_market_emotion, get_kph_limit_ladder, get_stock_changes
        out["cls_market_emotion"] = get_cls_market_emotion()
        out["kph_limit_ladder"] = get_kph_limit_ladder()
        out["stock_changes_8201"] = get_stock_changes("8201")
    except Exception as e:
        out["levistock_error"] = str(e)[:200]
    try:
        from stock_common import (get_kpl_market_sentiment, get_kpl_limit_up_detail,
                                  get_kpl_broken_ratio, get_kpl_up_down)
        out["kpl_sentiment"] = get_kpl_market_sentiment()
        out["kpl_up_down"] = get_kpl_up_down()
        out["kpl_limit_up_detail"] = get_kpl_limit_up_detail()
        out["kpl_broken_ratio"] = get_kpl_broken_ratio()
    except Exception as e:
        out["kpl_error"] = str(e)[:200]
    try:
        from stock_common import get_plate_rotation_matrix, get_plate_rotation_top
        out["plate_rotation_matrix"] = get_plate_rotation_matrix(source="kaipan", days=20, top_n=30)
        out["plate_rotation_top"] = get_plate_rotation_top()
    except Exception as e:
        out["plate_rot_error"] = str(e)[:200]
    try:
        from stock_common import eastmoney_datacenter
        r = eastmoney_datacenter(
            "RPT_DAILYBILLBOARD_DETAILSNEW",
            {"SECURITY_CODE": "1"}, page_size=50,
        )
        out["dragon_tiger_today"] = r
    except Exception as e:
        out["dragon_tiger_error"] = str(e)[:200]
    return out


def collect_tdx_f10(pool: list) -> dict:
    """TDX F10 财务九件套补充: 财务分析/股本/分红(TCP,免费)。"""
    from core.tdx_client import tdx_get_financial_analysis, tdx_get_share_capital, tdx_get_dividend_history

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec = {}
        for name, fn in [("financial_analysis", tdx_get_financial_analysis),
                         ("share_capital", tdx_get_share_capital),
                         ("dividend_history", tdx_get_dividend_history)]:
            try:
                rec[name] = fn(c)
            except Exception as e:
                rec[name] = {"__error__": str(e)[:150]}
        out["stocks"][c] = rec
    return out


def collect_thsdk(pool: list) -> dict:
    """同花顺 SDK 实时快照(正式账号;非交易时段服务器拒绝,容错记录)。

    V17.2.0: thsdk TCP 网关已从项目中完全移除(用户场景为盘后/盘前运行,
    thsdk 仅盘中可用、对自己无价值)。此采集器保留为占位,返回已移除标记。
    """
    return {"stocks": {}, "error": "thsdk TCP 网关已于 V17.2.0 移除"}


def _last_completed_trading_day():
    """最近已完成交易日(周末回退周五;节假日不识别——探针用途可接受)。"""
    import datetime

    d = datetime.date.today()
    while d.weekday() >= 5:
        d -= datetime.timedelta(days=1)
    return d


def collect_fuyao(pool: list) -> dict:
    """fuyao 官方 REST 全景采集（V17.0.5 新源——字典 §12.8.12c，全量契约见 verify/fuyao_api_full.md）。

    个股级: 行情快照 / 估值(ps_ttm·pcf_ttm 新维度) / 集合竞价终态 /
            五类财务指标(ROE·扣非ROE·ROA 官方口径——tx65/tx66 对撞终判源)
    市场级: 短线风向标基准 / 涨跌停炸板池(date_ms 任意交易日回查) / 异动原因 / 龙虎榜
    无 Key 时自动禁用(meta 标记 no_key)；~35 请求 @2rps(sc_network 域限流)。
    """
    from stock_common import (
        get_fuyao_snapshot, get_fuyao_valuation, get_fuyao_fin_indicators,
        get_fuyao_auction_snapshot, get_fuyao_auction_benchmark,
        get_fuyao_limit_pool, get_fuyao_anomaly, get_fuyao_dragon_tiger,
        get_fuyao_hot_list, is_fuyao_enabled,
    )

    out: dict = {"stocks": {}, "market": {}}
    if not is_fuyao_enabled():
        out["error"] = "no_key_disabled"
        return out
    codes = [p["code"] for p in pool]
    td = _last_completed_trading_day()
    date_ms = int(datetime.combine(td, dt_time()).timestamp() * 1000)
    out["probe_trading_day"] = td.isoformat()
    out["date_ms"] = date_ms

    snap = {r.get("ticker"): r for r in (get_fuyao_snapshot(codes) or [])}
    val = {r.get("ticker"): r for r in (get_fuyao_valuation(codes) or [])}
    auction = {r.get("ticker"): r for r in (get_fuyao_auction_snapshot(codes, stage="final") or [])}
    # V17.0.24: 三大报表(近 8 期 quarterly + 年报 annual)——财务 TTM 族主源原始锚:
    # f163 静态PE=现价÷f160(年报EPS) 闭环验证 + ocf_ttm/revenue_ttm TTM 重建(R_YTD+FY−H1)
    finrep = {}
    try:
        from stock_common.sc_fuyao import get_fuyao_financials as _gff
        for p in pool:
            c = p["code"]
            finrep[c] = {
                "income_q": _gff("income", c, limit=8, period="quarterly") or [],
                "balance_q": _gff("balance", c, limit=8, period="quarterly") or [],
                "cashflow_q": _gff("cashflow", c, limit=8, period="quarterly") or [],
                "income_a": _gff("income", c, limit=3, period="annual") or [],
            }
    except Exception as _e:
        finrep["__error__"] = str(_e)[:200]
    for p in pool:
        c = p["code"]
        ind = None
        used_report = None
        for rpt in (_last_completed_trading_day().strftime("%Y") + "-2",
                    _last_completed_trading_day().strftime("%Y") + "-1"):
            ind = get_fuyao_fin_indicators(c, rpt)
            if ind:
                used_report = rpt
                break
        out["stocks"][c] = {
            "snapshot": snap.get(c),
            "valuation": val.get(c),
            "auction_final": auction.get(c),
            "fin_indicators": ind,
            "fin_report": used_report,
            # V17.0.24: 三大报表原始数据(TTM 重建/静态PE 闭环锚)
            "financials": finrep.get(c) if isinstance(finrep.get(c), dict) else None,
        }

    mkt = out["market"]
    bench = get_fuyao_auction_benchmark(td.isoformat())
    mkt["short_term_benchmark"] = bench[:80] if isinstance(bench, list) else bench

    # ── 中报(yyyy-2)就绪自动探测——tx[65]=扣非加权ROE(TTM) 的 L1 终判数据源 ──
    # 哨兵: 首只股探 2026-2；上游入库滞后(披露日≠入库日, code=5003)时跳过全量拉取省配额
    year = td.strftime("%Y")
    sentinel = get_fuyao_fin_indicators(codes[0], year + "-2")
    mkt["h1_indicators_ready"] = bool(sentinel)
    mkt["h1_indicators"] = {}
    if sentinel:
        for c in codes:
            ind = get_fuyao_fin_indicators(c, year + "-2") or {}
            p = ind.get("profitability") or {}
            if p:
                mkt["h1_indicators"][c] = {
                    "ded_weighted_roe": p.get("index_deduct_weighted_avg_roe"),
                    "weighted_roe": p.get("index_weighted_avg_roe"),
                    "roa": p.get("total_assets_net_ratio"),
                }
        print(f"  ⭐ 中报指标已入库({len(mkt['h1_indicators'])} 只)——tx65/tx66 L1 终判条件达成")

    for kind in ("up", "down", "break"):
        pd_ = get_fuyao_limit_pool(kind, page=1, size=200, date_ms=date_ms)
        items = (pd_ or {}).get("item") or []
        mkt[f"limit_{kind}_pool"] = {
            "total": ((pd_ or {}).get("pagination") or {}).get("total"),
            "count_captured": len(items),
            "item": items,
        }
    mkt["anomaly_list"] = (get_fuyao_anomaly() or [])[:60]
    mkt["dragon_tiger"] = (get_fuyao_dragon_tiger(td.isoformat()) or [])[:60]
    mkt["hot_list_hour"] = (get_fuyao_hot_list("hour") or [])[:50]
    return out


def collect_ftshare(pool: list) -> dict:
    """FTShare MCP 全景采集（V17.0.7 新源——字典 §12.20，全字段镜像见 verify/ftshare_fields_mirror.md）。

    个股级: 千股千评四族（评分日序列/参与意愿/关注度/机构参与度）/
            董监高变动明细(26字段) / 商誉个股明细
    市场级: 大盘资金流 / DAEC 涨跌分布聚合 / 停牌列表 /
            昨日涨停池(炸板回封时间数组) / 限售解禁按日 / 股权质押汇总
    ~126 请求 @2rps(sc_network 域限流 market.ft.tech)；会话自动续期(TTL≈2h)。
    """
    from stock_common.sc_ftshare import (
        is_ftshare_enabled, get_ft_comment_score_series, get_ft_comment_desire,
        get_ft_comment_focus, get_ft_comment_org_participate,
        get_ft_ggmx_changes, get_ft_goodwill_stock_detail,
        get_ft_pledge_summary, get_ft_dapan_flow, get_ft_market_snapshot,
        get_ft_suspension_list, get_ft_limit_up_pool_yesterday,
        get_ft_unlock_by_date,
    )

    out: dict = {"stocks": {}, "market": {}}
    if not is_ftshare_enabled():
        out["error"] = "disabled"
        return out

    for p in pool:
        c = p["code"]
        # V17.1.x: 去截断, 采全集(评分日序列/董监高变动/商誉明细全量), 方法轮与对撞铁律需完整经验。
        out["stocks"][c] = {
            "comment_score": get_ft_comment_score_series(c) or [],
            "comment_desire": get_ft_comment_desire(c),
            "comment_focus": get_ft_comment_focus(c),
            "comment_org": get_ft_comment_org_participate(c),
            "ggmx": get_ft_ggmx_changes(c) or [],
            "goodwill_detail": get_ft_goodwill_stock_detail(c) or [],
        }

    mkt = out["market"]
    mkt["dapan_flow"] = get_ft_dapan_flow()
    mkt["market_snapshot"] = get_ft_market_snapshot()
    mkt["suspension_list"] = (get_ft_suspension_list() or [])[:50]
    mkt["limit_up_pool_yesterday"] = get_ft_limit_up_pool_yesterday()
    td = _last_completed_trading_day().strftime("%Y%m%d")
    mkt["unlock_by_date"] = (get_ft_unlock_by_date(td) or [])[:80]
    mkt["pledge_summary"] = get_ft_pledge_summary()
    mkt["probe_trading_day"] = td
    return out


def collect_em_kline_f61(pool: list) -> dict:
    """东财日K线(**push2his** 域)——f61 换手率为 CYQ 筹码分布唯一源(字典 V17.0.14)。

    TDX 0x0010 日K 与腾讯 ifzq 均无换手率 → 仅东财日K有。
    🔴 域选择实测(2026-09-01): push2delay/push2 主域 kline dktotal=0 空返回(延时镜像
    无历史窗口); **push2his 才有全窗口**(dktotal=5995, 150 根含今日)——与生产
    `get_cyq_distribution` 的 `_em_fflow_request(prefer_his=True)` 同源。
    klines 结构: "date,open,close,high,low,volume,amount,amplitude,pct,chg,turnover"
    其中 turnover=f61 换手率; fqt=0 不复权(成本分布口径)。
    """
    from stock_common import _quick_request

    out = {"stocks": {}}
    domain_dead = False  # V17.0.24: 域级熔断(push2his 与 push2 同风控面, 3 连败即停)
    fail_streak = 0
    for p in pool:
        c = p["code"]
        if domain_dead:
            out["stocks"][c] = {"__error__": "push2his circuit-broken (family risk-control)"}
            continue
        secid = em_secid_prefix(c) + c
        try:
            r = _quick_request(
                "https://push2his.eastmoney.com/api/qt/stock/kline/get",
                params={
                    "secid": secid, "fields1": "f1,f2,f3,f4,f5,f6",
                    "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                    "klt": "101", "fqt": "0", "end": "20500101", "lmt": "150",
                    "ut": "b2884a393a59ad64002292a3e90d46a5",
                },
                headers={"Referer": "https://quote.eastmoney.com/"},
                timeout=15,
            )
            if r is None:
                out["stocks"][c] = {"__error__": "request failed"}
                fail_streak += 1
                if fail_streak >= 3:
                    domain_dead = True
                continue
            data = (r.json() or {}).get("data") or {}
            klines = data.get("klines") or []
            fail_streak = 0
            out["stocks"][c] = {
                "secid": secid, "dktotal": data.get("dktotal"), "n_klines": len(klines),
                "klines_tail30": klines[-30:],   # 近 30 根精简
                "klines_all": klines if len(klines) <= 150 else klines[:150],
            }
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_em_fund_flow(pool: list) -> dict:
    """东财资金流四档(push2delay 域)——f137 主力净额唯一同口径源(V17.0.16)。

    stock/get: f135/136/137=主力(超大+大单)、f138/139/140=超大单、f141/142/143=大单、
    f144/145/146=中单、f149=小单净。铁证 f137=f140+f143(169/169); ulist f62==f137(96.6%)。
    全走 push2delay 镜像域(独立风控 1.0rps), 不碰 push2 主域。
    """
    from stock_common import _quick_request

    # V17.1.x: 补全 f147/f148(散单买/卖额, 主字典 §12.3.4 已登记)——原列表漏此二项致采集缺失。
    ff_fields = ",".join(["f135", "f136", "f137",
                          "f138", "f139", "f140",
                          "f141", "f142", "f143",
                          "f144", "f145", "f146",
                          "f147", "f148",   # 散单(第五档)买/卖额
                          "f149"])
    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        secid = em_secid_prefix(c) + c
        try:
            r = _quick_request(
                "https://push2delay.eastmoney.com/api/qt/stock/get",
                params={"secid": secid, "fltt": "2", "invt": "2", "fields": ff_fields,
                        "ut": "fa5fd1943c7b386f172d6893dbfba10b"},
                headers={"Referer": "https://quote.eastmoney.com/"},
                timeout=10,
            )
            if r is None:
                out["stocks"][c] = {"__error__": "request failed"}
                continue
            data = (r.json() or {}).get("data") or {}
            out["stocks"][c] = {"secid": secid, "n_fields": len(data), "data": data}
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_ulist239(pool: list) -> dict:
    """东财 push2delay ulist.np 批量全字段(1 次请求 20 只,字典 §12.9 ulist 239 字段)。"""
    from stock_common import _quick_request

    def _mkt(c):
        if c.startswith(("92", "8", "4", "43", "83", "87")):
            return "0."  # 北交所(920 等)必须先判——"9" 前缀会被沪市分支吃掉(V16.4.1 bug 修复)
        if c.startswith(("6", "5", "9")):
            return "1."
        return "0."

    secids = ",".join(_mkt(p["code"]) + p["code"] for p in pool)
    try:
        r = _quick_request(
            "https://push2delay.eastmoney.com/api/qt/ulist.np/get",
            params={"fltt": "2", "invt": "2", "secids": secids,
                    "fields": PUSH2_FULL_FIELDS},
            headers={"Referer": "https://quote.eastmoney.com/"},
            timeout=15,
        )
        if r is None:
            return {"__error__": "request failed"}
        diff = (r.json() or {}).get("data", {}).get("diff") or []
        out = {"stocks": {}}
        for item in diff:
            code = str(item.get("f12", ""))
            if code:
                out["stocks"][code] = {"n_fields": len(item), "data": item}
        return out
    except Exception as e:
        return {"__error__": str(e)[:200]}


def collect_push2ex(pool: list) -> dict:
    """push2ex 涨停/跌停/炸板池(市场级,字典 §12.9.2)。"""
    out = {}
    try:
        from stock_common import get_limit_up_pool, get_limit_down_pool, get_limit_broken_pool
        out["limit_up_pool"] = get_limit_up_pool()
        out["limit_down_pool"] = get_limit_down_pool()
        out["limit_broken_pool"] = get_limit_broken_pool()
    except Exception as e:
        out["error"] = str(e)[:200]
    return out


def collect_em_hot(pool: list) -> dict:
    """东财人气榜(市场级,emappdata 域)。"""
    try:
        from stock_common import em_hot_rank
        return {"hot_rank": em_hot_rank(top=50)}
    except Exception as e:
        return {"error": str(e)[:200]}


def collect_cls(pool: list) -> dict:
    """财联社快讯(市场级)。"""
    try:
        from stock_common import cls_telegraph
        return {"telegraph": cls_telegraph(page_size=50)}
    except Exception as e:
        return {"error": str(e)[:200]}


def collect_datacenter(pool: list) -> dict:
    """东财 datacenter 个股级: 两融/北向/解禁(每只 3 请求,1.0rps)。"""
    from stock_common import get_margin_trading, get_northbound_hold, get_lockup_expiry

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec = {}
        for name, fn in [("margin_trading", get_margin_trading),
                         ("northbound_hold", get_northbound_hold),
                         ("lockup_expiry", get_lockup_expiry)]:
            try:
                v = fn(c)
                rec[name] = v if isinstance(v, (list, dict)) else {"value": v}
            except Exception as e:
                rec[name] = {"__error__": str(e)[:150]}
        out["stocks"][c] = rec
    return out


def collect_tdx_f10_more(pool: list) -> dict:
    """TDX F10 补充: 股东研究/公司新闻/异动提醒(TCP 免费)。"""
    from core.tdx_client import tdx_get_shareholder_research, tdx_get_company_news_f10, tdx_get_latest_reminders

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec = {}
        for name, fn in [("shareholder_research", tdx_get_shareholder_research),
                         ("company_news", lambda x: tdx_get_company_news_f10(x, count=10)),
                         ("reminders", tdx_get_latest_reminders)]:
            try:
                rec[name] = fn(c)
            except Exception as e:
                rec[name] = {"__error__": str(e)[:150]}
        out["stocks"][c] = rec
    return out


def collect_cninfo(pool: list) -> dict:
    """巨潮互动易(irm.cninfo,3rps;全 20 只)。"""
    from stock_common import cninfo_irm

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        try:
            out["stocks"][c] = cninfo_irm(c, page_size=10)
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:150]}
    return out


def collect_reports(pool: list) -> dict:
    """东财研报 reportapi(全 20 只,1.0rps)。"""
    from stock_common import get_reports

    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        try:
            out["stocks"][c] = get_reports(c, max_pages=1)
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:150]}
    return out


def dry_run(pool: list) -> None:
    print(f"[dry-run] pool={len(pool)} 只")
    from core.zhb_client import get_zhb, is_data_fresh
    zhb = get_zhb()
    print(f"  ZHB     : date={zhb.date if zhb else 'N/A'} fresh={is_data_fresh()}")
    from core.tdx_client import _check_tdx
    print(f"  TDX     : {_check_tdx()}")
    from stock_common import _quick_request
    r = _quick_request("https://qt.gtimg.cn/q=sh600519", timeout=8)
    print(f"  腾讯    : {'OK' if r is not None else 'FAIL'}")
    r = _quick_request("https://push2.eastmoney.com/api/qt/stock/get",
                       params={"secid": "1.600519", "fltt": "2", "invt": "2"},
                       headers={"Referer": "https://quote.eastmoney.com/"}, timeout=8)
    print(f"  push2   : {'OK' if r is not None else 'FAIL'}")


def main() -> None:
    ap = argparse.ArgumentParser(description="字段验证采集")
    ap.add_argument("--date", default=datetime.now().strftime("%Y%m%d"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", default="", help="只采指定源(逗号分隔: zhb,tdx,tencent,push2)")
    args = ap.parse_args()

    pool = load_pool()
    if args.dry_run:
        dry_run(pool)
        return

    t0 = time.time()
    print(f"▶ 采集开始: {args.date} | 股票 {len(pool)} 只 | 源: ZHB/TDX/腾讯/push2", flush=True)
    meta = {"date": args.date, "start": time.strftime("%Y-%m-%d %H:%M:%S"), "sources": {}}

    collectors = {
        "zhb": collect_zhb,
        "tdx": collect_tdx,
        "tencent": collect_tencent,
        "push2": collect_push2,
        "push2_full": collect_push2_full,   # V16.4.1: f1-f250 显式全字段
        "sina": collect_sina,               # V16.4.1: 新浪行情全字段
        "axdata": collect_axdata,           # V16.4.1: 短线指标 34 字段(零网络)
        "market_sources": collect_market_sources,  # V16.4.1: 财联社/KPL/板块轮动/龙虎榜
        "tdx_f10": collect_tdx_f10,         # V16.4.1: F10 财务/股本/分红
        "thsdk": collect_thsdk,             # V17.2.0: 同花顺 SDK TCP 网关已移除(占位返回移除标记)
        "fuyao": collect_fuyao,             # V17.0.5: fuyao 官方 REST(盘后可用——竞价/池/财务指标/估值 PS·PCF); V17.0.24 补三大报表
        "em_kline_f61": collect_em_kline_f61,   # V17.0.24: 东财日K f61 换手率(CYQ 唯一源, delay 域)
        "em_fund_flow": collect_em_fund_flow,   # V17.0.24: 资金流四档 f137 族(主力净唯一同口径源, delay 域)
        "ulist239": collect_ulist239,       # V16.4.1: push2delay ulist 239 字段(批量)
        "push2ex": collect_push2ex,         # V16.4.1: 涨停/跌停/炸板池
        "em_hot": collect_em_hot,           # V16.4.1: 人气榜
        "cls": collect_cls,                 # V16.4.1: 财联社快讯
        "datacenter": collect_datacenter,   # V16.4.1: 两融/北向/解禁
        "tdx_f10_more": collect_tdx_f10_more,  # V16.4.1: 股东/新闻/提醒
        "cninfo": collect_cninfo,           # V16.4.1: 巨潮互动易
        "reports": collect_reports,         # V16.4.1: 研报
        "ftshare": collect_ftshare,         # V17.0.7: FTShare MCP(千股千评/董监高/商誉/质押/解禁/打板池)
    }
    if args.only:
        collectors = {k: v for k, v in collectors.items() if k in [s.strip() for s in args.only.split(",")]}
    out_dir = os.path.join(OUT_BASE, args.date)
    os.makedirs(out_dir, exist_ok=True)

    for name, fn in collectors.items():
        try:
            t1 = time.time()
            data = fn(pool)
            path = os.path.join(out_dir, f"raw_{name}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1, default=str)
            meta["sources"][name] = {"ok": True, "secs": round(time.time() - t1, 1), "file": path}
            print(f"  ✔ {name}: {meta['sources'][name]['secs']}s", flush=True)
        except Exception as e:
            meta["sources"][name] = {"ok": False, "error": str(e)[:300]}
            print(f"  ✖ {name}: {e}", flush=True)

    meta["end"] = time.strftime("%Y-%m-%d %H:%M:%S")
    meta["total_secs"] = round(time.time() - t0, 1)
    # V17.0.10: 记录 ZHB 数据日期(T-1 规则)——对撞破解必须先核对此字段再定对撞报告日期
    try:
        meta["zhb_data_date"] = json.load(
            open(os.path.join(out_dir, "raw_zhb.json"), encoding="utf-8")
        ).get("zhb_date", "")
    except Exception:
        meta["zhb_data_date"] = ""
    with open(os.path.join(out_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(f"✔ 完成: {out_dir} | 总耗时 {meta['total_secs']}s | ZHB={meta.get('zhb_data_date')}", flush=True)


if __name__ == "__main__":
    main()

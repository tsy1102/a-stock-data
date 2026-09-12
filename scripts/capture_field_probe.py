#!/usr/bin/env python3
"""capture_field_probe.py — 字段实测验证采集脚本(V17.2.12 主字典对齐)

固定股票池(docs/field_verification/pool.json)20 股,按天采集各源全字段。
采集器集合与主字典 field_registry.json(23 源)逐源映射(V17.2.12 对齐):

  已采集(可用 producer):
    ZHB / TDX / 腾讯(qt.gtimg) / 东财-push2(+push2_full 全字段变体) / 新浪 / axdata(短线指标)
    / 市场源(market_sources) / TDX-F10 / 同花顺-fuyao / 东财-em_kline_f61 / 东财-资金流(em_fund_flow)
    / 东财-ulist239 / 东财-push2ex / 东财-热榜(em_hot) / 财联社(cls) / 东财-datacenter / 巨潮(cninfo)
    / 东财-reports / levistock(ftshare) / TDX-F10-more
  已登记且已接入真实 producer(写 raw 文件, 计入异常清单判定):
    东财-clist(§12.8.6, V17.2.13)/ 东财-slist(§12.8.5, V17.2.13)
  已登记但暂无 producer(标记 unwired, 写 meta 不进异常清单):
    沪深交易所(§12.8.17, 龙虎榜已被 fuyao 覆盖; 官方行情/公告端点待 probing)
  已废弃不采集(标记 deprecated):
    百度(baidu, §12.8.16 ❌→⏸️, PAE 失效改走 TDX 适配器)
  真实可用, 已于 V17.2.13 补登 registry(此前 SECTION_MAP 漏登记, 属治理抽取债):
    TDX(行情+F10) / axdata / push2_full
  已从项目彻底移除, 采集器同步删除(§12.8.12b 章节保留为退役追溯):
    同花顺-thsdk(V17.0.29 移除 TCP 网关)

V17.0.24(2026-09-01) 据主字典最新定案更新:
  - 新增 em_kline_f61: 东财日K(f61 换手率)——CYQ 筹码分布唯一源(字典 V17.0.14)
  - 新增 em_fund_flow: push2delay f137/f140/f143/f146/f149 资金流四档——主力净额
    唯一同口径源(V17.0.16: 主力净=f137, 勿 f137+f140); 走 delay 域不碰 push2 主域
  - collect_fuyao 补 fin_report 三大报表(income/balance/cashflow)——f163 静态PE
    闭环(f160 年报EPS)与 ocf_ttm/revenue_ttm TTM 重建的原始锚数据(V17.0.7)
V17.2.9(2026-09-12) 元数据与健康度修复:
  - --only 增量采集**合并**已有 meta.json(sources/schemes/start/zhb_data_date 均保留),
    修复「单源覆写整份元数据」缺陷; 新增 meta["only"] 与 meta["run"] 运行摘要。
  - 新增 assess_result(): 按返回物中 __error__ 的真实数量判定源状态 ok/partial/failed,
    修复「采集函数内部吞异常返回错误占位、外层仍标 ok=True」缺陷(A8 禁止静默迁就)。
    源条目新增 status / n_error / n_total / n_dead / error_sample 字段。
  - 控制台: 异常源打印 ⚠ + 失败计数, 运行结束追加异常源清单。

V17.2.12(2026-09-12) 采集脚本↔主字典(field_registry.json, 23 源)逐源对齐:
  - collectors 集合扩展为主字典 23 源的完整映射: 已登记但暂无 producer 的 东财-clist/slist、
    沪深交易所, 以及已废弃的 百度, 统一以 unwired/deprecated 标记纳入 collectors(写 meta、
    不进异常源清单), 使脚本采集清单与主字典源清单一一对应。
  - SOURCE_SCHEME 同步增补 baidu/clist/slist/exchange 四项 scheme 标注, 并与
    verify_cross_source_crack.py 的 BUILTIN_SCHEME 保持一致(对撞护栏血缘)。
  - TDX(行情+F10)/axdata/push2_full 为真实可用采集器但 registry 漏登记, 保留采集并在本注记标注
    (属字典侧补登, 非脚本缺陷)。

V17.2.13(2026-09-12) clist/slist 真实 producer 接入(Q3 用户授权):
  - collect_clist / collect_slist 由 unwired 占位升级为真实 producer: 直连 push2 clist/get、slist/get
    (复刻 get_board_fund_flow 的 _quick_request + 83.push2 备域回退策略, 遵守 A1 分域限流)。
  - clist 覆盖 行业/概念/地域 三类板块, 按 §12.8.6 登记字段全集(排名 + 今日/5日/10日 资金流)抓原始 f 字段;
    slist 按 §12.8.5 **逐股**抓其归属板块(须带 secid, 裸 spt=3 实测 rc:102 已订正)字段 f12/f14/f3/f128/f140。
    周六休市不影响(东财数据 API 7×24 服务最近交易日快照)。
  - 沪深交易所(§12.8.17)仍 unwired: 龙虎榜已被 fuyao 覆盖, 官方行情/公告端点需单独 probing(反爬/域差异), 待后续。
  - 配套: registry 补登 TDX/axdata/push2_full、退役 thsdk(见 V17.2.13 governance 提交); 采集脚本移除 collect_thsdk。

输出: docs/field_verification/{YYYYMMDD}/raw_{source}.json(顶层含 scheme 字段体系标注) + meta.json(含 schemes 映射)
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
# V17.2.7: 确保本脚本目录(含 field_meta.py)在 sys.path, 使采集时懒加载 field_meta 必然可达
_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from stock_common.sc_utils import em_secid_prefix  # V17.0 S3: 统一 secid 前缀

POOL_PATH = os.path.join(_ROOT, "docs", "field_verification", "pool.json")
OUT_BASE = os.path.join(_ROOT, "docs", "field_verification")

# V17.1.x: 东财 stock/get 全字段(与主字典登记口径对齐 f1-f250, 保证采集不遗漏任何字段)。
# 统一供 push2 / push2_full / ulist239 / em_fund_flow 等东财 f 编号端点复用;
# 主字典 push2/ulist 最高登记到 f250, 故 range(1,251) 即全量。新增 f 编号时只需改此处。
PUSH2_FULL_FIELDS = ",".join(f"f{i}" for i in range(1, 251))

# A 方案(V17.2.5, 第九轮后落地): 字段体系(scheme)血缘标注。
# 东方财富存在两套 f 编号体系, 同号≠同义(铁证 ulist.f62 == push2.f137 主力净):
#   em.stock_get : push2 / push2_full / em_fund_flow 走 stock/get 端点, 同一套 f 编号
#                  (f62=主力净, f164=pe_ttm); axdata 复用其 f 命名, 占位同族。
#   em.ulist_np  : ulist239 走 ulist.np 端点, 独立 f 编号, 与 stock/get 不同号。
# 其余源为命名/数组体系(zhb/tdx/tencent/sina/fuyao/ftshare…), 与任何 f 编号天然不可按号对应。
# 标注写入每个 raw_{source}.json 顶层 scheme 键 + meta.json(schemes 映射), 供对撞工具
# 与字典 lint 做血缘校验, 从数据层面固化「同号即同义」陷阱的硬提示。
SOURCE_SCHEME = {
    "push2":          "em.stock_get",
    "push2_full":     "em.stock_get",
    "em_fund_flow":   "em.stock_get",   # 同样走 push2delay stock/get, 与 push2 同编号族
    "axdata":         "em.stock_get",    # 复用 PUSH2_FULL_FIELDS 命名(实际短纤指标, 占位同族)
    "ulist239":       "em.ulist_np",     # 独立 f 编号体系, 与 stock/get 不同号
    "zhb":            "zhb",
    "tdx":            "tdx",
    "tencent":        "tencent.qt",
    "sina":           "sina.hq",
    "fuyao":          "fuyao",
    "ftshare":        "ftshare",
    "em_kline_f61":   "em.kline",
    "datacenter":     "em.datacenter",
    "push2ex":        "em.push2ex",
    "em_hot":         "em.hot",
    "cls":            "cls",
    "cninfo":         "cninfo",
    "reports":        "reports",
    "market_sources": "market.mixed",
    "tdx_f10":        "tdx.f10",
    "tdx_f10_more":   "tdx.f10",
    # V17.2.12 主字典对齐: registry 已登记但本脚本暂无 producer 的源(显式标注血缘, 供对撞/lint 校验)
    "baidu":          "baidu.deprecated",   # §12.8.16 ❌→⏸️ 已废弃(PAE 失效, 改 TDX 适配器); 占位不采集
    "clist":          "em.clist",           # 东财-clist(板块排名/板块资金流, §12.8.6); V17.2.13 真实 producer 已接入
    "slist":          "em.slist",           # 东财-slist(个股所属板块/概念归属, §12.8.5); V17.2.13 真实 producer(须 secid, 裸 spt=3→rc:102 已订正)
    "exchange":       "exchange.official",  # 沪深交易所官方(§12.8.17); 龙虎榜已被 fuyao 覆盖; 待官方端点 probing
}

# 模块文档未改动处见上方 docstring; 输出文件新增 scheme 标注(见 main)。


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
        # V17.2.0 增补: 显式暴露 TDX 协议直解字段(内盘/外盘/涨速)为顶层键,
        # 便于碰撞脚本纵向串联, 无需钻 quote_full 嵌套。源=本地 easy_tdx TCP(非云连接器)。
        # limit_up/limit_down 已随同次改动落入 quote_full, 碰撞脚本按需从 quote_full 读取。
        _qf = rec["quote_full"]
        if isinstance(_qf, dict) and "__error__" not in _qf:
            for _k in ("s_vol", "b_vol", "rise_speed"):
                if _qf.get(_k) is not None:
                    rec[_k] = _qf[_k]
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


# ── V17.2.12 主字典对齐: registry 已登记但本脚本暂无 producer 的源 ──
# 这些采集器返回 {"__unwired__": ...} 占位, 由 main() 识别为 unwired/deprecated 状态
# (写 meta、不写 raw 文件、不计入异常源清单), 使脚本采集清单与主字典 23 源一一对应。
def collect_baidu(pool: list) -> dict:
    """百度股市通(已废弃占位, 不采集)。

    字典 §12.8.16: 百度 PAE `getrelatedblock` 已失效(ResultCode 10003),
    K线/行情已切 TDX 适配器, 状态 ❌→⏸️。registry 仍标 active(与字典不一致)——
    本采集器保留为 deprecated 占位, 明确标注, 不发出任何请求(A8: 不假装成功也不假装失败)。
    """
    return {"__unwired__": "deprecated", "registry_name": "百度(baidu)",
            "section": "12.8.16 百度股市通（K线带MA）❌→⏸️",
            "reason": "百度 PAE 已失效, K线/行情改走 TDX 适配器; 不采集"}


def collect_clist(pool: list) -> dict:
    """东财 clist(板块排名/板块资金流, §12.8.6)——真实 producer(V17.2.13)。

    走 push2 clist/get(东财板块榜), 覆盖 行业(m:90 t:2)/概念(t:3)/地域(t:1) 三类,
    按 §12.8.6 登记字段全集抓取原始 f 字段(排名 + 今日/5日/10日 资金流)。
    A1: 复用 stock_common._quick_request(分域限流); 主域失败回退 83.push2 备域
    (与 get_board_fund_flow 同策略)。注意 push2 有 IP 级风控, 本脚本为偶发字段核查用途、
    非生产批量管线, 故可接受; 若遇 RemoteDisconnected 需等待 30-60 分钟再跑。
    """
    from stock_common import _quick_request, UA
    # §12.8.6 登记字段全集: 排名(f2/f3/f4/f12/f13/f14/f104/f105/f128/f136/f140/f141/f207)
    # + 资金流今日(f62/f184/f66/f72/f78/f84)/5日(f164/f165/f109/f257)/10日(f174/f175/f160)
    FIELDS = ("f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207,"
              "f62,f184,f66,f72,f78,f84,f164,f165,f109,f257,f174,f175,f160")
    TYPES = [("industry", "m:90+t:2"), ("concept", "m:90+t:3"), ("area", "m:90+t:1")]
    out = {"records": [], "by_type": {}}
    for label, fs in TYPES:
        # V17.2.13 稳健分页: 以服务端 data.total 为权威总数驱动翻页, 避免「单页未满即误判末页」
        # 导致的概念板(400+ 只)被截断为 100 的问题; 另设 50 页硬上限防异常死循环。
        all_recs = []
        total = None
        pn = 1
        while pn <= 50:
            params = {"po": "1", "np": "1", "fltt": "2", "invt": "2", "fs": fs,
                      "fields": FIELDS, "pz": "200", "pn": str(pn),
                      "ut": "bd1d9ddb04089700cf9c27f6f7426281"}
            hdr = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
            try:
                r = _quick_request("https://push2.eastmoney.com/api/qt/clist/get",
                                   params=params, headers=hdr, timeout=10)
                if r is None:
                    r = _quick_request("http://83.push2.eastmoney.com/api/qt/clist/get",
                                       params=params, headers=hdr, timeout=10)
                if r is None:
                    out["by_type"][label] = {"__error__": "request failed (both domains)"}
                    break
                d = (r.json() or {}).get("data") or {}
                if total is None:
                    total = d.get("total")
                diff = d.get("diff") or []
                if isinstance(diff, dict):
                    diff = list(diff.values())
                if not diff:
                    break
                for it in diff:
                    rec = dict(it); rec["_board_type"] = label
                    all_recs.append(rec)
                # 终止条件: 已达权威 total / 本页未满(末页) / 硬上限
                if total is not None and len(all_recs) >= total:
                    break
                if len(diff) < 200:
                    break
                pn += 1
            except Exception as e:
                out["by_type"][label] = {"__error__": str(e)[:200]}
                break
        out["records"].extend(all_recs)
        out["by_type"][label] = {"n": len(all_recs), "total": total}
    return out


def collect_slist(pool: list) -> dict:
    """东财 slist(个股所属板块/概念归属, §12.8.5)——真实 producer(V17.2.13, 联网实测修正)。

    V17.2.13 联网实测订正(关键): slist/get **必须带 secid(个股 secid)**, 裸 spt=3(无 secid)
    服务端恒返回 rc:102(拒收)。带 secid 时返回**该股票所属的全部板块**(行业/概念/地域混合一表),
    字段: f12=板块 BK 代码、f14=板块名、f3=板块当日涨跌幅%、f128=板块龙头股名、f140=龙头股代码。
    → 与 §12.8.5「个股所属板块/概念归属」语义完全吻合(逐股返回其归属板块列表)。
    此前字典 §12.8.5 误记为「裸 spt=3 返回全局混合板块列表」, 经本次实测更正(裸 spt=3 → rc:102)。
    A1: 复用 _quick_request(0.4rps 分域限流) + 83.push2 备域回退; 周六休市不影响(东财 7×24 快照)。
    逐股请求(20 股), 单股失败记 __error__ 不中断(A8 禁止静默迁就)。
    """
    from stock_common import _quick_request, UA
    FIELDS = "f12,f14,f3,f128,f140"  # 板块代码/名/涨跌幅/龙头名/龙头代码
    out = {"stocks": {}}
    for p in pool:
        c = p["code"]
        secid = em_secid_prefix(c) + c
        params = {"spt": "3", "np": "1", "fltt": "2", "invt": "2", "secid": secid,
                  "fields": FIELDS, "pz": "200", "pn": "1",
                  "ut": "bd1d9ddb04089700cf9c27f6f7426281"}
        hdr = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
        try:
            r = _quick_request("https://push2.eastmoney.com/api/qt/slist/get",
                               params=params, headers=hdr, timeout=10)
            if r is None:
                r = _quick_request("http://83.push2.eastmoney.com/api/qt/slist/get",
                                   params=params, headers=hdr, timeout=10)
            if r is None:
                out["stocks"][c] = {"__error__": "request failed (both domains)"}
                continue
            d = (r.json() or {}).get("data") or {}
            diff = d.get("diff") or []
            if isinstance(diff, dict):
                diff = list(diff.values())
            out["stocks"][c] = {"secid": secid, "n_boards": len(diff), "boards": diff}
        except Exception as e:
            out["stocks"][c] = {"__error__": str(e)[:200]}
    return out


def collect_exchange(pool: list) -> dict:
    """沪深交易所官方(龙虎榜/行情/公告备胎, §12.8.17)——registry 已登记, 暂无 producer。

    龙虎榜已由 fuyao dragon_tiger 覆盖(字典已标注 ✅ 已覆盖); 交易所独立行情/公告备胎
    无对应采集函数, 标记 unwired。
    """
    return {"__unwired__": True, "registry_name": "沪深交易所",
            "section": "12.8.17 沪深交易所官方（龙虎榜/行情/公告备胎）",
            "reason": "registry 已登记; 龙虎榜已被 fuyao 覆盖, 其余端点无 producer → unwired"}


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


def assess_result(data) -> tuple:
    """V17.2.9: 判定采集结果的真实健康度。

    背景: 采集函数内部普遍以 try/except 吞掉异常并写入 `{"__error__": ...}` 占位
    (全脚本 26 处), 因此 `fn(pool)` 正常返回 **不代表采集成功**。旧逻辑据此记
    `ok: True`, 导致 em_kline_f61 遇东财风控 20/20 全失败、push2 主域 20/20 全失败时
    仍被标为成功(触碰公理 A8「禁止静默迁就」)。

    本函数递归统计返回物中 `__error__` 的出现次数, 据此给出三态判定:
      - "ok"      : 零 __error__
      - "partial" : 存在 __error__(字段级失败, 或仅部分容器元素整体失败)
      - "failed"  : 容器元素全部整体失败, 或整个返回物就是一个错误占位

    Args:
        data: 采集函数返回物(通常形如 {"stocks": {code: {...}}})

    Returns:
        (ok, info); ok = (status == "ok"); info 含 status/n_error[/n_total/error_sample]
    """
    n_err = 0
    sample = None

    def walk(o):
        nonlocal n_err, sample
        if isinstance(o, dict):
            if "__error__" in o:
                n_err += 1
                if sample is None:
                    sample = str(o["__error__"])[:160]
                return
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(data)

    # 顶层容器规模 + 其中"整体失败"的元素数(用于区分 partial / failed)。
    # 注意: n_error 是**字段级**计数, 与容器元素数不同量纲, 不能直接比大小 ——
    # 一只股票可有多个字段级 __error__, 故须单独统计"整个元素就是错误占位"的数量。
    n_total = None
    n_dead = 0
    if isinstance(data, dict):
        for _key in ("stocks", "records", "items"):
            _v = data.get(_key)
            if isinstance(_v, (dict, list)) and len(_v):
                n_total = len(_v)
                _items = _v.values() if isinstance(_v, dict) else _v
                n_dead = sum(1 for it in _items
                             if isinstance(it, dict) and "__error__" in it)
                break

    if n_err == 0:
        return True, {"status": "ok", "n_error": 0}

    if isinstance(data, dict) and "__error__" in data:
        status = "failed"                      # 整个返回物即错误占位
    elif n_total is not None and n_dead >= n_total:
        status = "failed"                      # 容器元素全部整体失败
    else:
        status = "partial"                     # 字段级失败 / 仅部分元素失败

    info = {"status": status, "n_error": n_err}
    if n_total is not None:
        info["n_total"] = n_total
        info["n_dead"] = n_dead
    if sample:
        info["error_sample"] = sample
    return False, info


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

    out_dir = os.path.join(OUT_BASE, args.date)
    os.makedirs(out_dir, exist_ok=True)
    meta_path = os.path.join(out_dir, "meta.json")

    meta = {"date": args.date, "start": time.strftime("%Y-%m-%d %H:%M:%S"), "sources": {}}
    # V17.2.9 修复: --only 增量采集必须**合并**已有 meta.json, 而非整份覆盖 ——
    # 否则未参与本次采集的源会从元数据中消失(曾致 22 源元数据被单源覆写)。
    if args.only and os.path.isfile(meta_path):
        try:
            with open(meta_path, encoding="utf-8") as f:
                _prev = json.load(f)
            if isinstance(_prev.get("sources"), dict):
                meta["sources"].update(_prev["sources"])
            if isinstance(_prev.get("schemes"), dict):
                meta["schemes"] = dict(_prev["schemes"])
            for _k in ("start", "zhb_data_date"):
                if _prev.get(_k):
                    meta[_k] = _prev[_k]
            if _prev.get("end"):
                meta["prev_end"] = _prev["end"]
        except Exception as e:
            print(f"  ⚠ 已有 meta.json 读取失败, 本次将整份覆盖: {e}", flush=True)
    meta["only"] = args.only or None

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
        # V17.2.12 主字典对齐: registry 已登记但本脚本暂无 producer(标记 unwired) / 已废弃(deprecated)
        "baidu": collect_baidu,            # §12.8.16 ❌→⏸️ 已废弃, 占位不采集
        "clist": collect_clist,            # §12.8.6 东财-clist; 暂无 producer → unwired
        "slist": collect_slist,            # §12.8.5 东财-slist; 暂无 producer → unwired
        "exchange": collect_exchange,      # §12.8.17 沪深交易所; 龙虎榜已被 fuyao 覆盖 → unwired
    }
    if args.only:
        collectors = {k: v for k, v in collectors.items() if k in [s.strip() for s in args.only.split(",")]}

    for name, fn in collectors.items():
        try:
            t1 = time.time()
            data = fn(pool)
            # V17.2.12 主字典对齐: registry 已登记但本脚本暂无 producer 的源返回 __unwired__ 占位,
            # 显式记为 unwired/deprecated(区别于 ok/partial/failed), 不写 raw 文件、不计入异常源清单。
            _uw = data.get("__unwired__") if isinstance(data, dict) else None
            if _uw:
                _kind = "deprecated" if _uw == "deprecated" else "unwired"
                meta["sources"][name] = {
                    "scheme": SOURCE_SCHEME.get(name, "unknown"),
                    "ok": False, "status": _kind,
                    "registry_name": data.get("registry_name"),
                    "section": data.get("section"),
                    "secs": round(time.time() - t1, 1),
                }
                print(f"  ⊘ {name}: {_kind} (registry 已登记, 无 producer)", flush=True)
                continue
            # A 方案: 标注字段体系(scheme)血缘, 写入 raw 文件顶层 + meta, 供对撞工具/lint 校验
            _scheme = SOURCE_SCHEME.get(name, "unknown")
            if isinstance(data, dict):
                data["scheme"] = _scheme
            # V17.2.7: 字段级 raw/computed + 窗口溯源元数据, 嵌入 raw 文件顶层 `field_meta` 键,
            # 使原始采集物自带字段身份溯源(consumed by computed_collider.py)。懒加载, 失败不影响采集。
            _fm = None
            try:
                from field_meta import field_meta_block
                _fm = field_meta_block(name)
            except Exception:
                _fm = None
            if _fm is not None and isinstance(data, dict):
                data["field_meta"] = _fm
            path = os.path.join(out_dir, f"raw_{name}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1, default=str)
            # V17.2.9 修复: 采集函数会**内部吞异常**并返回 {"__error__": ...} 占位,
            # 旧逻辑只要 fn(pool) 不抛异常就记 ok=True(曾致 em_kline_f61 20/20 全失败仍标 ok)。
            # 现按返回物中 __error__ 的实际数量判定 status: ok / partial / failed。
            _ok, _info = assess_result(data)
            _entry = {"scheme": _scheme, "ok": _ok,
                      "field_meta": _fm is not None,
                      "secs": round(time.time() - t1, 1), "file": path}
            _entry.update(_info)
            meta["sources"][name] = _entry
            if _ok:
                print(f"  ✔ {name}: {_entry['secs']}s", flush=True)
            else:
                _nt = _entry.get("n_total")
                _cnt = f"{_entry['n_error']}/{_nt}" if _nt else str(_entry["n_error"])
                print(f"  ⚠ {name}: {_entry['secs']}s | {_entry['status']} | "
                      f"{_cnt} 处 __error__ | {_entry.get('error_sample', '')}", flush=True)
        except Exception as e:
            meta["sources"][name] = {"scheme": SOURCE_SCHEME.get(name, "unknown"),
                                     "ok": False, "error": str(e)[:300]}
            print(f"  ✖ {name}: {e}", flush=True)

    meta["end"] = time.strftime("%Y-%m-%d %H:%M:%S")
    meta["total_secs"] = round(time.time() - t0, 1)
    # A 方案: 本日各源字段体系(scheme)血缘总览, 供对撞工具/lint 直接读取
    # V17.2.9: 与已有 schemes 合并(--only 时不得丢失未采源的血缘标注)
    meta["schemes"] = {**(meta.get("schemes") or {}),
                       **{k: SOURCE_SCHEME.get(k, "unknown") for k in collectors}}
    # V17.0.10: 记录 ZHB 数据日期(T-1 规则)——对撞破解必须先核对此字段再定对撞报告日期
    try:
        _zhb = json.load(
            open(os.path.join(out_dir, "raw_zhb.json"), encoding="utf-8")
        ).get("zhb_date", "")
        meta["zhb_data_date"] = _zhb or meta.get("zhb_data_date", "")
    except Exception:
        meta.setdefault("zhb_data_date", "")
    # V17.2.9: 本次运行的源级健康度汇总(--only 时只统计本次 collectors, 不误报历史源)
    # V17.2.12: unwired/deprecated 为 registry 已登记但无 producer / 已废弃的预期态, 不计入异常源。
    def _is_abnormal(s: dict) -> bool:
        st = s.get("status")
        if st in ("ok", "unwired", "deprecated"):
            return False
        return not s.get("ok", True)
    _bad = [k for k in collectors if _is_abnormal(meta["sources"].get(k, {}))]
    meta["run"] = {"only": args.only or None, "n_sources": len(collectors),
                   "n_abnormal": len(_bad), "abnormal": _bad}
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    print(f"✔ 完成: {out_dir} | 总耗时 {meta['total_secs']}s | ZHB={meta.get('zhb_data_date')}", flush=True)
    if _bad:
        print(f"⚠ 本次存在异常源 {len(_bad)}/{len(collectors)}: {', '.join(_bad)}", flush=True)


if __name__ == "__main__":
    main()

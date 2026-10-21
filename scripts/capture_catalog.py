from __future__ import annotations

from typing import Dict, List

from scripts.collision_dates import EVENT_SOURCES

# V17.1.x: 东财 stock/get 全字段(与主字典登记口径对齐 f1-f250, 保证采集不遗漏任何字段)。
# 统一供 push2 / ulist239 / em_fund_flow 等东财 f 编号端点复用;
# 主字典 push2/ulist 最高登记到 f250, 故 range(1,251) 即全量。新增 f 编号时只需改此处。
EM_FULL_FIELDS = ",".join(f"f{i}" for i in range(1, 251))

# A 方案(V17.2.5, 第九轮后落地): 字段体系(scheme)血缘标注。
# 东方财富存在两套 f 编号体系, 同号≠同义(铁证 ulist.f62 == push2.f137 主力净):
#   em.stock_get : push2 / em_fund_flow 走 stock/get 端点, 同一套 f 编号
#                  (f62=主力净, f164=pe_ttm)。AxData 是本地 ZHB 短线指标, 独立标记。
#   em.ulist_np  : ulist239 走 ulist.np 端点, 独立 f 编号, 与 stock/get 不同号。
# 其余运行源为命名/数组体系(zhb/tdx/tencent/sina/fuyao…), 与任何 f 编号天然不可按号对应。
# 标注写入每个 raw_{source}.json 顶层 scheme 键 + meta.json(schemes 映射), 供对撞工具
# 与字典 lint 做血缘校验, 从数据层面固化「同号即同义」陷阱的硬提示。
SOURCE_SCHEME = {
    "push2": "em.stock_get",
    "em_fund_flow": "em.stock_get",  # 同样走 push2delay stock/get, 与 push2 同编号族
    "axdata": "axdata.shortline",  # collect_axdata 读取本地 ZHB/AxData 短线指标, 非 Eastmoney
    "kpl": "kpl.limit_up_detail",  # KPL 个股明细独立落盘，保留接口字段路径和来源日期
    "kph": "kph.limit_up_history",  # AxData 传输层访问开盘红历史涨停明细
    "ulist239": "em.ulist_np",  # 独立 f 编号体系, 与 stock/get 不同号
    "zhb": "zhb",
    "tdx": "tdx",
    "eltdx": "eltdx",  # V17.2.25 补登: eltdx 7709/7615 Rust 客户端, 实时连板/短线指标源; 此前漏登记致 scheme=unknown 被 collide 跳过
    "tencent": "tencent.qt",
    "sina": "sina.hq",
    "sina_extended": "sina.extended",
    "fuyao": "fuyao",
    "ftshare": "ftshare",
    "ftshare_rest": "ftshare.rest.a_share_quote",
    "em_kline_f61": "em.kline",
    "datacenter": "em.datacenter",
    "push2ex": "em.push2ex",
    "em_hot": "em.hot",
    "cls": "cls",
    "cninfo": "cninfo",
    "reports": "reports",
    "market_sources": "market.mixed",
    "tdx_f10": "tdx.f10",
    "tdx_f10_more": "tdx.f10",
    # 百度 K 线仅在 --only baidu 时做单次限量验证；默认不触发未经确认的网络请求。
    "baidu": "baidu.kline_probe",
    "clist": "em.clist",  # 东财-clist(板块排名/板块资金流, §12.8.6); V17.2.13 真实 producer 已接入
    "slist": "em.slist",  # 东财-slist(个股所属板块/概念归属, §12.8.5); V17.2.13 真实 producer(须 secid, 裸 spt=3→rc:102 已订正)
    "exchange": "exchange.official",  # 沪深交易所官方(§12.8.17); V17.2.14 真实 producer 已接入(直连 szse/sse 龙虎榜端点)
    # V17.4.0: 事件驱动/可转债/宏观层采集(吸收上游 3.9.0 §11/§14/§15) — 复用 em.datacenter scheme 供 collide 读取;
    #          常量 _EM_REPORTS 标 verified=False, 本采集仅作真伪验证占位(治理铁律: 推断走候选、不越级定案)。
    "event_dc": "em.datacenter",
    "macro_dc": "em.datacenter",
    # V17.4.1: 吸收层 5 模块(新源+新字段, 经上游权威仓库对撞校正) — 各标独立 scheme 供 collide 读取
    "research_sina": "sina.research",  # 新浪研报(研报第二来源, §2.4)
    "etf": "sse/szse.etf_shares",  # ETF 份额(万份, §4.7)
    "news_wscn_cctv": "cctv.news",  # 央视新闻联播(§5.5; WSCN 宏观日历已在 macro_dc)
    "sse_e_interaction": "sse.e_interaction",  # 上证e互动(§10.3)
    "st_list": "em.clist",  # ST/*ST 名单(§6.8, 风险警示板过滤)
}

# 逐股采集器的预期覆盖范围。明确抽样的来源只检查实际计划采集的代码；
# 市场级来源不伪造股票覆盖要求。
FULL_POOL_STOCK_SOURCES = {
    "zhb",
    "tdx",
    "eltdx",
    "tencent",
    "push2",
    "sina",
    "sina_extended",
    "baidu",
    "axdata",
    "tdx_f10",
    "fuyao",
    "em_kline_f61",
    "em_fund_flow",
    "ulist239",
    "slist",
    "datacenter",
    "event_dc",
    "tdx_f10_more",
    "cninfo",
    "reports",
    "ftshare_rest",
}

SOURCE_REQUIRED_PATHS: Dict[str, List[tuple]] = {
    "market_sources": [
        ("cls_market_emotion",),
        ("kph_limit_ladder",),
        ("stock_changes_8201",),
        ("kpl_sentiment",),
        ("kpl_up_down",),
        ("kpl_plate_strength",),
        ("kpl_broken_ratio",),
        ("plate_rotation_matrix",),
        ("plate_rotation_top",),
    ],
    "kpl": [("stocks",)],
    "kph": [("stocks",)],
    "clist": [("by_type", "industry"), ("by_type", "concept"), ("by_type", "area")],
    "push2ex": [("limit_up_pool",), ("limit_down_pool",), ("limit_broken_pool",)],
    "em_hot": [("hot_rank",)],
    "cls": [("telegraph",)],
    "etf": [("etf_sh",), ("etf_sz",)],
    "news_wscn_cctv": [("cctv_xwlb",)],
    "sina_extended": [("stocks",)],
    "ftshare_rest": [("stocks",)],
}

# No field-status check is allowed to remove a source collector. These states
# describe endpoint lifecycle only; verified fields continue to be captured.
NON_RAW_SOURCE_STATUS = {"baidu": "pending_validation"}

EVENT_ONLY_CAPTURE_SOURCES = EVENT_SOURCES

SINA_PAUSED_OPTION_FIELDS = (
    "ask",
    "ask_vol",
    "bid",
    "bid_vol",
    "delta",
    "gamma",
    "iv",
    "last",
    "limit_down",
    "limit_up",
    "open",
    "open_interest",
    "prev_close",
    "strike",
    "theory",
    "theta",
    "vega",
)

SINA_CAPTURED_FIELD_CODES = (
    "item_tongbi",
    "item_value",
    "netamount",
    "opendate",
    "report_type",
    "trade",
    "turnover",
)

SINA_REQUIRED_FLOW_FIELDS = ("opendate", "trade", "netamount", "turnover")

SINA_UNRESOLVED_FIELD_CODES = ("close", "date", "net_amount")

BAIDU_PENDING_FIELD_CODES = ("ma5avgprice", "ma10avgprice", "ma20avgprice")

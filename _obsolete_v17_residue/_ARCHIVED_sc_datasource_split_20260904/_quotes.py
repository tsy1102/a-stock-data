"""stock_common/sc_datasource/_quotes.py — V17.1 拆包子模块（Facade 重导出，零行为变化）"""
from ._shared import *  # 取得 import 块名 + 常量（含私有，见 _shared.__all__）

def get_tencent_quote(code: str) -> Dict[str, Any]:
    """V4: 个股行情 → 腾讯 HTTP 实时（V16.0 修正名不副实问题）。

    V16.0: 原实现直接 return tdx_get_quote_full(code)，与 L1 TDX 是同一函数两次调用，
    导致 data_provider 的"腾讯 L2 fallback"完全冗余。现改为真正请求腾讯 qt.gtimg.cn，
    返回规范字段 dict（经 normalize_at_boundary 归一化）。
    """
    try:
        from stock_common.sc_schema import normalize_at_boundary, DataSource
        from stock_common import _quick_request, _safe_float
        from core.tdx_client import (
            _TENCENT_FIELD_INDEX as _f,
            _TENCENT_MIN_FIELDS,
            _tencent_volume_divisor,  # V17.0.12: 科创板成交量单位换算
        )  # V16.2.4 (B5): 统一字段索引
        prefix = "sh" if code.startswith("6") else ("bj" if code.startswith(("8", "4", "92")) else "sz")
        r = _quick_request(f"https://qt.gtimg.cn/q={prefix}{code}", timeout=10)
        if r is None:
            return {}
        r.encoding = "gbk"
        text = r.text
        if "=" not in text or '"' not in text:
            return {}
        vals = text.split('"')[1].split("~")

        def _tv(key, default=0.0):
            """V17.0.25: 腾讯字段越界安全取值——索引超数组长度(如 [86] 委差)时返回 default,
            避免短数组个股直接下标 IndexError 致整条行情返回 {}（静默丢失兜底源）。"""
            _i = _f.get(key)
            if _i is None or _i >= len(vals):
                return default
            try:
                return float(vals[_i])
            except (ValueError, TypeError):
                return default

        if len(vals) < _TENCENT_MIN_FIELDS:
            _debug_log(
                f"datasource tencent quote: 字段数 {len(vals)} < {_TENCENT_MIN_FIELDS} "
                f"（腾讯协议可能变更，需核对 tdx_client._TENCENT_FIELD_INDEX）"
            )
            return {}
        _price_v = _safe_float(vals[_f["price"]])
        _vol_v = _safe_float(vals[_f["volume_hand"]])
        # V17.0.12: 科创板(688) 腾讯返回的是「股」而非「手」——÷100 归一到手。
        # 实测(2026-08-29, 20 股): 成交额÷(量×现价) 反推每手股数, 688 段=1.01~1.02, 其余=99.3~100.9。
        # 未修正前: 腾讯作为行情兜底源时, 科创板 volume_hand 被放大 100×。
        _vdiv = _tencent_volume_divisor(code)
        if _vol_v and _vdiv != 1.0:
            _vol_v = _vol_v / _vdiv
        # V16.3 O16: 北交所老号段僵尸数据检测（参考仓库 v3.6.0）——43/83/87 已迁 920xxx，
        # 腾讯对老码返回 HTTP 200 + 成交量 0 + 价格定格迁移日的僵尸数据——丢弃触发上游 fallback
        if code.startswith(("43", "83", "87")) and _vol_v == 0 and _price_v > 0:
            _debug_log(f"datasource tencent quote stale (老号段僵尸数据): {code}")
            return {}
        raw = {
            "code": code,
            "name": vals[_f["name"]],
            "price": _price_v,
            "prev_close": _safe_float(vals[_f["last_close"]]),
            "open": _safe_float(vals[_f["open"]]),
            "volume_hand": _vol_v,  # 手（V17.0.12: 科创板 688 已在上方 ÷100 归一）
            "change_pct": _safe_float(vals[_f["change_pct"]]),
            "amount_wan": _safe_float(vals[_f["amount_wan"]]),  # 万元
            "turnover_pct": _safe_float(vals[_f["turnover_pct"]]),
            "vol_ratio": _safe_float(vals[_f["vol_ratio"]]),  # V16.4.0: 量比 v49——val 策略 07 金叉依赖
            "pe_ttm": _safe_float(vals[_f["pe_ttm"]]),
            # V17.0.23(2026-09-01): 静态PE(f163/LYR)——腾讯[53]=pe_static 实锤(主字典§12.8.12e,
            # 茅台 19.73=push2 f163 120/120); 批量路径已接, 逐股现同步, 静态PE完全脱离 push2。
            "pe_lyr": _safe_float(vals[_f["pe_static"]]),
            # V17.0 修复: 删 pe_dynamic←[52]——🔴2026-09-01 纠正：腾讯 [52]=f162=动态PE(pe_mrq), 非静态;
            # 原注释"实为静态PE"系 2026-08-13 误订(已据 fuyao 120/120 + 同花顺官方 pe_mrq=动态 推翻)。
            # 注: 腾讯[53]=f163=静态PE(pe_lyr) 现为 L1(字典定案), 非"无独立静态PE"; pe_dynamic 仍只信 f162/fuyao。
            "mcap_yi": _safe_float(vals[_f["mcap_yi"]]),  # 亿元
            "pb": _safe_float(vals[_f["pb"]]),
            "high": _safe_float(vals[_f["high"]]),
            "low": _safe_float(vals[_f["low"]]),
            # V16.3 O20: 字典多源对齐（field_dict 12.1 破解）——52周/股息率 fallback 链补腾讯
            "high_52w": _safe_float(vals[_f["high_52w"]]),
            "low_52w": _safe_float(vals[_f["low_52w"]]),
            "dividend_yield": _safe_float(vals[_f["dividend_yield"]]),
            # V16.3.3 (2026-08-10 字典 12.1/12.15.5): 腾讯未知位破解接入
            # V17.0.5 正名: roa=TTM 滚动口径(~~年化~~)；新增 tx65=扣非加权ROE(TTM)——盈利质量对
            "roa": _safe_float(vals[_f["roa_ttm"]]),              # ROA(TTM 滚动, %)
            "roe_deduct_ttm": _safe_float(vals[_f["roe_deduct_ttm"]]),  # 扣非加权ROE(TTM, %)
            "change_180td_pct": _safe_float(vals[_f["change_180td_pct"]]),  # 近180交易日涨跌幅(%) — V17.0.7 定案(tx75, 前复权; ~~主力净流入(亿)~~证伪)
            # V17.0.25(2026-09-03): [85] 据主字典 09-03 主动升级定案 = 均价/VWAP 类价格派生(L3候选强)
            "avg_price": _tv("avg_price"),  # 均价/VWAP（茅台 t85=1297.00≈自算VWAP 1297.04, 误差0.003%）
            # V17.0.25(2026-09-03): [56]/[86] 据主字典 09-03 主动升级定案新增（越界安全取）
            "beta": _tv("beta"),            # Beta 族（高置信, 腾讯口径 Beta 估计值）
            "bid_ask_net": _tv("bid_ask_net"),  # 手级带符号量（候选=委差/盘口净量, L4）
            "bid1_vol": _safe_float(vals[_f["bid1_vol"]]),          # 买一量(手) — V16.3.4 新增（sht 封单资金用）
        }
        result = normalize_at_boundary(raw, DataSource.TENCENT)
        # V16.3.3: normalize 为白名单映射——腾讯独有字段（normalize 未定义）在此透传
        # V17.0.25: 透传列表增补 avg_price/beta/bid_ask_net（[85]/[56]/[86] 09-03 定案字段）
        for _xk in ("roa", "roe_deduct_ttm", "change_180td_pct", "avg_price", "beta",
                    "bid_ask_net", "bid1_vol", "vol_ratio", "pe_lyr"):
            if raw.get(_xk) not in (None, 0, "", "0", "0.0"):
                result[_xk] = raw[_xk]
        return result
    except Exception as _e:
        _debug_log(f"datasource get_tencent_quote ({code}): {_e}")
        return {}

async def get_tencent_quote_async(session: Any, code: str) -> Dict[str, Any]:
    """异步版 get_tencent_quote（复用 TDX 同步函数）"""
    import asyncio
    from core.tdx_client import tdx_get_quote_full

    return await asyncio.to_thread(tdx_get_quote_full, code)

def get_concept_blocks(code: str) -> Dict[str, Any]:
    """V7.5 + V15.4 方案 C: 概念板块 — TDX 优先, ZHB tdxchain.cfg 兜底。

    返回: {"industry": [...], "concept": [...], "region": [...], "concept_tags": [...]}

    V15.4 改进:
      - TDX boards concept 优先
      - 概念为空时 fallback 到 ZHB get_concept_from_zhb (解析 tdxchain.cfg)
      - 避免 V15.3 实测"概念板块 0 个"问题（sht 报告对比 V9.6 缺 16 个概念）
    """
    from core.tdx_client import tdx_get_belong_boards

    boards = tdx_get_belong_boards(code) or {}
    result = {
        "industry": boards.get("industry", []),
        "concept": boards.get("concept", []),
        "region": boards.get("area", []),
        "concept_tags": [c["name"] for c in boards.get("concept", []) if c.get("name")],
    }
    # V15.4: 概念为空时 fallback 到 ZHB concept_chain (tdxchain.cfg)
    if not result["concept"]:
        try:
            from core.data_provider import get_concept_from_zhb

            zhb_concepts = get_concept_from_zhb(code) or []
            if zhb_concepts:
                # ZHB 返回的是概念名列表, 包装成 TDX 同样的 dict 格式
                result["concept"] = [
                    {"name": cn, "code": "", "type": "concept"} for cn in zhb_concepts
                ]
                result["concept_tags"] = list(zhb_concepts)
                _debug_log(
                    f"get_concept_blocks ZHB fallback OK ({code}): {len(zhb_concepts)} concepts"
                )
        except Exception as _e:
            _debug_log(f"get_concept_blocks ZHB fallback error ({code}): {_e}")
    return result

async def get_concept_blocks_async(session: Any, code: str) -> Dict[str, Any]:
    """异步版 get_concept_blocks"""
    import asyncio

    return await asyncio.to_thread(get_concept_blocks, code)

def get_ths_hot_raw(date_str: str) -> list:
    """V17.0 S4: 同花顺 getharden 原始列表(三版收敛的唯一请求入口)。

    返回当日强势股行列表 list[dict]（含 id/name/code/reason/date/market），失败返回 []。
    V17.0 探针实测(2026-08-13): 响应 UTF-8 JSON, r.json() 直接解析即可——原 mak 版
    GBK 重试分支永不触发(死分支); 失败不写负缓存(原 async 版写 {} 会毒化后续调用)。
    """
    _cached_rows = _THS_HOT_REASON_CACHE.get(date_str)
    if _cached_rows is not None:
        return _cached_rows
    url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{date_str}/orderby/date/orderway/desc/charset/GBK/"
    try:
        r = _quick_request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"},
            timeout=10,
        )
        if r is None:
            return []
        d = r.json()
        if str(d.get("errocode", 0)) != "0":
            return []
        rows = d.get("data") or []
        _THS_HOT_REASON_CACHE[date_str] = rows
        return rows
    except Exception as _e:
        _debug_log(f"datasource ths hot raw error: {_e}")
    return []

def get_ths_hot_reason(code: str, date_str: str) -> Optional[Dict[str, Any]]:
    """V7.5: 同花顺热点题材归因（短线脚本抽取统一）。

    返回: {"reason": str} 或 None。
    V16.2: 进程级缓存 —— 按 date_str 缓存全市场结果（HTTP 接口一次返回当日全部涨停股原因，
    原逐股重复请求；sht 全市场 7000+ 只 → 1 次）。
    V17.0 S4: 底层统一走 get_ths_hot_raw（三版收敛, 缓存存原始行）。
    """
    rows = get_ths_hot_raw(date_str)
    for row in rows:
        if str(row.get("code")) == str(code) and row.get("reason"):
            return {"reason": row["reason"]}
    return None

async def get_ths_hot_reason_async(
    session: Any, code: str, date_str: str
) -> Optional[Dict[str, Any]]:
    """V7.5: 同花顺热点题材归因

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    V16.2: 复用同步版进程缓存（按 date_str 一次拉取）。
    V17.0 S4: 底层统一走同步 get_ths_hot_raw（to_thread 执行，三版收敛）。
    """
    rows = _THS_HOT_REASON_CACHE.get(date_str)
    if rows is None:
        import asyncio

        await asyncio.to_thread(get_ths_hot_raw, date_str)
        rows = _THS_HOT_REASON_CACHE.get(date_str) or []
    for row in rows:
        if str(row.get("code")) == str(code) and row.get("reason"):
            return {"reason": row["reason"]}
    return None

def get_fupan_zttt() -> Dict[str, Any]:
    """复盘啦涨停天梯（get_zttt 缓存包装）——StockList[99]/ZhuShuList[22] 完整结构。
    字典 12.10.4：涨停天梯；2026-08-10 实测 99 只与财联社/KPL 三源一致。
    """
    try:
        from levistock.stock.stock_fupanla_kph import get_zttt
        return get_zttt() or {}
    except Exception as _e:
        _debug_log(f"datasource fupan zttt: {_e}")
        return {}

def get_fupan_pmsl() -> Dict[str, Any]:
    """复盘啦盘面梳理（get_pmsl 缓存包装）——List[30] 每条 6 字段（TimeMin/TagID/ZSCode/Detail/TagShuXing/TagName）。"""
    try:
        from levistock.stock.stock_fupanla_kph import get_pmsl
        return get_pmsl() or {}
    except Exception as _e:
        _debug_log(f"datasource fupan pmsl: {_e}")
        return {}

def get_stock_permanent_info(code: str) -> Dict[str, Any]:
    """永久不变字段（10 年缓存——字典 12.15.8 static_permanent）。
    - list_date: push2 f189（东财基础信息——外层永久缓存吸收单次 HTTP 成本）
    - ipo_price: ZHB tdxstat2 Col[16]（本地零网络）
    - name_core: 由调用方 parse_stock_name 处理（核心名称永久）
    返回 {"list_date", "ipo_price"}（缺失字段省略）。
    """
    out: Dict[str, Any] = {}
    try:
        # V16.3.3: list_date 走 push2delay f189（push2 主域连接风控实测——f189 拿不到）
        # V16.4.1: "9" 前缀误命中 920 北交所(secid 1.920xxx 恒失败) → 北交所分支提前
        if code.startswith(("92", "8", "4", "43", "83", "87")):
            _mkt = "0"
        else:
            _mkt = "1" if code.startswith(("6", "9")) else "0"
        r = _quick_request(
            "https://push2delay.eastmoney.com/api/qt/stock/get",
            params={"secid": f"{_mkt}.{code}", "fields": "f189",
                    "ut": "f057cbcbce2a86e2866ab8877db1d059"},
            timeout=10,
        )
        if r is not None and r.status_code == 200:
            _d = r.json().get("data") or {}
            if _d.get("f189"):
                out["list_date"] = str(_d["f189"])
    except Exception as _e:
        _debug_log(f"permanent list_date ({code}): {_e}")
    if not out.get("list_date"):
        # TDX 0x0010 兜底（ipo_date 字段——字典 12.14 已录）
        try:
            from core.tdx_client import tdx_get_finance_info
            fin = tdx_get_finance_info(code) or {}
            if fin.get("ipo_date"):
                out["list_date"] = str(fin["ipo_date"])
        except Exception as _e:
            _debug_log(f"permanent list_date tdx ({code}): {_e}")
    try:
        from core.zhb_client import get_zhb_single_stock_data
        z = get_zhb_single_stock_data(code) or {}
        if z.get("ipo_price"):
            out["ipo_price"] = z["ipo_price"]
    except Exception as _e:
        _debug_log(f"permanent ipo_price ({code}): {_e}")
    return out
    """复盘啦盘面梳理（get_pmsl 缓存包装）——List[30] 每条 6 字段。"""
    try:
        from levistock.stock.stock_fupanla_kph import get_pmsl
        return get_pmsl() or {}
    except Exception as _e:
        _debug_log(f"datasource fupan pmsl: {_e}")
        return {}

def ths_hot_list(period: str = "hour") -> List[Dict[str, Any]]:
    """同花顺热榜。period: hour/day。
    返回每只: rank/code/name/heat(人气值)/pct/rank_chg(排名变化)/concepts(概念标签)/tag。

    V15.2 降级策略：HTTP 失败时返回 [] 而非抛异常，避免 val 9 个策略
    (01/02/03/05/06/07/08/16) 因 hot_pool 为空而 0 命中。
    """
    try:
        r = _quick_request(
            "https://dq.10jqka.com.cn/fuyao/hot_list_data/out/hot_list/v1/stock",
            params={"stock_type": "a", "type": period, "list_type": "normal"},
            headers={"User-Agent": UA},
            timeout=10,
        )
        if r is None:
            _debug_log(
                "ths_hot_list: HTTP 返回 None，网络可能限流（不影响 val 报告，hot_pool 降级为空）"
            )
            return []
        lst = (r.json().get("data") or {}).get("stock_list") or []
    except Exception as _e:
        _debug_log(f"ths_hot_list ({period}) HTTP 失败，降级返回空 list: {_e}")
        return []
    out = []
    for it in lst:
        tag = it.get("tag") or {}
        out.append(
            {
                "rank": it.get("order"),
                "code": it.get("code"),
                "name": it.get("name"),
                "heat": it.get("rate"),
                "pct": it.get("rise_and_fall"),
                "rank_chg": it.get("hot_rank_chg"),
                "concepts": tag.get("concept_tag") or [],
                "tag": tag.get("popularity_tag", ""),
            }
        )
    return out

def em_hot_rank(top: int = 50) -> List[Dict[str, Any]]:
    """东财人气榜。返回 rank/code/name/price/pct/rank_chg。"""
    _hot_body = {"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38"}
    try:
        # V16.0.2: 改用 _quick_request（走 _DOMAIN_LIMITS 限流），
        # 原 EM_SESSION.post 直连绕过限流 → emappdata 10rps 封禁隐患
        import json as _json

        r = _quick_request(
            "https://emappdata.eastmoney.com/stockrank/getAllCurrentList",
            data=_json.dumps({**_hot_body, "marketType": "", "pageNo": 1, "pageSize": top}),
            headers={"User-Agent": UA, "Content-Type": "application/json"},
            timeout=10,
            method="POST",
        )
        if r is None:
            return []
        data = r.json().get("data") or []
        if not data:
            return []
        # 人气榜只给带前缀代码，用 push2delay 补名称/价格(V16.4.1: 原 push2 主域——
        # 连接级封禁期会整体失败 → 改 push2delay 镜像域,与采集脚本 ulist239 一致)
        secids = [("0." if it["sc"].startswith("SZ") else "1.") + it["sc"][2:] for it in data]
        u = _quick_request(
            "https://push2delay.eastmoney.com/api/qt/ulist.np/get",
            params={
                "ut": "f057cbcbce2a86e2866ab8877db1d059",
                "fltt": 2,
                "invt": 2,
                "fields": "f14,f3,f12,f2",
                "secids": ",".join(secids),
            },
            headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"},
            timeout=10,
        )
        if u is None:
            return []
        diff = (u.json().get("data") or {}).get("diff") or []
        if isinstance(diff, dict):
            diff = list(diff.values())
        nm = {x["f12"]: (x.get("f14"), x.get("f2"), x.get("f3")) for x in diff}
    except Exception as _e:
        _debug_log(f"datasource em_hot_rank: {_e}")
        return []
    out = []
    for it in data:
        code = it["sc"][2:]
        name, price, pct = nm.get(code, ("", None, None))
        out.append(
            {
                "rank": it["rk"],
                "code": code,
                "name": name,
                "price": price,
                "pct": pct,
                "rank_chg": it.get("hisRc"),
            }
        )
    return out

def em_hot_concept(code: str) -> List[Dict[str, Any]]:
    """东财个股热门概念命中（这只票当下被市场归到哪些概念在炒）。
    返回 [{concept, bk, hit(命中热度)}, ...]，按热度降序。
    """
    _hot_body = {"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38"}
    try:
        # V16.0.2: 改用 _quick_request（走限流），原 EM_SESSION.post 直连绕过限流
        import json as _json

        prefix = "BJ" if code.startswith(("92", "8", "4", "43", "83", "87")) else ("SH" if code.startswith("6") else "SZ")
        r = _quick_request(
            "https://emappdata.eastmoney.com/stockrank/getHotStockRankList",
            data=_json.dumps({**_hot_body, "srcSecurityCode": prefix + code}),
            headers={"User-Agent": UA, "Content-Type": "application/json"},
            timeout=10,
            method="POST",
        )
        if r is None:
            return []
        data = r.json().get("data") or []
    except Exception as _e:
        _debug_log(f"datasource em_hot_concept ({code}): {_e}")
        return []
    return [
        {"concept": x.get("conceptName"), "bk": x.get("conceptId"), "hit": x.get("hitCount")}
        for x in data
    ]

def get_stock_changes(change_type: str = "8201") -> List[Dict[str, Any]]:
    """V16.1.7: 东财盘口异动（字典 §12.10.1，levistock 实测 2782 条）。

    change_type: 8201 火箭发射 / 8193 大笔买入 / 8205 封涨停板 / 64 有大买盘 / 8202 快速反弹
    返回: [{code/name/market/time/change_pct/price/change_type/date}]
    V17.0.1e(2026-08-16): levistock 把原始字段 i 原样放入 change_pct——
    实际 i 为逗号串 "涨跌幅小数,价格,涨跌幅小数"(push2ex getAllStockChanges 原始结构),
    _safe_float 解析失败 → 涨幅恒 0。此处直接解析原始 JSON 修复。
    """
    try:
        import requests
        from stock_common import UA
        from stock_common.stock_calendar import get_last_trading_day
        from stock_common.sc_network import _em_wait_process_interval
        _em_wait_process_interval()
        _params = {
            "type": change_type,
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "pageindex": 0,
            "pagesize": 10000,
            "dpt": "wzchanges",
        }
        resp = requests.get(
            "https://push2ex.eastmoney.com/getAllStockChanges",
            params=_params, headers={"User-Agent": UA}, timeout=10,
        )
        resp.raise_for_status()
        body = (resp.json().get("data") or {})
        items = body.get("allstock", []) or []
        _date = get_last_trading_day().strftime("%m-%d")
        rows = []
        for item in items:
            if not isinstance(item, dict):
                continue
            code = str(item.get("c", ""))
            name = str(item.get("n", ""))
            if name.startswith("ST") or name.startswith("*ST"):
                continue
            tm = str(item.get("tm", ""))
            if len(tm) == 5:
                tm = "0" + tm
            chg, px = 0.0, 0.0
            _i = str(item.get("i", ""))
            if _i and "," in _i:
                _parts = _i.split(",")
                try:
                    # i 结构: 8201 火箭发射=涨幅,价格,涨幅; 8193 大笔买入/64 有大买盘=量(手),价格,涨跌幅,金额
                    # 统一: 第三段=盘中触发时刻涨跌幅(小数→%), 第二段=触发价(实测 5 股全部自洽)
                    chg = float(_parts[2]) * 100.0 if len(_parts) >= 3 else 0.0
                    px = float(_parts[1]) if len(_parts) >= 2 else 0.0
                except (ValueError, IndexError):
                    pass
            rows.append({
                "code": code,
                "name": name,
                "market": str(item.get("m", "")),
                "time": tm,
                "change_pct": chg,
                "price": px,
                "change_type": change_type,
                "date": _date,
            })
        return rows
    except Exception as _e:
        _debug_log(f"datasource get_stock_changes: {_e}")
    return []

def get_shortline_indicators(code: str) -> Dict[str, Any]:
    """V16.1.7: AxData 短线指标 34 字段（字典 §12.12.1，实测 stats_root 消费项目 zhb.zip）。

    stats_root 用项目 cache/zhb 最新包（零额外下载）。
    返回: open_volume_ratio(开盘量比)/auction_prev_volume_ratio(竞价昨比)/
          seal_to_amount_ratio(封成比)/seal_to_float_ratio(封流比)/
          limit_board_text(几天几板)/limit_up_streak_days(连板)/
          free_float_shares(自由流通股本Z)/year_limit_up_days 等 34 字段
    """
    import glob
    import os

    try:
        from axdata_core import request_interface
        # 找最新 zhb 包
        zhb_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache", "zhb")
        zips = sorted(glob.glob(os.path.join(zhb_dir, "zhb_*.zip")))
        if not zips:
            return {}
        stats_root = zips[-1]
        r = request_interface(
            "stock_shortline_indicators_tdx",
            params={"code": code, "stats_root": stats_root},
            fields=None, persist=False, data_root=None,
        )
        records = getattr(r, "records", None)
        if records and isinstance(records[0], dict):
            return records[0]
    except Exception as _e:
        _debug_log(f"datasource get_shortline_indicators ({code}): {_e}")
    return {}

def get_tdx_chip_race(period: int = 0, sort: int = 1) -> List[Dict[str, Any]]:
    """通达信早盘/尾盘抢筹数据（字典无此源——来源 myhhub/stock stock_chip_race.py）。

    Args:
        period: 0=早盘抢筹, 1=尾盘抢筹
        sort: 排序(1=委托金额/2=成交金额/3=开盘金额/4=幅度/5=占比)

    Returns:
        [{"code","name","price","change_rate","bid_rate","bid_trust_amount",...}]
    """
    from stock_common import _quick_request

    payload = json.dumps([{
        "funcId": 20, "offset": 0, "count": 100,
        "sort": sort, "period": period, "Token": _TDX_QC_TOKEN,
        "modname": "JJQC",
    }])
    r = _quick_request(_TDX_QC_URL, data=payload, timeout=10, method="POST",
                       headers={"Content-Type": "application/json; charset=UTF-8"})
    if r is None:
        return []
    try:
        rows = r.json()
        if isinstance(rows, list) and rows:
            inner = rows[0].get("data") or []
            out = []
            for d in inner:
                out.append({
                    "code": d.get("StockCode", ""),
                    "name": d.get("StockName", ""),
                    "pre_close": float(d.get("ZSJ", 0)) / 10000,
                    "open_price": float(d.get("KPJ", 0)) / 10000,
                    "price": float(d.get("ZJCJG", 0)) / 10000,
                    "change_rate": float(d.get("ZDF", 0)),
                    "deal_amount_wan": float(d.get("CJJE", 0)) / 1e4,
                    "bid_trust_amount_wan": float(d.get("QCWTJE", 0)) / 1e4,
                    "bid_deal_amount_wan": float(d.get("QCCJJE", 0)) / 1e4,
                    "bid_rate_pct": float(d.get("QCFD", 0)) * 100,
                    "bid_ratio_pct": float(d.get("QCZB", 0)) * 100,
                    "limitup_days": int(d.get("TJZT", 0)),
                    "limitup_boards": int(d.get("TJQB", 0)),
                })
            return out
    except Exception as _e:
        _debug_log(f"datasource get_tdx_chip_race: {_e}")
    return []

def get_em_xuangu(sty_fields: str = "", filter_expr: str = "",
                  page: int = 1, page_size: int = 50) -> List[Dict[str, Any]]:
    """东财选股器服务端筛选（200+ 字段任意组合——来源 myhhub/stock stock_selection.py）。

    Args:
        sty_fields: 逗号分隔的字段代码串（如 SECURITY_CODE,TOTAL_MARKET_CAP,NEW_PRICE）
        filter_expr: 过滤表达式（如 (MARKET="上交所主板")(NEW_PRICE>10)）
        page/page_size: 分页

    Returns:
        [{"SECURITY_CODE":"600519","SECURITY_NAME_ABBR":"贵州茅台",...}]
    """
    import requests as _req
    from stock_common.sc_network import EM_SESSION

    headers = {
        "User-Agent": UA,
        "Referer": "https://data.eastmoney.com/xuangu/",
    }
    params = {
        "sty": sty_fields if sty_fields else "ALL",
        "p": page,
        "ps": page_size,
        "source": "SELECT_SECURITIES",
        "client": "WEB",
    }
    if filter_expr:
        params["filter"] = filter_expr
    try:
        r = EM_SESSION.get(_EM_XUANGU_URL, params=params, headers=headers, timeout=15)
        if r.status_code != 200:
            return []
        d = r.json()
        return (d.get("result") or {}).get("data") or []
    except Exception as _e:
        _debug_log(f"datasource get_em_xuangu: {_e}")
        return []

def _kpl_post(url: str, action: str, controller: str, extra: dict = None) -> Optional[dict]:
    """KPL 统一 POST（直接 requests.post——必须用 Dalvik UA，_quick_request 会覆盖导致空数据）。
    自行限流 >=200ms。V17.0.7 字典 §12.21.5。"""
    import time as _time
    global _KPL_LAST_CALL
    el = _time.time() - _KPL_LAST_CALL
    if el < 0.2:
        _time.sleep(0.2 - el)
    _KPL_LAST_CALL = _time.time()

    params = dict(_KPL_BASE)
    params["a"] = action
    params["c"] = controller
    if extra:
        params.update(extra)
    body_parts = []
    for k, v in params.items():
        body_parts.append(f"{k}={v}")
    body = "&".join(body_parts) + "&"
    import requests as _req_mod
    try:
        r = _req_mod.post(url, data=body.encode("utf-8"),
                          headers=dict(_KPL_HEADERS), timeout=15)
        if r.status_code != 200:
            return None
        txt = r.text
        cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", txt)
        d = json.loads(cleaned)
        ec = str(d.get("errcode", ""))
        if ec != "0":
            _debug_log(f"kpl {action}/{controller}: errcode={ec} {d.get('errmsg','')[:60]}")
            return None
        return d.get("data") or d
    except Exception as e:
        _debug_log(f"kpl {action}/{controller}: {e}")
        return None

def kpl_get_market_emotion() -> Optional[Dict[str, Any]]:
    """市场情绪实时数据（涨停数/跌停数/强度/连板高度）。

    Returns:
        {"ztjs": 涨停数, "df_num": 跌停数, "strong": 强度,
         "lbgd": 连板高度, "Day": 日期}
    """
    return _kpl_post(_KPL_HQ, "ChangeStatistics", "HomeDingPan")

def kpl_get_rise_fall_analysis() -> Optional[List]:
    """涨跌分析 [涨停数,?,跌停数,?,涨跌比%,?,日期]。"""
    return _kpl_post(_KPL_HQ, "RiseFallAnalysis", "HomeDingPan")

def kpl_get_stock_zd_num() -> Optional[Dict[str, Any]]:
    """涨跌家数。"""
    return _kpl_post(_KPL_HQ, "MarketStockZDNum", "HomeDingPan")

def kpl_get_real_ranking_info(date: str = "", index: int = 0) -> Optional[Dict[str, Any]]:
    """板块排行列表(30只/页, 19列含 code/name/strength/change_pct/speed/
    turnover/main_net/main_buy/main_sell/vol_ratio/circ_mv/big_order_net/
    total_mv/pe_today/pe_next 等)。"""
    return _kpl_post(_KPL_HIS, "RealRankingInfo", "ZhiShuRanking", {
        "Type": "1", "ZSType": "7", "Index": str(index), "st": "30",
        "Date": date, "Order": "1",
    })

def kpl_get_stock_list_w8(plate_id: str, date: str = "",
                          stock_type: int = 0) -> Optional[Dict[str, Any]]:
    """板块成分股详情(63字段, 需遍历 Type 0~19 合并去重)。
    域名必须用 apphis.longhuvip.com；响应 key 是小写 list。"""
    return _kpl_post(_KPL_HIS, "ZhiShuStockList_W8", "ZhiShuRanking", {
        "PlateID": plate_id, "Date": date, "Type": str(stock_type),
        "Index": "0", "st": "30", "Order": "1", "TSZB": "0",
        "IsZZ": "0", "TSZB_Type": "0", "filterType": "0", "old": "1",
    })

def kpl_get_ytfp_bkhx(date: str = "") -> Optional[Dict[str, Any]]:
    """复盘啦板块核心(涨停原因+题材+个股明细)。"""
    extra = {}
    if date:
        extra["Date"] = date
    return _kpl_post(_KPL_HIS, "GetYTFP_BKHX", "FuPanLa", extra)

def kpl_get_ytfp_sctd(date: str = "") -> Optional[Dict[str, Any]]:
    """复盘啦市场题材(几天几板 Tips，如'3天2板')。"""
    extra = {}
    if date:
        extra["Date"] = date
    return _kpl_post(_KPL_HIS, "GetYTFP_SCTD", "FuPanLa", extra)

def kpl_get_lhb_stock_list() -> Optional[Dict[str, Any]]:
    """龙虎榜股票列表。"""
    return _kpl_post(_KPL_LHB, "GetStockList", "LongHuBang")

def kpl_get_info() -> Optional[Dict[str, Any]]:
    """首页聚合(ErBanList/JJJYList/TKGKList)。"""
    extra = {"View": "1"}
    return _kpl_post(_KPL_HQ, "GetInfo", "Index", extra)

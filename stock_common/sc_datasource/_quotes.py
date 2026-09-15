"""_quotes.py — V17.2 拆包子模块（共享命名空间片段，由 __init__ 载入）

本文件不是独立可导入模块；其源码被 stock_common/sc_datasource/__init__.py
exec 进包命名空间，与包内其他函数/状态共享同一 globals()。
"""
# flake8: noqa: F821  (名称来自包共享命名空间，本片段不单独导入)

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
        # V17.2.x(2026-09-10) 调整 D: 腾讯[8]/[7] 内盘/外盘 单位随板块(科创板按股)→÷_vdiv 归一手
        #   （与 TDX s_vol/b_vol、push2 f161/f49 单位对齐，统一层合成时不致量级错配）
        _ssv = _tv("s_vol")
        if _ssv and _vdiv != 1.0:
            _ssv = _ssv / _vdiv
        _bsv = _tv("b_vol")
        if _bsv and _vdiv != 1.0:
            _bsv = _bsv / _vdiv
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
            # V17.2.x(2026-09-10) 调整 A: 均价源 [85]→[51]（字典 09-08 round12 定案: [85]对均价锚仅3/20已撤销, [51]强锚+TDX快照）
            "avg_price": _tv("avg_price"),  # 均价/VWAP（腾讯[51]；TDX快照 average_price 同义）
            # V17.0.25(2026-09-03): [56] Beta 族（高置信, 腾讯口径 Beta 估计值）
            "beta": _tv("beta"),
            # V17.2.x(2026-09-10) 调整 B: 委差源 [86]→[50]（字典 09-08 定案: [86]非委差已撤销, [50]+push2 f192 为 canonical）
            "bid_ask_net": _tv("bid_ask_net"),  # 委差（手级带符号量, 腾讯[50]；push2 f192 兜底）
            # V17.2.x(2026-09-10) 调整 C/D: 委比/买二卖二价/内盘外盘（字典 §12.8.12e canonical 实装）
            "entrust_ratio": _tv("entrust_ratio"),  # 委比%(腾讯[74]；push2 f191 / TDX快照 同义)
            "bid2": _tv("bid2"),  # 买二价(元, 腾讯[12]；tdx bid2 / sina[14] 同义)
            "ask2": _tv("ask2"),  # 卖二价(元, 腾讯[22]；tdx ask2 / sina[24] 同义)
            "s_vol": _ssv,  # 内盘(主动卖, 手) — 腾讯[8]（科创板按股已÷_vdiv 归手）
            "b_vol": _bsv,  # 外盘(主动买, 手) — 腾讯[7]（科创板按股已÷_vdiv 归手）
            "bid1_vol": _safe_float(vals[_f["bid1_vol"]]),          # 买一量(手) — V16.3.4 新增（sht 封单额用）
            # V17.0.27(2026-09-07): 涨停/跌停价脱离 push2——腾讯[47]/[48]（字典 12.8.12e 行3082/3083 实锤）
            "limit_up": _safe_float(vals[_f["limit_up"]]),
            "limit_down": _safe_float(vals[_f["limit_down_price"]]),
        }
        result = normalize_at_boundary(raw, DataSource.TENCENT)
        # V16.3.3: normalize 为白名单映射——腾讯独有字段（normalize 未定义）在此透传
        # V17.0.25: 透传列表增补 avg_price/beta/bid_ask_net（[85]/[56]/[86] 09-03 定案字段）
        # V17.2.x(2026-09-10): 透传列表增补 entrust_ratio/bid2/ask2/s_vol/b_vol（调整 C/D 实装字段）
        for _xk in ("roa", "roe_deduct_ttm", "change_180td_pct", "avg_price", "beta",
                    "bid_ask_net", "entrust_ratio", "bid2", "ask2", "s_vol", "b_vol",
                    "bid1_vol", "vol_ratio", "pe_lyr",
                    "limit_up", "limit_down"):
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


@cached(category="concept_blocks", ttl_seconds=TTL["concept_blocks"], cross_verify=True)
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


@requires_push2
def get_em_quote_full(code: str) -> Dict[str, Any]:
    """V15.2 P0 修复: 通过东财 push2 stock/get 获取完整行情。

    V16.3.3: host 参数化重构——本函数走 push2 主域（风控最严，最后手段）；
    常规兜底请用 get_em_quote_full_delay（push2delay 镜像域，风控独立）。
    """
    return _em_quote_full_impl(code, "https://push2.eastmoney.com/api/qt/stock/get")


@cached(category="quote_full_delay", trading_day=True, valid_if=make_valid_if())
def get_em_quote_full_delay(code: str) -> Dict[str, Any]:
    """V16.3.3 (2026-08-10 字典 12.15.5): push2delay 镜像域版全字段行情。

    2026-08-10 实测：push2 主域连接级风控（RemoteDisconnected）；push2delay 风控独立、
    114 字段全量可用、延时 15 分钟非盘中无影响——统一层 L3 东财兜底应优先本函数。

    V17.0.26(2026-09-03): 加 @cached——原每次调用直打 push2delay（单股 sht/med/lng 报告
    每只多次、重跑 val 全市场重复打），违反字典 §12.15.5「push2delay 镜像域应优先缓存以降频」。
    trading_day=True 保证日级数据次日 9:30 刷新（15min 延时数据缓存一天无影响）；
    valid_if 拒绝空/全零行情避免投毒。数据_provider 的进程内 _PD_EXTRA_CACHE 仍做单 run 兜底去重。
    """
    r = _em_quote_full_impl(code, "https://push2delay.eastmoney.com/api/qt/stock/get")
    if not r and em_exchange_prefix(code, upper=True) == "BJ":  # V17.2.11: 北交所东财封禁 → 官方备份
        r = get_bse_quote_backup(code) or {}
    return r


def get_em_fund_flow_multiday(code: str) -> Dict[str, Any]:
    """V17.2.1: 多日主力净流入（ulist.np 端点 f164/f165；单位 元 / %）。

    ⚠️ 跨端点同号异义铁律：push2delay **stock/get 主域** 的 f164 = pe_ttm（估值字段），
       与 **ulist.np 端点** 的 f164 = 近5日主力净流入 **同号不同义**（东财跨端点复用 f 编号）。
       本函数固定走 ulist.np，绝不从主域读 f164，避免污染 pe_ttm。

    V17.2.1 实证（docs/field_verification/20260907_round5_multiday_check.md）：
       ulist f164 == 最近 5 个**交易日**主力净(f62)滚动和，命中 10/11（按交易日序，非自然日）。

    返回 {"fund_main_5d": 元, "fund_main_5d_pct": %}；失败/风控返回 {}。
    """
    try:
        from stock_common.sc_utils import em_secid_prefix
        from stock_common import _quick_request

        r = _quick_request(
            "https://push2delay.eastmoney.com/api/qt/ulist.np/get",
            params={
                "fltt": "2", "invt": "2",
                "secids": em_secid_prefix(code) + code,
                "fields": "f12,f164,f165",
            },
            headers={"Referer": "https://quote.eastmoney.com/"},
            timeout=10,
        )
        if r is None:
            return {}
        diff = (r.json().get("data") or {}).get("diff") or []
        if isinstance(diff, dict):
            diff = list(diff.values())
        if not diff or not isinstance(diff[0], dict):
            return {}
        it = diff[0]
        out: Dict[str, Any] = {}
        _v = it.get("f164")
        if isinstance(_v, (int, float)):
            out["fund_main_5d"] = float(_v)
        _p = it.get("f165")
        if isinstance(_p, (int, float)):
            out["fund_main_5d_pct"] = float(_p)
        return out
    except Exception as _e:
        _debug_log(f"datasource get_em_fund_flow_multiday({code}): {_e}")
        return {}

def get_em_ulist_batch(codes: List[str], fields: str = _ULIST_BATCH_FIELDS) -> List[Dict[str, Any]]:
    """V17.0.26: push2delay ulist.np 批量行情取数，返回**原始 diff 记录列表**。

    背景(DEBT-011)：原先这段取数内联在 `core/data_provider.prefetch_quote_batch` 里
    直连裸 HTTP，违反公理 A1（数据访问收口）。本函数把它下沉到适配器层。

    分层约定（**重要**）:
      - 本函数**只取数、不做业务语义映射**：返回原始 f2/f12/... 记录，
        字段→业务名的映射与单位换算由调用方（Tier1 门面 data_provider）负责。
        这样"取数在适配器、语义在门面"，避免语义散落两处。
      - 安全域：固定 push2delay **镜像域**（风控独立），严禁 push2 主域
        （45000/h 封禁 20h）。
      - 自动分批：>300 只按 300/批拆分。
      - 容错：单批失败（返回 None）或抛异常 → 跳过该批，不冒泡中断调用方。

    关于缓存（公理 A4，有意不加 @cached，详见 DEBT-011 台账论证）:
      - 批量接口若按 codes 组合做 key，组合数爆炸（sht 35 只的任意子集），
        命中率极低，且 300 个 code 拼出的 key ≈ 2.1KB，SQLite 索引效率低；
      - 真正的去重由**调用方门面层按 code 粒度**完成（prefetch_quote_batch 的
        _BATCH_QUOTE_CACHE 只把 missing 的 code 传下来），比按批组合缓存更有效；
      - 跨运行的单股行情缓存已由 `get_em_quote_full_delay` 覆盖。

    Args:
        codes: 股票代码列表（6 位纯数字，如 ["600519", "000001"]）
        fields: 东财字段集；默认覆盖行情/OHLC/市值。
                **不含估值字段** —— 实测 ulist.np 的 f162/f167/f126 恒返回 "-"
                （与 stock/get 单股接口语义不同），估值须走单股接口补齐。

    Returns:
        list: 原始 diff 记录列表（每条 dict，键为 "f2"/"f12" 等东财字段码）。
              全部失败返回 []（**只返回非空结果**，符合公理 A4）。
    """
    if not codes:
        return []

    # 92 北交所须先于 9 判定，统一走 em_secid_prefix（勿手写 startswith("9")）
    from stock_common.sc_utils import em_secid_prefix
    from stock_common import _quick_request

    rows: List[Dict[str, Any]] = []
    for i in range(0, len(codes), _ULIST_BATCH_SIZE):
        chunk = codes[i : i + _ULIST_BATCH_SIZE]
        secids = ",".join(em_secid_prefix(c) + c for c in chunk)
        try:
            r = _quick_request(
                "https://push2delay.eastmoney.com/api/qt/ulist.np/get",
                params={"fltt": "2", "invt": "2", "secids": secids, "fields": fields},
                headers={"Referer": "https://quote.eastmoney.com/"},
                timeout=10,
            )
            if r is None:      # 风控/封禁跳过，与 `_quick_request` 的 None 约定一致
                continue
            diff = (r.json().get("data") or {}).get("diff") or []
            # 东财偶发以 dict（下标→记录）形式返回，统一摊平为 list
            if isinstance(diff, dict):
                diff = list(diff.values())
            rows.extend(x for x in diff if isinstance(x, dict))
        except Exception as _e:
            _debug_log(f"datasource get_em_ulist_batch chunk[{i}:{i + _ULIST_BATCH_SIZE}]: {_e}")
            continue
    return rows


def _em_quote_full_impl(code: str, host: str = "https://push2delay.eastmoney.com/api/qt/stock/get") -> Dict[str, Any]:
    """内部实现：host 参数化的全字段行情获取（f43-f221，字典 12.9.1）。

    ZHB tdxstat.cfg 35 字段中无 price/change_pct/open/high/low/last_close 等行情字段，
    只能从 HTTP 接口拿。push2 stock/get 是最权威的实时行情源（盘后返回收盘价）。

    Returns:
        dict: {
            "price": float,           # f43  现价（盘后=昨收）
            "open": float,            # f46  今开
            "high": float,            # f44  最高
            "low": float,             # f45  最低
            "last_close": float,      # f60  昨收
            "change_pct": float,      # f170 涨跌幅(%)（push2 直接给出，不需要用 price-昨收 算）
            "amplitude_pct": float,   # f171 振幅(%)
            "change_amt": float,      # f169 涨跌额
            "volume_hand": float,     # f47  成交量(手)
            "amount_wan": float,      # f48  成交额(元→万元)
            "turnover_pct": float,    # f168 换手率(%)
            "pe_ttm": float,          # f164 PE（TTM） (fltt=2 下为浮点，无需 /100) — 🔴2026-09-01 纠正：f164=T重TTM，f163才是静态PE
            "pe_lyr": float,           # f163 静态PE(LYR, 现价÷年报EPS)
            "pe_dynamic": float,
            "pb": float,
            "mcap_yi": float,         # f116 总市值(元→亿元)
            "float_mcap_yi": float,   # f117 流通市值(元→亿元)
            "total_shares": float,    # f84  总股本(股→万股)
            "float_shares": float,    # f85  流通股本(股→万股)
            "name": str,              # f58  股票名称（最新）
            "industry": str,          # f127 行业名称
            "board": str,             # f128 地域板块名称
            "list_date": str,         # f189 上市日期
            "data_date": str,         # 行情快照日期
            # V17.0.7 财务 TTM 族（口径经 fuyao 官方报表终判）:
            "ocf_ttm": float,           # f103 经营活动现金流量净额 TTM (元)
            "revenue_ttm": float,       # f104 营业总收入 TTM (元)
            "net_profit_period": float, # f105 归母净利润 最新报告期 (元)
            "eps_deduct_ttm": float,    # f108 扣非每股收益 TTM (元/股)
            "net_profit_annual": float, # f109 归母净利润 最新年报 (元)
            "eps_annual": float,        # f160 年报EPS (=f109/f84) (元/股)
            "undist_profit_ps": float,  # f190 每股未分配利润 (元/股)
        }
    """
    if not code or len(code) != 6:
        return {}
    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    url = host
    # V16.1: 字段包从 19 个扩展为已验证字段包（2026-08-04 官方 TdxQuant 交叉验证）
    #   f51/f52=涨停/跌停价、f55=EPS、f92=BPS、f126=股息率、f162-167=PE×3/PB
    #   f174/f175=52周高低、f137-146=资金流12字段、f198=行业码、f80=交易时段
    #   f129=概念列表（V16.1.7: 概念链 push2 兜底源）
    # 生产字段包（固定，非 f1-f250 全量，防风控）
    params = {
        "fltt": "2",
        "invt": "2",
        "secid": secid,
        "fields": (
            "f43,f44,f45,f46,f47,f48,f57,f58,f60,f84,f85,"
            "f116,f117,f127,f128,f129,f168,f169,f170,f171,f189,"  # V16.2.3: f168 换手率补回（sht 换手率 0.00%）
            "f49,f51,f52,f55,f92,f126,f161,f162,f163,f164,f165,f166,f167,f191,f192,"
            "f174,f175,f198,f80,f221,"  # V16.2: f221 报告期
            # V17.0.16: 补 f149(小单净) —— 旧版只取 f135-f146，缺小单档，
            # 导致四档占比之和不足 100%（大盘股缺 ~3%，小盘股缺 ~38%）。
            "f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f149,"
            "f178,"
            # V17.0.7(2026-08-25 字典终破): 财务 TTM 族——f103 经营现金流净额(TTM 元)/
            # f104 营业总收入(TTM 元)/f105 归母净利(最新报告期 元)/f108 扣非EPS(TTM)/
            # f109 归母净利(最新年报 元)/f160 年报EPS/f190 每股未分配利润
            "f103,f104,f105,f108,f109,f160,f190"
        ),
        "ut": "f057cbcbce2a86e2866ab8877db1d059",
    }
    headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
    try:
        r = em_get(url, params=params, headers=headers, timeout=10)
        if r is None:
            return {}
        d = r.json()
        if not d or "data" not in d or not d["data"]:
            return {}
        data = d["data"]
        result: Dict[str, Any] = {}

        # 价格类（push2 用 fltt=2/invt=2 时，f43/f44/f45/f46/f60/f169 直接是元为单位的 float）
        for src, dst in [
            ("f43", "price"),
            ("f44", "high"),
            ("f45", "low"),
            ("f46", "open"),
            ("f60", "last_close"),
            ("f169", "change_amt"),
        ]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 涨跌幅/振幅/换手率（push2 直接给出数字，单位 %）
        for src, dst in [
            ("f170", "change_pct"),
            ("f171", "amplitude_pct"),
            ("f168", "turnover_pct"),
        ]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 成交量(手) — push2 f47 单位是手
        vol_hand = data.get("f47")
        if vol_hand is not None and vol_hand != "-":
            try:
                result["volume_hand"] = float(vol_hand)
            except (TypeError, ValueError):
                pass
        # 成交额(元) — push2 f48 单位是元，转万元
        amt_yuan = data.get("f48")
        if amt_yuan is not None and amt_yuan != "-":
            try:
                result["amount_wan"] = float(amt_yuan) / 10000.0
            except (TypeError, ValueError):
                pass

        # 总市值/流通市值（push2 f116/f117 单位是元，转亿元）
        mcap_yuan = data.get("f116")
        if mcap_yuan is not None and mcap_yuan != "-":
            try:
                result["mcap_yi"] = float(mcap_yuan) / 1e8
            except (TypeError, ValueError):
                pass
        float_mcap_yuan = data.get("f117")
        if float_mcap_yuan is not None and float_mcap_yuan != "-":
            try:
                result["float_mcap_yi"] = float(float_mcap_yuan) / 1e8
            except (TypeError, ValueError):
                pass

        # 股本（push2 f84/f85 单位是股，转万股）
        total_shares = data.get("f84")
        if total_shares is not None and total_shares != "-":
            try:
                result["total_shares"] = float(total_shares) / 10000.0
            except (TypeError, ValueError):
                pass
        float_shares = data.get("f85")
        if float_shares is not None and float_shares != "-":
            try:
                result["float_shares"] = float(float_shares) / 10000.0
            except (TypeError, ValueError):
                pass

        # 名称/行业/地域/上市日期
        name = data.get("f58")
        if name and isinstance(name, str):
            result["name"] = name
        industry = data.get("f127")
        if industry and isinstance(industry, str):
            result["industry"] = industry
        board = data.get("f128")
        if board and isinstance(board, str):
            result["board"] = board
        # V16.1.7: f129 概念列表（逗号分隔 → list，概念链 push2 兜底源）
        concepts_raw = data.get("f129")
        if concepts_raw and isinstance(concepts_raw, str):
            result["concepts"] = [c.strip() for c in concepts_raw.split(",") if c.strip()]
        list_date = data.get("f189")
        if list_date:
            try:
                ld = str(int(list_date))
                if len(ld) == 8:
                    result["list_date"] = f"{ld[:4]}-{ld[4:6]}-{ld[6:8]}"
            except (TypeError, ValueError):
                pass

        # ─────────────────────────────────────────────
        # V16.1: push2 扩展字段（2026-08-04 官方 TdxQuant 交叉验证）
        # ─────────────────────────────────────────────
        # 涨停/跌停价（f51/f52，官方 ZTPrice/DTPrice 精确匹配）
        for src, dst in [("f51", "limit_up"), ("f52", "limit_down")]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # EPS/BPS（f55/f92，与东财 F10 精确匹配）
        for src, dst in [("f55", "eps"), ("f92", "bps")]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 股息率（f126，官方 DYRatio 匹配）
        v = data.get("f126")
        if v is not None and v != "-":
            try:
                result["dividend_yield"] = float(v)
            except (TypeError, ValueError):
                pass

        # V17.2.x(2026-09-10) 调整 B/D: 委差/委比/内盘/外盘（字典 §12.8.12e；push2 stock/get f192/f191/f161/f49）
        #   ⚠️ 跨端点同号异义铁律：f49/f161/f191/f192 仅在本 stock/get 主域/镜像域读取，绝不混入 ulist.np 端点
        for src, dst in [
            ("f191", "entrust_ratio"),   # 委比%(东财 B14)
            ("f192", "bid_ask_net"),     # 委差(手, 东财 B13)
            ("f161", "s_vol"),           # 内盘(主动卖成交量, 手)
            ("f49", "b_vol"),            # 外盘(主动买成交量, 手)
        ]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # PE 三口径 + PB（🔴2026-09-01 据 field_dict 定案纠正：f162=动态PE/f163=静态PE（LYR）/f164=TTM(pe_ttm)/f167=PB）
        pe_map = {
            "f162": "pe_dynamic",
            "f163": "pe_lyr",
            "f164": "pe_ttm",
            "f167": "pb",
        }
        for src, dst in pe_map.items():
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 52周高低（f174/f175，官方 HisHigh/HisLow 精确匹配）
        for src, dst in [("f174", "high_52w"), ("f175", "low_52w")]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # 行业板块代码（f198，如 BK1277）
        v = data.get("f198")
        if v and isinstance(v, str):
            result["industry_code_push2"] = v

        # V16.2: 最新报告期（f221，YYYYMMDD）
        v = data.get("f221")
        if v and str(v).strip() and str(v).strip() != "-":
            result["report_period"] = str(v).strip()

        # 交易时段数组（f80，JSON 字符串 → 原样保留）
        v = data.get("f80")
        if v and isinstance(v, str):
            try:
                result["trading_periods"] = json.loads(v)
            except (TypeError, ValueError, json.JSONDecodeError):
                result["trading_periods"] = []

        # 资金流字段(f135-f146 + f149)——V17.0.16(2026-08-31) 结构实证**重定案**
        #
        # ⚠️ 旧版(V17.0)把 f135-f146 当成**并列的四档** 特大/大单/中单/小单，并算
        #    「主力净额 = f137 + f140」——**错的**，本段已按实证重写。
        #
        # 三条独立铁证（详见 docs/field_dict.md §12.3.3）：
        #   ① 结构自洽 + 全组合盲搜（12 采集日 169 样本，相对差 **0.00**，100% 命中）：
        #        f135 = f138 + f141     f136 = f139 + f142     f137 = f140 + f143
        #      → **f137 是合计档**，不可能是并列的"特大单净"。
        #        旧命名下应推出 f137 = f138 − f139 = f140，但实测 0/169 相等（96.4% 显著分离）。
        #   ② ulist239 同名号段（12 采集日 236 样本）：**f62 == f66 + f72 命中 236/236 = 100%**
        #      → 东财标准档位：f62=主力净、f66=超大单净、f72=大单净、f78=中单净、f84=小单净。
        #   ③ 跨接口对撞（234 样本，2% 容差）：
        #        f62==f137 96.6%   f66==f140 98.3%   f72==f143 96.2%
        #        f78==f146 95.7%   f84==f149 96.2%   f84==f146 仅 0.9%（排除）
        #
        # 正确层级（买/卖/净 三组 + 主力为合计）：
        #      f138/139/140 = 超大单 买/卖/净
        #      f141/142/143 = 大单   买/卖/净
        #      f135/136/137 = **主力** 买/卖/净  （= 超大单 + 大单，东财官方"主力"定义）
        #      f144/145/146 = 中单   买/卖/净
        #      f149         = 小单净（**f135-f146 段内没有小单买/卖明细**）
        #
        # 后果（旧 bug 的实际影响）：`主力净 = f137 + f140` 把超大单净**重复计一次**，
        #   实测 (f137+f140)/f137 中位 **1.196** → 主力净额虚高约 **40%**，
        #   并沿 data_provider `main_net_buy_amount` 流入各报告章节（静默、不报错）。
        #   现改为**直接取 f137**，不再相加。
        #
        # 单位: 元
        flow_map = {
            "f135": ("fund_main_buy", "fund_flow"),      # 主力买入额 = f138 + f141
            "f136": ("fund_main_sell", "fund_flow"),     # 主力卖出额 = f139 + f142
            "f137": ("fund_main_today", "fund_flow"),    # 主力净额   = f140 + f143（**不可再加 f140**）
            "f138": ("fund_super_buy", "fund_flow"),     # 超大单买入额
            "f139": ("fund_super_sell", "fund_flow"),    # 超大单卖出额
            "f140": ("fund_super_today", "fund_flow"),   # 超大单净额
            "f141": ("fund_large_buy", "fund_flow"),     # 大单买入额
            "f142": ("fund_large_sell", "fund_flow"),    # 大单卖出额
            "f143": ("fund_large_today", "fund_flow"),   # 大单净额
            "f144": ("fund_mid_buy", "fund_flow"),       # 中单买入额
            "f145": ("fund_mid_sell", "fund_flow"),      # 中单卖出额
            "f146": ("fund_mid_today", "fund_flow"),     # 中单净额
            "f149": ("fund_small_today", "fund_flow"),   # 小单净额（无买/卖明细）
        }
        for src, (dst, _cat) in flow_map.items():
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        # V17.0.16: 主力净额**直接等于 f137**（东财已聚合好 超大单 + 大单）。
        # 旧版在此外加 f140 属重复计数，见上方 flow_map 注释的三条铁证。

        # 近5日主力净流入数组（f178，JSON）
        v = data.get("f178")
        if v and isinstance(v, str):
            try:
                result["fund_5d_array"] = json.loads(v)
                # V17.0: 5日主力净由 f178 数组聚合(替代原 f141 误读)
                _s5 = sum(float(x.get("mainNetAmt", 0)) for x in result["fund_5d_array"] if isinstance(x, dict))
                if _s5:
                    result["fund_main_5d"] = _s5
            except (TypeError, ValueError, json.JSONDecodeError):
                pass

        # V17.0.7(2026-08-25 字典终破): 财务 TTM 族(单位见键注释; 口径经
        # fuyao 官方三大报表 5/5 终判 + 报告期切换动态双证——详见
        # docs/field_verification/20260825_cross_analysis.md)
        for src, dst in [
            ("f103", "ocf_ttm"),            # 经营活动现金流量净额 TTM (元)
            ("f104", "revenue_ttm"),        # 营业总收入 TTM (元)
            ("f105", "net_profit_period"),  # 归母净利润 最新报告期 (元)
            ("f108", "eps_deduct_ttm"),     # 扣非每股收益 TTM (元/股)
            ("f109", "net_profit_annual"),  # 归母净利润 最新年报 (元)
            ("f160", "eps_annual"),         # 年报EPS (=f109/f84) (元/股)
            ("f190", "undist_profit_ps"),   # 每股未分配利润 (元/股, ≡ulist f48)
        ]:
            v = data.get(src)
            if v is not None and v != "-":
                try:
                    result[dst] = float(v)
                except (TypeError, ValueError):
                    pass

        result["data_date"] = datetime.now().strftime("%Y-%m-%d")
        return result
    except Exception as _e:
        _debug_log(f"sc_datasource get_em_quote_full ({code}): {_e}")
        return {}


@cached(category="fupan_review", ttl_seconds=TTL["fupan_review"], trading_day=True)
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


@cached(category="fupan_review", ttl_seconds=TTL["fupan_review"], trading_day=True)
def get_fupan_pmsl() -> Dict[str, Any]:
    """复盘啦盘面梳理（get_pmsl 缓存包装）——List[30] 每条 6 字段（TimeMin/TagID/ZSCode/Detail/TagShuXing/TagName）。"""
    try:
        from levistock.stock.stock_fupanla_kph import get_pmsl
        return get_pmsl() or {}
    except Exception as _e:
        _debug_log(f"datasource fupan pmsl: {_e}")
        return {}


@cached(category="static_permanent", ttl_seconds=TTL["static_permanent"], valid_if=make_valid_if())
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


@cached(
    category="ths_hot_reason",
    ttl_seconds=TTL["ths_hot_reason"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False, min_size=1),
)  # V15.2: 拒绝空 list；空时返回 [] 不缓存
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


@cached(category="hot_rank", ttl_seconds=TTL["hot_rank"])
@requires_push2
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


@cached(category="hot_concept", ttl_seconds=TTL["hot_concept"])
def em_hot_concept(code: str) -> List[Dict[str, Any]]:
    """东财个股热门概念命中（这只票当下被市场归到哪些概念在炒）。
    返回 [{concept, bk, hit(命中热度)}, ...]，按热度降序。
    """
    _hot_body = {"appId": "appId01", "globalId": "786e4c21-70dc-435a-93bb-38"}
    try:
        # V16.0.2: 改用 _quick_request（走限流），原 EM_SESSION.post 直连绕过限流
        import json as _json

        prefix = em_exchange_prefix(code, upper=True)  # V17.2.11: 收敛散点 startswith("6") 路由
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


@cached(category="market_emotion", ttl_seconds=TTL["limit_pool"], trading_day=True)
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


@cached(category="basic_info", ttl_seconds=TTL["basic_info"], trading_day=True)
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


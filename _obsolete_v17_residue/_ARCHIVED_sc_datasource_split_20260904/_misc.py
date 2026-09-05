"""stock_common/sc_datasource/_misc.py — V17.1 拆包子模块（Facade 重导出，零行为变化）"""
from ._shared import *  # 取得 import 块名 + 常量（含私有，见 _shared.__all__）

def get_historical_high_qfq(code: str, count: int = 640) -> Optional[float]:
    """V17.0.5 P2: 历史最高价（腾讯前复权日线, ~640 根≈2.6 年窗口）。

    参考仓库 v3.7.0/3.2.5#28 同源问题修复: TDX bars 为不复权原始价,
    长期分红股跨除权比较会低估真实回撤。qfq 口径与现价同基准可直接比。
    接口: web.ifzq.gtimg.cn fqkline(字典 §12.1 备胎——免费无鉴权, 与 TDX 实测一致)。
    """
    from stock_common.sc_network import _quick_request

    mkt = "bj" if code.startswith(("92", "8", "4", "43", "83", "87")) else (
        "sh" if code.startswith(("6", "9", "5")) else "sz")
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    try:
        r = _quick_request(
            url,
            params={"param": f"{mkt}{code},day,,,{count},qfq"},
            headers={"Referer": "https://gu.qq.com/"},
            timeout=10,
        )
        if r is None:
            return None
        d = (r.json() or {}).get("data") or {}
        node = d.get(f"{mkt}{code}") or {}
        days = node.get("qfqday") or node.get("day") or []
        highs = [float(row[3]) for row in days if len(row) > 3 and float(row[3]) > 0]
        return max(highs) if highs else None
    except Exception as _e:
        _debug_log(f"datasource historical_high_qfq ({code}): {_e}")
        return None

def baidu_kline_full(code, count=800, is_index=False):
    """全量K线 → tdx_client 适配器（纯 TDX 日K线）。

    V16.3 O16: 修正误导性 docstring——百度 PAE 已无实际调用（v3.1.0 起参考仓库同款
    下线 fundflow，本仓库 K 线全程 TDX），函数名保留向后兼容。
    V16.3 O19: 加 count 参数（脚本层直调 tdx_get_security_bars 统一入口，跨脚本共享缓存）。
    V17.0.17: 形参重排为 (code, count=800, is_index=False)。原签名 (code, is_index=False,
    count=800) 是footgun——调用点 baidu_kline_full(code, 60) 会把 60 当成 is_index(真值)去取
    **指数**K线, 个股返回空, 致 K线形态/异动雷达章节恒空, 且伴随"指数K线响应截断"告警。
    重排后位置第2参即 count, 与所有调用点"count 位置传参"的意图一致(仅 get_sht 指数分支用
    关键字 is_index=True)。
    """
    from core.tdx_client import tdx_get_security_bars, tdx_get_index_bars

    if is_index:
        return tdx_get_index_bars(code)
    return tdx_get_security_bars(code, count=count)

def get_cyq_distribution(code: str, days: int = 240) -> Dict[str, Any]:
    """V17.0.14: 筹码分布 CYQ —— 东财 push2 日K线(f61 换手率) → calculate_cyq。

    来源(参考 chengzuopeng/stock-sdk chips 维度, 2026-08-30 分析): 成本分布是报告价值维度;
    本项目 calculate_cyq(三角形分布+换手率衰减, 与通达信 CYQ 一致) V17.0.7 已实现,
    但此前**未接入管线**(仅股东户数代理进 筹码面评分), 且**从未有单测**——
    V17.0.14 本函数补齐数据入口, 单测见 tests/core/test_core_cyq.py(28 例, 含算法/入口/评分三层)。

    为何用东财 kline: TDX 0x0010 日K(mootdx bars)与腾讯 ifzq fqkline 均**不含换手率字段**,
    而 CYQ 必需 OHLC+换手率; 东财 push2his kline 的 f61=换手率(%)为权威口径, 复用 fflow 多域轮换。

    Args:
        code: 6位股票代码
        days: 换手窗口(默认240≥calculate_cyq 的 cyq_days=210)

    Returns:
        calculate_cyq 字典(benefit_pct/avg_cost/cost_90_*/concentration_90/cost_70_*/concentration_70)
        + "source" 字段; 失败/数据不足返回 {}。
    """
    from stock_common.sc_technical import calculate_cyq

    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 含北交所 92
    params = {
        "lmt": str(days),
        "klt": "101",  # 日K
        "secid": secid,
        "fqt": "0",  # V17.0.17: 不复权(成本分布用实际成交价); 缺省 EM 返回 rc:102 data:null
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
        "end": "20500101",
    }
    # V17.0.15: 24h 磁盘缓存（审查发现的关键风险）
    #   em_get 只有**令牌桶限流 + 熔断**，**没有任何数据缓存** → 未加缓存前，全仓扫描时
    #   sht/med/lng 三脚本各调一次 = **3N 次东财请求**。而东财 push2 系属**连接级风控**
    #   （RemoteDisconnected，字典 §12.3 实测恢复 20+ 小时），一旦触发会连带影响资金流/行情等
    #   同域接口。CYQ 依赖的 240 根日K+换手率属 T+1 稳定数据，与 K 线同性质 → 沿用同一 TTL。
    try:
        from stock_common.sc_kline_cache import get_cached_blob

        _cached = get_cached_blob("CYQ", code, days)
        if isinstance(_cached, dict) and _cached:
            return dict(_cached)
    except Exception:
        pass
    try:
        # V17.0.14: 复用 fflow 多域轮换(push2his 全窗口优先——历史 K线需全窗口)
        r = _em_fflow_request("/api/qt/stock/kline/get", params, prefer_his=True)
        if r is None:
            return {}
        d = r.json()
        klines = (d.get("data") or {}).get("klines") or []
        if not klines:
            return {}
        dates, opens, closes, highs, lows, turns = [], [], [], [], [], []
        for _kl in klines:
            _p = str(_kl).split(",")
            if len(_p) < 11:
                continue
            dates.append(_p[0])
            opens.append(_safe_float(_p[1]))
            closes.append(_safe_float(_p[2]))
            highs.append(_safe_float(_p[3]))
            lows.append(_safe_float(_p[4]))
            turns.append(_safe_float(_p[10]))  # f61 = 换手率(%)
        if len(closes) < 2:
            return {}
        _cyq = calculate_cyq(dates, opens, closes, highs, lows, turns)
        if _cyq:
            _cyq["source"] = "eastmoney_kline_f61"
            # 只缓存**非空**结果：若把失败/空数据也写进缓存，当日后续调用会全部命中空值，
            # 反而在接口恢复后仍拿不到数据（失败不缓存原则）。
            try:
                from stock_common.sc_kline_cache import set_cached_blob

                set_cached_blob("CYQ", code, days, _cyq)
            except Exception:
                pass
        return _cyq
    except Exception as _e:
        _debug_log(f"datasource cyq ({code}): {_e}")
        return {}

def _today_str() -> str:
    """当日 YYYYMMDD(缓存日期口径用)."""
    import datetime as _dt

    return _dt.date.today().strftime("%Y%m%d")

def start_datacenter_prefetch(codes, session, dragon_kwargs=None) -> int:
    """调度五类 datacenter 数据的整批预取(幂等——已调度的 (kind,code) 跳过)。

    必须在事件循环内调用(execute_batch_pipeline 的 prefetch_async_fn 钩子)。
    消费侧用 resolve_datacenter('kind', code) 取结果; 未调度的键走调用方直调。

    Returns:
        本次新入队的 (kind, code) 项数
    """
    import asyncio as _aio

    dk = dragon_kwargs or {}
    specs = {
        "dragon_tiger": lambda c: get_dragon_tiger_board_async(
            session, c, days=180,
            include_seats=dk.get("include_seats", True),
            enhance_seats=dk.get("enhance_seats", True)),
        "northbound": lambda c: get_northbound_hold_async(session, c, 20),
        "margin": lambda c: get_margin_trading_async(session, c),
        "lockup": lambda c: get_lockup_expiry_async(
            session, c, days=90, include_history=True),
        "block_trade": lambda c: get_block_trade_async(session, c),
    }
    loop = _aio.get_event_loop()
    scheduled = 0
    for kind, fetch in specs.items():
        todo = [c for c in codes if (kind, c) not in _DC_PREFETCH_FUTURES]
        if not todo:
            continue
        futs = {c: loop.create_future() for c in todo}
        # 先注册后执行——消费方随时 await 不竞态
        _DC_PREFETCH_FUTURES.update(futs)

        async def _run(_todo=todo, _futs=futs, _fetch=fetch, _kind=kind):
            for c in _todo:
                try:
                    res = await _fetch(c)
                except Exception as e:
                    _debug_log(f"datasource dc prefetch {_kind}/{c}: {e}")
                    res = None
                if not _futs[c].done():
                    _futs[c].set_result(res)

        loop.create_task(_run())
        scheduled += len(todo)
    return scheduled

async def resolve_datacenter(kind: str, code: str, direct_fn=None):
    """取预取结果; 该键未参与预取时回退 direct_fn()(原直调协程工厂)。"""
    fut = _DC_PREFETCH_FUTURES.get((kind, code))
    if fut is not None:
        return await fut
    if direct_fn is not None:
        return await direct_fn()
    return None

def _query_dt_pool_tc(date_str: str = "") -> Optional[int]:
    """V17.0.8: 东财 getTopicDTPool 的 tc 权威总数——pool 明细可能为空但 tc>0。
    用于 get_limit_pool_summary 跌停兜底（替代会读到 T-1 的 ZHB 快照）。"""
    if not date_str:
        from datetime import datetime

        date_str = datetime.now().strftime("%Y%m%d")
    url = "https://push2ex.eastmoney.com/getTopicDTPool"
    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "dpt": "wz.ztzt",
        "Pageindex": 0,
        "pagesize": 100,
        "sort": "fbt:asc",
        "date": date_str,
    }
    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return None
        d = r.json()
        tc = (d.get("data") or {}).get("tc")
        return int(tc) if tc is not None else None
    except Exception as _e:
        _debug_log(f"datasource dt pool tc: {_e}")
        return None

def get_tdx_day_tail(code: str) -> Dict[str, Any]:
    """V17.0.1d(2026-08-16): TDX 本机 .day 尾部快速读(零网络毫秒级).

    新版 .day 32B 记录: date<uint32> + open/high/low/close<int32×0.01元(分)> +
    amount<float32 元> + volume<int32 股> + reserved。
    返回 {price, open, high, low, amount_wan, date}。
    ⚠️ C1 终审修复(2026-08-15): 价格刻度 ÷1000→÷100(实测 600519 close=134199→1341.99)。
    用途: 休市/盘前 canonical OHLC/成交额缺口兜底(与 TDX 快照同源, 零网络)。
    """
    try:
        import os as _os
        import struct as _st

        _mkt = "bj" if code.startswith(("92", "8", "4", "43", "83", "87")) else ("sh" if code.startswith(("6", "9")) else "sz")
        _path = _os.path.join(_tdx_root(), "vipdoc", _mkt, "lday", f"{_mkt}{code}.day")
        with open(_path, "rb") as _f:
            _f.seek(-32, 2)
            _rec = _f.read(32)
        if len(_rec) < 32:
            return {}
        _date = _st.unpack_from("<I", _rec, 0)[0]
        _open = _st.unpack_from("<I", _rec, 4)[0] / 100.0
        _high = _st.unpack_from("<I", _rec, 8)[0] / 100.0
        _low = _st.unpack_from("<I", _rec, 12)[0] / 100.0
        _close = _st.unpack_from("<I", _rec, 16)[0] / 100.0
        if _close <= 0:
            return {}
        _amount = _st.unpack_from("<f", _rec, 20)[0]  # 元
        _volume = _st.unpack_from("<I", _rec, 24)[0]  # 股
        return {
            "price": _close,
            "open": _open,
            "high": _high,
            "low": _low,
            "amount_wan": (_amount / 1e4) if _amount and _amount > 0 else 0.0,
            "volume_hand": (_volume / 100.0) if _volume and _volume > 0 else 0.0,
            "date": _date,
        }
    except Exception as _e:
        _debug_log(f"get_tdx_day_tail ({code}): {_e}")
        return {}

def get_share_capital(code: str) -> Dict[str, Any]:
    """V10.1: 获取单只股票的股本数据（总股本、流通股）。

    Returns:
        {"total_shares": float, "float_shares": float, "updated_at": str}
        单位：万股
    """
    try:
        from stock_common.sc_capital_cache import get_share_capital as _get_cap

        return _get_cap(code)
    except Exception as _e:
        _debug_log(f"datasource share_capital ({code}): {_e}")
        return {"total_shares": 0, "float_shares": 0, "updated_at": ""}

def calc_mcap_yi(code: str, price: float) -> float:
    """V10.1: 计算总市值（亿元）。

    Args:
        code: 股票代码
        price: 当前价格（元）

    Returns:
        总市值（亿元），失败返回0
    """
    try:
        from stock_common.sc_capital_cache import calc_mcap_yi as _calc

        return _calc(code, price)
    except Exception as _e:
        _debug_log(f"datasource calc_mcap_yi ({code}): {_e}")
        return 0.0

def calc_float_mcap_yi(code: str, price: float) -> float:
    """V10.1: 计算流通市值（亿元）。

    Args:
        code: 股票代码
        price: 当前价格（元）

    Returns:
        流通市值（亿元），失败返回0
    """
    try:
        from stock_common.sc_capital_cache import calc_float_mcap_yi as _calc

        return _calc(code, price)
    except Exception as _e:
        _debug_log(f"datasource calc_float_mcap_yi ({code}): {_e}")
        return 0.0

def print_batch_summary(results, total):
    """批量执行结果汇总打印。

    Args:
        results: 结果列表，每项应为 {"code": str, "status": str, "error": str}。
        total: 总股票数量。
    """
    ok = [r for r in results if r["status"] == "成功"]
    fd = [r for r in results if r["status"] == "数据失败"]
    fg = [
        r
        for r in results
        if r["status"] in ("GD上传失败", "GD上传异常", "GD文件夹失败", "GD未连接")
    ]
    print(f"\n{'=' * 60}")
    print(f"  批量执行完成 — 共处理 {total} 只股票")
    print(f"{'=' * 60}")
    print(f"  ✅ 全部成功: {len(ok)}  |  ❌ 数据失败: {len(fd)}  |  ⚠️ GD上传失败: {len(fg)}")

def get_index_kline_closes(index_code: str, days: int = 250) -> List[float]:
    """指数日K收盘价序列（V17.0.7 自 mak.get_index_returns._get_kline 下沉统一层）。

    四源链(与 mak 原实现逐行为等价迁移, 全走限流包装):
      TDX 指数K线(core.tdx_client) → 腾讯 ifzq 前复权日K → 新浪 getKLineData
      → 腾讯实时 2 值(仅 1 日回报兜底)。
    供 mak 行业轮动/异动偏离(ret_3d/10d/20d/60d) 与其他脚本指数区间收益复用。

    Args:
        index_code: 指数代码（如 sh000001 / sz399106）
        days: 需要的交易日数量

    Returns:
        收盘价列表（升序）；全部失败返回 []
    """
    import json as _json

    # L1: TDX 指数K线(TCP 不封 IP)
    try:
        from core.tdx_client import tdx_get_index_bars

        keys, rows = tdx_get_index_bars(index_code, count=days)
        if keys and rows:
            ci = next((i for i, k in enumerate(keys)
                       if k in ("close", "close_price")), -1)
            if ci >= 0:
                closes = [_safe_float(r[ci]) for r in rows if len(r) > ci]
                if closes:
                    return closes
    except Exception as _e:
        _debug_log(f"datasource index_kline tdx error {index_code}: {_e}")

    # L2: 腾讯 ifzq 前复权日K（完整序列）
    try:
        r = _quick_request(
            f"https://ifzq.gtimg.cn/appstock/app/fqkline/get?param={index_code},day,,,{days},qfq",
            timeout=10,
        )
        if r:
            d = (r.json().get("data") or {}).get(index_code, {})
            kline = d.get("qfqday") or d.get("day") or []
            closes = [_safe_float(row[2]) for row in kline if len(row) > 2 and row[2]]
            if closes:
                return closes
    except Exception as _e:
        _debug_log(f"datasource index_kline tencent error {index_code}: {_e}")

    # L3: 新浪日K（V17.0.4: 与腾讯 ifzq 实测一致 <0.01）
    try:
        r = _quick_request(
            "https://quotes.sina.cn/cn/api/jsonp_v2.php/var/CN_MarketDataService.getKLineData",
            params={"symbol": index_code, "scale": 240, "ma": "no", "datalen": days},
            headers={"User-Agent": UA,
                     "Referer": "https://finance.sina.com.cn"},
            timeout=10,
        )
        if r:
            _m = re.search(r"\((.*)\)", r.text, re.S)
            if _m:
                _arr = _m.group(1)
                if _arr.startswith("["):
                    _rows = _json.loads(_arr)
                    closes = [_safe_float(x.get("close")) for x in _rows if x.get("close")]
                    closes = [c for c in closes if c > 0]
                    if closes:
                        return closes
    except Exception as _e:
        _debug_log(f"datasource index_kline sina error {index_code}: {_e}")

    # L4: 腾讯实时 2 值（仅 1 日回报——指标静默 None 有提示）
    try:
        r = _quick_request(f"https://qt.gtimg.cn/q={index_code}", timeout=10)
        if r:
            r.encoding = "gbk"
            v = r.text.split('"')[1].split("~")
            close = _safe_float(v[3])
            pre_close = _safe_float(v[4])
            return [pre_close, close] if close > 0 else []
    except Exception as _e:
        _debug_log(f"datasource index_kline realtime error {index_code}: {_e}")
    return []

def get_cls_market_emotion() -> Dict[str, Any]:
    """V16.1.7: 财联社市场情绪（字典 §12.10.2，实测可用）。

    返回: market_degree(热度0-100)/shsz_balance(两市成交额)/up_ratio(封板率)/
          up_open_num(炸板)/performance(昨涨停今表现)/up_open_ratio(高开率)/
          profit_ratio(获利率)/up_down_dis(涨跌分布)/limit_up_board(连板梯队)
    """
    try:
        import levistock as lk
        # V16.2: levistock 内部直连东财，绕过统一限流 → 调用前走进程级协调（全局 ≤1 rps）
        try:
            from stock_common.sc_network import _em_wait_process_interval
            _em_wait_process_interval()
        except Exception:
            pass
        d = lk.market_emotion_cls()
        if isinstance(d, dict) and d:
            return d
    except Exception as _e:
        _debug_log(f"datasource get_cls_market_emotion: {_e}")
    return {}

"""_eastmoney.py — V17.2 拆包子模块（共享命名空间片段，由 __init__ 载入）

本文件不是独立可导入模块；其源码被 stock_common/sc_datasource/__init__.py
exec 进包命名空间，与包内其他函数/状态共享同一 globals()。
"""
from __future__ import annotations
from datetime import datetime, timedelta
import asyncio
import code
import hashlib
import json
import os
import re
import urllib
import uuid
from stock_common.sc_network import DATACENTER_URL, RateLimitBlockedError, UA, _async_request_with_retry, _biz_logger, _debug_log, _gen_wait_process_interval, _http_logger, _quick_request, em_get, requires_push2
from stock_common.sc_utils import _safe_float, em_exchange_prefix, em_secid_prefix
from core.stock_cache import TTL, cached, make_valid_if
from ._shared import _DC_PREFETCH_FUTURES, _EM_BATCH_CACHE, _EM_BATCH_CACHE_DATE, _EM_L2_TTL, _FFLOW_HOSTS
from stock_common.sc_kpl import _f


def eastmoney_datacenter(
    code: str,
    report_name: str,
    columns: str = "ALL",
    filter_str: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
    page_index: int = 1,
) -> List[Dict[str, Any]]:
    """东财数据中心统一查询（datacenter-web.eastmoney.com）。

    V7.5 新增：HTTP状态码非200时记录日志，业务错误码(status=-1)时记录日志，JSON解析失败时记录日志。
    """
    try:
        full_filter = filter_str if filter_str else f'(SECURITY_CODE="{code}")'
        r = _quick_request(
            DATACENTER_URL,
            params={
                "reportName": report_name,
                "columns": columns,
                "filter": full_filter,
                "pageNumber": str(page_index),
                "pageSize": str(page_size),
                "sortColumns": sort_columns,
                "sortTypes": sort_types,
                "source": "WEB",
                "client": "WEB",
            },
            headers={"User-Agent": UA},
            timeout=15,
        )
        if r is None:
            return []
        # HTTP状态码检查
        if r.status_code != 200:
            _http_logger.error(f"{r.status_code} | {DATACENTER_URL} | {report_name} | {code}")
            return []
        try:
            d = r.json()
        except Exception as _json_err:
            _http_logger.error(
                f"JSONDecodeError | {DATACENTER_URL} | {report_name} | {code} | {_json_err}"
            )
            return []
        # 业务错误码检查
        if isinstance(d, dict) and d.get("status") == -1:
            _biz_logger.error(f"status=-1 | {report_name} | {code} | {d.get('message', '')}")
            return []
        if d.get("result") and d["result"].get("data"):
            return d["result"]["data"]
        return []
    except Exception as _e:
        _debug_log(f"eastmoney_datacenter({code}, {report_name}): {_e}")
        return []


def _em_filter(
    code: str,
    report_name: str,
    extra_filter: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
) -> List[Dict[str, Any]]:
    """东财数据中心查询便捷包装（自动拼接 SECURITY_CODE）。"""
    return eastmoney_datacenter(
        code,
        report_name,
        filter_str=f'(SECURITY_CODE="{code}"){extra_filter}' if extra_filter else "",
        page_size=page_size,
        sort_columns=sort_columns,
        sort_types=sort_types,
    )


async def eastmoney_datacenter_async(
    session: Any,
    code: str,
    report_name: str,
    columns: str = "ALL",
    filter_str: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
) -> List[Dict[str, Any]]:
    """async 版：东财数据中心统一查询（datacenter-web.eastmoney.com）。

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    try:
        full_filter = filter_str if filter_str else f'(SECURITY_CODE="{code}")'
        d = await _async_request_with_retry(
            session,
            DATACENTER_URL,
            params={
                "reportName": report_name,
                "columns": columns,
                "filter": full_filter,
                "pageNumber": "1",
                "pageSize": str(page_size),
                "sortColumns": sort_columns,
                "sortTypes": sort_types,
                "source": "WEB",
                "client": "WEB",
            },
            headers={"User-Agent": UA},
            timeout=15,
        )
        if d is None:
            return []
        if isinstance(d, dict) and d.get("status") == -1:
            _biz_logger.error(f"status=-1 | {report_name} | {code} | {d.get('message', '')}")
            return []
        if d.get("result") and d["result"].get("data"):
            return d["result"]["data"]
        return []
    except Exception as _e:
        _debug_log(f"eastmoney_datacenter_async({code}, {report_name}): {_e}")
        return []


async def _em_filter_async(
    session: Any,
    code: str,
    report_name: str,
    extra_filter: str = "",
    page_size: int = 50,
    sort_columns: str = "",
    sort_types: str = "-1",
) -> List[Dict[str, Any]]:
    """async 版：东财数据中心查询便捷包装（自动拼接 SECURITY_CODE）。

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    return await eastmoney_datacenter_async(
        session,
        code,
        report_name,
        filter_str=f'(SECURITY_CODE="{code}"){extra_filter}' if extra_filter else "",
        page_size=page_size,
        sort_columns=sort_columns,
        sort_types=sort_types,
    )


def get_em_batch_quotes(codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """V12.0: 东财批量行情查询（替代TDX批量查询，修复URL超长Bug）。

    V17.0(2026-08-15): 改 push2delay 镜像域 + secids 参数(原 fs 返回 data:null);
    V17.0.1a(2026-08-16): 当日进程缓存——增量拉取缺失代码, 命中直接返回。
    """
    if not codes:
        return {}
    # V17.0.1a: 当日缓存命中直接返回(增量)
    global _EM_BATCH_CACHE, _EM_BATCH_CACHE_DATE
    from datetime import datetime as _dt2
    _today2 = _dt2.now().strftime("%Y%m%d")
    if _EM_BATCH_CACHE_DATE != _today2:
        _EM_BATCH_CACHE.clear()
        _EM_BATCH_CACHE_DATE = _today2
    _missing = [c for c in codes if c not in _EM_BATCH_CACHE]
    if not _missing:
        return {c: _EM_BATCH_CACHE[c] for c in codes if c in _EM_BATCH_CACHE}

    # 东财市场代码前缀: 沪市为 1., 深市为 0.
    sh_codes = [f"{em_secid_prefix(c)}{c}" for c in codes if em_secid_prefix(c) == "1."]
    sz_codes = [f"{em_secid_prefix(c)}{c}" for c in codes if em_secid_prefix(c) == "0."]  # V17.0 S3: 统一前缀
    all_formatted_codes = sh_codes + sz_codes

    result = {}

    @requires_push2
    def _fetch_batch(code_chunk):
        if not code_chunk:
            return
        fs_str = ",".join(code_chunk)
        # V17.0(2026-08-15 运行前核查): push2 主域连接级封禁期整体失败+0.4rps 限流
        # (17 chunk × 2.5s = 42.5s)——改 push2delay 镜像域(1.0rps 独立风控, 与采集 ulist239/人气榜先例一致);
        # 盘后/盘中延时 15 分钟对 mak 全景报告可接受
        url = "https://push2delay.eastmoney.com/api/qt/ulist.np/get"
        # V15.2 P0 修复: 增加 mcap_yi 字段（f20 总市值=f116/1e8, f21=f117 流通市值）
        # 之前只拉 f2/f3，导致 val 报告 18 步策略 mcap_yi=0
        # V16.1: 扩展字段包 — f55 EPS/f92 BPS/f126 股息率/f162-167 PE/PB/f174-175 52周高低/f221 报告期
        # V17.0(2026-08-15): + f62 主力净流入(ulist f62 ↔ push2 f137, 跨接口对撞 96.6%)
        # V17.0.16(2026-08-31): 去掉 f66 —— 旧代码误把 f62 当"特大单净"、f66 当"大单净"再相加，
        #   实证 f62 == f66 + f72 (236/236) 证明 f62 已是主力净(含超大单+大单)，相加属重复计数。
        params = {
            "fltt": "2",
            "invt": "2",
            "secids": fs_str,  # V17.0(2026-08-15 冒烟修复): ulist.np/get 参数为 secids(非 fs)——fs 返回 data:null
            "fields": (
                "f12,f14,f2,f3,f20,f21,"
                "f55,f92,f126,f162,f163,f167,f174,f175,f221,"
                "f62"  # V17.0.16: 只取 f62(主力净)；f66 已不再使用（见上方注释）
            ),
        }
        try:
            r = em_get(url, params=params, headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}, timeout=15)
            if r is None:
                return
            d = r.json()
            items = d.get("data", {}).get("diff", [])
            for item in items:
                code = str(item.get("f12", ""))
                name = str(item.get("f14", ""))
                price = _safe_float(item.get("f2", 0))
                change_pct = _safe_float(item.get("f3", 0))
                # V15.2 P0: mcap_yi (f20) 和 float_mcap_yi (f21)
                # V16.3 O17: ulist f20/f21 实测单位是**元**（茅台 1635794278989）——需 /1e8 转亿
                # （此前直接赋值导致批量路径 mcap 错 1e8 倍——canonical L3 单股路径无此问题）
                mcap_yi = _safe_float(item.get("f20", 0)) / 1e8
                float_mcap_yi = _safe_float(item.get("f21", 0)) / 1e8
                if code:
                    result[code] = {
                        "name": name,
                        "price": price,
                        "change_pct": change_pct,
                        "mcap_yi": mcap_yi,
                        "float_mcap_yi": float_mcap_yi,
                        # V16.1: 扩展字段（val 横截面初筛用）
                        "eps": _safe_float(item.get("f55", 0)),
                        "bps": _safe_float(item.get("f92", 0)),
                        "dividend_yield": _safe_float(item.get("f126", 0)),
                        "pe_dynamic": _safe_float(item.get("f162", 0)),
                        "pe_lyr": _safe_float(item.get("f163", 0)),
                        "pe_ttm": _safe_float(item.get("f164", 0)),
                        "pb": _safe_float(item.get("f167", 0)),
                        "high_52w": _safe_float(item.get("f174", 0)),
                        "low_52w": _safe_float(item.get("f175", 0)),
                        "report_period": str(item.get("f221", "")),
                        # V17.0.16(2026-08-31): 主力净流入(万元) = **f62 本身**，不再 + f66。
                        # 旧版按「主力 = f62 + f66」计算，与 stock/get 侧「f137 + f140」是同一个 bug。
                        # 实证（12 采集日 236 样本）：**f62 == f66 + f72 命中 236/236 = 100%**
                        #   → f62 = 主力净(已含超大单+大单)，f66 = 超大单净，f72 = 大单净。
                        # 再加 f66 即重复计一次超大单，虚高约 40%（与 push2 侧同量级）。
                        # 索引对齐仍然成立：ulist f62/f66/f72 ↔ push2 f137/f140/f143（跨接口对撞 96%+）。
                        "main_net_inflow_wan": _safe_float(item.get("f62", 0)) / 1e4,
                    }
        except RateLimitBlockedError:
            # M9 修复：EM 连续 403(IP 被封) 必须显性抛出，不能再被宽 except 吞成空数据
            # （否则"IP 被封"表现为空结果，且无任何失败信号上浮到 run()/main.py）。
            raise
        except Exception as _e:
            _debug_log(f"datasource get_em_batch_quotes error: {_e}")

    chunk_size = 300
    for i in range(0, len(all_formatted_codes), chunk_size):
        chunk = all_formatted_codes[i : i + chunk_size]
        _fetch_batch(chunk)

    for _c, _v in result.items():
        _EM_BATCH_CACHE[_c] = _v  # V17.0.1a: 写回当日缓存
    return result


@cached(
    category="kline",
    ttl_seconds=TTL["kline"],
    trading_day=True,
    # V17.0.17: 原函数返回 (keys, rows) 元组, 而 make_valid_if() 只拒空 dict/list/None,
    # 不拒空 tuple —— 瞬断返回的 ([],[]) 被当作有效结果写入缓存, 并以 trading_day TTL 冻结
    # 整整一个交易日, 致全仓 K线形态/CYQ(OHLC) 章节恒空。改为显式拒绝空 rows:
    # ① 未来瞬断不再缓存 ② 已存在的 stale [[],[]] 在读取时 valid_if 失败被当作 miss 重新拉取(自愈合)。
    valid_if=lambda r: isinstance(r, (tuple, list)) and len(r) == 2 and len(r[1] or []) > 0,
)
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


@requires_push2
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


@cached(category="northbound", ttl_seconds=TTL["northbound"])
def get_northbound_hold(code: str, days: int = 20) -> List[Dict[str, Any]]:
    """北向资金持仓动态（SKILL.md V3.2 增强：本地CSV缓存回退）。

    注意：东财北向资金数据自2024-08后部分字段可能返回NaN，本函数已添加本地CSV缓存回退。

    Args:
        code: 股票代码。
        days: 查询天数。

    Returns:
        list: [{date, hold_shares, market_cap, hold_ratio, change_shares, change_ratio}, ...]。
    """
    import os

    data = eastmoney_datacenter(
        code,
        "RPT_MUTUAL_HOLDSTOCKNORTH_STA",
        filter_str=f'(SECURITY_CODE="{code}")',
        page_size=days,
        sort_columns="TRADE_DATE",
        sort_types="-1",
    )

    rows = []
    has_valid_data = False
    for row in data:
        hold_shares = float(row.get("HOLD_SHARES") or 0)
        hold_ratio = float(
            row.get("FREE_SHARES_RATIO")
            or row.get("A_SHARES_RATIO")
            or row.get("TOTAL_SHARES_RATIO")
            or row.get("HOLD_RATIO")
            or 0
        )
        if hold_shares > 0 or hold_ratio > 0:
            has_valid_data = True

        rows.append(
            {
                "date": str(row.get("TRADE_DATE", "") or "")[:10],
                "hold_shares": hold_shares,
                "market_cap": float(row.get("HOLD_MARKET_CAP") or row.get("MARKET_CAP") or 0),
                "hold_ratio": hold_ratio,
                "change_shares": float(row.get("CHANGE_SHARES") or 0),
                "change_ratio": float(row.get("CHANGE_RATE") or 0),
            }
        )

    if not has_valid_data and len(rows) == 0:
        return _load_northbound_cache(code, days)

    return rows


def _northbound_cache_path(code: str) -> str:
    """北向资金本地CSV缓存路径"""
    import os

    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cache")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, f"northbound_{code}.csv")


def _load_northbound_cache(code: str, days: int) -> List[Dict[str, Any]]:
    """从本地CSV缓存加载北向资金数据"""
    import os

    path = _northbound_cache_path(code)
    rows = []
    if not os.path.exists(path):
        return rows

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[1:]:  # 跳过表头
                parts = line.strip().split(",")
                if len(parts) >= 6:
                    rows.append(
                        {
                            "date": parts[0],
                            "hold_shares": float(parts[1]),
                            "market_cap": float(parts[2]),
                            "hold_ratio": float(parts[3]),
                            "change_shares": float(parts[4]),
                            "change_ratio": float(parts[5]),
                        }
                    )
    except Exception as _e:
        _debug_log(f"datasource northbound cache load error: {_e}")

    return rows[-days:] if rows else rows


async def get_northbound_hold_async(
    session: Any, code: str, days: int = 20
) -> List[Dict[str, Any]]:
    """async 版: 北向资金持仓动态

    V9.4: 原生 aiohttp 实现，移除 asyncio.to_thread 包装。
    """
    import os

    data = await eastmoney_datacenter_async(
        session,
        code,
        "RPT_MUTUAL_HOLDSTOCKNORTH_STA",
        filter_str=f'(SECURITY_CODE="{code}")',
        page_size=days,
        sort_columns="TRADE_DATE",
        sort_types="-1",
    )

    rows = []
    has_valid_data = False
    for row in data:
        hold_shares = float(row.get("HOLD_SHARES") or 0)
        hold_ratio = float(
            row.get("FREE_SHARES_RATIO")
            or row.get("A_SHARES_RATIO")
            or row.get("TOTAL_SHARES_RATIO")
            or row.get("HOLD_RATIO")
            or 0
        )
        if hold_shares > 0 or hold_ratio > 0:
            has_valid_data = True

        rows.append(
            {
                "date": str(row.get("TRADE_DATE", "") or "")[:10],
                "hold_shares": hold_shares,
                "market_cap": float(row.get("HOLD_MARKET_CAP") or row.get("MARKET_CAP") or 0),
                "hold_ratio": hold_ratio,
                "change_shares": float(row.get("CHANGE_SHARES") or 0),
                "change_ratio": float(row.get("CHANGE_RATE") or 0),
            }
        )

    if not has_valid_data and len(rows) == 0:
        return _load_northbound_cache(code, days)

    return rows


def start_datacenter_prefetch(codes, session, dragon_kwargs=None) -> int:
    """调度五类 datacenter 数据的整批预取(幂等——已调度的 (kind,code) 跳过)。

    必须在事件循环内调用(execute_batch_pipeline 的 prefetch_async_fn 钩子)。
    消费侧用 resolve_datacenter('kind', code) 取结果; 未调度的键走调用方直调。

    Returns:
        本次新入队的 (kind, code) 项数
    """
    from ._financials import get_block_trade_async
    from ._financials import get_lockup_expiry_async
    from ._financials import get_margin_trading_async
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


@cached(category="stock_news", ttl_seconds=TTL["stock_news"])
def get_eastmoney_stock_news(code: str, page_size: int = 20) -> List[Dict[str, Any]]:
    """获取东财个股新闻。

    V9.6: 东财search-api-web HTTP接口已失效（返回passportWeb而非新闻），
    现仅使用 TDX F10 公司报道数据。F10不可用时返回空列表。

    Args:
        code: 股票代码
        page_size: 返回数量上限

    Returns:
        list: 新闻列表，包含标题、发布时间、来源、摘要等字段
    """
    try:
        from core.tdx_client import tdx_get_company_news_f10

        f10_news = tdx_get_company_news_f10(code, count=page_size)
        if f10_news:
            return [
                {
                    "title": n.get('title', ''),
                    "publish_time": n.get('date', ''),
                    "source": "F10",
                    "summary": n.get('summary', ''),
                    "url": n.get('url', ''),
                }
                for n in f10_news
            ]
    except Exception as _e:
        _debug_log(f"datasource tdx company news f10 error: {_e}")
    return []


@cached(category="global_news", ttl_seconds=TTL["global_news"])
def get_eastmoney_global_news(page_size: int = 50) -> List[Dict[str, Any]]:
    """获取东财全球资讯（7×24 滚动快讯）。

    使用东财np-weblist接口获取7×24财经快讯，与财联社快讯互为独立备份。

    Args:
        page_size: 返回数量上限

    Returns:
        list: 资讯列表，包含标题、发布时间、内容等字段
    """
    url = "https://np-weblist.eastmoney.com/comm/web/getFastNewsList"

    import uuid

    params = {
        "client": "web",
        "biz": "web_724",
        "fastColumn": "102",
        "sortEnd": "",
        "pageSize": str(page_size),
        "req_trace": str(uuid.uuid4()),
    }

    headers = {"User-Agent": UA, "Referer": "https://kuaixun.eastmoney.com/"}

    try:
        r = em_get(url, params=params, headers=headers, timeout=15)
        if r is None:
            return []

        d = r.json()
        items = d.get("data", {}).get("fastNewsList", [])

        news_items = []
        for item in items[:page_size]:
            news_items.append(
                {
                    "title": item.get("title", ""),
                    "publish_time": item.get("showTime", ""),
                    "content": item.get("summary", "")[:200],
                    "type": item.get("type", ""),
                }
            )

        return news_items
    except Exception as _e:
        _debug_log(f"datasource get_eastmoney_global_news: {_e}")
        return []


@cached(category="cash_flow", ttl_seconds=TTL["cash_flow"], cross_verify=True, trading_day=True, valid_if=make_valid_if())
def get_eastmoney_cash_flow(code: str) -> List[Dict[str, Any]]:
    """获取东财现金流量表（新浪xjllb接口已失效，使用东财数据中心替代）

    V9.6: 新增，使用东财数据中心RPT_CASHFLOW表获取现金流量数据。
    """
    data = eastmoney_datacenter(
        code,
        "RPT_CASHFLOW",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=5,
        sort_columns="REPORT_DATE",
        sort_types="-1",
    )
    if not data:
        return []

    rows = []
    for r in data:
        rows.append(
            {
                "报告日": str(r.get("REPORT_DATE", "") or "")[:10],
                "经营活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_OPERATING", "") or "0"),
                "投资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_INVESTING", "") or "0"),
                "筹资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_FINANCING", "") or "0"),
                "现金及现金等价物净增加额": str(r.get("NET_INCREASE_CASH_EQUIVALENTS", "") or "0"),
            }
        )
    return rows


async def get_eastmoney_cash_flow_async(session: Any, code: str) -> List[Dict[str, Any]]:
    """async 版: 东财现金流量表

    V9.6: 新增，使用东财数据中心RPT_CASHFLOW表获取现金流量数据。
    """
    data = await eastmoney_datacenter_async(
        session,
        code,
        "RPT_CASHFLOW",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=5,
        sort_columns="REPORT_DATE",
        sort_types="-1",
    )
    if not data:
        return []

    rows = []
    for r in data:
        rows.append(
            {
                "报告日": str(r.get("REPORT_DATE", "") or "")[:10],
                "经营活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_OPERATING", "") or "0"),
                "投资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_INVESTING", "") or "0"),
                "筹资活动产生的现金流量净额": str(r.get("NET_CASH_FLOW_FINANCING", "") or "0"),
                "现金及现金等价物净增加额": str(r.get("NET_INCREASE_CASH_EQUIVALENTS", "") or "0"),
            }
        )
    return rows


@cached(
    category="hsgt_macro_flow", ttl_seconds=TTL["hsgt_macro_flow"], trading_day=True, use_args=False,
    valid_if=lambda r: bool(r and r.get("data_quality") != "invalid"),
)
def get_hsgt_macro_flow() -> Optional[Dict[str, Any]]:
    """同花顺北向资金大盘净流入（宏观风向标）"""
    url = "https://data.hexin.cn/market/hsgtApi/method/dayChart/"
    headers = {"User-Agent": UA, "Host": "data.hexin.cn", "Referer": "https://data.hexin.cn/"}
    try:
        r = _quick_request(url, headers=headers, timeout=10)
        if r is None:
            return None
        d = r.json()
        hgt = d.get("hgt", [])
        sgt = d.get("sgt", [])
        if not hgt or not sgt:
            return None
        # V17.0.4(2026-08-19 实测): 同花顺接口字段错位——hgt=当日分时(262 点 09:10-15:00),
        # sgt=历史收盘序列(35 点), 长度不同步 → sgt[-1] 恒为陈旧值(8/12-8/19 冻结在 379.75,
        # 全仓 47 份 sht/med 报告北向恒 -9.28/+379.75 系此根因)。长度不一致即判 invalid 拒绝展示。
        if len(hgt) != len(sgt):
            # V17.0.28 (2026-09-02): 原实现一旦长度不等就把 hgt/sgt 一并归零 → 连有效的沪股通
            # 当日实时值也丢了(实测 hgt=262 点当日分时从头累积, 末值 -9.28 亿有效;
            # sgt=35 点历史收盘序列, 末值 379.75 陈旧)。改为:
            #   识别「hgt 为当日分时」(长度>100 且首值≈0 即从头累积) → hgt 单值可用,
            #   sgt 标记为缺失, data_quality="partial_hgt_only", 由渲染层只展示沪股通。
            # 识别失败仍走原 invalid 分支, 保证不展示错误数字。
            # 注意: 不能用 _safe_float(默认 0.0) 判首值 —— 非数字会返回 0.0 造成误判。
            _hgt_head_ok = False
            try:
                _hgt_head_ok = abs(float(hgt[0])) < 1e-6
            except (TypeError, ValueError, IndexError):
                _hgt_head_ok = False
            _hgt_is_intraday = len(hgt) > 100 and _hgt_head_ok
            if _hgt_is_intraday:
                _hgt_real = float(hgt[-1]) if hgt[-1] else 0.0
                _debug_log(
                    "hsgt_macro_flow: hgt/sgt 长度不一致({}/{})——hgt 判为当日分时(可用), sgt 为历史序列(不可用)".format(
                        len(hgt), len(sgt)))
                return {
                    "hgt": _hgt_real, "sgt": 0.0, "total": _hgt_real,
                    "sgt_valid": False,
                    "data_quality": "partial_hgt_only",
                    "warning": "深股通序列为历史收盘序列(非当日), 本项仅沪股通值可用",
                }
            _debug_log("hsgt_macro_flow: hgt/sgt 序列长度不一致({}/{})——数据源字段错位, 拒绝展示".format(len(hgt), len(sgt)))
            return {
                "hgt": 0.0, "sgt": 0.0, "total": 0.0,
                "data_quality": "invalid", "warning": "北向数据源 hgt/sgt 序列错位(字段长度不同步), 当日值暂缺",
            }
        hgt_val = float(hgt[-1]) if hgt[-1] else 0
        sgt_val = float(sgt[-1]) if sgt[-1] else 0

        data_quality = "normal"
        warning = ""
        if abs(hgt_val) > 0:
            ratio = abs(sgt_val / hgt_val)
            if ratio > 3.0:
                data_quality = "degraded"
                warning = f"sgt/hgt比例异常({ratio:.2f})，建议谨慎使用"
                _debug_log(f"hsgt_macro_flow warning: {warning}")

        return {
            "hgt": hgt_val,
            "sgt": sgt_val,
            "total": hgt_val + sgt_val,
            "data_quality": data_quality,
            "warning": warning,
        }
    except Exception as _e:
        _debug_log(f"datasource get_hsgt_macro_flow: {_e}")
        return None


async def get_hsgt_macro_flow_async(session: Any) -> Optional[Dict[str, Any]]:
    """async 版: 同花顺北向资金大盘净流入

    V11.2: 委托到同步缓存版本（trading_day=True），避免批量模式下所有股票共享同一份T-1数据。
    第一只股票触发API调用并写入缓存，后续股票直接读缓存。
    """
    import asyncio

    return await asyncio.to_thread(get_hsgt_macro_flow)


@cached(category="fund_flow", ttl_seconds=TTL["fund_flow"], trading_day=True)
@requires_push2
def get_board_fund_flow(board_type: str = "industry", top_n: int = 20) -> List[Dict[str, Any]]:
    """获取板块资金流向（行业/概念/地域板块的主力净流入排名）。

    V16.0 新增，参考 a-stock-data V3.5 `board_fund_flow`。
    2026-08-03 联网验证：83.push2 备用域名可用。
    注意：push2 有 IP 级风控，遇 RemoteDisconnected 需等待 30-60 分钟。

    ⚠️ 遗留(dead-code, 2026-09-01 战略重估标注): 经全仓 grep 确认本函数**未被 5 大脚本活跃路径调用**
    （mak 板块分析走 KPL RealRankingInfo + ZHB 聚合, 不调板块资金流排名）。保留供未来/外部使用, 勿在
    批量管线中新增调用以免触发东财 push2 连接级风控。

    Args:
        board_type: "industry"(行业 m:90 t:2) / "concept"(概念 m:90 t:3) / "area"(地域 m:90 t:1)
        top_n: 返回前 N 个板块

    Returns:
        [{code, name, change_pct, main_net_wan, super_net_wan, large_net_wan, medium_net_wan, small_net_wan, turnover}]
    """
    fs_map = {
        "industry": "m:90+t:2+f:!50",
        "concept": "m:90+t:3+f:!50",
        "area": "m:90+t:1+f:!50",
    }
    fs = fs_map.get(board_type, fs_map["industry"])
    # V16.3 O16: 翻页支持（参考仓库 v3.5.1）——先取首页拿真实 total，top_n>200 才翻页；
    # total 缺失按"不足一页即末页"收敛；提前返空即跳出防死循环。
    _PAGE = 200  # 东财 clist 单页上限
    params_tpl = {
        "po": "1", "np": "1", "fltt": "2", "invt": "2",
        "fs": fs,
        "fields": "f12,f14,f2,f3,f62,f66,f69,f72,f75,f184",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
    }

    def _fetch_page(pn: int, pz: int) -> dict:
        params = dict(params_tpl, pn=str(pn), pz=str(pz))
        try:
            r = _quick_request(
                "https://push2.eastmoney.com/api/qt/clist/get",
                params=params, headers={"User-Agent": UA}, timeout=10,
            )
            if r is None:
                # fallback: 备用域名（83.push2 实测可用）
                r = _quick_request(
                    "http://83.push2.eastmoney.com/api/qt/clist/get",
                    params=params, headers={"User-Agent": UA}, timeout=10,
                )
            if r is None:
                return {}
            d = r.json()
            return d.get("data") or {}
        except Exception as _e:
            _debug_log(f"datasource board_fund_flow page {pn}: {_e}")
            return {}

    try:
        data0 = _fetch_page(1, min(top_n, _PAGE))
        if not data0:
            return []
        total = data0.get("total")
        if isinstance(total, str):
            try:
                total = int(total)
            except ValueError:
                total = None
        diff0 = data0.get("diff") or []
        if isinstance(diff0, dict):
            diff0 = list(diff0.values())
        all_items = list(diff0)
        # 需要翻页：total 存在且 > 当前已取，且 top_n 超过单页
        need = top_n if total is None else min(top_n, total)
        while len(all_items) < need and len(diff0) > 0:
            pn = len(all_items) // _PAGE + 1
            data_n = _fetch_page(pn, _PAGE)
            diff_n = data_n.get("diff") or []
            if isinstance(diff_n, dict):
                diff_n = list(diff_n.values())
            if not diff_n:
                break  # 提前返空即末页（防死循环）
            all_items.extend(diff_n)
        out = []
        for item in all_items[:top_n]:
            out.append(
                {
                    "code": str(item.get("f12", "")),
                    "name": str(item.get("f14", "")),
                    "change_pct": _safe_float(item.get("f3", 0)),
                    "main_net_wan": _safe_float(item.get("f62", 0)) / 1e4,  # 元→万元
                    "super_net_wan": _safe_float(item.get("f66", 0)) / 1e4,
                    "large_net_wan": _safe_float(item.get("f69", 0)) / 1e4,
                    "medium_net_wan": _safe_float(item.get("f72", 0)) / 1e4,
                    "small_net_wan": _safe_float(item.get("f75", 0)) / 1e4,
                    "turnover": _safe_float(item.get("f184", 0)),
                }
            )
        return out
    except Exception as _e:
        _debug_log(f"datasource get_board_fund_flow: {_e}")
        return []


@cached(category="fund_flow", ttl_seconds=TTL["fund_flow"], trading_day=True)
@requires_push2
def get_eastmoney_minute_fund_flow(code: str) -> List[Dict[str, Any]]:
    """获取东财个股分钟级资金流数据

    V9.6 新增：使用东财push2接口获取分钟级资金流，用于与TDX资金流加权融合。
    数据格式与同花顺/百度资金流不同，但覆盖更稳定。

    ⚠️ 遗留(dead-code, 2026-09-01 战略重估标注): 经全仓 grep 确认**未被 5 大脚本活跃路径调用**
    （主力净额统一走 push2delay f137 口径, 弃用 easy_tdx 原生资金流——见 §12.15.5）。
    保留供未来/外部使用, 勿在批量管线中新增调用。

    Returns:
        分钟级资金流列表，每项包含时间/主力净流入/小单净流入/中单净流入/大单净流入
    """
    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    params = {
        "lmt": "0",
        "klt": "1",  # 1分钟
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
    }
    try:
        # V16.2.4: 多域轮换（分钟级延时域可能无窗口，失败时返回空由调用方降级）
        r = _em_fflow_request("/api/qt/stock/fflow/kline/get", params)
        if r is None:
            return []
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        if not klines:
            return []

        result = []
        for line in klines:
            parts = line.split(",")
            if len(parts) >= 11:
                result.append(
                    {
                        "time": parts[0],
                        "main_net_inflow": _safe_float(parts[1]),  # 主力净流入
                        "small_net_inflow": _safe_float(parts[2]),  # 小单净流入
                        "medium_net_inflow": _safe_float(parts[3]),  # 中单净流入
                        "large_net_inflow": _safe_float(parts[4]),  # 大单净流入
                        "super_net_inflow": _safe_float(parts[5]),  # 超大单净流入
                    }
                )
        return result
    except Exception as _e:
        _debug_log(f"datasource get_eastmoney_minute_fund_flow ({code}): {_e}")
        return []


def get_fund_flow_weighted(code: str, tdx_data: Any = None) -> Dict[str, Any]:
    """获取加权融合资金流数据（V9.6 新增）

    融合TDX、东财分钟级资金流，按权重加权计算：
    - TDX TCP资金流：权重 1.0（最实时、最准确）
    - 东财分钟级资金流：权重 0.6（覆盖稳定、数据量大）

    ⚠️ 遗留(dead-code, 2026-09-01 战略重估标注): 经全仓 grep 确认**未被 5 大脚本活跃路径调用**
    （主力净额统一走 push2delay f137 口径, 弃用 easy_tdx 原生资金流——见 §12.15.5）。
    保留供未来/外部使用, 勿在批量管线中新增调用。

    Args:
        code: 股票代码
        tdx_data: TDX资金流数据（如已获取，避免重复请求）

    Returns:
        加权融合后的资金流数据
    """
    # M18 清理：本函数为不完整实现（仅记录 source/权重/标记，未算加权融合值），
    # 且全仓无调用方（仅 stock_common.__init__ 转发），属死代码。保留签名以避免
    # 外部意外 import 缺失，但明确标记不再使用；如需加权资金流请直接用
    # get_em_fund_flow / tdx_get_fund_flow。
    _debug_log(f"get_fund_flow_weighted 已废弃(无调用方): {code}")
    return {"primary_source": "none", "sources": {}, "deprecated": True}


def get_history_fund_flow_120d(code: str, days: int = 60, prefer: str = "auto") -> Dict[str, Any]:
    """V16.2.4 (D2): 统一 120 日资金流入口（消除 get_fund_flow_120d 在 sht/med 的双实现）。

    Args:
        code: 股票代码
        days: 天数（默认 60）
        prefer: "em"=东财直连（**推荐且为 sht/med 统一口径，2026-09-10 起**）；
                "tdx"=⚠️ 历史别名，勿再用：其调用的 tdx_get_history_fund_flow
                      自 V12.0 起已完全委托东财 HTTP，与本值同源同值，
                      却会多一次冗余二次调用并把 source 误标为 "tdx"；
                "auto"=同 "tdx"（保留仅为向后兼容）

    Returns:
        {"data": [dict(元)] 或 [], "error": str, "source": str}
        与 med/sht 原有 get_fund_flow_120d 返回结构完全一致。

    ⚠️ V17.0.13 资金流口径（easy_tdx #55，2026-08-30）：本项目主力净额统一走
    东财 push2 f137+f140 口径，**弃用 easy_tdx 原生资金流**（其 get_fund_flow
    基于 0x0fb5 逐笔聚合、按成交额分档，与东财/同花顺主力净流入不可比，重合度 ~14%）。
    下方 `tdx_get_history_fund_flow` 已委托东财 HTTP，最终仍归东财口径，安全；
    但若 future 改回原生 easy_tdx 资金流，须先评估口径差异，禁止直接当主力净额源。
    """
    def _norm_ff(data):
        """V16.3 O19: 强制归一为 dict 列表（单位元）——历史遗留 float 列表（万元）自动转 dict(元)。"""
        if data and isinstance(data[0], (int, float)):
            return [
                {
                    "date": "",
                    "main_net": v * 1e4,
                    "super_net": 0,
                    "large_net": 0,
                    "mid_net": 0,
                    "small_net": 0,
                }
                for v in data
            ]
        return data

    if prefer != "em":
        try:
            from core.tdx_client import tdx_get_history_fund_flow

            _tdx = tdx_get_history_fund_flow(code, days)
            if _tdx:
                return {"data": _norm_ff(_tdx), "error": "", "source": "tdx"}
        except Exception as _e:
            _debug_log(f"datasource get_history_fund_flow_120d tdx ({code}): {_e}")
    try:
        _em = get_em_history_fund_flow(code, days)
        if _em:
            return {"data": _norm_ff(_em), "error": "", "source": "eastmoney"}
    except Exception as _e:
        _debug_log(f"datasource get_history_fund_flow_120d em ({code}): {_e}")
    return {"data": [], "error": "资金流数据获取失败"}


def _em_l2_load_cached(_json, _os, _now) -> Optional[Dict[str, str]]:
    """读磁盘缓存（两级：code→二级名、name→成员）。返回 l2_map 或 None。"""
    _d = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    global _EM_L2_MEMBERS
    _mp = _os.path.join(_d, "cache", "em_industry_map_l2.json")
    _mb = _os.path.join(_d, "cache", "em_industry_members_l2.json")
    if not (_os.path.exists(_mp) and _os.path.exists(_mb)):
        return None
    try:
        if _now - _os.path.getmtime(_mp) > _EM_L2_TTL or _now - _os.path.getmtime(_mb) > _EM_L2_TTL:
            return None
        with open(_mp, encoding="utf-8") as _f:
            _m = _json.load(_f)
        with open(_mb, encoding="utf-8") as _f:
            _mbd = _json.load(_f)
        if isinstance(_m, dict) and isinstance(_mbd, dict):
            _EM_L2_MEMBERS = {k: list(v) for k, v in _mbd.items()}
            return _m
    except Exception as _e:
        _debug_log(f"datasource em_l2 cache read: {_e}")
    return None


@cached(category="news", ttl_seconds=TTL["news"])
def cls_telegraph(page_size: int = 50) -> List[Dict[str, Any]]:
    """财联社电报（全市场实时快讯）。v1 API + 本地签名，零 key。

    V9.6 新增：使用 cls.cn/v1/roll/get_roll_list，签名算法为 md5(sha1(按key字典序拼接的query串))。
    与东财7×24快讯互为独立备份（不同源、不同风控面）。

    Args:
        page_size: 返回条数，默认50条

    Returns:
        快讯列表，包含 title/content/time 字段
    """
    import hashlib
    from datetime import datetime

    params = {
        "appName": "CailianpressWeb",
        "os": "web",
        "sv": "7.7.5",
        "last_time": "",
        "refresh_type": "1",
        "rn": str(page_size),
    }
    qs = "&".join(f"{k}={params[k]}" for k in sorted(params))
    sign = hashlib.md5(hashlib.sha1(qs.encode()).hexdigest().encode()).hexdigest()
    url = f"https://www.cls.cn/v1/roll/get_roll_list?{qs}&sign={sign}"

    try:
        r = _quick_request(
            url, headers={"User-Agent": UA, "Referer": "https://www.cls.cn/"}, timeout=10
        )
        if r is None:
            return []
        d = r.json()
        if d.get("errno") != 0:
            _debug_log(f"cls_telegraph error: errno={d.get('errno')} errmsg={d.get('errmsg')}")
            return []

        rows = []
        for item in d.get("data", {}).get("roll_data", []) or []:
            ts = item.get("ctime")
            t = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else ""
            # V16.1: 保留 stock_list/subjects（供 sht 关联股票分析）
            stock_list = item.get("stock_list") or []
            subjects = item.get("subjects") or []
            rows.append(
                {
                    "title": item.get("title", "") or item.get("brie", ""),
                    "content": item.get("content", "") or item.get("brie", ""),
                    "time": t,
                    "level": item.get("level", ""),
                    "reading_num": item.get("reading_num", 0),
                    "stock_list": [
                        {
                            "code": str(s.get("StockID", "") or s.get("stock_code", "")),
                            "name": str(s.get("name", "") or s.get("stock_name", "")),
                            "pct": s.get("RiseRange"),
                        }
                        for s in stock_list
                        if isinstance(s, dict)
                    ],
                    "subjects": [
                        {
                            "id": s.get("subject_id"),
                            "name": s.get("subject_name", ""),
                        }
                        for s in subjects
                        if isinstance(s, dict)
                    ],
                }
            )
        return rows
    except Exception as _e:
        _debug_log(f"datasource cls_telegraph: {_e}")
        return []


def dragon_tiger_backup(trade_date: str) -> Dict[str, Any]:
    """龙虎榜官方备用源（东财被封时用）：上交所+深交所官方，零鉴权权威一手，含营业部席位。

    Args:
        trade_date: 交易日，格式 YYYY-MM-DD

    Returns:
        包含深交所结构化数据和上交所原始文件内容的字典
    """
    import urllib.request
    import ssl

    out = {"date": trade_date, "sse_raw": "", "szse": []}
    _ctx = ssl._create_unverified_context()

    # 深交所龙虎榜
    su = (
        "https://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON"
        f"&CATALOGID=1842_xxpl&TABKEY=tab1&txtStart={trade_date}&txtEnd={trade_date}&random=0.9"
    )
    try:
        req = urllib.request.Request(
            su,
            headers={
                "User-Agent": UA,
                "Referer": "https://www.szse.cn/disclosure/supervision/dealinfo/index.html",
            },
        )
        # V16.3 C1: 备胎源裸 urlopen 补节流（_DOMAIN_LIMITS 的 szse 域 3.0rps 不覆盖此直连路径）
        try:
            from stock_common.sc_network import _gen_wait_process_interval
            _gen_wait_process_interval()
        except Exception:
            pass
        # V16.3 O14: 备胎源强制直连（ProxyHandler({}) 忽略系统代理——GD 外全部直连）
        # V16.3 O22: OpenerDirector.open 不接受 context 关键字（原 TypeError 使备胎源永久失效）——
        # 自定义 SSL context 通过 HTTPSHandler 注入
        _opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            urllib.request.HTTPSHandler(context=_ctx),
        )
        with _opener.open(req, timeout=15) as r:
            d = json.loads(r.read())
        if isinstance(d, list) and d:
            for row in d[0].get("data", []):
                out["szse"].append(
                    {
                        "code": row.get("zqdm"),
                        "name": row.get("zqjc"),
                        "amount": row.get("cjje"),
                        "reason": row.get("plyy"),
                        "volume": row.get("cjsl"),
                        "note": row.get("bz"),
                    }
                )
    except Exception as _e:
        _debug_log(f"dragon_tiger_backup szse: {_e}")

    # 上交所龙虎榜（JSONP格式）
    eu = (
        "https://query.sse.com.cn/infodisplay/showTradePublicFile.do?"
        f"jsonCallBack=cb&isPagination=false&dateTx={trade_date}"
    )
    try:
        req = urllib.request.Request(
            eu,
            headers={
                "User-Agent": UA,
                "Referer": "https://www.sse.com.cn/disclosure/diclosure/public/",
            },
        )
        # V16.3 C1: 备胎源裸 urlopen 补节流
        try:
            from stock_common.sc_network import _gen_wait_process_interval
            _gen_wait_process_interval()
        except Exception:
            pass
        # V16.3 O14: 强制直连（忽略系统代理）
        _opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with _opener.open(req, timeout=15) as r:
            t = r.read().decode("utf-8", "ignore")
        if "(" in t and ")" in t:
            json_str = t[t.index("(") + 1 : t.rindex(")")]
            d = json.loads(json_str)
            out["sse_raw"] = "\n".join(d.get("fileContents", []))
    except Exception as _e:
        _debug_log(f"dragon_tiger_backup sse: {_e}")

    return out


def fund_flow_backup(code: str, days: int = 60) -> List[Dict[str, Any]]:
    """个股资金流备用源（东财被封时用）：新浪，日度四档单净额。

    Args:
        code: 股票代码
        days: 获取天数，默认60天

    Returns:
        资金流列表，包含日期、主力/大单/中单/小单净流入
    """
    # V16.3 O16: 北交所 920/8/4 号段走 bj 前缀（此 URL 当前未用 prefix，保留统一口径）
    prefix = em_exchange_prefix(code)  # V17.2.11: 收敛散点 startswith("6") 路由
    url = (
        "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/MoneyFlow.ssl_bkzj_bk"
    )
    params = {"page": "1", "num": str(days), "sort": "netamount", "asc": "0", "fenlei": "1"}

    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return []
        d = r.json()
        if isinstance(d, list):
            return d
        return []
    except Exception as _e:
        _debug_log(f"datasource fund_flow_backup ({code}): {_e}")
        return []


@cached(
    category="dragon_tiger",
    ttl_seconds=TTL["dragon_tiger"],
    trading_day=True,
    valid_if=make_valid_if(min_size=1),
)  # V15.2: 至少 1 条记录才缓存
def get_dragon_tiger_board(
    code: str, days: int = 30, include_seats: bool = True, enhance_seats: bool = True
) -> Dict[str, Any]:
    """V7.5: 统一龙虎榜查询（单只股票）。

    V8.5新增：enhance_seats参数，启用后自动调用seat_db增强席位分析。
    V10.2修复：移除 today_str 参数（改为内部自动计算），避免跨日缓存 key 污染。

    Args:
        code: 6位股票代码
        days: 回溯天数（sht默认30，med默认180）
        include_seats: 是否查询席位详情（默认True，设为False可减少2次API请求）
        enhance_seats: V8.5新增，是否增强席位分析（默认True，添加席位等级/风格/溢价信号）

    Returns:
        {
          "records": [{date, reason, net_buy, turnover}, ...],
          "seats": {"buy": [{name, buy_amt, sell_amt, net}, ...], "sell": [...]},
          "institution": {"buy_amt", "sell_amt", "net_amt"},
          "net_sum_5d": float,        # V7.5新增：近5日净额累加
          "net_sum_30d": float,       # V7.5新增：近30日（或days）净额累加
          "consecutive_net_buy_days": int,  # V7.5新增：连续净买入天数
          "seat_analysis": {...},     # V8.5新增：enhance_seats=True时返回
        }

    注意 (2026-06-16): 东财 datacenter API 日期字段过滤必须用单引号
    (`TRADE_DATE>='YYYY-MM-DD'`），双引号会报 code=9501。
    """
    # V10.2: today_str 内部自动计算，不作为函数参数（避免污染缓存 key）
    today_str = datetime.now().strftime("%Y-%m-%d")
    start_str = (datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=days)).strftime(
        "%Y-%m-%d"
    )
    records = []
    data = eastmoney_datacenter(
        code,
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{start_str}')(TRADE_DATE<='{today_str}')",
        page_size=50,
        sort_columns="TRADE_DATE",
        sort_types="-1",
    )
    for row in data:
        rec = {
            "date": str(row.get("TRADE_DATE", "") or "")[:10],
            "reason": row.get("EXPLANATION", ""),
            "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
            "turnover": round(_safe_float(row.get("TURNOVERRATE")), 2),
        }
        # V16.1: 保留高价值字段（sht 用：买卖占比/分析文本/偏离度）
        if row.get("EXPLAIN"):
            rec["explain"] = row["EXPLAIN"]
        if row.get("BUY_RATIO") is not None:
            rec["buy_ratio"] = round(_safe_float(row.get("BUY_RATIO")), 2)
        if row.get("SELL_RATIO") is not None:
            rec["sell_ratio"] = round(_safe_float(row.get("SELL_RATIO")), 2)
        if row.get("DEAL_NET_RATIO") is not None:
            rec["net_ratio"] = round(_safe_float(row.get("DEAL_NET_RATIO")), 2)
        if row.get("ACCUM_AMOUNT") is not None:
            rec["accum_amount"] = _safe_float(row.get("ACCUM_AMOUNT"))
        if row.get("FREE_MARKET_CAP") is not None:
            rec["free_market_cap"] = _safe_float(row.get("FREE_MARKET_CAP"))
        # D1-D5 涨跌偏离度（龙虎榜判定依据）
        for _dn in ("D1", "D2", "D5", "D10", "D20", "D30"):
            _k = f"{_dn}_CLOSE_ADJCHRATE"
            if row.get(_k) is not None:
                rec[f"dev_{_dn.lower()}"] = round(_safe_float(row.get(_k)), 3)
        records.append(rec)

    seats: Dict[str, List[Any]] = {"buy": [], "sell": []}
    institution: Dict[str, float] = {"buy_amt": 0.0, "sell_amt": 0.0, "net_amt": 0.0}

    if records and include_seats:
        latest_date = records[0]["date"]
        # 买入/卖出席席：用最新上榜日期 + SECURITY_CODE 过滤（单引号日期）
        buy_data = eastmoney_datacenter(
            code,
            "RPT_BILLBOARD_DAILYDETAILSBUY",
            filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{latest_date}')(TRADE_DATE<='{latest_date}')",
            page_size=50,
            sort_columns="BUY",
            sort_types="-1",
        )
        for row in buy_data[:5]:
            seats["buy"].append(
                {
                    "name": row.get("OPERATEDEPT_NAME", ""),
                    "code": str(row.get("OPERATEDEPT_CODE", "")),
                    "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                    "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                    "net": round((row.get("NET") or 0) / 10000, 1),
                }
            )
        sell_data = eastmoney_datacenter(
            code,
            "RPT_BILLBOARD_DAILYDETAILSSELL",
            filter_str=f"(SECURITY_CODE=\"{code}\")(TRADE_DATE>='{latest_date}')(TRADE_DATE<='{latest_date}')",
            page_size=50,
            sort_columns="SELL",
            sort_types="-1",
        )
        for row in sell_data[:5]:
            seats["sell"].append(
                {
                    "name": row.get("OPERATEDEPT_NAME", ""),
                    "code": str(row.get("OPERATEDEPT_CODE", "")),
                    "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                    "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                    "net": round((row.get("NET") or 0) / 10000, 1),
                }
            )
        # V17.2.26: 机构专用席位（code == "0" 为机构专用）。
        # 买入额/卖出额须对【买入榜 + 卖出榜】全量明细求和——
        # 机构专用被归入卖榜时其买入列此前被漏算，导致 institution.buy_amt 归零(报告 3.1)。
        for row in list(buy_data) + list(sell_data):
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                institution["buy_amt"] += row.get("BUY") or 0
                institution["sell_amt"] += row.get("SELL") or 0
        institution["buy_amt"] = round(institution["buy_amt"] / 10000, 1)
        institution["sell_amt"] = round(institution["sell_amt"] / 10000, 1)
        institution["net_amt"] = round(institution["buy_amt"] - institution["sell_amt"], 1)

    # V7.5新增：主力净额连续性统计
    net_sum_5d = round(sum(r["net_buy"] for r in records[:5]), 1)
    net_sum_30d_or_days = round(sum(r["net_buy"] for r in records), 1)
    consecutive_net_buy_days = sum(1 for r in records if r["net_buy"] > 0)

    result = {
        "records": records,
        "seats": seats,
        "institution": institution,
        "net_sum_5d": net_sum_5d,
        "net_sum_30d": net_sum_30d_or_days,
        "consecutive_net_buy_days": consecutive_net_buy_days,
    }

    # V8.5新增：席位增强分析
    if enhance_seats and (seats.get("buy") or seats.get("sell")):
        try:
            from stock_common.seat_db import enhance_lhb_seats

            result["seat_analysis"] = enhance_lhb_seats({"seats": seats})
        except ImportError:
            pass

    return result


@cached(
    category="dragon_tiger",
    ttl_seconds=TTL["dragon_tiger"],
    trading_day=True,
    valid_if=make_valid_if(min_size=1),
)  # V15.2: 至少 1 条记录才缓存
def get_recent_dragon_tiger(days: int = 5) -> Dict[str, Any]:
    """V7.5: 全市场龙虎榜上榜记录（用于异动扫描和席位活跃度策略）。

    Returns:
        { stock_code: {name, reason, net_buy, turnover, date}, ... }

    注意 (2026-06-16): 东财 datacenter API 日期字段过滤必须用单引号
    (`TRADE_DATE>='YYYY-MM-DD'`），双引号会报 code=9501。
    """
    url = DATACENTER_URL
    try:
        td = datetime.now().strftime("%Y-%m-%d")
        sd = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        params = {
            "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
            "columns": "SECURITY_CODE,SECURITY_NAME_ABBR,TRADE_DATE,EXPLANATION,BILLBOARD_NET_AMT,TURNOVERRATE",
            "filter": f"(TRADE_DATE>='{sd}')(TRADE_DATE<='{td}')",
            "pageNumber": "1",
            "pageSize": "200",
            "sortColumns": "TRADE_DATE",
            "sortTypes": "-1",
            "source": "WEB",
            "client": "WEB",
        }
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None:
            return {}
        d = r.json()
        data = d.get("result", {}).get("data", []) or []
        result = {}
        for row in data:
            code = str(row.get("SECURITY_CODE", ""))
            if code not in result:
                result[code] = {
                    "name": row.get("SECURITY_NAME_ABBR", ""),
                    "reason": row.get("EXPLANATION", ""),
                    "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
                    "turnover": round(_safe_float(row.get("TURNOVERRATE")), 2),
                    "date": str(row.get("TRADE_DATE", "") or "")[:10],
                }
        return result
    except Exception as _e:
        _debug_log(f"datasource get_recent_dragon_tiger ({days}d): {_e}")
        return {}


async def get_dragon_tiger_board_async(
    session, code: str, days: int = 30, include_seats: bool = True, enhance_seats: bool = True
) -> Dict[str, Any]:
    """异步版: 单只股票龙虎榜查询（代理到同步版）。

    V10.2: 移除 today_str 参数（同步版已内部自动计算）。
    """
    return await asyncio.to_thread(get_dragon_tiger_board, code, days, include_seats, enhance_seats)


async def get_recent_dragon_tiger_async(session, days: int = 5) -> Dict[str, Any]:
    """异步版: 全市场龙虎榜上榜记录（代理到同步版）。"""
    return await asyncio.to_thread(get_recent_dragon_tiger, days)


@cached(category="basic_info", ttl_seconds=TTL["basic_info"], cross_verify=True)
@requires_push2
def eastmoney_stock_info_push2(code: str) -> Dict[str, Any]:
    """东财 push2 个股基本面信息（含上市日期 f189，不走 TDX）。

    当 TDX 无法获取 list_date 时作为 fallback。
    返回: {code, name, industry, total_shares, float_shares, mcap, float_mcap, list_date}
    """
    market_code = 1 if em_secid_prefix(code) == "1." else 0  # V17.0 S3: 统一(含北交所 92)
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "fltt": "2",
        "invt": "2",
        "fields": "f57,f58,f84,f85,f127,f116,f117,f189,f43",
        "secid": f"{market_code}.{code}",
    }
    headers = {"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
    try:
        r = em_get(url, params=params, headers=headers, timeout=10)
        if r is None:
            return {}
        d = r.json().get("data", {})
        return {
            "code": d.get("f57", ""),
            "name": d.get("f58", ""),
            "industry": d.get("f127", ""),
            "total_shares": d.get("f84", 0),
            "float_shares": d.get("f85", 0),
            "mcap": d.get("f116", 0),
            "float_mcap": d.get("f117", 0),
            "list_date": str(d.get("f189", "")),
            "price": d.get("f43", 0),
        }
    except Exception as _e:
        _debug_log(f"datasource eastmoney_stock_info_push2 ({code}): {_e}")
        return {}


def _em_fflow_request(path: str, params: Dict[str, Any], timeout: int = 10, prefer_his: bool = False):
    """V16.2.4: 依次尝试 _FFLOW_HOSTS，返回首个非 None 的 Response（含 403/429 语义由 em_get 处理）。
    V17.0.4(2026-08-19): prefer_his=True(历史资金流) → push2his 全窗口优先——
    原顺序 push2delay 第 1(为 lmt=1 实时设计) 会把 daykline 历史请求截断成单日(8/18 全仓 sht 60日资金流仅 1 天根因)。
    """
    import random as _rand

    _hosts = list(_FFLOW_HOSTS)
    if prefer_his:
        _his = "push2his.eastmoney.com"
        _hosts = [_his] + [h for h in _hosts if h != _his]
    else:
        _rand.shuffle(_hosts[0:2])  # 前两域随机轮换（防固定域持续触发风控）
    for _h in _hosts:
        try:
            _r = em_get(f"https://{_h}{path}", params=params, headers={"User-Agent": UA}, timeout=timeout)
            if _r is not None:
                return _r
        except Exception as _e:
            _debug_log(f"datasource fflow host {_h} error: {type(_e).__name__} {str(_e)[:60]}")
    return None


@requires_push2
def get_em_fund_flow(code: str) -> Dict[str, Any]:
    """V12.0: 获取个股实时资金流（替代 TDX get_fund_flow）。

    ⚠️ V17.0.13 口径（easy_tdx #55，2026-08-30）：本项目主力净额统一用东财
    fflow 口径（与 push2 f137+f140 一致）。**严禁**改用 easy_tdx 原生
    get_fund_flow（0x0fb5 逐笔聚合，与东财/同花顺主力净流入重合度仅 ~14%，不可比）。

    使用东财 fflow daykline 接口，取最新一天的数据（即当日实时累计）。
    V16.2.4 修复: push2/push2his 域连接级风控时自动切 push2delay 延时镜像域
    （延时 15 分钟，盘后一致；风控面独立）。

    Returns:
        dict: {"main_net": float, "main_net_wan": float, "total_net": float,
               "super_in": float, "super_out": float,
               "large_in": float, "large_out": float,
               "medium_in": float, "medium_out": float,
               "small_in": float, "small_out": float}
    """
    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    params = {
        "lmt": "1",  # 只取最新一天
        "klt": "101",  # 日K线
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
    }
    try:
        r = _em_fflow_request("/api/qt/stock/fflow/daykline/get", params)
        if r is None:
            return {}
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        if not klines:
            return {}
        # klines 格式: "日期,主力净流入,小单净流入,中单净流入,大单净流入,超大单净流入"
        parts = klines[-1].split(",")
        if len(parts) < 6:
            return {}
        main_net = _safe_float(parts[1])
        small_net = _safe_float(parts[2])
        medium_net = _safe_float(parts[3])
        large_net = _safe_float(parts[4])
        super_net = _safe_float(parts[5])
        # 东财返回净额，TDX格式需要 in/out 分开
        # 转换规则：净额>0时in=净额,out=0；净额<0时in=0,out=|净额|
        return {
            "main_net": main_net,
            "main_net_wan": main_net / 10000.0,
            # 东财定义"主力净流入 = 大单净流入 + 超大单净流入"(见本函数 klines 格式注释)，
            # 故 total_net 应为主力+小单+中单，大单/超大单已被主力包含；原五档全加会把大/超重复计。
            # （原 V16.2 注释"漏大单/超大单"为误解，2026-08-30 修；如需实盘复核：
            # 取任一标的对比 main_net 与 large_net+super_net 是否相等）
            "total_net": main_net + small_net + medium_net,
            "super_in": max(super_net, 0),
            "super_out": max(-super_net, 0),
            "large_in": max(large_net, 0),
            "large_out": max(-large_net, 0),
            "medium_in": max(medium_net, 0),
            "medium_out": max(-medium_net, 0),
            "small_in": max(small_net, 0),
            "small_out": max(-small_net, 0),
        }
    except Exception as _e:
        _debug_log(f"datasource get_em_fund_flow ({code}): {_e}")
        return {}


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
    # L3 主：新浪纯 JSON host（与字典 §12.2 一致，免正则剥壳；2026-09-12 由 jsonp 切换）
    try:
        r = _quick_request(
            "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData",
            params={"symbol": index_code, "scale": 240, "ma": 5, "datalen": days},
            headers={"User-Agent": UA,
                     "Referer": "https://finance.sina.com.cn"},
            timeout=10,
        )
        if r:
            _rows = _json.loads(r.text)
            closes = [_safe_float(x.get("close")) for x in _rows if x.get("close")]
            closes = [c for c in closes if c > 0]
            if closes:
                return closes
    except Exception as _e:
        _debug_log(f"datasource index_kline sina json error {index_code}: {_e}")
    # L3b 备：新浪 jsonp host（正则剥壳兜底，保持历史可用性）
    try:
        r = _quick_request(
            "https://quotes.sina.cn/cn/api/jsonp_v2.php/var/CN_MarketDataService.getKLineData",
            params={"symbol": index_code, "scale": 240, "ma": 5, "datalen": days},
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
        _debug_log(f"datasource index_kline sina jsonp error {index_code}: {_e}")

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


@requires_push2
def get_em_history_fund_flow(code: str, days: int = 120) -> List[Dict[str, Any]]:
    """V12.0: 获取个股历史资金流（替代 TDX get_history_fund_flow）。

    ⚠️ V17.0.13 口径（easy_tdx #55，2026-08-30）：沿用东财 fflow 口径，与
    get_em_fund_flow / push2 f137+f140 一致。勿回退 easy_tdx 原生历史资金流
    （0x0fb5 逐笔聚合，与东财/同花顺主力净流入不可比）。

    使用东财 push2 fflow daykline 接口，取最近 N 天的日级数据。

    Args:
        code: 股票代码
        days: 返回天数

    Returns:
        list: [{"date": str, "main_net": float, "super_net": float,
                "large_net": float, "mid_net": float, "small_net": float}, ...]
    """
    secid = f"{em_secid_prefix(code)}{code}"  # V17.0 S3: 统一前缀(含北交所 92)

    params = {
        "lmt": str(max(days, 1)),
        "klt": "101",  # 日K线
        "secid": secid,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
    }
    try:
        # V16.2.4: 多域轮换（push2his 全窗口 → push2 → push2delay 单日保底）
        # V17.0.4(2026-08-19): prefer_his=True 历史资金流优先 push2his 全窗口
        # (原顺序 push2delay 第 1 会把历史请求截断成单日——8/18 全仓 60日资金流仅 1 天根因)
        r = _em_fflow_request("/api/qt/stock/fflow/daykline/get", params, prefer_his=True)
        if r is None:
            return []
        d = r.json()
        klines = d.get("data", {}).get("klines", [])
        if not klines:
            return []
        rows = []
        for line in klines:
            parts = line.split(",")
            if len(parts) < 6:
                continue
            main_net = _safe_float(parts[1])
            small_net = _safe_float(parts[2])
            medium_net = _safe_float(parts[3])
            large_net = _safe_float(parts[4])
            super_net = _safe_float(parts[5])
            date_str = str(parts[0])[:10]
            rows.append(
                {
                    "date": date_str,
                    "main_net": main_net,
                    "super_net": super_net,
                    "large_net": large_net,
                    "mid_net": medium_net,
                    "small_net": small_net,
                }
            )
        # 按日期降序（最新在前），与原 TDX 行为保持一致
        rows.sort(key=lambda x: x["date"], reverse=True)
        return rows
    except Exception as _e:
        _debug_log(f"datasource get_em_history_fund_flow ({code}): {_e}")
        return []


__all__ = [
    'DATACENTER_URL',
    'RateLimitBlockedError',
    'TTL',
    'UA',
    '_DC_PREFETCH_FUTURES',
    '_EM_BATCH_CACHE',
    '_EM_BATCH_CACHE_DATE',
    '_EM_L2_TTL',
    '_FFLOW_HOSTS',
    '_async_request_with_retry',
    '_biz_logger',
    '_debug_log',
    '_em_fflow_request',
    '_em_filter',
    '_em_filter_async',
    '_em_l2_load_cached',
    '_f',
    '_gen_wait_process_interval',
    '_http_logger',
    '_load_northbound_cache',
    '_northbound_cache_path',
    '_quick_request',
    '_safe_float',
    'asyncio',
    'baidu_kline_full',
    'cached',
    'cls_telegraph',
    'code',
    'datetime',
    'dragon_tiger_backup',
    'eastmoney_datacenter',
    'eastmoney_datacenter_async',
    'eastmoney_stock_info_push2',
    'em_exchange_prefix',
    'em_get',
    'em_secid_prefix',
    'fund_flow_backup',
    'get_board_fund_flow',
    'get_cyq_distribution',
    'get_dragon_tiger_board',
    'get_dragon_tiger_board_async',
    'get_eastmoney_cash_flow',
    'get_eastmoney_cash_flow_async',
    'get_eastmoney_global_news',
    'get_eastmoney_minute_fund_flow',
    'get_eastmoney_stock_news',
    'get_em_batch_quotes',
    'get_em_fund_flow',
    'get_em_history_fund_flow',
    'get_fund_flow_weighted',
    'get_history_fund_flow_120d',
    'get_hsgt_macro_flow',
    'get_hsgt_macro_flow_async',
    'get_index_kline_closes',
    'get_northbound_hold',
    'get_northbound_hold_async',
    'get_recent_dragon_tiger',
    'get_recent_dragon_tiger_async',
    'hashlib',
    'json',
    'make_valid_if',
    'os',
    're',
    'requires_push2',
    'resolve_datacenter',
    'start_datacenter_prefetch',
    'timedelta',
    'urllib',
    'uuid',
]

"""_pools.py — V17.2 拆包子模块（共享命名空间片段，由 __init__ 载入）

本文件现为独立可导入子模块（不再经 exec 注入）。
由 stock_common/sc_datasource/__init__.py 通过  显式 re-export 到包命名空间；
跨片段符号由各子模块函数体内的局部懒导入（from ._DEFINER import NAME）提供，
共享可变状态集中于 _shared.py（单实例）。
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import json
import re
from stock_common.sc_network import (
    UA,
    _debug_log,
    _em_wait_process_interval,
    _quick_request,
    requires_push2,
)
from stock_common.sc_utils import _safe_float, is_limit_down
from core.stock_cache import TTL, cached
from ._shared import _KPL_BASE, _KPL_HEADERS, _KPL_HIS, _KPL_HQ, _KPL_LAST_CALL, _KPL_LHB
from stock_common.sc_kpl import _f, get_kpl_broken_ratio, get_kpl_market_sentiment
from stock_common.stock_calendar import get_last_trading_day


def _parse_limit_pool(data: list) -> List[Dict[str, Any]]:
    """解析东财 push2ex 涨停池/炸板池/跌停池数据"""
    result = []
    for item in data:
        zttj = item.get("zttj", {})
        result.append(
            {
                "code": item.get("c", ""),
                "name": item.get("n", ""),
                "price": _safe_float(item.get("p")),
                "change_pct": _safe_float(item.get("zdp")),
                "amount": _safe_float(item.get("amount")),
                "circulating_value": _safe_float(item.get("ltsz")),
                "total_value": _safe_float(item.get("tshare")),
                "turnover_rate": _safe_float(item.get("hs")),
                "limit_count": _safe_float(item.get("lbc")),
                "first_limit_time": str(item.get("fbt", "")),
                "last_limit_time": str(item.get("lbt", "")),
                "limit_fund": _safe_float(item.get("fund")),
                "broken_count": _safe_float(item.get("zbc")),
                "sector": item.get("hybk", ""),
                "zt_days": _safe_float(zttj.get("days")) if isinstance(zttj, dict) else 0,
                "zt_continuous": _safe_float(zttj.get("ct")) if isinstance(zttj, dict) else 0,
            }
        )
    return result


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"], trading_day=True)
@requires_push2  # V16.0: push2ex 与东财共用风控面，标记审计
def get_limit_up_pool(date_str: str = "") -> List[Dict[str, Any]]:
    """获取东财涨停池数据

    Args:
        date_str: 日期字符串，格式 YYYYMMDD，默认当天

    Returns:
        涨停股票列表，包含代码/名称/封板时间/连板数/涨停原因等
    """
    if not date_str:
        from datetime import datetime

        date_str = datetime.now().strftime("%Y%m%d")

    url = "https://push2ex.eastmoney.com/getTopicZTPool"
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
            return []
        d = r.json()
        pool = d.get("data", {}).get("pool", [])
        return _parse_limit_pool(pool)
    except Exception as _e:
        _debug_log(f"datasource get_limit_up_pool: {_e}")
        return []


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"], trading_day=True)
@requires_push2  # V16.0: push2ex 与东财共用风控面，标记审计
def get_limit_broken_pool(date_str: str = "") -> List[Dict[str, Any]]:
    """获取东财炸板池数据

    Args:
        date_str: 日期字符串，格式 YYYYMMDD，默认当天

    Returns:
        炸板股票列表
    """
    if not date_str:
        from datetime import datetime

        date_str = datetime.now().strftime("%Y%m%d")

    url = "https://push2ex.eastmoney.com/getTopicZBPool"
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
            return []
        d = r.json()
        pool = d.get("data", {}).get("pool", [])
        return _parse_limit_pool(pool)
    except Exception as _e:
        _debug_log(f"datasource get_limit_broken_pool: {_e}")
        return []


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"], trading_day=True)
@requires_push2  # V16.0: push2ex 与东财共用风控面，标记审计
def get_limit_down_pool(date_str: str = "") -> List[Dict[str, Any]]:
    """获取东财跌停池数据

    Args:
        date_str: 日期字符串，格式 YYYYMMDD，默认当天

    Returns:
        跌停股票列表
    """
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
            return []
        d = r.json()
        pool = d.get("data", {}).get("pool", [])
        return _parse_limit_pool(pool)
    except Exception as _e:
        _debug_log(f"datasource get_limit_down_pool: {_e}")
        return []


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"], trading_day=True)
@requires_push2  # V16.0: push2ex 与东财共用风控面，标记审计
def get_yesterday_limit_pool(date_str: str = "") -> List[Dict[str, Any]]:
    """V16.1: 东财昨日涨停池（getYesterdayZTPool）— 昨涨停今表现。

    用于计算晋级率/赚钱效应（sht/mak 打板情绪）。

    Args:
        date_str: 日期字符串，格式 YYYYMMDD，默认当天（昨涨停池按当日接口返回昨日涨停股今日表现）

    Returns:
        列表，每项含:
            code/name/price/change_pct(今日涨幅)/turnover_rate/amplitude_pct(振幅)/
            speed(涨速)/y_first_seal(昨封板时间)/y_limit_count(昨连板数)/
            sector(行业)/zt_days/zt_continuous(N天M板)
    """
    if not date_str:
        from datetime import datetime

        date_str = datetime.now().strftime("%Y%m%d")

    url = "https://push2ex.eastmoney.com/getYesterdayZTPool"
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
            return []
        d = r.json()
        pool = d.get("data", {}).get("pool", [])
        result = []
        for item in pool:
            zttj = item.get("zttj", {}) or {}
            result.append(
                {
                    "code": item.get("c", ""),
                    "name": item.get("n", ""),
                    "price": _safe_float(item.get("p")),
                    "change_pct": _safe_float(item.get("zdp")),  # 今日涨幅
                    "turnover_rate": _safe_float(item.get("hs")),
                    "amplitude_pct": _safe_float(item.get("zf")),  # 振幅
                    "speed": _safe_float(item.get("zs")),  # 涨速
                    "y_first_seal": str(item.get("yfbt", "")),  # 昨封板时间
                    "y_limit_count": _safe_float(item.get("ylbc")),  # 昨连板数
                    "sector": item.get("hybk", ""),
                    "zt_days": _safe_float(zttj.get("days")) if isinstance(zttj, dict) else 0,
                    "zt_continuous": _safe_float(zttj.get("ct")) if isinstance(zttj, dict) else 0,
                }
            )
        return result
    except Exception as _e:
        _debug_log(f"datasource get_yesterday_limit_pool: {_e}")
        return []


@cached(
    category="limit_pool_v2",
    ttl_seconds=TTL["limit_pool"],
    trading_day=True,
    valid_if=lambda r: bool(
        r
        and isinstance(r, dict)
        and (
            (r.get("limit_up_count") or 0) > 0
            or (r.get("limit_down_count") or 0) > 0
            or (r.get("limit_broken_count") or 0) > 0
        )
    ),
)
@requires_push2  # V17.0.1g: 涨停池同花顺优先, 炸板/跌停池仍走 push2ex → 保留审计
def get_limit_pool_summary(date_str: str = "") -> Dict[str, Any]:
    """获取打板数据汇总（涨停池+炸板池+跌停池）

    V17.0.1g(2026-08-16): 涨停池改**同花顺优先**（10jqka 官方 dataapi, 字段更丰富:
    涨停原因/板型/封板率/炸板次数; 与东财 push2ex 62 vs 63 只仅差北交所口径）;
    同花顺无 sector 字段 → 用 TDX 本机 tdxhy 行业注入（零网络, 权威一级行业）;
    失败兜底东财 push2ex。炸板池/跌停池无同花顺替代, 保持东财 push2ex（用户已确认）.

    Returns:
        包含涨停/炸板/跌停数量和详细数据的字典
    """
    from ._industry import _tdxhy_industry_map
    from ._zhb import get_zhb_data_date
    from ._zhb import get_zhb_full_market_snapshot

    # 涨停池: 同花顺优先(2026-08-16 实测 62 只/1.01s), 东财兜底。
    # 若两者都返回空池，使用财联社/KPL/复盘啦的多源计数兜底；计数可用时
    # 不能再把全市场涨停显示为 0，但因多源接口只提供计数，明细仍保持为空。
    zt = ths_limit_up_pool(date_str)
    zt_source = "ths"
    _zt_count_override: Optional[int] = None
    if not zt:
        zt = get_limit_up_pool(date_str)
        zt_source = "em"
    if not zt:
        try:
            _multi = get_limit_pool_multi_source(date_str or None)
            _multi_total = _multi.get("total") if isinstance(_multi, dict) else None
            if isinstance(_multi_total, int) and _multi_total > 0:
                _zt_count_override = _multi_total
                zt_source = "multi"
                _debug_log(
                    f"get_limit_pool_summary limit-up count fallback: multi_source={_multi_total}, detail unavailable"
                )
        except Exception as _e_multi:
            _debug_log(f"get_limit_pool_summary multi-source fallback: {_e_multi}")
    # H1(审查 2026-08-16): 休市日 ths 内部回退最近交易日, 炸板/跌停池若仍用当天(空) →
    # 封板率 100% 假象。统一口径: 回退后日期传给东财炸板/跌停池(东财对历史日期也有效)
    _zt_date = ""
    if zt_source == "ths":
        try:
            _zt_date = get_last_trading_day().strftime("%Y%m%d")
        except Exception:
            _zt_date = ""
    # 同花顺源无 sector → TDX 本机 tdxhy 一级行业注入(零网络)
    if zt_source == "ths" and zt:
        try:
            _ind_map = _tdxhy_industry_map()
            for item in zt:
                item["sector"] = _ind_map.get(item.get("code") or "", "") or ""
        except Exception as _e:
            _debug_log(f"get_limit_pool_summary tdxhy sector inject: {_e}")
    zb = get_limit_broken_pool(_zt_date or date_str)
    dt = get_limit_down_pool(_zt_date or date_str)
    # V17.0.8(2026-08-26 报告核查): 修复跌停兜底——旧逻辑(ZHB 快照涨跌幅口径)在盘中读到
    # T-1(前一日) 快照, 把昨日跌停误报为今日(8/26 实测 22 假跌停, 真实=0)。
    # 权威顺序: ① 东财 getTopicDTPool tc 总数(pool 可能空但 tc>0) → ② KPL RiseFallAnalysis dt
    # (独立匿名源) → ③ ZHB 快照仅当数据日期==目标日期才允许(ZHB 盘中恒为 T-1)
    _dt_fb = None
    if not dt:
        try:
            from datetime import datetime as _dtm

            _target = _zt_date or date_str or _dtm.now().strftime("%Y%m%d")
            # ① push2ex tc 权威总数
            try:
                from stock_common.sc_datasource import _query_dt_pool_tc

                _dt_tc = _query_dt_pool_tc(_target)
                if _dt_tc is not None:
                    _dt_fb = _dt_tc
            except Exception as _e1:
                _debug_log(f"get_limit_pool_summary dt tc: {_e1}")
            # ② KPL 独立匿名源(交叉验证)
            if _dt_fb is None:
                try:
                    from stock_common.sc_kpl import get_kpl_broken_ratio

                    _kpl_rf = get_kpl_broken_ratio()
                    if (
                        _kpl_rf
                        and _kpl_rf.get("date")
                        == _target[:4] + "-" + _target[4:6] + "-" + _target[6:]
                    ):
                        _dt_fb = int(_kpl_rf.get("dt") or 0)
                except Exception as _e2:
                    _debug_log(f"get_limit_pool_summary kpl dt: {_e2}")
            # ③ ZHB 兜底: 仅当快照日期==目标日期(零网络最后手段)
            if _dt_fb is None:
                try:
                    from stock_common import is_limit_down

                    _zhb_date = get_zhb_data_date().replace("-", "")
                    if _zhb_date == _target:
                        _snap = get_zhb_full_market_snapshot() or {}
                        _dt_fb = sum(
                            1
                            for _c, _d in _snap.items()
                            if _d
                            and isinstance(_d, dict)
                            and is_limit_down(
                                _c,
                                str(_d.get("name", "") or ""),
                                _safe_float(_d.get("change_pct", 0)),
                            )
                        )
                    else:
                        _debug_log(
                            f"get_limit_pool_summary dt: zhb date {_zhb_date} != target {_target}, 跳过 T-1 误判兜底"
                        )
                except Exception as _e3:
                    _debug_log(f"get_limit_pool_summary zhb dt fallback: {_e3}")
            if _dt_fb is None:
                _dt_fb = 0
        except Exception as _e:
            _debug_log(f"get_limit_pool_summary dt fallback: {_e}")
            _dt_fb = 0

    # 按板块统计涨停分布(M4: 空 sector 归"其他", 不产生空键)
    sector_stats: Dict[str, int] = {}
    for item in zt:
        sec = item.get("sector") or "其他"
        sector_stats[sec] = sector_stats.get(sec, 0) + 1

    # 封板成功率：多源仅提供计数时，用互校涨停数作为分子；若炸板池可用，
    # 仍按“涨停 / (涨停 + 炸板)”计算，避免空明细把成功率伪造成 0%。
    _zt_count = _zt_count_override if _zt_count_override is not None else len(zt)
    total_attempt = _zt_count + len(zb)
    success_rate = _zt_count / total_attempt * 100 if total_attempt > 0 else 0

    return {
        "limit_up_count": _zt_count,
        "limit_broken_count": len(zb),
        "limit_down_count": len(dt) or _dt_fb,
        "success_rate": round(success_rate, 1),
        "sector_stats": dict(sorted(sector_stats.items(), key=lambda x: x[1], reverse=True)[:10]),
        "limit_up_list": zt,
        "limit_broken_list": zb,
        "limit_down_list": dt,
    }


@cached(category="limit_pool_v2", ttl_seconds=TTL["limit_pool"], trading_day=True)
def ths_limit_up_pool(date_str: str = "") -> List[Dict[str, Any]]:
    """同花顺涨停揭秘（涨停原因 + 封板质量增强源）。

    V9.6 新增：与东财涨停池互为补充，提供东财没有的字段：
    - 涨停原因题材（reason）
    - 板型（一字板/换手板/T字板）
    - 封板成功率（seal_rate）
    - 炸板次数（break_times）

    V17.0.1g(2026-08-16): 升格为涨停池**优先源**(同花顺优先, push2ex 兜底);
    空日期自动回退最近交易日(休市传当日返回空)。
    V17.0.1h(2026-08-16): 新增 7 字段(turnover_rate/currency_value/order_volume/
    last_time/change_tag/market_type/is_new——同一次请求已返回, 零额外压力);
    **缓存 category 升 limit_pool_v2**(旧 pickle 无新字段, 强制失效)。

    Args:
        date_str: 交易日，格式 YYYYMMDD

    Returns:
        涨停列表，包含 code/name/price/pct/reason/board_type/seal_rate 等字段
    """
    from datetime import datetime

    # V17.0.1g(2026-08-16): 休市日(周末/节假日)传当日返回空 → 自动回退最近交易日
    if not date_str:
        try:
            from stock_common.stock_calendar import get_last_trading_day, previous_trading_day

            date_str = get_last_trading_day().strftime("%Y%m%d")
        except Exception:
            date_str = datetime.now().strftime("%Y%m%d")
    url = "https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool"
    params = {
        "page": 1,
        "limit": 200,
        "field": "199112,10,9001,330323,330324,330325,9002,330329,133971,133970,1968584,3475914,9003,9004",
        "filter": "HS,GEM2STAR",
        "order_field": "330324",
        "order_type": "0",
        "date": date_str,
    }

    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return []
        info = (r.json().get("data") or {}).get("info", [])
        if not info:
            return []

        out = []
        for it in info:
            # V17.0.1g: high_days 中文文本("首板"/"2板"/"3板"...) → 连板数; 东财契约兼容
            _hd = str(it.get("high_days", "") or "")
            _lc = 1
            if _hd.endswith("板"):
                _n = _hd[:-1]
                if _n.isdigit():
                    try:
                        _lc = int(_n)
                    except (ValueError, TypeError):
                        _lc = 1

            # V17.0.1h: 附加字段(同一次请求已返回, 零额外压力)——打板质量/弹性/风险分层
            # M2(审查 2026-08-16): 时间戳可能为 "0"/None/非数字 → 0 或异常会输出 1970-01-01
            # 或整池吞错; 先 _safe_float 再判 >0(精度 <1s 无影响)
            def _fmt_ts(_v: Any) -> str:
                _f = _safe_float(_v)
                if _f > 0:
                    try:
                        return datetime.fromtimestamp(int(_f)).strftime("%H:%M:%S")
                    except (ValueError, OverflowError, OSError):
                        pass
                return ""

            _lbt = it.get("last_limit_up_time")
            out.append(
                {
                    "code": it.get("code"),
                    "name": it.get("name"),
                    "price": _safe_float(it.get("latest")),
                    "change_pct": _safe_float(it.get("change_rate")),
                    "reason": it.get("reason_type", ""),
                    "board_type": it.get("limit_up_type", ""),
                    "seal_rate": _safe_float(
                        it.get("limit_up_suc_rate")
                    ),  # 0-1 小数(实测全池 0-1, 1.0=完全封死)
                    "break_times": it.get("open_num") or 0,
                    "seal_amount": it.get("order_amount"),
                    "limit_fund": _safe_float(it.get("order_amount", 0)),  # 元, 东财契约同口径
                    "limit_count": _lc,
                    "zt_days": _lc,
                    "high_days": _hd,
                    "first_time": _fmt_ts(it.get("first_limit_up_time")),
                    "last_time": _fmt_ts(_lbt),
                    "is_again": it.get("is_again_limit"),
                    "turnover_rate": _safe_float(it.get("turnover_rate")),
                    "currency_value": _safe_float(it.get("currency_value")),  # 元
                    "order_volume": it.get("order_volume"),  # 股
                    "change_tag": it.get("change_tag", ""),
                    "market_type": it.get("market_type", ""),
                    "is_new": it.get("is_new"),
                }
            )
        return out
    except Exception as _e:
        _debug_log(f"datasource ths_limit_up_pool: {_e}")
        return []


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"], trading_day=True)
def em_stock_monitor(only_active: bool = True) -> List[Dict[str, Any]]:
    """获取交易所重点监控池（风险警示/重点监控名单）。

    V16.0 新增，参考 a-stock-data V3.6 `em_stock_monitor`。
    2026-08-03 联网验证：接口可用（实测 17 条）。

    Args:
        only_active: True=仅返回监控期内（VALIDATESTARTDATE~VALIDATEENDDATE）的标的

    Returns:
        [{code, name, market, start, end, link}]
        market: "SH"/"SZ"/"BJ"（注意 MARKET="B"=北交所，参考仓库实测 920575 *ST康乐）
    """
    url = "https://mobappconfig.securities.eastmoney.com/emcfg/stock_monitor.json"
    _mkt_map = {"1": "SH", "0": "SZ", "B": "BJ"}
    try:
        r = _quick_request(
            url,
            headers={"User-Agent": UA, "Referer": "https://vipmoney.eastmoney.com/"},
            timeout=15,
        )
        if r is None:
            return []
        rows = r.json()
        if not isinstance(rows, list):
            return []
        today = datetime.now().strftime("%Y-%m-%d")
        out = []
        for x in rows:
            start = str(x.get("VALIDATESTARTDATE", "") or "")
            end = str(x.get("VALIDATEENDDATE", "") or "")
            if only_active and not (start <= today <= end):
                continue
            raw_mkt = str(x.get("MARKET", "")).upper()
            out.append(
                {
                    "code": str(x.get("STKCODE", "")),
                    "name": str(x.get("STKNAME", "")),
                    "market": _mkt_map.get(raw_mkt, f"?{raw_mkt}"),
                    "start": start,
                    "end": end,
                    "link": str(x.get("LINK_URL", "") or ""),
                }
            )
        return out
    except Exception as _e:
        _debug_log(f"datasource em_stock_monitor: {_e}")
        return []


@cached(
    category="market_emotion_multi",
    ttl_seconds=TTL["market_emotion_multi"],
    trading_day=True,
    valid_if=lambda r: bool(
        r
        and isinstance(r, dict)
        and (
            (r.get("total") or 0) > 0
            or any(
                (v or 0) > 0
                for v in (r.get("sources") or {}).values()
                if isinstance(v, (int, float))
            )
        )
    ),
)
def get_limit_pool_multi_source(date: Optional[str] = None) -> Dict[str, Any]:
    """涨停池三源互校——财联社=KPL=复盘啦（2026-08-10 实测 99=99=99 三源一致）。

    源顺序（低风险优先）: 财联社 → KPL → 复盘啦 → push2ex(东财兜底)。
    每源 1 次调用（间隔 2s，失败自动跳过——不阻塞、不重复请求）。

    Args:
        date: 可选日期 YYYY-MM-DD（push2ex 历史；财联社/KPL/复盘啦用当日）

    Returns:
        dict: {
            "total": int,              # 涨停总数（多源一致值）
            "sources": {源: 数量},     # 各源实测值（None=源失败）
            "cross_verified": bool,    # ≥2 源一致
            "max_ladder": int,         # 最高连板
            "detail": dict,            # 复盘啦 StockList 全量等
        }
    """
    import time as _time
    from collections import Counter

    out: Dict[str, Any] = {"sources": {}, "cross_verified": False, "max_ladder": 0, "detail": {}}

    cls_n = None
    try:
        from stock_common import get_cls_market_emotion

        emo = get_cls_market_emotion() or {}
        try:
            cls_n = int(emo.get("up_ratio_num") or 0)
        except (ValueError, TypeError):
            cls_n = None
    except Exception as _e:
        _debug_log(f"multi_source cls: {_e}")
    out["sources"]["cls"] = cls_n
    _time.sleep(2.0)

    kpl_n = None
    try:
        from stock_common import get_kpl_market_sentiment

        sent = get_kpl_market_sentiment() or {}
        try:
            kpl_n = int(sent.get("ztjs") or 0)
        except (ValueError, TypeError):
            kpl_n = None
        try:
            out["max_ladder"] = max(out["max_ladder"], int(sent.get("lbgd") or 0))
        except (ValueError, TypeError):
            pass
    except Exception as _e:
        _debug_log(f"multi_source kpl: {_e}")
    out["sources"]["kpl"] = kpl_n
    _time.sleep(2.0)

    fupan_n = None
    fupan_list: List[Any] = []
    try:
        from levistock.stock.stock_fupanla_kph import get_zttt

        z = get_zttt() or {}
        sl = z.get("StockList") or []
        fupan_list = sl
        fupan_n = len(sl)
        for r in sl:
            if len(r) > 2:
                try:
                    out["max_ladder"] = max(out["max_ladder"], int(r[2]))
                except (ValueError, TypeError):
                    pass
    except Exception as _e:
        _debug_log(f"multi_source fupan: {_e}")
    out["sources"]["fupan"] = fupan_n
    out["detail"]["fupan_list"] = fupan_list[:200]
    _time.sleep(2.0)

    push2ex_n = None
    if cls_n is None and kpl_n is None and fupan_n is None:
        try:
            from stock_common import get_limit_up_pool

            pool = get_limit_up_pool(date or "") or []
            push2ex_n = len(pool)
        except Exception as _e:
            _debug_log(f"multi_source push2ex: {_e}")
    out["sources"]["push2ex"] = push2ex_n

    vals = [v for v in (cls_n, kpl_n, fupan_n, push2ex_n) if v is not None]
    if vals:
        cnt = Counter(vals)
        top_v, top_c = cnt.most_common(1)[0]
        if top_c >= 2:
            out["total"] = top_v
            out["cross_verified"] = True
        else:
            out["total"] = max(vals)
    else:
        out["total"] = 0

    return out


@cached(category="limit_pool", ttl_seconds=TTL["limit_pool"], trading_day=True)
def get_kph_limit_ladder(date_str: str = "") -> List[Dict[str, Any]]:
    """V16.1.7: 开盘红涨停天梯（字典 §12.10.4，实测 137 条）。

    返回: [{code/name/limit_count(连板)/limit_time/plate_name/
           one_word(大单一字)/popular(人气)/plate_limit_up_count/amount/plate_amount}]
    """
    try:
        import levistock as lk
        from datetime import timedelta

        # V16.2: 进程级节流（levistock 直连东财）
        try:
            from stock_common.sc_network import _em_wait_process_interval

            _em_wait_process_interval()
        except Exception:
            pass
        if not date_str:
            # V17.0.2g(2026-08-17): 开盘红复盘接口要求"已收盘交易日"(昨天或更早)——
            # 原 今天-1 在周一/节后运行取到休市日 → 接口空 → "涨停天梯获取失败"
            from stock_common.stock_calendar import get_last_trading_day, previous_trading_day
            from datetime import date as _date

            _ltd = get_last_trading_day()
            _d0 = _ltd if isinstance(_ltd, _date) else _ltd.date()
            # 最近交易日是今天(交易日盘中/盘前) → 回退到上一已收盘交易日
            if _d0 == _date.today():
                _d0 = previous_trading_day(_d0)
            date_str = _d0.strftime("%Y-%m-%d")
            # 接口可能尚未发布最近交易日数据 → 向前按交易日找首个有数据的日期。
            for _try in range(7):
                data = lk.get_zttt(date=date_str)
                _cnt = (
                    len(data.get("StockList") or []) if isinstance(data, dict) else len(data or [])
                )
                if _cnt > 0:
                    break
                _retry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                date_str = previous_trading_day(_retry_date).strftime("%Y-%m-%d")
            else:
                data = lk.get_zttt(date=date_str)
        else:
            data = lk.get_zttt(date=date_str)
        # levistock get_zttt 返回 dict: {"StockList": [...], "ZhuShuList": [...]}
        if isinstance(data, dict):
            data = data.get("StockList") or []
        if isinstance(data, list):
            rows = []
            for item in data:
                if isinstance(item, dict):
                    rows.append(item)
                elif isinstance(item, (list, tuple)) and len(item) >= 11:
                    # 开盘红 zttt 返回 list 索引: [0]code [1]name [2]连板 [3]时间戳 [4]板块码 [5]板块名 [6]大单一字 [7]人气 [8]板块涨停数 [9]个股额 [10]板块额
                    rows.append(
                        {
                            "code": item[0],
                            "name": item[1],
                            "limit_count": item[2],
                            "limit_time": item[3],
                            "plate_code": item[4],
                            "plate_name": item[5],
                            "one_word": item[6],
                            "popular": item[7],
                            "plate_limit_up_count": item[8],
                            "amount": item[9],
                            "plate_amount": item[10],
                        }
                    )
            return rows
    except Exception as _e:
        _debug_log(f"datasource get_kph_limit_ladder: {_e}")
    return []


def _kpl_post(
    url: str,
    action: str,
    controller: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Optional[Union[Dict[str, Any], List[Any]]]:
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
        r = _req_mod.post(url, data=body.encode("utf-8"), headers=dict(_KPL_HEADERS), timeout=15)
        if r.status_code != 200:
            return None
        txt = r.text
        cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", txt)
        d = json.loads(cleaned)
        ec = str(d.get("errcode", ""))
        if ec != "0":
            _debug_log(f"kpl {action}/{controller}: errcode={ec} {d.get('errmsg','')[:60]}")
            return None
        payload = d.get("data") or d
        if isinstance(payload, dict):
            return payload
        if isinstance(payload, list):
            return payload
        return None
    except Exception as e:
        _debug_log(f"kpl {action}/{controller}: {e}")
        return None


def kpl_get_market_emotion() -> Optional[Dict[str, Any]]:
    """市场情绪实时数据（涨停数/跌停数/强度/连板高度）。

    Returns:
        {"ztjs": 涨停数, "df_num": 跌停数, "strong": 强度,
         "lbgd": 连板高度, "Day": 日期}
    """
    result = _kpl_post(_KPL_HQ, "ChangeStatistics", "HomeDingPan")
    return result if isinstance(result, dict) else None


def kpl_get_rise_fall_analysis() -> Optional[List[Any]]:
    """涨跌分析 [涨停数,?,跌停数,?,涨跌比%,?,日期]。"""
    result = _kpl_post(_KPL_HQ, "RiseFallAnalysis", "HomeDingPan")
    return result if isinstance(result, list) else None


def kpl_get_stock_zd_num() -> Optional[Dict[str, Any]]:
    """涨跌家数。"""
    result = _kpl_post(_KPL_HQ, "MarketStockZDNum", "HomeDingPan")
    return result if isinstance(result, dict) else None


def kpl_get_real_ranking_info(date: str = "", index: int = 0) -> Optional[Dict[str, Any]]:
    """板块排行列表(30只/页, 19列含 code/name/strength/change_pct/speed/
    turnover/main_net/main_buy/main_sell/vol_ratio/circ_mv/big_order_net/
    total_mv/pe_today/pe_next 等)。"""
    result = _kpl_post(
        _KPL_HIS,
        "RealRankingInfo",
        "ZhiShuRanking",
        {
            "Type": "1",
            "ZSType": "7",
            "Index": str(index),
            "st": "30",
            "Date": date,
            "Order": "1",
        },
    )
    return result if isinstance(result, dict) else None


def kpl_get_stock_list_w8(
    plate_id: str, date: str = "", stock_type: int = 0
) -> Optional[Dict[str, Any]]:
    """板块成分股详情(63字段, 需遍历 Type 0~19 合并去重)。
    域名必须用 apphis.longhuvip.com；响应 key 是小写 list。"""
    result = _kpl_post(
        _KPL_HIS,
        "ZhiShuStockList_W8",
        "ZhiShuRanking",
        {
            "PlateID": plate_id,
            "Date": date,
            "Type": str(stock_type),
            "Index": "0",
            "st": "30",
            "Order": "1",
            "TSZB": "0",
            "IsZZ": "0",
            "TSZB_Type": "0",
            "filterType": "0",
            "old": "1",
        },
    )
    return result if isinstance(result, dict) else None


def kpl_get_ytfp_bkhx(date: str = "") -> Optional[Dict[str, Any]]:
    """复盘啦板块核心(涨停原因+题材+个股明细)。"""
    extra: Dict[str, Any] = {}
    if date:
        extra["Date"] = date
    result = _kpl_post(_KPL_HIS, "GetYTFP_BKHX", "FuPanLa", extra)
    return result if isinstance(result, dict) else None


def kpl_get_ytfp_sctd(date: str = "") -> Optional[Dict[str, Any]]:
    """复盘啦市场题材(几天几板 Tips，如'3天2板')。"""
    extra: Dict[str, Any] = {}
    if date:
        extra["Date"] = date
    result = _kpl_post(_KPL_HIS, "GetYTFP_SCTD", "FuPanLa", extra)
    return result if isinstance(result, dict) else None


def kpl_get_lhb_stock_list() -> Optional[Dict[str, Any]]:
    """龙虎榜股票列表。"""
    result = _kpl_post(_KPL_LHB, "GetStockList", "LongHuBang")
    return result if isinstance(result, dict) else None


def kpl_get_info() -> Optional[Dict[str, Any]]:
    """首页聚合(ErBanList/JJJYList/TKGKList)。"""
    extra = {"View": "1"}
    result = _kpl_post(_KPL_HQ, "GetInfo", "Index", extra)
    return result if isinstance(result, dict) else None


__all__ = [
    'TTL',
    'UA',
    '_KPL_BASE',
    '_KPL_HEADERS',
    '_KPL_HIS',
    '_KPL_HQ',
    '_KPL_LAST_CALL',
    '_KPL_LHB',
    '_debug_log',
    '_em_wait_process_interval',
    '_f',
    '_kpl_post',
    '_parse_limit_pool',
    '_quick_request',
    '_safe_float',
    'cached',
    'datetime',
    'em_stock_monitor',
    'get_kph_limit_ladder',
    'get_kpl_broken_ratio',
    'get_kpl_market_sentiment',
    'get_last_trading_day',
    'get_limit_broken_pool',
    'get_limit_down_pool',
    'get_limit_pool_multi_source',
    'get_limit_pool_summary',
    'get_limit_up_pool',
    'get_yesterday_limit_pool',
    'is_limit_down',
    'json',
    'kpl_get_info',
    'kpl_get_lhb_stock_list',
    'kpl_get_market_emotion',
    'kpl_get_real_ranking_info',
    'kpl_get_rise_fall_analysis',
    'kpl_get_stock_list_w8',
    'kpl_get_stock_zd_num',
    'kpl_get_ytfp_bkhx',
    'kpl_get_ytfp_sctd',
    're',
    'requires_push2',
    'ths_limit_up_pool',
    'timedelta',
]

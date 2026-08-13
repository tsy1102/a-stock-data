"""sc_kpl.py — 开盘啦 KPL 统一层适配器（V16.3 O35 新增，字典 §12.17/12.17.1）。

数据源：longhuvip.com 私有 API（Android UA）
- 匿名接口（无需 UserID/Token）：RiseFallAnalysis / MoodNumCount / ChangeStatistics /
  RealRankingInfo / DailyLimitPerformance
- Token 接口（可选，从 ths_credentials.json 同款 KPL_TOKEN/KPL_USER_ID 环境变量读）：
  MorningBiddingList（竞价涨停委买额——独有数据）

限流：实测匿名接口 1s 间隔安全；本适配器内置 QUERY_INTERVAL=0.6s（连接级限频）
缓存：@cached（market_emotion 5 分钟盘中 / plate_strength 1h——KPL 数据收盘后不变）

⚠️ 私有 API 风险：非官方公开，接口/字段可能变更；生产勿高依赖
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

# V16.3.3: KPL 情绪缓存（字典 12.15.5——mak A/B 段高频调用，KPL 收盘后不变）
# V17.0 S8: 删 _kpl_cached 适配器(与 _fuyao_cached 逐字重复)——直接使用规范 cached;
# core.stock_cache 是 sc_datasource 硬依赖, ImportError 分支属僵尸防御, 保留守卫结构。
try:
    from core.stock_cache import cached, TTL

    _HAS_CACHE = True
except ImportError:  # pragma: no cover
    _HAS_CACHE = False

_logger = logging.getLogger("sc_kpl")

# Android UA 必须（非 Dalvik 返回 errcode=0 但 List=[]）
_UA = "Dalvik/2.1.0 (Linux; U; Android 12; ALN-AL00 Build/W528JS)"
_QUERY_INTERVAL = 0.6

_HOSTS = {
    "hq": "https://apphq.longhuvip.com/w1/api/index.php",      # 实时
    "his": "https://apphis.longhuvip.com/w1/api/index.php",    # 历史
    "hwhq": "https://apphwhq.longhuvip.com/w1/api/index.php",  # 行情
    "shhq": "https://apphwshhq.longhuvip.com/w1/api/index.php",# 情绪
}

_last_request = 0.0
# V16.4.1: 节流时间戳加锁——多线程并发下原 0.6s 间隔被打穿(报告脚本 ThreadPoolExecutor 场景)
_throttle_lock = threading.Lock()


def _throttle():
    """连接级限频（0.6s/请求）。"""
    global _last_request
    with _throttle_lock:
        now = time.time()
        wait = _QUERY_INTERVAL - (now - _last_request)
        if wait > 0:
            time.sleep(wait)
        _last_request = time.time()


def _post(host: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """POST 请求（form 编码 + Dalvik UA）。"""
    _throttle()
    body = urllib.parse.urlencode(params, doseq=True).encode("utf-8")
    req = urllib.request.Request(_HOSTS[host], data=body, headers={
        "User-Agent": _UA,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Connection": "Keep-Alive",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8", errors="ignore"))
    except Exception as e:
        _logger.warning(f"kpl {host} {params.get('a')}: {e}")
        return {"_err": str(e)[:120]}


def _base() -> Dict[str, Any]:
    """基础参数（DeviceID 固定——匿名接口仅需此）。"""
    return {"PhoneOSNew": 1,
            "DeviceID": os.environ.get("KPL_DEVICE_ID", "d66474b3-fd78-3a95-a56d-76e29e765ea3"),
            "VerSion": "5.23.0.4", "apiv": "w44"}


@cached("kpl_sentiment", "kpl_sentiment", trading_day=True)
def get_kpl_market_sentiment() -> Dict[str, Any]:
    """KPL 市场情绪（ChangeStatistics）——情绪指标 strong(0-100)/连板高度/涨停家数。

    字典 §12.17：info=[ztjs 涨停家数, Day, df_num 大幅回撤, strong 情绪指标, lbgd 连板高度] + tip 提示
    交叉验证：8/7 strong=63/连板高度 4/涨停 74（与东财/财联社涨停池一致）
    """
    p = _base()
    p.update({"a": "ChangeStatistics", "st": 10, "c": "HomeDingPan"})
    d = _post("hq", p)
    if "_err" in d or d.get("errcode") != "0":
        return {}
    info = (d.get("info") or [{}])[0]
    return {
        "ztjs": int(info.get("ztjs") or 0),
        "df_num": int(info.get("df_num") or 0),
        "strong": int(info.get("strong") or 0),
        "lbgd": int(info.get("lbgd") or 0),
        "day": info.get("Day", ""),
        "tip": d.get("tip", ""),
    }


def get_kpl_up_down() -> Dict[str, Any]:
    """KPL 涨跌家数（MoodNumCount）——涨跌家数/涨停跌停/全市场量能。

    字典 §12.17：list={SZJS 上涨, XDJS 下跌, ZTJS 涨停, DTJS 跌停, qscln 全市场量能(万), q_zrcs 昨日, bl 破板率, color}
    """
    p = _base()
    p.update({"a": "MoodNumCount", "c": "MarketMood"})
    d = _post("shhq", p)
    if "_err" in d or d.get("errcode") != "0":
        return {}
    lst = d.get("list") or {}
    return {
        "rise_num": int(lst.get("SZJS") or 0),
        "fall_num": int(lst.get("XDJS") or 0),
        "zt_num": int(lst.get("ZTJS") or 0),
        "dt_num": int(lst.get("DTJS") or 0),
        "total_amount_wan": int(lst.get("qscln") or 0),  # 万
        "prev_amount_wan": int(lst.get("q_zrcs") or 0),
        "broken_ratio": float(lst.get("bl") or 0),
    }


def get_kpl_plate_strength(top_n: int = 20) -> List[Dict[str, Any]]:
    """KPL 精选板块强度（RealRankingInfo ZSType=7）——强度/涨幅/主力净额/今明 PE。

    字典 §12.17：list 19 元素数组：
      [0]=板块代码 [1]=名称 [2]=强度 [3]=涨幅 [4]=涨速 [5]=成交额 [6]=主力净额
      [7]=主买 [8]=主卖 [9]=量比 [10]=流通值 [12]=300万大单净额 [13]=总市值
      [14]=机构增仓 [15]=今PE [16]=明PE
    ⚠️ 非交易时间需 Date=YYYY-MM-DD
    """
    p = _base()
    p.update({"a": "RealRankingInfo", "Order": 1, "st": top_n, "Type": 1,
              "c": "ZhiShuRanking", "Index": 0, "ZSType": 7})
    d = _post("hq", p)
    if "_err" in d or d.get("errcode") != "0":
        return []
    out = []
    for row in d.get("list") or []:
        if len(row) < 17:
            continue
        out.append({
            "code": row[0], "name": row[1], "strength": _f(row[2]),
            "change_pct": _f(row[3]), "speed": _f(row[4]),
            "amount": _f(row[5]), "main_inflow": _f(row[6]),
            "main_buy": _f(row[7]), "main_sell": _f(row[8]),
            "vol_ratio": _f(row[9]), "circulation_value": _f(row[10]),
            "big_order_300w_net": _f(row[12]), "total_value": _f(row[13]),
            "institution_add": _f(row[14]),
            "pe_now": _f(row[15]), "pe_next": _f(row[16]),
        })
    return out


def get_kpl_limit_up_detail(pid_type: int = 1, date: Optional[str] = None) -> List[Dict[str, Any]]:
    """KPL 连板梯队（DailyLimitPerformance）——涨停股明细（涨停原因/封单/主力）。

    字典 §12.17：PidType=1 首板 / 2 二板 / 3 三板 / 4 四板 / 5 更高
    info=[代码, 名称, 0, "", 涨停时间, 涨停原因, 封单, 最大封单, 主力净额,
          主力买入, 主力卖出, 成交额, 板块, 实际流通, 实际换手, 1, 1, 振幅, "", 板块代码, 涨停数量]
    """
    p = _base()
    p.update({"a": "DailyLimitPerformance", "Order": 0, "st": 2000,
              "c": "HomeDingPan", "Index": 0, "PidType": pid_type, "Type": 4})
    if date:
        p["Day"] = date
    host = "his" if date else "hwhq"
    d = _post(host, p)
    if "_err" in d or d.get("errcode") != "0":
        return []
    out = []
    for grp in d.get("info") or []:
        # info 嵌套：[[[row1], [row2], ...]] —— 遍历全部行
        rows = grp if isinstance(grp, list) and grp and isinstance(grp[0], list) else [grp]
        for row in rows:
            if not isinstance(row, list) or len(row) < 14:
                continue
            out.append({
                "code": row[0], "name": row[1],
                "zt_time": row[4] if len(row) > 4 else None,
                "reason": row[5] if len(row) > 5 else "",
                "seal_amount": _f(row[6]) if len(row) > 6 else 0,
                "max_seal": _f(row[7]) if len(row) > 7 else 0,
                "main_inflow": _f(row[8]) if len(row) > 8 else 0,
                "main_buy": _f(row[9]) if len(row) > 9 else 0,
                "main_sell": _f(row[10]) if len(row) > 10 else 0,
                "amount": _f(row[11]) if len(row) > 11 else 0,
                "sector": row[12] if len(row) > 12 else "",
                "turnover_real": _f(row[14]) if len(row) > 14 else 0,
                "amplitude": _f(row[17]) if len(row) > 17 else 0,
                "sector_code": row[19] if len(row) > 19 else "",
            })
    return out


def get_kpl_broken_ratio() -> Dict[str, Any]:
    """KPL 涨跌停情绪（RiseFallAnalysis）——涨停/跌停/自然涨停/破板率/炸板。

    字典 §12.17：info=[[涨停, 跌停, 自然涨停, 曾跌停, 破板率, 炸板, 日期]]
    交叉验证：8/7 [74, 4, 71, 1, 26, 26] 与东财/财联社涨停 74 一致
    """
    p = _base()
    p.update({"a": "RiseFallAnalysis", "c": "HomeDingPan"})
    d = _post("shhq", p)
    if "_err" in d or d.get("errcode") != "0":
        return {}
    info = (d.get("info") or [[]])[0]
    if not isinstance(info, list) or len(info) < 6:
        return {}
    return {
        "zt": int(info[0]), "dt": int(info[1]),
        "zt_natural": int(info[2]), "dt_ever": int(info[3]),
        "broken_ratio": float(info[4]), "broken_num": int(info[5]),
        "date": str(info[6]) if len(info) > 6 else "",
    }


def _f(v: Any) -> float:
    try:
        return float(v) if v not in ("", None, "--") else 0.0
    except (TypeError, ValueError):
        return 0.0


if __name__ == "__main__":
    print("情绪:", get_kpl_market_sentiment())
    print("涨跌家数:", get_kpl_up_down())
    print("涨停梯队首板:", len(get_kpl_limit_up_detail(1)), "只")
    print("板块强度 top3:", get_kpl_plate_strength(3)[:1])
    print("涨跌停:", get_kpl_broken_ratio())

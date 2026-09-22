"""_st_list.py — ST / *ST 名单(全市场风险警示快照, 吸收上游 3.9.0 §6.8).

函数: st_stock_list() — 沪深京 ST/*ST 当日名单(代码/市场/名称/类型/价格/涨跌幅).
数据来源: 东财「风险警示板」过滤(含 B 股) + 北交所全表按名称筛。
注: 上游 baostock 兜底(东财不可达时)未接入——为避免引入未经验证的重 TCP 依赖;
东财两域(push2/push2delay)均不可达时返回 [] 并记日志(治理铁律: 不把失败伪装成空名单)。
reportName 常量: 无(clist 过滤, 非 datacenter reportName); _VERIFIED 标记取自上游权威实现(2026-09-22 对撞校正)。
"""
from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Tuple

from stock_common.sc_network import _quick_request, UA
from stock_common import _debug_log

EM_CLIST_HOSTS = ["https://push2.eastmoney.com", "https://push2delay.eastmoney.com"]


def _v39_num(value):
    if value is None or value == "":
        return None
    t = str(value).replace(",", "").strip()
    if t in ("", "-", "--", "None", "null"):
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _em_clist_all(fs: str, fields: str, page_size: int = 100) -> Tuple[List[Dict[str, Any]], str]:
    """东财 clist 全量翻页。主域网络失败时换 push2delay(同一接口, 行情延迟约 15 分钟)。"""
    errors = []
    for host in EM_CLIST_HOSTS:
        url = host + "/api/qt/clist/get"
        rows, page, total = [], 1, None
        try:
            while True:
                r = _quick_request(url, params={"pn": page, "pz": page_size, "po": 1, "np": 1,
                                               "fltt": 2, "invt": 2, "fid": "f12",
                                               "fs": fs, "fields": fields},
                                  headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"},
                                  timeout=15)
                if r is None:
                    raise RuntimeError("request_none")
                try:
                    payload = r.json()
                except Exception:
                    raise RuntimeError("非 JSON")
                data = payload.get("data") if isinstance(payload, dict) else None
                if not isinstance(data, dict) or payload.get("rc") != 0 or not data:
                    raise RuntimeError(f"东财 clist 返回异常或无数据（fs={fs}）: {str(payload)[:100]}")
                page_total = int(data.get("total"))
                diff = data.get("diff") or []
                if not isinstance(diff, list):
                    diff = list(diff.values())
                if total is None:
                    total = page_total
                elif page_total != total:
                    raise RuntimeError(f"东财 clist 翻页时 total 从 {total} 变成 {page_total}，请重试")
                rows.extend(diff)
                if not diff or len(rows) >= total:
                    break
                page += 1
        except Exception as exc:
            errors.append(f"{host}: {type(exc).__name__}: {exc}")
            continue
        if len(rows) != total:
            raise RuntimeError(f"东财 clist 翻页后 {len(rows)} 条，与 total={total} 不符")
        return rows, url
    raise RuntimeError("东财 push2 / push2delay 均不可达: " + "; ".join(errors))


def _parse_st_rec(rec: Dict[str, Any], is_bj: bool) -> Optional[Dict[str, Any]]:
    """单条记录解析: 坏记录跳过(记日志)而非中断整张名单。"""
    code = rec.get("f12")
    name = str(rec.get("f14") or "").strip()
    if not re.fullmatch(r"[0-9]{6}", str(code)):
        _debug_log(f"st_stock_list: 认不出的代码: f12={code!r}")
        return None
    if not name:
        _debug_log(f"st_stock_list: {code} 没有名称, 跳过")
        return None
    if is_bj:
        if "ST" not in name.upper():
            return None  # 北交所全表按名筛: 非 ST 直接丢弃
        market = "bj"
    else:
        market_id = rec.get("f13")
        if isinstance(market_id, bool) or market_id not in (0, 1):
            _debug_log(f"st_stock_list: 认不出的市场号: f12={code} f13={market_id!r}")
            return None
        market = "sh" if market_id == 1 else "sz"
    return {"code": str(code), "market": market, "name": name,
            "st_type": "*ST" if name.startswith("*") else "ST",
            "price": _v39_num(rec.get("f2")), "pct_change": _v39_num(rec.get("f3"))}


def st_stock_list() -> List[Dict[str, Any]]:
    """全市场 ST / *ST 名单(风险警示) — 当日快照。

    主源: 沪深风险警示板(含 B 股, fs=m:0+f:4,m:1+f:4), 必需; 不可达时抛错,
    让采集器记为 __error__(治理铁律: 不把源失败伪装成空名单)。
    北交所: 软补充(拉全表按名筛), 失败/为空不影响沪深结果。
    坏记录跳过而非中断整张名单。
    """
    fields = "f12,f13,f14,f2,f3"
    try:
        shsz, _ = _em_clist_all("m:0+f:4,m:1+f:4", fields)
    except RuntimeError as exc:
        # 主源不可达 → 抛错(采集器会记 __error__, 不伪装成空名单)
        raise RuntimeError(f"ST名单主源(沪深风险警示板)不可达: {exc}")
    if not shsz:
        raise RuntimeError("ST名单主源(沪深风险警示板)返回空, 疑似结构改变")
    rows: List[Dict[str, Any]] = []
    for rec in shsz:
        p = _parse_st_rec(rec, is_bj=False)
        if p:
            rows.append(p)
    # 北交所: 软补充(可选)
    try:
        bj, _ = _em_clist_all("m:0+t:81+s:2048", fields)
    except RuntimeError as exc:
        _debug_log(f"st_stock_list: 北交所补充失败, 仅用沪深({exc})")
        bj = []
    for rec in bj:
        p = _parse_st_rec(rec, is_bj=True)
        if p:
            rows.append(p)
    if not rows:
        raise RuntimeError("ST名单解析后为空, 疑似结构改变")
    return rows


_VERIFIED = True  # 取自上游权威仓库(2026-09-22 对撞校正); baostock 兜底路径未接入(待评估)
                # 主源(沪深)不可达时本函数抛错, 由采集器记为 __error__(不伪装空名单)

"""_st_list.py — ST / *ST 名单(全市场风险警示快照, 吸收上游 3.9.0 §6.8).

函数: st_stock_list() — 沪深京 ST/*ST 当日名单(代码/市场/名称/类型/价格/涨跌幅).
主源: 东财「风险警示板」过滤(含 B 股) + 北交所全表按名称筛。
兜底: baostock(仅沪深, 上游 §6.8 明确 baostock 不支持北交所) — 东财主源不可达时启用,
      使沪深名单仍可获取; BJ 始终只能来自东财(治理铁律: 不把源失败伪装成空名单)。
reportName 常量: 无(clist 过滤, 非 datacenter reportName); _VERIFIED 标记取自上游权威实现(2026-09-22 对撞校正)。
"""

from __future__ import annotations
import re
import threading
from typing import Any, Dict, List, Optional, Tuple

from stock_common.sc_network import _quick_request, UA
from stock_common import _debug_log

EM_CLIST_HOSTS = ["https://push2.eastmoney.com", "https://push2delay.eastmoney.com"]


def _v39_num(value: Any) -> Optional[float]:
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
                r = _quick_request(
                    url,
                    params={
                        "pn": page,
                        "pz": page_size,
                        "po": 1,
                        "np": 1,
                        "fltt": 2,
                        "invt": 2,
                        "fid": "f12",
                        "fs": fs,
                        "fields": fields,
                    },
                    headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"},
                    timeout=15,
                )
                if r is None:
                    raise RuntimeError("request_none")
                try:
                    payload = r.json()
                except Exception:
                    raise RuntimeError("非 JSON")
                data = payload.get("data") if isinstance(payload, dict) else None
                if not isinstance(data, dict) or payload.get("rc") != 0 or not data:
                    raise RuntimeError(
                        f"东财 clist 返回异常或无数据（fs={fs}）: {str(payload)[:100]}"
                    )
                total_value = data.get("total")
                if total_value is None:
                    raise RuntimeError("东财 clist 缺少 total")
                page_total = int(total_value)
                diff = data.get("diff") or []
                if not isinstance(diff, list):
                    diff = list(diff.values())
                if total is None:
                    total = page_total
                elif page_total != total:
                    raise RuntimeError(
                        f"东财 clist 翻页时 total 从 {total} 变成 {page_total}，请重试"
                    )
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
    return {
        "code": str(code),
        "market": market,
        "name": name,
        "st_type": "*ST" if name.startswith("*") else "ST",
        "price": _v39_num(rec.get("f2")),
        "pct_change": _v39_num(rec.get("f3")),
    }


def _st_list_baostock() -> List[Dict[str, Any]]:
    """baostock 兜底(仅沪深, baostock 不支持北交所) — 东财主源不可达时启用。

    用守护线程 + join 硬超时(20s)包裹, 避免受限网络下 baostock 挂起拖垮整份报告。
    返回与 _parse_st_rec 同形状的记录(无价格/涨跌幅); 未安装/失败/超时返回 []。
    """
    box: Dict[str, List[Dict[str, Any]]] = {}

    def _inner() -> List[Dict[str, Any]]:
        try:
            import baostock as bs
        except ImportError:
            _debug_log("st_stock_list: baostock 未安装, 跳过兜底(如需启用: pip install baostock)")
            return []
        try:
            lg = bs.login(timeout=15)
            if getattr(lg, "error_code", "1") != "0":
                _debug_log(
                    f"st_stock_list: baostock 登录失败({getattr(lg, 'error_msg', '?')}), 跳过兜底"
                )
                return []
            rs = bs.query_stock_basic()
            rows: List[Dict[str, Any]] = []
            while getattr(rs, "error_code", "1") == "0" and rs.next():
                rec = rs.get_row_data()
                if len(rec) < 2:
                    continue
                code_full, name = rec[0], (rec[1] or "")
                if not name or "ST" not in name.upper():
                    continue
                if not code_full or "." not in code_full:
                    continue
                prefix, c = code_full.split(".", 1)
                if prefix not in ("sh", "sz"):
                    continue  # baostock 仅 sh/sz, 无 bj(不支持北交所)
                rows.append(
                    {
                        "code": c,
                        "market": prefix,
                        "name": name.strip(),
                        "st_type": "*ST" if name.startswith("*") else "ST",
                        "price": None,
                        "pct_change": None,
                    }
                )
            return rows
        except Exception as exc:
            _debug_log(f"st_stock_list: baostock 兜底异常({exc}), 跳过")
            return []
        finally:
            try:
                bs.logout()
            except Exception:
                pass

    t = threading.Thread(target=lambda: box.__setitem__("rows", _inner()), daemon=True)
    t.start()
    t.join(timeout=20)
    if t.is_alive():
        _debug_log("st_stock_list: baostock 兜底超时(20s, 疑似网络受限), 跳过")
        return []
    return box.get("rows", [])


def st_stock_list() -> List[Dict[str, Any]]:
    """全市场 ST / *ST 名单(风险警示) — 当日快照。

    主源: 沪深风险警示板(含 B 股, fs=m:0+f:4,m:1+f:4), 必需; 不可达时抛错,
    让采集器记为 __error__(治理铁律: 不把源失败伪装成空名单)。
    兜底: 东财主源不可达 → baostock(仅沪深) 兜底, 使沪深名单仍可得。
    北交所: 东财 clist 软补充; baostock 不支持北交所, 故 BJ 仅来自东财(上游 §6.8 已知限制)。
    坏记录跳过而非中断整张名单。
    """
    fields = "f12,f13,f14,f2,f3"
    shsz_rows: List[Dict[str, Any]] = []
    try:
        shsz, _ = _em_clist_all("m:0+f:4,m:1+f:4", fields)
        for rec in shsz:
            p = _parse_st_rec(rec, is_bj=False)
            if p:
                shsz_rows.append(p)
    except RuntimeError as exc:
        _debug_log(f"st_stock_list: 沪深主源(东财)不可达({exc}), 尝试 baostock 兜底(仅沪深)")
        shsz_rows = _st_list_baostock()
    if not shsz_rows:
        raise RuntimeError("ST名单(沪深)主源与 baostock 兜底均不可用")

    rows: List[Dict[str, Any]] = list(shsz_rows)
    # 北交所: 东财 clist 软补充(可选; baostock 不支持北交所)
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


_VERIFIED = True  # 取自上游权威仓库(2026-09-22 对撞校正); V17.4.2 接入 baostock 兜底(仅沪深)
# 主源(沪深)不可达时走 baostock 兜底; 北交所仅来自东财(baostock 不支持北交所, 上游 §6.8 已知限制)

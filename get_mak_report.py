#!/usr/bin/env python3
"""
get_mak_report.py — A股异动及行业轮动扫描报告
融合全市场异动扫描与行业轮动强度扫描

版本信息:
    V15.2  2026-07-28 - V15.2 缓存 valid_if 强化（limit_pool/dragon_tiger）+ ths_hot_reason 失败降级
    V15.1  2026-07-26 - V15.1 全局 ZHB 旁路普及：异动扫描的大宗交易与解禁预警在休市日优先读取 ZHB 快照
    V15.0  2026-07-26 - 接入 CanonicalStockData 强类型数据合约，实施基于真实周期的 ZHB-First 离线优先路由
    V14.0  2026-07-22 - 文档同步：docstring 版本信息更新到 V14.0；is_workday() Bug 修复由 stock_common 上游提供
    V13.x  2026-07-22 - 受益于 stock_cache.py dataclass 透明序列化（脚本无改动）
    V12.6  2026-07-22 - 受益于字段路由简化（移除估值字段 HTTP fallback）
    V12.4  2026-07-22 - 抽象 BaseReportRunner 基类
    V9.5   2026-07-11 - 基础设施修复：aiohttp原生异步迁移、静默异常日志化（脚本本身无改动，受益于底层修复）
    V9.4   2026-07-11 - 死代码清理+性能优化：全市场异动扫描引入 ThreadPoolExecutor 并行（max_workers=3）；修复连板/涨停表格显示bug；休市提示文案统一
    V9.3.3 2026-07-11 - 死代码清理 + 性能优化：全市场异动扫描引入 ThreadPoolExecutor 并行（max_workers=3）
    V9.3.2 2026-07-09 - 基础设施修复：TDX K线假数据防护、SQLite WAL死锁修复、代理环境兼容（脚本本身无改动，受益于底层修复）
    V9.3   2026-07-07 - 盘前行情模式：9:30前使用上一交易日日K线数据；删除报告标题硬编码版本号
    V9.2   2026-07-05 - 异常处理规范化；缓存交叉验证机制启用
    V9.1   2026-07-04 - 版本号统一升级（无功能变更，F10 公告兜底已在 V9.0 实现）
    V9.0   2026-07-02 - 舆情互动层（Layer 10）；上市日期 push2 fallback；valid_if 校验；_has_zero_price 拦截
    V8.9   2026-06-29 - 修复模块导入；清理冗余空行输出；模块版本统一
    V8.7   2026-06-25 - 死代码清理：同步版替换为薄包装
"""

# V16.4.1: 强制 UTF-8 输出（下沉到代码自身——任何 agent/机器/直接运行均 UTF-8，
# 不再依赖 main.py 注入的 PYTHONIOENCODING 环境变量）
from stock_common.env_setup import ensure_utf8_stdio

ensure_utf8_stdio()

import time, os, math, warnings, asyncio, re  # V17.0.4: +re/json(新浪指数 K 兜底); V17.0.25: +math(连板对数估算)
from typing import Any, Dict, List, Optional, Tuple
from datetime import date, datetime
from concurrent.futures import ThreadPoolExecutor, as_completed  # V16.4.1: 删 Counter

# H1/H2 修复(2026-08-15 二审): 全市场 ulist 主力净额(元, 带符号)模块级共享——_get_zhb_market_data 填充, 板块聚合/A 段读取
_MAIN_NET_MAP_GLOBAL: Dict[str, float] = {}
_MAIN_NET_REQUESTED_COUNT = 0
_MAIN_NET_RETURNED_COUNT = 0
_MAIN_NET_SOURCE_STATUS = "not_requested"
_MAIN_NET_DATA_DATE_NOTE = ""

warnings.filterwarnings("ignore")
from core.data_provider import get_market_snapshot_async
from stock_common.sc_utils import is_a_stock as _is_a_stock

from core.tdx_client import (  # V16.4.1: 删 tdx_get_security_bars/cleanup_tdx,
    tdx_get_board_list,
    tdx_get_board_members,
    tdx_get_market_abnormal_data,
)
from stock_common import (
    _safe_float,
    _debug_log,  # V17.0 审查: 删 UA 死导入(getharden 委托 sc_datasource 后无引用)
    _load_strategy_config,
    get_recent_dragon_tiger,
    baidu_kline_full as _tdx_kline_full,
    BaseReportRunner,  # V16.4.1: 删 _request_with_retry/common_parse_args
    is_trading_day,
    get_market_status,
    is_zhb_data_fresh,
    zhb_field_safe,
    get_zhb_data_date,
    calc_mcap_yi as _calc_mcap_yi,
    limit_pct_for,  # V16.2: 统一涨跌停阈值（主板/ST 10 / 双创 20 / 北交所 30）
    is_limit_up,
    is_limit_down,  # V16.0: 统一涨停/跌停判断（含 ST）
    get_zhb_market_stat2_snapshot,
)  # V10.3

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 加载策略阈值配置（模块级缓存，check_stock 函数中使用）
_sc_ma = _load_strategy_config()
_abnl = _sc_ma.get("abnormal", {})
_ret10_warn = _abnl.get("ret_10d_warn", 70.0)  # 10日累计涨幅警示阈值
_ret10_down = _abnl.get("ret_10d_severe_down", -50.0)  # 10日严重下跌阈值
_vol_locked = _abnl.get("volume_locked_pct", 3.0)  # 极度锁仓阈值
_vol_overload = _abnl.get("volume_overload_pct", 25.0)  # 爆量阈值


# V16.3.3 (2026-08-10 字典 12.15.8): ST/次新标注（不剔除——ST 涨跌幅已统一 10%，市场价值正常体现）
def _name_mark(name: str) -> str:
    """V17.0 S5: 统一走 sc_utils.name_mark（原本地实现已收敛）。"""
    from stock_common.sc_utils import name_mark as _u_name_mark

    return _u_name_mark(name)


def _is_industry_code(ic) -> bool:
    """V16.2.16: 行业段判断（8803xx/8804xx 通达信行业、881xxx 申万版；滤掉风格/概念/地域）。"""
    try:
        from core.zhb_client import is_industry_code as _zhb_is_ind

        return _zhb_is_ind(ic)
    except Exception:
        s = str(ic or "")
        return len(s) == 6 and s.isdigit() and s.startswith(("8803", "8804", "881"))


def _fmt_ret(v):
    if v is None:
        return "N/A"
    return f"{v:+.2f}"


INDEX_MAP = {
    "sh000001": "上证指数",
    "sz399001": "深证成指",
    "sz399102": "创业板综指",
    "sz399106": "深证综指",
    "sz399006": "创业板指",
    "sh000680": "科创综指",
}


def get_stock_index(code):
    if code.startswith("688"):
        return "sh000680"
    elif code.startswith(("300", "301")):
        return "sz399102"
    elif code.startswith("6"):
        return "sh000001"
    elif code.startswith(("000", "001", "002", "003")):
        return "sz399001"
    else:
        return "sz399001"


def get_board_name(code, name):
    if "ST" in name or "*ST" in name:
        return "ST"
    if code.startswith("688"):
        return "科创板"
    if code.startswith(("300", "301")):
        return "创业板"
    return "主板"


def calc_official_deviation(stock_ret, index_ret):
    if index_ret is None:
        return 0.0
    s_val = 1 + stock_ret / 100.0
    i_val = 1 + index_ret / 100.0
    if i_val <= 0:
        return 0.0
    return round((s_val / i_val - 1) * 100, 2)


def _market_breadth_display(up_count: int, down_count: int) -> tuple[str, str]:
    """Format breadth without turning a zero-down denominator into an artificial ratio."""
    if up_count <= 0 and down_count <= 0:
        return "N/A", "无有效涨跌方向样本"
    if down_count <= 0:
        return "∞", "上涨样本中无下跌"
    ratio = up_count / down_count
    if up_count <= 0:
        sentiment = "偏空"
    elif ratio > 1.5:
        sentiment = "偏多"
    elif ratio < 0.67:
        sentiment = "偏空"
    else:
        sentiment = "均衡"
    return f"{ratio:.2f}", sentiment


def _select_ulist_main_net_for_date(
    quotes: Dict[str, Dict[str, Any]], expected_date: str
) -> tuple[Dict[str, float], str, Dict[str, int]]:
    """Keep only f62 values whose same-row Ulist date anchors match the market date."""
    try:
        expected_date = datetime.strptime(expected_date, "%Y-%m-%d").date().isoformat()
    except (TypeError, ValueError):
        stats = {
            "date_match_rows": 0,
            "date_mismatch_rows": 0,
            "unverified_rows": len(quotes),
            "missing_flow_rows": 0,
        }
        return {}, "交易日历基准日期不可用；拒绝汇总未定日的 Ulist f62。", stats

    flows: Dict[str, float] = {}
    stats = {
        "date_match_rows": 0,
        "date_mismatch_rows": 0,
        "unverified_rows": 0,
        "missing_flow_rows": 0,
    }
    for code, quote in quotes.items():
        if not isinstance(quote, dict) or quote.get("_source_as_of_date_status") != "verified":
            stats["unverified_rows"] += 1
            continue
        if quote.get("_source_as_of_date") != expected_date:
            stats["date_mismatch_rows"] += 1
            continue
        stats["date_match_rows"] += 1
        raw_flow = quote.get("main_net_inflow_wan")
        if raw_flow in (None, ""):
            stats["missing_flow_rows"] += 1
            continue
        flow_wan = _safe_float(raw_flow)
        if not math.isfinite(flow_wan):
            stats["missing_flow_rows"] += 1
            continue
        flows[str(code)] = flow_wan * 1e4

    note = (
        f"交易日历基准 {expected_date}；要求同一 Ulist 行 f124/f297 日期锚一致；"
        f"日期匹配 {stats['date_match_rows']} 条，汇总有效 f62 {len(flows)} 条；"
        f"排除日期不符 {stats['date_mismatch_rows']} 条、日期锚缺失/冲突/不完整 "
        f"{stats['unverified_rows']} 条、匹配日期但 f62 缺失 {stats['missing_flow_rows']} 条。"
    )
    return flows, note, stats


def _verified_main_net_amount(code: str) -> float:
    """Return only the valid ulist f62 value; ZHB's similarly named field is auction amount."""
    value = _MAIN_NET_MAP_GLOBAL.get(str(code), 0.0)
    return value if math.isfinite(value) else 0.0


def _format_limit_pool_source_summary(
    sources: dict,
    total: Any,
    unqueried_sources=(),
    *,
    cross_verified: bool = False,
) -> tuple[str, str]:
    """Render source observations without treating a date label as an as-of proof."""
    source_map = sources if isinstance(sources, dict) else {}
    kpl_count = source_map.get("kpl")
    push2_count = source_map.get("push2ex")
    total_count = total if type(total) is int and total >= 0 else None
    cross_verified = bool(
        cross_verified
        and type(kpl_count) is int
        and kpl_count >= 0
        and type(push2_count) is int
        and push2_count == kpl_count
        and (total_count is None or total_count == kpl_count)
    )
    source_parts = []
    valid_counts: list[tuple[str, int]] = []
    unqueried = set(unqueried_sources or ())
    labels = {
        "cls": "CLS",
        "kpl": "KPL(开盘啦)",
        "fupan": "KPH复盘榜",
        "push2ex": "东财Push2",
    }
    for name, value in source_map.items():
        if name not in {"kpl", "push2ex"}:
            source_parts.append(f"{labels.get(name, name)}=不纳入（非本节合格计数源）")
            continue
        if value is None:
            status = "未查询" if name in unqueried else "无可用值/日期标签不匹配"
            source_parts.append(f"{labels.get(name, name)}={status}")
            continue
        if type(value) is not int or value < 0:
            source_parts.append(f"{labels.get(name, name)}=无效值")
            continue
        if name == "kpl":
            date_note = (
                "来源实际数据日已核实" if cross_verified else "Day标签匹配；来源实际数据日未核实"
            )
            source_parts.append(f"{labels[name]}={value}（{date_note}）")
        else:
            date_note = (
                "来源实际数据日已核实" if cross_verified else "按请求日期查询；来源实际数据日未核实"
            )
            source_parts.append(f"{labels[name]}={value}（{date_note}）")
        valid_counts.append((name, value))

    source_text = " / ".join(source_parts) if source_parts else "无来源结果"
    if not valid_counts:
        status = "无可用统计值，未生成汇总结论"
    elif len(valid_counts) == 1:
        name = valid_counts[0][0]
        if name == "kpl":
            status = "仅有 KPL 日期标签匹配的观测值；来源实际数据日未核实，不能作同日交叉确认"
        else:
            status = "仅有东财按请求日期查询的观测值，未能交叉验证"
    elif len(valid_counts) >= 2 and valid_counts[0][1] == valid_counts[1][1]:
        count = valid_counts[0][1]
        if cross_verified and (total_count is None or total_count == count):
            status = f"KPL 与东财 Push2 两个来源一致（{count}），可同日交叉确认"
        else:
            status = (
                f"两个来源计数值均为 {count}；KPL Day 仅为响应标签，"
                "来源实际数据日未核实，不作同日交叉确认"
            )
    else:
        details = " / ".join(f"{labels[name]} {count}" for name, count in valid_counts)
        status = f"来源观测计数不一致（{details}），未采用任一来源作为汇总结论"

    failed_count = sum(
        1
        for name, value in source_map.items()
        if name in {"kpl", "push2ex"} and value is None and name not in unqueried
    )
    if failed_count:
        status += f"；另有 {failed_count} 个来源无可用值"
    return source_text, status


def _limit_pool_count_mismatch_note(
    multi_total: Any, pool_count: Any, requested_data_date: Any = None
) -> str:
    """Explain date-aligned count differences without claiming list-level equivalence."""
    try:
        if multi_total is None or pool_count is None or int(multi_total) == int(pool_count):
            return ""
    except (TypeError, ValueError):
        return ""
    day_note = f"请求数据日 {requested_data_date} 的" if requested_data_date else ""
    return (
        f"⚠️ 计数差异：{day_note}来源对照计数 {multi_total} 只与本节涨停名单 {pool_count} 只不同；"
        "请求日期和来源日期标签不等于实际数据日期证明，且未逐股对齐；封板率和明细仅代表本节名单。"
    )


def _main_flow_summary_lines(
    flow_values: Dict[str, float],
    requested_count: int,
    returned_count: int,
    *,
    zhb_auction_amount_wan: float = 0.0,
    zhb_data_date: str = "",
    source_status: str = "not_requested",
    source_date_note: str = "",
) -> List[str]:
    """Render main-flow and auction amount as separate, correctly labeled measures."""
    if flow_values:
        total_yi = sum(_safe_float(value) for value in flow_values.values()) / 1e8
        complete = requested_count > 0 and returned_count >= requested_count
        status = "全样本返回" if complete else "覆盖不完整"
        lines = [
            f"  ulist f62 主力净额覆盖：{returned_count}/{requested_count} 条扫描样本；未返回项不代表零净流。",
            f"  💰 本次扫描样本主力净额合计：{total_yi:+.2f}亿元（ulist f62，{status}）",
        ]
        if source_date_note:
            lines.insert(1, f"  Ulist 行日期核验：{source_date_note}")
        if complete and total_yi > 50:
            lines.append("    🟢 完整扫描样本主力净额超过 +50 亿元参考阈值")
        elif complete and total_yi < -50:
            lines.append("    🔴 完整扫描样本主力净额低于 -50 亿元参考阈值")
        elif not complete:
            lines.append("    ⚠️ 覆盖不完整，不据样本合计推断全市场资金方向")
        if source_status == "shared_cooldown":
            lines.append(
                "    来源状态：push2delay 共享风控冷却中，本轮跳过请求；缺项不按零值处理。"
            )
        elif source_status == "partial":
            lines.append("    来源状态：仅返回部分有效 f62 样本；缺项不按零值处理。")
        elif source_status == "error":
            lines.append("    来源状态：批量 f62 请求异常；不据此判断资金方向。")
        return lines

    lines = [
        f"  ulist f62 主力净额覆盖：{returned_count}/{requested_count} 条扫描样本；未返回项不代表零净流。",
        "  💰 主力净流入：暂缺（ulist f62 未返回有效样本），不作资金方向判断。",
    ]
    if source_date_note:
        lines.insert(1, f"  Ulist 行日期核验：{source_date_note}")
    if source_status == "shared_cooldown":
        lines.append("  来源状态：push2delay 共享风控冷却中，本轮跳过请求；未返回不代表零净流。")
    elif source_status == "error":
        lines.append("  来源状态：批量 f62 请求异常；未返回不代表零净流。")
    elif source_status == "no_valid_rows":
        lines.append("  来源状态：请求未返回可用 f62 数值；未返回不代表零净流。")
    elif source_status == "date_mismatch":
        lines.append("  来源状态：Ulist 行日期与交易日历基准不符；本轮不混合其他数据日的净额。")
    elif source_status == "date_unconfirmed":
        lines.append("  来源状态：Ulist 同行日期锚缺失、冲突或不可解析；本轮不汇总未定日净额。")
    if zhb_auction_amount_wan > 0:
        auction_yi = zhb_auction_amount_wan / 1e4
        as_of = zhb_data_date or "未确认"
        lines.append(
            f"  ZHB竞价金额代理：{auction_yi:.2f}亿元（数据日 {as_of}；不是主力净流入，不用于多空判断）"
        )
    return lines


async def get_market_abnormal_data():
    """Build full-market anomaly inputs from one ZHB snapshot and a dated Tencent batch.

    Tencent values are overlaid only when their per-field timestamp is valid. ZHB package
    dates remain attached to ZHB fields, and the legacy TDX-named fallback also reads ZHB.
    """
    global _MAIN_NET_MAP_GLOBAL, _MAIN_NET_REQUESTED_COUNT, _MAIN_NET_RETURNED_COUNT
    global _MAIN_NET_SOURCE_STATUS, _MAIN_NET_DATA_DATE_NOTE
    _MAIN_NET_MAP_GLOBAL = {}
    _MAIN_NET_REQUESTED_COUNT = 0
    _MAIN_NET_RETURNED_COUNT = 0
    _MAIN_NET_SOURCE_STATUS = "not_requested"
    _MAIN_NET_DATA_DATE_NOTE = ""

    # V17.4: retain dated ZHB periods even when the package is one trading day behind;
    # Tencent current-day fields are accepted only with their per-row [30] timestamp.
    # The previous TDX-named fallback also read the ZHB snapshot, so both paths now share
    # one provenance-aware builder and one Tencent batch request.
    _tencent_map: Dict[str, Any] = {}
    _snapshot_loaded = False
    try:
        _snap = await get_market_snapshot_async()
        _snapshot_loaded = True
        _snap_codes = list(_snap.keys()) if _snap else []
    except Exception as _snapshot_error:
        _debug_log(f"mak snapshot async: {_snapshot_error}")
        _snap_codes = []
    if _snap_codes:
        try:
            from core.tdx_client import _tencent_batch_fallback

            _tencent_map = _tencent_batch_fallback(_snap_codes) or {}
        except Exception as _e:
            _debug_log(f"mak tencent batch: {_e}")
    data = await _get_zhb_market_data(
        tencent_map=_tencent_map,
        snapshot=_snap if _snapshot_loaded else None,
    )
    if not data:
        data = await asyncio.to_thread(tdx_get_market_abnormal_data)
        if data:
            _annotate_zhb_market_fields(data, get_zhb_data_date())
            if not _tencent_map:
                try:
                    from core.tdx_client import _tencent_batch_fallback

                    _tencent_map = _tencent_batch_fallback([s.get("code", "") for s in data]) or {}
                except Exception as _e:
                    _debug_log(f"mak tencent batch(fallback): {_e}")
            _apply_tencent_cover(data, _tencent_map)
    # 主力净额批量(ulist f62)必须在两条行情路径后统一执行；每轮先清空模块状态，避免复用上轮样本。
    if data:
        try:
            _bq_codes = [str(d.get("code", "")) for d in data if d.get("code")]
            if _bq_codes:
                _MAIN_NET_REQUESTED_COUNT = len(_bq_codes)
                from stock_common.sc_datasource import is_em_batch_quotes_cooling_down

                if is_em_batch_quotes_cooling_down():
                    _MAIN_NET_SOURCE_STATUS = "shared_cooldown"
                    _debug_log(
                        "mak ulist f62 skipped: push2delay shared risk-group cooldown is active"
                    )
                else:
                    from stock_common.sc_datasource import get_em_batch_quotes

                    _MAIN_NET_SOURCE_STATUS = "loading"
                    _bq = await asyncio.to_thread(get_em_batch_quotes, _bq_codes) or {}
                    try:
                        from stock_common.stock_calendar import latest_market_data_date

                        _ulist_expected_date = latest_market_data_date(datetime.now()).isoformat()
                    except Exception as _date_error:
                        _debug_log(f"mak Ulist expected date unavailable: {_date_error}")
                        _ulist_expected_date = ""
                    (
                        _MAIN_NET_MAP_GLOBAL,
                        _MAIN_NET_DATA_DATE_NOTE,
                        _ulist_date_stats,
                    ) = _select_ulist_main_net_for_date(_bq, _ulist_expected_date)
                    _MAIN_NET_RETURNED_COUNT = len(_MAIN_NET_MAP_GLOBAL)
                    _MAIN_NET_SOURCE_STATUS = (
                        "loaded"
                        if _MAIN_NET_RETURNED_COUNT >= _MAIN_NET_REQUESTED_COUNT
                        else "partial" if _MAIN_NET_RETURNED_COUNT else "no_valid_rows"
                    )
                    if not _MAIN_NET_RETURNED_COUNT:
                        if _ulist_date_stats["date_match_rows"]:
                            _MAIN_NET_SOURCE_STATUS = "no_valid_rows"
                        elif _ulist_date_stats["date_mismatch_rows"]:
                            _MAIN_NET_SOURCE_STATUS = "date_mismatch"
                        else:
                            _MAIN_NET_SOURCE_STATUS = "date_unconfirmed"
                    elif _MAIN_NET_RETURNED_COUNT < _MAIN_NET_REQUESTED_COUNT:
                        _MAIN_NET_SOURCE_STATUS = "partial"
                    if _MAIN_NET_RETURNED_COUNT < _MAIN_NET_REQUESTED_COUNT * 0.5:
                        _debug_log(
                            "mak ulist f62 coverage below 50%: "
                            f"{_MAIN_NET_RETURNED_COUNT}/{_MAIN_NET_REQUESTED_COUNT}; "
                            "skip immediate full-batch retry"
                        )
        except Exception as _e:
            _MAIN_NET_SOURCE_STATUS = "error"
            _debug_log(f"mak ulist main_net batch (unified): {_e}")
    # V17.3.11: 腾讯实时覆盖已改为单次获取并共享（ZHB 路径内层构建 / TDX 路径 _apply_tencent_cover），
    # 此处不再二次拉取。
    return data


def _apply_tencent_cover(data, tencent_map: Dict[str, Any]) -> None:
    """Overlay only Tencent fields whose per-field timestamp agrees with their date.

    ZHB values remain in place when Tencent provenance is missing or inconsistent.
    """
    if not data or not tencent_map:
        return
    try:
        _cov = 0
        for s in data:
            _tq = tencent_map.get(s.get("code", ""), {})
            _sources = _tq.get("_field_sources") or {}
            _tq_price, _price_date, _price_time = _dated_tencent_value(_tq, "price")
            _tq_change, _quote_date, _quote_time = _dated_tencent_value(_tq, "change_pct")
            if _tq_price is not None and _tq_price > 0:
                s["price"] = _tq_price
                _set_field_metadata(
                    s,
                    "price",
                    _sources.get("price", "tencent:qt.gtimg"),
                    _price_date,
                    _price_time,
                )
            if _tq_change is not None:
                s["change_pct"] = _tq_change
                _set_field_metadata(
                    s,
                    "change_pct",
                    _sources.get("change_pct", "tencent:qt.gtimg"),
                    _quote_date,
                    _quote_time,
                )
                _daily = s.get("_zhb_daily_returns") or {}
                _ret_3d = _calc_3d_from_daily(
                    _daily,
                    today_change_pct=_tq_change,
                    quote_as_of_date=_quote_date,
                    zhb_as_of_date=s.get("_zhb_data_date", ""),
                )
                if _ret_3d is not None and _quote_date:
                    s["ret_3d"] = _ret_3d
                    _set_field_metadata(
                        s,
                        "ret_3d",
                        "tencent+zhb:tdxstat",
                        _quote_date,
                        _quote_time,
                    )
                _cov += 1
            _tq_turnover, _turnover_date, _turnover_time = _dated_tencent_value(_tq, "turnover_pct")
            if _tq_turnover is not None:
                s["turnover"] = _tq_turnover
                _set_field_metadata(
                    s,
                    "turnover",
                    _sources.get("turnover_pct", "tencent:qt.gtimg"),
                    _turnover_date,
                    _turnover_time,
                )
            # V16.2.14: 补股票名称（ZHB 快照缺失时，如退市整理/新上市股）
            if _tq.get("name") and not s.get("name"):
                s["name"] = _tq["name"]
        _debug_log(f"mak tencent realtime cover: {_cov}/{len(data)} 只")
    except Exception as _e:
        _debug_log(f"mak tencent cover error: {_e}")


def _annotate_zhb_market_fields(data, zhb_data_date: str) -> None:
    for stock in data or []:
        zhb_date = _normalize_mak_date(stock.get("_zhb_data_date") or zhb_data_date)
        stock["_zhb_data_date"] = zhb_date
        for field in (
            "price",
            "change_pct",
            "turnover",
            "amount_yi",
            "ret_3d",
            "ret_5d",
            "ret_10d",
            "ret_20d",
            "ret_60d",
            "change_pct_1d",
            "change_pct_2d",
        ):
            value = _optional_number(stock.get(field))
            if value is not None and (field != "price" or value > 0):
                _set_field_metadata(stock, field, "zhb:tdxstat", zhb_date)


def _normalize_mak_date(value: Any) -> str:
    raw = str(value or "").strip()
    if len(raw) >= 10 and raw[4:5] == "-":
        try:
            return date.fromisoformat(raw[:10]).isoformat()
        except ValueError:
            return ""
    if len(raw) >= 8 and raw[:8].isdigit():
        try:
            return datetime.strptime(raw[:8], "%Y%m%d").date().isoformat()
        except ValueError:
            return ""
    return ""


def _optional_number(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _dated_tencent_value(quote: Dict[str, Any], field: str) -> Tuple[Optional[float], str, str]:
    """Return a Tencent field only when its row timestamp proves the same date."""
    value = _optional_number(quote.get(field))
    if value is None:
        return None, "", ""
    dates = quote.get("_field_as_of_dates") or {}
    timestamps = quote.get("_field_as_of_timestamps") or {}
    field_date = _normalize_mak_date(dates.get(field))
    observed_at = str(timestamps.get(field) or "")
    try:
        observed = datetime.fromisoformat(observed_at)
    except ValueError:
        return None, "", ""
    if not field_date or observed.date().isoformat() != field_date:
        return None, "", ""
    return value, field_date, observed.isoformat(sep=" ")


def _set_field_metadata(
    stock: Dict[str, Any],
    field: str,
    source: str,
    as_of_date: str,
    observed_at: str = "",
    status: str = "verified",
) -> None:
    normalized_date = _normalize_mak_date(as_of_date)
    stock.setdefault("_field_meta", {})[field] = {
        "source": source,
        "as_of_date": normalized_date,
        "observed_at": observed_at,
        "status": status if normalized_date else "date_unconfirmed",
    }


def _metric_for_date(
    stock: Dict[str, Any],
    field: str,
    expected_date: str,
    *,
    require_close_quote: bool = False,
) -> Tuple[Optional[float], str]:
    expected = _normalize_mak_date(expected_date)
    if not expected:
        return None, "date_unconfirmed"
    value = _optional_number(stock.get(field))
    if value is None:
        return None, "value_missing"
    meta = (stock.get("_field_meta") or {}).get(field)
    if not isinstance(meta, dict) or meta.get("status") != "verified":
        return None, "date_unconfirmed"
    metric_date = _normalize_mak_date(meta.get("as_of_date"))
    if metric_date != expected:
        return None, "date_mismatch"
    if require_close_quote:
        source = str(meta.get("source", ""))
        if "tencent" in source:
            observed_at = str(meta.get("observed_at") or "")
            try:
                observed = datetime.fromisoformat(observed_at)
            except ValueError:
                return None, "quote_timestamp_unconfirmed"
            if observed.date().isoformat() != metric_date:
                return None, "quote_timestamp_date_mismatch"
            if observed.time() < datetime.strptime("15:00:00", "%H:%M:%S").time():
                return None, "quote_not_final_close"
        elif source.startswith("zhb:"):
            # A same-day ZHB package must not qualify as a closing snapshot before the
            # market has closed. Previous-session packages remain valid pre-market.
            now = datetime.now()
            if (
                metric_date == now.date().isoformat()
                and now.time() < datetime.strptime("15:00:00", "%H:%M:%S").time()
            ):
                return None, "snapshot_not_final_close"
        else:
            return None, "close_status_unconfirmed"
    return value, "eligible"


async def _get_zhb_market_data(
    tencent_map: Optional[Dict[str, Any]] = None,
    snapshot: Optional[Dict[str, Any]] = None,
):
    """V10.1: 从zhb全市场快照构建异动扫描数据。

    返回格式与tdx_get_market_abnormal_data一致，便于无缝替换。
    V11.5: 使用data_provider的get_market_snapshot_async统一获取数据
    V17.4: Tencent snapshot fields require per-field row timestamps; values without a
           valid date anchor fall back to ZHB values while retaining the package date.
    """
    try:
        if snapshot is None:
            snapshot = await get_market_snapshot_async()
        if not snapshot:
            return []

        # ZHB snapshot 已包含全市场行情，直接复用，避免重复解析和网络 IO。
        price_map = snapshot

        result = []
        # V17.3.11: 腾讯批量实时覆盖改为**上层单次获取并共享传入**（见 get_market_abnormal_data）：
        # 本函数不再自行拉取，直接用传入的 tencent_map 构建 price/change_pct/amount/turnover/
        # mcap/ret_3d（盘中今日值），避免原 V15.5.15(内层)+V15.5.16(外层) 双拉全市场腾讯。
        # V17.0.2g(2026-08-17): 主力净额批量已上移至 get_market_abnormal_data 统一执行(两条路径)
        # V14.2.1: 提前一次性获取 ZHB profile 离线简称（修复 mak 0只 Bug）
        _tencent_map = tencent_map or {}
        from core.zhb_client import get_stock_name_from_zhb

        zhb_data_date = _normalize_mak_date(get_zhb_data_date())
        zhb_periods_safe = {
            "ret_5d": bool(
                zhb_data_date and zhb_field_safe("change_5k_bar", data_date=zhb_data_date)
            ),
            "ret_10d": bool(
                zhb_data_date and zhb_field_safe("change_10k_bar", data_date=zhb_data_date)
            ),
            "ret_20d": bool(
                zhb_data_date and zhb_field_safe("change_20k_bar", data_date=zhb_data_date)
            ),
            "ret_60d": bool(
                zhb_data_date and zhb_field_safe("change_60k_bar", data_date=zhb_data_date)
            ),
        }

        zhb_name_cache = {}
        for code, stat in snapshot.items():
            # V14.2.1: ZHB tdxstat 快照无 name 字段，用 profile.dat 离线字典补齐
            name = price_map.get(code, {}).get("name", "")
            if not name:
                # 优先从 ZHB profile.dat 提取（零网络请求）
                if code not in zhb_name_cache:
                    zhb_name_cache[code] = get_stock_name_from_zhb(code) or ""
                name = zhb_name_cache[code]
            if not name:
                continue
            if "ST" in name or "退" in name:
                continue

            # Preserve Tencent's per-row quote timestamp separately from the ZHB package date.
            _tq = _tencent_map.get(code, {})
            _tq_sources = _tq.get("_field_sources") or {}
            _tq_cp, _tq_date, _tq_time = _dated_tencent_value(_tq, "change_pct")
            _tq_price, _tq_price_date, _tq_price_time = _dated_tencent_value(_tq, "price")
            _tq_to, _tq_to_date, _tq_to_time = _dated_tencent_value(_tq, "turnover_pct")
            _tq_amount, _tq_amount_date, _tq_amount_time = _dated_tencent_value(_tq, "amount_wan")

            _zhb_price = _optional_number(price_map.get(code, {}).get("price"))
            price = _tq_price if _tq_price is not None else _zhb_price
            _zhb_change_pct = _optional_number(stat.get("change_pct"))
            change_pct = _tq_cp if _tq_cp is not None else _zhb_change_pct
            _zhb_amount = _optional_number(stat.get("amount"))
            amount_wan = _tq_amount if _tq_amount is not None else _zhb_amount
            _zhb_turnover = _optional_number(price_map.get(code, {}).get("turnover_pct"))
            turnover = _tq_to if _tq_to is not None else _zhb_turnover

            # 2026-08-11: 修复恒 0——腾讯批量直给 mcap_yi，缺失才走 股本×price 计算
            mcap_yi = _safe_float(_tq.get("mcap_yi") or 0) or _calc_mcap_yi(code, price or 0.0)

            # Trading-bar fields avoid comparing calendar-day returns with trading-day index windows.
            ret_5d = (
                _optional_number(stat.get("change_5k_bar")) if zhb_periods_safe["ret_5d"] else None
            )
            ret_10d = (
                _optional_number(stat.get("change_10k_bar"))
                if zhb_periods_safe["ret_10d"]
                else None
            )
            ret_20d = (
                _optional_number(stat.get("change_20k_bar"))
                if zhb_periods_safe["ret_20d"]
                else None
            )
            ret_60d = (
                _optional_number(stat.get("change_60k_bar"))
                if zhb_periods_safe["ret_60d"]
                else None
            )
            _daily_stat = {
                "change_pct": stat.get("change_pct"),
                "change_pct_1d": stat.get("change_pct_1d"),
                "change_pct_2d": stat.get("change_pct_2d"),
            }
            ret_3d = None
            ret_3d_uses_tencent = False
            if _tq_cp is not None:
                ret_3d = _calc_3d_from_daily(
                    _daily_stat,
                    today_change_pct=_tq_cp,
                    quote_as_of_date=_tq_date,
                    zhb_as_of_date=zhb_data_date,
                )
                ret_3d_uses_tencent = ret_3d is not None
            ret_3d_date = _tq_date if ret_3d_uses_tencent else zhb_data_date
            if ret_3d is None:
                ret_3d = _calc_3d_from_daily(_daily_stat)
                ret_3d_date = zhb_data_date if ret_3d is not None else ""

            stock = {
                "code": code,
                "name": name,
                "price": price,
                "change_pct": change_pct,
                "turnover": turnover,
                "mcap_yi": mcap_yi,
                "amount_yi": amount_wan / 10000.0 if amount_wan is not None else None,
                "ret_3d": ret_3d,
                "ret_5d": ret_5d,
                "ret_10d": ret_10d,
                "ret_20d": ret_20d,
                "ret_60d": ret_60d,
                # V16.4.1: 新股标记字段——change_pct_1d/2d 为空 = 上市不足 3 个交易日
                # (创业板/科创板新股前 5 日无涨跌幅限制, 首日 +662% 等极端值会让偏离判定失真)
                "change_pct_1d": _optional_number(stat.get("change_pct_1d")),
                "change_pct_2d": _optional_number(stat.get("change_pct_2d")),
                # ZHB main_net_buy_amount 实为竞价金额，不能回退填入主力净额字段。
                "main_net_amount": _verified_main_net_amount(code),
                # V16.2.16: Col[13] 大量为风格/概念（微盘股/近已解禁等）→ 只保留行业段
                # （8803xx/8804xx 通达信行业、881xxx 申万版），其余置空避免伪行业聚合
                "industry_code": (
                    stat.get("industry_code", "")
                    if _is_industry_code(stat.get("industry_code", ""))
                    else ""
                ),
                "_zhb_data_date": zhb_data_date,
            }
            for _field, _value, _source, _field_date, _observed_at in (
                (
                    "price",
                    price,
                    (
                        _tq_sources.get("price", "tencent:qt.gtimg")
                        if _tq_price is not None
                        else "zhb:tdxstat"
                    ),
                    _tq_price_date or zhb_data_date,
                    _tq_price_time,
                ),
                (
                    "change_pct",
                    change_pct,
                    (
                        _tq_sources.get("change_pct", "tencent:qt.gtimg")
                        if _tq_cp is not None
                        else "zhb:tdxstat"
                    ),
                    _tq_date or zhb_data_date,
                    _tq_time,
                ),
                (
                    "turnover",
                    turnover,
                    (
                        _tq_sources.get("turnover_pct", "tencent:qt.gtimg")
                        if _tq_to is not None
                        else "zhb:tdxstat"
                    ),
                    _tq_to_date or zhb_data_date,
                    _tq_to_time,
                ),
                (
                    "amount_yi",
                    stock["amount_yi"],
                    (
                        _tq_sources.get("amount_wan", "tencent:qt.gtimg")
                        if _tq_amount is not None
                        else "zhb:tdxstat"
                    ),
                    _tq_amount_date or zhb_data_date,
                    _tq_amount_time,
                ),
            ):
                if _value is not None and (_field != "price" or _value > 0):
                    _set_field_metadata(stock, _field, _source, _field_date, _observed_at)
            _set_field_metadata(
                stock,
                "ret_3d",
                "tencent+zhb:tdxstat" if ret_3d_uses_tencent else "zhb:tdxstat",
                ret_3d_date,
                _tq_time if ret_3d_uses_tencent else "",
            )
            for _field, _value in (
                ("ret_5d", ret_5d),
                ("ret_10d", ret_10d),
                ("ret_20d", ret_20d),
                ("ret_60d", ret_60d),
            ):
                if _value is not None and zhb_data_date:
                    _set_field_metadata(stock, _field, "zhb:tdxstat", zhb_data_date)
            result.append(stock)

        return result
    except Exception as _e:
        _debug_log(f"mak zhb_market_data: {_e}")
        return []


def _calc_3d_from_daily(
    stat,
    today_change_pct=None,
    *,
    quote_as_of_date: str = "",
    zhb_as_of_date: str = "",
):
    """Compound three consecutive daily returns, preserving missing values and dates."""
    if today_change_pct is None:
        values = [
            _optional_number(stat.get("change_pct")),
            _optional_number(stat.get("change_pct_1d")),
            _optional_number(stat.get("change_pct_2d")),
        ]
    else:
        quote_date = _normalize_mak_date(quote_as_of_date)
        zhb_date = _normalize_mak_date(zhb_as_of_date)
        if not quote_date or not zhb_date:
            # Legacy callers without dates may still calculate a provisional value;
            # the MAК evaluator will not accept it without field date metadata.
            values = [
                _optional_number(today_change_pct),
                _optional_number(stat.get("change_pct")),
                _optional_number(stat.get("change_pct_1d")),
            ]
        elif quote_date == zhb_date:
            # ZHB already contains the current trading day; avoid counting it twice.
            values = [
                _optional_number(today_change_pct),
                _optional_number(stat.get("change_pct_1d")),
                _optional_number(stat.get("change_pct_2d")),
            ]
        else:
            try:
                from stock_common.stock_calendar import previous_trading_day

                expected_zhb_date = previous_trading_day(
                    date.fromisoformat(quote_date), include_current=False
                ).isoformat()
            except (ValueError, NotImplementedError):
                return None
            if zhb_date != expected_zhb_date:
                return None
            values = [
                _optional_number(today_change_pct),
                _optional_number(stat.get("change_pct")),
                _optional_number(stat.get("change_pct_1d")),
            ]
    if any(value is None for value in values):
        return None
    numeric_values = [value for value in values if value is not None]
    returns = [value / 100.0 for value in numeric_values]
    return round(((1 + returns[0]) * (1 + returns[1]) * (1 + returns[2]) - 1) * 100, 2)


# V17.3.12: K线 count 归一——count_history_deviations(get_baidu_kline days=x→baidu count=x+10)/
# annotate_technical_pattern(→baidu 35)/ST 分支(baidu 30) 同一 code 进程内可能 3 次 TDX 取数；
# 统一取 60 根(覆盖最大窗口) 进程内 memo，各调用方按需切片复用（@cached(kline) 仍按新 key 落盘）。
_MAK_KLINE_MEMO: Dict[str, Any] = {}

# V17.3.12: 全市场扫描并行度。实测对照(600 样本)：纯 CPU 负载下 workers=6 反比 3 慢
# (GIL 限制 CPython 线程无法并行 CPU 型 Python；2.72s vs 2.62s)；CPU+TDX-I/O 混合下
# 6 仅快 ~3%(噪声内)。check_stock 主体为 CPU 绑定(K线已 memo 去重，仅触发股 1 次本地 TCP)，
# 故 3→6 无法稳定提速、且可能微降。保持 3(已验证安全值)；提速主要来源是 #1 K线去重与 #3 L2 共享。
MAK_SCAN_WORKERS = 3


def _mak_kline_raw(code):
    """取该 code 的 60 根日K (keys, rows)，进程内 memo 复用（V17.3.12 去重）。"""
    if code not in _MAK_KLINE_MEMO:
        _MAK_KLINE_MEMO[code] = _tdx_kline_full(code, count=60)
    return _MAK_KLINE_MEMO[code]


def get_tdx_kline(code, days=20):
    """Return daily TDX bars through the historical ``baidu_kline_full`` compatibility wrapper."""
    keys, rows = _mak_kline_raw(code)
    if not keys or not rows:
        return [], []
    idx_map = {k: i for i, k in enumerate(keys)}
    ci = idx_map.get("close", -1)
    vi = idx_map.get("volume", -1)
    if ci < 0:
        return [], []
    closes = [_safe_float(r[ci]) for r in rows[-days:] if len(r) > ci]
    vols = [_safe_float(r[vi]) for r in rows[-days:] if len(r) > vi and vi >= 0] if vi >= 0 else []
    return closes, vols


# Keep the old module-level name for external callers; it has never used a live Baidu endpoint.
get_baidu_kline = get_tdx_kline


def _dated_stock_bars(code: str):
    keys, rows = _mak_kline_raw(code)
    if not keys or not rows:
        return []
    date_i = next((i for i, key in enumerate(keys) if key in ("time", "date", "datetime")), -1)
    close_i = next((i for i, key in enumerate(keys) if key in ("close", "close_price")), -1)
    if date_i < 0 or close_i < 0:
        return []
    bars = {}
    for row in rows:
        if len(row) <= max(date_i, close_i):
            continue
        day = _normalize_mak_date(row[date_i])
        close = _optional_number(row[close_i])
        if day and close is not None and close > 0:
            bars[day] = {"date": day, "close": close, "source": "tdx"}
    return [bars[day] for day in sorted(bars)]


def _index_return_for_date(bars, end_date: str, period: int) -> Optional[float]:
    try:
        end = date.fromisoformat(end_date)
        from stock_common.stock_calendar import recent_trading_dates

        expected_dates = [
            day.isoformat() for day in reversed(recent_trading_dates(period + 1, as_of=end))
        ]
    except (ValueError, NotImplementedError):
        return None
    if not expected_dates or expected_dates[-1] != end_date:
        return None
    close_by_date = {
        _normalize_mak_date(bar.get("date")): _optional_number(bar.get("close"))
        for bar in bars
        if isinstance(bar, dict)
    }
    if any(close_by_date.get(day) is None for day in expected_dates):
        return None
    first_close = close_by_date[expected_dates[0]]
    last_close = close_by_date[expected_dates[-1]]
    if first_close is None or last_close is None or first_close <= 0:
        return None
    return round((last_close / first_close - 1) * 100, 2)


def get_index_returns(as_of_dates=None):
    """Return index returns by exact end date and retain dated bars for historical joins."""
    if as_of_dates is None:
        from stock_common.stock_calendar import latest_market_data_date

        as_of_dates = [latest_market_data_date(datetime.now()).isoformat()]
    end_dates = sorted({_normalize_mak_date(value) for value in as_of_dates} - {""})
    result = {end_date: {} for end_date in end_dates}
    bars_pool = {}
    for index_code in INDEX_MAP:
        try:
            from stock_common.sc_datasource import get_index_kline_bars

            bars = get_index_kline_bars(index_code, days=250)
        except Exception as _e:
            _debug_log(f"mak index_kline unified error {index_code}: {_e}")
            bars = []
        bars_pool[index_code] = bars
        for end_date in end_dates:
            result[end_date][index_code] = {
                "ret_3d": _index_return_for_date(bars, end_date, 3),
                "ret_10d": _index_return_for_date(bars, end_date, 10),
                "ret_20d": _index_return_for_date(bars, end_date, 20),
                "ret_60d": _index_return_for_date(bars, end_date, 60),
            }
    return result, bars_pool


def get_abnormal_announcements(code):
    """V17.0 S4: 统一走 sc_datasource.get_strategic_announcements(带缓存+TDX兜底)。

    原本地实现(orgId 动态查询 + searchkey fallback + 7 天窗口)与共享版重复——
    现以 keywords=["异常波动"] 复用共享层, 返回 (异常公告数, 严重异常数)。
    """
    try:
        from stock_common.sc_datasource import get_strategic_announcements

        anns = get_strategic_announcements(code, page_size=10, days=7, keywords=["异常波动"])
        abnormal = [a for a in anns if "异常波动" in (a.get("title", "") or "")]
        severe = [a for a in abnormal if "严重" in (a.get("title", "") or "")]
        return len(abnormal), len(severe)
    except Exception as _e:
        _debug_log(f"mak get_abnormal_announcements: {_e}")
        return 0, 0


def count_history_deviations(code, index_code, index_bars_pool, as_of_date, days_lookback=10):
    """Count the prior ten valid three-session deviation windows by exact bar dates."""
    try:
        end = date.fromisoformat(_normalize_mak_date(as_of_date))
        from stock_common.stock_calendar import recent_trading_dates

        prior_end_dates = recent_trading_dates(days_lookback + 1, as_of=end)
    except (ValueError, NotImplementedError):
        return None, None, 0
    if not prior_end_dates or prior_end_dates[0] != end:
        return None, None, 0
    prior_end_dates = prior_end_dates[1:]
    stock_bars = _dated_stock_bars(code)
    index_bars = index_bars_pool.get(index_code, [])
    stock_close = {
        _normalize_mak_date(b.get("date")): _optional_number(b.get("close")) for b in stock_bars
    }
    index_close = {
        _normalize_mak_date(b.get("date")): _optional_number(b.get("close")) for b in index_bars
    }
    count = 0
    last_dev = None
    valid_windows = 0
    for window_end in prior_end_dates:
        window_date = window_end.isoformat()
        try:
            from stock_common.stock_calendar import recent_trading_dates

            window_dates = [
                day.isoformat() for day in reversed(recent_trading_dates(4, as_of=window_end))
            ]
        except (ValueError, NotImplementedError):
            continue
        if not window_dates or window_dates[-1] != window_date:
            continue
        if any(
            stock_close.get(day) is None or index_close.get(day) is None for day in window_dates
        ):
            continue
        stock_start = stock_close[window_dates[0]]
        index_start = index_close[window_dates[0]]
        if stock_start <= 0 or index_start <= 0:
            continue
        stock_ret = (stock_close[window_dates[-1]] / stock_start - 1) * 100
        index_ret = (index_close[window_dates[-1]] / index_start - 1) * 100
        dev = calc_official_deviation(stock_ret, index_ret)
        valid_windows += 1
        if abs(dev) >= 20:
            count += 1
            last_dev = dev
    if valid_windows != days_lookback:
        return None, last_dev, valid_windows
    return count, last_dev, valid_windows


def _evaluate_stock(s, idx_rets_by_date, index_bars_pool, expected_data_date=None):
    code = s["code"]
    name = s["name"]
    idx_code = get_stock_index(code)
    board = get_board_name(code, name)
    threshold = int(limit_pct_for(code, name))
    signals = []
    rule_status = {}

    def _inputs(field, period):
        meta = (s.get("_field_meta") or {}).get(field) or {}
        metric_date = _normalize_mak_date(meta.get("as_of_date"))
        if not metric_date:
            rule_status[period] = "date_unconfirmed"
            return None, None, None
        expected_date = _normalize_mak_date(expected_data_date)
        if expected_date and metric_date != expected_date:
            rule_status[period] = "stock_metric_date_mismatch"
            return None, None, metric_date
        stock_return, reason = _metric_for_date(s, field, metric_date, require_close_quote=True)
        if stock_return is None:
            rule_status[period] = reason
            return None, None, metric_date
        index_return = ((idx_rets_by_date.get(metric_date) or {}).get(idx_code) or {}).get(field)
        index_return = _optional_number(index_return)
        if index_return is None:
            rule_status[period] = "index_window_missing_or_misaligned"
            return None, None, metric_date
        rule_status[period] = "evaluated"
        return stock_return, index_return, metric_date

    def _add(level, tag, desc, score, period, metric_date):
        signals.append(
            {
                "level": level,
                "tag": tag,
                "desc": f"{desc}（数据日 {metric_date}）",
                "score": score,
                "period": period,
                "as_of_date": metric_date,
            }
        )

    stock_return, index_return, metric_date = _inputs("ret_3d", "3d")
    if stock_return is not None and index_return is not None:
        deviation = calc_official_deviation(stock_return, index_return)
        if board == "主板" and 18 <= abs(deviation) < 20:
            _add(
                "卡异动",
                "💎",
                f"3日偏离值{deviation:+.2f}%，距主板20%红线仅差{20-abs(deviation):.2f}%",
                abs(deviation),
                "3d",
                metric_date,
            )
        elif board in ("创业板", "科创板") and 27 <= abs(deviation) < 30:
            _add(
                "卡异动",
                "💎",
                f"3日偏离值{deviation:+.2f}%，距{board}30%红线仅差{30-abs(deviation):.2f}%",
                abs(deviation),
                "3d",
                metric_date,
            )
        if abs(deviation) >= threshold:
            hist_count = None
            try:
                if not code.startswith(("8", "4")):
                    hist_count, _, _ = count_history_deviations(
                        code, idx_code, index_bars_pool, metric_date, 10
                    )
            except Exception as error:
                _debug_log(f"mak hist_deviation error {code}: {error}")
            count_note = ""
            if hist_count is not None and board == "主板" and hist_count >= 3:
                count_note = f" ⚠️ 近10个交易日已触发{hist_count}次同向异动！再触发1次停牌核查！"
            elif hist_count is not None and board in ("创业板", "科创板") and hist_count >= 2:
                count_note = f" ⚠️ 近10个交易日已触发{hist_count}次同向异动！再触发1次停牌核查！"
            turnover, _ = _metric_for_date(s, "turnover", metric_date, require_close_quote=True)
            volume_note = ""
            if turnover is not None and turnover < _vol_locked:
                volume_note = " [极度锁仓，动能强劲]"
            elif turnover is not None and turnover > _vol_overload:
                volume_note = " [爆量滞涨，警惕派发]"
            _add(
                "已触发",
                "🔥" if deviation > 0 else "💥",
                f"3日偏离值{deviation:+.2f}%≥{threshold}%({board})触发短期异动{volume_note}{count_note}",
                abs(deviation),
                "3d",
                metric_date,
            )

    stock_return, index_return, metric_date = _inputs("ret_10d", "10d")
    if stock_return is not None and index_return is not None:
        deviation = calc_official_deviation(stock_return, index_return)
        ceiling = 100 - deviation if deviation > 0 else None
        ceiling_note = ""
        if ceiling is not None and ceiling > 0:
            remaining_stops = ceiling / limit_pct_for(code, name)
            if remaining_stops <= 3:
                ceiling_note = f" 距100%仅剩{ceiling:.1f}%（约{remaining_stops:.1f}涨停）！"
        if deviation >= _ret10_warn:
            _add(
                "严重",
                "🔥🔥",
                f"10日偏离值{deviation:+.2f}%≥+{_ret10_warn:.0f}%，触发严重异动！{ceiling_note}",
                deviation,
                "10d",
                metric_date,
            )
        elif deviation <= _ret10_down:
            _add(
                "严重",
                "💥💥",
                f"10日偏离值{deviation:+.2f}%≤{_ret10_down:.0f}%，触发严重异动",
                -deviation,
                "10d",
                metric_date,
            )
        elif ceiling is not None and ceiling <= 15:
            _add(
                "严重预警",
                "🚨",
                f"10日偏离值{deviation:+.2f}%（距100%仅剩{ceiling:.1f}%）{ceiling_note}",
                deviation,
                "10d",
                metric_date,
            )

    stock_return, index_return, metric_date = _inputs("ret_20d", "20d")
    if stock_return is not None and index_return is not None:
        deviation_20d = calc_official_deviation(stock_return, index_return)
        if deviation_20d >= 100:
            _add(
                "严重",
                "🔥🔥🔥",
                f"20日偏离值{deviation_20d:+.2f}%≥+100%，触发严重异动！",
                deviation_20d,
                "20d",
                metric_date,
            )
        elif deviation_20d <= -50:
            _add(
                "严重",
                "💥💥💥",
                f"20日偏离值{deviation_20d:+.2f}%≤-50%，触发严重异动",
                -deviation_20d,
                "20d",
                metric_date,
            )
    return {"signals": signals, "rule_status": rule_status}


def check_stock(s, idx_rets, index_bars_pool):
    """Return verified anomaly signals while retaining the historical list return shape."""
    return _evaluate_stock(s, idx_rets, index_bars_pool)["signals"]


# Part 2: Sector rotation engine + generate_sector_report + __main__

_INDUSTRY_ALIASES = {
    # V16.0: 仅保留明确同义的映射；删除以偏概全的错配
    # （医药制造≠化学制药、电子信息≠光学光电子、化工行业≠化学制品、
    #   农牧饲渔≠种植业、公用事业≠电力、新能源≠光伏设备）
    "酿酒行业": "酿酒行业",
    "食品饮料": "食品饮料",
    "家电行业": "家电行业",
    "汽车整车": "汽车整车",
    "汽车零部件": "汽车零部件",
    "医药制造": "医药制造",
    "化学制药": "化学制药",
    "医疗器械": "医疗器械",
    "医药商业": "医药商业",
    "电子元件": "电子元件",
    "光学光电子": "光学光电子",
    "软件开发": "软件开发",
    "通信服务": "通信服务",
    "互联网服务": "互联网服务",
    "银行": "银行",
    "保险": "保险",
    "证券": "证券",
    "房地产开发": "房地产开发",
    "水泥建材": "水泥建材",
    "建筑装饰": "建筑装饰",
    "通用设备": "通用设备",
    "电力": "电力",
    "公用事业": "公用事业",
    "光伏设备": "光伏设备",
    "工业金属": "工业金属",
    "钢铁": "钢铁",
    "煤炭开采": "煤炭开采",
    "石油石化": "石油石化",
    "化学制品": "化学制品",
    "农牧饲渔": "农牧饲渔",
    "种植业": "种植业",
    "养殖业": "养殖业",
    "航天装备": "航天装备",
    "船舶制造": "船舶制造",
    "环境治理": "环境治理",
    "物流": "物流",
    "航空机场": "航空机场",
}


def normalize_industry(bk_name):
    if not isinstance(bk_name, str) or not bk_name.strip():
        return "其他"
    bk_name = bk_name.strip()
    if bk_name in _INDUSTRY_ALIASES:
        return _INDUSTRY_ALIASES[bk_name]
    for kw, target in _INDUSTRY_ALIASES.items():
        if kw in bk_name or bk_name in kw:
            return target
    return bk_name


def get_all_sectors():
    """V4: 两阶段评分 — 第1轮 change_pct 粗选前50，第2轮 board_members 精评。

    V15.1: 当 TDX/东财 HTTP 不可用时，自动旁路到 ZHB tdxstat + industry_code
          自聚合板块行情（覆盖 ~90% 申万行业），确保 mak 报告 C/D/E/F 不空白。
    V16.3 L（push2 风控治本）: 优先级反转——**ZHB 旁路优先**（_build_sectors_from_zhb
          129 申万二级板块全成员、零网络、零 push2）；TDX board_list 仅当 ZHB 失败时兜底。
          原 TDX→东财 路径的 BK 码与 MAC 成员码体系不匹配 → 每板块 fallback push2 clist
          （100 次）→ 2026-08-06 实跑触发 push2 风控。
    """
    sectors = _build_sectors_from_zhb()
    if not sectors:
        sectors = tdx_get_board_list(0)
        if not sectors:
            return []
    # 第1轮: 所有板块粗评分（仅涨跌幅），取前 50 进入精评
    for s in sectors:
        sc = s["change_pct"]
        s["_rough"] = (
            30 if sc > 3 else (20 if sc > 1 else (10 if sc > 0 else (-10 if sc < -2 else 0)))
        )
        s["up_count"] = s.get("up_count", 0)
        s["down_count"] = s.get("down_count", 0)
        s["amount_yi"] = s.get("amount_yi", 0)
        s["main_inflow"] = s.get("main_inflow", 0)
        s["_member_codes"] = s.get("_member_codes", [])
        s["_member_count"] = s.get("_member_count", 0)
        s["leader_change"] = s.get("leader_change", 0)
        s["leader"] = s.get("leader_name", s.get("leader", ""))
        s["mcap_yi"] = s.get("mcap_yi", 0)
        s["turnover"] = s.get("turnover", 0)
    sectors.sort(key=lambda x: x["_rough"], reverse=True)
    _top_n = min(50, len(sectors))
    # 第2轮: 前 50 板块精评（成分股成交额 + 涨跌家数 + 主力净流）
    for i in range(_top_n):
        s = sectors[i]
        if s.get("_member_count", 0) > 0:
            # ZHB 旁路路径已有 _member_codes/up_count/down_count/amount_yi/main_inflow
            continue
        members = get_sector_stocks(s["code"])
        if members:
            s["up_count"] = sum(1 for m in members if m.get("change_pct", 0) > 0)
            s["down_count"] = sum(1 for m in members if m.get("change_pct", 0) < 0)
            s["amount_yi"] = sum(m.get("amount_yi", 0) for m in members)
            s["main_inflow"] = sum(m.get("main_net_amount", 0) for m in members)
            s["_member_codes"] = [m["code"] for m in members]
            s["_member_count"] = len(members)
    return sectors


def _build_sectors_from_zhb() -> List[Dict[str, Any]]:
    """V15.1: 从 ZHB tdxstat 全市场快照 + industry_code 自聚合板块行情。

    数据源：get_zhb_full_market_snapshot()（纯内存 dict 提取，零网络）。
    每个行业聚合：
      - change_pct: 板块内加权涨跌幅（按市值权重）
      - amount_yi: 板块成分股成交额之和
      - main_inflow: 板块主力净流入之和
      - up_count / down_count: 板块涨跌家数
      - leader_name / leader_change: 板块涨幅最大股
      - _member_codes: 板块成分股代码列表
    """
    try:
        from stock_common.sc_datasource import get_zhb_full_market_snapshot
        from core.zhb_client import get_zhb

        snap = get_zhb_full_market_snapshot()
        if not snap:
            return []
        zhb = get_zhb()
        if zhb is None:
            return []
        industry_map = zhb.industry_map  # 行业代码 → 名称

        # V16.0: 腾讯实时覆盖 change_pct（板块涨幅口径与个股 A 段一致）
        # 原实现直接用 ZHB T-1 快照 change_pct → 板块涨幅反映昨日，个股反映今日，口径错位
        # V16.3 O27: 同时记录腾讯 T 日成交额（amount_wan），板块 amount_yi 改为 T 日聚合
        _tencent_rt: Dict[str, Dict[str, float]] = {}
        try:
            from core.tdx_client import _tencent_batch_fallback

            _tm = _tencent_batch_fallback(list(snap.keys())) or {}
            for _code, _tq in _tm.items():
                # V16.3 O21: 平盘（0%）也是今日事实——is not None 判定，0 不回退 ZHB T-1
                _entry: Dict[str, float] = {}
                if _tq.get("change_pct") is not None:
                    _entry["change_pct"] = _safe_float(_tq.get("change_pct", 0))
                _amt = _safe_float(_tq.get("amount_wan", 0))
                if _amt > 0:
                    _entry["amount_wan"] = _amt
                # 2026-08-11: 注入腾讯 mcap_yi/price——修复板块市值加权恒退化（ZHB 快照无 mcap_yi）
                _mcap = _safe_float(_tq.get("mcap_yi", 0))
                if _mcap > 0:
                    _entry["mcap_yi"] = _mcap
                _tq_price = _safe_float(_tq.get("price", 0))
                if _tq_price > 0:
                    _entry["price"] = _tq_price
                if _entry:
                    _tencent_rt[_code] = _entry
        except Exception as _e:
            _debug_log(f"mak ZHB sectors tencent cover: {_e}")

        # 按行业分组 —— V16.2.17: 统一东财申万二级行业（datacenter 低风险一次性映射），
        # Col[13] 仅作兜底（且只接受行业段 8803/8804/881，实测大量风格板块污染）
        _em_ind_map: Dict[str, str] = {}
        try:
            from stock_common import get_em_industry_l2_data

            _em_ind_map, _ = get_em_industry_l2_data()
        except Exception as _e:
            _debug_log(f"mak em industry map: {_e}")
        buckets: Dict[str, Dict[str, Any]] = {}
        for code, stat in snap.items():
            ind_code = stat.get("industry_code", "")
            # 东财一级优先（申万口径统一）；无映射时用 Col[13] 行业段兜底
            ind_code = _em_ind_map.get(code, "") or (
                ind_code if _is_industry_code(ind_code) else ""
            )
            if not ind_code:
                continue
            # V16.0: 优先用腾讯实时涨跌幅（今日盘中），否则退回 ZHB T-1
            _rt = _tencent_rt.get(code)
            _rt_chg = _rt.get("change_pct") if _rt else None
            chg = _rt_chg if _rt_chg is not None else (stat.get("change_pct", 0) or 0)
            # V16.3 O27: 板块成交额改腾讯 T 日聚合（amount_wan 万→亿），
            # 原 ZHB T-1 amount 盘中失真（成交额是昨日）；腾讯缺失时退回 T-1
            _rt_amt = _rt.get("amount_wan") if _rt else None
            amt = (
                (_rt_amt / 10000.0) if _rt_amt else ((stat.get("amount", 0) or 0) / 10000.0)
            )  # 万→亿
            # 2026-08-11: 修复恒 0——腾讯 mcap_yi → price×股本计算兜底（与 val 4 级兜底同思路）
            _rt_mcap = _safe_float(_rt.get("mcap_yi", 0)) if _rt else 0
            mcap = _rt_mcap
            if not mcap:
                _rt_price = _safe_float(_rt.get("price", 0)) if _rt else 0
                _base = _rt_price if _rt_price > 0 else (_safe_float(stat.get("price", 0) or 0))
                if _base > 0:
                    mcap = _safe_float(_calc_mcap_yi(code, _base) or 0)
            # V17.0.16: 板块主力净流入使用 ulist 批量 f62（真主力，带符号），
            # 不再用 ZHB main_net_buy_amount（实为竞价额恒正）。
            main_net = _MAIN_NET_MAP_GLOBAL.get(code, 0.0)
            if not main_net:
                # ZHB 的 main_net_buy_amount 是竞价额，不是主力净流入；缺失时保持 0，
                # 避免把正的竞价成交额误计入板块资金流。
                main_net = 0.0
            b = buckets.setdefault(
                ind_code,
                {
                    "_codes": [],
                    "_chgs": [],
                    "_amts": [],
                    "_mcaps": [],
                    "_main_inflow": 0.0,
                    "_up": 0,
                    "_down": 0,
                    "_best_chg": -999.0,
                    "_best_code": "",
                    "_best_name": "",
                },
            )
            b["_codes"].append(code)
            b["_chgs"].append(chg)
            b["_amts"].append(amt)
            b["_mcaps"].append(mcap)
            b["_main_inflow"] += main_net
            if chg > 0:
                b["_up"] += 1
            elif chg < 0:
                b["_down"] += 1
            if chg > b["_best_chg"]:
                b["_best_chg"] = chg
                # 用 ZHB name fallback 取股票名
                b["_best_code"] = code
                b["_best_name"] = zhb.get_stock_name(code) or ""

        # 转成 sectors 列表
        sectors = []
        for ind_code, b in buckets.items():
            # 加权涨跌幅（市值权重）
            total_mcap = sum(b["_mcaps"])
            if total_mcap > 0:
                weighted_chg = sum(c * m for c, m in zip(b["_chgs"], b["_mcaps"])) / total_mcap
            else:
                weighted_chg = sum(b["_chgs"]) / len(b["_chgs"]) if b["_chgs"] else 0
            sectors.append(
                {
                    "code": ind_code,
                    "name": industry_map.get(ind_code, ind_code),
                    "change_pct": round(weighted_chg, 2),
                    "price": 0,
                    "up_count": b["_up"],
                    "down_count": b["_down"],
                    "amount_yi": round(sum(b["_amts"]), 2),
                    "main_inflow": b["_main_inflow"],  # 元（V16.0 已从万元统一为元）
                    "_member_codes": b["_codes"],
                    "_member_count": len(b["_codes"]),
                    "leader_name": b["_best_name"],
                    "leader_change": round(b["_best_chg"], 2),
                    "mcap_yi": round(total_mcap, 2),
                    "turnover": 0,
                }
            )
        _debug_log(f"mak ZHB sectors: {len(sectors)} 个板块（聚合自 {len(snap)} 只股票）")
        return sectors
    except Exception as _e:
        _debug_log(f"mak _build_sectors_from_zhb: {_e}")
        return []


def get_sector_stocks(sector_code):
    """V4: 板块成分股 → TDX board_members 替代 push2"""
    members = tdx_get_board_members(sector_code)
    if not members:
        return []
    stocks = []
    for m in members:
        stocks.append(
            {
                "code": m["code"],
                "name": m["name"],
                "change_pct": m.get("change_pct", 0),
                "price": m.get("price", 0),
                "mcap_yi": m.get("mcap_yi", 0),
                "turnover": m.get("turnover", 0),
                "amount_yi": (
                    m.get("mcap_yi", 0) * m.get("turnover", 0) / 100
                    if m.get("turnover", 0) > 0
                    else 0
                ),
                "main_net_amount": m.get("main_net_amount", 0),
            }
        )
    return stocks


# V7: get_recent_dragon_tiger 由 stock_common 统一提供


async def get_ths_hot_pool(date_str):
    """V17.0 S4: 请求统一走 sc_datasource.get_ths_hot_raw(三版收敛), 本地保留加工。

    加工: 涨跌幅 snapshot 交叉修正 + 过滤 0 涨跌 + 按涨跌幅降序。
    """
    from stock_common.sc_datasource import get_ths_hot_raw

    try:
        items = await asyncio.to_thread(get_ths_hot_raw, date_str)
        if not items:
            return []
        rows = []
        codes = []
        for item in items:
            code = str(item.get("code", ""))
            if not code:
                continue
            codes.append(code)
            rows.append(
                {
                    "code": code,
                    "name": item.get("name", ""),
                    "reason": item.get("reason", ""),
                    "zhangfu": _safe_float(item.get("zhangfu", item.get("change", 0))),
                }
            )
        quotes = await get_market_snapshot_async(codes)
        for row in rows:
            q = quotes.get(row["code"], {})
            tdx_change = q.get("change_pct", 0)
            if tdx_change != 0:
                row["zhangfu"] = tdx_change
        rows = [r for r in rows if r["zhangfu"] != 0]
        rows.sort(key=lambda x: x["zhangfu"], reverse=True)
        return rows
    except Exception as e:
        print(f"get_ths_hot_pool error: {e}", flush=True)
        return []


def compute_rotation_scores(sectors):
    if not sectors:
        return {}
    for s in sectors:
        score = 0.0
        sc = s["change_pct"]
        if sc > 3:
            score += 30
        elif sc > 1:
            score += 20
        elif sc > 0:
            score += 10
        elif sc < -2:
            score -= 10
        a_yi = s.get("amount_yi", 0)
        if a_yi > 200:
            score += 20
        elif a_yi > 50:
            score += 10
        if sc > 0 and (s.get("up_count", 0) / max(s.get("down_count", 0) + 1, 1)) > 3:
            score += 15
        if s.get("main_inflow", 0) > 0:
            score += 10
        if s.get("leader_change", 0) > 3:
            score += 10
        s["score"] = round(score, 1)
    return {s["name"]: s for s in sectors}


def analyze_top_stocks(top_sectors):
    result = []
    _sec_cache = {}
    # V16.0: ZHB 旁路板块（_member_codes 非空）优先从全市场快照构建成分股，
    # 避免 get_sector_stocks(申万代码) 强制补 BK 前缀导致 E 段成分股总数 0 只。
    _zhb_member_stocks_cache: Dict[str, List[Dict]] = {}

    def _zhb_member_stocks(member_codes: List[str]) -> List[Dict]:
        if not member_codes:
            return []
        key = "|".join(sorted(member_codes))
        if key in _zhb_member_stocks_cache:
            return _zhb_member_stocks_cache[key]
        try:
            from stock_common.sc_datasource import get_zhb_full_market_snapshot

            snap = get_zhb_full_market_snapshot() or {}
            # V16.3 J: 名称兜底用腾讯批量（profile 仅覆盖 1644 只，缺失时显示 code(code)）
            _tq_names = {}
            # V16.3 O22: _tm 在 try 前初始化（原仅 try 内赋值——异常时 E 段整段 NameError 丢失）
            _tm: dict = {}
            try:
                from core.tdx_client import _tencent_batch_fallback

                _tm = _tencent_batch_fallback(member_codes) or {}
                _tq_names = {_c: _q.get("name", "") for _c, _q in _tm.items() if _q.get("name")}
            except Exception as _e:
                _debug_log(f"mak E tencent names: {_e}")
            from core.zhb_client import get_stock_name_from_zhb

            stocks = []
            for _c in member_codes:
                _st = snap.get(_c) or {}
                _tq = _tm.get(_c) or {}
                # V16.3 O21: E 段成分股 change_pct 优先腾讯 T 日实时（原只用于 name——
                # 盘中运行 E 段"涨停梯队/龙头"实为昨日名单，与 D 段板块 T 日口径错位）
                _cp = (
                    _safe_float(_tq.get("change_pct"))
                    if _tq.get("change_pct") is not None
                    else _safe_float(_st.get("change_pct", 0))
                )
                _mc = _safe_float(_st.get("mcap_yi", 0))
                _to = _safe_float(_st.get("turnover", 0))
                # V17.0.8: 名称优先级——腾讯实时名优先(T 日), ZHB/TDX 名含历史旧名
                # (霞客环保→协鑫能科/哈高科→湘财股份/二纺机→市北高新) 仅兜底
                _nm = _tq_names.get(_c, "") or get_stock_name_from_zhb(_c) or _c
                stocks.append(
                    {
                        "code": _c,
                        "name": _nm,
                        "change_pct": _cp,
                        "price": _safe_float(_tq.get("price") or _st.get("price", 0)),
                        "mcap_yi": _mc,
                        "turnover": _to,
                        "amount_yi": (
                            _safe_float(_tq.get("amount_wan", 0)) / 10000.0
                            if _tq.get("amount_wan")
                            else (
                                _safe_float(_st.get("amount", 0)) / 10000.0
                                if _st.get("amount", 0)
                                else 0
                            )
                        ),
                        # 仅使用 ulist f62；ZHB main_net_buy_amount 是竞价金额代理，不是主力净额。
                        "main_net_amount": _verified_main_net_amount(_c),
                        # [ENRICH] 区间收益 + 已验证的 ulist f62 主力净额(零新增取数)
                        "ret_5d": _safe_float(_st.get("change_5d", 0)),
                        "ret_10d": _safe_float(_st.get("change_10d", 0)),
                        "ret_20d": _safe_float(_st.get("change_20d", 0)),
                        "ret_60d": _safe_float(_st.get("change_60d", 0)),
                        "main_inflow": _verified_main_net_amount(_c),
                    }
                )
            _zhb_member_stocks_cache[key] = stocks
            return stocks
        except Exception as _e:
            _debug_log(f"mak analyze_top_stocks zhb members: {_e}")
            return []

    for s in top_sectors:
        if s["code"] in _sec_cache:
            stocks = _sec_cache[s["code"]]
        elif s.get("_member_codes"):
            # V16.0: ZHB 旁路板块直接用已聚合成员代码
            stocks = _zhb_member_stocks(s["_member_codes"])
            _sec_cache[s["code"]] = stocks
        else:
            stocks = get_sector_stocks(s["code"])
            _sec_cache[s["code"]] = stocks
        _sec_code = s["code"]
        # V16.0: 用统一 is_limit_up 判断涨停（ST 10% 与主板一致），替代硬编码 19.5/9.5
        # V16.2: 统一用 limit_pct_for 阈值（主板/ST 10 / 创业板·科创板 20 / 北交所 30）
        _limit_thr = limit_pct_for(_sec_code, s.get("name", ""))
        limit_up = [
            st
            for st in stocks
            if is_limit_up(st["code"], st.get("name", ""), st.get("change_pct", 0))
        ]
        over7 = [st for st in stocks if 7 <= st.get("change_pct", 0) < _limit_thr]
        over5 = [st for st in stocks if 5 <= st.get("change_pct", 0) < 7]
        _leaders = limit_up[:3]
        if len(_leaders) < 3:
            _backup = [st for st in over7 if st not in _leaders]
            _leaders += _backup[: 3 - len(_leaders)]
        if len(_leaders) < 3:
            _backup2 = [st for st in over5 if st not in _leaders]
            _leaders += _backup2[: 3 - len(_leaders)]
        # TOP5涨幅（取前5只）
        _top5 = sorted(stocks, key=lambda x: x.get("change_pct", 0) or 0, reverse=True)[:5]
        result.append(
            {
                "sector": s["name"],
                "data": s,
                "total_stocks": len(stocks),
                "limit_up_count": len(limit_up),
                "over7_count": len(over7),
                "over5_count": len(over5),
                "limit_up_stocks": [
                    {"code": st["code"], "name": st["name"], "change_pct": st.get("change_pct", 0)}
                    for st in _leaders
                ],
                # V17.0.8: 涨停全量名单（E 段"涨停家数 → 名单"须与 count 严格一致，
                # 原用 _leaders(含 over7/over5 替补) 导致声称3只实际只1只涨停的误导）
                "limit_up_all": [
                    {"code": st["code"], "name": st["name"], "change_pct": st.get("change_pct", 0)}
                    for st in limit_up
                ],
                "top5_stocks": [
                    {
                        "code": st["code"],
                        "name": st["name"],
                        "change_pct": st.get("change_pct", 0),
                        "ret_5d": _safe_float(st.get("ret_5d", 0)),
                        "ret_10d": _safe_float(st.get("ret_10d", 0)),
                        "ret_20d": _safe_float(st.get("ret_20d", 0)),
                        "ret_60d": _safe_float(st.get("ret_60d", 0)),
                        "turnover": _safe_float(st.get("turnover", 0)),
                        "mcap_yi": _safe_float(st.get("mcap_yi", 0)),
                        "main_inflow": _safe_float(st.get("main_inflow", 0)),
                    }
                    for st in _top5
                ],
            }
        )
    return result


def annotate_technical_pattern(code):
    try:
        closes, _ = get_tdx_kline(code, 25)
        if len(closes) < 20:
            return ""
        p = closes[-1]
        if p <= 0:
            return ""
        ma5 = sum(closes[-5:]) / 5
        ma10 = sum(closes[-10:]) / 10
        ma20 = sum(closes[-20:]) / 20
        tags = []
        if p > ma20 and all(closes[-i] > closes[-i - 1] for i in range(1, 4)):
            tags.append("多头排列")
        elif p > ma20 and closes[-1] > closes[-2] and closes[-2] <= ma20:
            tags.append("突破MA20")
        elif p > ma10 and closes[-1] > closes[-2] and closes[-2] <= ma10:
            tags.append("突破MA10")
        if ma5 > ma10 > ma20:
            tags.append("均线多头")
        return " | ".join(tags) if tags else ""
    except (ValueError, TypeError, IndexError):
        return ""


async def generate_sector_report(output_path):
    _td = date.today()
    if not is_trading_day(_td):
        from stock_common.stock_calendar import previous_trading_day

        _td = previous_trading_day(_td)
    today_str = _td.strftime("%Y-%m-%d")
    now = datetime.now()
    _mkt_status, _mkt_note = get_market_status(now)
    lines = []

    def L(s=""):
        lines.append(s)

    L("=" * 90)
    # V17.0.2i: 头部拆分(报告名/时间+时段分行)——原一行过长
    L("  **📊 A股异动及行业轮动扫描报告**")
    L(f"  ⏱ 生成时间 {now.strftime('%Y-%m-%d %H.%M.%S')} | {_mkt_note}")
    L("=" * 90)
    print("[数据装载] 获取全市场多日数据与指数基准...", flush=True)
    _t0 = time.time()
    all_stocks = await get_market_abnormal_data()
    # V16.2.7: ZHB 全市场快照含 ETF/LOF/可转债（7948 只）——选股无意义且拖慢扫描，
    # 过滤为纯 A 股（与 val 的 _is_a_stock 同口径：00/30/60/68/92 前缀）
    _before = len(all_stocks)
    all_stocks = [s for s in all_stocks if _is_a_stock(s.get("code", ""))]
    # ELTDX 天梯按本次 A 股代码范围查询；上游 limit_ladder 内部会构建 shortline 指标。
    _eltdx_ladder = []
    try:
        from core.eltdx_adapter import get_eltdx_limit_ladder

        _eltdx_ladder = await asyncio.to_thread(
            get_eltdx_limit_ladder,
            codes=[s.get("code", "") for s in all_stocks if s.get("code")],
        )
    except Exception as _e:
        _debug_log(f"mak eltdx limit_ladder: {_e}")
    if len(all_stocks) < _before:
        print(
            f"  📋 A股过滤: 移除 {_before - len(all_stocks)} 只 ETF/LOF/可转债（{_before} → {len(all_stocks)}）",
            flush=True,
        )
    from stock_common.stock_calendar import latest_market_data_date

    _target_data_date = latest_market_data_date(now).isoformat()
    _zhb_date = _normalize_mak_date(get_zhb_data_date())
    _zhb_check_as_of = datetime.now()
    _zhb_fresh = is_zhb_data_fresh(max_delay_days=3, data_date=_zhb_date, as_of=_zhb_check_as_of)
    _zhb_age = None
    if _zhb_date:
        try:
            from stock_common.stock_calendar import trading_day_age

            _zhb_age = trading_day_age(date.fromisoformat(_zhb_date), as_of=_zhb_check_as_of)
        except (TypeError, ValueError, NotImplementedError) as _e:
            _debug_log(f"mak zhb snapshot age ({_zhb_date}): {_e}")
    if _zhb_date:
        if _zhb_age is None:
            _fresh_tag = "有效交易日龄无法核实"
        elif _zhb_age < 0:
            _fresh_tag = "日期晚于当前行情基准日，需复核"
        elif _zhb_age == 0:
            _fresh_tag = "与当前行情基准日一致"
        else:
            _fresh_tag = f"滞后 {_zhb_age} 个有效交易日"
        if _zhb_age is None or _zhb_age < 0:
            _tolerance_tag = "容限状态无法核实"
        elif _zhb_fresh:
            _tolerance_tag = "在3个交易日容限内"
        else:
            _tolerance_tag = "超出3个交易日容限"
        L(f"  ZHB全市场快照数据日：{_zhb_date}（{_fresh_tag}；{_tolerance_tag}）")
        print(
            f"  ⚡ zhb全市场: {len(all_stocks)}只（{_zhb_date}；{_fresh_tag}；{_tolerance_tag}），"
            f"耗时{time.time()-_t0:.2f}s",
            flush=True,
        )
    else:
        L("  ZHB全市场快照数据日：未确认")
    L(
        f"  目标行情日：{_target_data_date}；当前异动只评估该数据日。逐字段核验来源日期，收盘异动仅采用 15:00 后的腾讯时间戳或收盘后的同日 ZHB 快照。"
    )
    _index_dates = [_target_data_date]
    if _zhb_date and _zhb_date != _target_data_date:
        _index_dates.append(_zhb_date)
    idx_rets_by_date, index_bars_pool = get_index_returns(_index_dates)
    for ic, nm in INDEX_MAP.items():
        r = (idx_rets_by_date.get(_target_data_date) or {}).get(ic, {})
        L(f"  📈 {nm}: 3日{_fmt_ret(r.get('ret_3d'))}%  10日{_fmt_ret(r.get('ret_10d'))}%")
    print("[异动引擎] 扫描全市场异动信号...", flush=True)
    results = {"卡异动": [], "已触发": [], "严重": [], "严重预警": []}
    rule_evaluations = {period: {"evaluated": 0, "reasons": {}} for period in ("3d", "10d", "20d")}

    # V9.3.3: 并行扫描（ThreadPoolExecutor）；V17.3.12 并行度改走命名常量 MAK_SCAN_WORKERS。
    # 注：实测 3→6 不提速(纯CPU下GIL反慢、CPU+I/O混合仅快~3%噪声内)，故常量值保持 3（见下定义处注释）。
    def _check_one(s):
        """Return verified signals and explicit per-window evaluation status."""
        try:
            evaluation = _evaluate_stock(
                s, idx_rets_by_date, index_bars_pool, expected_data_date=_target_data_date
            )
            return (s["code"], s["name"], evaluation)
        except Exception as _e:
            _debug_log(f"mak check_stock error {s['code']}: {_e}")
            return (
                s["code"],
                s["name"],
                {
                    "signals": [],
                    "rule_status": {period: "evaluation_error" for period in rule_evaluations},
                },
            )

    with ThreadPoolExecutor(max_workers=MAK_SCAN_WORKERS) as executor:
        futures = {executor.submit(_check_one, s): s for s in all_stocks}
        for i, future in enumerate(as_completed(futures)):
            if i % 1000 == 0:
                print(f"  已扫描 {i}/{len(all_stocks)}", flush=True)
            try:
                code, name, evaluation = future.result()
                for period, status in evaluation["rule_status"].items():
                    counter = rule_evaluations.setdefault(period, {"evaluated": 0, "reasons": {}})
                    if status == "evaluated":
                        counter["evaluated"] += 1
                    else:
                        counter["reasons"][status] = counter["reasons"].get(status, 0) + 1
                for r in evaluation["signals"]:
                    results[r["level"]].append({**r, "code": code, "name": name})
            except Exception as _e:
                _debug_log(f"mak future.result error: {_e}")
    total_abnormal = len(results["已触发"]) + len(results["严重"])
    _current_changes = {
        s["code"]: _metric_for_date(s, "change_pct", _target_data_date, require_close_quote=True)[0]
        for s in all_stocks
    }
    _current_changes = {
        code: value for code, value in _current_changes.items() if value is not None
    }
    _zt_count = sum(
        1
        for s in all_stocks
        if _current_changes.get(s["code"]) is not None
        and is_limit_up(s["code"], s.get("name", ""), _current_changes[s["code"]])
    )
    _dt_count = sum(
        1
        for s in all_stocks
        if _current_changes.get(s["code"]) is not None
        and is_limit_down(s["code"], s.get("name", ""), _current_changes[s["code"]])
    )
    L(f"\n{'='*90}")
    L("## 【A. 全市场情绪监测看板】")
    L(f"{'---'}")
    L(
        "  说明：涨跌广度和涨跌停计数只统计与目标行情日一致且已确认收盘时点的个股涨跌幅；"
        "缺失、日期不符或收盘前快照不计为零。个股异动规则按各指标自身数据日与指数同日窗口分别评估。"
    )
    # V17.0(2026-08-15): 北向宏观资金 + 两融杠杆情绪(A 段增强, P4)
    try:
        from stock_common.sc_datasource import get_hsgt_macro_flow

        # ⚠️ 修复(2026-08-15): 同步网络调用在 async 上下文会阻塞事件循环 → to_thread 包装
        _hsgt = await asyncio.to_thread(get_hsgt_macro_flow)
        if _hsgt:
            # V17.0.4(2026-08-19): invalid → 同花顺 hgt/sgt 序列错位, 末值恒陈旧——不展示错误数字
            if _hsgt.get("data_quality") == "invalid":
                L("  🌐 北向资金: 数据源异常(hgt/sgt 序列错位), 净流入暂缺")
            elif _hsgt.get("data_quality") == "partial_hgt_only":
                # V17.0.28: hgt=当日分时(可用), sgt=历史序列(不可用) → 只展示沪股通并声明单口径
                _hsig = "偏多" if _hsgt.get("hgt", 0) > 0 else "偏空"
                L(
                    f"  🌐 北向资金: 沪股通 {_hsgt.get('hgt', 0):+.2f}亿（{_hsig}）"
                    f" | 深股通序列为历史值暂缺，本项为沪股通单口径，非北向合计"
                )
            else:
                _hsig = "偏多" if _hsgt.get("total", 0) > 0 else "偏空"
                L(
                    f"  🌐 北向资金: 净流入 {_hsgt.get('total', 0):.2f} 亿(沪 {_hsgt.get('hgt', 0):.2f} | 深 {_hsgt.get('sgt', 0):.2f}) 外资情绪{_hsig}"
                )
                # M13 修复(2026-08-15 二审): 数据降级标记(与 med 一致, 2026-08-12 深股通 379.75 亿异常)
                if _hsgt.get("data_quality") == "degraded":
                    L("  ⚠️ 北向资金数据源存疑(异常波动), 仅供参考")
        else:
            L("  🌐 北向资金: (数据获取失败)")
    except Exception as _e:
        _debug_log(f"mak hsgt macro: {_e}")
    _up_cnt = sum(1 for value in _current_changes.values() if value > 0)
    _down_cnt = sum(1 for value in _current_changes.values() if value < 0)
    _flat_cnt = sum(1 for value in _current_changes.values() if value == 0)
    _ratio_text, _ = _market_breadth_display(_up_cnt, _down_cnt)
    _directional_samples = _up_cnt + _down_cnt
    _unverified_samples = max(0, len(all_stocks) - len(_current_changes))
    L(
        f"  🌡️ 样本观测(剔除ST/退): 涨停阈值命中{_zt_count} | 跌停阈值命中{_dt_count} | 异动触发{total_abnormal}只"
        f"（目标数据日 {_target_data_date}；有效收盘涨跌幅 {_directional_samples + _flat_cnt}/{len(all_stocks)}；"
        "与B段涨停池/通达信全市场口径不同，不可直接相加比较）"
    )
    L(
        f"  📊 样本涨跌广度观测: 上涨{_up_cnt}/下跌{_down_cnt} | 涨跌比{_ratio_text}"
        f" | 平盘{_flat_cnt}只 | 未确认/日期不符/收盘前{_unverified_samples}只（未当作平盘）"
    )
    for _period, _label in (("3d", "3日"), ("10d", "10交易日"), ("20d", "20交易日")):
        _coverage = rule_evaluations[_period]
        _reasons = _coverage["reasons"]
        _reason_text = "、".join(f"{key}:{value}" for key, value in sorted(_reasons.items()))
        L(
            f"  🔎 个股异动评估({_label}): {_coverage['evaluated']}/{len(all_stocks)} 可评估"
            + (f"；未评估原因 {_reason_text}" if _reason_text else "；无日期/窗口缺口")
        )
    # TDX 市场统计是独立的本次响应；接口未提供可核验数据日，不作同日交叉校验。
    try:
        from core.tdx_client import tdx_get_market_stat

        _ms = await asyncio.to_thread(tdx_get_market_stat)
        if _ms:
            _ms_ud, _ = _market_breadth_display(
                int(_ms.get("up_count", 0) or 0), int(_ms.get("down_count", 0) or 0)
            )
            L(
                "  📊 全市场(通达信·本次响应，接口未提供可核验数据日): "
                f"上涨{_ms['up_count']}/下跌{_ms['down_count']}"
                f" | 涨停{_ms['limit_up_count']}/跌停{_ms['limit_down_count']}"
                f" | 平{_ms['neutral_count']}/停牌{_ms['suspended_count']}"
                f" | 涨跌比{_ms_ud} | 总市值{_ms['total_market_cap']/1e12:.2f}万亿"
                "（通达信源端全市场口径，含 ST/退市整理/北交所）"
            )
    except Exception as _e:
        _debug_log(f"mak market stat: {_e}")

    # V17.0.5 P0: fuyao 竞价情绪聚合(短线风向标 benchmark——9:25 盘前即得, 时效领先叙事型情绪源)
    try:
        from stock_common import get_fuyao_auction_benchmark, is_fuyao_enabled

        if is_fuyao_enabled():
            _bench = await asyncio.to_thread(get_fuyao_auction_benchmark)
            if _bench:
                _n = len(_bench)
                _high_open = sum(
                    1 for b in _bench if any("高开" in str(t) for t in (b.get("tags") or []))
                )
                _vol_up = sum(
                    1 for b in _bench if any("放量" in str(t) for t in (b.get("tags") or []))
                )
                _pos_a = sum(1 for b in _bench if (b.get("auction_pct") or 0) > 0)
                if _n:
                    L(
                        f"  ⚡ 竞价风向标(fuyao, 样本{_n}): 高开标签 {_high_open} 只({_high_open/_n*100:.0f}%)"
                        f" | 放量 {_vol_up} 只({_vol_up/_n*100:.0f}%) | 竞价红盘 {_pos_a} 只({_pos_a/_n*100:.0f}%)"
                    )
                    if _high_open / _n > 0.5 and _vol_up / _n > 0.3:
                        L("    🔥 竞价高开+放量共振，开盘进攻氛围浓厚")
                    elif _pos_a / _n < 0.3:
                        L("    ⚠️ 竞价红盘占比不足三成，开盘防御为上")
        else:
            L("  ⚠️ 竞价风向标：fuyao 竞价数据未启用（无盘前 9:25 短线情绪基准，开盘氛围判断缺失）")
    except Exception as _e:
        _debug_log(f"mak fuyao auction benchmark: {_e}")

    # 市场情绪展示只采用已核实的 KPL 字段；CLS 聚合字段未定案，保留研究采集但不作报告解释。
    try:
        from stock_common import get_kpl_market_sentiment, get_kpl_plate_strength
        from stock_common.stock_calendar import latest_market_data_date

        _market_data_date = latest_market_data_date(now).isoformat()
        _kpl = await asyncio.to_thread(get_kpl_market_sentiment)
        if _kpl:
            _day_label = str(_kpl.get("day") or "未提供")
            L(f"  📊 开盘啦市场情绪指标（响应日期标签 {_day_label}；标签未确认为来源实际数据日）:")
            _kpl_parts = []
            if _kpl.get("ztjs") is not None:
                _kpl_parts.append(f"涨停家数 {_kpl['ztjs']} 只")
            if _kpl.get("lbgd") is not None:
                _kpl_parts.append(f"最高连续涨停 {_kpl['lbgd']} 板")
            if _kpl.get("df_num") is not None:
                _kpl_parts.append(f"大幅回撤个股数 {_kpl['df_num']} 只")
            if _kpl.get("strong") is not None:
                _kpl_parts.append(f"情绪指标分值 {_kpl['strong']}（0–100；非百分比或概率）")
            if _kpl_parts:
                L("  " + " | ".join(_kpl_parts))
            _tip = str(_kpl.get("tip") or "").strip()
            if _tip:
                L(f"  来源提示: {_tip[:160]}")

        # KPL 板块接口的请求日不是来源日期证明；字段映射/单位未定案，只展示接口原始值。
        _plates = await asyncio.to_thread(get_kpl_plate_strength, top_n=8, date=_market_data_date)
        if _plates:
            L(
                f"\n  🧭 开盘啦 ZSType=7 板块榜（请求数据日 {_market_data_date}；字段含义/单位未定案，仅展示接口原始值）:"
            )
            for _plate in _plates[:8]:
                _name = str(_plate.get("name") or "").strip()
                if not _name:
                    continue
                _parts = [_name]
                if _plate.get("strength") is not None:
                    _parts.append(f"col_02={_plate['strength']}")
                L("    " + " | ".join(_parts))
    except Exception as _e:
        _debug_log(f"mak kpl verified sentiment/plate strength: {_e}")

    # V10.3: 汇总本次扫描样本的主力净额；ZHB 竞价金额单独展示，不混作主力资金方向。
    _auction_amount_wan = 0.0
    if not _MAIN_NET_MAP_GLOBAL:
        _stat2_snapshot = get_zhb_market_stat2_snapshot()
        if _stat2_snapshot:
            _auction_amount_wan = sum(
                _safe_float(_stat.get("main_net_buy_amount", 0))
                for _stat in _stat2_snapshot.values()
            )
    for _flow_line in _main_flow_summary_lines(
        _MAIN_NET_MAP_GLOBAL,
        _MAIN_NET_REQUESTED_COUNT,
        _MAIN_NET_RETURNED_COUNT,
        zhb_auction_amount_wan=_auction_amount_wan,
        zhb_data_date=get_zhb_data_date() or "",
        source_status=_MAIN_NET_SOURCE_STATUS,
        source_date_note=_MAIN_NET_DATA_DATE_NOTE,
    ):
        L(_flow_line)
    _limit_up_samples = [
        s
        for s in all_stocks
        if _current_changes.get(s["code"]) is not None
        and is_limit_up(s["code"], s.get("name", ""), _current_changes[s["code"]])
    ]
    # 连板梯队只统计 ELTDX 明确返回的 ladder_level，不用近 3 日涨幅推算连板数。
    _ladder_counts: dict[str, int] = {}
    _max_board = 0
    _seen_ladder_codes: set[str] = set()
    for _row in _eltdx_ladder:
        if not isinstance(_row, dict):
            continue
        _raw_code = str(_row.get("code") or _row.get("full_code") or "").strip().lower()
        _plain_code = re.sub(r"^(sh|sz|bj)", "", _raw_code)
        if not _plain_code or _plain_code in _seen_ladder_codes:
            continue
        try:
            _raw_level = _row.get("ladder_level")
            if isinstance(_raw_level, bool):
                continue
            _level_value = float(_raw_level)
            if not math.isfinite(_level_value) or not _level_value.is_integer():
                continue
            _level = int(_level_value)
        except (TypeError, ValueError, OverflowError):
            continue
        if _level < 1:
            continue
        _seen_ladder_codes.add(_plain_code)
        _label = f"{_level}板" if _level <= 6 else "7板+"
        _ladder_counts[_label] = _ladder_counts.get(_label, 0) + 1
        _max_board = max(_max_board, _level)
    if _ladder_counts:
        _ladder_str = " | ".join(
            f"{k}: {v}只"
            for k, v in sorted(
                _ladder_counts.items(),
                key=lambda item: int(item[0].split("板")[0].replace("+", "")),
            )
        )
        L(f"  📊 连板梯队（通达信 ELTDX 返回记录）: {_ladder_str} | 最高 {_max_board} 板")
        L(
            "    ℹ️ 仅统计 ELTDX 返回且含有效 ladder_level 的记录；未返回记录不推定为首板或非连板，"
            "也不再用近 3 日涨幅估算连板数。KPL 最高连板字段在上方单独列示，不与本表混算。"
        )
    else:
        L(
            "  📊 连板梯队：本次未取得含有效 ladder_level 的 ELTDX 记录；"
            "不根据近 3 日涨幅估算板数，也不据此判断市场没有连板股。"
        )
    _up_abn = [r for r in results["已触发"] if r.get("tag") == "🔥"]
    if _up_abn:
        # V16.1: 原"异动信号回测(近似)"表述是伪回测（统计的是已上涨股票当前 ret_5d，
        # 非信号发出后的前瞻收益）→ 改为现状描述，不做胜率暗示
        _up_codes = list(dict.fromkeys(r["code"] for r in _up_abn))[:30]
        _signal_date_by_code = {
            r["code"]: r.get("as_of_date", "") for r in _up_abn if r["code"] in _up_codes
        }
        _ret5_values = []
        for _code in _up_codes:
            _stock = next((s for s in all_stocks if s["code"] == _code), None)
            if _stock is None:
                continue
            _ret5, _ = _metric_for_date(_stock, "ret_5d", _signal_date_by_code.get(_code, ""))
            if _ret5 is not None:
                _ret5_values.append(_ret5)
        if _ret5_values:
            _positive_ratio = (
                sum(1 for value in _ret5_values if value > 0) / len(_ret5_values) * 100
            )
            L(
                f"  📊 多头异动股同数据日近5交易日涨幅为正的比例: {_positive_ratio:.0f}%"
                f"（可对齐 {len(_ret5_values)}/{len(_up_codes)} 只，现状统计非前瞻回测）"
            )
        else:
            L("  📊 多头异动股近5交易日涨幅：没有与异动数据日对齐的有效样本，暂不计算比例。")
    L(f"{'---'}")
    L(
        f"  扫描汇总: 卡异动{len(results['卡异动'])}只 | 已触发{len(results['已触发'])}只 | 严重{len(results['严重'])}只"
    )
    _tech_cache = {}

    def _tech(code):
        if code not in _tech_cache:
            _tech_cache[code] = annotate_technical_pattern(code)
        return _tech_cache[code]

    items = sorted(results["卡异动"], key=lambda x: x["score"], reverse=True)
    if items:
        L("\n  💎 黄金控盘区 —— 精准卡异动标的（距红线不足2%）:")
        for r in items[:10]:
            _tt = _tech(r["code"])
            _tt_str = f" [{_tt}]" if _tt else ""
            L(f"    {r['tag']} {r['name']}({r['code']}){_tt_str}  {r['desc']}")
    items = sorted(results["严重预警"], key=lambda x: x["score"], reverse=True)
    if items:
        L("\n  🚨 雷区风控 —— 濒临严重异动/停牌:")
        for r in items[:8]:
            _tt = _tech(r["code"])
            _tt_str = f" [{_tt}]" if _tt else ""
            L(f"    🚨 {r['name']}({r['code']})  {r['desc']}")
    items = sorted(results["严重"], key=lambda x: x["score"], reverse=True)
    if items:
        # V16.4.1: 标题修正——"严重" 是 10日/20日偏离(非 3日"已触发"级别)
        L("\n  🔥🔥 严重异动 —— 10日/20日偏离值触发:")
        for r in items[:8]:
            ann_info = ""
            _tt = _tech(r["code"])
            _tt_str = f" [{_tt}]" if _tt else ""
            L(f"    {r['tag']} {r['name']}({r['code']}){_tt_str}  {r['desc']}{ann_info}")
    _up = sorted(
        [r for r in results["已触发"] if r.get("tag") == "🔥"],
        key=lambda x: x["score"],
        reverse=True,
    )
    _down = sorted(
        [r for r in results["已触发"] if r.get("tag") == "💥"],
        key=lambda x: x["score"],
        reverse=True,
    )
    if _up:
        L("\n  🔺 多头控盘 —— 新晋正向偏离异动:")
        for r in _up[:10]:
            L(f"    🔥 {r['name']}({r['code']})  {r['desc']}")
    if _down:
        L("\n  🔻 空头崩盘 —— 新晋负向偏离异动:")
        for r in _down[:5]:
            L(f"    💥 {r['name']}({r['code']})  {r['desc']}")
    # V17.3 (2026-09-10 mak 审查建议3): 复合异动标的——同票跨"卡异动/已触发/严重/严重预警"多严重度
    # 合并为分层严重度汇总, 减少同一标的在多处重复呈现; 各窗口明细仍保留于上方分级区(诊断价值)
    _combo = {}
    for _lv in ("严重", "严重预警", "已触发", "卡异动"):
        for _r in results[_lv]:
            _combo.setdefault(_r["code"], []).append(_lv)
    _combo_multi = {c: ls for c, ls in _combo.items() if len(ls) >= 2}
    if _combo_multi:
        _sev_order = {"严重": 0, "严重预警": 1, "已触发": 2, "卡异动": 3}
        L("\n  📌 复合异动标的（多窗口共振 · 分层严重度汇总）:")
        for _c in sorted(_combo_multi, key=lambda c: min(_sev_order[x] for x in _combo_multi[c])):
            _nm = next(
                (
                    r["name"]
                    for _lv in ("严重", "已触发", "卡异动")
                    for r in results[_lv]
                    if r["code"] == _c
                ),
                _c,
            )
            _lv_str = " + ".join(sorted(set(_combo_multi[_c]), key=lambda x: _sev_order[x]))
            L(f"    • {_nm}({_c}): {_lv_str}")
    # 板块-异动交叉分析
    L(f"\n{'='*90}")
    L("## 【B. 涨停池扫描（打板情绪看板）】")
    L(f"{'---'}")
    from stock_common.stock_calendar import latest_market_data_date

    _pool_data_date = latest_market_data_date(datetime.now()).isoformat()
    L(f"  涨停池查询目标日：{_pool_data_date}")
    try:
        # MAK 保持关闭 Push2；这里只列 KPL 响应统计值作对照，不把 Day 标签当作实际数据日证明。
        _multi = {}
        try:
            from stock_common import get_limit_pool_multi_source

            _multi = get_limit_pool_multi_source(_pool_data_date, allow_push2ex=False)
            if _multi.get("sources"):
                _src_txt, _verified = _format_limit_pool_source_summary(
                    _multi.get("sources", {}),
                    _multi.get("total"),
                    _multi.get("unqueried_sources", ()),
                    cross_verified=_multi.get("cross_verified") is True,
                )
                _multi_total = _multi.get("total")
                if type(_multi_total) is int:
                    if _multi.get("cross_verified") is True:
                        _total_text = f"{_multi_total} 只（同日交叉确认）"
                    elif _multi.get("counts_agree") is True:
                        _total_text = f"{_multi_total} 只（两源数值相同，实际数据日未确认）"
                    else:
                        _observed_source = (
                            "KPL响应观测"
                            if type(_multi.get("sources", {}).get("kpl")) is int
                            else "东财按请求日期查询"
                        )
                        _total_text = f"{_multi_total} 只（{_observed_source}，实际数据日未确认）"
                else:
                    _total_text = "未知"
                _max_ladder = _multi.get("max_ladder")
                _max_ladder_text = (
                    f"KPL lbgd={_max_ladder}（响应 Day 标签匹配）"
                    if _max_ladder is not None
                    else "未知"
                )
                L(
                    f"  📊 涨停数来源对照: {_src_txt} → {_total_text}；"
                    f"{_verified} | 最高连板 {_max_ladder_text}"
                )
        except Exception as _e:
            _debug_log(f"mak multi_source error: {_e}")

        from stock_common import get_limit_pool_summary

        pool = get_limit_pool_summary(_pool_data_date, allow_push2ex=False)
        zt_count = pool.get("limit_up_count")
        zb_count = pool.get("limit_broken_count", 0)
        _multi_total = _multi.get("total")
        _mismatch_note = (
            _limit_pool_count_mismatch_note(
                _multi_total, zt_count, _multi.get("requested_data_date")
            )
            if pool.get("limit_up_count_available") is True
            else ""
        )
        if _mismatch_note:
            L(f"  {_mismatch_note}")
        # B 段只展示显式目标数据日、日期合格的来源计数；不以 A 段可能混合时点的样本数回填。
        _dt_available = pool.get("limit_down_count_available", False) is True
        dt_count = pool.get("limit_down_count")

        # V17.0.5 P1: fuyao 跌停池明细(first/last_limit_time——东财 getTopicDTPool 空缺的正式解法)
        try:
            from stock_common import get_fuyao_limit_pool as _f_lp, is_fuyao_enabled as _f_on

            if _f_on():
                import datetime as _dt_mod
                from stock_common.stock_calendar import get_last_trading_day

                _last_trade_day = get_last_trading_day()
                _d = (
                    _last_trade_day
                    if isinstance(_last_trade_day, _dt_mod.date)
                    else _last_trade_day.date()
                )
                _dms = int(_dt_mod.datetime.combine(_d, _dt_mod.time()).timestamp() * 1000)
                _dlp = await asyncio.to_thread(_f_lp, "down", 1, 100, _dms)
                _dl_items = (_dlp or {}).get("item") or []
                if _dl_items:
                    L("\n  跌停明细（fuyao 官方）:")
                    L("| 代码 | 名称 | 跌幅 | 首次跌停 | 最后跌停 | 换手 |")
                    L("|---|---|---|---|---|---|")
                    for _it in _dl_items[:20]:
                        L(
                            f"| {_it.get('ticker','')} | {_it.get('name','')}"
                            f"{_name_mark(_it.get('name',''))} | {_it.get('price_change_ratio_pct',0):.2f}%"
                            f" | {_it.get('first_limit_time','-')} | {_it.get('last_limit_time','-')}"
                            f" | {_it.get('turnover_ratio_pct',0):.2f}% |"
                        )
            else:
                L(
                    "  跌停明细：fuyao 数据未启用（无官方首次/最后跌停时刻与换手，仅保留涨停池口径跌停数）"
                )
        except Exception as _e:
            _debug_log(f"mak fuyao limit_down detail: {_e}")
        success_rate = pool.get("success_rate")
        _zt_available = pool.get("limit_up_count_available", False) is True
        _zb_available = pool.get("limit_broken_count_available", False) is True
        _zt_text = str(zt_count) if _zt_available else "未取得"
        _zb_text = str(zb_count) if _zb_available else "未取得"
        _dt_text = str(dt_count) if _dt_available and dt_count is not None else "未取得"
        _success_text = f"{success_rate:.0f}%" if success_rate is not None else "未取得"
        L(
            f"  涨停 {_zt_text} 只 | 炸板 {_zb_text} 只 | 跌停 {_dt_text} 只 | 封板率 {_success_text}（涨停池口径）"
        )
        L("  ℹ️ 同花顺涨停名单接口未返回独立实际数据日；名单及数量仅为目标日期请求的来源响应观察。")
        if not _zb_available or not _dt_available:
            L(
                "  ℹ️ 未取得的炸板/跌停数不按 0 计；各项只采用目标数据日符合来源日期规则的结果，口径可能不同。"
            )
        # V17.4.x (#444): 涨跌停数为涨停池口径；与其他来源并列观察，未逐只对齐前不称为一致确认。
        L(
            "  ℹ️ 本节涨跌停数、封板率和名单统一按涨停池口径；其他来源日期未在本报告中核实，且未逐股对账前仅作并列观察，不称为交叉确认。"
        )

        # 涨停板块分布
        sector_stats = pool.get("sector_stats", {})
        if sector_stats:
            _missing_sector_count = sector_stats.get("板块信息未提供", sector_stats.get("其他", 0))
            _known_sector_stats = [
                (sec, cnt)
                for sec, cnt in sector_stats.items()
                if sec not in ("板块信息未提供", "其他")
            ]
            L("\n  涨停板块分布（TOP10）:")
            for sec, cnt in _known_sector_stats[:10]:
                # V17.0.2l: 无冒号格式——原 "化工: 4 只" 被字段值块转表(表头强制加粗), 用户: 竖排
                # V17.2.27(2026-09-18) P2: 板块名统一走 normalize_industry, 与 C/D/E/F 段粒度一致
                L(f"    {normalize_industry(sec)}({cnt} 只)")
            if _missing_sector_count:
                L(f"    行业分类未取得: {_missing_sector_count} 只（不计入板块分布）")
            if not _known_sector_stats and not _missing_sector_count:
                L("    暂无可用的涨停行业分类")

        # 涨停明细(V17.0.2f: 直接 md 表格 7 列; V17.2.x: 按封板时间升序排序并渲染为表格,
        # 截断注移至表后——避免引用块插在分隔行与数据行之间破坏 md 表格结构, 与炸板明细一致)
        zt_list = pool.get("limit_up_list", [])
        if zt_list:

            def _seal_key(it):
                # 封板时间排序键: 兼容 ths "HH:MM:SS" 与 东财 push2ex "HHMM[SS]" 两种格式
                _raw = it.get("first_limit_time", "") or it.get("first_time", "")
                try:
                    if ":" in str(_raw):
                        _h, _m, _s = str(_raw).split(":")
                        return int(_h) * 3600 + int(_m) * 60 + int(_s)
                    _v = int(_raw) if _raw not in ("", None) else 0
                    if _v > 0:
                        return (_v // 10000) * 3600 + ((_v % 10000) // 100) * 60 + (_v % 100)
                except Exception:
                    pass
                return 10**9  # 缺封板时间者置末

            zt_list = sorted(zt_list, key=_seal_key)
            L("\n  涨停明细（按封板时间排序）:")
            L("| 代码 | 名称 | 涨跌幅 | 连板 | 封板时间 | 封单额(亿) | 板块 |")
            L("|---|---|---|---|---|---|---|")
            for item in zt_list[:30]:
                fund_yi = item.get("limit_fund", 0) / 1e8 if item.get("limit_fund", 0) else 0
                # H2(审查 2026-08-16): ths 优先源输出 first_time(已格式化 HH:MM:SS),
                # 东财 push2ex 输出 first_limit_time(5 位串 "92500")——双键兼容;
                # ths 路径直接显示格式化时间, 东财路径按 HHMM 拆
                fbt_raw = item.get("first_limit_time", "") or item.get("first_time", "")
                try:
                    _fbt_int = int(fbt_raw) if fbt_raw not in ("", None) else 0
                except (TypeError, ValueError):
                    _fbt_int = 0
                if ":" in str(fbt_raw):
                    fbt_fmt = str(fbt_raw)
                elif _fbt_int > 0:
                    fbt_h = _fbt_int // 10000
                    fbt_m = (_fbt_int % 10000) // 100
                    fbt_fmt = f"{fbt_h:02d}:{fbt_m:02d}"
                else:
                    fbt_fmt = str(fbt_raw)
                L(
                    f"| {item.get('code','')} | {item.get('name','')}{_name_mark(item.get('name',''))} | {item.get('change_pct',0):+.2f}% | {item.get('limit_count',0):.0f} | {fbt_fmt} | {fund_yi:+.2f} | {normalize_industry(item.get('sector') or '板块信息未提供')} |"
                )
            if len(zt_list) > 30:
                # V17.0.8: 明细截断注明(原 43 只只显 30 行, 读者误以为总数=表行数); 置于表后不破坏表格
                L(f"  > 共 {len(zt_list)} 只, 上表显示前 30 只（完整名单见涨停池源）")

        # 炸板明细(V17.0.2f: md 表格)
        zb_list = pool.get("limit_broken_list", [])
        if zb_list:
            L("\n  炸板明细:")
            L("| 代码 | 名称 | 涨幅 | 炸板次数 | 板块 |")
            L("|---|---|---|---|---|")
            for item in zb_list[:15]:
                L(
                    f"| {item.get('code','')} | {item.get('name','')}{_name_mark(item.get('name',''))} | {item.get('change_pct',0):+.2f}% | {item.get('broken_count',0):.0f} | {normalize_industry(item.get('sector') or '板块信息未提供')} |"
                )
    except Exception as _e:
        _debug_log(f"mak limit_pool: {_e}")
        L("  (打板数据获取失败)")

    # KPH（开盘红）涨停天梯，与 KPL（开盘啦）情绪统计保持独立来源。
    # V17.0.1f(2026-08-16): 移除盘口异动段——用户原则: 5 大脚本零东财 push2ex 接口
    try:
        from stock_common import get_kph_limit_ladder

        L(f"\n{'='*90}")
        L("## 【B+. 涨停天梯（开盘红）】")
        L(f"{'---'}")
        # V16.4.1: 提前初始化——import/接口失败时 _ladder 未定义, L1562 引用会 NameError 击穿
        _ladder = []
        _ladder = get_kph_limit_ladder()
        if _ladder:
            L(f"  涨停天梯共 {len(_ladder)} 只:")
            # V17.0.2f: md 表格
            L("| 代码 | 名称 | 连板 | 大单一字 | 人气 | 板块涨停 | 个股额(亿) |")
            L("|---|---|---|---|---|---|---|")
            for s in _ladder[:20]:
                _one = "✓" if s.get("one_word") else ""
                _pop = "🔥" if s.get("popular") else ""
                _amt = _safe_float(s.get("amount", 0)) / 1e8
                L(
                    f"| {str(s.get('code',''))} | {str(s.get('name',''))} | {s.get('limit_count',0)} | {_one} | {_pop} | {s.get('plate_limit_up_count',0)} | {_amt:.2f} |"
                )
            if len(_ladder) > 20:
                L(f"  （上表显示前 20 只，完整名单共 {len(_ladder)} 只）")
        else:
            L("  (涨停天梯数据获取失败)")

    except Exception as _e:
        _debug_log(f"mak ladder: {_e}")

    # V17.0.5 P1: fuyao 连板天梯互校(boards 六档矩阵+seal_nextday 次日封板率——独有字段)
    try:
        from stock_common import (
            get_fuyao_limit_up_ladder as _f_ladder,
            is_fuyao_enabled as _f_lad_on,
        )

        if _f_lad_on():
            _lad = await asyncio.to_thread(_f_ladder)
            _lad_items = (_lad or {}).get("item") or []
            if _lad_items and isinstance(_lad_items, list):
                _latest = _lad_items[0] if isinstance(_lad_items[0], dict) else {}
                _boards = _latest.get("boards") or {}
                _BOARD_CN = {
                    "two_board": "二",
                    "three_board": "三",
                    "four_board": "四",
                    "five_board": "五",
                    "six_board": "六",
                    "seven_over": "七",
                }
                _summary = []
                for _bk in (
                    "two_board",
                    "three_board",
                    "four_board",
                    "five_board",
                    "six_board",
                    "seven_over",
                ):
                    _lst = _boards.get(_bk) or []
                    if _lst:
                        _sealed_next = sum(1 for x in _lst if x.get("seal_nextday"))
                        _cn = _BOARD_CN.get(_bk, _bk.replace("_board", ""))
                        _summary.append(f"{_cn}板{len(_lst)}只(次日续封{_sealed_next})")
                if _summary:
                    L("\n  🪜 fuyao 连板矩阵互校（30 日窗口最新日）:")
                    L("    " + " | ".join(_summary))
        else:
            L("  ⚠️ fuyao 连板矩阵互校：竞价数据未启用（无连板六档矩阵 / 次日封板率互校）")
    except Exception as _e:
        _debug_log(f"mak fuyao ladder: {_e}")

    L(f"\n{'='*90}")
    # V16.4.0: 同花顺独家交叉验证（原 G 段移入——涨停明细末尾备注）
    try:
        _ths_pool = await get_ths_hot_pool(today_str)
    except Exception as _e:
        _debug_log(f"mak ths pool note: {_e}")
        _ths_pool = []
    if _ths_pool:
        _zt_all = {s.get("code", "") for s in _limit_up_samples}
        _ladder_all = (
            {str(s.get("code", "")) for s in (_ladder or [])}
            if isinstance(_ladder, list)
            else set()
        )
        _ths_only = [
            h
            for h in _ths_pool
            if h.get("code") not in _zt_all and h.get("code") not in _ladder_all
        ]
        L("")
        L(f"  ❗ 同花顺独家 {len(_ths_only)} 只（东财口径未覆盖，交叉验证增量；下表仅列前 10）:")
        if _ths_only:
            # V17.0.2i: 直接 md 表格 4 列(原空格表"涨幅% 题材"因 1 空格粘连合并列)
            L("| 代码 | 名称 | 涨幅% | 题材 |")
            L("|---|---|---|---|")
            for _h in _ths_only[:10]:
                L(
                    f"| {_h.get('code','')} | {_h.get('name','')}{_name_mark(_h.get('name',''))} | {_safe_float(_h.get('zhangfu',0)):+.2f}% | {str(_h.get('reason',''))[:40]} |"
                )
    else:
        L("")
        L(
            "  ⚠️ 同花顺独家交叉验证：数据源受限（同花顺网页接口 401 反爬），强势股热池暂无法获取，交叉验证增量视角缺失。"
        )

    # 通达信 ELTDX 连板天梯与 KPH（开盘红）分源展示，不合并成一个来源结论。
    if _eltdx_ladder:
        L("## 【B++. 连板天梯（通达信 eltdx 实时核验）】")
        L(
            "  （数据来源: 通达信 eltdx（TDX 公网主站 7709/7615 实时）；与 B+ KPH（开盘红）连板天梯分源展示）"
        )
        _ladder_sorted = sorted(
            [r for r in _eltdx_ladder if isinstance(r, dict) and (r.get("ladder_level") or 0) >= 2],
            key=lambda x: (x.get("ladder_level") or 0),
            reverse=True,
        )
        if _ladder_sorted:
            L("| 代码 | 名称 | 连板 | 连续涨停日 | 封流比% | 板块 |")
            L("| --- | --- | --- | --- | --- | --- |")
            for _r in _ladder_sorted[:30]:
                _ec = _r.get("code") or _r.get("full_code") or ""
                _plain = _ec[2:] if _ec.startswith(("sh", "sz", "bj")) else _ec
                _nm = _r.get("name") or _r.get("stock_name") or _plain
                _ll = _r.get("ladder_level") or 0
                _streak = _r.get("limit_up_streak_days") or 0
                _seal = _r.get("seal_to_float_ratio") or 0.0
                _ind = normalize_industry(_r.get("industry") or _r.get("sector") or "")
                L(f"| {_plain} | {_nm} | {_ll}连板 | {_streak} | {_seal:.2f} | {_ind} |")
        else:
            L(f"  eltdx 返回 {len(_eltdx_ladder)} 条记录，但其中没有可展示的 ≥2 板天梯记录。")
        L("")
    else:
        # 适配器将空响应、异常和超时统一降级为空列表，故报告不能仅凭空结果断言源不可用。
        L("## 【B++. 连板天梯（通达信 eltdx 实时核验）】")
        L(
            "  ⚠️ 本次未取得可用天梯记录；适配器会将空响应、异常或超时统一降级为空列表，"
            "因此无法据此区分数据源故障与当日无符合记录。"
        )
        L("     该维度无等价后备通道，本节暂缺；不能据此判断市场没有连板股。")
        L("")

    L("## 【C. 板块-异动集中度分析】")
    L(f"{'---'}")
    sectors = get_all_sectors()
    scored = compute_rotation_scores(sectors)
    sorted_sectors = sorted(sectors, key=lambda x: x.get("score", 0), reverse=True)
    _abnormal_codes = set(r["code"] for r in results["已触发"] + results["严重"])
    _sector_density = []
    for _s in sorted_sectors:
        _sc = _s.get("_member_codes", [])
        _cnt = sum(1 for c in _sc if c in _abnormal_codes)
        _total = _s.get("_member_count", len(_sc)) or 1
        if _cnt > 0:
            _density = _cnt / _total * 100
            _sector_density.append((_s["name"], _cnt, _density))
    _sector_density.sort(key=lambda x: x[1], reverse=True)
    # 龙虎榜数据补全（近5日常规异动）
    _dt_map = get_recent_dragon_tiger(3)
    if _dt_map:
        _extra_dt_codes = set(_dt_map.keys()) - _abnormal_codes
    else:
        _extra_dt_codes = set()
    # V17.2.9: 修复 C 段空表 bug——原 `if _sector_density or _dt_map` 在仅有龙虎榜数据
    # (_dt_map 非空) 而无板块集聚(_sector_density 空) 时误触发标题, 但循环只遍历空列表
    # 导致标题下无内容, 且龙虎榜补全(_extra_dt_codes)从未渲染。拆为两段独立输出。
    if _sector_density:
        L("  异动集聚板块TOP5（异动股数/密度）:")
        for _nm, _cnt, _den in _sector_density[:5]:
            L(f"    {normalize_industry(_nm)}: {_cnt}只异动（板块内密度{_den:.1f}%）")
            _s = next((s for s in sorted_sectors if s["name"] == _nm), None)
            if _s:
                _stocks = get_sector_stocks(_s["code"])
                _sc = [st["code"] for st in _stocks]
                for _abn in results["已触发"] + results["严重"]:
                    if _abn["code"] in _sc:
                        L(f"      {_abn['code']} {_abn['name']} - {_abn.get('desc','')}")
    else:
        L("  今日异动股较少，未形成明显板块集聚")
    # 龙虎榜异动补全（独立于板块集聚，避免仅龙虎榜数据时标题空表）
    if _dt_map:
        L("  龙虎榜异动补全（近3日，非已触发异常股）:")
        for _c in list(_extra_dt_codes)[:5]:
            _dt = _dt_map.get(_c)
            if not _dt:
                continue
            _dtn = _dt.get("name", "")
            _dt_display = f"{_c} {_dtn}" if _dtn else _c
            L(
                f"    {_dt_display} - {str(_dt.get('reason', ''))[:40]} | 净买{float(_dt.get('net_buy', 0)):.0f}万"
            )
    # Historical high-return review uses only dated trading-bar fields.
    _recent_high = []
    for stock in all_stocks:
        _values = {}
        _dates = {}
        for _field in ("ret_3d", "ret_10d", "ret_20d"):
            _meta = (stock.get("_field_meta") or {}).get(_field) or {}
            _metric_date = _normalize_mak_date(_meta.get("as_of_date"))
            _value, _ = _metric_for_date(stock, _field, _metric_date, require_close_quote=True)
            _values[_field] = _value
            _dates[_field] = _metric_date if _value is not None else ""
        _threshold = limit_pct_for(stock.get("code", ""), stock.get("name", ""))
        _matched = (
            (_values["ret_10d"] is not None and abs(_values["ret_10d"]) >= 80)
            or (_values["ret_20d"] is not None and abs(_values["ret_20d"]) >= 150)
            or (_values["ret_3d"] is not None and abs(_values["ret_3d"]) >= _threshold)
        )
        if _matched:
            _recent_high.append(
                {
                    "code": stock["code"],
                    "name": stock["name"],
                    "ret_3d": _values["ret_3d"],
                    "ret_10d": _values["ret_10d"],
                    "ret_20d": _values["ret_20d"],
                    "dates": _dates,
                }
            )
    # 龙虎榜补全回溯名单；TDX 日 K 每个窗口必须有完整且同日结束的交易日条。
    if _dt_map:
        _recent_codes = {row["code"] for row in _recent_high}
        for code, dt_row in _dt_map.items():
            if code in _recent_codes:
                continue
            stock = next((item for item in all_stocks if item["code"] == code), None)
            if stock:
                _values = {}
                _dates = {}
                for _field in ("ret_3d", "ret_10d", "ret_20d"):
                    _meta = (stock.get("_field_meta") or {}).get(_field) or {}
                    _metric_date = _normalize_mak_date(_meta.get("as_of_date"))
                    _values[_field], _ = _metric_for_date(
                        stock,
                        _field,
                        _metric_date,
                        require_close_quote=True,
                    )
                    _dates[_field] = _metric_date if _values[_field] is not None else ""
                if any(value is not None for value in _values.values()):
                    _recent_high.append(
                        {
                            "code": code,
                            "name": stock["name"],
                            **_values,
                            "dates": _dates,
                        }
                    )
                continue
            try:
                dated_bars = await asyncio.to_thread(_dated_stock_bars, code)
            except Exception as error:
                _debug_log(f"mak recent_high_kline error {code}: {error}")
                dated_bars = []
            values = {
                f"ret_{period}d": _index_return_for_date(dated_bars, _target_data_date, period)
                for period in (3, 10, 20)
            }
            dates = {
                field: _target_data_date if value is not None else ""
                for field, value in values.items()
            }
            if any(value is not None for value in values.values()):
                _recent_high.append(
                    {
                        "code": code,
                        "name": dt_row.get("name", ""),
                        "ret_3d": values["ret_3d"],
                        "ret_10d": values["ret_10d"],
                        "ret_20d": values["ret_20d"],
                        "dates": dates,
                    }
                )
    _recent_high.sort(key=lambda row: abs(row["ret_10d"] or 0), reverse=True)
    if _recent_high:
        _recent_top = _recent_high[:50]
        _recent_ann = {}
        _ann_t0 = time.time()
        for _r in _recent_top[:15]:
            try:
                _a, _s = get_abnormal_announcements(_r["code"])
                if _a > 0:
                    _recent_ann[_r["code"]] = (_a, _s)
            except Exception as _e:
                _debug_log(f"mak abnormal_announcements error: {_e}")
        _ann_dt = time.time() - _ann_t0
        print(f"  公告查询耗时: {_ann_dt:.2f}s", flush=True)
        L(f"\n{'='*90}")
        L("## 【个股异动回溯（仅列有日期化指标的样本）】")
        L(f"{'---'}")
        L(
            "| 代码 | 名称 | 3交易日涨幅 | 10交易日涨幅 | 20交易日涨幅 | 指标数据日(3/10/20) | 公告 |"
        )
        L("|---|---|---|---|---|---|---|")
        _shown = 0
        for _r in _recent_top[:30]:
            _a_info = ""
            if _r["code"] in _recent_ann:
                _a_cnt, _s_cnt = _recent_ann[_r["code"]]
                _a_info = f"已发{_a_cnt}份(严重{_s_cnt}份)" if _s_cnt > 0 else f"已发{_a_cnt}份"
            else:
                continue
            _fmt_metric = lambda value: f"{value:+.2f}%" if value is not None else "未评估"
            _date_label = ", ".join(
                f"{period}日={_r['dates'].get(field) or '未确认'}"
                for period, field in ((3, "ret_3d"), (10, "ret_10d"), (20, "ret_20d"))
            )
            L(
                f"| {_r['code']} | {_r['name']} | {_fmt_metric(_r['ret_3d'])} | "
                f"{_fmt_metric(_r['ret_10d'])} | {_fmt_metric(_r['ret_20d'])} | {_date_label} | {_a_info} |"
            )
            _shown += 1
        if _shown == 0:
            L("  (无可报告的日期化异动回溯公告样本；不据此断言没有公告)")
        L("\n  > 💡 指标窗口按各自数据日计算，公告为近7日检索结果；本节不是精确的历史触发回放。")

    L(f"\n{'='*90}")
    L("## 【D. 行业轮动强度扫描】")
    L(
        "  💡 口径: ZHB 快照聚合申万二级行业, 成交额/主力净流为板块成分股 T 日聚合"
        "(板块成员数以实际快照覆盖为准); 与 E 段 TOP10 深度分析口径一致。"
    )
    L(f"{'---'}")
    top10 = sorted_sectors[:10]
    L(f"  行业总数: {len(sectors)}个")
    # V17.0.2f: md 表格(用户: 该表应完整分列)
    L("| 排名 | 板块名称 | 评分 | 涨跌幅 | 成交额(亿) | 主力净流(亿) |")
    L("|---|---|---|---|---|---|")
    for i, ts in enumerate(top10, 1):
        name = normalize_industry(ts["name"])
        _mfi = round(ts.get("main_inflow", 0) / 1e8, 2) if abs(ts.get("main_inflow", 0)) > 0 else 0
        L(
            f"| {i} | {name} | {ts.get('score',0):.1f} | {ts['change_pct']:+.2f}% | {ts.get('amount_yi',0):.1f} | {_mfi:+.2f} |"
        )
    if top10:
        L(
            f"\n  🏆 轮动冠军: {normalize_industry(top10[0]['name'])} 评分 {top10[0].get('score',0):.1f}"
        )
        # V16.3 O37: 板块轮动矩阵对照（duanxianxia——ths 涨幅/kaipan 强度双口径，字典 §12.18）
        try:
            from stock_common import get_plate_rotation_top

            _pr_top = get_plate_rotation_top("kaipan", 20, 5)
            if _pr_top:
                L("\n  🧭 外部轮动对照（短线侠板块轮动接口，kaipan 请求口径；指标值 top5）:")
                L("| 排名 | 数据日期 | 板块代码 | 板块名称 | 指标值 | 方向 |")
                L("|---|---|---|---|---:|---|")
                for _p in _pr_top:
                    L(
                        f"| {_p['rank']} | {_p.get('date') or '未确认'} | {_p['code']} | "
                        f"{_p['name']} | {_p['value']} | "
                        f"{'↑' if _p['color']=='red' else '↓'} |"
                    )
        except Exception as _e:
            _debug_log(f"mak plate rotation cross-check: {_e}")
    else:
        L("\n  ⚠️ 无法获取行业板块数据")
    L(f"\n{'='*90}")
    L("## 【E. TOP10 板块深度分析（涨停梯队 + 龙头股）】")
    L(f"{'---'}")
    top_analysis = analyze_top_stocks(top10)
    for ta in top_analysis:
        nm = normalize_industry(ta["sector"])
        _code = ta["data"].get("code", "")
        # V16.3 L: ZHB 旁路板块 code=行业名（非 BK 码）→ 避免 "煤炭开采 (煤炭开采)" 重复
        _code_show = f" ({_code})" if _code and _code != ta["sector"] else ""
        L(f"\n  🔥 {nm}{_code_show} 总分={ta['data'].get('score',0):.1f}")

        L(f"     ├─ 成分股总数: {ta.get('total_stocks',0)} 只")
        if ta["limit_up_count"] > 0:
            # V17.0.8: 涨停名单用真实涨停全量(limit_up_all)而非梯队(_leaders 含替补)
            _zt_names = " ".join(st["name"] + st["code"] for st in ta.get("limit_up_all", []))
            L(f"     ├─ 涨停家数: {ta['limit_up_count']} 只 → {_zt_names}")
        else:
            L("     ├─ 涨停家数: 0 只")
        _top5 = ta.get("top5_stocks", [])
        if _top5:
            L("     └─ 涨幅 TOP5:")
            for _t5 in _top5:
                _t5_chg = _t5.get("change_pct", 0)
                _t5_icon = "🚀" if _t5_chg >= 10 else ("📈" if _t5_chg >= 5 else "  ")
                L(f"       {_t5_icon} {_t5['name']}({_t5['code']})  {_t5_chg:>+8.2f}%")
                # [ENRICH] 数据维度充实（仅用 ZHB 快照已有字段，零新增取数；异常不阻断报告）
                try:
                    from stock_common.enrich_helpers import mak_stock_lines

                    for _ln in mak_stock_lines(_t5):
                        L("       " + _ln)
                except Exception as _e:
                    _debug_log(f"mak enrich top5 error: {_e}")
        _items = []
        for _st in ta["limit_up_stocks"]:
            # V16.0: 统一 is_limit_up 判断（ST 10% 与主板一致）
            _label = (
                "涨停"
                if is_limit_up(_st["code"], _st.get("name", ""), _st.get("change_pct", 0))
                else f"{_st.get('change_pct',0):+.1f}%"
            )
            _items.append(f"{_st['name']}({_st['code']}, {_label})")
        # V17.0.2i: 无龙头时不输出空"龙头:"行
        if _items:
            L(f"    龙头: {' | '.join(_items)}")
    L(f"\n{'='*90}")
    L("## 【F. 行业资金流样本核验】")
    L(f"{'---'}")
    if _MAIN_NET_MAP_GLOBAL:
        L(
            f"  ulist f62 返回 {_MAIN_NET_RETURNED_COUNT}/{_MAIN_NET_REQUESTED_COUNT} 条扫描样本；"
            "行业汇总只累计已返回字段，缺项不代表净流为零或净流出。"
        )
        if _MAIN_NET_DATA_DATE_NOTE:
            L(f"  Ulist 行日期核验：{_MAIN_NET_DATA_DATE_NOTE}")
    else:
        L("  ulist f62 无可用样本；本节不判定行业主力资金方向。")
        if _MAIN_NET_DATA_DATE_NOTE:
            L(f"  Ulist 行日期核验：{_MAIN_NET_DATA_DATE_NOTE}")
        if _MAIN_NET_SOURCE_STATUS == "shared_cooldown":
            L("  来源状态：push2delay 共享风控冷却中，本轮跳过请求；缺项不作零净流处理。")
        elif _MAIN_NET_SOURCE_STATUS == "error":
            L("  来源状态：批量 f62 请求异常；缺项不作零净流处理。")
    # V16.4.0: 按评分筛选（原 sectors[:50] 前 50 高评分板块可能全为净流入 → 虚涨段恒空）
    _scored = [s for s in sectors if s.get("score", 0) >= 30] or sectors
    # 全部行业均无非零合计时，只报告无法判断，不把空值当作真实零流量。
    _has_flow = any((s.get("main_inflow", 0) or 0) != 0 for s in _scored)
    if not _has_flow:
        L("  ⚠️ 未形成非零行业净额汇总；真实零值与来源缺项无法仅凭此处区分，不作方向判断。")
    else:
        with_money = [s for s in _scored if s.get("main_inflow", 0) > 0]
        without_money = [s for s in _scored if s.get("main_inflow", 0) < 0]
        if with_money:
            # V17.0.2f: md 表格
            L("  主力净流入样本:")
            L("| 板块 | 评分 | 涨跌幅 | 主力净流入(亿) |")
            L("|---|---|---|---|")
            _sorted_in = sorted(with_money, key=lambda x: x.get("main_inflow", 0), reverse=True)
            for s in _sorted_in[:10]:
                L(
                    f"| {normalize_industry(s['name'])} | {s.get('score',0):.1f} | {s['change_pct']:+.2f}% | {round(s['main_inflow']/1e8,2):+.2f} |"
                )
        if without_money:
            # V17.0.2f: md 表格
            L("  ⚠️ 涨幅与已观测主力净流出同时出现（样本提示）:")
            L("| 板块 | 评分 | 涨跌幅 | 主力净流出(亿) |")
            L("|---|---|---|---|")
            _sorted_out = sorted(without_money, key=lambda x: x.get("main_inflow", 0))
            for s in _sorted_out[:10]:
                L(
                    f"| {normalize_industry(s['name'])} | {s.get('score',0):.1f} | {s['change_pct']:+.2f}% | {round(abs(s['main_inflow'])/1e8,2):.2f} |"
                )
        else:
            # 批量主力净额缺失时，虚涨段无法判断，避免用恒正的 ZHB 竞价额伪造净流出结论。
            L("  ℹ️ 本次筛选未发现主力净流出板块。")
    _lurking = [
        s for s in sectors if s.get("main_inflow", 0) > 3e8 and 1 <= s.get("change_pct", 0) <= 5
    ]
    _lurking.sort(key=lambda x: x.get("main_inflow", 0), reverse=True)
    if _lurking:
        # V17.0.2f: md 表格
        L("\n  🕵️ 主力净流入且涨幅不高的板块样本（供观察，不据此判断建仓）:")
        L("| 板块 | 涨跌幅 | 主力净流入(亿) |")
        L("|---|---|---|")
        for _l in _lurking[:5]:
            _lnm = normalize_industry(_l["name"])
            _lfi = round(_l["main_inflow"] / 1e8, 2)
            L(f"| {_lnm} | {_l['change_pct']:+.2f}% | {_lfi:+.2f} |")
    L(f"\n{'='*90}")
    # V17.0(2026-08-15 C 方案): 全量 md 化——渲染层确定性转换(标题/分隔线/F10 边框表/对齐空格表→md)
    # V17.4.1 吸收层市场级信号附录: 申购日历(抽水压力)/ETF份额/新浪研报/央视新闻联播/上证e互动/ST名单
    try:
        from stock_common.sc_market_signals import render_market_signals_section

        for _ms in render_market_signals_section(today_str):
            L(_ms)
    except Exception as _e:
        L(f"  ⚠️ 市场信号附录渲染未完成（{type(_e).__name__}）。")
    from stock_common.md_render import render_md_report

    output = render_md_report(output_path, lines)
    return output


class MakReportRunner(BaseReportRunner):
    """A股异动及行业轮动扫描报告 Runner"""

    def __init__(self):
        super().__init__("get_mak_report", "mak", "A股异动及行业轮动扫描报告")

    def execute_pipeline(self) -> str:
        sn = os.path.basename(__file__).replace(".py", "")
        ts = self.report_ts  # V17.0 R1: 基类统一口径(%Y%m%d_%H%M)
        args = self.args
        if args is None:
            raise RuntimeError("report arguments have not been initialized")
        op = os.path.join(args.output, f"{sn}_{ts}.md")
        try:
            print("  ⏱ 预计 2-3 分钟", flush=True)
        except UnicodeEncodeError:
            print("  [INFO] 预计 2-3 分钟", flush=True)

        try:
            asyncio.run(generate_sector_report(op))
            print(f"  ✅ 已保存: {op}", flush=True)
        except Exception as e:
            print(f"❌ 报告生成失败: {e}", flush=True)
            raise e
        return op

    def upload_reports(self, drive: Any, folder_id: str, output_file: str) -> None:
        self.upload_single_report(drive, folder_id, output_file)


if __name__ == "__main__":
    runner = MakReportRunner()
    runner.run()

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

import time, os, warnings, asyncio  # V16.4.1: 删 argparse
from typing import Any, Dict, List
from datetime import date, datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed  # V16.4.1: 删 Counter

# H1/H2 修复(2026-08-15 二审): 全市场 ulist 主力净额(元, 带符号)模块级共享——_get_zhb_market_data 填充, 板块聚合/A 段读取
_MAIN_NET_MAP_GLOBAL: Dict[str, float] = {}

warnings.filterwarnings('ignore')
from core.data_provider import get_market_snapshot_async

from core.tdx_client import (  # V16.4.1: 删 tdx_get_security_bars/cleanup_tdx
    tdx_get_index_bars,
    tdx_get_board_list,
    tdx_get_board_members,
    tdx_get_market_abnormal_data,
)
from stock_common import (
    _safe_float,
    _quick_request,
    _debug_log,  # V17.0 审查: 删 UA 死导入(getharden 委托 sc_datasource 后无引用)
    _load_strategy_config,
    get_recent_dragon_tiger,
    baidu_kline_full,
    BaseReportRunner,  # V16.4.1: 删 _request_with_retry/common_parse_args
    is_trading_day,
    get_market_status,
    get_zhb_full_market_snapshot,
    is_zhb_data_fresh,
    zhb_field_safe,
    get_zhb_data_date,
    get_zhb_industry_map,
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


def _is_a_stock(code: str) -> bool:
    """V17.0 S3: 统一走 sc_utils.is_a_stock（原本地 _A_STOCK_PREFIXES 定义已收敛）。"""
    from stock_common.sc_utils import is_a_stock as _u_is_a_stock

    return _u_is_a_stock(code)


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
    "sh000688": "科创综指",
}


def get_stock_index(code):
    if code.startswith("688"):
        return "sh000688"
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


async def get_market_abnormal_data():
    """V7: 全市场 + 多周期涨幅 → TDX MAC 协议（push2 fallback 已删除）
    V10.1: 优先使用zhb全市场快照，零网络请求，失败时回退到TDX
    V10.2: zhb优先级分级——mak脚本依赖change_pct判断涨停/跌停，属于实时字段，
           zhb日期非今日时必须fallback到TDX获取当日实时涨跌幅
    V11.5: 使用data_provider异步接口
    V15.1: 与其他 5 大报告脚本统一接入 get_canonical_stock_data，但 mak 是全市场异动扫描场景
          （3000+ 股票），保留批量入口 get_market_snapshot_async 而非逐只调用，避免性能回退。
          对应的 dataclass 形式由 _canonicalize_snapshot 转换层提供（V15.1）。
    """
    # V10.2: change_pct是实时字段，zhb日期必须是今天才能用
    if zhb_field_safe("change_pct"):
        data = await _get_zhb_market_data()
        if not data:
            data = await asyncio.to_thread(tdx_get_market_abnormal_data)
    else:
        data = await asyncio.to_thread(tdx_get_market_abnormal_data)
    # V15.5.16: 统一腾讯实时覆盖（无论 ZHB/TDX 分支）— 今日盘中涨停判断
    if data:
        try:
            from core.tdx_client import _tencent_batch_fallback

            _tm = _tencent_batch_fallback([s.get("code", "") for s in data]) or {}
            _cov = 0
            for s in data:
                _tq = _tm.get(s.get("code", ""), {})
                if _tq.get("price"):
                    s["price"] = _safe_float(_tq["price"])
                if _tq.get("change_pct") is not None:
                    s["change_pct"] = _safe_float(_tq["change_pct"])
                    _cov += 1
                # V16.2.14: 补股票名称（ZHB 快照缺失时，如退市整理/新上市股——
                # 原缺失导致报告多处"只有代码无名称"）
                if _tq.get("name") and not s.get("name"):
                    s["name"] = _tq["name"]
            _debug_log(f"mak tencent realtime cover: {_cov}/{len(data)} 只")
        except Exception as _e:
            _debug_log(f"mak tencent cover error: {_e}")
    return data


async def _get_zhb_market_data():
    """V10.1: 从zhb全市场快照构建异动扫描数据。

    返回格式与tdx_get_market_abnormal_data一致，便于无缝替换。
    V11.5: 使用data_provider的get_market_snapshot_async统一获取数据
    """
    try:
        snapshot = await get_market_snapshot_async()
        if not snapshot:
            return []

        all_codes = list(snapshot.keys())
        # V15.3 P0 修复: 原代码重复调用 get_market_snapshot_async(all_codes)，
        # 第一次已经返回完整 dict，第二次只是浪费一次 ZHB 解析/网络 IO。
        # 直接复用 snapshot 作为 price_map。
        price_map = snapshot
        industry_map = get_zhb_industry_map()

        result = []
        # V15.5.15: 腾讯批量实时行情（今日 change_pct/price，盘中涨停判断）
        # ZHB T-1 change_pct 不反映今日盘中涨停 → A 段涨停数失真
        _tencent_map: Dict[str, Dict[str, Any]] = {}
        try:
            from core.tdx_client import _tencent_batch_fallback

            _tencent_map = _tencent_batch_fallback(all_codes) or {}
        except Exception as _e:
            _debug_log(f"mak tencent batch: {_e}")
        # V17.0(2026-08-15): 主力净流入批量方案——ulist.np/get 批量 f62+f66(=push2 f137+f140 特大+大单净,
        # 20/20 对齐实锤)。此前 main_net_amount=ZHB main_net_buy_amount(实为竞价额, 名实不符)。
        # fallback 链: ulist 批量(主) → ZHB 竞价额(兜底, 语义标注)
        _main_net_map: Dict[str, float] = {}
        try:
            from stock_common.sc_datasource import get_em_batch_quotes

            # ⚠️ H2 修复(2026-08-15 审查): 同步网络批量(17 chunk ~20-30s)在 async 上下文阻塞事件循环 → to_thread
            _bq = await asyncio.to_thread(get_em_batch_quotes, all_codes) or {}
            _main_net_map = {
                code: (q.get("main_net_inflow_wan", 0.0) or 0.0) * 1e4  # 万元 → 元(下游 /1e8 元口径)
                for code, q in _bq.items()
            }
            global _MAIN_NET_MAP_GLOBAL
            _MAIN_NET_MAP_GLOBAL = dict(_main_net_map)  # H1: 板块聚合/A 段共享(元, 带符号)
        except Exception as _e:
            _debug_log(f"mak ulist main_net batch: {_e}")
        # V14.2.1: 提前一次性获取 ZHB profile 离线简称（修复 mak 0只 Bug）
        from core.zhb_client import get_stock_name_from_zhb

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
            if 'ST' in name or '退' in name:
                continue

            # V15.5.15: 腾讯实时优先（今日 change_pct/price），缺失回退 ZHB T-1
            _tq = _tencent_map.get(code, {})
            price = _safe_float(_tq.get("price") or price_map.get(code, {}).get("price", 0))
            # V16.3 O21: 平盘（change_pct=0）也是今日事实——is not None 判定，0 不回退 ZHB T-1
            _tq_cp = _tq.get("change_pct")
            change_pct = _safe_float(_tq_cp if _tq_cp is not None else stat.get("change_pct", 0))
            # V16.3 O21: amount 优先腾讯 T 日（原 stat.amount=T-1——盘中"今日成交额"实为昨日）
            amount_wan = _safe_float(
                _tq.get("amount_wan")
                if _tq.get("amount_wan") is not None
                else stat.get("amount", 0)
            )
            # V16.3 O21: turnover 优先腾讯 T 日（原 price_map=ZHB T-1）
            _tq_to = _tq.get("turnover_pct")
            turnover = _safe_float(
                _tq_to if _tq_to is not None else price_map.get(code, {}).get("turnover_pct", 0)
            )

            # 2026-08-11: 修复恒 0——腾讯批量直给 mcap_yi，缺失才走 股本×price 计算
            mcap_yi = _safe_float(_tq.get("mcap_yi") or 0) or _calc_mcap_yi(code, price)

            ret_5d = _safe_float(stat.get("change_5d", 0))
            ret_10d = _safe_float(stat.get("change_10d", 0))
            ret_20d = _safe_float(stat.get("change_20d", 0))
            ret_60d = _safe_float(stat.get("change_60d", 0))

            # V16.3 O21: ret_3d 的 r0 用腾讯 T 日（原 stat.change_pct=T-1——盘中 3 日偏离失真）
            ret_3d = _calc_3d_from_daily(stat, today_change_pct=change_pct if _tq_cp is not None else None)

            result.append(
                {
                    "code": code,
                    "name": name,
                    "price": price,
                    "change_pct": change_pct,
                    "turnover": turnover,
                    "mcap_yi": mcap_yi,
                    "amount_yi": amount_wan / 10000.0 if amount_wan > 0 else 0,
                    "ret_3d": ret_3d,
                    "ret_5d": ret_5d,
                    "ret_10d": ret_10d,
                    "ret_20d": ret_20d,
                    "ret_60d": ret_60d,
                    # V16.4.1: 新股标记字段——change_pct_1d/2d 为空 = 上市不足 3 个交易日
                    # (创业板/科创板新股前 5 日无涨跌幅限制, 首日 +662% 等极端值会让偏离判定失真)
                    "change_pct_1d": stat.get("change_pct_1d", ""),
                    "change_pct_2d": stat.get("change_pct_2d", ""),
                    # V17.0(2026-08-15): 主力净额=ulist 批量 f62+f66(元口径, H1/M5 修复: 统一元+0值不误回退)
                    "main_net_amount": (
                        _main_net_map[code] if code in _main_net_map
                        else (_safe_float(stat.get("main_net_buy_amount", 0)) or 0) * 1e4
                    ),
                    # V16.2.16: Col[13] 大量为风格/概念（微盘股/近已解禁等）→ 只保留行业段
                    #（8803xx/8804xx 通达信行业、881xxx 申万版），其余置空避免伪行业聚合
                    "industry_code": (
                        stat.get("industry_code", "")
                        if _is_industry_code(stat.get("industry_code", ""))
                        else ""
                    ),
                }
            )

        return result
    except Exception as _e:
        _debug_log(f"mak zhb_market_data: {_e}")
        return []


def _calc_3d_from_daily(stat, today_change_pct=None):
    """V10.1: 从T/T-1/T-2日涨跌幅推算3日累计涨跌幅。

    使用复利计算：(1+r1)*(1+r2)*(1+r3) - 1
    V16.0: 三值全 0（数据缺失）时返回 0，不再用 change_5d*0.6 捏造 fudge 值，
    避免把捏造数据当作真实 3 日涨跌幅进入异动判定。
    V16.3 O21: today_change_pct 参数——盘中腾讯 T 日涨跌幅优先（原 stat.change_pct 为 T-1）。
    """
    _r0_raw = today_change_pct if today_change_pct is not None else stat.get("change_pct", 0)
    r0 = _safe_float(_r0_raw) / 100.0
    r1 = _safe_float(stat.get("change_pct_1d", 0)) / 100.0
    r2 = _safe_float(stat.get("change_pct_2d", 0)) / 100.0

    if r0 == 0 and r1 == 0 and r2 == 0:
        return 0.0

    ret_3d = ((1 + r0) * (1 + r1) * (1 + r2) - 1) * 100.0
    return round(ret_3d, 2)


def get_baidu_kline(code, days=20):
    """V4: K线数据 → tdx_client 适配器（TDX日K线，自动fallback百度）"""
    keys, rows = baidu_kline_full(code, count=days + 10)
    if not keys or not rows:
        return [], []
    idx_map = {k: i for i, k in enumerate(keys)}
    ci = idx_map.get('close', -1)
    vi = idx_map.get('volume', -1)
    if ci < 0:
        return [], []
    closes = [_safe_float(r[ci]) for r in rows[-days:] if len(r) > ci]
    vols = [_safe_float(r[vi]) for r in rows[-days:] if len(r) > vi and vi >= 0] if vi >= 0 else []
    return closes, vols


def get_index_returns():
    def _calc(closes, days):
        if len(closes) < days + 1:
            return None
        return (
            (closes[-1] - closes[-(days + 1)]) / closes[-(days + 1)] * 100
            if closes[-(days + 1)] > 0
            else None
        )

    def _get_kline(ic):
        """V7: 指数K线 → TDX → 百度PAE → 腾讯（兜底）"""
        try:
            keys, rows = tdx_get_index_bars(ic, count=250)
            if keys and rows:
                ci = next((i for i, k in enumerate(keys) if k in ("close", "close_price")), -1)
                if ci >= 0:
                    closes = [_safe_float(r[ci]) for r in rows if len(r) > ci]
                    if closes:
                        return closes
        except Exception as _e:
            _debug_log(f"mak index_kline tdx error {ic}: {_e}")
        # 腾讯日K序列兜底（V16.3 O19: 原实时 2 值 → ret_3d/10d/20d/60d 静默 None——
        # 改用 ifzq.gtimg.cn 前复权日K，完整序列）
        try:
            r = _quick_request(
                f"https://ifzq.gtimg.cn/appstock/app/fqkline/get?param={ic},day,,,250,qfq",
                timeout=10,
            )
            if r:
                d = (r.json().get("data") or {}).get(ic, {})
                kline = d.get("qfqday") or d.get("day") or []
                closes = [_safe_float(row[2]) for row in kline if len(row) > 2 and row[2]]
                if closes:
                    return closes
        except Exception as _e:
            _debug_log(f"mak index_kline tencent kline error {ic}: {_e}")
        # 最后兜底：实时 2 值（仅 1 日回报——指标静默 None 有提示）
        try:
            r = _quick_request(f"https://qt.gtimg.cn/q={ic}", timeout=10)
            if r:
                r.encoding = "gbk"
                v = r.text.split('"')[1].split("~")
                close = _safe_float(v[3])
                pre_close = _safe_float(v[4])
                return [pre_close, close] if close > 0 else []
        except Exception as _e:
            _debug_log(f"mak index_kline error: {_e}")
            return []

    result = {}
    closes_pool = {}
    for ic in INDEX_MAP:
        closes = _get_kline(ic)
        closes_pool[ic] = closes
        result[ic] = {
            "ret_3d": _calc(closes, 3),
            "ret_10d": _calc(closes, 10),
            "ret_20d": _calc(closes, 20),
            "ret_60d": _calc(closes, 60),
        }
    return result, closes_pool


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


def count_history_deviations(code, index_code, index_closes_pool, days_lookback=10):
    """V16.1: 修复负索引错位（原 abs() 转正索引取错位置）。

    原实现: si = -(i+4) → abs(si) 后按正索引访问，语义错误（正索引从头部数）。
    修正: 直接用负索引（Python 语义，从尾部数），窗口为 [-(i+4)-2, -(i+4)] 共 3 根。
    """
    closes, _ = get_baidu_kline(code, days_lookback + 5)
    if len(closes) < days_lookback + 3:
        return 0, None
    idx_closes = index_closes_pool.get(index_code, [])
    if len(idx_closes) < days_lookback + 3:
        return 0, None
    count = 0
    last_dev = None
    for i in range(days_lookback):
        # 窗口末端索引（倒数第 i+4 根），向前取 3 根计算 3 日涨幅
        si = -(i + 4)
        if si - 2 < -len(closes):
            continue
        s_chg = (
            (closes[si] - closes[si - 2]) / closes[si - 2] * 100 if closes[si - 2] > 0 else 0
        )
        ii = -(i + 4)
        if ii - 2 < -len(idx_closes):
            continue
        i_chg = (
            (idx_closes[ii] - idx_closes[ii - 2]) / idx_closes[ii - 2] * 100
            if idx_closes[ii - 2] > 0
            else 0
        )
        dev = s_chg - i_chg
        if abs(dev) >= 20:
            count += 1
            last_dev = dev
    return count, last_dev


def check_stock(s, idx_rets, index_closes_pool):
    code = s["code"]
    name = s["name"]
    # V16.4.1: 上市不足 3 个交易日的新股跳过偏离异动判定——
    # 创业板/科创板新股前 5 日无涨跌幅限制(首日 +662% 等), 3/10/20 日偏离无意义
    # (2026-08-12 实测 301717 超纯应材 8/11 上市首日 +662.24% → 20日偏离被误算 +676.84%)
    if not s.get("change_pct_1d") and not s.get("change_pct_2d"):
        return []
    idx_code = get_stock_index(code)
    idx = idx_rets.get(idx_code, {})
    th = int(limit_pct_for(code, name))  # V17.0 S3: 直调统一阈值(替代 get_threshold)
    board = get_board_name(code, name)
    results = []
    if s["ret_3d"] != 0 and idx.get("ret_3d") is not None:
        dev = calc_official_deviation(s["ret_3d"], idx["ret_3d"])
        if board == "主板":
            if 18 <= abs(dev) < 20:
                results.append(
                    {
                        "level": "卡异动",
                        "tag": "💎",
                        "desc": f"3日偏离值{dev:+.2f}%，距主板20%红线仅差{20-abs(dev):.2f}%",
                        "score": abs(dev),
                    }
                )
        elif board in ("创业板", "科创板"):
            if 27 <= abs(dev) < 30:
                results.append(
                    {
                        "level": "卡异动",
                        "tag": "💎",
                        "desc": f"3日偏离值{dev:+.2f}%，距{board}30%红线仅差{30-abs(dev):.2f}%",
                        "score": abs(dev),
                    }
                )
        if abs(dev) >= th:
            hist_cnt = 0
            # V16.2.12: 北交所老段（8/4 开头）白名单服务器无 K 线（实测 832000/430047），
            # 历史偏离无法计算 → 直接 0（正确降级），跳过 7s 换台探测
            if code.startswith(("8", "4")):
                hist_cnt = 0
            else:
                try:
                    hist_cnt, _ = count_history_deviations(code, idx_code, index_closes_pool, 10)
                except Exception as _e:
                    _debug_log(f"mak hist_deviation error: {_e}")
                    hist_cnt = 0
            cnt_warn = ""
            if board == "主板" and hist_cnt >= 3:
                cnt_warn = f" ⚠️ 近10日已触发{hist_cnt}次同向异动！再触发1次停牌核查！"
            elif board in ("创业板", "科创板") and hist_cnt >= 2:
                cnt_warn = f" ⚠️ 近10日已触发{hist_cnt}次同向异动！再触发1次停牌核查！"
            _tr = s.get("turnover", 0)
            vol_note = ""
            if _tr < _vol_locked:
                vol_note = " [极度锁仓，动能强劲]"
            elif _tr > _vol_overload:
                vol_note = " [爆量滞涨，警惕派发]"
            results.append(
                {
                    "level": "已触发",
                    "tag": "🔥" if dev > 0 else "💥",
                    "desc": f"3日偏离值{dev:+.2f}%≥{th}%({board})触发短期异动{vol_note}{cnt_warn}",
                    "score": abs(dev),
                }
            )
    if s["ret_10d"] != 0 and idx.get("ret_10d") is not None:
        # V16.0: 统一复利口径（与 3 日偏离一致），原代码用简单减法
        dev = calc_official_deviation(s["ret_10d"], idx["ret_10d"])
        ceiling = 100 - dev if dev > 0 else None
        ceiling_note = ""
        if ceiling is not None and ceiling > 0:
            limit_pct = limit_pct_for(code, s.get("name", ""))
            remaining_stops = ceiling / limit_pct
            if remaining_stops <= 3:
                ceiling_note = f" 距100%仅剩{ceiling:.1f}%（约{remaining_stops:.1f}涨停）！"
        if dev >= _ret10_warn:
            results.append(
                {
                    "level": "严重",
                    "tag": "🔥🔥",
                    "desc": f"10日偏离值{dev:+.2f}%≥+{_ret10_warn:.0f}%，触发严重异动！{ceiling_note}",
                    "score": dev,
                }
            )
        elif dev <= _ret10_down:
            results.append(
                {
                    "level": "严重",
                    "tag": "💥💥",
                    "desc": f"10日偏离值{dev:+.2f}%≤{_ret10_down:.0f}%, 触发严重异动",
                    "score": -dev,
                }
            )
        elif ceiling is not None and ceiling <= 15:
            results.append(
                {
                    "level": "严重预警",
                    "tag": "🚨",
                    "desc": f"10日偏离值{dev:+.2f}%（距100%仅剩{ceiling:.1f}%）{ceiling_note}",
                    "score": dev,
                }
            )
    # V16.0: 无真实 30 日数据时不再用 (ret_60d - idx_60d)/2 冒充 30 日偏离，
    # 改为 20 日复利口径偏离（用真实的 ret_20d），避免捏造指标。
    if s["ret_20d"] != 0 and idx.get("ret_20d") is not None:
        dev_20d = calc_official_deviation(s["ret_20d"], idx["ret_20d"])
        if dev_20d >= 100:
            results.append(
                {
                    "level": "严重",
                    "tag": "🔥🔥🔥",
                    "desc": f"20日偏离值{dev_20d:+.2f}%≥+100%, 触发严重异动！",
                    "score": dev_20d,
                }
            )
        elif dev_20d <= -50:
            results.append(
                {
                    "level": "严重",
                    "tag": "💥💥💥",
                    "desc": f"20日偏离值{dev_20d:+.2f}%≤-50%, 触发严重异动",
                    "score": -dev_20d,
                }
            )
    return results


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
            ind_code = _em_ind_map.get(code, "") or (ind_code if _is_industry_code(ind_code) else "")
            if not ind_code:
                continue
            # V16.0: 优先用腾讯实时涨跌幅（今日盘中），否则退回 ZHB T-1
            _rt = _tencent_rt.get(code)
            _rt_chg = _rt.get("change_pct") if _rt else None
            chg = _rt_chg if _rt_chg is not None else (stat.get("change_pct", 0) or 0)
            # V16.3 O27: 板块成交额改腾讯 T 日聚合（amount_wan 万→亿），
            # 原 ZHB T-1 amount 盘中失真（成交额是昨日）；腾讯缺失时退回 T-1
            _rt_amt = _rt.get("amount_wan") if _rt else None
            amt = (_rt_amt / 10000.0) if _rt_amt else ((stat.get("amount", 0) or 0) / 10000.0)  # 万→亿
            # 2026-08-11: 修复恒 0——腾讯 mcap_yi → price×股本计算兜底（与 val 4 级兜底同思路）
            _rt_mcap = _safe_float(_rt.get("mcap_yi", 0)) if _rt else 0
            mcap = _rt_mcap
            if not mcap:
                _rt_price = _safe_float(_rt.get("price", 0)) if _rt else 0
                _base = _rt_price if _rt_price > 0 else (_safe_float(stat.get("price", 0) or 0))
                if _base > 0:
                    mcap = _safe_float(_calc_mcap_yi(code, _base) or 0)
            # H1 修复(2026-08-15 二审): 板块主力净流入改用 ulist 批量 f62+f66 结果(真主力, 带符号),
            # 不再用 ZHB main_net_buy_amount(实为竞价额恒正→"虚涨"判定恒空/“真金白银”恒满)
            main_net = _MAIN_NET_MAP_GLOBAL.get(code, 0.0)
            if not main_net:
                main_net = (_safe_float(stat.get("main_net_buy_amount", 0)) or 0) * 1e4  # 兜底: 竞价额(标注)
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
                _nm = get_stock_name_from_zhb(_c) or _tq_names.get(_c, "") or _c
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
                        "main_net_amount": _safe_float(_st.get("main_net_buy_amount", 0)) * 1e4,
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
                "top5_stocks": [
                    {"code": st["code"], "name": st["name"], "change_pct": st.get("change_pct", 0)}
                    for st in _top5
                ],
            }
        )
    return result


def annotate_technical_pattern(code):
    try:
        closes, _ = get_baidu_kline(code, 25)
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
        for _ in range(7):
            _td -= timedelta(days=1)
            if is_trading_day(_td):
                break
    today_str = _td.strftime("%Y-%m-%d")
    now = datetime.now()
    _mkt_status, _mkt_note = get_market_status(now)
    lines = []

    def L(s=""):
        lines.append(s)

    L("=" * 90)
    L(f"  📊 A股异动及行业轮动扫描报告 — {today_str} {now.strftime('%H:%M:%S')} {_mkt_note}")
    L("=" * 90)
    print("[数据装载] 获取全市场多日数据与指数基准...", flush=True)
    _t0 = time.time()
    all_stocks = await get_market_abnormal_data()
    # V16.2.7: ZHB 全市场快照含 ETF/LOF/可转债（7948 只）——选股无意义且拖慢扫描，
    # 过滤为纯 A 股（与 val 的 _is_a_stock 同口径：00/30/60/68/92 前缀）
    _before = len(all_stocks)
    all_stocks = [s for s in all_stocks if _is_a_stock(s.get("code", ""))]
    if len(all_stocks) < _before:
        print(f"  📋 A股过滤: 移除 {_before - len(all_stocks)} 只 ETF/LOF/可转债（{_before} → {len(all_stocks)}）", flush=True)
    _zhb_date = get_zhb_data_date()
    _zhb_fresh = is_zhb_data_fresh(max_delay_days=3)
    if _zhb_date:
        _fresh_tag = "✅新鲜" if _zhb_fresh else "⚠️延迟"
        print(
            f"  ⚡ zhb全市场: {len(all_stocks)}只（{_zhb_date} {_fresh_tag}），耗时{time.time()-_t0:.2f}s",
            flush=True,
        )
    idx_rets, index_closes_pool = get_index_returns()
    for ic, nm in INDEX_MAP.items():
        r = idx_rets.get(ic, {})
        L(f"  📈 {nm}: 3日{_fmt_ret(r.get('ret_3d'))}%  10日{_fmt_ret(r.get('ret_10d'))}%")
    print("[异动引擎] 扫描全市场异动信号...", flush=True)
    results = {"卡异动": [], "已触发": [], "严重": [], "严重预警": []}

    # V9.3.3: 并行扫描（ThreadPoolExecutor，max_workers=3）
    def _check_one(s):
        """单股票检测，返回 (code, name, rules)"""
        try:
            rules = check_stock(s, idx_rets, index_closes_pool)
            return (s["code"], s["name"], rules)
        except Exception as _e:
            _debug_log(f"mak check_stock error {s['code']}: {_e}")
            return (s["code"], s["name"], [])

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(_check_one, s): s for s in all_stocks}
        for i, future in enumerate(as_completed(futures)):
            if i % 1000 == 0:
                print(f"  已扫描 {i}/{len(all_stocks)}", flush=True)
            try:
                code, name, rules = future.result()
                for r in rules:
                    results[r["level"]].append({**r, "code": code, "name": name})
            except Exception as _e:
                _debug_log(f"mak future.result error: {_e}")
    total_abnormal = len(results["已触发"]) + len(results["严重"])
    # V16.0: 复用统一 is_limit_up/is_limit_down（自动识别 ST 与板块阈值），
    # 消除硬编码 9.5/19.5 导致 ST 涨停漏判的问题（ST 10% 与主板一致）
    _zt_count = sum(
        1 for s in all_stocks if is_limit_up(s["code"], s.get("name", ""), s.get("change_pct", 0))
    )
    _zt_float = sum(
        1 for s in all_stocks
        if 5 <= s.get("change_pct", 0) < limit_pct_for(s["code"], s.get("name", ""))
    )
    _zb_rate = _zt_float / max(_zt_count + _zt_float, 1) * 100
    _dt_count = sum(
        1 for s in all_stocks if is_limit_down(s["code"], s.get("name", ""), s.get("change_pct", 0))
    )
    _lbp = _zt_count
    L(f"\n{'='*90}")
    L("【A. 全市场情绪监测看板】")
    L(f"{'─'*90}")
    # V17.0(2026-08-15): 北向宏观资金 + 两融杠杆情绪(A 段增强, P4)
    try:
        from stock_common.sc_datasource import get_hsgt_macro_flow

        # ⚠️ 修复(2026-08-15): 同步网络调用在 async 上下文会阻塞事件循环 → to_thread 包装
        _hsgt = await asyncio.to_thread(get_hsgt_macro_flow)
        if _hsgt:
            _hsig = "偏多" if _hsgt.get("total", 0) > 0 else "偏空"
            L(f"  🌐 北向资金: 净流入 {_hsgt.get('total', 0):.2f} 亿(沪 {_hsgt.get('hgt', 0):.2f} | 深 {_hsgt.get('sgt', 0):.2f}) 外资情绪{_hsig}")
            # M13 修复(2026-08-15 二审): 数据降级标记(与 med 一致, 2026-08-12 深股通 379.75 亿异常)
            if _hsgt.get("data_quality") == "degraded":
                L(f"  ⚠️ 北向数据降级: {_hsgt.get('warning', '源数据异常')}")
        else:
            L("  🌐 北向资金: (数据获取失败)")
    except Exception as _e:
        _debug_log(f"mak hsgt macro: {_e}")
    _up_cnt = sum(1 for s in all_stocks if s.get("change_pct", 0) > 0)
    _down_cnt = sum(1 for s in all_stocks if s.get("change_pct", 0) < 0)
    _ud_ratio = _up_cnt / max(_down_cnt, 1)
    L(f"  🌡️ 短线情绪: 涨停{_zt_count} | 跌停{_dt_count} | 异动触发{total_abnormal}只"
      f"（涨停按涨跌幅口径,与 B 段涨停池口径不同）")
    L(
        f"  📊 市场广度: 上涨{_up_cnt}/下跌{_down_cnt} | 涨跌比{_ud_ratio:.2f} | {'偏多' if _ud_ratio>1.5 else '偏空' if _ud_ratio<0.7 else '均衡'}"
    )

    # V16.1.7: 财联社市场情绪增强（字典 §12.10.2 实测可用——热度/封板率/炸板/高开率/获利率/连板梯队）
    # V16.3 O37: KPL 情绪互校（字典 §12.15.2——财联社 → 开盘红 → KPL 三源兜底，8/7 交叉验证：涨停 74 三家一致）
    try:
        from stock_common import get_cls_market_emotion
        _emotion = await asyncio.to_thread(get_cls_market_emotion)  # M10: 防阻塞
        if not _emotion:
            # O37: 财联社失败 → KPL 兜底（strong 情绪值/连板高度——匿名接口）
            try:
                from stock_common import get_kpl_market_sentiment, get_kpl_broken_ratio
                _kpl = await asyncio.to_thread(get_kpl_market_sentiment)  # M10: 防阻塞
                _kbr = get_kpl_broken_ratio()
                if _kpl:
                    _ks = _kpl.get("strong")
                    if _ks is not None:
                        _emo_tag = "🔥 亢奋" if _ks >= 75 else "😐 中性" if _ks >= 40 else "🧊 冰点"
                        L(f"  🌡️ 开盘啦情绪值: {_ks}/100 {_emo_tag}（连板高度 {_kpl.get('lbgd')} | 大幅回撤 {_kpl.get('df_num')}）")
                    if _kbr:
                        L(f"  📈 开盘啦破板率: {_kbr.get('broken_ratio')}（涨停 {_kbr.get('zt')} | 跌停 {_kbr.get('dt')} | 炸板 {_kbr.get('broken_num')}）")
            except Exception as _e2:
                _debug_log(f"mak kpl emotion fallback: {_e2}")
        elif _emotion:
            _md = _emotion.get("market_degree")
            _ur = _emotion.get("up_ratio")
            _uo = _emotion.get("up_open_num")
            _perf = _emotion.get("performance")
            _uor = _emotion.get("up_open_ratio")
            _pr = _emotion.get("profit_ratio")
            if _md is not None:
                _emo_tag = "🔥 亢奋" if _md >= 75 else "😐 中性" if _md >= 40 else "🧊 冰点"
                L(f"  🌡️ 财联社市场热度: {_md}/100 {_emo_tag}")
            if _ur is not None:
                L(f"  📈 封板率: {_ur}（炸板 {_uo} 只）| 高开率: {_uor} | 获利率: {_pr} | 昨涨停今表现: {_perf}")
            _ladder = _emotion.get("limit_up_board") or {}
            if isinstance(_ladder, dict) and _ladder:
                _ladder_str = " | ".join(f"{k}{v.get('count','')}家({v.get('continuous_rate','')})" for k, v in list(_ladder.items())[:4])
                L(f"  🪜 财联社连板梯队: {_ladder_str}")
            # O37: KPL 情绪指标互校（strong/连板高度——不同体系独立验证）
            try:
                from stock_common import get_kpl_market_sentiment
                _kpl = get_kpl_market_sentiment()
                if _kpl and _kpl.get("strong") is not None:
                    L(f"  🧭 开盘啦互校: 情绪值 {_kpl.get('strong')} | 连板高度 {_kpl.get('lbgd')} | 涨停 {_kpl.get('ztjs')}（独立源交叉验证）")
            except Exception as _e3:
                _debug_log(f"mak kpl emotion cross-check: {_e3}")
    except Exception as _e:
        _debug_log(f"mak cls_market_emotion: {_e}")

    # V10.3: 全市场主力净买入总量
    # H2 修复(2026-08-15 二审): 改用 ulist 批量 f62+f66 真主力(带符号)——原 ZHB main_net_buy_amount
    # 实为竞价额(恒正)→ 求和恒正, "大幅净流入"信号恒触发
    _total_main_net_buy = 0
    _main_net_buy_count = 0
    if _MAIN_NET_MAP_GLOBAL:
        for _code, _mna in _MAIN_NET_MAP_GLOBAL.items():
            _total_main_net_buy += _mna
            if _mna > 0:
                _main_net_buy_count += 1
    _main_net_src_label = "ulist f62+f66 口径"
    if not _MAIN_NET_MAP_GLOBAL:
        # H2 终审修复: ZHB 兜底为万元值——统一 /1e4 转亿元(原共用 /1e8 小 1e4 倍), 标签区分
        _stat2_snapshot = get_zhb_market_stat2_snapshot()
        if _stat2_snapshot:
            for _code, _stat in _stat2_snapshot.items():
                _mna = _safe_float(_stat.get("main_net_buy_amount", 0))
                if _mna:
                    _total_main_net_buy += _mna
                    if _mna > 0:
                        _main_net_buy_count += 1
        _total_main_net_buy_yi = _total_main_net_buy / 1e4
        _main_net_src_label = "ZHB 竞价额兜底口径(⚠️非主力)"
    else:
        _total_main_net_buy_yi = _total_main_net_buy / 1e8
    L(
        f"  💰 主力资金: 全市场主力净流入{_total_main_net_buy_yi:+.2f}亿元"
        f"（{_main_net_buy_count}只净流入，{_main_net_src_label}）"
    )
    if _total_main_net_buy_yi > 50:
        L(f"    🟢 主力资金大幅净流入，市场资金面偏多")
    elif _total_main_net_buy_yi < -50:
        L(f"    🔴 主力资金大幅净流出，市场资金面偏空")
    if _lbp > 80:
        L(f"    🔥 涨停{_lbp}家 > 80，情绪极度亢奋，警惕分化回落")
    if total_abnormal > 40 and _lbp > 60:
        L("    ⚠️ 异动+涨停双高，情绪高潮临界点，谨防次日退潮")
    if _dt_count > 20:
        L(f"    💥 跌停{_dt_count}家 > 20，亏钱效应扩散，防御优先")
    _zt_3d = [
        s for s in all_stocks if is_limit_up(s["code"], s.get("name", ""), s.get("change_pct", 0))
    ]
    _lb_3d = {}
    _max_board = 0
    for s in _zt_3d:
        r3 = s.get("ret_3d", 0)
        code = s.get("code", "")
        # V16.2: 按板块统一阈值（主板/ST 10, 创业板·科创板 20, 北交所 30）
        _lim = limit_pct_for(code, s.get("name", ""))
        if r3 >= _lim * 2.9:
            _lb_3d['3板+'] = _lb_3d.get('3板+', 0) + 1
            _max_board = max(_max_board, 3)
        elif r3 >= _lim * 1.9:
            _lb_3d['2板'] = _lb_3d.get('2板', 0) + 1
            _max_board = max(_max_board, 2)
        elif r3 >= _lim * 0.95:
            _lb_3d['首板'] = _lb_3d.get('首板', 0) + 1
    if _lb_3d:
        _ladder_str = ' | '.join(f'{k}: {v}家' for k, v in sorted(_lb_3d.items()))
        _max_desc = f", 最高{_max_board}板" if _max_board else ", 最高首板"
        L(f"  📊 连板梯队: {_ladder_str}{_max_desc}")
        if _max_board >= 4:
            L(f"    🔥 高标{_max_board}板打开空间，可积极做多")
        elif _max_board <= 1 and _zt_count > 30:
            L("    ⚠️ 涨停多但无高度板，首板跟风为主，持续性存疑")
    _up_abn = [r for r in results["已触发"] if r.get("tag") == "🔥"]
    if _up_abn:
        # V16.1: 原"异动信号回测(近似)"表述是伪回测（统计的是已上涨股票当前 ret_5d，
        # 非信号发出后的前瞻收益）→ 改为现状描述，不做胜率暗示
        _pos_5d = 0
        for r in _up_abn[:30]:
            for s in all_stocks:
                if s["code"] == r["code"] and s.get("ret_5d", 0) > 0:
                    _pos_5d += 1
                    break
        _pos_ratio = _pos_5d / min(len(_up_abn), 30) * 100
        L(
            f"  📊 多头异动股近5日涨幅为正的比例: {_pos_ratio:.0f}%（{min(len(_up_abn),30)}只样本，现状统计非前瞻回测）"
        )
    L(f"{'─'*90}")
    L(
        f"  扫描汇总: 卡异动{len(results['卡异动'])}只 | 已触发{len(results['已触发'])}只 | 严重{len(results['严重'])}只"
    )
    if total_abnormal > 40:
        L(f"  ⚠️ 全市场异动总数{total_abnormal}只处于历史高位，警惕监管降温")
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
    # 板块-异动交叉分析
    L(f"\n{'='*90}")
    L("【B. 涨停池扫描（打板情绪看板）】")
    L(f"{'─'*90}")
    try:
        # V16.3.3 (2026-08-10 字典 12.15.5): 涨停数三源互校——财联社=KPL=复盘啦
        # （2026-08-10 实测 99=99=99 一致）；push2ex 明细仍作主数据源
        try:
            from stock_common import get_limit_pool_multi_source

            _multi = get_limit_pool_multi_source()
            if _multi.get("sources"):
                _src_txt = " / ".join(
                    f"{k}={v}" for k, v in _multi["sources"].items() if v is not None
                )
                _verified = "✅ 三源互校一致" if _multi.get("cross_verified") else "⚠️ 源间差异"
                L(f"  📊 涨停数互校: 财联社/KPL/复盘啦 {_src_txt} → {_multi.get('total')} 只 {_verified} | 最高连板 {_multi.get('max_ladder')}")
        except Exception as _e:
            _debug_log(f"mak multi_source error: {_e}")

        from stock_common import get_limit_pool_summary

        pool = get_limit_pool_summary()
        zt_count = pool.get("limit_up_count", 0)
        zb_count = pool.get("limit_broken_count", 0)
        dt_count = pool.get("limit_down_count", 0)
        success_rate = pool.get("success_rate", 0)
        L(
            f"  涨停 {zt_count} 只 | 炸板 {zb_count} 只 | 跌停 {dt_count} 只 | 封板率 {success_rate:.0f}%"
        )

        # 涨停板块分布
        sector_stats = pool.get("sector_stats", {})
        if sector_stats:
            L("\n  涨停板块分布（TOP10）:")
            for sec, cnt in list(sector_stats.items())[:10]:
                L(f"    {sec}: {cnt} 只")

        # 涨停明细
        zt_list = pool.get("limit_up_list", [])
        if zt_list:
            L("\n  涨停明细（按封板时间排序）:")
            L(
                f"  {'代码':<8} {'名称':<10} {'涨跌幅':>8} {'连板':>4} {'封板时间':>8} {'封板资金(亿)':>10} {'板块':<12}"
            )
            L(f"  {'-'*70}")
            for item in zt_list[:30]:
                fund_yi = item.get('limit_fund', 0) / 1e8 if item.get('limit_fund', 0) else 0
                # H2(审查 2026-08-16): ths 优先源输出 first_time(已格式化 HH:MM:SS),
                # 东财 push2ex 输出 first_limit_time(5 位串 "92500")——双键兼容;
                # ths 路径直接显示格式化时间, 东财路径按 HHMM 拆
                fbt_raw = item.get('first_limit_time', '') or item.get('first_time', '')
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
                    f"  {item.get('code',''):<8} {item.get('name',''):<10}{_name_mark(item.get('name',''))} {item.get('change_pct',0):>+8.2f}% {item.get('limit_count',0):>4.0f} {fbt_fmt:>8} {fund_yi:>+10.2f} {item.get('sector',''):<12}"
                )

        # 炸板明细
        zb_list = pool.get("limit_broken_list", [])
        if zb_list:
            L("\n  炸板明细:")
            for item in zb_list[:15]:
                L(
                    f"    {item.get('code','')} {item.get('name','')}{_name_mark(item.get('name',''))} 涨幅{item.get('change_pct',0):+.2f}% 炸板{item.get('broken_count',0):.0f}次 板块:{item.get('sector','')}"
                )
    except Exception as _e:
        _debug_log(f"mak limit_pool: {_e}")
        L("  (打板数据获取失败)")

    # V16.1.7: 开盘红涨停天梯（字典 §12.10.4 实测可用）
    # V17.0.1f(2026-08-16): 移除盘口异动段——用户原则: 5 大脚本零东财 push2ex 接口
    try:
        from stock_common import get_kph_limit_ladder
        L(f"\n{'='*90}")
        L("【B+. 涨停天梯（开盘红）】")
        L(f"{'─'*90}")
        # V16.4.1: 提前初始化——import/接口失败时 _ladder 未定义, L1562 引用会 NameError 击穿
        _ladder = []
        _ladder = get_kph_limit_ladder()
        if _ladder:
            L(f"  涨停天梯共 {len(_ladder)} 只:")
            L(f"  {'代码':<8} {'名称':<10} {'连板':>4} {'大单一字':>6} {'人气':>4} {'板块涨停':>6} {'个股额(亿)':>10}")
            L(f"  {'-'*70}")
            for s in _ladder[:20]:
                _one = "✓" if s.get("one_word") else ""
                _pop = "🔥" if s.get("popular") else ""
                _amt = _safe_float(s.get("amount", 0)) / 1e8
                L(f"  {str(s.get('code','')):<8} {str(s.get('name','')):<10} {s.get('limit_count',0):>4} {_one:>6} {_pop:>4} {s.get('plate_limit_up_count',0):>6} {_amt:>10.2f}")
        else:
            L("  (涨停天梯数据获取失败)")
    except Exception as _e:
        _debug_log(f"mak ladder: {_e}")

    L(f"\n{'='*90}")
    # V16.4.0: 同花顺独家交叉验证（原 G 段移入——涨停明细末尾备注）
    try:
        _ths_pool = await get_ths_hot_pool(today_str)
    except Exception as _e:
        _debug_log(f"mak ths pool note: {_e}")
        _ths_pool = []
    if _ths_pool:
        _zt_all = {s.get('code', '') for s in _zt_3d} if '_zt_3d' in dir() else set()
        _ladder_all = {str(s.get('code', '')) for s in (_ladder or [])} if isinstance(_ladder, list) else set()
        _ths_only = [h for h in _ths_pool if h.get('code') not in _zt_all and h.get('code') not in _ladder_all]
        L('')
        L(f"  ❗ 同花顺独家 {len(_ths_only)} 只（东财口径未覆盖，交叉验证增量）:")
        if _ths_only:
            L(f"  {'代码':<8} {'名称':<10} {'涨幅%':>7} {'题材':<30}")
            L(f"  {'-'*65}")
            for _h in _ths_only[:10]:
                L(f"  {_h.get('code',''):<8} {_h.get('name',''):<10}{_name_mark(_h.get('name',''))} {_safe_float(_h.get('zhangfu',0)):>+7.2f}% {str(_h.get('reason',''))[:30]:<30}")

    L("【C. 板块-异动集中度分析】")
    L(f"{'─'*90}")
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
    if _sector_density or _dt_map:
        L("  异动集聚板块TOP5（异动股数/密度，含龙虎榜补全）:")
        for _nm, _cnt, _den in _sector_density[:5]:
            L(f"    {normalize_industry(_nm)}: {_cnt}只异动（板块内密度{_den:.1f}%）")
            _s = next((s for s in sorted_sectors if s["name"] == _nm), None)
            if _s:
                _stocks = get_sector_stocks(_s["code"])
                _sc = [st["code"] for st in _stocks]
                for _abn in results["已触发"] + results["严重"]:
                    if _abn["code"] in _sc:
                        L(f"      {_abn['code']} {_abn['name']} - {_abn.get('desc','')}")
                # 补全龙虎榜异动股票
                for _c, _dt in _dt_map.items():
                    if _c in _sc and _c not in _abnormal_codes:
                        _dtn = _dt.get("name", "")
                        _dt_display = f"{_c} {_dtn}" if _dtn else _c
                        L(
                            f"      {_dt_display} (龙虎榜) - {_dt['reason'][:40]} | 净买{_dt['net_buy']:.0f}万"
                        )
    else:
        L("  今日异动股较少，未形成明显板块集聚")
    # 近5日异动回溯（基于10日/20日/60日偏离值反推）
    _recent_high = []
    for s in all_stocks:
        _r3 = s.get("ret_3d", 0)
        _r10 = s.get("ret_10d", 0)
        _r20 = s.get("ret_20d", 0)
        _r60 = s.get("ret_60d", 0)
        # V16.2: 3日阈值统一（主板/ST 10 / 双创 20 / 北交所 30）
        _th = limit_pct_for(s.get("code", ""), s.get("name", ""))
        _matched = False
        # 10日严重：近日可能触发过
        if abs(_r10) >= 80:
            _matched = True
        # 20日严重
        if abs(_r20) >= 150:
            _matched = True
        # 3日已触发（当天或最近几天内）
        if abs(_r3) >= _th:
            _matched = True
        if _matched:
            _recent_high.append((s["code"], s["name"], _r3, _r10, _r20))
    # 龙虎榜补全回溯名单
    if _dt_map:
        for _c, _dt in _dt_map.items():
            if _c not in {_r[0] for _r in _recent_high}:
                _s = next((s for s in all_stocks if s["code"] == _c), None)
                if _s:
                    _recent_high.append(
                        (
                            _c,
                            _s["name"],
                            _s.get("ret_3d", 0),
                            _s.get("ret_10d", 0),
                            _s.get("ret_20d", 0),
                        )
                    )
                else:
                    # ST/退市不在 all_stocks 池中 → 从 TDX K线 临时算 3/10/20 日涨幅
                    _r3 = _r10 = _r20 = 0
                    try:
                        _k, _kr = baidu_kline_full(_c, count=30)
                        if _k and _kr:
                            _ci = next(
                                (i for i, kk in enumerate(_k) if kk in ("close", "close_price")), -1
                            )
                            if _ci >= 0:
                                _cls = [_safe_float(r[_ci]) for r in _kr if len(r) > _ci]
                                if len(_cls) >= 22:
                                    _r3 = (_cls[-1] / _cls[-4] - 1) * 100 if _cls[-4] > 0 else 0
                                    _r10 = (_cls[-1] / _cls[-11] - 1) * 100 if _cls[-11] > 0 else 0
                                    _r20 = (_cls[-1] / _cls[-21] - 1) * 100 if _cls[-21] > 0 else 0
                    except Exception as _e:
                        _debug_log(f"mak recent_high_kline error: {_e}")
                    _recent_high.append((_c, _dt.get("name", ""), _r3, _r10, _r20))
    _recent_high.sort(key=lambda x: abs(x[3]), reverse=True)
    if _recent_high:
        _recent_top = _recent_high[:50]
        _recent_ann = {}
        _ann_t0 = time.time()
        for _r in _recent_top[:15]:
            try:
                _a, _s = get_abnormal_announcements(_r[0])
                if _a > 0:
                    _recent_ann[_r[0]] = (_a, _s)
            except Exception as _e:
                _debug_log(f"mak abnormal_announcements error: {_e}")
        _ann_dt = time.time() - _ann_t0
        print(f"  公告查询耗时: {_ann_dt:.2f}s", flush=True)
        L(f"\n{'='*90}")
        L("【近3日异动回溯（高偏离值个股，可能近日触发过异动）】")
        L(f"{'─'*90}")
        L(f"  {'代码':<8} {'名称':<12} {'3日偏离':>9} {'10日偏离':>9} {'20日偏离':>9} {'公告':<12}")
        L(f"  {'-'*75}")
        _shown = 0
        for _r in _recent_top[:30]:
            _a_info = ""
            if _r[0] in _recent_ann:
                _a_cnt, _s_cnt = _recent_ann[_r[0]]
                _a_info = f"已发{_a_cnt}份(严重{_s_cnt}份)" if _s_cnt > 0 else f"已发{_a_cnt}份"
            else:
                continue
            L(
                f"  {_r[0]:<8} {_r[1]:<12} {_r[2]:>+9.2f}% {_r[3]:>+9.2f}% {_r[4]:>+9.2f}% {_a_info:<12}"
            )
            _shown += 1
        if _shown == 0:
            L("  (近3日无股票触发异常波动公告)")
        L("  \n  💡 注: 回溯基于当日快照的10日/20日偏离值反推，非精确历史回放")

    L(f"\n{'='*90}")
    L("【D. 行业轮动强度扫描】")
    L(f"{'─'*90}")
    top10 = sorted_sectors[:10]
    L(f"  行业总数: {len(sectors)}个")
    L(
        f"  {'排名':<6} {'板块名称':<18} {'评分':>5} {'涨跌幅':>7} {'成交额(亿)':>9} {'主力净流(亿)':>11}"
    )
    L(f"  {'-'*55}")
    for i, ts in enumerate(top10, 1):
        name = normalize_industry(ts["name"])
        _mfi = round(ts.get('main_inflow', 0) / 1e8, 2) if abs(ts.get('main_inflow', 0)) > 0 else 0
        L(
            f"  {i:<6} {name:<18} {ts.get('score',0):>5.1f} {ts['change_pct']:>+7.2f}% {ts.get('amount_yi',0):>9.1f} {_mfi:>+11.2f}"
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
                L(f"\n  🧭 外部轮动对照（开盘啦强度分 top5）:")
                for _p in _pr_top:
                    L(f"      #{_p['rank']} {_p['code']} {_p['name']} 强度 {_p['value']} {'↑' if _p['color']=='red' else '↓'}")
        except Exception as _e:
            _debug_log(f"mak plate rotation cross-check: {_e}")
    else:
        L("\n  ⚠️ 无法获取行业板块数据")
    L(f"\n{'='*90}")
    L("【E. TOP10 板块深度分析（涨停梯队 + 龙头股）】")
    L(f"{'─'*90}")
    top_analysis = analyze_top_stocks(top10)
    for ta in top_analysis:
        nm = normalize_industry(ta["sector"])
        _code = ta['data'].get('code', '')
        # V16.3 L: ZHB 旁路板块 code=行业名（非 BK 码）→ 避免 "煤炭开采 (煤炭开采)" 重复
        _code_show = f" ({_code})" if _code and _code != ta["sector"] else ""
        L(f"\n  🔥 {nm}{_code_show} 总分={ta['data'].get('score',0):.1f}")

        L(f"     ├─ 成分股总数: {ta.get('total_stocks',0)} 只")
        if ta['limit_up_count'] > 0:
            _zt_names = ' '.join(st['name'] + st['code'] for st in ta['limit_up_stocks'])
            L(f"     ├─ 涨停家数: {ta['limit_up_count']} 只 → {_zt_names}")
        else:
            L("     ├─ 涨停家数: 0 只")
        _top5 = ta.get('top5_stocks', [])
        if _top5:
            L("     └─ 涨幅 TOP5:")
            for _t5 in _top5:
                _t5_chg = _t5.get('change_pct', 0)
                _t5_icon = '🚀' if _t5_chg >= 10 else ('📈' if _t5_chg >= 5 else '  ')
                L(f"       {_t5_icon} {_t5['name']}({_t5['code']})  {_t5_chg:>+8.2f}%")
        _items = []
        for _st in ta['limit_up_stocks']:
            # V16.0: 统一 is_limit_up 判断（ST 10% 与主板一致）
            _label = (
                '涨停'
                if is_limit_up(_st['code'], _st.get('name', ''), _st.get('change_pct', 0))
                else f"{_st.get('change_pct',0):+.1f}%"
            )
            _items.append(f"{_st['name']}({_st['code']}, {_label})")
        L(f"    龙头: {' | '.join(_items)}")
    L(f"\n{'='*90}")
    L("【F. 资金流验证：真金白银 vs 虚涨】")
    L(f"{'─'*90}")
    # V16.4.0: 按评分筛选（原 sectors[:50] 前 50 高评分板块可能全为净流入 → 虚涨段恒空）
    _scored = [s for s in sectors if s.get("score", 0) >= 30] or sectors
    with_money = [s for s in _scored if s.get("main_inflow", 0) > 0]
    without_money = [s for s in _scored if s.get("main_inflow", 0) <= 0]
    without_money = [s for s in sectors[:50] if s.get("main_inflow", 0) <= 0]
    if with_money:
        _sorted_in = sorted(with_money, key=lambda x: x.get('main_inflow', 0), reverse=True)
        L("  ✅ 真金白银: 高评分且主力净流入:")
        for s in _sorted_in[:10]:
            L(
                f"    {normalize_industry(s['name'])}: 评分{s.get('score',0):.1f} 涨幅{s['change_pct']:+.2f}% 净流入{round(s['main_inflow']/1e8,2):+.2f}亿"
            )
    if without_money:
        _sorted_out = sorted(without_money, key=lambda x: x.get('main_inflow', 0), reverse=True)
        L("  ⚠️ 虚涨（主力净流出）:")
        for s in _sorted_out[:10]:
            L(
                f"    {normalize_industry(s['name'])}: 评分{s.get('score',0):.1f} 涨幅{s['change_pct']:+.2f}% 主力净流出{round(abs(s['main_inflow'])/1e8,2):.2f}亿"
            )
    _lurking = [
        s for s in sectors if s.get("main_inflow", 0) > 3e8 and 1 <= s.get("change_pct", 0) <= 5
    ]
    _lurking.sort(key=lambda x: x.get("main_inflow", 0), reverse=True)
    if _lurking:
        L("\n  🕵️ 潜伏信号（主力大幅流入但涨幅不大，可能正在建仓）:")
        L(f"  {'-'*60}")
        for _l in _lurking[:5]:
            _lnm = normalize_industry(_l["name"])
            _lfi = round(_l["main_inflow"] / 1e8, 2)
            L(f"    {_lnm}: 涨幅{_l['change_pct']:+.2f}% 主力净流入{_lfi:+.2f}亿")
    L(f"\n{'='*90}")
    # V17.0(2026-08-15 C 方案): 全量 md 化——渲染层确定性转换(标题/分隔线/F10 边框表/对齐空格表→md)
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
        op = os.path.join(self.args.output, f"{sn}_{ts}.md")
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

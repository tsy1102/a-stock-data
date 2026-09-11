#!/usr/bin/env python3
"""
get_val_report.py — 23 策略全市场发现引擎
方法论驱动的 A 股选股脚本，从全市场发现可操作标的。
每策略精选 TOP 5，生成含具体数值推理的报告。

版本信息:
    V15.2  2026-07-28 - V15.2 性能优化：21 策略去重循环 get_pe_ttm_async，从 _snapshot dict O(1) 读；ths_hot_reason 失败降级；L1 缓存上限 5000→10000
    V15.1  2026-07-26 - V15.1 策略并发 100% 线程池 Worker 隔离：策略 20/21/22 恢复纯同步 def，解除主事件循环 20 分钟死锁挂起问题
    V15.0  2026-07-26 - 接入 CanonicalStockData 强类型数据合约，实施基于真实周期的 ZHB-First 离线优先路由
    V14.0  2026-07-22 - 文档同步：docstring 版本信息更新到 V14.0；is_workday() Bug 修复由 stock_common 上游提供
    V13.x  2026-07-22 - 受益于 stock_cache.py dataclass 透明序列化（脚本无改动）
    V12.6  2026-07-22 - 受益于字段路由简化（移除估值字段 HTTP fallback）
    V12.4  2026-07-22 - 抽象 BaseReportRunner 基类
    V9.5   2026-07-11 - 基础设施修复：aiohttp原生异步迁移、静默异常日志化（脚本本身无改动，受益于底层修复）
    V9.3.3 2026-07-11 - VERSION文件单一来源版本号管理
    V9.3.2 2026-07-09 - 基础设施修复：TDX K线假数据防护、SQLite WAL死锁修复、代理环境兼容（脚本本身无改动，受益于底层修复）
    V9.3   2026-07-07 - 盘前行情模式：9:30前使用上一交易日日K线数据；修复 _safe_float 对 pandas Series 的处理；删除报告标题硬编码版本号
    V9.2   2026-07-05 - 异常处理规范化；缓存交叉验证机制启用
    V9.1.1 2026-07-04 - 移除 deprecated F10 章节追加函数；F10 死代码精简
    V9.1 2026-07-04 - 版本号统一升级（F10 章节/附录集成在 ful/med/lng 报告中）
    V9.0 2026-07-02 - 舆情互动层（Layer 10）；上市日期 push2 fallback；valid_if 校验；_has_zero_price 拦截
    V8.9 2026-06-29 - 修复缺失导入(_load_settings/holder_change)；清理冗余快照逻辑；模块版本统一
    V8.7 2026-06-25 - 死代码清理：同步版替换为薄包装：并发数调整为3/策略18初筛Top20
    V8.5 2026-06-22 - 初始V8.5版本

V7.5 新增:
  - ThreadPoolExecutor 并行执行策略（目标: 7min -> 4-5min）
  - 策略07【政策驱动(含热度图谱)】（原 08+15 合并：政策关键词 + 同花顺 reason tags 量化热度）
  - 策略14【北向Top30】（东财机构持仓结构分析，高北向持仓+加仓标的）
  - 策略15【龙虎榜】（全市场龙虎榜扫描 + 游资席位识别 + 机构买卖评分）
  - 从 stock_common 导入统一龙虎榜函数 / 统一板块判断 / 涨停判断

Usage:
    python get_val_report.py                  # 全量 23 策略
    python get_val_report.py -o ./reports     # 指定输出目录
    python get_val_report.py --no-upload      # 跳过 GD 上传
"""

# V16.4.1: 强制 UTF-8 输出（下沉到代码自身——任何 agent/机器/直接运行均 UTF-8，
# 不再依赖 main.py 注入的 PYTHONIOENCODING 环境变量）
from stock_common.env_setup import ensure_utf8_stdio

ensure_utf8_stdio()

import time, os
from datetime import date, datetime, timedelta  # V16.1: 策略13 TTM 股息率需 timedelta
from typing import Any, Dict, Optional  # V16.4.1: 删 List 未使用

_KLINE_PRICE_CACHE: Dict[str, Dict] = {}  # V17.0: bypass 模式 .day 收盘价缓存

# V17.0.x(2026-09-10) P0 热启动会话缓存: 按 ZHB 数据日期缓存快照与腾讯批量行情, 同日
# 重跑 / main.py 批次(val→sht→med→lng)复用, 跳过网络拉取(原每次 3–7 分钟含腾讯批量 8s+)。
# 仅进程内有效(新进程必空); ZHB 日期不变则数据不变, 缓存恒有效。
_VAL_SNAPSHOT_CACHE: Dict[str, Any] = {}
_VAL_TENCENT_CACHE: Dict[str, Dict[str, Dict[str, Any]]] = {}
# 取数成本分桶(P2 并发): 网络/逐股K线/盘后datacenter 类限流到 3, 纯内存/ZHB 类放宽到 8。
_VAL_NET_HEAVY = {1, 3, 7, 8, 15, 16, 17, 19, 22, 25}

def _fast_day_close(code: str) -> Dict:
    """V17.0(2026-08-15): TDX 本机 .day 尾部快速读(零网络毫秒级).

    新版 .day 32B 记录: date<uint32> + open/high/low/close<int32×0.01元(分)> +
    amount<float32 元> + volume<int32 股> + reserved。返回 {price, open, high, low, date}。
    ⚠️ C1 终审修复(2026-08-15): 价格刻度 ÷1000→÷100(实测 600519 close=134199→1341.99)。
    """
    try:
        import os as _os
        import struct as _st

        _mkt = "bj" if code.startswith(("92", "8", "4", "43", "83", "87")) else ("sh" if code.startswith(("6", "9")) else "sz")  # H1 终审修复: 92 北交所先判(9 前缀会被沪市分支吃掉)
        _path = _os.path.join(r"C:\new_tdx64\vipdoc", _mkt, "lday", f"{_mkt}{code}.day")
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
        return {"price": _close, "open": _open, "high": _high, "low": _low, "date": _date}
    except Exception:
        return {}




from core.tdx_client import (tdx_get_weekly_bars,
                         tdx_get_board_list,
                         tdx_get_all_stocks)  # V16.4.1: 删 cleanup_tdx
# V17.0.26(2026-09-03) DEBT-009: 移除 _quick_request / JP_URL 导入。
#   二者唯一使用处已改用 sc_datasource.get_em_board_members 适配器（公理 A1 数据访问收口）。
#   保留无用的裸客户端 import 会诱导后人继续直连，故一并清理（UA 为无害常量，保留）。
from stock_common import (_safe_float, UA,
                           _load_settings, _load_strategy_config, get_holder_structure,
                           holder_change, is_limit_up, is_limit_down,
                           get_recent_dragon_tiger, get_dragon_tiger_board,
                           BaseReportRunner,  # V16.4.1: 删 _request_with_retry/common_parse_args
                           save_text_report,  # V17.0 S5: 写尾样板公共函数
                           get_tencent_quote,
                           baidu_kline_full as common_baidu_kline_full,
                           get_dividend_history as common_get_dividend_history,
                           get_market_status,
                           _debug_log,
                           cls_telegraph as _cls_telegraph,
                           get_eastmoney_global_news as _eastmoney_global_news,
                           get_zhb_market_snapshot, is_zhb_data_fresh,
                           get_zhb_data_date,
                           calc_mcap_yi as _calc_mcap_yi,
                           get_sina_financial_report, get_financial_report_with_fallback,
                           get_em_batch_quotes)  # V11.5
from core.data_provider import (get_market_snapshot_async,
                           get_turnover_pct_async,
                           get_main_net_buy)  # V16.1: 策略18 用同步版; V16.4.1: 删 async 版; V17.0: 内部=f137+f140 主力净
from stock_common.sc_network import _fallback_logger  # V17.2.x: 策略级超时降级纳入统一 fallback 审计
import asyncio
import inspect

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ═══════════════════════════════════════════════════
# 数据获取层
# ═══════════════════════════════════════════════════

# ─── 百度股市通 K线（返回全量行） ───

def baidu_kline_last(code: str) -> Dict[str, Any]:
    """V4: 最新K线+MA → tdx_client 适配器（本地计算MA5/10/20）"""
    keys, rows = common_baidu_kline_full(code, count=120)
    if not keys or not rows or not rows[-1]: return {}
    idx_map = {k: i for i, k in enumerate(keys)}
    ci = idx_map.get('close', -1)
    # 取最新一行
    last = rows[-1]
    res = {}
    for idx, key in enumerate(keys):
        if idx < len(last): res[key] = last[idx]
    # V4 fix: TDX 数据无 MA 字段，本地计算
    if 'ma5avgprice' not in res and ci >= 0 and len(rows) >= 20:
        closes = [_safe_float(r[ci]) for r in rows if len(r) > ci]
        closes = [c for c in closes if c > 0]
        res['ma5avgprice'] = str(round(_sma(closes, 5) or 0, 2))
        res['ma10avgprice'] = str(round(_sma(closes, 10) or 0, 2))
        res['ma20avgprice'] = str(round(_sma(closes, 20) or 0, 2))
    return res


def _sma(data: list, n: int) -> Optional[float]:
    """简单移动平均（H2: 原 3 处重复的 sma/_sma 嵌套函数提取为模块级）。"""
    if len(data) < n:
        return None
    return sum(data[-n:]) / n


# ─── 周线聚合（日K线 → 周K线 + MA计算） — 策略02使用 ───

def compute_weekly_ma(code):
    """V4: 周线MA → 优先 TDX 周K线直取，不可用时日线聚合 fallback"""
    # 优先：TDX 周K线
    keys, rows = tdx_get_weekly_bars(code, count=100)
    if keys and rows and len(rows) >= 10:
        idx_map = {k: i for i, k in enumerate(keys)}
        ci = idx_map.get('close', -1)
        if ci >= 0:
            closes = [_safe_float(r[ci]) for r in rows if len(r) > ci]
            closes = [c for c in closes if c > 0]
            if len(closes) >= 10:
                ma5 = _sma(closes, 5)
                ma10 = _sma(closes, 10)
                ma20 = _sma(closes, 20)
                ma30 = _sma(closes, 30)
                last_close = closes[-1] if closes else 0
                spreads = [v for v in [ma5, ma10, ma20, ma30] if v is not None and v > 0]
                cluster_spread = ((max(spreads) - min(spreads)) / min(spreads) * 100) if len(spreads) >= 4 and min(spreads) > 0 else None
                last_week_date = rows[-1][0] if rows and len(rows[-1]) > 0 else ""
                return {
                    "ma5": ma5, "ma10": ma10, "ma20": ma20, "ma30": ma30,
                    "last_close": last_close, "cluster_spread": cluster_spread,
                    "week_count": len(rows), "last_week_date": last_week_date,
                }

    # Fallback: 日K线手动聚合为周K线（TDX 不可用时）
    keys, rows = common_baidu_kline_full(code, count=600)
    if not keys or not rows or len(rows) < 50:
        return {}
    idx_map = {k: i for i, k in enumerate(keys)}
    ci = idx_map.get('close', -1)
    ti = idx_map.get('time', 0)
    if ci < 0:
        return {}

    # 按 ISO 周聚合
    weeks = {}
    for row in rows:
        if len(row) <= max(ci, ti): continue
        date_str = row[ti]
        if len(date_str) < 10: continue
        try:
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        except ValueError:
            continue
        week_key = dt.strftime("%G-W%V")
        close = _safe_float(row[ci])
        if week_key not in weeks:
            weeks[week_key] = {"close": close, "date": date_str[:10]}
        else:
            weeks[week_key] = {"close": close, "date": date_str[:10]}

    week_closes = [(k, v["close"], v["date"]) for k, v in sorted(weeks.items())]
    if len(week_closes) < 10: return {}

    closes = [c for _, c, _ in week_closes]

    ma5 = _sma(closes, 5)
    ma10 = _sma(closes, 10)
    ma20 = _sma(closes, 20)
    ma30 = _sma(closes, 30)
    last_close = closes[-1] if closes else 0
    spreads = [v for v in [ma5, ma10, ma20, ma30] if v is not None and v > 0]
    cluster_spread = ((max(spreads) - min(spreads)) / min(spreads) * 100) if len(spreads) >= 4 and min(spreads) > 0 else None
    return {
        "ma5": ma5, "ma10": ma10, "ma20": ma20, "ma30": ma30,
        "last_close": last_close, "cluster_spread": cluster_spread,
        "week_count": len(week_closes),
        "last_week_date": week_closes[-1][2] if week_closes else "",
    }


# ─── 同花顺热点 ───

def ths_hot_reason(date_str=None):
    """同花顺当日强势股归因 — 返回 list[dict]

    V17.0 S4: 统一走 sc_datasource.get_ths_hot_raw（三版收敛, 原本地实现删除）。
    """
    from stock_common.sc_datasource import get_ths_hot_raw

    if date_str is None:
        date_str = date.today().strftime("%Y-%m-%d")
    return get_ths_hot_raw(date_str)


# ─── 行业板块排名 ───

def industry_comparison(top_n=20):
    """V17.2.x(2026-09-10): 已下沉至 `stock_common.sc_datasource.get_industry_ranking`，此处仅薄转发。

    保留本名是为兼容既有调用点；实现见共享层（val/lng 原两份近乎重复的实现已合并）。
    返回 list[dict]（ZHB 行业榜行 或 TDX board_list 板块）。
    """
    from stock_common.sc_datasource import get_industry_ranking

    return get_industry_ranking(top_n, "val")


# ─── 新闻源 ───

def cls_telegraph(page_size=50):
    """财联社电报（全市场实时快讯）— 引用 sc_datasource 统一实现"""
    return _cls_telegraph(page_size)

def eastmoney_global_news(page_size=50):
    """东财全球财经资讯（7x24 滚动）— 引用 sc_datasource 统一实现"""
    return _eastmoney_global_news(page_size)

# ─── 股东户数变化 ───

def holder_num_change(code, page_size=5):
    """V7.5: 股东户数变化 → 东财优先 + 内存缓存"""
    return holder_change(code)


# ─── 模拟PE百分位 — 策略05使用 ───

def estimate_pe_percentile(code, price, total_shares):
    """
    基于新浪12期财报 + 历史日K线，估算近3年模拟PE百分位。
    返回: {percentile, pe_min, pe_max, pe_current, quarters}

    V16.1 修复：
      1. 财报按报告日排序（旧→新）后再拆季度——原逻辑假设 profits 旧→新，
         但新浪返回最新在前，直接相减会把所有季度归零
      2. 亏损季度不再截断为 0（保留负值，真实反映 TTM 利润）
      3. K线锚点用"报告期+60天"近似披露日（原直接用报告期 → 轻微前视）
    """
    fin = get_financial_report_with_fallback(code, num_periods=12)  # B: 新浪为主源，缺失时 fuyao 利润表兜底
    if len(fin) < 4:
        return None

    # 按报告日升序排序（旧→新），确保季度拆解方向正确
    fin_sorted = sorted(
        [f for f in fin if f.get("报告日")],
        key=lambda x: x["报告日"],
    )
    if len(fin_sorted) < 4:
        return None

    profits = []
    for f in fin_sorted:
        try: p = float(f["净利润"])
        except (ValueError, TypeError, KeyError): p = 0
        profits.append(p)

    if total_shares <= 0 or all(p == 0 for p in profits):
        return None

    # 还原为单季度（新浪财报是累计值，逐季拆解；亏损季度保留负值）
    # V16.2.14 修复: 跨年边界 —— 每年 Q1(03-31) 的累计值 < 去年 Q4 累计，直接相减得大负数
    # （实测 2024Q1=384亿 - 2023Q4累计=1480亿 = -1096亿 → TTM/PE 全错乱，PE 显示千万倍级）
    sq_profits = []
    _prev_year = None
    for i, _f in enumerate(fin_sorted):
        _yr = str(_f.get("报告日", ""))[:4]
        if i == 0 or _yr != _prev_year:
            sq_profits.append(profits[i])  # 首条 / 每年 Q1：累计值即当季值
        else:
            sq_profits.append(profits[i] - profits[i - 1])
        _prev_year = _yr

    ttm_eps_list = []
    ttm_dates = []
    for i in range(len(sq_profits) - 3):
        ttm_profit = sum(sq_profits[i:i + 4])
        eps = ttm_profit / total_shares
        if eps > 0:
            ttm_eps_list.append(eps)
            ttm_dates.append(fin_sorted[i + 3]["报告日"])

    if not ttm_eps_list:
        return None

    keys, rows = _fast_kline(code)
    if not rows:
        return None

    idx_close = -1
    for i, k in enumerate(keys):
        if k in ("close", "close_price"):
            idx_close = i
            break
    if idx_close < 0: return None

    historical_pes = []
    for i, (eps, dt_str) in enumerate(zip(ttm_eps_list, ttm_dates)):
        # V16.1: 披露日近似 = 报告期 + 60 天（A股年报/季报披露窗口）
        try:
            _anchor = (datetime.strptime(dt_str, "%Y-%m-%d") + timedelta(days=60)).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            _anchor = dt_str
        for row in reversed(rows):
            if len(row) <= idx_close: continue
            row_date = row[0] if len(row) > 0 else ""
            if row_date[:10] <= _anchor:
                close_price = _safe_float(row[idx_close])
                if close_price > 0:
                    historical_pes.append(close_price / eps)
                break

    if len(historical_pes) < 2:
        return None

    current_pe = price / ttm_eps_list[-1] if ttm_eps_list[-1] > 0 else 0
    if current_pe <= 0:
        return None

    pe_min = min(historical_pes)
    pe_max = max(historical_pes)
    if pe_max == pe_min:
        percentile = 50.0
    else:
        percentile = (current_pe - pe_min) / (pe_max - pe_min) * 100

    return {
        "percentile": percentile,
        "pe_current": current_pe,
        "pe_min": pe_min,
        "pe_max": pe_max,
        "quarters": len(ttm_eps_list),
    }


# ═══════════════════════════════════════════════════
# 全市场股票池构建 + 流动性筛选
# ═══════════════════════════════════════════════════

# ─── V9.6 阶段二-2.4: tdxstat 批量初筛 ───

def _tdxstat_prescreen(stocks):
    """V9.6: 使用 zhb.tdxstat 对全市场批量初筛，标注数据并过滤停牌股。

    作用：
        1. 从 zhb.zip 的 tdxstat.cfg 一次性拿到全市场统计快照（零 HTTP）
        2. 为每只股票标注 pe_ttm/change_5d..60d/high_52w/low_52w 等字段
        3. 过滤掉 tdxstat 中 volume=0 的停牌股，减少后续策略的无效扫描

    Args:
        stocks: tdx_get_all_stocks() 返回的全市场列表

    Returns:
        tuple (screened_stocks, zhb_date_str, is_fresh)
        - zhb 不可用时，返回原列表 + 空日期 + False，保持向后兼容
    """
    if not stocks:
        return stocks, "", False

    try:
        # V17.0.4(2026-08-19): 改用合并快照(tdxstat+tdxstat2)——原 get_zhb_market_snapshot
        # 仅 tdxstat, 无 high_52w/low_52w → 策略16(52周低位)恒 0 命中(实测 0/7991)
        from core.zhb_client import full_market_snapshot

        snapshot = full_market_snapshot()
    except Exception as _e:
        _debug_log(f"val tdxstat_prescreen: snapshot error: {_e}")
        return stocks, "", False

    if not snapshot:
        _debug_log("val tdxstat_prescreen: zhb snapshot empty, skip")
        return stocks, "", False

    zhb_date = ""
    try:
        zhb_date = get_zhb_data_date() or ""
    except Exception:
        pass

    fresh = is_zhb_data_fresh(max_delay_days=3)

    # 标注 + 过滤
    screened = []
    excluded = 0
    for s in stocks:
        code = s.get("code", "")
        stat = snapshot.get(code)
        if stat is None:
            # tdxstat 中没有的股票（如新股），保留但不标注
            screened.append(s)
            continue
        # V16.0: ZHB 不再提供 volume 字段（Col[24] 误映射已移除）。
        # 原"volume=0 过滤停牌股"逻辑失效（恒 None），停牌股由后续策略行情获取自然排除。
        # 标注字段（不覆盖已有字段）
        for k, v in stat.items():
            if k not in ("market", "code", "date"):
                if k not in s:
                    s[k] = v
        screened.append(s)

    if excluded > 0:
        print(f"  ⚡ tdxstat初筛: 过滤{excluded}只停牌股，{len(screened)}/{len(stocks)}只进入策略扫描", flush=True)
    else:
        print(f"  ⚡ tdxstat初筛: {len(screened)}/{len(stocks)}只（zhb日期:{zhb_date or '未知'}）", flush=True)

    return screened, zhb_date, fresh


# ═══════════════════════════════════════════════════
# 23 个策略引擎（扫描函数）
# ═══════════════════════════════════════════════════

# V15.1: A 股代码前缀白名单（沪深主板/创业板/科创板/北交所），其余（ETF/LOF/可转债）过滤掉
# V17.0 S3: 统一收敛到 stock_common.sc_utils（is_a_stock/A_STOCK_PREFIXES 单一来源）


def _is_a_stock(code: str) -> bool:
    """V17.2.x(2026-09-10): 直接转调 sc_utils.is_a_stock（原本地前缀表早已收敛）。

    与 mak 的同名包装曾构成两份重复实现，现两者均为同构单行转发，保留仅为调用点兼容。
    """
    from stock_common.sc_utils import is_a_stock

    return is_a_stock(code)

def _zhb_weekly_eligible(stock: dict) -> bool:
    """V14.3 P1: 周线多头策略的 ZHB 前置过滤。

    过滤逻辑：
      1) 基础过滤：必须有 amount（市值活跃）+ mcap_yi（市值 >= 50 亿）
      2) 趋势过滤：change_20d > 0 或 streak_days >= 1（至少有短期上行动量）
      3) 估值过滤：pe_ttm > 0（非亏损股）
    ZHB 数据缺失时放行（保证不漏选）。
    """
    if not stock:
        return True
    # 1. 基础过滤
    if _safe_float(stock.get("mcap_yi", 0)) < 50:
        return False
    if _safe_float(stock.get("amount", 0)) <= 0:
        return False
    # 2. 趋势过滤（任一满足即可）
    change_20d = _safe_float(stock.get("change_20d", 0))
    change_60d = _safe_float(stock.get("change_60d", 0))
    streak = _safe_int(stock.get("streak_days", 0))
    if change_20d <= -10 and change_60d <= -20 and streak < 1:
        return False  # 趋势太弱，不值得查 K 线
    # 3. 估值过滤
    pe = _safe_float(stock.get("pe_ttm", 0))
    if pe != 0 and pe < 0:
        return False  # 亏损股跳过
    return True


def _zhb_pattern_eligible(stock: dict, pattern: str = "double_bottom") -> bool:
    """V14.3 P1: 形态类策略的 ZHB 前置过滤（double_bottom / three_soldiers）。

    形态策略对趋势敏感，前置过滤更严格：
      1) W底（double_bottom）：需要 60 日内大跌后反弹，要求 change_60d < -5 且 change_20d > 0
      2) 红三兵（three_soldiers）：需要连涨态势，要求 streak_days >= 2 或 change_5d > 3
    ZHB 数据缺失时放行。
    """
    if not stock:
        return True
    if _safe_float(stock.get("mcap_yi", 0)) < 50:
        return False
    if _safe_float(stock.get("amount", 0)) <= 0:
        return False
    change_5d = _safe_float(stock.get("change_5d", 0))
    change_20d = _safe_float(stock.get("change_20d", 0))
    change_60d = _safe_float(stock.get("change_60d", 0))
    streak = _safe_int(stock.get("streak_days", 0))
    if pattern == "double_bottom":
        # W底：60 日大跌 + 20 日反弹
        if change_60d > 5:
            return False
        if change_20d < -5:
            return False
    elif pattern == "three_soldiers":
        # 红三兵：连涨
        if streak < 2 and change_5d < 2:
            return False
    return True


def _top10_sorted(candidates, key_func, reverse=True):
    """从候选列表中取 TOP10，按 key_func 排序"""
    candidates.sort(key=key_func, reverse=reverse)
    return candidates[:10]


# ─── V15.5.8: 快速 K 线（TDX 优先，百度 fallback）───

def _fast_kline(code: str, count: int = 800):
    """V15.5.8: K 线获取——优先 TDX(mootdx+磁盘缓存, 跨进程持久, 缓存命中零网络),
    失败 fallback 百度。

    V17.0.4(2026-08-19): 修复注释与代码不符——原实现只调 common_baidu_kline_full(百度 HTTP,
    每只 0.9s 冷+网络波动) → 形态类策略(05/06/12)命中随网络波动(凌晨全 0)。
    TDX 磁盘缓存(sc_kline_cache)命中后稳定且零网络。
    """
    try:
        from core.tdx_client import tdx_get_security_bars

        _k, _r = tdx_get_security_bars(code, count)
        if _r and len(_r) >= 65:
            return _k, _r
    except Exception as _e:
        _debug_log(f"val _fast_kline tdx ({code}): {_e}")
    try:
        _k, _r = common_baidu_kline_full(code, count=count)
        if _r and len(_r) >= 65:
            # V17.0.10c(2026-08-28): 百度 fallback 结果也落盘, 使后续运行命中磁盘缓存(零网络/零
            # TDX 锁), 避免 TDX 常年 <65 行的标的每次运行都重复 0.9~15s 百度请求(总时长"越来越长"根因)。
            # 落盘键与 tdx_get_security_bars 读取键一致("D", code, count), 下次运行 tdx 入口直接命中。
            try:
                from stock_common.sc_kline_cache import set_cached_kline

                set_cached_kline("D", code, count, (_k, _r))
            except Exception:
                pass
            return _k, _r
    except Exception as _e:
        _debug_log(f"val _fast_kline baidu ({code}): {_e}")
    return common_baidu_kline_full(code)


# ─── 策略01: 龙回头战法 ───

async def strategy_01_longhuitou(hot_pool, today_str):
    _sc = _load_strategy_config()
    _ma_dev_mid = _sc.get("technical", {}).get("ma_deviation_mid", 3.0)
    _turnover_cap = _sc.get("strategy", {}).get("turnover_cap_pct", 8.0)
    _zhangfu_min = _sc.get("strategy", {}).get("zhangfu_min", 5.0)
    result = []
    for stock in hot_pool:
        code = stock.get("code", "")
        name = stock.get("name", "")
        zhangfu = _safe_float(stock.get("zhangfu", stock.get("涨幅%", 0)))
        if zhangfu < _zhangfu_min:
            continue
        kline = baidu_kline_last(code)
        if not kline: continue
        try:
            price = _safe_float(kline.get("close", kline.get("close_price", 0)))
            ma10 = _safe_float(kline.get("ma10avgprice") or kline.get("ma10", 0))
        except (ValueError, IndexError):
            continue
        if price <= 0 or ma10 <= 0: continue
        ma10_bias = (price - ma10) / ma10 * 100
        if abs(ma10_bias) > _ma_dev_mid: continue
        # V17.0.15: 换手率取值次序 = 池内已有实时字段(腾讯批量预加载, V15.5.9) > ZHB 查询。
        # ⚠️ 原实现 `await get_turnover_pct_async(code) or 0` 存在静默缺陷：
        #   get_turnover_pct 只查 ZHB 且**无实时兜底**，交易日 09:30-24:00（最常运行时段）
        #   _should_use_zhb_for_realtime() 恒 False → 返回 None → 被 `or 0` 变成 0，于是
        #     ①"换手率仅 0.0%，缩量企稳"是**由数据缺失伪造的利好结论**；
        #     ②0 ≤ _turnover_cap 故不会被过滤；③(8-0)*0.1 反而拿到**最高**加分。
        #   三者叠加 → 盘中运行时该策略结论系统性虚高（缺失值被当成"极度缩量"这一极值）。
        turnover = _safe_float(stock.get("turnover_pct", 0))
        if turnover <= 0:
            try:
                turnover = await get_turnover_pct_async(code) or 0
            except Exception:
                turnover = 0
        if turnover > _turnover_cap: continue
        if turnover > 0:
            _to_txt = f"换手率仅{turnover:.1f}%，缩量企稳，筹码沉淀充分"
            _to_score = (8 - turnover) * 0.1
        else:
            # 取不到换手率 → 该判据**不参与**：既不伪造利好，也不因此误剔除标的
            _to_txt = "换手率数据缺失(未参与缩量判据)"
            _to_score = 0.0
        reason = (
            f"前期强势股(涨幅{zhangfu:.1f}%)，"
            f"当前回踩MA10({ma10:.2f}元)，乖离率{ma10_bias:+.2f}%，"
            f"{_to_txt}"
        )
        result.append({"code": code, "name": name, "reason": reason,
                       "score": -abs(ma10_bias) + _to_score})
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略02: 周线级别多均线多头排列（含金叉共振, V17.0.x 合并策略07） ───

def strategy_02_weekly_ma(stocks, top_n=None):
    _sc = _load_strategy_config()
    if top_n is None:
        top_n = _sc.get("strategy", {}).get("top_n_cap", 200)
    _cluster_cap = _sc.get("strategy", {}).get("cluster_spread_cap", 5.0)
    # V16.3 O27: 预筛全市场（ZHB 内存零成本）→ 趋势强度排序取 top_n 逐股确认。
    # 原 mcap 排序截断会漏掉小市值强趋势股；趋势优先覆盖最强信号
    _pool = [s for s in stocks if _zhb_weekly_eligible(s)]
    candidates = sorted(
        _pool,
        key=lambda x: (
            _safe_float(x.get("change_20d", 0)),
            _safe_float(x.get("streak_days", 0)),
        ),
        reverse=True,
    )[:top_n]
    result = []
    for s in candidates:
        code = s["code"]
        # V14.3 P1: ZHB 前置过滤（避免无意义 K 线网络请求）
        # ZHB 有完整周线/形态信息时直接命中，否则跳过网络请求
        if not _zhb_weekly_eligible(s):
            continue
        w = compute_weekly_ma(code)
        if not w or w.get("week_count", 0) < 25: continue
        if any(v is None or v <= 0 for v in [w.get("ma5"), w.get("ma10"), w.get("ma20"), w.get("ma30")]): continue
        if not (w.get("ma5", 0) > w.get("ma10", 0) > w.get("ma20", 0) > w.get("ma30", 0)): continue
        if w.get("cluster_spread") is None or w.get("cluster_spread") >= _cluster_cap: continue
        if w.get("last_close", 0) < w.get("ma5", 0): continue
        reason = (
            f"周线MA5/10/20/30在{w.get('last_close', 0):.2f}元附近极度聚合"
            f"(离散度{w.get('cluster_spread', 0):.2f}%)，"
            f"本周{w.get('last_week_date', '')}放量突破MA5，"
            "确认大级别趋势反转信号"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": -w.get("cluster_spread", 0)})
    return _top10_sorted(result, lambda x: x["score"])


def _kline_indices(keys):
    """提取K线数据的关键字段索引"""
    idx = {}
    for i, k in enumerate(keys):
        if k in ("close", "close_price"): idx["close"] = i
        elif k == "volume": idx["vol"] = i
        elif k == "open": idx["open"] = i
        elif k in ("high", "high_price"): idx["high"] = i
        elif k in ("low", "low_price"): idx["low"] = i
    return idx

# ─── 策略03: 量价齐升 ───

def strategy_03_volume_breakout(hot_pool):
    _sc = _load_strategy_config()
    _box_factor = _sc.get("strategy", {}).get("box_break_factor", 1.01)
    _vol_ratio_cap = _sc.get("strategy", {}).get("vol_ratio_cap", 2.5)
    result = []
    for stock in hot_pool:
        code = stock.get("code", "")
        name = stock.get("name", "")
        keys, rows = common_baidu_kline_full(code, count=100)
        if len(rows) < 65: continue
        idx_close = -1
        idx_vol = -1
        for i, k in enumerate(keys):
            if k in ("close", "close_price"): idx_close = i
            if k == "volume": idx_vol = i
        if idx_close < 0: continue
        closes = []
        volumes = []
        for row in rows:
            if len(row) <= max(idx_close, idx_vol) if idx_vol >= 0 else len(row) <= idx_close: continue
            c = _safe_float(row[idx_close])
            closes.append(c)
            if idx_vol >= 0:
                v = _safe_float(row[idx_vol])
                volumes.append(v)
        if len(closes) < 65: continue
        # V16.1: 箱体上沿用"前60根"（排除现价）— 原 max(closes[-60:]) 含现价，
        # 导致 current_price < box_top*1.01 恒真，策略永不命中
        recent_60 = closes[-61:-1]
        box_top = max(recent_60)
        current_price = closes[-1]
        if current_price < box_top * _box_factor: continue
        if len(volumes) >= 11:
            avg_vol_10 = sum(volumes[-11:-1]) / 10
            today_vol = volumes[-1]
            vol_ratio = today_vol / avg_vol_10 if avg_vol_10 > 0 else 0
            if vol_ratio < _vol_ratio_cap: continue
        else:
            continue
        reason = (
            f"突破60日箱体上沿({box_top:.2f}元)，"
            f"现价{current_price:.2f}元，"
            f"成交量放大至{vol_ratio:.1f}倍于10日均量，"
            "阻力位已扫清，上行空间打开"
        )
        result.append({"code": code, "name": name, "reason": reason,
                       "score": vol_ratio})
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略04: 核心资产打折买入 ───

async def strategy_04_core_discount(stocks):
    _sc = _load_strategy_config()
    _pe_high = _sc.get("valuation", {}).get("pe_high", 50.0)
    _pb_high = _sc.get("valuation", {}).get("pb_high", 8.0)
    _pe_percentile_warn = _sc.get("strategy", {}).get("pe_percentile_warn", 15.0)
    _mcap_min = _sc.get("strategy", {}).get("mcap_big_cap_min", 100.0)
    _top_n = _sc.get("strategy", {}).get("top_n_cap", 200)
    big_caps = [s for s in stocks if s.get("mcap_yi", 0) >= _mcap_min]
    if not big_caps: return []
    big_caps = sorted(big_caps, key=lambda x: x.get("mcap_yi", 0), reverse=True)[:_top_n]
    result = []
    # V15.1: 统一接入 get_canonical_stock_data 强类型合约（替代旧的 get_stock_composite_async）
    from core.data_provider import get_canonical_stock_data
    for s in big_caps:
        code = s["code"]
        try:
            # 同步函数走 to_thread，避免阻塞 asyncio 事件循环
            cdata = await asyncio.to_thread(get_canonical_stock_data, code)
        except Exception:
            continue
        pe = _safe_float(cdata.pe_ttm)
        if pe <= 0 or pe > _pe_high: continue
        pb = _safe_float(cdata.pb)  # V16.3.7: 口径统一——PB 一律走 canonical（腾讯/push2 除息口径）
        if pb > _pb_high: continue
        mcap = _safe_float(cdata.mcap_yi)
        price = _safe_float(cdata.price)
        if mcap <= 0 or price <= 0: continue
        total_shares = int(mcap * 1e8 / price)
        # V16.4.1: PE 分位用实时价(cdata.price)而非 ZHB T-1 价——原混用导致盘中/盘后分位偏差
        pe_data = estimate_pe_percentile(code, price, total_shares)
        if pe_data is None: continue
        pe_percentile = _safe_float(pe_data.get("percentile", 100))
        if pe_percentile > _pe_percentile_warn: continue
        reason = (
            f"当前PE({_safe_float(pe_data.get('pe_current', 0)):.1f}x)处于近3年模拟PE区间低位"
            f"(最低{_safe_float(pe_data.get('pe_min', 0)):.1f}x~最高{_safe_float(pe_data.get('pe_max', 0)):.1f}x)，"
            f"约{pe_percentile:.0f}%分位（基于{pe_data.get('quarters', 0)}期TTM数据估算），"
            "属于非理性折价区间"
        )
        result.append({"code": code, "name": s.get("name", "") or cdata.name, "reason": reason,
                       "score": -pe_percentile})
        if len(result) >= 5:
            break
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略05: W底形态 ───

def strategy_05_double_bottom(stocks, top_n=None):
    _sc = _load_strategy_config()
    _wbottom_depth = _sc.get("strategy", {}).get("wbottom_depth_cap", 5.0)
    if top_n is None:
        top_n = _sc.get("strategy", {}).get("top_n_cap", 200)
    _box_factor = _sc.get("strategy", {}).get("box_break_factor", 1.01)
    _vol_inc_factor = _sc.get("strategy", {}).get("volume_increase_factor", 1.2)
    # V16.3 O27: 预筛全市场（ZHB 内存）→ 趋势强度排序取 top_n 逐股确认（同策略02）
    _pool = [s for s in stocks if _zhb_pattern_eligible(s, pattern="double_bottom")]
    candidates = sorted(
        _pool,
        key=lambda x: (
            _safe_float(x.get("change_20d", 0)),
            _safe_float(x.get("streak_days", 0)),
        ),
        reverse=True,
    )[:top_n]
    result = []
    for s in candidates:
        code = s["code"]
        # V14.3 P1: ZHB 前置过滤（避免 W底形态 K 线网络请求）
        if not _zhb_pattern_eligible(s, pattern="double_bottom"):
            continue
        keys, rows = _fast_kline(code)
        if len(rows) < 100: continue
        idx_close = -1
        idx_vol = -1
        for i, k in enumerate(keys):
            if k in ("close", "close_price"): idx_close = i
            if k == "volume": idx_vol = i
        if idx_close < 0: continue
        closes = [_safe_float(r[idx_close]) for r in rows[-100:] if len(r) > idx_close]
        if len(closes) < 60: continue
        recent_60 = closes[-60:]
        min_idx = recent_60.index(min(recent_60))
        first_third = recent_60[:len(recent_60)//2]
        if not first_third: continue
        second_low = min(first_third)
        second_idx = first_third.index(second_low)
        if abs(min_idx - second_idx) < 10: continue
        low_diff = abs(recent_60[min_idx] - second_low) / max(recent_60[min_idx], second_low) * 100
        if low_diff > _wbottom_depth: continue
        neck_start = min(second_idx, min_idx)
        neck_end = max(second_idx, min_idx)
        neckline = max(recent_60[neck_start:neck_end+1])
        current_price = closes[-1]
        if current_price < neckline * _box_factor: continue
        if idx_vol >= 0:
            vols = [_safe_float(r[idx_vol]) for r in rows[-10:] if len(r) > idx_vol]
            if len(vols) >= 5:
                # 成交量确认：使用5日均量对比，突破需放量
                avg_vol_5 = sum(vols[-5:]) / min(5, len(vols))
                vol_increasing = vols[-1] > avg_vol_5 * _vol_inc_factor
            else:
                vol_increasing = True
        else:
            vol_increasing = True
        reason = (
            f"W底形态确认：两个低点分别{second_low:.2f}和{recent_60[min_idx]:.2f}元"
            f"（偏离{low_diff:.1f}%），"
            f"突破颈线{neckline:.2f}元至{current_price:.2f}元"
            + ("，成交量放大确认突破有效" if vol_increasing else "")
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": current_price / neckline if neckline > 0 else 0})
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略06: 红三兵 ───

def strategy_06_three_soldiers(stocks, top_n=500):
    # V16.3 O27: 预筛全市场（ZHB 内存）→ 趋势强度排序取 top_n 逐股确认（同策略02/05）
    _pool = [s for s in stocks if _zhb_pattern_eligible(s, pattern="three_soldiers")]
    candidates = sorted(
        _pool,
        key=lambda x: (
            _safe_float(x.get("change_20d", 0)),
            _safe_float(x.get("streak_days", 0)),
        ),
        reverse=True,
    )[:top_n]
    result = []
    for s in candidates:
        code = s["code"]
        # V14.3 P1: ZHB 前置过滤（避免红三兵 K 线网络请求）
        if not _zhb_pattern_eligible(s, pattern="three_soldiers"):
            continue
        keys, rows = _fast_kline(code)
        if len(rows) < 10: continue
        idx_open = -1; idx_close = -1; idx_vol = -1
        for i, k in enumerate(keys):
            if k in ("close", "close_price"): idx_close = i
            if k == "open": idx_open = i
            if k == "volume": idx_vol = i
        if idx_close < 0 or idx_open < 0: continue
        last3 = rows[-3:]
        if len(last3) < 3: continue
        closes = [_safe_float(r[idx_close]) for r in last3]
        opens = [_safe_float(r[idx_open]) for r in last3]
        vols = [_safe_float(r[idx_vol]) for r in last3] if idx_vol >= 0 else [0, 0, 0]
        if not all(c > o for c, o in zip(closes, opens)): continue
        if not (closes[0] < closes[1] < closes[2]): continue
        if idx_vol >= 0 and vols[0] > 0 and vols[1] > 0 and vols[2] > 0:
            if not (vols[0] < vols[1] < vols[2]): continue
        reason = (
            f"底部红三兵形态确认：连续三天收阳（{closes[0]:.2f}→{closes[1]:.2f}→{closes[2]:.2f}元），"
            "成交量阶梯放大，低位建仓信号明确"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": closes[2] / closes[0]})
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略07: 政策驱动流（含政策热度图谱, V7.5: 同花顺 reason tags + 新闻 NLP; V17.0.x 合并策略15） ───

async def strategy_07_policy_driven(stocks, hot_pool=None):
    _cfg = _load_settings()
    policy_keywords = _cfg.get("policy_keywords", ["政策", "支持", "资金", "规划", "印发", "发布", "推动", "鼓励",
                       "十四五", "补贴", "减税", "利好", "振兴", "基建", "消费", "科技"])

    # 优先：从同花顺热点 reason tags 中匹配政策驱动标的
    if hot_pool:
        _ths_result = []
        for h in hot_pool:
            tag = h.get("reason_tag", "")
            h_code = h.get("code", "")
            if any(kw in tag for kw in policy_keywords):
                _s = next((s for s in (stocks or []) if s.get("code", "") == h_code), None)
                if _s and 5 <= _s.get("mcap_yi", 0) <= 50:
                    # V15.2: 从 _snapshot dict O(1) 读 pe_ttm，避免循环 get_pe_ttm_async 触发 5743 次 zhb_data 缓存
                    pe_ttm = _safe_float(_s.get("pe_ttm", 0))
                    if pe_ttm > 0:
                        _ths_result.append({
                            "code": h_code, "name": h.get("name", ""),
                            "reason": f"同花顺题材归因: {tag[:80]}，市值{_s.get('mcap_yi',0):.1f}亿",
                            "score": h.get("zhangfu", 0),
                        })
        if len(_ths_result) >= 3:
            return _top10_sorted(_ths_result, lambda x: x["score"])

    # Fallback: 新闻 NLP 关键词匹配
    news_list = await asyncio.to_thread(cls_telegraph, 30)
    if not news_list:
        news_list = eastmoney_global_news(30)
    if not news_list: return []
    all_text = " ".join([n.get("title", "") + " " + n.get("content", "") for n in news_list])
    found_policy = [kw for kw in policy_keywords if kw in all_text]
    if len(found_policy) < 3:
        return []
    candidates = [s for s in (stocks or []) if 5 <= s.get("mcap_yi", 0) <= 50]
    if not candidates: return []
    result = []
    # V15.1: 统一接入 get_canonical_stock_data 强类型合约（替代旧的 get_stock_composite_async）
    from core.data_provider import get_canonical_stock_data
    for s in candidates[:200]:
        code = s["code"]
        # V16.4.0: 快照 O(1)——原逐股 canonical（200×2.5s≈500s）改为快照 pe_ttm（ZHB 已有）
        pe_ttm = _safe_float(s.get("pe_ttm", 0))
        if not pe_ttm > 0: continue
        mcap_yi = _safe_float(s.get("mcap_yi", 0))
        reason = (
            f"近期新闻出现政策关键词: {", ".join(found_policy[:3])}，"
            f"市值{mcap_yi:.1f}亿（小盘对政策更敏感），"
            f"PE={pe_ttm:.1f}x（低估后备）"
        )
        result.append({"code": code, "name": s.get("name", "") or "", "reason": reason,
                       "score": -pe_ttm})
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略08: 日历效应法 ───

def strategy_08_calendar_rotation():
    month = date.today().month
    _cfg = _load_settings()
    _raw = _cfg.get("season_map", {})
    season_map = {int(k): v for k, v in _raw.items()}  # YAML 键转 int
    target_industries = season_map.get(month, ["银行", "食品饮料", "医药"])
    ind_data = industry_comparison(30)
    if not ind_data: return []
    matched = []
    for ind in ind_data:
        if any(t in ind.get("name", "") for t in target_industries):
            matched.append(ind)
    if not matched: return []
    result = []
    seen_codes = set()
    for ind in matched:
        # V16.4.1: leader 字段可能只有名称无代码(get_industry_rank_from_zhb 返回 leader_name,
        # 无 leader 代码)——名称不能当代码用(2026-08-12 实测报告出现"昀冢科技 (昀冢科技)")。
        # 无 6 位代码的 leader 直接走下方成分股补全路径。
        leader_code = ind.get("leader") or ""
        if not (str(leader_code).isdigit() and len(str(leader_code)) == 6):
            leader_code = ""
        if leader_code and leader_code in seen_codes:
            continue
        if leader_code:
            seen_codes.add(leader_code)
            q = get_tencent_quote(leader_code)
            reason = (
                f"当前{month}月，日历效应指向{', '.join(target_industries)}板块，"
                f"行业'{ind.get('name', '')}'涨幅{ind.get('change_pct', 0)}%，为板块领涨股"
            )
            result.append({"code": leader_code, "name": q.get("name", ""),
                           "reason": reason, "score": _safe_float(ind.get("change_pct", 0))})
    if len(result) < 5:
        for ind in matched:
            if len(result) >= 5: break
            ind_code = ind.get("code", "")
            if not ind_code: continue
            try:
                # V17.0.26(2026-09-03) DEBT-009: 改用 sc_datasource 适配器 get_em_board_members（公理 A1 数据访问收口）。
                #   原实现两处缺陷：
                #   ① 生产脚本直连裸 _quick_request(JP_URL) —— 绕过统一层，无缓存、无归一化；
                #   ② 取值 .get("dif") —— 东财 clist 接口返回键实为 "diff"，致 items 恒为 []，
                #      日历效应成分股**从未入选**（静默失效、无报错，与 DEBT-008 同类的静默 bug）。
                #   适配器封装同一接口、键名正确、BK 前缀已规范化，且 f9/f23 的 PE/PB 口径已按 V17.0.15 修正。
                from stock_common.sc_datasource import get_em_board_members
                for item in get_em_board_members(ind_code)[:20]:
                    if len(result) >= 5:
                        break
                    c = str(item.get("code", ""))
                    if c in seen_codes:
                        continue
                    seen_codes.add(c)
                    result.append({
                        "code": c, "name": item.get("name", ""),
                        "reason": f"{month}月日历效应板块'{ind.get('name', '')}'成分股，行业排名第{ind.get('rank', 0)}位",
                        "score": _safe_float(item.get("change_pct", 0)),
                    })
            except Exception as _e:
                _debug_log(f"val calendar_effect_item: {_e}")
                continue
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略09: 逆向白马流 ───

async def strategy_09_contrarian_value(stocks, top_n=300):
    _sc = _load_strategy_config()
    _roe_good = _sc.get("fundamental", {}).get("roe_good", 15.0)
    candidates = [s for s in stocks if s.get("mcap_yi", 0) >= 50][:top_n]
    result = []
    for s in candidates:
        code = s["code"]
        # V16.3 O19: 统一层 ROE（F10 加权净资产收益率——与 med/lng 报告口径一致；
        # 原 tdx_get_finance_roe 为 0x0010 单期摊薄口径，跨脚本不可比）
        try:
            from stock_common.sc_datasource import get_gross_margin_and_roe

            gmar = await asyncio.to_thread(get_gross_margin_and_roe, code) or {}
            roe = gmar.get("roe")
        except Exception as _e:
            _debug_log(f"val strategy_10 roe error ({code}): {_e}")
            roe = None
        if roe is None or roe < _roe_good: continue
        keys, rows = _fast_kline(code)
        if len(rows) < 250: continue
        _ki = _kline_indices(keys); idx_c = _ki.get("close", -1); idx_v = _ki.get("vol", -1); idx_close = _ki.get("close", -1)
        if idx_close < 0: continue
        closes = [_safe_float(r[idx_close]) for r in rows[-250:] if len(r) > idx_close]
        if not closes: continue
        high_52w = max(closes[-250:])
        current_price = closes[-1]
        drawdown = (current_price - high_52w) / high_52w * 100
        if drawdown > -40: continue
        # V15.2: 从 s dict O(1) 读 pe_ttm（避免循环 get_pe_ttm_async 触发大量 zhb_data 缓存）
        pe_ttm = _safe_float(s.get("pe_ttm", 0))
        reason = (
            f"最新ROE={roe:.1f}%≥15%（优质白马），"
            f"距52周最高价{high_52w:.2f}元已下跌{abs(drawdown):.0f}%，"
            f"当前PE={pe_ttm:.1f}x，非基本面因素导致的错杀"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": -drawdown})
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略10: 筹码集中 ───

def strategy_10_holder_concentration(stocks, top_n=300):
    """V4: 筹码集中 — top_n=300 + 提前终止"""
    candidates = sorted(stocks, key=lambda x: x.get("mcap_yi", 0), reverse=True)[:top_n]
    result = []
    for s in candidates:
        code = s["code"]
        holders = holder_num_change(code, 3)
        if len(holders) < 2: continue
        if _safe_float(holders[0].get("change_ratio", 0)) >= -3: continue
        if _safe_float(holders[1].get("change_ratio", 0)) >= -3: continue
        avg_shrink = (abs(_safe_float(holders[0].get("change_ratio", 0))) + abs(_safe_float(holders[1].get("change_ratio", 0)))) / 2
        reason = (
            f"股东户数连续两季缩减（{holders[1].get('date', '')}: "
            f"{_safe_float(holders[1].get('change_ratio', 0)):.1f}%, "
            f"{holders[0].get('date', '')}: {_safe_float(holders[0].get('change_ratio', 0)):.1f}%），"
            f"平均每季缩减{avg_shrink:.1f}%，筹码集中度持续提升"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": avg_shrink})
        if len(result) >= 5:
            break
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略11: 量价背离防守 ───

def strategy_11_divergence_warning(stocks, top_n=300):
    candidates = sorted(stocks, key=lambda x: x.get("mcap_yi", 0), reverse=True)[:top_n]
    result = []
    for s in candidates:
        code = s["code"]
        keys, rows = _fast_kline(code)
        if len(rows) < 25: continue
        idx_close = -1; idx_vol = -1
        for i, k in enumerate(keys):
            if k in ("close", "close_price"): idx_close = i
            if k == "volume": idx_vol = i
        if idx_close < 0 or idx_vol < 0: continue
        recent = rows[-20:]
        closes = [_safe_float(r[idx_close]) for r in recent if len(r) > idx_close]
        vols = [_safe_float(r[idx_vol]) for r in recent if len(r) > idx_vol]
        if len(closes) < 5 or len(vols) < 5: continue
        if closes[-1] < max(closes): continue
        if not (vols[-3] > vols[-2] > vols[-1]): continue
        vol_decline_pct = (vols[-3] - vols[-1]) / vols[-3] * 100
        reason = (
            f"⚠️ 危险信号：价格创20日新高{closes[-1]:.2f}元，"
            f"但成交量连续3日萎缩{vol_decline_pct:.0f}%，"
            "【多头陷阱警告】——量价背离，警惕结构性顶部"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": vol_decline_pct})
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略12: 红利低波 ───

def strategy_12_dividend_yield(stocks):
    # V14.3.2: 4 天回测推荐 100（100 稳定性 0.57 > 300 稳定性 0.43）
    candidates = [s for s in stocks if s.get("mcap_yi", 0) >= 50][:100]
    result = []
    for s in candidates:
        code = s["code"]
        price = s.get("price", 0)
        if price <= 0: continue
        divs = common_get_dividend_history(code)
        if not divs or len(divs) < 3: continue  # V16.2.3: 兼容 None（TDX 分红接口失败）
        # V16.1: TTM 股息率 = 近 12 个月累计派息 / 现价（原只用最近一次分红，低估半年报/季报分红公司）
        one_year_ago = (date.today() - timedelta(days=365)).strftime("%Y-%m-%d")
        ttm_bonus = sum(
            _safe_float(d.get("bonus_rmb", 0))
            for d in divs if str(d.get("date", "")) >= one_year_ago
        )
        if ttm_bonus <= 0:
            ttm_bonus = _safe_float(divs[0].get("bonus_rmb", 0))
        if ttm_bonus <= 0: continue
        yield_pct = ttm_bonus / price * 100
        if yield_pct < 4.0: continue
        years_with_div = len([d for d in divs if _safe_float(d.get("bonus_rmb", 0)) > 0])
        reason = (
            f"TTM股息率{yield_pct:.2f}%（近12月累计派息{ttm_bonus:.4f}元/现价{price:.2f}元），"
            f"近{years_with_div}个报告期持续分红，稳定的现金奶牛资产"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": yield_pct})
        if len(result) >= 5:
            break
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略13: 头部资金风向标 ───

def strategy_13_liquidity_king(top_liquidity_pool):
    """
    在成交额 Top 5% 的核心池中，寻找今日成交额超越5日均量1.5倍且收阳的个股。
    """
    result = []
    for s in top_liquidity_pool:
        code = s["code"]
        keys, rows = _fast_kline(code)
        if len(rows) < 10: continue
        idx_vol = -1; idx_close = -1
        for i, k in enumerate(keys):
            if k == "volume": idx_vol = i
            if k in ("close", "close_price"): idx_close = i
        if idx_vol < 0 or idx_close < 0: continue
        vols = [_safe_float(r[idx_vol]) for r in rows[-6:] if len(r) > idx_vol]
        closes = [_safe_float(r[idx_close]) for r in rows[-2:] if len(r) > idx_close]
        if len(vols) < 6 or len(closes) < 2: continue
        avg_vol_5d = sum(vols[-6:-1]) / 5
        today_vol = vols[-1]
        if avg_vol_5d > 0 and today_vol > avg_vol_5d * 1.5 and closes[-1] >= closes[-2]:
            vol_ratio = today_vol / avg_vol_5d
            # MEDIUM(审查 2026-08-16): amount(万元) 与 amount_yi(亿元) 单位不同——
            # 分键换算统一为亿元: amount/10000 → 亿, amount_yi 原样
            _amt_yi = _safe_float(s.get("amount", 0)) / 10000 if _safe_float(s.get("amount", 0)) else _safe_float(s.get("amount_yi", 0))
            reason = (
                f"位列全市场前5%核心流动性池，今日成交额{_amt_yi:.2f}亿！"
                f"成交量异常放大至5日均量的{vol_ratio:.1f}倍，"
                "主力资金高位接盘或强力破局，流动性溢价显著"
            )
            result.append({
                "code": code, "name": s.get("name", ""), "reason": reason,
                "score": _amt_yi * vol_ratio,
            })
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略14: 北向持仓 Top30 异动（V7.5 新增） ───

def strategy_14_northbound_top(all_stocks, top_n=200):
    """
    V7.5: 北向（香港中央结算）持仓占比 Top30 标的筛选。
    数据源: 东财 RPT_F10_EH_HOLDERS（已封装在 stock_common.get_holder_structure）
    逻辑:
      1) 取市值前 top_n 的大票（北向更倾向布局大盘蓝筹）
      2) 对每只票提取最新季度的 northbound 持仓比例
      3) 筛选北向持仓 >= 3% 的标的
      4) 若有两季度数据，标注「加仓」或「减仓」
      5) 按北向持仓占比降序取 Top 5
    """
    _stock_map = {s["code"]: s for s in (all_stocks or [])}
    candidates = sorted(all_stocks or [], key=lambda x: x.get("mcap_yi", 0), reverse=True)[:top_n]
    results = []

    for s in candidates:
        code = s["code"]
        try:
            holders = get_holder_structure(code)
        except Exception as _e:
            _debug_log(f"val holder_structure: {_e}")
            holders = []
        if not holders:
            continue

        # 最新季度数据
        latest = holders[0]
        nb_ratio = _safe_float(latest.get("northbound", 0))
        if nb_ratio < 3.0:
            continue

        total_ratio = _safe_float(latest.get("total", 0))
        foreign_count = int(latest.get("foreign_count", 0))
        report_date = str(latest.get("date", ""))

        # 判断加仓趋势（对比上季度）
        trend_text = ""
        if len(holders) >= 2:
            prev_nb = _safe_float(holders[1].get("northbound", 0))
            diff = round(nb_ratio - prev_nb, 2)
            if diff > 0.3:
                trend_text = f"（较上季加仓 +{diff:.2f}%）"
            elif diff < -0.3:
                trend_text = f"（较上季减仓 {diff:.2f}%）"
            else:
                trend_text = "（持仓稳定）"

        stock_name = s.get("name", "") or _stock_map.get(code, {}).get("name", code)
        mcap = s.get("mcap_yi", 0) or _stock_map.get(code, {}).get("mcap_yi", 0)
        change_pct = s.get("change_pct", 0) or _stock_map.get(code, {}).get("change_pct", 0)

        reason = (
            f"北向（香港中央结算）持仓 {nb_ratio:.2f}%，"
            f"机构+北向+QFII合计 {total_ratio:.1f}%，"
            f"外资机构家数（不含北向） {foreign_count} 家，"
            f"报告期 {report_date}，"
            f"市值 {mcap:.0f}亿，今日涨跌 {change_pct:+.1f}%{trend_text}"
        )
        results.append({
            "code": code, "name": stock_name, "reason": reason,
            "score": nb_ratio,
        })
        if len(results) >= 8:  # 多拿一点供排序
            break

    return _top10_sorted(results, lambda x: x["score"])


# ─── 策略15: 龙虎榜席位活跃度（V7.5 新增） ───

def strategy_15_longhu_activity(all_stocks, today_str=None, top_n=200):
    """
    V7.5: 龙虎榜席位活跃度筛选。
    数据源: stock_common.get_recent_dragon_tiger（全市场）+ get_dragon_tiger_board（单股席位）
    逻辑:
      1) 获取近5日全市场龙虎榜上榜标的
      2) 对每只票取最近一次上榜的席位明细（买卖前五+机构）
      3) 多维度评分：机构净买额、著名游资席位识别、连续上榜天数、换手率
      4) 返回综合评分 Top5
    """
    if today_str is None:
        from datetime import date
        today_str = date.today().strftime("%Y-%m-%d")

    _stock_map = {s["code"]: s for s in (all_stocks or [])}
    dt_data = get_recent_dragon_tiger(7)
    if not dt_data:
        return []

    # 加载游资标签配置（用于识别著名席位）
    _cfg = _load_settings()
    _trader_tags = _cfg.get("trader_tags", {}) if _cfg else {}

    # 方案4：先全市场初筛，再对Top20查席位明细
    # 初筛评分：净买额 + 换手率 + 日期新鲜度
    def _preliminary_score(code, info):
        net_buy = abs(_safe_float(info.get("net_buy", 0)))
        turnover = _safe_float(info.get("turnover", 0))
        # 日期新鲜度：越近得分越高（最近=7分，7天前=0分）
        try:
            from datetime import datetime, date
            d = datetime.strptime(info.get("date", ""), "%Y-%m-%d").date()
            days_ago = (date.today() - d).days
            date_score = max(0, 7 - days_ago)
        except Exception as _e:
            _debug_log(f"val northbound_date_parse: {_e}")
            date_score = 0
        # 综合评分
        return net_buy * 0.05 + turnover * 2.0 + date_score * 3.0

    pre_ranked = sorted(
        dt_data.items(),
        key=lambda x: _preliminary_score(x[0], x[1]),
        reverse=True
    )
    codes_to_check = [code for code, _ in pre_ranked[:20]]

    results = []
    for code in codes_to_check:
        try:
            # 取该股最近7天的席位明细
            dtb = get_dragon_tiger_board(code, days=7)
            if not dtb or not dtb.get("records"):
                continue

            # 基础评分：机构净买额
            inst = dtb.get("institution", {})
            inst_net = _safe_float(inst.get("net_amt", 0))
            inst_buy = _safe_float(inst.get("buy_amt", 0))
            inst_sell = _safe_float(inst.get("sell_amt", 0))

            # 上榜次数
            _records = dtb.get("records", [])
            list_days = len(_records)
            first_date = _records[-1].get("date", today_str) if _records else today_str
            last_date = _records[0].get("date", today_str) if _records else today_str
            recent_net_sum = sum(_safe_float(r.get("net_buy", 0)) for r in _records)

            # 游资席位识别：在买一/买二/买三出现著名游资名称则加分
            hot_dept_score = 0.0
            hot_dept_names = []
            for side_key in ["buy", "sell"]:
                for seat in dtb.get("seats", {}).get(side_key, []):
                    sname = str(seat.get("name", ""))
                    for kw, tag in _trader_tags.items():
                        if kw in sname:
                            if side_key == "buy":
                                hot_dept_score += 3.0
                            else:
                                hot_dept_score += 1.0
                            if tag and tag not in hot_dept_names:
                                hot_dept_names.append(tag)
                            break

            # 换手率加分：3-15% 为活跃合理区间
            # V17.0.15: 区分「真实低换手」与「数据缺失」。龙虎榜 turnover 来自 TDX
            #   TURNOVERRATE（本地 TDX 日线陈旧，见字典 §12.x），缺失时 _safe_float→0.0。
            #   该值**只影响加分不影响过滤**（turnover_bonus 下限 0），故方向不会反；
            #   但原实现把 avg_turnover 无条件拼进 reason 文本 → 缺失时输出
            #   「平均换手率 0.0%」这一**由数据缺失伪造的事实**。这里改为缺失则不出该子句。
            _to_vals = [_safe_float(r.get("turnover", 0)) for r in _records]
            _to_valid = [v for v in _to_vals if v > 0]
            avg_turnover = (sum(_to_valid) / len(_to_valid)) if _to_valid else 0.0
            _to_txt = f"，平均换手率 {avg_turnover:.1f}%" if _to_valid else ""
            turnover_bonus = 0.0
            if 3.0 <= avg_turnover <= 15.0:
                turnover_bonus = 2.0
            elif 15.0 < avg_turnover <= 25.0:
                turnover_bonus = 1.0

            # 综合评分
            score = (
                inst_net * 0.05        # 机构净买额（万元，占比权重）
                + list_days * 1.5      # 连续上榜天数加分
                + hot_dept_score       # 游资席位识别
                + abs(recent_net_sum) * 0.01  # 近期净买总量
                + turnover_bonus       # 换手率合理区间
                + inst_buy * 0.03     # 机构买额加分
                - inst_sell * 0.03    # 机构卖额扣分
            )

            if score <= 0:
                continue

            # 股票信息：从 all_stocks 取，否则从龙虎榜数据取
            stock_info = _stock_map.get(code, {})
            stock_name = stock_info.get("name", "") or dt_data.get(code, {}).get("name", code)
            mcap = stock_info.get("mcap_yi", 0) or 0
            change_pct = stock_info.get("change_pct", 0) or 0
            # V16.4.1: 新股首日/前 5 日无涨跌幅限制(创业板/科创板)——极端涨跌幅(如 301717 首日
            # +662%)标注说明,避免被误读为普通涨跌幅(2026-08-12 实测)
            _chg_note = ""
            if abs(change_pct) > 50:
                _chg_note = "（上市初期无涨跌幅限制）"

            dept_tag_str = "、".join(hot_dept_names) if hot_dept_names else "无著名游资席位"
            reason = (
                f"近{list_days}天上榜，最近一次 {last_date}，"
                f"机构净买 {inst_net:+.1f}万（买 {inst_buy:+.1f}万 / 卖 {inst_sell:+.1f}万），"
                f"席位标签: {dept_tag_str}，"
                f"期间合计净买 {recent_net_sum:+.1f}万"
                f"{_to_txt}，"          # V17.0.15: 换手率缺失时整句省略，避免伪造 0.0%
                f"市值 {mcap:.0f}亿，今日涨跌 {change_pct:+.1f}%{_chg_note}"
            )
            results.append({
                "code": code, "name": stock_name, "reason": reason,
                "score": round(score, 2),
            })
            if len(results) >= 30:
                break
        except Exception as _e:
            _debug_log(f"val strategy_item: {_e}")
            continue

    return _top10_sorted(results, lambda x: x["score"])

# ─── 策略16: 52周位置百分位（V10.3新增）──

def strategy_16_52w_position(stocks, top_n=200):
    """V10.3: 52周位置百分位策略。
    利用zhb的high_52w/low_52w，筛选处于52周低位的优质标的。
    
    逻辑:
      1) 计算现价格在52周区间内的位置百分位
      2) 筛选位置百分位<30%（超卖区域）且PE合理的标的
      3) 评分: 位置百分位越低越好
    """
    result = []
    for s in stocks:
        code = s["code"]
        high_52w = _safe_float(s.get("high_52w", 0))
        low_52w = _safe_float(s.get("low_52w", 0))
        price = _safe_float(s.get("price", 0))
        pe_ttm = _safe_float(s.get("pe_ttm", 0))
        if not high_52w or not low_52w or not price:
            continue
        if high_52w <= low_52w:
            continue
        position_pct = (price - low_52w) / (high_52w - low_52w) * 100
        if position_pct > 30:
            continue
        if pe_ttm > 50:
            continue
        reason = (
            f"52周位置百分位={position_pct:.0f}%（低位超卖），"
            f"52周区间[{low_52w:.2f}, {high_52w:.2f}]（T-1），"
            f"现价{price:.2f}元(实时)，PE={pe_ttm:.1f}x(实时)"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": 100 - position_pct})
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略17: 主力资金占比因子（V10.3新增）──

def strategy_17_main_fund_ratio(stocks, top_n=1000):
    """V10.3: 主力资金占比因子策略。
    利用zhb的主力净流入额（T-1），TDX实时资金流作为fallback。
    
    逻辑:
      1) 计算主力净流入额占总成交额的比例
      2) 筛选主力资金占比>3%的标的（主力控盘度高）
      3) 评分: 主力资金占比越高越好
    """
    result = []
    # V15.5.14: 放宽到 3 天（原默认 2 天，ZHB 延迟 3 天 → 1000 只逐股 TDX 卡死）
    use_zhb = is_zhb_data_fresh(max_delay_days=3)
    # V15.5.14: 预加载 tdxstat2 全市场资金流（O(1) 读，替代逐股 get_main_net_buy）
    _zhb_stat2: Dict[str, Dict[str, Any]] = {}
    if use_zhb:
        try:
            from stock_common import get_zhb_market_stat2_snapshot
            _zhb_stat2 = get_zhb_market_stat2_snapshot() or {}
        except Exception as _e:
            _debug_log(f"val strategy20 stat2 load: {_e}")
    for s in stocks:
        code = s["code"]
        # V16.3 O21: 资金占比需分子分母同基准——use_zhb 时分母也用 stat2 T-1 amount
        #（原分母=腾讯 T 日成交额 → 盘中 T-1 资金流 ÷ T 日成交额 时间基准错位）
        _s2 = _zhb_stat2.get(code, {}) if use_zhb else {}
        amount_wan = (
            _safe_float(_s2.get("amount", 0))
            if use_zhb and _s2.get("amount")
            else _safe_float(s.get("amount", 0))
        )
        if not amount_wan or amount_wan == 0:
            continue
        main_amount = 0.0
        data_source = ""
        if use_zhb:
            # ⚠️ V17.0 实锤: main_net_buy_amount 实为开盘金额(竞价额)——策略 20/21/22 基于竞价额, 需改用东财 f137(待办)
            main_amount = _safe_float(_s2.get("main_net_buy_amount", 0))
            if main_amount:
                data_source = "ZHB(T-1,同基准)"
            # V16.3 O39 修复: stat2 缺字段（0）→ 不再单股 get_main_net_buy 兜底
            #（原 73 只 × 东财 2.38s/只限流 = 173s；stat2 全覆盖，缺字段本就不可得）
        if not main_amount or main_amount <= 0:
            # V16.3 O39 修复: 净流出/0/缺字段——use_zhb 时直接跳过（原逻辑对 ~4000 只净流出
            # + 99 只缺字段股每次 get_main_net_buy → is_zhb_data_fresh 检查 + 东财 2.36s/只限流
            # → 全市场 618s+ 卡死；且东财 T 日口径破坏 O21 同基准）
            if use_zhb:
                continue
            # 盘中（use_zhb=False）→ data_provider.get_main_net_buy（内部 ZHB→HTTP 优先级）
            try:
                mnb = get_main_net_buy(code)
                if mnb and mnb.get("main_net_buy_amount"):
                    main_amount = _safe_float(mnb["main_net_buy_amount"])
                    data_source = "HTTP/统一层"
            except Exception as _e:
                _debug_log(f"val strategy20 get_main_net_buy http {code}: {_e}")
                continue
        if not main_amount or main_amount <= 0:
            continue
        fund_ratio = abs(main_amount) / amount_wan * 100
        if fund_ratio < 3:
            continue
        reason = (
            # H5 修复(2026-08-15 二审): 文案口径与 V17.0 实锤一致——ZHB 主路径=竞价额, 非主力净流入
            f"竞价额占比={fund_ratio:.2f}%（占成交额高，资金关注度强），"
            f"开盘竞价额{main_amount:+.0f}万元（{data_source}，⚠️竞价额非主力净流入），"
            f"总成交额{amount_wan:.0f}万元"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": fund_ratio})
    return _top10_sorted(result, lambda x: x["score"])


# ═══════════════════════════════════════════════════════════════
# V11.5 新增：策略18（量能三连击）+ 策略19（资金动量）
# 基于 data_provider.get_volume_acceleration / get_capital_momentum
# 纯 ZHB 数据，无 HTTP fallback
# ═══════════════════════════════════════════════════════════════

def strategy_18_volume_acceleration(stocks, top_n=200):
    """V11.5: 量能三连击策略（纯 ZHB 数据）。

    V16.1: 字段契约对齐 get_volume_acceleration 真实返回
    （amount_t_1/amount_t_2/amount_t_3/is_accelerating/acceleration_ratio）。
    原 vol_ratio_5d/turnover_5d 字段不存在 → 策略恒空。
    """
    from core.data_provider import get_volume_acceleration
    result = []
    for s in stocks:
        code = s["code"]
        try:
            va = get_volume_acceleration(code)
        except Exception as _e:
            _debug_log(f"val strategy20 get_volume_acceleration {code}: {_e}")
            continue
        if not va or not isinstance(va, dict):
            continue
        accel_ratio = _safe_float(va.get("acceleration_ratio", 0))
        is_accel = bool(va.get("is_accelerating", False))
        # 加速比率>1（放量递增）即候选；is_accelerating 为强条件
        if not is_accel or accel_ratio <= 1.05:
            continue
        amt1 = _safe_float(va.get("amount_t_1", 0))
        amt2 = _safe_float(va.get("amount_t_2", 0))
        amt3 = _safe_float(va.get("amount_t_3", 0))
        score = accel_ratio * 10
        reason = (
            f"量能三连击: 成交额 {amt3:.0f}→{amt2:.0f}→{amt1:.0f}万 递增，"
            f"加速比 {accel_ratio:.2f}（放量加速）"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason, "score": score})
    return _top10_sorted(result, lambda x: x["score"])


def strategy_19_capital_momentum(stocks):
    """V11.5: 资金动量策略（纯 ZHB 数据）。

    V16.1: 字段契约对齐 get_capital_momentum 真实返回
    （net_buy_t_1/net_buy_t_2/momentum/momentum_ratio/signal）。
    原 main_net_ratio/streak_days 字段不存在 → 策略恒空。
    ⚠️ V17.0(2026-08-14)实锤: 底层 main_net_buy_amount 为竞价额——本策略实为**竞价动量**(非主力资金),
    展示文案以"竞价"口径呈现。
    """
    from core.data_provider import get_capital_momentum
    result = []
    for s in stocks:
        code = s["code"]
        try:
            cm = get_capital_momentum(code)
        except Exception as _e:
            _debug_log(f"val strategy21 get_capital_momentum {code}: {_e}")
            continue
        if not cm or not isinstance(cm, dict):
            continue
        momentum_ratio = _safe_float(cm.get("momentum_ratio", 0))
        momentum = _safe_float(cm.get("momentum", 0))
        signal = str(cm.get("signal", ""))
        # 动量比率>0 且信号为看多
        if momentum_ratio <= 0.05:
            continue
        score = momentum_ratio * 100
        reason = (
            # H5 修复(2026-08-15 二审): 策略19 底层=竞价额动量(实锤), 文案如实标注
            f"竞价动量: 竞价额动量比={momentum_ratio:.2f}，"
            f"动量值={momentum:.0f}（信号: {signal or '看多'}，⚠️竞价额口径非主力净流入）"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason, "score": score})
    return _top10_sorted(result, lambda x: x["score"])


def strategy_20_yjyg(stocks):
    """V17.0(2026-08-15): 业绩预增策略 — 东财 datacenter 业绩预告(RPT_PUBLIC_OP_NEWPREDICT).

    预告类型=预增/扭亏 且 净利变动幅度>=50% 为候选; 8 月中报预告窗口期信号强。
    ⚠️ 限流修复(2026-08-15): 全市场一次分页拉取(get_yjyg_all, 当日缓存), 不逐股请求。
    """
    from stock_common.sc_datasource import get_yjyg_all

    try:
        yg_map = get_yjyg_all() or {}
    except Exception as _e:
        _debug_log(f"val strategy22 get_yjyg_all: {_e}")
        return []

    result = []
    for s in stocks:
        code = s["code"]
        yg = yg_map.get(code)
        if not yg:
            continue
        ptype = yg.get("predict_type", "")
        inc = yg.get("increase_rate", 0)
        if ptype not in ("预增", "扭亏", "续盈", "略增"):
            continue
        if inc < 50:
            continue
        score = min(inc, 200)
        reason = (
            f"业绩{ptype}: 净利变动 {inc:+.1f}%"
            f"(区间 {yg.get('inc_lower', 0):+.0f}~{yg.get('inc_upper', 0):+.0f}%, "
            f"{yg.get('notice_date', '')} 公告)"
            f"{' 中报窗口' if yg.get('report_date', '').startswith('2026-06') else ''}"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason, "score": score})
    return _top10_sorted(result, lambda x: x["score"])


def strategy_21_earnings_expect(stocks):
    """V17.0(2026-08-15): 盈利预期策略 — 本机 ProfitForecast(零网络)预测 EPS 增速 + 股东户数筹码集中.

    预测 EPS 同比增速(2026E vs 2025A)>=20% 且股东户数下降(筹码集中)为候选。
    """
    from stock_common.sc_datasource import get_eps_forecast, holder_change

    result = []
    for s in stocks:
        code = s["code"]
        try:
            ef = get_eps_forecast(code, local_only=True)  # H4 修复: 全市场扫描仅本机数据, 禁止网络兜底
            if ef is None or len(ef) < 2:
                continue
            rows = ef.to_dict("records")
            eps_a = next((float(r["均值"]) for r in rows if "2025" in str(r["年度"]) and "A" in str(r["年度"])), 0)
            eps_e = next((float(r["均值"]) for r in rows if "2026" in str(r["年度"]) and "E" in str(r["年度"])), 0)
            if not eps_a or not eps_e:
                continue
            growth = (eps_e / eps_a - 1) * 100
            if growth < 20:
                continue
            hc = holder_change(code, local_only=True) or []  # H6 修复: 全市场扫描仅缓存命中判筹码集中
            holder_shr = False
            if len(hc) >= 2:
                # H3 修复: 契约键为 holder_num(_compute_holder_changes), 非 holder
                holder_shr = (hc[0].get("holder_num", 0) or 0) < (hc[1].get("holder_num", 0) or 0)
            score = growth * 0.8 + (30 if holder_shr else 0)
            reason = (
                f"盈利预期: 2026E EPS {eps_e:.2f} vs 2025A {eps_a:.2f} 增速 {growth:.0f}%"
                f"{' + 股东户数下降(筹码集中)' if holder_shr else ''}"
            )
            result.append({"code": code, "name": s.get("name", ""), "reason": reason, "score": score})
        except Exception as _e:
            _debug_log(f"val strategy23 eps expect {code}: {_e}")
            continue
    return _top10_sorted(result, lambda x: x["score"])
def strategy_22_mtd_momentum(stocks):
    """V17.0.5: 月内动量策略（纯 ZHB 数据，零网络——tdxstat2 Col[11] change_mtd）。

    口径: 本月至今累积涨跌幅(基准=上月末最后交易日收盘)。
    入选: 5% <= MTD <= 25%（强势但未透支; >25% 多为连板末端接力风险）;
    排除停牌(MTD 缺失)。与策略18/19(量能/竞价动量)正交: 月内趋势维度。
    """
    result = []
    for s in stocks:
        code = s.get("code", "")
        mtd = _safe_float(s.get("change_mtd"), 0)
        if mtd == 0 or not (5.0 <= mtd <= 25.0):
            continue
        score = mtd
        reason = (
            f"本月至今 +{mtd:.2f}%(基准=上月末收盘)——月内趋势强劲且未过度拉伸,"
            f"持有期动量延续候选"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason, "score": score})
    return _top10_sorted(result, lambda x: x["score"])
def strategy_23_ps_undervalued(stocks, top_n=500):
    """V17.0.5 P2: PS 低估值策略（fuyao 估值快照批量——市值 top_n 预筛控配额）。

    逻辑: 全样本 PS(TTM) 20 分位以下 且 PCF>0(经营现金流为正)。
    适用: 高毛利未盈利/轻资产类 PE 失效标的的替代估值锚。
    无 Key/限流时静默返回空(不阻塞其余策略)。
    """
    from stock_common import get_fuyao_valuation, is_fuyao_enabled

    if not is_fuyao_enabled():
        return []
    pool = sorted(stocks, key=lambda x: _safe_float(x.get("mcap_yi", 0)), reverse=True)[:top_n]
    vals = {}
    for i in range(0, len(pool), 100):
        batch = [s["code"] for s in pool[i: i + 100]]
        try:
            for r in get_fuyao_valuation(batch):
                vals[str(r.get("ticker"))] = r
        except Exception as _e:
            _debug_log(f"val strategy25 valuation batch {i}: {_e}")
    if not vals:
        return []
    _ps_sorted = sorted(
        float(v["ps_ttm"]) for v in vals.values()
        if v.get("ps_ttm") is not None and float(v["ps_ttm"]) > 0
    )
    if not _ps_sorted:
        return []
    _q20 = _ps_sorted[int(len(_ps_sorted) * 0.2)]
    result = []
    for s in pool:
        r = vals.get(s.get("code", ""))
        if not r:
            continue
        ps = r.get("ps_ttm")
        pcf = r.get("pcf_ttm")
        if ps is None or ps <= 0 or ps > _q20:
            continue
        if pcf is None or pcf <= 0:
            continue
        score = (_q20 / ps) * 10
        reason = (
            f"PS(TTM) {ps:.2f}x ≤ 全市场20分位({_q20:.2f}x)且经营现金流为正"
            f"(PCF {pcf:.1f}x)——收入端低估候选"
        )
        result.append({"code": s["code"], "name": s.get("name", ""), "reason": reason, "score": score})
    return _top10_sorted(result, lambda x: x["score"])




def _safe_int(v) -> int:
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return 0


# ═══════════════════════════════════════════════
# 报告生成（V7.5 异步版为主，同步版为 asyncio.run 包装）
# ═══════════════════════════════════════════════

def run_discovery(output_path):
    """同步版包装：委托给异步版执行（保留向后兼容）。"""
    return asyncio.run(run_discovery_async(output_path))


async def run_discovery_async(output_path):
    """V7.5 异步版: 使用 asyncio.gather 并行跑 20 策略（约 2-3x 提速）

    V14.3.1: 移除入口处 _TDX_KLINE_CACHE.clear()（冗余操作）。
    理由：进程级缓存本就只活在本进程内，新进程必空；同进程内 23 策略
    共享同一份 L1 缓存是性能优化（22 次复用 vs 22 次从 L2 重读）。
    """
    _t_now = datetime.now()
    today_str = _t_now.strftime("%Y-%m-%d")
    lines = []
    def L(s=""): lines.append(s)

    L("---")
    L(f"  **A 股策略发现报告**  [{today_str} {_t_now.strftime('%H.%M.%S')}]")
    L("---")
    L("  市场: A 股 | 策略: 23 | 引擎: asyncio | 并发: 3")
    L("-" * 85)
    L("  预热: 加载市场数据 & 策略配置…")
    _load_t0 = time.time()  # V17.0.10c(2026-08-28): 加载阶段耗时基；用于把总时长在"加载 vs 扫描"间拆分归因

    cfg = _load_settings()
    _cfg = cfg or {}

    # V11.5: 使用 data_provider 统一数据中心层
    # 优先ZHB全量快照，失败fallback到TDX全市场，保持混合分层架构
    _zhb_date, _zhb_fresh = "", False
    all_stocks = []
    # V17.0.x(2026-09-10) P0 热启动: ZHB 快照 + 腾讯批量行情按数据日期进程级缓存,
    # 同日重跑 / main.py 批次(val→sht→med→lng)复用, 跳过网络拉取(原每次 3–7 分钟)。
    try:
        _zhb_date_probe = get_zhb_data_date() or ""
    except Exception:
        _zhb_date_probe = ""
    # V16.4.1: 提前初始化——snapshot 失败走 tdx_get_all_stocks 兜底时, 下方 L2046 引用
    # _tencent_map 会 NameError(原 try 内 L1726 才赋值, 兜底路径未覆盖)
    _tencent_map: Dict[str, Dict[str, Any]] = {}
    try:
        _snapshot = _VAL_SNAPSHOT_CACHE.get(_zhb_date_probe) if _zhb_date_probe else None
        if _snapshot is None:
            _snapshot = await get_market_snapshot_async()
            if _zhb_date_probe:
                _VAL_SNAPSHOT_CACHE[_zhb_date_probe] = _snapshot
        if _snapshot:
            _zhb_date = get_zhb_data_date() or ""
            _zhb_fresh = is_zhb_data_fresh(max_delay_days=3)
            all_codes = list(_snapshot.keys())

            # V12.1 休市期旁路优化：仅在非交易日和盘前（9:15前）旁路，其余时段获取T日数据
            # V16.2 修复: 市场状态判断提前 —— 原逻辑先全市场腾讯批量（133 批/8s+）再丢弃，休市纯浪费
            from stock_common import get_market_status
            m_status, _ = get_market_status()
            is_bypass = m_status in ("closed", "pre_market")
            # V16.3 O39 修复: is_bypass 时也初始化 _tencent_map（原 else 分支才赋值——
            # 休市旁路时下方 L1746 腾讯 mcap 兜底引用未定义变量 → UnboundLocalError →
            # 被外层 except 吞 → tdx 兜底失败 → 提前 return → val 假成功不落盘）
            _tencent_map: Dict[str, Dict[str, Any]] = {}
            if is_bypass:
                L(f"  ⚡ 探测到非盘中时段 ({m_status})，自动旁路实时行情，直接复用 ZHB 昨收快照基准！")
                _price_map = {}
            else:
                # V15.5.9: 全市场腾讯批量预加载（不封 IP，含 mcap_yi/pe_ttm/turnover_pct）
                # 替代原逐股 get_em_quote_full（push2 连接级风控 + 1.5s 限流 → 7957 次卡死数小时）
                try:
                    from core.tdx_client import _tencent_batch_fallback
                    _tc_key = f"{_zhb_date_probe}|live"
                    _tencent_map = _VAL_TENCENT_CACHE.get(_tc_key)
                    if _tencent_map is None:
                        _tencent_map = _tencent_batch_fallback(all_codes)
                        _VAL_TENCENT_CACHE[_tc_key] = _tencent_map
                    if _tencent_map:
                        _debug_log(f"val tencent batch: {len(_tencent_map)}/{len(all_codes)} 只")
                except Exception as _e:
                    _debug_log(f"val tencent batch error: {_e}")
                L(f"  ✅ data_provider全市场: {len(all_codes)}只，腾讯批量行情 {len(_tencent_map)}只…")
                _price_map = _tencent_map

                # V17.2.x(2026-09-10) 性能优化: 用已拉取的全市场腾讯批量行情零网络预热
                # core.data_provider._BATCH_QUOTE_CACHE。get_canonical_stock_data 命中后跳过 TDX/腾讯
                # 单股/EM 逐股网络(L399 批量命中短路, 且本批已含 open/high/low/last_close 使 OHLC 需求满足
                # 不再回退 TDX), 且本批已含 roa/roe_deduct_ttm/limit_up/limit_down/pb → L490 估值补取亦短路。
                # val 全市场逐股扫描(策略04/07 各 5000+ 只)由"数千次串行网络"降为"纯内存命中"。
                # 零额外请求(复用管道已发生的同一批量拉取, 防封三层机制不变); 仅 val 进程内映射一次。
                try:
                    import datetime as _dt_mod
                    from core import data_provider as _dp
                    _bq_cache = _dp._BATCH_QUOTE_CACHE
                    _pd_extra = _dp._PD_EXTRA_CACHE
                    _today_str = _dt_mod.datetime.now().strftime("%Y%m%d")
                    _warmed = 0
                    for _c, _m in _tencent_map.items():
                        if _m and _m.get("price"):
                            # V17.2.x(2026-09-10) 性能优化: 把已拉取的全市场腾讯批量行情零网络预热进
                            # core.data_provider._BATCH_QUOTE_CACHE —— get_canonical_stock_data 命中后跳过
                            # TDX/腾讯单股/push2 逐股网络(L399 批量命中短路, OHLC 已含故不再回退 TDX,
                            # 估值字段 roa/roe_deduct_ttm/limit_up/limit_down/pb 已含故 L490 估值补取短路)。
                            _bq_cache[_c] = dict(_m)
                            # V17.2.x(2026-09-10) 性能优化: val 不消费 pe_dynamic/fund_main_today/财务TTM族,
                            # 但 get_canonical_stock_data 的 L640 push2delay 补充块会因这两字段缺失而对每只股票
                            # 打 1 次被全局 ~1.2s 文件锁串行的 get_em_quote_full_delay —— 全市场 5000+ 只即数千秒瓶颈。
                            # 用哨兵 0 预填 _PD_EXTRA_CACHE 使 L648 缓存命中、L653 push2 跳过
                            # (L659/L669 对 0 值排除, 不污染 rt_quote)。仅 val 进程作用域, 不影响其它报告。
                            _pd_extra[_c] = {
                                "pe_dynamic": float(_m.get("pe_dynamic") or 0),
                                "fund_main_today": 0.0,
                                "fund_main_5d": 0.0,
                                "fund_super_today": 0.0,
                                "fund_large_today": 0.0,
                                "fund_mid_today": 0.0,
                                "fund_small_today": 0.0,
                            }
                            _warmed += 1
                    # 锁定日期, 防止 get_canonical_stock_data 首次调用时 L645 清掉上面的 _PD_EXTRA_CACHE 预热
                    _dp._PD_EXTRA_CACHE_DATE = _today_str
                    if _warmed:
                        _debug_log(f"val batch-quote prewarm: {_warmed}/{len(_tencent_map)} 只 -> _BATCH_QUOTE_CACHE(+_PD_EXTRA_CACHE 哨兵)")
                except Exception as _e:
                    _debug_log(f"val batch-quote prewarm error: {_e}")

            # 转换为列表格式，过滤停牌股（volume=0），补充市值
            # V16.0: ZHB 不再提供 volume 字段（Col[24] 误映射已移除），此过滤自然失效
            all_stocks = []
            _excluded = 0  # V16.0: ZHB 无 volume 后停牌过滤失效，恒 0（保留统计位）
            _mcap_count = 0
            for _code, _stat in _snapshot.items():
                # V16.0: ZHB 不再提供 volume 字段，原"volume=0 过滤停牌"失效，移除
                _stock = {"code": _code}
                for _k, _v in _stat.items():
                    if _k not in ("market", "date"):
                        _stock[_k] = _v
                
                # ZHB自带市值预统计
                if "mcap_yi" in _stock and _stock["mcap_yi"] > 0:
                    _mcap_count += 1
                    
                _price = _safe_float(_price_map.get(_code, {}).get("price", 0))
                # V17.2.7(2026-09-07) 修复: 腾讯 T 日涨跌幅覆盖 ZHB T-1（与 mak 一致）。
                # 原仅覆盖 price, change_pct 仍为 ZHB T-1 → 风控仪表盘涨停/跌停按 9/4 口径计算,
                # 与 mak 同日(9/7)广度(87/92/95)不可比。盘前/休市旁路时 _price_map 为空, 不覆盖(保留 ZHB T-1)。
                _tq_cp = _price_map.get(_code, {}).get("change_pct")
                if _tq_cp is not None:
                    _stock["change_pct"] = _safe_float(_tq_cp)
                # V17.0(2026-08-15 运行核查): bypass(纯ZHB/休市)模式下 _price_map 为空 →
                # price=0 → mcap 全 0 → 依赖 price/mcap 的策略(01/02/04/05/06/10/13/18)全 0 命中。
                # 修复: 用 TDX 本机 .day 日线(零网络, 盘前模式同款)补收盘价 → 市值链恢复
                if _price <= 0:
                    try:
                        # V17.0(2026-08-15): TDX 本机 .day 尾部快速读(零网络毫秒级)——
                        # 新版 .day 格式: date<uint32> + OHLC<int32×0.001元> + amount<float32万> + volume<int32手>
                        _pk = _KLINE_PRICE_CACHE.get(_code)
                        if _pk is None:
                            _pk = _fast_day_close(_code) or {}
                            _KLINE_PRICE_CACHE[_code] = _pk
                        if _pk.get("price"):
                            # M2 终审修复: .day 日期新鲜度校验——陈旧收盘价禁用于市值计算
                            # V17.0.4(2026-08-19): 放宽为容忍 7 天——TDX .day 常滞后于 ZHB
                            # (客户端未同步, 实测 8/14 vs ZHB 8/17), 原严格拒绝 → bypass 无价
                            # → mcap=0 → 形态/估值类策略全 0 命中(8/19 4:22 全 0 根因);
                            # 市值粗算对 ≤7 天旧价不敏感(偏差<3%), 拒绝的代价(全策略 0)更大
                            try:
                                _day_ok = str(_pk.get("date", 0)) >= str(int(_zhb_date or 0) - 7)
                            except (ValueError, TypeError):
                                _day_ok = True
                            if not _day_ok:
                                _debug_log(f"val .day stale ({_code}): {_pk.get('date')} < ZHB-7d {_zhb_date}")
                            else:
                                _price = _safe_float(_pk["price"])
                                _price_map.setdefault(_code, {})["price"] = _price
                    except Exception as _e:
                        _debug_log(f"val kline price fallback ({_code}): {_e}")
                # V15.2 P0 修复: price_map 中 price 可能为 0（push2 部分股票未返回）
                _rt_data = _price_map.get(_code, {})
                if _price and _price > 0:
                    _stock["price"] = _price
                    _mcap = _calc_mcap_yi(_code, _price)
                    if _mcap > 0:
                        if "mcap_yi" not in _stock or not _stock["mcap_yi"] > 0:
                            _mcap_count += 1
                        _stock["mcap_yi"] = _mcap
                # V15.2 P0 修复: 当 _price=0 但 _rt_data 有 mcap_yi（push2 直接给）时，
                # 优先用 _rt_data["mcap_yi"]（避免 0 价格导致 mcap 算不出来）
                if not _stock.get("mcap_yi") and _rt_data.get("mcap_yi"):
                    # M18 修复：先取新值再判"旧值缺失/为0"决定是否计数，避免赋值后判断恒 False(漏计)
                    _new_mcap = _safe_float(_rt_data["mcap_yi"])
                    if _new_mcap > 0:
                        if "mcap_yi" not in _stock or not _stock.get("mcap_yi") > 0:
                            _mcap_count += 1
                        _stock["mcap_yi"] = _new_mcap
                # V15.2 P0 兜底: 上面都没拿到 mcap_yi（_price=0 且 push2 批量无 mcap），
                # 改用 get_em_quote_full 单只拉（已有 push2 fallback，可拿到 mcap）
                if not _stock.get("mcap_yi") or _stock["mcap_yi"] <= 0:
                    # V15.5.9: 腾讯批量兜底（不封 IP）— 优先于逐股 push2
                    _tq = _tencent_map.get(_code, {})
                    _tq_mcap = _safe_float(_tq.get("mcap_yi", 0))
                    if _tq_mcap > 0:
                        _stock["mcap_yi"] = _tq_mcap
                        if not _stock.get("price") and _tq.get("price"):
                            _stock["price"] = _safe_float(_tq["price"])
                        if not _stock.get("pe_ttm") and _tq.get("pe_ttm"):
                            _stock["pe_ttm"] = _safe_float(_tq["pe_ttm"])
                        if not _stock.get("turnover_pct") and _tq.get("turnover_pct"):
                            _stock["turnover_pct"] = _safe_float(_tq["turnover_pct"])
                        _mcap_count += 1
                    # V15.5.13: 腾讯缺失不再逐股 push2（连接级风控 → 全市场卡死）
                    # mcap=0 由策略的 mcap>=50 过滤自然排除，可接受
                    # V11.5: 实时字段统一覆盖（混合分层：API动态层覆盖静态层）
                    _rt = _price_map.get(_code, {})
                    # V16.3 O21: 平盘（0%）也是今日事实——is not None 判定，0 不回退 ZHB T-1
                    if _rt.get("change_pct") is not None:
                        _stock["change_pct"] = _safe_float(_rt.get("change_pct", 0))
                    _real_amount = _safe_float(_rt.get("amount_wan", 0))
                    if _real_amount and _real_amount > 0:
                        _stock["amount"] = _real_amount
                        _stock["amount_yi"] = _real_amount / 10000.0
                    _real_pe = _safe_float(_rt.get("pe_ttm", 0))
                    if _real_pe and _real_pe > 0:
                        _stock["pe_ttm"] = _real_pe
                    _real_turnover = _safe_float(_rt.get("turnover_pct", 0))
                    if _real_turnover and _real_turnover > 0:
                        _stock["turnover_pct"] = _real_turnover
                else:
                    _amount_wan = _safe_float(_stat.get("amount", 0))
                    if _amount_wan > 0:
                        _stock["amount_yi"] = _amount_wan / 10000.0
                all_stocks.append(_stock)
            # V17.2.7(2026-09-07) 修复: 数据基准标签如实反映实际取数路径, 消除"✅新鲜"误导。
            # 盘后/盘中: 腾讯 T 日行情已生效 → 基准=今日, 与 mak 同口径;
            # 盘前/休市旁路: 仅 ZHB T-1 可用 → 基准=最新交易日(标注 T-1 快照)。
            _t_day_used = (not is_bypass) and bool(_tencent_map)
            if m_status in ("morning", "afternoon", "post_market"):
                _fresh_tag = "✅T日实时"
            elif m_status == "post_close":
                _fresh_tag = "✅T日收盘"
            else:
                _fresh_tag = "⚠️T-1快照(最新交易日)"
            _basis_date = _zhb_date if (is_bypass or not _tencent_map) else time.strftime("%Y%m%d")
            L(f"  ✅ data_provider全市场: {len(all_stocks)}只（过滤{_excluded}只停牌股，市值覆盖率{_mcap_count}/{len(all_stocks)}）[{_fresh_tag}]")
            if _basis_date:
                L(f"  📊 数据日期: {_basis_date}"
                  f"{'（腾讯T日,与mak同基准）' if _t_day_used else '（ZHB最新交易日快照）'}")
            if is_bypass:
                L(f"  📊 数据分层: [纯ZHB横截面] 已完全复用 ZHB 历史数据，无任何实时网络开销")
            else:
                L(f"  📊 数据分层: [API实时] price/change_pct/amount/pe_ttm/turnover_pct | [静态层] high_52w/low_52w/pb/dividend_yield/ipo_price/industry_code")
        else:
            raise ValueError("market snapshot empty")
    except Exception as _e:
        _debug_log(f"val data_provider_load: {_e}, fallback to tdx_get_all_stocks")
        all_stocks = tdx_get_all_stocks()
        if not all_stocks:
            L("  ❌ 无法获取全市场股票数据")
            # V16.3 O39 修复: 提前 return 前也落盘（失败报告可见 + 文件存在供 GD 上传）——
            # 原实现空手 return → execute_pipeline 无条件打印"已保存" → 文件不存在 + 无 GD（假成功）
            # 附异常详情（用户可见失败原因——原 _debug_log 日志用户不可见）
            try:
                _err_detail = str(_e)[:300]
            except Exception:
                _err_detail = type(_e).__name__
            L(f"  ⚠️ 失败原因: {_err_detail}")
            try:
                # V17.0 审查: 收敛为公共写尾样板(save_text_report), 修 UnboundLocalError——
                # 原写文件失败时 L1831 return _fail_out 变量未绑定
                _fail_out = save_text_report(output_path, lines)
                _debug_log(f"val failure report written: {output_path} ({len(_fail_out)} chars)")
                return _fail_out
            except Exception as _we:
                _debug_log(f"val failure report write error: {_we}")
                return ""
        # fallback时仍做初筛
        all_stocks, _zhb_date, _zhb_fresh = _tdxstat_prescreen(all_stocks)

    # V10.0: 扩大扫描范围，利用zhb零成本数据
    # 热点池: ~100只→~300只；流动性池: 300只→500只
    _stock_map = {s["code"]: s for s in all_stocks}
    # V15.1: 过滤 ETF/LOF/可转债（仅保留 A 股）
    _before = len(all_stocks)
    all_stocks = [s for s in all_stocks if _is_a_stock(s.get("code", ""))]
    _filtered = _before - len(all_stocks)
    if _filtered > 0:
        L(f"  📋 V15.1 A 股过滤: 移除 {_filtered} 只 ETF/LOF/可转债（{_before} → {len(all_stocks)}）")
        _stock_map = {s["code"]: s for s in all_stocks}
    ths_hot_list = ths_hot_reason(today_str)
    if not ths_hot_list:
        # V16.3 O27: 同花顺强势股失败（401 反爬/超时）→ 东财人气榜兜底（统一层已有，
        # emappdata 独立域 1.0rps，仅失败时触发，封禁风险≈0）
        try:
            from stock_common import em_hot_rank
            _hr = em_hot_rank() or []
            ths_hot_list = [
                {"code": _r.get("code", ""), "name": _r.get("name", ""),
                 "zhangfu": _safe_float(_r.get("pct", 0)), "reason": ""}
                for _r in _hr if _r.get("code")
            ]
            if ths_hot_list:
                L(f"  ⚠ 同花顺强势股获取失败 → 东财人气榜兜底 {len(ths_hot_list)} 只")
        except Exception as _e:
            _debug_log(f"val hot pool fallback: {_e}")
    if not ths_hot_list:
        # V17.0.x(2026-09-10) 新维度修复: 同花顺 + 东财人气榜均不可用(反爬/限流)时,
        # 退化为 ZHB 内存强势股(当日涨幅降序 Top300)——零网络、稳定,
        # 避免 01/03/07/08/15 五策略因上游反爬系统性空出(原 hot_pool=[] 致全空)。
        try:
            _gainers = sorted(
                [s for s in all_stocks if _safe_float(s.get("change_pct", 0)) > 0],
                key=lambda x: _safe_float(x.get("change_pct", 0)),
                reverse=True,
            )[:300]
            ths_hot_list = [
                {"code": s.get("code", ""), "name": s.get("name", ""),
                 "zhangfu": _safe_float(s.get("change_pct", 0)), "reason": ""}
                for s in _gainers if s.get("code")
            ]
            if ths_hot_list:
                L(f"  ⚠ 同花顺/东财热点源均不可用 → ZHB 内存强势股兜底 {len(ths_hot_list)} 只（涨幅降序 Top300）")
        except Exception as _e:
            _debug_log(f"val hot pool zhb fallback: {_e}")
    ths_hot_codes = {item.get("code", "") for item in ths_hot_list if item.get("code")}
    # V16.1: 热点池合并同花顺原始字段（zhangfu/reason）→ 快照记录，
    # 修复策略01 读 zhangfu、策略14 读 reason_tag 字段契约断裂问题
    _ths_by_code = {item.get("code", ""): item for item in ths_hot_list if item.get("code")}
    hot_pool = []
    for s in all_stocks:
        if s.get("code", "") not in ths_hot_codes:
            continue
        _merged = dict(s)
        _th = _ths_by_code.get(s.get("code", ""), {})
        # V17.0.15 实证纠正（探针 2026-08-28，getharden 返回 81 行）:
        #   getharden **确实**返回 zhangfu(涨幅%) 与 huanshou(换手率%)，例如
        #   000712 锦龙股份 {"close":11.8,"zhangfu":9.972,"huanshou":1.69}。
        #   ⚠️ 旧注释 V16.4.0「getharden 不返回涨幅」**与实证矛盾、是错的** ——
        #   字典 §12.8.12 的字段表才是对的。故本分支是**主路径**而非兜底。
        #   elif 仅在「东财人气榜兜底且 pct 缺失」时才可能触发，保留作防御。
        if _th.get("zhangfu") is not None:
            _merged["zhangfu"] = _safe_float(_th["zhangfu"])
        elif _merged.get("change_pct"):
            # V16.4.1 修复: 原 L1880 残留 `_merged["zhangfu"] = _th["zhangfu"]` 复制粘贴错误
            # —— elif 分支中 _th 必无 zhangfu, 裸索引必然 KeyError('zhangfu') 导致 val 全崩
            _merged["zhangfu"] = _safe_float(_merged.get("change_pct"))
        if _th.get("reason"):
            _merged["reason_tag"] = _th["reason"]
        # huanshou = getharden 当日换手率(%)（实证存在）。仅当为正才覆盖——
        # 东财人气榜兜底路径无此键，此时保留腾讯批量预加载的 turnover_pct。
        if _safe_float(_th.get("huanshou") or 0) > 0:
            _merged["turnover_pct"] = _safe_float(_th["huanshou"])
        hot_pool.append(_merged)

    # V16.3 O27: hot_pool ZHB 预筛（缩小 01/03/07 的逐股 K 线量——ZHB 内存零成本，
    # 只过滤明显空头股；回调中的 01 龙回头候选不受影响）
    if hot_pool:
        _zs_map = {_s["code"]: _s for _s in all_stocks}
        _keep = []
        for _h in hot_pool:
            _zs = _zs_map.get(_h.get("code", ""), {})
            _chg5 = _safe_float(_zs.get("change_5d", 0))
            _chg20 = _safe_float(_zs.get("change_20d", 0))
            if _chg5 <= -15 and _chg20 <= -25 and _safe_int(_zs.get("streak_days", 0)) < 1:
                continue  # 明显空头（5日/20日深跌且无连涨）——跳过，省 K 线请求
            _keep.append(_h)
        if 0 < len(_keep) < len(hot_pool):
            L(f"  📋 O27 hot_pool ZHB 预筛: {len(hot_pool)} → {len(_keep)} 只（过滤明显空头）")
            hot_pool = _keep

    top_liquidity_pool = sorted(all_stocks, key=lambda x: _safe_float(x.get("amount", 0) or x.get("amount_yi", 0)), reverse=True)[:500]

    L(f"  ✅ 全市场: {len(all_stocks)} | 热点池(同花顺强势): {len(hot_pool)} | 流动性Top500: {len(top_liquidity_pool)}")
    L(f"  ⏱ 全市场数据加载完成 @ {datetime.now().strftime('%H.%M.%S')}（耗时 {time.time() - _load_t0:.1f}s）")

    all_selections = {}

    # V7.5: 策略阶段 Semaphore 控制并发。V17.0.x(2026-09-10) P2: 按取数成本分桶——
    # 网络/逐股K线/盘后datacenter 类(见 _VAL_NET_HEAVY)限流到 3, 纯内存/ZHB 类放宽到 8,
    # 避免零成本策略被无谓串行化浪费时间预算。
    _strategy_sem_net = asyncio.Semaphore(3)
    _strategy_sem_mem = asyncio.Semaphore(8)

    # 每策略硬超时墙（根因修复，2026-09-09）。
    # 背景：底层 requests.Session 的 timeout=15 仅覆盖 connect/read，不覆盖 DNS 解析
    # （socket.getaddrinfo 不受其约束）。当上游（fuyao/东财）DNS 或路由间歇挂起时，单次
    # 网络调用会远超 15s 甚至无限挂起 → asyncio.to_thread 永不返回 → asyncio.gather 整批
    # 停滞 → 不打印"完成"行 → main.py 静默 900s 后强制 kill（rc=-1）。
    # 此处强加每策略墙：单策略上游挂起被隔离为「超时跳过 + 日志」，其余策略正常产出，
    # 整批不被拖垮。取值须 < main.py _STALL_TIMEOUT(900)，确保超时打印能重置卡死计时。
    _STRATEGY_TIMEOUT = 720

    async def _run_sync_strategy(name, func, *args):
        # V15.5.11: 完成即打印耗时（运行时 profiling，替代逐策略单测）
        _st = time.time()
        try:
            _num = int(name[2:4]) if name[2:4].isdigit() else 0
        except Exception:
            _num = 0
        _sem = _strategy_sem_net if _num in _VAL_NET_HEAVY else _strategy_sem_mem
        async with _sem:
            try:
                if inspect.iscoroutinefunction(func):
                    _r = await asyncio.wait_for(func(*args), timeout=_STRATEGY_TIMEOUT)
                else:
                    _coro = asyncio.to_thread(func, *args)
                    _r = await asyncio.wait_for(_coro, timeout=_STRATEGY_TIMEOUT)
            except asyncio.TimeoutError:
                # 上游阻塞（DNS/路由挂起等）触发：隔离该策略，不阻断其余策略与整批。
                _debug_log(
                    f"val strategy {name}: 硬超时({_STRATEGY_TIMEOUT}s)跳过——上游阻塞"
                    f"(疑似 DNS/路由挂起，requests timeout 不覆盖解析阶段)，已隔离"
                )
                # 纳入统一 fallback 审计：与项目既有源降级/_fallback_logger 体系对齐，
                # 使"策略级超时降级"这一降级事件可被统一日志检索与监控。
                try:
                    _fallback_logger.warning(
                        f"val strategy {name}: 策略级超时降级({_STRATEGY_TIMEOUT}s)——"
                        f"上游阻塞(疑似 DNS/路由挂起)，该策略降级为空选，不阻断其余策略"
                    )
                except Exception:
                    pass
                try:
                    print(f"  {name}... ⚠ 超时跳过({_STRATEGY_TIMEOUT}s)", flush=True)
                except UnicodeEncodeError:
                    print(f"  [TIMEOUT] {name} skipped({_STRATEGY_TIMEOUT}s)", flush=True)
                return []
        _dt = time.time() - _st
        _cnt = len(_r) if isinstance(_r, list) else "?"
        try:
            print(f"  {name}... 完成({_cnt}只, {_dt:.0f}s)", flush=True)
        except UnicodeEncodeError:
            print(f"  [OK] {name}... done({_cnt}, {_dt:.0f}s)", flush=True)
        return _r

    # V10.0: 扩大策略扫描范围，利用zhb零成本数据
    # V14.3 P1: _top_n_large 1000 → 300（避免周日休市日 1000 次 TDX TCP 请求卡死 15 分钟）
    # V14.3.2: 4 天 ZHB 回测验证（cache/zhb/zhb_202607{21,22,23,24}）
    #   - 选中数曲线：100→1000 多数策略 100 就饱和
    #   - 稳定性曲线（Jaccard）：10/11/15 在 200-300 提升最大
    #   - 推荐差异化：02/04/06/13/22→100, 11/12/17/19→200, 05→300, 20→1000
    # V16.3 O27: 全市场化改造——
    #   - 17/18/19/20 纯 ZHB 内存策略 → 全市场（毫秒级零成本；20 回测 top1000 仅覆盖
    #     19.9% 命中，80% 控盘股在池外，全市场 136 只全覆盖）
    #   - 02/05/06 预筛全市场（函数内 ZHB 内存先行）→ 趋势强度排序取 top300 逐股确认
    #     （V14.3.2 曾推荐 02→100/05→300；现按趋势优先，弱趋势小市值不再被 mcap 截断）
    _top_n_large = 300   # 形态类（02/05/06）— O27: 趋势强度排序后 top300 逐股确认
    _top_n_medium = 200  # 财务/筹码类（11/12/17）— 回测推荐 200（稳定性提升 26%）
    _top_n_small = 100   # 周线/核心（02/04）— V14.3.2 推荐（O27 后 02 改走 _top_n_large）
    _top_n_pure = 200    # 纯 ZHB 类（17/20）— 回测推荐 200（O27 后 17/19 全市场，保留备用）
    _top_n_fund = 1000   # 主力资金（18）— O27 后全市场（回测 top1000 覆盖率仅 19.9%）

    # 策略注册（1-20 为同步函数，用 Semaphore 控制并发）
    # V14.3.2: 基于 4 天 ZHB 回测（docs/backtest_v1432/）差异化 top_n
    # V16.3 O27: 全市场化（19/20/21/22 直接传 all_stocks；02/05/06 函数内预筛+趋势排序）
    _strategy_defs = [
        ("策略01【龙回头】", strategy_01_longhuitou, (hot_pool, today_str)),
        ("策略02【周线多头】", strategy_02_weekly_ma, (all_stocks, _top_n_large)),  # O27: 预筛全市场+趋势 top300
        ("策略03【量价齐升】", strategy_03_volume_breakout, (hot_pool,)),
        ("策略04【核心打折】", strategy_04_core_discount, (all_stocks,)),  # 内部 200
        ("策略05【W底形态】", strategy_05_double_bottom, (all_stocks, _top_n_large)),  # O27: 函数内预筛+趋势 top300
        ("策略06【红三兵】", strategy_06_three_soldiers, (all_stocks, _top_n_large)),  # O27: 函数内预筛+趋势 top300
        ("策略07【政策驱动(含热度图谱)】", strategy_07_policy_driven, (all_stocks, hot_pool)),
        ("策略08【日历效应】", strategy_08_calendar_rotation, ()),
        ("策略09【逆向白马】", strategy_09_contrarian_value,
         (sorted(all_stocks, key=lambda x: x.get("mcap_yi", 999999), reverse=True)[:_top_n_medium], _top_n_medium)),
        ("策略10【筹码集中】", strategy_10_holder_concentration, (all_stocks, _top_n_medium)),  # 200（稳定性提升 26%）
        ("策略11【量价信号】", strategy_11_divergence_warning, (all_stocks, _top_n_medium)),  # 200
        ("策略12【高股息】", strategy_12_dividend_yield, (all_stocks,)),  # 内部 300→100
        ("策略13【流动性王】", strategy_13_liquidity_king, (top_liquidity_pool,)),
        ("策略14【北向Top】", strategy_14_northbound_top, (all_stocks, _top_n_medium)),  # V14.3.2: 150→200
        ("策略15【龙虎榜】", strategy_15_longhu_activity, (all_stocks, today_str)),
        ("策略16【52周低位】", strategy_16_52w_position, (all_stocks,)),  # O27: 全市场（纯内存毫秒级）
        ("策略17【竞价额占比】", strategy_17_main_fund_ratio, (all_stocks,)),  # V17.0.x: main_net_buy_amount 实锤=竞价额(非主力净流入), 如实命名
        ("策略18【竞价额加速】", strategy_18_volume_acceleration, (all_stocks,)),  # V17.0.x: 竞价额三连加速, 非主力净流入
        ("策略19【竞价动量】", strategy_19_capital_momentum, (all_stocks,)),  # V17.0(2026-08-14)实锤: 竞价额动量
        ("策略20【业绩预增】", strategy_20_yjyg, (all_stocks,)),  # V17.0: 东财业绩预告(datacenter 单股查询)
        ("策略21【盈利预期】", strategy_21_earnings_expect, (all_stocks,)),  # V17.0: 本机 ProfitForecast+股东户数
        ("策略22【月内动量】", strategy_22_mtd_momentum, (all_stocks,)),  # V17.0.5: change_mtd(ZHB Col[11], 零网络)
        ("策略23【PS低估值】", strategy_23_ps_undervalued, (all_stocks,)),  # V17.0.5 P2: fuyao PS·PCF(市值top500)
    ]

    try:
        print("  ▶ 23 策略并行扫描（asyncio 模式，并发 3）…", flush=True)
    except UnicodeEncodeError:
        print("  >> 23 策略并行扫描（asyncio 模式，并发 3）…", flush=True)
    _scan_t0 = time.time()

    _names = [item[0] for item in _strategy_defs]
    _tasks = [_run_sync_strategy(name, func, *args) for name, func, args in _strategy_defs]
    _results = await asyncio.gather(*_tasks, return_exceptions=True)

    _scan_total_time = time.time() - _scan_t0
    _names_full = _names

    for _name, _raw in zip(_names_full, _results):
        _r, _err = [], None
        if isinstance(_raw, Exception):
            _err = str(_raw)[:60]
            _debug_log(f"val strategy {_name}: {_err}")  # M1 终审修复: 异常可见性(双打印修复副作用)
        elif isinstance(_raw, list):
            _r = _raw
        all_selections[_name] = _r
        # V17.0(2026-08-15): 进度已在 _run_sync_strategy 内实时打印(带耗时)——此处不再重复打印
    
    try:
        print(f"  扫描完成（共 {_scan_total_time:.1f}s）", flush=True)
    except UnicodeEncodeError:
        # V16.3 A4: 原兜底分支重打同一中文串（无 ascii 替换）会二次抛异常崩溃
        print(f"  [OK] scan done ({_scan_total_time:.1f}s)".encode('ascii', errors='replace').decode('ascii'), flush=True)

    # V15.1: 补充缺失的股票名称（zhb数据源无name字段）
    # 优先用 ZHB unified_name_map（profile.dat + relation.dat + tdxpkmore + pttab，
    # 覆盖 ~30%），缺失的再从东财批量拉取补充。
    _all_codes = set()
    for _items in all_selections.values():
        for _item in _items:
            _name = _item.get("name", "")
            if not _name or _name == _item["code"]:
                _all_codes.add(_item["code"])
    if _all_codes:
        # V15.1: ZHB 字典优先（零网络请求）
        _zhb_name_map: Dict[str, str] = {}
        try:
            from core.zhb_client import get_zhb
            _zhb_name_map = get_zhb().unified_name_map
        except Exception as _e:
            _debug_log(f"val zhb name map: {_e}")
        # V15.1: 仅对 ZHB 字典未命中的股票补名称（避免 27 批 × 15s 超时拖垮整体性能）
        _unmatched = [_c for _c in _all_codes if not _zhb_name_map.get(_c)]
        # V16.1.7: 优先复用已有 _tencent_map（主路径已批量拉取，零额外请求）；
        # 仅腾讯也未命中的才走东财批量（≤200 只兜底，push2 限流最严）
        _name_map = {}
        if _unmatched:
            _tencent_hit = {_c: _tencent_map.get(_c, {}) for _c in _unmatched if _tencent_map.get(_c, {}).get("name")}
            if _tencent_hit:
                _name_map.update({_c: {"name": v["name"]} for _c, v in _tencent_hit.items()})
            _still_missing = [_c for _c in _unmatched if _c not in _name_map]
            if _still_missing and len(_still_missing) <= 200:  # 数量 ≤200 才走东财，否则纯 ZHB 兜底
                try:
                    # M14 修复(2026-08-15 二审): 同步批量在 async 上下文阻塞 → to_thread
                    _em_names = await asyncio.to_thread(get_em_batch_quotes, _still_missing)
                    _name_map.update(_em_names)
                except Exception as _e:
                    _debug_log(f"val name em_batch_quotes: {_e}")
        for _items in all_selections.values():
            for _item in _items:
                _name = _item.get("name", "")
                if not _name or _name == _item["code"]:
                    # 优先用 ZHB 字典
                    _nm = _zhb_name_map.get(_item["code"], "") or _name_map.get(_item["code"], {}).get("name", _item["code"])
                    _item["name"] = _nm
                    if _item["code"] in _stock_map:
                        _stock_map[_item["code"]]["name"] = _nm

    L("\n" + "=" * 85)
    L("  扫描结果汇总: " + str(len(all_selections)) + "个策略共产出 " + str(sum(len(v) for v in all_selections.values())) + " 次选择")
    L("---")

    # V16.3 J: _sfmt 同步注册表——补 21/22、删已移除的 14、修正 15（流动性王）
    _sfmt = {"策略01":"01 龙回头", "策略02":"02 周线多头(含金叉)", "策略03":"03 量价齐升", "策略04":"04 核心打折", "策略05":"05 W底形态", "策略06":"06 红三兵", "策略07":"07 政策驱动(含热度图谱)", "策略08":"08 日历效应", "策略09":"09 逆向白马", "策略10":"10 筹码集中", "策略11":"11 量价信号", "策略12":"12 高股息", "策略13":"13 流动性王", "策略14":"14 北向Top", "策略15":"15 龙虎榜", "策略16":"16 52周低位", "策略17":"17 竞价额占比", "策略18":"18 竞价额加速", "策略19":"19 竞价动量", "策略20":"20 业绩预增", "策略21":"21 盈利预期", "策略22":"22 月内动量", "策略23":"23 PS低估值"}

    for _st_name in _names_full:
        items = all_selections.get(_st_name, [])
        _k = _st_name[:4] if len(_st_name) >= 4 else _st_name
        _title = _sfmt.get(_k, _st_name)
        L("\n" + "-"*85)
        L(f"[{_title}]")
        if items:
            # V17.0.2d(2026-08-17): 用户要求显示全部候选(策略输出上限 10, 原展示截断 5)
            for idx2, item in enumerate(items[:10], 1):
                # V16.3.3 (2026-08-10 字典 12.15.8): ST 标注（不剔除——ST 涨跌幅已统一 10%，市场价值正常体现）
                # V17.0 S5: 统一走 sc_utils.name_mark
                from stock_common.sc_utils import name_mark as _u_name_mark

                _st_mark = _u_name_mark(item.get('name', ''))
                L(f"  #{idx2}  {item.get('name', '')} ({item.get('code', '')}){_st_mark}")
                L(f"     {item.get('reason','')}")
        else:
            # V17.0.x(2026-09-10) 新维度: 无产出时给出成因提示, 避免"空章节"误导
            if _k == "策略23":
                try:
                    from stock_common import is_fuyao_enabled
                    if not is_fuyao_enabled():
                        L("  ⚠️ 未配置 fuyao 估值源，本策略已跳过（无 Key 时恒空，属预期）")
                except Exception:
                    pass
            elif _k in ("策略14", "策略15", "策略20"):
                L("  ⚠️ 盘后数据（北向/龙虎榜/业绩预告）当前时段无产出，属预期")
            L("  (今日无符合该策略阈值的标的)")

    _cf = {}
    for name, items in all_selections.items():
        for item in items:
            _c = item.get("code", ""); _cf[_c] = _cf.get(_c, 0) + 1
    _res = [(c, n) for c, n in sorted(_cf.items(), key=lambda x: x[1], reverse=True) if n >= 2]
    L(f"\n{'='*85}")
    L("[多策略共振金股推荐]")
    if _res:
        for code, cnt in _res[:10]:
            _nm = _stock_map.get(code, {}).get("name", code)
            L(f"  **{_nm}({code})**: {cnt}个策略")
    else:
        L("  今日暂无共振股票")

    _zt = sum(1 for s in all_stocks if is_limit_up(s.get("code", ""), s.get("name", ""), _safe_float(s.get("change_pct", 0))))
    _dt_total = sum(1 for s in all_stocks if is_limit_down(s.get("code", ""), s.get("name", ""), _safe_float(s.get("change_pct", 0))))
    L(f"\n{'='*85}")
    L("[风控仪表盘 & 仓位管理]")
    L(f"  涨停{_zt} | 跌停{_dt_total}")
    # V16.1: 删除硬编码策略胜率（"55-65%"等非当前运行计算结果，误导投资决策）
    L("  ℹ️ 策略胜率需前瞻回测验证（当前版本不做历史回测声明）")
    L(f"\n{'='*85}")
    # V17.0(2026-08-15 C 方案): 全量 md 化——渲染层确定性转换(标题/分隔线/F10 边框表/对齐空格表→md)
    from stock_common.md_render import render_md_report
    output = render_md_report(output_path, lines)
    return output


class ValReportRunner(BaseReportRunner):
    """23 策略全市场发现引擎 Runner"""

    def __init__(self):
        super().__init__("get_val_report", "val", "23 策略全市场发现引擎")

    def execute_pipeline(self) -> str:
        ts = self.report_ts  # V17.0 R1: 基类统一口径(%Y%m%d_%H%M)
        op = os.path.join(self.args.output, f"get_val_report_{ts}.md")
        try:
            print("  ⏱ 预计运行 3-7 分钟（asyncio 异步模式）", flush=True)
        except UnicodeEncodeError:
            print("  [INFO] 预计运行 3-7 分钟（asyncio 异步模式）", flush=True)

        # M4 修复（O39 守卫收口，2026-08-30）：
        #  - 异步成功 / 同步回退 两条路径的执行都放到异常分支里，但文件存在性判定
        #    移到 try/except 之外，避免"异步成功却落盘失败"时误触发同步回退（双跑）。
        #  - 文件真实存在才打印"✅ 已保存"；不存在则打印"⚠️ 报告未生成"警告，
        #    不再静默假成功（V16.3 O39 回归守卫）。
        #  - 仅当"异步与同步双路均失败（抛异常）"时才向上抛 RuntimeError，
        #    让 run()（M1 已改为 re-raise）以非零退出码结束，main.py 的 all_ok 才是真实值。
        _async_ok = False
        try:
            asyncio.run(run_discovery_async(op))
            _async_ok = os.path.exists(op)
        except Exception as e:
            print(f"  ⚠️ asyncio 失败，退回同步模式: {e}", flush=True)
            try:
                run_discovery(op)
                _async_ok = os.path.exists(op)
            except Exception as e2:
                print(f"❌ 报告生成失败: {e2}", flush=True)
                raise e2
        if _async_ok:
            try:
                print(f"  ✅ 已保存: {op}", flush=True)
            except UnicodeEncodeError:
                print(f"  [OK] 已保存: {op}", flush=True)
        else:
            _err = f"报告未生成（文件不存在: {op}）"
            try:
                print(f"  ⚠️ {_err}", flush=True)
            except UnicodeEncodeError:
                print(f"  [WARN] {_err}", flush=True)
        return op

    def upload_reports(self, drive: Any, folder_id: str, output_file: str) -> None:
        self.upload_single_report(drive, folder_id, output_file)


if __name__ == "__main__":
    runner = ValReportRunner()
    runner.run()

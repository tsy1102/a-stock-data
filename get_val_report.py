#!/usr/bin/env python3
"""
get_val_report.py — 21 策略全市场发现引擎
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
  - 策略15【政策热度图谱】（同花顺 reason tags + 政策关键词 量化热度）
  - 策略16【北向Top30】（东财机构持仓结构分析，高北向持仓+加仓标的）
  - 策略17【龙虎榜席位活跃度】（全市场龙虎榜扫描 + 游资席位识别 + 机构买卖评分）
  - 从 stock_common 导入统一龙虎榜函数 / 统一板块判断 / 涨停判断

Usage:
    python get_val_report.py                  # 全量 21 策略
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
from stock_common import (_safe_float, _quick_request, UA,
                           JP_URL,
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
                           get_sina_financial_report,
                           get_em_batch_quotes)  # V11.5
from core.data_provider import (get_market_snapshot_async,
                           get_turnover_pct_async,
                           get_main_net_buy)  # V16.1: 策略20 用同步版; V16.4.1: 删 async 版; V17.0: 内部=f137+f140 主力净
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
    """2026-08-11: 升级 O25——ZHB 快照聚合优先（同 lng/sht/med），TDX board_list 兜底。
    原 V4 直连 TDX board_list：T-1 口径缺失、无市值加权；O25 返回 leader_name 键（老消费方读 leader，兼容处理）。"""
    try:
        from stock_common.sc_datasource import get_industry_rank_from_zhb

        rows = get_industry_rank_from_zhb(top_n)
        if rows:
            return rows
    except Exception as _e:
        _debug_log(f"val industry_rank zhb error: {_e}")
    sectors = tdx_get_board_list(0)
    if not sectors:
        return []
    return sectors


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
    fin = get_sina_financial_report(code, num_periods=12)
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
        snapshot = get_zhb_market_snapshot()
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
# 15 个策略引擎
# ═══════════════════════════════════════════════════

# V15.1: A 股代码前缀白名单（沪深主板/创业板/科创板/北交所），其余（ETF/LOF/可转债）过滤掉
# V17.0 S3: 统一收敛到 stock_common.sc_utils（is_a_stock/A_STOCK_PREFIXES 单一来源）


def _is_a_stock(code: str) -> bool:
    """V17.0 S3: 统一走 sc_utils.is_a_stock（原本地 _A_STOCK_PREFIXES 定义已收敛）。"""
    from stock_common.sc_utils import is_a_stock as _u_is_a_stock

    return _u_is_a_stock(code)

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
    """V15.5.8: K 线获取 — 优先 TDX（easy_tdx 适配器+磁盘缓存，快），失败 fallback 百度。

    val 全市场扫描 strategy_05/06/12/15 对 1300 只候选逐股取 K 线，
    原 common_baidu_kline_full（HTTP 0.9s/次）冷缓存 700-1200 秒。
    TDX 适配器实测 0.0s/次（磁盘缓存命中）。
    """
    try:
        # V16.3 O22: 统一走 baidu_kline_full（原局部 tdx_get_security_bars 死 import 已清）
        _k, _r = common_baidu_kline_full(code, count=count)
        if _r and len(_r) >= 65:
            return _k, _r
    except Exception as _e:
        _debug_log(f"val _fast_kline tdx fallback ({code}): {_e}")
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
        try:
            turnover = await get_turnover_pct_async(code) or 0
        except Exception:
            turnover = 0
        if turnover > _turnover_cap: continue
        reason = (
            f"前期强势股(涨幅{zhangfu:.1f}%)，"
            f"当前回踩MA10({ma10:.2f}元)，乖离率{ma10_bias:+.2f}%，"
            f"换手率仅{turnover:.1f}%，缩量企稳，筹码沉淀充分"
        )
        result.append({"code": code, "name": name, "reason": reason,
                       "score": -abs(ma10_bias) + (8 - turnover) * 0.1})
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略02: 周线级别多均线多头排列 ───

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
        # V16.1: 箱体上沿用"前60根"（排除当前价）— 原 max(closes[-60:]) 含当前价，
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
            f"当前价{current_price:.2f}元，"
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
    # V16.3.7: THS 批量 PB 仅作**校验**（口径已统一——PB 一律走 canonical 腾讯/push2 除息口径，与东财/腾讯官网一致）；
    # 字典 PB 双口径矩阵：THS 静态 vs 除息，除息窗口差异可至 14%（茅台 2026-08）；50 只/批 + 0.1s 限频
    # V16.4.0: thsdk 通道仅盘中（9:30-15:00）可用——盘后官方账号拒绝登录（-6），
    # 200 只逐只尝试会白等 10-15 分钟；与 canonical（data_provider is_trading_hours 保护）对齐
    try:
        from stock_common import get_market_status

        _th_status = get_market_status()
        _th_status = _th_status[0] if isinstance(_th_status, tuple) else _th_status
        _ths_allowed = _th_status in ("morning", "lunch", "afternoon")
    except Exception:
        _ths_allowed = False  # V16.4.0 保守：时段不确定时不调 THS（THS 为校验非主源）
    if _ths_allowed:
        try:
            from stock_common import get_ths_market_snapshot
            _ths_codes = [
                ("USHA" if s["code"].startswith("6") else "USZA") + s["code"]
                for s in big_caps if s["code"][:2] not in ("92", "43", "83", "87", "88")
            ]
            if _ths_codes:
                _ths_map = await asyncio.to_thread(get_ths_market_snapshot, _ths_codes)
                _ths_pb = {}
                for _c, _d in _ths_map.items():
                    for _k, _v in _d.items():
                        if _k.startswith("市净率") and _v not in (None, "", 4294967295, 2147483648):
                            _ths_pb[_c[4:]] = _v
                            break
                for _s in big_caps:
                    if _s["code"] in _ths_pb:
                        _s["pb_ths"] = _ths_pb[_s["code"]]
        except Exception as _e:
            _debug_log(f"val strategy04 ths pb: {_e}")
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
        # V16.3.7: THS 静态值 pb_ths 仅校验（见下），不参与取值——消除双口径漂移
        # V16.3.7: 校验日志——THS 静态（扩展1）vs canonical（除息）差异 >10% 提示除息窗口
        pb = _safe_float(cdata.pb)  # V16.3.7: 口径统一——PB 一律走 canonical（腾讯/push2 除息口径）
        _ths_ref = _safe_float(s.get("pb_ths", 0))
        if _ths_ref > 0 and pb > 0 and abs(pb - _ths_ref) / pb > 0.10:
            _debug_log(f"val04 pb 口径差异 {code}: canonical {pb} vs THS {_ths_ref}（除息窗口？）")
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


# ─── 策略07: 均线金叉 ───

def strategy_07_golden_cross(hot_pool):
    result = []
    for stock in hot_pool:
        code = stock.get("code", "")
        name = stock.get("name", "")
        kline = baidu_kline_last(code)
        if not kline: continue
        try:
            ma5 = _safe_float(kline.get("ma5avgprice", 0))
            ma10 = _safe_float(kline.get("ma10avgprice") or kline.get("ma10", 0))
            ma20 = _safe_float(kline.get("ma20avgprice", 0))
        except (ValueError, IndexError):
            continue
        if any(v <= 0 for v in [ma5, ma10, ma20]): continue
        if not (ma5 > ma10 > ma20): continue
        q = get_tencent_quote(code)
        vol_ratio = q.get("vol_ratio", 0)
        if vol_ratio < 1.3: continue
        reason = (
            f"MA5({ma5:.2f})上穿MA10({ma10:.2f})和MA20({ma20:.2f})，"
            f"量比{vol_ratio:.1f}倍，激活锁仓筹码，技术性多头趋势确立"
        )
        result.append({"code": code, "name": name, "reason": reason,
                       "score": vol_ratio})
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略08: 政策驱动流（V7.5: 优先用同花顺 reason tags，新闻 NLP 为 fallback） ───

async def strategy_08_policy_driven(stocks, hot_pool=None):
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


# ─── 策略09: 日历效应法 ───

def strategy_09_calendar_rotation():
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
                params = {"pn": "1", "pz": "20", "po": "1", "np": "1",
                          "fltt": "2", "invt": "2", "fs": f"b:{ind_code}",
                          "fields": "f12,f14,f2,f3,f20"}
                # V16.2.10: 改 _quick_request（JP_URL=83.push2 属 push2 系风控面，
                # 原 _request_with_retry 无令牌桶/熔断/封禁跳过/跨进程锁 → 限流遗漏入口）
                r = _quick_request(JP_URL, params=params, headers={"User-Agent": UA}, timeout=10)
                if r is None: continue
                items = (r.json().get("data") or {}).get("dif", [])
                for item in items:
                    if len(result) >= 5: break
                    c = str(item.get("f12", ""))
                    if c in seen_codes: continue
                    seen_codes.add(c)
                    result.append({
                        "code": c, "name": item.get("f14", ""),
                        "reason": f"{month}月日历效应板块'{ind.get('name', '')}'成分股，行业排名第{ind.get('rank', 0)}位",
                        "score": _safe_float(item.get("f3", 0)),
                    })
            except Exception as _e:
                _debug_log(f"val calendar_effect_item: {_e}")
                continue
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略10: 逆向白马流 ───

async def strategy_10_contrarian_value(stocks, top_n=300):
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


# ─── 策略11: 筹码集中 ───

def strategy_11_holder_concentration(stocks, top_n=300):
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


# ─── 策略12: 量价背离防守 ───

def strategy_12_divergence_warning(stocks, top_n=300):
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


# ─── 策略13: 红利低波 ───

def strategy_13_dividend_yield(stocks):
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


# ─── 策略15: 头部资金风向标 ───

def strategy_14_liquidity_king(top_liquidity_pool):
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


# ─── 策略16: 政策热度图谱（V7.5 新增） ───

def strategy_15_policy_heatmap(all_stocks, hot_pool):
    """
    V7.5: 综合同花顺 reason tags + 政策关键词命中 + 市场热度 量化评分。
    相比策略08（只做简单匹配），本策略引入三维热度评分：
      score = 涨幅贡献 + 关键词命中数 + 成交额分位
    只选市值 10-300亿（政策弹性最显著的区间），避免巨无霸或小票失真。
    """
    _cfg = _load_settings()
    policy_keywords = _cfg.get("policy_keywords", ["政策", "支持", "资金", "规划", "印发", "发布", "推动", "鼓励",
                       "十四五", "补贴", "减税", "利好", "振兴", "基建", "消费", "科技"])

    candidates = {}

    # 1) 从 hot_pool（同花顺强势股）中提取带政策 reason tag 的标的
    if hot_pool:
        for h in hot_pool[:200]:
            tag = h.get("reason_tag", "")
            matched = [kw for kw in policy_keywords if kw in tag]
            if not matched:
                continue
            candidates[h["code"]] = {
                "code": h["code"], "name": h.get("name", ""),
                "tag": tag[:100], "matched_kw": matched,
                "change_pct": _safe_float(h.get("zhangfu", 0)),
                "amount_yi": _safe_float(h.get("amount_yi", 0)),
                "mcap_yi": _safe_float(h.get("mcap_yi", 0)),
            }

    # 2) 从 all_stocks 中补充带政策关键词的板块归因（若 name 包含相关词）
    for s in all_stocks or []:
        if s["code"] in candidates:
            continue
        _nm = s.get("name", "")
        _reason = ""
        for tag_key in ["reason", "reason_tag", "reason_tags"]:
            if tag_key in s:
                _reason = str(s[tag_key])
                break
        matched = [kw for kw in policy_keywords if kw in _reason or kw in _nm]
        if not matched:
            continue
        candidates[s["code"]] = {
            "code": s["code"], "name": _nm, "tag": _reason[:80],
            "matched_kw": matched,
            "change_pct": _safe_float(s.get("change_pct", 0)),
            "amount_yi": _safe_float(s.get("amount_yi", 0)),
            "mcap_yi": _safe_float(s.get("mcap_yi", 0)),
        }

    if not candidates:
        return []

    # 3) 市值过滤（10-300亿）+ 计算三维热度分
    results = []
    all_amounts = [_safe_float(c.get("amount_yi", 0)) for c in candidates.values() if _safe_float(c.get("amount_yi", 0)) > 0]
    max_amount = max(all_amounts) if all_amounts else 1.0
    for code, c in candidates.items():
        if not (10.0 <= _safe_float(c.get("mcap_yi", 0)) <= 300.0):
            continue
        # 涨幅贡献（-5%到+10%线性映射 0-1）
        change_contrib = max(0.0, min(1.0, (_safe_float(c.get("change_pct", 0)) + 5.0) / 15.0))
        # 关键词命中数（1-N，映射 0-1）
        kw_contrib = min(1.0, len(c.get("matched_kw", [])) / 4.0)
        # 成交额分位（相对本池最高）
        amount_contrib = (_safe_float(c.get("amount_yi", 0)) / max_amount) if max_amount > 0 else 0
        # 综合分
        score = (change_contrib * 0.5 + kw_contrib * 0.3 + amount_contrib * 0.2) * 100
        reason = (
            f"政策关键词命中: {', '.join(c.get('matched_kw', [])[:3])}，"
            f"今日涨幅 {_safe_float(c.get('change_pct', 0)):+.1f}%，成交额 {_safe_float(c.get('amount_yi', 0)):.1f}亿，"
            f"市值 {_safe_float(c.get('mcap_yi', 0)):.0f}亿，热度评分 {score:.1f}"
        )
        results.append({"code": code, "name": c.get("name", ""), "reason": reason, "score": score})

    return _top10_sorted(results, lambda x: x["score"])


# ─── 策略17: 北向持仓 Top30 异动（V7.5 新增） ───

def strategy_16_northbound_top(all_stocks, top_n=200):
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
            f"外资机构家数 {foreign_count} 家，"
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


# ─── 策略18: 龙虎榜席位活跃度（V7.5 新增） ───

def strategy_17_longhu_activity(all_stocks, today_str=None, top_n=200):
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
            avg_turnover = sum(_safe_float(r.get("turnover", 0)) for r in _records) / max(list_days, 1)
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
                f"期间合计净买 {recent_net_sum:+.1f}万，"
                f"平均换手率 {avg_turnover:.1f}%，"
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

# ─── 策略19: 52周位置百分位（V10.3新增）──

def strategy_18_52w_position(stocks, top_n=200):
    """V10.3: 52周位置百分位策略。
    利用zhb的high_52w/low_52w，筛选处于52周低位的优质标的。
    
    逻辑:
      1) 计算当前价格在52周区间内的位置百分位
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
            f"当前价{price:.2f}元(实时)，PE={pe_ttm:.1f}x(实时)"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": 100 - position_pct})
    return _top10_sorted(result, lambda x: x["score"])


# ─── 策略20: 主力资金占比因子（V10.3新增）──

def strategy_19_main_fund_ratio(stocks, top_n=1000):
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
# V11.5 新增：策略21（量能三连击）+ 策略22（资金动量）
# 基于 data_provider.get_volume_acceleration / get_capital_momentum
# 纯 ZHB 数据，无 HTTP fallback
# ═══════════════════════════════════════════════════════════════

def strategy_20_volume_acceleration(stocks, top_n=200):
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


def strategy_21_capital_momentum(stocks):
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
            # H5 修复(2026-08-15 二审): 策略21 底层=竞价额动量(实锤), 文案如实标注
            f"竞价动量: 竞价额动量比={momentum_ratio:.2f}，"
            f"动量值={momentum:.0f}（信号: {signal or '看多'}，⚠️竞价额口径非主力净流入）"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason, "score": score})
    return _top10_sorted(result, lambda x: x["score"])


def strategy_22_yjyg(stocks):
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


def strategy_23_earnings_expect(stocks):
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
    理由：进程级缓存本就只活在本进程内，新进程必空；同进程内 21 策略
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

    cfg = _load_settings()
    _cfg = cfg or {}

    # V11.5: 使用 data_provider 统一数据中心层
    # 优先ZHB全量快照，失败fallback到TDX全市场，保持混合分层架构
    _zhb_date, _zhb_fresh = "", False
    all_stocks = []
    # V16.4.1: 提前初始化——snapshot 失败走 tdx_get_all_stocks 兜底时, 下方 L2046 引用
    # _tencent_map 会 NameError(原 try 内 L1726 才赋值, 兜底路径未覆盖)
    _tencent_map: Dict[str, Dict[str, Any]] = {}
    try:
        _snapshot = await get_market_snapshot_async()
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
                    _tencent_map = _tencent_batch_fallback(all_codes)
                    if _tencent_map:
                        _debug_log(f"val tencent batch: {len(_tencent_map)}/{len(all_codes)} 只")
                except Exception as _e:
                    _debug_log(f"val tencent batch error: {_e}")
                L(f"  ✅ data_provider全市场: {len(all_codes)}只，腾讯批量行情 {len(_tencent_map)}只…")
                _price_map = _tencent_map

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
                            # M2 终审修复: .day 日期新鲜度校验(陈旧收盘价禁用于市值计算)
                            if str(_pk.get("date", 0)) < str(_zhb_date or 0):
                                _debug_log(f"val .day stale ({_code}): {_pk.get('date')} < ZHB {_zhb_date}")
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
                    _stock["mcap_yi"] = _safe_float(_rt_data["mcap_yi"])
                    if _stock["mcap_yi"] > 0:
                        if "mcap_yi" not in _stock or not _stock["mcap_yi"] > 0:
                            _mcap_count += 1
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
            _fresh_tag = "✅新鲜" if _zhb_fresh else "⚠️延迟"
            L(f"  ✅ data_provider全市场: {len(all_stocks)}只（过滤{_excluded}只停牌股，市值覆盖率{_mcap_count}/{len(all_stocks)}）[{_fresh_tag}]")
            if _zhb_date:
                L(f"  📊 数据日期: {_zhb_date}")
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
    ths_hot_codes = {item.get("code", "") for item in ths_hot_list if item.get("code")}
    # V16.1: 热点池合并同花顺原始字段（zhangfu/reason）→ 快照记录，
    # 修复策略01 读 zhangfu、策略16 读 reason_tag 字段契约断裂问题
    _ths_by_code = {item.get("code", ""): item for item in ths_hot_list if item.get("code")}
    hot_pool = []
    for s in all_stocks:
        if s.get("code", "") not in ths_hot_codes:
            continue
        _merged = dict(s)
        _th = _ths_by_code.get(s.get("code", ""), {})
        if _th.get("zhangfu") is not None:
            _merged["zhangfu"] = _th["zhangfu"]
        elif _merged.get("change_pct"):
            # V16.4.0: getharden 不返回涨幅——用腾讯批量 change_pct 兜底（否则策略 01 恒 0 命中）
            # V16.4.1 修复: 原 L1880 残留 `_merged["zhangfu"] = _th["zhangfu"]` 复制粘贴错误
            # —— elif 分支中 _th 必无 zhangfu, 裸索引必然 KeyError('zhangfu') 导致 val 全崩
            _merged["zhangfu"] = _safe_float(_merged.get("change_pct"))
        if _th.get("reason"):
            _merged["reason_tag"] = _th["reason"]
        if _th.get("huanshou") is not None:
            _merged["turnover_pct"] = _th["huanshou"]
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
    L(f"  ⏱ 全市场数据加载完成 @ {datetime.now().strftime('%H.%M.%S')}")

    all_selections = {}

    # V7.5: 策略阶段 Semaphore(3) 控制并发
    _strategy_sem = asyncio.Semaphore(3)

    async def _run_sync_strategy(name, func, *args):
        # V15.5.11: 完成即打印耗时（运行时 profiling，替代逐策略单测）
        _st = time.time()
        async with _strategy_sem:
            if inspect.iscoroutinefunction(func):
                _r = await func(*args)
            else:
                _r = await asyncio.to_thread(func, *args)
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
    #   - 稳定性曲线（Jaccard）：11/12/17 在 200-300 提升最大
    #   - 推荐差异化：02/04/06/13/22→100, 11/12/17/19→200, 05→300, 20→1000
    # V16.3 O27: 全市场化改造——
    #   - 19/20/21/22 纯 ZHB 内存策略 → 全市场（毫秒级零成本；20 回测 top1000 仅覆盖
    #     19.9% 命中，80% 控盘股在池外，全市场 136 只全覆盖）
    #   - 02/05/06 预筛全市场（函数内 ZHB 内存先行）→ 趋势强度排序取 top300 逐股确认
    #     （V14.3.2 曾推荐 02→100/05→300；现按趋势优先，弱趋势小市值不再被 mcap 截断）
    _top_n_large = 300   # 形态类（02/05/06）— O27: 趋势强度排序后 top300 逐股确认
    _top_n_medium = 200  # 财务/筹码类（11/12/17）— 回测推荐 200（稳定性提升 26%）
    _top_n_small = 100   # 周线/核心（02/04）— V14.3.2 推荐（O27 后 02 改走 _top_n_large）
    _top_n_pure = 200    # 纯 ZHB 类（19/22）— 回测推荐 200（O27 后 19/21 全市场，保留备用）
    _top_n_fund = 1000   # 主力资金（20）— O27 后全市场（回测 top1000 覆盖率仅 19.9%）

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
        ("策略07【金叉共振】", strategy_07_golden_cross, (hot_pool,)),
        ("策略08【政策驱动】", strategy_08_policy_driven, (all_stocks, hot_pool)),
        ("策略09【日历效应】", strategy_09_calendar_rotation, ()),
        ("策略10【逆向白马】", strategy_10_contrarian_value,
         (sorted(all_stocks, key=lambda x: x.get("mcap_yi", 999999), reverse=True)[:_top_n_medium], _top_n_medium)),
        ("策略11【筹码集中】", strategy_11_holder_concentration, (all_stocks, _top_n_medium)),  # 200（稳定性提升 26%）
        ("策略12【量价信号】", strategy_12_divergence_warning, (all_stocks, _top_n_medium)),  # 200
        ("策略13【高股息】", strategy_13_dividend_yield, (all_stocks,)),  # 内部 300→100
        ("策略14【流动性王】", strategy_14_liquidity_king, (top_liquidity_pool,)),
        ("策略15【政策热度】", strategy_15_policy_heatmap, (all_stocks, hot_pool)),
        ("策略16【北向Top】", strategy_16_northbound_top, (all_stocks, _top_n_medium)),  # V14.3.2: 150→200
        ("策略17【龙虎榜】", strategy_17_longhu_activity, (all_stocks, today_str)),
        ("策略18【52周低位】", strategy_18_52w_position, (all_stocks,)),  # O27: 全市场（纯内存毫秒级）
        ("策略19【主力资金】", strategy_19_main_fund_ratio, (all_stocks,)),  # O27: 全市场（回测 top1000 覆盖率仅 19.9%）
        ("策略20【量能三连击】", strategy_20_volume_acceleration, (all_stocks,)),  # O27: 全市场（内存 O(1)）
        ("策略21【资金动量】", strategy_21_capital_momentum, (all_stocks,)),  # V11.5: 纯ZHB数据
        ("策略22【业绩预增】", strategy_22_yjyg, (all_stocks,)),  # V17.0: 东财业绩预告(datacenter 单股查询)
        ("策略23【盈利预期】", strategy_23_earnings_expect, (all_stocks,)),  # V17.0: 本机 ProfitForecast+股东户数
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
    _sfmt = {"策略01":"01 龙回头", "策略02":"02 周线多头", "策略03":"03 量价齐升", "策略04":"04 核心打折", "策略05":"05 W底形态", "策略06":"06 红三兵", "策略07":"07 金叉共振", "策略08":"08 政策驱动", "策略09":"09 日历效应", "策略10":"10 逆向白马", "策略11":"11 筹码集中", "策略12":"12 量价信号", "策略13":"13 高股息", "策略14":"14 流动性王", "策略15":"15 政策热度", "策略16":"16 北向Top", "策略17":"17 龙虎榜", "策略18":"18 52周低位", "策略19":"19 主力资金", "策略20":"20 量能三连击", "策略21":"21 资金动量", "策略22":"22 业绩预增", "策略23":"23 盈利预期"}

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
    """21 策略全市场发现引擎 Runner"""

    def __init__(self):
        super().__init__("get_val_report", "val", "23 策略全市场发现引擎")

    def execute_pipeline(self) -> str:
        ts = self.report_ts  # V17.0 R1: 基类统一口径(%Y%m%d_%H%M)
        op = os.path.join(self.args.output, f"get_val_report_{ts}.md")
        try:
            print("  ⏱ 预计运行 3-7 分钟（asyncio 异步模式）", flush=True)
        except UnicodeEncodeError:
            print("  [INFO] 预计运行 3-7 分钟（asyncio 异步模式）", flush=True)

        try:
            asyncio.run(run_discovery_async(op))
            # V16.3 O39 修复: "已保存"前验证文件真实存在（原无条件打印——失败时假成功）
            if os.path.exists(op):
                try:
                    print(f"  ✅ 已保存: {op}", flush=True)
                except UnicodeEncodeError:
                    print(f"  [OK] 已保存: {op}", flush=True)
            else:
                try:
                    print(f"  ⚠️ 报告未生成（文件不存在: {op}）", flush=True)
                except UnicodeEncodeError:
                    print(f"  [WARN] 报告未生成: {op}", flush=True)
        except Exception as e:
            try:
                print(f"  ⚠️ asyncio 失败，退回同步模式: {e}", flush=True)
            except UnicodeEncodeError:
                print(f"  [WARN] asyncio 失败，退回同步模式: {e}", flush=True)
            try:
                run_discovery(op)
                try:
                    print(f"  ✅ 已保存: {op}", flush=True)
                except UnicodeEncodeError:
                    print(f"  [OK] 已保存: {op}", flush=True)
            except Exception as e2:
                try:
                    print(f"❌ 报告生成失败: {e2}", flush=True)
                except UnicodeEncodeError:
                    print(f"[FAIL] 报告生成失败: {e2}", flush=True)
                raise e2
        return op

    def upload_reports(self, drive: Any, folder_id: str, output_file: str) -> None:
        self.upload_single_report(drive, folder_id, output_file)


if __name__ == "__main__":
    runner = ValReportRunner()
    runner.run()

#!/usr/bin/env python3
"""
get_val_report.py — 18 策略全市场发现引擎
方法论驱动的 A 股选股脚本，从全市场发现可操作标的。
每策略精选 TOP 5，生成含具体数值推理的报告。

版本信息:
    V15.2  2026-07-28 - V15.2 性能优化：22 策略去重循环 get_pe_ttm_async，从 _snapshot dict O(1) 读；ths_hot_reason 失败降级；L1 缓存上限 5000→10000
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
  - 策略16【政策热度图谱】（同花顺 reason tags + 政策关键词 量化热度）
  - 策略17【北向Top30】（东财机构持仓结构分析，高北向持仓+加仓标的）
  - 策略18【龙虎榜席位活跃度】（全市场龙虎榜扫描 + 游资席位识别 + 机构买卖评分）
  - 从 stock_common 导入统一龙虎榜函数 / 统一板块判断 / 涨停判断

Usage:
    python get_val_report.py                  # 全量 18 策略
    python get_val_report.py -o ./reports     # 指定输出目录
    python get_val_report.py --no-upload      # 跳过 GD 上传
"""

import time, os
from datetime import date, datetime, timedelta  # V16.1: 策略13 TTM 股息率需 timedelta
from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor

from gd_uploader import init_gd, upload_type_reports, cleanup_gd_proxy
from tdx_client import (tdx_get_security_bars,
                         tdx_get_weekly_bars,
                         tdx_get_board_list,
                         tdx_get_all_stocks,
                         tdx_get_finance_roe, cleanup_tdx)  # V16.0: 移除 tdx_get_fund_flow（改统一层）
from stock_common import (_safe_float, _request_with_retry, _quick_request, UA,
                           JP_URL,
                           _load_settings, _load_strategy_config, get_holder_structure,
                           holder_change, is_limit_up, is_limit_down,
                           get_recent_dragon_tiger, get_dragon_tiger_board,
                           parse_args as common_parse_args, BaseReportRunner,
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
from data_provider import (get_market_snapshot_async,
                           get_turnover_pct_async,
                           get_main_net_buy_async,
                           get_main_net_buy)  # V16.1: 策略20 用同步版（原缺失导入）
import asyncio
import inspect

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ═══════════════════════════════════════════════════
# 数据获取层
# ═══════════════════════════════════════════════════

# ─── 百度股市通 K线（返回全量行） ───

def baidu_kline_last(code: str) -> Dict[str, Any]:
    """V4: 最新K线+MA → tdx_client 适配器（本地计算MA5/10/20）"""
    keys, rows = tdx_get_security_bars(code, count=120)
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
        def _sma(d, n):
            if len(d) < n: return 0
            return sum(d[-n:]) / n
        res['ma5avgprice'] = str(round(_sma(closes, 5), 2))
        res['ma10avgprice'] = str(round(_sma(closes, 10), 2))
        res['ma20avgprice'] = str(round(_sma(closes, 20), 2))
    return res


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
                def sma(data, n):
                    if len(data) < n: return None
                    return sum(data[-n:]) / n
                ma5 = sma(closes, 5)
                ma10 = sma(closes, 10)
                ma20 = sma(closes, 20)
                ma30 = sma(closes, 30)
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
    keys, rows = tdx_get_security_bars(code, count=600)
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

    def sma(data, n):
        if len(data) < n: return None
        return sum(data[-n:]) / n

    ma5 = sma(closes, 5)
    ma10 = sma(closes, 10)
    ma20 = sma(closes, 20)
    ma30 = sma(closes, 30)
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
    """同花顺当日强势股归因 — 返回 list[dict]"""
    if date_str is None: date_str = date.today().strftime("%Y-%m-%d")
    url = f"http://zx.10jqka.com.cn/event/api/getharden/date/{date_str}/orderby/date/orderway/desc/charset/GBK/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0 Safari/537.36"}
    try:
        r = _quick_request(url, headers=headers, timeout=10)
        if r is None: return []
        data = r.json()
        if str(data.get("errocode", 0)) != "0": return []
        return data.get("data") or []
    except Exception as _e:
        _debug_log(f"val eastmoney_stock_news: {_e}")
        return []


# ─── 行业板块排名 ───

def industry_comparison(top_n=20):
    """V4: 全行业排名 → TDX board_list 替代 push2"""
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
_A_STOCK_PREFIXES = (
    "00",  # 深市主板/中小板
    "30",  # 深市创业板
    "60",  # 沪市主板
    "68",  # 沪市科创板
    "92",  # 北交所（920xxx 段 334 只 4.2%）
)


def _is_a_stock(code: str) -> bool:
    """V15.1: 判断是否为 A 股（沪深主板/创业板/科创板/北交所）。

    过滤掉的非 A 股：ETF（15/51/56/58 等）、LOF（50）、可转债（11/12/18）、
    国债/债券 ETF、封闭式基金等。
    """
    if not code or len(code) != 6 or not code.isdigit():
        return False
    return code[:2] in _A_STOCK_PREFIXES

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


def _top5_sorted(candidates, key_func, reverse=True):
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
        from tdx_client import tdx_get_security_bars
        _k, _r = tdx_get_security_bars(code, count=count)
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
    return _top5_sorted(result, lambda x: x["score"])


# ─── 策略02: 周线级别多均线多头排列 ───

def strategy_02_weekly_ma(stocks, top_n=None):
    _sc = _load_strategy_config()
    if top_n is None:
        top_n = _sc.get("strategy", {}).get("top_n_cap", 200)
    _cluster_cap = _sc.get("strategy", {}).get("cluster_spread_cap", 5.0)
    candidates = sorted(stocks, key=lambda x: x.get("mcap_yi", 0), reverse=True)[:top_n]
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
    return _top5_sorted(result, lambda x: x["score"])


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
        keys, rows = tdx_get_security_bars(code, count=100)
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
    return _top5_sorted(result, lambda x: x["score"])


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
    from data_provider import get_canonical_stock_data
    for s in big_caps:
        code = s["code"]
        try:
            # 同步函数走 to_thread，避免阻塞 asyncio 事件循环
            cdata = await asyncio.to_thread(get_canonical_stock_data, code)
        except Exception:
            continue
        pe = _safe_float(cdata.pe_ttm)
        if pe <= 0 or pe > _pe_high: continue
        pb = _safe_float(cdata.pb)
        if pb > _pb_high: continue
        mcap = _safe_float(cdata.mcap_yi)
        price = _safe_float(cdata.price)
        if mcap <= 0 or price <= 0: continue
        total_shares = int(mcap * 1e8 / price)
        pe_data = estimate_pe_percentile(code, s.get("price", 0), total_shares)
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
    return _top5_sorted(result, lambda x: x["score"])


# ─── 策略05: W底形态 ───

def strategy_05_double_bottom(stocks, top_n=None):
    _sc = _load_strategy_config()
    _wbottom_depth = _sc.get("strategy", {}).get("wbottom_depth_cap", 5.0)
    if top_n is None:
        top_n = _sc.get("strategy", {}).get("top_n_cap", 200)
    _box_factor = _sc.get("strategy", {}).get("box_break_factor", 1.01)
    _vol_inc_factor = _sc.get("strategy", {}).get("volume_increase_factor", 1.2)
    candidates = sorted(stocks, key=lambda x: x.get("mcap_yi", 0), reverse=True)[:top_n]
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
    return _top5_sorted(result, lambda x: x["score"])


# ─── 策略06: 红三兵 ───

def strategy_06_three_soldiers(stocks, top_n=500):
    candidates = sorted(stocks, key=lambda x: x.get("mcap_yi", 0), reverse=True)[:top_n]
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
    return _top5_sorted(result, lambda x: x["score"])


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
    return _top5_sorted(result, lambda x: x["score"])


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
            return _top5_sorted(_ths_result, lambda x: x["score"])

    # Fallback: 新闻 NLP 关键词匹配
    news_list = cls_telegraph(30)
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
    from data_provider import get_canonical_stock_data
    for s in candidates[:200]:
        code = s["code"]
        try:
            # 同步函数走 to_thread，避免阻塞 asyncio 事件循环
            cdata = await asyncio.to_thread(get_canonical_stock_data, code)
        except Exception:
            continue
        pe_ttm = _safe_float(cdata.pe_ttm)
        if not pe_ttm > 0: continue
        mcap_yi = _safe_float(cdata.mcap_yi)
        reason = (
            f"今日新闻出现政策关键词: {', '.join(found_policy[:3])}，"
            f"市值{mcap_yi:.1f}亿（中小盘弹性标的），"
            f"PE={pe_ttm:.1f}x，攻守兼备"
        )
        result.append({"code": code, "name": s.get("name", "") or cdata.name, "reason": reason,
                       "score": -pe_ttm})
    return _top5_sorted(result, lambda x: x["score"])


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
        leader_code = ind.get("leader", "")
        if not leader_code or leader_code in seen_codes: continue
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
    return _top5_sorted(result, lambda x: x["score"])


# ─── 策略10: 逆向白马流 ───

async def strategy_10_contrarian_value(stocks, top_n=300):
    _sc = _load_strategy_config()
    _roe_good = _sc.get("fundamental", {}).get("roe_good", 15.0)
    candidates = [s for s in stocks if s.get("mcap_yi", 0) >= 50][:top_n]
    result = []
    for s in candidates:
        code = s["code"]
        # V4: TDX get_finance_info 替代 push2 MAINFINADATA（单期ROE ≥ 15%）
        roe = tdx_get_finance_roe(code)
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
    return _top5_sorted(result, lambda x: x["score"])


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
    return _top5_sorted(result, lambda x: x["score"])


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
    return _top5_sorted(result, lambda x: x["score"])


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
    return _top5_sorted(result, lambda x: x["score"])


# ─── 策略15: 头部资金风向标 ───

def strategy_15_liquidity_king(top_liquidity_pool):
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
            reason = (
                f"位列全市场前5%核心流动性池，今日成交额{_safe_float(s.get('amount', 0) or s.get('amount_yi', 0))/10000:.2f}亿！"
                f"成交量异常放大至5日均量的{vol_ratio:.1f}倍，"
                "主力资金高位接盘或强力破局，流动性溢价显著"
            )
            result.append({
                "code": code, "name": s.get("name", ""), "reason": reason,
                "score": _safe_float(s.get('amount', 0) or s.get('amount_yi', 0)) * vol_ratio / 10000,
            })
    return _top5_sorted(result, lambda x: x["score"])


# ─── 策略16: 政策热度图谱（V7.5 新增） ───

def strategy_16_policy_heatmap(all_stocks, hot_pool):
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

    return _top5_sorted(results, lambda x: x["score"])


# ─── 策略17: 北向持仓 Top30 异动（V7.5 新增） ───

def strategy_17_northbound_top(all_stocks, top_n=200):
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

    return _top5_sorted(results, lambda x: x["score"])


# ─── 策略18: 龙虎榜席位活跃度（V7.5 新增） ───

def strategy_18_longhu_activity(all_stocks, today_str=None, top_n=200):
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

            dept_tag_str = "、".join(hot_dept_names) if hot_dept_names else "无著名游资席位"
            reason = (
                f"近{list_days}天上榜，最近一次 {last_date}，"
                f"机构净买 {inst_net:+.1f}万（买 {inst_buy:+.1f}万 / 卖 {inst_sell:+.1f}万），"
                f"席位标签: {dept_tag_str}，"
                f"期间合计净买 {recent_net_sum:+.1f}万，"
                f"平均换手率 {avg_turnover:.1f}%，"
                f"市值 {mcap:.0f}亿，今日涨跌 {change_pct:+.1f}%"
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

    return _top5_sorted(results, lambda x: x["score"])

# ─── 策略19: 52周位置百分位（V10.3新增）──

def strategy_19_52w_position(stocks, top_n=200):
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
    return _top5_sorted(result, lambda x: x["score"])


# ─── 策略20: 主力资金占比因子（V10.3新增）──

def strategy_20_main_fund_ratio(stocks, top_n=1000):
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
        amount_wan = _safe_float(s.get("amount", 0))
        if not amount_wan or amount_wan == 0:
            continue
        main_amount = 0.0
        data_source = ""
        if use_zhb:
            # V15.5.14: tdxstat2 全市场快照 O(1) 读（main_net_buy_amount）
            _s2 = _zhb_stat2.get(code, {})
            main_amount = _safe_float(_s2.get("main_net_buy_amount", 0))
            if main_amount:
                data_source = "ZHB(T-1)"
            else:
                try:
                    zhb_main = get_main_net_buy(code)
                except Exception as _e:
                    _debug_log(f"val strategy20 get_main_net_buy {code}: {_e}")
                    zhb_main = None
                if zhb_main:
                    main_amount = _safe_float(zhb_main.get("main_net_buy_amount", 0))
                    data_source = "ZHB(T-1)"
        if not main_amount or main_amount <= 0:
            # V16.0: 统一走 data_provider.get_main_net_buy（内部 ZHB→HTTP 优先级），
            # 替代直连 tdx_get_fund_flow（函数名误导，实为东财 HTTP）
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
            f"主力资金占比={fund_ratio:.2f}%（主力控盘度高），"
            f"主力净流入{main_amount:+.0f}万元（{data_source}），"
            f"总成交额{amount_wan:.0f}万元"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": fund_ratio})
    return _top5_sorted(result, lambda x: x["score"])


# ═══════════════════════════════════════════════════════════════
# V11.5 新增：策略21（量能三连击）+ 策略22（资金动量）
# 基于 data_provider.get_volume_acceleration / get_capital_momentum
# 纯 ZHB 数据，无 HTTP fallback
# ═══════════════════════════════════════════════════════════════

def strategy_21_volume_acceleration(stocks, top_n=200):
    """V11.5: 量能三连击策略（纯 ZHB 数据）。

    V16.1: 字段契约对齐 get_volume_acceleration 真实返回
    （amount_t_1/amount_t_2/amount_t_3/is_accelerating/acceleration_ratio）。
    原 vol_ratio_5d/turnover_5d 字段不存在 → 策略恒空。
    """
    from data_provider import get_volume_acceleration
    result = []
    for s in stocks:
        code = s["code"]
        try:
            va = get_volume_acceleration(code)
        except Exception as _e:
            _debug_log(f"val strategy21 get_volume_acceleration {code}: {_e}")
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
    return _top5_sorted(result, lambda x: x["score"])


def strategy_22_capital_momentum(stocks):
    """V11.5: 资金动量策略（纯 ZHB 数据）。

    V16.1: 字段契约对齐 get_capital_momentum 真实返回
    （net_buy_t_1/net_buy_t_2/momentum/momentum_ratio/signal）。
    原 main_net_ratio/streak_days 字段不存在 → 策略恒空。
    """
    from data_provider import get_capital_momentum
    result = []
    for s in stocks:
        code = s["code"]
        try:
            cm = get_capital_momentum(code)
        except Exception as _e:
            _debug_log(f"val strategy22 get_capital_momentum {code}: {_e}")
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
            f"资金动量: 主力净流入动量比={momentum_ratio:.2f}，"
            f"动量值={momentum:.0f}（信号: {signal or '看多'}）"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason, "score": score})
    return _top5_sorted(result, lambda x: x["score"])


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
    理由：进程级缓存本就只活在本进程内，新进程必空；同进程内 22 策略
    共享同一份 L1 缓存是性能优化（22 次复用 vs 22 次从 L2 重读）。
    """
    _t_now = datetime.now()
    today_str = _t_now.strftime("%Y-%m-%d")
    lines = []
    def L(s=""): lines.append(s)

    L("─" * 85)
    L(f"  A 股策略发现报告  [{today_str} {_t_now.strftime('%H:%M:%S')}]")
    L("─" * 85)
    L("  市场: A 股 | 策略: 21 | 引擎: asyncio | 并发: 3")
    L("-" * 85)
    L("  预热: 加载市场数据 & 策略配置…")

    cfg = _load_settings()
    _cfg = cfg or {}

    # V11.5: 使用 data_provider 统一数据中心层
    # 优先ZHB全量快照，失败fallback到TDX全市场，保持混合分层架构
    _zhb_date, _zhb_fresh = "", False
    all_stocks = []
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
            if is_bypass:
                L(f"  ⚡ 探测到非盘中时段 ({m_status})，自动旁路实时行情，直接复用 ZHB 昨收快照基准！")
                _price_map = {}
            else:
                # V15.5.9: 全市场腾讯批量预加载（不封 IP，含 mcap_yi/pe_ttm/turnover_pct）
                # 替代原逐股 get_em_quote_full（push2 连接级风控 + 1.5s 限流 → 7957 次卡死数小时）
                _tencent_map: Dict[str, Dict[str, Any]] = {}
                try:
                    from tdx_client import _tencent_batch_fallback
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
                # V15.2 P0 修复: price_map 中 price 可能为 0（push2 部分股票未返回），
                # 此时从 _price_map 其它字段（amount_wan/change_pct）判断是否有任何 push2 数据
                _rt_data = _price_map.get(_code, {})
                if not _price and _rt_data.get("amount_wan"):
                    # price 缺失但 amount_wan 存在 → 实际有 push2 数据
                    _price = 0  # 保持 0，mcap 后续用 push2 fallback 算
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
                    _real_chg = _safe_float(_rt.get("change_pct", 0))
                    if _real_chg:
                        _stock["change_pct"] = _real_chg
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
            return "\n".join(filter(None, lines))
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
        if _th.get("reason"):
            _merged["reason_tag"] = _th["reason"]
        if _th.get("huanshou") is not None:
            _merged["turnover_pct"] = _th["huanshou"]
        hot_pool.append(_merged)

    top_liquidity_pool = sorted(all_stocks, key=lambda x: _safe_float(x.get("amount", 0) or x.get("amount_yi", 0)), reverse=True)[:500]

    L(f"  ✅ 全市场: {len(all_stocks)} | 热点池(同花顺强势): {len(hot_pool)} | 流动性Top500: {len(top_liquidity_pool)}")
    L(f"  ⏱ 全市场数据加载完成 @ {datetime.now().strftime('%H:%M:%S')}")

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
    _top_n_large = 300   # 形态类（05 W底/06 红三兵）— 回测推荐 300
    _top_n_medium = 200  # 财务/筹码类（11/12/17）— 回测推荐 200（稳定性提升 26%）
    _top_n_small = 100   # 周线/核心（02/04）— 回测推荐 100（已经饱和）
    _top_n_pure = 200    # 纯 ZHB 类（19/22）— 回测推荐 200
    _top_n_fund = 1000   # 主力资金（20）— 条件严苛，需 1000 才饱和

    # 策略注册（1-20 为同步函数，用 Semaphore 控制并发）
    # V14.3.2: 基于 4 天 ZHB 回测（docs/backtest_v1432/）差异化 top_n
    _strategy_defs = [
        ("策略01【龙回头】", strategy_01_longhuitou, (hot_pool, today_str)),
        ("策略02【周线多头】", strategy_02_weekly_ma, (all_stocks, _top_n_small)),  # V14.3.2: 200→100
        ("策略03【量价齐升】", strategy_03_volume_breakout, (hot_pool,)),
        ("策略04【核心打折】", strategy_04_core_discount, (all_stocks,)),  # 内部 200
        ("策略05【W底形态】", strategy_05_double_bottom,
         (sorted(all_stocks, key=lambda x: _safe_float(x.get("amount", 0) or x.get("amount_yi", 0)), reverse=True)[:_top_n_large], _top_n_large)),
        ("策略06【红三兵】", strategy_06_three_soldiers,
         (sorted(all_stocks, key=lambda x: _safe_float(x.get("amount", 0) or x.get("amount_yi", 0)), reverse=True)[:_top_n_large], _top_n_large)),
        ("策略07【金叉共振】", strategy_07_golden_cross, (hot_pool,)),
        ("策略08【政策驱动】", strategy_08_policy_driven, (all_stocks, hot_pool)),
        ("策略09【日历效应】", strategy_09_calendar_rotation, ()),
        ("策略10【逆向白马】", strategy_10_contrarian_value,
         (sorted(all_stocks, key=lambda x: x.get("mcap_yi", 999999), reverse=True)[:_top_n_medium], _top_n_medium)),
        ("策略11【筹码集中】", strategy_11_holder_concentration, (all_stocks, _top_n_medium)),  # 200（稳定性提升 26%）
        ("策略12【量价信号】", strategy_12_divergence_warning, (all_stocks, _top_n_medium)),  # 200
        ("策略13【高股息】", strategy_13_dividend_yield, (all_stocks,)),  # 内部 300→100
        ("策略15【流动性王】", strategy_15_liquidity_king, (top_liquidity_pool,)),
        ("策略16【政策热度】", strategy_16_policy_heatmap, (all_stocks, hot_pool)),
        ("策略17【北向Top】", strategy_17_northbound_top, (all_stocks, _top_n_medium)),  # V14.3.2: 150→200
        ("策略18【龙虎榜】", strategy_18_longhu_activity, (all_stocks, today_str)),
        ("策略19【52周低位】", strategy_19_52w_position,
         (sorted(all_stocks, key=lambda x: _safe_float(x.get("amount", 0) or x.get("amount_yi", 0)), reverse=True)[:_top_n_pure], _top_n_pure)),  # V14.3.2: 收缩到 200
        ("策略20【主力资金】", strategy_20_main_fund_ratio,
         (sorted(all_stocks, key=lambda x: _safe_float(x.get("amount", 0) or x.get("amount_yi", 0)), reverse=True)[:_top_n_fund], _top_n_fund)),  # V14.3.2: 1000
        ("策略21【量能三连击】", strategy_21_volume_acceleration,
         (sorted(all_stocks, key=lambda x: _safe_float(x.get("amount", 0) or x.get("amount_yi", 0)), reverse=True)[:_top_n_pure], _top_n_pure)),  # V14.3.2: 200
        ("策略22【资金动量】", strategy_22_capital_momentum, (all_stocks,)),  # V11.5: 纯ZHB数据
    ]

    try:
        print("  ▶ 21 策略并行扫描（asyncio 模式，并发 3）…", flush=True)
    except UnicodeEncodeError:
        print("  >> 21 策略并行扫描（asyncio 模式，并发 3）…", flush=True)
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
        elif isinstance(_raw, list):
            _r = _raw
        all_selections[_name] = _r
        _status = f"异常({_err})" if _err else f"完成({len(_r)}只)"
        try:
            print(f"  {_name}... {_status}", flush=True)
        except UnicodeEncodeError:
            print(f"  {_name}... {_status}".encode('ascii', errors='replace').decode('ascii'), flush=True)
    
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
            from zhb_client import get_zhb
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
                    _em_names = get_em_batch_quotes(_still_missing)
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
    L("  扫描结果汇总: 20个策略共产出 " + str(sum(len(v) for v in all_selections.values())) + " 次选择")
    L("─" * 85)

    _sfmt = {"策略01":"01 龙回头战法","策略02":"02 周线多头","策略03":"03 量价齐升","策略04":"04 核心打折","策略05":"05 W底形态","策略06":"06 红三兵","策略07":"07 均线金叉","策略08":"08 政策驱动","策略09":"09 日历效应","策略10":"10 逆向白马","策略11":"11 筹码集中","策略12":"12 量价信号","策略13":"13 红利低波","策略14":"14 股债平衡","策略15":"15 头部风向标","策略16":"16 政策热度","策略17":"17 北向Top","策略18":"18 龙虎榜活跃度","策略19":"19 52周低位","策略20":"20 主力资金"}

    for _st_name in _names_full:
        items = all_selections.get(_st_name, [])
        _k = _st_name[:4] if len(_st_name) >= 4 else _st_name
        _title = _sfmt.get(_k, _st_name)
        L("\n" + "-"*85)
        L(f"[{_title}]")
        if items:
            for idx2, item in enumerate(items[:5], 1):
                L(f"  #{idx2}  {item.get('name', '')} ({item.get('code', '')})")
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
            L(f"  {_nm}({code}): {cnt}个策略")
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
    output = "\n".join(filter(None, lines))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
    return output


class ValReportRunner(BaseReportRunner):
    """18 策略全市场发现引擎 Runner"""

    def __init__(self):
        super().__init__("get_val_report", "val", "18 策略全市场发现引擎")

    def execute_pipeline(self) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        op = os.path.join(self.args.output, f"get_val_report_{ts}.txt")
        try:
            print("  ⏱ 预计运行 3-7 分钟（asyncio 异步模式）", flush=True)
        except UnicodeEncodeError:
            print("  [INFO] 预计运行 3-7 分钟（asyncio 异步模式）", flush=True)

        try:
            asyncio.run(run_discovery_async(op))
            try:
                print(f"  ✅ 已保存: {op}", flush=True)
            except UnicodeEncodeError:
                print(f"  [OK] 已保存: {op}", flush=True)
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


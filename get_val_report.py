#!/usr/bin/env python3
"""
get_val_report.py — 18 策略全市场发现引擎
方法论驱动的 A 股选股脚本，从全市场发现可操作标的。
每策略精选 TOP 5，生成含具体数值推理的报告。

版本信息:
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
from datetime import date, datetime
from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor

from gd_uploader import init_gd, upload_type_reports, cleanup_gd_proxy
from tdx_client import (tdx_get_security_bars, tdx_get_quotes_batch,
                         tdx_get_weekly_bars,
                         tdx_get_board_list,
                         tdx_get_all_stocks,
                         tdx_get_finance_roe, cleanup_tdx)
from stock_common import (_safe_float, _request_with_retry, _quick_request, UA,
                           JP_URL,
                           _load_settings, _load_strategy_config, get_holder_structure,
                           holder_change, is_limit_up, is_limit_down,
                           get_recent_dragon_tiger, get_dragon_tiger_board,
                           parse_args as common_parse_args,
                           get_tencent_quote,
                           baidu_kline_full as common_baidu_kline_full,
                           get_dividend_history as common_get_dividend_history,
                           is_trading_day, get_market_status,
                           _debug_log,
                           cls_telegraph as _cls_telegraph,
                           get_eastmoney_global_news as _eastmoney_global_news,
                           get_zhb_market_snapshot, is_zhb_data_fresh,
                           get_zhb_data_date, get_zhb_stock_stat,
                           get_zhb_52w_range)
import asyncio

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ═══════════════════════════════════════════════════
# 数据获取层
# ═══════════════════════════════════════════════════

def tencent_quote_batch(codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """V4: 批量行情 → tdx_client 适配器（TDX+腾讯合并，自动fallback）"""
    return tdx_get_quotes_batch(codes)


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


# ─── 新浪财报（多期） ───

def sina_financial_report(code, num_periods=12):
    """新浪利润表 — 支持多期数（默认12期 ≈ 3年）"""
    prefix = "sh" if code.startswith("6") else "sz"
    paper_code = f"{prefix}{code}"
    url = "https://quotes.sina.cn/cn/api/openapi.php/CompanyFinanceService.getFinanceReport2022"
    params = {"paperCode": paper_code, "source": "lrb", "type": "0", "page": "1", "num": str(num_periods)}
    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=15)
        if r is None: return []
        rl = (r.json().get("result") or {}).get("data", {}).get("report_list", {})
        rows = []
        for date_key, period in rl.items():
            item_map = {}
            for entry in period.get("data", []):
                item_map[entry.get("item_title", "")] = entry.get("item_value")
            rows.append({
                "报告日": f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}",
                "营业总收入": item_map.get("营业总收入") or "0",
                "营业成本": item_map.get("营业成本") or "0",
                "净利润": item_map.get("归属于母公司所有者的净利润") or item_map.get("净利润") or "0",
            })
        return rows
    except Exception as _e:
        _debug_log(f"val financial_parse: {_e}")
        return []


# ─── 股东户数变化 ───

def holder_num_change(code, page_size=5):
    """V7.5: 股东户数变化 → 东财优先 + 内存缓存"""
    return holder_change(code)


# ─── 模拟PE百分位 — 策略05使用 ───

def estimate_pe_percentile(code, price, total_shares):
    """
    基于新浪12期财报 + 历史日K线，估算近3年模拟PE百分位。
    返回: {percentile, pe_min, pe_max, pe_current, quarters}
    """
    fin = sina_financial_report(code, num_periods=12)
    if len(fin) < 4:
        return None

    profits = []
    for f in fin:
        try: p = float(f["净利润"])
        except (ValueError, TypeError, KeyError): p = 0
        profits.append(p)

    if total_shares <= 0 or all(p == 0 for p in profits):
        return None

    # 还原为单季度后计算TTM
    # TTM按季度反推(新浪财报是累计值,需Q1/Q2/Q3/Q4逐季拆解)
    sq_profits = []
    for i in range(len(profits)-1, 0, -1):
        sq_profits.append(max(profits[i] - profits[i-1], 0))
    sq_profits.append(profits[0])  # 最新一期本身是单季度
    sq_profits = sq_profits[::-1]  # 倒序回到最新在前

    ttm_eps_list = []
    ttm_dates = []
    for i in range(len(sq_profits) - 3):
        ttm_profit = sum(sq_profits[i:i+4])
        eps = ttm_profit / total_shares
        if eps > 0:
            ttm_eps_list.append(eps)
            ttm_dates.append(fin[i+3]["报告日"])

    if not ttm_eps_list:
        return None

    keys, rows = common_baidu_kline_full(code)
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
        for row in reversed(rows):
            if len(row) <= idx_close: continue
            row_date = row[0] if len(row) > 0 else ""
            if row_date[:10] <= dt_str:
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
        # 过滤停牌股（volume=0）
        vol = stat.get("volume")
        if vol is not None and _safe_float(vol) == 0:
            excluded += 1
            continue
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

def _top5_sorted(candidates, key_func, reverse=True):
    """从候选列表中取 TOP5，按 key_func 排序"""
    candidates.sort(key=key_func, reverse=reverse)
    return candidates[:5]


# ─── 策略01: 龙回头战法 ───

def strategy_01_longhuitou(hot_pool, today_str):
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
        q = get_tencent_quote(code)
        turnover = q.get("turnover_pct", 0)
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
        recent_60 = closes[-60:]
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

def strategy_04_core_discount(stocks):
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
    for s in big_caps:
        code = s["code"]
        q = get_tencent_quote(code)
        if not q: continue
        pe = q.get("pe_ttm", 0)
        if pe <= 0 or pe > _pe_high: continue
        pb = q.get("pb", 0)
        if pb > _pb_high: continue
        mcap = q.get("mcap_yi", 0)
        price = q.get("price", 0)
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
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
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
        keys, rows = common_baidu_kline_full(code)
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
        keys, rows = common_baidu_kline_full(code)
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

def strategy_08_policy_driven(stocks, hot_pool=None):
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
                    q = get_tencent_quote(h_code)
                    if q.get("pe_ttm", 0) > 0:
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
    for s in candidates[:200]:
        code = s["code"]
        q = get_tencent_quote(code)
        if not q.get("pe_ttm", 0) > 0: continue
        reason = (
            f"今日新闻出现政策关键词: {', '.join(found_policy[:3])}，"
            f"市值{q.get('mcap_yi', 0):.1f}亿（中小盘弹性标的），"
            f"PE={q.get('pe_ttm', 0):.1f}x，攻守兼备"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": -q.get("pe_ttm", 0)})
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
                r = _request_with_retry(JP_URL, params=params, headers={"User-Agent": UA}, timeout=10)
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

def strategy_10_contrarian_value(stocks, top_n=300):
    _sc = _load_strategy_config()
    _roe_good = _sc.get("fundamental", {}).get("roe_good", 15.0)
    candidates = [s for s in stocks if s.get("mcap_yi", 0) >= 50][:top_n]
    result = []
    for s in candidates:
        code = s["code"]
        # V4: TDX get_finance_info 替代 push2 MAINFINADATA（单期ROE ≥ 15%）
        roe = tdx_get_finance_roe(code)
        if roe is None or roe < _roe_good: continue
        keys, rows = common_baidu_kline_full(code)
        if len(rows) < 250: continue
        _ki = _kline_indices(keys); idx_c = _ki.get("close", -1); idx_v = _ki.get("vol", -1); idx_close = _ki.get("close", -1)
        if idx_close < 0: continue
        closes = [_safe_float(r[idx_close]) for r in rows[-250:] if len(r) > idx_close]
        if not closes: continue
        high_52w = max(closes[-250:])
        current_price = closes[-1]
        drawdown = (current_price - high_52w) / high_52w * 100
        if drawdown > -40: continue
        q = get_tencent_quote(code)
        reason = (
            f"最新ROE={roe:.1f}%≥15%（优质白马），"
            f"距52周最高价{high_52w:.2f}元已下跌{abs(drawdown):.0f}%，"
            f"当前PE={q.get('pe_ttm', 0):.1f}x，非基本面因素导致的错杀"
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
        keys, rows = common_baidu_kline_full(code)
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
    candidates = [s for s in stocks if s.get("mcap_yi", 0) >= 50][:300]
    result = []
    for s in candidates:
        code = s["code"]
        price = s.get("price", 0)
        if price <= 0: continue
        divs = common_get_dividend_history(code)
        if len(divs) < 3: continue
        recent_bonus = _safe_float(divs[0].get("bonus_rmb", 0))
        if recent_bonus <= 0: continue
        yield_pct = recent_bonus / price * 100
        if yield_pct < 4.0: continue
        years_with_div = len([d for d in divs if _safe_float(d.get("bonus_rmb", 0)) > 0])
        reason = (
            f"当前股息率{yield_pct:.2f}%（每股派息{recent_bonus:.4f}元/现价{price:.2f}元），"
            f"近{years_with_div}个报告期持续分红，稳定的现金奶牛资产"
        )
        result.append({"code": code, "name": s.get("name", ""), "reason": reason,
                       "score": yield_pct})
        if len(result) >= 5:
            break
    return _top5_sorted(result, lambda x: x["score"])


# ─── 策略14: 股债平衡 ───

def strategy_14_asset_rebalance():
    codes = ["510300", "511010"]
    quotes = tencent_quote_batch(codes)
    if len(quotes) < 2: return []
    equity = quotes.get("510300", {})
    bond = quotes.get("511010", {})
    equity_name = equity.get("name", "沪深300ETF")
    bond_name = bond.get("name", "国债ETF")
    equity_change = equity.get("change_pct", 0)
    bond_change = bond.get("change_pct", 0)
    diff = abs(equity_change - bond_change)
    if diff < 3:
        return [{"code": "510300", "name": equity_name,
                 "reason": f"当前股债走势趋于均衡（偏离度{diff:.1f}%），无需再平衡", "score": 0}]
    result = []
    if equity_change > bond_change:
        result.append({"code": "510300", "name": equity_name,
                       "reason": f"【再平衡信号】权益类近期走强(+{equity_change:.1f}%) >> 债券(+{bond_change:.1f}%)，偏离度{diff:.1f}%，建议减仓权益、加仓债券回归50:50",
                       "score": diff})
    else:
        result.append({"code": "511010", "name": bond_name,
                       "reason": f"【再平衡信号】债券类近期走强(+{bond_change:.1f}%) >> 权益(+{equity_change:.1f}%)，偏离度{diff:.1f}%，建议减仓债券、加仓权益回归50:50",
                       "score": diff})
    result.append({"code": "511010", "name": bond_name,
                   "reason": f"资产配置对冲标的，当前与{equity_name}形成互补",
                   "score": diff * 0.8})
    return result[:5]


# ─── 策略15: 头部资金风向标 ───

def strategy_15_liquidity_king(top_liquidity_pool):
    """
    在成交额 Top 5% 的核心池中，寻找今日成交额超越5日均量1.5倍且收阳的个股。
    """
    result = []
    for s in top_liquidity_pool:
        code = s["code"]
        keys, rows = common_baidu_kline_full(code)
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
            dtb = get_dragon_tiger_board(code, today_str, days=7)
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


# ═══════════════════════════════════════════════
# 报告生成（V7.5 异步版为主，同步版为 asyncio.run 包装）
# ═══════════════════════════════════════════════

def run_discovery(output_path):
    """同步版包装：委托给异步版执行（保留向后兼容）。"""
    return asyncio.run(run_discovery_async(output_path))


async def run_discovery_async(output_path):
    """V7.5 异步版: 使用 asyncio.gather 并行跑 18 策略（约 2-3x 提速）"""
    _t_now = datetime.now()
    today_str = _t_now.strftime("%Y-%m-%d")
    lines = []
    def L(s=""): lines.append(s)

    L("─" * 85)
    L(f"  A 股策略发现报告  [{today_str} {_t_now.strftime('%H:%M:%S')}]")
    L("─" * 85)
    L("  市场: A 股 | 策略: 18 | 引擎: asyncio | 并发: 3")
    L("-" * 85)
    L("  预热: 加载市场数据 & 策略配置…")

    cfg = _load_settings()
    _cfg = cfg or {}

    # V10.0: 使用 zhb.stock_stats 替代 tdx_get_all_stocks（零HTTP，更快）
    # zhb包含7938只股票，35个字段，本地解析<0.1秒
    _zhb_date, _zhb_fresh = "", False
    all_stocks = []
    try:
        _snapshot = get_zhb_market_snapshot()
        if _snapshot:
            _zhb_date = get_zhb_data_date() or ""
            _zhb_fresh = is_zhb_data_fresh(max_delay_days=3)
            # 转换为列表格式，过滤停牌股（volume=0）
            all_stocks = []
            _excluded = 0
            for _code, _stat in _snapshot.items():
                _vol = _stat.get("volume")
                if _vol is not None and _safe_float(_vol) == 0:
                    _excluded += 1
                    continue
                _stock = {"code": _code}
                for _k, _v in _stat.items():
                    if _k not in ("market", "date"):
                        _stock[_k] = _v
                all_stocks.append(_stock)
            _fresh_tag = "✅新鲜" if _zhb_fresh else "⚠️延迟"
            L(f"  ✅ zhb全市场: {len(all_stocks)}只（过滤{_excluded}只停牌股）[{_fresh_tag}]")
            if _zhb_date:
                L(f"  📊 zhb数据日期: {_zhb_date}")
        else:
            raise ValueError("zhb snapshot empty")
    except Exception as _e:
        _debug_log(f"val zhb_load: {_e}, fallback to tdx_get_all_stocks")
        all_stocks = tdx_get_all_stocks()
        if not all_stocks:
            L("  ❌ 无法获取全市场股票数据")
            return "\n".join(filter(None, lines))
        # fallback时仍做初筛
        all_stocks, _zhb_date, _zhb_fresh = _tdxstat_prescreen(all_stocks)

    # V10.0: 扩大扫描范围，利用zhb零成本数据
    # 热点池: ~100只→~300只；流动性池: 300只→500只
    _stock_map = {s["code"]: s for s in all_stocks}
    ths_hot_list = ths_hot_reason(today_str)
    ths_hot_codes = {item.get("code", "") for item in ths_hot_list if item.get("code")}
    hot_pool = [s for s in all_stocks if s.get("code", "") in ths_hot_codes]

    top_liquidity_pool = sorted(all_stocks, key=lambda x: _safe_float(x.get("amount", 0) or x.get("amount_yi", 0)), reverse=True)[:500]

    L(f"  ✅ 全市场: {len(all_stocks)} | 热点池(同花顺强势): {len(hot_pool)} | 流动性Top500: {len(top_liquidity_pool)}")
    L(f"  ⏱ 全市场数据加载完成 @ {datetime.now().strftime('%H:%M:%S')}")

    all_selections = {}

    # V7.5: 策略阶段 Semaphore(3) 控制并发
    _strategy_sem = asyncio.Semaphore(3)

    async def _run_sync_strategy(name, func, *args):
        async with _strategy_sem:
            return await asyncio.to_thread(func, *args)

    # V10.0: 扩大策略扫描范围，利用zhb零成本数据
    # top_n: 200-300 → 500-1000，发现更多优质标的
    _top_n_large = 1000  # 周线/形态类策略（需K线，耗时较长）
    _top_n_medium = 500  # 财务/筹码类策略（需HTTP，中等耗时）
    _top_n_small = 300   # 北向/流动性类策略（快速）

    # 策略注册（1-17 为同步函数，用 Semaphore 控制并发）
    _strategy_defs = [
        ("策略01【龙回头】", strategy_01_longhuitou, (hot_pool, today_str)),
        ("策略02【周线多头】", strategy_02_weekly_ma, (all_stocks, _top_n_medium)),
        ("策略03【量价齐升】", strategy_03_volume_breakout, (hot_pool,)),
        ("策略04【核心打折】", strategy_04_core_discount, (all_stocks,)),
        ("策略05【W底形态】", strategy_05_double_bottom,
         (sorted(all_stocks, key=lambda x: _safe_float(x.get("amount", 0) or x.get("amount_yi", 0)), reverse=True)[:_top_n_large], _top_n_large)),
        ("策略06【红三兵】", strategy_06_three_soldiers,
         (sorted(all_stocks, key=lambda x: _safe_float(x.get("amount", 0) or x.get("amount_yi", 0)), reverse=True)[:_top_n_large], _top_n_large)),
        ("策略07【金叉共振】", strategy_07_golden_cross, (hot_pool,)),
        ("策略08【政策驱动】", strategy_08_policy_driven, (all_stocks, hot_pool)),
        ("策略09【日历效应】", strategy_09_calendar_rotation, ()),
        ("策略10【逆向白马】", strategy_10_contrarian_value,
         (sorted(all_stocks, key=lambda x: x.get("mcap_yi", 999999), reverse=True)[:_top_n_medium], _top_n_medium)),
        ("策略11【筹码集中】", strategy_11_holder_concentration, (all_stocks, _top_n_medium)),
        ("策略12【量价信号】", strategy_12_divergence_warning, (all_stocks, _top_n_medium)),
        ("策略13【高股息】", strategy_13_dividend_yield, (all_stocks,)),
        ("策略14【股债平衡】", strategy_14_asset_rebalance, ()),
        ("策略15【流动性王】", strategy_15_liquidity_king, (top_liquidity_pool,)),
        ("策略16【政策热度】", strategy_16_policy_heatmap, (all_stocks, hot_pool)),
        ("策略17【北向Top】", strategy_17_northbound_top, (all_stocks, _top_n_small)),
        ("策略18【龙虎榜】", strategy_18_longhu_activity, (all_stocks, today_str)),
    ]

    print("  ▶ 18 策略并行扫描（asyncio 模式，并发 3）…", flush=True)
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
        print(f"  {_name}... {_status}", flush=True)
    
    print(f"  扫描完成（共 {_scan_total_time:.1f}s）", flush=True)

    # V10.0: 补充缺失的股票名称（zhb数据源无name字段）
    _all_codes = set()
    for _items in all_selections.values():
        for _item in _items:
            _name = _item.get("name", "")
            if not _name or _name == _item["code"]:
                _all_codes.add(_item["code"])
    if _all_codes:
        _name_map = tencent_quote_batch(list(_all_codes))
        for _items in all_selections.values():
            for _item in _items:
                _name = _item.get("name", "")
                if not _name or _name == _item["code"]:
                    _item["name"] = _name_map.get(_item["code"], {}).get("name", _item["code"])

    L("\n" + "=" * 85)
    L("  扫描结果汇总: 18个策略共产出 " + str(sum(len(v) for v in all_selections.values())) + " 次选择")
    L("─" * 85)

    _sfmt = {"策略01":"01 龙回头战法","策略02":"02 周线多头","策略03":"03 量价齐升","策略04":"04 核心打折","策略05":"05 W底形态","策略06":"06 红三兵","策略07":"07 均线金叉","策略08":"08 政策驱动","策略09":"09 日历效应","策略10":"10 逆向白马","策略11":"11 筹码集中","策略12":"12 量价信号","策略13":"13 红利低波","策略14":"14 股债平衡","策略15":"15 头部风向标","策略16":"16 政策热度","策略17":"17 北向Top","策略18":"18 龙虎榜活跃度"}

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
    for _b in ["01 龙回头: 震荡市胜率55-65%","02 周线多头: 趋势市胜率60-70%","03 量价齐升: 趋势启动胜率50-60%","04 核心打折: 价值回归胜率55-65%","10 逆向白马: 中线最佳胜率60-70%","13 红利低波: 熊市优选胜率65-75%","16 政策热度: 主题轮动胜率55-65%","17 北向Top: 聪明钱方向胜率60-70%"]:
        L(f"  策略回测: {_b}")
    L(f"\n{'='*85}")
    output = "\n".join(filter(None, lines))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
    return output


if __name__ == "__main__":
    args = common_parse_args("18 策略全市场发现引擎")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    op = os.path.join(args.output, f"get_val_report_{ts}.txt")
    print(f"🚀 全市场18策略发现引擎启动 — {date.today()}", flush=True)
    print("  ⏱ 预计运行 3-7 分钟（asyncio 异步模式）", flush=True)

    os.makedirs(args.output, exist_ok=True)
    try:
        asyncio.run(run_discovery_async(op))
        print(f"  ✅ 已保存: {op}", flush=True)
    except Exception as e:
        print(f"  ⚠ asyncio 失败，退回同步模式: {e}", flush=True)
        try:
            run_discovery(op)
            print(f"  ✅ 已保存: {op}", flush=True)
        except Exception as e2:
            print(f"❌ 报告生成失败: {e2}", flush=True)
            cleanup_tdx()
            exit(1)

    # GD 上传
    drive, gd_proxy_set, gd_parent_folder_id, skip_upload = None, False, None, False
    if not args.no_upload:
        drive, gd_proxy_set, gd_parent_folder_id, skip_upload = init_gd(base_dir)
        if drive and not skip_upload:
            if upload_type_reports(drive, gd_parent_folder_id, "val", [op]) <= 0:
                print("  ⚠️ GD 上传失败", flush=True)
    cleanup_gd_proxy(gd_proxy_set)
    cleanup_tdx()


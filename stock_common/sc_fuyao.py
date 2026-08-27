"""sc_fuyao.py — 同花顺官方金融数据 REST API（fuyao.aicubes.cn）统一适配器

V16.3.3 新增：官方 REST 通道（字典 §12.8.12c）——Key 交互引导 + 跳过禁用逻辑。

Key 获取优先级：
    1. 环境变量 THS_FUYAO_API_KEY（推荐，CI/长期使用）
    2. 项目根 fuyao_key.txt（交互输入后自动保存，已 gitignore）
    3. 交互式引导（ensure_fuyao_key）——无 Key 时提供两个选项：
       a. 粘贴新 Key → 自动验证（meta/tickers/search）→ 保存 → 继续
       b. 跳过 → 本进程禁用 fuyao（_FUYAO_DISABLED=True），后续调用自动返回 None

协议（字典 §12.8.12c）：
    Base https://fuyao.aicubes.cn，全 GET，头 X-api-key
    成功 = HTTP 200 且 code==0；信封 {code, message, request_id, data}（data.item 数组）
    错误码：4001 限流（调用方退避）；Key 无效 2003
    限流：fuyao.aicubes.cn 已入 sc_network._DOMAIN_LIMITS（500ms/2rps）
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from stock_common.sc_network import _quick_request, _debug_log

# V16.3.3: fuyao 数据缓存（字典 12.15.5 新源充实后——避免每次网络请求消耗 Key 配额/限流）
# V17.0 S8: 删 _fuyao_cached 适配器(与 _kpl_cached 逐字重复)——直接使用规范 cached
try:
    from core.stock_cache import cached, TTL

    _HAS_CACHE = True
except ImportError:  # pragma: no cover
    _HAS_CACHE = False

_logger = logging.getLogger("fuyao_adapter")

_REPO_ROOT = Path(__file__).resolve().parent.parent
_KEY_FILE = _REPO_ROOT / "fuyao_key.txt"

_BASE = "https://fuyao.aicubes.cn"

# 本进程禁用标记（ensure_fuyao_key 选择"跳过"后置 True——后续调用自动返回 None）
_FUYAO_DISABLED = False
# 已缓存的有效 Key
_CACHED_KEY: Optional[str] = None

# 常用端点路径（字典 §12.8.12c——V17.0.5 契约镜像 62 端点，按业务接入优先级）
EP_SNAPSHOT = "/api/a-share/prices/snapshot"
EP_KLINE = "/api/a-share/prices/historical"
EP_VALUATION = "/api/a-share/valuations/snapshot"
EP_LIMIT_UP_LADDER = "/api/a-share/special-data/limit-up-ladder"
EP_HOT_LIST = "/api/a-share/special-data/hot-stock-list"
EP_DRAGON_TIGER = "/api/a-share/special-data/dragon-tiger-list"
EP_TICKER_SEARCH = "/api/meta/tickers/search"
# V17.0.5 新增（契约镜像 docs/verify/fuyao_api_full.md）
EP_AUCTION_SNAP = "/api/a-share/auction/snapshot"
EP_AUCTION_BENCH = "/api/a-share/auction/short-term-benchmark"
EP_LIMIT_UP_POOL = "/api/a-share/special-data/limit-up-pool"
EP_LIMIT_DOWN_POOL = "/api/a-share/special-data/limit-down-pool"
EP_LIMIT_BREAK_POOL = "/api/a-share/special-data/limit-break-pool"
EP_ANOMALY_STOCK = "/api/a-share/special-data/anomaly-analysis-stock"
EP_ANOMALY_LIST = "/api/a-share/special-data/anomaly-analysis-list"
EP_FIN_INDICATORS = "/api/a-share/financials/indicators"
EP_INCOME = "/api/a-share/financials/income-statements"
EP_BALANCE = "/api/a-share/financials/balance-sheets"
EP_CASHFLOW = "/api/a-share/financials/cash-flow-statements"
EP_TRADING_DAYS = "/api/a-share/calendar/trading-days"
EP_ADJ_FACTORS = "/api/a-share/corporate-actions/adjustment-factors"
EP_INDEX_CATALOG = "/api/a-share-index/catalog/ths-index-list"
EP_INDEX_CONSTITUENTS = "/api/a-share-index/constituents/ths-stock-list"
EP_INDEX_SNAPSHOT = "/api/a-share-index/prices/snapshot"
EP_INDEX_HISTORICAL = "/api/a-share-index/prices/historical"


def is_fuyao_enabled() -> bool:
    """fuyao 是否可用（未被跳过且 Key 可解析）。"""
    return not _FUYAO_DISABLED and get_fuyao_key() is not None


def get_fuyao_key() -> Optional[str]:
    """解析 Key：环境变量 → fuyao_key.txt → None。不触发交互。"""
    global _CACHED_KEY
    if _CACHED_KEY:
        return _CACHED_KEY
    env = os.environ.get("THS_FUYAO_API_KEY", "").strip()
    if env:
        _CACHED_KEY = env
        return env
    if _KEY_FILE.is_file():
        k = _KEY_FILE.read_text(encoding="utf-8").strip()
        if k:
            _CACHED_KEY = k
            return k
    return None


def _print_guide() -> None:
    """打印获取 API Key 的指导。"""
    print("=" * 60)
    print("  🔑 同花顺金融数据 API（fuyao）未配置 Key")
    print("=" * 60)
    print("  获取步骤（约 1 分钟）：")
    print("    1. 打开 https://fuyao.aicubes.cn/ ，用同花顺账号登录")
    print("    2. 进入「API Key 管理」页：https://fuyao.aicubes.cn/admin")
    print("    3. 点击「创建 API Key」，填写别名（如 a-stock-data）")
    print("    4. 复制弹出的 Key（形如 sk-fuyao-xxxxxxxx，只显示一次）")
    print("")
    print("  也可设置环境变量 THS_FUYAO_API_KEY 后重启脚本。")
    print("=" * 60)


def _interactive_acquire(stdin: Any = None) -> Optional[str]:
    """交互获取 Key 的核心循环（可注入 stdin 便于测试）。

    返回: 有效 Key / None（跳过）。stdin 缺省 sys.stdin。
    """
    global _FUYAO_DISABLED, _CACHED_KEY
    _print_guide()
    inp = stdin if stdin is not None else sys.stdin
    while True:
        try:
            line = inp.readline() if hasattr(inp, "readline") else input()
            if not line:
                raise EOFError
            choice = line.strip()
        except (EOFError, KeyboardInterrupt):
            choice = "2"
        if choice == "1":
            new_key = input("  粘贴 API Key: ").strip() if stdin is None else inp.readline().strip()
            if not new_key:
                print("  ⚠️ 输入为空，请重试（或选 2 跳过）")
                continue
            if _verify_key(new_key):
                _save_key(new_key)
                _CACHED_KEY = new_key
                print("  ✅ Key 验证通过，已保存到 fuyao_key.txt（gitignore）")
                return new_key
            print("  ❌ Key 验证失败（可能无效或未授权），请检查后重试（或选 2 跳过）")
        elif choice == "2":
            _FUYAO_DISABLED = True
            _debug_log("fuyao: 用户选择跳过——本进程禁用 fuyao 接口")
            print("  ℹ️ 已跳过——本进程后续 fuyao 接口自动返回空（下次运行可再配置）")
            return None
        else:
            print("  ⚠️ 无效选择，请输入 1 或 2")


def ensure_fuyao_key(interactive: bool = True, stdin: Any = None) -> Optional[str]:
    """确保 fuyao Key 可用。

    - 已配置（env/文件）→ 直接返回
    - 未配置且 interactive=True → 打印指导，用户二选一：
        1) 粘贴新 Key（自动验证并保存到 fuyao_key.txt）→ 返回 Key
        2) 跳过 → 本进程禁用 fuyao，返回 None
      （stdin 可注入用于测试；非交互终端无输入时自动跳过，不阻塞）
    - 未配置且 interactive=False → 返回 None（不打扰）
    """
    global _FUYAO_DISABLED, _CACHED_KEY
    if _FUYAO_DISABLED:
        return None
    k = get_fuyao_key()
    if k:
        return k
    if not interactive:
        return None
    _inp = stdin if stdin is not None else sys.stdin
    if _inp is None or not hasattr(_inp, "isatty") or not _inp.isatty():
        # 非交互终端（子进程管道/CI）——尝试读管道输入；无输入则自动跳过，不阻塞
        if stdin is None:
            try:
                import msvcrt  # Windows 控制台按键检测

                if not msvcrt.kbhit():
                    _debug_log("fuyao: 非交互终端且无输入，自动跳过 Key 引导")
                    _FUYAO_DISABLED = True
                    return None
            except Exception:
                _debug_log("fuyao: 非交互终端，自动跳过 Key 引导")
                _FUYAO_DISABLED = True
                return None
    return _interactive_acquire(stdin=_inp)


def _save_key(key: str) -> None:
    """保存 Key 到项目根 fuyao_key.txt（已 gitignore）。"""
    try:
        _KEY_FILE.write_text(key.strip(), encoding="utf-8")
    except Exception as _e:
        _debug_log(f"fuyao: 保存 Key 失败: {_e}")


def _verify_key(key: str) -> bool:
    """验证 Key：meta/tickers/search 一次请求（code==0 即有效）。"""
    try:
        resp = _fuyao_raw("/api/meta/tickers/search", {"q": "600519", "limit": 1}, key=key)
        return resp is not None and resp.get("code") == 0
    except Exception as _e:
        _debug_log(f"fuyao: Key 验证异常: {_e}")
        return False


def _fuyao_raw(
    path: str, params: Optional[Dict[str, Any]] = None, key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """统一请求（走 sc_network._quick_request 域限流）。失败返回 None。"""
    k = key or get_fuyao_key()
    if not k:
        return None
    try:
        headers = {"X-api-key": k, "User-Agent": "Mozilla/5.0"}
        r = _quick_request(_BASE + path, params=params, headers=headers, timeout=15)
        if r is None:
            _debug_log(f"fuyao: 请求被限流/拒绝 {path}")
            return None
        if r.status_code != 200:
            _debug_log(f"fuyao: HTTP {r.status_code} {path}")
            return None
        d = r.json()
        if d.get("code") != 0:
            _debug_log(f"fuyao: code={d.get('code')} msg={d.get('message')} {path}")
            if d.get("code") in (2001, 2003):
                _debug_log("fuyao: Key 无效——请重新配置（删除 fuyao_key.txt 或更新环境变量）")
            return d
        return d
    except Exception as _e:
        _debug_log(f"fuyao: 请求异常 {path}: {_e}")
        return None


def _items(d: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """提取信封 data.item（兼容 dict 嵌套）。"""
    if not d:
        return []
    data = d.get("data") or {}
    if isinstance(data, list):
        return data
    items = data.get("item") or []
    return items if isinstance(items, list) else []


def fuyao_to_thscode(code: str) -> str:
    """项目 6 位代码 → thscode。

    ⚠️ 北交所必须先判（V17.0.5 实测 bug："920118" 被 '9' 分支吃成 .SH → 服务端
    1002 Unknown thscode 且**整批拒绝**；与 V16.4.1 ulist secids 同类顺序坑）。
    """
    code = code.strip()
    if code.endswith((".SH", ".SZ", ".BJ")):
        return code
    if code.startswith(("92", "8", "4", "43", "83", "87")):
        return f"{code}.BJ"
    if code.startswith(("6", "9", "5")):
        return f"{code}.SH"
    return f"{code}.SZ"


@cached("fuyao_snapshot")
def get_fuyao_snapshot(codes: List[str]) -> List[Dict[str, Any]]:
    """行情快照（EP_SNAPSHOT）。无 Key/已跳过 → 空列表。"""
    if not codes:
        return []
    ths = ",".join(fuyao_to_thscode(c) for c in codes)
    return _items(_fuyao_raw(EP_SNAPSHOT, {"thscodes": ths}))


@cached("fuyao_valuation")
def get_fuyao_valuation(codes: List[str]) -> List[Dict[str, Any]]:
    """估值快照（pe_ttm/pe_mrq/pb_mrq/ps_ttm/pcf_ttm）。"""
    if not codes:
        return []
    ths = ",".join(fuyao_to_thscode(c) for c in codes)
    return _items(_fuyao_raw(EP_VALUATION, {"thscodes": ths}))


def get_fuyao_kline(
    thscode: str,
    interval: str = "1d",
    start_ms: Optional[int] = None,
    end_ms: Optional[int] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """历史 K线（EP_KLINE）。interval: 1d/1w/1m/5m/15m/30m/60m。"""
    params: Dict[str, Any] = {
        "thscode": fuyao_to_thscode(thscode),
        "interval": interval,
        "limit": limit,
    }
    if start_ms:
        params["start"] = start_ms
    if end_ms:
        params["end"] = end_ms
    return _items(_fuyao_raw(EP_KLINE, params))


@cached("fuyao_ladder", trading_day=True)
def get_fuyao_limit_up_ladder() -> Optional[Dict[str, Any]]:
    """涨停梯队（date + boards 连板分类——独有结构，字典 §12.8.12c）。"""
    d = _fuyao_raw(EP_LIMIT_UP_LADDER)
    return (d.get("data") or {}) if d and d.get("code") == 0 else None


def get_fuyao_hot_list(period: str = "hour") -> List[Dict[str, Any]]:
    """热股榜（period: hour/day/week）。"""
    return _items(_fuyao_raw(EP_HOT_LIST, {"period": period}))


def get_fuyao_dragon_tiger(trade_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """龙虎榜（trade_date 可选 YYYY-MM-DD，盘后可回查）。"""
    params = {}
    if trade_date:
        params["trade_date"] = trade_date
    return _items(_fuyao_raw(EP_DRAGON_TIGER, params))


# ═══════════════════════════════════════════════════════════════
# V17.0.5 新增端点（契约镜像 docs/verify/fuyao_api_full.md §12.8.12c）
# 盘后可用：财务/日历/复权/特色池/竞价终态——thsdk TCP 盘后关闭(-6)的替代通道
# ═══════════════════════════════════════════════════════════════


@cached("fuyao_auction")
def get_fuyao_auction_snapshot(codes: List[str], stage: str = "final") -> List[Dict[str, Any]]:
    """集合竞价快照（stage: live=盘中实时 / final=终态盘后可查）。

    字段: auction_price/auction_pct/auction_volume/auction_amount/auction_unmatched(未匹配量)/
          auction_turnover_pct/auction_yesterday_ratio_pct(昨量比)/auction_volume_ratio(竞价量比)/
          pre_close_price/open_price/last_price/float_market_cap——对照 ZHB tdxstat2 竞价族。
    """
    if not codes:
        return []
    ths = ",".join(fuyao_to_thscode(c) for c in codes)
    return _items(_fuyao_raw(EP_AUCTION_SNAP, {"thscodes": ths, "stage": stage}))


def get_fuyao_auction_benchmark(date: Optional[str] = None) -> List[Dict[str, Any]]:
    """短线风向标竞价基准（date=YYYY-MM-DD；tags[]: "高开"/"放量"等——同花顺独家分类）。"""
    params = {"date": date} if date else {}
    return _items(_fuyao_raw(EP_AUCTION_BENCH, params))


def get_fuyao_limit_pool(
    kind: str = "up", page: int = 1, size: int = 100, date_ms: Optional[int] = None,
    sort_field: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """涨跌停/炸板池（kind: up/down/break）。返回 data 全量（含 pagination/item[]）。

    date_ms: 交易日零点毫秒戳——**任意交易日盘后回查**(东财 push2ex 仅当日)；
    up 池 sort_field 白名单: last_price/continue_day_cnt/seal_money/limit_up_time。
    up: seal_money/max_seal_money(封单双口径,元)/limit_up_reason/continue_day_text/cnt；
    down: first/last_limit_time；break: open_times(开板次数)。
    """
    ep = {"up": EP_LIMIT_UP_POOL, "down": EP_LIMIT_DOWN_POOL, "break": EP_LIMIT_BREAK_POOL}.get(kind)
    if not ep:
        return None
    params: Dict[str, Any] = {"page": page, "size": size}
    if date_ms:
        params["date_ms"] = date_ms
    if sort_field:
        params["sort_field"] = sort_field
    d = _fuyao_raw(ep, params)
    return (d.get("data") or {}) if d and d.get("code") == 0 else None


@cached("fuyao_seal_map", trading_day=True)
def get_fuyao_seal_map() -> Dict[str, Dict[str, Any]]:
    """当日涨停池 → {ticker: item} 映射（sht 封单衰减率数据源；trading_day 缓存——全市场一次请求）。

    item 含 seal_money(当前封单,元)/max_seal_money(峰值封单,元)/continue_day_cnt/limit_up_reason。
    盘中=当日实时封单；盘后/周末自动回退最近完成交易日(date_ms 参数)。
    """
    d = get_fuyao_limit_pool(kind="up", page=1, size=200)
    items = (d or {}).get("item") or []
    if not items:
        # 周末/节假日：服务端按"当前自然日"返空 → 回退最近已完成工作日
        try:
            import datetime

            _d = datetime.date.today()
            while _d.weekday() >= 5:
                _d -= datetime.timedelta(days=1)
            date_ms = int(datetime.datetime.combine(_d, datetime.time()).timestamp() * 1000)
            d = get_fuyao_limit_pool(kind="up", page=1, size=200, date_ms=date_ms)
            items = (d or {}).get("item") or []
        except Exception as _e:
            _debug_log(f"fuyao seal_map 回退查询失败: {_e}")
    return {str(it.get("ticker")): it for it in items if it.get("ticker")}


def get_fuyao_seal_info(code: str) -> Optional[Dict[str, Any]]:
    """单只股票当日封单信息（非涨停股→None）。返回 {seal_money, max_seal_money,
    seal_decay_ratio(封单衰减率=current/max, 越低=烂板), continue_day_cnt, limit_up_reason}。
    单位: 元。"""
    it = get_fuyao_seal_map().get(str(code).strip())
    if not it:
        return None
    cur = fnum_local(it.get("seal_money"))
    mx = fnum_local(it.get("max_seal_money"))
    decay = None
    if cur is not None and mx and mx > 0:
        decay = round(cur / mx, 4)
    return {
        "seal_money": cur,
        "max_seal_money": mx,
        "seal_decay_ratio": decay,
        "continue_day_cnt": it.get("continue_day_cnt"),
        "limit_up_reason": it.get("limit_up_reason") or None,
    }


def get_fuyao_anomaly(code: Optional[str] = None) -> List[Dict[str, Any]]:
    """个股异动原因（AI 分析文本+keyword_list+tag_name——独有；code=None 查列表）。"""
    if code:
        return _items(_fuyao_raw(EP_ANOMALY_STOCK, {"thscodes": fuyao_to_thscode(code)}))
    return _items(_fuyao_raw(EP_ANOMALY_LIST))


@cached("fuyao_indicators", trading_day=True)
def get_fuyao_fin_indicators(thscode: str, report: str) -> Optional[Dict[str, Any]]:
    """五类财务指标（report=YYYY-N 季报制，盘后可查；trading_day 缓存——报告期数据稳定）。

    ⭐ index_weighted_avg_roe(ROE)/index_deduct_weighted_avg_roe(扣非ROE)/total_assets_net_ratio(ROA)
    官方口径——tx[65]/tx[66] 对撞终判源。返回 {ability: {index_id: value}} 展平结构。
    ⚠️ 上游契约偏差: 实际返回 calculate_* 前缀 id；中报(yyyy-2)入库滞后于披露日(5003)。
    """
    d = _fuyao_raw(EP_FIN_INDICATORS, {"thscode": fuyao_to_thscode(thscode), "report": report})
    if not d or d.get("code") != 0:
        return None
    data = d.get("data") or {}
    out: Dict[str, Dict[str, Any]] = {}
    for ab in data.get("abilities") or []:
        ability = ab.get("ability") or ""
        out[ability] = {
            (ind.get("index_id") or ""): ind.get("value")
            for ind in (ab.get("indicators") or [])
            if ind.get("index_id")
        }
    return out


def get_fuyao_financials(
    kind: str, thscode: str, limit: int = 4, report: Optional[str] = None,
    period: str = "quarterly",
) -> List[Dict[str, Any]]:
    """三大报表（kind: income/balance/cashflow；limit 期数或 report 指定单期）。

    V17.0.7 修复: 上游契约要求必传 `period`(annual/quarterly)——原实现缺失导致
    code=1001 "Missing required parameter: period", 恒返回空列表(潜伏 bug,
    本次 fuyao TTM 兜底接入时实测发现)。
    """
    ep = {"income": EP_INCOME, "balance": EP_BALANCE, "cashflow": EP_CASHFLOW}.get(kind)
    if not ep:
        return []
    params: Dict[str, Any] = {
        "thscode": fuyao_to_thscode(thscode),
        "limit": limit,
        "period": period,
    }
    if report:
        params["report"] = report
    return _items(_fuyao_raw(ep, params))


def get_fuyao_trading_days(start: Optional[str] = None, end: Optional[str] = None) -> List[Dict[str, Any]]:
    """交易日序列（date_ms/date）。"""
    params: Dict[str, Any] = {}
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    return _items(_fuyao_raw(EP_TRADING_DAYS, params))


def get_fuyao_adjustment_factors(thscode: str) -> List[Dict[str, Any]]:
    """复权因子事件表（ticker/ex_date_ms/dividend_per_share/per_share_bonus）。"""
    return _items(_fuyao_raw(EP_ADJ_FACTORS, {"thscode": fuyao_to_thscode(thscode)}))


def get_fuyao_index_catalog(index_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """同花顺指数目录（行业/概念板块清单——THS 板块体系入口）。"""
    params: Dict[str, Any] = {}
    if index_type:
        params["type"] = index_type
    return _items(_fuyao_raw(EP_INDEX_CATALOG, params))


def get_fuyao_index_constituents(ths_index_code: str) -> List[Dict[str, Any]]:
    """同花顺指数成分股（thscode/ticker/name）。"""
    return _items(_fuyao_raw(EP_INDEX_CONSTITUENTS, {"thscode": ths_index_code}))


def get_fuyao_index_snapshot(codes: List[str]) -> List[Dict[str, Any]]:
    """指数行情快照（11 字段同股票快照口径）。"""
    if not codes:
        return []
    ths = ",".join(c if "." in c else fuyao_to_thscode(c) for c in codes)
    return _items(_fuyao_raw(EP_INDEX_SNAPSHOT, {"thscodes": ths}))


# ═══════════════════════════════════════════════════════════════
# V17.0.5 基金域（lng/med 机构行为侧证）——契约见 verify/fuyao_api_full.md
# ═══════════════════════════════════════════════════════════════

EP_FUND_HOLDINGS = "/api/fund/portfolio/holdings"
EP_FUND_PROFILE = "/api/fund/profile/detail"

# 自选基金清单（gitignore；缺失→侧证功能静默跳过零请求）
FUND_WATCH_PATH = _REPO_ROOT / "credentials" / "fund_watch.json"


@cached("fuyao_fund_holdings", trading_day=True)
def get_fuyao_fund_holdings(fund_thscode: str, fund_type: str = "otc") -> Optional[Dict[str, Any]]:
    """基金重仓持仓（定期披露，非实时；trading_day 缓存——批量 lng/med 防 N×M 重复请求）。返回 data 全量或 None。

    item[]: thscode/ticker/stock_name/hold_ratio/asset_type/position_capital/
            period_increase_rate_pct/investment_rank/end_date_ms；
    汇总: total_stock_ratio_pct/main_industry/concentration_ratio/turnover_rate_pct。
    """
    d = _fuyao_raw(EP_FUND_HOLDINGS, {"fund_type": fund_type, "thscode": fund_thscode})
    return (d.get("data") or {}) if d and d.get("code") == 0 else None


def get_fuyao_fund_profile(fund_thscode: str, fund_type: str = "otc") -> Optional[Dict[str, Any]]:
    """基金基本资料（成立/规模/经理/费率）。"""
    d = _fuyao_raw(EP_FUND_PROFILE, {"fund_type": fund_type, "thscode": fund_thscode})
    return (d.get("data") or {}) if d and d.get("code") == 0 else None


def load_fund_watch() -> List[Dict[str, Any]]:
    """读取自选基金清单。缺失/格式错 → []。

    格式: {"funds": [{"thscode": "025480.OF", "fund_type": "otc", "alias": "可选别名"}]}
    （模板见 credentials/fund_watch.example.json）
    """
    try:
        if FUND_WATCH_PATH.is_file():
            cfg = json.loads(FUND_WATCH_PATH.read_text(encoding="utf-8"))
            funds = cfg.get("funds") or []
            return [f for f in funds if isinstance(f, dict) and f.get("thscode")]
    except Exception as _e:
        _debug_log(f"fuyao: fund_watch.json 读取失败: {_e}")
    return []


def get_fund_watch_evidence(stock_code: str, max_funds: int = 8) -> Optional[Dict[str, Any]]:
    """lng/med 机构行为侧证：自选基金是否重仓目标股票（配置门控，无清单→None 零请求）。

    返回 {"held": [...], "not_held": ["别名(code)"], "checked": N}；
    held 元素: alias/thscode/hold_ratio/investment_rank/period_increase_rate_pct/
               fund_stock_pct(基金股票仓位)/main_industry/concentration_ratio。
    """
    watch = load_fund_watch()
    if not watch:
        return None
    stock_code = stock_code.strip()
    held: List[Dict[str, Any]] = []
    not_held: List[str] = []
    for f in watch[:max_funds]:
        ftype = f.get("fund_type") or ("exchange" if f["thscode"].endswith((".SH", ".SZ")) else "otc")
        data = get_fuyao_fund_holdings(f["thscode"], ftype)
        if not data:
            continue
        alias = f.get("alias") or f["thscode"]
        items = data.get("item") or []
        hit = next((it for it in items if str(it.get("ticker")) == stock_code), None)
        if hit:
            held.append({
                "alias": alias,
                "thscode": f["thscode"],
                "stock_name": hit.get("stock_name"),
                "hold_ratio": fnum_local(hit.get("hold_ratio")),
                "investment_rank": hit.get("investment_rank"),
                "period_increase_rate_pct": fnum_local(hit.get("period_increase_rate_pct")),
                "end_date_ms": hit.get("end_date_ms"),
                "fund_stock_pct": fnum_local(data.get("stock_ratio_pct")),
                "main_industry": data.get("main_industry"),
                "concentration_ratio": fnum_local(data.get("concentration_ratio")),
            })
        else:
            not_held.append(alias)
    return {"held": held, "not_held": not_held, "checked": len(held) + len(not_held)}


def fnum_local(v: Any) -> Optional[float]:
    try:
        if v in (None, "", "-"):
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    # 自检：Key 状态 + 一次真实查询（不打印 Key）
    k = ensure_fuyao_key()
    if k:
        print(
            "Key 状态: 已配置（来源:",
            "环境变量" if os.environ.get("THS_FUYAO_API_KEY") else "fuyao_key.txt",
            ")",
        )
        snap = get_fuyao_snapshot(["600519"])
        if snap:
            print(f"实测行情快照: 茅台 last_price={snap[0].get('last_price')}")
        else:
            print("实测行情快照: 空（检查 Key/网络）")
    else:
        print("Key 状态: 未配置或已跳过")

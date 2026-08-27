#!/usr/bin/env python3
"""
data_provider.py — 统一数据中心层 - V11.5正式启用

版本日期：2026-07-28 (V15.2)
   - V15.2: P0 崩溃修复 - get_canonical_stock_data 中 board 变量初始化；12 个 zhb_data 函数补 valid_if；tdx_get_quote_full 重构为 ZHB→TDX→HTTP
   - V15.1: industry 字段改用 TDX boards；get_amount_wan 优先级 ZHB→腾讯→TDX；启用 change_30d 字段
   - V15.0: 标准化数据合约 CanonicalStockData + ZHB 时空路由矩阵 + 熔断静默降级
   - V14.2: ZHB 数据集深度集成 - profile.dat/concept_chain/neednote/xgsg/brkseat/special_tags
          新增 get_stock_basic_info_from_zhb / get_concept_from_zhb /
          get_new_share_calendar_from_zhb / get_special_tags_from_zhb
   - V14.0: is_workday() 修复由上游 stock_calendar 提供；ANTI_POISON_DEVIATION_THRESHOLD 标记废弃
   - V13.x: 字段路由简化 + sc_schema 元数据层
   - V12.6: REQUIRES_REALTIME_HTTP / ZHB_SUFFICIENT 字段分类

核心架构设计：
  - ZHB优先原则：所有能从ZHB获取的数据，优先使用ZHB本地快照
  - 实时类数据 → 盘中TDX(或腾讯)优先，盘前/盘后优先ZHB（延迟1-2交易日）
  - T-1类数据 → 优先ZHB本地读取，失败fallback到API
  - 静态/财务数据 → 优先ZHB本地基础库，失败fallback到腾讯HTTP
  - 市值动态计算：总股本(本地静态) × 实时价格(API)

ZHB时间体系说明：
  - ZHB文件次日更新机制：今日运行脚本，获取的是昨日(或上一交易日)的数据
  - 例如：7月17日运行 → zhb_20260716（7月16日数据）
  - 非交易日运行：获取最近一个交易日的数据
  - ZHB中的"基准日" = ZHB文件名日期
  - amount/main_net_buy_amount: 基准日数据
  - amount_1d/main_net_buy_amount_1d: 基准日前一交易日数据
  - amount_2d: 基准日前两交易日数据

接口优先级原则（按字段TDX支持情况分级）：
  - 实时字段（price/change_pct/amount）：ZHB(盘后)→TDX(盘中)→腾讯(fallback)
    * TDX TCP原生支持这些字段，真正高效
    * tdx_get_quote_full内部已含缓存+腾讯兜底补强
  - 估值字段（pe_ttm/pb/turnover_pct）：ZHB→腾讯
    * TDX TCP不返回这些字段，无需TDX中间层
  - 股息率：ZHB only
    * TDX和腾讯都不直接返回，ZHB有完整数据
  - 量能/资金因子（get_volume_acceleration/get_capital_momentum）：纯ZHB数据
    * 无需实时T数据，仅使用ZHB内部的amount/amount_1d/amount_2d等字段

核心特性：
  - 全函数缓存装饰器（基于 stock_cache，按字段变化频率分级TTL）
  - 交易状态感知（盘前/盘中/盘后自动切换数据源策略）
  - 同步/异步双版本接口
  - ZHB全量数据预取优化（减少重复调用）
  - 按TDX支持情况分级的fallback机制
  - 量能三连击因子和资金动量加速因子（纯ZHB数据，时间维度完全对齐）

TTL分级策略：
  - 实时层（price/change_pct/amount）：30分钟 + 交易日模式
  - 日变层（pe_ttm/pb/turnover_pct/main_net_buy/streak_days）：24小时 + 交易日模式
  - 周变层（52w_range）：7天
  - 季度层（total_shares/industry）：90天
  - 月变层（dividend_yield）：30天
"""

from typing import Any, Dict, Optional, List
import math
from datetime import datetime, date, timedelta  # timedelta 供 _get_trading_date_offset 使用（M14 注释修正）

from core.stock_cache import cached, TTL, make_valid_if  # V15.2: 强化 valid_if
from stock_common.sc_network import _fallback_logger


def _debug_log(msg: str) -> None:
    _fallback_logger.debug(msg)


def _safe_float(v) -> float:
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


# ─────────────────────────────────────────────────────────────
# V16.3.10: 批量行情预取（push2delay ulist——多股单请求全字段）
# 场景：sht 批量 30 只核心行情（现状 30×canonical 逐股）→ 1-2 次请求预取
# 数据源：push2delay ulist.np（延时镜像域，避免 push2 主域风控；300 只/批）
# 命中后 canonical 实时段跳过 TDX/腾讯单股/push2 逐股（rt_quote 已全字段）
# ─────────────────────────────────────────────────────────────
_BATCH_QUOTE_CACHE: Dict[str, Dict[str, Any]] = {}
_BATCH_QUOTE_DATE: str = ""
# V17.0: push2delay 估值/资金流补取进程缓存(当天)——sht 批量 35 只免重复请求
_PD_EXTRA_CACHE: Dict[str, Dict[str, Any]] = {}
_PD_EXTRA_CACHE_DATE: str = ""
# V17.0.7: fuyao 财务 TTM 族兜底进程缓存——键=(code, report_period), 报告期稳定
_FY_TTM_CACHE: Dict[Any, Dict[str, Any]] = {}


def prefetch_quote_batch(codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """批量预取行情（push2delay ulist，300/批），结果缓存到进程内。

    字段映射基于字典 12.9.1 破解表（f2 价/f3 涨跌/f15-18 OHLC/f20-21 市值/
    f51-52 涨跌停/f55 EPS/f71 均价/f84-85 股本/f126 股息率/f162-167 估值/f174-175 52周）。
    """
    global _BATCH_QUOTE_DATE
    from datetime import datetime as _dt

    _today = _dt.now().strftime("%Y%m%d")
    if _BATCH_QUOTE_DATE != _today:
        _BATCH_QUOTE_CACHE.clear()
        _BATCH_QUOTE_DATE = _today

    missing = [c for c in codes if c not in _BATCH_QUOTE_CACHE]
    if not missing:
        return {c: _BATCH_QUOTE_CACHE[c] for c in codes}

    def _mkt(code: str) -> str:
        # V17.0 修复: 92 北交所必须先行(原 9 先于 92 → 920xxx 拼 "1." 沪市 secid 恒失败)
        from stock_common.sc_utils import em_secid_prefix

        return em_secid_prefix(code)

    try:
        from stock_common import _quick_request, _safe_float

        fields = "f2,f3,f4,f5,f6,f8,f12,f14,f15,f16,f17,f18,f20,f21"
        for i in range(0, len(missing), 300):
            chunk = missing[i : i + 300]
            secids = ",".join(_mkt(c) + c for c in chunk)
            r = _quick_request(
                "https://push2delay.eastmoney.com/api/qt/ulist.np/get",
                params={"fltt": "2", "invt": "2", "secids": secids, "fields": fields},
                headers={"Referer": "https://quote.eastmoney.com/"},
                timeout=10,
            )
            if r is None:
                continue
            for item in ((r.json().get("data") or {}).get("diff") or []):
                code = str(item.get("f12", ""))
                if not code:
                    continue

                def _f(key, div=1.0):
                    v = item.get(key)
                    try:
                        return float(v) / div if v not in (None, "-", "") else 0.0
                    except (ValueError, TypeError):
                        return 0.0

                # V16.3.10 实测：ulist 批量接口仅返回行情字段（f2-f21），
                # 估值类（f162 PE/f167 PB/f174-175 52周/f126 股息率）返回 "-"——
                # 与 stock/get 单股接口字段语义不同，PE/PB/52周留待 TDX/腾讯单股补齐
                _BATCH_QUOTE_CACHE[code] = {
                    "price": _f("f2"),
                    "change_pct": _f("f3"),
                    "change_amt": _f("f4"),
                    "volume_hand": _f("f5"),
                    "amount_wan": _f("f6", 1e4),
                    "turnover_pct": _f("f8"),
                    "name": item.get("f14", ""),
                    "high": _f("f15"),
                    "low": _f("f16"),
                    "open": _f("f17"),
                    "prev_close": _f("f18"),
                    "mcap_yi": _f("f20", 1e8),
                    "float_mcap_yi": _f("f21", 1e8),
                }
    except Exception as _e:
        _debug_log(f"prefetch_quote_batch error: {_e}")

    return {c: _BATCH_QUOTE_CACHE[c] for c in codes if c in _BATCH_QUOTE_CACHE}


# V12.6: field routing classification (run-time + field type)
#
# Decision rules:
#   if runtime == pre_market:
#       -> all fields use ZHB
#   elif field in REQUIRES_REALTIME_HTTP:
#       -> HTTP (quote / fund flow)
#   else:
#       -> ZHB (valuation / finance / share / sector)

# V14.2.1: 动态从 sc_schema.FIELD_SPECS 生成（避免重复维护）
# 单一权威源：sc_schema.FIELD_SPECS 的 is_real_time 字段
try:
    from stock_common.sc_schema import list_realtime_http_fields, list_zhb_sufficient_fields

    REQUIRES_REALTIME_HTTP = frozenset(list_realtime_http_fields())
    ZHB_SUFFICIENT = frozenset(list_zhb_sufficient_fields())
except ImportError:
    # Fallback: 如果 sc_schema 不可用（理论上不会发生），用静态定义
    REQUIRES_REALTIME_HTTP = frozenset(
        {
            "price",
            "change_pct",
            "amount",
            "volume",
            "open",
            "high",
            "low",
            "prev_close",
            "change_pct_1d",
            "change_pct_2d",
            "amount_1d",
            "amount_2d",
            "main_net_buy_hands",
            "main_net_buy_hands_1d",
            "main_net_buy_amount",
            "main_net_buy_amount_1d",
        }
    )
    ZHB_SUFFICIENT = frozenset(
        {
            # valuation
            "pe_ttm",
            "pe_dynamic",
            "pb",
            "dividend_yield",
            "turnover_pct",
            # finance
            "net_profit",
            "revenue",
            "roe",
            "eps",
            # share capital
            "total_shares",
            "float_shares",
            "mcap",
            "float_mcap",
            "holder_count",
            # sector
            "industry_code",
            "industry",
            "board",
            "concept",
            # historical change
            "change_5d",
            "change_10d",
            "change_20d",
            "change_30d",
            "change_60d",
            "change_ytd",
            # V17.0.5: tdxstat2 Col[11] 正名——本月至今涨跌幅(基准=上月末收盘)
            "change_mtd",
            "streak_days",
            # 52w / ipo / employees
            "high_52w",
            "low_52w",
            "ipo_price",
            "employee_count",
        }
    )

# V14.2.1: ZHB_SUFFICIENT 已在 try/except 块中通过 sc_schema 动态生成（或 Fallback 静态定义）


def is_realtime_http_field(field_name):
    # V12.6: True means must use HTTP real-time API
    return field_name in REQUIRES_REALTIME_HTTP


def is_zhb_sufficient_field(field_name):
    # V12.6: True means ZHB alone is sufficient
    return field_name in ZHB_SUFFICIENT


# ═══════════════════════════════════════════════════════════════
# V14.2 新增：ZHB 本地数据集获取函数（HTTP 调用减半）
# 数据源：field_dict.md 第三节第 4 小节
# ═══════════════════════════════════════════════════════════════


def get_stock_basic_info_from_zhb(code: str) -> Optional[Dict[str, Any]]:
    """从 ZHB profile.dat 获取股票基本信息（V14.2 新增，替代东财 HTTP）。

    Returns:
        {"code": "600519", "name": "贵州茅台", "source": "zhb"}
        ZHB 数据缺失时返回 None
    """
    try:
        from core.zhb_client import get_stock_name_from_zhb

        name = get_stock_name_from_zhb(code)
        if name:
            return {"code": code, "name": name, "source": "zhb"}
        return None
    except Exception:
        return None


def get_concept_from_zhb(code: str) -> List[str]:
    """从 ZHB tdxchain.cfg 获取股票所属概念/产业链节点（V14.2 新增）。

    Returns:
        概念名称列表（如 ["5G", "白酒", "MSCI"]），ZHB 缺失时返回空列表
    """
    try:
        from core.zhb_client import get_stock_concepts_from_zhb

        return get_stock_concepts_from_zhb(code)
    except Exception:
        return []


def get_new_share_calendar_from_zhb() -> List[Dict[str, Any]]:
    """从 ZHB xgsg.cfg 获取新股申购日历（V14.2 新增，替代东财新股 API）。

    Returns:
        新股列表 [{"code", "name", "issue_date", "ipo_price", ...}],
        ZHB 缺失时返回空列表
    """
    try:
        from core.zhb_client import get_ipo_list

        return get_ipo_list()
    except Exception:
        return []


def get_special_tags_from_zhb() -> Dict[str, List[str]]:
    """从 ZHB pttab.dat 获取特别标签（红筹/AH/概念 等，V14.2 新增）。

    Returns:
        {标签名: [股票代码列表]}，ZHB 缺失时返回空字典
    """
    try:
        from core.zhb_client import get_special_tags_from_zhb as _impl

        return _impl()
    except Exception:
        return {}


def is_zhb_dataset_available() -> bool:
    """检查 ZHB 6 个新数据集是否至少有一个可用（V14.2 新增）。

    Returns:
        True 表示 ZHB 数据已加载且 profile/concept_chain 至少一个有数据
    """
    try:
        from core.zhb_client import get_zhb

        zhb = get_zhb()
        if zhb is None:
            return False
        return bool(zhb.stock_profile) or bool(zhb.concept_chain)
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════
# 统一规范数据接口 (Canonical Data API)
# ═══════════════════════════════════════════════════════════════


def get_canonical_stock_data(code: str, force_realtime: bool = False) -> Any:
    """获取强类型统一规范数据合约对象 (Canonical Stock Data)

    遵从以下重构路由策略：
      1. T+1日盘前 (<09:30) / 假日：100% 走 ZHB 本地提取，零网络开销。
      2. T日盘后 (15:00-24:00): 因当天的 ZHB 包在深夜前未生成，行情与资金流字段强制走 HTTP/TDX 接口获取 T 日实际收盘数据。
      3. T日盘中 (09:30-15:00): 4 大行情/资金流字段走 HTTP/TDX 实时；静态/估值/财务/股本/概念等 30+ 项走 ZHB。
      4. Boundary Validator: 自动对单位、边界及异常值进行清洗与归一化补全。
    """
    from stock_common.sc_schema import CanonicalStockData
    from stock_common.stock_calendar import is_workday
    from core.zhb_client import get_stock_name_from_zhb

    code_str = str(code).zfill(6)
    now = datetime.now()
    is_today_trading = is_workday(now.date())

    t_val = now.hour * 100 + now.minute
    is_pre_market = t_val < 930
    is_post_market = is_today_trading and (t_val >= 1500)
    is_trading_hours = is_today_trading and (930 <= t_val < 1500)

    # 1. 提取 ZHB 本地快照
    zhb_dict = {}
    try:
        from stock_common import get_zhb_single_stock_data

        zhb_dict = get_zhb_single_stock_data(code_str) or {}
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data get_zhb error: {_e}")

    # 判断行情与资金流是否需要走 HTTP / TDX 实时
    need_realtime_quote = force_realtime or is_trading_hours or is_post_market or not zhb_dict

    # V15.4 方案 C: per-field source label
    # 字典 key = 字段名 (e.g. "price", "mcap_yi", "industry")
    # 字典 value = 数据来源标签 (e.g. "realtime:push2", "realtime:tencent", "calculated", "missing")
    field_sources: Dict[str, str] = {}

    # 2. 实时/收盘行情 — V15.4 4 级 fallback 链
    # V16.0: 原 PUSH2_FIELD_MAP（f43/f44→price/high 映射表）已删除——
    # get_em_quote_full 直接返回规范字段名，L3 push2 fallback 直接遍历 em_quote_raw。
    rt_quote: Dict[str, Any] = {}  # 最终的行情 dict (cdata 字段名为 key)
    em_quote_raw: Dict[str, Any] = {}  # push2 原始字段 (f43/f44/...)

    if need_realtime_quote:
        # V16.3.10: 批量预取命中（sht 批量场景 1-2 次请求预取 30 只全字段）——
        # 命中后直接填充 rt_quote，跳过 TDX/腾讯单股/push2 逐股段（price 已有值自动短路）
        _batch_hit = False
        _bq = _BATCH_QUOTE_CACHE.get(code_str)
        if _bq and _bq.get("price"):
            _batch_hit = True
            for _k, _v in _bq.items():
                if _v not in (None, 0, "", "0", "0.0"):
                    rt_quote[_k] = _v
                    field_sources[_k] = "realtime:push2delay:batch"
            _debug_log(f"get_canonical_stock_data batch prefetch hit ({code_str})")
        # L1: TDX 实时——V17.0 修复: prefetch 命中后跳过(原无条件执行, 35 只批量白做 35 次 TCP)
        # V17.0.1c: 批量命中时批量数据无 OHLC(ulist 仅 15 精选字段) → OHLC 缺口补 TDX 快照
        _need_ohlc = not (rt_quote.get("open") and rt_quote.get("high") and rt_quote.get("low"))
        if not _batch_hit or _need_ohlc:
            try:
                from core.tdx_client import tdx_get_quote_full

                _tdx = tdx_get_quote_full(code_str) or {}
                if _batch_hit and _need_ohlc:
                    for _k in ("open", "high", "low", "last_close"):
                        if _tdx.get(_k) not in (None, 0, "", "0", "0.0"):
                            rt_quote[_k] = _tdx[_k]
                            field_sources[_k] = "realtime:tdx"
                elif _tdx.get("price"):
                    rt_quote = _tdx
                    for _k in _tdx:
                        field_sources[_k] = "realtime:tdx"
            except Exception as _e:
                _debug_log(f"get_canonical_stock_data tdx_get_quote_full error: {_e}")

        # L2: 腾讯行情 (V16 端口优先级: 不封 IP，优先于 push2；参考仓库: 腾讯/通达信优先)
        if not rt_quote.get("price"):
            try:
                from stock_common import get_tencent_quote

                _tencent = get_tencent_quote(code_str) or {}
                if _tencent.get("price"):
                    # 腾讯返回的字段名大多与 cdata 一致, 直接 update
                    for _k, _v in _tencent.items():
                        if _v not in (None, 0, '', '0', '0.0'):
                            rt_quote[_k] = _v
                            field_sources[_k] = "realtime:tencent"
                    if rt_quote.get("price"):
                        _debug_log(f"get_canonical_stock_data tencent fallback OK ({code_str})")
            except Exception as _e:
                _debug_log(f"get_canonical_stock_data tencent fallback error ({code_str}): {_e}")

        # L3: 东财最后手段 (V16.3.3 2026-08-10 字典 12.15.5:
        # push2 主域连接级风控实锤——push2delay 镜像域优先（风控独立、114 字段全量、延时 15min 非盘中无影响）；
        # push2 主域仅作最后兜底（风控最严，独有数据才用）
        if not rt_quote.get("price"):
            em_quote_raw: Dict[str, Any] = {}
            try:
                from stock_common.sc_datasource import get_em_quote_full_delay

                em_quote_raw = get_em_quote_full_delay(code_str) or {}
            except Exception as _e:
                _debug_log(f"get_canonical_stock_data push2delay error ({code_str}): {_e}")
            if not em_quote_raw:
                try:
                    from stock_common.sc_datasource import get_em_quote_full

                    em_quote_raw = get_em_quote_full(code_str) or {}
                except Exception as _e:
                    _debug_log(f"get_canonical_stock_data push2 error ({code_str}): {_e}")
            if em_quote_raw:
                # V16.0: get_em_quote_full* 返回的已是规范字段名（price/high/low/...），
                # 直接遍历合并。原 PUSH2_FIELD_MAP 用 f43/f44/... 去 .get() 拿不到值 → push2 兜底从未生效。
                for f_cdata, _v in em_quote_raw.items():
                    if f_cdata in ("name", "industry", "board", "list_date", "data_date"):
                        rt_quote[f_cdata] = _v
                        field_sources[f_cdata] = "realtime:push2delay"
                        continue
                    if _v not in (None, 0, '', '0', '0.0'):
                        # 数值字段转 float（push2 数值可能为字符串）
                        # V16.4.1: 原条件写反——"非字符串才转 float"导致字符串原样保留, 注释意图从未生效
                        try:
                            rt_quote[f_cdata] = float(_v) if isinstance(_v, str) else _v
                        except (ValueError, TypeError):
                            rt_quote[f_cdata] = _v
                        field_sources[f_cdata] = "realtime:push2delay"
                if rt_quote.get("price"):
                    _debug_log(
                        f"get_canonical_stock_data push2delay fallback OK ({code_str}) — {len(rt_quote)} fields mapped"
                    )

    # V16.3.3 (2026-08-10 字典 12.15.5/12.15.6): 腾讯独有/实时估值字段补取——
    # roa(tx66)/盘口价(tx85)/pe_ttm/pb/股息率为腾讯字段；
    # TDX 成功时 L2 fallback 不执行（TDX TCP 无 pe/pb/股息率），故主动补 1 次腾讯
    # （5rps 不封 IP，低成本）——C/D 层实时估值必须覆盖 ZHB T-1（19.88 vs 20.39 实测）
    # V17.0.6 修复: 去 need_realtime_quote 门控——roa/roe_deduct_ttm 为季报披露驱动的
    # 静态财务指标(TTM 滚动)，盘后完全可从腾讯获取(实测周六 1272.83/32.41 精确)，
    # 原门控导致盘后报告盈利质量对恒为 0(missing)
    if not rt_quote.get("roa") or not rt_quote.get("pe_ttm") or not rt_quote.get("roe_deduct_ttm"):
        try:
            from stock_common import get_tencent_quote

            _tq = get_tencent_quote(code_str) or {}
            # V17.0 修复: 补取循环删 pe_dynamic——腾讯 [52] 实为静态 PE(字典实锤),
            # 原会覆盖 push2 f162 的真动态 PE(15.55→20.58 错值); pe_dynamic 只信 f162/fuyao
            # V17.0.7: 删 main_net_inflow_yi(tx75 证伪=近180交易日涨幅, 非主力净流入)
            for _tf in ("roa", "roe_deduct_ttm", "panel_price",
                        "pe_ttm", "pb", "dividend_yield"):
                if _tq.get(_tf) not in (None, 0, '', '0', '0.0'):
                    rt_quote[_tf] = _tq[_tf]
                    field_sources[_tf] = "realtime:tencent"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data tencent extras error ({code_str}): {_e}")

    # V16.3.3 (2026-08-10 字典 12.15.5): fuyao 估值印证位——有 Key 才用（无 Key 自动跳过）：
    # 腾讯失败时 fuyao 兜底估值（pe_ttm/pb_mrq 实测=腾讯精确 20.385/6.22）；官方 REST 风控面独立
    # V17.0.6: 去 need_realtime_quote 门控——估值字段盘后同样可从 fuyao 获取(实测周六精确)
    if not rt_quote.get("pe_ttm") or not rt_quote.get("ps_ttm"):
        try:
            from stock_common.sc_fuyao import is_fuyao_enabled, get_fuyao_valuation

            if is_fuyao_enabled():
                _fv = (get_fuyao_valuation([code_str]) or [])
                if _fv:
                    _f0 = _fv[0]
                    for _fk, _fsk in (("pe_ttm", "pe_ttm"), ("pe_mrq", "pe_dynamic"),
                                      ("pb_mrq", "pb"), ("ps_ttm", "ps_ttm"),
                                      ("pcf_ttm", "pcf_ttm")):
                        if not rt_quote.get(_fsk) and _f0.get(_fk) not in (None, 0, '', '0', '0.0'):
                            rt_quote[_fsk] = _f0[_fk]
                            field_sources[_fsk] = "realtime:fuyao"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data fuyao valuation error ({code_str}): {_e}")

    # ⭐ V17.0.7 层级调整: fuyao 升为财务 TTM 族**主源**——报告期驱动静态值无需实时性,
    # 同花顺官方 REST 独立风控域(4001 退避, 无 push 封禁史), 盘后可查;
    # push2delay 降为兜底(见下方 _ed 块, 仅填缺失键)。用户运行时段多为盘后,
    # thsdk(TCP) 有盘后/午休关闸 → 定位为盘中专属特殊层, 不进通用 fallback 链。
    # 聚合式(经 600519 对撞: ocf_ttm/net_profit_period/net_profit_annual 与
    # push2 f103/f105/f109 逐字等): ocf_ttm = FY(Q4)+本期−去年同期(act_cash_flow_net);
    # revenue_ttm 同法(operating_income, ⚠️ 营业收入口径 vs f104 总收入差~1.8%);
    # eps_annual = net_profit_annual ÷ 总股本(sc_capital_cache 万股→股)。
    # **进程缓存(按 code+report_period)**: 报告期数据稳定, 当日同股只算一次
    if not rt_quote.get("ocf_ttm") or not rt_quote.get("revenue_ttm") \
            or not rt_quote.get("net_profit_period") or not rt_quote.get("eps_annual"):
        try:
            from stock_common.sc_fuyao import is_fuyao_enabled

            if is_fuyao_enabled():
                global _FY_TTM_CACHE
                _fy_key = (code_str, str(rt_quote.get("report_period") or ""))
                _fy_cached = _FY_TTM_CACHE.get(_fy_key)
                if _fy_cached is None:
                    from stock_common.sc_fuyao import (
                        get_fuyao_financials as _gff, fnum_local as _fl)

                    def _series(kind, field):
                        rows = _gff(kind, code_str, limit=8) or []
                        out = {}
                        for r0 in rows:
                            key = (int(r0.get("fiscal_year") or 0),
                                   str(r0.get("fiscal_period") or ""))
                            out[key] = _fl(r0.get(field))
                        return out

                    _cf = _series("cashflow", "act_cash_flow_net")
                    _inc = _series("income", "operating_income")
                    _npf = _series("income", "parent_holder_net_profit")
                    if _cf and _inc and _npf:
                        # 本期 = 最新一条; 去年同期 = 同 fiscal_period 上一年; FY = 最近 Q4
                        _cur_key = max(_cf)
                        _cur_y, _cur_p = _cur_key
                        _yago = _cf.get((_cur_y - 1, _cur_p))
                        _fy_keys = [k for k in _cf if k[1] == "Q4" and k[0] < _cur_y]
                        _fy_ocf = _cf.get(max(_fy_keys)) if _fy_keys else None
                        if None not in (_yago, _fy_ocf):
                            _ocf = _fy_ocf + (_cf.get(_cur_key) or 0) - _yago
                            _rev_fyk = [k for k in _inc if k[1] == "Q4" and k[0] < _cur_y]
                            _rev_fy = _inc.get(max(_rev_fyk), 0) if _rev_fyk else 0
                            _np_fy = _npf.get(max(
                                (k for k in _npf if k[1] == "Q4" and k[0] < _cur_y)))
                            _fy_cached = {
                                "ocf_ttm": _ocf,
                                "revenue_ttm": _rev_fy + (_inc.get(_cur_key) or 0)
                                - (_inc.get((_cur_y - 1, _cur_p)) or 0),
                                "net_profit_period": _npf.get(_cur_key),
                                "net_profit_annual": _np_fy,
                            }
                            _FY_TTM_CACHE[_fy_key] = _fy_cached
                if _fy_cached:
                    for _fk2 in ("ocf_ttm", "revenue_ttm",
                                 "net_profit_period", "net_profit_annual"):
                        _v2 = _fy_cached.get(_fk2)
                        if _v2 and not rt_quote.get(_fk2):
                            rt_quote[_fk2] = _v2
                            field_sources[_fk2] = "realtime:fuyao"
                    # eps_annual 折算——fuyao 无 EPS 字段, 用股本缓存归一(万股→股)
                    if _fy_cached.get("net_profit_annual") and not rt_quote.get("eps_annual"):
                        try:
                            from stock_common.sc_capital_cache import get_share_capital as _gc2

                            _sh_wan = _safe_float((_gc2(code_str) or {}).get("total_shares"))
                            if _sh_wan > 0:
                                rt_quote["eps_annual"] = (
                                    _fy_cached["net_profit_annual"] / (_sh_wan * 1e4))
                                field_sources["eps_annual"] = "calc:fuyao_np_annual/capital"
                        except Exception as _e2:
                            _debug_log(f"fuyao eps_annual calc error ({code_str}): {_e2}")
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data fuyao ttm primary error ({code_str}): {_e}")

    # V17.0 修复: push2delay 估值+资金流补取——TDX 成功路径(TCP 无 PE/资金流统计)缺
    # pe_dynamic/fund_*; 腾讯 [52] 实为静态 PE(字典实锤)不可作动态源;
    # ⚠️ V17.0.7: 原"腾讯 tx75 主力净流入方向相反不可作首选"注释作废——tx75 实为
    # 近180交易日涨跌幅(非资金流, 语义完全不同), 资金流只信 push2delay f137 族。
    # 统一 push2delay f162/f137 一次请求补全。**无条件执行(盘前也补)**: 主力净流入为
    # 日级动态字段, 盘前/盘后均应显示最近交易日 f137(而非 ZHB T-1)——sht 二章/七章口径统一的关键。
    # **进程缓存(当天)**: sht 35 只批量每只 1 次 → 缓存命中免重复
    # **V17.0.7 层级**: 本块降为财务 TTM 族**兜底**——pe_dynamic/fund_* 维持无条件覆盖
    # (push2delay 唯一源), 财务四键仅在 fuyao 未填时补(不再覆盖 fuyao 主源值);
    # eps_deduct_ttm/undist_profit_ps 无 fuyao 对应, 仍由本块提供(push 独有字段)
    if not rt_quote.get("pe_dynamic") or not rt_quote.get("fund_main_today"):
        global _PD_EXTRA_CACHE, _PD_EXTRA_CACHE_DATE
        from datetime import datetime as _dt2

        _today = _dt2.now().strftime("%Y%m%d")
        if _PD_EXTRA_CACHE_DATE != _today:
            _PD_EXTRA_CACHE.clear()
            _PD_EXTRA_CACHE_DATE = _today
        _ed = _PD_EXTRA_CACHE.get(code_str)
        if _ed is None:
            try:
                from stock_common.sc_datasource import get_em_quote_full_delay

                _ed = get_em_quote_full_delay(code_str) or {}
                if _ed:
                    _PD_EXTRA_CACHE[code_str] = _ed  # V17.0: 仅非空缓存——失败下次重试(空缓存会污染测试/重试)
            except Exception as _e:
                _debug_log(f"get_canonical_stock_data push2delay pe/fund error ({code_str}): {_e}")
                _ed = {}
        if _ed.get("pe_dynamic") not in (None, 0, '', '0', '0.0'):
            rt_quote["pe_dynamic"] = _ed["pe_dynamic"]
            field_sources["pe_dynamic"] = "realtime:push2delay"
        for _fk in ("fund_main_today", "fund_main_5d",
                    "fund_super_today", "fund_large_today", "fund_mid_today", "fund_small_today"):
            if _ed.get(_fk) not in (None, 0, '', '0', '0.0'):
                rt_quote[_fk] = _ed[_fk]
                field_sources[_fk] = "realtime:push2delay"
        # 财务族兜底——仅补缺失(fuyao 主源已填的键不覆盖); eps_deduct_ttm/
        # undist_profit_ps 为 push 独有, 直接补
        for _fk in ("ocf_ttm", "revenue_ttm", "net_profit_period", "net_profit_annual",
                    "eps_deduct_ttm", "eps_annual", "undist_profit_ps"):
            if not rt_quote.get(_fk) and _ed.get(_fk) not in (None, 0, '', '0', '0.0'):
                rt_quote[_fk] = _ed[_fk]
                field_sources[_fk] = "realtime:push2delay"

    # 3. 实时/收盘资金流
    rt_fund = {}
    if need_realtime_quote:
        try:
            from core.tdx_client import tdx_get_fund_flow

            rt_fund = tdx_get_fund_flow(code_str) or {}
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data tdx_get_fund_flow error: {_e}")

    # 4. 字段清洗与 Boundary Validation (V15.4: 每字段独立 source 标签)
    basic_info = get_stock_basic_info_from_zhb(code_str)
    zhb_name = basic_info.get('name', '') if isinstance(basic_info, dict) else ''
    # name: 优先级 push2/tencent/tdx > ZHB
    name = str(
        rt_quote.get('name')
        or zhb_dict.get('name')
        or zhb_name
        or get_stock_name_from_zhb(code_str)
        or ''
    )
    if not field_sources.get("name"):
        if name:
            field_sources["name"] = "zhb:static" if zhb_name == name else "calculated"

    # V16.3.3 (2026-08-10 字典名称设计): 结构化名称——核心名（永久不变）+ ST/次新标记
    # 临时前缀（N/C/XD/XR/DR/S）忽略；ST/*ST 不可忽略（风险信号）
    try:
        from stock_common.sc_utils import parse_stock_name

        name_core, is_st, is_new = parse_stock_name(name)
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data parse_stock_name error: {_e}")
        name_core, is_st, is_new = name, False, False

    # ─────────────────────────────────────────────────────────
    # 行情字段 (price/change_pct/open/high/low/amount/turnover)
    # V15.4: 已在 L1/L2/L3 标记 source, 这里仅做字段清洗
    # ─────────────────────────────────────────────────────────
    def _extract_with_source(field_name, rt_default=None, zhb_default=None):
        """V15.4: 提取字段并按 source 优先级处理。

        V17.0.1c(2026-08-16): 去掉 need_realtime_quote 门控——休市/盘前 rt_quote
        仍来自 TDX 快照(最近交易日), 值正确; 原门控导致休市时 open/high/low
        只从 zhb 取(ZHB 无 OHLC) → 报告 0.00 元。rt_quote 有值优先, zhb 兜底。
        V17.0.1d(2026-08-16): zhb 分支改用 zhb_default——原用 field_name 查
        zhb_dict, 而 amount_wan 的 zhb 键是 'amount'(字段名查不到) → 成交额恒 0。
        """
        if rt_quote.get(field_name) not in (None, 0, '', '0', '0.0'):
            return _safe_float(rt_quote.get(field_name)), field_sources.get(
                field_name, "realtime:unknown"
            )
        if zhb_default not in (None, 0, '', '0', '0.0'):
            return _safe_float(zhb_default), "zhb:t-1"
        if zhb_dict.get(field_name) not in (None, 0, '', '0', '0.0'):
            return _safe_float(zhb_dict.get(field_name)), "zhb:t-1"
        return _safe_float(rt_default if rt_default is not None else 0), "missing"

    price, price_src = _extract_with_source("price", rt_quote.get("price"), zhb_dict.get("price"))
    # V15.5.3: ZHB tdxstat 无 price 字段，非交易日/盘前缺失时走 get_stock_price
    # 完整链（ZHB→TDX→腾讯，15s TTL）——修复 med/lng 报告 price=0.00
    if not price and price_src == "missing":
        try:
            _sp = get_stock_price(code_str)
            if _sp:
                price = _safe_float(_sp)
                price_src = "realtime:tdx"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data get_stock_price fallback error: {_e}")
    field_sources["price"] = price_src
    change_pct, _ = _extract_with_source(
        "change_pct", rt_quote.get("change_pct"), zhb_dict.get("change_pct")
    )
    field_sources["change_pct"] = field_sources.get("change_pct", _ if _ else price_src)
    open_p, _ = _extract_with_source("open", rt_quote.get("open"), zhb_dict.get("open"))
    field_sources["open"] = field_sources.get("open", price_src)
    high_p, _ = _extract_with_source("high", rt_quote.get("high"), zhb_dict.get("high"))
    field_sources["high"] = field_sources.get("high", price_src)
    low_p, _ = _extract_with_source("low", rt_quote.get("low"), zhb_dict.get("low"))
    field_sources["low"] = field_sources.get("low", price_src)
    # V17.0.1d: 休市/盘前 OHLC 缺口 → TDX 本机 .day 兜底(零网络, 与 TDX 快照同源)
    if not (open_p and high_p and low_p):
        try:
            from stock_common.sc_datasource import get_tdx_day_tail

            _day = get_tdx_day_tail(code_str)
            if _day:
                if not open_p:
                    open_p = _safe_float(_day.get("open"))
                    field_sources["open"] = "tdx:.day"
                if not high_p:
                    high_p = _safe_float(_day.get("high"))
                    field_sources["high"] = "tdx:.day"
                if not low_p:
                    low_p = _safe_float(_day.get("low"))
                    field_sources["low"] = "tdx:.day"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data .day ohlc fallback error: {_e}")
    prev_close, _ = _extract_with_source(
        "prev_close", rt_quote.get("last_close"), zhb_dict.get("prev_close")
    )
    # V17.0.1c: TDX/zhb 均无昨收(TDX 快照无 last_close)时, 用 price 与 change_pct 反算
    # M3(审查 2026-08-16): 反算加 sanity——change_pct 极端(如 -99.9, 可转债/退市整理无跌停保护)
    # 会放大昨收荒谬值; 反算结果必须落在 price*0.5~price*2 内才接受
    if not prev_close and price and change_pct:
        try:
            _pc = _safe_float(price / (1 + change_pct / 100.0))
            if _pc > 0 and (price * 0.5 <= _pc <= price * 2.0):
                prev_close = _pc
            else:
                _debug_log(f"get_canonical_stock_data prev_close 反算超界拒绝: price={price} chg={change_pct} pc={_pc}")
        except (ZeroDivisionError, TypeError):
            prev_close = 0
    field_sources["prev_close"] = field_sources.get("prev_close", price_src)
    amount_wan, amount_src = _extract_with_source(
        "amount_wan", rt_quote.get("amount_wan"), zhb_dict.get("amount")
    )
    field_sources["amount_wan"] = amount_src
    # V16.0: volume_hand 不再从 ZHB 兜底 — ZHB Col[24] 曾误映射为 volume(成交量)，
    # V17.0.9: Col[24] 已破解正名为 cash_reserve_wan(货币资金/万元, 静态财报字段)。
    # 真实成交量只能来自实时行情。
    volume_hand, _ = _extract_with_source(
        "volume_hand", rt_quote.get("volume_hand"), None
    )
    field_sources["volume_hand"] = field_sources.get("volume_hand", price_src)
    turnover_pct, _ = _extract_with_source(
        "turnover_pct", rt_quote.get("turnover_pct"), zhb_dict.get("turnover_pct")
    )
    # V16.2.3 修复: TDX 0x010C 无换手率、ZHB 无此字段 → sht 换手率恒 0。
    # 腾讯行情 f38 有换手率且 @cached（命中无网络开销），补作兜底。
    if not turnover_pct:
        try:
            from stock_common import get_tencent_quote

            _tq = get_tencent_quote(code_str) or {}
            _tv = _safe_float(_tq.get("turnover_pct") or 0)
            if _tv > 0:
                turnover_pct = _tv
                field_sources["turnover_pct"] = "realtime:tencent"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data turnover tencent fallback error: {_e}")
    field_sources["turnover_pct"] = field_sources.get("turnover_pct", price_src)

    # 估值类 (V16.3.3 2026-08-10 字典 12.15.6 ABCD 分层修正:
    # A/B 层(休市/盘前) ZHB 优先；C/D 层(盘中/盘后) 实时优先——T-1 pe 与实时价不匹配
    # (实测：茅台实时 20.39 vs ZHB T-1 19.88，价差 2.5% 导致 pe 失真))
    if need_realtime_quote:
        pe_ttm = _safe_float(rt_quote.get('pe_ttm') or zhb_dict.get('pe_ttm'))
    else:
        pe_ttm = _safe_float(zhb_dict.get('pe_ttm') or rt_quote.get('pe_ttm'))
    if pe_ttm < 0 or pe_ttm > 10000:
        pe_ttm = 0.0
    field_sources["pe_ttm"] = (
        "realtime:" + (field_sources.get("pe_ttm", "tencent").split(":")[-1])
        if need_realtime_quote and rt_quote.get('pe_ttm')
        else ("zhb:static" if zhb_dict.get('pe_ttm') else field_sources.get("pe_ttm", "missing"))
    )
    # V16.3.3 (2026-08-10 字典 12.15.5): ROA 总资产收益率 — 腾讯 tx66（银行股精确：
    # 招行 1.12=年化 ROA/工行 0.67=年报 ROA 实测验证）；ZHB/push2delay 均无此字段
    # V17.0.5 正名: 口径实为 **TTM 滚动**（fuyao total_assets_net_ratio 同族；银行 TTM≈年报故曾误标"年化"）
    roa = _safe_float(rt_quote.get('roa') or 0)
    if roa > 0 and roa < 100:
        field_sources["roa"] = "realtime:tencent"
    else:
        roa = 0.0
        field_sources["roa"] = "missing"
    # V17.0.5: 扣非加权 ROE(TTM 滚动) — 腾讯 tx65（fuyao index_deduct_weighted_avg_roe 同族，
    # 茅台 32.41 vs 官方 Q1 32.52；披露日跳变天然实验）——与 roa 成盈利质量对，lng 复利引擎口径升级候选
    roe_deduct_ttm = _safe_float(rt_quote.get('roe_deduct_ttm') or 0)
    if 0 < roe_deduct_ttm < 500:
        field_sources["roe_deduct_ttm"] = "realtime:tencent"
    else:
        roe_deduct_ttm = 0.0
        field_sources["roe_deduct_ttm"] = "missing"
    if need_realtime_quote:
        pe_dynamic = _safe_float(rt_quote.get('pe_dynamic') or zhb_dict.get('pe_dynamic'))
    else:
        pe_dynamic = _safe_float(zhb_dict.get('pe_dynamic') or rt_quote.get('pe_dynamic'))
    field_sources["pe_dynamic"] = (
        "realtime:" + (field_sources.get("pe_dynamic", "tencent").split(":")[-1])
        if need_realtime_quote and rt_quote.get('pe_dynamic')
        else ("zhb:static" if zhb_dict.get('pe_dynamic') else field_sources.get("pe_dynamic", "missing"))
    )
    # pb: ABCD 分层——C/D 层实时优先（腾讯/push2delay）；A/B 层 ZHB（ZHB 本无 pb，走计算）
    if need_realtime_quote:
        pb = _safe_float(rt_quote.get('pb') or zhb_dict.get('pb'))
    else:
        pb = _safe_float(zhb_dict.get('pb') or rt_quote.get('pb'))
    # V17.0.5: PS(TTM)/PCF(TTM)——fuyao valuation 独有维度(rt_quote 由 L503 补取注入)
    ps_ttm = _safe_float(rt_quote.get('ps_ttm') or 0)
    pcf_ttm = _safe_float(rt_quote.get('pcf_ttm') or 0)
    # V16.3.3 (2026-08-10 字典 12.15.5): THS 盘中 PB 优先——仅 C 层(930-1500)调用
    # （THS 盘后返回空实测 23:16 全 query_key 空；账号限频 1.5s）
    if pb <= 0 and is_trading_hours:
        try:
            from stock_common.sc_ths import get_ths_pb

            _tpb = get_ths_pb(code_str)
            if _tpb and _tpb > 0:
                pb = round(_tpb, 2)
                field_sources["pb"] = "realtime:ths"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data ths pb error ({code_str}): {_e}")
    # V15.5.3: pb 兜底 — ZHB 无 pb 字段，用 TDX 每股净资产计算 (price / bvps)
    if pb <= 0 and price > 0:
        try:
            from core.tdx_client import tdx_get_finance_info

            _fin = tdx_get_finance_info(code_str) or {}
            _bvps = _safe_float(_fin.get('meigujingzichan'))
            if _bvps > 0:
                pb = round(price / _bvps, 2)
                field_sources["pb"] = "calculated"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data pb calc error: {_e}")
    field_sources["pb"] = (
        "realtime:" + (field_sources.get("pb", "tencent").split(":")[-1])
        if need_realtime_quote and rt_quote.get('pb')
        else ("zhb:static" if zhb_dict.get('pb') else field_sources.get("pb", "missing"))
    )
    # 股息率: ABCD 分层——C/D 层实时优先（腾讯 f126/push2delay，实测 3.86 vs ZHB T-1 3.97）
    if need_realtime_quote:
        dividend_yield = _safe_float(rt_quote.get('dividend_yield') or zhb_dict.get('dividend_yield'))
    else:
        dividend_yield = _safe_float(zhb_dict.get('dividend_yield') or rt_quote.get('dividend_yield'))
    field_sources["dividend_yield"] = (
        "realtime:" + (field_sources.get("dividend_yield", "tencent").split(":")[-1])
        if need_realtime_quote and rt_quote.get('dividend_yield')
        else ("zhb:static" if zhb_dict.get('dividend_yield') else field_sources.get("dividend_yield", "missing"))
    )
    # V15.4: 振幅/量比 (push2 f171/f49)
    amplitude_pct = _safe_float(rt_quote.get('amplitude_pct') or zhb_dict.get('amplitude_pct') or 0)
    if amplitude_pct <= 0 and high_p > 0 and low_p > 0 and prev_close > 0:
        # L4 公式推算: 振幅 = (high - low) / last_close
        amplitude_pct = round((high_p - low_p) / prev_close * 100, 2)
        field_sources["amplitude_pct"] = "calculated"
    else:
        field_sources["amplitude_pct"] = field_sources.get("amplitude_pct", "missing")
    vol_ratio = _safe_float(rt_quote.get('vol_ratio') or 0)
    field_sources["vol_ratio"] = field_sources.get("vol_ratio", "missing")

    # 资金流类（V17.0 修复 2026-08-13: 统一优先级 push2delay f137(=f135-f136 主力买卖差) → 东财 rt_fund
    # ⚠️ V17.0.7 (2026-08-25): 删除"腾讯 tx75 主力净流入(亿)"兜底分支——tx75 实为**近180交易日
    # 涨跌幅%(前复权)**(K线窗口扫描定案, 字典 12.1), 旧分支会将其 ×10000 注入假主力净额
    # (603221 134.52 → +13.45亿假流入); "方向相反"旧观察即此错位的表现
    pd_main = _safe_float(rt_quote.get('fund_main_today') or 0)  # 元(主力净=f137+f140 特大+大单, V17.0 定案)
    # V17.0: 无条件 f137 优先(日级动态字段, 盘前/盘后均取最近交易日)——与 get_main_net_buy 同源
    # ⚠️ 2026-08-14 实锤: ZHB main_net_buy_amount 实为**开盘金额(竞价额)**(19/19 恒正+占比<5%),
    # 不可作主力净流入——ZHB 分支已移除
    if pd_main:
        main_net_buy_wan = pd_main / 1e4  # 元 → 万元
        field_sources["main_net_buy_wan"] = "realtime:push2delay"
    else:
        main_net_buy_wan = _safe_float(rt_fund.get('main_net_wan'))
        field_sources["main_net_buy_wan"] = "realtime:eastmoney"
    # ⚠️ V17.0(2026-08-14): ZHB main_net_buy_hands 实为**早盘竞价量**(手, [9]×开盘≈[14] 铁证),
    # 不可作主力净买入量——非实时路径置 0, 主力净量仅信 TDX 0x0011(rt_fund)
    main_net_buy_hands = _safe_float(rt_fund.get('main_net_hands') if need_realtime_quote else 0)
    field_sources["main_net_buy_hands"] = (
        "realtime:eastmoney" if rt_fund.get('main_net_hands') is not None else "missing"
    )
    # ⚠️ V17.0: ZHB main_net_buy_amount_1d 实为昨日开盘金额(竞价额)——不再作为主力净流入 T-1
    main_net_buy_wan_1d = 0.0
    field_sources["main_net_buy_wan_1d"] = "missing"

    # 财务与股本类
    roe = _safe_float(zhb_dict.get('roe')) if zhb_dict.get('roe') is not None else None
    field_sources["roe"] = "zhb:static" if roe is not None else "missing"
    gross_margin = (
        _safe_float(zhb_dict.get('gross_margin'))
        if zhb_dict.get('gross_margin') is not None
        else None
    )
    field_sources["gross_margin"] = "zhb:static" if gross_margin is not None else "missing"
    net_profit_margin = (
        _safe_float(zhb_dict.get('net_profit_margin'))
        if zhb_dict.get('net_profit_margin') is not None
        else None
    )
    field_sources["net_profit_margin"] = (
        "zhb:static" if net_profit_margin is not None else "missing"
    )
    net_profit = _safe_float(zhb_dict.get('net_profit'))
    field_sources["net_profit"] = "zhb:static" if net_profit else "missing"
    revenue = _safe_float(zhb_dict.get('revenue'))
    field_sources["revenue"] = "zhb:static" if revenue else "missing"
    # V16.3 O: ZHB 无 roe/毛利率/净利率/net_profit/revenue（tdxstat 碰撞确认无财务深度字段），
    # 未命中时 fallback TDX —— F10 财务分析（roe/毛利率，@cached gross_margin_roe）+
    # 0x0010（净利/营收，单位角 → /10 得元，@cached financial）——逐股首次后零重复请求。
    if roe is None or gross_margin is None:
        try:
            from stock_common.sc_datasource import get_gross_margin_and_roe

            _gmar = get_gross_margin_and_roe(code_str) or {}
            if roe is None and _gmar.get('roe') is not None:
                roe = _safe_float(_gmar.get('roe'))
                field_sources["roe"] = "tdx:f10" if roe is not None else "missing"
            if gross_margin is None and _gmar.get('gross_margin') is not None:
                gross_margin = _safe_float(_gmar.get('gross_margin'))
                field_sources["gross_margin"] = "tdx:f10" if gross_margin is not None else "missing"
        except Exception as _e:
            _debug_log(f"canonical gross_margin_roe fallback error ({code_str}): {_e}")
    if not net_profit or not revenue:
        try:
            from core.tdx_client import tdx_get_finance_info

            _fin = tdx_get_finance_info(code_str) or {}
            if not net_profit and _fin.get('jinglirun') is not None:
                net_profit = _safe_float(_fin.get('jinglirun')) / 10.0
                field_sources["net_profit"] = "tdx:0x0010" if net_profit else "missing"
            if not revenue and _fin.get('zhuyingshouru') is not None:
                revenue = _safe_float(_fin.get('zhuyingshouru')) / 10.0
                field_sources["revenue"] = "tdx:0x0010" if revenue else "missing"
        except Exception as _e:
            _debug_log(f"canonical finance_info fallback error ({code_str}): {_e}")
    # V16.3 O20: 字典多源对齐——0x0010 失败时新浪财报兜底（@cached financial，
    # 主源成功零额外请求；单位：新浪元直接）
    if not net_profit or not revenue:
        try:
            from stock_common.sc_datasource import get_sina_financial_report

            _fin_rows = get_sina_financial_report(code_str, 1) or []
            if not net_profit and _fin_rows:
                _np = _safe_float(_fin_rows[0].get("净利润"))
                if _np:
                    net_profit = _np
                    field_sources["net_profit"] = "sina:lrb"
            if not revenue and _fin_rows:
                _rev = _safe_float(_fin_rows[0].get("营业总收入"))
                if _rev:
                    revenue = _rev
                    field_sources["revenue"] = "sina:lrb"
        except Exception as _e:
            _debug_log(f"canonical sina financial fallback error ({code_str}): {_e}")
    # 净利率自算兜底——仅当净利/营收同源同单位时计算（0x0010 角或新浪元，
    # V16.3 O20 扩展：新浪同源也可自算；混合源单位相消失效跳过）
    if (
        net_profit_margin is None
        and net_profit
        and revenue
        and field_sources.get("net_profit") == field_sources.get("revenue")
        and field_sources.get("net_profit") in ("tdx:0x0010", "sina:lrb")
    ):
        _npm = (net_profit / revenue) * 100.0
        if math.isfinite(_npm):
            net_profit_margin = round(_npm, 2)
            field_sources["net_profit_margin"] = "calc:net_profit/revenue"
    # V16.2: EPS 主字段接入 push2 f55（实时 T 日数据源优先，ZHB T-1 兜底）
    # V16.3 O: 离线兜底 F10 基本每股收益（main_indicators，与 ZHB tipinfo 交叉验证一致）
    eps = _safe_float(rt_quote.get('eps') or zhb_dict.get('eps'))
    if not eps:
        # 离线兜底 F10 基本每股收益（main_indicators，与 ZHB tipinfo 交叉验证一致；
        # @cached gross_margin_roe——roe/毛利率分支已调过则零额外请求）
        try:
            from stock_common.sc_datasource import get_gross_margin_and_roe

            _gmar2 = get_gross_margin_and_roe(code_str) or {}
            if _gmar2.get('eps') is not None:
                eps = _safe_float(_gmar2.get('eps'))
        except Exception as _e:
            _debug_log(f"canonical eps f10 fallback error ({code_str}): {_e}")
    if rt_quote.get('eps'):
        field_sources["eps"] = "realtime:push2"
    elif eps and zhb_dict.get('eps'):
        field_sources["eps"] = "zhb:static"
    elif eps:
        field_sources["eps"] = "tdx:f10"
    else:
        field_sources["eps"] = "missing"

    # 股本类 — V15.4 4 级 fallback: push2/tdx/tencent > ZHB
    # V16.3 A2 注: rt_quote 若来自 get_stock_info(TDX finance) 其 total_shares 单位是**股**，
    # 直接当万股会错 10000 倍——当前实测 rt_quote 不含股本（走下方 capital_cache 万股兜底，
    # 值正确），此防御注释防止未来 rt_quote 加股本字段时误用。
    total_shares_wan = _safe_float(rt_quote.get('total_shares') or zhb_dict.get('total_shares'))
    # V15.5.3: 股本兜底 ← sc_capital_cache（V10.1 全局股本缓存，ZHB 无 total_shares 字段）
    if not total_shares_wan:
        try:
            from stock_common.sc_capital_cache import get_share_capital as _get_cap

            _cap = _get_cap(code_str) or {}
            total_shares_wan = _safe_float(_cap.get('total_shares'))
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data total_shares fallback error: {_e}")
    # V16.3.10 合理性校验（与 pe 范围过滤对称）：万股量级防御——
    # A 股总股本 ≤ ~2000 亿股 = 2e6 万股；>1e7 明显为"股"单位误入，按 股→万 归一
    if total_shares_wan > 1e7:
        total_shares_wan = total_shares_wan / 1e4
    if rt_quote.get('total_shares') and rt_quote.get('total_shares') > 0:
        field_sources["total_shares_wan"] = field_sources.get("total_shares", "realtime:unknown")
    else:
        field_sources["total_shares_wan"] = "zhb:static"
    float_shares_wan = _safe_float(rt_quote.get('float_shares') or zhb_dict.get('float_shares'))
    # V15.5.3: 流通股本兜底 — sc_capital_cache
    if not float_shares_wan:
        try:
            from stock_common.sc_capital_cache import get_share_capital as _get_cap

            _cap = _get_cap(code_str) or {}
            float_shares_wan = _safe_float(_cap.get('float_shares'))
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data float_shares fallback error: {_e}")
    if rt_quote.get('float_shares') and rt_quote.get('float_shares') > 0:
        field_sources["float_shares_wan"] = field_sources.get("float_shares", "realtime:unknown")
    else:
        field_sources["float_shares_wan"] = "zhb:static"

    # 市值类 — V15.4: 优先 rt_quote.mcap_yi, 否则 L4 公式推算
    mcap_yi = _safe_float(
        rt_quote.get('mcap_yi')
        if need_realtime_quote and rt_quote.get('mcap_yi')
        else zhb_dict.get('mcap_yi')
    )
    if mcap_yi <= 0 and total_shares_wan > 0 and price > 0:
        # L4 公式推算: mcap = total_shares * price / 1e8
        mcap_yi = round((total_shares_wan * 10000 * price) / 1e8, 2)
        field_sources["mcap_yi"] = "calculated"
    # V16.3.10 合理性校验：亿单位量级防御——A 股总市值 ≤ ~50 万亿 = 5e5 亿，
    # >1e6 明显为"万元"单位误入（总股本×价格公式放大 1e4 的遗留），按 万→亿 归一
    if mcap_yi > 1e6:
        mcap_yi = mcap_yi / 1e4
        field_sources["mcap_yi"] = "calculated:norm"
    else:
        field_sources["mcap_yi"] = field_sources.get("mcap_yi", "missing")
    float_mcap_yi = _safe_float(
        rt_quote.get('float_mcap_yi')
        if need_realtime_quote and rt_quote.get('float_mcap_yi')
        else zhb_dict.get('float_mcap_yi')
    )
    if float_mcap_yi <= 0 and float_shares_wan > 0 and price > 0:
        float_mcap_yi = round((float_shares_wan * 10000 * price) / 1e8, 2)
        field_sources["float_mcap_yi"] = "calculated"
    else:
        field_sources["float_mcap_yi"] = field_sources.get("float_mcap_yi", "missing")

    holder_count = int(zhb_dict.get('holder_count') or 0)
    field_sources["holder_count"] = "zhb:static" if holder_count else "missing"
    # V16.3 O: 股东户数兜底 — 0x0010 gudong_renshu（比巨潮 stock_hold_num_cninfo 更易，
    # 与 net_profit/revenue 同一次 finance_info 拉取共用缓存）
    if not holder_count:
        try:
            from core.tdx_client import tdx_get_finance_info

            _fin_hc = tdx_get_finance_info(code_str) or {}
            _hc = _safe_float(_fin_hc.get('gudong_renshu'))
            if _hc and _hc > 0:
                holder_count = int(_hc)
                field_sources["holder_count"] = "tdx:0x0010"
        except Exception as _e:
            _debug_log(f"canonical holder_count fallback error ({code_str}): {_e}")

    # 历史衍生指标
    change_5d = _safe_float(zhb_dict.get('change_5d'))
    field_sources["change_5d"] = "zhb:static" if change_5d else "missing"
    change_10d = _safe_float(zhb_dict.get('change_10d'))
    field_sources["change_10d"] = "zhb:static" if change_10d else "missing"
    change_20d = _safe_float(zhb_dict.get('change_20d'))
    field_sources["change_20d"] = "zhb:static" if change_20d else "missing"
    # V15.1: 启用 change_30d（tdxstat.cfg Col[18]）⚠️ V17.0 实锤: tdxstat.cfg 无 30 日列,
    # change_30d 为历史遗留 key 实读 Col[18]=20 日值(与 change_20d 相同); 真实 30 日仅 TdxQuant ZAFPre30
    change_30d = _safe_float(zhb_dict.get('change_30d'))
    field_sources["change_30d"] = "zhb:static" if change_30d else "missing"
    change_60d = _safe_float(zhb_dict.get('change_60d'))
    field_sources["change_60d"] = "zhb:static" if change_60d else "missing"
    change_ytd = _safe_float(zhb_dict.get('change_ytd'))
    field_sources["change_ytd"] = "zhb:static" if change_ytd else "missing"
    # V17.0.5: 本月至今涨跌幅(tdxstat2 Col[11] 正名 change_mtd, 基准=上月末收盘)
    change_mtd = _safe_float(zhb_dict.get('change_mtd'))
    field_sources["change_mtd"] = "zhb:static" if change_mtd else "missing"
    streak_days = int(zhb_dict.get('streak_days') or 0)
    field_sources["streak_days"] = "zhb:static" if streak_days else "missing"
    # V16.2: 52 周高低价主字段接入 push2 f174/f175（实时优先，ZHB T-1 兜底）
    high_52w = _safe_float(rt_quote.get('high_52w') or zhb_dict.get('high_52w'))
    field_sources["high_52w"] = (
        "realtime" if rt_quote.get('high_52w') else ("zhb:static" if high_52w else "missing")
    )
    low_52w = _safe_float(rt_quote.get('low_52w') or zhb_dict.get('low_52w'))
    field_sources["low_52w"] = (
        "realtime" if rt_quote.get('low_52w') else ("zhb:static" if low_52w else "missing")
    )
    ipo_price = _safe_float(zhb_dict.get('ipo_price'))
    field_sources["ipo_price"] = "zhb:static" if ipo_price else "missing"
    employee_count = int(zhb_dict.get('employee_count') or 0)
    field_sources["employee_count"] = "zhb:static" if employee_count else "missing"

    # V15.4 方案 C: industry fallback 链（V16.1.7 调整）
    # 优先级: push2 f127 (免费副产品, 行情 L3 已调 get_em_quote_full 零额外请求)
    #        > TDX boards (TCP 不易封禁, 行情走 TDX/腾讯时行业走此级)
    #        > ZHB static (盘前/静态兜底)
    # 注: 行情链正常(TDX/腾讯成功)时 em_quote_raw 为空 → 行业自动走 TDX TCP, 不碰东财;
    #     仅行情 fallback 到 push2 时行业才用 push2 f127 (此时零额外请求)。腾讯级已删(无 industry 字段, 死级)
    industry = ''
    board = ''
    industry_code = str(zhb_dict.get('industry_code') or '')
    # V16.2.17: L0 东财申万二级行业（datacenter 域低风险，全市场映射一次性缓存，零逐股请求；
    # 东财二级与申万二级同源（半导体/白酒Ⅱ/光学光电子），统一"申万二级"口径）
    try:
        from stock_common import get_em_industry_l2

        _em_ind = get_em_industry_l2(code_str)
        if _em_ind:
            industry = _em_ind
            field_sources["industry"] = "realtime:em-datacenter"
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data em industry: {_e}")
    # L1: push2 (em_quote_raw 已在 L3 push2 fallback 中填充, 免费副产品)
    # V16.0: get_em_quote_full 返回规范名 — f127→industry, f128→board(地域)
    if em_quote_raw.get('industry') and em_quote_raw['industry'] not in (None, '', 'None'):
        industry = str(em_quote_raw['industry']).strip()
        field_sources["industry"] = "realtime:push2"
    # V17.0 修正: get_em_quote_full 不返回 industry_code; ZHB tdxstat2 Col[13] 为双段混合
    # (881=通达信行业板块可靠 / 880=概念风格不可当行业)——该变量仅入 field_sources 不入 cdata 契约
    if em_quote_raw.get('board') and em_quote_raw['board'] not in (None, '', 'None'):
        board = str(em_quote_raw['board']).strip()
        field_sources["board"] = "realtime:push2"
    # L2: TDX boards（TCP 不易封禁）
    if not industry:
        try:
            from core.tdx_client import tdx_get_belong_boards

            boards = tdx_get_belong_boards(code_str)
            if boards and boards.get("industry"):
                industry = boards["industry"][0].get("name", "")
                field_sources["industry"] = field_sources.get("industry", "tdx:boards")
            if not board and boards and boards.get("area"):
                board = boards["area"][0].get("name", "")
                field_sources["board"] = "tdx:boards"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data tdx boards error: {_e}")
    # L3: ZHB 静态（profile.dat）—— 最后的兜底
    if not industry:
        if basic_info and isinstance(basic_info, dict) and basic_info.get('industry'):
            industry = basic_info['industry']
            field_sources["industry"] = "zhb:static"
        elif zhb_dict.get('industry'):
            industry = zhb_dict['industry']
            field_sources["industry"] = "zhb:static"
    # V16.3 J: 删除"剥离'子'后缀"逻辑——V16.2.17 统一东财申万二级后官方名为
    # "光学光电子"，剥离成"光学光电"导致 sht/med/lng 报告行业名不一致
    if not industry:
        field_sources["industry"] = field_sources.get("industry", "missing")
    if not field_sources.get("industry_code"):
        field_sources["industry_code"] = field_sources.get("industry", "missing")
    if not field_sources.get("board"):
        field_sources["board"] = "missing"
    # concepts: 优先 TDX concept (TCP), 其次 push2 f129 (免费副产品), 最后 ZHB concept_chain
    concepts_list = []
    try:
        from core.tdx_client import tdx_get_belong_boards

        boards = tdx_get_belong_boards(code_str)
        if boards and boards.get("concept"):
            concepts_list = [c.get("name", "") for c in boards["concept"] if c.get("name")]
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data tdx concepts error: {_e}")
    # V16.1.7: push2 f129 概念列表兜底（get_em_quote_full 已解析 f129→concepts）
    if not concepts_list and em_quote_raw.get('concepts'):
        try:
            concepts_list = [str(c).strip() for c in em_quote_raw['concepts'] if str(c).strip()]
            field_sources["concepts"] = "realtime:push2"
        except Exception:
            pass
    # ZHB concept_chain 仅作补充（V15.1 后已重写为板块代码→名称映射，不再支持成分股）
    if not concepts_list:
        concepts_list = get_concept_from_zhb(code_str)
        field_sources["concepts"] = "zhb:concept_chain"
    else:
        field_sources["concepts"] = field_sources.get("concepts", "tdx:boards")

    # V16.0: 上市日期（list_date）— 从 push2 f189 / rt_quote / em_quote_raw 提取
    # V16.2 修复: 去掉 data_date 回退（data_date 是本机日期，上市日期缺失时置空而非写成当天）
    # V16.3.3 (2026-08-10 字典 12.15.8): list_date 永久字段走独立 10 年缓存（static_permanent）——
    # 首次 HTTP 后永不过期，不再每次从行情链提取
    try:
        from stock_common.sc_datasource import get_stock_permanent_info

        _pinfo = get_stock_permanent_info(code_str) or {}
        _p_list_date = _pinfo.get("list_date")
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data permanent info error ({code_str}): {_e}")
        _p_list_date = None
    list_date = str(
        _p_list_date
        or rt_quote.get("list_date")
        or em_quote_raw.get("list_date")
        or ""
    )
    if list_date and list_date not in ("None", "nan"):
        field_sources["list_date"] = "static:permanent" if _p_list_date else (
            "realtime:push2" if rt_quote.get("list_date") else "missing"
        )
    else:
        list_date = ""

    # V17.0.6 修复: source_tag 只看价格字段(price)是否来自实时源——
    # 原 `and rt_quote` 在 roa/ps_ttm 等财务字段补取后恒真, 导致盘后/熔断时误标 http/tdx
    source_tag = "http/tdx" if need_realtime_quote and rt_quote.get("price") else "zhb"
    time_anchor_tag = "t_day" if (is_trading_hours or is_post_market) else "t-1"

    return CanonicalStockData(
        code=code_str,
        name=name,
        name_core=name_core,
        is_st=is_st,
        is_new=is_new,
        price=price,
        change_pct=change_pct,
        open=open_p,
        high=high_p,
        low=low_p,
        prev_close=prev_close,
        amount_wan=amount_wan,
        volume_hand=volume_hand,
        pe_ttm=pe_ttm,
        pe_dynamic=pe_dynamic,
        pb=pb,
        ps_ttm=ps_ttm,
        pcf_ttm=pcf_ttm,
        dividend_yield=dividend_yield,
        turnover_pct=turnover_pct,
        main_net_buy_wan=main_net_buy_wan,
        main_net_buy_hands=main_net_buy_hands,
        # V17.0.1a 规范化: 竞价族规范键(与 main_net_buy_* 同值, 键名语义化)
        open_amount_wan=main_net_buy_wan,  # 竞价额(万元)
        bid_volume_hand=main_net_buy_hands,  # 竞价量(手)
        main_net_buy_wan_1d=main_net_buy_wan_1d,
        roe=roe or 0.0,
        roa=roa or 0.0,
        roe_deduct_ttm=roe_deduct_ttm or 0.0,  # V17.0.5: 扣非加权ROE(TTM 滚动, 腾讯 tx65)
        gross_margin=gross_margin or 0.0,
        net_profit_margin=net_profit_margin or 0.0,
        net_profit=net_profit,
        revenue=revenue,
        eps=eps,
        total_shares_wan=total_shares_wan,
        float_shares_wan=float_shares_wan,
        mcap_yi=mcap_yi,
        float_mcap_yi=float_mcap_yi,
        holder_count=holder_count,
        change_5d=change_5d,
        change_10d=change_10d,
        change_20d=change_20d,
        change_30d=change_30d,
        change_60d=change_60d,
        change_ytd=change_ytd,
        change_mtd=change_mtd,  # V17.0.5: 本月至今涨跌幅(ZHB tdxstat2 Col[11] 正名字段)
        streak_days=streak_days,
        high_52w=high_52w,
        low_52w=low_52w,
        ipo_price=ipo_price,
        employee_count=employee_count,
        list_date=list_date,
        industry=industry,
        industry_code=industry_code,
        board=board,
        concepts=tuple(concepts_list),
        data_source=source_tag,
        time_anchor=time_anchor_tag,
        is_valid=True,
        # V15.4 方案 C: per-field source label
        field_sources=dict(field_sources),
        # V16.1: push2 扩展字段（f51/f52 涨停跌停、f55/f92 EPS/BPS、f126 股息率、
        # f162-167 PE/PB、f174/f175 52周、f137-146 资金流、f198 行业码、f80 交易时段、
        # f178 5日资金流数组、data_date 行情日期）— 从 rt_quote/em_quote_raw 透传
        limit_up=_safe_float(rt_quote.get("limit_up") or em_quote_raw.get("limit_up") or 0),
        limit_down=_safe_float(rt_quote.get("limit_down") or em_quote_raw.get("limit_down") or 0),
        bps=_safe_float(rt_quote.get("bps") or em_quote_raw.get("bps") or 0),
        pe_more=_safe_float(rt_quote.get("pe_more") or em_quote_raw.get("pe_more") or 0),
        industry_code_push2=str(
            rt_quote.get("industry_code_push2") or em_quote_raw.get("industry_code_push2") or ""
        ),
        trading_periods=tuple(
            rt_quote.get("trading_periods") or em_quote_raw.get("trading_periods") or ()
        ),
        report_period=str(
            rt_quote.get("report_period")
            or em_quote_raw.get("report_period")
            or zhb_dict.get("report_date")
            or ""
        ),
        bid1_vol=_safe_float(rt_quote.get("bid1_vol") or em_quote_raw.get("bid1_vol") or 0),
        quote_date=str(rt_quote.get("data_date") or em_quote_raw.get("data_date") or ""),
        fund_main_today=_safe_float(rt_quote.get("fund_main_today") or em_quote_raw.get("fund_main_today") or 0),
        fund_super_today=_safe_float(rt_quote.get("fund_super_today") or em_quote_raw.get("fund_super_today") or 0),
        fund_large_today=_safe_float(rt_quote.get("fund_large_today") or em_quote_raw.get("fund_large_today") or 0),
        fund_mid_today=_safe_float(rt_quote.get("fund_mid_today") or em_quote_raw.get("fund_mid_today") or 0),
        fund_main_5d=_safe_float(rt_quote.get("fund_main_5d") or em_quote_raw.get("fund_main_5d") or 0),
        fund_small_today=_safe_float(rt_quote.get("fund_small_today") or em_quote_raw.get("fund_small_today") or 0),
        fund_5d_array=tuple(rt_quote.get("fund_5d_array") or em_quote_raw.get("fund_5d_array") or ()),
        # V17.0.7: 财务 TTM 族(push2 f103-f190, fuyao 官方报表终判口径)——
        # 从 rt_quote/em_quote_raw 透传(get_em_quote_full* 已解析规范键)
        ocf_ttm=_safe_float(rt_quote.get("ocf_ttm") or em_quote_raw.get("ocf_ttm") or 0),
        revenue_ttm=_safe_float(rt_quote.get("revenue_ttm") or em_quote_raw.get("revenue_ttm") or 0),
        net_profit_period=_safe_float(
            rt_quote.get("net_profit_period") or em_quote_raw.get("net_profit_period") or 0
        ),
        net_profit_annual=_safe_float(
            rt_quote.get("net_profit_annual") or em_quote_raw.get("net_profit_annual") or 0
        ),
        eps_annual=_safe_float(rt_quote.get("eps_annual") or em_quote_raw.get("eps_annual") or 0),
        eps_deduct_ttm=_safe_float(
            rt_quote.get("eps_deduct_ttm") or em_quote_raw.get("eps_deduct_ttm") or 0
        ),
        undist_profit_ps=_safe_float(
            rt_quote.get("undist_profit_ps") or em_quote_raw.get("undist_profit_ps") or 0
        ),
    )


# ═══════════════════════════════════════════════════
# 交易状态感知
# ═══════════════════════════════════════════════════


def _get_market_status() -> str:
    """获取当前市场状态（简化版，用于数据源选择策略）。

    Returns:
        'pre_market' - 盘前（< 9:30）
        'trading' - 盘中（9:30-11:30, 13:00-15:00）
        'post_market' - 盘后（>= 15:00 或 非交易日）
    """
    try:
        from stock_common.sc_datasource import get_market_status

        status, _ = get_market_status()
        if status in ("morning", "afternoon"):
            return "trading"
        elif status == "pre_market":
            return "pre_market"
        else:
            return "post_market"
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    now = datetime.now()
    t = now.hour * 100 + now.minute
    if t < 930:
        return "pre_market"
    elif 930 <= t < 1130 or 1300 <= t < 1500:
        return "trading"
    else:
        return "post_market"


def _should_use_zhb_for_realtime() -> bool:
    """判断实时字段是否可以使用 ZHB 内存数据。

    规则（根据真实物理更新规律）：
    1. 休市日/周末/节假日：100% 走 ZHB 本地内存提取（T-1日即最新已闭市数据）。
    2. 交易日 00:00 - 09:30 (盘前)：100% 走 ZHB 本地内存提取（夜间已更新为 T-1日收盘数据）。
    3. 交易日 09:30 - 24:00 (含盘中 09:30-15:00 与盘后 15:00-24:00)：
       必须走 HTTP/TDX 实时行情（在 15:00-24:00 磁盘上的 ZHB 数据包仍然是 T-1 日，
       用户要获取的是今天 T 日的最新收盘数据）。
    """
    try:
        from stock_common import is_workday

        now = datetime.now()
        today = now.date()
        if not is_workday(today):
            return True
        t = now.hour * 100 + now.minute
        return t < 930
    except Exception as _e:
        _debug_log(f"data_provider _should_use_zhb_for_realtime error: {_e}")
        return _get_market_status() != "trading"


def _parse_zhb_date(zhb_date_str: str):
    """V16.2: 统一解析 ZHB 日期（支持 YYYYMMDD 与 YYYY-MM-DD 两种格式）。"""
    if not zhb_date_str:
        return None
    try:
        s = str(zhb_date_str).strip()
        if len(s) == 8 and s.isdigit():
            return datetime.strptime(s, "%Y%m%d").date()
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _get_zhb_date_offset() -> int:
    """计算ZHB数据日期相对于今天的交易日偏移。

    返回值：
      0 = ZHB数据就是今天的（只在盘前且当天ZHB已更新时可能）
      1 = ZHB数据是昨天的（最常见情况）
      2+ = ZHB数据是更早的（非交易日运行时）
    """
    try:
        from stock_common import get_zhb_data_date

        zhb_date_str = get_zhb_data_date()
        zhb_date = _parse_zhb_date(zhb_date_str)
        if zhb_date is None:
            return 99

        today = datetime.now().date()

        if zhb_date >= today:
            return 0
        return (today - zhb_date).days
    except Exception:
        return 99


def _get_trading_date_offset() -> int:
    """计算ZHB数据日期相对于最新交易日的偏移量（ΔT）。

    这是日期对齐器的核心函数。它比较的是：
    - ZHB数据日期（T_zhb）
    - API行情能够获取到的最新交易日期（T_quote）

    返回值（ΔT）：
      0 = ZHB与API基准同频（周末/盘前/16:30后）
      1 = ZHB比API慢一天（盘中运行）
      2+ = ZHB数据严重过期

    时间场景映射：
      盘前(00:00-09:15): ΔT=0（ZHB和API都是昨天收盘数据）
      盘中(09:30-15:00): ΔT=1（API是今天实时，ZHB是昨天）
      盘后(15:00-16:30): ΔT=1（API是今天收盘，ZHB是昨天）
      盘后(16:30后): ΔT=0（新ZHB已生成）
      非交易日: ΔT=0（都是上一交易日数据）
    """
    try:
        from stock_common import get_zhb_data_date
        from stock_common.stock_calendar import is_workday, get_last_trading_day

        zhb_date_str = get_zhb_data_date()
        zhb_date = _parse_zhb_date(zhb_date_str)
        if zhb_date is None:
            return 99

        today = datetime.now().date()
        now = datetime.now()

        last_td = get_last_trading_day(today)

        if is_workday(today):
            if now.hour < 9 or (now.hour == 9 and now.minute < 30):
                if zhb_date >= last_td - timedelta(days=1):
                    return 0
                return (last_td - zhb_date).days
            elif now.hour >= 16:
                if zhb_date >= last_td:
                    return 0
                return (last_td - zhb_date).days
            else:
                if zhb_date >= last_td - timedelta(days=1):
                    return 1
                return (last_td - zhb_date).days + 1
        else:
            if zhb_date >= last_td:
                return 0
            return (last_td - zhb_date).days
    except Exception:
        return _get_zhb_date_offset()


# ═══════════════════════════════════════════════════
# 原子数据获取函数
# ═══════════════════════════════════════════════════


@cached(category="stock_quote", ttl_seconds=15)
def get_stock_price(code: str) -> Optional[float]:
    """获取股票实时价格。

    优先级：ZHB(盘后) → TDX(TCP+内部缓存) → 腾讯(HTTP fallback)
    TTL：15秒（盘中快速刷新，盘后及开盘前走ZHB本地解析）
    """
    if _should_use_zhb_for_realtime():
        try:
            from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh

            if is_zhb_data_fresh(max_delay_days=1):
                zhb = get_zhb_single_stock_data(code)
                if zhb:
                    price = _safe_float(zhb.get("price", 0))
                    if price > 0:
                        return price
        except Exception as _e:
            _debug_log(f"data_provider error: {_e}")
            pass

    # TDX优先（TCP协议，内部含缓存+腾讯兜底补强）
    try:
        from core.tdx_client import tdx_get_quote_full

        q = tdx_get_quote_full(code)
        if q:
            p = _safe_float(q.get("price", 0))
            if p > 0:
                return p
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # 腾讯HTTP最后兜底
    try:
        from stock_common import get_tencent_quote

        q = get_tencent_quote(code)
        if q:
            return _safe_float(q.get("price", 0))
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["dividend"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False),
)  # V15.2: 拒绝 None/空（但允许 0 值）
def get_dividend_yield(code: str) -> Optional[float]:
    """获取股息率。

    静态字段：ZHB only（TDX和腾讯都不直接返回股息率，ZHB有完整数据）。
    TTL：30天（分红半年才变，价格驱动日变但30天足够）。
    """
    try:
        from stock_common import get_zhb_dividend_yield, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=3):
            yield_val = get_zhb_dividend_yield(code)
            if yield_val:
                return yield_val
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(category="stock_quote", ttl_seconds=1800, trading_day=True)
def get_change_pct(code: str) -> Optional[float]:
    """获取涨跌幅。

    优先级：ZHB(盘后) → TDX(TCP+内部缓存) → 腾讯(HTTP fallback)
    TTL：30分钟 + 交易日模式
    """
    if _should_use_zhb_for_realtime():
        try:
            from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh

            if is_zhb_data_fresh(max_delay_days=1):
                zhb = get_zhb_single_stock_data(code)
                if zhb:
                    change_pct = _safe_float(zhb.get("change_pct", 0))
                    if change_pct != 0 or zhb.get("price", 0) > 0:
                        return change_pct
        except Exception as _e:
            _debug_log(f"data_provider error: {_e}")
            pass

    # TDX优先（TCP协议，内部含缓存+腾讯兜底补强）
    try:
        from core.tdx_client import tdx_get_quote_full

        q = tdx_get_quote_full(code)
        if q:
            return _safe_float(q.get("change_pct", 0))
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # 腾讯HTTP最后兜底
    try:
        from stock_common import get_tencent_quote

        q = get_tencent_quote(code)
        if q:
            return _safe_float(q.get("change_pct", 0))
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False),
)  # V15.2: 拒绝 None/空
def get_change_ytd(code: str) -> Optional[float]:
    """获取年初至今涨幅。

    静态字段：优先ZHB → K线计算。
    """
    try:
        from stock_common import get_zhb_change_ytd, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=3):
            return get_zhb_change_ytd(code)
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # Fallback：从TDX K线数据近似计算年初至今涨幅
    try:
        from core.tdx_client import tdx_get_security_bars

        keys, rows = tdx_get_security_bars(code, count=260)
        if keys and rows:
            idx_close = keys.index('close') if 'close' in keys else 2
            current_price = _safe_float(rows[0][idx_close])
            # rows从新到旧，取约250个交易日前作为年初近似
            if len(rows) >= 2:
                year_start_idx = min(len(rows) - 1, 243)
                year_start_price = _safe_float(rows[year_start_idx][idx_close])
                if year_start_price > 0 and current_price > 0:
                    return (current_price - year_start_price) / year_start_price * 100
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(category="stock_quote", ttl_seconds=1800, trading_day=True)
def get_amount_wan(code: str) -> Optional[float]:
    """获取成交额（万元）。

    V15.1: 优先级 ZHB（T-1）→ 腾讯 HTTP → TDX TCP
    盘中/盘后/盘前都用 ZHB T-1 数据（1 天延迟可接受），
    ZHB 缺失时降级到腾讯/TDX 实时数据。
    TTL：30分钟 + 交易日模式
    """
    # 优先级 1：ZHB（T-1 数据，1 天延迟可接受；V16.3 M: A 类仅盘前/非交易日可用——
    # 9:30-24:00 含盘后 ZHB 仍为 T-1，不接受当日成交额用 T-1）
    try:
        from stock_common import get_zhb_amount_wan, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=1) and _should_use_zhb_for_realtime():
            amount = get_zhb_amount_wan(code)
            if amount and amount > 0:
                return amount
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass

    # Fallback 1：腾讯 HTTP（实时，但仅盘中使用）
    try:
        from stock_common import get_tencent_quote

        q = get_tencent_quote(code)
        if q:
            # V16.0: get_tencent_quote 返回的 amount_wan 已是万元（tdx_client.py:476），
            # 原代码读 amount 再 /10000 取不到值且单位错误
            amt = _safe_float(q.get("amount_wan", 0))
            if amt > 0:
                return amt
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # Fallback 2：TDX TCP
    try:
        from core.tdx_client import tdx_get_quote_full

        q = tdx_get_quote_full(code)
        if q:
            return _safe_float(q.get("amount_wan", 0))
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(),
)  # V15.2: 拒绝 None/空 dict/全 0
def get_main_net_buy(code: str) -> Optional[Dict[str, Any]]:
    """获取主力资金流向。

    V17.0 (2026-08-13 字典实锤): 统一口径——优先级 push2delay f137(当日权威, 与 canonical 一致)
    → ZHB T-1 → TDX 0x0011(实时兜底)。原"ZHB 优先"导致 sht 二章(本函数)与七章(canonical)
    显示不同日期/口径(实测 600276: 二章 2162万[8/12 ZHB] vs 七章 -22272万[8/13 f137])。
    """
    # L1: 东财 f137(今日权威, 与 canonical.main_net_buy_wan 同源)——盘后=当日最终, 盘中=15 分钟延时累计
    try:
        from stock_common.sc_datasource import get_em_quote_full_delay

        _ed = get_em_quote_full_delay(code) or {}
        if _ed.get("fund_main_today") not in (None, 0, '', '0', '0.0'):
            return {
                "main_net_buy_hands": 0,  # L5 终审修复: get_em_quote_full_delay 无 fund_main_hands 键, 恒 0
                "main_net_buy_hands_1d": 0,
                "main_net_buy_hands_2d": 0,
                "main_net_buy_amount": _safe_float(_ed.get("fund_main_today")) / 1e4,  # 元→万
                "main_net_buy_amount_1d": 0,
                "main_net_buy_amount_2d": 0,
                "source": "push2delay:f137",
            }
    except Exception as _e:
        _debug_log(f"data_provider error (f137 primary): {_e}")
    # L2: 盘前/非交易日用 ZHB T-1——⚠️ 2026-08-14 实锤: ZHB main_net_buy_amount 实为
    # **开盘金额(竞价额)**(19/19 恒正+占比<5%), 非主力净流入——已删除该分支
    try:
        from core.tdx_client import tdx_get_fund_flow, tdx_get_history_fund_flow

        ff = tdx_get_fund_flow(code)
        if ff:
            history = tdx_get_history_fund_flow(code, days=5)
            main_net_buy_hands_1d = 0
            main_net_buy_amount_1d = 0
            if history and len(history) >= 2:
                prev_day = history[1]
                # H3 修复(2026-08-15 二审): 历史资金流单位=元(东财 get_em_history_fund_flow),
                # 原样赋给 万元 字段 → T-1 主力净流入虚高 1e4 倍; 且 main_net_hands 键不存在→恒 0
                main_net_buy_amount_1d = _safe_float(prev_day.get("main_net", 0)) / 1e4  # 元→万
            return {
                "main_net_buy_hands": 0,  # 东财无手数字段, 恒 0(与 L1 一致)
                "main_net_buy_hands_1d": main_net_buy_hands_1d,
                "main_net_buy_hands_2d": 0,
                "main_net_buy_amount": _safe_float(ff.get("main_net_wan", 0)),
                "main_net_buy_amount_1d": main_net_buy_amount_1d,
                "main_net_buy_amount_2d": 0,
            }
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


def get_zt_streak_info(code: str) -> Dict[str, Any]:
    """V17.0.1a 统一层规范化: 涨停族信息(零网络, ZHB 本机).

    返回 {zt_lianban(连板天数), zt_type(涨停类型 0-1盘中/2+一字), zt_seal_amount(封单额万),
          zt_seal_amount_1d/2d(昨日/前日封单额)}——tdxstat[31]/[33] + tdxstat2[4]/[6]/[8]。
    V17.0.5 语义铁证(cross_analysis.md Part A): 封单额=limit_up_down_seal,
    涨停为正/跌停为负; 三日滚动 col4@T≡col6@T+1≡col8@T+2(全市场 1434/1434)。
    sht 连板追踪统一入口(替代直连 get_zhb_single_stock_data 散取)。
    """
    try:
        from stock_common.sc_datasource import get_zhb_single_stock_data

        z = get_zhb_single_stock_data(code) or {}
        return {
            "zt_lianban": int(z.get("zt_lianban", 0) or 0),
            "zt_type": int(z.get("zt_type", -1) if z.get("zt_type") is not None else -1),
            "zt_seal_amount": float(z.get("zt_seal_amount", 0) or 0),
            "zt_seal_amount_1d": float(z.get("zt_seal_amount_1d", 0) or 0),
            "zt_seal_amount_2d": float(z.get("zt_seal_amount_2d", 0) or 0),
        }
    except Exception as _e:
        _debug_log(f"data_provider get_zt_streak_info ({code}): {_e}")
        return {}


def calc_mcap_yi(code: str, price: Optional[float] = None) -> Optional[float]:
    """计算总市值（亿元）。

    动态计算：总股本(本地静态) × 实时价格(API)。
    V17.0.1(2026-08-16 性能修复): 股本优先 TDX 本机 base.dbf(标准 DBF, 零网络毫秒级)——
    原 get_share_capital 缓存未命中时逐股 TDX TCP(6000+ 只=700s+, val 加载 811s 根因)。
    """
    if price is None:
        price = get_stock_price(code)
    if not price or price <= 0:
        return None
    total_wan = _local_share_capital(code)
    if not total_wan:
        try:
            from stock_common import get_share_capital

            cap = get_share_capital(code)
            total_wan = cap.get("total_shares", 0)
        except Exception as _e:
            _debug_log(f"data_provider error: {_e}")
            return None
    if total_wan > 0:
        return price * total_wan / 10000.0
    return None


_BASE_DBF_SHARES: Optional[Dict[str, float]] = None  # V17.0.1: base.dbf 总股本(万股) 模块级缓存


def _local_share_capital(code: str) -> float:
    """TDX 本机 base.dbf 总股本(万股)——零网络(标准 DBF, 7880 只, 一次性加载缓存).

    V17.0.1: base.dbf 已全解(§四 客户端文件表)——ZGB 字段=总股本(万股)。
    """
    global _BASE_DBF_SHARES
    if _BASE_DBF_SHARES is None:
        try:
            import struct as _st

            _p = r"C:\new_tdx64\T0002\hq_cache\base.dbf"
            with open(_p, "rb") as _f:
                _raw = _f.read()
            _nrec, _hlen, _rlen = _st.unpack_from("<I H H", _raw, 4)
            _fields = []
            _i = 32
            while _raw[_i] != 0x0D:
                _name = _raw[_i:_i + 11].split(b"\x00")[0].decode("gbk", "ignore")
                _fields.append((_name, _raw[_i + 16]))
                _i += 32
            _zgb_idx = next((k for k, (n, _) in enumerate(_fields) if n == "ZGB"), -1)
            _gpd_idx = next((k for k, (n, _) in enumerate(_fields) if n == "GPDM"), -1)
            _pos = _hlen + 1
            _map: Dict[str, float] = {}
            for _r in range(_nrec):
                if _gpd_idx < 0 or _zgb_idx < 0:
                    break
                _code = _raw[_pos:_pos + _rlen].decode("gbk", "ignore")
                # 按字段偏移解析(GPDM/ZGB 位置固定, 逐字段累计偏移)
                _off = _pos
                _code_v = ""
                _zgb_v = 0.0
                for _k, (_n, _l) in enumerate(_fields):
                    _seg = _raw[_off:_off + _l].decode("gbk", "ignore").strip()
                    if _k == _gpd_idx:
                        _code_v = _seg
                    elif _k == _zgb_idx:
                        try:
                            _zgb_v = float(_seg)
                        except ValueError:
                            _zgb_v = 0.0
                    _off += _l
                if _code_v and _zgb_v > 0:
                    _map[_code_v] = _zgb_v
                _pos += _rlen
            _BASE_DBF_SHARES = _map
        except Exception as _e:
            _debug_log(f"data_provider base.dbf shares load error: {_e}")
            _BASE_DBF_SHARES = {}
    return float(_BASE_DBF_SHARES.get(code, 0.0) or 0.0)


@cached(category="basic_info_static", ttl_seconds=TTL["basic_info_static"])
def get_stock_info(code: str) -> Optional[Dict[str, Any]]:
    """获取股票基本信息（综合）。"""
    try:
        from stock_common import get_stock_info

        return get_stock_info(code)
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


# ═══════════════════════════════════════════════════
# 新增常用字段函数
# ═══════════════════════════════════════════════════


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False),
)  # V15.2: 拒绝 None/空
def get_turnover_pct(code: str) -> Optional[float]:
    """V12.6: turnover_pct uses ZHB only, no HTTP fallback.
    V16.3 M: 换手率归 A 类（当日即时指标）——9:30-24:00 不接受 ZHB T-1，
    仅盘前/非交易日用 ZHB；运行时 canonical 的腾讯兜底接管（get_canonical_stock_data）。
    """
    try:
        from stock_common import get_zhb_single_stock_data

        if _should_use_zhb_for_realtime():
            zhb = get_zhb_single_stock_data(code)
            if zhb:
                turnover = _safe_float(zhb.get("turnover_pct", 0))
                if turnover > 0:
                    return turnover
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(check_zeros=False),
)  # V15.2: 拒绝 None/空
def get_streak_days(code: str) -> Optional[int]:
    """获取连涨连跌天数。

    正=连涨，负=连跌，0=震荡。
    准实时字段：优先ZHB → K线计算。
    """
    try:
        from stock_common import get_zhb_streak_days, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=1) and _should_use_zhb_for_realtime():
            return get_zhb_streak_days(code)
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    # Fallback：从TDX K线数据计算连涨连跌天数
    try:
        from core.tdx_client import tdx_get_security_bars

        keys, rows = tdx_get_security_bars(code, count=20)
        if keys and rows and len(rows) >= 2:
            idx_close = keys.index('close') if 'close' in keys else 2
            closes = [_safe_float(r[idx_close]) for r in rows if r[idx_close]]
            if len(closes) >= 2:
                # rows从新到旧，比较连续同方向
                streak = 0
                if closes[0] > closes[1]:
                    # 连涨
                    for i in range(len(closes) - 1):
                        if closes[i] > closes[i + 1]:
                            streak += 1
                        else:
                            break
                elif closes[0] < closes[1]:
                    # 连跌
                    for i in range(len(closes) - 1):
                        if closes[i] < closes[i + 1]:
                            streak -= 1
                        else:
                            break
                return streak
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(),
)  # V15.2: 拒绝 None/空 dict/全 0
def get_volume_acceleration(code: str) -> Optional[Dict[str, Any]]:
    """量能三连击因子（纯ZHB数据，无需实时T数据）。

    检测放量加速趋势：ZHB中amount > amount_1d > amount_2d 成交额递增。
    全部使用ZHB内部数据（文件名日期为基准日），时间维度完全对齐。

    ZHB时间体系说明：
      - amount: ZHB文件名日期的成交额（基准日）
      - amount_1d: 基准日前一交易日成交额
      - amount_2d: 基准日前两交易日成交额
      - 实际运行时，ZHB数据日期 = 脚本运行日期 - 1个交易日（次日更新机制）

    返回字典：
      amount_t_1: 基准日成交额（万元）
      amount_t_2: 前一交易日成交额（万元）
      amount_t_3: 前两交易日成交额（万元）
      is_accelerating: 是否放量加速（amount > amount_1d > amount_2d）
      acceleration_ratio: 加速比率（amount/amount_1d）
    """
    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh

        if not is_zhb_data_fresh(max_delay_days=3):
            return None

        zhb = get_zhb_single_stock_data(code)
        if not zhb:
            return None

        amount_t_1 = _safe_float(zhb.get("amount", 0)) if zhb.get("amount", 0) else 0
        amount_t_2 = _safe_float(zhb.get("amount_1d", 0))
        amount_t_3 = _safe_float(zhb.get("amount_2d", 0))

        if amount_t_1 <= 0 or amount_t_2 <= 0 or amount_t_3 <= 0:
            return None

        is_acc = amount_t_1 > amount_t_2 and amount_t_2 > amount_t_3
        accel_ratio = amount_t_1 / amount_t_2

        return {
            "amount_t_1": amount_t_1,
            "amount_t_2": amount_t_2,
            "amount_t_3": amount_t_3,
            "is_accelerating": is_acc,
            "acceleration_ratio": accel_ratio,
        }
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(),
)  # V15.2: 拒绝 None/空 dict/全 0
def get_capital_momentum(code: str) -> Optional[Dict[str, Any]]:
    """资金动量加速因子（纯ZHB数据，无需实时T数据）。

    ⚠️ V17.0(2026-08-14)实锤修正: main_net_buy_amount/1d 实为**竞价额/昨日竞价额**(竞价量×价 15/17 铁证),
    非主力净流入——本函数实际检测的是**竞价强度加速度**(今昨竞价额变化), 语义=竞价动量代理。
    val 策略21"资金动量"基于此——若需真主力资金请改用东财 f137(批量场景待方案)。

    ZHB时间体系说明：
      - main_net_buy_amount: ZHB文件名日期的竞价额（基准日, 键名历史遗留）
      - main_net_buy_amount_1d: 基准日前一交易日竞价额
      - 实际运行时，ZHB数据日期 = 脚本运行日期 - 1个交易日（次日更新机制）

    返回字典：
      net_buy_t_1: 基准日竞价额（万元, 键名历史遗留）
      net_buy_t_2: 前一交易日竞价额（万元）
      momentum: 动量值（竞价额加速度）
      momentum_ratio: 动量比率（相对变化率）
      signal: 信号标签（抢筹加速期/衰竭期/平稳）
    """
    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh

        if not is_zhb_data_fresh(max_delay_days=3):
            return None

        zhb = get_zhb_single_stock_data(code)
        if not zhb:
            return None

        net_buy_t_1 = _safe_float(zhb.get("main_net_buy_amount", 0))
        net_buy_t_2 = _safe_float(zhb.get("main_net_buy_amount_1d", 0))

        if net_buy_t_1 == 0 and net_buy_t_2 == 0:
            return None

        momentum = net_buy_t_1 - net_buy_t_2
        momentum_ratio = (
            momentum / abs(net_buy_t_2)
            if net_buy_t_2 != 0
            else float('inf') if momentum > 0 else float('-inf')
        )

        signal = "平稳"
        if momentum > 0:
            if momentum_ratio > 0.3:
                signal = "抢筹加速期"
            elif momentum_ratio > 0:
                signal = "温和流入"
        else:
            if momentum_ratio < -0.5:
                signal = "衰竭期"
            elif momentum_ratio < 0:
                signal = "流入放缓"

        return {
            "net_buy_t_1": net_buy_t_1,
            "net_buy_t_2": net_buy_t_2,
            "momentum": momentum,
            "momentum_ratio": momentum_ratio,
            "signal": signal,
        }
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return None


# ═══════════════════════════════════════════════════
# 市场快照
# ═══════════════════════════════════════════════════


@cached(
    category="zhb_data",
    ttl_seconds=TTL["f10_fund_flow"],
    trading_day=True,
    valid_if=make_valid_if(min_size=1),
)  # V15.2: 至少 1 只股票才缓存
def get_market_snapshot(codes: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """获取市场快照。

    V12.6 优化路径：
      1. 优先 ZHB 全量快照 (ZHB_SUFFICIENT 字段用此路径)
      2. fallback 到东财 push2 批量接口 (REQUIRES_REALTIME_HTTP 字段用此路径)
         - get_em_batch_quotes 内部自动分批 300/请求
      3. 注：V12.6 后不再有逐字段 HTTP 调用，性能提升显著
    """
    try:
        from stock_common import get_zhb_full_market_snapshot, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=3):
            snapshot = get_zhb_full_market_snapshot(codes)
            if snapshot:
                return snapshot
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    try:
        from stock_common import get_em_batch_quotes

        if codes:
            return get_em_batch_quotes(codes)
    except Exception as _e:
        _debug_log(f"data_provider error: {_e}")
        pass
    return {}


# ═══════════════════════════════════════════════════
# 高级数据聚合接口
# ═══════════════════════════════════════════════════




# ═══════════════════════════════════════════════════
# 异步版本函数
# ═══════════════════════════════════════════════════












async def get_main_net_buy_async(code: str, session=None) -> Optional[Dict[str, Any]]:
    """异步版：获取主力资金流向。"""
    return get_main_net_buy(code)


async def get_change_pct_async(code: str, session=None) -> Optional[float]:
    """异步版：获取涨跌幅。"""
    return get_change_pct(code)






async def get_turnover_pct_async(code: str, session=None) -> Optional[float]:
    """异步版：获取换手率。"""
    return get_turnover_pct(code)




async def get_market_snapshot_async(
    codes: Optional[List[str]] = None, session=None
) -> Dict[str, Dict[str, Any]]:
    """异步版：获取市场快照。"""
    return get_market_snapshot(codes)






# ═══════════════════════════════════════════════════════════════
# V13.1 dataclass 输出辅助 (opt-in，不影响现有 dict 调用方)
# ═══════════════════════════════════════════════════════════════






# V13.1: 第 3 个 dataclass opt-in 接口（roadmap 11.1 要求"3 个 dataclass 输出函数"）
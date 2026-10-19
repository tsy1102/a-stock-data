"""统一报告数据门面与字段路由。

``get_canonical_stock_data`` 返回 ``CanonicalStockData``，负责字段归一化、来源选择、
fallback 和逐字段 ``field_sources`` 溯源。ZHB 是否可用由交易时段和字段新鲜度共同决定；
不能把整层概括为全局 ZHB 优先。精确路由规则见 ``docs/architecture.md``。

路由维护时需要共同检查：
- ``sc_schema.FIELD_SPECS`` 中字段的实时性元数据；
- ``_should_use_zhb_for_realtime`` 与 ``get_canonical_stock_data`` 的实时行情判定；
- ``sc_datasource.zhb_field_safe`` 的逐字段快照延迟分级。

ZHB 文件名日期表示数据日期，不是采集时间。多日字段以各自的有效交易日偏移表示；
新闻和公告等自然日信息由对应专项适配器负责。缓存、专用字段和原始客户端边界
遵循 ``docs/ARCHITECTURE_THEORY.md`` 与 ``AGENTS.md``。
"""

from typing import Any, Dict, Optional, List

# Compatibility exports are consumed through core.data_provider by legacy adapters.
from core._accessors import (  # noqa: F401
    get_concept_from_zhb,
    get_dividend_yield as get_dividend_yield,
    get_change_pct,
    get_change_ytd as get_change_ytd,
    get_amount_wan as get_amount_wan,
    get_main_net_buy,
    get_streak_days as get_streak_days,
)
import math
from datetime import date, datetime

from core.stock_cache import (  # V15.2: 强化 valid_if
    cached,
    TTL,
    make_valid_if,
)


def _debug_log(msg: str) -> None:
    # V17.3 循环导入修复: 原顶层 from stock_common.sc_network import _fallback_logger
    # (data_provider.py:64) 是 stock_common↔data_provider 导入期环的触发点;
    # 改为函数内懒导入, 消除顶层跨引(运行期模块已全载, 必成功)。
    from stock_common.sc_network import _fallback_logger

    _fallback_logger.debug(msg)


def _safe_float(v) -> float:
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


# ─────────────────────────────────────────────────────────────
# V17.4.45: 报告个股批量路由——push2delay 基础行情 (300/批) + 腾讯补充字段 (60/批)
# SHT/MED/LNG 通常由每只股票的串行腾讯补取压缩为每组代码一次腾讯批量请求；
# L2 保存逐字段来源，canonical 不会把腾讯预热字段误标成 push2delay。
# ─────────────────────────────────────────────────────────────
_BATCH_QUOTE_CACHE: Dict[str, Dict[str, Any]] = {}
_BATCH_QUOTE_DATE: str = ""
_BATCH_QUOTE_TENCENT_ATTEMPTED: set[str] = set()
_BATCH_QUOTE_FIELD_SOURCES_KEY = "_field_sources"
_BATCH_QUOTE_UNKNOWN_SOURCE = "realtime:batch:source_unknown"
# V17.0: push2delay 估值/资金流补取进程缓存(当天)——sht 批量 35 只免重复请求
_PD_EXTRA_CACHE: Dict[str, Dict[str, Any]] = {}
_PD_EXTRA_CACHE_DATE: str = ""

# V17.0.7: fuyao 财务 TTM 族兜底进程缓存——键=(code, report_period), 报告期稳定
_FY_TTM_CACHE: Dict[Any, Dict[str, Any]] = {}


def _quote_has_value(value: Any) -> bool:
    return value not in (None, 0, "", "0", "0.0")


def _ensure_quote_cache_date() -> str:
    """Rotate process-local quote caches together at the local calendar-day boundary."""
    global _BATCH_QUOTE_DATE, _PD_EXTRA_CACHE_DATE

    today = datetime.now().strftime("%Y%m%d")
    if _BATCH_QUOTE_DATE != today:
        _BATCH_QUOTE_CACHE.clear()
        _BATCH_QUOTE_TENCENT_ATTEMPTED.clear()
        _BATCH_QUOTE_DATE = today
    if _PD_EXTRA_CACHE_DATE != today:
        _PD_EXTRA_CACHE.clear()
        _PD_EXTRA_CACHE_DATE = today
    return today


def prewarm_canonical_quote_cache(
    quote_map: Dict[str, Dict[str, Any]],
    *,
    source_label: str = "realtime:batch:source_unknown",
    skip_realtime_extras: bool = False,
    persist_l2: bool = True,
) -> int:
    """把已有批量行情安全地预热到统一层公开缓存入口。

    ``skip_realtime_extras`` 仅写入进程内的缺失哨兵，避免逐股补取不消费字段；
    哨兵不会进入 L2，防止其他报告把“跳过”误读成真实零值。
    """
    if not isinstance(quote_map, dict) or not quote_map:
        return 0

    _ensure_quote_cache_date()
    persisted: Dict[str, Dict[str, Any]] = {}
    warmed = 0
    normalized_source = str(source_label or _BATCH_QUOTE_UNKNOWN_SOURCE)
    for raw_code, raw_quote in quote_map.items():
        code = str(raw_code or "").strip()
        if code.isdigit() and len(code) < 6:
            code = code.zfill(6)
        if not code or not isinstance(raw_quote, dict) or not raw_quote:
            continue

        quote = {key: value for key, value in raw_quote.items() if not str(key).startswith("_")}
        if not _quote_has_value(quote.get("price")):
            continue
        sources = {
            key: normalized_source for key, value in quote.items() if _quote_has_value(value)
        }
        quote[_BATCH_QUOTE_FIELD_SOURCES_KEY] = sources
        _BATCH_QUOTE_CACHE[code] = quote
        persisted[code] = quote

        if skip_realtime_extras:
            _PD_EXTRA_CACHE[code] = {
                "pe_dynamic": _safe_float(quote.get("pe_dynamic") or 0),
                "fund_main_today": 0.0,
                "fund_main_5d": 0.0,
                "fund_super_today": 0.0,
                "fund_large_today": 0.0,
                "fund_mid_today": 0.0,
                "fund_small_today": 0.0,
            }
        warmed += 1

    if persist_l2 and persisted:
        try:
            from core.stock_cache import persist_quote_batch_l2

            persist_quote_batch_l2(persisted)
        except Exception as _e:
            _debug_log(f"prewarm_canonical_quote_cache L2 write: {_e}")
    return warmed


def _public_quote_batch_result(codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """去除缓存内部元数据，维持批量预取对调用方的业务字段视图。"""
    result: Dict[str, Dict[str, Any]] = {}
    for code in codes:
        quote = _BATCH_QUOTE_CACHE.get(code)
        if quote:
            result[code] = {key: value for key, value in quote.items() if not key.startswith("_")}
    return result


def prefetch_quote_batch(codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """批量准备个股行情：东财 push2delay 行情 + 腾讯批量补充字段。

    东财负责优先提供基础行情；腾讯批量仅补齐基础行情中没有的估值、财务比率、
    涨跌停和盘口字段。两者均按批获取，单只缺失时仍由统一层的逐股 fallback 兜底。
    内部缓存同时保留逐字段来源，公开返回值不暴露缓存元数据。
    """
    if not codes:
        return {}

    _ensure_quote_cache_date()

    missing = [c for c in codes if c not in _BATCH_QUOTE_CACHE]
    # 版本化 L2 只读含逐字段来源的快照，旧格式由缓存键升级自然失效。
    if missing:
        try:
            from core.stock_cache import read_quote_batch_l2

            _l2_map = read_quote_batch_l2(missing)
            for c, _l2 in _l2_map.items():
                if c in missing and isinstance(_l2, dict) and _l2:
                    _BATCH_QUOTE_CACHE[c] = dict(_l2)
            missing = [c for c in missing if c not in _BATCH_QUOTE_CACHE]
        except Exception as _e:
            _debug_log(f"prefetch_quote_batch L2 read: {_e}")

    # push2delay 按 300/批返回基础行情；估值空缺由下面的腾讯批量路由补齐。
    to_fetch = list(missing)
    if missing:
        try:
            from stock_common.sc_datasource import get_em_ulist_batch

            for item in get_em_ulist_batch(missing):
                code = str(item.get("f12", ""))
                if not code:
                    continue

                def _f(key: str, div: float = 1.0) -> float:
                    value = item.get(key)
                    if value is None or value in ("-", ""):
                        return 0.0
                    try:
                        return float(value) / div
                    except (ValueError, TypeError):
                        return 0.0

                quote: Dict[str, Any] = {
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
                quote[_BATCH_QUOTE_FIELD_SOURCES_KEY] = {
                    key: "realtime:push2delay:batch"
                    for key, value in quote.items()
                    if _quote_has_value(value)
                }
                _BATCH_QUOTE_CACHE[code] = quote
        except Exception as _e:
            _debug_log(f"prefetch_quote_batch push2delay error: {_e}")

    # 腾讯 qt.gtimg.cn 的 60/批返回包含 canonical 单股腾讯接口的主要补充字段。
    # 通常的逐股腾讯补取因而压缩为一批；不覆盖已有的 push2delay 基础行情。
    _tencent_required = ("roa", "pe_ttm", "roe_deduct_ttm", "limit_up", "limit_down")
    tencent_codes = [
        code
        for code in codes
        if code not in _BATCH_QUOTE_TENCENT_ATTEMPTED
        and any(
            not _quote_has_value(_BATCH_QUOTE_CACHE.get(code, {}).get(field))
            for field in _tencent_required
        )
    ]
    if tencent_codes:
        _BATCH_QUOTE_TENCENT_ATTEMPTED.update(tencent_codes)
        try:
            from core.tdx_client import _tencent_batch_fallback
            from core.stock_cache import TENCENT_REPORT_BATCH_CACHE_CATEGORY

            tencent_map = _tencent_batch_fallback(
                tencent_codes,
                use_l2_cache=True,
                cache_category=TENCENT_REPORT_BATCH_CACHE_CATEGORY,
            )
            for code, tencent_quote in tencent_map.items():
                if code not in tencent_codes or not isinstance(tencent_quote, dict):
                    continue
                quote = _BATCH_QUOTE_CACHE.setdefault(code, {})
                source_map = quote.get(_BATCH_QUOTE_FIELD_SOURCES_KEY)
                if not isinstance(source_map, dict):
                    source_map = {}
                for field, value in tencent_quote.items():
                    if field.startswith("_") or not _quote_has_value(value):
                        continue
                    if not _quote_has_value(quote.get(field)):
                        quote[field] = value
                        source_map[field] = "realtime:tencent:batch"
                    elif field not in source_map:
                        source_map[field] = _BATCH_QUOTE_UNKNOWN_SOURCE
                quote[_BATCH_QUOTE_FIELD_SOURCES_KEY] = source_map
        except Exception as _e:
            _debug_log(f"prefetch_quote_batch tencent batch: {_e}")

    # 落盘新版快照，供后续个股脚本跨进程复用。
    try:
        from core.stock_cache import persist_quote_batch_l2

        persist_quote_batch_l2(
            {c: _BATCH_QUOTE_CACHE[c] for c in to_fetch if c in _BATCH_QUOTE_CACHE}
        )
    except Exception as _e:
        _debug_log(f"prefetch_quote_batch L2 write: {_e}")

    return _public_quote_batch_result(codes)


# V12.6: field routing classification (run-time + field type)
#
# Decision rules（V12.6 原始设计描述）:
#   if runtime == pre_market:
#       -> all fields use ZHB
#   elif field in REQUIRES_REALTIME_HTTP:
#       -> HTTP (quote / fund flow)
#   else:
#       -> ZHB (valuation / finance / share / sector)
#
# ⚠️ 2026-08-30 校正：上面这段是 V12.6 的**设计意图**，已不是当前实际行为。
#    实际路由**不读取**下方两个集合做分支，而是由三处决定（详见 AGENTS.md §8.2 注记）：
#      1. _should_use_zhb_for_realtime()       —— 交易时段判定（本文件 :1394）
#      2. get_canonical_stock_data 内联三态     —— need_realtime_quote（本文件 :365-383）
#      3. sc_datasource.zhb_field_safe(field)  —— ABCD 新鲜度分级（A=0 / B=1 / C=3 / D=90 天）
#
#    下方 REQUIRES_REALTIME_HTTP / ZHB_SUFFICIENT 自 V14.2.1 起从 sc_schema.FIELD_SPECS
#    动态生成，现仅作为**测试契约元数据**存在（tests/core/test_core_routing.py 14 例、
#    test_core_schema.py 通过 is_realtime_http_field / is_zhb_sufficient_field 查询），
#    业务代码零调用 —— 删除会破坏回归，禁止删除。

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
            # V17.2.x(2026-09-10): change_30d 已删(实为 20 日值错误副本, 详见 sc_schema 说明)
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
    from core.canonical_metadata import (
        build_field_as_of_dates,
        canonical_data_source,
        filter_zhb_snapshot_fields,
        normalize_as_of_date,
        quote_time_anchor,
    )
    from core.zhb_client import (
        get_stock_name_from_zhb,
        get_stock_name_from_zhb_offline_only,
        cache_stock_name_from_network,
        normalize_persistent_name,
    )

    code_str = str(code).zfill(6)
    now = datetime.now()
    _ensure_quote_cache_date()
    is_today_trading = is_workday(now.date())

    t_val = now.hour * 100 + now.minute
    is_post_market = is_today_trading and (t_val >= 1500)
    is_trading_hours = is_today_trading and (930 <= t_val < 1500)

    # 1. 提取 ZHB 本地快照，并按每个原始字段的 ABCD 交易日阈值过滤。
    raw_zhb_dict: Dict[str, Any] = {}
    zhb_dict: Dict[str, Any] = {}
    zhb_data_date = ""
    stale_zhb_realtime_fields: List[str] = []
    try:
        from stock_common import get_zhb_single_stock_data
        from stock_common.sc_datasource import get_zhb_data_date
        from stock_common.sc_datasource._zhb import zhb_field_max_delay_days

        raw_zhb_dict = get_zhb_single_stock_data(code_str) or {}
        zhb_data_date = get_zhb_data_date() or ""
        zhb_dict = filter_zhb_snapshot_fields(raw_zhb_dict, zhb_data_date, as_of=now)
        stale_zhb_realtime_fields = [
            field_name
            for field_name in raw_zhb_dict
            if field_name != "report_date"
            and zhb_field_max_delay_days(field_name) == 0
            and field_name not in zhb_dict
        ]
        if len(zhb_dict) < len(raw_zhb_dict):
            _debug_log(
                f"canonical ZHB stale fields ({code_str}, {zhb_data_date or 'unknown'}): "
                f"{len(raw_zhb_dict) - len(zhb_dict)} rejected"
            )
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data get_zhb error: {_e}")

    # 判断行情与资金流是否需要走 HTTP / TDX 实时
    need_realtime_quote = (
        force_realtime
        or is_trading_hours
        or is_post_market
        or not zhb_dict
        or bool(stale_zhb_realtime_fields)
    )

    # V15.4 方案 C: per-field source label
    # 字典 key = 字段名 (e.g. "price", "mcap_yi", "industry")
    # 字典 value = 数据来源标签 (e.g. "realtime:push2", "realtime:tencent", "calculated", "missing")
    field_sources: Dict[str, str] = {}
    source_as_of_dates: Dict[str, str] = {}

    def _actual_realtime_source(field_name: str, default_family: str = "unknown") -> str:
        source = field_sources.get(field_name, "")
        if source:
            return source
        return f"realtime:{default_family}"

    def _record_source_as_of_date(source_family: str, payload: Any) -> None:
        """只接受 payload 明确标注的有效日期，不把采集日期当成数据日期。"""
        if not isinstance(payload, dict):
            return
        source_date = normalize_as_of_date(
            payload.get("as_of_date") or payload.get("source_as_of_date")
        )
        if source_date:
            source_as_of_dates[source_family] = source_date

    # 2. 实时/收盘行情 — V15.4 4 级 fallback 链
    # V16.0: 原 PUSH2_FIELD_MAP（f43/f44→price/high 映射表）已删除——
    # get_em_quote_full 直接返回规范字段名，L3 push2 fallback 直接遍历 em_quote_raw。
    rt_quote: Dict[str, Any] = {}  # 最终的行情 dict (cdata 字段名为 key)
    em_quote_raw: Dict[str, Any] = {}  # push2 原始字段 (f43/f44/...)

    if need_realtime_quote:
        # V17.4.45: 批量预取包含来源分明的 push2delay 基础行情与腾讯补充字段。
        # 命中后逐字段填充 rt_quote；仍保留 OHLC、微观结构和缺失字段的单股补源。
        _batch_hit = False
        _bq = _BATCH_QUOTE_CACHE.get(code_str)
        if _bq and _bq.get("price"):
            _batch_hit = True
            _batch_sources = _bq.get(_BATCH_QUOTE_FIELD_SOURCES_KEY)
            if not isinstance(_batch_sources, dict):
                _batch_sources = {}
            for _k, _v in _bq.items():
                if _k.startswith("_"):
                    continue
                if _v not in (None, 0, "", "0", "0.0"):
                    rt_quote[_k] = _v
                    field_sources[_k] = _batch_sources.get(_k) or _BATCH_QUOTE_UNKNOWN_SOURCE
            _debug_log(f"get_canonical_stock_data batch prefetch hit ({code_str})")
        # 行情 fallback 顺序由下方内联分支实现，并由
        # tests/core/test_quote_fallback_order.py 对实际调用顺序做回归验证。
        # L1: TDX 实时——V17.0 修复: prefetch 命中后跳过(原无条件执行, 35 只批量白做 35 次 TCP)
        # V17.0.1c: 批量命中时批量数据无 OHLC(ulist 仅 15 精选字段) → OHLC 缺口补 TDX 快照
        _need_ohlc = not (rt_quote.get("open") and rt_quote.get("high") and rt_quote.get("low"))
        if not _batch_hit or _need_ohlc:
            try:
                from core.tdx_client import tdx_get_quote_full_with_sources

                _tdx, _tdx_sources = tdx_get_quote_full_with_sources(code_str)
                _tdx = _tdx or {}
                _tdx_sources = _tdx_sources or {}
                _record_source_as_of_date("tdx", _tdx)
                if _batch_hit and _need_ohlc:
                    for _k in ("open", "high", "low", "last_close"):
                        if _tdx.get(_k) not in (None, 0, "", "0", "0.0"):
                            rt_quote[_k] = _tdx[_k]
                            field_sources[_k] = _tdx_sources.get(_k, "source:unknown")
                elif _tdx.get("price"):
                    rt_quote = _tdx
                    for _k in _tdx:
                        if _k in ("data_date", "as_of_date", "source_as_of_date", "collected_at"):
                            continue
                        field_sources[_k] = _tdx_sources.get(_k, "source:unknown")
            except Exception as _e:
                _debug_log(f"get_canonical_stock_data tdx_get_quote_full error: {_e}")

        # L2: 腾讯行情 (V16 端口优先级: 不封 IP，优先于 push2；参考仓库: 腾讯/通达信优先)
        if not rt_quote.get("price"):
            try:
                from stock_common import get_tencent_quote

                _tencent = get_tencent_quote(code_str) or {}
                _record_source_as_of_date("tencent", _tencent)
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
            em_quote_raw = {}
            _em_source = ""
            try:
                from stock_common.sc_datasource import get_em_quote_full_delay

                em_quote_raw = get_em_quote_full_delay(code_str) or {}
                if em_quote_raw:
                    _em_source = "realtime:push2delay"
                    _record_source_as_of_date("push2delay", em_quote_raw)
            except Exception as _e:
                _debug_log(f"get_canonical_stock_data push2delay error ({code_str}): {_e}")
            if not em_quote_raw:
                try:
                    from stock_common.sc_datasource import get_em_quote_full

                    em_quote_raw = get_em_quote_full(code_str) or {}
                    if em_quote_raw:
                        _em_source = "realtime:push2"
                        _record_source_as_of_date("push2", em_quote_raw)
                except Exception as _e:
                    _debug_log(f"get_canonical_stock_data push2 error ({code_str}): {_e}")
            if em_quote_raw:
                # V16.0: get_em_quote_full* 返回的已是规范字段名（price/high/low/...），
                # 直接遍历合并。原 PUSH2_FIELD_MAP 用 f43/f44/... 去 .get() 拿不到值 → push2 兜底从未生效。
                for f_cdata, _v in em_quote_raw.items():
                    if f_cdata in ("name", "industry", "board", "list_date", "data_date"):
                        rt_quote[f_cdata] = _v
                        field_sources[f_cdata] = _em_source
                        continue
                    if _v not in (None, 0, '', '0', '0.0'):
                        # 数值字段转 float（push2 数值可能为字符串）
                        # V16.4.1: 原条件写反——"非字符串才转 float"导致字符串原样保留, 注释意图从未生效
                        try:
                            rt_quote[f_cdata] = float(_v) if isinstance(_v, str) else _v
                        except (ValueError, TypeError):
                            rt_quote[f_cdata] = _v
                        field_sources[f_cdata] = _em_source
                if rt_quote.get("price"):
                    _debug_log(
                        f"get_canonical_stock_data push2delay fallback OK ({code_str}) — {len(rt_quote)} fields mapped"
                    )

    # V16.3.3 (2026-08-10 字典 12.15.5/12.15.6): 腾讯独有/实时估值字段补取——
    # roa(tx66)/均价(tx51)/pe_ttm/pb/股息率为腾讯字段；
    # TDX 成功时 L2 fallback 不执行（TDX TCP 无 pe/pb/股息率），故主动补 1 次腾讯
    # （5rps 不封 IP，低成本）——C/D 层实时估值必须覆盖 ZHB T-1（19.88 vs 20.39 实测）
    # V17.0.6 修复: 去 need_realtime_quote 门控——roa/roe_deduct_ttm 为季报披露驱动的
    # 静态财务指标(TTM 滚动)，盘后完全可从腾讯获取(实测周六 1272.83/32.41 精确)，
    # 原门控导致盘后报告盈利质量对恒为 0(missing)
    if (
        not rt_quote.get("roa")
        or not rt_quote.get("pe_ttm")
        or not rt_quote.get("roe_deduct_ttm")
        or not rt_quote.get("limit_up")
        or not rt_quote.get("limit_down")
    ):
        try:
            from stock_common import get_tencent_quote

            _tq = get_tencent_quote(code_str) or {}
            _record_source_as_of_date("tencent", _tq)
            # V17.0 修复: 补取循环删 pe_dynamic——🔴2026-09-01 纠正：腾讯 [52]=f162=动态PE(pe_mrq, 字典实锤),
            # 非静态PE; 原注释"实为静态PE"系 2026-08-13 误订。pe_dynamic 只信 f162/fuyao, 不取腾讯[52]避免多源混用
            # V17.0.7: 删 main_net_inflow_yi(tx75 证伪=近180交易日涨幅, 非主力净流入)
            # V17.2.x(2026-09-10) 调整 A/B/C: avg_price 源 [85]→[51]、bid_ask_net 源 [86]→[50](+push2 f192)；
            #   增补 entrust_ratio([74])/bid2([12])/ask2([22]) 接线(字典 §12.8.12e canonical 实装)
            for _tf in (
                "roa",
                "roe_deduct_ttm",
                "avg_price",
                "beta",
                "bid_ask_net",
                "entrust_ratio",
                "bid2",
                "ask2",
                "pe_ttm",
                "pe_lyr",
                "pb",
                "dividend_yield",
                "limit_up",
                "limit_down",
            ):
                if _tq.get(_tf) not in (None, 0, '', '0', '0.0'):
                    rt_quote[_tf] = _tq[_tf]
                    field_sources[_tf] = "realtime:tencent"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data tencent extras error ({code_str}): {_e}")

    # V17.2.0: TDX 实时五档直解字段兜底（内盘/外盘/涨速/涨跌停价计算）——批量预取(ulist)路径下
    # TDX 未被咨询, 这些源生字段缺失; 主动补 1 次 TDX TCP(get_canonical_stock_data 已缓存, 命中即廉价)。
    # 优先级: 腾讯[47/48] > TDX get_price_limits 计算 > push2 f51/f52(已在上方填充)
    _need_tdx_supp = (
        "s_vol" not in rt_quote
        or "b_vol" not in rt_quote
        or "rise_speed" not in rt_quote
        or not rt_quote.get("limit_up")
        or not rt_quote.get("limit_down")
    )
    if _need_tdx_supp:
        try:
            from core.tdx_client import tdx_get_quote_full_with_sources as _tdx_qf

            _tdx_sup, _tdx_sup_sources = _tdx_qf(code_str)
            _tdx_sup = _tdx_sup or {}
            _tdx_sup_sources = _tdx_sup_sources or {}
            _record_source_as_of_date("tdx", _tdx_sup)
            for _k in ("s_vol", "b_vol", "rise_speed", "limit_up", "limit_down"):
                if _k not in rt_quote or rt_quote.get(_k) in (None, 0, '', '0', '0.0'):
                    _v = _tdx_sup.get(_k)
                    if _v not in (None, 0, '', '0', '0.0'):
                        rt_quote[_k] = _v
                        field_sources[_k] = _tdx_sup_sources.get(_k, "source:unknown")
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data tdx supplement error ({code_str}): {_e}")

    # V16.3.3 (2026-08-10 字典 12.15.5): fuyao 估值印证位——有 Key 才用（无 Key 自动跳过）：
    # 腾讯失败时 fuyao 兜底估值（pe_ttm/pb_mrq 实测=腾讯精确 20.385/6.22）；官方 REST 风控面独立
    # V17.0.6: 去 need_realtime_quote 门控——估值字段盘后同样可从 fuyao 获取(实测周六精确)
    if not rt_quote.get("pe_ttm") or not rt_quote.get("ps_ttm"):
        try:
            from stock_common.sc_fuyao import is_fuyao_enabled, get_fuyao_valuation

            if is_fuyao_enabled():
                _fv = get_fuyao_valuation([code_str]) or []
                if _fv:
                    _f0 = _fv[0]
                    _record_source_as_of_date("fuyao", _f0)
                    for _fk, _fsk in (
                        ("pe_ttm", "pe_ttm"),
                        ("pe_mrq", "pe_dynamic"),
                        ("pb_mrq", "pb"),
                        ("ps_ttm", "ps_ttm"),
                        ("pcf_ttm", "pcf_ttm"),
                    ):
                        if not rt_quote.get(_fsk) and _f0.get(_fk) not in (None, 0, '', '0', '0.0'):
                            rt_quote[_fsk] = _f0[_fk]
                            field_sources[_fsk] = "realtime:fuyao"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data fuyao valuation error ({code_str}): {_e}")

    # ⭐ V17.0.7 层级调整: fuyao 升为财务 TTM 族**主源**——报告期驱动静态值无需实时性,
    # 同花顺官方 REST 独立风控域(4001 退避, 无 push 封禁史), 盘后可查;
    # push2delay 降为兜底(见下方 _ed 块, 仅填缺失键)。用户运行时段多为盘后,
    # thsdk TCP 网关(仅盘中可用)已于 2026-09-07 移除——主力净流入统一走东财 f137, 不进通用 fallback 链。
    # 聚合式(经 600519 对撞: ocf_ttm/net_profit_period/net_profit_annual 与
    # push2 f103/f105/f109 逐字等): ocf_ttm = FY(Q4)+本期−去年同期(act_cash_flow_net);
    # revenue_ttm 同法(operating_income, ⚠️ 营业收入口径 vs f104 总收入差~1.8%);
    # eps_annual = net_profit_annual ÷ 总股本(sc_capital_cache 万股→股)。
    # **进程缓存(按 code+report_period)**: 报告期数据稳定, 当日同股只算一次
    if (
        not rt_quote.get("ocf_ttm")
        or not rt_quote.get("revenue_ttm")
        or not rt_quote.get("net_profit_period")
        or not rt_quote.get("eps_annual")
    ):
        try:
            from stock_common.sc_fuyao import is_fuyao_enabled

            if is_fuyao_enabled():
                _fy_key = (code_str, str(rt_quote.get("report_period") or ""))
                _fy_cached = _FY_TTM_CACHE.get(_fy_key)
                if _fy_cached is None:
                    from stock_common.sc_fuyao import (
                        get_fuyao_financials as _gff,
                        fnum_local as _fl,
                    )

                    def _series(kind, field):
                        rows = _gff(kind, code_str, limit=8) or []
                        out = {}
                        for r0 in rows:
                            key = (
                                int(r0.get("fiscal_year") or 0),
                                str(r0.get("fiscal_period") or ""),
                            )
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
                        if _yago is not None and _fy_ocf is not None:
                            _ocf = _fy_ocf + (_cf.get(_cur_key) or 0) - _yago
                            _rev_fyk = [k for k in _inc if k[1] == "Q4" and k[0] < _cur_y]
                            _rev_fy = _inc.get(max(_rev_fyk), 0) if _rev_fyk else 0
                            _np_fy = _npf.get(
                                max((k for k in _npf if k[1] == "Q4" and k[0] < _cur_y))
                            )
                            _fy_cached = {
                                "ocf_ttm": _ocf,
                                "revenue_ttm": _rev_fy
                                + (_inc.get(_cur_key) or 0)
                                - (_inc.get((_cur_y - 1, _cur_p)) or 0),
                                "net_profit_period": _npf.get(_cur_key),
                                "net_profit_annual": _np_fy,
                            }
                            _FY_TTM_CACHE[_fy_key] = _fy_cached
                if _fy_cached:
                    for _fk2 in (
                        "ocf_ttm",
                        "revenue_ttm",
                        "net_profit_period",
                        "net_profit_annual",
                    ):
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
                                rt_quote["eps_annual"] = _fy_cached["net_profit_annual"] / (
                                    _sh_wan * 1e4
                                )
                                field_sources["eps_annual"] = "calc:fuyao_np_annual/capital"
                        except Exception as _e2:
                            _debug_log(f"fuyao eps_annual calc error ({code_str}): {_e2}")
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data fuyao ttm primary error ({code_str}): {_e}")

    # V17.0 修复: push2delay 估值+资金流补取——TDX 成功路径(TCP 无 PE/资金流统计)缺
    # pe_dynamic/fund_*; 🔴2026-09-01 纠正：腾讯 [52]=f162=动态PE(字典实锤), 可作动态源参考但
    # 统一以 push2 f162 为权威动态PE; 注[53]=f163=静态PE(pe_lyr);
    # ⚠️ V17.0.7: 原"腾讯 tx75 主力净流入方向相反不可作首选"注释作废——tx75 实为
    # 近180交易日涨跌幅(非资金流, 语义完全不同), 资金流只信 push2delay f137 族。
    # 统一 push2delay f162/f137 一次请求补全。**无条件执行(盘前也补)**: 主力净流入为
    # 日级动态字段, 盘前/盘后均应显示最近交易日 f137(而非 ZHB T-1)——sht 二章/七章口径统一的关键。
    # **进程缓存(当天)**: sht 35 只批量每只 1 次 → 缓存命中免重复
    # **V17.0.7 层级**: 本块降为财务 TTM 族**兜底**——pe_dynamic/fund_* 维持无条件覆盖
    # (push2delay 唯一源), 财务四键仅在 fuyao 未填时补(不再覆盖 fuyao 主源值);
    # eps_deduct_ttm/undist_profit_ps 无 fuyao 对应, 仍由本块提供(push 独有字段)
    if not rt_quote.get("pe_dynamic") or rt_quote.get("fund_main_today") is None:
        _ed = _PD_EXTRA_CACHE.get(code_str)
        if _ed is None:
            try:
                from stock_common.sc_datasource import get_em_quote_full_delay

                _ed = get_em_quote_full_delay(code_str) or {}
                _record_source_as_of_date("push2delay", _ed)
                if _ed:
                    _PD_EXTRA_CACHE[code_str] = (
                        _ed  # V17.0: 仅非空缓存——失败下次重试(空缓存会污染测试/重试)
                    )
            except Exception as _e:
                _debug_log(f"get_canonical_stock_data push2delay pe/fund error ({code_str}): {_e}")
                _ed = {}
        if _ed.get("pe_dynamic") not in (None, 0, '', '0', '0.0'):
            rt_quote["pe_dynamic"] = _ed["pe_dynamic"]
            field_sources["pe_dynamic"] = "realtime:push2delay"
        for _fk in (
            "fund_main_today",
            "fund_main_5d",
            "fund_main_5d_pct",
            "fund_super_today",
            "fund_large_today",
            "fund_mid_today",
            "fund_small_today",
            # V17.2.1: 五档买/卖毛额(净额已在上方)——多空力道判断用
            "fund_main_buy",
            "fund_main_sell",
            "fund_super_buy",
            "fund_super_sell",
            "fund_large_buy",
            "fund_large_sell",
            "fund_mid_buy",
            "fund_mid_sell",
        ):
            # 资金流字段的 0 是有效净额，不代表源缺失；解析器只在上游实际给出字段时写入 key。
            if _fk in _ed and _ed.get(_fk) is not None:
                rt_quote[_fk] = _ed[_fk]
                field_sources[_fk] = "realtime:push2delay"
        # V17.2.1: 近5日主力净兜底 —— f178 数组聚合缺失时, 改用 ulist.np 端点 f164/f165。
        #   ⚠️ 口径铁律: 主域 stock/get 的 f164 = pe_ttm(估值), **绝不可取**;
        #      仅 ulist.np 端点的 f164 才是多日主力净(东财跨端点复用 f 编号)。
        if rt_quote.get("fund_main_5d") is None:
            try:
                from stock_common.sc_datasource import get_em_fund_flow_multiday

                _mm = get_em_fund_flow_multiday(code_str) or {}
                _record_source_as_of_date("push2delay", _mm)
                for _mk in ("fund_main_5d", "fund_main_5d_pct"):
                    if _mk in _mm and _mm.get(_mk) is not None:
                        rt_quote[_mk] = _mm[_mk]
                        field_sources[_mk] = "realtime:push2delay-ulist"
            except Exception as _e2:
                _debug_log(f"get_canonical_stock_data multiday fallback ({code_str}): {_e2}")
        # 财务族兜底——仅补缺失(fuyao 主源已填的键不覆盖); eps_deduct_ttm/
        # undist_profit_ps 为 push 独有, 直接补
        for _fk in (
            "ocf_ttm",
            "revenue_ttm",
            "net_profit_period",
            "net_profit_annual",
            "eps_deduct_ttm",
            "eps_annual",
            "undist_profit_ps",
        ):
            if not rt_quote.get(_fk) and _ed.get(_fk) not in (None, 0, '', '0', '0.0'):
                rt_quote[_fk] = _ed[_fk]
                field_sources[_fk] = "realtime:push2delay"

    # 3. 实时/收盘资金流
    rt_fund: Dict[str, Any] = {}
    if need_realtime_quote:
        try:
            from core.tdx_client import tdx_get_fund_flow

            rt_fund = tdx_get_fund_flow(code_str) or {}
            _record_source_as_of_date("tdx", rt_fund)
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data tdx_get_fund_flow error: {_e}")

    # 4. 字段清洗与 Boundary Validation (V15.4: 每字段独立 source 标签)
    basic_info = get_stock_basic_info_from_zhb(code_str)
    zhb_name = basic_info.get('name', '') if isinstance(basic_info, dict) else ''
    # name: 优先级 push2/tencent/tdx(网络) > ZHB 离线 > 持久化缓存(零网络)
    # V17.3.3 持久化名称缓存：get_stock_name_from_zhb 已内置 ZHB 离线→磁盘缓存链路
    offline_name = get_stock_name_from_zhb(code_str)
    name = str(rt_quote.get('name') or offline_name or '')
    # V17.3.3 写回：name 来自网络且 ZHB 离线缺失 → 写盘，避免重复联网
    if name and rt_quote.get('name') and not get_stock_name_from_zhb_offline_only(code_str):
        cache_stock_name_from_network(code_str, name)
    if not field_sources.get("name"):
        if name:
            # 来源比对用归一化主体名（剥离分红/次新等单日前缀，保留 ST），避免误标
            name_persist = normalize_persistent_name(name)
            if get_stock_name_from_zhb_offline_only(code_str) == name_persist:
                field_sources["name"] = "zhb:static"
            elif offline_name == name_persist:
                field_sources["name"] = "cache:persist"
            else:
                field_sources["name"] = "calculated"

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
            return _safe_float(zhb_default), "zhb:cache"
        if zhb_dict.get(field_name) not in (None, 0, '', '0', '0.0'):
            return _safe_float(zhb_dict.get(field_name)), "zhb:cache"
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
    change_pct, change_src = _extract_with_source(
        "change_pct", rt_quote.get("change_pct"), zhb_dict.get("change_pct")
    )
    field_sources["change_pct"] = field_sources.get("change_pct") or change_src or price_src
    open_p, open_src = _extract_with_source("open", rt_quote.get("open"), zhb_dict.get("open"))
    field_sources["open"] = field_sources.get("open", open_src)
    high_p, high_src = _extract_with_source("high", rt_quote.get("high"), zhb_dict.get("high"))
    field_sources["high"] = field_sources.get("high", high_src)
    low_p, low_src = _extract_with_source("low", rt_quote.get("low"), zhb_dict.get("low"))
    field_sources["low"] = field_sources.get("low", low_src)
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
    prev_close, prev_close_src = _extract_with_source(
        "prev_close", rt_quote.get("last_close"), zhb_dict.get("prev_close")
    )
    if rt_quote.get("last_close") and field_sources.get("last_close"):
        prev_close_src = field_sources["last_close"]
    # V17.0.1c: TDX/zhb 均无昨收(TDX 快照无 last_close)时, 用 price 与 change_pct 反算
    # M3(审查 2026-08-16): 反算加 sanity——change_pct 极端(如 -99.9, 可转债/退市整理无跌停保护)
    # 会放大昨收荒谬值; 反算结果必须落在 price*0.5~price*2 内才接受
    if not prev_close and price and change_pct:
        try:
            _pc = _safe_float(price / (1 + change_pct / 100.0))
            if _pc > 0 and (price * 0.5 <= _pc <= price * 2.0):
                prev_close = _pc
                prev_close_src = "calculated:price_change_pct"
            else:
                _debug_log(
                    f"get_canonical_stock_data prev_close 反算超界拒绝: price={price} chg={change_pct} pc={_pc}"
                )
        except (ZeroDivisionError, TypeError):
            prev_close = 0
    field_sources["prev_close"] = field_sources.get("prev_close", prev_close_src)
    amount_wan, amount_src = _extract_with_source(
        "amount_wan", rt_quote.get("amount_wan"), zhb_dict.get("amount")
    )
    field_sources["amount_wan"] = amount_src
    # V16.0: volume_hand 不再从 ZHB 兜底 — ZHB Col[24] 曾误映射为 volume(成交量)，
    # V17.0.9: Col[24] 已破解正名为 cash_reserve_wan(货币资金/万元, 静态财报字段)。
    # 真实成交量只能来自实时行情。
    volume_hand, volume_src = _extract_with_source("volume_hand", rt_quote.get("volume_hand"), None)
    field_sources["volume_hand"] = field_sources.get("volume_hand", volume_src)
    turnover_pct, turnover_src = _extract_with_source(
        "turnover_pct", rt_quote.get("turnover_pct"), zhb_dict.get("turnover_pct")
    )
    # V16.2.3 修复: TDX 0x010C 无换手率、ZHB 无此字段 → sht 换手率恒 0。
    # 腾讯行情 f38 有换手率且 @cached（命中无网络开销），补作兜底。
    if not turnover_pct:
        try:
            from stock_common import get_tencent_quote

            _tq = get_tencent_quote(code_str) or {}
            _record_source_as_of_date("tencent", _tq)
            _tv = _safe_float(_tq.get("turnover_pct") or 0)
            if _tv > 0:
                turnover_pct = _tv
                field_sources["turnover_pct"] = "realtime:tencent"
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data turnover tencent fallback error: {_e}")
    field_sources["turnover_pct"] = field_sources.get("turnover_pct", turnover_src)

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
        _actual_realtime_source("pe_ttm")
        if need_realtime_quote and rt_quote.get('pe_ttm')
        else ("zhb:static" if zhb_dict.get('pe_ttm') else field_sources.get("pe_ttm", "missing"))
    )
    # V16.3.3 (2026-08-10 字典 12.15.5): ROA 总资产收益率 — 腾讯 tx66（银行股精确：
    # 招行 1.12=年化 ROA/工行 0.67=年报 ROA 实测验证）；ZHB/push2delay 均无此字段
    # V17.0.5 正名: 口径实为 **TTM 滚动**（fuyao total_assets_net_ratio 同族；银行 TTM≈年报故曾误标"年化"）
    roa = _safe_float(rt_quote.get('roa') or 0)
    if roa > 0 and roa < 100:
        field_sources["roa"] = _actual_realtime_source("roa", "tencent")
    else:
        roa = 0.0
        field_sources["roa"] = "missing"
    # V17.0.5: 扣非加权 ROE(TTM 滚动) — 腾讯 tx65（fuyao index_deduct_weighted_avg_roe 同族，
    # 茅台 32.41 vs 官方 Q1 32.52；披露日跳变天然实验）——与 roa 成盈利质量对，lng 复利引擎口径升级候选
    roe_deduct_ttm = _safe_float(rt_quote.get('roe_deduct_ttm') or 0)
    if 0 < roe_deduct_ttm < 500:
        field_sources["roe_deduct_ttm"] = _actual_realtime_source("roe_deduct_ttm", "tencent")
    else:
        roe_deduct_ttm = 0.0
        field_sources["roe_deduct_ttm"] = "missing"
    if need_realtime_quote:
        pe_dynamic = _safe_float(rt_quote.get('pe_dynamic') or zhb_dict.get('pe_dynamic'))
    else:
        pe_dynamic = _safe_float(zhb_dict.get('pe_dynamic') or rt_quote.get('pe_dynamic'))
    field_sources["pe_dynamic"] = (
        _actual_realtime_source("pe_dynamic")
        if need_realtime_quote and rt_quote.get('pe_dynamic')
        else (
            "zhb:static"
            if zhb_dict.get('pe_dynamic')
            else field_sources.get("pe_dynamic", "missing")
        )
    )
    # V17.0.17(2026-09-01) 据主字典定案新增: 静态PE(LYR, f163) 透传。
    # 来源优先级: rt_quote(含 push2delay 已 merge 的 pe_lyr) > em_quote_raw(push2 原始) > 0(缺失)。
    # ZHB 离线包无静态PE字段([3]=动态/[9]=TTM), 故盘后/休市且仅 ZHB 兜底时 pe_lyr=0 → 下游展示 N/A(缺失不伪造)。
    pe_lyr = _safe_float(rt_quote.get('pe_lyr') or em_quote_raw.get('pe_lyr') or 0)
    if pe_lyr < 0 or pe_lyr > 10000:
        pe_lyr = 0.0
    if pe_lyr > 0:
        field_sources["pe_lyr"] = (
            _actual_realtime_source("pe_lyr", "push2")
            if rt_quote.get('pe_lyr')
            else "realtime:push2"
        )
    else:
        field_sources["pe_lyr"] = "missing"  # 静态PE 缺失(非所有源都有, 不伪造)
    # pb: ABCD 分层——C/D 层实时优先（腾讯/push2delay）；A/B 层 ZHB（ZHB 本无 pb，走计算）
    if need_realtime_quote:
        pb = _safe_float(rt_quote.get('pb') or zhb_dict.get('pb'))
    else:
        pb = _safe_float(zhb_dict.get('pb') or rt_quote.get('pb'))
    # V17.0.5: PS(TTM)/PCF(TTM)——fuyao valuation 独有维度(rt_quote 由 L503 补取注入)
    ps_ttm = _safe_float(rt_quote.get('ps_ttm') or 0)
    pcf_ttm = _safe_float(rt_quote.get('pcf_ttm') or 0)
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
    # V17.1: 总资产/净资产(资产负债表项)——TDX GetFinanceInfo(0x0010) 已 @cached, 边际代价低
    total_assets = 0.0
    net_assets = 0.0
    try:
        from core.tdx_client import tdx_get_finance_info

        _fin_bs = tdx_get_finance_info(code_str) or {}
        # zongzichan/jingzichan 单位=角(→元需/10), 字典§零·C line300/308 实锤
        total_assets = _safe_float(_fin_bs.get('zongzichan')) / 10.0
        net_assets = _safe_float(_fin_bs.get('jingzichan')) / 10.0
        if total_assets:
            field_sources["total_assets"] = "static:tdx_f10"
        if net_assets:
            field_sources["net_assets"] = "static:tdx_f10"
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data balance-sheet assets error ({code_str}): {_e}")
    field_sources["pb"] = (
        _actual_realtime_source("pb")
        if need_realtime_quote and rt_quote.get('pb')
        else ("zhb:static" if zhb_dict.get('pb') else field_sources.get("pb", "missing"))
    )
    # 股息率: ABCD 分层——C/D 层实时优先（腾讯 f126/push2delay，实测 3.86 vs ZHB T-1 3.97）
    if need_realtime_quote:
        dividend_yield = _safe_float(
            rt_quote.get('dividend_yield') or zhb_dict.get('dividend_yield')
        )
    else:
        dividend_yield = _safe_float(
            zhb_dict.get('dividend_yield') or rt_quote.get('dividend_yield')
        )
    field_sources["dividend_yield"] = (
        _actual_realtime_source("dividend_yield")
        if need_realtime_quote and rt_quote.get('dividend_yield')
        else (
            "zhb:static"
            if zhb_dict.get('dividend_yield')
            else field_sources.get("dividend_yield", "missing")
        )
    )
    # V15.4: 振幅/量比 (振幅 push2 f171 / 量比 腾讯 idx49·TDX快照; ⚠️ push2 f49 实为外盘, 非量比)
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
    # 元(主力净 = push2 f137；V17.0.16 重定案: f137 本身已是 超大单净(f140) + 大单净(f143)，
    # 旧版再 +f140 属重复计数，虚高约 40%。详见字典 §12.3.3)
    pd_main = _safe_float(rt_quote.get("fund_main_today"))
    _pd_main_source = field_sources.get("fund_main_today")
    # V17.0: 无条件 f137 优先(日级动态字段, 盘前/盘后均取最近交易日)——与 get_main_net_buy 同源
    # ⚠️ 2026-08-14 实锤: ZHB main_net_buy_amount 实为**开盘金额(竞价额)**(19/19 恒正+占比<5%),
    # 不可作主力净流入——ZHB 分支已移除
    if rt_quote.get("fund_main_today") is not None and _pd_main_source not in (None, "", "missing"):
        # V17.2.x(2026-09-10) 审计决策 Q1: 明确 main_net_buy_wan 与 fund_main_today 的主从关系——
        #   主: fund_main_today(push2 f137, 元)/1e4; 兜底: 下方 rt_fund['main_net_wan'](东财)。
        #   二者为同一指标的不同单位, 禁止再为其单独取数(双写会导致两值分叉)。
        main_net_buy_wan = pd_main / 1e4  # 元 → 万元
        field_sources["main_net_buy_wan"] = _actual_realtime_source("fund_main_today")
    else:
        main_net_buy_wan = _safe_float(rt_fund.get('main_net_wan'))
        field_sources["main_net_buy_wan"] = (
            "realtime:tdx" if rt_fund.get("main_net_wan") is not None else "missing"
        )
    # ⚠️ V17.0(2026-08-14): ZHB main_net_buy_hands 实为**早盘竞价量**(手, [9]×开盘≈[14] 铁证),
    # 不可作主力净买入量——非实时路径置 0, 主力净量仅信 TDX 0x0011(rt_fund)
    main_net_buy_hands = _safe_float(rt_fund.get('main_net_hands') if need_realtime_quote else 0)
    field_sources["main_net_buy_hands"] = (
        "realtime:tdx"
        if need_realtime_quote and rt_fund.get('main_net_hands') is not None
        else "missing"
    )
    # ⚠️ V17.0: ZHB main_net_buy_amount_1d 实为昨日开盘金额(竞价额)——不再作为主力净流入 T-1
    main_net_buy_wan_1d = 0.0
    field_sources["main_net_buy_wan_1d"] = "missing"

    # V17.2.x(2026-09-10) 审计 P2-1: 资金流四档恒等式**运行时校验**(不阻断, 仅告警)——
    #   字典 §12.3.3 实证 f137 = f140 + f143 / f135 = f138 + f141 / f136 = f139 + f142。
    #   上游直供值与派生值应一致; 显著偏离说明字段映射被改坏或端点语义漂移, 需人工介入。
    _fm = _safe_float(rt_quote.get("fund_main_today") or em_quote_raw.get("fund_main_today") or 0)
    _fs = _safe_float(rt_quote.get("fund_super_today") or em_quote_raw.get("fund_super_today") or 0)
    _fund_large = _safe_float(
        rt_quote.get("fund_large_today") or em_quote_raw.get("fund_large_today") or 0
    )
    if _fm and (_fs or _fund_large) and abs(_fm - (_fs + _fund_large)) > max(1.0, abs(_fm) * 0.01):
        try:
            _debug_log(
                f"data_provider 资金流恒等式偏离: f137({_fm:.0f}) != f140+f143({_fs + _fund_large:.0f}) "
                f"—— 疑似字段映射或端点语义漂移"
            )
        except Exception:
            pass

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
        field_sources["eps"] = _actual_realtime_source("eps", "push2")
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
    _cap: Dict[str, Any] = {}
    if not total_shares_wan:
        try:
            from stock_common.sc_capital_cache import get_share_capital as _get_cap

            _cap = _get_cap(code_str) or {}
            total_shares_wan = _safe_float(_cap.get('total_shares'))
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data total_shares fallback error: {_e}")
    # V17.3 修复(跨层同步): 阈值必须与 sc_capital_cache(v2, _CAPITAL_SCHEMA_VERSION=2)对齐——取 1e9 万股(=1e13 股, 远超任何 A 股)。
    # 旧阈值 1e7 少算一个数量级, 曾把正确大盘股万股值(工农中建 2e7~3.6e7 万股)误当"股"再÷10000,
    # 致 total_shares_wan / mcap_yi 错 10000 倍(sc_capital_cache 注释已实锤此误伤)。统一层内联守卫须同步修正。
    if total_shares_wan > 1e9:
        total_shares_wan = total_shares_wan / 1e4
    if _safe_float(rt_quote.get('total_shares')) > 0:
        field_sources["total_shares_wan"] = field_sources.get("total_shares", "realtime:unknown")
    elif _safe_float(zhb_dict.get("total_shares")) > 0:
        field_sources["total_shares_wan"] = "zhb:static"
    elif _safe_float(_cap.get("total_shares")) > 0:
        field_sources["total_shares_wan"] = "cache:share_capital:source_unknown"
    else:
        field_sources["total_shares_wan"] = "missing"
    float_shares_wan = _safe_float(rt_quote.get('float_shares') or zhb_dict.get('float_shares'))
    # V15.5.3: 流通股本兜底 — sc_capital_cache
    if not float_shares_wan:
        try:
            from stock_common.sc_capital_cache import get_share_capital as _get_cap

            _cap = _get_cap(code_str) or {}
            float_shares_wan = _safe_float(_cap.get('float_shares'))
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data float_shares fallback error: {_e}")
    if _safe_float(rt_quote.get('float_shares')) > 0:
        field_sources["float_shares_wan"] = field_sources.get("float_shares", "realtime:unknown")
    elif _safe_float(zhb_dict.get("float_shares")) > 0:
        field_sources["float_shares_wan"] = "zhb:static"
    elif _safe_float(_cap.get("float_shares")) > 0:
        field_sources["float_shares_wan"] = "cache:share_capital:source_unknown"
    else:
        field_sources["float_shares_wan"] = "missing"
    # V17.3 同步(跨层一致): float_shares_wan 与 total_shares_wan 同源(均经 sc_capital_cache 万股归一),
    # 加相同 >1e9 防御, 防未来 rt_quote 加流通股本字段时"股"单位误入(与 total_shares_wan 守卫对称)
    if float_shares_wan > 1e9:
        float_shares_wan = float_shares_wan / 1e4

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
    # V17.3 同步(跨层一致): 与 mcap_yi(行1147 >1e6 万元→亿 守卫)对称, 防 zhb/rt_quote 万元单位误入
    if float_mcap_yi > 1e6:
        float_mcap_yi = float_mcap_yi / 1e4

    # V17.3.4 (2026-09-21): 市值双源一致性护栏（纯观测，非破坏性）。
    # 当直取市值可用时，与「股本×价」公式估值独立比对；偏差 > 2× 仅记 debug 告警，
    # 不改变取值（主路径已优先直取）。用于发现 rt_quote/ZHB 市值单位或股本缓存异常。
    if price and price > 0:
        if mcap_yi > 0 and total_shares_wan > 0:
            _est = round((total_shares_wan * 10000 * price) / 1e8, 2)
            if _est > 0 and (mcap_yi / _est > 2 or _est / mcap_yi > 2):
                _debug_log(
                    f"mcap_yi 双源偏差>{2}x ({code}): 直取={mcap_yi} 估算={_est} "
                    f"[src={field_sources.get('mcap_yi')}]"
                )
        if float_mcap_yi > 0 and float_shares_wan > 0:
            _fest = round((float_shares_wan * 10000 * price) / 1e8, 2)
            if _fest > 0 and (float_mcap_yi / _fest > 2 or _fest / float_mcap_yi > 2):
                _debug_log(
                    f"float_mcap_yi 双源偏差>{2}x ({code}): 直取={float_mcap_yi} 估算={_fest} "
                    f"[src={field_sources.get('float_mcap_yi')}]"
                )

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
    # V17.2.x(2026-09-10) 审计决策 Q2: change_30d **已删除**——
    #   tdxstat.cfg 无 30 日列, 该 key 实读 Col[18]=20 日值(与 change_20d 完全同值), 属带误导名的错误副本;
    #   真实 30 日需 TdxQuant ZAFPre30(当前无该依赖)。需要 30 日涨跌幅请由 K 线自算。
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
        _actual_realtime_source("high_52w")
        if rt_quote.get('high_52w')
        else ("zhb:static" if high_52w else "missing")
    )
    low_52w = _safe_float(rt_quote.get('low_52w') or zhb_dict.get('low_52w'))
    field_sources["low_52w"] = (
        _actual_realtime_source("low_52w")
        if rt_quote.get('low_52w')
        else ("zhb:static" if low_52w else "missing")
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
    field_sources["industry_code"] = "zhb:static" if industry_code else "missing"
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
        field_sources["industry_code"] = "missing"
    if not field_sources.get("board"):
        field_sources["board"] = "missing"
    # V17.0.32(2026-09-06): 市场类型枚举 sec_type（≡ ulist f182: 主板=2/创业板=5/科创板=32/北交所=80）。
    # 权威 L1 源为 ulist f182(主字典 2026-08-19 f182 定案 20/20 实锤); 统一层零网络,
    # 由代码前缀本地推导(与 f182 语义精确一致, ST 不改变市场类型归属)。
    try:
        from stock_common.sc_utils import get_sec_type_enum

        sec_type = get_sec_type_enum(code_str)
        field_sources["sec_type"] = "calculated"
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data sec_type error ({code_str}): {_e}")
        sec_type = 0
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
        from core._accessors import normalize_list_date

        _pinfo = get_stock_permanent_info(code_str) or {}
        _p_list_date = _pinfo.get("list_date")
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data permanent info error ({code_str}): {_e}")
        _p_list_date = None
    # V17.3.5 修正(报告审查 #362): 永久缓存可能残留残缺上市日期(如 '1998-04-')。
    # 归一化后若非完整 YYYY-MM-DD, 则 TDX 0x0010 ipo_date 兜底补全(本地 TCP, 廉价)。
    _raw_ld = _p_list_date or rt_quote.get("list_date") or em_quote_raw.get("list_date") or ""
    list_date = normalize_list_date(_raw_ld)
    _tdx_ipo_date = ""
    if not (len(list_date) == 10 and list_date[4] == "-" and list_date[7] == "-"):
        try:
            from core.tdx_client import tdx_get_finance_info

            _fi = tdx_get_finance_info(code_str) or {}
            if _fi.get("ipo_date"):
                _tdx_ipo_date = _fi["ipo_date"]
                _tdx_ld = normalize_list_date(_tdx_ipo_date)
                if _tdx_ld and len(_tdx_ld) == 10 and _tdx_ld[4] == "-" and _tdx_ld[7] == "-":
                    list_date = _tdx_ld
        except Exception as _e:
            _debug_log(f"get_canonical_stock_data list_date tdx fallback error ({code_str}): {_e}")
    if list_date and list_date not in ("None", "nan"):
        _normalized_p_list_date = normalize_list_date(_p_list_date) if _p_list_date else ""
        _normalized_rt_list_date = normalize_list_date(
            rt_quote.get("list_date") or em_quote_raw.get("list_date") or ""
        )
        if _normalized_p_list_date == list_date:
            field_sources["list_date"] = "static:permanent"
        elif _normalized_rt_list_date == list_date:
            field_sources["list_date"] = _actual_realtime_source("list_date")
        elif _tdx_ipo_date and normalize_list_date(_tdx_ipo_date) == list_date:
            field_sources["list_date"] = "tdx:0x0010"
        else:
            field_sources["list_date"] = "unknown"
    else:
        list_date = ""

    # 来源和时间锚点在装配完成后依据价格字段的来源与明确有效日期计算。

    # V17.2.22: eltdx 7709/7615 实时短线/连板指标经统一层暴露。
    # 只读模块级 bundle 缓存(由 get_eltdx_shortline_bundle 批量预热, 300s TTL);
    # 缓存未命中(未批量预热/TDX 源 eltdx 不可用)则留默认 —— 绝不 per-stock 触发取数(N+1 打爆 TDX TCP)。
    eltdx_ladder_level = 0
    eltdx_limit_up_streak_days = 0
    eltdx_limit_board_text = ""
    eltdx_seal_to_float_ratio = 0.0
    eltdx_open_volume_ratio = 0.0
    eltdx_seal_amount = 0.0
    eltdx_opening_rush = 0.0
    eltdx_auction_prev_volume_ratio = 0.0
    eltdx_open_prev_amount_ratio = 0.0
    eltdx_open_change_pct = 0.0
    eltdx_open_turnover_z = 0.0
    eltdx_has_shortline = False
    try:
        from core.eltdx_adapter import get_eltdx_shortline_for_code

        _eltdx = get_eltdx_shortline_for_code(code_str)
        if _eltdx:
            eltdx_ladder_level = int(_eltdx.get("ladder_level") or 0)
            eltdx_limit_up_streak_days = int(_eltdx.get("limit_up_streak_days") or 0)
            eltdx_limit_board_text = str(_eltdx.get("limit_board_text") or "")
            eltdx_seal_to_float_ratio = _safe_float(_eltdx.get("seal_to_float_ratio"))
            eltdx_open_volume_ratio = _safe_float(_eltdx.get("open_volume_ratio"))
            eltdx_seal_amount = _safe_float(_eltdx.get("seal_amount"))
            eltdx_opening_rush = _safe_float(_eltdx.get("opening_rush"))
            eltdx_auction_prev_volume_ratio = _safe_float(_eltdx.get("auction_prev_volume_ratio"))
            eltdx_open_prev_amount_ratio = _safe_float(_eltdx.get("open_prev_amount_ratio"))
            eltdx_open_change_pct = _safe_float(_eltdx.get("open_change_pct"))
            eltdx_open_turnover_z = _safe_float(_eltdx.get("open_turnover_z"))
            eltdx_has_shortline = True
            field_sources["eltdx_shortline"] = "eltdx:cache"
    except Exception as _e:
        _debug_log(f"get_canonical_stock_data eltdx enrichment error ({code_str}): {_e}")

    field_as_of_dates = build_field_as_of_dates(
        field_sources,
        source_as_of_dates,
        zhb_data_date=zhb_data_date,
    )
    quote_date = field_as_of_dates.get("price", "")
    price_source = field_sources.get("price", "missing")
    source_tag = canonical_data_source(price_source)
    collected_at_time = datetime.now().astimezone()
    time_anchor_tag = quote_time_anchor(quote_date, collected_at_time)
    collected_at = collected_at_time.isoformat(timespec="seconds")

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
        pe_lyr=pe_lyr,  # V17.0.17(2026-09-01) 据主字典定案新增: 静态PE(LYR, f163) 透传
        pb=pb,
        ps_ttm=ps_ttm,
        pcf_ttm=pcf_ttm,
        dividend_yield=dividend_yield,
        turnover_pct=turnover_pct,
        vol_ratio=vol_ratio,  # A: 量比透传(腾讯 idx49 / TDX快照; 字典 push2 f50≡量比; 旧注"push2 f49"与"上方:900"均误, f49=外盘)
        # V17.2.0: TDX 实时五档直解 内盘/外盘/涨速
        # V17.2.x(2026-09-10) 调整 D: 内盘/外盘合成——TDX实时(权威) > push2 f161/f49 > 腾讯[8]/[7]
        s_vol=_safe_float(rt_quote.get("s_vol") or em_quote_raw.get("s_vol") or 0),
        b_vol=_safe_float(rt_quote.get("b_vol") or em_quote_raw.get("b_vol") or 0),
        rise_speed=_safe_float(rt_quote.get("rise_speed") or 0),
        total_assets=total_assets,  # V17.1: 总资产(元, TDX f10 zongzichan/10)
        net_assets=net_assets,  # V17.1: 净资产/股东权益(元, TDX f10 jingzichan/10)
        main_net_buy_wan=main_net_buy_wan,
        main_net_buy_hands=main_net_buy_hands,
        # V17.2.x(2026-09-10) 审计: open_amount_wan / bid_volume_hand **已删除**——
        #   二者是 main_net_buy_wan / main_net_buy_hands 的**误名别名**: 注释标"竞价额/竞价量",
        #   实际值却是主力净(与 2026-08-14 实锤"ZHB 该族实为竞价额"的历史错位正相反), 名实不符且全仓零消费。
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
        sec_type=sec_type,  # V17.0.32(2026-09-06): 市场类型枚举(≡ ulist f182)
        concepts=tuple(concepts_list),
        data_source=source_tag,
        time_anchor=time_anchor_tag,
        collected_at=collected_at,
        # V17.2.x(2026-09-10) 审计决策 Q6: 真实质量门禁(原硬编码 True 且全仓零引用)
        #   停牌股 prev_close>0 仍判有效 → 不误杀; 完全取数失败(价与昨收皆 0)才判无效。
        is_valid=bool(code_str) and (price > 0 or prev_close > 0),
        # V15.4 方案 C: per-field source label
        field_sources=dict(field_sources),
        # V16.1: push2 扩展字段（f51/f52 涨停跌停、f55/f92 EPS/BPS、f126 股息率、
        # f162-167 PE/PB、f174/f175 52周、f137-146 资金流、f198 行业码、f80 交易时段、
        # f178 5日资金流数组、data_date 行情日期）— 从 rt_quote/em_quote_raw 透传
        limit_up=_safe_float(rt_quote.get("limit_up") or em_quote_raw.get("limit_up") or 0),
        limit_down=_safe_float(rt_quote.get("limit_down") or em_quote_raw.get("limit_down") or 0),
        bps=_safe_float(rt_quote.get("bps") or em_quote_raw.get("bps") or 0),
        # V17.0.31(2026-09-04) DEBT-003: pe_more 已删除（A2 无冗余别名）。
        #   它曾是 f164 的历史别名，但 f164 现统一映射为 pe_ttm（sc_datasource:6191），
        #   已无任何源产出 pe_more 键 → 该字段恒为 0，是死字段。
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
        # V17.2.x(2026-09-10) 调整 A/B/C: 统一层契约接线(字典 §12.8.12e canonical)
        # avg_price=均价/VWAP(腾讯[51]+TDX快照)、beta=腾讯[56]口径Beta估计、
        # bid_ask_net=委差(腾讯[50]+push2 f192)、entrust_ratio=委比%(腾讯[74]+push2 f191+TDX快照)、
        # bid2=买二价(腾讯[12]+tdx bid2)、ask2=卖二价(腾讯[22]+tdx ask2)
        avg_price=_safe_float(rt_quote.get("avg_price") or em_quote_raw.get("avg_price") or 0),
        beta=_safe_float(rt_quote.get("beta") or em_quote_raw.get("beta") or 0),
        bid_ask_net=_safe_float(
            rt_quote.get("bid_ask_net") or em_quote_raw.get("bid_ask_net") or 0
        ),
        entrust_ratio=_safe_float(
            rt_quote.get("entrust_ratio") or em_quote_raw.get("entrust_ratio") or 0
        ),
        bid2=_safe_float(rt_quote.get("bid2") or em_quote_raw.get("bid2") or 0),
        ask2=_safe_float(rt_quote.get("ask2") or em_quote_raw.get("ask2") or 0),
        quote_date=quote_date,
        field_as_of_dates=field_as_of_dates,
        fund_main_today=_safe_float(
            rt_quote.get("fund_main_today") or em_quote_raw.get("fund_main_today") or 0
        ),
        fund_super_today=_safe_float(
            rt_quote.get("fund_super_today") or em_quote_raw.get("fund_super_today") or 0
        ),
        fund_large_today=_safe_float(
            rt_quote.get("fund_large_today") or em_quote_raw.get("fund_large_today") or 0
        ),
        fund_mid_today=_safe_float(
            rt_quote.get("fund_mid_today") or em_quote_raw.get("fund_mid_today") or 0
        ),
        fund_main_5d=_safe_float(
            rt_quote.get("fund_main_5d") or em_quote_raw.get("fund_main_5d") or 0
        ),
        fund_small_today=_safe_float(
            rt_quote.get("fund_small_today") or em_quote_raw.get("fund_small_today") or 0
        ),
        fund_5d_array=tuple(
            rt_quote.get("fund_5d_array") or em_quote_raw.get("fund_5d_array") or ()
        ),
        # V17.2.1: 五档资金流买/卖毛额 + 近5日主力净占比
        fund_main_buy=_safe_float(
            rt_quote.get("fund_main_buy") or em_quote_raw.get("fund_main_buy") or 0
        ),
        fund_main_sell=_safe_float(
            rt_quote.get("fund_main_sell") or em_quote_raw.get("fund_main_sell") or 0
        ),
        fund_super_buy=_safe_float(
            rt_quote.get("fund_super_buy") or em_quote_raw.get("fund_super_buy") or 0
        ),
        fund_super_sell=_safe_float(
            rt_quote.get("fund_super_sell") or em_quote_raw.get("fund_super_sell") or 0
        ),
        fund_large_buy=_safe_float(
            rt_quote.get("fund_large_buy") or em_quote_raw.get("fund_large_buy") or 0
        ),
        fund_large_sell=_safe_float(
            rt_quote.get("fund_large_sell") or em_quote_raw.get("fund_large_sell") or 0
        ),
        fund_mid_buy=_safe_float(
            rt_quote.get("fund_mid_buy") or em_quote_raw.get("fund_mid_buy") or 0
        ),
        fund_mid_sell=_safe_float(
            rt_quote.get("fund_mid_sell") or em_quote_raw.get("fund_mid_sell") or 0
        ),
        fund_main_5d_pct=_safe_float(
            rt_quote.get("fund_main_5d_pct") or em_quote_raw.get("fund_main_5d_pct") or 0
        ),
        # V17.0.7: 财务 TTM 族(push2 f103-f190, fuyao 官方报表终判口径)——
        # 从 rt_quote/em_quote_raw 透传(get_em_quote_full* 已解析规范键)
        ocf_ttm=_safe_float(rt_quote.get("ocf_ttm") or em_quote_raw.get("ocf_ttm") or 0),
        revenue_ttm=_safe_float(
            rt_quote.get("revenue_ttm") or em_quote_raw.get("revenue_ttm") or 0
        ),
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
        # V17.2.22: eltdx 7709/7615 实时短线/连板指标(经统一层暴露, 读批量缓存)
        eltdx_ladder_level=eltdx_ladder_level,
        eltdx_limit_up_streak_days=eltdx_limit_up_streak_days,
        eltdx_limit_board_text=eltdx_limit_board_text,
        eltdx_seal_to_float_ratio=eltdx_seal_to_float_ratio,
        eltdx_open_volume_ratio=eltdx_open_volume_ratio,
        eltdx_seal_amount=eltdx_seal_amount,
        eltdx_opening_rush=eltdx_opening_rush,
        eltdx_auction_prev_volume_ratio=eltdx_auction_prev_volume_ratio,
        eltdx_open_prev_amount_ratio=eltdx_open_prev_amount_ratio,
        eltdx_open_change_pct=eltdx_open_change_pct,
        eltdx_open_turnover_z=eltdx_open_turnover_z,
        eltdx_has_shortline=eltdx_has_shortline,
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
        from stock_common.stock_calendar import is_workday

        now = datetime.now()
        today = now.date()
        if not is_workday(today):
            return True
        t = now.hour * 100 + now.minute
        return t < 930
    except Exception as _e:
        _debug_log(f"data_provider _should_use_zhb_for_realtime error: {_e}")
        return _get_market_status() != "trading"


def _parse_zhb_date(zhb_date_str: Optional[str]) -> Optional[date]:
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
    """计算 ZHB 数据日期相对当前有效行情日的交易日偏移。

    返回值：
      0 = ZHB 与当前有效行情日同日
      1+ = ZHB 落后相应数量的交易日
    """
    try:
        from stock_common import get_zhb_data_date
        from stock_common.stock_calendar import trading_day_age

        zhb_date_str = get_zhb_data_date()
        zhb_date = _parse_zhb_date(zhb_date_str)
        if zhb_date is None:
            return 99
        return max(0, trading_day_age(zhb_date, datetime.now()))
    except Exception:
        return 99


def _get_trading_date_offset() -> int:
    """计算ZHB数据日期相对于最新交易日的偏移量（ΔT）。

    这是日期对齐器的核心函数。它比较的是：
    - ZHB数据日期（T_zhb）
    - API行情能够获取到的最新交易日期（T_quote）

    交易日 9:30 前以最近已完成交易日为基准；9:30 起以当日为基准。
    周末、法定休市日和周末调休补班日均不增加偏移。
    """
    try:
        from stock_common import get_zhb_data_date
        from stock_common.stock_calendar import latest_market_data_date, trading_days_between

        zhb_date_str = get_zhb_data_date()
        zhb_date = _parse_zhb_date(zhb_date_str)
        if zhb_date is None:
            return 99

        now = datetime.now()
        reference_date = latest_market_data_date(now)
        return max(0, trading_days_between(zhb_date, reference_date))
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


def get_zt_streak_info(code: str) -> Dict[str, Any]:
    """V17.0.1a 统一层规范化: 涨停族信息(零网络, ZHB 本机).

    返回 {zt_lianban(连板数, tdxstat[33] ✅L1), zt_type(涨停类型, ZHB 无可靠源→恒 -1), zt_seal_amount(封单额万),
          zt_seal_amount_1d/2d(昨日/前日封单额)}——tdxstat[33]/[31] + tdxstat2[4]/[6]/[8]。
    V17.0.10: Col[33]=连板数(原 ztlx 涨停类型假设证伪), Col[31]=异动周期计数(⚠️, 非严格连板)。
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


def get_hot_concepts(code: str) -> List[Dict[str, Any]]:
    """V17.3.4 (2026-09-21): 热门概念访问器——零状态、lazy、try/except。

    沿用 get_zt_streak_info 的规范模式：不在 get_canonical_stock_data 热路径内调用
    （避免新增网络延迟），由各报告脚本在自身概念/热门段按需调用（与 get_sht_report.py:2203
    同款）。返回东财 em_hot_concept 概念列表 [{'concept','code','reason',...}]，异常时返回 []。
    """
    try:
        from stock_common import em_hot_concept

        return em_hot_concept(code) or []
    except Exception as _e:
        _debug_log(f"data_provider get_hot_concepts ({code}): {_e}")
        return []


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
                _name = _raw[_i : _i + 11].split(b"\x00")[0].decode("gbk", "ignore")
                _fields.append((_name, _raw[_i + 16]))
                _i += 32
            _zgb_idx = next((k for k, (n, _) in enumerate(_fields) if n == "ZGB"), -1)
            _gpd_idx = next((k for k, (n, _) in enumerate(_fields) if n == "GPDM"), -1)
            _pos = _hlen + 1
            _map: Dict[str, float] = {}
            for _r in range(_nrec):
                if _gpd_idx < 0 or _zgb_idx < 0:
                    break
                # 按字段偏移解析(GPDM/ZGB 位置固定, 逐字段累计偏移)
                _off = _pos
                _code_v = ""
                _zgb_v = 0.0
                for _k, (_n, _l) in enumerate(_fields):
                    _seg = _raw[_off : _off + _l].decode("gbk", "ignore").strip()
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

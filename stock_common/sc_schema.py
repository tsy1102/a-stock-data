# -*- coding: utf-8 -*-
"""sc_schema.py - V13.0 Schema 骨架（数据字段归一化层）

V13.0 设计目标：
  - 在数据源适配器边界处完成字段归一化（Normalize at Boundary）
  - 下游策略层零侵入：data.change_pct（不是 data.change_pct.value）
  - slots=True 节省内存，frozen=True 保证不可变

V13.0 阶段任务（roadmap 10.1-10.4）：
  - 仅定义骨架（Enum + dataclass）
  - 不接入 data_provider（保持 V12.x 完全兼容）
  - V13.1 才接入，V13.2 才迁移下游

设计原则（采纳 Gemini 建议 + 用户修正）：
  1. 边界归一化：数据源适配器在拿到原始数据的第一时间完成清洗
  2. slots=True 性能优化：dataclass 必须 @dataclass(slots=True, frozen=True)
  3. 访问语法保持简洁：下游使用 quote.change_pct 而非 quote.change_pct.value
  4. 不破坏现有代码：V13.0 仅定义骨架
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Tuple


# ═══════════════════════════════════════════════════════════════
# 枚举定义
# ═══════════════════════════════════════════════════════════════

class TimeAnchor(Enum):
    """时间锚点：标记数据属于哪个交易日。

    V12.6 修正：
      - ZHB 数据永远是 T-1（上一交易日）
      - HTTP 实时数据是 T_NOW（运行当日）
      - 物理上同一字段在不同源会有不同 TimeAnchor
    """
    T_DAY = "t_day"           # 脚本意义上的"今日"（用户期望的当日数据）
    T_MINUS_1 = "t-1"         # 上一交易日（ZHB 特征）
    T_OPEN = "t_open"          # 当日开盘价
    T_YEAR_START = "ytd"       # 年初至今
    UNKNOWN = "unknown"


class DataSource(Enum):
    """数据源标识。

    V12.6 修正：
      - ZHB 永远是上一交易日数据
      - HTTP 实时接口返回当日实时数据
      - TDX 通过 TCP 协议获取数据（盘中实时）
    """
    ZHB = "zhb"
    TDX = "tdx"
    TENCENT = "tencent"
    EASTMONEY = "em"
    SINA = "sina"
    FALLBACK = "fb"           # 多级 fallback 中间件


class Unit(Enum):
    """字段单位（用于显示和计算一致性检查）。"""
    YUAN = "yuan"             # 元
    WAN_YUAN = "wan_yuan"     # 万元
    YI_YUAN = "yi_yuan"       # 亿元
    SHARE = "share"           # 股
    WAN_SHARE = "wan_share"   # 万股
    PERCENT = "percent"       # 百分点（如 2.5 表示 +2.5%）
    TIMESTAMP = "timestamp"   # 时间戳（秒）
    COUNT = "count"           # 计数（无单位）
    TEXT = "text"             # V15.3: 字符串/名称（无单位，如行业名/股票名/概念名）


# ═══════════════════════════════════════════════════════════════
# 字段元数据（FieldSpec）
# ═══════════════════════════════════════════════════════════════

@dataclass(slots=True, frozen=True)
class FieldSpec:
    """字段元数据。

    描述一个数据字段的所有静态属性，用于：
      - V13.1 数据源路由（决定走 ZHB / HTTP / TDX）
      - V13.2 归一化函数（统一字段名、单位、时间锚点）
      - 文档自动化（从元数据生成 markdown 表格）
    """
    name: str               # 字段英文名（与 ZHB / HTTP 接口对齐）
    description: str         # 字段中文说明
    source_preference: Tuple[DataSource, ...]  # 数据源优先级（按顺序尝试）
    time_anchor: TimeAnchor  # 字段的时间锚点（T_MINUS_1 表示 T-1 数据）
    unit: Unit               # 字段单位
    is_real_time: bool       # 是否需要实时数据（True=HTTP 必走，False=ZHB 够用）
    zhb_t_minus_1_acceptable: bool  # T-1 数据是否影响判断（True=可用 ZHB，False=必须 HTTP）
    batch_friendly: bool = False  # 是否支持批量获取（True=可走 get_em_batch_quotes 等批量接口）


# ═══════════════════════════════════════════════════════════════
# 字段元数据表（V13.0 10.2）
# ═══════════════════════════════════════════════════════════════
#
# 设计原则：
#   - is_real_time=True: 行情/资金流类，必须 HTTP
#   - zhb_t_minus_1_acceptable=True: 估值/财务类，ZHB 即可
#   - batch_friendly=True: 字段在 push2 接口的批量返回中存在
#
# 数据源参考 docs/field_dict.md

FIELD_SPECS: Tuple[FieldSpec, ...] = (
    # ─── 行情类（必须 HTTP 实时，V12.6 REQUIRES_REALTIME_HTTP）───
    FieldSpec(
        name="price", description="当前价格（昨收参考）",
        source_preference=(DataSource.ZHB, DataSource.TDX, DataSource.TENCENT, DataSource.EASTMONEY),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.YUAN,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="change_pct", description="涨跌幅（百分点）",
        source_preference=(DataSource.ZHB, DataSource.TDX, DataSource.EASTMONEY),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.PERCENT,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="amount", description="成交额（万元）",
        source_preference=(DataSource.ZHB, DataSource.TENCENT, DataSource.TDX),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.WAN_YUAN,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="volume", description="成交量（手）",
        source_preference=(DataSource.ZHB, DataSource.TENCENT, DataSource.TDX),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.COUNT,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="open", description="开盘价（元）",
        source_preference=(DataSource.ZHB, DataSource.TDX, DataSource.EASTMONEY),
        time_anchor=TimeAnchor.T_OPEN, unit=Unit.YUAN,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="high", description="最高价（元）",
        source_preference=(DataSource.ZHB, DataSource.TDX, DataSource.EASTMONEY),
        time_anchor=TimeAnchor.T_DAY, unit=Unit.YUAN,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="low", description="最低价（元）",
        source_preference=(DataSource.ZHB, DataSource.TDX, DataSource.EASTMONEY),
        time_anchor=TimeAnchor.T_DAY, unit=Unit.YUAN,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="prev_close", description="昨收价（元）",
        source_preference=(DataSource.ZHB, DataSource.TDX),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.YUAN,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),

    # ─── 资金流类（必须 HTTP 实时）───
    FieldSpec(
        name="main_net_buy_hands", description="主力净买入（手）",
        source_preference=(DataSource.ZHB, DataSource.TDX, DataSource.EASTMONEY),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.COUNT,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="main_net_buy_hands_1d", description="T-1 主力净买入（手）",
        source_preference=(DataSource.ZHB, DataSource.TDX),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.COUNT,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="main_net_buy_amount", description="主力净买入额（万元）",
        source_preference=(DataSource.ZHB, DataSource.TDX, DataSource.EASTMONEY),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.WAN_YUAN,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="main_net_buy_amount_1d", description="T-1 主力净买入额（万元）",
        source_preference=(DataSource.ZHB, DataSource.TDX),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.WAN_YUAN,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),

    # ─── 估值类（ZHB 即可，V12.6 ZHB_SUFFICIENT）───
    FieldSpec(
        name="pe_ttm", description="PE-TTM（倍）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.COUNT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="pe_dynamic", description="动态 PE（倍）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.COUNT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="pb", description="市净率（倍）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.COUNT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="dividend_yield", description="股息率（百分点）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.PERCENT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="turnover_pct", description="换手率（百分点）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.PERCENT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),

    # ─── 财务类（ZHB 即可）───
    FieldSpec(
        name="net_profit", description="净利润（元）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.YUAN,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="revenue", description="营业收入（元）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.YUAN,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="roe", description="ROE（百分点）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.PERCENT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="eps", description="每股收益（元）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.YUAN,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),

    # ─── 股本类（ZHB 即可）───
    FieldSpec(
        name="total_shares", description="总股本（万股）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.WAN_SHARE,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="float_shares", description="流通股本（万股）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.WAN_SHARE,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="mcap", description="总市值（亿元）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.YI_YUAN,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),

    # ─── 历史涨跌幅（ZHB 即可）───
    FieldSpec(
        name="change_5d", description="近 5 日累计涨跌幅（百分点）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.PERCENT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="change_10d", description="近 10 日累计涨跌幅（百分点）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.PERCENT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="change_20d", description="近 20 日累计涨跌幅（百分点）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.PERCENT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="change_30d", description="近 30 日累计涨跌幅（百分点，V15.1 启用）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.PERCENT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="change_60d", description="近 60 日累计涨跌幅（百分点）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.PERCENT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="change_ytd", description="年初至今涨跌幅（百分点）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_YEAR_START, unit=Unit.PERCENT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="streak_days", description="连涨/连跌天数",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.COUNT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),

    # ─── 52 周/IPO/员工（ZHB 即可）───
    FieldSpec(
        name="high_52w", description="52 周最高价（元）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.YUAN,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="low_52w", description="52 周最低价（元）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.YUAN,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="ipo_price", description="IPO 发行价（元）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.YUAN,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="employee_count", description="员工总数",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.COUNT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),

    # ─── 板块/题材（ZHB 即可）───
    FieldSpec(
        name="industry", description="行业归属",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.TEXT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="industry_code", description="行业代码",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.TEXT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="board", description="板块归属",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.TEXT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),
    FieldSpec(
        name="concept", description="概念/题材（来自 ZHB tdxchain.cfg）",
        source_preference=(DataSource.ZHB,),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.TEXT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
)


# 构建按字段名索引的 dict（O(1) 查找）
_FIELD_SPEC_BY_NAME = {spec.name: spec for spec in FIELD_SPECS}


def get_field_spec(field_name: str) -> FieldSpec:
    """根据字段名获取 FieldSpec。

    Args:
        field_name: 字段英文名

    Returns:
        对应的 FieldSpec

    Raises:
        KeyError: 字段名未在 FIELD_SPECS 中定义
    """
    return _FIELD_SPEC_BY_NAME[field_name]


def has_field_spec(field_name: str) -> bool:
    """检查字段是否已定义 FieldSpec。"""
    return field_name in _FIELD_SPEC_BY_NAME


def list_field_names() -> Tuple[str, ...]:
    """列出所有已定义字段名。"""
    return tuple(_FIELD_SPEC_BY_NAME.keys())


def list_realtime_http_fields() -> Tuple[str, ...]:
    """列出所有 is_real_time=True 的字段（V12.6 REQUIRES_REALTIME_HTTP 等价）。"""
    return tuple(s.name for s in FIELD_SPECS if s.is_real_time)


def list_zhb_sufficient_fields() -> Tuple[str, ...]:
    """列出所有 is_real_time=False 的字段（V12.6 ZHB_SUFFICIENT 等价）。

    V14.2.1 修订：原定义 `zhb_t_minus_1_acceptable=True` 含义是"ZHB 数据可接受"，
    但与 `is_real_time=True` 存在交集（如 price 既能走 HTTP 也能用 ZHB 兜底）。
    data_provider 期望的 ZHB_SUFFICIENT 是**严格**意义——"不强制走 HTTP"，
    对应 `is_real_time=False`。
    """
    return tuple(s.name for s in FIELD_SPECS if not s.is_real_time)


# ═══════════════════════════════════════════════════════════════
# V13.0 10.3: 归一化函数骨架（仅接口，不接入 data_provider）
# ═══════════════════════════════════════════════════════════════

@dataclass(slots=True, frozen=True)
class NormalizedQuote:
    """归一化后的行情快照（V13.0 草案）。

    边界归一化原则（Normalize at Boundary）：
      - 数据源适配器在拿到原始数据的第一时间完成归一化
      - 下游策略层访问语法：quote.change_pct（不是 quote.change_pct.value）
      - 任何字段单位都统一到标准（yuan / wan_yuan / percent）

    V13.0 阶段：仅定义 dataclass，不接入 data_provider
    V13.1 阶段：实现 normalize_at_boundary() 函数
    V13.2 阶段：data_provider 的 get_* 接口迁移到返回 NormalizedQuote
    """
    code: str                # 6 位股票代码
    data_date: str           # YYYYMMDD 格式（ZHB 包名 / TDX 数据日期）
    price: float             # 元
    change_pct: float        # 百分点
    source: DataSource       # 数据源
    time_anchor: TimeAnchor  # 时间锚点


@dataclass(slots=True, frozen=True)
class CanonicalStockData:
    """统一规范数据合约对象 (Canonical Stock Data Contract)

    全系统 6 大报告脚本与策略引擎调用的标准强类型数据结构。
    规范全系统所有字段的命名、单位、类型与元数据溯源。
    """
    code: str
    name: str = ""
    price: float = 0.0               # 当前/收盘价格 (元)
    change_pct: float = 0.0          # 涨跌幅 (%)
    open: float = 0.0                # 开盘价 (元)
    high: float = 0.0                # 最高价 (元)
    low: float = 0.0                 # 最低价 (元)
    prev_close: float = 0.0          # 昨收价 (元)
    amount_wan: float = 0.0          # 成交额 (万元)
    volume_hand: float = 0.0         # 成交量 (手)

    # 估值类
    pe_ttm: float = 0.0              # PE(TTM) (倍)
    pe_dynamic: float = 0.0          # 动态PE (倍)
    pb: float = 0.0                  # PB (倍)
    dividend_yield: float = 0.0      # 股息率 (%)
    turnover_pct: float = 0.0        # 换手率 (%)

    # 资金流类
    main_net_buy_wan: float = 0.0    # 主力净买额 (万元)
    main_net_buy_hands: float = 0.0  # 主力净买量 (手)
    main_net_buy_wan_1d: float = 0.0 # T-1 主力净买额 (万元)

    # 财务与股本类
    roe: float = 0.0                 # ROE (%)
    gross_margin: float = 0.0        # 毛利率 (%)
    net_profit_margin: float = 0.0   # 净利率 (%)
    net_profit: float = 0.0          # 净利润 (元)
    revenue: float = 0.0             # 营业收入 (元)
    eps: float = 0.0                 # 每股收益 (元)
    total_shares_wan: float = 0.0    # 总股本 (万股)
    float_shares_wan: float = 0.0    # 流通股本 (万股)
    mcap_yi: float = 0.0             # 总市值 (亿元)
    float_mcap_yi: float = 0.0       # 流通市值 (亿元)
    holder_count: int = 0            # 股东户数 (户)

    # 衍生与历史指标
    change_5d: float = 0.0           # 5日涨跌幅 (%)
    change_10d: float = 0.0          # 10日涨跌幅 (%)
    change_20d: float = 0.0          # 20日涨跌幅 (%)
    change_30d: float = 0.0          # 30日涨跌幅 (%) — V15.1 启用
    change_60d: float = 0.0          # 60日涨跌幅 (%)
    change_ytd: float = 0.0          # 年初至今涨跌幅 (%)
    streak_days: int = 0             # 连涨(正)/连跌(负)天数
    high_52w: float = 0.0            # 52周最高 (元)
    low_52w: float = 0.0             # 52周最低 (元)
    ipo_price: float = 0.0           # IPO发行价 (元)
    employee_count: int = 0          # 员工总数 (人)
    list_date: str = ""              # V16.0: 上市日期 (YYYY-MM-DD，来源 push2 f189 / TDX 0x0010 ipo_date)

    # V16.1: push2 扩展字段（2026-08-04 官方 TdxQuant 交叉验证）
    limit_up: float = 0.0            # 涨停价 (元) — push2 f51 / 官方 ZTPrice
    limit_down: float = 0.0          # 跌停价 (元) — push2 f52 / 官方 DTPrice
    bps: float = 0.0                 # 每股净资产 (元) — push2 f92 / 东财F10 BPS
    pe_more: float = 0.0             # PE(MorePE 口径) — push2 f164 / 官方 MorePE
    industry_code_push2: str = ""    # 行业板块代码 (如 BK1277) — push2 f198
    trading_periods: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # 交易时段数组 — push2 f80
    report_period: str = ""          # 最新报告期 (YYYYMMDD) — push2 f221 / ulist f221
    quote_date: str = ""             # 行情快照日期 (YYYY-MM-DD) — push2 data_date

    # V16.1: 资金流细分（push2 f135-f146，单位元）
    fund_main_today: float = 0.0     # 主力净流入(今日)
    fund_super_today: float = 0.0    # 超大单净流入(今日)
    fund_large_today: float = 0.0    # 大单净流入(今日)
    fund_mid_today: float = 0.0      # 中单净流入(今日)
    fund_main_5d: float = 0.0        # 主力净流入(5日)
    fund_super_5d: float = 0.0       # 超大单净流入(5日)
    fund_large_5d: float = 0.0       # 大单净流入(5日)
    fund_main_10d: float = 0.0       # 主力净流入(10日)
    fund_super_10d: float = 0.0      # 超大单净流入(10日)
    fund_large_10d: float = 0.0      # 大单净流入(10日)
    fund_5d_array: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # 近5日主力净流入数组 — push2 f178

    # 板块与概念
    industry: str = ""               # 行业分类
    industry_code: str = ""          # 行业代码
    board: str = ""                  # 板块归属
    concepts: Tuple[str, ...] = field(default_factory=tuple) # 所属概念

    # 元数据溯源
    data_source: str = "zhb"         # 数据来源 (zhb / tdx / http)
    time_anchor: str = "t-1"         # 时效锚点 (t_day / t-1)
    is_valid: bool = True            # 数据合法校验标记

    # V15.4: per-field source label (方案 C)
    # 字典 key = 字段名 (e.g. "price", "mcap_yi", "industry")
    # 字典 value = 数据来源标签 (e.g. "realtime:push2", "realtime:tencent", "calculated", "missing")
    # 上层用 cdata.field_sources.get("price") 可知道这个 price 是 push2 实时还是 TDX 还是 ZHB 兜底
    # 状态码定义:
    #   realtime:push2      - 推算实时价 (hq.sinajs.cn) 100% 准确
    #   realtime:tencent    - 腾讯行情实时
    #   realtime:tdx        - TDX 实时
    #   closing:tdx         - TDX 收盘价
    #   closing:push2       - 推算收盘价
    #   zhb:t-1             - ZHB T-1 静态
    #   zhb:t-0             - ZHB T 日盘后
    #   calculated          - 公式推算 (e.g. mcap = total_shares × price)
    #   missing             - 完全没拿到
    field_sources: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为通用字典（兼容旧脚本解析）。"""
        from dataclasses import asdict
        d = asdict(self)
        d['concepts'] = list(self.concepts)
        return d


def normalize_at_boundary(raw: dict, source: DataSource) -> dict:
    """边界归一化函数（V13.0 10.3 骨架，V16.0 实现）。

    将各数据源原始 dict 的字段名/单位统一到 CanonicalStockData 规范字段名，
    返回规范 dict（供 data_provider / 策略层使用）。

    支持字段别名映射（不同源同名异义）与单位换算：
      - last_close / pre_close → prev_close
      - amount (单位因源而异) → amount_wan（统一万元）
      - mcap / total_mv → mcap_yi（亿元）
      - total_share / zongguben → total_shares_wan（万股）
      - main_net_buy / main_net_wan → main_net_buy_wan
      - change_pct / chg → change_pct（百分点）
      - 保留原字段名相同的直接透传

    Args:
        raw: 数据源原始 dict
        source: 数据源标识（决定单位换算基准）

    Returns:
        归一化后的规范字段 dict
    """
    if not raw:
        raise ValueError("normalize_at_boundary: raw dict is empty")

    def _f(*keys: str) -> float:
        for k in keys:
            v = raw.get(k)
            if v is not None and v not in ("", "-", "0.0", "None"):
                try:
                    return float(v)
                except (ValueError, TypeError):
                    pass
        return 0.0

    out: dict = {}
    _EM = source in (DataSource.EASTMONEY, DataSource.SINA)

    # 价格类（元）
    for target, *keys in [
        ("price", "price", "f43"),
        ("open", "open", "f46"),
        ("high", "high", "f44"),
        ("low", "low", "f45"),
        ("prev_close", "prev_close", "last_close", "f60"),
    ]:
        v = _f(*keys)
        if v != 0.0:
            out[target] = round(v, 4)

    # 涨跌幅 / 换手率（百分点）
    for target, *keys in [
        ("change_pct", "change_pct", "f170"),
        ("turnover_pct", "turnover_pct", "f168"),
    ]:
        v = _f(*keys)
        if v != 0.0:
            out[target] = round(v, 4)

    # 成交额（统一万元）：EM/TDX/SINA 原始是元 → /1e4；ZHB/TENCENT 已是万元
    amt_wan = _f("amount_wan", "f48")
    if amt_wan == 0.0:
        amt_wan = _f("amount")
    if amt_wan != 0.0:
        # V16.0: 无论从 amount_wan/f48/amount 取到，EM/SINA 源都需元→万元
        if _EM:
            amt_wan = amt_wan / 1e4
        out["amount_wan"] = round(amt_wan, 4)

    # 成交量（统一手）：TDX/腾讯 volume 可能是股 → /100
    vol = _f("volume_hand", "f47")
    if vol == 0.0:
        vol = _f("volume", "vol")
        if vol != 0.0 and not _EM:
            vol = vol / 100.0
    if vol != 0.0:
        out["volume_hand"] = round(vol, 2)

    # 估值（倍 / %）
    for target, *keys in [
        ("pe_ttm", "pe_ttm", "f162"),
        ("pe_dynamic", "pe_dynamic", "f163"),
        ("pb", "pb", "f167"),
        ("dividend_yield", "dividend_yield"),
    ]:
        v = _f(*keys)
        if v != 0.0:
            out[target] = round(v, 4)

    # 资金流（统一万元）
    v = _f("main_net_buy_wan", "main_net_buy_amount", "main_net_wan")
    if v != 0.0:
        out["main_net_buy_wan"] = round(v, 4)
    v = _f("main_net_buy_hands")
    if v != 0.0:
        out["main_net_buy_hands"] = round(v, 2)

    # 股本（统一万股）：EM/SINA 原始是股 → /1e4；TDX 0x0010 zongguben 也是股
    # V16.3 A2: TDX 分支原样透传（把股当万股）为隐患——raw 约定是"数据源原始 dict"
    #（TDX finance 输出 zongguben=股，V16.2.3 确认），故统一 /1e4 转万股。
    total = _f("total_shares_wan", "f84", "total_shares", "zongguben")
    if total != 0.0:
        out["total_shares_wan"] = round(total / 1e4, 2)
    flt = _f("float_shares_wan", "f85", "float_shares", "liutongguben")
    if flt != 0.0:
        out["float_shares_wan"] = round(flt / 1e4, 2)

    # 市值（统一亿元）：EM/SINA 原始是元 → /1e8
    mc = _f("mcap_yi", "f116", "mcap", "total_mv")
    if mc != 0.0:
        out["mcap_yi"] = round(mc / 1e8, 4) if _EM else round(mc, 4)
    fmc = _f("float_mcap_yi", "f117", "float_mcap")
    if fmc != 0.0:
        out["float_mcap_yi"] = round(fmc / 1e8, 4) if _EM else round(fmc, 4)

    # 财务 / 历史涨跌幅（透传）
    for target, *keys in [
        ("net_profit", "net_profit", "jinglirun"),
        ("revenue", "revenue", "zhuyingshouru"),
        ("roe", "roe"),
        ("eps", "eps"),
        ("change_5d", "change_5d"),
        ("change_10d", "change_10d"),
        ("change_20d", "change_20d"),
        ("change_30d", "change_30d"),
        ("change_60d", "change_60d"),
        ("change_ytd", "change_ytd"),
        ("high_52w", "high_52w"),
        ("low_52w", "low_52w"),
        ("ipo_price", "ipo_price"),
        ("streak_days", "streak_days"),
        ("holder_count", "holder_count", "gudongrenshu"),
    ]:
        v = _f(*keys)
        if v != 0.0:
            out[target] = round(v, 4) if isinstance(v, float) else v

    # 文本类
    for target, *keys in [
        ("code", "code", "symbol", "f57"),
        ("name", "name", "f58"),
        ("industry", "industry", "f127"),
        ("board", "board", "f128"),
        ("list_date", "list_date", "f189"),
    ]:
        v = raw.get(keys[0])
        if v is None:
            for k in keys[1:]:
                v = raw.get(k)
                if v:
                    break
        if v and str(v) not in ("None", "nan"):
            out[target] = str(v)

    return out

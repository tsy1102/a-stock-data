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
        name="price", description="现价（昨收参考）",
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
        name="prev_close", description="昨收盘（元）",
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
        name="main_net_buy_amount", description="主力净买入额（万元）⚠️ V17.0 实锤: ZHB 该键实为开盘金额(竞价额)——主力净流入请用东财 f137",
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
        # V17.0.15 实证校正（原 V12.6 规格已与代码+字典漂移，三处证据）：
        #   ① 换手率是**当日即时指标**——get_turnover_pct docstring(V16.3 M) 明确
        #      "9:30-24:00 不接受 ZHB T-1，仅盘前/非交易日用 ZHB"；
        #   ② canonical 主源实为**腾讯 T 日实时**：get_canonical_stock_data(:785-801)
        #      rt_quote → zhb → `get_tencent_quote` 兜底，并写 field_sources
        #      = "realtime:tencent"（V16.2.3，起因是 TDX 0x010C 无换手率、ZHB 无此字段
        #      → sht 换手率恒 0）；
        #   ③ 同花顺 getharden `huanshou` 亦为**当日**换手率（2026-08-28 探针实测
        #      81 行：000712 huanshou=1.69 / zhangfu=9.972，见字典 §12.8.12）。
        #   故主源 = 腾讯(东财 f168 同义) T 日；ZHB T-1 仅盘前/非交易日可接受。
        name="turnover_pct", description="换手率（百分点，当日即时指标）",
        source_preference=(DataSource.TENCENT, DataSource.ZHB),
        time_anchor=TimeAnchor.T_DAY, unit=Unit.PERCENT,
        is_real_time=True, zhb_t_minus_1_acceptable=True, batch_friendly=True,
    ),

    # ─── 财务类（ZHB 即可；V16.3 O: TDX 0x0010/F10 为实际主源——ZHB 无这些字段，见 field_dict §零）───
    FieldSpec(
        name="net_profit", description="净利润（元）",
        source_preference=(DataSource.TDX, DataSource.ZHB),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.YUAN,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="revenue", description="营业收入（元）",
        source_preference=(DataSource.TDX, DataSource.ZHB),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.YUAN,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="roe", description="ROE（百分点）",
        source_preference=(DataSource.TDX, DataSource.ZHB),
        time_anchor=TimeAnchor.T_MINUS_1, unit=Unit.PERCENT,
        is_real_time=False, zhb_t_minus_1_acceptable=True, batch_friendly=False,
    ),
    FieldSpec(
        name="eps", description="每股收益（元）",
        source_preference=(DataSource.TDX, DataSource.ZHB),
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
    # V17.2.x(2026-09-10) 审计决策 Q2: FieldSpec(change_30d) 已随契约字段一并删除——
    #   实读 Col[18]=20 日值, 与 change_20d 完全同值, 属带误导名的错误副本。需要 30 日请由 K 线自算。
    FieldSpec(
        name="change_60d",
        description="近60根K线涨跌幅（截至T-1口径，百分点；V16.3 O28 修正：原误读 Col[19] 含当日，现读 Col[20]）",
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
    # V17.2.x(2026-09-10) 审计: 本字段由 parse_stock_name() 正常产出并已进契约, 但 5 大脚本零消费
    #   (脚本直接用 name 做字符串处理 → 受 N/C/XD/XR/ST 临时前缀污染)。建议脚本统一改用 name_core 比对名称。
    name_core: str = ""          # V16.3.3: 核心名称（去 N/C/XD/XR/DR/S 临时前缀 + ST 标记）——名称主体永久不变
    is_st: bool = False          # V16.3.3: 是否 ST/*ST（退市风险信号——不可忽略）
    is_new: bool = False         # V16.3.3: 是否次新股（N/C 前缀，上市 ≤5 日）
    price: float = 0.0               # 当前/收盘价格 (元)
    change_pct: float = 0.0          # 涨跌幅 (%)
    open: float = 0.0                # 开盘价 (元)
    high: float = 0.0                # 最高价 (元)
    low: float = 0.0                 # 最低价 (元)
    prev_close: float = 0.0          # 昨收盘 (元)
    amount_wan: float = 0.0          # 成交额 (万元)
    volume_hand: float = 0.0         # 成交量 (手)

    # 估值类
    pe_ttm: float = 0.0              # PE（TTM） (倍)
    pe_dynamic: float = 0.0          # 动态PE (倍)
    pe_lyr: float = 0.0              # 静态PE(LYR, f163, 现价÷年报EPS) — V17.0.17(2026-09-01) 据主字典定案新增透传
    pb: float = 0.0                  # PB (倍)
    ps_ttm: float = 0.0              # V17.0.5: 市销率 TTM (fuyao 独有)
    pcf_ttm: float = 0.0             # V17.0.5: 市现率 TTM (fuyao 独有)
    # V17.2.x(2026-09-10) 调整 A: 均价源 [85]→[51]（字典 09-08 round12 定案: [85]对均价锚仅3/20已撤销, [51]强锚+TDX快照 average_price）
    avg_price: float = 0.0          # 均价 / VWAP（元，腾讯 qt.gtimg [51] + TDX快照 average_price）
    dividend_yield: float = 0.0      # 股息率 (%)
    turnover_pct: float = 0.0        # 换手率 (%)
    vol_ratio: float = 0.0           # 量比 (腾讯 idx49 / TDX快照; 字典 push2 f50≡量比 同源同义, 本层 push2 路径未请求 f50 — V16.4.0/2026-09-10 审计)
    # V17.2.0(2026-09-07): TDX 实时五档行情协议直解（非派生）——内盘/外盘/涨速
    s_vol: float = 0.0               # 内盘(主动卖成交量, 手) — easy_tdx SecurityQuote.s_vol (TDX 协议直解)
    b_vol: float = 0.0               # 外盘(主动买成交量, 手) — easy_tdx SecurityQuote.b_vol
    rise_speed: float = 0.0          # 涨速(%/min) — easy_tdx SecurityQuote.rise_speed (协议 reversed_bytes9/100)
    # V17.1: 资产负债表项(TDX GetFinanceInfo 0x0010, 单位角→元)——季频静态, 不扩大实时取数集
    total_assets: float = 0.0        # 总资产 (元, TDX f10 zongzichan/10)
    net_assets: float = 0.0          # 净资产/股东权益 (元, TDX f10 jingzichan/10)

    # 资金流类
    # V17.2.x(2026-09-10) 审计决策 Q1 —— 资金流主口径消歧:
    #   main_net_buy_wan 与 fund_main_today 是**同一指标的不同单位**:
    #   实证 data_provider.py:957→962 → main_net_buy_wan = fund_main_today / 1e4 (元→万元),
    #   仅当 fund_main_today 缺失时才回落东财 rt_fund['main_net_wan'](独立兜底源)。
    #   → 口径权威 = fund_main_today(元, push2 f137); main_net_buy_wan 为展示层便利字段,
    #     **禁止**为其单独取数(否则即双写, 两值可能分叉)。
    main_net_buy_wan: float = 0.0    # 主力净买额(万元) ≡ fund_main_today/1e4(主) 或 rt_fund(兜底); 非独立指标
    main_net_buy_hands: float = 0.0  # 主力净买量(手) —— 独立源: 东财 rt_fund['main_net_hands'](仅实时路径)
    main_net_buy_wan_1d: float = 0.0 # T-1 主力净买额(万元) —— ⚠️ 当前恒 0: ZHB 该键实为昨日竞价额(已实锤不可用), 无 T-1 源接入, 保留占位

    # 财务与股本类
    roe: float = 0.0                 # ROE (%)
    roa: float = 0.0                 # V17.0.5 正名: ROA(TTM 滚动 %) — 腾讯 tx66（招行 1.12 精确；~~年化~~银行 TTM≈年报故曾误标）
    roe_deduct_ttm: float = 0.0      # V17.0.5: 扣非加权ROE(TTM 滚动 %) — 腾讯 tx65（fuyao index_deduct_weighted_avg_roe 同族）
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
    # V17.0.25(2026-09-03): Beta（腾讯 [56]，据主字典 09-03 主动升级定案 = Beta 族高置信）
    beta: float = 0.0                # Beta（腾讯口径 Beta 估计值, 与自算 Pearson=0.908; 非本系统重算）
    # V17.2.x(2026-09-10) 调整 B: 委差源 [86]→[50]+push2 f192（字典 09-08 定案: [86]非委差已撤销, [50]+f192 为 canonical）
    bid_ask_net: float = 0.0         # 委差（手级带符号量, 腾讯[50] + push2 f192 兜底）
    # V17.2.x(2026-09-10) 调整 C: 委比%（腾讯[74] + push2 f191 + TDX快照 entrust_ratio；字典 §12.8.12e canonical）
    entrust_ratio: float = 0.0       # 委比(%)（腾讯[74]；push2 f191 / TDX快照 同义）
    change_5d: float = 0.0           # 5日涨跌幅 (%)
    change_10d: float = 0.0          # 10日涨跌幅 (%)
    change_20d: float = 0.0          # 20日涨跌幅 (%)
    # ⚠️ change_30d 已于 V17.2.x(2026-09-10) 审计**删除**(审计决策 Q2):
    #   zhb_client.py:851 实读 Col[18]=20 日值 → 与 change_20d 完全同值, 属带误导名的错误副本;
    #   tdxstat.cfg 无 30 日列, 真实 30 日需 TdxQuant ZAFPre30(当前无该依赖)。
    #   如需 30 日涨跌幅, 请由 K 线自算, **勿恢复此字段**。
    change_60d: float = 0.0          # 60日涨跌幅 (%)
    change_ytd: float = 0.0          # 年初至今涨跌幅 (%)
    # V17.0.5: 本月至今涨跌幅(tdxstat2 Col[11] 正名, 基准=上月末最后交易日收盘)
    change_mtd: float = 0.0
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
    industry_code_push2: str = ""    # 行业板块代码 (如 BK1277) — push2 f198
    trading_periods: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # 交易时段数组 — push2 f80
    report_period: str = ""          # 最新报告期 (YYYYMMDD) — push2 f221 / ulist f221
    quote_date: str = ""             # 行情快照日期 (YYYY-MM-DD) — push2 data_date（⚠️ 有单测断言 tests/core/test_core_schema.py:275, 勿删）
    bid1_vol: float = 0.0            # 买一量 (手) ← 腾讯协议 v10（2026-08-11: 新增——sht 封单额/信号/预警依赖）
    # V17.2.x(2026-09-10) 调整 C: 买二/卖二价（腾讯[12]/[22] + tdx bid2/ask2 + sina[14]/[24]；字典 §12.8.12e canonical）
    bid2: float = 0.0                # 买二价 (元)
    ask2: float = 0.0                # 卖二价 (元)

    # V16.1: 资金流细分(push2, 单位元)
    # V17.0.16(2026-08-31) 重定案 —— 旧版把四组当并列四档并算「主力 = f137 + f140」，**错的**。
    # 实证（详见 docs/field_dict.md §12.3.3）：f137 = f140 + f143 精确成立（169/169，相对差 0.00），
    # 且跨接口对撞 f62==f137 / f66==f140 / f72==f143 命中 96%+
    #   → f137 本身就是主力净（超大单 + 大单），**不可再相加**；旧算法虚高约 40%。
    fund_main_today: float = 0.0     # 主力净流入(今日, f137 = 超大单净 + 大单净)
    fund_super_today: float = 0.0    # 超大单净流入(今日, f140)
    fund_large_today: float = 0.0    # 大单净流入(今日, f143)
    fund_mid_today: float = 0.0      # 中单净流入(今日, f146)
    fund_small_today: float = 0.0    # 小单净流入(今日, f149) — V17.0.16 订正(原记 f146 实为中单净)
    # V17.2.1: 五档资金流「买入额/卖出额」(毛额) —— 净额见上方，毛额用于判断多空力道
    #   东财实证(茅台 2026-09-07 盘中): 主力买 = 超大单买 + 大单买 (231726069+752484240=984210309)
    fund_main_buy: float = 0.0       # 主力买入额(今日, f135 = 超大单买 f138 + 大单买 f141)
    fund_main_sell: float = 0.0      # 主力卖出额(今日, f136 = 超大单卖 f139 + 大单卖 f142)
    fund_super_buy: float = 0.0      # 超大单买入额(今日, f138)
    fund_super_sell: float = 0.0     # 超大单卖出额(今日, f139)
    fund_large_buy: float = 0.0      # 大单买入额(今日, f141)
    fund_large_sell: float = 0.0     # 大单卖出额(今日, f142)
    fund_mid_buy: float = 0.0        # 中单买入额(今日, f144)
    fund_mid_sell: float = 0.0       # 中单卖出额(今日, f145)
    fund_main_5d: float = 0.0        # 主力净流入(近5日, f178 数组聚合；兜底 ulist f164)
    fund_main_5d_pct: float = 0.0    # 近5日主力净占比%(ulist f165) — V17.2.1 新增
    fund_5d_array: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # 近5日主力净流入数组 — push2 f178

    # V17.0.7 财务 TTM 族(push2 f103-f190, 口径经 fuyao 官方三大报表 5/5 终判;
    # 详见 docs/field_verification/20260825_cross_analysis.md)
    ocf_ttm: float = 0.0             # 经营活动现金流量净额 TTM (元) — push2 f103
    revenue_ttm: float = 0.0         # 营业总收入 TTM (元) — push2 f104
    net_profit_period: float = 0.0   # 归母净利润 最新报告期 (元) — push2 f105
    net_profit_annual: float = 0.0   # 归母净利润 最新年报 (元) — push2 f109
    eps_annual: float = 0.0          # 年报EPS =f109/f84 (元/股) — push2 f160
    eps_deduct_ttm: float = 0.0      # 扣非每股收益 TTM (元/股) — push2 f108
    undist_profit_ps: float = 0.0    # 每股未分配利润 (元/股, ≡ulist f48) — push2 f190

    # 板块与概念
    industry: str = ""               # 行业分类
    # V17.2.x(2026-09-10) 审计决策 Q10: industry_code 与 industry_code_push2 **非冗余**——
    #   二者属不同分类体系: 本字段=TDX 行业码; industry_code_push2=东财板块代码(push2 f198, 如 BK1277)。
    industry_code: str = ""          # 行业代码 (TDX 行业分类体系)
    board: str = ""                  # 板块归属（地域, f128）
    # V17.0.32(2026-09-06): 市场类型枚举(≡ ulist f182, 主字典 2026-08-19 定案 20/20 实锤)
    #   主板=2 / 创业板=5 / 科创板=32 / 北交所=80; ST 不改变归属。
    #   与 board(地域) 正交——前者是交易所/市场类型, 后者是注册地。
    sec_type: int = 0                # 市场类型枚举（f182）
    concepts: Tuple[str, ...] = field(default_factory=tuple) # 所属概念

    # 元数据溯源
    # V17.2.x(2026-09-10) 审计决策 Q6: is_valid 由"恒 True 空壳"升级为**真实质量门禁**
    #   (此前 data_provider 硬编码 is_valid=True 且全仓零引用 = 数据质量不可观测)。
    #   规则: code 非空 且 价格类字段至少一项有效(price>0 或 prev_close>0)。
    data_source: str = "zhb"         # 数据来源 (zhb / tdx / http)
    time_anchor: str = "t-1"         # 时效锚点 (t_day / t-1)
    is_valid: bool = True            # 数据合法校验结果(真实 QC, 非恒 True)

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

    # V17.2.22: eltdx 7709/7615 实时短线/连板指标(经统一层 get_canonical_stock_data 暴露)
    # 数据来源: get_eltdx_shortline_bundle 批量预热 -> 模块级缓存 -> 统一层 per-stock 读缓存(非取数)
    # 默认值=未命中(TDX 源 eltdx 不可用 / 未批量预热) —— 不污染核心 86 字段契约(FIELD_SPECS 不含此组)
    eltdx_ladder_level: int = 0            # 连板高度(档位, eltdx limit_ladder.ladder_level)
    eltdx_limit_up_streak_days: int = 0    # 连续涨停天数(ShortlineIndicator.limit_up_streak_days)
    eltdx_limit_board_text: str = ""       # 连板梯队文本(limit_board_text, e.g. "3天3板")
    eltdx_seal_to_float_ratio: float = 0.0 # 封单额/流通市值(%)——封板坚决度(seal_to_float_ratio)
    eltdx_open_volume_ratio: float = 0.0   # 开盘成交量比(open_volume_ratio)
    eltdx_seal_amount: float = 0.0         # 封单额(元, seal_amount)
    eltdx_opening_rush: float = 0.0        # 开盘抢筹(opening_rush)
    eltdx_auction_prev_volume_ratio: float = 0.0  # 竞价量比(auction_prev_volume_ratio)
    eltdx_open_prev_amount_ratio: float = 0.0     # 开盘额/昨额比(open_prev_amount_ratio)
    eltdx_open_change_pct: float = 0.0     # 开盘涨跌幅%(open_change_pct)
    eltdx_open_turnover_z: float = 0.0     # 开盘换手Z(open_turnover_z)
    eltdx_has_shortline: bool = False      # 是否命中 eltdx 短线指标(批量缓存命中标记)

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
    # 🔴 2026-09-01 统一层纠错（据 field_dict §12.8.12e/【PE 口径铁证】定案）：
    #   f162=动态PE(pe_mrq) / f163=静态PE(LYR,pe_lyr) / f164=TTM(pe_ttm)。
    #   原 `pe_ttm←f162`/`pe_dynamic←f163` 与主字典**完全相反**，会将静态PE灌入 pe_ttm、
    #   动态PE灌入 pe_dynamic 的兜底键，导致下游"PE（TTM）"实际显示静态值。现已按定案纠正。
    for target, *keys in [
        ("pe_ttm", "pe_ttm", "f164"),
        ("pe_dynamic", "pe_dynamic", "f162"),
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
        # V17.2.x(2026-09-10): change_30d 别名映射已删(字段本身已删, 见审计决策 Q2)
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

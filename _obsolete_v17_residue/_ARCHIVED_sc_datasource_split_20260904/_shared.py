"""stock_common/sc_datasource.py - 数据源查询模块

V10.2 更新：
  - 修复 get_lockup_expiry/get_dragon_tiger_board 的 today_str 参数污染缓存key（移除参数改为内部自动计算）
  - 放宽 industry_peers/basic_info 的 valid_if 校验（避免空值拒写缓存）
  - 新增 zhb_field_safe(field_name) 函数：按字段时效性分级判断zhb数据是否安全可用
  - get_market_status() 交易日16:30后从 closed 改为 post_close（避免盘后误显示"休市日"）

V9.5 更新：
  - aiohttp原生异步迁移：10个HTTP异步函数从 asyncio.to_thread() 改为 _async_request_with_retry/_async_quick_request
  - 修复 get_strategic_announcements_async 中 _load_config 未定义错误（改为 _load_settings）

V9.3.3 更新：
  - sync/async 重复代码重构：9个独立实现的 async 函数改为 asyncio.to_thread() 代理，消除同步逻辑重复
  - 删除未使用的 _holder_fetch_em_async 函数

V9.3.2 更新：
  - _do_request 禁用系统代理（proxies={"http": None, "https": None}），避免代理环境拦截请求
  - 增加 ProxyError 和通用 Exception 异常捕获，防止代理异常导致脚本卡死

V9.3 更新：
  - 融资融券数据清洗（get_margin_trading）：日期截断到 10 位，过滤金额全为 0 的无效行

V9.2 更新：
  - 约 24 处 except Exception: pass 加 _debug_log 日志
  - is_trading_day() 降级到 weekday 判断时打印首次警告
  - fcf_forecast 类型标注修正：List[float] → Optional[List[float]]

V9.1.1 更新：
  - 移除 render_f10_chapter() 死代码（F10 章节已从报告中移除）
  - F10 优先级调整：移除研报/大宗/十大流通股东/利润表/资产负债表的 F10 优先逻辑

V9.1 更新：
  - 11 个 HTTP 函数添加 F10 优先逻辑（F10 优先 + HTTP 兜底）
  - 7 个异步函数委托到同步版（自动获得 F10 优先逻辑）
  - 新增 6 个验证函数（verify_financial_data 等，对比 F10 vs HTTP/TDX）
  - 新增 render_data_quality_appendix() 渲染数据质量核查附录

包含所有外部数据源查询函数，按功能分组：
- 东财数据中心
- 股东数据
- 公告和股东结构
- 行情、研报、北向资金
- 融资融券、大宗交易、分红、概念
- 同花顺、行业对比、新闻
- 新浪财报、限售解禁、毛利率
- 交易日历、异步包装
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time
import re
import json
import asyncio
import os

# 导入网络层
from stock_common.sc_network import (
    em_get,
    _quick_request,
    requires_push2,
    DATACENTER_URL,
    UA,
    _http_logger,
    _biz_logger,
    _debug_log,
    _async_request_with_retry,
    _async_quick_request,
    RateLimitBlockedError,
)

# 导入配置加载
from stock_common.sc_utils import _load_settings, _safe_float, em_secid_prefix  # V17.0 S3: 统一 secid 前缀

# 导入缓存层
from core.stock_cache import TTL, cached, make_valid_if  # V15.2: 强化 valid_if

_HOLDER_CACHE_TTL: int = 60 * 86400

_HOLDER_CACHE_REFRESH: int = 90 * 86400

_CNINFO_ORGID_CACHE = {}

_holder_structure_cache: Dict[str, List[Dict[str, Any]]] = {}

_EM_BATCH_CACHE: Dict[str, Dict[str, Any]] = {}

_EM_BATCH_CACHE_DATE: str = ""

_PROFIT_FORECAST_CACHE = None

_PROFIT_FORECAST_INDEX: dict = {}

_PROFIT_FORECAST_INDEX_SHORT: dict = {}

_YJYG_ALL_CACHE = None

_PROFIT_CACHE_LOCK = None

_YJYG_LOCK = None

_DC_PREFETCH_FUTURES: Dict[Any, Any] = {}

_THS_HOT_REASON_CACHE: Dict[str, list] = {}

_calendar_fallback_warned = False

_TDXHY_CACHE: Optional[Dict[str, str]] = None

_EM_L2_MAP: Optional[Dict[str, str]] = None

_EM_L2_MEMBERS: Optional[Dict[str, List[str]]] = None

_EM_L2_LOADED_TS = 0.0

_EM_L2_TTL = 7 * 86400

_EM_INDUSTRY_L1_NAMES = frozenset({
    "农林牧渔", "基础化工", "钢铁", "有色金属", "电子", "家用电器", "食品饮料",
    "纺织服饰", "轻工制造", "医药生物", "公用事业", "交通运输", "房地产", "商贸零售",
    "社会服务", "综合", "建筑材料", "建筑装饰", "电力设备", "机械设备", "国防军工",
    "汽车", "计算机", "传媒", "通信", "银行", "非银金融", "煤炭", "石油石化",
    "环保", "美容护理",
})

_ZHB_REALTIME_FIELDS = frozenset(
    {
        "change_pct",
        "change_pct_1d",
        "change_pct_2d",
        "amount",
        "amount_1d",
        "amount_2d",
        "price",
        "open",
        "high",
        "low",
        "prev_close",
    }
)

_ZHB_NEAR_REALTIME_FIELDS = frozenset(
    {
        # V10.3: 主力资金流向字段 — 日频准实时，1天延迟可接受
        "main_net_buy_hands",
        "main_net_buy_hands_1d",
        "main_net_buy_amount",
        "main_net_buy_amount_1d",
        # V16.3.3: streak_days 连板天数 1 个交易日即变（8/7 涨停 → 8/8 可能断板）——
        # 原归静态(3天)严重失真，上移准实时
        "streak_days",
    }
)

_ZHB_STATIC_FIELDS = frozenset(
    {
        "ipo_price",
        "employee_count",
        "total_shares",
        "float_shares",
        "total_shares_wan",
        "float_shares_wan",
        "industry",
        "industry_code",
        "board",
        "concepts",
        "list_date",
        "name",
    }
)

_ULIST_BATCH_FIELDS = "f2,f3,f4,f5,f6,f8,f12,f14,f15,f16,f17,f18,f20,f21"

_ULIST_BATCH_SIZE = 300

_EM_BOARD_TYPE_FS_MAP = {
    0: "m:90+t:2",  # 行业一级
    1: "m:90+t:2",  # 行业二级（东财不区分，使用相同 fs）
    3: "m:90+t:1",  # 地域
    4: "m:90+t:3",  # 概念
}

_FFLOW_HOSTS = (
    "push2delay.eastmoney.com", # 延时镜像优先(独立风控, 当日数据够用)
    "push2his.eastmoney.com",   # 历史资金流主域(全窗口, 兜底)
    "push2.eastmoney.com",      # 实时主域(最后兜底)
)

_TDX_QC_URL = "http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp"

_TDX_QC_TOKEN = "6679f5cadca97d68245a086793fc1bfc0a50b487487c812f"

_EM_XUANGU_URL = "https://data.eastmoney.com/dataapi/xuangu/list"

_KPL_HQ = "https://apphwhq.longhuvip.com/w1/api/index.php"

_KPL_HIS = "https://apphis.longhuvip.com/w1/api/index.php"

_KPL_LHB = "https://applhb.longhuvip.com/w1/api/index.php"

_KPL_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; ALN-AL00 Build/W528JS)",
    "Connection": "Keep-Alive",
}

_KPL_BASE = {
    "PhoneOSNew": "1",
    "DeviceID": "80ca7d1b-2a24-3cd0-a915-99b61f6f88aa",
    "VerSion": "5.23.0.4",
    "apiv": "w44",
    "UserID": "",
    "Token": "",
}

_KPL_LAST_CALL: float = 0.0

def _tdx_root() -> str:
    """TDX 安装根目录（M12 修复：原代码硬编码 C:\\new_tdx64，非该安装路径的机器直接 FileNotFoundError）。

    优先读取环境变量 TDX_HOME / TDX_ROOT，缺省回退 C:\\new_tdx64 以保持兼容。
    """
    return os.environ.get("TDX_HOME") or os.environ.get("TDX_ROOT") or r"C:\new_tdx64"

__all__ = [
    'Any',
    'DATACENTER_URL',
    'Dict',
    'List',
    'Optional',
    'RateLimitBlockedError',
    'TTL',
    'Tuple',
    'UA',
    '_CNINFO_ORGID_CACHE',
    '_DC_PREFETCH_FUTURES',
    '_EM_BATCH_CACHE',
    '_EM_BATCH_CACHE_DATE',
    '_EM_BOARD_TYPE_FS_MAP',
    '_EM_INDUSTRY_L1_NAMES',
    '_EM_L2_LOADED_TS',
    '_EM_L2_MAP',
    '_EM_L2_MEMBERS',
    '_EM_L2_TTL',
    '_EM_XUANGU_URL',
    '_FFLOW_HOSTS',
    '_HOLDER_CACHE_REFRESH',
    '_HOLDER_CACHE_TTL',
    '_KPL_BASE',
    '_KPL_HEADERS',
    '_KPL_HIS',
    '_KPL_HQ',
    '_KPL_LAST_CALL',
    '_KPL_LHB',
    '_PROFIT_CACHE_LOCK',
    '_PROFIT_FORECAST_CACHE',
    '_PROFIT_FORECAST_INDEX',
    '_PROFIT_FORECAST_INDEX_SHORT',
    '_TDXHY_CACHE',
    '_TDX_QC_TOKEN',
    '_TDX_QC_URL',
    '_THS_HOT_REASON_CACHE',
    '_ULIST_BATCH_FIELDS',
    '_ULIST_BATCH_SIZE',
    '_YJYG_ALL_CACHE',
    '_YJYG_LOCK',
    '_ZHB_NEAR_REALTIME_FIELDS',
    '_ZHB_REALTIME_FIELDS',
    '_ZHB_STATIC_FIELDS',
    '_async_quick_request',
    '_async_request_with_retry',
    '_biz_logger',
    '_calendar_fallback_warned',
    '_debug_log',
    '_holder_structure_cache',
    '_http_logger',
    '_load_settings',
    '_quick_request',
    '_safe_float',
    'asyncio',
    'cached',
    'datetime',
    'em_get',
    'em_secid_prefix',
    'json',
    'make_valid_if',
    'os',
    're',
    'requires_push2',
    'time',
    'timedelta'
]

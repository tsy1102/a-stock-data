#!/usr/bin/env python3
"""stock_cache.py — 统一缓存层 (SQLite + 装饰器模式)

设计目标：
  - 所有 get_* 网络请求函数统一走本层，避免重复请求 + 降低 API 被封概率
  - 基于 SQLite 的持久化缓存，支持 TTL 自动过期 + LRU 清理
  - 装饰器模式：@cached，不破坏原函数签名（@cached_async 从未实现，V17.0 已移除占位）

V15.0 更新：
  - ZHB 离线数据全量旁路 (Bypass SQLite Disk Cache)：30+ 静态/估值/财务字段直接在 RAM 字典提取（<0.001ms），零 SQLite 磁盘读写开销
  - 数据库职责瘦身：仅保留历史 K线、龙虎榜席位明细、F10 报表三表等重网络 API
  - 数据库空间瘦身，杜绝 Windows 平台 .db-journal 文件死锁风险

V15.2 更新：
  - 统一 valid_if 工厂函数 make_valid_if()：拒绝 None/空 dict/空 list/全零 dict，替代散落的 r is not None
  - 恢复 V10.0/V12.6 期间简化的 ZHB 交叉验证 _cross_verify_with_zhb()
  - 恢复 cross_verify=True "两次获取一致" 语义（仅多天 TTL 启用）
  - L1 缓存上限 5000→10000，避免 val 报告 5721+ zhb_data 频繁淘汰
  - _has_zero_price 递归检查嵌套结构，捕获龙虎榜未成交席位等 0 值
  - stock_cache.py clear CLI 增强，支持按 category 清理

V10.2 更新：
  - 修复 cross_verify 读写互斥BUG：get_cache 的 prev_value != value 检查与 set_cache 数据变化分支冲突，导致14个分类缓存永久失效
  - 修复 _has_zero_price 递归误杀：原递归检查嵌套结构导致龙虎榜/行业对比等含0值子项的有效缓存被跳过，改为仅检查顶层
  - 修复 today_str 污染缓存key：lockup_expiry/dragon_tiger 函数参数含 today_str 导致跨日key不同，移除该参数改为内部自动计算

V9.3.3 更新：
  - schema 单点维护：定义 _CACHE_TABLE_SQL/_CACHE_INDEX_SQLS/_CACHE_PRAGMAS 常量，消除 _get_db() 和 _get_async_db() 的重复代码
  - 删除 _migrate_verify_columns，prev_value/verified 字段直接定义在主表 SQL 中

V9.3.2 更新：
  - journal_mode 从 WAL 改为 DELETE，避免多进程并发写产生 -wal/-shm 文件锁死锁
  - cache_size 从 -64000(64MB) 降到 -8000(8MB)，减少多进程内存占用

V9.3 更新：
  - 行情缓存 Key 增加交易日期隔离：格式改为 Q:{code}:{trading_date}，盘前/盘中数据独立保留
  - 异步缓存字段迁移补全：_get_async_db() 自动迁移 prev_value / verified 列

V9.2 更新：
  - 新增交叉验证机制（cross_verify）：11 个多天 TTL 分类启用两次获取对比
  - 新增 prev_value / verified 字段，支持自动表结构迁移
  - cross_verify 分支 SELECT-then-UPDATE 加 _db_lock 并发保护
  - 异步连接复用：_get_async_db() 单例，3 个异步函数共享连接
  - 约 6 处 except Exception: pass 加 _cache_logger.debug 日志
  - 移除 # type: ignore，用 cast() 替代

V9.1 更新：
  - 新增 16 个 F10 分类 TTL（5 个高频用交易日过期，11 个低频用固定 TTL）
  - @cached / set_cache 新增 trading_day: bool 参数
  - 新增 _calc_trading_day_expiry() 按最近交易日计算过期时间

TTL 分级策略（V10.0 优化）：
  - 静态数据（股票基本信息、概念板块）：30 天
  - 财务数据（财报、资产负债表）：90 天
  - 日频数据（龙虎榜、K线、资金流、打板）：7 天（历史数据不变）
  - 历史数据（北向、解禁、融资融券、大宗）：14-90 天
  - 研报：3 天
  - 行业/概念热度：24 小时
  - 分红历史：30 天
  - 实时行情（get_tencent_quote）：不缓存
  - 缓存命中率统计：进程退出时自动打印（atexit）

目录结构：
  cache/
  └── stock_cache.db        # SQLite 数据库文件
"""

from __future__ import annotations

import json
from collections import OrderedDict  # V15.3: L1 缓存改 LRU
from dataclasses import asdict, is_dataclass
import os
import sys
import hashlib
import time
import sqlite3
import threading
import atexit
import functools
import logging
from typing import Any, Callable, Dict, Optional, TypeVar, Union, cast
from datetime import datetime, date, time as dtime
from pathlib import Path

_cache_logger = logging.getLogger("stock_cache")

# ═══════════════════════════════════════
# L1 内存缓存（V10.3 新增）
# ═══════════════════════════════════════
# L1: Memory Cache — 同脚本运行期内零I/O，大幅提升命中率
# L2: SQLite Cache — 跨进程/跨运行持久化
#
# L1 缓存策略：
#   - 使用字典存储，key为完整cache_key，value为(value, expiry_time)元组
#   - 支持TTL自动过期，get时检查expiry_time
#   - 最大条目数限制（防止内存无限增长）
#   - 线程安全（使用锁）
#

# V15.3 LRU 改造: 用 OrderedDict 维护访问顺序，热点 key 永驻
# 旧版按"最早过期"淘汰会把热点 key 错杀（如果热点 key ttl 短）
_L1_CACHE: "OrderedDict[str, tuple]" = OrderedDict()  # {cache_key: (value, expiry_timestamp)}
_L1_CACHE_LOCK = threading.Lock()
_L1_MAX_ENTRIES = 10000  # V15.2: L1最大条目数 5000→10000（val 报告 5721+ zhb_data 频繁淘汰）


def _l1_get(key: str, cross_verify: bool = False) -> Optional[Any]:
    """L1内存缓存读取。V15.3 LRU: 访问时把 key 移到 OrderedDict 末尾。
    V16.2: 存储 (value, expiry, verified) —— cross_verify 模式拒绝未验证缓存（修复 L1 绕过 verified）。"""
    with _L1_CACHE_LOCK:
        entry = _L1_CACHE.get(key)
        if entry is None:
            return None
        value, expiry = entry[0], entry[1]
        verified = entry[2] if len(entry) > 2 else False
        if expiry > time.time():
            if cross_verify and not verified:
                return None
            # LRU: 命中时移到末尾（最近使用），淘汰时 popitem(last=False) 删最久未用
            _L1_CACHE.move_to_end(key)
            return value
        del _L1_CACHE[key]
    return None


def _l1_set(key: str, value: Any, ttl_seconds: int, verified: bool = False) -> None:
    """L1内存缓存写入。

    V15.3 LRU: 写入时已存在则刷新 expiry 并移到末尾；
    满了时 popitem(last=False) 删除最久未访问的 key（热点 key 永驻）。

    V13.1: dataclass 透明序列化，确保 get_cache 返回 dict（不破坏现有调用）。
    V16.2: 存储 verified 标记（cross_verify 数据一致性追踪）。
    """
    serialized = _serialize_for_cache(value)
    with _L1_CACHE_LOCK:
        expiry = time.time() + ttl_seconds
        if key in _L1_CACHE:
            # 已存在则更新 + 移到末尾
            _L1_CACHE[key] = (serialized, expiry, verified)
            _L1_CACHE.move_to_end(key)
            return
        _L1_CACHE[key] = (serialized, expiry, verified)
        if len(_L1_CACHE) > _L1_MAX_ENTRIES:
            # 淘汰最久未访问的（OrderedDict 头部）
            _L1_CACHE.popitem(last=False)


def _l1_clear() -> None:
    """清空L1内存缓存。"""
    with _L1_CACHE_LOCK:
        _L1_CACHE.clear()


# ═══════════════════════════════════════
# 缓存命中率统计（V10.0）
# ═══════════════════════════════════════
_CACHE_STATS: Dict[str, Any] = {
    "total_get": 0,
    "total_hit": 0,
    "category_stats": {},  # {category: {"hits": 0, "misses": 0}}
}
_STATS_LOCK = threading.Lock()


def _record_cache_hit(category: str, hit: bool) -> None:
    """记录缓存命中/未命中。"""
    with _STATS_LOCK:
        _CACHE_STATS["total_get"] += 1
        if hit:
            _CACHE_STATS["total_hit"] += 1
        cat_stats = _CACHE_STATS["category_stats"].setdefault(category, {"hits": 0, "misses": 0})
        if hit:
            cat_stats["hits"] += 1
        else:
            cat_stats["misses"] += 1


# V16.0: 原内存版 print_cache_stats（旧 175 行）与 CLI 版（1001 行）同名冲突，
# 后者覆盖前者 → 内存版为死代码，已删除。保留 CLI DB 统计版。
# atexit 注册（原 200 行）实际运行时指向 CLI 版。


# ═══════════════════════════════════════
# 目录与文件路径
# ═══════════════════════════════════════
# V17.0 包化: 上提一级到仓库根(模块移入 core/ 后 __file__ 在 core/ 下)
_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cache")
_CACHE_DB = os.path.join(_CACHE_DIR, "stock_cache.db")
os.makedirs(_CACHE_DIR, exist_ok=True)

# 缓存大小上限（500 MB）
_MAX_CACHE_SIZE_MB = 500
_MAX_CACHE_SIZE_BYTES = _MAX_CACHE_SIZE_MB * 1024 * 1024

# 环境变量开关：STOCK_NOCACHE=1 临时禁用缓存
_DISABLE_CACHE = os.environ.get("STOCK_NOCACHE", "") == "1"

# ═══════════════════════════════════════
# V16 软过期窗口（秒）: 硬过期后仍可返回旧值的窗口
# 解决"集体过期 → 并发重拉 → 限流/封 IP"（参考仓库: 东财风控，批量任务降频）
# 适用: HTTP 重负载分类。窗口取 1 个 TTL 周期，过期后数据仍可信（历史数据不变）
_SOFT_EXPIRY_WINDOW: "Dict[str, int]" = {
    "dragon_tiger":     7 * 86400,   # 历史数据不变，过期后仍可信
    "fund_flow":        7 * 86400,
    "margin_trading":   7 * 86400,
    "block_trade":      7 * 86400,
    "lockup_expiry":    7 * 86400,
    "announcements":    7 * 86400,
    "northbound":       7 * 86400,
    "reports":          1 * 86400,
    "industry_reports": 1 * 86400,
    "stock_news":       6 * 3600,
    "global_news":      6 * 3600,
    "news":             6 * 3600,
    "hot_rank":         2 * 3600,
    "hot_concept":      2 * 3600,
}

# 软过期命中统计
_SOFT_STATS = {"soft_hit_count": 0, "hard_miss_count": 0}

# V16.0: 批量提交计数器 — L2 读命中不再每次 UPDATE 后立即 commit，
# 每 _COMMIT_BATCH 次才 commit 一次，减少万级读命中的 SQLite 写放大
_COMMIT_BATCH = 50
_pending_commit_count = 0
# V16.0: 写路径 _enforce_size_limit 节流计数器 — 每 _SIZE_LIMIT_EVERY 次写才全表清理
_SIZE_LIMIT_EVERY = 100
_write_count_since_cleanup = 0


def _maybe_commit(force: bool = False) -> None:
    """V16.0: 批量提交：达到阈值或强制时才 commit。"""
    global _pending_commit_count
    _pending_commit_count += 1
    if force or _pending_commit_count >= _COMMIT_BATCH:
        try:
            _get_db().commit()
        except Exception as _e:
            _cache_logger.debug(f"_maybe_commit: {_e}")
        _pending_commit_count = 0


def _soft_expiry_allowed(category: str, expires_at: float, now: float) -> bool:
    """软过期判断: 条目已硬过期，但在软窗口内 → 允许返回旧值。"""
    window = _SOFT_EXPIRY_WINDOW.get(category, 0)
    if window <= 0:
        return False
    return now < expires_at + window


# ═══════════════════════════════════════
# TTL 常量（秒）
# ═══════════════════════════════════════
TTL: Dict[str, int] = {
    # 静态数据（几乎不变）
    "static_permanent":  3650 * 86400,  # V16.3.3: 绝对不变字段（上市日期/发行价/核心名称/代码/交易所）——10 年
    "basic_info":       1 * 3600,    # 股票基本信息（含市值/价格等动态字段，V16.3 O24: 1天→1小时）
    "basic_info_static": 365 * 86400, # 股票静态信息（总股本/上市日期——上市日期永远不变，V16.3 O24: 90天→365天）
    "share_capital":   90 * 86400,   # 股本数据（总股本、流通股，V10.1新增）
    "concept_blocks":  30 * 86400,   # 概念板块列表（V10.0: 7天→30天）
    "board_type":       7 * 86400,   # 沪市/深市/北交所
    "board_list":       7 * 86400,   # 板块列表（行业排名参照系——T-1 可接受，V16.3 O25 新增，trading_day 覆盖）

    # 财务数据（改为 24 小时或跟随 trading_day，废弃原 90 天静态，防止错位穿透）
    "financial":        24 * 3600,   # 新浪利润表
    "balance_sheet":    24 * 3600,   # 新浪资产负债表
    "cash_flow":        24 * 3600,   # 东财现金流量表（V9.6新增）
    "eps_forecast":     24 * 3600,   # EPS 预测

    # 日频数据（收盘后固定，历史数据不变可延长TTL）
    "dragon_tiger":     7 * 86400,   # 龙虎榜（历史数据不变，V10.0: 1天→7天）
    "northbound":      30 * 86400,   # 北向资金持股（历史数据不变，V10.0: 7天→30天）
    "margin_trading":  14 * 86400,   # 融资融券（历史数据不变，V10.0: 3天→14天）
    "block_trade":     14 * 86400,   # 大宗交易（历史数据不变，V10.0: 3天→14天）
    "lockup_expiry":   90 * 86400,   # 限售解禁（日期固定，V10.0: 7天→90天）
    "announcements":   30 * 86400,   # 巨潮公告（发布后不变，V10.0: 7天→30天）
    "hsgt_flow":       14 * 86400,   # 沪深港通资金流（历史数据不变，V10.0: 3天→14天）
    "kline":            7 * 86400,   # K线行情（历史数据不变，V10.0: 1天→7天）
    "limit_pool":       7 * 86400,   # 打板数据（历史数据不变，V10.0: 1天→7天）
    "fund_flow":        7 * 86400,   # 资金流数据（历史数据不变，V10.0: 1天→7天）

    # 舆情互动（V8.9 新增）
    "hot_rank":         1 * 3600,    # 东财人气榜（小时级变化）
    "hot_concept":      1 * 3600,    # 概念命中（小时级变化）

    # 研报（V16 校准: 3天→1小时，避免新研报滞后；研报非秒级数据，1h 刷新足够）
    "reports":          1 * 3600,    # 东财研报列表
    "industry_reports": 1 * 3600,    # 行业研报

    # 新闻舆情（更新频繁）
    "stock_news":       6 * 3600,    # 个股新闻（6小时）
    "global_news":      1 * 3600,    # 全球资讯（1小时）
    "news":             6 * 3600,    # 财联社快讯（V9.6新增，6小时）

    # 行业/概念热度（每日变化，V11.2: 改为交易日模式）
    "industry_compare":  24 * 3600,   # 行业板块排名（trading_day=True覆盖）
    "industry_peers_v2": 24 * 3600,   # 行业可比公司（V16.2.16 版本化——trading_day 覆盖）
    "ths_hot_reason":   24 * 3600,   # 同花顺热点题材（trading_day=True覆盖）
    "hsgt_macro_flow":  24 * 3600,   # 北向资金大盘流向（trading_day=True覆盖）

    # V16.3.3 新源缓存分类（2026-08-10 字典 12.15.5 充实后补充）
    "market_emotion_multi": 7 * 86400,  # 涨停池三源互校（财联社=KPL=复盘啦——trading_day 覆盖，盘中 6s+ 调用必须缓存）
    "kpl_sentiment":        7 * 86400,  # KPL 市场情绪（strong/连板/涨停——trading_day 覆盖）
    "fupan_review":         7 * 86400,  # 复盘啦涨停天梯/盘面（get_zttt/get_pmsl——trading_day 覆盖）
    "plate_rotation":       7 * 86400,  # 板块轮动 N×天矩阵（duanxianxia——trading_day 覆盖）
    "fuyao_snapshot":       30 * 60,    # fuyao 行情快照（30min——盘中动态）
    "fuyao_valuation":      1 * 3600,   # fuyao 估值（1h——pe/pb 随价但低频）
    "fuyao_ladder":         7 * 86400,  # fuyao 涨停梯队（trading_day 覆盖）
    "fuyao_auction":        30 * 60,    # fuyao 集合竞价快照（30min；stage=final 终态盘后稳定）
    # V17.0.5: 基金域/财务指标（trading_day 覆盖——报告期/定期披露数据日频足够）
    "fuyao_fund_holdings":  7 * 86400,  # 基金重仓持仓（lng/med 批量侧证防 N×M 重复请求）
    "fuyao_indicators":     7 * 86400,  # 五类财务指标（ROE/扣非/ROA 官方口径）
    "fuyao_seal_map":       30 * 60,    # 涨停池封单映射（30min——盘中封单动态，sht 衰减率用）

    # 分红历史（公告不频繁）
    "dividend":         30 * 86400,   # 分红历史

    # F10 数据（V9.0 新增；V16.3 O25 清理 8 个死分类——现 F10 走 f10_financial 等在用分类）
    # 高频分类（每日更新，休市不变，通过 @cached(trading_day=True) 启用交易日模式）
    "f10_reminders":       24 * 3600,   # F2 最新提示（交易日模式覆盖此值）
    "f10_news":            24 * 3600,   # F13 公司报道（交易日模式覆盖此值）
    "f10_announcements":   24 * 3600,   # F12 公司公告（交易日模式覆盖此值）
    "f10_fund_flow":       24 * 3600,   # F9 资金动向（交易日模式覆盖此值）
    "f10_shareholder":      7 * 86400,  # F5 股东研究（季度更新）
    "f10_share_capital":    7 * 86400,  # F4 股本结构（偶尔更新）
    "f10_financial":       24 * 3600,  # F3 财务分析（V16.3 O: F10 接入主缓存）

    # 通用兜底（1 小时）
    "default":          3600,
}


def _calc_trading_day_expiry() -> float:
    """计算交易日模式的过期时间戳（V16.3 O24 用户 TTL 语义重构）。

    用户逻辑：TTL 以"数据交易日"为粒度，非物理时间——
    - **9:30 是分界**：交易日 9:30 后 = 新的一天（延续到 24:00）；
      9:30 前数据=上一交易日（盘前 T-1 正确）
    - **同一数据交易日内的多次扫描共享缓存**（9:30 后首次拉当日数据，后续共享）
    - **非交易日不过期**（数据日不变——周五缓存跨周末仍有效，直到下个交易日 9:30）

    过期点 = 下一个数据交易日 9:30：
    - 交易日且 now >= 9:30 → 数据日=今天 → 下个交易日 9:30 过期（次日刷新）
    - 交易日且 now < 9:30 → 数据日=上一交易日 → 今天 9:30 过期（开盘即新一天）
    - 非交易日 → 数据日=最近交易日 → 下个交易日 9:30 过期

    任何异常时 fallback 到 now + 24h（保证不会因日历问题导致缓存写入失败）。

    Returns:
        float: 过期时间戳（time.time() 格式）
    """
    try:
        from stock_common.stock_calendar import is_workday, get_next_trading_day
    except Exception as _e:
        _cache_logger.debug(f"calc_trading_day_expiry import error: {_e}")
        return time.time() + 24 * 3600

    now = datetime.now()
    today = now.date()

    try:
        # V16.3 O29: 运算符优先级 bug 修复——原 `is_workday(today) and now.hour < 9 or (now.hour == 9 and now.minute < 30)`
        # 被解析为 `(is_workday and hour<9) OR (hour==9 and minute<30)`——非交易日 9:00-9:29
        # 命中第二分支（未检查 is_workday）→ target=今天 9:30（已过去）→ 缓存立即过期
        if is_workday(today) and (now.hour < 9 or (now.hour == 9 and now.minute < 30)):
            # 交易日 9:30 前：数据=上一交易日 → 今天 9:30 过期（开盘即新一天）
            target = datetime.combine(today, dtime(9, 30))
        else:
            # 9:30 后（含交易日与非交易日）：数据日已定 → 下个交易日 9:30 过期
            next_td = get_next_trading_day(today)
            target = datetime.combine(next_td, dtime(9, 30))
    except Exception as _e:
        _cache_logger.debug(f"calc_trading_day_expiry calc error: {_e}")
        # 交易日历年份超出范围或其他异常，fallback 到 24h
        return time.time() + 24 * 3600

    ts = target.timestamp()
    # 安全检查：expires_at 必须大于 now
    if ts <= time.time():
        return time.time() + 24 * 3600
    return ts

# ═══════════════════════════════════════
# SQLite Schema 常量（单点维护）
# ═══════════════════════════════════════
_CACHE_TABLE_SQL = (
    "CREATE TABLE IF NOT EXISTS cache_entries ("
    "  key TEXT PRIMARY KEY,"
    "  value BLOB NOT NULL,"
    "  created_at REAL NOT NULL,"
    "  expires_at REAL NOT NULL,"
    "  hit_count INTEGER DEFAULT 0,"
    "  last_accessed REAL NOT NULL,"
    "  prev_value BLOB,"
    "  verified INTEGER DEFAULT 0"
    ")"
)
_CACHE_INDEX_SQLS = [
    "CREATE INDEX IF NOT EXISTS idx_expires ON cache_entries(expires_at)",
    "CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)",
]
_CACHE_PRAGMAS = [
    ("PRAGMA journal_mode=DELETE",),    # DELETE 模式，多进程安全
    ("PRAGMA synchronous=NORMAL",),     # 平衡性能与安全
    ("PRAGMA cache_size=-8000",),       # 8MB 缓存
]

# ═══════════════════════════════════════
# SQLite 数据库初始化
# ═══════════════════════════════════════
_db_lock = threading.RLock()  # 多线程安全锁
_db: Optional[sqlite3.Connection] = None


def _get_db() -> sqlite3.Connection:
    """获取数据库连接（懒加载，线程安全）。"""
    global _db
    if _db is not None:
        return _db
    with _db_lock:
        if _db is not None:
            return _db
        _db = sqlite3.connect(_CACHE_DB, check_same_thread=False, timeout=30.0)
        for _pragma in _CACHE_PRAGMAS:
            _db.execute(_pragma[0])
        _db.execute(_CACHE_TABLE_SQL)
        for _idx in _CACHE_INDEX_SQLS:
            _db.execute(_idx)
        _db.commit()
        return _db


def _close_db() -> None:
    """关闭数据库连接（进程退出时调用，确保 WAL 日志完整 checkpoint）。"""
    global _db
    if _db is not None:
        with _db_lock:
            if _db is not None:
                try:
                    _db.commit()
                    _db.execute("PRAGMA wal_checkpoint(FULL)")
                    _db.close()
                    _cache_logger.debug("Database connection closed")
                except Exception as _e:
                    _cache_logger.debug(f"_close_db error: {_e}")
                _db = None

atexit.register(_close_db)


def _maybe_enforce_size_limit() -> None:
    """V16.0: 节流版 _enforce_size_limit — 每 _SIZE_LIMIT_EVERY 次写才执行一次全表清理。

    原实现每次 set_cache 都调用 _enforce_size_limit（DELETE 过期 + commit），
    冷 run 上万次写 → 上万次全表清理 ≈ 20-60s 纯浪费。
    """
    global _write_count_since_cleanup
    _write_count_since_cleanup += 1
    if _write_count_since_cleanup >= _SIZE_LIMIT_EVERY:
        _write_count_since_cleanup = 0
        try:
            _enforce_size_limit()
        except Exception as _e:
            _cache_logger.debug(f"_maybe_enforce_size_limit: {_e}")


def _enforce_size_limit() -> None:
    """写入时维护：先清理过期条目，再检查是否超限。"""
    db = _get_db()
    # 先清理过期条目（替代 _startup_cleanup 的功能）
    try:
        db.execute("DELETE FROM cache_entries WHERE expires_at<?", (time.time(),))
        db.commit()
    except Exception as _e:
        _cache_logger.debug(f"enforce_size_limit cleanup: {_e}")
    # 再检查 DB 大小是否超限
    # V16.3 C3: 变量名修正——原 db_path 实际存的是"字节数"（误导）
    db_size_bytes = os.path.getsize(_CACHE_DB)
    if db_size_bytes < _MAX_CACHE_SIZE_BYTES:
        return
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM cache_entries")
    total = cursor.fetchone()[0]
    if total == 0:
        return
    # 删除最久未访问的 20%（V16.3 C3: f-string 拼 LIMIT 改参数化，防注入模式）
    delete_count = max(1, total // 5)
    cursor.execute(
        "DELETE FROM cache_entries WHERE key IN ("
        "  SELECT key FROM cache_entries ORDER BY last_accessed ASC LIMIT ?"
        ")",
        (delete_count,),
    )
    db.commit()
    print(f"[stock_cache] 缓存超限（{db_size_bytes / 1024 / 1024:.1f}MB），已清理 {delete_count} 条最久未访问条目", flush=True)


# ═══════════════════════════════════════
# 核心缓存 API
# ═══════════════════════════════════════

def _build_key(category: str, func_name: str, *args: Any, **kwargs: Any) -> str:
    """根据函数名+参数生成缓存 key。"""
    parts = [category, func_name]
    if args:
        parts.append("_".join(str(a) for a in args))
    if kwargs:
        parts.append("_".join(f"{k}={v}" for k, v in sorted(kwargs.items())))
    raw = ":".join(parts)
    # key 过长时用 MD5 压缩
    if len(raw) > 200:
        h = hashlib.md5(raw.encode("utf-8")).hexdigest()
        return f"{category}:{func_name}:{h}"
    return raw


def get_cache(category: str, func_name: str, *args: Any,
              cross_verify: bool = False, **kwargs: Any) -> Optional[Any]:
    """查询缓存，返回解析后的数据或 None。
    V10.3: L1/L2双级缓存架构 — 优先L1内存缓存，失败fallback到L2 SQLite。

    Args:
        category: 缓存分类
        func_name: 函数名
        cross_verify: True=需要验证通过才返回（未验证返回None，触发重新获取）
        *args, **kwargs: 函数参数（用于构建key）
    """
    if _DISABLE_CACHE:
        _record_cache_hit(category, False)
        return None
    key = _build_key(category, func_name, *args, **kwargs)
    
    # V10.3: 优先 L1 内存缓存（V16.2: cross_verify 模式 L1 也校验 verified）
    l1_result = _l1_get(key, cross_verify=cross_verify)
    if l1_result is not None:
        _record_cache_hit(category, True)
        return l1_result
    
    now = time.time()
    try:
        db = _get_db()
        cursor = db.cursor()
        cursor.execute(
            "SELECT value, expires_at, hit_count, prev_value, verified "
            "FROM cache_entries WHERE key=?",
            (key,)
        )
        row = cursor.fetchone()
        if row is None:
            _record_cache_hit(category, False)
            return None
        value_blob, expires_at, hit_count, prev_value_blob, verified = row
        # V16 软过期三态判断: 新鲜 / 软过期(stale) / 硬过期
        if expires_at <= now:
            if _soft_expiry_allowed(category, expires_at, now):
                _SOFT_STATS["soft_hit_count"] += 1
            else:
                _SOFT_STATS["hard_miss_count"] += 1
                _record_cache_hit(category, False)
                return None
        # 交叉验证模式：未验证的缓存视为未命中
        # V10.2 修复：删除 prev_value != value 的误删检查
        #   原逻辑：set_cache 数据变化分支会写入 prev_value=旧值, value=新值, verified=1
        #   get_cache 检查 prev_value != value 时会删除缓存 → 永久失效
        #   prev_value 仅用于数据变更追踪，不影响缓存命中
        if cross_verify and not verified:
            _record_cache_hit(category, False)
            return None
        # 更新访问时间 + 命中计数
        # V16.0: 去掉每读 commit（原代码每次命中 UPDATE+commit → 万级重访 30-90s）
        cursor.execute(
            "UPDATE cache_entries SET hit_count=hit_count+1, last_accessed=? WHERE key=?",
            (now, key)
        )
        _maybe_commit()
        # V10.3: 将L2结果写入L1，加速后续访问
        value = json.loads(value_blob.decode("utf-8"))
        # V13.1: dataclass 自动反序列化暂不启用，由调用方按需调用 _deserialize_from_cache()
        # V16: 仅新鲜数据写回 L1；软过期 stale 数据不写（避免 L1 长期返回旧值）
        ttl = expires_at - now
        if ttl > 0:
            _l1_set(key, value, ttl, verified=bool(verified))
        _record_cache_hit(category, True)
        return value
    except Exception as _e:
        _cache_logger.debug(f"get_cache error ({key}): {_e}")
        _record_cache_hit(category, False)
        return None


def _serialize_for_cache(value):
    """V13.1: dataclass 透明序列化（写入时把 dataclass 转 dict）

    支持：
      - dataclass 实例：递归 asdict() 转为 dict
      - 嵌套结构（dict/list 内含 dataclass）：递归转换
      - 普通类型（str/int/float/None）：原样返回
    """
    if is_dataclass(value) and not isinstance(value, type):
        return _serialize_for_cache(asdict(value))
    if isinstance(value, dict):
        return {k: _serialize_for_cache(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize_for_cache(v) for v in value]
    return value


def _deserialize_from_cache(value, target_cls=None):
    """V13.1: dataclass 透明反序列化（读取时把 dict 转 dataclass）

    Args:
        value: 从缓存读出的 JSON 反序列化结果（dict/primitives）
        target_cls: 可选的目标 dataclass 类型。如果提供且 value 是 dict，
                    则反序列化为 target_cls 实例。

    V13.1 阶段暂不启用自动反序列化（避免破坏现有调用），
    仅作为工具函数提供给 V13.2 Runner 主动调用。
    """
    if target_cls is not None and isinstance(value, dict):
        try:
            return target_cls(**value)
        except (TypeError, ValueError):
            return value
    return value


# ═══════════════════════════════════════════════════════════
# V15.2: 统一 valid_if 工厂函数（替代散落的 r is not None）
# ═══════════════════════════════════════════════════════════

def make_valid_if(check_zeros: bool = True, min_size: int = 0) -> Callable[[Any], bool]:
    """V15.2: 生成通用 valid_if 校验函数。

    用于 @cached 装饰器，统一拒绝空数据缓存。

    Args:
        check_zeros: 是否检查所有数值为 0（默认 True）
        min_size: dict/list 最小有效长度（默认 0，即空 dict 拒绝）

    Returns:
        callable: 接受返回值 r，返回 True/False

    Examples:
        # F10 数据：拒绝 None/空 dict/全 0 dict
        @cached(category="f10_fund_flow", valid_if=make_valid_if())

        # 龙虎榜：要求至少 1 条记录
        @cached(category="dragon_tiger", valid_if=make_valid_if(min_size=1))

        # 纯数据列表：拒绝空 list
        @cached(category="news", valid_if=make_valid_if(check_zeros=False))
    """
    def validator(r: Any) -> bool:
        # 1) None 拒绝
        if r is None:
            return False
        # 2) 空 dict/list 拒绝
        if isinstance(r, (dict, list)) and len(r) <= min_size:
            return False
        # 3) 全 0 字段检查（仅对 dict）
        if check_zeros and isinstance(r, dict):
            for v in r.values():
                if isinstance(v, (int, float)) and v == 0:
                    return False
                # 嵌套 dict 递归检查一层
                if isinstance(v, dict):
                    for vv in v.values():
                        if isinstance(vv, (int, float)) and vv == 0:
                            return False
        return True
    return validator


def _has_zero_price(value: Any) -> bool:
    """递归检查 dict 是否包含 price=0 或 close=0（TDX 坏数据特征）。

    V15.2 修复：原 V10.2 实现仅检查顶层 dict 的 price/close 字段，但实际场景中
    龙虎榜未成交席位的子 dict 含 price=0，板块列表中无成交板块的嵌套 dict 含
    amount=0 都被漏过。改为递归检查所有 dict 层级（深度上限 3 层避免性能问题）。

    排除规则（避免误杀）：
      - list/tuple 中的 0 值不视为坏数据
      - 字段名以 _ 开头（私有标记）不检查
    """
    def _check_recursive(v: Any, depth: int = 0) -> bool:
        if depth > 3:
            return False
        if isinstance(v, dict):
            # 检查关键价格字段
            for key in ("price", "close", "open", "high", "low"):
                if v.get(key) == 0:
                    return True
            # 递归子 dict
            for sub_v in v.values():
                if _check_recursive(sub_v, depth + 1):
                    return True
        return False
    return _check_recursive(value)


# ═══════════════════════════════════════════════════════════
# V15.2: ZHB 交叉验证工具函数（恢复用户历史机制）
# ═══════════════════════════════════════════════════════════

def _cross_verify_with_zhb(code: str, http_value: Any, threshold_pct: float = 50.0) -> bool:
    """V15.2: HTTP 返回值与 ZHB dict 关键字段对比，偏离过大则拒绝。

    用途：防止"网络瞬断 → HTTP 返回异常值"被缓存。
    适用场景：F10/f10_fund_flow/dragon_tiger 等 HTTP 数据。

    Args:
        code: 股票代码
        http_value: HTTP 接口返回值（dict）
        threshold_pct: 偏离阈值（默认 50%），超出视为坏数据

    Returns:
        bool: True=通过验证，False=偏离过大拒绝

    异常安全：任何 ZHB 读取异常都返回 True（不阻断缓存）
    """
    if not code or not isinstance(http_value, dict):
        return True
    try:
        from stock_common import get_zhb_single_stock_data
        zhb = get_zhb_single_stock_data(code)
        if not zhb:
            return True  # 无 ZHB 数据时跳过验证
        # 关键字段对比（HTTP vs ZHB）
        for field in ("pe_ttm", "pb", "price", "change_pct"):
            if field not in http_value or field not in zhb:
                continue
            v_http = _safe_float(http_value.get(field))
            v_zhb = _safe_float(zhb.get(field))
            if v_zhb == 0 or v_http == 0:
                continue  # 一方为 0 时不对比
            diff_pct = abs(v_http - v_zhb) / abs(v_zhb) * 100
            if diff_pct > threshold_pct:
                # 偏离过大，记日志但不抛异常
                try:
                    from stock_common import _debug_log
                    _debug_log(f"cross_verify fail: {code} {field} http={v_http} zhb={v_zhb} diff={diff_pct:.1f}%")
                except Exception:
                    pass
                return False
    except Exception:
        return True  # 任何异常都通过验证
    return True


def _safe_float(v: Any) -> float:
    """安全转 float（V15.2: cross_verify 工具）"""
    try:
        if v is None or v == "":
            return 0.0
        return float(v)
    except (TypeError, ValueError):
        return 0.0


# V16.0: 加入 zhb_data — 17 个函数体只读 ZHB RAM 字典（<1ms），
# 原走完整 SQLite 写路径（INSERT+commit+全表清理 ≈ 2-4ms/次），负优化
# V16.3 C2: 旁路名单内的分类 = @cached 装饰器**永不写入 L1/L2**（命中率恒 0，
# 装饰器仅为接口一致性保留）——非 bug，是有意设计；后续若 data_provider 的
# get_market_snapshot 等出现真实计算开销，再移出本名单。
_ZHB_BYPASS_CATEGORIES = {
    "basic_info_static", "share_capital", "concept_blocks", "board_type",
    "zhb_data",
}


def set_cache(category: str, func_name: str, value: Any, ttl: int, *args: Any,
              trading_day: bool = False, cross_verify: bool = False, **kwargs: Any) -> None:
    """写入缓存（None/空值/价格为零不写入）。
    V15.0: ZHB 静态分类白名单触发 100% 磁盘旁路，零 SQLite 磁盘写开销。
    V15.2: F10/f10_fund_flow/dragon_tiger 自动调用 _cross_verify_with_zhb。
    """
    if _DISABLE_CACHE:
        return
    if category in _ZHB_BYPASS_CATEGORIES:
        return
    if value is None:
        return
    if isinstance(value, (list, dict)) and len(value) == 0:
        return
    # V8.9: 检测 price=0 / close=0 — TDX 坏数据特征，不缓存
    if _has_zero_price(value):
        return
    # V15.2: F10 / f10_fund_flow / dragon_tiger 自动 ZHB 交叉验证
    # 提取股票代码（args[0] 通常是 code）
    if category in ("f10_fund_flow", "f10_announcements", "f10_reminders",
                    "f10_financial", "f10_shareholder", "f10_share_capital",
                    "f10_news", "dragon_tiger") and args:
        code = args[0] if isinstance(args[0], str) else ""
        if code and not _cross_verify_with_zhb(code, value):
            return  # 偏离 ZHB 过大，拒绝缓存
    key = _build_key(category, func_name, *args, **kwargs)
    now = time.time()
    # V9.0: trading_day 模式 — 过期时间设为下一个交易日 15:00
    # V16.2 修复: min(now+ttl, 交易日截止) —— 盘中 ttl 仍生效（如 stock_quote 30min），
    # 修复原实现 trading_day 覆盖 ttl 导致实时数据盘中冻结到收盘的问题
    expires_at = _calc_trading_day_expiry() if trading_day else now + ttl
    if trading_day:
        expires_at = min(expires_at, now + ttl)
    try:
        db = _get_db()
        value_bytes = json.dumps(_serialize_for_cache(value), ensure_ascii=False).encode("utf-8")
        cursor = db.cursor()

        if not cross_verify:
            # 普通模式：直接写入，不验证
            cursor.execute(
                "INSERT OR REPLACE INTO cache_entries "
                "(key, value, created_at, expires_at, hit_count, last_accessed, prev_value, verified) "
                "VALUES (?, ?, ?, ?, 0, ?, NULL, 0)",
                (key, value_bytes, now, expires_at, now)
            )
        else:
            # V15.2 真正实现"两次获取一致"语义：
            #   - 第一次写入：verified=1（V16.0: 信任调用方 valid_if 校验，避免冷启动双拉）
            #   - 第二次相同数据：prev_value == value_bytes，verified=1
            #   - 第二次不同数据：prev_value != value_bytes，verified 降为 0
            #   - get_cache cross_verify=True 时返回 verified=1 的缓存
            #   - 冷启动首次命中即返回（V16.0 修复原逻辑首写 verified=0 → 每次冷 run 双拉）
            with _db_lock:
                cursor.execute(
                    "SELECT value, prev_value, verified FROM cache_entries WHERE key=? AND expires_at>?",
                    (key, now)
                )
                row = cursor.fetchone()
                if row is None:
                    # 第一次写入：verified=1（V16.0: 不再等待第二次验证）
                    cursor.execute(
                        "INSERT OR REPLACE INTO cache_entries "
                        "(key, value, created_at, expires_at, hit_count, last_accessed, prev_value, verified) "
                        "VALUES (?, ?, ?, ?, 0, ?, ?, 1)",
                        (key, value_bytes, now, expires_at, now, value_bytes)
                    )
                else:
                    existing_blob, prev_value_blob, verified = row
                    if prev_value_blob == value_bytes:
                        # 第二次获取与上次一致：标记 verified=1（两次获取一致）
                        cursor.execute(
                            "UPDATE cache_entries SET value=?, verified=1, "
                            "expires_at=?, last_accessed=? WHERE key=?",
                            (value_bytes, expires_at, now, key)
                        )
                    else:
                        # 第二次获取与上次不同：仅更新 prev_value/value，verified 仍 0
                        # 等待下一次获取再验证
                        cursor.execute(
                            "UPDATE cache_entries SET value=?, prev_value=?, verified=0, "
                            "created_at=?, expires_at=?, last_accessed=? WHERE key=?",
                            (value_bytes, existing_blob, now, expires_at, now, key)
                        )

        # V16.0: 写路径去掉每写 commit（原每次 INSERT + commit + 全表清理双 commit）
        _maybe_commit(force=True)  # 写入必须落盘，但用批量化 commit
        _maybe_enforce_size_limit()
        
        # V10.3: 同时写入 L1 内存缓存（V16.2: 带 verified 标记）
        l1_ttl = expires_at - now
        if l1_ttl > 0:
            # V16.4.1: row is None(首次插入)分支走 else 前的 INSERT, `verified` 从未定义 →
            # 原 NameError 被外层 except 吞掉, L1 永不写入(6 个 cross_verify 分类每次冷写都丢 L1)
            _l1_verified = bool(verified) if cross_verify and "verified" in locals() else False
            _l1_set(key, value, l1_ttl, verified=_l1_verified)
    except Exception as _e:
        _cache_logger.debug(f"set_cache: {_e}")


def invalidate_category(category: str, pattern: str = "") -> int:
    """按分类批量删除缓存条目。

    Args:
        category: 分类前缀（如 "dragon_tiger"）
        pattern: 可选的代码过滤（如 "600519"，空=删除该分类全部）

    Returns:
        删除的条目数量

    V12.1: 同步清空 L1 内存缓存，防止 L1/L2 数据不一致。
    """
    try:
        db = _get_db()
        cursor = db.cursor()
        if pattern:
            cursor.execute(
                "DELETE FROM cache_entries WHERE key LIKE ?",
                (f"{category}:%{pattern}%",)
            )
        else:
            cursor.execute(
                "DELETE FROM cache_entries WHERE key LIKE ?",
                (f"{category}:%",)
            )
        db.commit()
        deleted = cursor.rowcount
        # V12.1: 同步清空 L1 内存缓存，确保一致性
        # V12.5 修复: 函数名错误 _l1_cache_clear → _l1_clear (V12.1 引入的回归 bug)
        _l1_clear()
        return deleted
    except Exception as _e:
        _cache_logger.debug(f"invalidate_category error ({category}): {_e}")
        return 0


def invalidate_prefix(prefix: str) -> int:
    """按 key 前缀批量删除（如 "holder:600519"）。

    V12.1: 同步清空 L1 内存缓存，防止 L1/L2 数据不一致。
    """
    try:
        db = _get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM cache_entries WHERE key LIKE ?", (f"{prefix}%",))
        db.commit()
        deleted = cursor.rowcount
        # V12.1: 同步清空 L1 内存缓存，确保一致性
        # V12.5 修复: 函数名错误 _l1_cache_clear → _l1_clear
        _l1_clear()
        return deleted
    except Exception as _e:
        _cache_logger.debug(f"invalidate_prefix error ({prefix}): {_e}")
        return 0


def clear_expired() -> int:
    """删除所有已过期的缓存条目，返回删除数量。
    V16.2: 同时清理 L1 中已过期条目（原 L1 残留导致 clear 后仍返回旧值）。"""
    _l1_clear()  # L1 无法精确按 key 过期，直接整体清（进程级，成本低）
    try:
        db = _get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM cache_entries WHERE expires_at<?", (time.time(),))
        db.commit()
        return cursor.rowcount
    except Exception as _e:
        _cache_logger.debug(f"clear_expired error: {_e}")
        return 0


def clear_all() -> None:
    """清空所有缓存。V16.2: 同时清空 L1（原只清 SQLite，同进程仍返回旧值）。"""
    _l1_clear()
    try:
        db = _get_db()
        db.execute("DELETE FROM cache_entries")
        db.commit()
    except Exception as _e:
        _cache_logger.debug(f"clear_cache: {_e}")


def cache_stats() -> Dict[str, Any]:
    """返回缓存统计信息（供调试和 CLI 使用）。"""
    try:
        db = _get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*), SUM(hit_count), SUM(LENGTH(value)) FROM cache_entries")
        row = cursor.fetchone()
        count, hits, size_bytes = row
        cursor.execute("SELECT COUNT(*) FROM cache_entries WHERE expires_at<?", (time.time(),))
        expired = cursor.fetchone()[0]

        # V9.2: 验证状态统计
        now = time.time()
        cursor.execute(
            "SELECT COUNT(*) FROM cache_entries WHERE expires_at>? AND verified=1",
            (now,)
        )
        verified_valid = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM cache_entries WHERE expires_at>? AND verified=0",
            (now,)
        )
        unverified_valid = cursor.fetchone()[0]

        # 按分类统计（含验证状态）
        cursor.execute(
            "SELECT SUBSTR(key, 1, INSTR(key, ':') - 1) AS cat, COUNT(*), SUM(hit_count), "
            "SUM(CASE WHEN verified=1 AND expires_at>? THEN 1 ELSE 0 END) AS verified_cnt "
            "FROM cache_entries GROUP BY cat",
            (now,)
        )
        by_category = {}
        for cat, cnt, h, v_cnt in cursor.fetchall():
            by_category[cat or "unknown"] = {
                "count": cnt,
                "hits": h or 0,
                "verified": v_cnt or 0,
            }

        # 文件大小
        db_file_size = os.path.getsize(_CACHE_DB) if os.path.exists(_CACHE_DB) else 0

        valid = max(0, (count or 0) - expired)
        return {
            "total_entries": count or 0,
            "valid_entries": valid,
            "total_hits": hits or 0,
            "expired_entries": expired,
            "verified_entries": verified_valid or 0,
            "unverified_entries": unverified_valid or 0,
            "db_size_bytes": db_file_size,
            "db_size_mb": round(db_file_size / 1024 / 1024, 2),
            "by_category": by_category,
        }
    except Exception as e:
        return {"error": str(e)}


def print_cache_stats() -> None:
    """打印缓存统计到 stdout（CLI 工具函数）。"""
    stats = cache_stats()
    if "error" in stats:
        print(f"缓存统计失败: {stats['error']}", flush=True)
        return
    print("\n" + "=" * 50, flush=True)
    print("  📦 缓存统计", flush=True)
    print("=" * 50, flush=True)
    expired = stats['expired_entries']
    valid = stats['valid_entries']
    verified = stats.get('verified_entries', 0)
    unverified = stats.get('unverified_entries', 0)
    print(f"  总条目数   : {stats['total_entries']}", flush=True)
    print(f"  ├─ 有效   : {valid} (查询时自动命中)", flush=True)
    print(f"  │  ├─ 已验证 : {verified} (交叉验证通过)", flush=True)
    print(f"  │  └─ 未验证 : {unverified} (等待二次确认)", flush=True)
    print(f"  └─ 待清理 : {expired} (过期数据，查询时自动跳过)", flush=True)
    print(f"  总命中次数 : {stats['total_hits']}", flush=True)
    print(f"  数据库大小 : {stats['db_size_mb']} MB / {_MAX_CACHE_SIZE_MB} MB", flush=True)
    print(f"  使用率     : {stats['db_size_mb'] / _MAX_CACHE_SIZE_MB * 100:.1f}%", flush=True)
    print("-" * 50, flush=True)
    print("  各分类统计（有效条目）：", flush=True)
    for cat, info in sorted(stats.get("by_category", {}).items()):
        v = info.get('verified', 0)
        print(f"    {cat:<20} 条目: {info['count']:>5}  已验证: {v:>4}  命中: {info['hits']:>6}", flush=True)
    print("=" * 50 + "\n", flush=True)


# ═══════════════════════════════════════
# 同步装饰器 @cached
# ═══════════════════════════════════════
F = TypeVar("F", bound=Callable[..., Any])


def cached(category: str, ttl_seconds: Optional[int] = None,
           use_args: bool = True,
           valid_if: Optional[Callable[[Any], bool]] = None,
           trading_day: bool = False,
           cross_verify: bool = False) -> Callable[[F], F]:
    """同步函数缓存装饰器。

    用法：
        @cached(category="dragon_tiger", ttl_seconds=TTL["dragon_tiger"])
        def get_dragon_tiger_board(code: str, ...):
            ...

    Args:
        category: 缓存分类（决定 TTL 查表 key）
        ttl_seconds: 覆盖 TTL，None 则用 TTL[category]
        use_args: True=缓存 key 包含函数参数（区分不同股票代码），False=仅函数名
        valid_if: 可选校验函数，接收函数返回值，True=写入缓存，False=跳过
        trading_day: True=按交易日过期（下一个交易日 15:00），False=固定 TTL（默认）
        cross_verify: True=启用交叉验证（两次获取一致才标记为已验证，未验证不返回缓存）
    """
    _ttl = ttl_seconds if ttl_seconds is not None else TTL.get(category, TTL["default"])
    # V16.2: per-key single-flight —— 同 key 并发 miss 时仅一次上游请求（SQLite 锁不能阻止重复网络请求）
    _sf_locks: Dict[str, threading.Lock] = {}
    _sf_lock_guard = threading.Lock()

    def _sf_acquire(sf_key: str) -> threading.Lock:
        with _sf_lock_guard:
            lock = _sf_locks.get(sf_key)
            if lock is None:
                lock = threading.Lock()
                _sf_locks[sf_key] = lock
            return lock

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if _DISABLE_CACHE:
                return func(*args, **kwargs)
            # 提取缓存 key 的参数
            if use_args:
                cache_value = get_cache(category, func.__name__, *args,
                                        cross_verify=cross_verify, **kwargs)
                sf_key = _build_key(category, func.__name__, *args, **kwargs)
            else:
                cache_value = get_cache(category, func.__name__,
                                        cross_verify=cross_verify)
                sf_key = f"{category}:{func.__name__}"
            if cache_value is not None:
                # V8.9: 读取时也校验 — 命中但校验不通过视为未命中
                if valid_if is None or valid_if(cache_value):
                    return cache_value
            else:
                cache_value = None  # 确保下面重新获取
            # V16.2: single-flight —— 锁内再查一次（双检锁），避免重复上游请求
            _lock = _sf_acquire(sf_key)
            with _lock:
                cache_value2 = get_cache(category, func.__name__,
                                         cross_verify=cross_verify, *args, **kwargs) if use_args else get_cache(
                                             category, func.__name__, cross_verify=cross_verify)
                if cache_value2 is not None and (valid_if is None or valid_if(cache_value2)):
                    return cache_value2
                result = func(*args, **kwargs)
            # valid_if 校验：不通过则不缓存
            if valid_if is None or valid_if(result):
                if use_args:
                    set_cache(category, func.__name__, result, _ttl, *args,
                              trading_day=trading_day, cross_verify=cross_verify, **kwargs)
                else:
                    set_cache(category, func.__name__, result, _ttl,
                              trading_day=trading_day, cross_verify=cross_verify)
            return result

        return cast(F, wrapper)
    return decorator


# ═══════════════════════════════════════
# V17.0 S8: @cached_async 从未实现(此前仅注释占位)——实际异步模式为
# "sync @cached + async 包装委托 sync" (sc_datasource/report 层), 占位 TypeVar AF 一并移除。
# ═══════════════════════════════════════





# 启动清理已移除（V8.9）：改为写入时通过 _enforce_size_limit 处理过期条目


# ═══════════════════════════════════════
# CLI 工具（可直接运行 python stock_cache.py）
# ═══════════════════════════════════════
if __name__ == "__main__":
    # V16.4.1: CLI 入口强制 UTF-8 输出（库 import 时不动全局 stdio）
    for _stream in (sys.stdout, sys.stderr):
        if _stream is not None and hasattr(_stream, "reconfigure"):
            try:
                _stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    import argparse

    parser = argparse.ArgumentParser(description="stock_cache CLI 工具")
    parser.add_argument("action", choices=["stats", "clear", "clear-expired", "clear-all"],
                        help="stats=查看统计 / clear=按分类清理 / clear-expired=清过期 / clear-all=清全部")
    parser.add_argument("--category", "-c", default="", help="分类名（用于 clear 命令）")
    parser.add_argument("--pattern", "-p", default="", help="代码过滤（用于 clear 命令）")
    args = parser.parse_args()

    if args.action == "stats":
        print_cache_stats()
    elif args.action == "clear-expired":
        n = clear_expired()
        print(f"已清理 {n} 条过期缓存", flush=True)
    elif args.action == "clear-all":
        clear_all()
        print("已清空全部缓存", flush=True)
    elif args.action == "clear":
        if not args.category:
            print("错误：clear 命令需要 --category 参数", flush=True)
            sys.exit(1)
        n = invalidate_category(args.category, args.pattern)
        print(f"已清理 {n} 条 {args.category} 缓存（pattern={args.pattern or '全部'}）", flush=True)

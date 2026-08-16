#!/usr/bin/env python3
"""tdx_client.py — 通达信共享行情模块。

提供统一的 easy-tdx 数据访问接口，所有适配器函数返回格式与 V3 完全兼容。
当 TDX 服务器不可达时自动回退到原始 HTTP 源（百度K线/腾讯行情）。

版本信息:
    V15.2  2026-07-28 - 8 个 F10 函数 valid_if 强化（用 make_valid_if 替代 r is not None）；tdx_get_quote_full 重构为 ZHB→TDX→HTTP 优先级
    V15.1  2026-07-26 - tdx_get_fund_flow 改名为 em_get_fund_flow（新增别名，保留旧函数）；tdx_get_history_fund_flow 同理
    V14.0  2026-07-22 - 文档同步：docstring 版本信息更新到 V14.0
    V12.6  2026-07-22 - 受益于字段路由简化
    V12.0  2026-07-22 - 移除 easy_tdx（历史）；V15.5 通过 _EasyTdxAdapter 重新集成（首选）
    V10.2  2026-07-16 - F10系列valid_if放宽：bool(r)改为r is not None，避免空dict/list拒写缓存
    V9.5   2026-07-11 - 静默异常日志化（23处 except Exception 添加 _debug_log）
    V9.4   2026-07-11 - VERSION文件单一来源版本号管理
    V9.3.3 2026-07-10 - 代码质量提升：GD上传路径修复、GLM报告Bug修复、死代码清理、sync/async重构、schema统一
    V9.3.2 2026-07-09 - K线假数据防护：健康检查增加K线校验，TdxDecodeError时标记坏主机并强制换IP重连
    V9.3   2026-07-07 - 盘前行情模式：9:30前使用日K线上一交易日数据，避免实时接口返回0导致涨跌幅-100%；行情缓存Key增加交易日期，盘前/盘中数据独立保留
    V9.2   2026-07-05 - 异常处理规范化；重连前关闭旧连接防止泄漏
    V9.1.1 2026-07-04 - 补全 F10 交易日缓存策略；精简 6 个未使用的 F10 函数
    V9.1   2026-07-04 - F10 全覆盖：新增12个F10函数（公司概况/财务/股东/股本/新闻/研报/行业/经营/治理/资本运作/主题/异动）
    V9.0   2026-07-02 - 全量 TDX 服务器探测（53个节点）；F10 公告兜底（filename+start+length）
    V8.6   2026-06-24 - 限流安全加固：请求频率限制(20ms)/重连指数退避/线程锁保护
    V8.5   2026-06-22 - TDX请求最小间隔 + 指数退避重连
    V8.0   2026-06-17 - 初始版本
    V7.5 - Monkey-patch心跳线程/全局调用锁/进程内缓存
"""

from __future__ import annotations

import time
import os
import json
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Tuple, cast

import requests

from stock_common import _safe_float, UA, _request_with_retry, _quick_request, _debug_log
from core.stock_cache import cached, make_valid_if, TTL  # V15.2 强化 + V15.5.7 TTL
from core.config import TDX_MIN_INTERVAL, MAX_RETRY_COUNT, RETRY_DELAY_SECONDS

# V16.2.13: easy_tdx "声称 N 条但首条即解析失败" 警告 = 标的无 K 线的**正常降级提示**
#（8/4 老段已适配器拦截；92 个别新股首次换台仍触发，无法预判）→ 精确过滤该消息，
# 不刷屏且不影响 easy_tdx 其他日志（协议错误仍可见）。
try:
    import logging as _tdx_logging

    class _KlineEmptyFilter(_tdx_logging.Filter):
        def filter(self, record) -> bool:
            _msg = record.getMessage()
            return "声称" not in _msg and "首条即解析失败" not in _msg

    _tdx_logging.getLogger("easy_tdx.commands.security_bars").addFilter(_KlineEmptyFilter())
except Exception:
    pass

# ═══════════════════════════════════════
# V7.5: 全局调用锁
# `_TDX_CLIENT` 是单例，多线程并发读写同一个 socket 会导致协议包错乱卡死。
# 用 RLock 让同一线程可重入。
# V12.0: 移除 easy_tdx 后，MacClient 相关代码已全部删除，仅保留 mootdx 客户端。
# ═══════════════════════════════════════
import threading as _tdx_th

_TDX_AVAILABLE: Optional[bool] = None
_TDX_CLIENT: Optional[Any] = None
_last_request_time: float = 0.0
_TDX_RECONNECT_ATTEMPTS: int = MAX_RETRY_COUNT
_TDX_RECONNECT_DELAY: float = RETRY_DELAY_SECONDS
# V8.5: TDX请求最小间隔（秒），防止过快请求被服务器断开
# 100ms = 约10次/秒，批量运行时更稳定
_TDX_MIN_INTERVAL: float = TDX_MIN_INTERVAL
_TDX_CALL_LOCK = _tdx_th.RLock()


def _tdx_throttle():
    """V8.5: TDX请求节流：确保两次请求间隔 >= _TDX_MIN_INTERVAL

    必须在 _TDX_CALL_LOCK 内调用。
    """
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if _last_request_time > 0 and elapsed < _TDX_MIN_INTERVAL:
        time.sleep(_TDX_MIN_INTERVAL - elapsed)
    _last_request_time = time.time()


# ── V7.5: 进程内缓存 ─────────────────────────────────────────────
# 策略并发阶段只做纯 CPU 计算，不再触发网络 IO。
# key 格式: f"{period}:{code}:{count}"，period: D=日线, W=周线, Q=行情
_TDX_KLINE_CACHE: Dict[str, Tuple[List[str], List[List[str]]]] = {}
# V16.2.12: 标的级 K 线失败记忆 {code: 到期时间戳} —— 北交所老段（8/4 开头）等
# 白名单服务器确认无 K 线的标的，5 分钟内直接返回空，避免每次 6-12s 换台探测
_TDX_KLINE_EMPTY_UNTIL: Dict[str, float] = {}
_TDX_WKLINE_CACHE: Dict[str, Tuple[List[str], List[List[str]]]] = {}
_TDX_QUOTE_CACHE: Dict[str, Dict[str, Any]] = {}


# ═══════════════════════════════════════
# 基础工具
# ═══════════════════════════════════════
def _market_prefix(code: str) -> str:
    # V16.2.2: 北交所含 92 新段（原 92 被 "9" 吸走 → sh 错误）
    if code.startswith(("8", "4", "92")):
        return "bj"
    if code.startswith(("6", "9")):
        return "sh"
    return "sz"


def _market_from_code(code: str) -> int:
    # V16.2.2: 北交所含 92 新段
    if code.startswith(("8", "4", "92")):
        return 2
    if code.startswith(("6", "9")):
        return 1
    return 0


def _index_to_market_code(idx_code: str) -> Tuple[int, str]:
    prefix = idx_code[:2]
    num = idx_code[2:]
    m = 1 if prefix == "sh" else 0
    return (m, num)


# ═══════════════════════════════════════
# 按域名独立限流配置（基于诊断脚本实测）
# ═══════════════════════════════════════
# 腾讯行情 qt.gtimg.cn:      并发10, sleep=0ms → 100% 成功
# 新浪财报 quotes.sina.cn:    并发10, sleep=0ms → 100% 成功
# 同花顺强势 zx.10jqka.com.cn: 并发10, sleep=0ms → 100% 成功
# 东财 datacenter-web.eastmoney.com: 并发3, sleep=100ms → 100% 成功
# ═══════════════════════════════════════
_DOMAIN_LIMITS: Dict[str, Dict[str, Any]] = {
    "qt.gtimg.cn": {"sleep_ms": 0, "semaphore": None},
    "quotes.sina.cn": {"sleep_ms": 0, "semaphore": None},
    "finance.pae.baidu.com": {"sleep_ms": 0, "semaphore": None},
    "zx.10jqka.com.cn": {"sleep_ms": 100, "semaphore": None},
    "datacenter-web.eastmoney.com": {"sleep_ms": 1000, "semaphore": None},
    "reportapi.eastmoney.com": {"sleep_ms": 1000, "semaphore": None},
}
# V16.3 A3: 已移除 push2.eastmoney.com 条目——本表仅服务 tdx_client 内部 _http_get
#（实测唯一调用方 _tencent_batch_fallback 打腾讯域）。东财 push2 属 sc_network 风控面
#（0.4rps/2.5s 共享归一化桶），此前本表 push2=100ms 比 sc_network 严 10 倍松弛，
# 若未来在本表加东财 URL 即成限流旁路（隐藏陷阱）。东财请求一律走 sc_network 入口。
# 每个域名独立的最后请求时间
_DOMAIN_LAST_TIME: Dict[str, float] = {}
# 限流字典的线程锁
_DOMAIN_LAST_TIME_LOCK = _tdx_th.Lock()


def _http_get(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 15,
) -> Optional[requests.Response]:
    """按域名独立限流的 HTTP GET 请求（基于诊断脚本实测参数）。

    V9.0 新增：线程锁保护 _DOMAIN_LAST_TIME。
    """
    import random as _rand

    # 解析域名
    from urllib.parse import urlparse

    parsed = urlparse(url)
    domain = parsed.netloc

    # 获取该域名的限流配置（默认 sleep=100ms 作为兜底）
    limit = _DOMAIN_LIMITS.get(domain, {"sleep_ms": 100})
    sleep_ms = limit["sleep_ms"]

    # 按域名独立 sleep（加线程锁保护）
    wait_ms = 0.0
    with _DOMAIN_LAST_TIME_LOCK:
        last_time = _DOMAIN_LAST_TIME.get(domain, 0.0)
        now = time.time()
        elapsed_ms = (now - last_time) * 1000
        if sleep_ms > 0 and last_time > 0 and elapsed_ms < sleep_ms:
            wait_ms = sleep_ms - elapsed_ms
        _DOMAIN_LAST_TIME[domain] = now + wait_ms / 1000.0
    if wait_ms > 0:
        time.sleep(wait_ms / 1000.0)

    try:
        # V9.3.1: 数据获取全部直连，不使用系统代理（代理仅用于GD上传）
        return requests.get(
            url,
            params=params,
            headers=headers or {"User-Agent": UA},
            timeout=timeout,
            proxies={"http": None, "https": None},
        )
    except Exception as _e:
        _debug_log(f"tdx _tdx_http_get error ({url}): {_e}")
        return None


# ═══════════════════════════════════════
# TDX 连接管理
# ═══════════════════════════════════════

# ── V15.5: easy_tdx 1.20.4 适配层 ──────────────────────────────
# 背景: mootdx 0.11.7 停更（2024-07）+ BESTIP bug 无修复，且 TDX 服务器存在
# "TCP 握手通但返空 body"的静默空表（参考仓库 FAQ V3.4.1 #43）。
# easy_tdx 1.20.4 内置: 服务器健康分引擎(_health) + K线空数据故障转移(_reconnect)
# + 52 候选服务器。本适配层把其 API 包装成 mootdx 兼容接口，下游零改动。
# ───────────────────────────────────────────────────────────────
# V16.2.11 全量核查（2026-08-05，54 台去重：easy_tdx known hosts + 通达信 HQHOST 43 + HFHost 2）：
#   FULL（bars+quotes+finance 三项全通过）仅 5 台 —— 其余 39 台为接入/财务服务器
#   （bars/quotes 恒空仅 finance OK），6 台连接失败。白名单只保留 FULL 服务器。
# 实测 FULL：180.153.18.170（primary）、115.238.56.198、115.238.90.165、
#            218.75.126.9、159.75.55.232（通达信 HFHost 深圳备用站）
# 注：通达信 DSHOST（扩展市场 Port 7727）为基金/港股协议，项目 std 行情(7709)不适用。
# ───────────────────────────────────────────────────────────────
# V16.3.9 移动线路复测（2026-08-11，74 台 = easy_tdx config + v9.6 缓存合并去重）：
#   FULL 6 台 —— 原 5 台全部保持（移动线路可达性无退化）+
#   新增 120.76.152.87（easy_tdx calc_hosts，原 54 台筛查未覆盖）。
#   46 台 PARTIAL（quotes 恒空、bars/fin OK——腾讯云/华为云接入服务器，不入选）、23 台 FAIL。
#   完整数据：docs/network_servers.md §二 + cache/tdx_full_retest_20260811.json
# ───────────────────────────────────────────────────────────────

# 实测可用服务器白名单（2026-08-11 移动线路复测，6 台 FULL）
_EASY_TDX_PRIMARY_HOST = "180.153.18.170"
_EASY_TDX_PREFERRED_HOSTS = [
    "180.153.18.170",
    "115.238.56.198",
    "115.238.90.165",
    "218.75.126.9",
    "159.75.55.232",
    "120.76.152.87",
]

# mootdx frequency → easy_tdx KlineCategory 映射
# mootdx: 0=5min 1=15min 2=30min 3=60min 4=day 5=week 6=month 7/8=1min 9=day 10=quarter 11=year
# easy_tdx: MIN_1=7 MIN_5=0 MIN_15=1 MIN_30=2 MIN_60=3 DAY=4 WEEK=5 MONTH=6 QUARTER=10 YEAR=11
_FREQ_TO_CATEGORY = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 7, 9: 4, 10: 10, 11: 11}

# 沪市指数白名单（000 开头中属于 SH 的指数；399xxx 属 SZ）
_SH_INDEX_CODES = {"000001", "000016", "000300", "000688", "000852", "000905"}


def _easy_market(code: str, is_index: bool = False) -> int:
    """本项目 code → easy_tdx Market（0=深圳, 1=上海, 2=北京）。"""
    if is_index:
        if code.startswith("399"):
            return 0  # 深证成指/创业板指
        return 1  # 沪指数（含 000xxx 白名单）
    # V16.2.2 修复: 北交所（8 开头 83/87/88、4 开头 43/46、92 开头 920xxx）→ 2 北京。
    # 原实现把它们映射到深圳/上海 → 服务器返回空响应（"声称 800 条但首条即解析失败"）。
    if code.startswith(("8", "4", "92")):
        return 2
    # 股票/ETF/B股: 6/5/9 开头为沪市
    return 1 if code.startswith(("6", "5", "9")) else 0


class _EasyTdxAdapter:
    """把 easy_tdx 1.20.4 TdxClient 包装成 mootdx 兼容接口（V15.5）。

    字段对齐:
      - bars: vol 股→手(/100)；新增 datetime 列（date + ' 00:00'，与 mootdx 一致）
      - index_bars: 同 bars（指数）
      - quotes: pre_close → last_close（mootdx 列名）
      - finance: 列名去下划线（jing_lirun → jinglirun 等，mootdx 风格）
    """

    def __init__(self, client: Any) -> None:
        self._client = client
        self.closed = False

    def _df_aligned(self, df) -> Any:
        """补 datetime 列（date → datetime YYYY-MM-DD HH:MM）。"""
        if df is None or df.empty:
            return df
        df = df.copy()
        if "date" in df.columns and "datetime" not in df.columns:
            df["datetime"] = df["date"].astype(str) + " 00:00"
        return df

    def bars(self, symbol: str, frequency: int = 9, start: int = 0, offset: int = 800) -> Any:
        # V16.2.13: 北交所老段（8/4 开头非 92）白名单 5 台服务器确认无 K 线（实测 832000/430047）——
        # 直接返回空，**不调用 easy_tdx**（避免库内"声称 800 条"警告刷屏 + 6-12s 换台浪费）
        if symbol.startswith(("8", "4")) and not symbol.startswith("92"):
            import pandas as _pd

            return _pd.DataFrame()
        market = _easy_market(symbol)
        category = _FREQ_TO_CATEGORY.get(frequency, 4)
        try:
            df = self._client.get_security_bars(market, symbol, category, start, offset)
        except Exception as _e:
            _debug_log(f"easy_tdx bars error ({symbol}): {_e}")
            import pandas as _pd

            return _pd.DataFrame()
        if df is None or df.empty:
            return df
        df = self._df_aligned(df)
        # V15.5: easy_tdx vol 单位=股，mootdx=手 → /100 对齐下游
        if "vol" in df.columns:
            df["vol"] = df["vol"] / 100.0
        return df

    def index_bars(
        self, symbol: str, frequency: int = 9, start: int = 0, offset: int = 800, market: Any = None
    ) -> Any:
        mkt = market if market is not None else _easy_market(symbol, is_index=True)
        category = _FREQ_TO_CATEGORY.get(frequency, 4)
        try:
            df = self._client.get_index_bars(mkt, symbol, category, start, offset)
        except Exception as _e:
            _debug_log(f"easy_tdx index_bars error ({symbol}): {_e}")
            import pandas as _pd

            return _pd.DataFrame()
        return self._df_aligned(df)

    def xdxr(self, symbol: str) -> Any:
        """V16.2.14: 除权除息历史（mootdx 兼容接口）→ easy_tdx get_xdxr_info。

        缺失该方法是分红获取失败根因（tdx_get_dividend_history 调 client.xdxr() 抛
        AttributeError 被误报为"TDX 接口暂不可用"，而 v9.6 mootdx 有 xdxr 所以正常）。
        """
        market = _easy_market(symbol)
        try:
            df = self._client.get_xdxr_info(market, symbol)
        except Exception as _e:
            _debug_log(f"easy_tdx xdxr error ({symbol}): {_e}")
            import pandas as _pd

            return _pd.DataFrame()
        return df

    def quotes(self, symbol: str) -> Any:
        market = _easy_market(symbol)
        try:
            df = self._client.get_security_quotes([(market, symbol)])
        except Exception as _e:
            _debug_log(f"easy_tdx quotes error ({symbol}): {_e}")
            import pandas as _pd

            return _pd.DataFrame()
        if df is None or df.empty:
            return df
        df = df.copy()
        # mootdx 列名 last_close（easy_tdx 叫 pre_close）
        if "pre_close" in df.columns and "last_close" not in df.columns:
            df["last_close"] = df["pre_close"]
        return df

    def finance(self, symbol: str) -> Any:
        market = _easy_market(symbol)
        try:
            df = self._client.get_finance_info(market, symbol)
        except Exception as _e:
            _debug_log(f"easy_tdx finance error ({symbol}): {_e}")
            import pandas as _pd

            return _pd.DataFrame()
        if df is None or df.empty:
            return df
        # V16.2 修复: 保留原始列名（updated_date/gudong_renshu 必须原样），
        # 同时为带下划线列补无下划线别名（jing_lirun → jinglirun），兼容两套下游读取。
        df = df.copy()
        alias = {}
        for c in df.columns:
            key = str(c).strip()
            plain = key.replace("_", "")
            if plain != key:
                alias[plain] = key
        if alias:
            for plain, orig in alias.items():
                if plain not in df.columns:
                    df[plain] = df[orig]
        return df

    def get_finance_info(self, market: Any = None, symbol: str = "") -> Any:
        """V16.2: 兼容调用方直接 client.get_finance_info()（lng/股东 F10 使用）。
        market 参数兼容 mootdx 风格 (market, code) 或 code 单参。
        """
        if not symbol and market is not None and isinstance(market, str):
            symbol = market
            market = None
        if not symbol:
            return None
        return self.finance(symbol)

    def F10C(self, symbol: str) -> list:
        """V16.3 O: F10 分类目录（mootdx 兼容）。

        easy_tdx get_company_info_category（0x02CF 协议）→ [{'name','filename','start','length'}, ...]。
        """
        try:
            market = _easy_market(symbol)
            df = self._client.get_company_info_category(market, symbol)
            if df is None or df.empty:
                return []
            out = []
            for _, row in df.iterrows():
                out.append(
                    {
                        "name": str(row.get("name", "")),
                        "filename": str(row.get("filename", "")),
                        "start": str(row.get("start", 0)),
                        "length": str(row.get("length", 0)),
                    }
                )
            return out
        except Exception as _e:
            _debug_log(f"easy_tdx F10C error ({symbol}): {_e}")
            return []

    def F10(self, symbol: str, name: str) -> str:
        """V16.3 O: F10 指定分类文本（mootdx 兼容）。

        easy_tdx get_company_info_content（0x02D0 协议）按分类 start/length 切片。
        """
        try:
            market = _easy_market(symbol)
            cats = self._client.get_company_info_category(market, symbol)
            if cats is None or cats.empty:
                return ""
            for _, row in cats.iterrows():
                if str(row.get("name", "")) != name:
                    continue
                start = row.get("start", 0)
                length = row.get("length", 0)
                # NaN 防护：pandas 空值 int() 会抛 ValueError，跳过该行
                if start != start or length != length:
                    _debug_log(f"easy_tdx F10 NaN start/length ({symbol} {name})")
                    continue
                content = self._client.get_company_info_content(
                    market,
                    symbol,
                    str(row.get("filename", "")),
                    int(start),
                    int(length),
                )
                return content or ""
        except Exception as _e:
            _debug_log(f"easy_tdx F10 error ({symbol}): {_e}")
        return ""

    def close(self) -> None:
        self.closed = True
        try:
            self._client.close()
        except Exception:
            pass


def _tdx_host_data_complete(client) -> bool:
    """V16.2.9: 验证 TDX 服务器数据完整性（bars + quotes + finance 三项全通过）。

    实测（2026-08-05 全量探测）：部分服务器**只提供财务数据**（150.158.160.2、
    124.71.187.122、111.229.247.189 等 bars/quotes 恒空，仅 finance OK）——
    若 from_best_host 按延迟选中它们，K线/报价全部"声称 800 条但首条即解析失败"。
    因此选台必须验证三项，仅连上无意义。
    注: client 是 easy_tdx TdxClient（原生方法 get_security_bars/get_security_quotes/get_finance_info）。
    """
    try:
        from easy_tdx import Market, KlineCategory

        _df = client.get_security_bars(Market.SH, "600519", KlineCategory.DAY, 0, 5)
        if _df is None or _df.empty:
            return False
        _q = client.get_security_quotes([(Market.SH, "600519")])
        if _q is None or len(_q) == 0:
            return False
        _f = client.get_finance_info(Market.SH, "600519")
        if _f is None or len(_f) == 0:
            return False
        return True
    except Exception as _e:
        _debug_log(f"tdx host data completeness check failed: {_e}")
        return False


def _create_easy_tdx_adapter():
    """创建 easy_tdx 1.20.4 适配器。

    V16.2.8: primary 失败时用 easy_tdx 全量 known hosts（40+ 台）扩大搜索空间。
    V16.2.9: **必须验证数据完整性**（bars+quotes+finance 三项）——实测部分服务器
    只提供财务数据（150.158.160.2/124.71.187.122/111.229.247.189 等），
    from_best_host 按延迟选台会选中它们 → 连接成功但 K线/报价全空。
    V16.2.11: 全量 54 台核查后白名单仅 5 台 FULL（见 _EASY_TDX_PREFERRED_HOSTS 注释），
    探测只遍历白名单（其余 39 台为接入/财务服务器，bars/quotes 恒空）。
    """
    try:
        from easy_tdx.client import TdxClient

        # 1) 首选 primary，验证完整性（180.153.18.170 实测全量 ✓）
        try:
            c = TdxClient(
                host=_EASY_TDX_PRIMARY_HOST, port=7709, auto_reconnect=True, heartbeat_interval=15.0
            )
            c.connect()
            if _tdx_host_data_complete(c):
                _debug_log(f"easy_tdx connected (full-data verified): {_EASY_TDX_PRIMARY_HOST}")
                return _EasyTdxAdapter(c)
            _debug_log(f"easy_tdx primary {_EASY_TDX_PRIMARY_HOST} 数据不全，继续探测")
            try:
                c.close()
            except Exception:
                pass
        except Exception as _e:
            _debug_log(f"easy_tdx primary host failed ({_EASY_TDX_PRIMARY_HOST}): {_e}")

        # 2) 白名单（仅 FULL 服务器，V16.2.11 全量核查）逐台探测：连接 + 三项完整性验证，通过才返回
        #    （不再遍历 easy_tdx 全量 45 台——其中 39 台为接入/财务服务器，bars/quotes 恒空）
        _fallback_hosts = list(_EASY_TDX_PREFERRED_HOSTS)
        if _EASY_TDX_PRIMARY_HOST not in _fallback_hosts:
            _fallback_hosts.insert(0, _EASY_TDX_PRIMARY_HOST)
        for _h in _fallback_hosts:
            try:
                _c = TdxClient(host=_h, port=7709, auto_reconnect=True, heartbeat_interval=15.0)
                _c.connect()
                if _tdx_host_data_complete(_c):
                    _debug_log(f"easy_tdx full-data host found: {_h}")
                    return _EasyTdxAdapter(_c)
                _debug_log(f"easy_tdx host {_h} 数据不全（bars/quotes/finance 未全通过），跳过")
                try:
                    _c.close()
                except Exception:
                    pass
            except Exception as _e:
                _debug_log(f"easy_tdx host {_h} connect failed: {type(_e).__name__} {str(_e)[:60]}")
        # V16.2.9: from_best_host（延迟最优）结果必须验证完整性，不全则视为无可用全量服务器
        try:
            c = TdxClient.from_best_host(hosts=_fallback_hosts, ping_timeout=3.0)
            if _tdx_host_data_complete(c):
                _debug_log("easy_tdx from_best_host connected (full-data verified)")
                return _EasyTdxAdapter(c)
            _debug_log("easy_tdx from_best_host 结果数据不全，放弃 easy_tdx（宁缺毋滥）")
            try:
                c.close()
            except Exception:
                pass
        except Exception as _e:
            _debug_log(f"easy_tdx from_best_host failed: {_e}")
        return None
    except Exception as _e:
        _debug_log(f"easy_tdx adapter create error: {_e}")
        return None


def _check_tdx() -> bool:
    """V12.0: 检测 mootdx 是否可用（缓存结果）。

    V14.2.3: bestip=True 改为 False（避免 mootdx 探速循环卡死）
    """
    global _TDX_AVAILABLE
    if _TDX_AVAILABLE is not None:
        return _TDX_AVAILABLE
    with _TDX_CALL_LOCK:
        if _TDX_AVAILABLE is not None:
            return _TDX_AVAILABLE
        # V15.5: easy_tdx 1.20.4 优先探测（健康分+空数据换台+52服务器）
        # V16.2.9: _create_easy_tdx_adapter 已内置数据完整性验证（bars+quotes+finance），
        # 此处 bars 探测仅作兜底确认（适配器返回即已全量验证过）
        _adapter = _create_easy_tdx_adapter()
        if _adapter is not None:
            try:
                _df = _adapter.bars(symbol='600519', frequency=9, start=0, offset=1)
                _TDX_AVAILABLE = _df is not None and not _df.empty
                if not _TDX_AVAILABLE:
                    _debug_log("tdx _check_tdx: easy_tdx bars 空，回退 mootdx")
                    raise RuntimeError("easy_tdx bars empty")
                _adapter.close()
                return _TDX_AVAILABLE
            except Exception as _e:
                _debug_log(f"tdx _check_tdx easy_tdx error: {_e}")
        # mootdx 备胎
        try:
            from mootdx.quotes import Quotes

            # V14.2.3: bestip=False 跳过 mootdx 探速循环（与 _get_tdx_client 保持一致）
            _c = Quotes.factory(market='std', bestip=False)
            _df = _c.bars(symbol='600519', frequency=9, start=0, offset=1)
            _TDX_AVAILABLE = _df is not None and not _df.empty
            try:
                _c.close()
            except Exception:
                pass
        except Exception as _e:
            _debug_log(f"tdx _check_tdx mootdx error: {_e}")
            _TDX_AVAILABLE = False
    return _TDX_AVAILABLE


def _get_tdx_client() -> Optional[Any]:
    """V12.0: 获取 mootdx StdQuotes 客户端（线程安全，自动重连）。

    mootdx 内部已管理 bestip 选择、心跳线程、自动重连，无需 monkey-patch。
    保留 _TDX_CALL_LOCK 串行化避免协议包错乱，保留 _tdx_throttle 节流。
    """
    with _TDX_CALL_LOCK:
        global _TDX_CLIENT
        for attempt in range(_TDX_RECONNECT_ATTEMPTS):
            if _TDX_CLIENT is not None:
                if not getattr(_TDX_CLIENT, 'closed', True):
                    return _TDX_CLIENT
                try:
                    _TDX_CLIENT.close()
                except Exception as _e:
                    _debug_log(f"tdx close old mootdx client: {_e}")
                _TDX_CLIENT = None
                if attempt < _TDX_RECONNECT_ATTEMPTS - 1:
                    time.sleep(_TDX_RECONNECT_DELAY * (2**attempt))
                continue
            if not _check_tdx():
                return None
            # V15.5: easy_tdx 1.20.4 首选（内置健康分+空数据换台+52服务器）
            _adapter = _create_easy_tdx_adapter()
            if _adapter is not None:
                _TDX_CLIENT = _adapter
                _tdx_health_check(_TDX_CLIENT)
                return _TDX_CLIENT
            # mootdx 备胎（同协议双通道）
            try:
                from mootdx.quotes import Quotes

                # V14.2.1: bestip=True 会触发 mootdx "[-] 选择最快的服务器..." 探速循环，
                # 休市日多个 TCP 节点超时导致卡死数分钟。改为 False 跳过探速，
                # 与 zhb_client.py 保持一致（手动指定服务器）。
                _TDX_CLIENT = Quotes.factory(market='std', bestip=False)
                _tdx_health_check(_TDX_CLIENT)
                return _TDX_CLIENT
            except Exception as _e:
                _debug_log(f"tdx _get_tdx_client mootdx new client error: {_e}")
                _TDX_CLIENT = None
                if attempt < _TDX_RECONNECT_ATTEMPTS - 1:
                    time.sleep(_TDX_RECONNECT_DELAY * (2**attempt))
        return None


def _tdx_health_check(client) -> None:
    """V12.0: mootdx 关键接口健康检查。

    mootdx 内部 bestip 已过滤不可用节点，这里仅做日志记录便于调试，
    K线假数据仍触发换IP（通过抛 RuntimeError 让 _get_tdx_client 重连）。
    """
    try:
        _df = client.bars(symbol='600519', frequency=9, start=0, offset=1)
        if _df is None or _df.empty:
            _debug_log("TDX health check: bars 返回空")
        else:
            _debug_log("TDX health check: bars 正常")
    except Exception as _e:
        _debug_log(f"TDX health check: bars 异常: {_e}")
    try:
        _q = client.quotes(symbol='600519')
        if _q is None or _q.empty:
            _debug_log("TDX health check: quotes 不可用")
        else:
            _debug_log("TDX health check: quotes 正常")
    except Exception as _e:
        _debug_log(f"TDX health check: quotes 异常: {_e}")
    try:
        _f = client.finance(symbol='600519')
        if _f is None or _f.empty:
            _debug_log("TDX health check: finance 不可用")
        else:
            _debug_log("TDX health check: finance 正常")
    except Exception as _e:
        _debug_log(f"TDX health check: finance 异常: {_e}")
    try:
        _x = client.xdxr(symbol='600519')
        if _x is None or _x.empty:
            _debug_log("TDX health check: xdxr 不可用")
        else:
            _debug_log("TDX health check: xdxr 正常")
    except Exception as _e:
        _debug_log(f"TDX health check: xdxr 异常: {_e}")


def _reset_tdx_connections() -> None:
    """V7.5: 重置所有 TDX 缓存引用（加锁）。"""
    with _TDX_CALL_LOCK:
        global _TDX_CLIENT, _TDX_AVAILABLE
        _TDX_CLIENT = None
        _TDX_AVAILABLE = None


# V16.2: 连续空响应计数 —— 批量失败（>阈值）时强制换台，避免 easy_tdx 卡在坏服务器
# 上对每只股票反复 ping_all（52 台 × 5s）导致策略扫描慢 10-60s/股。
# 注意: 调用点可能已持有 _TDX_CALL_LOCK（threading.Lock 不可重入），故直接置空全局、不走 _reset_tdx_connections。
_TDX_EMPTY_STREAK = 0
_TDX_EMPTY_STREAK_THRESHOLD = 5


def _tdx_inc_empty_streak() -> None:
    global _TDX_EMPTY_STREAK, _TDX_CLIENT, _TDX_AVAILABLE
    _TDX_EMPTY_STREAK += 1
    if _TDX_EMPTY_STREAK >= _TDX_EMPTY_STREAK_THRESHOLD:
        _TDX_EMPTY_STREAK = 0
        _TDX_CLIENT = None
        _TDX_AVAILABLE = None
        _debug_log(f"tdx: 连续 {_TDX_EMPTY_STREAK_THRESHOLD} 次 K线空响应，强制重建连接换台")


def _tdx_reset_empty_streak() -> None:
    global _TDX_EMPTY_STREAK
    _TDX_EMPTY_STREAK = 0


def cleanup_tdx() -> None:
    """V7.5: 脚本退出前清理（加锁）。"""
    with _TDX_CALL_LOCK:
        global _TDX_CLIENT, _TDX_AVAILABLE
        try:
            if _TDX_CLIENT is not None:
                _stop_ev = getattr(_TDX_CLIENT, '_stop_event', None)
                if _stop_ev is not None:
                    _stop_ev.set()
                time.sleep(0.05)
        except Exception as _e:
            _debug_log(f"tdx cleanup client heartbeat: {_e}")
        _TDX_CLIENT = None
        _TDX_AVAILABLE = None


# ═══════════════════════════════════════
# Fallback: 原始 V3 HTTP 源
# ═══════════════════════════════════════
def _tencent_quote_full_fallback(code: str, is_pre_market: bool = False) -> Dict[str, Any]:
    """腾讯行情兜底 → dict(含 name, price, change_pct, pe, pb 等)。

    V9.3: 盘前模式（is_pre_market=True）使用上一交易日日K线数据，避免实时接口返回0值
    """
    if is_pre_market:
        return _pre_market_quote_from_kline(code)

    try:
        url = f"https://qt.gtimg.cn/q={_market_prefix(code)}{code}"
        r = _quick_request(url, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return {}
        r.encoding = "gbk"
        vals = r.text.split('"')[1].split("~")
        if len(vals) < _TENCENT_MIN_FIELDS:
            _debug_log(
                f"tdx tencent quote: 字段数 {len(vals)} < {_TENCENT_MIN_FIELDS} "
                f"（腾讯协议可能变更，需核对 _TENCENT_FIELD_INDEX）"
            )
            return {}
        _f = _TENCENT_FIELD_INDEX
        # V16.3 O16: 北交所老号段僵尸数据检测（参考仓库 v3.6.0）——43/83/87 已迁 920，
        # 腾讯对老码返回成交量 0 + 价格定格——丢弃触发后续 fallback
        _vol_v = _safe_float(vals[_f["volume_hand"]])
        _price_v = _safe_float(vals[_f["price"]])
        if code.startswith(("43", "83", "87")) and _vol_v == 0 and _price_v > 0:
            _debug_log(f"tdx tencent quote stale (老号段僵尸数据): {code}")
            return {}
        return {
            "name": vals[_f["name"]],
            "price": _price_v,
            "last_close": _safe_float(vals[_f["last_close"]]),
            "open": _safe_float(vals[_f["open"]]),
            "change_amt": _safe_float(vals[_f["change_amt"]]),
            "change_pct": _safe_float(vals[_f["change_pct"]]),
            "high": _safe_float(vals[_f["high"]]),
            "low": _safe_float(vals[_f["low"]]),
            "amount_wan": _safe_float(vals[_f["amount_wan"]]),
            "turnover_pct": _safe_float(vals[_f["turnover_pct"]]),
            "pe_ttm": _safe_float(vals[_f["pe_ttm"]]),
            "amplitude_pct": _safe_float(vals[_f["amplitude_pct"]]),
            "float_mcap_yi": _safe_float(vals[_f["float_mcap_yi"]]),
            "mcap_yi": _safe_float(vals[_f["mcap_yi"]]),
            "pb": _safe_float(vals[_f["pb"]]),
            "limit_up": _safe_float(vals[_f["limit_up"]]),
            "limit_down_price": _safe_float(vals[_f["limit_down_price"]]),
            "vol_ratio": _safe_float(vals[_f["vol_ratio"]]),
            "pe_static": _safe_float(vals[_f["pe_static"]]),
            "bid1_vol": _safe_float(vals[_f["bid1_vol"]]) * 100,
        }
    except Exception as _e:
        _debug_log(f"tdx _tencent_quote_full_fallback error ({code}): {_e}")
        return {}


def _pre_market_quote_from_kline(code: str) -> Dict[str, Any]:
    """盘前模式：从日K线数据构建行情字典。

    使用上一交易日的收盘价作为当前价，上上个交易日收盘价作为昨收，
    重新计算涨跌幅。
    """
    try:
        keys, rows = tdx_get_security_bars(code, count=3)
        if not keys or len(rows) < 2:
            return {}

        idx_close = keys.index('close') if 'close' in keys else 2
        idx_open = keys.index('open') if 'open' in keys else 1
        idx_high = keys.index('high') if 'high' in keys else 3
        idx_low = keys.index('low') if 'low' in keys else 4
        idx_amount = keys.index('amount') if 'amount' in keys else 6

        # V16.4.1: 实测 tdx_get_security_bars 返回升序(旧→新)——原 rows[0]/rows[1] 取到最旧,
        # 盘前价格/涨跌幅全部基于错误基准计算
        last_row = rows[-1]
        prev_row = rows[-2]

        close = _safe_float(last_row[idx_close], 0)
        prev_close = _safe_float(prev_row[idx_close], 0)
        open_val = _safe_float(last_row[idx_open], 0)
        high = _safe_float(last_row[idx_high], 0)
        low = _safe_float(last_row[idx_low], 0)
        amount_wan = _safe_float(last_row[idx_amount], 0) / 10000

        change_amt = 0.0
        change_pct = 0.0
        if prev_close > 0:
            change_amt = close - prev_close
            change_pct = change_amt / prev_close * 100

        return {
            "name": "",
            "price": close,
            "last_close": prev_close,
            "open": open_val,
            "change_amt": change_amt,
            "change_pct": change_pct,
            "high": high,
            "low": low,
            "amount_wan": amount_wan,
            "turnover_pct": 0.0,
            "pe_ttm": 0.0,
            "amplitude_pct": 0.0,
            "float_mcap_yi": 0.0,
            "mcap_yi": 0.0,
            "pb": 0.0,
            "limit_up": 0.0,
            "limit_down_price": 0.0,
            "vol_ratio": 0.0,
            "pe_static": 0.0,
            "_is_pre_market": True,
        }
    except Exception as _e:
        _debug_log(f"pre-market quote from kline error: {_e}")
        return {}


_TENCENT_BATCH_CACHE: Dict[str, Dict[str, Dict[str, Any]]] = {}
_TENCENT_BATCH_CACHE_DATE: str = ""


# V16.2.4 (B5): 腾讯 qt.gtimg.cn 协议字段位置索引集中管理（腾讯历史上调整过字段顺序，
# 散落硬编码会静默错位 → 数据全错且不报错）
_TENCENT_FIELD_INDEX = {
    "name": 1,
    "price": 3,
    "last_close": 4,
    "open": 5,
    "volume_hand": 6,      # 成交量(手)
    "bid1_vol": 10,
    "change_amt": 31,
    "change_pct": 32,
    "high": 33,
    "low": 34,
    "amount_wan": 37,      # 成交额(万)
    "turnover_pct": 38,    # 换手率(%)
    "pe_ttm": 39,          # 市盈率(TTM)
    "amplitude_pct": 43,
    "float_mcap_yi": 44,   # 流通市值(亿)
    "mcap_yi": 45,         # 总市值(亿)
    "pb": 46,
    "limit_up": 47,
    "limit_down_price": 48,
    "vol_ratio": 49,
    # V16.4.1: 删重复键(原 L880 与 L872 同为 pe_ttm:39, 后者恒生效)
    "pe_dynamic": 52,      # V16.3.3 修正: [52]=动态PE/MRQ（实测 15.47=push2delay f162=fuyao pe_mrq）
    "pe_static": 53,       # V16.3.3 修正: [53]=静态PE（实测 20.48=push2delay f163，原误标 52）
    # V16.3 O20: 破解确认的新字段（field_dict 12.1）
    "high_52w": 67,        # 52周最高价(元)
    "low_52w": 68,         # 52周最低价(元)
    "dividend_yield": 64,  # 股息率(%)（=push2 f126 同源）
    # V16.3.3 (2026-08-10 字典 12.1/12.15.5 实测): 腾讯未知位破解
    "roa": 66,             # ROA 总资产收益率(%) — 已验证（招行 1.12=年化 ROA 精确）
    "main_net_inflow_yi": 75,  # 主力净流入(亿) — 与 push2 f137 同值（-4.55 验证）
    "panel_price": 85,     # 盘口参考价（≈price±0.1，未确认精确语义）
}
_TENCENT_MIN_FIELDS = 69  # V16.3 O22: 覆盖 high_52w=67/low_52w=68/dividend_yield=64 索引（原 53 会 IndexError）  # 协议最小字段数（不足即视为 schema 变化/截断）


def _tencent_batch_fallback(codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """腾讯批量行情 → {code: {name, price, change_pct, ...}}。

    V15.5.10: 分批（每批 60 只）——全市场 7957 只拼单 URL（64KB）会被腾讯拒绝。
    V16.0: 进程内缓存（按交易日维度）— mak 双重拉取 / val→mak 跨脚本复用，
    避免全市场 133 批 ×2 重复拉取（原浪费 60-150s）。
    """
    if not codes:
        return {}
    global _TENCENT_BATCH_CACHE_DATE
    _today = datetime.now().strftime("%Y%m%d")
    if _TENCENT_BATCH_CACHE_DATE != _today:
        _TENCENT_BATCH_CACHE.clear()
        _TENCENT_BATCH_CACHE_DATE = _today
    result: Dict[str, Dict[str, Any]] = {}
    # 收集未命中的代码
    missing = [c for c in codes if c not in _TENCENT_BATCH_CACHE]
    if missing:
        _BATCH = 60  # 腾讯 qt.gtimg.cn 单次 URL 安全上限（经验值 60-80）
        # V16.2: 腾讯批量接入进程级节流（原批间固定 100ms 无协调，多进程时叠加）——用通用协调锁
        try:
            from stock_common.sc_network import _gen_wait_process_interval
        except Exception:
            _gen_wait_process_interval = None
        for _start in range(0, len(missing), _BATCH):
            _chunk = missing[_start : _start + _BATCH]
            prefixed = [f"{_market_prefix(c)}{c}" for c in _chunk]
            try:
                if _gen_wait_process_interval is not None:
                    try:
                        _gen_wait_process_interval()
                    except Exception:
                        pass
                r = _http_get("https://qt.gtimg.cn/q=" + ",".join(prefixed), timeout=15)
                if r is None:
                    continue
                for line in r.text.strip().split(";"):
                    if "=" not in line or '"' not in line:
                        continue
                    key = line.split("=")[0].split("_")[-1]
                    vals = line.split('"')[1].split("~")
                    if len(vals) < _TENCENT_MIN_FIELDS:
                        # V16.2.4 (B5): 长度不足 = 腾讯协议变化/响应截断 → 告警而非静默丢弃
                        _debug_log(
                            f"tdx tencent batch: 字段数 {len(vals)} < {_TENCENT_MIN_FIELDS} "
                            f"（腾讯协议可能变更，需核对 _TENCENT_FIELD_INDEX）"
                        )
                        continue
                    cv = key[2:]
                    # V16.3 O16: 北交所老号段僵尸数据丢弃（43/83/87 已迁 920，成交量 0 定格）
                    # V16.3 O22: float 解析包进 per-code 保护（原在批级 try 外——
                    # 单只坏字段（如 "--"）丢整批 60 只）
                    try:
                        _bvol = float(vals[_TENCENT_FIELD_INDEX["volume_hand"]]) if vals[_TENCENT_FIELD_INDEX["volume_hand"]] else 0
                        _bprice = float(vals[_TENCENT_FIELD_INDEX["price"]]) if vals[_TENCENT_FIELD_INDEX["price"]] else 0
                    except (ValueError, TypeError):
                        continue
                    if cv.startswith(("43", "83", "87")) and _bvol == 0 and _bprice > 0:
                        _debug_log(f"tdx tencent batch stale (老号段僵尸数据): {cv}")
                        continue
                    try:
                        _TENCENT_BATCH_CACHE[cv] = {
                            "name": vals[_TENCENT_FIELD_INDEX["name"]],
                            "price": _bprice,
                            "change_pct": float(vals[_TENCENT_FIELD_INDEX["change_pct"]]) if vals[_TENCENT_FIELD_INDEX["change_pct"]] else 0,
                            "mcap_yi": float(vals[_TENCENT_FIELD_INDEX["mcap_yi"]]) if vals[_TENCENT_FIELD_INDEX["mcap_yi"]] else 0,
                            "pe_ttm": float(vals[_TENCENT_FIELD_INDEX["pe_ttm"]]) if vals[_TENCENT_FIELD_INDEX["pe_ttm"]] else 0,
                            "turnover_pct": float(vals[_TENCENT_FIELD_INDEX["turnover_pct"]]) if vals[_TENCENT_FIELD_INDEX["turnover_pct"]] else 0,
                            "amount_wan": float(vals[_TENCENT_FIELD_INDEX["amount_wan"]]) if vals[_TENCENT_FIELD_INDEX["amount_wan"]] else 0,
                        }
                    except (ValueError, TypeError):
                        pass
            except Exception as _e:
                _debug_log(f"tdx tencent_quote_batch parse error (batch {_start}): {_e}")
            # V16.0: 批间加 100ms 间隔，消除全市场 133 批 0 间隔连打模式
            if _start + _BATCH < len(missing):
                time.sleep(0.1)
    # 组装结果（含缓存命中）
    for c in codes:
        if c in _TENCENT_BATCH_CACHE:
            result[c] = _TENCENT_BATCH_CACHE[c]
    return result


# ═══════════════════════════════════════
# 行情 + K线适配器
# ═══════════════════════════════════════
def tdx_get_security_bars(code: str, count: int = 800) -> Tuple[List[str], List[List[str]]]:
    """获取日 K 线 → (keys, rows)，V7.5: 进程内缓存 + 全局锁。

    V12.0: 底层改用 mootdx StdQuotes.bars(frequency=9)。
    mootdx 返回 DataFrame 列：open/close/high/low/vol/amount/year/month/day/datetime。
    """
    cache_key = f"D:{code}:{count}"
    cached = _TDX_KLINE_CACHE.get(cache_key)
    if cached is not None:
        return cached
    # V14.3 P3: 跨进程磁盘缓存（避免周日首次跑 1000+ 次 TCP 请求）
    try:
        from stock_common.sc_kline_cache import get_cached_kline, set_cached_kline

        disk_cached = get_cached_kline("D", code, count)
        if disk_cached is not None:
            _TDX_KLINE_CACHE[cache_key] = disk_cached
            return disk_cached
    except Exception:
        pass
    with _TDX_CALL_LOCK:
        cached = _TDX_KLINE_CACHE.get(cache_key)
        if cached is not None:
            return cached
        # V14.3 P3: 再次检查磁盘缓存（防止并发首次进入）
        try:
            from stock_common.sc_kline_cache import get_cached_kline, set_cached_kline

            disk_cached = get_cached_kline("D", code, count)
            if disk_cached is not None:
                _TDX_KLINE_CACHE[cache_key] = disk_cached
                return disk_cached
        except Exception:
            pass
        for _retry in range(2):
            # V16.2.12: 标的级失败记忆 —— 该代码 5 分钟内已被确认无 K 线（如北交所老段 8/4 开头
            # 在白名单 5 台服务器全部无数据），直接返回空，避免每只重复 6-12s 换台探测
            if time.time() < _TDX_KLINE_EMPTY_UNTIL.get(code, 0.0):
                return [], []
            client = _get_tdx_client()
            if client is None:
                result = [], []
                _TDX_KLINE_CACHE[cache_key] = result
                return result
            try:
                _tdx_throttle()  # V8.5: TDX请求节流
                # V14.3 P2: 显式 5s 超时包装（仅 Unix 下通过 SIGALRM 启用，Windows 下属性安全隔离）
                import signal

                if hasattr(signal, 'SIGALRM'):

                    def _timeout_handler(signum, frame):
                        raise TimeoutError("tdx_get_security_bars timeout (5s)")

                    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
                    signal.alarm(5)
                try:
                    bars = client.bars(symbol=code, frequency=9, start=0, offset=count)
                finally:
                    if hasattr(signal, 'SIGALRM'):
                        signal.alarm(0)
                        signal.signal(signal.SIGALRM, old_handler)
                if bars is None or bars.empty:
                    # V16.2 修复: easy_tdx 空响应（ret_count 撒谎/服务器截断）。
                    # V16.2.13: easy_tdx 已内部换台（auto_reconnect=True → _find_host_returning_data
                    # 逐台实测白名单 5 台）——空 df = 换台后仍空 = 标的确无（如 92 新股/8/4 老段），
                    # 项目层重建换台是冗余重复，直接记忆 5 分钟返回空。
                    _tdx_inc_empty_streak()
                    _TDX_KLINE_EMPTY_UNTIL[code] = time.time() + 300  # 5 分钟失败记忆
                    result = [], []
                    _TDX_KLINE_CACHE[cache_key] = result
                    return result
                keys = ['time', 'open', 'close', 'high', 'low', 'volume', 'amount']
                rows = []
                for _, row in bars.iterrows():
                    # mootdx 用 'datetime' 列（'YYYY-MM-DD HH:MM'），取前10位日期
                    dt = str(row.get('datetime', ''))
                    rows.append(
                        [
                            dt[:10],
                            str(row.get('open', '')),
                            str(row.get('close', '')),
                            str(row.get('high', '')),
                            str(row.get('low', '')),
                            str(row.get('vol', '')),
                            str(row.get('amount', '')),
                        ]
                    )
                result = (keys, rows)
                _tdx_reset_empty_streak()  # V16.2: K线成功 → 清零连续空响应计数
                _TDX_KLINE_CACHE[cache_key] = result
                # V14.3 P3: 写入跨进程磁盘缓存
                if rows:
                    try:
                        from stock_common.sc_kline_cache import set_cached_kline

                        set_cached_kline("D", code, count, result)
                    except Exception:
                        pass
                return result
            except Exception as _e:
                _err_name = type(_e).__name__
                if 'Decode' in _err_name or '数据不足' in str(_e):
                    _debug_log(f"tdx K线解码失败: {_e}")
                # V16.2.13 修复: 原 _reset_tdx_connections() 在 _TDX_CALL_LOCK 内重入锁
                #（threading.Lock 不可重入）→ 异常路径死锁隐患；直接置空全局
                global _TDX_CLIENT, _TDX_AVAILABLE
                _TDX_CLIENT = None
                _TDX_AVAILABLE = None
                continue
        result = [], []
        _debug_log(f"tdx K线获取失败，返回空数据 ({code})")
        # V16.2 修复: 连接失败结果不写进程级缓存（原写入后同进程永久不重试）。
        # 停牌/新上市等"真无K线"股票由 bars.empty 正常路径处理（写缓存）。
        return result


def tdx_get_latest_bar_with_ma(code: str):
    keys, rows = tdx_get_security_bars(code, count=120)
    if not keys or not rows:
        return {}
    idx_map = {k: i for i, k in enumerate(keys)}
    ci = idx_map.get('close', -1)
    if ci < 0 or len(rows) < 20:
        return {}
    closes = [_safe_float(r[ci]) for r in rows if len(r) > ci]
    closes = [c for c in closes if c > 0]

    def _sma(data, n):
        if len(data) < n:
            return 0
        return sum(data[-n:]) / n

    last = rows[-1]
    result = {}
    for i, k in enumerate(keys):
        if i < len(last):
            result[k] = last[i]
    result['ma5avgprice'] = f"{_sma(closes, 5):.2f}"
    result['ma10avgprice'] = f"{_sma(closes, 10):.2f}"
    result['ma20avgprice'] = f"{_sma(closes, 20):.2f}"
    return result


def _is_before_market_open() -> bool:
    """判断当前是否为盘前时段（9:30之前）。"""
    now = datetime.now()
    return now.hour < 9 or (now.hour == 9 and now.minute < 30)


def _get_trading_date_for_quote() -> str:
    """获取当前行情数据对应的交易日期。

    盘前（<9:30）：使用上一交易日日期
    盘中（>=9:30）：使用今日日期
    """
    if _is_before_market_open():
        from stock_common.stock_calendar import get_last_trading_day

        return get_last_trading_day().strftime("%Y-%m-%d")
    return datetime.now().strftime("%Y-%m-%d")


def tdx_get_quote_full(code: str) -> Dict[str, Any]:
    """获取个股完整行情（V15.1 重构：ZHB → TDX → 腾讯 HTTP）。

    V9.3: 盘前模式（9:30前）使用上一交易日日K线数据，缓存Key包含交易日期
    V12.0: 底层改用 mootdx StdQuotes.quotes(symbol)。注意 mootdx 列名为
           'last_close'（对应原 easy_tdx 的 'pre_close'）。
    V15.1: 优先级调整 ZHB → TDX → 腾讯 HTTP（与 docs/field_dict.md 一致）：
           - 盘前/盘后：ZHB T-1 数据（无网络）
           - 盘中：ZHB 缺失时走 TDX TCP
           - TDX 失败/缺失：降级到腾讯 HTTP
    """
    trading_date = _get_trading_date_for_quote()
    cache_key = f"Q:{code}:{trading_date}"
    cached = _TDX_QUOTE_CACHE.get(cache_key)
    if cached is not None:
        return cached
    result: Dict[str, Any] = {}

    # 优先级 1：ZHB 本地（盘前/盘后/周末/16:30后用 T-1 数据）
    try:
        from stock_common import get_zhb_single_stock_data, is_zhb_data_fresh

        if is_zhb_data_fresh(max_delay_days=1):
            zhb = get_zhb_single_stock_data(code)
            if zhb:
                _safe = lambda k: zhb.get(k, 0)
                if _safe("price"):
                    result["price"] = zhb["price"]
                if _safe("change_pct") is not None:
                    result["change_pct"] = zhb["change_pct"]
                if _safe("open"):
                    result["open"] = zhb["open"]
                if _safe("high"):
                    result["high"] = zhb["high"]
                if _safe("low"):
                    result["low"] = zhb["low"]
                if _safe("last_close"):
                    result["last_close"] = zhb["last_close"]
                # V16.0: ZHB tdxstat2 Col[3] amount 已是万元（zhb_client.py:797），去掉二次 /10000
                # 之前误除导致 ZHB 新鲜时 amount_wan 缩小 1 万倍
                if _safe("amount"):
                    result["amount_wan"] = zhb["amount"]
                # V16.0: 移除 ZHB volume 注入 — Col[24] 曾误映射为 volume(成交量)，
                # 经 9 天连续+联网核实为恒定静态数据(非成交量)，已改名为 unknown_24。
                # 真实成交量只能来自 TDX/腾讯行情（下方 TDX TCP 分支填充）。
                # if _safe("volume"): result["volume_hand"] = zhb["volume"]
                if _safe("pe_ttm"):
                    result["pe_ttm"] = zhb["pe_ttm"]
                if _safe("pb"):
                    result["pb"] = zhb["pb"]
                if _safe("turnover_pct"):
                    result["turnover_pct"] = zhb["turnover_pct"]
                if _safe("change_pct_1d") is not None:
                    result["change_pct_1d"] = zhb["change_pct_1d"]
                if _safe("change_pct_2d") is not None:
                    result["change_pct_2d"] = zhb["change_pct_2d"]
                if _safe("amount_1d"):
                    result["amount_1d"] = zhb["amount_1d"]
                if _safe("amount_2d"):
                    result["amount_2d"] = zhb["amount_2d"]
                if zhb.get("industry"):
                    result["industry"] = zhb["industry"]
    except Exception as _e:
        _debug_log(f"tdx zhb quote fallback error ({code}): {_e}")

    # 优先级 2：TDX TCP（盘中实时补强）
    # V16.2 修复: 盘中/盘后 TDX 实时值**覆盖** ZHB T-1（price/change_pct/open/high/low/amount 等实时字段），
    # 防止 T-1 数据被标记为实时。盘前(_is_before_market_open)仍保留 ZHB。
    _is_rt = not _is_before_market_open()
    with _TDX_CALL_LOCK:
        cached = _TDX_QUOTE_CACHE.get(cache_key)
        if cached is not None:
            return cached
        client = _get_tdx_client()
        if client is not None:
            try:
                _tdx_throttle()  # V8.5: TDX请求节流
                quotes = client.quotes(symbol=code)
                if quotes is not None and not quotes.empty:
                    q = quotes.iloc[0]
                    # mootdx 列名 'last_close' = 昨收
                    pre_close = q.get('last_close', 0)
                    # 实时字段：盘中覆盖 ZHB，盘前仅补缺
                    def _put(key, val, overwrite=True):
                        if val is None:
                            return
                        if overwrite or key not in result or not result.get(key):
                            result[key] = val
                    if q.get('price'):
                        _put('price', q['price'], _is_rt)
                    if pre_close:
                        _put('last_close', pre_close, _is_rt)
                    if q.get('open'):
                        _put('open', q['open'], _is_rt)
                    if q.get('high'):
                        _put('high', q['high'], _is_rt)
                    if q.get('low'):
                        _put('low', q['low'], _is_rt)
                    if q.get('amount'):
                        _put('amount_wan', q['amount'] / 10000.0, _is_rt)
                    # 涨跌幅：以 TDX 现价/昨收为准（盘中有实时昨收），确保覆盖 T-1
                    if pre_close and pre_close > 0 and q.get('price'):
                        _put('change_pct', (q['price'] - pre_close) / pre_close * 100, _is_rt)
                        _put('change_amt', q['price'] - pre_close, _is_rt)
                    for i in range(1, 6):
                        _put(f'bid{i}', q.get(f'bid{i}', 0), _is_rt)
                        _put(f'ask{i}', q.get(f'ask{i}', 0), _is_rt)
            except Exception as _e:
                _debug_log(f"tdx quote supplement error: {_e}")

    # 优先级 3：腾讯 HTTP（最后兜底）
    if not result or "pe_ttm" not in result:
        http_result = _tencent_quote_full_fallback(code, is_pre_market=_is_before_market_open())
        if http_result:
            # 合并：HTTP 仅填充 ZHB/TDX 缺失的字段
            for k, v in http_result.items():
                if k not in result or not result.get(k):
                    result[k] = v

    # V8.9: 兜底仍无 pe_ttm → 返回空字典（让 if q: 保护生效）
    # V16.1.7 修正: 缺 pe_ttm 不应整体置空——TDX 的 price/change_pct 仍有效，
    # 置空会丢掉 TCP 实时价导致链跳到腾讯/东财。pe_ttm 缺失留 0，由上层 ZHB 兜底。
    if result and "pe_ttm" not in result:
        if not any(result.get(k) for k in ("price", "change_pct", "amount_wan", "turnover_pct")):
            result = {}
        else:
            result["pe_ttm"] = 0.0
    _TDX_QUOTE_CACHE[cache_key] = result
    return result


def tdx_get_index_quote(idx_code: str) -> Dict[str, Any]:
    """获取指数行情（TDX 优先，腾讯兜底）。

    V12.0: mootdx 的 index_bars 直接接受指数代码（如 '000001'），
           不再需要 market/code 拆分。
    """
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is not None:
            try:
                _tdx_throttle()  # V8.5: TDX请求节流
                _, code = _index_to_market_code(idx_code)
                bars = client.index_bars(symbol=code, frequency=9, start=0, offset=2)
                if bars is None or bars.empty:
                    # V16.2.7: easy_tdx 指数空响应（ret_count 撒谎）→ 换台重试一次
                    global _TDX_CLIENT, _TDX_AVAILABLE
                    _TDX_CLIENT = None
                    _TDX_AVAILABLE = None
                    _debug_log(f"tdx index_quote 空响应 ({idx_code})，换台重试")
                    client = _get_tdx_client()
                    if client is not None:
                        bars = client.index_bars(symbol=code, frequency=9, start=0, offset=2)
                if bars is not None and not bars.empty and len(bars) >= 2:
                    last_c = float(bars.iloc[-1]['close'])
                    prev_c = float(bars.iloc[-2]['close'])
                    last_o = float(bars.iloc[-1]['open'])
                    chg = (last_c - prev_c) / prev_c * 100 if prev_c > 0 else 0
                    return {
                        "price": round(last_c, 2),
                        "open": round(last_o, 2),
                        "change_pct": round(chg, 2),
                    }
            except Exception as _e:
                _debug_log(f"tdx index_quote error: {_e}")
    try:
        url = f"https://qt.gtimg.cn/q={idx_code}"
        r = _quick_request(url, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return {}
        r.encoding = "gbk"
        v = r.text.split('"')[1].split("~")
        return {
            "price": _safe_float(v[3]),
            "open": _safe_float(v[5]),
            "change_pct": _safe_float(v[32]),
        }
    except Exception as _e:
        _debug_log(f"tdx tdx_get_index_quote error ({idx_code}): {_e}")
        return {}


@cached(category="kline", ttl_seconds=TTL["kline"], trading_day=True, valid_if=make_valid_if())  # V16.1: 8000 根 K 线太贵，24h 磁盘缓存
def tdx_get_historical_high(code: str) -> Optional[float]:
    """历史最高价（800 根日 K 线内）。

    V12.0: mootdx bars offset 上限较高，可一次性拉取 8000 根。
    V16.1: 补 @cached（val/lng 多次调用场景，避免重复 8000 根拉取）。
    """
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None:
            return None
        try:
            bars = client.bars(symbol=code, frequency=9, start=0, offset=8000)
            if bars is None or bars.empty:
                return None
            values = [float(v) for v in bars['high'].tolist() if float(v) > 0]
            return max(values) if values else None
        except Exception as _e:
            _debug_log(f"tdx tdx_get_historical_high error ({code}): {_e}")
            return None


def tdx_get_index_bars(idx_code: str, count: int = 250):
    """V12.0: mootdx index_bars 直接接受指数代码。"""
    for _retry in range(2):
        with _TDX_CALL_LOCK:
            client = _get_tdx_client()
            if client is None:
                return [], []
            try:
                m, code = _index_to_market_code(idx_code)
                bars = client.index_bars(symbol=code, market=m, frequency=9, start=0, offset=count)
                if bars is None or bars.empty:
                    # V16.2.7: easy_tdx 指数空响应（服务器不提供该指数/ret_count 撒谎）→ 换台重试一次
                    if _retry == 0:
                        global _TDX_CLIENT, _TDX_AVAILABLE
                        _TDX_CLIENT = None
                        _TDX_AVAILABLE = None
                        _debug_log(f"tdx index_bars 空响应 ({idx_code})，换台重试")
                        continue
                    return [], []
                keys = ['time', 'open', 'close', 'high', 'low', 'volume', 'amount']
                rows = []
                for _, row in bars.iterrows():
                    dt = str(row.get('datetime', ''))
                    rows.append(
                        [
                            dt[:10],
                            str(row.get('open', '')),
                            str(row.get('close', '')),
                            str(row.get('high', '')),
                            str(row.get('low', '')),
                            str(row.get('vol', '')),
                            str(row.get('amount', '')),
                        ]
                    )
                return keys, rows
            except Exception as _e:
                _err_name = type(_e).__name__
                if 'Decode' in _err_name or '数据不足' in str(_e):
                    _debug_log(f"tdx 指数K线解码失败: {_e}")
                _reset_tdx_connections()
                continue
    return [], []


def tdx_get_weekly_bars(code: str, count: int = 100):
    """V12.0: mootdx bars(frequency=5) 返回周K线。

    V14.3 P3: 接入跨进程磁盘缓存。
    """
    cache_key = f"W:{code}:{count}"
    cached = _TDX_WKLINE_CACHE.get(cache_key)
    if cached is not None:
        return cached
    # V14.3 P3: 跨进程磁盘缓存
    try:
        from stock_common.sc_kline_cache import get_cached_kline, set_cached_kline

        disk_cached = get_cached_kline("W", code, count)
        if disk_cached is not None:
            _TDX_WKLINE_CACHE[cache_key] = disk_cached
            return disk_cached
    except Exception:
        pass
    with _TDX_CALL_LOCK:
        cached = _TDX_WKLINE_CACHE.get(cache_key)
        if cached is not None:
            return cached
        client = _get_tdx_client()
        if client is None:
            result: Tuple[List[Any], List[Any]] = ([], [])
            _TDX_WKLINE_CACHE[cache_key] = result
            return result
        try:
            # V14.3 P2: 显式 5s 超时包装（仅 Unix 下通过 SIGALRM 启用，Windows 下属性安全隔离）
            import signal

            if hasattr(signal, 'SIGALRM'):

                def _timeout_handler(signum, frame):
                    raise TimeoutError("tdx_get_weekly_bars timeout (5s)")

                old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
                signal.alarm(5)
            try:
                bars = client.bars(symbol=code, frequency=5, start=0, offset=count)
            finally:
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
            if bars is None or bars.empty:
                result = ([], [])
                _TDX_WKLINE_CACHE[cache_key] = result
                return result
            keys = ['time', 'open', 'close', 'high', 'low', 'volume', 'amount']
            rows = []
            for _, row in bars.iterrows():
                dt = str(row.get('datetime', ''))
                rows.append(
                    [
                        dt[:10],
                        str(row.get('open', '')),
                        str(row.get('close', '')),
                        str(row.get('high', '')),
                        str(row.get('low', '')),
                        str(row.get('vol', '')),
                        str(row.get('amount', '')),
                    ]
                )
            result = (keys, rows)
            _TDX_WKLINE_CACHE[cache_key] = result
            # V14.3 P3: 写入跨进程磁盘缓存
            if rows:
                try:
                    from stock_common.sc_kline_cache import set_cached_kline

                    set_cached_kline("W", code, count, result)
                except Exception:
                    pass
            return result
        except Exception as _e:
            if 'Decode' in type(_e).__name__ or '数据不足' in str(_e):
                _debug_log(f"tdx 周K线解码失败: {_e}")
            result = ([], [])
            # V16.2 修复: 失败结果不写进程级缓存（与日线一致，避免永久负缓存）
            return result


# ═══════════════════════════════════════
# 资金流适配器
# ═══════════════════════════════════════
@cached(
    category="f10_fund_flow", trading_day=True, valid_if=make_valid_if()
)  # V15.2: 拒绝空 dict/全 0
def tdx_get_fund_flow(code: str):
    # V12.0: 委托到东财 HTTP 接口（原 TDX get_fund_flow 已废弃）
    try:
        from stock_common.sc_datasource import get_em_fund_flow

        return get_em_fund_flow(code)
    except Exception as _e:
        _debug_log(f"tdx tdx_get_fund_flow error ({code}): {_e}")
        return None  # V15.2: 失败返回 None（不再返回 {}，避免 valid_if 误判）


@cached(
    category="f10_fund_flow", trading_day=True, valid_if=make_valid_if()
)  # V15.2: 拒绝空 dict/全 0
def tdx_get_history_fund_flow(code: str, days: int = 120):
    # V12.0: 委托到东财 HTTP 接口（原 TDX get_history_fund_flow 已废弃）
    try:
        from stock_common.sc_datasource import get_em_history_fund_flow

        return get_em_history_fund_flow(code, days)
    except Exception as _e:
        _debug_log(f"tdx tdx_get_history_fund_flow error ({code}): {_e}")
        return None  # V15.2: 失败返回 None（不再返回 []，避免 valid_if 误判）


# ═══════════════════════════════════════
# 除权除息 + 公告适配器
# ═══════════════════════════════════════
@cached(
    category="financial", ttl_seconds=TTL["financial"]
)  # V15.5.7: val strategy_10 300 次逐股 TDX 去重
def tdx_get_finance_info(code: str) -> Optional[Dict[str, Any]]:
    """
    V13.0: 提取完整的 GetFinanceInfo (0x0010) 二进制解析结果，返回包含 37 个字段的核心财务数据字典。
    关键字段：
    - updated_date (财报披露日，可用于事件驱动 TTL)
    - zongguben (总股本), liutongguben (流通股本)
    - jinglirun (净利润), zhuyingshouru (主营收入)
    - jingzichan (净资产), zongzichan (总资产)
    - jingyingxianjinliu (经营现金流)
    """
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None:
            return None
        try:
            info = client.finance(symbol=code)
            if info is None or info.empty:
                return None
            # 将 DataFrame 首行转换为纯净的 dict
            # mootdx 返回的列包含了所有核心财务指标，并把 np.nan 转换为 None，方便后续处理
            import math

            row = info.iloc[0].to_dict()
            clean_row = {}
            for k, v in row.items():
                if isinstance(v, float) and math.isnan(v):
                    clean_row[k] = None
                else:
                    clean_row[k] = v
            return clean_row
        except Exception as _e:
            _debug_log(f"tdx tdx_get_finance_info error ({code}): {_e}")
            return None


@cached(category="dividend", ttl_seconds=86400, cross_verify=True)  # V16.0: S13 高股息 100 次逐股 xdxr 无缓存 → 补缓存
def tdx_get_dividend_history(code: str):
    """V12.0: mootdx xdxr 列为 year/month/day（无 'date' 列），组合成日期字符串。
    V16.2.3: 连接失败返回 None（与"真无分红"[] 区分，报告不再误报"一毛不拔"）。
    V16.2.14: easy_tdx xdxr 用 'date' 列（YYYY-MM-DD HH:MM:SS），mootdx 用 year/month/day —— 双格式兼容。"""
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None:
            return None
        try:
            df = client.xdxr(symbol=code)
            if df is None or df.empty:
                return []
            rows = []
            for _, row in df.iterrows():
                cat = int(row.get('category', 0) or 0)
                if cat != 1:
                    continue
                fh = _safe_float(row.get('fenhong', 0))
                szg = _safe_float(row.get('songzhuangu', 0))
                pg = _safe_float(row.get('peigu', 0))
                # easy_tdx: 'date' 列（'YYYY-MM-DD HH:MM:SS'）→ 取前 10 位
                date_str = str(row.get('date', '') or '').strip()[:10]
                if not date_str or date_str == 'NaT':
                    # mootdx: year/month/day 组合
                    y = int(row.get('year', 0) or 0)
                    m = int(row.get('month', 0) or 0)
                    d = int(row.get('day', 0) or 0)
                    date_str = f"{y:04d}-{m:02d}-{d:02d}" if y > 0 else ''
                rows.append(
                    {
                        "date": date_str,
                        "bonus_rmb": fh,
                        "bonus_ratio": pg,
                        "transfer_ratio": szg,
                    }
                )
            rows.sort(key=lambda x: x["date"], reverse=True)
            return rows
        except Exception as _e:
            _debug_log(f"tdx tdx_get_dividend_history error ({code}): {_e}")
            return None


def tdx_get_eps_from_reports(code: str):
    try:
        api = "https://reportapi.eastmoney.com/report/list"
        for page in range(1, 3):
            params = {
                "pageSize": "50",
                "industry": "*",
                "rating": "*",
                "beginTime": "2000-01-01",
                "endTime": "2030-01-01",
                "pageNo": str(page),
                "code": code,
                "qType": "0",
            }
            r = _quick_request(api, params=params, timeout=30)
            if r is None:
                break
            rows = r.json().get("data") or []
            if not rows:
                break
            this_year = next_year = None
            for r2 in rows:
                ty = r2.get("predictThisYearEps")
                ny = r2.get("predictNextYearEps")
                if ty is not None:
                    this_year = float(ty)
                if ny is not None:
                    next_year = float(ny)
                if this_year is not None:
                    return {
                        "eps_cur": this_year,
                        "eps_next": next_year,
                        "analyst_count": 1,
                        "source": "东财研报",
                    }
        return None
    except Exception as _e:
        _debug_log(f"tdx tdx_get_eps_from_reports error ({code}): {_e}")
        return None


@cached(
    category="f10_announcements", trading_day=True, valid_if=make_valid_if()
)  # V15.2: 拒绝空 dict/全 0
def tdx_get_latest_announcements(code: str, days: int = 7):
    """从 TDX F10 公司公告中获取最新公告列表。

    V12.0: mootdx 用 F10C(symbol) 返回 list[OrderedDict] 取分类元数据，
           F10(symbol, name) 直接返回完整文本（不需要 filename/start/length）。

    Args:
        code: 股票代码
        days: 仅返回最近 N 天的公告，None=不限制

    Returns:
        list[dict]: 公告列表，每项含 title/date/category
    """
    with _TDX_CALL_LOCK:
        client = _get_tdx_client()
        if client is None:
            return []
        try:
            cats = client.F10C(symbol=code)
            if not cats:
                return []
            # 找到「公司公告」分类
            ann_cat = next((c for c in cats if c.get('name') == '公司公告'), None)
            if ann_cat is None:
                # mootdx 的 F10 数据源不含「公司公告」分类（easy_tdx 特有）
                # 该函数返回空，调用方应改用巨潮资讯 HTTP 接口（sc_datasource 已有）
                _debug_log(f"tdx tdx_get_latest_announcements: mootdx 无「公司公告」分类 ({code})")
                return []
            _tdx_throttle()
            content = client.F10(symbol=code, name='公司公告')
            # mootdx 在 name 不存在时返回 dict（所有分类），存在时返回 str
            if not isinstance(content, str) or not content:
                return []
            # 解析 F10 公告表格格式（GBK 文本，┌┬┐├┼┤└┴┘ 等分隔符）
            import re as _re

            lines = content.split('\n')
            anns = []
            current_date = ''
            from datetime import datetime, timedelta

            cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d') if days else ''
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 匹配日期: YYYY-MM-DD HH:MM 格式
                m = _re.match(r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})', line)
                if m:
                    current_date = m.group(1)
                    # 按日期过滤
                    if cutoff and current_date < cutoff:
                        continue
                    # 提取标题（去掉日期时间后的剩余内容）
                    title = line[m.end() :].strip()
                    # 去掉左侧表格竖线分隔符
                    title = title.lstrip('│').strip()
                    # 去掉右侧表格竖线
                    title = title.rstrip('│').strip()
                    if title and len(title) > 3:
                        anns.append(
                            {"title": title[:120], "date": current_date, "category": "公司公告"}
                        )
                elif current_date and not cutoff or (cutoff and current_date >= cutoff):
                    # 续行（上一行的公告标题可能换行）
                    if line.startswith('│') or '│' in line:
                        # 跳过纯表格装饰线
                        if _re.match(r'^[┌┬┐├┼┤└┴┘─│\s]+$', line):
                            continue
                        # 提取标题内容
                        parts = line.split('│')
                        for p in parts:
                            p = p.strip()
                            if p and len(p) > 3 and not _re.match(r'^[\d:\-\s]+$', p):
                                anns.append(
                                    {"title": p[:120], "date": current_date, "category": "公司公告"}
                                )
                                break
            return anns[:10]
        except Exception as _e:
            _debug_log(f"tdx tdx_get_latest_announcements error ({code}): {_e}")
            return []


# ═══════════════════════════════════════
# F10 分类数据获取（V9.0 新增）
# ═══════════════════════════════════════


def _f10_get_content(code: str, category_name: str) -> str:
    """获取 F10 指定分类的原始文本内容。

    V12.0: mootdx 的 F10(symbol, name) 直接返回完整文本，
           F10C(symbol) 仅用于校验分类是否存在。

    Args:
        code: 股票代码
        category_name: 分类名称（如 '最新提示'、'公司报道'）

    Returns:
        str: 原始文本内容，失败返回空字符串
    """
    client = _get_tdx_client()
    if client is None:
        return ''
    try:
        # V16.2: F10 系列调用纳入 _TDX_CALL_LOCK（原 F10C 在锁外，多线程并发穿破节流）
        with _TDX_CALL_LOCK:
            # 先用 F10C 校验分类存在（避免直接 F10 拉取空分类）
            cats = client.F10C(symbol=code)
            if not cats or not any(c.get('name') == category_name for c in cats):
                return ''
            _tdx_throttle()
            content = client.F10(symbol=code, name=category_name)
        # mootdx 在 name 不存在时返回 dict（所有分类），存在时返回 str
        if not isinstance(content, str):
            return ''
        return content or ''
    except Exception as _e:
        _debug_log(f"tdx _f10_get_content error ({code}): {_e}")
        return ''


@cached(
    category="f10_reminders", trading_day=True, valid_if=make_valid_if()
)  # V15.2: 拒绝空 dict/全 0
def tdx_get_latest_reminders(code: str) -> dict:
    """从 TDX F10「最新提示」分类获取综合信息（8 个子栏目一次拿全）。

    替代 3 个 HTTP 接口：
    - get_eastmoney_stock_news（最新报道）
    - get_block_trade（大宗交易）
    - get_margin_trading（融资融券）

    Returns:
        dict: {
            "latest_indicators": {eps, net_asset, roe, ...},
            "interaction_qa": [{date, question, answer}, ...],
            "latest_announcements": [{date, title, summary, url}, ...],
            "latest_news": [{date, title, summary, url}, ...],
            "abnormal_movements": [...],
            "block_trades": [{date, price, volume, amount, buyer, seller}, ...],
            "margin_trading": [{date, finance_balance, finance_buy, ...}, ...],
            "risk_warnings": {...}
        }
    """
    from stock_common.f10_parser import (
        split_sections,
        parse_table,
        parse_paragraph_blocks,
        parse_key_value_table,
        extract_field,
    )
    import re as _re

    with _TDX_CALL_LOCK:
        content = _f10_get_content(code, '最新提示')
        if not content:
            return {}

        sections = split_sections(content)
        result: dict = {}

        # 1. 最新提示子栏目 — 提取关键指标
        s1 = sections.get('最新提示', '')
        if s1:
            indicators: dict = {}

            def _extract_indicator(text: str, label: str) -> Optional[float]:
                """从表格行提取第一个有效数值（跳过 ---）。"""
                m = _re.search(label + r'\s*│(.+)', text)
                if m:
                    # 用 │ 分割值列，找第一个有效数字
                    vals = [v.strip() for v in m.group(1).split('│')]
                    for v in vals:
                        if v and v != '---':
                            return _safe_float(v)
                return None

            indicators['eps'] = _extract_indicator(s1, r'每股收益\(元\)')
            indicators['net_asset'] = _extract_indicator(s1, r'每股净资产\(元\)')
            indicators['roe'] = _extract_indicator(s1, r'加权净资产收益率\(%?\)')
            indicators['total_capital'] = _extract_indicator(s1, r'总股本\(万股\)')
            indicators['float_capital'] = _extract_indicator(s1, r'实际流通A股\(万股\)')
            # 提取最新指标变动原因
            m = _re.search(r'最新指标变动原因\s*│\s*(.+?)│', s1)
            if m:
                indicators['change_reason'] = m.group(1).strip()
            # 提取股东人数
            m = _re.search(r'股东人数:截止([\d-]+),公司股东户数([\d]+),([减少增加]+)([\d.]+)%', s1)
            if m:
                indicators['holder_count'] = {
                    'date': m.group(1),
                    'count': int(m.group(2)),
                    'change': m.group(3),
                    'change_pct': _safe_float(m.group(4)),
                }
            # 提取财务同比
            m = _re.search(
                r'财务同比:([\d-]+)\s*营业收入\(万元\):([\d.]+)\s*同比增\(%\):([\d.-]+)\s*净利润\(万元\):([\d.]+)\s*同比增\(%\):([\d.-]+)',
                s1,
            )
            if m:
                indicators['financial_yoy'] = {
                    'date': m.group(1),
                    'revenue': _safe_float(m.group(2)),
                    'revenue_yoy': _safe_float(m.group(3)),
                    'net_profit': _safe_float(m.group(4)),
                    'net_profit_yoy': _safe_float(m.group(5)),
                }
            result['latest_indicators'] = indicators

        # 2. 互动问答
        s2 = sections.get('互动问答', '')
        if s2 and '暂无数据' not in s2:
            qa_list: list = []
            lines = s2.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i].strip().lstrip('│').strip()
                # 匹配日期行（MM-DD 或 YYYY-MM-DD）
                m = _re.match(r'(\d{2}-\d{2}|\d{4}-\d{2}-\d{2})', line)
                if m and '问：' in line:
                    date = m.group(1)
                    # 提取问题
                    question = ''
                    qm = _re.search(r'问：(.+)', line)
                    if qm:
                        question = qm.group(1).strip().rstrip('│').strip()
                    # 向后搜索答案
                    answer = ''
                    for j in range(i + 1, min(i + 15, len(lines))):
                        ans_line = lines[j].strip().lstrip('│').strip()
                        if ans_line.startswith('答：'):
                            answer = ans_line[2:].strip().rstrip('│').strip()
                            break
                        elif _re.match(r'\d{2}-\d{2}', ans_line):
                            break
                    if question:
                        qa_list.append(
                            {'date': date, 'question': question[:200], 'answer': answer[:500]}
                        )
                    i = j + 1 if answer else i + 1
                else:
                    i += 1
            result['interaction_qa'] = qa_list[:5]
        else:
            result['interaction_qa'] = []

        # 3. 最新公告
        s3 = sections.get('最新公告', '')
        if s3 and '暂无数据' not in s3:
            result['latest_announcements'] = parse_paragraph_blocks(s3)[:5]
        else:
            result['latest_announcements'] = []

        # 4. 最新报道
        s4 = sections.get('最新报道', '')
        if s4 and '暂无数据' not in s4:
            result['latest_news'] = parse_paragraph_blocks(s4)[:5]
        else:
            result['latest_news'] = []

        # 5. 最新异动
        s5 = sections.get('最新异动', '')
        result['abnormal_movements'] = (
            [] if '暂无数据' in s5 else [s5.strip()[:200]] if s5.strip() else []
        )

        # 6. 大宗交易
        s6 = sections.get('大宗交易', '')
        if s6 and '暂无数据' not in s6:
            rows = parse_table(s6)
            block_trades: list = []
            for r in rows:
                block_trades.append(
                    {
                        'date': r.get('交易日期', ''),
                        'price': _safe_float(r.get('成交价格(元)', 0)),
                        'volume': _safe_float(r.get('成交数量(万股)', 0)),
                        'amount': _safe_float(r.get('成交金额(万元)', 0)),
                        'buyer': r.get('买方营业部', ''),
                        'seller': r.get('卖方营业部', ''),
                    }
                )
            result['block_trades'] = block_trades
        else:
            result['block_trades'] = []

        # 7. 融资融券
        s7 = sections.get('融资融券', '')
        if s7 and '暂无数据' not in s7:
            rows = parse_table(s7)
            margin_data: list = []
            for r in rows:
                margin_data.append(
                    {
                        'date': r.get('交易日期', ''),
                        'finance_balance': _safe_float(r.get('融资余额(万元)', 0)),
                        'finance_buy': _safe_float(r.get('融资买入额(万元)', 0)),
                        'securities_balance': _safe_float(r.get('融券余额(万元)', 0)),
                        'securities_sell': _safe_float(r.get('融券卖出量(万股)', 0)),
                        'total_balance': _safe_float(r.get('融资融券余额(万元)', 0)),
                    }
                )
            result['margin_trading'] = margin_data
        else:
            result['margin_trading'] = []

        # 8. 风险提示
        s8 = sections.get('风险提示', '')
        risk: dict = {}
        if s8:
            # 违规稽查 — 检查是否有实际数据（非"暂无数据"）
            if '违规稽查' in s8:
                vi_idx = s8.find('违规稽查')
                # 取违规稽查到下一个子标题之间的文本
                next_sub = s8.find('【', vi_idx + 4)
                violation_text = s8[vi_idx:next_sub] if next_sub > 0 else s8[vi_idx:]
                if '暂无数据' not in violation_text:
                    risk['violation'] = parse_key_value_table(violation_text[:800])
                else:
                    risk['violation'] = {}
            # 交易所问询
            if '交易所问询' in s8:
                inquiry_text = s8[s8.find('交易所问询') :]
                next_sub = s8.find('【', s8.find('交易所问询') + 4)
                inquiry_text = (
                    inquiry_text[: next_sub - s8.find('交易所问询')]
                    if next_sub > 0
                    else inquiry_text
                )
                risk['inquiry'] = '暂无数据' not in inquiry_text
            # 交易所监管
            if '交易所监管' in s8:
                sup_text = s8[s8.find('交易所监管') :]
                next_sub = s8.find('【', s8.find('交易所监管') + 4)
                sup_text = (
                    sup_text[: next_sub - s8.find('交易所监管')] if next_sub > 0 else sup_text
                )
                risk['supervision'] = '暂无数据' not in sup_text
            # 特别处理
            if '特别处理' in s8:
                st_text = s8[s8.find('特别处理') :]
                risk['special_treatment'] = '暂无数据' not in st_text[:100]
        result['risk_warnings'] = risk

        return result


@cached(
    category="f10_financial", valid_if=make_valid_if(), cross_verify=True, trading_day=True
)  # V15.2: 强化 valid_if
def tdx_get_financial_analysis(code: str) -> dict:
    """从 TDX F10「财务分析」分类获取综合财务信息（10 个子栏目一次拿全）。

    替代 3 个新浪 HTTP 接口：
    - get_sina_financial_report（利润表 lrb）
    - get_sina_balance_sheet（资产负债表 fzb）
    - get_gross_margin_and_roe（毛利率+ROE）

    Returns:
        dict: {
            "main_indicators": [{period, 审计意见, 归母净利(未调整:万), ...}, ...],
            "solvency": [{period, 流动比率, 速动比率, ...}, ...],
            "operation": [{period, 应收账款周转率, ...}, ...],
            "profitability": [{period, 净资产收益率, 销售毛利率, ...}, ...],
            "growth": [{period, 营业收入增长率, ...}, ...],
            "indicator_changes": [{period, items: [{subject, reason, ...}]}],
            "balance_sheet": [{period, 货币资金, 存货, ...}, ...],
            "income_statement": [...],
            "cash_flow": [...],
            "qoq_analysis": [...]
        }
    """
    from stock_common.f10_parser import (
        split_sections,
        find_subsection,
        parse_tables,
        parse_table,
        transpose_table,
        merge_continuation_lines,
    )
    import re as _re

    with _TDX_CALL_LOCK:
        content = _f10_get_content(code, '财务分析')
        if not content:
            return {}

        sections = split_sections(content)
        result: dict = {}

        # 1. 主要财务指标（可能含多个表格：年报对比 + 近5期）
        # 银行股嵌套结构：find_subsection 在 '财务指标' 顶层 section 内查找 【主要财务指标】
        s1 = find_subsection(sections, '主要财务指标')
        if s1:
            tables = parse_tables(s1)
            merged: dict = {}
            for tbl in tables:
                if not tbl:
                    continue
                # 找 key_col（第一个列名，通常是"财务指标"）
                key_col = next(iter(tbl[0].keys())) if tbl[0] else ''
                transposed = transpose_table(tbl, key_col)
                for entry in transposed:
                    period = entry.get('period', '')
                    if period and period not in merged:
                        merged[period] = entry
            result['main_indicators'] = list(merged.values())
        else:
            result['main_indicators'] = []

        # 2-5. 偿债/营运/盈利/成长能力指标
        # 银行股的"成长能力指标"叫"发展能力指标"，通过 aliases 兼容
        section_specs = [
            ('solvency', '偿债能力指标', None),
            ('operation', '营运能力指标', None),
            ('profitability', '盈利能力指标', None),
            ('growth', '成长能力指标', ['发展能力指标']),  # 银行股别名
        ]
        for result_key, section_name, aliases in section_specs:
            s = find_subsection(sections, section_name, aliases)
            if s:
                tables = parse_tables(s)
                merged: dict = {}
                for tbl in tables:
                    if not tbl:
                        continue
                    actual_key = next(iter(tbl[0].keys())) if tbl[0] else section_name
                    transposed = transpose_table(tbl, actual_key)
                    for entry in transposed:
                        period = entry.get('period', '')
                        if period and period not in merged:
                            merged[period] = entry
                result[result_key] = list(merged.values())
            else:
                result[result_key] = []

        # 6. 指标变动说明（多块表格，每块前有"截止日期:YYYY-MM-DD"）
        # 银行股的指标变动叫"异动科目"，find_subsection 会通过顶层 '异动科目' section 查找
        s6 = find_subsection(sections, '指标变动说明', ['异动科目'])
        if s6 and '暂无数据' not in s6:
            # 按"截止日期:YYYY-MM-DD"分割
            parts = _re.split(r'截止日期[:：]\s*(\d{4}-\d{2}-\d{2})', s6)
            changes: list = []
            # parts[0] = preamble, then alternating (date, content)
            for i in range(1, len(parts), 2):
                period = parts[i]
                block_text = parts[i + 1] if i + 1 < len(parts) else ''
                # 预处理：合并跨行文本单元格（前2列为文本）
                merged_text = merge_continuation_lines(block_text, num_text_cols=2)
                rows = parse_table(merged_text)
                items: list = []
                for r in rows:
                    items.append(
                        {
                            'subject': r.get('变动科目', '').strip(),
                            'reason': r.get('变动原因', '').strip(),
                            'current_value': _safe_float(r.get('本期数值(万)', 0) or 0),
                            'previous_value': _safe_float(r.get('上期/期初数(万)', 0) or 0),
                            'change_pct': _safe_float(r.get('变动幅度(%)', 0) or 0),
                        }
                    )
                if items:
                    changes.append({'period': period, 'items': items})
            result['indicator_changes'] = changes
        else:
            result['indicator_changes'] = []

        # 7. 资产负债表摘要（银行股嵌套在 '报表摘要' 顶层 section 下）
        s7 = find_subsection(sections, '资产负债表摘要')
        if s7:
            tables = parse_tables(s7)
            merged: dict = {}
            for tbl in tables:
                if not tbl:
                    continue
                actual_key = next(iter(tbl[0].keys())) if tbl[0] else '资产负债指标(万元)'
                transposed = transpose_table(tbl, actual_key)
                for entry in transposed:
                    period = entry.get('period', '')
                    if period and period not in merged:
                        merged[period] = entry
            result['balance_sheet'] = list(merged.values())
        else:
            result['balance_sheet'] = []

        # 8-10. 利润表摘要 / 现金流量表摘要 / 环比分析（部分股票可能无数据）
        for result_key, section_name in [
            ('income_statement', '利润表摘要'),
            ('cash_flow', '现金流量表摘要'),
            ('qoq_analysis', '环比分析'),
        ]:
            s = find_subsection(sections, section_name)
            if s and '暂无数据' not in s:
                tables = parse_tables(s)
                merged: dict = {}
                for tbl in tables:
                    if not tbl:
                        continue
                    actual_key = next(iter(tbl[0].keys())) if tbl[0] else ''
                    transposed = transpose_table(tbl, actual_key)
                    for entry in transposed:
                        period = entry.get('period', '')
                        if period and period not in merged:
                            merged[period] = entry
                result[result_key] = list(merged.values())
            else:
                result[result_key] = []

        return result


@cached(
    category="f10_shareholder", valid_if=make_valid_if(), cross_verify=True
)  # V15.2: 强化 valid_if
def tdx_get_shareholder_research(code: str) -> dict:
    """从 TDX F10「股东研究」分类获取股东信息（7 个子栏目）。

    替代 2 个东财 HTTP 接口：
    - get_eastmoney_shareholders（十大股东）
    - get_eastmoney_holder_changes（股东人数变化）

    Returns:
        dict: {
            "controlling_shareholder": {...},   # 控股股东/实际控制人
            "planned_changes": [...],           # 股东增减持计划
            "major_holder_changes": [...],      # 重要股东持股变动
            "shareholder_changes": [...],       # 十大股东列表（按期）
            "holder_count": [...],              # 股东人数变化
            "same_controller_stocks": [...],    # 同大股东个股
            "fund_holdings": [...]              # 基金持股
        }
    """
    from stock_common.f10_parser import (
        split_sections,
        parse_table,
        parse_tables,
        parse_key_value_table,
        parse_text_table,
    )
    import re as _re

    with _TDX_CALL_LOCK:
        content = _f10_get_content(code, '股东研究')
        if not content:
            return {}
        sections = split_sections(content)
        result: dict = {}

        # 1. 控股股东与实际控制人（键值对表格）
        s1 = sections.get('控股股东与实际控股人', '')
        if s1 and '暂无数据' not in s1:
            result['controlling_shareholder'] = parse_key_value_table(s1)
        else:
            result['controlling_shareholder'] = {}

        # 2. 股东增减持计划
        s2 = sections.get('股东增减持计划', '')
        if s2 and '暂无数据' not in s2:
            # 提取摘要信息
            plan_info: dict = {}
            m = _re.search(r'最新公告日期[：:]\s*([\d-]+)', s2)
            if m:
                plan_info['latest_date'] = m.group(1)
            m = _re.search(r'变动方向[：:]\s*([^，,]+)', s2)
            if m:
                plan_info['direction'] = m.group(1).strip()
            m = _re.search(r'进度[：:]\s*([^，,\s]+)', s2)
            if m:
                plan_info['progress'] = m.group(1).strip()
            rows = parse_table(s2)
            plan_info['details'] = rows
            result['planned_changes'] = plan_info
        else:
            result['planned_changes'] = {}

        # 3. 重要股东持股变动（标准表格）
        s3 = sections.get('重要股东持股变动', '')
        if s3 and '暂无数据' not in s3:
            result['major_holder_changes'] = parse_table(s3)
        else:
            result['major_holder_changes'] = []

        # 4. 股东变化（十大股东 — 空格分隔文本格式）
        s4 = sections.get('股东变化', '')
        if s4 and '暂无数据' not in s4:
            # 按"●十大股东"和"●十大流通股东"分割
            shareholder_periods: list = []
            blocks = _re.split(r'●(十大股东|十大流通股东)\s*', s4)
            # blocks: [preamble, label1, content1, label2, content2, ...]
            for i in range(1, len(blocks), 2):
                label = blocks[i]
                content_block = blocks[i + 1] if i + 1 < len(blocks) else ''
                # 提取截止日期
                m = _re.search(r'截止日期[：:]\s*([\d-]+)', content_block)
                period = m.group(1) if m else ''
                # 提取摘要
                m = _re.search(r'前十大[^\n]*累计持有[：:]?([^\n]+)', content_block)
                summary = m.group(1).strip() if m else ''
                # 解析十大股东明细（空格分隔，可能跨行）
                lines = content_block.split('\n')
                # 找到表头行（含"股东名称"）
                header_idx = -1
                for j, line in enumerate(lines):
                    if '股东名称' in line:
                        header_idx = j
                        break
                holders: list = []
                if header_idx >= 0:
                    # 跳过分隔线，解析数据行
                    for j in range(header_idx + 1, len(lines)):
                        line = lines[j].strip()
                        if not line or '──' in line:
                            continue
                        if line.startswith('●') or '截止日期' in line:
                            break
                        # 用 2+ 空格分割
                        parts = [p.strip() for p in _re.split(r'\s{2,}', line) if p.strip()]
                        # 十大股东格式：名称 股份性质 持股数 占比 增减 一致行动人
                        if len(parts) >= 5:
                            holders.append(
                                {
                                    'name': parts[0],
                                    'share_type': parts[1],
                                    'shares': parts[2],
                                    'ratio': parts[3],
                                    'change': parts[4],
                                    'group': parts[5] if len(parts) > 5 else '',
                                }
                            )
                shareholder_periods.append(
                    {'type': label, 'period': period, 'summary': summary, 'holders': holders[:10]}
                )
            result['shareholder_changes'] = shareholder_periods
        else:
            result['shareholder_changes'] = []

        # 5. 股东人数变化（表格，每行一期，截止日期为第一列）
        s5 = sections.get('股东人数变化', '')
        if s5 and '暂无数据' not in s5:
            tables = parse_tables(s5)
            holder_list: list = []
            seen_periods: set = set()
            for tbl in tables:
                if not tbl:
                    continue
                for row in tbl:
                    period = (row.get('截止日期', '') or row.get('日期', '') or '').strip()
                    if period and period not in seen_periods:
                        seen_periods.add(period)
                        entry = {'period': period}
                        for k, v in row.items():
                            if k not in ('截止日期', '日期'):
                                entry[k] = v.strip() if isinstance(v, str) else v
                        holder_list.append(entry)
            result['holder_count'] = holder_list
        else:
            result['holder_count'] = []

        # 6-7. 同大股东个股 / 基金持股（常为空）
        s6 = sections.get('同大股东个股', '')
        result['same_controller_stocks'] = [] if (not s6 or '暂无数据' in s6) else parse_table(s6)
        s7 = sections.get('基金持股', '')
        result['fund_holdings'] = [] if (not s7 or '暂无数据' in s7) else parse_table(s7)

        return result


@cached(
    category="f10_share_capital", valid_if=make_valid_if(), cross_verify=True
)  # V15.2: 强化 valid_if
def tdx_get_share_capital(code: str) -> dict:
    """从 TDX F10「股本结构」分类获取股本信息（4 个子栏目）。

    替代 1 个东财 HTTP 接口：
    - get_eastmoney_lockup_expiry（限售解禁）

    Returns:
        dict: {
            "structure": [...],      # 股本结构（按期）
            "changes": [...],        # 股本变化历史
            "lockup_expiry": [...],  # 限售解禁时间表
            "buyback": [...]         # 股票回购记录
        }
    """
    from stock_common.f10_parser import split_sections, parse_table, parse_tables, transpose_table

    with _TDX_CALL_LOCK:
        content = _f10_get_content(code, '股本结构')
        if not content:
            return {}
        sections = split_sections(content)
        result: dict = {}

        # 1. 股本结构（表格，转置为按期）
        s1 = sections.get('股本结构', '')
        if s1 and '暂无数据' not in s1:
            tables = parse_tables(s1)
            merged: dict = {}
            for tbl in tables:
                if not tbl:
                    continue
                key_col = next(iter(tbl[0].keys())) if tbl[0] else ''
                transposed = transpose_table(tbl, key_col)
                for entry in transposed:
                    period = entry.get('period', '')
                    if period and period not in merged:
                        merged[period] = entry
            result['structure'] = list(merged.values())
        else:
            result['structure'] = []

        # 2. 股本变化（标准表格，每行一条变更记录）
        s2 = sections.get('股本变化', '')
        if s2 and '暂无数据' not in s2:
            result['changes'] = parse_table(s2)
        else:
            result['changes'] = []

        # 3. 限售解禁
        s3 = sections.get('限售解禁', '')
        if s3 and '暂无数据' not in s3:
            result['lockup_expiry'] = parse_table(s3)
        else:
            result['lockup_expiry'] = []

        # 4. 股票回购（键值对表格，按公告日组织）
        s4 = sections.get('股票回购', '')
        if s4 and '暂无数据' not in s4:
            tables = parse_tables(s4)
            buyback_list: list = []
            for tbl in tables:
                if not tbl:
                    continue
                # 回购表格是键值对格式：每行一个指标，列是不同公告日
                key_col = next(iter(tbl[0].keys())) if tbl[0] else ''
                date_cols = [c for c in tbl[0].keys() if c != key_col]
                for date_col in date_cols:
                    entry: dict = {'announce_date': date_col.strip()}
                    for row in tbl:
                        indicator = (row.get(key_col) or '').strip()
                        if indicator:
                            entry[indicator] = (row.get(date_col) or '').strip()
                    buyback_list.append(entry)
            result['buyback'] = buyback_list
        else:
            result['buyback'] = []

        return result


@cached(category="f10_news", trading_day=True, valid_if=make_valid_if())  # V15.2: 拒绝空 dict/全 0
def tdx_get_company_news_f10(code: str, count: int = 10) -> list:
    """从 TDX F10 公司新闻分类获取列表。

    V12.0: mootdx F10C 无「公司报道」分类，改用语义等价的「公司大事」。
    「公司大事」是表格格式（｜ 日期 ｜ 标题 ｜），与「公司报道」段落格式不同，
    需使用专门的表格解析逻辑。保留对原「公司报道」的 fallback。

    替代 1 个东财 HTTP 接口：
    - get_eastmoney_stock_news

    Args:
        code: 股票代码
        count: 返回条数上限

    Returns:
        list: [{date, title, summary, url}, ...]
    """
    import re as _re
    from stock_common.f10_parser import parse_paragraph_blocks

    with _TDX_CALL_LOCK:
        # V12.0: 先尝试 mootdx 的「公司大事」（表格格式），再 fallback 到 easy_tdx 的「公司报道」（段落格式）
        content = _f10_get_content(code, '公司大事')
        if content:
            # 「公司大事」表格格式解析：｜   YYYY-MM-DD   ｜标题内容｜
            news = []
            # 匹配 ｜   日期   ｜标题｜  格式
            pattern = _re.compile(r'[｜|]\s*(\d{4}-\d{2}-\d{2})\s*[｜|]\s*([^｜|]+?)\s*[｜|]')
            for m in pattern.finditer(content):
                date_str = m.group(1)
                title = m.group(2).strip()
                if title and len(title) > 3:
                    news.append(
                        {
                            "date": date_str,
                            "title": title[:200],
                            "summary": "",
                            "url": "",
                        }
                    )
            if news:
                return news[:count]
            # 表格解析失败时，尝试段落解析（万一格式变化）
        # Fallback: 「公司报道」段落格式
        content = _f10_get_content(code, '公司报道')
        if not content:
            return []
        lines = content.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if '──' in line and '┬' in line:
                start_idx = i
                break
        if start_idx > 0:
            content = '\n'.join(lines[start_idx:])
        news = parse_paragraph_blocks(content)
        return news[:count]


def tdx_get_industry_analysis(code: str) -> dict:
    """从 TDX F10「行业分析」分类获取行业地位信息（5 个子栏目）。

    替代 1 个东财 HTTP 接口：
    - get_eastmoney_industry_board

    Returns:
        dict: {
            "industry": {...},              # 所属行业
            "market_performance": [...],    # 市场表现排名
            "company_scale": [...],         # 公司规模排名
            "valuation_level": [...],       # 估值水平排名
            "financial_status": [...]       # 财务状况排名
        }
    """
    from stock_common.f10_parser import split_sections, parse_text_table
    import re as _re

    with _TDX_CALL_LOCK:
        content = _f10_get_content(code, '行业分析')
        if not content:
            return {}
        sections = split_sections(content)
        result: dict = {}

        # 1. 所属行业（文本，如"所属研究行业:酿酒(共36家)"）
        s1 = sections.get('所属行业', '')
        if s1 and '暂无数据' not in s1:
            industry: dict = {}
            m = _re.search(r'所属研究行业[：:]\s*(\S+?)\s*\(共(\d+)家\)', s1)
            if m:
                industry['name'] = m.group(1)
                industry['total_count'] = int(m.group(2))
            else:
                # 兜底：取第一行非空文本
                for line in s1.split('\n'):
                    line = line.strip()
                    if line and '暂无数据' not in line:
                        industry['raw'] = line
                        break
            result['industry'] = industry
        else:
            result['industry'] = {}

        # 2-5. 四个排名表（空格分隔文本表格）
        for result_key, section_name in [
            ('market_performance', '市场表现排名'),
            ('company_scale', '公司规模排名'),
            ('valuation_level', '估值水平排名'),
            ('financial_status', '财务状况排名'),
        ]:
            s = sections.get(section_name, '')
            if s and '暂无数据' not in s:
                # 提取截止日期
                m = _re.search(r'截止日期[：:]\s*([\d-]+)', s)
                cutoff_date = m.group(1) if m else ''
                rows = parse_text_table(s)
                # 找本股票在排名中的位置
                my_rank: dict = {}
                for r in rows:
                    if code in str(r.values()) or '贵州茅台' in str(r.values()):
                        my_rank = r
                        break
                result[result_key] = {
                    'cutoff_date': cutoff_date,
                    'my_rank': my_rank,
                    'top_rankings': rows[:10],  # 前10名
                }
            else:
                result[result_key] = {'cutoff_date': '', 'my_rank': {}, 'top_rankings': []}

        return result


# ═══════════════════════════════════════════════════════════════
# V12.0: 板块/全市场函数（原 MacClient 实现，已迁移到东财 HTTP + ZHB）
# ═══════════════════════════════════════════════════════════════

# ── V15.5.1: easy_tdx MacClient（v9.6 概念板块源，MAC 协议不走 push2）──
_TDX_MAC_CLIENT = None


def _get_mac_client() -> Optional[Any]:
    """V15.5.1: 获取 easy_tdx MacClient（MAC 协议，板块归属源）。

    v9.6 概念板块走 MacClient.get_belong_board（TCP 不封 IP）；
    v15 误改为 push2 HTTP → 当前网络 push2 风控挂 → 概念 0 个。
    恢复 v9.6 路径：白名单服务器首选 + from_best_host 换台。
    """
    global _TDX_MAC_CLIENT
    with _TDX_CALL_LOCK:
        for attempt in range(_TDX_RECONNECT_ATTEMPTS):
            if _TDX_MAC_CLIENT is not None:
                try:
                    if hasattr(_TDX_MAC_CLIENT, "ensure_connected"):
                        _TDX_MAC_CLIENT.ensure_connected()
                    return _TDX_MAC_CLIENT
                except Exception as _e:
                    _debug_log(f"tdx _get_mac_client ensure_connected: {_e}")
                    try:
                        _TDX_MAC_CLIENT.close()
                    except Exception:
                        pass
                    _TDX_MAC_CLIENT = None
                    if attempt < _TDX_RECONNECT_ATTEMPTS - 1:
                        time.sleep(_TDX_RECONNECT_DELAY * (2**attempt))
                    continue
            try:
                from easy_tdx.mac.client import MacClient

                try:
                    _c = MacClient(
                        host=_EASY_TDX_PRIMARY_HOST,
                        port=7709,
                        auto_reconnect=True,
                        heartbeat_interval=15.0,
                    )
                    _c.connect()
                    _TDX_MAC_CLIENT = _c
                except Exception as _e:
                    _debug_log(f"easy_tdx mac primary failed ({_EASY_TDX_PRIMARY_HOST}): {_e}")
                    _TDX_MAC_CLIENT = MacClient.from_best_host(
                        hosts=_EASY_TDX_PREFERRED_HOSTS, ping_timeout=3.0
                    )
                    _TDX_MAC_CLIENT.connect()
                _debug_log("easy_tdx MacClient connected")
                return _TDX_MAC_CLIENT
            except Exception as _e:
                _debug_log(f"tdx _get_mac_client easy_tdx error: {_e}")
                _TDX_MAC_CLIENT = None
                if attempt < _TDX_RECONNECT_ATTEMPTS - 1:
                    time.sleep(_TDX_RECONNECT_DELAY * (2**attempt))
    return None


def tdx_get_belong_boards(code: str):
    """获取股票所属板块（行业/概念/地域/风格）。

    V15.5.1: 恢复 v9.6 路径 — easy_tdx MacClient.get_belong_board（MAC 协议 TCP，
    不封 IP）首选；失败 fallback 东财 push2 HTTP（原 V12.0 路径）。
    背景: V12.0 误改为 push2 后，push2 连接级风控（参考仓库 FAQ）→ 概念板块 0 个。

    Returns:
        dict: {"industry": [...], "concept": [...], "area": [...], "style": [...]}
              每项为 [{"code": str, "name": str}, ...]
    """
    with _TDX_CALL_LOCK:
        client = _get_mac_client()
        if client is not None:
            try:
                df = client.get_belong_board(_easy_market(code), code)
                if df is not None and not df.empty:
                    result: Dict[str, List[Any]] = {
                        "industry": [],
                        "concept": [],
                        "area": [],
                        "style": [],
                    }
                    # v9.6 type_map: 0/1/2/12=行业 3=地域 4=概念 5=风格
                    # V15.5.2: 补 type=2（实测 000100 行业板块"元器件"=type 2）
                    # V16.2.14: 行业一级(0/1/12)优先于二级(2)——一级(如"光学光电")更贴近
                    # 东财/申万通用口径；二级(如"元器件")为细分兜底（不同服务器返回层级不同）
                    type_map = {
                        0: "industry",
                        1: "industry",
                        2: "industry",
                        12: "industry",
                        3: "area",
                        4: "concept",
                        5: "style",
                    }
                    for _, row in df.iterrows():
                        bt = int(row.get('board_type', -1))
                        cat = type_map.get(bt)
                        if cat is None:
                            continue
                        result[cat].append(
                            {
                                "code": str(row.get('board_code', '')),
                                "name": str(row.get('board_name', '')),
                                "_bt": bt,
                            }
                        )
                    # V16.2.14: industry 排序 —— 一级(0/1/12)在前，二级(2)在后
                    for _cat in ("industry",):
                        _items = result[_cat]
                        if len(_items) > 1:
                            _items.sort(key=lambda x: 0 if x.get("_bt") in (0, 1, 12) else 1)
                        for _it in _items:
                            _it.pop("_bt", None)
                    _debug_log(
                        f"tdx_get_belong_boards mac OK ({code}): "
                        f"industry={len(result['industry'])} concept={len(result['concept'])}"
                    )
                    return result
            except Exception as _e:
                _debug_log(f"tdx_get_belong_boards mac error ({code}): {_e}")
    # fallback: 东财 push2（原 V12.0 路径）
    try:
        from stock_common.sc_datasource import get_em_belong_boards

        return get_em_belong_boards(code)
    except Exception as _e:
        _debug_log(f"tdx_get_belong_boards {code}: {_e}")
        return {}


@cached(category="board_list", ttl_seconds=TTL["board_list"], trading_day=True, valid_if=make_valid_if())
def tdx_get_board_list(board_type: int = 0):
    """获取板块列表（行业/概念/地域等）。

    V12.0: 委托到东财 HTTP 接口（原 TDX MacClient.get_board_list 已废弃）。
    V16.3 L 注: 曾尝试恢复 MAC 优先——经用户纠正方向错误（MAC 56 通达信行业
    粒度粗于东财 100，且与申万二级口径不一致）；行业排名应走 ZHB 旁路（129 申万二级，
    见 get_mak_report._build_sectors_from_zhb）。本函数保持东财委托（低频批量 clist，
    非逐股，非风控元凶；风控元凶 mak 100 次 members fallback 已由 ZHB 旁路消除）。
    V16.3 O25: 加交易日粒度缓存——lng/med/sht 行业排名参照系（T-1 可接受，
    避免每次报告现取东财 clist）；mak/val 同享（当日共享、次日 9:30 刷新）。

    Args:
        board_type: 0=行业一级, 1=行业二级, 4=概念, 3=地域

    Returns:
        list: [{"rank": int, "code": str, "name": str, "price": float,
                "change_pct": float, "leader_name": str, "leader_change": float,
                "up_count": int, "down_count": int}, ...]
    """
    try:
        from stock_common.sc_datasource import get_em_board_list

        return get_em_board_list(board_type)
    except Exception as _e:
        _debug_log(f"tdx_get_board_list type={board_type}: {_e}")
        return []


def tdx_get_board_members(board_code: str, sort_by_change: bool = True):
    """获取板块成员列表。

    V15.5.2: 恢复 v9.6 MacClient.get_board_members（MAC 协议 TCP，不封 IP）；
             失败 fallback 东财 push2 HTTP。

    Returns:
        list: [{"code": str, "name": str, "price": float, "change_pct": float,
                "mcap_yi": float, "turnover": float, "pe": float,
                "main_net_amount": float}, ...]
    """
    with _TDX_CALL_LOCK:
        client = _get_mac_client()
        if client is not None:
            try:
                df = client.get_board_members(board_code)
                if df is None or df.empty:
                    # V16.4.1: 空结果继续走东财兜底(原直接 return [] 使 docstring 承诺的
                    # fallback 永不触发, 板块成分静默为空)
                    raise ValueError("empty board members (tdx)")
                members = []
                for _, row in df.iterrows():
                    close = _safe_float(row.get('close', 0))
                    pre_close = _safe_float(row.get('pre_close', 0))
                    chg = (
                        round((close - pre_close) / pre_close * 100, 2)
                        if pre_close > 0
                        else _safe_float(row.get('speed_pct', 0))
                    )
                    members.append(
                        {
                            "code": str(row.get('code', '')),
                            "name": str(row.get('name', '')),
                            "price": close,
                            "change_pct": chg,
                            "mcap_yi": _safe_float(row.get('total_market_cap_ab', 0)) / 1e8,
                            "turnover": _safe_float(row.get('turnover', 0)),
                            "pe": _safe_float(row.get('pe_dynamic', row.get('pe_ttm', 0))),
                            "main_net_amount": _safe_float(row.get('main_net_amount', 0)),
                        }
                    )
                return members
            except Exception as _e:
                _debug_log(f"tdx_get_board_members mac {board_code}: {_e}")
    # fallback: 东财 push2
    try:
        from stock_common.sc_datasource import get_em_board_members

        return get_em_board_members(board_code)
    except Exception as _e:
        _debug_log(f"tdx_get_board_members {board_code}: {_e}")
        return []


def tdx_get_board_by_name(board_name: str, board_type: int = 0):
    """按名称查找板块并返回成员列表。

    V15.5.2: 恢复 v9.6 MacClient.get_board_list 名称匹配（MAC 协议 TCP）；
             失败 fallback 东财 push2 HTTP。

    Args:
        board_name: 板块名称（支持模糊匹配）
        board_type: 板块类型

    Returns:
        list: 同 tdx_get_board_members 返回格式
    """
    with _TDX_CALL_LOCK:
        client = _get_mac_client()
        if client is not None:
            try:
                from easy_tdx.mac.enums import BoardType

                bt = BoardType(board_type)
            except Exception as _e:
                _debug_log(f"tdx tdx_get_board_by_name BoardType error ({board_type}): {_e}")
                bt = None
            if bt is not None:
                try:
                    board_df = client.get_board_list(bt)
                    if board_df is not None and not board_df.empty:
                        _name_clean = (
                            board_name.replace("行业", "")
                            .replace("板块", "")
                            .replace("Ⅱ", "")
                            .replace("Ⅲ", "")
                        )
                        matched_code = None
                        for _, row in board_df.iterrows():
                            row_name = str(row.get('name', ''))
                            row_clean = (
                                row_name.replace("行业", "")
                                .replace("板块", "")
                                .replace("Ⅱ", "")
                                .replace("Ⅲ", "")
                            )
                            if (
                                board_name in row_name
                                or row_name in board_name
                                or _name_clean in row_clean
                                or row_clean in _name_clean
                            ):
                                matched_code = str(row.get('code', ''))
                                break
                        if matched_code:
                            return tdx_get_board_members(matched_code)
                except Exception as _e:
                    _debug_log(f"tdx tdx_get_board_by_name mac error: {_e}")
    # fallback: 东财 push2
    try:
        from stock_common.sc_datasource import get_em_board_list, get_em_board_members

        board_list = get_em_board_list(board_type)
        if not board_list:
            return []
        _name_clean = (
            board_name.replace("行业", "").replace("板块", "").replace("Ⅱ", "").replace("Ⅲ", "")
        )
        matched_code = None
        for row in board_list:
            row_name = str(row.get('name', ''))
            row_clean = (
                row_name.replace("行业", "").replace("板块", "").replace("Ⅱ", "").replace("Ⅲ", "")
            )
            if (
                board_name in row_name
                or row_name in board_name
                or _name_clean in row_clean
                or row_clean in _name_clean
            ):
                matched_code = str(row.get('code', ''))
                break
        if matched_code is None:
            return []
        return get_em_board_members(matched_code)
    except Exception as _e:
        _debug_log(f"tdx_get_board_by_name {board_name}: {_e}")
        return []


def tdx_get_market_abnormal_data():
    """全市场A股 + 多周期涨幅（用于异动扫描）。

    V12.0: 改用 ZHB 全市场快照（原 TDX MacClient.get_stock_quotes_list 已废弃）。
    ZHB 数据为 T-1 收盘快照，对异动扫描足够。

    Returns:
        list: [{"code": str, "name": str, "price": float, "change_pct": float,
                "turnover": float, "mcap_yi": float,
                "ret_3d": float, "ret_5d": float, "ret_10d": float,
                "ret_20d": float, "ret_60d": float,
                "main_net_amount": float}, ...]
    """
    try:
        from stock_common import get_zhb_full_market_snapshot
        from core.zhb_client import get_stock_name_from_zhb

        snapshot = get_zhb_full_market_snapshot()
        if not snapshot:
            return []
        all_stocks = []
        # V14.2.1: 提前加载 ZHB profile 名称（修复 name 字段缺失 Bug）
        zhb_name_cache: Dict[str, str] = {}
        # V15.5.17: unified_name_map 优先（profile.dat 解析失败时仍覆盖 44%）
        _unified_name: Dict[str, str] = {}
        try:
            from core.zhb_client import get_zhb

            _unified_name = get_zhb().unified_name_map or {}
        except Exception:
            pass
        for code, data in snapshot.items():
            if not isinstance(data, dict):
                continue
            name = str(data.get('name', '') or '')
            if not name:
                # V14.2.1: ZHB tdxstat 快照无 name 字段，用 profile.dat 离线字典补齐
                # V15.5.17: unified_name_map 优先（relation.dat+pttab 等合并，覆盖 44%）
                if _unified_name.get(code):
                    name = _unified_name[code]
                elif code not in zhb_name_cache:
                    zhb_name_cache[code] = get_stock_name_from_zhb(code) or ""
                    name = zhb_name_cache[code]
            # V15.5.17: name 缺失不再 continue（mak 层腾讯批量补全 name）
            # 仅跳过明确的 ST/退市（避免垃圾股进扫描）
            if 'ST' in name or '退' in name:
                continue
            price = _safe_float(data.get('price', 0))
            change_pct = _safe_float(data.get('change_pct', 0))
            # V15.5.17: price 缺失不再 continue（腾讯批量补全 price）
            all_stocks.append(
                {
                    'code': code,
                    'name': name,
                    'price': price,
                    'change_pct': change_pct,
                    'turnover': _safe_float(data.get('turnover_pct', 0)),
                    'mcap_yi': _safe_float(data.get('mcap_yi', 0)),
                    'ret_3d': 0.0,  # V16.1: 移除 change_pct_2d 冒充 3 日收益（非真实 3 日窗口，宁缺毋滥）
                    'ret_5d': _safe_float(data.get('change_5d', 0)),
                    'ret_10d': _safe_float(data.get('change_10d', 0)),
                    'ret_20d': _safe_float(data.get('change_20d', 0)),
                    'ret_60d': _safe_float(data.get('change_60d', 0)),
                    'main_net_amount': _safe_float(data.get('main_net_buy_amount', 0)) * 10000,  # ⚠️ V17.0 实锤=竞价额(万元→元), 非主力净
                }
            )
        return all_stocks
    except Exception as _e:
        _debug_log(f"tdx_get_market_abnormal_data: {_e}")
        return []


def tdx_get_all_stocks():
    """全市场A股列表。

    V12.0: 改用 ZHB 全市场快照（原 TDX MacClient.get_stock_quotes_list 已废弃）。
    ZHB 数据为 T-1 收盘快照，对盘后分析足够。

    Returns:
        list: [{"code": str, "name": str, "price": float, "change_pct": float,
                "mcap_yi": float, "turnover_pct": float, "amount_yi": float}, ...]
    """
    try:
        from stock_common import get_zhb_full_market_snapshot

        snapshot = get_zhb_full_market_snapshot()
        if not snapshot:
            return []
        all_stocks = []
        for code, data in snapshot.items():
            if not isinstance(data, dict):
                continue
            name = str(data.get('name', '') or '')
            if not name or 'ST' in name or '退' in name:
                continue
            price = _safe_float(data.get('price', 0))
            if price <= 0:
                continue
            amount_wan = _safe_float(data.get('amount', 0))
            all_stocks.append(
                {
                    'code': code,
                    'name': name,
                    'price': price,
                    'change_pct': _safe_float(data.get('change_pct', 0)),
                    'mcap_yi': _safe_float(data.get('mcap_yi', 0)),
                    'turnover_pct': _safe_float(data.get('turnover_pct', 0)),
                    'amount_yi': amount_wan / 10000.0,
                }
            )
        return all_stocks
    except Exception as _e:
        _debug_log(f"tdx tdx_get_all_stocks error: {_e}")
        return []
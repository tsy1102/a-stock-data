#!/usr/bin/env python3
"""eltdx 适配器 — 把 eltdx (Rust 内核 7709/7615 通达信客户端) 包装成 mootdx 兼容接口。

V17.2.15: 取代 easy_tdx 成为 TDX TCP 主源（core/tdx_client.py 调用）。

设计要点:
  - eltdx Rust 握手已含 2026-09 新式单条随机 msg_id → tdx_client 不再需要 _tdx_handshake_patch。
  - 返回结构与 _EasyTdxAdapter 对齐（DataFrame 列名/单位 mootdx 兼容），下游零改动。
  - FinanceRecord *_raw_float 聚合字段为**万元**口径，映射 mootdx 角口径需 ×100000
    （data_provider 对 zongzichan/jingzichan/jinglirun 按角处理 /10 得元，已用平安银行反推验证）。
  - 北交所(83/87/88/43/46/92)快照 eltdx 偶发解析失败(实测 "snapshot record marker not found") →
    抛异常交上层 HTTP fallback（ZHB/腾讯/东财），与 easy_tdx 降级策略一致。
  - 主站固定: pin 白名单 FULL 主机 + probe_hosts=False，避免冷连接全量探测（~6min）。
  - F10 二进制分类(0x02CF/0x02D0) eltdx 无等价实现 → F10C/F10 返回空，F10 函数走东财 fallback。
  - xdxr(分红除权) eltdx capital_changes 映射待补 → 返回空 DataFrame，分红历史走其他源。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from stock_common import _debug_log

import time

import pandas as _pd

# get_eltdx_shortline_bundle 模块级缓存: 同进程同 codes 集合共享 bundle, 避免 val 多策略重复连接 eltdx。
_SHORTLINE_BUNDLE_CACHE: dict = {"key": None, "ts": 0.0, "val": None}
_SHORTLINE_TTL: float = 300.0

# 已知全量 FULL 主机（V16.2.11/16.3.9 复测 6 台），pin 避免 eltdx 冷探测。
# 注意 eltdx 主机格式须为 "ip:7709"（裸 IP 会被 rank_hosts_from_cache 过滤）。
_ELTDX_HOSTS = [
    "180.153.18.170:7709",
    "115.238.56.198:7709",
    "115.238.90.165:7709",
    "218.75.126.9:7709",
    "159.75.55.232:7709",
    "120.76.152.87:7709",
]

# mootdx frequency(int) → eltdx period(str)
_FREQ_TO_ELTDX = {
    0: "5min", 1: "15min", 2: "30min", 3: "60min",
    4: "day", 5: "week", 6: "month", 7: "1min", 8: "1min",
    9: "day", 10: "quarter", 11: "year",
}

# eltdx FinanceRecord 字段 → (mootdx 列名, 单位换算)
#   scale: 'qy2jiao' = 千元→角 ×10000; 'yuan' = 元 ×1; 'raw' = 原样(股/户/字符串)
#   实测反推(eltdx zong_zi_chan_raw_float=6.029e9 → 平安银行总资产~6万亿 元):
#   eltdx 聚合字段为**千元**口径(非万元)，千元→角=×10000；data_provider 对 zongzichan/
#   jingzichan/jinglirun 按角处理 /10 得元，故 ×10000 后链路口径闭合。
_FIN_MAP = [
    ("liu_tong_gu_ben_raw_float", "liutongguben", "raw"),
    ("zong_gu_ben_raw_float", "zhongguben", "raw"),
    ("guo_jia_gu_raw_float", "guojiagu", "raw"),
    ("fa_qi_ren_fa_ren_gu_raw_float", "fajirenfarengu", "raw"),
    ("fa_ren_gu_raw_float", "farengu", "raw"),
    ("b_gu_raw_float", "bgu", "raw"),
    ("h_gu_raw_float", "hgu", "raw"),
    ("zong_zi_chan_raw_float", "zongzichan", "qy2jiao"),
    ("liu_dong_zi_chan_raw_float", "liudongzichan", "qy2jiao"),
    ("gu_ding_zi_chan_raw_float", "gudingzichan", "qy2jiao"),
    ("wu_xing_zi_chan_raw_float", "wuxingzichan", "qy2jiao"),
    ("gu_dong_ren_shu_raw_float", "gudongrenshu", "raw"),
    ("liu_dong_fu_zhai_raw_float", "liudongfuzhai", "qy2jiao"),
    ("chang_qi_fu_zhai_raw_float", "changqifuzhai", "qy2jiao"),
    ("zi_ben_gong_ji_jin_raw_float", "zibengongjijin", "qy2jiao"),
    ("jing_zi_chan_raw_float", "jingzichan", "qy2jiao"),
    ("zhu_ying_shou_ru_raw_float", "zhuyingshouru", "qy2jiao"),
    ("zhu_ying_li_run_raw_float", "zhuyinglyrun", "qy2jiao"),
    ("ying_shou_zhang_kuan_raw_float", "yingshouzhangkuan", "qy2jiao"),
    ("ying_ye_li_run_raw_float", "yingyelirun", "qy2jiao"),
    ("tou_zi_shou_yu_raw_float", "touzishouyu", "qy2jiao"),
    ("jing_ying_xian_jin_liu_raw_float", "jingyingxianjinliu", "qy2jiao"),
    ("zong_xian_jin_liu_raw_float", "zongxianjinliu", "qy2jiao"),
    ("cun_huo_raw_float", "cunhuo", "qy2jiao"),
    ("li_run_zong_he_raw_float", "lirunzonghe", "qy2jiao"),
    ("shui_hou_li_run_raw_float", "shuihouli run", "qy2jiao"),
    ("jing_li_run_raw_float", "jinglirun", "qy2jiao"),
    ("wei_fen_li_run_raw_float", "weifenlirun", "qy2jiao"),
    ("mei_gu_jing_zi_chan_raw_float", "meigujingzichan", "yuan"),
    ("bao_liu_2_raw_float", "baoliu2", "raw"),
    ("eps_raw", "eps", "yuan"),
]


class _EltdxAdapter:
    """mootdx 兼容接口封装（V17.2.15, eltdx 内核）。"""

    def __init__(self, client: Any) -> None:
        self._client = client
        self.closed = False

    @staticmethod
    def _empty() -> Any:
        return _pd.DataFrame()

    # ── 实时行情快照 ───────────────────────────────────────────────
    def quotes(self, symbol: str) -> Any:
        try:
            snaps = self._client.quotes.get_snapshots([symbol])
        except Exception as _e:  # 北交所等偶发解析失败 → 交上层 fallback
            _debug_log(f"eltdx quotes error ({symbol}): {_e}")
            return self._empty()
        if not snaps:
            return self._empty()
        s = snaps[0]
        row = {
            "code": getattr(s, "code", symbol),
            "price": s.last_price,
            "last_close": s.pre_close_price,
            "open": s.open_price,
            "high": s.high_price,
            "low": s.low_price,
            "amount": s.amount,
            "s_vol": s.inside_dish,
            "b_vol": s.outer_disc,
        }
        for i, lv in enumerate(s.buy_levels[:5], 1):
            row[f"bid{i}"] = lv.price
        for i, lv in enumerate(s.sell_levels[:5], 1):
            row[f"ask{i}"] = lv.price
        return _pd.DataFrame([row])

    # ── K 线 ───────────────────────────────────────────────────────
    def bars(self, symbol, frequency=9, start=0, offset=800) -> Any:
        # 北交所老段（8/4 开头非 92）已知无 K 线 → 直接返回空（同 easy_tdx 处理）
        if symbol.startswith(("8", "4")) and not symbol.startswith("92"):
            return self._empty()
        period = _FREQ_TO_ELTDX.get(frequency, "day")
        try:
            series = self._client.bars.get(
                symbol, period=period, start=start, count=offset, include_raw=False
            )
        except Exception as _e:
            _debug_log(f"eltdx bars error ({symbol}): {_e}")
            return self._empty()
        bars = getattr(series, "bars", None) or []
        rows = []
        for b in bars:
            d = str(b.time)[:10]
            rows.append(
                {
                    "date": d,
                    "datetime": f"{d} 00:00",
                    "open": b.open,
                    "close": b.close,
                    "high": b.high,
                    "low": b.low,
                    "vol": b.volume_lots,
                    "amount": b.amount,
                }
            )
        return _pd.DataFrame(rows)

    def index_bars(self, symbol, frequency=9, start=0, offset=800, market=None) -> Any:
        return self.bars(symbol, frequency, start, offset)

    # ── 分红除权（eltdx capital_changes 映射待补，暂返回空）────────
    def xdxr(self, symbol: str) -> Any:
        _debug_log(f"eltdx xdxr stub ({symbol}): eltdx capital_changes 映射未实现，返回空")
        return self._empty()

    # ── 财务 0x0010 ───────────────────────────────────────────────
    def finance(self, symbol: str) -> Any:
        try:
            batch = self._client.corporate.finance_batch(symbol, include_raw=False)
        except Exception as _e:
            _debug_log(f"eltdx finance error ({symbol}): {_e}")
            return self._empty()
        recs = getattr(batch, "records", None) or []
        if not recs:
            return self._empty()
        r = recs[0]
        out: dict[str, Any] = {}
        for attr, col, scale in _FIN_MAP:
            v = getattr(r, attr, None)
            if v is None:
                continue
            if scale == "qy2jiao":
                v = v * 10000.0  # 千元 → 角（对齐 mootdx 角口径）
            out[col] = v
        out["updated_date"] = str(getattr(r, "updated_date", ""))
        out["ipo_date"] = str(getattr(r, "ipo_date", ""))
        # 带下划线别名兼容下游双格式读取
        for k in list(out.keys()):
            no_us = str(k).replace(" ", "").replace("_", "")
            if no_us != k and no_us not in out:
                out[no_us] = out[k]
        return _pd.DataFrame([out])

    def get_finance_info(self, market=None, symbol="") -> Any:
        if not symbol and market is not None and isinstance(market, str):
            symbol = market
        if not symbol:
            return self._empty()
        return self.finance(symbol)

    # ── 涨跌停价（eltdx 无直接接口，交上层 ±10% 计算或跳过）──────
    def price_limits(self, symbol, pre_close):
        return (None, None)

    # ── 市场统计（eltdx limits 尽力而为）──────────────────────────
    def market_stat(self):
        try:
            lim = getattr(self._client, "limits", None)
            if lim is not None and hasattr(lim, "market_stat"):
                return lim.market_stat()
        except Exception as _e:
            _debug_log(f"eltdx market_stat error: {_e}")
        return None

    # ── F10 二进制分类（eltdx 无等价，返回空 → F10 函数走东财）────
    def F10C(self, symbol: str) -> list:
        return []

    def F10(self, symbol: str, name: str) -> str:
        return ""

    def close(self) -> None:
        self.closed = True
        try:
            self._client.close()
        except Exception:
            pass


def create_eltdx_adapter() -> Optional[Any]:
    """创建 eltdx 适配器（pin 白名单主机，避免冷探测）。失败返回 None。"""
    try:
        from eltdx import TdxClient

        c = TdxClient(hosts=_ELTDX_HOSTS, probe_hosts=False, timeout=8.0)
        # 触发一次连接验证（取一只票快照，确保握手/主站可用）
        c.quotes.get_snapshots(["sh600519"])
        return _EltdxAdapter(c)
    except Exception as _e:
        _debug_log(f"eltdx adapter create error: {_e}")
        return None


def is_eltdx_available() -> bool:
    """V17.3: 轻量探测 eltdx 本地 TDX 适配层是否已安装。

    供 val 报告在 eltdx 依赖策略(26 连板梯队 / 27 短线资金强度)空产出时,
    区分'数据源缺失(本地 TDX 未连接 / eltdx 未装)'与'真实无符合标的',
    避免误导用户以为当日无连板/抢筹标的。
    """
    try:
        import eltdx  # noqa: F401
        return True
    except Exception:
        return False


def get_eltdx_shortline_bundle(all_codes: List[str], timeout: float = 20.0) -> Tuple[list, dict]:
    """eltdx 连板天梯(limit_ladder) + 批量短线指标(shortline_indicators) 一体化采集。

    V17.2.16: 供 val 策略层(策略26 连板梯队·短线封单强度)使用。
    数据: 本地 TDX 7709/7615 实时(TCP); 无本地 TDX / eltdx 未装 / 上游异常 / 卡死(墙钟超时)
          → 返回 ([], {}) 降级为空选, 不阻断其余策略。
    返回: (ladder_list, shortline_map)
      ladder_list:  list[dict]  —— limit_ladder() 全局连板天梯(rows)
      shortline_map: {ecode: dict} —— shortline_indicators(ecodes) 批量命中(ShortlineIndicator 41 字段)
    """
    from dataclasses import asdict, is_dataclass

    def _jfy(o):
        if isinstance(o, bytes):
            return o.hex()
        if isinstance(o, (list, tuple)):
            return [_jfy(x) for x in o]
        if isinstance(o, dict):
            return {str(k): _jfy(v) for k, v in o.items()}
        if is_dataclass(o) and not isinstance(o, type):
            return _jfy(asdict(o))
        if isinstance(o, (str, int, float, bool)) or o is None:
            return o
        return str(o)

    def _ecode(code: str) -> str:
        c = str(code)
        if c.startswith(("sh", "sz", "bj")):
            return c
        if c.startswith(("6", "5", "9", "11", "13")):
            return "sh" + c
        if c.startswith(("8", "4", "92")):
            return "bj" + c
        return "sz" + c  # 0/3/2/1 开头

    # 模块级缓存: 同进程同 codes 集合 300s 内复用 bundle, 避免 val 多策略/统一层重复连接 eltdx
    _ecodes = [_ecode(c) for c in all_codes]
    _ckey = frozenset(_ecodes)
    _cache = _SHORTLINE_BUNDLE_CACHE
    if _cache.get("key") == _ckey and (time.time() - _cache.get("ts", 0.0)) < _SHORTLINE_TTL:
        _cached = _cache.get("val")
        if _cached:
            return _cached

    def _work():
        try:
            from eltdx import TdxClient
        except Exception as _e:  # eltdx 未安装 → 下游策略降级为空选
            _debug_log(f"eltdx shortline bundle: import failed {_e}")
            return ([], {})
        client = None
        try:
            client = TdxClient(hosts=_ELTDX_HOSTS, probe_hosts=False, timeout=8.0)
            # ── 连板天梯(全局, 一次调用) ──
            ladder: list = []
            try:
                _ll = client.helpers.limit_ladder()
                _rows = getattr(_ll, "rows", None) or []
                ladder = [_jfy(r) for r in _rows]
            except Exception as _e:
                _debug_log(f"eltdx limit_ladder: {_e}")
            # ── 批量短线指标(按代码, 一次批量) ──
            ecodes = [_ecode(c) for c in all_codes]
            sl_map: dict = {}
            try:
                _sl = client.helpers.shortline_indicators(ecodes)
                _sl_rows = getattr(_sl, "rows", None)
                _sl_iter = _sl_rows if _sl_rows is not None else _sl
                for _rec in (_sl_iter or []):
                    _d = _jfy(_rec)
                    _cc = _d.get("code") or _d.get("full_code")
                    if _cc:
                        sl_map[_cc] = _d
            except Exception as _e:
                _debug_log(f"eltdx shortline_indicators: {_e}")
            return (ladder, sl_map)
        except Exception as _e:  # 连接/握手失败(无本地 TDX) → 降级
            _debug_log(f"eltdx shortline bundle: {_e}")
            return ([], {})
        finally:
            try:
                if client is not None:
                    client.close()
            except Exception:
                pass

    # 硬墙钟封顶: eltdx 在无本地 TDX 时连接阶段可能超出 timeout=8 长效挂起。
    # 用 daemon 线程 + join(timeout) 兜底(非 ThreadPoolExecutor: 其 __exit__ 的
    # shutdown(wait=True) 会阻塞等待挂起线程, 使超时失效)。daemon=True 保证进程退出不被拖住。
    import threading

    _result: dict = {"val": ([], {})}

    def _target():
        try:
            _result["val"] = _work()
        except Exception as _e:
            _debug_log(f"eltdx shortline bundle: {_e}")
            _result["val"] = ([], {})

    _t = threading.Thread(target=_target, daemon=True)
    _t.start()
    _t.join(timeout=timeout)
    if _t.is_alive():
        _debug_log(f"eltdx shortline bundle: 墙钟超时({timeout}s)降级为空选(无本地TDX/主站不可达)")
        return ([], {})
    _val = _result["val"]
    _ladder, _sl = _val
    # 仅缓存有效数据(非降级空选), 避免空选污染缓存导致 300s 内无法重试
    if _ladder or _sl:
        _SHORTLINE_BUNDLE_CACHE["key"] = _ckey
        _SHORTLINE_BUNDLE_CACHE["ts"] = time.time()
        _SHORTLINE_BUNDLE_CACHE["val"] = _val
    return _val


def get_eltdx_limit_ladder(timeout: float = 20.0) -> list:
    """eltdx 全局连板天梯(limit_ladder) —— 独立轻量接口，供市场级扫描(mak)使用。

    V17.2.24: 仅取全局梯队(一次调用)，不做 per-stock 批量 shortline_indicators
              （避免 mak 对全市场 5000+ 代码触发超时/拖慢整批）。
    数据: 本地 TDX 7709/7615 实时(TCP); 无本地 TDX / eltdx 未装 / 上游异常 / 卡死(墙钟超时)
          → 返回 [] 降级, 不阻断报告。
    返回: list[dict] —— 每行含 code/full_code/ladder_level/limit_up_streak_days/
          limit_board_text/seal_to_float_ratio/open_volume_ratio 等(ShortlineIndicator schema)。
    """
    from dataclasses import asdict, is_dataclass

    def _jfy(o):
        if isinstance(o, bytes):
            return o.hex()
        if isinstance(o, (list, tuple)):
            return [_jfy(x) for x in o]
        if isinstance(o, dict):
            return {str(k): _jfy(v) for k, v in o.items()}
        if is_dataclass(o) and not isinstance(o, type):
            return _jfy(asdict(o))
        if isinstance(o, (str, int, float, bool)) or o is None:
            return o
        return str(o)

    def _work():
        try:
            from eltdx import TdxClient
        except Exception as _e:
            _debug_log(f"eltdx limit_ladder: import failed {_e}")
            return []
        client = None
        try:
            client = TdxClient(hosts=_ELTDX_HOSTS, probe_hosts=False, timeout=8.0)
            _ll = client.helpers.limit_ladder()
            _rows = getattr(_ll, "rows", None) or []
            return [_jfy(r) for r in _rows]
        except Exception as _e:
            _debug_log(f"eltdx limit_ladder: {_e}")
            return []
        finally:
            try:
                if client is not None:
                    client.close()
            except Exception:
                pass

    import threading
    _result: dict = {"val": []}

    def _target():
        try:
            _result["val"] = _work()
        except Exception as _e:
            _debug_log(f"eltdx limit_ladder: {_e}")
            _result["val"] = []

    _t = threading.Thread(target=_target, daemon=True)
    _t.start()
    _t.join(timeout=timeout)
    if _t.is_alive():
        _debug_log(f"eltdx limit_ladder: 墙钟超时({timeout}s)降级为空(无本地TDX/主站不可达)")
        return []
    return _result["val"]


def get_eltdx_shortline_for_code(code: str, timeout: float = 20.0) -> Optional[Dict[str, Any]]:
    """从模块级 bundle 缓存读取单只股票的 eltdx 短线/连板指标(不触发取数)。

    V17.2.22: 供统一层 get_canonical_stock_data 暴露 eltdx 数据。
    仅当此前某处调用过 get_eltdx_shortline_bundle(all_codes) 预热缓存(批量, 300s TTL)时有效;
    否则返回 None —— 调用方应自行批量预热, 禁止 per-stock 触发取数(N+1 打爆 TDX TCP)。
    返回 dict 含: ladder_level / limit_up_streak_days / limit_board_text / seal_to_float_ratio /
    open_volume_ratio / seal_amount / opening_rush / auction_prev_volume_ratio /
    open_prev_amount_ratio / open_change_pct / open_turnover_z (ShortlineIndicator schema)。
    """
    c = str(code)
    if c.startswith(("sh", "sz", "bj")):
        ek = c
    elif c.startswith(("6", "5", "9", "11", "13")):
        ek = "sh" + c
    elif c.startswith(("8", "4", "92")):
        ek = "bj" + c
    else:
        ek = "sz" + c
    _cache = _SHORTLINE_BUNDLE_CACHE
    if _cache.get("key") is None or (time.time() - _cache.get("ts", 0.0)) >= _SHORTLINE_TTL:
        return None
    _val = _cache.get("val")
    if not _val:
        return None
    _ladder, _sl_map = _val
    rec: Dict[str, Any] = {}
    # 优先 sl_map(ShortlineIndicator 41 字段全量)
    _sl = _sl_map.get(ek) or _sl_map.get(code)
    if _sl:
        rec.update(_sl)
    # 连板天梯行按 code 匹配(兜底, 部分标的 sl_map 可能缺)
    if _ladder:
        for _r in _ladder:
            _rc = _r.get("code") or _r.get("full_code") or ""
            if _rc in (ek, code):
                rec.update(_r)
                break
    return rec if rec else None


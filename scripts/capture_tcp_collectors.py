"""Collectors backed by the local ZHB cache and TDX/TCP adapters.

Entry-point wrappers inject the handful of normalization helpers that remain
publicly patchable from ``capture_field_probe`` tests.
"""

from typing import Any, Callable, Dict, List, Optional

__all__ = [
    "collect_zhb",
    "collect_tdx",
    "collect_eltdx",
    "collect_tdx_f10",
    "collect_tdx_f10_more",
]


def collect_zhb(pool: list, resolve_name_fn: Callable[[str], Optional[str]]) -> dict:
    """读取 ZHB 全字段；本地缓存过期时由 get_zhb 按其规则尝试刷新。"""
    from core.zhb_client import (
        full_market_snapshot,
        market_stat_snapshot,
        market_stat2_snapshot,
        get_tip_info,
        get_zhb,
    )

    zhb = get_zhb()
    zhb_date = zhb.date if zhb is not None else ""
    full = full_market_snapshot([p["code"] for p in pool]) or {}
    stat = market_stat_snapshot([p["code"] for p in pool]) or {}
    stat2 = market_stat2_snapshot([p["code"] for p in pool]) or {}
    out: Dict[str, Any] = {"zhb_date": zhb_date, "stocks": {}}
    for p in pool:
        c = p["code"]
        tip = get_tip_info(c)
        out["stocks"][c] = {
            "name": resolve_name_fn(c),
            "full": full.get(c),
            "stat": stat.get(c),
            "stat2": stat2.get(c),
            "tipinfo": tip,
        }
    return out


def collect_tdx(
    pool: list,
    normalize_quote_fn: Callable[[Any], Optional[Dict[str, Any]]],
    has_populated_fn: Callable[[Any], bool],
) -> dict:
    """TDX 行情快照 + 财务(失败标的记 None,不中断)。

    字段探针使用 tdx_get_quote_raw，直接读取 TDX adapter 行情，不走
    tdx_get_quote_full 的 ZHB/Tencent 降级，也不复用其合成缓存；adapter
    顺序为 eltdx 优先、easy_tdx 兜底。财务数据仍经既有
    tdx_get_finance_info 读取。两项均为空时给该股票增加错误标记，避免
    把空响应计为成功采集。
    """
    from core.tdx_client import tdx_get_quote_raw, tdx_get_finance_info

    out: Dict[str, Any] = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec: Dict[str, Any] = {}
        missing_components = []
        try:
            rec["quote_raw"] = tdx_get_quote_raw(c)
        except Exception as e:
            rec["quote_raw"] = {"__error__": str(e)[:200]}
        rec["quote_full"] = normalize_quote_fn(rec["quote_raw"])
        if not has_populated_fn(rec["quote_full"]):
            missing_components.append("quote_full")
        # 显式暴露 TDX 快照直解字段(内盘/外盘/涨速)为顶层键，便于碰撞脚本纵向串联。
        # quote_full 只含 TDX adapter 返回值及其可复算行情量，不混入 ZHB/Tencent 回退值。
        _qf = rec["quote_full"]
        if isinstance(_qf, dict) and "__error__" not in _qf:
            for _k in ("s_vol", "b_vol", "rise_speed"):
                if _qf.get(_k) is not None:
                    rec[_k] = _qf[_k]
        try:
            rec["finance_info"] = tdx_get_finance_info(c)
        except Exception as e:
            rec["finance_info"] = {"__error__": str(e)[:200]}
        if not has_populated_fn(rec["finance_info"]):
            missing_components.append("finance_info")
        if missing_components:
            rec["__error__"] = "TDX returned no populated source fields for: " + ", ".join(
                missing_components
            )
        out["stocks"][c] = rec
    return out


def collect_eltdx(pool: list, failure_marker_fn: Callable[[Any], Any], lite: bool = False) -> dict:
    """eltdx 全字段采集（V17.2.15, 主字典第 24 源）。

    eltdx = Rust 内核通达信 7709/7615 客户端（PyPI 在线、零依赖、Research-Only 许可）。
    覆盖: 行情快照(含 tail_raw 原始帧尾字节) / 日K(含 record_hex 原始记录) / 市场统计
    (sh880005) / 0x0010 财务(含 finance_info_raw 原始块) / F10 新闻 / 短线指标
    (ShortlineIndicator 41 字段) / 全局 Helpers(连板天梯/题材强度排行/成交对比/买卖力道
    /实时排名)。
    返回「命名字段 + 原始字节」双轨, 供 collide.py 值级对撞 + 原始字节二次解码(见 D 步)。
    源 = 本地 eltdx TCP(非云连接器); 标注 scheme="eltdx" 独立血缘, 不动东财主路径。
    lite 模式(lite=True, 由 --eltdx-lite 触发): 跳过 kline_day/finance_batch
    (对撞未消费且与 TDX 源冗余), 仅保留
    quote_snapshot + shortline + 连板天梯——即 collide.py 真正消费的 eltdx 字段。
    注: lite 仅省次要载荷(实测 688.1s→668.5s, 约 2.8%); eltdx 采集主瓶颈是逐股
    get_snapshots RPC(≈33s/股), 已通过 L461 起「批量 get_snapshots(ecodes) 一次预取」
    彻底消解(20 次 RPC 往返→1 次), 与 eltdx shortline_indicators 批量 API 同源。
    """
    from dataclasses import asdict, is_dataclass
    from datetime import datetime as _dt

    def _jfy(o):
        """dataclass / datetime / bytes -> JSON 安全(字节统一转 hex)。"""
        if isinstance(o, bytes):
            return o.hex()
        if isinstance(o, (list, tuple)):
            return [_jfy(x) for x in o]
        if isinstance(o, dict):
            return {str(k): _jfy(v) for k, v in o.items()}
        if isinstance(o, _dt):
            return o.isoformat()
        if is_dataclass(o) and not isinstance(o, type):
            return _jfy(asdict(o))
        if isinstance(o, (str, int, float, bool)) or o is None:
            return o
        return str(o)

    def _ecode(code: str) -> str:
        c = str(code).lower()
        if c.startswith("sh92"):
            return "bj" + c[2:]
        if c.startswith(("sh", "sz", "bj")):
            return c
        if c.startswith(("92", "8", "4")):
            return "bj" + c
        if c.startswith(("6", "5", "9", "11", "13")):
            return "sh" + c
        return "sz" + c  # 0/3/2/1 开头

    def _is_bse(ec: str) -> bool:
        # 保留 sh92 识别以兼容旧数据；新请求始终将 92xxxx 映射为 bj 前缀。
        return ec.startswith("bj") or (ec.startswith("sh") and ec[2:].startswith("92"))

    # 注意: eltdx 客户端非线程安全, 任何 eltdx 调用放进后台线程都会死锁挂起;
    # 因此全程主线程直调, 不做线程超时护栏(护栏本身即死锁源)。挂起源靠"限定 codes 范围"消除。

    try:
        from eltdx import TdxClient
    except Exception as _e:
        return {"stocks": {}, "__error__": f"eltdx import failed: {str(_e)[:200]}"}

    client = None
    out: Dict[str, Any] = {"stocks": {}, "global_helpers": {}}
    try:
        # 默认探测主站(含 2026-09 新式握手); 单客户端复用(连接池)避免逐股重连。
        client = TdxClient(timeout=8)
        # 池代码(供全局 helpers 限域 + 逐股循环复用)
        codes = [p["code"] for p in pool]
        ecodes = [_ecode(c) for c in codes]
        _bse = [e for e in ecodes if _is_bse(e)]
        _a = [e for e in ecodes if e not in _bse]
        _gh = out["global_helpers"]
        # ── 全局 Helpers(仅处理本次池内代码) ──
        # V17.2.28 根因修正: limit_ladder/theme_strength_rank/stock_theme_strength_rank 默认 codes=None
        # 会扫描全市场 A 股(~5000 只)的 shortline_indicators + F10 主题查询, 单只 ~50ms 累积→~660s 挂起。
        # 修复: 显式传入本池 ecodes(仅 ~20 只)将工作量降到本池, 秒级完成; eltdx 调用一律主线程直调
        # (线程护栏会死锁非线程安全的客户端, 已废弃)。volume_comparison/buy_sell_strength 是逐股辅助
        # (需 code 参数), 不属于全局, 移除以免报错。
        _global_helpers: List[tuple[str, Callable[[], Any]]] = [
            ("limit_ladder", lambda: client.helpers.limit_ladder(codes=ecodes)),
            ("theme_strength_rank", lambda: client.helpers.theme_strength_rank(codes=ecodes)),
            (
                "stock_theme_strength_rank",
                lambda: client.helpers.stock_theme_strength_rank(codes=ecodes),
            ),
            ("realtime_rank", lambda: client.helpers.realtime_rank()),
            ("market_stat_880005", lambda: client.bars.get("sh880005", period="day", count=1)),
        ]
        for _name, _fn in _global_helpers:
            try:
                _gh[_name] = _jfy(_fn())
            except Exception as _e:
                _gh[_name] = failure_marker_fn(_e)
        # ── 逐股 ──
        # 短线指标(逐股, 41 字段/股) -> 命中映射(_sl_map); 主线程逐股直调
        # (实测 ~1.0s/股, A股与 BSE 均安全, BSE 快速报错不挂)。
        _sl_map = {}
        _sl_errors: Dict[str, dict] = {}
        # V17.2.28: 批量 shortline_indicators 进后台线程会死锁挂起, 且遇 BSE 坏码整批挂起;
        # 改用主线程逐股直调(实测 ~1.0s/股, A股与 BSE 均安全, BSE 快速报错不挂), 绝无挂起。
        for _ec in ecodes:
            try:
                _sl_one = client.helpers.shortline_indicators([_ec])
                # shortline_indicators 返回 ShortlineIndicatorTable(非 list); 须取 .rows 迭代,
                # 否则会遍历 dataclass 字段而非记录, 导致 shortline 永远挂不上。
                _matched = False
                for _rec in getattr(_sl_one, "rows", None) or []:
                    _recd = _jfy(_rec)
                    _cc = _recd.get("full_code") or _recd.get("code")
                    if _cc:
                        _reported = str(_cc).lower()
                        _reported_ec = _ecode(_reported)
                        if _reported_ec == _ec:
                            _sl_map[_ec] = _recd
                            _matched = True
                if not _matched:
                    _sl_errors[_ec] = {"__error__": "shortline response missing requested code"}
            except Exception as _e:
                _sl_errors[_ec] = failure_marker_fn(_e)
        # ── 行情快照(A股批量一次取全部, 避免逐股 RPC 往返) ──
        # A股、北交所分别批量请求：北交所必须使用 bj92xxxx 市场码，避免旧 sh92xxxx marker 错误。
        # 旧采集 688s 真正主因 = global_helpers 默认扫描全市场(~5000 只)→ 已改为限本池 ecodes。
        _snap_map = {}

        def _merge_snapshot_rows(snapshot_result: Any, requested_codes: List[str]) -> None:
            _batch_snaps = (
                getattr(snapshot_result, "snapshots", snapshot_result)
                if not isinstance(snapshot_result, list)
                else snapshot_result
            )
            if isinstance(_batch_snaps, dict):
                for _key, _value in _batch_snaps.items():
                    _snap_map[_ecode(str(_key))] = _value
            elif isinstance(_batch_snaps, (list, tuple)):
                for _index, _entry in enumerate(_batch_snaps):
                    _reported_code = (
                        getattr(_entry, "full_code", None)
                        or getattr(_entry, "code", None)
                        or (
                            _entry.get("full_code") or _entry.get("code")
                            if isinstance(_entry, dict)
                            else None
                        )
                    )
                    if _reported_code:
                        _snap_map[_ecode(str(_reported_code))] = _entry
                    elif _index < len(requested_codes):
                        _snap_map[requested_codes[_index]] = _entry

        if _a:
            try:
                _batch = client.quotes.get_snapshots(_a)
                _merge_snapshot_rows(_batch, _a)
            except Exception as _e:
                # A股批量失败(罕见)→ 降级逐股保住快照(挂起风险已由 BSE 隔离消除)
                out["snapshot_error"] = f"A-share batch failed, fallback per-code: {str(_e)[:120]}"
                for _ec in _a:
                    try:
                        _s = client.quotes.get_snapshots([_ec])
                        _merge_snapshot_rows(_s, [_ec])
                        if _ec not in _snap_map:
                            _snap_map[_ec] = {"__error__": "snapshot request returned no record"}
                    except Exception as _single_error:
                        _snap_map[_ec] = {"__error__": str(_single_error)[:200]}
        if _bse:
            try:
                _bse_batch = client.quotes.get_snapshots(_bse)
                _merge_snapshot_rows(_bse_batch, _bse)
            except Exception as _e:
                out["bse_snapshot_error"] = f"BSE batch failed, fallback per-code: {str(_e)[:120]}"
                for _ec in _bse:
                    try:
                        _snapshot = client.quotes.get_snapshots([_ec])
                        _merge_snapshot_rows(_snapshot, [_ec])
                        if _ec not in _snap_map:
                            _snap_map[_ec] = {"__error__": "snapshot request returned no record"}
                    except Exception as _single_error:
                        _snap_map[_ec] = {"__error__": str(_single_error)[:200]}
        for p in pool:
            c = p["code"]
            ec = _ecode(c)
            rec: Dict[str, Any] = {}
            # 行情快照(含 tail_raw 原始帧尾) —— 已由批量 _snap_map 预取
            try:
                if ec in _snap_map:
                    _snapshot = _jfy(_snap_map[ec])
                    rec["quote_snapshot"] = (
                        _snapshot
                        if _snapshot is not None
                        else {"__error__": "snapshot batch returned an empty record"}
                    )
                else:
                    try:
                        _snap = client.quotes.get_snapshots([ec])
                        _merge_snapshot_rows(_snap, [ec])
                        rec["quote_snapshot"] = (
                            _jfy(_snap_map[ec])
                            if ec in _snap_map
                            else {"__error__": "snapshot request returned no record"}
                        )
                    except Exception as _e:
                        rec["quote_snapshot"] = {"__error__": str(_e)[:200]}
            except Exception as _e:
                rec["quote_snapshot"] = {"__error__": str(_e)[:200]}
            # 日K(最新若干根 + record_hex 原始记录) —— lite 模式跳过(与 tdx 源冗余, 对撞未消费)
            if not lite:
                try:
                    _ks = client.bars.get(ec, period="day", count=5, include_raw=True)
                    _bars = getattr(_ks, "bars", None) or []
                    rec["kline_day"] = [_jfy(b) for b in _bars]
                except Exception as _e:
                    rec["kline_day"] = {"__error__": str(_e)[:200]}
            # 0x0010 财务(含 finance_info_raw 原始块) —— lite 模式跳过(与 tdx 源冗余, 对撞未消费)
            if not lite:
                try:
                    _fb = client.corporate.finance_batch(ec, include_raw=True)
                    _recs = getattr(_fb, "records", None) or []
                    rec["finance_batch"] = [_jfy(r) for r in _recs]
                except Exception as _e:
                    rec["finance_batch"] = {"__error__": str(_e)[:200]}
            # 短线指标(命中)
            if ec in _sl_map:
                rec["shortline"] = _sl_map[ec]
            elif ec in _sl_errors:
                rec["shortline"] = _sl_errors[ec]
            else:
                rec["shortline"] = {"__error__": "shortline response missing requested code"}
            out["stocks"][c] = rec
        # V17.2.25: 全局连板天梯(global_helpers.limit_ladder) 折回逐股结构, 使 collide.py
        # (只读 stocks 逐股) 能消费 eltdx 特有连板字段(ladder_level/limit_up_streak_days/
        # seal_to_float_ratio/open_volume_ratio/limit_board_text)。匹配键=plain code。
        _ll = _gh.get("limit_ladder", {})
        _ll_rows = _ll.get("rows") if isinstance(_ll, dict) else None
        if _ll_rows:
            for _row in _ll_rows:
                _rc = _row.get("code") or _row.get("full_code")
                _rc_plain = (
                    _rc[2:] if isinstance(_rc, str) and _rc[:2] in ("sh", "sz", "bj") else _rc
                )
                if _rc_plain in out["stocks"]:
                    out["stocks"][_rc_plain]["limit_ladder"] = _jfy(_row)
                elif _rc in out["stocks"]:
                    out["stocks"][_rc]["limit_ladder"] = _jfy(_row)
    finally:
        try:
            if client is not None:
                client.close()
        except Exception:
            pass
    return out


def collect_tdx_f10(pool: list) -> dict:
    """TDX F10 财务九件套补充: 财务分析/股本/分红(TCP,免费)。"""
    from core.tdx_client import (
        tdx_get_financial_analysis,
        tdx_get_share_capital,
        tdx_get_dividend_history,
    )

    out: Dict[str, Any] = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec: Dict[str, Any] = {}
        for name, fn in [
            ("financial_analysis", tdx_get_financial_analysis),
            ("share_capital", tdx_get_share_capital),
            ("dividend_history", tdx_get_dividend_history),
        ]:
            try:
                rec[name] = fn(c)
            except Exception as e:
                rec[name] = {"__error__": str(e)[:150]}
        out["stocks"][c] = rec
    return out


def collect_tdx_f10_more(pool: list) -> dict:
    """TDX F10 补充: 股东研究/公司新闻/异动提醒(TCP 免费)。"""
    from core.tdx_client import (
        tdx_get_shareholder_research,
        tdx_get_company_news_f10,
        tdx_get_latest_reminders,
    )

    out: Dict[str, Any] = {"stocks": {}}
    for p in pool:
        c = p["code"]
        rec: Dict[str, Any] = {}
        for name, fn in [
            ("shareholder_research", tdx_get_shareholder_research),
            ("company_news", lambda x: tdx_get_company_news_f10(x, count=10)),
            ("reminders", tdx_get_latest_reminders),
        ]:
            try:
                rec[name] = fn(c)
            except Exception as e:
                rec[name] = {"__error__": str(e)[:150]}
        out["stocks"][c] = rec
    return out

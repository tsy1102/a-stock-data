"""_misc.py — V17.2 拆包子模块（共享命名空间片段，由 __init__ 载入）

本文件不是独立可导入模块；其源码被 stock_common/sc_datasource/__init__.py
exec 进包命名空间，与包内其他函数/状态共享同一 globals()。
"""

import datetime
from stock_common.sc_network import UA, _debug_log
from stock_common.sc_utils import TTL, cached


import datetime
from stock_common.sc_network import UA, _debug_log
from stock_common.sc_utils import TTL, cached


def _tdx_root() -> str:
    """TDX 安装根目录（M12 修复：原代码硬编码 C:\\new_tdx64，非该安装路径的机器直接 FileNotFoundError）。

    优先读取环境变量 TDX_HOME / TDX_ROOT，缺省回退 C:\\new_tdx64 以保持兼容。
    """
    return os.environ.get("TDX_HOME") or os.environ.get("TDX_ROOT") or r"C:\new_tdx64"


def get_historical_high_qfq(code: str, count: int = 640) -> Optional[float]:
    """V17.0.5 P2: 历史最高价（腾讯前复权日线, ~640 根≈2.6 年窗口）。

    参考仓库 v3.7.0/3.2.5#28 同源问题修复: TDX bars 为不复权原始价,
    长期分红股跨除权比较会低估真实回撤。qfq 口径与现价同基准可直接比。
    接口: web.ifzq.gtimg.cn fqkline(字典 §12.1 备胎——免费无鉴权, 与 TDX 实测一致)。
    """
    from stock_common.sc_network import _quick_request

    mkt = "bj" if code.startswith(("92", "8", "4", "43", "83", "87")) else (
        "sh" if code.startswith(("6", "9", "5")) else "sz")
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    try:
        r = _quick_request(
            url,
            params={"param": f"{mkt}{code},day,,,{count},qfq"},
            headers={"Referer": "https://gu.qq.com/"},
            timeout=10,
        )
        if r is None:
            return None
        d = (r.json() or {}).get("data") or {}
        node = d.get(f"{mkt}{code}") or {}
        days = node.get("qfqday") or node.get("day") or []
        highs = [float(row[3]) for row in days if len(row) > 3 and float(row[3]) > 0]
        return max(highs) if highs else None
    except Exception as _e:
        _debug_log(f"datasource historical_high_qfq ({code}): {_e}")
        return None


def _today_str() -> str:
    """当日 YYYYMMDD(缓存日期口径用)."""
    import datetime as _dt

    return _dt.date.today().strftime("%Y%m%d")


def _query_dt_pool_tc(date_str: str = "") -> Optional[int]:
    """V17.0.8: 东财 getTopicDTPool 的 tc 权威总数——pool 明细可能为空但 tc>0。
    用于 get_limit_pool_summary 跌停兜底（替代会读到 T-1 的 ZHB 快照）。"""
    if not date_str:
        from datetime import datetime

        date_str = datetime.now().strftime("%Y%m%d")
    url = "https://push2ex.eastmoney.com/getTopicDTPool"
    params = {
        "ut": "7eea3edcaed734bea9cbfc24409ed989",
        "dpt": "wz.ztzt",
        "Pageindex": 0,
        "pagesize": 100,
        "sort": "fbt:asc",
        "date": date_str,
    }
    try:
        r = _quick_request(url, params=params, headers={"User-Agent": UA}, timeout=10)
        if r is None:
            return None
        d = r.json()
        tc = (d.get("data") or {}).get("tc")
        return int(tc) if tc is not None else None
    except Exception as _e:
        _debug_log(f"datasource dt pool tc: {_e}")
        return None


def get_tdx_day_tail(code: str) -> Dict[str, Any]:
    """V17.0.1d(2026-08-16): TDX 本机 .day 尾部快速读(零网络毫秒级).

    新版 .day 32B 记录: date<uint32> + open/high/low/close<int32×0.01元(分)> +
    amount<float32 元> + volume<int32 股> + reserved。
    返回 {price, open, high, low, amount_wan, date}。
    ⚠️ C1 终审修复(2026-08-15): 价格刻度 ÷1000→÷100(实测 600519 close=134199→1341.99)。
    用途: 休市/盘前 canonical OHLC/成交额缺口兜底(与 TDX 快照同源, 零网络)。
    """
    try:
        import os as _os
        import struct as _st

        _mkt = "bj" if code.startswith(("92", "8", "4", "43", "83", "87")) else ("sh" if code.startswith(("6", "9")) else "sz")
        _path = _os.path.join(_tdx_root(), "vipdoc", _mkt, "lday", f"{_mkt}{code}.day")
        with open(_path, "rb") as _f:
            _f.seek(-32, 2)
            _rec = _f.read(32)
        if len(_rec) < 32:
            return {}
        _date = _st.unpack_from("<I", _rec, 0)[0]
        _open = _st.unpack_from("<I", _rec, 4)[0] / 100.0
        _high = _st.unpack_from("<I", _rec, 8)[0] / 100.0
        _low = _st.unpack_from("<I", _rec, 12)[0] / 100.0
        _close = _st.unpack_from("<I", _rec, 16)[0] / 100.0
        if _close <= 0:
            return {}
        _amount = _st.unpack_from("<f", _rec, 20)[0]  # 元
        _volume = _st.unpack_from("<I", _rec, 24)[0]  # 股
        return {
            "price": _close,
            "open": _open,
            "high": _high,
            "low": _low,
            "amount_wan": (_amount / 1e4) if _amount and _amount > 0 else 0.0,
            "volume_hand": (_volume / 100.0) if _volume and _volume > 0 else 0.0,
            "date": _date,
        }
    except Exception as _e:
        _debug_log(f"get_tdx_day_tail ({code}): {_e}")
        return {}


def get_share_capital(code: str) -> Dict[str, Any]:
    """V10.1: 获取单只股票的股本数据（总股本、流通股）。

    Returns:
        {"total_shares": float, "float_shares": float, "updated_at": str}
        单位：万股
    """
    try:
        from stock_common.sc_capital_cache import get_share_capital as _get_cap

        return _get_cap(code)
    except Exception as _e:
        _debug_log(f"datasource share_capital ({code}): {_e}")
        return {"total_shares": 0, "float_shares": 0, "updated_at": ""}


def calc_mcap_yi(code: str, price: float) -> float:
    """V10.1: 计算总市值（亿元）。

    Args:
        code: 股票代码
        price: 现价（元）

    Returns:
        总市值（亿元），失败返回0
    """
    try:
        from stock_common.sc_capital_cache import calc_mcap_yi as _calc

        return _calc(code, price)
    except Exception as _e:
        _debug_log(f"datasource calc_mcap_yi ({code}): {_e}")
        return 0.0


def calc_float_mcap_yi(code: str, price: float) -> float:
    """V10.1: 计算流通市值（亿元）。

    Args:
        code: 股票代码
        price: 现价（元）

    Returns:
        流通市值（亿元），失败返回0
    """
    try:
        from stock_common.sc_capital_cache import calc_float_mcap_yi as _calc

        return _calc(code, price)
    except Exception as _e:
        _debug_log(f"datasource calc_float_mcap_yi ({code}): {_e}")
        return 0.0


def print_batch_summary(results, total):
    """批量执行结果汇总打印。

    Args:
        results: 结果列表，每项应为 {"code": str, "status": str, "error": str}。
        total: 总股票数量。
    """
    ok = [r for r in results if r["status"] == "成功"]
    fd = [r for r in results if r["status"] == "数据失败"]
    fg = [
        r
        for r in results
        if r["status"] in ("GD上传失败", "GD上传异常", "GD文件夹失败", "GD未连接")
    ]
    print(f"\n{'=' * 60}")
    print(f"  批量执行完成 — 共处理 {total} 只股票")
    print(f"{'=' * 60}")
    print(f"  ✅ 全部成功: {len(ok)}  |  ❌ 数据失败: {len(fd)}  |  ⚠️ GD上传失败: {len(fg)}")


@cached(category="market_emotion", ttl_seconds=TTL["limit_pool"], trading_day=True)
def get_cls_market_emotion() -> Dict[str, Any]:
    """V16.1.7: 财联社市场情绪（字典 §12.10.2，实测可用）。

    返回: market_degree(热度0-100)/shsz_balance(两市成交额)/up_ratio(封板率)/
          up_open_num(炸板)/performance(昨涨停今表现)/up_open_ratio(高开率)/
          profit_ratio(获利率)/up_down_dis(涨跌分布)/limit_up_board(连板梯队)
    """
    try:
        import levistock as lk
        # V16.2: levistock 内部直连东财，绕过统一限流 → 调用前走进程级协调（全局 ≤1 rps）
        try:
            from stock_common.sc_network import _em_wait_process_interval
            _em_wait_process_interval()
        except Exception:
            pass
        d = lk.market_emotion_cls()
        if isinstance(d, dict) and d:
            return d
    except Exception as _e:
        _debug_log(f"datasource get_cls_market_emotion: {_e}")
    return {}


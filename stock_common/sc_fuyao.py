"""sc_fuyao.py — 同花顺官方金融数据 REST API（fuyao.aicubes.cn）统一适配器

V16.3.3 新增：官方 REST 通道（字典 §12.8.12c）——Key 交互引导 + 跳过禁用逻辑。

Key 获取优先级：
    1. 环境变量 THS_FUYAO_API_KEY（推荐，CI/长期使用）
    2. 项目根 fuyao_key.txt（交互输入后自动保存，已 gitignore）
    3. 交互式引导（ensure_fuyao_key）——无 Key 时提供两个选项：
       a. 粘贴新 Key → 自动验证（meta/tickers/search）→ 保存 → 继续
       b. 跳过 → 本进程禁用 fuyao（_FUYAO_DISABLED=True），后续调用自动返回 None

协议（字典 §12.8.12c）：
    Base https://fuyao.aicubes.cn，全 GET，头 X-api-key
    成功 = HTTP 200 且 code==0；信封 {code, message, request_id, data}（data.item 数组）
    错误码：4001 限流（调用方退避）；Key 无效 2003
    限流：fuyao.aicubes.cn 已入 sc_network._DOMAIN_LIMITS（500ms/2rps）
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from stock_common.sc_network import _quick_request, _debug_log

# V16.3.3: fuyao 数据缓存（字典 12.15.5 新源充实后——避免每次网络请求消耗 Key 配额/限流）
# V17.0 S8: 删 _fuyao_cached 适配器(与 _kpl_cached 逐字重复)——直接使用规范 cached
try:
    from core.stock_cache import cached, TTL

    _HAS_CACHE = True
except ImportError:  # pragma: no cover
    _HAS_CACHE = False

_logger = logging.getLogger("fuyao_adapter")

_REPO_ROOT = Path(__file__).resolve().parent.parent
_KEY_FILE = _REPO_ROOT / "fuyao_key.txt"

_BASE = "https://fuyao.aicubes.cn"

# 本进程禁用标记（ensure_fuyao_key 选择"跳过"后置 True——后续调用自动返回 None）
_FUYAO_DISABLED = False
# 已缓存的有效 Key
_CACHED_KEY: Optional[str] = None

# 常用端点路径（字典 §12.8.12c 31 端点子集——按业务接入优先级）
EP_SNAPSHOT = "/api/a-share/prices/snapshot"
EP_KLINE = "/api/a-share/prices/historical"
EP_VALUATION = "/api/a-share/valuations/snapshot"
EP_LIMIT_UP_LADDER = "/api/a-share/special-data/limit-up-ladder"
EP_HOT_LIST = "/api/a-share/special-data/hot-stock-list"
EP_DRAGON_TIGER = "/api/a-share/special-data/dragon-tiger-list"
EP_TICKER_SEARCH = "/api/meta/tickers/search"


def is_fuyao_enabled() -> bool:
    """fuyao 是否可用（未被跳过且 Key 可解析）。"""
    return not _FUYAO_DISABLED and get_fuyao_key() is not None


def get_fuyao_key() -> Optional[str]:
    """解析 Key：环境变量 → fuyao_key.txt → None。不触发交互。"""
    global _CACHED_KEY
    if _CACHED_KEY:
        return _CACHED_KEY
    env = os.environ.get("THS_FUYAO_API_KEY", "").strip()
    if env:
        _CACHED_KEY = env
        return env
    if _KEY_FILE.is_file():
        k = _KEY_FILE.read_text(encoding="utf-8").strip()
        if k:
            _CACHED_KEY = k
            return k
    return None


def _print_guide() -> None:
    """打印获取 API Key 的指导。"""
    print("=" * 60)
    print("  🔑 同花顺金融数据 API（fuyao）未配置 Key")
    print("=" * 60)
    print("  获取步骤（约 1 分钟）：")
    print("    1. 打开 https://fuyao.aicubes.cn/ ，用同花顺账号登录")
    print("    2. 进入「API Key 管理」页：https://fuyao.aicubes.cn/admin")
    print("    3. 点击「创建 API Key」，填写别名（如 a-stock-data）")
    print("    4. 复制弹出的 Key（形如 sk-fuyao-xxxxxxxx，只显示一次）")
    print("")
    print("  也可设置环境变量 THS_FUYAO_API_KEY 后重启脚本。")
    print("=" * 60)


def _interactive_acquire(stdin: Any = None) -> Optional[str]:
    """交互获取 Key 的核心循环（可注入 stdin 便于测试）。

    返回: 有效 Key / None（跳过）。stdin 缺省 sys.stdin。
    """
    global _FUYAO_DISABLED, _CACHED_KEY
    _print_guide()
    inp = stdin if stdin is not None else sys.stdin
    while True:
        try:
            line = inp.readline() if hasattr(inp, "readline") else input()
            if not line:
                raise EOFError
            choice = line.strip()
        except (EOFError, KeyboardInterrupt):
            choice = "2"
        if choice == "1":
            new_key = input("  粘贴 API Key: ").strip() if stdin is None else inp.readline().strip()
            if not new_key:
                print("  ⚠️ 输入为空，请重试（或选 2 跳过）")
                continue
            if _verify_key(new_key):
                _save_key(new_key)
                _CACHED_KEY = new_key
                print("  ✅ Key 验证通过，已保存到 fuyao_key.txt（gitignore）")
                return new_key
            print("  ❌ Key 验证失败（可能无效或未授权），请检查后重试（或选 2 跳过）")
        elif choice == "2":
            _FUYAO_DISABLED = True
            _debug_log("fuyao: 用户选择跳过——本进程禁用 fuyao 接口")
            print("  ℹ️ 已跳过——本进程后续 fuyao 接口自动返回空（下次运行可再配置）")
            return None
        else:
            print("  ⚠️ 无效选择，请输入 1 或 2")


def ensure_fuyao_key(interactive: bool = True, stdin: Any = None) -> Optional[str]:
    """确保 fuyao Key 可用。

    - 已配置（env/文件）→ 直接返回
    - 未配置且 interactive=True → 打印指导，用户二选一：
        1) 粘贴新 Key（自动验证并保存到 fuyao_key.txt）→ 返回 Key
        2) 跳过 → 本进程禁用 fuyao，返回 None
      （stdin 可注入用于测试；非交互终端无输入时自动跳过，不阻塞）
    - 未配置且 interactive=False → 返回 None（不打扰）
    """
    global _FUYAO_DISABLED, _CACHED_KEY
    if _FUYAO_DISABLED:
        return None
    k = get_fuyao_key()
    if k:
        return k
    if not interactive:
        return None
    _inp = stdin if stdin is not None else sys.stdin
    if _inp is None or not hasattr(_inp, "isatty") or not _inp.isatty():
        # 非交互终端（子进程管道/CI）——尝试读管道输入；无输入则自动跳过，不阻塞
        if stdin is None:
            try:
                import msvcrt  # Windows 控制台按键检测

                if not msvcrt.kbhit():
                    _debug_log("fuyao: 非交互终端且无输入，自动跳过 Key 引导")
                    _FUYAO_DISABLED = True
                    return None
            except Exception:
                _debug_log("fuyao: 非交互终端，自动跳过 Key 引导")
                _FUYAO_DISABLED = True
                return None
    return _interactive_acquire(stdin=_inp)


def _save_key(key: str) -> None:
    """保存 Key 到项目根 fuyao_key.txt（已 gitignore）。"""
    try:
        _KEY_FILE.write_text(key.strip(), encoding="utf-8")
    except Exception as _e:
        _debug_log(f"fuyao: 保存 Key 失败: {_e}")


def _verify_key(key: str) -> bool:
    """验证 Key：meta/tickers/search 一次请求（code==0 即有效）。"""
    try:
        resp = _fuyao_raw("/api/meta/tickers/search", {"q": "600519", "limit": 1}, key=key)
        return resp is not None and resp.get("code") == 0
    except Exception as _e:
        _debug_log(f"fuyao: Key 验证异常: {_e}")
        return False


def _fuyao_raw(
    path: str, params: Optional[Dict[str, Any]] = None, key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """统一请求（走 sc_network._quick_request 域限流）。失败返回 None。"""
    k = key or get_fuyao_key()
    if not k:
        return None
    try:
        headers = {"X-api-key": k, "User-Agent": "Mozilla/5.0"}
        r = _quick_request(_BASE + path, params=params, headers=headers, timeout=15)
        if r is None:
            _debug_log(f"fuyao: 请求被限流/拒绝 {path}")
            return None
        if r.status_code != 200:
            _debug_log(f"fuyao: HTTP {r.status_code} {path}")
            return None
        d = r.json()
        if d.get("code") != 0:
            _debug_log(f"fuyao: code={d.get('code')} msg={d.get('message')} {path}")
            if d.get("code") in (2001, 2003):
                _debug_log("fuyao: Key 无效——请重新配置（删除 fuyao_key.txt 或更新环境变量）")
            return d
        return d
    except Exception as _e:
        _debug_log(f"fuyao: 请求异常 {path}: {_e}")
        return None


def _items(d: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """提取信封 data.item（兼容 dict 嵌套）。"""
    if not d:
        return []
    data = d.get("data") or {}
    if isinstance(data, list):
        return data
    items = data.get("item") or []
    return items if isinstance(items, list) else []


def fuyao_to_thscode(code: str) -> str:
    """项目 6 位代码 → thscode（600519→600519.SH / 000001→000001.SZ / 8xx/4xx→BJ）。"""
    code = code.strip()
    if code.endswith((".SH", ".SZ", ".BJ")):
        return code
    if code.startswith(("6", "9")):
        return f"{code}.SH"
    if code.startswith(("8", "4", "92")):
        return f"{code}.BJ"
    return f"{code}.SZ"


@cached("fuyao_snapshot", "fuyao_snapshot")
def get_fuyao_snapshot(codes: List[str]) -> List[Dict[str, Any]]:
    """行情快照（EP_SNAPSHOT）。无 Key/已跳过 → 空列表。"""
    if not codes:
        return []
    ths = ",".join(fuyao_to_thscode(c) for c in codes)
    return _items(_fuyao_raw(EP_SNAPSHOT, {"thscodes": ths}))


@cached("fuyao_valuation", "fuyao_valuation")
def get_fuyao_valuation(codes: List[str]) -> List[Dict[str, Any]]:
    """估值快照（pe_ttm/pe_mrq/pb_mrq/ps_ttm/pcf_ttm）。"""
    if not codes:
        return []
    ths = ",".join(fuyao_to_thscode(c) for c in codes)
    return _items(_fuyao_raw(EP_VALUATION, {"thscodes": ths}))


def get_fuyao_kline(
    thscode: str,
    interval: str = "1d",
    start_ms: Optional[int] = None,
    end_ms: Optional[int] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """历史 K线（EP_KLINE）。interval: 1d/1w/1m/5m/15m/30m/60m。"""
    params: Dict[str, Any] = {
        "thscode": fuyao_to_thscode(thscode),
        "interval": interval,
        "limit": limit,
    }
    if start_ms:
        params["start"] = start_ms
    if end_ms:
        params["end"] = end_ms
    return _items(_fuyao_raw(EP_KLINE, params))


@cached("fuyao_ladder", "fuyao_ladder", trading_day=True)
def get_fuyao_limit_up_ladder() -> Optional[Dict[str, Any]]:
    """涨停梯队（date + boards 连板分类——独有结构，字典 §12.8.12c）。"""
    d = _fuyao_raw(EP_LIMIT_UP_LADDER)
    return (d.get("data") or {}) if d and d.get("code") == 0 else None


def get_fuyao_hot_list(period: str = "hour") -> List[Dict[str, Any]]:
    """热股榜（period: hour/day/week）。"""
    return _items(_fuyao_raw(EP_HOT_LIST, {"period": period}))


def get_fuyao_dragon_tiger(trade_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """龙虎榜（trade_date 可选 YYYY-MM-DD）。"""
    params = {}
    if trade_date:
        params["trade_date"] = trade_date
    return _items(_fuyao_raw(EP_DRAGON_TIGER, params))


if __name__ == "__main__":
    # 自检：Key 状态 + 一次真实查询（不打印 Key）
    k = ensure_fuyao_key()
    if k:
        print(
            "Key 状态: 已配置（来源:",
            "环境变量" if os.environ.get("THS_FUYAO_API_KEY") else "fuyao_key.txt",
            ")",
        )
        snap = get_fuyao_snapshot(["600519"])
        if snap:
            print(f"实测行情快照: 茅台 last_price={snap[0].get('last_price')}")
        else:
            print("实测行情快照: 空（检查 Key/网络）")
    else:
        print("Key 状态: 未配置或已跳过")

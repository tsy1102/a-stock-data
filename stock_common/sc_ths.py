"""sc_ths.py — 同花顺 THS SDK 统一适配器（V16.3 O30 新增）。

凭证模式（参照 GD credentials.json）：
    1. 环境变量：THS_USERNAME / THS_PASSWORD / THS_MAC（最高优先，SDK 原生支持）
    2. 配置文件：ths_credentials.json（仓库根目录，已 gitignore，格式见下）
    3. 游客兜底：SDK 内置 thsguest_* 随机账号（仅测试，随时可能失效）

ths_credentials.json 格式：
    {"username": "your_user", "password": "your_pass", "mac": "aa:bb:cc:dd:ee:ff"}

协议说明：
    - TCP 连接同花顺官方行情服务器（非 HTTP 反爬面，不触发 401）
    - 限流实测（2026-08-09 游客）：1s 间隔 × 50 次全部成功；生产建议 1.5-2s 间隔
    - 批量查询务必 sleep 间隔，勿高频循环
"""
from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

_logger = logging.getLogger("ths_adapter")

_REPO_ROOT = Path(__file__).resolve().parent.parent
# V17.0: 凭据集中到 credentials/ 子目录
_CFG_PATH = _REPO_ROOT / "credentials" / "ths_credentials.json"

# 实测限流参考（2026-08-09）：游客 1s×50 全过 → 保守间隔
QUERY_INTERVAL = 1.5


def _is_placeholder(value: Optional[str]) -> bool:
    """占位符检测（模板值未替换时跳过，回退游客）。"""
    if not value:
        return True
    return value.strip().upper().startswith("YOUR_")


def get_ths_credentials() -> Optional[Dict[str, str]]:
    """读取 THS 账号：环境变量 → 配置文件 → None（游客兜底由 SDK 处理）。"""
    username = os.environ.get("THS_USERNAME")
    password = os.environ.get("THS_PASSWORD")
    if username and password and not _is_placeholder(username) and not _is_placeholder(password):
        return {"username": username, "password": password,
                "mac": os.environ.get("THS_MAC", "")}
    try:
        if _CFG_PATH.exists():
            cfg = json.loads(_CFG_PATH.read_text(encoding="utf-8"))
            if cfg.get("username") and cfg.get("password") \
                    and not _is_placeholder(cfg["username"]) and not _is_placeholder(cfg["password"]):
                return {"username": cfg["username"], "password": cfg["password"],
                        "mac": cfg.get("mac", "")}
    except Exception as _e:
        _logger.warning(f"ths_credentials.json 读取失败: {_e}")
    return None


def get_ths_client(ops: Optional[Dict[str, Any]] = None):
    """创建 THS 客户端（账号优先，游客兜底）。用法：with get_ths_client() as ths: ..."""
    from thsdk import THS

    creds = get_ths_credentials()
    if creds:
        _logger.info("THS 使用正式账号")
        ops = dict(ops or {})
        ops.update(creds)
    return THS(ops)


def query_with_interval(method: str, *args, interval: float = QUERY_INTERVAL, **kwargs):
    """限流封装：单次查询 + 固定间隔（批量循环时手动 sleep 更可控）。"""
    from thsdk import THS

    with get_ths_client() as ths:
        resp = getattr(ths, method)(*args, **kwargs)
        time.sleep(interval)
        return resp


# ═══════════════════════════════════════════════════════════════
# V16.3 O35: 统一层入口（字典 §12.8.12b 字段核实结论）
# ═══════════════════════════════════════════════════════════════

def get_ths_market_snapshot(codes: list) -> dict:
    """THS 实时快照：market_data_cn "扩展1" query_key（2026-08-11 实测：原"盘面"字段集已改版，
    市净率等估值字段已不在其中；扩展1 含 市净率/市盈率TTM/主力净流入/量比/换手 等估值+资金字段）。
    覆盖 PB/PE/资金流核心字段。
    PE TTM/5日涨幅/流通市值/总市值/委比/涨速/当前量/振幅/主力净量/主力净流入/
    昨收/涨停价/跌停价/最高/最低/开盘涨幅——**PB 需扩展1（市净率 3 变体）**

    单次连接批量查询（正式账号实测 30 次连续无限频；游客限 20ms/次）。
    返回 {code: {字段: 值}}——仅含非空值。
    """
    from thsdk import THS

    if not codes:
        return {}
    codes = list(codes)
    out: dict = {}
    with get_ths_client() as ths:
        for i in range(0, len(codes), 50):  # 分批（单次最多 100 只）
            batch = codes[i : i + 50]
            for code in batch:
                try:
                    r = ths.market_data_cn(code, query_key="扩展1")
                    if r.success and r.data:
                        d = {k: v for k, v in r.data[0].items()
                             if v not in (None, "", 4294967295, 2147483648)}
                        out[code] = d
                except Exception as _e:
                    _logger.warning(f"ths snapshot {code}: {_e}")
                time.sleep(0.1)  # 正式账号实测无限频；保守 0.1s
    return out


def get_ths_pb(code: str) -> Optional[float]:
    """THS 市净率（扩展1 query_key——市净率 3 变体同值）。

    ZHB 无 PB——ths 可补（字典 §12.8.12b：茅台 6.05/工行 0.68 实测合理）。
    """
    from thsdk import THS

    with get_ths_client() as ths:
        try:
            r = ths.market_data_cn(code, query_key="扩展1")
            if r.success and r.data:
                # 市净率 3 变体（2947/592920/1149395 同值）——匹配"市净率"前缀
                pb = None
                for k, v in r.data[0].items():
                    if k.startswith("市净率") and v not in (None, "", 4294967295, 2147483648):
                        pb = v
                        break
                return float(pb) if pb is not None else None
        except Exception as _e:
            _logger.warning(f"ths pb {code}: {_e}")
    return None


if __name__ == "__main__":
    # 自检：打印凭证来源（不打印密码）
    c = get_ths_credentials()
    print("凭证来源:", "环境变量/配置文件" if c else "游客兜底")
    if c:
        print("账号:", c["username"])
    from thsdk import THS

    with get_ths_client() as ths:
        r = ths.search_symbols("600519")
        print("自检查询:", r.success, r.data[:1] if r.data else r.error)

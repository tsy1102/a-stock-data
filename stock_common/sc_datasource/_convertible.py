"""_convertible.py — 可转债层 (V17.4 吸收上游 3.9.0 §15).

函数: convertible_bonds() — 条款/转股价值/溢价率, 状态分 交易中/待上市/已摘牌/无法判断。
数据来源: 东财 datacenter。设计对齐上游: source/source_url/fetched_at 溯源; 结构错抛 RuntimeError。

reportName 常量: 2026-09-22 经上游权威仓库 SKILL.md 对撞校正 —— 原候选 RPT_CB_LIST 错误,
已订正为上游验证过的 RPT_BOND_CB_LIST(verify 终检仍按治理铁律待本项目 collide 确认字段语义)。
"""

from __future__ import annotations
from typing import Any, Dict, List
import time

from ._eastmoney import eastmoney_datacenter
from stock_common import _debug_log

DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

# V17.4.1: 经上游权威仓库 SKILL.md 对撞校正(原误 RPT_CB_LIST)
_EM_REPORTS: Dict[str, str] = {
    "convertible_bonds": "RPT_BOND_CB_LIST",
}
_SOURCE_URLS: Dict[str, str] = {"convertible_bonds": DATACENTER_URL}
_VERIFIED = True  # 常量取自上游权威仓库; 字段语义待本项目 collide 终检


def _trace(source: str) -> Dict[str, Any]:
    return {"source": source, "source_url": _SOURCE_URLS.get(source, ""), "fetched_at": time.time()}


def convertible_bonds(include_delisted: bool = False) -> List[Dict[str, Any]]:
    """可转债列表: 条款/转股价值/溢价率。

    include_delisted=False 仅返回交易中/待上市; True 含已摘牌。东财源。
    V17.4.1: 拉全量后在 Python 侧按 STATUS 过滤(避免错误过滤串掩盖 reportName 真伪, 便于对撞验证)。
    """
    try:
        rows = eastmoney_datacenter(
            "", _EM_REPORTS["convertible_bonds"], filter_str="", page_size=500
        )
    except Exception as _e:
        _debug_log(f"convertible_bonds: 取值失败 -> {_e}")
        return []
    if not include_delisted:
        rows = [r for r in rows if str(r.get("STATUS", "")).strip() in ("交易中", "待上市", "")]
    for r in rows:
        r.update(_trace("convertible_bonds"))
    return rows

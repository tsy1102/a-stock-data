"""_convertible.py — 可转债层 (V17.4 吸收上游 3.9.0 §15).

函数: convertible_bonds() — 条款/转股价值/溢价率, 状态分 交易中/待上市/已摘牌/无法判断。
数据来源: 东财 datacenter。设计对齐上游: source/source_url/fetched_at 溯源; 结构错抛 RuntimeError。
reportName 常量集中登记于 _EM_REPORTS, 标注 verified=False, 待对撞验证(治理铁律: 推断走候选、不越级定案)。

在常量未经对撞验证前, 函数取值异常时优雅降级返回 [](不伪造数据); 待 collide 验证通过再切换为严格
RuntimeError 契约。
"""
from __future__ import annotations
from typing import Any, Dict, List
import time

from ._eastmoney import eastmoney_datacenter
from stock_common import _debug_log

DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

_EM_REPORTS: Dict[str, str] = {
    "convertible_bonds": "RPT_CB_LIST",   # TODO: 对撞验证
}
_SOURCE_URLS: Dict[str, str] = {"convertible_bonds": DATACENTER_URL}
_VERIFIED = False


def _trace(source: str) -> Dict[str, Any]:
    return {"source": source, "source_url": _SOURCE_URLS.get(source, ""), "fetched_at": time.time()}


def convertible_bonds(include_delisted: bool = False) -> List[Dict[str, Any]]:
    """可转债列表: 条款/转股价值/溢价率。

    include_delisted=False 仅返回交易中/待上市; True 含已摘牌。东财源。
    """
    try:
        _filter = " " if include_delisted else '(STATUS="交易中")'
        rows = eastmoney_datacenter("", _EM_REPORTS["convertible_bonds"], filter_str=_filter, page_size=200)
    except Exception as _e:
        _debug_log(f"convertible_bonds: 取值失败(待对撞验证) -> {_e}")
        return []
    for r in rows:
        r.update(_trace("convertible_bonds"))
    return rows

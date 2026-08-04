"""sc_snapshot.py — V15.3 报告间共享股票快照数据单一来源

V15.2 之前问题：
- get_sht_report.py:42 / get_med_report.py:38 / get_lng_report.py:38 / get_ful_report.py:121
  各自定义同名 _SNAPSHOT_DATA: dict = {}
- 当前子进程模型下互不干扰；但同进程多报告场景会互相覆盖
- upload_multi_reports 跨报告共享 name_resolver 也直接 globals().get("_SNAPSHOT_DATA")

V15.3 修复：
- 抽出到 stock_common.sc_snapshot 单一来源
- 4 个报告 import 后用 sc_snapshot.register(code, data) 写入
- sc_report_runner 的 name_resolver 改用 sc_snapshot.get(code)
- 加 thread lock 防止异步上下文下 race condition
"""
from __future__ import annotations

import threading
from typing import Any, Dict, Optional


# 进程内单一股票快照存储
_snapshot: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()


def register(code: str, data: Dict[str, Any]) -> None:
    """注册/更新单只股票的快照数据。

    Args:
        code: 6 位股票代码
        data: 快照 dict（至少包含 name/price/change_pct）
    """
    if not code or not isinstance(data, dict):
        return
    with _lock:
        _snapshot[code] = data


def get(code: str) -> Optional[Dict[str, Any]]:
    """获取单只股票的快照数据，未注册返回 None。"""
    with _lock:
        return _snapshot.get(code)


def all_codes() -> list:
    """返回所有已注册股票代码列表。"""
    with _lock:
        return list(_snapshot.keys())


def clear() -> None:
    """清空所有快照（仅用于测试或重置场景）。"""
    with _lock:
        _snapshot.clear()


def snapshot_dict() -> Dict[str, Dict[str, Any]]:
    """返回完整快照 dict（拷贝，避免外部修改污染内部状态）。"""
    with _lock:
        return dict(_snapshot)


class SnapshotProxy:
    """V15.3.1 共享代理类: 模拟原 _SNAPSHOT_DATA[code]=... 写入语义。

    V15.3 引入时 4 大报告各自定义了 20 行重复的 _SnapshotProxy 类；
    V15.3.1 提取到 stock_common.sc_snapshot 统一提供，避免 ~80 行重复。

    用法（在报告脚本中）：
        from stock_common.sc_snapshot import SnapshotProxy
        _SNAPSHOT_DATA = SnapshotProxy()  # 模块级单例
    """
    def __setitem__(self, code, value):
        register(code, value)

    def __getitem__(self, code):
        return get(code)

    def __contains__(self, code):
        return get(code) is not None

    def items(self):
        return snapshot_dict().items()

    def keys(self):
        return snapshot_dict().keys()

    def values(self):
        return snapshot_dict().values()

    def __bool__(self):
        return bool(snapshot_dict())

    def __iter__(self):
        return iter(snapshot_dict())

    def __len__(self):
        return len(snapshot_dict())


# V15.3.1 便捷模块级单例（直接 `from stock_common.sc_snapshot import _SNAPSHOT_DATA`）
_SNAPSHOT_DATA = SnapshotProxy()
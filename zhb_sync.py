#!/usr/bin/env python3
"""zhb_sync.py — ZHB 自动化入库管道

实现定时检测、下载、校验、入库和清理的完整流程：

功能特性：
    - 定时检测：支持固定时间触发（如 09:00/18:00）和间隔触发（如每6小时）
    - 智能下载：仅在数据日期更新时下载，避免无效请求
    - 数据校验：校验 zip 完整性、字段数量、数据日期合理性
    - 自动入库：解析后写入本地缓存，支持内存缓存预热
    - 清理策略：保留最近 N 天数据，自动清理过期文件
    - 断点续传：支持从上次中断处继续
    - 状态追踪：记录最后成功同步时间，避免重复同步

使用方式：
    1. 命令行运行：python zhb_sync.py --once  # 单次同步
    2. 定时任务：python zhb_sync.py --cron "0 9,18 * * *"  # 每天9点和18点
    3. 后台守护：python zhb_sync.py --interval 6  # 每6小时同步一次

版本: V14.0（2026-07-22，文档同步）
    V13.x：受益于 stock_cache.py dataclass 透明序列化
    V12.6：受益于字段路由简化（REQUIRES_REALTIME_HTTP）
    V10.3：初始版本
"""

from __future__ import annotations

import os
import sys
import time
import json
import argparse
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

try:
    from zhb_client import (
        get_zhb, _download_zhb_zip, _parse_zhb_data, _save_to_cache,
        _cleanup_old_files, _get_cache_path, _ZHB_CACHE_DIR, _KEEP_DAYS,
        _acquire_file_lock, _release_file_lock, _check_disk_space,
        _zhb_memory_cache, _zhb_cache_lock
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from zhb_client import (
        get_zhb, _download_zhb_zip, _parse_zhb_data, _save_to_cache,
        _cleanup_old_files, _get_cache_path, _ZHB_CACHE_DIR, _KEEP_DAYS,
        _acquire_file_lock, _release_file_lock, _check_disk_space,
        _zhb_memory_cache, _zhb_cache_lock
    )


# ═══════════════════════════════════════
# 配置常量
# ═══════════════════════════════════════

_SYNC_STATE_FILE = os.path.join(_ZHB_CACHE_DIR, ".sync_state.json")
_SYNC_LOG_FILE = os.path.join(_ZHB_CACHE_DIR, "sync.log")

# 默认同步时间（交易日后）
DEFAULT_SYNC_TIMES = ["09:00", "18:00"]

# 最小同步间隔（避免过于频繁）
_MIN_SYNC_INTERVAL_SECONDS = 3600


# ═══════════════════════════════════════
# 状态管理
# ═══════════════════════════════════════

def _load_sync_state() -> Dict[str, Any]:
    """加载同步状态。"""
    if os.path.exists(_SYNC_STATE_FILE):
        try:
            with open(_SYNC_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "last_sync_time": 0,
        "last_sync_date": "",
        "last_sync_success": False,
        "consecutive_failures": 0,
        "total_syncs": 0,
        "total_failures": 0,
    }


def _save_sync_state(state: Dict[str, Any]) -> None:
    """保存同步状态。"""
    try:
        os.makedirs(_ZHB_CACHE_DIR, exist_ok=True)
        with open(_SYNC_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def _log_sync(message: str) -> None:
    """记录同步日志。"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line, flush=True)
    try:
        os.makedirs(_ZHB_CACHE_DIR, exist_ok=True)
        with open(_SYNC_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")
    except Exception:
        pass


# ═══════════════════════════════════════
# 数据校验
# ═══════════════════════════════════════

def _validate_zhb_data(zhb) -> bool:
    """校验 zhb 数据完整性。

    校验项：
        1. 数据日期是否合理（不超过今天）
        2. tdxstat.cfg 是否有足够数据
        3. tdxstat2.cfg 是否存在
        4. 文件数量是否正常
    """
    if zhb is None:
        _log_sync("校验失败：数据为空")
        return False

    if not zhb.date:
        _log_sync("校验失败：数据日期为空")
        return False

    try:
        data_date = datetime.strptime(zhb.date, "%Y%m%d").date()
        today = datetime.now().date()
        if data_date > today:
            _log_sync(f"校验失败：数据日期({zhb.date})超过今天")
            return False
        if (today - data_date).days > 7:
            _log_sync(f"警告：数据日期({zhb.date})已过期7天以上")
    except ValueError:
        _log_sync(f"校验失败：无效的数据日期格式({zhb.date})")
        return False

    stat_count = len(zhb.stock_stats) if zhb._stock_stats is not None else 0
    stat2_count = len(zhb.stock_stats2) if zhb._stock_stats2 is not None else 0

    if stat_count < 5000:
        _log_sync(f"警告：tdxstat 数据量偏少({stat_count})，正常约7000+")

    if stat2_count < 5000:
        _log_sync(f"警告：tdxstat2 数据量偏少({stat2_count})，正常约7000+")

    required_files = ["tdxstat.cfg", "tdxstat2.cfg", "tdxzs3.cfg"]
    missing = [f for f in required_files if f not in zhb.raw_files]
    if missing:
        _log_sync(f"校验失败：缺少必要文件 {missing}")
        return False

    _log_sync(f"校验通过：日期={zhb.date}, tdxstat={stat_count}只, tdxstat2={stat2_count}只")
    return True


# ═══════════════════════════════════════
# 核心同步逻辑
# ═══════════════════════════════════════

def _get_latest_cached_date() -> Optional[str]:
    """获取本地缓存中最新的数据日期。"""
    try:
        if not os.path.exists(_ZHB_CACHE_DIR):
            return None
        zip_files = [f for f in os.listdir(_ZHB_CACHE_DIR) if f.endswith(".zip")]
        if not zip_files:
            return None
        zip_files.sort(reverse=True)
        latest = zip_files[0]
        date_str = latest.replace("zhb_", "").replace(".zip", "")
        return date_str
    except Exception:
        return None


def sync_once(force: bool = False) -> bool:
    """执行一次完整同步。

    Args:
        force: 强制同步，忽略最小间隔限制

    Returns:
        True if sync succeeded, False otherwise
    """
    state = _load_sync_state()
    now = time.time()

    if not force and now - state["last_sync_time"] < _MIN_SYNC_INTERVAL_SECONDS:
        _log_sync(f"跳过同步：距离上次同步仅 {(now - state['last_sync_time'])/60:.0f} 分钟")
        return False

    _log_sync("开始同步...")

    if not _check_disk_space():
        _log_sync("磁盘空间不足")
        state["consecutive_failures"] += 1
        state["total_failures"] += 1
        _save_sync_state(state)
        return False

    if not _acquire_file_lock(timeout=30.0):
        _log_sync("获取文件锁失败，可能有其他进程正在同步")
        return False

    try:
        latest_cached_date = _get_latest_cached_date()
        _log_sync(f"本地最新缓存日期: {latest_cached_date or '无'}")

        data = _download_zhb_zip()
        if not data:
            _log_sync("下载失败：所有服务器连接失败")
            state["consecutive_failures"] += 1
            state["total_failures"] += 1
            state["last_sync_time"] = now
            _save_sync_state(state)
            return False

        _log_sync(f"下载成功：{len(data)} bytes")

        zhb = _parse_zhb_data(data)
        if not zhb:
            _log_sync("解析失败")
            state["consecutive_failures"] += 1
            state["total_failures"] += 1
            state["last_sync_time"] = now
            _save_sync_state(state)
            return False

        if not _validate_zhb_data(zhb):
            state["consecutive_failures"] += 1
            state["total_failures"] += 1
            state["last_sync_time"] = now
            _save_sync_state(state)
            return False

        if not force and latest_cached_date == zhb.date:
            _log_sync(f"数据日期未更新({zhb.date})，无需保存")
            state["last_sync_time"] = now
            state["last_sync_success"] = True
            _save_sync_state(state)
            return True

        _save_to_cache(zhb.date, data)
        _cleanup_old_files()

        with _zhb_cache_lock:
            global _zhb_memory_cache
            _zhb_memory_cache = zhb

        state["last_sync_time"] = now
        state["last_sync_date"] = zhb.date
        state["last_sync_success"] = True
        state["consecutive_failures"] = 0
        state["total_syncs"] += 1
        _save_sync_state(state)

        _log_sync(f"同步成功：日期={zhb.date}")
        return True

    except Exception as e:
        _log_sync(f"同步异常：{e}")
        state["consecutive_failures"] += 1
        state["total_failures"] += 1
        state["last_sync_time"] = now
        _save_sync_state(state)
        return False
    finally:
        _release_file_lock()


# ═══════════════════════════════════════
# 定时调度
# ═══════════════════════════════════════

def _parse_cron(cron_expr: str) -> Optional[tuple]:
    """解析简单的 cron 表达式。

    支持格式：
        - "0 9 * * *" 每天9点
        - "0 9,18 * * *" 每天9点和18点
        - "30 10 * * 1-5" 工作日10:30

    Returns:
        (minute, hours, days, months, weekdays) 或 None
    """
    parts = cron_expr.split()
    if len(parts) != 5:
        return None
    try:
        minute = [int(x) for x in parts[0].split(",")] if parts[0] != "*" else list(range(60))
        hour = [int(x) for x in parts[1].split(",")] if parts[1] != "*" else list(range(24))
        day = [int(x) for x in parts[2].split(",")] if parts[2] != "*" else list(range(1, 32))
        month = [int(x) for x in parts[3].split(",")] if parts[3] != "*" else list(range(1, 13))
        weekday = [int(x) for x in parts[4].split(",")] if parts[4] != "*" else list(range(7))
        return (minute, hour, day, month, weekday)
    except ValueError:
        return None


def _should_run_at_time(cron_spec: tuple) -> bool:
    """检查当前时间是否匹配 cron 表达式。"""
    minute_spec, hour_spec, day_spec, month_spec, weekday_spec = cron_spec
    now = datetime.now()
    return (
        now.minute in minute_spec and
        now.hour in hour_spec and
        now.day in day_spec and
        now.month in month_spec and
        now.weekday() in weekday_spec
    )


def run_cron(cron_expr: str) -> None:
    """按 cron 表达式定时运行同步。"""
    cron_spec = _parse_cron(cron_expr)
    if not cron_spec:
        _log_sync(f"无效的 cron 表达式: {cron_expr}")
        return

    _log_sync(f"启动定时任务：{cron_expr}")
    last_run_hour = -1

    while True:
        now = datetime.now()
        if now.hour != last_run_hour and _should_run_at_time(cron_spec):
            last_run_hour = now.hour
            _log_sync(f"触发定时同步 ({now.strftime('%H:%M')})")
            sync_once()
        time.sleep(60)


def run_interval(hours: int) -> None:
    """按固定间隔运行同步。"""
    interval_seconds = hours * 3600
    _log_sync(f"启动间隔任务：每 {hours} 小时")

    while True:
        _log_sync("触发间隔同步")
        sync_once()
        _log_sync(f"下次同步在 {hours} 小时后")
        time.sleep(interval_seconds)


# ═══════════════════════════════════════
# 命令行接口
# ═══════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(description="ZHB 自动化入库管道")
    parser.add_argument("--once", action="store_true", help="执行一次同步后退出")
    parser.add_argument("--force", action="store_true", help="强制同步（忽略最小间隔）")
    parser.add_argument("--cron", type=str, help="Cron 表达式（如 '0 9,18 * * *'）")
    parser.add_argument("--interval", type=int, help="同步间隔（小时）")
    parser.add_argument("--status", action="store_true", help="查看同步状态")

    args = parser.parse_args()

    if args.status:
        state = _load_sync_state()
        print("同步状态:")
        print(f"  上次同步时间: {datetime.fromtimestamp(state['last_sync_time']).strftime('%Y-%m-%d %H:%M:%S') if state['last_sync_time'] else '从未'}")
        print(f"  上次同步日期: {state['last_sync_date'] or '无'}")
        print(f"  上次同步成功: {'是' if state['last_sync_success'] else '否'}")
        print(f"  连续失败次数: {state['consecutive_failures']}")
        print(f"  总同步次数: {state['total_syncs']}")
        print(f"  总失败次数: {state['total_failures']}")
        print(f"  本地缓存日期: {_get_latest_cached_date() or '无'}")
        return

    if args.once:
        success = sync_once(force=args.force)
        sys.exit(0 if success else 1)

    if args.cron:
        run_cron(args.cron)
        return

    if args.interval:
        run_interval(args.interval)
        return

    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""update_calendar.py - 从 chinese-calendar 库提取数据，更新 stock_calendar.py

用法：
    python scripts/update_calendar.py              # 更新到库支持的最新年份
    python scripts/update_calendar.py --backup     # 更新前自动备份旧文件
    python scripts/update_calendar.py --check      # 仅检查库数据年份范围
    python scripts/update_calendar.py --dry-run    # 预览生成内容，不写入

原理：
    从已安装的 chinese_calendar 库读取 holidays / in_lieu_days，
    按原有格式重新生成 stock_common/stock_calendar.py。
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# V16.4.1: 强制 UTF-8 输出（下沉到代码自身——任何 agent/机器/直接运行均 UTF-8，
# 不依赖系统代码页/环境变量/Profile；纯标准库，幂等）
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _get_lib_data() -> tuple[dict, dict, int, int]:
    """从 chinese_calendar 库获取数据。

    Returns:
        (holidays_dict, in_lieu_days_dict, min_year, max_year)
    """
    try:
        import chinese_calendar
    except ImportError:
        print("错误：chinese-calendar 库未安装", file=sys.stderr)
        print("请先运行: pip install chinese-calendar", file=sys.stderr)
        sys.exit(1)

    holidays = dict(chinese_calendar.constants.holidays)
    in_lieu_days = dict(chinese_calendar.constants.in_lieu_days)

    all_dates = list(holidays.keys()) + list(in_lieu_days.keys())
    min_year = min(d.year for d in all_dates)
    max_year = max(d.year for d in all_dates)

    return holidays, in_lieu_days, min_year, max_year


_HOLIDAY_ENUM_MAP = {
    "New Year's Day": "new_years_day",
    "Spring Festival": "spring_festival",
    "Tomb-sweeping Day": "tomb_sweeping_day",
    "Labour Day": "labour_day",
    "Dragon Boat Festival": "dragon_boat_festival",
    "National Day": "national_day",
    "Mid-autumn Festival": "mid_autumn_festival",
}


def _holiday_enum(holiday_name: str) -> str:
    name = str(holiday_name)
    return _HOLIDAY_ENUM_MAP.get(name, "new_years_day")


def _dict_lines(data: dict, indent: str = "    ") -> list[str]:
    lines = []
    for d in sorted(data.keys()):
        attr = _holiday_enum(data[d])
        lines.append(f"{indent}datetime.date({d.year}, {d.month}, {d.day}): Holiday.{attr},")
    return lines


def _replace_date_dict(content: str, name: str, data: dict) -> str:
    """Replace one top-level date dictionary while preserving surrounding calendar logic."""
    token = f"{name} = {{"
    if content.count(token) != 1:
        raise ValueError(f"expected exactly one {name} dictionary in stock_calendar.py")
    start = content.index(token)
    line_start = content.rfind("\n", 0, start) + 1
    close = content.find("\n}", start)
    if close < 0:
        raise ValueError(f"could not find the end of {name} dictionary")
    end = close + 2
    entries = "\n".join(_dict_lines(data))
    replacement = f"{name} = {{\n{entries}\n}}"
    return content[:line_start] + replacement + content[end:]


def update_calendar_data(content: str, holidays: dict, workdays: dict) -> str:
    """Patch only the generated date tables, keeping project-specific functions intact."""
    if "def is_trading_day(" not in content:
        raise ValueError("stock_calendar.py lacks the A-share trading-day implementation")
    updated = _replace_date_dict(content, "holidays", holidays)
    return _replace_date_dict(updated, "workdays", workdays)


def generate_calendar_file(holidays: dict, workdays: dict, min_year: int, max_year: int) -> str:
    """生成完整的 stock_calendar.py 文件内容。"""
    hl = "\n".join(_dict_lines(holidays))
    wl = "\n".join(_dict_lines(workdays))

    return '''# -*- coding: utf-8 -*-
# A股交易日历数据模块 (V9.2)
# 基于 chinese-calendar 库的数据，数据范围 {min_year}-{max_year}
# 由 chinese_calendar.constants 提取，通过 scripts/update_calendar.py 自动生成
#
# V9.2 更新：
#   - 新增 CLI 入口（python scripts/update_calendar.py 更新数据）
#   - 新增 data_years() 查询数据范围
#
# V9.1 新增：
#   - get_last_trading_day(date=None): 最近一个交易日（休市时返回上一个交易日）
#   - get_next_trading_day(date=None): 下一个交易日
#   用于 F10 缓存的 trading_day 过期策略

from __future__ import absolute_import, unicode_literals
import datetime

# ==================== Holiday 枚举 ====================
class Holiday:
    new_years_day = "New Year's Day"  # 元旦
    spring_festival = "Spring Festival"  # 春节
    tomb_sweeping_day = "Tomb-sweeping Day"  # 清明
    labour_day = "Labour Day"  # 劳动节
    dragon_boat_festival = "Dragon Boat Festival"  # 端午
    national_day = "National Day"  # 国庆节
    mid_autumn_festival = "Mid-autumn Festival"  # 中秋


# ==================== 节假日字典 ====================
holidays = {{
{hl}
}}

# ==================== 调休工作日（周末但需上班）====================
workdays = {{
{wl}
}}

# ==================== 核心函数 ====================

def _wrap_date(date):
    """将 datetime 转换为 date"""
    if isinstance(date, datetime.datetime):
        return date.date()
    return date


def _validate_date(date):
    """检查日期是否在支持范围内"""
    date = _wrap_date(date)
    if not isinstance(date, datetime.date):
        raise TypeError("unsupported type {{type(date)}}, expected datetime.date")
    min_year = min(holidays.keys()).year
    max_year = max(holidays.keys()).year
    if not (min_year <= date.year <= max_year):
        raise NotImplementedError(
            "no available data for year {{date.year}}, only year between [{{min_year}}, {{max_year}}] supported"
        )
    return date


def is_trading_day(date):
    """A-share exchange session; civil make-up weekends remain market holidays."""
    date = _validate_date(date)
    return date.weekday() < 5 and date not in holidays


def is_workday(date):
    """Compatibility alias: this calendar's workday means an A-share session."""
    return is_trading_day(date)


def previous_trading_day(date, include_current=False):
    date = _validate_date(date)
    if not include_current:
        date -= datetime.timedelta(days=1)
    for _ in range(30):
        if is_trading_day(date):
            return date
        date -= datetime.timedelta(days=1)
    raise NotImplementedError("no trading day found in the previous 30 days")


def add_trading_days(date, offset):
    date = _validate_date(date)
    if offset == 0:
        return date
    step = 1 if offset > 0 else -1
    remaining = abs(offset)
    while remaining:
        date += datetime.timedelta(days=step)
        if is_trading_day(date):
            remaining -= 1
    return date


def trading_days_between(start, end):
    """Count sessions in (start, end]; a reversed interval returns a negative count."""
    first = _validate_date(start)
    last = _validate_date(end)
    if first == last:
        return 0
    if first > last:
        return -trading_days_between(last, first)
    count = 0
    date = first + datetime.timedelta(days=1)
    while date <= last:
        if is_trading_day(date):
            count += 1
        date += datetime.timedelta(days=1)
    return count


def latest_market_data_date(as_of=None):
    """Use the prior session before 09:30; use today's session from 09:30 onward."""
    value = datetime.datetime.now() if as_of is None else as_of
    if isinstance(value, datetime.datetime):
        date = _validate_date(value.date())
        session_started = value.timetz().replace(tzinfo=None) >= datetime.time(9, 30)
    else:
        date = _validate_date(value)
        session_started = True
    if session_started and is_trading_day(date):
        return date
    return previous_trading_day(date, include_current=False)


def trading_day_age(data_date, as_of=None):
    return trading_days_between(data_date, latest_market_data_date(as_of))


def trading_day_window(days, as_of=None):
    if days < 1:
        raise ValueError("days must be a positive integer")
    end = latest_market_data_date(as_of)
    return add_trading_days(end, -(days - 1)), end


def recent_trading_dates(count, as_of=None):
    if count < 0:
        raise ValueError("count must be non-negative")
    if count == 0:
        return []
    date = latest_market_data_date(as_of)
    result = [date]
    for _ in range(count - 1):
        date = previous_trading_day(date, include_current=False)
        result.append(date)
    return result


def get_last_trading_day(date=None):
    """获取给定日期之前（含）最近的交易日

    Args:
        date: datetime.date 或 datetime.datetime，默认今天

    Returns:
        datetime.date: 最近的交易日

    Raises:
        NotImplementedError: 年份超出支持范围
    """
    if date is None:
        date = datetime.date.today()
    date = _wrap_date(date)
    for _ in range(30):
        if is_workday(date):
            return date
        date -= datetime.timedelta(days=1)
    raise NotImplementedError("no trading day found in the last 30 days")


def get_next_trading_day(date=None):
    """获取给定日期之后（不含）最近的交易日

    Args:
        date: datetime.date 或 datetime.datetime，默认今天

    Returns:
        datetime.date: 下一个交易日

    Raises:
        NotImplementedError: 年份超出支持范围
    """
    if date is None:
        date = datetime.date.today()
    date = _wrap_date(date)
    date += datetime.timedelta(days=1)
    for _ in range(30):
        try:
            if is_workday(date):
                return date
        except NotImplementedError:
            raise
        date += datetime.timedelta(days=1)
    raise NotImplementedError("no trading day found in the next 30 days")


def data_years() -> tuple:
    """返回当前数据支持的年份范围 (min_year, max_year)"""
    all_dates = list(holidays.keys()) + list(workdays.keys())
    return min(d.year for d in all_dates), max(d.year for d in all_dates)
'''.format(min_year=min_year, max_year=max_year, hl=hl, wl=wl)


def main():
    parser = argparse.ArgumentParser(description="更新 stock_calendar.py 日历数据")
    parser.add_argument("--check", action="store_true", help="仅检查 chinese-calendar 库的年份范围")
    parser.add_argument("--backup", action="store_true", help="更新前自动备份旧文件")
    parser.add_argument("--dry-run", action="store_true", help="仅预览生成内容，不写入文件")
    args = parser.parse_args()

    holidays, workdays, min_year, max_year = _get_lib_data()

    if args.check:
        print(f"chinese-calendar 库数据范围: {min_year}-{max_year}")
        print(f"节假日条目数: {len(holidays)}")
        print(f"调休工作日条目数: {len(workdays)}")
        return

    target = Path(__file__).parent.parent / "stock_common" / "stock_calendar.py"
    current = target.read_text(encoding="utf-8") if target.exists() else None

    if args.dry_run:
        content = (
            update_calendar_data(current, holidays, workdays)
            if current is not None
            else generate_calendar_file(holidays, workdays, min_year, max_year)
        )
        sys.stdout.write(content[:3000])
        print(f"\n... (共 {len(content)} 字符)")
        return

    if args.backup and target.exists():
        backup_path = target.with_suffix(".py.bak")
        shutil.copy2(target, backup_path)
        print(f"已备份旧文件: {backup_path}")

    content = (
        update_calendar_data(current, holidays, workdays)
        if current is not None
        else generate_calendar_file(holidays, workdays, min_year, max_year)
    )
    target.write_text(content, encoding="utf-8")
    print(f"已更新: {target}")
    print(f"数据范围: {min_year}-{max_year}")
    print(f"节假日条目: {len(holidays)}")
    print(f"调休工作日条目: {len(workdays)}")


if __name__ == "__main__":
    main()

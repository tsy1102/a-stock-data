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


def generate_calendar_file(holidays: dict, workdays: dict,
                           min_year: int, max_year: int) -> str:
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


def is_workday(date):
    """判断是否为工作日（A股交易日）

    Args:
        date: datetime.date 或 datetime.datetime

    Returns:
        bool: True=交易日, False=休市日
    """
    try:
        date = _validate_date(date)
        weekday = date.weekday()
        return bool(date in workdays or (weekday <= 4 and date not in holidays))
    except NotImplementedError:
        raise


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
'''


def main():
    parser = argparse.ArgumentParser(description="更新 stock_calendar.py 日历数据")
    parser.add_argument("--check", action="store_true",
                        help="仅检查 chinese-calendar 库的年份范围")
    parser.add_argument("--backup", action="store_true",
                        help="更新前自动备份旧文件")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅预览生成内容，不写入文件")
    args = parser.parse_args()

    holidays, workdays, min_year, max_year = _get_lib_data()

    if args.check:
        print(f"chinese-calendar 库数据范围: {min_year}-{max_year}")
        print(f"节假日条目数: {len(holidays)}")
        print(f"调休工作日条目数: {len(workdays)}")
        return

    target = Path(__file__).parent.parent / "stock_common" / "stock_calendar.py"

    if args.dry_run:
        content = generate_calendar_file(holidays, workdays, min_year, max_year)
        sys.stdout.write(content[:3000])
        print(f"\n... (共 {len(content)} 字符)")
        return

    if args.backup and target.exists():
        backup_path = target.with_suffix(".py.bak")
        shutil.copy2(target, backup_path)
        print(f"已备份旧文件: {backup_path}")

    content = generate_calendar_file(holidays, workdays, min_year, max_year)
    target.write_text(content, encoding="utf-8")
    print(f"已更新: {target}")
    print(f"数据范围: {min_year}-{max_year}")
    print(f"节假日条目: {len(holidays)}")
    print(f"调休工作日条目: {len(workdays)}")


if __name__ == "__main__":
    main()

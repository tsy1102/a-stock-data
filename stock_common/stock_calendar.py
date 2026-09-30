# -*- coding: utf-8 -*-
# A股交易日历数据模块
# 基于 chinese-calendar 库的数据，数据范围 2004-2026
# 由 chinese_calendar.constants 和 chinese_calendar.utils 提取优化
#
# V9.2 新增：
#   - CLI 入口支持 --check / --update / --get-last / --get-next
#   - scripts/update_calendar.py 脚本支持从 chinese-calendar 库自动更新数据
#
# V9.1 新增：
#   - get_last_trading_day(date=None): 最近一个交易日（休市时返回上一个交易日）
#   - get_next_trading_day(date=None): 下一个交易日
#   用于 F10 缓存的 trading_day 过期策略（方案B）

from __future__ import absolute_import, unicode_literals
import datetime
from typing import Any, List, Optional, Set, Tuple, Union, cast


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
holidays = {
    datetime.date(2004, 1, 1): Holiday.new_years_day,
    datetime.date(2004, 1, 22): Holiday.spring_festival,
    datetime.date(2004, 1, 23): Holiday.spring_festival,
    datetime.date(2004, 1, 24): Holiday.spring_festival,
    datetime.date(2004, 1, 25): Holiday.spring_festival,
    datetime.date(2004, 1, 26): Holiday.spring_festival,
    datetime.date(2004, 1, 27): Holiday.spring_festival,
    datetime.date(2004, 1, 28): Holiday.spring_festival,
    datetime.date(2004, 5, 1): Holiday.labour_day,
    datetime.date(2004, 5, 2): Holiday.labour_day,
    datetime.date(2004, 5, 3): Holiday.labour_day,
    datetime.date(2004, 5, 4): Holiday.labour_day,
    datetime.date(2004, 5, 5): Holiday.labour_day,
    datetime.date(2004, 5, 6): Holiday.labour_day,
    datetime.date(2004, 5, 7): Holiday.labour_day,
    datetime.date(2004, 10, 1): Holiday.national_day,
    datetime.date(2004, 10, 2): Holiday.national_day,
    datetime.date(2004, 10, 3): Holiday.national_day,
    datetime.date(2004, 10, 4): Holiday.national_day,
    datetime.date(2004, 10, 5): Holiday.national_day,
    datetime.date(2004, 10, 6): Holiday.national_day,
    datetime.date(2004, 10, 7): Holiday.national_day,
    datetime.date(2005, 1, 1): Holiday.new_years_day,
    datetime.date(2005, 1, 2): Holiday.new_years_day,
    datetime.date(2005, 1, 3): Holiday.new_years_day,
    datetime.date(2005, 2, 9): Holiday.spring_festival,
    datetime.date(2005, 2, 10): Holiday.spring_festival,
    datetime.date(2005, 2, 11): Holiday.spring_festival,
    datetime.date(2005, 2, 12): Holiday.spring_festival,
    datetime.date(2005, 2, 13): Holiday.spring_festival,
    datetime.date(2005, 2, 14): Holiday.spring_festival,
    datetime.date(2005, 2, 15): Holiday.spring_festival,
    datetime.date(2005, 5, 1): Holiday.labour_day,
    datetime.date(2005, 5, 2): Holiday.labour_day,
    datetime.date(2005, 5, 3): Holiday.labour_day,
    datetime.date(2005, 5, 4): Holiday.labour_day,
    datetime.date(2005, 5, 5): Holiday.labour_day,
    datetime.date(2005, 5, 6): Holiday.labour_day,
    datetime.date(2005, 5, 7): Holiday.labour_day,
    datetime.date(2005, 10, 1): Holiday.national_day,
    datetime.date(2005, 10, 2): Holiday.national_day,
    datetime.date(2005, 10, 3): Holiday.national_day,
    datetime.date(2005, 10, 4): Holiday.national_day,
    datetime.date(2005, 10, 5): Holiday.national_day,
    datetime.date(2005, 10, 6): Holiday.national_day,
    datetime.date(2005, 10, 7): Holiday.national_day,
    datetime.date(2006, 1, 1): Holiday.new_years_day,
    datetime.date(2006, 1, 2): Holiday.new_years_day,
    datetime.date(2006, 1, 3): Holiday.new_years_day,
    datetime.date(2006, 1, 29): Holiday.spring_festival,
    datetime.date(2006, 1, 30): Holiday.spring_festival,
    datetime.date(2006, 1, 31): Holiday.spring_festival,
    datetime.date(2006, 2, 1): Holiday.spring_festival,
    datetime.date(2006, 2, 2): Holiday.spring_festival,
    datetime.date(2006, 2, 3): Holiday.spring_festival,
    datetime.date(2006, 2, 4): Holiday.spring_festival,
    datetime.date(2006, 5, 1): Holiday.labour_day,
    datetime.date(2006, 5, 2): Holiday.labour_day,
    datetime.date(2006, 5, 3): Holiday.labour_day,
    datetime.date(2006, 5, 4): Holiday.labour_day,
    datetime.date(2006, 5, 5): Holiday.labour_day,
    datetime.date(2006, 5, 6): Holiday.labour_day,
    datetime.date(2006, 5, 7): Holiday.labour_day,
    datetime.date(2006, 10, 1): Holiday.national_day,
    datetime.date(2006, 10, 2): Holiday.national_day,
    datetime.date(2006, 10, 3): Holiday.national_day,
    datetime.date(2006, 10, 4): Holiday.national_day,
    datetime.date(2006, 10, 5): Holiday.national_day,
    datetime.date(2006, 10, 6): Holiday.national_day,
    datetime.date(2006, 10, 7): Holiday.national_day,
    datetime.date(2007, 1, 1): Holiday.new_years_day,
    datetime.date(2007, 1, 2): Holiday.new_years_day,
    datetime.date(2007, 1, 3): Holiday.new_years_day,
    datetime.date(2007, 2, 18): Holiday.spring_festival,
    datetime.date(2007, 2, 19): Holiday.spring_festival,
    datetime.date(2007, 2, 20): Holiday.spring_festival,
    datetime.date(2007, 2, 21): Holiday.spring_festival,
    datetime.date(2007, 2, 22): Holiday.spring_festival,
    datetime.date(2007, 2, 23): Holiday.spring_festival,
    datetime.date(2007, 2, 24): Holiday.spring_festival,
    datetime.date(2007, 5, 1): Holiday.labour_day,
    datetime.date(2007, 5, 2): Holiday.labour_day,
    datetime.date(2007, 5, 3): Holiday.labour_day,
    datetime.date(2007, 5, 4): Holiday.labour_day,
    datetime.date(2007, 5, 5): Holiday.labour_day,
    datetime.date(2007, 5, 6): Holiday.labour_day,
    datetime.date(2007, 5, 7): Holiday.labour_day,
    datetime.date(2007, 10, 1): Holiday.national_day,
    datetime.date(2007, 10, 2): Holiday.national_day,
    datetime.date(2007, 10, 3): Holiday.national_day,
    datetime.date(2007, 10, 4): Holiday.national_day,
    datetime.date(2007, 10, 5): Holiday.national_day,
    datetime.date(2007, 10, 6): Holiday.national_day,
    datetime.date(2007, 10, 7): Holiday.national_day,
    datetime.date(2007, 12, 30): Holiday.new_years_day,
    datetime.date(2007, 12, 31): Holiday.new_years_day,
    datetime.date(2008, 1, 1): Holiday.new_years_day,
    datetime.date(2008, 2, 6): Holiday.spring_festival,
    datetime.date(2008, 2, 7): Holiday.spring_festival,
    datetime.date(2008, 2, 8): Holiday.spring_festival,
    datetime.date(2008, 2, 9): Holiday.spring_festival,
    datetime.date(2008, 2, 10): Holiday.spring_festival,
    datetime.date(2008, 2, 11): Holiday.spring_festival,
    datetime.date(2008, 2, 12): Holiday.spring_festival,
    datetime.date(2008, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2008, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2008, 4, 6): Holiday.tomb_sweeping_day,
    datetime.date(2008, 5, 1): Holiday.labour_day,
    datetime.date(2008, 5, 2): Holiday.labour_day,
    datetime.date(2008, 5, 3): Holiday.labour_day,
    datetime.date(2008, 6, 7): Holiday.dragon_boat_festival,
    datetime.date(2008, 6, 8): Holiday.dragon_boat_festival,
    datetime.date(2008, 6, 9): Holiday.dragon_boat_festival,
    datetime.date(2008, 9, 13): Holiday.mid_autumn_festival,
    datetime.date(2008, 9, 14): Holiday.mid_autumn_festival,
    datetime.date(2008, 9, 15): Holiday.mid_autumn_festival,
    datetime.date(2008, 9, 29): Holiday.national_day,
    datetime.date(2008, 9, 30): Holiday.national_day,
    datetime.date(2008, 10, 1): Holiday.national_day,
    datetime.date(2008, 10, 2): Holiday.national_day,
    datetime.date(2008, 10, 3): Holiday.national_day,
    datetime.date(2008, 10, 4): Holiday.national_day,
    datetime.date(2008, 10, 5): Holiday.national_day,
    datetime.date(2009, 1, 1): Holiday.new_years_day,
    datetime.date(2009, 1, 2): Holiday.new_years_day,
    datetime.date(2009, 1, 3): Holiday.new_years_day,
    datetime.date(2009, 1, 25): Holiday.spring_festival,
    datetime.date(2009, 1, 26): Holiday.spring_festival,
    datetime.date(2009, 1, 27): Holiday.spring_festival,
    datetime.date(2009, 1, 28): Holiday.spring_festival,
    datetime.date(2009, 1, 29): Holiday.spring_festival,
    datetime.date(2009, 1, 30): Holiday.spring_festival,
    datetime.date(2009, 1, 31): Holiday.spring_festival,
    datetime.date(2009, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2009, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2009, 4, 6): Holiday.tomb_sweeping_day,
    datetime.date(2009, 5, 1): Holiday.labour_day,
    datetime.date(2009, 5, 2): Holiday.labour_day,
    datetime.date(2009, 5, 3): Holiday.labour_day,
    datetime.date(2009, 5, 28): Holiday.dragon_boat_festival,
    datetime.date(2009, 5, 29): Holiday.dragon_boat_festival,
    datetime.date(2009, 5, 30): Holiday.dragon_boat_festival,
    datetime.date(2009, 10, 1): Holiday.national_day,
    datetime.date(2009, 10, 2): Holiday.national_day,
    datetime.date(2009, 10, 3): Holiday.mid_autumn_festival,
    datetime.date(2009, 10, 4): Holiday.national_day,
    datetime.date(2009, 10, 5): Holiday.national_day,
    datetime.date(2009, 10, 6): Holiday.national_day,
    datetime.date(2009, 10, 7): Holiday.national_day,
    datetime.date(2009, 10, 8): Holiday.national_day,
    datetime.date(2010, 1, 1): Holiday.new_years_day,
    datetime.date(2010, 1, 2): Holiday.new_years_day,
    datetime.date(2010, 1, 3): Holiday.new_years_day,
    datetime.date(2010, 2, 13): Holiday.spring_festival,
    datetime.date(2010, 2, 14): Holiday.spring_festival,
    datetime.date(2010, 2, 15): Holiday.spring_festival,
    datetime.date(2010, 2, 16): Holiday.spring_festival,
    datetime.date(2010, 2, 17): Holiday.spring_festival,
    datetime.date(2010, 2, 18): Holiday.spring_festival,
    datetime.date(2010, 2, 19): Holiday.spring_festival,
    datetime.date(2010, 4, 3): Holiday.tomb_sweeping_day,
    datetime.date(2010, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2010, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2010, 5, 1): Holiday.labour_day,
    datetime.date(2010, 5, 2): Holiday.labour_day,
    datetime.date(2010, 5, 3): Holiday.labour_day,
    datetime.date(2010, 6, 14): Holiday.dragon_boat_festival,
    datetime.date(2010, 6, 15): Holiday.dragon_boat_festival,
    datetime.date(2010, 6, 16): Holiday.dragon_boat_festival,
    datetime.date(2010, 9, 22): Holiday.mid_autumn_festival,
    datetime.date(2010, 9, 23): Holiday.mid_autumn_festival,
    datetime.date(2010, 9, 24): Holiday.mid_autumn_festival,
    datetime.date(2010, 10, 1): Holiday.national_day,
    datetime.date(2010, 10, 2): Holiday.national_day,
    datetime.date(2010, 10, 3): Holiday.national_day,
    datetime.date(2010, 10, 4): Holiday.national_day,
    datetime.date(2010, 10, 5): Holiday.national_day,
    datetime.date(2010, 10, 6): Holiday.national_day,
    datetime.date(2010, 10, 7): Holiday.national_day,
    datetime.date(2011, 1, 1): Holiday.new_years_day,
    datetime.date(2011, 1, 2): Holiday.new_years_day,
    datetime.date(2011, 1, 3): Holiday.new_years_day,
    datetime.date(2011, 2, 2): Holiday.spring_festival,
    datetime.date(2011, 2, 3): Holiday.spring_festival,
    datetime.date(2011, 2, 4): Holiday.spring_festival,
    datetime.date(2011, 2, 5): Holiday.spring_festival,
    datetime.date(2011, 2, 6): Holiday.spring_festival,
    datetime.date(2011, 2, 7): Holiday.spring_festival,
    datetime.date(2011, 2, 8): Holiday.spring_festival,
    datetime.date(2011, 4, 3): Holiday.tomb_sweeping_day,
    datetime.date(2011, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2011, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2011, 4, 30): Holiday.labour_day,
    datetime.date(2011, 5, 1): Holiday.labour_day,
    datetime.date(2011, 5, 2): Holiday.labour_day,
    datetime.date(2011, 6, 4): Holiday.dragon_boat_festival,
    datetime.date(2011, 6, 6): Holiday.dragon_boat_festival,
    datetime.date(2011, 9, 10): Holiday.mid_autumn_festival,
    datetime.date(2011, 9, 11): Holiday.mid_autumn_festival,
    datetime.date(2011, 9, 12): Holiday.mid_autumn_festival,
    datetime.date(2011, 10, 1): Holiday.national_day,
    datetime.date(2011, 10, 2): Holiday.national_day,
    datetime.date(2011, 10, 3): Holiday.national_day,
    datetime.date(2011, 10, 4): Holiday.national_day,
    datetime.date(2011, 10, 5): Holiday.national_day,
    datetime.date(2011, 10, 6): Holiday.national_day,
    datetime.date(2011, 10, 7): Holiday.national_day,
    datetime.date(2012, 1, 1): Holiday.new_years_day,
    datetime.date(2012, 1, 2): Holiday.new_years_day,
    datetime.date(2012, 1, 3): Holiday.new_years_day,
    datetime.date(2012, 1, 22): Holiday.spring_festival,
    datetime.date(2012, 1, 23): Holiday.spring_festival,
    datetime.date(2012, 1, 24): Holiday.spring_festival,
    datetime.date(2012, 1, 25): Holiday.spring_festival,
    datetime.date(2012, 1, 26): Holiday.spring_festival,
    datetime.date(2012, 1, 27): Holiday.spring_festival,
    datetime.date(2012, 1, 28): Holiday.spring_festival,
    datetime.date(2012, 4, 2): Holiday.tomb_sweeping_day,
    datetime.date(2012, 4, 3): Holiday.tomb_sweeping_day,
    datetime.date(2012, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2012, 4, 29): Holiday.labour_day,
    datetime.date(2012, 4, 30): Holiday.labour_day,
    datetime.date(2012, 5, 1): Holiday.labour_day,
    datetime.date(2012, 6, 22): Holiday.dragon_boat_festival,
    datetime.date(2012, 6, 24): Holiday.dragon_boat_festival,
    datetime.date(2012, 9, 30): Holiday.mid_autumn_festival,
    datetime.date(2012, 10, 1): Holiday.national_day,
    datetime.date(2012, 10, 2): Holiday.national_day,
    datetime.date(2012, 10, 3): Holiday.national_day,
    datetime.date(2012, 10, 4): Holiday.national_day,
    datetime.date(2012, 10, 5): Holiday.national_day,
    datetime.date(2012, 10, 6): Holiday.national_day,
    datetime.date(2012, 10, 7): Holiday.national_day,
    datetime.date(2013, 1, 1): Holiday.new_years_day,
    datetime.date(2013, 1, 2): Holiday.new_years_day,
    datetime.date(2013, 1, 3): Holiday.new_years_day,
    datetime.date(2013, 2, 9): Holiday.spring_festival,
    datetime.date(2013, 2, 10): Holiday.spring_festival,
    datetime.date(2013, 2, 11): Holiday.spring_festival,
    datetime.date(2013, 2, 12): Holiday.spring_festival,
    datetime.date(2013, 2, 13): Holiday.spring_festival,
    datetime.date(2013, 2, 14): Holiday.spring_festival,
    datetime.date(2013, 2, 15): Holiday.spring_festival,
    datetime.date(2013, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2013, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2013, 4, 6): Holiday.tomb_sweeping_day,
    datetime.date(2013, 4, 29): Holiday.labour_day,
    datetime.date(2013, 4, 30): Holiday.labour_day,
    datetime.date(2013, 5, 1): Holiday.labour_day,
    datetime.date(2013, 6, 10): Holiday.dragon_boat_festival,
    datetime.date(2013, 6, 11): Holiday.dragon_boat_festival,
    datetime.date(2013, 6, 12): Holiday.dragon_boat_festival,
    datetime.date(2013, 9, 19): Holiday.mid_autumn_festival,
    datetime.date(2013, 9, 20): Holiday.mid_autumn_festival,
    datetime.date(2013, 9, 21): Holiday.mid_autumn_festival,
    datetime.date(2013, 10, 1): Holiday.national_day,
    datetime.date(2013, 10, 2): Holiday.national_day,
    datetime.date(2013, 10, 3): Holiday.national_day,
    datetime.date(2013, 10, 4): Holiday.national_day,
    datetime.date(2013, 10, 5): Holiday.national_day,
    datetime.date(2013, 10, 6): Holiday.national_day,
    datetime.date(2013, 10, 7): Holiday.national_day,
    datetime.date(2014, 1, 1): Holiday.new_years_day,
    datetime.date(2014, 1, 31): Holiday.spring_festival,
    datetime.date(2014, 2, 1): Holiday.spring_festival,
    datetime.date(2014, 2, 2): Holiday.spring_festival,
    datetime.date(2014, 2, 3): Holiday.spring_festival,
    datetime.date(2014, 2, 4): Holiday.spring_festival,
    datetime.date(2014, 2, 5): Holiday.spring_festival,
    datetime.date(2014, 2, 6): Holiday.spring_festival,
    datetime.date(2014, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2014, 4, 6): Holiday.tomb_sweeping_day,
    datetime.date(2014, 4, 7): Holiday.tomb_sweeping_day,
    datetime.date(2014, 5, 1): Holiday.labour_day,
    datetime.date(2014, 5, 2): Holiday.labour_day,
    datetime.date(2014, 5, 3): Holiday.labour_day,
    datetime.date(2014, 6, 2): Holiday.dragon_boat_festival,
    datetime.date(2014, 9, 8): Holiday.mid_autumn_festival,
    datetime.date(2014, 10, 1): Holiday.national_day,
    datetime.date(2014, 10, 2): Holiday.national_day,
    datetime.date(2014, 10, 3): Holiday.national_day,
    datetime.date(2014, 10, 4): Holiday.national_day,
    datetime.date(2014, 10, 5): Holiday.national_day,
    datetime.date(2014, 10, 6): Holiday.national_day,
    datetime.date(2014, 10, 7): Holiday.national_day,
    datetime.date(2015, 1, 1): Holiday.new_years_day,
    datetime.date(2015, 1, 2): Holiday.new_years_day,
    datetime.date(2015, 1, 3): Holiday.new_years_day,
    datetime.date(2015, 2, 18): Holiday.spring_festival,
    datetime.date(2015, 2, 19): Holiday.spring_festival,
    datetime.date(2015, 2, 20): Holiday.spring_festival,
    datetime.date(2015, 2, 21): Holiday.spring_festival,
    datetime.date(2015, 2, 22): Holiday.spring_festival,
    datetime.date(2015, 2, 23): Holiday.spring_festival,
    datetime.date(2015, 2, 24): Holiday.spring_festival,
    datetime.date(2015, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2015, 4, 6): Holiday.tomb_sweeping_day,
    datetime.date(2015, 5, 1): Holiday.labour_day,
    datetime.date(2015, 6, 20): Holiday.dragon_boat_festival,
    datetime.date(2015, 6, 22): Holiday.dragon_boat_festival,
    datetime.date(2015, 9, 3): Holiday.national_day,
    datetime.date(2015, 9, 4): Holiday.national_day,
    datetime.date(2015, 9, 27): Holiday.mid_autumn_festival,
    datetime.date(2015, 10, 1): Holiday.national_day,
    datetime.date(2015, 10, 2): Holiday.national_day,
    datetime.date(2015, 10, 3): Holiday.national_day,
    datetime.date(2015, 10, 4): Holiday.national_day,
    datetime.date(2015, 10, 5): Holiday.national_day,
    datetime.date(2015, 10, 6): Holiday.national_day,
    datetime.date(2015, 10, 7): Holiday.national_day,
    datetime.date(2016, 1, 1): Holiday.new_years_day,
    datetime.date(2016, 2, 7): Holiday.spring_festival,
    datetime.date(2016, 2, 8): Holiday.spring_festival,
    datetime.date(2016, 2, 9): Holiday.spring_festival,
    datetime.date(2016, 2, 10): Holiday.spring_festival,
    datetime.date(2016, 2, 11): Holiday.spring_festival,
    datetime.date(2016, 2, 12): Holiday.spring_festival,
    datetime.date(2016, 2, 13): Holiday.spring_festival,
    datetime.date(2016, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2016, 5, 1): Holiday.labour_day,
    datetime.date(2016, 5, 2): Holiday.labour_day,
    datetime.date(2016, 6, 9): Holiday.dragon_boat_festival,
    datetime.date(2016, 6, 10): Holiday.dragon_boat_festival,
    datetime.date(2016, 6, 11): Holiday.dragon_boat_festival,
    datetime.date(2016, 9, 15): Holiday.mid_autumn_festival,
    datetime.date(2016, 9, 16): Holiday.mid_autumn_festival,
    datetime.date(2016, 9, 17): Holiday.mid_autumn_festival,
    datetime.date(2016, 10, 1): Holiday.national_day,
    datetime.date(2016, 10, 2): Holiday.national_day,
    datetime.date(2016, 10, 3): Holiday.national_day,
    datetime.date(2016, 10, 4): Holiday.national_day,
    datetime.date(2016, 10, 5): Holiday.national_day,
    datetime.date(2016, 10, 6): Holiday.national_day,
    datetime.date(2016, 10, 7): Holiday.national_day,
    datetime.date(2017, 1, 1): Holiday.new_years_day,
    datetime.date(2017, 1, 2): Holiday.new_years_day,
    datetime.date(2017, 1, 27): Holiday.spring_festival,
    datetime.date(2017, 1, 28): Holiday.spring_festival,
    datetime.date(2017, 1, 29): Holiday.spring_festival,
    datetime.date(2017, 1, 30): Holiday.spring_festival,
    datetime.date(2017, 1, 31): Holiday.spring_festival,
    datetime.date(2017, 2, 1): Holiday.spring_festival,
    datetime.date(2017, 2, 2): Holiday.spring_festival,
    datetime.date(2017, 4, 2): Holiday.tomb_sweeping_day,
    datetime.date(2017, 4, 3): Holiday.tomb_sweeping_day,
    datetime.date(2017, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2017, 5, 1): Holiday.labour_day,
    datetime.date(2017, 5, 28): Holiday.dragon_boat_festival,
    datetime.date(2017, 5, 29): Holiday.dragon_boat_festival,
    datetime.date(2017, 5, 30): Holiday.dragon_boat_festival,
    datetime.date(2017, 10, 1): Holiday.national_day,
    datetime.date(2017, 10, 2): Holiday.national_day,
    datetime.date(2017, 10, 3): Holiday.national_day,
    datetime.date(2017, 10, 4): Holiday.mid_autumn_festival,
    datetime.date(2017, 10, 5): Holiday.national_day,
    datetime.date(2017, 10, 6): Holiday.national_day,
    datetime.date(2017, 10, 7): Holiday.national_day,
    datetime.date(2017, 10, 8): Holiday.national_day,
    datetime.date(2018, 1, 1): Holiday.new_years_day,
    datetime.date(2018, 2, 15): Holiday.spring_festival,
    datetime.date(2018, 2, 16): Holiday.spring_festival,
    datetime.date(2018, 2, 17): Holiday.spring_festival,
    datetime.date(2018, 2, 18): Holiday.spring_festival,
    datetime.date(2018, 2, 19): Holiday.spring_festival,
    datetime.date(2018, 2, 20): Holiday.spring_festival,
    datetime.date(2018, 2, 21): Holiday.spring_festival,
    datetime.date(2018, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2018, 4, 6): Holiday.tomb_sweeping_day,
    datetime.date(2018, 4, 7): Holiday.tomb_sweeping_day,
    datetime.date(2018, 4, 29): Holiday.labour_day,
    datetime.date(2018, 4, 30): Holiday.labour_day,
    datetime.date(2018, 5, 1): Holiday.labour_day,
    datetime.date(2018, 6, 18): Holiday.dragon_boat_festival,
    datetime.date(2018, 9, 24): Holiday.mid_autumn_festival,
    datetime.date(2018, 10, 1): Holiday.national_day,
    datetime.date(2018, 10, 2): Holiday.national_day,
    datetime.date(2018, 10, 3): Holiday.national_day,
    datetime.date(2018, 10, 4): Holiday.national_day,
    datetime.date(2018, 10, 5): Holiday.national_day,
    datetime.date(2018, 10, 6): Holiday.national_day,
    datetime.date(2018, 10, 7): Holiday.national_day,
    datetime.date(2018, 12, 30): Holiday.new_years_day,
    datetime.date(2018, 12, 31): Holiday.new_years_day,
    datetime.date(2019, 1, 1): Holiday.new_years_day,
    datetime.date(2019, 2, 4): Holiday.spring_festival,
    datetime.date(2019, 2, 5): Holiday.spring_festival,
    datetime.date(2019, 2, 6): Holiday.spring_festival,
    datetime.date(2019, 2, 7): Holiday.spring_festival,
    datetime.date(2019, 2, 8): Holiday.spring_festival,
    datetime.date(2019, 2, 9): Holiday.spring_festival,
    datetime.date(2019, 2, 10): Holiday.spring_festival,
    datetime.date(2019, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2019, 4, 6): Holiday.tomb_sweeping_day,
    datetime.date(2019, 4, 7): Holiday.tomb_sweeping_day,
    datetime.date(2019, 5, 1): Holiday.labour_day,
    datetime.date(2019, 5, 2): Holiday.labour_day,
    datetime.date(2019, 5, 3): Holiday.labour_day,
    datetime.date(2019, 5, 4): Holiday.labour_day,
    datetime.date(2019, 6, 7): Holiday.dragon_boat_festival,
    datetime.date(2019, 6, 8): Holiday.dragon_boat_festival,
    datetime.date(2019, 6, 9): Holiday.dragon_boat_festival,
    datetime.date(2019, 9, 13): Holiday.mid_autumn_festival,
    datetime.date(2019, 9, 14): Holiday.mid_autumn_festival,
    datetime.date(2019, 9, 15): Holiday.mid_autumn_festival,
    datetime.date(2019, 10, 1): Holiday.national_day,
    datetime.date(2019, 10, 2): Holiday.national_day,
    datetime.date(2019, 10, 3): Holiday.national_day,
    datetime.date(2019, 10, 4): Holiday.national_day,
    datetime.date(2019, 10, 5): Holiday.national_day,
    datetime.date(2019, 10, 6): Holiday.national_day,
    datetime.date(2019, 10, 7): Holiday.national_day,
    datetime.date(2020, 1, 1): Holiday.new_years_day,
    datetime.date(2020, 1, 24): Holiday.spring_festival,
    datetime.date(2020, 1, 25): Holiday.spring_festival,
    datetime.date(2020, 1, 26): Holiday.spring_festival,
    datetime.date(2020, 1, 27): Holiday.spring_festival,
    datetime.date(2020, 1, 28): Holiday.spring_festival,
    datetime.date(2020, 1, 29): Holiday.spring_festival,
    datetime.date(2020, 1, 30): Holiday.spring_festival,
    datetime.date(2020, 1, 31): Holiday.spring_festival,
    datetime.date(2020, 2, 1): Holiday.spring_festival,
    datetime.date(2020, 2, 2): Holiday.spring_festival,
    datetime.date(2020, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2020, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2020, 4, 6): Holiday.tomb_sweeping_day,
    datetime.date(2020, 5, 1): Holiday.labour_day,
    datetime.date(2020, 5, 2): Holiday.labour_day,
    datetime.date(2020, 5, 3): Holiday.labour_day,
    datetime.date(2020, 5, 4): Holiday.labour_day,
    datetime.date(2020, 5, 5): Holiday.labour_day,
    datetime.date(2020, 6, 25): Holiday.dragon_boat_festival,
    datetime.date(2020, 6, 26): Holiday.dragon_boat_festival,
    datetime.date(2020, 6, 27): Holiday.dragon_boat_festival,
    datetime.date(2020, 10, 1): Holiday.national_day,
    datetime.date(2020, 10, 2): Holiday.national_day,
    datetime.date(2020, 10, 3): Holiday.national_day,
    datetime.date(2020, 10, 4): Holiday.national_day,
    datetime.date(2020, 10, 5): Holiday.national_day,
    datetime.date(2020, 10, 6): Holiday.national_day,
    datetime.date(2020, 10, 7): Holiday.national_day,
    datetime.date(2020, 10, 8): Holiday.national_day,
    datetime.date(2021, 1, 1): Holiday.new_years_day,
    datetime.date(2021, 1, 2): Holiday.new_years_day,
    datetime.date(2021, 1, 3): Holiday.new_years_day,
    datetime.date(2021, 2, 11): Holiday.spring_festival,
    datetime.date(2021, 2, 12): Holiday.spring_festival,
    datetime.date(2021, 2, 13): Holiday.spring_festival,
    datetime.date(2021, 2, 14): Holiday.spring_festival,
    datetime.date(2021, 2, 15): Holiday.spring_festival,
    datetime.date(2021, 2, 16): Holiday.spring_festival,
    datetime.date(2021, 2, 17): Holiday.spring_festival,
    datetime.date(2021, 4, 3): Holiday.tomb_sweeping_day,
    datetime.date(2021, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2021, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2021, 5, 1): Holiday.labour_day,
    datetime.date(2021, 5, 2): Holiday.labour_day,
    datetime.date(2021, 5, 3): Holiday.labour_day,
    datetime.date(2021, 5, 4): Holiday.labour_day,
    datetime.date(2021, 5, 5): Holiday.labour_day,
    datetime.date(2021, 6, 12): Holiday.dragon_boat_festival,
    datetime.date(2021, 6, 13): Holiday.dragon_boat_festival,
    datetime.date(2021, 6, 14): Holiday.dragon_boat_festival,
    datetime.date(2021, 9, 19): Holiday.mid_autumn_festival,
    datetime.date(2021, 9, 20): Holiday.mid_autumn_festival,
    datetime.date(2021, 9, 21): Holiday.mid_autumn_festival,
    datetime.date(2021, 10, 1): Holiday.national_day,
    datetime.date(2021, 10, 2): Holiday.national_day,
    datetime.date(2021, 10, 3): Holiday.national_day,
    datetime.date(2021, 10, 4): Holiday.national_day,
    datetime.date(2021, 10, 5): Holiday.national_day,
    datetime.date(2021, 10, 6): Holiday.national_day,
    datetime.date(2021, 10, 7): Holiday.national_day,
    datetime.date(2022, 1, 1): Holiday.new_years_day,
    datetime.date(2022, 1, 2): Holiday.new_years_day,
    datetime.date(2022, 1, 3): Holiday.new_years_day,
    datetime.date(2022, 1, 31): Holiday.spring_festival,
    datetime.date(2022, 2, 1): Holiday.spring_festival,
    datetime.date(2022, 2, 2): Holiday.spring_festival,
    datetime.date(2022, 2, 3): Holiday.spring_festival,
    datetime.date(2022, 2, 4): Holiday.spring_festival,
    datetime.date(2022, 2, 5): Holiday.spring_festival,
    datetime.date(2022, 2, 6): Holiday.spring_festival,
    datetime.date(2022, 4, 3): Holiday.tomb_sweeping_day,
    datetime.date(2022, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2022, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2022, 4, 30): Holiday.labour_day,
    datetime.date(2022, 5, 1): Holiday.labour_day,
    datetime.date(2022, 5, 2): Holiday.labour_day,
    datetime.date(2022, 5, 3): Holiday.labour_day,
    datetime.date(2022, 5, 4): Holiday.labour_day,
    datetime.date(2022, 6, 3): Holiday.dragon_boat_festival,
    datetime.date(2022, 6, 4): Holiday.dragon_boat_festival,
    datetime.date(2022, 6, 5): Holiday.dragon_boat_festival,
    datetime.date(2022, 9, 10): Holiday.mid_autumn_festival,
    datetime.date(2022, 9, 11): Holiday.mid_autumn_festival,
    datetime.date(2022, 9, 12): Holiday.mid_autumn_festival,
    datetime.date(2022, 10, 1): Holiday.national_day,
    datetime.date(2022, 10, 2): Holiday.national_day,
    datetime.date(2022, 10, 3): Holiday.national_day,
    datetime.date(2022, 10, 4): Holiday.national_day,
    datetime.date(2022, 10, 5): Holiday.national_day,
    datetime.date(2022, 10, 6): Holiday.national_day,
    datetime.date(2022, 10, 7): Holiday.national_day,
    datetime.date(2022, 12, 31): Holiday.new_years_day,
    datetime.date(2023, 1, 1): Holiday.new_years_day,
    datetime.date(2023, 1, 2): Holiday.new_years_day,
    datetime.date(2023, 1, 21): Holiday.spring_festival,
    datetime.date(2023, 1, 22): Holiday.spring_festival,
    datetime.date(2023, 1, 23): Holiday.spring_festival,
    datetime.date(2023, 1, 24): Holiday.spring_festival,
    datetime.date(2023, 1, 25): Holiday.spring_festival,
    datetime.date(2023, 1, 26): Holiday.spring_festival,
    datetime.date(2023, 1, 27): Holiday.spring_festival,
    datetime.date(2023, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2023, 4, 29): Holiday.labour_day,
    datetime.date(2023, 4, 30): Holiday.labour_day,
    datetime.date(2023, 5, 1): Holiday.labour_day,
    datetime.date(2023, 5, 2): Holiday.labour_day,
    datetime.date(2023, 5, 3): Holiday.labour_day,
    datetime.date(2023, 6, 22): Holiday.dragon_boat_festival,
    datetime.date(2023, 6, 23): Holiday.dragon_boat_festival,
    datetime.date(2023, 6, 24): Holiday.dragon_boat_festival,
    datetime.date(2023, 9, 29): Holiday.mid_autumn_festival,
    datetime.date(2023, 9, 30): Holiday.national_day,
    datetime.date(2023, 10, 1): Holiday.national_day,
    datetime.date(2023, 10, 2): Holiday.national_day,
    datetime.date(2023, 10, 3): Holiday.national_day,
    datetime.date(2023, 10, 4): Holiday.national_day,
    datetime.date(2023, 10, 5): Holiday.national_day,
    datetime.date(2023, 10, 6): Holiday.national_day,
    datetime.date(2023, 12, 30): Holiday.new_years_day,
    datetime.date(2023, 12, 31): Holiday.new_years_day,
    datetime.date(2024, 1, 1): Holiday.new_years_day,
    datetime.date(2024, 2, 10): Holiday.spring_festival,
    datetime.date(2024, 2, 11): Holiday.spring_festival,
    datetime.date(2024, 2, 12): Holiday.spring_festival,
    datetime.date(2024, 2, 13): Holiday.spring_festival,
    datetime.date(2024, 2, 14): Holiday.spring_festival,
    datetime.date(2024, 2, 15): Holiday.spring_festival,
    datetime.date(2024, 2, 16): Holiday.spring_festival,
    datetime.date(2024, 2, 17): Holiday.spring_festival,
    datetime.date(2024, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2024, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2024, 4, 6): Holiday.tomb_sweeping_day,
    datetime.date(2024, 5, 1): Holiday.labour_day,
    datetime.date(2024, 5, 2): Holiday.labour_day,
    datetime.date(2024, 5, 3): Holiday.labour_day,
    datetime.date(2024, 5, 4): Holiday.labour_day,
    datetime.date(2024, 5, 5): Holiday.labour_day,
    datetime.date(2024, 6, 10): Holiday.dragon_boat_festival,
    datetime.date(2024, 9, 15): Holiday.mid_autumn_festival,
    datetime.date(2024, 9, 16): Holiday.mid_autumn_festival,
    datetime.date(2024, 9, 17): Holiday.mid_autumn_festival,
    datetime.date(2024, 10, 1): Holiday.national_day,
    datetime.date(2024, 10, 2): Holiday.national_day,
    datetime.date(2024, 10, 3): Holiday.national_day,
    datetime.date(2024, 10, 4): Holiday.national_day,
    datetime.date(2024, 10, 5): Holiday.national_day,
    datetime.date(2024, 10, 6): Holiday.national_day,
    datetime.date(2024, 10, 7): Holiday.national_day,
    datetime.date(2025, 1, 1): Holiday.new_years_day,
    datetime.date(2025, 1, 28): Holiday.spring_festival,
    datetime.date(2025, 1, 29): Holiday.spring_festival,
    datetime.date(2025, 1, 30): Holiday.spring_festival,
    datetime.date(2025, 1, 31): Holiday.spring_festival,
    datetime.date(2025, 2, 1): Holiday.spring_festival,
    datetime.date(2025, 2, 2): Holiday.spring_festival,
    datetime.date(2025, 2, 3): Holiday.spring_festival,
    datetime.date(2025, 2, 4): Holiday.spring_festival,
    datetime.date(2025, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2025, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2025, 4, 6): Holiday.tomb_sweeping_day,
    datetime.date(2025, 5, 1): Holiday.labour_day,
    datetime.date(2025, 5, 2): Holiday.labour_day,
    datetime.date(2025, 5, 3): Holiday.labour_day,
    datetime.date(2025, 5, 4): Holiday.labour_day,
    datetime.date(2025, 5, 5): Holiday.labour_day,
    datetime.date(2025, 5, 31): Holiday.dragon_boat_festival,
    datetime.date(2025, 6, 1): Holiday.dragon_boat_festival,
    datetime.date(2025, 6, 2): Holiday.dragon_boat_festival,
    datetime.date(2025, 10, 1): Holiday.national_day,
    datetime.date(2025, 10, 2): Holiday.national_day,
    datetime.date(2025, 10, 3): Holiday.national_day,
    datetime.date(2025, 10, 4): Holiday.national_day,
    datetime.date(2025, 10, 5): Holiday.national_day,
    datetime.date(2025, 10, 6): Holiday.mid_autumn_festival,
    datetime.date(2025, 10, 7): Holiday.national_day,
    datetime.date(2025, 10, 8): Holiday.national_day,
    datetime.date(2026, 1, 1): Holiday.new_years_day,
    datetime.date(2026, 1, 2): Holiday.new_years_day,
    datetime.date(2026, 1, 3): Holiday.new_years_day,
    datetime.date(2026, 2, 15): Holiday.spring_festival,
    datetime.date(2026, 2, 16): Holiday.spring_festival,
    datetime.date(2026, 2, 17): Holiday.spring_festival,
    datetime.date(2026, 2, 18): Holiday.spring_festival,
    datetime.date(2026, 2, 19): Holiday.spring_festival,
    datetime.date(2026, 2, 20): Holiday.spring_festival,
    datetime.date(2026, 2, 21): Holiday.spring_festival,
    datetime.date(2026, 2, 22): Holiday.spring_festival,
    datetime.date(2026, 2, 23): Holiday.spring_festival,
    datetime.date(2026, 4, 4): Holiday.tomb_sweeping_day,
    datetime.date(2026, 4, 5): Holiday.tomb_sweeping_day,
    datetime.date(2026, 4, 6): Holiday.tomb_sweeping_day,
    datetime.date(2026, 5, 1): Holiday.labour_day,
    datetime.date(2026, 5, 2): Holiday.labour_day,
    datetime.date(2026, 5, 3): Holiday.labour_day,
    datetime.date(2026, 5, 4): Holiday.labour_day,
    datetime.date(2026, 5, 5): Holiday.labour_day,
    datetime.date(2026, 6, 19): Holiday.dragon_boat_festival,
    datetime.date(2026, 6, 20): Holiday.dragon_boat_festival,
    datetime.date(2026, 6, 21): Holiday.dragon_boat_festival,
    datetime.date(2026, 9, 25): Holiday.mid_autumn_festival,
    datetime.date(2026, 9, 26): Holiday.mid_autumn_festival,
    datetime.date(2026, 9, 27): Holiday.mid_autumn_festival,
    datetime.date(2026, 10, 1): Holiday.national_day,
    datetime.date(2026, 10, 2): Holiday.national_day,
    datetime.date(2026, 10, 3): Holiday.national_day,
    datetime.date(2026, 10, 4): Holiday.national_day,
    datetime.date(2026, 10, 5): Holiday.national_day,
    datetime.date(2026, 10, 6): Holiday.national_day,
    datetime.date(2026, 10, 7): Holiday.national_day,
}

# ==================== 调休工作日（周末但需上班）====================
workdays = {
    datetime.date(2004, 1, 17): Holiday.spring_festival,
    datetime.date(2004, 1, 18): Holiday.spring_festival,
    datetime.date(2004, 5, 8): Holiday.labour_day,
    datetime.date(2004, 5, 9): Holiday.labour_day,
    datetime.date(2004, 10, 9): Holiday.national_day,
    datetime.date(2004, 10, 10): Holiday.national_day,
    datetime.date(2005, 2, 5): Holiday.spring_festival,
    datetime.date(2005, 2, 6): Holiday.spring_festival,
    datetime.date(2005, 4, 30): Holiday.labour_day,
    datetime.date(2005, 5, 8): Holiday.labour_day,
    datetime.date(2005, 10, 8): Holiday.national_day,
    datetime.date(2005, 10, 9): Holiday.national_day,
    datetime.date(2006, 1, 28): Holiday.spring_festival,
    datetime.date(2006, 2, 5): Holiday.spring_festival,
    datetime.date(2006, 4, 29): Holiday.labour_day,
    datetime.date(2006, 4, 30): Holiday.labour_day,
    datetime.date(2006, 9, 30): Holiday.national_day,
    datetime.date(2006, 10, 8): Holiday.national_day,
    datetime.date(2006, 12, 30): Holiday.new_years_day,
    datetime.date(2006, 12, 31): Holiday.new_years_day,
    datetime.date(2007, 2, 17): Holiday.spring_festival,
    datetime.date(2007, 2, 25): Holiday.spring_festival,
    datetime.date(2007, 4, 28): Holiday.labour_day,
    datetime.date(2007, 4, 29): Holiday.labour_day,
    datetime.date(2007, 9, 29): Holiday.national_day,
    datetime.date(2007, 9, 30): Holiday.national_day,
    datetime.date(2007, 12, 29): Holiday.new_years_day,
    datetime.date(2008, 2, 2): Holiday.spring_festival,
    datetime.date(2008, 2, 3): Holiday.spring_festival,
    datetime.date(2008, 5, 4): Holiday.labour_day,
    datetime.date(2008, 9, 27): Holiday.national_day,
    datetime.date(2008, 9, 28): Holiday.national_day,
    datetime.date(2009, 1, 4): Holiday.new_years_day,
    datetime.date(2009, 1, 24): Holiday.spring_festival,
    datetime.date(2009, 2, 1): Holiday.spring_festival,
    datetime.date(2009, 5, 31): Holiday.dragon_boat_festival,
    datetime.date(2009, 9, 27): Holiday.national_day,
    datetime.date(2009, 10, 10): Holiday.national_day,
    datetime.date(2010, 2, 20): Holiday.spring_festival,
    datetime.date(2010, 2, 21): Holiday.spring_festival,
    datetime.date(2010, 6, 12): Holiday.dragon_boat_festival,
    datetime.date(2010, 6, 13): Holiday.dragon_boat_festival,
    datetime.date(2010, 9, 19): Holiday.mid_autumn_festival,
    datetime.date(2010, 9, 25): Holiday.mid_autumn_festival,
    datetime.date(2010, 9, 26): Holiday.national_day,
    datetime.date(2010, 10, 9): Holiday.national_day,
    datetime.date(2011, 1, 30): Holiday.spring_festival,
    datetime.date(2011, 2, 12): Holiday.spring_festival,
    datetime.date(2011, 4, 2): Holiday.tomb_sweeping_day,
    datetime.date(2011, 10, 8): Holiday.national_day,
    datetime.date(2011, 10, 9): Holiday.national_day,
    datetime.date(2011, 12, 31): Holiday.new_years_day,
    datetime.date(2012, 1, 21): Holiday.spring_festival,
    datetime.date(2012, 1, 29): Holiday.spring_festival,
    datetime.date(2012, 3, 31): Holiday.tomb_sweeping_day,
    datetime.date(2012, 4, 1): Holiday.tomb_sweeping_day,
    datetime.date(2012, 4, 28): Holiday.labour_day,
    datetime.date(2012, 9, 29): Holiday.national_day,
    datetime.date(2013, 1, 5): Holiday.new_years_day,
    datetime.date(2013, 1, 6): Holiday.new_years_day,
    datetime.date(2013, 2, 16): Holiday.spring_festival,
    datetime.date(2013, 2, 17): Holiday.spring_festival,
    datetime.date(2013, 4, 7): Holiday.tomb_sweeping_day,
    datetime.date(2013, 4, 27): Holiday.labour_day,
    datetime.date(2013, 4, 28): Holiday.labour_day,
    datetime.date(2013, 6, 8): Holiday.dragon_boat_festival,
    datetime.date(2013, 6, 9): Holiday.dragon_boat_festival,
    datetime.date(2013, 9, 22): Holiday.mid_autumn_festival,
    datetime.date(2013, 9, 29): Holiday.national_day,
    datetime.date(2013, 10, 12): Holiday.national_day,
    datetime.date(2014, 1, 26): Holiday.spring_festival,
    datetime.date(2014, 2, 8): Holiday.spring_festival,
    datetime.date(2014, 5, 4): Holiday.labour_day,
    datetime.date(2014, 9, 28): Holiday.national_day,
    datetime.date(2014, 10, 11): Holiday.national_day,
    datetime.date(2015, 1, 4): Holiday.new_years_day,
    datetime.date(2015, 2, 15): Holiday.spring_festival,
    datetime.date(2015, 2, 28): Holiday.spring_festival,
    datetime.date(2015, 9, 6): "Anti-Fascist 70th Day",
    datetime.date(2015, 10, 10): Holiday.national_day,
    datetime.date(2016, 2, 6): Holiday.spring_festival,
    datetime.date(2016, 2, 14): Holiday.spring_festival,
    datetime.date(2016, 6, 12): Holiday.dragon_boat_festival,
    datetime.date(2016, 9, 18): Holiday.mid_autumn_festival,
    datetime.date(2016, 10, 8): Holiday.national_day,
    datetime.date(2016, 10, 9): Holiday.national_day,
    datetime.date(2017, 1, 22): Holiday.spring_festival,
    datetime.date(2017, 2, 4): Holiday.spring_festival,
    datetime.date(2017, 4, 1): Holiday.tomb_sweeping_day,
    datetime.date(2017, 5, 27): Holiday.dragon_boat_festival,
    datetime.date(2017, 9, 30): Holiday.national_day,
    datetime.date(2018, 2, 11): Holiday.spring_festival,
    datetime.date(2018, 2, 24): Holiday.spring_festival,
    datetime.date(2018, 4, 8): Holiday.tomb_sweeping_day,
    datetime.date(2018, 4, 28): Holiday.labour_day,
    datetime.date(2018, 9, 29): Holiday.national_day,
    datetime.date(2018, 9, 30): Holiday.national_day,
    datetime.date(2018, 12, 29): Holiday.new_years_day,
    datetime.date(2019, 2, 2): Holiday.spring_festival,
    datetime.date(2019, 2, 3): Holiday.spring_festival,
    datetime.date(2019, 4, 28): Holiday.labour_day,
    datetime.date(2019, 5, 5): Holiday.labour_day,
    datetime.date(2019, 9, 29): Holiday.national_day,
    datetime.date(2019, 10, 12): Holiday.national_day,
    datetime.date(2020, 1, 19): Holiday.spring_festival,
    datetime.date(2020, 4, 26): Holiday.labour_day,
    datetime.date(2020, 5, 9): Holiday.labour_day,
    datetime.date(2020, 6, 28): Holiday.dragon_boat_festival,
    datetime.date(2020, 9, 27): Holiday.national_day,
    datetime.date(2020, 10, 10): Holiday.national_day,
    datetime.date(2021, 2, 7): Holiday.spring_festival,
    datetime.date(2021, 2, 20): Holiday.spring_festival,
    datetime.date(2021, 4, 25): Holiday.labour_day,
    datetime.date(2021, 5, 8): Holiday.labour_day,
    datetime.date(2021, 9, 18): Holiday.mid_autumn_festival,
    datetime.date(2021, 9, 26): Holiday.national_day,
    datetime.date(2021, 10, 9): Holiday.national_day,
    datetime.date(2022, 1, 29): Holiday.spring_festival,
    datetime.date(2022, 1, 30): Holiday.spring_festival,
    datetime.date(2022, 4, 2): Holiday.tomb_sweeping_day,
    datetime.date(2022, 4, 24): Holiday.labour_day,
    datetime.date(2022, 5, 7): Holiday.labour_day,
    datetime.date(2022, 10, 8): Holiday.national_day,
    datetime.date(2022, 10, 9): Holiday.national_day,
    datetime.date(2023, 1, 28): Holiday.spring_festival,
    datetime.date(2023, 1, 29): Holiday.spring_festival,
    datetime.date(2023, 4, 23): Holiday.labour_day,
    datetime.date(2023, 5, 6): Holiday.labour_day,
    datetime.date(2023, 6, 25): Holiday.dragon_boat_festival,
    datetime.date(2023, 10, 7): Holiday.national_day,
    datetime.date(2023, 10, 8): Holiday.national_day,
    datetime.date(2024, 2, 4): Holiday.spring_festival,
    datetime.date(2024, 2, 18): Holiday.spring_festival,
    datetime.date(2024, 4, 7): Holiday.tomb_sweeping_day,
    datetime.date(2024, 4, 28): Holiday.labour_day,
    datetime.date(2024, 5, 11): Holiday.labour_day,
    datetime.date(2024, 9, 14): Holiday.mid_autumn_festival,
    datetime.date(2024, 9, 29): Holiday.national_day,
    datetime.date(2024, 10, 12): Holiday.national_day,
    datetime.date(2025, 1, 26): Holiday.spring_festival,
    datetime.date(2025, 2, 8): Holiday.spring_festival,
    datetime.date(2025, 4, 27): Holiday.labour_day,
    datetime.date(2025, 9, 28): Holiday.national_day,
    datetime.date(2025, 10, 11): Holiday.national_day,
    datetime.date(2026, 1, 4): Holiday.new_years_day,
    datetime.date(2026, 2, 14): Holiday.spring_festival,
    datetime.date(2026, 2, 28): Holiday.spring_festival,
    datetime.date(2026, 5, 9): Holiday.labour_day,
    datetime.date(2026, 9, 20): Holiday.national_day,
    datetime.date(2026, 10, 10): Holiday.national_day,
}

# ==================== 核心函数 ====================


def _wrap_date(date: Any) -> Any:
    """将 datetime 转换为 date"""
    if isinstance(date, datetime.datetime):
        return date.date()
    return date


def _validate_date(date: Any) -> datetime.date:
    """检查日期是否在支持范围内"""
    date = _wrap_date(date)
    if not isinstance(date, datetime.date):
        raise TypeError(f"unsupported type {type(date)}, expected datetime.date")
    min_year = min(holidays.keys()).year
    max_year = max(holidays.keys()).year
    if not (min_year <= date.year <= max_year):
        raise NotImplementedError(
            f"no available data for year {date.year}, only year between [{min_year}, {max_year}] supported"
        )
    return date


def is_trading_day(date: Union[datetime.date, datetime.datetime]) -> bool:
    """判断 A 股交易所开市日；周末调休补班日仍按休市处理。

    ``workdays`` 保存民用调休补班日，不代表证券交易所开市。该纯本地函数
    可供 ZHB 加载期间使用，不会反向导入 ZHB。
    """
    day = _validate_date(date)
    return day.weekday() < 5 and day not in holidays


def is_workday(date: Union[datetime.date, datetime.datetime]) -> bool:
    """兼容旧名称：判断 A 股交易日，不把周末调休补班日当成交易日。"""
    day = _validate_date(date)
    if not is_trading_day(day):
        return False

    # ZHB 只补充本地表未列出的工作日休市信息；绝不能覆盖周末休市规则。
    try:
        from core.zhb_client import get_holidays

        zhb_holidays = get_holidays()
        if zhb_holidays and day.strftime("%Y%m%d") in zhb_holidays:
            return False
    except Exception:
        pass
    return True


def previous_trading_day(
    date: Union[datetime.date, datetime.datetime], include_current: bool = False
) -> datetime.date:
    """获取指定日期之前最近的交易日；``include_current`` 控制是否包含当天。"""
    day = _validate_date(date)
    if not include_current:
        day -= datetime.timedelta(days=1)
    for _ in range(30):
        if is_trading_day(day):
            return day
        day -= datetime.timedelta(days=1)
    raise NotImplementedError("no trading day found in the previous 30 days")


def add_trading_days(date: Union[datetime.date, datetime.datetime], offset: int) -> datetime.date:
    """从给定日期向前或向后移动 ``offset`` 个交易日（起始日不计入偏移）。"""
    day = _validate_date(date)
    if offset == 0:
        return day
    step = 1 if offset > 0 else -1
    remaining = abs(offset)
    while remaining:
        day += datetime.timedelta(days=step)
        if is_trading_day(day):
            remaining -= 1
    return day


def trading_days_between(
    start: Union[datetime.date, datetime.datetime],
    end: Union[datetime.date, datetime.datetime],
) -> int:
    """返回 ``(start, end]`` 内的交易日数；反向区间返回负数。"""
    first = _validate_date(start)
    last = _validate_date(end)
    if first == last:
        return 0
    if first > last:
        return -trading_days_between(last, first)

    count = 0
    day = first + datetime.timedelta(days=1)
    while day <= last:
        if is_trading_day(day):
            count += 1
        day += datetime.timedelta(days=1)
    return count


def latest_market_data_date(
    as_of: Optional[Union[datetime.date, datetime.datetime]] = None,
) -> datetime.date:
    """返回数据年龄的基准交易日：交易日 9:30 前取上一交易日，其后取当天。

    显式传入 ``date`` 时按该日收盘后处理；不传时使用本机当前时间。
    """
    value = datetime.datetime.now() if as_of is None else as_of
    if isinstance(value, datetime.datetime):
        day = _validate_date(value.date())
        local_time = value.timetz().replace(tzinfo=None)
        session_started = local_time >= datetime.time(9, 30)
    else:
        day = _validate_date(value)
        session_started = True

    if session_started and is_trading_day(day):
        return day
    return previous_trading_day(day, include_current=False)


def trading_day_age(
    data_date: Union[datetime.date, datetime.datetime],
    as_of: Optional[Union[datetime.date, datetime.datetime]] = None,
) -> int:
    """返回数据日期至当前有效行情日期之间经过的交易日数。"""
    return trading_days_between(data_date, latest_market_data_date(as_of))


def trading_day_window(
    days: int, as_of: Optional[Union[datetime.date, datetime.datetime]] = None
) -> Tuple[datetime.date, datetime.date]:
    """返回最近 ``days`` 个交易日的闭区间日期，末端遵循 9:30 分界。"""
    if days < 1:
        raise ValueError("days must be a positive integer")
    end = latest_market_data_date(as_of)
    start = add_trading_days(end, -(days - 1))
    return start, end


def recent_trading_dates(
    count: int, as_of: Optional[Union[datetime.date, datetime.datetime]] = None
) -> List[datetime.date]:
    """按从新到旧顺序返回最近 ``count`` 个实际交易日。"""
    if count < 0:
        raise ValueError("count must be non-negative")
    if count == 0:
        return []
    day = latest_market_data_date(as_of)
    result = [day]
    for _ in range(count - 1):
        day = previous_trading_day(day, include_current=False)
        result.append(day)
    return result


# ═══════════════════════════════════════════════════════════════
# V14.2 新增：ZHB neednote.dat 官方日历补充
# ═══════════════════════════════════════════════════════════════


def _load_zhb_neednote_supplement() -> Tuple[Set[datetime.date], Set[datetime.date]]:
    """V14.2：加载 ZHB neednote.dat 官方休市日+调休补班日作为本地字典的补充。

    V14.2.1 改进：预过滤空元素 + 全角空格，避免异常开销。

    Returns:
        (supplement_holidays: set, supplement_workdays: set)
        加载失败时返回 (set(), set())
    """
    try:
        from core.zhb_client import get_zhb_official_holidays, get_zhb_official_jyweek

        supplement_holidays: Set[datetime.date] = set()
        # V14.2.1: 预过滤空元素和空白字符串
        for d_str in (s for s in get_zhb_official_holidays() if s and s.strip()):
            d_str = d_str.strip()
            try:
                year = int(d_str[:4])
                month = int(d_str[4:6])
                day = int(d_str[6:8])
                supplement_holidays.add(datetime.date(year, month, day))
            except (ValueError, TypeError, IndexError):
                continue
        supplement_workdays: Set[datetime.date] = set()
        for d_str in (s for s in get_zhb_official_jyweek() if s and s.strip()):
            d_str = d_str.strip()
            try:
                year = int(d_str[:4])
                month = int(d_str[4:6])
                day = int(d_str[6:8])
                supplement_workdays.add(datetime.date(year, month, day))
            except (ValueError, TypeError, IndexError):
                continue
        return supplement_holidays, supplement_workdays
    except Exception:
        return set(), set()


# V14.2 模块级缓存（一次性加载）
_zhb_holidays_supplement: Set[datetime.date] = set()
_zhb_workdays_supplement: Set[datetime.date] = set()
_zhb_supplement_loaded: bool = False
# V14.2.1: 记录上次加载时的 ZHB 数据日期，检测到变更时自动重载
_last_zhb_supplement_date: str = ""


def _ensure_zhb_supplement_loaded() -> None:
    """确保 ZHB 补充数据已加载（V14.2 + V14.2.1 自动重载）。

    V14.2.1 改进：当 ZHB 数据日期变更时（如盘后守护进程下载了新 zhb.zip），
    自动重新加载补充日历，避免缓存陈旧。
    """
    global _zhb_holidays_supplement, _zhb_workdays_supplement, _zhb_supplement_loaded, _last_zhb_supplement_date
    try:
        from core.zhb_client import get_zhb

        zhb = get_zhb()
        current_date = zhb.date if zhb is not None else ""
        # 已加载且日期未变：直接返回
        if _zhb_supplement_loaded and current_date == _last_zhb_supplement_date:
            return
        # 数据日期更新或首次加载：重新读取
        _zhb_holidays_supplement, _zhb_workdays_supplement = _load_zhb_neednote_supplement()
        _last_zhb_supplement_date = current_date
        _zhb_supplement_loaded = True
    except Exception:
        # 加载失败时仍标记为已加载（避免每次调用都重试）
        if not _zhb_supplement_loaded:
            _zhb_holidays_supplement, _zhb_workdays_supplement = set(), set()
            _zhb_supplement_loaded = True


def invalidate_zhb_supplement_cache() -> None:
    """强制清空 ZHB 补充日历缓存（V14.2.1 新增）。

    用法：zhb_sync.py 下载完新 zhb.zip 后可调用此函数触发 reload。
    """
    global _zhb_holidays_supplement, _zhb_workdays_supplement, _zhb_supplement_loaded, _last_zhb_supplement_date
    _zhb_holidays_supplement = set()
    _zhb_workdays_supplement = set()
    _zhb_supplement_loaded = False
    _last_zhb_supplement_date = ""


def is_workday_with_zhb_supplement(
    date: Union[datetime.date, datetime.datetime],
) -> bool:
    """在本地交易日历上补充 ZHB neednote.dat 的工作日休市信息。

    ZHB 补班日属于民用日历信息，不能使周末成为 A 股交易日。
    """
    day = _validate_date(date)
    if not is_trading_day(day):
        return False

    _ensure_zhb_supplement_loaded()
    if day in _zhb_holidays_supplement:
        return False

    # ZHB holidays 作为本地和 neednote 日历之外的辅助校验。
    try:
        from core.zhb_client import get_holidays

        zhb_holidays = get_holidays()
        if zhb_holidays and day.strftime("%Y%m%d") in zhb_holidays:
            return False
    except Exception:
        pass
    return True


def get_zhb_supplement_count() -> dict:
    """V14.2：返回 ZHB 补充日历的统计信息。

    Returns:
        {"holidays": N, "workdays": M, "loaded": bool}
    """
    _ensure_zhb_supplement_loaded()
    return {
        "holidays": len(_zhb_holidays_supplement),
        "workdays": len(_zhb_workdays_supplement),
        "loaded": _zhb_supplement_loaded,
    }


def get_last_trading_day(
    date: Optional[Union[datetime.date, datetime.datetime]] = None,
) -> datetime.date:
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
    date = cast(datetime.date, _wrap_date(date))
    # 向前回溯直到找到交易日（最多回溯 30 天）
    for _ in range(30):
        try:
            if is_workday(date):
                return date
        except NotImplementedError:
            # 跨年度时年份超出范围，回退到 weekday 判断
            weekday = date.weekday()
            if weekday <= 4:
                return date
        date -= datetime.timedelta(days=1)
    # 极端情况：30 天内无交易日（不应该发生）
    raise NotImplementedError("no trading day found in the last 30 days")


def get_next_trading_day(
    date: Optional[Union[datetime.date, datetime.datetime]] = None,
) -> datetime.date:
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
    date = cast(datetime.date, _wrap_date(date))
    date += datetime.timedelta(days=1)
    # 向后查找直到找到交易日（最多查找 30 天）
    for _ in range(30):
        try:
            if is_workday(date):
                return date
        except NotImplementedError:
            # 年份超出范围，无法判断
            raise
        date += datetime.timedelta(days=1)
    raise NotImplementedError("no trading day found in the next 30 days")


def data_years() -> tuple:
    """返回当前数据支持的年份范围 (min_year, max_year)"""
    all_dates = list(holidays.keys()) + list(workdays.keys())
    return min(d.year for d in all_dates), max(d.year for d in all_dates)


def _cli_update(backup: bool = False, dry_run: bool = False) -> None:
    """调用 scripts/update_calendar.py 更新日历数据。"""
    import subprocess
    import sys
    import os

    script_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "update_calendar.py"
    )
    if not os.path.isfile(script_path):
        print(f"错误：找不到更新脚本 {script_path}", file=sys.stderr)
        sys.exit(1)

    cmd = [sys.executable, script_path]
    if backup:
        cmd.append("--backup")
    if dry_run:
        cmd.append("--dry-run")
    raise SystemExit(subprocess.call(cmd))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="A股交易日历（stock_calendar.py）")
    parser.add_argument("--check", action="store_true", help="检查当前数据支持的年份范围")
    parser.add_argument("--update", action="store_true", help="从 chinese-calendar 库更新数据")
    parser.add_argument(
        "--backup", action="store_true", help="更新前自动备份旧文件（配合 --update 使用）"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="仅预览更新内容，不写入文件（配合 --update 使用）"
    )
    args = parser.parse_args()

    if args.check:
        min_y, max_y = data_years()
        print(f"当前日历数据范围: {min_y}-{max_y}")
        print(f"节假日条目数: {len(holidays)}")
        print(f"调休工作日条目数: {len(workdays)}")
    elif args.update:
        _cli_update(backup=args.backup, dry_run=args.dry_run)
    else:
        parser.print_help()

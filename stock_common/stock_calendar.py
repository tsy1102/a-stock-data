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

def _wrap_date(date):
    """将 datetime 转换为 date"""
    if isinstance(date, datetime.datetime):
        return date.date()
    return date


def _validate_date(date):
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


def is_workday(date):
    """判断是否为工作日（A股交易日）

    V14.0 修复：本地 holidays/workdays 字典作为权威数据，ZHB 仅作为辅助校验。
      之前的 V10.0 实现有 Bug：当 ZHB 残缺（仅 37 条数据）且某个日期在 ZHB 中
      找不到时，会错误返回 weekday <= 4，导致 2025-1-1/2026-1-1 等节假日
      被误判为工作日。

    决策顺序（V14.0 修正）：
      1. 本地 holidays 字典（621 条，2004-2026+ 完整覆盖）→ False
      2. 本地 workdays 字典（调休工作日）→ True
      3. ZHB 数据（1991-2030，但实际只有 37 条）作为补充校验 → 命中即 False
      4. 周末判断（weekday > 4）→ False
      5. 兜底：weekday <= 4 → True

    Args:
        date: datetime.date 或 datetime.datetime

    Returns:
        bool: True=交易日, False=休市日
    """
    try:
        date = _validate_date(date)
        weekday = date.weekday()

        # 1. 权威数据：本地 holidays（先检查本地，避免 ZHB 残缺导致误判）
        if date in holidays:
            return False

        # 2. 权威数据：本地 workdays（调休工作日）
        if date in workdays:
            return True

        # 3. 辅助校验：ZHB 数据（残缺时不影响本地判断）
        try:
            from core.zhb_client import get_holidays
            zhb_holidays = get_holidays()
            if zhb_holidays:
                date_str = date.strftime("%Y%m%d")
                if date_str in zhb_holidays:
                    return False  # ZHB 命中节假日
        except Exception:
            pass

        # 4 & 5. 兜底：周末 vs 工作日
        return weekday <= 4
    except NotImplementedError:
        # 年份超出范围，抛出异常供上层处理
        raise


# ═══════════════════════════════════════════════════════════════
# V14.2 新增：ZHB neednote.dat 官方日历补充
# ═══════════════════════════════════════════════════════════════

def _load_zhb_neednote_supplement():
    """V14.2：加载 ZHB neednote.dat 官方休市日+调休补班日作为本地字典的补充。

    V14.2.1 改进：预过滤空元素 + 全角空格，避免异常开销。

    Returns:
        (supplement_holidays: set, supplement_workdays: set)
        加载失败时返回 (set(), set())
    """
    try:
        from core.zhb_client import get_zhb_official_holidays, get_zhb_official_jyweek
        supplement_holidays = set()
        # V14.2.1: 预过滤空元素和空白字符串
        for d_str in (s for s in get_zhb_official_holidays() if s and s.strip()):
            d_str = d_str.strip()
            try:
                year = int(d_str[:4])
                month = int(d_str[4:6])
                day = int(d_str[6:8])
                supplement_holidays.add(date(year, month, day))
            except (ValueError, TypeError, IndexError):
                continue
        supplement_workdays = set()
        for d_str in (s for s in get_zhb_official_jyweek() if s and s.strip()):
            d_str = d_str.strip()
            try:
                year = int(d_str[:4])
                month = int(d_str[4:6])
                day = int(d_str[6:8])
                supplement_workdays.add(date(year, month, day))
            except (ValueError, TypeError, IndexError):
                continue
        return supplement_holidays, supplement_workdays
    except Exception:
        return set(), set()


# V14.2 模块级缓存（一次性加载）
_zhb_holidays_supplement: set = set()
_zhb_workdays_supplement: set = set()
_zhb_supplement_loaded: bool = False
# V14.2.1: 记录上次加载时的 ZHB 数据日期，检测到变更时自动重载
_last_zhb_supplement_date: str = ""


def _ensure_zhb_supplement_loaded():
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


def is_workday_with_zhb_supplement(date):
    """V14.2：在 is_workday() 基础上叠加 ZHB neednote.dat 补充日历。

    优先级：
      1. 本地 holidays 字典（621 条）→ False
      2. 本地 workdays 字典（调休工作日）→ True
      3. ZHB neednote.dat 官方休市日（补充未来日期）→ False
      4. ZHB neednote.dat 官方调休补班日 → True
      5. ZHB holidays（残缺数据，仅辅助校验）→ 命中即 False
      6. 周末判断 → False
      7. 兜底：weekday <= 4 → True

    本地字典不可用时（如年内日期），ZHB 补充数据可作为兜底。
    """
    date = _validate_date(date)
    weekday = date.weekday()

    # 1 & 2. 本地字典（V14.0 权威数据）
    if date in holidays:
        return False
    if date in workdays:
        return True

    # 3 & 4. V14.2 新增：ZHB neednote.dat 补充
    _ensure_zhb_supplement_loaded()
    if date in _zhb_holidays_supplement:
        return False
    if date in _zhb_workdays_supplement:
        return True

    # 5. V14.0 ZHB 残缺数据辅助校验
    try:
        from core.zhb_client import get_holidays
        zhb_holidays = get_holidays()
        if zhb_holidays:
            date_str = date.strftime("%Y%m%d")
            if date_str in zhb_holidays:
                return False
    except Exception:
        pass

    # 6 & 7. 周末 vs 工作日
    return weekday <= 4


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
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "scripts", "update_calendar.py"
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
    import sys

    parser = argparse.ArgumentParser(description="A股交易日历（stock_calendar.py）")
    parser.add_argument("--check", action="store_true",
                        help="检查当前数据支持的年份范围")
    parser.add_argument("--update", action="store_true",
                        help="从 chinese-calendar 库更新数据")
    parser.add_argument("--backup", action="store_true",
                        help="更新前自动备份旧文件（配合 --update 使用）")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅预览更新内容，不写入文件（配合 --update 使用）")
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

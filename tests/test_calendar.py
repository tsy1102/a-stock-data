# -*- coding: utf-8 -*-
"""tests/test_calendar.py — A股交易日历模块单元测试

覆盖：
1. 已知节假日、调休日、周末交易日验证
2. is_workday 基础逻辑
3. 边界日期、错误输入处理
"""

import datetime
import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_calendar import is_workday, _wrap_date, _validate_date


class TestWrapDate:
    """datetime → date 转换测试"""

    def test_datetime_to_date(self):
        d = datetime.datetime(2025, 5, 1, 10, 30, 0)
        assert _wrap_date(d) == datetime.date(2025, 5, 1)

    def test_date_stays_date(self):
        d = datetime.date(2025, 5, 1)
        assert _wrap_date(d) == d


class TestValidateDate:
    """日期范围验证测试"""

    def test_valid_date_2025(self):
        d = datetime.date(2025, 5, 1)
        assert _validate_date(d) == d

    def test_valid_date_2026(self):
        d = datetime.date(2026, 6, 22)
        assert _validate_date(d) == d

    def test_invalid_type_raises_typeerror(self):
        with pytest.raises(TypeError):
            _validate_date("2025-05-01")

    def test_out_of_range_raises_notimplemented(self):
        # 年份 1900 不在支持范围内
        with pytest.raises(NotImplementedError):
            _validate_date(datetime.date(1900, 1, 1))


class TestKnownHolidays:
    """已知法定节假日（休市日）测试"""

    def test_new_year_2025_jan_1(self):
        # 2025年1月1日：元旦
        assert is_workday(datetime.date(2025, 1, 1)) is False

    def test_spring_festival_2025_first_day(self):
        # 2025年春节 1/28 - 2/4
        assert is_workday(datetime.date(2025, 1, 28)) is False

    def test_labour_2025_may_1(self):
        # 2025年劳动节 5/1 - 5/5
        assert is_workday(datetime.date(2025, 5, 1)) is False

    def test_national_day_2025_oct_1(self):
        # 2025年国庆节 10/1 - 10/8
        assert is_workday(datetime.date(2025, 10, 1)) is False

    def test_2026_new_year_jan_1(self):
        assert is_workday(datetime.date(2026, 1, 1)) is False

    def test_2026_spring_festival_week(self):
        # 2026年春节 2/15 - 2/23
        assert is_workday(datetime.date(2026, 2, 18)) is False

    def test_2026_labour_day(self):
        assert is_workday(datetime.date(2026, 5, 1)) is False

    def test_2026_dragon_boat_jun_19(self):
        # 2026年端午节 6/19 - 6/21
        assert is_workday(datetime.date(2026, 6, 20)) is False

    def test_2026_mid_autumn_sep_25(self):
        # 2026年中秋节 9/25 - 9/27
        assert is_workday(datetime.date(2026, 9, 26)) is False

    def test_2026_national_day_oct_1_to_7(self):
        # 2026年国庆节 10/1 - 10/7
        assert is_workday(datetime.date(2026, 10, 5)) is False


class TestKnownWorkdays:
    """已知调休工作日测试（周末但需上班）"""

    def test_2025_spring_festival_makeup_jan_26(self):
        # 2025年春节调休：1月26日（周日）→ 工作日
        assert is_workday(datetime.date(2025, 1, 26)) is True

    def test_2025_spring_festival_makeup_feb_8(self):
        # 2025年春节调休：2月8日（周六）→ 工作日
        assert is_workday(datetime.date(2025, 2, 8)) is True

    def test_2025_labour_makeup_apr_27(self):
        # 2025年劳动节调休：4月27日（周日）→ 工作日
        assert is_workday(datetime.date(2025, 4, 27)) is True

    def test_2025_national_day_makeup_sep_28(self):
        # 2025年国庆调休：9月28日（周日）→ 工作日
        assert is_workday(datetime.date(2025, 9, 28)) is True

    def test_2025_national_day_makeup_oct_11(self):
        # 2025年国庆调休：10月11日（周六）→ 工作日
        assert is_workday(datetime.date(2025, 10, 11)) is True

    def test_2026_spring_festival_makeup_feb_14(self):
        # 2026年春节调休：2月14日（周六）→ 工作日
        assert is_workday(datetime.date(2026, 2, 14)) is True

    def test_2026_spring_festival_makeup_feb_28(self):
        # 2026年春节调休：2月28日（周六）→ 工作日
        assert is_workday(datetime.date(2026, 2, 28)) is True

    def test_2026_labour_makeup_may_9(self):
        # 2026年劳动节调休：5月9日（周六）→ 工作日
        assert is_workday(datetime.date(2026, 5, 9)) is True

    def test_2026_national_day_makeup_sep_20(self):
        # 2026年国庆调休：9月20日（周日）→ 工作日
        assert is_workday(datetime.date(2026, 9, 20)) is True

    def test_2026_national_day_makeup_oct_10(self):
        # 2026年国庆调休：10月10日（周六）→ 工作日
        assert is_workday(datetime.date(2026, 10, 10)) is True


class TestRegularWeekdays:
    """普通周一至周五（非节假日）应为交易日"""

    def test_normal_monday_2025(self):
        # 2025年3月3日 周一
        assert is_workday(datetime.date(2025, 3, 3)) is True

    def test_normal_friday_2025(self):
        # 2025年6月20日 周五
        assert is_workday(datetime.date(2025, 6, 20)) is True

    def test_normal_friday_2026(self):
        # 2026年6月26日 周五（非节假日）
        assert is_workday(datetime.date(2026, 6, 26)) is True


class TestWeekendsAreNonWorkdays:
    """普通周末（非调休日）应休市"""

    def test_saturday_2025_jun_21(self):
        # 2025年6月21日 周六
        assert is_workday(datetime.date(2025, 6, 21)) is False

    def test_sunday_2025_jun_22(self):
        # 2025年6月22日 周日
        assert is_workday(datetime.date(2025, 6, 22)) is False

    def test_saturday_2026_jul_4(self):
        # 2026年7月4日 周六（非调休日）
        assert is_workday(datetime.date(2026, 7, 4)) is False


class TestWithDatetimeInput:
    """datetime 对象输入也应正常工作"""

    def test_datetime_input_workday(self):
        dt = datetime.datetime(2025, 6, 20, 9, 30, 0)
        assert is_workday(dt) is True

    def test_datetime_input_weekend(self):
        dt = datetime.datetime(2025, 6, 21, 10, 0, 0)
        assert is_workday(dt) is False


class TestEdgeCases:
    """边界与错误输入处理"""

    def test_out_of_range_raises(self):
        with pytest.raises(NotImplementedError):
            is_workday(datetime.date(1900, 1, 1))

    def test_string_input_raises(self):
        with pytest.raises(TypeError):
            is_workday("2025-05-01")

    def test_none_input_raises(self):
        with pytest.raises(TypeError):
            is_workday(None)

    def test_int_input_raises(self):
        with pytest.raises(TypeError):
            is_workday(20250620)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

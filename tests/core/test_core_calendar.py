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

from core import zhb_client
from stock_common.stock_calendar import (
    _validate_date,
    _wrap_date,
    add_trading_days,
    is_trading_day,
    is_workday,
    latest_market_data_date,
    recent_trading_dates,
    trading_day_age,
    trading_day_window,
    trading_days_between,
)


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


class TestMakeupWeekendsAreNotTradingDays:
    """民用调休补班日周末仍是证券市场休市日。"""

    def test_2025_spring_festival_makeup_jan_26(self):
        # 2025年春节调休：1月26日（周日）→ 市场休市
        assert is_workday(datetime.date(2025, 1, 26)) is False

    def test_2025_spring_festival_makeup_feb_8(self):
        # 2025年春节调休：2月8日（周六）→ 市场休市
        assert is_workday(datetime.date(2025, 2, 8)) is False

    def test_2025_labour_makeup_apr_27(self):
        # 2025年劳动节调休：4月27日（周日）→ 市场休市
        assert is_workday(datetime.date(2025, 4, 27)) is False

    def test_2025_national_day_makeup_sep_28(self):
        # 2025年国庆调休：9月28日（周日）→ 市场休市
        assert is_workday(datetime.date(2025, 9, 28)) is False

    def test_2025_national_day_makeup_oct_11(self):
        # 2025年国庆调休：10月11日（周六）→ 市场休市
        assert is_workday(datetime.date(2025, 10, 11)) is False

    def test_2026_spring_festival_makeup_feb_14(self):
        # 2026年春节调休：2月14日（周六）→ 市场休市
        assert is_workday(datetime.date(2026, 2, 14)) is False

    def test_2026_spring_festival_makeup_feb_28(self):
        # 2026年春节调休：2月28日（周六）→ 市场休市
        assert is_workday(datetime.date(2026, 2, 28)) is False

    def test_2026_labour_makeup_may_9(self):
        # 交易所 5 月 6 日复市；5 月 9 日周六仍休市
        assert is_workday(datetime.date(2026, 5, 9)) is False

    def test_2026_national_day_makeup_sep_20(self):
        # 2026年国庆调休：9月20日（周日）→ 市场休市
        assert is_workday(datetime.date(2026, 9, 20)) is False

    def test_2026_national_day_makeup_oct_10(self):
        # 2026年国庆调休：10月10日（周六）→ 市场休市
        assert is_workday(datetime.date(2026, 10, 10)) is False


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


class TestTradingDayArithmetic:
    def test_makeup_weekend_is_closed_and_next_session_skips_it(self):
        assert is_trading_day(datetime.date(2026, 5, 9)) is False
        assert add_trading_days(datetime.date(2026, 5, 8), 1) == datetime.date(2026, 5, 11)

    def test_holiday_weekend_age_counts_sessions_not_calendar_days(self):
        start = datetime.date(2026, 9, 24)
        end = datetime.date(2026, 9, 28)
        assert trading_days_between(start, end) == 1
        assert trading_days_between(end, start) == -1

    def test_market_data_reference_has_0930_boundary(self):
        before_open = datetime.datetime(2026, 9, 28, 9, 29)
        at_open = datetime.datetime(2026, 9, 28, 9, 30)
        assert latest_market_data_date(before_open) == datetime.date(2026, 9, 24)
        assert latest_market_data_date(at_open) == datetime.date(2026, 9, 28)
        assert trading_day_age(datetime.date(2026, 9, 24), before_open) == 0
        assert trading_day_age(datetime.date(2026, 9, 24), at_open) == 1

    def test_trade_day_window_skips_mid_autumn_closure_and_makeup_sunday(self):
        start, end = trading_day_window(5, datetime.datetime(2026, 9, 28, 9, 30))
        assert (start, end) == (datetime.date(2026, 9, 21), datetime.date(2026, 9, 28))
        assert recent_trading_dates(4, datetime.date(2026, 9, 28)) == [
            datetime.date(2026, 9, 28),
            datetime.date(2026, 9, 24),
            datetime.date(2026, 9, 23),
            datetime.date(2026, 9, 22),
        ]

    def test_zhb_freshness_uses_trading_day_age(self, monkeypatch):
        current = [datetime.datetime(2026, 9, 28, 9, 29)]

        class FixedDateTime:
            @staticmethod
            def now():
                return current[0]

            @staticmethod
            def strptime(value, fmt):
                return datetime.datetime.strptime(value, fmt)

        monkeypatch.setattr(zhb_client, "datetime", FixedDateTime)
        fake_zhb = type("FakeZhb", (), {"date": "20260924"})()

        assert zhb_client.ZhbData.is_fresh(fake_zhb, max_delay_days=0) is True
        current[0] = datetime.datetime(2026, 9, 28, 9, 30)
        assert zhb_client.ZhbData.is_fresh(fake_zhb, max_delay_days=0) is False
        assert zhb_client.ZhbData.is_fresh(fake_zhb, max_delay_days=1) is True


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

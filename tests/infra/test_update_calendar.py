from datetime import date
from pathlib import Path

from scripts.update_calendar import generate_calendar_file, update_calendar_data


def test_generated_calendar_keeps_makeup_weekend_closed():
    holidays = {date(2026, 10, day): "National Day" for day in range(1, 8)}
    workdays = {date(2026, 10, 10): "National Day"}
    source = generate_calendar_file(holidays, workdays, 2026, 2026)
    namespace = {}
    exec(compile(source, "generated_stock_calendar.py", "exec"), namespace)

    assert namespace["is_trading_day"](date(2026, 10, 10)) is False
    assert namespace["get_last_trading_day"](date(2026, 10, 10)) == date(2026, 10, 9)
    assert namespace["recent_trading_dates"](4, date(2026, 10, 12)) == [
        date(2026, 10, 12),
        date(2026, 10, 9),
        date(2026, 10, 8),
        date(2026, 9, 30),
    ]


def test_update_patches_date_tables_without_replacing_project_logic():
    calendar_path = Path(__file__).resolve().parents[2] / "stock_common" / "stock_calendar.py"
    current = calendar_path.read_text(encoding="utf-8")
    holidays = {date(2026, 10, day): "National Day" for day in range(1, 8)}
    workdays = {date(2026, 10, 10): "National Day"}

    updated = update_calendar_data(current, holidays, workdays)
    namespace = {"__name__": "patched_stock_calendar"}
    exec(compile(updated, "patched_stock_calendar.py", "exec"), namespace)

    assert namespace["is_trading_day"](date(2026, 10, 10)) is False
    assert namespace["trading_days_between"](date(2026, 9, 30), date(2026, 10, 12)) == 3
    assert "def is_workday_with_zhb_supplement" in updated
    assert "def trading_day_age" in updated

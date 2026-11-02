from __future__ import annotations

from datetime import datetime, timezone

import pytest

from stock_common.sc_datasource import _sse_e_interaction as sse


def test_sse_time_parses_seconds_relative_to_reference_time() -> None:
    now = datetime(2026, 10, 17, 14, 15, 43)

    assert sse._sse_time("43秒前", now=now) == "2026-10-17 14:15"


def test_sse_time_parses_chinese_and_iso_absolute_formats() -> None:
    assert sse._sse_time("2026年10月21日 17:47") == "2026-10-21 17:47"
    assert sse._sse_time("2026-10-21 17:47") == "2026-10-21 17:47"
    assert sse._sse_time("2026/10/21 17:47") == "2026-10-21 17:47"


def test_sse_time_parses_day_words_and_relative_durations() -> None:
    now = datetime(2026, 10, 17, 14, 15, 43)

    assert sse._sse_time("今天 14:30", now=now) == "2026-10-17 14:30"
    assert sse._sse_time("昨天 18:22", now=now) == "2026-10-16 18:22"
    assert sse._sse_time("前天 08:00", now=now) == "2026-10-15 08:00"
    assert sse._sse_time("2分钟前", now=now) == "2026-10-17 14:13"
    assert sse._sse_time("3小时前", now=now) == "2026-10-17 11:15"
    assert sse._sse_time("刚才", now=now) == "2026-10-17 14:15"


def test_sse_time_parses_month_day_and_clock_only_formats() -> None:
    now = datetime(2026, 1, 2, 12, 0)

    assert sse._sse_time("12-31 08:30", now=now) == "2025-12-31 08:30"
    assert sse._sse_time("09:31", now=now) == "2026-01-02 09:31"


def test_sse_time_uses_beijing_for_aware_reference_times() -> None:
    now = datetime(2026, 10, 23, 0, 30, tzinfo=timezone.utc)

    assert sse._sse_time("昨天 18:22", now=now) == "2026-10-22 18:22"
    assert sse._sse_time("刚刚", now=now) == "2026-10-23 08:30"


def test_sse_time_rejects_invalid_and_out_of_range_values() -> None:
    assert sse._sse_time("2026-02-30 12:00") is None
    assert sse._sse_time("昨天 25:00") is None
    assert sse._sse_time("25:00") is None
    assert sse._sse_time("02-29 18:00", now=datetime(2024, 1, 1)) is None
    assert sse._sse_time(f"{10**20}天前", now=datetime(2026, 10, 17)) is None
    assert sse._sse_time("前天 09:00", now=datetime(1, 1, 1)) is None
    assert sse._sse_time("时间待定", now=datetime(2026, 10, 17)) is None


def _feed(question_time: str, answer_time: str) -> str:
    return (
        '<div class="m_feed_item" id="item-1795125">'
        '<div class="m_feed_txt"><a href="/">:农业银行(601288)</a>测试问题</div>'
        f'<div class="m_feed_from"><span>{question_time}</span></div>'
        '<div class="m_feed_detail m_qa">'
        '<div class="m_feed_txt">测试回复</div>'
        f'<div class="m_feed_from"><span>{answer_time}</span></div>'
        "</div></div>"
    )


def _freeze_now(monkeypatch, fixed_now: datetime) -> None:

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    monkeypatch.setattr(sse, "datetime", FrozenDateTime)


def test_sse_feed_keeps_answer_with_seconds_relative_time(monkeypatch) -> None:
    _freeze_now(monkeypatch, datetime(2026, 10, 17, 14, 15, 43))
    rows = sse._sse_parse_feed(_feed("2026年10月17日 14:00", "43秒前"))

    assert rows[0]["question_time"] == "2026-10-17 14:00"
    assert rows[0]["answer_time"] == "2026-10-17 14:15"


def test_sse_feed_parses_iso_question_and_yesterday_answer(monkeypatch) -> None:
    _freeze_now(monkeypatch, datetime(2026, 10, 17, 14, 15))

    rows = sse._sse_parse_feed(_feed("2026-10-17 14:00", "昨天 18:22"))

    assert rows[0]["question_time"] == "2026-10-17 14:00"
    assert rows[0]["answer_time"] == "2026-10-16 18:22"


def test_sse_feed_keeps_fail_fast_contract_for_unrecognized_times(monkeypatch) -> None:
    _freeze_now(monkeypatch, datetime(2026, 10, 17, 14, 15))

    with pytest.raises(RuntimeError, match="回复时间认不出"):
        sse._sse_parse_feed(_feed("2026-10-17 14:00", "时间待定"))
    with pytest.raises(RuntimeError, match="提问时间认不出"):
        sse._sse_parse_feed(_feed("时间待定", "昨天 18:22"))

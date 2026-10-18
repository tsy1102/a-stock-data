from __future__ import annotations

from datetime import datetime

from stock_common.sc_datasource import _sse_e_interaction as sse


def test_sse_time_parses_seconds_relative_to_reference_time() -> None:
    now = datetime(2026, 10, 17, 14, 15, 43)

    assert sse._sse_time("43秒前", now=now) == "2026-10-17 14:15"


def test_sse_feed_keeps_answer_with_seconds_relative_time(monkeypatch) -> None:
    fixed_now = datetime(2026, 10, 17, 14, 15, 43)

    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now

    monkeypatch.setattr(sse, "datetime", FrozenDateTime)
    feed = (
        '<div class="m_feed_item" id="item-1795125">'
        '<div class="m_feed_txt"><a href="/">:农业银行(601288)</a>测试问题</div>'
        '<div class="m_feed_from"><span>2026年10月17日 14:00</span></div>'
        '<div class="m_feed_detail m_qa">'
        '<div class="m_feed_txt">测试回复</div>'
        '<div class="m_feed_from"><span>43秒前</span></div>'
        "</div></div>"
    )

    rows = sse._sse_parse_feed(feed)

    assert len(rows) == 1
    assert rows[0]["id"] == "1795125"
    assert rows[0]["code"] == "601288"
    assert rows[0]["answer"] == "测试回复"
    assert rows[0]["answer_time"] == "2026-10-17 14:15"

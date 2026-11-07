from stock_common import sc_rate_utils


def test_advance_interval_timestamp_waits_only_for_remaining_interval(monkeypatch):
    times = iter((10.0, 11.5))
    waits = []
    monkeypatch.setattr(sc_rate_utils.time, "time", lambda: next(times))
    monkeypatch.setattr(sc_rate_utils.time, "sleep", waits.append)

    result = sc_rate_utils.advance_interval_timestamp(9.0, 2.0)

    assert waits == [1.0]
    assert result == 11.5


def test_advance_interval_timestamp_does_not_sleep_when_interval_elapsed(monkeypatch):
    times = iter((12.0, 12.25))
    waits = []
    monkeypatch.setattr(sc_rate_utils.time, "time", lambda: next(times))
    monkeypatch.setattr(sc_rate_utils.time, "sleep", waits.append)

    result = sc_rate_utils.advance_interval_timestamp(10.0, 1.0)

    assert waits == []
    assert result == 12.25

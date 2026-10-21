import json
import multiprocessing
import os
import time
from pathlib import Path

import pytest

from stock_common import sc_network, sc_network_limits


class _ImmediateAwaitable:
    def __init__(self, value):
        self.value = value

    def __await__(self):
        if False:
            yield None
        return self.value


def _immediate_to_thread(func, *args, **kwargs):
    return _ImmediateAwaitable(func(*args, **kwargs))


def _run_coroutine_without_event_loop(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as result:
        return result.value
    raise AssertionError("coroutine unexpectedly yielded during the mocked async gate")


def _run_em_group_gate_process(
    lock_file, start_event, result_queue, group_key, global_interval, group_interval
):
    from stock_common import sc_network as worker_network

    if not start_event.wait(10):
        result_queue.put(("error", "start event timed out"))
        return
    started = time.monotonic()
    worker_network._network_limits.process_rate_limit_wait(
        lock_file,
        global_interval,
        group_key,
        group_interval,
        file_lock_acquire=worker_network._file_lock_acquire,
        file_lock_release=worker_network._file_lock_release,
        debug_log=worker_network._debug_log,
        os_module=os,
        open_file=open,
        time_module=time,
    )
    result_queue.put(("ok", started, time.monotonic()))


class _FakeTime:
    def __init__(self, now=1_000.0):
        self.now = now

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def _process_em_slot(lock_file, fake_time, group, global_interval, group_interval):
    return sc_network_limits.process_rate_limit_wait(
        str(lock_file),
        global_interval,
        group,
        group_interval,
        file_lock_acquire=lambda _path, _timeout: True,
        file_lock_release=lambda _path: None,
        debug_log=lambda _message: None,
        os_module=os,
        open_file=open,
        time_module=fake_time,
    )


def test_em_risk_groups_have_distinct_rates_and_shared_push2_family():
    push2_hosts = (
        "push2.eastmoney.com",
        "push2his.eastmoney.com",
        "83.push2.eastmoney.com",
        "1.push2.eastmoney.com",
        "2.push2.eastmoney.com",
    )

    for host in push2_hosts:
        assert sc_network._em_rate_limit_policy(host) == ("push2.eastmoney.com", 0.25)

    assert sc_network._em_rate_limit_policy("push2delay.eastmoney.com") == (
        "push2delay.eastmoney.com",
        1.0,
    )
    assert sc_network._em_rate_limit_policy("push2ex.eastmoney.com") == (
        "push2ex.eastmoney.com",
        0.6,
    )


def test_em_process_scheduler_enforces_global_and_per_group_intervals(tmp_path):
    lock_file = tmp_path / "em_rate_limit"
    fake_time = _FakeTime()

    assert _process_em_slot(lock_file, fake_time, "push2", 0.5, 4.0) == 0.0
    assert _process_em_slot(lock_file, fake_time, "push2delay", 0.5, 1.0) == pytest.approx(0.5)
    assert _process_em_slot(lock_file, fake_time, "push2", 0.5, 4.0) == pytest.approx(3.5)

    state_text = lock_file.read_text(encoding="utf-8")
    assert state_text.startswith("v3|")
    state = json.loads(state_text[3:])
    assert set(state["groups"]) == {"push2", "push2delay"}
    assert state["global_next_allowed"] == pytest.approx(fake_time.now + 0.5)


def test_em_process_scheduler_migrates_v2_global_state(tmp_path):
    lock_file = tmp_path / "em_rate_limit"
    lock_file.write_text("v2|1001.000000000", encoding="utf-8")
    fake_time = _FakeTime()

    waited = _process_em_slot(lock_file, fake_time, "push2ex", 0.3, 1.7)

    assert waited == pytest.approx(1.0)
    assert fake_time.now == pytest.approx(1_001.0)
    assert lock_file.read_text(encoding="utf-8").startswith("v3|")


def test_em_process_scheduler_fails_closed_on_corrupt_state(tmp_path):
    lock_file = tmp_path / "em_rate_limit"
    lock_file.write_text("v3|{broken", encoding="utf-8")
    released = []

    with pytest.raises(ValueError, match="invalid EM rate-limit state JSON"):
        sc_network_limits.process_rate_limit_wait(
            str(lock_file),
            1.2,
            "push2",
            4.0,
            file_lock_acquire=lambda _path, _timeout: True,
            file_lock_release=lambda path: released.append(path),
            debug_log=lambda _message: None,
            os_module=os,
            open_file=open,
            time_module=_FakeTime(),
        )

    assert released == [str(lock_file)]


def test_em_process_scheduler_serializes_same_group_across_processes(tmp_path):
    context = multiprocessing.get_context("spawn")
    start_event = context.Event()
    result_queue = context.Queue()
    lock_file = str(tmp_path / "em_rate_limit")
    processes = [
        context.Process(
            target=_run_em_group_gate_process,
            args=(lock_file, start_event, result_queue, "push2.eastmoney.com", 0.1, 0.2),
        )
        for _ in range(2)
    ]
    for process in processes:
        process.start()
    start_event.set()
    results = [result_queue.get(timeout=15) for _ in processes]
    for process in processes:
        process.join(timeout=15)

    assert all(process.exitcode == 0 for process in processes)
    assert all(result[0] == "ok" for result in results)
    completion_times = sorted(result[2] for result in results)
    assert completion_times[1] - completion_times[0] >= 0.15


def test_em_global_interval_is_shared_across_risk_groups_and_processes(tmp_path):
    context = multiprocessing.get_context("spawn")
    start_event = context.Event()
    result_queue = context.Queue()
    lock_file = str(tmp_path / "em_rate_limit")
    processes = [
        context.Process(
            target=_run_em_group_gate_process,
            args=(lock_file, start_event, result_queue, group, 0.2, 0.0),
        )
        for group in ("push2.eastmoney.com", "push2delay.eastmoney.com")
    ]
    for process in processes:
        process.start()
    start_event.set()
    results = [result_queue.get(timeout=15) for _ in processes]
    for process in processes:
        process.join(timeout=15)

    assert all(process.exitcode == 0 for process in processes)
    assert all(result[0] == "ok" for result in results)
    completion_times = sorted(result[2] for result in results)
    assert completion_times[1] - completion_times[0] >= 0.15


def test_em_403_streak_isolated_by_risk_group(monkeypatch):
    monkeypatch.setattr(sc_network, "_CONSECUTIVE_403", {})

    assert sc_network._record_em_403("push2.eastmoney.com") == 1
    assert sc_network._record_em_403("push2ex.eastmoney.com") == 1
    sc_network._reset_em_403("push2his.eastmoney.com")

    assert sc_network._CONSECUTIVE_403 == {"push2ex.eastmoney.com": 1}


def test_stock_changes_uses_limited_push2ex_transport_with_one_transient_retry(monkeypatch):
    from stock_common.sc_datasource import _quotes

    calls = []

    def fake_quick_request(*args, **kwargs):
        calls.append((args, kwargs))
        return None

    monkeypatch.setattr(sc_network, "_quick_request", fake_quick_request)

    result = _quotes.get_stock_changes("rate-limit-retry-policy-test")

    assert result == []
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[0] == "https://push2ex.eastmoney.com/getAllStockChanges"
    assert kwargs["max_retries"] == 2


def test_em_sync_gate_passes_push2_family_policy(monkeypatch):
    calls = []

    def fake_process_rate_limit_wait(*args, **kwargs):
        calls.append((args, kwargs))
        return 0.0

    monkeypatch.setattr(
        sc_network._network_limits, "process_rate_limit_wait", fake_process_rate_limit_wait
    )

    assert sc_network._em_wait_process_interval("push2his.eastmoney.com") == 0.0

    args, _kwargs = calls[0]
    assert args[2] == "push2.eastmoney.com"
    assert args[3] == pytest.approx(4.0)


def test_em_async_gate_uses_same_risk_group_scheduler(monkeypatch):
    calls = []

    def fake_process_rate_limit_wait(*args, **kwargs):
        calls.append((args, kwargs))
        return 0.0

    monkeypatch.setattr(
        sc_network._network_limits, "process_rate_limit_wait", fake_process_rate_limit_wait
    )
    monkeypatch.setattr(sc_network.asyncio, "to_thread", _immediate_to_thread)

    _run_coroutine_without_event_loop(
        sc_network._em_wait_process_interval_async("push2ex.eastmoney.com")
    )

    assert len(calls) == 1
    args, _kwargs = calls[0]
    assert args[2] == "push2ex.eastmoney.com"
    assert args[3] == pytest.approx(1.0 / 0.6)

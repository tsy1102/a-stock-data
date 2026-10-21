import asyncio
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import os
import time
from io import StringIO
from pathlib import Path

import pytest

from stock_common import sc_network


class _ImmediateAwaitable:
    def __init__(self, value):
        self.value = value

    def __await__(self):
        if False:
            yield None
        return self.value


def _threaded_to_thread(func, *args, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as executor:
        return _ImmediateAwaitable(executor.submit(func, *args, **kwargs).result())


def _run_coroutine_without_event_loop(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as result:
        return result.value
    raise AssertionError("coroutine unexpectedly yielded while using the immediate test awaitable")


def _run_async_gate_in_worker_process(lock_file):
    from stock_common import sc_network as worker_network

    original_to_thread = worker_network.asyncio.to_thread
    worker_network.asyncio.to_thread = _threaded_to_thread
    try:
        return _run_coroutine_without_event_loop(
            worker_network._process_interval_wait_async(lock_file, 0.3, True)
        )
    finally:
        worker_network.asyncio.to_thread = original_to_thread


def _run_interval_gate(lock_file, mode, start_event, result_queue):
    from stock_common import sc_network as worker_network

    if not start_event.wait(10):
        result_queue.put(("error", "start event timed out"))
        return
    try:
        if mode == "async":
            _run_async_gate_in_worker_process(lock_file)
        else:
            worker_network._process_interval_wait(lock_file, 0.3, True, True)
        result_queue.put(("ok", time.monotonic()))
    except Exception as exc:
        result_queue.put(("error", f"{type(exc).__name__}: {exc}"))
        raise


def _acquire_rate_limit_lock_then_exit(lock_file, acquired_event):
    from stock_common import sc_network as worker_network

    if not worker_network._file_lock_acquire(lock_file, timeout=5.0):
        os._exit(2)
    acquired_event.set()
    os._exit(0)


def test_provider_interval_wait_serializes_request_start_times(tmp_path, monkeypatch):
    now = [100.0]
    waits = []
    monkeypatch.setattr(sc_network, "_file_lock_acquire", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(sc_network, "_file_lock_release", lambda _path: None)
    monkeypatch.setattr(sc_network.time, "time", lambda: now[0])

    def fake_sleep(seconds):
        waits.append(seconds)
        now[0] += seconds

    monkeypatch.setattr(sc_network.time, "sleep", fake_sleep)
    lock_file = str(tmp_path / "provider.lock")
    state_file = str(tmp_path / "provider.state")

    assert sc_network._provider_interval_wait(lock_file, state_file, 1.0) == 0.0
    now[0] += 0.2
    waited = sc_network._provider_interval_wait(lock_file, state_file, 1.0)

    assert waited == pytest.approx(0.8)
    assert waits == [pytest.approx(0.8)]
    assert float(Path(state_file).read_text(encoding="ascii")) == pytest.approx(101.0)


def test_provider_interval_wait_fails_closed_when_mutex_times_out(monkeypatch):
    monkeypatch.setattr(sc_network, "_file_lock_acquire", lambda *_args, **_kwargs: False)

    with pytest.raises(TimeoutError, match="provider rate-limit lock timed out"):
        sc_network._provider_interval_wait("unused.lock", "unused.state", 1.0)


def test_process_interval_wait_fails_closed_when_mutex_times_out(monkeypatch):
    monkeypatch.setattr(sc_network, "_file_lock_acquire", lambda *_args, **_kwargs: False)

    with pytest.raises(TimeoutError, match="process rate-limit lock timed out"):
        sc_network._process_interval_wait("unused.lock", 1.0, use_lock=True, use_content_ts=True)


def test_process_interval_wait_initializes_missing_general_state(tmp_path):
    state_file = tmp_path / "general.state"

    assert (
        sc_network._process_interval_wait(
            str(state_file), 0.0, use_lock=False, use_content_ts=False
        )
        == 0.0
    )
    content = state_file.read_text(encoding="utf-8")
    assert content.startswith("v2|")
    assert float(content.split("|", 1)[1]) > 0


def test_process_interval_wait_propagates_general_state_read_failure(tmp_path, monkeypatch):
    state_file = tmp_path / "unreadable.state"
    state_file.write_text("100", encoding="utf-8")

    def fail_read(path, mode="r", *args, **kwargs):
        if str(path) == str(state_file) and mode == "r":
            raise PermissionError("rate-limit state is unreadable")
        return open(path, mode, *args, **kwargs)

    monkeypatch.setattr(sc_network, "open", fail_read, raising=False)

    with pytest.raises(PermissionError, match="state is unreadable"):
        sc_network._process_interval_wait(
            str(state_file), 0.0, use_lock=False, use_content_ts=False
        )


def test_process_interval_wait_fails_closed_on_corrupt_timestamp(tmp_path, monkeypatch):
    lock_file = tmp_path / "corrupt.lock"
    lock_file.write_text("123|nan", encoding="utf-8")
    released = []
    monkeypatch.setattr(sc_network, "_file_lock_acquire", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(sc_network, "_file_lock_release", released.append)

    with pytest.raises(ValueError, match="invalid process rate-limit timestamp"):
        sc_network._process_interval_wait(str(lock_file), 1.0, use_lock=True, use_content_ts=True)

    assert released == [str(lock_file)]


@pytest.mark.parametrize(
    ("state", "message"),
    [
        ("123|-0.1", "invalid process rate-limit timestamp"),
        ("v2|9999999999", "too far in the future"),
    ],
)
def test_process_interval_wait_rejects_invalid_or_future_state(
    tmp_path, monkeypatch, state, message
):
    state_file = tmp_path / "invalid.state"
    state_file.write_text(state, encoding="utf-8")
    released = []
    monkeypatch.setattr(sc_network.time, "time", lambda: 1000.0)
    monkeypatch.setattr(sc_network, "_file_lock_acquire", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(sc_network, "_file_lock_release", released.append)

    with pytest.raises(ValueError, match=message):
        sc_network._process_interval_wait(str(state_file), 1.0, use_lock=True, use_content_ts=True)

    assert released == [str(state_file)]


def test_process_interval_wait_fails_closed_when_state_write_fails(tmp_path, monkeypatch):
    lock_file = tmp_path / "write-fails.lock"
    lock_file.write_text("123|100.0", encoding="utf-8")
    original_open = open
    released = []

    def fail_write(path, mode="r", *args, **kwargs):
        if mode == "w":
            raise PermissionError("rate-limit state is read-only")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(sc_network, "open", fail_write, raising=False)
    monkeypatch.setattr(sc_network.time, "time", lambda: 200.0)
    monkeypatch.setattr(sc_network, "_file_lock_acquire", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(sc_network, "_file_lock_release", released.append)

    with pytest.raises(PermissionError, match="read-only"):
        sc_network._process_interval_wait(str(lock_file), 1.0, use_lock=True, use_content_ts=True)

    assert released == [str(lock_file)]


def test_async_process_interval_wait_propagates_state_read_failure(tmp_path, monkeypatch):
    state_file = tmp_path / "unreadable.lock"

    def fail_read(*_args, **_kwargs):
        raise PermissionError("rate-limit state is unreadable")

    monkeypatch.setattr(sc_network, "open", fail_read, raising=False)
    monkeypatch.setattr(sc_network.asyncio, "to_thread", _threaded_to_thread)

    with pytest.raises(PermissionError, match="unreadable"):
        _run_coroutine_without_event_loop(
            sc_network._process_interval_wait_async(str(state_file), 1.0, use_content_ts=True)
        )


def test_async_process_interval_wait_propagates_state_write_failure(tmp_path, monkeypatch):
    state_file = tmp_path / "read-only.lock"

    def fail_write(path, mode="r", **_kwargs):
        if mode == "r":
            return StringIO("123|100.0")
        raise PermissionError("rate-limit state is read-only")

    monkeypatch.setattr(sc_network, "open", fail_write, raising=False)
    monkeypatch.setattr(sc_network.time, "time", lambda: 200.0)
    monkeypatch.setattr(sc_network.asyncio, "to_thread", _threaded_to_thread)

    with pytest.raises(PermissionError, match="read-only"):
        _run_coroutine_without_event_loop(
            sc_network._process_interval_wait_async(str(state_file), 1.0, use_content_ts=True)
        )


def test_provider_interval_wait_fails_closed_on_corrupt_state(tmp_path, monkeypatch):
    state_file = tmp_path / "provider.state"
    state_file.write_text("nan", encoding="ascii")
    released = []
    monkeypatch.setattr(sc_network, "_file_lock_acquire", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(sc_network, "_file_lock_release", released.append)

    with pytest.raises(ValueError, match="invalid provider rate-limit timestamp"):
        sc_network._provider_interval_wait(str(tmp_path / "provider.lock"), str(state_file), 1.0)

    assert released == [str(tmp_path / "provider.lock")]


def test_provider_interval_wait_rejects_far_future_state(tmp_path, monkeypatch):
    state_file = tmp_path / "provider.state"
    state_file.write_text("9999999999", encoding="ascii")
    released = []
    monkeypatch.setattr(sc_network.time, "time", lambda: 1000.0)
    monkeypatch.setattr(sc_network, "_file_lock_acquire", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(sc_network, "_file_lock_release", released.append)

    with pytest.raises(ValueError, match="too far in the future"):
        sc_network._provider_interval_wait(str(tmp_path / "provider.lock"), str(state_file), 0.5)

    assert released == [str(tmp_path / "provider.lock")]


def test_gen_process_interval_gate_uses_shared_mutex_and_state(monkeypatch):
    calls = []
    monkeypatch.setattr(
        sc_network,
        "_process_interval_wait",
        lambda *args, **kwargs: calls.append((args, kwargs)) or 0.0,
    )

    assert sc_network._gen_wait_process_interval() == 0.0
    assert calls[0][0][0] == sc_network._gen_lock_file
    assert calls[0][1] == {"use_lock": True, "use_content_ts": True}


def test_process_interval_wait_serializes_sync_and_async_processes(tmp_path):
    context = multiprocessing.get_context("spawn")
    state_file = str(tmp_path / "shared.state")
    start_event = context.Event()
    result_queue = context.Queue()
    processes = [
        context.Process(
            target=_run_interval_gate,
            args=(state_file, mode, start_event, result_queue),
        )
        for mode in ("sync", "async")
    ]
    try:
        for process in processes:
            process.start()
        start_event.set()
        results = [result_queue.get(timeout=15) for _ in processes]
        for process in processes:
            process.join(timeout=15)
        assert all(process.exitcode == 0 for process in processes)
        assert all(result[0] == "ok" for result in results), results
        starts = sorted(result[1] for result in results)
        assert starts[1] - starts[0] >= 0.28
        assert Path(state_file).read_text(encoding="utf-8").startswith("v2|")
    finally:
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
        result_queue.close()
        result_queue.join_thread()


def test_rate_limit_mutex_is_released_when_process_exits(tmp_path):
    context = multiprocessing.get_context("spawn")
    lock_file = str(tmp_path / "crash.lock")
    acquired_event = context.Event()
    process = context.Process(
        target=_acquire_rate_limit_lock_then_exit,
        args=(lock_file, acquired_event),
    )
    try:
        process.start()
        assert acquired_event.wait(15)
        process.join(timeout=15)
        assert process.exitcode == 0
        assert sc_network._file_lock_acquire(lock_file, timeout=2.0)
        sc_network._file_lock_release(lock_file)
    finally:
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)


def test_confirmed_provider_block_is_persisted_until_manual_review(tmp_path, monkeypatch):
    block_file = tmp_path / "provider_blocks.json"
    monkeypatch.setattr(sc_network, "_LEVISTOCK_BLOCK_FILE", str(block_file))
    monkeypatch.setattr(sc_network, "_LEVISTOCK_BLOCK_LOCK_FILE", str(tmp_path / "block.lock"))
    monkeypatch.setattr(sc_network, "_file_lock_acquire", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(sc_network, "_file_lock_release", lambda _path: None)
    monkeypatch.setattr(sc_network, "_LEVISTOCK_BLOCKED_LOCAL", set())

    marked = sc_network._mark_levistock_provider_block("cls", RuntimeError("HTTP 403 Forbidden"))

    assert marked is True
    assert sc_network._levistock_provider_is_blocked("cls") is True
    assert sc_network._levistock_provider_is_blocked("kph") is False
    assert '"status_code": 403' in block_file.read_text(encoding="utf-8")


def test_levistock_provider_limit_stops_before_wait_or_request(monkeypatch):
    monkeypatch.setattr(sc_network, "_levistock_provider_is_blocked", lambda _family: True)
    monkeypatch.setattr(
        sc_network,
        "_provider_interval_wait",
        lambda *_args, **_kwargs: pytest.fail("blocked provider reached rate limiter"),
    )

    with pytest.raises(RuntimeError, match="blocked until manual recovery review"):
        sc_network._cls_wait_process_interval()

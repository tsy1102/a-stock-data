from pathlib import Path

import pytest

from stock_common import sc_network


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

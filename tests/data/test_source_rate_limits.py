import asyncio
import multiprocessing
import time
from pathlib import Path

import pytest

from stock_common import sc_network


def _run_provider_gate_process(lock_path, state_path, start_event, result_queue):
    try:
        start_event.wait(10)
        sc_network._provider_interval_wait(lock_path, state_path, 0.15)
        result_queue.put(("ok", time.monotonic()))
    except Exception as exc:
        result_queue.put(("error", f"{type(exc).__name__}: {exc}"))


@pytest.mark.parametrize(
    ("url", "expected_group", "expected_interval"),
    [
        ("https://qt.gtimg.cn/q=sh600000", "tencent", 0.2),
        ("https://www.10jqka.com.cn/", "ths", 0.2),
        ("https://irm.cninfo.com.cn/api", "cninfo", 1 / 3),
        ("https://www.cninfo.com.cn/api", "cninfo", 1 / 3),
        ("https://apphwshhq.longhuvip.com/w1/api", "kpl", 1.0),
        ("https://unknown.example/api", "host:unknown.example", 0.2),
    ],
)
def test_source_rate_policy_uses_provider_group_and_configured_floor(
    url, expected_group, expected_interval
):
    group, interval = sc_network._source_rate_limit_policy(url)

    assert group == expected_group
    assert interval == pytest.approx(expected_interval)


def test_eastmoney_cannot_use_the_generic_source_limiter():
    with pytest.raises(ValueError, match="Eastmoney requests must use"):
        sc_network._source_rate_limit_policy("https://push2.eastmoney.com/api")


def test_source_wait_shares_state_between_hosts_in_one_provider_group(monkeypatch):
    reservations = []

    def capture(lock_path, state_path, interval):
        reservations.append((lock_path, state_path, interval))
        return 0.0

    monkeypatch.setattr(sc_network, "_provider_interval_wait", capture)

    sc_network._source_rate_limit_wait("https://irm.cninfo.com.cn/newircs/first")
    sc_network._source_rate_limit_wait("https://www.cninfo.com.cn/api/second")

    assert reservations[0][:2] == reservations[1][:2]
    assert reservations[0][2] == pytest.approx(1 / 3)


def test_provider_source_slots_serialize_processes(tmp_path):
    context = multiprocessing.get_context("spawn")
    start_event = context.Event()
    result_queue = context.Queue()
    lock_path = str(Path(tmp_path) / "source.lock")
    state_path = str(Path(tmp_path) / "source.state")
    processes = [
        context.Process(
            target=_run_provider_gate_process,
            args=(lock_path, state_path, start_event, result_queue),
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
    start_times = sorted(result[1] for result in results)
    assert start_times[1] - start_times[0] >= 0.10


def test_sync_request_fails_closed_when_source_limiter_is_unavailable(monkeypatch):
    def fail_gate(_domain):
        raise TimeoutError("source limiter unavailable")

    monkeypatch.setattr(sc_network, "_source_rate_limit_wait", fail_gate)
    monkeypatch.setattr(
        sc_network,
        "_resolve_host_with_timeout",
        lambda _domain: pytest.fail("DNS resolution ran before the source gate"),
    )
    requests = []
    monkeypatch.setattr(
        sc_network._HTTP_SESSION,
        "get",
        lambda *args, **kwargs: requests.append((args, kwargs)),
    )

    result = sc_network._do_request(
        "https://unknown.example/api", None, None, 1, 1, None, "GET", True
    )

    assert result is None
    assert requests == []


def test_async_request_fails_closed_before_using_session(monkeypatch):
    async def fail_gate(_domain):
        raise TimeoutError("source limiter unavailable")

    monkeypatch.setattr(sc_network, "_HAS_ASYNCIO", True)
    monkeypatch.setattr(sc_network, "_HAS_AIOHTTP", True)
    monkeypatch.setattr(sc_network, "_source_rate_limit_wait_async", fail_gate)

    async def request():
        return await sc_network._async_quick_request(object(), "https://unknown.example/api")

    with pytest.raises(TimeoutError, match="source limiter unavailable"):
        asyncio.run(request())


def test_kpl_post_fails_closed_when_shared_limiter_is_unavailable(monkeypatch):
    from stock_common import sc_kpl

    def fail_gate(*_args, **_kwargs):
        raise TimeoutError("source limiter unavailable")

    monkeypatch.setattr(sc_network, "_provider_interval_wait", fail_gate)
    requests = []
    monkeypatch.setattr(
        sc_kpl.urllib.request,
        "urlopen",
        lambda *args, **kwargs: requests.append((args, kwargs)),
    )

    with pytest.raises(TimeoutError, match="source limiter unavailable"):
        sc_kpl._post("hq", {"a": "test"})

    assert requests == []

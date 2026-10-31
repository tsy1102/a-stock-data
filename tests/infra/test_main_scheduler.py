"""Regression coverage for scheduler success/failure reporting."""

import main


def test_missing_report_script_is_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "_SCRIPT_DIR", str(tmp_path))

    coroutine = main._run_script_async("missing_report.py", [], str(tmp_path), True, "短线")
    try:
        coroutine.send(None)
    except StopIteration as completed:
        result = completed.value
    else:
        coroutine.close()
        raise AssertionError("missing-script branch unexpectedly suspended")

    assert result == ("missing_report.py", 1, 0.0, "短线")


def test_scheduler_requires_one_success_result_per_task():
    assert main._all_tasks_succeeded([("get_sht_report.py", 0, 1.2, "短线")], 1)
    assert not main._all_tasks_succeeded([], 1)
    assert not main._all_tasks_succeeded([RuntimeError("failed")], 1)
    assert not main._all_tasks_succeeded(
        [("get_sht_report.py", 0, 1.2, "短线"), RuntimeError("failed")], 2
    )
    assert not main._all_tasks_succeeded([("get_sht_report.py", 1, 1.2, "短线")], 1)


def test_effective_concurrency_keeps_google_drive_uploads_serialized():
    assert main._effective_concurrency(2, no_upload=True) == 2
    assert main._effective_concurrency(2, no_upload=False) == 1
    assert main._effective_concurrency(8, no_upload=True) == 2
    assert main._effective_concurrency(0, no_upload=True) == 1


def test_task_batches_keep_market_scans_and_first_cache_warmup_serial():
    tasks = [
        ("get_val_report.py", [], "out", True, "全市场选股"),
        ("get_mak_report.py", [], "out", True, "异动扫描"),
        ("get_sht_report.py", ["600000"], "out", True, "短线"),
        ("get_med_report.py", ["600000"], "out", True, "中线"),
        ("get_lng_report.py", ["600000"], "out", True, "长线"),
    ]

    batches = main._plan_task_batches(tasks, 2)

    assert [[task[0] for task in batch] for batch in batches] == [
        ["get_val_report.py"],
        ["get_mak_report.py"],
        ["get_sht_report.py", "get_med_report.py"],
        ["get_lng_report.py"],
    ]


def test_task_batches_warm_a_single_stock_cache_before_parallel_reports():
    tasks = [
        ("get_mak_report.py", [], "out", True, "异动扫描"),
        ("get_sht_report.py", ["600000"], "out", True, "短线"),
        ("get_med_report.py", ["600000"], "out", True, "中线"),
        ("get_lng_report.py", ["600000"], "out", True, "长线"),
    ]

    batches = main._plan_task_batches(tasks, 2)

    assert [[task[0] for task in batch] for batch in batches] == [
        ["get_mak_report.py"],
        ["get_sht_report.py"],
        ["get_med_report.py", "get_lng_report.py"],
    ]

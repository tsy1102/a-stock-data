"""Regression coverage for scheduler success/failure reporting."""

import asyncio

import main


def test_missing_report_script_is_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "_SCRIPT_DIR", str(tmp_path))

    result = asyncio.run(
        main._run_script_async("missing_report.py", [], str(tmp_path), True, "短线")
    )

    assert result == ("missing_report.py", 1, 0.0, "短线")


def test_scheduler_requires_one_success_result_per_task():
    assert main._all_tasks_succeeded([("get_sht_report.py", 0, 1.2, "短线")], 1)
    assert not main._all_tasks_succeeded([], 1)
    assert not main._all_tasks_succeeded([RuntimeError("failed")], 1)
    assert not main._all_tasks_succeeded(
        [("get_sht_report.py", 0, 1.2, "短线"), RuntimeError("failed")], 2
    )
    assert not main._all_tasks_succeeded([("get_sht_report.py", 1, 1.2, "短线")], 1)

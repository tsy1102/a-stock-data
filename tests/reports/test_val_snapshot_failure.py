from types import SimpleNamespace

import pytest

import get_val_report


def test_empty_snapshot_report_is_preserved_and_runner_raises(monkeypatch, tmp_path):
    runner = get_val_report.ValReportRunner()
    runner.args = SimpleNamespace(output=str(tmp_path))
    output_path = tmp_path / f"get_val_report_{runner.report_ts}.md"

    def fake_asyncio_run(coroutine):
        try:
            output_path.write_text(
                f"# diagnostic\n{get_val_report._VAL_EMPTY_SNAPSHOT_MARKER}\n",
                encoding="utf-8",
            )
        finally:
            coroutine.close()

    monkeypatch.setattr(get_val_report.asyncio, "run", fake_asyncio_run)

    with pytest.raises(RuntimeError, match="市场快照为空"):
        runner.execute_pipeline()

    assert output_path.exists()
    assert get_val_report._is_empty_snapshot_failure_report(str(output_path))

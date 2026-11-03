from __future__ import annotations

import builtins
import sys

import pytest

from scripts import verify_sync_check


@pytest.mark.parametrize(
    ("module_name", "failure_label"),
    [
        ("gen_zhb_subdict", "ZHB 镜像覆盖检查无法执行"),
        ("gen_ulist_subdict", "ulist239 镜像覆盖检查无法执行"),
    ],
)
def test_unavailable_hard_mirror_parser_fails_gate(
    monkeypatch, tmp_path, capsys, module_name, failure_label
):
    original_import = builtins.__import__

    def fail_mirror_parser(name, *args, **kwargs):
        if name == module_name:
            raise ImportError("injected mirror parser import failure")
        return original_import(name, *args, **kwargs)

    report_path = tmp_path / "verify_sync_report.md"
    monkeypatch.setattr(builtins, "__import__", fail_mirror_parser)
    monkeypatch.setattr(
        sys,
        "argv",
        ["verify_sync_check.py", "--report-output", str(report_path)],
    )

    result = verify_sync_check.main()
    output = capsys.readouterr().out

    assert result == 1
    assert failure_label in output
    assert "HARD FAIL: 1 | WARN: 0" in output
    assert report_path.is_file()
    assert failure_label in report_path.read_text(encoding="utf-8")

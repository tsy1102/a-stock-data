"""Project-local temporary directory contract."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from stock_common._temp import configure_project_temp


def test_configure_project_temp_defaults_to_repo_tmp(monkeypatch):
    monkeypatch.delenv("ASTOCK_TEMP_DIR", raising=False)
    monkeypatch.setattr(tempfile, "tempdir", None)
    for variable in ("TEMP", "TMP", "TMPDIR"):
        monkeypatch.setenv(variable, "original-temp")

    temp_path = configure_project_temp()

    expected = Path(__file__).resolve().parents[1] / ".tmp"
    assert temp_path == expected.resolve()
    assert temp_path.is_dir()
    assert tempfile.gettempdir() == str(temp_path)
    assert all(os.environ[variable] == str(temp_path) for variable in ("TEMP", "TMP", "TMPDIR"))


def test_configure_project_temp_honors_explicit_override(monkeypatch, tmp_path):
    monkeypatch.setenv("ASTOCK_TEMP_DIR", str(tmp_path / "custom-temp"))
    monkeypatch.setattr(tempfile, "tempdir", None)
    for variable in ("TEMP", "TMP", "TMPDIR"):
        monkeypatch.setenv(variable, "original-temp")

    temp_path = configure_project_temp()

    assert temp_path == (tmp_path / "custom-temp").resolve()
    assert temp_path.is_dir()
    assert all(os.environ[variable] == str(temp_path) for variable in ("TEMP", "TMP", "TMPDIR"))

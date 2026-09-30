"""Regression tests for the main entry point's dependency preflight."""

import builtins
import importlib.util

import pytest

import main


def _hide_google_drive_packages(monkeypatch):
    original_import = builtins.__import__

    def import_without_google(name, *args, **kwargs):
        if name.startswith("google"):
            raise ImportError(name)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_google)


def test_optional_google_dependencies_warn_without_blocking(monkeypatch, capsys):
    monkeypatch.setattr(importlib.util, "find_spec", lambda _name: object())
    _hide_google_drive_packages(monkeypatch)

    main.check_dependencies()

    output = capsys.readouterr().out
    assert "可选依赖" in output
    assert "缺少必要依赖" not in output


def test_required_dependencies_match_runtime_adapters(monkeypatch, capsys):
    checked = []

    def find_spec(name):
        checked.append(name)
        return None if name == "eltdx" else object()

    monkeypatch.setattr(importlib.util, "find_spec", find_spec)
    _hide_google_drive_packages(monkeypatch)

    with pytest.raises(SystemExit) as error:
        main.check_dependencies()

    output = capsys.readouterr().out
    assert error.value.code == 1
    assert "eltdx" in output
    assert "easy_tdx" in checked
    assert "eltdx" in checked
    assert "openpyxl" in checked
    assert "pytdx" not in checked

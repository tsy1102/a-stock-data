from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import black

from scripts import verify_black_api, verify_python_syntax


def test_black_source_files_skip_deleted_git_entries(tmp_path: Path, monkeypatch) -> None:
    tracked = tmp_path / "tracked.py"
    tracked.write_text("value = 1\n", encoding="utf-8")
    monkeypatch.setattr(verify_black_api, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(
        verify_black_api,
        "_project_black_config",
        lambda: (
            black.FileMode(line_length=100),
            verify_black_api.re.compile(r"\.pyi?$"),
            verify_black_api.re.compile(r"^$"),
            verify_black_api.re.compile(r"^$"),
        ),
    )
    monkeypatch.setattr(
        verify_black_api.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout="tracked.py\ndeleted.py\n"),
    )

    assert verify_black_api._source_files() == [tracked]


def test_black_check_returns_nonzero_when_formatting_is_needed(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    source = tmp_path / "needs_formatting.py"
    source.write_text("value=  1\n", encoding="utf-8")
    monkeypatch.setattr(verify_black_api, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(
        verify_black_api,
        "_project_black_config",
        lambda: (black.FileMode(line_length=100), None, None, None),
    )
    monkeypatch.setattr(verify_black_api, "_source_files", lambda: [source])

    assert verify_black_api.main() == 1
    output = capsys.readouterr().out
    assert "needs_formatting.py" in output
    assert "1 need formatting" in output


def test_python_syntax_check_skips_deleted_git_entries(tmp_path: Path, monkeypatch, capsys) -> None:
    source = tmp_path / "valid.py"
    source.write_text("value = 1\n", encoding="utf-8")
    monkeypatch.setattr(verify_python_syntax, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(verify_python_syntax, "OUTPUT_ROOT", tmp_path / ".tmp" / "compiled")
    monkeypatch.setattr(
        verify_python_syntax.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout="valid.py\ndeleted.py\n"),
    )

    assert verify_python_syntax.main() == 0
    assert "PASS (1 files)" in capsys.readouterr().out


def test_python_syntax_check_returns_nonzero_on_invalid_syntax(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    source = tmp_path / "invalid.py"
    source.write_text("def broken(:\n", encoding="utf-8")
    monkeypatch.setattr(verify_python_syntax, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(verify_python_syntax, "OUTPUT_ROOT", tmp_path / ".tmp" / "compiled")
    monkeypatch.setattr(
        verify_python_syntax.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(stdout="invalid.py\n"),
    )

    assert verify_python_syntax.main() == 1
    assert "Python syntax failures" in capsys.readouterr().out
